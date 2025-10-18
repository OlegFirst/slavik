"""
Scenario Orchestrator Integration Client

REAL integration with existing Scenario Orchestrator service (Port 8085)
for AI-powered scenario generation and learning accumulation.

This integrates with the existing working service at:
/platform-services/simulation/scenarios/scenario_orchestrator/
"""

import logging
from typing import Dict, List, Optional, Any
import httpx

from models.pydantic_models import SimulationResult
from config.settings import Settings

logger = logging.getLogger(__name__)


class ScenarioOrchestratorClient:
    """
    Existing Scenario Orchestrator integration client

    Integrates with the working Scenario Orchestrator service that provides:
    - AI-powered scenario generation (via AI Orchestrator)
    - Learning accumulation system
    - JaamSim configuration generation
    - Experience-based insights
    - Continuous improvement recommendations

    Service Location: /scenarios/scenario_orchestrator/main.py
    Port: 8085
    """

    def __init__(self, settings: Settings):
        """
        Initialize Scenario Orchestrator client

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.base_url = settings.scenario_orchestrator_url
        self.enabled = settings.scenario_orchestrator_enabled
        self.timeout = 60.0  # Longer timeout for AI generation

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout
        )

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    # ========================================================================
    # AI SCENARIO GENERATION
    # ========================================================================

    async def generate_ai_scenario(
        self,
        category: str,
        complexity: int = 3,
        duration_hours: int = 4,
        participants: int = 10,
        affected_systems: Optional[List[str]] = None,
        custom_objectives: Optional[List[str]] = None,
        organization_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI-powered scenario using existing Scenario Orchestrator

        Uses the working AI generation pipeline that:
        1. Builds AI prompt from requirements
        2. Queries AI Orchestrator for generation
        3. Formats response into structured scenario
        4. Generates JaamSim configs (if complexity >= 4)
        5. Saves to file system or Odoo

        Args:
            category: Scenario category
                - epidemic
                - blackout
                - cyber
                - supply
                - natural
                - terrorism
            complexity: Complexity level (1-5)
                - 1-2: Simple tabletop
                - 3: Standard simulation
                - 4-5: Full-scale with JaamSim
            duration_hours: Exercise duration
            participants: Number of participants
            affected_systems: List of affected systems
            custom_objectives: Custom exercise objectives
            organization_context: Organization context for customization

        Returns:
            Generated scenario data with:
            - scenario_id: Unique ID
            - title: Scenario title
            - file_path: Path to saved scenario
            - ai_generated: True
            - jaamsim_config: JaamSim config (if applicable)
        """
        if not self.enabled:
            logger.debug("Scenario Orchestrator disabled, skipping AI generation")
            return {}

        try:
            logger.info(f"Requesting AI scenario generation: {category}, complexity={complexity}")

            response = await self.client.post(
                "/scenarios/generate",
                json={
                    "category": category,
                    "complexity": complexity,
                    "duration_hours": duration_hours,
                    "participants": participants,
                    "affected_systems": affected_systems or [],
                    "custom_objectives": custom_objectives or [],
                    "organization_context": organization_context
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"AI scenario generated: {result.get('scenario_id')}")
            logger.debug(f"Scenario title: {result.get('title')}")

            return result

        except httpx.HTTPError as e:
            logger.error(f"AI scenario generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def get_available_scenarios(self) -> Dict[str, Any]:
        """
        Get available scenarios from Odoo BCM Scenario Hub

        Returns:
            List of available scenarios from Odoo integration
        """
        if not self.enabled:
            return {"scenarios": [], "source": "disabled"}

        try:
            response = await self.client.get("/scenarios/available")
            response.raise_for_status()
            result = response.json()

            logger.info(f"Retrieved {len(result.get('scenarios', []))} scenarios from Odoo")
            return result

        except httpx.HTTPError as e:
            logger.warning(f"Failed to get available scenarios: {e}")
            return {"scenarios": [], "source": "error", "error": str(e)}

    # ========================================================================
    # LEARNING SYSTEM INTEGRATION
    # ========================================================================

    async def collect_exercise_result(
        self,
        exercise_id: str,
        scenario_id: str,
        template_id: str,
        results: SimulationResult
    ) -> Dict[str, Any]:
        """
        Submit exercise results to existing learning accumulation system

        The existing system:
        1. Stores exercise result
        2. Updates scenario learning data
        3. Accumulates patterns (successful elements, common issues)
        4. Calculates effectiveness metrics
        5. Generates AI-powered improvement recommendations (after 3+ uses)
        6. Notifies AI Orchestrator of learning data

        Args:
            exercise_id: Exercise/simulation ID
            scenario_id: Scenario ID
            template_id: Template ID
            results: Simulation results

        Returns:
            Learning collection response with:
            - status: success/error
            - scenario_learning_updated: bool
            - total_scenario_uses: int
            - avg_effectiveness: float
        """
        if not self.enabled:
            logger.debug("Scenario Orchestrator disabled, skipping learning collection")
            return {}

        try:
            # Convert SimulationResult to ExerciseResult format
            exercise_result = {
                "exercise_id": exercise_id,
                "scenario_id": scenario_id,
                "template_id": template_id,
                "exercise_type": results.engine_used,
                "duration_actual_hours": results.duration_seconds / 3600,
                "participants_count": len(results.participant_performance),
                "success_metrics": results.metrics,
                "participant_feedback": results.participant_performance,
                "simulation_metrics": results.detailed_metrics,
                "lessons_learned": results.lessons_learned,
                "improvement_suggestions": results.recommendations,
                "effectiveness_score": results.quality_score
            }

            logger.info(f"Submitting exercise result to learning system: {exercise_id}")

            response = await self.client.post(
                "/learning/exercise-result",
                json=exercise_result
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"Learning data collected: uses={result.get('total_scenario_uses')}, "
                       f"avg_effectiveness={result.get('avg_effectiveness')}")

            return result

        except httpx.HTTPError as e:
            logger.warning(f"Learning collection failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def get_scenario_insights(
        self,
        scenario_id: str
    ) -> Dict[str, Any]:
        """
        Get accumulated learning insights for scenario

        Returns insights from experience accumulation:
        - Total uses
        - Average effectiveness
        - Effectiveness trend (last 5)
        - Successful elements
        - Common issues
        - AI-powered recommendations
        - Improvement areas

        Args:
            scenario_id: Scenario ID

        Returns:
            Learning insights dictionary
        """
        if not self.enabled:
            return {
                "insights": {
                    "total_uses": 0,
                    "avg_effectiveness": 0,
                    "recommendations": ["Service disabled"]
                }
            }

        try:
            response = await self.client.get(
                f"/learning/scenario/{scenario_id}/insights"
            )
            response.raise_for_status()
            result = response.json()

            insights = result.get("insights", {})
            logger.info(f"Retrieved insights for {scenario_id}: "
                       f"uses={insights.get('total_uses')}, "
                       f"effectiveness={insights.get('avg_effectiveness')}")

            return result

        except httpx.HTTPError as e:
            logger.warning(f"Insights retrieval failed: {e}")
            return {
                "status": "error",
                "scenario_id": scenario_id,
                "insights": {},
                "error": str(e)
            }

    async def get_learning_dashboard(self) -> Dict[str, Any]:
        """
        Get platform-wide learning dashboard data

        Returns aggregated learning data:
        - Total scenarios with learning data
        - Total exercises completed
        - Average platform effectiveness
        - Recent exercise results (last 10)
        - Top performing scenarios (top 5)
        - Scenarios needing improvement (effectiveness < 6.0)

        Returns:
            Dashboard data dictionary
        """
        if not self.enabled:
            return {
                "dashboard": {
                    "total_scenarios_with_data": 0,
                    "total_exercises_completed": 0,
                    "avg_platform_effectiveness": 0
                }
            }

        try:
            response = await self.client.get("/learning/dashboard")
            response.raise_for_status()
            result = response.json()

            dashboard = result.get("dashboard", {})
            logger.info(f"Learning dashboard: scenarios={dashboard.get('total_scenarios_with_data')}, "
                       f"exercises={dashboard.get('total_exercises_completed')}, "
                       f"avg_effectiveness={dashboard.get('avg_platform_effectiveness')}")

            return result

        except httpx.HTTPError as e:
            logger.warning(f"Dashboard retrieval failed: {e}")
            return {
                "status": "error",
                "dashboard": {},
                "error": str(e)
            }

    # ========================================================================
    # JAAMSIM CONFIGURATION
    # ========================================================================

    async def get_jaamsim_config(
        self,
        category: str,
        complexity: int,
        duration_hours: int,
        participants: int
    ) -> Optional[str]:
        """
        Get JaamSim configuration from existing generator

        The existing generator creates JaamSim .cfg files with:
        - Scenario-specific distributions (impact, recovery)
        - Simulation entities (generators, queues, servers, sinks)
        - Participant capacity configuration
        - Exercise duration settings

        Note: This is extracted from the scenario generation response
        when complexity >= 4

        Args:
            category: Scenario category
            complexity: Complexity level (must be >= 4 for JaamSim)
            duration_hours: Exercise duration
            participants: Number of participants

        Returns:
            JaamSim configuration string or None
        """
        if not self.enabled or complexity < 4:
            logger.debug("JaamSim config not applicable (disabled or complexity < 4)")
            return None

        try:
            # Generate scenario to get JaamSim config
            result = await self.generate_ai_scenario(
                category=category,
                complexity=complexity,
                duration_hours=duration_hours,
                participants=participants
            )

            jaamsim_config = result.get("jaamsim_config")

            if jaamsim_config:
                logger.info(f"JaamSim config retrieved for {category} scenario")
            else:
                logger.warning("JaamSim config not generated (complexity may be < 4)")

            return jaamsim_config

        except Exception as e:
            logger.error(f"Failed to get JaamSim config: {e}")
            return None

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def supports_jaamsim(self, complexity: int) -> bool:
        """
        Check if scenario complexity supports JaamSim

        Args:
            complexity: Complexity level (1-5)

        Returns:
            True if complexity >= 4 (full-scale exercises)
        """
        return complexity >= 4

    def get_scenario_level(self, complexity: int) -> str:
        """
        Get exercise level from complexity

        Args:
            complexity: Complexity level (1-5)

        Returns:
            "tabletop" or "full"
        """
        return "full" if complexity >= 4 else "tabletop"

    # ========================================================================
    # HEALTH CHECK
    # ========================================================================

    async def health_check(self) -> Dict:
        """
        Check Scenario Orchestrator service health

        Returns:
            Health status dictionary with:
            - status: healthy/unhealthy/disabled
            - connected: bool
            - service: service name
            - version: service version
            - capabilities: list of capabilities
        """
        if not self.enabled:
            return {
                "status": "disabled",
                "connected": False,
                "service": "scenario_orchestrator"
            }

        try:
            response = await self.client.get("/health", timeout=5.0)
            response.raise_for_status()
            health_data = response.json()

            return {
                "status": "healthy",
                "connected": True,
                "service": health_data.get("service", "scenario_orchestrator"),
                "version": health_data.get("version", "unknown"),
                "capabilities": health_data.get("capabilities", []),
                "response": health_data
            }

        except httpx.HTTPError as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "service": "scenario_orchestrator",
                "error": str(e)
            }
