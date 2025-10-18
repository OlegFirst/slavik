"""
Workflow Intelligence Integration Client

REAL integration with Workflow Intelligence service for:
- PDCA cycle creation and management
- Case Library storage (Simulation cases)
- Similar case search for learning
- Workflow process integration
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx

from models.pydantic_models import (
    TaskSpecification,
    SimulationResult,
    Simulation,
    PDCACyclePhase
)
from config.settings import Settings

logger = logging.getLogger(__name__)


class WorkflowIntelligenceClient:
    """
    Workflow Intelligence integration client

    Provides:
    - Automatic PDCA cycle creation after simulations
    - Simulation case storage in Case Library
    - Similar case search for learning
    - Workflow process integration
    """

    def __init__(self, settings: Settings):
        """
        Initialize Workflow Intelligence client

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.base_url = settings.workflow_intelligence_url
        self.enabled = settings.workflow_intelligence_enabled
        self.timeout = 30.0

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout
        )

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    # ========================================================================
    # PDCA CYCLE MANAGEMENT
    # ========================================================================

    async def create_pdca_cycle(
        self,
        simulation_id: str,
        specification: TaskSpecification,
        results: SimulationResult,
        organization_id: str,
        tenant_id: str
    ) -> Optional[str]:
        """
        Create PDCA cycle from simulation results

        Automatically creates a complete PDCA cycle:
        - PLAN: Original specification and objectives
        - DO: Simulation execution data
        - CHECK: Results analysis and metrics
        - ACT: Recommendations and improvements

        Args:
            simulation_id: Simulation ID
            specification: Original task specification
            results: Simulation results
            organization_id: Organization ID
            tenant_id: Tenant ID

        Returns:
            PDCA cycle ID or None
        """
        if not self.enabled:
            logger.debug("Workflow Intelligence disabled, skipping PDCA creation")
            return None

        try:
            # Prepare PDCA cycle data
            pdca_data = {
                "name": f"Simulation PDCA: {specification.goal[:50]}",
                "description": f"PDCA cycle created from simulation {simulation_id}",
                "source_type": "simulation",
                "source_id": simulation_id,
                "organization_id": organization_id,
                "tenant_id": tenant_id,

                # PLAN phase
                "plan": {
                    "objectives": [specification.goal],
                    "expected_outcomes": specification.expected_outcomes,
                    "constraints": specification.constraints,
                    "context": specification.context,
                    "success_criteria": results.success_criteria,
                    "planned_at": specification.created_at.isoformat() if specification.created_at else None
                },

                # DO phase
                "do": {
                    "execution_summary": {
                        "simulation_id": simulation_id,
                        "engine_used": results.engine_used,
                        "duration_seconds": results.duration_seconds,
                        "events_count": len(results.events),
                        "participants_count": len(results.participant_performance)
                    },
                    "actions_taken": self._extract_actions(results),
                    "data_collected": results.detailed_metrics,
                    "executed_at": results.completed_at.isoformat() if results.completed_at else None
                },

                # CHECK phase
                "check": {
                    "actual_results": {
                        "success_rate": results.overall_success_rate,
                        "metrics": results.metrics,
                        "kpis_achieved": results.kpis_achieved
                    },
                    "variance_analysis": self._calculate_variance(specification, results),
                    "strengths": self._extract_strengths(results),
                    "weaknesses": self._extract_weaknesses(results),
                    "checked_at": datetime.utcnow().isoformat()
                },

                # ACT phase
                "act": {
                    "recommendations": results.recommendations,
                    "improvements_identified": results.improvement_areas,
                    "lessons_learned": results.lessons_learned,
                    "next_steps": self._generate_next_steps(results),
                    "decided_at": datetime.utcnow().isoformat()
                },

                "metadata": {
                    "auto_generated": True,
                    "quality_score": results.quality_score
                }
            }

            response = await self.client.post(
                "/api/v1/pdca/cycles",
                json=pdca_data
            )
            response.raise_for_status()
            result = response.json()

            cycle_id = result.get("id")
            logger.info(f"PDCA cycle created: {cycle_id} for simulation {simulation_id}")
            return cycle_id

        except httpx.HTTPError as e:
            logger.error(f"PDCA cycle creation failed: {e}")
            return None

    async def update_pdca_phase(
        self,
        cycle_id: str,
        phase: PDCACyclePhase,
        phase_data: Dict[str, Any]
    ) -> bool:
        """
        Update specific PDCA phase

        Args:
            cycle_id: PDCA cycle ID
            phase: Phase to update (plan, do, check, act)
            phase_data: Updated phase data

        Returns:
            True if updated successfully
        """
        if not self.enabled:
            return False

        try:
            response = await self.client.patch(
                f"/api/v1/pdca/cycles/{cycle_id}/phases/{phase.value}",
                json=phase_data
            )
            response.raise_for_status()

            logger.info(f"PDCA phase {phase.value} updated for cycle {cycle_id}")
            return True

        except httpx.HTTPError as e:
            logger.warning(f"PDCA phase update failed: {e}")
            return False

    async def get_pdca_cycle(self, cycle_id: str) -> Optional[Dict]:
        """
        Get PDCA cycle by ID

        Args:
            cycle_id: PDCA cycle ID

        Returns:
            PDCA cycle data or None
        """
        if not self.enabled:
            return None

        try:
            response = await self.client.get(f"/api/v1/pdca/cycles/{cycle_id}")
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.warning(f"PDCA cycle retrieval failed: {e}")
            return None

    # ========================================================================
    # CASE LIBRARY INTEGRATION
    # ========================================================================

    async def create_simulation_case(
        self,
        simulation: Simulation,
        results: SimulationResult,
        specification: TaskSpecification,
        organization_id: str,
        tenant_id: str
    ) -> Optional[str]:
        """
        Store simulation as case in Case Library

        Creates a Simulation Case (Type 3) that can be:
        - Searched by other users
        - Used as learning material
        - Referenced in future simulations
        - Contributed to community if quality is high

        Args:
            simulation: Simulation instance
            results: Simulation results
            specification: Original specification
            organization_id: Organization ID
            tenant_id: Tenant ID

        Returns:
            Case ID or None
        """
        if not self.enabled:
            logger.debug("Workflow Intelligence disabled, skipping case creation")
            return None

        try:
            case_data = {
                "title": f"Simulation Case: {specification.goal[:50]}",
                "description": specification.goal,
                "case_type": "simulation",  # Type 3: Simulation Case
                "source_id": simulation.id,
                "organization_id": organization_id,
                "tenant_id": tenant_id,

                # Case content
                "context": {
                    "scenario": specification.context,
                    "initial_conditions": specification.constraints,
                    "objectives": [specification.goal]
                },

                "problem": {
                    "description": specification.goal,
                    "challenges": specification.expected_challenges or [],
                    "complexity_level": results.complexity_level
                },

                "solution": {
                    "approach": {
                        "engine": results.engine_used,
                        "configuration": simulation.engine_config.model_dump()
                    },
                    "actions_taken": self._extract_actions(results),
                    "timeline": self._build_timeline(results),
                    "resources_used": simulation.scenario.available_resources
                },

                "outcome": {
                    "success_rate": results.overall_success_rate,
                    "metrics_achieved": results.metrics,
                    "kpis_met": results.kpis_achieved,
                    "participant_performance": results.participant_performance
                },

                "lessons_learned": results.lessons_learned,
                "recommendations": results.recommendations,

                # Metadata for search and filtering
                "tags": self._generate_case_tags(specification, results),
                "category": specification.category if hasattr(specification, 'category') else "general",
                "difficulty_level": results.complexity_level,
                "duration_minutes": results.duration_seconds // 60,

                "quality_metrics": {
                    "quality_score": results.quality_score,
                    "completeness": self._calculate_completeness(results),
                    "contribution_worthy": results.quality_score >= 8.0
                },

                "metadata": {
                    "created_from": "simulation",
                    "simulation_id": simulation.id,
                    "auto_generated": True
                }
            }

            response = await self.client.post(
                "/api/v1/cases",
                json=case_data
            )
            response.raise_for_status()
            result = response.json()

            case_id = result.get("id")
            logger.info(f"Simulation case created: {case_id} from simulation {simulation.id}")
            return case_id

        except httpx.HTTPError as e:
            logger.error(f"Case creation failed: {e}")
            return None

    async def search_similar_cases(
        self,
        specification: TaskSpecification,
        limit: int = 10,
        min_quality: float = 7.0
    ) -> List[Dict]:
        """
        Search for similar cases in Case Library

        Uses RAG-based search to find relevant cases based on:
        - Goal similarity
        - Context similarity
        - Category/tags matching
        - Quality threshold

        Args:
            specification: Task specification to match
            limit: Maximum cases to return
            min_quality: Minimum quality score

        Returns:
            List of similar cases
        """
        if not self.enabled:
            return []

        try:
            response = await self.client.post(
                "/api/v1/cases/search",
                json={
                    "query": specification.goal,
                    "context": specification.context,
                    "case_type": "simulation",
                    "filters": {
                        "min_quality_score": min_quality
                    },
                    "limit": limit
                }
            )
            response.raise_for_status()
            result = response.json()

            cases = result.get("cases", [])
            logger.info(f"Found {len(cases)} similar cases for specification")
            return cases

        except httpx.HTTPError as e:
            logger.warning(f"Similar case search failed: {e}")
            return []

    async def get_case_by_id(self, case_id: str) -> Optional[Dict]:
        """
        Get case by ID

        Args:
            case_id: Case ID

        Returns:
            Case data or None
        """
        if not self.enabled:
            return None

        try:
            response = await self.client.get(f"/api/v1/cases/{case_id}")
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.warning(f"Case retrieval failed: {e}")
            return None

    async def update_case_feedback(
        self,
        case_id: str,
        feedback: Dict[str, Any]
    ) -> bool:
        """
        Update case with usage feedback

        Args:
            case_id: Case ID
            feedback: Feedback data (rating, usefulness, comments)

        Returns:
            True if updated successfully
        """
        if not self.enabled:
            return False

        try:
            response = await self.client.post(
                f"/api/v1/cases/{case_id}/feedback",
                json=feedback
            )
            response.raise_for_status()
            return True

        except httpx.HTTPError as e:
            logger.warning(f"Case feedback update failed: {e}")
            return False

    # ========================================================================
    # WORKFLOW PROCESS INTEGRATION
    # ========================================================================

    async def trigger_workflow(
        self,
        workflow_type: str,
        trigger_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Trigger a workflow process

        Can trigger workflows for:
        - Post-simulation review process
        - Approval workflows for community contribution
        - Incident response workflows from simulation findings

        Args:
            workflow_type: Type of workflow to trigger
            trigger_data: Workflow trigger data

        Returns:
            Workflow instance ID or None
        """
        if not self.enabled:
            return None

        try:
            response = await self.client.post(
                "/api/v1/workflows/trigger",
                json={
                    "workflow_type": workflow_type,
                    "trigger_data": trigger_data
                }
            )
            response.raise_for_status()
            result = response.json()

            workflow_id = result.get("workflow_id")
            logger.info(f"Workflow triggered: {workflow_id} (type: {workflow_type})")
            return workflow_id

        except httpx.HTTPError as e:
            logger.warning(f"Workflow trigger failed: {e}")
            return None

    # ========================================================================
    # HEALTH CHECK
    # ========================================================================

    async def health_check(self) -> Dict:
        """
        Check Workflow Intelligence health

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

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _extract_actions(self, results: SimulationResult) -> List[Dict]:
        """Extract actions taken during simulation"""
        actions = []

        for event in results.events:
            if hasattr(event, 'action_taken'):
                actions.append({
                    "timestamp": event.timestamp,
                    "action": event.action_taken,
                    "actor": event.actor if hasattr(event, 'actor') else "system",
                    "outcome": event.outcome if hasattr(event, 'outcome') else None
                })

        return actions

    def _calculate_variance(
        self,
        specification: TaskSpecification,
        results: SimulationResult
    ) -> Dict:
        """Calculate variance between expected and actual results"""
        variance = {
            "expected_vs_actual": {},
            "deviations": []
        }

        # Compare expected outcomes with actual
        if specification.expected_outcomes:
            for expected in specification.expected_outcomes:
                variance["expected_vs_actual"][expected] = {
                    "expected": expected,
                    "achieved": expected in results.lessons_learned  # Simplified
                }

        return variance

    def _extract_strengths(self, results: SimulationResult) -> List[str]:
        """Extract strengths from results"""
        strengths = []

        if results.overall_success_rate >= 0.8:
            strengths.append("High overall success rate")

        if results.kpis_achieved:
            strengths.append(f"Achieved {len(results.kpis_achieved)} KPIs")

        # Add more strength extraction logic

        return strengths

    def _extract_weaknesses(self, results: SimulationResult) -> List[str]:
        """Extract weaknesses from results"""
        weaknesses = []

        if results.overall_success_rate < 0.6:
            weaknesses.append("Low overall success rate")

        if results.improvement_areas:
            weaknesses.extend(results.improvement_areas)

        return weaknesses

    def _generate_next_steps(self, results: SimulationResult) -> List[str]:
        """Generate next steps from results"""
        next_steps = []

        if results.recommendations:
            next_steps.extend([f"Implement: {rec}" for rec in results.recommendations[:3]])

        if results.improvement_areas:
            next_steps.append(f"Focus on improving: {results.improvement_areas[0]}")

        return next_steps

    def _build_timeline(self, results: SimulationResult) -> List[Dict]:
        """Build timeline from simulation events"""
        timeline = []

        for event in results.events:
            timeline.append({
                "timestamp": event.timestamp if hasattr(event, 'timestamp') else None,
                "event": event.event_type if hasattr(event, 'event_type') else str(event),
                "description": event.description if hasattr(event, 'description') else None
            })

        return timeline

    def _generate_case_tags(
        self,
        specification: TaskSpecification,
        results: SimulationResult
    ) -> List[str]:
        """Generate tags for case"""
        tags = []

        # Add engine tag
        tags.append(f"engine_{results.engine_used}")

        # Add success level tag
        if results.overall_success_rate >= 0.8:
            tags.append("high_success")
        elif results.overall_success_rate >= 0.6:
            tags.append("moderate_success")
        else:
            tags.append("low_success")

        # Add complexity tag
        tags.append(f"complexity_{results.complexity_level}")

        return tags

    def _calculate_completeness(self, results: SimulationResult) -> float:
        """Calculate case completeness score"""
        completeness = 0.0
        total_checks = 6

        if results.lessons_learned:
            completeness += 1
        if results.recommendations:
            completeness += 1
        if results.metrics:
            completeness += 1
        if results.events:
            completeness += 1
        if results.participant_performance:
            completeness += 1
        if results.detailed_metrics:
            completeness += 1

        return completeness / total_checks
