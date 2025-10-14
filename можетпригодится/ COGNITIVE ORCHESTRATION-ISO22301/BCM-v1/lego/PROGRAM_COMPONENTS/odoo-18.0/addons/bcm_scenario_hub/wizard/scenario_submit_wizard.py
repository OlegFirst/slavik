# -*- coding: utf-8 -*-

import logging
import json
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class ScenarioSubmitWizard(models.TransientModel):
    """Мастер отправки сценария на модерацию"""
    _name = 'bcm.scenario.submit.wizard'
    _description = 'Scenario Submission Wizard'
    
    scenario_id = fields.Many2one(
        'bcm.scenario', 
        string='Scenario',
        required=True,
        readonly=True
    )
    
    # Информация о сценарии для просмотра
    scenario_name = fields.Char(related='scenario_id.title', readonly=True)
    scenario_content = fields.Text(related='scenario_id.content_md', readonly=True)
    
    # Метаданные отправки
    submission_notes = fields.Text(
        string='Submission Notes',
        help='Additional notes for reviewers'
    )
    
    # Чек-лист готовности
    content_complete = fields.Boolean(
        string='Content is Complete',
        help='Scenario content is fully written and ready for review'
    )
    
    metadata_complete = fields.Boolean(
        string='Metadata is Complete',
        help='All required metadata fields are filled'
    )
    
    iso_compliant = fields.Boolean(
        string='ISO 22301 Compliant',
        help='Scenario follows ISO 22301 standards'
    )
    
    tested_scenario = fields.Boolean(
        string='Scenario Tested',
        help='Scenario has been tested or validated'
    )
    
    # AI валидация
    ai_validation_enabled = fields.Boolean(
        string='Run AI Validation',
        default=True,
        help='Use AI to validate scenario before submission'
    )
    
    ai_validation_results = fields.Text(
        string='AI Validation Results',
        readonly=True
    )
    
    validation_score = fields.Float(
        string='Validation Score',
        readonly=True
    )
    
    # Состояние мастера
    state = fields.Selection([
        ('prepare', 'Prepare Submission'),
        ('validate', 'AI Validation'),
        ('review', 'Review & Submit'),
        ('submitting', 'Submitting...'),
        ('done', 'Submitted')
    ], string='State', default='prepare')
    
    @api.model
    def default_get(self, fields_list):
        """Получить значения по умолчанию"""
        defaults = super().default_get(fields_list)
        
        scenario_id = self._context.get('active_id')
        if scenario_id:
            scenario = self.env['bcm.scenario'].browse(scenario_id)
            defaults['scenario_id'] = scenario_id
            
            # Автоматически проверить готовность метаданных
            defaults['metadata_complete'] = bool(
                scenario.domains and
                scenario.tags and
                scenario.difficulty_level and
                scenario.scenario_type
            )
            
            # Проверить полноту контента
            defaults['content_complete'] = bool(
                scenario.content and
                len(scenario.content.strip()) > 100 and
                scenario.description and
                len(scenario.description.strip()) > 50
            )
        
        return defaults
    
    def action_next_step(self):
        """Перейти к следующему шагу"""
        if self.state == 'prepare':
            if self.ai_validation_enabled:
                return self._step_validate()
            else:
                return self._step_review()
        elif self.state == 'validate':
            return self._step_review()
        elif self.state == 'review':
            return self._step_submit()
        else:
            raise UserError(_('Invalid wizard state'))
    
    def action_previous_step(self):
        """Вернуться к предыдущему шагу"""
        if self.state == 'review':
            if self.ai_validation_enabled:
                self.state = 'validate'
            else:
                self.state = 'prepare'
        elif self.state == 'validate':
            self.state = 'prepare'
        
        return self._reload_wizard()
    
    def _step_validate(self):
        """Шаг AI валидации"""
        self.state = 'validate'
        
        # Запустить AI валидацию
        if self.ai_validation_enabled:
            try:
                self._run_ai_validation()
            except Exception as e:
                _logger.warning(f"AI validation failed: {e}")
                self.ai_validation_results = f"AI validation failed: {str(e)}"
                self.validation_score = 0.0
        
        return self._reload_wizard()
    
    def _step_review(self):
        """Шаг просмотра перед отправкой"""
        self.state = 'review'
        
        # Финальные проверки
        if not self._check_readiness():
            raise UserError(_('Scenario is not ready for submission. Please complete all requirements.'))
        
        return self._reload_wizard()
    
    def _step_submit(self):
        """Отправить сценарий на модерацию"""
        self.state = 'submitting'
        
        try:
            # Обновить статус сценария
            self.scenario_id.write({
                'status': 'pending_review',
                'submission_notes': self.submission_notes,
                'validation_score': self.validation_score if self.ai_validation_enabled else 0.0,
            })
            
            # Создать уведомление для модераторов
            self._notify_moderators()
            
            # Создать активность для отслеживания
            self._create_review_activity()
            
            self.state = 'done'
            
            return self._show_success()
            
        except Exception as e:
            _logger.error(f"Scenario submission failed: {e}")
            raise UserError(_('Submission failed: %s') % str(e))
    
    def _run_ai_validation(self):
        """Запустить AI валидацию сценария"""
        ai_service = self.env['bcm.ai.integration']
        
        # Подготовить данные сценария для валидации
        scenario_data = {
            'name': self.scenario_id.title,
            'description': self.scenario_id.content_md[:500] if self.scenario_id.content_md else '',
            'content': self.scenario_id.content_md,
            'scenario_type': self.scenario_id.scenario_type,
            'difficulty_level': self.scenario_id.difficulty_level,
            'domains': [d.name for d in self.scenario_id.domains],
            'tags': [t.name for t in self.scenario_id.tags],
            'iso22301_compliance': self.scenario_id.iso22301_compliance,
            'execution_time_hours': self.scenario_id.execution_time_hours,
        }
        
        try:
            # Вызов к AI Orchestrator для валидации
            validation_result = ai_service.scenario_validate_content(
                scenario_data=scenario_data,
                validation_criteria={
                    'check_iso22301_compliance': True,
                    'check_content_completeness': True,
                    'check_technical_accuracy': True,
                    'check_practical_applicability': True,
                    'check_security_considerations': True
                }
            )
            
            if validation_result.get('status') == 'success':
                validation = validation_result.get('validation', {})
                
                # Сохранить общую оценку
                self.validation_score = validation.get('overall_score', 0.0)
                
                # Формировать отчет о валидации
                report_lines = []
                
                # Общая оценка
                score = validation.get('overall_score', 0) * 100
                report_lines.append(f"Overall Score: {score:.1f}%")
                report_lines.append("")
                
                # Детальные критерии
                criteria = validation.get('criteria_scores', {})
                for criterion, details in criteria.items():
                    score = details.get('score', 0) * 100
                    status = "PASS" if score >= 70 else "WARN" if score >= 50 else "FAIL"
                    criterion_name = criterion.replace('_', ' ').title()
                    report_lines.append(f"[{status}] {criterion_name}: {score:.1f}%")
                    
                    if details.get('feedback'):
                        for feedback in details['feedback'][:2]:  # Ограничить feedback
                            report_lines.append(f"   • {feedback}")
                
                # Рекомендации по улучшению
                if validation.get('improvement_suggestions'):
                    report_lines.append("")
                    report_lines.append("Improvement Suggestions:")
                    for suggestion in validation['improvement_suggestions'][:5]:
                        report_lines.append(f"• {suggestion}")
                
                # Проблемы и предупреждения
                if validation.get('issues'):
                    report_lines.append("")
                    report_lines.append("Issues to Address:")
                    for issue in validation['issues'][:5]:
                        report_lines.append(f"• {issue}")
                
                self.ai_validation_results = '\n'.join(report_lines)
                
        except Exception as e:
            _logger.error(f"AI validation failed: {e}")
            self.ai_validation_results = f"AI validation encountered an error: {str(e)}\n\nPlease proceed with manual review."
            self.validation_score = 0.0
    
    def _check_readiness(self):
        """Проверить готовность сценария к отправке"""
        required_checks = [
            self.content_complete,
            self.metadata_complete,
        ]
        
        # Если AI валидация включена, учесть её результат
        if self.ai_validation_enabled:
            required_checks.append(self.validation_score >= 0.6)  # Минимум 60%
        
        return all(required_checks)
    
    def _notify_moderators(self):
        """Уведомить модераторов о новом сценарии"""
        moderator_group = self.env.ref('bcm_scenario_hub.group_scenario_reviewer')
        moderators = moderator_group.users
        
        if moderators:
            # Создать уведомление
            self.scenario_id.message_post(
                body=_("""
                    <p><strong>New scenario submitted for review</strong></p>
                    <p>Scenario: <strong>%s</strong></p>
                    <p>Author: %s</p>
                    <p>Submission notes: %s</p>
                    %s
                """) % (
                    self.scenario_id.title,
                    self.scenario_id.author_user_id.name,
                    self.submission_notes or 'None',
                    f"<p>AI Validation Score: {self.validation_score * 100:.1f}%</p>" if self.ai_validation_enabled else ""
                ),
                subject=f"New Scenario for Review: {self.scenario_id.title}",
                partner_ids=moderators.mapped('partner_id').ids,
                message_type='notification'
            )
    
    def _create_review_activity(self):
        """Создать активность для отслеживания процесса ревью"""
        activity_type = self.env.ref('bcm_scenario_hub.mail_activity_scenario_review', raise_if_not_found=False)
        
        if activity_type:
            self.env['mail.activity'].create({
                'activity_type_id': activity_type.id,
                'summary': f'Review scenario: {self.scenario_id.title}',
                'note': self.submission_notes or 'No additional notes provided.',
                'res_id': self.scenario_id.id,
                'res_model_id': self.env['ir.model']._get('bcm.scenario').id,
                'user_id': self.env.ref('bcm_scenario_hub.group_scenario_reviewer').users[:1].id if self.env.ref('bcm_scenario_hub.group_scenario_reviewer').users else self.env.uid,
            })
    
    def _reload_wizard(self):
        """Перезагрузить мастер"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Submit Scenario for Review'),
            'res_model': 'bcm.scenario.submit.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self._context
        }
    
    def _show_success(self):
        """Показать сообщение об успешной отправке"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Scenario Submitted Successfully'),
                'message': _('Your scenario "%s" has been submitted for review. Moderators will review it shortly.') % self.scenario_id.title,
                'type': 'success',
                'sticky': True,
            }
        }
    
    def action_force_submit(self):
        """Принудительно отправить без полных проверок (для экстренных случаев)"""
        if not self.env.user.has_group('bcm_scenario_hub.group_scenario_admin'):
            raise UserError(_('Only administrators can force submit scenarios.'))
        
        return self._step_submit()
