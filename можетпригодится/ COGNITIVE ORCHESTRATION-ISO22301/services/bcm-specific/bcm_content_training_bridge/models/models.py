from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json

class BcmTemplate(models.Model):
    """Enhanced BCM Templates with Document and Workflow support"""
    _name = 'bcm.template'
    _description = 'BCM Templates - Documents and Workflows'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'category, sequence, name'

    name = fields.Char('Template Name', required=True, tracking=True)
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence', default=10)

    # Template categorization
    category = fields.Selection([
        ('document', 'Document Template'),
        ('workflow', 'BPMN Workflow Template'),
        ('form', 'Form Template'),
        ('checklist', 'Checklist Template'),
        ('report', 'Report Template')
    ], string='Template Category', required=True, default='document')

    template_type = fields.Selection([
        # Document templates
        ('policy', 'BCM Policy'),
        ('procedure', 'BCM Procedure'),
        ('plan', 'Business Continuity Plan'),
        ('bia_report', 'BIA Report'),
        ('risk_register', 'Risk Register'),
        ('incident_report', 'Incident Report'),

        # BPMN workflow templates
        ('tabletop_exercise', 'Tabletop Exercise Workflow'),
        ('functional_exercise', 'Functional Exercise Workflow'),
        ('full_scale_exercise', 'Full-Scale Exercise Workflow'),
        ('incident_response', 'Incident Response Workflow'),
        ('compliance_audit', 'Compliance Audit Workflow'),
        ('risk_assessment', 'Risk Assessment Workflow'),

        # Form templates
        ('bia_form', 'BIA Assessment Form'),
        ('risk_form', 'Risk Assessment Form'),
        ('exercise_form', 'Exercise Evaluation Form'),

        # Checklists
        ('exercise_checklist', 'Exercise Checklist'),
        ('incident_checklist', 'Incident Response Checklist'),
        ('audit_checklist', 'Audit Checklist')
    ], string='Template Type', required=True)

    description = fields.Text('Description')
    notes = fields.Text('Implementation Notes')

    # Template content
    content = fields.Html('Template Content', help='HTML content for document templates')
    bpmn_xml = fields.Text('BPMN 2.0 XML', help='BPMN workflow definition for workflow templates')
    form_schema = fields.Text('Form Schema (JSON)', help='JSON schema for form templates')

    # ISO 22301 compliance
    iso_clause = fields.Selection([
        ('4.1', 'Clause 4.1 - Organization Context'),
        ('4.2', 'Clause 4.2 - Stakeholder Needs'),
        ('4.3', 'Clause 4.3 - BCMS Scope'),
        ('4.4', 'Clause 4.4 - BCMS Implementation'),
        ('5.1', 'Clause 5.1 - Leadership'),
        ('6.1', 'Clause 6.1 - Risk Management'),
        ('7.1', 'Clause 7.1 - Resources'),
        ('8.1', 'Clause 8.1 - Operation'),
        ('9.1', 'Clause 9.1 - Monitoring'),
        ('10.1', 'Clause 10.1 - Improvement')
    ], string='ISO 22301 Clause')

    # Usage tracking
    usage_count = fields.Integer('Usage Count', default=0)
    last_used = fields.Datetime('Last Used')

    # Relations
    scenario_types = fields.Many2many(
        'bcm.scenario',
        string='Compatible Scenarios',
        help='Scenario types this template applies to'
    )

    # AI enhancement
    is_ai_enhanced = fields.Boolean('AI Enhanced', default=False)
    ai_prompt = fields.Text('AI Generation Prompt', help='Prompt for AI-assisted template generation')

    # Multi-tenancy
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True, index=True,
        default=lambda self: self.env.company,
        help='Company/tenant isolation'
    )

    @api.constrains('bpmn_xml')
    def _check_bpmn_xml(self):
        """Validate BPMN XML format"""
        for template in self:
            if template.category == 'workflow' and template.bpmn_xml:
                # Basic BPMN XML validation
                if not template.bpmn_xml.strip().startswith('<?xml'):
                    raise ValidationError(_('BPMN XML must be valid XML format'))

    @api.constrains('form_schema')
    def _check_form_schema(self):
        """Validate form schema JSON"""
        for template in self:
            if template.form_schema:
                try:
                    json.loads(template.form_schema)
                except json.JSONDecodeError:
                    raise ValidationError(_('Form schema must be valid JSON'))

    def action_generate_with_ai(self):
        """Generate template content using AI"""
        if not self.ai_prompt:
            raise ValidationError(_('AI prompt is required for AI generation'))

        # TODO: Integrate with AI Orchestrator
        # Call AI service to generate template content
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('AI Generation'),
                'message': _('AI template generation will be implemented in next phase'),
                'type': 'info',
            }
        }

    def action_preview_template(self):
        """Preview template content"""
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/preview/template/{self.id}',
            'target': 'new',
        }

    def action_use_template(self):
        """Use template (increment usage counter)"""
        self.usage_count += 1
        self.last_used = fields.Datetime.now()

        if self.category == 'workflow' and self.bpmn_xml:
            # Create workflow instance via BPMN Service
            return self._create_workflow_instance()
        else:
            # Create document from template
            return self._create_document_from_template()

    def _create_workflow_instance(self):
        """Create BPMN workflow instance with JaamSim integration"""
        try:
            # Check if this template requires simulation
            needs_simulation = self.template_type in ['full_scale_exercise', 'functional_exercise']

            if needs_simulation:
                # Generate JaamSim configuration from template
                jaamsim_config = self._generate_jaamsim_config()

                # Call Exercise Simulators Bridge to initialize simulation
                import requests
                simulation_data = {
                    'template_id': self.id,
                    'template_name': self.name,
                    'bpmn_xml': self.bpmn_xml,
                    'jaamsim_config': jaamsim_config,
                    'exercise_type': self.template_type
                }

                response = requests.post(
                    'http://exercise_simulators:8094/api/simulations/initialize',
                    json=simulation_data,
                    timeout=30
                )

                if response.status_code == 200:
                    simulation_result = response.json()
                    simulation_id = simulation_result.get('simulation_id')

                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('Simulation Initialized'),
                            'message': f'JaamSim simulation "{simulation_id}" initialized for template "{self.name}"',
                            'type': 'success',
                        }
                    }

            # Standard BPMN workflow without simulation
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Workflow Ready'),
                    'message': f'BPMN workflow "{self.name}" ready for execution',
                    'type': 'success',
                }
            }

        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f'Error creating workflow instance: {e}')
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Workflow Error'),
                    'message': f'Failed to initialize workflow: {str(e)}',
                    'type': 'danger',
                }
            }

    def _generate_jaamsim_config(self):
        """Generate JaamSim configuration from BPMN template"""

        config_template = f"""# JaamSim Configuration for {self.name}
# Auto-generated from BPMN workflow template

RecordEdits

# Template-specific parameters
Define DiscreteDistribution {{ EventDistribution }}
Define ExponentialDistribution {{ ProcessingDistribution }}
Define UniformDistribution {{ ResourceDistribution }}

# Configure based on template type
EventDistribution ValueList {{ 1 2 3 4 5 }}
EventDistribution ProbabilityList {{ 0.1 0.2 0.4 0.2 0.1 }}

ProcessingDistribution Mean {{ 30 min }}
ResourceDistribution MinValue {{ 5 min }}
ResourceDistribution MaxValue {{ 60 min }}

# Exercise simulation entities
Define EntityGenerator {{ ExerciseEvents }}
Define Queue {{ ParticipantQueue }}
Define Server {{ {"ExerciseTeam ResponseTeam" if self.template_type == "full_scale_exercise" else "ExerciseTeam"} }}
Define EntitySink {{ CompletedTasks }}

# Configure for exercise type
{"ExerciseTeam Capacity { 10 }" if self.template_type == "full_scale_exercise" else "ExerciseTeam Capacity { 5 }"}
{"ResponseTeam Capacity { 8 }" if self.template_type == "full_scale_exercise" else ""}

# Simulation timeline
Define SimulationRun {{ {self.name.replace(' ', '')}Simulation }}
{self.name.replace(' ', '')}Simulation RunDuration {{ {"8 h" if self.template_type == "full_scale_exercise" else "4 h"} }}

# Output configuration
Define FileToWrite {{ ExerciseResults }}
ExerciseResults DataSource {{ ParticipantQueue.QueueTime ExerciseTeam.Utilization }}
ExerciseResults OutputFile {{ '{self.name.lower().replace(' ', '_')}_results.csv' }}
"""

        return config_template

    def _create_document_from_template(self):
        """Create document from template"""
        # TODO: Integration with document creation
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Document Created'),
                'message': f'Document created from template "{self.name}"',
                'type': 'success',
            }
        }


# Legacy model for backward compatibility
class BcmTemplatesRecord(models.Model):
    _name = 'bcm_templates.record'
    _description = 'BCM Templates Record (Legacy)'

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
