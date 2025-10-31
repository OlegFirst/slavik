# -*- coding: utf-8 -*-
{
    'name': 'BCM Reporting',
    'version': '18.0.1.0.0',


    'category': 'Business Continuity',


    'summary': 'Cross-module analytics with dashboards, automated reports and data visualization',
    'description': 'BCM reporting and analytics module',
    'author': 'BCM Platform Team',


    'website': 'https://github.com/SEH-foundation/ISO-22301',


    'license': 'LGPL-3',


    'depends': ['base', 'web', 'mail', 'bcm_core', 'bcm_governance', 'bcm_community', 'bcm_intelligent_base'],  # CRITICAL UPDATE: Added governance dependencies
    'data': [
        'security/ir.model.access.csv',
        'views/simple_menu.xml',
    ],
    'installable': True,
    'application': True,



    'auto_install': False,
    'sequence': 35,
}