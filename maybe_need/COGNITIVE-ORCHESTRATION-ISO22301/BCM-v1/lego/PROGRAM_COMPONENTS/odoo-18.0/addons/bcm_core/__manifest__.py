# -*- coding: utf-8 -*-
{
    'name': 'BCM Core - Business Continuity Foundation',
    'version': '18.0.2.0.0',  # AI LIFECYCLE MONITOR UPDATE


    'category': 'Business Continuity',


    'sequence': 1,

    'summary': 'Core BCM functionality: Organization context, base configurations, and ISO 22301 framework',
    'description': """
BCM Core Module - Foundation Layer 🏢
=====================================

Фундаментальный модуль платформы BCM, обеспечивающий базовую инфраструктуру для всей системы.

**🎯 Основные функции:**
• Управление контекстом организации
• Структура бизнес-единиц и подразделений
• Реестр критически важных функций
• Управление заинтересованными сторонами (RACI матрица)
• Правовые и регуляторные требования
• AI Lifecycle Monitor - мониторинг здоровья 10 AI-органов
• Мультитенантная архитектура

**📊 Ключевые возможности:**
• Централизованный профиль организации
• Иерархическая структура бизнес-единиц
• Картирование критических функций и процессов
• Отслеживание зависимостей между функциями
• Реестр соответствия требованиям
• Интеграция с Keycloak SSO
• Полная изоляция данных по компаниям

**🏆 ISO 22301 Соответствие:**
• Пункт 4.1: Понимание организации и ее контекста
• Пункт 4.2: Понимание потребностей заинтересованных сторон
• Пункт 4.3: Определение области применения BCMS
• Пункт 4.4: Система управления непрерывностью бизнеса

**🔧 Технические детали:**
• PostgreSQL для хранения критических данных
• Redis для кэширования конфигураций (TTL 15 мин)
• Базовые классы для всех BCM модулей
• EventBus интеграция для real-time уведомлений
• REST API endpoints для внешних интеграций

**📦 Модели данных:**
• bcm.plan - Планы восстановления и непрерывности
• bcm.incident - Управление инцидентами
• bcm.business.process - Бизнес-процессы
• bcm.ai.lifecycle - Мониторинг AI органов
• bcm.stakeholder - Реестр заинтересованных сторон
• bcm.critical.function - Критические бизнес-функции
    """,
    'author': 'BCM Platform Team',


    'website': 'https://github.com/SEH-foundation/ISO-22301',


    'license': 'LGPL-3',


    'depends': ['base', 'mail', 'bcm_base'],
    'data': [
        # Security
        'security/bcm_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/bcm_core_data.xml',
        'data/bcm_sequences.xml',

        # Views
        'views/menu.xml',
        'views/bcm_plan_views.xml',
        'views/bcm_incident_views.xml',
        'views/bcm_business_process_views.xml',
        'views/bcm_ai_lifecycle_views.xml',
    ],
    'demo': [
    ],
    # 'assets': {
    # },
    'installable': True,


    'application': True,


    'auto_install': False,


    # 'post_init_hook': 'post_init_hook',
    # 'uninstall_hook': 'uninstall_hook',
}
