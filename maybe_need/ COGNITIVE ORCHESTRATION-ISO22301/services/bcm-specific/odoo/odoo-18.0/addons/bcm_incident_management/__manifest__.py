# -*- coding: utf-8 -*-
{
    'name': 'BCM Incident Management',
    'version': '18.0.2.0.0',  # UPDATED FOR ODOO 18 COMPATIBILITY


    'category': 'Business Continuity',


    'summary': 'Advanced incident management with AI Commander and automated response workflows',
    'description': '''BCM Incident Management - Crisis Response 🚨
=============================================

Комплексное управление инцидентами с AI Commander.

**🎭 Классификация инцидентов:**
• Уровни: Критический / Высокий / Средний / Низкий
• Типы: Природные / Кибер / Операционные / Пандемия
• Автоматическая классификация через AI

**🤖 AI Commander функции:**
• Интеллектуальная маршрутизация
• Генерация чек-листов реагирования
• Предсказание эскалации
• Рекомендации по восстановлению
• Анализ похожих инцидентов

**📱 Координация реагирования:**
• Мобильное приложение для отчетов
• Автоматические каскады уведомлений
• Виртуальный командный центр
• Интеграция с системами оповещения
• GPS tracking команд реагирования

**📊 Мониторинг и отчетность:**
• Real-time дашборды
• Таймлайн событий
• Метрики реагирования
• Post-incident анализ
• Lessons learned база знаний''',
    'author': 'BCM Platform Team',


    'website': 'https://github.com/SEH-foundation/ISO-22301',


    'license': 'LGPL-3',


    'depends': [
        'base',
        'web',
        'mail',
        'bcm_core',
        'bcm_incident',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'data/cron_jobs.xml',
    ],
    'installable': True,
    'application': True,



    'auto_install': False,


    'sequence': 12,

}
