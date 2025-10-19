"""
Main FastAPI Application - Unified Orchestration System

Entry point for BCM Orchestration Platform.
Exposes REST API for all orchestrators.
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from control_center.unified_controller_integrated import UnifiedController
from models import (
    ScenarioGenerationRequest,
    EventPublishRequest,
    WorkflowStartRequest,
    BIAStartRequest,
    IncidentReportRequest,
    AuditStartRequest
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global controller instance
controller: UnifiedController = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager

    Handles startup and shutdown of orchestration system
    """
    global controller

    # Startup
    logger.info("Starting Unified Orchestration System...")
    controller = UnifiedController()

    startup_result = await controller.start_all()
    if startup_result['status'] != 'started':
        logger.error(f"Failed to start system: {startup_result}")
        raise Exception("System startup failed")

    logger.info("System ready")

    yield

    # Shutdown
    logger.info("Shutting down Unified Orchestration System...")
    await controller.stop_all()
    logger.info("System shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="BCM Unified Orchestration API",
    description="Unified orchestration platform for Business Continuity Management",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# SYSTEM ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "orchestrator"}


@app.get("/api/v1/system/status")
async def get_system_status():
    """Get overall system status"""
    return await controller.get_system_status()


@app.post("/api/v1/system/restart")
async def restart_system():
    """Restart entire system"""
    result = await controller.restart_all()
    if result['status'] == 'restart_failed':
        raise HTTPException(status_code=500, detail=result)
    return result


@app.post("/api/v1/system/orchestrator/{orchestrator}/restart")
async def restart_orchestrator(orchestrator: str):
    """Restart specific orchestrator"""
    result = await controller.restart_orchestrator(orchestrator)
    if result['status'] == 'error':
        raise HTTPException(status_code=400, detail=result)
    return result


# ============================================================================
# PLATFORM ORCHESTRATOR ENDPOINTS
# ============================================================================

@app.get("/api/v1/platform/status")
async def get_platform_status():
    """Get Platform Orchestrator status"""
    return await controller.get_platform_status()


@app.post("/api/v1/platform/services/{service}/start")
async def start_service(service: str):
    """Start specific service"""
    platform = controller.platform
    success = await platform.docker_manager.start_service(service)

    if success:
        return {"status": "started", "service": service}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to start {service}")


@app.post("/api/v1/platform/services/{service}/stop")
async def stop_service(service: str):
    """Stop specific service"""
    platform = controller.platform
    success = await platform.docker_manager.stop_service(service)

    if success:
        return {"status": "stopped", "service": service}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to stop {service}")


@app.post("/api/v1/platform/services/{service}/restart")
async def restart_service(service: str):
    """Restart specific service"""
    platform = controller.platform
    success = await platform.docker_manager.restart_service(service)

    if success:
        return {"status": "restarted", "service": service}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to restart {service}")


@app.get("/api/v1/platform/services/{service}/status")
async def get_service_status(service: str):
    """Get service status"""
    platform = controller.platform
    service_info = await platform.service_registry.get_service(service)

    if not service_info:
        raise HTTPException(status_code=404, detail=f"Service {service} not found")

    return service_info


@app.get("/api/v1/platform/services")
async def list_services():
    """List all registered services"""
    platform = controller.platform
    services = await platform.service_registry.list_services()
    return {"services": services}


# ============================================================================
# AI ORCHESTRATOR ENDPOINTS
# ============================================================================

@app.get("/api/v1/ai/status")
async def get_ai_status():
    """Get AI Orchestrator status"""
    return await controller.get_ai_status()


@app.get("/api/v1/ai/rules")
async def list_ai_rules():
    """List all orchestration rules"""
    ai = controller.ai
    return {
        "rules": [
            {
                "name": rule.name,
                "event_type": rule.event_type,
                "enabled": rule.enabled,
                "priority": rule.priority
            }
            for rule in ai.rules
        ]
    }


@app.post("/api/v1/ai/rules/{rule_name}/enable")
async def enable_rule(rule_name: str):
    """Enable orchestration rule"""
    ai = controller.ai
    rule = next((r for r in ai.rules if r.name == rule_name), None)

    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule {rule_name} not found")

    rule.enabled = True
    return {"status": "enabled", "rule": rule_name}


@app.post("/api/v1/ai/rules/{rule_name}/disable")
async def disable_rule(rule_name: str):
    """Disable orchestration rule"""
    ai = controller.ai
    rule = next((r for r in ai.rules if r.name == rule_name), None)

    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule {rule_name} not found")

    rule.enabled = False
    return {"status": "disabled", "rule": rule_name}


@app.get("/api/v1/ai/decisions")
async def list_decisions():
    """List all AI decisions"""
    ai = controller.ai
    return {
        "total": len(ai.decisions),
        "pending": len(ai.pending_decisions),
        "decisions": [
            {
                "id": d.id,
                "type": d.type,
                "title": d.title,
                "status": d.status,
                "confidence": d.confidence,
                "created_at": d.created_at.isoformat()
            }
            for d in ai.decisions[-50:]  # Last 50
        ]
    }


@app.post("/api/v1/ai/decisions/{decision_id}/approve")
async def approve_decision(decision_id: str, approved_by: str = "api_user"):
    """Approve pending AI decision"""
    ai = controller.ai

    if decision_id not in ai.pending_decisions:
        raise HTTPException(status_code=404, detail="Decision not found or already processed")

    await ai.approve_decision(decision_id, approved_by)
    return {"status": "approved", "decision_id": decision_id}


@app.post("/api/v1/ai/decisions/{decision_id}/reject")
async def reject_decision(decision_id: str, rejected_by: str = "api_user"):
    """Reject pending AI decision"""
    ai = controller.ai

    if decision_id not in ai.pending_decisions:
        raise HTTPException(status_code=404, detail="Decision not found or already processed")

    await ai.reject_decision(decision_id, rejected_by)
    return {"status": "rejected", "decision_id": decision_id}


# ============================================================================
# SCENARIO ORCHESTRATOR ENDPOINTS
# ============================================================================

@app.get("/api/v1/scenario/status")
async def get_scenario_status():
    """Get Scenario Orchestrator status"""
    return await controller.get_scenario_status()


@app.post("/api/v1/scenario/generate")
async def generate_scenario(request: ScenarioGenerationRequest):
    """Generate AI-powered BCM scenario"""
    scenario_orch = controller.scenario
    scenario = await scenario_orch.generate_scenario(request)

    return {
        "status": "generated",
        "scenario": {
            "id": scenario.id,
            "title": scenario.title,
            "category": scenario.category,
            "level": scenario.level,
            "duration_hours": scenario.meta_duration,
            "participants": scenario.meta_participants,
            "is_ai_generated": scenario.is_ai_generated,
            "has_jaamsim_config": scenario.jaamsim_config is not None,
            "created_at": scenario.created_at.isoformat()
        }
    }


@app.get("/api/v1/scenario/{scenario_id}")
async def get_scenario(scenario_id: str):
    """Get scenario by ID"""
    scenario_orch = controller.scenario

    if scenario_id not in scenario_orch.scenario_storage:
        raise HTTPException(status_code=404, detail="Scenario not found")

    scenario = scenario_orch.scenario_storage[scenario_id]
    return scenario.dict()


@app.get("/api/v1/scenario/{scenario_id}/learning")
async def get_scenario_learning(scenario_id: str):
    """Get learning insights for scenario"""
    scenario_orch = controller.scenario
    learning = await scenario_orch.learning.get_scenario_learning(scenario_id)

    if not learning:
        raise HTTPException(status_code=404, detail="No learning data for this scenario")

    return learning


@app.get("/api/v1/scenario/learning/stats")
async def get_learning_stats():
    """Get overall learning statistics"""
    scenario_orch = controller.scenario
    stats = await scenario_orch.learning.get_stats()
    return stats


# ============================================================================
# LEGACY ENDPOINTS (for backward compatibility)
# ============================================================================

@app.post("/api/v1/events/publish")
async def publish_event(request: EventPublishRequest):
    """Publish event to EventBus"""
    platform = controller.platform

    await platform.publish_event(
        event_type=request.event_type,
        data=request.data,
        tenant_id=request.tenant_id
    )

    return {"status": "published", "event_type": request.event_type}


@app.post("/api/v1/workflows/start")
async def start_workflow(request: WorkflowStartRequest):
    """Start workflow (legacy endpoint)"""
    # Forward to AI orchestrator for processing
    await controller.platform.publish_event(
        event_type='workflow.start_requested',
        data=request.dict()
    )

    return {"status": "workflow_started", "workflow_id": request.workflow_id}


@app.post("/api/v1/bcm/bia/start")
async def start_bia(request: BIAStartRequest):
    """Start BIA process"""
    await controller.platform.publish_event(
        event_type='bcm.bia.start_requested',
        data=request.dict(),
        tenant_id=request.tenant_id
    )

    return {"status": "bia_started"}


@app.post("/api/v1/bcm/incident/report")
async def report_incident(request: IncidentReportRequest):
    """Report incident"""
    await controller.platform.publish_event(
        event_type='bcm.incident.opened',
        data=request.dict(),
        tenant_id=request.tenant_id
    )

    return {"status": "incident_reported"}


@app.post("/api/v1/bcm/audit/start")
async def start_audit(request: AuditStartRequest):
    """Start audit"""
    await controller.platform.publish_event(
        event_type='bcm.audit.start_requested',
        data=request.dict(),
        tenant_id=request.tenant_id
    )

    return {"status": "audit_started"}


# ============================================================================
# AI ORCHESTRATOR ADVANCED ENDPOINTS
# ============================================================================

@app.post("/api/v1/ai/analyze/process-risk")
async def analyze_process_risk(process: Dict[str, Any]):
    """Analyze business process risk"""
    ai = controller.ai
    analysis = await ai.intelligence.analyze_business_process_risk(process)

    return {
        "status": "success",
        "analysis": analysis,
        "generated_at": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/ai/analyze/incident")
async def classify_incident_ai(incident: Dict[str, Any]):
    """AI classification of incident"""
    ai = controller.ai
    classification = await ai.intelligence.classify_incident(incident)

    return {
        "status": "success",
        "classification": classification,
        "generated_at": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/ai/nlp/query")
async def process_nlp_query(query: Dict[str, Any]):
    """Process natural language query"""
    # Simple NLP response
    return {
        "query": query.get("query", ""),
        "intent": "general",
        "response": "AI Orchestrator is ready to help with BCM tasks"
    }


# ============================================================================
# CLAUDE AI ENDPOINTS
# ============================================================================

@app.post("/api/v1/claude/analyze-changes")
async def claude_analyze_changes(request: Dict[str, Any]):
    """Claude analyzes code changes"""
    from ai import ClaudeProEngine

    claude = ClaudeProEngine()
    changes = request.get("changes", "")
    context = request.get("context", {})

    analysis = await claude.analyze_code_changes(changes, context)

    return {
        "status": "success",
        "analysis": analysis
    }


@app.post("/api/v1/claude/generate-config")
async def claude_generate_config(requirements: Dict[str, Any]):
    """Claude generates deployment config"""
    from ai import ClaudeProEngine

    claude = ClaudeProEngine()
    config = await claude.generate_deployment_config(requirements)

    return {
        "status": "success",
        "config": config
    }


@app.post("/api/v1/claude/create-pr")
async def claude_create_pr(pr_data: Dict[str, Any]):
    """Claude creates intelligent PR"""
    from ai import ClaudeProEngine

    claude = ClaudeProEngine()
    improvements = pr_data.get("improvements", [])
    pr_info = await claude.create_intelligent_pr(improvements, pr_data)

    return {
        "status": "success",
        "pr_info": pr_info
    }


# ============================================================================
# AI AGENT ENDPOINTS
# ============================================================================

@app.post("/api/v1/ai/agent/process")
async def process_with_ai_agent(request: Dict[str, Any]):
    """Route request to appropriate AI agent"""
    from ai import ai_router, AgentCapability

    capability_str = request.get("capability", "")
    data = request.get("data", {})
    context = request.get("context")

    # Map capability string to enum
    capability_map = {
        "pdca": AgentCapability.PDCA,
        "bia": AgentCapability.BIA_ANALYSIS,
        "document": AgentCapability.DOCUMENT_PROCESSING,
        "compliance": AgentCapability.COMPLIANCE_CHECK,
        "workflow": AgentCapability.WORKFLOW_ORCHESTRATION,
        "github": AgentCapability.GITHUB_INTEGRATION,
        "decision": AgentCapability.DECISION_SUPPORT,
        "context": AgentCapability.CONTEXT_AWARENESS
    }

    capability = capability_map.get(capability_str.lower())
    if not capability:
        raise HTTPException(status_code=400, detail=f"Unknown capability: {capability_str}")

    result = await ai_router.route_request(capability, data, context)

    return {
        "status": "success",
        "capability": capability_str,
        "result": result
    }


@app.get("/api/v1/ai/agents/health")
async def check_ai_agents_health():
    """Check health of all AI agents"""
    from ai import ai_router

    health_status = await ai_router.health_check_all_agents()

    return {
        "status": "completed",
        "agents": health_status,
        "healthy_count": sum(1 for agent in health_status.values() if agent["healthy"]),
        "total_count": len(health_status)
    }


@app.get("/api/v1/ai/agents/analytics")
async def get_ai_agent_analytics():
    """Get AI agent analytics"""
    from ai import ai_router

    analytics = ai_router.get_agent_analytics()

    return {
        "status": "success",
        "analytics": analytics
    }


# ============================================================================
# GITHUB INTEGRATION ENDPOINTS
# ============================================================================

@app.post("/api/v1/auth/token-exchange")
async def exchange_github_token(request: Dict[str, Any]):
    """Exchange GitHub JWT for internal token"""
    from integrations import GitHubTokenManager

    token_manager = GitHubTokenManager()
    github_jwt = request.get("token", "")

    if not github_jwt:
        raise HTTPException(status_code=400, detail="No GitHub token provided")

    result = await token_manager.exchange_github_token(github_jwt)

    return result


@app.post("/api/v1/auth/refresh-token")
async def refresh_user_token(request: Dict[str, Any]):
    """Refresh expired token"""
    from integrations import GitHubTokenManager

    token_manager = GitHubTokenManager()
    refresh_token = request.get("refresh_token", "")

    if not refresh_token:
        raise HTTPException(status_code=400, detail="No refresh token provided")

    result = await token_manager.refresh_token(refresh_token)

    return result


# ============================================================================
# DEPLOYMENT ORCHESTRATION ENDPOINTS
# ============================================================================

@app.post("/api/v1/deployment/orchestrate")
async def orchestrate_deployment(plan: Dict[str, Any]):
    """AI-orchestrated deployment"""
    ai = controller.ai

    # Convert dict to DeploymentPlan
    from models import DeploymentPlan

    deployment_plan = DeploymentPlan(**plan)
    result = await ai.devops.orchestrate_deployment(deployment_plan)

    return {
        "status": "success",
        "result": result.dict()
    }


@app.get("/api/v1/deployment/history")
async def get_deployment_history():
    """Get deployment history"""
    ai = controller.ai

    return {
        "deployments": ai.devops.deployment_history[-10:],
        "learned_patterns": ai.devops.learned_patterns,
        "total_deployments": len(ai.devops.deployment_history)
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,  # Changed from 8000 to avoid conflict with Gateway
        reload=True,
        log_level="info"
    )