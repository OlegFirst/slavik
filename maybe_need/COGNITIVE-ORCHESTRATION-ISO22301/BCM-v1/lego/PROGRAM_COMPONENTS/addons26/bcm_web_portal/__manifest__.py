# -*- coding: utf-8 -*-
{
    'name': 'BCM Web Portal',
    'version': '18.0.1.0.0',
    'category': 'Business Continuity',
    'summary': 'Unified web portal with client self-service and admin interface (portal + admin_website)',
    'description': '''
BCM Web Portal - Unified Web Interface 🌐
=========================================

Объединенный веб-портал, включающий:

**🏠 Client Portal (из bcm_portal):**
• Client self-service dashboard
• BIA results viewing
• Business continuity plans access
• Incident reporting
• Exercise participation
• Training materials access
• Document management

**⚙️ Admin Interface (из admin_website functionality):**
• System administration panel
• User management interface
• Content management system
• Configuration settings
• System monitoring dashboard
• Audit logs and analytics

**🌍 Public Website:**
• Landing pages
• Product information
• Contact forms
• Public documentation
• Client registration

**🔐 Unified Authentication:**
• Single Sign-On (SSO) integration
• Multi-factor authentication
• Role-based access control
• Session management
• Security audit logging

**📱 Responsive Design:**
• Mobile-friendly interface
• Adaptive layouts
• Touch-optimized controls
• Progressive web app features
• Offline capability

**🤖 AI Integration:**
• AI assistant widget
• Smart search functionality
• Intelligent recommendations
• Automated support responses
• Predictive analytics

**🔄 API Gateway:**
• RESTful API endpoints
• GraphQL support
• WebSocket connections
• Real-time notifications
• Third-party integrations

**🔄 Unified Benefits:**
• Single entry point for all users
• Consistent UI/UX experience
• Shared components and resources
• Simplified maintenance (2→1 module)
• Better performance and security
• Centralized analytics
    ''',
    'author': 'BCM Platform Team',
    'website': 'https://github.com/SEH-foundation/ISO-22301',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'portal',
        'website',
        'mail',
        'auth_signup',
        'bcm_clients',  # Client management (NOT merged)
        'bcm_core',
        'bcm_training',
        'bcm_exercise',
        'bcm_governance',
        'bcm_community',
        'bcm_intelligent_base',  # AI integration
    ],
    'external_dependencies': {
        'python': [
            'requests',
            'PyJWT',
            'werkzeug',
            'qrcode',
            'passlib',
        ]
    },
    'data': [
        # Security
        'security/portal_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/portal_groups.xml',
        'data/portal_menus.xml',
        'data/mail_templates.xml',
        
        # Views - Backend
        'views/portal_user_views.xml',
        'views/portal_settings_views.xml',
        'views/portal_content_views.xml',
        'views/portal_analytics_views.xml',
        'views/admin_dashboard_views.xml',
        'views/menu.xml',
        
        # Website Templates
        'website/templates/portal_layout.xml',
        'website/templates/client_portal.xml',
        'website/templates/admin_interface.xml',
        'website/templates/public_pages.xml',
        'website/templates/auth_pages.xml',
    ],
    'demo': [
        'demo/demo_portal_users.xml',
        'demo/demo_portal_content.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # Portal CSS
            'bcm_web_portal/static/src/scss/portal.scss',
            'bcm_web_portal/static/src/scss/client_portal.scss',
            'bcm_web_portal/static/src/scss/admin_interface.scss',
            
            # Portal JavaScript
            'bcm_web_portal/static/src/js/portal_main.js',
            'bcm_web_portal/static/src/js/client_dashboard.js',
            'bcm_web_portal/static/src/js/admin_dashboard.js',
            'bcm_web_portal/static/src/js/ai_assistant.js',
            'bcm_web_portal/static/src/js/websocket_client.js',
            
            # Third-party libraries
            'bcm_web_portal/static/lib/js/chart.min.js',
            'bcm_web_portal/static/lib/js/moment.min.js',
        ],
        'web.assets_backend': [
            'bcm_web_portal/static/src/scss/backend_portal.scss',
            'bcm_web_portal/static/src/js/portal_backend.js',
            'bcm_web_portal/static/src/js/portal_widgets.js',
        ],
    },
    'controllers': [
        'controllers.portal_main',
        'controllers.client_portal',
        'controllers.admin_interface',
        'controllers.api_endpoints',
        'controllers.auth_controller',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 10,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
