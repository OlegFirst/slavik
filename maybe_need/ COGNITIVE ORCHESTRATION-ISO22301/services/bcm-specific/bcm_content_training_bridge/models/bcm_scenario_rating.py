# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class BcmScenarioRating(models.Model):
    _name = 'bcm.scenario.rating'
    _description = 'BCM Scenario Rating by Users'
    _order = 'created_at desc'
    _rec_name = 'scenario_id'
    
    # Уникальность: один пользователь - один рейтинг на сценарий
    _sql_constraints = [
        ('unique_user_scenario', 'unique(scenario_id, user_id)', 
         'You can only rate each scenario once!')
    ]
    
    # Основные поля согласно ТЗ
    scenario_id = fields.Many2one(
        'bcm.scenario',
        string='Scenario',
        required=True,
        ondelete='cascade'
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        default=lambda self: self.env.user
    )
    
    stars = fields.Selection([
        ('1', '1 Star - Very Poor'),
        ('2', '2 Stars - Poor'),
        ('3', '3 Stars - Fair'),
        ('4', '4 Stars - Good'),
        ('5', '5 Stars - Excellent')
    ], string='Rating', required=True)
    
    comment = fields.Text(
        string='Comment',
        help='Optional comment about the scenario'
    )
    
    created_at = fields.Datetime(
        string='Rating Date',
        default=fields.Datetime.now,
        readonly=True
    )
    
    # Детальная оценка (опционально)
    usability = fields.Selection([
        ('1', 'Very Difficult'),
        ('2', 'Difficult'),
        ('3', 'Moderate'),
        ('4', 'Easy'),
        ('5', 'Very Easy')
    ], string='Ease of Use')
    
    realism = fields.Selection([
        ('1', 'Unrealistic'),
        ('2', 'Somewhat Realistic'),
        ('3', 'Realistic'),
        ('4', 'Very Realistic'),
        ('5', 'Highly Realistic')
    ], string='Realism')
    
    educational_value = fields.Selection([
        ('1', 'No Value'),
        ('2', 'Limited Value'),
        ('3', 'Some Value'),
        ('4', 'Good Value'),
        ('5', 'Excellent Value')
    ], string='Educational Value')
    
    # Связанные поля для отображения
    scenario_title = fields.Char(
        related='scenario_id.title',
        string='Scenario Title',
        readonly=True
    )
    
    scenario_category = fields.Selection(
        related='scenario_id.category',
        string='Category',
        readonly=True
    )
    
    user_name = fields.Char(
        related='user_id.name',
        string='User Name',
        readonly=True
    )
    
    user_company = fields.Char(
        related='user_id.company_id.name',
        string='User Company',
        readonly=True
    )
    
    # Метаданные
    helpful_count = fields.Integer(
        string='Helpful Count',
        default=0,
        help='Number of users who found this rating helpful'
    )
    
    reported = fields.Boolean(
        string='Reported',
        default=False,
        help='Whether this rating was reported as inappropriate'
    )
    
    verified_user = fields.Boolean(
        string='Verified User',
        compute='_compute_verified_user',
        help='User has been verified or is from a trusted organization'
    )
    
    @api.depends('user_id')
    def _compute_verified_user(self):
        """Определить верифицированных пользователей"""
        for record in self:
            # TODO: Логика верификации пользователей
            # Например, пользователи с определенными группами или доменами email
            record.verified_user = record.user_id.has_group('base.group_user')
    
    @api.model
    def create(self, vals):
        """Создание рейтинга с проверками"""
        # Проверить что сценарий опубликован
        scenario = self.env['bcm.scenario'].browse(vals.get('scenario_id'))
        if scenario.status != 'published':
            raise ValidationError(_('You can only rate published scenarios'))
        
        # Проверить что пользователь не автор
        if scenario.author_user_id.id == vals.get('user_id', self.env.user.id):
            raise ValidationError(_('You cannot rate your own scenario'))
        
        rating = super().create(vals)
        
        # Уведомить автора сценария
        rating._notify_scenario_author()
        
        return rating
    
    def write(self, vals):
        """Обновление рейтинга"""
        # Можно изменить только свой рейтинг
        for record in self:
            if record.user_id != self.env.user:
                raise ValidationError(_('You can only edit your own ratings'))
        
        result = super().write(vals)
        
        # Обновить средний рейтинг сценария
        for record in self:
            record.scenario_id._compute_ratings()
        
        return result
    
    def unlink(self):
        """Удаление рейтинга"""
        # Можно удалить только свой рейтинг
        for record in self:
            if record.user_id != self.env.user and not self.env.user.has_group('base.group_system'):
                raise ValidationError(_('You can only delete your own ratings'))
        
        scenarios = self.mapped('scenario_id')
        result = super().unlink()
        
        # Пересчитать рейтинги для затронутых сценариев
        scenarios._compute_ratings()
        
        return result
    
    def action_mark_helpful(self):
        """Отметить рейтинг как полезный"""
        self.ensure_one()
        
        if self.user_id == self.env.user:
            raise ValidationError(_('You cannot mark your own rating as helpful'))
        
        # TODO: Реализовать таблицу helpful votes для предотвращения повторных голосов
        self.helpful_count += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Thank you!'),
                'message': _('You marked this rating as helpful'),
                'type': 'success'
            }
        }
    
    def action_report_inappropriate(self):
        """Пожаловаться на неуместный рейтинг"""
        self.ensure_one()
        
        if self.user_id == self.env.user:
            raise ValidationError(_('You cannot report your own rating'))
        
        self.reported = True
        
        # Уведомить модераторов
        moderators = self.env['res.users'].search([
            ('groups_id', 'in', [self.env.ref('bcm_scenario_hub.group_scenario_reviewer').id])
        ])
        
        for moderator in moderators:
            self.env['mail.activity'].create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': _('Review reported rating'),
                'note': _('Rating reported as inappropriate by %s') % self.env.user.name,
                'res_model': 'bcm.scenario.rating',
                'res_id': self.id,
                'user_id': moderator.id,
            })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Report Submitted'),
                'message': _('The rating has been reported for review'),
                'type': 'success'
            }
        }
    
    def _notify_scenario_author(self):
        """Уведомить автора сценария о новом рейтинге"""
        self.ensure_one()
        
        # Создать активность для автора
        self.scenario_id.activity_schedule(
            'mail.mail_activity_data_todo',
            user_id=self.scenario_id.author_user_id.id,
            summary=_('New rating for your scenario'),
            note=_('User %s rated your scenario "%s" with %s stars') % 
                 (self.user_name, self.scenario_title, self.stars)
        )
    
    @api.model
    def get_user_ratings(self, user_id=None):
        """Получить все рейтинги пользователя"""
        if user_id is None:
            user_id = self.env.user.id
        
        return self.search([('user_id', '=', user_id)])
    
    @api.model
    def get_top_rated_scenarios(self, limit=10, category=None):
        """Получить топ сценариев по рейтингу"""
        domain = [('scenario_id.status', '=', 'published')]
        
        if category:
            domain.append(('scenario_id.category', '=', category))
        
        # Группировка по сценариям с подсчетом среднего рейтинга
        ratings = self.read_group(
            domain=domain,
            fields=['scenario_id', 'stars'],
            groupby=['scenario_id'],
            limit=limit,
            orderby='stars desc'
        )
        
        result = []
        for group in ratings:
            if group['scenario_id']:
                scenario = self.env['bcm.scenario'].browse(group['scenario_id'][0])
                result.append({
                    'scenario': scenario,
                    'avg_rating': group['stars'],
                    'rating_count': group['scenario_id_count']
                })
        
        return result
