# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class BCMPlan(models.Model):
    """BCM Plan model"""
    _name = 'bcm.plan'
    _description = 'BCM Plan'
    _inherit = ['bcm.base']
    _order = 'sequence, name'

    name = fields.Char('Plan Name', required=True)
    description = fields.Text('Description')
    plan_type = fields.Selection([
        ('recovery', 'Recovery Plan'),
        ('continuity', 'Continuity Plan'),
        ('emergency', 'Emergency Response'),
        ('communication', 'Communication Plan'),
        ('it_disaster', 'IT Disaster Recovery')
    ], string='Plan Type', default='recovery', required=True)

    status = fields.Selection([
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('outdated', 'Outdated')
    ], string='Status', default='draft', tracking=True)

    sequence = fields.Integer('Sequence', default=10)

    # Plan content
    recovery_procedures = fields.Html('Recovery Procedures')
    activation_criteria = fields.Html('Activation Criteria')
    contact_list = fields.Html('Emergency Contacts')

    # Relationships
    business_process_ids = fields.Many2many(
        'bcm.business.process',
        string='Related Business Processes'
    )
    incident_ids = fields.One2many('bcm.incident', 'plan_id', string='Related Incidents')

    # Metrics
    rto_hours = fields.Float('RTO (Hours)', help='Recovery Time Objective')
    rpo_hours = fields.Float('RPO (Hours)', help='Recovery Point Objective')
    estimated_cost = fields.Monetary('Estimated Implementation Cost', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    def send_event_to_eventbus(self, event_type, data):
        """Send event to EventBus service"""
        try:
            # This would integrate with EventBus service
            _logger.info(f"Event sent: {event_type} - {data}")
        except Exception as e:
            _logger.error(f"Failed to send event: {e}")


class BCMIncident(models.Model):
    """BCM Incident model"""
    _name = 'bcm.incident'
    _description = 'BCM Incident'
    _inherit = ['bcm.base']
    _order = 'create_date desc'

    name = fields.Char('Incident Title', required=True)
    description = fields.Text('Description')

    severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Severity', default='medium', required=True, tracking=True)

    category = fields.Selection([
        ('operational', 'Operational'),
        ('technical', 'Technical'),
        ('security', 'Security'),
        ('natural', 'Natural Disaster'),
        ('human', 'Human Error'),
        ('external', 'External Threat')
    ], string='Category', default='operational', required=True)

    status = fields.Selection([
        ('draft', 'Draft'),
        ('reported', 'Reported'),
        ('investigating', 'Under Investigation'),
        ('responding', 'Response in Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ], string='Status', default='draft', tracking=True)

    # Response details
    response_checklist = fields.Text('Response Checklist')
    ai_generated_checklist = fields.Boolean('AI Generated', default=False)
    resolution_notes = fields.Html('Resolution Notes')

    # Relationships
    plan_id = fields.Many2one('bcm.plan', string='Associated Plan')
    assigned_user_id = fields.Many2one('res.users', string='Assigned To')

    # Timestamps
    reported_date = fields.Datetime('Reported Date', default=fields.Datetime.now)
    resolved_date = fields.Datetime('Resolved Date')

    def send_event_to_eventbus(self, event_type, data):
        """Send event to EventBus service"""
        try:
            _logger.info(f"Incident event sent: {event_type} - {data}")
        except Exception as e:
            _logger.error(f"Failed to send incident event: {e}")


class BCMBusinessProcess(models.Model):
    """Business Process model"""
    _name = 'bcm.business.process'
    _description = 'Business Process'
    _inherit = ['bcm.base']

    name = fields.Char('Process Name', required=True)
    description = fields.Text('Description')

    criticality = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Criticality', default='medium', required=True)

    # Process details
    process_owner_id = fields.Many2one('res.users', string='Process Owner')
    department_id = fields.Many2one('hr.department', string='Department')

    # BIA Data
    rto_target = fields.Float('RTO Target (Hours)')
    rpo_target = fields.Float('RPO Target (Hours)')
    financial_impact_per_hour = fields.Monetary('Financial Impact/Hour', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    # Dependencies
    dependency_ids = fields.Many2many(
        'bcm.business.process',
        'process_dependency_rel',
        'process_id',
        'dependency_id',
        string='Dependencies'
    )