# -*- coding: utf-8 -*-
{
    'name': 'BCM Incident',
    'version': '18.0.5.0.0',  # FIXED UNKNOWN OBJECT ERROR


    'summary': 'Core incident management functionality with AI-generated responses',
    'description': '''BCM Incident - Core Management 🚨
==================================

Базовая функциональность управления инцидентами.

**📝 Управление инцидентами:**
• Incident reporting
• Categorization
• Status tracking
• Workflow management
• Resolution tracking

**🤖 AI функции:**
• Auto-classification
• Response checklists
• Similar incidents
• Recovery suggestions
• Impact analysis

**📊 Tracking:**
• Incident timeline
• Activity logs
• Communication records
• Resource usage
• Resolution documentation

**🔄 Интеграция:**
• Notification system
• Escalation rules
• Team assignments
• External alerts
• Report generation''',
    'category': 'Business Continuity',


    'author': 'BCM Platform Team',


    'website': 'https://github.com/SEH-foundation/ISO-22301',


    'license': 'LGPL-3',


    'depends': [
        'base',
        'web',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/bcm_incident_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,

    'auto_install': False,




    'sequence': 13,

}
