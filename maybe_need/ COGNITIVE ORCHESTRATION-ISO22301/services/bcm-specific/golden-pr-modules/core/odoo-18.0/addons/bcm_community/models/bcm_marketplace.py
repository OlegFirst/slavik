# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta

class BcmServiceRequest(models.Model):
    """Client requests for BCM services - like job postings"""
    _name = 'bcm.service.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'BCM Service Request'
    _order = 'create_date desc'
    
    name = fields.Char('Request Title', required=True, tracking=True)
    description = fields.Html('Detailed Description', required=True)
    
    # Client Information
    client_id = fields.Many2one('res.partner', 'Client', required=True)
    client_user_id = fields.Many2one('res.users', 'Client User', required=True)
    company_name = fields.Char('Company Name')
    industry_id = fields.Many2one('bcm.industry', 'Industry')
    company_size = fields.Selection([
        ('small', '1-50 employees'),
        ('medium', '51-200 employees'),
        ('large', '201-1000 employees'),
        ('enterprise', '1000+ employees')
    ], string='Company Size')
    
    # Request Details
    service_type = fields.Selection([
        ('consulting', 'Consulting'),
        ('assessment', 'Risk Assessment'),
        ('bia', 'Business Impact Analysis'),
        ('planning', 'BCM Planning'),
        ('training', 'Training & Workshop'),
        ('audit', 'Audit & Review'),
        ('implementation', 'Implementation Support'),
        ('crisis_support', 'Crisis Management Support'),
        ('other', 'Other')
    ], string='Service Type', required=True)
    
    urgency = fields.Selection([
        ('low', 'Low - Flexible timeline'),
        ('medium', 'Medium - Within 2-4 weeks'),
        ('high', 'High - Within 1 week'),
        ('urgent', 'Urgent - ASAP')
    ], string='Urgency', default='medium')
    
    # Scope
    scope_of_work = fields.Text('Scope of Work')
    deliverables = fields.Text('Expected Deliverables')
    
    # Timeline
    start_date = fields.Date('Desired Start Date')
    end_date = fields.Date('Expected End Date')
    duration_estimate = fields.Float('Estimated Duration (hours)')
    
    # Budget
    budget_type = fields.Selection([
        ('hourly', 'Hourly Rate'),
        ('fixed', 'Fixed Budget'),
        ('negotiable', 'Negotiable')
    ], string='Budget Type')
    
    budget_min = fields.Float('Minimum Budget')
    budget_max = fields.Float('Maximum Budget')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    
    # Requirements
    required_certifications = fields.Text('Required Certifications')
    required_experience = fields.Integer('Minimum Years of Experience')
    required_skills = fields.Many2many(
        'bcm.specialization',
        'request_specialization_rel',
        'request_id',
        'specialization_id',
        string='Required Skills'
    )
    
    # Location
    work_location = fields.Selection([
        ('remote', 'Remote'),
        ('onsite', 'Onsite'),
        ('hybrid', 'Hybrid')
    ], string='Work Location', default='remote')
    
    location_country_id = fields.Many2one('res.country', 'Country')
    location_state_id = fields.Many2one('res.country.state', 'State')
    location_city = fields.Char('City')
    
    # Proposals
    proposal_ids = fields.One2many('bcm.service.proposal', 'request_id', 'Proposals')
    proposal_count = fields.Integer('Number of Proposals', compute='_compute_proposal_count')
    
    # Selected Specialist
    selected_proposal_id = fields.Many2one('bcm.service.proposal', 'Selected Proposal')
    selected_specialist_id = fields.Many2one('bcm.specialist', 'Selected Specialist', related='selected_proposal_id.specialist_id')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('in_review', 'Reviewing Proposals'),
        ('assigned', 'Specialist Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    # Dates
    posted_date = fields.Datetime('Posted Date')
    deadline = fields.Datetime('Application Deadline')
    completion_date = fields.Date('Completion Date')
    
    # Visibility
    is_public = fields.Boolean('Public Request', default=True, help='Visible to all specialists')
    invited_specialist_ids = fields.Many2many(
        'bcm.specialist',
        'request_specialist_invite_rel',
        'request_id',
        'specialist_id',
        string='Invited Specialists'
    )
    
    @api.depends('proposal_ids')
    def _compute_proposal_count(self):
        for record in self:
            record.proposal_count = len(record.proposal_ids)
    
    def action_post(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Only draft requests can be posted."))
        self.write({
            'state': 'posted',
            'posted_date': fields.Datetime.now()
        })
        # Notify relevant specialists
        self._notify_specialists()
    
    def action_assign(self, proposal_id):
        self.ensure_one()
        proposal = self.env['bcm.service.proposal'].browse(proposal_id)
        if proposal.request_id.id != self.id:
            raise ValidationError(_("Invalid proposal for this request."))
        
        self.write({
            'selected_proposal_id': proposal_id,
            'state': 'assigned'
        })
        # Accept the selected proposal
        proposal.action_accept()
        # Reject other proposals
        other_proposals = self.proposal_ids.filtered(lambda p: p.id != proposal_id)
        other_proposals.action_reject()
    
    def _notify_specialists(self):
        """Notify matching specialists about new request"""
        # Find matching specialists based on skills and availability
        specialists = self.env['bcm.specialist'].search([
            ('active', '=', True),
            ('availability_status', 'in', ['available', 'busy']),
            ('specialization_ids', 'in', self.required_skills.ids)
        ])
        
        # Send notifications
        for specialist in specialists:
            self.message_post(
                body=_("New service request matching your profile: %s") % self.name,
                partner_ids=[specialist.partner_id.id],
                subtype_xmlid='mail.mt_comment'
            )


class BcmServiceProposal(models.Model):
    """Specialist proposals for service requests"""
    _name = 'bcm.service.proposal'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'BCM Service Proposal'
    _order = 'create_date desc'
    
    request_id = fields.Many2one('bcm.service.request', 'Service Request', required=True, ondelete='cascade')
    specialist_id = fields.Many2one('bcm.specialist', 'Specialist', required=True)
    
    # Proposal Details
    cover_letter = fields.Html('Cover Letter', required=True)
    proposed_approach = fields.Text('Proposed Approach')
    
    # Timeline
    proposed_start_date = fields.Date('Proposed Start Date')
    proposed_duration = fields.Float('Proposed Duration (hours)')
    proposed_end_date = fields.Date('Proposed End Date')
    
    # Pricing
    pricing_type = fields.Selection([
        ('hourly', 'Hourly Rate'),
        ('fixed', 'Fixed Price'),
        ('milestone', 'Milestone-Based')
    ], string='Pricing Type', required=True)
    
    proposed_rate = fields.Float('Proposed Rate')
    total_cost = fields.Float('Total Cost Estimate')
    currency_id = fields.Many2one('res.currency', related='request_id.currency_id')
    
    # Additional Info
    relevant_experience = fields.Text('Relevant Experience')
    portfolio_item_ids = fields.Many2many(
        'bcm.specialist.portfolio',
        'proposal_portfolio_rel',
        'proposal_id',
        'portfolio_id',
        string='Relevant Portfolio Items'
    )
    
    # Attachments
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn')
    ], string='Status', default='draft', tracking=True)
    
    submission_date = fields.Datetime('Submission Date')
    review_date = fields.Datetime('Review Date')
    
    # Client feedback
    client_notes = fields.Text('Client Notes')
    rejection_reason = fields.Text('Rejection Reason')
    
    def action_submit(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Only draft proposals can be submitted."))
        
        # Check if specialist already submitted a proposal
        existing = self.search([
            ('request_id', '=', self.request_id.id),
            ('specialist_id', '=', self.specialist_id.id),
            ('state', 'not in', ['draft', 'withdrawn']),
            ('id', '!=', self.id)
        ])
        if existing:
            raise ValidationError(_("You have already submitted a proposal for this request."))
        
        self.write({
            'state': 'submitted',
            'submission_date': fields.Datetime.now()
        })
        
        # Notify client
        self.request_id.message_post(
            body=_("New proposal received from %s") % self.specialist_id.name,
            subtype_xmlid='mail.mt_comment'
        )
    
    def action_accept(self):
        self.ensure_one()
        self.write({
            'state': 'accepted',
            'review_date': fields.Datetime.now()
        })
        # Create project
        self._create_project()
    
    def action_reject(self):
        self.ensure_one()
        self.write({
            'state': 'rejected',
            'review_date': fields.Datetime.now()
        })
    
    def _create_project(self):
        """Create a BCM project from accepted proposal"""
        project = self.env['bcm.marketplace.project'].create({
            'name': self.request_id.name,
            'request_id': self.request_id.id,
            'proposal_id': self.id,
            'specialist_id': self.specialist_id.id,
            'client_id': self.request_id.client_id.id,
            'start_date': self.proposed_start_date,
            'end_date': self.proposed_end_date,
            'budget': self.total_cost,
            'state': 'new'
        })
        return project


class BcmMarketplaceProject(models.Model):
    """Active BCM consulting projects"""
    _name = 'bcm.marketplace.project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'BCM Marketplace Project'
    _order = 'create_date desc'
    
    name = fields.Char('Project Name', required=True, tracking=True)
    code = fields.Char('Project Code', default='New', copy=False)
    
    # Relations
    request_id = fields.Many2one('bcm.service.request', 'Original Request')
    proposal_id = fields.Many2one('bcm.service.proposal', 'Selected Proposal')
    specialist_id = fields.Many2one('bcm.specialist', 'Specialist', required=True)
    client_id = fields.Many2one('res.partner', 'Client', required=True)
    
    # Project Details
    description = fields.Html('Project Description')
    objectives = fields.Text('Project Objectives')
    deliverables = fields.Text('Deliverables')
    
    # Timeline
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date')
    actual_start_date = fields.Date('Actual Start Date')
    actual_end_date = fields.Date('Actual End Date')
    
    # Financial
    budget = fields.Float('Total Budget')
    spent_amount = fields.Float('Amount Spent')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    payment_terms = fields.Text('Payment Terms')
    
    # Progress
    progress = fields.Float('Progress (%)', default=0.0)
    milestone_ids = fields.One2many('bcm.project.milestone', 'project_id', 'Milestones')
    
    # Time Tracking
    timesheet_ids = fields.One2many('bcm.project.timesheet', 'project_id', 'Timesheets')
    total_hours = fields.Float('Total Hours', compute='_compute_total_hours', store=True)
    
    # Status
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='new', tracking=True)
    
    # Reviews and Ratings
    specialist_rating = fields.Float('Specialist Rating')
    client_rating = fields.Float('Client Rating')
    specialist_review = fields.Text('Review for Specialist')
    client_review = fields.Text('Review for Client')
    
    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('bcm.marketplace.project') or 'New'
        return super().create(vals)
    
    @api.depends('timesheet_ids.hours')
    def _compute_total_hours(self):
        for record in self:
            record.total_hours = sum(record.timesheet_ids.mapped('hours'))
    
    def action_start(self):
        self.ensure_one()
        self.write({
            'state': 'in_progress',
            'actual_start_date': fields.Date.today()
        })
    
    def action_complete(self):
        self.ensure_one()
        self.write({
            'state': 'completed',
            'actual_end_date': fields.Date.today(),
            'progress': 100.0
        })
        # Trigger review process
        self._request_reviews()
    
    def _request_reviews(self):
        """Request reviews from both parties"""
        # Send review request to client
        self.message_post(
            body=_("Project completed. Please provide your review and rating."),
            partner_ids=[self.client_id.id],
            subtype_xmlid='mail.mt_comment'
        )
        # Send review request to specialist
        self.message_post(
            body=_("Project completed. Please provide your review and rating."),
            partner_ids=[self.specialist_id.partner_id.id],
            subtype_xmlid='mail.mt_comment'
        )