# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import requests
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class BCMMicroservicesBridge(models.Model):
    """Universal Bridge between Odoo BCM Modules and Platform Microservices

    This bridge enables seamless communication between:
    - BCM Living Organism (Odoo modules)
    - External Platform Services (AI Cluster, Document Services, etc.)

    Key Features:
    - Service Discovery and Health Monitoring
    - Event Routing (Odoo ↔ Microservices)
    - API Versioning and Compatibility
    - Gradual Migration Support (Microservice → Odoo Module)
    """

    _name = 'bcm.microservices.bridge'
    _description = 'Bridge between Odoo and Platform Microservices'
    _rec_name = 'bridge_name'

    # Bridge Configuration
    bridge_name = fields.Char('Bridge Name', default='BCM Platform Bridge', required=True)
    bridge_status = fields.Selection([
        ('active', 'Active'),
        ('maintenance', 'Maintenance'),
        ('error', 'Error'),
        ('disabled', 'Disabled')
    ], default='active', string='Bridge Status')

    # Service Discovery
    discovered_services = fields.Json('Discovered Services', default=dict)
    last_discovery_scan = fields.Datetime('Last Discovery Scan')
    auto_discovery_enabled = fields.Boolean('Auto Discovery', default=True)

    # Statistics
    total_requests_sent = fields.Integer('Total Requests Sent', default=0)
    total_requests_received = fields.Integer('Total Requests Received', default=0)
    failed_requests_count = fields.Integer('Failed Requests', default=0)
    last_request_timestamp = fields.Datetime('Last Request')

    # Health Monitoring
    health_check_interval = fields.Integer('Health Check Interval (minutes)', default=5)
    unhealthy_services = fields.Json('Unhealthy Services', default=dict)

    @api.model
    def get_default_bridge(self):
        """Get or create default bridge instance"""
        bridge = self.search([('bridge_name', '=', 'BCM Platform Bridge')], limit=1)
        if not bridge:
            bridge = self.create({
                'bridge_name': 'BCM Platform Bridge',
                'bridge_status': 'active'
            })
        return bridge

    @api.model
    def discover_platform_services(self):
        """Auto-discover all platform microservices

        Scans known ports and endpoints to find running services
        """
        try:
            bridge = self.get_default_bridge()

            # Platform services configuration
            service_discovery_config = {
                'ai_cluster': {
                    'endpoints': [
                        'http://ai-orchestrator:8000',
                        'http://ai-consultant:8001',
                        'http://ai-analytics:8002',
                        'http://localhost:8000',  # Local development
                        'http://localhost:8001',
                        'http://localhost:8002'
                    ],
                    'health_path': '/health',
                    'capabilities': ['ai_orchestration', 'ai_consultation', 'ai_analytics']
                },
                'document_services': {
                    'endpoints': [
                        'http://document-processor:8010',
                        'http://document-storage:8011',
                        'http://document-search:8012',
                        'http://localhost:8010',
                        'http://localhost:8011',
                        'http://localhost:8012'
                    ],
                    'health_path': '/health',
                    'capabilities': ['document_processing', 'document_storage', 'document_search']
                },
                'integration_hub': {
                    'endpoints': [
                        'http://integration-hub:8020',
                        'http://thehive-adapter:8021',
                        'http://moodle-adapter:8022',
                        'http://localhost:8020',
                        'http://localhost:8021',
                        'http://localhost:8022'
                    ],
                    'health_path': '/health',
                    'capabilities': ['external_integrations', 'security_tools', 'lms_integration']
                },
                'notification_center': {
                    'endpoints': [
                        'http://notification-center:8030',
                        'http://localhost:8030'
                    ],
                    'health_path': '/health',
                    'capabilities': ['email_notifications', 'slack_notifications', 'webhooks']
                }
            }

            discovered = {}

            for service_name, config in service_discovery_config.items():
                discovered[service_name] = []

                for endpoint in config['endpoints']:
                    try:
                        # Test service availability
                        response = requests.get(
                            f"{endpoint}{config['health_path']}",
                            timeout=3
                        )

                        if response.status_code == 200:
                            service_info = {
                                'endpoint': endpoint,
                                'status': 'healthy',
                                'capabilities': config['capabilities'],
                                'last_checked': fields.Datetime.now().isoformat(),
                                'response_time': response.elapsed.total_seconds()
                            }

                            # Try to get service metadata
                            try:
                                metadata_response = requests.get(f"{endpoint}/metadata", timeout=2)
                                if metadata_response.status_code == 200:
                                    service_info['metadata'] = metadata_response.json()
                            except:
                                pass

                            discovered[service_name].append(service_info)
                            _logger.info(f'Discovered service: {service_name} at {endpoint}')

                    except requests.exceptions.RequestException as e:
                        _logger.debug(f'Service not available: {endpoint} - {e}')
                        continue

            # Update bridge with discovered services
            bridge.write({
                'discovered_services': discovered,
                'last_discovery_scan': fields.Datetime.now()
            })

            return discovered

        except Exception as e:
            _logger.error(f'Service discovery failed: {e}')
            return {}

    def call_microservice(self, service_type, endpoint, data, method='POST', timeout=10):
        """Universal method to call any platform microservice

        Args:
            service_type: 'ai_cluster', 'document_services', 'integration_hub', etc.
            endpoint: API endpoint path (e.g., '/process-document')
            data: Request payload
            method: HTTP method (GET, POST, PUT, DELETE)
            timeout: Request timeout in seconds
        """
        try:
            bridge = self.get_default_bridge()

            # Get available services for this type
            discovered_services = bridge.discovered_services or {}
            services = discovered_services.get(service_type, [])

            if not services:
                # Try to rediscover services
                _logger.info(f'No services found for {service_type}, attempting rediscovery')
                self.discover_platform_services()
                discovered_services = bridge.discovered_services or {}
                services = discovered_services.get(service_type, [])

                if not services:
                    raise UserError(f'No healthy services available for {service_type}')

            # Select best available service (first healthy one for now)
            selected_service = None
            for service in services:
                if service.get('status') == 'healthy':
                    selected_service = service
                    break

            if not selected_service:
                raise UserError(f'No healthy services available for {service_type}')

            # Make the request
            service_url = selected_service['endpoint']
            full_url = f"{service_url}{endpoint}"

            headers = {
                'Content-Type': 'application/json',
                'X-BCM-Source': 'odoo-bridge',
                'X-BCM-Company': str(self.env.company.id),
                'X-BCM-User': str(self.env.user.id)
            }

            start_time = datetime.now()

            if method.upper() == 'GET':
                response = requests.get(full_url, params=data, headers=headers, timeout=timeout)
            elif method.upper() == 'POST':
                response = requests.post(full_url, json=data, headers=headers, timeout=timeout)
            elif method.upper() == 'PUT':
                response = requests.put(full_url, json=data, headers=headers, timeout=timeout)
            elif method.upper() == 'DELETE':
                response = requests.delete(full_url, json=data, headers=headers, timeout=timeout)
            else:
                raise ValidationError(f'Unsupported HTTP method: {method}')

            response_time = (datetime.now() - start_time).total_seconds()

            # Update statistics
            bridge.write({
                'total_requests_sent': bridge.total_requests_sent + 1,
                'last_request_timestamp': fields.Datetime.now()
            })

            # Log successful request
            _logger.info(f'Microservice call successful: {service_type}{endpoint} '
                        f'({response.status_code}, {response_time:.2f}s)')

            if response.status_code >= 200 and response.status_code < 300:
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'data': response.json() if response.content else {},
                    'response_time': response_time,
                    'service_endpoint': service_url
                }
            else:
                # Handle error response
                bridge.write({'failed_requests_count': bridge.failed_requests_count + 1})
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': response.text,
                    'service_endpoint': service_url
                }

        except requests.exceptions.Timeout:
            bridge.write({'failed_requests_count': bridge.failed_requests_count + 1})
            raise UserError(f'Request timeout: {service_type}{endpoint}')

        except requests.exceptions.RequestException as e:
            bridge.write({'failed_requests_count': bridge.failed_requests_count + 1})
            raise UserError(f'Request failed: {str(e)}')

        except Exception as e:
            bridge.write({'failed_requests_count': bridge.failed_requests_count + 1})
            _logger.error(f'Microservice call failed: {e}')
            raise UserError(f'Microservice call failed: {str(e)}')

    @api.model
    def route_event_to_microservices(self, event_type, event_data, target_services=None):
        """Route BCM Event Bus events to external microservices

        This extends the organism's nervous system to external services
        """
        try:
            bridge = self.get_default_bridge()

            # Define event routing rules
            event_routing_map = {
                'document_uploaded': ['document_services'],
                'risk_identified': ['ai_cluster', 'notification_center'],
                'incident_created': ['integration_hub', 'notification_center'],
                'audit_finding_created': ['ai_cluster', 'document_services'],
                'training_completed': ['integration_hub'],
                'governance_policy_changed': ['ai_cluster', 'document_services', 'notification_center']
            }

            # Determine target services
            if target_services is None:
                target_services = event_routing_map.get(event_type, [])

            if not target_services:
                _logger.info(f'No external services configured for event: {event_type}')
                return {'routed_count': 0}

            routed_count = 0
            results = {}

            for service_type in target_services:
                try:
                    # Route event to service
                    result = self.call_microservice(
                        service_type=service_type,
                        endpoint='/events/bcm',
                        data={
                            'event_type': event_type,
                            'event_data': event_data,
                            'source': 'bcm_organism',
                            'timestamp': fields.Datetime.now().isoformat(),
                            'company_id': self.env.company.id
                        },
                        method='POST'
                    )

                    if result.get('success'):
                        routed_count += 1
                        results[service_type] = 'success'
                        _logger.info(f'Event {event_type} routed to {service_type}')
                    else:
                        results[service_type] = f"error: {result.get('error', 'unknown')}"
                        _logger.warning(f'Failed to route event {event_type} to {service_type}')

                except Exception as e:
                    results[service_type] = f'exception: {str(e)}'
                    _logger.error(f'Exception routing event {event_type} to {service_type}: {e}')

            return {
                'routed_count': routed_count,
                'total_targets': len(target_services),
                'results': results
            }

        except Exception as e:
            _logger.error(f'Event routing failed: {e}')
            return {'routed_count': 0, 'error': str(e)}

    @api.model
    def handle_microservice_event(self, service_name, event_data):
        """Handle events received from external microservices

        Convert microservice events into BCM Event Bus events
        """
        try:
            # Get BCM Event Bus
            event_bus = self.env['bcm.event.bus']

            # Convert microservice event to BCM organism event
            organism_event_type = f"microservice_{event_data.get('event_type', 'unknown')}"
            organism_event_data = {
                'source_service': service_name,
                'original_event': event_data,
                'received_at': fields.Datetime.now().isoformat(),
                'converted_by': 'microservices_bridge'
            }

            # Publish to organism
            success = event_bus.publish_event(
                event_type=organism_event_type,
                source_module='bcm_microservices_bridge',
                event_data=organism_event_data,
                priority='normal'
            )

            if success:
                _logger.info(f'Microservice event converted: {service_name} → BCM organism')
                return True
            else:
                _logger.warning(f'Failed to convert microservice event: {service_name}')
                return False

        except Exception as e:
            _logger.error(f'Microservice event handling failed: {e}')
            return False

    def action_test_service_connectivity(self):
        """Test connectivity to all discovered services"""
        try:
            # Rediscover services
            discovered = self.discover_platform_services()

            if not discovered:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Service Discovery'),
                        'message': 'No platform services discovered',
                        'type': 'warning',
                    }
                }

            # Count healthy services
            total_services = 0
            healthy_services = 0

            for service_type, services in discovered.items():
                for service in services:
                    total_services += 1
                    if service.get('status') == 'healthy':
                        healthy_services += 1

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Platform Connectivity Test'),
                    'message': f'Found {healthy_services}/{total_services} healthy services',
                    'type': 'success' if healthy_services > 0 else 'warning',
                }
            }

        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connectivity Test Failed'),
                    'message': f'Error: {str(e)}',
                    'type': 'danger',
                }
            }

    def action_test_ai_cluster_call(self):
        """Test AI Cluster connectivity and functionality"""
        try:
            # Test AI orchestration
            result = self.call_microservice(
                service_type='ai_cluster',
                endpoint='/orchestrate',
                data={
                    'workflow_type': 'test_connectivity',
                    'data': {'test': True, 'timestamp': fields.Datetime.now().isoformat()}
                }
            )

            if result.get('success'):
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('AI Cluster Test'),
                        'message': f'AI Cluster connectivity successful (response time: {result.get("response_time", 0):.2f}s)',
                        'type': 'success',
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('AI Cluster Test Failed'),
                        'message': f'Error: {result.get("error", "Unknown error")}',
                        'type': 'danger',
                    }
                }

        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('AI Cluster Test Error'),
                    'message': f'Exception: {str(e)}',
                    'type': 'danger',
                }
            }

    @api.model
    def get_bridge_health_status(self):
        """Get comprehensive health status of the bridge and connected services"""
        try:
            bridge = self.get_default_bridge()
            discovered_services = bridge.discovered_services or {}

            service_health = {}
            total_services = 0
            healthy_services = 0

            for service_type, services in discovered_services.items():
                service_health[service_type] = {
                    'total': len(services),
                    'healthy': 0,
                    'services': []
                }

                for service in services:
                    total_services += 1
                    status = service.get('status', 'unknown')
                    if status == 'healthy':
                        healthy_services += 1
                        service_health[service_type]['healthy'] += 1

                    service_health[service_type]['services'].append({
                        'endpoint': service.get('endpoint'),
                        'status': status,
                        'response_time': service.get('response_time', 0)
                    })

            bridge_health = 'healthy'
            if healthy_services == 0:
                bridge_health = 'critical'
            elif healthy_services < total_services * 0.5:
                bridge_health = 'warning'

            return {
                'bridge_status': bridge_health,
                'total_services': total_services,
                'healthy_services': healthy_services,
                'service_details': service_health,
                'last_discovery': bridge.last_discovery_scan.isoformat() if bridge.last_discovery_scan else None,
                'statistics': {
                    'total_requests_sent': bridge.total_requests_sent,
                    'total_requests_received': bridge.total_requests_received,
                    'failed_requests': bridge.failed_requests_count,
                    'success_rate': ((bridge.total_requests_sent - bridge.failed_requests_count) /
                                   max(bridge.total_requests_sent, 1)) * 100
                }
            }

        except Exception as e:
            return {
                'bridge_status': 'error',
                'error': str(e)
            }