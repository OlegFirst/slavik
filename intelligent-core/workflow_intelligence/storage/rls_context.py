"""
Row Level Security (RLS) Context Manager
Управляет tenant_id для изоляции на уровне БД
"""

from contextlib import asynccontextmanager
from typing import Optional, TYPE_CHECKING
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

if TYPE_CHECKING:
    from shared.database import DatabaseManager

logger = structlog.get_logger(__name__)


async def set_rls_context(session: AsyncSession, tenant_id: str) -> None:
    """
    Set RLS context for SQLAlchemy session

    Args:
        session: SQLAlchemy AsyncSession
        tenant_id: Tenant ID for RLS isolation
    """
    await session.execute(
        text("SET LOCAL app.current_tenant_id = :tenant_id"),
        {"tenant_id": tenant_id}
    )

    logger.debug("rls.context.set", tenant_id=tenant_id)


class RLSContext:
    """
    Context manager для установки tenant_id в PostgreSQL сессии

    Использование:
        async with RLSContext(connection, tenant_id):
            # Все запросы автоматически фильтруются по tenant_id
            result = await conn.fetch("SELECT * FROM workflow_contexts")
    """

    def __init__(
        self,
        connection: asyncpg.Connection,
        tenant_id: str,
        verify: bool = True
    ):
        """
        Args:
            connection: PostgreSQL connection
            tenant_id: Tenant ID для изоляции
            verify: Проверять что tenant_id установлен
        """
        self.connection = connection
        self.tenant_id = tenant_id
        self.verify = verify
        self.previous_tenant_id: Optional[str] = None

    async def __aenter__(self):
        """Установить tenant_id в начале контекста"""

        # Сохранить предыдущий tenant_id (если был)
        try:
            self.previous_tenant_id = await self.connection.fetchval(
                "SELECT current_setting('app.current_tenant_id', true)"
            )
        except:
            self.previous_tenant_id = None

        # Установить новый tenant_id
        await self.connection.execute(
            "SET LOCAL app.current_tenant_id = $1",
            self.tenant_id
        )

        # Верификация (опционально)
        if self.verify:
            actual_tenant_id = await self.connection.fetchval(
                "SELECT current_setting('app.current_tenant_id', true)"
            )

            if actual_tenant_id != self.tenant_id:
                raise RuntimeError(
                    f"RLS context failed to set tenant_id: "
                    f"expected {self.tenant_id}, got {actual_tenant_id}"
                )

        logger.debug(
            "rls.context.set",
            tenant_id=self.tenant_id,
            previous=self.previous_tenant_id
        )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Восстановить предыдущий tenant_id"""

        # Восстановить или сбросить
        if self.previous_tenant_id:
            await self.connection.execute(
                "SET LOCAL app.current_tenant_id = $1",
                self.previous_tenant_id
            )
        else:
            # Сбросить настройку
            try:
                await self.connection.execute(
                    "RESET app.current_tenant_id"
                )
            except:
                pass

        logger.debug(
            "rls.context.reset",
            tenant_id=self.tenant_id,
            restored_to=self.previous_tenant_id
        )


@asynccontextmanager
async def rls_context(
    connection: asyncpg.Connection,
    tenant_id: str,
    verify: bool = True
):
    """
    Async context manager для RLS

    Использование:
        async with rls_context(conn, "tenant_001"):
            # Все запросы изолированы по tenant_001
            rows = await conn.fetch("SELECT * FROM workflow_contexts")

    Args:
        connection: PostgreSQL connection
        tenant_id: Tenant ID
        verify: Проверять установку tenant_id
    """
    ctx = RLSContext(connection, tenant_id, verify)
    async with ctx:
        yield ctx


class RLSPoolContext:
    """
    RLS Context для connection pool

    Использование:
        async with RLSPoolContext(pool, tenant_id) as conn:
            # conn - это connection с установленным tenant_id
            rows = await conn.fetch("SELECT * FROM workflow_contexts")
    """

    def __init__(
        self,
        pool: asyncpg.Pool,
        tenant_id: str,
        verify: bool = True
    ):
        self.pool = pool
        self.tenant_id = tenant_id
        self.verify = verify
        self.connection: Optional[asyncpg.Connection] = None

    async def __aenter__(self) -> asyncpg.Connection:
        """Получить connection и установить tenant_id"""

        # Получить connection из pool
        self.connection = await self.pool.acquire()

        # Установить tenant_id
        await self.connection.execute(
            "SET LOCAL app.current_tenant_id = $1",
            self.tenant_id
        )

        # Верификация
        if self.verify:
            actual_tenant_id = await self.connection.fetchval(
                "SELECT current_setting('app.current_tenant_id', true)"
            )

            if actual_tenant_id != self.tenant_id:
                raise RuntimeError(
                    f"RLS pool context failed to set tenant_id: "
                    f"expected {self.tenant_id}, got {actual_tenant_id}"
                )

        logger.debug(
            "rls.pool_context.acquired",
            tenant_id=self.tenant_id
        )

        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Вернуть connection в pool и сбросить tenant_id"""

        if self.connection:
            # Сбросить tenant_id перед возвратом в pool
            try:
                await self.connection.execute(
                    "RESET app.current_tenant_id"
                )
            except:
                pass

            # Вернуть в pool
            await self.pool.release(self.connection)

            logger.debug(
                "rls.pool_context.released",
                tenant_id=self.tenant_id
            )


@asynccontextmanager
async def rls_pool_context(
    pool: asyncpg.Pool,
    tenant_id: str,
    verify: bool = True
):
    """
    Async context manager для RLS с pool

    Использование:
        async with rls_pool_context(pool, "tenant_001") as conn:
            # conn изолирован по tenant_001
            rows = await conn.fetch("SELECT * FROM workflow_contexts")

    Args:
        pool: asyncpg connection pool
        tenant_id: Tenant ID
        verify: Проверять установку tenant_id
    """
    ctx = RLSPoolContext(pool, tenant_id, verify)
    async with ctx as conn:
        yield conn


async def verify_rls_enabled(session: AsyncSession) -> dict:
    """
    Проверить что RLS включен на всех таблицах

    Returns:
        {
            "workflow_contexts": {"enabled": True, "forced": False},
            "workflow_cases": {"enabled": True, "forced": False},
            ...
        }
    """
    result_obj = await session.execute(text("""
        SELECT
            c.relname::text AS table_name,
            c.relrowsecurity AS rls_enabled,
            c.relforcerowsecurity AS rls_forced
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'workflow_intelligence'
          AND c.relkind = 'r'
        ORDER BY c.relname
    """))

    rows = result_obj.fetchall()

    result = {}
    for row in rows:
        result[row[0]] = {
            'enabled': row[1],
            'forced': row[2]
        }

    return result


async def test_rls_isolation(
    db_manager: "DatabaseManager",
    tenant1: str = "tenant_test_1",
    tenant2: str = "tenant_test_2"
) -> dict:
    """
    Тест изоляции RLS

    Проверяет что:
    1. Tenant1 видит только свои данные
    2. Tenant2 видит только свои данные
    3. Tenant1 НЕ видит данные Tenant2

    Returns:
        {
            "success": bool,
            "details": {...}
        }
    """

    # 1. Создать тестовые данные для двух tenant'ов
    async for session in db_manager.get_session():
        await set_rls_context(session, tenant1)
        await session.execute(
            text("""
                INSERT INTO workflow_intelligence.workflow_contexts
                    (workflow_id, module, tenant_id, context)
                VALUES (:workflow_id, 'test', :tenant_id, '{"test": 1}')
                ON CONFLICT (workflow_id, tenant_id) DO NOTHING
            """),
            {"workflow_id": f"test_wf_{tenant1}", "tenant_id": tenant1}
        )
        await session.commit()
        break

    async for session in db_manager.get_session():
        await set_rls_context(session, tenant2)
        await session.execute(
            text("""
                INSERT INTO workflow_intelligence.workflow_contexts
                    (workflow_id, module, tenant_id, context)
                VALUES (:workflow_id, 'test', :tenant_id, '{"test": 2}')
                ON CONFLICT (workflow_id, tenant_id) DO NOTHING
            """),
            {"workflow_id": f"test_wf_{tenant2}", "tenant_id": tenant2}
        )
        await session.commit()
        break

    # 2. Проверить изоляцию
    async for session in db_manager.get_session():
        await set_rls_context(session, tenant1)
        result1 = await session.execute(text("""
            SELECT workflow_id, tenant_id
            FROM workflow_intelligence.workflow_contexts
            WHERE workflow_id LIKE 'test_wf_%'
        """))
        rows_tenant1 = result1.fetchall()
        break

    async for session in db_manager.get_session():
        await set_rls_context(session, tenant2)
        result2 = await session.execute(text("""
            SELECT workflow_id, tenant_id
            FROM workflow_intelligence.workflow_contexts
            WHERE workflow_id LIKE 'test_wf_%'
        """))
        rows_tenant2 = result2.fetchall()
        break

    # 3. Проверить результаты
    tenant1_sees_only_own = all(
        row[1] == tenant1
        for row in rows_tenant1
    )

    tenant2_sees_only_own = all(
        row[1] == tenant2
        for row in rows_tenant2
    )

    tenant1_cannot_see_tenant2 = not any(
        row[1] == tenant2
        for row in rows_tenant1
    )

    success = (
        tenant1_sees_only_own and
        tenant2_sees_only_own and
        tenant1_cannot_see_tenant2
    )

    # 4. Cleanup
    async for session in db_manager.get_session():
        await set_rls_context(session, tenant1)
        await session.execute(
            text("""
                DELETE FROM workflow_intelligence.workflow_contexts
                WHERE workflow_id = :workflow_id
            """),
            {"workflow_id": f"test_wf_{tenant1}"}
        )
        await session.commit()
        break

    async for session in db_manager.get_session():
        await set_rls_context(session, tenant2)
        await session.execute(
            text("""
                DELETE FROM workflow_intelligence.workflow_contexts
                WHERE workflow_id = :workflow_id
            """),
            {"workflow_id": f"test_wf_{tenant2}"}
        )
        await session.commit()
        break

    return {
        "success": success,
        "details": {
            "tenant1_isolation": tenant1_sees_only_own,
            "tenant2_isolation": tenant2_sees_only_own,
            "cross_tenant_blocked": tenant1_cannot_see_tenant2,
            "tenant1_rows": len(rows_tenant1),
            "tenant2_rows": len(rows_tenant2)
        }
    }
