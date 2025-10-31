# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class BcmProjectMilestone(models.Model):
    _name = 'bcm.project.milestone'
    _description = 'BCM Project Milestone'
    _order = 'sequence, deadline'
    
    project_id = fields.Many2one('bcm.marketplace.project', 'Project', required=True, ondelete='cascade')
    name = fields.Char('Milestone Name', required=True)
    description = fields.Text('Description')
    
    sequence = fields.Integer('Sequence', default=10)
    deadline = fields.Date('Deadline')
    completion_date = fields.Date('Completion Date')
    
    deliverables = fields.Text('Deliverables')
    acceptance_criteria = fields.Text('Acceptance Criteria')
    
    amount = fields.Float('Payment Amount')
    currency_id = fields.Many2one('res.currency', related='project_id.currency_id')
    
    state = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='pending')
    
    # Attachments for deliverables
    attachment_ids = fields.Many2many('ir.attachment', string='Deliverable Attachments')
    
    # Approval
    approved_by = fields.Many2one('res.users', 'Approved By')
    approval_date = fields.Datetime('Approval Date')
    rejection_reason = fields.Text('Rejection Reason')
    
    def action_submit_for_review(self):
        self.ensure_one()
        if not self.attachment_ids:
            raise ValidationError(_("Please attach deliverables before submitting for review."))
        self.state = 'review'
        
        # Notify client
        self.project_id.message_post(
            body=_("Milestone '%s' submitted for review") % self.name,
            partner_ids=[self.project_id.client_id.id],
            subtype_xmlid='mail.mt_comment'
        )
    
    def action_approve(self):
        self.ensure_one()
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approval_date': fields.Datetime.now(),
            'completion_date': fields.Date.today()
        })
        
        # Update project progress
        self.project_id._update_progress()
    
    def action_reject(self):
        self.ensure_one()
        self.state = 'rejected'


class BcmProjectTimesheet(models.Model):
    _name = 'bcm.project.timesheet'
    _description = 'BCM Project Timesheet'
    _order = 'date desc'
    
    project_id = fields.Many2one('bcm.marketplace.project', 'Project', required=True, ondelete='cascade')
    specialist_id = fields.Many2one('bcm.specialist', 'Specialist', required=True)
    
    date = fields.Date('Date', required=True, default=fields.Date.today)
    hours = fields.Float('Hours Worked', required=True)
    
    description = fields.Text('Work Description', required=True)
    task_type = fields.Selection([
        ('analysis', 'Analysis'),
        ('documentation', 'Documentation'),
        ('meeting', 'Meeting'),
        ('implementation', 'Implementation'),
        ('review', 'Review'),
        ('training', 'Training'),
        ('other', 'Other')
    ], string='Task Type', required=True)
    
    # Billing
    hourly_rate = fields.Float('Hourly Rate')
    amount = fields.Float('Amount', compute='_compute_amount', store=True)
    currency_id = fields.Many2one('res.currency', related='project_id.currency_id')
    is_billable = fields.Boolean('Billable', default=True)
    is_invoiced = fields.Boolean('Invoiced', default=False)
    
    # Approval
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft')
    
    approved_by = fields.Many2one('res.users', 'Approved By')
    approval_date = fields.Datetime('Approval Date')
    
    @api.depends('hours', 'hourly_rate')
    def _compute_amount(self):
        for record in self:
            record.amount = record.hours * record.hourly_rate
    
    def action_submit(self):
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError(_("Only draft timesheets can be submitted."))
        self.state = 'submitted'
    
    def action_approve(self):
        self.ensure_one()
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approval_date': fields.Datetime.now()
        })


class BcmSpecialistReview(models.Model):
    _name = 'bcm.specialist.review'
    _description = 'Specialist Review'
    _order = 'create_date desc'
    
    specialist_id = fields.Many2one('bcm.specialist', 'Specialist', required=True)
    project_id = fields.Many2one('bcm.marketplace.project', 'Project', required=True)
    reviewer_id = fields.Many2one('res.partner', 'Reviewer', required=True)
    
    # Ratings (1-5 scale)
    overall_rating = fields.Float('Overall Rating', required=True)
    expertise_rating = fields.Float('Expertise')
    communication_rating = fields.Float('Communication')
    timeliness_rating = fields.Float('Timeliness')
    value_rating = fields.Float('Value for Money')
    
    # Review
    review_title = fields.Char('Review Title')
    review_text = fields.Text('Review', required=True)
    
    # Recommendation
    would_recommend = fields.Boolean('Would Recommend')
    would_hire_again = fields.Boolean('Would Hire Again')
    
    # Verification
    is_verified = fields.Boolean('Verified Review', default=False)
    verification_notes = fields.Text('Verification Notes')
    
    # Response
    specialist_response = fields.Text('Specialist Response')
    response_date = fields.Date('Response Date')
    
    # Helpful votes
    helpful_count = fields.Integer('Helpful Votes', default=0)
    unhelpful_count = fields.Integer('Not Helpful Votes', default=0)
    
    @api.constrains('overall_rating')
    def _check_rating(self):
        for record in self:
            if record.overall_rating < 1 or record.overall_rating > 5:
                raise ValidationError(_("Rating must be between 1 and 5."))


class BcmMarketplaceDispute(models.Model):
    _name = 'bcm.marketplace.dispute'
    _description = 'Marketplace Dispute'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    name = fields.Char('Dispute Title', required=True, tracking=True)
    project_id = fields.Many2one('bcm.marketplace.project', 'Project', required=True)
    
    # Parties
    raised_by = fields.Selection([
        ('client', 'Client'),
        ('specialist', 'Specialist')
    ], string='Raised By', required=True)
    
    specialist_id = fields.Many2one('bcm.specialist', related='project_id.specialist_id')
    client_id = fields.Many2one('res.partner', related='project_id.client_id')
    
    # Dispute Details
    dispute_type = fields.Selection([
        ('payment', 'Payment Issue'),
        ('quality', 'Quality of Work'),
        ('timeline', 'Timeline/Deadline'),
        ('scope', 'Scope Creep'),
        ('communication', 'Communication Issues'),
        ('other', 'Other')
    ], string='Dispute Type', required=True)
    
    description = fields.Text('Dispute Description', required=True)
    requested_resolution = fields.Text('Requested Resolution')
    
    # Evidence
    attachment_ids = fields.Many2many('ir.attachment', string='Supporting Documents')
    
    # Resolution
    assigned_mediator = fields.Many2one('res.users', 'Assigned Mediator')
    mediation_notes = fields.Text('Mediation Notes')
    resolution = fields.Text('Resolution')
    
    # Status
    state = fields.Selection([
        ('open', 'Open'),
        ('investigation', 'Under Investigation'),
        ('mediation', 'In Mediation'),
        ('resolved', 'Resolved'),
        ('escalated', 'Escalated'),
        ('closed', 'Closed')
    ], string='Status', default='open', tracking=True)
    
    resolution_date = fields.Date('Resolution Date')
    
    def action_start_investigation(self):
        self.ensure_one()
        self.state = 'investigation'
        
        # Notify both parties
        partners = [self.specialist_id.partner_id.id, self.client_id.id]
        self.message_post(
            body=_("Dispute is now under investigation."),
            partner_ids=partners,
            subtype_xmlid='mail.mt_comment'
        )
    
    def action_resolve(self):
        self.ensure_one()
        if not self.resolution:
            raise ValidationError(_("Please provide a resolution before closing the dispute."))
        
        self.write({
            'state': 'resolved',
            'resolution_date': fields.Date.today()
        })