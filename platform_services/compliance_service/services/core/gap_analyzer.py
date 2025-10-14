"""
Gap Analyzer - Identifies compliance gaps and generates remediation plans

Migrated from: /services/BCM_1/compliance_checker/app.py:309-384
Date: 2025-10-01
Enhanced with: async, database, workflow integration, EventBus

Severity calculation (PRODUCTION-TESTED):
- weighted_gap = (target_score - current_score) * requirement_weight
- CRITICAL: weighted_gap > 60 OR score < 30
- HIGH: weighted_gap > 40 OR score < 50
- MEDIUM: weighted_gap > 20 OR score < 70
- LOW: else

Effort estimation:
- Base hours: CRITICAL=40, HIGH=24, MEDIUM=16, LOW=8
- +4 hours per missing evidence type
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging
import uuid

from compliance.models.database import GapModel
from compliance.models.enums import GapSeverity, GapStatus, ComplianceStatus
from compliance.integrations.eventbus import EventBusService

logger = logging.getLogger(__name__)


class GapAnalyzer:
    """
    Gap analysis engine for identifying and prioritizing compliance gaps

    This analyzer implements the proven gap severity and effort estimation
    algorithms from compliance_checker, enhanced for production use with
    database persistence and workflow integration.
    """

    def __init__(self, db: AsyncSession, eventbus: Optional[EventBusService] = None):
        """
        Initialize gap analyzer

        Args:
            db: Async database session
            eventbus: Optional EventBus client for publishing events
        """
        self.db = db
        self.eventbus = eventbus

    async def identify_gaps(
        self,
        assessment_results: List[Dict],
        assessment_id: str,
        tenant_id: str,
        target_compliance_level: float = 85.0
    ) -> List[GapModel]:
        """
        Identify compliance gaps from assessment results

        For each requirement that scores below the target level, creates
        a gap record with:
        - Severity based on weighted gap calculation
        - Smart recommendations based on missing evidence
        - Effort estimation in hours
        - Links to assessment for traceability

        Args:
            assessment_results: List of requirement assessment results from AssessmentEngine
            assessment_id: UUID of parent assessment
            tenant_id: Tenant ID for multi-tenancy
            target_compliance_level: Target compliance % (default 85%)

        Returns:
            List of created gap records (persisted to database)
        """
        logger.info(
            f"Identifying gaps for assessment {assessment_id}: "
            f"target={target_compliance_level}%"
        )

        gaps = []

        for result in assessment_results:
            # Only create gap if score below target
            if result["score"] < target_compliance_level:
                # Determine severity (PROVEN ALGORITHM)
                severity = self.determine_severity(
                    current_score=result["score"],
                    target_score=target_compliance_level,
                    weight=result.get("weight", 1.0)
                )

                # Generate smart recommendations
                recommendations = self.generate_recommendations(result)

                # Estimate remediation effort
                effort_hours = self.estimate_effort(result, severity)

                # Create gap record
                gap = GapModel(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant_id,
                    requirement_id=result["requirement_id"],
                    assessment_id=assessment_id,
                    current_score=result["score"],
                    target_score=target_compliance_level,
                    gap_percentage=target_compliance_level - result["score"],
                    severity=severity.value,
                    status=GapStatus.OPEN.value,
                    description=(
                        f"Текущая оценка {result['score']:.1f}% "
                        f"не достигает целевого уровня {target_compliance_level}%"
                    ),
                    recommended_actions=recommendations,
                    estimated_effort_hours=effort_hours,
                    identified_at=datetime.utcnow()
                )

                self.db.add(gap)
                gaps.append(gap)

                logger.info(
                    f"Gap identified for {result['requirement_id']}: "
                    f"severity={severity.value}, gap={gap.gap_percentage:.1f}%"
                )

        # Persist gaps to database
        await self.db.commit()

        # Publish event
        if self.eventbus and gaps:
            try:
                await self.eventbus.publish({
                    "event_type": "bcm.compliance.gaps.identified",
                    "tenant_id": tenant_id,
                    "data": {
                        "assessment_id": assessment_id,
                        "gaps_count": len(gaps),
                        "critical_gaps": len([
                            g for g in gaps
                            if g.severity == GapSeverity.CRITICAL.value
                        ]),
                        "high_gaps": len([
                            g for g in gaps
                            if g.severity == GapSeverity.HIGH.value
                        ]),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                })
            except Exception as e:
                logger.error(f"Failed to publish gaps identified event: {e}")

        logger.info(f"Identified {len(gaps)} compliance gaps")

        return gaps

    def determine_severity(
        self,
        current_score: float,
        target_score: float,
        weight: float
    ) -> GapSeverity:
        """
        Determine gap severity based on weighted gap calculation

        Source: compliance_checker/app.py:334-348
        This algorithm considers both the absolute gap size and the
        requirement weight to prioritize critical gaps.

        Args:
            current_score: Current compliance score (0-100)
            target_score: Target compliance score (0-100)
            weight: ISO requirement weight (1.0-3.0)

        Returns:
            GapSeverity enum value
        """
        gap_size = target_score - current_score
        weighted_gap = gap_size * weight

        # PROVEN SEVERITY THRESHOLDS
        if weighted_gap > 60 or current_score < 30:
            return GapSeverity.CRITICAL
        elif weighted_gap > 40 or current_score < 50:
            return GapSeverity.HIGH
        elif weighted_gap > 20 or current_score < 70:
            return GapSeverity.MEDIUM
        else:
            return GapSeverity.LOW

    def generate_recommendations(
        self,
        assessment_result: Dict
    ) -> List[str]:
        """
        Generate smart recommendations based on assessment results

        Source: compliance_checker/app.py:350-368
        Provides actionable recommendations based on:
        - Missing evidence types
        - Verification status
        - Overall coverage

        Args:
            assessment_result: Single requirement assessment result

        Returns:
            List of actionable recommendations (in Russian)
        """
        actions = []

        # Recommendation 1: Missing evidence
        missing_evidence = assessment_result.get("missing_evidence", [])
        if missing_evidence:
            actions.append(
                f"Предоставить недостающие доказательства: "
                f"{', '.join(missing_evidence)}"
            )

        # Recommendation 2: Verification rate too low
        if assessment_result.get("verification_rate", 0) < 80:
            actions.append(
                "Провести верификацию предоставленных доказательств"
            )

        # Recommendation 3: Overall coverage too low
        if assessment_result.get("evidence_coverage", 0) < 60:
            actions.append(
                "Разработать дополнительную документацию"
            )

        # Fallback recommendation
        if not actions:
            actions.append(
                "Провести детальную оценку для определения "
                "конкретных улучшений"
            )

        return actions

    def estimate_effort(
        self,
        assessment_result: Dict,
        severity: GapSeverity
    ) -> int:
        """
        Estimate remediation effort in hours

        Source: compliance_checker/app.py:370-384
        Uses base effort by severity plus additional hours for
        each missing evidence type.

        Args:
            assessment_result: Single requirement assessment result
            severity: Gap severity

        Returns:
            Estimated effort in hours
        """
        # Base effort by severity (PROVEN VALUES)
        base_hours = {
            GapSeverity.CRITICAL: 40,
            GapSeverity.HIGH: 24,
            GapSeverity.MEDIUM: 16,
            GapSeverity.LOW: 8
        }

        effort = base_hours[severity]

        # Add 4 hours per missing evidence type
        missing_count = len(assessment_result.get("missing_evidence", []))
        effort += missing_count * 4

        return effort

    async def get_critical_gaps(
        self,
        tenant_id: str,
        limit: int = 10
    ) -> List[GapModel]:
        """
        Get critical gaps for tenant (for dashboard)

        Args:
            tenant_id: Tenant ID
            limit: Maximum number of gaps to return

        Returns:
            List of critical/high severity gaps
        """
        from sqlalchemy import select, and_

        stmt = select(GapModel).where(
            and_(
                GapModel.tenant_id == tenant_id,
                GapModel.status == GapStatus.OPEN.value,
                GapModel.severity.in_([
                    GapSeverity.CRITICAL.value,
                    GapSeverity.HIGH.value
                ])
            )
        ).order_by(
            GapModel.gap_percentage.desc()
        ).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()
