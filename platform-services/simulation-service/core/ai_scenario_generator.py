"""
AI Scenario Generator
=====================

AI-powered scenario generation using LLM models for BCM exercises.

Adapted from: /simulation/exercise_simulators/ai_scenario_generator.py
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ScenarioType(str, Enum):
    """Exercise scenario types"""
    TABLETOP = "tabletop"
    FUNCTIONAL = "functional"
    FULL_SCALE = "full_scale"
    SIMULATION = "simulation"


class ScenarioParameters(BaseModel):
    """Parameters for AI scenario generation"""
    category: str = Field(..., description="Scenario category (cyber, pandemic, blackout, etc.)")
    complexity: int = Field(3, ge=1, le=5, description="Complexity level 1-5")
    duration_hours: int = Field(4, description="Exercise duration in hours")
    participants: int = Field(10, description="Number of participants")
    affected_systems: List[str] = Field(default_factory=list, description="Affected systems")
    custom_objectives: List[str] = Field(default_factory=list, description="Custom objectives")


class GeneratedScenario(BaseModel):
    """AI-generated scenario"""
    title: str
    description: str
    category: str
    scenario_type: ScenarioType
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    injects: List[Dict[str, Any]] = Field(default_factory=list)
    success_metrics: List[str] = Field(default_factory=list)
    jaamsim_config: Optional[str] = None
    nics_setup: Optional[Dict[str, Any]] = None


class AIScenarioGenerator:
    """
    AI-powered scenario generator that learns from exercise outcomes

    Uses LLM models to generate realistic BCM exercise scenarios
    with historical context and learning capabilities.
    """

    def __init__(
        self,
        ai_orchestrator_url: str = None,
        model_runner_url: str = None
    ):
        self.ai_orchestrator_url = ai_orchestrator_url or os.getenv(
            "AI_ORCHESTRATOR_URL",
            "http://localhost:8000"
        )
        self.model_runner_url = model_runner_url or os.getenv(
            "MODEL_RUNNER_URL",
            "http://localhost:8088"
        )
        self.scenario_history = []

    async def generate_scenario(self, params: ScenarioParameters) -> GeneratedScenario:
        """
        Generate AI-powered BCM exercise scenario

        Args:
            params: Scenario generation parameters

        Returns:
            Complete generated scenario with timeline, injects, and metrics
        """
        logger.info(f"Generating AI scenario: {params.category} (complexity {params.complexity})")

        # Get AI context from orchestrator
        ai_context = await self._get_ai_context(params)

        # Generate scenario using LLM
        scenario_prompt = self._build_scenario_prompt(params, ai_context)
        generated_content = await self._query_llm(scenario_prompt)

        # Parse and structure the scenario
        scenario = self._parse_scenario_response(generated_content, params)

        # Generate JaamSim configuration if simulation type
        if params.category in ['cyber', 'blackout', 'supply'] and params.complexity >= 4:
            scenario.jaamsim_config = await self._generate_jaamsim_config(scenario)

        # Generate NICS setup for complex scenarios
        if params.complexity >= 4:
            scenario.nics_setup = await self._generate_nics_setup(scenario)

        logger.info(f"Generated scenario: {scenario.title}")
        return scenario

    async def _get_ai_context(self, params: ScenarioParameters) -> Dict[str, Any]:
        """Get AI context from orchestrator"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.ai_orchestrator_url}/analyze/scenario-context",
                    json={
                        "category": params.category,
                        "complexity": params.complexity,
                        "historical_data": True
                    }
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"AI context fetch failed: {response.status_code}")
                    return {}

        except Exception as e:
            logger.warning(f"Could not get AI context: {e}")
            return {}

    def _build_scenario_prompt(self, params: ScenarioParameters, ai_context: Dict) -> str:
        """Build comprehensive prompt for LLM scenario generation"""

        historical_insights = ai_context.get('insights', [])
        similar_incidents = ai_context.get('similar_incidents', [])

        prompt = f"""
Generate a realistic BCM exercise scenario with the following specifications:

SCENARIO REQUIREMENTS:
- Category: {params.category}
- Complexity Level: {params.complexity}/5
- Duration: {params.duration_hours} hours
- Participants: {params.participants} people
- Affected Systems: {', '.join(params.affected_systems) if params.affected_systems else 'TBD'}

HISTORICAL CONTEXT:
{json.dumps(historical_insights, indent=2) if historical_insights else 'No historical data available'}

SIMILAR REAL INCIDENTS:
{json.dumps(similar_incidents, indent=2) if similar_incidents else 'None identified'}

CUSTOM OBJECTIVES:
{', '.join(params.custom_objectives) if params.custom_objectives else 'Standard BCM objectives'}

Please generate a comprehensive scenario that includes:

1. SCENARIO OVERVIEW:
   - Compelling title
   - Realistic background story
   - Clear initial situation

2. TIMELINE (Hour by Hour):
   - Progressive escalation
   - Key decision points
   - Realistic time constraints

3. EXERCISE INJECTS:
   - Phone calls, emails, news reports
   - System alerts and notifications
   - Stakeholder communications
   - External pressures

4. SUCCESS METRICS:
   - Measurable objectives
   - Time-based milestones
   - Communication effectiveness
   - Decision quality indicators

5. REALISM FACTORS:
   - Based on actual incident patterns
   - Industry-specific considerations
   - Regional/local context
   - Regulatory requirements

Format the response as structured JSON with clear sections.
"""

        return prompt

    async def _query_llm(self, prompt: str) -> str:
        """Query local LLM for scenario generation"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.model_runner_url}/v1/chat/completions",
                    json={
                        "model": "gemma3:latest",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert BCM consultant specializing in realistic exercise scenario creation."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": 2000,
                        "temperature": 0.8
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"LLM query failed: {response.status_code}")
                    return self._get_fallback_scenario()

        except Exception as e:
            logger.error(f"LLM connection error: {e}")
            return self._get_fallback_scenario()

    def _parse_scenario_response(self, llm_response: str, params: ScenarioParameters) -> GeneratedScenario:
        """Parse LLM response into structured scenario"""

        try:
            # Try to extract JSON from response
            if "```json" in llm_response:
                json_start = llm_response.find("```json") + 7
                json_end = llm_response.find("```", json_start)
                json_content = llm_response[json_start:json_end]
                parsed = json.loads(json_content)
            else:
                # Try direct JSON parse
                parsed = json.loads(llm_response)

        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            parsed = self._get_fallback_scenario_data(params)

        return GeneratedScenario(
            title=parsed.get('title', f'{params.category.title()} Exercise Scenario'),
            description=parsed.get('description', 'AI-generated BCM exercise scenario'),
            category=params.category,
            scenario_type=ScenarioType.SIMULATION if params.complexity >= 4 else ScenarioType.TABLETOP,
            timeline=parsed.get('timeline', []),
            injects=parsed.get('injects', []),
            success_metrics=parsed.get('success_metrics', [])
        )

    async def _generate_jaamsim_config(self, scenario: GeneratedScenario) -> str:
        """Generate JaamSim configuration for simulation scenarios"""

        config_template = f"""
# JaamSim Configuration: {scenario.title}
# Generated automatically for BCM exercise simulation

RecordEdits

# Scenario-specific parameters
Define DiscreteDistribution {{ ImpactDistribution }}
Define ExponentialDistribution {{ RecoveryDistribution }}
Define UniformDistribution {{ ResponseDistribution }}

# Configure based on scenario category
ImpactDistribution ValueList {{ 1 2 3 4 5 }}
ImpactDistribution ProbabilityList {{ 0.1 0.2 0.4 0.2 0.1 }}

RecoveryDistribution Mean {{ 2 h }}
ResponseDistribution MinValue {{ 5 min }}
ResponseDistribution MaxValue {{ 30 min }}

# Entities and processes
Define EntityGenerator {{ IncidentSource }}
Define Queue {{ ResponseQueue }}
Define Server {{ EmergencyTeam BackupSystems }}
Define Branch {{ DecisionPoint }}
Define EntitySink {{ ResolvedIncidents }}

# Scenario timeline integration
"""

        return config_template

    async def _generate_nics_setup(self, scenario: GeneratedScenario) -> Dict[str, Any]:
        """Generate NICS setup for complex scenarios"""

        return {
            "incident_type": scenario.category,
            "command_structure": {
                "incident_commander": "IC",
                "operations_chief": "OPS",
                "planning_chief": "PLAN",
                "logistics_chief": "LOG",
                "finance_admin_chief": "FIN"
            },
            "required_forms": ["ICS-201", "ICS-202", "ICS-203"],
            "communication_channels": [
                {"name": "Command", "frequency": "155.100"},
                {"name": "Tactical", "frequency": "155.200"},
                {"name": "Support", "frequency": "155.300"}
            ],
            "gis_layers": ["critical_infrastructure", "evacuation_routes", "resources"]
        }

    def _get_fallback_scenario(self) -> str:
        """Fallback scenario if AI generation fails"""
        return """
{
    "title": "Standard BCM Exercise Scenario",
    "description": "A comprehensive business continuity exercise designed to test organizational readiness.",
    "timeline": [
        {"time": "09:00", "event": "Initial incident notification", "type": "inject"},
        {"time": "09:30", "event": "Impact assessment required", "type": "decision"},
        {"time": "10:00", "event": "Activation of continuity plans", "type": "action"}
    ],
    "injects": [
        {"type": "phone_call", "content": "Emergency notification from facility management", "timing": "09:00"},
        {"type": "email", "content": "System alert: Critical infrastructure offline", "timing": "09:15"}
    ],
    "success_metrics": [
        "Response time under 30 minutes",
        "All key personnel contacted within 1 hour",
        "Alternative processes activated within 2 hours"
    ]
}
        """

    def _get_fallback_scenario_data(self, params: ScenarioParameters) -> Dict:
        """Get basic scenario data as fallback"""
        return {
            "title": f"{params.category.title()} Response Exercise",
            "description": f"BCM exercise focusing on {params.category} incident response",
            "timeline": [
                {"time": "09:00", "event": "Scenario begins", "type": "start"}
            ],
            "injects": [],
            "success_metrics": ["Successful completion of exercise objectives"]
        }

    async def learn_from_exercise(self, scenario_id: str, outcomes: Dict[str, Any]):
        """
        Learn from exercise outcomes to improve future scenarios

        Args:
            scenario_id: ID of completed scenario
            outcomes: Exercise outcomes and feedback
        """

        learning_data = {
            "scenario_id": scenario_id,
            "outcomes": outcomes,
            "timestamp": datetime.now().isoformat(),
            "lessons_learned": outcomes.get('lessons_learned', []),
            "effectiveness_score": outcomes.get('effectiveness_score', 0),
            "participant_feedback": outcomes.get('feedback', [])
        }

        # Send to AI orchestrator for learning
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    f"{self.ai_orchestrator_url}/learn/exercise-outcome",
                    json=learning_data
                )
                logger.info(f"Exercise learning data sent for scenario {scenario_id}")

        except Exception as e:
            logger.error(f"Failed to send learning data: {e}")

        # Store locally for backup
        self.scenario_history.append(learning_data)
        logger.info(f"Scenario learning recorded: {scenario_id}")
