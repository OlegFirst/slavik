# -*- coding: utf-8 -*-
{
    'name': 'BCM Templates',
    'version': '18.0.1.0.0',
    'summary': 'Document templates library with AI generation and Monaco editor integration',
    'description': '''BCM Templates - Document Library 📄
====================================

Библиотека шаблонов с AI-генерацией.

**📚 Категории шаблонов:**
• Политики BCM
• Процедуры
• Формы оценки
• Отчеты
• Чек-листы
• Коммуникации

**🤖 AI возможности:**
• Генерация контента
• Auto-completion
• Проверка соответствия
• Перевод на языки
• Адаптация под отрасль

**✏️ Monaco Editor:**
• Syntax highlighting
• IntelliSense
• Multi-cursor editing
• Find and replace
• Code folding

**🔧 Управление:**
• Version control
• Approval workflow
• Access control
• Change tracking
• Export formats''',
    'category': 'Business Continuity',
    'author': 'BCM Platform Team',
    'website': 'https://github.com/SEH-foundation/ISO-22301',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'bcm_core',
        'bcm_base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/bcm_templates_data.xml',
        'views/bcm_template_views.xml',
        'views/bcm_document_views.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 40,
}
