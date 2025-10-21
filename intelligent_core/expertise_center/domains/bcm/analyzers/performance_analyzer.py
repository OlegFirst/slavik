"""
 Performance Analyst

BCM KPI intelligence and metrics analysis
"""

import sys
from pathlib import Path
from typing import Dict, Any
import httpx

sys.path.insert(0, str(Path(__file__).parent))
from base_organ import BaseAIOrgan
from expertise_center.monitoring.metrics import track_analyzer_call


class PerformanceAnalyst(BaseAIOrgan):
    """
    Performance analysis organ

    Analyzes BCM KPIs, metrics, trends, and performance optimization
    """

    def __init__(self, llm_router=None):
        super().__init__(
            organ_name="Performance Analyst",
            emoji="",
            llm_router=llm_router
        )

    def _build_system_prompt(self) -> str:
        return """You are the Performance Analyst, a BCM metrics and KPI intelligence AI.

Your role:
- Analyze BCM performance metrics and KPIs
- Identify trends and patterns in BCM data
- Benchmark performance against industry standards
- Recommend KPI improvements and new metrics
- Detect anomalies and performance degradation
- Provide data-driven optimization insights

You use quantitative analysis and provide actionable, metrics-driven recommendations."""

    @track_analyzer_call(analyzer_name="performance", domain="bcm")
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze BCM performance metrics

        Context keys:
        - twin_id: Digital Twin ID (for health metrics)
        - kpi_data: Current KPI values
        - historical_data: Time-series KPI data
        - time_period: Analysis period (e.g., "last_30_days")
        - focus_areas: Specific areas to analyze (optional)
        - benchmarks: Industry benchmarks (optional)
        """

        twin_id = context.get('twin_id')
        kpi_data = context.get('kpi_data', {})
        historical = context.get('historical_data', [])
        time_period = context.get('time_period', 'last_30_days')
        focus_areas = context.get('focus_areas', [])
        benchmarks = context.get('benchmarks', {})

        # Get Digital Twin health metrics
        health_metrics = []
        twin_state = {}
        if twin_id:
            twin_state = await self._get_twin_state(twin_id)
            health_metrics = await self._get_health_metrics(twin_id, time_period)

        # Get industry benchmarks if not provided
        if not benchmarks and twin_state.get('industry'):
            benchmarks = await self._get_industry_benchmarks(twin_state.get('industry'))

        # Build performance analysis prompt
        user_prompt = f"""
Analyze BCM performance metrics for this organization:

TIME PERIOD: {time_period}

ORGANIZATION:
- Name: {twin_state.get('name', 'Unknown')}
- Industry: {twin_state.get('industry', 'Unknown')}
- BCM Maturity: {twin_state.get('state', {}).get('bcm_maturity', 'Unknown')}

CURRENT KPIs:
{self._format_kpis(kpi_data)}

HISTORICAL TRENDS:
{self._format_historical(historical)}

HEALTH METRICS (Digital Twin):
{self._format_health_metrics(health_metrics)}

{f"FOCUS AREAS: {', '.join(focus_areas)}" if focus_areas else ""}

INDUSTRY BENCHMARKS:
{self._format_benchmarks(benchmarks)}

Provide:
1. **Performance Summary** (overall BCM health score 0-100 with justification)
2. **Key Findings** (top 5 insights from metrics analysis)
3. **Trend Analysis** (improving/declining/stable trends)
4. **Anomalies Detected** (any unusual patterns or red flags)
5. **Benchmark Comparison** (how we compare to industry standards)
6. **Optimization Recommendations** (prioritized improvements)
7. **New KPI Suggestions** (metrics we should start tracking)

Use data-driven language and include specific numbers when available.
"""

        # Query LLM with moderate temperature
        response = await self._query_llm(
            system_prompt=self._build_system_prompt(),
            user_prompt=user_prompt,
            temperature=0.5  # Moderate temperature for analytical work
        )

        # Parse response
        insights, recommendations = self._parse_performance_response(response)

        return self.format_response(
            insights=insights,
            recommendations=recommendations,
            metadata={
                "analysis_type": "performance",
                "time_period": time_period,
                "kpi_count": len(kpi_data),
                "historical_points": len(historical),
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

    async def _get_health_metrics(self, twin_id: int, time_period: str) -> list:
        """Get health metrics from Digital Twin"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8030/api/twin/organizations/{twin_id}/health",
                    params={"period": time_period}
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            self.logger.debug(f"Health metrics not available: {e}")

        return []

    async def _get_industry_benchmarks(self, industry: str) -> Dict[str, Any]:
        """Get industry benchmarks from Domain Intelligence"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8020/api/governance/domain/knowledge",
                    params={
                        "industry": industry,
                        "knowledge_type": "kpi_benchmarks"
                    }
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            self.logger.debug(f"Domain Intelligence not available: {e}")

        return {}

    def _format_kpis(self, kpi_data: Dict[str, Any]) -> str:
        """Format current KPI data"""
        if not kpi_data:
            return "No KPI data provided"

        formatted = []
        for kpi_name, value in kpi_data.items():
            formatted.append(f"- {kpi_name}: {value}")

        return "\n".join(formatted)

    def _format_historical(self, historical: list) -> str:
        """Format historical data"""
        if not historical:
            return "No historical data available"

        if len(historical) < 3:
            return "Limited historical data - trends may not be reliable"

        return f"{len(historical)} data points available for trend analysis"

    def _format_health_metrics(self, metrics: list) -> str:
        """Format health metrics"""
        if not metrics:
            return "No health metrics available"

        # Show last 5 metrics
        formatted = []
        for metric in metrics[:5]:
            formatted.append(
                f"- {metric.get('metric_type')}: {metric.get('value')} "
                f"(recorded: {metric.get('recorded_at')})"
            )

        return "\n".join(formatted)

    def _format_benchmarks(self, benchmarks: Dict[str, Any]) -> str:
        """Format industry benchmarks"""
        if not benchmarks:
            return "No industry benchmarks available"

        return "Industry benchmark data available for comparison"

    def _parse_performance_response(self, response: str) -> tuple:
        """Parse LLM response into insights and recommendations"""
        lines = response.split('\n')

        insights = []
        recommendations = []

        current_section = None

        for line in lines:
            line = line.strip()

            # Detect sections
            if any(keyword in line.lower() for keyword in ['summary', 'finding', 'trend', 'anomaly', 'benchmark', 'comparison', 'score']):
                current_section = 'insights'
            elif any(keyword in line.lower() for keyword in ['optimization', 'recommendation', 'improvement', 'suggest', 'kpi']):
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
                "Performance metrics require baseline establishment",
                "KPI tracking needs improvement",
                "Trend analysis pending sufficient data"
            ]

        if not recommendations:
            recommendations = [
                "Establish consistent KPI measurement cadence",
                "Implement automated metric collection",
                "Set realistic performance targets",
                "Regular performance review meetings"
            ]

        return insights, recommendations
