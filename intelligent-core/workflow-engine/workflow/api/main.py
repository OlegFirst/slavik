"""
Unified Workflow Engine - REST API
===================================

FastAPI service for BPMN workflow management with:
- PostgreSQL persistence (Supabase)
- Redis caching
- EventBus integration
- Prometheus metrics
- Multi-tenancy (JWT auth)
"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

# Our modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from intelligent_core.platform_core.workflow.core.unified_engine import UnifiedWorkflowEngine
from intelligent_core.platform_core.workflow.bpmn.models import ProcessStatus, TaskStatus
from intelligent_core.platform_core.workflow.persistence.database import DatabaseManager

# Infrastructure
from infrastructure.eventbus import create_eventbus, Event
from infrastructure.database.managers.cache_manager import CacheManager
from infrastructure.database.managers.rate_limiter import RateLimiter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="Unified Workflow API",
    description="BPMN workflow engine with AI recommendations and PostgreSQL persistence",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# PROMETHEUS METRICS
# ============================================

# Counters
workflow_instances_total = Counter(
    'workflow_instances_total',
    'Total workflow instances created',
    ['tenant_id', 'module']
)

workflow_tasks_completed = Counter(
    'workflow_tasks_completed_total',
    'Total tasks completed',
    ['tenant_id', 'module']
)

workflow_instances_completed = Counter(
    'workflow_instances_completed_total',
    'Total workflow instances completed',
    ['tenant_id', 'module']
)

# Histograms
workflow_task_duration = Histogram(
    'workflow_task_duration_seconds',
    'Task completion duration',
    ['tenant_id', 'module', 'task_type']
)

workflow_instance_duration = Histogram(
    'workflow_instance_duration_seconds',
    'Workflow instance duration',
    ['tenant_id', 'module']
)

# Gauges
workflow_active_instances = Gauge(
    'workflow_active_instances',
    'Currently active workflow instances',
    ['tenant_id', 'module']
)

# ============================================
# GLOBAL STATE
# ============================================

eventbus = None
cache_manager = None
rate_limiter = None

# ============================================
# PYDANTIC MODELS
# ============================================

class StartProcessRequest(BaseModel):
    """Request to start workflow from BPMN"""
    bpmn_xml: str = Field(..., description="BPMN 2.0 XML content")
    process_name: str = Field(..., min_length=1, max_length=255)
    initial_variables: Dict[str, Any] = Field(default_factory=dict)
    started_by: Optional[str] = None
    description: Optional[str] = None
    version: str = Field(default="1.0")


class CompleteTaskRequest(BaseModel):
    """Request to complete task"""
    variables: Dict[str, Any] = Field(default_factory=dict)
    completed_by: Optional[str] = None


class AssignTaskRequest(BaseModel):
    """Request to assign task"""
    assignee: str = Field(..., description="Email of assignee")


class VisualStateResponse(BaseModel):
    """Visual state for UI rendering"""
    type: str
    bpmn_xml: str
    current_activities: List[str]
    active_tasks: List[Dict[str, Any]]
    workflow_context: Dict[str, Any]
    predictions: Optional[Dict[str, Any]] = None
    visualization_hints: Dict[str, Any]


# ============================================
# AUTHENTICATION & AUTHORIZATION
# ============================================

def get_tenant_id_from_header(x_tenant_id: Optional[str] = Header(None)) -> str:
    """
    Extract tenant ID from header

    In production, this should validate JWT token and extract tenant_id
    For now, simple header-based
    """
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Tenant-ID header"
        )
    return x_tenant_id


async def get_workflow_engine(
    tenant_id: str = Depends(get_tenant_id_from_header),
    module: str = "bia"
) -> UnifiedWorkflowEngine:
    """
    Dependency: Get workflow engine for tenant

    Creates new engine instance for each request
    (In production, consider connection pooling)
    """
    try:
        engine = await UnifiedWorkflowEngine.create(
            tenant_id=tenant_id,
            module=module,
            database_url=os.getenv("DATABASE_URL"),
            workflow_intelligence_enabled=True
        )
        return engine
    except Exception as e:
        logger.error(f"Failed to create workflow engine: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize workflow engine: {str(e)}"
        )


# ============================================
# STARTUP / SHUTDOWN
# ============================================

@app.on_event("startup")
async def startup():
    """Initialize infrastructure on startup"""
    global eventbus, cache_manager, rate_limiter

    logger.info("🚀 Starting Unified Workflow API...")

    # Initialize EventBus
    try:
        eventbus = create_eventbus('memory')  # or 'redis' if Redis available
        logger.info("✅ EventBus initialized")
    except Exception as e:
        logger.warning(f"⚠️ EventBus not available: {e}")

    # Initialize Cache Manager
    try:
        cache_manager = CacheManager()
        await cache_manager.connect()
        logger.info("✅ Cache Manager connected")
    except Exception as e:
        logger.warning(f"⚠️ Cache not available: {e}")

    # Initialize Rate Limiter
    try:
        rate_limiter = RateLimiter()
        await rate_limiter.connect()
        logger.info("✅ Rate Limiter initialized")
    except Exception as e:
        logger.warning(f"⚠️ Rate Limiter not available: {e}")

    logger.info("✅ Unified Workflow API ready!")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    global cache_manager, rate_limiter

    logger.info("🛑 Shutting down Unified Workflow API...")

    if cache_manager:
        await cache_manager.disconnect()

    if rate_limiter:
        await rate_limiter.disconnect()

    logger.info("✅ Shutdown complete")


# ============================================
# HEALTH & METRICS
# ============================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "unified-workflow-api",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "eventbus": eventbus is not None,
        "cache": cache_manager is not None,
        "rate_limiter": rate_limiter is not None
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# ============================================
# WORKFLOW ENDPOINTS
# ============================================

@app.post("/processes", status_code=status.HTTP_201_CREATED)
async def start_process(
    request: StartProcessRequest,
    engine: UnifiedWorkflowEngine = Depends(get_workflow_engine),
    tenant_id: str = Depends(get_tenant_id_from_header)
):
    """
    Start new workflow process from BPMN XML

    Returns:
        instance_id: UUID of created process instance
    """
    try:
        instance_id = await engine.start_process_from_bpmn(
            bpmn_xml=request.bpmn_xml,
            process_name=request.process_name,
            initial_variables=request.initial_variables,
            started_by=request.started_by,
            description=request.description,
            version=request.version
        )

        # Metrics
        workflow_instances_total.labels(
            tenant_id=tenant_id,
            module=engine.module
        ).inc()

        workflow_active_instances.labels(
            tenant_id=tenant_id,
            module=engine.module
        ).inc()

        # Publish event
        if eventbus:
            event = Event.create(
                event_type='workflow.instance.started',
                data={
                    'instance_id': instance_id,
                    'process_name': request.process_name,
                    'tenant_id': tenant_id,
                    'module': engine.module
                },
                source='workflow-api',
                tenant_id=tenant_id
            )
            await eventbus.publish(event)

        return {
            "instance_id": instance_id,
            "status": "started",
            "message": f"Workflow '{request.process_name}' started successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error starting process: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start process: {str(e)}"
        )
    finally:
        await engine.close()


@app.get("/instances/{instance_id}/visual-state")
async def get_visual_state(
    instance_id: str,
    engine: UnifiedWorkflowEngine = Depends(get_workflow_engine),
    tenant_id: str = Depends(get_tenant_id_from_header)
):
    """
    Get visual state for UI rendering (bpmn-js)

    Returns:
        VisualState with BPMN XML, active tasks, AI recommendations
    """
    try:
        # Check cache first
        cache_key = f"visual_state:{tenant_id}:{instance_id}"
        if cache_manager:
            cached = await cache_manager.get(cache_key)
            if cached:
                return cached

        visual_state = await engine.get_visual_state(instance_id)

        # Cache for 30 seconds
        if cache_manager:
            await cache_manager.set(cache_key, visual_state.dict(), ttl=30)

        return visual_state.dict()

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting visual state: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get visual state: {str(e)}"
        )
    finally:
        await engine.close()


@app.post("/tasks/{task_id}/complete", status_code=status.HTTP_200_OK)
async def complete_task(
    task_id: str,
    request: CompleteTaskRequest,
    engine: UnifiedWorkflowEngine = Depends(get_workflow_engine),
    tenant_id: str = Depends(get_tenant_id_from_header)
):
    """
    Complete task and advance workflow

    Handles gateway evaluation automatically
    """
    try:
        start_time = datetime.utcnow()

        await engine.complete_task(
            task_id=task_id,
            variables=request.variables,
            completed_by=request.completed_by
        )

        # Metrics
        duration = (datetime.utcnow() - start_time).total_seconds()
        workflow_task_duration.labels(
            tenant_id=tenant_id,
            module=engine.module,
            task_type="user_task"  # TODO: get actual task type
        ).observe(duration)

        workflow_tasks_completed.labels(
            tenant_id=tenant_id,
            module=engine.module
        ).inc()

        # Publish event
        if eventbus:
            event = Event.create(
                event_type='workflow.task.completed',
                data={
                    'task_id': task_id,
                    'tenant_id': tenant_id,
                    'variables': request.variables
                },
                source='workflow-api',
                tenant_id=tenant_id
            )
            await eventbus.publish(event)

        return {
            "status": "completed",
            "task_id": task_id,
            "message": "Task completed successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error completing task: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete task: {str(e)}"
        )
    finally:
        await engine.close()


@app.post("/tasks/{task_id}/assign", status_code=status.HTTP_200_OK)
async def assign_task(
    task_id: str,
    request: AssignTaskRequest,
    engine: UnifiedWorkflowEngine = Depends(get_workflow_engine)
):
    """Assign task to user"""
    try:
        await engine.assign_task(task_id=task_id, assignee=request.assignee)

        return {
            "status": "assigned",
            "task_id": task_id,
            "assignee": request.assignee
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error assigning task: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign task: {str(e)}"
        )
    finally:
        await engine.close()


@app.get("/users/{user_email}/tasks")
async def get_user_tasks(
    user_email: str,
    engine: UnifiedWorkflowEngine = Depends(get_workflow_engine),
    status_filter: Optional[TaskStatus] = None
):
    """
    Get user's task inbox

    Returns list of active tasks with AI recommendations
    """
    try:
        tasks = await engine.get_active_tasks_for_user(
            assignee=user_email,
            status=status_filter
        )

        return {
            "user": user_email,
            "tasks": tasks,
            "count": len(tasks)
        }

    except Exception as e:
        logger.error(f"Error getting user tasks: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tasks: {str(e)}"
        )
    finally:
        await engine.close()


@app.get("/processes")
async def list_processes(
    engine: UnifiedWorkflowEngine = Depends(get_workflow_engine),
    module: Optional[str] = None
):
    """List deployed BPMN processes"""
    try:
        processes = await engine.list_processes(module=module)

        return {
            "processes": processes,
            "count": len(processes)
        }

    except Exception as e:
        logger.error(f"Error listing processes: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list processes: {str(e)}"
        )
    finally:
        await engine.close()


@app.get("/instances")
async def list_instances(
    engine: UnifiedWorkflowEngine = Depends(get_workflow_engine),
    status_filter: Optional[ProcessStatus] = None
):
    """List workflow instances"""
    try:
        instances = await engine.list_instances(status=status_filter)

        return {
            "instances": instances,
            "count": len(instances)
        }

    except Exception as e:
        logger.error(f"Error listing instances: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list instances: {str(e)}"
        )
    finally:
        await engine.close()


@app.delete("/instances/{instance_id}", status_code=status.HTTP_200_OK)
async def terminate_instance(
    instance_id: str,
    reason: Optional[str] = None,
    engine: UnifiedWorkflowEngine = Depends(get_workflow_engine),
    tenant_id: str = Depends(get_tenant_id_from_header)
):
    """Terminate workflow instance"""
    try:
        await engine.terminate_process(instance_id=instance_id, reason=reason)

        # Metrics
        workflow_active_instances.labels(
            tenant_id=tenant_id,
            module=engine.module
        ).dec()

        return {
            "status": "terminated",
            "instance_id": instance_id,
            "reason": reason
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error terminating instance: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to terminate instance: {str(e)}"
        )
    finally:
        await engine.close()


# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("WORKFLOW_API_PORT", 8010))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
