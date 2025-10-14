# 📚 BCM Platform - Чистая структура документации

## 🎯 Проблема
Создалась каша из документов - непонятно где что искать и какие файлы актуальные.

## ✅ Решение: Четкая структура

### **Основные разделы:**

## 1. 📋 МАСТЕР-ИНДЕКС
**Файл**: `/docs/MASTER_INDEX.md`
- Главный навигатор по всей документации
- Ссылки на все ключевые файлы
- Статус каждого документа (актуальный/устаревший)

---

## 2. 🏗️ АРХИТЕКТУРА ПЛАТФОРМЫ
**Папка**: `/docs/architecture/`

### Ключевые файлы:
- **`PLATFORM_OVERVIEW.md`** - Общая архитектура (22 модуля + 16 сервисов)
- **`SERVICE_DEPENDENCIES.md`** - Карта зависимостей между сервисами
- **`MODULE_RELATIONSHIPS.md`** - Связи между BCM модулями
- **`INFRASTRUCTURE_MAP.md`** - PostgreSQL, Redis, Keycloak, etc.

---

## 3. 📦 МОДУЛИ (ИНДИВИДУАЛЬНО)
**Папка**: `/docs/modules/individual/`

### Каждый модуль = отдельный файл:
```
bcm_core.md                    # Foundation модуль
bcm_risk_management.md         # Risk + AI + FAIR + Monte Carlo
bcm_bia.md                     # Business Impact Analysis + ML
bcm_incident_management.md     # Incident handling + workflows
bcm_reporting.md               # Analytics + Grafana integration
bcm_audit.md                   # Compliance + ISO 22301
bcm_ai_control.md             # Digital BCM Organism + 10 AI organs
bcm_governance.md             # Policy management
bcm_plans.md                  # Business continuity planning
bcm_training.md               # Learning management
bcm_kpi.md                    # Performance metrics
bcm_portal.md                 # Client self-service
bcm_admin_website.md          # Admin management portal
bcm_community.md              # Knowledge base + forums
bcm_scenario_hub.md           # AI scenario generation
bcm_templates.md              # Document templates + BPMN
bcm_clients.md                # Multi-tenant management
bcm_context.md                # Organizational structure
bcm_base.md                   # Base functionality
bcm_config.md                 # Configuration management
bcm_intelligent_base.md       # AI integration base
bcm_incident.md               # Basic incident model
```

### Структура каждого файла модуля:
```markdown
# bcm_[module_name] - [Module Title]

## 📋 Обзор модуля
- Назначение и цели
- Ключевые функции
- Место в общей архитектуре

## 🏗️ Техническая архитектура
- Python модели и поля
- API endpoints
- Контроллеры и views
- JavaScript компоненты (если есть)

## 🔗 Зависимости
- Odoo модули (base, web, mail, etc.)
- Другие BCM модули
- Внешние сервисы
- Python пакеты

## 🎯 Бизнес-логика
- Основные workflow
- Правила валидации
- Алгоритмы и расчеты
- AI интеграции

## 🔌 API спецификация
- REST endpoints
- Request/response форматы
- Примеры вызовов
- WebSocket события (если есть)

## 💾 Модели данных
- Все поля с описанием
- Связи с другими моделями
- Computed поля
- Constraints и правила

## 🔐 Безопасность
- Группы пользователей
- Права доступа
- Record rules
- Multi-tenant изоляция

## 🎨 UI компоненты
- Views (forms, lists, kanban)
- Menu структура
- Специальные виджеты
- CSS стили (если есть)

## 🧪 Тестирование
- Ключевые сценарии
- Тестовые данные
- Integration points
- Известные ограничения

## 📊 Примеры использования
- Типичные user flows
- Код примеры
- Скриншоты/mockups (если есть)
```

---

## 4. 💼 БИЗНЕС-ЛОГИКА
**Папка**: `/docs/business_logic/`

### Файлы:
- **`WORKFLOWS.md`** - Детальные workflow каждого модуля
- **`USER_JOURNEYS.md`** - Пользовательские сценарии
- **`PDCA_PROCESSES.md`** - PDCA циклы и процессы
- **`INTEGRATION_FLOWS.md`** - Как модули взаимодействуют
- **`BUSINESS_RULES.md`** - Бизнес-правила и ограничения

---

## 5. 🖥️ FRONTEND ДОКУМЕНТАЦИЯ
**Папка**: `/docs/frontend/`

### Структурированные файлы:
- **`00_MASTER_INDEX.md`** - Навигатор для frontend команды
- **`01_ARCHITECTURE.md`** - Frontend архитектура
- **`02_API_INTEGRATION.md`** - Примеры кода Vue.js + API
- **`03_UI_UX_GUIDE.md`** - Design system и компоненты
- **`04_DEVELOPMENT_ROADMAP.md`** - План разработки по этапам
- **`05_BUSINESS_FLOWS.md`** - Как бизнес-процессы влияют на UI
- **`06_TESTING_STRATEGY.md`** - Тестирование frontend

---

## 6. ⚙️ СЕРВИСЫ
**Папка**: `/docs/services/`

### Каждый сервис = отдельный файл:
```
ai_orchestrator.md            # AI Orchestrator (порт 8000)
eventbus.md                   # EventBus (порт 8001)
auth_service.md               # Auth Service (порт 8005)
bia_engine.md                 # BIA Engine (порт 8082)
scenario_orchestrator.md     # Scenario Orchestrator (порт 8085)
compliance_checker.md        # Compliance Checker (порт 8084)
document_processor.md        # Document Processor (порт 8083)
notification_service.md      # Notification Service (порт 8004)
grafana_adapter.md           # Grafana Adapter (порт 8006)
thehive_adapter.md           # TheHive Adapter (порт 8007)
lms_adapter.md               # LMS Adapter (порт 8008)
bpmn_service.md              # BPMN Service
ai_control_center.md         # AI Control Center (порт 8200)
```

---

## 7. 🔧 РУКОВОДСТВА
**Папка**: `/docs/guides/`

### Практические руководства:
- **`DEVELOPMENT_SETUP.md`** - Настройка среды разработки
- **`DEPLOYMENT_GUIDE.md`** - Деплой в production
- **`TROUBLESHOOTING.md`** - Решение типичных проблем
- **`BEST_PRACTICES.md`** - Лучшие практики разработки

---

## 📁 Итоговая структура:

```
docs/
├── MASTER_INDEX.md                    # 🎯 НАЧНИ ОТСЮДА
│
├── architecture/                      # 🏗️ Общая архитектура
│   ├── PLATFORM_OVERVIEW.md
│   ├── SERVICE_DEPENDENCIES.md
│   ├── MODULE_RELATIONSHIPS.md
│   └── INFRASTRUCTURE_MAP.md
│
├── modules/individual/                # 📦 Каждый модуль отдельно
│   ├── bcm_core.md
│   ├── bcm_risk_management.md
│   ├── bcm_bia.md
│   ├── bcm_incident_management.md
│   ├── ... (все 22 модуля)
│   └── bcm_ai_control.md
│
├── services/                         # ⚙️ Каждый сервис отдельно
│   ├── ai_orchestrator.md
│   ├── eventbus.md
│   ├── auth_service.md
│   └── ... (все 16 сервисов)
│
├── business_logic/                   # 💼 Бизнес-процессы
│   ├── WORKFLOWS.md
│   ├── USER_JOURNEYS.md
│   ├── PDCA_PROCESSES.md
│   └── INTEGRATION_FLOWS.md
│
├── frontend/                         # 🖥️ Для frontend команды
│   ├── 00_MASTER_INDEX.md
│   ├── 01_ARCHITECTURE.md
│   ├── 02_API_INTEGRATION.md
│   ├── 03_UI_UX_GUIDE.md
│   ├── 04_DEVELOPMENT_ROADMAP.md
│   └── 05_BUSINESS_FLOWS.md
│
├── guides/                          # 🔧 Практические руководства
│   ├── DEVELOPMENT_SETUP.md
│   ├── DEPLOYMENT_GUIDE.md
│   └── TROUBLESHOOTING.md
│
└── archive/                         # 📦 Устаревшие документы
    └── ... (все старые файлы)
```

---

## 🎯 Принципы новой структуры:

### ✅ Один файл = одна тема
- Каждый модуль в отдельном файле
- Каждый сервис в отдельном файле
- Четкая тематическая группировка

### ✅ Иерархическая навигация
- MASTER_INDEX.md как главная точка входа
- Каждая папка с собственным README
- Четкие ссылки между документами

### ✅ Статус документов
- Актуальные в основных папках
- Устаревшие в /archive/
- Метки статуса в каждом файле

### ✅ Удобство поиска
- Понятные имена файлов
- Консистентная структура
- Теги и категории

---

## 🚀 Следующие шаги:

1. **Создать новую структуру папок**
2. **Переместить актуальные файлы**
3. **Создать индивидуальные файлы модулей**
4. **Написать MASTER_INDEX.md**
5. **Переместить устаревшее в archive/**
6. **Обновить все ссылки**

---

> **Результат**: Четкая, логичная структура где каждый может быстро найти нужную информацию без хаоса и дублирования.