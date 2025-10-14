"""
TheHive Adapter for Incident Management
Integrates with TheHive SOAR platform for security incident handling
"""

import asyncio
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    FALSE_POSITIVE = "false_positive"


class CaseStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "InProgress"
    RESOLVED = "Resolved"
    DELETED = "Deleted"


class Alert(BaseModel):
    id: str
    title: str
    description: str
    severity: IncidentSeverity
    source: str = "BCM Platform"
    source_ref: Optional[str] = None
    artifacts: List[Dict] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tenant_id: str = "demo"


class Case(BaseModel):
    id: Optional[str] = None
    case_id: Optional[int] = None
    title: str
    description: str
    severity: IncidentSeverity
    status: CaseStatus = CaseStatus.OPEN
    owner: Optional[str] = None
    assignee: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    bcm_context: Dict[str, Any] = Field(default_factory=dict)


class Task(BaseModel):
    id: Optional[str] = None
    case_id: str
    title: str
    description: Optional[str] = None
    status: str = "Waiting"
    owner: Optional[str] = None
    assignee: Optional[str] = None
    group: str = "BCM"
    flag: bool = False
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None


class Observable(BaseModel):
    data: str
    dataType: str  # ip, domain, url, hash, email, etc.
    message: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    ioc: bool = False
    sighted: bool = False


class TheHiveAdapter:
    """Adapter for integrating with TheHive SOAR platform"""
    
    def __init__(self, config: Dict[str, Any]):
        self.base_url = config.get("thehive_url", "http://localhost:9000")
        self.api_key = config.get("api_key", "")
        self.eventbus_url = config.get("eventbus_url", "http://localhost:8001")
        self.org_name = config.get("org_name", "BCM")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=30.0, headers=self.headers)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.client.aclose()
    
    async def publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish incident events to EventBus"""
        try:
            event = {
                "event_type": event_type,
                "tenant_id": data.get("tenant_id", "demo"),
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "thehive_adapter"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.eventbus_url}/api/events/publish",
                    json=event
                )
                response.raise_for_status()
                logger.info(f"Published event: {event_type}")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
    
    # Alert Management
    async def create_alert(self, alert: Alert) -> Alert:
        """Create an alert in TheHive"""
        try:
            payload = {
                "title": alert.title,
                "description": alert.description,
                "severity": self._map_severity(alert.severity),
                "source": alert.source,
                "sourceRef": alert.source_ref or alert.id,
                "artifacts": alert.artifacts,
                "tags": alert.tags + ["BCM", "ISO22301"],
                "type": "bcm_incident",
                "customFields": {
                    "bcm.tenant_id": {"string": alert.tenant_id},
                    "bcm.incident_type": {"string": "operational"}
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/alert",
                json=payload
            )
            
            if response.status_code == 201:
                result = response.json()
                alert.id = result.get("_id")
                
                # Publish event
                await self.publish_event("bcm.incident.alert_created", {
                    "alert_id": alert.id,
                    "title": alert.title,
                    "severity": alert.severity,
                    "tenant_id": alert.tenant_id
                })
                
            return alert
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            raise
    
    async def promote_alert_to_case(self, alert_id: str) -> Case:
        """Convert alert to case"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/alert/{alert_id}/createCase"
            )
            
            if response.status_code == 201:
                result = response.json()
                case = Case(
                    id=result.get("_id"),
                    case_id=result.get("caseId"),
                    title=result.get("title"),
                    description=result.get("description"),
                    severity=self._reverse_map_severity(result.get("severity", 2)),
                    status=CaseStatus(result.get("status", "Open")),
                    tags=result.get("tags", [])
                )
                
                # Publish event
                await self.publish_event("bcm.incident.case_created", {
                    "case_id": case.id,
                    "case_number": case.case_id,
                    "title": case.title,
                    "severity": case.severity,
                    "tenant_id": "demo"
                })
                
                return case
        except Exception as e:
            logger.error(f"Failed to promote alert: {e}")
            raise
    
    # Case Management
    async def create_case(self, case: Case) -> Case:
        """Create a case directly"""
        try:
            payload = {
                "title": case.title,
                "description": case.description,
                "severity": self._map_severity(case.severity),
                "status": case.status.value,
                "tags": case.tags + ["BCM", "ISO22301"],
                "metrics": case.metrics,
                "customFields": {
                    "bcm.tenant_id": {"string": "demo"},
                    "bcm.process_affected": {"string": case.bcm_context.get("process", "")},
                    "bcm.recovery_time": {"number": case.bcm_context.get("rto", 4)}
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/case",
                json=payload
            )
            
            if response.status_code == 201:
                result = response.json()
                case.id = result.get("_id")
                case.case_id = result.get("caseId")
                
                # Publish event
                await self.publish_event("bcm.incident.case_created", {
                    "case_id": case.id,
                    "case_number": case.case_id,
                    "title": case.title,
                    "severity": case.severity,
                    "tenant_id": "demo"
                })
                
                # Auto-create initial tasks
                await self._create_bcm_tasks(case.id)
                
            return case
        except Exception as e:
            logger.error(f"Failed to create case: {e}")
            raise
    
    async def get_cases(self, status: Optional[CaseStatus] = None, 
                       severity: Optional[IncidentSeverity] = None) -> List[Case]:
        """Get cases with optional filters"""
        try:
            # Mock data for demonstration
            cases = [
                Case(
                    id="case_001",
                    case_id=101,
                    title="Data Center Power Outage",
                    description="Primary data center lost power",
                    severity=IncidentSeverity.CRITICAL,
                    status=CaseStatus.IN_PROGRESS,
                    tags=["infrastructure", "critical_process"],
                    bcm_context={
                        "process": "IT Services",
                        "rto": 2,
                        "impact": "high"
                    }
                ),
                Case(
                    id="case_002",
                    case_id=102,
                    title="Supply Chain Disruption",
                    description="Key supplier unable to deliver",
                    severity=IncidentSeverity.HIGH,
                    status=CaseStatus.OPEN,
                    tags=["supply_chain", "vendor"],
                    bcm_context={
                        "process": "Manufacturing",
                        "rto": 8,
                        "impact": "medium"
                    }
                ),
                Case(
                    id="case_003",
                    case_id=103,
                    title="Ransomware Attack Detected",
                    description="Ransomware detected on file servers",
                    severity=IncidentSeverity.CRITICAL,
                    status=CaseStatus.IN_PROGRESS,
                    tags=["security", "ransomware"],
                    bcm_context={
                        "process": "All",
                        "rto": 1,
                        "impact": "critical"
                    }
                )
            ]
            
            if status:
                cases = [c for c in cases if c.status == status]
            if severity:
                cases = [c for c in cases if c.severity == severity]
            
            return cases
        except Exception as e:
            logger.error(f"Failed to get cases: {e}")
            return []
    
    async def update_case(self, case_id: str, updates: Dict[str, Any]) -> Case:
        """Update case details"""
        try:
            response = await self.client.patch(
                f"{self.base_url}/api/case/{case_id}",
                json=updates
            )
            
            if response.status_code == 200:
                # Publish event
                await self.publish_event("bcm.incident.case_updated", {
                    "case_id": case_id,
                    "updates": updates,
                    "tenant_id": "demo"
                })
            
            return Case(id=case_id, **updates)
        except Exception as e:
            logger.error(f"Failed to update case: {e}")
            raise
    
    # Task Management
    async def create_task(self, task: Task) -> Task:
        """Create a task in a case"""
        try:
            payload = {
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "group": task.group,
                "flag": task.flag
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/case/{task.case_id}/task",
                json=payload
            )
            
            if response.status_code == 201:
                result = response.json()
                task.id = result.get("_id")
                
                # Publish event
                await self.publish_event("bcm.incident.task_created", {
                    "task_id": task.id,
                    "case_id": task.case_id,
                    "title": task.title,
                    "tenant_id": "demo"
                })
            
            return task
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise
    
    async def _create_bcm_tasks(self, case_id: str):
        """Auto-create BCM-specific tasks for a case"""
        bcm_tasks = [
            Task(
                case_id=case_id,
                title="Activate Crisis Management Team",
                description="Notify and assemble CMT members",
                group="BCM"
            ),
            Task(
                case_id=case_id,
                title="Assess Business Impact",
                description="Evaluate impact on critical processes",
                group="BCM"
            ),
            Task(
                case_id=case_id,
                title="Implement Recovery Strategy",
                description="Execute appropriate recovery procedures",
                group="BCM"
            ),
            Task(
                case_id=case_id,
                title="Stakeholder Communication",
                description="Update internal and external stakeholders",
                group="BCM"
            )
        ]
        
        for task in bcm_tasks:
            await self.create_task(task)
    
    # Observable Management
    async def add_observable(self, case_id: str, observable: Observable) -> Observable:
        """Add observable to case"""
        try:
            payload = {
                "data": observable.data,
                "dataType": observable.dataType,
                "message": observable.message,
                "tags": observable.tags,
                "ioc": observable.ioc,
                "sighted": observable.sighted
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/case/{case_id}/observable",
                json=payload
            )
            
            return observable
        except Exception as e:
            logger.error(f"Failed to add observable: {e}")
            raise
    
    # Analytics
    async def get_incident_metrics(self, tenant_id: str = "demo") -> Dict[str, Any]:
        """Get incident metrics for dashboard"""
        try:
            metrics = {
                "total_alerts": 47,
                "active_cases": 8,
                "mttr": 4.2,  # Mean Time To Resolution (hours)
                "severity_breakdown": {
                    "critical": 2,
                    "high": 5,
                    "medium": 12,
                    "low": 28
                },
                "status_breakdown": {
                    "new": 3,
                    "in_progress": 5,
                    "resolved": 35,
                    "closed": 4
                },
                "top_incident_types": [
                    {"type": "infrastructure", "count": 15},
                    {"type": "security", "count": 12},
                    {"type": "supply_chain", "count": 8},
                    {"type": "personnel", "count": 7},
                    {"type": "natural_disaster", "count": 5}
                ],
                "response_time_avg": 0.5,  # hours
                "escalation_rate": 18.5  # percentage
            }
            return metrics
        except Exception as e:
            logger.error(f"Failed to get incident metrics: {e}")
            return {}
    
    # Helper methods
    def _map_severity(self, severity: IncidentSeverity) -> int:
        """Map BCM severity to TheHive severity (1-4)"""
        mapping = {
            IncidentSeverity.LOW: 1,
            IncidentSeverity.MEDIUM: 2,
            IncidentSeverity.HIGH: 3,
            IncidentSeverity.CRITICAL: 4
        }
        return mapping.get(severity, 2)
    
    def _reverse_map_severity(self, severity: int) -> IncidentSeverity:
        """Map TheHive severity to BCM severity"""
        mapping = {
            1: IncidentSeverity.LOW,
            2: IncidentSeverity.MEDIUM,
            3: IncidentSeverity.HIGH,
            4: IncidentSeverity.CRITICAL
        }
        return mapping.get(severity, IncidentSeverity.MEDIUM)


# FastAPI service endpoint
if __name__ == "__main__":
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    
    app = FastAPI(title="TheHive Adapter Service")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    config = {
        "thehive_url": "http://localhost:9000",
        "api_key": "demo_key",
        "eventbus_url": "http://localhost:8001"
    }
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "thehive_adapter"}
    
    @app.post("/api/alerts")
    async def create_alert(alert: Alert):
        async with TheHiveAdapter(config) as adapter:
            result = await adapter.create_alert(alert)
            return result.dict()
    
    @app.post("/api/cases")
    async def create_case(case: Case):
        async with TheHiveAdapter(config) as adapter:
            result = await adapter.create_case(case)
            return result.dict()
    
    @app.get("/api/cases")
    async def get_cases(status: Optional[CaseStatus] = None, 
                        severity: Optional[IncidentSeverity] = None):
        async with TheHiveAdapter(config) as adapter:
            cases = await adapter.get_cases(status, severity)
            return {"cases": [c.dict() for c in cases]}
    
    @app.get("/api/metrics")
    async def get_metrics(tenant_id: str = "demo"):
        async with TheHiveAdapter(config) as adapter:
            metrics = await adapter.get_incident_metrics(tenant_id)
            return metrics
    
    @app.post("/api/alerts/{alert_id}/promote")
    async def promote_alert(alert_id: str):
        async with TheHiveAdapter(config) as adapter:
            case = await adapter.promote_alert_to_case(alert_id)
            return case.dict()
    
    uvicorn.run(app, host="0.0.0.0", port=8007)
