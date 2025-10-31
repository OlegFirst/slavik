# -*- coding: utf-8 -*-
{
    'name': 'BCM Scenario Hub',
    'version': '18.0.2.0.0',  # AI SCENARIO CREATOR UPDATE


    'summary': 'Community marketplace for BCM scenarios with AI generation and one-click deployment',
    'description': '''BCM Scenario Hub - Scenario Marketplace
===========================================

Маркетплейс и библиотека сценариев BCM.

**Маркетплейс функции:**
• Каталог готовых сценариев
• Рейтинги и отзывы
• Публикация сообществом
• Модерация контента
• Лицензирование

**Категории сценариев:**
• Пандемия/Эпидемия
• Отключение электричества
• Кибератаки
• Сбои цепочки поставок
• Природные катастрофы
• Социальные волнения
• Технологические сбои

**AI генерация:**
• Создание сценариев по описанию
• Адаптация под отрасль
• Локализация сценариев
• Сложность по уровням
• Автоматические инъекции

**One-click deployment:**
• Применение к клиентам
• Кастомизация параметров
• Планирование учений
• Tracking результатов
• Benchmarking''',
    'category': 'Business Continuity',
    'summary': 'Community marketplace for BCM scenarios with AI generation and one-click deployment',
    'author': 'BCM Platform Team',
    'website': 'https://github.com/SEH-foundation/ISO-22301',
    'license': 'LGPL-3',


    'depends': [
        'base',
        'web',
        'mail',
        'website',
        'bcm_clients',
        'bcm_digital_twin_core',
        'bcm_community',  # CRITICAL FIX: Added missing dependency
        'bcm_governance',  # CRITICAL FIX: Added for compliance integration
    ],
    'external_dependencies': {
        'python': ['markdown', 'requests']
    },
    'data': [
        'security/bcm_scenario_security.xml',
        'security/ir.model.access.csv',
        'views/bcm_scenario_views.xml',
        'views/bcm_scenario_review_views.xml',
        'views/bcm_scenario_rating_views.xml',
        'views/bcm_tag_domain_views.xml',
        'views/bcm_scenario_hub_menus.xml',
    ],
    # 'assets': {
    # },
    'demo': [
    ],
    'installable': True,
    'application': True,

    'auto_install': False,




    'sequence': 26,

}
