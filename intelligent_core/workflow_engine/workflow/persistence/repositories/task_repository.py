"""
Task Repository

CRUD operations for BPMN tasks
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import uuid
import json

from ...bpmn.models import Task, TaskStatus, TaskType


class TaskRepository:
    """
    Repository for BPMN tasks

    Manages workflow.bpmn_tasks table
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, task: Task) -> str:
        """
        Create new task

        Args:
            task: Task model

        Returns:
            str: Task ID
        """
        task_id = task.id or str(uuid.uuid4())

        query = text("""
            INSERT INTO workflow.bpmn_tasks (
                id, instance_id, activity_id, name, task_type,
                assignee, status, variables, ai_recommendations,
                ai_predicted_duration_hours, created_at
            )
            VALUES (
                :id, :instance_id, :activity_id, :name, :task_type,
                :assignee, :status, :variables, :ai_recommendations,
                :ai_predicted_duration_hours, NOW()
            )
            RETURNING id
        """)

        result = await self.session.execute(query, {
            "id": task_id,
            "instance_id": task.instance_id,
            "activity_id": task.activity_id,
            "name": task.name,
            "task_type": task.task_type.value if isinstance(task.task_type, TaskType) else task.task_type,
            "assignee": task.assignee,
            "status": task.status.value if isinstance(task.status, TaskStatus) else task.status,
            "variables": json.dumps(task.variables),
            "ai_recommendations": json.dumps(task.ai_recommendations) if task.ai_recommendations else None,
            "ai_predicted_duration_hours": task.ai_predicted_duration_hours
        })

        await self.session.commit()

        return task_id

    async def get_by_id(self, task_id: str) -> Optional[Task]:
        """
        Get task by ID

        Args:
            task_id: Task ID

        Returns:
            Task or None
        """
        query = text("""
            SELECT *
            FROM workflow.bpmn_tasks
            WHERE id = :task_id
        """)

        result = await self.session.execute(query, {"task_id": task_id})
        row = result.fetchone()

        if not row:
            return None

        return Task(
            id=str(row.id),
            process_instance_id=str(row.instance_id),
            activity_id=row.activity_id,
            name=row.name,
            task_type=TaskType(row.task_type),
            assignee=row.assignee,
            status=TaskStatus(row.status),
            variables=row.variables if isinstance(row.variables, dict) else {},
            ai_recommendations=row.ai_recommendations if row.ai_recommendations else None,
            ai_predicted_duration_hours=row.ai_predicted_duration_hours,
            created_at=row.created_at,
            completed_at=row.completed_at
        )

    async def list_by_instance(
        self,
        instance_id: str,
        status: Optional[TaskStatus] = None
    ) -> List[Task]:
        """
        List tasks for instance

        Args:
            instance_id: Instance ID
            status: Filter by status (optional)

        Returns:
            List[Task]
        """
        query_str = """
            SELECT *
            FROM workflow.bpmn_tasks
            WHERE instance_id = :instance_id
        """

        params = {"instance_id": instance_id}

        if status:
            query_str += " AND status = :status"
            params["status"] = status.value

        query_str += " ORDER BY created_at"

        query = text(query_str)
        result = await self.session.execute(query, params)

        tasks = []
        for row in result.fetchall():
            tasks.append(Task(
                id=str(row.id),
                process_instance_id=str(row.instance_id),
                activity_id=row.activity_id,
                name=row.name,
                task_type=TaskType(row.task_type),
                assignee=row.assignee,
                status=TaskStatus(row.status),
                variables=row.variables if isinstance(row.variables, dict) else {},
                ai_recommendations=row.ai_recommendations if row.ai_recommendations else None,
                ai_predicted_duration_hours=row.ai_predicted_duration_hours,
                created_at=row.created_at,
                completed_at=row.completed_at
            ))

        return tasks

    async def list_by_assignee(
        self,
        tenant_id: str,
        assignee: str,
        status: Optional[TaskStatus] = TaskStatus.ACTIVE,
        limit: int = 100
    ) -> List[Task]:
        """
        List tasks assigned to user

        Args:
            tenant_id: Tenant identifier (for RLS)
            assignee: User identifier
            status: Filter by status (default: ACTIVE)
            limit: Max results

        Returns:
            List[Task]
        """
        query_str = """
            SELECT t.*
            FROM workflow.bpmn_tasks t
            JOIN workflow.bpmn_instances i ON t.instance_id = i.id
            WHERE i.tenant_id = :tenant_id
            AND t.assignee = :assignee
        """

        params = {
            "tenant_id": tenant_id,
            "assignee": assignee,
            "limit": limit
        }

        if status:
            query_str += " AND t.status = :status"
            params["status"] = status.value

        query_str += " ORDER BY t.created_at DESC LIMIT :limit"

        query = text(query_str)
        result = await self.session.execute(query, params)

        tasks = []
        for row in result.fetchall():
            tasks.append(Task(
                id=str(row.id),
                process_instance_id=str(row.instance_id),
                activity_id=row.activity_id,
                name=row.name,
                task_type=TaskType(row.task_type),
                assignee=row.assignee,
                status=TaskStatus(row.status),
                variables=row.variables if isinstance(row.variables, dict) else {},
                ai_recommendations=row.ai_recommendations if row.ai_recommendations else None,
                ai_predicted_duration_hours=row.ai_predicted_duration_hours,
                created_at=row.created_at,
                completed_at=row.completed_at
            ))

        return tasks

    async def update_status(
        self,
        task_id: str,
        status: TaskStatus,
        completed_at: Optional[datetime] = None
    ) -> bool:
        """
        Update task status

        Args:
            task_id: Task ID
            status: New status
            completed_at: Completion timestamp (if applicable)

        Returns:
            bool: True if updated
        """
        query_str = """
            UPDATE workflow.bpmn_tasks
            SET status = :status
        """

        params = {
            "task_id": task_id,
            "status": status.value if isinstance(status, TaskStatus) else status
        }

        if completed_at:
            query_str += ", completed_at = :completed_at"
            params["completed_at"] = completed_at

        query_str += " WHERE id = :task_id"

        query = text(query_str)
        result = await self.session.execute(query, params)
        await self.session.commit()

        return result.rowcount > 0

    async def assign(
        self,
        task_id: str,
        assignee: str
    ) -> bool:
        """
        Assign task to user

        Args:
            task_id: Task ID
            assignee: User identifier

        Returns:
            bool: True if updated
        """
        query = text("""
            UPDATE workflow.bpmn_tasks
            SET assignee = :assignee
            WHERE id = :task_id
        """)

        result = await self.session.execute(query, {
            "task_id": task_id,
            "assignee": assignee
        })
        await self.session.commit()

        return result.rowcount > 0

    async def update_variables(
        self,
        task_id: str,
        variables: Dict[str, Any],
        merge: bool = True
    ) -> bool:
        """
        Update task variables

        Args:
            task_id: Task ID
            variables: Variables to update
            merge: If True, merge with existing. If False, replace

        Returns:
            bool: True if updated
        """
        if merge:
            query = text("""
                UPDATE workflow.bpmn_tasks
                SET variables = variables || :new_variables::jsonb
                WHERE id = :task_id
            """)
        else:
            query = text("""
                UPDATE workflow.bpmn_tasks
                SET variables = :new_variables::jsonb
                WHERE id = :task_id
            """)

        result = await self.session.execute(query, {
            "task_id": task_id,
            "new_variables": json.dumps(variables)
        })
        await self.session.commit()

        return result.rowcount > 0

    async def update_ai_recommendations(
        self,
        task_id: str,
        recommendations: List[Dict[str, Any]]
    ) -> bool:
        """
        Update AI recommendations for task

        Args:
            task_id: Task ID
            recommendations: List of AI recommendations

        Returns:
            bool: True if updated
        """
        query = text("""
            UPDATE workflow.bpmn_tasks
            SET ai_recommendations = :recommendations::jsonb
            WHERE id = :task_id
        """)

        result = await self.session.execute(query, {
            "task_id": task_id,
            "recommendations": json.dumps(recommendations)
        })
        await self.session.commit()

        return result.rowcount > 0

    async def update_ai_prediction(
        self,
        task_id: str,
        predicted_duration_hours: float
    ) -> bool:
        """
        Update AI predicted duration

        Args:
            task_id: Task ID
            predicted_duration_hours: Predicted duration in hours

        Returns:
            bool: True if updated
        """
        query = text("""
            UPDATE workflow.bpmn_tasks
            SET ai_predicted_duration_hours = :predicted_duration_hours
            WHERE id = :task_id
        """)

        result = await self.session.execute(query, {
            "task_id": task_id,
            "predicted_duration_hours": predicted_duration_hours
        })
        await self.session.commit()

        return result.rowcount > 0

    async def complete(
        self,
        task_id: str,
        variables: Optional[Dict[str, Any]] = None,
        completed_at: Optional[datetime] = None
    ) -> bool:
        """
        Complete task

        Args:
            task_id: Task ID
            variables: Variables to merge
            completed_at: Completion timestamp (defaults to NOW)

        Returns:
            bool: True if updated
        """
        query_str = """
            UPDATE workflow.bpmn_tasks
            SET status = 'COMPLETED',
                completed_at = :completed_at
        """

        params = {
            "task_id": task_id,
            "completed_at": completed_at or datetime.utcnow()
        }

        if variables:
            query_str += ", variables = variables || :variables::jsonb"
            params["variables"] = json.dumps(variables)

        query_str += " WHERE id = :task_id"

        query = text(query_str)
        result = await self.session.execute(query, params)
        await self.session.commit()

        return result.rowcount > 0

    async def cancel_by_instance(
        self,
        instance_id: str
    ) -> int:
        """
        Cancel all active tasks for instance

        Args:
            instance_id: Instance ID

        Returns:
            int: Number of tasks cancelled
        """
        query = text("""
            UPDATE workflow.bpmn_tasks
            SET status = 'CANCELLED'
            WHERE instance_id = :instance_id
            AND status = 'ACTIVE'
        """)

        result = await self.session.execute(query, {"instance_id": instance_id})
        await self.session.commit()

        return result.rowcount

    async def get_active_count_by_assignee(
        self,
        tenant_id: str,
        assignee: str
    ) -> int:
        """
        Get count of active tasks for user

        Args:
            tenant_id: Tenant identifier
            assignee: User identifier

        Returns:
            int: Count of active tasks
        """
        query = text("""
            SELECT COUNT(*)
            FROM workflow.bpmn_tasks t
            JOIN workflow.bpmn_instances i ON t.instance_id = i.id
            WHERE i.tenant_id = :tenant_id
            AND t.assignee = :assignee
            AND t.status = 'ACTIVE'
        """)

        result = await self.session.execute(query, {
            "tenant_id": tenant_id,
            "assignee": assignee
        })
        count = result.scalar()

        return count or 0

    async def get_statistics(
        self,
        tenant_id: str,
        assignee: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get task statistics

        Args:
            tenant_id: Tenant identifier
            assignee: Filter by assignee (optional)

        Returns:
            Dict with statistics
        """
        query_str = """
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE t.status = 'ACTIVE') as active,
                COUNT(*) FILTER (WHERE t.status = 'COMPLETED') as completed,
                COUNT(*) FILTER (WHERE t.status = 'CANCELLED') as cancelled,
                AVG(EXTRACT(EPOCH FROM (t.completed_at - t.created_at)) / 3600)
                    FILTER (WHERE t.status = 'COMPLETED' AND t.completed_at IS NOT NULL)
                    as avg_duration_hours
            FROM workflow.bpmn_tasks t
            JOIN workflow.bpmn_instances i ON t.instance_id = i.id
            WHERE i.tenant_id = :tenant_id
        """

        params = {"tenant_id": tenant_id}

        if assignee:
            query_str += " AND t.assignee = :assignee"
            params["assignee"] = assignee

        query = text(query_str)
        result = await self.session.execute(query, params)
        row = result.fetchone()

        return {
            "total": row.total or 0,
            "active": row.active or 0,
            "completed": row.completed or 0,
            "cancelled": row.cancelled or 0,
            "avg_duration_hours": float(row.avg_duration_hours) if row.avg_duration_hours else None
        }

    async def delete(self, task_id: str) -> bool:
        """
        Delete task (hard delete)

        Args:
            task_id: Task ID

        Returns:
            bool: True if deleted
        """
        query = text("""
            DELETE FROM workflow.bpmn_tasks
            WHERE id = :task_id
        """)

        result = await self.session.execute(query, {"task_id": task_id})
        await self.session.commit()

        return result.rowcount > 0
