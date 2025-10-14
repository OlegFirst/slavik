"""
Monitoring Backend API
======================

FastAPI backend for admin-control-center monitoring dashboard.

Provides:
- Real-time metrics from Prometheus
- Service health checks
- PDCA analytics
- Alert management
- WebSocket for live updates

Port: 8050
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any
import httpx

# Prometheus metrics
from prometheus_client import Counter, Gauge, Histogram, generate_latest, REGISTRY

# Routes
from routes import dashboard, metrics, pdca, alerts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BCM Monitoring API",
    description="Real-time monitoring and analytics for BCM Platform",
    version="1.0.0"
)

# CORS - allow admin-control-center to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        "http://localhost:3006",
        "http://localhost:3007",
        "http://localhost:3008",  # admin-control-center
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["Metrics"])
app.include_router(pdca.router, prefix="/api/v1/pdca", tags=["PDCA"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")

manager = ConnectionManager()

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "BCM Monitoring API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "dashboard": "/api/v1/dashboard",
            "metrics": "/api/v1/metrics",
            "pdca": "/api/v1/pdca",
            "alerts": "/api/v1/alerts",
            "websocket": "/ws"
        }
    }

# Prometheus metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)
active_connections = Gauge(
    'active_websocket_connections',
    'Number of active WebSocket connections'
)
request_duration_seconds = Histogram(
    'request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check Prometheus connection
    prometheus_ok = False
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:9090/-/healthy", timeout=2.0)
            prometheus_ok = resp.status_code == 200
    except:
        pass

    return {
        "status": "healthy" if prometheus_ok else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {
            "prometheus": "ok" if prometheus_ok else "error"
        }
    }

@app.get("/metrics")
async def metrics_endpoint():
    """Prometheus metrics endpoint"""
    # Update active connections gauge
    active_connections.set(len(manager.active_connections))

    # Generate and return metrics
    return Response(
        content=generate_latest(REGISTRY),
        media_type="text/plain"
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Send updates every 5 seconds
            await asyncio.sleep(5)

            # Fetch latest metrics
            try:
                async with httpx.AsyncClient() as client:
                    # Get service health
                    services_resp = await client.get(
                        "http://localhost:9090/api/v1/targets",
                        timeout=2.0
                    )
                    services_data = services_resp.json()

                    # Send to client
                    await websocket.send_json({
                        "type": "metrics_update",
                        "timestamp": datetime.utcnow().isoformat(),
                        "data": {
                            "services": len(services_data.get("data", {}).get("activeTargets", [])),
                            "health": "ok"
                        }
                    })
            except Exception as e:
                logger.error(f"Error fetching metrics: {e}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8050, log_level="info")
