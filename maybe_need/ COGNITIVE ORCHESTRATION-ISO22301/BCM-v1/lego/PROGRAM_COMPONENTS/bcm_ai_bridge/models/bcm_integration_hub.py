# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class BCMIntegrationHub(models.Model):
    """
    BCM Integration Hub - центральный хаб для координации всех интеграций
    Превращает изолированные модули в единый интеллектуальный организм
    """
    _name = 'bcm.integration.hub'
    _description = 'BCM Integration Hub - Central Coordination Point'
    _rec_name = 'name'

    name = fields.Char('Hub Name', default='BCM Central Integration Hub')
    active = fields.Boolean('Active', default=True)

    # Hub status and metrics
    total_integrations = fields.Integer('Total Integrations', default=0)
    successful_integrations = fields.Integer('Successful Integrations', default=0)
    failed_integrations = fields.Integer('Failed Integrations', default=0)
    last_sync = fields.Datetime('Last Sync')

    # Integration mapping
    module_dependencies = fields.Json('Module Dependencies Map')
    integration_flows = fields.Json('Integration Flow Definitions')
    workflow_templates = fields.Json('Cross-Module Workflow Templates')

    # ============== INTEGRATION ORCHESTRATION ==============

    @api.model
    def orchestrate_workflow(self, workflow_name, initial_data, initiator_module):
        """
        Оркестрирует комплексный workflow между модулями
        Это центральная функция превращения модулей в единый организм
        """

        workflow_definitions = {
            # Risk -> Project -> Incident -> Audit Chain
            'comprehensive_risk_management': {
                'steps': [
                    {'module': 'bcm_risk_management', 'action': 'assess_risk'},
                    {'module': 'bcm_project_management', 'action': 'create_mitigation_project'},
                    {'module': 'bcm_incident_management', 'action': 'prepare_response_plan'},
                    {'module': 'bcm_audit', 'action': 'schedule_compliance_check'},
                ],
                'rollback_strategy': 'compensating_actions',
            },

            # Incident -> Recovery -> Project -> Audit Chain
            'incident_response_recovery': {
                'steps': [
                    {'module': 'bcm_incident_management', 'action': 'classify_incident'},
                    {'module': 'bcm_project_management', 'action': 'activate_recovery_project'},
                    {'module': 'bcm_plans', 'action': 'execute_recovery_procedures'},
                    {'module': 'bcm_audit', 'action': 'document_lessons_learned'},
                ],
                'rollback_strategy': 'escalation_path',
            },

            # Audit -> Risk -> Project -> Training Chain
            'audit_finding_remediation': {
                'steps': [
                    {'module': 'bcm_audit', 'action': 'analyze_finding'},
                    {'module': 'bcm_risk_management', 'action': 'update_risk_register'},
                    {'module': 'bcm_project_management', 'action': 'create_corrective_action_project'},
                    {'module': 'bcm_training', 'action': 'develop_training_program'},
                ],
                'rollback_strategy': 'partial_completion',
            },

            # Project Health -> Risk -> Incident -> Governance Chain
            'project_health_escalation': {
                'steps': [
                    {'module': 'bcm_project_management', 'action': 'assess_health_decline'},
                    {'module': 'bcm_risk_management', 'action': 'elevate_associated_risks'},
                    {'module': 'bcm_incident_management', 'action': 'create_preventive_incident'},
                    {'module': 'bcm_governance', 'action': 'executive_notification'},
                ],
                'rollback_strategy': 'status_restoration',
            },
        }

        workflow_def = workflow_definitions.get(workflow_name)
        if not workflow_def:
            _logger.error(f"Unknown workflow: {workflow_name}")
            return {'success': False, 'error': 'Unknown workflow'}

        return self._execute_workflow_chain(workflow_def, initial_data, initiator_module)

    def _execute_workflow_chain(self, workflow_def, data, initiator_module):
        """Выполняет цепочку действий workflow"""

        workflow_id = self._generate_workflow_id()
        execution_log = []
        current_data = data.copy()

        _logger.info(f"Starting workflow chain {workflow_id} from {initiator_module}")

        try:
            for step_index, step in enumerate(workflow_def['steps']):
                step_result = self._execute_workflow_step(
                    step,
                    current_data,
                    workflow_id,
                    step_index
                )

                execution_log.append({
                    'step': step_index,
                    'module': step['module'],
                    'action': step['action'],
                    'result': step_result,
                    'timestamp': fields.Datetime.now(),
                })

                if not step_result.get('success', False):
                    # Workflow step failed - execute rollback strategy
                    _logger.error(f"Workflow step failed: {step['module']}.{step['action']}")
                    rollback_result = self._execute_rollback(
                        workflow_def['rollback_strategy'],
                        execution_log,
                        current_data
                    )
                    return {
                        'success': False,
                        'workflow_id': workflow_id,
                        'failed_step': step_index,
                        'execution_log': execution_log,
                        'rollback_result': rollback_result,
                    }

                # Update data with results from this step
                current_data.update(step_result.get('output_data', {}))

            # All steps completed successfully
            self.successful_integrations += 1
            self._log_successful_workflow(workflow_id, execution_log)

            return {
                'success': True,
                'workflow_id': workflow_id,
                'execution_log': execution_log,
                'final_data': current_data,
            }

        except Exception as e:
            self.failed_integrations += 1
            _logger.error(f"Workflow {workflow_id} crashed: {str(e)}")
            return {
                'success': False,
                'workflow_id': workflow_id,
                'error': str(e),
                'execution_log': execution_log,
            }

    def _execute_workflow_step(self, step, data, workflow_id, step_index):
        """Выполняет отдельный шаг workflow в указанном модуле"""

        module_name = step['module']
        action_name = step['action']

        # Publish event to target module
        event_bus = self.env['bcm.event.bus']
        event = event_bus.publish_event(
            f'workflow_step_{action_name}',
            'bcm_integration_hub',
            {
                'workflow_id': workflow_id,
                'step_index': step_index,
                'action': action_name,
                'data': data,
            },
            target_modules=[module_name],
            priority='high'
        )

        # Wait for module to process the event and return result
        # In real implementation, this would be async with proper timeout handling
        return self._wait_for_step_completion(event, timeout=30)

    def _wait_for_step_completion(self, event, timeout=30):
        """Ждет завершения шага workflow с таймаутом"""

        # Simplified synchronous implementation
        # In production, use proper async/await pattern

        import time
        start_time = time.time()

        while time.time() - start_time < timeout:
            event.refresh()

            if event.processed:
                processing_results = event.processing_results or {}

                # Check if any module returned a result
                for module_name, result in processing_results.items():
                    if result.get('success'):
                        return {
                            'success': True,
                            'result': result.get('result'),
                            'output_data': result.get('output_data', {}),
                        }

                # All modules failed
                return {'success': False, 'error': 'All target modules failed'}

            time.sleep(0.5)  # Poll every 500ms

        # Timeout reached
        return {'success': False, 'error': 'Workflow step timeout'}

    # ============== SMART MODULE COORDINATION ==============

    @api.model
    def coordinate_intelligent_response(self, trigger_event, context):
        """
        Интеллектуальная координация ответа всех связанных модулей
        На основе одного события активирует весь организм
        """

        coordination_strategies = {
            'critical_project_health': {
                'primary_responders': ['bcm_incident_management'],
                'secondary_responders': ['bcm_risk_management', 'bcm_governance'],
                'information_recipients': ['bcm_audit', 'bcm_reporting'],
                'ai_analysis_required': True,
            },

            'high_severity_incident': {
                'primary_responders': ['bcm_project_management', 'bcm_plans'],
                'secondary_responders': ['bcm_governance', 'bcm_communication'],
                'information_recipients': ['bcm_risk_management', 'bcm_audit'],
                'ai_analysis_required': True,
            },

            'critical_audit_finding': {
                'primary_responders': ['bcm_project_management', 'bcm_governance'],
                'secondary_responders': ['bcm_risk_management'],
                'information_recipients': ['bcm_incident_management', 'bcm_training'],
                'ai_analysis_required': True,
            },

            'risk_threshold_exceeded': {
                'primary_responders': ['bcm_project_management'],
                'secondary_responders': ['bcm_incident_management'],
                'information_recipients': ['bcm_audit', 'bcm_governance'],
                'ai_analysis_required': True,
            },
        }

        strategy = coordination_strategies.get(trigger_event)
        if not strategy:
            return self._default_coordination(trigger_event, context)

        # Get AI analysis if required
        ai_insights = {}
        if strategy.get('ai_analysis_required'):
            bridge = self.env['bcm.ai.bridge'].get_instance()
            ai_insights = bridge.request_analysis(f'coordination_{trigger_event}', context)

        # Coordinate response across all module tiers
        coordination_result = {
            'trigger_event': trigger_event,
            'coordination_id': self._generate_coordination_id(),
            'ai_insights': ai_insights,
            'responses': {},
        }

        # Primary responders - immediate action required
        for module in strategy['primary_responders']:
            response = self._coordinate_primary_response(module, trigger_event, context, ai_insights)
            coordination_result['responses'][module] = {
                'type': 'primary',
                'response': response,
                'timestamp': fields.Datetime.now(),
            }

        # Secondary responders - supporting actions
        for module in strategy['secondary_responders']:
            response = self._coordinate_secondary_response(module, trigger_event, context, ai_insights)
            coordination_result['responses'][module] = {
                'type': 'secondary',
                'response': response,
                'timestamp': fields.Datetime.now(),
            }

        # Information recipients - awareness notifications
        for module in strategy['information_recipients']:
            self._send_information_notification(module, trigger_event, context, ai_insights)

        return coordination_result

    def _coordinate_primary_response(self, module, trigger_event, context, ai_insights):
        """Координирует первичный отклик модуля"""

        event_bus = self.env['bcm.event.bus']
        return event_bus.publish_event(
            f'primary_response_{trigger_event}',
            'bcm_integration_hub',
            {
                'trigger_event': trigger_event,
                'context': context,
                'ai_insights': ai_insights,
                'response_type': 'primary',
                'urgency': 'immediate',
            },
            target_modules=[module],
            priority='critical'
        )

    def _coordinate_secondary_response(self, module, trigger_event, context, ai_insights):
        """Координирует вторичный отклик модуля"""

        event_bus = self.env['bcm.event.bus']
        return event_bus.publish_event(
            f'secondary_response_{trigger_event}',
            'bcm_integration_hub',
            {
                'trigger_event': trigger_event,
                'context': context,
                'ai_insights': ai_insights,
                'response_type': 'secondary',
                'urgency': 'high',
            },
            target_modules=[module],
            priority='high'
        )

    def _send_information_notification(self, module, trigger_event, context, ai_insights):
        """Отправляет информационное уведомление модулю"""

        event_bus = self.env['bcm.event.bus']
        event_bus.publish_event(
            f'information_{trigger_event}',
            'bcm_integration_hub',
            {
                'trigger_event': trigger_event,
                'context': context,
                'ai_insights': ai_insights,
                'notification_type': 'informational',
            },
            target_modules=[module],
            priority='normal'
        )

    # ============== ADAPTIVE LEARNING ==============

    def learn_from_integration_patterns(self):
        """
        Обучение на паттернах интеграции для улучшения координации
        Анализирует успешные и неуспешные интеграции
        """

        # Анализ последних интеграций
        recent_events = self.env['bcm.event.bus'].search([
            ('timestamp', '>=', fields.Datetime.now() - timedelta(days=7))
        ])

        # Группировка по типам событий и результатам
        success_patterns = {}
        failure_patterns = {}

        for event in recent_events:
            event_type = event.event_type
            was_successful = event.state == 'completed'

            if was_successful:
                if event_type not in success_patterns:
                    success_patterns[event_type] = {'count': 0, 'avg_processing_time': 0}
                success_patterns[event_type]['count'] += 1
            else:
                if event_type not in failure_patterns:
                    failure_patterns[event_type] = {'count': 0, 'common_errors': []}
                failure_patterns[event_type]['count'] += 1

        # Отправляем паттерны в Meta-AI для обучения
        bridge = self.env['bcm.ai.bridge'].get_instance()
        bridge.send_learning_data({
            'learning_type': 'integration_patterns',
            'success_patterns': success_patterns,
            'failure_patterns': failure_patterns,
            'analysis_period': '7_days',
            'module': 'bcm_integration_hub',
        })

        return {
            'success_patterns': success_patterns,
            'failure_patterns': failure_patterns,
            'learning_sent': True,
        }

    # ============== UTILITY METHODS ==============

    def _generate_workflow_id(self):
        """Генерирует уникальный ID для workflow"""
        import uuid
        return f"wf_{str(uuid.uuid4())[:8]}"

    def _generate_coordination_id(self):
        """Генерирует уникальный ID для координации"""
        import uuid
        return f"coord_{str(uuid.uuid4())[:8]}"

    def _execute_rollback(self, rollback_strategy, execution_log, data):
        """Выполняет rollback workflow при ошибке"""

        if rollback_strategy == 'compensating_actions':
            # Выполняет компенсирующие действия для каждого выполненного шага
            return self._execute_compensating_actions(execution_log)

        elif rollback_strategy == 'escalation_path':
            # Эскалирует проблему на уровень выше
            return self._escalate_workflow_failure(execution_log, data)

        elif rollback_strategy == 'partial_completion':
            # Принимает частичное выполнение workflow
            return self._handle_partial_completion(execution_log)

        elif rollback_strategy == 'status_restoration':
            # Восстанавливает предыдущие состояния
            return self._restore_previous_states(execution_log, data)

        return {'rollback_strategy': rollback_strategy, 'executed': False}

    def _log_successful_workflow(self, workflow_id, execution_log):
        """Логирует успешно выполненный workflow"""

        _logger.info(f"Workflow {workflow_id} completed successfully with {len(execution_log)} steps")

        # Publish success event for analytics
        event_bus = self.env['bcm.event.bus']
        event_bus.publish_event(
            'workflow_completed_successfully',
            'bcm_integration_hub',
            {
                'workflow_id': workflow_id,
                'steps_count': len(execution_log),
                'execution_log': execution_log,
            },
            priority='normal'
        )

    # ============== API METHODS ==============

    @api.model
    def get_integration_health_dashboard(self):
        """Возвращает данные для dashboard здоровья интеграций"""

        # Получаем статистику событий
        event_bus = self.env['bcm.event.bus']
        event_stats = event_bus.get_event_statistics()

        # Получаем здоровье модулей
        registry = self.env['bcm.module.registry']
        module_health = registry.check_all_modules_health()

        # Формируем dashboard data
        return {
            'total_integrations': self.total_integrations,
            'success_rate': (
                self.successful_integrations / max(self.total_integrations, 1) * 100
            ),
            'event_statistics': event_stats,
            'module_health': module_health,
            'last_sync': self.last_sync,
            'organism_status': self._assess_organism_health(module_health),
        }

    def _assess_organism_health(self, module_health):
        """Оценивает общее здоровье BCM организма"""

        if not module_health:
            return 'unknown'

        healthy_modules = sum(1 for status in module_health.values() if status['healthy'])
        total_modules = len(module_health)

        health_percentage = (healthy_modules / total_modules) * 100

        if health_percentage >= 90:
            return 'excellent'
        elif health_percentage >= 75:
            return 'good'
        elif health_percentage >= 50:
            return 'fair'
        else:
            return 'critical'