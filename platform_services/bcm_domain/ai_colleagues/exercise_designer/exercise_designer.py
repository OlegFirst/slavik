"""Exercise Designer AI - Tabletop Exercise Expert"""
import logging
from typing import Dict, Any
from platform_services.bcm_domain.ai_colleagues.base.base_colleague import BaseAIColleague, AssistantContext
from intelligent_core.ai_foundation import RAGPipeline

logger = logging.getLogger(__name__)

class ExerciseDesignerAI(BaseAIColleague):
    """Exercise Designer AI - Tabletop Exercise Expert"""

    def __init__(self, rag_pipeline: RAGPipeline, config: Dict[str, Any]):
        super().__init__(
            name="Exercise Designer AI",
            specialty="Exercise Design & Scenario Development",
            rag_pipeline=rag_pipeline,
            config=config
        )
        self.exercises_designed = 0
        logger.info("Exercise Designer AI initialized!")

    def _build_system_prompt(self, context: AssistantContext) -> str:
        return f"""You are **Exercise Designer AI**, expert in BCM exercise design and facilitation.

**Your Expertise:**
- Tabletop exercise design
- Scenario development
- Inject creation
- Exercise evaluation
- ISO 22301 clause 8.5 requirements

**Current Context:** {context.value}

**Guidelines:**
1. Create realistic, challenging scenarios
2. Design progressive injects
3. Include evaluation criteria
4. Test specific plans and procedures
5. Facilitate learning outcomes

**Tone:** Creative, structured, educational
"""

    def _post_process_answer(self, answer: str, intent: Dict[str, Any], context: AssistantContext) -> str:
        if "exercise" in answer.lower() and "**Exercise Note:**" not in answer:
            answer += "\n\n**Exercise Note:** Capture lessons learned and update plans accordingly"
        return answer

    def get_stats(self) -> Dict[str, Any]:
        base = super().get_stats()
        base.update({"exercises_designed": self.exercises_designed})
        return base
