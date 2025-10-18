"""
Training Service
FULL Business Logic для Training Programs и Enrollments
Сохранена ВСЯ логика из original main.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime

from models.database import (
    TrainingProgram,
    TrainingEnrollment,
    ProgramStatus,
    EnrollmentStatus,
)
from models.domain import (
    ProgramCreate,
    ProgramUpdate,
    EnrollmentCreate,
    EnrollmentProgressUpdate,
    EnrollmentAssessment,
)
from repositories.training_repository import (
    TrainingProgramRepository,
    TrainingEnrollmentRepository,
)
from workflows.training_workflow import (
    EnrollmentState,
    EnrollmentAction,
    can_transition,
    get_next_state,
    validate_transition,
    validate_enrollment_data,
    validate_progress_update,
    validate_assessment_score,
    validate_assessment_attempts,
    determine_assessment_result,
    can_start_training,
    can_complete_training,
    can_issue_certification,
    auto_progress_calculation,
    get_state_entry_actions,
    validate_enrollment_deadline,
    should_auto_complete,
    calculate_certification_expiry,
)


class TrainingService:
    """
    Training Service - FULL Business Logic
    
    Handles:
    - Training Program Management
    - Enrollment Workflow (with state machine)
    - Progress Tracking
    - Assessment
    - Certification
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.program_repo = TrainingProgramRepository(session)
        self.enrollment_repo = TrainingEnrollmentRepository(session)

    # ========================================================================
    # TRAINING PROGRAMS
    # ========================================================================

    async def create_program(self, data: ProgramCreate) -> TrainingProgram:
        """Create training program"""
        
        # Check if program code exists
        existing = await self.program_repo.get_by_code(
            data.tenant_id,
            data.program_code
        )
        if existing:
            raise ValueError(f"Program code {data.program_code} already exists")

        # Create program
        program = TrainingProgram(
            tenant_id=data.tenant_id,
            program_code=data.program_code,
            program_name=data.program_name,
            description=data.description,
            program_type=data.program_type,
            bci_training_level=data.bci_training_level,
            target_audience=data.target_audience,
            iso_clause=data.iso_clause,
            learning_objectives=data.learning_objectives,
            curriculum=data.curriculum,
            duration_hours=data.duration_hours,
            delivery_method=data.delivery_method,
            assessment_required=data.assessment_required,
            passing_score=data.passing_score,
            certification_awarded=data.certification_awarded,
            status=ProgramStatus.DRAFT,
        )

        return await self.program_repo.create(program)

    async def get_program(self, program_id: int) -> TrainingProgram:
        """Get program by ID"""
        program = await self.program_repo.get_by_id(program_id)
        if not program:
            raise ValueError(f"Program {program_id} not found")
        return program

    async def update_program(
        self,
        program_id: int,
        data: ProgramUpdate
    ) -> TrainingProgram:
        """Update program"""
        program = await self.get_program(program_id)

        # Update fields
        if data.program_name is not None:
            program.program_name = data.program_name
        if data.description is not None:
            program.description = data.description
        if data.status is not None:
            program.status = data.status
        if data.learning_objectives is not None:
            program.learning_objectives = data.learning_objectives
        if data.curriculum is not None:
            program.curriculum = data.curriculum
        if data.passing_score is not None:
            program.passing_score = data.passing_score

        return await self.program_repo.update(program)

    async def publish_program(self, program_id: int) -> TrainingProgram:
        """Publish program"""
        program = await self.get_program(program_id)

        if program.status != ProgramStatus.DRAFT:
            raise ValueError("Only draft programs can be published")

        program.status = ProgramStatus.PUBLISHED
        return await self.program_repo.update(program)

    async def archive_program(self, program_id: int) -> TrainingProgram:
        """Archive program"""
        program = await self.get_program(program_id)
        program.status = ProgramStatus.ARCHIVED
        return await self.program_repo.update(program)

    async def list_programs(
        self,
        tenant_id: str,
        status: Optional[ProgramStatus] = None,
        program_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TrainingProgram]:
        """List programs"""
        return await self.program_repo.list_by_tenant(
            tenant_id, status, program_type, skip, limit
        )

    # ========================================================================
    # ENROLLMENTS - CORE WORKFLOW
    # ========================================================================

    async def create_enrollment(self, data: EnrollmentCreate) -> TrainingEnrollment:
        """
        Create enrollment (start of workflow)
        State: DRAFT
        """

        # Validate program exists and is published
        program = await self.get_program(data.program_id)
        if program.status != ProgramStatus.PUBLISHED:
            raise ValueError("Cannot enroll in unpublished program")

        # Check if already enrolled
        existing = await self.enrollment_repo.get_by_person_and_program(
            data.tenant_id,
            data.person_id,
            data.program_id
        )
        if existing and existing.status not in [
            EnrollmentStatus.ARCHIVED,
            EnrollmentStatus.COMPLETED
        ]:
            raise ValueError("Already enrolled in this program")

        # Validate enrollment data
        valid, error = validate_enrollment_data({
            "person_id": data.person_id,
            "person_name": data.person_name,
            "program_id": data.program_id,
        })
        if not valid:
            raise ValueError(error)

        # Validate enrollment deadline
        deadline_valid, deadline_warning = validate_enrollment_deadline(
            data.target_completion_date,
            program.duration_hours,
            datetime.utcnow()
        )
        if deadline_warning:
            # Log warning but don't block enrollment
            print(f"WARNING: {deadline_warning}")

        # Create enrollment
        enrollment = TrainingEnrollment(
            tenant_id=data.tenant_id,
            program_id=data.program_id,
            person_id=data.person_id,
            person_name=data.person_name,
            person_department=data.department,
            assigned_by=data.enrolled_by,
            target_completion_date=data.target_completion_date,
            status=EnrollmentStatus.DRAFT,
            progress_percentage=0,
            assessment_passed=False,
            certification_issued=False,
            points_earned=0,
            enrolled_date=datetime.utcnow(),
            assessment_attempts=0,
        )

        return await self.enrollment_repo.create(enrollment)

    async def submit_enrollment(self, enrollment_id: int) -> TrainingEnrollment:
        """
        Submit enrollment for approval
        Transition: DRAFT → SUBMITTED
        """
        enrollment = await self._get_enrollment(enrollment_id)

        # Validate transition
        if not can_transition(enrollment.status.value, EnrollmentAction.SUBMIT.value):
            raise ValueError(f"Cannot submit from status {enrollment.status}")

        # Perform transition
        enrollment.status = EnrollmentStatus.SUBMITTED
        enrollment.submitted_date = datetime.utcnow()

        return await self.enrollment_repo.update(enrollment)

    async def approve_enrollment(self, enrollment_id: int, approved_by: str) -> TrainingEnrollment:
        """
        Approve enrollment
        Transition: SUBMITTED → APPROVED
        """
        enrollment = await self._get_enrollment(enrollment_id)

        if not can_transition(enrollment.status.value, EnrollmentAction.APPROVE.value):
            raise ValueError(f"Cannot approve from status {enrollment.status}")

        enrollment.status = EnrollmentStatus.APPROVED
        enrollment.approved_by = approved_by
        enrollment.approved_date = datetime.utcnow()

        return await self.enrollment_repo.update(enrollment)

    async def start_training(self, enrollment_id: int) -> TrainingEnrollment:
        """
        Start training
        Transition: APPROVED → IN_PROGRESS
        """
        enrollment = await self._get_enrollment(enrollment_id)

        # Business rule check
        can_start, start_error = can_start_training(enrollment.status.value, enrollment.approved_date)
        if not can_start:
            raise ValueError(start_error)

        if not can_transition(enrollment.status.value, EnrollmentAction.START.value):
            raise ValueError(f"Cannot start from status {enrollment.status}")

        enrollment.status = EnrollmentStatus.IN_PROGRESS
        enrollment.started_date = datetime.utcnow()

        # Execute state entry actions
        entry_actions = get_state_entry_actions(EnrollmentState.IN_PROGRESS.value)
        # (можно отправить welcome email, создать задачи, etc.)

        return await self.enrollment_repo.update(enrollment)

    async def update_progress(
        self,
        enrollment_id: int,
        data: EnrollmentProgressUpdate
    ) -> TrainingEnrollment:
        """Update training progress with smart auto-complete"""
        enrollment = await self._get_enrollment(enrollment_id)
        program = await self.get_program(enrollment.program_id)

        if enrollment.status != EnrollmentStatus.IN_PROGRESS:
            raise ValueError("Can only update progress for in-progress enrollments")

        # Validate progress
        validate_progress_update({
            "progress_percentage": data.progress_percentage,
            "current_progress": enrollment.progress_percentage,
        })

        # Update progress
        enrollment.progress_percentage = data.progress_percentage
        if data.modules_completed:
            enrollment.modules_completed = data.modules_completed
        if data.time_spent_minutes:
            enrollment.time_spent_hours = (
                enrollment.time_spent_hours or 0
            ) + (data.time_spent_minutes / 60.0)

        # Update last activity
        enrollment.last_activity_date = datetime.utcnow()

        # Check for smart auto-complete
        should_complete, reason = should_auto_complete(
            enrollment.progress_percentage,
            enrollment.time_spent_hours * 60 if enrollment.time_spent_hours else None,
            program.duration_hours,
            enrollment.status.value
        )

        if should_complete:
            # Auto-transition to COMPLETED
            enrollment.status = EnrollmentStatus.COMPLETED
            enrollment.completion_date = datetime.utcnow()

            # Publish auto-complete event (if eventbus available)
            try:
                from shared.eventbus import get_eventbus
                eventbus = get_eventbus()
                await eventbus.publish(
                    "training.auto_completed",
                    {
                        "enrollment_id": enrollment.id,
                        "person_id": enrollment.person_id,
                        "program_id": enrollment.program_id,
                        "reason": reason,
                    },
                    tenant_id=enrollment.tenant_id
                )
            except Exception as e:
                # Don't fail if event publishing fails
                print(f"Failed to publish auto-complete event: {e}")

        return await self.enrollment_repo.update(enrollment)

    async def complete_training(self, enrollment_id: int) -> TrainingEnrollment:
        """
        Complete training
        Transition: IN_PROGRESS → COMPLETED
        """
        enrollment = await self._get_enrollment(enrollment_id)

        # Business rule check
        can_complete, complete_error = can_complete_training(
            enrollment.status.value,
            enrollment.progress_percentage,
            enrollment.time_spent_hours * 60 if enrollment.time_spent_hours else None
        )
        if not can_complete:
            raise ValueError(complete_error)

        if not can_transition(enrollment.status.value, EnrollmentAction.COMPLETE.value):
            raise ValueError(f"Cannot complete from status {enrollment.status}")

        enrollment.status = EnrollmentStatus.COMPLETED
        enrollment.completion_date = datetime.utcnow()

        return await self.enrollment_repo.update(enrollment)

    async def submit_assessment(
        self,
        enrollment_id: int,
        data: EnrollmentAssessment
    ) -> TrainingEnrollment:
        """
        Submit assessment result with retry logic
        - Maximum 3 attempts allowed
        - Auto-fail enrollment after max attempts exceeded
        Transition: COMPLETED → ASSESSED (or FAILED)
        """
        enrollment = await self._get_enrollment(enrollment_id)
        program = await self.get_program(enrollment.program_id)

        if enrollment.status not in [EnrollmentStatus.COMPLETED, EnrollmentStatus.ASSESSED]:
            raise ValueError("Can only assess completed training")

        # Check assessment attempts limit (max 3)
        attempts_valid, attempts_error = validate_assessment_attempts(
            enrollment.assessment_attempts,
            max_attempts=3
        )
        if not attempts_valid:
            raise ValueError(attempts_error)

        # Validate score
        valid, error = validate_assessment_score(data.assessment_score, program.passing_score)
        if not valid:
            raise ValueError(error)

        # Increment attempts
        enrollment.assessment_attempts = (enrollment.assessment_attempts or 0) + 1

        # Determine result
        result = determine_assessment_result(
            data.assessment_score,
            program.passing_score
        )

        # Update enrollment
        enrollment.assessment_score = data.assessment_score
        enrollment.assessment_date = data.assessment_date or datetime.utcnow()
        enrollment.assessment_type = data.assessment_type
        enrollment.assessor = data.assessor
        enrollment.assessment_feedback = data.feedback
        enrollment.assessment_passed = result["passed"]

        # Handle pass/fail
        if result["passed"]:
            enrollment.status = EnrollmentStatus.ASSESSED
        else:
            # Check if max attempts reached
            if enrollment.assessment_attempts >= 3:
                # Auto-fail enrollment
                enrollment.status = EnrollmentStatus.FAILED

                # Publish fail event
                try:
                    from shared.eventbus import get_eventbus
                    eventbus = get_eventbus()
                    await eventbus.publish(
                        "training.assessment_failed",
                        {
                            "enrollment_id": enrollment.id,
                            "person_id": enrollment.person_id,
                            "program_id": enrollment.program_id,
                            "attempts": enrollment.assessment_attempts,
                            "final_score": data.assessment_score,
                        },
                        tenant_id=enrollment.tenant_id
                    )
                except Exception as e:
                    print(f"Failed to publish assessment failed event: {e}")
            else:
                # Allow retry - keep status as COMPLETED
                enrollment.status = EnrollmentStatus.COMPLETED

        return await self.enrollment_repo.update(enrollment)

    async def issue_certification(self, enrollment_id: int) -> TrainingEnrollment:
        """
        Issue certification with expiry calculation
        - Auto-calculates expiry date based on program validity_months
        Transition: ASSESSED → CERTIFIED
        """
        enrollment = await self._get_enrollment(enrollment_id)
        program = await self.get_program(enrollment.program_id)

        # Business rule check
        can_certify, certify_error = can_issue_certification(
            enrollment.status.value,
            enrollment.assessment_passed,
            program.certification_awarded
        )
        if not can_certify:
            raise ValueError(certify_error)

        if not can_transition(enrollment.status.value, EnrollmentAction.CERTIFY.value):
            raise ValueError(f"Cannot certify from status {enrollment.status}")

        # Issue certification
        certification_date = datetime.utcnow()
        enrollment.status = EnrollmentStatus.CERTIFIED
        enrollment.certification_issued = True
        enrollment.certification_date = certification_date
        enrollment.certification_number = f"CERT-{enrollment.tenant_id}-{enrollment.id}"

        # Calculate expiry date if program has validity period
        if program.certification_validity_months:
            enrollment.certification_expiry_date = calculate_certification_expiry(
                certification_date,
                program.certification_validity_months
            )

        # Publish certification event
        try:
            from shared.eventbus import get_eventbus
            eventbus = get_eventbus()
            await eventbus.publish(
                "training.certified",
                {
                    "enrollment_id": enrollment.id,
                    "person_id": enrollment.person_id,
                    "program_id": enrollment.program_id,
                    "certification_number": enrollment.certification_number,
                    "certification_date": certification_date.isoformat(),
                    "expiry_date": enrollment.certification_expiry_date.isoformat() if enrollment.certification_expiry_date else None,
                },
                tenant_id=enrollment.tenant_id
            )
        except Exception as e:
            print(f"Failed to publish certification event: {e}")

        return await self.enrollment_repo.update(enrollment)

    # ========================================================================
    # HELPERS
    # ========================================================================

    async def _get_enrollment(self, enrollment_id: int) -> TrainingEnrollment:
        """Get enrollment with validation"""
        enrollment = await self.enrollment_repo.get_by_id(enrollment_id)
        if not enrollment:
            raise ValueError(f"Enrollment {enrollment_id} not found")
        return enrollment

    async def get_enrollment(self, enrollment_id: int) -> TrainingEnrollment:
        """Public get enrollment"""
        return await self._get_enrollment(enrollment_id)

    async def list_enrollments_by_person(
        self,
        tenant_id: str,
        person_id: str,
        status: Optional[EnrollmentStatus] = None
    ) -> List[TrainingEnrollment]:
        """List enrollments for person"""
        return await self.enrollment_repo.list_by_person(
            tenant_id, person_id, status
        )

    async def list_enrollments_by_program(
        self,
        program_id: int,
        status: Optional[EnrollmentStatus] = None
    ) -> List[TrainingEnrollment]:
        """List enrollments for program"""
        return await self.enrollment_repo.list_by_program(program_id, status)
