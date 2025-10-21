"""
PDCA Cycles PostgreSQL Repository

Replaces in-memory storage with real PostgreSQL persistence.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import asdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import json

logger = logging.getLogger(__name__)


class PDCACycleRepository:
    """
    PostgreSQL repository for PDCA cycles

    Provides:
    - Save cycles to database
    - Get benchmarks from history
    - Query lessons and patterns
    - Statistics and analytics
    """

    def __init__(self, db_session: AsyncSession, tenant_id: str):
        self.db = db_session
        self.tenant_id = tenant_id

    async def save_cycle(self, cycle_data: Dict[str, Any]) -> str:
        """
        Save PDCA cycle to PostgreSQL

        Args:
            cycle_data: Complete PDCACycleData as dict

        Returns:
            cycle_id: UUID of saved cycle
        """

        query = text("""
            INSERT INTO workflow_intelligence.pdca_cycles (
                workflow_id, module, tenant_id, user_id,
                cycle_started_at, cycle_completed_at, do_duration,
                plan_data, plan_recommendations, expected_outcomes, estimated_duration,
                similar_cases_count,
                do_data,
                check_data, deviations, benchmarks, quality_score,
                lessons_learned, patterns_detected, improvements,
                saved_to_knowledge_base, saved_to_case_library, contributed_to_predictive
            ) VALUES (
                :workflow_id, :module, :tenant_id::UUID, :user_id::UUID,
                :cycle_started_at, :cycle_completed_at, :do_duration,
                :plan_data::JSONB, :plan_recommendations, :expected_outcomes::JSONB, :estimated_duration,
                :similar_cases_count,
                :do_data::JSONB,
                :check_data::JSONB, :deviations, :benchmarks::JSONB, :quality_score,
                :lessons_learned, :patterns_detected, :improvements,
                :saved_to_knowledge_base, :saved_to_case_library, :contributed_to_predictive
            )
            RETURNING id
        """)

        result = await self.db.execute(query, {
            "workflow_id": cycle_data["workflow_id"],
            "module": cycle_data["module"],
            "tenant_id": self.tenant_id,
            "user_id": cycle_data.get("user_id"),
            "cycle_started_at": cycle_data["cycle_started_at"],
            "cycle_completed_at": cycle_data.get("cycle_completed_at"),
            "do_duration": cycle_data.get("do_duration"),
            "plan_data": json.dumps(cycle_data["plan_data"]),
            "plan_recommendations": cycle_data.get("plan_recommendations", []),
            "expected_outcomes": json.dumps(cycle_data["plan_data"].get("expected_outcomes", {})),
            "estimated_duration": cycle_data["plan_data"].get("estimated_duration"),
            "similar_cases_count": cycle_data.get("similar_cases_count", 0),
            "do_data": json.dumps(cycle_data.get("do_data", {})),
            "check_data": json.dumps(cycle_data.get("check_data", {})),
            "deviations": cycle_data.get("deviations", []),
            "benchmarks": json.dumps(cycle_data.get("benchmarks", {})),
            "quality_score": cycle_data.get("quality_score"),
            "lessons_learned": cycle_data.get("lessons_learned", []),
            "patterns_detected": cycle_data.get("patterns_detected", []),
            "improvements": cycle_data.get("improvements", []),
            "saved_to_knowledge_base": cycle_data.get("saved_to_knowledge_base", False),
            "saved_to_case_library": cycle_data.get("saved_to_case_library", False),
            "contributed_to_predictive": cycle_data.get("contributed_to_predictive", False)
        })

        cycle_id = result.scalar()
        await self.db.commit()

        logger.info(f" PDCA cycle saved: {cycle_id} (workflow={cycle_data['workflow_id']}, module={cycle_data['module']})")

        return str(cycle_id)

    async def get_benchmarks(
        self,
        module: str,
        days_back: int = 90
    ) -> Dict[str, float]:
        """
        Get statistical benchmarks for module

        Uses PostgreSQL function for optimized query

        Returns:
            {
                'avg_duration': float,
                'min_duration': float,
                'max_duration': float,
                'median_duration': float,
                'p95_duration': float,
                'avg_quality_score': float,
                'total_cycles': int,
                'success_rate': float
            }
        """

        query = text("""
            SELECT
                avg_duration,
                min_duration,
                max_duration,
                median_duration,
                p95_duration,
                avg_quality_score,
                total_cycles,
                success_rate
            FROM workflow_intelligence.get_pdca_benchmarks(
                :module,
                :tenant_id::UUID,
                :days_back
            )
        """)

        result = await self.db.execute(query, {
            "module": module,
            "tenant_id": self.tenant_id,
            "days_back": days_back
        })

        row = result.fetchone()

        if not row or row.total_cycles == 0:
            logger.warning(f"No benchmarks found for module={module}, tenant={self.tenant_id}")
            return {
                "avg_duration": 0,
                "min_duration": 0,
                "max_duration": 0,
                "median_duration": 0,
                "p95_duration": 0,
                "avg_quality_score": 0,
                "total_cycles": 0,
                "success_rate": 0
            }

        return {
            "avg_duration": row.avg_duration or 0,
            "min_duration": row.min_duration or 0,
            "max_duration": row.max_duration or 0,
            "median_duration": row.median_duration or 0,
            "p95_duration": row.p95_duration or 0,
            "avg_quality_score": row.avg_quality_score or 0,
            "total_cycles": row.total_cycles,
            "success_rate": row.success_rate or 0
        }

    async def get_recent_patterns(
        self,
        module: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get frequently occurring patterns"""

        query = text("""
            SELECT
                pattern,
                frequency,
                avg_quality_score,
                last_seen
            FROM workflow_intelligence.get_recent_patterns(
                :module,
                :tenant_id::UUID,
                :limit
            )
        """)

        result = await self.db.execute(query, {
            "module": module,
            "tenant_id": self.tenant_id,
            "limit": limit
        })

        patterns = []
        for row in result:
            patterns.append({
                "pattern": row.pattern,
                "frequency": row.frequency,
                "avg_quality_score": row.avg_quality_score,
                "last_seen": row.last_seen
            })

        return patterns

    async def get_lessons_learned(
        self,
        module: str,
        min_quality: float = 70.0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get high-quality lessons"""

        query = text("""
            SELECT
                lesson,
                cycle_id,
                quality_score,
                created_at
            FROM workflow_intelligence.get_lessons_learned(
                :module,
                :tenant_id::UUID,
                :min_quality,
                :limit
            )
        """)

        result = await self.db.execute(query, {
            "module": module,
            "tenant_id": self.tenant_id,
            "min_quality": min_quality,
            "limit": limit
        })

        lessons = []
        for row in result:
            lessons.append({
                "lesson": row.lesson,
                "cycle_id": str(row.cycle_id),
                "quality_score": row.quality_score,
                "created_at": row.created_at
            })

        return lessons

    async def get_cycle_by_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get PDCA cycle for specific workflow"""

        query = text("""
            SELECT
                id,
                workflow_id,
                module,
                cycle_started_at,
                cycle_completed_at,
                do_duration,
                plan_data,
                plan_recommendations,
                do_data,
                check_data,
                deviations,
                benchmarks,
                quality_score,
                lessons_learned,
                patterns_detected,
                improvements
            FROM workflow_intelligence.pdca_cycles
            WHERE workflow_id = :workflow_id
            AND tenant_id = :tenant_id::UUID
            ORDER BY created_at DESC
            LIMIT 1
        """)

        result = await self.db.execute(query, {
            "workflow_id": workflow_id,
            "tenant_id": self.tenant_id
        })

        row = result.fetchone()

        if not row:
            return None

        return {
            "id": str(row.id),
            "workflow_id": row.workflow_id,
            "module": row.module,
            "cycle_started_at": row.cycle_started_at,
            "cycle_completed_at": row.cycle_completed_at,
            "do_duration": row.do_duration,
            "plan_data": row.plan_data,
            "plan_recommendations": row.plan_recommendations,
            "do_data": row.do_data,
            "check_data": row.check_data,
            "deviations": row.deviations,
            "benchmarks": row.benchmarks,
            "quality_score": row.quality_score,
            "lessons_learned": row.lessons_learned,
            "patterns_detected": row.patterns_detected,
            "improvements": row.improvements
        }

    async def get_recent_cycles(
        self,
        module: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recent completed cycles for analysis"""

        base_query = """
            SELECT
                id,
                workflow_id,
                module,
                cycle_started_at,
                cycle_completed_at,
                do_duration,
                quality_score,
                deviations,
                lessons_learned,
                patterns_detected
            FROM workflow_intelligence.pdca_cycles
            WHERE tenant_id = :tenant_id::UUID
            AND cycle_completed_at IS NOT NULL
        """

        if module:
            base_query += " AND module = :module"

        base_query += " ORDER BY cycle_completed_at DESC LIMIT :limit"

        query = text(base_query)

        params = {
            "tenant_id": self.tenant_id,
            "limit": limit
        }

        if module:
            params["module"] = module

        result = await self.db.execute(query, params)

        cycles = []
        for row in result:
            cycles.append({
                "id": str(row.id),
                "workflow_id": row.workflow_id,
                "module": row.module,
                "cycle_started_at": row.cycle_started_at,
                "cycle_completed_at": row.cycle_completed_at,
                "do_duration": row.do_duration,
                "quality_score": row.quality_score,
                "deviations": row.deviations,
                "lessons_learned": row.lessons_learned,
                "patterns_detected": row.patterns_detected
            })

        return cycles

    async def update_cycle_metadata(
        self,
        workflow_id: str,
        saved_to_knowledge_base: bool = False,
        saved_to_case_library: bool = False,
        contributed_to_predictive: bool = False
    ):
        """Update cycle metadata flags"""

        query = text("""
            UPDATE workflow_intelligence.pdca_cycles
            SET
                saved_to_knowledge_base = COALESCE(:saved_to_kb, saved_to_knowledge_base),
                saved_to_case_library = COALESCE(:saved_to_cl, saved_to_case_library),
                contributed_to_predictive = COALESCE(:contributed_pred, contributed_to_predictive),
                updated_at = NOW()
            WHERE workflow_id = :workflow_id
            AND tenant_id = :tenant_id::UUID
        """)

        await self.db.execute(query, {
            "workflow_id": workflow_id,
            "tenant_id": self.tenant_id,
            "saved_to_kb": saved_to_knowledge_base if saved_to_knowledge_base else None,
            "saved_to_cl": saved_to_case_library if saved_to_case_library else None,
            "contributed_pred": contributed_to_predictive if contributed_to_predictive else None
        })

        await self.db.commit()

    async def get_statistics(
        self,
        module: Optional[str] = None,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Get PDCA statistics for monitoring"""

        base_query = """
            SELECT
                COUNT(*) as total_cycles,
                AVG(do_duration) as avg_duration,
                AVG(quality_score) as avg_quality,
                COUNT(*) FILTER (WHERE quality_score >= 70) as successful_cycles,
                COUNT(*) FILTER (WHERE quality_score < 70) as failed_cycles,
                AVG(array_length(lessons_learned, 1)) as avg_lessons_per_cycle,
                AVG(array_length(patterns_detected, 1)) as avg_patterns_per_cycle
            FROM workflow_intelligence.pdca_cycles
            WHERE tenant_id = :tenant_id::UUID
            AND cycle_completed_at IS NOT NULL
            AND cycle_completed_at > NOW() - :days_back::TEXT::INTERVAL
        """

        if module:
            base_query += " AND module = :module"

        query = text(base_query)

        params = {
            "tenant_id": self.tenant_id,
            "days_back": f"{days_back} days"
        }

        if module:
            params["module"] = module

        result = await self.db.execute(query, params)
        row = result.fetchone()

        total = row.total_cycles or 0
        success_rate = (row.successful_cycles / total * 100) if total > 0 else 0

        return {
            "total_cycles": total,
            "avg_duration_seconds": row.avg_duration or 0,
            "avg_quality_score": row.avg_quality or 0,
            "successful_cycles": row.successful_cycles or 0,
            "failed_cycles": row.failed_cycles or 0,
            "success_rate_percent": success_rate,
            "avg_lessons_per_cycle": row.avg_lessons_per_cycle or 0,
            "avg_patterns_per_cycle": row.avg_patterns_per_cycle or 0,
            "period_days": days_back
        }

    async def get_recent_cycles(
        self,
        module: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get recent PDCA cycles with summary info"""

        base_query = """
            SELECT
                id,
                workflow_id,
                module,
                cycle_started_at,
                cycle_completed_at,
                do_duration,
                quality_score,
                array_length(lessons_learned, 1) as lessons_count,
                array_length(patterns_detected, 1) as patterns_count,
                array_length(deviations, 1) as deviations_count
            FROM workflow_intelligence.pdca_cycles
            WHERE tenant_id = :tenant_id::UUID
            AND cycle_completed_at IS NOT NULL
        """

        if module:
            base_query += " AND module = :module"

        base_query += " ORDER BY cycle_completed_at DESC LIMIT :limit"

        query = text(base_query)

        params = {
            "tenant_id": self.tenant_id,
            "limit": limit
        }

        if module:
            params["module"] = module

        result = await self.db.execute(query, params)

        cycles = []
        for row in result:
            cycles.append({
                "id": str(row.id),
                "workflow_id": row.workflow_id,
                "module": row.module,
                "cycle_started_at": row.cycle_started_at,
                "cycle_completed_at": row.cycle_completed_at,
                "do_duration": row.do_duration,
                "quality_score": row.quality_score,
                "lessons_count": row.lessons_count or 0,
                "patterns_count": row.patterns_count or 0,
                "deviations_count": row.deviations_count or 0
            })

        return cycles

    async def get_cycle_by_workflow_id(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get full PDCA cycle by workflow ID (alias for get_cycle_by_workflow)"""
        return await self.get_cycle_by_workflow(workflow_id)

    async def update_cycle_metadata(
        self,
        workflow_id: str,
        saved_to_knowledge_base: Optional[bool] = None,
        saved_to_case_library: Optional[bool] = None,
        contributed_to_predictive: Optional[bool] = None
    ):
        """Update cycle metadata flags"""

        updates = []
        params = {
            "workflow_id": workflow_id,
            "tenant_id": self.tenant_id
        }

        if saved_to_knowledge_base is not None:
            updates.append("saved_to_knowledge_base = :saved_to_knowledge_base")
            params["saved_to_knowledge_base"] = saved_to_knowledge_base

        if saved_to_case_library is not None:
            updates.append("saved_to_case_library = :saved_to_case_library")
            params["saved_to_case_library"] = saved_to_case_library

        if contributed_to_predictive is not None:
            updates.append("contributed_to_predictive = :contributed_to_predictive")
            params["contributed_to_predictive"] = contributed_to_predictive

        if not updates:
            return

        query = text(f"""
            UPDATE workflow_intelligence.pdca_cycles
            SET {', '.join(updates)}
            WHERE workflow_id = :workflow_id
            AND tenant_id = :tenant_id::UUID
        """)

        await self.db.execute(query, params)
        await self.db.commit()

        logger.info(f" Updated metadata for workflow {workflow_id}")
