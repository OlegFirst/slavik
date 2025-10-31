# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class BCMAIConsultant(models.Model):
    _name = 'bcm.ai.consultant'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'BCM AI Consultant - Интеллектуальный консультант по BCM'
    _order = 'create_date desc'
    _rec_name = 'name'

    # Основные поля
    name = fields.Char(
        string='Название консультанта',
        required=True,
        default='AI BCM Консультант'
    )

    bcm_client_id = fields.Many2one(
        'bcm.client',
        string='BCM Client',
        required=True,
        help='Клиент BCM для которого работает консультант'
    )

    # Тип AI и конфигурация
    ai_type = fields.Selection([
        ('chatgpt4', 'ChatGPT-4'),
        ('claude', 'Claude AI'),
        ('gemini', 'Google Gemini'),
        ('local', 'Локальная модель'),
    ], string='Тип AI', default='claude', required=True)

    ai_config = fields.Text(
        string='Конфигурация AI',
        help='JSON конфигурация для подключения к AI сервису'
    )

    # Языки и контекст
    languages = fields.Selection([
        ('ru', 'Русский'),
        ('en', 'English'),
        ('multi', 'Многоязычный'),
    ], string='Языки', default='multi', required=True)

    context_data = fields.Text(
        string='Контекстные данные',
        help='JSON с информацией об организации для персонализации ответов'
    )

    # База знаний
    knowledge_base_ids = fields.One2many(
        'bcm.ai.knowledge.base',
        'consultant_id',
        string='База знаний',
        help='Связанная база знаний ISO 22301 и BCM практик'
    )

    # Сессии консультаций
    consultation_session_ids = fields.One2many(
        'bcm.ai.consultation.session',
        'consultant_id',
        string='Сессии консультаций',
        help='История консультационных сессий'
    )

    # Статистика
    total_consultations = fields.Integer(
        string='Всего консультаций',
        compute='_compute_statistics',
        store=True
    )

    average_rating = fields.Float(
        string='Средний рейтинг',
        compute='_compute_statistics',
        store=True
    )

    last_consultation_date = fields.Datetime(
        string='Последняя консультация',
        compute='_compute_statistics',
        store=True
    )

    # Состояние и настройки
    is_active = fields.Boolean(
        string='Активен',
        default=True,
        help='Активен ли консультант для новых сессий'
    )

    auto_learn = fields.Boolean(
        string='Автообучение',
        default=True,
        help='Автоматическое обучение на основе обратной связи'
    )

    response_template = fields.Text(
        string='Шаблон ответов',
        help='Базовый шаблон для форматирования ответов консультанта'
    )

    # Системные поля
    company_id = fields.Many2one(
        'res.company',
        string='Компания',
        default=lambda self: self.env.company,
        required=True
    )

    @api.depends('consultation_session_ids', 'consultation_session_ids.rating')
    def _compute_statistics(self):
        """Вычисление статистики консультаций"""
        for consultant in self:
            sessions = consultant.consultation_session_ids
            consultant.total_consultations = len(sessions)

            if sessions:
                ratings = sessions.filtered('rating').mapped('rating')
                consultant.average_rating = sum(ratings) / len(ratings) if ratings else 0.0
                consultant.last_consultation_date = max(sessions.mapped('create_date'))
            else:
                consultant.average_rating = 0.0
                consultant.last_consultation_date = False

    def action_start_consultation(self):
        """Открытие новой сессии консультации"""
        self.ensure_one()
        if not self.is_active:
            raise UserError(_('Консультант не активен'))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Новая консультация',
            'res_model': 'bcm.ai.consultation.session',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_consultant_id': self.id,
                'default_bcm_client_id': self.bcm_client_id.id,
            }
        }

    def action_view_knowledge_base(self):
        """Просмотр базы знаний"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'База знаний',
            'res_model': 'bcm.ai.knowledge.base',
            'view_mode': 'list,form',
            'domain': [('consultant_id', '=', self.id)],
            'context': {'default_consultant_id': self.id}
        }

    def action_consultation_history(self):
        """Просмотр истории консультаций"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'История консультаций',
            'res_model': 'bcm.ai.consultation.session',
            'view_mode': 'list,form',
            'domain': [('consultant_id', '=', self.id)],
            'context': {'default_consultant_id': self.id}
        }

    def get_ai_response(self, question, context=None):
        """Получение ответа от AI (заглушка для интеграции)"""
        self.ensure_one()
        # Здесь должна быть интеграция с реальными AI сервисами
        return {
            'response': f'Ответ AI консультанта на вопрос: {question}',
            'confidence': 0.85,
            'sources': [],
            'suggestions': []
        }

    @api.model
    def create_default_consultant(self, bcm_client_id):
        """Создание консультанта по умолчанию для нового клиента"""
        bcm_client = self.env['bcm.client'].browse(bcm_client_id)
        consultant = self.create({
            'name': f'AI Консультант - {bcm_client.name}',
            'bcm_client_id': bcm_client_id,
            'ai_type': 'claude',
            'languages': 'multi',
            'context_data': json.dumps({
                'organization_name': bcm_client.name,
                'industry': bcm_client.industry if hasattr(bcm_client, 'industry') else '',
                'created_date': str(datetime.now()),
            }, ensure_ascii=False, indent=2)
        })

        _logger.info(f"Создан AI консультант для клиента {bcm_client.name}")
        return consultant