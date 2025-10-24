# Workflow Intelligence - Optimization Action Plan

**Module:** `intelligent_core/workflow_intelligence`
**Current Status:** 75% complete, Production Ready (core features)
**Target:** 95% complete, Full Production Deployment
**Focus:** Internal module optimization (без external integrations)

---

## Executive Summary

Этот план фокусируется ТОЛЬКО на улучшении модуля workflow_intelligence изнутри:
- Устранение дублирования кода
- Рефакторинг структуры
- Реализация недостающих компонентов
- Автоматизация процессов
- Оптимизация производительности

**НЕ включает:** Интеграцию с другими platform services (это отдельный проект).

---

## Current State Analysis

### ✅ Что работает хорошо (не трогать)

1. **core/** - Workflow Engine (1,679 LOC)
   - ✅ Отличная архитектура
   - ✅ Universal state machine protocol
   - ✅ PDCA rules реализованы
   - **Действие:** Оставить как есть

2. **case_library/** - Learning Repository (1,581 LOC)
   - ✅ Автоматический сбор successful cases
   - ✅ PostgreSQL + Qdrant integration
   - ✅ Semantic search
   - **Действие:** Minor improvements only

3. **governance/** - Governance v2.0 (3,497 LOC)
   - ✅ Goals + Rules Engine
   - ✅ 4-level governance
   - ✅ Self-monitoring
   - **Действие:** Оставить как есть

4. **storage/** - Storage Layer (1,573 LOC)
   - ✅ PostgreSQL adapter
   - ✅ Row-Level Security
   - ✅ Async operations
   - **Действие:** Оставить как есть

5. **temporal_workflows/** - Durable Workflows (6,561 LOC)
   - ✅ 9 workflows implemented
   - ✅ Temporal.io integration
   - **Действие:** Оставить как есть

### ⚠️ Что нужно исправить (priority)

| Проблема | Файлов | LOC | Приоритет | Effort |
|----------|--------|-----|-----------|--------|
| **Code Duplication** | 4 | 2,452 | CRITICAL | 4h |
| **API Structure** | 1 | 1,048 | HIGH | 8h |
| **Compliance Stub** | 1 | 222 | HIGH | 16h |
| **ML Missing** | 2 | 191 | MEDIUM | 40h |
| **Missing Workflows** | 0 | 0 | MEDIUM | 24h |
| **Testing** | ~10 | ~1,300 | MEDIUM | 16h |

---

## Action Plan

### Phase 1: Code Cleanup (1 день, 8 hours)

#### Task 1.1: Устранить дублирование кода (4 hours)

**Проблема:**
```
workflow_intelligence/
├── bcm_processes.py (682 строки)              ⚠️ DUPLICATE
├── process_framework.py (547 строк)           ⚠️ DUPLICATE
├── process_orchestration_api.py (626 строк)   ⚠️ DUPLICATE
├── document_templates.py (597 строк)          ⚠️ DUPLICATE
│
├── workflows/bcm_processes.py (682 строки)    ✅ KEEP
├── infrastructure/
│   ├── process_framework/ (547 строк split)   ✅ KEEP
│   ├── orchestration/orchestrator.py (626)    ✅ KEEP
│   └── templates/ (597 строк split)           ✅ KEEP
```

**Действия:**

1. **Удалить корневые файлы** (1h)
   ```bash
   cd /Users/MD/AI-Platform-ISO/intelligent_core/workflow_intelligence

   # Backup first
   mkdir -p _archive/duplicates_backup_$(date +%Y%m%d)
   cp bcm_processes.py _archive/duplicates_backup_$(date +%Y%m%d)/
   cp process_framework.py _archive/duplicates_backup_$(date +%Y%m%d)/
   cp process_orchestration_api.py _archive/duplicates_backup_$(date +%Y%m%d)/
   cp document_templates.py _archive/duplicates_backup_$(date +%Y%m%d)/

   # Remove duplicates
   rm bcm_processes.py
   rm process_framework.py
   rm process_orchestration_api.py
   rm document_templates.py
   ```

2. **Обновить __init__.py exports** (2h)
   ```python
   # __init__.py - UPDATE exports

   # BEFORE (pointing to root files):
   # from .process_framework import ProcessDefinition, ProcessStep

   # AFTER (pointing to infrastructure):
   from .infrastructure.process_framework import (
       ProcessDefinition,
       ProcessStep,
       ProcessInstance,
       ProcessFramework,
       get_process_framework
   )

   from .infrastructure.orchestration import (
       ProcessOrchestrator,
       get_process_orchestrator
   )

   from .infrastructure.templates import (
       DocumentTemplate,
       DocumentTemplateLibrary,
       get_document_library
   )

   from .workflows import (
       create_bia_process,
       create_risk_assessment_process,
       create_bc_plan_process,
       register_all_bcm_processes
   )

   # Update __all__ list accordingly
   ```

3. **Тестирование** (1h)
   ```bash
   # Test imports
   python3 -c "from intelligent_core.workflow_intelligence import ProcessDefinition"
   python3 -c "from intelligent_core.workflow_intelligence import ProcessOrchestrator"
   python3 -c "from intelligent_core.workflow_intelligence import create_bia_process"

   # Run existing tests
   pytest intelligent_core/workflow_intelligence/
   ```

**Deliverable:**
- ✅ -2,452 строки дублированного кода
- ✅ Clean root directory
- ✅ All imports работают
- ✅ Tests passing

#### Task 1.2: Cleanup корневой директории (30 min)

**Текущее состояние:**
```bash
ls -la
# .DS_Store            ⚠️ Remove
# KPI.yaml             ✅ Keep
# README.md            ✅ Keep
# __init__.py          ✅ Keep
# main.py              ✅ Keep
# requirements.txt     ✅ Keep
# setup.py             ✅ Keep
# metrics_exporter.py  ✅ Keep (small utility)
```

**Действия:**
```bash
# Remove .DS_Store
find . -name ".DS_Store" -delete

# Archive old reports (если есть)
mkdir -p _archive/old_reports_$(date +%Y%m%d)
mv *REPORT*.md _archive/old_reports_$(date +%Y%m%d)/ 2>/dev/null || true
```

#### Task 1.3: Update documentation (1.5h)

**Файлы для обновления:**

1. **README.md** - Update структура после удаления duplicates
   ```markdown
   ## Directory Structure

   ```
   workflow_intelligence/
   ├── core/                    # ✅ Workflow Engine
   ├── case_library/            # ✅ Learning Repository
   ├── ai/                      # ✅ AI Advisor
   ├── governance/              # ✅ Governance v2.0
   ├── ml/                      # ⚠️ Stub - ML models
   ├── workflows/               # ✅ BCM Process Definitions
   ├── infrastructure/          # ✅ Process Governance
   │   ├── process_framework/  # Process definition framework
   │   ├── orchestration/      # AI-powered orchestrator
   │   ├── templates/          # Document templates
   │   ├── policies/           # Governance policies
   │   └── monitoring/         # Infrastructure monitoring
   ├── integration/             # ✅ External integrations
   ├── temporal_workflows/      # ✅ Temporal.io workflows
   ├── storage/                 # ✅ Storage adapters
   ├── monitoring/              # ✅ Health monitoring
   ├── metrics/                 # ✅ Metrics collection
   ├── audit/                   # ✅ Audit logging
   ├── auth/                    # ✅ Authentication
   ├── compliance/              # ⚠️ Stub - ISO checker
   ├── schemas/                 # ✅ Pydantic schemas
   ├── examples/                # ✅ Example code
   └── docs/                    # ✅ Documentation
   ```
   ```

2. **CLEANUP_REPORT.md** - Create new cleanup report

**Deliverable:**
- ✅ Updated README.md
- ✅ New CLEANUP_REPORT.md
- ✅ Clean directory structure

---

### Phase 2: API Refactoring (1 день, 8 hours)

#### Task 2.1: Refactor main.py (6h)

**Текущая проблема:**
- main.py = 1,048 строк
- Все 28 API endpoints в одном файле
- Сложность maintenance

**Целевая структура:**
```
api/
├── __init__.py              # Router registration
├── cases.py                 # Case Library endpoints (4)
├── governance.py            # Governance endpoints (5)
├── pdca.py                  # PDCA endpoints (7)
├── workflows.py             # Workflow endpoints (2)
├── health.py                # Health & metrics (3)
└── v1/                      # API versioning (future)
```

**Действия:**

1. **Создать api/cases.py** (1h)
   ```python
   """
   Case Library API endpoints
   """
   from fastapi import APIRouter, HTTPException
   from typing import Dict, Any, List

   router = APIRouter(prefix="/cases", tags=["cases"])

   @router.post("/add")
   async def add_case(case_data: Dict[str, Any]):
       """Add new workflow case"""
       # Move from main.py
       pass

   @router.get("/{case_id}")
   async def get_case(case_id: str):
       """Get workflow case by ID"""
       pass

   @router.post("/search")
   async def search_cases(query: Dict[str, Any]):
       """Search similar cases"""
       pass

   @router.post("/bulk")
   async def bulk_add_cases(cases: List[Dict[str, Any]]):
       """Bulk add cases"""
       pass
   ```

2. **Создать api/governance.py** (1h)
   ```python
   """
   Governance API endpoints
   """
   from fastapi import APIRouter

   router = APIRouter(prefix="/governance", tags=["governance"])

   @router.post("/validate")
   async def validate_workflow(workflow_data: Dict[str, Any]):
       """Validate workflow against governance rules"""
       pass

   @router.get("/summary")
   async def get_governance_summary():
       """Get governance system summary"""
       pass

   @router.get("/goals")
   async def get_goals():
       """Get all goals"""
       pass

   @router.get("/rules")
   async def get_rules():
       """Get all rules"""
       pass

   @router.get("/optimization-suggestions")
   async def get_optimization_suggestions():
       """Get optimization suggestions"""
       pass
   ```

3. **Создать api/pdca.py** (1h)
   ```python
   """
   PDCA API endpoints
   """
   from fastapi import APIRouter

   router = APIRouter(prefix="/pdca", tags=["pdca"])

   @router.get("/status")
   async def get_pdca_status():
       """Get PDCA engine status"""
       pass

   @router.get("/cycles")
   async def get_all_cycles():
       """Get all PDCA cycles"""
       pass

   @router.get("/cycles/{workflow_id}")
   async def get_workflow_cycles(workflow_id: str):
       """Get PDCA cycles for workflow"""
       pass

   @router.get("/benchmarks/{module}")
   async def get_benchmarks(module: str):
       """Get benchmarks by module"""
       pass

   @router.get("/patterns")
   async def get_patterns():
       """Get detected patterns"""
       pass

   @router.get("/lessons")
   async def get_lessons_learned():
       """Get lessons learned"""
       pass

   @router.get("/statistics")
   async def get_statistics():
       """Get PDCA statistics"""
       pass
   ```

4. **Создать api/workflows.py** (1h)
   ```python
   """
   Workflow Analysis API endpoints
   """
   from fastapi import APIRouter

   router = APIRouter(tags=["workflows"])

   @router.post("/analyze")
   async def analyze_workflow(context: Dict[str, Any]):
       """Analyze workflow context"""
       pass

   @router.post("/recommend")
   async def recommend_actions(workflow_id: str):
       """Recommend next actions"""
       pass
   ```

5. **Создать api/health.py** (30min)
   ```python
   """
   Health & Metrics API endpoints
   """
   from fastapi import APIRouter

   router = APIRouter(tags=["health"])

   @router.get("/health")
   async def health_check():
       """Health check"""
       return {"status": "healthy"}

   @router.get("/info")
   async def get_info():
       """Get service info"""
       pass

   @router.get("/metrics")
   async def get_metrics():
       """Get Prometheus metrics"""
       pass
   ```

6. **Обновить api/__init__.py** (30min)
   ```python
   """
   API Router Registration
   """
   from fastapi import APIRouter
   from . import cases, governance, pdca, workflows, health

   # Create main router
   api_router = APIRouter()

   # Include all sub-routers
   api_router.include_router(cases.router)
   api_router.include_router(governance.router)
   api_router.include_router(pdca.router)
   api_router.include_router(workflows.router)
   api_router.include_router(health.router)

   __all__ = ["api_router"]
   ```

7. **Упростить main.py** (1h)
   ```python
   """
   Workflow Intelligence Service - Main Entry Point
   Port: 8037
   """
   from fastapi import FastAPI
   from contextlib import asynccontextmanager
   import asyncio

   from api import api_router
   from core import event_bus
   from governance import GovernanceOrchestrator
   from core.pdca_rules import PDCAEngine

   # Lifespan management
   @asynccontextmanager
   async def lifespan(app: FastAPI):
       # Startup
       print("🚀 Starting Workflow Intelligence Service...")

       # Initialize components
       governance_orchestrator = GovernanceOrchestrator()
       pdca_engine = PDCAEngine()

       # Start self-monitoring
       async def self_monitor():
           while True:
               await asyncio.sleep(60)
               health = await governance_orchestrator.check_system_health()
               print(f"📊 System health: {health}")

       monitoring_task = asyncio.create_task(self_monitor())

       yield

       # Shutdown
       monitoring_task.cancel()
       print("🛑 Stopping Workflow Intelligence Service...")

   # Create app
   app = FastAPI(
       title="Workflow Intelligence API",
       version="1.0.0",
       lifespan=lifespan
   )

   # Include API router
   app.include_router(api_router, prefix="/api/v1")

   # Root endpoint
   @app.get("/")
   async def root():
       return {
           "service": "Workflow Intelligence",
           "version": "1.0.0",
           "status": "running"
       }

   if __name__ == "__main__":
       import uvicorn
       uvicorn.run(app, host="0.0.0.0", port=8037)
   ```

**Deliverable:**
- ✅ main.py: 1,048 строк → ~150 строк (85% reduction)
- ✅ Modular API structure
- ✅ Easy to add new endpoints
- ✅ Better code organization

#### Task 2.2: Тестирование refactored API (2h)

```bash
# Start service
python main.py

# Test all endpoints
curl http://localhost:8037/
curl http://localhost:8037/api/v1/health
curl http://localhost:8037/api/v1/cases/search -X POST -d '{}'
curl http://localhost:8037/api/v1/governance/summary
curl http://localhost:8037/api/v1/pdca/status

# OpenAPI docs
open http://localhost:8037/docs
```

---

### Phase 3: Compliance Implementation (2 дня, 16 hours)

#### Task 3.1: Реализовать ISO22301Checker (12h)

**Текущее состояние:**
- compliance/iso_checker.py = 222 строки stub
- Mostly TODO placeholders
- Нет реальных checks

**Целевое состояние:**
- Full ISO 22301:2019 compliance checker
- All 11 clauses with real checks
- Automated gap analysis
- Compliance reports

**Файл:** compliance/iso_checker.py

Полный код уже есть в дизайн-документе (WORKFLOW_INTELLIGENCE_PLATFORM_COVERAGE_DESIGN.md, раздел 5.2).

**Действия:**

1. **Заменить stub на full implementation** (8h)
   - Copy code from design doc
   - Add all 11 clause requirements
   - Implement check_clause() method
   - Implement check_all_clauses() method
   - Implement generate_compliance_report() method

2. **Добавить тесты** (2h)
   ```python
   # tests/test_compliance.py

   import pytest
   from compliance.iso_checker import ISO22301Checker, ComplianceLevel

   @pytest.mark.asyncio
   async def test_bia_clause_full_compliance():
       checker = ISO22301Checker()

       evidence = {
           "activities_identified": True,
           "impact_analysis": {"critical": 5, "major": 10},
           "rto_defined": "4 hours",
           "rpo_defined": "1 hour",
           "mtpd_defined": "24 hours",
           "dependencies_identified": ["IT", "HR", "Finance"],
           "evidence_documents": [
               "BIA Report",
               "Impact assessment",
               "Recovery objectives"
           ]
       }

       result = await checker.check_clause("8.2.2", evidence)

       assert result.level == ComplianceLevel.FULLY_COMPLIANT
       assert result.score >= 0.95
       assert len(result.gaps) == 0

   @pytest.mark.asyncio
   async def test_bia_clause_non_compliance():
       checker = ISO22301Checker()

       evidence = {
           "activities_identified": True
           # Missing everything else
       }

       result = await checker.check_clause("8.2.2", evidence)

       assert result.level == ComplianceLevel.NON_COMPLIANT
       assert result.score < 0.50
       assert len(result.gaps) > 0

   @pytest.mark.asyncio
   async def test_full_compliance_report():
       checker = ISO22301Checker()

       org_data = {
           "8.2.2": {  # BIA clause
               "activities_identified": True,
               "impact_analysis": {},
               "rto_defined": "4h",
               "rpo_defined": "1h",
               "mtpd_defined": "24h",
               "dependencies_identified": [],
               "evidence_documents": ["BIA Report"]
           }
           # ... other clauses ...
       }

       report = await checker.generate_compliance_report(
           organization_id="test-org-123",
           organization_data=org_data
       )

       assert "overall_score" in report
       assert "certification_ready" in report
       assert "summary" in report
       assert "clause_results" in report
   ```

3. **Интеграция с API** (2h)
   ```python
   # api/compliance.py (NEW FILE)

   from fastapi import APIRouter, HTTPException
   from compliance.iso_checker import ISO22301Checker

   router = APIRouter(prefix="/compliance", tags=["compliance"])

   @router.post("/check-clause")
   async def check_clause(clause: str, evidence: dict):
       """Check compliance for specific ISO clause"""
       checker = ISO22301Checker()
       result = await checker.check_clause(clause, evidence)
       return result

   @router.post("/full-report")
   async def generate_full_report(org_id: str, org_data: dict):
       """Generate full compliance report"""
       checker = ISO22301Checker()
       report = await checker.generate_compliance_report(org_id, org_data)
       return report

   @router.get("/requirements")
   async def get_requirements():
       """Get all ISO 22301 requirements"""
       checker = ISO22301Checker()
       return checker.REQUIREMENTS
   ```

**Deliverable:**
- ✅ Full ISO 22301 compliance checker
- ✅ 11 clauses with real checks
- ✅ Automated reports
- ✅ API endpoints
- ✅ Unit tests

#### Task 3.2: Integration с Governance (2h)

**Цель:** Connect compliance checker с governance/rules_engine_v2.py

```python
# governance/compliance_integration.py (NEW FILE)

from compliance.iso_checker import ISO22301Checker
from .rules_engine_v2 import RulesEngineV2

class ComplianceGovernanceIntegration:
    """
    Integration между Compliance и Governance
    """

    def __init__(self):
        self.compliance_checker = ISO22301Checker()
        self.rules_engine = RulesEngineV2()

    async def validate_with_compliance(
        self,
        workflow_id: str,
        workflow_data: dict
    ) -> dict:
        """
        Validate workflow against both governance rules AND ISO compliance
        """

        # Governance validation
        governance_result = await self.rules_engine.validate(workflow_data)

        # Compliance validation (для BCM workflows)
        compliance_result = None
        if workflow_data.get("module") in ["bia", "risk", "planning"]:
            clause = self._get_relevant_clause(workflow_data["module"])
            compliance_result = await self.compliance_checker.check_clause(
                clause=clause,
                evidence=workflow_data.get("evidence", {})
            )

        return {
            "governance": governance_result,
            "compliance": compliance_result,
            "overall_valid": (
                governance_result["valid"] and
                (compliance_result is None or compliance_result.score >= 0.70)
            )
        }

    def _get_relevant_clause(self, module: str) -> str:
        """Map module to ISO clause"""
        mapping = {
            "bia": "8.2.2",
            "risk": "8.2.3",
            "planning": "8.4"
        }
        return mapping.get(module, "4.1")
```

**Deliverable:**
- ✅ Governance + Compliance unified validation
- ✅ ISO checks в workflow validation

#### Task 3.3: Documentation (2h)

```markdown
# docs/COMPLIANCE_MODULE.md (NEW FILE)

# ISO 22301 Compliance Module

## Overview

Full implementation ISO 22301:2019 compliance checker.

## Features

- ✅ All 11 clauses implemented
- ✅ Automated gap analysis
- ✅ Compliance reports generation
- ✅ Integration with Governance Engine

## Usage

### Check Single Clause

```python
from compliance.iso_checker import ISO22301Checker

checker = ISO22301Checker()

evidence = {
    "activities_identified": True,
    "rto_defined": "4 hours",
    # ... other fields
}

result = await checker.check_clause("8.2.2", evidence)
print(f"Compliance level: {result.level}")
print(f"Score: {result.score}")
print(f"Gaps: {result.gaps}")
```

### Generate Full Report

```python
report = await checker.generate_compliance_report(
    organization_id="org-123",
    organization_data={
        "8.2.2": {...},  # BIA evidence
        "8.2.3": {...},  # Risk evidence
        # ... other clauses
    }
)

print(f"Overall score: {report['overall_score']}")
print(f"Certification ready: {report['certification_ready']}")
```

## API Endpoints

- POST `/api/v1/compliance/check-clause` - Check single clause
- POST `/api/v1/compliance/full-report` - Generate full report
- GET `/api/v1/compliance/requirements` - Get all requirements
```

---

### Phase 4: ML Pipeline (5 дней, 40 hours)

#### Task 4.1: ML Training Infrastructure (16h)

**Создать:** ml/training/

**Структура:**
```
ml/
├── __init__.py
├── cross_module_learning.py (existing)
├── predictor.py (NEW - реализовать)
├── training/
│   ├── __init__.py
│   ├── pipeline.py (NEW)
│   ├── feature_engineering.py (NEW)
│   ├── model_versioning.py (NEW)
│   └── evaluation.py (NEW)
└── models/
    ├── duration_predictor.pkl
    ├── risk_predictor.pkl
    └── success_predictor.pkl
```

**Код уже есть в дизайне** (WORKFLOW_INTELLIGENCE_PLATFORM_COVERAGE_DESIGN.md, раздел 5.3).

**Действия:**

1. **Создать ml/training/pipeline.py** (8h)
   - Copy from design doc
   - Implement MLTrainingPipeline class
   - train_duration_predictor()
   - train_risk_predictor()
   - train_success_predictor()

2. **Создать ml/predictor.py** (4h)
   ```python
   """
   ML Predictor - Production prediction service
   """
   import joblib
   from typing import Dict, Any
   import numpy as np

   class MLPredictor:
       """Production ML prediction service"""

       def __init__(self):
           self.models = {}
           self._load_models()

       def _load_models(self):
           """Load trained models"""
           try:
               self.models['duration'] = joblib.load('ml/models/duration_predictor.pkl')
               self.models['risk'] = joblib.load('ml/models/risk_predictor.pkl')
               self.models['success'] = joblib.load('ml/models/success_predictor.pkl')
           except FileNotFoundError:
               print("⚠️ Models not found. Run training first.")

       async def predict_duration(
           self,
           workflow_type: str,
           org_context: Dict[str, Any]
       ) -> float:
           """Predict workflow duration in hours"""
           if 'duration' not in self.models:
               return 24.0  # Default fallback

           features = self._extract_features(workflow_type, org_context)
           prediction = self.models['duration'].predict([features])[0]
           return float(prediction)

       async def predict_risk(
           self,
           workflow_id: str,
           current_state: Dict[str, Any]
       ) -> Dict[str, Any]:
           """Predict risk level for workflow"""
           if 'risk' not in self.models:
               return {"level": "medium", "confidence": 0.5}

           features = self._extract_risk_features(current_state)
           prediction = self.models['risk'].predict([features])[0]
           proba = self.models['risk'].predict_proba([features])[0]

           risk_levels = ["low", "medium", "high"]
           return {
               "level": risk_levels[prediction],
               "confidence": float(max(proba)),
               "probabilities": {
                   "low": float(proba[0]),
                   "medium": float(proba[1]),
                   "high": float(proba[2])
               }
           }

       def _extract_features(self, workflow_type, context):
           """Extract features from context"""
           return np.array([
               context.get("org_size", 100),
               context.get("complexity", 5),
               context.get("industry_code", 0),
               len(context.get("required_steps", [])),
               context.get("team_size", 3)
           ])

       def _extract_risk_features(self, state):
           """Extract risk features"""
           return np.array([
               state.get("org_size", 100),
               state.get("industry_risk_level", 1),
               state.get("regulatory_complexity", 1),
               state.get("previous_incidents", 0),
               state.get("bcms_maturity", 2)
           ])
   ```

3. **Training script** (2h)
   ```python
   # scripts/train_ml_models.py (NEW FILE)

   import asyncio
   from ml.training.pipeline import MLTrainingPipeline
   from case_library.repository import CaseRepository

   async def main():
       # Initialize case library
       case_repo = CaseRepository()

       # Create pipeline
       pipeline = MLTrainingPipeline(case_repo)

       print("🚀 Training ML models...")

       # Train duration predictor
       print("\n1️⃣ Training duration predictor...")
       duration_result = await pipeline.train_duration_predictor()
       print(f"   Score: {duration_result['score']:.3f}")
       print(f"   Samples: {duration_result['samples']}")

       # Train risk predictor
       print("\n2️⃣ Training risk predictor...")
       risk_result = await pipeline.train_risk_predictor()
       print(f"   Score: {risk_result['score']:.3f}")
       print(f"   Samples: {risk_result['samples']}")

       print("\n✅ Training complete!")
       print("   Models saved to ml/models/")

   if __name__ == "__main__":
       asyncio.run(main())
   ```

4. **Интеграция с AI Advisor** (2h)
   ```python
   # ai/context_advisor.py - UPDATE

   from ml.predictor import MLPredictor

   class ContextAdvisor:
       def __init__(self, workflow_engine, case_library, ml_predictor=None):
           self.workflow_engine = workflow_engine
           self.case_library = case_library
           self.ml_predictor = ml_predictor or MLPredictor()  # ADD THIS

       async def get_contextual_advice(self, context):
           # ... existing code ...

           # ADD: ML predictions
           predicted_duration = await self.ml_predictor.predict_duration(
               workflow_type=context.get("workflow_type"),
               org_context=context
           )

           predicted_risk = await self.ml_predictor.predict_risk(
               workflow_id=context.get("workflow_id"),
               current_state=context
           )

           return {
               "advice": advice,
               "predictions": {
                   "duration_hours": predicted_duration,
                   "risk": predicted_risk
               }
           }
   ```

**Deliverable:**
- ✅ ML training pipeline
- ✅ 3 trained models (duration, risk, success)
- ✅ MLPredictor production service
- ✅ Integration with AI Advisor
- ✅ Training script

#### Task 4.2: Model Versioning (8h)

```python
# ml/training/model_versioning.py (NEW FILE)

import joblib
import json
from datetime import datetime
from pathlib import Path

class ModelVersioning:
    """Model versioning система"""

    def __init__(self, models_dir: str = "ml/models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.versions_file = self.models_dir / "versions.json"

    def save_model(
        self,
        model,
        model_name: str,
        metadata: dict
    ) -> str:
        """Save model with version"""

        # Load version history
        versions = self._load_versions()

        # Increment version
        current_version = versions.get(model_name, {}).get("latest_version", 0) + 1

        # Save model
        model_filename = f"{model_name}_v{current_version}.pkl"
        model_path = self.models_dir / model_filename
        joblib.dump(model, model_path)

        # Update versions
        if model_name not in versions:
            versions[model_name] = {"versions": []}

        version_info = {
            "version": current_version,
            "filename": model_filename,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata
        }

        versions[model_name]["versions"].append(version_info)
        versions[model_name]["latest_version"] = current_version
        versions[model_name]["latest_filename"] = model_filename

        self._save_versions(versions)

        # Create symlink to latest
        latest_link = self.models_dir / f"{model_name}.pkl"
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(model_filename)

        return model_filename

    def load_model(self, model_name: str, version: int = None):
        """Load model by name and optional version"""

        versions = self._load_versions()

        if model_name not in versions:
            raise ValueError(f"Model {model_name} not found")

        if version is None:
            # Load latest
            filename = versions[model_name]["latest_filename"]
        else:
            # Load specific version
            version_info = next(
                (v for v in versions[model_name]["versions"] if v["version"] == version),
                None
            )
            if not version_info:
                raise ValueError(f"Version {version} not found for {model_name}")
            filename = version_info["filename"]

        model_path = self.models_dir / filename
        return joblib.load(model_path)

    def _load_versions(self) -> dict:
        if self.versions_file.exists():
            with open(self.versions_file) as f:
                return json.load(f)
        return {}

    def _save_versions(self, versions: dict):
        with open(self.versions_file, 'w') as f:
            json.dump(versions, f, indent=2)
```

#### Task 4.3: A/B Testing Framework (8h)

```python
# ml/ab_testing.py (NEW FILE)

class ABTestingFramework:
    """
    A/B testing для ML models
    Сравнение новой версии модели с текущей
    """

    def __init__(self):
        self.test_results = []

    async def run_ab_test(
        self,
        model_a,
        model_b,
        test_data: list,
        metric: str = "accuracy"
    ) -> dict:
        """Run A/B test between two models"""

        predictions_a = [model_a.predict([sample]) for sample in test_data]
        predictions_b = [model_b.predict([sample]) for sample in test_data]

        # Calculate metrics
        score_a = self._calculate_metric(predictions_a, test_data, metric)
        score_b = self._calculate_metric(predictions_b, test_data, metric)

        # Statistical significance test
        is_significant = self._test_significance(score_a, score_b)

        result = {
            "model_a_score": score_a,
            "model_b_score": score_b,
            "improvement": score_b - score_a,
            "significant": is_significant,
            "winner": "B" if score_b > score_a and is_significant else "A"
        }

        self.test_results.append(result)
        return result

    def _calculate_metric(self, predictions, test_data, metric):
        # Implement metric calculation
        pass

    def _test_significance(self, score_a, score_b):
        # Implement significance test
        pass
```

#### Task 4.4: Automated Retraining (8h)

```python
# ml/auto_retrain.py (NEW FILE)

import asyncio
from datetime import datetime, timedelta

class AutoRetrainingScheduler:
    """
    Автоматическое переобучение моделей
    Runs as background task
    """

    def __init__(self, pipeline, retrain_interval_days=7):
        self.pipeline = pipeline
        self.retrain_interval = timedelta(days=retrain_interval_days)
        self.last_retrain = {}

    async def start(self):
        """Start auto-retraining scheduler"""
        print("🤖 Auto-retraining scheduler started")

        while True:
            await asyncio.sleep(3600)  # Check every hour

            # Check if retraining needed
            for model_name in ["duration_predictor", "risk_predictor"]:
                if self._should_retrain(model_name):
                    await self._retrain_model(model_name)

    def _should_retrain(self, model_name: str) -> bool:
        """Check if model should be retrained"""
        last_retrain = self.last_retrain.get(model_name)

        if last_retrain is None:
            return True

        return datetime.now() - last_retrain > self.retrain_interval

    async def _retrain_model(self, model_name: str):
        """Retrain specific model"""
        print(f"🔄 Retraining {model_name}...")

        if model_name == "duration_predictor":
            result = await self.pipeline.train_duration_predictor()
        elif model_name == "risk_predictor":
            result = await self.pipeline.train_risk_predictor()

        self.last_retrain[model_name] = datetime.now()

        print(f"✅ {model_name} retrained. Score: {result['score']:.3f}")
```

**Deliverable:**
- ✅ Model versioning system
- ✅ A/B testing framework
- ✅ Auto-retraining scheduler
- ✅ Production-grade ML pipeline

---

### Phase 5: Missing Workflows (3 дня, 24 hours)

Код уже есть в дизайне (WORKFLOW_INTELLIGENCE_PLATFORM_COVERAGE_DESIGN.md, раздел 5.1).

#### Task 5.1: Training Workflow (8h)
- Copy from design doc
- Create workflows/training_workflow.py
- Full implementation с ISO 22301 Clause 7.2

#### Task 5.2: Exercise Workflow (8h)
- Create workflows/exercise_workflow.py
- ISO 22301 Clause 8.5

#### Task 5.3: Audit Workflow (8h)
- Create workflows/audit_workflow.py
- ISO 22301 Clause 9.2

**Deliverable:**
- ✅ 3 new workflows
- ✅ Complete BCM lifecycle coverage
- ✅ ISO 22301 compliant

---

### Phase 6: Testing & Quality (2 дня, 16 hours)

#### Task 6.1: Create tests/ directory (2h)

```
tests/
├── __init__.py
├── conftest.py
├── unit/
│   ├── test_core_engine.py
│   ├── test_case_library.py
│   ├── test_governance.py
│   ├── test_compliance.py
│   └── test_ml_predictor.py
├── integration/
│   ├── test_api.py
│   ├── test_workflows.py
│   └── test_end_to_end.py
└── performance/
    └── test_load.py
```

#### Task 6.2: Unit tests (8h)

```python
# tests/unit/test_core_engine.py

import pytest
from core.workflow_engine import WorkflowEngine, WorkflowContext

@pytest.mark.asyncio
async def test_workflow_engine_initialization():
    engine = WorkflowEngine(
        module="test",
        state_machine=MockStateMachine()
    )
    assert engine.module == "test"

@pytest.mark.asyncio
async def test_workflow_execution():
    engine = WorkflowEngine(module="bia")
    result = await engine.execute_workflow({
        "organization": "Test Org",
        "workflow_type": "bia"
    })
    assert result["status"] == "completed"
```

#### Task 6.3: Integration tests (4h)

```python
# tests/integration/test_api.py

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_case_library_endpoint():
    response = client.post("/api/v1/cases/search", json={
        "module": "bia",
        "industry": "healthcare"
    })
    assert response.status_code == 200
```

#### Task 6.4: Coverage report (2h)

```bash
# Run tests with coverage
pytest --cov=. --cov-report=html --cov-report=term

# Target: 80%+ coverage
```

**Deliverable:**
- ✅ Comprehensive test suite
- ✅ 80%+ code coverage
- ✅ CI/CD ready

---

### Phase 7: Automation (1 день, 8 hours)

#### Task 7.1: Pre-commit hooks (2h)

```yaml
# .pre-commit-config.yaml (NEW FILE)

repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.9

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100']

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

#### Task 7.2: GitHub Actions CI/CD (3h)

```yaml
# .github/workflows/workflow_intelligence_ci.yml (NEW FILE)

name: Workflow Intelligence CI

on:
  push:
    paths:
      - 'intelligent_core/workflow_intelligence/**'
  pull_request:
    paths:
      - 'intelligent_core/workflow_intelligence/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          cd intelligent_core/workflow_intelligence
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          cd intelligent_core/workflow_intelligence
          pytest --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./intelligent_core/workflow_intelligence/coverage.xml
```

#### Task 7.3: Automated ML retraining (2h)

```python
# Add to main.py lifespan

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Workflow Intelligence Service...")

    # Start auto-retraining
    from ml.auto_retrain import AutoRetrainingScheduler
    from ml.training.pipeline import MLTrainingPipeline

    pipeline = MLTrainingPipeline(case_library)
    auto_retrain = AutoRetrainingScheduler(pipeline, retrain_interval_days=7)
    retrain_task = asyncio.create_task(auto_retrain.start())

    yield

    # Shutdown
    retrain_task.cancel()
```

#### Task 7.4: Monitoring automation (1h)

```python
# monitoring/auto_alerts.py (NEW FILE)

class AutoAlertSystem:
    """Автоматические алерты для critical issues"""

    async def monitor_health(self):
        """Monitor system health"""
        while True:
            await asyncio.sleep(60)

            # Check metrics
            metrics = await self.get_metrics()

            # Alert if threshold exceeded
            if metrics["error_rate"] > 0.05:
                await self.send_alert("High error rate detected")

            if metrics["response_time_p95"] > 2000:
                await self.send_alert("Slow response time")

    async def send_alert(self, message: str):
        # Send to Slack/email/etc
        print(f"🚨 ALERT: {message}")
```

**Deliverable:**
- ✅ Pre-commit hooks
- ✅ CI/CD pipeline
- ✅ Auto ML retraining
- ✅ Auto alerts

---

## Summary Timeline

| Phase | Tasks | Duration | Deliverable |
|-------|-------|----------|-------------|
| **1. Code Cleanup** | Remove duplicates, clean root | 1 день | -2,452 LOC, clean structure |
| **2. API Refactoring** | Modular API structure | 1 день | main.py 1000→150 LOC |
| **3. Compliance** | Full ISO22301Checker | 2 дня | Real compliance checks |
| **4. ML Pipeline** | Training, versioning, A/B | 5 дней | Trained models, predictor |
| **5. Missing Workflows** | Training, Audit, Exercise | 3 дня | 3 new workflows |
| **6. Testing** | Unit, integration, coverage | 2 дня | 80%+ coverage |
| **7. Automation** | CI/CD, auto-retrain, alerts | 1 день | Full automation |
| **TOTAL** | 25 tasks | **15 дней** | Production-ready module |

---

## Metrics

### Before → After

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Code Duplication** | 2,452 lines | 0 lines | -100% |
| **main.py size** | 1,048 lines | ~150 lines | -85% |
| **API Structure** | Monolithic | Modular | ✅ |
| **Compliance** | 10% (stub) | 100% (full) | +900% |
| **ML Models** | 0 trained | 3 trained | +∞ |
| **Workflows** | 4 | 7 | +75% |
| **Test Coverage** | ~50% | 80%+ | +60% |
| **Automation** | Manual | Automated | ✅ |
| **Overall Completeness** | 75% | 95% | +27% |

---

## Priority Actions (First Week)

**Day 1-2: Code Cleanup**
1. Remove duplicates (4h)
2. Update __init__.py (2h)
3. Test imports (1h)
4. Documentation (1.5h)

**Day 3-4: API Refactoring**
1. Create api/ modules (6h)
2. Update main.py (1h)
3. Testing (1h)

**Day 5: Compliance Start**
1. Implement ISO22301Checker (8h)

**Week 1 Deliverable:**
- ✅ Clean codebase (no duplicates)
- ✅ Modular API structure
- ✅ Compliance module 50% done

---

## Next Steps

1. **Review этого плана** - подтверждение scope
2. **Start Phase 1** - code cleanup (немедленно можно начать)
3. **Daily standups** - tracking progress
4. **Weekly review** - adjust plan if needed

---

**Plan Version:** 1.0.0
**Date:** 2025-10-21
**Status:** Ready for Execution
**Focus:** Internal module optimization only
**Timeline:** 15 дней (3 недели)
**ROI:** From 75% → 95% completeness

Ready to start? 🚀
