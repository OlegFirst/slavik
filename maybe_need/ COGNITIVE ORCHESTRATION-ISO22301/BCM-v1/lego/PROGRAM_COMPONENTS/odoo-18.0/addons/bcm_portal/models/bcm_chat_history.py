# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class BcmChatHistory(models.Model):
    _name = 'bcm.chat.history'
    _description = 'BCM AI Chat History'
    _order = 'create_date desc'
    _rec_name = 'user_message'
    
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
    
    # Содержимое чата
    user_message = fields.Text(
        string='User Message',
        required=True, index=True
    )
    
    ai_response = fields.Text(
        string='AI Response',
        required=True, index=True
    )
    
    session_id = fields.Char(
        string='Session ID',
        help='Browser session identifier'
    )
    
    # Метаданные
    response_time = fields.Float(
        string='Response Time (seconds)',
        help='Time taken to generate AI response'
    )
    
    tokens_used = fields.Integer(
        string='Tokens Used',
        help='Number of AI tokens consumed'
    )
    
    feedback_rating = fields.Selection([
        ('1', 'Very Poor'),
        ('2', 'Poor'),
        ('3', 'Fair'),
        ('4', 'Good'),
        ('5', 'Excellent')
    ], string='User Feedback')
    
    feedback_comment = fields.Text(
        string='Feedback Comment'
    )
    
    # Даты
    create_date = fields.Datetime(
        string='Created On',
        default=fields.Datetime.now,
        readonly=True
    )
    
    @api.model
    def get_recent_history(self, client_id, limit=10):
        """Получить недавнюю историю чата для клиента"""
        return self.search([
            ('client_id', '=', client_id),
            ('user_id', '=', self.env.user.id)
        ], limit=limit, order='create_date desc')
    
    @api.model
    def get_popular_queries(self, client_id=None, limit=5):
        """Получить популярные запросы"""
        domain = []
        if client_id:
            domain.append(('client_id', '=', client_id))
        
        # Группировка по похожим сообщениям (упрощенно)
        records = self.search(domain, limit=limit * 2)
        
        # TODO: Реализовать группировку по семантическому сходству
        # Пока просто возвращаем последние уникальные запросы
        seen_messages = set()
        unique_queries = []
        
        for record in records:
            message_key = record.user_message.lower()[:50]  # Первые 50 символов
            if message_key not in seen_messages:
                unique_queries.append(record)
                seen_messages.add(message_key)
                if len(unique_queries) >= limit:
                    break
        
        return unique_queries
    
    def action_provide_feedback(self):
        """Действие для предоставления обратной связи"""
        self.ensure_one()
        
        return {
            'name': 'Provide Feedback',
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.chat.feedback.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_chat_history_id': self.id}
        }
