# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class AIOrganMetrics(models.Model):
    _name = 'bcm.ai.organ.metrics'
    _description = 'AI Organ Performance Metrics'
    _order = 'timestamp desc'

    name = fields.Char(string='Metric Name', required=True)
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)

    # AI Organ Reference
    organ_name = fields.Selection([
        ('governance_brain', 'Governance Brain'),
        ('emergency_response', 'Emergency Response'),
        ('impact_oracle', 'Impact Oracle'),
        ('scenario_creator', 'Scenario Creator'),
        ('risk_advisor', 'Risk Advisor'),
        ('compliance_guardian', 'Compliance Guardian'),
        ('performance_analyst', 'Performance Analyst'),
        ('learning_coach', 'Learning Coach'),
        ('plan_generator', 'Plan Generator'),
        ('lifecycle_monitor', 'Lifecycle Monitor'),
    ], string='AI Organ', required=True)

    digital_twin_id = fields.Many2one('bcm.digital.twin', string='Digital Twin')
    bcm_client_id = fields.Many2one('bcm.client', string='BCM Client')

    # Performance Metrics
    response_time_ms = fields.Float(string='Response Time (ms)')
    accuracy_score = fields.Float(string='Accuracy Score %')
    confidence_level = fields.Float(string='Confidence Level %')

    # Activity Metrics
    requests_processed = fields.Integer(string='Requests Processed')
    successful_requests = fields.Integer(string='Successful Requests')
    failed_requests = fields.Integer(string='Failed Requests')
    success_rate = fields.Float(string='Success Rate %', compute='_compute_success_rate')

    # Health Status
    status = fields.Selection([
        ('active', 'Active'),
        ('idle', 'Idle'),
        ('busy', 'Busy'),
        ('error', 'Error'),
        ('maintenance', 'Maintenance')
    ], string='Status', default='active')

    health_score = fields.Float(string='Health Score', help='Overall health 0-100')

    # Resource Usage
    cpu_usage = fields.Float(string='CPU Usage %')
    memory_usage = fields.Float(string='Memory Usage %')

    # Quality Metrics
    user_satisfaction = fields.Float(string='User Satisfaction Score')
    recommendation_quality = fields.Float(string='Recommendation Quality')

    # Contextual Data
    context_data = fields.Text(string='Context Data JSON')
    error_logs = fields.Text(string='Error Logs')

    @api.depends('requests_processed', 'successful_requests')
    def _compute_success_rate(self):
        for record in self:
            if record.requests_processed > 0:
                record.success_rate = (record.successful_requests / record.requests_processed) * 100
            else:
                record.success_rate = 0.0

    @api.model
    def collect_ai_organ_metrics(self):
        """Collect metrics from all AI Organs via API"""
        try:
            dt_service_url = self.env['ir.config_parameter'].sudo().get_param(
                'digital_twin.service_url', 'http://localhost:3000'
            )

            # Get AI organs status
            response = requests.get(f"{dt_service_url}/api/ai-organs/status", timeout=30)

            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    self._process_ai_organ_data(data['data'])
                return True
            else:
                _logger.error(f"AI Organs API error: {response.status_code}")
                return False

        except Exception as e:
            _logger.error(f"Error collecting AI organ metrics: {e}")
            return False

    def _process_ai_organ_data(self, organs_data):
        """Process AI organ data from API"""
        for organ_data in organs_data:
            # Create metric record for each organ
            self.create({
                'name': f"Metrics - {organ_data.get('name', 'Unknown')}",
                'organ_name': organ_data.get('type', 'governance_brain'),
                'status': organ_data.get('status', 'active'),
                'health_score': organ_data.get('health_score', 100),
                'response_time_ms': organ_data.get('avg_response_time', 0),
                'accuracy_score': organ_data.get('accuracy', 95),
                'confidence_level': organ_data.get('confidence', 90),
                'requests_processed': organ_data.get('total_requests', 0),
                'successful_requests': organ_data.get('successful_requests', 0),
                'failed_requests': organ_data.get('failed_requests', 0),
                'cpu_usage': organ_data.get('cpu_usage', 0),
                'memory_usage': organ_data.get('memory_usage', 0),
                'user_satisfaction': organ_data.get('satisfaction_score', 85),
                'recommendation_quality': organ_data.get('quality_score', 90),
                'context_data': json.dumps(organ_data, indent=2)
            })

    def action_view_organ_details(self):
        """View detailed organ performance"""
        return {
            'name': f'{self.organ_name} Details',
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.ai.organ.metrics',
            'domain': [('organ_name', '=', self.organ_name)],
            'view_mode': 'tree,form,graph,pivot',
            'context': {'default_organ_name': self.organ_name}
        }


class AIOrganDashboard(models.Model):
    _name = 'bcm.ai.organ.dashboard'
    _description = 'AI Organ Dashboard'

    name = fields.Char(string='Dashboard Name', default='AI Organs Overview')
    date = fields.Date(string='Date', default=fields.Date.context_today)

    # Summary metrics
    total_organs = fields.Integer(string='Total AI Organs', default=10)
    active_organs = fields.Integer(string='Active Organs', compute='_compute_organ_stats')
    error_organs = fields.Integer(string='Organs in Error', compute='_compute_organ_stats')

    avg_health_score = fields.Float(string='Average Health Score', compute='_compute_organ_stats')
    avg_response_time = fields.Float(string='Average Response Time', compute='_compute_organ_stats')

    # Organ metrics lines
    organ_metrics_ids = fields.One2many('bcm.ai.organ.metrics', 'id', string='Recent Metrics')

    @api.depends('organ_metrics_ids')
    def _compute_organ_stats(self):
        for record in self:
            # Get latest metrics for each organ
            latest_metrics = {}
            for metric in record.organ_metrics_ids:
                if metric.organ_name not in latest_metrics:
                    latest_metrics[metric.organ_name] = metric
                elif metric.timestamp > latest_metrics[metric.organ_name].timestamp:
                    latest_metrics[metric.organ_name] = metric

            # Calculate stats
            record.active_organs = len([m for m in latest_metrics.values() if m.status == 'active'])
            record.error_organs = len([m for m in latest_metrics.values() if m.status == 'error'])

            if latest_metrics:
                record.avg_health_score = sum(m.health_score for m in latest_metrics.values()) / len(latest_metrics)
                record.avg_response_time = sum(m.response_time_ms for m in latest_metrics.values()) / len(latest_metrics)
            else:
                record.avg_health_score = 0
                record.avg_response_time = 0

    def action_refresh_metrics(self):
        """Refresh all AI organ metrics"""
        self.env['bcm.ai.organ.metrics'].collect_ai_organ_metrics()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Metrics Updated',
                'message': 'AI Organ metrics have been refreshed',
                'type': 'success'
            }
        }

    def action_view_real_time_dashboard(self):
        """Open real-time web dashboard"""
        return {
            'type': 'ir.actions.act_url',
            'url': 'http://localhost:3000/ai-organs-dashboard',
            'target': 'new',
        }