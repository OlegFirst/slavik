# -*- coding: utf-8 -*-
{
    'name': 'BCM Admin Website',
    'version': '18.0.1.0.0',
    'category': 'Business Continuity',
    'sequence': 60,
    'summary': 'Web-based administration interface for system management',
    'description': '''BCM Admin Website - System Admin 🖥️
====================================

Веб-интерфейс администрирования системы.

**👤 Управление пользователями:**
• User provisioning
• Role management
• Permission control
• Password resets
• Account monitoring

**📊 System monitoring:**
• Health checks
• Performance metrics
• Error tracking
• Resource usage
• Service status

**⚙️ Администрирование:**
• Module management
• Configuration control
• Log viewing
• Backup management
• Update control

**🔐 Безопасность:**
• Access logs
• Security alerts
• Session management
• IP restrictions
• Admin audit trail''',
    'author': 'BCM Platform Team',
    'website': 'https://github.com/SEH-foundation/ISO-22301',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'website',
        'bcm_core',
        'bcm_base',
    ],
    'data': [
        'security/admin_website_security.xml',
        'security/ir.model.access.csv',
        'templates/admin_dashboard.xml',
        'templates/admin_modules.xml',
        'templates/admin_module_detail.xml',
        'templates/admin_ai.xml',
        'templates/admin_users.xml',
        'templates/admin_reports.xml',
        'templates/admin_settings.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
