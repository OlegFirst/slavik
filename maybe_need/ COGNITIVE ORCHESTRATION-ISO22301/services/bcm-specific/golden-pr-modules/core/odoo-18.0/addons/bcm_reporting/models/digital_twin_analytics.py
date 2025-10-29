# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class DigitalTwinAnalytics(models.Model):
    _name = 'bcm.digital.twin.analytics'
    _description = 'Digital Twin Analytics and Reporting'
    _order = 'date desc'

    name = fields.Char(string='Analytics Report Name', required=True)
    date = fields.Datetime(string='Report Date', default=fields.Datetime.now)
    digital_twin_id = fields.Many2one('bcm.digital.twin', string='Digital Twin', required=True)
    bcm_client_id = fields.Many2one('bcm.client', string='BCM Client', required=True)

    # Analytics Data
    health_score = fields.Float(string='Health Score', help='Overall health score 0-100')
    risk_level = fields.Selection([
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk')
    ], string='Risk Level', default='medium')

    # Metrics
    total_simulations = fields.Integer(string='Total Simulations Run')
    successful_simulations = fields.Integer(string='Successful Simulations')
    failed_simulations = fields.Integer(string='Failed Simulations')
    success_rate = fields.Float(string='Success Rate %', compute='_compute_success_rate')

    # Performance Metrics
    avg_response_time = fields.Float(string='Avg Response Time (ms)')
    uptime_percentage = fields.Float(string='Uptime %', help='Digital Twin availability')

    # BCM Specific Metrics
    rto_compliance = fields.Float(string='RTO Compliance %', help='Recovery Time Objective compliance')
    rpo_compliance = fields.Float(string='RPO Compliance %', help='Recovery Point Objective compliance')

    # AI Organ Performance
    ai_organs_active = fields.Integer(string='Active AI Organs')
    ai_organs_total = fields.Integer(string='Total AI Organs')
    ai_effectiveness = fields.Float(string='AI Effectiveness Score')

    # Raw Data
    raw_metrics = fields.Text(string='Raw Metrics JSON')
    report_data = fields.Text(string='Full Report Data')

    @api.depends('total_simulations', 'successful_simulations')
    def _compute_success_rate(self):
        for record in self:
            if record.total_simulations > 0:
                record.success_rate = (record.successful_simulations / record.total_simulations) * 100
            else:
                record.success_rate = 0.0

    def action_generate_report(self):
        """Generate analytics report from Digital Twin API"""
        try:
            # Get Digital Twin service URL from config
            dt_service_url = self.env['ir.config_parameter'].sudo().get_param(
                'digital_twin.service_url', 'http://localhost:3000'
            )

            # Fetch analytics data
            response = requests.get(
                f"{dt_service_url}/api/digital-twins/{self.digital_twin_id.external_id}/metrics",
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                self._process_analytics_data(data)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': 'Analytics report generated successfully',
                        'type': 'success'
                    }
                }
            else:
                _logger.error(f"Digital Twin API error: {response.status_code}")

        except Exception as e:
            _logger.error(f"Error generating analytics report: {e}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': f'Failed to generate report: {str(e)}',
                    'type': 'danger'
                }
            }

    def _process_analytics_data(self, data):
        """Process analytics data from Digital Twin API"""
        if 'data' in data:
            metrics = data['data']

            # Update basic metrics
            self.health_score = metrics.get('health_score', 0)
            self.total_simulations = metrics.get('total_simulations', 0)
            self.successful_simulations = metrics.get('successful_simulations', 0)
            self.failed_simulations = metrics.get('failed_simulations', 0)
            self.avg_response_time = metrics.get('avg_response_time', 0)
            self.uptime_percentage = metrics.get('uptime_percentage', 100)

            # BCM metrics
            self.rto_compliance = metrics.get('rto_compliance', 0)
            self.rpo_compliance = metrics.get('rpo_compliance', 0)

            # AI metrics
            self.ai_organs_active = metrics.get('ai_organs_active', 0)
            self.ai_organs_total = metrics.get('ai_organs_total', 10)
            self.ai_effectiveness = metrics.get('ai_effectiveness', 0)

            # Determine risk level based on health score
            if self.health_score >= 90:
                self.risk_level = 'low'
            elif self.health_score >= 70:
                self.risk_level = 'medium'
            elif self.health_score >= 50:
                self.risk_level = 'high'
            else:
                self.risk_level = 'critical'

            # Store raw data
            self.raw_metrics = json.dumps(metrics, indent=2)
            self.report_data = json.dumps(data, indent=2)

    @api.model
    def generate_scheduled_reports(self):
        """Scheduled method to generate reports for all Digital Twins"""
        digital_twins = self.env['bcm.digital.twin'].search([('is_active', '=', True)])

        for twin in digital_twins:
            report = self.create({
                'name': f"Scheduled Report - {twin.name}",
                'digital_twin_id': twin.id,
                'bcm_client_id': twin.bcm_client_id.id,
            })
            report.action_generate_report()

        return True

    def action_view_dashboard(self):
        """Open Digital Twin dashboard"""
        return {
            'type': 'ir.actions.act_url',
            'url': f'http://localhost:3000/dashboard/{self.digital_twin_id.external_id}',
            'target': 'new',
        }


class DigitalTwinSnapshot(models.Model):
    _name = 'bcm.digital.twin.snapshot'
    _description = 'Digital Twin Snapshot Analytics'
    _order = 'snapshot_date desc'

    name = fields.Char(string='Snapshot Name', required=True)
    snapshot_date = fields.Datetime(string='Snapshot Date', default=fields.Datetime.now)
    digital_twin_id = fields.Many2one('bcm.digital.twin', string='Digital Twin', required=True)

    # Snapshot metrics
    size_mb = fields.Float(string='Size (MB)')
    creation_time = fields.Float(string='Creation Time (seconds)')
    compression_ratio = fields.Float(string='Compression Ratio')

    # Validation
    is_valid = fields.Boolean(string='Valid Snapshot', default=True)
    validation_errors = fields.Text(string='Validation Errors')

    # Comparison
    diff_from_previous = fields.Text(string='Changes from Previous')
    significant_changes = fields.Integer(string='Significant Changes Count')

    # External reference
    external_snapshot_id = fields.Char(string='External Snapshot ID')

    def action_restore_snapshot(self):
        """Restore Digital Twin from this snapshot"""
        try:
            dt_service_url = self.env['ir.config_parameter'].sudo().get_param(
                'digital_twin.service_url', 'http://localhost:3000'
            )

            response = requests.post(
                f"{dt_service_url}/api/snapshots/{self.external_snapshot_id}/restore",
                timeout=60
            )

            if response.status_code == 200:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': 'Digital Twin restored from snapshot successfully',
                        'type': 'success'
                    }
                }
            else:
                raise Exception(f"API returned status {response.status_code}")

        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': f'Failed to restore snapshot: {str(e)}',
                    'type': 'danger'
                }
            }