# -*- coding: utf-8 -*-
{
    'name': 'BCM Risk Management',
    'version': '18.0.2.0.0',
    'category': 'Business Continuity',
    'summary': 'AI Risk Advisor with FAIR methodology and Monte Carlo simulation',
    'description': '''BCM Risk Management - AI Risk Advisor 🎯
=========================================

Продвинутое управление рисками с AI Risk Advisor.

**🧮 Методологии оценки:**
• FAIR (Factor Analysis of Information Risk)
• Monte Carlo симуляция (10,000 итераций)
• Матрицы вероятности и воздействия
• Анализ сценариев "что если"

**🤖 AI возможности:**
• Предиктивная аналитика рисков
• Раннее предупреждение об угрозах
• Автоматическая генерация сценариев
• Корреляционный анализ рисков
• NLP для анализа отчетов

**📊 Визуализация:**
• Heat maps рисков
• Временные тренды
• Bow-tie диаграммы
• Dashboard руководителя
• Real-time алерты

**⚙️ Автоматизация:**
• Триггеры для BIA анализа
• Интеграция с Incident Management
• Автоматические отчеты
• Уведомления о превышении порогов''',
    'author': 'BCM Platform Team',
    'website': 'https://github.com/SEH-foundation/ISO-22301',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'bcm_core',
        'bcm_base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/risk_ai_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 11,
}
