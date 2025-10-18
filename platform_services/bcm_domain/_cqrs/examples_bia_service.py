"""
Example: BIA Service with CQRS
===============================

Complete example of integrating CQRS into BIA Service.

This example shows:
1. Aggregate definition
2. Command and Query definitions
3. Projection definitions
4. Service integration
5. FastAPI endpoints

Directory structure:
    platform_services/bcm_domain/services/bia_service/
    ├── cqrs/
    │   ├── __init__.py
    │   ├── aggregates.py       # BIA aggregates
    │   ├── commands.py         # BIA commands
    │   ├── queries.py          # BIA queries
    │   ├── projections.py      # BIA projections
    │   └── handlers.py         # Command/Query handlers
    ├── api/
    │   └── routes_cqrs.py      # CQRS-based routes
    └── main.py                 # Service initialization
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

# CQRS imports
import sys
from pathlib import Path
cqrs_path = Path(__file__).parent
if str(cqrs_path) not in sys.path:
    sys.path.insert(0, str(cqrs_path))

from command_handler import Aggregate, Command, CommandResult
from query_handler import Query, QueryResult, cached_query
from projection_builder import Projection
from read_model_updater import ReadModelConfig
from event_store import Event, EventMetadata

logger = logging.getLogger(__name__)


# ============================================================================
# 1. AGGREGATES
# ============================================================================

class BIAProcessAggregate(Aggregate):
    """
    BIA Process Aggregate.

    Enforces business rules for BIA processes.
    """

    def __init__(self, aggregate_id: str):
        super().__init__(aggregate_id, "BIAProcess")
        # State
        self.name: Optional[str] = None
        self.department: Optional[str] = None
        self.process_owner: Optional[str] = None
        self.criticality: Optional[str] = None
        self.rto_hours: Optional[int] = None
        self.rpo_hours: Optional[int] = None
        self.mtpd_hours: Optional[int] = None
        self.financial_impact: Dict[str, float] = {}
        self.dependencies: List[Dict[str, Any]] = []
        self.status: str = "DRAFT"
        self.created_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    # ===== Commands =====

    def create(
        self,
        name: str,
        department: str,
        process_owner: str,
        criticality: str,
        rto_hours: int,
        rpo_hours: int,
        mtpd_hours: int,
        financial_impact: Dict[str, float],
        dependencies: List[Dict[str, Any]]
    ):
        """Create BIA process."""
        # Business rules validation
        if not name or len(name) < 3:
            raise ValueError("Name must be at least 3 characters")

        if criticality not in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            raise ValueError("Invalid criticality level")

        if rto_hours < 0 or rpo_hours < 0 or mtpd_hours < 0:
            raise ValueError("Time objectives must be non-negative")

        if rto_hours < rpo_hours:
            raise ValueError("RTO must be >= RPO")

        if mtpd_hours < rto_hours:
            raise ValueError("MTPD must be >= RTO")

        # Validate financial impact timeline
        if financial_impact:
            time_periods = ["1_hour", "4_hours", "8_hours", "24_hours"]
            values = [financial_impact.get(tp, 0) for tp in time_periods]
            if not all(values[i] <= values[i+1] for i in range(len(values)-1)):
                raise ValueError("Financial impact must increase over time")

        # Generate event
        self._apply_event(Event(
            event_type="BIAProcessCreated",
            aggregate_type=self.aggregate_type,
            aggregate_id=self.aggregate_id,
            version=self.version + 1,
            data={
                "name": name,
                "department": department,
                "process_owner": process_owner,
                "criticality": criticality,
                "rto_hours": rto_hours,
                "rpo_hours": rpo_hours,
                "mtpd_hours": mtpd_hours,
                "financial_impact": financial_impact,
                "dependencies": dependencies,
                "status": "DRAFT",
                "created_at": datetime.utcnow().isoformat()
            }
        ))

    def update_recovery_objectives(
        self,
        rto_hours: Optional[int] = None,
        rpo_hours: Optional[int] = None,
        mtpd_hours: Optional[int] = None,
        justification: Optional[str] = None
    ):
        """Update recovery time objectives."""
        # Use existing values if not provided
        new_rto = rto_hours if rto_hours is not None else self.rto_hours
        new_rpo = rpo_hours if rpo_hours is not None else self.rpo_hours
        new_mtpd = mtpd_hours if mtpd_hours is not None else self.mtpd_hours

        # Validate
        if new_rto < new_rpo:
            raise ValueError("RTO must be >= RPO")

        if new_mtpd < new_rto:
            raise ValueError("MTPD must be >= RTO")

        # Generate event
        self._apply_event(Event(
            event_type="BIAProcessRecoveryObjectivesUpdated",
            aggregate_type=self.aggregate_type,
            aggregate_id=self.aggregate_id,
            version=self.version + 1,
            data={
                "rto_hours": new_rto,
                "rpo_hours": new_rpo,
                "mtpd_hours": new_mtpd,
                "previous_rto": self.rto_hours,
                "previous_rpo": self.rpo_hours,
                "previous_mtpd": self.mtpd_hours,
                "justification": justification
            }
        ))

    def update_criticality(self, criticality: str, justification: str):
        """Update criticality level."""
        if criticality not in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            raise ValueError("Invalid criticality level")

        if criticality == self.criticality:
            return  # No change

        self._apply_event(Event(
            event_type="BIAProcessCriticalityChanged",
            aggregate_type=self.aggregate_type,
            aggregate_id=self.aggregate_id,
            version=self.version + 1,
            data={
                "criticality": criticality,
                "previous_criticality": self.criticality,
                "justification": justification
            }
        ))

    def add_dependency(self, dependency: Dict[str, Any]):
        """Add process dependency."""
        # Validate dependency
        if not dependency.get("type") or not dependency.get("name"):
            raise ValueError("Dependency must have type and name")

        # Check for duplicates
        if any(d["name"] == dependency["name"] for d in self.dependencies):
            raise ValueError(f"Dependency {dependency['name']} already exists")

        self._apply_event(Event(
            event_type="BIAProcessDependencyAdded",
            aggregate_type=self.aggregate_type,
            aggregate_id=self.aggregate_id,
            version=self.version + 1,
            data={"dependency": dependency}
        ))

    def complete(self, assessor: str, reviewer: Optional[str] = None):
        """Mark BIA process as completed."""
        if self.status == "COMPLETED":
            raise ValueError("BIA process already completed")

        # Validate minimum requirements for completion
        if not self.name or not self.criticality:
            raise ValueError("Cannot complete BIA without name and criticality")

        if self.rto_hours is None or self.rpo_hours is None:
            raise ValueError("Cannot complete BIA without RTO and RPO")

        self._apply_event(Event(
            event_type="BIAProcessCompleted",
            aggregate_type=self.aggregate_type,
            aggregate_id=self.aggregate_id,
            version=self.version + 1,
            data={
                "previous_status": self.status,
                "assessor": assessor,
                "reviewer": reviewer,
                "completed_at": datetime.utcnow().isoformat()
            }
        ))

    def reopen(self, reason: str):
        """Reopen completed BIA process."""
        if self.status != "COMPLETED":
            raise ValueError("Can only reopen completed BIA processes")

        self._apply_event(Event(
            event_type="BIAProcessReopened",
            aggregate_type=self.aggregate_type,
            aggregate_id=self.aggregate_id,
            version=self.version + 1,
            data={
                "previous_status": self.status,
                "reason": reason,
                "reopened_at": datetime.utcnow().isoformat()
            }
        ))

    # ===== Event Handlers =====

    def _apply_BIAProcessCreated(self, event: Event):
        """Apply BIAProcessCreated event."""
        self.name = event.data["name"]
        self.department = event.data["department"]
        self.process_owner = event.data["process_owner"]
        self.criticality = event.data["criticality"]
        self.rto_hours = event.data["rto_hours"]
        self.rpo_hours = event.data["rpo_hours"]
        self.mtpd_hours = event.data["mtpd_hours"]
        self.financial_impact = event.data.get("financial_impact", {})
        self.dependencies = event.data.get("dependencies", [])
        self.status = event.data.get("status", "DRAFT")
        self.created_at = datetime.fromisoformat(event.data["created_at"])

    def _apply_BIAProcessRecoveryObjectivesUpdated(self, event: Event):
        """Apply recovery objectives updated event."""
        self.rto_hours = event.data["rto_hours"]
        self.rpo_hours = event.data["rpo_hours"]
        self.mtpd_hours = event.data["mtpd_hours"]

    def _apply_BIAProcessCriticalityChanged(self, event: Event):
        """Apply criticality changed event."""
        self.criticality = event.data["criticality"]

    def _apply_BIAProcessDependencyAdded(self, event: Event):
        """Apply dependency added event."""
        self.dependencies.append(event.data["dependency"])

    def _apply_BIAProcessCompleted(self, event: Event):
        """Apply BIA process completed event."""
        self.status = "COMPLETED"
        self.completed_at = datetime.fromisoformat(event.data["completed_at"])

    def _apply_BIAProcessReopened(self, event: Event):
        """Apply BIA process reopened event."""
        self.status = "DRAFT"
        self.completed_at = None

    # ===== Snapshot Support =====

    def to_dict(self) -> Dict[str, Any]:
        """Convert aggregate to dictionary for snapshot."""
        return {
            "name": self.name,
            "department": self.department,
            "process_owner": self.process_owner,
            "criticality": self.criticality,
            "rto_hours": self.rto_hours,
            "rpo_hours": self.rpo_hours,
            "mtpd_hours": self.mtpd_hours,
            "financial_impact": self.financial_impact,
            "dependencies": self.dependencies,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Restore aggregate from snapshot."""
        self.name = data.get("name")
        self.department = data.get("department")
        self.process_owner = data.get("process_owner")
        self.criticality = data.get("criticality")
        self.rto_hours = data.get("rto_hours")
        self.rpo_hours = data.get("rpo_hours")
        self.mtpd_hours = data.get("mtpd_hours")
        self.financial_impact = data.get("financial_impact", {})
        self.dependencies = data.get("dependencies", [])
        self.status = data.get("status", "DRAFT")

        created_at = data.get("created_at")
        self.created_at = datetime.fromisoformat(created_at) if created_at else None

        completed_at = data.get("completed_at")
        self.completed_at = datetime.fromisoformat(completed_at) if completed_at else None


# ============================================================================
# 2. COMMANDS
# ============================================================================

@dataclass
class CreateBIAProcessCommand(Command):
    """Command to create BIA process."""
    name: str = ""
    department: str = ""
    process_owner: str = ""
    criticality: str = ""
    rto_hours: int = 0
    rpo_hours: int = 0
    mtpd_hours: int = 0
    financial_impact: Dict[str, float] = field(default_factory=dict)
    dependencies: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class UpdateRecoveryObjectivesCommand(Command):
    """Command to update recovery objectives."""
    aggregate_id: str = ""
    rto_hours: Optional[int] = None
    rpo_hours: Optional[int] = None
    mtpd_hours: Optional[int] = None
    justification: Optional[str] = None


@dataclass
class UpdateCriticalityCommand(Command):
    """Command to update criticality."""
    aggregate_id: str = ""
    criticality: str = ""
    justification: str = ""


@dataclass
class AddDependencyCommand(Command):
    """Command to add dependency."""
    aggregate_id: str = ""
    dependency: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompleteBIAProcessCommand(Command):
    """Command to complete BIA process."""
    aggregate_id: str = ""
    assessor: str = ""
    reviewer: Optional[str] = None


@dataclass
class ReopenBIAProcessCommand(Command):
    """Command to reopen BIA process."""
    aggregate_id: str = ""
    reason: str = ""


# ============================================================================
# 3. QUERIES
# ============================================================================

@dataclass
class GetBIAProcessesQuery(Query):
    """Query to get list of BIA processes."""
    criticality: Optional[str] = None
    status: Optional[str] = None
    department: Optional[str] = None
    limit: int = 100
    offset: int = 0


@dataclass
class GetBIAProcessDetailQuery(Query):
    """Query to get single BIA process."""
    process_id: str = ""


@dataclass
class GetCriticalProcessesQuery(Query):
    """Query to get critical processes."""
    limit: int = 20


@dataclass
class GetBIASummaryQuery(Query):
    """Query to get BIA summary."""
    pass


@dataclass
class GetBIADashboardQuery(Query):
    """Query to get dashboard data."""
    pass


# ============================================================================
# 4. PROJECTIONS
# ============================================================================

class BIAProcessListProjection(Projection):
    """BIA Process List Projection for queries."""

    def __init__(self):
        super().__init__()
        self.projection_name = "bia_process_list"

    async def ensure_schema(self, conn):
        """Create read model tables."""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS read_bia_processes (
                id VARCHAR(255) PRIMARY KEY,
                tenant_id VARCHAR(255) NOT NULL,
                name VARCHAR(500) NOT NULL,
                department VARCHAR(255),
                process_owner VARCHAR(255),
                criticality VARCHAR(50) NOT NULL,
                rto_hours INTEGER NOT NULL,
                rpo_hours INTEGER NOT NULL,
                mtpd_hours INTEGER NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'DRAFT',
                dependency_count INTEGER DEFAULT 0,
                created_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """)

        # Indexes
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_read_bia_tenant
            ON read_bia_processes(tenant_id)
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_read_bia_criticality
            ON read_bia_processes(tenant_id, criticality)
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_read_bia_status
            ON read_bia_processes(tenant_id, status)
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_read_bia_department
            ON read_bia_processes(tenant_id, department)
        """)

    async def handle_event(self, event: Event, conn):
        """Handle BIA events."""
        if event.event_type == "BIAProcessCreated":
            await conn.execute("""
                INSERT INTO read_bia_processes (
                    id, tenant_id, name, department, process_owner,
                    criticality, rto_hours, rpo_hours, mtpd_hours,
                    status, dependency_count, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                ON CONFLICT (id) DO NOTHING
            """,
                event.aggregate_id,
                event.metadata.tenant_id,
                event.data["name"],
                event.data.get("department"),
                event.data.get("process_owner"),
                event.data["criticality"],
                event.data["rto_hours"],
                event.data["rpo_hours"],
                event.data["mtpd_hours"],
                event.data.get("status", "DRAFT"),
                len(event.data.get("dependencies", [])),
                datetime.fromisoformat(event.data["created_at"])
            )

        elif event.event_type == "BIAProcessRecoveryObjectivesUpdated":
            await conn.execute("""
                UPDATE read_bia_processes
                SET rto_hours = $1, rpo_hours = $2, mtpd_hours = $3,
                    updated_at = NOW()
                WHERE id = $4
            """,
                event.data["rto_hours"],
                event.data["rpo_hours"],
                event.data["mtpd_hours"],
                event.aggregate_id
            )

        elif event.event_type == "BIAProcessCriticalityChanged":
            await conn.execute("""
                UPDATE read_bia_processes
                SET criticality = $1, updated_at = NOW()
                WHERE id = $2
            """, event.data["criticality"], event.aggregate_id)

        elif event.event_type == "BIAProcessDependencyAdded":
            await conn.execute("""
                UPDATE read_bia_processes
                SET dependency_count = dependency_count + 1, updated_at = NOW()
                WHERE id = $1
            """, event.aggregate_id)

        elif event.event_type == "BIAProcessCompleted":
            await conn.execute("""
                UPDATE read_bia_processes
                SET status = 'COMPLETED',
                    completed_at = $1,
                    updated_at = NOW()
                WHERE id = $2
            """,
                datetime.fromisoformat(event.data["completed_at"]),
                event.aggregate_id
            )

        elif event.event_type == "BIAProcessReopened":
            await conn.execute("""
                UPDATE read_bia_processes
                SET status = 'DRAFT', completed_at = NULL, updated_at = NOW()
                WHERE id = $1
            """, event.aggregate_id)

    async def clear(self, conn):
        """Clear projection data."""
        await conn.execute("TRUNCATE TABLE read_bia_processes")


class BIASummaryProjection(Projection):
    """BIA Summary Projection for dashboard."""

    def __init__(self):
        super().__init__()
        self.projection_name = "bia_summary"

    async def ensure_schema(self, conn):
        """Create summary table."""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS read_bia_summary (
                tenant_id VARCHAR(255) PRIMARY KEY,
                total_processes INTEGER DEFAULT 0,
                critical_count INTEGER DEFAULT 0,
                high_count INTEGER DEFAULT 0,
                medium_count INTEGER DEFAULT 0,
                low_count INTEGER DEFAULT 0,
                completed_count INTEGER DEFAULT 0,
                draft_count INTEGER DEFAULT 0,
                avg_rto_hours FLOAT DEFAULT 0,
                avg_rpo_hours FLOAT DEFAULT 0,
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """)

    async def handle_event(self, event: Event, conn):
        """Update summary statistics."""
        tenant_id = event.metadata.tenant_id

        if event.event_type == "BIAProcessCreated":
            # Initialize if needed
            await conn.execute("""
                INSERT INTO read_bia_summary (tenant_id)
                VALUES ($1)
                ON CONFLICT (tenant_id) DO NOTHING
            """, tenant_id)

            # Update counts
            criticality = event.data["criticality"]
            await conn.execute(f"""
                UPDATE read_bia_summary
                SET total_processes = total_processes + 1,
                    {criticality.lower()}_count = {criticality.lower()}_count + 1,
                    draft_count = draft_count + 1,
                    updated_at = NOW()
                WHERE tenant_id = $1
            """, tenant_id)

            # Recalculate averages
            await self._recalculate_averages(conn, tenant_id)

        elif event.event_type == "BIAProcessCompleted":
            await conn.execute("""
                UPDATE read_bia_summary
                SET completed_count = completed_count + 1,
                    draft_count = draft_count - 1,
                    updated_at = NOW()
                WHERE tenant_id = $1
            """, tenant_id)

        elif event.event_type == "BIAProcessReopened":
            await conn.execute("""
                UPDATE read_bia_summary
                SET completed_count = completed_count - 1,
                    draft_count = draft_count + 1,
                    updated_at = NOW()
                WHERE tenant_id = $1
            """, tenant_id)

    async def _recalculate_averages(self, conn, tenant_id: str):
        """Recalculate average RTO/RPO."""
        avg_rto, avg_rpo = await conn.fetchrow("""
            SELECT AVG(rto_hours), AVG(rpo_hours)
            FROM read_bia_processes
            WHERE tenant_id = $1
        """, tenant_id)

        if avg_rto:
            await conn.execute("""
                UPDATE read_bia_summary
                SET avg_rto_hours = $1, avg_rpo_hours = $2
                WHERE tenant_id = $3
            """, float(avg_rto), float(avg_rpo), tenant_id)

    async def clear(self, conn):
        """Clear summary data."""
        await conn.execute("TRUNCATE TABLE read_bia_summary")


# ============================================================================
# 5. FASTAPI INTEGRATION
# ============================================================================

# Example request/response models
class CreateBIARequest(BaseModel):
    """Request model for creating BIA process."""
    name: str
    department: str
    process_owner: str
    criticality: str
    rto_hours: int
    rpo_hours: int
    mtpd_hours: int
    financial_impact: Optional[Dict[str, float]] = {}
    dependencies: Optional[List[Dict[str, Any]]] = []


class UpdateRTORequest(BaseModel):
    """Request model for updating RTO."""
    rto_hours: Optional[int] = None
    rpo_hours: Optional[int] = None
    mtpd_hours: Optional[int] = None
    justification: Optional[str] = None


# Example router
router = APIRouter(prefix="/api/v2/bia", tags=["BIA CQRS"])


@router.post("/processes", status_code=201)
async def create_bia_process(
    request: CreateBIARequest,
    current_user=None  # Depends(get_current_user)
):
    """
    Create BIA process using CQRS.

    Example:
        ```bash
        curl -X POST http://localhost:8012/api/v2/bia/processes \\
             -H "Content-Type: application/json" \\
             -d '{
               "name": "Payment Processing",
               "department": "Finance",
               "process_owner": "John Doe",
               "criticality": "CRITICAL",
               "rto_hours": 2,
               "rpo_hours": 1,
               "mtpd_hours": 4
             }'
        ```
    """
    from _cqrs import get_command_handler

    command_handler = get_command_handler()

    result = await command_handler.handle(
        command=CreateBIAProcessCommand(
            tenant_id="tenant_123",  # From current_user
            user_id="user_456",  # From current_user
            name=request.name,
            department=request.department,
            process_owner=request.process_owner,
            criticality=request.criticality,
            rto_hours=request.rto_hours,
            rpo_hours=request.rpo_hours,
            mtpd_hours=request.mtpd_hours,
            financial_impact=request.financial_impact,
            dependencies=request.dependencies
        ),
        executor=lambda agg, cmd: agg.create(
            cmd.name,
            cmd.department,
            cmd.process_owner,
            cmd.criticality,
            cmd.rto_hours,
            cmd.rpo_hours,
            cmd.mtpd_hours,
            cmd.financial_impact,
            cmd.dependencies
        ),
        aggregate_type="BIAProcess",
        create_new=True
    )

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    return {
        "id": result.aggregate_id,
        "version": result.version,
        "message": "BIA process created successfully"
    }


@router.get("/processes")
async def list_bia_processes(
    criticality: Optional[str] = None,
    status: Optional[str] = None,
    department: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user=None
):
    """
    List BIA processes using CQRS query.

    Example:
        ```bash
        curl http://localhost:8012/api/v2/bia/processes?criticality=CRITICAL&limit=20
        ```
    """
    from _cqrs import get_query_handler

    query_handler = get_query_handler()

    result = await query_handler.get_bia_processes(
        GetBIAProcessesQuery(
            tenant_id="tenant_123",
            criticality=criticality,
            status=status,
            department=department,
            limit=limit,
            offset=offset
        )
    )

    return {
        "processes": result.data,
        "count": result.count,
        "cached": result.cached
    }


@router.get("/processes/{process_id}")
async def get_bia_process(process_id: str, current_user=None):
    """Get BIA process details."""
    from _cqrs import get_query_handler

    query_handler = get_query_handler()

    result = await query_handler.get_bia_process_detail(
        GetBIAProcessDetailQuery(
            tenant_id="tenant_123",
            process_id=process_id
        )
    )

    if not result.success or not result.data:
        raise HTTPException(status_code=404, detail="BIA process not found")

    return result.data


@router.put("/processes/{process_id}/rto")
async def update_rto(
    process_id: str,
    request: UpdateRTORequest,
    current_user=None
):
    """Update recovery objectives."""
    from _cqrs import get_command_handler

    command_handler = get_command_handler()

    result = await command_handler.handle(
        command=UpdateRecoveryObjectivesCommand(
            tenant_id="tenant_123",
            user_id="user_456",
            aggregate_id=process_id,
            rto_hours=request.rto_hours,
            rpo_hours=request.rpo_hours,
            mtpd_hours=request.mtpd_hours,
            justification=request.justification
        ),
        executor=lambda agg, cmd: agg.update_recovery_objectives(
            cmd.rto_hours,
            cmd.rpo_hours,
            cmd.mtpd_hours,
            cmd.justification
        ),
        aggregate_type="BIAProcess",
        aggregate_id=process_id
    )

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    return {"message": "Recovery objectives updated", "version": result.version}


@router.post("/processes/{process_id}/complete")
async def complete_bia_process(process_id: str, current_user=None):
    """Complete BIA process."""
    from _cqrs import get_command_handler

    command_handler = get_command_handler()

    result = await command_handler.handle(
        command=CompleteBIAProcessCommand(
            tenant_id="tenant_123",
            user_id="user_456",
            aggregate_id=process_id,
            assessor="user_456"
        ),
        executor=lambda agg, cmd: agg.complete(cmd.assessor, cmd.reviewer),
        aggregate_type="BIAProcess",
        aggregate_id=process_id
    )

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    return {"message": "BIA process completed", "version": result.version}


@router.get("/summary")
async def get_summary(current_user=None):
    """Get BIA summary."""
    from _cqrs import get_query_handler

    query_handler = get_query_handler()

    result = await query_handler.get_bia_summary(
        GetBIASummaryQuery(tenant_id="tenant_123")
    )

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)

    return result.data or {}


# ============================================================================
# 6. SERVICE INITIALIZATION
# ============================================================================

async def initialize_bia_cqrs(app, settings):
    """
    Initialize BIA CQRS components.

    Call this in main.py during startup.

    Example:
        ```python
        @app.on_event("startup")
        async def startup():
            await initialize_bia_cqrs(app, settings)
        ```
    """
    from _cqrs import (
        init_cqrs, get_command_handler, get_projection_builder,
        get_read_model_updater
    )
    from shared.eventbus import get_eventbus

    # Initialize CQRS
    logger.info("Initializing BIA CQRS...")
    cmd_handler, query_handler = await init_cqrs(
        database_url=settings.DATABASE_URL,
        eventbus_client=get_eventbus(),
        redis_url=settings.REDIS_URL
    )

    # Register aggregates
    cmd_handler.register_aggregate(
        "BIAProcess",
        lambda id: BIAProcessAggregate(id)
    )

    # Register projections
    projection_builder = get_projection_builder()
    projection_builder.register_projection(BIAProcessListProjection())
    projection_builder.register_projection(BIASummaryProjection())
    await projection_builder.ensure_schemas()

    # Configure read model updater
    updater = get_read_model_updater()

    updater.register_config(ReadModelConfig(
        projection_name="bia_process_list",
        event_types=[
            "BIAProcessCreated",
            "BIAProcessRecoveryObjectivesUpdated",
            "BIAProcessCriticalityChanged",
            "BIAProcessDependencyAdded",
            "BIAProcessCompleted",
            "BIAProcessReopened"
        ],
        cache_patterns=[
            "cqrs:query:get_bia_processes:*",
            "cqrs:query:get_bia_process_detail:*",
            "cqrs:query:get_critical_processes:*"
        ]
    ))

    updater.register_config(ReadModelConfig(
        projection_name="bia_summary",
        event_types=[
            "BIAProcessCreated",
            "BIAProcessCompleted",
            "BIAProcessReopened"
        ],
        cache_patterns=[
            "cqrs:query:get_bia_summary:*"
        ]
    ))

    # Start updater
    await updater.start(poll_interval=1.0, catch_up=True)

    logger.info("BIA CQRS initialized successfully")


"""
USAGE SUMMARY
=============

1. Add to main.py:
   ```python
   from cqrs.examples_bia_service import initialize_bia_cqrs, router

   @app.on_event("startup")
   async def startup():
       await initialize_bia_cqrs(app, settings)

   app.include_router(router)
   ```

2. Test commands:
   ```bash
   # Create BIA
   curl -X POST http://localhost:8012/api/v2/bia/processes \\
        -H "Content-Type: application/json" \\
        -d '{"name": "Test", "criticality": "HIGH", "rto_hours": 4, ...}'

   # List BIA processes
   curl http://localhost:8012/api/v2/bia/processes

   # Get summary
   curl http://localhost:8012/api/v2/bia/summary
   ```

3. Monitor:
   ```python
   # Get metrics
   from _cqrs import get_read_model_updater
   updater = get_read_model_updater()
   metrics = await updater.get_metrics()
   print(f"Events processed: {metrics['events_processed']}")
   ```

4. Rebuild projections (if needed):
   ```python
   from _cqrs import get_projection_builder
   builder = get_projection_builder()
   await builder.rebuild_projection("bia_process_list")
   ```
"""
