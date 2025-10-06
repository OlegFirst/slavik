# 🗂️ Модули: Стратегия Размещения

**Версия**: 1.0
**Дата**: 2025-10-06
**Статус**: Проектный Документ

---

## 📋 Обзор Нераспределенных Модулей

### Найдено 4 модуля, требующих размещения:

1. **intelligent-core/coordination-center/** - ✅ Реализован (2,526 LOC, порт 8004)
2. **intelligent-core/insrumets/** - 🚧 Частично реализован (симуляция + digital twin)
3. **intelligent-core/AI-Servises/** - ✅ 4 сервиса (routing, project-agent, mio-manager, workflow-optimizer)
4. Другие модули в intelligent-core

---

## 🎯 Стратегия Размещения

### Принцип Организации:

```
intelligent-core/
├── ai-foundation/          # AI Infrastructure (RAG, ML, Learning, LLM)
├── workflow_intelligence/  # Workflow Engine (THE BRAIN)
├── expertise-center/       # Domain Plugins (BCM specialists, colleagues, analyzers)
│
├── orchestration/          # 🎯 ORCHESTRATION LAYER
│   ├── coordination-center/     # ✅ AI → Tools посредник
│   ├── ai-orchestration/        # Exists (AI task orchestration)
│   └── service-orchestration/   # NEW (service-level orchestration)
│
├── simulation/             # 🔬 SIMULATION & MODELING LAYER
│   ├── digital-twin/            # Digital Twin (moved from insrumets)
│   ├── scenarios/               # Scenario testing (moved from insrumets)
│   ├── engines/                 # Simulation engines (moved from insrumets)
│   └── thehive/                 # TheHive integration (moved from insrumets)
│
├── devops-ai/              # 🤖 DEVOPS AI LAYER (NEW!)
│   ├── agent-router/            # Agent routing service
│   ├── project-agent/           # Project analysis CLI
│   ├── mio-manager/             # Monitoring & Observability Manager
│   └── workflow-optimizer/      # Workflow optimization
│
└── [other modules...]
```

---

## 📁 Детальное Размещение

### 1. coordination-center → `orchestration/coordination-center/`

**Текущий статус**: ✅ **РЕАЛИЗОВАН и работает** (2,526 LOC, порт 8004)

**Что это**:
- Посредник между Intelligent Core (AI мозги) и Execution Engine (инструменты)
- Command Interpreter - транслирует Intent → API calls
- Tool Registry - каталог инструментов для AI
- Execution Tracker - трекинг выполнения
- Security Layer - контроль AI действий

**Где размещать**: `intelligent-core/orchestration/coordination-center/`

**Обоснование**:
- ✅ Это **orchestration** модуль (координирует AI → Tools)
- ✅ Логически относится к orchestration layer
- ✅ Работает рядом с ai-orchestration (AI task orchestration)
- ✅ УЖЕ НАХОДИТСЯ в правильном месте!

**Структура** (текущая, менять не нужно):
```
intelligent-core/orchestration/coordination-center/
├── api/
│   ├── __init__.py
│   └── routes.py                 # FastAPI routes
├── core/
│   ├── __init__.py
│   ├── command_interpreter.py    # Intent → Commands
│   ├── tool_registry.py          # Tool catalog
│   ├── execution_tracker.py      # Execution tracking
│   └── security_layer.py         # AI security
├── claude-integration/
│   ├── __init__.py
│   └── governance_brain.py       # Claude integration
├── models/
│   ├── __init__.py
│   └── schemas.py                # Pydantic models
├── tests/
│   ├── __init__.py
│   └── test_e2e_bia_creation.py
├── main.py                       # FastAPI app (port 8004)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

**Действия**: ✅ **НЕТ - модуль уже на своем месте!**

---

### 2. insrumets → `simulation/` (НОВАЯ ДИРЕКТОРИЯ)

**Текущий статус**: 🚧 Частично реализован, требует реорганизации

**Текущая структура** (плохо организована):
```
intelligent-core/insrumets/        # ❌ Опечатка в названии
├── digital-twin/                  # Digital Twin (~15 LOC файлов)
├── scenarios/                     # Сценарии тестирования
│   ├── bcm_incident/
│   └── scenario_orchestrator/
└── simulation/                    # Симуляторы
    ├── simulation/                # ❌ Вложенность
    ├── simulation2/
    └── thehive/                   # TheHive integration
```

**Что это**:
- **digital-twin/** - Цифровой двойник организации (collectors, bridges, core)
- **scenarios/** - Сценарии инцидентов и тестирование
- **simulation/** - Симуляторы (BIA engine, exercise simulators, scenario orchestrator)
- **thehive/** - Интеграция с TheHive (incident response platform)

**Куда размещать**: `intelligent-core/simulation/` (НОВАЯ ДИРЕКТОРИЯ)

**Обоснование**:
- ✅ Это **simulation & modeling** компонент
- ✅ Не AI infrastructure, не workflow, не domain plugin
- ✅ Самостоятельный слой для симуляции и моделирования
- ✅ Исправляет опечатку "insrumets"

**Новая структура**:
```
intelligent-core/simulation/           # NEW! Simulation & Modeling Layer
│
├── digital-twin/                      # Digital Twin Component
│   ├── api/                           # FastAPI endpoints
│   ├── core/
│   │   ├── twin_engine.py             # Core twin engine
│   │   ├── state_manager.py           # State management
│   │   └── synchronizer.py            # Real-world sync
│   ├── collectors/                    # Data collectors
│   │   ├── bia_collector.py
│   │   ├── risk_collector.py
│   │   └── metrics_collector.py
│   ├── bridges/                       # External integrations
│   │   ├── platform_bridge.py
│   │   └── eventbus_bridge.py
│   ├── models/
│   └── main.py
│
├── scenarios/                         # Scenario Testing
│   ├── bcm_incident/                  # BCM incident scenarios
│   │   ├── scenarios/
│   │   │   ├── cyber_attack.json
│   │   │   ├── natural_disaster.json
│   │   │   └── supply_chain.json
│   │   └── simulator.py
│   │
│   └── orchestrator/                  # Scenario orchestration
│       ├── api/
│       ├── core/
│       │   ├── scenario_engine.py
│       │   └── flow_manager.py
│       └── models/
│
├── engines/                           # Simulation Engines
│   ├── bia_engine/                    # BIA simulation (CIW)
│   │   ├── bia_ciw_engine.py
│   │   ├── app.py
│   │   └── main.py
│   │
│   ├── exercise_simulator/            # Exercise simulation
│   │   ├── scenario_flow_manager.py
│   │   ├── ai_scenario_generator.py
│   │   ├── nics_client.py             # NICS integration
│   │   ├── jaamsim_client.py          # JaamSim integration
│   │   └── bridge_service.py
│   │
│   └── process_simulator/             # Process mining simulation
│       └── sim_adapter.py
│
├── integrations/                      # External Integrations
│   └── thehive/                       # TheHive integration
│       ├── thehive_client.py
│       ├── thehive_adapter.py
│       ├── bridge_service.py
│       ├── webhooks.py
│       └── mock_data.py
│
├── __init__.py
├── README.md
└── requirements.txt
```

**План миграции**:
```bash
# 1. Создать новую директорию
mkdir -p /Users/MD/AI-Platform-ISO/intelligent-core/simulation

# 2. Переместить digital-twin
mv /Users/MD/AI-Platform-ISO/intelligent-core/insrumets/digital-twin \
   /Users/MD/AI-Platform-ISO/intelligent-core/simulation/

# 3. Переместить scenarios
mv /Users/MD/AI-Platform-ISO/intelligent-core/insrumets/scenarios \
   /Users/MD/AI-Platform-ISO/intelligent-core/simulation/

# 4. Реорганизовать simulation (убрать вложенность)
mkdir -p /Users/MD/AI-Platform-ISO/intelligent-core/simulation/engines
mv /Users/MD/AI-Platform-ISO/intelligent-core/insrumets/simulation/simulation/bia_engine \
   /Users/MD/AI-Platform-ISO/intelligent-core/simulation/engines/
mv /Users/MD/AI-Platform-ISO/intelligent-core/insrumets/simulation/simulation/exercise_simulators \
   /Users/MD/AI-Platform-ISO/intelligent-core/simulation/engines/
# ... и так далее

# 5. Переместить TheHive integration
mkdir -p /Users/MD/AI-Platform-ISO/intelligent-core/simulation/integrations
mv /Users/MD/AI-Platform-ISO/intelligent-core/insrumets/simulation/thehive \
   /Users/MD/AI-Platform-ISO/intelligent-core/simulation/integrations/

# 6. Архивировать старое
mkdir -p /Users/MD/AI-Platform-ISO/intelligent-core/_archive/migration_2025_10_06
mv /Users/MD/AI-Platform-ISO/intelligent-core/insrumets \
   /Users/MD/AI-Platform-ISO/intelligent-core/_archive/migration_2025_10_06/
```

**Время миграции**: 2-3 часа

---

### 3. AI-Servises → `devops-ai/` (НОВАЯ ДИРЕКТОРИЯ)

**Текущий статус**: ✅ 4 реализованных сервиса, но плохое название директории

**Текущая структура** (плохое название):
```
intelligent-core/AI-Servises/      # ❌ Опечатка + неясное название
├── agent-router/                  # Agent routing service (295 LOC)
├── project-agent/                 # Project analysis CLI
├── mio-manager/                   # Monitoring & Observability (port 8046)
└── ai_workflow_optimizer/         # Workflow optimization
```

**Что это**:
- **agent-router** - Роутинг AI запросов между микросервисами
- **project-agent** - CLI агент для анализа проектов (security, quality, testing, compliance)
- **mio-manager** - AI-powered мониторинг и observability
- **ai_workflow_optimizer** - Оптимизация workflow через AI

**Куда размещать**: `intelligent-core/devops-ai/` (НОВАЯ ДИРЕКТОРИЯ)

**Обоснование**:
- ✅ Это **DevOps AI** инструменты (не бизнес-логика!)
- ✅ Не domain-specific (не BCM, не HR, не Finance)
- ✅ Помогают в разработке и операциях платформы
- ✅ Исправляет опечатку "Servises" → "devops-ai"

**Новая структура**:
```
intelligent-core/devops-ai/            # NEW! DevOps AI Tools Layer
│
├── agent-router/                      # AI Agent Router (port TBD)
│   ├── __init__.py
│   ├── router.py                      # Main routing logic (295 LOC)
│   ├── models.py                      # Agent roles, capabilities
│   ├── health.py                      # Health checks
│   ├── analytics.py                   # Routing analytics
│   ├── requirements.txt
│   └── README.md
│
├── project-agent/                     # Project Analysis CLI
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── cli.py                     # Main CLI
│   │   ├── config.py                  # Configuration
│   │   ├── indexer.py                 # Code indexing
│   │   ├── domain_detector.py         # Auto-domain detection
│   │   ├── modules/
│   │   │   ├── security.py            # Security module
│   │   │   ├── quality.py             # Quality module
│   │   │   └── testing.py             # Testing module
│   │   ├── compliance.py              # Compliance checks
│   │   ├── report.py                  # Report generation
│   │   ├── changelog.py               # Changelog generation
│   │   ├── bpmn_yaml.py               # BPMN/YAML mapping
│   │   └── doc_sync.py                # Doc/Code sync check
│   ├── test-project/                  # Test project
│   ├── setup.py
│   ├── requirements.txt
│   ├── README.md
│   ├── QUICKSTART.md
│   └── START_HERE.md
│
├── mio-manager/                       # Monitoring & Observability Manager
│   ├── api/                           # FastAPI endpoints
│   ├── models/
│   ├── repositories/
│   ├── integrations/
│   │   ├── prometheus/
│   │   ├── grafana/
│   │   └── thehive/
│   ├── workflows/
│   │   └── automated_response_engine.py
│   ├── scheduler/
│   │   └── automation_jobs.py
│   ├── main.py                        # FastAPI app (port 8046)
│   ├── config.py
│   ├── database.py
│   ├── requirements.txt
│   ├── README.md
│   └── INDEX.md
│
├── workflow-optimizer/                # AI Workflow Optimizer
│   ├── main.py
│   ├── optimizer.py
│   ├── models.py
│   └── README.md
│
├── __init__.py
├── README.md                          # Overview of all DevOps AI tools
└── requirements.txt                   # Shared dependencies
```

**План миграции**:
```bash
# 1. Создать новую директорию
mkdir -p /Users/MD/AI-Platform-ISO/intelligent-core/devops-ai

# 2. Переместить все сервисы
mv /Users/MD/AI-Platform-ISO/intelligent-core/AI-Servises/agent-router \
   /Users/MD/AI-Platform-ISO/intelligent-core/devops-ai/

mv /Users/MD/AI-Platform-ISO/intelligent-core/AI-Servises/project-agent \
   /Users/MD/AI-Platform-ISO/intelligent-core/devops-ai/

mv /Users/MD/AI-Platform-ISO/intelligent-core/AI-Servises/mio-manager \
   /Users/MD/AI-Platform-ISO/intelligent-core/devops-ai/

# 3. Переименовать ai_workflow_optimizer → workflow-optimizer
mv /Users/MD/AI-Platform-ISO/intelligent-core/AI-Servises/ai_workflow_optimizer \
   /Users/MD/AI-Platform-ISO/intelligent-core/devops-ai/workflow-optimizer

# 4. Создать общий README
cat > /Users/MD/AI-Platform-ISO/intelligent-core/devops-ai/README.md << 'EOF'
# DevOps AI Tools

AI-powered tools for development and operations.

## Services:

1. **agent-router** - AI agent routing service
2. **project-agent** - Project analysis CLI
3. **mio-manager** - Monitoring & Observability Manager (port 8046)
4. **workflow-optimizer** - Workflow optimization

## Usage:

See individual service READMEs for details.
EOF

# 5. Архивировать старое
mv /Users/MD/AI-Platform-ISO/intelligent-core/AI-Servises \
   /Users/MD/AI-Platform-ISO/intelligent-core/_archive/migration_2025_10_06/
```

**Время миграции**: 1-2 часа

---

## 🗺️ Полная Карта После Миграции

```
intelligent-core/
│
├── ai-foundation/              # 🏗️ AI INFRASTRUCTURE
│   ├── rag/
│   ├── ml/
│   ├── learning/
│   ├── context/
│   └── llm/
│
├── workflow_intelligence/      # 🧠 THE BRAIN (Workflow Engine)
│   ├── core/
│   ├── services/
│   └── workflows/
│
├── expertise-center/           # 🎓 DOMAIN PLUGINS
│   ├── core/
│   ├── shared/
│   └── domains/
│       └── bcm/
│
├── orchestration/              # 🎯 ORCHESTRATION LAYER
│   ├── coordination-center/   # ✅ AI → Tools посредник (port 8004)
│   ├── ai-orchestration/      # AI task orchestration
│   └── service-orchestration/ # Service-level orchestration
│
├── simulation/                 # 🔬 SIMULATION & MODELING LAYER (NEW!)
│   ├── digital-twin/          # Digital Twin
│   ├── scenarios/             # Scenario testing
│   ├── engines/               # Simulation engines
│   └── integrations/
│       └── thehive/           # TheHive integration
│
├── devops-ai/                  # 🤖 DEVOPS AI LAYER (NEW!)
│   ├── agent-router/          # Agent routing
│   ├── project-agent/         # Project analysis CLI
│   ├── mio-manager/           # Monitoring & Observability (port 8046)
│   └── workflow-optimizer/    # Workflow optimization
│
├── community_intelligence/     # 🌐 COMMUNITY AI
├── collective/                 # 🤝 COLLECTIVE INTELLIGENCE
├── predictive/                 # 🔮 PREDICTIVE SERVICES
├── learning-system/            # 📚 LEARNING SYSTEM
├── living-docs/                # 📖 LIVING DOCUMENTATION
│
└── _archive/                   # 🗄️ ARCHIVE
    └── migration_2025_10_06/
        ├── insrumets/          # Moved to simulation/
        └── AI-Servises/        # Moved to devops-ai/
```

---

## 📊 Сравнение: До и После

### ДО (текущее состояние):
```
intelligent-core/
├── coordination-center/        # ✅ OK (in orchestration/)
├── insrumets/                  # ❌ Опечатка, плохая структура
├── AI-Servises/                # ❌ Опечатка, неясное название
└── [other modules]
```

**Проблемы**:
- ❌ Опечатки в названиях (insrumets, Servises)
- ❌ Нет четкой классификации
- ❌ Смешанная логика (simulation + devops в разных местах)

### ПОСЛЕ (предложение):
```
intelligent-core/
├── orchestration/
│   └── coordination-center/    # ✅ AI → Tools посредник
├── simulation/                 # ✅ NEW! Simulation & Modeling
│   ├── digital-twin/
│   ├── scenarios/
│   ├── engines/
│   └── integrations/
├── devops-ai/                  # ✅ NEW! DevOps AI Tools
│   ├── agent-router/
│   ├── project-agent/
│   ├── mio-manager/
│   └── workflow-optimizer/
└── [other modules]
```

**Преимущества**:
- ✅ Нет опечаток
- ✅ Четкая классификация (orchestration, simulation, devops-ai)
- ✅ Логичная структура
- ✅ Легко найти нужный модуль

---

## 🚀 План Миграции

### Фаза 1: Проверка (30 минут)
```bash
# Проверить что ничего не сломается
grep -r "from insrumets" intelligent-core/ platform-services/
grep -r "from AI-Servises" intelligent-core/ platform-services/
grep -r "import insrumets" intelligent-core/ platform-services/
grep -r "import AI-Servises" intelligent-core/ platform-services/
```

### Фаза 2: Создание новых директорий (15 минут)
```bash
mkdir -p intelligent-core/simulation
mkdir -p intelligent-core/devops-ai
```

### Фаза 3: Миграция simulation (1-2 часа)
```bash
# Следовать плану из секции "2. insrumets → simulation/"
```

### Фаза 4: Миграция devops-ai (1 час)
```bash
# Следовать плану из секции "3. AI-Servises → devops-ai/"
```

### Фаза 5: Обновление импортов (30 минут)
```bash
# Если есть импорты (вряд ли), обновить их
find intelligent-core platform-services -name "*.py" -exec sed -i '' \
  's/from insrumets/from simulation/g' {} +

find intelligent-core platform-services -name "*.py" -exec sed -i '' \
  's/from AI-Servises/from devops_ai/g' {} +
```

### Фаза 6: Архивирование старого (15 минут)
```bash
mkdir -p intelligent-core/_archive/migration_2025_10_06
mv intelligent-core/insrumets intelligent-core/_archive/migration_2025_10_06/
mv intelligent-core/AI-Servises intelligent-core/_archive/migration_2025_10_06/
```

### Фаза 7: Тестирование (1 час)
```bash
# Проверить что все работает
pytest intelligent-core/simulation/
pytest intelligent-core/devops-ai/

# Проверить coordination-center (он уже на месте)
pytest intelligent-core/orchestration/coordination-center/
```

### Фаза 8: Документация (30 минут)
```bash
# Обновить FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md
# Создать README.md для новых директорий
```

**TOTAL TIME: 5-7 часов**

---

## ✅ Чек-лист После Миграции

- [ ] intelligent-core/simulation/ создана и заполнена
- [ ] intelligent-core/devops-ai/ создана и заполнена
- [ ] intelligent-core/orchestration/coordination-center/ не тронута (уже на месте)
- [ ] Старые директории в _archive/
- [ ] Все импорты обновлены
- [ ] Тесты проходят
- [ ] README.md созданы для новых директорий
- [ ] FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md обновлена
- [ ] Git commit с описанием изменений

---

## 📝 Обоснование Решений

### Почему simulation/ (не digital-twin/)?
- ✅ digital-twin - только ЧАСТЬ функционала
- ✅ Есть также scenarios, engines, integrations
- ✅ simulation - более общее и правильное название

### Почему devops-ai/ (не tools/ или services/)?
- ✅ tools/ слишком общее (может быть что угодно)
- ✅ services/ путаница с platform-services/
- ✅ devops-ai/ четко показывает назначение - AI для DevOps

### Почему coordination-center в orchestration/?
- ✅ Это orchestration модуль (координирует AI → Tools)
- ✅ Логически рядом с ai-orchestration
- ✅ УЖЕ НАХОДИТСЯ там (ничего делать не нужно!)

---

## 🎯 Следующие Шаги

1. **Утверждение** - Получить подтверждение на миграцию
2. **Резервная копия** - Сделать backup всего intelligent-core/
3. **Миграция** - Выполнить план миграции (5-7 часов)
4. **Тестирование** - Убедиться что ничего не сломалось
5. **Обновление документации** - Обновить архитектурные документы
6. **Git commit** - Зафиксировать изменения

---

**Версия**: 1.0
**Дата**: 2025-10-06
**Статус**: Готов к утверждению
**Ожидается**: Подтверждение для начала миграции
