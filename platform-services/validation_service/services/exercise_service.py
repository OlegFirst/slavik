"""
Exercise Service
Business logic for exercise management
"""

from typing import List, Optional, Dict
from datetime import datetime
from repositories.repository import ValidationRepository
from workflows import can_start_exercise, can_complete_exercise
from models.database import Exercise as ExerciseDB
from models.domain import ExerciseType, ExerciseStatus


class ExerciseService:
    """Exercise business logic service"""

    def __init__(self, repository: ValidationRepository):
        self.repo = repository

    async def create_exercise(self, exercise_data: Dict) -> ExerciseDB:
        """Create new exercise with validation"""
        # Check for duplicate code
        existing = await self.repo.get_exercise_by_code(exercise_data["exercise_code"])
        if existing:
            raise ValueError(f"Exercise code {exercise_data['exercise_code']} already exists")

        # Set defaults
        exercise_data["status"] = ExerciseStatus.PLANNED
        exercise_data["corrective_actions_required"] = 0
        exercise_data["corrective_actions_completed"] = 0

        return await self.repo.create_exercise(exercise_data)

    async def start_exercise(self, exercise_id: int) -> ExerciseDB:
        """Start exercise with workflow validation"""
        exercise = await self.repo.get_exercise(exercise_id)
        if not exercise:
            raise ValueError("Exercise not found")

        # Validate transition
        can_start, error = can_start_exercise(exercise)
        if not can_start:
            raise ValueError(error)

        # Update exercise
        updates = {
            "status": ExerciseStatus.IN_PROGRESS,
            "actual_start_date": datetime.utcnow()
        }
        return await self.repo.update_exercise(exercise_id, updates)

    async def complete_exercise(self, exercise_id: int) -> ExerciseDB:
        """Complete exercise with workflow validation"""
        exercise = await self.repo.get_exercise(exercise_id)
        if not exercise:
            raise ValueError("Exercise not found")

        can_complete, error = can_complete_exercise(exercise)
        if not can_complete:
            raise ValueError(error)

        # Calculate duration
        updates = {
            "status": ExerciseStatus.COMPLETED,
            "actual_end_date": datetime.utcnow()
        }

        if exercise.actual_start_date:
            duration = (updates["actual_end_date"] - exercise.actual_start_date).total_seconds() / 3600
            updates["actual_duration_hours"] = round(duration, 2)

        return await self.repo.update_exercise(exercise_id, updates)

    async def list_exercises(
        self,
        tenant_id: str,
        status: Optional[ExerciseStatus] = None,
        exercise_type: Optional[ExerciseType] = None
    ) -> List[ExerciseDB]:
        """List exercises with filters"""
        status_str = status.value if status else None
        type_str = exercise_type.value if exercise_type else None
        return await self.repo.list_exercises(tenant_id, status_str, type_str)

    async def get_exercise(self, exercise_id: int) -> ExerciseDB:
        """Get exercise by ID"""
        exercise = await self.repo.get_exercise(exercise_id)
        if not exercise:
            raise ValueError("Exercise not found")
        return exercise

    async def add_observation(self, exercise_id: int, observation_data: Dict) -> "ExerciseObservationDB":
        """Add observation to exercise"""
        from models.domain import ObservationType

        # Verify exercise exists
        exercise = await self.repo.get_exercise(exercise_id)
        if not exercise:
            raise ValueError("Exercise not found")

        # Set defaults
        if "timestamp" not in observation_data or observation_data["timestamp"] is None:
            observation_data["timestamp"] = datetime.utcnow()

        # Set corrective_action_required based on observation type
        observation_data["corrective_action_required"] = (
            observation_data["observation_type"] in [ObservationType.WEAKNESS, ObservationType.GAP]
        )

        observation_data["exercise_id"] = exercise_id
        return await self.repo.create_observation(observation_data)

    async def generate_report(self, exercise_id: int) -> Dict:
        """Generate exercise report"""
        from models.domain import ObservationType

        # Get exercise
        exercise = await self.repo.get_exercise(exercise_id)
        if not exercise:
            raise ValueError("Exercise not found")

        # Get observations
        observations = await self.repo.list_observations_for_exercise(exercise_id)

        # Get actions
        actions = await self.repo.list_actions_for_exercise(exercise_id)

        # Build report
        report = {
            "exercise": {
                "exercise_code": exercise.exercise_code,
                "exercise_name": exercise.exercise_name,
                "exercise_type": exercise.exercise_type.value,
                "planned_date": exercise.planned_date.isoformat() if exercise.planned_date else None,
                "actual_start": exercise.actual_start_date.isoformat() if exercise.actual_start_date else None,
                "actual_end": exercise.actual_end_date.isoformat() if exercise.actual_end_date else None,
                "duration_hours": exercise.actual_duration_hours,
                "facilitator": exercise.facilitator,
                "participants_count": len(exercise.participants) if exercise.participants else 0,
            },
            "objectives": {
                "total": len(exercise.objectives) if exercise.objectives else 0,
                "met": len(exercise.objectives_met) if exercise.objectives_met else 0,
            },
            "observations": {
                "total": len(observations),
                "strengths": len([o for o in observations if o.observation_type == ObservationType.STRENGTH]),
                "weaknesses": len([o for o in observations if o.observation_type == ObservationType.WEAKNESS]),
                "gaps": len([o for o in observations if o.observation_type == ObservationType.GAP]),
                "details": [
                    {
                        "type": o.observation_type.value,
                        "severity": o.severity.value,
                        "title": o.title,
                        "description": o.description,
                    }
                    for o in observations
                ],
            },
            "corrective_actions": {
                "total": len(actions),
                "open": len([a for a in actions if a.status == 'open']),
                "in_progress": len([a for a in actions if a.status == 'in_progress']),
                "completed": len([a for a in actions if a.status == 'completed']),
            },
            "lessons_learned": exercise.lessons_learned,
            "overall_success": exercise.overall_success,
        }

        return report
