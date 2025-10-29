# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class BcmOrganizationalContext(models.Model):
    """Organizational Context for ISO 22301 BCMS"""
    _name = 'bcm.context'
    _description = 'BCM Organizational Context'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char(
        string='Context Name',
        required=True, index=True,
        tracking=True,
        help='Name of the organizational context element'
    )
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(default=True, tracking=True)
    
    # Context Type
    context_type = fields.Selection([
        ('internal', 'Internal Factor'),
        ('external', 'External Factor'),
        ('stakeholder', 'Stakeholder Requirement'),
        ('regulatory', 'Regulatory Requirement'),
        ('strategic', 'Strategic Objective')
    ], string='Context Type', required=True, tracking=True)
    
    # Context Details
    description = fields.Html(
        string='Description',
        help='Detailed description of the context element'
    )
    impact_on_bcms = fields.Text(
        string='Impact on BCMS',
        help='How this context affects the BCMS'
    )
    
    # Risk and Opportunity Assessment
    risk_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Risk Level', tracking=True)
    
    opportunity_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], string='Opportunity Level', tracking=True)
    
    # Review and Monitoring
    review_frequency = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semiannually', 'Semi-annually'),
        ('annually', 'Annually')
    ], string='Review Frequency', default='quarterly')
    
    last_review_date = fields.Date(string='Last Review Date')
    next_review_date = fields.Date(
        string='Next Review Date',
        compute='_compute_next_review_date',
        store=True
    )
    
    # Responsible Parties
    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible Person',
        tracking=True
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Responsible Department'
    )
    
    # Multi-tenancy
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True, index=True,
        default=lambda self: self.env.company,
        help='Company/tenant isolation'
    )
    
    # Related Records
    stakeholder_ids = fields.One2many(
        'bcm.stakeholder',
        'context_id',
        string='Related Stakeholders'
    )
    
    @api.depends('last_review_date', 'review_frequency')
    def _compute_next_review_date(self):
        """Calculate next review date based on frequency"""
        from dateutil.relativedelta import relativedelta
        
        for record in self:
            if record.last_review_date and record.review_frequency:
                if record.review_frequency == 'monthly':
                    record.next_review_date = record.last_review_date + relativedelta(months=1)
                elif record.review_frequency == 'quarterly':
                    record.next_review_date = record.last_review_date + relativedelta(months=3)
                elif record.review_frequency == 'semiannually':
                    record.next_review_date = record.last_review_date + relativedelta(months=6)
                elif record.review_frequency == 'annually':
                    record.next_review_date = record.last_review_date + relativedelta(years=1)
            else:
                record.next_review_date = False
    
    def action_mark_reviewed(self):
        """Mark context as reviewed today"""
        self.write({
            'last_review_date': fields.Date.today()
        })
        self.message_post(
            body=_('Context reviewed on %s') % fields.Date.today()
        )

class BcmStakeholder(models.Model):
    """Stakeholders and their requirements"""
    _name = 'bcm.stakeholder'
    _description = 'BCM Stakeholder'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Stakeholder Name',
        required=True, index=True,
        tracking=True
    )
    stakeholder_type = fields.Selection([
        ('internal', 'Internal Stakeholder'),
        ('external', 'External Stakeholder'),
        ('regulatory', 'Regulatory Body'),
        ('customer', 'Customer/Patient'),
        ('supplier', 'Supplier/Vendor'),
        ('partner', 'Business Partner'),
        ('community', 'Community/Public')
    ], string='Type', required=True, tracking=True)
    
    # Contact Information
    contact_person = fields.Char(string='Contact Person')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    address = fields.Text(string='Address')
    
    # Requirements and Expectations
    requirements = fields.Html(
        string='Requirements & Expectations',
        help='Key requirements and expectations from this stakeholder'
    )
    
    influence_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Influence Level', required=True, tracking=True)
    
    interest_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], string='Interest Level', required=True, tracking=True)
    
    # Communication
    communication_method = fields.Selection([
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('meeting', 'Face-to-face Meeting'),
        ('portal', 'Web Portal'),
        ('report', 'Regular Reports')
    ], string='Preferred Communication', tracking=True)
    
    communication_frequency = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('as_needed', 'As Needed'),
        ('emergency_only', 'Emergency Only')
    ], string='Communication Frequency', tracking=True)
    
    # Relations
    context_id = fields.Many2one(
        'bcm.context',
        string='Related Context'
    )
    
    # Multi-tenancy
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True, index=True,
        default=lambda self: self.env.company
    )
    
    active = fields.Boolean(default=True, tracking=True)

class BcmScope(models.Model):
    """BCMS Scope Definition"""
    _name = 'bcm.scope'
    _description = 'BCM Scope'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Scope Element',
        required=True, index=True,
        tracking=True
    )
    
    scope_type = fields.Selection([
        ('inclusion', 'Included in BCMS'),
        ('exclusion', 'Excluded from BCMS'),
        ('boundary', 'Scope Boundary')
    ], string='Scope Type', required=True, tracking=True)
    
    description = fields.Html(
        string='Description',
        help='Detailed description of the scope element'
    )
    
    justification = fields.Text(
        string='Justification',
        help='Justification for inclusion/exclusion'
    )
    
    # Organizational Units
    department_ids = fields.Many2many(
        'hr.department',
        string='Departments'
    )
    
    # Geographical Scope
    geographical_scope = fields.Text(
        string='Geographical Scope',
        help='Locations, regions, or facilities covered'
    )
    
    # Services and Products
    services_products = fields.Text(
        string='Services/Products',
        help='Services or products within scope'
    )
    
    # Review
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By'
    )
    approval_date = fields.Date(string='Approval Date')
    
    # Multi-tenancy
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True, index=True,
        default=lambda self: self.env.company
    )
    
    active = fields.Boolean(default=True, tracking=True)

class BcmPolicy(models.Model):
    """BCM Policies and Objectives"""
    _name = 'bcm.policy'
    _description = 'BCM Policy'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char(
        string='Policy Name',
        required=True, index=True,
        tracking=True
    )
    sequence = fields.Integer(string='Sequence', default=10)
    
    policy_type = fields.Selection([
        ('policy', 'Policy Statement'),
        ('objective', 'BCM Objective'),
        ('principle', 'BCM Principle'),
        ('standard', 'Standard/Procedure')
    ], string='Type', required=True, tracking=True)
    
    content = fields.Html(
        string='Content',
        help='Full content of the policy/objective'
    )
    
    # Measurement and KPIs
    measurable = fields.Boolean(
        string='Measurable Objective',
        help='Is this a measurable objective with KPIs?'
    )
    target_value = fields.Float(string='Target Value')
    measurement_unit = fields.Char(string='Measurement Unit')
    
    # Review and Approval
    version = fields.Char(string='Version', default='1.0')
    effective_date = fields.Date(
        string='Effective Date',
        default=fields.Date.today
    )
    review_date = fields.Date(string='Next Review Date')
    
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By'
    )
    approval_date = fields.Date(string='Approval Date')
    
    # Multi-tenancy
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True, index=True,
        default=lambda self: self.env.company
    )
    
    active = fields.Boolean(default=True, tracking=True)
