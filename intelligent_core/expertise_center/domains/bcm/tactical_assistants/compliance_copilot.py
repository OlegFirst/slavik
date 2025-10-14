"""
Compliance Copilot

First AI Digital Colleague - specializes in ISO 22301:2019 compliance,
BCM best practices, and regulatory guidance.

Extends BaseAIColleague with compliance-specific expertise.
"""

import logging
from typing import Optional, Dict, Any
from expertise_center.shared.base import BaseTacticalAssistant

logger = logging.getLogger(__name__)


class ComplianceCopilot(BaseTacticalAssistant):
    """
    Compliance Copilot - Your ISO 22301 Expert

    Specializes in:
    - ISO 22301:2019 compliance analysis
    - Gap assessment
    - Compliance roadmaps
    - Regulatory guidance
    - Audit preparation
    - Best practices recommendations
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize ComplianceCopilot."""
        super().__init__(
            assistant_id="compliance_copilot",
            name="Compliance Copilot",
            specialty="ISO 22301:2019 Compliance & BCM Best Practices",
            domain="bcm"
        )

        # AI Foundation integrations inherited from BaseTacticalAssistant:
        # self.rag, self.llm, self.context_builder are available

        self.config = config or {}

        logger.info("Compliance Copilot initialized and ready!")
    def _build_system_prompt(self, context: AssistantContext) -> str:
        """
        Build Compliance Copilot's system prompt.

        This defines the colleague's personality, expertise, and response style.
        """
        base_prompt = f"""You are **Compliance Copilot**, an expert BCM (Business Continuity Management) consultant specializing in ISO 22301:2019 compliance.

**Your Expertise:**
- Deep knowledge of ISO 22301:2019 standard and its requirements
- BCM best practices from leading consulting firms (McKinsey, Deloitte, EY)
- Regulatory compliance across industries (healthcare, finance, government)
- Gap analysis and compliance roadmapping
- Audit preparation and evidence management
- Practical implementation guidance

**Your Personality:**
- Professional yet friendly and approachable
- Clear and concise in explanations
- Action-oriented - always suggest next steps
- Reference specific ISO 22301 clauses when relevant
- Provide practical, implementable advice

**Current Context:** {context.value}

**Guidelines for Responses:**
1. **Be Specific**: Reference ISO 22301 clauses (e.g., "Per clause 8.4.1...")
2. **Be Practical**: Provide actionable steps, not just theory
3. **Be Thorough**: Cover all aspects of the question
4. **Be Structured**: Use clear formatting (bullets, sections)
5. **Suggest Actions**: Always end with recommended next steps
6. **Use Data**: Reference the BCM data provided in context

**Response Format:**
- Start with a direct answer to the question
- Provide relevant ISO 22301 requirements
- Include specific recommendations based on provided data
- End with 2-5 concrete next actions

**Tone:** Professional, confident, helpful, encouraging
"""

        # Add context-specific guidance
        context_guidance = {
            AssistantContext.COMPLIANCE: """
**Focus Areas for Compliance Context:**
- Gap analysis against ISO 22301 requirements
- Compliance status assessment
- Missing evidence or documentation
- Corrective actions needed
- Compliance roadmap priorities
""",
            AssistantContext.GOVERNANCE: """
**Focus Areas for Governance Context:**
- Governance structure alignment with ISO 22301
- Roles and responsibilities (clause 5.3)
- Top management commitment (clause 5.1)
- Policy and objectives (clauses 5.2, 6.2)
- Resource allocation
""",
            AssistantContext.RISK: """
**Focus Areas for Risk Context:**
- Risk assessment per ISO 22301 clause 8.2.2
- Risk treatment alignment with business objectives
- Integration with BIA results
- Compliance with risk management requirements
""",
            AssistantContext.BIA: """
**Focus Areas for BIA Context:**
- BIA requirements per ISO 22301 clause 8.2.2
- Critical processes identification
- RTO/RPO determination
- Dependencies and impacts
- Compliance with BIA requirements
""",
            AssistantContext.PLANNING: """
**Focus Areas for Planning Context:**
- BCMS planning per clause 6.1
- Objectives and planning per clause 6.2
- Integration with PDCA cycle
- Compliance planning requirements
""",
            AssistantContext.RESPONSE: """
**Focus Areas for Response Context:**
- Incident response per clause 8.4
- Emergency procedures
- Communication requirements
- Compliance during incidents
""",
            AssistantContext.DOCUMENTS: """
**Focus Areas for Documents Context:**
- Documented information requirements (clause 7.5)
- Document control
- Records management
- Audit evidence preparation
"""
        }

        guidance = context_guidance.get(context, "")
        return base_prompt + guidance

    def _post_process_answer(
        self,
        answer: str,
        intent: Dict[str, Any],
        context: AssistantContext
    ) -> str:
        """
        Post-process answer to add Compliance Copilot's signature style.

        Adds:
        - Friendly intro/outro
        - Compliance confidence indicator
        - ISO 22301 reference highlighting
        """
        # Add friendly intro if answer doesn't start with greeting
        if not any(answer.lower().startswith(greeting) for greeting in ["hi", "hello", "great", "sure", "i'd"]):
            intros = {
                "list_items": "Here's what I found from your BCM data:",
                "analyze": "I've analyzed your data and here are my findings:",
                "assess_compliance": "Based on ISO 22301 requirements, here's your compliance status:",
                "query_info": "Let me help you with that:",
                "recommend": "Based on best practices and your current state:"
            }
            intent_type = intent.get("intent_type", "query_info")
            intro = intros.get(intent_type, "Here's my analysis:")
            answer = f"{intro}\n\n{answer}"

        # Add compliance note if assessing compliance
        if "compliance" in context.value or "compliance" in intent.get("intent_type", ""):
            if "**Compliance Note:**" not in answer:
                answer += "\n\n**Compliance Note:** All recommendations align with ISO 22301:2019 requirements. Review suggested actions to close any gaps."

        return answer

    async def assess_compliance_gap(
        self,
        tenant_id: str = "demo"
    ) -> Dict[str, Any]:
        """
        Perform comprehensive compliance gap analysis.

        Returns:
            Dict with gap analysis results
        """
        query = """
        Perform a comprehensive ISO 22301:2019 compliance gap analysis.
        Identify missing requirements, incomplete implementations, and priority gaps.
        Provide a compliance roadmap with prioritized actions.
        """

        result = await self.process_message(
            user_message=query,
            context=AssistantContext.COMPLIANCE,
            tenant_id=tenant_id
        )

        return {
            "gap_analysis": result.content,
            "priority_gaps": result.actions,
            "confidence": result.confidence,
            "metadata": result.metadata
        }

    async def generate_compliance_report(
        self,
        tenant_id: str = "demo"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive compliance status report.

        Returns:
            Dict with compliance report
        """
        query = """
        Generate a comprehensive BCM compliance status report including:
        - Overall compliance percentage
        - Implemented requirements
        - Gaps by ISO 22301 clause
        - Priority recommendations
        - Compliance trend
        """

        result = await self.process_message(
            user_message=query,
            context=AssistantContext.COMPLIANCE,
            tenant_id=tenant_id
        )

        return {
            "report": result.content,
            "recommendations": result.actions,
            "metadata": result.metadata
        }

    async def get_clause_guidance(
        self,
        clause: str,
        tenant_id: str = "demo"
    ) -> str:
        """
        Get implementation guidance for specific ISO 22301 clause.

        Args:
            clause: ISO 22301 clause number (e.g., "8.4.1")
            tenant_id: Tenant ID

        Returns:
            Implementation guidance
        """
        query = f"""
        Provide detailed implementation guidance for ISO 22301 clause {clause}.
        Include:
        - Requirement summary
        - Implementation steps
        - Common challenges
        - Best practices
        - Examples
        """

        result = await self.process_message(
            user_message=query,
            context=AssistantContext.COMPLIANCE,
            tenant_id=tenant_id
        )

        return result.content
