# Диаграммы платформы AI-Platform-ISO

**Дата создания**: 2025-10-09
**Версия платформы**: 2.0.0
**Всего диаграмм**: 36 Mermaid диаграмм

---

## 📊 Содержание

Все диаграммы извлечены из документации и организованы по категориям для удобного использования.

### 📁 Категории

1. [**Architecture**](#architecture) (24 диаграммы)
2. [**User Scenarios**](#user-scenarios) (4 диаграммы) 🆕
3. [**Dependencies**](#dependencies) (1 диаграмма) 🆕
4. [**Flows**](#flows) (3 диаграммы) 🆕
5. [**Integration**](#integration) (4 диаграммы)
6. [**Business Processes**](#business-processes) (1 диаграмма)

---

## Architecture

**Папка**: `architecture/`
**Количество**: 24 диаграммы (23 из ARCHITECTURE_VISUALIZATIONS + 1 platform-architecture)

### Диаграммы системной архитектуры

Файл `platform-architecture.mmd` - основная архитектурная диаграмма платформы.

Файлы из `ARCHITECTURE_VISUALIZATIONS.md`:

| # | Файл | Описание |
|---|------|----------|
| 01 | `ARCHITECTURE_VISUALIZATIONS_01.mmd` | High-Level System Overview - Полная схема системы с 4 слоями |
| 02 | `ARCHITECTURE_VISUALIZATIONS_02.mmd` | Four-Layer Architecture - Архитектура по слоям |
| 03 | `ARCHITECTURE_VISUALIZATIONS_03.mmd` | Platform Services Layer - Слой платформенных сервисов (12 сервисов) |
| 04 | `ARCHITECTURE_VISUALIZATIONS_04.mmd` | Service Dependency Graph - Граф зависимостей сервисов |
| 05 | `ARCHITECTURE_VISUALIZATIONS_05.mmd` | Reverse Dependency View - Обратные зависимости (Who Uses What) |
| 06 | `ARCHITECTURE_VISUALIZATIONS_06.mmd` | Complete Workflow Execution Flow - Полный поток выполнения workflow |
| 07 | `ARCHITECTURE_VISUALIZATIONS_07.mmd` | AI-Powered Analysis Flow - Поток AI-анализа |
| 08 | `ARCHITECTURE_VISUALIZATIONS_08.mmd` | Predictive Intelligence Flow - Поток предиктивного анализа |
| 09 | `ARCHITECTURE_VISUALIZATIONS_09.mmd` | Collective Intelligence Flow - Поток коллективного интеллекта |
| 10 | `ARCHITECTURE_VISUALIZATIONS_10.mmd` | EventBus Topology - Топология шины событий (Redis Streams + RabbitMQ) |
| 11 | `ARCHITECTURE_VISUALIZATIONS_11.mmd` | Event Flow Patterns - Паттерны событийных потоков |
| 12 | `ARCHITECTURE_VISUALIZATIONS_12.mmd` | Database Schema Organization - Организация схемы БД |
| 13 | `ARCHITECTURE_VISUALIZATIONS_13.mmd` | Database Connections Map - Карта подключений к БД |
| 14 | `ARCHITECTURE_VISUALIZATIONS_14.mmd` | API Gateway to Services - API Gateway → Сервисы |
| 15 | `ARCHITECTURE_VISUALIZATIONS_15.mmd` | Inter-Service Communication - Межсервисное взаимодействие |
| 16 | `ARCHITECTURE_VISUALIZATIONS_16.mmd` | API Endpoint Summary - Сводка API endpoints (150+ endpoints) |
| 17 | `ARCHITECTURE_VISUALIZATIONS_17.mmd` | Docker Compose Local Development - Локальная разработка |
| 18 | `ARCHITECTURE_VISUALIZATIONS_18.mmd` | Kubernetes Production Deployment - Production развертывание |
| 19 | `ARCHITECTURE_VISUALIZATIONS_19.mmd` | Complete Infrastructure Stack - Полный инфраструктурный стек |
| 20 | `ARCHITECTURE_VISUALIZATIONS_20.mmd` | Infrastructure Ports Map - Карта портов инфраструктуры |
| 21 | `ARCHITECTURE_VISUALIZATIONS_21.mmd` | Event Intelligence Auto-Discovery - Автообнаружение событий |
| 22 | `ARCHITECTURE_VISUALIZATIONS_22.mmd` | Stuck Organization Recovery Flow - Поток восстановления застрявших организаций |
| 23 | `ARCHITECTURE_VISUALIZATIONS_23.mmd` | Proactive Prediction Flow - Поток проактивных предсказаний |

### Ключевые компоненты на диаграммах

- **4 Слоя**: Infrastructure, Intelligent Core (11 модулей), Platform Services (12 сервисов), Integration
- **23 Сервиса**: С распределением по портам 8000-8070
- **EventBus**: Redis Streams + RabbitMQ
- **Базы данных**: PostgreSQL, Redis, Qdrant (векторная БД)
- **API Gateway**: 150+ endpoints
- **AI Foundation**: LLM routing, RAG, ML models

---

## User Scenarios

**Папка**: `user-scenarios/`
**Количество**: 4 диаграммы 🆕

| # | Файл | Тип | Описание |
|---|------|-----|----------|
| 1 | `BCM_USER_JOURNEY.mmd` | Flowchart | Полный пользовательский путь: BIA → Risk → Plan → Exercise |
| 2 | `BIA_DETAILED_WORKFLOW.mmd` | Sequence | Детальный workflow BIA с AI анализом (6 шагов) |
| 3 | `ADMIN_SERVICE_MONITORING.mmd` | Graph | Администраторская панель: мониторинг 23 сервисов + инфраструктура |
| 4 | `RISK_ASSESSMENT_FLOW.mmd` | Flowchart | Процесс оценки рисков: от выявления до регистрации (3 источника, AI анализ) |

### Ключевые сценарии

**BCM User Journey**:
- 4 основных потока: BIA, Risk Assessment, BC Planning, Exercise
- AI рекомендации на каждом этапе
- Интеграция с EventBus для уведомлений

**BIA Workflow**:
- 6-шаговый мастер
- AI анализ критических функций
- Автоматическое построение графа зависимостей
- Валидация RTO/RPO целей

**Admin Monitoring**:
- Мониторинг всех 23 сервисов
- Health checks в реальном времени
- Управление инфраструктурой (PostgreSQL, Redis, RabbitMQ, Qdrant)
- Интеграция с Prometheus/Grafana

**Risk Assessment**:
- 3 источника рисков: Manual, AI-discovered, BIA-derived
- Матрица рисков 5×5 (Impact × Likelihood)
- AI предложения по митигации
- Автоматическая нотификация стейкхолдеров

---

## Dependencies

**Папка**: `dependencies/`
**Количество**: 1 диаграмма 🆕

| # | Файл | Описание |
|---|------|----------|
| 1 | `SERVICE_DEPENDENCIES_DETAILED.mmd` | Детальный граф зависимостей всех сервисов |

### Граф зависимостей

**SERVICE_DEPENDENCIES_DETAILED**:
- **4 слоя**: API Layer, Platform Services, Intelligent Core, Infrastructure
- **11 Platform Services**: BIA, Risk, Compliance, Governance, Planning, Plans, Response, Documents, Validation, Learning, BCM Coord
- **6 Intelligent Core модулей**: AI Foundation, Workflow Intelligence, Expertise Center, Predictive, Collective, Event Intelligence
- **4 Infrastructure компонента**: PostgreSQL, Redis, RabbitMQ, Qdrant

**Ключевые зависимости**:
- Все Platform Services → AI Foundation (для AI анализа)
- BIA/Risk/Planning → Workflow Intelligence (для BPMN workflow)
- AI Foundation → Qdrant (RAG), Redis (кеш)
- Event Intelligence → RabbitMQ (события)

**Дополнительные диаграммы зависимостей в Architecture**:
- `ARCHITECTURE_VISUALIZATIONS_04.mmd` - Service Dependency Graph
- `ARCHITECTURE_VISUALIZATIONS_05.mmd` - Reverse Dependency View

---

## Flows

**Папка**: `flows/`
**Количество**: 3 диаграммы 🆕

| # | Файл | Тип | Описание |
|---|------|-----|----------|
| 1 | `EVENTBUS_MESSAGE_FLOW.mmd` | Sequence | Детальный поток сообщений EventBus: публикация → доставка → retry |
| 2 | `DATA_FLOW_COMPLETE.mmd` | Flowchart | Полный поток данных от пользователя до ответа (с AI) |
| 3 | `AI_ORCHESTRATION_FLOW.mmd` | Graph | Оркестрация AI: RAG, Multi-Agent, BPMN маршрутизация |

### Описание потоков

**EventBus Message Flow**:
- **Publisher** → Redis Streams (XADD) → **Event ID**
- Redis → RabbitMQ (topic exchange) → **Routing**
- RabbitMQ → 3 Subscribers **параллельно**
- **ACK/NACK** механизм с retry
- Redis хранит историю для replay

**Data Flow Complete**:
- User Input → Validation → Route to Service
- **Ветвление**: Needs AI? → AI Foundation (RAG + LLM) / Direct Processing
- RAG: Qdrant Vector DB → Context Retrieval → LLM Reasoning
- Result → PostgreSQL → Publish Event → Redis/RabbitMQ
- Downstream Services → Process Event → Notify Users
- Response → UI → User

**AI Orchestration Flow**:
- Intent Detection → **3 маршрута**:
  1. **Simple Query** → RAG Pipeline → Qdrant → LLM → Answer
  2. **Complex Analysis** → Multi-Agent (3 specialists) → Synthesize → LLM → Answer
  3. **Workflow** → BPMN Engine → Task Execution → Workflow Result
- Все ответы → Build Response → Cache → User

**Дополнительные диаграммы потоков в Architecture**:
- `ARCHITECTURE_VISUALIZATIONS_06.mmd` - Workflow Execution Flow
- `ARCHITECTURE_VISUALIZATIONS_07.mmd` - AI-Powered Analysis Flow
- `ARCHITECTURE_VISUALIZATIONS_08.mmd` - Predictive Intelligence Flow
- `ARCHITECTURE_VISUALIZATIONS_09.mmd` - Collective Intelligence Flow
- `ARCHITECTURE_VISUALIZATIONS_11.mmd` - Event Flow Patterns
- `ARCHITECTURE_VISUALIZATIONS_21.mmd` - Auto-Discovery Flow
- `ARCHITECTURE_VISUALIZATIONS_22.mmd` - Recovery Flow
- `ARCHITECTURE_VISUALIZATIONS_23.mmd` - Proactive Prediction Flow

---

## Integration

**Папка**: `integration/`
**Количество**: 4 диаграммы

| # | Файл | Источник | Описание |
|---|------|----------|----------|
| 1 | `SPRINT_1_ASSEMBLY_PLAN_01.mmd` | SPRINT_1_ASSEMBLY_PLAN.md | План сборки Sprint 1 |
| 2 | `ИНСТРУМЕНТЫ_ДОКУМЕНТАЦИИ_АНАЛИЗ_01.mmd` | ИНСТРУМЕНТЫ_ДОКУМЕНТАЦИИ_АНАЛИЗ.md | Анализ инструментов документации |
| 3 | `DOCUMENTATION_UPDATE_PLAN_01.mmd` | DOCUMENTATION_UPDATE_PLAN.md | План обновления документации |
| 4 | `PHASE1_SYSTEM_BCM_COMPLETE_01.mmd` | PHASE1_SYSTEM_BCM_COMPLETE.md | Завершение Phase 1 System BCM |

### Темы интеграционных диаграмм

- **EventBus Integration**: Интеграция шины событий
- **Service Discovery**: Обнаружение сервисов
- **API Integration**: Интеграция API между сервисами
- **Documentation Pipeline**: Конвейер обработки документации

---

## Business Processes

**Папка**: `business-processes/`
**Количество**: 1 диаграмма

| # | Файл | Источник | Описание |
|---|------|----------|----------|
| 1 | `DOC_GENERATORS_UPDATED_01.mmd` | DOC_GENERATORS_UPDATED.md | Обновленные генераторы документации |

### Бизнес-процессы

- **Document Generation**: Автоматическая генерация документации
- **BPMN Workflows**: Бизнес-процессы в формате BPMN 2.0

---

## 🛠️ Как использовать диаграммы

### Просмотр диаграмм

**Онлайн**:
1. Откройте [Mermaid Live Editor](https://mermaid.live)
2. Скопируйте содержимое .mmd файла
3. Вставьте в редактор
4. Диаграмма отобразится автоматически

**VS Code**:
1. Установите расширение "Markdown Preview Mermaid Support"
2. Откройте .mmd файл
3. Нажмите `Cmd+Shift+V` (Mac) или `Ctrl+Shift+V` (Windows/Linux)

**IntelliJ IDEA / PyCharm**:
1. Установите плагин "Mermaid"
2. Откройте .mmd файл
3. Используйте встроенный preview

### Экспорт в PNG/SVG

**Онлайн**:
- [Mermaid Live Editor](https://mermaid.live) - экспорт в PNG, SVG, PDF

**CLI**:
```bash
# Установка mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Конвертация в PNG
mmdc -i diagram.mmd -o diagram.png

# Конвертация в SVG
mmdc -i diagram.mmd -o diagram.svg
```

### Встраивание в документацию

**Markdown**:
\`\`\`markdown
\`\`\`mermaid
graph TD
    A[Start] --> B[End]
\`\`\`
\`\`\`

**HTML**:
```html
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<div class="mermaid">
graph TD
    A[Start] --> B[End]
</div>
```

---

## 📊 Статистика

### По категориям

| Категория | Количество | Процент |
|-----------|------------|---------|
| Architecture | 24 | 66.7% |
| User Scenarios | 4 | 11.1% |
| Integration | 4 | 11.1% |
| Flows | 3 | 8.3% |
| Dependencies | 1 | 2.8% |
| Business Processes | 1 | 2.8% |
| **ВСЕГО** | **36** | **100%** |

### По типам диаграмм

- **Graph/Flowchart**: ~23 диаграммы
- **Sequence Diagrams**: ~6 диаграмм
- **State Diagrams**: ~2 диаграммы
- **Entity Relationship**: ~3 диаграммы
- **Mixed Types**: ~2 диаграммы

---

## 📚 Связанные документы

- [ARCHITECTURE_VISUALIZATIONS.md](../architecture/ARCHITECTURE_VISUALIZATIONS.md) - Исходный документ с 23 диаграммами
- [PLATFORM_ARCHITECTURE_MAP.md](../../docs/PLATFORM_ARCHITECTURE_MAP.md) - Карта архитектуры платформы
- [ARCHITECTURE.md](../../docs/ARCHITECTURE.md) - Детальная архитектурная документация
- [TZ_USER_INTERFACE.md](../TZ_USER_INTERFACE.md) - Техническое задание для UI/UX
- [INDEX.md](../INDEX.md) - Главный индекс проектной документации

---

## 🔄 Обновление диаграмм

Диаграммы автоматически извлечены из документации: **2025-10-09**

Для обновления диаграмм запустите:
```bash
python3 /tmp/extract_diagrams_v2.py
```

Или вручную добавьте новые .mmd файлы в соответствующие папки.

---

## ✅ Чеклист использования

**Для разработчиков**:
- [ ] Просмотрите основную архитектурную диаграмму (`architecture/platform-architecture.mmd`)
- [ ] Изучите полную системную архитектуру (`ARCHITECTURE_VISUALIZATIONS_01.mmd`)
- [ ] Понимание потоков данных (`flows/DATA_FLOW_COMPLETE.mmd`)
- [ ] Изучите EventBus топологию (`flows/EVENTBUS_MESSAGE_FLOW.mmd`)
- [ ] Понимание зависимостей сервисов (`dependencies/SERVICE_DEPENDENCIES_DETAILED.mmd`)
- [ ] Ознакомьтесь с deployment диаграммами (`ARCHITECTURE_VISUALIZATIONS_17-18.mmd`)

**Для UI/UX дизайнеров**:
- [ ] Изучите пользовательский путь (`user-scenarios/BCM_USER_JOURNEY.mmd`)
- [ ] Понимание BIA workflow (`user-scenarios/BIA_DETAILED_WORKFLOW.mmd`)
- [ ] Ознакомьтесь с риск-оценкой (`user-scenarios/RISK_ASSESSMENT_FLOW.mmd`)
- [ ] Изучите требования к UI из [TZ_USER_INTERFACE.md](../TZ_USER_INTERFACE.md)

**Для администраторов**:
- [ ] Понимание мониторинга (`user-scenarios/ADMIN_SERVICE_MONITORING.mmd`)
- [ ] Изучите инфраструктурную схему (`ARCHITECTURE_VISUALIZATIONS_19.mmd`)
- [ ] Ознакомьтесь с портами (`ARCHITECTURE_VISUALIZATIONS_20.mmd`)

---

**Последнее обновление**: 2025-10-09
**Версия документа**: 2.0.0
