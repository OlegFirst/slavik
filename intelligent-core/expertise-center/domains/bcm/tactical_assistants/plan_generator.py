"""Plan Generator AI - BCP/DRP Generation Expert"""
import logging
from typing import Optional, Dict, Any
from expertise_center.shared.base import BaseTacticalAssistant

logger = logging.getLogger(__name__)

class PlanGeneratorAI(BaseTacticalAssistant):
    """Plan Generator AI - BCP/DRP Expert"""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize PlanGeneratorAI."""
        super().__init__(
            assistant_id="plan_generator",
            name="Plan Generator AI",
            specialty="BCP/DRP Generation & Recovery Strategies",
            domain="bcm"
        )

        # AI Foundation integrations inherited from BaseTacticalAssistant:
        # self.rag, self.llm, self.context_builder are available

        self.config = config or {}
        self.plans_generated = 0

        logger.info("Plan Generator AI initialized!")
    def _build_system_prompt(self, context: AssistantContext) -> str:
        return f"""You are **Plan Generator AI**, expert in Business Continuity and Disaster Recovery planning.

**Your Expertise:**
- BCP/DRP development per ISO 22301 clause 8.3
- Recovery strategy design
- Plan templates and runbooks
- RTO/RPO-driven planning
- Risk-based recovery priorities

**Current Context:** {context.value}

**Guidelines:**
1. Reference ISO 22301 requirements
2. Align with BIA (RTO/RPO) and Risk data
3. Create actionable, testable plans
4. Include specific recovery steps
5. Define roles and responsibilities

**Tone:** Professional, detailed, structured
"""

    def _post_process_answer(self, answer: str, intent: Dict[str, Any], context: AssistantContext) -> str:
        if "plan" in answer.lower() and "**Plan Note:**" not in answer:
            answer += "\n\n**Plan Note:** All plans should be tested through exercises per ISO 22301 clause 8.5"
        return answer

    def get_stats(self) -> Dict[str, Any]:
        base = super().get_stats()
        base.update({"plans_generated": self.plans_generated})
        return base
