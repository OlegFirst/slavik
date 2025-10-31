# -*- coding: utf-8 -*-
{
    'name': 'BCM Exercise',
    'version': '18.0.1.0.0',
    'summary': 'Exercise planning and execution for tabletop, functional and full-scale simulations',
    'description': '''BCM Exercise - Training & Simulations 🎮
=========================================

Планирование и проведение учений BCM.

**🎯 Типы учений:**
• Настольные (Tabletop)
• Функциональные
• Полномасштабные симуляции
• Drill упражнения
• Ориентационные сессии

**📅 Планирование:**
• Календарь учений
• Назначение участников
• Распределение ролей
• Подготовка материалов
• Логистика и ресурсы

**🎬 Проведение:**
• Контроль инъекций
• Real-time мониторинг
• Коммуникационный хаб
• Tracking решений
• Хронометраж

**📊 Оценка результатов:**
• Метрики производительности
• Gap анализ
• After-action reports
• Improvement планы
• Lessons learned''',
    'category': 'Business Continuity',
    'author': 'BCM Platform Team',
    'website': 'https://github.com/SEH-foundation/ISO-22301',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'bcm_core',
        'bcm_plans',
        'bcm_base',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 30,
}
