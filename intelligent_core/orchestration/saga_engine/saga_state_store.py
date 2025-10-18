"""
Saga State Store
================

Persistent storage for saga execution state to enable recovery and monitoring.
Supports multiple backends (Redis, PostgreSQL, etc.) with a common interface.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod
import json
import logging
from .saga_definition import (
    SagaExecution, SagaStepExecution, SagaStatus, SagaStepStatus
)

logger = logging.getLogger(__name__)


class SagaStateStore(ABC):
    """Abstract base class for saga state storage"""

    @abstractmethod
    async def save_saga(self, saga: SagaExecution) -> None:
        """Save or update saga execution state"""
        pass

    @abstractmethod
    async def get_saga(self, saga_id: str) -> Optional[SagaExecution]:
        """Retrieve saga execution state by ID"""
        pass

    @abstractmethod
    async def save_step(self, saga_id: str, step: SagaStepExecution) -> None:
        """Save or update step execution state"""
        pass

    @abstractmethod
    async def get_step(self, saga_id: str, step_name: str) -> Optional[SagaStepExecution]:
        """Retrieve step execution state"""
        pass

    @abstractmethod
    async def list_sagas(
        self,
        status: Optional[SagaStatus] = None,
        tenant_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[SagaExecution]:
        """List saga executions with optional filtering"""
        pass

    @abstractmethod
    async def delete_saga(self, saga_id: str) -> bool:
        """Delete saga execution state"""
        pass

    @abstractmethod
    async def cleanup_old_sagas(self, older_than_days: int = 30) -> int:
        """Clean up old completed/failed sagas. Returns count deleted."""
        pass


class InMemorySagaStateStore(SagaStateStore):
    """
    In-memory saga state store for development and testing.
    NOT suitable for production (data lost on restart).
    """

    def __init__(self):
        self.sagas: Dict[str, SagaExecution] = {}
        self.logger = logger

    async def save_saga(self, saga: SagaExecution) -> None:
        """Save saga to memory"""
        self.sagas[saga.saga_id] = saga
        self.logger.debug(f"Saved saga {saga.saga_id} to memory store")

    async def get_saga(self, saga_id: str) -> Optional[SagaExecution]:
        """Get saga from memory"""
        return self.sagas.get(saga_id)

    async def save_step(self, saga_id: str, step: SagaStepExecution) -> None:
        """Save step execution state"""
        saga = self.sagas.get(saga_id)
        if saga:
            saga.step_executions[step.step_name] = step
            self.logger.debug(f"Saved step {step.step_name} for saga {saga_id}")
        else:
            self.logger.warning(f"Saga {saga_id} not found for step save")

    async def get_step(self, saga_id: str, step_name: str) -> Optional[SagaStepExecution]:
        """Get step execution state"""
        saga = self.sagas.get(saga_id)
        if saga:
            return saga.step_executions.get(step_name)
        return None

    async def list_sagas(
        self,
        status: Optional[SagaStatus] = None,
        tenant_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[SagaExecution]:
        """List sagas from memory"""
        sagas = list(self.sagas.values())

        # Filter by status
        if status:
            sagas = [s for s in sagas if s.status == status]

        # Filter by tenant
        if tenant_id:
            sagas = [s for s in sagas if s.tenant_id == tenant_id]

        # Sort by started_at descending
        sagas.sort(key=lambda x: x.started_at or datetime.min, reverse=True)

        # Apply pagination
        return sagas[offset:offset + limit]

    async def delete_saga(self, saga_id: str) -> bool:
        """Delete saga from memory"""
        if saga_id in self.sagas:
            del self.sagas[saga_id]
            self.logger.debug(f"Deleted saga {saga_id} from memory store")
            return True
        return False

    async def cleanup_old_sagas(self, older_than_days: int = 30) -> int:
        """Clean up old sagas"""
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(days=older_than_days)
        to_delete = []

        for saga_id, saga in self.sagas.items():
            if saga.completed_at and saga.completed_at < cutoff:
                if saga.status in [SagaStatus.COMPLETED, SagaStatus.COMPENSATED]:
                    to_delete.append(saga_id)

        for saga_id in to_delete:
            del self.sagas[saga_id]

        self.logger.info(f"Cleaned up {len(to_delete)} old sagas")
        return len(to_delete)


class RedisSagaStateStore(SagaStateStore):
    """
    Redis-based saga state store for production use.
    Provides persistence and fast access.
    """

    def __init__(self, redis_client, key_prefix: str = "saga:"):
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.logger = logger

    def _saga_key(self, saga_id: str) -> str:
        """Get Redis key for saga"""
        return f"{self.key_prefix}{saga_id}"

    def _index_key(self, index_type: str) -> str:
        """Get Redis key for index"""
        return f"{self.key_prefix}index:{index_type}"

    async def save_saga(self, saga: SagaExecution) -> None:
        """Save saga to Redis"""
        key = self._saga_key(saga.saga_id)
        data = json.dumps(saga.to_dict(), default=str)

        # Save saga data
        await self.redis.set(key, data)

        # Update indices
        # Status index
        await self.redis.sadd(
            self._index_key(f"status:{saga.status.value}"),
            saga.saga_id
        )

        # Tenant index
        if saga.tenant_id:
            await self.redis.sadd(
                self._index_key(f"tenant:{saga.tenant_id}"),
                saga.saga_id
            )

        # Set TTL for completed sagas (30 days)
        if saga.status in [SagaStatus.COMPLETED, SagaStatus.COMPENSATED]:
            await self.redis.expire(key, 30 * 24 * 60 * 60)

        self.logger.debug(f"Saved saga {saga.saga_id} to Redis")

    async def get_saga(self, saga_id: str) -> Optional[SagaExecution]:
        """Get saga from Redis"""
        key = self._saga_key(saga_id)
        data = await self.redis.get(key)

        if not data:
            return None

        # Deserialize
        saga_dict = json.loads(data)
        return self._deserialize_saga(saga_dict)

    async def save_step(self, saga_id: str, step: SagaStepExecution) -> None:
        """Save step by updating the saga"""
        saga = await self.get_saga(saga_id)
        if saga:
            saga.step_executions[step.step_name] = step
            await self.save_saga(saga)
        else:
            self.logger.warning(f"Saga {saga_id} not found for step save")

    async def get_step(self, saga_id: str, step_name: str) -> Optional[SagaStepExecution]:
        """Get step from saga"""
        saga = await self.get_saga(saga_id)
        if saga:
            return saga.step_executions.get(step_name)
        return None

    async def list_sagas(
        self,
        status: Optional[SagaStatus] = None,
        tenant_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[SagaExecution]:
        """List sagas from Redis"""
        saga_ids = set()

        # Get saga IDs from indices
        if status:
            ids = await self.redis.smembers(self._index_key(f"status:{status.value}"))
            saga_ids = set(ids) if ids else set()
        elif tenant_id:
            ids = await self.redis.smembers(self._index_key(f"tenant:{tenant_id}"))
            saga_ids = set(ids) if ids else set()
        else:
            # Get all saga keys
            pattern = f"{self.key_prefix}*"
            keys = await self.redis.keys(pattern)
            saga_ids = {key.decode().replace(self.key_prefix, '') for key in keys
                       if not key.decode().startswith(f"{self.key_prefix}index:")}

        # Fetch sagas
        sagas = []
        for saga_id in saga_ids:
            saga = await self.get_saga(saga_id)
            if saga:
                sagas.append(saga)

        # Sort by started_at
        sagas.sort(key=lambda x: x.started_at or datetime.min, reverse=True)

        # Apply pagination
        return sagas[offset:offset + limit]

    async def delete_saga(self, saga_id: str) -> bool:
        """Delete saga from Redis"""
        saga = await self.get_saga(saga_id)
        if not saga:
            return False

        # Remove from indices
        await self.redis.srem(
            self._index_key(f"status:{saga.status.value}"),
            saga_id
        )
        if saga.tenant_id:
            await self.redis.srem(
                self._index_key(f"tenant:{saga.tenant_id}"),
                saga_id
            )

        # Delete saga
        key = self._saga_key(saga_id)
        result = await self.redis.delete(key)

        self.logger.debug(f"Deleted saga {saga_id} from Redis")
        return result > 0

    async def cleanup_old_sagas(self, older_than_days: int = 30) -> int:
        """Clean up old sagas from Redis"""
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(days=older_than_days)

        # Get completed and compensated sagas
        saga_ids = set()
        for status in [SagaStatus.COMPLETED, SagaStatus.COMPENSATED]:
            ids = await self.redis.smembers(self._index_key(f"status:{status.value}"))
            if ids:
                saga_ids.update(ids)

        # Check each saga's completion time
        deleted_count = 0
        for saga_id in saga_ids:
            saga = await self.get_saga(saga_id)
            if saga and saga.completed_at and saga.completed_at < cutoff:
                if await self.delete_saga(saga_id):
                    deleted_count += 1

        self.logger.info(f"Cleaned up {deleted_count} old sagas from Redis")
        return deleted_count

    def _deserialize_saga(self, data: Dict[str, Any]) -> SagaExecution:
        """Convert dictionary to SagaExecution"""
        # Deserialize step executions
        step_executions = {}
        for step_name, step_data in data.get('step_executions', {}).items():
            step_executions[step_name] = self._deserialize_step(step_data)

        return SagaExecution(
            saga_id=data['saga_id'],
            definition_name=data['definition_name'],
            definition_version=data['definition_version'],
            status=SagaStatus(data['status']),
            started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            step_executions=step_executions,
            execution_context=data.get('execution_context', {}),
            result=data.get('result'),
            error=data.get('error'),
            tenant_id=data.get('tenant_id'),
            correlation_id=data.get('correlation_id'),
            parent_saga_id=data.get('parent_saga_id'),
            metadata=data.get('metadata', {})
        )

    def _deserialize_step(self, data: Dict[str, Any]) -> SagaStepExecution:
        """Convert dictionary to SagaStepExecution"""
        return SagaStepExecution(
            step_id=data['step_id'],
            step_name=data['step_name'],
            saga_id=data['saga_id'],
            status=SagaStepStatus(data['status']),
            started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            attempts=data.get('attempts', 0),
            max_attempts=data.get('max_attempts', 3),
            result=data.get('result'),
            error=data.get('error'),
            error_details=data.get('error_details'),
            compensation_started_at=datetime.fromisoformat(data['compensation_started_at']) if data.get('compensation_started_at') else None,
            compensation_completed_at=datetime.fromisoformat(data['compensation_completed_at']) if data.get('compensation_completed_at') else None,
            compensation_result=data.get('compensation_result'),
            compensation_error=data.get('compensation_error'),
            idempotency_key=data.get('idempotency_key'),
            output_context=data.get('output_context', {})
        )


class PostgresSagaStateStore(SagaStateStore):
    """
    PostgreSQL-based saga state store for production use.
    Provides full ACID guarantees and complex querying.
    """

    def __init__(self, db_pool):
        """
        Initialize with asyncpg database pool.

        Requires tables:
        - sagas: Main saga execution table
        - saga_steps: Step execution table
        """
        self.db = db_pool
        self.logger = logger

    async def save_saga(self, saga: SagaExecution) -> None:
        """Save saga to PostgreSQL"""
        query = """
            INSERT INTO sagas (
                saga_id, definition_name, definition_version, status,
                started_at, completed_at, execution_context, result, error,
                tenant_id, correlation_id, parent_saga_id, metadata
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            ON CONFLICT (saga_id) DO UPDATE SET
                status = EXCLUDED.status,
                completed_at = EXCLUDED.completed_at,
                execution_context = EXCLUDED.execution_context,
                result = EXCLUDED.result,
                error = EXCLUDED.error,
                metadata = EXCLUDED.metadata
        """

        await self.db.execute(
            query,
            saga.saga_id,
            saga.definition_name,
            saga.definition_version,
            saga.status.value,
            saga.started_at,
            saga.completed_at,
            json.dumps(saga.execution_context),
            json.dumps(saga.result) if saga.result else None,
            saga.error,
            saga.tenant_id,
            saga.correlation_id,
            saga.parent_saga_id,
            json.dumps(saga.metadata)
        )

        # Save all steps
        for step in saga.step_executions.values():
            await self.save_step(saga.saga_id, step)

        self.logger.debug(f"Saved saga {saga.saga_id} to PostgreSQL")

    async def get_saga(self, saga_id: str) -> Optional[SagaExecution]:
        """Get saga from PostgreSQL"""
        query = """
            SELECT saga_id, definition_name, definition_version, status,
                   started_at, completed_at, execution_context, result, error,
                   tenant_id, correlation_id, parent_saga_id, metadata
            FROM sagas
            WHERE saga_id = $1
        """

        row = await self.db.fetchrow(query, saga_id)
        if not row:
            return None

        # Get steps
        steps_query = """
            SELECT * FROM saga_steps WHERE saga_id = $1
        """
        step_rows = await self.db.fetch(steps_query, saga_id)

        step_executions = {}
        for step_row in step_rows:
            step = self._row_to_step(step_row)
            step_executions[step.step_name] = step

        return SagaExecution(
            saga_id=row['saga_id'],
            definition_name=row['definition_name'],
            definition_version=row['definition_version'],
            status=SagaStatus(row['status']),
            started_at=row['started_at'],
            completed_at=row['completed_at'],
            step_executions=step_executions,
            execution_context=json.loads(row['execution_context']) if row['execution_context'] else {},
            result=json.loads(row['result']) if row['result'] else None,
            error=row['error'],
            tenant_id=row['tenant_id'],
            correlation_id=row['correlation_id'],
            parent_saga_id=row['parent_saga_id'],
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )

    async def save_step(self, saga_id: str, step: SagaStepExecution) -> None:
        """Save step to PostgreSQL"""
        query = """
            INSERT INTO saga_steps (
                step_id, step_name, saga_id, status, started_at, completed_at,
                attempts, max_attempts, result, error, error_details,
                compensation_started_at, compensation_completed_at,
                compensation_result, compensation_error,
                idempotency_key, output_context
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
            ON CONFLICT (saga_id, step_name) DO UPDATE SET
                status = EXCLUDED.status,
                completed_at = EXCLUDED.completed_at,
                attempts = EXCLUDED.attempts,
                result = EXCLUDED.result,
                error = EXCLUDED.error,
                error_details = EXCLUDED.error_details,
                compensation_started_at = EXCLUDED.compensation_started_at,
                compensation_completed_at = EXCLUDED.compensation_completed_at,
                compensation_result = EXCLUDED.compensation_result,
                compensation_error = EXCLUDED.compensation_error,
                output_context = EXCLUDED.output_context
        """

        await self.db.execute(
            query,
            step.step_id,
            step.step_name,
            saga_id,
            step.status.value,
            step.started_at,
            step.completed_at,
            step.attempts,
            step.max_attempts,
            json.dumps(step.result) if step.result else None,
            step.error,
            json.dumps(step.error_details) if step.error_details else None,
            step.compensation_started_at,
            step.compensation_completed_at,
            json.dumps(step.compensation_result) if step.compensation_result else None,
            step.compensation_error,
            step.idempotency_key,
            json.dumps(step.output_context)
        )

    async def get_step(self, saga_id: str, step_name: str) -> Optional[SagaStepExecution]:
        """Get step from PostgreSQL"""
        query = """
            SELECT * FROM saga_steps
            WHERE saga_id = $1 AND step_name = $2
        """

        row = await self.db.fetchrow(query, saga_id, step_name)
        if not row:
            return None

        return self._row_to_step(row)

    async def list_sagas(
        self,
        status: Optional[SagaStatus] = None,
        tenant_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[SagaExecution]:
        """List sagas from PostgreSQL"""
        conditions = []
        params = []
        param_idx = 1

        if status:
            conditions.append(f"status = ${param_idx}")
            params.append(status.value)
            param_idx += 1

        if tenant_id:
            conditions.append(f"tenant_id = ${param_idx}")
            params.append(tenant_id)
            param_idx += 1

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
            SELECT saga_id FROM sagas
            WHERE {where_clause}
            ORDER BY started_at DESC
            LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """
        params.extend([limit, offset])

        rows = await self.db.fetch(query, *params)

        sagas = []
        for row in rows:
            saga = await self.get_saga(row['saga_id'])
            if saga:
                sagas.append(saga)

        return sagas

    async def delete_saga(self, saga_id: str) -> bool:
        """Delete saga from PostgreSQL"""
        # Delete steps first (foreign key constraint)
        await self.db.execute("DELETE FROM saga_steps WHERE saga_id = $1", saga_id)

        # Delete saga
        result = await self.db.execute("DELETE FROM sagas WHERE saga_id = $1", saga_id)

        self.logger.debug(f"Deleted saga {saga_id} from PostgreSQL")
        return result.split()[-1] != '0'

    async def cleanup_old_sagas(self, older_than_days: int = 30) -> int:
        """Clean up old sagas from PostgreSQL"""
        query = """
            DELETE FROM sagas
            WHERE completed_at < NOW() - INTERVAL '%s days'
            AND status IN ('completed', 'compensated')
        """

        result = await self.db.execute(query, older_than_days)
        deleted_count = int(result.split()[-1])

        self.logger.info(f"Cleaned up {deleted_count} old sagas from PostgreSQL")
        return deleted_count

    def _row_to_step(self, row) -> SagaStepExecution:
        """Convert database row to SagaStepExecution"""
        return SagaStepExecution(
            step_id=row['step_id'],
            step_name=row['step_name'],
            saga_id=row['saga_id'],
            status=SagaStepStatus(row['status']),
            started_at=row['started_at'],
            completed_at=row['completed_at'],
            attempts=row['attempts'],
            max_attempts=row['max_attempts'],
            result=json.loads(row['result']) if row['result'] else None,
            error=row['error'],
            error_details=json.loads(row['error_details']) if row['error_details'] else None,
            compensation_started_at=row['compensation_started_at'],
            compensation_completed_at=row['compensation_completed_at'],
            compensation_result=json.loads(row['compensation_result']) if row['compensation_result'] else None,
            compensation_error=row['compensation_error'],
            idempotency_key=row['idempotency_key'],
            output_context=json.loads(row['output_context']) if row['output_context'] else {}
        )
