# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ScenarioApplyWizard(models.TransientModel):
    """Мастер-виджет применения сценария к клиенту"""
    _name = 'bcm.scenario.apply.wizard'
    _description = 'Scenario Application Wizard'
    
    # Основные поля
    scenario_id = fields.Many2one(
        'bcm.scenario', 
        string='Scenario',
        required=True,
        readonly=True
    )
    
    client_id = fields.Many2one(
        'bcm.client',
        string='Target Client',
        required=True,
        help='Client to apply this scenario to'
    )
    
    application_type = fields.Selection([
        ('exercise', 'Create Exercise'),
        ('plan', 'Create BCM Plan'),
        ('template', 'Create Template'),
        ('assessment', 'Risk Assessment')
    ], string='Application Type', required=True, default='exercise')
    
    # Параметры применения
    name = fields.Char(
        string='Name',
        required=True,
        help='Name for the created resource'
    )
    
    description = fields.Text(
        string='Description',
        help='Additional description for the application'
    )
    
    # Параметризация через JSONSchema
    scenario_parameters = fields.Text(
        string='Scenario Parameters',
        help='JSON parameters for scenario customization'
    )
    
    parameter_values = fields.Text(
        string='Parameter Values',
        help='JSON values provided by user for parameters'
    )
    
    # Планирование
    scheduled_date = fields.Datetime(
        string='Scheduled Date',
        help='When to execute/implement this scenario'
    )
    
    duration_hours = fields.Float(
        string='Expected Duration (Hours)',
        default=2.0
    )
    
    # Участники (для учений)
    participant_ids = fields.Many2many(
        'res.users',
        string='Participants',
        help='Users who will participate in this scenario'
    )
    
    # Настройки симуляции
    simulation_enabled = fields.Boolean(
        string='Enable Simulation',
        default=False,
        help='Use sim_adapter for realistic simulation'
    )
    
    simulation_config = fields.Text(
        string='Simulation Configuration',
        help='Configuration for simulation engine'
    )
    
    # AI настройки
    ai_adaptation = fields.Boolean(
        string='AI Adaptation',
        default=True,
        help='Use AI to adapt scenario to client context'
    )
    
    adaptation_notes = fields.Text(
        string='AI Adaptation Notes',
        readonly=True,
        help='Notes from AI adaptation process'
    )
    
    # Состояние мастера
    state = fields.Selection([
        ('configure', 'Configure Parameters'),
        ('customize', 'Customize & Adapt'),
        ('review', 'Review & Confirm'),
        ('applying', 'Applying...'),
        ('done', 'Completed')
    ], string='State', default='configure')
    
    # Результат применения
    created_resource_id = fields.Integer(string='Created Resource ID')
    created_resource_model = fields.Char(string='Created Resource Model')
    
    @api.model
    def default_get(self, fields_list):
        """Получить значения по умолчанию из контекста"""
        defaults = super().default_get(fields_list)
        
        # Получить сценарий из контекста
        scenario_id = self._context.get('active_id') or self._context.get('scenario_id')
        if scenario_id:
            scenario = self.env['bcm.scenario'].browse(scenario_id)
            defaults['scenario_id'] = scenario_id
            defaults['name'] = f"{scenario.title} - Application"
            defaults['description'] = scenario.content_md[:500] if scenario.content_md else ''
            defaults['duration_hours'] = scenario.execution_time_hours or 2.0
            
            # Установить параметры сценария
            if scenario.scenario_parameters:
                defaults['scenario_parameters'] = scenario.scenario_parameters
        
        # Попытаться определить клиента из пользователя
        user_client = self.env['bcm.client.contact'].search([
            ('user_id', '=', self.env.uid)
        ], limit=1)
        if user_client:
            defaults['client_id'] = user_client.client_id.id
        
        return defaults
    
    @api.onchange('scenario_id')
    def _onchange_scenario_id(self):
        """Обновить поля при изменении сценария"""
        if self.scenario_id:
            self.name = f"{self.scenario_id.title} - Application"
            self.description = self.scenario_id.content_md[:500] if self.scenario_id.content_md else ''
            self.duration_hours = self.scenario_id.execution_time_hours or 2.0
            self.scenario_parameters = self.scenario_id.scenario_parameters
    
    @api.onchange('application_type')
    def _onchange_application_type(self):
        """Адаптировать интерфейс под тип применения"""
        if self.application_type == 'exercise':
            self.simulation_enabled = True
        elif self.application_type == 'assessment':
            self.ai_adaptation = True
    
    def action_next_step(self):
        """Перейти к следующему шагу мастера"""
        if self.state == 'configure':
            return self._step_customize()
        elif self.state == 'customize':
            return self._step_review()
        elif self.state == 'review':
            return self._step_apply()
        else:
            raise UserError(_('Invalid wizard state'))
    
    def action_previous_step(self):
        """Вернуться к предыдущему шагу"""
        if self.state == 'review':
            self.state = 'customize'
        elif self.state == 'customize':
            self.state = 'configure'
        
        return self._reload_wizard()
    
    def _step_customize(self):
        """Шаг кастомизации и AI адаптации"""
        self.state = 'customize'
        
        # Запустить AI адаптацию если включена
        if self.ai_adaptation and self.client_id:
            try:
                self._run_ai_adaptation()
            except Exception as e:
                _logger.warning(f"AI adaptation failed: {e}")
                self.adaptation_notes = f"AI adaptation failed: {str(e)}"
        
        return self._reload_wizard()
    
    def _step_review(self):
        """Шаг просмотра и подтверждения"""
        self.state = 'review'
        
        # Валидация параметров
        if self.parameter_values:
            try:
                json.loads(self.parameter_values)
            except json.JSONDecodeError:
                raise ValidationError(_('Invalid JSON in parameter values'))
        
        return self._reload_wizard()
    
    def _step_apply(self):
        """Применить сценарий к клиенту"""
        self.state = 'applying'
        
        try:
            if self.application_type == 'exercise':
                resource = self._create_exercise()
            elif self.application_type == 'plan':
                resource = self._create_plan()
            elif self.application_type == 'template':
                resource = self._create_template()
            elif self.application_type == 'assessment':
                resource = self._create_assessment()
            else:
                raise UserError(_('Unsupported application type'))
            
            self.created_resource_id = resource.id
            self.created_resource_model = resource._name
            self.state = 'done'
            
            # Увеличить счетчик применений сценария
            self.scenario_id.sudo().write({
                'downloads_count': self.scenario_id.downloads_count + 1
            })
            
            return self._show_success()
            
        except Exception as e:
            _logger.error(f"Scenario application failed: {e}")
            raise UserError(_('Application failed: %s') % str(e))
    
    def _run_ai_adaptation(self):
        """Запустить AI адаптацию сценария под клиента"""
        ai_service = self.env['bcm.ai.integration']
        
        # Подготовить контекст клиента
        client_context = {
            'client_id': self.client_id.id,
            'client_name': self.client_id.name,
            'sector': self.client_id.sector,
            'region': self.client_id.region,
            'company_size': getattr(self.client_id, 'company_size', 'unknown'),
            'current_bcm_maturity': getattr(self.client_id, 'bcm_maturity_level', 'unknown'),
        }
        
        # Получить контекст из vault
        vault_entries = self.env['bcm.client.vault'].search([
            ('client_id', '=', self.client_id.id),
            ('context_type', 'in', ['organization', 'processes', 'risks'])
        ], limit=10)
        
        vault_context = []
        for entry in vault_entries:
            vault_context.append({
                'type': entry.context_type,
                'content': entry.content_text[:500],  # Ограничить для AI
                'sensitivity': entry.sensitivity_level
            })
        
        # Запрос к AI Orchestrator для адаптации
        try:
            adaptation_result = ai_service.scenario_adapt_to_client(
                scenario_id=self.scenario_id.id,
                scenario_content=self.scenario_id.content_md,
                client_context=client_context,
                vault_context=vault_context,
                application_type=self.application_type
            )
            
            if adaptation_result.get('status') == 'success':
                adaptation = adaptation_result.get('adaptation', {})
                
                # Обновить параметры на основе адаптации
                if adaptation.get('suggested_parameters'):
                    self.parameter_values = json.dumps(
                        adaptation['suggested_parameters'], 
                        indent=2
                    )
                
                # Обновить длительность
                if adaptation.get('recommended_duration_hours'):
                    self.duration_hours = adaptation['recommended_duration_hours']
                
                # Сохранить заметки по адаптации
                notes = []
                if adaptation.get('client_specific_modifications'):
                    notes.append("Client-specific modifications:")
                    notes.extend([f"• {mod}" for mod in adaptation['client_specific_modifications']])
                
                if adaptation.get('risk_considerations'):
                    notes.append("\nRisk considerations:")
                    notes.extend([f"• {risk}" for risk in adaptation['risk_considerations']])
                
                if adaptation.get('resource_recommendations'):
                    notes.append("\nResource recommendations:")
                    notes.extend([f"• {rec}" for rec in adaptation['resource_recommendations']])
                
                self.adaptation_notes = '\n'.join(notes)
                
        except Exception as e:
            _logger.error(f"AI adaptation failed: {e}")
            self.adaptation_notes = f"AI adaptation encountered an error: {str(e)}"
    
    def _create_exercise(self):
        """Создать учение на основе сценария"""
        # Парсинг параметров
        parameters = {}
        if self.parameter_values:
            try:
                parameters = json.loads(self.parameter_values)
            except json.JSONDecodeError:
                parameters = {}
        
        # Создать учение
        exercise_vals = {
            'name': self.name,
            'notes': f"Exercise based on scenario: {self.scenario_id.title}\n\n{self.description or ''}",
            'company_id': self.client_id.company_id.id,
            # Дополнительные поля, если они есть в модели
        }
        
        # Добавить кастомные поля если они существуют
        if hasattr(self.env['bcm_exercise.record'], 'scheduled_date'):
            exercise_vals['scheduled_date'] = self.scheduled_date
        if hasattr(self.env['bcm_exercise.record'], 'duration_hours'):
            exercise_vals['duration_hours'] = self.duration_hours
        if hasattr(self.env['bcm_exercise.record'], 'scenario_id'):
            exercise_vals['scenario_id'] = self.scenario_id.id
        if hasattr(self.env['bcm_exercise.record'], 'participant_ids'):
            exercise_vals['participant_ids'] = [(6, 0, self.participant_ids.ids)]
        
        exercise = self.env['bcm_exercise.record'].create(exercise_vals)
        
        # Если включена симуляция, настроить sim_adapter
        if self.simulation_enabled:
            self._setup_simulation(exercise)
        
        return exercise
    
    def _create_plan(self):
        """Создать план непрерывности на основе сценария"""
        plan_vals = {
            'name': self.name,
            'notes': f"Plan based on scenario: {self.scenario_id.title}\n\n{self.scenario_id.content_md}\n\n{self.description or ''}",
            'company_id': self.client_id.company_id.id,
        }
        
        return self.env['bcm_plans.record'].create(plan_vals)
    
    def _create_template(self):
        """Создать шаблон на основе сценария"""
        template_vals = {
            'name': self.name,
            'notes': f"Template based on scenario: {self.scenario_id.title}\n\n{self.scenario_id.content_md}\n\n{self.description or ''}",
            'company_id': self.client_id.company_id.id,
        }
        
        return self.env['bcm_templates.record'].create(template_vals)
    
    def _create_assessment(self):
        """Создать оценку рисков на основе сценария"""
        # Использовать существующую модель или создать новую запись
        assessment_vals = {
            'name': self.name,
            'notes': f"Risk assessment based on scenario: {self.scenario_id.title}\n\n{self.description or ''}",
            'company_id': self.client_id.company_id.id,
        }
        
        # Попробовать создать в подходящей модели
        try:
            return self.env['bcm_audit.record'].create(assessment_vals)
        except:
            # Fallback к общей модели
            return self.env['bcm_context.record'].create(assessment_vals)
    
    def _setup_simulation(self, exercise):
        """Настроить симуляцию для учения"""
        if not self.simulation_config:
            # Создать базовую конфигурацию симуляции
            sim_config = {
                'scenario_type': self.scenario_id.scenario_type,
                'simulation_duration': self.duration_hours,
                'participants': len(self.participant_ids),
                'complexity': self.scenario_id.difficulty_level,
                'client_context': {
                    'sector': self.client_id.sector,
                    'size': getattr(self.client_id, 'company_size', 'medium')
                }
            }
            self.simulation_config = json.dumps(sim_config, indent=2)
        
        # Здесь будет интеграция с sim_adapter
        _logger.info(f"Setting up simulation for exercise {exercise.id} with config: {self.simulation_config}")
    
    def _reload_wizard(self):
        """Перезагрузить мастер с текущим состоянием"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Apply Scenario to Client'),
            'res_model': 'bcm.scenario.apply.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self._context
        }
    
    def _show_success(self):
        """Показать результат успешного применения"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Scenario Applied Successfully'),
            'res_model': self.created_resource_model,
            'res_id': self.created_resource_id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_open_created_resource(self):
        """Открыть созданный ресурс"""
        if not self.created_resource_id or not self.created_resource_model:
            raise UserError(_('No resource was created'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Created Resource'),
            'res_model': self.created_resource_model,
            'res_id': self.created_resource_id,
            'view_mode': 'form',
            'target': 'current',
        }
