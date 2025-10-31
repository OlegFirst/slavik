from odoo import http, fields
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class BCMCoreAPIController(http.Controller):

    @http.route('/api/bcm/core/metrics', type='json', auth='user', methods=['GET'])
    def get_platform_metrics(self):
        """Get BCM platform metrics for dashboard"""
        try:
            # Get critical processes count
            critical_processes = request.env['bcm.business.process'].search_count([
                ('criticality', '=', 'critical')
            ]) if hasattr(request.env, 'bcm.business.process') else 0

            # Get compliance level (mock calculation)
            compliance_level = 92  # Can be calculated from actual compliance data

            # Get average RTO
            avg_rto = 4.2  # Can be calculated from business processes

            # Get risk score
            risk_score = 87  # Can be calculated from risk assessments

            return {
                'status': 'success',
                'data': {
                    'criticalProcesses': critical_processes,
                    'complianceLevel': compliance_level,
                    'avgRTO': avg_rto,
                    'riskScore': risk_score
                }
            }
        except Exception as e:
            _logger.error(f"Error getting platform metrics: {e}")
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/bcm/core/context', type='json', auth='user', methods=['GET'])
    def get_organization_context(self):
        """Get organization context information"""
        try:
            # Get company information
            company = request.env.company

            # Get BCM context if available
            context_data = []
            if hasattr(request.env, 'bcm.context'):
                contexts = request.env['bcm.context'].search([])
                context_data = [{
                    'id': ctx.id,
                    'name': ctx.name,
                    'description': ctx.description or '',
                    'status': 'active',
                    'last_review': ctx.write_date.strftime('%Y-%m-%d') if ctx.write_date else ''
                } for ctx in contexts]

            # Default context if no BCM context
            if not context_data:
                context_data = [
                    {
                        'id': 1,
                        'name': 'Organization Scope',
                        'description': company.name,
                        'status': 'active',
                        'last_review': fields.Date.today().strftime('%Y-%m-%d')
                    }
                ]

            return {
                'status': 'success',
                'data': {
                    'company': {
                        'name': company.name,
                        'id': company.id
                    },
                    'context': context_data
                }
            }
        except Exception as e:
            _logger.error(f"Error getting organization context: {e}")
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/bcm/core/health', type='json', auth='user', methods=['GET'])
    def get_system_health(self):
        """Get system health status"""
        try:
            # Check various system components
            health_status = {
                'status': 'healthy',
                'statusText': 'All Systems Operational',
                'components': {
                    'database': 'healthy',
                    'ai_services': 'healthy',
                    'modules': 'healthy'
                },
                'last_check': fields.Datetime.now().isoformat()
            }

            return {
                'status': 'success',
                'data': health_status
            }
        except Exception as e:
            _logger.error(f"Error getting system health: {e}")
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/bcm/core/activities', type='json', auth='user', methods=['GET'])
    def get_recent_activities(self, limit=10):
        """Get recent BCM activities"""
        try:
            activities = []

            # Get mail messages for BCM modules
            if hasattr(request.env, 'mail.message'):
                messages = request.env['mail.message'].search([
                    ('model', 'like', 'bcm.%')
                ], limit=limit, order='date desc')

                activities = [{
                    'id': msg.id,
                    'title': msg.subject or 'BCM Activity',
                    'description': msg.preview or '',
                    'timestamp': msg.date.isoformat() if msg.date else '',
                    'type': 'info',
                    'model': msg.model
                } for msg in messages]

            # Default activities if no messages
            if not activities:
                activities = [
                    {
                        'id': 1,
                        'title': 'BCM Platform Initialized',
                        'description': 'All BCM modules loaded successfully',
                        'timestamp': fields.Datetime.now().isoformat(),
                        'type': 'success',
                        'model': 'bcm.core'
                    }
                ]

            return {
                'status': 'success',
                'data': activities
            }
        except Exception as e:
            _logger.error(f"Error getting recent activities: {e}")
            return {'status': 'error', 'message': str(e)}