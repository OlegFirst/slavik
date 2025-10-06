"""
Risk Organ - LLM Analysis Component

Migrated from: /ai-orchestration/muscles/ai_organs/risk_advisor.py

Provides:
- Risk identification analysis
- Likelihood assessment
- Impact calculation
- FAIR methodology expertise
- Treatment recommendations
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "ai-orchestration/muscles/ai_organs"))

from base_organ import BaseAIOrgan


class RiskOrgan(BaseAIOrgan):
    """
    Risk Organ - specialized LLM for risk analysis

    Extends BaseAIOrgan with risk-specific prompts and analysis methods
    """

    def __init__(self, llm_router=None):
        super().__init__(
            organ_name="Risk Organ",
            emoji="⚡",
            llm_router=llm_router
        )

    def _build_system_prompt(self) -> str:
        return """You are the Risk Organ, a specialized AI for BCM risk analysis using FAIR methodology.

Your role:
- Identify business continuity risks systematically
- Assess risk severity and likelihood with quantitative methods
- Calculate impact across 4 dimensions: financial, operational, reputational, regulatory
- Apply FAIR methodology: TEF (Threat Event Frequency) × LM (Loss Magnitude) = ALE (Annual Loss Expectancy)
- Recommend risk treatments: reduce, accept, transfer, avoid
- Prioritize risks based on ALE and organizational risk appetite

Standards compliance:
- ISO 22301 (Business Continuity Management)
- ISO 31000 (Risk Management)
- FAIR (Factor Analysis of Information Risk)

Output format:
- Be quantitative when possible (use numbers, percentages, dollar amounts)
- Cite industry benchmarks when available
- Provide reasoning for all assessments
- Structure responses as JSON-compatible dicts with 'insights' and 'recommendations'
"""

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze risks based on action type

        Context keys:
        - action: identify_risks | analyze_likelihood | calculate_impact | fair_analysis | plan_treatments
        - process: Process data (for identify_risks)
        - risks: Risks data (for other actions)
        - workflow_context: Full AI context from AIContextBuilder
        - org_size, org_revenue, risk_appetite, budget (optional org params)

        Returns:
            {
                'insights': {...},  # Main analysis results
                'recommendations': [...],  # Action recommendations
                'metadata': {...}  # Confidence, benchmarks used, etc
            }
        """
        action = context.get('action')

        if action == 'identify_risks':
            return await self._identify_risks(context)
        elif action == 'analyze_likelihood':
            return await self._analyze_likelihood(context)
        elif action == 'calculate_impact':
            return await self._calculate_impact(context)
        elif action == 'fair_analysis':
            return await self._fair_analysis(context)
        elif action == 'plan_treatments':
            return await self._plan_treatments(context)
        else:
            return await self._general_risk_analysis(context)

    # ========================================================================
    # RISK IDENTIFICATION
    # ========================================================================

    async def _identify_risks(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Identify risks for a business process"""
        process = context.get('process', {})
        workflow_context = context.get('workflow_context', {})
        user_input = context.get('user_input', '')

        # Get similar cases from workflow context
        similar_cases = workflow_context.get('similar_cases', [])
        benchmarks = workflow_context.get('benchmarks', {})

        user_prompt = f"""
Identify business continuity risks for this process:

PROCESS INFORMATION:
- Name: {process.get('name', 'Unknown')}
- Type: {process.get('type', 'Unknown')}
- Criticality: {process.get('criticality', 'Unknown')}
- Description: {process.get('description', 'N/A')}
- Dependencies: {process.get('dependencies', [])}

USER INPUT:
{user_input if user_input else 'Perform comprehensive risk identification'}

INDUSTRY BENCHMARKS:
{self._format_benchmarks(benchmarks)}

SIMILAR CASES:
{self._format_similar_cases(similar_cases)}

Identify risks using this structure for EACH risk:
{{
    "description": "Clear risk description",
    "threat": "What threatens the process",
    "vulnerability": "What makes it vulnerable",
    "category": "operational|financial|technology|external|compliance"
}}

Provide 5-10 risks in JSON format.
"""

        response = await self._query_llm(
            system_prompt=self._build_system_prompt(),
            user_prompt=user_prompt,
            temperature=0.6  # Slightly creative for risk discovery
        )

        # Parse response
        risks = self._parse_risks_response(response)

        return self.format_response(
            insights=risks,
            recommendations=[
                "Prioritize risks by criticality of the process",
                "Consider dependencies when assessing cascading risks",
                "Review similar industry cases for additional risks"
            ],
            metadata={
                "analysis_type": "identify_risks",
                "risks_count": len(risks),
                "benchmarks_used": len(benchmarks),
                "similar_cases_used": len(similar_cases)
            }
        )

    # ========================================================================
    # LIKELIHOOD ANALYSIS
    # ========================================================================

    async def _analyze_likelihood(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze likelihood for identified risks"""
        risks = context.get('risks', [])
        workflow_context = context.get('workflow_context', {})
        benchmarks = workflow_context.get('benchmarks', {})

        user_prompt = f"""
Analyze likelihood for these risks:

RISKS:
{self._format_risks(risks)}

INDUSTRY BENCHMARKS:
{self._format_benchmarks(benchmarks)}

For EACH risk, provide likelihood analysis:
{{
    "risk_id": "risk_id_here",
    "score": 1-5,  // 1=rare, 2=unlikely, 3=possible, 4=likely, 5=almost certain
    "frequency": "Once per year|month|week|day",
    "reasoning": "Why this likelihood score",
    "confidence": 0.0-1.0  // Your confidence in this assessment
}}

Use industry data and benchmarks to inform scores.
Respond with JSON dict where keys are risk_ids.
"""

        response = await self._query_llm(
            system_prompt=self._build_system_prompt(),
            user_prompt=user_prompt,
            temperature=0.4  # Lower for quantitative assessment
        )

        # Parse response
        likelihood_scores = self._parse_likelihood_response(response, risks)

        return self.format_response(
            insights=likelihood_scores,
            recommendations=[
                "Review likelihood scores against industry benchmarks",
                "Consider historical incident data if available",
                "Update likelihood as organizational context changes"
            ],
            metadata={
                "analysis_type": "analyze_likelihood",
                "risks_analyzed": len(risks)
            }
        )

    # ========================================================================
    # IMPACT CALCULATION
    # ========================================================================

    async def _calculate_impact(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate impact across 4 dimensions"""
        risks = context.get('risks', [])
        org_size = context.get('org_size', 'medium')
        org_revenue = context.get('org_revenue', 0)
        workflow_context = context.get('workflow_context', {})

        user_prompt = f"""
Calculate impact for these risks across 4 dimensions:

RISKS (with likelihood):
{self._format_risks(risks)}

ORGANIZATION:
- Size: {org_size}
- Annual Revenue: ${org_revenue:,}

For EACH risk, calculate impact:
{{
    "risk_id": "risk_id_here",
    "financial": 0-100,  // Financial impact score (0-100)
    "operational": 0-100,  // Operational disruption (0-100)
    "reputational": 0-100,  // Reputation damage (0-100)
    "regulatory": 0-100,  // Compliance/legal impact (0-100)
    "reasoning": "Explanation for scores"
}}

Consider:
- Organization size and revenue
- Risk likelihood
- Recovery complexity
- Regulatory requirements

Respond with JSON dict where keys are risk_ids.
"""

        response = await self._query_llm(
            system_prompt=self._build_system_prompt(),
            user_prompt=user_prompt,
            temperature=0.5
        )

        # Parse response
        impact_scores = self._parse_impact_response(response, risks)

        return self.format_response(
            insights=impact_scores,
            recommendations=[
                "Prioritize risks with high financial + operational impact",
                "Consider reputational damage for customer-facing processes",
                "Review regulatory impact for compliance-critical processes"
            ],
            metadata={
                "analysis_type": "calculate_impact",
                "risks_analyzed": len(risks)
            }
        )

    # ========================================================================
    # FAIR ANALYSIS
    # ========================================================================

    async def _fair_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform FAIR analysis: TEF × LM = ALE"""
        risks = context.get('risks', [])
        org_revenue = context.get('org_revenue', 0)
        workflow_context = context.get('workflow_context', {})

        user_prompt = f"""
Perform FAIR (Factor Analysis of Information Risk) analysis:

RISKS (with likelihood + impact):
{self._format_risks(risks)}

ORGANIZATION:
- Annual Revenue: ${org_revenue:,}

For EACH risk, calculate FAIR metrics:
{{
    "risk_id": "risk_id_here",
    "tef": 0.0,  // Threat Event Frequency (events/year)
    "lm": 0.0,   // Loss Magnitude ($ per event)
    "reasoning": "How TEF and LM were calculated"
}}

TEF (Threat Event Frequency):
- Based on likelihood score (1-5)
- Convert to events per year

LM (Loss Magnitude):
- Based on impact scores
- Convert to dollar amount per event
- Consider: revenue loss, recovery costs, fines, reputation costs

Formula: ALE = TEF × LM (will be calculated automatically)

Respond with JSON dict where keys are risk_ids.
"""

        response = await self._query_llm(
            system_prompt=self._build_system_prompt(),
            user_prompt=user_prompt,
            temperature=0.3  # Very precise for financial calculations
        )

        # Parse response
        fair_metrics = self._parse_fair_response(response, risks)

        return self.format_response(
            insights=fair_metrics,
            recommendations=[
                f"Total ALE: ${sum(m.get('tef', 0) * m.get('lm', 0) for m in fair_metrics.values()):,.2f}",
                "Focus treatment on highest ALE risks first",
                "Compare ALE to treatment costs for ROI analysis"
            ],
            metadata={
                "analysis_type": "fair_analysis",
                "risks_analyzed": len(risks),
                "methodology": "FAIR"
            }
        )

    # ========================================================================
    # TREATMENT PLANNING
    # ========================================================================

    async def _plan_treatments(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Plan risk treatments"""
        risks = context.get('risks', [])
        budget = context.get('budget', 0)
        risk_appetite = context.get('risk_appetite', 'medium')
        workflow_context = context.get('workflow_context', {})

        user_prompt = f"""
Plan risk treatments based on FAIR analysis:

RISKS (with FAIR metrics):
{self._format_risks(risks)}

ORGANIZATION:
- Risk Budget: ${budget:,}
- Risk Appetite: {risk_appetite}

For EACH risk, recommend treatment:
{{
    "risk_id": "risk_id_here",
    "treatment_type": "reduce|accept|transfer|avoid",
    "actions": ["Action 1", "Action 2", ...],
    "priority": "critical|high|medium|low",
    "cost": 0.0,  // Estimated treatment cost
    "reduction": 0.0,  // Expected ALE reduction %
    "reasoning": "Why this treatment"
}}

Treatment types:
- REDUCE: Implement controls (if cost < ALE)
- ACCEPT: Live with risk (if ALE < risk appetite)
- TRANSFER: Insurance, outsourcing (if ALE high but unpredictable)
- AVOID: Eliminate activity (if ALE unacceptable)

Prioritize by:
1. ALE (highest first)
2. Treatment ROI (reduction / cost)
3. Risk appetite

Respond with JSON dict where keys are risk_ids.
"""

        response = await self._query_llm(
            system_prompt=self._build_system_prompt(),
            user_prompt=user_prompt,
            temperature=0.4
        )

        # Parse response
        treatments = self._parse_treatments_response(response, risks)

        return self.format_response(
            insights=treatments,
            recommendations=[
                "Implement critical priority treatments immediately",
                "Review treatment ROI before committing budget",
                "Monitor residual risk after treatment"
            ],
            metadata={
                "analysis_type": "plan_treatments",
                "risks_analyzed": len(risks)
            }
        )

    # ========================================================================
    # GENERAL RISK ANALYSIS
    # ========================================================================

    async def _general_risk_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """General risk analysis (fallback)"""
        org_state = context.get('organization_state', {})
        known_risks = context.get('known_risks', [])

        user_prompt = f"""
Analyze BCM risks for this organization:

ORGANIZATION:
- Name: {org_state.get('name', 'Unknown')}
- Industry: {org_state.get('industry', 'Unknown')}
- Operational Status: {org_state.get('state', {}).get('operational_status', 'N/A')}

KNOWN RISKS:
{self._format_risks(known_risks) if known_risks else 'No known risks'}

Provide:
1. Top 5 critical risks (with severity: Critical/High/Medium/Low)
2. Risk interdependencies
3. Mitigation recommendations (prioritized)
4. Early warning indicators
"""

        response = await self._query_llm(
            system_prompt=self._build_system_prompt(),
            user_prompt=user_prompt,
            temperature=0.5
        )

        # Parse response
        risks, recommendations = self._parse_general_response(response)

        return self.format_response(
            insights=risks,
            recommendations=recommendations,
            metadata={
                "analysis_type": "general_risk_analysis"
            }
        )

    # ========================================================================
    # PARSING HELPERS
    # ========================================================================

    def _parse_risks_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse identified risks from LLM response"""
        # Try JSON parsing first
        import json
        try:
            data = json.loads(response)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'risks' in data:
                return data['risks']
        except:
            pass

        # Fallback: extract from text
        risks = []
        lines = response.split('\n')
        current_risk = {}

        for line in lines:
            line = line.strip()
            if 'description' in line.lower():
                if current_risk:
                    risks.append(current_risk)
                current_risk = {'description': line.split(':', 1)[-1].strip()}
            elif 'threat' in line.lower() and current_risk:
                current_risk['threat'] = line.split(':', 1)[-1].strip()
            elif 'vulnerability' in line.lower() and current_risk:
                current_risk['vulnerability'] = line.split(':', 1)[-1].strip()
            elif 'category' in line.lower() and current_risk:
                current_risk['category'] = line.split(':', 1)[-1].strip()

        if current_risk:
            risks.append(current_risk)

        return risks if risks else [
            {
                "description": "Operational disruption risk",
                "threat": "Service interruption",
                "vulnerability": "Single point of failure",
                "category": "operational"
            }
        ]

    def _parse_likelihood_response(self, response: str, risks: List[Dict]) -> Dict[str, Any]:
        """Parse likelihood scores"""
        import json
        try:
            return json.loads(response)
        except:
            # Fallback: default scores
            return {
                risk.get('id', f"risk_{i}"): {
                    "score": 3,
                    "frequency": "Once per year",
                    "reasoning": "Default assessment",
                    "confidence": 0.5
                }
                for i, risk in enumerate(risks)
            }

    def _parse_impact_response(self, response: str, risks: List[Dict]) -> Dict[str, Any]:
        """Parse impact scores"""
        import json
        try:
            return json.loads(response)
        except:
            # Fallback: default scores
            return {
                risk.get('id', f"risk_{i}"): {
                    "financial": 50,
                    "operational": 50,
                    "reputational": 50,
                    "regulatory": 50,
                    "reasoning": "Default assessment"
                }
                for i, risk in enumerate(risks)
            }

    def _parse_fair_response(self, response: str, risks: List[Dict]) -> Dict[str, Any]:
        """Parse FAIR metrics"""
        import json
        try:
            return json.loads(response)
        except:
            # Fallback: default metrics
            return {
                risk.get('id', f"risk_{i}"): {
                    "tef": 1.0,
                    "lm": 10000.0,
                    "reasoning": "Default FAIR assessment"
                }
                for i, risk in enumerate(risks)
            }

    def _parse_treatments_response(self, response: str, risks: List[Dict]) -> Dict[str, Any]:
        """Parse treatment plans"""
        import json
        try:
            return json.loads(response)
        except:
            # Fallback: default treatments
            return {
                risk.get('id', f"risk_{i}"): {
                    "treatment_type": "reduce",
                    "actions": ["Implement controls", "Monitor risk"],
                    "priority": "medium",
                    "cost": 5000.0,
                    "reduction": 50.0,
                    "reasoning": "Default treatment plan"
                }
                for i, risk in enumerate(risks)
            }

    def _parse_general_response(self, response: str) -> tuple:
        """Parse general risk analysis"""
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

        return risks or ["Default risk analysis needed"], recommendations or ["Review risk profile"]

    # ========================================================================
    # FORMATTING HELPERS
    # ========================================================================

    def _format_risks(self, risks: List[Dict]) -> str:
        """Format risks for prompt"""
        if not risks:
            return "No risks provided"

        formatted = []
        for i, risk in enumerate(risks, 1):
            formatted.append(f"{i}. {risk.get('description', 'Unknown risk')}")
            if risk.get('id'):
                formatted.append(f"   ID: {risk['id']}")
            if risk.get('threat'):
                formatted.append(f"   Threat: {risk['threat']}")
            if risk.get('likelihood_score'):
                formatted.append(f"   Likelihood: {risk['likelihood_score']}")
            if risk.get('impact'):
                formatted.append(f"   Impact: {risk['impact']}")

        return '\n'.join(formatted)

    def _format_benchmarks(self, benchmarks: Dict) -> str:
        """Format industry benchmarks"""
        if not benchmarks:
            return "No benchmarks available"

        formatted = []
        for key, value in benchmarks.items():
            formatted.append(f"- {key}: {value}")

        return '\n'.join(formatted)

    def _format_similar_cases(self, cases: List[Dict]) -> str:
        """Format similar cases"""
        if not cases:
            return "No similar cases found"

        formatted = []
        for i, case in enumerate(cases[:3], 1):  # Limit to 3
            formatted.append(f"{i}. {case.get('description', 'Case')}")
            if case.get('outcome'):
                formatted.append(f"   Outcome: {case['outcome']}")

        return '\n'.join(formatted)
