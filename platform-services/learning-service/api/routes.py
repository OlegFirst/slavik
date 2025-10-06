"""
Learning Service API Routes
ВСЕ endpoints из original main.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from shared.database import get_db
from shared.eventbus import get_eventbus
from shared.auth.dependencies import get_current_user_dep, require_role
from models.domain import *
from services.training_service import TrainingService
from services.gamification_service import GamificationService
from workflows.gamification_workflow import ActionCategory

router = APIRouter()


# ============================================================================
# TRAINING PROGRAMS
# ============================================================================

@router.post("/programs", response_model=ProgramResponse, status_code=201)
async def create_program(
    data: ProgramCreate,
    current_user: dict = Depends(require_role("admin", "bcm_manager")),
    db: AsyncSession = Depends(get_db)
):
    """Create training program - Admin/BCM Manager only"""
    # Override tenant_id from JWT token
    data.tenant_id = current_user["tenant_id"]

    service = TrainingService(db)
    program = await service.create_program(data)
    
    # Publish event
    try:
        eventbus = get_eventbus()
        await eventbus.publish(
            "learning.program.created",
            {
                "program_id": program.id,
                "tenant_id": program.tenant_id,
                "program_code": program.program_code,
            }
        )
    except:
        pass  # Don't fail if eventbus unavailable

    return program


@router.get("/programs/{program_id}", response_model=ProgramResponse)
async def get_program(
    program_id: int,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """Get program by ID - Authenticated users"""
    service = TrainingService(db)
    try:
        program = await service.get_program(program_id)
        
        # Add calculated fields
        enrollment_count = await service.program_repo.get_enrollment_count(program_id)
        completion_rate = await service.program_repo.get_completion_rate(program_id)
        
        response = ProgramResponse.model_validate(program)
        response.enrollment_count = enrollment_count
        response.completion_rate = completion_rate
        
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/programs/{program_id}", response_model=ProgramResponse)
async def update_program(
    program_id: int,
    data: ProgramUpdate,
    current_user: dict = Depends(require_role("admin", "bcm_manager")),
    db: AsyncSession = Depends(get_db)
):
    """Update program - Admin/BCM Manager only"""
    service = TrainingService(db)
    try:
        program = await service.update_program(program_id, data)
        return program
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/programs/{program_id}/publish", response_model=ProgramResponse)
async def publish_program(
    program_id: int,
    current_user: dict = Depends(require_role("admin", "bcm_manager")),
    db: AsyncSession = Depends(get_db)
):
    """Publish program - Admin/BCM Manager only"""
    service = TrainingService(db)
    try:
        program = await service.publish_program(program_id)
        
        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "learning.program.published",
                {
                    "program_id": program.id,
                    "tenant_id": program.tenant_id,
                }
            )
        except:
            pass

        return program
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/programs/{program_id}/archive", response_model=ProgramResponse)
async def archive_program(
    program_id: int,
    current_user: dict = Depends(require_role("admin", "bcm_manager")),
    db: AsyncSession = Depends(get_db)
):
    """Archive program - Admin/BCM Manager only"""
    service = TrainingService(db)
    program = await service.archive_program(program_id)
    return program


@router.get("/programs", response_model=List[ProgramResponse])
async def list_programs(
    status: Optional[ProgramStatus] = None,
    program_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """List programs - Authenticated users"""
    # Use tenant_id from JWT token
    tenant_id = current_user["tenant_id"]

    service = TrainingService(db)
    programs = await service.list_programs(
        tenant_id, status, program_type, skip, limit
    )
    return programs


# ============================================================================
# ENROLLMENTS - WORKFLOW
# ============================================================================

@router.post("/enrollments", response_model=EnrollmentResponse, status_code=201)
async def create_enrollment(
    data: EnrollmentCreate,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """Create enrollment (start workflow) - Authenticated users"""
    # Override tenant_id from JWT token
    data.tenant_id = current_user["tenant_id"]

    service = TrainingService(db)
    try:
        enrollment = await service.create_enrollment(data)
        
        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "learning.enrollment.created",
                {
                    "enrollment_id": enrollment.id,
                    "tenant_id": enrollment.tenant_id,
                    "person_id": enrollment.person_id,
                    "program_id": enrollment.program_id,
                }
            )
        except:
            pass

        return enrollment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/enrollments/{enrollment_id}", response_model=EnrollmentResponse)
async def get_enrollment(
    enrollment_id: int,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """Get enrollment - Authenticated users"""
    service = TrainingService(db)
    try:
        enrollment = await service.get_enrollment(enrollment_id)
        return enrollment
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/enrollments/{enrollment_id}/submit", response_model=EnrollmentResponse)
async def submit_enrollment(
    enrollment_id: int,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """Submit enrollment for approval - Authenticated users"""
    service = TrainingService(db)
    try:
        enrollment = await service.submit_enrollment(enrollment_id)
        
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "learning.enrollment.submitted",
                {"enrollment_id": enrollment.id}
            )
        except:
            pass

        return enrollment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/enrollments/{enrollment_id}/approve", response_model=EnrollmentResponse)
async def approve_enrollment(
    enrollment_id: int,
    approved_by: str,
    current_user: dict = Depends(require_role("admin", "bcm_manager", "manager")),
    db: AsyncSession = Depends(get_db)
):
    """Approve enrollment - Admin/Manager only"""
    service = TrainingService(db)
    try:
        enrollment = await service.approve_enrollment(enrollment_id, approved_by)
        return enrollment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/enrollments/{enrollment_id}/start", response_model=EnrollmentResponse)
async def start_training(
    enrollment_id: int,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """Start training - Authenticated users"""
    service = TrainingService(db)
    try:
        enrollment = await service.start_training(enrollment_id)
        
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "learning.training.started",
                {"enrollment_id": enrollment.id}
            )
        except:
            pass

        return enrollment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/enrollments/{enrollment_id}/progress", response_model=EnrollmentResponse)
async def update_progress(
    enrollment_id: int,
    data: EnrollmentProgressUpdate,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """Update training progress - Authenticated users"""
    service = TrainingService(db)
    try:
        enrollment = await service.update_progress(enrollment_id, data)
        return enrollment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/enrollments/{enrollment_id}/complete", response_model=EnrollmentResponse)
async def complete_training(
    enrollment_id: int,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """Complete training - Authenticated users"""
    service = TrainingService(db)
    try:
        enrollment = await service.complete_training(enrollment_id)
        
        # Award points for completion
        gamification = GamificationService(db)
        await gamification.award_points_for_action(
            enrollment.tenant_id,
            enrollment.person_id,
            enrollment.person_name,
            ActionCategory.ENROLLMENT_COMPLETED,
            {"enrollment_id": enrollment.id}
        )
        
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "learning.training.completed",
                {"enrollment_id": enrollment.id}
            )
        except:
            pass

        return enrollment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/enrollments/{enrollment_id}/assess", response_model=EnrollmentResponse)
async def submit_assessment(
    enrollment_id: int,
    data: EnrollmentAssessment,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """Submit assessment - Authenticated users"""
    service = TrainingService(db)
    try:
        enrollment = await service.submit_assessment(enrollment_id, data)
        
        # Award points if passed
        if enrollment.assessment_passed:
            gamification = GamificationService(db)
            await gamification.award_points_for_action(
                enrollment.tenant_id,
                enrollment.person_id,
                enrollment.person_name,
                ActionCategory.ASSESSMENT_PASSED,
                {
                    "enrollment_id": enrollment.id,
                    "score": enrollment.assessment_score,
                }
            )
        
        return enrollment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/enrollments/{enrollment_id}/certify", response_model=EnrollmentResponse)
async def issue_certification(
    enrollment_id: int,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """Issue certification - Authenticated users"""
    service = TrainingService(db)
    try:
        enrollment = await service.issue_certification(enrollment_id)
        
        # Award points for certification
        gamification = GamificationService(db)
        await gamification.award_points_for_action(
            enrollment.tenant_id,
            enrollment.person_id,
            enrollment.person_name,
            ActionCategory.CERTIFICATION_EARNED,
            {
                "enrollment_id": enrollment.id,
                "certification_number": enrollment.certification_number,
            }
        )
        
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "learning.certification.issued",
                {
                    "enrollment_id": enrollment.id,
                    "certification_number": enrollment.certification_number,
                }
            )
        except:
            pass

        return enrollment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/persons/{person_id}/enrollments", response_model=List[EnrollmentResponse])
async def list_person_enrollments(
    person_id: str,
    status: Optional[EnrollmentStatus] = None,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """List enrollments for person - Authenticated users"""
    # Use tenant_id from JWT token
    tenant_id = current_user["tenant_id"]

    service = TrainingService(db)
    enrollments = await service.list_enrollments_by_person(
        tenant_id, person_id, status
    )
    return enrollments


# ============================================================================
# GAMIFICATION
# ============================================================================

@router.get("/persons/{person_id}/achievements", response_model=List[AchievementResponse])
async def get_user_achievements(
    person_id: str,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """Get user achievements - Authenticated users"""
    # Use tenant_id from JWT token
    tenant_id = current_user["tenant_id"]

    service = GamificationService(db)
    achievements = await service.get_user_achievements(tenant_id, person_id)
    return achievements


@router.get("/persons/{person_id}/points")
async def get_user_points(
    person_id: str,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """Get user total points - Authenticated users"""
    # Use tenant_id from JWT token
    tenant_id = current_user["tenant_id"]

    service = GamificationService(db)
    points = await service.get_user_total_points(tenant_id, person_id)
    level_data = await service.get_user_level(tenant_id, person_id)
    
    return {
        "person_id": person_id,
        "total_points": points,
        "level": level_data["current_level"],
        "level_progress": level_data,
    }


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    limit: int = 50,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """Get leaderboard - Authenticated users"""
    # Use tenant_id from JWT token
    tenant_id = current_user["tenant_id"]

    service = GamificationService(db)
    entries = await service.get_leaderboard(tenant_id, limit)
    
    return LeaderboardResponse(
        tenant_id=tenant_id,
        period="all_time",
        updated_at=datetime.utcnow(),
        entries=entries,
    )


@router.get("/persons/{person_id}/rank")
async def get_user_rank(
    person_id: str,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """Get user rank - Authenticated users"""
    # Use tenant_id from JWT token
    tenant_id = current_user["tenant_id"]

    service = GamificationService(db)
    rank = await service.get_user_rank(tenant_id, person_id)
    
    return {
        "person_id": person_id,
        "rank": rank,
    }
