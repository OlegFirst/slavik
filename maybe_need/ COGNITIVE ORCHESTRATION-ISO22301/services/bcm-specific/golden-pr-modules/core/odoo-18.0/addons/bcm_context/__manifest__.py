# -*- coding: utf-8 -*-
{
    'name': 'BCM Context',
    'version': '18.0.1.0.0',


    'summary': 'Organizational context management per ISO 22301 Clause 4',
    'description': '''BCM Context - Organization Analysis 🏢
=======================================

Управление контекстом организации (ISO 22301 Clause 4).

**🎯 Элементы контекста:**
• Внутренний контекст
• Внешний контекст
• Заинтересованные стороны
• Область применения BCMS
• Требования и ожидания

**📊 Анализ организации:**
• Структура организации
• Продукты и услуги
• Локации и объекты
• Технологические зависимости
• Правовые требования
• Культурные факторы

**🔄 Управление изменениями:**
• Context monitoring
• Change tracking
• Impact assessment
• Stakeholder updates
• Requirement updates

**📝 Документация:**
• Context statements
• Stakeholder registry
• Scope definitions
• Requirement matrix
• Integration maps''',
    'category': 'Business Continuity',


    'author': 'BCM Platform Team',


    'website': 'https://github.com/SEH-foundation/ISO-22301',


    'license': 'LGPL-3',


    'depends': [
        'base',
        'web',
        'mail',
        'bcm_core',
    ],
    'data': [
        'security/bcm_context_security.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,

    'auto_install': False,




    'sequence': 8,

}
