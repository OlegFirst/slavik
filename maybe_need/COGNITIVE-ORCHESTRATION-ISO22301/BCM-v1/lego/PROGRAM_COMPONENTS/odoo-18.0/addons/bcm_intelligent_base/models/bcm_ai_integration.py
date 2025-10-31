# -*- coding: utf-8 -*-

import json
import logging
import requests
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class BCMAIIntegration(models.Model):
    """Central AI Integration Hub for BCM Platform"""
    _name = 'bcm.ai.integration'
    _description = 'BCM AI Integration Hub'
    _rec_name = 'service_name'
    _order = 'sequence, service_name'
    
    sequence = fields.Integer('Sequence', default=10)
    service_name = fields.Char('Service Name', required=True)
    service_type = fields.Selection([
        ('orchestrator', 'AI Orchestrator'),
        ('bia_engine', 'BIA Engine v2.0'),
        ('document_processor', 'Document Processor'),
        ('compliance_checker', 'Compliance Checker'),
    ], string='Service Type', required=True)
    
    service_url = fields.Char('Service URL', required=True)
    api_key = fields.Char('API Key')
    is_active = fields.Boolean('Active', default=True)
    
    # Service health monitoring
    last_health_check = fields.Datetime('Last Health Check')
    health_status = fields.Selection([
        ('healthy', 'Healthy'),
        ('degraded', 'Degraded'),
        ('unhealthy', 'Unhealthy'),
        ('unknown', 'Unknown'),
    ], string='Health Status', default='unknown')
    
    # Multi-tenancy
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True, index=True,
        default=lambda self: self.env.company
    )
    
    @api.model
    def get_service_url(self, service_type):
        """Get active service URL by type"""
        service = self.search([
            ('service_type', '=', service_type),
            ('is_active', '=', True),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        
        if not service:
            # Fallback to environment configuration
            import os
            url_map = {
                'orchestrator': os.getenv('AI_ORCHESTRATOR_URL', 'http://ai_orchestrator:8000'),
                'bia_engine': os.getenv('BIA_ENGINE_URL', 'http://bia_engine:8082'),
                'document_processor': os.getenv('DOCUMENT_PROCESSOR_URL', 'http://document_processor:8083'),
                'compliance_checker': os.getenv('COMPLIANCE_CHECKER_URL', 'http://compliance_checker:8084'),
            }
            return url_map.get(service_type)
        
        return service.service_url
    
    def check_health(self):
        """Check health status of AI service"""
        for service in self:
            try:
                response = requests.get(
                    f"{service.service_url}/health",
                    timeout=5
                )
                
                if response.status_code == 200:
                    service.health_status = 'healthy'
                else:
                    service.health_status = 'degraded'
                    
            except requests.RequestException as e:
                _logger.error(f"Health check failed for {service.service_name}: {e}")
                service.health_status = 'unhealthy'
            
            service.last_health_check = fields.Datetime.now()
    
    # BIA Engine Integration Methods
    def bia_optimize_single_process(self, process_data, risk_tolerance=0.05):
        """Call BIA Engine to optimize single process"""
        bia_url = self.get_service_url('bia_engine')
        
        if not bia_url:
            raise UserError(_('BIA Engine service is not configured'))
        
        try:
            response = requests.post(
                f"{bia_url}/api/v1/bia/optimize-single",
                json={
                    'process': process_data,
                    'risk_tolerance': risk_tolerance
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise UserError(
                    _('BIA Engine returned error: %s') % response.text
                )
                
        except requests.RequestException as e:
            _logger.error(f"BIA Engine request failed: {e}")
            raise UserError(_('Failed to connect to BIA Engine: %s') % str(e))
    
    def bia_compute_comprehensive_analysis(self, processes_data, analysis_period_days, risk_tolerance):
        """Call BIA Engine for comprehensive analysis"""
        bia_url = self.get_service_url('bia_engine')
        
        if not bia_url:
            raise UserError(_('BIA Engine service is not configured'))
        
        try:
            response = requests.post(
                f"{bia_url}/api/v1/bia/comprehensive-analysis",
                json={
                    'processes': processes_data,
                    'analysis_period_days': analysis_period_days,
                    'risk_tolerance': risk_tolerance
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise UserError(
                    _('BIA Engine returned error: %s') % response.text
                )
                
        except requests.RequestException as e:
            _logger.error(f"BIA Engine comprehensive analysis failed: {e}")
            raise UserError(_('Failed to connect to BIA Engine: %s') % str(e))
    
    # AI Orchestrator Integration Methods
    def orchestrate_incident_classification(self, incident_data):
        """Call AI Orchestrator to classify incident"""
        orchestrator_url = self.get_service_url('orchestrator')
        
        if not orchestrator_url:
            raise UserError(_('AI Orchestrator service is not configured'))
        
        try:
            response = requests.post(
                f"{orchestrator_url}/analyze/incident",
                json=incident_data,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise UserError(
                    _('AI Orchestrator returned error: %s') % response.text
                )
                
        except requests.RequestException as e:
            _logger.error(f"AI Orchestrator request failed: {e}")
            raise UserError(_('Failed to connect to AI Orchestrator: %s') % str(e))
    
    # Document Processor Integration Methods
    def process_document(self, document_path, document_type=None):
        """Call Document Processor to analyze document"""
        processor_url = self.get_service_url('document_processor')
        
        if not processor_url:
            raise UserError(_('Document Processor service is not configured'))
        
        try:
            with open(document_path, 'rb') as f:
                files = {'file': f}
                data = {'document_type': document_type} if document_type else {}
                
                response = requests.post(
                    f"{processor_url}/api/v1/process",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise UserError(
                    _('Document Processor returned error: %s') % response.text
                )
                
        except requests.RequestException as e:
            _logger.error(f"Document Processor request failed: {e}")
            raise UserError(_('Failed to connect to Document Processor: %s') % str(e))
    
    # Compliance Checker Integration Methods
    def check_compliance(self, compliance_data):
        """Call Compliance Checker to assess ISO 22301 compliance"""
        checker_url = self.get_service_url('compliance_checker')
        
        if not checker_url:
            raise UserError(_('Compliance Checker service is not configured'))
        
        try:
            response = requests.post(
                f"{checker_url}/api/v1/assess",
                json=compliance_data,
                timeout=20
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise UserError(
                    _('Compliance Checker returned error: %s') % response.text
                )
                
        except requests.RequestException as e:
            _logger.error(f"Compliance Checker request failed: {e}")
            raise UserError(_('Failed to connect to Compliance Checker: %s') % str(e))
    
    @api.model
    def cron_health_check_all_services(self):
        """Cron job to check health of all AI services"""
        services = self.search([('is_active', '=', True)])
        services.check_health()
        
        # Send notification if any service is unhealthy
        unhealthy = services.filtered(lambda s: s.health_status == 'unhealthy')
        if unhealthy:
            message = _('The following AI services are unhealthy: %s') % ', '.join(
                unhealthy.mapped('service_name')
            )
            _logger.warning(message)
            
            # Create activity for system admin
            admin = self.env.ref('base.user_admin')
            self.env['mail.activity'].create({
                'res_model': 'bcm.ai.integration',
                'res_id': unhealthy[0].id,
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': 'AI Services Health Alert',
                'note': message,
                'user_id': admin.id,
                'date_deadline': fields.Date.today(),
            })
