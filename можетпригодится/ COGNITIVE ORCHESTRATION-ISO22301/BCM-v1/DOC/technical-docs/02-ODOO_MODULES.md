# 📦 Odoo BCM Модули - Техническая документация

**Всего модулей**: 29 директорий (28 с манифестами)
**Версия Odoo**: 18.0 Community Edition
**Расположение**: `/core/odoo-18.0/addons/`

---

## 📋 Полный список модулей (29)

### ✅ Функциональные модули (28)

1. **bcm_admin_website** - Административный веб-сайт
2. **bcm_ai_consultant** - AI консультант для BCM
3. **bcm_ai_control** - AI Control Center (управление 10 AI органами)
4. **bcm_ai_twin_orchestrator** - Оркестратор AI цифровых двойников
5. **bcm_audit** - Аудит и соответствие
6. **bcm_base** - Базовый модуль с AI Foundation
7. **bcm_bia** - Business Impact Analysis (1073 строки кода)
8. **bcm_clients** - Управление клиентами
9. **bcm_community** - Community & Knowledge Hub
10. **bcm_config** - Конфигурация системы
11. **bcm_context** - Контекст организации
12. **bcm_core** - Core модуль BCM
13. **bcm_corporate_twin** - Корпоративный цифровой двойник
14. **bcm_digital_copy_manager** - Управление цифровыми копиями
15. **bcm_digital_twin_core** - Ядро Digital Twin
16. **bcm_exercise** - Учения и тренировки (345 строк)
17. **bcm_governance** - Управление и комплаенс (1698 строк)
18. **bcm_incident** - Управление инцидентами (349 строк)
19. **bcm_incident_management** - Расширенное управление инцидентами
20. **bcm_intelligent_base** - Интеллектуальная база знаний
21. **bcm_kpi** - KPI и метрики
22. **bcm_plans** - Планы непрерывности бизнеса
23. **bcm_portal** - Клиентский портал
24. **bcm_reporting** - Отчётность
25. **bcm_risk_management** - Управление рисками (712 строк)
26. **bcm_scenario_hub** - Центр управления сценариями
27. **bcm_templates** - Шаблоны документов
28. **bcm_training** - Обучение персонала

### ❌ Незавершённые модули (1)

29. **bcm_web_portal** - Пустая директория (только структура папок)
    - Есть папки `views/` и `website/`, но они пустые
    - Нет `__manifest__.py`
    - **Полная версия существует на ветке `golden-pr-iso22301`**

---

## 🔑 Ключевые модули

### 1. bcm_base - AI Foundation
**Версия**: 18.0.1.0.0
**Размер**: 461 строка кода
**Зависимости**: base, web, mail

**Функциональность**:
- Базовые классы для всех модулей
- AI Orchestrator интеграция
- Document Processor интеграция
- Compliance Checker интеграция
- REST API для внешних сервисов
- Централизованное логирование

**Ключевые файлы**:
- `models/bcm_ai_service.py` - AI сервисы
- `models/eventbus_integration.py` - EventBus интеграция

---

### 2. bcm_bia - Business Impact Analysis
**Версия**: 18.0.1.0.0
**Размер**: 1073 строки кода
**Зависимости**: bcm_base

**Функциональность**:
- Анализ бизнес-процессов
- Расчёт RTO/RPO
- AI Impact Oracle
- Dependency Graph
- Каскадные риски
- Финансовый анализ

**Модели**:
```python
class BCMBusinessProcess(models.Model):
    # Основные параметры
    annual_revenue_impact = fields.Float()
    staff_count = fields.Integer()

    # AI-оптимизированные параметры
    optimized_rto_hours = fields.Float(readonly=True)
    optimized_rpo_minutes = fields.Float(readonly=True)
    confidence_score = fields.Float(readonly=True)

    # Финансовые расчеты
    total_financial_impact_24h = fields.Float(readonly=True)
    cascade_risk_score = fields.Float(readonly=True)
```

**Ключевые файлы**:
- `models/models.py` (464 строки) - Основные модели
- `models/ai_impact_oracle.py` (208 строк) - AI оценка влияния
- `models/dependency_validator.py` - Валидация зависимостей
- `models/eventbus_integration.py` - EventBus события

---

### 3. bcm_governance - Управление и комплаенс
**Версия**: 18.0.2.0.0 (AI GOVERNANCE BRAIN UPDATE)
**Размер**: 1698 строк кода
**Зависимости**: base, web, mail, hr, bcm_context

**Функциональность**:
- 🧠 AI Governance Brain
- Управление политиками
- Gap-анализ соответствия ISO 22301
- Workflow согласования
- Регуляторная отчётность
- Executive dashboards

**Модели**:
```python
class BCMComplianceRequirement(models.Model):
    iso_clause = fields.Char()  # ISO 22301 clause
    requirement_text = fields.Text()
    compliance_status = fields.Selection([
        ('none', 'Not Implemented'),
        ('partial', 'Partially Compliant'),
        ('full', 'Fully Compliant')
    ])
```

**Ключевые файлы**:
- `models/models.py` (568 строк) - Основные модели
- `models/compliance_api_methods.py` - API методы
- `models/bcm_compliance_extension.py` - Расширения
- `models/policy_workflow.py` - Workflow политик

**ISO 22301 Mapping**:
- Requirements: 5.1, 5.2, 5.3 (Leadership)
- Gap analysis integration
- Compliance tracking

---

### 4. bcm_risk_management - Управление рисками
**Версия**: 18.0.1.0.0
**Размер**: 712 строк кода

**Функциональность**:
- Risk Assessment
- Risk Treatment
- AI Risk Advisor
- FAIR + Monte Carlo
- Risk scenarios

---

### 5. bcm_ai_control - AI Control Center
**Версия**: 18.0.1.0.0
**Размер**: 1289 строк кода

**Функциональность**:
- Управление 10 AI органами
- Мониторинг состояния AI
- Координация AI задач
- Anthropic Claude интеграция

**Ключевые файлы**:
- `models/ai_control_dashboard.py` - Dashboard
- `models/ai_organ_coordinator.py` - Координация
- `models/anthropic_integration.py` - Claude API

---

## 🔗 Зависимости модулей

### Граф зависимостей (упрощённый):

```
bcm_base (foundation)
    ↓
    ├─→ bcm_context
    │       ↓
    │       └─→ bcm_governance
    │
    ├─→ bcm_bia
    ├─→ bcm_risk_management
    ├─→ bcm_incident
    └─→ bcm_plans
```

### Критические зависимости:
- Все модули зависят от **bcm_base**
- **bcm_governance** зависит от **bcm_context**
- **Циклические зависимости были устранены** (см. комментарий в bcm_governance/__manifest__.py:57)

---

## 📊 Статистика кода

| Модуль | Строк кода | Моделей (.py) | Views (.xml) | Статус |
|--------|------------|---------------|--------------|--------|
| bcm_governance | 1698 | 6 | 4 | ✅ Полный |
| bcm_ai_control | 1289 | 3 | 2 | ✅ Полный |
| bcm_bia | 1073 | 6 | 1 | ✅ Полный |
| bcm_risk_management | 712 | 4 | 2 | ✅ Полный |
| bcm_base | 461 | 3 | 2 | ✅ Полный |
| bcm_incident | 349 | 2 | 1 | ✅ Полный |
| bcm_exercise | 345 | 2 | 1 | ✅ Полный |

**Общий объём**: ~8,000+ строк Python кода в ключевых модулях

---

## 🔄 EventBus Integration

Многие модули интегрированы с EventBus для real-time событий:

```python
# Пример из bcm_bia/models/eventbus_integration.py
class BIAEventBusIntegration:
    def publish_bia_completed(self, process_id, results):
        event = {
            'type': 'bia.analysis.completed',
            'process_id': process_id,
            'rto': results['optimized_rto'],
            'rpo': results['optimized_rpo'],
            'financial_impact': results['impact_24h']
        }
        self.eventbus_client.publish(event)
```

---

## 🎯 ISO 22301 Mapping

Модули покрывают следующие требования ISO 22301:2019:

| Требование | Модули | Статус |
|------------|--------|--------|
| 4.1-4.4 (Context) | bcm_context | ✅ Реализовано |
| 5.1-5.3 (Leadership) | bcm_governance | ✅ Реализовано |
| 6.1 (Risk Assessment) | bcm_risk_management | ✅ Реализовано |
| 8.1.3-8.1.4 (BIA) | bcm_bia | ✅ Реализовано |
| 8.2 (BC Strategy) | bcm_plans | ⚠️ Частично |
| 8.3 (BC Procedures) | bcm_incident | ⚠️ Частично |
| 8.4-8.5 (Exercises) | bcm_exercise | ⚠️ Частично |
| 9.2 (Audit) | bcm_audit | ⚠️ Частично |
| 10.1-10.2 (Improvement) | bcm_improvement | ❌ Не найден |

---

## 🚨 Проблемы и рекомендации

### Критические проблемы:
1. **bcm_web_portal** - пустой модуль (восстановить из golden-pr)
2. **Циклические зависимости** - требуют runtime integration через API
3. **Не все ISO требования покрыты** - ~50% соответствия

### Рекомендации:
1. Восстановить `bcm_web_portal` из ветки `golden-pr-iso22301`
2. Завершить модули `bcm_plans`, `bcm_incident`, `bcm_exercise`
3. Создать недостающие модули для полного ISO 22301 покрытия
4. Документировать все API endpoints
5. Добавить unit тесты для каждого модуля

---

## 📍 Дополнительная информация

### Сравнение с golden-pr-iso22301:
На ветке `golden-pr-iso22301` всего **26 модулей** против 29 на текущей:
- **bcm_web_portal** там полноценный
- **bcm_incident** единый (не разделён)
- Нет разделения на `bcm_portal` + `bcm_admin_website`

См. `/Users/MD/golden-pr-26-modules/` для сравнения.

---

**Последнее обновление**: 2025-09-28
**Версия документа**: 1.0