# -*- coding: utf-8 -*-
{
    'name': 'BCM Base - AI Foundation',
    'version': '18.0.1.0.0',
    'category': 'Business Continuity',
    'sequence': 2,
    'summary': 'Base module with AI Orchestrator, Document Processor, and Compliance Checker',
    'description': """
BCM Base - AI Foundation Module 🤖
===================================

Базовый модуль с AI-интеграцией для всей платформы BCM.

**🧠 AI Компоненты:**
• AI Orchestrator - координация 10 AI-органов
• Document Processor - интеллектуальная обработка документов
• Compliance Checker - проверка соответствия ISO 22301
• REST API интеграция с внешними AI сервисами

**⚙️ Основные функции:**
• Базовые классы и общие утилиты для всех модулей
• Валидаторы и бизнес-правила
• Управление API-аутентификацией и сессиями
• Централизованное логирование и мониторинг
• Обработка ошибок и восстановление

**🔗 Интеграции:**
• Anthropic Claude API (claude-3-opus)
• Локальные AI модели (fallback)
• EventBus для real-time коммуникаций
• Внешние REST API сервисы
• Webhook обработчики

**📊 Сервисные конфигурации:**
• Настройки подключения к микросервисам
• Управление API ключами
• Конфигурация endpoints
• Мониторинг состояния сервисов
• Автоматическое переподключение

**🔧 Технические возможности:**
• Абстрактные базовые модели для наследования
• Общие миксины и декораторы
• Утилиты для работы с данными
• Кэширование и оптимизация
• Асинхронная обработка задач

Этот модуль является обязательной зависимостью для всех других BCM модулей.
    """,
    'author': 'BCM Platform Team',
    'website': 'https://github.com/SEH-foundation/ISO-22301',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
    ],
    'external_dependencies': {
        'python': [
            'requests',
        ]
    },
    'data': [
        'security/bcm_security.xml',
        'security/ir.model.access.csv',
        'data/bcm_data.xml',
        'views/bcm_service_config_views.xml',
        'views/bcm_menus.xml',
    ],
    'demo': [
    ],
    # 'assets': {
    # },
    'installable': True,
    'auto_install': False,
    'application': True,
}
