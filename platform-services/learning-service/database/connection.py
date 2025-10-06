"""
Learning Service - Database Connection & Session Management
Supabase PostgreSQL with SSL
"""

import os
import ssl
from pathlib import Path
from typing import AsyncGenerator
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from .models import Base

# Load environment variables from AI-Platform-ISO/.env
env_path = Path(__file__).parent.parent.parent.parent.parent / ".env"
load_dotenv(env_path)

# Database URL from environment (Supabase)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres.tpdkhddtbhpoqzzgxfni:K%40x3ta9V8GK5rnW@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"
)

# Convert to asyncpg driver for SQLAlchemy
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Connection Pool Settings
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"

# SSL context for asyncpg - Supabase pooler uses self-signed cert
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False  # Supabase pooler cert issue
ssl_context.verify_mode = ssl.CERT_NONE  # Don't verify cert for pooler

# Connection arguments for asyncpg
_connect_args = {
    "ssl": ssl_context,
    "server_settings": {
        "application_name": "learning_service",
        "search_path": "learning,public"
    }
}

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=DB_ECHO,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=DB_POOL_TIMEOUT,
    pool_pre_ping=True,  # Validate connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    connect_args=_connect_args
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI endpoints

    Usage:
        @app.get("/api/learning/programs")
        async def list_programs(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_db_with_context(
    tenant_id: str = None,
    user_id: str = None
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session with context variables set

    Sets PostgreSQL session variables for RLS:
    - app.current_tenant_id
    - app.current_user_id

    Usage:
        async def endpoint(
            current_user: dict = Depends(get_current_user),
            db: AsyncSession = Depends(get_db_with_context)
        ):
            # RLS automatically filters by tenant
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            # Set context for Row Level Security
            if tenant_id:
                await session.execute(
                    text("SET LOCAL app.current_tenant_id = :tenant_id"),
                    {"tenant_id": str(tenant_id)}
                )

            if user_id:
                await session.execute(
                    text("SET LOCAL app.current_user_id = :user_id"),
                    {"user_id": str(user_id)}
                )

            yield session
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initialize database connection (check connectivity)"""
    import logging
    logger = logging.getLogger(__name__)

    logger.info("Initializing database connection...")

    try:
        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"✅ Connected to PostgreSQL: {version}")

            # Check if learning schema exists
            result = await conn.execute(
                text("""
                    SELECT schema_name
                    FROM information_schema.schemata
                    WHERE schema_name = 'learning'
                """)
            )
            schema = result.scalar()

            if schema:
                logger.info("✅ Learning schema found")
            else:
                logger.warning("⚠️  Learning schema not found - run migrations")

    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise

async def close_db():
    """Close database connection"""
    import logging
    logger = logging.getLogger(__name__)

    logger.info("Closing database connection...")
    await engine.dispose()
    logger.info("✅ Database connection closed")

async def check_db_health() -> dict:
    """
    Check database health

    Returns:
        {
            "status": "healthy" | "unhealthy",
            "latency_ms": float,
            "pool_size": int,
            "pool_overflow": int
        }
    """
    import time
    import logging
    logger = logging.getLogger(__name__)

    try:
        start = time.time()
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        latency = (time.time() - start) * 1000

        pool = engine.pool

        return {
            "status": "healthy",
            "latency_ms": round(latency, 2),
            "pool_size": pool.size(),
            "pool_overflow": pool.overflow(),
            "checkedout": pool.checkedout()
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
