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
import structlog
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from shared.database import DatabaseManager
from .rls_context import set_rls_context, verify_rls_enabled, test_rls_isolation

logger = structlog.get_logger(__name__)


class PostgresStorageAdapter:
    """PostgreSQL storage adapter using shared bcm_platform database"""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize with DatabaseManager

        Args:
            db_manager: Shared DatabaseManager instance from shared.database
        """
        self.db_manager = db_manager
        self.engine: AsyncEngine = db_manager.engine

    async def connect(self):
        """Initialize schema (engine already connected via DatabaseManager)"""
        # Ensure schema exists
        async for session in self.db_manager.get_session():
            await self._ensure_schema(session)
            break  # Only need one session for initialization

        logger.info("workflow_intelligence.storage.connected")

    async def _ensure_schema(self, session: AsyncSession):
        """Create workflow_intelligence schema and tables if not exists"""

        # Create schema
        await session.execute(text("""
            CREATE SCHEMA IF NOT EXISTS workflow_intelligence;
        """))

        # Enable pgvector extension
        await session.execute(text("""
            CREATE EXTENSION IF NOT EXISTS vector;
        """))

        # Create bcm_app_user if not exists (for RLS grants)
        await session.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'bcm_app_user') THEN
                    CREATE ROLE bcm_app_user;
                END IF;
            END
            $$;
        """))

        # Workflow contexts table
        await session.execute(text("""
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
        """))

        # Workflow cases table (for learning)
        await session.execute(text("""
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
        """))

        # Create vector index for similarity search
        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS workflow_cases_embedding_idx
            ON workflow_intelligence.workflow_cases
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
        """))

        # Benchmarks table (aggregated statistics)
        await session.execute(text("""
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
        """))

        # ML predictions table
        await session.execute(text("""
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
        """))

        # Commit schema changes
        await session.commit()

        # Apply RLS policies
        await self._apply_rls_policies(session)

        logger.info("workflow_intelligence.schema.created")

    async def _apply_rls_policies(self, session: AsyncSession):
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
                        await session.execute(text(statement))
                    except Exception as e:
                        # Some statements may fail if already exists (DROP POLICY IF EXISTS, etc)
                        # This is expected and safe to ignore
                        if "does not exist" not in str(e).lower():
                            logger.warning(
                                "rls.policy.warning",
                                statement=statement[:100],
                                error=str(e)
                            )

            # Commit RLS policies
            await session.commit()
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
        async for session in self.db_manager.get_session():
            await set_rls_context(session, tenant_id)

            await session.execute(
                text("""
                    INSERT INTO workflow_intelligence.workflow_contexts
                        (workflow_id, module, tenant_id, context, updated_at)
                    VALUES (:workflow_id, :module, :tenant_id, :context, NOW())
                    ON CONFLICT (workflow_id, tenant_id)
                    DO UPDATE SET
                        context = :context,
                        updated_at = NOW()
                """),
                {
                    "workflow_id": workflow_id,
                    "module": module,
                    "tenant_id": tenant_id,
                    "context": json.dumps(context)
                }
            )
            await session.commit()
            break

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
        async for session in self.db_manager.get_session():
            await set_rls_context(session, tenant_id)

            result = await session.execute(
                text("""
                    SELECT context FROM workflow_intelligence.workflow_contexts
                    WHERE workflow_id = :workflow_id AND tenant_id = :tenant_id
                """),
                {"workflow_id": workflow_id, "tenant_id": tenant_id}
            )
            row = result.fetchone()

            if row:
                return json.loads(row[0])
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
        embedding = str([0.0] * 1536)

        async for session in self.db_manager.get_session():
            await set_rls_context(session, tenant_id)

            await session.execute(
                text("""
                    INSERT INTO workflow_intelligence.workflow_cases
                        (case_id, module, tenant_id, org_industry, org_size, org_maturity,
                         journey, total_duration_days, success, user_satisfaction,
                         success_patterns, lessons_learned, embedding, completed_at)
                    VALUES (:case_id, :module, :tenant_id, :org_industry, :org_size, :org_maturity,
                            :journey, :total_duration_days, :success, :user_satisfaction,
                            :success_patterns, :lessons_learned, :embedding::vector, NOW())
                    ON CONFLICT (case_id) DO NOTHING
                """),
                {
                    "case_id": case_id,
                    "module": module,
                    "tenant_id": tenant_id,
                    "org_industry": case_data.get('org_context', {}).get('industry'),
                    "org_size": case_data.get('org_context', {}).get('size'),
                    "org_maturity": case_data.get('org_context', {}).get('maturity_level'),
                    "journey": json.dumps(case_data.get('journey', [])),
                    "total_duration_days": case_data.get('metrics', {}).get('total_duration_days'),
                    "success": case_data.get('metrics', {}).get('completed_successfully'),
                    "user_satisfaction": case_data.get('metrics', {}).get('user_satisfaction'),
                    "success_patterns": json.dumps(case_data.get('success_patterns', [])),
                    "lessons_learned": json.dumps(case_data.get('lessons_learned', [])),
                    "embedding": embedding
                }
            )
            await session.commit()
            break

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
        async for session in self.db_manager.get_session():
            if tenant_id:
                # Tenant-specific search (RLS protected)
                await set_rls_context(session, tenant_id)

            result = await session.execute(
                text("""
                    SELECT
                        case_id,
                        org_industry,
                        org_size,
                        journey,
                        total_duration_days,
                        success_patterns,
                        lessons_learned
                    FROM workflow_intelligence.workflow_cases
                    WHERE module = :module
                      AND org_industry = :industry
                      AND org_size = :org_size
                      AND success = true
                    ORDER BY completed_at DESC
                    LIMIT :limit
                """),
                {
                    "module": module,
                    "industry": org_context.get('industry'),
                    "org_size": org_context.get('size'),
                    "limit": limit
                }
            )
            rows = result.fetchall()

            return [
                {
                    'case_id': row[0],
                    'org_industry': row[1],
                    'org_size': row[2],
                    'journey': json.loads(row[3]),
                    'total_duration_days': row[4],
                    'success_patterns': json.loads(row[5]),
                    'lessons_learned': json.loads(row[6])
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

        async for session in self.db_manager.get_session():
            # Try to get cached benchmark
            result = await session.execute(
                text("""
                    SELECT
                        avg_duration_days,
                        success_rate,
                        common_challenges,
                        best_practices,
                        total_cases
                    FROM workflow_intelligence.benchmarks
                    WHERE module = :module
                      AND (:industry::varchar IS NULL OR industry = :industry)
                      AND (:org_size::varchar IS NULL OR org_size = :org_size)
                """),
                {"module": module, "industry": industry, "org_size": org_size}
            )
            row = result.fetchone()

            if row:
                return {
                    'avg_duration_days': row[0],
                    'success_rate': row[1],
                    'common_challenges': json.loads(row[2]),
                    'best_practices': json.loads(row[3]),
                    'total_cases': row[4]
                }

            # Calculate on-the-fly if no cached benchmark
            stats_result = await session.execute(
                text("""
                    SELECT
                        AVG(total_duration_days) as avg_duration,
                        AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate,
                        COUNT(*) as total_cases
                    FROM workflow_intelligence.workflow_cases
                    WHERE module = :module
                      AND (:industry::varchar IS NULL OR org_industry = :industry)
                      AND (:org_size::varchar IS NULL OR org_size = :org_size)
                """),
                {"module": module, "industry": industry, "org_size": org_size}
            )
            stats = stats_result.fetchone()

            if stats and stats[2] > 0:
                return {
                    'avg_duration_days': float(stats[0]) if stats[0] else 0,
                    'success_rate': float(stats[1]) if stats[1] else 0,
                    'common_challenges': [],
                    'best_practices': [],
                    'total_cases': stats[2]
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
        async for session in self.db_manager.get_session():
            await set_rls_context(session, tenant_id)

            await session.execute(
                text("""
                    INSERT INTO workflow_intelligence.ml_predictions
                        (workflow_id, tenant_id, success_probability,
                         estimated_duration_days, risk_level, risk_factors,
                         model_version)
                    VALUES (:workflow_id, :tenant_id, :success_probability,
                            :estimated_duration_days, :risk_level, :risk_factors,
                            :model_version)
                """),
                {
                    "workflow_id": workflow_id,
                    "tenant_id": tenant_id,
                    "success_probability": prediction.get('success_probability'),
                    "estimated_duration_days": prediction.get('estimated_duration_days'),
                    "risk_level": prediction.get('risk_level'),
                    "risk_factors": json.dumps(prediction.get('risk_factors', [])),
                    "model_version": prediction.get('model_version', 'v1.0')
                }
            )
            await session.commit()
            break

    async def verify_rls_status(self) -> Dict[str, Any]:
        """
        Проверить статус RLS

        Returns:
            {
                "rls_enabled": {...},
                "isolation_test": {...}
            }
        """
        async for session in self.db_manager.get_session():
            rls_status = await verify_rls_enabled(session)
            isolation_test = await test_rls_isolation(self.db_manager)
            break

        return {
            "rls_enabled": rls_status,
            "isolation_test": isolation_test
        }

    async def close(self) -> None:
        """Close database connections (handled by DatabaseManager)"""
        # No longer need to close pool - managed by DatabaseManager
        logger.info("workflow_intelligence.storage.closed")
