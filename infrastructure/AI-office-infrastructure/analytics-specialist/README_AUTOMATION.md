# 🤖 Automated Knowledge & Intelligence System

**Создана система самообучения и самосовершенствования платформы**

> Система, которая изучает саму себя, моделирует свое поведение, и становится экспертом в своих предметных областях (BCM, ISO 22301, и т.д.)

---

## 🎯 Концепция

### Проблема
- У нас есть **код** (базовая бизнес-логика)
- У нас есть **модули** (platform-services, intelligent-core, infrastructure)
- Все модули запускаются + **AI** как дополнительный элемент
- AI увеличивает **в тысячи раз** варианты использования кода

### Решение
Создать **мега прокаченного эксперта**, который:
1. **Изучает сам себя** (self-learning) - анализирует каждый модуль
2. **Моделирует поведение** (system modeling) - понимает как работает
3. **Проектирует улучшения** (continuous improvement) - предлагает развитие
4. **Становится экспертом** (domain expertise) - накапливает знания BCM/ISO 22301

---

## 🏗️ Архитектура

### 3 Основных Компонента

#### 1. **System Behavior Analyzer**
📍 `tools/system_behavior_analyzer.py`

**Что делает:**
- Анализирует состояния системы (states, transitions)
- Извлекает поведенческие паттерны из Event Bus / GitHub / Database
- Обнаруживает edge cases и граничные условия
- Генерирует user scenarios (Gherkin format)
- Конвертирует flows → executable code (Python rules, Temporal workflows)

**Ключевые возможности:**
```python
# Анализ состояний
state_machine = await analyzer.analyze_system_states()
# → 15+ states, valid transitions, entry/exit conditions

# Извлечение паттернов
patterns = await analyzer.extract_behavioral_patterns(source="events")
# → "BIA → Risk → Plans" flow (347 occurrences, 95% confidence)

# Обнаружение edge cases
edge_cases = await analyzer.detect_edge_cases()
# → "Journey jumps from BIA to Exercise (skips Risk)" - CRITICAL

# Генерация правил
rules = await analyzer.convert_flows_to_rules(output_format="python")
# → Generated: generated_rules.py
```

#### 2. **Intelligent Module Analyzer**
📍 `tools/intelligent_module_analyzer.py`

**Что делает:**
- Анализирует **каждый модуль** платформы глубоко
- Извлекает domain expertise (BCM, ISO 22301, Risk Management)
- Генерирует **x1000 сценариев использования** через AI
- Оценивает уровень экспертизы (beginner/intermediate/expert)
- Создает improvement roadmap для каждого модуля

**Для каждого модуля создается:**
```
1. Code Analysis
   - Структура: классы, функции, API endpoints
   - Метрики: LOC, complexity, dependencies

2. Behavioral Model
   - Цель модуля (purpose)
   - Паттерны взаимодействия (API, Events, Database)

3. Usage Scenarios
   - Базовые сценарии (из кода): ~10 сценариев
   - AI-расширенные (через LLM): ~100+ сценариев
   - Различные контексты, edge cases, интеграции

4. Domain Expertise
   - Концепции (BIA, RTO, RPO, Risk Assessment)
   - Стандарты (ISO 22301, ISO 31000, NIST)
   - Уровень экспертизы

5. Improvement Roadmap
   - Приоритезированные улучшения
   - Квартальный план (Q1, Q2, Q3, Q4)
```

**Пример запуска:**
```bash
# Анализировать все модули
python3 intelligent_module_analyzer.py --all

# Результат:
# - reports/module_analysis/bia-service_analysis.json
# - reports/module_analysis/bia-service_analysis.md
# - reports/module_analysis/MASTER_ANALYSIS_REPORT.md
```

#### 3. **Automated Knowledge Pipeline**
📍 `workflows/automated_knowledge_pipeline.py`

**Что делает:**
- Объединяет все процессы в **единый pipeline**
- Запускается автоматически (GitHub Actions, scheduler)
- Интегрирует с RAG (Qdrant) для AI Memory
- Генерирует документацию
- Отправляет уведомления

**6 стадий pipeline:**
```
Stage 1: System Analysis
├─ Analyze system states (15+ states)
├─ Detect edge cases (invalid transitions, boundary conditions)
└─ Output: state_machine.json, edge_cases.json

Stage 2: Pattern Extraction
├─ Extract behavioral patterns from Event Bus
├─ Analyze frequency and confidence
└─ Output: behavioral_patterns.json

Stage 3: Documentation Generation
├─ Generate user scenarios (Gherkin format)
├─ Call AI documentation generator
└─ Output: user_scenarios.json, README.md, API.md

Stage 4: Rules Generation
├─ Convert flows → Python validation rules
├─ Convert flows → Temporal workflows
└─ Output: generated_rules.py, generated_workflows.py

Stage 5: RAG Integration
├─ Load comprehensive docs into Qdrant
├─ Index scenarios into vector database
└─ Output: 3 Qdrant collections

Stage 6: Event Catalog
├─ Scan codebase for event usage
├─ Generate event catalog
└─ Output: EVENTS.md, events_catalog.json
```

---

## 🚀 Использование

### 1. Запуск вручную

```bash
# Полный pipeline (все 6 стадий)
python3 infrastructure/AI-office-infrastructure/analytics-specialist/workflows/automated_knowledge_pipeline.py --full

# Только анализ
python3 infrastructure/AI-office-infrastructure/analytics-specialist/workflows/automated_knowledge_pipeline.py --analyze

# Только документация
python3 infrastructure/AI-office-infrastructure/analytics-specialist/workflows/automated_knowledge_pipeline.py --docs

# Только RAG индексация
python3 infrastructure/AI-office-infrastructure/analytics-specialist/workflows/automated_knowledge_pipeline.py --index
```

### 2. Через API (analytics-specialist)

```bash
# Trigger pipeline
curl -X POST http://localhost:8007/api/v1/pipeline/trigger \
  -H "Content-Type: application/json" \
  -d '{"mode": "full", "async_execution": true}'

# Check status
curl http://localhost:8007/api/v1/pipeline/status/pipeline_20251009_120000

# List runs
curl http://localhost:8007/api/v1/pipeline/list?limit=10

# Get latest
curl http://localhost:8007/api/v1/pipeline/latest

# Health check
curl http://localhost:8007/api/v1/pipeline/health
```

### 3. Автоматически (GitHub Actions)

Pipeline запускается автоматически:
- **На каждый push** в main/develop (если изменены файлы в intelligent-core/, platform-services/, infrastructure/)
- **Ежедневно** в 02:00 UTC (полный pipeline)

Файл: `.github/workflows/automated-knowledge-pipeline.yml`

### 4. Через scheduler (mio-manager)

```python
from infrastructure.AI_office_infrastructure.mio_manager.workflows.knowledge_pipeline_scheduler import KnowledgePipelineScheduler

scheduler = KnowledgePipelineScheduler()

# Schedule daily full pipeline (02:00 UTC)
await scheduler.schedule_daily_full_pipeline()

# Schedule hourly analysis
await scheduler.schedule_hourly_analysis()

# On-demand trigger
result = await scheduler.trigger_on_demand(mode="full", reason="Testing")
```

---

## 📊 Outputs

### Где находятся результаты

```
infrastructure/AI-office-infrastructure/analytics-specialist/reports/
├── pipeline_report_20251009_120000.json     # Pipeline run summary
├── state_machine.json                        # System states & transitions
├── edge_cases.json                           # Detected edge cases
├── behavioral_patterns.json                  # Extracted patterns
├── user_scenarios.json                       # Generated scenarios
├── generated_rules.py                        # Python validation rules
├── generated_workflows.py                    # Temporal workflows
└── module_analysis/                          # Module analysis reports
    ├── bia-service_analysis.json
    ├── bia-service_analysis.md
    ├── risk-service_analysis.json
    ├── risk-service_analysis.md
    └── MASTER_ANALYSIS_REPORT.md            # Complete platform analysis
```

### Что индексируется в Qdrant (RAG/Memory)

**3 коллекции:**

1. **`platform_capabilities`** - AI capabilities (LLM, RAG, Orchestration, Domain Experts)
2. **`platform_patterns`** - Infrastructure patterns (Event Bus, Saga, Circuit Breaker)
3. **`platform_scenarios`** - Usage scenarios (570+ scenarios + generated scenarios)

---

## 🔄 Интеграции

### С существующими инструментами

Pipeline интегрирован с:

1. **doc-generators/** (infrastructure/tools/)
   - `ai_documentation_generator.py` - AI-powered README generation
   - `documentation_generator.py` - Module documentation
   - `event_catalog_generator.py` - Event catalog

2. **analytics-specialist**
   - API endpoints для trigger/monitor pipeline
   - Background task execution
   - Metrics recording

3. **mio-manager**
   - Scheduled automation (cron-style)
   - Monitoring pipeline execution
   - Notifications

4. **monitoring service**
   - Metrics: `pipeline.daily.success`, `pipeline.daily.failure`
   - Health checks
   - Alerting

5. **notification service**
   - Slack notifications
   - Email alerts
   - GitHub issues on failure

6. **Qdrant (RAG/Memory)**
   - Vector embeddings (sentence-transformers)
   - Knowledge base indexing
   - Semantic search

---

## ⚙️ Конфигурация

### Pipeline Config
📍 `config/pipeline_config.yaml`

```yaml
pipeline:
  modes:
    full: [system_analysis, pattern_extraction, docs, rules, rag, events]
    analyze: [system_analysis, pattern_extraction]
    docs: [documentation_generation]
    index: [rag_integration]

  stages:
    system_analysis:
      timeout_seconds: 300
      sources: [database, events, github]

    pattern_extraction:
      thresholds:
        high_frequency: 100
        medium_frequency: 10

    rag_integration:
      qdrant:
        url: "${QDRANT_URL}"
        api_key: "${QDRANT_API_KEY}"
      embedding:
        model: "sentence-transformers/all-mpnet-base-v2"

scheduling:
  schedules:
    daily_full_pipeline:
      cron: "0 2 * * *"  # 02:00 UTC
    hourly_analysis:
      cron: "0 * * * *"  # Every hour
```

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...          # For AI generation
QDRANT_URL=http://localhost:6333      # Vector database
QDRANT_API_KEY=...                    # Qdrant API key

# Optional
REDIS_URL=redis://localhost:6379      # Event Bus
DATABASE_URL=postgresql://...          # PostgreSQL
SLACK_WEBHOOK_URL=...                 # Notifications
```

---

## 📈 Метрики и мониторинг

### Записываемые метрики

```
pipeline.daily.success           # Daily pipeline успешно
pipeline.daily.failure           # Daily pipeline failed
pipeline.hourly.triggered        # Hourly analysis triggered
pipeline.on_demand.full          # On-demand full pipeline
pipeline.on_demand.analyze       # On-demand analysis
```

### Health Check

```bash
curl http://localhost:8007/api/v1/pipeline/health

# Response:
{
  "status": "healthy",
  "components": {
    "pipeline": "ok",
    "reports_dir": "ok",
    "analyzer": "ok"
  },
  "active_runs": 2,
  "timestamp": "2025-10-09T12:00:00"
}
```

---

## 🎓 Как это работает (пример)

### Сценарий: Daily Full Pipeline

**02:00 UTC - GitHub Actions trigger**

```
1. System Analysis (5 min)
   ├─ Scan PostgreSQL for journey states
   ├─ Scan Redis Streams for events
   ├─ Scan GitHub workflows for patterns
   └─ Generate state_machine.json

2. Pattern Extraction (5 min)
   ├─ Extract "BIA → Risk → Plans" flow (347 occurrences)
   ├─ Extract "Stuck → Intervention" pattern (52 occurrences)
   └─ Generate behavioral_patterns.json

3. Documentation Generation (10 min)
   ├─ Convert patterns → Gherkin scenarios
   ├─ Call AI doc generator (Claude)
   └─ Generate README.md for 15 modules

4. Rules Generation (5 min)
   ├─ Convert "BIA must have ≥1 process" → Python validator
   ├─ Convert "ISO Journey" → Temporal workflow
   └─ Generate generated_rules.py

5. RAG Integration (10 min)
   ├─ Load 7 comprehensive docs
   ├─ Create embeddings (768-dim vectors)
   ├─ Upload to Qdrant (platform_scenarios collection)
   └─ Index 570+ scenarios

6. Event Catalog (5 min)
   ├─ Scan codebase for event.publish() / event.subscribe()
   ├─ Generate EVENTS.md
   └─ Generate events_catalog.json (85 events)

Total: ~40 minutes
```

**Result:**
- ✅ 6/6 stages complete
- 📊 Generated 15 module reports
- 🧠 Indexed 577 scenarios to Qdrant
- 📋 Cataloged 85 events
- 🚀 Platform became smarter!

---

## 🔮 Будущие улучшения

### Roadmap

**Q1 2025**
- ✅ System Behavior Analyzer
- ✅ Intelligent Module Analyzer
- ✅ Automated Knowledge Pipeline
- ✅ GitHub Actions integration
- ✅ mio-manager scheduler

**Q2 2025**
- [ ] Real-time pattern detection (streaming)
- [ ] Predictive edge case detection (ML model)
- [ ] Auto-fix suggestions (code generation)
- [ ] A/B testing for improvements

**Q3 2025**
- [ ] Multi-language support (TypeScript, Go)
- [ ] Visual system modeling (interactive diagrams)
- [ ] Collaborative learning (multi-tenant)

**Q4 2025**
- [ ] Self-healing capabilities
- [ ] Autonomous optimization
- [ ] Full AGI integration 🤖

---

## 🤝 Contributing

### Добавление нового анализатора

1. Создать `tools/my_analyzer.py`
2. Добавить в `automated_knowledge_pipeline.py`:
   ```python
   async def _stage_my_analysis(self):
       my_analyzer = MyAnalyzer()
       results = await my_analyzer.analyze()
       self.pipeline_state["outputs"]["my_analysis"] = results
   ```
3. Добавить в `pipeline_config.yaml`:
   ```yaml
   stages:
     my_analysis:
       enabled: true
       timeout_seconds: 300
   ```

### Расширение существующего анализатора

Пример: добавить новый тип edge case

```python
# В system_behavior_analyzer.py
async def detect_edge_cases(self):
    edge_cases = []

    # Add your new edge case
    edge_cases.append(EdgeCase(
        case_id="edge_my_case_001",
        description="My custom edge case",
        trigger_conditions=[...],
        severity="high",
        mitigation="How to fix"
    ))

    return edge_cases
```

---

## 📚 Документация

### Связанные документы

- [System Behavior Analyzer](tools/system_behavior_analyzer.py) - State machine modeling
- [Intelligent Module Analyzer](tools/intelligent_module_analyzer.py) - Module deep analysis
- [Pipeline Config](config/pipeline_config.yaml) - Configuration
- [API Routes](api/pipeline_routes.py) - REST API
- [Scheduler](../mio-manager/workflows/knowledge_pipeline_scheduler.py) - Automation

### Comprehensive Platform Docs

📍 `/doc-project/comprehensive-platform-docs/`

- **AI_FOUNDATION_CAPABILITIES.md** (45 KB) - LLM, RAG, ML
- **AI_ORCHESTRATION_CAPABILITIES.md** (38 KB) - Cognitive Loop
- **DOMAIN_EXPERTISE_CAPABILITIES.md** (42 KB) - 14 Specialists
- **PREDICTIVE_INTELLIGENCE_CAPABILITIES.md** (35 KB) - Predictions
- **INFRASTRUCTURE_ORCHESTRATION_COMPLETE.md** (52 KB) - 18 Patterns
- **BUSINESS_PROCESS_SCENARIOS_COMPLETE.md** (78 KB) - 10 Examples
- **ALL_USAGE_SCENARIOS_CATALOG.md** (112 KB) - 570+ Scenarios

---

## ❓ FAQ

**Q: Как часто запускается pipeline?**
A: Ежедневно (02:00 UTC) + на каждый push в main/develop

**Q: Где хранятся результаты?**
A: `infrastructure/AI-office-infrastructure/analytics-specialist/reports/`

**Q: Как добавить свой модуль в анализ?**
A: Положите в `platform-services/`, `intelligent-core/`, или `infrastructure/` - он будет обнаружен автоматически

**Q: Можно ли запустить pipeline локально?**
A: Да! `python3 workflows/automated_knowledge_pipeline.py --full`

**Q: Нужен ли API key для Anthropic?**
A: Для AI-extended scenarios - да. Без него работает, но генерирует меньше сценариев

**Q: Как посмотреть статус запущенного pipeline?**
A: `curl http://localhost:8007/api/v1/pipeline/latest`

---

## 🎉 Итог

Создана **самообучающаяся интеллектуальная система**, которая:

✅ **Изучает саму себя** - анализирует каждый модуль платформы
✅ **Моделирует поведение** - понимает states, transitions, patterns
✅ **Генерирует знания** - создает x1000 сценариев через AI
✅ **Становится экспертом** - накапливает знания BCM/ISO 22301
✅ **Непрерывно улучшается** - предлагает improvements, создает roadmaps
✅ **Автоматизирована** - запускается ежедневно без вмешательства

**Результат: Мега прокаченный эксперт, который не останавливается совершенствоваться! 🚀**

---

*Generated by Automated Knowledge & Intelligence System*
*Version: 1.0.0*
*Last Updated: 2025-10-09*
