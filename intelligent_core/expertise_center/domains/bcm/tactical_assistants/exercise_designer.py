"""Exercise Designer AI - Tabletop Exercise Expert"""
import logging
from typing import Optional, Dict, Any
from expertise_center.shared.base import BaseTacticalAssistant

logger = logging.getLogger(__name__)

class ExerciseDesignerAI(BaseTacticalAssistant):
    """Exercise Designer AI - Tabletop Exercise Expert"""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize ExerciseDesignerAI."""
        super().__init__(
            assistant_id="exercise_designer",
            name="Exercise Designer AI",
            specialty="Exercise Design & Scenario Development",
            domain="bcm"
        )

        # AI Foundation integrations inherited from BaseTacticalAssistant:
        # self.rag, self.llm, self.context_builder are available

        self.config = config or {}
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
