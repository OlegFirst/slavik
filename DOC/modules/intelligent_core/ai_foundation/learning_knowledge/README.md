# 🎓 Unified Learning & Knowledge System

**Version:** 2.0.0
**Status:** ✅ Production-Ready
**Location:** `/intelligent-core/ai-foundation/learning-knowledge/`

---

## 🎯 Vision

**Единая самообучающаяся экосистема платформы**, где:

- 👥 **Люди учатся из опыта AI** - Реальные кейсы → Обучающие материалы
- 🤖 **AI учится из действий людей** - Паттерны → Улучшенные модели
- 📚 **Знания накапливаются** - Стандарты + Кейсы + Паттерны + Уроки
- 🔄 **Платформа эволюционирует** - Каждое действие делает систему умнее

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│          UNIFIED LEARNING & KNOWLEDGE SYSTEM                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📚 KNOWLEDGE CORE                                          │
│  ├── Standards (ISO/BCI/WHO/NIST)                          │
│  ├── Workflow Cases                                        │
│  ├── Vector Search (Qdrant)                                │
│  └── Auto-Update Monitoring                                │
│                                                             │
│  🤖 LEARNING ENGINE                                         │
│  ├── Pattern Detection                                     │
│  ├── ML Self-Learning                                      │
│  ├── Competency Tracking                                   │
│  └── Gamification                                          │
│                                                             │
│  👥 HUMAN TRAINING                                          │
│  ├── Training Programs                                     │
│  ├── Exercises & Simulations                               │
│  ├── Awareness Campaigns                                   │
│  └── Skill Gap Analysis                                    │
│                                                             │
│  🔄 KNOWLEDGE CREATION (Cross-Learning)                     │
│  ├── Patterns → Articles                                   │
│  ├── Cases → Lessons                                       │
│  ├── Standards → Training Materials                        │
│  └── AI ↔ Human Knowledge Synthesis                        │
│                                                             │
│  🌐 UNIFIED API                                             │
│  └── One API for all knowledge & learning needs            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Structure

```
learning-knowledge/
├── knowledge/              # Knowledge Management
│   ├── loader/
│   │   ├── standards_loader.py    # ISO/BCI/WHO/NIST
│   │   └── case_loader.py         # Workflow cases
│   ├── indexer/
│   │   └── vector_indexer.py      # Semantic search
│   └── updater/
│       └── standards_monitor.py    # Auto-updates
│
├── learning/               # Learning Engine
│   ├── engines/
│   │   ├── pattern_detector.py     # Pattern detection
│   │   ├── ml_predictor.py         # ML predictions
│   │   ├── self_learning_engine.py # Self-improving AI
│   │   └── competency_tracker.py   # Competency tracking
│   └── ml/
│       └── models/                 # ML model definitions
│
├── training/               # Human Learning
│   ├── programs/                   # Training programs
│   ├── exercises/                  # Simulations
│   ├── competency/                 # Skill tracking
│   └── gamification/               # Badges & achievements
│
├── creation/               # Knowledge Creation (NEW!)
│   ├── creators/
│   │   ├── article_creator.py      # Auto-create articles
│   │   └── lesson_creator.py       # Cases → Lessons
│   └── synthesis/
│       ├── pattern_to_knowledge.py # Patterns → Knowledge
│       └── case_to_lesson.py       # Cases → Lessons
│
├── api/                    # Unified API
│   ├── main.py                     # FastAPI application
│   ├── knowledge_router.py         # Knowledge endpoints
│   ├── learning_router.py          # Learning endpoints
│   └── training_router.py          # Training endpoints
│
├── integrations/           # Platform Integration
│   ├── workflow_adapter.py         # Workflow engine
│   ├── ai_advisor_adapter.py       # AI advisors
│   └── expertise_adapter.py        # Domain experts
│
├── monitoring/             # Observability
│   ├── metrics.py                  # Prometheus metrics
│   └── analytics.py                # Learning analytics
│
└── tests/                  # Tests
    ├── test_knowledge.py
    ├── test_learning.py
    └── test_integration.py
```

---

## 🚀 Quick Start

### 1. Load Knowledge

```python
from learning_knowledge.knowledge import StandardsLoader, CaseCollector

# Load ISO standard
loader = StandardsLoader()
iso_22301 = await loader.load_iso_standard("iso-22301")

# Collect workflow case
collector = CaseCollector()
case = await collector.collect_workflow_case(
    workflow_id="wf-123",
    module="bia",
    outcome="success",
    organization_context={...},
    metrics={...}
)
```

### 2. Detect Patterns

```python
from learning_knowledge.learning import PatternDetector

# Detect patterns from cases
detector = PatternDetector()
patterns = detector.detect_patterns(exercise_results)

# Patterns: failures, successes, trends, anomalies
```

### 3. Create Training

```python
from learning_knowledge.training import ProgramManager

# Create personalized training
manager = ProgramManager()
program = await manager.create_personalized_program(
    user_id="user123",
    role="bcm_specialist",
    current_competencies={...}
)
```

### 4. Cross-Learning (NEW!)

```python
from learning_knowledge.creation import ArticleCreator

# Auto-create article from patterns
creator = ArticleCreator()
article = await creator.create_from_pattern(
    pattern_id="pattern-123",
    pattern_data={...}
)

# Article saved to knowledge base → Other users learn
```

---

## 🔄 Virtuous Learning Cycle

```
1. User completes BIA workflow
   ↓
2. Case saved to knowledge base
   ↓
3. Pattern detector finds success pattern
   ↓
4. Article creator makes training material
   ↓
5. Other users learn from article
   ↓
6. More users succeed using pattern
   ↓
7. AI model improves predictions
   ↓
8. Platform gets smarter ♻️
```

---

## 📊 Key Features

### Knowledge Management ✅
- ISO/BCI/WHO/NIST standards loading
- Workflow case collection
- Vector semantic search
- Auto-update monitoring
- Case similarity search

### Learning Engine ✅
- Pattern detection (failures, successes, trends)
- ML self-learning models
- Competency tracking
- Process gap analysis
- Gamification (badges, achievements)

### Human Training ✅
- Training program management
- Exercise simulations
- Awareness campaigns
- Skill gap analysis
- Personalized learning paths

### Cross-Learning 🆕
- Patterns → Articles (auto-generation)
- Cases → Lessons (synthesis)
- AI → Human knowledge transfer
- Human → AI learning feedback
- Continuous platform evolution

---

## 🔗 Integration Examples

### With Workflow Engine

```python
# Auto-collect cases on workflow completion
from learning_knowledge.integrations import WorkflowAdapter

adapter = WorkflowAdapter(workflow_engine)
# Cases auto-saved on completion ✅
```

### With AI Experts

```python
# Query knowledge for recommendations
from learning_knowledge.api import UnifiedSearchClient

results = await search.query(
    "ISO 22301 BIA best practices",
    sources=["standards", "cases", "lessons"]
)
```

### With Human Interface

```python
# Get personalized training
from learning_knowledge.training import ProgramManager

program = await manager.get_program_for_user(
    user_id="user123",
    include_gamification=True
)
```

---

## 📈 Metrics & Analytics

### Knowledge Growth
- Standards indexed
- Cases collected
- Articles auto-created
- Lessons synthesized

### Learning Progress
- User competencies improved
- Patterns detected
- Model accuracy increased
- Training completion rates

### Platform Intelligence
- AI recommendation accuracy
- Cross-learning effectiveness
- Knowledge reuse rate
- Time to competency

---

## 🛠️ API Endpoints

### Knowledge API
- `GET /knowledge/standards` - List standards
- `GET /knowledge/standards/{id}` - Get standard
- `GET /knowledge/cases` - List cases
- `POST /knowledge/cases/search` - Search cases

### Learning API
- `GET /learning/patterns` - List patterns
- `POST /learning/predict` - ML prediction
- `GET /learning/competencies/{user_id}` - User competencies

### Training API
- `GET /training/programs` - List programs
- `POST /training/programs` - Create program
- `GET /training/achievements/{user_id}` - User achievements

### Unified Search
- `POST /search` - Search across all sources

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/test_knowledge.py -v
pytest tests/test_learning.py -v
pytest tests/test_integration.py -v
```

---

## 📝 Configuration

### Domains Configuration (`config/domains.yaml`)
```yaml
domains:
  iso:
    standards: [22301, 27001, 31000]
    auto_update: true
  bci:
    sources: [gpg-2018]
  who:
    frameworks: [erf-2023]
```

### Sources Configuration (`config/sources.yaml`)
```yaml
sources:
  iso:
    rss_url: "https://www.iso.org/rss"
    check_interval: 86400
  bci:
    url: "https://www.thebci.org/gpg"
```

---

## 🔄 Migration from Old Systems

This unified system replaces:
- `/intelligent-core/knowledge-system/` → `knowledge/`
- `/intelligent-core/learning-system/` → `learning/`
- `/platform-services/learning-service/` → `training/` (extracted)

All functionality preserved + new cross-learning features added.

---

## 📚 Documentation

- [Design Document](../../../doc-project/UNIFIED_LEARNING_KNOWLEDGE_SYSTEM_DESIGN.md)
- [Migration Guide](#) (TBD)
- [API Reference](#) (TBD)

---

## ✅ Status

**Completion:** 100%
- ✅ Knowledge Core - Complete
- ✅ Learning Engine - Complete
- ✅ Training System - Complete
- ✅ API - Complete
- ✅ Integration - Complete
- ✅ Tests - Complete

**Next:** Deploy & Monitor

---

**Built with:** ❤️ Partnership
**Motto:** "Ничего не потерять - только улучшить!"
