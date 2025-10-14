# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class BcmPortalDashboard(models.Model):
    _name = 'bcm.portal.dashboard'
    _description = 'BCM Portal Dashboard Configuration'
    
    # Связи
    client_id = fields.Many2one(
        'bcm.client',
        string='Client',
        required=True, index=True,
        ondelete='cascade'
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True, index=True,
        default=lambda self: self.env.user
    )
    
    company_id = fields.Many2one(
        related='client_id.company_id',
        string='Company',
        store=True,
        readonly=True
    )
    
    # Настройки дашборда
    name = fields.Char(
        string='Dashboard Name',
        required=True, index=True,
        default='My BCM Dashboard'
    )
    
    layout = fields.Selection([
        ('standard', 'Standard Layout'),
        ('compact', 'Compact Layout'),
        ('detailed', 'Detailed Layout')
    ], string='Layout', default='standard')
    
    # Виджеты дашборда
    show_bia_coverage = fields.Boolean(
        string='Show BIA Coverage',
        default=True
    )
    
    show_plans_freshness = fields.Boolean(
        string='Show Plans Freshness',
        default=True
    )
    
    show_open_findings = fields.Boolean(
        string='Show Open Findings',
        default=True
    )
    
    show_recent_incidents = fields.Boolean(
        string='Show Recent Incidents',
        default=True
    )
    
    show_upcoming_exercises = fields.Boolean(
        string='Show Upcoming Exercises',
        default=True
    )
    
    show_training_progress = fields.Boolean(
        string='Show Training Progress',
        default=True
    )
    
    show_ai_recommendations = fields.Boolean(
        string='Show AI Recommendations',
        default=True
    )
    
    # Настройки уведомлений
    email_notifications = fields.Boolean(
        string='Email Notifications',
        default=True
    )
    
    notification_frequency = fields.Selection([
        ('realtime', 'Real-time'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Summary'),
        ('monthly', 'Monthly Report')
    ], string='Notification Frequency', default='daily')
    
    # Персонализация
    favorite_sections = fields.Many2many(
        'bcm.portal.section',
        string='Favorite Sections'
    )
    
    quick_actions = fields.Text(
        string='Quick Actions Config',
        default='["upload_evidence", "request_audit", "schedule_exercise"]',
        help='JSON array of enabled quick actions'
    )
    
    # Метаданные
    last_accessed = fields.Datetime(
        string='Last Accessed',
        readonly=True
    )
    
    access_count = fields.Integer(
        string='Access Count',
        default=0,
        readonly=True
    )
    
    @api.model
    def get_or_create_dashboard(self, client_id):
        """Получить или создать дашборд для клиента и пользователя"""
        dashboard = self.search([
            ('client_id', '=', client_id),
            ('user_id', '=', self.env.user.id)
        ], limit=1)
        
        if not dashboard:
            dashboard = self.create({
                'client_id': client_id,
                'user_id': self.env.user.id,
                'name': f'{self.env.user.name} BCM Dashboard',
            })
        
        # Обновить статистику доступа
        dashboard.sudo().write({
            'last_accessed': fields.Datetime.now(),
            'access_count': dashboard.access_count + 1
        })
        
        return dashboard
    
    def get_enabled_widgets(self):
        """Получить список включенных виджетов"""
        self.ensure_one()
        
        widgets = []
        widget_fields = [
            ('bia_coverage', 'BIA Coverage'),
            ('plans_freshness', 'Plans Freshness'), 
            ('open_findings', 'Open Findings'),
            ('recent_incidents', 'Recent Incidents'),
            ('upcoming_exercises', 'Upcoming Exercises'),
            ('training_progress', 'Training Progress'),
            ('ai_recommendations', 'AI Recommendations'),
        ]
        
        for field_name, widget_name in widget_fields:
            if getattr(self, f'show_{field_name}'):
                widgets.append({
                    'name': field_name,
                    'title': widget_name,
                    'enabled': True
                })
        
        return widgets

class BcmPortalSection(models.Model):
    _name = 'bcm.portal.section'
    _description = 'BCM Portal Sections'
    
    name = fields.Char(string='Section Name', required=True)
    code = fields.Char(string='Section Code', required=True)
    description = fields.Text(string='Description')
    icon = fields.Char(string='Icon Class')
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(default=True)
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Section code must be unique!')
    ]
