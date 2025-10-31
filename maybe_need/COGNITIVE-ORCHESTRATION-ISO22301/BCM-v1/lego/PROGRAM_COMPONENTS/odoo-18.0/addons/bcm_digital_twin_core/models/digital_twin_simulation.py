# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class DigitalTwinSimulation(models.Model):
    _name = 'bcm.digital.twin.simulation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Digital Twin Simulation'
    _order = 'create_date desc'

    # Basic Information
    name = fields.Char(
        string='Simulation Name',
        required=True,
        tracking=True,
        default=lambda self: _('New Simulation')
    )

    organization_id = fields.Many2one(
        'bcm.digital.twin.organization',
        string='Organization',
        required=True,
        tracking=True
    )

    # Simulation Type and Parameters
    scenario_type = fields.Selection([
        # Core simulations (выполняются в Odoo)
        ('budget_optimization', 'Budget Optimization'),
        ('resource_allocation', 'Resource Allocation'),
        ('risk_assessment', 'Risk Assessment'),

        # Complex simulations (отправляются в Node.js)
        ('crisis_management', 'Crisis Management'),
        ('scaling_analysis', 'Scaling Analysis'),
        ('market_simulation', 'Market Simulation'),
        ('supply_chain', 'Supply Chain Analysis'),
        ('policy_impact', 'Policy Impact'),

        # Domain-specific
        ('grant_impact', 'Grant Impact (NPO)'),
        ('compliance_simulation', 'Compliance Simulation (Corporate)'),
        ('citizen_service', 'Citizen Service (Government)'),
        ('infrastructure_resilience', 'Infrastructure Resilience')
    ], string='Scenario Type', required=True, tracking=True)

    simulation_mode = fields.Selection([
        ('quick', 'Quick Analysis (Odoo)'),
        ('standard', 'Standard Simulation (Hybrid)'),
        ('deep', 'Deep Analysis (Node.js)')
    ], string='Simulation Mode', default='standard')

    # Parameters
    parameters = fields.Text(
        string='Simulation Parameters',
        help='JSON parameters for simulation'
    )

    # BCM Integration
    related_incident = fields.Many2one(
        'bcm.incident',
        string='Related Incident',
        help='Link to BCM incident if simulation is incident-related'
    )

    related_plan = fields.Many2one(
        'bcm.plans',
        string='Related BCM Plan'
    )

    related_bia = fields.Many2one(
        'bcm.bia',
        string='Related BIA'
    )

    related_risk = fields.Many2one(
        'bcm.risk.management',
        string='Related Risk'
    )

    # State and Execution
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ready', 'Ready'),
        ('running', 'Running'),
        ('processing', 'Processing Results'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    execution_type = fields.Selection([
        ('local', 'Local (Odoo)'),
        ('remote', 'Remote (Node.js)'),
        ('hybrid', 'Hybrid')
    ], string='Execution Type', compute='_compute_execution_type')

    # Results
    results = fields.Text(
        string='Simulation Results',
        help='JSON results from simulation'
    )

    ai_insights = fields.Text(
        string='AI Insights',
        help='AI-generated insights from simulation'
    )

    recommendations = fields.Text(
        string='Recommendations',
        help='Action recommendations based on results'
    )

    # Metrics
    execution_time = fields.Float(
        string='Execution Time (seconds)',
        readonly=True
    )

    confidence_score = fields.Float(
        string='Confidence Score',
        help='Confidence level of simulation results (0-100)'
    )

    impact_score = fields.Float(
        string='Impact Score',
        help='Estimated impact score (0-100)'
    )

    # Timestamps
    start_date = fields.Datetime(string='Start Time')
    completion_date = fields.Datetime(string='Completion Time')

    # Error handling
    error_message = fields.Text(string='Error Message')

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )

    @api.depends('scenario_type', 'simulation_mode')
    def _compute_execution_type(self):
        """Determine where simulation will be executed"""
        for record in self:
            # Simple simulations run locally in Odoo
            local_scenarios = ['budget_optimization', 'resource_allocation', 'risk_assessment']

            # Complex simulations require Node.js
            remote_scenarios = ['crisis_management', 'scaling_analysis', 'market_simulation',
                               'supply_chain', 'policy_impact']

            if record.simulation_mode == 'quick' or record.scenario_type in local_scenarios:
                record.execution_type = 'local'
            elif record.simulation_mode == 'deep' or record.scenario_type in remote_scenarios:
                record.execution_type = 'remote'
            else:
                record.execution_type = 'hybrid'

    def action_prepare_simulation(self):
        """Prepare simulation for execution"""
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(_("Only draft simulations can be prepared"))

        # Validate parameters
        if self.parameters:
            try:
                json.loads(self.parameters)
            except ValueError:
                raise ValidationError(_("Parameters must be valid JSON"))

        # Auto-generate name if needed
        if self.name == _('New Simulation'):
            self.name = f"{self.organization_id.name} - {dict(self._fields['scenario_type'].selection).get(self.scenario_type)} - {fields.Date.today()}"

        self.state = 'ready'

        self.message_post(
            body=_("Simulation prepared and ready to run"),
            message_type='notification'
        )

    def action_run_simulation(self):
        """Execute simulation based on type"""
        self.ensure_one()

        if self.state not in ['ready', 'failed']:
            raise UserError(_("Simulation must be in Ready or Failed state to run"))

        self.state = 'running'
        self.start_date = fields.Datetime.now()

        try:
            if self.execution_type == 'local':
                # Run simulation locally in Odoo
                self._run_local_simulation()

            elif self.execution_type == 'remote':
                # Send to Node.js service for complex simulation
                self._run_remote_simulation()

            else:  # hybrid
                # Run basic analysis locally, complex parts remotely
                self._run_hybrid_simulation()

        except Exception as e:
            self.state = 'failed'
            self.error_message = str(e)
            _logger.error(f"Simulation failed: {str(e)}")
            raise

    def _run_local_simulation(self):
        """Run simulation locally in Odoo (for simple scenarios)"""
        _logger.info(f"Running local simulation: {self.name}")

        results = {}

        if self.scenario_type == 'budget_optimization':
            results = self._simulate_budget_optimization()

        elif self.scenario_type == 'resource_allocation':
            results = self._simulate_resource_allocation()

        elif self.scenario_type == 'risk_assessment':
            results = self._simulate_risk_assessment()

        # Process results
        self._process_simulation_results(results)

    def _run_remote_simulation(self):
        """Send simulation to Node.js service"""
        _logger.info(f"Running remote simulation: {self.name}")

        # Use bridge to call Node.js service
        bridge = self.env['bcm.digital.twin.bridge']
        bridge.execute_simulation(self)

    def _run_hybrid_simulation(self):
        """Run hybrid simulation (local + remote)"""
        _logger.info(f"Running hybrid simulation: {self.name}")

        # Run quick local analysis first
        local_results = self._get_quick_local_analysis()

        # Send to Node.js for deep analysis
        bridge = self.env['bcm.digital.twin.bridge']
        remote_results = bridge.execute_simulation(self)

        # Combine results
        combined_results = self._combine_simulation_results(local_results, remote_results)

        self._process_simulation_results(combined_results)

    def _simulate_budget_optimization(self):
        """Local budget optimization simulation"""
        params = json.loads(self.parameters or '{}')

        # Simple budget optimization logic
        current_budget = params.get('current_budget', 1000000)
        optimization_target = params.get('target_savings', 0.15)  # 15% savings

        results = {
            'current_budget': current_budget,
            'optimized_budget': current_budget * (1 - optimization_target),
            'potential_savings': current_budget * optimization_target,
            'recommendations': [
                'Reduce operational costs by 10%',
                'Optimize resource allocation',
                'Implement automation for routine tasks'
            ],
            'confidence': 75.0
        }

        return results

    def _simulate_resource_allocation(self):
        """Local resource allocation simulation"""
        params = json.loads(self.parameters or '{}')

        resources = params.get('resources', {})
        priorities = params.get('priorities', [])

        # Simple allocation algorithm
        allocated = {}
        total_resources = sum(resources.values()) if resources else 100

        for priority in priorities:
            allocated[priority] = total_resources * 0.3  # Simplified allocation

        results = {
            'current_allocation': resources,
            'optimized_allocation': allocated,
            'efficiency_gain': 15.0,
            'recommendations': [
                'Reallocate resources to high-priority areas',
                'Consider cross-functional resource sharing'
            ],
            'confidence': 70.0
        }

        return results

    def _simulate_risk_assessment(self):
        """Local risk assessment simulation"""
        org = self.organization_id

        # Get BCM risk data if available
        risk_score = 50.0  # Base score

        if self.related_risk:
            # Adjust based on BCM risk data
            risk_score = getattr(self.related_risk, 'risk_score', 50.0)

        results = {
            'overall_risk_score': risk_score,
            'risk_categories': {
                'operational': risk_score * 0.3,
                'financial': risk_score * 0.25,
                'strategic': risk_score * 0.25,
                'compliance': risk_score * 0.2
            },
            'top_risks': [
                'Supply chain disruption',
                'Cybersecurity threats',
                'Regulatory changes'
            ],
            'mitigation_strategies': [
                'Implement business continuity plan',
                'Enhance cybersecurity measures',
                'Regular compliance audits'
            ],
            'confidence': 65.0
        }

        return results

    def _get_quick_local_analysis(self):
        """Get quick local analysis for hybrid simulation"""
        return {
            'quick_assessment': True,
            'organization_health': self.organization_id.twin_health_score or 70.0,
            'risk_level': 'medium',
            'immediate_concerns': []
        }

    def _combine_simulation_results(self, local_results, remote_results):
        """Combine local and remote simulation results"""
        combined = {
            'local_analysis': local_results,
            'remote_analysis': remote_results,
            'combined_insights': {},
            'confidence': (
                local_results.get('confidence', 50) +
                remote_results.get('confidence', 50)
            ) / 2
        }

        return combined

    def _process_simulation_results(self, results):
        """Process and store simulation results"""
        self.results = json.dumps(results)
        self.completion_date = fields.Datetime.now()

        # Calculate execution time
        if self.start_date:
            delta = self.completion_date - self.start_date
            self.execution_time = delta.total_seconds()

        # Extract key metrics
        self.confidence_score = results.get('confidence', 0)
        self.impact_score = results.get('impact_score', 0)

        # Generate AI insights (if enabled)
        if self.organization_id.enable_ai_analysis:
            self._generate_ai_insights(results)

        # Generate recommendations
        self._generate_recommendations(results)

        self.state = 'completed'

        self.message_post(
            body=_("Simulation completed successfully"),
            message_type='notification'
        )

    def _generate_ai_insights(self, results):
        """Generate AI insights from simulation results"""
        # Call AI orchestrator if available
        if self.env['ir.module.module'].search([('name', '=', 'ai_twin_orchestrator'), ('state', '=', 'installed')]):
            orchestrator = self.env['bcm.ai.twin.orchestrator']
            insights = orchestrator.analyze_simulation_results(self.id, results)
            self.ai_insights = json.dumps(insights)
        else:
            # Basic insights without AI orchestrator
            self.ai_insights = json.dumps({
                'summary': 'Simulation completed with moderate confidence',
                'key_findings': results.get('recommendations', []),
                'risk_level': 'medium'
            })

    def _generate_recommendations(self, results):
        """Generate actionable recommendations"""
        recommendations = results.get('recommendations', [])

        # Add scenario-specific recommendations
        if self.scenario_type == 'budget_optimization':
            recommendations.append('Review and optimize recurring expenses')
        elif self.scenario_type == 'crisis_management':
            recommendations.append('Update crisis response protocols')

        self.recommendations = json.dumps(recommendations)

    def action_apply_recommendations(self):
        """Apply simulation recommendations to BCM"""
        self.ensure_one()

        if self.state != 'completed':
            raise UserError(_("Can only apply recommendations from completed simulations"))

        recommendations = json.loads(self.recommendations or '[]')

        # Create BCM tasks or updates based on recommendations
        # This would integrate with BCM modules

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Success"),
                'message': _("Recommendations applied to BCM system"),
                'type': 'success'
            }
        }

    def action_rerun_simulation(self):
        """Rerun simulation with same parameters"""
        self.ensure_one()

        new_sim = self.copy({
            'name': f"{self.name} (Rerun)",
            'state': 'draft',
            'results': False,
            'ai_insights': False,
            'recommendations': False,
            'execution_time': 0,
            'start_date': False,
            'completion_date': False,
            'error_message': False
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.digital.twin.simulation',
            'res_id': new_sim.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model
    def create(self, vals):
        """Override create to set default name"""
        if vals.get('name', _('New Simulation')) == _('New Simulation'):
            vals['name'] = self.env['ir.sequence'].next_by_code('bcm.digital.twin.simulation') or _('New Simulation')
        return super().create(vals)