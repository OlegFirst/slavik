"""
🎨 AI Platform ISO - Unified Web UI
====================================

Central web interface for managing and monitoring the entire AI Platform.

Integrates:
- Tools Management (all 26 analysis tools)
- Grafana Dashboards (metrics visualization)
- Prometheus Metrics (real-time monitoring)
- Service Discovery (all services status)
- Workflow Intelligence (workflow analytics)
- Community Intelligence (collaboration metrics)

Port: 8888
Access: http://localhost:8888
"""

import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# ============================================================================
# CONFIGURATION
# ============================================================================

PLATFORM_ROOT = os.getenv("PLATFORM_ROOT", "/Users/MD/AI-Platform-ISO")

# Service URLs
SERVICES = {
    # AI Office Infrastructure
    "analytics_specialist": "http://localhost:8051",
    "mio_manager": "http://localhost:8046",
    "ai_orchestrator": "http://localhost:8004",

    # Intelligent Core
    "workflow_intelligence": "http://localhost:8030",
    "community_intelligence": "http://localhost:8031",
    "collective": "http://localhost:8032",
    "predictive": "http://localhost:8033",
    "ai_foundation": "http://localhost:8050",

    # Observability
    "prometheus": "http://localhost:9090",
    "grafana": "http://localhost:3000",
    "alertmanager": "http://localhost:9093",
}

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# APPLICATION LIFECYCLE
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    logger.info("=" * 70)
    logger.info("🎨 AI Platform Web UI Starting...")
    logger.info("=" * 70)
    logger.info(f"   Unified Dashboard: http://localhost:8888")
    logger.info(f"   Grafana Integration: {SERVICES['grafana']}")
    logger.info(f"   Prometheus Integration: {SERVICES['prometheus']}")
    logger.info("=" * 70)

    yield

    logger.info("🛑 AI Platform Web UI Shutting Down...")

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="AI Platform ISO - Web UI",
    description="Unified web interface for AI Platform management and monitoring",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory=f"{os.path.dirname(__file__)}/static"), name="static")

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def main_dashboard():
    """
    Main unified dashboard

    Shows:
    - Platform overview
    - All services status
    - Quick access to all subsystems
    - Real-time metrics
    """

    with open(f"{os.path.dirname(__file__)}/templates/dashboard.html", "r") as f:
        return f.read()

# ============================================================================
# TOOLS MANAGEMENT
# ============================================================================

@app.get("/tools", response_class=HTMLResponse)
async def tools_dashboard():
    """Tools management interface"""
    with open(f"{os.path.dirname(__file__)}/templates/tools.html", "r") as f:
        return f.read()

# ============================================================================
# MONITORING & OBSERVABILITY
# ============================================================================

@app.get("/monitoring", response_class=HTMLResponse)
async def monitoring_dashboard():
    """
    Monitoring dashboard with embedded Grafana
    """
    with open(f"{os.path.dirname(__file__)}/templates/monitoring.html", "r") as f:
        return f.read()

@app.get("/metrics")
async def prometheus_proxy():
    """Proxy to Prometheus metrics"""
    return RedirectResponse(url=f"{SERVICES['prometheus']}/metrics")

# ============================================================================
# SERVICES STATUS
# ============================================================================

@app.get("/api/services/status")
async def get_services_status() -> Dict[str, Any]:
    """
    Get status of all platform services

    Returns health check for each service
    """
    status = {}

    async with httpx.AsyncClient(timeout=5.0) as client:
        for service_name, base_url in SERVICES.items():
            try:
                # Try common health endpoints
                for path in ["/health", "/api/health", "/"]:
                    try:
                        response = await client.get(f"{base_url}{path}")
                        if response.status_code == 200:
                            status[service_name] = {
                                "status": "healthy",
                                "url": base_url,
                                "response_time_ms": response.elapsed.total_seconds() * 1000,
                                "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else None
                            }
                            break
                    except:
                        continue
                else:
                    # No health endpoint responded
                    status[service_name] = {
                        "status": "unreachable",
                        "url": base_url,
                        "error": "No health endpoint available"
                    }

            except Exception as e:
                status[service_name] = {
                    "status": "error",
                    "url": base_url,
                    "error": str(e)
                }

    return {
        "timestamp": datetime.now().isoformat(),
        "services": status,
        "total": len(SERVICES),
        "healthy": len([s for s in status.values() if s["status"] == "healthy"]),
        "unhealthy": len([s for s in status.values() if s["status"] != "healthy"])
    }

# ============================================================================
# ANALYTICS TOOLS API
# ============================================================================

@app.get("/api/tools/list")
async def get_tools_list() -> Dict[str, Any]:
    """Get list of all available analysis tools"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{SERVICES['analytics_specialist']}/api/v1/analytics/status")
            data = response.json()

            return {
                "tools": data.get("tools", {}),
                "competency_level": data.get("competency_level", "unknown"),
                "total": len(data.get("tools", {}))
            }
    except Exception as e:
        logger.error(f"Failed to get tools list: {e}")
        return {
            "tools": {},
            "error": str(e)
        }

@app.post("/api/tools/{tool_name}/execute")
async def execute_tool(tool_name: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute a specific tool"""
    try:
        endpoint_map = {
            "ast_analyzer": "/api/v1/analytics/tools/ast-analysis",
            "api_mapper": "/api/v1/analytics/tools/api-map",
            "dependency_validator": "/api/v1/analytics/tools/dependency-validation",
            "security_scanner": "/api/v1/analytics/tools/security-scan",
            "module_scanner": "/api/v1/analytics/tools/module-scan",
        }

        endpoint = endpoint_map.get(tool_name, f"/api/v1/analytics/tools/{tool_name}")

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{SERVICES['analytics_specialist']}{endpoint}",
                json=parameters or {}
            )
            return response.json()

    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PROMETHEUS INTEGRATION
# ============================================================================

@app.get("/api/prometheus/query")
async def prometheus_query(query: str) -> Dict[str, Any]:
    """Query Prometheus for metrics"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{SERVICES['prometheus']}/api/v1/query",
                params={"query": query}
            )
            return response.json()
    except Exception as e:
        logger.error(f"Prometheus query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prometheus/targets")
async def prometheus_targets() -> Dict[str, Any]:
    """Get Prometheus scrape targets"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{SERVICES['prometheus']}/api/v1/targets")
            return response.json()
    except Exception as e:
        logger.error(f"Failed to get Prometheus targets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# GRAFANA INTEGRATION
# ============================================================================

@app.get("/api/grafana/dashboards")
async def get_grafana_dashboards() -> Dict[str, Any]:
    """Get list of Grafana dashboards"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Grafana API requires authentication
            # For now, return predefined dashboards
            return {
                "dashboards": [
                    {
                        "uid": "workflow-intelligence",
                        "title": "Workflow Intelligence",
                        "url": f"{SERVICES['grafana']}/d/workflow-intelligence"
                    },
                    {
                        "uid": "platform-wide",
                        "title": "Platform Overview",
                        "url": f"{SERVICES['grafana']}/d/platform-wide"
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Failed to get Grafana dashboards: {e}")
        return {"dashboards": [], "error": str(e)}

# ============================================================================
# WORKFLOW INTELLIGENCE
# ============================================================================

@app.get("/api/workflows/stats")
async def get_workflow_stats() -> Dict[str, Any]:
    """Get workflow statistics from Workflow Intelligence service"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{SERVICES['workflow_intelligence']}/api/v1/stats")
            return response.json()
    except Exception as e:
        logger.error(f"Failed to get workflow stats: {e}")
        return {"error": str(e)}

# ============================================================================
# COMMUNITY INTELLIGENCE
# ============================================================================

@app.get("/api/community/stats")
async def get_community_stats() -> Dict[str, Any]:
    """Get community statistics"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{SERVICES['community_intelligence']}/api/v1/stats")
            return response.json()
    except Exception as e:
        logger.error(f"Failed to get community stats: {e}")
        return {"error": str(e)}

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8888,
        reload=True,
        log_level="info"
    )
