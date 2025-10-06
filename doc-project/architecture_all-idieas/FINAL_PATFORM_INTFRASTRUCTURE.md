Продолжаю алгоритм запуска:

---

```bash
# 1. Создать .env
cp .env.example .env
# Отредактировать: добавить API ключи (OpenAI, Anthropic, Pinecone)

# 2. Запустить инфраструктуру
docker-compose -f docker-compose.dev.yml up -d

# 3. Проверить что всё работает
docker-compose ps  # все сервисы должны быть "Up"

# 4. Проверить connectivity
psql postgresql://bcm:bcm_dev_pass@localhost:5432/bcm_platform
# \dt  # должна быть пустая БД
# \q

redis-cli ping  # должно вернуть PONG

# 5. Проверить Neo4j
# Открыть http://localhost:7474
# Login: neo4j / neo4j_dev_pass
```

### Phase 2: Database Schemas (День 1-2)

```bash
# Создать все migrations для каждого сервиса

# Governance Service
cd services/governance
alembic init alembic
# Создать модели в models/database.py
alembic revision --autogenerate -m "initial governance schema"
alembic upgrade head

# BIA Service
cd ../bia
alembic init alembic
alembic revision --autogenerate -m "initial bia schema"
alembic upgrade head

# Risk Service
cd ../risk
alembic init alembic
alembic revision --autogenerate -m "initial risk schema"
alembic upgrade head

# ... repeat for all services

# Case Library
cd ../case_library
alembic init alembic
alembic revision --autogenerate -m "workflow cases schema"
alembic upgrade head
```

**Verify migrations:**
```sql
-- Проверить что таблицы созданы
psql postgresql://bcm:bcm_dev_pass@localhost:5432/bcm_platform

\dt  -- должны видеть все таблицы

SELECT * FROM organizations;  -- пусто, но таблица есть
```

### Phase 3: Knowledge Graph (День 2-3)

```bash
# Ingest ISO 22301 в Neo4j
cd scripts
python ingest_iso22301.py

# Ingest BCI Good Practice Guidelines
python ingest_bci_gpg.py

# Verify в Neo4j browser (http://localhost:7474)
# Query:
MATCH (s:Standard) RETURN s

# Должны видеть ISO 22301, ISO 27001, BCI GPG
```

**Скрипт для инициализации Knowledge Graph:**

```python
# scripts/ingest_iso22301.py
from neo4j import GraphDatabase
import json

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "neo4j_dev_pass")
)

def ingest_iso22301():
    with driver.session() as session:
        # Standard
        session.run("""
            CREATE (s:Standard {
                id: 'ISO22301:2019',
                name: 'ISO 22301:2019',
                title: 'Security and resilience - Business continuity management systems',
                type: 'international_standard',
                published: date('2019-10-31')
            })
        """)
        
        # Clauses (упрощенная версия)
        clauses = [
            {"id": "4", "title": "Context of the organization", "parent": None},
            {"id": "4.1", "title": "Understanding the organization and its context", "parent": "4"},
            {"id": "5", "title": "Leadership", "parent": None},
            {"id": "6", "title": "Planning", "parent": None},
            {"id": "6.1", "title": "Actions to address risks and opportunities", "parent": "6"},
            {"id": "7", "title": "Support", "parent": None},
            {"id": "8", "title": "Operation", "parent": None},
            {"id": "8.2", "title": "Business impact analysis and risk assessment", "parent": "8"},
            {"id": "8.2.2", "title": "Business impact analysis", "parent": "8.2"},
            {"id": "8.3", "title": "Business continuity strategy", "parent": "8"},
            {"id": "8.4", "title": "Business continuity procedures", "parent": "8"},
            {"id": "8.4.4", "title": "Business continuity plans and procedures", "parent": "8.4"},
            {"id": "9", "title": "Performance evaluation", "parent": None},
            {"id": "10", "title": "Improvement", "parent": None}
        ]
        
        for clause in clauses:
            session.run("""
                MATCH (s:Standard {id: 'ISO22301:2019'})
                CREATE (c:Clause {
                    id: $id,
                    title: $title,
                    parent: $parent
                })
                CREATE (s)-[:HAS_CLAUSE]->(c)
            """, **clause)
        
        # Requirements (примеры для 8.2.2)
        requirements = [
            {
                "clause": "8.2.2",
                "req_id": "8.2.2.a",
                "text": "The organization shall conduct a BIA to identify critical activities and their dependencies",
                "type": "mandatory"
            },
            {
                "clause": "8.2.2",
                "req_id": "8.2.2.b",
                "text": "Determine impact over time of disruption to critical activities",
                "type": "mandatory"
            },
            {
                "clause": "8.2.2",
                "req_id": "8.2.2.c",
                "text": "Establish prioritized timeframes (RTO, RPO, MTPD)",
                "type": "mandatory"
            }
        ]
        
        for req in requirements:
            session.run("""
                MATCH (c:Clause {id: $clause})
                CREATE (r:Requirement {
                    id: $req_id,
                    text: $text,
                    type: $type
                })
                CREATE (c)-[:HAS_REQUIREMENT]->(r)
            """, **req)
        
        print("✅ ISO 22301 ingested successfully")

if __name__ == "__main__":
    ingest_iso22301()
    driver.close()
```

### Phase 4: Core Platform Services (День 3-4)

**Порядок запуска (важен!):**

```bash
# 1. EventBus (первым - все от него зависят)
cd services/eventbus
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# Должен запуститься на :8001

# Verify:
curl http://localhost:8001/health
# {"status": "healthy"}

# 2. Orchestrator (вторым)
cd ../orchestrator
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# :8002

curl http://localhost:8002/health

# 3. API Gateway (третьим)
cd ../api_gateway
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# :8000

curl http://localhost:8000/health
```

### Phase 5: Domain Services (День 4-7)

**Запускать в порядке зависимостей:**

```bash
# 1. Governance (не зависит ни от кого)
cd services/governance
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# :8010

# Test: создать организацию
curl -X POST http://localhost:8000/api/organizations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Hospital",
    "industry": "healthcare",
    "size": "medium"
  }'

# 2. BIA (зависит от Governance)
cd ../bia
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# :8011

# Test: начать BIA
curl -X POST http://localhost:8000/api/bia/start \
  -H "Content-Type: application/json" \
  -d '{"org_id": "org_id_from_previous_step"}'

# 3. Risk (зависит от BIA)
cd ../risk
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# :8013

# 4. Planning (зависит от BIA + Risk)
cd ../planning
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# :8015

# 5. Response
cd ../response
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# :8016

# 6. Compliance
cd ../compliance
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# :8018

# 7. Documents
cd ../documents
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# :8019

# 8. Training
cd ../training
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# :8020
```

**Verify все сервисы:**
```bash
# Проверить Service Registry в Orchestrator
curl http://localhost:8002/services

# Должны видеть все зарегистрированные сервисы с status "healthy"
```

### Phase 6: Intelligence Layer (День 8-10)

```bash
# 1. Knowledge Graph Service
cd services/knowledge_graph
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &

# Test query
curl http://localhost:8000/api/knowledge-graph/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "MATCH (c:Clause {id: \"8.2.2\"}) RETURN c"
  }'

# 2. Case Library Service
cd ../case_library
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &

# Verify case collector subscribing to events
# Должны видеть в логах: "Subscribed to workflow events"

# 3. ML Predictor (initial training - нет данных пока)
cd ../ml_predictor
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &

# 4. AI Experts
cd ../../ai_experts/bcm_advisor
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &

cd ../compliance_auditor
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &

cd ../strategic_advisor
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
```

**Test AI Expert:**
```bash
# Test BIA Advisor
curl -X POST http://localhost:8000/api/ai/bia/bia_123/advice \
  -H "Content-Type: application/json"

# Должен вернуть advice (возможно с placeholder данными если BIA пустой)
```

### Phase 7: Frontend (День 11-12)

```bash
cd frontend/bcm-platform

# Install dependencies
npm install

# Start development server
npm run dev

# Открыть http://localhost:3000
```

**Verify integration:**
1. Зарегистрировать пользователя
2. Создать организацию
3. Начать BIA
4. Добавить процесс
5. Проверить что AI Advisor показывает advice

### Phase 8: MCP Interface (День 13-14)

```bash
cd interfaces/mcp

# Install MCP SDK
pip install mcp

# Start MCP server
python mcp_server.py

# Подключить к Claude Desktop:
# ~/.claude/config.json:
{
  "mcpServers": {
    "bcm-platform": {
      "command": "python",
      "args": ["/path/to/mcp_server.py"]
    }
  }
}
```

**Test в Claude Desktop:**
```
User: "Recommend RTO for Emergency Department in my hospital"
Claude: [использует bcm-platform MCP tool]
```

---

## 9. СТАНДАРТЫ КОДА

### 9.1 Service Template

**Каждый сервис следует единой структуре:**

```python
# services/{service_name}/main.py

from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from shared.database import get_db
from shared.eventbus import EventBusClient
from shared.orchestrator import OrchestratorClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await orchestrator.register_service(
        name=SERVICE_NAME,
        port=SERVICE_PORT,
        health_check_url="/health"
    )
    
    await eventbus.subscribe(
        service=SERVICE_NAME,
        topics=get_subscribed_topics()
    )
    
    yield
    
    # Shutdown
    await orchestrator.unregister_service(SERVICE_NAME)
    await eventbus.unsubscribe(SERVICE_NAME)

app = FastAPI(
    title=f"{SERVICE_NAME} Service",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": "1.0.0"
    }

@app.get("/ready")
async def ready():
    # Check dependencies
    db_ok = await check_database()
    eventbus_ok = await check_eventbus()
    
    return {
        "ready": db_ok and eventbus_ok,
        "checks": {
            "database": db_ok,
            "eventbus": eventbus_ok
        }
    }

# Include routers
from api.routes import router
app.include_router(router, prefix=f"/{SERVICE_NAME}")
```

### 9.2 Domain Models (Pydantic)

```python
# services/{service_name}/models/domain.py

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ProcessTier(str, Enum):
    TIER_1 = "tier_1"  # Critical
    TIER_2 = "tier_2"  # Important
    TIER_3 = "tier_3"  # Normal
    TIER_4 = "tier_4"  # Low priority

class BusinessProcess(BaseModel):
    id: Optional[str] = None
    org_id: str = Field(..., description="Organization ID")
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    owner: str = Field(..., description="Process owner")
    tier: ProcessTier
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "org_id": "org_123",
                "name": "Emergency Department",
                "description": "24/7 emergency care services",
                "owner": "Dr. John Smith",
                "tier": "tier_1"
            }
        }
```

### 9.3 Database Models (SQLAlchemy)

```python
# services/{service_name}/models/database.py

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from shared.database.base import Base, TenantMixin, TimestampMixin
import uuid
from datetime import datetime

class BusinessProcessDB(Base, TenantMixin, TimestampMixin):
    __tablename__ = "business_processes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(String)
    owner = Column(String(255), nullable=False)
    tier = Column(
        Enum('tier_1', 'tier_2', 'tier_3', 'tier_4', name='process_tier'),
        nullable=False
    )
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_process_org_tier', 'org_id', 'tier'),
    )
```

### 9.4 Repository Pattern

```python
# services/{service_name}/repositories/repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from models.database import BusinessProcessDB
from models.domain import BusinessProcess

class BIARepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_process(
        self,
        process: BusinessProcess
    ) -> str:
        """Create new business process"""
        db_process = BusinessProcessDB(
            **process.dict(exclude={'id', 'created_at', 'updated_at'})
        )
        self.session.add(db_process)
        await self.session.commit()
        await self.session.refresh(db_process)
        return str(db_process.id)
    
    async def get_process(
        self,
        process_id: str
    ) -> Optional[BusinessProcess]:
        """Get process by ID"""
        result = await self.session.execute(
            select(BusinessProcessDB)
            .where(BusinessProcessDB.id == process_id)
        )
        db_process = result.scalar_one_or_none()
        
        if not db_process:
            return None
        
        return BusinessProcess.from_orm(db_process)
    
    async def list_processes(
        self,
        org_id: str,
        tier: Optional[str] = None
    ) -> List[BusinessProcess]:
        """List all processes for organization"""
        query = select(BusinessProcessDB).where(
            BusinessProcessDB.org_id == org_id
        )
        
        if tier:
            query = query.where(BusinessProcessDB.tier == tier)
        
        result = await self.session.execute(query)
        db_processes = result.scalars().all()
        
        return [BusinessProcess.from_orm(p) for p in db_processes]
```

### 9.5 Service Layer

```python
# services/{service_name}/services/business_logic.py

from repositories.repository import BIARepository
from shared.eventbus import EventBusClient
from datetime import datetime

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
        process: ProcessCreate
    ) -> str:
        """Business logic for adding process"""
        
        # Validation
        if not process.name:
            raise ValueError("Process name required")
        
        # Check duplicates
        existing = await self.repo.find_by_name(
            bia_id, process.name
        )
        if existing:
            raise ValueError(f"Process '{process.name}' already exists")
        
        # Save
        process_id = await self.repo.create_process(bia_id, process)
        
        # Publish event
        await self.eventbus.publish("bia.process.added", {
            "bia_id": bia_id,
            "process_id": process_id,
            "process_data": process.dict(),
            "timestamp": datetime.now().isoformat()
        })
        
        return process_id
```

### 9.6 API Routes

```python
# services/{service_name}/api/routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models.domain import BusinessProcess, ProcessCreate
from services.business_logic import BIAService
from shared.auth import get_current_user

router = APIRouter()

@router.post(
    "/processes",
    response_model=dict,
    status_code=status.HTTP_201_CREATED
)
async def create_process(
    bia_id: str,
    process: ProcessCreate,
    service: BIAService = Depends(get_bia_service),
    user = Depends(get_current_user)
):
    """
    Create new business process
    
    - **bia_id**: BIA session ID
    - **process**: Process data
    
    Returns process ID
    """
    try:
        process_id = await service.add_process(bia_id, process)
        return {
            "process_id": process_id,
            "message": "Process created successfully"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/processes",
    response_model=List[BusinessProcess]
)
async def list_processes(
    bia_id: str,
    tier: Optional[str] = None,
    service: BIAService = Depends(get_bia_service),
    user = Depends(get_current_user)
):
    """
    List all processes for BIA
    
    - **bia_id**: BIA session ID
    - **tier**: Optional filter by tier
    """
    processes = await service.list_processes(bia_id, tier)
    return processes
```

### 9.7 Event Publishing

```python
# services/{service_name}/events/publishers.py

from shared.eventbus import EventBusClient
from typing import Any, Dict

class BIAEventPublisher:
    def __init__(self, eventbus: EventBusClient):
        self.eventbus = eventbus
    
    async def publish_process_added(
        self,
        bia_id: str,
        process_id: str,
        process_data: Dict[str, Any]
    ):
        """Publish process added event"""
        await self.eventbus.publish(
            topic="bia.process.added",
            data={
                "bia_id": bia_id,
                "process_id": process_id,
                "process": process_data,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    async def publish_workflow_action(
        self,
        org_id: str,
        action: str,
        data: Dict[str, Any]
    ):
        """Publish workflow action for Case Collector"""
        await self.eventbus.publish(
            topic="bia.workflow.action.taken",
            data={
                "org_id": org_id,
                "module": "bia",
                "action": action,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
        )
```

### 9.8 Event Subscribing

```python
# services/{service_name}/events/subscribers.py

from shared.eventbus import EventBusClient, Event
from services.business_logic import BIAService

class BIAEventSubscriber:
    def __init__(
        self,
        eventbus: EventBusClient,
        service: BIAService
    ):
        self.eventbus = eventbus
        self.service = service
    
    async def start(self):
        """Start subscribing to events"""
        await self.eventbus.subscribe(
            topics=["governance.organization.created"],
            handler=self.handle_event
        )
    
    async def handle_event(self, event: Event):
        """Route event to appropriate handler"""
        if event.topic == "governance.organization.created":
            await self.on_organization_created(event)
    
    async def on_organization_created(self, event: Event):
        """Auto-create BIA template for new organization"""
        org_id = event.data["org_id"]
        industry = event.data["industry"]
        
        # Create BIA
        bia_id = await self.service.start_bia(org_id)
        
        # Add suggested processes
        suggested = get_default_processes_for_industry(industry)
        for process in suggested:
            await self.service.add_process(bia_id, process)
```

---

## 10. INTEGRATION PATTERNS

### 10.1 Synchronous (REST)

**Use case**: Immediate response needed

```typescript
// Frontend
const response = await fetch('/api/organizations', {
  method: 'POST',
  body: JSON.stringify(orgData)
});
const org = await response.json();
```

```python
# API Gateway proxies to service
@gateway.post("/api/organizations")
async def create_organization(org_data: dict):
    response = await httpx.post(
        f"{GOVERNANCE_URL}/organizations",
        json=org_data
    )
    return response.json()
```

### 10.2 Asynchronous (Events)

**Use case**: Multiple services need to react

```python
# Service A publishes
await eventbus.publish("bia.completed", {
    "org_id": "org_123",
    "bia_id": "bia_456",
    "critical_processes": [...]
})

# Service B subscribes
@eventbus.subscribe("bia.completed")
async def on_bia_completed(event):
    # Auto-start risk assessment
    await risk_service.create_assessment(event.data)

# Service C also subscribes
@eventbus.subscribe("bia.completed")
async def on_bia_completed(event):
    # Check ISO compliance
    await compliance_service.check_clause(event.data, "8.2.2")
```

### 10.3 Orchestrated (Workflow)

**Use case**: Multi-step business process

```python
@workflow.defn
class BIAProcessWorkflow:
    @workflow.run
    async def run(self, org_id: str):
        # Step 1
        await workflow.execute_activity(
            identify_processes,
            args=[org_id],
            timeout=timedelta(days=7)
        )
        
        # Step 2
        await workflow.execute_activity(
            analyze_dependencies,
            args=[org_id],
            timeout=timedelta(days=7)
        )
        
        # ... etc
```

---

## 11. ПРИМЕРЫ КОДА

### Complete BIA Workflow Example

```python
# User starts BIA → adds process → AI analyzes → completes BIA

# 1. User starts BIA
POST /api/bia/start
{
  "org_id": "hospital_001"
}

Response: {"bia_id": "bia_123", "status": "started"}

# BIA Service публикует:
eventbus.publish("bia.workflow.started", {...})

# 2. User adds process
POST /api/bia/bia_123/processes
{
  "name": "Emergency Department",
  "description": "24/7 emergency care",
  "owner": "Dr. Smith",
  "tier": "tier_1"
}

Response: {"process_id": "proc_456"}

# BIA Service:
- Saves process to DB
- Publishes "bia.process.added"
- Case Collector records action

# 3. User requests AI to analyze impact
POST /api/ai/bia/bia_123/analyze-impact
{
  "process_id": "proc_456"
}

# AI Expert:
- Gets workflow context (from BIA Service)
- Gets similar cases (from Case Library)
- Gets ISO guidance (from Knowledge Graph)
- LLM analyzes
- Returns impact assessment

Response: {
  "financial_impact": {...},
  "operational_impact": {...},
  "recommended_tier": "tier_1"
}

# 4. User determines RTO (AI assisted)
POST /api/ai/bia/bia_123/recommend-rto
{
  "process_id": "proc_456"
}

# AI Expert:
- Analyzes process criticality
- Checks industry benchmarks
- References similar successful cases
- Recommends RTO

Response: {
  "rto_hours": 0,
  "rationale": "Tier 1 critical, immediate availability required",
  "alternatives": [{rto: 1, risk: "high"}]
}

# 5. User completes BIA
POST /api/bia/bia_123/complete

# BIA Service:
- Validates all requirements met
- Updates workflow state to "completed"
- Publishes "bia.workflow.completed"

# EventBus broadcasts to:
- Risk Service → auto-creates risk assessments
- Planning Service → prepares strategy options
- Compliance Service → checks ISO 8.2.2 compliance
- Case Collector → compiles into workflow case
```

---

## 12. DEPLOYMENT CHECKLIST

### Development
- [ ] PostgreSQL running
- [ ] Redis running
- [ ] Neo4j running with data
- [ ] MinIO running
- [ ] All services started
- [ ] Frontend running
- [ ] Can create organization
- [ ] Can start BIA
- [ ] AI Advisor responds

### Staging
- [ ] Docker Compose deployed
- [ ] Environment variables set
- [ ] Database migrations applied
- [ ] Knowledge Graph populated
- [ ] SSL certificates configured
- [ ] Monitoring setup (Prometheus/Grafana)
- [ ] Load testing passed
- [ ] Backup strategy configured

### Production
- [ ] Kubernetes cluster ready
- [ ] Secrets managed (Vault/AWS Secrets Manager)
- [ ] Auto-scaling configured
- [ ] CDN for frontend
- [ ] Database replicas
- [ ] Disaster recovery plan
- [ ] Monitoring alerts configured
- [ ] Log aggregation (ELK)
- [ ] Performance baselines established

---

## 13. TROUBLESHOOTING

### Service не запускается
```bash
# Check logs
docker-compose logs -f service_name

# Check dependencies
curl http://localhost:5432  # PostgreSQL
redis-cli ping              # Redis
curl http://localhost:7474  # Neo4j

# Check EventBus
curl http://localhost:8001/health
```

### Events не доходят
```bash
# Check EventBus logs
docker-compose logs -f eventbus

# Manually publish test event
curl -X POST http://localhost:8001/publish \
  -H "Content-Type: application/json" \
  -d '{"topic": "test", "data": {}}'

# Check subscriber
# В логах сервиса должно быть: "Subscribed to topics: [...]"
```

### AI Advisor не отвечает
```bash
# Check AI Expert service
curl http://localhost:8000/api/ai/health

# Check LLM API keys
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY

# Test direct LLM call
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model": "claude-sonnet-4", "messages": [{"role": "user", "content": "test"}]}'
```

---

# 🎯 ИТОГО: ПОЛНАЯ АРХИТЕКТУРА

Этот документ описывает:

✅ **5 слоев архитектуры** с четким разделением ответственности  
✅ **Все компоненты** от БД до MCP интерфейса  
✅ **Workflow State Machine** для контекстного AI  
✅ **Case Library** для самообучения платформы  
✅ **Алгоритм запуска снизу вверх** с конкретными командами  
✅ **Стандарты кода** для каждого типа компонента  
✅ **Integration patterns** (sync/async/orchestrated)  
✅ **Примеры кода** для всех ключевых flow  
✅ **Deployment checklist**  
✅ **Troubleshooting guide**

**MCP правильно** - это interface layer (способ доступа), не AI компонент  
**Сборка правильно** - снизу вверх (Data → Platform → Intelligence → Interface)

---
