# 🗺️ КАРТА РЕОРГАНИЗАЦИИ PROGRAM_COMPONENTS

## 📊 АНАЛИЗ СУЩЕСТВУЮЩИХ КОМПОНЕНТОВ:

### BCM МОДУЛИ (30+ штук):
```
addons26/bcm_* → Odoo модули для BCM
```

### ИНТЕГРАЦИОННЫЕ КОМПОНЕНТЫ:
```
integrations/ → Внешние интеграции
adapters/ → Адаптеры
bridges/ → Мосты
```

### ПОЛЬЗОВАТЕЛЬСКИЕ КОМПОНЕНТЫ:
```
portal/ → Порталы пользователей
*client* → Клиентские компоненты
*user* → Пользовательские компоненты
```

### СИМУЛЯТОРЫ И ИНЖЕНЕРНЫЕ КОМПОНЕНТЫ:
```
exercise_simulators/ → Симуляторы упражнений
digital-twin-* → Digital Twin платформы
bia_engine/ → Движок BIA
```

## 🎯 ПЛАН РЕОРГАНИЗАЦИИ:

### 1. DOMAIN_REGISTRY/bcm/
**ПЕРЕМЕСТИТЬ:**
- `bcm_base` → Базовая конфигурация домена
- `bcm_config` → Конфигурация домена
- `bcm_context` → Контекст домена

### 2. MODULE_LIBRARY/
**ПЕРЕМЕСТИТЬ ПО ФУНКЦИЯМ:**

#### risk-assessment/
- `bcm_risk_management/` (если есть)
- Логика оценки рисков из других модулей

#### business-impact-analysis/
- `bcm_bia/` → Анализ влияния на бизнес
- `bia_engine/` → Движок BIA

#### incident-management/
- `bcm_incident/` → Управление инцидентами
- `bcm_incident_management/` → Расширенное управление

#### exercise-testing/
- `bcm_exercise/` → Учения и тестирования
- `exercise_simulators/` → Симуляторы

#### compliance-audit/
- `bcm_audit/` → Аудит и соответствие
- `bcm_governance/` → Управление

#### continuity-planning/
- `bcm_plans/` → Планы непрерывности
- `bcm_templates/` → Шаблоны планов

#### reporting-analytics/
- `bcm_reporting/` → Отчетность
- `bcm_kpi/` → KPI и метрики

#### digital-twin/
- `bcm_digital_twin_core/` → Ядро цифрового двойника
- `bcm_corporate_twin/` → Корпоративный двойник
- `digital-twin-platform/` → Платформа
- `digital-twin-engine/` → Движок

### 3. INTEGRATION_LAYER/
**ПЕРЕМЕСТИТЬ:**

#### external/
- `integrations/` → Внешние интеграции
- `thehive/` → TheHive интеграция
- `moodle/` → Moodle интеграция

#### platform-adapters/
- `adapters/` → Различные адаптеры
- `bridges/` → Мосты между системами
- `bcm_ai_bridge/` → AI мост

#### data-connectors/
- `crm_bridge/` → CRM интеграция
- `document_*` → Документооборот

### 4. USER_CONTEXT/
**ПЕРЕМЕСТИТЬ:**

#### user-profiles/
- Компоненты `*user*`
- Пользовательские настройки

#### client-management/
- `bcm_clients/` → Управление клиентами
- Компоненты `*client*`

#### portal-interfaces/
- `portal/` → Портальные компоненты
- `bcm_web_portal/` → BCM веб-портал
- `bcm_community/` → Сообщество

#### personalization/
- Пользовательские предпочтения
- Адаптивные интерфейсы

### 5. BUSINESS_PROCESSES/
**ПЕРЕМЕСТИТЬ:**

#### templates/
- `bcm_templates/` → Шаблоны процессов
- BPMN файлы из различных модулей

#### domain-specific/bcm/
- BCM-специфичные процессы
- ISO 22301 workflow

## 🔄 АЛГОРИТМ ПЕРЕМЕЩЕНИЯ:

### Этап 1: Анализ зависимостей
```bash
# Для каждого компонента анализируем:
- Зависимости от других модулей
- Используемые API
- Данные которые обрабатывает
- Пользовательские интерфейсы
```

### Этап 2: Категоризация
```bash
# Определяем тип компонента:
- Domain Configuration (DOMAIN_REGISTRY)
- Passive Module (MODULE_LIBRARY)
- Integration/Adapter (INTEGRATION_LAYER)
- User Interface (USER_CONTEXT)
- Business Process (BUSINESS_PROCESSES)
```

### Этап 3: Перемещение
```bash
# Сохраняем структуру но меняем логическую организацию:
- Создаем символические ссылки
- Обновляем импорты
- Тестируем работоспособность
```

## 📋 ПРИОРИТЕТЫ ПЕРЕМЕЩЕНИЯ:

### 🔥 КРИТИЧНЫЕ (делаем первыми):
1. `bcm_base`, `bcm_config` → DOMAIN_REGISTRY
2. `bcm_bia` → MODULE_LIBRARY/business-impact-analysis
3. `bcm_incident` → MODULE_LIBRARY/incident-management
4. `bcm_clients`, `portal` → USER_CONTEXT

### ⚠️ ВАЖНЫЕ (делаем вторыми):
1. `bcm_digital_twin_*` → MODULE_LIBRARY/digital-twin
2. `integrations` → INTEGRATION_LAYER
3. `exercise_simulators` → MODULE_LIBRARY/exercise-testing

### 📝 ОБЫЧНЫЕ (делаем последними):
1. `bcm_reporting` → MODULE_LIBRARY/reporting-analytics
2. `bcm_templates` → BUSINESS_PROCESSES
3. Остальные bcm_* модули

## 🧪 ТЕСТИРОВАНИЕ ПОСЛЕ ПЕРЕМЕЩЕНИЯ:

### Проверяем:
- [ ] Все импорты работают
- [ ] API endpoints доступны
- [ ] Зависимости разрешены
- [ ] Пользовательские интерфейсы загружаются
- [ ] Данные корректно обрабатываются

### Обновляем:
- [ ] Конфигурационные файлы
- [ ] Документацию
- [ ] Тесты
- [ ] Docker конфигурации

---

## 📈 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ:

После реорганизации получим:
- ✅ Четкое разделение по функциям
- ✅ Переиспользуемые модули
- ✅ Универсальную архитектуру
- ✅ Легкую масштабируемость

**БЕЗ ПОЛОМКИ СУЩЕСТВУЮЩЕЙ ФУНКЦИОНАЛЬНОСТИ!**