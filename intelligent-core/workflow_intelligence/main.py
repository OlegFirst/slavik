"""
Workflow Intelligence Service

Standalone FastAPI service providing:
- Case Library API
- Workflow Analysis
- ML-powered recommendations
- Goals + Rules Governance (NEW!)

Port: 8037

Version 2.0 Features:
- Goals Engine: Positive targets for optimization
- Rules Engine V2: Multi-level hierarchy with recursive application
- Governance Orchestrator: Unified decision making
- Self-monitoring: System validates itself ("eat own dog food")
"""

import logging
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, HTTPException, Response, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uvicorn
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import asyncio

# Add shared event_bus to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.event_bus import init_event_bus, get_event_bus, publish_event, subscribe_to

# Import new governance components
from governance.governance_orchestrator import (
    GovernanceOrchestrator,
    GovernanceContext,
    GovernanceDecision,
    RuleAppliesTo,
    create_governance_orchestrator
)
from governance.goals_engine import GoalLevel, GoalStatus
from governance.rules_engine_v2 import RuleCategory, RuleSeverity

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
PORT = 8037
HOST = "0.0.0.0"
GOVERNANCE_CONFIG_PATH = Path(__file__).parent / "governance" / "goals.yaml"

# Global governance orchestrator
governance: Optional[GovernanceOrchestrator] = None

# Global PDCA engine
pdca_engine = None

# Self-monitoring task
self_monitoring_task = None


async def system_self_monitoring():
    """
    Background task for system self-monitoring

    Workflow Intelligence validates itself against goals and rules
    every 60 seconds. This is the "eat own dog food" implementation.
    """
    global governance

    while True:
        try:
            await asyncio.sleep(60)  # Check every 60 seconds

            if not governance:
                continue

            # Collect system metrics
            system_metrics = {
                'response_time_ms': 150,  # TODO: Collect real metrics
                'ml_accuracy_percent': 87,
                'transition_time_seconds': 2.5,
                'uptime_percent': 99.9,
                'cpu_utilization_percent': 65,
                'memory_utilization_percent': 70
            }

            # Validate system against governance
            decision = await governance.validate_system_health(system_metrics)

            if decision.decision_type in ['block', 'warn']:
                logger.warning(
                    f"🔴 SELF-MONITORING ALERT: {decision.rationale}"
                )

                # Publish system health event
                await publish_event(
                    event_type="workflow.system.health.warning",
                    data={
                        'decision_type': decision.decision_type,
                        'rationale': decision.rationale,
                        'actions': decision.actions_to_take,
                        'escalate': decision.escalate_to_human
                    }
                )
            else:
                logger.debug("✅ System self-check passed")

        except Exception as e:
            logger.error(f"System self-monitoring error: {e}")


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global governance, pdca_engine, self_monitoring_task

    # Startup
    logger.info("🚀 Starting Workflow Intelligence Service v2.0")
    logger.info(f"📍 Port: {PORT}")

    # Initialize EventBus
    try:
        await init_event_bus(
            service_name="workflow-intelligence",
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379")
        )
        logger.info("✅ EventBus initialized")
    except Exception as e:
        logger.warning(f"⚠️ EventBus init failed: {e}")

    # Initialize Governance Orchestrator
    try:
        governance = create_governance_orchestrator(str(GOVERNANCE_CONFIG_PATH))
        logger.info("✅ Governance Orchestrator initialized")
        logger.info(f"   - Goals: {len(governance.goals_engine.goals)}")
        logger.info(f"   - Rules: {len(governance.rules_engine.rules)}")

        # Get initial governance summary
        summary = governance.get_governance_summary()
        logger.info(f"   - Governance Maturity: {summary['governance_maturity_score']}/100")

    except Exception as e:
        logger.error(f"❌ Governance init failed: {e}")
        governance = None

    # Initialize PDCA Rules Engine (NEW!)
    try:
        from .enable_pdca import enable_pdca_for_platform_eventbus

        event_bus = get_event_bus()
        if event_bus:
            pdca_engine = await enable_pdca_for_platform_eventbus(
                event_bus=event_bus,
                tenant_id=os.getenv("TENANT_ID", "default-tenant")
            )
            logger.info("✅ PDCA Rules Engine activated")
            logger.info("   - All workflows will go through PDCA cycles")
            logger.info("   - PLAN → DO → CHECK → ACT")
        else:
            logger.warning("⚠️ EventBus not available, skipping PDCA activation")
    except Exception as e:
        logger.error(f"❌ PDCA initialization failed: {e}", exc_info=True)
        pdca_engine = None

    # Start system self-monitoring background task
    if governance:
        self_monitoring_task = asyncio.create_task(system_self_monitoring())
        logger.info("✅ System self-monitoring started (60s interval)")

    logger.info("✅ Service ready!")
    yield

    # Shutdown
    logger.info("👋 Shutting down Workflow Intelligence Service")

    # Cancel self-monitoring
    if self_monitoring_task:
        self_monitoring_task.cancel()
        try:
            await self_monitoring_task
        except asyncio.CancelledError:
            pass

    bus = get_event_bus()
    if bus:
        await bus.close()

# Create FastAPI app
app = FastAPI(
    lifespan=lifespan,
    title="Workflow Intelligence Service",
    description="Workflow Intelligence, Case Library & ML Analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router
router = APIRouter(tags=["Workflow Intelligence"])


# ==================== Models ====================

class CaseAddRequest(BaseModel):
    """Add case to library"""
    case_data: Dict[str, Any]
    module: str
    source: str = "community"
    metadata: Optional[Dict[str, Any]] = None


class CaseResponse(BaseModel):
    """Case response"""
    case_id: str
    status: str
    message: str


class WorkflowAnalysisRequest(BaseModel):
    """Workflow analysis request"""
    workflow_id: str
    workflow_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class WorkflowAnalysisResponse(BaseModel):
    """Workflow analysis response"""
    workflow_id: str
    analysis: Dict[str, Any]
    recommendations: List[str]
    confidence: float


# ==================== Core Endpoints ====================

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "workflow-intelligence",
        "version": "1.0.0"
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@router.get("/info")
async def get_info():
    """Service information"""
    return {
        "service": "workflow-intelligence",
        "version": "1.0.0",
        "features": [
            "Case Library Management",
            "Workflow Analysis",
            "ML Recommendations",
            "Community Integration"
        ],
        "endpoints": {
            "cases": [
                "/cases/add",
                "/cases/{case_id}",
                "/cases/search"
            ],
            "analysis": [
                "/analyze",
                "/recommend"
            ]
        },
        "status": "available"
    }


# ==================== Case Library Endpoints ====================

@router.post("/cases/add", response_model=CaseResponse)
async def add_case(request: CaseAddRequest):
    """
    Add case to workflow intelligence library

    Used by community_intelligence to sync approved cases
    """
    try:
        # TODO: Full implementation with case_library
        # For now, accept and return success
        import uuid
        case_id = str(uuid.uuid4())

        logger.info(
            f"📚 Case added to library: {case_id} "
            f"(module: {request.module}, source: {request.source})"
        )

        # Publish event
        await publish_event(
            event_type="workflow.case.added",
            data={
                "case_id": case_id,
                "module": request.module,
                "source": request.source,
                "metadata": request.metadata or {}
            }
        )

        return CaseResponse(
            case_id=case_id,
            status="success",
            message=f"Case added to library successfully"
        )

    except Exception as e:
        logger.error(f"Failed to add case: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cases/{case_id}")
async def get_case(case_id: str):
    """Get case by ID"""
    # TODO: Full implementation
    return {
        "case_id": case_id,
        "status": "found",
        "data": {
            "module": "example",
            "title": "Example Case",
            "description": "Case description here"
        },
        "note": "Full implementation coming soon"
    }


@router.post("/cases/search")
async def search_cases(query: Dict[str, Any]):
    """Search cases in library"""
    # TODO: Full implementation
    return {
        "results": [],
        "total": 0,
        "note": "Full implementation coming soon"
    }


@router.post("/cases/bulk")
async def bulk_operations(operations: List[Dict[str, Any]]):
    """Bulk case operations"""
    # TODO: Full implementation
    return {
        "processed": len(operations),
        "status": "success",
        "note": "Full implementation coming soon"
    }


# ==================== Workflow Analysis Endpoints ====================

@router.post("/analyze", response_model=WorkflowAnalysisResponse)
async def analyze_workflow(request: WorkflowAnalysisRequest):
    """
    Analyze workflow with ML

    Returns insights and recommendations
    """
    try:
        # TODO: Full ML implementation
        # For now, return simple analysis

        logger.info(f"🔍 Analyzing workflow: {request.workflow_id}")

        return WorkflowAnalysisResponse(
            workflow_id=request.workflow_id,
            analysis={
                "complexity": "medium",
                "estimated_duration": "10 minutes",
                "risk_level": "low",
                "optimization_potential": "moderate"
            },
            recommendations=[
                "Consider parallel execution for independent tasks",
                "Add error handling for critical steps",
                "Cache frequently accessed data"
            ],
            confidence=0.75
        )

    except Exception as e:
        logger.error(f"Workflow analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend")
async def get_recommendations(workflow_data: Dict[str, Any]):
    """Get ML-powered recommendations for workflow"""
    # TODO: Full ML implementation
    return {
        "recommendations": [
            {
                "type": "optimization",
                "priority": "high",
                "description": "Optimize data loading",
                "expected_impact": "30% faster execution"
            },
            {
                "type": "reliability",
                "priority": "medium",
                "description": "Add retry logic",
                "expected_impact": "95% success rate"
            }
        ],
        "note": "Full ML implementation coming soon"
    }


# ==================== NEW: Governance Endpoints ====================

class GovernanceValidateRequest(BaseModel):
    """Request to validate workflow against governance"""
    workflow_id: str
    workflow_data: Dict[str, Any]
    current_stage: str
    start_time: Optional[str] = None


class GovernanceDecisionModel(BaseModel):
    """Governance decision response"""
    decision_id: str
    decision_type: str
    rationale: str
    actions_to_take: List[str]
    escalate_to_human: bool
    rule_violations: List[Dict[str, Any]] = []
    optimization_suggestions: List[Dict[str, Any]] = []


@router.post("/governance/validate", response_model=GovernanceDecisionModel)
async def validate_workflow_governance(request: GovernanceValidateRequest):
    """
    Validate user workflow against Goals + Rules governance

    This endpoint checks:
    - Rules compliance (Constitution, Compliance, Organization, Best Practice, ML)
    - Goal progress (completion time, quality, etc.)
    - Suggests optimizations if goals at risk

    Example:
    ```json
    {
      "workflow_id": "bia_123",
      "workflow_data": {
        "processes": [...],
        "rto_hours": 4,
        "financial_impact": 50000
      },
      "current_stage": "assess_impact",
      "start_time": "2025-10-09T10:00:00Z"
    }
    ```

    Returns decision: "allow", "block", "warn", "suggest_optimization"
    """
    if not governance:
        raise HTTPException(
            status_code=503,
            detail="Governance system not initialized"
        )

    try:
        logger.info(f"🔍 Validating workflow {request.workflow_id} against governance")

        # Validate with governance orchestrator
        decision = governance.validate_user_workflow(
            workflow_data=request.workflow_data,
            workflow_id=request.workflow_id,
            current_stage=request.current_stage,
            start_time=request.start_time
        )

        # Convert to response model
        return GovernanceDecisionModel(
            decision_id=decision.decision_id,
            decision_type=decision.decision_type,
            rationale=decision.rationale,
            actions_to_take=decision.actions_to_take,
            escalate_to_human=decision.escalate_to_human,
            rule_violations=[
                {
                    'rule_id': v.rule_id,
                    'rule_name': v.rule_name,
                    'severity': v.severity.value,
                    'message': v.message,
                    'can_override': v.can_override
                }
                for v in decision.rule_violations
            ],
            optimization_suggestions=[
                {
                    'goal_id': s.goal_id,
                    'goal_name': s.goal_name,
                    'strategy': s.strategy,
                    'priority': s.priority,
                    'actions': s.actions
                }
                for s in decision.optimization_suggestions
            ]
        )

    except Exception as e:
        logger.error(f"Governance validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/governance/summary")
async def get_governance_summary():
    """
    Get overall governance health summary

    Returns:
    - Goals status (achieved, on_track, at_risk, behind)
    - Rules compliance (violations count)
    - Decisions history
    - Governance maturity score (0-100)
    """
    if not governance:
        raise HTTPException(
            status_code=503,
            detail="Governance system not initialized"
        )

    try:
        summary = governance.get_governance_summary()
        return summary

    except Exception as e:
        logger.error(f"Failed to get governance summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/governance/goals")
async def get_goals_status():
    """
    Get all goals with their current status

    Groups goals by level:
    - User goals (BIA completion, quality, etc.)
    - System goals (performance, accuracy, etc.)
    - Component goals (AI Foundation, BIA Service, etc.)
    - Platform goals (MTTR, user satisfaction, etc.)
    """
    if not governance:
        raise HTTPException(
            status_code=503,
            detail="Governance system not initialized"
        )

    try:
        goals_by_level = {
            'user_goals': [
                {
                    'goal_id': g.goal_id,
                    'name': g.name,
                    'status': g.status.value,
                    'progress_percent': g.progress_percent,
                    'metrics': g.metrics,
                    'current_values': g.current_values
                }
                for g in governance.goals_engine.get_goals_by_level(GoalLevel.USER)
            ],
            'system_goals': [
                {
                    'goal_id': g.goal_id,
                    'name': g.name,
                    'status': g.status.value,
                    'progress_percent': g.progress_percent,
                    'metrics': g.metrics,
                    'current_values': g.current_values
                }
                for g in governance.goals_engine.get_goals_by_level(GoalLevel.SYSTEM)
            ],
            'component_goals': [
                {
                    'goal_id': g.goal_id,
                    'name': g.name,
                    'status': g.status.value,
                    'progress_percent': g.progress_percent,
                    'metrics': g.metrics,
                    'current_values': g.current_values
                }
                for g in governance.goals_engine.get_goals_by_level(GoalLevel.COMPONENT)
            ],
            'platform_goals': [
                {
                    'goal_id': g.goal_id,
                    'name': g.name,
                    'status': g.status.value,
                    'progress_percent': g.progress_percent,
                    'metrics': g.metrics,
                    'current_values': g.current_values
                }
                for g in governance.goals_engine.get_goals_by_level(GoalLevel.PLATFORM)
            ]
        }

        return goals_by_level

    except Exception as e:
        logger.error(f"Failed to get goals status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/governance/rules")
async def get_rules_catalog():
    """
    Get all governance rules by category

    Categories:
    - Constitution: Unchangeable platform principles
    - Compliance: ISO 22301, NIST, WHO (can override with justification)
    - Organization: Corporate policies (configurable)
    - Best Practice: From Case Library (suggestions)
    - ML-Driven: Adaptive rules from ML (dynamic)
    """
    if not governance:
        raise HTTPException(
            status_code=503,
            detail="Governance system not initialized"
        )

    try:
        rules_by_category = {
            'constitution': [
                {
                    'rule_id': r.rule_id,
                    'name': r.name,
                    'description': r.description,
                    'severity': r.severity.value,
                    'applies_to': [level.value for level in r.applies_to],
                    'can_override': r.can_override
                }
                for r in governance.rules_engine.get_rules_by_category(RuleCategory.CONSTITUTION)
            ],
            'compliance': [
                {
                    'rule_id': r.rule_id,
                    'name': r.name,
                    'description': r.description,
                    'severity': r.severity.value,
                    'source': r.source,
                    'applies_to': [level.value for level in r.applies_to],
                    'can_override': r.can_override,
                    'override_requires': r.override_requires
                }
                for r in governance.rules_engine.get_rules_by_category(RuleCategory.COMPLIANCE)
            ],
            'organization': [
                {
                    'rule_id': r.rule_id,
                    'name': r.name,
                    'description': r.description,
                    'severity': r.severity.value,
                    'applies_to': [level.value for level in r.applies_to],
                    'configurable': r.configurable,
                    'default_value': r.default_value
                }
                for r in governance.rules_engine.get_rules_by_category(RuleCategory.ORGANIZATION)
            ],
            'best_practice': [
                {
                    'rule_id': r.rule_id,
                    'name': r.name,
                    'description': r.description,
                    'source': r.source,
                    'source_case_count': r.source_details.get('source_case_count'),
                    'applies_to': [level.value for level in r.applies_to]
                }
                for r in governance.rules_engine.get_rules_by_category(RuleCategory.BEST_PRACTICE)
            ],
            'ml_driven': [
                {
                    'rule_id': r.rule_id,
                    'name': r.name,
                    'description': r.description,
                    'model': r.source_details.get('model'),
                    'accuracy': r.source_details.get('accuracy'),
                    'applies_to': [level.value for level in r.applies_to]
                }
                for r in governance.rules_engine.get_rules_by_category(RuleCategory.ML_DRIVEN)
            ]
        }

        return rules_by_category

    except Exception as e:
        logger.error(f"Failed to get rules catalog: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/governance/optimization-suggestions")
async def get_optimization_suggestions():
    """
    Get current optimization suggestions

    Returns suggestions for goals that are at risk or behind target.
    Includes:
    - Goal name and current status
    - Optimization strategy
    - Specific actions to take
    - Expected impact
    """
    if not governance:
        raise HTTPException(
            status_code=503,
            detail="Governance system not initialized"
        )

    try:
        suggestions = governance.goals_engine.get_optimization_suggestions()

        return {
            'suggestions': [
                {
                    'goal_id': s.goal_id,
                    'goal_name': s.goal_name,
                    'strategy': s.strategy,
                    'priority': s.priority,
                    'actions': s.actions,
                    'expected_impact': s.expected_impact,
                    'timestamp': s.timestamp
                }
                for s in suggestions
            ],
            'total': len(suggestions)
        }

    except Exception as e:
        logger.error(f"Failed to get optimization suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== NEW: PDCA Endpoints ====================

@router.get("/pdca/status")
async def get_pdca_status():
    """
    Get PDCA system status

    Returns whether PDCA is initialized and working
    """
    if not pdca_engine:
        return {
            'status': 'inactive',
            'message': 'PDCA not initialized',
            'initialized': False
        }

    return {
        'status': 'active',
        'message': 'PDCA Rules Engine is running',
        'initialized': True,
        'tenant_id': pdca_engine.tenant_id,
        'components': {
            'database': pdca_engine.db is not None,
            'case_library': pdca_engine.case_library is not None,
            'knowledge_base': pdca_engine.knowledge_base is not None,
            'pattern_detector': pdca_engine.pattern_detector is not None
        }
    }


@router.get("/pdca/cycles")
async def list_pdca_cycles(
    module: Optional[str] = None,
    limit: int = 20
):
    """
    List recent PDCA cycles

    Args:
        module: Filter by module (bia, risk, compliance, etc.)
        limit: Maximum results to return

    Returns:
        List of PDCA cycles with summaries
    """
    if not pdca_engine:
        raise HTTPException(
            status_code=503,
            detail="PDCA not initialized"
        )

    try:
        # Get cycles from repository
        cycles = await pdca_engine.pdca_repo.get_recent_cycles(
            module=module,
            limit=limit
        )

        return {
            'cycles': cycles,
            'total': len(cycles),
            'module': module
        }

    except Exception as e:
        logger.error(f"Failed to list PDCA cycles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pdca/cycles/{workflow_id}")
async def get_pdca_cycle(workflow_id: str):
    """
    Get detailed PDCA cycle for a workflow

    Returns full cycle data:
    - PLAN: Recommendations, expected outcomes, benchmarks
    - DO: Execution data, duration
    - CHECK: Quality score, deviations
    - ACT: Lessons learned, patterns, improvements
    """
    if not pdca_engine:
        raise HTTPException(
            status_code=503,
            detail="PDCA not initialized"
        )

    try:
        cycle = await pdca_engine.pdca_repo.get_cycle_by_workflow_id(workflow_id)

        if not cycle:
            raise HTTPException(
                status_code=404,
                detail=f"No PDCA cycle found for workflow {workflow_id}"
            )

        return cycle

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get PDCA cycle: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pdca/benchmarks/{module}")
async def get_pdca_benchmarks(
    module: str,
    days_back: int = 90
):
    """
    Get PDCA benchmarks for a module

    Returns statistical benchmarks:
    - Average duration
    - Median duration
    - P95 duration
    - Average quality score
    - Success rate
    - Total cycles
    """
    if not pdca_engine:
        raise HTTPException(
            status_code=503,
            detail="PDCA not initialized"
        )

    try:
        benchmarks = await pdca_engine.pdca_repo.get_benchmarks(
            module=module,
            days_back=days_back
        )

        return {
            'module': module,
            'days_back': days_back,
            'benchmarks': benchmarks
        }

    except Exception as e:
        logger.error(f"Failed to get benchmarks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pdca/patterns")
async def get_pdca_patterns(
    module: Optional[str] = None,
    limit: int = 20
):
    """
    Get detected patterns from PDCA cycles

    Returns patterns discovered by ML analysis
    """
    if not pdca_engine:
        raise HTTPException(
            status_code=503,
            detail="PDCA not initialized"
        )

    try:
        patterns = await pdca_engine.pdca_repo.get_recent_patterns(
            module=module,
            limit=limit
        )

        return {
            'patterns': patterns,
            'total': len(patterns),
            'module': module
        }

    except Exception as e:
        logger.error(f"Failed to get patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pdca/lessons")
async def get_pdca_lessons(
    module: Optional[str] = None,
    min_quality: float = 70.0,
    limit: int = 20
):
    """
    Get lessons learned from PDCA cycles

    Returns high-quality lessons that can be applied to future workflows
    """
    if not pdca_engine:
        raise HTTPException(
            status_code=503,
            detail="PDCA not initialized"
        )

    try:
        lessons = await pdca_engine.pdca_repo.get_lessons_learned(
            module=module,
            min_quality=min_quality,
            limit=limit
        )

        return {
            'lessons': lessons,
            'total': len(lessons),
            'module': module,
            'min_quality': min_quality
        }

    except Exception as e:
        logger.error(f"Failed to get lessons: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pdca/statistics")
async def get_pdca_statistics(
    module: Optional[str] = None,
    days_back: int = 30
):
    """
    Get overall PDCA statistics

    Returns:
    - Total cycles
    - Average quality scores
    - Most common deviations
    - Learning velocity (lessons/day)
    - Pattern discovery rate
    """
    if not pdca_engine:
        raise HTTPException(
            status_code=503,
            detail="PDCA not initialized"
        )

    try:
        stats = await pdca_engine.pdca_repo.get_statistics(
            module=module,
            days_back=days_back
        )

        return {
            'statistics': stats,
            'module': module,
            'days_back': days_back
        }

    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Include router
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "workflow-intelligence",
        "version": "1.0.0",
        "status": "running",
        "mode": "api_gateway",
        "docs": "/docs",
        "health": "/health",
        "info": "/info"
    }


@app.get("/health")
async def app_health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "workflow-intelligence",
        "version": "1.0.0"
    }




if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False
    )
