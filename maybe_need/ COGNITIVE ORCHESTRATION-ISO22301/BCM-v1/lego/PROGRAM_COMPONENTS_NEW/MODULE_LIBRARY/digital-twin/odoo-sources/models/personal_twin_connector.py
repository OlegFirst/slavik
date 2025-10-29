# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, AccessError
import json
import logging
import uuid
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class PersonalTwinConnector(models.Model):
    """
    Personal Digital Twin Connector for frontend integration

    This model manages the connection between users and their personal digital twins
    across multiple frontend interfaces (Web Portal v2, Admin Panel, main Odoo).

    Provides real-time updates, customizable dashboards, and multi-portal support.
    """
    _name = 'bcm.personal.twin.connector'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Personal Digital Twin Frontend Connector'
    _order = 'user_id, create_date desc'

    # Core Fields
    name = fields.Char(
        string='Connector Name',
        compute='_compute_name',
        store=True,
        help="Auto-generated name based on user and creation date"
    )

    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        index=True,
        tracking=True,
        help="User associated with this personal digital twin"
    )

    # Digital Twin Reference
    digital_twin_id = fields.Many2one(
        'bcm.digital.twin.organization',
        string='Digital Twin',
        help="Reference to the user's digital twin organization"
    )

    # Frontend Connection Management
    active_sessions = fields.Json(
        string='Active Sessions',
        default=lambda self: {},
        help="Current frontend sessions: {session_id: {portal_type, timestamp, client_info}}"
    )

    widget_configs = fields.Json(
        string='Widget Configurations',
        default=lambda self: self._get_default_widget_configs(),
        help="Dashboard widget settings: {widget_id: {position, size, settings}}"
    )

    dashboard_layouts = fields.Json(
        string='Dashboard Layouts',
        default=lambda self: self._get_default_dashboard_layouts(),
        help="User's custom dashboard layouts per portal type"
    )

    websocket_channels = fields.Json(
        string='WebSocket Channels',
        default=lambda self: {},
        help="Real-time communication channels: {channel_id: {type, filters, subscription_time}}"
    )

    notification_settings = fields.Json(
        string='Notification Settings',
        default=lambda self: self._get_default_notification_settings(),
        help="User preferences for real-time updates and notifications"
    )

    # Status and Metrics
    is_active = fields.Boolean(
        string='Is Active',
        default=True,
        tracking=True,
        help="Whether this connector is actively processing updates"
    )

    last_activity = fields.Datetime(
        string='Last Activity',
        default=fields.Datetime.now,
        help="Last time user interacted with their digital twin dashboard"
    )

    connection_count = fields.Integer(
        string='Active Connections',
        compute='_compute_connection_count',
        help="Number of currently active frontend connections"
    )

    total_sessions = fields.Integer(
        string='Total Sessions',
        default=0,
        help="Total number of sessions created for this connector"
    )

    # Performance Metrics
    update_frequency = fields.Selection([
        ('realtime', 'Real-time'),
        ('high', 'High (every 5s)'),
        ('medium', 'Medium (every 30s)'),
        ('low', 'Low (every 5min)')
    ], string='Update Frequency', default='medium', tracking=True,
       help="How frequently to send updates to frontend")

    last_update_sent = fields.Datetime(
        string='Last Update Sent',
        help="Timestamp of last update sent to frontend"
    )

    @api.depends('user_id', 'create_date')
    def _compute_name(self):
        """Compute connector name based on user and creation date"""
        for record in self:
            if record.user_id:
                date_str = record.create_date.strftime('%Y-%m-%d') if record.create_date else 'new'
                record.name = f"Personal Twin Connector - {record.user_id.name} ({date_str})"
            else:
                record.name = "Personal Twin Connector - No User"

    @api.depends('active_sessions')
    def _compute_connection_count(self):
        """Count active frontend connections"""
        for record in self:
            if record.active_sessions:
                # Count sessions that are still active (less than 1 hour old)
                current_time = datetime.now()
                active_count = 0
                for session_id, session_data in record.active_sessions.items():
                    if isinstance(session_data, dict) and 'timestamp' in session_data:
                        session_time = datetime.fromisoformat(session_data['timestamp'])
                        if (current_time - session_time).total_seconds() < 3600:  # 1 hour
                            active_count += 1
                record.connection_count = active_count
            else:
                record.connection_count = 0

    def _get_default_widget_configs(self):
        """Default widget configurations for new connectors"""
        return {
            'twin_status': {
                'position': {'x': 0, 'y': 0},
                'size': {'width': 4, 'height': 2},
                'settings': {'show_health': True, 'auto_refresh': True}
            },
            'activity_feed': {
                'position': {'x': 4, 'y': 0},
                'size': {'width': 8, 'height': 4},
                'settings': {'max_items': 10, 'show_timestamps': True}
            },
            'metrics_chart': {
                'position': {'x': 0, 'y': 2},
                'size': {'width': 6, 'height': 3},
                'settings': {'chart_type': 'line', 'time_range': '24h'}
            },
            'notifications': {
                'position': {'x': 6, 'y': 2},
                'size': {'width': 6, 'height': 3},
                'settings': {'priority_filter': 'medium', 'auto_dismiss': False}
            }
        }

    def _get_default_dashboard_layouts(self):
        """Default dashboard layouts for different portal types"""
        return {
            'web_portal_v2': {
                'layout_type': 'grid',
                'columns': 12,
                'row_height': 60,
                'theme': 'default'
            },
            'admin_panel': {
                'layout_type': 'flexible',
                'columns': 16,
                'row_height': 50,
                'theme': 'admin'
            },
            'odoo_main': {
                'layout_type': 'kanban',
                'columns': 3,
                'row_height': 200,
                'theme': 'odoo'
            }
        }

    def _get_default_notification_settings(self):
        """Default notification settings"""
        return {
            'real_time_updates': True,
            'priority_filters': ['high', 'critical'],
            'notification_types': {
                'twin_status_change': True,
                'simulation_results': True,
                'risk_alerts': True,
                'system_health': False,
                'activity_updates': True
            },
            'delivery_channels': {
                'websocket': True,
                'email': False,
                'browser_notification': True
            },
            'quiet_hours': {
                'enabled': False,
                'start_time': '22:00',
                'end_time': '08:00'
            }
        }

    @api.model
    def establish_frontend_connection(self, session_id, portal_type, client_info=None):
        """
        Establish a new frontend connection for the current user

        Args:
            session_id (str): Unique session identifier
            portal_type (str): Type of portal ('web_portal_v2', 'admin_panel', 'odoo_main')
            client_info (dict): Optional client information (browser, IP, etc.)

        Returns:
            dict: Connection information and initial dashboard data
        """
        if not self.env.user:
            raise AccessError(_("User must be authenticated to establish connection"))

        # Find or create connector for current user
        connector = self.search([('user_id', '=', self.env.user.id)], limit=1)
        if not connector:
            connector = self.create({
                'user_id': self.env.user.id,
                'digital_twin_id': self._get_user_digital_twin().id if self._get_user_digital_twin() else False
            })

        # Update active sessions
        current_sessions = connector.active_sessions or {}
        current_sessions[session_id] = {
            'portal_type': portal_type,
            'timestamp': datetime.now().isoformat(),
            'client_info': client_info or {},
            'user_agent': self.env.context.get('HTTP_USER_AGENT', 'Unknown')
        }

        connector.write({
            'active_sessions': current_sessions,
            'last_activity': fields.Datetime.now(),
            'total_sessions': connector.total_sessions + 1
        })

        _logger.info(f"Frontend connection established: User {self.env.user.name}, "
                    f"Portal {portal_type}, Session {session_id}")

        return {
            'connection_id': session_id,
            'connector_id': connector.id,
            'dashboard_data': connector.get_dashboard_data_for_user(),
            'websocket_channels': connector._get_websocket_channels_for_portal(portal_type),
            'update_frequency': connector.update_frequency
        }

    def send_real_time_update(self, data, target_widgets=None, session_filter=None):
        """
        Send real-time update to connected frontends

        Args:
            data (dict): Update data to send
            target_widgets (list): Specific widgets to update (None = all)
            session_filter (dict): Filter sessions by criteria

        Returns:
            dict: Delivery status
        """
        self.ensure_one()

        if not self.is_active:
            return {'status': 'skipped', 'reason': 'connector_inactive'}

        # Check notification settings
        if not self._should_send_update(data):
            return {'status': 'filtered', 'reason': 'notification_settings'}

        # Prepare update payload
        update_payload = {
            'timestamp': datetime.now().isoformat(),
            'connector_id': self.id,
            'user_id': self.user_id.id,
            'data': data,
            'target_widgets': target_widgets,
            'update_type': data.get('type', 'general')
        }

        # Filter active sessions
        active_sessions = self._get_filtered_sessions(session_filter)

        # Send to WebSocket channels (would be implemented with actual WebSocket library)
        delivery_results = []
        for session_id, session_data in active_sessions.items():
            try:
                # Here you would integrate with your WebSocket implementation
                # For now, we'll simulate the delivery
                delivery_results.append({
                    'session_id': session_id,
                    'portal_type': session_data.get('portal_type'),
                    'status': 'delivered',
                    'timestamp': datetime.now().isoformat()
                })
                _logger.debug(f"Update sent to session {session_id}: {data.get('type', 'unknown')}")
            except Exception as e:
                delivery_results.append({
                    'session_id': session_id,
                    'status': 'failed',
                    'error': str(e)
                })
                _logger.error(f"Failed to send update to session {session_id}: {e}")

        # Update last update timestamp
        self.write({
            'last_update_sent': fields.Datetime.now(),
            'last_activity': fields.Datetime.now()
        })

        return {
            'status': 'sent',
            'delivery_results': delivery_results,
            'sessions_count': len(active_sessions),
            'payload_size': len(str(update_payload))
        }

    def get_dashboard_data_for_user(self):
        """
        Get comprehensive dashboard data for the user

        Returns:
            dict: Dashboard data including widgets, layouts, and metrics
        """
        self.ensure_one()

        # Get digital twin data
        twin_data = {}
        if self.digital_twin_id:
            twin_data = {
                'id': self.digital_twin_id.id,
                'name': self.digital_twin_id.name,
                'status': getattr(self.digital_twin_id, 'status', 'unknown'),
                'last_sync': getattr(self.digital_twin_id, 'last_sync', None),
                'health_score': self._calculate_twin_health_score()
            }

        # Get activity data
        activity_data = self._get_recent_activity()

        # Get metrics data
        metrics_data = self._get_twin_metrics()

        # Get notifications
        notifications = self._get_user_notifications()

        return {
            'user_info': {
                'id': self.user_id.id,
                'name': self.user_id.name,
                'avatar': self._get_user_avatar_url()
            },
            'twin_data': twin_data,
            'activity_data': activity_data,
            'metrics_data': metrics_data,
            'notifications': notifications,
            'widget_configs': self.widget_configs,
            'dashboard_layouts': self.dashboard_layouts,
            'connection_info': {
                'connector_id': self.id,
                'active_connections': self.connection_count,
                'last_activity': self.last_activity.isoformat() if self.last_activity else None,
                'update_frequency': self.update_frequency
            }
        }

    def update_widget_configuration(self, widget_id, new_config):
        """
        Update configuration for a specific widget

        Args:
            widget_id (str): Widget identifier
            new_config (dict): New configuration data

        Returns:
            bool: Success status
        """
        self.ensure_one()

        try:
            current_configs = self.widget_configs or {}
            current_configs[widget_id] = new_config

            self.write({
                'widget_configs': current_configs,
                'last_activity': fields.Datetime.now()
            })

            # Broadcast change to connected sessions
            self.send_real_time_update({
                'type': 'widget_config_update',
                'widget_id': widget_id,
                'config': new_config
            }, target_widgets=[widget_id])

            _logger.info(f"Widget configuration updated: {widget_id} for user {self.user_id.name}")
            return True

        except Exception as e:
            _logger.error(f"Failed to update widget configuration: {e}")
            return False

    def broadcast_twin_changes(self, change_data):
        """
        Broadcast digital twin changes to all connected sessions

        Args:
            change_data (dict): Information about the changes
        """
        self.ensure_one()

        update_data = {
            'type': 'twin_change',
            'change_data': change_data,
            'twin_id': self.digital_twin_id.id if self.digital_twin_id else None,
            'timestamp': datetime.now().isoformat()
        }

        self.send_real_time_update(update_data)

        _logger.info(f"Twin changes broadcasted for user {self.user_id.name}: {change_data.get('type', 'unknown')}")

    # Helper Methods

    def _get_user_digital_twin(self):
        """Get the user's digital twin organization"""
        # This would implement logic to find or create a digital twin for the user
        # For now, return the first available twin or None
        return self.env['bcm.digital.twin.organization'].search([
            ('create_uid', '=', self.env.user.id)
        ], limit=1)

    def _should_send_update(self, data):
        """Check if update should be sent based on notification settings"""
        notification_settings = self.notification_settings or {}

        # Check if real-time updates are enabled
        if not notification_settings.get('real_time_updates', True):
            return False

        # Check update type filters
        update_type = data.get('type', 'general')
        notification_types = notification_settings.get('notification_types', {})

        if update_type in notification_types:
            return notification_types[update_type]

        # Check priority filters
        priority = data.get('priority', 'medium')
        priority_filters = notification_settings.get('priority_filters', ['high', 'critical'])

        return priority in priority_filters

    def _get_filtered_sessions(self, session_filter=None):
        """Get active sessions filtered by criteria"""
        active_sessions = self.active_sessions or {}

        if not session_filter:
            return active_sessions

        filtered_sessions = {}
        for session_id, session_data in active_sessions.items():
            # Check if session matches filter criteria
            if self._session_matches_filter(session_data, session_filter):
                filtered_sessions[session_id] = session_data

        return filtered_sessions

    def _session_matches_filter(self, session_data, session_filter):
        """Check if session matches filter criteria"""
        if 'portal_type' in session_filter:
            if session_data.get('portal_type') != session_filter['portal_type']:
                return False

        if 'max_age_minutes' in session_filter:
            session_time = datetime.fromisoformat(session_data.get('timestamp', ''))
            age_minutes = (datetime.now() - session_time).total_seconds() / 60
            if age_minutes > session_filter['max_age_minutes']:
                return False

        return True

    def _get_websocket_channels_for_portal(self, portal_type):
        """Get WebSocket channels configuration for specific portal"""
        base_channels = [
            f"personal_twin_{self.user_id.id}",
            f"user_notifications_{self.user_id.id}",
            f"twin_updates_{self.digital_twin_id.id}" if self.digital_twin_id else None
        ]

        # Add portal-specific channels
        if portal_type == 'admin_panel':
            base_channels.extend([
                f"admin_alerts_{self.user_id.id}",
                "system_status"
            ])
        elif portal_type == 'web_portal_v2':
            base_channels.extend([
                f"portal_activities_{self.user_id.id}",
                "general_announcements"
            ])

        return [channel for channel in base_channels if channel]

    def _calculate_twin_health_score(self):
        """Calculate health score for the digital twin"""
        if not self.digital_twin_id:
            return 0

        # Implement health score calculation logic
        # This is a simplified version
        score = 100

        # Deduct points for various issues
        if not hasattr(self.digital_twin_id, 'last_sync') or not self.digital_twin_id.last_sync:
            score -= 20

        if self.connection_count == 0:
            score -= 10

        return max(0, min(100, score))

    def _get_recent_activity(self, limit=10):
        """Get recent activity for the user's digital twin"""
        # This would implement logic to fetch recent activities
        # For now, return sample data
        return [
            {
                'id': 1,
                'type': 'simulation_completed',
                'title': 'Business continuity simulation completed',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'status': 'success'
            },
            {
                'id': 2,
                'type': 'risk_assessment',
                'title': 'New risk identified in supply chain',
                'timestamp': (datetime.now() - timedelta(hours=5)).isoformat(),
                'status': 'warning'
            }
        ]

    def _get_twin_metrics(self):
        """Get metrics data for the digital twin"""
        # This would implement logic to fetch actual metrics
        # For now, return sample data
        return {
            'performance_score': 85,
            'sync_status': 'healthy',
            'last_update': datetime.now().isoformat(),
            'active_simulations': 2,
            'pending_assessments': 1,
            'charts': {
                'activity_trend': [
                    {'date': '2024-09-15', 'value': 75},
                    {'date': '2024-09-16', 'value': 82},
                    {'date': '2024-09-17', 'value': 78},
                    {'date': '2024-09-18', 'value': 85}
                ]
            }
        }

    def _get_user_notifications(self, limit=5):
        """Get recent notifications for the user"""
        # This would implement logic to fetch actual notifications
        # For now, return sample data
        return [
            {
                'id': 1,
                'type': 'info',
                'title': 'Digital twin sync completed',
                'message': 'Your digital twin has been synchronized with the latest data.',
                'timestamp': datetime.now().isoformat(),
                'read': False
            },
            {
                'id': 2,
                'type': 'warning',
                'title': 'Simulation requires attention',
                'message': 'Business continuity simulation has identified potential risks.',
                'timestamp': (datetime.now() - timedelta(hours=3)).isoformat(),
                'read': True
            }
        ]

    def _get_user_avatar_url(self):
        """Get user avatar URL"""
        # This would implement logic to get actual avatar URL
        return f"/web/image/res.users/{self.user_id.id}/avatar_128"

    # Cleanup Methods

    @api.model
    def cleanup_inactive_sessions(self):
        """Cleanup inactive sessions (cron job)"""
        connectors = self.search([('is_active', '=', True)])

        for connector in connectors:
            if connector.active_sessions:
                current_time = datetime.now()
                active_sessions = {}

                for session_id, session_data in connector.active_sessions.items():
                    if isinstance(session_data, dict) and 'timestamp' in session_data:
                        session_time = datetime.fromisoformat(session_data['timestamp'])
                        if (current_time - session_time).total_seconds() < 3600:  # Keep sessions active for 1 hour
                            active_sessions[session_id] = session_data

                if active_sessions != connector.active_sessions:
                    connector.write({'active_sessions': active_sessions})
                    _logger.info(f"Cleaned up inactive sessions for user {connector.user_id.name}")

    @api.constrains('user_id')
    def _check_unique_user_connector(self):
        """Ensure only one active connector per user"""
        for record in self:
            if record.user_id:
                existing = self.search([
                    ('user_id', '=', record.user_id.id),
                    ('id', '!=', record.id),
                    ('is_active', '=', True)
                ])
                if existing:
                    raise ValidationError(
                        _("User %s already has an active personal twin connector. "
                          "Please deactivate the existing connector first.") % record.user_id.name
                    )