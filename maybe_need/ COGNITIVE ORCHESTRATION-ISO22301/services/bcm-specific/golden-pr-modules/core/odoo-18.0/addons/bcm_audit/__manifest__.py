# -*- coding: utf-8 -*-
{
    'name': 'BCM Audit',
    'version': '18.0.1.0.0',


    'summary': 'Audit management with compliance tracking, CAPA and gap analysis',
    'description': '''BCM Audit - Compliance Assurance 📋
====================================

Управление аудитами и соответствием.

**🔍 Типы аудитов:**
• Внутренние аудиты
• Внешние аудиты
• Compliance аудиты
• Supplier аудиты
• Self-assessments

**📝 Управление находками:**
• Finding tracking
• CAPA управление
• Evidence collection
• Root cause анализ
• Corrective actions

**🎯 Compliance функции:**
• ISO 22301 чеклисты
• Gap анализ
• Compliance scoring
• Maturity оценка
• Certification support

**📊 Отчетность:**
• Audit dashboards
• Finding trends
• CAPA статус
• Compliance metrics
• Executive reports''',
    'category': 'Business Continuity',


    'author': 'BCM Platform Team',


    'website': 'https://github.com/SEH-foundation/ISO-22301',


    'license': 'LGPL-3',


    'depends': [
        'base',
        'web',
        'mail',
        'bcm_core',
        'bcm_context',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
    ],
    'demo': [
        'demo/audit_demo.xml',
    ],
    'installable': True,
    'application': True,

    'auto_install': False,




    'sequence': 37,
}
