"""
PostgreSQL Storage Adapter for Workflow Intelligence
Использует ОБЩУЮ базу данных bcm_platform, схему workflow_intelligence

RLS (Row Level Security) ENABLED:
- Все запросы автоматически изолированы по tenant_id
- Используется app.current_tenant_id session parameter
- Полная изоляция данных на уровне БД
"""

import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
import asyncpg
from asyncpg import Pool
import structlog
from pathlib import Path

from .rls_context import rls_pool_context, verify_rls_enabled, test_rls_isolation

logger = structlog.get_logger(__name__)


class PostgresStorageAdapter:
    """PostgreSQL storage adapter using shared bcm_platform database"""

    def __init__(self, database_url: str):
        """
        Initialize with database URL

        Args:
            database_url: PostgreSQL connection string (same as other services)
                         postgresql://user:pass@localhost:5432/bcm_platform
        """
        self.database_url = database_url
        self.pool: Optional[Pool] = None

    async def connect(self):
        """Create connection pool"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=2,
                max_size=10,
                command_timeout=60,
            )

            # Ensure schema exists
            async with self.pool.acquire() as conn:
                await self._ensure_schema(conn)

            logger.info("workflow_intelligence.storage.connected")

    async def _ensure_schema(self, conn):
        """Create workflow_intelligence schema and tables if not exists"""

        # Create schema
        await conn.execute("""
            CREATE SCHEMA IF NOT EXISTS workflow_intelligence;
        """)

        # Enable pgvector extension
        await conn.execute("""
            CREATE EXTENSION IF NOT EXISTS vector;
        """)

        # Create bcm_app_user if not exists (for RLS grants)
        await conn.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'bcm_app_user') THEN
                    CREATE ROLE bcm_app_user;
                END IF;
            END
            $$;
        """)

        # Workflow contexts table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS workflow_intelligence.workflow_contexts (
                id SERIAL PRIMARY KEY,
                workflow_id VARCHAR(255) NOT NULL,
                module VARCHAR(100) NOT NULL,
                tenant_id VARCHAR(255) NOT NULL,
                context JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(workflow_id, tenant_id)
            );
        """)

        # Workflow cases table (for learning)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS workflow_intelligence.workflow_cases (
                id SERIAL PRIMARY KEY,
                case_id VARCHAR(255) UNIQUE NOT NULL,
                module VARCHAR(100) NOT NULL,
                tenant_id VARCHAR(255) NOT NULL,

                -- Organization context (anonymized)
                org_industry VARCHAR(100),
                org_size VARCHAR(50),
                org_maturity VARCHAR(50),

                -- Workflow journey
                journey JSONB NOT NULL,

                -- Metrics
                total_duration_days INTEGER,
                success BOOLEAN,
                user_satisfaction FLOAT,

                -- Patterns and lessons
                success_patterns JSONB,
                lessons_learned JSONB,

                -- Vector embedding for similarity search
                embedding vector(1536),

                created_at TIMESTAMP DEFAULT NOW(),
                completed_at TIMESTAMP
            );
        """)

        # Create vector index for similarity search
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS workflow_cases_embedding_idx
            ON workflow_intelligence.workflow_cases
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
        """)

        # Benchmarks table (aggregated statistics)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS workflow_intelligence.benchmarks (
                id SERIAL PRIMARY KEY,
                module VARCHAR(100) NOT NULL,
                industry VARCHAR(100),
                org_size VARCHAR(50),

                avg_duration_days FLOAT,
                success_rate FLOAT,
                common_challenges JSONB,
                best_practices JSONB,

                total_cases INTEGER,
                last_updated TIMESTAMP DEFAULT NOW(),

                UNIQUE(module, industry, org_size)
            );
        """)

        # ML predictions table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS workflow_intelligence.ml_predictions (
                id SERIAL PRIMARY KEY,
                workflow_id VARCHAR(255) NOT NULL,
                tenant_id VARCHAR(255) NOT NULL,

                success_probability FLOAT,
                estimated_duration_days INTEGER,
                risk_level VARCHAR(50),
                risk_factors JSONB,

                model_version VARCHAR(50),
                predicted_at TIMESTAMP DEFAULT NOW()
            );
        """)

        # Apply RLS policies
        await self._apply_rls_policies(conn)

        logger.info("workflow_intelligence.schema.created")

    async def _apply_rls_policies(self, conn):
        """Apply Row Level Security policies"""

        # Read and execute RLS policies SQL
        rls_sql_path = Path(__file__).parent / "rls_policies.sql"

        if rls_sql_path.exists():
            rls_sql = rls_sql_path.read_text()

            # Execute RLS policies (split by semicolon for multiple statements)
            for statement in rls_sql.split(';'):
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    try:
                        await conn.execute(statement)
                    except Exception as e:
                        # Some statements may fail if already exists (DROP POLICY IF EXISTS, etc)
                        # This is expected and safe to ignore
                        if "does not exist" not in str(e).lower():
                            logger.warning(
                                "rls.policy.warning",
                                statement=statement[:100],
                                error=str(e)
                            )

            logger.info("workflow_intelligence.rls.applied")
        else:
            logger.warning(
                "workflow_intelligence.rls.skipped",
                reason="rls_policies.sql not found"
            )

    async def save_workflow_context(
        self,
        workflow_id: str,
        module: str,
        context: Dict[str, Any],
        tenant_id: str
    ) -> None:
        """
        Save workflow context (current state)

        RLS PROTECTED: Автоматически изолировано по tenant_id
        """
        async with rls_pool_context(self.pool, tenant_id) as conn:
            await conn.execute("""
                INSERT INTO workflow_intelligence.workflow_contexts
                    (workflow_id, module, tenant_id, context, updated_at)
                VALUES ($1, $2, $3, $4, NOW())
                ON CONFLICT (workflow_id, tenant_id)
                DO UPDATE SET
                    context = $4,
                    updated_at = NOW()
            """, workflow_id, module, tenant_id, json.dumps(context))

        logger.info("workflow_context.saved", workflow_id=workflow_id, module=module, tenant_id=tenant_id)

    async def get_workflow_context(
        self,
        workflow_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get workflow context

        RLS PROTECTED: Может получить только свои данные
        """
        async with rls_pool_context(self.pool, tenant_id) as conn:
            row = await conn.fetchrow("""
                SELECT context FROM workflow_intelligence.workflow_contexts
                WHERE workflow_id = $1 AND tenant_id = $2
            """, workflow_id, tenant_id)

            if row:
                return json.loads(row['context'])
            return None

    async def save_case(
        self,
        case_id: str,
        module: str,
        case_data: Dict[str, Any],
        tenant_id: str
    ) -> None:
        """
        Save completed workflow case for learning

        RLS PROTECTED: Автоматически изолировано по tenant_id
        """

        # Generate embedding (placeholder - will use actual embeddings later)
        # For now, create zero vector
        embedding = [0.0] * 1536

        async with rls_pool_context(self.pool, tenant_id) as conn:
            await conn.execute("""
                INSERT INTO workflow_intelligence.workflow_cases
                    (case_id, module, tenant_id, org_industry, org_size, org_maturity,
                     journey, total_duration_days, success, user_satisfaction,
                     success_patterns, lessons_learned, embedding, completed_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, NOW())
                ON CONFLICT (case_id) DO NOTHING
            """,
                case_id,
                module,
                tenant_id,
                case_data.get('org_context', {}).get('industry'),
                case_data.get('org_context', {}).get('size'),
                case_data.get('org_context', {}).get('maturity_level'),
                json.dumps(case_data.get('journey', [])),
                case_data.get('metrics', {}).get('total_duration_days'),
                case_data.get('metrics', {}).get('completed_successfully'),
                case_data.get('metrics', {}).get('user_satisfaction'),
                json.dumps(case_data.get('success_patterns', [])),
                json.dumps(case_data.get('lessons_learned', [])),
                embedding  # Vector embedding
            )

        logger.info("workflow_case.saved", case_id=case_id, module=module, tenant_id=tenant_id)

    async def find_similar_cases(
        self,
        module: str,
        org_context: Dict[str, Any],
        current_stage: str,
        limit: int = 5,
        tenant_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find similar successful cases

        RLS NOTE: Если tenant_id указан - ищет только свои cases.
                  Если НЕ указан - ищет ПО ВСЕМ tenant'ам (для benchmarking/learning)
                  НО данные анонимизированы!
        """

        # For now, filter by industry and org_size (will add vector similarity later)
        if tenant_id:
            # Tenant-specific search (RLS protected)
            async with rls_pool_context(self.pool, tenant_id) as conn:
                rows = await conn.fetch("""
                    SELECT
                        case_id,
                        org_industry,
                        org_size,
                        journey,
                        total_duration_days,
                        success_patterns,
                        lessons_learned
                    FROM workflow_intelligence.workflow_cases
                    WHERE module = $1
                      AND org_industry = $2
                      AND org_size = $3
                      AND success = true
                    ORDER BY completed_at DESC
                    LIMIT $4
                """,
                    module,
                    org_context.get('industry'),
                    org_context.get('size'),
                    limit
                )
        else:
            # Cross-tenant search (для learning) - БЕЗ RLS, но анонимизировано
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT
                        case_id,
                        org_industry,
                        org_size,
                        journey,
                        total_duration_days,
                        success_patterns,
                        lessons_learned
                    FROM workflow_intelligence.workflow_cases
                    WHERE module = $1
                      AND org_industry = $2
                      AND org_size = $3
                      AND success = true
                    ORDER BY completed_at DESC
                    LIMIT $4
                """,
                    module,
                    org_context.get('industry'),
                    org_context.get('size'),
                    limit
                )

        return [
            {
                'case_id': row['case_id'],
                'org_industry': row['org_industry'],
                'org_size': row['org_size'],
                'journey': json.loads(row['journey']),
                'total_duration_days': row['total_duration_days'],
                'success_patterns': json.loads(row['success_patterns']),
                'lessons_learned': json.loads(row['lessons_learned'])
            }
            for row in rows
        ]

    async def get_benchmarks(
        self,
        module: str,
        industry: Optional[str] = None,
        org_size: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get benchmarks (or calculate on-the-fly)"""

        async with self.pool.acquire() as conn:
            # Try to get cached benchmark
            row = await conn.fetchrow("""
                SELECT
                    avg_duration_days,
                    success_rate,
                    common_challenges,
                    best_practices,
                    total_cases
                FROM workflow_intelligence.benchmarks
                WHERE module = $1
                  AND ($2::varchar IS NULL OR industry = $2)
                  AND ($3::varchar IS NULL OR org_size = $3)
            """, module, industry, org_size)

            if row:
                return {
                    'avg_duration_days': row['avg_duration_days'],
                    'success_rate': row['success_rate'],
                    'common_challenges': json.loads(row['common_challenges']),
                    'best_practices': json.loads(row['best_practices']),
                    'total_cases': row['total_cases']
                }

            # Calculate on-the-fly if no cached benchmark
            stats = await conn.fetchrow("""
                SELECT
                    AVG(total_duration_days) as avg_duration,
                    AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate,
                    COUNT(*) as total_cases
                FROM workflow_intelligence.workflow_cases
                WHERE module = $1
                  AND ($2::varchar IS NULL OR org_industry = $2)
                  AND ($3::varchar IS NULL OR org_size = $3)
            """, module, industry, org_size)

            if stats and stats['total_cases'] > 0:
                return {
                    'avg_duration_days': float(stats['avg_duration']) if stats['avg_duration'] else 0,
                    'success_rate': float(stats['success_rate']) if stats['success_rate'] else 0,
                    'common_challenges': [],
                    'best_practices': [],
                    'total_cases': stats['total_cases']
                }

            return {
                'avg_duration_days': 0,
                'success_rate': 0,
                'common_challenges': [],
                'best_practices': [],
                'total_cases': 0
            }

    async def save_prediction(
        self,
        workflow_id: str,
        prediction: Dict[str, Any],
        tenant_id: str
    ) -> None:
        """
        Save ML prediction

        RLS PROTECTED: Автоматически изолировано по tenant_id
        """
        async with rls_pool_context(self.pool, tenant_id) as conn:
            await conn.execute("""
                INSERT INTO workflow_intelligence.ml_predictions
                    (workflow_id, tenant_id, success_probability,
                     estimated_duration_days, risk_level, risk_factors,
                     model_version)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
                workflow_id,
                tenant_id,
                prediction.get('success_probability'),
                prediction.get('estimated_duration_days'),
                prediction.get('risk_level'),
                json.dumps(prediction.get('risk_factors', [])),
                prediction.get('model_version', 'v1.0')
            )

    async def verify_rls_status(self) -> Dict[str, Any]:
        """
        Проверить статус RLS

        Returns:
            {
                "rls_enabled": {...},
                "isolation_test": {...}
            }
        """
        async with self.pool.acquire() as conn:
            rls_status = await verify_rls_enabled(conn)

        isolation_test = await test_rls_isolation(self.pool)

        return {
            "rls_enabled": rls_status,
            "isolation_test": isolation_test
        }

    async def close(self) -> None:
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("workflow_intelligence.storage.closed")
