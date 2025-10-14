# 🔄 PDCA Lifecycle Manager

**Version**: 1.0.0
**Status**: Production Ready
**Port**: 8060

---

## 🎯 Purpose

**PDCA Lifecycle Manager** - ядро Living PDCA System. Управляет всеми PDCA циклами платформы на 4 уровнях:
- 1️⃣ **MICRO**: Каждое действие пользователя
- 2️⃣ **WORKFLOW**: Полные workflow
- 3️⃣ **ORGANIZATIONAL**: Годовые циклы организаций
- 4️⃣ **PLATFORM**: Эволюция платформы

---

## 🏗️ Architecture

```
PDCA Lifecycle Manager (Port 8060)
├── Core
│   ├── cycle_manager.py       # Управление циклами
│   ├── decorators.py          # @pdca_tracked
│   └── models.py              # Data models
│
├── Levels
│   ├── micro_pdca.py          # Уровень 1: Действия
│   ├── workflow_pdca.py       # Уровень 2: Workflows
│   ├── organizational_pdca.py # Уровень 3: Организации
│   └── platform_pdca.py       # Уровень 4: Платформа
│
├── Knowledge
│   ├── pattern_detector.py    # Detect patterns
│   ├── lesson_extractor.py    # Extract lessons
│   └── knowledge_saver.py     # Save to KB
│
├── Integration
│   ├── workflow_adapter.py    # Workflow Intelligence
│   ├── knowledge_adapter.py   # Learning & Knowledge
│   └── eventbus_adapter.py    # EventBus
│
└── API
    └── routes.py              # REST API
```

---

## 🚀 Quick Start

### Installation

```bash
cd intelligent-core/pdca-lifecycle
pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
# Edit .env with your settings
```

### Run Service

```bash
python main.py
# Service starts on http://localhost:8060
```

---

## 📖 Usage Examples

### 1. Track Micro Action

```python
from pdca_lifecycle import pdca_tracked

@pdca_tracked(level="micro", action="bia_completion")
async def complete_bia(bia_id: str, user_id: str):
    """Каждый BIA автоматически отслеживается как PDCA цикл"""

    # Ваш код (без изменений)
    result = await bia_service.complete(bia_id)

    # PDCA автоматически:
    # - Создаёт цикл PLAN
    # - Отслеживает DO
    # - Валидирует CHECK
    # - Извлекает уроки ACT

    return result

# Результат:
# - Lesson saved: "Hospitals need oxygen for ER"
# - Pattern detected: "RTO=0 for ER processes"
# - Benchmark updated: "Avg BIA time: 12min"
```

### 2. Track Workflow

```python
from pdca_lifecycle import workflow_pdca

@workflow_pdca(workflow_type="certification")
async def certification_workflow(org_id: str):
    """Полный workflow отслеживается как большой PDCA цикл"""

    # Workflow Intelligence logic
    result = await workflow_intelligence.execute(
        workflow="certification",
        org_id=org_id
    )

    # PDCA автоматически извлекает:
    # - Time to complete vs planned
    # - Budget vs actual
    # - Success patterns
    # - Bottlenecks

    return result

# Результат:
# - Lesson: "Training Week 4 > Week 6"
# - Pattern: "AI docs save 40% time"
# - Benchmark: "Certification: 11 weeks avg"
```

### 3. Manual Cycle Creation

```python
from pdca_lifecycle import PDCAManager

manager = PDCAManager()

# Создать цикл
cycle = await manager.create_cycle(
    level="micro",
    action="custom_process",
    context={
        "org_id": "org123",
        "user_id": "user456"
    }
)

# PLAN phase
await manager.plan(
    cycle_id=cycle.id,
    plan_data={
        "goal": "Complete risk assessment",
        "expected_duration": "20 minutes",
        "expected_outcome": "15 risks identified"
    }
)

# DO phase
await manager.do(
    cycle_id=cycle.id,
    execution_data={
        "started_at": datetime.now(),
        "actions": [...]
    }
)

# CHECK phase
result = await manager.check(
    cycle_id=cycle.id,
    actual_outcome={
        "duration": "18 minutes",  # 2min faster!
        "risks_found": 17           # 2 more than expected!
    }
)

# ACT phase (auto-extracts lessons)
lessons = await manager.act(
    cycle_id=cycle.id,
    deviations=result.deviations
)

# Lessons saved automatically
# - Pattern: "Risk assessment faster than expected"
# - Lesson: "User expertise improved"
```

---

## 🔄 4 Levels of PDCA

### Level 1: MICRO (Every Action)

**What**: Every user action is tracked as mini PDCA cycle

**Examples**:
- Create BIA
- Assess risk
- Generate BCP
- Complete training
- Run exercise

**Auto-tracked**:
```python
# Just add decorator
@pdca_tracked(level="micro", action="bia")
async def my_action():
    # Your code unchanged
    pass

# PDCA happens automatically!
```

### Level 2: WORKFLOW (Complete Workflows)

**What**: Full workflows tracked as large PDCA cycles

**Examples**:
- BIA → Risk → BCP → Exercise
- Gap Analysis → Roadmap → Certification
- Incident → Response → Recovery

**Integration**:
```python
# Workflow Intelligence already exists
# Just add PDCA wrapper

from pdca_lifecycle import enable_workflow_pdca

# One-time setup
enable_workflow_pdca(workflow_intelligence_instance)

# All workflows now tracked!
```

### Level 3: ORGANIZATIONAL (Annual Cycles)

**What**: Organizations tracked over years

**Examples**:
- Annual BCM review
- Maturity progression
- Multi-year improvement

**Setup**:
```python
# Auto-start for each organization
await PDCAManager.start_annual_cycle(
    org_id="org123",
    year=2025
)

# Quarterly checks auto-scheduled
# Year-end lessons auto-extracted
```

### Level 4: PLATFORM (Platform Evolution)

**What**: Platform improves itself

**Examples**:
- ML model retraining
- Feature development
- Performance optimization

**Always Running**:
```python
# Platform PDCA runs automatically
# No configuration needed

# Quarterly goals set by AI
# Continuous improvements tracked
# Evolution monitored 24/7
```

---

## 📊 API Reference

### Cycles API

```
POST   /api/v1/cycles                 # Create cycle
GET    /api/v1/cycles/{cycle_id}      # Get cycle
PUT    /api/v1/cycles/{cycle_id}/plan # PLAN phase
PUT    /api/v1/cycles/{cycle_id}/do   # DO phase
PUT    /api/v1/cycles/{cycle_id}/check # CHECK phase
POST   /api/v1/cycles/{cycle_id}/act  # ACT phase (close)
GET    /api/v1/cycles                 # List cycles
```

### Patterns & Lessons API

```
GET    /api/v1/patterns               # Get detected patterns
GET    /api/v1/lessons                # Get extracted lessons
GET    /api/v1/benchmarks             # Get benchmarks
```

### Monitoring API

```
GET    /health                        # Health check
GET    /metrics                       # Prometheus metrics
GET    /api/v1/stats                  # Platform statistics
```

---

## 🔌 Integration Points

### With Workflow Intelligence

```python
from intelligent_core.workflow_intelligence import WorkflowEngine
from pdca_lifecycle import enable_workflow_pdca

# Enable PDCA for all workflows
enable_workflow_pdca(WorkflowEngine)

# All workflows now extract lessons!
```

### With Learning & Knowledge

```python
from intelligent_core.ai_foundation.learning_knowledge import KnowledgeBase
from pdca_lifecycle import PDCAManager

# Auto-save lessons to knowledge base
PDCAManager.on_lesson_extracted(
    callback=lambda lesson: KnowledgeBase.save_lesson(lesson)
)
```

### With EventBus

```python
# PDCA events published automatically
# Subscribe to events:

from infrastructure.eventbus import subscribe

@subscribe("pdca.cycle.completed")
async def on_cycle_complete(event):
    print(f"Cycle completed: {event.cycle_id}")
    print(f"Lessons: {event.lessons}")

@subscribe("pdca.pattern.detected")
async def on_pattern(event):
    print(f"New pattern: {event.pattern.description}")
```

---

## 📈 Metrics & Monitoring

### Key Metrics

```
pdca_cycles_total{level="micro"}            # Total micro cycles
pdca_cycles_total{level="workflow"}         # Total workflow cycles
pdca_cycles_total{level="organizational"}   # Total org cycles
pdca_cycles_total{level="platform"}         # Total platform cycles

pdca_lessons_extracted_total                # Total lessons
pdca_patterns_detected_total                # Total patterns
pdca_knowledge_items_created_total          # Knowledge items

pdca_cycle_duration_seconds{level}          # Cycle duration
pdca_knowledge_reuse_rate                   # Knowledge reuse
```

### Health Dashboard

```bash
# Check health
curl http://localhost:8060/health

# Get statistics
curl http://localhost:8060/api/v1/stats

# Response:
{
  "total_cycles": 1247,
  "active_cycles": 34,
  "lessons_extracted": 892,
  "patterns_detected": 156,
  "knowledge_items": 1048,
  "uptime": "45 days"
}
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/test_micro_pdca.py -v
pytest tests/test_workflow_pdca.py -v
pytest tests/test_integration.py -v

# Coverage
pytest --cov=. --cov-report=html
```

---

## 📝 Configuration

### Environment Variables

```bash
# Service
PORT=8060
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# Integration
WORKFLOW_INTELLIGENCE_URL=http://localhost:8037
KNOWLEDGE_BASE_URL=http://localhost:8025
EVENTBUS_URL=http://localhost:8001

# PDCA Settings
AUTO_CLOSE_CYCLES=true
AUTO_EXTRACT_LESSONS=true
MIN_PATTERN_CONFIDENCE=0.7
```

---

## 🚀 Deployment

### Docker

```bash
# Build
docker build -t pdca-lifecycle .

# Run
docker run -p 8060:8060 pdca-lifecycle
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pdca-lifecycle
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: pdca-lifecycle
        image: pdca-lifecycle:latest
        ports:
        - containerPort: 8060
```

---

## 🔧 Development

### Project Structure

```
pdca-lifecycle/
├── core/
│   ├── __init__.py
│   ├── cycle_manager.py      # Core cycle management
│   ├── decorators.py          # @pdca_tracked decorator
│   └── models.py              # Pydantic models
│
├── levels/
│   ├── micro_pdca.py          # Level 1 logic
│   ├── workflow_pdca.py       # Level 2 logic
│   ├── organizational_pdca.py # Level 3 logic
│   └── platform_pdca.py       # Level 4 logic
│
├── knowledge/
│   ├── pattern_detector.py    # Pattern detection
│   ├── lesson_extractor.py    # Lesson extraction
│   └── knowledge_saver.py     # Save to knowledge base
│
├── integration/
│   ├── workflow_adapter.py    # Workflow Intelligence
│   ├── knowledge_adapter.py   # Knowledge Base
│   └── eventbus_adapter.py    # EventBus
│
├── api/
│   └── routes.py              # FastAPI routes
│
├── tests/
├── main.py                    # Entry point
├── requirements.txt
└── README.md
```

### Adding New Action Type

```python
# 1. Create decorator variant
from pdca_lifecycle.core.decorators import create_pdca_tracker

@create_pdca_tracker(
    level="micro",
    action="my_new_action"
)
async def my_new_action():
    pass

# 2. That's it! PDCA tracking enabled.
```

---

## 📚 Documentation

- [Living PDCA System Architecture](../../docs/LIVING_PDCA_SYSTEM_ARCHITECTURE.md)
- [API Documentation](http://localhost:8060/docs)
- [Integration Guide](docs/INTEGRATION.md)

---

**Built with**: FastAPI + SQLAlchemy + EventBus
**Maintained by**: AI Platform Team
**License**: Proprietary

---

🔄 **Living PDCA System** - платформа, которая становится экспертом через практику!
