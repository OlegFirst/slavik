"""
Scenario Orchestrator - BCM scenario generation and management

From /services/scenario_orchestrator/main.py
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import httpx

from core import BaseOrchestrator
from models import ScenarioGenerationRequest, Scenario
from .learning_engine import LearningEngine

logger = logging.getLogger(__name__)


class ScenarioOrchestrator(BaseOrchestrator):
    """
    Scenario generation and learning orchestrator

    Responsibilities:
    - Generate AI-powered BCM scenarios
    - Create JaamSim simulation configs
    - Collect exercise results
    - Learn from exercise feedback
    - Recommend scenario improvements
    """

    def __init__(self):
        super().__init__()

        self.learning = LearningEngine()
        self.scenario_storage = {}  # In-memory for now
        self.ai_orchestrator_url = "http://ai_orchestrator:8000"  # TODO: from config
        self.odoo_url = "http://odoo:8069"

        logger.info("ScenarioOrchestrator initialized")

    async def start(self) -> None:
        """Start scenario orchestrator"""
        if self.running:
            logger.warning("Scenario Orchestrator already running")
            return

        logger.info("Starting Scenario Orchestrator...")

        self.running = True
        logger.info("Scenario Orchestrator started")

        await self.publish_event(
            event_type='scenario.orchestrator.ready',
            data={}
        )

    async def stop(self) -> None:
        """Stop scenario orchestrator"""
        self.running = False
        logger.info("Scenario Orchestrator stopped")

    async def get_status(self) -> Dict[str, Any]:
        """Get scenario orchestrator status"""
        return {
            'running': self.running,
            'scenarios_generated': len(self.scenario_storage),
            'learning_data': await self.learning.get_stats(),
            'timestamp': datetime.utcnow().isoformat()
        }

    async def generate_scenario(self, request: ScenarioGenerationRequest) -> Scenario:
        """
        Generate AI-powered BCM scenario

        Args:
            request: Scenario generation parameters

        Returns:
            Generated scenario
        """
        logger.info(f"Generating scenario: {request.category}, complexity {request.complexity}")

        # Build AI prompt
        ai_prompt = self._build_generation_prompt(request)

        # Query AI Orchestrator for generation
        ai_response = await self._query_ai_orchestrator(ai_prompt, request)

        # Format response
        scenario = Scenario(
            id=f"scenario_{uuid.uuid4().hex[:12]}",
            title=f"{request.category.title()} BCM Exercise Scenario",
            category=request.category,
            level="full" if request.complexity >= 4 else "tabletop",
            meta_duration=request.duration_hours,
            meta_participants=request.participants,
            content_md=self._format_to_markdown(ai_response, request),
            is_ai_generated=True,
            ai_generation_params={
                'complexity': request.complexity,
                'ai_model': 'ai_orchestrator',
                'generated_at': datetime.utcnow().isoformat()
            },
            jaamsim_config=self._generate_jaamsim_config(request) if request.complexity >= 4 else None,
            created_at=datetime.utcnow()
        )

        # Store scenario
        self.scenario_storage[scenario.id] = scenario

        # Save to Odoo (async)
        await self._save_to_odoo(scenario)

        logger.info(f"Scenario generated: {scenario.id}")

        return scenario

    def _build_generation_prompt(self, request: ScenarioGenerationRequest) -> str:
        """Build AI prompt for scenario generation"""
        return f"""
Generate a comprehensive BCM exercise scenario with the following parameters:

SCENARIO REQUIREMENTS:
- Category: {request.category}
- Complexity: {request.complexity}/5
- Duration: {request.duration_hours} hours
- Participants: {request.participants}
- Affected Systems: {', '.join(request.affected_systems) if request.affected_systems else 'TBD'}
- Organization Context: {request.organization_context or 'Generic organization'}

DELIVERABLES:
1. Scenario title and background story
2. Hour-by-hour timeline with escalation points
3. Exercise injects (emails, calls, alerts)
4. Success metrics and evaluation criteria
5. JaamSim simulation parameters (if complexity >= 4)

Format as structured response for BCM Scenario Hub.
"""

    async def _query_ai_orchestrator(self, prompt: str, request: ScenarioGenerationRequest) -> str:
        """Query AI Orchestrator for scenario generation"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.ai_orchestrator_url}/nlp/query",
                    json={
                        "query": prompt,
                        "context": {
                            "scenario_type": "bcm_exercise",
                            "complexity": request.complexity,
                            "category": request.category
                        },
                        "user_role": "scenario_generator"
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "")
                else:
                    logger.error(f"AI Orchestrator error: {response.status_code}")
                    return "Generated scenario placeholder"

        except Exception as e:
            logger.error(f"Error querying AI Orchestrator: {e}")
            return "Generated scenario placeholder"

    def _format_to_markdown(self, ai_response: str, request: ScenarioGenerationRequest) -> str:
        """Format AI response to markdown"""
        return f"""# {request.category.title()} BCM Exercise Scenario

## Scenario Overview
{ai_response[:500] if ai_response else 'AI-generated scenario content'}

## Exercise Parameters
- **Complexity Level**: {request.complexity}/5
- **Duration**: {request.duration_hours} hours
- **Participants**: {request.participants}
- **Category**: {request.category}

## Affected Systems
{', '.join(request.affected_systems) if request.affected_systems else 'To be determined'}

## AI Generation Details
- **Generated by**: BCM Scenario Orchestrator
- **Generated on**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

---
*This scenario was automatically generated using AI and should be reviewed before execution.*
"""

    def _generate_jaamsim_config(self, request: ScenarioGenerationRequest) -> Optional[str]:
        """Generate JaamSim configuration for complex scenarios"""
        if request.complexity < 4:
            return None

        return f"""# AI-Generated JaamSim Configuration
# Scenario: {request.category.title()} Exercise
# Complexity: {request.complexity}/5

RecordEdits

Define DiscreteDistribution {{ ImpactDistribution }}
Define ExponentialDistribution {{ RecoveryDistribution }}

ImpactDistribution ValueList {{ 1 2 3 4 5 }}
ImpactDistribution ProbabilityList {{ 0.1 0.2 0.4 0.2 0.1 }}

RecoveryDistribution Mean {{ {request.duration_hours} h }}

Define EntityGenerator {{ IncidentSource }}
Define Queue {{ ResponseQueue }}
Define Server {{ ResponseTeam }}
Define EntitySink {{ ResolvedIncidents }}

ResponseTeam Capacity {{ {min(request.participants, 10)} }}

Define SimulationRun {{ {request.category.title()}Exercise }}
{request.category.title()}Exercise RunDuration {{ {request.duration_hours} h }}
"""

    async def _save_to_odoo(self, scenario: Scenario) -> None:
        """Save scenario to Odoo BCM Scenario Hub"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.odoo_url}/api/v1/bcm_scenario",
                    json=scenario.dict(),
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code in [200, 201]:
                    logger.info(f"Scenario {scenario.id} saved to Odoo")
                else:
                    logger.warning(f"Failed to save to Odoo: {response.status_code}")

        except Exception as e:
            logger.error(f"Error saving to Odoo: {e}")