"""
Dashboard API
Provides compliance overview and analytics endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging

from compliance.database.connection import get_db
from compliance.models.database import (
    AssessmentModel,
    GapModel,
    EvidenceModel,
    GapSeverity,
    GapStatus,
    EvidenceStatus,
    AssessmentStatus
)
from compliance.repositories.assessment_repository import AssessmentRepository
from compliance.repositories.gap_repository import GapRepository
from compliance.repositories.evidence_repository import EvidenceRepository
from compliance.standards.iso_22301 import ISO_22301_REQUIREMENTS
from sqlalchemy import select, and_, func, desc

logger = logging.getLogger(__name__)
router = APIRouter()


# Dependency injection factories
def get_assessment_repository(db: AsyncSession = Depends(get_db)) -> AssessmentRepository:
    """Get Assessment repository with database session"""
    return AssessmentRepository(db)


def get_gap_repository(db: AsyncSession = Depends(get_db)) -> GapRepository:
    """Get Gap repository with database session"""
    return GapRepository(db)


def get_evidence_repository(db: AsyncSession = Depends(get_db)) -> EvidenceRepository:
    """Get Evidence repository with database session"""
    return EvidenceRepository(db)


@router.get("/overview")
async def get_compliance_overview(
    tenant_id: str,
    assessment_repo: AssessmentRepository = Depends(get_assessment_repository),
    gap_repo: GapRepository = Depends(get_gap_repository),
    evidence_repo: EvidenceRepository = Depends(get_evidence_repository),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive compliance overview

    Provides high-level compliance metrics including:
    - Latest assessment score
    - Gap distribution by severity
    - Evidence statistics
    - Compliance trend

    Args:
        tenant_id: Tenant identifier
        db: Database session

    Returns:
        Compliance overview dashboard data
    """
    try:
        # Get latest assessment
        latest_assessment_stmt = select(AssessmentModel).where(
            and_(
                AssessmentModel.tenant_id == tenant_id,
                AssessmentModel.status == AssessmentStatus.COMPLETED.value
            )
        ).order_by(desc(AssessmentModel.completed_at)).limit(1)

        latest_assessment_result = await db.execute(latest_assessment_stmt)
        latest_assessment = latest_assessment_result.scalar_one_or_none()

        # Get gap statistics
        gap_stats_stmt = select(
            GapModel.severity,
            func.count(GapModel.id).label('count')
        ).where(
            and_(
                GapModel.tenant_id == tenant_id,
                GapModel.status != GapStatus.VERIFIED.value
            )
        ).group_by(GapModel.severity)

        gap_stats_result = await db.execute(gap_stats_stmt)
        gap_stats = {row.severity: row.count for row in gap_stats_result}

        # Get evidence statistics
        evidence_stats_stmt = select(
            EvidenceModel.status,
            func.count(EvidenceModel.id).label('count')
        ).where(
            EvidenceModel.tenant_id == tenant_id
        ).group_by(EvidenceModel.status)

        evidence_stats_result = await db.execute(evidence_stats_stmt)
        evidence_stats = {row.status: row.count for row in evidence_stats_result}

        # Calculate compliance score
        overall_score = latest_assessment.overall_score if latest_assessment else 0.0

        # Get historical assessments for trend (last 6)
        historical_stmt = select(AssessmentModel).where(
            and_(
                AssessmentModel.tenant_id == tenant_id,
                AssessmentModel.status == AssessmentStatus.COMPLETED.value
            )
        ).order_by(desc(AssessmentModel.completed_at)).limit(6)

        historical_result = await db.execute(historical_stmt)
        historical_assessments = historical_result.scalars().all()

        compliance_trend = [
            {
                "date": a.completed_at.isoformat() if a.completed_at else None,
                "score": a.overall_score
            }
            for a in reversed(historical_assessments)
        ]

        return {
            "overall_compliance": overall_score,
            "compliance_status": _get_compliance_status(overall_score),
            "last_assessment": {
                "id": latest_assessment.id,
                "date": latest_assessment.completed_at.isoformat() if latest_assessment.completed_at else None,
                "score": latest_assessment.overall_score
            } if latest_assessment else None,
            "gaps": {
                "total": sum(gap_stats.values()),
                "by_severity": {
                    "critical": gap_stats.get(GapSeverity.CRITICAL.value, 0),
                    "high": gap_stats.get(GapSeverity.HIGH.value, 0),
                    "medium": gap_stats.get(GapSeverity.MEDIUM.value, 0),
                    "low": gap_stats.get(GapSeverity.LOW.value, 0)
                }
            },
            "evidence": {
                "total": sum(evidence_stats.values()),
                "verified": evidence_stats.get(EvidenceStatus.VERIFIED.value, 0),
                "submitted": evidence_stats.get(EvidenceStatus.SUBMITTED.value, 0),
                "under_review": evidence_stats.get(EvidenceStatus.UNDER_REVIEW.value, 0),
                "draft": evidence_stats.get(EvidenceStatus.DRAFT.value, 0)
            },
            "compliance_trend": compliance_trend,
            "total_requirements": len(ISO_22301_REQUIREMENTS),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get compliance overview: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get compliance overview: {str(e)}"
        )


@router.get("/requirements-matrix")
async def get_requirements_matrix(
    tenant_id: str,
    assessment_id: str = None,
    assessment_repo: AssessmentRepository = Depends(get_assessment_repository),
    gap_repo: GapRepository = Depends(get_gap_repository),
    evidence_repo: EvidenceRepository = Depends(get_evidence_repository),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get ISO 22301 requirements compliance matrix

    Provides detailed breakdown of compliance status for each requirement:
    - Requirement details
    - Current compliance score
    - Evidence count
    - Gap status

    Args:
        tenant_id: Tenant identifier
        assessment_id: Optional specific assessment ID
        db: Database session

    Returns:
        Requirements compliance matrix
    """
    try:
        # Get latest or specified assessment
        if assessment_id:
            assessment_stmt = select(AssessmentModel).where(
                and_(
                    AssessmentModel.id == assessment_id,
                    AssessmentModel.tenant_id == tenant_id
                )
            )
        else:
            assessment_stmt = select(AssessmentModel).where(
                and_(
                    AssessmentModel.tenant_id == tenant_id,
                    AssessmentModel.status == AssessmentStatus.COMPLETED.value
                )
            ).order_by(desc(AssessmentModel.completed_at)).limit(1)

        assessment_result = await db.execute(assessment_stmt)
        assessment = assessment_result.scalar_one_or_none()

        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No assessment found"
            )

        # Build matrix for each requirement
        matrix = []

        for req_id, requirement in ISO_22301_REQUIREMENTS.items():
            # Get evidence count
            evidence_stmt = select(func.count(EvidenceModel.id)).where(
                and_(
                    EvidenceModel.tenant_id == tenant_id,
                    EvidenceModel.requirement_id == req_id,
                    EvidenceModel.status.in_([
                        EvidenceStatus.VERIFIED.value,
                        EvidenceStatus.SUBMITTED.value
                    ])
                )
            )
            evidence_result = await db.execute(evidence_stmt)
            evidence_count = evidence_result.scalar()

            # Get gaps
            gaps_stmt = select(GapModel).where(
                and_(
                    GapModel.tenant_id == tenant_id,
                    GapModel.assessment_id == assessment.id,
                    GapModel.requirement_id == req_id
                )
            )
            gaps_result = await db.execute(gaps_stmt)
            gaps = gaps_result.scalars().all()

            # Determine score (simplified - would come from assessment results in production)
            has_gap = len(gaps) > 0
            score = gaps[0].current_score if gaps else 100.0

            matrix.append({
                "requirement_id": req_id,
                "title": requirement["title"],
                "category": requirement["category"],
                "weight": requirement["weight"],
                "score": score,
                "status": _get_requirement_status(score),
                "evidence_count": evidence_count,
                "gaps": [
                    {
                        "id": g.id,
                        "severity": g.severity,
                        "status": g.status
                    }
                    for g in gaps
                ]
            })

        return {
            "assessment_id": assessment.id,
            "assessment_date": assessment.completed_at.isoformat() if assessment.completed_at else None,
            "overall_score": assessment.overall_score,
            "requirements": matrix,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get requirements matrix: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get requirements matrix: {str(e)}"
        )


@router.get("/roadmap")
async def get_compliance_roadmap(
    tenant_id: str,
    gap_repo: GapRepository = Depends(get_gap_repository),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get compliance remediation roadmap

    Provides prioritized list of gaps with remediation plans:
    - Critical gaps first
    - Estimated effort
    - Target dates
    - Current progress

    Args:
        tenant_id: Tenant identifier
        db: Database session

    Returns:
        Compliance roadmap with prioritized gaps
    """
    try:
        # Get all active gaps ordered by severity and effort
        gaps_stmt = select(GapModel).where(
            and_(
                GapModel.tenant_id == tenant_id,
                GapModel.status.in_([
                    GapStatus.OPEN.value,
                    GapStatus.IN_PROGRESS.value,
                    GapStatus.RESOLVED.value
                ])
            )
        ).order_by(
            desc(GapModel.severity),
            GapModel.estimated_effort.asc()
        )

        gaps_result = await db.execute(gaps_stmt)
        gaps = gaps_result.scalars().all()

        # Calculate total effort and timeline
        total_effort = sum(g.estimated_effort or 0 for g in gaps)

        # Group by severity
        roadmap_by_severity = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }

        for gap in gaps:
            gap_data = {
                "id": gap.id,
                "requirement_id": gap.requirement_id,
                "requirement_title": ISO_22301_REQUIREMENTS.get(gap.requirement_id, {}).get("title", "Unknown"),
                "description": gap.description,
                "severity": gap.severity,
                "status": gap.status,
                "current_score": gap.current_score,
                "target_score": gap.target_score,
                "estimated_effort": gap.estimated_effort,
                "progress": gap.progress,
                "target_date": gap.target_date.isoformat() if gap.target_date else None,
                "assignee_id": gap.assignee_id,
                "remediation_plan": gap.remediation_plan
            }

            roadmap_by_severity[gap.severity].append(gap_data)

        # Calculate phase timeline
        phases = [
            {
                "phase": "Phase 1: Critical Gaps",
                "gaps": roadmap_by_severity["critical"],
                "total_effort": sum(g["estimated_effort"] or 0 for g in roadmap_by_severity["critical"]),
                "gap_count": len(roadmap_by_severity["critical"])
            },
            {
                "phase": "Phase 2: High Priority",
                "gaps": roadmap_by_severity["high"],
                "total_effort": sum(g["estimated_effort"] or 0 for g in roadmap_by_severity["high"]),
                "gap_count": len(roadmap_by_severity["high"])
            },
            {
                "phase": "Phase 3: Medium Priority",
                "gaps": roadmap_by_severity["medium"],
                "total_effort": sum(g["estimated_effort"] or 0 for g in roadmap_by_severity["medium"]),
                "gap_count": len(roadmap_by_severity["medium"])
            },
            {
                "phase": "Phase 4: Low Priority",
                "gaps": roadmap_by_severity["low"],
                "total_effort": sum(g["estimated_effort"] or 0 for g in roadmap_by_severity["low"]),
                "gap_count": len(roadmap_by_severity["low"])
            }
        ]

        return {
            "total_gaps": len(gaps),
            "total_effort_hours": total_effort,
            "estimated_duration_weeks": round(total_effort / 40, 1),  # Assuming 40 hours/week
            "phases": phases,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get compliance roadmap: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get compliance roadmap: {str(e)}"
        )


@router.get("/analytics")
async def get_compliance_analytics(
    tenant_id: str,
    days: int = 90,
    assessment_repo: AssessmentRepository = Depends(get_assessment_repository),
    gap_repo: GapRepository = Depends(get_gap_repository),
    evidence_repo: EvidenceRepository = Depends(get_evidence_repository),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get compliance analytics and trends

    Args:
        tenant_id: Tenant identifier
        days: Number of days to analyze (default: 90)
        db: Database session

    Returns:
        Compliance analytics
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get assessments in period
        assessments_stmt = select(AssessmentModel).where(
            and_(
                AssessmentModel.tenant_id == tenant_id,
                AssessmentModel.status == AssessmentStatus.COMPLETED.value,
                AssessmentModel.completed_at >= cutoff_date
            )
        ).order_by(AssessmentModel.completed_at)

        assessments_result = await db.execute(assessments_stmt)
        assessments = assessments_result.scalars().all()

        # Calculate trend
        score_trend = [
            {
                "date": a.completed_at.isoformat(),
                "score": a.overall_score
            }
            for a in assessments
        ]

        # Get gap resolution rate
        resolved_gaps_stmt = select(func.count(GapModel.id)).where(
            and_(
                GapModel.tenant_id == tenant_id,
                GapModel.status == GapStatus.VERIFIED.value,
                GapModel.verified_at >= cutoff_date
            )
        )
        resolved_result = await db.execute(resolved_gaps_stmt)
        resolved_gaps = resolved_result.scalar()

        total_gaps_stmt = select(func.count(GapModel.id)).where(
            and_(
                GapModel.tenant_id == tenant_id,
                GapModel.created_at >= cutoff_date
            )
        )
        total_result = await db.execute(total_gaps_stmt)
        total_gaps = total_result.scalar()

        resolution_rate = (resolved_gaps / total_gaps * 100) if total_gaps > 0 else 0

        # Average time to verify evidence
        verified_evidence_stmt = select(EvidenceModel).where(
            and_(
                EvidenceModel.tenant_id == tenant_id,
                EvidenceModel.status == EvidenceStatus.VERIFIED.value,
                EvidenceModel.verified_at >= cutoff_date
            )
        )
        verified_evidence_result = await db.execute(verified_evidence_stmt)
        verified_evidence = verified_evidence_result.scalars().all()

        avg_verification_time = None
        if verified_evidence:
            verification_times = [
                (e.verified_at - e.created_at).total_seconds() / 3600  # hours
                for e in verified_evidence
                if e.verified_at and e.created_at
            ]
            if verification_times:
                avg_verification_time = sum(verification_times) / len(verification_times)

        return {
            "period_days": days,
            "assessments_count": len(assessments),
            "score_trend": score_trend,
            "current_score": assessments[-1].overall_score if assessments else 0,
            "score_change": (assessments[-1].overall_score - assessments[0].overall_score) if len(assessments) > 1 else 0,
            "gap_resolution_rate": round(resolution_rate, 1),
            "gaps_resolved": resolved_gaps,
            "gaps_created": total_gaps,
            "avg_evidence_verification_time_hours": round(avg_verification_time, 1) if avg_verification_time else None,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get compliance analytics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get compliance analytics: {str(e)}"
        )


# Helper functions

def _get_compliance_status(score: float) -> str:
    """Determine compliance status from score"""
    if score >= 90:
        return "excellent"
    elif score >= 75:
        return "good"
    elif score >= 60:
        return "needs_improvement"
    else:
        return "critical"


def _get_requirement_status(score: float) -> str:
    """Determine requirement status from score"""
    if score >= 90:
        return "compliant"
    elif score >= 60:
        return "partial"
    else:
        return "non_compliant"
