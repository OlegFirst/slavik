#!/usr/bin/env python3
"""
Centralized Backend API Gateway for BCM Platform
Единая точка доступа ко всем backend микросервисам
"""

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import json
import time
import logging
from typing import Dict, Any, Optional
import os
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("unified_api_gateway")

app = FastAPI(
    title="BCM Unified API Gateway",
    description="Centralized gateway for all BCM backend services",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service registry - все BCM backend сервисы (Docker hostnames)
SERVICE_REGISTRY = {
    # Core services
    "odoo": {"url": "http://odoo:8069", "health": "/web/health", "description": "Odoo BCM Core"},
    "ai_orchestrator": {"url": "http://ai_orchestrator:8000", "health": "/health", "description": "AI Orchestrator"},
    "database_gateway": {"url": "http://unified_database_gateway:8888", "health": "/health", "description": "Database Gateway"},
    "crm_bridge": {"url": "http://crm_bridge:8778", "health": "/health", "description": "CRM Bridge Service"},
    "monitoring_service": {"url": "http://monitoring_service:8779", "health": "/health", "description": "Monitoring Service"},

    # BCM modules
    "bia_engine": {"url": "http://bia_engine:8082", "health": "/health", "description": "BIA Engine"},
    "document_processor": {"url": "http://document_processor:8083", "health": "/health", "description": "Document Processor"},
    "compliance_checker": {"url": "http://compliance_checker:8084", "health": "/health", "description": "Compliance Checker"},
    "notification_service": {"url": "http://notification_service:8002", "health": "/health", "description": "Notification Service"},
    "github_app": {"url": "http://github_app:8011", "health": "/health", "description": "GitHub Integration"},

    # Infrastructure
    "prometheus": {"url": "http://prometheus:9090", "health": "/-/healthy", "description": "Prometheus"},
    "grafana": {"url": "http://grafana:3000", "health": "/api/health", "description": "Grafana"},
    "rabbitmq": {"url": "http://rabbitmq:15672", "health": "/api/aliveness-test/%2F", "description": "RabbitMQ Management"},

    # Simulation services
    "scenario_orchestrator": {"url": "http://scenario_orchestrator:8085", "health": "/health", "description": "Scenario Orchestrator"},
    "exercise_simulators": {"url": "http://exercise_simulators:8094", "health": "/health", "description": "Exercise Simulators"},
    "bcm_mcp_server": {"url": "http://bcm_mcp_server:8087", "health": "/health", "description": "BCM MCP Server"},

    # Development tools
    "module_validator": {"url": "http://module_validator:5001", "health": "/health", "description": "Module Validator"},
    "deployer": {"url": "http://deployer:8009", "health": "/health", "description": "Deployer Service"},

    # External services (localhost for external access)
    "external_grafana": {"url": "http://host.docker.internal:3003", "health": "/api/health", "description": "External Grafana (Host)"}
}

# Request metrics
request_metrics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "services_called": {},
    "start_time": datetime.now()
}

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Track request metrics"""
    start_time = time.time()
    request_metrics["total_requests"] += 1

    try:
        response = await call_next(request)
        if response.status_code < 400:
            request_metrics["successful_requests"] += 1
        else:
            request_metrics["failed_requests"] += 1
        return response
    except Exception as e:
        request_metrics["failed_requests"] += 1
        raise e
    finally:
        # Track service usage
        path = str(request.url.path)
        if path.startswith("/api/"):
            service = path.split("/")[2] if len(path.split("/")) > 2 else "unknown"
            request_metrics["services_called"][service] = request_metrics["services_called"].get(service, 0) + 1

@app.get("/health")
async def health_check():
    """Health check for the gateway"""
    return {
        "status": "healthy",
        "service": "unified_api_gateway",
        "timestamp": datetime.now().isoformat(),
        "registered_services": len(SERVICE_REGISTRY),
        "uptime": str(datetime.now() - request_metrics["start_time"])
    }

@app.get("/services")
async def list_services():
    """List all registered services"""
    return {
        "services": SERVICE_REGISTRY,
        "total": len(SERVICE_REGISTRY),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/services/health")
async def check_all_services():
    """Check health of all registered services"""
    health_results = []

    async with httpx.AsyncClient(timeout=5.0) as client:
        for service_name, service_config in SERVICE_REGISTRY.items():
            start_time = time.time()
            try:
                health_url = f"{service_config['url']}{service_config['health']}"
                response = await client.get(health_url)
                response_time = (time.time() - start_time) * 1000

                health_results.append({
                    "service": service_name,
                    "status": "online" if response.status_code == 200 else "degraded",
                    "url": service_config["url"],
                    "description": service_config["description"],
                    "response_time": round(response_time, 2),
                    "last_checked": datetime.now().isoformat()
                })
            except Exception as e:
                health_results.append({
                    "service": service_name,
                    "status": "offline",
                    "url": service_config["url"],
                    "description": service_config["description"],
                    "error": str(e),
                    "last_checked": datetime.now().isoformat()
                })

    online_count = sum(1 for r in health_results if r["status"] == "online")

    return {
        "services": health_results,
        "summary": {
            "total": len(health_results),
            "online": online_count,
            "offline": len(health_results) - online_count,
            "health_percentage": round((online_count / len(health_results)) * 100, 1)
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/metrics")
async def get_metrics():
    """Get gateway metrics"""
    uptime = datetime.now() - request_metrics["start_time"]

    return {
        "requests": {
            "total": request_metrics["total_requests"],
            "successful": request_metrics["successful_requests"],
            "failed": request_metrics["failed_requests"],
            "success_rate": round((request_metrics["successful_requests"] / max(request_metrics["total_requests"], 1)) * 100, 2)
        },
        "services": {
            "registered": len(SERVICE_REGISTRY),
            "usage": request_metrics["services_called"]
        },
        "uptime": {
            "seconds": int(uptime.total_seconds()),
            "human": str(uptime)
        },
        "timestamp": datetime.now().isoformat()
    }

# API Gateway routes - проксирование запросов к сервисам
@app.api_route("/api/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_to_service(service_name: str, path: str, request: Request):
    """Proxy requests to backend services"""

    # Check if service is registered
    if service_name not in SERVICE_REGISTRY:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service_name}' not found in registry"
        )

    service_config = SERVICE_REGISTRY[service_name]
    target_url = f"{service_config['url']}/{path}"

    # Get request body and headers
    body = await request.body()
    headers = dict(request.headers)

    # Remove host header to avoid conflicts
    headers.pop("host", None)

    # Make request to target service
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            start_time = time.time()

            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=dict(request.query_params)
            )

            response_time = (time.time() - start_time) * 1000

            # Log request
            logger.info(f"Proxied {request.method} {target_url} -> {response.status_code} ({response_time:.1f}ms)")

            # Return response
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type")
            )

        except httpx.TimeoutException:
            logger.error(f"Timeout calling {service_name}: {target_url}")
            raise HTTPException(status_code=504, detail=f"Service {service_name} timeout")
        except httpx.ConnectError:
            logger.error(f"Connection error to {service_name}: {target_url}")
            raise HTTPException(status_code=503, detail=f"Service {service_name} unavailable")
        except Exception as e:
            logger.error(f"Error calling {service_name}: {e}")
            raise HTTPException(status_code=500, detail=f"Internal error calling {service_name}")

# Direct database operations (legacy support)
@app.api_route("/database/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_database_gateway(path: str, request: Request):
    """Proxy database operations to database gateway"""
    return await proxy_to_service("database_gateway", path, request)

# Service discovery endpoints
@app.post("/services/register")
async def register_service(service_data: dict):
    """Register a new service"""
    service_name = service_data.get("name")
    if not service_name:
        raise HTTPException(status_code=400, detail="Service name required")

    SERVICE_REGISTRY[service_name] = {
        "url": service_data.get("url"),
        "health": service_data.get("health", "/health"),
        "description": service_data.get("description", f"Service {service_name}")
    }

    logger.info(f"Registered service: {service_name}")
    return {"message": f"Service {service_name} registered successfully"}

@app.delete("/services/{service_name}")
async def unregister_service(service_name: str):
    """Unregister a service"""
    if service_name not in SERVICE_REGISTRY:
        raise HTTPException(status_code=404, detail="Service not found")

    del SERVICE_REGISTRY[service_name]
    logger.info(f"Unregistered service: {service_name}")
    return {"message": f"Service {service_name} unregistered successfully"}

# Load balancing (simple round-robin for services with multiple instances)
service_instances = {}

@app.post("/services/{service_name}/instances")
async def add_service_instance(service_name: str, instance_data: dict):
    """Add instance for load balancing"""
    if service_name not in service_instances:
        service_instances[service_name] = []

    service_instances[service_name].append({
        "url": instance_data.get("url"),
        "weight": instance_data.get("weight", 1),
        "health": instance_data.get("health", "/health")
    })

    return {"message": f"Instance added to {service_name}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8777, log_level="info")