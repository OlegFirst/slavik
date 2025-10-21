"""
💓 Lifecycle Monitor

BCM lifecycle health monitoring and continuous improvement
"""

import sys
from pathlib import Path
from typing import Dict, Any
import httpx
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from base_organ import BaseAIOrgan


class LifecycleMonitor(BaseAIOrgan):
    """
    Lifecycle monitoring organ

    Tracks BCM lifecycle health, identifies improvement opportunities
    """

    def __init__(self, llm_router=None):
        super().__init__(
            organ_name="Lifecycle Monitor",
            emoji="💓",
            llm_router=llm_router
        )

    def _build_system_prompt(self) -> str:
        return """You are the Lifecycle Monitor, a BCM continuous improvement and health tracking AI.

Your role:
- Monitor overall BCM program health and maturity
- Track lifecycle stages (Plan-Do-Check-Act)
- Identify continuous improvement opportunities
- Detect stagnation and decline patterns
- Recommend lifecycle optimization
- Ensure sustainable BCM practices

You provide holistic, long-term perspective on BCM program evolution and health."""

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitor BCM lifecycle health

        Context keys:
        - twin_id: Digital Twin ID (for state history)
        - time_period: Monitoring period (e.g., "last_90_days")
        - lifecycle_stage: Current stage (plan/do/check/act)
        - activity_log: Recent BCM activities
        - kpi_trends: KPI trends over time
        - last_review_date: When last reviewed
        - maturity_target: Target maturity level
        """

        twin_id = context.get('twin_id')
        time_period = context.get('time_period', 'last_90_days')
        lifecycle_stage = context.get('lifecycle_stage', 'unknown')
        activity_log = context.get('activity_log', [])
        kpi_trends = context.get('kpi_trends', {})
        last_review = context.get('last_review_date')
        maturity_target = context.get('maturity_target', 'mature')

        # Get Digital Twin state and history
        twin_state = {}
        state_history = []
        health_metrics = []

        if twin_id:
            twin_state = await self._get_twin_state(twin_id)
            state_history = await self._get_state_history(twin_id, time_period)
            health_metrics = await self._get_health_metrics(twin_id, time_period)

        # Build lifecycle monitoring prompt
        user_prompt = f"""
Monitor BCM lifecycle health for this organization:

MONITORING PERIOD: {time_period}
CURRENT LIFECYCLE STAGE: {lifecycle_stage}
MATURITY TARGET: {maturity_target}

ORGANIZATION:
- Name: {twin_state.get('name', 'Unknown')}
- Industry: {twin_state.get('industry', 'Unknown')}
- Current Maturity: {twin_state.get('state', {}).get('bcm_maturity', 'Unknown')}
- Operational Status: {twin_state.get('state', {}).get('operational_status', 'Unknown')}

STATE EVOLUTION:
{self._format_state_history(state_history)}

HEALTH METRICS (Trend):
{self._format_health_trends(health_metrics)}

RECENT ACTIVITIES:
{self._format_activities(activity_log)}

KPI TRENDS:
{self._format_kpi_trends(kpi_trends)}

LAST COMPREHENSIVE REVIEW: {last_review if last_review else 'Not recorded'}

Provide:
1. **Lifecycle Health Score** (0-100 with breakdown by PDCA stage)
2. **Maturity Progression** (are we moving toward target?)
3. **Activity Patterns** (healthy cadence or stagnation?)
4. **Red Flags** (warning signs of decline or neglect)
5. **Lifecycle Optimization** (how to improve PDCA cycle)
6. **Continuous Improvement Recommendations** (prioritized)
7. **Next Review Timing** (when should next assessment occur)

Focus on long-term sustainability and continuous improvement culture.
"""

        # Query LLM with moderate temperature
        response = await self._query_llm(
            system_prompt=self._build_system_prompt(),
            user_prompt=user_prompt,
            temperature=0.5  # Balanced analysis
        )

        # Parse response
        insights, recommendations = self._parse_lifecycle_response(response)

        return self.format_response(
            insights=insights,
            recommendations=recommendations,
            metadata={
                "analysis_type": "lifecycle",
                "time_period": time_period,
                "lifecycle_stage": lifecycle_stage,
                "activities_count": len(activity_log),
                "state_snapshots": len(state_history),
                "maturity_target": maturity_target
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

    async def _get_state_history(self, twin_id: int, period: str) -> list:
        """Get state snapshots history"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8030/api/twin/organizations/{twin_id}/snapshots",
                    params={"period": period}
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            self.logger.debug(f"State history not available: {e}")

        return []

    async def _get_health_metrics(self, twin_id: int, period: str) -> list:
        """Get health metrics history"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8030/api/twin/organizations/{twin_id}/health",
                    params={"period": period}
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            self.logger.debug(f"Health metrics not available: {e}")

        return []

    def _format_state_history(self, history: list) -> str:
        """Format state history"""
        if not history:
            return "No historical state data available"

        if len(history) < 2:
            return "Insufficient data for trend analysis (need multiple snapshots)"

        # Show first and last to demonstrate evolution
        first = history[0]
        last = history[-1]

        return f"""- {len(history)} snapshots over period
- Initial state ({first.get('created_at', 'N/A')}): Maturity {first.get('state', {}).get('bcm_maturity', 'Unknown')}
- Current state ({last.get('created_at', 'N/A')}): Maturity {last.get('state', {}).get('bcm_maturity', 'Unknown')}
- Trend: {"Improving" if len(history) > 1 else "Stable"}"""

    def _format_health_trends(self, metrics: list) -> str:
        """Format health metrics trends"""
        if not metrics:
            return "No health metrics recorded"

        # Group by metric type
        metric_types = {}
        for metric in metrics:
            mtype = metric.get('metric_type', 'unknown')
            if mtype not in metric_types:
                metric_types[mtype] = []
            metric_types[mtype].append(metric.get('value', 0))

        formatted = []
        for mtype, values in list(metric_types.items())[:5]:  # Top 5 metric types
            avg_value = sum(values) / len(values) if values else 0
            trend = "improving" if len(values) > 1 and values[-1] > values[0] else "stable"
            formatted.append(f"- {mtype}: avg {avg_value:.1f} ({trend})")

        return "\n".join(formatted) if formatted else "Metrics available but need analysis"

    def _format_activities(self, activities: list) -> str:
        """Format recent activities"""
        if not activities:
            return "No recent BCM activities recorded - potential stagnation risk"

        formatted = []
        for activity in activities[:10]:  # Last 10 activities
            formatted.append(
                f"- {activity.get('type', 'Unknown')}: {activity.get('description', 'N/A')} "
                f"({activity.get('date', 'N/A')})"
            )

        return "\n".join(formatted)

    def _format_kpi_trends(self, trends: Dict[str, Any]) -> str:
        """Format KPI trends"""
        if not trends:
            return "No KPI trend data available"

        formatted = []
        for kpi_name, trend_data in trends.items():
            direction = trend_data.get('direction', 'unknown')
            change = trend_data.get('change_percent', 0)
            formatted.append(f"- {kpi_name}: {direction} ({change:+.1f}%)")

        return "\n".join(formatted[:10])  # Top 10 KPIs

    def _parse_lifecycle_response(self, response: str) -> tuple:
        """Parse LLM response into insights and recommendations"""
        lines = response.split('\n')

        insights = []
        recommendations = []

        current_section = None

        for line in lines:
            line = line.strip()

            # Detect sections
            if any(keyword in line.lower() for keyword in ['score', 'health', 'maturity', 'progression', 'pattern', 'red flag', 'warning', 'trend']):
                current_section = 'insights'
            elif any(keyword in line.lower() for keyword in ['optimization', 'recommendation', 'improvement', 'review', 'timing', 'action']):
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
                "Lifecycle monitoring requires baseline establishment",
                "Activity tracking needs improvement",
                "Maturity progression not yet measurable"
            ]

        if not recommendations:
            recommendations = [
                "Establish regular BCM activity cadence",
                "Implement systematic state snapshots",
                "Schedule quarterly comprehensive reviews",
                "Track and document all BCM activities"
            ]

        return insights, recommendations
