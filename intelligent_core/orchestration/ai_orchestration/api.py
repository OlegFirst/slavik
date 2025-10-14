"""
AI Orchestrator FastAPI Endpoints
==================================

REST API for AI Orchestrator:
- Health check
- Decision endpoint
- Status and stats
- Prometheus metrics export
"""

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging

from .orchestrator import AIOrchestrator
from .policy_aware_orchestrator import PolicyAwareOrchestrator
from .metrics import get_metrics

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Orchestrator API",
    description="Central AI decision-making system for BCM platform",
    version="1.0.0"
)

# Global orchestrator instance
orchestrator: Optional[PolicyAwareOrchestrator] = None


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class DecisionRequest(BaseModel):
    """Request model for decision endpoint."""
    situation: Dict[str, Any]
    tenant_id: str = 'default'


class DecisionResponse(BaseModel):
    """Response model for decision endpoint."""
    decision_id: str
    action: str
    rationale: str
    priority: str
    confidence: float
    safety_approved: bool
    metadata: Dict[str, Any]


class ExecutionRequest(BaseModel):
    """Request model for execution endpoint."""
    decision_id: str


class ExecutionResponse(BaseModel):
    """Response model for execution endpoint."""
    success: bool
    message: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    initialized: bool
    version: str
    components: Dict[str, bool]


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize orchestrator on startup."""
    global orchestrator
    try:
        logger.info("🔄 Initializing AI Orchestrator...")

        # Create Policy-Aware Orchestrator (integrates both AI + Infrastructure governance)
        orchestrator = PolicyAwareOrchestrator(
            event_bus_backend='redis',
            enable_evolution=True,
            enable_safety=True
        )

        # Initialize all components
        await orchestrator.initialize()

        logger.info("✅ AI Orchestrator API started successfully")

    except Exception as e:
        logger.error(f"❌ Failed to initialize orchestrator: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global orchestrator
    if orchestrator:
        try:
            await orchestrator.shutdown()
            logger.info("✅ AI Orchestrator shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# ============================================================================
# HEALTH & STATUS
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns orchestrator status and component health.
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    return HealthResponse(
        status="healthy" if orchestrator.initialized else "initializing",
        initialized=orchestrator.initialized,
        version="1.0.0",
        components={
            "context_aggregator": orchestrator.context_aggregator is not None,
            "priority_engine": orchestrator.priority_engine is not None,
            "strategy_selector": orchestrator.strategy_selector is not None,
            "safety_monitor": orchestrator.safety_monitor is not None,
            "evolution_engine": orchestrator.evolution_engine is not None,
            "service_registry": orchestrator.service_registry is not None,
            "pdca_engine": orchestrator.pdca_engine is not None,
            "crisis_coordinator": orchestrator.crisis_coordinator is not None,
            "decision_center": orchestrator.decision_center is not None
        }
    )


@app.get("/stats")
async def get_stats():
    """
    Get orchestrator statistics.

    Returns decision counts, execution stats, and component stats.
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    return orchestrator.get_stats()


# ============================================================================
# DECISION-MAKING
# ============================================================================

@app.post("/api/v1/decide", response_model=DecisionResponse)
async def make_decision(request: DecisionRequest):
    """
    Make decision for given situation.

    Args:
        request: Situation data and tenant ID

    Returns:
        Decision with action, rationale, and metadata
    """
    if not orchestrator or not orchestrator.initialized:
        raise HTTPException(status_code=503, detail="Orchestrator not ready")

    try:
        # Make decision
        decision = await orchestrator.decide(
            situation=request.situation,
            tenant_id=request.tenant_id
        )

        return DecisionResponse(
            decision_id=decision.id,
            action=decision.action.value,
            rationale=decision.rationale,
            priority=decision.priority.name,
            confidence=decision.confidence,
            safety_approved=decision.safety_approved,
            metadata=decision.metadata
        )

    except Exception as e:
        logger.error(f"Decision failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Decision failed: {str(e)}")


@app.post("/api/v1/execute", response_model=ExecutionResponse)
async def execute_decision(request: ExecutionRequest):
    """
    Execute a decision.

    Note: Typically decisions are executed immediately after being made.
    This endpoint is for manual execution or retry scenarios.

    Args:
        request: Decision ID to execute

    Returns:
        Execution result
    """
    if not orchestrator or not orchestrator.initialized:
        raise HTTPException(status_code=503, detail="Orchestrator not ready")

    # This is a simplified version - in production you'd look up decision from storage
    raise HTTPException(
        status_code=501,
        detail="Manual execution endpoint not fully implemented. "
               "Use decide() which executes automatically."
    )


# ============================================================================
# CRISIS COORDINATION
# ============================================================================

@app.post("/api/v1/crisis/detect")
async def detect_crisis(situation: Dict[str, Any]):
    """
    Manually trigger crisis detection.

    Args:
        situation: Crisis situation data

    Returns:
        Crisis detection result
    """
    if not orchestrator or not orchestrator.crisis_coordinator:
        raise HTTPException(status_code=503, detail="Crisis coordinator not available")

    crisis_id = await orchestrator.crisis_coordinator.detect_crisis(situation)

    if crisis_id:
        return {
            "crisis_detected": True,
            "crisis_id": crisis_id
        }
    else:
        return {
            "crisis_detected": False,
            "message": "Situation does not constitute crisis"
        }


@app.get("/api/v1/crisis/{crisis_id}/status")
async def get_crisis_status(crisis_id: str):
    """
    Get crisis status.

    Args:
        crisis_id: Crisis identifier

    Returns:
        Crisis status information
    """
    if not orchestrator or not orchestrator.crisis_coordinator:
        raise HTTPException(status_code=503, detail="Crisis coordinator not available")

    status = await orchestrator.crisis_coordinator.monitor_crisis_status(crisis_id)

    if not status.get('exists'):
        raise HTTPException(status_code=404, detail="Crisis not found")

    return status


# ============================================================================
# PROMETHEUS METRICS
# ============================================================================

@app.get("/metrics", response_class=PlainTextResponse)
async def prometheus_metrics():
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus text format for scraping.
    """
    metrics = get_metrics()
    return Response(
        content=metrics.get_latest_metrics(),
        media_type=metrics.get_content_type()
    )


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.post("/admin/evolve")
async def trigger_evolution():
    """
    Manually trigger evolution cycle.

    Returns:
        Evolution result
    """
    if not orchestrator or not orchestrator.evolution_engine:
        raise HTTPException(status_code=503, detail="Evolution engine not available")

    # Trigger evolution
    result = await orchestrator.evolution_engine.run_evolution_cycle()

    return {
        "success": True,
        "improvements_generated": result.get('improvements_count', 0)
    }


@app.get("/admin/memory/stats")
async def get_memory_stats():
    """
    Get memory system statistics.

    Returns:
        Memory layer stats
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    return orchestrator.memory.get_stats()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8050,
        log_level="info"
    )
