"""
Risk Analyzer
Fast LLM risk analysis
"""
from typing import Dict, Any
from .base_analyzer import BaseAnalyzer


class RiskAnalyzer(BaseAnalyzer):
    """
    Risk Analysis Analyzer

    Performs fast LLM-based risk analysis using FAIR methodology
    """

    def _build_system_prompt(self) -> str:
        """Build system prompt for risk analysis"""
        return """You are the Risk Analyzer, a specialized AI for BCM risk analysis.

Your role:
- Identify and analyze business continuity risks
- Assess risk severity and likelihood using FAIR methodology
- Recommend risk mitigation strategies (reduce, accept, transfer, avoid)
- Prioritize risks based on impact and RTO/RPO
- Suggest risk monitoring approaches

FAIR Framework:
- TEF (Threat Event Frequency) - how often threat occurs
- LM (Loss Magnitude) - $ impact per event
- ALE (Annual Loss Expectancy) = TEF × LM

Risk Severity Levels:
- 5 (Critical): RTO < 4h, SPOF present, financial impact > $1M
- 4 (High): RTO < 24h, multiple dependencies, impact $100K-$1M
- 3 (Medium): RTO < 72h, some dependencies, impact $10K-$100K
- 2 (Low): RTO < 1 week, minimal dependencies, impact < $10K
- 1 (Minimal): RTO > 1 week, no critical dependencies

Provide actionable, quantitative risk insights in JSON format:
{
  "insights": [
    "Critical risk: [description with severity level]",
    "Vulnerability: [specific weakness identified]"
  ],
  "recommendations": [
    "Mitigation: [specific action with priority]",
    "Monitoring: [early warning indicator]"
  ]
}
"""

    def _build_user_prompt(self, context: Dict[str, Any]) -> str:
        """Build user prompt from context"""
        process = context.get('process', {})
        dependencies = context.get('dependencies', [])
        existing_risks = context.get('existing_risks', [])
        industry = context.get('industry', 'Unknown')

        # Count SPOFs
        spof_count = sum(1 for d in dependencies if d.get('single_point_of_failure'))

        # Format dependencies
        dep_list = []
        for dep in dependencies[:10]:  # Top 10
            spof_marker = "⚠️ SPOF" if dep.get('single_point_of_failure') else ""
            dep_list.append(
                f"  • {dep.get('type', 'N/A')}: {dep.get('name', 'Unknown')} "
                f"(criticality: {dep.get('criticality', 'N/A')}) {spof_marker}"
            )

        dependencies_text = "\n".join(dep_list) if dep_list else "  No dependencies"

        # Format existing risks
        risks_text = "\n".join([
            f"  • {risk.get('description', 'N/A')} (severity: {risk.get('severity', 'N/A')})"
            for risk in existing_risks[:5]
        ]) if existing_risks else "  No existing risks recorded"

        return f"""
Analyze BCM risks for this process:

PROCESS:
- Name: {process.get('name', 'Unknown')}
- Tier: {process.get('tier', 'N/A')}
- RTO: {process.get('rto_hours', 'N/A')} hours
- RPO: {process.get('rpo_hours', 'N/A')} hours
- Industry: {industry}

DEPENDENCIES ({len(dependencies)} total, {spof_count} SPOFs):
{dependencies_text}

EXISTING RISKS ({len(existing_risks)} total):
{risks_text}

Provide:
1. Top 3-5 critical risks (with severity 1-5)
2. Key vulnerabilities (especially SPOFs)
3. Prioritized mitigation recommendations
4. Early warning indicators for monitoring

Return as JSON with "insights" and "recommendations" arrays.
"""

    def _calculate_confidence(
        self,
        parsed: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for risk analysis"""
        score = 0.5  # baseline

        # Has insights
        if parsed.get('insights') and len(parsed['insights']) >= 3:
            score += 0.2

        # Has recommendations
        if parsed.get('recommendations') and len(parsed['recommendations']) >= 3:
            score += 0.2

        # Has process data
        process = context.get('process', {})
        if process.get('rto_hours') is not None:
            score += 0.1

        # Has dependencies
        if context.get('dependencies'):
            score += 0.1

        return min(score, 1.0)
