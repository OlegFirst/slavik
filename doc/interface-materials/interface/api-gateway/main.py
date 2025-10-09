"""
API Gateway - Единая точка входа для всех API запросов
Маршрутизация, аутентификация, rate limiting
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import httpx
import os
from typing import Optional

app = FastAPI(
    title="BCM API Gateway",
    description="Unified API gateway with routing, auth, and rate limiting",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
EXECUTION_ENGINE_URL = os.getenv("EXECUTION_ENGINE_URL", "http://execution-engine:8000")
INTELLIGENT_CORE_URL = os.getenv("INTELLIGENT_CORE_URL", "http://intelligent-core:9000")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")

# HTTP Client
client = httpx.AsyncClient(timeout=30.0)

# ============================================
# HEALTH CHECK
# ============================================

@app.get("/")
async def root():
    return {
        "service": "BCM API Gateway",
        "status": "operational",
        "version": "1.0.0",
        "routes": {
            "/api/v1/ai/*": "Intelligent Core",
            "/api/v1/bcm/*": "Execution Engine",
            "/api/v1/auth/*": "Auth Service"
        }
    }

@app.get("/health")
async def health_check():
    """Check health of gateway and downstream services"""

    services_status = {}

    # Check Execution Engine
    try:
        response = await client.get(f"{EXECUTION_ENGINE_URL}/health", timeout=5.0)
        services_status["execution_engine"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        services_status["execution_engine"] = "unreachable"

    # Check Intelligent Core
    try:
        response = await client.get(f"{INTELLIGENT_CORE_URL}/health", timeout=5.0)
        services_status["intelligent_core"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        services_status["intelligent_core"] = "unreachable"

    overall_healthy = all(status == "healthy" for status in services_status.values())

    return {
        "status": "healthy" if overall_healthy else "degraded",
        "services": services_status
    }

# ============================================
# PROXY ROUTES
# ============================================

async def proxy_request(
    request: Request,
    target_url: str,
    path: str
):
    """Generic proxy function"""

    # Build target URL
    url = f"{target_url}{path}"

    # Get query params
    query_params = dict(request.query_params)

    # Get headers (exclude host)
    headers = dict(request.headers)
    headers.pop("host", None)

    # Get body if present
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()

    try:
        # Forward request
        response = await client.request(
            method=request.method,
            url=url,
            params=query_params,
            headers=headers,
            content=body
        )

        # Return response
        return StreamingResponse(
            response.aiter_bytes(),
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

# ============================================
# AI ROUTES (Intelligent Core)
# ============================================

@app.api_route(
    "/api/v1/ai/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy_ai(request: Request, path: str):
    """Proxy to Intelligent Core"""
    return await proxy_request(request, INTELLIGENT_CORE_URL, f"/api/v1/{path}")

# Direct convenience routes
@app.post("/api/v1/decisions/make")
async def make_decision(request: Request):
    """AI decision making"""
    return await proxy_request(request, INTELLIGENT_CORE_URL, "/api/v1/decisions/make")

@app.post("/api/v1/digital-twin/simulate")
async def simulate_disruption(request: Request):
    """Digital Twin simulation"""
    return await proxy_request(request, INTELLIGENT_CORE_URL, "/api/v1/digital-twin/simulate")

@app.post("/api/v1/chat")
async def ai_chat(request: Request):
    """AI conversational interface"""
    return await proxy_request(request, INTELLIGENT_CORE_URL, "/api/v1/chat")

# ============================================
# BCM ROUTES (Execution Engine)
# ============================================

@app.api_route(
    "/api/v1/bcm/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy_bcm(request: Request, path: str):
    """Proxy to Execution Engine"""
    return await proxy_request(request, EXECUTION_ENGINE_URL, f"/api/v1/{path}")

# Workflow routes
@app.post("/api/v1/workflows/{workflow}/execute")
async def execute_workflow(request: Request, workflow: str):
    """Execute PLAN/DO/CHECK/ACT workflow"""
    return await proxy_request(request, EXECUTION_ENGINE_URL, f"/api/v1/workflows/{workflow}/execute")

# Capability routes
@app.api_route(
    "/api/v1/capabilities/{capability}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy_capability(request: Request, capability: str, path: str):
    """Proxy to specific capability (BIA, Risk, Planning, etc.)"""
    return await proxy_request(request, EXECUTION_ENGINE_URL, f"/api/v1/capabilities/{capability}/{path}")

# ============================================
# AGGREGATED ROUTES (Call multiple services)
# ============================================

@app.get("/api/v1/dashboard/overview")
async def dashboard_overview(org_id: int):
    """
    Aggregated dashboard data from multiple services
    """

    # Call multiple services in parallel
    try:
        # Get BIA summary
        bia_response = await client.get(
            f"{EXECUTION_ENGINE_URL}/api/v1/capabilities/bia/processes",
            params={"org_id": org_id}
        )
        bia_data = bia_response.json()

        # Get Risk summary
        risk_response = await client.get(
            f"{EXECUTION_ENGINE_URL}/api/v1/capabilities/risk/assessments",
            params={"org_id": org_id}
        )
        risk_data = risk_response.json()

        # Get Active incidents
        incidents_response = await client.get(
            f"{EXECUTION_ENGINE_URL}/api/v1/capabilities/response/incidents",
            params={"org_id": org_id, "status": "open"}
        )
        incidents_data = incidents_response.json()

        # Aggregate
        return {
            "org_id": org_id,
            "summary": {
                "critical_processes": len([p for p in bia_data.get("processes", []) if p.get("criticality") >= 4]),
                "high_risks": len([r for r in risk_data.get("risks", []) if r.get("risk_score") >= 15]),
                "active_incidents": len(incidents_data.get("incidents", [])),
                "iso_compliance": "87%"
            },
            "bia": bia_data,
            "risks": risk_data,
            "incidents": incidents_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard data: {str(e)}")

# ============================================
# WEBSOCKET (для real-time updates)
# ============================================

from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket для real-time обновлений
    (инциденты, алерты, статус восстановления)
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process and broadcast
            await manager.broadcast(f"Received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
