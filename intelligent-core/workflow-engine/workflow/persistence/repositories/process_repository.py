"""
Process Repository

CRUD operations for BPMN processes (definitions)
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, insert, update, delete
from datetime import datetime
import uuid

from ...bpmn.models import BPMNProcess


class ProcessRepository:
    """
    Repository for BPMN process definitions

    Manages workflow.bpmn_processes table
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, process: BPMNProcess) -> str:
        """
        Create new process definition

        Args:
            process: BPMNProcess model

        Returns:
            str: Process ID
        """
        process_id = process.id or str(uuid.uuid4())

        query = text("""
            INSERT INTO workflow.bpmn_processes (
                id, tenant_id, module, name, description, bpmn_xml,
                version, is_active, created_by, created_at
            )
            VALUES (
                :id, :tenant_id, :module, :name, :description, :bpmn_xml,
                :version, :is_active, :created_by, NOW()
            )
            RETURNING id
        """)

        result = await self.session.execute(query, {
            "id": process_id,
            "tenant_id": process.tenant_id,
            "module": process.module,
            "name": process.name,
            "description": process.description,
            "bpmn_xml": process.bpmn_xml,
            "version": process.version,
            "is_active": process.is_active,
            "created_by": process.created_by
        })

        await self.session.commit()

        return process_id

    async def get_by_id(self, process_id: str) -> Optional[BPMNProcess]:
        """
        Get process by ID

        Args:
            process_id: Process ID

        Returns:
            BPMNProcess or None
        """
        query = text("""
            SELECT *
            FROM workflow.bpmn_processes
            WHERE id = :process_id
        """)

        result = await self.session.execute(query, {"process_id": process_id})
        row = result.fetchone()

        if not row:
            return None

        return BPMNProcess(
            id=str(row.id),
            tenant_id=row.tenant_id,
            module=row.module,
            name=row.name,
            description=row.description,
            bpmn_xml=row.bpmn_xml,
            version=row.version,
            is_active=row.is_active,
            created_by=row.created_by,
            created_at=row.created_at,
            updated_at=row.updated_at
        )

    async def list_by_tenant(
        self,
        tenant_id: str,
        module: Optional[str] = None,
        active_only: bool = True
    ) -> List[BPMNProcess]:
        """
        List processes for tenant

        Args:
            tenant_id: Tenant identifier
            module: Filter by module (optional)
            active_only: Only return active processes

        Returns:
            List[BPMNProcess]
        """
        query_str = """
            SELECT *
            FROM workflow.bpmn_processes
            WHERE tenant_id = :tenant_id
        """

        params = {"tenant_id": tenant_id}

        if module:
            query_str += " AND module = :module"
            params["module"] = module

        if active_only:
            query_str += " AND is_active = true"

        query_str += " ORDER BY created_at DESC"

        query = text(query_str)
        result = await self.session.execute(query, params)

        processes = []
        for row in result.fetchall():
            processes.append(BPMNProcess(
                id=str(row.id),
                tenant_id=row.tenant_id,
                module=row.module,
                name=row.name,
                description=row.description,
                bpmn_xml=row.bpmn_xml,
                version=row.version,
                is_active=row.is_active,
                created_by=row.created_by,
                created_at=row.created_at,
                updated_at=row.updated_at
            ))

        return processes

    async def update(self, process_id: str, updates: dict) -> bool:
        """
        Update process

        Args:
            process_id: Process ID
            updates: Dictionary of fields to update

        Returns:
            bool: True if updated
        """
        # Build SET clause dynamically
        set_clauses = []
        params = {"process_id": process_id}

        for key, value in updates.items():
            if key in ["name", "description", "bpmn_xml", "version", "is_active"]:
                set_clauses.append(f"{key} = :{key}")
                params[key] = value

        if not set_clauses:
            return False

        set_clauses.append("updated_at = NOW()")

        query_str = f"""
            UPDATE workflow.bpmn_processes
            SET {', '.join(set_clauses)}
            WHERE id = :process_id
        """

        query = text(query_str)
        result = await self.session.execute(query, params)
        await self.session.commit()

        return result.rowcount > 0

    async def delete(self, process_id: str) -> bool:
        """
        Delete process (soft delete - sets is_active = false)

        Args:
            process_id: Process ID

        Returns:
            bool: True if deleted
        """
        query = text("""
            UPDATE workflow.bpmn_processes
            SET is_active = false, updated_at = NOW()
            WHERE id = :process_id
        """)

        result = await self.session.execute(query, {"process_id": process_id})
        await self.session.commit()

        return result.rowcount > 0

    async def hard_delete(self, process_id: str) -> bool:
        """
        Hard delete process (removes from database)

        Warning: This will cascade delete all instances and tasks!

        Args:
            process_id: Process ID

        Returns:
            bool: True if deleted
        """
        query = text("""
            DELETE FROM workflow.bpmn_processes
            WHERE id = :process_id
        """)

        result = await self.session.execute(query, {"process_id": process_id})
        await self.session.commit()

        return result.rowcount > 0
