# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import logging

_logger = logging.getLogger(__name__)

class BCMDigitalTwinIntegration(models.AbstractModel):
    """
    Abstract model for BCM modules integration with Digital Twin
    """
    _name = 'bcm.digital.twin.integration'
    _description = 'BCM Digital Twin Integration Layer'

    @api.model
    def integrate_with_bcm_client(self, client_id, twin_org_id):
        """Integrate BCM Client with Digital Twin Organization"""
        client = self.env['bcm.client'].browse(client_id)
        twin_org = self.env['bcm.digital.twin.organization'].browse(twin_org_id)

        if client and twin_org:
            twin_org.bcm_client_id = client.id

            # Sync basic data
            twin_data = {
                'client_name': client.name,
                'client_code': getattr(client, 'code', ''),
                'client_type': getattr(client, 'client_type', ''),
                'industry': getattr(client, 'industry', ''),
            }

            twin_org.twin_config = json.dumps(twin_data)

            _logger.info(f"Integrated BCM Client {client.name} with Digital Twin Organization {twin_org.name}")
            return True
        return False

    @api.model
    def sync_bcm_context(self, context_id, twin_org_id):
        """Sync BCM Context with Digital Twin"""
        context = self.env['bcm.context'].browse(context_id)
        twin_org = self.env['bcm.digital.twin.organization'].browse(twin_org_id)

        if context and twin_org:
            context_data = {
                'business_units': getattr(context, 'business_units', []),
                'critical_functions': getattr(context, 'critical_functions', []),
                'stakeholders': getattr(context, 'stakeholders', []),
                'regulatory_requirements': getattr(context, 'regulatory_requirements', [])
            }

            # Update twin configuration
            config = json.loads(twin_org.twin_config or '{}')
            config['bcm_context'] = context_data
            twin_org.twin_config = json.dumps(config)

            return True
        return False

    @api.model
    def sync_with_bcm_bia(self, bia_id, simulation_id):
        """Sync BCM BIA with Digital Twin Simulation"""
        bia = self.env['bcm.bia'].browse(bia_id)
        simulation = self.env['bcm.digital.twin.simulation'].browse(simulation_id)

        if bia and simulation:
            simulation.related_bia = bia.id

            # Add BIA data to simulation parameters
            bia_data = {
                'critical_functions': getattr(bia, 'critical_functions', []),
                'recovery_time_objectives': getattr(bia, 'rto', {}),
                'recovery_point_objectives': getattr(bia, 'rpo', {}),
                'impact_analysis': getattr(bia, 'impact_analysis', {})
            }

            params = json.loads(simulation.parameters or '{}')
            params['bia_data'] = bia_data
            simulation.parameters = json.dumps(params)

            return True
        return False

    @api.model
    def sync_with_bcm_risk(self, risk_id, simulation_id):
        """Sync BCM Risk Management with Digital Twin Simulation"""
        risk = self.env['bcm.risk.management'].browse(risk_id)
        simulation = self.env['bcm.digital.twin.simulation'].browse(simulation_id)

        if risk and simulation:
            simulation.related_risk = risk.id

            # Add risk data to simulation
            risk_data = {
                'risk_type': getattr(risk, 'risk_type', ''),
                'risk_level': getattr(risk, 'risk_level', ''),
                'probability': getattr(risk, 'probability', 0),
                'impact': getattr(risk, 'impact', 0),
                'mitigation_strategies': getattr(risk, 'mitigation_strategies', [])
            }

            params = json.loads(simulation.parameters or '{}')
            params['risk_data'] = risk_data
            simulation.parameters = json.dumps(params)

            return True
        return False

    @api.model
    def sync_with_bcm_incident(self, incident_id, simulation_id):
        """Sync BCM Incident with Digital Twin Simulation"""
        incident = self.env['bcm.incident'].browse(incident_id)
        simulation = self.env['bcm.digital.twin.simulation'].browse(simulation_id)

        if incident and simulation:
            simulation.related_incident = incident.id

            # Add incident data for crisis simulation
            incident_data = {
                'incident_type': getattr(incident, 'incident_type', ''),
                'severity': getattr(incident, 'severity', ''),
                'affected_areas': getattr(incident, 'affected_areas', []),
                'response_time': getattr(incident, 'response_time', 0),
                'recovery_actions': getattr(incident, 'recovery_actions', [])
            }

            params = json.loads(simulation.parameters or '{}')
            params['incident_data'] = incident_data
            simulation.parameters = json.dumps(params)

            # Set simulation type for crisis management
            simulation.scenario_type = 'crisis_management'

            return True
        return False

    @api.model
    def sync_with_bcm_ai_control(self, ai_control_id, orchestrator_id):
        """Sync BCM AI Control with AI Twin Orchestrator"""
        ai_control = self.env['bcm.ai.control'].browse(ai_control_id) if self.env.get('bcm.ai.control') else None
        orchestrator = self.env['bcm.ai.twin.orchestrator'].browse(orchestrator_id)

        if ai_control and orchestrator:
            # Get AI organs status from BCM AI Control
            ai_organs_status = {}

            # Map BCM AI organs to orchestrator
            organ_mapping = {
                'governance_brain': 'bcm_governance',
                'emergency_response': 'bcm_emergency',
                'impact_oracle': 'bcm_impact',
                'scenario_creator': 'bcm_scenario',
                'risk_advisor': 'bcm_risk',
                'compliance_guardian': 'bcm_compliance',
                'performance_analyst': 'bcm_performance',
                'learning_coach': 'bcm_learning',
                'plan_generator': 'bcm_plan',
                'lifecycle_monitor': 'bcm_lifecycle'
            }

            for organ, bcm_field in organ_mapping.items():
                if hasattr(ai_control, bcm_field):
                    ai_organs_status[organ] = {
                        'available': True,
                        'status': getattr(ai_control, f'{bcm_field}_status', 'inactive'),
                        'last_run': getattr(ai_control, f'{bcm_field}_last_run', '')
                    }
                else:
                    ai_organs_status[organ] = {'available': False}

            orchestrator.organs_status = json.dumps(ai_organs_status)

            return True
        return False

class BCMClientDigitalTwin(models.Model):
    """Extension of BCM Client for Digital Twin"""
    _inherit = 'bcm.client'

    digital_twin_ids = fields.One2many(
        'bcm.digital.twin.organization',
        'bcm_client_id',
        string='Digital Twins'
    )

    digital_twin_count = fields.Integer(
        string='Digital Twin Count',
        compute='_compute_digital_twin_count'
    )

    has_active_twin = fields.Boolean(
        string='Has Active Digital Twin',
        compute='_compute_has_active_twin'
    )

    @api.depends('digital_twin_ids')
    def _compute_digital_twin_count(self):
        for record in self:
            record.digital_twin_count = len(record.digital_twin_ids)

    @api.depends('digital_twin_ids', 'digital_twin_ids.twin_status')
    def _compute_has_active_twin(self):
        for record in self:
            record.has_active_twin = any(
                twin.twin_status == 'active'
                for twin in record.digital_twin_ids
            )

    def action_create_digital_twin(self):
        """Create Digital Twin for this BCM Client"""
        return {
            'name': _('Create Digital Twin'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.digital.twin.organization',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_bcm_client_id': self.id,
                'default_name': f"Digital Twin - {self.name}",
                'default_domain_type': getattr(self, 'client_type', 'corporate')
            }
        }

    def action_view_digital_twins(self):
        """View Digital Twins for this client"""
        return {
            'name': _('Digital Twins'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.digital.twin.organization',
            'view_mode': 'tree,form',
            'domain': [('bcm_client_id', '=', self.id)],
            'context': {'default_bcm_client_id': self.id}
        }

class BCMIncidentDigitalTwin(models.Model):
    """Extension of BCM Incident for Digital Twin Simulations"""
    _inherit = 'bcm.incident'

    digital_twin_simulation_ids = fields.One2many(
        'bcm.digital.twin.simulation',
        'related_incident',
        string='Digital Twin Simulations'
    )

    simulation_count = fields.Integer(
        string='Simulation Count',
        compute='_compute_simulation_count'
    )

    @api.depends('digital_twin_simulation_ids')
    def _compute_simulation_count(self):
        for record in self:
            record.simulation_count = len(record.digital_twin_simulation_ids)

    def action_run_crisis_simulation(self):
        """Run crisis management simulation for this incident"""
        # Find organization's digital twin
        if self.client_id and self.client_id.digital_twin_ids:
            twin_org = self.client_id.digital_twin_ids.filtered(
                lambda t: t.twin_status == 'active'
            )[:1]

            if twin_org:
                return {
                    'name': _('Crisis Simulation'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'bcm.digital.twin.simulation',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_organization_id': twin_org.id,
                        'default_related_incident': self.id,
                        'default_scenario_type': 'crisis_management',
                        'default_name': f"Crisis Simulation - {self.name}"
                    }
                }

        raise UserError(_("No active Digital Twin found for this client"))

class BCMRiskDigitalTwin(models.Model):
    """Extension of BCM Risk Management for Digital Twin"""
    _inherit = 'bcm.risk.management'

    digital_twin_simulation_ids = fields.One2many(
        'bcm.digital.twin.simulation',
        'related_risk',
        string='Risk Simulations'
    )

    def action_run_risk_simulation(self):
        """Run risk assessment simulation"""
        # Find organization's digital twin
        if hasattr(self, 'client_id') and self.client_id.digital_twin_ids:
            twin_org = self.client_id.digital_twin_ids.filtered(
                lambda t: t.twin_status == 'active'
            )[:1]

            if twin_org:
                return {
                    'name': _('Risk Simulation'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'bcm.digital.twin.simulation',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_organization_id': twin_org.id,
                        'default_related_risk': self.id,
                        'default_scenario_type': 'risk_assessment',
                        'default_name': f"Risk Simulation - {self.name}"
                    }
                }

class BCMBIADigitalTwin(models.Model):
    """Extension of BCM BIA for Digital Twin"""
    _inherit = 'bcm.bia'

    digital_twin_simulation_ids = fields.One2many(
        'bcm.digital.twin.simulation',
        'related_bia',
        string='BIA Simulations'
    )

    def action_run_impact_simulation(self):
        """Run business impact simulation"""
        # Find organization's digital twin
        if hasattr(self, 'client_id') and self.client_id.digital_twin_ids:
            twin_org = self.client_id.digital_twin_ids.filtered(
                lambda t: t.twin_status == 'active'
            )[:1]

            if twin_org:
                return {
                    'name': _('Impact Simulation'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'bcm.digital.twin.simulation',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_organization_id': twin_org.id,
                        'default_related_bia': self.id,
                        'default_scenario_type': 'impact_analysis',
                        'default_name': f"Impact Simulation - {self.name}"
                    }
                }