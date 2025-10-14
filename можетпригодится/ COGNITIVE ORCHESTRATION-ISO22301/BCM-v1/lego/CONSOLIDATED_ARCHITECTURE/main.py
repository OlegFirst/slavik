"""
Consolidated Cognitive Orchestration System
Hybrid: JavaScript Orchestrators + Python FastAPI + Production Integrations

Combines:
- Our 5 Parallel Orchestrators (universal architecture)
- Their FastAPI + Redis + PostgreSQL (production-ready)
- AI Bridge Layer (cognitive capabilities)
- Sandbox Evolution (self-improvement)
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import our orchestrator wrappers
from orchestrators import CognitiveOrchestrationController
from models import (
    SystemRequest, BridgeRequest, ProgramRequest,
    ClientRequest, SandboxRequest, HealthResponse,
    MetricsResponse, ExperimentRequest, BusinessLogicRequest
)
from integrations import RedisClient, PostgreSQLClient, DockerManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
cognitive_controller: Optional[CognitiveOrchestrationController] = None
redis_client: Optional[RedisClient] = None
postgres_client: Optional[PostgreSQLClient] = None
docker_manager: Optional[DockerManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with hybrid architecture startup"""
    global cognitive_controller, redis_client, postgres_client, docker_manager

    # Startup
    logger.info("🚀 Starting Consolidated Cognitive Orchestration System...")

    try:
        # Initialize production integrations (from colleagues)
        logger.info("🔗 Initializing production integrations...")
        redis_client = RedisClient()
        postgres_client = PostgreSQLClient()
        docker_manager = DockerManager()

        await redis_client.connect()
        await postgres_client.connect()
        await docker_manager.initialize()

        # Initialize our cognitive orchestrators
        logger.info("🧠 Initializing cognitive orchestrators...")
        cognitive_controller = CognitiveOrchestrationController({
            'redis_client': redis_client,
            'postgres_client': postgres_client,
            'docker_manager': docker_manager
        })

        await cognitive_controller.start()

        logger.info("✅ Consolidated system started successfully!")

        yield

    except Exception as error:
        logger.error(f"❌ Startup failed: {error}")
        raise

    # Shutdown
    logger.info("🛑 Shutting down Consolidated Cognitive Orchestration System...")

    if cognitive_controller:
        await cognitive_controller.shutdown()

    if redis_client:
        await redis_client.disconnect()

    if postgres_client:
        await postgres_client.disconnect()

    if docker_manager:
        await docker_manager.cleanup()

    logger.info("✅ Shutdown complete")


# Create FastAPI app with hybrid architecture
app = FastAPI(
    title="Cognitive Orchestration API",
    description="Consolidated hybrid architecture: Universal Orchestrators + Production Integrations",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== UNIVERSAL ORCHESTRATION ENDPOINTS =====

@app.post("/api/v2/orchestrate", response_model=Dict[str, Any])
async def universal_orchestrate(request: Dict[str, Any], background_tasks: BackgroundTasks):
    """
    Universal orchestration endpoint - automatically routes to correct orchestrator
    Combines our intelligent routing with their production infrastructure
    """
    try:
        # Use our AI-powered routing
        result = await cognitive_controller.handle(request)

        # Store metrics in Redis (their approach)
        background_tasks.add_task(store_metrics, request, result)

        return {
            "success": True,
            "result": result,
            "processed_by": "cognitive-orchestration-v2",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as error:
        logger.error(f"Orchestration error: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Orchestration failed: {str(error)}"
        )


@app.get("/api/v2/health", response_model=HealthResponse)
async def get_system_health():
    """Enhanced health check with production monitoring"""
    try:
        # Our cognitive health check
        cognitive_health = await cognitive_controller.get_system_health()

        # Their infrastructure health check
        infrastructure_health = {
            "redis": await redis_client.health_check(),
            "postgres": await postgres_client.health_check(),
            "docker": await docker_manager.health_check()
        }

        overall_status = "healthy"
        if not all(cognitive_health.get("orchestrators", {}).values()):
            overall_status = "degraded"
        if not all(infrastructure_health.values()):
            overall_status = "critical"

        return HealthResponse(
            status=overall_status,
            cognitive_orchestrators=cognitive_health,
            infrastructure=infrastructure_health,
            timestamp=datetime.utcnow()
        )

    except Exception as error:
        logger.error(f"Health check error: {error}")
        return HealthResponse(
            status="error",
            error=str(error),
            timestamp=datetime.utcnow()
        )


@app.get("/api/v2/metrics", response_model=MetricsResponse)
async def get_system_metrics():
    """Comprehensive metrics from both architectures"""
    try:
        # Our cognitive metrics
        cognitive_metrics = cognitive_controller.get_metrics()

        # Their infrastructure metrics
        infrastructure_metrics = {
            "redis_stats": await redis_client.get_stats(),
            "postgres_stats": await postgres_client.get_stats(),
            "docker_stats": await docker_manager.get_stats()
        }

        return MetricsResponse(
            cognitive=cognitive_metrics,
            infrastructure=infrastructure_metrics,
            timestamp=datetime.utcnow()
        )

    except Exception as error:
        logger.error(f"Metrics error: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metrics collection failed: {str(error)}"
        )


# ===== SPECIALIZED ORCHESTRATOR ENDPOINTS =====

@app.post("/api/v2/system/process")
async def system_orchestrate(request: SystemRequest):
    """System-level orchestration with Redis event bus"""
    result = await cognitive_controller.system_orchestrator.handle(request.dict())

    # Publish to Redis event bus (their approach)
    await redis_client.publish("system.events", {
        "type": "system.processed",
        "request_id": result.get("requestId"),
        "timestamp": datetime.utcnow().isoformat()
    })

    return result


@app.post("/api/v2/bridge/translate")
async def bridge_orchestrate(request: BridgeRequest):
    """AI-powered bridge translation with caching"""
    # Check Redis cache first (their approach)
    cache_key = f"bridge:{hash(str(request.dict()))}"
    cached_result = await redis_client.get(cache_key)

    if cached_result:
        return {"cached": True, "result": cached_result}

    # Use our AI bridge
    result = await cognitive_controller.bridge_orchestrator.handle(request.dict())

    # Cache result (their approach)
    await redis_client.setex(cache_key, 300, result)

    return {"cached": False, "result": result}


@app.post("/api/v2/program/execute")
async def program_orchestrate(request: ProgramRequest):
    """Business logic execution with PostgreSQL persistence"""
    result = await cognitive_controller.program_orchestrator.handle(request.dict())

    # Store execution record in PostgreSQL (their approach)
    await postgres_client.execute("""
        INSERT INTO program_executions (domain, module, action, result, timestamp)
        VALUES ($1, $2, $3, $4, $5)
    """, request.domain, request.module, request.action, result, datetime.utcnow())

    return result


@app.post("/api/v2/client/request")
async def client_orchestrate(request: ClientRequest):
    """Client request processing with enhanced security"""
    result = await cognitive_controller.client_orchestrator.handle(request.dict())
    return result


@app.post("/api/v2/sandbox/experiment")
async def sandbox_experiment(request: ExperimentRequest):
    """Sandbox experimentation with Docker isolation"""
    # Create isolated Docker container (their approach)
    container_id = await docker_manager.create_sandbox(
        image="python:3.11-slim",
        code=request.code,
        constraints=request.constraints
    )

    try:
        # Run experiment in our sandbox orchestrator
        result = await cognitive_controller.sandbox_orchestrator.handle({
            "type": "run-experiment",
            "container_id": container_id,
            **request.dict()
        })

        return result

    finally:
        # Cleanup container (their approach)
        await docker_manager.cleanup_container(container_id)


# ===== ADVANCED HYBRID ENDPOINTS =====

@app.post("/api/v2/business-logic/bcm")
async def execute_bcm_logic(request: BusinessLogicRequest):
    """BCM business logic with full integration stack"""
    # Use our program orchestrator for BCM domain
    result = await cognitive_controller.execute_business_logic(
        domain="bcm",
        module=request.module,
        action=request.action,
        data=request.data,
        context=request.context or {}
    )

    # Store in PostgreSQL with audit trail (their approach)
    await postgres_client.execute("""
        INSERT INTO bcm_operations (module, action, data, result, user_id, timestamp)
        VALUES ($1, $2, $3, $4, $5, $6)
    """, request.module, request.action, request.data, result,
        request.context.get("user_id"), datetime.utcnow())

    return result


@app.post("/api/v2/ai/evolve")
async def evolve_system_component(component: str, parameters: Dict[str, Any] = None):
    """AI evolution with persistent learning"""
    # Use our sandbox for evolution
    result = await cognitive_controller.evolve_component(component, parameters or {})

    # Store evolution results in PostgreSQL (their approach)
    if result.get("improvement", 0) > 1.1:
        await postgres_client.execute("""
            INSERT INTO evolution_improvements (component, improvement_factor,
                                             parameters, timestamp)
            VALUES ($1, $2, $3, $4)
        """, component, result["improvement"], parameters, datetime.utcnow())

    return result


@app.get("/api/v2/dashboard/status")
async def get_dashboard_data():
    """Dashboard data combining both architectures"""
    # Get data from all sources
    cognitive_status = await cognitive_controller.get_system_health()
    infrastructure_status = {
        "redis": await redis_client.get_info(),
        "postgres": await postgres_client.get_connection_stats(),
        "docker": await docker_manager.get_container_stats()
    }

    # Recent operations from PostgreSQL (their approach)
    recent_operations = await postgres_client.fetch("""
        SELECT module, action, timestamp FROM bcm_operations
        ORDER BY timestamp DESC LIMIT 10
    """)

    return {
        "cognitive_orchestrators": cognitive_status,
        "infrastructure": infrastructure_status,
        "recent_operations": recent_operations,
        "timestamp": datetime.utcnow().isoformat()
    }


# ===== UTILITY FUNCTIONS =====

async def store_metrics(request: Dict[str, Any], result: Dict[str, Any]):
    """Background task to store metrics"""
    try:
        await redis_client.lpush("request_metrics", {
            "request_type": request.get("type"),
            "duration": result.get("duration"),
            "success": result.get("success"),
            "timestamp": datetime.utcnow().isoformat()
        })

        # Keep only last 1000 metrics
        await redis_client.ltrim("request_metrics", 0, 999)

    except Exception as error:
        logger.warning(f"Failed to store metrics: {error}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )