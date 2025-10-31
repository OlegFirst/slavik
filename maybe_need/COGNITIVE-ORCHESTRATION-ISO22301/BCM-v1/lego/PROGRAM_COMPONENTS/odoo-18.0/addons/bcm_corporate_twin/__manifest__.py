# -*- coding: utf-8 -*-
{
    'name': 'BCM Corporate Digital Twin',
    'version': '18.0.1.0.0',
    'category': 'Business Continuity',
    'sequence': 75,
    'summary': 'Corporate-specific Digital Twin with financial modeling, supply chain analysis and compliance tracking',
    'description': '''BCM Corporate Digital Twin - Enterprise Focus
==============================================

Корпоративный модуль Digital Twin с углубленной аналитикой для бизнеса.

**Финансовое моделирование:**
• Cash flow анализ и прогнозирование
• Revenue impact симуляции
• Budget allocation оптимизация
• Cost-benefit анализ BCM мер
• Financial stress testing

**Supply Chain анализ:**
• Supplier dependency mapping
• Disruption impact моделирование
• Alternative supplier анализ
• Inventory optimization
• Logistics resilience planning

**Compliance tracking:**
• Regulatory compliance мониторинг
• SOX, GDPR, отраслевые стандарты
• Audit trail и документооборот
• Risk assessment автоматизация
• Compliance dashboard

**Market simulation:**
• Competitive analysis моделирование
• Market share impact симуляции
• Customer behavior predictions
• Brand reputation tracking
• Economic scenario planning

**BCM корпоративные метрики:**
• Business process criticality
• Employee productivity impact
• Customer satisfaction metrics
• Operational efficiency KPIs
• Stakeholder communication effectiveness

**Integration возможности:**
• ERP systems integration
• CRM data synchronization
• Financial systems connectivity
• HR platforms integration
• Business intelligence tools''',
    'author': 'BCM Platform Team',
    'website': 'https://github.com/SEH-foundation/ISO-22301',
    'depends': [
        'base',
        'bcm_core',
        'bcm_digital_twin_core',
        'bcm_base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/corporate_twin_views.xml',
        'views/financial_model_views.xml',
        'views/supply_chain_views.xml',
        'views/compliance_views.xml',
        'views/menu_views.xml',
        'data/corporate_twin_data.xml',
    ],
    'assets': {'web.assets_backend': ['bcm_corporate_twin/static/src/js/corporate_dashboard.js', 'bcm_corporate_twin/static/src/css/corporate_twin.css']},
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
