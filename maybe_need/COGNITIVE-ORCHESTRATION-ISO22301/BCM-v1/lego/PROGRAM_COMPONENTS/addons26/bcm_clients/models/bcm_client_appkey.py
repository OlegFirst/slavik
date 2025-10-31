# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import hashlib
import secrets
import logging

_logger = logging.getLogger(__name__)

class BcmScope(models.Model):
    _name = 'bcm.scope'
    _description = 'BCM API Scope'
    
    name = fields.Char(string='Scope Name', required=True)
    description = fields.Text(string='Description')
    
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Scope name must be unique!')
    ]

class BcmClientAppkey(models.Model):
    _name = 'bcm.client.appkey'
    _description = 'BCM Client API Key'
    _inherit = ['mail.thread']
    _order = 'client_id, created_at desc'
    
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
    
    # Основная информация о ключе
    name = fields.Char(
        string='Key Name',
        required=True, index=True,
        help='Descriptive name for this API key'
    )
    
    description = fields.Text(
        string='Description',
        help='Purpose and usage of this API key'
    )
    
    # Хеш токена (НЕ сам токен)
    token_hash = fields.Char(
        string='Token Hash',
        readonly=True,
        help='SHA-256 hash of the API token'
    )
    
    # Временный токен для отображения (только при создании)
    token_display = fields.Char(
        string='API Token',
        compute='_compute_token_display',
        help='API Token (visible only once after creation)'
    )
    
    # Области доступа
    scope_ids = fields.Many2many(
        'bcm.scope',
        string='Access Scopes',
        help='API access scopes for this key'
    )
    
    # Сроки действия
    created_at = fields.Datetime(
        string='Created At',
        default=fields.Datetime.now,
        readonly=True
    )
    
    valid_until = fields.Datetime(
        string='Valid Until',
        required=True, index=True,
        help='Expiration date for this API key'
    )
    
    last_used = fields.Datetime(
        string='Last Used',
        readonly=True,
        help='Last time this API key was used'
    )
    
    # Статус
    revoked = fields.Boolean(
        string='Revoked',
        default=False,
        tracking=True,
        help='Whether this API key is revoked'
    )
    
    revoke_reason = fields.Text(
        string='Revoke Reason',
        help='Reason for revoking this API key'
    )
    
    # Статистика использования
    usage_count = fields.Integer(
        string='Usage Count',
        default=0,
        readonly=True,
        help='Number of times this API key was used'
    )
    
    rate_limit = fields.Integer(
        string='Rate Limit (per hour)',
        default=1000,
        help='Maximum requests per hour for this key'
    )
    
    # IP restrictions
    allowed_ips = fields.Text(
        string='Allowed IPs',
        help='Comma-separated list of allowed IP addresses (empty = all IPs)'
    )
    
    active = fields.Boolean(default=True)
    
    # Вычисляемые поля
    is_expired = fields.Boolean(
        compute='_compute_status',
        string='Expired',
        store=True
    )
    
    is_valid = fields.Boolean(
        compute='_compute_status',
        string='Valid',
        store=True
    )
    
    status_display = fields.Char(
        compute='_compute_status',
        string='Status'
    )
    
    @api.depends('revoked', 'valid_until')
    def _compute_status(self):
        now = fields.Datetime.now()
        for record in self:
            record.is_expired = record.valid_until < now
            record.is_valid = not record.revoked and not record.is_expired
            
            if record.revoked:
                record.status_display = 'Revoked'
            elif record.is_expired:
                record.status_display = 'Expired'
            else:
                record.status_display = 'Active'
    
    def _compute_token_display(self):
        """Показать токен только при создании"""
        for record in self:
            # Токен показывается только через контекст после создания
            record.token_display = self.env.context.get('show_token', '') if record.id == self.env.context.get('new_key_id') else ''
    
    @api.model
    def create(self, vals):
        """Создание API ключа с генерацией токена"""
        # Генерировать случайный токен
        token = self._generate_token()
        vals['token_hash'] = self._hash_token(token)
        
        api_key = super().create(vals)
        
        # Сохранить токен в контексте для однократного показа
        self.env.context = dict(self.env.context, show_token=token, new_key_id=api_key.id)
        
        _logger.info(f"Created API key {api_key.name} for client {api_key.client_id.name}")
        
        return api_key
    
    def write(self, vals):
        """Обновление с логированием изменений"""
        if 'revoked' in vals and vals['revoked']:
            vals['revoke_reason'] = vals.get('revoke_reason', 'Manually revoked')
            
        result = super().write(vals)
        
        if vals.get('revoked'):
            for record in self:
                _logger.info(f"Revoked API key {record.name} for client {record.client_id.name}")
                
        return result
    
    def _generate_token(self):
        """Генерация случайного токена"""
        return f"bcm_{secrets.token_urlsafe(32)}"
    
    def _hash_token(self, token):
        """Хеширование токена для безопасного хранения"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def verify_token(self, token):
        """Проверка токена"""
        self.ensure_one()
        
        if self.revoked or self.is_expired:
            return False
            
        return self.token_hash == self._hash_token(token)
    
    def action_revoke(self):
        """Отозвать API ключ"""
        self.ensure_one()
        
        if self.revoked:
            raise ValidationError(_('API key is already revoked'))
        
        return {
            'name': _('Revoke API Key'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.client.appkey.revoke.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_appkey_id': self.id}
        }
    
    def action_regenerate(self):
        """Перегенерировать токен"""
        self.ensure_one()
        
        if self.revoked:
            raise ValidationError(_('Cannot regenerate token for revoked API key'))
        
        # Создать новый ключ с теми же настройками
        new_vals = {
            'client_id': self.client_id.id,
            'name': self.name + ' (Regenerated)',
            'description': self.description,
            'scope_ids': [(6, 0, self.scope_ids.ids)],
            'valid_until': self.valid_until,
            'rate_limit': self.rate_limit,
            'allowed_ips': self.allowed_ips
        }
        
        new_key = self.create(new_vals)
        
        # Отозвать старый ключ
        self.write({
            'revoked': True,
            'revoke_reason': 'Regenerated'
        })
        
        return {
            'name': _('New API Key'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.client.appkey',
            'res_id': new_key.id,
            'view_mode': 'form',
            'target': 'current'
        }
    
    def record_usage(self, request_ip=None):
        """Записать использование API ключа"""
        self.ensure_one()
        
        self.write({
            'usage_count': self.usage_count + 1,
            'last_used': fields.Datetime.now()
        })
        
        # TODO: Записать детальную статистику использования
        _logger.debug(f"API key {self.name} used from IP {request_ip}")
    
    def check_rate_limit(self):
        """Проверить лимит запросов"""
        self.ensure_one()
        
        # TODO: Реализация проверки rate limit
        # Можно использовать Redis или простой подсчет в базе
        return True
    
    def check_ip_restriction(self, request_ip):
        """Проверить IP ограничения"""
        self.ensure_one()
        
        if not self.allowed_ips:
            return True
            
        allowed_list = [ip.strip() for ip in self.allowed_ips.split(',')]
        return request_ip in allowed_list
