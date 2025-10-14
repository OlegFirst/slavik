"""
Digital Twin - Advanced AI Scenario Generator
AI-powered scenario generation with learning capabilities

Integrated from simulation/exercise_simulators - provides intelligent
scenario generation with historical context and continuous learning.
"""

import httpx
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
import os

logger = logging.getLogger(__name__)


class ScenarioParameters(BaseModel):
    """Parameters for AI scenario generation"""
    category: str = Field(..., description="Scenario category (cyber, pandemic, natural_disaster, etc.)")
    complexity: int = Field(3, ge=1, le=5, description="Complexity level 1-5")
    duration_hours: int = Field(4, ge=1, le=168, description="Exercise duration in hours")
    participants: int = Field(10, ge=1, description="Number of participants")
    affected_systems: List[str] = Field(default_factory=list, description="Systems affected by scenario")
    custom_objectives: List[str] = Field(default_factory=list, description="Custom exercise objectives")
    organization_context: Optional[Dict[str, Any]] = None  # Industry, size, etc.


class GeneratedScenario(BaseModel):
    """AI-generated BCM scenario"""
    title: str
    description: str
    category: str
    scenario_type: str  # tabletop, functional, full_scale, simulation
    timeline: List[Dict[str, Any]]
    injects: List[Dict[str, Any]]
    success_metrics: List[str]
    ai_metadata: Dict[str, Any] = Field(default_factory=dict)


class AdvancedScenarioGenerator:
    """
    Advanced AI-powered scenario generator with learning capabilities

    Features:
    - Historical context integration from past exercises
    - Sophisticated prompt engineering for BCM scenarios
    - Learning loop - improves from exercise outcomes
    - Multi-LLM support (local Gemma, OpenAI, etc.)
    - Fallback mechanisms for robustness
    """

    def __init__(
        self,
        ai_orchestrator_url: Optional[str] = None,
        model_runner_url: Optional[str] = None
    ):
        """
        Initialize Advanced AI Scenario Generator

        Args:
            ai_orchestrator_url: URL for AI orchestrator service (provides context)
            model_runner_url: URL for LLM model runner (Gemma, etc.)
        """
        self.ai_orchestrator_url = ai_orchestrator_url or os.getenv(
            "AI_ORCHESTRATOR_URL", "http://ai-orchestrator:8000"
        )
        self.model_runner_url = model_runner_url or os.getenv(
            "MODEL_RUNNER_URL", "http://model-runner:8088"
        )
        self.scenario_history: List[Dict] = []
        self.client_timeout = 60.0

        logger.info(f"Advanced AI Scenario Generator initialized")
        logger.info(f"AI Orchestrator: {self.ai_orchestrator_url}")
        logger.info(f"Model Runner: {self.model_runner_url}")

    async def generate_scenario(
        self,
        params: ScenarioParameters
    ) -> GeneratedScenario:
        """
        Generate AI-powered BCM exercise scenario

        Process:
        1. Get historical context from AI orchestrator
        2. Build sophisticated prompt with context
        3. Query LLM for scenario generation
        4. Parse and structure response
        5. Return complete scenario

        Args:
            params: Scenario generation parameters

        Returns:
            Generated scenario with timeline, injects, metrics

        Example:
            params = ScenarioParameters(
                category="cyber_attack",
                complexity=4,
                duration_hours=6,
                participants=15,
                affected_systems=["email", "crm", "database"],
                custom_objectives=["Test incident response", "Evaluate communication"]
            )
            scenario = await generator.generate_scenario(params)
        """
        logger.info(f"Generating AI scenario: {params.category} (complexity {params.complexity})")

        # Step 1: Get historical context and insights
        ai_context = await self._get_ai_context(params)

        # Step 2: Build sophisticated prompt
        scenario_prompt = self._build_scenario_prompt(params, ai_context)

        # Step 3: Query LLM
        generated_content = await self._query_llm(scenario_prompt)

        # Step 4: Parse response
        scenario = self._parse_scenario_response(generated_content, params, ai_context)

        logger.info(f"AI scenario generated: {scenario.title}")

        return scenario

    async def _get_ai_context(self, params: ScenarioParameters) -> Dict[str, Any]:
        """
        Get AI context from orchestrator service

        Retrieves:
        - Historical insights from past exercises
        - Similar real-world incidents
        - Industry-specific patterns
        - Best practices and lessons learned
        """
        try:
            async with httpx.AsyncClient(timeout=self.client_timeout) as client:
                response = await client.post(
                    f"{self.ai_orchestrator_url}/analyze/scenario-context",
                    json={
                        "category": params.category,
                        "complexity": params.complexity,
                        "historical_data": True,
                        "organization_context": params.organization_context
                    }
                )

                if response.status_code == 200:
                    context = response.json()
                    logger.info(f"AI context retrieved: {len(context.get('insights', []))} insights")
                    return context
                else:
                    logger.warning(f"AI context request failed: {response.status_code}")
                    return {}

        except Exception as e:
            logger.warning(f"Could not get AI context: {e}")
            return {}

    def _build_scenario_prompt(
        self,
        params: ScenarioParameters,
        ai_context: Dict
    ) -> str:
        """
        Build comprehensive prompt for LLM scenario generation

        Includes:
        - Scenario requirements (category, complexity, duration)
        - Historical context and insights
        - Similar real incidents
        - Custom objectives
        - Industry/organizational context
        - Detailed structure requirements
        """
        historical_insights = ai_context.get('insights', [])
        similar_incidents = ai_context.get('similar_incidents', [])
        org_context = params.organization_context or {}

        # Build industry context
        industry_context = ""
        if org_context.get('industry'):
            industry_context = f"\nIndustry: {org_context['industry']}"
        if org_context.get('size'):
            industry_context += f"\nOrganization Size: {org_context['size']}"

        prompt = f"""Generate a realistic BCM exercise scenario with the following specifications:

SCENARIO REQUIREMENTS:
- Category: {params.category}
- Complexity Level: {params.complexity}/5
- Duration: {params.duration_hours} hours
- Participants: {params.participants} people
- Affected Systems: {', '.join(params.affected_systems) if params.affected_systems else 'TBD'}
{industry_context}

HISTORICAL CONTEXT:
{json.dumps(historical_insights, indent=2) if historical_insights else 'No historical data available'}

SIMILAR REAL INCIDENTS:
{json.dumps(similar_incidents, indent=2) if similar_incidents else 'None identified'}

CUSTOM OBJECTIVES:
{', '.join(params.custom_objectives) if params.custom_objectives else 'Standard BCM objectives'}

Please generate a comprehensive scenario that includes:

1. SCENARIO OVERVIEW:
   - Compelling, realistic title
   - Detailed background story
   - Clear initial situation
   - Realistic triggers and catalysts

2. TIMELINE (Hour by Hour):
   - Progressive escalation
   - Key decision points
   - Realistic time constraints
   - Recovery milestones

3. EXERCISE INJECTS:
   - Phone calls and voicemails
   - Emails and text messages
   - News reports and social media
   - System alerts and notifications
   - Stakeholder communications
   - Regulatory inquiries
   - External pressures (media, customers, etc.)

4. SUCCESS METRICS:
   - Measurable objectives
   - Time-based milestones
   - Communication effectiveness metrics
   - Decision quality indicators
   - Recovery time targets

5. REALISM FACTORS:
   - Based on actual incident patterns
   - Industry-specific considerations
   - Regional/local context
   - Regulatory requirements
   - Cascading effects
   - Human factors and stress

Format the response as structured JSON with the following structure:
{{
    "title": "Scenario Title",
    "description": "Detailed description",
    "timeline": [
        {{"time": "HH:MM", "event": "Event description", "type": "inject|decision|action"}}
    ],
    "injects": [
        {{"type": "type", "content": "inject content", "timing": "HH:MM", "source": "source"}}
    ],
    "success_metrics": ["metric1", "metric2", ...]
}}
"""

        return prompt

    async def _query_llm(self, prompt: str) -> str:
        """
        Query LLM for scenario generation

        Supports:
        - Local Gemma via model runner
        - OpenAI API (fallback)
        - Other LLM providers
        """
        try:
            async with httpx.AsyncClient(timeout=self.client_timeout) as client:
                response = await client.post(
                    f"{self.model_runner_url}/v1/chat/completions",
                    json={
                        "model": "gemma3:latest",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert BCM consultant specializing in realistic exercise scenario creation. "
                                          "You have extensive experience with ISO 22301, incident response, and crisis management."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": 2000,
                        "temperature": 0.8  # Creative but controlled
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    logger.info("LLM query successful")
                    return content
                else:
                    logger.error(f"LLM query failed: {response.status_code}")
                    return self._get_fallback_scenario()

        except Exception as e:
            logger.error(f"LLM connection error: {e}")
            return self._get_fallback_scenario()

    def _parse_scenario_response(
        self,
        llm_response: str,
        params: ScenarioParameters,
        ai_context: Dict
    ) -> GeneratedScenario:
        """
        Parse LLM response into structured scenario

        Handles:
        - JSON extraction from markdown code blocks
        - Unstructured text parsing
        - Validation and error recovery
        """
        try:
            # Try to extract JSON from response
            if "```json" in llm_response:
                json_start = llm_response.find("```json") + 7
                json_end = llm_response.find("```", json_start)
                json_content = llm_response[json_start:json_end]
                parsed = json.loads(json_content)
            elif "```" in llm_response:
                # Try generic code block
                json_start = llm_response.find("```") + 3
                json_end = llm_response.find("```", json_start)
                json_content = llm_response[json_start:json_end]
                parsed = json.loads(json_content)
            else:
                # Try parsing entire response
                parsed = json.loads(llm_response)

        except Exception as e:
            logger.warning(f"Failed to parse LLM JSON response: {e}")
            # Fallback to text extraction
            parsed = self._extract_scenario_parts(llm_response)

        # Determine scenario type based on complexity
        scenario_type = self._determine_scenario_type(params.complexity)

        # Build AI metadata
        ai_metadata = {
            'ai_generated': True,
            'model': 'gemma3:latest',
            'complexity': params.complexity,
            'has_historical_context': bool(ai_context.get('insights')),
            'generation_timestamp': datetime.now().isoformat()
        }

        return GeneratedScenario(
            title=parsed.get('title', f'{params.category.title()} Exercise Scenario'),
            description=parsed.get('description', 'AI-generated BCM exercise scenario'),
            category=params.category,
            scenario_type=scenario_type,
            timeline=parsed.get('timeline', []),
            injects=parsed.get('injects', []),
            success_metrics=parsed.get('success_metrics', []),
            ai_metadata=ai_metadata
        )

    def _determine_scenario_type(self, complexity: int) -> str:
        """Determine scenario type based on complexity"""
        if complexity >= 5:
            return "full_scale"
        elif complexity >= 4:
            return "simulation"
        elif complexity >= 3:
            return "functional"
        else:
            return "tabletop"

    def _extract_scenario_parts(self, text: str) -> Dict:
        """Extract scenario components from unstructured text (fallback)"""
        logger.warning("Using fallback text extraction")

        return {
            "title": "AI-Generated BCM Scenario",
            "description": text[:300] + "..." if len(text) > 300 else text,
            "timeline": [
                {"time": "09:00", "event": "Scenario begins", "type": "start"},
                {"time": "10:00", "event": "Initial assessment", "type": "decision"},
                {"time": "12:00", "event": "Response activation", "type": "action"}
            ],
            "injects": [
                {"type": "notification", "content": "Initial incident alert", "timing": "09:00"}
            ],
            "success_metrics": [
                "Timely incident detection",
                "Effective communication",
                "Successful recovery"
            ]
        }

    def _get_fallback_scenario(self) -> str:
        """Fallback scenario template if AI generation fails"""
        return """
{
    "title": "Standard BCM Exercise Scenario",
    "description": "A comprehensive business continuity exercise designed to test organizational readiness and response capabilities.",
    "timeline": [
        {"time": "09:00", "event": "Initial incident notification received", "type": "inject"},
        {"time": "09:15", "event": "Incident assessment and escalation", "type": "decision"},
        {"time": "09:30", "event": "BCM team activation", "type": "action"},
        {"time": "10:00", "event": "Stakeholder notifications", "type": "action"},
        {"time": "10:30", "event": "Alternative process activation", "type": "action"},
        {"time": "12:00", "event": "Status update and re-assessment", "type": "decision"}
    ],
    "injects": [
        {"type": "phone_call", "content": "Emergency notification from facility management - critical infrastructure offline", "timing": "09:00", "source": "Facility Manager"},
        {"type": "email", "content": "System alert: Primary systems unavailable, estimated recovery time unknown", "timing": "09:15", "source": "IT Operations"},
        {"type": "sms", "content": "Customer complaints increasing, social media activity rising", "timing": "09:45", "source": "Customer Service"},
        {"type": "news_alert", "content": "Local news reporting service disruptions", "timing": "10:15", "source": "Media"}
    ],
    "success_metrics": [
        "Incident detected and escalated within 15 minutes",
        "BCM team activated within 30 minutes",
        "All key stakeholders notified within 1 hour",
        "Alternative processes activated within 2 hours",
        "Regular status updates provided every 30 minutes"
    ]
}
        """

    async def learn_from_exercise(
        self,
        scenario_id: str,
        outcomes: Dict[str, Any]
    ) -> bool:
        """
        Learn from exercise outcomes to improve future scenarios

        Sends feedback to AI orchestrator for:
        - Scenario effectiveness analysis
        - Pattern recognition
        - Future scenario improvement

        Args:
            scenario_id: ID of completed scenario
            outcomes: Exercise outcomes with lessons learned, feedback, scores

        Returns:
            True if learning data sent successfully
        """
        learning_data = {
            "scenario_id": scenario_id,
            "outcomes": outcomes,
            "timestamp": datetime.now().isoformat(),
            "lessons_learned": outcomes.get('lessons_learned', []),
            "effectiveness_score": outcomes.get('effectiveness_score', 0),
            "participant_feedback": outcomes.get('feedback', []),
            "improvements_needed": outcomes.get('improvements', [])
        }

        # Store locally for backup
        self.scenario_history.append(learning_data)

        # Send to AI orchestrator for learning
        try:
            async with httpx.AsyncClient(timeout=self.client_timeout) as client:
                response = await client.post(
                    f"{self.ai_orchestrator_url}/learn/exercise-outcome",
                    json=learning_data
                )

                if response.status_code == 200:
                    logger.info(f"Exercise learning data sent successfully for scenario {scenario_id}")
                    return True
                else:
                    logger.warning(f"Learning data submission failed: {response.status_code}")
                    return False

        except Exception as e:
            logger.error(f"Failed to send learning data: {e}")
            return False

    def get_scenario_history(self) -> List[Dict]:
        """Get local scenario history (for backup/analysis)"""
        return self.scenario_history
