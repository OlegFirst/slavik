# -*- coding: utf-8 -*-
{
    'name': 'BCM Plans',
    'version': '18.0.1.0.0',
    'summary': 'Business continuity and recovery plan management with version control',
    'description': '''BCM Plans - Recovery Planning 📑
=================================

Управление планами непрерывности и восстановления.

**📋 Типы планов:**
• Business Continuity Plans (BCP)
• Disaster Recovery Plans (DRP)
• Emergency Response Plans (ERP)
• Crisis Communication Plans
• Pandemic Response Plans
• Cyber Incident Response Plans

**🔄 Управление версиями:**
• Version control
• Change tracking
• Approval workflows
• Review schedules
• Distribution control

**📝 Компоненты планов:**
• Activation procedures
• Contact lists
• Recovery procedures
• Resource requirements
• Alternative sites
• Vendor information

**🚀 Функции:**
• Template library
• Multi-format export
• Plan testing integration
• Maintenance scheduling
• Gap identification''',
    'category': 'Business Continuity',
    'author': 'BCM Platform Team',
    'website': 'https://github.com/SEH-foundation/ISO-22301',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'bcm_core',
        'bcm_base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 16,
}
