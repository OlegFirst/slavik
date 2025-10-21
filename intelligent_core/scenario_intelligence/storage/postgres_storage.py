"""
PostgreSQL Storage для Scenario Intelligence

Постоянное хранилище сценариев в PostgreSQL с полной поддержкой:
- CRUD операции
- Поиск и фильтрация
- Full-text search
- RLS для multi-tenancy
- Транзакции
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

try:
    import asyncpg
    from asyncpg import Pool, Connection
except ImportError:
    asyncpg = None
    Pool = None
    Connection = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgresScenarioStorage:
    """
    PostgreSQL Storage для сценариев

    Использует schema: scenario_intelligence
    Таблица: scenarios

    Features:
    - Async операции через asyncpg
    - Full-text search
    - JSONB для гибкого хранения
    - RLS для security
    - Индексы для performance
    """

    def __init__(self, connection_string: str = None, pool: Pool = None):
        """
        Initialize PostgreSQL storage

        Args:
            connection_string: PostgreSQL connection string
            pool: Existing connection pool (если уже создан)
        """
        if asyncpg is None:
            raise ImportError("asyncpg is required: pip install asyncpg")

        self.connection_string = connection_string
        self.pool: Optional[Pool] = pool
        self._external_pool = pool is not None  # Не закрывать внешний pool

    async def initialize(self):
        """Создать connection pool"""
        if self.pool is None and self.connection_string:
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            logger.info(" PostgreSQL pool created")

    async def close(self):
        """Закрыть connection pool"""
        if self.pool and not self._external_pool:
            await self.pool.close()
            logger.info(" PostgreSQL pool closed")

    async def register(self, scenario: Dict[str, Any], organization_id: Optional[str] = None) -> bool:
        """
        Сохранить сценарий в PostgreSQL

        Args:
            scenario: Сценарий (с или без обертки 'scenario')
            organization_id: ID организации (None = platform scenario)

        Returns:
            True если успешно
        """
        if not self.pool:
            logger.error("Pool not initialized")
            return False

        # Handle both formats
        if 'scenario' in scenario:
            scenario = scenario['scenario']

        meta = scenario.get('meta', {})
        scenario_id = meta.get('id')

        if not scenario_id:
            logger.error("Scenario без ID")
            return False

        try:
            async with self.pool.acquire() as conn:
                # Извлечь поля
                level = meta.get('level')
                scenario_type = meta.get('type', 'unknown')
                version = meta.get('version', '1.0.0')

                ownership = scenario.get('ownership', {})
                module = ownership.get('module')
                subsystem = ownership.get('subsystem')
                pillar = ownership.get('pillar')

                # Сохранить весь сценарий как JSONB в content
                # asyncpg поддерживает прямую передачу dict как JSONB
                content = scenario

                # INSERT or UPDATE (используя существующую схему)
                query = """
                    INSERT INTO scenario_intelligence.scenarios (
                        id, level, type, version,
                        module, subsystem, pillar,
                        content
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb)
                    ON CONFLICT (id) DO UPDATE SET
                        level = EXCLUDED.level,
                        type = EXCLUDED.type,
                        version = EXCLUDED.version,
                        module = EXCLUDED.module,
                        subsystem = EXCLUDED.subsystem,
                        pillar = EXCLUDED.pillar,
                        content = EXCLUDED.content,
                        updated_at = NOW()
                    RETURNING id, created_at, updated_at
                """

                result = await conn.fetchrow(
                    query,
                    scenario_id, level, scenario_type, version,
                    module, subsystem, pillar,
                    json.dumps(content)  # asyncpg требует JSON string для ::jsonb cast
                )

                logger.info(
                    f" Saved scenario: {scenario_id} "
                    f"(level {level}, type {scenario_type}, "
                    f"created: {result['created_at']}, updated: {result['updated_at']})"
                )

                return True

        except Exception as e:
            logger.error(f" Failed to save scenario {scenario_id}: {e}")
            return False

    async def get_scenario_by_id(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить сценарий по ID

        Args:
            scenario_id: ID сценария

        Returns:
            Сценарий (JSONB data) или None
        """
        if not self.pool:
            logger.error("Pool not initialized")
            return None

        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT content
                    FROM scenario_intelligence.scenarios
                    WHERE id = $1
                """

                row = await conn.fetchrow(query, scenario_id)

                if row:
                    # content может быть строкой или dict, парсим если нужно
                    content = row['content']
                    if isinstance(content, str):
                        return json.loads(content)
                    return content
                else:
                    return None

        except Exception as e:
            logger.error(f" Failed to get scenario {scenario_id}: {e}")
            return None

    async def get_scenario(
        self,
        scenario_id: str,
        level: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Получить сценарий по ID и опционально level

        Args:
            scenario_id: ID сценария
            level: Уровень (опционально)

        Returns:
            Сценарий или None
        """
        if not self.pool:
            logger.error("Pool not initialized")
            return None

        try:
            async with self.pool.acquire() as conn:
                if level is not None:
                    query = """
                        SELECT content
                        FROM scenario_intelligence.scenarios
                        WHERE id = $1 AND level = $2
                    """
                    row = await conn.fetchrow(query, scenario_id, level)
                else:
                    query = """
                        SELECT content
                        FROM scenario_intelligence.scenarios
                        WHERE id = $1
                    """
                    row = await conn.fetchrow(query, scenario_id)

                if row:
                    content = row['content']
                    if isinstance(content, str):
                        return json.loads(content)
                    return content
                else:
                    return None

        except Exception as e:
            logger.error(f" Failed to get scenario {scenario_id}: {e}")
            return None

    async def find_scenarios(
        self,
        level: Optional[int] = None,
        type: Optional[str] = None,
        module: Optional[str] = None,
        service: Optional[str] = None,
        subsystem: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Найти сценарии по фильтрам

        Args:
            level: Уровень
            type: Тип
            module: Модуль
            service: Сервис
            subsystem: Подсистема
            query: Full-text search запрос
            limit: Максимум результатов

        Returns:
            Список сценариев
        """
        if not self.pool:
            logger.error("Pool not initialized")
            return []

        try:
            async with self.pool.acquire() as conn:
                # Простой фильтр (search_scenarios function может не существовать в старой схеме)
                conditions = []
                params = []
                param_idx = 1

                if level is not None:
                    conditions.append(f"level = ${param_idx}")
                    params.append(level)
                    param_idx += 1

                if type:
                    conditions.append(f"type = ${param_idx}")
                    params.append(type)
                    param_idx += 1

                if module:
                    conditions.append(f"module = ${param_idx}")
                    params.append(module)
                    param_idx += 1

                if subsystem:
                    conditions.append(f"subsystem = ${param_idx}")
                    params.append(subsystem)
                    param_idx += 1

                # Full-text search через search_vector
                if query:
                    conditions.append(f"search_vector @@ plainto_tsquery('english', ${param_idx})")
                    params.append(query)
                    param_idx += 1

                where_clause = " AND ".join(conditions) if conditions else "TRUE"

                sql = f"""
                    SELECT content
                    FROM scenario_intelligence.scenarios
                    WHERE {where_clause}
                    ORDER BY created_at DESC
                    LIMIT ${param_idx}
                """
                params.append(limit)

                rows = await conn.fetch(sql, *params)

                # Парсим content если строка
                scenarios = []
                for row in rows:
                    content = row['content']
                    if isinstance(content, str):
                        scenarios.append(json.loads(content))
                    else:
                        scenarios.append(content)
                return scenarios

        except Exception as e:
            logger.error(f" Failed to find scenarios: {e}")
            return []

    async def list_all(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Получить все сценарии

        Args:
            limit: Максимум результатов

        Returns:
            Список сценариев
        """
        if not self.pool:
            logger.error("Pool not initialized")
            return []

        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT content
                    FROM scenario_intelligence.scenarios
                    ORDER BY created_at DESC
                    LIMIT $1
                """

                rows = await conn.fetch(query, limit)

                # Парсим content если строка
                scenarios = []
                for row in rows:
                    content = row['content']
                    if isinstance(content, str):
                        scenarios.append(json.loads(content))
                    else:
                        scenarios.append(content)
                return scenarios

        except Exception as e:
            logger.error(f" Failed to list all scenarios: {e}")
            return []

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику по сценариям

        Returns:
            Статистика (используя функцию get_statistics())
        """
        if not self.pool:
            logger.error("Pool not initialized")
            return {}

        try:
            async with self.pool.acquire() as conn:
                # Простая статистика (функция get_statistics может не существовать)
                query = """
                    SELECT
                        COUNT(*) as total_scenarios,
                        jsonb_object_agg(
                            COALESCE(level::text, 'unknown'),
                            level_count
                        ) FILTER (WHERE level IS NOT NULL) as by_level,
                        jsonb_object_agg(
                            COALESCE(type, 'unknown'),
                            type_count
                        ) FILTER (WHERE type IS NOT NULL) as by_type,
                        jsonb_object_agg(
                            COALESCE(module, 'unknown'),
                            module_count
                        ) FILTER (WHERE module IS NOT NULL) as by_module
                    FROM (
                        SELECT
                            level,
                            type,
                            module,
                            COUNT(*) OVER (PARTITION BY level) as level_count,
                            COUNT(*) OVER (PARTITION BY type) as type_count,
                            COUNT(*) OVER (PARTITION BY module) as module_count
                        FROM scenario_intelligence.scenarios
                    ) stats
                    LIMIT 1
                """
                row = await conn.fetchrow(query)

                if row:
                    return {
                        'total_scenarios': row['total_scenarios'],
                        'by_level': row['by_level'] or {},
                        'by_type': row['by_type'] or {},
                        'by_module': row['by_module'] or {}
                    }
                else:
                    return {}

        except Exception as e:
            logger.error(f" Failed to get statistics: {e}")
            return {}

    async def delete_scenario(self, scenario_id: str) -> bool:
        """
        Удалить сценарий

        Args:
            scenario_id: ID сценария

        Returns:
            True если успешно
        """
        if not self.pool:
            logger.error("Pool not initialized")
            return False

        try:
            async with self.pool.acquire() as conn:
                query = """
                    DELETE FROM scenario_intelligence.scenarios
                    WHERE id = $1
                    RETURNING id
                """

                result = await conn.fetchrow(query, scenario_id)

                if result:
                    logger.info(f" Deleted scenario: {scenario_id}")
                    return True
                else:
                    logger.warning(f"️ Scenario not found: {scenario_id}")
                    return False

        except Exception as e:
            logger.error(f" Failed to delete scenario {scenario_id}: {e}")
            return False

    async def bulk_register(
        self,
        scenarios: List[Dict[str, Any]],
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Массовое сохранение сценариев (транзакция)

        Args:
            scenarios: Список сценариев
            organization_id: ID организации

        Returns:
            {'success': count, 'failed': count, 'errors': [...]}
        """
        if not self.pool:
            logger.error("Pool not initialized")
            return {'success': 0, 'failed': len(scenarios), 'errors': ['Pool not initialized']}

        success_count = 0
        failed_count = 0
        errors = []

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                for scenario in scenarios:
                    try:
                        # Переиспользуем логику register
                        if 'scenario' in scenario:
                            scenario = scenario['scenario']

                        meta = scenario.get('meta', {})
                        scenario_id = meta.get('id')

                        if not scenario_id:
                            failed_count += 1
                            errors.append(f"Scenario without ID")
                            continue

                        # Извлечь поля
                        level = meta.get('level')
                        scenario_type = meta.get('type', 'unknown')
                        version = meta.get('version', '1.0.0')

                        ownership = scenario.get('ownership', {})
                        module = ownership.get('module')
                        subsystem = ownership.get('subsystem')
                        pillar = ownership.get('pillar')

                        content = scenario

                        query = """
                            INSERT INTO scenario_intelligence.scenarios (
                                id, level, type, version,
                                module, subsystem, pillar,
                                content
                            )
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb)
                            ON CONFLICT (id) DO UPDATE SET
                                level = EXCLUDED.level,
                                type = EXCLUDED.type,
                                version = EXCLUDED.version,
                                module = EXCLUDED.module,
                                subsystem = EXCLUDED.subsystem,
                                pillar = EXCLUDED.pillar,
                                content = EXCLUDED.content,
                                updated_at = NOW()
                        """

                        await conn.execute(
                            query,
                            scenario_id, level, scenario_type, version,
                            module, subsystem, pillar,
                            json.dumps(content)  # asyncpg требует JSON string для ::jsonb cast
                        )

                        success_count += 1

                    except Exception as e:
                        failed_count += 1
                        errors.append(f"{scenario_id}: {str(e)}")

        logger.info(f" Bulk register: {success_count} success, {failed_count} failed")

        return {
            'success': success_count,
            'failed': failed_count,
            'errors': errors
        }


# Test
async def main():
    """Test PostgreSQL Storage"""
    import os

    # Из переменной окружения или hardcode для теста
    DATABASE_URL = os.getenv("DATABASE_URL",
        "postgresql://postgres.tpdkhddtbhpoqzzgxfni:K@x3ta9V8GK5rnW@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"
    )

    storage = PostgresScenarioStorage(connection_string=DATABASE_URL)

    try:
        await storage.initialize()

        # Тестовый сценарий
        test_scenario = {
            'meta': {
                'id': 'test-postgres-vault-store',
                'level': 1,
                'type': 'functional',
                'version': '1.0.0'
            },
            'ownership': {
                'module': 'vault',
                'service': 'vault-service'
            },
            'description': {
                'title': 'Test PostgreSQL Vault Store',
                'summary': 'Testing PostgreSQL storage integration'
            },
            'steps': []
        }

        # Register
        success = await storage.register(test_scenario)
        print(f"\n Register: {success}")

        # Get by ID
        scenario = await storage.get_scenario_by_id('test-postgres-vault-store')
        print(f" Get by ID: {scenario['meta']['id']}")

        # Find by filters
        scenarios = await storage.find_scenarios(level=1, type='functional')
        print(f" Find by filters: {len(scenarios)} scenarios")

        # Full-text search
        scenarios = await storage.find_scenarios(query='vault')
        print(f" Full-text search: {len(scenarios)} scenarios")

        # Statistics
        stats = await storage.get_statistics()
        print(f" Statistics: {stats}")

        # Delete
        # deleted = await storage.delete_scenario('test-postgres-vault-store')
        # print(f" Delete: {deleted}")

    finally:
        await storage.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
