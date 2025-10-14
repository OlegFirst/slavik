# -*- coding: utf-8 -*-

from . import models
from . import wizards
from . import controllers

def post_init_hook(env):
    """
    Post-installation hook для настройки unified incident module
    """
    # Создаем default incident categories
    create_default_incident_categories(env)
    
    # Настраиваем AI Commander default rules
    setup_ai_commander_defaults(env)
    
    # Создаем default response team templates
    create_default_response_teams(env)
    
    # Настраиваем cron jobs для автоматизации
    setup_automation_jobs(env)


def create_default_incident_categories(env):
    """Создание базовых категорий инцидентов"""
    categories = [
        {
            'name': 'Operational Disruption',
            'code': 'OPS',
            'severity_default': 'medium',
            'rto_default': 4,  # hours
            'auto_escalate_after': 60,  # minutes
        },
        {
            'name': 'Cyber Security Incident',
            'code': 'CYBER',
            'severity_default': 'high',
            'rto_default': 1,  # hours
            'auto_escalate_after': 30,  # minutes
        },
        {
            'name': 'Natural Disaster',
            'code': 'NATURAL',
            'severity_default': 'critical',
            'rto_default': 8,  # hours
            'auto_escalate_after': 15,  # minutes
        },
        {
            'name': 'Supply Chain Disruption',
            'code': 'SUPPLY',
            'severity_default': 'medium',
            'rto_default': 24,  # hours
            'auto_escalate_after': 120,  # minutes
        },
        {
            'name': 'Health & Safety Emergency',
            'code': 'HEALTH',
            'severity_default': 'critical',
            'rto_default': 0.5,  # hours
            'auto_escalate_after': 10,  # minutes
        },
        {
            'name': 'Financial Impact Event',
            'code': 'FINANCIAL',
            'severity_default': 'high',
            'rto_default': 2,  # hours
            'auto_escalate_after': 45,  # minutes
        }
    ]
    
    IncidentCategory = env['bcm.incident.category']
    
    for cat_data in categories:
        existing = IncidentCategory.search([('code', '=', cat_data['code'])])
        if not existing:
            IncidentCategory.create(cat_data)


def setup_ai_commander_defaults(env):
    """Настройка AI Commander по умолчанию"""
    ai_rules = [
        {
            'name': 'Auto-classify by keywords',
            'trigger_type': 'on_create',
            'condition': 'description_contains_keywords',
            'action': 'classify_incident',
            'active': True,
        },
        {
            'name': 'Auto-escalate critical incidents',
            'trigger_type': 'on_severity_change',
            'condition': 'severity_is_critical',
            'action': 'immediate_escalation',
            'active': True,
        },
        {
            'name': 'Generate response checklist',
            'trigger_type': 'on_status_change',
            'condition': 'status_is_responding',
            'action': 'create_checklist',
            'active': True,
        },
        {
            'name': 'Find similar incidents',
            'trigger_type': 'on_create',
            'condition': 'always',
            'action': 'analyze_similar',
            'active': True,
        }
    ]
    
    AIRule = env['bcm.ai.rule']
    
    for rule_data in ai_rules:
        existing = AIRule.search([('name', '=', rule_data['name'])])
        if not existing:
            AIRule.create(rule_data)


def create_default_response_teams(env):
    """Создание шаблонов команд реагирования"""
    team_templates = [
        {
            'name': 'Crisis Management Team',
            'code': 'CMT',
            'description': 'Executive-level crisis management',
            'activation_criteria': 'Critical incidents requiring executive decision',
            'roles': [
                'Incident Commander',
                'Communications Lead', 
                'Operations Manager',
                'Legal Advisor',
                'HR Representative'
            ]
        },
        {
            'name': 'IT Emergency Response',
            'code': 'IT-ERT',
            'description': 'Technical incident response team',
            'activation_criteria': 'IT systems and cyber security incidents',
            'roles': [
                'IT Manager',
                'Security Specialist',
                'Systems Administrator',
                'Network Engineer',
                'Database Administrator'
            ]
        },
        {
            'name': 'Physical Security Team',
            'code': 'PST',
            'description': 'Physical security and safety response',
            'activation_criteria': 'Physical security breaches and safety emergencies',
            'roles': [
                'Security Manager',
                'Safety Officer',
                'Facilities Manager',
                'First Aid Responder',
                'Local Emergency Contact'
            ]
        }
    ]
    
    ResponseTeam = env['bcm.response.team.template']
    
    for team_data in team_templates:
        existing = ResponseTeam.search([('code', '=', team_data['code'])])
        if not existing:
            ResponseTeam.create(team_data)


def setup_automation_jobs(env):
    """Настройка cron jobs для автоматизации"""
    cron_jobs = [
        {
            'name': 'AI Commander: Process Pending Recommendations',
            'model_id': env.ref('bcm_incident_unified.model_bcm_incident').id,
            'code': 'model.process_ai_recommendations()',
            'interval_number': 5,
            'interval_type': 'minutes',
            'active': True,
        },
        {
            'name': 'Auto-escalate Overdue Incidents',
            'model_id': env.ref('bcm_incident_unified.model_bcm_incident').id,
            'code': 'model.check_escalation_rules()',
            'interval_number': 15,
            'interval_type': 'minutes',
            'active': True,
        },
        {
            'name': 'Update GPS Tracking Data',
            'model_id': env.ref('bcm_incident_unified.model_bcm_response_team_member').id,
            'code': 'model.update_gps_locations()',
            'interval_number': 2,
            'interval_type': 'minutes',
            'active': True,
        },
        {
            'name': 'Generate Daily Incident Reports',
            'model_id': env.ref('bcm_incident_unified.model_bcm_incident').id,
            'code': 'model.generate_daily_reports()',
            'interval_number': 1,
            'interval_type': 'days',
            'active': True,
        }
    ]
    
    CronJob = env['ir.cron']
    
    for job_data in cron_jobs:
        existing = CronJob.search([('name', '=', job_data['name'])])
        if not existing:
            CronJob.create(job_data)


def uninstall_hook(env):
    """
    Cleanup hook при удалении модуля
    """
    # Деактивируем cron jobs
    cron_jobs = env['ir.cron'].search([
        ('name', 'like', 'AI Commander%'),
        ('name', 'like', 'Auto-escalate%'),
        ('name', 'like', 'Update GPS%'),
        ('name', 'like', 'Generate Daily%')
    ])
    cron_jobs.write({'active': False})
    
    # Архивируем активные инциденты (не удаляем!)
    active_incidents = env['bcm.incident'].search([
        ('status', 'not in', ['resolved', 'closed'])
    ])
    active_incidents.write({'active': False})
    
    # Логируем uninstall
    env['ir.logging'].sudo().create({
        'name': 'bcm_incident_unified.uninstall',
        'type': 'server',
        'level': 'INFO',
        'message': f'Module uninstalled. {len(active_incidents)} incidents archived.',
        'path': __file__,
        'func': 'uninstall_hook',
    })