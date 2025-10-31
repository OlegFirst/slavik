# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
import json
import requests
import logging

_logger = logging.getLogger(__name__)


class BCMAnalyticsDashboard(models.Model):
    _name = 'bcm.analytics.dashboard'
    _description = 'BCM Analytics Dashboard'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'last_updated desc'

    # Basic Information
    name = fields.Char('Dashboard Name', required=True, tracking=True)
    description = fields.Text('Description')
    dashboard_type = fields.Selection([
        ('executive', 'Executive Dashboard'),
        ('ai_insights', 'AI Insights Dashboard'),
        ('operational', 'Operational Dashboard'),
    ], string='Dashboard Type', required=True, default='executive')

    # Configuration
    auto_refresh = fields.Boolean('Auto Refresh', default=False)
    refresh_interval_minutes = fields.Integer('Refresh Interval (Minutes)', default=30)
    last_updated = fields.Datetime('Last Updated', default=fields.Datetime.now)

    # Executive Metrics
    total_scenarios = fields.Integer('Total Scenarios', readonly=True)
    total_exercises = fields.Integer('Total Exercises', readonly=True)
    ai_generated_scenarios = fields.Integer('AI Generated Scenarios', readonly=True)
    platform_effectiveness = fields.Float('Platform Effectiveness (%)', readonly=True)

    # AI Learning Metrics
    scenarios_with_learning_data = fields.Integer('Scenarios with Learning Data', readonly=True)
    avg_platform_effectiveness = fields.Float('Average Platform Effectiveness', readonly=True)
    total_exercises_completed = fields.Integer('Total Exercises Completed', readonly=True)

    # Chart Data (JSON fields)
    exercise_performance_chart = fields.Text('Exercise Performance Chart Data')
    scenario_effectiveness_chart = fields.Text('Scenario Effectiveness Chart Data')
    ai_recommendations_list = fields.Text('AI Recommendations Data')
    top_scenarios_list = fields.Text('Top Scenarios Data')

    # Raw Analytics Data
    analytics_data = fields.Text('Raw Analytics Data (JSON)')

    def action_refresh_analytics(self):
        """Refresh analytics data from various sources"""
        self.ensure_one()

        try:
            # Collect data from different sources
            self._collect_executive_metrics()
            self._collect_ai_learning_metrics()
            self._collect_chart_data()
            self._collect_recommendations()

            # Update timestamp
            self.last_updated = fields.Datetime.now()

            # Log activity
            self.message_post(
                body=f"Analytics dashboard '{self.name}' refreshed successfully",
                message_type='notification'
            )

        except Exception as e:
            _logger.error(f"Failed to refresh analytics dashboard {self.id}: {str(e)}")
            self.message_post(
                body=f"Failed to refresh analytics: {str(e)}",
                message_type='notification'
            )

    def _collect_executive_metrics(self):
        """Collect executive-level metrics"""
        try:
            # Get scenarios from bcm_scenario_hub
            scenarios = self.env['bcm.scenario'].search([])
            self.total_scenarios = len(scenarios)
            self.ai_generated_scenarios = len(scenarios.filtered(lambda s: s.generation_type == 'ai'))

            # Get exercises from bcm_exercise
            exercises = self.env['bcm.exercise'].search([])
            self.total_exercises = len(exercises)

            # Calculate platform effectiveness
            if exercises:
                completed_exercises = exercises.filtered(lambda e: e.state == 'completed')
                if completed_exercises:
                    total_rating = sum(completed_exercises.mapped('overall_rating'))
                    self.platform_effectiveness = (total_rating / (len(completed_exercises) * 10)) * 100
                else:
                    self.platform_effectiveness = 0
            else:
                self.platform_effectiveness = 0

        except Exception as e:
            _logger.error(f"Error collecting executive metrics: {str(e)}")

    def _collect_ai_learning_metrics(self):
        """Collect AI learning metrics from Scenario Orchestrator"""
        try:
            # Try to connect to Scenario Orchestrator
            learning_url = "http://localhost:8085/learning/dashboard"

            try:
                response = requests.get(learning_url, timeout=5)
                if response.status_code == 200:
                    learning_data = response.json()
                    dashboard_data = learning_data.get('dashboard', {})

                    self.scenarios_with_learning_data = dashboard_data.get('total_scenarios_with_data', 0)
                    self.avg_platform_effectiveness = dashboard_data.get('avg_platform_effectiveness', 0)
                    self.total_exercises_completed = dashboard_data.get('total_exercises_completed', 0)

                    # Store raw data
                    self.analytics_data = json.dumps(learning_data, indent=2)
                else:
                    _logger.warning(f"Scenario Orchestrator returned status {response.status_code}")

            except requests.exceptions.RequestException as e:
                _logger.warning(f"Could not connect to Scenario Orchestrator: {str(e)}")
                # Fallback to local data
                self._collect_fallback_learning_metrics()

        except Exception as e:
            _logger.error(f"Error collecting AI learning metrics: {str(e)}")

    def _collect_fallback_learning_metrics(self):
        """Fallback metrics when Scenario Orchestrator is not available"""
        # Use local Odoo data as fallback
        scenarios_with_exercises = self.env['bcm.scenario'].search([
            ('exercise_ids', '!=', False)
        ])
        self.scenarios_with_learning_data = len(scenarios_with_exercises)

        exercises = self.env['bcm.exercise'].search([('state', '=', 'completed')])
        self.total_exercises_completed = len(exercises)

        if exercises:
            avg_rating = sum(exercises.mapped('overall_rating')) / len(exercises)
            self.avg_platform_effectiveness = (avg_rating / 10) * 100
        else:
            self.avg_platform_effectiveness = 0

    def _collect_chart_data(self):
        """Collect and format chart data"""
        try:
            # Exercise Performance Trend
            exercises = self.env['bcm.exercise'].search([
                ('state', '=', 'completed'),
                ('completion_date', '>=', fields.Date.today() - timedelta(days=30))
            ], order='completion_date asc')

            performance_data = {
                'labels': [],
                'datasets': [{
                    'label': 'Exercise Performance',
                    'data': [],
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                }]
            }

            for exercise in exercises:
                performance_data['labels'].append(exercise.completion_date.strftime('%Y-%m-%d'))
                performance_data['datasets'][0]['data'].append(exercise.overall_rating)

            self.exercise_performance_chart = json.dumps(performance_data)

            # Scenario Effectiveness Distribution
            scenarios = self.env['bcm.scenario'].search([])
            effectiveness_data = {
                'labels': ['High (>80%)', 'Medium (60-80%)', 'Low (<60%)'],
                'datasets': [{
                    'data': [0, 0, 0],
                    'backgroundColor': ['#4CAF50', '#FF9800', '#F44336']
                }]
            }

            for scenario in scenarios:
                if hasattr(scenario, 'effectiveness_score'):
                    score = scenario.effectiveness_score
                    if score > 80:
                        effectiveness_data['datasets'][0]['data'][0] += 1
                    elif score > 60:
                        effectiveness_data['datasets'][0]['data'][1] += 1
                    else:
                        effectiveness_data['datasets'][0]['data'][2] += 1

            self.scenario_effectiveness_chart = json.dumps(effectiveness_data)

        except Exception as e:
            _logger.error(f"Error collecting chart data: {str(e)}")

    def _collect_recommendations(self):
        """Collect AI recommendations"""
        try:
            # Try to get recommendations from Scenario Orchestrator
            recommendations_url = "http://localhost:8085/learning/recommendations"

            try:
                response = requests.get(recommendations_url, timeout=5)
                if response.status_code == 200:
                    recommendations = response.json()
                    self.ai_recommendations_list = json.dumps(recommendations, indent=2)
                else:
                    self._generate_fallback_recommendations()

            except requests.exceptions.RequestException:
                self._generate_fallback_recommendations()

        except Exception as e:
            _logger.error(f"Error collecting recommendations: {str(e)}")

    def _generate_fallback_recommendations(self):
        """Generate fallback recommendations based on local data"""
        recommendations = []

        # Analyze exercise completion rates
        total_exercises = self.env['bcm.exercise'].search_count([])
        completed_exercises = self.env['bcm.exercise'].search_count([('state', '=', 'completed')])

        if total_exercises > 0:
            completion_rate = (completed_exercises / total_exercises) * 100
            if completion_rate < 70:
                recommendations.append({
                    'id': 'rec_001',
                    'type': 'Exercise Completion',
                    'priority': 'High',
                    'title': 'Improve Exercise Completion Rate',
                    'description': f'Current completion rate is {completion_rate:.1f}%. Consider reviewing exercise complexity and providing better guidance.',
                    'confidence': 85,
                    'expected_impact': 15
                })

        # Analyze scenario effectiveness
        scenarios = self.env['bcm.scenario'].search([])
        if scenarios:
            ai_scenarios = scenarios.filtered(lambda s: hasattr(s, 'generation_type') and s.generation_type == 'ai')
            if len(ai_scenarios) < len(scenarios) * 0.3:
                recommendations.append({
                    'id': 'rec_002',
                    'type': 'AI Enhancement',
                    'priority': 'Medium',
                    'title': 'Increase AI-Generated Scenarios',
                    'description': 'Consider using AI to generate more diverse scenarios for better coverage.',
                    'confidence': 75,
                    'expected_impact': 20
                })

        self.ai_recommendations_list = json.dumps(recommendations, indent=2)

    @api.model
    def create_default_dashboards(self):
        """Create default analytics dashboards"""
        dashboards = [
            {
                'name': 'Executive Overview',
                'dashboard_type': 'executive',
                'description': 'High-level metrics for executive reporting',
                'auto_refresh': True,
                'refresh_interval_minutes': 60,
            },
            {
                'name': 'AI Learning Insights',
                'dashboard_type': 'ai_insights',
                'description': 'AI-powered learning analytics and recommendations',
                'auto_refresh': True,
                'refresh_interval_minutes': 30,
            }
        ]

        for dashboard_data in dashboards:
            existing = self.search([('name', '=', dashboard_data['name'])])
            if not existing:
                dashboard = self.create(dashboard_data)
                dashboard.action_refresh_analytics()

    @api.model
    def cron_refresh_dashboards(self):
        """Cron job to refresh auto-refresh enabled dashboards"""
        dashboards = self.search([
            ('auto_refresh', '=', True),
            '|',
            ('last_updated', '=', False),
            ('last_updated', '<=', fields.Datetime.now() - timedelta(minutes=30))
        ])

        for dashboard in dashboards:
            try:
                dashboard.action_refresh_analytics()
            except Exception as e:
                _logger.error(f"Failed to auto-refresh dashboard {dashboard.id}: {str(e)}")