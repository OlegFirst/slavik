# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging

_logger = logging.getLogger(__name__)

class BCMLearningCoach(models.Model):
    """AI Learning Coach - Adaptive Training Intelligence"""
    _name = 'bcm.learning.coach'
    _description = 'AI Learning Coach - Adaptive Training Intelligence'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Learning Session', required=True)

    # Coach Configuration
    coaching_style = fields.Selection([
        ('adaptive', '🎯 Adaptive - Personalized Learning'),
        ('intensive', '🔥 Intensive - Accelerated Training'),
        ('supportive', '🤝 Supportive - Guided Learning'),
        ('challenging', '💪 Challenging - Advanced Training')
    ], string='Coaching Style', default='adaptive')

    # Learning Intelligence
    ai_learning_analysis = fields.Html('AI Learning Analysis', readonly=True)
    competency_gaps = fields.Text('AI-Identified Competency Gaps')
    learning_recommendations = fields.Html('AI Learning Recommendations')
    training_optimization = fields.Text('Training Optimization Suggestions')

    # Exercise-Based Learning
    exercise_learning_integration = fields.Boolean('Exercise Learning Integration', default=True)
    performance_tracking = fields.Boolean('Performance Tracking', default=True)
    adaptive_pathways = fields.Boolean('Adaptive Learning Pathways', default=True)

    # Coach Memory
    learning_patterns = fields.Text('Learning Patterns Recognized')
    coaching_effectiveness = fields.Text('Coaching Effectiveness Data')
    learner_preferences = fields.Text('Learner Preference Patterns')

    # Coach Metrics
    learners_coached = fields.Integer('Learners Coached', default=0)
    competency_improvements = fields.Float('Competency Improvement Rate')
    learning_acceleration = fields.Float('Learning Acceleration Factor')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def action_ai_competency_analysis(self):
        """AI-powered competency gap analysis"""
        try:
            # Collect learning data from exercises and training
            learning_data = self._collect_learning_performance_data()

            coaching_prompt = f"""
AI LEARNING COACH ANALYSIS

COMPETENCY ANALYSIS REQUEST:
Organization: {self.company_id.name}
Coaching Style: {self.coaching_style}
Learning Session: {self.name}

LEARNING PERFORMANCE DATA:
{json.dumps(learning_data, indent=2)}

LEARNING COACH INTELLIGENCE REQUIRED:

1. COMPETENCY GAP ANALYSIS:
   - Individual competency assessment
   - Role-based skill gap identification
   - Critical training needs prioritization
   - Learning pathway recommendations

2. EXERCISE-BASED LEARNING:
   - Exercise performance correlation
   - Skill development opportunities
   - Training reinforcement needs
   - Practical application gaps

3. ADAPTIVE LEARNING DESIGN:
   - Personalized learning paths
   - Learning style adaptation
   - Pace optimization recommendations
   - Engagement enhancement strategies

4. PERFORMANCE PREDICTION:
   - Learning outcome forecasting
   - Training effectiveness prediction
   - Competency development timeline
   - ROI optimization opportunities

5. COACHING RECOMMENDATIONS:
   - Individual coaching strategies
   - Group training optimizations
   - Learning reinforcement methods
   - Continuous improvement approaches

Provide ADAPTIVE LEARNING INTELLIGENCE with personalized coaching recommendations.
"""

            result = self._call_learning_coach_ai(coaching_prompt, learning_data)

            if result:
                self.write({
                    'ai_learning_analysis': result.get('analysis_html', ''),
                    'competency_gaps': json.dumps(result.get('gaps', {})),
                    'learning_recommendations': result.get('recommendations_html', ''),
                    'training_optimization': json.dumps(result.get('optimization', {})),
                    'learners_coached': self.learners_coached + len(learning_data.get('learners', []))
                })

                # Generate personalized learning plans
                self._generate_personalized_learning_plans(result)

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Learning Coach Analysis Complete'),
                        'message': 'Competency gaps analyzed and learning paths optimized',
                        'type': 'success',
                    }
                }

        except Exception as e:
            raise UserError(f'Learning coach analysis failed: {str(e)}')

    def _collect_learning_performance_data(self):
        """Collect learning performance data from exercises and training"""
        # Get exercise performance data
        exercises = self.env['bcm.exercise'].search([
            ('company_id', '=', self.company_id.id),
            ('state', '=', 'completed')
        ])

        learning_data = {
            'exercises_completed': len(exercises),
            'avg_exercise_performance': 0.85,  # Would calculate from actual data
            'learners': [],
            'competency_areas': [
                'incident_response',
                'business_continuity',
                'risk_assessment',
                'crisis_communication'
            ]
        }

        return learning_data

    def _call_learning_coach_ai(self, prompt, learning_data):
        """Call AI Orchestrator for learning analysis"""
        try:
            import requests

            response = requests.post(
                'http://ai_orchestrator:8000/nlp/query',
                json={
                    'query': prompt,
                    'context': {
                        'learning_data': learning_data,
                        'ai_organ': 'learning_coach',
                        'coaching_style': self.coaching_style
                    },
                    'user_role': 'learning_coach'
                },
                timeout=60
            )

            return response.json() if response.status_code == 200 else None

        except Exception as e:
            _logger.error(f'Learning coach AI call failed: {e}')
            return None

    def _generate_personalized_learning_plans(self, ai_analysis_result):
        """Generate personalized learning plans based on AI analysis"""
        try:
            if not ai_analysis_result:
                _logger.warning("No AI analysis result provided for learning plan generation")
                return

            # Extract competency gaps from AI analysis
            competency_gaps = ai_analysis_result.get('competency_gaps', [])
            learning_style = ai_analysis_result.get('recommended_style', self.coaching_style)

            # Generate learning path recommendations
            learning_plans = []
            for gap in competency_gaps:
                plan = {
                    'competency_area': gap.get('area'),
                    'current_level': gap.get('current_level', 0),
                    'target_level': gap.get('target_level', 5),
                    'learning_modules': gap.get('suggested_modules', []),
                    'estimated_duration': gap.get('duration_hours', 8),
                    'learning_style': learning_style,
                    'priority': gap.get('priority', 'medium')
                }
                learning_plans.append(plan)

            # Store the generated plans
            self.learning_recommendations = self._format_learning_plans(learning_plans)

            # Update coaching effectiveness metrics
            self.learners_coached += 1
            self.competency_improvements = ai_analysis_result.get('predicted_improvement', 0.0)

            _logger.info(f"Generated {len(learning_plans)} personalized learning plans")

        except Exception as e:
            _logger.error(f"Failed to generate personalized learning plans: {e}")

    def _format_learning_plans(self, plans):
        """Format learning plans as HTML for display"""
        html_content = "<h3>🎯 Personalized Learning Plans</h3>"

        for i, plan in enumerate(plans, 1):
            html_content += f"""
            <div class="learning-plan">
                <h4>{i}. {plan['competency_area']}</h4>
                <p><strong>Current Level:</strong> {plan['current_level']}/5</p>
                <p><strong>Target Level:</strong> {plan['target_level']}/5</p>
                <p><strong>Learning Style:</strong> {plan['learning_style']}</p>
                <p><strong>Estimated Duration:</strong> {plan['estimated_duration']} hours</p>
                <p><strong>Priority:</strong> {plan['priority']}</p>
                <ul>
                    {''.join(f"<li>{module}</li>" for module in plan['learning_modules'])}
                </ul>
            </div>
            """

        return html_content