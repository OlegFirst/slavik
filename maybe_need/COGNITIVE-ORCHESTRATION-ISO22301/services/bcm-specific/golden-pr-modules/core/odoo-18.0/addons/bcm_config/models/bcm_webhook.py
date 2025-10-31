# -*- coding: utf-8 -*-
from odoo import models, fields, api
import requests
import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class BCMWebhookMixin(models.AbstractModel):
    """Mixin to add webhook functionality to BCM models"""
    _name = 'bcm.webhook.mixin'
    _description = 'BCM Webhook Mixin'
    
    @api.model
    def send_event_to_eventbus(self, event_type, data=None):
        """Send event to EventBus service"""
        try:
            config = self.env['bcm.config'].get_config()
            if not config.webhook_enabled:
                _logger.debug(f"Webhooks disabled, skipping event {event_type}")
                return False
            
            eventbus_url = config.eventbus_base_url
            if not eventbus_url:
                _logger.warning("EventBus URL not configured")
                return False
            
            # Prepare event payload
            payload = {
                'event_type': event_type,
                'tenant_id': config.get_tenant_id(),
                'user_id': self.env.user.login,
                'data': data or {},
                'correlation_id': f'odoo_{self._name}_{getattr(self, "id", 0)}',
                'metadata': {
                    'source': 'odoo',
                    'model': self._name,
                    'record_id': getattr(self, 'id', None),
                    'timestamp': datetime.utcnow().isoformat(),
                    'company_id': self.env.company.id
                }
            }
            
            # Prepare headers
            headers = {'Content-Type': 'application/json'}
            
            # Add authentication if configured
            if config.webhook_authentication == 'api_key' and config.webhook_api_key:
                headers['X-API-Key'] = config.webhook_api_key
            elif config.webhook_authentication == 'bearer_token' and config.webhook_api_key:
                headers['Authorization'] = f'Bearer {config.webhook_api_key}'
            
            # Send to EventBus with retry logic
            for attempt in range(config.webhook_retry_count):
                try:
                    response = requests.post(
                        f'{eventbus_url}/api/events/publish',
                        json=payload,
                        headers=headers,
                        timeout=config.webhook_timeout
                    )
                    
                    if response.status_code in [200, 201, 202]:
                        _logger.info(f"Event {event_type} sent successfully (attempt {attempt + 1})")
                        return True
                    else:
                        _logger.warning(f"Event send failed (attempt {attempt + 1}): {response.status_code} - {response.text}")
                        
                except requests.exceptions.Timeout:
                    _logger.warning(f"Event send timeout (attempt {attempt + 1})")
                except requests.exceptions.ConnectionError:
                    _logger.warning(f"Event send connection error (attempt {attempt + 1})")
                
                if attempt == config.webhook_retry_count - 1:
                    _logger.error(f"Failed to send event {event_type} after {config.webhook_retry_count} attempts")
                    
            return False
                
        except Exception as e:
            _logger.error(f"Error sending event to EventBus: {str(e)}")
            return False
    
    @api.model
    def call_orchestrator(self, endpoint, data=None):
        """Call Orchestrator service and get response"""
        try:
            config = self.env['bcm.config'].get_config()
            if not config.webhook_enabled:
                _logger.debug("Webhooks disabled, skipping orchestrator call")
                return None
                
            orchestrator_url = config.orchestrator_base_url
            
            if not orchestrator_url:
                _logger.warning("Orchestrator URL not configured")
                return None
            
            # Prepare request data
            request_data = data or {}
            if 'tenant_id' not in request_data:
                request_data['tenant_id'] = config.get_tenant_id()
            if 'user_id' not in request_data:
                request_data['user_id'] = self.env.user.login
            
            # Prepare headers
            headers = {'Content-Type': 'application/json'}
            
            # Add authentication if configured
            if config.webhook_authentication == 'api_key' and config.webhook_api_key:
                headers['X-API-Key'] = config.webhook_api_key
            elif config.webhook_authentication == 'bearer_token' and config.webhook_api_key:
                headers['Authorization'] = f'Bearer {config.webhook_api_key}'
            
            # Call orchestrator with retry logic
            for attempt in range(config.webhook_retry_count):
                try:
                    response = requests.post(
                        f'{orchestrator_url}{endpoint}',
                        json=request_data,
                        headers=headers,
                        timeout=config.webhook_timeout
                    )
                    
                    if response.status_code == 200:
                        _logger.info(f"Orchestrator call successful: {endpoint}")
                        return response.json()
                    else:
                        _logger.warning(f"Orchestrator call failed (attempt {attempt + 1}): {response.status_code} - {response.text}")
                        
                except requests.exceptions.Timeout:
                    _logger.warning(f"Orchestrator call timeout (attempt {attempt + 1})")
                except requests.exceptions.ConnectionError:
                    _logger.warning(f"Orchestrator connection error (attempt {attempt + 1})")
                
                if attempt == config.webhook_retry_count - 1:
                    _logger.error(f"Failed to call orchestrator {endpoint} after {config.webhook_retry_count} attempts")
            
            return None
                
        except Exception as e:
            _logger.error(f"Error calling Orchestrator: {str(e)}")
            return None

class BCMCompanyMixin(models.AbstractModel):
    """Mixin to add company_id to all BCM models"""
    _name = 'bcm.company.mixin'
    _description = 'BCM Company Mixin'
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True
    )
