# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging

_logger = logging.getLogger(__name__)

class BCMScenarioCreator(models.Model):
    """AI Scenario Creator - Creative Scenario Generation Intelligence"""
    _name = 'bcm.scenario.creator'
    _description = 'AI Scenario Creator - Creative Intelligence Engine'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Scenario Creation Session', required=True)
    creation_mode = fields.Selection([
        ('creative', '🎨 Creative - Innovative Scenarios'),
        ('realistic', '📊 Realistic - Data-driven Scenarios'),
        ('adaptive', '🔄 Adaptive - Learning-based Scenarios'),
        ('collaborative', '👥 Collaborative - Community-driven')
    ], string='Creation Mode', default='creative')

    # Creative Intelligence
    ai_creativity_level = fields.Float('AI Creativity Level', default=0.8)
    scenario_complexity = fields.Integer('Scenario Complexity', default=3)
    innovation_factor = fields.Float('Innovation Factor', default=0.7)

    # Generated Scenarios
    generated_scenarios = fields.One2many('bcm.scenario', 'creator_session_id', 'Generated Scenarios')
    scenario_effectiveness = fields.Text('Scenario Effectiveness Data (JSON)')

    # Creative Memory
    creative_patterns = fields.Text('Creative Patterns Learned')
    successful_scenarios = fields.Text('Successful Scenario Templates')
    user_preferences = fields.Text('User Preference Patterns')

    # Performance Metrics
    scenarios_created = fields.Integer('Scenarios Created', default=0)
    avg_creation_time = fields.Float('Avg Creation Time (sec)')
    user_satisfaction = fields.Float('User Satisfaction Score')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def action_ai_scenario_burst(self):
        """AI Scenario Burst - Generate multiple scenarios rapidly"""
        try:
            burst_categories = ['cyber', 'epidemic', 'blackout', 'supply', 'natural']
            generated_scenarios = []

            for category in burst_categories:
                scenario_prompt = f"""
AI SCENARIO CREATOR - CREATIVE MODE

SCENARIO GENERATION REQUEST:
Category: {category}
Creativity Level: {self.ai_creativity_level}
Innovation Factor: {self.innovation_factor}
Organization: {self.company_id.name}

CREATIVE CHALLENGE:
Create an innovative {category} scenario that:
1. Challenges conventional thinking
2. Tests organizational adaptability
3. Incorporates modern threat vectors
4. Provides learning opportunities
5. Balances realism with creativity

SCENARIO REQUIREMENTS:
- Unique and engaging narrative
- Practical exercise potential
- Clear learning objectives
- Measurable success criteria
- Adaptable to organization context

Generate creative scenario with compelling storyline and practical application.
"""

                # Call Scenario Orchestrator for generation
                result = self._call_scenario_creator_ai(scenario_prompt, category)

                if result and result.get('scenario_id'):
                    generated_scenarios.append(result['scenario_id'])

            self.write({
                'scenarios_created': len(generated_scenarios),
                'scenario_effectiveness': json.dumps({
                    'burst_session': True,
                    'categories_generated': burst_categories,
                    'scenario_ids': generated_scenarios,
                    'timestamp': fields.Datetime.now().isoformat()
                })
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Scenario Burst Complete'),
                    'message': f'Generated {len(generated_scenarios)} innovative scenarios',
                    'type': 'success',
                }
            }

        except Exception as e:
            raise UserError(f'Scenario burst failed: {str(e)}')

    def action_adaptive_scenario_learning(self):
        """Adaptive learning from scenario usage patterns"""
        try:
            # Analyze scenario effectiveness from usage
            scenarios = self.env['bcm.scenario'].search([
                ('meta_ai_generated', '=', True),
                ('company_id', '=', self.company_id.id)
            ])

            learning_data = []
            for scenario in scenarios:
                effectiveness_data = {
                    'scenario_id': scenario.id,
                    'category': scenario.category,
                    'exercise_count': scenario.exercise_count,
                    'avg_rating': scenario.avg_rating,
                    'usage_patterns': self._analyze_scenario_usage(scenario)
                }
                learning_data.append(effectiveness_data)

            # AI learning prompt
            learning_prompt = f"""
AI SCENARIO CREATOR - LEARNING MODE

SCENARIO EFFECTIVENESS ANALYSIS:
{json.dumps(learning_data, indent=2)}

As the AI Scenario Creator, analyze scenario effectiveness and improve creativity:

1. PATTERN RECOGNITION:
   - Which scenario types are most effective?
   - What elements make scenarios engaging?
   - Which creativity approaches work best?

2. USER PREFERENCE ANALYSIS:
   - What scenarios do users prefer?
   - Which complexity levels are optimal?
   - What narrative styles are most effective?

3. CREATIVE EVOLUTION:
   - How can creativity be enhanced?
   - What new scenario approaches to try?
   - Which innovation factors to adjust?

4. ADAPTIVE RECOMMENDATIONS:
   - Personalization strategies
   - Organization-specific adaptations
   - Creative enhancement opportunities

Learn and evolve creative intelligence for better scenario generation.
"""

            # Process learning through AI
            learning_result = self._call_learning_ai(learning_prompt)

            self.write({
                'creative_patterns': learning_result.get('patterns', ''),
                'successful_scenarios': learning_result.get('successful_templates', ''),
                'user_preferences': learning_result.get('preferences', '')
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Creative Learning Complete'),
                    'message': 'AI Scenario Creator has evolved its creative intelligence',
                    'type': 'success',
                }
            }

        except Exception as e:
            raise UserError(f'Adaptive learning failed: {str(e)}')

    def _call_scenario_creator_ai(self, prompt, category):
        """Call Scenario Orchestrator for creative generation"""
        try:
            import requests

            response = requests.post(
                'http://scenario_orchestrator:8085/scenarios/generate',
                json={
                    'category': category,
                    'complexity': self.scenario_complexity,
                    'duration_hours': 4,
                    'participants': 10,
                    'creativity_boost': True,
                    'innovation_factor': self.innovation_factor
                },
                timeout=60
            )

            return response.json() if response.status_code == 200 else None

        except Exception as e:
            _logger.error(f'Scenario creator AI call failed: {e}')
            return None