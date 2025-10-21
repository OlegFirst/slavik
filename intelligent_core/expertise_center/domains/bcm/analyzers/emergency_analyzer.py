"""
 Emergency Response

Crisis management and incident response intelligence
"""

import sys
from pathlib import Path
from typing import Dict, Any
import httpx

sys.path.insert(0, str(Path(__file__).parent))
from base_organ import BaseAIOrgan
from expertise_center.monitoring.metrics import track_analyzer_call


class EmergencyResponse(BaseAIOrgan):
    """
    Emergency response organ

    Crisis management, incident response, real-time decision support
    """

    def __init__(self, llm_router=None):
        super().__init__(
            organ_name="Emergency Response",
            emoji="",
            llm_router=llm_router
        )

    def _build_system_prompt(self) -> str:
        return """You are the Emergency Response organ, a crisis management AI specialist.

Your role:
- Provide real-time incident response guidance
- Assess crisis severity and urgency
- Recommend immediate actions and priorities
- Coordinate emergency procedures
- Generate crisis communication drafts
- Monitor escalation criteria

You operate in high-pressure scenarios with focus on speed, clarity, and actionable guidance."""

    @track_analyzer_call(analyzer_name="emergency", domain="bcm")
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze emergency situation and provide response guidance

        Context keys:
        - twin_id: Digital Twin ID (for current state)
        - incident_type: Type of incident
        - incident_description: Detailed description
        - severity: Initial severity assessment (optional)
        - affected_systems: List of affected systems/processes
        - current_actions: Actions already taken
        """

        twin_id = context.get('twin_id')
        incident_type = context.get('incident_type', 'Unknown incident')
        description = context.get('incident_description', '')
        severity = context.get('severity', 'Unknown')
        affected_systems = context.get('affected_systems', [])
        current_actions = context.get('current_actions', [])

        # Get Digital Twin state
        twin_state = {}
        if twin_id:
            twin_state = await self._get_twin_state(twin_id)

        # Get active dependencies
        dependencies = []
        if twin_id:
            dependencies = await self._get_dependencies(twin_id)

        # Build emergency analysis prompt
        user_prompt = f"""
EMERGENCY SITUATION ANALYSIS:

INCIDENT TYPE: {incident_type}
SEVERITY: {severity}

DESCRIPTION:
{description}

ORGANIZATION STATE:
- Name: {twin_state.get('name', 'Unknown')}
- Industry: {twin_state.get('industry', 'Unknown')}
- Current Status: {twin_state.get('state', {}).get('operational_status', 'N/A')}

AFFECTED SYSTEMS:
{self._format_affected_systems(affected_systems)}

CURRENT ACTIONS TAKEN:
{self._format_current_actions(current_actions)}

DEPENDENCIES AT RISK:
{self._format_dependencies(dependencies)}

Provide IMMEDIATE response guidance:
1. Severity reassessment (Critical/High/Medium/Low) with justification
2. Top 5 immediate actions (prioritized, time-sensitive)
3. Stakeholders to notify (prioritized)
4. Communication template (brief internal alert)
5. Escalation criteria (when to escalate further)
6. Risks of cascading failures
7. Estimated time to stabilization

CRITICAL: Keep responses concise and actionable for crisis conditions.
"""

        # Query LLM with low temperature for crisis response
        response = await self._query_llm(
            system_prompt=self._build_system_prompt(),
            user_prompt=user_prompt,
            temperature=0.3  # Very low temperature for crisis scenarios
        )

        # Parse response
        insights, recommendations = self._parse_emergency_response(response)

        return self.format_response(
            insights=insights,
            recommendations=recommendations,
            metadata={
                "analysis_type": "emergency",
                "incident_type": incident_type,
                "initial_severity": severity,
                "affected_systems_count": len(affected_systems),
                "actions_taken": len(current_actions)
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

    async def _get_dependencies(self, twin_id: int) -> list:
        """Get dependencies from Digital Twin"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8030/api/twin/organizations/{twin_id}/dependencies"
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            self.logger.error(f"Error getting dependencies: {e}")

        return []

    def _format_affected_systems(self, systems: list) -> str:
        """Format affected systems"""
        if not systems:
            return "No specific systems identified"

        return "\n".join([f"- {system}" for system in systems])

    def _format_current_actions(self, actions: list) -> str:
        """Format current actions"""
        if not actions:
            return "No actions taken yet"

        return "\n".join([f"- {action}" for action in actions])

    def _format_dependencies(self, dependencies: list) -> str:
        """Format dependencies at risk"""
        if not dependencies:
            return "No dependency data available"

        formatted = []
        for dep in dependencies[:5]:  # Show top 5 critical dependencies
            formatted.append(
                f"- {dep.get('from_entity_type')}:{dep.get('from_entity_id')} → "
                f"{dep.get('to_entity_type')}:{dep.get('to_entity_id')}"
            )

        return "\n".join(formatted)

    def _parse_emergency_response(self, response: str) -> tuple:
        """Parse LLM response into insights and recommendations"""
        lines = response.split('\n')

        insights = []
        recommendations = []

        current_section = None

        for line in lines:
            line = line.strip()

            # Detect sections
            if 'severity' in line.lower() or 'assessment' in line.lower() or 'risk' in line.lower():
                current_section = 'insights'
            elif 'action' in line.lower() or 'notify' in line.lower() or 'communication' in line.lower() or 'escalation' in line.lower():
                current_section = 'recommendations'

            # Extract bullet points
            if line and line[0] in ['-', '•', '1', '2', '3', '4', '5', '6', '7']:
                clean_line = line.lstrip('-•1234567890. ').strip()
                if clean_line:
                    if current_section == 'insights':
                        insights.append(clean_line)
                    elif current_section == 'recommendations':
                        recommendations.append(clean_line)

        # Defaults
        if not insights:
            insights = ["Emergency situation requires immediate assessment", "Monitor for cascading failures"]

        if not recommendations:
            recommendations = [
                "Activate incident response team",
                "Notify key stakeholders",
                "Document all actions taken",
                "Prepare status updates"
            ]

        return insights, recommendations
