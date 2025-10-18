"""
🧠 Governance Brain

Strategic intelligence and policy guidance
"""

import sys
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent))
from base_organ import BaseAIOrgan


class GovernanceBrain(BaseAIOrgan):
    """
    Strategic intelligence organ

    Analyzes governance, policies, strategic alignment
    """

    def __init__(self, llm_router=None):
        super().__init__(
            organ_name="Governance Brain",
            emoji="🧠",
            llm_router=llm_router
        )

    def _build_system_prompt(self) -> str:
        return """You are the Governance Brain, a strategic intelligence AI for BCM.

Your role:
- Analyze organizational governance structures
- Evaluate policy effectiveness
- Assess strategic alignment with BCM objectives
- Identify governance gaps and risks
- Recommend governance improvements

You provide high-level strategic insights, not operational details."""

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze governance and strategic alignment

        Context keys:
        - organization_state: Current org state from Digital Twin
        - policies: List of current policies
        - strategic_objectives: Strategic goals
        - compliance_requirements: Regulatory requirements
        """

        org_state = context.get('organization_state', {})
        policies = context.get('policies', [])
        objectives = context.get('strategic_objectives', [])
        compliance = context.get('compliance_requirements', [])

        # Build analysis prompt
        user_prompt = f"""
Analyze the BCM governance for this organization:

ORGANIZATION STATE:
{self._format_org_state(org_state)}

CURRENT POLICIES:
{self._format_policies(policies)}

STRATEGIC OBJECTIVES:
{self._format_objectives(objectives)}

COMPLIANCE REQUIREMENTS:
{self._format_compliance(compliance)}

Provide:
1. Governance strengths
2. Governance gaps
3. Strategic alignment assessment
4. Top 3 governance recommendations
"""

        # Query LLM
        response = await self._query_llm(
            system_prompt=self._build_system_prompt(),
            user_prompt=user_prompt,
            temperature=0.6  # Lower temperature for strategic analysis
        )

        # Parse response into structured format
        insights, recommendations = self._parse_response(response)

        return self.format_response(
            insights=insights,
            recommendations=recommendations,
            metadata={
                "analysis_type": "governance",
                "organization_id": org_state.get('id'),
                "policies_analyzed": len(policies)
            }
        )

    def _format_org_state(self, org_state: Dict[str, Any]) -> str:
        """Format organization state for prompt"""
        if not org_state:
            return "No organization state provided"

        return f"""
- Organization: {org_state.get('name', 'Unknown')}
- Domain: {org_state.get('domain', 'Unknown')}
- Industry: {org_state.get('industry', 'Unknown')}
- Operational Status: {org_state.get('state', {}).get('operational_status', 'Unknown')}
"""

    def _format_policies(self, policies: list) -> str:
        """Format policies for prompt"""
        if not policies:
            return "No policies provided"

        return "\n".join([f"- {p}" for p in policies])

    def _format_objectives(self, objectives: list) -> str:
        """Format objectives for prompt"""
        if not objectives:
            return "No strategic objectives provided"

        return "\n".join([f"- {obj}" for obj in objectives])

    def _format_compliance(self, compliance: list) -> str:
        """Format compliance requirements for prompt"""
        if not compliance:
            return "No compliance requirements specified"

        return "\n".join([f"- {req}" for req in compliance])

    def _parse_response(self, response: str) -> tuple:
        """Parse LLM response into insights and recommendations"""
        # Simple parsing - in production would be more sophisticated
        lines = response.split('\n')

        insights = []
        recommendations = []

        current_section = None

        for line in lines:
            line = line.strip()

            if 'strength' in line.lower() or 'gap' in line.lower() or 'assessment' in line.lower():
                current_section = 'insights'
            elif 'recommendation' in line.lower():
                current_section = 'recommendations'

            if line and line[0] in ['-', '•', '1', '2', '3', '4', '5']:
                clean_line = line.lstrip('-•123456789. ').strip()
                if clean_line:
                    if current_section == 'insights':
                        insights.append(clean_line)
                    elif current_section == 'recommendations':
                        recommendations.append(clean_line)

        # Ensure we have at least some output
        if not insights:
            insights = ["Governance analysis completed - see full response for details"]

        if not recommendations:
            recommendations = ["Review governance framework", "Update BCM policies", "Enhance strategic alignment"]

        return insights, recommendations
