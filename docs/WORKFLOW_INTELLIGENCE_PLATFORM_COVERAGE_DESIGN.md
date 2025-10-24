# Workflow Intelligence - Complete Platform Coverage Design

**Module:** `intelligent_core/workflow_intelligence`
**Version:** 2.0.0 (Platform Integration)
**Date:** 2025-10-21
**Status:** Architecture Design Document
**Author:** Claude Code + MD

---

## Executive Summary

**Workflow Intelligence** является центральным "мозговым центром" платформы AI-Platform-ISO, обеспечивающим:
- Интеллектуальное управление всеми workflows платформы
- Обучение на успешных кейсах
- Governance и compliance для всех сервисов
- PDCA continuous improvement для всей платформы

Этот документ определяет **комплексное покрытие платформы** - как workflow_intelligence должен интегрироваться с каждым компонентом системы.

### Текущий Статус

**Сейчас:**
- ✅ 75% complete (core features production-ready)
- ✅ Интеграция с BIA service работает
- ⚠️ Интеграция с остальными 11 BCM services отсутствует
- ⚠️ Интеграция с 10 intelligent_core modules частичная

**После реализации этого дизайна:**
- 🎯 100% platform coverage
- 🎯 Централизованный workflow management для всех 40+ microservices
- 🎯 Единая governance system для всей платформы
- 🎯 Cross-module learning и knowledge sharing

---

## Table of Contents

1. [Platform Architecture Overview](#1-platform-architecture-overview)
2. [Current Integration Status](#2-current-integration-status)
3. [Complete Platform Coverage Map](#3-complete-platform-coverage-map)
4. [Integration Design by Layer](#4-integration-design-by-layer)
5. [Missing Components Implementation](#5-missing-components-implementation)
6. [Service Adapters Design](#6-service-adapters-design)
7. [API Extensions](#7-api-extensions)
8. [Workflow Definitions](#8-workflow-definitions)
9. [Governance Integration](#9-governance-integration)
10. [Implementation Roadmap](#10-implementation-roadmap)

---

## 1. Platform Architecture Overview

### 1.1 5-Layer Platform Architecture

```
┌─────────────────────────────────────────────────────────┐
│ 5. HUMAN INTERFACE LAYER                                │
│    Admin Panel | API Gateway | Mobile PWA (planned)     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│ 4. PLATFORM SERVICES LAYER (12 BCM services)            │
│    bcm_domain/                                           │
│    ├── services/                                         │
│    │   ├── bia_service/          ✅ Has adapter         │
│    │   ├── risk_service/         ❌ NO adapter          │
│    │   ├── compliance_service/   ❌ NO adapter          │
│    │   ├── planning_service/     ❌ NO adapter          │
│    │   ├── training_service/     ❌ NO adapter          │
│    │   ├── exercise_service/     ❌ NO adapter          │
│    │   ├── audit_service/        ❌ NO adapter          │
│    │   └── ... (5 more)                                 │
│    business_monitoring/          ⚠️ EventBus only       │
│    digital_twin/                 ❌ NO integration      │
│    living_docs/                  ❌ NO integration      │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│ 3. INTELLIGENT CORE LAYER (11 AI modules)               │
│    workflow_intelligence/        ← THIS MODULE 🎯       │
│    orchestration/                ⚠️ Separate, should unify│
│    ai_foundation/                ⚠️ Optional dependency │
│    expertise_center/             ⚠️ Partial integration │
│    predictive/                   ❌ NO integration      │
│    collective/                   ❌ NO integration      │
│    scenario_intelligence/        ❌ NO integration      │
│    event_intelligence/           ❌ NO integration      │
│    community_intelligence/       ❌ NO integration      │
│    system_bcm_service/           ❌ NO integration      │
│    workflow_engine/              ❌ Duplicate?          │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│ 2. SHARED LIBRARIES LAYER                                │
│    shared/database               ✅ Fully integrated    │
│    shared/event_bus              ✅ Fully integrated    │
│    shared/auth                   ⚠️ Own auth/ exists    │
│    shared/logging                ⚠️ Own audit/ exists   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│ 1. INFRASTRUCTURE LAYER                                  │
│    EventBus | PostgreSQL | Redis | Prometheus           │
│    ✅ All integrated via storage/ and integration/      │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Workflow Intelligence Role

**Workflow Intelligence** = **Central Brain Center** платформы:

1. **Workflow Management Engine**
   - Управляет всеми workflows платформы (BIA, Risk, Planning, Training, Audit, Exercise, etc.)
   - Универсальный движок, который может работать с любым state machine
   - Единая точка мониторинга всех workflows

2. **Intelligence Layer**
   - AI Advisor дает контекстные советы для всех модулей
   - Case Library учится на успешных executions
   - ML Predictor предсказывает риски и оптимизирует
   - PDCA Engine обеспечивает continuous improvement

3. **Governance Center**
   - Governance v2.0 (Goals + Rules) валидирует всю платформу
   - ISO 22301 compliance checks для всех services
   - Self-monitoring и recursive governance

4. **Integration Hub**
   - Интеграция с всеми BCM services через adapters
   - Интеграция с intelligent_core modules
   - EventBus publisher для platform-wide communication

---

## 2. Current Integration Status

### 2.1 What's Integrated ✅

| Component | Integration Type | Status | Completeness |
|-----------|------------------|--------|--------------|
| **Infrastructure** |
| PostgreSQL | storage/postgres_adapter.py | ✅ Full | 100% |
| Redis | production_modules/cache.py | ✅ Full | 100% |
| EventBus | integration/eventbus_publisher.py | ✅ Full | 100% |
| Prometheus | metrics/process_metrics.py | ✅ Full | 100% |
| **Platform Services** |
| BIA Service | integration/bia_adapter.py | ✅ Full | 90% |
| **Intelligent Core** |
| AI Foundation | integration/ai_context_builder.py | ⚠️ Optional | 50% |
| Expertise Center | temporal_workflows/expertise_workflow.py | ⚠️ Partial | 40% |
| **Shared** |
| shared/database | storage/ usage | ✅ Full | 100% |
| shared/event_bus | main.py, integration/ | ✅ Full | 100% |

### 2.2 What's Missing ❌

| Component | Type | Priority | Reason Missing |
|-----------|------|----------|----------------|
| **BCM Services (11 missing)** |
| Risk Service | Service Adapter | HIGH | No adapter exists |
| Compliance Service | Service Adapter | HIGH | No adapter exists |
| Planning Service | Service Adapter | HIGH | No adapter exists |
| Training Service | Service Adapter | MEDIUM | No adapter exists |
| Exercise Service | Service Adapter | MEDIUM | No adapter exists |
| Audit Service | Service Adapter | MEDIUM | No adapter exists |
| Governance Service | Service Adapter | MEDIUM | No adapter exists |
| Knowledge Quality Manager | Service Adapter | MEDIUM | No adapter exists |
| AI Colleagues | Service Adapter | LOW | No adapter exists |
| Business Monitoring | Integration | MEDIUM | Only EventBus |
| Digital Twin | Integration | LOW | No integration |
| **Intelligent Core (7 missing)** |
| orchestration/ | Unification | HIGH | Separate orchestrator |
| predictive/ | Integration | MEDIUM | No integration |
| collective/ | Integration | MEDIUM | No integration |
| scenario_intelligence/ | Integration | HIGH | No integration |
| event_intelligence/ | Integration | MEDIUM | No integration |
| community_intelligence/ | Integration | LOW | No integration |
| system_bcm_service/ | Integration | MEDIUM | No integration |
| workflow_engine/ | Evaluation | HIGH | Possible duplicate |
| **Workflows (3 missing)** |
| Training workflows | Workflow Definition | MEDIUM | Not implemented |
| Audit workflows | Workflow Definition | MEDIUM | Not implemented |
| Exercise workflows | Workflow Definition | MEDIUM | Not implemented |

### 2.3 Integration Health Score

```
Total Platform Components: 30
  - BCM Services: 12
  - Intelligent Core: 11
  - Shared: 4
  - Infrastructure: 3

Currently Integrated: 7 (23%)
  - Fully: 5 (17%)
  - Partially: 2 (7%)

Missing Integration: 23 (77%)

Integration Health Score: 23/100 🔴
Target Score: 95/100 🎯
```

---

## 3. Complete Platform Coverage Map

### 3.1 Coverage Matrix

| Layer | Component | Current | Target | Gap | Priority |
|-------|-----------|---------|--------|-----|----------|
| **Platform Services Layer** |
| BIA Service | ✅ 90% | 100% | Workflow definitions | MEDIUM |
| Risk Service | ❌ 0% | 100% | Adapter + workflows | HIGH |
| Compliance Service | ❌ 0% | 100% | Adapter + workflows | HIGH |
| Planning Service | ❌ 0% | 100% | Adapter + workflows | HIGH |
| Training Service | ❌ 0% | 90% | Adapter + workflows | MEDIUM |
| Exercise Service | ❌ 0% | 90% | Adapter + workflows | MEDIUM |
| Audit Service | ❌ 0% | 90% | Adapter + workflows | MEDIUM |
| Governance Service | ⚠️ 40% | 100% | Adapter + sync | MEDIUM |
| Knowledge Quality Manager | ❌ 0% | 80% | Adapter | MEDIUM |
| AI Colleagues | ❌ 0% | 70% | Adapter (optional) | LOW |
| Business Monitoring | ⚠️ 30% | 80% | Metrics integration | MEDIUM |
| Digital Twin | ❌ 0% | 60% | Simulation integration | LOW |
| **Intelligent Core Layer** |
| workflow_intelligence | ✅ 75% | 100% | Complete missing parts | HIGH |
| orchestration | ⚠️ 0% | 90% | Unify/integrate | HIGH |
| ai_foundation | ⚠️ 50% | 90% | Full LLM integration | MEDIUM |
| expertise_center | ⚠️ 40% | 90% | Routing integration | MEDIUM |
| predictive | ❌ 0% | 80% | ML pipeline integration | MEDIUM |
| collective | ❌ 0% | 70% | Case library sync | MEDIUM |
| scenario_intelligence | ❌ 0% | 90% | Scenario workflows | HIGH |
| event_intelligence | ❌ 0% | 70% | Event processing | MEDIUM |
| community_intelligence | ❌ 0% | 60% | Community learning | LOW |
| system_bcm_service | ❌ 0% | 80% | System-wide BCM | MEDIUM |
| workflow_engine | ❓ ? | 0% or 100% | Evaluate duplication | HIGH |
| **Shared Layer** |
| shared/database | ✅ 100% | 100% | None | - |
| shared/event_bus | ✅ 100% | 100% | None | - |
| shared/auth | ⚠️ 60% | 100% | Unify with own auth/ | MEDIUM |
| shared/logging | ⚠️ 60% | 100% | Unify with own audit/ | LOW |

**Coverage Summary:**
- **Current Platform Coverage:** 23% (7/30 components)
- **Target Platform Coverage:** 90% (27/30 components)
- **Gap:** 67% (20 components need integration)

---

## 4. Integration Design by Layer

### 4.1 Platform Services Layer Integration

#### 4.1.1 BCM Services Integration Pattern

**Design:** Adapter Pattern (следуя bia_adapter.py)

**Template: Service Adapter**

```python
# integration/risk_adapter.py (example)

from typing import Dict, Any, Optional
import httpx
from shared.event_bus import publish_event

class RiskServiceAdapter:
    """
    Adapter для интеграции workflow_intelligence с Risk Service

    Использование:
        adapter = RiskServiceAdapter(base_url="http://risk-service:8001")
        risk_data = await adapter.get_assessment(assessment_id="risk-123")
        await adapter.create_workflow(org_id="org-456", context={...})
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8001",
        timeout: int = 30
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def get_assessment(self, assessment_id: str) -> Dict[str, Any]:
        """Get risk assessment data"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/assessments/{assessment_id}"
        )
        response.raise_for_status()
        return response.json()

    async def create_workflow(
        self,
        org_id: str,
        context: Dict[str, Any],
        workflow_type: str = "risk_assessment"
    ) -> Dict[str, Any]:
        """Create risk assessment workflow"""
        payload = {
            "organization_id": org_id,
            "workflow_type": workflow_type,
            "context": context,
            "managed_by": "workflow_intelligence"
        }

        response = await self.client.post(
            f"{self.base_url}/api/v1/workflows",
            json=payload
        )
        response.raise_for_status()
        result = response.json()

        # Publish event для platform-wide notification
        await publish_event(
            event_type="workflow.risk_assessment.created",
            data={
                "workflow_id": result["id"],
                "organization_id": org_id,
                "status": "initiated"
            }
        )

        return result

    async def update_workflow_status(
        self,
        workflow_id: str,
        status: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update workflow status"""
        payload = {"status": status}
        if context:
            payload["context"] = context

        response = await self.client.patch(
            f"{self.base_url}/api/v1/workflows/{workflow_id}",
            json=payload
        )
        response.raise_for_status()

        # Publish event
        await publish_event(
            event_type=f"workflow.risk_assessment.{status}",
            data={"workflow_id": workflow_id}
        )

    async def get_workflow_context(
        self,
        workflow_id: str
    ) -> Dict[str, Any]:
        """Get workflow context для AI Advisor"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/workflows/{workflow_id}/context"
        )
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
```

**Нужно создать adapters для:**

1. **risk_adapter.py** - Risk Assessment Service
2. **compliance_adapter.py** - Compliance Service
3. **planning_adapter.py** - BC Planning Service
4. **training_adapter.py** - Training Service
5. **exercise_adapter.py** - Exercise Service
6. **audit_adapter.py** - Audit Service
7. **governance_adapter.py** - Governance Service
8. **knowledge_quality_adapter.py** - Knowledge Quality Manager
9. **business_monitoring_adapter.py** - Business Monitoring
10. **digital_twin_adapter.py** - Digital Twin (optional)

#### 4.1.2 Service Registry Update

**Файл: integration/service_registry.py**

```python
"""
Service Registry для всех BCM services
Централизованный реестр с auto-discovery
"""

from typing import Dict, Optional, Type
from .bia_adapter import BIAServiceAdapter
from .risk_adapter import RiskServiceAdapter
from .compliance_adapter import ComplianceServiceAdapter
from .planning_adapter import PlanningServiceAdapter
from .training_adapter import TrainingServiceAdapter
from .exercise_adapter import ExerciseServiceAdapter
from .audit_adapter import AuditServiceAdapter

class ServiceRegistry:
    """Central registry для всех BCM service adapters"""

    _adapters: Dict[str, Type] = {
        "bia": BIAServiceAdapter,
        "risk": RiskServiceAdapter,
        "compliance": ComplianceServiceAdapter,
        "planning": PlanningServiceAdapter,
        "training": TrainingServiceAdapter,
        "exercise": ExerciseServiceAdapter,
        "audit": AuditServiceAdapter,
    }

    _instances: Dict[str, Any] = {}

    @classmethod
    def get_adapter(cls, service_name: str) -> Any:
        """Get or create adapter instance"""
        if service_name not in cls._instances:
            adapter_class = cls._adapters.get(service_name)
            if not adapter_class:
                raise ValueError(f"Unknown service: {service_name}")
            cls._instances[service_name] = adapter_class()
        return cls._instances[service_name]

    @classmethod
    def list_services(cls) -> list:
        """List all registered services"""
        return list(cls._adapters.keys())

    @classmethod
    async def health_check_all(cls) -> Dict[str, bool]:
        """Check health of all registered services"""
        results = {}
        for service_name in cls._adapters.keys():
            adapter = cls.get_adapter(service_name)
            try:
                await adapter.health_check()
                results[service_name] = True
            except Exception:
                results[service_name] = False
        return results

# Global registry instance
service_registry = ServiceRegistry()
```

### 4.2 Intelligent Core Layer Integration

#### 4.2.1 Orchestration Unification

**Проблема:**
- `intelligent_core/orchestration/` существует отдельно
- `workflow_intelligence/` имеет свой orchestrator
- Дублирование функциональности

**Решение: Унификация**

**Опция A: workflow_intelligence использует orchestration/**
```python
# workflow_intelligence/integration/orchestration_client.py

from intelligent_core.orchestration.ai_orchestration import AIOrchestrator

class OrchestrationIntegration:
    """Integration с platform orchestrator"""

    def __init__(self):
        self.orchestrator = AIOrchestrator()

    async def delegate_workflow(
        self,
        workflow_type: str,
        context: dict
    ):
        """Delegate workflow to platform orchestrator"""
        return await self.orchestrator.execute_workflow(
            workflow_type=workflow_type,
            context=context,
            managed_by="workflow_intelligence"
        )
```

**Опция B: orchestration/ использует workflow_intelligence**
```python
# intelligent_core/orchestration/workflow_intelligence_client.py

from intelligent_core.workflow_intelligence import WorkflowEngine

class WorkflowIntelligenceClient:
    """Client для использования workflow_intelligence из orchestrator"""

    async def execute_intelligent_workflow(
        self,
        module: str,
        workflow_id: str,
        context: dict
    ):
        """Execute workflow через workflow_intelligence"""
        # Use workflow_intelligence as backend
        pass
```

**Рекомендация: Опция A + Опция B (взаимодействие)**
- `orchestration/` - high-level platform orchestration (saga patterns, coordination)
- `workflow_intelligence/` - workflow engine + intelligence layer
- Они взаимодействуют, но не дублируют

#### 4.2.2 AI Foundation Integration

**Цель:** Полная интеграция с LLM для AI Advisor

**Файл: integration/ai_foundation_client.py**

```python
"""
Full integration с AI Foundation для LLM capabilities
"""

from typing import Dict, Any, Optional
from intelligent_core.ai_foundation import LLMClient, EmbeddingClient

class AIFoundationIntegration:
    """Integration с AI Foundation (LLM, embeddings, RAG)"""

    def __init__(self):
        self.llm = LLMClient()
        self.embeddings = EmbeddingClient()

    async def get_contextual_advice(
        self,
        workflow_context: Dict[str, Any],
        similar_cases: list
    ) -> str:
        """Get AI advice using platform LLM"""

        # Build prompt with context
        prompt = self._build_advice_prompt(
            context=workflow_context,
            cases=similar_cases
        )

        # Call LLM через AI Foundation
        response = await self.llm.complete(
            prompt=prompt,
            temperature=0.7,
            max_tokens=1000
        )

        return response.text

    async def embed_case(self, case_text: str) -> list:
        """Generate embeddings для case library"""
        return await self.embeddings.embed(case_text)

    def _build_advice_prompt(
        self,
        context: Dict[str, Any],
        cases: list
    ) -> str:
        """Build prompt template"""
        return f"""
You are a BCM expert AI advisor.

Current workflow context:
{context}

Similar successful cases:
{cases}

Provide contextual advice for next steps.
"""
```

#### 4.2.3 Scenario Intelligence Integration

**Цель:** Использовать scenario_intelligence для advanced scenario generation

**Файл: integration/scenario_intelligence_client.py**

```python
"""
Integration с Scenario Intelligence для AI-powered scenarios
"""

from intelligent_core.scenario_intelligence import ScenarioGenerator

class ScenarioIntelligenceIntegration:
    """Integration с scenario intelligence module"""

    def __init__(self):
        self.generator = ScenarioGenerator()

    async def generate_training_scenarios(
        self,
        org_context: Dict[str, Any],
        difficulty: str = "medium"
    ) -> list:
        """Generate training scenarios для organization"""

        scenarios = await self.generator.generate(
            domain="bcm",
            context=org_context,
            difficulty=difficulty,
            count=5
        )

        return scenarios

    async def generate_exercise_scenario(
        self,
        org_id: str,
        scenario_type: str
    ) -> Dict[str, Any]:
        """Generate exercise scenario"""
        return await self.generator.generate_exercise(
            organization_id=org_id,
            type=scenario_type
        )
```

#### 4.2.4 Predictive Integration

**Цель:** ML predictions для workflows

**Файл: integration/predictive_client.py**

```python
"""
Integration с Predictive module для ML predictions
"""

from intelligent_core.predictive import PredictiveEngine

class PredictiveIntegration:
    """Integration с predictive analytics"""

    def __init__(self):
        self.engine = PredictiveEngine()

    async def predict_workflow_duration(
        self,
        workflow_type: str,
        org_context: Dict[str, Any]
    ) -> float:
        """Predict workflow duration"""
        return await self.engine.predict_duration(
            workflow_type=workflow_type,
            context=org_context
        )

    async def predict_risk_level(
        self,
        workflow_id: str,
        current_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict risk level для workflow"""
        return await self.engine.predict_risk(
            workflow_id=workflow_id,
            state=current_state
        )
```

### 4.3 Shared Layer Unification

#### 4.3.1 Auth Unification

**Проблема:**
- workflow_intelligence имеет собственный `auth/` module
- Platform имеет `shared/auth`

**Решение: Унификация**

```python
# auth/__init__.py (updated)

"""
Auth module - unified с shared/auth
"""

from shared.auth import (
    authenticate_user,
    authorize_action,
    get_current_user,
    create_access_token
)

# Re-export для backward compatibility
__all__ = [
    "authenticate_user",
    "authorize_action",
    "get_current_user",
    "create_access_token"
]

# Keep workflow-specific decorators
from .decorators import require_workflow_permission
from .permissions import check_workflow_access

__all__ += [
    "require_workflow_permission",
    "check_workflow_access"
]
```

---

## 5. Missing Components Implementation

### 5.1 Missing Workflows

#### 5.1.1 Training Workflow

**Файл: workflows/training_workflow.py**

```python
"""
Training Workflow Definition для BCM Training Programs
"""

from infrastructure.process_framework import (
    ProcessDefinition,
    ProcessStep,
    FormField
)

def create_training_workflow() -> ProcessDefinition:
    """
    Create BCM Training workflow definition

    Phases:
    1. Training Needs Assessment
    2. Training Program Design
    3. Training Delivery
    4. Training Evaluation
    5. Continuous Improvement
    """

    return ProcessDefinition(
        id="bcm_training_v1",
        name="BCM Training Program",
        version="1.0",
        description="ISO 22301 Clause 7.2 - Competence & Training",

        steps=[
            ProcessStep(
                id="needs_assessment",
                name="Training Needs Assessment",
                description="Identify competency gaps and training requirements",
                required=True,
                form_fields=[
                    FormField(
                        id="current_competencies",
                        label="Current Staff Competencies",
                        field_type="textarea",
                        required=True,
                        validation={"min_length": 100}
                    ),
                    FormField(
                        id="required_competencies",
                        label="Required Competencies (ISO 22301)",
                        field_type="checklist",
                        required=True,
                        options=[
                            "BIA methodology",
                            "Risk assessment",
                            "BC plan development",
                            "Crisis management",
                            "Exercise planning"
                        ]
                    ),
                    FormField(
                        id="competency_gaps",
                        label="Identified Gaps",
                        field_type="textarea",
                        required=True
                    )
                ],
                validations=[
                    {
                        "rule": "competency_gaps_analysis_complete",
                        "message": "Must analyze all competency areas"
                    }
                ]
            ),

            ProcessStep(
                id="program_design",
                name="Training Program Design",
                description="Design training program based on gaps",
                required=True,
                dependencies=["needs_assessment"],
                form_fields=[
                    FormField(
                        id="training_objectives",
                        label="Training Objectives",
                        field_type="textarea",
                        required=True,
                        help_text="SMART objectives for each competency gap"
                    ),
                    FormField(
                        id="training_methods",
                        label="Training Methods",
                        field_type="multiselect",
                        required=True,
                        options=[
                            "Classroom training",
                            "E-learning modules",
                            "Workshops",
                            "Tabletop exercises",
                            "Simulations",
                            "On-the-job training"
                        ]
                    ),
                    FormField(
                        id="training_schedule",
                        label="Training Schedule",
                        field_type="date_range",
                        required=True
                    ),
                    FormField(
                        id="training_materials",
                        label="Training Materials",
                        field_type="file_upload",
                        required=True,
                        validation={"allowed_types": ["pdf", "pptx", "docx"]}
                    )
                ]
            ),

            ProcessStep(
                id="delivery",
                name="Training Delivery",
                description="Execute training program",
                required=True,
                dependencies=["program_design"],
                form_fields=[
                    FormField(
                        id="participants",
                        label="Training Participants",
                        field_type="user_multiselect",
                        required=True
                    ),
                    FormField(
                        id="attendance_records",
                        label="Attendance Records",
                        field_type="table",
                        required=True
                    ),
                    FormField(
                        id="training_completion",
                        label="Training Completion Status",
                        field_type="percentage",
                        required=True
                    )
                ]
            ),

            ProcessStep(
                id="evaluation",
                name="Training Evaluation",
                description="Evaluate training effectiveness",
                required=True,
                dependencies=["delivery"],
                form_fields=[
                    FormField(
                        id="participant_feedback",
                        label="Participant Feedback (Level 1)",
                        field_type="survey_results",
                        required=True
                    ),
                    FormField(
                        id="knowledge_assessment",
                        label="Knowledge Assessment (Level 2)",
                        field_type="test_results",
                        required=True,
                        validation={"min_pass_rate": 0.70}
                    ),
                    FormField(
                        id="behavior_change",
                        label="Behavior Change (Level 3)",
                        field_type="observation",
                        required=False
                    ),
                    FormField(
                        id="business_impact",
                        label="Business Impact (Level 4)",
                        field_type="metrics",
                        required=False
                    )
                ]
            ),

            ProcessStep(
                id="improvement",
                name="Continuous Improvement",
                description="Apply lessons learned to improve training",
                required=True,
                dependencies=["evaluation"],
                form_fields=[
                    FormField(
                        id="lessons_learned",
                        label="Lessons Learned",
                        field_type="textarea",
                        required=True
                    ),
                    FormField(
                        id="improvement_actions",
                        label="Improvement Actions",
                        field_type="action_items",
                        required=True
                    )
                ]
            )
        ],

        governance_rules=[
            "iso_22301_7_2_competence",
            "training_effectiveness_70_percent"
        ],

        metrics=[
            "training_completion_rate",
            "competency_improvement_score",
            "training_satisfaction_score"
        ]
    )
```

#### 5.1.2 Exercise Workflow

**Файл: workflows/exercise_workflow.py**

```python
"""
Exercise Workflow Definition для BCM Exercises
ISO 22301 Clause 8.5 - Exercise & Testing
"""

def create_exercise_workflow() -> ProcessDefinition:
    """
    Create BCM Exercise workflow definition

    Phases:
    1. Exercise Planning
    2. Exercise Design
    3. Exercise Execution
    4. Exercise Evaluation
    5. Improvement Actions
    """

    return ProcessDefinition(
        id="bcm_exercise_v1",
        name="BCM Exercise Program",
        version="1.0",
        description="ISO 22301 Clause 8.5 - Exercise and testing",

        steps=[
            ProcessStep(
                id="exercise_planning",
                name="Exercise Planning",
                description="Plan exercise scope, objectives, and type",
                required=True,
                form_fields=[
                    FormField(
                        id="exercise_type",
                        label="Exercise Type",
                        field_type="select",
                        required=True,
                        options=[
                            "Tabletop Exercise",
                            "Walkthrough",
                            "Functional Exercise",
                            "Full-Scale Exercise"
                        ]
                    ),
                    FormField(
                        id="exercise_objectives",
                        label="Exercise Objectives",
                        field_type="textarea",
                        required=True,
                        help_text="What capabilities are being tested?"
                    ),
                    FormField(
                        id="scope",
                        label="Exercise Scope",
                        field_type="multiselect",
                        required=True,
                        options=[
                            "BC Plan activation",
                            "Crisis management team",
                            "Communication procedures",
                            "Recovery procedures",
                            "Failover to alternate site"
                        ]
                    )
                ]
            ),

            # ... more steps ...
        ]
    )
```

#### 5.1.3 Audit Workflow

**Файл: workflows/audit_workflow.py**

```python
"""
Audit Workflow Definition для ISO 22301 Internal Audits
ISO 22301 Clause 9.2 - Internal Audit
"""

def create_audit_workflow() -> ProcessDefinition:
    """
    Create Internal Audit workflow definition

    Phases:
    1. Audit Planning
    2. Audit Preparation
    3. Audit Execution
    4. Audit Reporting
    5. Follow-up Actions
    """

    return ProcessDefinition(
        id="bcm_audit_v1",
        name="ISO 22301 Internal Audit",
        version="1.0",
        description="ISO 22301 Clause 9.2 - Internal audit",

        steps=[
            ProcessStep(
                id="audit_planning",
                name="Audit Planning",
                description="Plan audit scope, schedule, and team",
                required=True,
                form_fields=[
                    FormField(
                        id="audit_scope",
                        label="Audit Scope",
                        field_type="checklist",
                        required=True,
                        options=[
                            "Context of organization (4)",
                            "Leadership (5)",
                            "Planning (6)",
                            "Support (7)",
                            "Operation (8)",
                            "Performance evaluation (9)",
                            "Improvement (10)"
                        ]
                    ),
                    FormField(
                        id="audit_criteria",
                        label="Audit Criteria",
                        field_type="text",
                        required=True,
                        default="ISO 22301:2019"
                    ),
                    FormField(
                        id="audit_team",
                        label="Audit Team",
                        field_type="user_multiselect",
                        required=True,
                        validation={"min_members": 1}
                    )
                ]
            ),

            # ... more steps ...
        ]
    )
```

### 5.2 Compliance Module Implementation

**Файл: compliance/iso_checker.py (rewrite)**

```python
"""
ISO 22301 Compliance Checker - FULL IMPLEMENTATION
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ComplianceLevel(Enum):
    FULLY_COMPLIANT = "fully_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "not_applicable"

@dataclass
class ClauseRequirement:
    """ISO 22301 clause requirement"""
    clause: str
    title: str
    description: str
    mandatory_fields: List[str]
    evidence_required: List[str]
    review_frequency_months: Optional[int] = None

@dataclass
class ComplianceCheck:
    """Result of compliance check"""
    clause: str
    level: ComplianceLevel
    score: float  # 0.0 - 1.0
    findings: List[str]
    evidence: List[str]
    gaps: List[str]
    recommendations: List[str]

class ISO22301Checker:
    """
    Complete ISO 22301:2019 compliance checker
    Implements checks for all 10 clauses
    """

    # ISO 22301 Requirements Database
    REQUIREMENTS = {
        "4.1": ClauseRequirement(
            clause="4.1",
            title="Understanding the organization and its context",
            description="Determine external and internal issues relevant to BCMS",
            mandatory_fields=[
                "external_issues",
                "internal_issues",
                "interested_parties",
                "bcms_scope"
            ],
            evidence_required=[
                "Context analysis document",
                "Stakeholder register"
            ],
            review_frequency_months=12
        ),

        "8.2.2": ClauseRequirement(
            clause="8.2.2",
            title="Business Impact Analysis",
            description="BIA to determine priorities for recovery",
            mandatory_fields=[
                "activities_identified",
                "impact_analysis",
                "rto_defined",
                "rpo_defined",
                "mtpd_defined",
                "dependencies_identified"
            ],
            evidence_required=[
                "BIA report",
                "Impact assessment",
                "Recovery objectives"
            ],
            review_frequency_months=6
        ),

        "8.2.3": ClauseRequirement(
            clause="8.2.3",
            title="Risk Assessment",
            description="Risk assessment for disruptions",
            mandatory_fields=[
                "risks_identified",
                "likelihood_assessed",
                "impact_assessed",
                "risk_evaluation",
                "treatment_strategy"
            ],
            evidence_required=[
                "Risk register",
                "Risk assessment report",
                "Treatment plan"
            ],
            review_frequency_months=12
        ),

        "8.3": ClauseRequirement(
            clause="8.3",
            title="Business Continuity Strategy",
            description="BC strategy for protecting and recovering",
            mandatory_fields=[
                "strategy_defined",
                "recovery_options",
                "resource_requirements",
                "strategy_approved"
            ],
            evidence_required=[
                "BC strategy document",
                "Strategy approval"
            ],
            review_frequency_months=12
        ),

        "8.4": ClauseRequirement(
            clause="8.4",
            title="Business Continuity Plans",
            description="BC plans and procedures",
            mandatory_fields=[
                "bc_plans_documented",
                "procedures_defined",
                "roles_assigned",
                "contact_lists",
                "recovery_procedures"
            ],
            evidence_required=[
                "BC plan documents",
                "Procedures",
                "Contact lists"
            ],
            review_frequency_months=6
        ),

        "8.5": ClauseRequirement(
            clause="8.5",
            title="Exercise and Testing",
            description="Exercise and test BC arrangements",
            mandatory_fields=[
                "exercise_program",
                "exercise_objectives",
                "exercise_scenarios",
                "exercise_results",
                "lessons_learned"
            ],
            evidence_required=[
                "Exercise plan",
                "Exercise reports",
                "Improvement actions"
            ],
            review_frequency_months=12
        ),

        "9.1": ClauseRequirement(
            clause="9.1",
            title="Monitoring and Measurement",
            description="Monitor, measure, analyze and evaluate BCMS",
            mandatory_fields=[
                "metrics_defined",
                "monitoring_methods",
                "measurement_results",
                "performance_analysis"
            ],
            evidence_required=[
                "Performance metrics",
                "Measurement results",
                "Analysis reports"
            ],
            review_frequency_months=3
        ),

        "9.2": ClauseRequirement(
            clause="9.2",
            title="Internal Audit",
            description="Conduct internal audits",
            mandatory_fields=[
                "audit_program",
                "audit_criteria",
                "audit_scope",
                "audit_findings",
                "corrective_actions"
            ],
            evidence_required=[
                "Audit plan",
                "Audit reports",
                "Corrective action records"
            ],
            review_frequency_months=12
        ),

        "9.3": ClauseRequirement(
            clause="9.3",
            title="Management Review",
            description="Top management review of BCMS",
            mandatory_fields=[
                "review_agenda",
                "audit_results_reviewed",
                "performance_reviewed",
                "improvement_opportunities",
                "decisions_documented"
            ],
            evidence_required=[
                "Management review minutes",
                "Decisions and actions"
            ],
            review_frequency_months=12
        ),

        "10.1": ClauseRequirement(
            clause="10.1",
            title="Nonconformity and Corrective Action",
            description="React to nonconformity and take corrective action",
            mandatory_fields=[
                "nonconformity_identified",
                "root_cause_analysis",
                "corrective_action_taken",
                "effectiveness_review"
            ],
            evidence_required=[
                "Nonconformity register",
                "Root cause analysis",
                "Corrective action records"
            ],
            review_frequency_months=None  # As needed
        ),

        "10.2": ClauseRequirement(
            clause="10.2",
            title="Continual Improvement",
            description="Continually improve BCMS suitability, adequacy and effectiveness",
            mandatory_fields=[
                "improvement_opportunities",
                "improvement_actions",
                "results_measured"
            ],
            evidence_required=[
                "Improvement register",
                "Action plans",
                "Results"
            ],
            review_frequency_months=6
        )
    }

    async def check_clause(
        self,
        clause: str,
        evidence: Dict[str, Any]
    ) -> ComplianceCheck:
        """
        Check compliance для specific clause

        Args:
            clause: ISO clause number (e.g., "8.2.2")
            evidence: Dictionary с evidence data

        Returns:
            ComplianceCheck с results
        """
        requirement = self.REQUIREMENTS.get(clause)
        if not requirement:
            raise ValueError(f"Unknown clause: {clause}")

        findings = []
        gaps = []
        evidence_list = []

        # Check mandatory fields
        missing_fields = []
        for field in requirement.mandatory_fields:
            if field not in evidence or not evidence[field]:
                missing_fields.append(field)
                gaps.append(f"Missing mandatory field: {field}")
            else:
                evidence_list.append(f"{field}: {evidence[field]}")

        # Check evidence
        missing_evidence = []
        for req_evidence in requirement.evidence_required:
            if not self._has_evidence(evidence, req_evidence):
                missing_evidence.append(req_evidence)
                gaps.append(f"Missing evidence: {req_evidence}")

        # Calculate compliance score
        total_requirements = (
            len(requirement.mandatory_fields) +
            len(requirement.evidence_required)
        )
        missing_count = len(missing_fields) + len(missing_evidence)
        score = 1.0 - (missing_count / total_requirements)

        # Determine compliance level
        if score >= 0.95:
            level = ComplianceLevel.FULLY_COMPLIANT
        elif score >= 0.70:
            level = ComplianceLevel.PARTIALLY_COMPLIANT
        else:
            level = ComplianceLevel.NON_COMPLIANT

        # Generate findings
        if level == ComplianceLevel.FULLY_COMPLIANT:
            findings.append(f"✅ Clause {clause} is fully compliant")
        elif level == ComplianceLevel.PARTIALLY_COMPLIANT:
            findings.append(f"⚠️ Clause {clause} is partially compliant")
        else:
            findings.append(f"❌ Clause {clause} is non-compliant")

        # Generate recommendations
        recommendations = self._generate_recommendations(
            clause, missing_fields, missing_evidence
        )

        return ComplianceCheck(
            clause=clause,
            level=level,
            score=score,
            findings=findings,
            evidence=evidence_list,
            gaps=gaps,
            recommendations=recommendations
        )

    async def check_all_clauses(
        self,
        organization_data: Dict[str, Any]
    ) -> Dict[str, ComplianceCheck]:
        """Check compliance для всех clauses"""
        results = {}
        for clause in self.REQUIREMENTS.keys():
            results[clause] = await self.check_clause(
                clause=clause,
                evidence=organization_data.get(clause, {})
            )
        return results

    async def generate_compliance_report(
        self,
        organization_id: str,
        organization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate complete compliance report"""

        checks = await self.check_all_clauses(organization_data)

        # Calculate overall score
        total_score = sum(check.score for check in checks.values())
        overall_score = total_score / len(checks)

        # Count compliance levels
        fully_compliant = sum(
            1 for check in checks.values()
            if check.level == ComplianceLevel.FULLY_COMPLIANT
        )
        partially_compliant = sum(
            1 for check in checks.values()
            if check.level == ComplianceLevel.PARTIALLY_COMPLIANT
        )
        non_compliant = sum(
            1 for check in checks.values()
            if check.level == ComplianceLevel.NON_COMPLIANT
        )

        return {
            "organization_id": organization_id,
            "overall_score": overall_score,
            "certification_ready": overall_score >= 0.85,
            "summary": {
                "fully_compliant": fully_compliant,
                "partially_compliant": partially_compliant,
                "non_compliant": non_compliant,
                "total_clauses": len(checks)
            },
            "clause_results": checks,
            "priority_actions": self._get_priority_actions(checks),
            "next_review_date": self._calculate_next_review()
        }

    def _has_evidence(
        self,
        evidence: Dict[str, Any],
        required_evidence: str
    ) -> bool:
        """Check if required evidence exists"""
        # Simple check - can be enhanced with document verification
        return "evidence_documents" in evidence and \
               any(required_evidence.lower() in doc.lower()
                   for doc in evidence.get("evidence_documents", []))

    def _generate_recommendations(
        self,
        clause: str,
        missing_fields: List[str],
        missing_evidence: List[str]
    ) -> List[str]:
        """Generate recommendations based on gaps"""
        recommendations = []

        if missing_fields:
            recommendations.append(
                f"Complete missing mandatory fields: {', '.join(missing_fields)}"
            )

        if missing_evidence:
            recommendations.append(
                f"Provide required evidence: {', '.join(missing_evidence)}"
            )

        # Clause-specific recommendations
        if clause == "8.2.2" and "rto_defined" in missing_fields:
            recommendations.append(
                "Conduct BIA interviews to determine Recovery Time Objectives (RTO)"
            )

        if clause == "8.5" and "exercise_program" in missing_fields:
            recommendations.append(
                "Establish exercise program with annual tabletop and biennial full-scale exercises"
            )

        return recommendations

    def _get_priority_actions(
        self,
        checks: Dict[str, ComplianceCheck]
    ) -> List[Dict[str, Any]]:
        """Get priority actions from all checks"""
        actions = []

        # Sort by score (lowest first = highest priority)
        sorted_checks = sorted(
            checks.items(),
            key=lambda x: x[1].score
        )

        for clause, check in sorted_checks[:5]:  # Top 5 priorities
            if check.gaps:
                actions.append({
                    "clause": clause,
                    "priority": "HIGH" if check.score < 0.5 else "MEDIUM",
                    "gaps": check.gaps,
                    "recommendations": check.recommendations
                })

        return actions

    def _calculate_next_review(self) -> str:
        """Calculate next review date based on requirements"""
        from datetime import datetime, timedelta
        # Most frequent review is quarterly (3 months)
        next_review = datetime.now() + timedelta(days=90)
        return next_review.strftime("%Y-%m-%d")
```

### 5.3 ML Training Pipeline

**Файл: ml/training/pipeline.py**

```python
"""
ML Training Pipeline для ML Predictor
Обучение моделей на case library data
"""

from typing import List, Dict, Any
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
import joblib

class MLTrainingPipeline:
    """
    ML training pipeline для workflow predictions

    Models:
    - Duration predictor (regression)
    - Risk predictor (classification)
    - Success predictor (classification)
    """

    def __init__(self, case_library):
        self.case_library = case_library
        self.models = {}

    async def train_duration_predictor(self):
        """Train duration prediction model"""

        # Fetch training data от case library
        cases = await self.case_library.get_all_cases()

        # Prepare features
        X, y = self._prepare_duration_features(cases)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train model
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        model.fit(X_train, y_train)

        # Evaluate
        score = model.score(X_test, y_test)

        # Save model
        self.models['duration_predictor'] = model
        joblib.dump(model, 'models/duration_predictor.pkl')

        return {
            "model": "duration_predictor",
            "score": score,
            "samples": len(cases)
        }

    async def train_risk_predictor(self):
        """Train risk prediction model"""

        cases = await self.case_library.get_all_cases()
        X, y = self._prepare_risk_features(cases)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        model.fit(X_train, y_train)

        score = model.score(X_test, y_test)

        self.models['risk_predictor'] = model
        joblib.dump(model, 'models/risk_predictor.pkl')

        return {
            "model": "risk_predictor",
            "score": score,
            "samples": len(cases)
        }

    def _prepare_duration_features(
        self,
        cases: List[Dict[str, Any]]
    ):
        """Prepare features для duration prediction"""
        X = []
        y = []

        for case in cases:
            features = [
                case.get("org_size", 0),
                case.get("complexity", 0),
                case.get("industry_code", 0),
                len(case.get("steps", [])),
                case.get("team_size", 1)
            ]
            X.append(features)
            y.append(case.get("duration_hours", 0))

        return np.array(X), np.array(y)

    def _prepare_risk_features(
        self,
        cases: List[Dict[str, Any]]
    ):
        """Prepare features для risk prediction"""
        X = []
        y = []

        for case in cases:
            features = [
                case.get("org_size", 0),
                case.get("industry_risk_level", 0),
                case.get("regulatory_complexity", 0),
                case.get("previous_incidents", 0),
                case.get("bcms_maturity", 0)
            ]
            X.append(features)

            # Risk level: 0=low, 1=medium, 2=high
            y.append(case.get("risk_level", 1))

        return np.array(X), np.array(y)
```

---

## 6. Service Adapters Design

### 6.1 Complete Service Adapter List

**Создать следующие adapters:**

| Service | Adapter File | Priority | Base URL | Key Methods |
|---------|--------------|----------|----------|-------------|
| BIA | bia_adapter.py | ✅ Done | :8001 | get_analysis(), create_workflow() |
| Risk | risk_adapter.py | HIGH | :8002 | get_assessment(), create_workflow() |
| Compliance | compliance_adapter.py | HIGH | :8003 | check_compliance(), get_report() |
| Planning | planning_adapter.py | HIGH | :8004 | get_plan(), create_workflow() |
| Training | training_adapter.py | MEDIUM | :8005 | get_program(), schedule_training() |
| Exercise | exercise_adapter.py | MEDIUM | :8006 | create_exercise(), get_results() |
| Audit | audit_adapter.py | MEDIUM | :8007 | schedule_audit(), get_findings() |
| Governance | governance_adapter.py | MEDIUM | :8008 | sync_goals(), sync_rules() |
| Knowledge QM | knowledge_quality_adapter.py | LOW | :8009 | get_knowledge(), quality_check() |
| Business Mon | business_monitoring_adapter.py | MEDIUM | :8010 | get_metrics(), subscribe_events() |

### 6.2 Adapter Template

Все adapters следуют единому template (см. раздел 4.1.1).

---

## 7. API Extensions

### 7.1 New API Endpoints

**Добавить к существующим 28 endpoints:**

```python
# api/service_workflows.py (NEW FILE)

from fastapi import APIRouter, Depends
from integration.service_registry import service_registry

router = APIRouter(prefix="/api/v1/services", tags=["services"])

@router.post("/bia/workflow")
async def create_bia_workflow(
    org_id: str,
    context: dict
):
    """Create BIA workflow через service adapter"""
    adapter = service_registry.get_adapter("bia")
    return await adapter.create_workflow(org_id, context)

@router.post("/risk/workflow")
async def create_risk_workflow(
    org_id: str,
    context: dict
):
    """Create risk assessment workflow"""
    adapter = service_registry.get_adapter("risk")
    return await adapter.create_workflow(org_id, context)

# ... similar for all services ...

@router.get("/health")
async def check_all_services_health():
    """Health check для всех registered services"""
    return await service_registry.health_check_all()

@router.get("/list")
async def list_services():
    """List all integrated BCM services"""
    return {
        "services": service_registry.list_services(),
        "count": len(service_registry.list_services())
    }
```

**New endpoints summary:**
- POST `/api/v1/services/{service}/workflow` - Create workflow для service
- GET `/api/v1/services/{service}/status` - Get service status
- GET `/api/v1/services/health` - Health check всех services
- GET `/api/v1/services/list` - List integrated services
- POST `/api/v1/workflows/cross-service` - Cross-service workflow
- GET `/api/v1/platform/coverage` - Platform coverage report

### 7.2 API Refactoring

**Переместить routes из main.py в api/**

```
api/
├── __init__.py
├── cases.py          # Case Library endpoints
├── governance.py     # Governance endpoints
├── pdca.py           # PDCA endpoints
├── workflows.py      # Workflow endpoints
├── services.py       # Service integration endpoints (NEW)
├── intelligence.py   # Intelligence endpoints (NEW)
└── platform.py       # Platform-wide endpoints (NEW)
```

**main.py должен содержать только:**
- FastAPI app initialization
- Lifespan management
- Route registration
- Middleware setup

---

## 8. Workflow Definitions

### 8.1 Complete Workflow Library

**Текущие workflows:**
1. ✅ BIA workflow (workflows/bia_workflow.py)
2. ✅ Risk assessment workflow (workflows/bcm_processes.py)
3. ✅ BC plan workflow (workflows/bcm_processes.py)
4. ✅ Compliance assessment workflow (workflows/bcm_processes.py)

**Добавить workflows:**
5. ❌ Training workflow (workflows/training_workflow.py) - См. раздел 5.1.1
6. ❌ Exercise workflow (workflows/exercise_workflow.py) - См. раздел 5.1.2
7. ❌ Audit workflow (workflows/audit_workflow.py) - См. раздел 5.1.3
8. ❌ Incident response workflow
9. ❌ Recovery workflow
10. ❌ Supplier management workflow
11. ❌ Awareness & communication workflow
12. ❌ Documentation management workflow

### 8.2 Workflow Registry

**Файл: workflows/registry.py**

```python
"""
Central Workflow Registry
All BCM workflows registered here
"""

from .bia_workflow import create_bia_process
from .bcm_processes import (
    create_risk_assessment_process,
    create_bc_plan_process
)
from .training_workflow import create_training_workflow
from .exercise_workflow import create_exercise_workflow
from .audit_workflow import create_audit_workflow

WORKFLOW_REGISTRY = {
    "bia": create_bia_process,
    "risk_assessment": create_risk_assessment_process,
    "bc_plan": create_bc_plan_process,
    "training": create_training_workflow,
    "exercise": create_exercise_workflow,
    "audit": create_audit_workflow
}

def get_workflow_definition(workflow_type: str):
    """Get workflow definition by type"""
    factory = WORKFLOW_REGISTRY.get(workflow_type)
    if not factory:
        raise ValueError(f"Unknown workflow type: {workflow_type}")
    return factory()

def list_workflows():
    """List all available workflows"""
    return list(WORKFLOW_REGISTRY.keys())
```

---

## 9. Governance Integration

### 9.1 Platform-Wide Governance

**Цель:** Governance v2.0 должен валидировать ВСЮ платформу

**Файл: governance/platform_governance.py**

```python
"""
Platform-Wide Governance
Validates all platform services через workflow_intelligence
"""

from .governance_orchestrator import GovernanceOrchestrator
from integration.service_registry import service_registry

class PlatformGovernance:
    """
    Governance для всей платформы
    Uses workflow_intelligence governance engine
    """

    def __init__(self):
        self.orchestrator = GovernanceOrchestrator()

    async def validate_all_services(self) -> Dict[str, Any]:
        """Validate all BCM services against governance rules"""

        results = {}

        for service_name in service_registry.list_services():
            # Get service workflows
            adapter = service_registry.get_adapter(service_name)
            workflows = await adapter.get_active_workflows()

            # Validate each workflow
            for workflow in workflows:
                validation = await self.orchestrator.validate_workflow(
                    workflow_id=workflow["id"],
                    context=workflow["context"]
                )

                results[f"{service_name}/{workflow['id']}"] = validation

        return {
            "total_workflows": len(results),
            "compliant": sum(1 for r in results.values() if r["compliant"]),
            "violations": sum(len(r["violations"]) for r in results.values()),
            "details": results
        }

    async def generate_platform_governance_report(self) -> Dict[str, Any]:
        """Generate platform-wide governance report"""

        validation_results = await self.validate_all_services()

        return {
            "platform_health": "healthy" if validation_results["violations"] == 0 else "issues",
            "validation_summary": validation_results,
            "recommendations": self._get_platform_recommendations(validation_results)
        }
```

### 9.2 Recursive Governance

**Governance validирует сам себя:**

```python
# In governance_orchestrator.py

async def self_validate(self) -> Dict[str, Any]:
    """
    Self-validation - governance validates itself
    'Eat own dog food' principle
    """

    # Validate governance configuration
    config_validation = await self._validate_governance_config()

    # Validate rules consistency
    rules_validation = await self._validate_rules_consistency()

    # Validate goals alignment
    goals_validation = await self._validate_goals_alignment()

    return {
        "self_validation_passed": all([
            config_validation["valid"],
            rules_validation["valid"],
            goals_validation["valid"]
        ]),
        "config": config_validation,
        "rules": rules_validation,
        "goals": goals_validation
    }
```

---

## 10. Implementation Roadmap

### 10.1 Phase 1: Critical Integrations (2 weeks)

**Priority: HIGH - Production blockers**

**Week 1: Service Adapters**
- [ ] Day 1-2: Create risk_adapter.py, compliance_adapter.py, planning_adapter.py
- [ ] Day 3: Create service_registry.py с all adapters
- [ ] Day 4: Update __init__.py exports
- [ ] Day 5: Write integration tests

**Week 2: API Refactoring + Compliance**
- [ ] Day 1-2: Refactor API structure (move routes из main.py в api/)
- [ ] Day 3-4: Implement full ISO22301Checker (compliance/iso_checker.py)
- [ ] Day 5: Testing и validation

**Deliverables:**
- ✅ 3 core service adapters (Risk, Compliance, Planning)
- ✅ Clean API structure
- ✅ Working compliance module
- ✅ Integration tests passing

### 10.2 Phase 2: Missing Workflows (2 weeks)

**Priority: MEDIUM - Functionality gaps**

**Week 3: Workflow Definitions**
- [ ] Day 1-2: Create training_workflow.py (complete)
- [ ] Day 2-3: Create exercise_workflow.py (complete)
- [ ] Day 4-5: Create audit_workflow.py (complete)

**Week 4: Workflow Integration**
- [ ] Day 1: Create workflow registry
- [ ] Day 2-3: Create service adapters (training, exercise, audit)
- [ ] Day 4: Temporal workflow definitions
- [ ] Day 5: Testing

**Deliverables:**
- ✅ 3 new workflows (Training, Exercise, Audit)
- ✅ Full BCM workflow coverage
- ✅ Workflow registry

### 10.3 Phase 3: Intelligent Core Integration (2 weeks)

**Priority: MEDIUM - Intelligence features**

**Week 5: AI & ML Integration**
- [ ] Day 1-2: Full ai_foundation integration (LLM client)
- [ ] Day 3: Scenario intelligence integration
- [ ] Day 4: Predictive integration
- [ ] Day 5: ML training pipeline setup

**Week 6: Orchestration Unification**
- [ ] Day 1-2: Evaluate orchestration/ vs workflow_intelligence orchestrator
- [ ] Day 3-4: Implement unification (bidirectional integration)
- [ ] Day 5: Testing

**Deliverables:**
- ✅ Full LLM integration (AI Advisor реально работает)
- ✅ ML models trained
- ✅ Orchestration unification complete

### 10.4 Phase 4: Additional Services (1 week)

**Priority: LOW - Nice to have**

**Week 7: Remaining Adapters**
- [ ] Day 1: knowledge_quality_adapter.py
- [ ] Day 2: business_monitoring_adapter.py
- [ ] Day 3: Additional workflows (incident, recovery)
- [ ] Day 4: Collective integration
- [ ] Day 5: Testing + documentation

**Deliverables:**
- ✅ 100% service coverage
- ✅ Additional workflows
- ✅ Complete documentation

### 10.5 Phase 5: Code Quality (1 week)

**Priority: HIGH - Technical debt**

**Week 8: Cleanup**
- [ ] Day 1: Remove code duplication (корневые файлы → infrastructure/)
- [ ] Day 2: Auth/audit unification с shared/
- [ ] Day 3: Improve test coverage (target 80%)
- [ ] Day 4: Performance optimization
- [ ] Day 5: Final documentation update

**Deliverables:**
- ✅ Zero code duplication
- ✅ 80%+ test coverage
- ✅ Clean architecture
- ✅ Production ready

---

## 11. Success Metrics

### 11.1 Integration Metrics

| Metric | Current | Target | Deadline |
|--------|---------|--------|----------|
| **Service Integration** |
| BCM services covered | 1/12 (8%) | 12/12 (100%) | Week 4 |
| Intelligent core modules | 2/11 (18%) | 10/11 (91%) | Week 6 |
| **Code Quality** |
| Code duplication | 2,452 lines | 0 lines | Week 8 |
| Test coverage | ~50% | 80%+ | Week 8 |
| API structure | monolithic | modular | Week 2 |
| **Functionality** |
| Workflows implemented | 4/12 (33%) | 12/12 (100%) | Week 4 |
| ML models trained | 0 | 3 | Week 5 |
| Compliance checks | 10% | 100% | Week 2 |
| **Platform Coverage** |
| Overall coverage | 23% | 95% | Week 8 |

### 11.2 Quality Gates

**Gate 1 (Week 2):**
- ✅ All HIGH priority service adapters created
- ✅ API refactored
- ✅ Compliance module functional
- ✅ Integration tests > 70% pass rate

**Gate 2 (Week 4):**
- ✅ All core workflows implemented
- ✅ Workflow registry complete
- ✅ Service adapters for all workflows
- ✅ Platform coverage > 60%

**Gate 3 (Week 6):**
- ✅ AI/ML fully integrated
- ✅ Orchestration unified
- ✅ Platform coverage > 80%

**Gate 4 (Week 8):**
- ✅ Zero code duplication
- ✅ 80%+ test coverage
- ✅ Platform coverage > 95%
- ✅ Production ready

---

## 12. Architecture Diagrams

### 12.1 Current vs Target Architecture

**CURRENT (23% coverage):**
```
workflow_intelligence
    │
    ├── ✅ PostgreSQL (storage)
    ├── ✅ Redis (cache)
    ├── ✅ EventBus (events)
    ├── ✅ Prometheus (metrics)
    │
    ├── ✅ BIA Service (adapter)
    │
    ├── ⚠️ AI Foundation (partial)
    ├── ⚠️ Expertise Center (partial)
    │
    └── ❌ 11 BCM services (NO adapters)
    └── ❌ 9 intelligent_core modules (NO integration)
```

**TARGET (95% coverage):**
```
workflow_intelligence (CENTRAL BRAIN)
    │
    ├── Infrastructure Layer (100%)
    │   ├── ✅ PostgreSQL
    │   ├── ✅ Redis
    │   ├── ✅ EventBus
    │   └── ✅ Prometheus
    │
    ├── Platform Services Layer (100%)
    │   ├── ✅ BIA Service
    │   ├── ✅ Risk Service
    │   ├── ✅ Compliance Service
    │   ├── ✅ Planning Service
    │   ├── ✅ Training Service
    │   ├── ✅ Exercise Service
    │   ├── ✅ Audit Service
    │   ├── ✅ Governance Service
    │   ├── ✅ Knowledge Quality Manager
    │   ├── ✅ Business Monitoring
    │   └── ✅ Digital Twin
    │
    ├── Intelligent Core Layer (91%)
    │   ├── ✅ AI Foundation (LLM, RAG)
    │   ├── ✅ Orchestration (unified)
    │   ├── ✅ Expertise Center
    │   ├── ✅ Predictive (ML pipeline)
    │   ├── ✅ Collective (case library sync)
    │   ├── ✅ Scenario Intelligence
    │   ├── ✅ Event Intelligence
    │   ├── ✅ System BCM Service
    │   └── ⚠️ Community Intelligence (optional)
    │
    └── Shared Layer (100%)
        ├── ✅ shared/database
        ├── ✅ shared/event_bus
        ├── ✅ shared/auth (unified)
        └── ✅ shared/logging (unified)
```

### 12.2 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│ USER REQUEST                                            │
│ "Start BIA workflow for Hospital X"                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ WORKFLOW INTELLIGENCE API (Port 8037)                   │
│ POST /api/v1/services/bia/workflow                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ├─── Governance Check
                     │    └─> GovernanceOrchestrator validates
                     │
                     ├─── AI Advisor
                     │    └─> ContextAdvisor suggests approach
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ SERVICE ADAPTER                                          │
│ BIAServiceAdapter.create_workflow()                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ├─── Call BIA Service API
                     │    └─> POST http://bia-service:8001/api/v1/workflows
                     │
                     ├─── Publish Event
                     │    └─> EventBus: "workflow.bia.created"
                     │
                     ├─── Store in Case Library
                     │    └─> PostgreSQL: workflow_cases table
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ WORKFLOW ENGINE                                          │
│ - Track workflow execution                               │
│ - PDCA cycle monitoring                                  │
│ - Metrics collection                                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ├─── ML Predictor
                     │    └─> Predict duration, risks
                     │
                     ├─── Prometheus Metrics
                     │    └─> workflow_duration, success_rate
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ PLATFORM INTEGRATION                                     │
│ - Orchestration coordination                             │
│ - EventBus propagation                                   │
│ - Cross-service workflows                                │
└─────────────────────────────────────────────────────────┘
```

---

## 13. Conclusion

### 13.1 Summary

Этот дизайн обеспечивает **полное покрытие платформы** для workflow_intelligence:

**Сейчас:**
- 23% platform coverage (7/30 components integrated)
- Работает только BIA service adapter
- Частичная интеграция с 2 intelligent_core modules

**После реализации:**
- 95% platform coverage (27/30 components integrated)
- Все 12 BCM services integrated через adapters
- 10/11 intelligent_core modules integrated
- Унифицированные shared libraries
- Полный набор workflows (12 workflows)
- ML models trained и работают
- Compliance module реально проверяет ISO 22301

### 13.2 Benefits

1. **Централизованный Workflow Management**
   - Единая точка управления для всех workflows платформы
   - Consistent governance для всех services
   - Cross-service learning через case library

2. **Intelligence для Всей Платформы**
   - AI Advisor для всех BCM services
   - ML predictions для всех workflows
   - PDCA continuous improvement platform-wide

3. **Complete BCM Coverage**
   - Все 12 ISO 22301 workflows покрыты
   - Full compliance checking
   - Automated reporting

4. **Clean Architecture**
   - Zero code duplication
   - Modular API structure
   - Clear separation of concerns
   - 80%+ test coverage

### 13.3 Next Steps

1. **Review этого дизайна** с командой/пользователем
2. **Approve roadmap** (8 weeks)
3. **Start Phase 1** (critical integrations)
4. **Weekly checkpoints** для tracking progress

### 13.4 Investment Required

**Effort Estimation:**
- Phase 1 (Critical): 2 weeks × 1 developer = 80 hours
- Phase 2 (Workflows): 2 weeks × 1 developer = 80 hours
- Phase 3 (Intelligence): 2 weeks × 1 developer = 80 hours
- Phase 4 (Additional): 1 week × 1 developer = 40 hours
- Phase 5 (Quality): 1 week × 1 developer = 40 hours

**Total:** 8 weeks / 320 hours / ~$50K developer time

**ROI:**
- Platform coverage: 23% → 95% (+72%)
- Code quality: 80/100 → 95/100 (+15%)
- Functionality: 33% workflows → 100% workflows (+67%)
- Technical debt: HIGH → LOW
- **Value delivered:** Production-ready central brain для всей платформы

---

**Document Version:** 1.0.0
**Date:** 2025-10-21
**Status:** Design Complete - Awaiting Approval
**Next:** Review + Phase 1 kickoff

---

**Designed by:** Claude Code + MD
**For:** AI-Platform-ISO Workflow Intelligence Module
**Purpose:** Complete Platform Coverage Architecture
