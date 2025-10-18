# Saga Engine Integration Guide

This guide shows how to integrate the Saga Pattern Engine with the AI Platform ISO system.

## Table of Contents

1. [Quick Integration](#quick-integration)
2. [EventBus Integration](#eventbus-integration)
3. [Service Invoker Setup](#service-invoker-setup)
4. [State Store Configuration](#state-store-configuration)
5. [Coordination Center Integration](#coordination-center-integration)
6. [Workflow Intelligence Integration](#workflow-intelligence-integration)
7. [API Integration](#api-integration)
8. [Monitoring & Observability](#monitoring--observability)

## Quick Integration

### 1. Install Dependencies

Add to your service's `requirements.txt`:

```text
# Already included in platform
asyncpg>=0.27.0  # For PostgreSQL state store
aioredis>=2.0.0  # For Redis state store
```

### 2. Basic Setup

```python
# In your service initialization (e.g., main.py)

from intelligent_core.orchestration.saga_engine import (
    SagaOrchestrator,
    InMemorySagaStateStore,  # or RedisSagaStateStore, PostgresSagaStateStore
)
from intelligent_core.shared.eventbus import eventbus
from intelligent_core.orchestration.saga_engine.example_sagas import (
    register_all_example_sagas
)

# Create state store
state_store = InMemorySagaStateStore()
# OR for production:
# state_store = RedisSagaStateStore(redis_client)
# state_store = PostgresSagaStateStore(db_pool)

# Create orchestrator
saga_orchestrator = SagaOrchestrator(
    state_store=state_store,
    service_invoker=invoke_platform_service,  # See below
    event_publisher=lambda event_type, data: eventbus.publish(event_type, data)
)

# Register example sagas
register_all_example_sagas(saga_orchestrator)

# Make orchestrator available globally
app.state.saga_orchestrator = saga_orchestrator
```

## EventBus Integration

### Subscribe to Saga Events

```python
# In your event handlers setup

from intelligent_core.shared.eventbus import eventbus
from intelligent_core.orchestration.coordination_center.core.event_handlers import (
    CoordinationEventHandlers
)

async def setup_saga_event_handlers():
    """Setup handlers for saga events"""

    handlers = CoordinationEventHandlers()

    # Handle saga completion
    async def on_saga_completed(event_data: dict, tenant_id: str):
        saga_id = event_data.get("saga_id")
        saga_name = event_data.get("saga_name")
        result = event_data.get("result")

        logger.info(f"✅ Saga {saga_name} completed: {saga_id}")

        # Trigger downstream workflows
        if saga_name == "create_bcm_program":
            await trigger_program_activation(result)

    # Handle saga failure
    async def on_saga_failed(event_data: dict, tenant_id: str):
        saga_id = event_data.get("saga_id")
        error = event_data.get("error")

        logger.error(f"❌ Saga {saga_id} failed: {error}")

        # Send alerts
        await alerting_service.send_alert({
            "level": "error",
            "title": "Saga Execution Failed",
            "message": f"Saga {saga_id} failed: {error}",
            "saga_id": saga_id
        })

    # Handle compensation
    async def on_saga_compensated(event_data: dict, tenant_id: str):
        saga_id = event_data.get("saga_id")

        logger.info(f"🔄 Saga {saga_id} compensated (rolled back)")

        # Notify users
        await notification_service.notify_saga_rollback(saga_id)

    # Subscribe to events
    await eventbus.subscribe("saga.completed", on_saga_completed)
    await eventbus.subscribe("saga.failed", on_saga_failed)
    await eventbus.subscribe("saga.compensated", on_saga_compensated)
    await eventbus.subscribe("saga.compensation_failed", on_saga_failed)

# Call during application startup
await setup_saga_event_handlers()
```

### Publish Custom Events

```python
# From within your service methods

async def create_bia_assessment(params: dict):
    """Service method that can be called from saga"""

    # Publish event when starting
    await eventbus.publish("bia.assessment.started", {
        "assessment_id": params.get("_saga_id"),
        "tenant_id": params.get("_tenant_id")
    })

    # Do the work
    assessment = await do_create_assessment(params)

    # Publish event when done
    await eventbus.publish("bia.assessment.created", {
        "assessment_id": assessment.id,
        "tenant_id": params.get("_tenant_id")
    })

    return {"assessment_id": assessment.id, "status": "created"}
```

## Service Invoker Setup

The service invoker is the bridge between the Saga Engine and your platform services.

### Option 1: Direct Service Invocation

```python
# service_invoker.py

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Import all your services
from platform_services.bia_service.services.bia_service import BIAService
from platform_services.plans_service.services.plan_service import PlanService
from platform_services.compliance_service.services.assessment_engine import AssessmentEngine
# ... etc

# Create service instances (or get from dependency injection)
services = {
    "bia_service": BIAService(),
    "plans_service": PlanService(),
    "compliance_service": AssessmentEngine(),
    # ... etc
}

async def invoke_platform_service(action: str, params: Dict[str, Any]) -> Any:
    """
    Invoke a platform service method.

    Args:
        action: Service method in format "service_name.method_name"
        params: Method parameters

    Returns:
        Result from service invocation

    Raises:
        ValueError: If service or method not found
        Exception: Any exception from service method
    """
    try:
        # Parse action
        if '.' not in action:
            raise ValueError(f"Invalid action format: {action}. Expected 'service.method'")

        service_name, method_name = action.split('.', 1)

        # Get service
        service = services.get(service_name)
        if not service:
            raise ValueError(f"Service not found: {service_name}")

        # Get method
        if not hasattr(service, method_name):
            raise ValueError(f"Method not found: {service_name}.{method_name}")

        method = getattr(service, method_name)

        # Remove saga metadata from params before calling
        clean_params = {
            k: v for k, v in params.items()
            if not k.startswith('_')
        }

        # Invoke method
        logger.info(f"Invoking {action} with params: {list(clean_params.keys())}")
        result = await method(**clean_params)

        logger.info(f"Invoked {action} successfully")
        return result

    except Exception as e:
        logger.error(f"Error invoking {action}: {e}", exc_info=True)
        raise
```

### Option 2: HTTP Service Invocation

```python
# http_service_invoker.py

import httpx
from typing import Dict, Any

class HTTPServiceInvoker:
    """Invoke services via HTTP/REST APIs"""

    def __init__(self, service_registry: Dict[str, str]):
        """
        Args:
            service_registry: Map of service_name -> base_url
        """
        self.service_registry = service_registry
        self.client = httpx.AsyncClient(timeout=30.0)

    async def __call__(self, action: str, params: Dict[str, Any]) -> Any:
        """Invoke service method via HTTP"""

        service_name, method_name = action.split('.', 1)

        # Get service URL
        base_url = self.service_registry.get(service_name)
        if not base_url:
            raise ValueError(f"Service not found: {service_name}")

        # Map method to endpoint
        # You can customize this mapping
        endpoint = f"{base_url}/api/{method_name}"

        # Invoke
        response = await self.client.post(endpoint, json=params)
        response.raise_for_status()

        return response.json()

# Usage
service_registry = {
    "bia_service": "http://bia-service:8001",
    "plans_service": "http://plans-service:8002",
    "compliance_service": "http://compliance-service:8003",
}

service_invoker = HTTPServiceInvoker(service_registry)
```

### Option 3: Message Queue Invocation

```python
# mq_service_invoker.py

import json
import uuid
from typing import Dict, Any
import asyncio

class MessageQueueServiceInvoker:
    """Invoke services via message queue (async)"""

    def __init__(self, mq_client):
        self.mq = mq_client
        self.pending_responses = {}

    async def __call__(self, action: str, params: Dict[str, Any]) -> Any:
        """Invoke service via message queue"""

        # Create request
        request_id = str(uuid.uuid4())
        request = {
            "request_id": request_id,
            "action": action,
            "params": params
        }

        # Create response future
        future = asyncio.Future()
        self.pending_responses[request_id] = future

        # Send request
        service_name = action.split('.')[0]
        await self.mq.publish(
            f"service.{service_name}.requests",
            json.dumps(request)
        )

        # Wait for response (with timeout)
        try:
            result = await asyncio.wait_for(future, timeout=30.0)
            return result
        finally:
            self.pending_responses.pop(request_id, None)

    async def handle_response(self, message):
        """Handle response from service"""
        data = json.loads(message)
        request_id = data.get("request_id")

        future = self.pending_responses.get(request_id)
        if future and not future.done():
            if data.get("error"):
                future.set_exception(Exception(data["error"]))
            else:
                future.set_result(data.get("result"))
```

## State Store Configuration

### PostgreSQL Setup

```python
# database.py

import asyncpg
from intelligent_core.orchestration.saga_engine import PostgresSagaStateStore

async def setup_saga_state_store():
    """Setup PostgreSQL state store"""

    # Create connection pool
    db_pool = await asyncpg.create_pool(
        host="localhost",
        port=5432,
        database="bcm_platform",
        user="bcm_user",
        password="secure_password",
        min_size=5,
        max_size=20
    )

    # Initialize schema
    async with db_pool.acquire() as conn:
        with open("saga_engine/schema.sql") as f:
            await conn.execute(f.read())

    # Create state store
    state_store = PostgresSagaStateStore(db_pool)

    return state_store
```

### Redis Setup

```python
# redis_state_store.py

import aioredis
from intelligent_core.orchestration.saga_engine import RedisSagaStateStore

async def setup_redis_state_store():
    """Setup Redis state store"""

    # Create Redis client
    redis = await aioredis.create_redis_pool(
        'redis://localhost:6379',
        encoding='utf-8',
        minsize=5,
        maxsize=20
    )

    # Create state store
    state_store = RedisSagaStateStore(
        redis,
        key_prefix="bcm:saga:"
    )

    return state_store
```

## Coordination Center Integration

```python
# In coordination_center/main.py

from intelligent_core.orchestration.saga_engine import SagaOrchestrator

class CoordinationCenter:
    def __init__(self):
        self.saga_orchestrator = None

    def register_saga_orchestrator(self, orchestrator: SagaOrchestrator):
        """Register saga orchestrator"""
        self.saga_orchestrator = orchestrator

    async def execute_coordination_saga(
        self,
        saga_name: str,
        context: dict,
        tenant_id: str = None
    ):
        """Execute a saga as part of coordination"""

        if not self.saga_orchestrator:
            raise RuntimeError("Saga orchestrator not registered")

        # Execute saga
        execution = await self.saga_orchestrator.execute_saga(
            saga_name=saga_name,
            initial_context=context,
            tenant_id=tenant_id
        )

        # Return result
        if execution.is_completed():
            return {
                "status": "success",
                "saga_id": execution.saga_id,
                "result": execution.result
            }
        else:
            return {
                "status": "failed",
                "saga_id": execution.saga_id,
                "error": execution.error
            }

# In coordination API
@router.post("/execute-saga")
async def execute_saga(
    request: ExecuteSagaRequest,
    center: CoordinationCenter = Depends(get_coordination_center)
):
    """Execute a saga through coordination center"""

    result = await center.execute_coordination_saga(
        saga_name=request.saga_name,
        context=request.context,
        tenant_id=request.tenant_id
    )

    return result
```

## Workflow Intelligence Integration

```python
# In workflow_intelligence/saga_step_executor.py

from intelligent_core.orchestration.saga_engine import SagaOrchestrator

class SagaStepExecutor:
    """Execute sagas from workflow steps"""

    def __init__(self, saga_orchestrator: SagaOrchestrator):
        self.orchestrator = saga_orchestrator

    async def execute_saga_step(
        self,
        step: WorkflowStep,
        workflow_context: dict
    ):
        """Execute a workflow step that triggers a saga"""

        # Extract saga info from step
        saga_name = step.action_params.get("saga_name")
        saga_context = step.action_params.get("context", {})

        # Merge with workflow context
        merged_context = {**workflow_context, **saga_context}

        # Execute saga
        execution = await self.orchestrator.execute_saga(
            saga_name=saga_name,
            initial_context=merged_context,
            tenant_id=workflow_context.get("tenant_id"),
            correlation_id=workflow_context.get("workflow_id")
        )

        # Return result
        if execution.is_completed():
            return {
                "status": "completed",
                "output": execution.result
            }
        else:
            raise Exception(f"Saga failed: {execution.error}")

# In workflow definition
workflow = WorkflowDefinition(name="bcm_onboarding")

workflow.add_step(WorkflowStep(
    name="create_program",
    action_type="saga",
    action_params={
        "saga_name": "create_bcm_program",
        "context": {
            "program_name": "${input.program_name}",
            "organization_id": "${input.organization_id}"
        }
    }
))
```

## API Integration

### FastAPI Routes

```python
# api/saga_routes.py

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/sagas", tags=["sagas"])

class ExecuteSagaRequest(BaseModel):
    saga_name: str
    context: dict
    tenant_id: Optional[str] = None

class SagaStatusResponse(BaseModel):
    saga_id: str
    status: str
    started_at: Optional[str]
    completed_at: Optional[str]
    error: Optional[str]
    steps: list

@router.post("/execute")
async def execute_saga(
    request: ExecuteSagaRequest,
    orchestrator: SagaOrchestrator = Depends(get_saga_orchestrator)
):
    """Execute a saga"""

    execution = await orchestrator.execute_saga(
        saga_name=request.saga_name,
        initial_context=request.context,
        tenant_id=request.tenant_id
    )

    return {
        "saga_id": execution.saga_id,
        "status": execution.status.value
    }

@router.get("/{saga_id}")
async def get_saga_status(
    saga_id: str,
    orchestrator: SagaOrchestrator = Depends(get_saga_orchestrator)
):
    """Get saga execution status"""

    status = await orchestrator.get_saga_status(saga_id)

    if not status:
        raise HTTPException(status_code=404, detail="Saga not found")

    return status

@router.post("/{saga_id}/recover")
async def recover_saga(
    saga_id: str,
    orchestrator: SagaOrchestrator = Depends(get_saga_orchestrator)
):
    """Recover a failed saga"""

    execution = await orchestrator.recover_saga(saga_id)

    if not execution:
        raise HTTPException(status_code=404, detail="Saga not found")

    return {
        "saga_id": execution.saga_id,
        "status": execution.status.value
    }

@router.get("/")
async def list_sagas(
    status: Optional[str] = None,
    tenant_id: Optional[str] = None,
    limit: int = 100,
    orchestrator: SagaOrchestrator = Depends(get_saga_orchestrator)
):
    """List saga executions"""

    from intelligent_core.orchestration.saga_engine import SagaStatus

    status_enum = SagaStatus(status) if status else None

    sagas = await orchestrator.state_store.list_sagas(
        status=status_enum,
        tenant_id=tenant_id,
        limit=limit
    )

    return {
        "sagas": [
            {
                "saga_id": s.saga_id,
                "definition_name": s.definition_name,
                "status": s.status.value,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "tenant_id": s.tenant_id
            }
            for s in sagas
        ]
    }
```

## Monitoring & Observability

### Prometheus Metrics

```python
# monitoring/saga_metrics.py

from prometheus_client import Counter, Histogram, Gauge

# Metrics
saga_executions_total = Counter(
    'saga_executions_total',
    'Total saga executions',
    ['saga_name', 'status']
)

saga_duration_seconds = Histogram(
    'saga_duration_seconds',
    'Saga execution duration',
    ['saga_name']
)

saga_steps_total = Counter(
    'saga_steps_total',
    'Total saga step executions',
    ['saga_name', 'step_name', 'status']
)

saga_compensations_total = Counter(
    'saga_compensations_total',
    'Total saga compensations',
    ['saga_name', 'result']
)

active_sagas = Gauge(
    'active_sagas',
    'Number of currently executing sagas'
)

# Instrumentation wrapper
class InstrumentedSagaOrchestrator:
    def __init__(self, orchestrator: SagaOrchestrator):
        self.orchestrator = orchestrator

    async def execute_saga(self, *args, **kwargs):
        saga_name = args[0] if args else kwargs.get('saga_name')

        active_sagas.inc()
        try:
            with saga_duration_seconds.labels(saga_name=saga_name).time():
                execution = await self.orchestrator.execute_saga(*args, **kwargs)

            # Record metrics
            saga_executions_total.labels(
                saga_name=saga_name,
                status=execution.status.value
            ).inc()

            return execution
        finally:
            active_sagas.dec()
```

### Logging

```python
# logging_config.py

import logging
import json

class SagaLogFormatter(logging.Formatter):
    """Custom formatter for saga logs"""

    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name
        }

        # Add saga context if available
        if hasattr(record, 'saga_id'):
            log_data['saga_id'] = record.saga_id
        if hasattr(record, 'step_name'):
            log_data['step_name'] = record.step_name
        if hasattr(record, 'tenant_id'):
            log_data['tenant_id'] = record.tenant_id

        return json.dumps(log_data)

# Setup logging
handler = logging.StreamHandler()
handler.setFormatter(SagaLogFormatter())

saga_logger = logging.getLogger('saga_engine')
saga_logger.addHandler(handler)
saga_logger.setLevel(logging.INFO)
```

### Health Checks

```python
# health.py

@router.get("/health/sagas")
async def saga_health_check(
    orchestrator: SagaOrchestrator = Depends(get_saga_orchestrator)
):
    """Health check for saga engine"""

    from intelligent_core.orchestration.saga_engine import SagaStatus

    # Check for stuck sagas
    executing = await orchestrator.state_store.list_sagas(
        status=SagaStatus.EXECUTING
    )

    stuck_count = 0
    for saga in executing:
        if saga.started_at:
            duration = (datetime.utcnow() - saga.started_at).total_seconds()
            if duration > 3600:  # 1 hour
                stuck_count += 1

    return {
        "status": "healthy" if stuck_count == 0 else "degraded",
        "executing_sagas": len(executing),
        "stuck_sagas": stuck_count,
        "registered_definitions": len(orchestrator.saga_definitions)
    }
```

## Complete Example

See `example_integration.py` for a complete working example of integrating the Saga Engine with the AI Platform ISO system.

## Troubleshooting

### Common Issues

1. **Saga stuck in executing state**
   - Check service invoker is working
   - Check for timeout issues
   - Use recovery endpoint to resume

2. **Compensation not working**
   - Verify compensation_action is defined
   - Check service invoker can call compensation methods
   - Review compensation logs

3. **State not persisting**
   - Verify database connection
   - Check schema is created
   - Review state store configuration

4. **Events not publishing**
   - Verify EventBus connection
   - Check event_publisher is configured
   - Review EventBus logs

For more help, see the main README.md or contact the platform team.
