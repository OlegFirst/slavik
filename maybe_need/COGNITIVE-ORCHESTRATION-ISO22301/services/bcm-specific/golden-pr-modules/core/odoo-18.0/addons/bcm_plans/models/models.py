# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class BcmContinuityPlan(models.Model):
    """Business Continuity Plans"""
    _name = 'bcm.plan'
    _description = 'BCM Continuity Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, name'

    name = fields.Char(
        string='Plan Name',
        required=True, index=True,
        tracking=True,
        help='Name of the business continuity plan'
    )
    
    # Plan Classification
    plan_type = fields.Selection([
        ('business_continuity', 'Business Continuity Plan'),
        ('disaster_recovery', 'Disaster Recovery Plan'),
        ('emergency_response', 'Emergency Response Plan'),
        ('crisis_management', 'Crisis Management Plan'),
        ('incident_response', 'Incident Response Plan')
    ], string='Plan Type', required=True, tracking=True)
    
    priority = fields.Selection([
        ('1', 'Critical'),
        ('2', 'High'),
        ('3', 'Medium'),
        ('4', 'Low')
    ], string='Priority', required=True, default='3', tracking=True)
    
    # Plan Status and Lifecycle
    status = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('archived', 'Archived')
    ], string='Status', default='draft', required=True, tracking=True)
    
    version = fields.Char(
        string='Version',
        default='1.0',
        help='Current version of the plan'
    )
    
    # Plan Content
    objective = fields.Html(
        string='Plan Objective',
        help='Main objective and purpose of this plan'
    )
    
    scope = fields.Html(
        string='Plan Scope',
        help='Scope and applicability of the plan'
    )
    
    assumptions = fields.Html(
        string='Assumptions',
        help='Key assumptions underlying the plan'
    )
    
    # Activation Criteria
    activation_triggers = fields.Html(
        string='Activation Triggers',
        help='Conditions that trigger plan activation'
    )
    
    activation_authority = fields.Many2one(
        'res.users',
        string='Activation Authority',
        help='Person authorized to activate this plan'
    )
    
    # Recovery Objectives
    rto = fields.Integer(
        string='RTO (hours)',
        help='Recovery Time Objective in hours'
    )
    
    rpo = fields.Integer(
        string='RPO (hours)',
        help='Recovery Point Objective in hours'  
    )
    
    mtpd = fields.Integer(
        string='MTPD (hours)',
        help='Maximum Tolerable Period of Disruption in hours'
    )
    
    # Plan Procedures
    procedure_ids = fields.One2many(
        'bcm.plan.procedure',
        'plan_id',
        string='Procedures'
    )
    
    # Resources and Dependencies
    resource_ids = fields.One2many(
        'bcm.plan.resource',
        'plan_id',
        string='Required Resources'
    )
    
    # Responsible Parties
    plan_owner_id = fields.Many2one(
        'res.users',
        string='Plan Owner',
        required=True, index=True,
        tracking=True
    )
    
    team_leader_id = fields.Many2one(
        'res.users',
        string='Team Leader',
        tracking=True
    )
    
    team_member_ids = fields.Many2many(
        'res.users',
        string='Team Members'
    )
    
    # Review and Maintenance
    review_frequency = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semiannually', 'Semi-annually'),
        ('annually', 'Annually')
    ], string='Review Frequency', default='annually')
    
    last_review_date = fields.Date(string='Last Review Date')
    next_review_date = fields.Date(
        string='Next Review Date',
        compute='_compute_next_review_date',
        store=True
    )
    
    last_test_date = fields.Date(string='Last Test Date')
    next_test_date = fields.Date(string='Next Test Date')
    
    # Approval Workflow
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
    
    @api.depends('last_review_date', 'review_frequency')
    def _compute_next_review_date(self):
        """Calculate next review date"""
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
    
    def action_activate(self):
        """Activate the plan"""
        self.write({
            'status': 'active',
            'activation_date': fields.Datetime.now()
        })
        self.message_post(
            body=_('Plan activated on %s') % fields.Datetime.now()
        )
    
    def action_deactivate(self):
        """Deactivate the plan"""
        self.write({'status': 'approved'})
        self.message_post(body=_('Plan deactivated'))
    
    def action_generate_draft(self):
        """Generate draft plan steps using AI Orchestrator"""
        self.ensure_one()
        
        try:
            import requests
            
            # Получить URL Orchestrator из настроек
            BcmConfig = self.env.get('bcm.config')
            if not BcmConfig:
                raise ValidationError(_('BCM Settings not configured'))
            
            config = BcmConfig.sudo().search([], limit=1)
            if not config or not config.orchestrator_base_url:
                raise ValidationError(_('AI Orchestrator URL is not configured. Please configure it in BCM Settings.'))
            
            # Подготовить данные для AI
            plan_data = {
                'type': 'plan',
                'plan_id': self.id,
                'name': self.name,
                'plan_type': self.plan_type,
                'priority': self.priority,
                'description': self.description or '',
                'process_ids': [p.id for p in self.process_ids] if self.process_ids else [],
                'company_id': self.company_id.id
            }
            
            # Вызов AI Orchestrator
            url = f"{config.orchestrator_base_url}/recommendations"
            response = requests.post(
                url,
                json=plan_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Создать draft шаги плана
                if result.get('steps'):
                    for idx, step in enumerate(result.get('steps', [])):
                        self.env['bcm.plan.procedure'].create({
                            'plan_id': self.id,
                            'sequence': (idx + 1) * 10,
                            'name': step.get('name', f'Step {idx + 1}'),
                            'description': step.get('description', ''),
                            'responsible_user_id': self.plan_owner_id.id,
                            'estimated_duration': step.get('duration', 60),
                            'is_critical': step.get('critical', False)
                        })
                
                # Обновить описание плана с рекомендациями AI
                if result.get('recommendations'):
                    self.description = (self.description or '') + '\n\n' + _('AI Recommendations:\n') + result.get('recommendations')
                
                self.message_post(
                    body=_('Draft plan generated with %s steps by AI Orchestrator') % len(result.get('steps', []))
                )
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Draft Plan Generated'),
                        'message': _('%s plan steps have been generated') % len(result.get('steps', [])),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise ValidationError(_('AI Orchestrator returned error: %s') % response.text)
                
        except requests.exceptions.RequestException as e:
            raise ValidationError(_('Failed to connect to AI Orchestrator: %s') % str(e))
        except Exception as e:
            raise ValidationError(_('Plan generation failed: %s') % str(e))

class BcmPlanProcedure(models.Model):
    """Plan Procedures and Steps"""
    _name = 'bcm.plan.procedure'
    _description = 'BCM Plan Procedure'
    _order = 'sequence, name'

    plan_id = fields.Many2one(
        'bcm.plan',
        string='Plan',
        required=True, index=True,
        ondelete='cascade'
    )
    
    sequence = fields.Integer(string='Sequence', default=10)
    
    name = fields.Char(
        string='Procedure Name',
        required=True, index=True
    )
    
    procedure_type = fields.Selection([
        ('immediate', 'Immediate Response'),
        ('short_term', 'Short-term Recovery'),
        ('long_term', 'Long-term Recovery'),
        ('communication', 'Communication'),
        ('coordination', 'Coordination'),
        ('logistics', 'Logistics')
    ], string='Type', required=True)
    
    description = fields.Html(
        string='Procedure Description',
        help='Detailed procedure steps'
    )
    
    # Execution Details
    estimated_duration = fields.Integer(
        string='Estimated Duration (minutes)',
        help='Expected time to complete procedure'
    )
    
    responsible_role = fields.Char(
        string='Responsible Role',
        help='Role responsible for executing this procedure'
    )
    
    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible Person'
    )
    
    # Dependencies
    prerequisite_ids = fields.Many2many(
        'bcm.plan.procedure',
        'procedure_prerequisite_rel',
        'procedure_id',
        'prerequisite_id',
        string='Prerequisites',
        help='Procedures that must complete before this one'
    )
    
    # Resources
    required_resources = fields.Text(
        string='Required Resources',
        help='Resources needed to execute this procedure'
    )
    
    # Verification
    success_criteria = fields.Text(
        string='Success Criteria',
        help='How to verify successful completion'
    )
    
    # Multi-tenancy
    company_id = fields.Many2one(
        'res.company',
        related='plan_id.company_id',
        store=True
    )

class BcmPlanResource(models.Model):
    """Plan Resources"""
    _name = 'bcm.plan.resource'
    _description = 'BCM Plan Resource'
    _order = 'resource_type, name'

    plan_id = fields.Many2one(
        'bcm.plan',
        string='Plan',
        required=True, index=True,
        ondelete='cascade'
    )
    
    name = fields.Char(
        string='Resource Name',
        required=True, index=True
    )
    
    resource_type = fields.Selection([
        ('personnel', 'Personnel'),
        ('facility', 'Facility/Location'),
        ('equipment', 'Equipment'),
        ('technology', 'Technology/System'),
        ('supplier', 'Supplier/Vendor'),
        ('information', 'Information/Data'),
        ('financial', 'Financial Resource')
    ], string='Resource Type', required=True)
    
    description = fields.Text(
        string='Description',
        help='Detailed description of the resource'
    )
    
    # Availability
    availability_requirement = fields.Selection([
        ('immediate', 'Immediate (0-1 hour)'),
        ('short_term', 'Short-term (1-24 hours)'),
        ('medium_term', 'Medium-term (1-7 days)'),
        ('long_term', 'Long-term (>7 days)')
    ], string='Availability Requirement', required=True)
    
    # Criticality
    criticality = fields.Selection([
        ('critical', 'Critical'),
        ('important', 'Important'),
        ('useful', 'Useful'),
        ('optional', 'Optional')
    ], string='Criticality', required=True)
    
    # Resource Details
    quantity_required = fields.Integer(
        string='Quantity Required',
        default=1
    )
    
    location = fields.Char(
        string='Location',
        help='Where the resource is located or can be obtained'
    )
    
    contact_person = fields.Char(
        string='Contact Person',
        help='Person to contact for this resource'
    )
    
    contact_details = fields.Text(
        string='Contact Details',
        help='Phone, email, or other contact information'
    )
    
    # Alternatives
    alternative_resources = fields.Text(
        string='Alternative Resources',
        help='Alternative resources if primary is unavailable'
    )
    
    # Multi-tenancy
    company_id = fields.Many2one(
        'res.company',
        related='plan_id.company_id',
        store=True
    )

class BcmPlanExecution(models.Model):
    """Plan Execution Records"""
    _name = 'bcm.plan.execution'
    _description = 'BCM Plan Execution'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'execution_date desc'

    plan_id = fields.Many2one(
        'bcm.plan',
        string='Plan',
        required=True, index=True
    )
    
    name = fields.Char(
        string='Execution Name',
        required=True, index=True,
        default=lambda self: _('Plan Execution')
    )
    
    execution_type = fields.Selection([
        ('actual', 'Actual Incident'),
        ('test', 'Test/Exercise'),
        ('drill', 'Drill'),
        ('walkthrough', 'Walkthrough')
    ], string='Execution Type', required=True)
    
    execution_date = fields.Datetime(
        string='Execution Date',
        default=fields.Datetime.now,
        required=True, index=True
    )
    
    # Execution Details
    trigger_event = fields.Text(
        string='Trigger Event',
        help='What triggered the plan execution'
    )
    
    activated_by = fields.Many2one(
        'res.users',
        string='Activated By',
        required=True, index=True
    )
    
    # Performance Metrics
    actual_activation_time = fields.Integer(
        string='Activation Time (minutes)',
        help='Time taken to activate the plan'
    )
    
    actual_recovery_time = fields.Integer(
        string='Recovery Time (hours)',
        help='Actual time to achieve recovery objectives'
    )
    
    effectiveness_rating = fields.Selection([
        ('1', 'Poor'),
        ('2', 'Fair'),
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent')
    ], string='Effectiveness Rating')
    
    # Results and Lessons Learned
    summary = fields.Html(
        string='Execution Summary',
        help='Summary of the execution'
    )
    
    lessons_learned = fields.Html(
        string='Lessons Learned',
        help='Key lessons learned from execution'
    )
    
    improvement_actions = fields.Html(
        string='Improvement Actions',
        help='Actions to improve the plan'
    )
    
    # Multi-tenancy
    company_id = fields.Many2one(
        'res.company',
        related='plan_id.company_id',
        store=True
    )
