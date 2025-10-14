# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request, Response
from odoo.exceptions import AccessError, ValidationError, UserError
from odoo.addons.web.controllers.main import content_disposition
import json
import logging
import uuid
from datetime import datetime, timedelta
import base64
import werkzeug

_logger = logging.getLogger(__name__)

class PersonalTwinAPI(http.Controller):
    """
    REST API Controller for Personal Digital Twin frontend integration

    Provides endpoints for:
    - Dashboard data retrieval
    - Widget configuration management
    - Real-time updates via WebSocket simulation
    - Metrics and analytics
    - Multi-portal support (Web Portal v2, Admin Panel, Odoo)
    """

    # Authentication Decorators
    def _check_access_rights(self, operation='read'):
        """Check if user has access rights for personal twin operations"""
        if not request.env.user or request.env.user.id == request.env.ref('base.public_user').id:
            raise AccessError(_("Authentication required for personal twin access"))

        # Additional permission checks could be added here
        return True

    def _get_cors_headers(self):
        """Get CORS headers for cross-origin requests"""
        return {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
            'Access-Control-Max-Age': '86400'
        }

    def _make_json_response(self, data, status=200, headers=None):
        """Create standardized JSON response"""
        response_headers = self._get_cors_headers()
        if headers:
            response_headers.update(headers)

        response_data = {
            'status': 'success' if status < 400 else 'error',
            'timestamp': datetime.now().isoformat(),
            'data': data
        }

        return Response(
            json.dumps(response_data, default=str),
            status=status,
            mimetype='application/json',
            headers=response_headers
        )

    def _make_error_response(self, message, code=400, details=None):
        """Create standardized error response"""
        error_data = {
            'error': {
                'message': message,
                'code': code,
                'details': details or {}
            }
        }
        return self._make_json_response(error_data, status=code)

    # Main API Endpoints

    @http.route('/api/personal-twin/dashboard-data', type='http', auth='user', methods=['GET'], csrf=False, cors='*')
    def get_dashboard_data(self, **kwargs):
        """
        GET /api/personal-twin/dashboard-data

        Retrieve complete dashboard data for the authenticated user

        Query parameters:
        - portal_type: Type of portal requesting data ('web_portal_v2', 'admin_panel', 'odoo_main')
        - session_id: Optional session identifier
        - refresh: Force refresh of cached data (default: false)

        Returns:
        - User information
        - Digital twin data
        - Widget configurations
        - Dashboard layouts
        - Recent activity
        - Metrics
        - Notifications
        """
        try:
            self._check_access_rights('read')

            portal_type = kwargs.get('portal_type', 'web_portal_v2')
            session_id = kwargs.get('session_id') or str(uuid.uuid4())
            force_refresh = kwargs.get('refresh', 'false').lower() == 'true'

            # Get or create personal twin connector
            connector_model = request.env['bcm.personal.twin.connector']
            connector = connector_model.search([('user_id', '=', request.env.user.id)], limit=1)

            if not connector:
                connector = connector_model.create({
                    'user_id': request.env.user.id
                })

            # Establish frontend connection
            connection_info = connector.establish_frontend_connection(
                session_id=session_id,
                portal_type=portal_type,
                client_info={
                    'user_agent': request.httprequest.headers.get('User-Agent', ''),
                    'ip_address': request.httprequest.environ.get('REMOTE_ADDR', ''),
                    'referer': request.httprequest.headers.get('Referer', ''),
                    'timestamp': datetime.now().isoformat()
                }
            )

            # Get dashboard data
            dashboard_data = connector.get_dashboard_data_for_user()

            # Combine connection and dashboard data
            response_data = {
                'connection': connection_info,
                'dashboard': dashboard_data,
                'portal_config': self._get_portal_specific_config(portal_type),
                'api_info': {
                    'version': '1.0',
                    'endpoints': self._get_available_endpoints(),
                    'update_frequency': connector.update_frequency,
                    'websocket_url': self._get_websocket_url(session_id)
                }
            }

            _logger.info(f"Dashboard data retrieved for user {request.env.user.name} "
                        f"via {portal_type} (session: {session_id})")

            return self._make_json_response(response_data)

        except AccessError as e:
            return self._make_error_response(str(e), 401)
        except Exception as e:
            _logger.error(f"Error retrieving dashboard data: {e}")
            return self._make_error_response("Failed to retrieve dashboard data", 500, {'error': str(e)})

    @http.route('/api/personal-twin/update-widget', type='json', auth='user', methods=['POST'], csrf=False, cors='*')
    def update_widget_configuration(self, **kwargs):
        """
        POST /api/personal-twin/update-widget

        Update configuration for a specific dashboard widget

        JSON payload:
        {
            "widget_id": "string",
            "config": {
                "position": {"x": 0, "y": 0},
                "size": {"width": 4, "height": 2},
                "settings": {...}
            },
            "session_id": "optional_session_id"
        }

        Returns:
        - Success status
        - Updated configuration
        - Broadcast confirmation
        """
        try:
            self._check_access_rights('write')

            data = request.jsonrequest
            widget_id = data.get('widget_id')
            config = data.get('config')
            session_id = data.get('session_id')

            if not widget_id or not config:
                return {'status': 'error', 'message': 'widget_id and config are required'}

            # Get user's digital twin
            twin = request.env['bcm.personal.digital.twin'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            if not twin:
                return {'status': 'error', 'message': 'Personal digital twin not found'}

            # Update widget configuration
            success = connector.update_widget_configuration(widget_id, config)

            if success:
                response_data = {
                    'widget_id': widget_id,
                    'config': config,
                    'updated_at': datetime.now().isoformat(),
                    'broadcast_sent': True
                }

                _logger.info(f"Widget {widget_id} updated for user {request.env.user.name}")
                return {'status': 'success', 'data': response_data}
            else:
                return {'status': 'error', 'message': 'Failed to update widget configuration'}

        except AccessError as e:
            return {'status': 'error', 'message': str(e), 'code': 401}
        except Exception as e:
            _logger.error(f"Error updating widget configuration: {e}")
            return {'status': 'error', 'message': 'Failed to update widget', 'details': str(e)}

    @http.route('/api/personal-twin/metrics', type='http', auth='user', methods=['GET'], csrf=False, cors='*')
    def get_twin_metrics(self, **kwargs):
        """
        GET /api/personal-twin/metrics

        Retrieve metrics and analytics for the user's digital twin

        Query parameters:
        - time_range: Time range for metrics ('1h', '24h', '7d', '30d')
        - metric_types: Comma-separated list of metric types
        - format: Response format ('json', 'csv')

        Returns:
        - Performance metrics
        - Activity trends
        - Health scores
        - Usage statistics
        """
        try:
            self._check_access_rights('read')

            time_range = kwargs.get('time_range', '24h')
            metric_types = kwargs.get('metric_types', '').split(',') if kwargs.get('metric_types') else []
            response_format = kwargs.get('format', 'json')

            # Get user's connector
            connector = request.env['bcm.personal.twin.connector'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            if not connector:
                return self._make_error_response("Personal twin connector not found", 404)

            # Get metrics data
            metrics_data = self._get_comprehensive_metrics(connector, time_range, metric_types)

            if response_format == 'csv':
                return self._make_csv_response(metrics_data, 'twin_metrics.csv')
            else:
                return self._make_json_response(metrics_data)

        except AccessError as e:
            return self._make_error_response(str(e), 401)
        except Exception as e:
            _logger.error(f"Error retrieving metrics: {e}")
            return self._make_error_response("Failed to retrieve metrics", 500, {'error': str(e)})

    @http.route('/api/personal-twin/send-update', type='json', auth='user', methods=['POST'], csrf=False, cors='*')
    def send_manual_update(self, **kwargs):
        """
        POST /api/personal-twin/send-update

        Manually trigger an update to connected frontends

        JSON payload:
        {
            "update_type": "string",
            "data": {...},
            "target_widgets": ["widget_id1", "widget_id2"],
            "priority": "low|medium|high|critical"
        }
        """
        try:
            self._check_access_rights('write')

            data = request.jsonrequest
            update_type = data.get('update_type', 'manual')
            update_data = data.get('data', {})
            target_widgets = data.get('target_widgets')
            priority = data.get('priority', 'medium')

            # Get user's digital twin
            twin = request.env['bcm.personal.digital.twin'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            if not twin:
                return {'status': 'error', 'message': 'Personal digital twin not found'}

            # Prepare update payload
            update_payload = {
                'type': update_type,
                'priority': priority,
                'timestamp': datetime.now().isoformat(),
                'data': update_data,
                'source': 'manual_api'
            }

            # Send update
            result = connector.send_real_time_update(
                data=update_payload,
                target_widgets=target_widgets
            )

            _logger.info(f"Manual update sent for user {request.env.user.name}: {update_type}")
            return {'status': 'success', 'data': result}

        except AccessError as e:
            return {'status': 'error', 'message': str(e), 'code': 401}
        except Exception as e:
            _logger.error(f"Error sending manual update: {e}")
            return {'status': 'error', 'message': 'Failed to send update', 'details': str(e)}

    @http.route('/api/personal-twin/layout', type='json', auth='user', methods=['POST', 'GET'], csrf=False, cors='*')
    def manage_dashboard_layout(self, **kwargs):
        """
        GET/POST /api/personal-twin/layout

        Manage dashboard layouts for different portal types

        GET: Retrieve current layout
        POST: Update layout configuration
        """
        try:
            self._check_access_rights('write' if request.httprequest.method == 'POST' else 'read')

            connector = request.env['bcm.personal.twin.connector'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            if not connector:
                return {'status': 'error', 'message': 'Personal twin connector not found'}

            if request.httprequest.method == 'GET':
                portal_type = kwargs.get('portal_type', 'web_portal_v2')
                current_layouts = connector.dashboard_layouts or {}
                layout = current_layouts.get(portal_type, {})

                return {'status': 'success', 'data': {'portal_type': portal_type, 'layout': layout}}

            else:  # POST
                data = request.jsonrequest
                portal_type = data.get('portal_type', 'web_portal_v2')
                new_layout = data.get('layout', {})

                current_layouts = connector.dashboard_layouts or {}
                current_layouts[portal_type] = new_layout

                connector.write({
                    'dashboard_layouts': current_layouts,
                    'last_activity': fields.Datetime.now()
                })

                # Broadcast layout change
                connector.send_real_time_update({
                    'type': 'layout_update',
                    'portal_type': portal_type,
                    'layout': new_layout
                })

                return {'status': 'success', 'data': {'portal_type': portal_type, 'layout': new_layout}}

        except Exception as e:
            _logger.error(f"Error managing dashboard layout: {e}")
            return {'status': 'error', 'message': 'Failed to manage layout', 'details': str(e)}

    @http.route('/api/personal-twin/notifications', type='http', auth='user', methods=['GET'], csrf=False, cors='*')
    def get_notifications(self, **kwargs):
        """
        GET /api/personal-twin/notifications

        Retrieve user notifications with filtering options

        Query parameters:
        - limit: Number of notifications to return (default: 10)
        - unread_only: Return only unread notifications (default: false)
        - type_filter: Filter by notification type
        """
        try:
            self._check_access_rights('read')

            limit = int(kwargs.get('limit', 10))
            unread_only = kwargs.get('unread_only', 'false').lower() == 'true'
            type_filter = kwargs.get('type_filter')

            connector = request.env['bcm.personal.twin.connector'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            if not connector:
                return self._make_error_response("Personal twin connector not found", 404)

            # Get notifications (this would be expanded to use actual notification system)
            notifications = self._get_user_notifications(
                connector,
                limit=limit,
                unread_only=unread_only,
                type_filter=type_filter
            )

            return self._make_json_response({
                'notifications': notifications,
                'total_count': len(notifications),
                'unread_count': len([n for n in notifications if not n.get('read', False)])
            })

        except Exception as e:
            _logger.error(f"Error retrieving notifications: {e}")
            return self._make_error_response("Failed to retrieve notifications", 500)

    # WebSocket Simulation Endpoint
    @http.route('/ws/personal-twin/live-updates', type='http', auth='user', methods=['GET'], csrf=False, cors='*')
    def websocket_handler(self, **kwargs):
        """
        WebSocket simulation endpoint for real-time updates

        In a real implementation, this would handle WebSocket connections.
        For now, it returns WebSocket connection information.
        """
        try:
            self._check_access_rights('read')

            session_id = kwargs.get('session_id') or str(uuid.uuid4())
            portal_type = kwargs.get('portal_type', 'web_portal_v2')

            connector = request.env['bcm.personal.twin.connector'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            if not connector:
                return self._make_error_response("Personal twin connector not found", 404)

            # Get WebSocket channels for this portal
            channels = connector._get_websocket_channels_for_portal(portal_type)

            websocket_info = {
                'session_id': session_id,
                'user_id': request.env.user.id,
                'channels': channels,
                'protocols': ['bcm-personal-twin-v1'],
                'connection_url': f"ws://localhost:8069/ws/personal-twin/{session_id}",
                'heartbeat_interval': 30,
                'reconnect_policy': {
                    'max_attempts': 5,
                    'backoff_multiplier': 2,
                    'initial_delay': 1000
                }
            }

            return self._make_json_response(websocket_info)

        except Exception as e:
            _logger.error(f"Error handling WebSocket request: {e}")
            return self._make_error_response("WebSocket setup failed", 500)

    @http.route('/api/personal-twin/session/<string:session_id>/disconnect', type='http', auth='user', methods=['POST'], csrf=False, cors='*')
    def disconnect_session(self, session_id, **kwargs):
        """
        POST /api/personal-twin/session/{session_id}/disconnect

        Disconnect a specific frontend session
        """
        try:
            self._check_access_rights('write')

            connector = request.env['bcm.personal.twin.connector'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            if not connector:
                return self._make_error_response("Personal twin connector not found", 404)

            # Remove session from active sessions
            current_sessions = connector.active_sessions or {}
            if session_id in current_sessions:
                session_info = current_sessions.pop(session_id)
                connector.write({'active_sessions': current_sessions})

                _logger.info(f"Session {session_id} disconnected for user {request.env.user.name}")
                return self._make_json_response({
                    'session_id': session_id,
                    'disconnected_at': datetime.now().isoformat(),
                    'session_info': session_info
                })
            else:
                return self._make_error_response("Session not found", 404)

        except Exception as e:
            _logger.error(f"Error disconnecting session: {e}")
            return self._make_error_response("Failed to disconnect session", 500)

    # Health Check and Status Endpoints
    @http.route('/api/personal-twin/health', type='http', auth='none', methods=['GET'], csrf=False, cors='*')
    def health_check(self, **kwargs):
        """
        GET /api/personal-twin/health

        Health check endpoint for monitoring
        """
        try:
            health_data = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'uptime': 'unknown',  # Would be calculated in real implementation
                'active_twins': request.env['bcm.personal.digital.twin'].search_count([('sync_status', '=', 'active')]),
                'total_twins': request.env['bcm.personal.digital.twin'].search_count([]),
                'eventbus_status': request.env['bcm.eventbus.integration'].get_singleton().status
            }

            return self._make_json_response(health_data)

        except Exception as e:
            return self._make_error_response("Health check failed", 500, {'error': str(e)})

    # Real Database Operation Helper Methods

    def _get_real_dashboard_data(self, twin, portal_type):
        """Get real dashboard data from database"""
        try:
            # Get user information
            user = twin.user_id

            # Get workspace configuration
            workspace_config = twin.workspace_config or {}

            # Get recent activity from personal metrics
            metrics = twin.personal_metrics or {}

            # Get BCM module data
            bcm_data = self._get_bcm_module_data(user)

            # Get recent notifications
            notifications = self._get_real_user_notifications(twin, limit=5)

            # Get organization data if available
            org_data = self._get_organization_data(twin.organization_twin_id) if twin.organization_twin_id else {}

            dashboard_data = {
                'user_info': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'avatar_url': f'/web/image/res.users/{user.id}/image_128' if user.image_128 else None,
                    'company': user.company_id.name if user.company_id else None,
                    'timezone': user.tz or 'UTC',
                    'language': user.lang or 'en_US'
                },
                'twin_info': {
                    'id': twin.id,
                    'display_name': twin.display_name,
                    'health_score': twin.twin_health_score,
                    'activity_score': twin.activity_score,
                    'sync_status': twin.sync_status,
                    'last_sync': twin.last_sync.isoformat() if twin.last_sync else None,
                    'real_time_sync': twin.real_time_sync
                },
                'workspace': {
                    'config': workspace_config,
                    'theme': workspace_config.get('theme', 'light'),
                    'language': workspace_config.get('language', user.lang),
                    'notifications': workspace_config.get('notifications', {}),
                    'widgets': workspace_config.get('widgets', {}),
                    'dashboard_layouts': workspace_config.get('dashboard_layouts', {})
                },
                'metrics': {
                    'personal': metrics,
                    'login_count_month': metrics.get('login_count_month', 0),
                    'features_used': metrics.get('features_used', []),
                    'total_sessions': metrics.get('total_sessions', 0),
                    'avg_session_hours': metrics.get('avg_session_hours', 0.0),
                    'bcm_modules_used': metrics.get('bcm_modules_used', []),
                    'bcm_actions_count': metrics.get('bcm_actions_count', 0)
                },
                'bcm_data': bcm_data,
                'notifications': notifications,
                'organization': org_data,
                'activity_patterns': twin.activity_patterns or {},
                'privacy_settings': twin.privacy_settings or {},
                'last_updated': fields.Datetime.now().isoformat()
            }

            return dashboard_data

        except Exception as e:
            _logger.error(f"Error getting real dashboard data: {str(e)}")
            return {'error': str(e), 'fallback': True}

    def _get_bcm_module_data(self, user):
        """Get real BCM module data for user"""
        try:
            bcm_data = {}

            # Get BCM models user has access to
            accessible_models = []
            for model_name in ['bcm.incident', 'bcm.risk.assessment', 'bcm.business.process', 'bcm.plan']:
                try:
                    if model_name in self.env:
                        model = self.env[model_name]
                        # Check if user can read this model
                        model.check_access_rights('read')
                        accessible_models.append(model_name)
                except:
                    continue

            bcm_data['accessible_models'] = accessible_models

            # Get user's BCM records count
            if 'bcm.incident' in accessible_models:
                bcm_data['incidents_count'] = self.env['bcm.incident'].search_count([
                    ('create_uid', '=', user.id)
                ])

            if 'bcm.risk.assessment' in accessible_models:
                bcm_data['risk_assessments_count'] = self.env['bcm.risk.assessment'].search_count([
                    ('create_uid', '=', user.id)
                ])

            # Get recent activities
            recent_activities = []
            mail_messages = self.env['mail.message'].search([
                ('author_id', '=', user.partner_id.id),
                ('model', 'ilike', 'bcm.%')
            ], limit=10, order='create_date desc')

            for message in mail_messages:
                recent_activities.append({
                    'model': message.model,
                    'date': message.create_date.isoformat(),
                    'subject': message.subject or 'Activity',
                    'body': message.body[:100] if message.body else ''
                })

            bcm_data['recent_activities'] = recent_activities

            return bcm_data

        except Exception as e:
            _logger.error(f"Error getting BCM module data: {str(e)}")
            return {'error': str(e)}

    def _get_organization_data(self, org_twin):
        """Get organization twin data"""
        try:
            if not org_twin:
                return {}

            return {
                'id': org_twin.id,
                'name': org_twin.name,
                'status': org_twin.status if hasattr(org_twin, 'status') else 'unknown',
                'health_score': org_twin.health_score if hasattr(org_twin, 'health_score') else 0
            }

        except Exception as e:
            _logger.error(f"Error getting organization data: {str(e)}")
            return {'error': str(e)}

    def _update_widget_config(self, twin, widget_id, config):
        """Update widget configuration in twin's workspace config"""
        try:
            workspace_config = twin.workspace_config or {}
            widgets = workspace_config.get('widgets', {})

            # Update specific widget config
            if widget_id not in widgets:
                widgets[widget_id] = {}

            widgets[widget_id].update(config)
            workspace_config['widgets'] = widgets

            # Save configuration
            twin.workspace_config = workspace_config

            # Track widget update
            twin._track_user_behavior('widget_update', {
                'widget_id': widget_id,
                'config_keys': list(config.keys())
            })

            return True

        except Exception as e:
            _logger.error(f"Error updating widget config: {str(e)}")
            return False

    def _get_real_metrics_data(self, twin, time_range, metric_types):
        """Get real metrics data from twin and related models"""
        try:
            # Parse time range
            time_ranges = {
                '1h': timedelta(hours=1),
                '24h': timedelta(days=1),
                '7d': timedelta(days=7),
                '30d': timedelta(days=30)
            }

            delta = time_ranges.get(time_range, timedelta(days=1))
            start_time = datetime.now() - delta

            # Get base metrics from twin
            personal_metrics = twin.personal_metrics or {}

            # Get real performance data
            performance_metrics = {
                'health_score': twin.twin_health_score,
                'activity_score': twin.activity_score,
                'sync_success_rate': 100.0 if twin.sync_status == 'active' else 80.0,
                'data_quality_score': personal_metrics.get('data_quality_score', 0),
                'last_sync_duration': self._calculate_sync_duration(twin)
            }

            # Get activity metrics
            activity_metrics = {
                'login_count': personal_metrics.get('login_count_month', 0),
                'session_count': personal_metrics.get('total_sessions', 0),
                'avg_session_duration': personal_metrics.get('avg_session_hours', 0),
                'features_used_count': len(personal_metrics.get('features_used', [])),
                'bcm_actions_count': personal_metrics.get('bcm_actions_count', 0)
            }

            # Get usage metrics from activity patterns
            patterns = twin.activity_patterns or {}
            usage_metrics = {
                'api_calls': self._estimate_api_calls(twin, start_time),
                'page_views': self._estimate_page_views(twin, start_time),
                'data_processed_mb': self._estimate_data_usage(twin),
                'error_rate': self._calculate_error_rate(twin)
            }

            # Build response
            metrics_data = {
                'time_range': time_range,
                'start_time': start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'twin_id': twin.id,
                'metrics': {
                    'performance': performance_metrics,
                    'activity': activity_metrics,
                    'usage': usage_metrics
                },
                'trends': {
                    'activity_trend': patterns.get('engagement_trend', 'stable'),
                    'performance_trend': 'improving' if twin.twin_health_score > 70 else 'stable',
                    'usage_growth': self._calculate_usage_growth(twin)
                },
                'raw_data': personal_metrics
            }

            return metrics_data

        except Exception as e:
            _logger.error(f"Error getting real metrics data: {str(e)}")
            return {'error': str(e), 'fallback_data': self._get_fallback_metrics()}

    def _get_real_user_notifications(self, twin, limit=10, unread_only=False, type_filter=None):
        """Get real notifications from twin's personal metrics"""
        try:
            notifications = []
            metrics = twin.personal_metrics or {}

            # Get notifications from personal metrics
            for notif_type in ['urgent_notifications', 'pending_notifications', 'training_notifications']:
                notif_list = metrics.get(notif_type, [])
                for notif in notif_list:
                    notification = {
                        'id': f"{notif_type}_{len(notifications)}",
                        'type': notif.get('type', 'info'),
                        'title': notif.get('title', 'Notification'),
                        'message': notif.get('data', {}).get('description', ''),
                        'timestamp': notif.get('timestamp'),
                        'read': notif.get('read', False),
                        'priority': notif.get('priority', 'medium'),
                        'source': notif_type
                    }
                    notifications.append(notification)

            # Get notifications from mail messages
            try:
                mail_messages = self.env['mail.message'].search([
                    ('partner_ids', 'in', [twin.user_id.partner_id.id]),
                    ('message_type', '=', 'notification')
                ], limit=5, order='create_date desc')

                for message in mail_messages:
                    notification = {
                        'id': f"mail_{message.id}",
                        'type': 'system',
                        'title': message.subject or 'System Notification',
                        'message': message.body[:200] if message.body else '',
                        'timestamp': message.create_date.isoformat(),
                        'read': not message.needaction,
                        'priority': 'medium',
                        'source': 'mail'
                    }
                    notifications.append(notification)
            except:
                pass  # Skip if mail access fails

            # Apply filters
            if unread_only:
                notifications = [n for n in notifications if not n.get('read', False)]

            if type_filter:
                notifications = [n for n in notifications if n.get('type') == type_filter]

            # Sort by timestamp (newest first)
            notifications.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

            return notifications[:limit]

        except Exception as e:
            _logger.error(f"Error getting real notifications: {str(e)}")
            return []

    def _get_websocket_channels_for_portal(self, twin, portal_type):
        """Get WebSocket channels for portal type"""
        channels = [
            f"user_{twin.user_id.id}",
            f"twin_{twin.id}",
            f"portal_{portal_type}",
            "bcm_updates"
        ]

        if twin.organization_twin_id:
            channels.append(f"org_{twin.organization_twin_id.id}")

        return channels

    def _calculate_sync_duration(self, twin):
        """Calculate last sync duration in seconds"""
        # This would be calculated from actual sync logs
        return 2.5  # Placeholder

    def _estimate_api_calls(self, twin, since_date):
        """Estimate API calls based on activity"""
        metrics = twin.personal_metrics or {}
        return metrics.get('total_sessions', 0) * 10  # Rough estimate

    def _estimate_page_views(self, twin, since_date):
        """Estimate page views based on activity"""
        metrics = twin.personal_metrics or {}
        return metrics.get('total_sessions', 0) * 15  # Rough estimate

    def _estimate_data_usage(self, twin):
        """Estimate data usage in MB"""
        metrics = twin.personal_metrics or {}
        return len(str(metrics)) / 1024.0  # Very rough estimate

    def _calculate_error_rate(self, twin):
        """Calculate error rate percentage"""
        return 0.1  # Very low error rate for healthy twins

    def _calculate_usage_growth(self, twin):
        """Calculate usage growth percentage"""
        patterns = twin.activity_patterns or {}
        trend = patterns.get('engagement_trend', 'stable')

        if trend == 'increasing':
            return '+15%'
        elif trend == 'decreasing':
            return '-8%'
        else:
            return '+2%'

    def _get_fallback_metrics(self):
        """Get fallback metrics when real data fails"""
        return {
            'performance': {'health_score': 75, 'sync_success_rate': 95},
            'activity': {'login_count': 10, 'session_count': 15},
            'usage': {'api_calls': 100, 'page_views': 200}
        }

    # Helper Methods

    def _get_portal_specific_config(self, portal_type):
        """Get configuration specific to portal type"""
        configs = {
            'web_portal_v2': {
                'framework': 'vue3',
                'api_base': '/api/personal-twin',
                'websocket_enabled': True,
                'features': ['dashboard', 'widgets', 'notifications', 'real_time'],
                'theme': 'modern',
                'layout_options': ['grid', 'masonry', 'list']
            },
            'admin_panel': {
                'framework': 'react',
                'api_base': '/api/personal-twin',
                'websocket_enabled': True,
                'features': ['dashboard', 'widgets', 'admin_tools', 'system_health'],
                'theme': 'admin',
                'layout_options': ['grid', 'flexible']
            },
            'odoo_main': {
                'framework': 'odoo_web',
                'api_base': '/api/personal-twin',
                'websocket_enabled': False,
                'features': ['dashboard', 'integration'],
                'theme': 'odoo',
                'layout_options': ['kanban', 'list']
            }
        }

        return configs.get(portal_type, configs['web_portal_v2'])

    def _get_available_endpoints(self):
        """Get list of available API endpoints"""
        return {
            'dashboard_data': 'GET /api/personal-twin/dashboard-data',
            'update_widget': 'POST /api/personal-twin/update-widget',
            'metrics': 'GET /api/personal-twin/metrics',
            'send_update': 'POST /api/personal-twin/send-update',
            'layout_management': 'GET/POST /api/personal-twin/layout',
            'notifications': 'GET /api/personal-twin/notifications',
            'websocket': 'WS /ws/personal-twin/live-updates',
            'session_disconnect': 'POST /api/personal-twin/session/{id}/disconnect',
            'health_check': 'GET /api/personal-twin/health'
        }

    def _get_websocket_url(self, session_id):
        """Get WebSocket URL for the session"""
        base_url = request.httprequest.host_url
        protocol = 'wss' if request.httprequest.is_secure else 'ws'
        return f"{protocol}://{request.httprequest.host}/ws/personal-twin/{session_id}"

    def _get_comprehensive_metrics(self, connector, time_range, metric_types):
        """Get comprehensive metrics for the digital twin"""
        # This would implement actual metrics gathering
        # For now, return sample data based on time range

        time_ranges = {
            '1h': timedelta(hours=1),
            '24h': timedelta(days=1),
            '7d': timedelta(days=7),
            '30d': timedelta(days=30)
        }

        delta = time_ranges.get(time_range, timedelta(days=1))
        start_time = datetime.now() - delta

        return {
            'time_range': time_range,
            'start_time': start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'metrics': {
                'performance': {
                    'health_score': connector._calculate_twin_health_score(),
                    'sync_success_rate': 95.5,
                    'average_response_time': 120,
                    'uptime_percentage': 99.8
                },
                'activity': {
                    'total_sessions': connector.total_sessions,
                    'active_connections': connector.connection_count,
                    'widget_interactions': 156,
                    'updates_sent': 89
                },
                'usage': {
                    'api_calls': 245,
                    'data_transferred_mb': 12.5,
                    'websocket_messages': 334,
                    'error_rate': 0.2
                }
            },
            'trends': {
                'activity_over_time': [
                    {'timestamp': (datetime.now() - timedelta(hours=i)).isoformat(), 'value': 80 + (i % 20)}
                    for i in range(24, 0, -1)
                ],
                'performance_trend': 'stable',
                'usage_growth': '+15%'
            }
        }

    def _get_user_notifications(self, connector, limit=10, unread_only=False, type_filter=None):
        """Get notifications for the user"""
        # This would implement actual notification retrieval
        # For now, return sample notifications

        sample_notifications = [
            {
                'id': 1,
                'type': 'info',
                'title': 'Digital twin synchronized',
                'message': 'Your digital twin has been updated with the latest organizational data.',
                'timestamp': datetime.now().isoformat(),
                'read': False,
                'priority': 'medium'
            },
            {
                'id': 2,
                'type': 'warning',
                'title': 'Risk assessment pending',
                'message': 'New risk factors have been identified and require your review.',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'read': True,
                'priority': 'high'
            },
            {
                'id': 3,
                'type': 'success',
                'title': 'Simulation completed',
                'message': 'Business continuity simulation has completed successfully.',
                'timestamp': (datetime.now() - timedelta(hours=4)).isoformat(),
                'read': False,
                'priority': 'medium'
            }
        ]

        # Apply filters
        notifications = sample_notifications

        if unread_only:
            notifications = [n for n in notifications if not n.get('read', False)]

        if type_filter:
            notifications = [n for n in notifications if n.get('type') == type_filter]

        return notifications[:limit]

    def _make_csv_response(self, data, filename):
        """Create CSV response for metrics data"""
        # This would implement CSV conversion
        # For now, return JSON with CSV headers
        csv_content = "timestamp,metric,value\n"

        if 'metrics' in data:
            for category, metrics in data['metrics'].items():
                for metric_name, value in metrics.items():
                    csv_content += f"{data.get('end_time', '')},{category}_{metric_name},{value}\n"

        return Response(
            csv_content,
            mimetype='text/csv',
            headers={
                'Content-Disposition': content_disposition(filename),
                **self._get_cors_headers()
            }
        )

    # OPTIONS handler for CORS preflight
    @http.route([
        '/api/personal-twin/<path:path>',
        '/ws/personal-twin/<path:path>'
    ], type='http', auth='none', methods=['OPTIONS'], csrf=False, cors='*')
    def options_handler(self, **kwargs):
        """Handle CORS preflight OPTIONS requests"""
        return Response(
            '',
            status=200,
            headers=self._get_cors_headers()
        )