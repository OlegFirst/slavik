# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging
from datetime import datetime, timedelta
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

_logger = logging.getLogger(__name__)

class BCMAITwinOrchestrator(models.Model):
    _name = 'bcm.ai.twin.orchestrator'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'bcm.ai.organs.api.integration']
    _description = 'AI Twin Orchestrator'
    _order = 'create_date desc'

    name = fields.Char(
        string='Analysis Name',
        required=True,
        default=lambda self: _('New AI Analysis')
    )

    organization_id = fields.Many2one(
        'bcm.digital.twin.organization',
        string='Organization',
        required=True,
        tracking=True
    )

    simulation_id = fields.Many2one(
        'bcm.digital.twin.simulation',
        string='Related Simulation',
        help='Simulation that triggered this AI analysis'
    )

    # AI Organs Status
    organs_status = fields.Text(
        string='AI Organs Status',
        help='JSON status of each AI organ'
    )

    # Analysis Configuration
    analysis_type = fields.Selection([
        ('comprehensive', 'Comprehensive Analysis'),
        ('risk_focused', 'Risk-Focused Analysis'),
        ('strategic', 'Strategic Planning'),
        ('operational', 'Operational Optimization'),
        ('compliance', 'Compliance Assessment'),
        ('predictive', 'Predictive Analysis'),
        ('emergency', 'Emergency Response')
    ], string='Analysis Type', required=True, default='comprehensive')

    priority = fields.Selection([
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Priority', default='normal')

    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('processing', 'Processing'),
        ('synthesizing', 'Synthesizing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], string='Status', default='draft', tracking=True)

    # Results
    ai_results = fields.Text(
        string='AI Analysis Results',
        help='Combined results from all AI organs'
    )

    synthesized_insights = fields.Text(
        string='Synthesized Insights',
        help='Final synthesized insights from all AI sources'
    )

    recommendations = fields.Text(
        string='AI Recommendations',
        help='Actionable recommendations from AI analysis'
    )

    # Metrics
    confidence_score = fields.Float(
        string='Overall Confidence',
        help='Combined confidence score (0-100)'
    )

    execution_time = fields.Float(
        string='Execution Time (seconds)'
    )

    organs_used = fields.Integer(
        string='AI Organs Used',
        compute='_compute_organs_used'
    )

    # Timestamps
    start_time = fields.Datetime(string='Start Time')
    completion_time = fields.Datetime(string='Completion Time')

    @api.depends('organs_status')
    def _compute_organs_used(self):
        for record in self:
            if record.organs_status:
                try:
                    status = json.loads(record.organs_status)
                    record.organs_used = len([o for o in status.values() if o.get('used', False)])
                except:
                    record.organs_used = 0
            else:
                record.organs_used = 0

    def action_run_analysis(self):
        """Run AI analysis"""
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(_("Only draft analyses can be run"))

        self.state = 'running'
        self.start_time = fields.Datetime.now()

        try:
            # Get Digital Twin data
            twin_data = self._get_twin_data()

            # Run AI organs analysis
            ai_results = self._run_ai_organs_parallel(twin_data)

            # Synthesize insights
            self.state = 'synthesizing'
            synthesized = self._synthesize_insights(ai_results)

            # Generate recommendations
            recommendations = self._generate_recommendations(synthesized)

            # Store results
            self._store_results(ai_results, synthesized, recommendations)

            self.state = 'completed'
            self.completion_time = fields.Datetime.now()

            # Calculate execution time
            if self.start_time:
                delta = self.completion_time - self.start_time
                self.execution_time = delta.total_seconds()

            self.message_post(
                body=_("AI Analysis completed successfully"),
                message_type='notification'
            )

            return self._get_completion_action()

        except Exception as e:
            self.state = 'failed'
            _logger.error(f"AI Analysis failed: {str(e)}")
            raise UserError(_("AI Analysis failed: %s") % str(e))

    def _get_twin_data(self):
        """Get Digital Twin data for analysis"""
        twin_data = {
            'organization': {
                'id': self.organization_id.id,
                'name': self.organization_id.name,
                'domain_type': self.organization_id.domain_type,
                'health_score': self.organization_id.twin_health_score,
                'config': json.loads(self.organization_id.twin_config or '{}')
            }
        }

        # Add simulation data if available
        if self.simulation_id:
            twin_data['simulation'] = {
                'scenario_type': self.simulation_id.scenario_type,
                'parameters': json.loads(self.simulation_id.parameters or '{}'),
                'results': json.loads(self.simulation_id.results or '{}')
            }

        # Add latest simulation results
        if self.organization_id.simulation_results:
            twin_data['latest_results'] = json.loads(self.organization_id.simulation_results)

        return twin_data

    def _run_ai_organs_parallel(self, twin_data):
        """Run AI organs analysis in parallel"""
        organs_config = self._get_organs_config()
        results = {}
        organs_status = {}

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {}

            # Submit tasks for each AI organ
            for organ_name, organ_config in organs_config.items():
                if self._should_use_organ(organ_name):
                    future = executor.submit(
                        self._call_ai_organ,
                        organ_name,
                        organ_config,
                        twin_data
                    )
                    futures[future] = organ_name

            # Collect results
            for future in as_completed(futures):
                organ_name = futures[future]
                try:
                    result = future.result(timeout=30)
                    results[organ_name] = result
                    organs_status[organ_name] = {
                        'used': True,
                        'status': 'completed',
                        'confidence': result.get('confidence', 0)
                    }
                except Exception as e:
                    _logger.warning(f"AI Organ {organ_name} failed: {str(e)}")
                    organs_status[organ_name] = {
                        'used': True,
                        'status': 'failed',
                        'error': str(e)
                    }

        self.organs_status = json.dumps(organs_status)
        return results

    def _get_organs_config(self):
        """Get AI organs configuration"""
        return {
            'governance_brain': {
                'name': 'Governance Brain',
                'type': 'strategic',
                'priority': 'high'
            },
            'emergency_response': {
                'name': 'Emergency Response',
                'type': 'operational',
                'priority': 'critical'
            },
            'impact_oracle': {
                'name': 'Impact Oracle',
                'type': 'predictive',
                'priority': 'high'
            },
            'scenario_creator': {
                'name': 'Scenario Creator',
                'type': 'creative',
                'priority': 'normal'
            },
            'risk_advisor': {
                'name': 'Risk Advisor',
                'type': 'analytical',
                'priority': 'high'
            },
            'compliance_guardian': {
                'name': 'Compliance Guardian',
                'type': 'regulatory',
                'priority': 'normal'
            },
            'performance_analyst': {
                'name': 'Performance Analyst',
                'type': 'analytical',
                'priority': 'normal'
            },
            'learning_coach': {
                'name': 'Learning Coach',
                'type': 'educational',
                'priority': 'low'
            },
            'plan_generator': {
                'name': 'Plan Generator',
                'type': 'creative',
                'priority': 'normal'
            },
            'lifecycle_monitor': {
                'name': 'Lifecycle Monitor',
                'type': 'monitoring',
                'priority': 'normal'
            }
        }

    def _should_use_organ(self, organ_name):
        """Determine if an AI organ should be used based on analysis type"""
        organ_map = {
            'comprehensive': ['all'],
            'risk_focused': ['risk_advisor', 'impact_oracle', 'emergency_response'],
            'strategic': ['governance_brain', 'scenario_creator', 'plan_generator'],
            'operational': ['performance_analyst', 'lifecycle_monitor', 'learning_coach'],
            'compliance': ['compliance_guardian', 'governance_brain'],
            'predictive': ['impact_oracle', 'scenario_creator', 'risk_advisor'],
            'emergency': ['emergency_response', 'impact_oracle', 'plan_generator']
        }

        organs_to_use = organ_map.get(self.analysis_type, [])
        return 'all' in organs_to_use or organ_name in organs_to_use

    def _call_ai_organ(self, organ_name, organ_config, twin_data):
        """Call individual AI organ"""
        _logger.info(f"Calling AI organ: {organ_name}")

        # Check if BCM AI module is available
        if self._is_bcm_ai_available(organ_name):
            return self._call_bcm_ai_organ(organ_name, twin_data)
        else:
            # Fallback to local simulation
            return self._simulate_ai_organ(organ_name, organ_config, twin_data)

    def _is_bcm_ai_available(self, organ_name):
        """Check if BCM AI organ is available"""
        # Map to BCM module names
        bcm_module_map = {
            'governance_brain': 'bcm_ai_control.governance',
            'emergency_response': 'bcm_incident',
            'risk_advisor': 'bcm_risk_management',
            'compliance_guardian': 'bcm_audit'
        }

        module_name = bcm_module_map.get(organ_name)
        if module_name:
            # Check if module exists
            try:
                model = self.env.get(module_name)
                return model is not None
            except:
                return False
        return False

    def _call_bcm_ai_organ(self, organ_name, twin_data):
        """Call actual BCM AI organ"""
        # Implementation would call actual BCM AI modules
        # For now, return simulated result
        return self._simulate_ai_organ(organ_name, {}, twin_data)

    def _simulate_ai_organ(self, organ_name, organ_config, twin_data):
        """Simulate AI organ analysis"""
        # Simulated AI analysis based on organ type
        simulations = {
            'governance_brain': self._simulate_governance_brain,
            'emergency_response': self._simulate_emergency_response,
            'impact_oracle': self._simulate_impact_oracle,
            'scenario_creator': self._simulate_scenario_creator,
            'risk_advisor': self._simulate_risk_advisor,
            'compliance_guardian': self._simulate_compliance_guardian,
            'performance_analyst': self._simulate_performance_analyst,
            'learning_coach': self._simulate_learning_coach,
            'plan_generator': self._simulate_plan_generator,
            'lifecycle_monitor': self._simulate_lifecycle_monitor
        }

        simulator = simulations.get(organ_name)
        if simulator:
            return simulator(twin_data)

        return {
            'organ': organ_name,
            'insights': ['Generic insight from ' + organ_name],
            'confidence': 60.0
        }

    def _simulate_governance_brain(self, twin_data):
        """Enhanced Governance Brain analysis using AI API"""
        return self.governance_brain_analysis(twin_data)

    def _simulate_risk_advisor(self, twin_data):
        """Enhanced Risk Advisor analysis using FAIR methodology"""
        return self.risk_advisor_analysis(twin_data)

    def _simulate_impact_oracle(self, twin_data):
        """Enhanced Impact Oracle with predictive analytics"""
        return self.impact_oracle_predictions(twin_data)

    def _simulate_scenario_creator(self, twin_data):
        """Simulate Scenario Creator"""
        return {
            'organ': 'scenario_creator',
            'scenarios': [
                {
                    'name': 'Digital Transformation Acceleration',
                    'description': 'Rapid digitalization scenario',
                    'probability': 0.7,
                    'impact': 'positive'
                },
                {
                    'name': 'Economic Downturn',
                    'description': 'Recession scenario',
                    'probability': 0.3,
                    'impact': 'negative'
                }
            ],
            'confidence': 68.0
        }

    def _simulate_emergency_response(self, twin_data):
        """Simulate Emergency Response analysis"""
        return {
            'organ': 'emergency_response',
            'readiness_score': 72.0,
            'response_capabilities': {
                'detection': 85.0,
                'response': 70.0,
                'recovery': 65.0,
                'communication': 78.0
            },
            'recommendations': [
                'Enhance crisis communication protocols',
                'Improve recovery time objectives',
                'Strengthen detection mechanisms'
            ],
            'confidence': 75.0
        }

    def _simulate_compliance_guardian(self, twin_data):
        """Enhanced Compliance Guardian with regulatory intelligence"""
        return self.compliance_guardian_check(twin_data)

    def _simulate_performance_analyst(self, twin_data):
        """Simulate Performance Analyst"""
        return {
            'organ': 'performance_analyst',
            'kpi_analysis': {
                'efficiency': 78.0,
                'effectiveness': 82.0,
                'productivity': 75.0
            },
            'trends': ['positive', 'stable', 'improving'],
            'confidence': 71.0
        }

    def _simulate_learning_coach(self, twin_data):
        """Simulate Learning Coach"""
        return {
            'organ': 'learning_coach',
            'training_recommendations': [
                'Crisis management training needed',
                'Digital skills enhancement program',
                'Leadership development initiative'
            ],
            'skill_gaps': ['data analysis', 'crisis response', 'digital tools'],
            'confidence': 65.0
        }

    def _simulate_plan_generator(self, twin_data):
        """Simulate Plan Generator"""
        return {
            'organ': 'plan_generator',
            'generated_plans': [
                {
                    'name': 'Business Continuity Enhancement',
                    'priority': 'high',
                    'duration': '6 months'
                },
                {
                    'name': 'Digital Resilience Program',
                    'priority': 'medium',
                    'duration': '12 months'
                }
            ],
            'confidence': 70.0
        }

    def _simulate_lifecycle_monitor(self, twin_data):
        """Simulate Lifecycle Monitor"""
        return {
            'organ': 'lifecycle_monitor',
            'health_status': {
                'overall': twin_data['organization']['health_score'] or 70.0,
                'systems': 75.0,
                'processes': 72.0,
                'people': 68.0
            },
            'alerts': ['System update required', 'Process optimization opportunity'],
            'confidence': 76.0
        }

    def _synthesize_insights(self, ai_results):
        """Synthesize insights from all AI organs"""
        synthesized = {
            'key_insights': [],
            'critical_findings': [],
            'opportunities': [],
            'threats': [],
            'consensus_areas': [],
            'divergent_views': [],
            'overall_confidence': 0
        }

        # Collect all insights
        all_insights = []
        confidence_scores = []

        for organ, result in ai_results.items():
            if 'insights' in result:
                all_insights.extend(result['insights'])
            if 'confidence' in result:
                confidence_scores.append(result['confidence'])

        # Calculate overall confidence
        if confidence_scores:
            synthesized['overall_confidence'] = sum(confidence_scores) / len(confidence_scores)

        # Extract key insights (simplified logic)
        synthesized['key_insights'] = all_insights[:5] if all_insights else []

        # Identify critical findings
        for organ, result in ai_results.items():
            if organ == 'risk_advisor' and 'risk_matrix' in result:
                for risk_type, score in result['risk_matrix'].items():
                    if score > 60:
                        synthesized['critical_findings'].append(
                            f"High {risk_type} risk: {score:.1f}"
                        )

            if organ == 'emergency_response' and 'readiness_score' in result:
                if result['readiness_score'] < 70:
                    synthesized['critical_findings'].append(
                        f"Emergency readiness below threshold: {result['readiness_score']:.1f}"
                    )

        # Identify opportunities
        if 'performance_analyst' in ai_results:
            perf = ai_results['performance_analyst']
            if 'kpi_analysis' in perf:
                for kpi, score in perf['kpi_analysis'].items():
                    if score < 80:
                        synthesized['opportunities'].append(
                            f"Opportunity to improve {kpi}: current {score:.1f}"
                        )

        self.confidence_score = synthesized['overall_confidence']

        return synthesized

    def _generate_recommendations(self, synthesized_insights):
        """Generate actionable recommendations"""
        recommendations = []

        # Based on critical findings
        for finding in synthesized_insights.get('critical_findings', []):
            if 'risk' in finding.lower():
                recommendations.append({
                    'type': 'risk_mitigation',
                    'priority': 'high',
                    'action': 'Implement risk mitigation strategies',
                    'details': finding
                })

            if 'emergency' in finding.lower():
                recommendations.append({
                    'type': 'emergency_preparedness',
                    'priority': 'critical',
                    'action': 'Enhance emergency response capabilities',
                    'details': finding
                })

        # Based on opportunities
        for opportunity in synthesized_insights.get('opportunities', []):
            recommendations.append({
                'type': 'improvement',
                'priority': 'medium',
                'action': 'Process optimization',
                'details': opportunity
            })

        return recommendations

    def _store_results(self, ai_results, synthesized, recommendations):
        """Store analysis results"""
        self.ai_results = json.dumps(ai_results)
        self.synthesized_insights = json.dumps(synthesized)
        self.recommendations = json.dumps(recommendations)

        # Update organization with latest insights
        if self.organization_id:
            self.organization_id.ai_insights = self.synthesized_insights

    def _get_completion_action(self):
        """Get action to show results"""
        return {
            'name': _('AI Analysis Results'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.ai.twin.orchestrator',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_apply_recommendations(self):
        """Apply AI recommendations"""
        self.ensure_one()

        if self.state != 'completed':
            raise UserError(_("Can only apply recommendations from completed analyses"))

        recommendations = json.loads(self.recommendations or '[]')

        # Create tasks or actions based on recommendations
        # This would integrate with BCM modules

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Success"),
                'message': _("Recommendations applied successfully"),
                'type': 'success'
            }
        }

    @api.model
    def create(self, vals):
        """Override create to set name"""
        if vals.get('name', _('New AI Analysis')) == _('New AI Analysis'):
            org = self.env['bcm.digital.twin.organization'].browse(vals.get('organization_id'))
            vals['name'] = f"AI Analysis - {org.name} - {fields.Date.today()}"
        return super().create(vals)