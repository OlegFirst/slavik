"""
Service Discovery - Enhanced Service Registry with Catalog Integration

Unified service discovery system combining:
- Static Service Catalog (templates/specifications)
- Dynamic Service Registry (runtime data)
- EventBus integration (real-time updates)
- PostgreSQL persistence (historical data)

Port: 8500 (Consul-compatible port)
"""

import logging
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import uvicorn

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from infrastructure.runtime.service_discovery.service_registry import ServiceRegistry
from infrastructure.runtime.service_discovery.catalog_integration import CatalogIntegration
from infrastructure.runtime.service_discovery.eventbus_integration import ServiceDiscoveryEventBusIntegration
from infrastructure.runtime.service_discovery.metrics_exporter import export_catalog_metrics

# Prometheus imports
from prometheus_client import make_asgi_app
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# EventBus imports
try:
    from infrastructure.eventbus import create_eventbus
    EVENTBUS_AVAILABLE = True
except ImportError:
    EVENTBUS_AVAILABLE = False
    logging.warning("EventBus not available")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("SERVICE_DISCOVERY_PORT", "8500"))
HOST = os.getenv("SERVICE_DISCOVERY_HOST", "0.0.0.0")

# Global instances
service_registry: Optional[ServiceRegistry] = None
catalog_integration: Optional[CatalogIntegration] = None
eventbus_integration: Optional[ServiceDiscoveryEventBusIntegration] = None
eventbus = None
scheduler: Optional[AsyncIOScheduler] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global service_registry, catalog_integration, eventbus_integration, eventbus, scheduler

    logger.info(" Service Discovery v2.0 starting...")
    logger.info("    Enhanced with Catalog Integration")

    # Initialize Service Registry
    service_registry = ServiceRegistry()
    logger.info("    Service Registry initialized")

    # Initialize Catalog Integration
    try:
        catalog_integration = CatalogIntegration()
        await catalog_integration.initialize()
        logger.info("    Catalog Integration initialized")
    except Exception as e:
        logger.error(f"    Catalog Integration failed: {e}")
        logger.warning("   ️  Running without Catalog")

    # Initialize EventBus Integration
    if EVENTBUS_AVAILABLE:
        try:
            eventbus = create_eventbus('redis')
            await eventbus.connect()
            logger.info("    EventBus connected")

            eventbus_integration = ServiceDiscoveryEventBusIntegration(
                service_registry=service_registry,
                eventbus=eventbus,
                heartbeat_timeout=60
            )
            await eventbus_integration.start()
            logger.info("    EventBus Integration started")

        except Exception as e:
            logger.error(f"    EventBus integration failed: {e}")
            logger.warning("   ️  Running without EventBus")
            eventbus_integration = None
    else:
        logger.warning("   ️  EventBus not available")

    # Initialize Prometheus Metrics Export
    if catalog_integration:
        try:
            # Initial export
            await export_catalog_metrics(catalog_integration, service_registry)
            logger.info("    Initial metrics exported to Prometheus")

            # Start periodic export (every 30 seconds)
            scheduler = AsyncIOScheduler()
            scheduler.add_job(
                export_catalog_metrics,
                'interval',
                seconds=30,
                args=[catalog_integration, service_registry],
                id='catalog_metrics_export',
                name='Export catalog metrics to Prometheus'
            )
            scheduler.start()
            logger.info("    Metrics export scheduler started (30s interval)")
        except Exception as e:
            logger.error(f"    Metrics export initialization failed: {e}")
            logger.warning("   ️  Running without Prometheus metrics")

    logger.info(" Service Discovery v2.0 ready on port 8500")
    logger.info("    Consul-compatible endpoints available")
    logger.info("    Unified Catalog + Registry view enabled")
    logger.info("    Prometheus metrics available at /metrics")

    yield

    # Shutdown
    logger.info(" Service Discovery shutting down...")

    if scheduler:
        scheduler.shutdown()
        logger.info("    Metrics scheduler stopped")

    if eventbus_integration:
        await eventbus_integration.stop()

    if eventbus:
        await eventbus.disconnect()

    logger.info(" Shutdown complete")

app = FastAPI(
    title="Service Discovery v2.0",
    description="Enhanced service registry with catalog integration",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Legacy in-memory registry for Consul compatibility
services: Dict[str, Dict] = {}

class ServiceRegistration(BaseModel):
    service_id: str
    service_name: str
    host: str
    port: int
    tags: Optional[List[str]] = []
    meta: Optional[Dict] = {}

class HealthCheck(BaseModel):
    service_id: str
    status: str  # "passing", "warning", "critical"

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "service-discovery",
        "version": "1.0.0",
        "registered_services": len(services)
    }

@app.post("/v1/agent/service/register")
async def register_service(registration: ServiceRegistration):
    """Register a service (Consul-compatible endpoint)"""
    services[registration.service_id] = {
        "id": registration.service_id,
        "name": registration.service_name,
        "host": registration.host,
        "port": registration.port,
        "tags": registration.tags,
        "meta": registration.meta,
        "registered_at": datetime.now().isoformat(),
        "health_status": "passing",
        "last_check": datetime.now().isoformat()
    }

    logger.info(f"Service registered: {registration.service_id} ({registration.service_name})")

    return {
        "status": "registered",
        "service_id": registration.service_id
    }

@app.delete("/v1/agent/service/deregister/{service_id}")
async def deregister_service(service_id: str):
    """Deregister a service"""
    if service_id not in services:
        raise HTTPException(status_code=404, detail="Service not found")

    del services[service_id]
    logger.info(f"Service deregistered: {service_id}")

    return {
        "status": "deregistered",
        "service_id": service_id
    }

@app.get("/v1/catalog/services")
async def list_services():
    """List all registered services"""
    unique_services = {}

    for service in services.values():
        name = service["name"]
        if name not in unique_services:
            unique_services[name] = service["tags"]

    return unique_services

@app.get("/v1/catalog/service/{service_name}")
async def get_service_instances(service_name: str):
    """Get all instances of a service"""
    instances = [
        {
            "ServiceID": s["id"],
            "ServiceName": s["name"],
            "ServiceAddress": s["host"],
            "ServicePort": s["port"],
            "ServiceTags": s["tags"],
            "ServiceMeta": s["meta"]
        }
        for s in services.values()
        if s["name"] == service_name
    ]

    if not instances:
        raise HTTPException(status_code=404, detail="Service not found")

    return instances

@app.put("/v1/agent/check/pass/{service_id}")
async def health_check_pass(service_id: str):
    """Mark health check as passing"""
    if service_id not in services:
        raise HTTPException(status_code=404, detail="Service not found")

    services[service_id]["health_status"] = "passing"
    services[service_id]["last_check"] = datetime.now().isoformat()

    return {"status": "ok"}

@app.put("/v1/agent/check/fail/{service_id}")
async def health_check_fail(service_id: str):
    """Mark health check as failed"""
    if service_id not in services:
        raise HTTPException(status_code=404, detail="Service not found")

    services[service_id]["health_status"] = "critical"
    services[service_id]["last_check"] = datetime.now().isoformat()

    return {"status": "ok"}

@app.get("/v1/health/service/{service_name}")
async def get_service_health(service_name: str):
    """Get health status of all instances of a service"""
    instances = [
        {
            "ServiceID": s["id"],
            "ServiceName": s["name"],
            "Status": s["health_status"],
            "LastCheck": s["last_check"]
        }
        for s in services.values()
        if s["name"] == service_name
    ]

    if not instances:
        raise HTTPException(status_code=404, detail="Service not found")

    return instances


# ============================================================================
# Enhanced Unified Catalog + Registry Endpoints
# ============================================================================

@app.get("/v2/catalog/services")
async def get_unified_services():
    """
    Get all services with unified catalog + runtime data

    Returns services from both catalog and registry,
    showing which are missing, registered, or unknown.
    """
    if not catalog_integration or not service_registry:
        raise HTTPException(
            status_code=503,
            detail="Catalog integration not available"
        )

    try:
        all_services = await catalog_integration.get_all_unified_services(service_registry)

        return {
            "services": [s.to_dict() for s in all_services],
            "count": len(all_services)
        }
    except Exception as e:
        logger.error(f"Error getting unified services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v2/catalog/services/{service_name}")
async def get_unified_service(service_name: str):
    """Get detailed unified view of a single service"""
    if not catalog_integration or not service_registry:
        raise HTTPException(
            status_code=503,
            detail="Catalog integration not available"
        )

    try:
        runtime_service = await service_registry.get_service(service_name)
        unified_service = await catalog_integration.get_unified_service(
            service_name,
            runtime_service
        )

        if not unified_service:
            raise HTTPException(status_code=404, detail="Service not found")

        return unified_service.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v2/catalog/stats")
async def get_catalog_stats():
    """
    Get comprehensive catalog statistics

    Shows:
    - Total services in catalog
    - Registered services (running)
    - Missing services (in catalog but not running)
    - Unknown services (running but not in catalog)
    - Coverage percentage
    - Grouping by type and business process
    """
    if not catalog_integration or not service_registry:
        raise HTTPException(
            status_code=503,
            detail="Catalog integration not available"
        )

    try:
        stats = await catalog_integration.get_catalog_stats(service_registry)
        return stats
    except Exception as e:
        logger.error(f"Error getting catalog stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v2/catalog/missing")
async def get_missing_services():
    """
    Get services that are in catalog but not registered

    These are services that SHOULD be running but aren't
    """
    if not catalog_integration or not service_registry:
        raise HTTPException(
            status_code=503,
            detail="Catalog integration not available"
        )

    try:
        missing = await catalog_integration.get_missing_services(service_registry)
        return {
            "services": [s.to_dict() for s in missing],
            "count": len(missing)
        }
    except Exception as e:
        logger.error(f"Error getting missing services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v2/catalog/unknown")
async def get_unknown_services():
    """
    Get services that are running but not in catalog

    These are services that are registered but have no template/specification
    """
    if not catalog_integration or not service_registry:
        raise HTTPException(
            status_code=503,
            detail="Catalog integration not available"
        )

    try:
        unknown = await catalog_integration.get_unknown_services(service_registry)
        return {
            "services": [s.to_dict() for s in unknown],
            "count": len(unknown)
        }
    except Exception as e:
        logger.error(f"Error getting unknown services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v2/catalog/healthy")
async def get_healthy_services():
    """
    Get all healthy services

    Healthy = registered + running + health_status=healthy
    """
    if not catalog_integration or not service_registry:
        raise HTTPException(
            status_code=503,
            detail="Catalog integration not available"
        )

    try:
        healthy = await catalog_integration.get_healthy_services(service_registry)
        return {
            "services": [s.to_dict() for s in healthy],
            "count": len(healthy)
        }
    except Exception as e:
        logger.error(f"Error getting healthy services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v2/registry/services")
async def get_registry_services():
    """
    Get all services from service registry (runtime only)

    This is the raw runtime data without catalog enrichment
    """
    if not service_registry:
        raise HTTPException(
            status_code=503,
            detail="Service registry not available"
        )

    try:
        services_list = await service_registry.list_services()
        return {
            "services": [s.to_dict() for s in services_list],
            "count": len(services_list)
        }
    except Exception as e:
        logger.error(f"Error getting registry services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v2/registry/stats")
async def get_registry_stats():
    """Get service registry statistics"""
    if not service_registry:
        raise HTTPException(
            status_code=503,
            detail="Service registry not available"
        )

    try:
        stats = await service_registry.get_registry_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting registry stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    logger.info(f"Starting Service Discovery on {HOST}:{PORT}")
    logger.info("Consul-compatible API endpoints enabled")

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    )
