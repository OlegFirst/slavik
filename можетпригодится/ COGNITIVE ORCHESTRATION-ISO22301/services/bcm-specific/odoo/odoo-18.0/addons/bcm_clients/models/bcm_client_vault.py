# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json
import logging

_logger = logging.getLogger(__name__)

class BcmClientVault(models.Model):
    _name = 'bcm.client.vault'
    _description = 'BCM Client Context Vault'
    _inherit = ['mail.thread']
    _order = 'client_id, updated_at desc'
    
    # Связь с клиентом
    client_id = fields.Many2one(
        'bcm.client',
        string='Client',
        required=True, index=True,
        ondelete='cascade'
    )
    
    company_id = fields.Many2one(
        related='client_id.company_id',
        string='Company',
        store=True,
        readonly=True
    )
    
    # Тип контекста
    context_type = fields.Selection([
        ('business_process', 'Business Process'),
        ('asset', 'Critical Asset'),
        ('system', 'IT System'),
        ('regulation', 'Regulatory Requirement'),
        ('stakeholder', 'Stakeholder Information'),
        ('risk', 'Risk Context'),
        ('integration', 'External Integration'),
        ('other', 'Other Context')
    ], string='Context Type', required=True)
    
    name = fields.Char(
        string='Context Name',
        required=True, index=True,
        help='Name or title of this context item'
    )
    
    description = fields.Text(
        string='Description',
        help='Detailed description of the context'
    )
    
    # Внешние ссылки
    external_refs = fields.Text(
        string='External References',
        default='{}',
        help='JSON with external system IDs (HIS/EMR/ERP/CMDB)'
    )
    
    # Уровень конфиденциальности
    sensitivity_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'), 
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Sensitivity Level', default='medium', required=True)
    
    # Векторное представление для AI (PostgreSQL pgvector)
    embedding = fields.Text(
        string='Vector Embedding',
        help='Vector representation for AI search (1536 dimensions)'
    )
    
    embedding_model = fields.Char(
        string='Embedding Model',
        default='text-embedding-ada-002',
        help='AI model used for embedding generation'
    )
    
    # Метаданные
    tags = fields.Char(
        string='Tags',
        help='Comma-separated tags for categorization'
    )
    
    source = fields.Selection([
        ('manual', 'Manual Entry'),
        ('import', 'Data Import'),
        ('api', 'API Integration'),
        ('ai_generated', 'AI Generated')
    ], string='Source', default='manual')
    
    # Даты
    created_at = fields.Datetime(
        string='Created At',
        default=fields.Datetime.now,
        readonly=True
    )
    
    updated_at = fields.Datetime(
        string='Updated At',
        default=fields.Datetime.now,
        tracking=True
    )
    
    # Статус индексации
    indexed = fields.Boolean(
        string='Indexed in AI',
        default=False,
        help='Whether this context is indexed in AI Orchestrator'
    )
    
    index_error = fields.Text(
        string='Indexing Error',
        help='Error message if indexing failed'
    )
    
    # Связанные объекты
    process_ids = fields.Many2many(
        'bcm.process',
        string='Related Business Processes'
    )
    
    active = fields.Boolean(default=True)
    
    @api.model
    def create(self, vals):
        """Создание контекста с автоматической индексацией"""
        vals['updated_at'] = fields.Datetime.now()
        vault_record = super().create(vals)
        
        # Запланировать индексацию
        vault_record._schedule_indexing()
        
        return vault_record
    
    def write(self, vals):
        """Обновление контекста с переиндексацией"""
        vals['updated_at'] = fields.Datetime.now()
        
        # Если изменили содержимое, нужна переиндексация
        content_fields = ['name', 'description', 'external_refs', 'tags']
        if any(field in vals for field in content_fields):
            vals['indexed'] = False
            vals['index_error'] = False
            
        result = super().write(vals)
        
        # Запланировать переиндексацию
        if not self.indexed:
            self._schedule_indexing()
            
        return result
    
    def get_external_references(self):
        """Получить внешние ссылки как словарь"""
        self.ensure_one()
        try:
            return json.loads(self.external_refs or '{}')
        except json.JSONDecodeError:
            return {}
    
    def set_external_references(self, refs_dict):
        """Установить внешние ссылки из словаря"""
        self.ensure_one()
        self.external_refs = json.dumps(refs_dict)
    
    def add_external_reference(self, system_name, ref_id):
        """Добавить внешнюю ссылку"""
        refs = self.get_external_references()
        refs[system_name] = ref_id
        self.set_external_references(refs)
    
    def _schedule_indexing(self):
        """Запланировать индексацию в AI Orchestrator"""
        # TODO: Реализация через cron job или прямой вызов
        self.env.ref('bcm_clients.cron_vault_indexing')._trigger()
        _logger.info(f"Scheduled indexing for vault record {self.id}")
    
    def action_reindex(self):
        """Принудительная переиндексация"""
        self.ensure_one()
        
        try:
            self._call_ai_orchestrator_index()
            
            self.write({
                'indexed': True,
                'index_error': False,
                'updated_at': fields.Datetime.now()
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Reindexing Success'),
                    'message': _('Context successfully reindexed in AI system'),
                    'type': 'success'
                }
            }
            
        except Exception as e:
            self.write({
                'indexed': False,
                'index_error': str(e)
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Reindexing Error'),
                    'message': _('Failed to reindex context: %s') % str(e),
                    'type': 'danger'
                }
            }
    
    def _call_ai_orchestrator_index(self):
        """Вызов AI Orchestrator для индексации"""
        # TODO: Реализация POST /clients/{client_id}/index
        payload = {
            'context_id': self.id,
            'context_type': self.context_type,
            'name': self.name,
            'description': self.description,
            'tags': self.tags,
            'sensitivity_level': self.sensitivity_level,
            'external_refs': self.get_external_references()
        }
        
        _logger.info(f"Indexing vault record {self.id}: {payload}")
        
        # Моковая генерация embedding (в production будет вызов API)
        import random
        mock_embedding = [random.random() for _ in range(1536)]
        self.embedding = json.dumps(mock_embedding)
    
    @api.model
    def cron_reindex_pending(self):
        """Cron job для переиндексации неиндексированных записей"""
        pending_records = self.search([('indexed', '=', False)])
        
        for record in pending_records:
            try:
                record._call_ai_orchestrator_index()
                record.write({
                    'indexed': True,
                    'index_error': False
                })
            except Exception as e:
                record.write({
                    'index_error': str(e)
                })
                _logger.error(f"Failed to index vault record {record.id}: {e}")
        
        _logger.info(f"Processed {len(pending_records)} pending vault records")
