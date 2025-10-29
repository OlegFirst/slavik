# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class BCMEventBus(models.Model):
    """
    BCM Event Bus - система событий для межмодульной коммуникации
    Превращает модули из изолированных компонентов в единый организм
    """
    _name = 'bcm.event.bus'
    _description = 'BCM Event Bus for Inter-Module Communication'
    _order = 'timestamp desc'
    _rec_name = 'event_type'

    # Event identification
    event_type = fields.Selection([
        # Project Management Events
        ('project_created', 'Project Created'),
        ('project_health_changed', 'Project Health Changed'),
        ('project_escalated', 'Project Escalated'),
        ('task_assigned', 'Task Assigned'),
        ('task_completed', 'Task Completed'),

        # Risk Management Events
        ('risk_identified', 'Risk Identified'),
        ('risk_level_changed', 'Risk Level Changed'),
        ('risk_mitigation_required', 'Risk Mitigation Required'),

        # Incident Events
        ('incident_created', 'Incident Created'),
        ('incident_escalated', 'Incident Escalated'),
        ('recovery_initiated', 'Recovery Initiated'),

        # Audit Events
        ('audit_finding_created', 'Audit Finding Created'),
        ('compliance_issue', 'Compliance Issue'),
        ('corrective_action_required', 'Corrective Action Required'),

        # AI Events
        ('ai_insight_generated', 'AI Insight Generated'),
        ('ai_recommendation_made', 'AI Recommendation Made'),
        ('learning_data_updated', 'Learning Data Updated'),

        # System Events
        ('module_registered', 'Module Registered'),
        ('integration_health_check', 'Integration Health Check'),
    ], string='Event Type', required=True)

    # Event metadata
    source_module = fields.Char('Source Module', required=True)
    target_modules = fields.Json('Target Modules', help='List of modules that should handle this event')
    event_data = fields.Json('Event Data', help='Structured data related to the event')

    # Tracking
    timestamp = fields.Datetime('Timestamp', default=fields.Datetime.now, required=True)
    processed = fields.Boolean('Processed', default=False)
    processing_results = fields.Json('Processing Results', help='Results from each module that processed this event')

    # Priority and routing
    priority = fields.Selection([
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], string='Priority', default='normal')

    correlation_id = fields.Char('Correlation ID', help='ID to group related events')

    # Status tracking
    state = fields.Selection([
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], string='State', default='pending')

    # ============== EVENT PUBLISHING ==============

    @api.model
    def publish_event(self, event_type, source_module, event_data, target_modules=None, priority='normal', correlation_id=None):
        """
        Публикует событие в шину для обработки другими модулями

        Args:
            event_type: тип события
            source_module: модуль-источник события
            event_data: данные события
            target_modules: список целевых модулей (если None - broadcast)
            priority: приоритет события
            correlation_id: ID для группировки связанных событий
        """

        # Автоматическое определение целевых модулей если не указано
        if target_modules is None:
            target_modules = self._get_interested_modules(event_type)

        # Создаем событие
        event = self.create({
            'event_type': event_type,
            'source_module': source_module,
            'target_modules': target_modules,
            'event_data': event_data,
            'priority': priority,
            'correlation_id': correlation_id or self._generate_correlation_id(),
            'state': 'pending',
        })

        # Немедленно обрабатываем критичные события
        if priority == 'critical':
            self._process_event_immediately(event)
        else:
            # Планируем асинхронную обработку
            self._schedule_event_processing(event)

        _logger.info(f"Published event {event_type} from {source_module} to {target_modules}")
        return event

    def _get_interested_modules(self, event_type):
        """Определяет какие модули заинтересованы в данном типе события"""

        # Карта событий -> заинтересованные модули
        interest_map = {
            'project_created': ['bcm_risk_management', 'bcm_audit', 'bcm_reporting'],
            'project_health_changed': ['bcm_risk_management', 'bcm_incident_management'],
            'project_escalated': ['bcm_incident_management', 'bcm_governance'],

            'risk_identified': ['bcm_project_management', 'bcm_incident_management', 'bcm_audit'],
            'risk_level_changed': ['bcm_project_management', 'bcm_governance'],

            'incident_created': ['bcm_project_management', 'bcm_risk_management', 'bcm_exercise'],
            'incident_escalated': ['bcm_governance', 'bcm_reporting'],

            'audit_finding_created': ['bcm_project_management', 'bcm_risk_management', 'bcm_governance'],

            'ai_insight_generated': ['all'],  # все модули заинтересованы в AI инсайтах
            'ai_recommendation_made': ['all'],
        }

        interested = interest_map.get(event_type, [])

        if 'all' in interested:
            # Получаем все зарегистрированные BCM модули
            registry = self.env['bcm.module.registry']
            return registry.get_all_active_modules()

        return interested

    # ============== EVENT PROCESSING ==============

    def _process_event_immediately(self, event):
        """Немедленная обработка критичных событий"""
        event.state = 'processing'
        self._route_event_to_modules(event)

    def _schedule_event_processing(self, event):
        """Планирует асинхронную обработку события"""
        # В продакшене здесь был бы вызов очереди задач (Celery, RQ)
        # Для Odoo используем cron job или обрабатываем синхронно для высокоприоритетных

        if event.priority == 'high':
            # Обрабатываем сразу
            self._route_event_to_modules(event)
        else:
            # Помечаем для обработки cron job'ом
            pass

    def _route_event_to_modules(self, event):
        """Направляет событие в соответствующие модули для обработки"""
        event.state = 'processing'
        results = {}

        target_modules = event.target_modules or []

        for module_name in target_modules:
            try:
                result = self._process_event_in_module(event, module_name)
                results[module_name] = {
                    'success': True,
                    'result': result,
                    'timestamp': fields.Datetime.now(),
                }
            except Exception as e:
                _logger.error(f"Failed to process event {event.event_type} in module {module_name}: {str(e)}")
                results[module_name] = {
                    'success': False,
                    'error': str(e),
                    'timestamp': fields.Datetime.now(),
                }

        # Сохраняем результаты
        event.write({
            'processing_results': results,
            'processed': True,
            'state': 'completed' if all(r.get('success') for r in results.values()) else 'failed',
        })

    def _process_event_in_module(self, event, module_name):
        """Обрабатывает событие в конкретном модуле"""

        # Карта модулей -> модели обработчиков событий
        handler_map = {
            'bcm_project_management': 'bcm.project.event.handler',
            'bcm_risk_management': 'bcm.risk.event.handler',
            'bcm_incident_management': 'bcm.incident.event.handler',
            'bcm_audit': 'bcm.audit.event.handler',
            'bcm_governance': 'bcm.governance.event.handler',
            'bcm_reporting': 'bcm.reporting.event.handler',
        }

        handler_model = handler_map.get(module_name)

        if not handler_model or handler_model not in self.env:
            # Если специального обработчика нет, используем общий механизм
            return self._generic_event_processing(event, module_name)

        # Вызываем специфический обработчик модуля
        handler = self.env[handler_model]
        return handler.handle_event(event.event_type, event.event_data, event.source_module)

    def _generic_event_processing(self, event, module_name):
        """Общий механизм обработки событий для модулей без специального обработчика"""

        # Простое логирование для модулей без обработчика
        _logger.info(f"Generic processing of {event.event_type} for {module_name}: {event.event_data}")

        # Здесь можно добавить базовую логику обработки
        return {'processed': True, 'method': 'generic'}

    # ============== EVENT QUERYING ==============

    @api.model
    def get_events_for_module(self, module_name, event_types=None, limit=100):
        """Получает события для конкретного модуля"""

        domain = [('target_modules', 'ilike', module_name)]

        if event_types:
            domain.append(('event_type', 'in', event_types))

        return self.search(domain, limit=limit, order='timestamp desc')

    @api.model
    def get_correlation_events(self, correlation_id):
        """Получает все события с одним correlation_id"""
        return self.search([('correlation_id', '=', correlation_id)], order='timestamp asc')

    # ============== UTILITY METHODS ==============

    def _generate_correlation_id(self):
        """Генерирует уникальный correlation ID"""
        import uuid
        return str(uuid.uuid4())

    # ============== CRON METHODS ==============

    @api.model
    def _cron_process_pending_events(self):
        """Cron job для обработки отложенных событий"""

        pending_events = self.search([
            ('state', '=', 'pending'),
            ('priority', 'in', ['low', 'normal']),
        ], limit=50, order='priority desc, timestamp asc')

        for event in pending_events:
            try:
                self._route_event_to_modules(event)
            except Exception as e:
                _logger.error(f"Failed to process pending event {event.id}: {str(e)}")
                event.state = 'failed'

    @api.model
    def _cron_cleanup_old_events(self):
        """Очистка старых событий"""
        from datetime import timedelta

        cutoff_date = fields.Datetime.now() - timedelta(days=30)
        old_events = self.search([
            ('timestamp', '<', cutoff_date),
            ('state', 'in', ['completed', 'failed']),
        ])

        _logger.info(f"Cleaning up {len(old_events)} old events")
        old_events.unlink()

    # ============== MONITORING ==============

    def action_reprocess_event(self):
        """Переобработка события"""
        self.ensure_one()

        if self.state in ['completed', 'failed']:
            self.write({
                'state': 'pending',
                'processed': False,
                'processing_results': {},
            })
            self._route_event_to_modules(self)

        return True

    @api.model
    def get_event_statistics(self):
        """Статистика событий для мониторинга"""

        stats = {}

        # Статистика по типам событий
        event_type_stats = self.read_group(
            [],
            ['event_type'],
            ['event_type']
        )
        stats['by_event_type'] = {r['event_type']: r['event_type_count'] for r in event_type_stats}

        # Статистика по состояниям
        state_stats = self.read_group(
            [],
            ['state'],
            ['state']
        )
        stats['by_state'] = {r['state']: r['state_count'] for r in state_stats}

        # Статистика по модулям
        module_stats = self.read_group(
            [],
            ['source_module'],
            ['source_module']
        )
        stats['by_source_module'] = {r['source_module']: r['source_module_count'] for r in module_stats}

        return stats