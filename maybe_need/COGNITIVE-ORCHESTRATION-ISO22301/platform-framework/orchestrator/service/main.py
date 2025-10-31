"""
AI Orchestrator Service - FastAPI
ISO 22301 BCM Platform Intelligent Decision Engine
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import json
import os
import redis.asyncio as redis
from contextlib import asynccontextmanager
import logging
import httpx

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
EVENTBUS_URL = os.getenv("EVENTBUS_URL", "http://localhost:8001")
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8081,http://localhost:8069").split(",")

# Global connections
redis_client = None
pending_decisions = {}

# Models
class RecommendationRequest(BaseModel):
    context: str = Field(..., description="Context for recommendation")
    data: Dict[str, Any] = Field(..., description="Data for analysis")
    tenant_id: str = Field(..., description="Tenant identifier")
    user_id: Optional[str] = Field(None, description="User requesting recommendation")

class RecommendationResponse(BaseModel):
    recommendation: str
    confidence: float
    reasoning: str
    alternatives: List[Dict[str, Any]] = []

class AuditSummaryRequest(BaseModel):
    audit_id: str
    evidence: List[Dict[str, Any]]
    tenant_id: str

class AuditSummaryResponse(BaseModel):
    summary: str
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    capa_items: List[Dict[str, Any]]

class AIDecision(BaseModel):
    id: str
    type: str
    title: str
    description: str
    recommendation: str
    confidence: float
    status: str = "pending"  # pending, approved, rejected
    created_at: datetime
    tenant_id: str
    data: Dict[str, Any] = {}

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    
    # Startup
    logger.info("Starting AI Orchestrator service...")
    
    # Redis connection
    redis_client = await redis.from_url(REDIS_URL)
    logger.info("Connected to Redis")
    
    # Start event listener in background
    asyncio.create_task(event_listener())
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Orchestrator service...")
    if redis_client:
        await redis_client.close()

# Create FastAPI app
app = FastAPI(
    title="BCM AI Orchestrator Service",
    description="Intelligent decision engine for ISO 22301 BCM Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Event listener
async def event_listener():
    """Subscribe to Redis and process BCM events"""
    pubsub = redis_client.pubsub()
    await pubsub.psubscribe("bcm.*")
    
    logger.info("Event listener started, subscribed to bcm.* events")
    
    async for message in pubsub.listen():
        if message["type"] == "pmessage":
            try:
                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                
                event = json.loads(data)
                await process_event(event)
            except Exception as e:
                logger.error(f"Error processing event: {e}")

async def process_event(event: Dict[str, Any]):
    """Process incoming BCM events and generate decisions"""
    event_type = event.get("event_type", "")
    tenant_id = event.get("tenant_id", "")
    
    logger.info(f"Processing event: {event_type} for tenant {tenant_id}")
    
    # Enhanced rule-based decision engine with auto-triggers
    if event_type == "bcm.bia.completed":
        await handle_bia_completed(event)
        # Auto-trigger: Generate BCP draft
        await trigger_bcp_generation(event)
    elif event_type == "bcm.incident.opened" or event_type == "bcm.incident.reported":
        await handle_incident_opened(event)
        # Auto-trigger: Generate response checklist
        await trigger_incident_response(event)
    elif event_type == "bcm.audit.initiated":
        await handle_audit_initiated(event)
    elif event_type == "bcm.training.scheduled":
        await handle_training_scheduled(event)
    elif event_type == "bcm.plan.draft_requested":
        # Auto-trigger: Generate plan draft based on BIA
        await trigger_plan_draft_generation(event)
    elif event_type == "bcm.kpi.calculated":
        # Auto-trigger: Generate improvement recommendations if KPIs are low
        await trigger_kpi_recommendations(event)

async def handle_bia_completed(event: Dict[str, Any]):
    """Generate BCP draft when BIA is completed"""
    tenant_id = event["tenant_id"]
    bia_data = event.get("data", {})
    
    # Create AI decision
    decision = AIDecision(
        id=f"decision_{datetime.utcnow().timestamp()}",
        type="bcp_generation",
        title="Generate Business Continuity Plan",
        description=f"BIA completed with {len(bia_data.get('critical_processes', []))} critical processes identified",
        recommendation="Generate comprehensive BCP based on BIA results",
        confidence=0.92,
        status="pending",
        created_at=datetime.utcnow(),
        tenant_id=tenant_id,
        data={
            "bia_id": bia_data.get("bia_id"),
            "critical_processes": bia_data.get("critical_processes", []),
            "rto_targets": bia_data.get("rto_targets", {}),
            "rpo_targets": bia_data.get("rpo_targets", {})
        }
    )
    
    # Store in pending decisions
    pending_decisions[decision.id] = decision
    
    # Publish event
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{EVENTBUS_URL}/api/events/publish",
            json={
                "event_type": "bcm.ai.decision.created",
                "tenant_id": tenant_id,
                "data": decision.dict()
            }
        )

async def handle_incident_opened(event: Dict[str, Any]):
    """Generate response checklist for new incident"""
    tenant_id = event["tenant_id"]
    incident_data = event.get("data", {})
    
    decision = AIDecision(
        id=f"decision_{datetime.utcnow().timestamp()}",
        type="incident_response",
        title="Incident Response Checklist",
        description=f"Critical incident: {incident_data.get('title', 'Unknown')}",
        recommendation="Execute immediate response actions",
        confidence=0.88,
        status="pending",
        created_at=datetime.utcnow(),
        tenant_id=tenant_id,
        data={
            "incident_id": incident_data.get("incident_id"),
            "severity": incident_data.get("severity", "high"),
            "checklist": generate_incident_checklist(incident_data)
        }
    )
    
    pending_decisions[decision.id] = decision

async def handle_audit_initiated(event: Dict[str, Any]):
    """Prepare audit recommendations"""
    tenant_id = event["tenant_id"]
    audit_data = event.get("data", {})
    
    decision = AIDecision(
        id=f"decision_{datetime.utcnow().timestamp()}",
        type="audit_preparation",
        title="Audit Preparation Recommendations",
        description=f"Audit scheduled for {audit_data.get('audit_date', 'TBD')}",
        recommendation="Review and prepare required documentation",
        confidence=0.85,
        status="pending",
        created_at=datetime.utcnow(),
        tenant_id=tenant_id,
        data={
            "audit_id": audit_data.get("audit_id"),
            "scope": audit_data.get("scope", []),
            "requirements": generate_audit_requirements(audit_data)
        }
    )
    
    pending_decisions[decision.id] = decision

async def handle_training_scheduled(event: Dict[str, Any]):
    """Generate training materials recommendations"""
    pass

def generate_incident_checklist(incident_data: Dict) -> List[Dict]:
    """Generate incident response checklist based on incident type"""
    severity = incident_data.get("severity", "medium")
    
    checklist = [
        {"task": "Assess immediate impact", "priority": "critical", "deadline": "15 minutes"},
        {"task": "Notify crisis management team", "priority": "critical", "deadline": "30 minutes"},
        {"task": "Activate communication protocols", "priority": "high", "deadline": "1 hour"},
        {"task": "Document incident timeline", "priority": "high", "deadline": "2 hours"},
    ]
    
    if severity == "critical":
        checklist.extend([
            {"task": "Activate alternate site", "priority": "critical", "deadline": "1 hour"},
            {"task": "Notify executive management", "priority": "critical", "deadline": "30 minutes"},
            {"task": "Prepare external communications", "priority": "high", "deadline": "2 hours"},
        ])
    
    return checklist

def generate_audit_requirements(audit_data: Dict) -> List[Dict]:
    """Generate audit preparation requirements"""
    return [
        {"requirement": "BIA documentation", "status": "required"},
        {"requirement": "BCP latest version", "status": "required"},
        {"requirement": "Exercise reports", "status": "required"},
        {"requirement": "Training records", "status": "required"},
        {"requirement": "Management review minutes", "status": "optional"},
    ]

# Health check
@app.get("/health")
async def health_check():
    try:
        await redis_client.ping()
        return {"status": "healthy", "service": "orchestrator"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Generate recommendations
@app.post("/api/recommendations", response_model=RecommendationResponse)
async def generate_recommendations(request: RecommendationRequest):
    try:
        # Simple rule-based recommendations (replace with LLM if API key available)
        context = request.context.lower()
        
        if "bia" in context:
            recommendation = "Based on the Business Impact Analysis, prioritize processes with RTO < 4 hours"
            confidence = 0.85
            reasoning = "Critical processes identified require immediate recovery capabilities"
        elif "incident" in context:
            recommendation = "Activate incident response team and assess impact on critical functions"
            confidence = 0.90
            reasoning = "Incident requires immediate coordinated response"
        elif "audit" in context:
            recommendation = "Prepare documentation and evidence for ISO 22301 compliance verification"
            confidence = 0.82
            reasoning = "Audit readiness ensures compliance demonstration"
        else:
            recommendation = "Review current BCM status and update plans as needed"
            confidence = 0.70
            reasoning = "Regular review maintains BCM effectiveness"
        
        return RecommendationResponse(
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=[
                {"option": "Conduct tabletop exercise", "priority": "medium"},
                {"option": "Update risk register", "priority": "low"}
            ]
        )
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Audit summarization
@app.post("/api/audit/summarize", response_model=AuditSummaryResponse)
async def summarize_audit(request: AuditSummaryRequest):
    try:
        # Process audit evidence
        findings = []
        capa_items = []
        
        for evidence in request.evidence:
            if evidence.get("status") == "non_conformity":
                findings.append({
                    "type": "non_conformity",
                    "description": evidence.get("description", ""),
                    "severity": "major"
                })
                capa_items.append({
                    "action": f"Address {evidence.get('description', 'issue')}",
                    "priority": "high",
                    "deadline": "30 days"
                })
            elif evidence.get("status") == "observation":
                findings.append({
                    "type": "observation",
                    "description": evidence.get("description", ""),
                    "severity": "minor"
                })
        
        summary = f"Audit completed with {len(findings)} findings ({len(capa_items)} requiring CAPA)"
        
        recommendations = [
            "Implement corrective actions within 30 days",
            "Schedule follow-up audit in 6 months",
            "Update BCM documentation based on findings"
        ]
        
        return AuditSummaryResponse(
            summary=summary,
            findings=findings,
            recommendations=recommendations,
            capa_items=capa_items
        )
    except Exception as e:
        logger.error(f"Error summarizing audit: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get pending AI decisions
@app.get("/api/ai/decisions/pending", response_model=List[AIDecision])
async def get_pending_decisions(tenant_id: str):
    try:
        # Filter decisions by tenant
        tenant_decisions = [
            decision for decision in pending_decisions.values()
            if decision.tenant_id == tenant_id and decision.status == "pending"
        ]
        
        # Sort by creation date
        tenant_decisions.sort(key=lambda x: x.created_at, reverse=True)
        
        return tenant_decisions
    except Exception as e:
        logger.error(f"Error fetching pending decisions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Approve decision
@app.post("/api/ai/decisions/{decision_id}/approve")
async def approve_decision(decision_id: str, background_tasks: BackgroundTasks):
    try:
        if decision_id not in pending_decisions:
            raise HTTPException(status_code=404, detail="Decision not found")
        
        decision = pending_decisions[decision_id]
        decision.status = "approved"
        
        # Execute decision in background
        background_tasks.add_task(execute_decision, decision)
        
        # Publish approval event
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{EVENTBUS_URL}/api/events/publish",
                json={
                    "event_type": "bcm.ai.decision.approved",
                    "tenant_id": decision.tenant_id,
                    "data": decision.dict()
                }
            )
        
        return {"status": "approved", "decision_id": decision_id}
    except Exception as e:
        logger.error(f"Error approving decision: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Reject decision
@app.post("/api/ai/decisions/{decision_id}/reject")
async def reject_decision(decision_id: str):
    try:
        if decision_id not in pending_decisions:
            raise HTTPException(status_code=404, detail="Decision not found")
        
        decision = pending_decisions[decision_id]
        decision.status = "rejected"
        
        # Publish rejection event
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{EVENTBUS_URL}/api/events/publish",
                json={
                    "event_type": "bcm.ai.decision.rejected",
                    "tenant_id": decision.tenant_id,
                    "data": decision.dict()
                }
            )
        
        return {"status": "rejected", "decision_id": decision_id}
    except Exception as e:
        logger.error(f"Error rejecting decision: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def execute_decision(decision: AIDecision):
    """Execute approved AI decision"""
    logger.info(f"Executing decision {decision.id} of type {decision.type}")
    
    if decision.type == "bcp_generation":
        await generate_bcp_draft(decision)
    elif decision.type == "incident_response":
        await create_incident_checklist(decision)
    elif decision.type == "audit_preparation":
        await prepare_audit_documentation(decision)

async def generate_bcp_draft(decision: AIDecision):
    """Generate BCP draft and send to Odoo"""
    # TODO: Implement actual BCP generation
    logger.info(f"Generating BCP draft for tenant {decision.tenant_id}")

async def create_incident_checklist(decision: AIDecision):
    """Create incident response checklist in Odoo"""
    logger.info(f"Creating incident checklist for tenant {decision.tenant_id}")

async def prepare_audit_documentation(decision: AIDecision):
    """Prepare audit documentation package"""
    logger.info(f"Preparing audit documentation for tenant {decision.tenant_id}")

# Auto-trigger functions
async def trigger_bcp_generation(event: Dict[str, Any]):
    """Automatically trigger BCP draft generation after BIA completion"""
    tenant_id = event["tenant_id"]
    bia_data = event.get("data", {})
    
    # Send callback to Odoo to create BCP draft
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{ODOO_URL}/bcm/plan/generate_from_bia",
                json={
                    "bia_id": bia_data.get("bia_id"),
                    "tenant_id": tenant_id,
                    "rto": bia_data.get("rto", 4),
                    "rpo": bia_data.get("rpo", 2),
                    "critical_processes": bia_data.get("critical_processes", [])
                },
                headers={"Content-Type": "application/json"}
            )
            logger.info(f"BCP generation triggered for BIA {bia_data.get('bia_id')}")
        except Exception as e:
            logger.error(f"Error triggering BCP generation: {e}")

async def trigger_incident_response(event: Dict[str, Any]):
    """Automatically generate incident response checklist"""
    tenant_id = event["tenant_id"]
    incident_data = event.get("data", {})
    
    # Generate AI response
    checklist = generate_incident_checklist(incident_data)
    
    # Send back to Odoo
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                f"{ODOO_URL}/bcm/incident/update_checklist",
                json={
                    "incident_id": incident_data.get("incident_id"),
                    "checklist": checklist,
                    "ai_generated": True
                },
                headers={"Content-Type": "application/json"}
            )
            
            # Also publish to EventBus
            await client.post(
                f"{EVENTBUS_URL}/api/events/publish",
                json={
                    "event_type": "bcm.incident.checklist_generated",
                    "tenant_id": tenant_id,
                    "data": {
                        "incident_id": incident_data.get("incident_id"),
                        "checklist_items": len(checklist)
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error updating incident checklist: {e}")

async def trigger_plan_draft_generation(event: Dict[str, Any]):
    """Generate plan draft using AI recommendations"""
    tenant_id = event["tenant_id"]
    plan_data = event.get("data", {})
    
    # Generate comprehensive plan structure
    plan_structure = {
        "sections": [
            {
                "title": "Executive Summary",
                "content": "This Business Continuity Plan ensures operational resilience..."
            },
            {
                "title": "Critical Processes",
                "content": f"Based on BIA, {len(plan_data.get('critical_processes', []))} critical processes identified"
            },
            {
                "title": "Recovery Strategies",
                "content": "Primary and alternate recovery strategies defined"
            },
            {
                "title": "Response Procedures",
                "content": "Step-by-step response procedures for various scenarios"
            },
            {
                "title": "Communication Plan",
                "content": "Internal and external communication protocols"
            }
        ],
        "recommendations": [
            "Review and update quarterly",
            "Conduct annual testing",
            "Train all key personnel"
        ]
    }
    
    # Send to EventBus
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{EVENTBUS_URL}/api/events/publish",
            json={
                "event_type": "bcm.plan.draft_generated",
                "tenant_id": tenant_id,
                "data": {
                    "plan_id": plan_data.get("plan_id"),
                    "structure": plan_structure,
                    "ai_generated": True
                }
            }
        )

async def trigger_kpi_recommendations(event: Dict[str, Any]):
    """Generate improvement recommendations based on KPI values"""
    tenant_id = event["tenant_id"]
    kpi_data = event.get("data", {})
    
    recommendations = []
    
    # Check KPI thresholds
    if kpi_data.get("bia_coverage", 100) < 80:
        recommendations.append({
            "type": "bia_improvement",
            "message": "BIA coverage below 80%. Schedule BIA assessments for uncovered processes.",
            "priority": "high"
        })
    
    if kpi_data.get("plans_up_to_date", 100) < 70:
        recommendations.append({
            "type": "plan_update",
            "message": "Plans outdated. Review and update plans older than 6 months.",
            "priority": "high"
        })
    
    if kpi_data.get("capa_on_time", 100) < 85:
        recommendations.append({
            "type": "capa_improvement",
            "message": "CAPA completion rate low. Review and expedite pending actions.",
            "priority": "medium"
        })
    
    if recommendations:
        # Publish recommendations event
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{EVENTBUS_URL}/api/events/publish",
                json={
                    "event_type": "bcm.kpi.recommendations",
                    "tenant_id": tenant_id,
                    "data": {
                        "period": kpi_data.get("period"),
                        "recommendations": recommendations,
                        "kpi_values": {
                            "bia_coverage": kpi_data.get("bia_coverage"),
                            "plans_up_to_date": kpi_data.get("plans_up_to_date"),
                            "capa_on_time": kpi_data.get("capa_on_time")
                        }
                    }
                }
            )

# Enhanced callback to Odoo
@app.post("/api/callback/odoo")
async def callback_to_odoo(data: Dict[str, Any]):
    """Send results back to Odoo"""
    try:
        action = data.get("action")
        
        if action == "update_plan":
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{ODOO_URL}/bcm/plan/update",
                    json=data.get("payload"),
                    headers={"Content-Type": "application/json"}
                )
                return {"status": "success", "odoo_response": response.status_code}
        
        elif action == "update_incident":
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{ODOO_URL}/bcm/incident/update",
                    json=data.get("payload"),
                    headers={"Content-Type": "application/json"}
                )
                return {"status": "success", "odoo_response": response.status_code}
        
        elif action == "create_capa":
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{ODOO_URL}/bcm/capa/create",
                    json=data.get("payload"),
                    headers={"Content-Type": "application/json"}
                )
                return {"status": "success", "odoo_response": response.status_code}
        
        return {"status": "error", "message": "Unknown action"}
    
    except Exception as e:
        logger.error(f"Error in Odoo callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
