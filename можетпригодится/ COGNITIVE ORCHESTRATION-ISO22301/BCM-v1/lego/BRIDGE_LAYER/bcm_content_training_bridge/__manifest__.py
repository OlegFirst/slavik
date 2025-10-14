# -*- coding: utf-8 -*-
{
    'name': 'BCM Content & Training Bridge',
    'version': '18.0.4.0.0',
    'summary': 'Bridge module: BCM content + Odoo gamification, e-learning, calendar & events',
    'description': '''
BCM Content Library Unified - Combined Module
==============================================

This module combines functionality from:
- bcm_templates: Document templates with AI generation
- bcm_scenario_hub: Scenario marketplace and library

Key Features:
-------------
**📄 Document Templates:**
• Policy templates
• Procedure templates
• Assessment forms
• Reports and checklists
• Communication templates
• Monaco editor integration
• Version control

**🎯 Scenario Library:**
• Crisis scenarios
• Exercise scenarios
• Response playbooks
• Industry-specific scenarios
• AI scenario generation
• Scenario rating system

**🛍️ Marketplace Features:**
• Community sharing
• Template/scenario ratings
• One-click deployment
• Customization wizard
• Export/import functionality

**🤖 AI Capabilities:**
• Content generation
• Auto-completion
• Compliance checking
• Language translation
• Industry adaptation
• Scenario creation from description

**🔧 Management:**
• Unified content catalog
• Approval workflows
• Access control
• Change tracking
• Version management
• Usage analytics
    ''',
    'category': 'Business Continuity',
    'author': 'BCM Platform Team',
    'website': 'https://github.com/SEH-foundation/ISO-22301',
    'license': 'LGPL-3',

    'depends': [
        'base',
        'web',
        'mail',
        'website',
        'bcm_core',
        'bcm_clients',
        'bcm_templates',         # Original template module
        'bcm_scenario_hub',      # Original scenario module
        'bcm_training',          # For e-learning integration

        # Odoo native modules for bridge
        'gamification',          # Odoo gamification system
        'calendar',              # Odoo calendar & events
        'website_slides',        # Odoo e-learning platform
        'survey',                # For assessments and quizzes
    ],

    'external_dependencies': {
        'python': ['markdown', 'requests']
    },

    'data': [
        # Security
        'security/content_library_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/content_categories.xml',
        'data/template_data.xml',
        'data/scenario_data.xml',

        # Views - Templates
        'views/template_views.xml',
        'views/document_views.xml',

        # Views - Scenarios
        'views/scenario_views.xml',
        'views/scenario_review_views.xml',
        'views/scenario_rating_views.xml',

        # Views - Common
        'views/content_marketplace_views.xml',
        'views/tag_domain_views.xml',

        # Menus
        'views/menu.xml',

        # Wizards
        'wizard/content_import_wizard_views.xml',
        'wizard/scenario_deployment_wizard_views.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'bcm_content_library_unified/static/src/js/monaco_editor.js',
            'bcm_content_library_unified/static/src/js/content_library.js',
            'bcm_content_library_unified/static/src/scss/content_library.scss',
        ],
        'web.assets_frontend': [
            'bcm_content_library_unified/static/src/js/marketplace.js',
            'bcm_content_library_unified/static/src/scss/marketplace.scss',
        ],
    },

    'demo': [
        'demo/templates_demo.xml',
        'demo/scenarios_demo.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 25,

    'post_init_hook': 'post_init_content_library',
    'uninstall_hook': 'uninstall_content_library',
}