"""
 Impact Oracle

Predictive business impact analysis
"""

import sys
from pathlib import Path
from typing import Dict, Any
import httpx

sys.path.insert(0, str(Path(__file__).parent))
from base_organ import BaseAIOrgan
from expertise_center.monitoring.metrics import track_analyzer_call


class ImpactOracle(BaseAIOrgan):
    """
    Predictive BIA organ

    Forecasts business impacts, RTO/RPO recommendations
    """

    def __init__(self, llm_router=None):
        super().__init__(
            organ_name="Impact Oracle",
            emoji="",
            llm_router=llm_router
        )

    def _build_system_prompt(self) -> str:
        return """You are the Impact Oracle, a predictive BIA specialist AI.

Your role:
- Predict business impact of disruptions
- Recommend appropriate RTO/RPO targets
- Assess financial and operational impacts
- Identify critical processes
- Forecast cascading effects

You provide data-driven impact predictions with quantitative estimates when possible."""

    @track_analyzer_call(analyzer_name="impact", domain="bcm")
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze business impact

        Context keys:
        - twin_id: Digital Twin ID (for state + dependencies)
        - disruption_scenario: What's being disrupted
        - process_data: Process information (optional)
        - industry_benchmarks: Industry data (optional from Domain Intelligence)
        """

        twin_id = context.get('twin_id')
        scenario = context.get('disruption_scenario', 'Unknown disruption')
        process_data = context.get('process_data', {})

        # Get Digital Twin state
        twin_state = {}
        if twin_id:
            twin_state = await self._get_twin_state(twin_id)

        # Get industry benchmarks if available
        industry = twin_state.get('industry')
        benchmarks = await self._get_industry_benchmarks(industry) if industry else {}

        # Build analysis prompt
        user_prompt = f"""
Predict the business impact for this disruption scenario:

SCENARIO: {scenario}

ORGANIZATION:
- Industry: {twin_state.get('industry', 'Unknown')}
- Current Status: {twin_state.get('state', {}).get('operational_status', 'N/A')}

PROCESS DATA:
{self._format_process_data(process_data)}

INDUSTRY BENCHMARKS:
{self._format_benchmarks(benchmarks)}

Provide:
1. Predicted financial impact (min/max range)
2. Operational impact assessment
3. Recommended RTO (hours)
4. Recommended RPO (hours)
5. Cascading effects to watch for
6. Impact severity: Critical/High/Medium/Low
"""

        # Query LLM
        response = await self._query_llm(
            system_prompt=self._build_system_prompt(),
            user_prompt=user_prompt,
            temperature=0.4  # Low temperature for predictions
        )

        # Parse response
        impacts, recommendations = self._parse_impact_response(response)

        return self.format_response(
            insights=impacts,
            recommendations=recommendations,
            metadata={
                "analysis_type": "impact",
                "scenario": scenario,
                "industry": industry,
                "has_benchmarks": bool(benchmarks)
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

    async def _get_industry_benchmarks(self, industry: str) -> Dict[str, Any]:
        """Get industry benchmarks from Domain Intelligence"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8020/api/governance/domain/knowledge?industry={industry}&knowledge_type=typical_rto"
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            self.logger.debug(f"Domain Intelligence not available: {e}")

        return {}

    def _format_process_data(self, process_data: Dict[str, Any]) -> str:
        """Format process data"""
        if not process_data:
            return "No process data provided"

        return f"""
- Process Name: {process_data.get('name', 'Unknown')}
- Criticality: {process_data.get('criticality', 'Unknown')}
- Current RTO: {process_data.get('rto_hours', 'Not set')} hours
- Current RPO: {process_data.get('rpo_hours', 'Not set')} hours
"""

    def _format_benchmarks(self, benchmarks: Dict[str, Any]) -> str:
        """Format industry benchmarks"""
        if not benchmarks:
            return "No industry benchmarks available"

        # Simple formatting - in production would be more detailed
        return "Industry benchmark data available for analysis"

    def _parse_impact_response(self, response: str) -> tuple:
        """Parse LLM response into impacts and recommendations"""
        lines = response.split('\n')

        impacts = []
        recommendations = []

        current_section = None

        for line in lines:
            line = line.strip()

            if 'impact' in line.lower() or 'rto' in line.lower() or 'rpo' in line.lower():
                current_section = 'impacts'
            elif 'recommendation' in line.lower() or 'cascading' in line.lower():
                current_section = 'recommendations'

            if line and line[0] in ['-', '•', '1', '2', '3', '4', '5']:
                clean_line = line.lstrip('-•123456789. ').strip()
                if clean_line:
                    if current_section == 'impacts':
                        impacts.append(clean_line)
                    elif current_section == 'recommendations':
                        recommendations.append(clean_line)

        # Defaults
        if not impacts:
            impacts = ["Operational impact requires assessment", "Financial impact to be quantified"]

        if not recommendations:
            recommendations = ["Establish RTO/RPO targets", "Monitor cascading effects", "Implement early warning systems"]

        return impacts, recommendations
