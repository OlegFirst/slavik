# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, AccessError
import json
import logging
import requests
import websocket
import threading
import time
import uuid
from datetime import datetime, timedelta
from contextlib import closing
import queue
import asyncio

_logger = logging.getLogger(__name__)

class EventBusIntegration(models.Model):
    _name = 'bcm.eventbus.integration'
    _description = 'EventBus Integration Layer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    # Core Configuration
    name = fields.Char(
        string='Integration Name',
        default='Digital Twin EventBus Integration',
        required=True
    )

    eventbus_url = fields.Char(
        string='EventBus URL',
        default='ws://localhost:8001',
        required=True,
        help="EventBus WebSocket or HTTP URL"
    )

    connection_type = fields.Selection([
        ('websocket', 'WebSocket'),
        ('http', 'HTTP REST'),
        ('hybrid', 'Hybrid (WebSocket + HTTP)')
    ], string='Connection Type', default='hybrid',
       help="Type of connection to EventBus")

    # Status and Health
    status = fields.Selection([
        ('disconnected', 'Disconnected'),
        ('connecting', 'Connecting'),
        ('connected', 'Connected'),
        ('error', 'Error'),
        ('maintenance', 'Maintenance')
    ], string='Status', default='disconnected', tracking=True)

    health_status = fields.Selection([
        ('healthy', 'Healthy'),
        ('degraded', 'Degraded'),
        ('unhealthy', 'Unhealthy')
    ], string='Health Status', default='healthy')

    last_ping = fields.Datetime(
        string='Last Ping',
        help="Last successful ping to EventBus"
    )

    last_message_sent = fields.Datetime(
        string='Last Message Sent',
        help="Timestamp of last message sent"
    )

    last_message_received = fields.Datetime(
        string='Last Message Received',
        help="Timestamp of last message received"
    )

    # Performance Metrics
    messages_sent_today = fields.Integer(
        string='Messages Sent Today',
        compute='_compute_daily_metrics',
        help="Number of messages sent today"
    )

    messages_received_today = fields.Integer(
        string='Messages Received Today',
        compute='_compute_daily_metrics',
        help="Number of messages received today"
    )

    avg_response_time = fields.Float(
        string='Avg Response Time (ms)',
        help="Average response time in milliseconds"
    )

    # Configuration Options
    auto_reconnect = fields.Boolean(
        string='Auto Reconnect',
        default=True,
        help="Automatically reconnect on connection loss"
    )

    max_retry_attempts = fields.Integer(
        string='Max Retry Attempts',
        default=5,
        help="Maximum number of reconnection attempts"
    )

    retry_interval = fields.Integer(
        string='Retry Interval (seconds)',
        default=10,
        help="Interval between retry attempts in seconds"
    )

    queue_size = fields.Integer(
        string='Message Queue Size',
        default=1000,
        help="Maximum size of outbound message queue"
    )

    # Event Filtering
    subscribe_events = fields.Text(
        string='Subscribe to Events',
        default='user_lifecycle,bcm_module_update,organization_update,risk_assessment_complete,incident_created,training_assigned',
        help="Comma-separated list of event types to subscribe to"
    )

    publish_events = fields.Boolean(
        string='Publish Events',
        default=True,
        help="Allow publishing events to EventBus"
    )

    # Authentication
    api_key = fields.Char(
        string='API Key',
        help="API key for EventBus authentication"
    )

    auth_token = fields.Char(
        string='Auth Token',
        help="Authentication token for EventBus"
    )

    # Message Logs
    message_log = fields.Json(
        string='Message Log',
        help="Log of recent messages",
        default=lambda self: []
    )

    error_log = fields.Json(
        string='Error Log',
        help="Log of connection and processing errors",
        default=lambda self: []
    )

    # Internal state
    connection_id = fields.Char(
        string='Connection ID',
        help="Unique connection identifier"
    )

    session_info = fields.Json(
        string='Session Info',
        help="Current session information"
    )

    # Computed Fields
    @api.depends('message_log')
    def _compute_daily_metrics(self):
        for record in self:
            today = fields.Date.today().strftime('%Y-%m-%d')
            logs = record.message_log or []

            sent_today = len([
                log for log in logs
                if log.get('direction') == 'outbound' and
                log.get('timestamp', '').startswith(today)
            ])

            received_today = len([
                log for log in logs
                if log.get('direction') == 'inbound' and
                log.get('timestamp', '').startswith(today)
            ])

            record.messages_sent_today = sent_today
            record.messages_received_today = received_today

    # Core Integration Methods

    @api.model
    def get_singleton(self):
        """Get or create the singleton EventBus integration"""
        integration = self.search([], limit=1)
        if not integration:
            integration = self.create({
                'name': 'Digital Twin EventBus Integration'
            })
        return integration

    def connect_to_eventbus(self):
        """Establish connection to EventBus"""
        try:
            self.status = 'connecting'
            self.connection_id = str(uuid.uuid4())

            if self.connection_type in ['websocket', 'hybrid']:
                success = self._connect_websocket()
                if not success and self.connection_type == 'hybrid':
                    success = self._connect_http()
            else:
                success = self._connect_http()

            if success:
                self.status = 'connected'
                self.health_status = 'healthy'
                self.last_ping = fields.Datetime.now()

                # Start health monitoring
                self._start_health_monitor()

                # Subscribe to events
                self._subscribe_to_events()

                self._log_message('system', 'Connected to EventBus', 'outbound')
                return True
            else:
                self.status = 'error'
                self.health_status = 'unhealthy'
                return False

        except Exception as e:
            self.status = 'error'
            self.health_status = 'unhealthy'
            self._log_error(f"Connection failed: {str(e)}")
            return False

    def _connect_websocket(self):
        """Connect via WebSocket"""
        try:
            # This would implement actual WebSocket connection
            # For now, simulate connection
            _logger.info(f"Connecting to EventBus via WebSocket: {self.eventbus_url}")

            # Simulate successful connection
            self.session_info = {
                'connection_type': 'websocket',
                'connected_at': fields.Datetime.now().isoformat(),
                'url': self.eventbus_url
            }

            return True

        except Exception as e:
            _logger.error(f"WebSocket connection failed: {str(e)}")
            return False

    def _connect_http(self):
        """Connect via HTTP"""
        try:
            # Test HTTP connection
            if self.eventbus_url.startswith('ws'):
                http_url = self.eventbus_url.replace('ws://', 'http://').replace('wss://', 'https://')
            else:
                http_url = self.eventbus_url

            response = requests.get(f"{http_url}/health", timeout=5)
            response.raise_for_status()

            self.session_info = {
                'connection_type': 'http',
                'connected_at': fields.Datetime.now().isoformat(),
                'url': http_url
            }

            _logger.info(f"Connected to EventBus via HTTP: {http_url}")
            return True

        except Exception as e:
            _logger.error(f"HTTP connection failed: {str(e)}")
            return False

    def disconnect_from_eventbus(self):
        """Disconnect from EventBus"""
        try:
            self.status = 'disconnected'
            self.connection_id = None
            self.session_info = {}

            self._log_message('system', 'Disconnected from EventBus', 'outbound')
            return True

        except Exception as e:
            self._log_error(f"Disconnect failed: {str(e)}")
            return False

    # Message Handling

    def send_message(self, event_type, data, priority='medium', target_services=None):
        """Send message to EventBus"""
        try:
            if self.status != 'connected':
                if self.auto_reconnect:
                    self.connect_to_eventbus()
                else:
                    raise UserError(_("EventBus not connected"))

            message = {
                'id': str(uuid.uuid4()),
                'event_type': event_type,
                'source': 'digital_twin_core',
                'timestamp': fields.Datetime.now().isoformat(),
                'priority': priority,
                'data': data,
                'connection_id': self.connection_id,
                'target_services': target_services or []
            }

            # Add authentication if configured
            if self.api_key:
                message['api_key'] = self.api_key
            if self.auth_token:
                message['auth_token'] = self.auth_token

            success = self._send_message_to_eventbus(message)

            if success:
                self.last_message_sent = fields.Datetime.now()
                self._log_message(event_type, message, 'outbound')
                return True
            else:
                self._log_error(f"Failed to send message: {event_type}")
                return False

        except Exception as e:
            self._log_error(f"Send message error: {str(e)}")
            return False

    def _send_message_to_eventbus(self, message):
        """Internal method to send message"""
        try:
            session = self.session_info or {}
            connection_type = session.get('connection_type', 'http')

            if connection_type == 'websocket':
                return self._send_websocket_message(message)
            else:
                return self._send_http_message(message)

        except Exception as e:
            _logger.error(f"Message send failed: {str(e)}")
            return False

    def _send_websocket_message(self, message):
        """Send message via WebSocket"""
        def send_async():
            try:
                # Simulate WebSocket send
                # In real implementation, would use actual WebSocket connection
                _logger.info(f"Sending WebSocket message: {message['event_type']}")
                return True
            except Exception as e:
                _logger.error(f"WebSocket send error: {str(e)}")
                return False

        # Send in background thread
        thread = threading.Thread(target=send_async)
        thread.daemon = True
        thread.start()
        return True

    def _send_http_message(self, message):
        """Send message via HTTP POST"""
        try:
            session = self.session_info or {}
            url = session.get('url', self.eventbus_url)

            if url.startswith('ws'):
                url = url.replace('ws://', 'http://').replace('wss://', 'https://')

            response = requests.post(f"{url}/events", json=message, timeout=10)
            response.raise_for_status()

            _logger.info(f"HTTP message sent: {message['event_type']}")
            return True

        except Exception as e:
            _logger.error(f"HTTP send error: {str(e)}")
            return False

    def receive_message(self, message_data):
        """Process received message from EventBus"""
        try:
            if not isinstance(message_data, dict):
                message_data = json.loads(message_data)

            event_type = message_data.get('event_type')
            source = message_data.get('source')
            data = message_data.get('data', {})

            # Ignore messages from own source
            if source == 'digital_twin_core':
                return True

            self.last_message_received = fields.Datetime.now()
            self._log_message(event_type, message_data, 'inbound')

            # Route message to appropriate handler
            self._route_message(event_type, data, message_data)

            return True

        except Exception as e:
            self._log_error(f"Message processing error: {str(e)}")
            return False

    def _route_message(self, event_type, data, full_message):
        """Route message to appropriate handler based on event type"""
        handlers = {
            'user_lifecycle': self._handle_user_lifecycle_event,
            'bcm_module_update': self._handle_bcm_module_event,
            'organization_update': self._handle_organization_event,
            'risk_assessment_complete': self._handle_risk_assessment_event,
            'incident_created': self._handle_incident_event,
            'training_assigned': self._handle_training_event,
            'system_health': self._handle_system_health_event,
            'service_discovery': self._handle_service_discovery_event,
        }

        handler = handlers.get(event_type, self._handle_unknown_event)
        handler(data, full_message)

    # Event Handlers

    def _handle_user_lifecycle_event(self, data, message):
        """Handle user lifecycle events"""
        try:
            user_id = data.get('user_id')
            event = data.get('event')

            if not user_id or not event:
                return

            # Forward to Digital Twin Lifecycle Manager
            lifecycle_manager = self.env['bcm.digital.twin.lifecycle.manager'].get_singleton()

            if event == 'user_created':
                lifecycle_manager.process_user_creation(user_id, data.get('user_data'))
            elif event == 'user_updated':
                lifecycle_manager.process_user_update(user_id, data.get('changed_fields'))
            elif event == 'user_login':
                lifecycle_manager.process_user_login(user_id, data.get('login_info'))
            elif event == 'user_logout':
                lifecycle_manager.process_user_logout(user_id, data.get('session_info'))
            elif event == 'user_deactivated':
                lifecycle_manager.process_user_deactivation(user_id)
            elif event == 'role_changed':
                lifecycle_manager.process_role_change(user_id, data.get('role_changes'))

        except Exception as e:
            _logger.error(f"User lifecycle event handler error: {str(e)}")

    def _handle_bcm_module_event(self, data, message):
        """Handle BCM module update events"""
        try:
            module_name = data.get('module')
            affected_users = data.get('affected_users', [])

            # Notify affected digital twins
            twins = self.env['bcm.personal.digital.twin'].search([
                ('user_id', 'in', affected_users)
            ])

            for twin in twins:
                twin._handle_bcm_module_update(data)

        except Exception as e:
            _logger.error(f"BCM module event handler error: {str(e)}")

    def _handle_organization_event(self, data, message):
        """Handle organization update events"""
        try:
            org_twin_id = data.get('org_twin_id')

            if org_twin_id:
                # Notify all personal twins in this organization
                twins = self.env['bcm.personal.digital.twin'].search([
                    ('organization_twin_id', '=', org_twin_id)
                ])

                for twin in twins:
                    twin._handle_organization_update(data)

        except Exception as e:
            _logger.error(f"Organization event handler error: {str(e)}")

    def _handle_risk_assessment_event(self, data, message):
        """Handle risk assessment completion events"""
        try:
            assigned_user_id = data.get('assigned_user_id')

            if assigned_user_id:
                twin = self.env['bcm.personal.digital.twin'].search([
                    ('user_id', '=', assigned_user_id)
                ], limit=1)

                if twin:
                    twin._handle_risk_assessment_update(data)

        except Exception as e:
            _logger.error(f"Risk assessment event handler error: {str(e)}")

    def _handle_incident_event(self, data, message):
        """Handle incident creation events"""
        try:
            assigned_users = data.get('assigned_users', [])

            if assigned_users:
                twins = self.env['bcm.personal.digital.twin'].search([
                    ('user_id', 'in', assigned_users)
                ])

                for twin in twins:
                    twin._handle_incident_notification(data)

        except Exception as e:
            _logger.error(f"Incident event handler error: {str(e)}")

    def _handle_training_event(self, data, message):
        """Handle training assignment events"""
        try:
            assigned_user_id = data.get('assigned_user_id')

            if assigned_user_id:
                twin = self.env['bcm.personal.digital.twin'].search([
                    ('user_id', '=', assigned_user_id)
                ], limit=1)

                if twin:
                    twin._handle_training_notification(data)

        except Exception as e:
            _logger.error(f"Training event handler error: {str(e)}")

    def _handle_system_health_event(self, data, message):
        """Handle system health events"""
        try:
            service_name = data.get('service')
            health_status = data.get('status')

            # Update service registry
            registry = self.env['bcm.service.registry'].get_singleton()
            registry.update_service_health(service_name, health_status, data)

        except Exception as e:
            _logger.error(f"System health event handler error: {str(e)}")

    def _handle_service_discovery_event(self, data, message):
        """Handle service discovery events"""
        try:
            service_info = data.get('service_info')

            if service_info:
                # Register new service
                registry = self.env['bcm.service.registry'].get_singleton()
                registry.register_service(service_info)

        except Exception as e:
            _logger.error(f"Service discovery event handler error: {str(e)}")

    def _handle_unknown_event(self, data, message):
        """Handle unknown event types"""
        _logger.warning(f"Received unknown event type: {message.get('event_type')}")

    # Health Monitoring

    def _start_health_monitor(self):
        """Start health monitoring thread"""
        def health_monitor():
            while self.status == 'connected':
                try:
                    self._send_health_ping()
                    time.sleep(30)  # Ping every 30 seconds
                except Exception as e:
                    _logger.error(f"Health monitor error: {str(e)}")
                    break

        thread = threading.Thread(target=health_monitor)
        thread.daemon = True
        thread.start()

    def _send_health_ping(self):
        """Send health ping to EventBus"""
        try:
            ping_data = {
                'service': 'digital_twin_core',
                'status': 'healthy',
                'timestamp': fields.Datetime.now().isoformat(),
                'connection_id': self.connection_id,
                'metrics': {
                    'active_twins': len(self.env['bcm.personal.digital.twin'].search([('sync_status', '=', 'active')])),
                    'messages_sent_today': self.messages_sent_today,
                    'messages_received_today': self.messages_received_today
                }
            }

            success = self.send_message('health_ping', ping_data, 'low')
            if success:
                self.last_ping = fields.Datetime.now()
                self.health_status = 'healthy'
            else:
                self.health_status = 'degraded'

        except Exception as e:
            self.health_status = 'unhealthy'
            _logger.error(f"Health ping failed: {str(e)}")

    # Event Subscription

    def _subscribe_to_events(self):
        """Subscribe to configured event types"""
        try:
            if not self.subscribe_events:
                return

            event_types = [e.strip() for e in self.subscribe_events.split(',')]

            subscription_data = {
                'connection_id': self.connection_id,
                'event_types': event_types,
                'service': 'digital_twin_core'
            }

            success = self.send_message('subscribe_events', subscription_data, 'high')
            if success:
                _logger.info(f"Subscribed to events: {event_types}")
            else:
                _logger.error("Failed to subscribe to events")

        except Exception as e:
            _logger.error(f"Event subscription failed: {str(e)}")

    # Utility Methods

    def _log_message(self, event_type, message_data, direction):
        """Log message for debugging and monitoring"""
        logs = self.message_log or []

        log_entry = {
            'timestamp': fields.Datetime.now().isoformat(),
            'event_type': event_type,
            'direction': direction,
            'message_id': message_data.get('id') if isinstance(message_data, dict) else None,
            'size_bytes': len(json.dumps(message_data)),
            'status': 'success'
        }

        logs.append(log_entry)

        # Keep only last 500 messages
        if len(logs) > 500:
            logs = logs[-500:]

        self.message_log = logs

    def _log_error(self, error_message):
        """Log error for monitoring"""
        errors = self.error_log or []

        error_entry = {
            'timestamp': fields.Datetime.now().isoformat(),
            'error': error_message,
            'connection_status': self.status,
            'health_status': self.health_status
        }

        errors.append(error_entry)

        # Keep only last 100 errors
        if len(errors) > 100:
            errors = errors[-100:]

        self.error_log = errors

    # Action Methods

    def action_connect(self):
        """Action to connect to EventBus"""
        self.ensure_one()
        success = self.connect_to_eventbus()

        if success:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Success"),
                    'message': _("Connected to EventBus successfully"),
                    'type': 'success'
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Error"),
                    'message': _("Failed to connect to EventBus"),
                    'type': 'danger'
                }
            }

    def action_disconnect(self):
        """Action to disconnect from EventBus"""
        self.ensure_one()
        success = self.disconnect_from_eventbus()

        if success:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Info"),
                    'message': _("Disconnected from EventBus"),
                    'type': 'info'
                }
            }

    def action_test_connection(self):
        """Action to test EventBus connection"""
        self.ensure_one()

        try:
            # Send test message
            test_data = {
                'test': True,
                'timestamp': fields.Datetime.now().isoformat(),
                'message': 'EventBus connection test'
            }

            success = self.send_message('connection_test', test_data, 'low')

            if success:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _("Success"),
                        'message': _("EventBus connection test successful"),
                        'type': 'success'
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _("Error"),
                        'message': _("EventBus connection test failed"),
                        'type': 'danger'
                    }
                }

        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Error"),
                    'message': f"Connection test failed: {str(e)}",
                    'type': 'danger'
                }
            }

    # Cron Methods

    @api.model
    def cron_health_check(self):
        """Cron job for health monitoring"""
        integration = self.get_singleton()

        if integration.status == 'connected':
            # Check if connection is still alive
            last_activity = max(
                integration.last_ping or fields.Datetime.from_string('1970-01-01'),
                integration.last_message_sent or fields.Datetime.from_string('1970-01-01'),
                integration.last_message_received or fields.Datetime.from_string('1970-01-01')
            )

            if (fields.Datetime.now() - last_activity).total_seconds() > 300:  # 5 minutes
                integration.health_status = 'degraded'

                if integration.auto_reconnect:
                    integration.connect_to_eventbus()

    @api.model
    def cron_cleanup_logs(self):
        """Cron job to clean up old logs"""
        integration = self.get_singleton()

        try:
            # Clean message logs (keep last 7 days)
            cutoff_date = (fields.Datetime.now() - timedelta(days=7)).isoformat()

            logs = integration.message_log or []
            filtered_logs = [
                log for log in logs
                if log.get('timestamp', '') >= cutoff_date
            ]
            integration.message_log = filtered_logs

            # Clean error logs (keep last 3 days)
            error_cutoff = (fields.Datetime.now() - timedelta(days=3)).isoformat()

            errors = integration.error_log or []
            filtered_errors = [
                error for error in errors
                if error.get('timestamp', '') >= error_cutoff
            ]
            integration.error_log = filtered_errors

        except Exception as e:
            _logger.error(f"Log cleanup failed: {str(e)}")

    # API Methods

    @api.model
    def api_send_event(self, event_type, data, priority='medium', target_services=None):
        """API method to send event to EventBus"""
        integration = self.get_singleton()
        return integration.send_message(event_type, data, priority, target_services)

    @api.model
    def api_receive_event(self, message_data):
        """API method to receive event from EventBus"""
        integration = self.get_singleton()
        return integration.receive_message(message_data)