# -*- coding: utf-8 -*-
{
    'name': 'BCM Incident Management Unified',
    'version': '18.0.1.0.0',
    'category': 'Business Continuity',
    'sequence': 12,
    'summary': 'Unified incident management with AI Commander, crisis response, and comprehensive workflow automation',
    'description': '''BCM Incident Management Unified 🚨
==========================================

Объединенное управление инцидентами с полным функционалом.

**🎯 ОБЪЕДИНЕННЫЙ ФУНКЦИОНАЛ:**
• Все функции bcm_incident (базовые)
• Все функции bcm_incident_management (расширенные)
• AI Commander с интеллектуальными рекомендациями
• Мобильное реагирование и GPS координация
• Автоматизированные workflows

**📝 БАЗОВОЕ УПРАВЛЕНИЕ ИНЦИДЕНТАМИ:**
• Incident reporting & categorization
• Status tracking & workflow management
• Timeline & activity logs
• Resolution documentation
• Integration с notification системами

**🤖 AI COMMANDER ФУНКЦИИ:**
• Автоматическая классификация инцидентов
• Интеллектуальная маршрутизация команд
• Генерация response checklists
• Предсказание эскалации рисков
• Анализ похожих инцидентов
• Рекомендации по восстановлению

**🎭 РАСШИРЕННАЯ КЛАССИФИКАЦИЯ:**
• Уровни: Critical / High / Medium / Low
• Типы: Natural / Cyber / Operational / Pandemic / Supply Chain
• Автоматическое определение приоритетов
• Интеграция с risk management

**📱 МОБИЛЬНАЯ КООРДИНАЦИЯ:**
• Мобильные отчеты об инцидентах
• GPS tracking команд реагирования
• Push notifications для команд
• Offline режим для критических ситуаций
• Виртуальный командный центр

**🔄 АВТОМАТИЗИРОВАННЫЕ WORKFLOWS:**
• Автоматические каскады уведомлений
• Escalation rules с временными триггерами
• Integration с external alerting systems
• Automated resource allocation
• Post-incident analysis workflows

**📊 РАСШИРЕННАЯ ОТЧЕТНОСТЬ:**
• Real-time dashboards & metrics
• Executive-level reporting
• Compliance reporting (ISO 22301)
• Lessons learned database
• Performance analytics & trends

**🔗 ИНТЕГРАЦИИ:**
• TheHive для security incidents
• External monitoring systems
• Communication platforms (Slack, Teams)
• GIS системы для location tracking
• ERP системы для resource management

**📋 ISO 22301 СООТВЕТСТВИЕ:**
• Полное соответствие требованиям стандарта
• Документированные процедуры
• Audit trail для всех действий
• Compliance reporting
• Continuous improvement процессы

Этот модуль объединяет лучшие практики incident management
с современными AI технологиями для максимальной эффективности
реагирования на business disruptions.
    ''',
    'author': 'BCM Platform Team',
    'website': 'https://github.com/SEH-foundation/ISO-22301',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'hr',        # Для управления response teams
        'calendar',  # Для планирования exercises
        'bcm_core',      # Базовая BCM инфраструктура
        'bcm_base',      # Базовый модуль BCM
        'bcm_config',    # Конфигурация BCM
        'bcm_context',   # Контекст организации BCM
    ],
    'external_dependencies': {
        'python': [
            'requests',  # Для external API integrations
            'geopy',     # Для GPS/location функций
            'numpy',     # Для AI analytics
        ]
    },
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/incident_security.xml',
        'security/record_rules.xml',
        
        # Data
        'data/migration_data.xml',
        'data/incident_sequences.xml',
        'data/incident_types_data.xml',
        'data/ai_commander_data.xml',
        'data/cron_jobs.xml',
        
        # Views - Core Incident Management
        'views/bcm_incident_views.xml',
        'views/incident_category_views.xml',
        'views/incident_status_views.xml',
        
        # Views - AI Commander
        'views/ai_commander_views.xml',
        'views/ai_recommendations_views.xml',
        'views/similar_incidents_views.xml',
        
        # Views - Response Teams
        'views/response_team_views.xml',
        'views/team_member_views.xml',
        'views/escalation_rules_views.xml',
        
        # Views - Crisis Communication
        'views/crisis_communication_views.xml',
        'views/communication_templates_views.xml',
        'views/stakeholder_notification_views.xml',
        
        # Views - Mobile & GPS
        'views/mobile_response_views.xml',
        'views/gps_tracking_views.xml',
        'views/field_operations_views.xml',
        
        # Views - Analytics & Reporting
        'views/incident_analytics_views.xml',
        'views/performance_metrics_views.xml',
        'views/lessons_learned_views.xml',
        
        # Views - Integrations
        'views/external_integrations_views.xml',
        'views/api_connections_views.xml',
        
        # Menus
        'views/incident_menus.xml',
        
        # Reports
        'reports/incident_reports.xml',
        'reports/incident_report_templates.xml',
        'reports/executive_summary_report.xml',
        
        # Wizards
        'wizards/incident_escalation_wizard.xml',
        'wizards/mass_notification_wizard.xml',
        'wizards/incident_closure_wizard.xml',
    ],
    'demo': [
        'demo/incident_demo_data.xml',
        'demo/response_team_demo.xml',
        'demo/ai_recommendations_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'bcm_incident_unified/static/src/css/incident_dashboard.css',
            'bcm_incident_unified/static/src/css/mobile_interface.css',
            'bcm_incident_unified/static/src/js/incident_timeline.js',
            'bcm_incident_unified/static/src/js/ai_commander_widget.js',
            'bcm_incident_unified/static/src/js/gps_tracking.js',
            'bcm_incident_unified/static/src/js/real_time_updates.js',
        ],
        'web.assets_frontend': [
            'bcm_incident_unified/static/src/css/mobile_reporting.css',
            'bcm_incident_unified/static/src/js/mobile_incident_form.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    
    # Module Classification
    'category_priority': 1,
    'website_path': '/bcm/incidents',
    
    # Technical metadata
    'cloc_exclude': [
        'static/src/lib/**/*',
        'static/description/demo_*',
    ],
    
    # Compatibility
    'odoo_version': '18.0',
    'python_version': '>=3.8',
    
    # Performance hints
    'preload_dependencies': True,
    'lazy_load_modules': [
        'bcm_incident_unified.gps_tracking',
        'bcm_incident_unified.ai_analytics',
    ],
}