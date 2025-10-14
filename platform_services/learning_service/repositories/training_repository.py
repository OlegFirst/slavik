"""
Training Repository
Data access layer for Training Programs and Enrollments
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.database import (
    TrainingProgram,
    TrainingEnrollment,
    ProgramStatus,
    EnrollmentStatus
)


class TrainingProgramRepository:
    """Repository for Training Programs"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, program: TrainingProgram) -> TrainingProgram:
        """Create training program"""
        self.session.add(program)
        await self.session.flush()
        await self.session.refresh(program)
        return program

    async def get_by_id(self, program_id: int) -> Optional[TrainingProgram]:
        """Get program by ID"""
        result = await self.session.execute(
            select(TrainingProgram).where(TrainingProgram.id == program_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, tenant_id: str, program_code: str) -> Optional[TrainingProgram]:
        """Get program by code"""
        result = await self.session.execute(
            select(TrainingProgram).where(
                and_(
                    TrainingProgram.tenant_id == tenant_id,
                    TrainingProgram.program_code == program_code
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: str,
        status: Optional[ProgramStatus] = None,
        program_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TrainingProgram]:
        """List programs for tenant"""
        query = select(TrainingProgram).where(TrainingProgram.tenant_id == tenant_id)

        if status:
            query = query.where(TrainingProgram.status == status)
        if program_type:
            query = query.where(TrainingProgram.program_type == program_type)

        query = query.offset(skip).limit(limit).order_by(TrainingProgram.created_at.desc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, program: TrainingProgram) -> TrainingProgram:
        """Update program"""
        await self.session.flush()
        await self.session.refresh(program)
        return program

    async def delete(self, program_id: int) -> bool:
        """Delete program"""
        program = await self.get_by_id(program_id)
        if program:
            await self.session.delete(program)
            await self.session.flush()
            return True
        return False

    async def get_enrollment_count(self, program_id: int) -> int:
        """Get enrollment count for program"""
        result = await self.session.execute(
            select(func.count(TrainingEnrollment.id)).where(
                TrainingEnrollment.program_id == program_id
            )
        )
        return result.scalar() or 0

    async def get_completion_rate(self, program_id: int) -> float:
        """Get completion rate for program"""
        total = await self.get_enrollment_count(program_id)
        if total == 0:
            return 0.0

        result = await self.session.execute(
            select(func.count(TrainingEnrollment.id)).where(
                and_(
                    TrainingEnrollment.program_id == program_id,
                    TrainingEnrollment.status.in_([
                        EnrollmentStatus.COMPLETED,
                        EnrollmentStatus.ASSESSED,
                        EnrollmentStatus.CERTIFIED
                    ])
                )
            )
        )
        completed = result.scalar() or 0
        return round((completed / total) * 100, 2)


class TrainingEnrollmentRepository:
    """Repository for Training Enrollments"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, enrollment: TrainingEnrollment) -> TrainingEnrollment:
        """Create enrollment"""
        self.session.add(enrollment)
        await self.session.flush()
        await self.session.refresh(enrollment)
        return enrollment

    async def get_by_id(self, enrollment_id: int) -> Optional[TrainingEnrollment]:
        """Get enrollment by ID"""
        result = await self.session.execute(
            select(TrainingEnrollment).where(TrainingEnrollment.id == enrollment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_person_and_program(
        self,
        tenant_id: str,
        person_id: str,
        program_id: int
    ) -> Optional[TrainingEnrollment]:
        """Get enrollment for person in program"""
        result = await self.session.execute(
            select(TrainingEnrollment).where(
                and_(
                    TrainingEnrollment.tenant_id == tenant_id,
                    TrainingEnrollment.person_id == person_id,
                    TrainingEnrollment.program_id == program_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_by_person(
        self,
        tenant_id: str,
        person_id: str,
        status: Optional[EnrollmentStatus] = None
    ) -> List[TrainingEnrollment]:
        """List enrollments for person"""
        query = select(TrainingEnrollment).where(
            and_(
                TrainingEnrollment.tenant_id == tenant_id,
                TrainingEnrollment.person_id == person_id
            )
        )

        if status:
            query = query.where(TrainingEnrollment.status == status)

        query = query.order_by(TrainingEnrollment.enrolled_date.desc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_program(
        self,
        program_id: int,
        status: Optional[EnrollmentStatus] = None
    ) -> List[TrainingEnrollment]:
        """List enrollments for program"""
        query = select(TrainingEnrollment).where(
            TrainingEnrollment.program_id == program_id
        )

        if status:
            query = query.where(TrainingEnrollment.status == status)

        query = query.order_by(TrainingEnrollment.enrolled_date.desc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, enrollment: TrainingEnrollment) -> TrainingEnrollment:
        """Update enrollment"""
        await self.session.flush()
        await self.session.refresh(enrollment)
        return enrollment

    async def delete(self, enrollment_id: int) -> bool:
        """Delete enrollment"""
        enrollment = await self.get_by_id(enrollment_id)
        if enrollment:
            await self.session.delete(enrollment)
            await self.session.flush()
            return True
        return False
