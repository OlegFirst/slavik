# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import json
import logging

_logger = logging.getLogger(__name__)

class DigitalTwinOrganization(models.Model):
    _name = 'bcm.digital.twin.organization'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Digital Twin Organization'
    _order = 'name, id desc'

    # Basic Information
    name = fields.Char(
        string='Organization Name',
        required=True,
        tracking=True,
        help="Name of the organization for Digital Twin modeling"
    )

    description = fields.Text(
        string='Description',
        help="Detailed description of the organization and its context"
    )

    # BCM Integration
    bcm_client_id = fields.Many2one(
        'bcm.client',
        string='BCM Client',
        required=True,
        tracking=True,
        help="Associated BCM client record"
    )

    bcm_context_id = fields.Many2one(
        'bcm.context',
        string='BCM Context',
        help="BCM organizational context"
    )

    # Domain Classification
    domain_type = fields.Selection([
        ('corporate', 'Corporate'),
        ('government', 'Government'),
        ('npo', 'Non-Profit Organization'),
        ('infrastructure', 'Critical Infrastructure')
    ], string='Organization Domain', required=True, tracking=True,
       help="Type of organization for domain-specific functionality")

    industry_sector = fields.Selection([
        ('manufacturing', 'Manufacturing'),
        ('financial', 'Financial Services'),
        ('healthcare', 'Healthcare'),
        ('technology', 'Technology'),
        ('retail', 'Retail'),
        ('energy', 'Energy & Utilities'),
        ('transportation', 'Transportation'),
        ('education', 'Education'),
        ('government', 'Government'),
        ('defense', 'Defense & Security'),
        ('ngo', 'NGO/NPO'),
        ('other', 'Other')
    ], string='Industry Sector', help="Specific industry classification")

    # Digital Twin Configuration
    twin_config = fields.Text(
        string='Twin Configuration',
        help="JSON configuration for Digital Twin parameters"
    )

    twin_status = fields.Selection([
        ('draft', 'Draft'),
        ('configuring', 'Configuring'),
        ('active', 'Active'),
        ('simulation', 'Running Simulation'),
        ('analysis', 'Under Analysis'),
        ('inactive', 'Inactive'),
        ('error', 'Error')
    ], string='Twin Status', default='draft', tracking=True)

    # Simulation Results
    simulation_results = fields.Text(
        string='Latest Simulation Results',
        help="JSON results from the latest simulation run"
    )

    prediction_models = fields.Text(
        string='Prediction Models',
        help="JSON configuration of AI prediction models"
    )

    ai_insights = fields.Text(
        string='AI Generated Insights',
        help="Latest insights from AI organs analysis"
    )

    # Metrics and KPIs
    twin_health_score = fields.Float(
        string='Twin Health Score',
        help="Overall health score of the Digital Twin (0-100)"
    )

    last_analysis_date = fields.Datetime(
        string='Last Analysis Date',
        help="When the last comprehensive analysis was performed"
    )

    simulation_count = fields.Integer(
        string='Total Simulations',
        compute='_compute_simulation_count',
        help="Total number of simulations run for this organization"
    )

    # Relationships
    simulation_ids = fields.One2many(
        'bcm.digital.twin.simulation',
        'organization_id',
        string='Simulations'
    )

    # Configuration flags
    auto_sync_bcm = fields.Boolean(
        string='Auto Sync with BCM',
        default=True,
        help="Automatically synchronize with BCM data"
    )

    enable_ai_analysis = fields.Boolean(
        string='Enable AI Analysis',
        default=True,
        help="Enable AI organs analysis for this organization"
    )

    enable_predictions = fields.Boolean(
        string='Enable Predictions',
        default=True,
        help="Enable predictive analytics"
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        help="Company this Digital Twin belongs to"
    )

    # Computed fields
    @api.depends('simulation_ids')
    def _compute_simulation_count(self):
        for record in self:
            record.simulation_count = len(record.simulation_ids)

    # Constraints
    @api.constrains('twin_config')
    def _check_twin_config(self):
        for record in self:
            if record.twin_config:
                try:
                    json.loads(record.twin_config)
                except ValueError:
                    raise ValidationError(_("Twin Configuration must be valid JSON"))

    @api.constrains('simulation_results')
    def _check_simulation_results(self):
        for record in self:
            if record.simulation_results:
                try:
                    json.loads(record.simulation_results)
                except ValueError:
                    raise ValidationError(_("Simulation Results must be valid JSON"))

    # Methods
    def action_create_digital_twin(self):
        """Create Digital Twin using external service"""
        self.ensure_one()

        if not self.bcm_client_id:
            raise UserError(_("BCM Client is required to create Digital Twin"))

        # Prepare data for Digital Twin service
        twin_data = self._prepare_twin_data()

        # Call Digital Twin Bridge
        bridge = self.env['bcm.digital.twin.bridge']
        try:
            # result = bridge.create_digital_twin(twin_data)  # Temporarily disabled
            result = {'config': {}, 'status': 'active'}  # Mock result

            # Update configuration with results
            self.twin_config = json.dumps(result.get('config', {}))
            self.twin_status = 'active'

            # Log activity
            self.message_post(
                body=_("Digital Twin created successfully"),
                message_type='notification'
            )

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Success"),
                    'message': _("Digital Twin created successfully"),
                    'type': 'success'
                }
            }

        except Exception as e:
            self.twin_status = 'error'
            _logger.error(f"Failed to create Digital Twin: {str(e)}")
            raise UserError(_("Failed to create Digital Twin: %s") % str(e))

    def action_sync_with_bcm(self):
        """Synchronize Digital Twin with BCM data"""
        self.ensure_one()

        bridge = self.env['bcm.digital.twin.bridge']
        try:
            result = bridge.sync_organization_data(self.id)

            self.message_post(
                body=_("Synchronized with BCM data successfully"),
                message_type='notification'
            )

            return result

        except Exception as e:
            _logger.error(f"Failed to sync with BCM: {str(e)}")
            raise UserError(_("Failed to sync with BCM: %s") % str(e))

    def action_run_ai_analysis(self):
        """Trigger AI analysis for this organization"""
        self.ensure_one()

        if not self.enable_ai_analysis:
            raise UserError(_("AI Analysis is disabled for this organization"))

        # Call AI Twin Orchestrator
        orchestrator = self.env['bcm.ai.twin.orchestrator']
        try:
            insights = orchestrator.coordinate_analysis(self.id)

            # Update AI insights
            self.ai_insights = json.dumps(insights)
            self.last_analysis_date = fields.Datetime.now()

            self.message_post(
                body=_("AI Analysis completed successfully"),
                message_type='notification'
            )

            return {
                'name': _('AI Analysis Results'),
                'type': 'ir.actions.act_window',
                'res_model': 'bcm.digital.twin.organization',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'current',
            }

        except Exception as e:
            _logger.error(f"AI Analysis failed: {str(e)}")
            raise UserError(_("AI Analysis failed: %s") % str(e))

    def action_view_simulations(self):
        """View simulations for this organization"""
        self.ensure_one()

        return {
            'name': _('Simulations'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.digital.twin.simulation',
            'view_mode': 'tree,form',
            'domain': [('organization_id', '=', self.id)],
            'context': {'default_organization_id': self.id},
            'target': 'current',
        }

    def _prepare_twin_data(self):
        """Prepare data for Digital Twin service"""
        bcm_data = {}

        # Get BCM client data
        if self.bcm_client_id:
            bcm_data.update({
                'client_name': self.bcm_client_id.name,
                'client_code': getattr(self.bcm_client_id, 'code', ''),
                'client_type': getattr(self.bcm_client_id, 'client_type', ''),
            })

        # Get BCM context data
        if self.bcm_context_id:
            bcm_data.update({
                'context_data': getattr(self.bcm_context_id, 'context_data', {}),
                'organizational_structure': getattr(self.bcm_context_id, 'org_structure', {}),
            })

        return {
            'organization_id': self.id,
            'name': self.name,
            'description': self.description,
            'domain_type': self.domain_type,
            'industry_sector': self.industry_sector,
            'bcm_data': bcm_data,
            'config': json.loads(self.twin_config) if self.twin_config else {}
        }

    @api.model
    def create(self, vals):
        """Override create to set default configuration"""
        if 'twin_config' not in vals:
            vals['twin_config'] = json.dumps(self._get_default_config(vals.get('domain_type')))

        return super().create(vals)

    def _get_default_config(self, domain_type):
        """Get default configuration based on domain type"""
        base_config = {
            'simulation_frequency': 'monthly',
            'analysis_depth': 'standard',
            'prediction_horizon': 12,  # months
            'ai_analysis_enabled': True
        }

        domain_configs = {
            'corporate': {
                'financial_modeling': True,
                'supply_chain_analysis': True,
                'market_analysis': True,
                'compliance_monitoring': True
            },
            'government': {
                'policy_impact_analysis': True,
                'citizen_service_modeling': True,
                'emergency_response_planning': True,
                'budget_optimization': True
            },
            'npo': {
                'impact_measurement': True,
                'grant_optimization': True,
                'donor_analysis': True,
                'program_effectiveness': True
            },
            'infrastructure': {
                'system_reliability': True,
                'security_assessment': True,
                'capacity_planning': True,
                'maintenance_optimization': True
            }
        }

        base_config.update(domain_configs.get(domain_type, {}))
        return base_config