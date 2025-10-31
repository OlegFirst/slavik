# -*- coding: utf-8 -*-
{
    'name': 'BCM Intelligent Base',
    'version': '18.0.1.0.0',


    'category': 'Business Continuity',


    'summary': 'Base AI services and intelligent processing capabilities',
    'description': '''BCM Intelligent Base - AI Services 🧠
======================================

Базовые AI сервисы и интеллектуальная обработка.

**🤖 Общие AI сервисы:**
• Natural language processing
• Document analysis
• Pattern recognition
• Predictive analytics
• Text generation
• Translation services

**⚙️ Базовые возможности:**
• AI service abstraction
• Common utilities
• Model management
• Prompt library
• Response caching

**🔧 Технические функции:**
• Service patterns
• Base AI classes
• Processing templates
• Error handling
• Performance optimization

**🔗 Интеграции:**
• AI model APIs
• Processing pipelines
• Service orchestration
• Cache management
• Queue processing''',
    'author': 'BCM Platform Team',


    'website': 'https://github.com/SEH-foundation/ISO-22301',


    'license': 'LGPL-3',


    'depends': [
        'base',
        'web',
        'mail',
        'project',
        'hr',
        'website',
        'portal',
        'bcm_governance',  # CRITICAL UPDATE: Added for governance integration
        # 'bcm_community',   # REMOVED: Caused circular dependency
    ],
    'external_dependencies': {
        'python': [
            'requests',
            'httpx',
            'pydantic',
            'numpy',
            'pandas',
            'fastapi',
        ]
    },
    'data': [
        # Security
        'security/bcm_security.xml',
        'security/ir.model.access.csv',
        
        # Core data
        'data/bcm_service_configs.xml',
    ],
    'demo': [
    ],
    # 'assets': {
    # },
    'installable': True,
    'application': True,

    'auto_install': False,




    'sequence': 6,

    # 'post_init_hook': 'post_init_hook',
    # 'uninstall_hook': 'uninstall_hook',
}
