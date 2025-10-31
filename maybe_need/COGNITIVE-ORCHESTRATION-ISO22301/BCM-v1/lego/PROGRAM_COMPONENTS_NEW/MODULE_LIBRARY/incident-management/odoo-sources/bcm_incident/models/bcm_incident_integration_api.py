# -*- coding: utf-8 -*-
"""
BCM Incident Integration API
=============================
Provides hooks and APIs for other modules to integrate with bcm_incident
"""

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class BCMIncidentIntegrationAPI(models.AbstractModel):
    """API абстрактная модель для интеграции с инцидентами"""
    _name = 'bcm.incident.integration.api'
    _description = 'BCM Incident Integration API'

    @api.model
    def register_incident_hook(self, module_name, hook_type, callback):
        """
        Регистрация hook'а для интеграции с инцидентами

        Args:
            module_name: Имя модуля, регистрирующего hook
            hook_type: Тип hook'а ('on_create', 'on_update', 'on_close', 'on_escalate')
            callback: Функция обратного вызова
        """
        hooks = self.env['ir.config_parameter'].sudo().get_param(
            'bcm.incident.integration.hooks', '{}'
        )

        try:
            import json
            hooks = json.loads(hooks)
            if module_name not in hooks:
                hooks[module_name] = {}
            hooks[module_name][hook_type] = str(callback)

            self.env['ir.config_parameter'].sudo().set_param(
                'bcm.incident.integration.hooks',
                json.dumps(hooks)
            )
            _logger.info(f"Registered {hook_type} hook for {module_name}")
            return True

        except Exception as e:
            _logger.error(f"Failed to register hook: {e}")
            return False

    @api.model
    def get_incident_data_for_integration(self, incident_id):
        """
        Получение данных инцидента для интеграции

        Returns:
            dict: Структурированные данные инцидента
        """
        incident = self.env['bcm.incident'].browse(incident_id)
        if not incident.exists():
            return {}

        return {
            'id': incident.id,
            'name': incident.name,
            'incident_number': incident.incident_number,
            'severity': incident.severity,
            'status': incident.status,
            'incident_type': incident.incident_type,
            'description': incident.description,
            'create_date': str(incident.create_date),
            'detected_date': str(incident.detected_date) if incident.detected_date else None,
            'response_date': str(incident.response_date) if incident.response_date else None,
            'resolution_date': str(incident.resolution_date) if incident.resolution_date else None,
            'ai_classification': incident.ai_classification,
            'ai_confidence': incident.ai_classification_confidence,
            'ai_risk_score': incident.ai_risk_score,
            'digital_twin_sync': incident.digital_twin_sync,
            'affected_systems': incident.affected_systems,
            'business_impact': incident.business_impact,
            'recovery_actions': incident.recovery_actions,
            'lessons_learned': incident.lessons_learned,
            'response_team_ids': incident.response_team_ids.ids,
            'escalation_level': incident.escalation_level,
        }

    @api.model
    def trigger_incident_simulation(self, incident_id):
        """
        Запуск симуляции инцидента для Digital Twin

        Args:
            incident_id: ID инцидента

        Returns:
            dict: Результат запуска симуляции
        """
        incident = self.env['bcm.incident'].browse(incident_id)
        if not incident.exists():
            return {'success': False, 'error': 'Incident not found'}

        # Проверяем наличие Digital Twin модуля
        if 'bcm.digital.twin.simulation' in self.env:
            try:
                simulation = self.env['bcm.digital.twin.simulation'].create({
                    'name': f"Simulation for {incident.name}",
                    'related_incident': incident.id,
                    'simulation_type': 'crisis_management',
                    'scenario_description': incident.description,
                })
                simulation.action_start_simulation()

                return {
                    'success': True,
                    'simulation_id': simulation.id,
                    'message': f"Simulation {simulation.name} started"
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        else:
            return {'success': False, 'error': 'Digital Twin module not installed'}

    @api.model
    def sync_with_external_system(self, incident_id, system_type):
        """
        Синхронизация инцидента с внешней системой

        Args:
            incident_id: ID инцидента
            system_type: Тип системы ('thehive', 'servicenow', 'jira', etc.)

        Returns:
            dict: Результат синхронизации
        """
        incident = self.env['bcm.incident'].browse(incident_id)
        if not incident.exists():
            return {'success': False, 'error': 'Incident not found'}

        incident_data = self.get_incident_data_for_integration(incident_id)

        # Здесь можно добавить интеграцию с конкретными системами
        integration_methods = {
            'thehive': '_sync_with_thehive',
            'servicenow': '_sync_with_servicenow',
            'jira': '_sync_with_jira',
            'digital_twin': '_sync_with_digital_twin',
        }

        method_name = integration_methods.get(system_type)
        if method_name and hasattr(self, method_name):
            return getattr(self, method_name)(incident_data)
        else:
            return {'success': False, 'error': f'Integration with {system_type} not configured'}

    def _sync_with_digital_twin(self, incident_data):
        """Синхронизация с Digital Twin"""
        if 'bcm.digital.twin.core' in self.env:
            try:
                # Ищем или создаем цифровую копию инцидента
                digital_copy = self.env['bcm.digital.copy'].search([
                    ('source_model', '=', 'bcm.incident'),
                    ('source_record_id', '=', incident_data['id'])
                ], limit=1)

                if not digital_copy:
                    digital_copy = self.env['bcm.digital.copy'].create({
                        'name': f"Digital Copy: {incident_data['name']}",
                        'source_model': 'bcm.incident',
                        'source_record_id': incident_data['id'],
                        'copy_type': 'incident',
                        'data_snapshot': str(incident_data),
                    })
                else:
                    digital_copy.write({
                        'data_snapshot': str(incident_data),
                        'last_sync': fields.Datetime.now(),
                    })

                # Запускаем синхронизацию
                digital_copy.action_sync()

                return {
                    'success': True,
                    'digital_copy_id': digital_copy.id,
                    'message': 'Successfully synced with Digital Twin'
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        else:
            return {'success': False, 'error': 'Digital Twin module not available'}

    @api.model
    def get_ai_recommendations(self, incident_id):
        """
        Получение AI рекомендаций для инцидента

        Args:
            incident_id: ID инцидента

        Returns:
            list: Список рекомендаций
        """
        incident = self.env['bcm.incident'].browse(incident_id)
        if not incident.exists():
            return []

        recommendations = []

        # Базовые рекомендации на основе типа и серьезности
        if incident.severity == 'critical':
            recommendations.append({
                'type': 'escalation',
                'priority': 'high',
                'action': 'Immediately escalate to Crisis Management Team',
                'reason': 'Critical severity requires immediate senior attention'
            })

        if incident.incident_type == 'cyber':
            recommendations.append({
                'type': 'isolation',
                'priority': 'high',
                'action': 'Isolate affected systems from network',
                'reason': 'Prevent lateral movement and data exfiltration'
            })

        if not incident.response_team_ids:
            recommendations.append({
                'type': 'team_activation',
                'priority': 'medium',
                'action': 'Activate appropriate response team',
                'reason': 'No response team currently assigned'
            })

        # AI анализ похожих инцидентов
        similar_incidents = self.env['bcm.incident'].search([
            ('incident_type', '=', incident.incident_type),
            ('severity', '=', incident.severity),
            ('status', 'in', ['resolved', 'closed']),
            ('id', '!=', incident.id)
        ], limit=5)

        if similar_incidents:
            avg_resolution_time = sum(
                (inc.resolution_date - inc.create_date).total_seconds() / 3600
                for inc in similar_incidents if inc.resolution_date
            ) / len(similar_incidents)

            recommendations.append({
                'type': 'timeline',
                'priority': 'low',
                'action': f'Expected resolution time: {avg_resolution_time:.1f} hours',
                'reason': f'Based on {len(similar_incidents)} similar resolved incidents'
            })

        return recommendations


class BCMIncidentIntegrationMixin(models.AbstractModel):
    """Mixin для добавления интеграционных возможностей в другие модули"""
    _name = 'bcm.incident.integration.mixin'
    _description = 'BCM Incident Integration Mixin'

    incident_integration_enabled = fields.Boolean(
        string='Incident Integration Enabled',
        default=False
    )

    linked_incident_ids = fields.Many2many(
        'bcm.incident',
        string='Linked Incidents',
        help='Incidents linked to this record'
    )

    def create_linked_incident(self, incident_data):
        """
        Создание связанного инцидента

        Args:
            incident_data: Данные для создания инцидента

        Returns:
            bcm.incident: Созданный инцидент
        """
        incident = self.env['bcm.incident'].create(incident_data)
        self.linked_incident_ids = [(4, incident.id)]
        return incident

    def link_to_incident(self, incident_id):
        """Связывание с существующим инцидентом"""
        self.linked_incident_ids = [(4, incident_id)]