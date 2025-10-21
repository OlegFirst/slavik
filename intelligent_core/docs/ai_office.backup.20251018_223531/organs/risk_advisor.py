"""
 Risk Advisor

Risk analysis and mitigation recommendations
"""

import sys
from pathlib import Path
from typing import Dict, Any
import httpx

sys.path.insert(0, str(Path(__file__).parent))
from base_organ import BaseAIOrgan


class RiskAdvisor(BaseAIOrgan):
    """
    Risk analysis organ

    Analyzes risks, vulnerabilities, and mitigation strategies
    """

    def __init__(self, llm_router=None):
        super().__init__(
            organ_name="Risk Advisor",
            emoji="",
            llm_router=llm_router
        )

    def _build_system_prompt(self) -> str:
        return """You are the Risk Advisor, a specialized AI for BCM risk analysis.

Your role:
- Identify and analyze business continuity risks
- Assess risk severity and likelihood
- Recommend risk mitigation strategies
- Prioritize risks based on impact
- Suggest risk monitoring approaches

You use quantitative methods when possible and provide actionable risk insights."""

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze risks

        Context keys:
        - twin_id: Digital Twin ID (optional - for dependency analysis)
        - organization_state: Current state
        - known_risks: List of known risks
        - scenario: Risk scenario to analyze (optional)
        """

        twin_id = context.get('twin_id')
        org_state = context.get('organization_state', {})
        known_risks = context.get('known_risks', [])
        scenario = context.get('scenario')

        # Get dependency graph if twin_id provided
        dependencies = []
        if twin_id:
            dependencies = await self._get_dependencies(twin_id)

        # Build analysis prompt
        user_prompt = f"""
Analyze BCM risks for this organization:

ORGANIZATION:
- Name: {org_state.get('name', 'Unknown')}
- Industry: {org_state.get('industry', 'Unknown')}
- Operational Status: {org_state.get('state', {}).get('operational_status', 'N/A')}

KNOWN RISKS:
{self._format_risks(known_risks)}

DEPENDENCIES:
{self._format_dependencies(dependencies)}

{f"SCENARIO TO ANALYZE: {scenario}" if scenario else ""}

Provide:
1. Top 5 critical risks (with severity: Critical/High/Medium/Low)
2. Risk interdependencies
3. Mitigation recommendations (prioritized)
4. Early warning indicators
"""

        # Query LLM
        response = await self._query_llm(
            system_prompt=self._build_system_prompt(),
            user_prompt=user_prompt,
            temperature=0.5  # Lower temperature for risk analysis
        )

        # Parse response
        risks, recommendations = self._parse_risk_response(response)

        return self.format_response(
            insights=risks,
            recommendations=recommendations,
            metadata={
                "analysis_type": "risk",
                "dependencies_analyzed": len(dependencies),
                "known_risks_count": len(known_risks)
            }
        )

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

    def _format_risks(self, risks: list) -> str:
        """Format known risks"""
        if not risks:
            return "No known risks provided - perform fresh analysis"

        return "\n".join([f"- {risk}" for risk in risks])

    def _format_dependencies(self, dependencies: list) -> str:
        """Format dependencies"""
        if not dependencies:
            return "No dependencies available"

        formatted = []
        for dep in dependencies[:10]:  # Limit to 10
            formatted.append(
                f"- {dep.get('from_entity_type')}:{dep.get('from_entity_id')} → "
                f"{dep.get('to_entity_type')}:{dep.get('to_entity_id')} "
                f"(strength: {dep.get('strength', 'N/A')})"
            )

        return "\n".join(formatted)

    def _parse_risk_response(self, response: str) -> tuple:
        """Parse LLM response into risks and recommendations"""
        lines = response.split('\n')

        risks = []
        recommendations = []

        current_section = None

        for line in lines:
            line = line.strip()

            if 'risk' in line.lower() and 'mitigation' not in line.lower():
                current_section = 'risks'
            elif 'mitigation' in line.lower() or 'recommendation' in line.lower():
                current_section = 'recommendations'

            if line and line[0] in ['-', '•', '1', '2', '3', '4', '5']:
                clean_line = line.lstrip('-•123456789. ').strip()
                if clean_line:
                    if current_section == 'risks':
                        risks.append(clean_line)
                    elif current_section == 'recommendations':
                        recommendations.append(clean_line)

        # Defaults
        if not risks:
            risks = ["Operational disruption risks", "Supply chain vulnerabilities", "IT system failures"]

        if not recommendations:
            recommendations = ["Implement risk monitoring", "Develop mitigation plans", "Regular risk assessments"]

        return risks, recommendations
