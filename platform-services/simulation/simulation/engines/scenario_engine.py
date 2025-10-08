"""
Scenario Engine

Runs BCM exercise scenarios
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta
import httpx

sys.path.insert(0, str(Path(__file__).parent))
from base_engine import BaseSimulationEngine


class ScenarioEngine(BaseSimulationEngine):
    """
    Scenario execution engine for BCM exercises
    """

    def validate_parameters(self) -> bool:
        """Validate parameters"""
        required = ['scenario_id']

        for param in required:
            if param not in self.parameters:
                raise ValueError(f"Missing required parameter: {param}")

        return True

    async def run(self) -> Dict[str, Any]:
        """
        Run scenario exercise

        Parameters:
            - scenario_id: ID of scenario to run
            - twin_id: Optional Digital Twin to apply scenario to
            - participants: List of participant IDs
            - duration_override: Optional duration override

        Returns:
            Exercise results
        """
        self.validate_parameters()

        scenario_id = self.parameters['scenario_id']
        twin_id = self.parameters.get('twin_id')
        participants = self.parameters.get('participants', [])

        self.log_progress("Loading scenario", 0)

        # Get scenario details
        scenario = await self._get_scenario(scenario_id)

        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        self.log_progress("Scenario loaded", 20)

        # Initialize exercise
        exercise_state = {
            "scenario_id": scenario_id,
            "start_time": datetime.utcnow(),
            "participants": participants,
            "timeline": scenario.get('timeline', []),
            "injects_delivered": [],
            "decisions_made": [],
            "objectives_completed": []
        }

        # Get initial twin state if specified
        if twin_id:
            initial_state = await self._get_twin_state(twin_id)
            exercise_state['initial_twin_state'] = initial_state

        self.log_progress("Exercise initialized", 40)

        # Execute timeline (simulated - in real exercise this would be real-time)
        for i, timeline_event in enumerate(scenario.get('timeline', [])):
            progress = 40 + (i / len(scenario.get('timeline', []))) * 40

            # Deliver inject
            inject_result = await self._deliver_inject(timeline_event)
            exercise_state['injects_delivered'].append(inject_result)

            self.log_progress(f"Delivered inject: {timeline_event.get('title', 'Unknown')}", progress)

        self.log_progress("All injects delivered", 80)

        # Evaluate exercise
        evaluation = await self._evaluate_exercise(scenario, exercise_state)

        self.log_progress("Exercise evaluated", 100)

        return {
            "simulation_id": self.simulation_id,
            "scenario": scenario,
            "exercise_state": exercise_state,
            "evaluation": evaluation,
            "confidence": 0.80
        }

    async def _get_scenario(self, scenario_id: int) -> Dict[str, Any]:
        """Get scenario from database"""
        # In real implementation, query database
        # For now, return mock scenario
        return {
            "id": scenario_id,
            "title": "Ransomware Attack Simulation",
            "category": "cyber",
            "timeline": [
                {
                    "hour": 0,
                    "title": "Initial Detection",
                    "description": "IT monitoring detects unusual encryption activity",
                    "inject_type": "alert"
                },
                {
                    "hour": 1,
                    "title": "Ransomware Confirmed",
                    "description": "Multiple systems encrypted. Ransom note discovered.",
                    "inject_type": "escalation"
                },
                {
                    "hour": 2,
                    "title": "Crisis Team Activation",
                    "description": "BCM team convened. DR plan activation recommended.",
                    "inject_type": "decision_point"
                },
                {
                    "hour": 4,
                    "title": "Media Inquiry",
                    "description": "Local news outlet requesting statement about outage.",
                    "inject_type": "communication"
                }
            ],
            "success_metrics": [
                "Crisis team activated within 2 hours",
                "Stakeholder communication within 4 hours",
                "DR plan execution started within 3 hours"
            ]
        }

    async def _get_twin_state(self, twin_id: int) -> Dict[str, Any]:
        """Get Digital Twin state"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8030/api/twin/organizations/{twin_id}/state"
                )

                if response.status_code == 200:
                    return response.json()['state']

        except Exception as e:
            self.logger.error(f"Error getting twin state: {e}")

        return {}

    async def _deliver_inject(self, timeline_event: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver exercise inject"""
        return {
            "event": timeline_event,
            "delivered_at": datetime.utcnow().isoformat(),
            "status": "delivered"
        }

    async def _evaluate_exercise(self, scenario: Dict[str, Any], exercise_state: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate exercise performance"""

        total_injects = len(scenario.get('timeline', []))
        delivered_injects = len(exercise_state.get('injects_delivered', []))

        # Calculate completion rate
        completion_rate = (delivered_injects / total_injects) if total_injects > 0 else 0

        # Evaluate objectives (mock - in real exercise based on participant actions)
        objectives_met = len(scenario.get('success_metrics', [])) // 2  # Mock: assume 50% met

        effectiveness_score = (completion_rate * 0.6 + (objectives_met / len(scenario.get('success_metrics', []))) * 0.4) * 10

        return {
            "completion_rate": completion_rate,
            "injects_delivered": delivered_injects,
            "total_injects": total_injects,
            "objectives_met": objectives_met,
            "total_objectives": len(scenario.get('success_metrics', [])),
            "effectiveness_score": round(effectiveness_score, 2),
            "recommendations": [
                "Document lessons learned",
                "Update BCP based on exercise findings",
                "Schedule follow-up training for identified gaps"
            ]
        }
