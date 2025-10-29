# -*- coding: utf-8 -*-
{
    'name': 'BCM Clients',
    'version': '18.0.1.0.0',
    'summary': 'Multi-tenant client management with data isolation and security',
    'description': '''BCM Clients - Client Management 👥
====================================

Мультитенантное управление клиентами.

**🏢 Управление клиентами:**
• Client profiles
• Organization data
• Contact management
• Service agreements
• Billing information

**🔐 Изоляция данных:**
• Company-based isolation
• Dedicated databases
• Access controls
• Data encryption
• Audit trails

**⚙️ Конфигурации:**
• Client-specific settings
• Custom branding
• Module access
• User limits
• Storage quotas

**📊 Функции:**
• Onboarding workflows
• Service tracking
• Usage analytics
• Client reporting
• Support tickets''',
    'category': 'Business Continuity',
    'author': 'BCM Platform Team',
    'website': 'https://github.com/SEH-foundation/ISO-22301',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'bcm_core',
        'bcm_base',
    ],
    'external_dependencies': {'python': ['requests', 'hashlib', 'json']},
    'data': [
        'security/bcm_clients_security.xml',
        'security/ir.model.access.csv',
        'data/bcm_clients_data.xml',
        'views/bcm_client_views.xml',
        'views/bcm_client_contact_views.xml',
        'views/bcm_client_vault_views.xml',
        'views/bcm_client_appkey_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/clients_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 49,
    'post_init_hook': 'post_init_hook',
}
