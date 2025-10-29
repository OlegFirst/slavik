# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
import json


class BCMCrisisCommunicationPlan(models.Model):
    """План кризисной коммуникации"""
    _name = 'bcm.crisis.communication.plan'
    _description = 'Crisis Communication Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    crisis_level = fields.Selection([
        ('1', 'Minor Disruption'),
        ('2', 'Significant Disruption'), 
        ('3', 'Major Crisis'),
        ('4', 'Severe Crisis'),
        ('5', 'Catastrophic Event')
    ], string='Crisis Level', required=True)
    
    communication_templates = fields.One2many(
        'bcm.communication.template',
        'plan_id',
        string='Communication Templates'
    )
    
    stakeholder_groups = fields.Many2many(
        'res.partner.category',
        string='Stakeholder Groups'
    )
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)


class BCMCommunicationTemplate(models.Model):
    """Шаблоны кризисной коммуникации"""
    _name = 'bcm.communication.template'
    _description = 'Communication Template'

    name = fields.Char(required=True)
    plan_id = fields.Many2one('bcm.crisis.communication.plan', required=True)
    template_type = fields.Selection([
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('social', 'Social Media'),
        ('press', 'Press Release'),
        ('internal', 'Internal Communication')
    ], required=True)
    
    subject = fields.Char()
    content = fields.Html()
    send_delay = fields.Integer(string='Send Delay (minutes)', default=0)
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)


class BCMStakeholderNotification(models.Model):
    """Уведомления заинтересованных сторон"""
    _name = 'bcm.stakeholder.notification'
    _description = 'Stakeholder Notification'

    incident_id = fields.Many2one('bcm.incident', required=True, ondelete='cascade')
    notification_type = fields.Selection([
        ('initial', 'Initial Notification'),
        ('update', 'Status Update'),
        ('escalation', 'Escalation Notice'),
        ('resolution', 'Resolution Notice'),
        ('closure', 'Closure Notice')
    ], required=True)
    
    recipient = fields.Many2one('res.partner', required=True)
    sent_at = fields.Datetime()
    status = fields.Selection([
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed')
    ], default='pending')
    
    message_content = fields.Text()
    delivery_method = fields.Selection([
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('phone', 'Phone Call'),
        ('push', 'Push Notification')
    ], default='email')
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)


class BCMAIResponseTemplate(models.Model):
    """AI шаблоны реагирования"""
    _name = 'bcm.ai.response.template'
    _description = 'AI Response Template'

    name = fields.Char(required=True)
    incident_type = fields.Selection([
        ('operational', 'Operational Disruption'),
        ('cyber', 'Cyber Security'),
        ('natural', 'Natural Disaster'),
        ('supply_chain', 'Supply Chain'),
        ('health_safety', 'Health & Safety'),
        ('financial', 'Financial Impact'),
        ('reputational', 'Reputational Risk')
    ], required=True)
    
    priority_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], required=True)
    
    response_checklist = fields.Text()
    escalation_triggers = fields.Text()
    ai_confidence_threshold = fields.Float(default=80.0)
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)


class BCMAIClassificationRule(models.Model):
    """Правила AI классификации"""
    _name = 'bcm.ai.classification.rule'
    _description = 'AI Classification Rule'

    name = fields.Char(required=True)
    rule_type = fields.Selection([
        ('keyword_match', 'Keyword Matching'),
        ('pattern_recognition', 'Pattern Recognition'),
        ('ml_classification', 'ML Classification')
    ], required=True)
    
    incident_type = fields.Selection([
        ('operational', 'Operational'),
        ('cyber', 'Cyber Security'),
        ('natural', 'Natural Disaster'),
        ('supply_chain', 'Supply Chain'),
        ('health_safety', 'Health & Safety')
    ], required=True)
    
    keywords = fields.Text()
    confidence_weight = fields.Float(default=70.0)
    active = fields.Boolean(default=True)
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)


class BCMAIEscalationRule(models.Model):
    """Правила AI эскалации"""
    _name = 'bcm.ai.escalation.rule'
    _description = 'AI Escalation Rule'

    name = fields.Char(required=True)
    trigger_condition = fields.Text(required=True)
    action_type = fields.Selection([
        ('auto_escalate', 'Automatic Escalation'),
        ('notify_manager', 'Notify Manager'),
        ('activate_team', 'Activate Response Team'),
        ('send_alert', 'Send Alert')
    ], required=True)
    
    escalation_level = fields.Integer(default=1)
    notification_template = fields.Text()
    active = fields.Boolean(default=True)
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)


class BCMAILearningPattern(models.Model):
    """Паттерны машинного обучения AI"""
    _name = 'bcm.ai.learning.pattern'
    _description = 'AI Learning Pattern'

    name = fields.Char(required=True)
    pattern_type = fields.Selection([
        ('recovery_time_analysis', 'Recovery Time Analysis'),
        ('success_factor_analysis', 'Success Factor Analysis'),
        ('failure_pattern_recognition', 'Failure Pattern Recognition'),
        ('escalation_prediction', 'Escalation Prediction')
    ], required=True)
    
    incident_type = fields.Selection([
        ('operational', 'Operational'),
        ('cyber', 'Cyber Security'),
        ('natural', 'Natural Disaster'),
        ('supply_chain', 'Supply Chain'),
        ('health_safety', 'Health & Safety')
    ])
    
    pattern_data = fields.Text()
    confidence_level = fields.Float()
    last_updated = fields.Datetime(default=fields.Datetime.now)
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)