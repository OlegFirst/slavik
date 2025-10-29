#!/usr/bin/env python3
"""
Dynamic Service Registry - автоматическое обнаружение и регистрация сервисов
Заменяет статический реестр на динамический с health checks
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional, List, Set
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import asyncio
import httpx
import json
import logging
import os
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("service_registry")

app = FastAPI(
    title="BCM Service Registry",
    description="Dynamic service discovery and health monitoring",
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

# Service models
class ServiceStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"
    STARTING = "starting"
    STOPPING = "stopping"

class ServiceType(str, Enum):
    CORE = "core"
    API = "api"
    WORKER = "worker"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    INTEGRATION = "integration"

class ServiceInfo(BaseModel):
    """Information about a registered service"""
    name: str
    url: str
    health_endpoint: str = "/health"
    type: ServiceType = ServiceType.API
    description: str = ""
    version: str = "1.0.0"
    metadata: Dict[str, Any] = {}
    dependencies: List[str] = []
    tags: List[str] = []

class ServiceRegistration(BaseModel):
    """Service registration request"""
    name: str
    url: str
    health_endpoint: str = "/health"
    type: ServiceType = ServiceType.API
    description: str = ""
    version: str = "1.0.0"
    metadata: Dict[str, Any] = {}
    dependencies: List[str] = []
    tags: List[str] = []
    ttl: int = 60  # Time to live in seconds

class ServiceHealth(BaseModel):
    """Service health status"""
    name: str
    status: ServiceStatus
    url: str
    last_check: datetime
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    consecutive_failures: int = 0
    uptime_percentage: float = 100.0
    metadata: Dict[str, Any] = {}

# Registry manager
class RegistryManager:
    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.health_status: Dict[str, ServiceHealth] = {}
        self.subscriptions: Dict[str, Set[WebSocket]] = {}
        self.check_interval = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))
        self.failure_threshold = int(os.getenv("FAILURE_THRESHOLD", "3"))
        self.success_threshold = int(os.getenv("SUCCESS_THRESHOLD", "2"))

        # Track health history for uptime calculation
        self.health_history: Dict[str, List[bool]] = {}

        # Background tasks
        self.health_check_task = None
        self.cleanup_task = None

    async def start_background_tasks(self):
        """Start background health checks and cleanup"""
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())

        # Register self
        await self.register_service(ServiceRegistration(
            name="service-registry",
            url="http://service-registry:8002",
            type=ServiceType.CORE,
            description="Dynamic service registry and discovery"
        ))

    async def register_service(self, registration: ServiceRegistration) -> ServiceInfo:
        """Register a new service or update existing"""
        service = ServiceInfo(**registration.dict(exclude={'ttl'}))

        # Store service info
        self.services[service.name] = service

        # Initialize health status
        if service.name not in self.health_status:
            self.health_status[service.name] = ServiceHealth(
                name=service.name,
                status=ServiceStatus.STARTING,
                url=service.url,
                last_check=datetime.utcnow()
            )
            self.health_history[service.name] = []

        # Immediate health check
        asyncio.create_task(self._check_service_health(service.name))

        # Notify subscribers
        await self._notify_subscribers("service_registered", {
            "service": service.name,
            "url": service.url
        })

        logger.info(f"Service registered: {service.name} at {service.url}")
        return service

    async def deregister_service(self, service_name: str):
        """Remove a service from registry"""
        if service_name in self.services:
            del self.services[service_name]

            if service_name in self.health_status:
                self.health_status[service_name].status = ServiceStatus.STOPPING

            # Notify subscribers
            await self._notify_subscribers("service_deregistered", {
                "service": service_name
            })

            logger.info(f"Service deregistered: {service_name}")

    async def get_service(self, service_name: str) -> Optional[ServiceInfo]:
        """Get information about a specific service"""
        return self.services.get(service_name)

    async def get_healthy_service(self, service_name: str) -> Optional[ServiceInfo]:
        """Get service only if it's healthy"""
        service = self.services.get(service_name)
        if service and self.health_status.get(service_name):
            if self.health_status[service_name].status == ServiceStatus.HEALTHY:
                return service
        return None

    async def get_services_by_type(self, service_type: ServiceType) -> List[ServiceInfo]:
        """Get all services of a specific type"""
        return [s for s in self.services.values() if s.type == service_type]

    async def get_services_by_tag(self, tag: str) -> List[ServiceInfo]:
        """Get all services with a specific tag"""
        return [s for s in self.services.values() if tag in s.tags]

    async def _check_service_health(self, service_name: str):
        """Check health of a specific service"""
        if service_name not in self.services:
            return

        service = self.services[service_name]
        health = self.health_status.get(service_name)

        try:
            start_time = datetime.utcnow()

            # Make health check request
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{service.url}{service.health_endpoint}")

            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            if response.status_code == 200:
                # Service is healthy
                health.status = ServiceStatus.HEALTHY
                health.response_time_ms = response_time
                health.error = None
                health.consecutive_failures = 0

                # Try to get additional health data
                try:
                    health_data = response.json()
                    health.metadata = health_data
                except:
                    pass

                # Update history
                self.health_history[service_name].append(True)

            else:
                # Service returned non-200 status
                health.consecutive_failures += 1
                if health.consecutive_failures >= self.failure_threshold:
                    health.status = ServiceStatus.UNHEALTHY
                else:
                    health.status = ServiceStatus.DEGRADED
                health.error = f"HTTP {response.status_code}"
                self.health_history[service_name].append(False)

        except httpx.TimeoutException:
            health.consecutive_failures += 1
            if health.consecutive_failures >= self.failure_threshold:
                health.status = ServiceStatus.UNHEALTHY
            else:
                health.status = ServiceStatus.DEGRADED
            health.error = "Timeout"
            self.health_history[service_name].append(False)

        except Exception as e:
            health.consecutive_failures += 1
            if health.consecutive_failures >= self.failure_threshold:
                health.status = ServiceStatus.UNHEALTHY
            else:
                health.status = ServiceStatus.DEGRADED
            health.error = str(e)
            self.health_history[service_name].append(False)

        # Update last check time
        health.last_check = datetime.utcnow()

        # Calculate uptime percentage (last 100 checks)
        history = self.health_history[service_name][-100:]
        if history:
            health.uptime_percentage = (sum(history) / len(history)) * 100

        # Notify if status changed
        if health.consecutive_failures == self.failure_threshold:
            await self._notify_subscribers("service_unhealthy", {
                "service": service_name,
                "error": health.error
            })
        elif health.consecutive_failures == 0 and len(history) > 1 and not history[-2]:
            await self._notify_subscribers("service_recovered", {
                "service": service_name
            })

    async def _health_check_loop(self):
        """Background task for periodic health checks"""
        while True:
            try:
                await asyncio.sleep(self.check_interval)

                # Check all services
                tasks = [
                    self._check_service_health(name)
                    for name in self.services.keys()
                ]
                await asyncio.gather(*tasks, return_exceptions=True)

            except Exception as e:
                logger.error(f"Health check loop error: {e}")

    async def _cleanup_loop(self):
        """Clean up stale services"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute

                now = datetime.utcnow()
                stale_services = []

                for name, health in self.health_status.items():
                    # Remove services that haven't been checked in 5 minutes
                    if (now - health.last_check).seconds > 300:
                        stale_services.append(name)

                for name in stale_services:
                    await self.deregister_service(name)
                    logger.warning(f"Removed stale service: {name}")

            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")

    async def _notify_subscribers(self, event: str, data: Dict[str, Any]):
        """Notify WebSocket subscribers about events"""
        message = json.dumps({
            "event": event,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })

        for websockets in self.subscriptions.values():
            disconnected = set()
            for websocket in websockets:
                try:
                    await websocket.send_text(message)
                except:
                    disconnected.add(websocket)

            # Remove disconnected websockets
            for ws in disconnected:
                websockets.discard(ws)

# Initialize manager
registry = RegistryManager()

@app.on_event("startup")
async def startup():
    """Start background tasks on startup"""
    await registry.start_background_tasks()
    logger.info("Service Registry started")

# API Endpoints

@app.get("/health")
async def health_check():
    """Health check for the registry itself"""
    return {
        "status": "healthy",
        "service": "service-registry",
        "registered_services": len(registry.services),
        "healthy_services": sum(
            1 for h in registry.health_status.values()
            if h.status == ServiceStatus.HEALTHY
        )
    }

@app.post("/register")
async def register_service(registration: ServiceRegistration):
    """Register a new service"""
    service = await registry.register_service(registration)
    return {
        "status": "registered",
        "service": service.dict()
    }

@app.delete("/deregister/{service_name}")
async def deregister_service(service_name: str):
    """Remove a service from registry"""
    await registry.deregister_service(service_name)
    return {"status": "deregistered", "service": service_name}

@app.get("/services")
async def list_services():
    """List all registered services"""
    services = []
    for name, info in registry.services.items():
        health = registry.health_status.get(name)
        services.append({
            **info.dict(),
            "health": health.dict() if health else None
        })
    return {"services": services, "total": len(services)}

@app.get("/service/{service_name}")
async def get_service(service_name: str):
    """Get information about a specific service"""
    service = await registry.get_service(service_name)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    health = registry.health_status.get(service_name)
    return {
        **service.dict(),
        "health": health.dict() if health else None
    }

@app.get("/services/type/{service_type}")
async def get_services_by_type(service_type: ServiceType):
    """Get all services of a specific type"""
    services = await registry.get_services_by_type(service_type)
    return {"services": [s.dict() for s in services]}

@app.get("/services/tag/{tag}")
async def get_services_by_tag(tag: str):
    """Get all services with a specific tag"""
    services = await registry.get_services_by_tag(tag)
    return {"services": [s.dict() for s in services]}

@app.get("/health/all")
async def get_all_health():
    """Get health status of all services"""
    return {
        "health": {
            name: health.dict()
            for name, health in registry.health_status.items()
        }
    }

@app.get("/discover/{service_name}")
async def discover_service(service_name: str):
    """Discover a healthy instance of a service"""
    service = await registry.get_healthy_service(service_name)
    if not service:
        raise HTTPException(
            status_code=503,
            detail=f"No healthy instance of {service_name} available"
        )
    return {"service": service.dict()}

@app.websocket("/ws/subscribe")
async def websocket_subscribe(websocket: WebSocket):
    """Subscribe to registry events via WebSocket"""
    await websocket.accept()

    # Generate subscription ID
    subscription_id = f"ws_{id(websocket)}"

    # Add to subscriptions
    if subscription_id not in registry.subscriptions:
        registry.subscriptions[subscription_id] = set()
    registry.subscriptions[subscription_id].add(websocket)

    try:
        # Send initial state
        await websocket.send_json({
            "event": "connected",
            "services": list(registry.services.keys())
        })

        # Keep connection alive
        while True:
            await asyncio.sleep(30)
            await websocket.send_json({"event": "ping"})

    except WebSocketDisconnect:
        registry.subscriptions[subscription_id].discard(websocket)
        if not registry.subscriptions[subscription_id]:
            del registry.subscriptions[subscription_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)