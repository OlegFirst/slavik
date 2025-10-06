# TECHNICAL SPECIFICATIONS BY LAYER

Version: 1.0
Date: 2025-10-04
Purpose: Detailed technical specs for each system layer

---

## HOW TO USE THIS DOCUMENT

**For Developers:** Technical details for implementing/integrating components
**For AI Agents:** Specifications to follow when building features
**For MD:** Reference for reviewing implementation quality

Each layer includes:
- Component responsibilities
- API specifications
- Data models
- Integration patterns
- Code examples

---

## LAYER 1: INFRASTRUCTURE

### PostgreSQL (Supabase)

**Connection Details:**
```python
DATABASE_URL = "postgresql://postgres.{project_ref}:{password}@{host}:5432/postgres"

# Connection pooling
DB_POOL_SIZE = 20
DB_MAX_OVERFLOW = 10
DB_POOL_TIMEOUT = 30
```

**Schema Structure:**
```sql
-- All in 'public' schema for MVP
-- Future: separate schemas (platform, system, business)

-- Key tables
auth.users                  -- Supabase managed
public.organizations        -- Multi-tenant root
public.individual_users     -- User profiles
public.platform_administrators  -- Admin users

-- BCM tables (all have org_id for RLS)
public.bia_sessions
public.business_processes
public.risk_assessments
public.bc_plans
public.incidents
-- ... (80+ tables total)

-- Intelligence tables
public.workflow_states
public.workflow_cases
public.workflow_events
```

**RLS Policy Pattern:**
```sql
-- Every table must have
CREATE POLICY "tenant_isolation_policy" ON table_name
FOR ALL USING (
    org_id IN (
        SELECT org_id FROM user_organizations
        WHERE user_id = auth.uid()
    )
);
```

**Migration Workflow:**
```bash
# Apply migration
psql $DATABASE_URL -f migrations_source/XXX_migration_name.sql

# Verify
psql $DATABASE_URL -c "\dt public.*"

# Check RLS
psql $DATABASE_URL -c "SELECT schemaname, tablename, policyname
    FROM pg_policies WHERE schemaname='public';"
```

---

### Redis (Upstash)

**Connection:**
```python
import redis.asyncio as redis

redis_client = redis.from_url(
    os.getenv("REDIS_URL"),
    encoding="utf-8",
    decode_responses=True,
    max_connections=50
)
```

**Usage Patterns:**

**Cache:**
```python
# Decorator pattern
from shared.cache import cache_result

@cache_result(ttl=300)  # 5 minutes
async def get_organization(org_id: str):
    # Expensive DB query
    return org
```

**Session Storage:**
```python
# Store session
await redis_client.setex(
    f"session:{session_id}",
    3600,  # 1 hour
    json.dumps(session_data)
)

# Get session
data = await redis_client.get(f"session:{session_id}")
```

**Rate Limiting:**
```python
# IP-based rate limiting
key = f"rate_limit:{ip}:{endpoint}"
current = await redis_client.incr(key)
if current == 1:
    await redis_client.expire(key, 60)  # 1 minute window
if current > 100:  # Max 100 requests/minute
    raise HTTPException(status_code=429)
```

**Pub/Sub (EventBus):**
```python
# Publisher
await redis_client.publish(
    "events:bia.process.added",
    json.dumps(event_data)
)

# Subscriber
pubsub = redis_client.pubsub()
await pubsub.subscribe("events:*")
async for message in pubsub.listen():
    handle_event(message)
```

---

### Neo4j

**Connection:**
```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "password")
)
```

**Data Model:**
```cypher
-- ISO 22301 Structure
(Standard:ISO22301 {id, name, version})
  -[:HAS_CLAUSE]->
(Clause {id, title, number})
  -[:HAS_REQUIREMENT]->
(Requirement {id, text, type})
  -[:APPLIES_TO]->
(BusinessProcess {id, name})

-- Example query
MATCH (s:Standard {id: 'ISO22301:2019'})-[:HAS_CLAUSE]->(c:Clause)
WHERE c.number = '8.2.2'
MATCH (c)-[:HAS_REQUIREMENT]->(r:Requirement)
RETURN c.title, collect(r.text) as requirements
```

**Initialization:**
```python
# scripts/init_neo4j.py
def ingest_iso22301(session):
    # Create standard
    session.run("""
        CREATE (s:Standard {
            id: 'ISO22301:2019',
            name: 'ISO 22301:2019',
            published: date('2019-10-31')
        })
    """)

    # Create clauses
    clauses = [
        {"id": "8.2.2", "title": "Business impact analysis"},
        # ... all clauses
    ]

    for clause in clauses:
        session.run("""
            MATCH (s:Standard {id: 'ISO22301:2019'})
            CREATE (c:Clause {id: $id, title: $title})
            CREATE (s)-[:HAS_CLAUSE]->(c)
        """, **clause)
```

---

### RabbitMQ

**Connection:**
```python
# Via message_queue/rabbitmq_manager.py
from infrastructure.message_queue.rabbitmq_manager import get_rabbitmq_manager

mq = await get_rabbitmq_manager(
    url="amqp://user:pass@localhost:5672/"
)
```

**Exchange/Queue Setup:**
```python
# EventBus creates on startup
await mq.setup_exchanges({
    "bcm_events": {
        "type": "topic",
        "durable": True
    }
})

await mq.setup_queues({
    "bia_events": {
        "routing_keys": ["bia.*"],
        "exchange": "bcm_events",
        "durable": True,
        "arguments": {
            "x-message-ttl": 86400000,  # 24 hours
            "x-max-length": 10000
        }
    }
})
```

**Publish:**
```python
await mq.publish(
    exchange="bcm_events",
    routing_key="bia.process.added",
    message={
        "bia_id": "...",
        "process": {...}
    },
    priority=5
)
```

**Consume:**
```python
async def handle_bia_event(message):
    data = json.loads(message.body)
    # Process event
    await message.ack()

await mq.consume(
    queue="bia_events",
    callback=handle_bia_event
)
```

---

## LAYER 2: PLATFORM SERVICES

### EventBus Service

**API Specification:**

**Publish Event:**
```http
POST /publish
Content-Type: application/json

{
  "event_type": "bia.process.added",
  "tenant_id": "org_123",
  "data": {
    "bia_id": "bia_456",
    "process": {...}
  },
  "user_id": "user_789",
  "metadata": {...}
}

Response 201:
{
  "event_id": "evt_uuid",
  "published_at": "2025-10-04T01:00:00Z"
}
```

**Subscribe to Events:**
```http
POST /subscribe
Content-Type: application/json

{
  "service": "risk_service",
  "topics": ["bia.*", "governance.policy.*"],
  "webhook_url": "http://risk-service:8012/events"
}

Response 200:
{
  "subscription_id": "sub_uuid",
  "topics": ["bia.*", "governance.policy.*"]
}
```

**WebSocket Stream:**
```javascript
const ws = new WebSocket('ws://localhost:8001/ws?tenant_id=org_123');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data.event_type, data.data);
};
```

**Event Schema:**
```python
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional

class Event(BaseModel):
    event_id: str
    event_type: str
    tenant_id: str
    timestamp: datetime
    data: Dict[str, Any]
    user_id: Optional[str]
    correlation_id: Optional[str]
    metadata: Optional[Dict[str, Any]]
```

---

### API Gateway

**Route Configuration:**
```python
# main.py
from fastapi import FastAPI, Request
import httpx

ROUTES = {
    "/api/v1/bia": "http://bia-service:8011",
    "/api/v1/risk": "http://risk-service:8012",
    "/api/v1/governance": "http://governance-service:8020",
    # ... all services
}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str):
    # Find target service
    service_url = find_service_for_path(path)

    # Forward request
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=f"{service_url}/{path}",
            content=await request.body(),
            headers=dict(request.headers)
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )
```

**Auth Middleware:**
```python
from fastapi import Security
from fastapi.security import HTTPBearer
from shared.auth import verify_jwt

security = HTTPBearer()

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Skip auth for health checks
    if request.url.path == "/health":
        return await call_next(request)

    # Verify JWT
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        user = await verify_jwt(token)
        request.state.user = user
    except Exception:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )

    return await call_next(request)
```

---

### Shared Libraries

**auth/ - Authentication:**
```python
# shared/auth/__init__.py

async def verify_jwt(token: str) -> Dict:
    """Verify JWT token and return user data"""
    from jose import jwt

    payload = jwt.decode(
        token,
        os.getenv("JWT_SECRET"),
        algorithms=["HS256"]
    )
    return payload

async def get_current_user(
    token: str = Depends(HTTPBearer())
) -> Dict:
    """FastAPI dependency for getting current user"""
    return await verify_jwt(token.credentials)

async def require_permission(
    permission: str,
    user: Dict = Depends(get_current_user)
):
    """Check if user has permission"""
    if permission not in user.get("permissions", []):
        raise HTTPException(status_code=403)
```

**cache/ - Caching:**
```python
# shared/cache/__init__.py

def cache_result(ttl: int = 300):
    """Decorator for caching function results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = f"{func.__name__}:{args}:{kwargs}"

            # Try cache
            cached = await redis_client.get(key)
            if cached:
                return json.loads(cached)

            # Call function
            result = await func(*args, **kwargs)

            # Store in cache
            await redis_client.setex(
                key, ttl, json.dumps(result)
            )

            return result
        return wrapper
    return decorator
```

**eventbus/ - EventBus Client:**
```python
# shared/eventbus/__init__.py

class EventBusClient:
    def __init__(self, url: str):
        self.url = url
        self.client = httpx.AsyncClient()

    async def publish(
        self,
        event_type: str,
        data: Dict,
        tenant_id: str,
        user_id: Optional[str] = None
    ):
        """Publish event to EventBus"""
        await self.client.post(
            f"{self.url}/publish",
            json={
                "event_type": event_type,
                "tenant_id": tenant_id,
                "data": data,
                "user_id": user_id
            }
        )

    async def subscribe(
        self,
        topics: List[str],
        handler: Callable
    ):
        """Subscribe to event topics"""
        # Implementation varies based on architecture
        # Could be WebSocket or webhook
        pass
```

---

## LAYER 3: BCM CORE SERVICES

### Service Template Pattern

**All BCM services follow this structure:**

**1. Configuration (config.py):**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Service identity
    SERVICE_NAME: str = "bia_service"
    SERVICE_PORT: int = 8011
    SERVICE_VERSION: str = "1.0.0"

    # Dependencies
    DATABASE_URL: str
    REDIS_URL: str
    EVENTBUS_URL: str

    # Auth
    JWT_SECRET: str

    class Config:
        env_file = ".env"
```

**2. Main App (main.py):**
```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db(settings.DATABASE_URL)
    await init_cache(settings.REDIS_URL)
    eventbus = EventBusClient(settings.EVENTBUS_URL)

    # Register with EventBus
    await eventbus.subscribe(
        topics=get_subscribed_topics(),
        handler=handle_event
    )

    yield

    # Shutdown
    await close_db()
    await close_cache()

app = FastAPI(
    title=f"{settings.SERVICE_NAME} API",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan
)

# Include routers
from api.routes import router
app.include_router(router, prefix="/bia")
```

**3. Domain Models (models/domain.py):**
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ProcessTier(str, Enum):
    TIER_1 = "tier_1"  # Critical
    TIER_2 = "tier_2"  # Important
    TIER_3 = "tier_3"  # Normal
    TIER_4 = "tier_4"  # Low priority

class BusinessProcessCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    owner: str
    tier: ProcessTier

    @validator('name')
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

class BusinessProcess(BusinessProcessCreate):
    id: str
    bia_id: str
    created_at: datetime
    updated_at: datetime
```

**4. Database Models (models/database.py):**
```python
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from shared.database.base import Base
import uuid
from datetime import datetime

class BusinessProcessDB(Base):
    __tablename__ = "business_processes"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    bia_id = Column(UUID, ForeignKey("bia_sessions.id"), nullable=False)
    org_id = Column(UUID, ForeignKey("organizations.id"), nullable=False)

    name = Column(String(255), nullable=False)
    description = Column(String)
    owner = Column(String(255), nullable=False)
    tier = Column(Enum('tier_1', 'tier_2', 'tier_3', 'tier_4', name='tier'), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_process_bia', 'bia_id'),
        Index('idx_process_org', 'org_id'),
    )
```

**5. Repository (repositories/repository.py):**
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

class BIARepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_process(
        self,
        bia_id: str,
        process: BusinessProcessCreate,
        org_id: str
    ) -> str:
        db_process = BusinessProcessDB(
            bia_id=bia_id,
            org_id=org_id,
            **process.dict()
        )
        self.session.add(db_process)
        await self.session.commit()
        await self.session.refresh(db_process)
        return str(db_process.id)

    async def get_processes(
        self,
        bia_id: str
    ) -> List[BusinessProcess]:
        result = await self.session.execute(
            select(BusinessProcessDB)
            .where(BusinessProcessDB.bia_id == bia_id)
        )
        db_processes = result.scalars().all()
        return [BusinessProcess.from_orm(p) for p in db_processes]
```

**6. Business Logic (services/business_logic.py):**
```python
class BIAService:
    def __init__(
        self,
        repository: BIARepository,
        eventbus: EventBusClient
    ):
        self.repo = repository
        self.eventbus = eventbus

    async def add_process(
        self,
        bia_id: str,
        process: BusinessProcessCreate,
        org_id: str,
        user_id: str
    ) -> str:
        # Validate
        if not process.name:
            raise ValueError("Process name required")

        # Save
        process_id = await self.repo.create_process(
            bia_id, process, org_id
        )

        # Publish event
        await self.eventbus.publish(
            event_type="bia.process.added",
            tenant_id=org_id,
            data={
                "bia_id": bia_id,
                "process_id": process_id,
                "process": process.dict()
            },
            user_id=user_id
        )

        return process_id
```

**7. API Routes (api/routes.py):**
```python
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter()

@router.post(
    "/processes",
    response_model=dict,
    status_code=status.HTTP_201_CREATED
)
async def create_process(
    bia_id: str,
    process: BusinessProcessCreate,
    service: BIAService = Depends(get_bia_service),
    user: dict = Depends(get_current_user)
):
    """Create new business process for BIA"""
    try:
        process_id = await service.add_process(
            bia_id=bia_id,
            process=process,
            org_id=user["org_id"],
            user_id=user["user_id"]
        )
        return {"process_id": process_id}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

---

## LAYER 4: INTELLIGENCE LAYER

### Workflow Intelligence Engine

**State Machine Usage:**

**1. Define Workflow:**
```python
from workflow_intelligence.core.state_machine import StateMachine

class BIAWorkflow(StateMachine):
    def __init__(self, bia_id: str):
        super().__init__(
            workflow_id=bia_id,
            initial_state="identify_processes"
        )

        # Define transitions
        self.define_transition(
            from_state="identify_processes",
            to_state="analyze_dependencies",
            condition=lambda data: len(data.get("processes", [])) >= 3,
            validators=[validate_processes_complete]
        )

        # Define state requirements
        self.define_state_requirements(
            state="identify_processes",
            requirements={
                "min_requirements": {"processes": 3},
                "required_fields": ["organization_context"]
            }
        )
```

**2. Use in Service:**
```python
# In BIA Service
from workflow_intelligence import WorkflowEngine

workflow_engine = WorkflowEngine(module="bia")

@router.post("/bia/start")
async def start_bia(org_id: str):
    # Create BIA
    bia_id = await create_bia_in_db(org_id)

    # Initialize workflow
    await workflow_engine.start(
        workflow_id=bia_id,
        workflow_type="bia_process",
        tenant_id=org_id
    )

    return {"bia_id": bia_id, "state": "identify_processes"}

@router.post("/bia/{bia_id}/process")
async def add_process(bia_id: str, process: ProcessCreate):
    # Add to database
    process_id = await save_process(bia_id, process)

    # Update workflow
    await workflow_engine.execute_action(
        workflow_id=bia_id,
        action="add_process",
        data={"process": process.dict()}
    )

    # Check if can advance
    context = await workflow_engine.get_context(bia_id)
    if context["can_advance"]:
        return {
            "process_id": process_id,
            "message": "Ready to move to next stage",
            "next_stage": context["next_available_state"]
        }
    else:
        return {
            "process_id": process_id,
            "validation_errors": context["validation_errors"]
        }
```

**3. AI Context Integration:**
```python
from workflow_intelligence.ai import ContextAdvisor

advisor = ContextAdvisor(
    workflow_engine=workflow_engine,
    llm_provider="anthropic"  # or "openai"
)

@router.post("/bia/{bia_id}/advice")
async def get_ai_advice(bia_id: str, question: str):
    # Get workflow context
    context = await workflow_engine.get_context(bia_id)

    # Get AI advice
    advice = await advisor.get_contextual_advice(
        workflow_id=bia_id,
        user_question=question,
        context=context
    )

    return {
        "advice": advice["message"],
        "suggestions": advice["next_steps"],
        "relevant_cases": advice["similar_cases"]
    }
```

---

## LAYER 5: USER INTERFACES

### Web Application (Next.js)

**API Client:**
```typescript
// lib/api-client.ts
class APIClient {
  private baseURL: string;
  private token: string | null = null;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
  }

  async request(endpoint: string, options: RequestInit = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(this.token && { 'Authorization': `Bearer ${this.token}` }),
      ...options.headers,
    };

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  async createBIA(orgId: string) {
    return this.request('/api/v1/bia/start', {
      method: 'POST',
      body: JSON.stringify({ org_id: orgId }),
    });
  }

  async addProcess(biaId: string, process: ProcessCreate) {
    return this.request(`/api/v1/bia/${biaId}/process`, {
      method: 'POST',
      body: JSON.stringify(process),
    });
  }

  async getAIAdvice(biaId: string, question: string) {
    return this.request(`/api/v1/bia/${biaId}/advice`, {
      method: 'POST',
      body: JSON.stringify({ question }),
    });
  }
}

export const api = new APIClient();
```

**React Component:**
```typescript
// components/BIAWorkflow.tsx
'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api-client';

export default function BIAWorkflow({ biaId }: { biaId: string }) {
  const [processes, setProcesses] = useState([]);
  const [aiAdvice, setAIAdvice] = useState(null);

  const addProcess = async (process) => {
    const result = await api.addProcess(biaId, process);
    setProcesses([...processes, result]);
  };

  const getAdvice = async (question) => {
    const advice = await api.getAIAdvice(biaId, question);
    setAIAdvice(advice);
  };

  return (
    <div>
      <h2>Business Impact Analysis</h2>

      <ProcessList processes={processes} />
      <AddProcessForm onSubmit={addProcess} />

      <AIAdvisor
        onAsk={getAdvice}
        advice={aiAdvice}
      />
    </div>
  );
}
```

---

## TESTING SPECIFICATIONS

### Unit Tests

**Service Tests:**
```python
import pytest
from services.business_logic import BIAService

@pytest.mark.asyncio
async def test_add_process():
    # Arrange
    repo = MockRepository()
    eventbus = MockEventBus()
    service = BIAService(repo, eventbus)

    # Act
    process_id = await service.add_process(
        bia_id="bia_123",
        process=ProcessCreate(name="Test", owner="John", tier="tier_1"),
        org_id="org_123",
        user_id="user_123"
    )

    # Assert
    assert process_id is not None
    assert repo.save_called
    assert eventbus.publish_called
    assert eventbus.last_event["event_type"] == "bia.process.added"
```

### Integration Tests

**End-to-End Flow:**
```python
@pytest.mark.integration
async def test_bia_workflow_complete():
    # Start BIA
    response = await client.post("/bia/start", json={"org_id": "org_123"})
    bia_id = response.json()["bia_id"]

    # Add processes
    for i in range(3):
        await client.post(f"/bia/{bia_id}/process", json={
            "name": f"Process {i}",
            "owner": "John",
            "tier": "tier_1"
        })

    # Check workflow state
    context = await workflow_engine.get_context(bia_id)
    assert context["current_state"] == "analyze_dependencies"
    assert len(context["data"]["processes"]) == 3

    # Verify events published
    events = await eventbus.get_events(tenant_id="org_123")
    assert len(events) == 4  # 1 start + 3 process added
```

---

**End of Technical Specifications**

For implementation details, refer to existing code in:
- `/platform-services/` - BCM service implementations
- `/EXTRACTED_FROM_SESSION/` - Complete extracted modules
- `/shared/` - Reusable libraries
