# 🔌 Plugin Architecture - Implementation Plan

**Date:** 2025-10-05
**Status:** Ready for Implementation
**Approach:** Domain as Plugin

---

## 🎯 Цель

Разделить платформу на **3 независимых слоя**:

1. **Platform Core** - системные функции (domain-agnostic)
2. **AI Intelligence** - AI компоненты (настраиваются под домен)
3. **Domain Layer** - программная часть (сменяемый plugin)

---

## 📊 Что уже готово (можно использовать)

### ✅ От вашего коллеги

1. **Unified Workflow Engine v2.0** (4,040 lines) - PRODUCTION READY
   - BPMN support
   - PostgreSQL persistence
   - Event-driven architecture
   - AI recommendations framework
   - **Статус:** Domain-agnostic, можно использовать как есть!

2. **ISO 22301 Integration** (35 documents, 283 graph nodes)
   - Knowledge Graph
   - RAG ingestion pipeline
   - Evidence requirements
   - **Статус:** BCM domain knowledge, нужно переместить в domain layer

3. **Database Infrastructure**
   - Supabase connection
   - Migrations applied
   - RLS policies
   - **Статус:** Infrastructure ready, можно использовать

### ✅ Из существующих модулей

1. **ai_platform/** - частично готова структура
   - chief/
   - managers/
   - experts/
   - shared/base classes

2. **ai-office/** - RAG pipeline, learning engine
   - RAG Pipeline (production-ready)
   - Meta Learning Engine
   - PDCA engine
   - Coordinator logic

3. **ai_experts/** - tools, learning, ML
   - Tools framework
   - Self-learning engine
   - ML models

4. **workflow_intelligence/** - case library, learning
   - Case library structure
   - Pattern extraction

---

## 🏗️ Целевая Архитектура

```
AI-Platform-ISO/
│
├── intelligent-core/               # LAYER 1 + 2 (Системный)
│   │
│   ├── platform-core/             # Layer 1: Platform Core (NEW!)
│   │   ├── workflow/              # ← unified-workflow (domain-agnostic)
│   │   ├── learning/              # ← learning-system
│   │   ├── community/             # ← community_intelligence
│   │   ├── collective/            # ← collective
│   │   ├── case-library/          # ← workflow_intelligence/case_library
│   │   └── coordination/          # ← coordination-center
│   │
│   ├── ai-intelligence/           # Layer 2: AI Intelligence (NEW!)
│   │   ├── chief/                 # ← ai_platform/chief
│   │   ├── managers/              # ← ai_platform/managers
│   │   ├── shared/                # Base classes, RAG, ML
│   │   │   ├── base/
│   │   │   ├── rag/               # ← ai-office/core/rag + ai_experts/rag
│   │   │   ├── ml/                # ← ai_experts/ml
│   │   │   └── learning/          # ← ai_experts/learning
│   │   └── api/                   # Platform API
│   │
│   └── ai-orchestration/          # MEGA-BRAIN (exists, needs refactor)
│
├── domains/                        # LAYER 3 (Программный - NEW!)
│   │
│   └── bcm/                       # BCM Domain Plugin
│       ├── experts/               # ← ai_platform/experts/domain
│       │   ├── bia_specialist.py
│       │   ├── risk_analyst.py
│       │   ├── planning_specialist.py
│       │   ├── incident_expert.py
│       │   ├── exercise_designer.py
│       │   ├── compliance_auditor.py
│       │   ├── collective_expert.py
│       │   ├── documentation_expert.py
│       │   ├── knowledge_manager.py
│       │   └── predictive_analyst.py
│       │
│       ├── tools/                 # ← ai_experts/tools
│       │   ├── bia_tools.py
│       │   ├── risk_tools.py
│       │   ├── compliance_tools.py
│       │   └── ...
│       │
│       ├── organs/                # ← ai-office/organs
│       │   ├── impact_oracle.py
│       │   ├── risk_advisor.py
│       │   ├── compliance_guardian.py
│       │   └── ...
│       │
│       ├── knowledge/             # ← ai_experts/knowledge
│       │   ├── iso22301/
│       │   ├── bci_gpg/
│       │   ├── knowledge_graph.py
│       │   └── iso_loader.py
│       │
│       ├── services/              # ← platform-services
│       │   ├── bia-service/
│       │   ├── risk-service/
│       │   ├── compliance-service/
│       │   └── ...
│       │
│       └── domain_config.py       # BCM Domain Plugin Config (NEW!)
│
└── infrastructure/                 # Infrastructure (не меняется)
```

---

## 📋 ПЛАН РЕАЛИЗАЦИИ

### 🎯 Phase 1: Foundation (Week 1) - Базовая структура

#### Task 1.1: Создать структуру Platform Core
**Assigned to:** Agent 1 (Ты - свежий взгляд)
**Complexity:** Medium
**Time:** 1-2 days

```bash
# Создать структуру
mkdir -p intelligent-core/platform-core/{workflow,learning,community,collective,case-library,coordination}

# Переместить domain-agnostic модули (БЕЗ изменения кода!)
mv intelligent-core/unified-workflow → intelligent-core/platform-core/workflow
mv intelligent-core/learning-system → intelligent-core/platform-core/learning
mv intelligent-core/community_intelligence → intelligent-core/platform-core/community
mv intelligent-core/collective → intelligent-core/platform-core/collective
```

**Deliverable:**
- [ ] Структура папок создана
- [ ] Модули перемещены
- [ ] Imports обновлены
- [ ] __init__.py файлы

---

#### Task 1.2: Создать AI Intelligence layer
**Assigned to:** Agent 2 (Коллега - знает workflow)
**Complexity:** Medium
**Time:** 1-2 days

```bash
# Создать структуру
mkdir -p intelligent-core/ai-intelligence/{chief,managers,shared,api}

# Переместить AI компоненты
cp -r intelligent-core/ai_platform/chief → ai-intelligence/chief
cp -r intelligent-core/ai_platform/managers → ai-intelligence/managers

# Создать shared из нескольких источников
mkdir -p ai-intelligence/shared/{base,rag,ml,learning}
```

**Merge plan для shared:**
- `base/` ← `ai_platform/shared/base/`
- `rag/` ← merge `ai-office/core/rag/` + `ai_experts/rag/`
- `ml/` ← `ai_experts/ml/`
- `learning/` ← `ai_experts/learning/` + `ai-office/core/learning/`

**Deliverable:**
- [ ] ai-intelligence структура создана
- [ ] Chief и Managers перемещены
- [ ] Shared компоненты объединены
- [ ] Base classes обновлены

---

#### Task 1.3: Создать BCM Domain plugin структуру
**Assigned to:** Agent 1
**Complexity:** Low
**Time:** 0.5 day

```bash
# Создать domain структуру
mkdir -p domains/bcm/{experts,tools,organs,knowledge,services}

# Создать plugin config (пустой пока)
touch domains/bcm/domain_config.py
touch domains/bcm/__init__.py
```

**Deliverable:**
- [ ] domains/bcm/ структура готова
- [ ] domain_config.py скелет создан

---

### 🎯 Phase 2: Base Classes (Week 1-2) - Фундамент

#### Task 2.1: Создать BaseDomain interface
**Assigned to:** Agent 1
**Complexity:** Medium
**Time:** 1 day

**File:** `intelligent-core/ai-intelligence/shared/base/base_domain.py`

```python
from typing import List, Dict, Type, Optional
from abc import ABC, abstractmethod

class BaseDomain(ABC):
    """Base class для domain plugins"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Domain name (e.g., 'bcm', 'hr', 'finance')"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Domain version"""
        pass

    @abstractmethod
    def get_experts(self) -> List[Type['BaseExpert']]:
        """List of expert classes"""
        pass

    @abstractmethod
    def get_tools(self) -> List[Type['BaseTool']]:
        """List of tool classes"""
        pass

    @abstractmethod
    def get_organs(self) -> List[Type['BaseOrgan']]:
        """List of organ classes"""
        pass

    @abstractmethod
    def get_knowledge_sources(self) -> Dict[str, str]:
        """Knowledge sources (name → path)"""
        pass

    @abstractmethod
    def register(self, platform: 'Platform') -> None:
        """Register domain with platform"""
        pass
```

**Deliverable:**
- [ ] BaseDomain interface создан
- [ ] Типы и абстракции определены
- [ ] Документация написана

---

#### Task 2.2: Обновить BaseExpert для domain support
**Assigned to:** Agent 2
**Complexity:** Medium
**Time:** 1 day

**File:** `intelligent-core/ai-intelligence/shared/base/base_expert.py`

Обновить существующий `ExpertAgent` class:

```python
class BaseExpert:
    """Base class for all domain experts"""

    def __init__(
        self,
        name: str,
        domain: str,  # NEW! (e.g., 'bcm', 'hr')
        specialization: str,
        tools: List['BaseTool'],
        organs: Optional[Dict[str, 'BaseOrgan']] = None,
        # Platform services (injected)
        workflow_engine: Optional['WorkflowEngine'] = None,
        case_library: Optional['CaseLibrary'] = None,
        learning_system: Optional['LearningSystem'] = None,
        rag_pipeline: Optional['RAGPipeline'] = None,
        ml_predictor: Optional['MLPredictor'] = None
    ):
        self.name = name
        self.domain = domain  # NEW!
        self.specialization = specialization
        self.tools = tools
        self.organs = organs or {}

        # Platform services (can be None if not needed)
        self.workflow = workflow_engine
        self.cases = case_library
        self.learning = learning_system
        self.rag = rag_pipeline
        self.ml = ml_predictor
```

**Deliverable:**
- [ ] BaseExpert обновлен
- [ ] Domain field добавлен
- [ ] Platform services injection
- [ ] Backward compatibility

---

#### Task 2.3: Создать Platform class
**Assigned to:** Agent 1
**Complexity:** High
**Time:** 2 days

**File:** `intelligent-core/ai-intelligence/platform.py`

```python
from typing import Optional
from .shared.base import BaseDomain
from .chief import ChiefExecutiveAI
from .managers import GovernanceManager, PlatformManager, DomainManager

class Platform:
    """Main platform class that loads domains"""

    def __init__(self):
        # Managers
        self.governance_manager = GovernanceManager()
        self.platform_manager = PlatformManager()
        self.domain_manager = DomainManager()

        # Chief
        self.chief = ChiefExecutiveAI(
            governance=self.governance_manager,
            platform=self.platform_manager,
            domain=self.domain_manager
        )

        # Platform Core services
        from ..platform_core.workflow import UnifiedWorkflowEngine
        from ..platform_core.case_library import CaseLibrary
        from ..platform_core.learning import LearningSystem

        self.workflow_engine = None  # Initialized per-tenant
        self.case_library = CaseLibrary()
        self.learning_system = LearningSystem()

        # Shared AI services
        from .shared.rag import RAGPipeline
        from .shared.ml import MLPredictor

        self.rag_pipeline = RAGPipeline()
        self.ml_predictor = MLPredictor()

        # Current domain
        self.current_domain: Optional[BaseDomain] = None

    async def load_domain(self, domain: BaseDomain):
        """Load domain plugin"""
        print(f"Loading domain: {domain.name}")

        # Register domain with platform
        domain.register(self)

        self.current_domain = domain
        print(f"✅ Domain {domain.name} loaded!")

    async def switch_domain(self, new_domain: BaseDomain):
        """Switch to different domain"""
        if self.current_domain:
            await self.unload_domain(self.current_domain)
        await self.load_domain(new_domain)

    async def unload_domain(self, domain: BaseDomain):
        """Unload domain"""
        # Cleanup domain resources
        self.domain_manager.clear_experts()
        self.current_domain = None
```

**Deliverable:**
- [ ] Platform class создан
- [ ] Domain loading logic
- [ ] Switch domain logic
- [ ] Platform services initialization

---

### 🎯 Phase 3: BCM Domain Plugin (Week 2-3) - Миграция BCM

#### Task 3.1: Создать BCMDomain config
**Assigned to:** Agent 2
**Complexity:** Medium
**Time:** 1 day

**File:** `domains/bcm/domain_config.py`

```python
from intelligent_core.ai_intelligence.shared.base import BaseDomain
from typing import List, Dict, Type

# Import all BCM experts
from .experts import (
    BIASpecialist,
    RiskAnalyst,
    PlanningSpecialist,
    IncidentExpert,
    ExerciseDesigner,
    ComplianceAuditor,
    CollectiveExpert,
    DocumentationExpert,
    KnowledgeManager,
    PredictiveAnalyst
)

# Import tools
from .tools import (
    BIAAnalysisTool,
    RiskAssessmentTool,
    ComplianceCheckTool,
    # ... all tools
)

# Import organs
from .organs import (
    ImpactOracle,
    RiskAdvisor,
    ComplianceGuardian,
    # ... all organs
)

class BCMDomain(BaseDomain):
    """Business Continuity Management Domain Plugin"""

    @property
    def name(self) -> str:
        return "bcm"

    @property
    def version(self) -> str:
        return "1.0.0"

    def get_experts(self) -> List[Type]:
        return [
            BIASpecialist,
            RiskAnalyst,
            PlanningSpecialist,
            IncidentExpert,
            ExerciseDesigner,
            ComplianceAuditor,
            CollectiveExpert,
            DocumentationExpert,
            KnowledgeManager,
            PredictiveAnalyst
        ]

    def get_tools(self) -> List[Type]:
        return [
            BIAAnalysisTool,
            RiskAssessmentTool,
            ComplianceCheckTool,
            # ... all tools
        ]

    def get_organs(self) -> List[Type]:
        return [
            ImpactOracle,
            RiskAdvisor,
            ComplianceGuardian,
            # ... all organs
        ]

    def get_knowledge_sources(self) -> Dict[str, str]:
        return {
            "iso22301": "domains/bcm/knowledge/iso22301",
            "bci_gpg": "domains/bcm/knowledge/bci_gpg",
            "who_framework": "domains/bcm/knowledge/who_framework"
        }

    def register(self, platform):
        """Register BCM domain with platform"""

        print(f"Registering BCM domain...")

        # Register experts
        for expert_class in self.get_experts():
            expert = expert_class(
                # Inject platform services
                workflow_engine=platform.workflow_engine,
                case_library=platform.case_library,
                learning_system=platform.learning_system,
                rag_pipeline=platform.rag_pipeline,
                ml_predictor=platform.ml_predictor,
                # Domain-specific
                tools=self._get_expert_tools(expert_class),
                organs=self._get_expert_organs(expert_class)
            )
            platform.domain_manager.register_expert(expert)

        # Load knowledge into RAG
        for name, path in self.get_knowledge_sources().items():
            platform.rag_pipeline.load_knowledge_source(name, path)

        print(f"✅ Registered {len(self.get_experts())} experts")
        print(f"✅ Loaded {len(self.get_knowledge_sources())} knowledge sources")
```

**Deliverable:**
- [ ] BCMDomain config полный
- [ ] Experts registration logic
- [ ] Knowledge loading logic

---

#### Task 3.2: Переместить BCM experts
**Assigned to:** Agent 1
**Complexity:** Low
**Time:** 1 day

```bash
# Copy experts (сохраняя код!)
cp intelligent-core/ai_platform/experts/domain/* → domains/bcm/experts/

# Update imports
# Old: from ai_platform.experts.domain import BIASpecialist
# New: from domains.bcm.experts import BIASpecialist
```

**Deliverable:**
- [ ] 10 experts перемещены в domains/bcm/experts/
- [ ] Imports обновлены
- [ ] __init__.py создан

---

#### Task 3.3: Переместить BCM tools
**Assigned to:** Agent 2
**Complexity:** Low
**Time:** 1 day

```bash
# Copy tools
cp intelligent-core/ai_experts/tools/* → domains/bcm/tools/

# Update imports
```

**Deliverable:**
- [ ] Tools перемещены
- [ ] Imports обновлены

---

#### Task 3.4: Переместить BCM organs
**Assigned to:** Agent 1
**Complexity:** Low
**Time:** 1 day

```bash
# Copy organs from ai-office
cp intelligent-core/ai-office/organs/* → domains/bcm/organs/
```

**Deliverable:**
- [ ] Organs перемещены

---

#### Task 3.5: Переместить BCM knowledge
**Assigned to:** Agent 2
**Complexity:** Low
**Time:** 0.5 day

```bash
# Copy ISO 22301 knowledge
cp -r intelligent-core/ai_experts/knowledge/* → domains/bcm/knowledge/
```

**Deliverable:**
- [ ] Knowledge files перемещены
- [ ] Knowledge Graph доступен

---

#### Task 3.6: Переместить BCM services
**Assigned to:** Agent 1
**Complexity:** Medium
**Time:** 1 day

```bash
# Move platform-services to domain
mv platform-services → domains/bcm/services/
```

**Update service dependencies:**
- Services теперь импортируют из `domains.bcm.experts`
- Services используют Platform Core через dependency injection

**Deliverable:**
- [ ] Services перемещены в domains/bcm/
- [ ] Dependencies обновлены

---

### 🎯 Phase 4: Integration & Testing (Week 3-4)

#### Task 4.1: Создать startup script
**Assigned to:** Agent 1
**Complexity:** Low
**Time:** 0.5 day

**File:** `intelligent-core/startup.py`

```python
import asyncio
from ai_intelligence.platform import Platform
from domains.bcm.domain_config import BCMDomain

async def main():
    # Create platform
    platform = Platform()

    # Load BCM domain
    bcm = BCMDomain()
    await platform.load_domain(bcm)

    # Test query
    result = await platform.chief.handle_request(
        query="How do I conduct a BIA for hospital?",
        context={
            "user_id": "test-user",
            "industry": "healthcare",
            "size": "medium"
        }
    )

    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

**Deliverable:**
- [ ] Startup script работает
- [ ] BCM domain загружается
- [ ] Тест запрос проходит

---

#### Task 4.2: Тестирование domain loading
**Assigned to:** Agent 2
**Complexity:** Medium
**Time:** 1 day

**Test scenarios:**
1. Load BCM domain → verify 10 experts registered
2. Query BIA question → verify BIA Specialist responds
3. Query Compliance → verify Compliance Auditor responds
4. Check knowledge loaded → verify ISO 22301 in RAG
5. Unload BCM → verify experts cleared

**Deliverable:**
- [ ] Integration tests написаны
- [ ] Все 5 scenarios pass

---

#### Task 4.3: Тестирование domain switching (optional)
**Assigned to:** Agent 1
**Complexity:** Low
**Time:** 0.5 day

**Test:**
1. Load BCM
2. Query BIA → works
3. Switch to HR domain (mock)
4. Query BIA → not found
5. Query HR question → works

**Deliverable:**
- [ ] Domain switching работает

---

### 🎯 Phase 5: Documentation & Cleanup (Week 4)

#### Task 5.1: Обновить документацию
**Assigned to:** Both
**Complexity:** Low
**Time:** 1 day

**Files to create/update:**
- `PLUGIN_ARCHITECTURE.md` - полное описание
- `domains/bcm/README.md` - BCM domain guide
- `MIGRATION_GUIDE.md` - как перейти от старой архитектуры

**Deliverable:**
- [ ] Документация complete

---

#### Task 5.2: Cleanup старых модулей
**Assigned to:** Agent 1
**Complexity:** Low
**Time:** 0.5 day

```bash
# Переместить в архив
mkdir _archive/
mv intelligent-core/ai-office → _archive/
mv intelligent-core/ai_experts → _archive/
mv intelligent-core/ai_platform → _archive/
```

**Deliverable:**
- [ ] Старые модули в архиве
- [ ] Проект чистый

---

## 📊 Timeline Summary

| Phase | Duration | Agent 1 | Agent 2 |
|-------|----------|---------|---------|
| Phase 1 | Week 1 | 2 days | 2 days |
| Phase 2 | Week 1-2 | 3 days | 2 days |
| Phase 3 | Week 2-3 | 4 days | 3 days |
| Phase 4 | Week 3-4 | 2 days | 2 days |
| Phase 5 | Week 4 | 1 day | 0.5 day |
| **Total** | **4 weeks** | **12 days** | **9.5 days** |

---

## ✅ Success Criteria

### Technical
- [ ] Platform Core domain-agnostic (no BCM references)
- [ ] BCM domain loads successfully
- [ ] 10 BCM experts registered
- [ ] All tools and organs working
- [ ] Knowledge Graph loaded
- [ ] Tests passing

### Architectural
- [ ] Clean separation of layers
- [ ] No circular dependencies
- [ ] Domain можно unload/reload
- [ ] Platform works without domain loaded
- [ ] Easy to add new domain (HR, Finance)

### Code Quality
- [ ] Type hints throughout
- [ ] Docstrings complete
- [ ] Tests coverage > 80%
- [ ] No deprecated imports
- [ ] Clean git history

---

## 🚀 Next Domains (Future)

После BCM можно добавить:

1. **HR Domain** - employee lifecycle, succession planning
2. **Finance Domain** - financial continuity, payment processing
3. **IT Domain** - IT disaster recovery, cyber resilience

Каждый domain = просто новая папка в `domains/`!

---

## 🎯 Immediate Next Steps

1. **Обсудить план** - оба агента должны понять архитектуру
2. **Выбрать задачи** - кто что берет из Phase 1
3. **Начать с Phase 1.1** - создать структуру Platform Core
4. **Параллельно Phase 1.2** - создать AI Intelligence
5. **Синхронизировать** - после каждой фазы

---

**Ready to start?** 🚀
