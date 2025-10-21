"""
Supabase Client Manager
Unified client for PostgreSQL + Auth + Storage
"""

import os
from typing import Optional, Dict, Any
from supabase import create_client, Client
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


class SupabaseManager:
    """
    Manages Supabase connection for:
    - PostgreSQL (via SQLAlchemy)
    - Auth (via Supabase client)
    - Storage (via Supabase client)
    """

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.database_url = os.getenv("DATABASE_URL")

        # Supabase client (for Auth & Storage)
        self.client: Optional[Client] = None

        # SQLAlchemy engine (for PostgreSQL)
        self.engine = None
        self.session_factory = None

    async def connect(self):
        """Initialize Supabase client and database engine"""

        # 1. Initialize Supabase client
        try:
            self.client = create_client(
                self.supabase_url,
                self.supabase_service_key  # Use service role for backend
            )
            logger.info(" Supabase client initialized")
        except Exception as e:
            logger.error(f" Failed to initialize Supabase client: {e}")
            raise

        # 2. Initialize SQLAlchemy async engine
        try:
            # Convert postgresql:// to postgresql+asyncpg://
            async_db_url = self.database_url.replace(
                "postgresql://",
                "postgresql+asyncpg://"
            )

            # Pool settings (only if not using NullPool)
            pool_settings = {}
            if os.getenv("DEBUG") != "true":
                pool_settings = {
                    "pool_size": int(os.getenv("DB_POOL_SIZE", 20)),
                    "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", 10)),
                    "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", 30)),
                }

            self.engine = create_async_engine(
                async_db_url,
                echo=os.getenv("DB_ECHO", "false").lower() == "true",
                poolclass=NullPool if os.getenv("DEBUG") == "true" else None,
                **pool_settings
            )

            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            # Test connection
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))

            logger.info(" PostgreSQL connection pool initialized")

        except Exception as e:
            logger.error(f" Failed to connect to PostgreSQL: {e}")
            raise

    async def disconnect(self):
        """Close database connections"""
        if self.engine:
            await self.engine.dispose()
            logger.info(" Database connections closed")

    async def get_session(self) -> AsyncSession:
        """Get async database session"""
        if not self.session_factory:
            raise RuntimeError("Database not initialized. Call connect() first.")
        return self.session_factory()

    async def health_check(self) -> Dict[str, Any]:
        """Check health of all Supabase services"""
        health = {
            "postgres": False,
            "auth": False,
            "storage": False
        }

        # Check PostgreSQL
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                health["postgres"] = result.scalar() == 1
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")

        # Check Auth (try to get user count)
        try:
            # This will fail if auth is not working
            response = self.client.auth.admin.list_users()
            health["auth"] = True
        except Exception as e:
            logger.error(f"Auth health check failed: {e}")

        # Check Storage (try to list buckets)
        try:
            buckets = self.client.storage.list_buckets()
            health["storage"] = True
        except Exception as e:
            logger.error(f"Storage health check failed: {e}")

        return health

    # Auth methods
    def sign_up(self, email: str, password: str, user_metadata: Optional[Dict] = None):
        """Sign up new user (requires email confirmation disabled in Supabase)"""
        return self.client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": user_metadata} if user_metadata else {}
        })

    def sign_in(self, email: str, password: str):
        """Sign in user"""
        return self.client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

    def get_user(self, jwt_token: str):
        """Get user from JWT token"""
        return self.client.auth.get_user(jwt_token)

    def verify_jwt(self, jwt_token: str):
        """Verify JWT token"""
        try:
            user = self.client.auth.get_user(jwt_token)
            return user is not None
        except:
            return False

    # Storage methods
    def upload_file(self, bucket: str, path: str, file_data: bytes):
        """Upload file to storage"""
        return self.client.storage.from_(bucket).upload(path, file_data)

    def get_public_url(self, bucket: str, path: str):
        """Get public URL for file"""
        return self.client.storage.from_(bucket).get_public_url(path)

    def create_bucket(self, name: str, public: bool = False):
        """Create storage bucket"""
        return self.client.storage.create_bucket(name, {"public": public})


# Global instance
supabase_manager = SupabaseManager()


# FastAPI dependency
async def get_db_session() -> AsyncSession:
    """FastAPI dependency for database session"""
    async with supabase_manager.get_session() as session:
        yield session
