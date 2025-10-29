# -*- coding: utf-8 -*-
{
    'name': 'BCM KPI',
    'version': '18.0.1.0.0',


    'summary': 'KPI management with real-time monitoring, alerts and performance scorecards',
    'description': '''BCM KPI - Performance Management 🎯
====================================

Управление ключевыми показателями BCM.

**📏 Стандартные KPI:**
• MTPD - Maximum Tolerable Period of Disruption
• RTO - Recovery Time Objective
• RPO - Recovery Point Objective
• Участие в учениях
• Актуальность планов
• Время реагирования

**⚡ Real-time мониторинг:**
• Live dashboards
• Threshold алерты
• Trend indicators
• Predictive analytics
• Anomaly detection

**🏆 Scorecards:**
• Balanced scorecard
• Department metrics
• Individual performance
• Team achievements
• Benchmarking

**📊 Отчетность:**
• C-level dashboards
• Drill-down анализ
• Historical trends
• Forecast модели
• What-if сценарии''',
    'category': 'Business Continuity',


    'author': 'BCM Platform Team',


    'website': 'https://github.com/SEH-foundation/ISO-22301',


    'license': 'LGPL-3',


    'depends': [
        'base',
        'web',
        'mail',
        'bcm_core',
        'bcm_context',
        'bcm_plans', 
        'bcm_incident',
        'bcm_governance',  # CRITICAL FIX: Added for compliance KPIs
        'bcm_intelligent_base',  # CRITICAL FIX: Added for AI analytics
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,

    'auto_install': False,




    'sequence': 36,

}
