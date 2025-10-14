# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)

class BcmClient(models.Model):
    _name = 'bcm.client'
    _description = 'BCM Client Organization'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'
    _sql_constraints = [
        ('name_company_unique', 'unique(name, company_id)', 
         'Client name must be unique within company!')
    ]

    # Основные поля
    name = fields.Char(
        string='Organization Name',
        required=True, index=True,
        tracking=True,
        help='Name of the client organization'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Tenant',
        required=True, index=True,
        default=lambda self: self.env.company,
        help='Company/tenant isolation'
    )
    
    sector = fields.Selection([
        ('hospital', 'Hospital/Healthcare'),
        ('public', 'Public Sector'),
        ('lab', 'Laboratory'),
        ('private', 'Private Enterprise'),
        ('financial', 'Financial Services'),
        ('manufacturing', 'Manufacturing'),
        ('education', 'Education'),
        ('energy', 'Energy & Utilities'),
        ('other', 'Other')
    ], string='Industry Sector', tracking=True)
    
    region = fields.Char(
        string='Geographic Region',
        tracking=True,
        help='Primary geographic region of operations'
    )
    
    onboarding_stage = fields.Selection([
        ('new', 'New Client'),
        ('bia_ready', 'BIA Analysis Ready'),
        ('plans', 'Plans Development'),
        ('live', 'Live/Production'),
        ('maintenance', 'Maintenance Mode')
    ], string='Onboarding Stage', default='new', tracking=True)
    
    dpa_signed = fields.Boolean(
        string='DPA Signed',
        default=False,
        tracking=True,
        help='Data Processing Agreement signed'
    )
    
    data_residency = fields.Selection([
        ('us', 'United States'),
        ('eu', 'European Union'),
        ('ca', 'Canada'),
        ('au', 'Australia'),
        ('custom', 'Custom Location')
    ], string='Data Residency', default='us', tracking=True)
    
    status = fields.Selection([
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('archived', 'Archived'),
        ('onboarding', 'Onboarding')
    ], string='Status', default='onboarding', tracking=True)
    
    notes = fields.Text(
        string='Internal Notes',
        help='Internal notes about the client'
    )
    
    # Связанные записи (Smart Buttons)
    contact_ids = fields.One2many(
        'bcm.client.contact',
        'client_id',
        string='Contacts'
    )
    
    vault_ids = fields.One2many(
        'bcm.client.vault',
        'client_id', 
        string='Context Vault'
    )
    
    appkey_ids = fields.One2many(
        'bcm.client.appkey',
        'client_id',
        string='API Keys'
    )
    
    # Вычисляемые поля для Smart Buttons
    contact_count = fields.Integer(
        compute='_compute_counts',
        string='Contacts'
    )
    
    vault_count = fields.Integer(
        compute='_compute_counts', 
        string='Context Records'
    )
    
    appkey_count = fields.Integer(
        compute='_compute_counts',
        string='API Keys'
    )
    
    # Связи с BCM объектами
    process_count = fields.Integer(
        compute='_compute_bcm_counts',
        string='Business Processes'
    )
    
    bia_count = fields.Integer(
        compute='_compute_bcm_counts',
        string='BIA Analyses'
    )
    
    plan_count = fields.Integer(
        compute='_compute_bcm_counts',
        string='BC Plans'
    )
    
    incident_count = fields.Integer(
        compute='_compute_bcm_counts',
        string='Incidents'
    )
    
    # Метрики клиента
    bia_coverage = fields.Float(
        compute='_compute_bcm_metrics',
        string='BIA Coverage %',
        help='Percentage of business processes covered by BIA'
    )
    
    plans_freshness = fields.Integer(
        compute='_compute_bcm_metrics',
        string='Plans Freshness (days)',
        help='Average age of business continuity plans in days'
    )
    
    open_findings = fields.Integer(
        compute='_compute_bcm_metrics',
        string='Open Findings',
        help='Number of open audit findings'
    )
    
    @api.depends('contact_ids', 'vault_ids', 'appkey_ids')
    def _compute_counts(self):
        for record in self:
            record.contact_count = len(record.contact_ids)
            record.vault_count = len(record.vault_ids)
            record.appkey_count = len(record.appkey_ids)
    
    def _compute_bcm_counts(self):
        """Вычисление количества связанных BCM объектов"""
        for record in self:
            # Подсчет бизнес-процессов
            BusinessProcess = self.env.get('bcm.business.process')
            if BusinessProcess:
                record.process_count = BusinessProcess.search_count([
                    ('company_id', '=', record.company_id.id)
                ])
            else:
                record.process_count = 0
            
            # Подсчет BIA анализов
            BiaAnalysis = self.env.get('bcm.bia.analysis')
            if BiaAnalysis:
                record.bia_count = BiaAnalysis.search_count([
                    ('company_id', '=', record.company_id.id)
                ])
            else:
                record.bia_count = 0
            
            # Подсчет планов
            BcmPlan = self.env.get('bcm.plan')
            if BcmPlan:
                record.plan_count = BcmPlan.search_count([
                    ('company_id', '=', record.company_id.id)
                ])
            else:
                record.plan_count = 0
            
            # Подсчет инцидентов
            BcmIncident = self.env.get('bcm.incident')
            if BcmIncident:
                record.incident_count = BcmIncident.search_count([
                    ('company_id', '=', record.company_id.id)
                ])
            else:
                record.incident_count = 0
    
    def _compute_bcm_metrics(self):
        """Вычисление метрик BCM для клиента"""
        for record in self:
            # TODO: Интеграция с BCM модулями для расчета метрик
            record.bia_coverage = 0.0
            record.plans_freshness = 0
            record.open_findings = 0
    
    @api.model
    def create(self, vals):
        """Создание клиента с уведомлением AI Orchestrator"""
        client = super().create(vals)
        
        # Отправить событие в AI Orchestrator
        try:
            self._notify_ai_orchestrator('client.created', {
                'client_id': client.id,
                'company_id': client.company_id.id,
                'name': client.name,
                'sector': client.sector,
                'onboarding_stage': client.onboarding_stage
            })
        except Exception as e:
            _logger.warning(f"Failed to notify AI Orchestrator about client creation: {e}")
            
        return client
    
    def write(self, vals):
        """Обновление клиента с уведомлением AI Orchestrator"""
        result = super().write(vals)
        
        # Отправить событие об изменении
        if any(key in vals for key in ['name', 'sector', 'onboarding_stage', 'status']):
            try:
                self._notify_ai_orchestrator('client.updated', {
                    'client_id': self.id,
                    'company_id': self.company_id.id,
                    'changes': list(vals.keys())
                })
            except Exception as e:
                _logger.warning(f"Failed to notify AI Orchestrator about client update: {e}")
                
        return result
    
    def action_archive_client(self):
        """Архивирование клиента"""
        self.write({'status': 'archived'})
        
        try:
            self._notify_ai_orchestrator('client.archived', {
                'client_id': self.id,
                'company_id': self.company_id.id
            })
        except Exception as e:
            _logger.warning(f"Failed to notify AI Orchestrator about client archival: {e}")
    
    def action_reindex_context(self):
        """Переиндексация контекста клиента в AI Orchestrator"""
        self.ensure_one()
        
        try:
            # Вызов AI Orchestrator для переиндексации
            self._call_ai_orchestrator_reindex()
            
            self.message_post(
                body=_('Client context successfully reindexed in AI system'),
                message_type='notification'
            )
        except Exception as e:
            _logger.error(f"Failed to reindex client context: {e}")
            raise ValidationError(_('Failed to reindex context: %s') % str(e))
    
    def _notify_ai_orchestrator(self, event_type, payload):
        """Отправка уведомления в AI Orchestrator"""
        # TODO: Реализация webhook в AI Orchestrator
        _logger.info(f"AI Orchestrator event: {event_type}, payload: {payload}")
    
    def _call_ai_orchestrator_reindex(self):
        """Вызов AI Orchestrator для переиндексации"""
        # TODO: Реализация вызова POST /clients/{id}/index
        _logger.info(f"Reindexing context for client {self.id}")
    
    # Smart Button Actions
    def action_view_contacts(self):
        """Открыть контакты клиента"""
        return {
            'name': _('Client Contacts'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.client.contact',
            'view_mode': 'list,form',
            'domain': [('client_id', '=', self.id)],
            'context': {'default_client_id': self.id}
        }
    
    def action_view_vault(self):
        """Открыть контекст клиента"""
        return {
            'name': _('Client Context'),
            'type': 'ir.actions.act_window', 
            'res_model': 'bcm.client.vault',
            'view_mode': 'list,form',
            'domain': [('client_id', '=', self.id)],
            'context': {'default_client_id': self.id}
        }
    
    def action_view_appkeys(self):
        """Открыть API ключи клиента"""
        return {
            'name': _('API Keys'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.client.appkey', 
            'view_mode': 'list,form',
            'domain': [('client_id', '=', self.id)],
            'context': {'default_client_id': self.id}
        }
    
    def action_view_processes(self):
        """Открыть бизнес-процессы клиента"""
        return {
            'name': _('Business Processes'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.business.process',
            'view_mode': 'list,form',
            'domain': [('company_id', '=', self.company_id.id)],
            'context': {'default_company_id': self.company_id.id}
        }
    
    def action_view_bia(self):
        """Открыть BIA анализы клиента"""
        return {
            'name': _('BIA Analyses'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.bia.analysis',
            'view_mode': 'list,form',
            'domain': [('company_id', '=', self.company_id.id)],
            'context': {'default_company_id': self.company_id.id}
        }
    
    def action_view_plans(self):
        """Открыть планы непрерывности клиента"""
        return {
            'name': _('Business Continuity Plans'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.plan',
            'view_mode': 'list,form',
            'domain': [('company_id', '=', self.company_id.id)],
            'context': {'default_company_id': self.company_id.id}
        }
    
    def action_view_incidents(self):
        """Открыть инциденты клиента"""
        return {
            'name': _('Incidents'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.incident',
            'view_mode': 'list,form',
            'domain': [('company_id', '=', self.company_id.id)],
            'context': {'default_company_id': self.company_id.id}
        }
