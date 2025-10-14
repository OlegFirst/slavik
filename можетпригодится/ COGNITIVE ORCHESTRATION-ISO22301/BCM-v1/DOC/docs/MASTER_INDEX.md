# 📚 BCM Platform - Master Documentation Index

> **🎯 НАЧНИ ОТСЮДА!** Навигация по всей документации проекта
>
> **Статус**: ✅ Актуальная и структурированная документация
> **Обновлено**: Январь 2025

---

## 🚀 Быстрый старт

### Для Frontend разработчиков:
1. 📖 [`frontend/clean/00_MASTER_INDEX.md`](frontend/clean/00_MASTER_INDEX.md) - Начни здесь
2. 🏗️ [`frontend/clean/01_ARCHITECTURE.md`](frontend/clean/01_ARCHITECTURE.md) - Архитектура
3. 🔌 [`frontend/clean/02_API_INTEGRATION.md`](frontend/clean/02_API_INTEGRATION.md) - API интеграция
4. 🎨 [`frontend/clean/03_UI_UX_GUIDE.md`](frontend/clean/03_UI_UX_GUIDE.md) - Design System

### Для Backend разработчиков:
1. 📋 [`modules/individual/`](modules/individual/) - Документация модулей
2. ⚙️ [`services/individual/`](services/individual/) - Документация сервисов
3. 💼 [`business_logic/`](business_logic/) - Бизнес-процессы

### Для Project Manager'ов:
1. 🗺️ [`frontend/clean/04_DEVELOPMENT_ROADMAP.md`](frontend/clean/04_DEVELOPMENT_ROADMAP.md) - План разработки
2. 💼 [`business_logic/USER_JOURNEYS.md`](business_logic/USER_JOURNEYS.md) - Пользовательские сценарии
3. 🔄 [`business_logic/WORKFLOWS.md`](business_logic/WORKFLOWS.md) - Бизнес-процессы

---

## 📂 Структура документации

### 🖥️ **Frontend Documentation** (Для команды фронтенда)
**Папка**: [`frontend/clean/`](frontend/clean/)

| Файл | Описание | Статус |
|------|----------|--------|
| [`00_MASTER_INDEX.md`](frontend/clean/00_MASTER_INDEX.md) | 🎯 Навигация для frontend команды | ✅ |
| [`01_ARCHITECTURE.md`](frontend/clean/01_ARCHITECTURE.md) | 🏗️ Техническая архитектура Vue.js | ✅ |
| [`02_API_INTEGRATION.md`](frontend/clean/02_API_INTEGRATION.md) | 🔌 API интеграция и примеры кода | ✅ |
| [`03_UI_UX_GUIDE.md`](frontend/clean/03_UI_UX_GUIDE.md) | 🎨 Design System и компоненты | ✅ |
| [`04_DEVELOPMENT_ROADMAP.md`](frontend/clean/04_DEVELOPMENT_ROADMAP.md) | 🗺️ План разработки по этапам | ✅ |
| [`05_BUSINESS_FLOWS.md`](frontend/clean/05_BUSINESS_FLOWS.md) | 💼 Бизнес-процессы в UI | ✅ |

---

### 📦 **Module Documentation** (Индивидуальные модули)
**Папка**: [`modules/individual/`](modules/individual/)

#### 🏗️ Foundation Modules
| Модуль | Описание | Статус |
|--------|----------|--------|
| [`bcm_core.md`](modules/individual/bcm_core.md) | Базовая платформа и мульти-тенантность | ✅ |
| [`bcm_base.md`](modules/individual/bcm_base.md) | Общие утилиты и компоненты | 🟡 |
| [`bcm_config.md`](modules/individual/bcm_config.md) | Конфигурация системы | 🟡 |
| [`bcm_clients.md`](modules/individual/bcm_clients.md) | Управление клиентами | 🟡 |

#### 💼 Business Core Modules
| Модуль | Описание | Статус |
|--------|----------|--------|
| [`bcm_risk_management.md`](modules/individual/bcm_risk_management.md) | Управление рисками + AI анализ | ✅ |
| [`bcm_bia.md`](modules/individual/bcm_bia.md) | Анализ воздействия + ML оптимизация | ✅ |
| [`bcm_governance.md`](modules/individual/bcm_governance.md) | Политики и управление | 🟡 |
| [`bcm_context.md`](modules/individual/bcm_context.md) | Организационный контекст | 🟡 |

#### 🚨 Operations Modules
| Модуль | Описание | Статус |
|--------|----------|--------|
| [`bcm_incident_management.md`](modules/individual/bcm_incident_management.md) | Продвинутое управление инцидентами | ✅ |
| [`bcm_incident.md`](modules/individual/bcm_incident.md) | Базовые инциденты | 🟡 |
| [`bcm_plans.md`](modules/individual/bcm_plans.md) | Планы непрерывности | 🟡 |
| [`bcm_audit.md`](modules/individual/bcm_audit.md) | Аудит и соответствие | 🟡 |
| [`bcm_training.md`](modules/individual/bcm_training.md) | Обучение и компетенции | 🟡 |

#### 📊 Analytics Modules
| Модуль | Описание | Статус |
|--------|----------|--------|
| [`bcm_reporting.md`](modules/individual/bcm_reporting.md) | Отчеты и аналитика | 🟡 |
| [`bcm_kpi.md`](modules/individual/bcm_kpi.md) | Метрики и KPI | 🟡 |

#### 🌐 User Interface Modules
| Модуль | Описание | Статус |
|--------|----------|--------|
| [`bcm_admin_website.md`](modules/individual/bcm_admin_website.md) | Административный портал | 🟡 |
| [`bcm_portal.md`](modules/individual/bcm_portal.md) | Клиентский портал | 🟡 |
| [`bcm_community.md`](modules/individual/bcm_community.md) | База знаний и форумы | 🟡 |
| [`bcm_templates.md`](modules/individual/bcm_templates.md) | Шаблоны документов | 🟡 |

#### 🤖 AI & Advanced Modules
| Модуль | Описание | Статус |
|--------|----------|--------|
| [`bcm_ai_control.md`](modules/individual/bcm_ai_control.md) | AI Control Center | 🟡 |
| [`bcm_scenario_hub.md`](modules/individual/bcm_scenario_hub.md) | AI генерация сценариев | 🟡 |
| [`bcm_intelligent_base.md`](modules/individual/bcm_intelligent_base.md) | AI интеграция | 🟡 |

---

### ⚙️ **Services Documentation** (Микросервисы)
**Папка**: [`services/individual/`](services/individual/)

#### 🤖 AI Services
| Сервис | Порт | Описание | Статус |
|--------|------|----------|--------|
| `ai_orchestrator.md` | 8000 | Центральный AI координатор | 🔵 |
| `ai_control_center.md` | 8200 | Digital BCM Organism | 🔵 |

#### 💼 Business Services
| Сервис | Порт | Описание | Статус |
|--------|------|----------|--------|
| `bia_engine.md` | 8082 | BIA анализ и оптимизация | 🔵 |
| `scenario_orchestrator.md` | 8085 | Управление сценариями | 🔵 |
| `compliance_checker.md` | 8084 | Проверка соответствия | 🔵 |
| `document_processor.md` | 8083 | Обработка документов | 🔵 |

#### 🔧 Infrastructure Services
| Сервис | Порт | Описание | Статус |
|--------|------|----------|--------|
| `auth_service.md` | 8005 | Аутентификация JWT | 🔵 |
| `eventbus.md` | 8001 | Обмен сообщениями | 🔵 |
| `notification_service.md` | 8004 | Уведомления | 🔵 |

#### 🔗 Adapter Services
| Сервис | Порт | Описание | Статус |
|--------|------|----------|--------|
| `grafana_adapter.md` | 8006 | Интеграция с Grafana | 🔵 |
| `thehive_adapter.md` | 8007 | Интеграция с TheHive | 🔵 |
| `lms_adapter.md` | 8008 | Интеграция с LMS | 🔵 |

---

### 💼 **Business Logic** (Бизнес-процессы)
**Папка**: [`business_logic/`](business_logic/)

| Файл | Описание | Статус |
|------|----------|--------|
| [`WORKFLOWS.md`](business_logic/WORKFLOWS.md) | Все бизнес-процессы модулей | ✅ |
| [`USER_JOURNEYS.md`](business_logic/USER_JOURNEYS.md) | Пользовательские сценарии | ✅ |
| [`PDCA_PROCESSES.md`](business_logic/PDCA_PROCESSES.md) | PDCA циклы | ✅ |
| [`INTEGRATION_FLOWS.md`](business_logic/INTEGRATION_FLOWS.md) | Интеграции между модулями | ✅ |
| [`BUSINESS_RULES.md`](business_logic/BUSINESS_RULES.md) | Бизнес-правила и ограничения | ✅ |

---

## 🎯 Статусы документации

| Статус | Значение | Описание |
|--------|----------|----------|
| ✅ | Готово | Полная, актуальная документация |
| 🟡 | В процессе | Базовая структура создана, нужно детализировать |
| 🔵 | Запланировано | Нужно создать с нуля |
| ❌ | Устарело | Перенесено в archive/ |

---

## 📋 Для разных ролей

### 👨‍💻 **Frontend Developer**
**Начни здесь**: [`frontend/clean/00_MASTER_INDEX.md`](frontend/clean/00_MASTER_INDEX.md)

**Ключевые файлы**:
1. Архитектура: [`frontend/clean/01_ARCHITECTURE.md`](frontend/clean/01_ARCHITECTURE.md)
2. API интеграция: [`frontend/clean/02_API_INTEGRATION.md`](frontend/clean/02_API_INTEGRATION.md)
3. UI компоненты: [`frontend/clean/03_UI_UX_GUIDE.md`](frontend/clean/03_UI_UX_GUIDE.md)
4. Бизнес-флоу: [`frontend/clean/05_BUSINESS_FLOWS.md`](frontend/clean/05_BUSINESS_FLOWS.md)

### 👨‍💼 **Project Manager**
**Начни здесь**: [`frontend/clean/04_DEVELOPMENT_ROADMAP.md`](frontend/clean/04_DEVELOPMENT_ROADMAP.md)

**Ключевые файлы**:
1. План разработки: [`frontend/clean/04_DEVELOPMENT_ROADMAP.md`](frontend/clean/04_DEVELOPMENT_ROADMAP.md)
2. Пользовательские сценарии: [`business_logic/USER_JOURNEYS.md`](business_logic/USER_JOURNEYS.md)
3. Бизнес-процессы: [`business_logic/WORKFLOWS.md`](business_logic/WORKFLOWS.md)

### 👨‍🔧 **Backend Developer**
**Начни здесь**: [`modules/individual/bcm_core.md`](modules/individual/bcm_core.md)

**Ключевые файлы**:
1. Модули: [`modules/individual/`](modules/individual/) (каждый модуль отдельно)
2. Сервисы: [`services/individual/`](services/individual/) (каждый сервис отдельно)
3. Интеграции: [`business_logic/INTEGRATION_FLOWS.md`](business_logic/INTEGRATION_FLOWS.md)

### 🎨 **UI/UX Designer**
**Начни здесь**: [`frontend/clean/03_UI_UX_GUIDE.md`](frontend/clean/03_UI_UX_GUIDE.md)

**Ключевые файлы**:
1. Design System: [`frontend/clean/03_UI_UX_GUIDE.md`](frontend/clean/03_UI_UX_GUIDE.md)
2. Пользовательские пути: [`business_logic/USER_JOURNEYS.md`](business_logic/USER_JOURNEYS.md)
3. Бизнес-флоу: [`frontend/clean/05_BUSINESS_FLOWS.md`](frontend/clean/05_BUSINESS_FLOWS.md)

### 🔍 **QA Engineer**
**Начни здесь**: [`business_logic/WORKFLOWS.md`](business_logic/WORKFLOWS.md)

**Ключевые файлы**:
1. Тестовые сценарии: [`business_logic/USER_JOURNEYS.md`](business_logic/USER_JOURNEYS.md)
2. Бизнес-правила: [`business_logic/BUSINESS_RULES.md`](business_logic/BUSINESS_RULES.md)
3. API документация: [`frontend/clean/02_API_INTEGRATION.md`](frontend/clean/02_API_INTEGRATION.md)

---

## 🔍 Поиск информации

### Ищешь информацию о конкретном модуле?
➡️ [`modules/individual/bcm_[module_name].md`](modules/individual/)

### Ищешь API документацию?
➡️ [`frontend/clean/02_API_INTEGRATION.md`](frontend/clean/02_API_INTEGRATION.md)

### Ищешь бизнес-процессы?
➡️ [`business_logic/WORKFLOWS.md`](business_logic/WORKFLOWS.md)

### Ищешь план разработки?
➡️ [`frontend/clean/04_DEVELOPMENT_ROADMAP.md`](frontend/clean/04_DEVELOPMENT_ROADMAP.md)

### Ищешь UI компоненты?
➡️ [`frontend/clean/03_UI_UX_GUIDE.md`](frontend/clean/03_UI_UX_GUIDE.md)

---

## 📞 Контакты и поддержка

### Документация
- **Ответственный**: Technical Writing Team
- **Обновления**: Еженедельно по понедельникам
- **Вопросы**: Создай issue в репозитории

### Техническая поддержка
- **Frontend**: frontend-team@bcm-platform.com
- **Backend**: backend-team@bcm-platform.com
- **DevOps**: devops-team@bcm-platform.com

---

## 📝 Как использовать эту документацию

### 1. **Определи свою роль** и найди соответствующий раздел выше
### 2. **Начни с рекомендованного файла** для своей роли
### 3. **Используй поиск** (Ctrl/Cmd + F) для быстрого нахождения информации
### 4. **Следуй ссылкам** между документами для углубленного изучения
### 5. **Проверяй статусы** документов - используй только актуальные (✅)

---

## 🔄 История изменений

| Дата | Изменения | Автор |
|------|-----------|-------|
| 2025-01-16 | Создание новой структуры документации | AI Documentation Team |
| 2025-01-16 | Консолидация business logic документации | AI Documentation Team |
| 2025-01-16 | Создание чистой frontend документации | AI Documentation Team |
| 2025-01-16 | Создание индивидуальных файлов модулей | AI Documentation Team |

---

> **💡 Совет**: Добавь эту страницу в закладки! Она будет твоей отправной точкой для всей документации проекта.

**Последнее обновление**: Январь 2025
**Версия документации**: 2.0