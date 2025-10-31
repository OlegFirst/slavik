# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging

_logger = logging.getLogger(__name__)

class BCMPlanGenerator(models.Model):
    """AI Plan Generator - Intelligent Continuity Planning"""
    _name = 'bcm.plan.generator'
    _description = 'AI Plan Generator - Intelligent Continuity Planning'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Plan Generation Session', required=True)

    # Generator Configuration
    generation_mode = fields.Selection([
        ('comprehensive', '📋 Comprehensive - Complete Plan Suite'),
        ('targeted', '🎯 Targeted - Specific Process Plans'),
        ('adaptive', '🔄 Adaptive - Dynamic Plan Optimization'),
        ('scenario_based', '🎭 Scenario-Based - Threat-Specific Plans')
    ], string='Generation Mode', default='comprehensive')

    # AI Plan Intelligence
    ai_plan_analysis = fields.Html('AI Plan Analysis', readonly=True)
    generated_plans = fields.One2many('bcm.plan', 'generator_session_id', 'Generated Plans')
    plan_optimization = fields.Text('AI Plan Optimization (JSON)')
    effectiveness_prediction = fields.Float('Predicted Effectiveness')

    # BIA Integration
    bia_integration = fields.Boolean('BIA Integration', default=True)
    risk_integration = fields.Boolean('Risk Integration', default=True)
    scenario_integration = fields.Boolean('Scenario Integration', default=True)

    # Plan Memory
    planning_patterns = fields.Text('Planning Patterns Learned')
    successful_strategies = fields.Text('Successful Planning Strategies')
    plan_wisdom = fields.Text('Planning Wisdom Accumulated')

    # Generator Metrics
    plans_generated = fields.Integer('Plans Generated', default=0)
    avg_generation_time = fields.Float('Avg Generation Time (min)')
    plan_adoption_rate = fields.Float('Plan Adoption Rate')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def action_ai_comprehensive_planning(self):
        """AI-powered comprehensive business continuity planning"""
        try:
            # Collect organizational context for planning
            planning_context = self._collect_planning_context()

            planning_prompt = f"""
AI PLAN GENERATOR - COMPREHENSIVE PLANNING

PLANNING SESSION:
Session: {self.name}
Generation Mode: {self.generation_mode}
Organization: {self.company_id.name}

ORGANIZATIONAL CONTEXT:
{json.dumps(planning_context, indent=2)}

COMPREHENSIVE PLANNING INTELLIGENCE REQUIRED:

1. BUSINESS CONTINUITY STRATEGY:
   - Strategic continuity objectives
   - Risk-based planning priorities
   - Resource allocation strategy
   - Recovery strategy framework

2. PROCESS-SPECIFIC PLANS:
   - Critical process continuity plans
   - Dependency-aware recovery procedures
   - Resource requirement specifications
   - Timeline optimization

3. CRISIS MANAGEMENT PLANS:
   - Crisis response procedures
   - Communication protocols
   - Stakeholder management
   - Media relations strategy

4. RECOVERY STRATEGIES:
   - Technology recovery plans
   - Facility continuity procedures
   - Supply chain alternatives
   - Workforce management

5. TESTING & MAINTENANCE:
   - Plan testing schedules
   - Maintenance procedures
   - Update triggers
   - Continuous improvement

Generate COMPREHENSIVE, ACTIONABLE business continuity plans.
"""

            result = self._call_plan_generator_ai(planning_prompt, planning_context)

            if result:
                # Create generated plans
                plans_created = self._create_plans_from_ai(result)

                self.write({
                    'ai_plan_analysis': result.get('analysis_html', ''),
                    'plan_optimization': json.dumps(result.get('optimization', {})),
                    'effectiveness_prediction': result.get('effectiveness', 0.8),
                    'plans_generated': len(plans_created)
                })

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Comprehensive Planning Complete'),
                        'message': f'Generated {len(plans_created)} business continuity plans',
                        'type': 'success',
                    }
                }

        except Exception as e:
            raise UserError(f'Comprehensive planning failed: {str(e)}')

    def action_scenario_based_planning(self):
        """Generate plans based on specific scenarios"""
        try:
            # Get available scenarios for planning
            scenarios = self.env['bcm.scenario'].search([
                ('is_published', '=', True),
                ('company_id', '=', self.company_id.id)
            ])

            scenario_planning_prompt = f"""
AI PLAN GENERATOR - SCENARIO-BASED PLANNING

AVAILABLE SCENARIOS:
{self._format_scenarios_for_ai(scenarios)}

SCENARIO-BASED PLANNING INTELLIGENCE:

1. SCENARIO ANALYSIS:
   - Threat scenario assessment
   - Impact pathway analysis
   - Critical dependency identification
   - Recovery challenge evaluation

2. SCENARIO-SPECIFIC PLANS:
   - Threat-specific response procedures
   - Scenario-tailored recovery strategies
   - Context-aware resource allocation
   - Adaptive response protocols

3. CROSS-SCENARIO OPTIMIZATION:
   - Common response elements
   - Shared resource optimization
   - Flexible procedure design
   - Scalable response frameworks

4. PLAN INTEGRATION:
   - Master plan coordination
   - Scenario plan hierarchy
   - Activation decision trees
   - Plan interoperability

Generate scenario-specific business continuity plans optimized for each threat type.
"""

            result = self._call_scenario_planning_ai(scenario_planning_prompt, scenarios)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Scenario-Based Planning Complete'),
                    'message': f'Plans generated for {len(scenarios)} scenarios',
                    'type': 'success',
                }
            }

        except Exception as e:
            raise UserError(f'Scenario-based planning failed: {str(e)}')

    def _collect_planning_context(self):
        """Collect organizational context for intelligent planning"""
        context = {
            'organization_size': 'medium',  # Would assess from employee count
            'industry_sector': 'general',   # Would get from company profile
            'critical_processes': self._get_critical_processes(),
            'risk_profile': self._get_risk_profile(),
            'regulatory_requirements': self._get_regulatory_context(),
            'resource_constraints': self._assess_resource_constraints()
        }
        return context

    def _call_plan_generator_ai(self, prompt, context):
        """Call AI for intelligent plan generation"""
        try:
            import requests

            response = requests.post(
                'http://ai_orchestrator:8000/nlp/query',
                json={
                    'query': prompt,
                    'context': {
                        **context,
                        'ai_organ': 'plan_generator',
                        'generation_mode': self.generation_mode
                    },
                    'user_role': 'plan_generator'
                },
                timeout=90
            )

            return response.json() if response.status_code == 200 else None

        except Exception as e:
            _logger.error(f'Plan generator AI call failed: {e}')
            return None