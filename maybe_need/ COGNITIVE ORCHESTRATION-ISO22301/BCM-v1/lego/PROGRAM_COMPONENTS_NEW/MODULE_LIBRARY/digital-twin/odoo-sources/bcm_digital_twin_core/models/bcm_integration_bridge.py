# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class BCMIntegrationBridge(models.Model):
    """
    Central integration bridge between BCM modules and Digital Twin
    Manages all cross-module data synchronization and coordination
    """
    _name = 'bcm.integration.bridge'
    _description = 'BCM Digital Twin Integration Bridge'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, create_date desc'

    name = fields.Char(
        string='Integration Name',
        required=True,
        default=lambda self: _('New Integration')
    )

    integration_type = fields.Selection([
        ('client', 'BCM Client Integration'),
        ('context', 'BCM Context Integration'),
        ('bia', 'Business Impact Analysis'),
        ('risk', 'Risk Management'),
        ('incident', 'Incident Management'),
        ('strategy', 'Strategy Integration'),
        ('plan', 'Plan Management'),
        ('exercise', 'Exercise & Testing'),
        ('audit', 'Audit & Compliance'),
        ('governance', 'Governance'),
        ('lifecycle', 'Lifecycle Management'),
        ('training', 'Training & Awareness'),
        ('metrics', 'Metrics & KPIs'),
        ('review', 'Management Review'),
        ('vendor', 'Vendor Management'),
        ('crisis', 'Crisis Management'),
        ('recovery', 'Recovery Management'),
        ('communication', 'Communication Management'),
        ('resource', 'Resource Management'),
        ('documentation', 'Documentation'),
        ('change', 'Change Management'),
        ('it_dr', 'IT Disaster Recovery'),
        ('facilities', 'Facilities Management')
    ], string='Integration Type', required=True)

    source_model = fields.Char(
        string='Source Model',
        help='BCM module model name'
    )

    source_record_id = fields.Integer(
        string='Source Record ID'
    )

    target_model = fields.Char(
        string='Target Model',
        default='bcm.digital.twin.organization'
    )

    target_record_id = fields.Integer(
        string='Target Record ID'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('syncing', 'Syncing'),
        ('paused', 'Paused'),
        ('error', 'Error'),
        ('archived', 'Archived')
    ], string='Status', default='draft', tracking=True)

    priority = fields.Selection([
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Priority', default='normal')

    sync_mode = fields.Selection([
        ('manual', 'Manual'),
        ('scheduled', 'Scheduled'),
        ('realtime', 'Real-time'),
        ('batch', 'Batch')
    ], string='Sync Mode', default='manual')

    sync_frequency = fields.Integer(
        string='Sync Frequency (hours)',
        default=24
    )

    last_sync_date = fields.Datetime(
        string='Last Sync',
        tracking=True
    )

    next_sync_date = fields.Datetime(
        string='Next Sync',
        compute='_compute_next_sync',
        store=True
    )

    sync_data = fields.Text(
        string='Sync Configuration',
        help='JSON configuration for data mapping'
    )

    error_log = fields.Text(
        string='Error Log'
    )

    success_count = fields.Integer(
        string='Successful Syncs',
        default=0
    )

    error_count = fields.Integer(
        string='Failed Syncs',
        default=0
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    @api.depends('last_sync_date', 'sync_frequency', 'sync_mode')
    def _compute_next_sync(self):
        for record in self:
            if record.sync_mode == 'scheduled' and record.last_sync_date:
                record.next_sync_date = record.last_sync_date + timedelta(hours=record.sync_frequency)
            else:
                record.next_sync_date = False

    def action_activate(self):
        """Activate integration"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Only draft integrations can be activated"))

        # Validate configuration
        self._validate_integration()

        self.state = 'active'
        self.message_post(
            body=_("Integration activated"),
            message_type='notification'
        )

        # Perform initial sync
        if self.sync_mode in ['realtime', 'scheduled']:
            self.action_sync()

    def action_sync(self):
        """Perform synchronization"""
        self.ensure_one()

        if self.state not in ['active', 'error']:
            raise UserError(_("Integration must be active to sync"))

        self.state = 'syncing'

        try:
            # Get sync method based on integration type
            sync_method = getattr(self, f'_sync_{self.integration_type}', None)

            if sync_method:
                result = sync_method()

                if result:
                    self.success_count += 1
                    self.last_sync_date = fields.Datetime.now()
                    self.state = 'active'

                    self.message_post(
                        body=_("Synchronization completed successfully"),
                        message_type='notification'
                    )
                else:
                    raise UserError(_("Synchronization failed"))
            else:
                raise UserError(_("Sync method not implemented for %s") % self.integration_type)

        except Exception as e:
            self.error_count += 1
            self.state = 'error'
            self.error_log = str(e)

            _logger.error(f"Integration sync failed: {str(e)}")

            self.message_post(
                body=_("Synchronization failed: %s") % str(e),
                message_type='notification',
                subtype_id=self.env.ref('mail.mt_comment').id
            )

    def action_pause(self):
        """Pause integration"""
        self.ensure_one()
        if self.state == 'active':
            self.state = 'paused'
            self.message_post(
                body=_("Integration paused"),
                message_type='notification'
            )

    def action_resume(self):
        """Resume integration"""
        self.ensure_one()
        if self.state == 'paused':
            self.state = 'active'
            self.message_post(
                body=_("Integration resumed"),
                message_type='notification'
            )

    def _validate_integration(self):
        """Validate integration configuration"""
        # Check if models exist
        if self.source_model:
            source = self.env.get(self.source_model)
            if not source:
                raise UserError(_("Source model %s not found") % self.source_model)

        if self.target_model:
            target = self.env.get(self.target_model)
            if not target:
                raise UserError(_("Target model %s not found") % self.target_model)

    # Sync methods for each integration type

    def _sync_client(self):
        """Sync BCM Client data"""
        if not self.source_record_id:
            return False

        client = self.env['bcm.client'].browse(self.source_record_id)
        if not client.exists():
            return False

        # Find or create Digital Twin
        twin = self.env['bcm.digital.twin.organization'].search([
            ('bcm_client_id', '=', client.id)
        ], limit=1)

        if not twin:
            twin = self.env['bcm.digital.twin.organization'].create({
                'name': f"Digital Twin - {client.name}",
                'bcm_client_id': client.id,
                'domain_type': getattr(client, 'client_type', 'corporate')
            })

        # Update twin data
        twin_data = {
            'client_name': client.name,
            'client_code': getattr(client, 'code', ''),
            'client_type': getattr(client, 'client_type', ''),
            'industry': getattr(client, 'industry', ''),
            'size': getattr(client, 'size', ''),
            'locations': getattr(client, 'location_count', 0)
        }

        twin.twin_config = json.dumps(twin_data)
        self.target_record_id = twin.id

        return True

    def _sync_context(self):
        """Sync BCM Context data"""
        if not self.source_record_id:
            return False

        context = self.env['bcm.context'].browse(self.source_record_id)
        if not context.exists():
            return False

        # Find Digital Twin for the client
        if hasattr(context, 'client_id'):
            twin = self.env['bcm.digital.twin.organization'].search([
                ('bcm_client_id', '=', context.client_id.id)
            ], limit=1)

            if twin:
                context_data = {
                    'business_units': self._get_field_value(context, 'business_units'),
                    'critical_functions': self._get_field_value(context, 'critical_functions'),
                    'stakeholders': self._get_field_value(context, 'stakeholders'),
                    'regulatory_requirements': self._get_field_value(context, 'regulatory_requirements'),
                    'internal_factors': self._get_field_value(context, 'internal_factors'),
                    'external_factors': self._get_field_value(context, 'external_factors')
                }

                config = json.loads(twin.twin_config or '{}')
                config['bcm_context'] = context_data
                twin.twin_config = json.dumps(config)

                self.target_record_id = twin.id
                return True

        return False

    def _sync_bia(self):
        """Sync Business Impact Analysis data"""
        if not self.source_record_id:
            return False

        bia = self.env['bcm.bia'].browse(self.source_record_id)
        if not bia.exists():
            return False

        # Create simulation for BIA
        simulation_data = {
            'name': f"BIA Analysis - {bia.name}",
            'scenario_type': 'impact_analysis',
            'related_bia': bia.id,
            'parameters': json.dumps({
                'critical_functions': self._get_field_value(bia, 'critical_functions'),
                'rto': self._get_field_value(bia, 'rto'),
                'rpo': self._get_field_value(bia, 'rpo'),
                'mtd': self._get_field_value(bia, 'mtd'),
                'impact_categories': self._get_field_value(bia, 'impact_categories')
            })
        }

        # Find organization
        if hasattr(bia, 'client_id'):
            twin = self.env['bcm.digital.twin.organization'].search([
                ('bcm_client_id', '=', bia.client_id.id)
            ], limit=1)

            if twin:
                simulation_data['organization_id'] = twin.id
                simulation = self.env['bcm.digital.twin.simulation'].create(simulation_data)
                self.target_record_id = simulation.id
                return True

        return False

    def _sync_risk(self):
        """Sync Risk Management data"""
        if not self.source_record_id:
            return False

        risk = self.env['bcm.risk.management'].browse(self.source_record_id)
        if not risk.exists():
            return False

        # Create risk simulation
        simulation_data = {
            'name': f"Risk Assessment - {risk.name}",
            'scenario_type': 'risk_assessment',
            'related_risk': risk.id,
            'parameters': json.dumps({
                'risk_type': self._get_field_value(risk, 'risk_type'),
                'risk_level': self._get_field_value(risk, 'risk_level'),
                'probability': self._get_field_value(risk, 'probability'),
                'impact': self._get_field_value(risk, 'impact'),
                'controls': self._get_field_value(risk, 'controls'),
                'mitigation': self._get_field_value(risk, 'mitigation_strategies')
            })
        }

        # Find organization
        if hasattr(risk, 'client_id'):
            twin = self.env['bcm.digital.twin.organization'].search([
                ('bcm_client_id', '=', risk.client_id.id)
            ], limit=1)

            if twin:
                simulation_data['organization_id'] = twin.id
                simulation = self.env['bcm.digital.twin.simulation'].create(simulation_data)
                self.target_record_id = simulation.id
                return True

        return False

    def _sync_incident(self):
        """Sync Incident Management data"""
        if not self.source_record_id:
            return False

        incident = self.env['bcm.incident'].browse(self.source_record_id)
        if not incident.exists():
            return False

        # Create crisis simulation
        simulation_data = {
            'name': f"Crisis Simulation - {incident.name}",
            'scenario_type': 'crisis_management',
            'related_incident': incident.id,
            'parameters': json.dumps({
                'incident_type': self._get_field_value(incident, 'incident_type'),
                'severity': self._get_field_value(incident, 'severity'),
                'affected_areas': self._get_field_value(incident, 'affected_areas'),
                'response_time': self._get_field_value(incident, 'response_time'),
                'escalation_level': self._get_field_value(incident, 'escalation_level')
            })
        }

        # Find organization
        if hasattr(incident, 'client_id'):
            twin = self.env['bcm.digital.twin.organization'].search([
                ('bcm_client_id', '=', incident.client_id.id)
            ], limit=1)

            if twin:
                simulation_data['organization_id'] = twin.id
                simulation = self.env['bcm.digital.twin.simulation'].create(simulation_data)

                # Run AI analysis
                if twin.enable_ai_analysis:
                    orchestrator = self.env['bcm.ai.twin.orchestrator'].create({
                        'name': f"Crisis Analysis - {incident.name}",
                        'organization_id': twin.id,
                        'simulation_id': simulation.id,
                        'analysis_type': 'emergency',
                        'priority': 'critical'
                    })
                    orchestrator.action_run_analysis()

                self.target_record_id = simulation.id
                return True

        return False

    def _get_field_value(self, record, field_name, default=None):
        """Safely get field value from record"""
        if hasattr(record, field_name):
            value = getattr(record, field_name)

            # Handle different field types
            if isinstance(value, models.Model):
                # Many2one
                return value.id
            elif hasattr(value, '_name'):
                # Recordset (One2many, Many2many)
                return value.ids
            else:
                return value

        return default

    @api.model
    def create_integration_for_module(self, module_name, record_id):
        """Create integration for a specific BCM module record"""
        # Map module to integration type
        module_map = {
            'bcm.client': 'client',
            'bcm.context': 'context',
            'bcm.bia': 'bia',
            'bcm.risk.management': 'risk',
            'bcm.incident': 'incident',
            'bcm.strategy': 'strategy',
            'bcm.plan': 'plan',
            'bcm.exercise': 'exercise',
            'bcm.audit': 'audit'
        }

        integration_type = module_map.get(module_name)
        if not integration_type:
            return False

        # Check if integration already exists
        existing = self.search([
            ('source_model', '=', module_name),
            ('source_record_id', '=', record_id),
            ('state', 'not in', ['archived'])
        ], limit=1)

        if existing:
            return existing

        # Create new integration
        record = self.env[module_name].browse(record_id)
        if record.exists():
            integration = self.create({
                'name': f"{integration_type.title()} Integration - {record.name}",
                'integration_type': integration_type,
                'source_model': module_name,
                'source_record_id': record_id,
                'state': 'draft'
            })
            return integration

        return False

    @api.model
    def cron_sync_integrations(self):
        """Cron job to sync scheduled integrations"""
        integrations = self.search([
            ('state', '=', 'active'),
            ('sync_mode', '=', 'scheduled'),
            ('next_sync_date', '<=', fields.Datetime.now())
        ])

        for integration in integrations:
            try:
                integration.action_sync()
            except Exception as e:
                _logger.error(f"Cron sync failed for integration {integration.name}: {str(e)}")