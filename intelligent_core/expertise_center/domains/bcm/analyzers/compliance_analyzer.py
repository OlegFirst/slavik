"""
️ Compliance Guardian

Standards compliance monitoring and gap analysis
"""

import sys
from pathlib import Path
from typing import Dict, Any
import httpx

sys.path.insert(0, str(Path(__file__).parent))
from base_organ import BaseAIOrgan
from expertise_center.monitoring.metrics import track_analyzer_call


class ComplianceGuardian(BaseAIOrgan):
    """
    Compliance monitoring organ

    Analyzes compliance with BCM standards (ISO 22301, NIST, etc.)
    """

    def __init__(self, llm_router=None):
        super().__init__(
            organ_name="Compliance Guardian",
            emoji="️",
            llm_router=llm_router
        )

    def _build_system_prompt(self) -> str:
        return """You are the Compliance Guardian, a BCM standards compliance AI specialist.

Your role:
- Assess compliance with BCM standards (ISO 22301, NIST CSF, ISO 27031, etc.)
- Identify compliance gaps and deficiencies
- Recommend remediation actions
- Track compliance status over time
- Map controls to multiple frameworks
- Provide audit-ready documentation guidance

You are thorough, precise, and cite specific standard clauses when applicable."""

    @track_analyzer_call(analyzer_name="compliance", domain="bcm")
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze compliance status

        Context keys:
        - twin_id: Digital Twin ID (for org context)
        - standards: List of standards to check (e.g., ['ISO_22301', 'NIST_CSF'])
        - current_controls: List of implemented controls
        - policies: List of current policies
        - audit_scope: Specific areas to audit (optional)
        - last_audit_date: When last audit was performed
        - known_gaps: Previously identified gaps
        """

        twin_id = context.get('twin_id')
        standards = context.get('standards', ['ISO_22301'])
        controls = context.get('current_controls', [])
        policies = context.get('policies', [])
        audit_scope = context.get('audit_scope')
        last_audit = context.get('last_audit_date')
        known_gaps = context.get('known_gaps', [])

        # Get Digital Twin state
        twin_state = {}
        if twin_id:
            twin_state = await self._get_twin_state(twin_id)

        # Get standard requirements from Domain Intelligence
        requirements = await self._get_standard_requirements(standards)

        # Build compliance analysis prompt
        user_prompt = f"""
Assess BCM compliance for this organization:

STANDARDS TO ASSESS:
{self._format_standards(standards)}

ORGANIZATION:
- Name: {twin_state.get('name', 'Unknown')}
- Industry: {twin_state.get('industry', 'Unknown')}
- Maturity Level: {twin_state.get('state', {}).get('bcm_maturity', 'Unknown')}

CURRENT CONTROLS:
{self._format_controls(controls)}

POLICIES:
{self._format_policies(policies)}

{f"AUDIT SCOPE: {audit_scope}" if audit_scope else "SCOPE: Full compliance assessment"}

{f"LAST AUDIT: {last_audit}" if last_audit else ""}

KNOWN GAPS:
{self._format_gaps(known_gaps)}

STANDARD REQUIREMENTS:
{self._format_requirements(requirements)}

Provide:
1. **Compliance Score** (% per standard, with justification)
2. **Critical Gaps** (top 5 gaps with standard clause references)
3. **Non-Compliance Risks** (what could go wrong)
4. **Remediation Roadmap** (prioritized actions with effort estimates)
5. **Quick Wins** (easy improvements for fast compliance boost)
6. **Audit Readiness** (assessment of current audit preparedness)

Be specific with standard clauses (e.g., "ISO 22301:2019 Clause 8.4.1").
"""

        # Query LLM with low temperature for compliance analysis
        response = await self._query_llm(
            system_prompt=self._build_system_prompt(),
            user_prompt=user_prompt,
            temperature=0.4  # Low temperature for precision
        )

        # Parse response
        insights, recommendations = self._parse_compliance_response(response)

        return self.format_response(
            insights=insights,
            recommendations=recommendations,
            metadata={
                "analysis_type": "compliance",
                "standards": standards,
                "controls_count": len(controls),
                "policies_count": len(policies),
                "known_gaps_count": len(known_gaps)
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

    async def _get_standard_requirements(self, standards: list) -> Dict[str, Any]:
        """Get standard requirements from Domain Intelligence"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8020/api/governance/domain/knowledge",
                    params={
                        "knowledge_type": "standard_requirements",
                        "standards": ",".join(standards)
                    }
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            self.logger.debug(f"Domain Intelligence not available: {e}")

        return {}

    def _format_standards(self, standards: list) -> str:
        """Format standards list"""
        if not standards:
            return "ISO 22301 (default)"

        return "\n".join([f"- {std}" for std in standards])

    def _format_controls(self, controls: list) -> str:
        """Format implemented controls"""
        if not controls:
            return "No controls documented"

        return "\n".join([f"- {control}" for control in controls[:20]])  # Top 20

    def _format_policies(self, policies: list) -> str:
        """Format policies"""
        if not policies:
            return "No policies documented"

        return "\n".join([f"- {policy}" for policy in policies])

    def _format_gaps(self, gaps: list) -> str:
        """Format known gaps"""
        if not gaps:
            return "No previously identified gaps"

        return "\n".join([f"- {gap}" for gap in gaps])

    def _format_requirements(self, requirements: Dict[str, Any]) -> str:
        """Format standard requirements"""
        if not requirements:
            return "Standard requirements not available - use general knowledge"

        return "Standard requirements available for analysis"

    def _parse_compliance_response(self, response: str) -> tuple:
        """Parse LLM response into insights and recommendations"""
        lines = response.split('\n')

        insights = []
        recommendations = []

        current_section = None

        for line in lines:
            line = line.strip()

            # Detect sections
            if any(keyword in line.lower() for keyword in ['score', 'gap', 'risk', 'non-compliance', 'readiness']):
                current_section = 'insights'
            elif any(keyword in line.lower() for keyword in ['remediation', 'recommendation', 'roadmap', 'quick win', 'action']):
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
            insights = [
                "Compliance assessment in progress",
                "Review required for gap identification",
                "Standard alignment to be verified"
            ]

        if not recommendations:
            recommendations = [
                "Document all implemented controls",
                "Map controls to standard requirements",
                "Schedule internal compliance audit",
                "Update BCM policy documentation"
            ]

        return insights, recommendations
