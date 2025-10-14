"""
AI Orchestrator Integration Client

REAL integration with AI Orchestrator service for:
- Specification validation
- Decision-making during simulations
- Result analysis
- Pattern storage in Memory System
"""

import logging
from typing import Dict, List, Optional, Any
import httpx

from models.pydantic_models import TaskSpecification, SimulationResult
from config.settings import Settings

logger = logging.getLogger(__name__)


class AIOrchestratorClient:
    """
    AI Orchestrator integration client

    Provides:
    - Pre-simulation validation
    - Real-time decision support
    - Post-simulation analysis
    - Memory System integration
    """

    def __init__(self, settings: Settings):
        """
        Initialize orchestrator client

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.base_url = settings.ai_orchestrator_url
        self.enabled = settings.ai_orchestrator_enabled
        self.timeout = 30.0

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout
        )

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    # ========================================================================
    # PRE-SIMULATION: Validation
    # ========================================================================

    async def validate_specification(
        self,
        specification: TaskSpecification,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Validate simulation specification before execution

        Uses AI Orchestrator to:
        - Check specification completeness
        - Assess feasibility
        - Identify risks
        - Suggest improvements

        Args:
            specification: Task specification
            context: Additional context (previous simulations, organization info)

        Returns:
            Validation result with suggestions
        """
        if not self.enabled:
            logger.debug("AI Orchestrator disabled, skipping validation")
            return {
                "is_valid": True,
                "confidence": 1.0,
                "suggestions": [],
                "risk_assessment": {}
            }

        try:
            response = await self.client.post(
                "/api/v1/validate/specification",
                json={
                    "specification": specification.model_dump(),
                    "simulation_context": context or {}
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"Specification validated: {result.get('is_valid')} (confidence: {result.get('confidence')})")
            return result

        except httpx.HTTPError as e:
            logger.error(f"Orchestrator validation request failed: {e}")
            # Graceful degradation
            return {
                "is_valid": True,
                "confidence": 0.5,
                "suggestions": [],
                "error": str(e)
            }

    async def suggest_engine(
        self,
        specification: TaskSpecification
    ) -> str:
        """
        Get AI recommendation for best simulation engine

        Args:
            specification: Task specification

        Returns:
            Recommended engine type
        """
        if not self.enabled:
            return "simpy"  # Default

        try:
            response = await self.client.post(
                "/api/v1/recommend/engine",
                json={"specification": specification.model_dump()}
            )
            response.raise_for_status()
            result = response.json()

            recommended = result.get("engine", "simpy")
            logger.info(f"Recommended engine: {recommended}")
            return recommended

        except httpx.HTTPError as e:
            logger.warning(f"Engine recommendation failed: {e}")
            return "simpy"  # Default fallback

    # ========================================================================
    # DURING SIMULATION: Real-time Decisions
    # ========================================================================

    async def decide_inject_timing(
        self,
        simulation_id: str,
        context: Dict,
        options: List[Dict]
    ) -> Dict:
        """
        Get AI decision for event injection timing

        Used during simulation to determine:
        - When to inject incidents
        - Which incidents to inject
        - Complexity escalation

        Args:
            simulation_id: Simulation ID
            context: Current simulation state (progress, participant status, events)
            options: Available injection options

        Returns:
            Decision with reasoning
        """
        if not self.enabled or not options:
            return options[0] if options else {}

        try:
            response = await self.client.post(
                "/api/v1/decide",
                json={
                    "decision_type": "inject_timing",
                    "context": {
                        "simulation_id": simulation_id,
                        **context
                    },
                    "options": options
                }
            )
            response.raise_for_status()
            result = response.json()

            decision = result.get("decision", {})
            logger.info(f"Injection decision: {decision.get('action')} - {decision.get('reason')}")
            return decision

        except httpx.HTTPError as e:
            logger.warning(f"Decision request failed: {e}")
            return options[0] if options else {}

    async def evaluate_participant_response(
        self,
        simulation_id: str,
        decision_data: Dict
    ) -> Dict:
        """
        Evaluate participant decision quality

        Args:
            simulation_id: Simulation ID
            decision_data: Decision made by participant

        Returns:
            Evaluation with score and feedback
        """
        if not self.enabled:
            return {"score": 0.8, "feedback": ""}

        try:
            response = await self.client.post(
                "/api/v1/evaluate/decision",
                json={
                    "simulation_id": simulation_id,
                    "decision": decision_data
                }
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.warning(f"Evaluation request failed: {e}")
            return {"score": 0.8, "feedback": ""}

    # ========================================================================
    # POST-SIMULATION: Analysis & Learning
    # ========================================================================

    async def analyze_results(
        self,
        simulation_id: str,
        results: SimulationResult,
        specification: TaskSpecification
    ) -> Dict:
        """
        Comprehensive AI analysis of simulation results

        Analyzes:
        - Performance vs objectives
        - Strengths and weaknesses
        - Patterns and insights
        - Recommendations for improvement

        Args:
            simulation_id: Simulation ID
            results: Simulation results
            specification: Original specification

        Returns:
            Analysis with insights and recommendations
        """
        if not self.enabled:
            return {
                "analysis": {
                    "strengths": [],
                    "weaknesses": [],
                    "patterns_identified": [],
                    "recommendations": []
                },
                "quality_score": 7.0,
                "contribution_worthy": False
            }

        try:
            response = await self.client.post(
                "/api/v1/analyze/simulation-results",
                json={
                    "simulation_id": simulation_id,
                    "results": results.model_dump(),
                    "specification": specification.model_dump()
                },
                timeout=60.0  # Analysis can take longer
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"Results analyzed: quality_score={result.get('quality_score')}, contribution_worthy={result.get('contribution_worthy')}")
            return result

        except httpx.HTTPError as e:
            logger.error(f"Result analysis failed: {e}")
            return {
                "analysis": {},
                "quality_score": 7.0,
                "contribution_worthy": False,
                "error": str(e)
            }

    async def generate_lessons_learned(
        self,
        simulation_id: str,
        results: SimulationResult
    ) -> List[str]:
        """
        Generate lessons learned from simulation

        Args:
            simulation_id: Simulation ID
            results: Simulation results

        Returns:
            List of lessons learned
        """
        if not self.enabled:
            return results.lessons_learned

        try:
            response = await self.client.post(
                "/api/v1/generate/lessons",
                json={
                    "simulation_id": simulation_id,
                    "results": results.model_dump()
                }
            )
            response.raise_for_status()
            result = response.json()

            lessons = result.get("lessons_learned", [])
            logger.info(f"Generated {len(lessons)} lessons learned")
            return lessons

        except httpx.HTTPError as e:
            logger.warning(f"Lesson generation failed: {e}")
            return results.lessons_learned

    # ========================================================================
    # MEMORY SYSTEM: Pattern Storage
    # ========================================================================

    async def store_simulation_pattern(
        self,
        simulation_id: str,
        pattern_data: Dict
    ) -> Optional[str]:
        """
        Store simulation pattern in Memory System

        Patterns stored in long-term memory for:
        - Future simulation improvement
        - Organizational learning
        - Best practice identification

        Args:
            simulation_id: Simulation ID
            pattern_data: Pattern information

        Returns:
            Memory ID or None
        """
        if not self.enabled:
            return None

        try:
            response = await self.client.post(
                "/api/v1/memory/store",
                json={
                    "memory_type": "simulation_pattern",
                    "content": {
                        "simulation_id": simulation_id,
                        **pattern_data
                    },
                    "layer": "long_term",
                    "retention_policy": "permanent"
                }
            )
            response.raise_for_status()
            result = response.json()

            memory_id = result.get("memory_id")
            logger.info(f"Pattern stored in memory: {memory_id}")
            return memory_id

        except httpx.HTTPError as e:
            logger.warning(f"Pattern storage failed: {e}")
            return None

    async def retrieve_similar_patterns(
        self,
        specification: TaskSpecification,
        limit: int = 5
    ) -> List[Dict]:
        """
        Retrieve similar simulation patterns from Memory System

        Args:
            specification: Task specification
            limit: Maximum patterns to retrieve

        Returns:
            List of similar patterns
        """
        if not self.enabled:
            return []

        try:
            response = await self.client.post(
                "/api/v1/memory/search",
                json={
                    "memory_type": "simulation_pattern",
                    "query": specification.goal,
                    "context": specification.context,
                    "limit": limit
                }
            )
            response.raise_for_status()
            result = response.json()

            patterns = result.get("patterns", [])
            logger.info(f"Retrieved {len(patterns)} similar patterns")
            return patterns

        except httpx.HTTPError as e:
            logger.warning(f"Pattern retrieval failed: {e}")
            return []

    # ========================================================================
    # HEALTH CHECK
    # ========================================================================

    async def health_check(self) -> Dict:
        """
        Check AI Orchestrator health

        Returns:
            Health status dictionary
        """
        if not self.enabled:
            return {
                "status": "disabled",
                "connected": False
            }

        try:
            response = await self.client.get("/health", timeout=5.0)
            response.raise_for_status()

            return {
                "status": "healthy",
                "connected": True,
                "response": response.json()
            }

        except httpx.HTTPError as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }
