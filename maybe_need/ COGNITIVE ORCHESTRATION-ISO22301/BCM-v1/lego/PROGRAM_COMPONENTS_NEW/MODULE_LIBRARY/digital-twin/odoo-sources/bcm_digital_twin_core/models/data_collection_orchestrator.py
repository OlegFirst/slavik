# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import requests
import json
import logging
from datetime import datetime, timedelta
import threading
import time
import asyncio
import aiohttp
import websockets
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import uuid
from contextlib import asynccontextmanager

_logger = logging.getLogger(__name__)

class DataCollectionOrchestrator(models.Model):
    _name = 'bcm.data.collection.orchestrator'
    _description = 'Digital Twin Data Collection Orchestrator'
    _order = 'create_date desc'

    # Core identification and status
    orchestrator_id = fields.Char(
        string='Orchestrator ID',
        required=True,
        default=lambda self: str(uuid.uuid4()),
        help="Unique identifier for this orchestrator instance"
    )

    name = fields.Char(
        string='Collection Name',
        required=True,
        help="Human-readable name for this collection configuration"
    )

    collection_status = fields.Selection([
        ('idle', 'Idle'),
        ('collecting', 'Collecting Data'),
        ('processing', 'Processing Data'),
        ('error', 'Error State'),
        ('paused', 'Paused'),
        ('stopping', 'Stopping')
    ], string='Collection Status', default='idle', tracking=True)

    # Service endpoint definitions
    service_endpoints = fields.Json(
        string='Service Endpoints',
        help="""JSON configuration for all BCM platform services:
        {
            "bcm_modules": {
                "bcm_core": {"url": "...", "auth": "...", "priority": 1},
                "bcm_training": {"url": "...", "auth": "...", "priority": 2}
            },
            "ai_services": {
                "ai_consultant": {"url": "...", "auth": "...", "priority": 1}
            },
            "integrations": {
                "keycloak": {"url": "...", "auth": "...", "priority": 3}
            }
        }""",
        default=lambda self: self._get_default_service_endpoints()
    )

    # Collection scheduling and timing
    collection_schedule = fields.Json(
        string='Collection Schedule',
        help="""JSON schedule configuration:
        {
            "real_time_services": ["bcm_core", "bcm_incident"],
            "intervals": {
                "high_priority": 10,    // seconds
                "medium_priority": 60,  // seconds
                "low_priority": 300     // seconds
            },
            "batch_collections": {
                "hourly": ["bcm_reporting", "bcm_kpi"],
                "daily": ["bcm_governance", "bcm_audit"]
            }
        }""",
        default=lambda self: self._get_default_collection_schedule()
    )

    # Active collection tracking
    active_collections = fields.Json(
        string='Active Collections',
        help="Currently running collection processes and their status",
        default=dict
    )

    # Timing and performance
    last_full_sync = fields.Datetime(
        string='Last Full Sync',
        help="Timestamp of the last complete data collection cycle"
    )

    last_partial_sync = fields.Datetime(
        string='Last Partial Sync',
        help="Timestamp of the last partial/incremental sync"
    )

    next_scheduled_sync = fields.Datetime(
        string='Next Scheduled Sync',
        compute='_compute_next_sync',
        store=True
    )

    # Error handling and logging
    error_log = fields.Text(
        string='Error Log',
        help="Detailed error messages and stack traces"
    )

    error_count = fields.Integer(
        string='Error Count',
        default=0,
        help="Number of errors encountered in current session"
    )

    max_retry_attempts = fields.Integer(
        string='Max Retry Attempts',
        default=3,
        help="Maximum number of retry attempts for failed collections"
    )

    # Performance metrics and statistics
    performance_metrics = fields.Json(
        string='Performance Metrics',
        help="""Collection performance statistics:
        {
            "total_collections": 0,
            "successful_collections": 0,
            "failed_collections": 0,
            "average_collection_time": 0.0,
            "data_volume_processed": 0,
            "services_response_times": {},
            "throughput_metrics": {}
        }""",
        default=lambda self: self._get_default_performance_metrics()
    )

    # Configuration options
    enable_real_time = fields.Boolean(
        string='Enable Real-time Collection',
        default=True,
        help="Enable WebSocket connections for real-time updates"
    )

    enable_parallel_collection = fields.Boolean(
        string='Enable Parallel Collection',
        default=True,
        help="Allow parallel collection from multiple services"
    )

    max_concurrent_collections = fields.Integer(
        string='Max Concurrent Collections',
        default=10,
        help="Maximum number of simultaneous collection processes"
    )

    rate_limit_requests_per_second = fields.Float(
        string='Rate Limit (req/sec)',
        default=10.0,
        help="Maximum requests per second to avoid overwhelming services"
    )

    collection_timeout = fields.Integer(
        string='Collection Timeout (seconds)',
        default=30,
        help="Timeout for individual service collection requests"
    )

    # WebSocket and real-time configuration
    websocket_endpoints = fields.Json(
        string='WebSocket Endpoints',
        help="WebSocket connection configurations for real-time updates",
        default=dict
    )

    # Data processing configuration
    data_validation_rules = fields.Json(
        string='Data Validation Rules',
        help="Rules for validating collected data before processing",
        default=lambda self: self._get_default_validation_rules()
    )

    @api.depends('collection_schedule')
    def _compute_next_sync(self):
        """Compute next scheduled synchronization time"""
        for record in self:
            if record.collection_schedule:
                # Calculate based on schedule configuration
                now = datetime.now()
                schedule = record.collection_schedule or {}
                intervals = schedule.get('intervals', {})
                min_interval = min(intervals.values()) if intervals.values() else 60
                record.next_scheduled_sync = now + timedelta(seconds=min_interval)
            else:
                record.next_scheduled_sync = False

    def _get_default_service_endpoints(self):
        """Generate default service endpoint configuration"""
        return {
            "bcm_modules": {
                "bcm_core": {
                    "url": "/web/dataset/call_kw/bcm.core/search_read",
                    "auth_type": "session",
                    "priority": 1,
                    "data_types": ["incidents", "plans", "processes"],
                    "collection_method": "api"
                },
                "bcm_training": {
                    "url": "/web/dataset/call_kw/bcm.training/search_read",
                    "auth_type": "session",
                    "priority": 2,
                    "data_types": ["courses", "progress", "certificates"],
                    "collection_method": "api"
                },
                "bcm_bia": {
                    "url": "/web/dataset/call_kw/bcm.bia/search_read",
                    "auth_type": "session",
                    "priority": 1,
                    "data_types": ["assessments", "impacts", "dependencies"],
                    "collection_method": "api"
                },
                "bcm_incident": {
                    "url": "/web/dataset/call_kw/bcm.incident/search_read",
                    "auth_type": "session",
                    "priority": 1,
                    "data_types": ["incidents", "responses", "timelines"],
                    "collection_method": "realtime"
                },
                "bcm_risk_management": {
                    "url": "/web/dataset/call_kw/bcm.risk/search_read",
                    "auth_type": "session",
                    "priority": 2,
                    "data_types": ["risks", "assessments", "mitigations"],
                    "collection_method": "api"
                }
            },
            "ai_services": {
                "ai_consultant": {
                    "url": "http://localhost:8001/api/v1/consultant/status",
                    "auth_type": "bearer",
                    "priority": 1,
                    "data_types": ["recommendations", "analysis", "insights"],
                    "collection_method": "websocket"
                },
                "ai_organs": {
                    "url": "http://localhost:8002/api/v1/organs/metrics",
                    "auth_type": "bearer",
                    "priority": 1,
                    "data_types": ["organ_status", "ai_metrics", "performance"],
                    "collection_method": "api"
                }
            },
            "integrations": {
                "keycloak": {
                    "url": "http://localhost:8080/auth/admin/realms/bcm/users",
                    "auth_type": "oauth2",
                    "priority": 3,
                    "data_types": ["users", "sessions", "permissions"],
                    "collection_method": "api"
                },
                "rabbitmq": {
                    "url": "http://localhost:15672/api/queues",
                    "auth_type": "basic",
                    "priority": 2,
                    "data_types": ["queue_status", "messages", "connections"],
                    "collection_method": "api"
                },
                "redis": {
                    "url": "http://localhost:6379",
                    "auth_type": "none",
                    "priority": 2,
                    "data_types": ["cache_metrics", "key_stats"],
                    "collection_method": "direct"
                },
                "grafana": {
                    "url": "http://localhost:3000/api/datasources",
                    "auth_type": "api_key",
                    "priority": 3,
                    "data_types": ["dashboards", "metrics", "alerts"],
                    "collection_method": "api"
                }
            },
            "adapters": {
                "bpmn_engine": {
                    "url": "http://localhost:8090/engine-rest/process-definition",
                    "auth_type": "basic",
                    "priority": 2,
                    "data_types": ["processes", "instances", "tasks"],
                    "collection_method": "api"
                },
                "lms_adapter": {
                    "url": "http://localhost:8091/api/v1/courses",
                    "auth_type": "bearer",
                    "priority": 3,
                    "data_types": ["courses", "enrollments", "progress"],
                    "collection_method": "api"
                },
                "thehive_adapter": {
                    "url": "http://localhost:9000/api/case",
                    "auth_type": "api_key",
                    "priority": 2,
                    "data_types": ["cases", "observables", "tasks"],
                    "collection_method": "api"
                }
            }
        }

    def _get_default_collection_schedule(self):
        """Generate default collection schedule"""
        return {
            "real_time_services": [
                "bcm_incident", "bcm_core", "ai_consultant"
            ],
            "intervals": {
                "critical": 5,      # 5 seconds for critical services
                "high": 30,         # 30 seconds for high priority
                "medium": 300,      # 5 minutes for medium priority
                "low": 1800         # 30 minutes for low priority
            },
            "batch_collections": {
                "every_minute": ["bcm_incident", "ai_organs"],
                "every_5_minutes": ["bcm_core", "bcm_bia"],
                "every_15_minutes": ["bcm_training", "bcm_risk_management"],
                "hourly": ["bcm_reporting", "bcm_kpi", "grafana"],
                "daily": ["bcm_governance", "bcm_audit", "keycloak"]
            },
            "priority_mapping": {
                "bcm_incident": "critical",
                "bcm_core": "high",
                "ai_consultant": "high",
                "ai_organs": "high",
                "bcm_bia": "medium",
                "bcm_training": "medium",
                "keycloak": "low",
                "grafana": "low"
            }
        }

    def _get_default_performance_metrics(self):
        """Generate default performance metrics structure"""
        return {
            "total_collections": 0,
            "successful_collections": 0,
            "failed_collections": 0,
            "average_collection_time": 0.0,
            "data_volume_processed": 0,
            "services_response_times": {},
            "throughput_metrics": {
                "collections_per_minute": 0,
                "data_points_per_second": 0
            },
            "error_rates": {},
            "last_updated": fields.Datetime.now().isoformat()
        }

    def _get_default_validation_rules(self):
        """Generate default data validation rules"""
        return {
            "required_fields": {
                "bcm_incident": ["id", "name", "status", "created_date"],
                "bcm_core": ["id", "name", "state"],
                "ai_services": ["service_id", "status", "timestamp"]
            },
            "data_types": {
                "timestamp_fields": ["created_date", "updated_date", "timestamp"],
                "numeric_fields": ["id", "priority", "severity"],
                "string_fields": ["name", "description", "status"]
            },
            "validation_rules": {
                "max_age_hours": 24,  # Reject data older than 24 hours
                "min_required_fields": 0.8,  # 80% of required fields must be present
                "max_payload_size_mb": 50  # Maximum payload size in MB
            }
        }

    # ========================================
    # SERVICE REGISTRATION AND MANAGEMENT
    # ========================================

    def register_service_endpoint(self, service_name, endpoint_config):
        """
        Register a new service endpoint for data collection

        Args:
            service_name (str): Unique name for the service
            endpoint_config (dict): Service configuration including URL, auth, etc.

        Returns:
            bool: True if registration successful
        """
        self.ensure_one()

        try:
            current_endpoints = self.service_endpoints or {}

            # Determine service category
            category = self._determine_service_category(service_name)

            if category not in current_endpoints:
                current_endpoints[category] = {}

            # Validate endpoint configuration
            self._validate_endpoint_config(endpoint_config)

            # Add timestamp and validation
            endpoint_config.update({
                'registered_date': fields.Datetime.now().isoformat(),
                'status': 'active',
                'last_health_check': None
            })

            current_endpoints[category][service_name] = endpoint_config
            self.service_endpoints = current_endpoints

            _logger.info(f"Registered service endpoint: {service_name}")
            return True

        except Exception as e:
            _logger.error(f"Failed to register service {service_name}: {str(e)}")
            self._log_error(f"Service registration failed: {service_name} - {str(e)}")
            return False

    def _determine_service_category(self, service_name):
        """Determine which category a service belongs to"""
        if service_name.startswith('bcm_'):
            return 'bcm_modules'
        elif 'ai' in service_name.lower():
            return 'ai_services'
        elif service_name in ['keycloak', 'rabbitmq', 'redis', 'grafana']:
            return 'integrations'
        else:
            return 'adapters'

    def _validate_endpoint_config(self, config):
        """Validate endpoint configuration"""
        required_fields = ['url', 'auth_type', 'priority', 'data_types', 'collection_method']

        for field in required_fields:
            if field not in config:
                raise ValidationError(f"Missing required field in endpoint config: {field}")

        if config['priority'] not in [1, 2, 3]:
            raise ValidationError("Priority must be 1 (high), 2 (medium), or 3 (low)")

        if config['collection_method'] not in ['api', 'websocket', 'realtime', 'direct']:
            raise ValidationError("Invalid collection method")

    # ========================================
    # COLLECTION ORCHESTRATION
    # ========================================

    def start_real_time_collection(self):
        """
        Start continuous real-time data collection from all configured services
        """
        self.ensure_one()

        if self.collection_status == 'collecting':
            raise UserError(_("Collection is already running"))

        try:
            self.collection_status = 'collecting'
            self.active_collections = {}
            self.error_count = 0

            # Initialize performance tracking
            self._reset_performance_metrics()

            # Start collection threads based on schedule
            self._start_scheduled_collections()

            # Start WebSocket connections for real-time services
            if self.enable_real_time:
                self._start_websocket_connections()

            _logger.info(f"Started real-time collection for orchestrator {self.orchestrator_id}")

        except Exception as e:
            self.collection_status = 'error'
            error_msg = f"Failed to start collection: {str(e)}"
            self._log_error(error_msg)
            raise UserError(_(error_msg))

    def _start_scheduled_collections(self):
        """Start scheduled collection processes based on configuration"""
        schedule = self.collection_schedule or {}
        endpoints = self.service_endpoints or {}

        # Start different collection intervals
        for category, services in endpoints.items():
            for service_name, config in services.items():
                priority = schedule.get('priority_mapping', {}).get(service_name, 'medium')
                interval = schedule.get('intervals', {}).get(priority, 300)

                # Create collection thread for this service
                threading.Thread(
                    target=self._collection_worker,
                    args=(service_name, config, interval),
                    daemon=True
                ).start()

    def _collection_worker(self, service_name, config, interval):
        """Worker thread for continuous service collection"""
        while self.collection_status == 'collecting':
            try:
                start_time = time.time()

                # Collect data from service
                data = self.collect_from_service(service_name)

                if data:
                    # Process collected data
                    processed_data = self.process_collected_data(data, service_name)

                    # Update digital twins
                    self.update_digital_twins(processed_data)

                    # Update performance metrics
                    collection_time = time.time() - start_time
                    self._update_performance_metrics(service_name, collection_time, True)

                # Respect rate limiting
                time.sleep(max(interval, 1.0 / self.rate_limit_requests_per_second))

            except Exception as e:
                self._update_performance_metrics(service_name, 0, False)
                self._log_error(f"Collection worker error for {service_name}: {str(e)}")
                time.sleep(interval * 2)  # Back off on error

    def collect_from_service(self, service_name):
        """
        Collect data from a specific service

        Args:
            service_name (str): Name of the service to collect from

        Returns:
            dict: Collected data or None if failed
        """
        try:
            # Find service configuration
            config = self._get_service_config(service_name)
            if not config:
                raise ValueError(f"No configuration found for service: {service_name}")

            # Update active collections
            collection_id = str(uuid.uuid4())
            self._update_active_collection(service_name, collection_id, 'collecting')

            # Collect based on method
            method = config.get('collection_method', 'api')

            if method == 'api':
                data = self._collect_via_api(service_name, config)
            elif method == 'websocket':
                data = self._collect_via_websocket(service_name, config)
            elif method == 'direct':
                data = self._collect_direct(service_name, config)
            else:
                raise ValueError(f"Unsupported collection method: {method}")

            self._update_active_collection(service_name, collection_id, 'completed')
            return data

        except Exception as e:
            self._update_active_collection(service_name, collection_id, 'failed')
            _logger.error(f"Failed to collect from {service_name}: {str(e)}")
            return None

    def _collect_via_api(self, service_name, config):
        """Collect data via REST API"""
        url = config['url']
        auth_config = self._get_auth_config(config)

        # Prepare request
        headers = {'Content-Type': 'application/json'}
        headers.update(auth_config.get('headers', {}))

        # Make request with timeout and retries
        for attempt in range(self.max_retry_attempts):
            try:
                response = requests.get(
                    url,
                    headers=headers,
                    timeout=self.collection_timeout,
                    **auth_config.get('params', {})
                )

                if response.status_code == 200:
                    return {
                        'service': service_name,
                        'timestamp': datetime.now().isoformat(),
                        'data': response.json(),
                        'metadata': {
                            'response_time': response.elapsed.total_seconds(),
                            'status_code': response.status_code
                        }
                    }
                else:
                    _logger.warning(f"API request failed for {service_name}: {response.status_code}")

            except requests.RequestException as e:
                if attempt == self.max_retry_attempts - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff

        return None

    def _collect_via_websocket(self, service_name, config):
        """Collect data via WebSocket connection"""
        # This is a simplified WebSocket implementation
        # In production, you'd want to use asyncio and maintain persistent connections
        try:
            ws_url = config.get('websocket_url', config['url'].replace('http', 'ws'))

            # For now, return cached WebSocket data if available
            ws_data = self.websocket_endpoints.get(service_name, {})

            return {
                'service': service_name,
                'timestamp': datetime.now().isoformat(),
                'data': ws_data,
                'metadata': {
                    'collection_method': 'websocket',
                    'connection_status': 'active'
                }
            }

        except Exception as e:
            _logger.error(f"WebSocket collection failed for {service_name}: {str(e)}")
            return None

    def _collect_direct(self, service_name, config):
        """Collect data via direct database/service connection"""
        # Implementation depends on the specific service
        # This is a placeholder for direct connections (e.g., Redis, database)
        return {
            'service': service_name,
            'timestamp': datetime.now().isoformat(),
            'data': {'status': 'collected_direct'},
            'metadata': {'collection_method': 'direct'}
        }

    def process_collected_data(self, data, source_service):
        """
        Process and validate collected data

        Args:
            data (dict): Raw collected data
            source_service (str): Name of source service

        Returns:
            dict: Processed and validated data
        """
        try:
            # Validate data structure
            if not self._validate_collected_data(data, source_service):
                _logger.warning(f"Data validation failed for {source_service}")
                return None

            # Extract and normalize data
            normalized_data = self._normalize_data(data, source_service)

            # Apply business logic transformations
            processed_data = self._apply_transformations(normalized_data, source_service)

            # Add processing metadata
            processed_data['processing'] = {
                'processed_at': datetime.now().isoformat(),
                'processor_id': self.orchestrator_id,
                'source_service': source_service,
                'validation_passed': True
            }

            return processed_data

        except Exception as e:
            _logger.error(f"Data processing failed for {source_service}: {str(e)}")
            self._log_error(f"Processing error for {source_service}: {str(e)}")
            return None

    def _validate_collected_data(self, data, source_service):
        """Validate collected data against defined rules"""
        rules = self.data_validation_rules or {}

        # Check required fields
        required_fields = rules.get('required_fields', {}).get(source_service, [])
        data_payload = data.get('data', {})

        if required_fields:
            missing_fields = [f for f in required_fields if f not in data_payload]
            if missing_fields:
                _logger.warning(f"Missing required fields for {source_service}: {missing_fields}")
                return False

        # Check data age
        max_age_hours = rules.get('validation_rules', {}).get('max_age_hours', 24)
        timestamp_str = data.get('timestamp')
        if timestamp_str:
            data_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            age_hours = (datetime.now() - data_time).total_seconds() / 3600
            if age_hours > max_age_hours:
                _logger.warning(f"Data too old for {source_service}: {age_hours} hours")
                return False

        return True

    def _normalize_data(self, data, source_service):
        """Normalize data format across different services"""
        normalized = {
            'service_name': source_service,
            'collection_timestamp': data.get('timestamp'),
            'raw_data': data.get('data', {}),
            'metadata': data.get('metadata', {}),
            'normalized_entities': []
        }

        # Service-specific normalization
        raw_data = data.get('data', {})

        if source_service.startswith('bcm_'):
            # Normalize BCM module data
            normalized['normalized_entities'] = self._normalize_bcm_data(raw_data, source_service)
        elif 'ai' in source_service:
            # Normalize AI service data
            normalized['normalized_entities'] = self._normalize_ai_data(raw_data, source_service)
        else:
            # Generic normalization
            normalized['normalized_entities'] = self._normalize_generic_data(raw_data, source_service)

        return normalized

    def _normalize_bcm_data(self, data, service_name):
        """Normalize BCM module specific data"""
        entities = []

        if isinstance(data, list):
            for item in data:
                entity = {
                    'id': item.get('id'),
                    'name': item.get('name', ''),
                    'status': item.get('state', item.get('status')),
                    'created_date': item.get('create_date'),
                    'updated_date': item.get('write_date'),
                    'source_module': service_name,
                    'entity_type': self._determine_entity_type(service_name),
                    'data': item
                }
                entities.append(entity)

        return entities

    def _normalize_ai_data(self, data, service_name):
        """Normalize AI service specific data"""
        entities = []

        # Handle AI service responses
        if isinstance(data, dict):
            entity = {
                'id': data.get('service_id', data.get('id')),
                'name': f"{service_name}_service",
                'status': data.get('status'),
                'metrics': data.get('metrics', {}),
                'recommendations': data.get('recommendations', []),
                'source_service': service_name,
                'entity_type': 'ai_service',
                'data': data
            }
            entities.append(entity)

        return entities

    def _normalize_generic_data(self, data, service_name):
        """Generic data normalization for other services"""
        entities = []

        if isinstance(data, dict):
            entity = {
                'id': data.get('id', str(uuid.uuid4())),
                'name': f"{service_name}_data",
                'status': data.get('status', 'active'),
                'source_service': service_name,
                'entity_type': 'generic',
                'data': data
            }
            entities.append(entity)

        return entities

    def update_digital_twins(self, processed_data):
        """
        Update digital twins with processed data

        Args:
            processed_data (dict): Processed data ready for twin updates
        """
        try:
            if not processed_data:
                return

            # Get digital twin models
            digital_twin_org = self.env['bcm.digital.twin.organization']

            # Process each normalized entity
            entities = processed_data.get('normalized_entities', [])

            for entity in entities:
                entity_type = entity.get('entity_type')
                source_service = entity.get('source_service', processed_data.get('service_name'))

                # Route to appropriate update method
                if entity_type == 'ai_service':
                    self._update_ai_service_twin(entity, source_service)
                elif source_service.startswith('bcm_'):
                    self._update_bcm_module_twin(entity, source_service)
                else:
                    self._update_generic_twin(entity, source_service)

            # Update last sync timestamp
            self.last_partial_sync = fields.Datetime.now()

            _logger.info(f"Updated digital twins with {len(entities)} entities from {processed_data.get('service_name')}")

        except Exception as e:
            _logger.error(f"Failed to update digital twins: {str(e)}")
            self._log_error(f"Twin update error: {str(e)}")

    def _update_ai_service_twin(self, entity, source_service):
        """Update AI service digital twin"""
        # Implementation would depend on your digital twin structure
        # This is a placeholder for AI service twin updates
        pass

    def _update_bcm_module_twin(self, entity, source_service):
        """Update BCM module digital twin"""
        # Implementation would depend on your digital twin structure
        # This is a placeholder for BCM module twin updates
        pass

    def _update_generic_twin(self, entity, source_service):
        """Update generic service digital twin"""
        # Implementation would depend on your digital twin structure
        # This is a placeholder for generic twin updates
        pass

    # ========================================
    # WEBSOCKET AND REAL-TIME FEATURES
    # ========================================

    def _start_websocket_connections(self):
        """Start WebSocket connections for real-time services"""
        schedule = self.collection_schedule or {}
        real_time_services = schedule.get('real_time_services', [])

        for service_name in real_time_services:
            config = self._get_service_config(service_name)
            if config and config.get('collection_method') == 'websocket':
                threading.Thread(
                    target=self._maintain_websocket_connection,
                    args=(service_name, config),
                    daemon=True
                ).start()

    def _maintain_websocket_connection(self, service_name, config):
        """Maintain persistent WebSocket connection for a service"""
        # This is a simplified implementation
        # In production, you'd want to use asyncio and proper WebSocket libraries
        while self.collection_status == 'collecting':
            try:
                # Simulate WebSocket connection and data reception
                # In reality, you'd establish actual WebSocket connections here
                time.sleep(10)  # Simulate periodic WebSocket messages

                # Update WebSocket endpoints with received data
                current_ws_data = self.websocket_endpoints or {}
                current_ws_data[service_name] = {
                    'last_message': datetime.now().isoformat(),
                    'connection_status': 'active',
                    'message_count': current_ws_data.get(service_name, {}).get('message_count', 0) + 1
                }
                self.websocket_endpoints = current_ws_data

            except Exception as e:
                _logger.error(f"WebSocket connection error for {service_name}: {str(e)}")
                time.sleep(30)  # Retry after delay

    # ========================================
    # UTILITY AND HELPER METHODS
    # ========================================

    def _get_service_config(self, service_name):
        """Get configuration for a specific service"""
        endpoints = self.service_endpoints or {}

        for category, services in endpoints.items():
            if service_name in services:
                return services[service_name]

        return None

    def _get_auth_config(self, config):
        """Get authentication configuration for a service"""
        auth_type = config.get('auth_type', 'none')

        if auth_type == 'session':
            return {'headers': {}, 'params': {}}
        elif auth_type == 'bearer':
            return {
                'headers': {'Authorization': 'Bearer YOUR_TOKEN'},
                'params': {}
            }
        elif auth_type == 'basic':
            return {'params': {'auth': ('username', 'password')}}
        elif auth_type == 'api_key':
            return {
                'headers': {'X-API-Key': 'YOUR_API_KEY'},
                'params': {}
            }
        else:
            return {'headers': {}, 'params': {}}

    def _determine_entity_type(self, service_name):
        """Determine entity type from service name"""
        type_mapping = {
            'bcm_incident': 'incident',
            'bcm_core': 'process',
            'bcm_training': 'training',
            'bcm_bia': 'assessment',
            'bcm_risk_management': 'risk'
        }
        return type_mapping.get(service_name, 'generic')

    def _apply_transformations(self, data, source_service):
        """Apply business logic transformations to normalized data"""
        # Add any business-specific transformations here
        return data

    def _update_active_collection(self, service_name, collection_id, status):
        """Update active collections tracking"""
        current_collections = self.active_collections or {}

        if service_name not in current_collections:
            current_collections[service_name] = {}

        current_collections[service_name][collection_id] = {
            'status': status,
            'timestamp': datetime.now().isoformat()
        }

        self.active_collections = current_collections

    def _update_performance_metrics(self, service_name, collection_time, success):
        """Update performance metrics"""
        current_metrics = self.performance_metrics or self._get_default_performance_metrics()

        current_metrics['total_collections'] += 1

        if success:
            current_metrics['successful_collections'] += 1

            # Update response times
            if service_name not in current_metrics['services_response_times']:
                current_metrics['services_response_times'][service_name] = []

            current_metrics['services_response_times'][service_name].append(collection_time)

            # Keep only last 100 measurements
            if len(current_metrics['services_response_times'][service_name]) > 100:
                current_metrics['services_response_times'][service_name] = \
                    current_metrics['services_response_times'][service_name][-100:]
        else:
            current_metrics['failed_collections'] += 1

            # Update error rates
            if service_name not in current_metrics['error_rates']:
                current_metrics['error_rates'][service_name] = 0
            current_metrics['error_rates'][service_name] += 1

        # Update average collection time
        if current_metrics['successful_collections'] > 0:
            all_times = []
            for service_times in current_metrics['services_response_times'].values():
                all_times.extend(service_times)
            current_metrics['average_collection_time'] = sum(all_times) / len(all_times)

        current_metrics['last_updated'] = datetime.now().isoformat()
        self.performance_metrics = current_metrics

    def _reset_performance_metrics(self):
        """Reset performance metrics for new collection session"""
        self.performance_metrics = self._get_default_performance_metrics()

    def _log_error(self, error_message):
        """Log error to error_log field"""
        timestamp = datetime.now().isoformat()
        error_entry = f"[{timestamp}] {error_message}\n"

        current_log = self.error_log or ""
        self.error_log = error_entry + current_log
        self.error_count += 1

    # ========================================
    # CONTROL METHODS
    # ========================================

    def stop_collection(self):
        """Stop data collection"""
        self.ensure_one()
        self.collection_status = 'stopping'

        # Clear active collections
        self.active_collections = {}

        # Set status to idle
        self.collection_status = 'idle'

        _logger.info(f"Stopped data collection for orchestrator {self.orchestrator_id}")

    def pause_collection(self):
        """Pause data collection"""
        self.ensure_one()
        if self.collection_status == 'collecting':
            self.collection_status = 'paused'
            _logger.info(f"Paused data collection for orchestrator {self.orchestrator_id}")

    def resume_collection(self):
        """Resume paused data collection"""
        self.ensure_one()
        if self.collection_status == 'paused':
            self.collection_status = 'collecting'
            _logger.info(f"Resumed data collection for orchestrator {self.orchestrator_id}")

    def force_full_sync(self):
        """Force a full synchronization of all services"""
        self.ensure_one()

        try:
            self.collection_status = 'collecting'

            # Collect from all configured services
            endpoints = self.service_endpoints or {}
            total_collected = 0

            for category, services in endpoints.items():
                for service_name, config in services.items():
                    data = self.collect_from_service(service_name)
                    if data:
                        processed_data = self.process_collected_data(data, service_name)
                        if processed_data:
                            self.update_digital_twins(processed_data)
                            total_collected += 1

            self.last_full_sync = fields.Datetime.now()
            self.collection_status = 'idle'

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Full sync completed. Collected data from %d services.') % total_collected,
                    'type': 'success',
                }
            }

        except Exception as e:
            self.collection_status = 'error'
            error_msg = f"Full sync failed: {str(e)}"
            self._log_error(error_msg)
            raise UserError(_(error_msg))

    def health_check_all_services(self):
        """Perform health check on all configured services"""
        self.ensure_one()

        endpoints = self.service_endpoints or {}
        health_results = {}

        for category, services in endpoints.items():
            health_results[category] = {}
            for service_name, config in services.items():
                try:
                    # Simple health check - attempt to reach the service
                    url = config['url']
                    response = requests.get(url, timeout=5)
                    health_results[category][service_name] = {
                        'status': 'healthy' if response.status_code < 400 else 'unhealthy',
                        'response_code': response.status_code,
                        'response_time': response.elapsed.total_seconds()
                    }
                except Exception as e:
                    health_results[category][service_name] = {
                        'status': 'error',
                        'error': str(e)
                    }

        return health_results

    @api.model
    def get_collection_statistics(self):
        """Get overall collection statistics across all orchestrators"""
        orchestrators = self.search([])

        stats = {
            'total_orchestrators': len(orchestrators),
            'active_orchestrators': len(orchestrators.filtered(lambda r: r.collection_status == 'collecting')),
            'total_services_configured': 0,
            'total_collections_today': 0,
            'average_response_time': 0.0
        }

        for orchestrator in orchestrators:
            endpoints = orchestrator.service_endpoints or {}
            for category, services in endpoints.items():
                stats['total_services_configured'] += len(services)

            metrics = orchestrator.performance_metrics or {}
            stats['total_collections_today'] += metrics.get('total_collections', 0)

        return stats