# -*- coding: utf-8 -*-
{
    'name': 'BCM AI Consultant',
    'version': '18.0.1.0.0',
    'category': 'Business Continuity',
    'sequence': 30,
    'summary': 'AI-powered BCM Consultant with ChatGPT/Claude Integration',
    'description': '''BCM AI Consultant - Smart Advisor
=======================================

Интеллектуальный консультант по непрерывности бизнеса с поддержкой ChatGPT-4 и Claude AI.

**AI Возможности:**
• Интеграция с ChatGPT-4 и Claude AI
• База знаний ISO 22301 и лучших практик
• Контекстные рекомендации для BCM
• Анализ рисков с предложениями мер
• Генерация планов и процедур

**Интерактивные консультации:**
• Чат-интерфейс с историей сессий
• Многоязычная поддержка (RU/EN)
• Персонализированные советы
• Интеграция с контекстом организации
• Экспорт диалогов в PDF/DOCX

**Умная аналитика:**
• Анализ готовности к чрезвычайным ситуациям
• Оценка зрелости BCM процессов
• Автоматические рекомендации по улучшению
• Прогнозирование рисков и трендов
• Benchmarking с отраслевыми стандартами

**ISO 22301 Соответствие:**
• Пункт 7.3: Осведомленность персонала
• Пункт 7.4: Коммуникация и консультации
• Пункт 9.1: Мониторинг эффективности''',
    'author': 'BCM Platform Team',
    'website': 'https://github.com/SEH-foundation/ISO-22301',
    'depends': [
        'base',
        'bcm_core',
        'bcm_ai_control',
        'bcm_base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ai_consultant_views.xml',
        'views/consultation_session_views.xml',
        'views/knowledge_base_views.xml',
        'views/menu_views.xml',
        'data/knowledge_base_data.xml',
    ],
    'assets': {'web.assets_backend': ['bcm_ai_consultant/static/src/xml/ai_consultant_widget.xml', 'bcm_ai_consultant/static/src/js/ai_consultant_widget.js', 'bcm_ai_consultant/static/src/css/ai_consultant.css']},
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
