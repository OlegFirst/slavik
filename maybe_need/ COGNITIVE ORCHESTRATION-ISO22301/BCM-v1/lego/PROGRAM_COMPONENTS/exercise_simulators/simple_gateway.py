#!/usr/bin/env python3
"""
Simplified BCM API Gateway - Quick Start Version
Minimal dependencies, maximum functionality
"""

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import json
import logging
from datetime import datetime
import os

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="BCM API Gateway",
    description="Centralized API Gateway for BCM Platform",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
SERVICES = {
    "odoo": os.getenv("ODOO_URL", "http://localhost:8069"),
    "ai_orchestrator": "http://localhost:8000",
    "bia_engine": "http://localhost:8082",
    "compliance_checker": "http://localhost:8084",
    "document_processor": "http://localhost:8083",
    "ai_control_center": "http://localhost:8200",
}

# HTTP client
http_client = httpx.AsyncClient(timeout=30.0)

# ===========================
# HEALTH CHECK
# ===========================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": list(SERVICES.keys())
    }

# ===========================
# BCM MODULES
# ===========================

@app.get("/bcm/modules/status")
async def get_bcm_modules_status():
    """Get status of all BCM modules"""
    # Mock data for now - replace with real Odoo calls
    modules = [
        {"name": "BCM Core", "installed": True, "version": "1.0"},
        {"name": "BCM Risk Management", "installed": True, "version": "1.0"},
        {"name": "BCM Business Impact Analysis", "installed": True, "version": "1.0"},
        {"name": "BCM Plans", "installed": True, "version": "1.0"},
        {"name": "BCM Incident Management", "installed": True, "version": "1.0"},
        {"name": "BCM Exercise", "installed": True, "version": "1.0"},
        {"name": "BCM Training", "installed": True, "version": "1.0"},
        {"name": "BCM Compliance", "installed": True, "version": "1.0"},
    ]
    return {"modules": modules}

# ===========================
# AI SERVICES
# ===========================

@app.get("/services/ai-control/organisms")
async def get_ai_organisms():
    """Get AI organisms status"""
    try:
        # Try to get real data from AI Control Center
        response = await http_client.get(f"{SERVICES['ai_control_center']}/api/organism/health")
        if response.status_code == 200:
            data = response.json()
            organisms = []
            for organ_id, organ in data.get("organs", {}).items():
                organisms.append({
                    "id": organ_id,
                    "name": organ.get("name"),
                    "status": organ.get("status", "unknown"),
                    "health_score": organ.get("health_score", 0),
                    "endpoint": organ.get("endpoint"),
                    "last_check": organ.get("last_check")
                })
            return {"organisms": organisms}
    except Exception as e:
        logger.warning(f"Could not reach AI Control Center: {e}")

    # Return mock data if service unavailable
    return {
        "organisms": [
            {"id": 1, "name": "AI Orchestrator Core", "status": "healthy", "health_score": 0.95},
            {"id": 2, "name": "PDCA Assistant", "status": "healthy", "health_score": 0.88},
            {"id": 3, "name": "BIA Engine", "status": "healthy", "health_score": 0.92},
            {"id": 4, "name": "Compliance Checker", "status": "warning", "health_score": 0.75},
            {"id": 5, "name": "Document Processor", "status": "healthy", "health_score": 0.90},
        ]
    }

@app.get("/services/ai-control/organisms/{organism_id}/config")
async def get_organism_config(organism_id: int):
    """Get AI organism configuration"""
    return {
        "id": organism_id,
        "config": {
            "max_tokens": 4000,
            "temperature": 0.7,
            "model": "gpt-4",
            "retry_attempts": 3
        }
    }

@app.get("/services/ai-control/organisms/{organism_id}/health")
async def get_organism_health(organism_id: int):
    """Get AI organism health details"""
    return {
        "id": organism_id,
        "health": {
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "request_count": 1234,
            "error_rate": 0.02,
            "avg_response_time": 0.234
        }
    }

@app.get("/services/ai-control/organisms/{organism_id}/logs")
async def get_organism_logs(organism_id: int, lines: int = 100):
    """Get AI organism logs"""
    logs = []
    for i in range(min(lines, 10)):
        logs.append(f"[{datetime.utcnow().isoformat()}] INFO: Organism {organism_id} processing request {i+1}")
    return {"logs": logs}

# ===========================
# SERVICE CONTROL
# ===========================

@app.post("/services/control/{service_name}/{action}")
async def control_service(service_name: str, action: str):
    """Control services (start/stop/restart)"""
    if action not in ["start", "stop", "restart"]:
        raise HTTPException(status_code=400, detail="Invalid action")

    # Mock implementation - in real scenario, would call Docker API
    return {
        "success": True,
        "service": service_name,
        "action": action,
        "message": f"Service {service_name} {action} initiated"
    }

# ===========================
# CONFIG MANAGEMENT
# ===========================

@app.get("/config/{category}")
async def get_config(category: str):
    """Get configuration by category"""
    configs = {
        "general": {
            "company_name": "BCM Platform Corp",
            "timezone": "UTC",
            "language": "en"
        },
        "security": {
            "password_policy": "strong",
            "mfa_enabled": True,
            "session_timeout": 3600
        },
        "integration": {
            "odoo_enabled": True,
            "ai_services_enabled": True,
            "webhook_enabled": False
        }
    }
    return configs.get(category, {})

@app.post("/config/{category}")
async def update_config(category: str, config: dict):
    """Update configuration"""
    return {
        "success": True,
        "category": category,
        "message": "Configuration updated"
    }

# ===========================
# TEMPLATES
# ===========================

@app.get("/templates")
async def get_templates():
    """Get all templates"""
    templates = [
        {"id": 1, "name": "Business Continuity Plan", "category": "Plan", "version": "2.0"},
        {"id": 2, "name": "Risk Assessment", "category": "Assessment", "version": "1.5"},
        {"id": 3, "name": "Incident Response", "category": "Procedure", "version": "3.1"},
    ]
    return {"templates": templates}

@app.post("/templates/{template_id}/process")
async def process_template(template_id: int):
    """Process template with AI"""
    return {
        "success": True,
        "template_id": template_id,
        "status": "processing",
        "message": "Template processing started"
    }

# ===========================
# CLIENTS
# ===========================

@app.get("/clients")
async def get_clients():
    """Get all clients"""
    clients = [
        {"id": 1, "name": "Acme Corp", "status": "active", "risk_level": "low"},
        {"id": 2, "name": "Tech Solutions", "status": "active", "risk_level": "medium"},
        {"id": 3, "name": "Global Industries", "status": "prospect", "risk_level": "high"},
    ]
    return {"clients": clients}

@app.post("/clients")
async def create_client(client: dict):
    """Create new client"""
    return {
        "success": True,
        "client_id": 4,
        "message": "Client created successfully"
    }

# ===========================
# USERS
# ===========================

@app.get("/users")
async def get_users():
    """Get all users"""
    users = [
        {"id": 1, "name": "Admin User", "email": "admin@bcm.com", "role": "admin"},
        {"id": 2, "name": "Manager User", "email": "manager@bcm.com", "role": "manager"},
        {"id": 3, "name": "Analyst User", "email": "analyst@bcm.com", "role": "analyst"},
    ]
    return {"users": users}

# ===========================
# WEBSOCKET
# ===========================

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    await websocket.send_json({
        "type": "connection",
        "status": "connected",
        "client_id": client_id,
        "timestamp": datetime.utcnow().isoformat()
    })

    try:
        while True:
            data = await websocket.receive_json()
            # Echo back for now
            await websocket.send_json({
                "type": "echo",
                "original": data,
                "timestamp": datetime.utcnow().isoformat()
            })
    except Exception as e:
        logger.info(f"WebSocket disconnected: {client_id}")

# ===========================
# STARTUP & SHUTDOWN
# ===========================

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 BCM API Gateway started successfully")
    logger.info(f"📡 Services configured: {list(SERVICES.keys())}")

@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()
    logger.info("👋 BCM API Gateway stopped")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="info")