# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class DigitalTwinScenario(models.Model):
    _name = 'bcm.digital.twin.scenario'
    _description = 'Digital Twin Scenario Simulation'
    _order = 'create_date desc'

    name = fields.Char(string='Scenario Name', required=True)
    scenario_id = fields.Many2one('bcm.scenario', string='Base Scenario', required=True)
    digital_twin_id = fields.Many2one('bcm.digital.twin', string='Target Digital Twin', required=True)

    # Simulation Status
    status = fields.Selection([
        ('draft', 'Draft'),
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], string='Status', default='draft')

    # Simulation Parameters
    simulation_type = fields.Selection([
        ('business_continuity', 'Business Continuity'),
        ('crisis_response', 'Crisis Response'),
        ('risk_assessment', 'Risk Assessment'),
        ('monte_carlo', 'Monte Carlo Risk'),
        ('compliance_gap', 'Compliance Gap Analysis')
    ], string='Simulation Type', default='business_continuity')

    # Timeline
    start_time = fields.Datetime(string='Simulation Start')
    end_time = fields.Datetime(string='Simulation End')
    duration_seconds = fields.Float(string='Duration (seconds)', compute='_compute_duration')

    # Results
    simulation_result = fields.Text(string='Simulation Results JSON')
    success_score = fields.Float(string='Success Score %')
    risk_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Risk Level')

    # Metrics
    total_events = fields.Integer(string='Total Events Simulated')
    critical_failures = fields.Integer(string='Critical Failures')
    recovery_time = fields.Float(string='Estimated Recovery Time (hours)')
    business_impact_score = fields.Float(string='Business Impact Score')

    # AI Analysis
    ai_recommendations = fields.Text(string='AI Recommendations')
    improvement_areas = fields.Text(string='Areas for Improvement')

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for record in self:
            if record.start_time and record.end_time:
                delta = record.end_time - record.start_time
                record.duration_seconds = delta.total_seconds()
            else:
                record.duration_seconds = 0

    def action_run_simulation(self):
        """Run Digital Twin simulation"""
        self.status = 'queued'
        self.start_time = fields.Datetime.now()

        try:
            # Get Digital Twin service URL
            dt_service_url = self.env['ir.config_parameter'].sudo().get_param(
                'digital_twin.service_url', 'http://localhost:3000'
            )

            # Prepare simulation data
            simulation_data = {
                'scenario_name': self.scenario_id.name,
                'scenario_type': self.simulation_type,
                'digital_twin_id': self.digital_twin_id.external_id,
                'parameters': {
                    'severity': self.scenario_id.severity_level,
                    'duration': self.scenario_id.duration_hours,
                    'affected_processes': self._get_affected_processes(),
                    'recovery_objectives': self._get_recovery_objectives()
                }
            }

            self.status = 'running'

            # Make API call to Digital Twin simulation endpoint
            response = requests.post(
                f"{dt_service_url}/api/bcm/scenarios/{self.simulation_type}",
                json=simulation_data,
                timeout=300  # 5 minutes timeout
            )

            if response.status_code == 200:
                result = response.json()
                self._process_simulation_results(result)
                self.status = 'completed'
                self.end_time = fields.Datetime.now()

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Simulation Completed',
                        'message': f'Digital Twin simulation completed successfully. Success Score: {self.success_score}%',
                        'type': 'success'
                    }
                }
            else:
                raise Exception(f"Simulation API returned status {response.status_code}")

        except Exception as e:
            self.status = 'failed'
            self.end_time = fields.Datetime.now()
            _logger.error(f"Digital Twin simulation failed: {e}")

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Simulation Failed',
                    'message': f'Simulation failed: {str(e)}',
                    'type': 'danger'
                }
            }

    def _get_affected_processes(self):
        """Get affected business processes from scenario"""
        # Extract from scenario description or related models
        return {
            'critical_processes': self.scenario_id.affected_processes.mapped('name') if hasattr(self.scenario_id, 'affected_processes') else [],
            'support_processes': [],
            'external_dependencies': []
        }

    def _get_recovery_objectives(self):
        """Get recovery time and point objectives"""
        return {
            'rto_hours': 4,  # Default Recovery Time Objective
            'rpo_hours': 1,  # Default Recovery Point Objective
            'mtd_hours': 24  # Maximum Tolerable Downtime
        }

    def _process_simulation_results(self, api_result):
        """Process simulation results from Digital Twin API"""
        if 'data' in api_result:
            results = api_result['data']

            # Store raw results
            self.simulation_result = json.dumps(results, indent=2)

            # Extract key metrics
            self.success_score = results.get('success_rate', 0) * 100
            self.total_events = results.get('total_events', 0)
            self.critical_failures = results.get('critical_failures', 0)
            self.recovery_time = results.get('avg_recovery_time_hours', 0)
            self.business_impact_score = results.get('business_impact_score', 0)

            # Determine risk level
            if self.success_score >= 90:
                self.risk_level = 'low'
            elif self.success_score >= 70:
                self.risk_level = 'medium'
            elif self.success_score >= 50:
                self.risk_level = 'high'
            else:
                self.risk_level = 'critical'

            # Extract AI recommendations
            self.ai_recommendations = results.get('ai_analysis', {}).get('recommendations', '')
            self.improvement_areas = results.get('ai_analysis', {}).get('improvement_areas', '')

    def action_view_results(self):
        """View detailed simulation results"""
        return {
            'name': 'Simulation Results',
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.digital.twin.scenario',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('bcm_scenario_hub.view_digital_twin_scenario_results_form').id,
            'target': 'new',
        }

    def action_create_improvement_plan(self):
        """Create improvement plan based on simulation results"""
        if not self.ai_recommendations:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Recommendations',
                    'message': 'No AI recommendations available. Run simulation first.',
                    'type': 'warning'
                }
            }

        # Create BCM plan with AI recommendations
        plan_vals = {
            'name': f"Improvement Plan - {self.name}",
            'bcm_client_id': self.digital_twin_id.bcm_client_id.id,
            'plan_type': 'improvement',
            'description': self.ai_recommendations,
            'source_simulation_id': self.id,
        }

        # This assumes bcm_plans module exists
        if 'bcm.plan' in self.env:
            plan = self.env['bcm.plan'].create(plan_vals)
            return {
                'name': 'Improvement Plan',
                'type': 'ir.actions.act_window',
                'res_model': 'bcm.plan',
                'res_id': plan.id,
                'view_mode': 'form',
                'target': 'current',
            }

    @api.model
    def run_scheduled_simulations(self):
        """Scheduled method to run automated simulations"""
        scenarios = self.search([
            ('status', '=', 'draft'),
            ('scenario_id.is_automated', '=', True)  # Assuming scenarios have automation flag
        ])

        for scenario in scenarios:
            scenario.action_run_simulation()

        return True


class BCMScenario(models.Model):
    _inherit = 'bcm.scenario'

    # Add Digital Twin integration fields
    digital_twin_simulation_ids = fields.One2many(
        'bcm.digital.twin.scenario',
        'scenario_id',
        string='Digital Twin Simulations'
    )

    simulation_count = fields.Integer(
        string='Simulation Count',
        compute='_compute_simulation_count'
    )

    is_automated = fields.Boolean(string='Automated Simulation', default=False)
    simulation_frequency = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ], string='Simulation Frequency')

    @api.depends('digital_twin_simulation_ids')
    def _compute_simulation_count(self):
        for record in self:
            record.simulation_count = len(record.digital_twin_simulation_ids)

    def action_run_on_digital_twin(self):
        """Quick action to run scenario on Digital Twin"""
        # Get default or first available Digital Twin
        digital_twin = self.env['bcm.digital.twin'].search([], limit=1)

        if not digital_twin:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Digital Twin',
                    'message': 'No Digital Twin available for simulation',
                    'type': 'warning'
                }
            }

        # Create and run simulation
        simulation = self.env['bcm.digital.twin.scenario'].create({
            'name': f"Simulation - {self.name}",
            'scenario_id': self.id,
            'digital_twin_id': digital_twin.id,
            'simulation_type': 'business_continuity'
        })

        return simulation.action_run_simulation()

    def action_view_simulations(self):
        """View all Digital Twin simulations for this scenario"""
        return {
            'name': f'Simulations - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.digital.twin.scenario',
            'domain': [('scenario_id', '=', self.id)],
            'view_mode': 'tree,form',
            'context': {'default_scenario_id': self.id}
        }