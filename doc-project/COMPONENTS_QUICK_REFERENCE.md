# 🎯 AI Platform - Быстрая Аналитика Компонентов

**Дата:** 2025-10-05
**Кто что делает - краткая справка**

---

## 🏛️ LEVEL 0: MEGA-BRAIN (CEO)

### `/intelligent-core/ai-orchestration/`
**Роль:** Главный мозг всей платформы
**Что делает:**
- Видит ВСЮ систему целиком
- Анализирует intent пользователя
- Принимает стратегические решения
- Делегирует задачи 3 Directors
- Управляет памятью платформы (4-tier)
- Координирует между сегментами

**Ключевые компоненты:**
- `brain/` - центр принятия решений
- `memory/` - рабочая, краткосрочная, долгосрочная, процедурная память
- `tentacles/` - интеграция с Directors
- `organs/` - 10 AI Organs (аналитические процессоры)

**Аналогия:** CEO компании

---

## 🏢 LEVEL 1: DIRECTORS (3 топ-менеджера)

### 1. Infrastructure Director (CTO)
**Сегмент:** Техническая инфраструктура
**Что делает:** Управляет всей технической платформой
**Не связан с:** BCM бизнес-логикой (чисто техника)

### 2. Platform Director (CIO)
**Сегмент:** Платформенная архитектура
**Что делает:** Управляет AI, workflow, обучением, инновациями

### 3. Domain Director (COO)
**Сегмент:** BCM бизнес-логика
**Что делает:** Управляет всеми BCM сервисами и процессами

**Аналогия:** Совет директоров

---

## 📊 LEVEL 2: MANAGERS (23 менеджера)

### 🔧 INFRASTRUCTURE MANAGERS (6)

#### 1. Database Manager
**Модули:** `/infrastructure/database/`
**Что делает:**
- Управляет PostgreSQL/Supabase
- Redis (cache, sessions, rate limiting)
- Vector DB (embeddings)
- Миграции схемы БД
- Бэкапы и восстановление

**Ключевые файлы:**
- `managers/supabase_client.py` - клиент Supabase
- `managers/db_manager.py` - управление БД
- `managers/cache_manager.py` - кэширование
- `managers/rate_limiter.py` - rate limiting
- `migrations_source/*.sql` - миграции схемы

---

#### 2. Security Manager
**Модули:** `/infrastructure/auth/`, `/infrastructure/security/`, `/infrastructure/secrets-manager/`
**Что делает:**
- Аутентификация (Supabase Auth)
- Авторизация (RLS policies)
- Управление секретами
- API security (JWT, keys)
- Защита от атак

---

#### 3. DevOps Manager
**Модули:** `/infrastructure/docker-management/`, `/infrastructure/kubernetes/`, `/infrastructure/deployment-service/`, `/infrastructure/github-integration/`
**Что делает:**
- CI/CD pipelines
- Docker контейнеры
- Kubernetes оркестрация
- Автоматический deployment
- GitHub workflows

---

#### 4. Monitoring Manager
**Модули:** `/infrastructure/monitoring/`, `/infrastructure/observability/`, `/infrastructure/performance/`
**Что делает:**
- Мониторинг производительности
- Health checks сервисов
- Alert management
- Логирование
- Трейсинг (distributed tracing)

---

#### 5. Integration Manager
**Модули:** `/infrastructure/eventbus/`, `/infrastructure/message-queue/`, `/infrastructure/realtime-websocket/`, `/infrastructure/service-discovery/`, `/infrastructure/intelligent-gateway/`
**Что делает:**
- EventBus (центральная нервная система)
- Message queue (RabbitMQ/Redis)
- WebSocket (real-time updates)
- Service discovery
- API Gateway (единая точка входа)

---

#### 6. Reliability Manager
**Модули:** `/infrastructure/reliability/`, `/infrastructure/scalability/`
**Что делает:**
- Горизонтальное масштабирование
- Circuit breaker
- Retry logic
- Disaster recovery
- Performance optimization

---

### 🤖 PLATFORM MANAGERS (7)

#### 1. Workflow Manager
**Модули:** `/intelligent-core/workflow_intelligence/`, `/intelligent-core/bpmn-workflow/`
**Что делает:**
- Workflow Intelligence Engine (самообучающийся движок)
- State machine для процессов
- BPMN визуальные workflow
- Transitions и validators
- Governance (checkpoints + creative zones)
- Case Library (собирает успешные кейсы)

**Ключевые компоненты:**
- `core/workflow_engine.py` - движок workflow
- `core/state_machine.py` - машина состояний
- `case_library/` - библиотека кейсов
- `governance/rules_engine.py` - правила и ограничения
- `workflows/definitions/*.yaml` - определения workflow (BIA, Risk, Planning)

**Важно:** Это мозг всей платформы для процессов!

---

#### 2. AI Orchestration Manager
**Модули:** `/intelligent-core/ai-orchestration/`
**Что делает:**
- MEGA-BRAIN (описан в Level 0)
- Multi-agent координация
- Управляет 10 AI Organs
- Стратегическое планирование
- Память платформы

**10 AI Organs (аналитические):**
1. `governance_brain.py` - анализ governance
2. `emergency_response.py` - симуляция кризисов
3. `impact_oracle.py` - анализ воздействия
4. `scenario_creator.py` - создание сценариев
5. `risk_advisor.py` - анализ рисков
6. `compliance_guardian.py` - проверка compliance
7. `performance_analyst.py` - анализ производительности
8. `learning_coach.py` - ML обучение
9. `plan_generator_organ.py` - генерация планов
10. `lifecycle_monitor.py` - отслеживание жизненного цикла

**Важно:** Organs = stateless аналитические процессоры (НЕ conversational!)

---

#### 3. Coordination Manager
**Модули:** `/intelligent-core/coordination-center/`
**Что делает:**
- "Руки для мозгов" - переводит Intent в действия
- Command Interpreter (Intent → API calls)
- Tool Registry (каталог всех инструментов)
- Execution Tracker (отслеживание выполнения)
- Security Layer (контроль AI действий)

**Ключевые файлы:**
- `command_interpreter.py` - интерпретация команд
- `tool_registry.py` - реестр инструментов
- `execution_tracker.py` - трекинг выполнения
- `security_layer.py` - безопасность AI

**Паттерн:** User/AI Intent → Coordination → API → Execution

---

#### 4. AI Office Manager (Chief AI Officer)
**Модули:** `/intelligent-core/ai-office/`
**Что делает:**
- Управляет 7 AI Colleagues (conversational помощники)
- RAG Pipeline (поиск в документах)
- PDCA Engine (Plan-Do-Check-Act)
- Colleague Coordinator (маршрутизация между коллегами)
- AI Workers (узкие задачи)

**7 AI Colleagues (conversational, stateful):**
1. `compliance_auditor.py` - помощь с compliance
2. `risk_analyst.py` - консультации по рискам
3. `bia_specialist.py` - помощь с BIA
4. `project_manager.py` - управление проектами
5. `incident_advisor.py` - советы по инцидентам
6. `exercise_designer.py` - дизайн упражнений
7. `plan_generator.py` - помощь с планами

**Инфраструктура:**
- `infrastructure/rag_pipeline.py` - RAG для поиска в знаниях
- `infrastructure/pdca_engine.py` - PDCA цикл
- `infrastructure/colleague_coordinator.py` - маршрутизация
- `workers/` - AI Workers (узкие задачи)

**Важно:** Colleagues = stateful, conversational, с памятью диалога!

**Отличие от Organs:**
- Colleagues = интерактивные консультанты (с пользователем)
- Organs = аналитические процессоры (без пользователя)

---

#### 5. Learning Manager
**Модули:** `/intelligent-core/learning-system/`, `/intelligent-core/predictive/`
**Что делает:**
- Machine Learning models
- Continuous learning (учится на каждом случае)
- Pattern recognition
- Predictive analytics
- ML Predictor (предсказывает RTO, сложность, риски)

**Ключевые возможности:**
- Предсказание RTO на основе industry/process
- Stuck detection (6 сигналов когда застряли)
- Success pattern recognition
- Benchmark calculation

---

#### 6. Knowledge Manager
**Модули:** `/intelligent-core/knowledge/`, `/intelligent-core/living-docs/`
**Что делает:**
- Knowledge graphs (граф знаний)
- Living Documentation (самообновляющаяся документация)
- Semantic search
- Document evolution (A/B тестирование доков)
- Gap detection (находит пробелы в документации)

**Living Docs возможности:**
- Auto-improvement на основе user interactions
- Personalization (адаптация под пользователя)
- Version tracking
- Quality metrics

---

#### 7. Community Manager
**Модули:** `/intelligent-core/community_intelligence/`, `/intelligent-core/collective/`
**Что делает:**
- Community Intelligence (коллективная мудрость)
- Collective Agents (privacy-preserving collaboration)
- Peer learning
- Case Library (библиотека успешных кейсов)
- K-anonymity (минимум 5 организаций)

**Community Intelligence:**
- Peer Review Engine
- Reputation System
- Benchmarking
- Case Sharing (анонимизированный)

**Collective Agents:**
- Privacy-preserving analysis
- Collective wisdom без раскрытия данных
- Federated learning patterns

---

### 📋 DOMAIN MANAGERS (10) - BCM Services

#### 1. BIA Manager
**Модули:** `/platform-services/bia-service/`
**Что делает:**
- Business Impact Analysis API
- Process identification
- RTO/RPO calculation
- Dependency mapping
- Impact assessment

**Workflow:**
- BIA process (6 stages)
- Checkpoints + creative zones
- Integration с Workflow Intelligence Engine

---

#### 2. Risk Manager
**Модули:** `/platform-services/risk-service/`
**Что делает:**
- Risk assessment API
- Threat identification
- Risk analysis (likelihood × impact)
- Risk treatment planning
- Vulnerability management

**Workflow:**
- Risk assessment process (5 stages)
- FAIR methodology
- Threat intelligence

---

#### 3. Planning Manager
**Модули:** `/platform-services/planning_service/`, `/platform-services/plans_service/`
**Что делает:**
- Business Continuity Planning API
- Strategy development
- Recovery procedures
- Plan documentation
- Testing coordination

**Workflow:**
- Planning process (3 stages)
- Strategy selection
- Procedure generation

---

#### 4. Incident Manager
**Модули:** `/platform-services/response-service/`
**Что делает:**
- Incident response API
- Crisis management
- Emergency coordination
- Post-incident review
- Incident tracking

---

#### 5. Exercise Manager
**Модули:** Пока нет отдельного сервиса (в roadmap)
**Что делает:**
- Exercise planning
- Testing execution
- Results analysis
- Improvement tracking
- Scenario simulation

---

#### 6. Compliance Manager
**Модули:** `/platform-services/compliance-service/`
**Что делает:**
- Compliance tracking
- Audit management
- Gap analysis
- ISO 22301 certification support
- Regulatory requirements

---

#### 7. Governance Manager
**Модули:** `/platform-services/governance-service/`
**Что делает:**
- Governance framework
- Policy management
- Stakeholder management
- Context management (organization profile)
- Strategic objectives

---

#### 8. Documentation Manager
**Модули:** `/platform-services/documents-service/`
**Что делает:**
- Document management
- Version control
- Document generation
- Templates
- Metadata management

---

#### 9. Validation Manager
**Модули:** `/platform-services/validation-service/`
**Что делает:**
- Data validation
- Quality assurance
- KPI tracking
- Performance metrics
- Alert management

---

#### 10. Supply Chain Manager
**Модули:** Пока нет отдельного сервиса (расширение в БД)
**Что делает:**
- Supply chain continuity
- Vendor assessment
- Third-party risk
- Dependency tracking
- Supplier management

---

## 🛠️ LEVEL 3: EXPERTS & SPECIALISTS

### Infrastructure Experts
- Database specialists
- Security engineers
- DevOps engineers
- SRE (Site Reliability Engineers)

### Platform Experts
- Workflow designers
- AI engineers
- ML engineers
- Knowledge engineers

### Domain Experts
- BIA specialists
- Risk analysts
- Continuity planners
- Compliance auditors
- Incident coordinators

**Примечание:** Experts создаются в `/intelligent-core/ai_platform/experts/`

---

## 🔧 LEVEL 4: TOOLS & ORGANS

### Tools (Structured Operations)
**Расположение:** `/intelligent-core/ai_platform/tools/`, `/intelligent-core/ai_experts/tools/`

**Примеры:**
- `bia_analysis_tool` - BIA анализ
- `rto_calculator` - расчет RTO
- `risk_scoring_tool` - оценка рисков
- `compliance_checker` - проверка compliance
- `document_generator` - генерация документов

**Формат:** Anthropic tool calling format

---

### Organs (Heavy Computation)
**Расположение:** `/intelligent-core/ai-orchestration/organs/`

**10 Organs:**
1. **Governance Brain** - governance анализ
2. **Emergency Response** - симуляция кризисов
3. **Impact Oracle** - анализ воздействия (dependency mapping)
4. **Scenario Creator** - создание сценариев
5. **Risk Advisor** - детальный анализ рисков
6. **Compliance Guardian** - проверка соответствия
7. **Performance Analyst** - анализ производительности
8. **Learning Coach** - ML обучение и тренировка
9. **Plan Generator Organ** - генерация планов
10. **Lifecycle Monitor** - отслеживание жизненного цикла

**Важно:** Organs = библиотека/должностные инструкции для Experts!

---

## 🔄 CROSS-CUTTING COMPONENTS

### EventBus (Central Nervous System)
**Модуль:** `/infrastructure/eventbus/`
**Что делает:**
- Центральная шина событий
- Все события платформы проходят через него
- Subscribers: Case Library, Learning, Monitoring, Audit

**События:**
- `workflow.started`
- `stage.changed`
- `checkpoint.passed`
- `ai.intervention`
- `error.occurred`

---

### Coordination Center (Intent → Action)
**Модуль:** `/intelligent-core/coordination-center/`
**Что делает:**
- Переводит high-level Intent в low-level API calls
- Tool Registry
- Execution Tracking
- Security Layer

---

### Case Library (Collective Wisdom)
**Модуль:** `/intelligent-core/workflow_intelligence/case_library/`
**Что делает:**
- Собирает успешные кейсы со всей платформы
- Анонимизирует данные (K-anonymity)
- Semantic search по кейсам
- Pattern recognition
- Benchmarking

---

### Memory (4-tier)
**Модуль:** `/intelligent-core/ai-orchestration/memory/`

**4 уровня:**
1. **Working Memory** (Redis) - текущие задачи, очередь
2. **Short-term** (Redis) - последние 24 часа, контекст сессии
3. **Long-term** (Supabase) - все решения, история, audit trail
4. **Procedural** (Vector DB) - паттерны, best practices, embeddings

---

### RAG Pipeline (Knowledge Retrieval)
**Модуль:** `/intelligent-core/ai-office/infrastructure/rag_pipeline.py`
**Что делает:**
- Semantic search в документах
- Context retrieval для AI Colleagues
- Augmented prompts
- BCM standards (ISO 22301, NIST, etc.)

**Pipeline:** Query → Vector Search → Retrieve Docs → Augment Prompt → LLM

---

## 📦 SHARED COMPONENTS

### `/shared/`
**Что делает:**
- Unified types (общие типы данных)
- Common utilities
- Shared data models
- Validators
- Constants

---

### `/tools/`
**Что делает:**
- CLI tools
- Automation scripts
- Code generators
- Testing utilities
- Seed data generator

---

## 🎯 QUICK REFERENCE TABLE

| Компонент | Уровень | Роль | Stateful? | User-Facing? |
|-----------|---------|------|-----------|--------------|
| **MEGA-BRAIN** | 0 | CEO - стратегия | ✅ | ❌ |
| **3 Directors** | 1 | Топ-менеджеры | ✅ | ❌ |
| **23 Managers** | 2 | Менеджеры сегментов | ✅ | ❌ |
| **AI Colleagues** | 3 | Консультанты | ✅ | ✅ |
| **AI Organs** | 4 | Аналитики | ❌ | ❌ |
| **BCM Services** | 3 | API сервисы | ❌ | ✅ (via API) |
| **Tools** | 4 | Инструменты | ❌ | ❌ |
| **EventBus** | Foundation | Нервная система | ❌ | ❌ |
| **Database** | Foundation | Хранилище | - | ❌ |
| **Coordination** | Foundation | Intent→Action | ❌ | ❌ |

---

## 🔑 KEY PATTERNS

### Stateful vs Stateless
- **Stateful:** AI Colleagues, MEGA-BRAIN, Managers (память нужна)
- **Stateless:** AI Organs, Tools, Services (чистые функции)

### RAG vs Direct LLM
- **RAG:** AI Colleagues (ищут в документах)
- **Direct:** AI Organs (анализируют данные)

### Conversational vs Analytical
- **Conversational:** AI Colleagues (диалог с пользователем)
- **Analytical:** AI Organs (обработка данных)

---

## 🎯 КТО ВЫЗЫВАЕТ КОГО?

```
User Request
    ↓
API Gateway
    ↓
MEGA-BRAIN (Level 0)
    ├─> Infrastructure Director (Level 1)
    │   └─> Database Manager (Level 2)
    │       └─> Supabase Client (Level 4)
    │
    ├─> Platform Director (Level 1)
    │   ├─> AI Office Manager (Level 2)
    │   │   └─> AI Colleague (Level 3)
    │   │       ├─> RAG Pipeline (Foundation)
    │   │       └─> Tool (Level 4)
    │   │
    │   └─> Workflow Manager (Level 2)
    │       └─> Workflow Engine (Level 3)
    │           └─> Case Library (Foundation)
    │
    └─> Domain Director (Level 1)
        └─> BIA Manager (Level 2)
            └─> BIA Service (Level 3)
                ├─> Workflow Engine (Platform)
                ├─> AI Organ (Level 4)
                └─> Database (Foundation)
```

---

## 📊 SUMMARY

**Всего компонентов:**
- 1 MEGA-BRAIN
- 3 Directors
- 23 Managers
- 7 AI Colleagues
- 10 AI Organs
- 10 BCM Services
- ~30 Tools
- 5 Foundation Services

**Всего:** ~90 активных компонентов

**Принцип:** Каждый компонент знает свою роль и не вылезает за границы!

---

**Готово!** Теперь ясно кто что делает! 🎯
