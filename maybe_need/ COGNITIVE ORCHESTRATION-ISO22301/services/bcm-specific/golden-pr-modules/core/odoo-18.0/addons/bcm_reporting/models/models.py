from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class BCMAnalyticsDashboard(models.Model):
    """Advanced Analytics Dashboard for BCM Platform"""
    _name = 'bcm.analytics.dashboard'
    _description = 'BCM Analytics Dashboard'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Dashboard Name', required=True)
    description = fields.Text('Description')

    # Dashboard configuration
    dashboard_type = fields.Selection([
        ('executive', 'Executive Summary'),
        ('operational', 'Operational Analytics'),
        ('exercise', 'Exercise Performance'),
        ('scenario', 'Scenario Effectiveness'),
        ('ai_insights', 'AI Learning Insights'),
        ('compliance', 'Compliance Analytics')
    ], string='Dashboard Type', required=True)

    # Analytics data
    analytics_data = fields.Text('Analytics Data (JSON)', help='Cached analytics data')
    last_updated = fields.Datetime('Last Updated', default=fields.Datetime.now)

    # Configuration
    auto_refresh = fields.Boolean('Auto Refresh', default=True)
    refresh_interval_minutes = fields.Integer('Refresh Interval (minutes)', default=30)

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def action_refresh_analytics(self):
        """Refresh analytics data"""
        analytics_data = self._compute_analytics_data()
        self.write({
            'analytics_data': json.dumps(analytics_data, indent=2),
            'last_updated': fields.Datetime.now()
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Analytics Refreshed'),
                'message': f'Dashboard "{self.name}" updated successfully',
                'type': 'success',
            }
        }

    def _compute_analytics_data(self):
        """Compute analytics data based on dashboard type"""
        if self.dashboard_type == 'exercise':
            return self._compute_exercise_analytics()
        elif self.dashboard_type == 'scenario':
            return self._compute_scenario_analytics()
        elif self.dashboard_type == 'ai_insights':
            return self._compute_ai_insights()
        elif self.dashboard_type == 'executive':
            return self._compute_executive_summary()
        else:
            return {}

    def _compute_exercise_analytics(self):
        """Exercise performance analytics"""
        exercises = self.env['bcm.exercise'].search([
            ('company_id', '=', self.company_id.id),
            ('state', 'in', ['completed', 'scheduled'])
        ])

        analytics = {
            'total_exercises': len(exercises),
            'exercises_by_type': {},
            'avg_duration': 0,
            'completion_rate': 0,
            'participant_engagement': {},
            'template_usage': {},
            'recent_exercises': []
        }

        # Exercise type distribution
        for exercise in exercises:
            exercise_type = exercise.exercise_type
            if exercise_type not in analytics['exercises_by_type']:
                analytics['exercises_by_type'][exercise_type] = 0
            analytics['exercises_by_type'][exercise_type] += 1

        # Template usage statistics
        for exercise in exercises:
            if exercise.template_id:
                template_name = exercise.template_id.name
                if template_name not in analytics['template_usage']:
                    analytics['template_usage'][template_name] = 0
                analytics['template_usage'][template_name] += 1

        # Recent exercises (last 10)
        recent_exercises = exercises.sorted('create_date', reverse=True)[:10]
        for exercise in recent_exercises:
            analytics['recent_exercises'].append({
                'id': exercise.id,
                'name': exercise.name,
                'type': exercise.exercise_type,
                'status': exercise.state,
                'participants': len(exercise.participant_ids),
                'created_date': exercise.create_date.isoformat() if exercise.create_date else None,
                'ai_generated': exercise.ai_generated
            })

        return analytics

    def _compute_scenario_analytics(self):
        """Scenario effectiveness analytics"""
        scenarios = self.env['bcm.scenario'].search([
            ('company_id', '=', self.company_id.id),
            ('is_published', '=', True)
        ])

        analytics = {
            'total_scenarios': len(scenarios),
            'ai_generated_count': 0,
            'scenarios_by_category': {},
            'avg_rating': 0,
            'most_used_scenarios': [],
            'effectiveness_trends': {}
        }

        # AI generated scenarios
        ai_scenarios = scenarios.filtered('meta_ai_generated')
        analytics['ai_generated_count'] = len(ai_scenarios)

        # Category distribution
        for scenario in scenarios:
            category = scenario.category
            if category not in analytics['scenarios_by_category']:
                analytics['scenarios_by_category'][category] = 0
            analytics['scenarios_by_category'][category] += 1

        # Average rating
        rated_scenarios = scenarios.filtered(lambda s: s.avg_rating > 0)
        if rated_scenarios:
            analytics['avg_rating'] = sum(rated_scenarios.mapped('avg_rating')) / len(rated_scenarios)

        # Most used scenarios (by exercise count)
        for scenario in scenarios:
            exercise_count = scenario.exercise_count or 0
            if exercise_count > 0:
                analytics['most_used_scenarios'].append({
                    'id': scenario.id,
                    'title': scenario.title,
                    'category': scenario.category,
                    'exercise_count': exercise_count,
                    'avg_rating': scenario.avg_rating,
                    'ai_generated': scenario.meta_ai_generated
                })

        # Sort by usage
        analytics['most_used_scenarios'].sort(key=lambda x: x['exercise_count'], reverse=True)
        analytics['most_used_scenarios'] = analytics['most_used_scenarios'][:10]

        return analytics

    def _compute_ai_insights(self):
        """AI learning insights analytics"""
        try:
            # Query Scenario Orchestrator для learning data
            import requests

            response = requests.get(
                'http://scenario_orchestrator:8085/learning/dashboard',
                timeout=10
            )

            if response.status_code == 200:
                learning_data = response.json()
                return learning_data.get('dashboard', {})

        except Exception as e:
            _logger.error(f'Failed to get AI insights: {e}')

        return {
            'total_scenarios_with_data': 0,
            'avg_platform_effectiveness': 0,
            'message': 'AI insights not available'
        }

    def _compute_executive_summary(self):
        """Executive summary combining all analytics"""
        exercise_data = self._compute_exercise_analytics()
        scenario_data = self._compute_scenario_analytics()
        ai_data = self._compute_ai_insights()

        return {
            'platform_overview': {
                'total_scenarios': scenario_data['total_scenarios'],
                'total_exercises': exercise_data['total_exercises'],
                'ai_generated_scenarios': scenario_data['ai_generated_count'],
                'avg_scenario_rating': round(scenario_data['avg_rating'], 2),
                'platform_effectiveness': ai_data.get('avg_platform_effectiveness', 0)
            },
            'recent_activity': exercise_data['recent_exercises'][:5],
            'top_scenarios': scenario_data['most_used_scenarios'][:5],
            'ai_insights_summary': {
                'scenarios_with_learning_data': ai_data.get('total_scenarios_with_data', 0),
                'total_completed_exercises': ai_data.get('total_exercises_completed', 0)
            }
        }

class BCMScenarioEffectivenessReport(models.Model):
    """Scenario effectiveness tracking and reporting"""
    _name = 'bcm.scenario.effectiveness'
    _description = 'Scenario Effectiveness Analytics'

    scenario_id = fields.Many2one('bcm.scenario', 'Scenario', required=True)
    measurement_date = fields.Date('Measurement Date', default=fields.Date.today)

    # Effectiveness metrics
    exercise_count = fields.Integer('Times Used')
    avg_participant_rating = fields.Float('Avg Participant Rating')
    completion_rate = fields.Float('Completion Rate %')
    time_effectiveness = fields.Float('Time Effectiveness %')
    learning_score = fields.Float('Learning Score')

    # AI-generated insights
    ai_recommendations = fields.Text('AI Recommendations')
    improvement_areas = fields.Text('Improvement Areas')
    success_factors = fields.Text('Success Factors')

    # Overall effectiveness
    overall_effectiveness = fields.Float('Overall Effectiveness', compute='_compute_overall_effectiveness', store=True)

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('avg_participant_rating', 'completion_rate', 'time_effectiveness', 'learning_score')
    def _compute_overall_effectiveness(self):
        """Compute overall effectiveness score"""
        for record in self:
            if all([record.avg_participant_rating, record.completion_rate, record.time_effectiveness, record.learning_score]):
                # Weighted average: 30% rating, 25% completion, 25% time, 20% learning
                effectiveness = (
                    record.avg_participant_rating * 0.3 +
                    record.completion_rate * 0.25 +
                    record.time_effectiveness * 0.25 +
                    record.learning_score * 0.2
                )
                record.overall_effectiveness = round(effectiveness, 2)
            else:
                record.overall_effectiveness = 0

    @api.model
    def update_from_scenario_orchestrator(self, scenario_id):
        """Update effectiveness data from Scenario Orchestrator learning API"""
        try:
            import requests

            response = requests.get(
                f'http://scenario_orchestrator:8085/learning/scenario/{scenario_id}/insights',
                timeout=10
            )

            if response.status_code == 200:
                insights = response.json().get('insights', {})

                # Create or update effectiveness record
                existing = self.search([
                    ('scenario_id', '=', scenario_id),
                    ('measurement_date', '=', fields.Date.today())
                ], limit=1)

                effectiveness_data = {
                    'scenario_id': scenario_id,
                    'exercise_count': insights.get('total_uses', 0),
                    'avg_participant_rating': insights.get('avg_effectiveness', 0),
                    'completion_rate': 85.0,  # Default, will be enhanced
                    'time_effectiveness': 80.0,  # Default, will be enhanced
                    'learning_score': insights.get('avg_effectiveness', 0),
                    'ai_recommendations': '\n'.join(insights.get('ai_recommendations', [])),
                    'improvement_areas': '\n'.join(insights.get('improvement_areas', [])),
                    'success_factors': '\n'.join(insights.get('successful_elements', []))
                }

                if existing:
                    existing.write(effectiveness_data)
                    return existing
                else:
                    return self.create(effectiveness_data)

        except Exception as e:
            _logger.error(f'Failed to update effectiveness from Scenario Orchestrator: {e}')
            return False

# Legacy model for backward compatibility
class BcmReporting(models.Model):
    _name = 'bcm.reporting'
    _description = 'BCM Reporting (Legacy)'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)