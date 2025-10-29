# -*- coding: utf-8 -*-
{
    'name': 'BCM Governance',
    'version': '18.0.2.0.0',  # AI GOVERNANCE BRAIN UPDATE


    'summary': 'AI Governance Brain for strategic BCM management and compliance',
    'description': '''BCM Governance - Strategic Management 🏛️
=========================================

Стратегическое управление BCM с AI Governance Brain.

**🧠 AI Governance Brain:**
• Стратегические рекомендации
• Анализ соответствия стандартам
• Предиктивная аналитика трендов
• Бенчмаркинг с индустрией
• Регуляторный мониторинг

**📋 Управление политиками:**
• Библиотека политик и процедур
• Workflow согласования
• Контроль версий
• Автоматические напоминания о пересмотре
• Интеграция с ISO 22301

**🎯 Комплаенс функции:**
• Gap-анализ соответствия
• Трекинг корректирующих действий
• Регуляторная отчетность
• Аудит trail
• Сертификационная поддержка

**📊 Отчетность для руководства:**
• Executive dashboards
• Board reporting пакеты
• Метрики зрелости BCMS
• ROI анализ BCM программы''',
    'category': 'Business Continuity',


    'author': 'BCM Platform Team',


    'website': 'https://github.com/SEH-foundation/ISO-22301',


    'license': 'LGPL-3',


    'depends': [
        'base',
        'web',
        'mail',
        'hr',  # Для управления персоналом
        'bcm_context',  # Связь с контекстом организации
        # CRITICAL FIX: Removed bcm_intelligent_base and bcm_kpi to break circular dependencies
        # These will be integrated at runtime through API calls
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/bcm_governance_data.xml',
        'data/iso22301_compliance_data.xml',
        'views/bcm_risk_views.xml',
        'views/bcm_compliance_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/governance_demo.xml',
    ],
    'installable': True,
    'application': True,

    'auto_install': False,




    'sequence': 15,
}
