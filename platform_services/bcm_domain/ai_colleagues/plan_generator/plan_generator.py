"""Plan Generator AI - BCP/DRP Generation Expert"""
import logging
from typing import Dict, Any
from platform_services.bcm_domain.ai_colleagues.base.base_colleague import BaseAIColleague, AssistantContext
from intelligent_core.ai_foundation import RAGPipeline

logger = logging.getLogger(__name__)

class PlanGeneratorAI(BaseAIColleague):
    """Plan Generator AI - BCP/DRP Expert"""

    def __init__(self, rag_pipeline: RAGPipeline, config: Dict[str, Any]):
        super().__init__(
            name="Plan Generator AI",
            specialty="BCP/DRP Generation & Recovery Strategies",
            rag_pipeline=rag_pipeline,
            config=config
        )
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
