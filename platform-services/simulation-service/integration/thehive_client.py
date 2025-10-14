"""
TheHive SOAR Integration Client
================================

Integration with TheHive platform for incident management during simulations.

Adapted from: /simulation/thehive/thehive_adapter.py
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class IncidentSeverity(str, Enum):
    """Incident severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    """Incident status"""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    FALSE_POSITIVE = "false_positive"


class CaseStatus(str, Enum):
    """Case status in TheHive"""
    OPEN = "Open"
    IN_PROGRESS = "InProgress"
    RESOLVED = "Resolved"
    DELETED = "Deleted"


class Alert(BaseModel):
    """Alert model for TheHive"""
    id: Optional[str] = None
    title: str
    description: str
    severity: IncidentSeverity
    source: str = "BCM Simulation"
    source_ref: Optional[str] = None
    artifacts: List[Dict] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tenant_id: str = "demo"


class Case(BaseModel):
    """Case model for TheHive"""
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
    """Task model for TheHive cases"""
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
    """Observable/IOC for cases"""
    data: str
    dataType: str  # ip, domain, url, hash, email, etc.
    message: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    ioc: bool = False
    sighted: bool = False


class TheHiveClient:
    """
    Client for integrating with TheHive SOAR platform

    Provides incident management capabilities for BCM simulations.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:9000",
        api_key: str = "",
        eventbus_url: str = "http://localhost:8001",
        org_name: str = "BCM"
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.eventbus_url = eventbus_url
        self.org_name = org_name

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
                "source": "thehive_client"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.eventbus_url}/api/events/publish",
                    json=event,
                    timeout=5.0
                )
                response.raise_for_status()
                logger.info(f"Published event: {event_type}")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")

    # ========================================================================
    # ALERT MANAGEMENT
    # ========================================================================

    async def create_alert(self, alert: Alert) -> Alert:
        """Create an alert in TheHive"""
        try:
            payload = {
                "title": alert.title,
                "description": alert.description,
                "severity": self._map_severity(alert.severity),
                "source": alert.source,
                "sourceRef": alert.source_ref or alert.id or f"sim_{datetime.utcnow().timestamp()}",
                "artifacts": alert.artifacts,
                "tags": alert.tags + ["BCM", "ISO22301", "Simulation"],
                "type": "bcm_simulation_incident",
                "customFields": {
                    "bcm.tenant_id": {"string": alert.tenant_id},
                    "bcm.incident_type": {"string": "simulation"}
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
                await self.publish_event("bcm.simulation.alert_created", {
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
                await self.publish_event("bcm.simulation.case_created", {
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

    # ========================================================================
    # CASE MANAGEMENT
    # ========================================================================

    async def create_case(self, case: Case) -> Case:
        """Create a case directly"""
        try:
            payload = {
                "title": case.title,
                "description": case.description,
                "severity": self._map_severity(case.severity),
                "status": case.status.value,
                "tags": case.tags + ["BCM", "ISO22301", "Simulation"],
                "metrics": case.metrics,
                "customFields": {
                    "bcm.tenant_id": {"string": "demo"},
                    "bcm.process_affected": {"string": case.bcm_context.get("process", "")},
                    "bcm.recovery_time": {"number": case.bcm_context.get("rto", 4)},
                    "bcm.simulation_id": {"string": case.bcm_context.get("simulation_id", "")}
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
                await self.publish_event("bcm.simulation.case_created", {
                    "case_id": case.id,
                    "case_number": case.case_id,
                    "title": case.title,
                    "severity": case.severity,
                    "tenant_id": "demo"
                })

                # Auto-create BCM tasks
                await self._create_bcm_tasks(case.id)

            return case

        except Exception as e:
            logger.error(f"Failed to create case: {e}")
            raise

    async def get_cases(
        self,
        status: Optional[CaseStatus] = None,
        severity: Optional[IncidentSeverity] = None,
        simulation_id: Optional[str] = None
    ) -> List[Case]:
        """Get cases with optional filters"""
        try:
            # In production, query TheHive API with filters
            # For now, return mock data for testing
            cases = await self._get_mock_cases()

            # Apply filters
            if status:
                cases = [c for c in cases if c.status == status]
            if severity:
                cases = [c for c in cases if c.severity == severity]
            if simulation_id:
                cases = [c for c in cases if c.bcm_context.get("simulation_id") == simulation_id]

            return cases

        except Exception as e:
            logger.error(f"Failed to get cases: {e}")
            return []

    async def update_case(self, case_id: str, updates: Dict[str, Any]) -> Optional[Case]:
        """Update case details"""
        try:
            response = await self.client.patch(
                f"{self.base_url}/api/case/{case_id}",
                json=updates
            )

            if response.status_code == 200:
                # Publish event
                await self.publish_event("bcm.simulation.case_updated", {
                    "case_id": case_id,
                    "updates": updates,
                    "tenant_id": "demo"
                })

                return Case(id=case_id, **updates)

            return None

        except Exception as e:
            logger.error(f"Failed to update case: {e}")
            return None

    # ========================================================================
    # TASK MANAGEMENT
    # ========================================================================

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
                await self.publish_event("bcm.simulation.task_created", {
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
            try:
                await self.create_task(task)
            except Exception as e:
                logger.warning(f"Failed to create task '{task.title}': {e}")

    # ========================================================================
    # ANALYTICS
    # ========================================================================

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

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

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

    async def _get_mock_cases(self) -> List[Case]:
        """Get mock cases for testing"""
        return [
            Case(
                id="case_001",
                case_id=101,
                title="Simulated Data Center Power Outage",
                description="Simulation: Primary data center lost power",
                severity=IncidentSeverity.CRITICAL,
                status=CaseStatus.IN_PROGRESS,
                tags=["infrastructure", "critical_process", "simulation"],
                bcm_context={
                    "process": "IT Services",
                    "rto": 2,
                    "impact": "high",
                    "simulation_id": "sim_001"
                }
            ),
            Case(
                id="case_002",
                case_id=102,
                title="Simulated Ransomware Attack",
                description="Simulation: Ransomware detected on file servers",
                severity=IncidentSeverity.CRITICAL,
                status=CaseStatus.IN_PROGRESS,
                tags=["security", "ransomware", "simulation"],
                bcm_context={
                    "process": "All",
                    "rto": 1,
                    "impact": "critical",
                    "simulation_id": "sim_002"
                }
            )
        ]
