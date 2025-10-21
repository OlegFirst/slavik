"""
 Scenario Creator

AI-powered BCM scenario generation
"""

import sys
from pathlib import Path
from typing import Dict, Any
import httpx

sys.path.insert(0, str(Path(__file__).parent))
from base_organ import BaseAIOrgan
from expertise_center.monitoring.metrics import track_analyzer_call


class ScenarioCreator(BaseAIOrgan):
    """
    Scenario generation organ

    Creates realistic BCM exercise scenarios, disruption simulations
    """

    def __init__(self, llm_router=None):
        super().__init__(
            organ_name="Scenario Creator",
            emoji="",
            llm_router=llm_router
        )

    def _build_system_prompt(self) -> str:
        return """You are the Scenario Creator, an AI specialist in BCM scenario design.

Your role:
- Generate realistic BCM exercise scenarios
- Create disruption simulations tailored to specific industries
- Design scenario injects and timeline events
- Balance realism with learning objectives
- Adapt scenarios based on organization maturity
- Include multi-layered complexity and cascading events

You create scenarios that are challenging but achievable, with clear learning outcomes."""

    @track_analyzer_call(analyzer_name="scenario", domain="bcm")
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate BCM scenario

        Context keys:
        - twin_id: Digital Twin ID (for org-specific scenarios)
        - scenario_type: Type of scenario (exercise/simulation/tabletop)
        - threat_type: Primary threat (cyber/natural/supply_chain/etc)
        - complexity_level: Beginner/Intermediate/Advanced
        - learning_objectives: What participants should learn
        - duration_hours: Expected scenario duration
        - past_scenarios: Previously run scenarios (to avoid repetition)
        """

        twin_id = context.get('twin_id')
        scenario_type = context.get('scenario_type', 'exercise')
        threat_type = context.get('threat_type', 'multi-hazard')
        complexity = context.get('complexity_level', 'Intermediate')
        objectives = context.get('learning_objectives', [])
        duration = context.get('duration_hours', 4)
        past_scenarios = context.get('past_scenarios', [])

        # Get Digital Twin state
        twin_state = {}
        if twin_id:
            twin_state = await self._get_twin_state(twin_id)

        # Get industry-specific threat intelligence
        industry = twin_state.get('industry')
        threat_intel = await self._get_threat_intelligence(industry, threat_type) if industry else {}

        # Build scenario generation prompt
        user_prompt = f"""
Generate a BCM scenario with the following requirements:

SCENARIO TYPE: {scenario_type}
THREAT TYPE: {threat_type}
COMPLEXITY LEVEL: {complexity}
DURATION: {duration} hours

ORGANIZATION CONTEXT:
- Name: {twin_state.get('name', 'Generic organization')}
- Industry: {twin_state.get('industry', 'Generic')}
- Size: {twin_state.get('state', {}).get('employee_count', 'Unknown')} employees
- Critical Processes: {self._format_critical_processes(twin_state)}

LEARNING OBJECTIVES:
{self._format_objectives(objectives)}

PAST SCENARIOS (avoid repetition):
{self._format_past_scenarios(past_scenarios)}

THREAT INTELLIGENCE:
{self._format_threat_intel(threat_intel)}

Generate:
1. **Scenario Title** (compelling and descriptive)
2. **Initial Situation** (realistic starting conditions)
3. **Timeline** (key events over {duration} hours with timestamps)
4. **Injects** (5-7 scenario injects with timing and complexity escalation)
5. **Success Metrics** (what good response looks like)
6. **Debrief Questions** (5 key questions for post-exercise discussion)
7. **Variants** (2-3 ways to adjust difficulty on-the-fly)

Make it realistic, industry-specific, and aligned with learning objectives.
"""

        # Query LLM with moderate temperature for creativity
        response = await self._query_llm(
            system_prompt=self._build_system_prompt(),
            user_prompt=user_prompt,
            temperature=0.7  # Higher temperature for creative scenario generation
        )

        # Parse response
        insights, recommendations = self._parse_scenario_response(response)

        return self.format_response(
            insights=insights,
            recommendations=recommendations,
            metadata={
                "analysis_type": "scenario",
                "scenario_type": scenario_type,
                "threat_type": threat_type,
                "complexity": complexity,
                "duration_hours": duration,
                "industry": industry
            }
        )

    async def _get_twin_state(self, twin_id: int) -> Dict[str, Any]:
        """Get Digital Twin state"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8030/api/twin/organizations/{twin_id}"
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            self.logger.error(f"Error getting twin state: {e}")

        return {}

    async def _get_threat_intelligence(self, industry: str, threat_type: str) -> Dict[str, Any]:
        """Get threat intelligence from Domain Intelligence"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8020/api/governance/domain/knowledge",
                    params={
                        "industry": industry,
                        "knowledge_type": "threat_scenarios",
                        "threat_type": threat_type
                    }
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            self.logger.debug(f"Domain Intelligence not available: {e}")

        return {}

    def _format_critical_processes(self, twin_state: Dict[str, Any]) -> str:
        """Extract critical processes from twin state"""
        state = twin_state.get('state', {})
        processes = state.get('critical_processes', [])

        if not processes:
            return "Not specified"

        return ", ".join(processes[:5])  # Top 5

    def _format_objectives(self, objectives: list) -> str:
        """Format learning objectives"""
        if not objectives:
            return "General BCM competency improvement"

        return "\n".join([f"- {obj}" for obj in objectives])

    def _format_past_scenarios(self, past: list) -> str:
        """Format past scenarios"""
        if not past:
            return "No past scenarios recorded - fresh design"

        return "\n".join([f"- {scenario}" for scenario in past[:5]])  # Last 5

    def _format_threat_intel(self, intel: Dict[str, Any]) -> str:
        """Format threat intelligence"""
        if not intel:
            return "No threat intelligence available - use general knowledge"

        return "Industry-specific threat data available for scenario design"

    def _parse_scenario_response(self, response: str) -> tuple:
        """Parse LLM response into insights and recommendations"""
        lines = response.split('\n')

        insights = []
        recommendations = []

        current_section = None

        for line in lines:
            line = line.strip()

            # Detect sections
            if any(keyword in line.lower() for keyword in ['title', 'situation', 'timeline', 'inject', 'event']):
                current_section = 'insights'
            elif any(keyword in line.lower() for keyword in ['success', 'metric', 'debrief', 'question', 'variant', 'adjust']):
                current_section = 'recommendations'

            # Extract content
            if line and line[0] in ['-', '•', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*']:
                clean_line = line.lstrip('-•1234567890. *').strip()
                if clean_line:
                    if current_section == 'insights':
                        insights.append(clean_line)
                    elif current_section == 'recommendations':
                        recommendations.append(clean_line)

        # Defaults
        if not insights:
            insights = ["Scenario generation in progress", "Tailored to organization context"]

        if not recommendations:
            recommendations = [
                "Run scenario in controlled environment first",
                "Brief facilitators on injects before exercise",
                "Prepare observation checklist",
                "Schedule debrief within 24 hours"
            ]

        return insights, recommendations
