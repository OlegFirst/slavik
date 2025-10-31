# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging

_logger = logging.getLogger(__name__)


class BCMAIKnowledgeBase(models.Model):
    _name = 'bcm.ai.knowledge.base'
    _description = 'BCM AI Knowledge Base - База знаний AI консультанта'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'
    _rec_name = 'name'

    name = fields.Char(
        string='Название',
        required=True
    )

    consultant_id = fields.Many2one(
        'bcm.ai.consultant',
        string='AI Консультант',
        required=True,
        ondelete='cascade'
    )

    # Категоризация
    category = fields.Selection([
        ('iso22301', 'ISO 22301 Standard'),
        ('best_practices', 'Лучшие практики'),
        ('procedures', 'Процедуры и инструкции'),
        ('templates', 'Шаблоны документов'),
        ('case_studies', 'Примеры из практики'),
        ('regulations', 'Нормативные требования'),
        ('industry_specific', 'Отраслевые знания'),
    ], string='Категория', required=True)

    knowledge_type = fields.Selection([
        ('text', 'Текстовый контент'),
        ('document', 'Документ'),
        ('template', 'Шаблон'),
        ('checklist', 'Чек-лист'),
        ('faq', 'Вопросы и ответы'),
    ], string='Тип знания', default='text', required=True)

    # Содержимое
    content = fields.Html(
        string='Содержимое',
        help='Основное содержимое знания'
    )

    summary = fields.Text(
        string='Краткое описание',
        help='Краткое описание для быстрого поиска'
    )

    keywords = fields.Char(
        string='Ключевые слова',
        help='Ключевые слова через запятую для поиска'
    )

    # Структурированные данные
    structured_data = fields.Text(
        string='Структурированные данные',
        help='JSON с структурированной информацией'
    )

    # Источники и ссылки
    source = fields.Char(
        string='Источник',
        help='Источник информации (стандарт, документ, эксперт)'
    )

    reference_url = fields.Char(
        string='Ссылка на источник'
    )

    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Вложения',
        help='Связанные документы и файлы'
    )

    # Применимость
    domain_types = fields.Selection([
        ('all', 'Все типы организаций'),
        ('corporate', 'Корпоративный сектор'),
        ('government', 'Государственный сектор'),
        ('npo', 'НКО и благотворительность'),
        ('critical_infrastructure', 'Критическая инфраструктура'),
    ], string='Применимость', default='all')

    industry_tags = fields.Char(
        string='Отраслевые теги',
        help='Теги отраслей через запятую'
    )

    # Качество и актуальность
    quality_score = fields.Float(
        string='Оценка качества',
        default=0.0,
        help='Оценка качества контента от 0 до 10'
    )

    last_reviewed = fields.Date(
        string='Последняя проверка',
        help='Дата последней проверки актуальности'
    )

    reviewer_id = fields.Many2one(
        'res.users',
        string='Проверяющий',
        help='Пользователь, который последний раз проверял контент'
    )

    is_approved = fields.Boolean(
        string='Одобрено',
        default=False,
        help='Прошел ли контент модерацию'
    )

    # Использование
    usage_count = fields.Integer(
        string='Количество использований',
        default=0,
        help='Сколько раз использовалось в консультациях'
    )

    effectiveness_rating = fields.Float(
        string='Рейтинг эффективности',
        compute='_compute_effectiveness',
        store=True,
        help='Рейтинг на основе обратной связи пользователей'
    )

    # Системные поля
    sequence = fields.Integer(
        string='Последовательность',
        default=10
    )

    active = fields.Boolean(
        string='Активно',
        default=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Компания',
        default=lambda self: self.env.company,
        required=True
    )

    # Связи с консультациями
    consultation_usage_ids = fields.One2many(
        'bcm.ai.knowledge.usage',
        'knowledge_id',
        string='Использование в консультациях'
    )

    @api.depends('consultation_usage_ids', 'consultation_usage_ids.rating')
    def _compute_effectiveness(self):
        """Вычисление рейтинга эффективности"""
        for knowledge in self:
            usages = knowledge.consultation_usage_ids.filtered('rating')
            if usages:
                ratings = [float(usage.rating) for usage in usages]
                knowledge.effectiveness_rating = sum(ratings) / len(ratings)
            else:
                knowledge.effectiveness_rating = 0.0

    def action_review_content(self):
        """Отметить как проверенное"""
        self.ensure_one()
        self.write({
            'last_reviewed': fields.Date.today(),
            'reviewer_id': self.env.user.id,
            'is_approved': True
        })

    def increment_usage(self):
        """Увеличить счетчик использования"""
        self.usage_count += 1

    @api.model
    def search_knowledge(self, query, category=None, domain_type=None, limit=10):
        """Поиск по базе знаний"""
        domain = [
            ('active', '=', True),
            ('is_approved', '=', True),
            '|', '|', '|',
            ('name', 'ilike', query),
            ('summary', 'ilike', query),
            ('content', 'ilike', query),
            ('keywords', 'ilike', query)
        ]

        if category:
            domain.append(('category', '=', category))

        if domain_type and domain_type != 'all':
            domain.extend([
                '|',
                ('domain_types', '=', 'all'),
                ('domain_types', '=', domain_type)
            ])

        return self.search(domain, limit=limit, order='effectiveness_rating desc, usage_count desc')

    @api.model
    def create_default_knowledge(self, consultant_id):
        """Создание базовых знаний для нового консультанта"""
        base_knowledge = [
            {
                'name': 'ISO 22301:2019 - Основы стандарта',
                'category': 'iso22301',
                'knowledge_type': 'text',
                'content': '''
                <h3>ISO 22301:2019 - Системы менеджмента непрерывности бизнеса</h3>
                <p>Международный стандарт, который устанавливает требования к системе управления непрерывностью бизнеса.</p>

                <h4>Ключевые принципы:</h4>
                <ul>
                    <li>Лидерство и приверженность руководства</li>
                    <li>Планирование и управление рисками</li>
                    <li>Поддержка и ресурсы</li>
                    <li>Операционная деятельность</li>
                    <li>Оценка результатов</li>
                    <li>Улучшение</li>
                </ul>
                ''',
                'summary': 'Базовые принципы и требования стандарта ISO 22301:2019',
                'keywords': 'ISO 22301, BCMS, непрерывность бизнеса, стандарт',
                'source': 'ISO 22301:2019',
                'quality_score': 9.5,
            },
            {
                'name': 'Анализ влияния на бизнес (BIA)',
                'category': 'procedures',
                'knowledge_type': 'checklist',
                'content': '''
                <h3>Этапы проведения BIA</h3>
                <ol>
                    <li>Определение критически важных бизнес-функций</li>
                    <li>Анализ зависимостей и ресурсов</li>
                    <li>Оценка временных параметров (RTO, RPO)</li>
                    <li>Расчет потенциальных потерь</li>
                    <li>Документирование результатов</li>
                </ol>
                ''',
                'summary': 'Пошаговая процедура проведения анализа влияния на бизнес',
                'keywords': 'BIA, анализ влияния, критические функции, RTO, RPO',
                'source': 'BCM Best Practices',
                'quality_score': 8.5,
            }
        ]

        for knowledge_data in base_knowledge:
            knowledge_data['consultant_id'] = consultant_id
            knowledge_data['is_approved'] = True
            self.create(knowledge_data)

        _logger.info(f"Создана базовая база знаний для консультанта {consultant_id}")


class BCMAIKnowledgeUsage(models.Model):
    _name = 'bcm.ai.knowledge.usage'
    _description = 'BCM AI Knowledge Usage - Использование знаний в консультациях'

    knowledge_id = fields.Many2one(
        'bcm.ai.knowledge.base',
        string='Знание',
        required=True,
        ondelete='cascade'
    )

    session_id = fields.Many2one(
        'bcm.ai.consultation.session',
        string='Сессия консультации',
        required=True,
        ondelete='cascade'
    )

    message_id = fields.Many2one(
        'bcm.ai.consultation.message',
        string='Сообщение',
        ondelete='cascade'
    )

    usage_type = fields.Selection([
        ('referenced', 'Упоминание'),
        ('quoted', 'Цитирование'),
        ('template_used', 'Использование шаблона'),
        ('procedure_followed', 'Следование процедуре'),
    ], string='Тип использования', required=True)

    rating = fields.Selection([
        ('1', 'Неполезно'),
        ('2', 'Малополезно'),
        ('3', 'Полезно'),
        ('4', 'Очень полезно'),
        ('5', 'Критически важно'),
    ], string='Оценка полезности')

    feedback = fields.Text(
        string='Обратная связь',
        help='Комментарий о полезности использованного знания'
    )

    create_date = fields.Datetime(
        string='Дата использования',
        default=fields.Datetime.now,
        readonly=True
    )