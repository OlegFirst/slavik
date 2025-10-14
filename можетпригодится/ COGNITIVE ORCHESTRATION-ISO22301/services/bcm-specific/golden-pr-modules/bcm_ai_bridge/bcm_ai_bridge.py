# -*- coding: utf-8 -*-
"""
BCM AI Bridge - Универсальный мост между локальными AI модулей и центральным Meta-AI

Архитектура:
- Каждый модуль имеет свой локальный AI для специфичных задач
- Bridge обеспечивает связь с центральным Meta-AI
- Meta-AI обучается на всех модулях и обогащает их знаниями
"""

from odoo import models, fields, api, _
import requests
import json
import logging
from datetime import datetime
import hashlib

_logger = logging.getLogger(__name__)


class BCMAIBridge(models.Model):
    """
    Универсальный мост для связи локальных AI с центральным Meta-AI
    Один для всей системы, используется всеми модулями
    """
    _name = 'bcm.ai.bridge'
    _description = 'BCM AI Universal Bridge'
    _rec_name = 'name'
    _order = 'priority desc, id desc'

    name = fields.Char('Bridge Name', default='BCM Meta-AI Bridge')
    active = fields.Boolean('Active', default=True)
    priority = fields.Integer('Priority', default=10)

    # Connection settings
    meta_ai_endpoint = fields.Char(
        'Meta-AI Endpoint',
        default='http://localhost:8000/api/meta-ai',
        help='Central Meta-AI service endpoint'
    )
    api_key = fields.Char('API Key')
    timeout = fields.Integer('Timeout (seconds)', default=30)

    # State and metrics
    state = fields.Selection([
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error'),
    ], string='Connection State', default='disconnected')

    last_sync = fields.Datetime('Last Synchronization')
    total_requests = fields.Integer('Total Requests', default=0)
    total_learning_events = fields.Integer('Learning Events Sent', default=0)

    # Knowledge synchronization
    knowledge_version = fields.Char('Knowledge Version')
    modules_connected = fields.Json('Connected Modules')

    # Cache
    cache_enabled = fields.Boolean('Enable Cache', default=True)
    cache_ttl = fields.Integer('Cache TTL (seconds)', default=300)
    _cache = {}  # Runtime cache

    # ============== SINGLETON PATTERN ==============

    @api.model
    def get_instance(self):
        """Получает активный экземпляр Bridge (singleton pattern)"""
        bridge = self.search([('active', '=', True)], order='priority desc', limit=1)

        if not bridge:
            # Создаем bridge если его нет
            bridge = self.create({
                'name': 'Auto-created Bridge',
                'active': True,
            })

        return bridge

    # ============== CORE COMMUNICATION ==============

    def request_analysis(self, analysis_type, data):
        """
        Запрос анализа от центрального AI
        Используется локальными AI для обогащения своих решений
        """
        self.ensure_one()

        cache_key = self._get_cache_key(analysis_type, data)

        # Проверяем кэш
        if self.cache_enabled and cache_key in self._cache:
            cached = self._cache[cache_key]
            if cached['timestamp'] + self.cache_ttl > datetime.now().timestamp():
                return cached['data']

        try:
            response = self._call_meta_ai('analysis', {
                'type': analysis_type,
                'data': data,
                'context': self._get_context(),
            })

            if response.get('success'):
                result = response.get('result', {})

                # Кэшируем результат
                if self.cache_enabled:
                    self._cache[cache_key] = {
                        'data': result,
                        'timestamp': datetime.now().timestamp(),
                    }

                return result

        except Exception as e:
            _logger.error(f"Bridge analysis request failed: {str(e)}")

        return {}

    def validate_decision(self, decision_type, data):
        """
        Валидация решения локального AI через Meta-AI
        Meta-AI может переопределить решение на основе глобального контекста
        """
        self.ensure_one()

        try:
            response = self._call_meta_ai('validate', {
                'decision_type': decision_type,
                'data': data,
                'context': self._get_context(),
            })

            if response.get('success'):
                return response.get('validation', {})

        except Exception as e:
            _logger.error(f"Bridge validation failed: {str(e)}")

        return {'approved': True}  # Default: не блокируем локальные решения

    def send_learning_data(self, learning_data):
        """
        Отправка данных для обучения Meta-AI
        Каждый модуль отправляет свой опыт для общего обучения
        """
        self.ensure_one()

        try:
            response = self._call_meta_ai('learn', {
                'learning_data': learning_data,
                'timestamp': fields.Datetime.now(),
                'source': self._get_module_context(learning_data.get('module')),
            })

            if response.get('success'):
                self.total_learning_events += 1

                # Meta-AI может вернуть обновленные правила
                if response.get('updated_rules'):
                    self._distribute_knowledge(response['updated_rules'])

            return response.get('success', False)

        except Exception as e:
            _logger.error(f"Bridge learning submission failed: {str(e)}")

        return False

    def get_model_updates(self, module_name):
        """
        Получение обновлений моделей для конкретного модуля
        Meta-AI обучается на всех модулях и распространяет знания
        """
        self.ensure_one()

        try:
            response = self._call_meta_ai('get_updates', {
                'module': module_name,
                'current_version': self._get_module_version(module_name),
            })

            if response.get('success') and response.get('updates'):
                return response['updates']

        except Exception as e:
            _logger.error(f"Bridge model updates failed: {str(e)}")

        return None

    # ============== META-AI ORCHESTRATION ==============

    def orchestrate_cross_module_decision(self, decision_context):
        """
        Оркестрация решений, затрагивающих несколько модулей
        Meta-AI координирует действия между модулями
        """
        self.ensure_one()

        try:
            response = self._call_meta_ai('orchestrate', {
                'decision_context': decision_context,
                'affected_modules': decision_context.get('modules', []),
                'priority': decision_context.get('priority', 'normal'),
            })

            if response.get('success'):
                orchestration_plan = response.get('plan', {})

                # Распределяем задачи по модулям
                for module, actions in orchestration_plan.items():
                    self._notify_module_ai(module, actions)

                return orchestration_plan

        except Exception as e:
            _logger.error(f"Bridge orchestration failed: {str(e)}")

        return {}

    def request_prediction(self, prediction_type, historical_data, context):
        """
        Запрос предсказания от Meta-AI на основе данных всех модулей
        """
        self.ensure_one()

        try:
            response = self._call_meta_ai('predict', {
                'type': prediction_type,
                'historical_data': historical_data,
                'context': context,
                'confidence_required': context.get('confidence_threshold', 0.7),
            })

            if response.get('success'):
                return {
                    'prediction': response.get('prediction'),
                    'confidence': response.get('confidence', 0),
                    'factors': response.get('factors', []),
                    'alternative_scenarios': response.get('alternatives', []),
                }

        except Exception as e:
            _logger.error(f"Bridge prediction failed: {str(e)}")

        return None

    # ============== KNOWLEDGE DISTRIBUTION ==============

    def _distribute_knowledge(self, knowledge_updates):
        """
        Распространение знаний от Meta-AI к локальным AI
        """
        for module_name, updates in knowledge_updates.items():
            try:
                # Находим локальный AI модуля
                local_ai = self._get_module_ai(module_name)
                if local_ai:
                    # Обновляем знания локального AI
                    if hasattr(local_ai, 'apply_knowledge_update'):
                        local_ai.apply_knowledge_update(updates)
                    else:
                        _logger.warning(f"Module {module_name} AI doesn't support knowledge updates")

            except Exception as e:
                _logger.error(f"Failed to distribute knowledge to {module_name}: {str(e)}")

    def _notify_module_ai(self, module_name, actions):
        """
        Уведомление локального AI модуля о необходимых действиях
        """
        try:
            local_ai = self._get_module_ai(module_name)
            if local_ai and hasattr(local_ai, 'execute_orchestrated_actions'):
                local_ai.execute_orchestrated_actions(actions)

        except Exception as e:
            _logger.error(f"Failed to notify module {module_name}: {str(e)}")

    # ============== MONITORING & HEALTH ==============

    def test_connection(self):
        """Тест соединения с Meta-AI"""
        self.ensure_one()

        try:
            response = self._call_meta_ai('ping', {})

            if response.get('success'):
                self.state = 'connected'
                return True
            else:
                self.state = 'error'
                return False

        except Exception as e:
            self.state = 'disconnected'
            _logger.error(f"Bridge connection test failed: {str(e)}")
            return False

    @api.model
    def monitor_ai_ecosystem(self):
        """
        Мониторинг всей AI экосистемы
        Возвращает статус всех локальных AI и Meta-AI
        """
        bridge = self.get_instance()

        ecosystem_status = {
            'meta_ai': {
                'connected': bridge.state == 'connected',
                'last_sync': bridge.last_sync,
                'requests': bridge.total_requests,
            },
            'modules': {},
        }

        # Проверяем все модули с AI
        ai_modules = [
            'bcm.project.ai.local',
            'bcm.risk.ai.local',
            'bcm.incident.ai.local',
            # ... другие модули
        ]

        for module_model in ai_modules:
            try:
                if module_model in self.env:
                    local_ai = self.env[module_model].search([('active', '=', True)], limit=1)
                    if local_ai:
                        ecosystem_status['modules'][module_model] = {
                            'active': True,
                            'accuracy': getattr(local_ai, 'accuracy_rate', 0),
                            'last_learning': getattr(local_ai, 'last_learning_date', None),
                        }
            except:
                pass

        return ecosystem_status

    # ============== PRIVATE METHODS ==============

    def _call_meta_ai(self, endpoint, data):
        """Базовый метод для вызова Meta-AI"""
        self.ensure_one()

        if not self.meta_ai_endpoint:
            return {'success': False, 'error': 'No Meta-AI endpoint configured'}

        headers = {
            'Content-Type': 'application/json',
        }

        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        payload = {
            'endpoint': endpoint,
            'data': data,
            'bridge_version': '1.0',
            'timestamp': fields.Datetime.now(),
        }

        try:
            response = requests.post(
                f"{self.meta_ai_endpoint}/{endpoint}",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )

            self.total_requests += 1

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'success': False,
                    'error': f'Meta-AI returned {response.status_code}'
                }

        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Request timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_context(self):
        """Получает контекст для Meta-AI"""
        return {
            'company_id': self.env.company.id,
            'user_id': self.env.user.id,
            'modules': self._get_active_modules(),
            'timestamp': fields.Datetime.now(),
        }

    def _get_module_context(self, module_name):
        """Получает контекст конкретного модуля"""
        return {
            'module': module_name,
            'version': self._get_module_version(module_name),
            'active': self._is_module_active(module_name),
        }

    def _get_active_modules(self):
        """Получает список активных BCM модулей"""
        # Это можно оптимизировать через кэш
        modules = []
        module_models = [
            'bcm.project.ai.local',
            'bcm.risk.ai.local',
            # ... другие
        ]

        for model in module_models:
            if model in self.env:
                modules.append(model.replace('.ai.local', ''))

        return modules

    def _get_module_ai(self, module_name):
        """Получает экземпляр локального AI модуля"""
        ai_model_map = {
            'bcm_project_management': 'bcm.project.ai.local',
            'bcm_risk_operations': 'bcm.risk.ai.local',
            # ... маппинг других модулей
        }

        model_name = ai_model_map.get(module_name)
        if model_name and model_name in self.env:
            return self.env[model_name].search([('active', '=', True)], limit=1)

        return None

    def _get_module_version(self, module_name):
        """Получает версию модуля"""
        # Simplified - в реальности брать из manifest
        return "1.0.0"

    def _is_module_active(self, module_name):
        """Проверяет активен ли модуль"""
        # Simplified
        return True

    def _get_cache_key(self, analysis_type, data):
        """Генерирует ключ для кэша"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(f"{analysis_type}:{data_str}".encode()).hexdigest()

    # ============== MODULE DISCOVERY & REGISTRATION ==============

    @api.model
    def _discover_and_register_modules(self):
        """Автоматически обнаруживает и регистрирует BCM модули"""
        registry = self.env['bcm.module.registry']
        registry.discover_bcm_modules()

        # Инициализируем Event Bus для новых модулей
        event_bus = self.env['bcm.event.bus']
        event_bus.publish_event(
            'module_discovery_completed',
            'bcm_ai_bridge',
            {'timestamp': fields.Datetime.now()}
        )

    # ============== INTER-MODULE ORCHESTRATION ==============

    def coordinate_cross_module_workflow(self, workflow_type, context):
        """
        Координирует рабочие процессы между модулями
        Например: Risk -> Project -> Incident -> Audit
        """
        self.ensure_one()

        workflow_handlers = {
            'risk_to_project': self._handle_risk_to_project_workflow,
            'incident_to_recovery': self._handle_incident_to_recovery_workflow,
            'audit_finding_to_action': self._handle_audit_to_action_workflow,
            'project_health_to_escalation': self._handle_project_escalation_workflow,
        }

        handler = workflow_handlers.get(workflow_type)
        if handler:
            return handler(context)

        # Generic workflow через Meta-AI
        return self.orchestrate_cross_module_decision({
            'workflow_type': workflow_type,
            'context': context,
            'modules': self._identify_affected_modules(workflow_type),
        })

    def _handle_risk_to_project_workflow(self, context):
        """Workflow: Выявлен риск -> Создать проект митигации"""
        risk_data = context.get('risk_data', {})

        # Публикуем событие о создании риска
        event_bus = self.env['bcm.event.bus']
        event_bus.publish_event(
            'risk_identified',
            'bcm_risk_management',
            risk_data,
            target_modules=['bcm_project_management'],
            priority='high'
        )

        # Запрашиваем у Meta-AI рекомендации по созданию проекта
        project_recommendation = self.request_analysis('risk_mitigation_project', {
            'risk_level': risk_data.get('risk_level'),
            'impact_score': risk_data.get('impact_score'),
            'risk_category': risk_data.get('category'),
        })

        return {
            'workflow': 'risk_to_project',
            'recommendation': project_recommendation,
            'next_actions': ['create_mitigation_project', 'assign_project_manager'],
        }

    def _handle_incident_to_recovery_workflow(self, context):
        """Workflow: Инцидент -> Активация плана восстановления"""
        incident_data = context.get('incident_data', {})

        # Анализируем серьезность инцидента через Meta-AI
        severity_analysis = self.request_analysis('incident_severity', {
            'incident_type': incident_data.get('incident_type'),
            'affected_systems': incident_data.get('affected_systems', []),
            'business_impact': incident_data.get('business_impact'),
        })

        # Если инцидент критичный, автоматически создаем проект восстановления
        if severity_analysis.get('severity_level', 0) >= 8:
            event_bus = self.env['bcm.event.bus']
            event_bus.publish_event(
                'recovery_initiated',
                'bcm_incident_management',
                {
                    'incident_id': incident_data.get('incident_id'),
                    'severity_analysis': severity_analysis,
                    'auto_recovery': True,
                },
                target_modules=['bcm_project_management'],
                priority='critical'
            )

        return {
            'workflow': 'incident_to_recovery',
            'severity_analysis': severity_analysis,
            'auto_recovery_triggered': severity_analysis.get('severity_level', 0) >= 8,
        }

    def _identify_affected_modules(self, workflow_type):
        """Определяет какие модули затронуты рабочим процессом"""
        workflow_module_map = {
            'risk_to_project': ['bcm_risk_management', 'bcm_project_management'],
            'incident_to_recovery': ['bcm_incident_management', 'bcm_project_management', 'bcm_plans'],
            'audit_finding_to_action': ['bcm_audit', 'bcm_project_management', 'bcm_governance'],
            'project_health_to_escalation': ['bcm_project_management', 'bcm_incident_management', 'bcm_governance'],
        }

        return workflow_module_map.get(workflow_type, [])

    # ============== REAL-TIME INTEGRATION HUB ==============

    def process_real_time_integration(self, source_module, integration_type, data):
        """
        Обрабатывает интеграционные события в реальном времени
        Центральная точка для всех межмодульных интеграций
        """
        self.ensure_one()

        integration_handlers = {
            'project_health_changed': self._handle_project_health_integration,
            'risk_level_escalated': self._handle_risk_escalation_integration,
            'incident_severity_increased': self._handle_incident_escalation_integration,
            'audit_finding_critical': self._handle_critical_audit_integration,
        }

        handler = integration_handlers.get(integration_type)
        if handler:
            return handler(source_module, data)

        # Generic обработка через Event Bus
        event_bus = self.env['bcm.event.bus']
        return event_bus.publish_event(
            integration_type,
            source_module,
            data,
            priority='normal'
        )

    def _handle_project_health_integration(self, source_module, data):
        """Интеграция при изменении здоровья проекта"""
        project_health = data.get('health_status')
        project_id = data.get('project_id')

        if project_health == 'critical':
            # Автоматически создаем инцидент при критическом состоянии проекта
            event_bus = self.env['bcm.event.bus']
            event_bus.publish_event(
                'project_escalated',
                source_module,
                {
                    'project_id': project_id,
                    'escalation_reason': 'critical_health_status',
                    'auto_incident_creation': True,
                },
                target_modules=['bcm_incident_management'],
                priority='high'
            )

            # Уведомляем Risk Management для обновления связанных рисков
            event_bus.publish_event(
                'project_health_changed',
                source_module,
                data,
                target_modules=['bcm_risk_management'],
                priority='normal'
            )

        return {'integration_processed': True, 'actions_triggered': ['incident_creation', 'risk_update']}

    # ============== CRON JOBS ==============

    @api.model
    def _cron_sync_with_meta_ai(self):
        """Периодическая синхронизация с Meta-AI"""
        bridge = self.get_instance()

        if bridge.test_connection():
            # Получаем обновления знаний
            response = bridge._call_meta_ai('sync', {
                'modules': bridge._get_active_modules(),
                'last_sync': bridge.last_sync or fields.Datetime.now(),
            })

            if response.get('success'):
                # Распространяем обновления
                if response.get('knowledge_updates'):
                    bridge._distribute_knowledge(response['knowledge_updates'])

                bridge.last_sync = fields.Datetime.now()
                bridge.knowledge_version = response.get('version', '0')

                _logger.info("Successfully synchronized with Meta-AI")

    @api.model
    def _cron_process_integration_health(self):
        """Мониторинг здоровья интеграций между модулями"""
        bridge = self.get_instance()

        # Проверяем здоровье всех модулей
        registry = self.env['bcm.module.registry']
        health_report = registry.check_all_modules_health()

        # Анализируем проблемные интеграции
        problematic_modules = [
            name for name, status in health_report.items()
            if not status['healthy']
        ]

        if problematic_modules:
            # Публикуем событие о проблемах с интеграцией
            event_bus = self.env['bcm.event.bus']
            event_bus.publish_event(
                'integration_health_issue',
                'bcm_ai_bridge',
                {
                    'problematic_modules': problematic_modules,
                    'health_report': health_report,
                },
                priority='high'
            )

            _logger.warning(f"Integration health issues detected: {problematic_modules}")

        return health_report