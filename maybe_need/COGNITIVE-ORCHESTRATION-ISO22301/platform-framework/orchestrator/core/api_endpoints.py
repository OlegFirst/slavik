"""
API Endpoints for BCM Event-Driven Architecture
FastAPI routes for workflow management
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import uuid

from .event_bus import event_bus, Event, EventType
from .ai_orchestrator import orchestrator
from .workflow_handlers import workflow_orchestrator

router = APIRouter(prefix="/api/v1/orchestrator", tags=["orchestrator"])


# ============================================
# Request/Response Models
# ============================================

class EventPublishRequest(BaseModel):
    """Request model for publishing events"""
    type: str = Field(..., description="Event type (e.g., bcm.bia.completed)")
    tenant_id: str = Field(..., description="Tenant identifier")
    actor: str = Field(..., description="User or system that triggered the event")
    module: str = Field(..., description="BCM module name")
    data: Dict[str, Any] = Field(..., description="Event payload data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class WorkflowStartRequest(BaseModel):
    """Request to start a workflow"""
    workflow_type: str = Field(..., description="Type of workflow (bia, incident, audit)")
    tenant_id: str
    user_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class BIAStartRequest(BaseModel):
    """Request to start BIA process"""
    tenant_id: str
    user_id: str
    departments: List[str] = Field(..., description="List of departments for BIA")


class IncidentReportRequest(BaseModel):
    """Request to report an incident"""
    tenant_id: str
    title: str
    description: str
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    type: str = Field(default="operational")
    affected_systems: List[str] = Field(default_factory=list)


class AuditStartRequest(BaseModel):
    """Request to start audit"""
    tenant_id: str
    auditor_id: str
    audit_type: str = Field(default="ISO_22301")
    scope: List[str] = Field(default_factory=list)


class DecisionApprovalRequest(BaseModel):
    """Request to approve/reject AI decision"""
    decision_id: str
    approved: bool
    approved_by: str
    comments: Optional[str] = None


# ============================================
# Event Management Endpoints
# ============================================

@router.post("/events/publish")
async def publish_event(request: EventPublishRequest, background_tasks: BackgroundTasks):
    """
    Publish an event to the event bus
    
    This endpoint allows manual event publishing for testing or integration
    """
    try:
        event = Event(
            id=str(uuid.uuid4()),
            type=EventType(request.type),
            timestamp=datetime.utcnow(),
            actor=request.actor,
            tenant_id=request.tenant_id,
            module=request.module,
            data=request.data,
            metadata=request.metadata
        )
        
        background_tasks.add_task(event_bus.publish, event)
        
        return JSONResponse(
            status_code=202,
            content={
                "message": "Event accepted for processing",
                "event_id": event.id,
                "type": request.type
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid event type: {request.type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/{tenant_id}")
async def get_events(
    tenant_id: str,
    event_type: Optional[str] = None,
    limit: int = 100,
    days: int = 7
):
    """
    Get events for a tenant
    
    Query parameters:
    - event_type: Filter by specific event type
    - limit: Maximum number of events to return
    - days: Number of days to look back
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        events = await event_bus.get_events(
            tenant_id=tenant_id,
            event_type=EventType(event_type) if event_type else None,
            start_date=start_date,
            limit=limit
        )
        
        return {
            "tenant_id": tenant_id,
            "count": len(events),
            "events": [e.to_dict() for e in events]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/{tenant_id}/stats")
async def get_event_stats(tenant_id: str):
    """Get event statistics for a tenant"""
    try:
        stats = event_bus.get_event_stats(tenant_id)
        return {
            "tenant_id": tenant_id,
            "statistics": stats,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Workflow Management Endpoints
# ============================================

@router.post("/workflows/bia/start")
async def start_bia_workflow(request: BIAStartRequest, background_tasks: BackgroundTasks):
    """
    Start Business Impact Analysis workflow
    
    This triggers the BIA subprocess defined in BPMN
    """
    try:
        process_id = await workflow_orchestrator.bia_handler.start_bia_process(
            tenant_id=request.tenant_id,
            user_id=request.user_id,
            departments=request.departments
        )
        
        return {
            "process_id": process_id,
            "status": "started",
            "message": f"BIA process started for {len(request.departments)} departments"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/incident/report")
async def report_incident(request: IncidentReportRequest, background_tasks: BackgroundTasks):
    """
    Report a new incident
    
    This triggers the incident handling subprocess
    """
    try:
        incident_id = str(uuid.uuid4())
        
        # Create incident event
        event = Event(
            id=str(uuid.uuid4()),
            type=EventType.INCIDENT_OPENED,
            timestamp=datetime.utcnow(),
            actor="user",
            tenant_id=request.tenant_id,
            module="bcm_incident",
            data={
                "id": incident_id,
                "title": request.title,
                "description": request.description,
                "severity": request.severity,
                "type": request.type,
                "affected_systems": request.affected_systems,
                "reported_at": datetime.utcnow().isoformat()
            }
        )
        
        background_tasks.add_task(event_bus.publish, event)
        
        return {
            "incident_id": incident_id,
            "status": "reported",
            "message": "Incident reported and AI analysis initiated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/audit/start")
async def start_audit_workflow(request: AuditStartRequest, background_tasks: BackgroundTasks):
    """
    Start audit workflow
    
    This triggers the audit subprocess defined in BPMN
    """
    try:
        audit_id = await workflow_orchestrator.audit_handler.start_audit_process(
            tenant_id=request.tenant_id,
            auditor_id=request.auditor_id,
            audit_type=request.audit_type
        )
        
        return {
            "audit_id": audit_id,
            "type": request.audit_type,
            "status": "started",
            "checklist_items": len(
                workflow_orchestrator.audit_handler.audit_sessions[audit_id]["checklist"]
            )
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/pdca/start")
async def start_pdca_cycle(tenant_id: str, user_id: str):
    """
    Start complete PDCA cycle
    
    This initiates the full PDCA workflow as defined in BPMN
    """
    try:
        cycle_id = await workflow_orchestrator.execute_pdca_cycle(tenant_id, user_id)
        
        return {
            "cycle_id": cycle_id,
            "tenant_id": tenant_id,
            "status": "initiated",
            "phases": ["PLAN", "DO", "CHECK", "ACT"],
            "message": "PDCA cycle initiated - starting with context import"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# AI Orchestrator Endpoints
# ============================================

@router.get("/ai/decisions/{tenant_id}")
async def get_ai_decisions(tenant_id: str, limit: int = 50):
    """Get AI orchestrator decisions for a tenant"""
    try:
        decisions = orchestrator.get_decision_history(tenant_id, limit)
        
        return {
            "tenant_id": tenant_id,
            "count": len(decisions),
            "decisions": [
                {
                    "id": d.id,
                    "timestamp": d.timestamp.isoformat(),
                    "event_type": d.event.type.value,
                    "rules_applied": d.rules_applied,
                    "reasoning": d.reasoning,
                    "confidence": d.confidence,
                    "approved": d.approved,
                    "actions_taken": d.actions_taken
                }
                for d in decisions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/decisions/{tenant_id}/pending")
async def get_pending_approvals(tenant_id: str):
    """Get AI decisions pending approval"""
    try:
        pending = orchestrator.get_pending_approvals(tenant_id)
        
        return {
            "tenant_id": tenant_id,
            "count": len(pending),
            "pending_decisions": [
                {
                    "id": d.id,
                    "timestamp": d.timestamp.isoformat(),
                    "event_type": d.event.type.value,
                    "reasoning": d.reasoning,
                    "confidence": d.confidence,
                    "actions_proposed": [a["type"] for a in d.actions_taken]
                }
                for d in pending
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/decisions/approve")
async def approve_decision(request: DecisionApprovalRequest):
    """Approve or reject an AI orchestrator decision"""
    try:
        await orchestrator.approve_decision(
            decision_id=request.decision_id,
            approved_by=request.approved_by,
            approved=request.approved
        )
        
        return {
            "decision_id": request.decision_id,
            "status": "approved" if request.approved else "rejected",
            "approved_by": request.approved_by,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/rules")
async def get_orchestration_rules():
    """Get current orchestration rules"""
    try:
        rules = []
        for rule in orchestrator.rules:
            rules.append({
                "name": rule.name,
                "event_type": rule.event_type.value,
                "conditions": rule.conditions,
                "actions": [a.value for a in rule.actions],
                "priority": rule.priority,
                "enabled": rule.enabled
            })
        
        return {
            "count": len(rules),
            "rules": rules
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Management Review Endpoints
# ============================================

@router.post("/governance/review")
async def conduct_management_review(
    tenant_id: str,
    kpi_achievement: int,
    incidents_handled: int,
    compliance_score: float,
    audit_findings: List[str] = None
):
    """Conduct management review (ACT phase)"""
    try:
        review_data = {
            "kpi_achievement": kpi_achievement,
            "incidents_handled": incidents_handled,
            "compliance_score": compliance_score,
            "audit_findings": audit_findings or []
        }
        
        review = await workflow_orchestrator.governance_handler.conduct_management_review(
            tenant_id=tenant_id,
            review_data=review_data
        )
        
        return {
            "review_id": review["id"],
            "tenant_id": tenant_id,
            "decisions": review["decisions"],
            "improvements_needed": review["improvements_needed"],
            "next_action": "restart_cycle" if review["improvements_needed"] else "maintain"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Health & Status Endpoints
# ============================================

@router.get("/health")
async def health_check():
    """Health check for orchestrator services"""
    return {
        "status": "healthy",
        "services": {
            "event_bus": "connected" if event_bus.redis_client else "disconnected",
            "ai_orchestrator": "running" if orchestrator.running else "stopped",
            "timestamp": datetime.utcnow().isoformat()
        }
    }


@router.post("/startup")
async def startup_services():
    """Initialize orchestrator services"""
    try:
        # Connect event bus
        await event_bus.connect()
        
        # Start AI orchestrator
        await orchestrator.start()
        
        return {
            "status": "started",
            "message": "Orchestrator services initialized successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start services: {str(e)}")


@router.post("/shutdown")
async def shutdown_services():
    """Gracefully shutdown orchestrator services"""
    try:
        # Stop AI orchestrator
        await orchestrator.stop()
        
        # Disconnect event bus
        await event_bus.disconnect()
        
        return {
            "status": "stopped",
            "message": "Orchestrator services shut down successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to shutdown services: {str(e)}")
