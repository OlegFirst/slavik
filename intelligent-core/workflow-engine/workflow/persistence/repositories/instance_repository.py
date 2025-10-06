"""
Instance Repository

CRUD operations for BPMN process instances
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import uuid
import json

from ...bpmn.models import ProcessInstance, ProcessStatus


class InstanceRepository:
    """
    Repository for BPMN process instances

    Manages workflow.bpmn_instances table
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, instance: ProcessInstance) -> str:
        """
        Create new process instance

        Args:
            instance: ProcessInstance model

        Returns:
            str: Instance ID
        """
        instance_id = instance.id or str(uuid.uuid4())

        query = text("""
            INSERT INTO workflow.bpmn_instances (
                id, process_id, tenant_id, status, variables,
                current_activities, workflow_intelligence_context,
                started_by, started_at
            )
            VALUES (
                :id, :process_id, :tenant_id, :status, :variables,
                :current_activities, :workflow_intelligence_context,
                :started_by, NOW()
            )
            RETURNING id
        """)

        result = await self.session.execute(query, {
            "id": instance_id,
            "process_id": instance.process_id,
            "tenant_id": instance.tenant_id,
            "status": instance.status.value if isinstance(instance.status, ProcessStatus) else instance.status,
            "variables": json.dumps(instance.variables),
            "current_activities": instance.current_activities,
            "workflow_intelligence_context": json.dumps(instance.workflow_intelligence_id) if instance.workflow_intelligence_id else None,
            "started_by": instance.started_by
        })

        await self.session.commit()

        return instance_id

    async def get_by_id(self, instance_id: str) -> Optional[ProcessInstance]:
        """
        Get instance by ID

        Args:
            instance_id: Instance ID

        Returns:
            ProcessInstance or None
        """
        query = text("""
            SELECT *
            FROM workflow.bpmn_instances
            WHERE id = :instance_id
        """)

        result = await self.session.execute(query, {"instance_id": instance_id})
        row = result.fetchone()

        if not row:
            return None

        return ProcessInstance(
            id=str(row.id),
            process_id=str(row.process_id),
            tenant_id=row.tenant_id,
            status=ProcessStatus(row.status),
            variables=row.variables if isinstance(row.variables, dict) else {},
            current_activities=list(row.current_activities) if row.current_activities else [],
            workflow_intelligence_id=str(row.workflow_intelligence_context) if row.workflow_intelligence_context else None,
            started_by=row.started_by,
            started_at=row.started_at,
            completed_at=row.completed_at
        )

    async def list_by_tenant(
        self,
        tenant_id: str,
        status: Optional[ProcessStatus] = None,
        process_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ProcessInstance]:
        """
        List instances for tenant

        Args:
            tenant_id: Tenant identifier
            status: Filter by status (optional)
            process_id: Filter by process (optional)
            limit: Max results
            offset: Pagination offset

        Returns:
            List[ProcessInstance]
        """
        query_str = """
            SELECT *
            FROM workflow.bpmn_instances
            WHERE tenant_id = :tenant_id
        """

        params = {"tenant_id": tenant_id, "limit": limit, "offset": offset}

        if status:
            query_str += " AND status = :status"
            params["status"] = status.value

        if process_id:
            query_str += " AND process_id = :process_id"
            params["process_id"] = process_id

        query_str += " ORDER BY started_at DESC LIMIT :limit OFFSET :offset"

        query = text(query_str)
        result = await self.session.execute(query, params)

        instances = []
        for row in result.fetchall():
            instances.append(ProcessInstance(
                id=str(row.id),
                process_id=str(row.process_id),
                tenant_id=row.tenant_id,
                status=ProcessStatus(row.status),
                variables=row.variables if isinstance(row.variables, dict) else {},
                current_activities=list(row.current_activities) if row.current_activities else [],
                workflow_intelligence_id=str(row.workflow_intelligence_context) if row.workflow_intelligence_context else None,
                started_by=row.started_by,
                started_at=row.started_at,
                completed_at=row.completed_at
            ))

        return instances

    async def update_status(
        self,
        instance_id: str,
        status: ProcessStatus,
        completed_at: Optional[datetime] = None
    ) -> bool:
        """
        Update instance status

        Args:
            instance_id: Instance ID
            status: New status
            completed_at: Completion timestamp (if applicable)

        Returns:
            bool: True if updated
        """
        query_str = """
            UPDATE workflow.bpmn_instances
            SET status = :status
        """

        params = {
            "instance_id": instance_id,
            "status": status.value if isinstance(status, ProcessStatus) else status
        }

        if completed_at:
            query_str += ", completed_at = :completed_at"
            params["completed_at"] = completed_at

        query_str += " WHERE id = :instance_id"

        query = text(query_str)
        result = await self.session.execute(query, params)
        await self.session.commit()

        return result.rowcount > 0

    async def update_variables(
        self,
        instance_id: str,
        variables: Dict[str, Any],
        merge: bool = True
    ) -> bool:
        """
        Update instance variables

        Args:
            instance_id: Instance ID
            variables: Variables to update
            merge: If True, merge with existing. If False, replace

        Returns:
            bool: True if updated
        """
        if merge:
            # Merge with existing variables using JSONB || operator
            query = text("""
                UPDATE workflow.bpmn_instances
                SET variables = variables || :new_variables::jsonb
                WHERE id = :instance_id
            """)
        else:
            # Replace variables completely
            query = text("""
                UPDATE workflow.bpmn_instances
                SET variables = :new_variables::jsonb
                WHERE id = :instance_id
            """)

        result = await self.session.execute(query, {
            "instance_id": instance_id,
            "new_variables": json.dumps(variables)
        })
        await self.session.commit()

        return result.rowcount > 0

    async def update_current_activities(
        self,
        instance_id: str,
        current_activities: List[str]
    ) -> bool:
        """
        Update current activities

        Args:
            instance_id: Instance ID
            current_activities: List of activity IDs

        Returns:
            bool: True if updated
        """
        query = text("""
            UPDATE workflow.bpmn_instances
            SET current_activities = :current_activities
            WHERE id = :instance_id
        """)

        result = await self.session.execute(query, {
            "instance_id": instance_id,
            "current_activities": current_activities
        })
        await self.session.commit()

        return result.rowcount > 0

    async def add_activity(
        self,
        instance_id: str,
        activity_id: str
    ) -> bool:
        """
        Add activity to current activities

        Args:
            instance_id: Instance ID
            activity_id: Activity ID to add

        Returns:
            bool: True if updated
        """
        query = text("""
            UPDATE workflow.bpmn_instances
            SET current_activities = array_append(current_activities, :activity_id)
            WHERE id = :instance_id
            AND NOT (:activity_id = ANY(current_activities))
        """)

        result = await self.session.execute(query, {
            "instance_id": instance_id,
            "activity_id": activity_id
        })
        await self.session.commit()

        return result.rowcount > 0

    async def remove_activity(
        self,
        instance_id: str,
        activity_id: str
    ) -> bool:
        """
        Remove activity from current activities

        Args:
            instance_id: Instance ID
            activity_id: Activity ID to remove

        Returns:
            bool: True if updated
        """
        query = text("""
            UPDATE workflow.bpmn_instances
            SET current_activities = array_remove(current_activities, :activity_id)
            WHERE id = :instance_id
        """)

        result = await self.session.execute(query, {
            "instance_id": instance_id,
            "activity_id": activity_id
        })
        await self.session.commit()

        return result.rowcount > 0

    async def update_workflow_intelligence_context(
        self,
        instance_id: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Update Workflow Intelligence context (for AI integration)

        Args:
            instance_id: Instance ID
            context: Workflow Intelligence context data

        Returns:
            bool: True if updated
        """
        query = text("""
            UPDATE workflow.bpmn_instances
            SET workflow_intelligence_context = :context::jsonb
            WHERE id = :instance_id
        """)

        result = await self.session.execute(query, {
            "instance_id": instance_id,
            "context": json.dumps(context)
        })
        await self.session.commit()

        return result.rowcount > 0

    async def get_active_count(self, tenant_id: str) -> int:
        """
        Get count of active instances for tenant

        Args:
            tenant_id: Tenant identifier

        Returns:
            int: Count of active instances
        """
        query = text("""
            SELECT COUNT(*)
            FROM workflow.bpmn_instances
            WHERE tenant_id = :tenant_id
            AND status = 'ACTIVE'
        """)

        result = await self.session.execute(query, {"tenant_id": tenant_id})
        count = result.scalar()

        return count or 0

    async def get_statistics(
        self,
        tenant_id: str,
        process_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get instance statistics

        Args:
            tenant_id: Tenant identifier
            process_id: Filter by process (optional)

        Returns:
            Dict with statistics
        """
        query_str = """
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status = 'ACTIVE') as active,
                COUNT(*) FILTER (WHERE status = 'COMPLETED') as completed,
                COUNT(*) FILTER (WHERE status = 'TERMINATED') as terminated,
                AVG(EXTRACT(EPOCH FROM (completed_at - started_at)) / 3600)
                    FILTER (WHERE status = 'COMPLETED' AND completed_at IS NOT NULL)
                    as avg_duration_hours
            FROM workflow.bpmn_instances
            WHERE tenant_id = :tenant_id
        """

        params = {"tenant_id": tenant_id}

        if process_id:
            query_str += " AND process_id = :process_id"
            params["process_id"] = process_id

        query = text(query_str)
        result = await self.session.execute(query, params)
        row = result.fetchone()

        return {
            "total": row.total or 0,
            "active": row.active or 0,
            "completed": row.completed or 0,
            "terminated": row.terminated or 0,
            "avg_duration_hours": float(row.avg_duration_hours) if row.avg_duration_hours else None
        }

    async def delete(self, instance_id: str) -> bool:
        """
        Delete instance (hard delete)

        Warning: This will cascade delete all tasks!

        Args:
            instance_id: Instance ID

        Returns:
            bool: True if deleted
        """
        query = text("""
            DELETE FROM workflow.bpmn_instances
            WHERE id = :instance_id
        """)

        result = await self.session.execute(query, {"instance_id": instance_id})
        await self.session.commit()

        return result.rowcount > 0
