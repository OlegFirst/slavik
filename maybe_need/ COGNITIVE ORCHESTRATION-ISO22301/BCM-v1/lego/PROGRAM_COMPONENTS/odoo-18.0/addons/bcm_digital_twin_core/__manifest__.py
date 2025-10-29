# -*- coding: utf-8 -*-
{
    'name': 'BCM Digital Twin Core',
    'version': '18.0.1.0.0',
    'category': 'Business Continuity',
    'sequence': 4,
    'summary': 'Digital twin integration for organization simulation and predictive modeling',
    'description': '''BCM Digital Twin - Virtual Organization
===========================================

Цифровой двойник организации для симуляций.

**Поддержка доменов:**
• Корпоративный сектор
• Государственные организации
• НКО
• Критическая инфраструктура

**Симуляции:**
• What-if анализ
• Stress testing
• Прогнозное моделирование
• Сценарное планирование
• Impact propagation

**3D визуализация:**
• Виртуальные офисы
• Сетевые топологии
• Process flows
• Resource maps
• Risk landscapes

**Интеграция:**
• IoT датчики
• SCADA системы
• ERP данные
• Real-time feeds
• AI predictions''',
    'author': 'BCM Platform Team',
    'website': 'https://github.com/SEH-foundation/ISO-22301',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'bcm_core',
        'bcm_intelligent_base',
        'bcm_base',
    ],
    'data': [
        'security/digital_twin_security.xml',
        'security/ir.model.access.csv',
        'data/digital_twin_sequences.xml',
        'data/digital_twin_data.xml',
        'views/digital_twin_organization_views.xml',
        'views/digital_twin_simulation_views.xml',
        'views/digital_twin_config_views.xml',
        'views/digital_twin_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
