# -*- coding: utf-8 -*-
{
    'name': 'BCM Microservices Bridge',
    'version': '18.0.1.0.0',
    'category': 'Business Continuity',
    'summary': 'Universal bridge between Odoo BCM modules and external microservices',
    'description': '''BCM Microservices Bridge 🌉
====================================

Universal communication bridge that connects Odoo BCM modules
with external platform microservices.

**🔗 Bridge Capabilities:**
• Service Discovery - auto-detect platform services
• HTTP/WebSocket communication with microservices
• Event routing between Odoo and external services
• Service health monitoring and failover
• API versioning and compatibility handling

**🏗️ Platform Integration:**
• AI Cluster (orchestrator, consultant, analytics)
• Document Services (processor, storage, search)
• Integration Hub (thehive, moodle, governance)
• Notification Center (email, slack, webhooks)

**🧬 Organism Integration:**
• Extends BCM Event Bus to external services
• Routes organism events to microservices
• Converts microservice responses to Odoo events
• Health monitoring for entire platform

**🔄 Migration Support:**
• Gradual microservice → Odoo module conversion
• Legacy service compatibility during migration
• Service wrapper for external APIs
• Database sync between services and Odoo''',
    'author': 'BCM Platform Team',
    'website': 'https://github.com/SEH-foundation/ISO-22301',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'bus',
        'bcm_ai_bridge',    # Depends on our AI Bridge
        'bcm_core'          # Depends on BCM Core if exists
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/microservices_bridge_views.xml',
        'data/microservices_configuration.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 5,
}