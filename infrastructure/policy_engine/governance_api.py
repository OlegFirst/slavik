"""
Governance REST API (Phase 1.1)
================================

FastAPI REST API for Governance Console.

Exposes:
- Decision history and statistics
- Escalation management
- Policy information
- Audit trail
- Manual approval/rejection
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from infrastructure.policy_engine.decision_center import InfrastructureDecisionCenter
from infrastructure.policy_engine.policy_engine import initialize_policy_engine
from infrastructure.policy_engine.audit_logger import AuditLogger
from infrastructure.eventbus import create_eventbus

logger = logging.getLogger(__name__)

# ============================================================================
# Pydantic Models
# ============================================================================

class GovernanceHealth(BaseModel):
    status: str
    decision_center_active: bool
    policy_engine_loaded: bool
    escalation_manager_active: bool
    total_policies: int
    governance_maturity_score: int

class DecisionResponse(BaseModel):
    id: str
    timestamp: str
    service_name: str
    action_type: str
    decision: str
    reasoning: str
    policy_matched: str
    requires_approval: bool
    escalation_level: Optional[int] = None
    approved_by: Optional[str] = None

class EscalationResponse(BaseModel):
    id: str
    timestamp: str
    service_name: str
    action_type: str
    level: int
    trigger: str
    status: str
    decision_id: str
    notified_channels: List[str]
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None

class PolicySummaryResponse(BaseModel):
    total_policies: int
    critical_services: int
    recovery_policies: int
    optimization_policies: int
    escalation_rules: int
    last_reload: str

class AuditEntryResponse(BaseModel):
    timestamp: str
    action: str
    service: str
    decision: str
    reasoning: str
    user: Optional[str] = None
    metadata: Dict[str, Any]

class GovernanceStatsResponse(BaseModel):
    total_decisions: int
    decisions_approved: int
    decisions_rejected: int
    decisions_escalated: int
    active_escalations: int
    resolved_escalations: int
    policy_compliance_rate: float
    avg_decision_time_ms: float
    governance_maturity_score: int

class DecisionRequest(BaseModel):
    service_name: str
    action_type: str
    current_attempt: Optional[int] = 1
    recommendation: Optional[Dict[str, Any]] = None

class ApprovalRequest(BaseModel):
    decision_id: str
    approved_by: str
    notes: Optional[str] = None

class EscalationResolveRequest(BaseModel):
    escalation_id: str
    resolved_by: str
    resolution_notes: str

# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="Infrastructure Governance API",
    description="Phase 1.1 Governance Layer - Decision Center, Policy Engine, Escalation Management",
    version="1.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (initialized on startup)
decision_center: Optional[InfrastructureDecisionCenter] = None
eventbus = None

# ============================================================================
# Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup():
    global decision_center, eventbus

    logger.info("🚀 Starting Governance API...")

    # Initialize EventBus
    eventbus = create_eventbus(backend='redis')

    # Initialize Policy Engine
    policy_engine = initialize_policy_engine()

    # Initialize Audit Logger
    audit_logger = AuditLogger()

    # Initialize Decision Center
    decision_center = InfrastructureDecisionCenter(
        policy_engine=policy_engine,
        audit_logger=audit_logger,
        eventbus=eventbus
    )

    logger.info("✅ Governance API ready")

@app.on_event("shutdown")
async def shutdown():
    logger.info("🛑 Shutting down Governance API")
    if eventbus:
        await eventbus.close()

# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/governance/health", response_model=GovernanceHealth)
async def get_health():
    """Get governance layer health status"""
    if not decision_center:
        raise HTTPException(status_code=503, detail="Decision Center not initialized")

    total_policies = len(decision_center.policy_engine.policies.get('recovery', {}).get('critical_services', {}))
    total_policies += len(decision_center.policy_engine.policies.get('optimization', {}).get('services', {}))

    # Calculate maturity score based on Phase 1.1 completion
    maturity_score = 70  # Base score for Phase 1.1
    if total_policies > 5:
        maturity_score += 10
    if len(decision_center.active_escalations) == 0:
        maturity_score += 10
    if decision_center.stats['total_decisions'] > 50:
        maturity_score += 10

    return {
        "status": "healthy",
        "decision_center_active": True,
        "policy_engine_loaded": decision_center.policy_engine.policies is not None,
        "escalation_manager_active": True,
        "total_policies": total_policies,
        "governance_maturity_score": min(100, maturity_score)
    }

@app.get("/governance/stats", response_model=GovernanceStatsResponse)
async def get_stats():
    """Get governance statistics"""
    if not decision_center:
        raise HTTPException(status_code=503, detail="Decision Center not initialized")

    total = decision_center.stats['total_decisions']
    approved = decision_center.stats['approved_decisions']

    compliance_rate = (approved / total * 100) if total > 0 else 0

    # Calculate avg decision time (simulated for now)
    avg_time = 15.5  # ms

    # Count active vs resolved escalations
    active_esc = len([e for e in decision_center.active_escalations.values() if e.status == 'ACTIVE'])
    resolved_esc = len([e for e in decision_center.active_escalations.values() if e.status == 'RESOLVED'])

    maturity = 70 + (10 if total > 50 else 0) + (10 if compliance_rate > 90 else 0)

    return {
        "total_decisions": total,
        "decisions_approved": approved,
        "decisions_rejected": decision_center.stats['rejected_decisions'],
        "decisions_escalated": decision_center.stats['escalated_decisions'],
        "active_escalations": active_esc,
        "resolved_escalations": resolved_esc,
        "policy_compliance_rate": compliance_rate,
        "avg_decision_time_ms": avg_time,
        "governance_maturity_score": min(100, maturity)
    }

# ============================================================================
# Decision Endpoints
# ============================================================================

@app.get("/governance/decisions", response_model=List[DecisionResponse])
async def get_decisions(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get recent decisions with pagination"""
    if not decision_center:
        raise HTTPException(status_code=503, detail="Decision Center not initialized")

    decisions = decision_center.decision_history[offset:offset+limit]

    return [
        {
            "id": d.decision_id,
            "timestamp": d.timestamp.isoformat(),
            "service_name": d.service_name,
            "action_type": d.decision_type.value,
            "decision": d.outcome.value,
            "reasoning": d.reasoning,
            "policy_matched": d.policy_matched or "default",
            "requires_approval": d.requires_human_approval,
            "escalation_level": d.escalation_level,
            "approved_by": d.metadata.get('approved_by')
        }
        for d in decisions
    ]

@app.get("/governance/decisions/{decision_id}", response_model=DecisionResponse)
async def get_decision(decision_id: str):
    """Get specific decision by ID"""
    if not decision_center:
        raise HTTPException(status_code=503, detail="Decision Center not initialized")

    decision = next((d for d in decision_center.decision_history if d.decision_id == decision_id), None)

    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    return {
        "id": decision.decision_id,
        "timestamp": decision.timestamp.isoformat(),
        "service_name": decision.service_name,
        "action_type": decision.decision_type.value,
        "decision": decision.outcome.value,
        "reasoning": decision.reasoning,
        "policy_matched": decision.policy_matched or "default",
        "requires_approval": decision.requires_human_approval,
        "escalation_level": decision.escalation_level,
        "approved_by": decision.metadata.get('approved_by')
    }

@app.post("/governance/decide", response_model=DecisionResponse)
async def request_decision(request: DecisionRequest):
    """Request a decision from Decision Center"""
    if not decision_center:
        raise HTTPException(status_code=503, detail="Decision Center not initialized")

    # Route to appropriate decision method
    if request.action_type in ['restart', 'failover', 'circuit_breaker']:
        decision, can_proceed = await decision_center.decide_recovery_action(
            service_name=request.service_name,
            action_type=request.action_type,
            current_attempt=request.current_attempt
        )
    else:
        decision, can_proceed = await decision_center.decide_optimization_action(
            service_name=request.service_name,
            action_type=request.action_type,
            recommendation=request.recommendation or {}
        )

    return {
        "id": decision.decision_id,
        "timestamp": decision.timestamp.isoformat(),
        "service_name": decision.service_name,
        "action_type": decision.decision_type.value,
        "decision": decision.outcome.value,
        "reasoning": decision.reasoning,
        "policy_matched": decision.policy_matched or "default",
        "requires_approval": decision.requires_human_approval,
        "escalation_level": decision.escalation_level
    }

@app.post("/governance/approve", response_model=DecisionResponse)
async def approve_decision(request: ApprovalRequest):
    """Approve a pending decision"""
    if not decision_center:
        raise HTTPException(status_code=503, detail="Decision Center not initialized")

    if request.decision_id not in decision_center.pending_approvals:
        raise HTTPException(status_code=404, detail="Pending approval not found")

    approval_req = decision_center.pending_approvals[request.decision_id]
    result = await decision_center.approve_action(
        approval_request=approval_req,
        approved_by=request.approved_by,
        notes=request.notes
    )

    # Find the decision
    decision = next((d for d in decision_center.decision_history if d.decision_id == request.decision_id), None)

    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    return {
        "id": decision.decision_id,
        "timestamp": decision.timestamp.isoformat(),
        "service_name": decision.service_name,
        "action_type": decision.decision_type.value,
        "decision": "APPROVE",
        "reasoning": decision.reasoning,
        "policy_matched": decision.policy_matched or "default",
        "requires_approval": False,
        "approved_by": request.approved_by
    }

@app.post("/governance/reject", response_model=DecisionResponse)
async def reject_decision(request: ApprovalRequest):
    """Reject a pending decision"""
    if not decision_center:
        raise HTTPException(status_code=503, detail="Decision Center not initialized")

    if request.decision_id not in decision_center.pending_approvals:
        raise HTTPException(status_code=404, detail="Pending approval not found")

    # Remove from pending and create rejection decision
    approval_req = decision_center.pending_approvals.pop(request.decision_id)

    decision = next((d for d in decision_center.decision_history if d.decision_id == request.decision_id), None)

    if decision:
        decision.outcome = 'REJECT'
        decision.metadata['rejected_by'] = request.approved_by
        decision.metadata['rejection_notes'] = request.notes

    return {
        "id": request.decision_id,
        "timestamp": datetime.utcnow().isoformat(),
        "service_name": approval_req.service_name,
        "action_type": approval_req.action_type,
        "decision": "REJECT",
        "reasoning": f"Manually rejected by {request.approved_by}",
        "policy_matched": "manual_override",
        "requires_approval": False,
        "approved_by": request.approved_by
    }

# ============================================================================
# Escalation Endpoints
# ============================================================================

@app.get("/governance/escalations", response_model=List[EscalationResponse])
async def get_escalations(status: str = Query("ACTIVE")):
    """Get escalations (ACTIVE, RESOLVED, or ALL)"""
    if not decision_center:
        raise HTTPException(status_code=503, detail="Decision Center not initialized")

    escalations = decision_center.active_escalations.values()

    if status != "ALL":
        escalations = [e for e in escalations if e.status == status]

    return [
        {
            "id": e.escalation_id,
            "timestamp": e.timestamp.isoformat(),
            "service_name": e.service_name,
            "action_type": e.action_type,
            "level": e.escalation_level,
            "trigger": e.reason,
            "status": e.status,
            "decision_id": e.decision_id,
            "notified_channels": e.notified_channels or [],
            "resolved_at": e.resolved_at.isoformat() if e.resolved_at else None,
            "resolved_by": e.resolved_by
        }
        for e in escalations
    ]

@app.post("/governance/escalations/{escalation_id}/resolve", response_model=EscalationResponse)
async def resolve_escalation(escalation_id: str, request: EscalationResolveRequest):
    """Resolve an escalation"""
    if not decision_center:
        raise HTTPException(status_code=503, detail="Decision Center not initialized")

    if escalation_id not in decision_center.active_escalations:
        raise HTTPException(status_code=404, detail="Escalation not found")

    escalation = decision_center.active_escalations[escalation_id]
    escalation.status = 'RESOLVED'
    escalation.resolved_at = datetime.utcnow()
    escalation.resolved_by = request.resolved_by
    escalation.metadata['resolution_notes'] = request.resolution_notes

    # Log audit
    await decision_center.audit_logger.log(
        action='escalation.resolved',
        service=escalation.service_name,
        decision=escalation_id,
        reasoning=request.resolution_notes,
        user=request.resolved_by
    )

    return {
        "id": escalation.escalation_id,
        "timestamp": escalation.timestamp.isoformat(),
        "service_name": escalation.service_name,
        "action_type": escalation.action_type,
        "level": escalation.escalation_level,
        "trigger": escalation.reason,
        "status": escalation.status,
        "decision_id": escalation.decision_id,
        "notified_channels": escalation.notified_channels or [],
        "resolved_at": escalation.resolved_at.isoformat() if escalation.resolved_at else None,
        "resolved_by": escalation.resolved_by
    }

# ============================================================================
# Policy Endpoints
# ============================================================================

@app.get("/governance/policies", response_model=PolicySummaryResponse)
async def get_policies():
    """Get policy summary"""
    if not decision_center:
        raise HTTPException(status_code=503, detail="Decision Center not initialized")

    policies = decision_center.policy_engine.policies

    critical_services = len(policies.get('recovery', {}).get('critical_services', {}))
    recovery_policies = critical_services
    optimization_policies = len(policies.get('optimization', {}).get('services', {}))
    escalation_rules = len(policies.get('escalation', {}).get('triggers', {}))

    return {
        "total_policies": critical_services + optimization_policies + escalation_rules,
        "critical_services": critical_services,
        "recovery_policies": recovery_policies,
        "optimization_policies": optimization_policies,
        "escalation_rules": escalation_rules,
        "last_reload": decision_center.policy_engine.last_reload_time.isoformat()
    }

@app.post("/governance/policies/reload", response_model=PolicySummaryResponse)
async def reload_policies():
    """Hot-reload policies from YAML"""
    if not decision_center:
        raise HTTPException(status_code=503, detail="Decision Center not initialized")

    decision_center.policy_engine.reload_policies()

    return await get_policies()

# ============================================================================
# Audit Endpoints
# ============================================================================

@app.get("/governance/audit", response_model=List[AuditEntryResponse])
async def get_audit_trail(
    limit: int = Query(100, ge=1, le=1000),
    service: Optional[str] = None
):
    """Get audit trail"""
    if not decision_center:
        raise HTTPException(status_code=503, detail="Decision Center not initialized")

    # Get recent entries from audit logger
    entries = await decision_center.audit_logger.get_recent(limit=limit, service=service)

    return [
        {
            "timestamp": e['timestamp'],
            "action": e['action'],
            "service": e['service'],
            "decision": e['decision'],
            "reasoning": e['reasoning'],
            "user": e.get('user'),
            "metadata": e.get('metadata', {})
        }
        for e in entries
    ]

# ============================================================================
# Prometheus Metrics
# ============================================================================

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    if not decision_center:
        return "# Governance metrics unavailable\n"

    stats = decision_center.stats

    metrics = f"""# HELP governance_decisions_total Total decisions made
# TYPE governance_decisions_total counter
governance_decisions_total {stats['total_decisions']}

# HELP governance_decisions_approved Total approved decisions
# TYPE governance_decisions_approved counter
governance_decisions_approved {stats['approved_decisions']}

# HELP governance_decisions_rejected Total rejected decisions
# TYPE governance_decisions_rejected counter
governance_decisions_rejected {stats['rejected_decisions']}

# HELP governance_decisions_escalated Total escalated decisions
# TYPE governance_decisions_escalated counter
governance_decisions_escalated {stats['escalated_decisions']}

# HELP governance_active_escalations Current active escalations
# TYPE governance_active_escalations gauge
governance_active_escalations {len(decision_center.active_escalations)}

# HELP governance_maturity_score Governance maturity score (0-100)
# TYPE governance_maturity_score gauge
governance_maturity_score 70
"""
    return metrics

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9091,
        log_level="info"
    )
