"""
BIA Specialist AI

AI Digital Colleague for Business Impact Analysis.

Specializes in:
- RTO/RPO determination
- Critical process identification
- Dependency mapping
- Impact assessment
- MTD/MBCO calculations
"""

import logging
from typing import Dict, Any

from platform_services.bcm_domain.ai_colleagues.base.base_colleague import BaseAIColleague, AssistantContext
from intelligent_core.ai_foundation import RAGPipeline

logger = logging.getLogger(__name__)


class BIASpecialistAI(BaseAIColleague):
    """
    BIA Specialist AI - Your Business Impact Analysis Expert

    Specializes in:
    - Business Impact Analysis methodology
    - RTO (Recovery Time Objective) determination
    - RPO (Recovery Point Objective) calculation
    - MTD (Maximum Tolerable Downtime) / MTPD assessment
    - MBCO (Minimum Business Continuity Objective)
    - Critical process identification
    - Dependency and interdependency analysis
    - Impact scoring (financial, operational, reputational)
    """

    def __init__(self, rag_pipeline: RAGPipeline, config: Dict[str, Any]):
        """Initialize BIA Specialist AI."""
        super().__init__(
            name="BIA Specialist AI",
            specialty="Business Impact Analysis & RTO/RPO Determination",
            rag_pipeline=rag_pipeline,
            config=config
        )

        self.bias_conducted = 0
        self.processes_analyzed = 0

        logger.info("BIA Specialist AI initialized and ready!")

    def _build_system_prompt(self, context: AssistantContext) -> str:
        """Build BIA Specialist AI's system prompt."""
        base_prompt = f"""You are **BIA Specialist AI**, an expert Business Impact Analysis consultant.

**Your Expertise:**
- **BIA Methodology**: ISO 22301 clause 8.2.2 requirements
- **Recovery Objectives**: RTO, RPO, MTD/MTPD, MBCO determination
- **Impact Assessment**: Financial, operational, reputational, regulatory
- **Criticality Analysis**: Tiered approach to process prioritization
- **Dependency Mapping**: Upstream/downstream dependencies
- **Resource Requirements**: People, technology, facilities, suppliers
- **BIA Questionnaires**: Design and analysis
- **Impact Quantification**: Time-based impact curves

**Your Personality:**
- Detail-oriented and methodical
- Business-focused, not just technical
- Excellent at asking the right questions
- Skilled at quantifying impacts
- Pragmatic about recovery objectives

**Current Context:** {context.value}

**Guidelines for Responses:**
1. **Focus on Business Impact**: Financial and operational consequences
2. **Be Specific with Objectives**: RTO in hours, RPO in data/transactions
3. **Consider All Impact Types**: Financial, operational, legal, reputational
4. **Map Dependencies**: Identify critical dependencies and single points of failure
5. **Tiered Criticality**: Not all processes are "critical"
6. **Realistic Objectives**: Balance business needs with cost

**Response Format:**
- Process criticality assessment
- Recommended RTO/RPO values with justification
- Impact analysis (time-based)
- Dependencies and risks
- Resource requirements for recovery

**BIA Key Metrics:**
- **RTO (Recovery Time Objective)**: Maximum acceptable downtime
- **RPO (Recovery Point Objective)**: Maximum acceptable data loss
- **MTD/MTPD**: Point of irreversible business damage
- **MBCO**: Minimum level of service to maintain viability
- **Impact over Time**: How impact increases as outage continues

**Criticality Tiers:**
- **Tier 1 (Critical)**: RTO < 4 hours, severe immediate impact
- **Tier 2 (Important)**: RTO 4-24 hours, significant impact
- **Tier 3 (Necessary)**: RTO 1-7 days, manageable impact
- **Tier 4 (Support)**: RTO > 7 days, minimal immediate impact

**Tone:** Analytical, business-focused, thorough, practical
"""

        context_guidance = {
            AssistantContext.BIA: """
**Focus Areas for BIA Context:**
- Critical process identification
- RTO/RPO analysis and determination
- Impact assessment (financial, operational)
- Dependency mapping
- Resource requirements
- BIA questionnaire design
- BIA report generation
""",
            AssistantContext.RISK: """
**Focus Areas for Risk Context:**
- Risk-BIA correlation
- Threat scenarios impact on critical processes
- Vulnerability of critical processes
- Impact-based risk prioritization
- Recovery strategy risk analysis
""",
            AssistantContext.PLANNING: """
**Focus Areas for Planning Context:**
- Recovery strategy development based on BIA
- Resource allocation based on criticality
- RTO/RPO-driven planning
- Recovery sequence and priorities
- Dependency-based recovery ordering
""",
            AssistantContext.COMPLIANCE: """
**Focus Areas for Compliance Context:**
- ISO 22301 clause 8.2.2 compliance
- BIA documentation requirements
- Stakeholder identification per ISO 22301
- BIA review and update requirements
- Audit evidence for BIA
""",
            AssistantContext.GOVERNANCE: """
**Focus Areas for Governance Context:**
- Management approval of BIA findings
- Resource allocation decisions
- Criticality tier definitions
- BIA scope and boundaries
- BIA methodology framework
"""
        }

        return base_prompt + context_guidance.get(context, "")

    def _post_process_answer(
        self,
        answer: str,
        intent: Dict[str, Any],
        context: AssistantContext
    ) -> str:
        """Post-process answer with BIA-specific formatting."""
        # Add RTO/RPO note
        if any(term in answer.lower() for term in ["rto", "rpo", "recovery time", "recovery point"]):
            if "**RTO/RPO Note:**" not in answer:
                answer += "\n\n**RTO/RPO Note:** Objectives should balance business requirements with cost. Shorter objectives = higher recovery costs."

        # Add dependency reminder
        if "depend" in answer.lower() or "critical" in answer.lower():
            if "**Dependencies:**" not in answer:
                answer += "\n\n**Dependencies:** Always consider upstream suppliers, downstream customers, and internal interdependencies."

        return answer

    async def analyze_process_criticality(
        self,
        process_data: Dict[str, Any],
        tenant_id: str = "demo"
    ) -> Dict[str, Any]:
        """
        Analyze process criticality and recommend objectives.

        Args:
            process_data: Process information
            tenant_id: Tenant ID

        Returns:
            Criticality analysis with RTO/RPO recommendations
        """
        query = f"""
        Analyze the criticality of this business process:

        **Process:** {process_data.get('name', 'Unknown')}
        **Description:** {process_data.get('description', 'Not provided')}
        **Department:** {process_data.get('department', 'Unknown')}
        **Revenue Impact:** {process_data.get('revenue_impact', 'Unknown')}/day
        **Regulatory Impact:** {process_data.get('regulatory', 'No')}
        **Customer Impact:** {process_data.get('customer_impact', 'Unknown')}

        **Provide:**
        1. Criticality tier (1-4) with justification
        2. Recommended RTO (in hours) with reasoning
        3. Recommended RPO (in hours/transactions) with reasoning
        4. MTD/MTPD estimation
        5. Impact analysis over time (1 hour, 4 hours, 24 hours, 7 days)
        6. Key dependencies
        7. Minimum resources needed for recovery
        """

        result = await self.process_message(
            user_message=query,
            context=AssistantContext.BIA,
            tenant_id=tenant_id
        )

        self.processes_analyzed += 1

        return {
            "criticality_analysis": result.content,
            "recommendations": result.actions,
            "confidence": result.confidence,
            "metadata": result.metadata
        }

    async def conduct_bia(
        self,
        organization_data: Dict[str, Any],
        tenant_id: str = "demo"
    ) -> Dict[str, Any]:
        """
        Conduct comprehensive BIA for organization.

        Args:
            organization_data: Organization and process data
            tenant_id: Tenant ID

        Returns:
            Complete BIA report
        """
        processes = organization_data.get('processes', [])
        process_summary = f"{len(processes)} processes" if processes else "No processes provided"

        query = f"""
        Conduct a Business Impact Analysis for this organization:

        **Organization:** {organization_data.get('name', 'Unknown')}
        **Industry:** {organization_data.get('industry', 'Unknown')}
        **Size:** {organization_data.get('size', 'Unknown')} employees
        **Processes:** {process_summary}

        **Provide comprehensive BIA including:**
        1. Critical process identification (Tier 1 and 2)
        2. RTO/RPO matrix for critical processes
        3. Impact assessment summary (financial, operational, reputational)
        4. Dependency map highlights
        5. Resource requirements summary
        6. Priority recovery sequence
        7. Key findings and recommendations
        8. Next steps for BCP development
        """

        result = await self.process_message(
            user_message=query,
            context=AssistantContext.BIA,
            tenant_id=tenant_id
        )

        self.bias_conducted += 1

        return {
            "bia_report": result.content,
            "critical_processes": result.actions,
            "confidence": result.confidence,
            "metadata": result.metadata
        }

    async def map_dependencies(
        self,
        process_data: Dict[str, Any],
        tenant_id: str = "demo"
    ) -> Dict[str, Any]:
        """
        Map process dependencies.

        Args:
            process_data: Process information
            tenant_id: Tenant ID

        Returns:
            Dependency map with risk analysis
        """
        query = f"""
        Map dependencies for this critical process:

        **Process:** {process_data.get('name', 'Unknown')}
        **Function:** {process_data.get('function', 'Unknown')}

        **Identify:**
        1. **Upstream Dependencies** (suppliers, data sources, prerequisites)
        2. **Downstream Dependencies** (customers, dependent processes)
        3. **Internal Dependencies** (people, technology, facilities)
        4. **External Dependencies** (vendors, utilities, third parties)
        5. **Single Points of Failure** (critical dependencies with no backup)
        6. **Dependency Risks** (what if each dependency fails?)
        7. **Mitigation Strategies** (how to reduce dependency risks)
        """

        result = await self.process_message(
            user_message=query,
            context=AssistantContext.BIA,
            tenant_id=tenant_id
        )

        return {
            "dependency_map": result.content,
            "risks": result.actions,
            "confidence": result.confidence,
            "metadata": result.metadata
        }

    async def calculate_impact_over_time(
        self,
        process_data: Dict[str, Any],
        tenant_id: str = "demo"
    ) -> Dict[str, Any]:
        """
        Calculate impact curve over time for process outage.

        Args:
            process_data: Process information
            tenant_id: Tenant ID

        Returns:
            Time-based impact analysis
        """
        query = f"""
        Calculate impact over time for outage of this process:

        **Process:** {process_data.get('name', 'Unknown')}
        **Daily Revenue:** {process_data.get('daily_revenue', 'Unknown')}
        **Customers Affected:** {process_data.get('customers', 'Unknown')}

        **Provide impact analysis at:**
        - **1 hour**: Immediate consequences
        - **4 hours**: Short-term impacts
        - **24 hours**: One business day impact
        - **3 days**: Multi-day consequences
        - **1 week**: Extended outage impact
        - **1 month**: Long-term business damage

        **Include:**
        - Financial impact (cumulative)
        - Operational impact
        - Reputational damage
        - Regulatory/legal consequences
        - Point of no return (MTD)
        """

        result = await self.process_message(
            user_message=query,
            context=AssistantContext.BIA,
            tenant_id=tenant_id
        )

        return {
            "impact_curve": result.content,
            "critical_timeframes": result.actions,
            "confidence": result.confidence,
            "metadata": result.metadata
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get BIA Specialist AI statistics"""
        base_stats = super().get_stats()
        base_stats.update({
            "bias_conducted": self.bias_conducted,
            "processes_analyzed": self.processes_analyzed
        })
        return base_stats
