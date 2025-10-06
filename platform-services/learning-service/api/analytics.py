"""
Learning Service Analytics Endpoints
Comprehensive analytics and reporting for training metrics
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from shared.database import get_db
from shared.auth.dependencies import get_current_user_dep, require_role
from models.database import (
    TrainingProgram,
    TrainingEnrollment,
    UserAchievement,
    ProgramStatus,
    EnrollmentStatus,
)

router = APIRouter()


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class TrainingMetrics(BaseModel):
    """Overall training metrics"""
    tenant_id: str
    period_start: datetime
    period_end: datetime

    total_enrollments: int
    active_enrollments: int
    completed_enrollments: int
    certified_enrollments: int
    failed_enrollments: int

    completion_rate: float
    certification_rate: float
    average_assessment_score: Optional[float]
    average_completion_time_days: Optional[float]

    total_training_hours: float
    total_certifications_issued: int
    certifications_expiring_soon: int  # Next 30 days


class ProgramPerformance(BaseModel):
    """Program-level performance metrics"""
    program_id: int
    program_code: str
    program_name: str

    total_enrollments: int
    completed: int
    in_progress: int
    failed: int

    completion_rate: float
    average_score: Optional[float]
    average_time_hours: Optional[float]

    pass_rate: Optional[float]
    certification_rate: Optional[float]


class DepartmentMetrics(BaseModel):
    """Department-level training metrics"""
    department: str

    total_enrollments: int
    completed: int
    completion_rate: float

    total_certifications: int
    average_score: Optional[float]

    total_points: int
    top_learner: Optional[str]


class LearnerProfile(BaseModel):
    """Individual learner analytics"""
    person_id: str
    person_name: str

    total_enrollments: int
    completed: int
    in_progress: int
    certified: int

    total_training_hours: float
    total_points: int
    total_achievements: int

    completion_rate: float
    average_score: Optional[float]

    current_rank: Optional[int]
    certifications: List[Dict]
    recent_activity: List[Dict]


class CertificationExpiry(BaseModel):
    """Certifications expiring soon"""
    enrollment_id: int
    person_id: str
    person_name: str
    program_name: str
    certification_number: str
    certification_date: datetime
    expiry_date: datetime
    days_until_expiry: int


class GamificationMetrics(BaseModel):
    """Gamification statistics"""
    tenant_id: str

    total_points_awarded: int
    total_achievements: int
    active_learners: int  # With activity in last 30 days

    top_performers: List[Dict]
    most_popular_achievements: List[Dict]
    average_points_per_learner: float


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/metrics", response_model=TrainingMetrics)
async def get_training_metrics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive training metrics for a period - Authenticated users

    Returns:
    - Enrollment statistics
    - Completion and certification rates
    - Assessment performance
    - Training hours delivered
    """
    # Use tenant_id from JWT token
    tenant_id = current_user["tenant_id"]

    # Default to last 30 days if not specified
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Base query filter
    base_filter = and_(
        TrainingEnrollment.tenant_id == tenant_id,
        TrainingEnrollment.enrolled_date >= start_date,
        TrainingEnrollment.enrolled_date <= end_date
    )

    # Total enrollments
    total_result = await db.execute(
        select(func.count(TrainingEnrollment.id)).where(base_filter)
    )
    total_enrollments = total_result.scalar() or 0

    # Status breakdown
    status_result = await db.execute(
        select(
            TrainingEnrollment.status,
            func.count(TrainingEnrollment.id)
        )
        .where(base_filter)
        .group_by(TrainingEnrollment.status)
    )
    status_counts = {status: count for status, count in status_result.all()}

    active = status_counts.get(EnrollmentStatus.IN_PROGRESS, 0)
    assessed = status_counts.get(EnrollmentStatus.ASSESSED, 0)
    completed = status_counts.get(EnrollmentStatus.COMPLETED, 0) + assessed
    certified = status_counts.get(EnrollmentStatus.CERTIFIED, 0)
    failed = status_counts.get(EnrollmentStatus.FAILED, 0)

    # Completion and certification rates
    completion_rate = (completed + certified) / total_enrollments * 100 if total_enrollments > 0 else 0
    certification_rate = certified / total_enrollments * 100 if total_enrollments > 0 else 0

    # Average assessment score
    score_result = await db.execute(
        select(func.avg(TrainingEnrollment.assessment_score))
        .where(
            and_(
                base_filter,
                TrainingEnrollment.assessment_score.isnot(None)
            )
        )
    )
    avg_score = score_result.scalar()

    # Average completion time
    time_result = await db.execute(
        select(
            func.avg(
                func.extract('epoch', TrainingEnrollment.completed_date - TrainingEnrollment.enrolled_date) / 86400
            )
        )
        .where(
            and_(
                base_filter,
                TrainingEnrollment.completed_date.isnot(None)
            )
        )
    )
    avg_completion_days = time_result.scalar()

    # Total training hours
    hours_result = await db.execute(
        select(func.sum(TrainingEnrollment.time_spent_hours))
        .where(base_filter)
    )
    total_hours = hours_result.scalar() or 0

    # Certifications expiring in next 30 days
    expiring_date = end_date + timedelta(days=30)
    expiring_result = await db.execute(
        select(func.count(TrainingEnrollment.id))
        .where(
            and_(
                TrainingEnrollment.tenant_id == tenant_id,
                TrainingEnrollment.certification_issued == True,
                TrainingEnrollment.certification_expiry_date.isnot(None),
                TrainingEnrollment.certification_expiry_date <= expiring_date,
                TrainingEnrollment.certification_expiry_date > end_date
            )
        )
    )
    expiring_count = expiring_result.scalar() or 0

    return TrainingMetrics(
        tenant_id=tenant_id,
        period_start=start_date,
        period_end=end_date,
        total_enrollments=total_enrollments,
        active_enrollments=active,
        completed_enrollments=completed,
        certified_enrollments=certified,
        failed_enrollments=failed,
        completion_rate=round(completion_rate, 2),
        certification_rate=round(certification_rate, 2),
        average_assessment_score=round(avg_score, 2) if avg_score else None,
        average_completion_time_days=round(avg_completion_days, 1) if avg_completion_days else None,
        total_training_hours=round(total_hours, 1),
        total_certifications_issued=certified,
        certifications_expiring_soon=expiring_count,
    )


@router.get("/programs/performance", response_model=List[ProgramPerformance])
async def get_program_performance(
    limit: int = Query(50, le=100),
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """
    Get performance metrics for all training programs - Authenticated users

    Returns program-level analytics including:
    - Enrollment and completion statistics
    - Average scores and completion times
    - Pass and certification rates
    """
    # Use tenant_id from JWT token
    tenant_id = current_user["tenant_id"]

    # Query program performance
    query = (
        select(
            TrainingProgram.id,
            TrainingProgram.program_code,
            TrainingProgram.program_name,
            func.count(TrainingEnrollment.id).label('total_enrollments'),
            func.sum(
                case((TrainingEnrollment.status.in_([EnrollmentStatus.COMPLETED, EnrollmentStatus.ASSESSED, EnrollmentStatus.CERTIFIED]), 1), else_=0)
            ).label('completed'),
            func.sum(
                case((TrainingEnrollment.status == EnrollmentStatus.IN_PROGRESS, 1), else_=0)
            ).label('in_progress'),
            func.sum(
                case((TrainingEnrollment.status == EnrollmentStatus.FAILED, 1), else_=0)
            ).label('failed'),
            func.avg(TrainingEnrollment.assessment_score).label('avg_score'),
            func.avg(TrainingEnrollment.time_spent_hours).label('avg_hours'),
            func.sum(
                case((TrainingEnrollment.assessment_passed == True, 1), else_=0)
            ).label('passed'),
            func.sum(
                case((TrainingEnrollment.certification_issued == True, 1), else_=0)
            ).label('certified'),
        )
        .join(TrainingEnrollment, TrainingEnrollment.program_id == TrainingProgram.id)
        .where(TrainingProgram.tenant_id == tenant_id)
        .group_by(TrainingProgram.id, TrainingProgram.program_code, TrainingProgram.program_name)
        .order_by(func.count(TrainingEnrollment.id).desc())
        .limit(limit)
    )

    result = await db.execute(query)
    rows = result.all()

    programs = []
    for row in rows:
        total = row.total_enrollments or 0
        completed = row.completed or 0
        passed = row.passed or 0
        certified = row.certified or 0

        completion_rate = (completed / total * 100) if total > 0 else 0
        pass_rate = (passed / completed * 100) if completed > 0 else None
        cert_rate = (certified / total * 100) if total > 0 else None

        programs.append(ProgramPerformance(
            program_id=row.id,
            program_code=row.program_code,
            program_name=row.program_name,
            total_enrollments=total,
            completed=completed,
            in_progress=row.in_progress or 0,
            failed=row.failed or 0,
            completion_rate=round(completion_rate, 2),
            average_score=round(row.avg_score, 2) if row.avg_score else None,
            average_time_hours=round(row.avg_hours, 1) if row.avg_hours else None,
            pass_rate=round(pass_rate, 2) if pass_rate else None,
            certification_rate=round(cert_rate, 2) if cert_rate else None,
        ))

    return programs


@router.get("/departments/metrics", response_model=List[DepartmentMetrics])
async def get_department_metrics(
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """
    Get training metrics by department - Authenticated users

    Returns:
    - Enrollment and completion statistics per department
    - Certification counts
    - Top learners by department
    """
    # Use tenant_id from JWT token
    tenant_id = current_user["tenant_id"]

    # Department-level stats
    query = (
        select(
            TrainingEnrollment.person_department,
            func.count(TrainingEnrollment.id).label('total_enrollments'),
            func.sum(
                case((TrainingEnrollment.status.in_([EnrollmentStatus.COMPLETED, EnrollmentStatus.ASSESSED, EnrollmentStatus.CERTIFIED]), 1), else_=0)
            ).label('completed'),
            func.sum(
                case((TrainingEnrollment.certification_issued == True, 1), else_=0)
            ).label('certified'),
            func.avg(TrainingEnrollment.assessment_score).label('avg_score'),
        )
        .where(
            and_(
                TrainingEnrollment.tenant_id == tenant_id,
                TrainingEnrollment.person_department.isnot(None)
            )
        )
        .group_by(TrainingEnrollment.person_department)
        .order_by(func.count(TrainingEnrollment.id).desc())
    )

    result = await db.execute(query)
    rows = result.all()

    departments = []
    for row in rows:
        total = row.total_enrollments or 0
        completed = row.completed or 0
        completion_rate = (completed / total * 100) if total > 0 else 0

        # Get top learner for department
        top_learner_query = (
            select(TrainingEnrollment.person_name)
            .where(
                and_(
                    TrainingEnrollment.tenant_id == tenant_id,
                    TrainingEnrollment.person_department == row.person_department
                )
            )
            .group_by(TrainingEnrollment.person_name)
            .order_by(func.count(TrainingEnrollment.id).desc())
            .limit(1)
        )
        top_learner_result = await db.execute(top_learner_query)
        top_learner = top_learner_result.scalar()

        # Get total points for department
        points_query = (
            select(func.sum(UserAchievement.points_earned))
            .join(
                TrainingEnrollment,
                and_(
                    UserAchievement.person_id == TrainingEnrollment.person_id,
                    UserAchievement.tenant_id == TrainingEnrollment.tenant_id
                )
            )
            .where(
                and_(
                    TrainingEnrollment.tenant_id == tenant_id,
                    TrainingEnrollment.person_department == row.person_department
                )
            )
        )
        points_result = await db.execute(points_query)
        total_points = points_result.scalar() or 0

        departments.append(DepartmentMetrics(
            department=row.person_department,
            total_enrollments=total,
            completed=completed,
            completion_rate=round(completion_rate, 2),
            total_certifications=row.certified or 0,
            average_score=round(row.avg_score, 2) if row.avg_score else None,
            total_points=total_points,
            top_learner=top_learner,
        ))

    return departments


@router.get("/learners/{person_id}/profile", response_model=LearnerProfile)
async def get_learner_profile(
    person_id: str,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive learner profile and analytics - Authenticated users

    Returns individual learner statistics including:
    - Enrollment and completion history
    - Points and achievements
    - Leaderboard rank
    - Recent activity
    """
    # Use tenant_id from JWT token
    tenant_id = current_user["tenant_id"]

    # Get person info
    person_query = (
        select(TrainingEnrollment.person_name)
        .where(
            and_(
                TrainingEnrollment.tenant_id == tenant_id,
                TrainingEnrollment.person_id == person_id
            )
        )
        .limit(1)
    )
    person_result = await db.execute(person_query)
    person_name = person_result.scalar() or "Unknown"

    # Enrollment stats
    stats_query = (
        select(
            func.count(TrainingEnrollment.id).label('total'),
            func.sum(case((TrainingEnrollment.status.in_([EnrollmentStatus.COMPLETED, EnrollmentStatus.ASSESSED, EnrollmentStatus.CERTIFIED]), 1), else_=0)).label('completed'),
            func.sum(case((TrainingEnrollment.status == EnrollmentStatus.IN_PROGRESS, 1), else_=0)).label('in_progress'),
            func.sum(case((TrainingEnrollment.certification_issued == True, 1), else_=0)).label('certified'),
            func.sum(TrainingEnrollment.time_spent_hours).label('total_hours'),
            func.avg(TrainingEnrollment.assessment_score).label('avg_score'),
        )
        .where(
            and_(
                TrainingEnrollment.tenant_id == tenant_id,
                TrainingEnrollment.person_id == person_id
            )
        )
    )
    stats_result = await db.execute(stats_query)
    stats = stats_result.one()

    total = stats.total or 0
    completed = stats.completed or 0
    completion_rate = (completed / total * 100) if total > 0 else 0

    # Gamification stats
    points_query = (
        select(
            func.sum(UserAchievement.points_earned),
            func.count(UserAchievement.id)
        )
        .where(
            and_(
                UserAchievement.tenant_id == tenant_id,
                UserAchievement.person_id == person_id
            )
        )
    )
    points_result = await db.execute(points_query)
    points_row = points_result.one()
    total_points = points_row[0] or 0
    total_achievements = points_row[1] or 0

    # Leaderboard rank
    rank_query = (
        select(func.count(func.distinct(UserAchievement.person_id)) + 1)
        .where(
            and_(
                UserAchievement.tenant_id == tenant_id,
                UserAchievement.total_points > total_points
            )
        )
    )
    rank_result = await db.execute(rank_query)
    rank = rank_result.scalar()

    # Certifications
    cert_query = (
        select(
            TrainingProgram.program_name,
            TrainingEnrollment.certification_number,
            TrainingEnrollment.certification_date,
            TrainingEnrollment.certification_expiry_date
        )
        .join(TrainingProgram, TrainingProgram.id == TrainingEnrollment.program_id)
        .where(
            and_(
                TrainingEnrollment.tenant_id == tenant_id,
                TrainingEnrollment.person_id == person_id,
                TrainingEnrollment.certification_issued == True
            )
        )
        .order_by(TrainingEnrollment.certification_date.desc())
    )
    cert_result = await db.execute(cert_query)
    certifications = [
        {
            "program_name": row.program_name,
            "certification_number": row.certification_number,
            "issued_date": row.certification_date.isoformat() if row.certification_date else None,
            "expiry_date": row.certification_expiry_date.isoformat() if row.certification_expiry_date else None,
        }
        for row in cert_result.all()
    ]

    # Recent activity (last 10)
    activity_query = (
        select(
            TrainingProgram.program_name,
            TrainingEnrollment.status,
            TrainingEnrollment.progress_percentage,
            TrainingEnrollment.last_activity_date
        )
        .join(TrainingProgram, TrainingProgram.id == TrainingEnrollment.program_id)
        .where(
            and_(
                TrainingEnrollment.tenant_id == tenant_id,
                TrainingEnrollment.person_id == person_id
            )
        )
        .order_by(TrainingEnrollment.last_activity_date.desc())
        .limit(10)
    )
    activity_result = await db.execute(activity_query)
    recent_activity = [
        {
            "program_name": row.program_name,
            "status": row.status.value,
            "progress": row.progress_percentage,
            "last_activity": row.last_activity_date.isoformat() if row.last_activity_date else None,
        }
        for row in activity_result.all()
    ]

    return LearnerProfile(
        person_id=person_id,
        person_name=person_name,
        total_enrollments=total,
        completed=completed,
        in_progress=stats.in_progress or 0,
        certified=stats.certified or 0,
        total_training_hours=round(stats.total_hours or 0, 1),
        total_points=total_points,
        total_achievements=total_achievements,
        completion_rate=round(completion_rate, 2),
        average_score=round(stats.avg_score, 2) if stats.avg_score else None,
        current_rank=rank,
        certifications=certifications,
        recent_activity=recent_activity,
    )


@router.get("/certifications/expiring", response_model=List[CertificationExpiry])
async def get_expiring_certifications(
    days: int = Query(30, description="Days until expiry"),
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """
    Get certifications expiring soon - Authenticated users

    Critical for recertification planning
    """
    # Use tenant_id from JWT token
    tenant_id = current_user["tenant_id"]

    expiry_date = datetime.utcnow() + timedelta(days=days)

    query = (
        select(
            TrainingEnrollment.id,
            TrainingEnrollment.person_id,
            TrainingEnrollment.person_name,
            TrainingProgram.program_name,
            TrainingEnrollment.certification_number,
            TrainingEnrollment.certification_date,
            TrainingEnrollment.certification_expiry_date
        )
        .join(TrainingProgram, TrainingProgram.id == TrainingEnrollment.program_id)
        .where(
            and_(
                TrainingEnrollment.tenant_id == tenant_id,
                TrainingEnrollment.certification_issued == True,
                TrainingEnrollment.certification_expiry_date.isnot(None),
                TrainingEnrollment.certification_expiry_date <= expiry_date,
                TrainingEnrollment.certification_expiry_date > datetime.utcnow()
            )
        )
        .order_by(TrainingEnrollment.certification_expiry_date)
    )

    result = await db.execute(query)
    rows = result.all()

    expiring = []
    for row in rows:
        days_until = (row.certification_expiry_date - datetime.utcnow()).days

        expiring.append(CertificationExpiry(
            enrollment_id=row.id,
            person_id=row.person_id,
            person_name=row.person_name,
            program_name=row.program_name,
            certification_number=row.certification_number,
            certification_date=row.certification_date,
            expiry_date=row.certification_expiry_date,
            days_until_expiry=days_until,
        ))

    return expiring


@router.get("/gamification/metrics", response_model=GamificationMetrics)
async def get_gamification_metrics(
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """
    Get gamification system metrics - Authenticated users

    Returns:
    - Total points and achievements
    - Active learner count
    - Top performers
    - Popular achievements
    """
    # Use tenant_id from JWT token
    tenant_id = current_user["tenant_id"]

    # Total stats
    totals_query = (
        select(
            func.sum(UserAchievement.points_earned),
            func.count(UserAchievement.id),
            func.count(func.distinct(UserAchievement.person_id))
        )
        .where(UserAchievement.tenant_id == tenant_id)
    )
    totals_result = await db.execute(totals_query)
    totals = totals_result.one()

    total_points = totals[0] or 0
    total_achievements = totals[1] or 0
    unique_learners = totals[2] or 0

    # Active learners (last 30 days)
    active_date = datetime.utcnow() - timedelta(days=30)
    active_query = (
        select(func.count(func.distinct(UserAchievement.person_id)))
        .where(
            and_(
                UserAchievement.tenant_id == tenant_id,
                UserAchievement.earned_date >= active_date
            )
        )
    )
    active_result = await db.execute(active_query)
    active_learners = active_result.scalar() or 0

    # Top performers (by points)
    top_query = (
        select(
            UserAchievement.person_name,
            func.sum(UserAchievement.points_earned).label('total_points'),
            func.count(UserAchievement.id).label('achievement_count')
        )
        .where(UserAchievement.tenant_id == tenant_id)
        .group_by(UserAchievement.person_name)
        .order_by(func.sum(UserAchievement.points_earned).desc())
        .limit(10)
    )
    top_result = await db.execute(top_query)
    top_performers = [
        {
            "person_name": row.person_name,
            "total_points": row.total_points,
            "achievements": row.achievement_count,
        }
        for row in top_result.all()
    ]

    # Most popular achievements
    popular_query = (
        select(
            UserAchievement.achievement_name,
            func.count(UserAchievement.id).label('earned_count')
        )
        .where(UserAchievement.tenant_id == tenant_id)
        .group_by(UserAchievement.achievement_name)
        .order_by(func.count(UserAchievement.id).desc())
        .limit(10)
    )
    popular_result = await db.execute(popular_query)
    popular_achievements = [
        {
            "achievement_name": row.achievement_name,
            "times_earned": row.earned_count,
        }
        for row in popular_result.all()
    ]

    avg_points = total_points / unique_learners if unique_learners > 0 else 0

    return GamificationMetrics(
        tenant_id=tenant_id,
        total_points_awarded=total_points,
        total_achievements=total_achievements,
        active_learners=active_learners,
        top_performers=top_performers,
        most_popular_achievements=popular_achievements,
        average_points_per_learner=round(avg_points, 1),
    )
