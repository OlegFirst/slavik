# -*- coding: utf-8 -*-
{
    'name': 'BCM Project Management',
    'version': '18.0.1.0.0',
    'category': 'BCM/Project',
    'summary': 'AI-Powered Business Continuity Project Management',
    'description': """
BCM Project Management Module
==============================

Transform standard Odoo Project Management into an intelligent BCM command center:

Key Features:
-------------
* **Smart Project Templates**: Auto-generate project structure based on BCM type
* **AI Task Generation**: Intelligent task creation based on best practices
* **Auto Assignment**: Smart resource allocation based on skills and availability
* **Health Monitoring**: Real-time project health status with predictive alerts
* **Automated Escalation**: Proactive issue detection and escalation
* **Recovery Planning**: Specialized tools for recovery plan implementation
* **Exercise Management**: Complete exercise lifecycle from planning to reporting
* **Compliance Tracking**: Built-in ISO 22301 compliance monitoring

AI Capabilities:
----------------
* Predictive deadline adjustments
* Risk-based prioritization
* Intelligent resource optimization
* Automated progress analysis
* Smart notification system

Perfect for:
------------
* BCM Managers
* Crisis Management Teams
* Recovery Coordinators
* Exercise Planners
* Compliance Officers
    """,
    'author': 'BCM Platform Team',
    'website': 'https://github.com/bcm-platform',
    'license': 'OPL-1',
    'depends': [
        'base',
        'project',
        'hr',
        'hr_skills',
        'calendar',
        'mail',
        'web_dashboard',
    ],
    'external_dependencies': {
        'python': [
            'pandas',
            'numpy',
            'requests',
        ],
    },
    'data': [
        # Security
        'security/bcm_project_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/bcm_project_data.xml',
        'data/bcm_project_templates.xml',
        'data/bcm_project_stages.xml',
        'data/ir_cron_data.xml',

        # Views
        'views/bcm_project_views.xml',
        'views/bcm_project_task_views.xml',
        'views/bcm_project_dashboard.xml',
        'views/bcm_project_menus.xml',

        # Wizards
        'wizard/bcm_project_generator_views.xml',
        'wizard/bcm_ai_assistant_views.xml',

        # Reports
        'reports/bcm_project_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'bcm_project_management/static/src/js/bcm_project_dashboard.js',
            'bcm_project_management/static/src/js/bcm_gantt_view.js',
            'bcm_project_management/static/src/css/bcm_project.css',
            'bcm_project_management/static/src/xml/bcm_project_templates.xml',
        ],
    },
    'demo': [
        'demo/bcm_project_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}