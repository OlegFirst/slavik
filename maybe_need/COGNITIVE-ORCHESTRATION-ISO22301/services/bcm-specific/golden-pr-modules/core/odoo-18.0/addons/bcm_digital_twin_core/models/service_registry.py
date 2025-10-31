# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, AccessError
import json
import logging
import requests
import threading
import time
from datetime import datetime, timedelta
from collections import defaultdict

_logger = logging.getLogger(__name__)

class ServiceRegistry(models.Model):
    _name = 'bcm.service.registry'
    _description = 'Service Registry & Health Monitor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    # Core Information
    name = fields.Char(
        string='Registry Name',
        default='BCM Service Registry',
        required=True
    )

    description = fields.Text(
        string='Description',
        help="Description of the service registry"
    )

    # Configuration
    discovery_enabled = fields.Boolean(
        string='Service Discovery Enabled',
        default=True,
        help="Enable automatic service discovery"
    )

    health_monitoring = fields.Boolean(
        string='Health Monitoring',
        default=True,
        help="Enable health monitoring for registered services"
    )

    auto_registration = fields.Boolean(
        string='Auto Registration',
        default=True,
        help="Allow services to auto-register"
    )

    # Monitoring Configuration
    health_check_interval = fields.Integer(
        string='Health Check Interval (seconds)',
        default=60,
        help="Interval between health checks"
    )

    timeout_threshold = fields.Integer(
        string='Timeout Threshold (seconds)',
        default=30,
        help="Timeout threshold for health checks"
    )

    retry_attempts = fields.Integer(
        string='Retry Attempts',
        default=3,
        help="Number of retry attempts for failed health checks"
    )

    # Status
    status = fields.Selection([
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('maintenance', 'Maintenance'),
        ('error', 'Error')
    ], string='Status', default='active', tracking=True)

    last_discovery_scan = fields.Datetime(
        string='Last Discovery Scan',
        help="Timestamp of last service discovery scan"
    )

    last_health_check = fields.Datetime(
        string='Last Health Check',
        help="Timestamp of last health check cycle"
    )

    # Metrics
    total_services = fields.Integer(
        string='Total Services',
        compute='_compute_service_metrics',
        help="Total number of registered services"
    )

    healthy_services = fields.Integer(
        string='Healthy Services',
        compute='_compute_service_metrics',
        help="Number of healthy services"
    )

    unhealthy_services = fields.Integer(
        string='Unhealthy Services',
        compute='_compute_service_metrics',
        help="Number of unhealthy services"
    )

    average_response_time = fields.Float(
        string='Average Response Time (ms)',
        compute='_compute_service_metrics',
        help="Average response time across all services"
    )

    # Service Data
    registered_services = fields.Json(
        string='Registered Services',
        help="JSON data of all registered services",
        default=lambda self: {}
    )

    service_health_log = fields.Json(
        string='Service Health Log',
        help="Historical health data for services",
        default=lambda self: {}
    )

    discovery_log = fields.Json(
        string='Discovery Log',
        help="Log of service discovery events",
        default=lambda self: []
    )

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )

    # Computed Fields
    @api.depends('registered_services')
    def _compute_service_metrics(self):
        for record in self:
            services = record.registered_services or {}

            record.total_services = len(services)

            healthy_count = 0
            unhealthy_count = 0
            total_response_time = 0
            response_time_count = 0

            for service_id, service_data in services.items():
                health_status = service_data.get('health_status', 'unknown')
                if health_status == 'healthy':
                    healthy_count += 1
                elif health_status in ['unhealthy', 'degraded']:
                    unhealthy_count += 1

                response_time = service_data.get('last_response_time', 0)
                if response_time > 0:
                    total_response_time += response_time
                    response_time_count += 1

            record.healthy_services = healthy_count
            record.unhealthy_services = unhealthy_count
            record.average_response_time = (
                total_response_time / response_time_count
                if response_time_count > 0 else 0
            )

    # Core Registry Methods

    @api.model
    def get_singleton(self):
        """Get or create the singleton service registry"""
        registry = self.search([], limit=1)
        if not registry:
            registry = self.create({
                'name': 'BCM Service Registry'
            })
        return registry

    def register_service(self, service_info):
        """Register a new service or update existing one"""
        try:
            if not isinstance(service_info, dict):
                raise ValueError("Service info must be a dictionary")

            required_fields = ['service_id', 'name', 'url', 'type']
            missing_fields = [field for field in required_fields if field not in service_info]
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")

            services = self.registered_services or {}
            service_id = service_info['service_id']

            # Prepare service data
            service_data = {
                'service_id': service_id,
                'name': service_info['name'],
                'url': service_info['url'],
                'type': service_info['type'],
                'version': service_info.get('version', '1.0.0'),
                'description': service_info.get('description', ''),
                'tags': service_info.get('tags', []),
                'endpoints': service_info.get('endpoints', {}),
                'health_endpoint': service_info.get('health_endpoint', '/health'),
                'dependencies': service_info.get('dependencies', []),
                'metadata': service_info.get('metadata', {}),
                'registered_at': fields.Datetime.now().isoformat(),
                'last_seen': fields.Datetime.now().isoformat(),
                'health_status': 'unknown',
                'last_health_check': None,
                'last_response_time': 0,
                'error_count': 0,
                'uptime_percentage': 100.0
            }

            # Update existing service or add new
            if service_id in services:
                # Preserve some existing data
                existing_data = services[service_id]
                service_data.update({
                    'registered_at': existing_data.get('registered_at', service_data['registered_at']),
                    'health_status': existing_data.get('health_status', 'unknown'),
                    'error_count': existing_data.get('error_count', 0),
                    'uptime_percentage': existing_data.get('uptime_percentage', 100.0)
                })

            services[service_id] = service_data
            self.registered_services = services

            # Log discovery event
            self._log_discovery_event('service_registered', {
                'service_id': service_id,
                'name': service_info['name'],
                'type': service_info['type'],
                'url': service_info['url']
            })

            # Send EventBus notification
            self._send_registry_event('service_registered', service_data)

            _logger.info(f"Service registered: {service_info['name']} ({service_id})")
            return True

        except Exception as e:
            _logger.error(f"Failed to register service: {str(e)}")
            self._log_discovery_event('registration_error', {
                'error': str(e),
                'service_info': service_info
            })
            return False

    def unregister_service(self, service_id):
        """Unregister a service"""
        try:
            services = self.registered_services or {}

            if service_id not in services:
                raise ValueError(f"Service {service_id} not found")

            service_data = services.pop(service_id)
            self.registered_services = services

            # Log discovery event
            self._log_discovery_event('service_unregistered', {
                'service_id': service_id,
                'name': service_data.get('name', 'Unknown')
            })

            # Send EventBus notification
            self._send_registry_event('service_unregistered', service_data)

            _logger.info(f"Service unregistered: {service_id}")
            return True

        except Exception as e:
            _logger.error(f"Failed to unregister service {service_id}: {str(e)}")
            return False

    def update_service_health(self, service_id, health_status, health_data=None):
        """Update health status for a service"""
        try:
            services = self.registered_services or {}

            if service_id not in services:
                _logger.warning(f"Service {service_id} not found for health update")
                return False

            service_data = services[service_id]
            service_data['health_status'] = health_status
            service_data['last_health_check'] = fields.Datetime.now().isoformat()
            service_data['last_seen'] = fields.Datetime.now().isoformat()

            if health_data:
                service_data['last_response_time'] = health_data.get('response_time', 0)
                if health_status == 'unhealthy':
                    service_data['error_count'] = service_data.get('error_count', 0) + 1

                # Update uptime calculation
                self._update_uptime_percentage(service_data)

            services[service_id] = service_data
            self.registered_services = services

            # Log health data
            self._log_health_data(service_id, health_status, health_data)

            # Send EventBus notification for critical status changes
            if health_status in ['unhealthy', 'degraded']:
                self._send_registry_event('service_health_alert', {
                    'service_id': service_id,
                    'service_name': service_data.get('name'),
                    'health_status': health_status,
                    'health_data': health_data
                })

            return True

        except Exception as e:
            _logger.error(f"Failed to update health for service {service_id}: {str(e)}")
            return False

    def get_service(self, service_id):
        """Get service information by ID"""
        services = self.registered_services or {}
        return services.get(service_id)

    def get_services_by_type(self, service_type):
        """Get all services of a specific type"""
        services = self.registered_services or {}
        return {
            sid: sdata for sid, sdata in services.items()
            if sdata.get('type') == service_type
        }

    def get_healthy_services(self):
        """Get all healthy services"""
        services = self.registered_services or {}
        return {
            sid: sdata for sid, sdata in services.items()
            if sdata.get('health_status') == 'healthy'
        }

    def discover_services(self):
        """Discover services automatically"""
        try:
            if not self.discovery_enabled:
                return True

            # Auto-discover BCM modules
            self._discover_bcm_modules()

            # Auto-discover known service endpoints
            self._discover_known_services()

            # Auto-discover from EventBus
            self._discover_from_eventbus()

            self.last_discovery_scan = fields.Datetime.now()

            self._log_discovery_event('discovery_scan_completed', {
                'services_found': len(self.registered_services or {}),
                'timestamp': fields.Datetime.now().isoformat()
            })

            return True

        except Exception as e:
            _logger.error(f"Service discovery failed: {str(e)}")
            self._log_discovery_event('discovery_error', {'error': str(e)})
            return False

    def _discover_bcm_modules(self):
        """Discover BCM modules as services"""
        try:
            # Get all installed BCM modules
            bcm_modules = self.env['ir.module.module'].search([
                ('name', 'ilike', 'bcm_%'),
                ('state', '=', 'installed')
            ])

            for module in bcm_modules:
                service_info = {
                    'service_id': f"bcm_module_{module.name}",
                    'name': module.shortdesc or module.name,
                    'url': f"http://localhost:8069/web#action=module_info&module={module.name}",
                    'type': 'bcm_module',
                    'version': module.latest_version or '1.0.0',
                    'description': module.summary or '',
                    'tags': ['bcm', 'odoo_module'],
                    'endpoints': {
                        'main': f"/web/dataset/call_kw/{module.name}",
                        'info': f"/web#action=module_info&module={module.name}"
                    },
                    'metadata': {
                        'module_name': module.name,
                        'author': module.author or 'Unknown',
                        'category': module.category_id.name if module.category_id else 'Unknown'
                    }
                }

                self.register_service(service_info)

        except Exception as e:
            _logger.error(f"BCM module discovery failed: {str(e)}")

    def _discover_known_services(self):
        """Discover known external services"""
        known_services = [
            {
                'service_id': 'eventbus_server',
                'name': 'EventBus Server',
                'url': 'ws://localhost:8001',
                'type': 'messaging',
                'health_endpoint': '/health',
                'tags': ['eventbus', 'websocket']
            },
            {
                'service_id': 'ai_orchestrator',
                'name': 'AI Orchestrator',
                'url': 'http://localhost:8000',
                'type': 'ai_service',
                'health_endpoint': '/health',
                'tags': ['ai', 'orchestrator']
            },
            {
                'service_id': 'bia_engine',
                'name': 'Business Impact Analysis Engine',
                'url': 'http://localhost:8082',
                'type': 'analysis_engine',
                'health_endpoint': '/health',
                'tags': ['bia', 'analysis']
            },
            {
                'service_id': 'document_processor',
                'name': 'Document Processor',
                'url': 'http://localhost:8083',
                'type': 'document_service',
                'health_endpoint': '/health',
                'tags': ['documents', 'processing']
            },
            {
                'service_id': 'web_portal_v2',
                'name': 'Web Portal V2',
                'url': 'http://localhost:3000',
                'type': 'frontend',
                'health_endpoint': '/api/health',
                'tags': ['frontend', 'vue3']
            },
            {
                'service_id': 'admin_panel',
                'name': 'Admin Panel',
                'url': 'http://localhost:3001',
                'type': 'frontend',
                'health_endpoint': '/api/health',
                'tags': ['frontend', 'react', 'admin']
            }
        ]

        for service_info in known_services:
            self.register_service(service_info)

    def _discover_from_eventbus(self):
        """Discover services from EventBus announcements"""
        try:
            # This would listen to EventBus for service announcements
            # For now, we'll simulate receiving announcements
            pass

        except Exception as e:
            _logger.error(f"EventBus discovery failed: {str(e)}")

    # Health Monitoring Methods

    def perform_health_checks(self):
        """Perform health checks on all registered services"""
        try:
            if not self.health_monitoring:
                return True

            services = self.registered_services or {}
            checked_count = 0
            healthy_count = 0
            errors = []

            for service_id, service_data in services.items():
                try:
                    health_status, health_data = self._check_service_health(service_data)
                    self.update_service_health(service_id, health_status, health_data)

                    if health_status == 'healthy':
                        healthy_count += 1

                    checked_count += 1

                except Exception as e:
                    error_msg = f"Health check failed for {service_id}: {str(e)}"
                    errors.append(error_msg)
                    _logger.error(error_msg)

                    # Mark as unhealthy
                    self.update_service_health(service_id, 'unhealthy', {
                        'error': str(e),
                        'check_time': fields.Datetime.now().isoformat()
                    })

            self.last_health_check = fields.Datetime.now()

            # Log health check summary
            summary = {
                'total_checked': checked_count,
                'healthy': healthy_count,
                'errors': len(errors),
                'error_messages': errors[:5]  # Limit to first 5 errors
            }

            self._log_discovery_event('health_check_completed', summary)

            # Send alert if too many services are unhealthy
            unhealthy_percentage = ((checked_count - healthy_count) / checked_count * 100) if checked_count > 0 else 0
            if unhealthy_percentage > 30:  # More than 30% unhealthy
                self._send_registry_event('system_health_alert', {
                    'alert_type': 'high_unhealthy_percentage',
                    'unhealthy_percentage': unhealthy_percentage,
                    'summary': summary
                })

            return True

        except Exception as e:
            _logger.error(f"Health check cycle failed: {str(e)}")
            return False

    def _check_service_health(self, service_data):
        """Check health of a single service"""
        try:
            url = service_data.get('url', '')
            health_endpoint = service_data.get('health_endpoint', '/health')
            service_type = service_data.get('type', '')

            start_time = time.time()

            # Different health check methods based on service type
            if service_type == 'bcm_module':
                # For BCM modules, check if they're still installed and accessible
                health_status, health_data = self._check_bcm_module_health(service_data)
            elif url.startswith('ws://') or url.startswith('wss://'):
                # WebSocket service
                health_status, health_data = self._check_websocket_health(url)
            elif url.startswith('http://') or url.startswith('https://'):
                # HTTP service
                health_status, health_data = self._check_http_health(url, health_endpoint)
            else:
                # Unknown service type
                health_status = 'unknown'
                health_data = {'reason': 'Unknown service type'}

            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            health_data['response_time'] = response_time
            health_data['check_time'] = fields.Datetime.now().isoformat()

            return health_status, health_data

        except Exception as e:
            return 'unhealthy', {'error': str(e), 'check_time': fields.Datetime.now().isoformat()}

    def _check_bcm_module_health(self, service_data):
        """Check health of a BCM module"""
        try:
            module_name = service_data.get('metadata', {}).get('module_name')
            if not module_name:
                return 'unhealthy', {'reason': 'No module name'}

            # Check if module is still installed
            module = self.env['ir.module.module'].search([
                ('name', '=', module_name),
                ('state', '=', 'installed')
            ], limit=1)

            if module:
                return 'healthy', {
                    'module_version': module.latest_version,
                    'module_state': module.state
                }
            else:
                return 'unhealthy', {'reason': 'Module not installed or not found'}

        except Exception as e:
            return 'unhealthy', {'error': str(e)}

    def _check_websocket_health(self, url):
        """Check health of a WebSocket service"""
        try:
            import websocket
            ws = websocket.create_connection(url, timeout=self.timeout_threshold)
            ws.close()
            return 'healthy', {'connection': 'successful'}

        except Exception as e:
            return 'unhealthy', {'connection_error': str(e)}

    def _check_http_health(self, url, health_endpoint):
        """Check health of an HTTP service"""
        try:
            health_url = f"{url.rstrip('/')}{health_endpoint}"
            response = requests.get(health_url, timeout=self.timeout_threshold)

            if response.status_code == 200:
                try:
                    health_data = response.json()
                    status = health_data.get('status', 'healthy')
                    return status, health_data
                except:
                    return 'healthy', {'status_code': response.status_code}
            else:
                return 'degraded', {
                    'status_code': response.status_code,
                    'reason': f"HTTP {response.status_code}"
                }

        except requests.exceptions.Timeout:
            return 'unhealthy', {'reason': 'timeout'}
        except requests.exceptions.ConnectionError:
            return 'unhealthy', {'reason': 'connection_error'}
        except Exception as e:
            return 'unhealthy', {'error': str(e)}

    # Logging and Monitoring

    def _log_discovery_event(self, event_type, data):
        """Log a discovery event"""
        logs = self.discovery_log or []

        log_entry = {
            'timestamp': fields.Datetime.now().isoformat(),
            'event_type': event_type,
            'data': data
        }

        logs.append(log_entry)

        # Keep only last 1000 log entries
        if len(logs) > 1000:
            logs = logs[-1000:]

        self.discovery_log = logs

    def _log_health_data(self, service_id, health_status, health_data):
        """Log health data for a service"""
        health_log = self.service_health_log or {}

        if service_id not in health_log:
            health_log[service_id] = []

        health_entry = {
            'timestamp': fields.Datetime.now().isoformat(),
            'status': health_status,
            'data': health_data or {}
        }

        health_log[service_id].append(health_entry)

        # Keep only last 100 health entries per service
        if len(health_log[service_id]) > 100:
            health_log[service_id] = health_log[service_id][-100:]

        self.service_health_log = health_log

    def _update_uptime_percentage(self, service_data):
        """Update uptime percentage for a service"""
        try:
            service_id = service_data['service_id']
            health_log = self.service_health_log or {}

            if service_id not in health_log:
                return

            recent_checks = health_log[service_id][-50:]  # Last 50 checks
            if not recent_checks:
                return

            healthy_checks = len([check for check in recent_checks if check.get('status') == 'healthy'])
            uptime_percentage = (healthy_checks / len(recent_checks)) * 100

            service_data['uptime_percentage'] = round(uptime_percentage, 2)

        except Exception as e:
            _logger.error(f"Failed to update uptime percentage: {str(e)}")

    def _send_registry_event(self, event_type, data):
        """Send registry event to EventBus"""
        try:
            eventbus = self.env['bcm.eventbus.integration'].get_singleton()
            eventbus.send_message(event_type, {
                'registry_id': self.id,
                'timestamp': fields.Datetime.now().isoformat(),
                'data': data
            })

        except Exception as e:
            _logger.error(f"Failed to send registry event: {str(e)}")

    # Action Methods

    def action_discover_services(self):
        """Action to trigger service discovery"""
        self.ensure_one()
        success = self.discover_services()

        if success:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Success"),
                    'message': _("Service discovery completed successfully"),
                    'type': 'success'
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Error"),
                    'message': _("Service discovery failed"),
                    'type': 'danger'
                }
            }

    def action_health_check(self):
        """Action to trigger health checks"""
        self.ensure_one()
        success = self.perform_health_checks()

        if success:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Success"),
                    'message': f"Health check completed. {self.healthy_services}/{self.total_services} services healthy",
                    'type': 'success'
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Error"),
                    'message': _("Health check failed"),
                    'type': 'danger'
                }
            }

    def action_view_services(self):
        """Action to view registered services"""
        self.ensure_one()

        return {
            'name': _('Registered Services'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.service.registry.services.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_registry_id': self.id,
                'services_data': self.registered_services
            }
        }

    def action_view_health_logs(self):
        """Action to view health logs"""
        self.ensure_one()

        return {
            'name': _('Service Health Logs'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.service.registry.health.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_registry_id': self.id,
                'health_data': self.service_health_log
            }
        }

    # Cron Methods

    @api.model
    def cron_discover_services(self):
        """Cron job for service discovery"""
        registry = self.get_singleton()
        if registry.status == 'active' and registry.discovery_enabled:
            registry.discover_services()

    @api.model
    def cron_health_checks(self):
        """Cron job for health checks"""
        registry = self.get_singleton()
        if registry.status == 'active' and registry.health_monitoring:
            registry.perform_health_checks()

    @api.model
    def cron_cleanup_logs(self):
        """Cron job to clean up old logs"""
        registry = self.get_singleton()

        try:
            # Clean discovery logs (keep last 30 days)
            cutoff_date = (fields.Datetime.now() - timedelta(days=30)).isoformat()

            logs = registry.discovery_log or []
            filtered_logs = [
                log for log in logs
                if log.get('timestamp', '') >= cutoff_date
            ]
            registry.discovery_log = filtered_logs

            # Clean health logs (keep last 7 days)
            health_cutoff = (fields.Datetime.now() - timedelta(days=7)).isoformat()

            health_log = registry.service_health_log or {}
            for service_id, service_logs in health_log.items():
                filtered_service_logs = [
                    log for log in service_logs
                    if log.get('timestamp', '') >= health_cutoff
                ]
                health_log[service_id] = filtered_service_logs

            registry.service_health_log = health_log

        except Exception as e:
            _logger.error(f"Log cleanup failed: {str(e)}")

    # API Methods

    @api.model
    def api_register_service(self, service_info):
        """API endpoint for service registration"""
        registry = self.get_singleton()
        return registry.register_service(service_info)

    @api.model
    def api_unregister_service(self, service_id):
        """API endpoint for service unregistration"""
        registry = self.get_singleton()
        return registry.unregister_service(service_id)

    @api.model
    def api_update_health(self, service_id, health_status, health_data=None):
        """API endpoint for health updates"""
        registry = self.get_singleton()
        return registry.update_service_health(service_id, health_status, health_data)

    @api.model
    def api_get_services(self, service_type=None):
        """API endpoint to get services"""
        registry = self.get_singleton()
        if service_type:
            return registry.get_services_by_type(service_type)
        else:
            return registry.registered_services or {}

    @api.model
    def api_get_healthy_services(self):
        """API endpoint to get healthy services only"""
        registry = self.get_singleton()
        return registry.get_healthy_services()