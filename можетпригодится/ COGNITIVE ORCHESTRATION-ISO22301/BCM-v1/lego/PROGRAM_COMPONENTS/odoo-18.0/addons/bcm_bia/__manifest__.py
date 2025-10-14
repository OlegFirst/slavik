# -*- coding: utf-8 -*-
{
    'name': 'BCM BIA - Business Impact Analysis',
    'version': '18.0.2.0.0',
    'summary': 'AI-Powered BIA with ML-enhanced BIA Engine v2.0 for RTO/RPO optimization',
    'description': '''BCM BIA - Business Impact Analysis 📊
======================================

AI-усиленный анализ воздействия на бизнес с ML-оптимизацией.

**🚀 BIA Engine v2.0:**
• ML-алгоритмы для расчета RTO/RPO
• Автоматическое определение критичности
• Финансовое моделирование потерь
• Каскадный анализ зависимостей
• Интеграция с микросервисом (порт 8082)

**🏭 Поддержка 9 отраслей:**
• Финансовые услуги
• Здравоохранение
• Производство
• Розничная торговля
• IT и технологии
• Энергетика
• Транспорт и логистика
• Государственный сектор
• Образование

**📈 Аналитика и отчеты:**
• Матрица приоритетов восстановления
• Анализ финансового воздействия
• Карты зависимостей процессов
• Требования к ресурсам
• ROI анализ мер защиты

**🔧 ML Возможности:**
• Паттерн-анализ исторических данных
• Предиктивное моделирование
• Аномальное обнаружение зависимостей
• Автоматическая калибровка коэффициентов''',
    'category': 'Business Continuity',
    'author': 'BCM Development Team',
    'website': 'https://github.com/SEH-foundation/ISO-22301',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'bcm_core',
        'bcm_base',
    ],
    'external_dependencies': {'python': ['requests', 'numpy', 'pandas']},
    'data': [
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
}
