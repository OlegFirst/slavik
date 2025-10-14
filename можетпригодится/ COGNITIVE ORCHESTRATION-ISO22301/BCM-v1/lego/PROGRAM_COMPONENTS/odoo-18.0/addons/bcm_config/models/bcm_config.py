# -*- coding: utf-8 -*-
from odoo import models, fields, api
import os

class BCMConfiguration(models.Model):
    _name = 'bcm.config'
    _description = 'BCM Platform Configuration'
    _rec_name = 'name'
    _order = 'id desc'

    name = fields.Char('Configuration Name', required=True, default='BCM Platform Config')
    company_id = fields.Many2one('res.company', string='Company', required=True, 
                                  default=lambda self: self.env.company)
    
    # Service URLs
    eventbus_url = fields.Char('EventBus URL', 
                                default=lambda self: os.getenv('EVENTBUS_URL', 'http://localhost:8001'))
    orchestrator_url = fields.Char('Orchestrator URL', 
                                    default=lambda self: os.getenv('ORCHESTRATOR_URL', 'http://localhost:8002'))
    bia_engine_url = fields.Char('BIA Engine URL', 
                                  default=lambda self: os.getenv('BIA_ENGINE_URL', 'http://localhost:8082'))
    document_processor_url = fields.Char('Document Processor URL', 
                                          default=lambda self: os.getenv('DOC_PROCESSOR_URL', 'http://localhost:8003'))
    
    # API Keys
    openai_api_key = fields.Char('OpenAI API Key', 
                                  default=lambda self: os.getenv('OPENAI_API_KEY', ''))
    
    # Webhook Settings
    webhook_enabled = fields.Boolean('Enable Webhooks', default=True)
    webhook_timeout = fields.Integer('Webhook Timeout (seconds)', default=30)
    webhook_retry_count = fields.Integer('Webhook Retry Count', default=3)
    
    # Feature Flags
    ai_recommendations_enabled = fields.Boolean('Enable AI Recommendations', default=True)
    auto_bcp_generation = fields.Boolean('Auto Generate BCP from BIA', default=True)
    auto_incident_response = fields.Boolean('Auto Generate Incident Response', default=True)
    
    @api.model
    def get_config(self):
        """Get or create configuration for current company"""
        config = self.search([('company_id', '=', self.env.company.id)], limit=1)
        if not config:
            config = self.create({
                'name': f'BCM Config - {self.env.company.name}',
                'company_id': self.env.company.id,
            })
        return config
    
    @api.model
    def get_service_url(self, service_name):
        """Get service URL by name"""
        config = self.get_config()
        url_field = f'{service_name}_url'
        if hasattr(config, url_field):
            return getattr(config, url_field)
        return None
