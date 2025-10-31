# -*- coding: utf-8 -*-
{
    'name': 'BCM AI Universal Bridge',
    'version': '18.0.1.0.0',
    'category': 'BCM/Intelligence',
    'summary': 'Universal bridge connecting all BCM modules with Meta-AI',
    'description': """
BCM AI Universal Bridge
=======================

Универсальный мост, объединяющий все BCM модули с центральным Meta-AI:

🧠 Core Features:
- Единая точка коммуникации с Meta-AI
- Event-driven архитектура для межмодульного взаимодействия
- Интеллектуальная оркестрация решений между модулями
- Централизованное обучение и распространение знаний

🔌 Integration Capabilities:
- BCM Project Management ↔ Risk Management
- Risk Assessment ↔ Incident Response
- Training ↔ Audit & Compliance
- All modules ↔ Central Intelligence

🎯 Business Value:
- Холистический подход к BCM
- Кросс-модульная аналитика
- Предиктивные возможности
- Автоматизация бизнес-процессов
    """,
    'author': 'BCM Platform Team',
    'website': 'https://bcm-platform.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'bus',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/bcm_ai_bridge_security.xml',
        'views/bcm_ai_bridge_views.xml',
        'data/bcm_ai_bridge_data.xml',
        'data/bcm_event_bus_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 5,
    'pre_init_hook': '_pre_init_hook',
    'post_init_hook': '_post_init_hook',
}