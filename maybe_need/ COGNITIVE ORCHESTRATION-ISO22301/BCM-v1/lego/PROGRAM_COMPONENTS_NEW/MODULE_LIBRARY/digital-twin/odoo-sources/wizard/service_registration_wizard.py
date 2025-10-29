# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import json

class ServiceRegistrationWizard(models.TransientModel):
    _name = 'bcm.service.registration.wizard'
    _description = 'Service Registration Wizard'

    orchestrator_id = fields.Many2one(
        'bcm.data.collection.orchestrator',
        string='Orchestrator',
        required=True,
        help="Select the orchestrator to register this service with"
    )

    service_name = fields.Char(
        string='Service Name',
        required=True,
        help="Unique name for the service (e.g., bcm_incident, ai_consultant)"
    )

    service_url = fields.Char(
        string='Service URL',
        required=True,
        help="Full URL endpoint for the service"
    )

    service_category = fields.Selection([
        ('bcm_modules', 'BCM Modules'),
        ('ai_services', 'AI Services'),
        ('integrations', 'Integrations'),
        ('adapters', 'Adapters')
    ], string='Service Category', required=True)

    auth_type = fields.Selection([
        ('none', 'No Authentication'),
        ('session', 'Session Based'),
        ('bearer', 'Bearer Token'),
        ('basic', 'Basic Authentication'),
        ('oauth2', 'OAuth2'),
        ('api_key', 'API Key')
    ], string='Authentication Type', required=True, default='session')

    api_key = fields.Char(
        string='API Key',
        help="API key for authentication (if applicable)"
    )

    username = fields.Char(
        string='Username',
        help="Username for basic authentication"
    )

    password = fields.Char(
        string='Password',
        help="Password for basic authentication"
    )

    bearer_token = fields.Text(
        string='Bearer Token',
        help="Bearer token for authentication"
    )

    priority = fields.Selection([
        (1, 'High (Critical)'),
        (2, 'Medium (Normal)'),
        (3, 'Low (Background)')
    ], string='Collection Priority', required=True, default=2)

    collection_method = fields.Selection([
        ('api', 'REST API'),
        ('websocket', 'WebSocket'),
        ('realtime', 'Real-time Events'),
        ('direct', 'Direct Connection')
    ], string='Collection Method', required=True, default='api')

    data_types = fields.Text(
        string='Data Types',
        help="Comma-separated list of data types this service provides (e.g., incidents, users, metrics)",
        placeholder="incidents, responses, timelines"
    )

    websocket_url = fields.Char(
        string='WebSocket URL',
        help="WebSocket endpoint (if different from main URL)"
    )

    test_connection = fields.Boolean(
        string='Test Connection',
        default=True,
        help="Test the connection before registering"
    )

    connection_test_result = fields.Text(
        string='Test Result',
        readonly=True
    )

    @api.onchange('service_name')
    def _onchange_service_name(self):
        """Auto-determine category based on service name"""
        if self.service_name:
            name = self.service_name.lower()
            if name.startswith('bcm_'):
                self.service_category = 'bcm_modules'
            elif 'ai' in name:
                self.service_category = 'ai_services'
            elif name in ['keycloak', 'rabbitmq', 'redis', 'grafana']:
                self.service_category = 'integrations'
            else:
                self.service_category = 'adapters'

    @api.onchange('collection_method')
    def _onchange_collection_method(self):
        """Update WebSocket URL visibility"""
        if self.collection_method == 'websocket' and self.service_url:
            self.websocket_url = self.service_url.replace('http', 'ws')

    def action_test_connection(self):
        """Test connection to the service"""
        self.ensure_one()

        try:
            import requests
            import time

            start_time = time.time()

            # Prepare authentication
            headers = {'Content-Type': 'application/json'}
            auth_params = {}

            if self.auth_type == 'api_key' and self.api_key:
                headers['X-API-Key'] = self.api_key
            elif self.auth_type == 'bearer' and self.bearer_token:
                headers['Authorization'] = f'Bearer {self.bearer_token}'
            elif self.auth_type == 'basic' and self.username and self.password:
                auth_params['auth'] = (self.username, self.password)

            # Make test request
            response = requests.get(
                self.service_url,
                headers=headers,
                timeout=10,
                **auth_params
            )

            response_time = time.time() - start_time

            if response.status_code < 400:
                self.connection_test_result = f"""✅ Connection Successful!

Status Code: {response.status_code}
Response Time: {response_time:.2f}s
Content Length: {len(response.content)} bytes

Service appears to be healthy and accessible."""
            else:
                self.connection_test_result = f"""⚠️ Connection Issues

Status Code: {response.status_code}
Response Time: {response_time:.2f}s
Error: {response.text[:200]}...

The service responded but may have authentication or endpoint issues."""

        except Exception as e:
            self.connection_test_result = f"""❌ Connection Failed

Error: {str(e)}

Please check:
- Service URL is correct and accessible
- Authentication credentials are valid
- Service is running and healthy
- Network connectivity is available"""

        return {
            'type': 'ir.actions.do_nothing',
        }

    def action_register_service(self):
        """Register the service with the orchestrator"""
        self.ensure_one()

        if self.test_connection and not self.connection_test_result:
            raise UserError(_("Please test the connection first before registering."))

        if self.test_connection and "❌" in self.connection_test_result:
            raise UserError(_("Connection test failed. Please fix the issues before registering."))

        try:
            # Prepare service configuration
            data_types_list = []
            if self.data_types:
                data_types_list = [dt.strip() for dt in self.data_types.split(',') if dt.strip()]

            endpoint_config = {
                'url': self.service_url,
                'auth_type': self.auth_type,
                'priority': self.priority,
                'data_types': data_types_list,
                'collection_method': self.collection_method,
                'websocket_url': self.websocket_url or None,
                'credentials': self._prepare_credentials(),
                'registered_via_wizard': True,
                'wizard_registration_date': fields.Datetime.now().isoformat()
            }

            # Register with orchestrator
            success = self.orchestrator_id.register_service_endpoint(
                self.service_name,
                endpoint_config
            )

            if success:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': _('Service "%s" has been successfully registered!') % self.service_name,
                        'type': 'success',
                    }
                }
            else:
                raise UserError(_("Failed to register service. Check the orchestrator logs for details."))

        except Exception as e:
            raise UserError(_("Registration failed: %s") % str(e))

    def _prepare_credentials(self):
        """Prepare credentials based on auth type"""
        credentials = {}

        if self.auth_type == 'api_key' and self.api_key:
            credentials['api_key'] = self.api_key
        elif self.auth_type == 'bearer' and self.bearer_token:
            credentials['bearer_token'] = self.bearer_token
        elif self.auth_type == 'basic' and self.username and self.password:
            credentials['username'] = self.username
            credentials['password'] = self.password

        return credentials

    @api.model
    def action_open_wizard(self):
        """Open the service registration wizard"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Register New Service'),
            'res_model': 'bcm.service.registration.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }