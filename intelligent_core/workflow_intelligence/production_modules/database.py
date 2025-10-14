"""
Database Layer for Process Framework

Provides connection pool and CRUD operations for:
- Process definitions
- Process instances
- Step executions
- Document templates
- Generated documents

Uses psycopg2 connection pool for scalability and performance.

Author: AI Platform Team
Date: 2025-10-11
"""

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor, Json
from contextlib import contextmanager
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


# =====================================================
# Database Configuration
# =====================================================

class DatabaseConfig:
    """Database configuration"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "workflow_intelligence",
        user: str = "postgres",
        password: str = "postgres",
        min_connections: int = 5,
        max_connections: int = 20
    ):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.min_connections = min_connections
        self.max_connections = max_connections

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for psycopg2"""
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.user,
            "password": self.password
        }


# =====================================================
# Process Framework Database
# =====================================================

class ProcessFrameworkDatabase:
    """
    Database layer for Process Framework

    Provides:
    - Connection pooling
    - CRUD operations for all tables
    - Transaction management
    - Error handling
    """

    def __init__(self, config: DatabaseConfig):
        """Initialize database with connection pool"""
        self.config = config

        try:
            self.pool = ThreadedConnectionPool(
                minconn=config.min_connections,
                maxconn=config.max_connections,
                **config.to_dict()
            )
            logger.info(
                f"Database pool initialized: {config.min_connections}-{config.max_connections} connections"
            )
        except psycopg2.Error as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """
        Get connection from pool

        Usage:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(...)
        """
        conn = None
        try:
            conn = self.pool.getconn()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                self.pool.putconn(conn)

    def close(self):
        """Close all connections in pool"""
        if self.pool:
            self.pool.closeall()
            logger.info("Database pool closed")

    # =====================================================
    # Process Definitions
    # =====================================================

    def create_process_definition(
        self,
        process_id: str,
        name: str,
        version: str,
        start_step_id: str,
        end_step_ids: List[str],
        description: Optional[str] = None,
        category: Optional[str] = None,
        iso_clause: Optional[str] = None,
        compliance_requirements: Optional[List[str]] = None,
        owner: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """Create process definition, returns UUID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO process_definitions (
                    process_id, name, version, description, category, iso_clause,
                    compliance_requirements, start_step_id, end_step_ids, owner, tags
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id
            """, (
                process_id, name, version, description, category, iso_clause,
                Json(compliance_requirements or []),
                start_step_id,
                Json(end_step_ids),
                owner,
                Json(tags or [])
            ))

            result = cursor.fetchone()
            process_def_id = str(result[0])

            logger.info(f"Created process definition: {process_id} v{version} ({process_def_id})")
            return process_def_id

    def get_process_definition(self, process_id: str, version: Optional[str] = None) -> Optional[Dict]:
        """Get process definition by process_id (and optional version)"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            if version:
                cursor.execute("""
                    SELECT * FROM process_definitions
                    WHERE process_id = %s AND version = %s
                """, (process_id, version))
            else:
                # Get latest version
                cursor.execute("""
                    SELECT * FROM process_definitions
                    WHERE process_id = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (process_id,))

            result = cursor.fetchone()
            return dict(result) if result else None

    def list_process_definitions(self) -> List[Dict]:
        """List all process definitions"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("""
                SELECT * FROM process_definitions
                ORDER BY created_at DESC
            """)

            return [dict(row) for row in cursor.fetchall()]

    # =====================================================
    # Process Steps
    # =====================================================

    def create_process_step(
        self,
        process_definition_id: str,
        step_id: str,
        name: str,
        step_type: str,
        next_steps: List[str],
        allowed_roles: List[str],
        description: Optional[str] = None,
        transition_conditions: Optional[Dict] = None,
        ai_agent: Optional[str] = None,
        document_template: Optional[str] = None,
        auto_approve: bool = False,
        estimated_duration_minutes: Optional[int] = None,
        sla_hours: Optional[int] = None,
        form_fields: Optional[List[Dict]] = None,
        step_order: Optional[int] = None
    ) -> str:
        """Create process step, returns UUID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO process_steps (
                    process_definition_id, step_id, name, description, step_type,
                    next_steps, transition_conditions, allowed_roles, ai_agent,
                    document_template, auto_approve, estimated_duration_minutes,
                    sla_hours, form_fields, step_order
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id
            """, (
                process_definition_id, step_id, name, description, step_type,
                Json(next_steps), Json(transition_conditions or {}),
                Json(allowed_roles), ai_agent, document_template, auto_approve,
                estimated_duration_minutes, sla_hours, Json(form_fields or []),
                step_order
            ))

            result = cursor.fetchone()
            step_uuid = str(result[0])

            logger.debug(f"Created step: {step_id} for process {process_definition_id}")
            return step_uuid

    def get_process_steps(self, process_definition_id: str) -> List[Dict]:
        """Get all steps for a process definition"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("""
                SELECT * FROM process_steps
                WHERE process_definition_id = %s
                ORDER BY step_order ASC, created_at ASC
            """, (process_definition_id,))

            return [dict(row) for row in cursor.fetchall()]

    # =====================================================
    # Process Instances
    # =====================================================

    def create_process_instance(
        self,
        instance_id: str,
        process_definition_id: str,
        status: str,
        current_step_id: str,
        started_by: str,
        data: Optional[Dict] = None,
        participants: Optional[List[str]] = None
    ) -> str:
        """Create process instance, returns UUID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO process_instances (
                    instance_id, process_definition_id, status, current_step_id,
                    started_by, data, participants
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id
            """, (
                instance_id, process_definition_id, status, current_step_id,
                started_by, Json(data or {}), Json(participants or [])
            ))

            result = cursor.fetchone()
            instance_uuid = str(result[0])

            logger.info(f"Created process instance: {instance_id} by {started_by}")
            return instance_uuid

    def get_process_instance(self, instance_id: str) -> Optional[Dict]:
        """Get process instance by instance_id"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("""
                SELECT * FROM process_instances
                WHERE instance_id = %s
            """, (instance_id,))

            result = cursor.fetchone()
            return dict(result) if result else None

    def update_process_instance(
        self,
        instance_id: str,
        status: Optional[str] = None,
        current_step_id: Optional[str] = None,
        data: Optional[Dict] = None,
        step_history: Optional[List[Dict]] = None,
        completed_at: Optional[datetime] = None
    ):
        """Update process instance"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Build dynamic update query
            updates = []
            params = []

            if status is not None:
                updates.append("status = %s")
                params.append(status)

            if current_step_id is not None:
                updates.append("current_step_id = %s")
                params.append(current_step_id)

            if data is not None:
                updates.append("data = %s")
                params.append(Json(data))

            if step_history is not None:
                updates.append("step_history = %s")
                params.append(Json(step_history))

            if completed_at is not None:
                updates.append("completed_at = %s")
                params.append(completed_at)

            if not updates:
                return  # Nothing to update

            # Always update updated_at
            updates.append("updated_at = NOW()")

            query = f"""
                UPDATE process_instances
                SET {', '.join(updates)}
                WHERE instance_id = %s
            """
            params.append(instance_id)

            cursor.execute(query, params)

            logger.debug(f"Updated process instance: {instance_id}")

    def list_process_instances(
        self,
        process_definition_id: Optional[str] = None,
        status: Optional[str] = None,
        started_by: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """List process instances with optional filters"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            conditions = []
            params = []

            if process_definition_id:
                conditions.append("process_definition_id = %s")
                params.append(process_definition_id)

            if status:
                conditions.append("status = %s")
                params.append(status)

            if started_by:
                conditions.append("started_by = %s")
                params.append(started_by)

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

            query = f"""
                SELECT * FROM process_instances
                {where_clause}
                ORDER BY started_at DESC
                LIMIT %s
            """
            params.append(limit)

            cursor.execute(query, params)

            return [dict(row) for row in cursor.fetchall()]

    # =====================================================
    # Step Executions
    # =====================================================

    def create_step_execution(
        self,
        process_instance_id: str,
        step_id: str,
        executed_by: str,
        result: str,
        input_data: Optional[Dict] = None,
        output_data: Optional[Dict] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
        ai_agent_used: Optional[str] = None,
        ai_confidence: Optional[float] = None
    ) -> str:
        """Create step execution record, returns UUID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO step_executions (
                    process_instance_id, step_id, executed_by, input_data,
                    output_data, result, error_message, duration_ms,
                    ai_agent_used, ai_confidence
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id
            """, (
                process_instance_id, step_id, executed_by,
                Json(input_data or {}), Json(output_data or {}),
                result, error_message, duration_ms,
                ai_agent_used, ai_confidence
            ))

            result = cursor.fetchone()
            execution_uuid = str(result[0])

            logger.debug(f"Recorded step execution: {step_id} by {executed_by}")
            return execution_uuid

    def get_step_executions(self, process_instance_id: str) -> List[Dict]:
        """Get all step executions for a process instance"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("""
                SELECT * FROM step_executions
                WHERE process_instance_id = %s
                ORDER BY executed_at ASC
            """, (process_instance_id,))

            return [dict(row) for row in cursor.fetchall()]

    # =====================================================
    # Analytics Views
    # =====================================================

    def get_process_completion_stats(self) -> List[Dict]:
        """Get process completion statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("SELECT * FROM process_completion_stats")

            return [dict(row) for row in cursor.fetchall()]

    def get_step_execution_stats(self) -> List[Dict]:
        """Get step execution statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("SELECT * FROM step_execution_stats")

            return [dict(row) for row in cursor.fetchall()]

    def get_document_generation_stats(self) -> List[Dict]:
        """Get document generation statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("SELECT * FROM document_generation_stats")

            return [dict(row) for row in cursor.fetchall()]

    # =====================================================
    # Utility Methods
    # =====================================================

    def execute_raw_query(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """Execute raw SQL query (use with caution)"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute(query, params or ())

            return [dict(row) for row in cursor.fetchall()]

    def health_check(self) -> bool:
        """Check database connection health"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# =====================================================
# Singleton Instance
# =====================================================

_database: Optional[ProcessFrameworkDatabase] = None


def get_database() -> ProcessFrameworkDatabase:
    """Get global database instance"""
    if _database is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _database


def init_database(config: DatabaseConfig) -> ProcessFrameworkDatabase:
    """Initialize global database instance"""
    global _database
    _database = ProcessFrameworkDatabase(config)
    logger.info("Process Framework database initialized")
    return _database


def close_database():
    """Close global database instance"""
    global _database
    if _database:
        _database.close()
        _database = None
        logger.info("Process Framework database closed")
