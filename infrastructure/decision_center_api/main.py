"""
Decision Center API - Main Application
=======================================

FastAPI wrapper над InfrastructureDecisionCenter.
Предоставляет REST API для внешних интеграций.
"""

import logging
from typing import List
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# Import enhanced Decision Center
from infrastructure.policy_engine import InfrastructureDecisionCenter
from infrastructure.decision_center.integrations.ai_hub import AIIntelligenceHub
from infrastructure.eventbus import create_eventbus

# Import API models
from .models import (
    DecisionRequest,
    DecisionResponse,
    EscalationRequest,
    EscalationResponse,
    ApprovalRequest,
    ApprovalResponse,
    StatsResponse,
    HealthResponse
)

logger = logging.getLogger(__name__)

# Global Decision Center instance
decision_center: InfrastructureDecisionCenter = None
eventbus = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown"""
    global decision_center, eventbus

    logger.info("🚀 Starting Decision Center API...")

    try:
        # Initialize EventBus (optional)
        try:
            eventbus = create_eventbus('redis')
            await eventbus.connect()
            logger.info("✅ EventBus connected")
        except Exception as e:
            logger.warning(f"⚠️ EventBus connection failed: {e}")
            eventbus = None

        # Initialize AI Hub (optional)
        try:
            ai_hub = AIIntelligenceHub(
                tier1_enabled=False,
                tier2_enabled=False,
                tier3_enabled=True,  # Quick tier for MVP
                tier4_enabled=False
            )
            logger.info("✅ AI Hub initialized")
        except Exception as e:
            logger.warning(f"⚠️ AI Hub initialization failed: {e}")
            ai_hub = None

        # Initialize Decision Center
        decision_center = InfrastructureDecisionCenter(
            ai_hub=ai_hub,
            enable_metrics=True,  # Enable Prometheus
            eventbus=eventbus
        )

        logger.info("✅ Decision Center API started successfully")
        logger.info(f"   - AI Hub: {'Enabled' if ai_hub else 'Disabled'}")
        logger.info(f"   - Metrics: Enabled")
        logger.info(f"   - EventBus: {'Connected' if eventbus else 'Disconnected'}")

        yield

    finally:
        # Cleanup
        logger.info("🛑 Shutting down Decision Center API...")
        if eventbus:
            await eventbus.close()
        logger.info("✅ Decision Center API shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Decision Center API",
    description="Infrastructure Decision Center REST API",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================
# Health & Status Endpoints
# ============================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        decision_center="running",
        ai_hub_available=decision_center.ai_hub is not None,
        metrics_enabled=decision_center.enable_metrics,
        eventbus_connected=eventbus is not None and eventbus.connected
    )


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint"""
    if not decision_center.enable_metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metrics not enabled"
        )

    return PlainTextResponse(
        content=generate_latest().decode('utf-8'),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get Decision Center statistics"""
    stats = await decision_center.get_stats()
    return StatsResponse(**stats)


# ============================================
# Decision Endpoints
# ============================================

@app.post("/api/v1/decisions", response_model=DecisionResponse)
async def request_decision(request: DecisionRequest):
    """
    Request a decision for infrastructure action

    This is the main endpoint for decision requests.
    Wraps `decide_recovery_action()` from InfrastructureDecisionCenter.
    """
    try:
        logger.info(f"📥 Decision request: {request.service} - {request.action}")

        # Call Decision Center
        decision, can_proceed = await decision_center.decide_recovery_action(
            service_name=request.service,
            action_type=request.action,
            trigger_data={
                'reason': request.reason,
                'context': request.context,
                'priority': request.priority
            },
            current_attempt=request.current_attempt
        )

        # Convert to API response
        response = DecisionResponse(
            decision_id=decision.decision_id,
            outcome=decision.outcome.value,
            can_proceed=can_proceed,
            reasoning=decision.reasoning,
            confidence_score=decision.confidence_score,
            policy_reference=decision.policy_reference,
            requires_approval=decision.requires_approval,
            ai_enhanced=decision.parameters.get('ai_enhanced', False),
            ai_confidence=decision.parameters.get('ai_confidence'),
            ai_model=decision.parameters.get('ai_model'),
            decided_at=decision.decided_at
        )

        logger.info(f"📤 Decision response: {decision.outcome.value} (can_proceed: {can_proceed})")

        return response

    except Exception as e:
        logger.error(f"❌ Error processing decision request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Decision processing failed: {str(e)}"
        )


@app.get("/api/v1/decisions/{decision_id}")
async def get_decision(decision_id: str):
    """Get decision by ID (from history)"""
    # Search in decision history
    for decision in decision_center.decision_history:
        if decision.decision_id == decision_id:
            return DecisionResponse(
                decision_id=decision.decision_id,
                outcome=decision.outcome.value,
                can_proceed=decision.outcome.value == "approved",
                reasoning=decision.reasoning,
                confidence_score=decision.confidence_score,
                policy_reference=decision.policy_reference,
                requires_approval=decision.requires_approval,
                ai_enhanced=decision.parameters.get('ai_enhanced', False),
                ai_confidence=decision.parameters.get('ai_confidence'),
                ai_model=decision.parameters.get('ai_model'),
                decided_at=decision.decided_at
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Decision {decision_id} not found"
    )


# ============================================
# Escalation Endpoints
# ============================================

@app.post("/api/v1/escalations", response_model=EscalationResponse)
async def create_escalation(request: EscalationRequest):
    """Create escalation to human operators"""
    try:
        logger.info(f"🚨 Escalation request: {request.service} - {request.reason}")

        escalation = await decision_center.escalate(
            service_name=request.service,
            reason=request.reason,
            decision_id=request.decision_id,
            severity=request.severity,
            context_data=request.context
        )

        response = EscalationResponse(
            escalation_id=escalation.escalation_id,
            service=escalation.service_name,
            severity=escalation.severity,
            reason=escalation.reason,
            status=escalation.status.value,
            assigned_team=escalation.assigned_team,
            created_at=escalation.created_at
        )

        logger.info(f"✅ Escalation created: {escalation.escalation_id}")

        return response

    except Exception as e:
        logger.error(f"❌ Error creating escalation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Escalation creation failed: {str(e)}"
        )


@app.get("/api/v1/escalations", response_model=List[EscalationResponse])
async def get_escalations():
    """Get all active escalations"""
    escalations = await decision_center.get_active_escalations()

    return [
        EscalationResponse(
            escalation_id=esc.escalation_id,
            service=esc.service_name,
            severity=esc.severity,
            reason=esc.reason,
            status=esc.status.value,
            assigned_team=esc.assigned_team,
            created_at=esc.created_at
        )
        for esc in escalations
    ]


@app.get("/api/v1/escalations/{escalation_id}")
async def get_escalation(escalation_id: str):
    """Get escalation by ID"""
    escalation = decision_center.active_escalations.get(escalation_id)

    if not escalation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Escalation {escalation_id} not found"
        )

    return EscalationResponse(
        escalation_id=escalation.escalation_id,
        service=escalation.service_name,
        severity=escalation.severity,
        reason=escalation.reason,
        status=escalation.status.value,
        assigned_team=escalation.assigned_team,
        created_at=escalation.created_at
    )


# ============================================
# Approval Endpoints
# ============================================

@app.get("/api/v1/approvals")
async def get_pending_approvals():
    """Get all pending approvals"""
    approvals = await decision_center.get_pending_approvals()

    return [
        {
            "approval_id": appr.approval_id,
            "service": appr.service_name,
            "action": appr.action_type,
            "justification": appr.justification,
            "status": appr.status.value,
            "required_approvers": appr.required_approvers,
            "expires_at": appr.expires_at,
            "created_at": appr.created_at
        }
        for appr in approvals
    ]


@app.post("/api/v1/approvals/respond", response_model=ApprovalResponse)
async def respond_to_approval(request: ApprovalRequest):
    """Approve or reject pending approval"""
    try:
        logger.info(
            f"📋 Approval response: {request.approval_id} - "
            f"{'APPROVED' if request.approved else 'REJECTED'} by {request.approved_by}"
        )

        can_proceed = await decision_center.approve_action(
            approval_id=request.approval_id,
            approved_by=request.approved_by,
            approved=request.approved,
            comment=request.comment
        )

        # Get updated approval
        approval = decision_center.pending_approvals.get(request.approval_id)

        if not approval:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Approval {request.approval_id} not found"
            )

        response = ApprovalResponse(
            approval_id=approval.approval_id,
            status=approval.status.value,
            can_proceed=can_proceed,
            decision_by=request.approved_by,
            decided_at=approval.approved_at or approval.rejected_at or datetime.utcnow()
        )

        logger.info(f"✅ Approval processed: {approval.status.value}")

        return response

    except Exception as e:
        logger.error(f"❌ Error processing approval: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Approval processing failed: {str(e)}"
        )


# ============================================
# Root Endpoint
# ============================================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "service": "Decision Center API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "stats": "/stats",
            "decisions": "/api/v1/decisions",
            "escalations": "/api/v1/escalations",
            "approvals": "/api/v1/approvals"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
