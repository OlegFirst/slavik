# 🏗️ КАТЕГОРИЗАЦИЯ ODOO МОДУЛЕЙ ДЛЯ РЕОРГАНИЗАЦИИ

## 📊 АНАЛИЗ СУЩЕСТВУЮЩИХ МОДУЛЕЙ:

### 1️⃣ ОРИГИНАЛЬНЫЕ ODOO МОДУЛИ (НЕ ТРОГАЕМ):
```
addons26/base/                  # Базовый Odoo
addons26/mail/                  # Почта Odoo
addons26/web/                   # Веб Odoo
addons26/portal/                # Портал Odoo
addons26/auth_*/                # Аутентификация Odoo
addons26/calendar/              # Календарь Odoo
addons26/contacts/              # Контакты Odoo
addons26/website/               # Сайт Odoo
...все стандартные Odoo модули
```
**РЕШЕНИЕ:** Оставляем как есть - это инфраструктура Odoo

### 2️⃣ НАШИ BCM МОДУЛИ (ПЕРЕНОСИМ В MODULE_LIBRARY):

#### 🏢 CORE/BASE МОДУЛИ → DOMAIN_REGISTRY:
```
bcm_core/                       # Ядро BCM → DOMAIN_REGISTRY/bcm/
bcm_base/                       # Базовые настройки → DOMAIN_REGISTRY/bcm/
bcm_config/                     # Конфигурация → DOMAIN_REGISTRY/bcm/
bcm_context/                    # Контекст → DOMAIN_REGISTRY/bcm/
```

#### 📋 ФУНКЦИОНАЛЬНЫЕ МОДУЛИ → MODULE_LIBRARY:
```
bcm_bia/                        → MODULE_LIBRARY/business-impact-analysis/
bcm_incident/                   → MODULE_LIBRARY/incident-management/
bcm_incident_management/        → MODULE_LIBRARY/incident-management/
bcm_exercise/                   → MODULE_LIBRARY/exercise-testing/
bcm_plans/                      → MODULE_LIBRARY/continuity-planning/
bcm_templates/                  → MODULE_LIBRARY/continuity-planning/
bcm_audit/                      → MODULE_LIBRARY/compliance-audit/
bcm_governance/                 → MODULE_LIBRARY/compliance-audit/
bcm_reporting/                  → MODULE_LIBRARY/reporting-analytics/
bcm_kpi/                        → MODULE_LIBRARY/reporting-analytics/
bcm_risk_management/            → MODULE_LIBRARY/risk-assessment/
bcm_training/                   → MODULE_LIBRARY/training-education/
```

#### 🤖 AI/ИНТЕЛЛЕКТУАЛЬНЫЕ МОДУЛИ:
```
bcm_ai_consultant/              → MODULE_LIBRARY/ai-advisor/
bcm_ai_control/                 → BRIDGE_LAYER/ai-control-bridge/
bcm_ai_twin_orchestrator/       → MODULE_LIBRARY/digital-twin/
bcm_intelligent_base/           → MODULE_LIBRARY/ai-analytics/
```

#### 🔗 DIGITAL TWIN МОДУЛИ:
```
bcm_digital_twin_core/          → MODULE_LIBRARY/digital-twin/
bcm_corporate_twin/             → MODULE_LIBRARY/digital-twin/
bcm_digital_copy_manager/       → MODULE_LIBRARY/digital-twin/
```

#### 👥 ПОЛЬЗОВАТЕЛЬСКИЕ МОДУЛИ → USER_CONTEXT:
```
bcm_clients/                    → USER_CONTEXT/client-management/
bcm_community/                  → USER_CONTEXT/community-portal/
bcm_web_portal/                 → USER_CONTEXT/web-interfaces/
bcm_portal/                     → USER_CONTEXT/portal-interfaces/
```

### 3️⃣ ИНТЕГРАЦИОННЫЕ МОДУЛИ → INTEGRATION_LAYER:

#### 🌉 МОСТЫ И АДАПТЕРЫ:
```
bcm_ai_bridge/                  → BRIDGE_LAYER/ai-integration/
bcm_microservices_bridge/       → BRIDGE_LAYER/microservices-bridge/
crm_bridge/                     → INTEGRATION_LAYER/external/crm/
bcm_content_training_bridge/    → INTEGRATION_LAYER/training/
```

#### 🔌 ВНЕШНИЕ ИНТЕГРАЦИИ:
```
thehive/                        → INTEGRATION_LAYER/external/thehive/
moodle/                         → INTEGRATION_LAYER/external/moodle/
integrations/                   → INTEGRATION_LAYER/external/
adapters/                       → INTEGRATION_LAYER/adapters/
```

### 4️⃣ STANDALONE СЕРВИСЫ (НЕ ODOO):

#### 🧮 ДВИЖКИ И ПРОЦЕССОРЫ:
```
bia_engine/                     → MODULE_LIBRARY/business-impact-analysis/
digital-twin-engine/            → MODULE_LIBRARY/digital-twin/
digital-twin-platform/         → MODULE_LIBRARY/digital-twin/
document_processor/             → MODULE_LIBRARY/document-processing/
compliance_checker/             → MODULE_LIBRARY/compliance-audit/
```

#### 🎯 СИМУЛЯТОРЫ:
```
exercise_simulators/            → MODULE_LIBRARY/exercise-testing/
```

## 🔄 СТРАТЕГИЯ ПЕРЕМЕЩЕНИЯ:

### ЭТАП 1: ПОДГОТОВКА
```bash
# 1. Создаем новую структуру папок
mkdir -p PROGRAM_COMPONENTS_RESTRUCTURED/{DOMAIN_REGISTRY,MODULE_LIBRARY,INTEGRATION_LAYER,USER_CONTEXT,BUSINESS_PROCESSES}

# 2. Анализируем зависимости между модулями
find addons26/bcm_* -name "__manifest__.py" -exec grep -l "depends.*bcm" {} \;
```

### ЭТАП 2: СОХРАНЕНИЕ ODOO СОВМЕСТИМОСТИ
```python
# Создаем адаптеры для Odoo модулей:
class OdooModuleAdapter:
    """Адаптер для запуска наших модулей в Odoo"""

    def __init__(self, module_path, new_location):
        self.odoo_module = module_path
        self.new_module = new_location

    def create_bridge(self):
        # Создаем мост между старым Odoo модулем и новым расположением
        # Сохраняем API совместимость
        pass
```

### ЭТАП 3: ПОСТЕПЕННАЯ МИГРАЦИЯ
1. **Копируем** модули в новую структуру (не перемещаем!)
2. **Создаем адаптеры** для обратной совместимости
3. **Тестируем** работу в новой структуре
4. **Переключаем** импорты постепенно
5. **Удаляем** старые только после полного тестирования

## 📋 ДЕТАЛЬНЫЙ ПЛАН ПО МОДУЛЯМ:

### 🏢 DOMAIN_REGISTRY/bcm/
```yaml
domain_configuration:
  core_modules:
    - source: "addons26/bcm_core/"
      target: "DOMAIN_REGISTRY/bcm/core/"
      type: "domain_foundation"

    - source: "addons26/bcm_base/"
      target: "DOMAIN_REGISTRY/bcm/base/"
      type: "base_configuration"

    - source: "addons26/bcm_context/"
      target: "DOMAIN_REGISTRY/bcm/context/"
      type: "organizational_context"

  capabilities_defined:
    - risk_management
    - business_impact_analysis
    - incident_management
    - continuity_planning
    - exercise_testing
    - compliance_audit
```

### 📚 MODULE_LIBRARY/ (Пассивные модули)
```yaml
passive_modules:
  business_impact_analysis:
    odoo_sources:
      - "addons26/bcm_bia/"
    standalone_sources:
      - "bia_engine/"
    integration: "odoo_adapter"

  incident_management:
    odoo_sources:
      - "addons26/bcm_incident/"
      - "addons26/bcm_incident_management/"
    external_integrations:
      - "thehive/" # TheHive для инцидентов

  digital_twin:
    odoo_sources:
      - "addons26/bcm_digital_twin_core/"
      - "addons26/bcm_corporate_twin/"
    standalone_sources:
      - "digital-twin-engine/"
      - "digital-twin-platform/"
    ai_integration: true
```

### 🔌 INTEGRATION_LAYER/
```yaml
integrations:
  platform_adapters:
    odoo_adapter:
      purpose: "Подключение Odoo модулей к системе"
      handles: ["bcm_*", "custom_models", "odoo_api"]

    standalone_adapter:
      purpose: "Подключение standalone сервисов"
      handles: ["engines", "processors", "external_apis"]

  external_services:
    thehive_connector: "integrations/thehive/"
    moodle_connector: "integrations/moodle/"
    custom_apis: "integrations/custom/"
```

### 👥 USER_CONTEXT/
```yaml
user_experience:
  client_management:
    source: "addons26/bcm_clients/"
    purpose: "Управление клиентами BCM"

  community_portal:
    source: "addons26/bcm_community/"
    purpose: "Сообщество пользователей"

  web_interfaces:
    sources:
      - "addons26/bcm_web_portal/"
      - "addons26/bcm_portal/"
    purpose: "Веб-интерфейсы пользователей"
```

## 🎯 КОНЕЧНАЯ АРХИТЕКТУРА:

```
PROGRAM_COMPONENTS_RESTRUCTURED/
│
├── DOMAIN_REGISTRY/
│   └── bcm/                    # BCM domain config (из bcm_core, bcm_base)
│
├── MODULE_LIBRARY/             # Пассивные модули
│   ├── business-impact-analysis/    # bcm_bia + bia_engine
│   ├── incident-management/         # bcm_incident + thehive integration
│   ├── digital-twin/               # все digital twin модули
│   ├── ai-advisor/                 # bcm_ai_consultant
│   └── ... (другие функциональные модули)
│
├── INTEGRATION_LAYER/
│   ├── platform-adapters/
│   │   ├── odoo-adapter/           # Мост к Odoo модулям
│   │   └── standalone-adapter/     # Мост к standalone сервисам
│   └── external/                   # Внешние интеграции
│
├── USER_CONTEXT/
│   ├── client-management/          # bcm_clients
│   ├── community-portal/           # bcm_community
│   └── web-interfaces/             # порталы
│
└── BUSINESS_PROCESSES/
    └── bcm-iso22301/              # BCM процессы
```

## ✅ ПРЕИМУЩЕСТВА ТАКОЙ РЕОРГАНИЗАЦИИ:

1. **Сохраняем Odoo** - модули остаются работать в Odoo
2. **Добавляем универсальность** - через адаптеры
3. **Легкая миграция** - постепенно, без поломок
4. **Масштабируемость** - легко добавлять новые домены
5. **Тестируемость** - каждый слой независим

**Главное: НЕ ЛОМАЕМ СУЩЕСТВУЮЩУЮ ФУНКЦИОНАЛЬНОСТЬ!**