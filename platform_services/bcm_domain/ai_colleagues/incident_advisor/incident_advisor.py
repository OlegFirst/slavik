"""Incident Advisor AI - Crisis Response Expert"""
import logging
from typing import Dict, Any
from platform_services.bcm_domain.ai_colleagues.base.base_colleague import BaseAIColleague, AssistantContext
from intelligent_core.ai_foundation import RAGPipeline

logger = logging.getLogger(__name__)

class IncidentAdvisorAI(BaseAIColleague):
    """Incident Advisor AI - Crisis Response Expert"""

    def __init__(self, rag_pipeline: RAGPipeline, config: Dict[str, Any]):
        super().__init__(
            name="Incident Advisor AI",
            specialty="Incident Response & Crisis Management",
            rag_pipeline=rag_pipeline,
            config=config
        )
        self.incidents_advised = 0
        logger.info("Incident Advisor AI initialized!")

    def _build_system_prompt(self, context: AssistantContext) -> str:
        return f"""You are **Incident Advisor AI**, expert in incident response and crisis management.

**Your Expertise:**
- ISO 22301 clause 8.4 incident response
- Crisis management
- Escalation procedures
- Communication templates
- Post-incident analysis

**Current Context:** {context.value}

**Guidelines:**
1. Provide immediate, actionable guidance
2. Assess severity and recommend escalation
3. Suggest communication strategies
4. Reference incident response plans
5. Focus on containment and recovery

**Tone:** Calm, decisive, clear, supportive
"""

    def _post_process_answer(self, answer: str, intent: Dict[str, Any], context: AssistantContext) -> str:
        if "incident" in answer.lower() and "**Incident Note:**" not in answer:
            answer += "\n\n**Incident Note:** Document all actions and decisions for post-incident review"
        return answer

    def get_stats(self) -> Dict[str, Any]:
        base = super().get_stats()
        base.update({"incidents_advised": self.incidents_advised})
        return base
