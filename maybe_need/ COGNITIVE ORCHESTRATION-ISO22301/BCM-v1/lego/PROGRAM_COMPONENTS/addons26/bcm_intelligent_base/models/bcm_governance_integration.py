# -*- coding: utf-8 -*-

"""
BCM Intelligent Base - Governance Integration
============================================

Интеграция AI сервисов с новой governance архитектурой:
- Enhanced Governance Service (микросервис)
- bcm_governance (compliance engine)
- bcm_community (knowledge base)
"""

import json
import logging
import requests
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class BCMGovernanceIntegration(models.Model):
    """Integration with Enhanced Governance Service"""
    _name = 'bcm.governance.integration'
    _description = 'Enhanced Governance Service Integration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Integration Name', required=True, default='Enhanced Governance Service')
    governance_url = fields.Char('Governance Service URL', 
                                default='http://governance_service:8009',
                                required=True)
    api_key = fields.Char('API Key', required=True, 
                         help='Admin API key for governance service authentication')
    
    # Health monitoring
    last_sync = fields.Datetime('Last Sync')
    health_status = fields.Selection([
        ('healthy', 'Healthy'),
        ('degraded', 'Degraded'),
        ('unhealthy', 'Unhealthy'),
        ('unknown', 'Unknown'),
    ], string='Health Status', default='unknown', tracking=True)
    
    # Sync statistics
    last_compliance_sync = fields.Datetime('Last Compliance Sync')
    last_quota_sync = fields.Datetime('Last Quota Sync')
    last_knowledge_generation = fields.Datetime('Last Knowledge Generation')
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    
    def _get_auth_headers(self):
        """Get authentication headers for governance service"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def check_health(self):
        """Check health of Enhanced Governance Service"""
        try:
            response = requests.get(
                f"{self.governance_url}/health",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.health_status = 'healthy'
                else:
                    self.health_status = 'degraded'
            else:
                self.health_status = 'unhealthy'
                
        except requests.RequestException as e:
            _logger.error(f"Governance service health check failed: {e}")
            self.health_status = 'unhealthy'
        
        self.last_sync = fields.Datetime.now()
    
    def sync_compliance_to_governance(self):
        """Sync compliance data TO Enhanced Governance Service"""
        try:
            response = requests.post(
                f"{self.governance_url}/api/compliance/sync",
                headers=self._get_auth_headers(),
                json={'tenant_id': 'demo'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self.last_compliance_sync = fields.Datetime.now()
                
                self.message_post(
                    body=f"Compliance sync successful: {result.get('synced_checks', 0)} checks synced",
                    subject="Compliance Sync Success"
                )
                
                return result
            else:
                raise UserError(f"Compliance sync failed: {response.text}")
                
        except requests.RequestException as e:
            _logger.error(f"Compliance sync failed: {e}")
            raise UserError(f"Failed to sync compliance data: {str(e)}")
    
    def trigger_knowledge_generation(self):
        """Trigger knowledge article generation for compliance gaps"""
        try:
            response = requests.post(
                f"{self.governance_url}/api/knowledge/generate-gaps",
                headers=self._get_auth_headers(),
                json={'tenant_id': 'demo'},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                self.last_knowledge_generation = fields.Datetime.now()
                
                self.message_post(
                    body=f"Knowledge generation successful: {result['data'].get('generated_articles', 0)} articles created",
                    subject="Knowledge Generation Success"
                )
                
                return result
            else:
                raise UserError(f"Knowledge generation failed: {response.text}")
                
        except requests.RequestException as e:
            _logger.error(f"Knowledge generation failed: {e}")
            raise UserError(f"Failed to generate knowledge articles: {str(e)}")
    
    def sync_quotas_from_odoo(self):
        """Sync quota usage FROM Odoo TO governance service"""
        try:
            response = requests.post(
                f"{self.governance_url}/api/quotas/sync",
                headers=self._get_auth_headers(),
                json={'tenant_id': 'demo'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self.last_quota_sync = fields.Datetime.now()
                
                self.message_post(
                    body=f"Quota sync successful: {len(result['data'])} quotas updated",
                    subject="Quota Sync Success"
                )
                
                return result
            else:
                raise UserError(f"Quota sync failed: {response.text}")
                
        except requests.RequestException as e:
            _logger.error(f"Quota sync failed: {e}")
            raise UserError(f"Failed to sync quotas: {str(e)}")
    
    def get_governance_metrics(self):
        """Get comprehensive governance metrics"""
        try:
            response = requests.get(
                f"{self.governance_url}/api/metrics",
                headers=self._get_auth_headers(),
                params={'tenant_id': 'demo'},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise UserError(f"Failed to get governance metrics: {response.text}")
                
        except requests.RequestException as e:
            _logger.error(f"Get governance metrics failed: {e}")
            raise UserError(f"Failed to get governance metrics: {str(e)}")
    
    def apply_retention_policies(self):
        """Apply data retention policies (REAL cleanup)"""
        try:
            response = requests.post(
                f"{self.governance_url}/api/retention/apply",
                headers=self._get_auth_headers(),
                json={'tenant_id': 'demo'},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                self.message_post(
                    body=f"Retention applied: {result['data'].get('deleted_items', 0)} items deleted, "
                          f"{result['data'].get('freed_space_gb', 0):.2f} GB freed",
                    subject="Retention Policies Applied"
                )
                
                return result
            else:
                raise UserError(f"Retention policy application failed: {response.text}")
                
        except requests.RequestException as e:
            _logger.error(f"Apply retention policies failed: {e}")
            raise UserError(f"Failed to apply retention policies: {str(e)}")
    
    def check_system_health(self):
        """Check health of all BCM services via governance service"""
        try:
            response = requests.get(
                f"{self.governance_url}/api/health/check",
                headers=self._get_auth_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise UserError(f"System health check failed: {response.text}")
                
        except requests.RequestException as e:
            _logger.error(f"System health check failed: {e}")
            raise UserError(f"Failed to check system health: {str(e)}")
    
    @api.model
    def cron_sync_all_governance_data(self):
        """Cron job to sync all governance data"""
        integrations = self.search([('company_id', '=', self.env.company.id)])
        
        for integration in integrations:
            try:
                # Check health first
                integration.check_health()
                
                if integration.health_status == 'healthy':
                    # Sync compliance data
                    integration.sync_compliance_to_governance()
                    
                    # Sync quotas
                    integration.sync_quotas_from_odoo()
                    
                    # Generate knowledge articles if needed
                    # (Only if last generation was more than 1 day ago)
                    if not integration.last_knowledge_generation or \
                       integration.last_knowledge_generation < fields.Datetime.now() - timedelta(days=1):
                        integration.trigger_knowledge_generation()
                
            except Exception as e:
                _logger.error(f"Governance sync failed for {integration.name}: {e}")
                
                # Create activity for admin
                admin = self.env.ref('base.user_admin')
                self.env['mail.activity'].create({
                    'res_model': 'bcm.governance.integration',
                    'res_id': integration.id,
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'summary': 'Governance Sync Failed',
                    'note': f'Governance synchronization failed: {str(e)}',
                    'user_id': admin.id,
                    'date_deadline': fields.Date.today(),
                })


class BCMAIIntegration(models.Model):
    """Enhanced AI Integration with Governance Support"""
    _inherit = 'bcm.ai.integration'
    
    def compliance_analysis_with_governance(self, compliance_data):
        """Enhanced compliance analysis with governance integration"""
        # First, use the standard compliance checker
        result = self.check_compliance(compliance_data)
        
        # Then, integrate with governance service for comprehensive analysis
        governance_integration = self.env['bcm.governance.integration'].search([
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        
        if governance_integration and governance_integration.health_status == 'healthy':
            try:
                # Sync results to governance service
                governance_integration.sync_compliance_to_governance()
                
                # Get comprehensive metrics
                metrics = governance_integration.get_governance_metrics()
                
                # Enhance result with governance data
                result['governance_metrics'] = metrics.get('data', {})
                result['overall_compliance'] = metrics.get('data', {}).get('compliance', {}).get('average_compliance', 0)
                
            except Exception as e:
                _logger.warning(f"Governance integration failed during compliance analysis: {e}")
                # Continue with standard result
        
        return result
    
    def ai_enhanced_knowledge_generation(self, gap_data):
        """AI-enhanced knowledge generation for compliance gaps"""
        # Use AI Orchestrator to enhance the gap analysis
        orchestrator_url = self.get_service_url('orchestrator')
        
        enhanced_gaps = []
        
        if orchestrator_url:
            try:
                response = requests.post(
                    f"{orchestrator_url}/analyze/compliance-gaps",
                    json={
                        'gaps': gap_data,
                        'context': 'knowledge_generation',
                        'iso_standard': 'ISO 22301:2019'
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    ai_result = response.json()
                    enhanced_gaps = ai_result.get('enhanced_gaps', gap_data)
                else:
                    _logger.warning(f"AI Orchestrator gap analysis failed: {response.text}")
                    enhanced_gaps = gap_data
                    
            except requests.RequestException as e:
                _logger.warning(f"AI Orchestrator request failed: {e}")
                enhanced_gaps = gap_data
        else:
            enhanced_gaps = gap_data
        
        # Trigger governance service knowledge generation with enhanced data
        governance_integration = self.env['bcm.governance.integration'].search([
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        
        if governance_integration:
            return governance_integration.trigger_knowledge_generation()
        else:
            raise UserError(_('Governance integration is not configured'))
