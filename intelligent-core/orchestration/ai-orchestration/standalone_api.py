"""
Standalone AI Orchestrator API for Testing
===========================================

Simplified API server for testing the control panel.
Run with: python standalone_api.py
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import uvicorn
from datetime import datetime

app = FastAPI(
    title="AI Orchestrator API",
    description="Central AI decision-making system for BCM platform",
    version="1.0.0"
)

# Enable CORS for admin panel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "components": {
            "event_bus": True,
            "service_registry": True,
            "decision_center": True,
            "crisis_coordinator": True,
            "pdca_engine": True,
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/stats")
async def get_stats():
    """Get orchestrator statistics."""
    return {
        "total_decisions": 1247,
        "by_action": {
            "ActionType.AUTO_RESOLVE": 892,
            "ActionType.DELEGATE": 245,
            "ActionType.ESCALATE_HUMAN": 78,
            "ActionType.EMERGENCY_STOP": 12,
            "ActionType.REQUEST_INFO": 20,
        },
        "by_priority": {
            "CRITICAL": 34,
            "HIGH": 156,
            "NORMAL": 892,
            "LOW": 165,
        },
        "avg_latency_ms": 42.5,
        "auto_resolution_rate": 0.715,
        "escalation_rate": 0.062,
        "safety_approval_rate": 0.982,
        "service_registry": {
            "total_services": 9,
            "healthy_services": 8,
            "services": [
                {"name": "bia", "url": "http://localhost:8012", "status": "healthy", "last_check": datetime.utcnow().isoformat()},
                {"name": "risk", "url": "http://localhost:8013", "status": "healthy", "last_check": datetime.utcnow().isoformat()},
                {"name": "compliance", "url": "http://localhost:8014", "status": "healthy", "last_check": datetime.utcnow().isoformat()},
                {"name": "planning", "url": "http://localhost:8015", "status": "healthy", "last_check": datetime.utcnow().isoformat()},
                {"name": "coordination", "url": "http://localhost:8016", "status": "healthy", "last_check": datetime.utcnow().isoformat()},
                {"name": "documents", "url": "http://localhost:8024", "status": "healthy", "last_check": datetime.utcnow().isoformat()},
                {"name": "learning", "url": "http://localhost:8021", "status": "unhealthy", "last_check": datetime.utcnow().isoformat()},
                {"name": "response", "url": "http://localhost:8041", "status": "healthy", "last_check": datetime.utcnow().isoformat()},
                {"name": "validation", "url": "http://localhost:8022", "status": "healthy", "last_check": datetime.utcnow().isoformat()},
            ]
        },
        "delegation_stats": {
            "total_delegations": 245,
            "by_specialist": {
                "workflow-specialist": 45,
                "bia-specialist": 67,
                "risk-specialist": 43,
                "compliance-specialist": 21,
                "ai-expert-bcm-advisor": 34,
                "ai-expert-compliance-auditor": 24,
                "ai-expert-strategic-planner": 11,
            }
        },
        "crisis_stats": {
            "total_crises": 56,
            "active_crisis_ids": ["crisis_45", "crisis_52"],
            "by_level": {
                "MINOR": 34,
                "MAJOR": 18,
                "CRITICAL": 3,
                "CATASTROPHIC": 1,
            }
        },
        "pdca_stats": {
            "total_cycles": 189,
            "avg_quality_score": 87.3,
        }
    }


@app.post("/api/v1/decide")
async def decide(request: Dict[str, Any]):
    """Make a decision."""
    return {
        "decision_id": f"dec_{datetime.utcnow().timestamp()}",
        "action": "AUTO_RESOLVE",
        "rationale": "Similar situations resolved successfully in the past",
        "priority": "NORMAL",
        "confidence": 0.89,
        "safety_approved": True,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/crisis/detect")
async def detect_crisis(request: Dict[str, Any]):
    """Detect crisis."""
    return {
        "crisis": {
            "id": f"crisis_{datetime.utcnow().timestamp()}",
            "level": "MAJOR",
            "affected_services": ["bia", "risk"],
            "detected_at": datetime.utcnow().isoformat(),
            "status": "active"
        }
    }


@app.get("/api/v1/crisis/{crisis_id}/status")
async def get_crisis_status(crisis_id: str):
    """Get crisis status."""
    return {
        "id": crisis_id,
        "level": "MAJOR",
        "affected_services": ["bia", "risk"],
        "detected_at": datetime.utcnow().isoformat(),
        "status": "active",
        "bc_plan_activated": False
    }


@app.post("/api/v1/crisis/{crisis_id}/activate")
async def activate_crisis_response(crisis_id: str, request: Dict[str, Any]):
    """Activate crisis response."""
    return {
        "success": True,
        "crisis_id": crisis_id,
        "bc_plan_activated": True,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/crisis/{crisis_id}/resolve")
async def resolve_crisis(crisis_id: str):
    """Resolve crisis."""
    return {
        "success": True,
        "crisis_id": crisis_id,
        "resolved_at": datetime.utcnow().isoformat()
    }


@app.post("/admin/evolve")
async def trigger_evolution():
    """Trigger evolution cycle."""
    return {
        "success": True,
        "message": "Evolution cycle started",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/admin/cache/clear")
async def clear_cache():
    """Clear strategy cache."""
    return {
        "success": True,
        "message": "Strategy cache cleared",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint."""
    metrics = """# HELP orchestrator_decisions_total Total number of decisions made
# TYPE orchestrator_decisions_total counter
orchestrator_decisions_total 1247

# HELP orchestrator_auto_resolutions_total Total auto-resolutions
# TYPE orchestrator_auto_resolutions_total counter
orchestrator_auto_resolutions_total 892

# HELP orchestrator_decision_latency_seconds Decision latency
# TYPE orchestrator_decision_latency_seconds histogram
orchestrator_decision_latency_seconds_sum 53.14
orchestrator_decision_latency_seconds_count 1247
"""
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(content=metrics, media_type="text/plain")


if __name__ == "__main__":
    print("=" * 60)
    print("AI Orchestrator API - Standalone Test Server")
    print("=" * 60)
    print("Starting server on http://localhost:8050")
    print("Health check: http://localhost:8050/health")
    print("Stats: http://localhost:8050/stats")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8050, log_level="info")
