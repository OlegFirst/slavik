# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging

_logger = logging.getLogger(__name__)


class BCMConsultationSession(models.Model):
    _name = 'bcm.ai.consultation.session'
    _description = 'BCM AI Consultation Session - Сессия консультации'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    name = fields.Char(
        string='Название сессии',
        required=True,
        default=lambda self: f'Консультация {fields.Datetime.now().strftime("%d.%m.%Y %H:%M")}'
    )

    consultant_id = fields.Many2one(
        'bcm.ai.consultant',
        string='AI Консультант',
        required=True,
        ondelete='cascade'
    )

    bcm_client_id = fields.Many2one(
        'bcm.client',
        string='BCM Client',
        required=True
    )

    # Статус сессии
    state = fields.Selection([
        ('draft', 'Черновик'),
        ('active', 'Активная'),
        ('completed', 'Завершена'),
        ('archived', 'Архивирована'),
    ], string='Статус', default='draft', tracking=True)

    # Сообщения в сессии
    message_ids = fields.One2many(
        'bcm.ai.consultation.message',
        'session_id',
        string='Сообщения'
    )

    # Тема и контекст
    topic = fields.Char(
        string='Тема консультации',
        help='Основная тема или вопрос консультации'
    )

    context_type = fields.Selection([
        ('general', 'Общие вопросы BCM'),
        ('risk_assessment', 'Оценка рисков'),
        ('bcp_development', 'Разработка планов'),
        ('incident_response', 'Реагирование на инциденты'),
        ('compliance', 'Соответствие требованиям'),
        ('training', 'Обучение персонала'),
    ], string='Контекст', default='general')

    # Рейтинг и обратная связь
    rating = fields.Selection([
        ('1', '1 - Очень плохо'),
        ('2', '2 - Плохо'),
        ('3', '3 - Удовлетворительно'),
        ('4', '4 - Хорошо'),
        ('5', '5 - Отлично'),
    ], string='Рейтинг')

    feedback = fields.Text(
        string='Обратная связь',
        help='Комментарии пользователя о качестве консультации'
    )

    # Статистика
    message_count = fields.Integer(
        string='Количество сообщений',
        compute='_compute_statistics',
        store=True
    )

    duration_minutes = fields.Float(
        string='Длительность (мин)',
        compute='_compute_duration',
        store=True
    )

    # Экспорт
    export_format = fields.Selection([
        ('pdf', 'PDF'),
        ('docx', 'Word документ'),
        ('txt', 'Текстовый файл'),
    ], string='Формат экспорта', default='pdf')

    # Системные поля
    start_date = fields.Datetime(
        string='Начало сессии',
        default=fields.Datetime.now
    )

    end_date = fields.Datetime(
        string='Окончание сессии'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Компания',
        default=lambda self: self.env.company,
        required=True
    )

    @api.depends('message_ids')
    def _compute_statistics(self):
        """Вычисление статистики сессии"""
        for session in self:
            session.message_count = len(session.message_ids)

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        """Вычисление длительности сессии"""
        for session in self:
            if session.start_date and session.end_date:
                delta = session.end_date - session.start_date
                session.duration_minutes = delta.total_seconds() / 60
            else:
                session.duration_minutes = 0.0

    def action_start_session(self):
        """Начало сессии"""
        self.ensure_one()
        self.write({
            'state': 'active',
            'start_date': fields.Datetime.now()
        })

    def action_complete_session(self):
        """Завершение сессии"""
        self.ensure_one()
        self.write({
            'state': 'completed',
            'end_date': fields.Datetime.now()
        })

    def action_export_session(self):
        """Экспорт диалога сессии"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Экспорт консультации',
            'res_model': 'bcm.ai.consultation.export.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_session_id': self.id}
        }

    def send_message(self, message_text, message_type='user'):
        """Отправка сообщения в сессию"""
        self.ensure_one()

        # Создание сообщения пользователя
        user_message = self.env['bcm.ai.consultation.message'].create({
            'session_id': self.id,
            'message_type': message_type,
            'content': message_text,
            'sender': self.env.user.name,
        })

        # Если это сообщение пользователя, получаем ответ AI
        if message_type == 'user':
            ai_response = self.consultant_id.get_ai_response(
                message_text,
                context=self._get_session_context()
            )

            # Создание ответного сообщения AI
            ai_message = self.env['bcm.ai.consultation.message'].create({
                'session_id': self.id,
                'message_type': 'ai',
                'content': ai_response.get('response', 'Извините, произошла ошибка'),
                'sender': self.consultant_id.name,
                'confidence': ai_response.get('confidence', 0.0),
                'metadata': json.dumps(ai_response, ensure_ascii=False),
            })

            return ai_message

        return user_message

    def _get_session_context(self):
        """Получение контекста сессии для AI"""
        return {
            'client_name': self.bcm_client_id.name,
            'topic': self.topic,
            'context_type': self.context_type,
            'previous_messages': len(self.message_ids),
            'session_duration': self.duration_minutes,
        }


class BCMConsultationMessage(models.Model):
    _name = 'bcm.ai.consultation.message'
    _description = 'BCM AI Consultation Message - Сообщение в консультации'
    _order = 'sequence, create_date asc'

    sequence = fields.Integer(
        string='Порядок',
        default=10,
        help='Порядок сообщения в сессии'
    )

    session_id = fields.Many2one(
        'bcm.ai.consultation.session',
        string='Сессия',
        required=True,
        ondelete='cascade'
    )

    message_type = fields.Selection([
        ('user', 'Пользователь'),
        ('ai', 'AI Консультант'),
        ('system', 'Система'),
    ], string='Тип сообщения', required=True)

    content = fields.Text(
        string='Содержимое',
        required=True
    )

    sender = fields.Char(
        string='Отправитель',
        required=True
    )

    # AI-специфичные поля
    confidence = fields.Float(
        string='Уверенность AI',
        help='Уровень уверенности AI в ответе (0.0 - 1.0)'
    )

    metadata = fields.Text(
        string='Метаданные',
        help='JSON с дополнительными данными от AI'
    )

    # Реакции пользователя
    is_helpful = fields.Boolean(
        string='Полезно',
        help='Отметка пользователя о полезности ответа'
    )

    user_rating = fields.Selection([
        ('1', '👎 Плохо'),
        ('2', '👍 Хорошо'),
        ('3', '⭐ Отлично'),
    ], string='Оценка пользователя')

    create_date = fields.Datetime(
        string='Время сообщения',
        default=fields.Datetime.now,
        readonly=True
    )