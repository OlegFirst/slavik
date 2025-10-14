# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json
import logging

_logger = logging.getLogger(__name__)

class BcmClientContact(models.Model):
    _name = 'bcm.client.contact'
    _description = 'BCM Client Contact'
    _inherit = ['mail.thread']
    _order = 'client_id, role, name'
    
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
    
    # Связь с пользователем
    user_id = fields.Many2one(
        'res.users',
        string='User Account',
        help='Odoo user account (can be portal user)'
    )
    
    # Основная информация
    name = fields.Char(
        compute='_compute_name',
        string='Contact Name',
        store=True
    )
    
    email = fields.Char(
        related='user_id.email',
        string='Email',
        readonly=True
    )
    
    phone = fields.Char(
        related='user_id.phone', 
        string='Phone',
        readonly=True
    )
    
    # Роль в BCM
    role = fields.Selection([
        ('bcm_lead', 'BCM Lead'),
        ('cio', 'CIO/IT Director'),
        ('qa', 'Quality Assurance'),
        ('auditor', 'Internal Auditor'),
        ('viewer', 'Viewer'),
        ('admin', 'Client Administrator'),
        ('coordinator', 'BCM Coordinator'),
        ('emergency', 'Emergency Response Team')
    ], string='BCM Role', required=True, tracking=True)
    
    # Настройки уведомлений
    notify_prefs = fields.Text(
        string='Notification Preferences',
        default='{}',
        help='JSON with notification preferences'
    )
    
    # Статус
    active = fields.Boolean(default=True)
    
    is_primary = fields.Boolean(
        string='Primary Contact',
        default=False,
        help='Primary contact for this client'
    )
    
    last_login = fields.Datetime(
        related='user_id.login_date',
        string='Last Login',
        readonly=True
    )
    
    @api.depends('user_id.name', 'user_id.email')
    def _compute_name(self):
        for record in self:
            if record.user_id:
                record.name = record.user_id.name or record.user_id.email or 'Unknown'
            else:
                record.name = 'No User Account'
    
    @api.model
    def create(self, vals):
        """Создание контакта с проверкой primary contact"""
        contact = super().create(vals)
        
        if contact.is_primary:
            # Убрать primary статус у других контактов этого клиента
            other_contacts = self.search([
                ('client_id', '=', contact.client_id.id),
                ('id', '!=', contact.id),
                ('is_primary', '=', True)
            ])
            other_contacts.write({'is_primary': False})
            
        return contact
    
    def write(self, vals):
        """Обновление контакта с проверкой primary contact"""
        result = super().write(vals)
        
        if vals.get('is_primary'):
            for record in self:
                # Убрать primary статус у других контактов этого клиента
                other_contacts = self.search([
                    ('client_id', '=', record.client_id.id),
                    ('id', '!=', record.id),
                    ('is_primary', '=', True)
                ])
                other_contacts.write({'is_primary': False})
                
        return result
    
    def get_notification_preferences(self):
        """Получить настройки уведомлений как словарь"""
        self.ensure_one()
        try:
            return json.loads(self.notify_prefs or '{}')
        except json.JSONDecodeError:
            return {}
    
    def set_notification_preferences(self, prefs_dict):
        """Установить настройки уведомлений из словаря"""
        self.ensure_one()
        self.notify_prefs = json.dumps(prefs_dict)
    
    def action_create_user_account(self):
        """Создать пользовательский аккаунт для контакта"""
        self.ensure_one()
        
        if self.user_id:
            raise ValidationError(_('User account already exists for this contact'))
            
        if not self.email:
            raise ValidationError(_('Email is required to create user account'))
        
        # Создать portal пользователя
        user_vals = {
            'name': self.name or 'BCM User',
            'login': self.email,
            'email': self.email,
            'company_id': self.company_id.id,
            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
            'active': True
        }
        
        user = self.env['res.users'].create(user_vals)
        self.user_id = user.id
        
        # Отправить приглашение
        user.action_reset_password()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('User Account Created'),
                'message': _('User account created and invitation sent to %s') % self.email,
                'type': 'success'
            }
        }
    
    def action_reset_password(self):
        """Сбросить пароль пользователя"""
        self.ensure_one()
        
        if not self.user_id:
            raise ValidationError(_('No user account exists for this contact'))
            
        self.user_id.action_reset_password()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Password Reset'),
                'message': _('Password reset email sent to %s') % self.email,
                'type': 'success'
            }
        }
