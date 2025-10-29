# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class BCMAIConnector(models.Model):
    _name = 'bcm.ai.connector'
    _description = 'BCM AI Service Connector'
    _rec_name = 'service_name'

    service_name = fields.Char('Service Name', default='BCM AI Service')
    endpoint_url = fields.Char('AI Endpoint URL',
        default='http://localhost:8000/api/ai',
        help='URL of your AI service endpoint')
    api_key = fields.Char('API Key', help='API key for authentication')
    is_active = fields.Boolean('Active', default=True)
    timeout = fields.Integer('Timeout (seconds)', default=30)

    @api.model
    def is_configured(self):
        """Check if AI service is configured"""
        connector = self.search([('is_active', '=', True)], limit=1)
        return bool(connector and connector.endpoint_url)

    @api.model
    def call_service(self, service_type, data):
        """Call AI service with data"""
        connector = self.search([('is_active', '=', True)], limit=1)
        if not connector:
            _logger.warning("No active AI connector configured")
            return {'success': False, 'error': 'No AI service configured'}

        try:
            headers = {
                'Content-Type': 'application/json',
            }
            if connector.api_key:
                headers['Authorization'] = f'Bearer {connector.api_key}'

            payload = {
                'service': service_type,
                'data': data,
                'context': {
                    'company_id': self.env.company.id,
                    'user_id': self.env.user.id,
                }
            }

            response = requests.post(
                connector.endpoint_url,
                json=payload,
                headers=headers,
                timeout=connector.timeout
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'success': False,
                    'error': f'AI service returned {response.status_code}'
                }

        except requests.exceptions.Timeout:
            _logger.error("AI service timeout")
            return {'success': False, 'error': 'Service timeout'}
        except Exception as e:
            _logger.error(f"AI service error: {str(e)}")
            return {'success': False, 'error': str(e)}

    @api.model
    def get_project_insights(self, project):
        """Get AI insights for a project"""
        data = {
            'project_name': project.name,
            'project_type': project.bcm_type,
            'criticality': project.criticality_level,
            'health_status': project.health_status,
            'tasks_count': len(project.task_ids),
            'overdue_tasks': project.tasks_overdue_count,
        }

        result = self.call_service('project_insights', data)

        if result.get('success'):
            return {
                'html_summary': result.get('insights', ''),
                'recommendations': result.get('recommendations', []),
                'risk_score': result.get('risk_score', 0),
            }

        return None

    @api.model
    def test_connection(self):
        """Test AI service connection"""
        result = self.call_service('ping', {})
        return result.get('success', False)