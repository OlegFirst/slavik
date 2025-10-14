# -*- coding: utf-8 -*-
{
    'name': 'BCM Portal',
    'version': '18.0.1.0.0',
    'summary': 'Client self-service portal with dashboards, document management and AI assistant',
    'description': '''BCM Portal - Client Self-Service 🌐
====================================

Клиентский портал самообслуживания.

**🏠 Главный дашборд:**
• KPI и метрики BCM
• Критические алерты
• Upcoming события
• Quick actions
• AI ассистент виджет

**📂 Разделы портала:**
• BIA результаты
• Планы непрерывности
• Инциденты
• Учения
• Аудиты и CAPA
• Обучение

**⚡ Быстрые действия:**
• Загрузка evidence
• Запрос аудита
• Создание инцидента
• Планирование учения
• Обновление контактов

**🔐 Безопасность:**
• SSO через Keycloak
• Multi-factor auth
• Ролевая модель
• Audit logging
• Data encryption''',
    'category': 'Business Continuity',
    'author': 'BCM Platform Team',
    'website': 'https://github.com/SEH-foundation/ISO-22301',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'portal',
        'bcm_core',
        'bcm_base',
    ],
    'external_dependencies': {'python': ['requests', 'PyJWT', 'werkzeug']},
    'data': [
        'templates/portal_templates.xml',
        'templates/bcm_dashboard_templates.xml',
        'templates/bcm_bia_templates.xml',
        'templates/bcm_sections_templates.xml',
        'templates/bcm_exercise_templates.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 50,
}
