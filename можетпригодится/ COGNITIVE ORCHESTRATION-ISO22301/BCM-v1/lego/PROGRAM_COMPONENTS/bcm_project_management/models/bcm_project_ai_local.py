# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class BCMProjectAILocal(models.Model):
    """
    Локальный AI компонент для Project Management модуля.
    Специализируется на проектных задачах, но общается с центральным AI через Bridge
    """
    _name = 'bcm.project.ai.local'
    _description = 'BCM Project Management Local AI'
    _rec_name = 'name'

    name = fields.Char('AI Instance Name', default='Project AI Assistant')
    active = fields.Boolean('Active', default=True)

    # Learning metrics
    tasks_analyzed = fields.Integer('Tasks Analyzed', default=0)
    predictions_made = fields.Integer('Predictions Made', default=0)
    accuracy_rate = fields.Float('Accuracy Rate (%)', default=0.0)
    last_learning_date = fields.Datetime('Last Learning')

    # Local knowledge base
    project_patterns = fields.Json('Learned Project Patterns')
    task_assignment_rules = fields.Json('Task Assignment Rules')
    risk_indicators = fields.Json('Risk Indicators')

    # ============== CORE AI FUNCTIONS ==============

    def analyze_project(self, project):
        """Анализирует проект и дает рекомендации"""
        self.ensure_one()

        # Собираем локальные данные
        local_analysis = self._local_project_analysis(project)

        # Обогащаем через центральный AI
        bridge = self.env['bcm.ai.bridge'].get_instance()
        if bridge:
            central_insights = bridge.request_analysis('project', {
                'project_id': project.id,
                'project_type': project.bcm_type,
                'local_analysis': local_analysis,
                'module': 'bcm_project_management',
            })

            # Объединяем локальный и центральный анализ
            return self._merge_insights(local_analysis, central_insights)

        return local_analysis

    def _local_project_analysis(self, project):
        """Локальный анализ проекта на основе накопленного опыта"""

        insights = {
            'health_factors': [],
            'risks': [],
            'recommendations': [],
            'predicted_completion': None,
        }

        # Анализ здоровья проекта
        if project.tasks_overdue_count > 0:
            insights['health_factors'].append({
                'factor': 'overdue_tasks',
                'severity': 'high' if project.tasks_overdue_count > 5 else 'medium',
                'impact': f'{project.tasks_overdue_count} tasks are overdue',
            })

        # Анализ паттернов из истории
        similar_projects = self._find_similar_projects(project)
        if similar_projects:
            avg_duration = sum(p.duration for p in similar_projects) / len(similar_projects)
            insights['predicted_completion'] = fields.Date.today() + timedelta(days=avg_duration)

        # Рекомендации на основе локального опыта
        if project.health_status == 'critical':
            insights['recommendations'].append({
                'priority': 'high',
                'action': 'escalate',
                'reason': 'Project health is critical',
                'suggested_action': 'Schedule emergency review meeting',
            })

        # Обучение на этом анализе
        self._learn_from_analysis(project, insights)

        return insights

    def suggest_task_assignee(self, task):
        """Предлагает исполнителя для задачи"""
        self.ensure_one()

        # Локальная логика выбора
        local_suggestion = self._local_assignee_suggestion(task)

        # Запрос к центральному AI для валидации
        bridge = self.env['bcm.ai.bridge'].get_instance()
        if bridge:
            validation = bridge.validate_decision('task_assignment', {
                'task_name': task.name,
                'local_suggestion': local_suggestion.id,
                'workload': self._get_user_workload(local_suggestion),
            })

            if validation.get('override'):
                return self.env['res.users'].browse(validation['suggested_user_id'])

        return local_suggestion

    def _local_assignee_suggestion(self, task):
        """Локальная логика выбора исполнителя"""

        # Используем накопленные правила
        if self.task_assignment_rules:
            rules = json.loads(self.task_assignment_rules or '{}')

            # Проверяем правила для типа задачи
            task_type = task.bcm_task_type or 'general'
            if task_type in rules:
                preferred_users = rules[task_type].get('preferred_users', [])
                if preferred_users:
                    # Выбираем наименее загруженного из предпочтительных
                    users = self.env['res.users'].browse(preferred_users)
                    return min(users, key=lambda u: self._get_user_workload(u))

        # Fallback на простую логику
        return task.project_id._find_best_assignee_for_task(task.name)

    def predict_task_duration(self, task):
        """Предсказывает длительность задачи"""
        self.ensure_one()

        # Анализируем похожие выполненные задачи
        similar_tasks = self._find_similar_tasks(task)

        if similar_tasks:
            # Вычисляем среднюю длительность
            durations = []
            for sim_task in similar_tasks:
                if sim_task.date_end and sim_task.date_begin:
                    duration = (sim_task.date_end - sim_task.date_begin).total_seconds() / 3600
                    durations.append(duration)

            if durations:
                avg_duration = sum(durations) / len(durations)

                # Корректируем на основе сложности
                if task.ai_complexity_score:
                    avg_duration *= (1 + task.ai_complexity_score / 10)

                # Отправляем в центральный AI для обучения
                self._send_to_central_learning({
                    'type': 'task_duration_prediction',
                    'task_type': task.bcm_task_type,
                    'predicted_hours': avg_duration,
                    'based_on_samples': len(durations),
                })

                return avg_duration

        # Default на основе типа
        return {'assessment': 8, 'implementation': 16, 'testing': 12}.get(task.bcm_task_type, 8)

    # ============== LEARNING METHODS ==============

    def _learn_from_analysis(self, project, insights):
        """Обучается на основе проведенного анализа"""

        # Обновляем паттерны
        patterns = json.loads(self.project_patterns or '{}')

        project_type = project.bcm_type
        if project_type not in patterns:
            patterns[project_type] = {
                'samples': 0,
                'avg_health_score': 0,
                'common_issues': {},
                'success_factors': [],
            }

        # Обновляем статистику
        type_patterns = patterns[project_type]
        type_patterns['samples'] += 1

        # Обновляем среднее здоровье
        old_avg = type_patterns['avg_health_score']
        new_avg = (old_avg * (type_patterns['samples'] - 1) + project.health_score) / type_patterns['samples']
        type_patterns['avg_health_score'] = new_avg

        # Сохраняем обновленные паттерны
        self.project_patterns = json.dumps(patterns)
        self.tasks_analyzed += len(project.task_ids)
        self.last_learning_date = fields.Datetime.now()

        # Отправляем в центральный AI для мета-обучения
        self._send_to_central_learning({
            'module': 'bcm_project_management',
            'learning_type': 'project_analysis',
            'data': {
                'project_type': project_type,
                'health_score': project.health_score,
                'insights': insights,
            }
        })

    def learn_from_task_completion(self, task):
        """Обучается на завершенной задаче"""
        self.ensure_one()

        # Обновляем правила назначения
        if task.user_ids:
            rules = json.loads(self.task_assignment_rules or '{}')
            task_type = task.bcm_task_type or 'general'

            if task_type not in rules:
                rules[task_type] = {'preferred_users': [], 'success_rate': {}}

            # Отслеживаем успешность исполнителя
            for user in task.user_ids:
                user_id = str(user.id)
                if user_id not in rules[task_type]['success_rate']:
                    rules[task_type]['success_rate'][user_id] = {'completed': 0, 'on_time': 0}

                rules[task_type]['success_rate'][user_id]['completed'] += 1

                if task.date_deadline and task.date_end <= task.date_deadline:
                    rules[task_type]['success_rate'][user_id]['on_time'] += 1

            self.task_assignment_rules = json.dumps(rules)

        # Отправляем в центральную систему
        self._send_to_central_learning({
            'module': 'bcm_project_management',
            'learning_type': 'task_completion',
            'data': {
                'task_type': task.bcm_task_type,
                'duration': (task.date_end - task.date_begin).total_seconds() / 3600 if task.date_begin else 0,
                'user_id': task.user_ids[0].id if task.user_ids else None,
                'completed_on_time': task.date_deadline and task.date_end <= task.date_deadline,
            }
        })

    # ============== HELPER METHODS ==============

    def _find_similar_projects(self, project):
        """Находит похожие завершенные проекты"""
        return self.env['project.project'].search([
            ('bcm_type', '=', project.bcm_type),
            ('id', '!=', project.id),
            ('active', '=', False),  # Завершенные проекты
        ], limit=10)

    def _find_similar_tasks(self, task):
        """Находит похожие завершенные задачи"""
        domain = [
            ('bcm_task_type', '=', task.bcm_task_type),
            ('id', '!=', task.id),
            ('stage_id.fold', '=', True),  # Завершенные
        ]

        if task.project_id.bcm_type:
            domain.append(('project_id.bcm_type', '=', task.project_id.bcm_type))

        return self.env['project.task'].search(domain, limit=20)

    def _get_user_workload(self, user):
        """Получает текущую загрузку пользователя"""
        return self.env['project.task'].search_count([
            ('user_ids', 'in', user.id),
            ('stage_id.fold', '=', False),
        ])

    def _merge_insights(self, local_insights, central_insights):
        """Объединяет локальные и центральные инсайты"""
        if not central_insights:
            return local_insights

        merged = dict(local_insights)

        # Объединяем рекомендации
        if 'recommendations' in central_insights:
            merged['recommendations'].extend(central_insights['recommendations'])

        # Используем более точное предсказание от центрального AI
        if 'predicted_completion' in central_insights:
            merged['predicted_completion'] = central_insights['predicted_completion']

        # Добавляем центральные риски
        if 'risks' in central_insights:
            merged['risks'].extend(central_insights['risks'])

        return merged

    def _send_to_central_learning(self, data):
        """Отправляет данные для обучения в центральный AI"""
        try:
            bridge = self.env['bcm.ai.bridge'].get_instance()
            if bridge:
                bridge.send_learning_data(data)
                self.predictions_made += 1
        except Exception as e:
            _logger.warning(f"Could not send to central AI: {str(e)}")

    # ============== CRON METHODS ==============

    @api.model
    def _cron_sync_with_central_ai(self):
        """Периодическая синхронизация с центральным AI"""
        local_ai = self.search([('active', '=', True)], limit=1)
        if not local_ai:
            return

        bridge = self.env['bcm.ai.bridge'].get_instance()
        if bridge:
            # Получаем обновленные модели и правила
            updates = bridge.get_model_updates('bcm_project_management')

            if updates:
                # Обновляем локальные правила
                if 'assignment_rules' in updates:
                    local_ai.task_assignment_rules = json.dumps(updates['assignment_rules'])

                if 'patterns' in updates:
                    local_ai.project_patterns = json.dumps(updates['patterns'])

                if 'accuracy' in updates:
                    local_ai.accuracy_rate = updates['accuracy']

                _logger.info("Project AI synchronized with central system")