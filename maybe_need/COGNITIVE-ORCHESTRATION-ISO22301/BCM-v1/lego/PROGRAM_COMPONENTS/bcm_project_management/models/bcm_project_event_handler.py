# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import logging

_logger = logging.getLogger(__name__)


class BCMProjectEventHandler(models.Model):
    """
    BCM Project Event Handler - превращает Project Management в "орган" BCM организма
    Обрабатывает события от других модулей и интегрируется с общей экосистемой
    """
    _name = 'bcm.project.event.handler'
    _description = 'BCM Project Event Handler for Inter-Module Integration'

    name = fields.Char('Handler Name', default='Project Management Event Handler')
    active = fields.Boolean('Active', default=True)

    # Event handling statistics
    events_processed = fields.Integer('Events Processed', default=0)
    last_event_processed = fields.Datetime('Last Event Processed')

    # ============== EVENT HANDLING CORE ==============

    @api.model
    def handle_event(self, event_type, event_data, source_module):
        """
        Главная функция обработки событий от других модулей
        Превращает проектный модуль в реактивный орган организма
        """

        handler_map = {
            # События от Risk Management
            'risk_identified': self._handle_risk_identified,
            'risk_level_changed': self._handle_risk_level_changed,
            'risk_mitigation_required': self._handle_risk_mitigation_required,

            # События от Incident Management
            'incident_created': self._handle_incident_created,
            'incident_escalated': self._handle_incident_escalated,
            'recovery_initiated': self._handle_recovery_initiated,

            # События от Audit
            'audit_finding_created': self._handle_audit_finding,
            'compliance_issue': self._handle_compliance_issue,
            'corrective_action_required': self._handle_corrective_action,

            # AI Events
            'ai_insight_generated': self._handle_ai_insight,
            'ai_recommendation_made': self._handle_ai_recommendation,

            # Workflow Events
            'workflow_step_create_mitigation_project': self._handle_workflow_create_project,
            'workflow_step_activate_recovery_project': self._handle_workflow_activate_recovery,
            'workflow_step_create_corrective_action_project': self._handle_workflow_corrective_action,

            # Response Events
            'primary_response_critical_project_health': self._handle_primary_critical_response,
            'secondary_response_high_severity_incident': self._handle_secondary_incident_response,
        }

        handler = handler_map.get(event_type)

        if handler:
            try:
                result = handler(event_data, source_module)
                self._update_processing_stats(True)

                _logger.info(f"Successfully handled event {event_type} from {source_module}")
                return result

            except Exception as e:
                _logger.error(f"Failed to handle event {event_type}: {str(e)}")
                self._update_processing_stats(False)
                return {'success': False, 'error': str(e)}

        # Unknown event type - log and ignore
        _logger.warning(f"Unknown event type {event_type} from {source_module}")
        return {'success': False, 'error': 'Unknown event type'}

    # ============== RISK MANAGEMENT INTEGRATION ==============

    def _handle_risk_identified(self, event_data, source_module):
        """
        Обработка события: Выявлен новый риск -> Создать проект митигации
        Автоматически реагируем на риски созданием проектов
        """

        risk_level = event_data.get('risk_level', 'medium')
        risk_category = event_data.get('category', 'unknown')
        risk_description = event_data.get('description', 'New risk identified')

        # Создаем проект митигации только для высоких и критичных рисков
        if risk_level in ['high', 'critical']:

            # Используем AI для определения параметров проекта
            ai_local = self.env['bcm.project.ai.local'].search([('active', '=', True)], limit=1)
            if ai_local:
                project_params = ai_local._analyze_risk_for_project_creation(event_data)
            else:
                project_params = self._default_risk_project_params(risk_level, risk_category)

            # Создаем проект митигации риска
            project = self.env['project.project'].create({
                'name': f"Risk Mitigation: {risk_description[:50]}",
                'bcm_type': 'improvement',  # или специальный тип 'risk_mitigation'
                'criticality_level': 'high' if risk_level == 'critical' else 'medium',
                'description': f"Automated project created to mitigate {risk_level} risk: {risk_description}",
                'auto_assign': True,
                'auto_escalate': True,
                'source_risk_id': event_data.get('risk_id'),
                'source_module': source_module,
            })

            # Автоматически генерируем задачи на основе категории риска
            self._generate_risk_mitigation_tasks(project, risk_category, event_data)

            # Публикуем событие о создании проекта
            self._publish_project_created_event(project, 'risk_mitigation')

            return {
                'success': True,
                'action': 'project_created',
                'project_id': project.id,
                'output_data': {'mitigation_project_id': project.id},
            }

        # Для низких рисков просто логируем
        return {
            'success': True,
            'action': 'risk_logged',
            'message': f"Low priority risk logged, no project created",
        }

    def _handle_risk_level_changed(self, event_data, source_module):
        """Обработка изменения уровня риска - может потребовать эскалация проекта"""

        risk_id = event_data.get('risk_id')
        new_level = event_data.get('new_risk_level')
        old_level = event_data.get('old_risk_level')

        # Находим связанный проект по risk_id
        related_project = self.env['project.project'].search([
            ('source_risk_id', '=', risk_id),
            ('active', '=', True)
        ], limit=1)

        if related_project:
            # Обновляем критичность проекта
            new_criticality = 'high' if new_level == 'critical' else 'medium' if new_level == 'high' else 'low'
            related_project.criticality_level = new_criticality

            # Если риск повысился до критичного - эскалируем проект
            if new_level == 'critical' and old_level != 'critical':
                related_project.action_escalate()

            return {
                'success': True,
                'action': 'project_updated',
                'project_id': related_project.id,
            }

        return {'success': True, 'action': 'no_related_project'}

    # ============== INCIDENT MANAGEMENT INTEGRATION ==============

    def _handle_incident_created(self, event_data, source_module):
        """Обработка создания инцидента - создаем проект реагирования"""

        incident_severity = event_data.get('severity', 'medium')
        incident_type = event_data.get('incident_type', 'unknown')

        # Для средних и высоких инцидентов создаем проекты реагирования
        if incident_severity in ['medium', 'high', 'critical']:

            project = self.env['project.project'].create({
                'name': f"Incident Response: {event_data.get('incident_name', 'Unknown')}",
                'bcm_type': 'incident',
                'criticality_level': incident_severity,
                'description': f"Response project for {incident_severity} incident",
                'auto_assign': True,
                'auto_escalate': True if incident_severity == 'critical' else False,
                'source_incident_id': event_data.get('incident_id'),
                'source_module': source_module,
            })

            # Генерируем задачи реагирования на инцидент
            self._generate_incident_response_tasks(project, incident_type, event_data)

            self._publish_project_created_event(project, 'incident_response')

            return {
                'success': True,
                'action': 'response_project_created',
                'project_id': project.id,
                'output_data': {'response_project_id': project.id},
            }

        return {'success': True, 'action': 'low_priority_incident'}

    def _handle_recovery_initiated(self, event_data, source_module):
        """Обработка инициации восстановления - создаем проект восстановления"""

        project = self.env['project.project'].create({
            'name': f"Recovery: {event_data.get('incident_name', 'System Recovery')}",
            'bcm_type': 'recovery',
            'criticality_level': 'high',
            'description': "Recovery project initiated by incident management",
            'auto_assign': True,
            'auto_escalate': True,
            'recovery_time_objective': event_data.get('rto', 4.0),
            'recovery_point_objective': event_data.get('rpo', 1.0),
            'maximum_tolerable_downtime': event_data.get('mtd', 24.0),
            'source_incident_id': event_data.get('incident_id'),
        })

        # Создаем задачи восстановления
        self._generate_recovery_tasks(project, event_data)

        self._publish_project_created_event(project, 'recovery')

        return {
            'success': True,
            'action': 'recovery_project_created',
            'project_id': project.id,
            'output_data': {'recovery_project_id': project.id},
        }

    # ============== AUDIT INTEGRATION ==============

    def _handle_audit_finding(self, event_data, source_module):
        """Обработка аудиторской находки - создаем корректирующий проект"""

        finding_severity = event_data.get('severity', 'medium')

        if finding_severity in ['high', 'critical']:
            project = self.env['project.project'].create({
                'name': f"Corrective Action: {event_data.get('finding_title', 'Audit Finding')}",
                'bcm_type': 'improvement',
                'criticality_level': finding_severity,
                'description': f"Corrective action for audit finding: {event_data.get('description', '')}",
                'source_audit_finding_id': event_data.get('finding_id'),
            })

            # Генерируем задачи корректирующих действий
            self._generate_corrective_action_tasks(project, event_data)

            self._publish_project_created_event(project, 'corrective_action')

            return {
                'success': True,
                'action': 'corrective_project_created',
                'project_id': project.id,
                'output_data': {'corrective_project_id': project.id},
            }

        return {'success': True, 'action': 'low_priority_finding'}

    # ============== AI INTEGRATION ==============

    def _handle_ai_insight(self, event_data, source_module):
        """Обработка AI инсайтов - обновляем проекты на основе рекомендаций"""

        insight_type = event_data.get('insight_type')
        project_id = event_data.get('project_id')
        recommendation = event_data.get('recommendation', {})

        if project_id:
            project = self.env['project.project'].browse(project_id)
            if project.exists():
                # Обновляем AI инсайты проекта
                project.ai_insights = json.dumps(recommendation)

                # Если есть критические рекомендации - создаем задачи
                if recommendation.get('priority') == 'critical':
                    self._create_tasks_from_ai_recommendation(project, recommendation)

                return {
                    'success': True,
                    'action': 'project_updated_with_insights',
                    'project_id': project_id,
                }

        return {'success': True, 'action': 'no_target_project'}

    # ============== WORKFLOW HANDLERS ==============

    def _handle_workflow_create_project(self, event_data, source_module):
        """Обработчик workflow шага создания проекта"""

        workflow_id = event_data.get('workflow_id')
        step_data = event_data.get('data', {})

        # Определяем тип проекта на основе workflow данных
        project_type = self._determine_project_type_from_workflow(step_data)

        project = self.env['project.project'].create({
            'name': f"Workflow Project: {workflow_id}",
            'bcm_type': project_type,
            'description': f"Project created by workflow {workflow_id}",
            'workflow_id': workflow_id,
        })

        return {
            'success': True,
            'result': f"Created project {project.id} for workflow {workflow_id}",
            'output_data': {'created_project_id': project.id},
        }

    # ============== TASK GENERATION ==============

    def _generate_risk_mitigation_tasks(self, project, risk_category, risk_data):
        """Генерирует задачи для проекта митигации риска"""

        task_templates = {
            'technical': [
                'Assess technical risk impact',
                'Develop technical mitigation plan',
                'Implement security controls',
                'Test mitigation measures',
            ],
            'operational': [
                'Review operational procedures',
                'Update process documentation',
                'Train staff on new procedures',
                'Monitor operational metrics',
            ],
            'compliance': [
                'Review compliance requirements',
                'Update policies and procedures',
                'Conduct compliance assessment',
                'Report to regulatory bodies',
            ],
        }

        tasks = task_templates.get(risk_category, task_templates['operational'])

        for i, task_name in enumerate(tasks):
            self.env['project.task'].create({
                'name': task_name,
                'project_id': project.id,
                'bcm_task_type': 'assessment' if 'assess' in task_name.lower() else 'implementation',
                'sequence': i + 1,
                'description': f"Task generated for {risk_category} risk mitigation",
            })

    def _generate_incident_response_tasks(self, project, incident_type, incident_data):
        """Генерирует задачи для проекта реагирования на инцидент"""

        base_tasks = [
            'Assess incident impact',
            'Activate response team',
            'Implement containment measures',
            'Communicate with stakeholders',
            'Document incident details',
            'Conduct post-incident review',
        ]

        for i, task_name in enumerate(base_tasks):
            self.env['project.task'].create({
                'name': task_name,
                'project_id': project.id,
                'bcm_task_type': 'assessment' if 'assess' in task_name.lower() else 'implementation',
                'sequence': i + 1,
            })

    # ============== UTILITY METHODS ==============

    def _publish_project_created_event(self, project, creation_reason):
        """Публикует событие о создании проекта для других модулей"""

        event_bus = self.env['bcm.event.bus']
        event_bus.publish_event(
            'project_created',
            'bcm_project_management',
            {
                'project_id': project.id,
                'project_name': project.name,
                'bcm_type': project.bcm_type,
                'criticality_level': project.criticality_level,
                'creation_reason': creation_reason,
            },
            priority='normal'
        )

    def _update_processing_stats(self, success):
        """Обновляет статистику обработки событий"""
        self.events_processed += 1
        self.last_event_processed = fields.Datetime.now()

        if not success:
            _logger.warning("Event processing failed - check logs")

    def _default_risk_project_params(self, risk_level, risk_category):
        """Возвращает параметры по умолчанию для проекта митигации риска"""
        return {
            'estimated_duration': 30 if risk_level == 'critical' else 60,  # days
            'team_size': 3 if risk_level == 'critical' else 2,
            'budget_estimate': 10000 if risk_level == 'critical' else 5000,
        }

    def _determine_project_type_from_workflow(self, workflow_data):
        """Определяет тип проекта на основе данных workflow"""

        if 'risk' in str(workflow_data).lower():
            return 'improvement'
        elif 'incident' in str(workflow_data).lower():
            return 'incident'
        elif 'audit' in str(workflow_data).lower():
            return 'audit'
        else:
            return 'improvement'  # default