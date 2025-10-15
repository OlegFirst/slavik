"""
Decision Center - FastAPI Application
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from ..core.decision_engine import DecisionEngine
from ..core.policy_engine import PolicyEngine
from ..core.escalation_manager import EscalationManager
from ..integrations.ai_hub_v2 import AIIntelligenceHub
from ..utils.audit_logger import AuditLogger
from ..utils.metrics import initialize_metrics
from ..models.decision import DecisionRequest, Decision

# EventBus integration for deep AI consultation
try:
    from infrastructure.eventbus import create_eventbus
    EVENTBUS_AVAILABLE = True
except ImportError:
    EVENTBUS_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Decision Center API",
    description="AI-driven decision making for infrastructure automation",
    version="1.0.0-mvp"
)

# Global components (initialized on startup)
policy_engine: Optional[PolicyEngine] = None
escalation_manager: Optional[EscalationManager] = None
audit_logger: Optional[AuditLogger] = None
ai_hub: Optional[AIIntelligenceHub] = None
decision_engine: Optional[DecisionEngine] = None
eventbus: Optional[Any] = None  # EventBus instance


# Pydantic models for API
class DecisionRequestModel(BaseModel):
    """API model for decision request"""
    service: str = Field(..., description="Service name (e.g., 'database', 'redis')")
    action: str = Field(..., description="Action to perform (e.g., 'restart', 'scale_up')")
    reason: str = Field(..., description="Reason for action")
    priority: int = Field(3, ge=1, le=5, description="Priority 1-5 (1=critical)")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    requester: str = Field("api", description="Requester identifier")


class DecisionResponseModel(BaseModel):
    """API model for decision response"""
    decision_id: str
    request_id: str
    decision_type: str
    outcome: str
    action: str
    justification: str
    decided_by: str
    decided_at: str
    expires_at: Optional[str]
    metadata: Dict[str, Any]


class EscalationResponseModel(BaseModel):
    """API model for escalation response"""
    escalation_id: str
    approved: bool
    operator: str
    resolution: str


class HealthResponse(BaseModel):
    """API model for health check"""
    status: str
    version: str
    components: Dict[str, str]


@app.on_event("startup")
async def startup():
    """Initialize components on startup"""
    global policy_engine, escalation_manager, audit_logger, ai_hub, decision_engine, eventbus

    logger.info("Starting Decision Center API...")

    # Initialize metrics
    initialize_metrics(version="1.0.0-mvp", environment="production")

    # Initialize components
    policy_engine = PolicyEngine(policy_file="policies.yaml")
    escalation_manager = EscalationManager()
    audit_logger = AuditLogger(log_dir="/var/log/decision_center")

    # Initialize AI Hub with real Claude integration
    # Tier 2 (Sonnet) is primary, Tier 3 (Haiku) for quick responses
    # Set ANTHROPIC_API_KEY env var to enable real AI
    ai_hub = AIIntelligenceHub(
        tier2_enabled=True,   # Claude Sonnet (primary)
        tier3_enabled=True,   # Claude Haiku (quick)
        tier1_enabled=False,  # Claude Opus (expensive, disabled by default)
        enable_fallback=True  # Fallback to heuristics if API unavailable
    )

    # Initialize EventBus for deep AI integration (optional)
    enable_deep_ai = False
    if EVENTBUS_AVAILABLE:
        try:
            logger.info("Initializing EventBus for deep AI integration...")
            eventbus = create_eventbus('memory')  # Start with memory backend for MVP
            await eventbus.connect()
            enable_deep_ai = True
            logger.info("✅ EventBus connected - deep AI integration enabled")
        except Exception as e:
            logger.warning(f"EventBus initialization failed: {e}")
            logger.warning("⚠️  Running without deep AI integration (direct AI Hub only)")
            eventbus = None
    else:
        logger.info("EventBus not available - running with direct AI Hub only")

    decision_engine = DecisionEngine(
        policy_engine=policy_engine,
        escalation_manager=escalation_manager,
        audit_logger=audit_logger,
        ai_hub=ai_hub,
        eventbus=eventbus,
        enable_deep_ai_integration=enable_deep_ai
    )

    logger.info("Decision Center API started successfully")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    global eventbus

    logger.info("Shutting down Decision Center API...")

    # Disconnect EventBus if connected
    if eventbus:
        try:
            await eventbus.disconnect()
            logger.info("✅ EventBus disconnected")
        except Exception as e:
            logger.error(f"EventBus disconnect error: {e}")

    logger.info("Decision Center API shutdown complete")


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "service": "Decision Center API",
        "version": "1.0.0-mvp",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    components = {
        "policy_engine": "ok" if policy_engine else "not_initialized",
        "decision_engine": "ok" if decision_engine else "not_initialized",
        "escalation_manager": "ok" if escalation_manager else "not_initialized",
        "audit_logger": "ok" if audit_logger else "not_initialized",
        "ai_hub": "ok" if ai_hub else "not_initialized"
    }

    # Add EventBus status if enabled
    if eventbus:
        components["eventbus"] = "connected"
        components["deep_ai_integration"] = "enabled"
    elif EVENTBUS_AVAILABLE:
        components["eventbus"] = "available_but_disconnected"
        components["deep_ai_integration"] = "disabled"
    else:
        components["eventbus"] = "not_available"
        components["deep_ai_integration"] = "not_available"

    return HealthResponse(
        status="healthy",
        version="1.0.0-mvp",
        components=components
    )


@app.post("/api/v1/decisions", response_model=DecisionResponseModel)
async def make_decision(request: DecisionRequestModel):
    """
    Make a decision

    This is the primary endpoint for requesting decisions.
    Infrastructure Coordinator calls this endpoint when it needs
    approval for an action.

    Args:
        request: Decision request

    Returns:
        Decision result

    Example:
        POST /api/v1/decisions
        {
            "service": "database",
            "action": "restart",
            "reason": "High memory usage detected",
            "priority": 2,
            "context": {
                "recovery_attempts": 1,
                "downtime_seconds": 120,
                "memory_usage_percent": 95
            },
            "requester": "infrastructure_coordinator"
        }
    """
    if not decision_engine:
        raise HTTPException(status_code=503, detail="Decision Engine not initialized")

    try:
        # Convert API model to domain model
        decision_request = DecisionRequest.create(
            service=request.service,
            action=request.action,
            reason=request.reason,
            priority=request.priority,
            context=request.context,
            requester=request.requester
        )

        # Make decision
        decision = await decision_engine.make_decision(decision_request)

        # Convert to API response
        return DecisionResponseModel(
            decision_id=decision.decision_id,
            request_id=decision.request_id,
            decision_type=decision.decision_type.value,
            outcome=decision.outcome.value,
            action=decision.action,
            justification=decision.justification,
            decided_by=decision.decided_by,
            decided_at=decision.decided_at.isoformat() + "Z",
            expires_at=decision.expires_at.isoformat() + "Z" if decision.expires_at else None,
            metadata=decision.metadata
        )

    except Exception as e:
        logger.error(f"Decision making failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Decision failed: {str(e)}")


@app.get("/api/v1/decisions/{decision_id}", response_model=DecisionResponseModel)
async def get_decision(decision_id: str):
    """
    Get decision by ID

    Args:
        decision_id: Decision ID

    Returns:
        Decision details

    Note:
        MVP implementation returns 404.
        Full implementation would query decision storage.
    """
    # TODO: Implement decision storage and retrieval
    raise HTTPException(status_code=404, detail="Decision storage not implemented in MVP")


@app.get("/api/v1/escalations", response_model=List[Dict[str, Any]])
async def list_escalations():
    """
    List active escalations

    Returns:
        List of active escalation requests
    """
    if not escalation_manager:
        raise HTTPException(status_code=503, detail="Escalation Manager not initialized")

    escalations = escalation_manager.get_active_escalations()

    return [
        {
            "escalation_id": esc.escalation_id,
            "service": esc.original_request.service,
            "action": esc.original_request.action,
            "escalation_level": esc.escalation_level.value,
            "urgency": esc.urgency,
            "reason": esc.reason,
            "assigned_to": esc.assigned_to,
            "created_at": esc.created_at.isoformat() + "Z"
        }
        for esc in escalations
    ]


@app.post("/api/v1/escalations/{escalation_id}/respond", response_model=DecisionResponseModel)
async def respond_to_escalation(
    escalation_id: str,
    response: EscalationResponseModel
):
    """
    Respond to escalation

    Operators use this endpoint to approve or reject escalated decisions.

    Args:
        escalation_id: Escalation ID
        response: Operator response

    Returns:
        Final decision

    Example:
        POST /api/v1/escalations/{id}/respond
        {
            "approved": true,
            "operator": "john.doe@company.com",
            "resolution": "Approved restart after reviewing metrics"
        }
    """
    if not escalation_manager:
        raise HTTPException(status_code=503, detail="Escalation Manager not initialized")

    try:
        decision = await escalation_manager.respond_to_escalation(
            escalation_id=escalation_id,
            approved=response.approved,
            operator=response.operator,
            resolution=response.resolution
        )

        return DecisionResponseModel(
            decision_id=decision.decision_id,
            request_id=decision.request_id,
            decision_type=decision.decision_type.value,
            outcome=decision.outcome.value,
            action=decision.action,
            justification=decision.justification,
            decided_by=decision.decided_by,
            decided_at=decision.decided_at.isoformat() + "Z",
            expires_at=decision.expires_at.isoformat() + "Z" if decision.expires_at else None,
            metadata=decision.metadata
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Escalation response failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Response failed: {str(e)}")


@app.get("/api/v1/policies/{service}", response_model=Dict[str, Any])
async def get_service_policies(service: str):
    """
    Get policies for service

    Args:
        service: Service name

    Returns:
        Service policies
    """
    if not policy_engine:
        raise HTTPException(status_code=503, detail="Policy Engine not initialized")

    try:
        policies = policy_engine.get_policies(service)
        return policies

    except Exception as e:
        logger.error(f"Failed to get policies: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get policies: {str(e)}")


@app.post("/api/v1/policies/reload")
async def reload_policies():
    """
    Reload policies from file

    Returns:
        Reload status
    """
    if not policy_engine:
        raise HTTPException(status_code=503, detail="Policy Engine not initialized")

    try:
        policy_engine.load_policies()
        return {
            "status": "success",
            "message": "Policies reloaded",
            "last_loaded": policy_engine.last_loaded.isoformat() + "Z"
        }

    except Exception as e:
        logger.error(f"Failed to reload policies: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Reload failed: {str(e)}")


@app.get("/api/v1/audit/history/{service}")
async def get_decision_history(service: str, days: int = 30):
    """
    Get decision history for service

    Args:
        service: Service name
        days: Number of days to look back (default 30)

    Returns:
        Decision history statistics
    """
    if not audit_logger:
        raise HTTPException(status_code=503, detail="Audit Logger not initialized")

    try:
        history = await audit_logger.get_decision_history(service, days)
        return history

    except Exception as e:
        logger.error(f"Failed to get history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@app.get("/api/v1/ai/status")
async def get_ai_status():
    """
    Get AI tier status

    Returns:
        AI tier information and status
    """
    if not ai_hub:
        raise HTTPException(status_code=503, detail="AI Hub not initialized")

    try:
        status = await ai_hub.get_tier_status()
        return status

    except Exception as e:
        logger.error(f"Failed to get AI status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get AI status: {str(e)}")


@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint

    Returns:
        Prometheus metrics in text format
    """
    return PlainTextResponse(
        content=generate_latest().decode('utf-8'),
        media_type=CONTENT_TYPE_LATEST
    )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "status_code": 500
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
