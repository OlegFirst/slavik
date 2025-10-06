"""
Row Level Security (RLS) Context Manager
Управляет tenant_id для изоляции на уровне БД
"""

from contextlib import asynccontextmanager
from typing import Optional
import asyncpg
import structlog

logger = structlog.get_logger(__name__)


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


async def verify_rls_enabled(connection: asyncpg.Connection) -> dict:
    """
    Проверить что RLS включен на всех таблицах

    Returns:
        {
            "workflow_contexts": {"enabled": True, "forced": False},
            "workflow_cases": {"enabled": True, "forced": False},
            ...
        }
    """
    rows = await connection.fetch("""
        SELECT
            c.relname::text AS table_name,
            c.relrowsecurity AS rls_enabled,
            c.relforcerowsecurity AS rls_forced
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'workflow_intelligence'
          AND c.relkind = 'r'
        ORDER BY c.relname
    """)

    result = {}
    for row in rows:
        result[row['table_name']] = {
            'enabled': row['rls_enabled'],
            'forced': row['rls_forced']
        }

    return result


async def test_rls_isolation(
    pool: asyncpg.Pool,
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
    async with rls_pool_context(pool, tenant1) as conn:
        await conn.execute("""
            INSERT INTO workflow_intelligence.workflow_contexts
                (workflow_id, module, tenant_id, context)
            VALUES ($1, 'test', $2, '{"test": 1}')
            ON CONFLICT (workflow_id, tenant_id) DO NOTHING
        """, f"test_wf_{tenant1}", tenant1)

    async with rls_pool_context(pool, tenant2) as conn:
        await conn.execute("""
            INSERT INTO workflow_intelligence.workflow_contexts
                (workflow_id, module, tenant_id, context)
            VALUES ($1, 'test', $2, '{"test": 2}')
            ON CONFLICT (workflow_id, tenant_id) DO NOTHING
        """, f"test_wf_{tenant2}", tenant2)

    # 2. Проверить изоляцию
    async with rls_pool_context(pool, tenant1) as conn:
        rows_tenant1 = await conn.fetch("""
            SELECT workflow_id, tenant_id
            FROM workflow_intelligence.workflow_contexts
            WHERE workflow_id LIKE 'test_wf_%'
        """)

    async with rls_pool_context(pool, tenant2) as conn:
        rows_tenant2 = await conn.fetch("""
            SELECT workflow_id, tenant_id
            FROM workflow_intelligence.workflow_contexts
            WHERE workflow_id LIKE 'test_wf_%'
        """)

    # 3. Проверить результаты
    tenant1_sees_only_own = all(
        row['tenant_id'] == tenant1
        for row in rows_tenant1
    )

    tenant2_sees_only_own = all(
        row['tenant_id'] == tenant2
        for row in rows_tenant2
    )

    tenant1_cannot_see_tenant2 = not any(
        row['tenant_id'] == tenant2
        for row in rows_tenant1
    )

    success = (
        tenant1_sees_only_own and
        tenant2_sees_only_own and
        tenant1_cannot_see_tenant2
    )

    # 4. Cleanup
    async with rls_pool_context(pool, tenant1) as conn:
        await conn.execute("""
            DELETE FROM workflow_intelligence.workflow_contexts
            WHERE workflow_id = $1
        """, f"test_wf_{tenant1}")

    async with rls_pool_context(pool, tenant2) as conn:
        await conn.execute("""
            DELETE FROM workflow_intelligence.workflow_contexts
            WHERE workflow_id = $1
        """, f"test_wf_{tenant2}")

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
