# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import json

class CollectionSetupWizard(models.TransientModel):
    _name = 'bcm.collection.setup.wizard'
    _description = 'Data Collection Setup Wizard'

    orchestrator_id = fields.Many2one(
        'bcm.data.collection.orchestrator',
        string='Orchestrator',
        required=True
    )

    setup_type = fields.Selection([
        ('quick_start', 'Quick Start (Default Configuration)'),
        ('custom', 'Custom Configuration'),
        ('import_config', 'Import Configuration')
    ], string='Setup Type', required=True, default='quick_start')

    # Quick Start Options
    enable_bcm_modules = fields.Boolean(
        string='Enable BCM Modules Collection',
        default=True,
        help="Automatically collect data from all BCM modules"
    )

    enable_ai_services = fields.Boolean(
        string='Enable AI Services Collection',
        default=True,
        help="Collect data from AI services and intelligent components"
    )

    enable_integrations = fields.Boolean(
        string='Enable Integrations Collection',
        default=True,
        help="Collect data from external integrations (Keycloak, RabbitMQ, etc.)"
    )

    enable_adapters = fields.Boolean(
        string='Enable Adapters Collection',
        default=False,
        help="Collect data from external adapters (BPMN, LMS, TheHive, etc.)"
    )

    # Collection Frequency
    collection_frequency = fields.Selection([
        ('realtime', 'Real-time (WebSocket + Events)'),
        ('high', 'High Frequency (Every 30 seconds)'),
        ('medium', 'Medium Frequency (Every 5 minutes)'),
        ('low', 'Low Frequency (Every 30 minutes)')
    ], string='Default Collection Frequency', default='medium')

    # Performance Settings
    max_concurrent = fields.Integer(
        string='Max Concurrent Collections',
        default=10,
        help="Maximum number of simultaneous collection processes"
    )

    rate_limit = fields.Float(
        string='Rate Limit (requests/second)',
        default=10.0,
        help="Maximum requests per second to avoid overwhelming services"
    )

    # Custom Configuration
    custom_services = fields.Text(
        string='Custom Services Configuration',
        help="JSON configuration for custom services",
        placeholder="""Example:
{
    "custom_service": {
        "url": "http://localhost:8080/api/data",
        "auth_type": "bearer",
        "priority": 2,
        "data_types": ["metrics", "logs"],
        "collection_method": "api"
    }
}"""
    )

    # Import Configuration
    config_file = fields.Binary(
        string='Configuration File',
        help="Upload a JSON configuration file"
    )

    config_filename = fields.Char(string='Filename')

    # Auto-discovery
    auto_discover_services = fields.Boolean(
        string='Auto-discover BCM Services',
        default=True,
        help="Automatically discover available BCM services in the system"
    )

    discovered_services = fields.Text(
        string='Discovered Services',
        readonly=True,
        help="Services found during auto-discovery"
    )

    # Validation and Testing
    validate_config = fields.Boolean(
        string='Validate Configuration',
        default=True,
        help="Validate service endpoints before applying configuration"
    )

    test_connections = fields.Boolean(
        string='Test All Connections',
        default=True,
        help="Test connections to all configured services"
    )

    setup_status = fields.Text(
        string='Setup Status',
        readonly=True,
        help="Status messages during setup process"
    )

    @api.onchange('setup_type')
    def _onchange_setup_type(self):
        """Update visibility based on setup type"""
        if self.setup_type == 'quick_start':
            self.auto_discover_services = True
        elif self.setup_type == 'import_config':
            self.validate_config = True
            self.test_connections = True

    def action_discover_services(self):
        """Auto-discover available BCM services"""
        self.ensure_one()

        try:
            discovered = {}
            status_messages = ["🔍 Starting service discovery...\n"]

            # Discover BCM modules
            if self.enable_bcm_modules:
                bcm_modules = self._discover_bcm_modules()
                discovered['bcm_modules'] = bcm_modules
                status_messages.append(f"✅ Found {len(bcm_modules)} BCM modules\n")

            # Discover AI services
            if self.enable_ai_services:
                ai_services = self._discover_ai_services()
                discovered['ai_services'] = ai_services
                status_messages.append(f"✅ Found {len(ai_services)} AI services\n")

            # Discover integrations
            if self.enable_integrations:
                integrations = self._discover_integrations()
                discovered['integrations'] = integrations
                status_messages.append(f"✅ Found {len(integrations)} integrations\n")

            # Discover adapters
            if self.enable_adapters:
                adapters = self._discover_adapters()
                discovered['adapters'] = adapters
                status_messages.append(f"✅ Found {len(adapters)} adapters\n")

            self.discovered_services = json.dumps(discovered, indent=2)
            status_messages.append(f"\n🎉 Discovery completed! Found {sum(len(category) for category in discovered.values())} total services")

            self.setup_status = ''.join(status_messages)

        except Exception as e:
            self.setup_status = f"❌ Discovery failed: {str(e)}"

        return {'type': 'ir.actions.do_nothing'}

    def _discover_bcm_modules(self):
        """Discover BCM modules in the system"""
        modules = {}

        # Get installed BCM modules
        bcm_modules = self.env['ir.module.module'].search([
            ('name', 'like', 'bcm_%'),
            ('state', '=', 'installed')
        ])

        for module in bcm_modules:
            modules[module.name] = {
                'url': f'/web/dataset/call_kw/{module.name}/search_read',
                'auth_type': 'session',
                'priority': 1 if module.name in ['bcm_core', 'bcm_incident'] else 2,
                'data_types': self._get_module_data_types(module.name),
                'collection_method': 'realtime' if module.name == 'bcm_incident' else 'api',
                'discovered': True
            }

        return modules

    def _discover_ai_services(self):
        """Discover AI services"""
        services = {}

        # Check for AI consultant
        try:
            import requests
            response = requests.get('http://localhost:8001/health', timeout=5)
            if response.status_code == 200:
                services['ai_consultant'] = {
                    'url': 'http://localhost:8001/api/v1/consultant/status',
                    'auth_type': 'bearer',
                    'priority': 1,
                    'data_types': ['recommendations', 'analysis', 'insights'],
                    'collection_method': 'websocket',
                    'discovered': True
                }
        except:
            pass

        # Check for AI organs
        try:
            response = requests.get('http://localhost:8002/health', timeout=5)
            if response.status_code == 200:
                services['ai_organs'] = {
                    'url': 'http://localhost:8002/api/v1/organs/metrics',
                    'auth_type': 'bearer',
                    'priority': 1,
                    'data_types': ['organ_status', 'ai_metrics', 'performance'],
                    'collection_method': 'api',
                    'discovered': True
                }
        except:
            pass

        return services

    def _discover_integrations(self):
        """Discover integration services"""
        integrations = {}

        # Common integration endpoints
        integration_endpoints = {
            'keycloak': 'http://localhost:8080/auth/admin/realms/bcm',
            'rabbitmq': 'http://localhost:15672/api/overview',
            'redis': 'http://localhost:6379',
            'grafana': 'http://localhost:3000/api/health'
        }

        for name, endpoint in integration_endpoints.items():
            try:
                import requests
                response = requests.get(endpoint, timeout=3)
                if response.status_code < 500:  # Service exists
                    integrations[name] = {
                        'url': endpoint,
                        'auth_type': 'basic' if name in ['rabbitmq', 'grafana'] else 'oauth2',
                        'priority': 3,
                        'data_types': self._get_integration_data_types(name),
                        'collection_method': 'api',
                        'discovered': True
                    }
            except:
                pass

        return integrations

    def _discover_adapters(self):
        """Discover adapter services"""
        adapters = {}

        # Common adapter endpoints
        adapter_endpoints = {
            'bpmn_engine': 'http://localhost:8090/engine-rest/version',
            'lms_adapter': 'http://localhost:8091/api/v1/health',
            'thehive_adapter': 'http://localhost:9000/api/status'
        }

        for name, endpoint in adapter_endpoints.items():
            try:
                import requests
                response = requests.get(endpoint, timeout=3)
                if response.status_code < 500:
                    adapters[name] = {
                        'url': endpoint.replace('/version', '').replace('/health', '').replace('/status', ''),
                        'auth_type': 'basic',
                        'priority': 2,
                        'data_types': self._get_adapter_data_types(name),
                        'collection_method': 'api',
                        'discovered': True
                    }
            except:
                pass

        return adapters

    def _get_module_data_types(self, module_name):
        """Get data types for BCM modules"""
        type_mapping = {
            'bcm_core': ['processes', 'plans', 'resources'],
            'bcm_incident': ['incidents', 'responses', 'timelines'],
            'bcm_training': ['courses', 'progress', 'certificates'],
            'bcm_bia': ['assessments', 'impacts', 'dependencies'],
            'bcm_risk_management': ['risks', 'assessments', 'mitigations'],
            'bcm_governance': ['policies', 'compliance', 'audits'],
            'bcm_reporting': ['reports', 'analytics', 'dashboards']
        }
        return type_mapping.get(module_name, ['data'])

    def _get_integration_data_types(self, integration_name):
        """Get data types for integrations"""
        type_mapping = {
            'keycloak': ['users', 'sessions', 'permissions'],
            'rabbitmq': ['queues', 'messages', 'connections'],
            'redis': ['cache_metrics', 'key_stats'],
            'grafana': ['dashboards', 'metrics', 'alerts']
        }
        return type_mapping.get(integration_name, ['metrics'])

    def _get_adapter_data_types(self, adapter_name):
        """Get data types for adapters"""
        type_mapping = {
            'bpmn_engine': ['processes', 'instances', 'tasks'],
            'lms_adapter': ['courses', 'enrollments', 'progress'],
            'thehive_adapter': ['cases', 'observables', 'tasks']
        }
        return type_mapping.get(adapter_name, ['data'])

    def action_validate_configuration(self):
        """Validate the configuration before applying"""
        self.ensure_one()

        try:
            status_messages = ["🔧 Validating configuration...\n"]

            if self.setup_type == 'quick_start':
                # Use discovered services
                if not self.discovered_services:
                    raise UserError(_("Please run service discovery first."))

                config = json.loads(self.discovered_services)

            elif self.setup_type == 'custom':
                # Use custom configuration
                if not self.custom_services:
                    raise UserError(_("Please provide custom services configuration."))

                config = json.loads(self.custom_services)

            elif self.setup_type == 'import_config':
                # Use imported configuration
                if not self.config_file:
                    raise UserError(_("Please upload a configuration file."))

                import base64
                config_data = base64.b64decode(self.config_file)
                config = json.loads(config_data.decode('utf-8'))

            # Validate configuration structure
            self._validate_config_structure(config)
            status_messages.append("✅ Configuration structure is valid\n")

            # Test connections if requested
            if self.test_connections:
                status_messages.append("🔌 Testing connections...\n")
                test_results = self._test_all_connections(config)

                for category, services in test_results.items():
                    for service_name, result in services.items():
                        if result['success']:
                            status_messages.append(f"  ✅ {service_name}: OK ({result['response_time']:.2f}s)\n")
                        else:
                            status_messages.append(f"  ❌ {service_name}: {result['error']}\n")

            status_messages.append("\n🎉 Configuration validation completed!")
            self.setup_status = ''.join(status_messages)

        except Exception as e:
            self.setup_status = f"❌ Validation failed: {str(e)}"

        return {'type': 'ir.actions.do_nothing'}

    def _validate_config_structure(self, config):
        """Validate configuration structure"""
        required_fields = ['url', 'auth_type', 'priority', 'data_types', 'collection_method']

        for category, services in config.items():
            if not isinstance(services, dict):
                raise ValidationError(f"Category '{category}' must contain a dictionary of services")

            for service_name, service_config in services.items():
                for field in required_fields:
                    if field not in service_config:
                        raise ValidationError(f"Service '{service_name}' missing required field: {field}")

    def _test_all_connections(self, config):
        """Test connections to all services in configuration"""
        import requests
        results = {}

        for category, services in config.items():
            results[category] = {}

            for service_name, service_config in services.items():
                try:
                    import time
                    start_time = time.time()

                    response = requests.get(
                        service_config['url'],
                        timeout=5
                    )

                    response_time = time.time() - start_time

                    results[category][service_name] = {
                        'success': response.status_code < 500,
                        'response_time': response_time,
                        'status_code': response.status_code
                    }

                except Exception as e:
                    results[category][service_name] = {
                        'success': False,
                        'error': str(e)
                    }

        return results

    def action_apply_configuration(self):
        """Apply the configuration to the orchestrator"""
        self.ensure_one()

        try:
            status_messages = ["🚀 Applying configuration...\n"]

            # Get configuration based on setup type
            if self.setup_type == 'quick_start':
                if not self.discovered_services:
                    raise UserError(_("Please run service discovery first."))
                config = json.loads(self.discovered_services)

            elif self.setup_type == 'custom':
                if not self.custom_services:
                    raise UserError(_("Please provide custom services configuration."))
                config = json.loads(self.custom_services)

            elif self.setup_type == 'import_config':
                if not self.config_file:
                    raise UserError(_("Please upload a configuration file."))
                import base64
                config_data = base64.b64decode(self.config_file)
                config = json.loads(config_data.decode('utf-8'))

            # Apply service endpoints
            self.orchestrator_id.service_endpoints = config
            status_messages.append("✅ Service endpoints configured\n")

            # Apply collection schedule
            schedule = self._generate_collection_schedule(config)
            self.orchestrator_id.collection_schedule = schedule
            status_messages.append("✅ Collection schedule configured\n")

            # Apply performance settings
            self.orchestrator_id.max_concurrent_collections = self.max_concurrent
            self.orchestrator_id.rate_limit_requests_per_second = self.rate_limit
            status_messages.append("✅ Performance settings applied\n")

            # Set up data validation rules
            validation_rules = self._generate_validation_rules(config)
            self.orchestrator_id.data_validation_rules = validation_rules
            status_messages.append("✅ Validation rules configured\n")

            status_messages.append("\n🎉 Configuration applied successfully!")
            status_messages.append(f"\nConfigured {sum(len(services) for services in config.values())} services across {len(config)} categories.")

            self.setup_status = ''.join(status_messages)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Configuration applied successfully! The orchestrator is ready to start collecting data.'),
                    'type': 'success',
                }
            }

        except Exception as e:
            self.setup_status = f"❌ Configuration failed: {str(e)}"
            raise UserError(_("Failed to apply configuration: %s") % str(e))

    def _generate_collection_schedule(self, config):
        """Generate collection schedule based on configuration"""
        frequency_mapping = {
            'realtime': {'interval': 5, 'realtime': True},
            'high': {'interval': 30, 'realtime': False},
            'medium': {'interval': 300, 'realtime': False},
            'low': {'interval': 1800, 'realtime': False}
        }

        frequency_config = frequency_mapping[self.collection_frequency]

        schedule = {
            'real_time_services': [],
            'intervals': {
                'critical': frequency_config['interval'],
                'high': frequency_config['interval'] * 2,
                'medium': frequency_config['interval'] * 6,
                'low': frequency_config['interval'] * 12
            },
            'batch_collections': {
                'frequent': [],
                'hourly': [],
                'daily': []
            },
            'priority_mapping': {}
        }

        # Classify services by priority and collection method
        for category, services in config.items():
            for service_name, service_config in services.items():
                priority = service_config.get('priority', 2)
                collection_method = service_config.get('collection_method', 'api')

                # Real-time services
                if collection_method in ['websocket', 'realtime'] or frequency_config['realtime']:
                    schedule['real_time_services'].append(service_name)

                # Priority mapping
                if priority == 1:
                    schedule['priority_mapping'][service_name] = 'critical'
                    schedule['batch_collections']['frequent'].append(service_name)
                elif priority == 2:
                    schedule['priority_mapping'][service_name] = 'high'
                    schedule['batch_collections']['hourly'].append(service_name)
                else:
                    schedule['priority_mapping'][service_name] = 'low'
                    schedule['batch_collections']['daily'].append(service_name)

        return schedule

    def _generate_validation_rules(self, config):
        """Generate data validation rules"""
        rules = {
            'required_fields': {},
            'data_types': {
                'timestamp_fields': ['created_date', 'updated_date', 'timestamp'],
                'numeric_fields': ['id', 'priority', 'severity'],
                'string_fields': ['name', 'description', 'status']
            },
            'validation_rules': {
                'max_age_hours': 24,
                'min_required_fields': 0.8,
                'max_payload_size_mb': 50
            }
        }

        # Set required fields based on service types
        for category, services in config.items():
            for service_name, service_config in services.items():
                data_types = service_config.get('data_types', [])

                if 'incidents' in data_types:
                    rules['required_fields'][service_name] = ['id', 'name', 'status', 'created_date']
                elif 'users' in data_types:
                    rules['required_fields'][service_name] = ['id', 'login', 'name']
                elif 'metrics' in data_types:
                    rules['required_fields'][service_name] = ['timestamp', 'value', 'metric_name']
                else:
                    rules['required_fields'][service_name] = ['id', 'name']

        return rules

    @api.model
    def action_open_wizard(self):
        """Open the collection setup wizard"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Setup Data Collection'),
            'res_model': 'bcm.collection.setup.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }