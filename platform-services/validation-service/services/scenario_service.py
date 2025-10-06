"""
Scenario Service
Business logic for exercise scenario management
"""

from typing import List, Optional, Dict
from repositories.repository import ValidationRepository
from models.database import ExerciseScenario as ExerciseScenarioDB


class ScenarioService:
    """Scenario business logic service"""

    def __init__(self, repository: ValidationRepository):
        self.repo = repository

    async def create_scenario(self, scenario_data: Dict) -> ExerciseScenarioDB:
        """Create new exercise scenario"""
        # Set defaults
        scenario_data["reusable"] = True
        scenario_data["times_used"] = 0

        return await self.repo.create_scenario(scenario_data)

    async def list_scenarios(
        self,
        tenant_id: str,
        scenario_type: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[ExerciseScenarioDB]:
        """List exercise scenarios with filters"""
        return await self.repo.list_scenarios(tenant_id, scenario_type, category)

    async def get_scenario(self, scenario_id: int) -> ExerciseScenarioDB:
        """Get scenario by ID"""
        scenario = await self.repo.get_scenario(scenario_id)
        if not scenario:
            raise ValueError("Scenario not found")
        return scenario
