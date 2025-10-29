# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import requests
import logging

_logger = logging.getLogger(__name__)

class BcmConfig(models.Model):
    """BCM Configuration Settings"""
    _name = 'bcm.config'
    _description = 'BCM Configuration'
    _rec_name = 'name'
    
    name = fields.Char(
        string='Configuration Name',
        default='BCM Settings',
        required=True
    )
    
    # AI Service URLs
    orchestrator_base_url = fields.Char(
        string='AI Orchestrator URL',
        help='Base URL for AI Orchestrator service (e.g., http://localhost:8000)'
    )
    
    bia_engine_base_url = fields.Char(
        string='BIA Engine URL',
        help='Base URL for BIA Engine service (e.g., http://localhost:8001)'
    )
    
    eventbus_base_url = fields.Char(
        string='Event Bus URL',
        help='Base URL for Event Bus service (e.g., http://localhost:8002)'
    )
    
    # Service Status
    orchestrator_status = fields.Selection([
        ('unknown', 'Unknown'),
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('error', 'Error')
    ], string='Orchestrator Status', default='unknown', readonly=True)
    
    bia_engine_status = fields.Selection([
        ('unknown', 'Unknown'),
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('error', 'Error')
    ], string='BIA Engine Status', default='unknown', readonly=True)
    
    eventbus_status = fields.Selection([
        ('unknown', 'Unknown'),
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('error', 'Error')
    ], string='Event Bus Status', default='unknown', readonly=True)
    
    last_status_check = fields.Datetime(
        string='Last Status Check',
        readonly=True
    )
    
    # Multi-tenancy
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        index=True,
        default=lambda self: self.env.company
    )
    
    active = fields.Boolean(default=True)
    
    # Webhook Configuration
    webhook_enabled = fields.Boolean(
        string='Enable Webhooks',
        default=True,
        help='Enable automatic webhook notifications to external services'
    )
    
    webhook_authentication = fields.Selection([
        ('none', 'No Authentication'),
        ('api_key', 'API Key'),
        ('bearer_token', 'Bearer Token')
    ], string='Webhook Authentication', default='none')
    
    webhook_api_key = fields.Char(
        string='Webhook API Key',
        help='API key for webhook authentication'
    )
    
    webhook_timeout = fields.Integer(
        string='Webhook Timeout (seconds)',
        default=30,
        help='Timeout for webhook HTTP requests'
    )
    
    webhook_retry_count = fields.Integer(
        string='Webhook Retry Count',
        default=3,
        help='Number of retry attempts for failed webhooks'
    )
    
    # Event Bus Configuration
    eventbus_tenant_id = fields.Char(
        string='Event Bus Tenant ID',
        help='Tenant identifier for Event Bus (default: company code)'
    )
    
    @api.model
    def get_config(self):
        """Get active configuration for current company"""
        config = self.search([
            ('company_id', '=', self.env.company.id),
            ('active', '=', True)
        ], limit=1)
        
        if not config:
            # Create default config if not exists
            config = self.create({
                'name': 'Default BCM Settings',
                'company_id': self.env.company.id
            })
        
        return config
    
    def action_test_connection(self):
        """Test connection to all configured services"""
        self.ensure_one()
        
        results = []
        
        # Test AI Orchestrator
        if self.orchestrator_base_url:
            status = self._test_service_connection(
                self.orchestrator_base_url,
                'AI Orchestrator'
            )
            self.orchestrator_status = status
            results.append(f"AI Orchestrator: {status}")
        
        # Test BIA Engine
        if self.bia_engine_base_url:
            status = self._test_service_connection(
                self.bia_engine_base_url,
                'BIA Engine'
            )
            self.bia_engine_status = status
            results.append(f"BIA Engine: {status}")
        
        # Test Event Bus
        if self.eventbus_base_url:
            status = self._test_service_connection(
                self.eventbus_base_url,
                'Event Bus'
            )
            self.eventbus_status = status
            results.append(f"Event Bus: {status}")
        
        self.last_status_check = fields.Datetime.now()
        
        # Show result notification
        message = '\n'.join(results) if results else 'No services configured'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Connection Test Results'),
                'message': message,
                'type': 'info' if any('online' in r for r in results) else 'warning',
                'sticky': False,
            }
        }
    
    def action_test_webhooks(self):
        """Test webhook configuration by sending test events"""
        self.ensure_one()
        
        if not self.webhook_enabled:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Webhooks Disabled'),
                    'message': _('Webhooks are not enabled in configuration'),
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        results = []
        
        # Test Event Bus webhook
        if self.eventbus_base_url:
            test_payload = {
                'event_type': 'bcm.test.webhook',
                'tenant_id': self.get_tenant_id(),
                'data': {'message': 'Test webhook from BCM configuration'},
                'user_id': self.env.user.login
            }
            
            success = self._send_test_webhook(
                f"{self.eventbus_base_url}/api/events/publish",
                test_payload
            )
            results.append(f"Event Bus webhook: {'Success' if success else 'Failed'}")
        
        # Test Orchestrator webhook
        if self.orchestrator_base_url:
            test_payload = {
                'context': 'test',
                'data': {'message': 'Test webhook from BCM configuration'},
                'tenant_id': self.get_tenant_id()
            }
            
            success = self._send_test_webhook(
                f"{self.orchestrator_base_url}/api/callback/odoo",
                test_payload
            )
            results.append(f"Orchestrator webhook: {'Success' if success else 'Failed'}")
        
        message = '\n'.join(results) if results else 'No webhook endpoints configured'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Webhook Test Results'),
                'message': message,
                'type': 'info' if any('Success' in r for r in results) else 'warning',
                'sticky': False,
            }
        }
    
    def _send_test_webhook(self, url, payload):
        """Send test webhook and return success status"""
        try:
            headers = {'Content-Type': 'application/json'}
            
            # Add authentication if configured
            if self.webhook_authentication == 'api_key' and self.webhook_api_key:
                headers['X-API-Key'] = self.webhook_api_key
            elif self.webhook_authentication == 'bearer_token' and self.webhook_api_key:
                headers['Authorization'] = f'Bearer {self.webhook_api_key}'
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.webhook_timeout
            )
            
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            _logger.error(f"Webhook test failed for {url}: {e}")
            return False
    
    def get_tenant_id(self):
        """Get tenant ID for event bus"""
        if self.eventbus_tenant_id:
            return self.eventbus_tenant_id
        
        # Default to company code or name
        company = self.company_id
        return company.code or company.name.lower().replace(' ', '_')
    
    def _test_service_connection(self, base_url, service_name):
        """Test connection to a specific service"""
        try:
            # Try health check endpoint
            health_url = f"{base_url}/health"
            response = requests.get(health_url, timeout=5)
            
            if response.status_code == 200:
                return 'online'
            else:
                return 'error'
                
        except requests.exceptions.ConnectionError:
            _logger.warning(f"Cannot connect to {service_name} at {base_url}")
            return 'offline'
        except requests.exceptions.Timeout:
            _logger.warning(f"Timeout connecting to {service_name} at {base_url}")
            return 'offline'
        except Exception as e:
            _logger.error(f"Error testing {service_name}: {e}")
            return 'error'
    
    @api.model
    def cron_check_service_status(self):
        """Cron job to check service status"""
        configs = self.search([('active', '=', True)])
        
        for config in configs:
            config.with_context(no_notification=True).action_test_connection()
    
    @api.constrains('orchestrator_base_url', 'bia_engine_base_url', 'eventbus_base_url')
    def _check_urls(self):
        """Validate URL format"""
        for record in self:
            urls = [
                ('AI Orchestrator', record.orchestrator_base_url),
                ('BIA Engine', record.bia_engine_base_url),
                ('Event Bus', record.eventbus_base_url)
            ]
            
            for name, url in urls:
                if url and not (url.startswith('http://') or url.startswith('https://')):
                    raise ValidationError(
                        _('%s URL must start with http:// or https://') % name
                    )
