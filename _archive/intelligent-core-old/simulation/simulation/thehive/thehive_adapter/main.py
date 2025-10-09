"""
TheHive Adapter Service - Security Incident & Case Management
ISO 22301 BCM Platform TheHive Integration
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import asyncio
import json
import os
import httpx
import uuid
from contextlib import asynccontextmanager
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
EVENTBUS_URL = os.getenv("EVENTBUS_URL", "http://localhost:8001")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8081,http://localhost:8069").split(",")

# TheHive Models
class TheHiveConfig(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=255)
    base_url: HttpUrl
    api_key: str = Field(..., min_length=1)
    tenant_id: str = Field(..., min_length=1)
    is_active: bool = Field(default=True)
    organization: Optional[str] = None
    settings: Dict[str, Any] = Field(default={})

class Case(BaseModel):
    id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=500)
    description: str
    severity: int = Field(ge=1, le=4)  # 1=Low, 2=Medium, 3=High, 4=Critical
    tlp: int = Field(ge=0, le=3, default=2)  # Traffic Light Protocol
    pap: int = Field(ge=0, le=3, default=2)  # Permissible Actions Protocol
    status: str = Field(default="Open")  # Open, Resolved, Deleted
    tags: List[str] = Field(default=[])
    assignee: Optional[str] = None
    owner: Optional[str] = None
    thehive_case_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

class Observable(BaseModel):
    id: Optional[str] = None
    case_id: str
    data_type: str  # ip, domain, file, url, etc.
    data: str
    message: Optional[str] = None
    tlp: int = Field(ge=0, le=3, default=2)
    ioc: bool = Field(default=False)
    sighted: bool = Field(default=False)
    tags: List[str] = Field(default=[])
    thehive_observable_id: Optional[str] = None

class Task(BaseModel):
    id: Optional[str] = None
    case_id: str
    title: str
    description: Optional[str] = None
    status: str = Field(default="Waiting")  # Waiting, InProgress, Completed, Cancel
    assignee: Optional[str] = None
    owner: Optional[str] = None
    order: int = Field(default=0)
    category: Optional[str] = None
    thehive_task_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Alert(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    severity: int = Field(ge=1, le=4)
    tlp: int = Field(ge=0, le=3, default=2)
    pap: int = Field(ge=0, le=3, default=2)
    type: str
    source: str
    source_ref: Optional[str] = None
    status: str = Field(default="New")  # New, Updated, Ignored, Imported
    tags: List[str] = Field(default=[])
    artifacts: List[Dict[str, Any]] = Field(default=[])
    thehive_alert_id: Optional[str] = None
    created_at: Optional[datetime] = None

# TheHive Adapter
class TheHiveAdapter:
    def __init__(self, config: TheHiveConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
        )
        self.base_url = str(config.base_url).rstrip('/')
    
    async def test_connection(self) -> bool:
        """Test connection to TheHive instance"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/status")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"TheHive connection test failed: {e}")
            return False
    
    async def create_case(self, case: Case) -> Case:
        """Create a new case in TheHive"""
        try:
            case_data = {
                "title": case.title,
                "description": case.description,
                "severity": case.severity,
                "tlp": case.tlp,
                "pap": case.pap,
                "tags": case.tags,
                "owner": case.owner or case.assignee
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/case",
                json=case_data
            )
            
            if response.status_code == 201:
                created_case = response.json()
                case.thehive_case_id = created_case.get("_id")
                case.id = str(uuid.uuid4())
                case.created_at = datetime.utcnow()
                case.status = created_case.get("status", "Open")
                
                logger.info(f"Created case {case.id} in TheHive: {case.thehive_case_id}")
                return case
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to create case")
                
        except Exception as e:
            logger.error(f"Failed to create TheHive case: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_case(self, case_id: str) -> Case:
        """Get case by TheHive case ID"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/case/{case_id}")
            
            if response.status_code == 200:
                case_data = response.json()
                case = Case(
                    id=str(uuid.uuid4()),
                    title=case_data.get("title"),
                    description=case_data.get("description"),
                    severity=case_data.get("severity", 2),
                    tlp=case_data.get("tlp", 2),
                    pap=case_data.get("pap", 2),
                    status=case_data.get("status"),
                    tags=case_data.get("tags", []),
                    owner=case_data.get("owner"),
                    thehive_case_id=case_data.get("_id"),
                    created_at=datetime.fromtimestamp(case_data.get("createdAt", 0) / 1000),
                    updated_at=datetime.fromtimestamp(case_data.get("updatedAt", 0) / 1000)
                )
                return case
            else:
                raise HTTPException(status_code=response.status_code, detail="Case not found")
                
        except Exception as e:
            logger.error(f"Failed to get TheHive case: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_cases(self, limit: int = 50, status: Optional[str] = None) -> List[Case]:
        """Get all cases from TheHive"""
        try:
            query = {"range": f"0-{limit}"}
            if status:
                query["filter"] = f"status:{status}"
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/query",
                json={
                    "query": [
                        {"_name": "listCase"},
                        {"_name": "sort", "_fields": [{"updatedAt": "desc"}]},
                        {"_name": "page", "from": 0, "to": limit}
                    ]
                }
            )
            
            if response.status_code == 200:
                cases_data = response.json()
                cases = []
                
                for case_data in cases_data:
                    case = Case(
                        id=str(uuid.uuid4()),
                        title=case_data.get("title"),
                        description=case_data.get("description"),
                        severity=case_data.get("severity", 2),
                        tlp=case_data.get("tlp", 2),
                        pap=case_data.get("pap", 2),
                        status=case_data.get("status"),
                        tags=case_data.get("tags", []),
                        owner=case_data.get("owner"),
                        thehive_case_id=case_data.get("_id"),
                        created_at=datetime.fromtimestamp(case_data.get("createdAt", 0) / 1000),
                        updated_at=datetime.fromtimestamp(case_data.get("updatedAt", 0) / 1000)
                    )
                    cases.append(case)
                
                return cases
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to get cases")
                
        except Exception as e:
            logger.error(f"Failed to get TheHive cases: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def update_case(self, case_id: str, updates: Dict[str, Any]) -> Case:
        """Update case in TheHive"""
        try:
            response = await self.client.patch(
                f"{self.base_url}/api/v1/case/{case_id}",
                json=updates
            )
            
            if response.status_code == 200:
                return await self.get_case(case_id)
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to update case")
                
        except Exception as e:
            logger.error(f"Failed to update TheHive case: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def create_alert(self, alert: Alert) -> Alert:
        """Create alert in TheHive"""
        try:
            alert_data = {
                "title": alert.title,
                "description": alert.description,
                "severity": alert.severity,
                "tlp": alert.tlp,
                "pap": alert.pap,
                "type": alert.type,
                "source": alert.source,
                "sourceRef": alert.source_ref or str(uuid.uuid4()),
                "tags": alert.tags,
                "artifacts": alert.artifacts
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/alert",
                json=alert_data
            )
            
            if response.status_code == 201:
                created_alert = response.json()
                alert.thehive_alert_id = created_alert.get("_id")
                alert.id = str(uuid.uuid4())
                alert.created_at = datetime.utcnow()
                alert.status = created_alert.get("status", "New")
                
                logger.info(f"Created alert {alert.id} in TheHive: {alert.thehive_alert_id}")
                return alert
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to create alert")
                
        except Exception as e:
            logger.error(f"Failed to create TheHive alert: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_alerts(self, limit: int = 50, status: Optional[str] = None) -> List[Alert]:
        """Get alerts from TheHive"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/query",
                json={
                    "query": [
                        {"_name": "listAlert"},
                        {"_name": "sort", "_fields": [{"date": "desc"}]},
                        {"_name": "page", "from": 0, "to": limit}
                    ]
                }
            )
            
            if response.status_code == 200:
                alerts_data = response.json()
                alerts = []
                
                for alert_data in alerts_data:
                    alert = Alert(
                        id=str(uuid.uuid4()),
                        title=alert_data.get("title"),
                        description=alert_data.get("description"),
                        severity=alert_data.get("severity", 2),
                        tlp=alert_data.get("tlp", 2),
                        pap=alert_data.get("pap", 2),
                        type=alert_data.get("type"),
                        source=alert_data.get("source"),
                        source_ref=alert_data.get("sourceRef"),
                        status=alert_data.get("status"),
                        tags=alert_data.get("tags", []),
                        artifacts=alert_data.get("artifacts", []),
                        thehive_alert_id=alert_data.get("_id"),
                        created_at=datetime.fromtimestamp(alert_data.get("date", 0) / 1000)
                    )
                    alerts.append(alert)
                
                return alerts
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to get alerts")
                
        except Exception as e:
            logger.error(f"Failed to get TheHive alerts: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def create_case_from_alert(self, alert_id: str) -> Case:
        """Convert alert to case"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/alert/{alert_id}/createCase"
            )
            
            if response.status_code == 201:
                case_data = response.json()
                case = Case(
                    id=str(uuid.uuid4()),
                    title=case_data.get("title"),
                    description=case_data.get("description"),
                    severity=case_data.get("severity", 2),
                    tlp=case_data.get("tlp", 2),
                    pap=case_data.get("pap", 2),
                    status=case_data.get("status"),
                    tags=case_data.get("tags", []),
                    owner=case_data.get("owner"),
                    thehive_case_id=case_data.get("_id"),
                    created_at=datetime.fromtimestamp(case_data.get("createdAt", 0) / 1000)
                )
                return case
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to create case from alert")
                
        except Exception as e:
            logger.error(f"Failed to create case from alert: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def add_task_to_case(self, case_id: str, task: Task) -> Task:
        """Add task to case"""
        try:
            task_data = {
                "title": task.title,
                "description": task.description,
                "owner": task.owner or task.assignee,
                "status": task.status,
                "order": task.order
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/case/{case_id}/task",
                json=task_data
            )
            
            if response.status_code == 201:
                created_task = response.json()
                task.thehive_task_id = created_task.get("_id")
                task.id = str(uuid.uuid4())
                task.created_at = datetime.utcnow()
                task.status = created_task.get("status", "Waiting")
                
                return task
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to create task")
                
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# TheHive Manager
class TheHiveManager:
    def __init__(self):
        self.configs: Dict[str, TheHiveConfig] = {}
        self.adapters: Dict[str, TheHiveAdapter] = {}
    
    async def add_config(self, config: TheHiveConfig) -> str:
        config_id = config.id or str(uuid.uuid4())
        config.id = config_id
        
        # Create adapter and test connection
        adapter = TheHiveAdapter(config)
        if not await adapter.test_connection():
            raise HTTPException(status_code=400, detail="TheHive connection failed")
        
        self.configs[config_id] = config
        self.adapters[config_id] = adapter
        
        logger.info(f"Added TheHive config {config_id}: {config.name}")
        return config_id
    
    async def get_adapter(self, config_id: str) -> TheHiveAdapter:
        if config_id not in self.adapters:
            raise HTTPException(status_code=404, detail="TheHive configuration not found")
        return self.adapters[config_id]
    
    async def publish_event(self, event_type: str, tenant_id: str, data: Dict[str, Any]):
        """Publish event to EventBus"""
        try:
            async with httpx.AsyncClient() as client:
                await client.post(f"{EVENTBUS_URL}/api/events/publish", json={
                    "event_type": event_type,
                    "tenant_id": tenant_id,
                    "data": data
                })
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")

# Global TheHive manager
thehive_manager = TheHiveManager()

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting TheHive Adapter Service...")
    yield
    logger.info("Shutting down TheHive Adapter Service...")

# Create FastAPI app
app = FastAPI(
    title="BCM TheHive Adapter Service",
    description="TheHive integration for ISO 22301 BCM Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "thehive_adapter"}

# Configuration Management
@app.post("/api/thehive/configs")
async def add_thehive_config(config: TheHiveConfig):
    config_id = await thehive_manager.add_config(config)
    return {"config_id": config_id, "status": "configured"}

@app.get("/api/thehive/configs")
async def get_thehive_configs(tenant_id: str):
    configs = [
        config for config in thehive_manager.configs.values()
        if config.tenant_id == tenant_id
    ]
    return {"configs": configs}

# Case Management
@app.post("/api/thehive/{config_id}/cases")
async def create_case(config_id: str, case: Case, tenant_id: str):
    adapter = await thehive_manager.get_adapter(config_id)
    created_case = await adapter.create_case(case)
    
    # Publish event
    await thehive_manager.publish_event("thehive.case.created", tenant_id, {
        "config_id": config_id,
        "case_id": created_case.id,
        "thehive_case_id": created_case.thehive_case_id,
        "title": created_case.title,
        "severity": created_case.severity
    })
    
    return {"case": created_case}

@app.get("/api/thehive/{config_id}/cases")
async def get_cases(config_id: str, limit: int = 50, status: Optional[str] = None):
    adapter = await thehive_manager.get_adapter(config_id)
    cases = await adapter.get_cases(limit, status)
    return {"cases": cases}

@app.get("/api/thehive/{config_id}/cases/{case_id}")
async def get_case(config_id: str, case_id: str):
    adapter = await thehive_manager.get_adapter(config_id)
    case = await adapter.get_case(case_id)
    return {"case": case}

@app.patch("/api/thehive/{config_id}/cases/{case_id}")
async def update_case(config_id: str, case_id: str, updates: Dict[str, Any], tenant_id: str):
    adapter = await thehive_manager.get_adapter(config_id)
    updated_case = await adapter.update_case(case_id, updates)
    
    # Publish event
    await thehive_manager.publish_event("thehive.case.updated", tenant_id, {
        "config_id": config_id,
        "case_id": case_id,
        "updates": updates
    })
    
    return {"case": updated_case}

# Alert Management
@app.post("/api/thehive/{config_id}/alerts")
async def create_alert(config_id: str, alert: Alert, tenant_id: str):
    adapter = await thehive_manager.get_adapter(config_id)
    created_alert = await adapter.create_alert(alert)
    
    # Publish event
    await thehive_manager.publish_event("thehive.alert.created", tenant_id, {
        "config_id": config_id,
        "alert_id": created_alert.id,
        "thehive_alert_id": created_alert.thehive_alert_id,
        "title": created_alert.title,
        "severity": created_alert.severity
    })
    
    return {"alert": created_alert}

@app.get("/api/thehive/{config_id}/alerts")
async def get_alerts(config_id: str, limit: int = 50, status: Optional[str] = None):
    adapter = await thehive_manager.get_adapter(config_id)
    alerts = await adapter.get_alerts(limit, status)
    return {"alerts": alerts}

@app.post("/api/thehive/{config_id}/alerts/{alert_id}/promote")
async def promote_alert_to_case(config_id: str, alert_id: str, tenant_id: str):
    adapter = await thehive_manager.get_adapter(config_id)
    case = await adapter.create_case_from_alert(alert_id)
    
    # Publish event
    await thehive_manager.publish_event("thehive.alert.promoted", tenant_id, {
        "config_id": config_id,
        "alert_id": alert_id,
        "case_id": case.id,
        "thehive_case_id": case.thehive_case_id
    })
    
    return {"case": case}

# Task Management
@app.post("/api/thehive/{config_id}/cases/{case_id}/tasks")
async def add_task_to_case(config_id: str, case_id: str, task: Task, tenant_id: str):
    adapter = await thehive_manager.get_adapter(config_id)
    task.case_id = case_id
    created_task = await adapter.add_task_to_case(case_id, task)
    
    # Publish event
    await thehive_manager.publish_event("thehive.task.created", tenant_id, {
        "config_id": config_id,
        "case_id": case_id,
        "task_id": created_task.id,
        "thehive_task_id": created_task.thehive_task_id,
        "title": created_task.title
    })
    
    return {"task": created_task}

# BCM-specific incident workflows
@app.post("/api/thehive/{config_id}/bcm/incident")
async def create_bcm_incident(
    config_id: str,
    tenant_id: str,
    incident_data: Dict[str, Any]
):
    """Create BCM incident case with predefined workflow"""
    adapter = await thehive_manager.get_adapter(config_id)
    
    # Create case for BCM incident
    case = Case(
        title=f"BCM Incident: {incident_data.get('title', 'Unknown')}",
        description=incident_data.get('description', ''),
        severity=incident_data.get('severity', 3),
        tags=["BCM", "Business-Continuity", incident_data.get('type', 'general')],
        owner=incident_data.get('incident_manager')
    )
    
    created_case = await adapter.create_case(case)
    
    # Add standard BCM tasks
    bcm_tasks = [
        {"title": "Initial Assessment", "order": 1},
        {"title": "Impact Analysis", "order": 2},
        {"title": "Activate Recovery Team", "order": 3},
        {"title": "Execute Recovery Plan", "order": 4},
        {"title": "Monitor Recovery Progress", "order": 5},
        {"title": "Post-Incident Review", "order": 6}
    ]
    
    for task_data in bcm_tasks:
        task = Task(
            case_id=created_case.thehive_case_id,
            title=task_data["title"],
            description=f"BCM workflow task: {task_data['title']}",
            order=task_data["order"],
            category="BCM"
        )
        await adapter.add_task_to_case(created_case.thehive_case_id, task)
    
    # Publish event
    await thehive_manager.publish_event("thehive.bcm.incident.created", tenant_id, {
        "config_id": config_id,
        "case_id": created_case.id,
        "thehive_case_id": created_case.thehive_case_id,
        "incident_data": incident_data
    })
    
    return {"case": created_case, "status": "BCM incident workflow initiated"}

# Mock Data Endpoints for Testing
from mock_data import get_mock_thehive_configs, get_mock_cases, get_mock_alerts, get_mock_observables, get_mock_tasks, get_mock_case_templates, get_mock_incident_metrics

@app.get("/api/thehive/mock/configs")
async def get_mock_thehive_config_data():
    """Get mock TheHive configuration data for testing"""
    return {"mock_configs": get_mock_thehive_configs()}

@app.get("/api/thehive/mock/cases")
async def get_mock_case_data():
    """Get mock case data for testing"""
    return {"mock_cases": get_mock_cases()}

@app.get("/api/thehive/mock/alerts")
async def get_mock_alert_data():
    """Get mock alert data for testing"""
    return {"mock_alerts": get_mock_alerts()}

@app.get("/api/thehive/mock/observables")
async def get_mock_observable_data():
    """Get mock observable data for testing"""
    return {"mock_observables": get_mock_observables()}

@app.get("/api/thehive/mock/tasks")
async def get_mock_task_data():
    """Get mock task data for testing"""
    return {"mock_tasks": get_mock_tasks()}

@app.get("/api/thehive/mock/templates")
async def get_mock_template_data():
    """Get mock case templates for BCM incidents"""
    return {"case_templates": get_mock_case_templates()}

@app.get("/api/thehive/mock/metrics")
async def get_mock_metrics_data():
    """Get mock incident metrics and KPIs"""
    return {"incident_metrics": get_mock_incident_metrics()}

@app.post("/api/thehive/mock/setup-demo-config")
async def setup_demo_thehive_config(tenant_id: str):
    """Setup demo TheHive configuration for testing"""
    mock_configs = get_mock_thehive_configs()
    demo_config = mock_configs[0]
    demo_config["tenant_id"] = tenant_id
    
    from main import TheHiveConfig
    config = TheHiveConfig(**demo_config)
    config_id = await thehive_manager.add_config(config)
    
    return {
        "status": "configured",
        "config_id": config_id,
        "description": "Demo TheHive configuration setup"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)