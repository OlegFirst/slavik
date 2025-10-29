{
    'name': 'BCM Config',
    'version': '18.0.1.0.0',


    'category': 'Business Continuity',


    'summary': 'System configuration and integration management hub',
    'description': '''BCM Config - System Configuration 🔧
=====================================

Централизованное управление конфигурациями.

**⚙️ Области конфигурации:**
• Email настройки
• Notification preferences
• Integration endpoints
• Security settings
• Performance tuning
• Backup configuration

**🔗 Управление интеграциями:**
• API endpoints
• Webhook management
• External services
• Authentication keys
• Rate limiting

**📊 System parameters:**
• Global settings
• Module configurations
• Feature toggles
• Default values
• System limits

**🔐 Безопасность:**
• Access controls
• Encryption settings
• Audit configuration
• Session management
• Password policies''',
    'author': 'BCM Platform Team',


    'website': 'https://github.com/SEH-foundation/ISO-22301',


    'license': 'LGPL-3',


    'depends': ['base', 'bcm_core'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,



    'auto_install': False,
    'sequence': 45,
}
