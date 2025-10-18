"""
Risk Analyst AI

AI Digital Colleague for risk assessment and quantification.

Specializes in:
- FAIR (Factor Analysis of Information Risk) methodology
- Quantitative risk analysis
- Threat modeling
- Risk treatment recommendations
- Risk-BIA integration
"""

import logging
from typing import Dict, Any

from platform_services.bcm_domain.ai_colleagues.base.base_colleague import BaseAIColleague, AssistantContext
from intelligent_core.ai_foundation import RAGPipeline

logger = logging.getLogger(__name__)


class RiskAnalystAI(BaseAIColleague):
    """
    Risk Analyst AI - Your Risk Assessment Expert

    Specializes in:
    - FAIR methodology for risk quantification
    - ISO 27005 risk assessment
    - Threat and vulnerability analysis
    - Risk treatment strategy development
    - Risk-BIA correlation
    - Risk register management
    - Quantitative vs. qualitative analysis
    """

    def __init__(self, rag_pipeline: RAGPipeline, config: Dict[str, Any]):
        """Initialize Risk Analyst AI."""
        super().__init__(
            name="Risk Analyst AI",
            specialty="FAIR Methodology & Risk Quantification",
            rag_pipeline=rag_pipeline,
            config=config
        )

        self.risks_analyzed = 0
        self.fair_assessments = 0

        logger.info("Risk Analyst AI initialized and ready!")

    def _build_system_prompt(self, context: AssistantContext) -> str:
        """Build Risk Analyst AI's system prompt."""
        base_prompt = f"""You are **Risk Analyst AI**, an expert risk assessment consultant specializing in quantitative risk analysis.

**Your Expertise:**
- **FAIR Methodology**: Factor Analysis of Information Risk for quantitative risk assessment
- **ISO 27005**: Information security risk management
- **ISO 22301 Clause 8.2**: Risk assessment and treatment requirements
- **Threat Modeling**: STRIDE, PASTA, attack trees
- **Risk Quantification**: Loss Event Frequency (LEF), Loss Magnitude (LM), Annual Loss Expectancy (ALE)
- **Risk Matrices**: Likelihood vs Impact analysis
- **Risk Treatment**: Avoidance, mitigation, transfer, acceptance
- **Risk-BIA Integration**: Connecting risk scenarios to business impacts

**Your Personality:**
- Analytical and data-driven
- Balances quantitative and qualitative approaches
- Risk-aware but pragmatic
- Excellent at explaining complex risk concepts simply
- Focus on actionable risk treatments

**Current Context:** {context.value}

**Guidelines for Responses:**
1. **Use FAIR When Possible**: Quantify risks in monetary terms (LEF × LM = ALE)
2. **Provide Probabilities**: Express likelihood as percentages or frequencies
3. **Reference Standards**: Cite ISO 22301, ISO 27005, NIST frameworks
4. **Show Your Work**: Explain risk calculation logic
5. **Prioritize Realistically**: Not everything is "high" risk
6. **Suggest Treatments**: Always provide risk treatment options

**Response Format:**
- Risk assessment summary
- Quantitative analysis (if data available)
- Top risks with prioritization
- Treatment recommendations
- Residual risk estimation

**FAIR Components:**
- **Threat Event Frequency (TEF)** = Contact Frequency × Probability of Action
- **Vulnerability** = Threat Capability vs. Resistance Strength
- **Loss Magnitude** = Primary Loss + Secondary Loss
- **Risk** = Loss Event Frequency × Loss Magnitude

**Tone:** Analytical, clear, balanced, actionable
"""

        context_guidance = {
            AssistantContext.RISK: """
**Focus Areas for Risk Context:**
- Risk register analysis and prioritization
- Threat and vulnerability identification
- Risk scenarios and narratives
- Risk treatment tracking
- Control effectiveness assessment
- Residual risk calculation
""",
            AssistantContext.BIA: """
**Focus Areas for BIA Context:**
- Risk-BIA correlation
- Impact analysis for risk scenarios
- Critical asset identification
- Threat scenarios affecting critical processes
- RTO/RPO risk implications
""",
            AssistantContext.COMPLIANCE: """
**Focus Areas for Compliance Context:**
- ISO 22301 clause 8.2 compliance (Risk assessment)
- Risk management framework requirements
- Risk documentation requirements
- Audit evidence for risk assessments
- Risk acceptance criteria
""",
            AssistantContext.GOVERNANCE: """
**Focus Areas for Governance Context:**
- Risk appetite and tolerance levels
- Risk governance structure
- Risk reporting to management
- Risk-based decision making
- Enterprise risk management integration
""",
            AssistantContext.PLANNING: """
**Focus Areas for Planning Context:**
- Risk treatment planning
- Control implementation planning
- Risk mitigation roadmap
- Resource allocation for risk treatments
- Risk monitoring and review planning
"""
        }

        return base_prompt + context_guidance.get(context, "")

    def _post_process_answer(
        self,
        answer: str,
        intent: Dict[str, Any],
        context: AssistantContext
    ) -> str:
        """Post-process answer with risk analysis formatting."""
        # Add FAIR note for quantitative analysis
        if any(term in answer.lower() for term in ["fair", "ale", "lef", "magnitude", "quantitative"]):
            if "**FAIR Note:**" not in answer:
                answer += "\n\n**FAIR Note:** Risk quantification uses FAIR methodology (Loss Event Frequency × Loss Magnitude). Values are estimates based on available data and expert judgment."

        # Add risk treatment reminder
        if "treatment" in answer.lower() or "mitigation" in answer.lower():
            if "**Treatment Options:**" not in answer:
                answer += "\n\n**Treatment Options:** Remember the 4 Ts: Transfer (insurance), Tolerate (accept), Treat (mitigate), Terminate (avoid)."

        return answer

    async def assess_risk(
        self,
        risk_data: Dict[str, Any],
        tenant_id: str = "demo"
    ) -> Dict[str, Any]:
        """
        Perform comprehensive risk assessment.

        Args:
            risk_data: Risk scenario data
            tenant_id: Tenant ID

        Returns:
            Risk assessment with FAIR quantification
        """
        query = f"""
        Perform a comprehensive risk assessment for this scenario:

        **Risk Scenario:**
        {risk_data.get('description', 'Unknown risk')}

        **Asset at Risk:**
        {risk_data.get('asset', 'Not specified')}

        **Threat Source:**
        {risk_data.get('threat', 'Not specified')}

        **Vulnerability:**
        {risk_data.get('vulnerability', 'Not specified')}

        **Provide:**
        1. FAIR quantitative assessment (if possible)
        2. Likelihood analysis (TEF estimation)
        3. Impact analysis (Loss Magnitude estimation)
        4. Overall risk level (LEF × LM)
        5. Risk treatment recommendations
        6. Residual risk after treatment
        """

        result = await self.process_message(
            user_message=query,
            context=AssistantContext.RISK,
            tenant_id=tenant_id
        )

        self.risks_analyzed += 1
        self.fair_assessments += 1

        return {
            "risk_assessment": result.content,
            "treatments": result.actions,
            "confidence": result.confidence,
            "metadata": result.metadata
        }

    async def prioritize_risks(
        self,
        risks: list,
        tenant_id: str = "demo"
    ) -> Dict[str, Any]:
        """
        Prioritize multiple risks.

        Args:
            risks: List of risk scenarios
            tenant_id: Tenant ID

        Returns:
            Prioritized risk list with recommendations
        """
        risk_summary = "\n".join([
            f"{i+1}. {r.get('title', 'Unknown')}: L={r.get('likelihood', '?')}, I={r.get('impact', '?')}"
            for i, r in enumerate(risks[:10])  # Top 10
        ])

        query = f"""
        Prioritize these {len(risks)} risks for a BCM program:

        {risk_summary}

        **Provide:**
        1. Top 5 critical risks (highest priority)
        2. Prioritization rationale (why these are top)
        3. Quick wins (easy to mitigate)
        4. Long-term concerns (strategic risks)
        5. Resource allocation recommendations
        """

        result = await self.process_message(
            user_message=query,
            context=AssistantContext.RISK,
            tenant_id=tenant_id
        )

        return {
            "prioritization": result.content,
            "top_risks": result.actions,
            "confidence": result.confidence,
            "metadata": result.metadata
        }

    async def suggest_risk_treatments(
        self,
        risk_id: str,
        risk_data: Dict[str, Any],
        tenant_id: str = "demo"
    ) -> Dict[str, Any]:
        """
        Suggest risk treatment options.

        Args:
            risk_id: Risk identifier
            risk_data: Risk details
            tenant_id: Tenant ID

        Returns:
            Treatment options with cost-benefit analysis
        """
        query = f"""
        Suggest risk treatment options for:

        **Risk ID:** {risk_id}
        **Risk:** {risk_data.get('title', 'Unknown')}
        **Current Risk Level:** {risk_data.get('risk_level', 'Unknown')}
        **Risk Score:** {risk_data.get('risk_score', 'Unknown')}

        **Provide:**
        1. **Transfer** options (insurance, outsourcing)
        2. **Tolerate** analysis (is acceptance viable?)
        3. **Treat** options (controls, mitigations)
        4. **Terminate** options (avoid the activity)
        5. Cost-benefit analysis for each option
        6. Recommended treatment strategy
        7. Residual risk after treatment
        """

        result = await self.process_message(
            user_message=query,
            context=AssistantContext.RISK,
            tenant_id=tenant_id
        )

        return {
            "treatment_options": result.content,
            "recommendations": result.actions,
            "confidence": result.confidence,
            "metadata": result.metadata
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get Risk Analyst AI statistics"""
        base_stats = super().get_stats()
        base_stats.update({
            "risks_analyzed": self.risks_analyzed,
            "fair_assessments": self.fair_assessments
        })
        return base_stats
