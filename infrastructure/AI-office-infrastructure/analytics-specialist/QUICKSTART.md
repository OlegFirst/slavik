# 🚀 Quick Start - Automated Knowledge System

**Запустить самообучающуюся систему за 5 минут**

---

## 📋 Требования

```bash
# Python 3.11+
python3 --version

# Зависимости
pip install anthropic sentence-transformers qdrant-client redis pyyaml apscheduler fastapi
```

## ⚡ Быстрый старт

### 1. Установка переменных окружения

```bash
# В .env или export
export ANTHROPIC_API_KEY="sk-ant-..."  # Для AI generation
export QDRANT_URL="http://localhost:6333"
export QDRANT_API_KEY="your-key"
```

### 2. Запуск полного pipeline

```bash
cd /Users/MD/AI-Platform-ISO

# Полный pipeline (все 6 стадий)
python3 infrastructure/AI-office-infrastructure/analytics-specialist/workflows/automated_knowledge_pipeline.py --full
```

**Что произойдет:**
```
🚀 Starting Automated Knowledge Pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Stage 1: System Analysis
   🔍 Analyzing system states...
   Found 15 states, 47 transitions
   🔍 Detecting edge cases...
   Found 8 edge cases
   ✅ system_analysis complete

📊 Stage 2: Pattern Extraction
   🔍 Extracting patterns from Event Bus...
   Found 4 behavioral patterns
   ✅ pattern_extraction complete

📊 Stage 3: Documentation Generation
   📝 Generating user scenarios...
   Generated 45 user scenarios (Gherkin format)
   ✅ documentation_generation complete

📊 Stage 4: Rules Generation
   🔧 Generating Python business rules...
   Generated: generated_rules.py
   🔧 Generating Temporal workflows...
   Generated: generated_workflows.py
   ✅ rules_generation complete

📊 Stage 5: RAG Integration
   📚 Loading comprehensive docs into Qdrant...
   Indexed 7 documents into Qdrant
   📚 Indexing generated scenarios...
   Indexed 45 scenarios
   ✅ rag_integration complete

📊 Stage 6: Event Catalog Generation
   📋 Generating event catalog...
   Cataloged 85 events
   ✅ event_catalog complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Pipeline completed successfully!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 PIPELINE SUMMARY
Stages completed: 6/6
Duration: 2400.00s (~40 min)
Status: ✅ SUCCESS

📁 Outputs:
   system_analysis: {states: 15, transitions: 47, edge_cases: 8}
   pattern_extraction: {patterns: 4, high_frequency: 2}
   documentation_generation: {user_scenarios: 45, ai_docs: 10}
   rules_generation: {python_rules: generated_rules.py, temporal: generated_workflows.py}
   rag_integration: {docs_indexed: 7, scenarios_indexed: 45}
   event_catalog: {events_cataloged: 85}
```

### 3. Анализ всех модулей

```bash
# Глубокий анализ КАЖДОГО модуля (создает мега эксперта)
python3 infrastructure/AI-office-infrastructure/analytics-specialist/tools/intelligent_module_analyzer.py --all
```

**Результат:**
```
infrastructure/AI-office-infrastructure/analytics-specialist/reports/module_analysis/
├── bia-service_analysis.json
├── bia-service_analysis.md
├── risk-service_analysis.json
├── risk-service_analysis.md
├── ai-foundation_analysis.json
├── ai-foundation_analysis.md
└── MASTER_ANALYSIS_REPORT.md  ← Полный обзор платформы
```

### 4. Просмотр результатов

```bash
# Посмотреть мастер-отчет
cat infrastructure/AI-office-infrastructure/analytics-specialist/reports/module_analysis/MASTER_ANALYSIS_REPORT.md

# Посмотреть отчет pipeline
cat infrastructure/AI-office-infrastructure/analytics-specialist/reports/pipeline_report_*.json | jq .
```

---

## 🎯 Основные сценарии

### Сценарий 1: Запуск только анализа

```bash
# Быстрый анализ (без документации и RAG)
python3 infrastructure/AI-office-infrastructure/analytics-specialist/workflows/automated_knowledge_pipeline.py --analyze

# Результат через 10 минут:
# - state_machine.json
# - edge_cases.json
# - behavioral_patterns.json
```

### Сценарий 2: Запуск через API

```bash
# Запустить analytics-specialist
cd infrastructure/AI-office-infrastructure/analytics-specialist
uvicorn main:app --host 0.0.0.0 --port 8007

# Trigger pipeline
curl -X POST http://localhost:8007/api/v1/pipeline/trigger \
  -H "Content-Type: application/json" \
  -d '{"mode": "full", "async_execution": true}'

# Получить run_id
# {"run_id": "pipeline_20251009_120000", "status": "running", ...}

# Проверить статус
curl http://localhost:8007/api/v1/pipeline/status/pipeline_20251009_120000

# Посмотреть последний запуск
curl http://localhost:8007/api/v1/pipeline/latest
```

### Сценарий 3: Настроить автоматический запуск

```python
# В mio-manager/main.py добавить:
from workflows.knowledge_pipeline_scheduler import setup_pipeline_schedules

# При старте
scheduler, pipeline_scheduler = await setup_pipeline_schedules()

# Теперь pipeline будет запускаться:
# - Ежедневно в 02:00 UTC (полный)
# - Каждый час (только анализ)
```

---

## 📊 Что получается на выходе

### 1. System Analysis

**Файл:** `reports/state_machine.json`

```json
{
  "states": {
    "journey_planning": {
      "entry_conditions": ["organization_onboarded", "gap_analysis_completed"],
      "exit_conditions": ["journey_plan_approved"],
      "possible_actions": ["create_journey_plan", "estimate_timeline"]
    },
    "journey_bia_execution": { ... },
    ...
  },
  "transitions": [
    {
      "from_state": "journey_planning",
      "to_state": "journey_bia_execution",
      "trigger": "journey_plan.approved",
      "conditions": ["journey.status === 'planned'"],
      "valid": true
    },
    ...
  ]
}
```

### 2. Edge Cases

**Файл:** `reports/edge_cases.json`

```json
[
  {
    "case_id": "edge_invalid_transition_001",
    "description": "Journey jumps from BIA to Exercise (skips Risk + Plans)",
    "severity": "critical",
    "trigger_conditions": ["bia.completed", "exercise.started", "NO risk.assessment"],
    "expected_behavior": "Saga Pattern enforces: BIA → Risk → Plans → Exercise",
    "mitigation": "Add saga validation: reject exercise.started if risk/plans not complete"
  },
  ...
]
```

### 3. Behavioral Patterns

**Файл:** `reports/behavioral_patterns.json`

```json
[
  {
    "pattern_id": "pattern_bia_to_risk_flow",
    "pattern_type": "user_flow",
    "description": "Standard BIA → Risk Assessment flow (happy path)",
    "frequency": 347,
    "confidence": 0.95,
    "example_traces": [
      {
        "events": [
          "bia.started",
          "bia.processes_identified",
          "bia.mtd_rto_rpo_set",
          "bia.completed",
          "risk.assessment_started"
        ]
      }
    ]
  },
  ...
]
```

### 4. Generated Rules (Python)

**Файл:** `reports/generated_rules.py`

```python
class BusinessRules:
    @staticmethod
    def validate_bia_scope(scope: Dict[str, Any]) -> bool:
        """Rule: BIA must have at least 1 process (from edge_boundary_001)"""
        if not scope.get("processes") or len(scope["processes"]) == 0:
            raise ValueError("BIA scope must include at least 1 process")
        return True

    @staticmethod
    def should_trigger_stuck_intervention(
        no_activity_days: int,
        dashboard_logins: int,
        ai_queries: int
    ) -> bool:
        """Rule: Trigger intervention if workflow stuck 7+ days"""
        if no_activity_days < 7:
            return False
        stuck_signals = sum([
            no_activity_days >= 7,
            dashboard_logins < 3,
            ai_queries == 0
        ])
        return stuck_signals >= 3
```

### 5. Module Analysis

**Файл:** `reports/module_analysis/bia-service_analysis.md`

```markdown
# bia-service - Intelligent Analysis

**Purpose:** Business Impact Analysis - assessing business process criticality and recovery objectives

## 💡 Usage Scenarios

### Base Scenarios (10)
1. Call POST /api/v1/bia/start
2. Call GET /api/v1/bia/{id}
3. Use BIAEngine.calculate_mtd_rto()
...

### AI-Extended Scenarios (120)
1. POST /api/v1/bia/start - normal case
2. POST /api/v1/bia/start - with invalid input
3. POST /api/v1/bia/start - with missing required fields
4. Conduct BIA for healthcare organization
5. Conduct BIA for financial institution
6. Conduct BIA with 100+ processes
...

## 🧠 Domain Expertise

**Domain:** bcm
**Key Concepts:** business, impact, analysis, recovery, rto, rpo, mtd, criticality
**Standards:** ISO 22301, ISO 22313
**Expertise Level:** expert
```

---

## 🔍 Проверка результатов

### Проверить, что все работает

```bash
# 1. Pipeline health
curl http://localhost:8007/api/v1/pipeline/health

# Ожидаемый ответ:
# {"status": "healthy", "components": {"pipeline": "ok", ...}}

# 2. Проверить, что файлы созданы
ls -lh infrastructure/AI-office-infrastructure/analytics-specialist/reports/

# Должно быть:
# - pipeline_report_*.json
# - state_machine.json
# - edge_cases.json
# - behavioral_patterns.json
# - user_scenarios.json
# - generated_rules.py
# - generated_workflows.py
# - module_analysis/ (директория)

# 3. Проверить Qdrant (если настроен)
curl http://localhost:6333/collections

# Должны быть коллекции:
# - platform_capabilities
# - platform_patterns
# - platform_scenarios
```

---

## 🐛 Troubleshooting

### Проблема: Pipeline не запускается

```bash
# Проверить зависимости
pip list | grep -E "anthropic|qdrant|redis|fastapi"

# Установить недостающие
pip install anthropic qdrant-client redis fastapi
```

### Проблема: ANTHROPIC_API_KEY not found

```bash
# Установить API key
export ANTHROPIC_API_KEY="sk-ant-your-key"

# Или запустить без AI
python3 workflows/automated_knowledge_pipeline.py --full --no-ai
```

### Проблема: Qdrant connection failed

```bash
# Запустить Qdrant локально
docker run -p 6333:6333 qdrant/qdrant

# Или пропустить RAG стадию
python3 workflows/automated_knowledge_pipeline.py --analyze
```

---

## 📚 Дальнейшие шаги

1. **Изучить отчеты**
   ```bash
   cat reports/module_analysis/MASTER_ANALYSIS_REPORT.md
   ```

2. **Настроить автоматический запуск**
   - GitHub Actions (уже настроен в `.github/workflows/automated-knowledge-pipeline.yml`)
   - mio-manager scheduler

3. **Интегрировать с RAG**
   - Настроить Qdrant
   - Проверить, что документы индексируются

4. **Использовать сгенерированные правила**
   ```python
   from reports.generated_rules import BusinessRules

   # Validate BIA scope
   BusinessRules.validate_bia_scope(scope)
   ```

5. **Посмотреть edge cases и исправить**
   ```bash
   cat reports/edge_cases.json | jq '.[] | select(.severity == "critical")'
   ```

---

## 💡 Полезные команды

```bash
# Быстрый анализ (10 мин)
python3 workflows/automated_knowledge_pipeline.py --analyze

# Только документация
python3 workflows/automated_knowledge_pipeline.py --docs

# Только RAG индексация
python3 workflows/automated_knowledge_pipeline.py --index

# Полный pipeline с выводом в custom директорию
python3 workflows/automated_knowledge_pipeline.py --full --output /tmp/my_reports

# Анализ конкретного модуля
python3 tools/intelligent_module_analyzer.py --module bia-service

# Проверить конфигурацию
cat config/pipeline_config.yaml

# Tail logs
tail -f automated_knowledge_pipeline.log
```

---

## 🎉 Готово!

Теперь у вас работает **самообучающаяся интеллектуальная система**, которая:

✅ Анализирует саму себя
✅ Генерирует знания (x1000 сценариев)
✅ Обнаруживает проблемы (edge cases)
✅ Предлагает улучшения
✅ Становится экспертом в BCM/ISO 22301

**Следующий шаг:** Посмотрите [README_AUTOMATION.md](README_AUTOMATION.md) для полного понимания системы.

---

*Quick Start Guide v1.0.0*
