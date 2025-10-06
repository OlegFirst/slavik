"""
Workflow Intelligence API Routes
Интеграция Workflow Intelligence Engine с Intelligent Core
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from workflow_intelligence import (
    WorkflowEngine,
    ContextAdvisor,
    CaseCollector,
    WorkflowContext,
    CaseQuery,
    event_bus
)

# Create API router
router = APIRouter(prefix="/api/v1/workflow", tags=["Workflow Intelligence"])

# ============================================================================
# GLOBAL INSTANCES (будут инициализированы при старте приложения)
# ============================================================================

workflow_engine: Optional[WorkflowEngine] = None
context_advisor: Optional[ContextAdvisor] = None
case_collector: Optional[CaseCollector] = None


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class StartWorkflowRequest(BaseModel):
    workflow_id: str
    module: str  # "bia", "risk", "plan", etc.
    initial_data: Dict[str, Any]
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None


class ExecuteActionRequest(BaseModel):
    action: str
    action_data: Dict[str, Any] = {}
    user_id: Optional[str] = None


class GetAdviceRequest(BaseModel):
    user_message: Optional[str] = None


class FindSimilarCasesRequest(BaseModel):
    module: str
    industry: Optional[str] = None
    org_size: Optional[str] = None
    current_stage: Optional[str] = None
    limit: int = 5


# ============================================================================
# WORKFLOW MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/start")
async def start_workflow(request: StartWorkflowRequest):
    """
    🚀 Запустить новый workflow

    Примеры:
    - BIA workflow для healthcare организации
    - Risk Assessment для финансовой компании
    - Business Continuity Plan для производства
    """
    if not workflow_engine:
        raise HTTPException(status_code=503, detail="Workflow engine not initialized")

    try:
        context = await workflow_engine.start(
            workflow_id=request.workflow_id,
            initial_data=request.initial_data,
            tenant_id=request.tenant_id,
            user_id=request.user_id
        )

        return {
            "status": "started",
            "workflow_id": request.workflow_id,
            "context": context.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{workflow_id}/context")
async def get_workflow_context(workflow_id: str):
    """
    📊 Получить текущий контекст workflow

    Возвращает:
    - Текущий stage
    - Прогресс (%)
    - Gaps (что не хватает)
    - Available actions (что можно делать)
    - Данные workflow
    """
    if not workflow_engine:
        raise HTTPException(status_code=503, detail="Workflow engine not initialized")

    try:
        context = await workflow_engine.get_context(workflow_id)
        return context.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{workflow_id}/actions")
async def execute_workflow_action(workflow_id: str, request: ExecuteActionRequest):
    """
    ⚡ Выполнить действие в workflow

    Примеры actions:
    - identify_processes (BIA)
    - assess_impact (BIA)
    - suggest_rto (BIA)
    - create_strategy (Planning)
    """
    if not workflow_engine:
        raise HTTPException(status_code=503, detail="Workflow engine not initialized")

    try:
        context = await workflow_engine.execute_action(
            workflow_id=workflow_id,
            action=request.action,
            action_data=request.action_data,
            user_id=request.user_id
        )

        return {
            "status": "executed",
            "action": request.action,
            "context": context.model_dump()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{workflow_id}/complete")
async def complete_workflow(workflow_id: str):
    """
    ✅ Завершить workflow

    Triggers:
    - Case collection (if successful)
    - ML model retraining
    - Benchmark updates
    """
    if not workflow_engine:
        raise HTTPException(status_code=503, detail="Workflow engine not initialized")

    try:
        context = await workflow_engine.complete(workflow_id)

        return {
            "status": "completed",
            "workflow_id": workflow_id,
            "context": context.model_dump()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AI ADVISOR ENDPOINTS
# ============================================================================

@router.post("/{workflow_id}/advice")
async def get_contextual_advice(workflow_id: str, request: GetAdviceRequest):
    """
    🤖 Получить контекстный AI совет

    AI понимает:
    - Где пользователь в workflow (current stage)
    - Что не хватает (gaps)
    - Что работало у похожих организаций (similar cases)
    - Средние показатели индустрии (benchmarks)

    Возвращает:
    - Совет на основе контекста
    - Suggested actions
    - Similar cases
    - Benchmarks
    """
    if not context_advisor:
        raise HTTPException(status_code=503, detail="Context advisor not initialized")

    try:
        advice = await context_advisor.get_contextual_advice(
            workflow_id=workflow_id,
            user_message=request.user_message
        )

        return advice
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}/similar-cases")
async def get_similar_cases(workflow_id: str, limit: int = 5):
    """
    📚 Найти похожие успешные cases

    Используется для:
    - Обучения на успехах других
    - Benchmarking
    - Best practices
    """
    if not context_advisor:
        raise HTTPException(status_code=503, detail="Context advisor not initialized")

    try:
        cases = await context_advisor.find_similar_cases(workflow_id, limit=limit)
        return [case.model_dump() for case in cases]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}/benchmarks")
async def get_workflow_benchmarks(workflow_id: str):
    """
    📈 Получить industry benchmarks

    Показывает:
    - Average duration
    - Success rate
    - Common challenges
    - Best practices
    """
    if not context_advisor:
        raise HTTPException(status_code=503, detail="Context advisor not initialized")

    try:
        benchmarks = await context_advisor.get_benchmarks(workflow_id)
        return benchmarks.model_dump() if benchmarks else None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CASE LIBRARY ENDPOINTS
# ============================================================================

@router.post("/cases/search")
async def search_similar_cases(request: FindSimilarCasesRequest):
    """
    🔍 Поиск похожих cases в библиотеке

    Фильтры:
    - Module (bia, risk, plan)
    - Industry
    - Organization size
    - Current stage
    """
    # TODO: Implement with CaseLibrary
    # For now, return empty
    return []


@router.get("/cases/{case_id}")
async def get_case_details(case_id: str):
    """
    📖 Получить детали case

    Включает:
    - Organization context (anonymized)
    - Journey (workflow steps)
    - Metrics
    - Success patterns
    - Lessons learned
    """
    # TODO: Implement with CaseRepository
    raise HTTPException(status_code=404, detail="Case not found")


@router.get("/benchmarks/{module}/{industry}")
async def get_benchmarks(module: str, industry: str, org_size: Optional[str] = None):
    """
    📊 Получить benchmarks для module/industry

    Показывает:
    - Средняя длительность workflow
    - Success rate
    - AI acceptance rate
    - Common challenges
    - Best practices
    """
    # TODO: Implement with CaseLibrary
    return {
        "module": module,
        "industry": industry,
        "org_size": org_size,
        "total_cases": 0,
        "avg_duration_days": None,
        "success_rate": None
    }


# ============================================================================
# EVENT STREAM ENDPOINTS
# ============================================================================

@router.get("/{workflow_id}/events")
async def get_workflow_events(workflow_id: str, limit: int = 100):
    """
    📡 Получить события workflow

    Для:
    - Audit trail
    - Debugging
    - Analytics
    """
    # TODO: Get events from storage
    return []


@router.get("/events/stream")
async def stream_events():
    """
    🔴 Real-time event stream (SSE)

    Для WebSocket/SSE подписки на события
    """
    # TODO: Implement SSE stream
    raise HTTPException(status_code=501, detail="Not implemented yet")


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/analytics/workflows")
async def get_workflow_analytics(
    module: Optional[str] = None,
    tenant_id: Optional[str] = None,
    days: int = 30
):
    """
    📊 Аналитика по workflows

    Показывает:
    - Total workflows
    - Completion rate
    - Average duration
    - AI usage statistics
    """
    # TODO: Implement analytics
    return {
        "total_workflows": 0,
        "completed": 0,
        "in_progress": 0,
        "avg_duration_days": None,
        "completion_rate": None
    }


# ============================================================================
# INITIALIZATION FUNCTION
# ============================================================================

async def initialize_workflow_intelligence(
    storage_adapter,
    case_repository,
    case_library,
    llm_config: Dict[str, Any]
):
    """
    Инициализация Workflow Intelligence Engine

    Вызывается при старте приложения
    """
    global workflow_engine, context_advisor, case_collector

    from workflow_intelligence.core.workflow_engine import InMemoryStorageAdapter

    # Для демо используем in-memory, в продакшене - PostgreSQL
    if storage_adapter is None:
        storage_adapter = InMemoryStorageAdapter()

    # Create workflow engine (universal, works with any state machine)
    workflow_engine = WorkflowEngine(
        module="universal",
        state_machine=None,  # Will be set per-workflow
        storage_adapter=storage_adapter
    )

    # Create context advisor
    if case_library:
        context_advisor = ContextAdvisor(
            workflow_engine=workflow_engine,
            case_library=case_library,
            llm_config=llm_config
        )

    # Create case collector
    if case_repository:
        case_collector = CaseCollector(
            workflow_engine=workflow_engine,
            case_repository=case_repository
        )

    print("✅ Workflow Intelligence Engine initialized")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_workflow_engine() -> WorkflowEngine:
    """Dependency injection for workflow engine"""
    if not workflow_engine:
        raise HTTPException(
            status_code=503,
            detail="Workflow engine not initialized"
        )
    return workflow_engine


def get_context_advisor() -> ContextAdvisor:
    """Dependency injection for context advisor"""
    if not context_advisor:
        raise HTTPException(
            status_code=503,
            detail="Context advisor not initialized"
        )
    return context_advisor
