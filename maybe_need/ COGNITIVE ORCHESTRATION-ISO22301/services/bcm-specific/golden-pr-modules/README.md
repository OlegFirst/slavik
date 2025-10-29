# 📦 GOLDEN-PR: 26 Консолидированных BCM Модулей

Экспорт из ветки `golden-pr-iso22301` проекта ISO-22301 BCM Platform

**Дата экспорта**: 2025-09-28
**Источник**: git branch `golden-pr-iso22301`
**Количество модулей**: 26

---

## 📋 Список модулей (26)

1. bcm_ai_consultant - AI консультант
2. bcm_ai_control - AI Control Center
3. bcm_ai_twin_orchestrator - AI Twin оркестратор
4. bcm_audit - Аудит
5. bcm_base - Базовый модуль с AI Foundation
6. bcm_bia - Business Impact Analysis
7. bcm_clients - Управление клиентами
8. bcm_community - Community & Knowledge Hub
9. bcm_config - Конфигурация
10. bcm_context - Контекст организации
11. bcm_core - Core модуль
12. bcm_corporate_twin - Корпоративный цифровой двойник
13. bcm_digital_copy_manager - Digital Copy Manager
14. bcm_digital_twin_core - Digital Twin Core
15. bcm_exercise - Учения и тренировки
16. bcm_governance - Управление и комплаенс
17. bcm_incident - Управление инцидентами (UNIFIED)
18. bcm_intelligent_base - Интеллектуальная база
19. bcm_kpi - KPI и метрики
20. bcm_plans - Планы непрерывности
21. bcm_reporting - Отчётность
22. bcm_risk_management - Управление рисками
23. bcm_scenario_hub - Центр сценариев
24. bcm_templates - Шаблоны документов
25. bcm_training - Обучение
26. **bcm_web_portal** - ✅ ПОЛНОЦЕННЫЙ веб-портал (unified)

---

## 🔑 Ключевые отличия от текущей ветки

### Консолидация:
- **bcm_web_portal** здесь ПОЛНЫЙ (на текущей ветке - пустой)
- **bcm_incident** единый модуль (на текущей ветке разделён на `bcm_incident` + `bcm_incident_management`)
- Отсутствуют: `bcm_admin_website`, `bcm_portal` (их функции в `bcm_web_portal`)

### Архитектурная разница:
**Golden-PR (26 модулей)**: Консолидированная структура
- Один unified портал
- Один модуль инцидентов
- Меньше дублирования

**Текущая ветка (29 модулей)**: Разделённая структура
- Разделённые порталы (portal + admin_website)
- Два модуля инцидентов
- Больше гибкости, но сложнее поддержка

---

## 📊 Статистика кода

По размеру и функциональности код **идентичен**:
- bcm_bia/models/models.py: 464 строки (одинаково)
- bcm_governance/models/models.py: 568 строк (одинаково)
- Все AI-специфичные файлы присутствуют

---

## 🎯 Назначение этой папки

Эта папка создана для:
1. Сравнения архитектурных подходов
2. Анализа консолидированной структуры
3. Возможного переноса полного `bcm_web_portal`
4. Архивирования стабильной версии

**НЕ переключаясь на ветку**, можно изучить и скопировать нужные компоненты.

---

## 📍 Расположение

```
/Users/MD/
├── ISO-22301/                    # Основной проект (текущая ветка)
│   └── core/odoo-18.0/addons/    # 29 модулей
└── golden-pr-26-modules/         # Экспорт golden-pr
    └── core/odoo-18.0/addons/    # 26 консолидированных модулей
```

---

**Создано**: 2025-09-28
**Метод экспорта**: `git archive` без переключения веток