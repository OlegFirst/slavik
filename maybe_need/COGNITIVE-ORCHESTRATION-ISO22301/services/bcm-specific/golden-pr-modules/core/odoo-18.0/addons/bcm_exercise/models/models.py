from odoo import models, fields, api, _
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class BcmExercise(models.Model):
    _name = 'bcm.exercise'
    _description = 'BCM Exercise Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char('Exercise Name', required=True, tracking=True)
    active = fields.Boolean(default=True)
    
    # Exercise Details
    exercise_type = fields.Selection([
        ('tabletop', 'Tabletop Exercise'),
        ('walkthrough', 'Walkthrough'),
        ('simulation', 'Simulation'),
        ('fullscale', 'Full-Scale Exercise')
    ], string='Exercise Type', required=True, default='tabletop', tracking=True)
    
    scenario = fields.Text('Exercise Scenario')
    ai_generated = fields.Boolean('AI Generated Scenario', default=False)

    # Template Integration (NEW)
    template_id = fields.Many2one(
        'bcm.template',
        string='Exercise Template',
        domain=[('category', '=', 'workflow')],
        help='BPMN workflow template for this exercise'
    )

    scenario_id = fields.Many2one(
        'bcm.scenario',
        string='Based on Scenario',
        help='Scenario this exercise is based on'
    )

    # BPMN Workflow Integration (NEW)
    bpmn_process_id = fields.Char('BPMN Process ID', help='External BPMN Service process ID')
    workflow_status = fields.Selection([
        ('draft', 'Draft'),
        ('initialized', 'Initialized'),
        ('running', 'Running'),
        ('suspended', 'Suspended'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], string='Workflow Status', default='draft', tracking=True)

    workflow_variables = fields.Text('Workflow Variables (JSON)', help='BPMN process variables')
    current_tasks = fields.Text('Current Tasks (JSON)', help='Active workflow tasks')
    
    # Status and Dates
    state = fields.Selection([
        ('requested', 'Requested'),
        ('pending', 'Pending Review'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='requested', tracking=True)
    
    planned_date = fields.Datetime('Planned Date/Time', tracking=True)
    
    # Participants
    requested_by = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user)
    assigned_facilitator = fields.Many2one('res.users', string='Assigned Facilitator', tracking=True)
    participant_ids = fields.Many2many('res.users', string='Participants')
    
    # Feedback
    feedback_data = fields.Text('Feedback Data')
    feedback_submitted = fields.Boolean('Feedback Submitted', default=False)
    feedback_date = fields.Datetime('Feedback Date')
    
    # Multi-tenancy
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True, index=True,
        default=lambda self: self.env.company,
        help='Company/tenant isolation'
    )

    def action_start_exercise_workflow(self):
        """Start BPMN workflow from template"""
        if not self.template_id or not self.template_id.bpmn_xml:
            from odoo.exceptions import ValidationError
            raise ValidationError(_('Exercise template with BPMN workflow is required'))

        # Prepare workflow variables
        workflow_vars = {
            'exercise_id': self.id,
            'exercise_name': self.name,
            'exercise_type': self.exercise_type,
            'scenario_id': self.scenario_id.id if self.scenario_id else None,
            'scenario_category': self.scenario_id.category if self.scenario_id else None,
            'participants': [p.id for p in self.participant_ids],
            'facilitator_id': self.assigned_facilitator.id if self.assigned_facilitator else None,
            'company_id': self.company_id.id
        }

        try:
            # Call BPMN Service to start workflow
            import requests
            import json

            bpmn_service_url = "http://bpmn_service:8005"
            workflow_data = {
                'process_definition_xml': self.template_id.bpmn_xml,
                'business_key': f'exercise_{self.id}',
                'variables': workflow_vars,
                'tenant_id': self.company_id.code or 'default'
            }

            response = requests.post(
                f'{bpmn_service_url}/api/process-instances',
                json=workflow_data,
                timeout=30
            )

            if response.status_code == 201:
                result = response.json()
                self.write({
                    'bpmn_process_id': result.get('process_id'),
                    'workflow_status': 'running',
                    'workflow_variables': json.dumps(workflow_vars),
                    'state': 'scheduled'
                })

                # Notify participants
                self._notify_exercise_start()

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Exercise Started'),
                        'message': f'BPMN workflow started for exercise "{self.name}"',
                        'type': 'success',
                    }
                }
            else:
                raise Exception(f'BPMN Service error: {response.status_code}')

        except Exception as e:
            _logger.error(f'Failed to start exercise workflow: {str(e)}')
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Workflow Error'),
                    'message': f'Failed to start workflow: {str(e)}',
                    'type': 'danger',
                }
            }

    def _notify_exercise_start(self):
        """Notify participants of exercise start"""
        try:
            # Notify via notification service
            import requests

            notification_data = {
                'title': f'BCM Exercise Started: {self.name}',
                'message': f'Exercise "{self.name}" has begun. Please check your tasks.',
                'channels': ['slack'],
                'severity': 'info',
                'recipients': [p.email for p in self.participant_ids if p.email],
                'metadata': {
                    'exercise_id': self.id,
                    'exercise_type': self.exercise_type,
                    'bpmn_process_id': self.bpmn_process_id
                }
            }

            requests.post(
                'http://notification_service:8002/external/notify',
                json=notification_data,
                timeout=5
            )

        except Exception as e:
            _logger.warning(f'Failed to send exercise notification: {str(e)}')

    @api.model
    def create_from_scenario(self, scenario_id, template_id=None):
        """Create exercise from scenario with optional template"""
        scenario = self.env['bcm.scenario'].browse(scenario_id)
        if not scenario.exists():
            return False

        # Auto-select template if not provided
        if not template_id:
            compatible_templates = self.env['bcm.template'].search([
                ('category', '=', 'workflow'),
                ('template_type', '=', f'{scenario.level}_exercise')
            ], limit=1)

            template_id = compatible_templates.id if compatible_templates else None

        exercise_data = {
            'name': f'Exercise: {scenario.title}',
            'exercise_type': scenario.level,
            'scenario': scenario.content_md or scenario.meta_description,
            'scenario_id': scenario.id,
            'template_id': template_id,
            'ai_generated': scenario.meta_ai_generated,
            'state': 'requested'
        }

        exercise = self.create(exercise_data)

        # Link back to scenario
        scenario.message_post(
            body=f'Exercise created: <a href="/web#id={exercise.id}&model=bcm.exercise">{exercise.name}</a>',
            subject='Exercise Created'
        )

        return exercise
    
    def action_schedule(self):
        """Schedule the exercise"""
        self.write({'state': 'scheduled'})
        self._send_status_notification()
        # EventBus integration will be added when bcm_core is installed
        _logger.info(f"Exercise {self.name} scheduled for {self.planned_date}")
        return True
    
    def _send_status_notification(self):
        """Send email notification on status change"""
        try:
            if self.requested_by and self.requested_by.email:
                subject = f"Exercise Status Update: {self.name}"
                body = f"""
                <p>Dear {self.requested_by.name},</p>
                <p>Your exercise request has been updated:</p>
                <ul>
                    <li><strong>Exercise:</strong> {self.name}</li>
                    <li><strong>Type:</strong> {self.exercise_type}</li>
                    <li><strong>Status:</strong> {self.state.title()}</li>
                    <li><strong>Planned Date:</strong> {self.planned_date or 'Not scheduled yet'}</li>
                </ul>
                <p>Best regards,<br/>BCM Team</p>
                """
                
                mail_values = {
                    'subject': subject,
                    'body_html': body,
                    'email_to': self.requested_by.email,
                    'model': self._name,
                    'res_id': self.id,
                }
                self.env['mail.mail'].create(mail_values).send()
        except Exception as e:
            _logger.error(f"Failed to send notification: {e}")


class BcmExerciseRecord(models.Model):
    _name = 'bcm_exercise.record'
    _description = 'BCM Exercise Record with Multi-tenancy'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    notes = fields.Text()
    
    # Multi-tenancy field
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True, index=True,
        default=lambda self: self.env.company,
        help='Company/tenant isolation'
    )
