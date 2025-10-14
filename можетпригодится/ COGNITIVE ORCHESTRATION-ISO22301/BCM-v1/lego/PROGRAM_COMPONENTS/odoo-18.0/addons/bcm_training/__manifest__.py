# -*- coding: utf-8 -*-
{
    'name': 'BCM Training',
    'version': '18.0.1.0.0',
    'summary': 'Learning management with AI Coach for BCM awareness and competence',
    'description': '''BCM Training - Learning & Development 🎓
=========================================

Управление обучением с AI Learning Coach.

**🤖 AI Learning Coach:**
• Персонализированные учебные траектории
• Адаптивное тестирование
• Генерация учебных материалов
• Q&A чат-бот поддержка
• Анализ пробелов в знаниях

**📚 Программы обучения:**
• Общая осведомленность BCM
• Ролевое обучение
• Кризисное реагирование
• Сертификационная подготовка
• Симуляционные тренинги

**🎯 Управление компетенциями:**
• Матрицы компетенций по ролям
• Skills assessment
• Gap анализ
• Планы развития
• Tracking прогресса

**📊 Аналитика обучения:**
• Completion rates
• Engagement метрики
• ROI обучения
• Effectiveness scoring
• Compliance отчеты''',
    'category': 'Business Continuity',
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
        'data/bcm_training_data.xml',
        'views/bcm_training_views.xml',
        'views/bcm_competence_views.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 20,
}
