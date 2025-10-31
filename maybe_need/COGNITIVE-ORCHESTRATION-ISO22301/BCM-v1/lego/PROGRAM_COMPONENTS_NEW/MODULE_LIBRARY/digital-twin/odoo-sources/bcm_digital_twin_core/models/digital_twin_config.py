# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json
import logging

_logger = logging.getLogger(__name__)

class DigitalTwinConfig(models.Model):
    _name = 'bcm.digital.twin.config'
    _description = 'Digital Twin Configuration'
    _order = 'name'

    name = fields.Char(
        string='Configuration Name',
        required=True
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    # Service Configuration
    service_url = fields.Char(
        string='Digital Twin Service URL',
        default='http://localhost:3001',
        help="Base URL for the Digital Twin Node.js service"
    )

    api_key = fields.Char(
        string='API Key',
        help="API key for authentication with Digital Twin service"
    )

    timeout = fields.Integer(
        string='Request Timeout (seconds)',
        default=30
    )

    retry_count = fields.Integer(
        string='Retry Count',
        default=3,
        help="Number of retry attempts for failed requests"
    )

    # Domain-specific Configurations
    domain_configs = fields.Text(
        string='Domain Configurations',
        help='JSON configuration for different domains'
    )

    # Simulation Settings
    default_simulation_mode = fields.Selection([
        ('quick', 'Quick Analysis'),
        ('standard', 'Standard'),
        ('deep', 'Deep Analysis')
    ], string='Default Simulation Mode', default='standard')

    enable_caching = fields.Boolean(
        string='Enable Result Caching',
        default=True
    )

    cache_duration = fields.Integer(
        string='Cache Duration (hours)',
        default=24
    )

    # AI Integration Settings
    enable_ai_analysis = fields.Boolean(
        string='Enable AI Analysis',
        default=True
    )

    ai_confidence_threshold = fields.Float(
        string='AI Confidence Threshold',
        default=70.0,
        help="Minimum confidence score for AI recommendations (0-100)"
    )

    # Performance Settings
    max_concurrent_simulations = fields.Integer(
        string='Max Concurrent Simulations',
        default=5
    )

    batch_processing_enabled = fields.Boolean(
        string='Enable Batch Processing',
        default=True
    )

    batch_size = fields.Integer(
        string='Batch Size',
        default=10
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )

    @api.model
    def get_active_config(self):
        """Get the active configuration"""
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            # Create default config if none exists
            config = self.create({
                'name': 'Default Configuration',
                'active': True,
                'domain_configs': json.dumps(self._get_default_domain_configs())
            })
        return config

    def _get_default_domain_configs(self):
        """Get default domain-specific configurations"""
        return {
            'corporate': {
                'financial_modeling_depth': 'detailed',
                'supply_chain_levels': 3,
                'market_analysis_scope': 'global',
                'compliance_frameworks': ['SOX', 'GDPR', 'ISO27001']
            },
            'government': {
                'citizen_service_categories': ['health', 'education', 'safety', 'infrastructure'],
                'emergency_response_levels': 5,
                'budget_categories': ['operational', 'capital', 'emergency', 'reserve'],
                'policy_impact_horizon': 36  # months
            },
            'npo': {
                'impact_measurement_framework': 'SROI',
                'grant_categories': ['operational', 'project', 'capacity', 'emergency'],
                'beneficiary_tracking': True,
                'donor_segments': ['individual', 'corporate', 'foundation', 'government']
            },
            'infrastructure': {
                'system_criticality_levels': 5,
                'maintenance_windows': 'quarterly',
                'redundancy_requirements': 'N+1',
                'security_framework': 'NIST'
            }
        }

    @api.constrains('domain_configs')
    def _check_domain_configs(self):
        for record in self:
            if record.domain_configs:
                try:
                    json.loads(record.domain_configs)
                except ValueError:
                    raise ValidationError(_("Domain Configurations must be valid JSON"))

    @api.constrains('ai_confidence_threshold')
    def _check_confidence_threshold(self):
        for record in self:
            if not 0 <= record.ai_confidence_threshold <= 100:
                raise ValidationError(_("AI Confidence Threshold must be between 0 and 100"))

    def test_connection(self):
        """Test connection to Digital Twin service"""
        self.ensure_one()

        bridge = self.env['bcm.digital.twin.bridge']
        result = bridge.test_connection()

        if result['success']:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Success"),
                    'message': _("Connection successful. Service version: %s") % result.get('version', 'unknown'),
                    'type': 'success'
                }
            }
        else:
            raise ValidationError(_("Connection failed: %s") % result['message'])

    def apply_configuration(self):
        """Apply this configuration as active"""
        # Deactivate all other configurations
        self.search([('id', '!=', self.id)]).write({'active': False})

        # Activate this configuration
        self.active = True

        # Update system parameters
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('digital_twin.service_url', self.service_url)
        params.set_param('digital_twin.api_key', self.api_key or '')
        params.set_param('digital_twin.timeout', str(self.timeout))
        params.set_param('digital_twin.retry_count', str(self.retry_count))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Success"),
                'message': _("Configuration applied successfully"),
                'type': 'success'
            }
        }

class DigitalTwinGlobalSettings(models.TransientModel):
    _name = 'bcm.digital.twin.settings'
    _inherit = 'res.config.settings'
    _description = 'Digital Twin Settings'

    # Service Settings
    dt_service_url = fields.Char(
        string='Service URL',
        config_parameter='digital_twin.service_url',
        default='http://localhost:3001'
    )

    dt_api_key = fields.Char(
        string='API Key',
        config_parameter='digital_twin.api_key'
    )

    dt_timeout = fields.Integer(
        string='Timeout (seconds)',
        config_parameter='digital_twin.timeout',
        default=30
    )

    # Feature Toggles
    dt_enable_ai = fields.Boolean(
        string='Enable AI Analysis',
        config_parameter='digital_twin.enable_ai',
        default=True
    )

    dt_enable_caching = fields.Boolean(
        string='Enable Caching',
        config_parameter='digital_twin.enable_caching',
        default=True
    )

    dt_enable_batch = fields.Boolean(
        string='Enable Batch Processing',
        config_parameter='digital_twin.enable_batch',
        default=True
    )

    # Performance Settings
    dt_max_concurrent = fields.Integer(
        string='Max Concurrent Simulations',
        config_parameter='digital_twin.max_concurrent',
        default=5
    )

    dt_cache_duration = fields.Integer(
        string='Cache Duration (hours)',
        config_parameter='digital_twin.cache_duration',
        default=24
    )

    @api.model
    def get_values(self):
        res = super(DigitalTwinGlobalSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()

        res.update(
            dt_service_url=params.get_param('digital_twin.service_url', 'http://localhost:3001'),
            dt_api_key=params.get_param('digital_twin.api_key', ''),
            dt_timeout=int(params.get_param('digital_twin.timeout', '30')),
            dt_enable_ai=params.get_param('digital_twin.enable_ai', 'True').lower() == 'true',
            dt_enable_caching=params.get_param('digital_twin.enable_caching', 'True').lower() == 'true',
            dt_enable_batch=params.get_param('digital_twin.enable_batch', 'True').lower() == 'true',
            dt_max_concurrent=int(params.get_param('digital_twin.max_concurrent', '5')),
            dt_cache_duration=int(params.get_param('digital_twin.cache_duration', '24')),
        )
        return res

    def test_dt_connection(self):
        """Test Digital Twin service connection"""
        bridge = self.env['bcm.digital.twin.bridge']
        bridge.setup_service_parameters(
            self.dt_service_url,
            self.dt_api_key,
            self.dt_timeout
        )

        result = bridge.test_connection()

        if result['success']:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Success"),
                    'message': _("Connection test successful"),
                    'type': 'success'
                }
            }
        else:
            raise ValidationError(_("Connection test failed: %s") % result['message'])