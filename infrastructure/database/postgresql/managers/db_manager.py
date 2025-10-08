"""
Enhanced Database Manager for AI-Powered BCM Platform
Supports multiple database levels and comprehensive features
"""

import os
from typing import Optional, Dict, Any, List
from urllib.parse import quote_plus
import psycopg2
import psycopg2.pool
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Base database manager with connection pooling and health checks
    Supports sync operations (for migrations, admin tasks)
    """

    def __init__(self, name: str, db_url: Optional[str] = None):
        self.name = name
        self.db_url = db_url or self._get_db_url()
        self.pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None

    def _get_db_url(self) -> str:
        """Get database URL from environment"""
        # URL-encode password if it contains special characters
        password = os.getenv("POSTGRES_PASSWORD", "K@x3ta9V8GK5rnW")
        encoded_password = quote_plus(password)

        host = os.getenv("POSTGRES_HOST", "aws-1-eu-north-1.pooler.supabase.com")
        port = os.getenv("POSTGRES_PORT", "5432")
        user = os.getenv("POSTGRES_USER", "postgres.tpdkhddtbhpoqzzgxfni")
        database = os.getenv("POSTGRES_DB", "postgres")

        return f"postgresql://{user}:{encoded_password}@{host}:{port}/{database}"

    def connect(self, min_conn: int = 2, max_conn: int = 10):
        """Initialize connection pool"""
        try:
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                min_conn,
                max_conn,
                self.db_url
            )
            logger.info(f"✅ {self.name} connection pool initialized ({min_conn}-{max_conn} connections)")
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.name} connection pool: {e}")
            raise

    def disconnect(self):
        """Close all connections in pool"""
        if self.pool:
            self.pool.closeall()
            logger.info(f"✅ {self.name} connection pool closed")

    @contextmanager
    def get_connection(self):
        """Get connection from pool (context manager)"""
        if not self.pool:
            raise RuntimeError(f"{self.name} not initialized. Call connect() first.")

        conn = self.pool.getconn()
        try:
            yield conn
        finally:
            self.pool.putconn(conn)

    @contextmanager
    def get_cursor(self, commit: bool = False):
        """Get cursor (context manager with auto-commit option)"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            try:
                yield cur
                if commit:
                    conn.commit()
            except Exception as e:
                conn.rollback()
                raise
            finally:
                cur.close()

    def execute(self, query: str, params: tuple = None, commit: bool = True) -> Optional[List]:
        """Execute query and return results"""
        with self.get_cursor(commit=commit) as cur:
            cur.execute(query, params)
            if cur.description:  # SELECT query
                return cur.fetchall()
            return None

    def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        health = {
            "name": self.name,
            "connected": False,
            "pool_size": 0,
            "active_connections": 0,
            "error": None
        }

        try:
            with self.get_cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                health["connected"] = result[0] == 1

                # Get pool stats
                if self.pool:
                    # Note: ThreadedConnectionPool doesn't expose these easily
                    # This is an approximation
                    health["pool_size"] = self.pool.maxconn

        except Exception as e:
            health["error"] = str(e)
            logger.error(f"{self.name} health check failed: {e}")

        return health


class SystemDBManager(DatabaseManager):
    """
    System Database Manager
    Handles: AI decision logs, embeddings, graph data
    """

    def __init__(self):
        # TODO: In production, use separate System DB
        # For now, use same Supabase with different schemas
        super().__init__("SystemDB")

    def log_ai_decision(self, decision_data: Dict[str, Any]):
        """Log AI decision to system DB"""
        # TODO: Implement when System DB schema is ready
        pass

    def store_embedding(self, text: str, embedding: List[float], metadata: Dict):
        """Store text embedding"""
        # TODO: Implement with pgvector
        pass


class PlatformDBManager(DatabaseManager):
    """
    Platform Database Manager
    Handles: Coordination, events, auth
    """

    def __init__(self):
        # TODO: In production, use separate Platform DB
        super().__init__("PlatformDB")

    def log_event(self, event_type: str, event_data: Dict[str, Any]):
        """Log platform event"""
        # TODO: Implement event logging
        pass


class BusinessDBManager(DatabaseManager):
    """
    Business Database Manager
    Handles: All BCM business data (organizations, users, BIA, Risk, etc.)
    """

    def __init__(self):
        super().__init__("BusinessDB")

    def get_organization(self, org_id: str) -> Optional[Dict]:
        """Get organization by ID"""
        result = self.execute(
            "SELECT * FROM public.organizations WHERE id = %s",
            (org_id,),
            commit=False
        )
        return dict(result[0]) if result else None

    def get_user_organizations(self, user_id: str) -> List[Dict]:
        """Get all organizations for user"""
        result = self.execute(
            """
            SELECT o.* FROM public.organizations o
            JOIN public.organization_users ou ON o.id = ou.organization_id
            WHERE ou.user_id = %s AND ou.is_active = true
            """,
            (user_id,),
            commit=False
        )
        return [dict(row) for row in result] if result else []


class RLSManager:
    """
    Row Level Security Manager
    Sets RLS context (current_user_id, tenant_id) for queries
    """

    @staticmethod
    def set_rls_context(cursor, user_id: str, tenant_id: str):
        """Set RLS context for current session"""
        cursor.execute("SET LOCAL app.current_user_id = %s", (user_id,))
        cursor.execute("SET LOCAL app.current_tenant_id = %s", (tenant_id,))

    @staticmethod
    def clear_rls_context(cursor):
        """Clear RLS context"""
        cursor.execute("RESET app.current_user_id")
        cursor.execute("RESET app.current_tenant_id")


class MigrationRunner:
    """
    Database Migration Runner
    Applies SQL migrations in order
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.migrations_path = "/Users/MD/AI-Platform-ISO/infrastructure/database/migrations_source"

    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations"""
        # Create migrations table if not exists
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS public.schema_migrations (
                version VARCHAR(255) PRIMARY KEY,
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """, commit=True)

        result = self.db.execute(
            "SELECT version FROM public.schema_migrations ORDER BY version",
            commit=False
        )
        return [row[0] for row in result] if result else []

    def apply_migration(self, migration_file: str):
        """Apply single migration"""
        import os

        migration_path = os.path.join(self.migrations_path, migration_file)

        with open(migration_path, 'r') as f:
            sql = f.read()

        # Extract version from filename (e.g., "001_schemas.sql" -> "001")
        version = migration_file.split('_')[0]

        # Apply migration in transaction
        with self.db.get_cursor(commit=True) as cur:
            cur.execute(sql)
            cur.execute(
                "INSERT INTO public.schema_migrations (version) VALUES (%s)",
                (version,)
            )

        logger.info(f"✅ Applied migration: {migration_file}")

    def run_pending_migrations(self):
        """Apply all pending migrations"""
        import os
        import glob

        applied = set(self.get_applied_migrations())

        # Get all migration files
        pattern = os.path.join(self.migrations_path, "*.sql")
        all_migrations = sorted(glob.glob(pattern))

        pending = []
        for migration_path in all_migrations:
            migration_file = os.path.basename(migration_path)
            version = migration_file.split('_')[0]

            if version not in applied:
                pending.append(migration_file)

        if not pending:
            logger.info("✅ No pending migrations")
            return

        logger.info(f"📄 Applying {len(pending)} pending migrations...")

        for migration_file in pending:
            try:
                self.apply_migration(migration_file)
            except Exception as e:
                logger.error(f"❌ Failed to apply {migration_file}: {e}")
                raise


# Global instances (initialized on startup)
system_db = SystemDBManager()
platform_db = PlatformDBManager()
business_db = BusinessDBManager()


async def initialize_all_databases():
    """Initialize all database connections"""
    system_db.connect()
    platform_db.connect()
    business_db.connect()
    logger.info("✅ All database connections initialized")


async def shutdown_all_databases():
    """Shutdown all database connections"""
    system_db.disconnect()
    platform_db.disconnect()
    business_db.disconnect()
    logger.info("✅ All database connections closed")


async def health_check_all() -> Dict[str, Any]:
    """Health check for all databases"""
    return {
        "system_db": system_db.health_check(),
        "platform_db": platform_db.health_check(),
        "business_db": business_db.health_check(),
    }
