# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import logging

_logger = logging.getLogger(__name__)


class BCMModuleRegistry(models.Model):
    """
    BCM Module Registry - реестр всех BCM модулей в системе
    Отслеживает какие модули установлены, их возможности и состояние
    """
    _name = 'bcm.module.registry'
    _description = 'BCM Module Registry for Integration Management'
    _rec_name = 'module_name'

    # Module identification
    module_name = fields.Char('Module Name', required=True, unique=True)
    technical_name = fields.Char('Technical Name', required=True)
    display_name = fields.Char('Display Name')
    version = fields.Char('Version')

    # Module status
    is_active = fields.Boolean('Active', default=True)
    is_installed = fields.Boolean('Installed', compute='_compute_installation_status')
    health_status = fields.Selection([
        ('healthy', 'Healthy'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('offline', 'Offline'),
    ], string='Health Status', default='healthy')

    # Integration capabilities
    supports_events = fields.Boolean('Supports Events', default=False)
    event_handler_model = fields.Char('Event Handler Model')
    provided_events = fields.Json('Provided Events', help='List of event types this module can generate')
    consumed_events = fields.Json('Consumed Events', help='List of event types this module can handle')

    # AI integration
    has_local_ai = fields.Boolean('Has Local AI', default=False)
    ai_model_name = fields.Char('AI Model Name')
    ai_capabilities = fields.Json('AI Capabilities', help='List of AI capabilities this module provides')

    # API endpoints
    api_endpoints = fields.Json('API Endpoints', help='List of API endpoints this module provides')
    webhook_urls = fields.Json('Webhook URLs', help='List of webhook URLs this module supports')

    # Dependencies and relationships
    depends_on = fields.Json('Module Dependencies')
    provides_for = fields.Json('Modules This Serves')

    # Monitoring
    last_health_check = fields.Datetime('Last Health Check')
    uptime_percentage = fields.Float('Uptime %', default=100.0)
    error_count_24h = fields.Integer('Errors (24h)', default=0)

    # Configuration
    configuration = fields.Json('Module Configuration')
    feature_flags = fields.Json('Feature Flags')

    # ============== COMPUTED FIELDS ==============

    @api.depends('technical_name')
    def _compute_installation_status(self):
        """Проверяет установлен ли модуль"""
        for record in self:
            try:
                module = self.env['ir.module.module'].search([
                    ('name', '=', record.technical_name)
                ], limit=1)
                record.is_installed = module and module.state == 'installed'
            except:
                record.is_installed = False

    # ============== MODULE DISCOVERY ==============

    @api.model
    def discover_bcm_modules(self):
        """Автоматически обнаруживает все BCM модули в системе"""

        # Список известных BCM модулей
        known_bcm_modules = [
            {
                'module_name': 'BCM Project Management',
                'technical_name': 'bcm_project_management',
                'display_name': 'Project Management',
                'supports_events': True,
                'event_handler_model': 'bcm.project.event.handler',
                'has_local_ai': True,
                'ai_model_name': 'bcm.project.ai.local',
                'provided_events': [
                    'project_created', 'project_health_changed', 'project_escalated',
                    'task_assigned', 'task_completed'
                ],
                'consumed_events': [
                    'risk_identified', 'incident_created', 'audit_finding_created',
                    'ai_insight_generated'
                ],
                'ai_capabilities': [
                    'project_analysis', 'task_assignment', 'duration_prediction',
                    'health_monitoring', 'risk_detection'
                ],
            },
            {
                'module_name': 'BCM Risk Management',
                'technical_name': 'bcm_risk_management',
                'display_name': 'Risk Management',
                'supports_events': True,
                'event_handler_model': 'bcm.risk.event.handler',
                'has_local_ai': True,
                'ai_model_name': 'bcm.risk.ai.local',
                'provided_events': [
                    'risk_identified', 'risk_level_changed', 'risk_mitigation_required'
                ],
                'consumed_events': [
                    'project_created', 'incident_created', 'audit_finding_created'
                ],
                'ai_capabilities': [
                    'risk_assessment', 'impact_analysis', 'mitigation_planning'
                ],
            },
            {
                'module_name': 'BCM Incident Management',
                'technical_name': 'bcm_incident_management',
                'display_name': 'Incident Management',
                'supports_events': True,
                'event_handler_model': 'bcm.incident.event.handler',
                'has_local_ai': True,
                'ai_model_name': 'bcm.incident.ai.local',
                'provided_events': [
                    'incident_created', 'incident_escalated', 'recovery_initiated'
                ],
                'consumed_events': [
                    'project_health_changed', 'risk_level_changed'
                ],
                'ai_capabilities': [
                    'incident_classification', 'impact_assessment', 'response_planning'
                ],
            },
            {
                'module_name': 'BCM Audit & Compliance',
                'technical_name': 'bcm_audit',
                'display_name': 'Audit & Compliance',
                'supports_events': True,
                'event_handler_model': 'bcm.audit.event.handler',
                'has_local_ai': True,
                'ai_model_name': 'bcm.audit.ai.local',
                'provided_events': [
                    'audit_finding_created', 'compliance_issue', 'corrective_action_required'
                ],
                'consumed_events': [
                    'project_created', 'risk_identified', 'incident_created'
                ],
                'ai_capabilities': [
                    'compliance_monitoring', 'audit_planning', 'finding_analysis'
                ],
            },
        ]

        # Регистрируем или обновляем модули
        for module_info in known_bcm_modules:
            existing = self.search([('technical_name', '=', module_info['technical_name'])])

            if existing:
                # Обновляем существующий
                existing.write(module_info)
            else:
                # Создаем новый
                self.create(module_info)

        _logger.info(f"Discovered and registered {len(known_bcm_modules)} BCM modules")

    # ============== MODULE MANAGEMENT ==============

    @api.model
    def register_module(self, module_info):
        """Регистрирует новый модуль в реестре"""

        existing = self.search([('technical_name', '=', module_info['technical_name'])])

        if existing:
            existing.write(module_info)
            action = 'updated'
        else:
            self.create(module_info)
            action = 'registered'

        _logger.info(f"Module {module_info['technical_name']} {action}")

        # Публикуем событие о регистрации модуля
        self.env['bcm.event.bus'].publish_event(
            'module_registered',
            'bcm_ai_bridge',
            {
                'module_name': module_info['technical_name'],
                'action': action,
                'capabilities': module_info.get('ai_capabilities', []),
            }
        )

        return existing if existing else self.search([('technical_name', '=', module_info['technical_name'])])

    def activate_module(self):
        """Активирует модуль"""
        self.ensure_one()
        self.is_active = True

        # Публикуем событие активации
        self.env['bcm.event.bus'].publish_event(
            'module_activated',
            'bcm_ai_bridge',
            {'module_name': self.technical_name}
        )

    def deactivate_module(self):
        """Деактивирует модуль"""
        self.ensure_one()
        self.is_active = False

    # ============== HEALTH MONITORING ==============

    def check_health(self):
        """Проверяет здоровье модуля"""
        self.ensure_one()

        try:
            # Проверяем установлен ли модуль
            if not self.is_installed:
                self.health_status = 'offline'
                return False

            # Проверяем доступность event handler'а
            if self.supports_events and self.event_handler_model:
                if self.event_handler_model not in self.env:
                    self.health_status = 'error'
                    return False

            # Проверяем AI компоненты
            if self.has_local_ai and self.ai_model_name:
                if self.ai_model_name not in self.env:
                    self.health_status = 'warning'
                else:
                    # Проверяем активность AI
                    ai_instances = self.env[self.ai_model_name].search([('active', '=', True)])
                    if not ai_instances:
                        self.health_status = 'warning'

            # Если все проверки прошли
            if self.health_status != 'error':
                self.health_status = 'healthy'

            self.last_health_check = fields.Datetime.now()
            return self.health_status == 'healthy'

        except Exception as e:
            _logger.error(f"Health check failed for {self.technical_name}: {str(e)}")
            self.health_status = 'error'
            return False

    @api.model
    def check_all_modules_health(self):
        """Проверяет здоровье всех активных модулей"""
        active_modules = self.search([('is_active', '=', True)])

        health_report = {}
        for module in active_modules:
            is_healthy = module.check_health()
            health_report[module.technical_name] = {
                'healthy': is_healthy,
                'status': module.health_status,
                'last_check': module.last_health_check,
            }

        # Публикуем общий отчет о здоровье
        self.env['bcm.event.bus'].publish_event(
            'integration_health_check',
            'bcm_ai_bridge',
            {'health_report': health_report},
            priority='normal'
        )

        return health_report

    # ============== QUERIES ==============

    @api.model
    def get_all_active_modules(self):
        """Возвращает список всех активных модулей"""
        return self.search([('is_active', '=', True)]).mapped('technical_name')

    @api.model
    def get_modules_with_ai(self):
        """Возвращает модули с AI возможностями"""
        return self.search([
            ('is_active', '=', True),
            ('has_local_ai', '=', True)
        ])

    @api.model
    def get_modules_for_event(self, event_type):
        """Находит модули, которые могут обработать данный тип события"""
        modules = self.search([('is_active', '=', True)])

        interested_modules = []
        for module in modules:
            consumed_events = module.consumed_events or []
            if event_type in consumed_events:
                interested_modules.append(module.technical_name)

        return interested_modules

    @api.model
    def get_integration_map(self):
        """Возвращает карту интеграций между модулями"""
        active_modules = self.search([('is_active', '=', True)])

        integration_map = {}
        for module in active_modules:
            integration_map[module.technical_name] = {
                'provides': module.provided_events or [],
                'consumes': module.consumed_events or [],
                'ai_capabilities': module.ai_capabilities or [],
                'health': module.health_status,
            }

        return integration_map

    # ============== CRON METHODS ==============

    @api.model
    def _cron_health_monitoring(self):
        """Cron job для мониторинга здоровья модулей"""
        return self.check_all_modules_health()

    @api.model
    def _cron_rediscover_modules(self):
        """Переобнаружение модулей (на случай установки новых)"""
        return self.discover_bcm_modules()