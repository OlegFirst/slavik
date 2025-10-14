"""
Case Library API

Endpoints for searching and browsing community-contributed cases
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from shared.database import get_db
from shared.auth import get_current_user
from ..models.database import CaseContribution, ContributionStatus

router = APIRouter()


# --- Pydantic Models ---

class CaseSearchRequest(BaseModel):
    """Search cases by criteria"""
    module: Optional[str] = None
    industry: Optional[str] = None
    org_size: Optional[str] = None
    tags: Optional[List[str]] = None
    min_quality_score: Optional[float] = Field(default=7.0, ge=1.0, le=10.0)


class CaseResponse(BaseModel):
    """Case response (anonymized)"""
    case_id: UUID
    module: str
    org_type: str
    tags: List[str]
    submitted_at: str
    avg_quality_score: float


class CaseDetail(CaseResponse):
    """Detailed case info"""
    case_data: dict
    success_patterns: List[str]
    challenges: List[str]
    lessons_learned: List[str]


# --- Endpoints ---

@router.get("/search", response_model=List[CaseResponse])
async def search_cases(
    module: Optional[str] = Query(default=None),
    industry: Optional[str] = Query(default=None),
    tags: Optional[str] = Query(default=None, description="Comma-separated tags"),
    min_quality: float = Query(default=7.0, ge=1.0, le=10.0),
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Search approved cases

    Filters:
    - module: BCM module (bia, risk, etc.)
    - industry: Healthcare, Finance, etc.
    - tags: Comma-separated tags
    - min_quality: Minimum average quality score
    - limit: Max results
    """

    from sqlalchemy import select, and_

    # Build query
    query = select(CaseContribution).where(
        CaseContribution.status == ContributionStatus.APPROVED
    )

    # Apply filters
    if module:
        query = query.where(CaseContribution.module == module)

    if industry:
        # Filter by org_type (contains industry)
        query = query.where(CaseContribution.original_org_type.ilike(f"%{industry}%"))

    if tags:
        tag_list = [t.strip() for t in tags.split(',')]
        query = query.where(CaseContribution.tags.overlap(tag_list))

    # Order by submission date (newest first)
    query = query.order_by(CaseContribution.approved_at.desc()).limit(limit)

    result = await db.execute(query)
    cases = result.scalars().all()

    return [
        CaseResponse(
            case_id=c.id,
            module=c.module,
            org_type=c.original_org_type or "unknown",
            tags=c.tags or [],
            submitted_at=c.submitted_at.isoformat(),
            avg_quality_score=8.0  # TODO: Calculate from reviews
        )
        for c in cases
    ]


@router.get("/{case_id}", response_model=CaseDetail)
async def get_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed case information

    Only approved cases are publicly accessible
    """

    case = await db.get(CaseContribution, case_id)

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )

    # Only approved cases are public
    if case.status != ContributionStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Case not publicly available"
        )

    # Extract structured data from case_data
    case_data = case.case_data
    success_patterns = case_data.get('success_patterns', [])
    challenges = case_data.get('challenges', [])
    lessons_learned = case_data.get('lessons_learned', [])

    return CaseDetail(
        case_id=case.id,
        module=case.module,
        org_type=case.original_org_type or "unknown",
        tags=case.tags or [],
        submitted_at=case.submitted_at.isoformat(),
        avg_quality_score=8.0,  # TODO: Calculate from reviews
        case_data=case_data,
        success_patterns=success_patterns,
        challenges=challenges,
        lessons_learned=lessons_learned
    )


@router.get("/similar/for-workflow", response_model=List[CaseResponse])
async def find_similar_cases(
    module: str = Query(..., description="Current workflow module"),
    industry: Optional[str] = Query(default=None),
    org_size: Optional[str] = Query(default=None),
    limit: int = Query(default=5, le=20),
    db: AsyncSession = Depends(get_db)
):
    """
    Find similar cases for current workflow

    Used by Workflow Intelligence to provide relevant examples

    Similarity factors:
    - Same module
    - Same industry (if provided)
    - Similar org size (if provided)
    - High quality scores
    """

    from sqlalchemy import select, and_

    query = select(CaseContribution).where(
        and_(
            CaseContribution.status == ContributionStatus.APPROVED,
            CaseContribution.module == module
        )
    )

    # Filter by industry if provided
    if industry:
        query = query.where(CaseContribution.original_org_type.ilike(f"%{industry}%"))

    # Order by quality (would need to join with reviews)
    query = query.order_by(CaseContribution.approved_at.desc()).limit(limit)

    result = await db.execute(query)
    cases = result.scalars().all()

    return [
        CaseResponse(
            case_id=c.id,
            module=c.module,
            org_type=c.original_org_type or "unknown",
            tags=c.tags or [],
            submitted_at=c.submitted_at.isoformat(),
            avg_quality_score=8.0  # TODO: Calculate
        )
        for c in cases
    ]


@router.get("/stats/overview")
async def get_case_library_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get Case Library statistics

    Returns:
    - Total approved cases
    - Cases by module
    - Cases by industry
    - Recent contributions
    """

    from sqlalchemy import select, func

    # Total approved cases
    total_result = await db.execute(
        select(func.count(CaseContribution.id)).where(
            CaseContribution.status == ContributionStatus.APPROVED
        )
    )
    total_cases = total_result.scalar() or 0

    # Cases by module
    module_result = await db.execute(
        select(
            CaseContribution.module,
            func.count(CaseContribution.id).label('count')
        )
        .where(CaseContribution.status == ContributionStatus.APPROVED)
        .group_by(CaseContribution.module)
    )
    cases_by_module = {row.module: row.count for row in module_result}

    # Recent contributions (last 30 days)
    from datetime import datetime, timedelta
    recent_result = await db.execute(
        select(func.count(CaseContribution.id)).where(
            and_(
                CaseContribution.status == ContributionStatus.APPROVED,
                CaseContribution.approved_at >= datetime.utcnow() - timedelta(days=30)
            )
        )
    )
    recent_count = recent_result.scalar() or 0

    return {
        'total_cases': total_cases,
        'cases_by_module': cases_by_module,
        'recent_contributions_30d': recent_count,
        'last_updated': datetime.utcnow().isoformat()
    }
