# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import json
import logging

_logger = logging.getLogger(__name__)


class BCMIncidentUnified(models.Model):
    """
    Unified Incident Management Model
    Объединяет функциональность bcm_incident + bcm_incident_management
    """
    _name = 'bcm.incident'
    _description = 'Business Continuity Incident'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, create_date desc'
    _rec_name = 'title'

    # ========================================
    # ОСНОВНЫЕ ПОЛЯ (из bcm_incident)
    # ========================================
    
    title = fields.Char(
        string='Incident Title',
        required=True,
        tracking=True,
        help="Brief description of the incident"
    )
    
    description = fields.Text(
        string='Description',
        required=True,
        tracking=True,
        help="Detailed description of what happened"
    )
    
    incident_number = fields.Char(
        string='Incident Number',
        required=True,
        copy=False,
        readonly=True,
        default='New',
        help="Unique incident identifier"
    )
    
    # Базовая классификация
    severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'), 
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Severity', required=True, default='medium', tracking=True)
    
    status = fields.Selection([
        ('draft', 'Draft'),
        ('detected', 'Detected'),
        ('assessing', 'Assessing'),
        ('responding', 'Responding'),
        ('recovering', 'Recovering'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ], string='Status', required=True, default='draft', tracking=True)
    
    incident_type = fields.Selection([
        ('operational', 'Operational Disruption'),
        ('cyber', 'Cyber Security'),
        ('natural', 'Natural Disaster'),
        ('supply_chain', 'Supply Chain'),
        ('health_safety', 'Health & Safety'),
        ('financial', 'Financial Impact'),
        ('reputational', 'Reputational Risk'),
        ('other', 'Other')
    ], string='Incident Type', required=True, tracking=True)
    
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High'),
        ('4', 'Critical')
    ], string='Priority', default='0', tracking=True)
    
    # Временные метрики
    detected_at = fields.Datetime(
        string='Detection Time',
        default=fields.Datetime.now,
        required=True,
        tracking=True
    )
    
    reported_at = fields.Datetime(
        string='Reported Time',
        default=fields.Datetime.now,
        tracking=True
    )
    
    resolved_at = fields.Datetime(
        string='Resolution Time',
        tracking=True
    )
    
    # RTO/RPO метрики
    target_rto = fields.Float(
        string='Target RTO (hours)',
        help="Recovery Time Objective in hours"
    )
    
    actual_rto = fields.Float(
        string='Actual RTO (hours)',
        compute='_compute_actual_rto',
        store=True,
        help="Actual recovery time achieved"
    )
    
    target_rpo = fields.Float(
        string='Target RPO (hours)',
        help="Recovery Point Objective in hours"
    )
    
    # Участники
    reported_by = fields.Many2one(
        'res.users',
        string='Reported By',
        default=lambda self: self.env.user,
        required=True,
        tracking=True
    )
    
    assigned_to = fields.Many2one(
        'res.users',
        string='Assigned To',
        tracking=True,
        help="Primary responsible person"
    )
    
    stakeholders = fields.Many2many(
        'res.users',
        string='Stakeholders',
        help="People who need to be notified"
    )
    
    # Воздействие
    affected_systems = fields.Text(
        string='Affected Systems',
        help="List of affected systems and services"
    )
    
    affected_locations = fields.Text(
        string='Affected Locations',
        help="Geographical locations impacted"
    )
    
    estimated_impact = fields.Selection([
        ('minimal', 'Minimal'),
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('major', 'Major'),
        ('severe', 'Severe')
    ], string='Estimated Impact', tracking=True)
    
    financial_impact = fields.Monetary(
        string='Estimated Financial Impact',
        currency_field='currency_id',
        tracking=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )
    
    # ========================================
    # РАСШИРЕННЫЕ ПОЛЯ (из bcm_incident_management)
    # ========================================
    
    # AI Commander функции
    ai_classification_confidence = fields.Float(
        string='AI Classification Confidence',
        help="AI confidence in automatic classification (0-100%)"
    )
    
    ai_recommendations = fields.Text(
        string='AI Recommendations',
        help="AI-generated recommendations for incident response"
    )
    
    ai_similar_incidents = fields.Many2many(
        'bcm.incident',
        'incident_similar_rel',
        'incident_id',
        'similar_id',
        string='Similar Incidents',
        help="AI-identified similar historical incidents"
    )
    
    ai_risk_score = fields.Float(
        string='AI Risk Score',
        help="AI-calculated risk score (0-100)"
    )
    
    ai_escalation_prediction = fields.Boolean(
        string='AI Predicts Escalation',
        help="AI prediction whether incident will escalate"
    )
    
    # Crisis Level (расширенная классификация)
    crisis_level = fields.Selection([
        ('0', 'No Crisis - Normal Operation'),
        ('1', 'Minor Disruption'),
        ('2', 'Significant Disruption'),
        ('3', 'Major Crisis'),
        ('4', 'Severe Crisis'),
        ('5', 'Catastrophic Event')
    ], string='Crisis Level', default='0', tracking=True)

    # ===== DIGITAL TWIN INTEGRATION =====
    # Fields required for Digital Twin simulations and analysis

    digital_twin_simulation_ids = fields.One2many(
        'bcm.digital.twin.simulation',
        'related_incident',
        string='Digital Twin Simulations',
        help='Crisis simulations based on this incident'
    )

    simulation_count = fields.Integer(
        string='Simulation Count',
        compute='_compute_simulation_count',
        help='Number of digital twin simulations for this incident'
    )

    # Compatibility fields for Digital Twin data extraction
    affected_areas = fields.Text(
        string='Affected Areas',
        compute='_compute_affected_areas',
        help='Combined affected systems and locations for Digital Twin'
    )

    recovery_actions = fields.Text(
        string='Recovery Actions',
        help='Actions taken for recovery - used by Digital Twin simulations'
    )

    response_time = fields.Float(
        string='Response Time (hours)',
        compute='_compute_response_time',
        help='Actual response time for Digital Twin analysis'
    )
    
    business_impact_level = fields.Selection([
        ('none', 'No Business Impact'),
        ('low', 'Low Impact'),
        ('medium', 'Medium Impact'),
        ('high', 'High Impact'),
        ('critical', 'Critical Impact')
    ], string='Business Impact Level', tracking=True)
    
    # Команды реагирования
    response_team_activated = fields.Boolean(
        string='Response Team Activated',
        default=False,
        tracking=True
    )
    
    response_team_members = fields.Many2many(
        'hr.employee',
        string='Response Team Members',
        help="Team members assigned to this incident"
    )
    
    incident_commander = fields.Many2one(
        'hr.employee',
        string='Incident Commander',
        tracking=True,
        help="Person leading the incident response"
    )
    
    # Эскалация
    escalation_level = fields.Integer(
        string='Escalation Level',
        default=0,
        tracking=True,
        help="Current escalation level (0 = no escalation)"
    )
    
    escalation_history = fields.Text(
        string='Escalation History',
        help="History of escalation actions"
    )
    
    auto_escalate = fields.Boolean(
        string='Auto Escalate',
        default=True,
        help="Whether to automatically escalate based on rules"
    )
    
    escalation_deadline = fields.Datetime(
        string='Escalation Deadline',
        compute='_compute_escalation_deadline',
        store=True,
        help="Deadline for next escalation"
    )
    
    # Мобильные функции
    mobile_reporting_enabled = fields.Boolean(
        string='Mobile Reporting Enabled',
        default=True
    )
    
    gps_tracking_enabled = fields.Boolean(
        string='GPS Tracking Enabled',
        default=False,
        help="Enable GPS tracking for response team"
    )
    
    field_updates = fields.One2many(
        'bcm.incident.field.update',
        'incident_id',
        string='Field Updates',
        help="Updates from field personnel"
    )
    
    # Коммуникации
    crisis_communication_plan = fields.Many2one(
        'bcm.crisis.communication.plan',
        string='Communication Plan',
        help="Activated crisis communication plan"
    )
    
    stakeholder_notifications = fields.One2many(
        'bcm.stakeholder.notification',
        'incident_id',
        string='Stakeholder Notifications'
    )
    
    media_attention = fields.Boolean(
        string='Media Attention',
        default=False,
        tracking=True,
        help="Whether incident has attracted media attention"
    )
    
    public_statement_required = fields.Boolean(
        string='Public Statement Required',
        default=False,
        tracking=True
    )
    
    # Интеграции
    external_ticket_number = fields.Char(
        string='External Ticket Number',
        help="Reference number in external system (ITSM, etc.)"
    )
    
    thehive_case_id = fields.Char(
        string='TheHive Case ID',
        help="Case ID in TheHive platform for security incidents"
    )
    
    integration_data = fields.Text(
        string='Integration Data',
        help="JSON data for external system integrations"
    )
    
    # Метрики и аналитика
    lessons_learned = fields.Text(
        string='Lessons Learned',
        help="Key lessons from incident resolution"
    )
    
    root_cause_analysis = fields.Text(
        string='Root Cause Analysis',
        help="Analysis of underlying causes"
    )
    
    preventive_measures = fields.Text(
        string='Preventive Measures',
        help="Measures to prevent similar incidents"
    )
    
    post_incident_review_required = fields.Boolean(
        string='Post-Incident Review Required',
        default=True
    )
    
    post_incident_review_completed = fields.Boolean(
        string='PIR Completed',
        default=False,
        tracking=True
    )
    
    # Связанные записи
    related_risks = fields.Many2many(
        'bcm.risk',
        string='Related Risks',
        help="Risks related to this incident"
    )
    
    related_bia_functions = fields.Many2many(
        'bcm.critical.function',
        string='Affected Critical Functions',
        help="Critical business functions affected"
    )
    
    triggered_plans = fields.Many2many(
        'bcm.plan',
        string='Triggered Plans',
        help="BCM plans activated for this incident"
    )
    
    # Статусные поля
    active = fields.Boolean(default=True)
    
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        required=True
    )
    
    # ========================================
    # COMPUTED FIELDS
    # ========================================
    
    @api.depends('detected_at', 'resolved_at')
    def _compute_actual_rto(self):
        """Вычисление фактического RTO"""
        for incident in self:
            if incident.detected_at and incident.resolved_at:
                delta = incident.resolved_at - incident.detected_at
                incident.actual_rto = delta.total_seconds() / 3600
            else:
                incident.actual_rto = 0.0
    
    @api.depends('detected_at', 'incident_type', 'severity')
    def _compute_escalation_deadline(self):
        """Вычисление deadline для эскалации"""
        for incident in self:
            if not incident.detected_at:
                incident.escalation_deadline = False
                continue
                
            # Правила эскалации по типу и серьезности
            escalation_rules = {
                ('critical', 'cyber'): 30,       # 30 минут
                ('critical', 'health_safety'): 15,  # 15 минут
                ('high', 'cyber'): 60,           # 1 час
                ('high', 'operational'): 120,    # 2 часа
                ('medium', 'any'): 240,          # 4 часа
                ('low', 'any'): 480,             # 8 часов
            }
            
            # Находим подходящее правило
            minutes = 240  # default
            for (sev, type_), mins in escalation_rules.items():
                if incident.severity == sev and (type_ == 'any' or incident.incident_type == type_):
                    minutes = mins
                    break
            
            incident.escalation_deadline = incident.detected_at + timedelta(minutes=minutes)
    
    # ========================================
    # CONSTRAINTS & VALIDATION
    # ========================================
    
    @api.constrains('target_rto', 'target_rpo')
    def _check_rto_rpo_values(self):
        """Проверка корректности RTO/RPO значений"""
        for incident in self:
            if incident.target_rto and incident.target_rto < 0:
                raise ValidationError(_("Target RTO cannot be negative"))
            if incident.target_rpo and incident.target_rpo < 0:
                raise ValidationError(_("Target RPO cannot be negative"))
            if incident.target_rto and incident.target_rpo and incident.target_rpo > incident.target_rto:
                raise ValidationError(_("Target RPO cannot be greater than Target RTO"))
    
    @api.constrains('detected_at', 'reported_at', 'resolved_at')
    def _check_datetime_sequence(self):
        """Проверка логической последовательности дат"""
        for incident in self:
            if incident.reported_at and incident.detected_at and incident.reported_at < incident.detected_at:
                raise ValidationError(_("Reported time cannot be before detection time"))
            if incident.resolved_at and incident.detected_at and incident.resolved_at < incident.detected_at:
                raise ValidationError(_("Resolution time cannot be before detection time"))
    
    # ========================================
    # LIFECYCLE METHODS
    # ========================================
    
    @api.model
    def create(self, vals):
        """Создание инцидента с автоматической нумерацией и AI анализом"""
        if vals.get('incident_number', 'New') == 'New':
            vals['incident_number'] = self.env['ir.sequence'].next_by_code('bcm.incident') or 'New'
        
        incident = super().create(vals)
        
        # Запускаем AI анализ
        incident._trigger_ai_analysis()
        
        # Автоматические уведомления
        incident._send_creation_notifications()
        
        return incident
    
    def write(self, vals):
        """Обновление с отслеживанием изменений и триггерами"""
        old_status = {incident.id: incident.status for incident in self}
        old_severity = {incident.id: incident.severity for incident in self}
        
        result = super().write(vals)
        
        # Проверяем изменения статуса
        if 'status' in vals:
            for incident in self:
                if old_status[incident.id] != incident.status:
                    incident._on_status_change(old_status[incident.id])
        
        # Проверяем изменения серьезности
        if 'severity' in vals:
            for incident in self:
                if old_severity[incident.id] != incident.severity:
                    incident._on_severity_change(old_severity[incident.id])
        
        return result
    
    # ========================================
    # ACTION METHODS
    # ========================================
    
    def action_start_response(self):
        """Начать реагирование на инцидент"""
        self.ensure_one()
        if self.status not in ['detected', 'assessing']:
            raise UserError(_("Cannot start response for incident in status '%s'") % self.status)
        
        self.write({
            'status': 'responding',
            'response_team_activated': True
        })
        
        # Активируем команду реагирования
        self._activate_response_team()
        
        # Запускаем AI рекомендации
        self._generate_ai_response_plan()
        
        return True
    
    def action_escalate(self):
        """Эскалация инцидента"""
        self.ensure_one()
        
        new_level = self.escalation_level + 1
        escalation_msg = f"Incident escalated to level {new_level} at {fields.Datetime.now()}"
        
        if self.escalation_history:
            escalation_history = f"{self.escalation_history}\n{escalation_msg}"
        else:
            escalation_history = escalation_msg
        
        self.write({
            'escalation_level': new_level,
            'escalation_history': escalation_history,
        })
        
        # Уведомляем заинтересованных лиц
        self._send_escalation_notifications()
        
        # Логируем в timeline
        self.message_post(
            body=escalation_msg,
            message_type='notification',
            subtype_xmlid='bcm_incident_unified.mt_incident_escalated'
        )
        
        return True
    
    def action_resolve(self):
        """Разрешение инцидента"""
        self.ensure_one()
        if self.status == 'resolved':
            raise UserError(_("Incident is already resolved"))
        
        self.write({
            'status': 'resolved',
            'resolved_at': fields.Datetime.now()
        })
        
        # Уведомления о разрешении
        self._send_resolution_notifications()
        
        # Планируем post-incident review
        if self.post_incident_review_required:
            self._schedule_post_incident_review()
        
        return True
    
    def action_close(self):
        """Закрытие инцидента"""
        self.ensure_one()
        if self.status != 'resolved':
            raise UserError(_("Cannot close incident that is not resolved"))
        
        if self.post_incident_review_required and not self.post_incident_review_completed:
            raise UserError(_("Cannot close incident without completing post-incident review"))
        
        self.write({'status': 'closed'})
        
        return True
    
    def action_reopen(self):
        """Переоткрытие инцидента"""
        self.ensure_one()
        if self.status not in ['resolved', 'closed']:
            raise UserError(_("Can only reopen resolved or closed incidents"))
        
        self.write({
            'status': 'responding',
            'resolved_at': False
        })
        
        return True
    
    # ========================================
    # AI METHODS
    # ========================================
    
    def _trigger_ai_analysis(self):
        """Запуск AI анализа инцидента"""
        self.ensure_one()
        
        # Автоматическая классификация
        ai_classification = self._ai_classify_incident()
        if ai_classification:
            self.write(ai_classification)
        
        # Поиск похожих инцидентов
        similar_incidents = self._ai_find_similar_incidents()
        if similar_incidents:
            self.ai_similar_incidents = [(6, 0, similar_incidents)]
        
        # Генерация рекомендаций
        recommendations = self._ai_generate_recommendations()
        if recommendations:
            self.ai_recommendations = recommendations
        
        # Расчет risk score
        risk_score = self._ai_calculate_risk_score()
        if risk_score:
            self.ai_risk_score = risk_score
    
    def _ai_classify_incident(self):
        """AI классификация инцидента"""
        # Placeholder для AI классификации
        # В реальной реализации здесь будет интеграция с AI сервисом
        
        keywords_map = {
            'cyber': ['hack', 'breach', 'malware', 'ransomware', 'phishing', 'ddos'],
            'operational': ['outage', 'failure', 'down', 'unavailable', 'performance'],
            'natural': ['earthquake', 'flood', 'fire', 'storm', 'hurricane'],
            'supply_chain': ['supplier', 'delivery', 'logistics', 'procurement'],
            'health_safety': ['injury', 'accident', 'safety', 'emergency', 'medical']
        }
        
        description_lower = (self.description or '').lower()
        title_lower = (self.title or '').lower()
        text = f"{title_lower} {description_lower}"
        
        best_match = None
        max_matches = 0
        
        for incident_type, keywords in keywords_map.items():
            matches = sum(1 for keyword in keywords if keyword in text)
            if matches > max_matches:
                max_matches = matches
                best_match = incident_type
        
        if best_match and max_matches > 0:
            confidence = min(90, max_matches * 30)  # Simple confidence calculation
            return {
                'incident_type': best_match,
                'ai_classification_confidence': confidence
            }
        
        return {}
    
    def _ai_find_similar_incidents(self):
        """Поиск похожих инцидентов через AI"""
        # Простой поиск по ключевым словам
        # В реальной реализации - векторный поиск или ML
        
        if not self.description:
            return []
        
        keywords = self.description.lower().split()[:10]  # Первые 10 слов
        
        domain = [
            ('id', '!=', self.id),
            ('status', 'in', ['resolved', 'closed']),
        ]
        
        # Поиск по ключевым словам в описании
        for keyword in keywords:
            if len(keyword) > 3:  # Игнорируем короткие слова
                domain.append(('description', 'ilike', keyword))
        
        similar = self.search(domain, limit=5)
        return similar.ids
    
    def _ai_generate_recommendations(self):
        """Генерация AI рекомендаций"""
        recommendations = []
        
        # Базовые рекомендации по типу инцидента
        type_recommendations = {
            'cyber': [
                "Isolate affected systems immediately",
                "Preserve evidence and logs", 
                "Notify security team and law enforcement if needed",
                "Reset credentials for affected accounts",
                "Run full security scan"
            ],
            'operational': [
                "Check system monitoring and logs",
                "Verify backup systems availability",
                "Assess resource requirements for recovery",
                "Communicate with affected users",
                "Document all actions taken"
            ],
            'natural': [
                "Ensure personnel safety first",
                "Activate emergency procedures",
                "Contact emergency services if needed",
                "Assess facility damage",
                "Implement alternate work arrangements"
            ]
        }
        
        if self.incident_type in type_recommendations:
            recommendations.extend(type_recommendations[self.incident_type])
        
        # Рекомендации по серьезности
        if self.severity == 'critical':
            recommendations.extend([
                "Activate Crisis Management Team",
                "Prepare executive briefing",
                "Consider media response strategy"
            ])
        
        return "\\n".join(f"• {rec}" for rec in recommendations)
    
    def _ai_calculate_risk_score(self):
        """Расчет AI risk score"""
        score = 0
        
        # Базовый score по серьезности
        severity_scores = {'low': 10, 'medium': 30, 'high': 60, 'critical': 90}
        score += severity_scores.get(self.severity, 30)
        
        # Модификаторы по типу
        type_modifiers = {
            'cyber': 1.5,
            'health_safety': 1.4,
            'natural': 1.3,
            'operational': 1.0,
            'supply_chain': 0.8
        }
        score *= type_modifiers.get(self.incident_type, 1.0)
        
        # Модификатор по времени
        if self.detected_at:
            hours_since = (fields.Datetime.now() - self.detected_at).total_seconds() / 3600
            if hours_since > 24:
                score *= 1.2  # Увеличиваем риск для старых инцидентов
        
        return min(100, score)
    
    # ========================================
    # NOTIFICATION METHODS  
    # ========================================
    
    def _send_creation_notifications(self):
        """Отправка уведомлений о создании инцидента"""
        self.ensure_one()
        
        # Уведомляем assigned_to
        if self.assigned_to:
            self.activity_schedule(
                'bcm_incident_unified.mail_activity_incident_assigned',
                user_id=self.assigned_to.id,
                summary=f"New incident assigned: {self.title}"
            )
        
        # Уведомляем stakeholders
        for stakeholder in self.stakeholders:
            self.message_notify(
                partner_ids=[stakeholder.partner_id.id],
                subject=f"New Incident: {self.incident_number}",
                body=f"Incident '{self.title}' has been created and requires attention."
            )
    
    def _send_escalation_notifications(self):
        """Уведомления об эскалации"""
        # Implementation for escalation notifications
        pass
    
    def _send_resolution_notifications(self):
        """Уведомления о разрешении"""
        # Implementation for resolution notifications
        pass
    
    # ========================================
    # AUTOMATION METHODS
    # ========================================
    
    def _on_status_change(self, old_status):
        """Обработка изменения статуса"""
        self.ensure_one()
        
        # Логируем изменение
        self.message_post(
            body=f"Status changed from {old_status} to {self.status}",
            message_type='notification'
        )
        
        # Специфичные действия по статусу
        if self.status == 'responding':
            self._on_response_started()
        elif self.status == 'resolved':
            self._on_incident_resolved()
    
    def _on_severity_change(self, old_severity):
        """Обработка изменения серьезности"""
        self.ensure_one()
        
        # Автоэскалация при повышении серьезности
        if self.severity == 'critical' and old_severity != 'critical':
            self.action_escalate()
    
    def _on_response_started(self):
        """Действия при начале реагирования"""
        # Генерируем AI план реагирования
        self._generate_ai_response_plan()
        
        # Активируем команду
        self._activate_response_team()
    
    def _on_incident_resolved(self):
        """Действия при разрешении инцидента"""
        # Обновляем метрики
        self._update_resolution_metrics()
        
        # Деактивируем команду
        self._deactivate_response_team()
    
    # ========================================
    # CRON METHODS
    # ========================================
    
    @api.model
    def process_ai_recommendations(self):
        """Cron job: Обработка AI рекомендаций"""
        active_incidents = self.search([
            ('status', 'in', ['detected', 'assessing', 'responding']),
            ('ai_recommendations', '=', False)
        ])
        
        for incident in active_incidents:
            try:
                incident._trigger_ai_analysis()
            except Exception as e:
                _logger.error(f"Failed to process AI recommendations for incident {incident.id}: {e}")
    
    @api.model
    def check_escalation_rules(self):
        """Cron job: Проверка правил эскалации"""
        now = fields.Datetime.now()
        
        overdue_incidents = self.search([
            ('status', 'in', ['detected', 'assessing', 'responding']),
            ('auto_escalate', '=', True),
            ('escalation_deadline', '<=', now)
        ])
        
        for incident in overdue_incidents:
            try:
                incident.action_escalate()
            except Exception as e:
                _logger.error(f"Failed to escalate incident {incident.id}: {e}")
    
    @api.model
    def generate_daily_reports(self):
        """Cron job: Генерация ежедневных отчетов"""
        # Implementation for daily reporting
        pass
    
    # ========================================
    # HELPER METHODS
    # ========================================
    
    def _activate_response_team(self):
        """Активация команды реагирования"""
        # Implementation for response team activation
        pass
    
    def _deactivate_response_team(self):
        """Деактивация команды реагирования"""
        # Implementation for response team deactivation  
        pass
    
    def _generate_ai_response_plan(self):
        """Генерация AI плана реагирования"""
        # Implementation for AI response plan generation
        pass
    
    def _update_resolution_metrics(self):
        """Обновление метрик разрешения"""
        # Implementation for metrics update
        pass
    
    def _schedule_post_incident_review(self):
        """Планирование post-incident review"""
        # Schedule PIR meeting/activity
        pass

    # ========================================
    # BACKWARD COMPATIBILITY WRAPPERS
    # ========================================

    def action_ai_emergency_response(self):
        """
        Backward compatibility wrapper for original action_ai_emergency_response
        Maps to new action_start_response with AI emergency mode
        """
        self.ensure_one()

        # Set emergency priority and activate AI
        self.write({
            'priority': '4',  # Critical
            'severity': 'critical',
            'status': 'responding',
            'response_team_activated': True
        })

        # Trigger AI analysis in emergency mode
        self._trigger_ai_analysis()

        # Generate emergency response plan
        self._generate_ai_emergency_response_plan()

        # Send event to EventBus (восстановленная функциональность)
        self.send_event_to_eventbus('bcm.incident.response_generated', {
            'incident_id': self.id,
            'severity': self.severity,
            'ai_activated': True
        })

        # Log emergency response activation
        self.message_post(
            body="Emergency AI response activated - legacy API compatibility",
            message_type='notification'
        )

        return self.action_start_response()

    def call_ai_orchestrator_fast_mode(self, prompt, context):
        """
        Backward compatibility wrapper for AI orchestrator calls
        Maps to new AI recommendation system with orchestrator integration
        """
        self.ensure_one()

        try:
            # Get AI orchestrator service config
            orchestrator_config = self.env['bcm.foundation.base'].search([
                ('service_endpoint', 'ilike', 'orchestrator'),
                ('active', '=', True)
            ], limit=1)

            if orchestrator_config:
                # Make external orchestrator call
                result = self._make_external_ai_call(
                    endpoint='/api/fast-analysis',
                    data={
                        'prompt': prompt,
                        'context': context,
                        'incident_id': self.incident_number,
                        'severity': self.severity,
                        'type': self.incident_type
                    }
                )

                if result:
                    # Update AI recommendations with orchestrator response
                    self.ai_recommendations = result.get('recommendations', '')
                    self.ai_risk_score = result.get('risk_score', 0)

                    return {
                        'success': True,
                        'response': result,
                        'recommendations': result.get('recommendations', ''),
                        'risk_score': result.get('risk_score', 0)
                    }

            # Fallback to internal AI if orchestrator unavailable
            self._trigger_ai_analysis()

            return {
                'success': True,
                'response': {
                    'recommendations': self.ai_recommendations,
                    'risk_score': self.ai_risk_score,
                    'fallback_mode': True
                }
            }

        except Exception as e:
            _logger.error(f"AI orchestrator call failed: {e}")

            # Emergency fallback response
            return self._emergency_fallback_response(context)

    def _emergency_fallback_response(self, context):
        """
        Backward compatibility wrapper for emergency fallback
        Enhanced with new incident workflow capabilities
        """
        self.ensure_one()

        # Basic emergency response based on incident type
        emergency_responses = {
            'cyber': [
                "IMMEDIATE: Isolate affected systems",
                "IMMEDIATE: Preserve logs and evidence",
                "URGENT: Notify security team",
                "URGENT: Reset credentials if breach suspected"
            ],
            'operational': [
                "IMMEDIATE: Check backup systems",
                "IMMEDIATE: Assess scope of impact",
                "URGENT: Activate contingency procedures",
                "URGENT: Communicate with affected users"
            ],
            'natural': [
                "IMMEDIATE: Ensure personnel safety",
                "IMMEDIATE: Contact emergency services if needed",
                "URGENT: Activate emergency procedures",
                "URGENT: Assess facility damage"
            ],
            'health_safety': [
                "IMMEDIATE: Ensure immediate safety",
                "IMMEDIATE: Contact emergency medical services",
                "URGENT: Evacuate if necessary",
                "URGENT: Document incident details"
            ]
        }

        fallback_response = emergency_responses.get(
            self.incident_type,
            [
                "IMMEDIATE: Assess situation",
                "URGENT: Implement containment measures",
                "URGENT: Notify stakeholders",
                "FOLLOW UP: Document actions taken"
            ]
        )

        # Update incident with fallback recommendations
        self.write({
            'ai_recommendations': "\n".join(f"• {action}" for action in fallback_response),
            'ai_risk_score': 75.0,  # High risk due to fallback mode
            'status': 'responding'
        })

        # Log fallback activation
        self.message_post(
            body=f"Emergency fallback response activated. Context: {context}",
            message_type='notification'
        )

        return {
            'success': True,
            'fallback_mode': True,
            'recommendations': fallback_response,
            'context': context
        }

    def action_ai_lifecycle_monitoring(self):
        """
        Backward compatibility wrapper for AI lifecycle monitoring
        Maps to new comprehensive incident analytics
        """
        self.ensure_one()

        # Calculate metrics using new methods
        response_time = self.actual_rto or 0
        effectiveness_score = self._calculate_effectiveness_score()
        learning_progress = self._assess_learning_progress()

        # Create comprehensive monitoring report
        monitoring_data = {
            'incident_id': self.incident_number,
            'avg_response_time': response_time,
            'effectiveness_score': effectiveness_score,
            'learning_progress': learning_progress,
            'ai_confidence': self.ai_classification_confidence or 0,
            'risk_score': self.ai_risk_score or 0,
            'status': self.status,
            'escalation_level': self.escalation_level,
            'timestamp': fields.Datetime.now().isoformat()
        }

        # Log monitoring data
        self.message_post(
            body=f"AI Lifecycle Monitoring Report:\n"
                 f"• Response Time: {response_time:.1f} hours\n"
                 f"• Effectiveness Score: {effectiveness_score:.1f}%\n"
                 f"• Learning Progress: {learning_progress:.1f}%\n"
                 f"• AI Risk Score: {self.ai_risk_score or 0:.1f}/100",
            message_type='notification'
        )

        return monitoring_data

    def _calculate_avg_response_time(self):
        """
        Backward compatibility wrapper - enhanced with new RTO calculation
        """
        return self.actual_rto or 0.0

    def _calculate_effectiveness_score(self):
        """
        Enhanced effectiveness calculation using new incident data
        """
        score = 50.0  # Base score

        # Adjust based on resolution time vs target
        if self.target_rto and self.actual_rto:
            if self.actual_rto <= self.target_rto:
                score += 30.0  # Met RTO target
            else:
                penalty = min(20.0, (self.actual_rto - self.target_rto) / self.target_rto * 20)
                score -= penalty

        # Adjust based on escalation levels
        score -= (self.escalation_level * 5.0)  # Penalty for escalations

        # Adjust based on AI confidence
        if self.ai_classification_confidence:
            score += (self.ai_classification_confidence / 100.0) * 10.0

        # Adjust based on post-incident review completion
        if self.post_incident_review_completed:
            score += 10.0

        return max(0.0, min(100.0, score))

    def _assess_learning_progress(self):
        """
        Enhanced learning assessment using AI and historical data
        """
        progress = 0.0

        # Base progress from similar incidents handling
        similar_count = len(self.ai_similar_incidents)
        if similar_count > 0:
            progress += min(40.0, similar_count * 10.0)

        # Progress from AI recommendations usage
        if self.ai_recommendations:
            progress += 20.0

        # Progress from lessons learned documentation
        if self.lessons_learned:
            progress += 25.0

        # Progress from preventive measures implementation
        if self.preventive_measures:
            progress += 15.0

        return min(100.0, progress)

    def _make_external_ai_call(self, endpoint, data):
        """Make external AI orchestrator call with proper error handling"""
        try:
            import requests
            import json

            # Get AI service configuration
            ai_service = self.env['bcm.foundation.service'].search([
                ('service_type', '=', 'ai_orchestrator'),
                ('is_active', '=', True),
                ('company_id', '=', self.company_id.id)
            ], limit=1)

            if not ai_service:
                return {'status': 'error', 'message': 'AI orchestrator service not configured'}

            # Prepare request
            url = f"{ai_service.full_url}/{endpoint.lstrip('/')}"
            headers = {'Content-Type': 'application/json'}

            if ai_service.auth_type == 'api_key' and ai_service.api_key:
                headers['X-API-Key'] = ai_service.api_key
            elif ai_service.auth_type == 'bearer_token' and ai_service.bearer_token:
                headers['Authorization'] = f'Bearer {ai_service.bearer_token}'

            # Make request with timeout and retry
            for attempt in range(ai_service.retry_attempts):
                try:
                    response = requests.post(
                        url,
                        headers=headers,
                        json=data,
                        timeout=ai_service.timeout
                    )

                    if response.status_code == 200:
                        return response.json()
                    else:
                        if attempt == ai_service.retry_attempts - 1:
                            return {
                                'status': 'error',
                                'message': f'HTTP {response.status_code}: {response.text}'
                            }
                except requests.exceptions.Timeout:
                    if attempt == ai_service.retry_attempts - 1:
                        return {'status': 'error', 'message': 'Request timeout'}
                except requests.exceptions.ConnectionError:
                    if attempt == ai_service.retry_attempts - 1:
                        return {'status': 'error', 'message': 'Connection failed'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _generate_ai_emergency_response_plan(self):
        """Generate AI-powered emergency response plan"""
        self.ensure_one()

        try:
            # Try external AI orchestrator first
            ai_result = self._make_external_ai_call(
                endpoint='/api/emergency-plan',
                data={
                    'incident_type': self.incident_type,
                    'severity': self.severity,
                    'description': self.description or '',
                    'affected_systems': self.affected_systems or '',
                    'business_impact': self.business_impact or ''
                }
            )

            if ai_result and ai_result.get('status') != 'error':
                # Update with AI-generated plan
                self.write({
                    'ai_recommendations': ai_result.get('emergency_plan', ''),
                    'ai_risk_score': ai_result.get('risk_assessment', 0),
                    'expected_rto': ai_result.get('estimated_rto', self.expected_rto)
                })
                return

        except Exception as e:
            _logger.warning(f"External AI call failed, using fallback: {e}")

        # Fallback: Generate basic emergency plan based on incident type
        emergency_plans = {
            'cyber': """
🚨 CYBER INCIDENT EMERGENCY RESPONSE PLAN

IMMEDIATE ACTIONS (0-15 minutes):
• Isolate affected systems from network
• Preserve digital evidence and logs
• Document attack vectors and impact scope
• Alert cybersecurity team and stakeholders

CONTAINMENT (15-60 minutes):
• Reset compromised credentials
• Apply security patches if vulnerability exploited
• Monitor for lateral movement
• Implement additional access controls

RECOVERY PLANNING:
• Assess data integrity and backup availability
• Plan system restoration sequence
• Coordinate with legal and compliance teams
• Prepare communication for affected parties
            """,
            'operational': """
🔧 OPERATIONAL INCIDENT EMERGENCY RESPONSE PLAN

IMMEDIATE ACTIONS (0-15 minutes):
• Assess impact on critical business functions
• Check status of backup systems and failovers
• Alert operations team and management
• Document scope and severity of disruption

STABILIZATION (15-60 minutes):
• Activate contingency procedures
• Redirect operations to backup systems
• Communicate with affected customers/users
• Monitor system performance and stability

RECOVERY PLANNING:
• Estimate restoration timeline
• Coordinate with technical teams
• Plan gradual service restoration
• Prepare post-incident analysis
            """,
            'natural': """
🌪️ NATURAL DISASTER EMERGENCY RESPONSE PLAN

IMMEDIATE ACTIONS (0-15 minutes):
• Ensure personnel safety and evacuation if needed
• Contact emergency services if required
• Assess facility damage and accessibility
• Account for all personnel

SAFETY MEASURES (15-60 minutes):
• Secure facility and equipment
• Document damage for insurance claims
• Activate alternate work locations
• Ensure communication channels remain open

BUSINESS CONTINUITY:
• Assess impact on critical operations
• Activate disaster recovery procedures
• Coordinate with facilities management
• Plan phased return to normal operations
            """,
        }

        plan = emergency_plans.get(self.incident_type, """
⚠️ GENERAL EMERGENCY RESPONSE PLAN

IMMEDIATE ACTIONS:
• Assess situation and impact scope
• Ensure personnel safety
• Alert appropriate response teams
• Document initial findings

CONTAINMENT:
• Implement immediate containment measures
• Prevent escalation of the incident
• Secure affected areas/systems
• Establish communication protocols

RECOVERY:
• Develop recovery timeline
• Coordinate response efforts
• Monitor progress and adjust plan
• Prepare for post-incident review
        """)

        # Update incident with generated plan
        self.write({
            'ai_recommendations': plan.strip(),
            'ai_risk_score': self._calculate_fallback_risk_score()
        })

    def _calculate_fallback_risk_score(self):
        """Calculate risk score when AI is unavailable"""
        base_score = {
            'low': 25,
            'medium': 50,
            'high': 75,
            'critical': 90
        }.get(self.severity, 50)

        # Adjust based on incident type
        type_multipliers = {
            'cyber': 1.2,
            'natural': 1.1,
            'health_safety': 1.3,
            'operational': 1.0
        }

        multiplier = type_multipliers.get(self.incident_type, 1.0)
        return min(100, base_score * multiplier)

    # ===== DIGITAL TWIN INTEGRATION METHODS =====

    @api.depends('digital_twin_simulation_ids')
    def _compute_simulation_count(self):
        """Compute number of digital twin simulations"""
        for record in self:
            record.simulation_count = len(record.digital_twin_simulation_ids)

    @api.depends('affected_systems', 'affected_locations')
    def _compute_affected_areas(self):
        """Compute affected areas from systems and locations"""
        for record in self:
            areas = []
            if record.affected_systems:
                areas.append(f"Systems: {record.affected_systems}")
            if record.affected_locations:
                areas.append(f"Locations: {record.affected_locations}")
            record.affected_areas = "\n".join(areas)

    @api.depends('actual_rto')
    def _compute_response_time(self):
        """Compute response time for Digital Twin"""
        for record in self:
            record.response_time = record.actual_rto or 0.0

    def action_run_crisis_simulation(self):
        """Run crisis management simulation for this incident - Digital Twin Integration"""
        self.ensure_one()

        try:
            # Find organization's digital twin through client
            twin_org = None
            if hasattr(self, 'client_id') and self.client_id:
                twin_org = self.client_id.digital_twin_ids.filtered(
                    lambda t: t.twin_status == 'active'
                )[:1]

            if twin_org:
                return {
                    'name': _('Crisis Simulation'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'bcm.digital.twin.simulation',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_organization_id': twin_org.id,
                        'default_related_incident': self.id,
                        'default_scenario_type': 'crisis_management',
                        'default_name': f"Crisis Simulation - {self.name}"
                    }
                }
            else:
                # Fallback: Open generic simulation creation
                return {
                    'name': _('Create Crisis Simulation'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'bcm.digital.twin.simulation',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_related_incident': self.id,
                        'default_scenario_type': 'crisis_management',
                        'default_name': f"Crisis Simulation - {self.name}",
                        'show_organization_warning': True
                    }
                }

        except Exception as e:
            _logger.error(f"Failed to create crisis simulation: {e}")
            raise UserError(_("Unable to create crisis simulation: %s") % str(e))

    def action_view_simulations(self):
        """View all digital twin simulations for this incident"""
        self.ensure_one()
        return {
            'name': _('Digital Twin Simulations'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.digital.twin.simulation',
            'view_mode': 'tree,form',
            'domain': [('related_incident', '=', self.id)],
            'context': {'default_related_incident': self.id}
        }

    def send_event_to_eventbus(self, event_type, data):
        """
        Send event to EventBus service - КРИТИЧНО ВОССТАНОВЛЕНО

        Оригинальный метод из bcm_core/models/bcm_models.py:54
        Был потерян при объединении модулей из-за отсутствия наследования от bcm.base
        """
        try:
            import logging
            _logger = logging.getLogger(__name__)

            # Простая версия как в оригинале - логирование события
            _logger.info(f"Event sent: {event_type} - {data}")

            # TODO: Интеграция с внешним EventBus сервисом
            # Пока используем базовое логирование как в оригинальном bcm_core

        except Exception as e:
            _logger = logging.getLogger(__name__)
            _logger.error(f"Failed to send event: {e}")


class BCMIncidentCategory(models.Model):
    """Категории инцидентов"""
    _name = 'bcm.incident.category'
    _description = 'Incident Category'
    
    name = fields.Char(required=True)
    code = fields.Char(required=True)
    severity_default = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'), 
        ('critical', 'Critical')
    ], string='Default Severity')
    rto_default = fields.Float(string='Default RTO (hours)')
    auto_escalate_after = fields.Integer(string='Auto Escalate After (minutes)')
    active = fields.Boolean(default=True)


class BCMIncidentFieldUpdate(models.Model):
    """Обновления с места событий"""
    _name = 'bcm.incident.field.update'
    _description = 'Field Update'
    _order = 'create_date desc'
    
    incident_id = fields.Many2one('bcm.incident', required=True, ondelete='cascade')
    reporter_id = fields.Many2one('hr.employee', required=True)
    update_text = fields.Text(required=True)
    gps_location = fields.Char(string='GPS Coordinates')
    photo_attachment = fields.Binary(string='Photo')
    create_date = fields.Datetime(default=fields.Datetime.now)