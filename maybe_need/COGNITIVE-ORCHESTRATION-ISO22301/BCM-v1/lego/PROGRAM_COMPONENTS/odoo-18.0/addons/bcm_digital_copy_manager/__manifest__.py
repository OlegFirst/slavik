# -*- coding: utf-8 -*-
{
    'name': 'BCM Digital Copy Manager',
    'version': '18.0.1.0.0',
    'category': 'Business Continuity',
    'sequence': 25,
    'summary': 'Digital Twin Snapshot and Version Control System',
    'description': '''BCM Digital Copy Manager - Time Travel
==============================================

Система управления цифровыми копиями (снапшотами) организаций для возврата к стабильным состояниям.

**Основные функции:**
• Создание снапшотов состояния Digital Twin
• Версионность и история изменений
• Сравнение состояний между снапшотами
• Восстановление из снапшотов
• Автоматическое резервное копирование по расписанию

**Управление версиями:**
• Полные и инкрементальные снапшоты
• Дерево зависимостей между копиями
• Теги и метаданные для категоризации
• Автоматическая очистка истекших копий
• Сжатие и оптимизация хранения

**Быстрое восстановление:**
• Одним кликом к любому состоянию
• Предварительный просмотр изменений
• Валидация целостности данных
• Rollback с проверкой зависимостей

**ISO 22301 Соответствие:**
• Пункт 8.4.2: Процедуры восстановления
• Пункт 8.5: Мониторинг и измерение
• Пункт 9.1: Внутренний аудит состояний''',
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
        'views/digital_copy_views.xml',
        'views/menu_views.xml',
        'data/sequence_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
