"""
Base AI Colleague

Foundation class for all AI Digital Colleagues.
Extends PDCA Assistant framework with RAG capabilities.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum
from pydantic import BaseModel, Field

from intelligent_core.ai_foundation import RAGPipeline

logger = logging.getLogger(__name__)


# Re-export PDCA models from original implementation
class PDCAPhase(str, Enum):
    PLAN = "plan"
    DO = "do"
    CHECK = "check"
    ACT = "act"


class AssistantContext(str, Enum):
    OVERVIEW = "overview"
    EVENTS = "events"
    ORCHESTRATOR = "orchestrator"
    DOCUMENTS = "documents"
    EXERCISES = "exercises"
    GOVERNANCE = "governance"
    TRAINING = "training"
    ADMIN = "admin"
    # BCM-specific contexts
    RISK = "risk"
    BIA = "bia"
    PLANNING = "planning"
    COMPLIANCE = "compliance"
    RESPONSE = "response"


class ActionType(str, Enum):
    SUGGEST = "suggest"
    CREATE = "create"
    ANALYZE = "analyze"
    REPORT = "report"
    SCHEDULE = "schedule"
    REVIEW = "review"


class NextBestAction(BaseModel):
    """Action suggestion with PDCA context"""
    id: str
    phase: PDCAPhase
    context: AssistantContext
    action_type: ActionType
    title: str
    description: str
    priority: str = "medium"  # low, medium, high, critical
    confidence: float = 0.8
    estimated_time: int = 15  # minutes
    prerequisites: List[str] = Field(default_factory=list)
    expected_outcome: str = ""
    api_endpoint: Optional[str] = None
    payload_template: Optional[Dict] = None


class AssistantMessage(BaseModel):
    """Message from AI colleague"""
    id: str
    sender: str  # user, assistant, colleague_name
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    phase: Optional[PDCAPhase] = None
    context: Optional[AssistantContext] = None
    confidence: Optional[float] = None
    actions: List[NextBestAction] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseAIColleague(ABC):
    """
    Base class for all AI Digital Colleagues.

    Provides:
    - PDCA framework (from original PDCA Assistant)
    - RAG capabilities (new)
    - Conversation tracking
    - EventBus integration
    - Action suggestions

    Each colleague specializes by:
    - Implementing _build_system_prompt()
    - Customizing _post_process_answer()
    - Defining specialty-specific actions
    """

    def __init__(
        self,
        name: str,
        specialty: str,
        rag_pipeline: RAGPipeline,
        config: Dict[str, Any]
    ):
        """
        Initialize AI colleague.

        Args:
            name: Colleague name (e.g., "Compliance Copilot")
            specialty: Specialty area (e.g., "ISO 22301 Compliance")
            rag_pipeline: Shared RAG pipeline instance
            config: Configuration dict
        """
        self.name = name
        self.specialty = specialty
        self.rag = rag_pipeline
        self.config = config

        # PDCA state (from original PDCA Assistant)
        self.current_phase = PDCAPhase.PLAN
        self.current_context = AssistantContext.OVERVIEW
        self.conversation_history: List[AssistantMessage] = []
        self.phase_progress = {"plan": 25, "do": 50, "check": 75, "act": 100}

        logger.info(f"Initialized {self.name} ({self.specialty})")

    async def process_message(
        self,
        user_message: str,
        context: AssistantContext,
        tenant_id: str = "demo"
    ) -> AssistantMessage:
        """
        Process user message through RAG pipeline.

        This is the MAIN method - replaces PDCA Assistant's hardcoded responses
        with RAG + Claude.

        Args:
            user_message: User's query
            context: BCM context (risk, bia, compliance, etc.)
            tenant_id: Tenant identifier

        Returns:
            AssistantMessage with answer and suggested actions
        """
        try:
            self.current_context = context
            logger.info(f"{self.name}: Processing message in {context.value} context")

            # Build conversation history for RAG
            conversation_for_rag = self._build_conversation_history()

            # Build system prompt (colleague-specific)
            system_prompt = self._build_system_prompt(context)

            # Process through RAG Pipeline
            rag_result = await self.rag.process_query(
                query=user_message,
                tenant_id=tenant_id,
                conversation_history=conversation_for_rag,
                system_prompt=system_prompt
            )

            # Post-process answer (colleague-specific customization)
            final_answer = self._post_process_answer(
                rag_result.answer,
                rag_result.intent,
                context
            )

            # Convert RAG suggested actions to NextBestAction format
            actions = self._convert_to_next_best_actions(
                rag_result.suggested_actions,
                context
            )

            # Create assistant message
            assistant_message = AssistantMessage(
                id=f"msg_{datetime.utcnow().timestamp()}",
                sender=self.name.lower().replace(" ", "_"),
                content=final_answer,
                phase=self.current_phase,
                context=context,
                confidence=rag_result.confidence,
                actions=actions,
                metadata={
                    "intent": rag_result.intent,
                    "context_used": rag_result.context_used,
                    "model": rag_result.model_used,
                    "tokens": rag_result.tokens_used,
                    "tenant_id": tenant_id
                }
            )

            # Store in history
            self.conversation_history.append(assistant_message)

            # Keep only last 10 messages
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]

            logger.info(
                f"{self.name}: Processed message "
                f"(confidence: {rag_result.confidence:.2f}, "
                f"actions: {len(actions)}, "
                f"tokens: {rag_result.tokens_used})"
            )

            return assistant_message

        except Exception as e:
            logger.error(f"{self.name}: Failed to process message: {e}", exc_info=True)
            # Return error message
            return AssistantMessage(
                id=f"msg_{datetime.utcnow().timestamp()}",
                sender=self.name.lower().replace(" ", "_"),
                content=f"I apologize, but I encountered an error: {str(e)}. Please try again.",
                phase=self.current_phase,
                context=context,
                confidence=0.0,
                actions=[],
                metadata={"error": str(e), "tenant_id": tenant_id}
            )

    @abstractmethod
    def _build_system_prompt(self, context: AssistantContext) -> str:
        """
        Build colleague-specific system prompt.

        Each colleague implements this to define their personality,
        expertise, and response style.

        Args:
            context: Current BCM context

        Returns:
            System prompt string
        """
        pass

    def _post_process_answer(
        self,
        answer: str,
        intent: Dict[str, Any],
        context: AssistantContext
    ) -> str:
        """
        Post-process Claude's answer.

        Override this to add colleague-specific formatting,
        additions, or modifications to the answer.

        Args:
            answer: Raw answer from Claude
            intent: Detected intent
            context: BCM context

        Returns:
            Processed answer
        """
        # Default: return as-is
        return answer

    def _convert_to_next_best_actions(
        self,
        rag_actions: List[Dict[str, Any]],
        context: AssistantContext
    ) -> List[NextBestAction]:
        """
        Convert RAG suggested actions to NextBestAction format.

        Args:
            rag_actions: Actions from RAG pipeline
            context: Current context

        Returns:
            List of NextBestAction
        """
        actions = []

        for idx, rag_action in enumerate(rag_actions):
            action = NextBestAction(
                id=f"{self.name.lower().replace(' ', '_')}_action_{idx}_{datetime.utcnow().timestamp()}",
                phase=self.current_phase,
                context=context,
                action_type=self._map_action_type(rag_action.get("type", "suggest")),
                title=rag_action.get("title", "")[:100],
                description=rag_action.get("description", ""),
                priority=rag_action.get("priority", "medium"),
                confidence=0.8,
                estimated_time=15
            )
            actions.append(action)

        return actions

    def _map_action_type(self, action_type_str: str) -> ActionType:
        """Map string action type to ActionType enum"""
        mapping = {
            "suggest": ActionType.SUGGEST,
            "create": ActionType.CREATE,
            "analyze": ActionType.ANALYZE,
            "report": ActionType.REPORT,
            "schedule": ActionType.SCHEDULE,
            "review": ActionType.REVIEW
        }
        return mapping.get(action_type_str.lower(), ActionType.SUGGEST)

    def _build_conversation_history(self) -> List[Dict[str, str]]:
        """
        Build conversation history for RAG in Claude format.

        Returns:
            List of {"role": "user"|"assistant", "content": "..."}
        """
        history = []

        for msg in self.conversation_history[-5:]:  # Last 5 messages
            role = "assistant" if msg.sender != "user" else "user"
            history.append({
                "role": role,
                "content": msg.content
            })

        return history

    async def update_phase(self, phase: PDCAPhase):
        """Update current PDCA phase"""
        self.current_phase = phase
        logger.info(f"{self.name}: Phase updated to {phase.value}")

    def get_stats(self) -> Dict[str, Any]:
        """Get colleague statistics"""
        return {
            "name": self.name,
            "specialty": self.specialty,
            "current_phase": self.current_phase.value,
            "current_context": self.current_context.value,
            "conversation_length": len(self.conversation_history),
            "phase_progress": self.phase_progress
        }
