# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, AccessError
import json
import logging
import requests
import threading
from datetime import datetime, timedelta
from contextlib import closing

_logger = logging.getLogger(__name__)

class DigitalTwinLifecycleManager(models.Model):
    _name = 'bcm.digital.twin.lifecycle.manager'
    _description = 'Digital Twin Lifecycle Manager'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'priority desc, create_date desc'

    # Core Information
    name = fields.Char(
        string='Manager Name',
        default='Digital Twin Lifecycle Manager',
        readonly=True
    )

    # Configuration
    auto_create_twins = fields.Boolean(
        string='Auto Create Twins',
        default=True,
        help="Automatically create digital twins for new users"
    )

    real_time_processing = fields.Boolean(
        string='Real-time Processing',
        default=True,
        help="Process lifecycle events in real-time"
    )

    eventbus_integration = fields.Boolean(
        string='EventBus Integration',
        default=True,
        help="Send lifecycle events to EventBus"
    )

    sync_frequency = fields.Selection([
        ('immediate', 'Immediate'),
        ('5min', 'Every 5 minutes'),
        ('15min', 'Every 15 minutes'),
        ('30min', 'Every 30 minutes'),
        ('1hour', 'Every hour'),
        ('6hour', 'Every 6 hours'),
        ('daily', 'Daily')
    ], string='Sync Frequency', default='immediate',
       help="Frequency for synchronizing user changes")

    # Status and Monitoring
    status = fields.Selection([
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('maintenance', 'Maintenance'),
        ('error', 'Error')
    ], string='Status', default='active', tracking=True)

    last_sync = fields.Datetime(
        string='Last Sync',
        help="Last time the manager synchronized user data"
    )

    total_twins_managed = fields.Integer(
        string='Total Twins Managed',
        compute='_compute_managed_twins',
        help="Total number of digital twins managed"
    )

    active_twins_count = fields.Integer(
        string='Active Twins',
        compute='_compute_managed_twins',
        help="Number of active digital twins"
    )

    # Performance Metrics
    events_processed_today = fields.Integer(
        string='Events Processed Today',
        compute='_compute_performance_metrics',
        help="Number of lifecycle events processed today"
    )

    success_rate = fields.Float(
        string='Success Rate (%)',
        compute='_compute_performance_metrics',
        help="Success rate for lifecycle event processing"
    )

    # Event Processing Configuration
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Priority', default='high')

    queue_size = fields.Integer(
        string='Queue Size',
        default=1000,
        help="Maximum size of the event processing queue"
    )

    max_retry_attempts = fields.Integer(
        string='Max Retry Attempts',
        default=3,
        help="Maximum number of retry attempts for failed events"
    )

    # Lifecycle Event Logs
    lifecycle_logs = fields.Json(
        string='Lifecycle Logs',
        help="JSON log of recent lifecycle events",
        default=lambda self: []
    )

    error_logs = fields.Json(
        string='Error Logs',
        help="JSON log of processing errors",
        default=lambda self: []
    )

    # Service Integration
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )

    # Computed Fields
    @api.depends()
    def _compute_managed_twins(self):
        for record in self:
            twins = self.env['bcm.personal.digital.twin'].search([])
            record.total_twins_managed = len(twins)
            record.active_twins_count = len(twins.filtered(lambda t: t.sync_status == 'active'))

    @api.depends()
    def _compute_performance_metrics(self):
        for record in self:
            today = fields.Date.today()
            logs = record.lifecycle_logs or []

            # Count today's events
            today_events = [
                log for log in logs
                if log.get('timestamp', '').startswith(today.strftime('%Y-%m-%d'))
            ]
            record.events_processed_today = len(today_events)

            # Calculate success rate
            if logs:
                successful_events = len([log for log in logs if log.get('status') == 'success'])
                record.success_rate = (successful_events / len(logs)) * 100
            else:
                record.success_rate = 0.0

    # Core Lifecycle Management Methods

    @api.model
    def get_singleton(self):
        """Get or create the singleton lifecycle manager"""
        manager = self.search([], limit=1)
        if not manager:
            manager = self.create({
                'name': 'Digital Twin Lifecycle Manager'
            })
        return manager

    def process_user_creation(self, user_id, user_data=None):
        """Process user creation event"""
        try:
            self._log_event('user_creation', {
                'user_id': user_id,
                'user_data': user_data or {},
                'auto_create': self.auto_create_twins
            })

            if not self.auto_create_twins:
                return True

            # Create digital twin for new user
            twin_model = self.env['bcm.personal.digital.twin']
            twin = twin_model.handle_user_created(user_id)

            if twin:
                self._send_lifecycle_event('user_created', {
                    'user_id': user_id,
                    'twin_id': twin.id,
                    'status': 'success'
                })
                return True
            else:
                self._log_error('Failed to create digital twin', {
                    'user_id': user_id,
                    'operation': 'user_creation'
                })
                return False

        except Exception as e:
            self._log_error(f"Error processing user creation: {str(e)}", {
                'user_id': user_id,
                'operation': 'user_creation'
            })
            return False

    def process_user_update(self, user_id, changed_fields, old_values=None):
        """Process user profile update event"""
        try:
            self._log_event('user_update', {
                'user_id': user_id,
                'changed_fields': changed_fields,
                'old_values': old_values or {}
            })

            # Update digital twin
            twin_model = self.env['bcm.personal.digital.twin']
            success = twin_model.handle_user_updated(user_id, changed_fields)

            if success:
                self._send_lifecycle_event('user_updated', {
                    'user_id': user_id,
                    'changed_fields': changed_fields,
                    'status': 'success'
                })
                return True
            else:
                self._log_error('Failed to update digital twin', {
                    'user_id': user_id,
                    'changed_fields': changed_fields,
                    'operation': 'user_update'
                })
                return False

        except Exception as e:
            self._log_error(f"Error processing user update: {str(e)}", {
                'user_id': user_id,
                'operation': 'user_update'
            })
            return False

    def process_user_login(self, user_id, login_info=None):
        """Process user login event"""
        try:
            login_data = login_info or {
                'timestamp': fields.Datetime.now().isoformat(),
                'ip_address': self.env.context.get('ip_address', ''),
                'user_agent': self.env.context.get('user_agent', '')
            }

            self._log_event('user_login', {
                'user_id': user_id,
                'login_info': login_data
            })

            # Handle login in digital twin
            twin_model = self.env['bcm.personal.digital.twin']
            success = twin_model.handle_user_login(user_id, login_data)

            if success:
                self._send_lifecycle_event('user_logged_in', {
                    'user_id': user_id,
                    'login_info': login_data,
                    'status': 'success'
                })
                return True
            else:
                self._log_error('Failed to process user login', {
                    'user_id': user_id,
                    'operation': 'user_login'
                })
                return False

        except Exception as e:
            self._log_error(f"Error processing user login: {str(e)}", {
                'user_id': user_id,
                'operation': 'user_login'
            })
            return False

    def process_user_logout(self, user_id, session_info=None):
        """Process user logout event"""
        try:
            session_data = session_info or {
                'timestamp': fields.Datetime.now().isoformat(),
                'session_duration': 0,
                'pages_visited': 0
            }

            self._log_event('user_logout', {
                'user_id': user_id,
                'session_info': session_data
            })

            # Handle logout in digital twin
            twin_model = self.env['bcm.personal.digital.twin']
            success = twin_model.handle_user_logout(user_id, session_data)

            if success:
                self._send_lifecycle_event('user_logged_out', {
                    'user_id': user_id,
                    'session_info': session_data,
                    'status': 'success'
                })
                return True
            else:
                self._log_error('Failed to process user logout', {
                    'user_id': user_id,
                    'operation': 'user_logout'
                })
                return False

        except Exception as e:
            self._log_error(f"Error processing user logout: {str(e)}", {
                'user_id': user_id,
                'operation': 'user_logout'
            })
            return False

    def process_user_deactivation(self, user_id):
        """Process user deactivation event"""
        try:
            self._log_event('user_deactivation', {
                'user_id': user_id
            })

            # Handle deactivation in digital twin
            twin_model = self.env['bcm.personal.digital.twin']
            success = twin_model.handle_user_deactivated(user_id)

            if success:
                self._send_lifecycle_event('user_deactivated', {
                    'user_id': user_id,
                    'status': 'success'
                })
                return True
            else:
                self._log_error('Failed to process user deactivation', {
                    'user_id': user_id,
                    'operation': 'user_deactivation'
                })
                return False

        except Exception as e:
            self._log_error(f"Error processing user deactivation: {str(e)}", {
                'user_id': user_id,
                'operation': 'user_deactivation'
            })
            return False

    def process_role_change(self, user_id, role_changes):
        """Process user role change event"""
        try:
            self._log_event('role_change', {
                'user_id': user_id,
                'role_changes': role_changes
            })

            # Handle role change in digital twin
            twin_model = self.env['bcm.personal.digital.twin']
            success = twin_model.handle_role_changed(user_id, role_changes)

            if success:
                self._send_lifecycle_event('user_role_changed', {
                    'user_id': user_id,
                    'role_changes': role_changes,
                    'status': 'success'
                })
                return True
            else:
                self._log_error('Failed to process role change', {
                    'user_id': user_id,
                    'role_changes': role_changes,
                    'operation': 'role_change'
                })
                return False

        except Exception as e:
            self._log_error(f"Error processing role change: {str(e)}", {
                'user_id': user_id,
                'operation': 'role_change'
            })
            return False

    # Bulk Operations

    def sync_all_users(self):
        """Synchronize all users with their digital twins"""
        try:
            self.status = 'active'
            users = self.env['res.users'].search([('active', '=', True)])
            twin_model = self.env['bcm.personal.digital.twin']

            processed = 0
            errors = 0

            for user in users:
                try:
                    # Get or create twin
                    twin = twin_model.search([('user_id', '=', user.id)], limit=1)
                    if not twin:
                        twin = twin_model.create_for_user(user.id)

                    # Sync data
                    if twin and twin.real_time_sync:
                        twin.action_sync_personal_data()

                    processed += 1

                except Exception as e:
                    _logger.error(f"Failed to sync user {user.name}: {str(e)}")
                    errors += 1

            self.last_sync = fields.Datetime.now()

            # Log results
            self._log_event('bulk_sync', {
                'users_processed': processed,
                'errors': errors,
                'total_users': len(users)
            })

            # Send summary event
            self._send_lifecycle_event('bulk_sync_completed', {
                'users_processed': processed,
                'errors': errors,
                'total_users': len(users),
                'status': 'success' if errors == 0 else 'partial_success'
            })

            return True

        except Exception as e:
            self.status = 'error'
            self._log_error(f"Bulk sync failed: {str(e)}", {
                'operation': 'bulk_sync'
            })
            return False

    def cleanup_inactive_twins(self):
        """Clean up inactive digital twins"""
        try:
            cutoff_date = fields.Datetime.now() - timedelta(days=90)

            inactive_twins = self.env['bcm.personal.digital.twin'].search([
                ('last_activity', '<', cutoff_date),
                ('sync_status', '=', 'offline')
            ])

            archived_count = 0
            for twin in inactive_twins:
                twin.write({
                    'sync_status': 'maintenance',
                    'real_time_sync': False
                })
                archived_count += 1

            self._log_event('cleanup', {
                'twins_archived': archived_count
            })

            return True

        except Exception as e:
            self._log_error(f"Cleanup failed: {str(e)}", {
                'operation': 'cleanup'
            })
            return False

    # EventBus Integration

    def _send_lifecycle_event(self, event_type, data, priority='medium'):
        """Send lifecycle event to EventBus"""
        if not self.eventbus_integration:
            return

        try:
            eventbus_url = self.env['ir.config_parameter'].sudo().get_param(
                'bcm.eventbus.url', 'ws://localhost:8001'
            )

            message = {
                'event_type': event_type,
                'source': 'digital_twin_lifecycle_manager',
                'timestamp': fields.Datetime.now().isoformat(),
                'priority': priority,
                'data': data,
                'manager_id': self.id
            }

            # Send via HTTP if WebSocket not available
            if eventbus_url.startswith('http'):
                response = requests.post(f"{eventbus_url}/events", json=message, timeout=5)
                response.raise_for_status()
            else:
                # Use WebSocket (simplified implementation)
                self._send_websocket_message(eventbus_url, message)

            _logger.info(f"Lifecycle event sent: {event_type}")

        except Exception as e:
            _logger.error(f"Failed to send lifecycle event: {str(e)}")

    def _send_websocket_message(self, url, message):
        """Send message via WebSocket in background"""
        def send_message():
            try:
                import websocket
                with closing(websocket.create_connection(url, timeout=5)) as ws:
                    ws.send(json.dumps(message))
            except Exception as e:
                _logger.error(f"WebSocket send failed: {str(e)}")

        thread = threading.Thread(target=send_message)
        thread.daemon = True
        thread.start()

    # Logging Methods

    def _log_event(self, event_type, data):
        """Log lifecycle event"""
        logs = self.lifecycle_logs or []

        log_entry = {
            'timestamp': fields.Datetime.now().isoformat(),
            'event_type': event_type,
            'data': data,
            'status': 'success'
        }

        logs.append(log_entry)

        # Keep only last 1000 logs
        if len(logs) > 1000:
            logs = logs[-1000:]

        self.lifecycle_logs = logs

    def _log_error(self, error_message, context):
        """Log processing error"""
        errors = self.error_logs or []

        error_entry = {
            'timestamp': fields.Datetime.now().isoformat(),
            'error': error_message,
            'context': context
        }

        errors.append(error_entry)

        # Keep only last 100 errors
        if len(errors) > 100:
            errors = errors[-100:]

        self.error_logs = errors

    # Action Methods

    def action_start_manager(self):
        """Start the lifecycle manager"""
        self.ensure_one()
        self.status = 'active'
        self._log_event('manager_started', {})

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Success"),
                'message': _("Digital Twin Lifecycle Manager started"),
                'type': 'success'
            }
        }

    def action_pause_manager(self):
        """Pause the lifecycle manager"""
        self.ensure_one()
        self.status = 'paused'
        self._log_event('manager_paused', {})

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Info"),
                'message': _("Digital Twin Lifecycle Manager paused"),
                'type': 'info'
            }
        }

    def action_sync_all_users(self):
        """Action to sync all users"""
        self.ensure_one()
        success = self.sync_all_users()

        if success:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Success"),
                    'message': _("All users synchronized successfully"),
                    'type': 'success'
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Error"),
                    'message': _("Failed to sync all users"),
                    'type': 'danger'
                }
            }

    def action_view_logs(self):
        """View lifecycle logs"""
        self.ensure_one()

        return {
            'name': _('Lifecycle Logs'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.digital.twin.lifecycle.logs.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_manager_id': self.id,
                'logs': self.lifecycle_logs,
                'errors': self.error_logs
            }
        }

    # Cron Methods

    @api.model
    def cron_process_pending_events(self):
        """Cron job to process pending lifecycle events"""
        manager = self.get_singleton()
        if manager.status != 'active':
            return

        try:
            # This would process queued events in a real implementation
            # For now, we'll perform a periodic sync
            if manager.sync_frequency != 'immediate':
                manager.sync_all_users()

        except Exception as e:
            _logger.error(f"Cron job failed: {str(e)}")
            manager.status = 'error'

    @api.model
    def cron_cleanup_old_logs(self):
        """Cron job to clean up old logs"""
        manager = self.get_singleton()

        try:
            # Clean up old lifecycle logs (keep last 30 days)
            cutoff_date = (fields.Datetime.now() - timedelta(days=30)).isoformat()

            logs = manager.lifecycle_logs or []
            filtered_logs = [
                log for log in logs
                if log.get('timestamp', '') >= cutoff_date
            ]
            manager.lifecycle_logs = filtered_logs

            # Clean up old error logs (keep last 7 days)
            error_cutoff = (fields.Datetime.now() - timedelta(days=7)).isoformat()

            errors = manager.error_logs or []
            filtered_errors = [
                error for error in errors
                if error.get('timestamp', '') >= error_cutoff
            ]
            manager.error_logs = filtered_errors

        except Exception as e:
            _logger.error(f"Log cleanup failed: {str(e)}")

    # API Methods for CRM Integration

    @api.model
    def api_user_created(self, user_id, user_data=None):
        """API endpoint for user creation events from CRM"""
        manager = self.get_singleton()
        return manager.process_user_creation(user_id, user_data)

    @api.model
    def api_user_updated(self, user_id, changed_fields, old_values=None):
        """API endpoint for user update events from CRM"""
        manager = self.get_singleton()
        return manager.process_user_update(user_id, changed_fields, old_values)

    @api.model
    def api_user_login(self, user_id, login_info=None):
        """API endpoint for user login events from CRM"""
        manager = self.get_singleton()
        return manager.process_user_login(user_id, login_info)

    @api.model
    def api_user_logout(self, user_id, session_info=None):
        """API endpoint for user logout events from CRM"""
        manager = self.get_singleton()
        return manager.process_user_logout(user_id, session_info)

    @api.model
    def api_user_deactivated(self, user_id):
        """API endpoint for user deactivation events from CRM"""
        manager = self.get_singleton()
        return manager.process_user_deactivation(user_id)

    @api.model
    def api_role_changed(self, user_id, role_changes):
        """API endpoint for role change events from CRM"""
        manager = self.get_singleton()
        return manager.process_role_change(user_id, role_changes)