"""
Base Specialist Class
Conversational layer for BCM AI system
"""
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import json


class BaseSpecialist(ABC):
    """
    Base class for all BCM AI Specialists

    Responsibilities:
    - Conversation management (history, context)
    - Intent detection
    - PDCA framework management
    - Delegation to Engines
    - Response formatting for UI
    """

    def __init__(self, engine=None, pdca_manager=None, rag_pipeline=None):
        """
        Initialize Specialist

        Args:
            engine: Business logic engine (e.g., RiskEngine)
            pdca_manager: PDCA framework manager
            rag_pipeline: RAG pipeline for knowledge retrieval
        """
        self.engine = engine
        self.pdca_manager = pdca_manager
        self.rag_pipeline = rag_pipeline
        self.conversation_memory = {}

    async def chat(
        self,
        message: str,
        context: Dict[str, Any],
        history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Main chat method

        Args:
            message: User message
            context: Context (process_id, org_id, industry, etc.)
            history: Conversation history

        Returns:
            {
                'response': str,
                'actions': List[dict],
                'pdca_stage': str,
                'analysis_data': dict,
                'metadata': dict
            }
        """
        # 1. Store conversation
        conversation_id = context.get('conversation_id', 'default')
        self._update_memory(conversation_id, message, history)

        # 2. Detect intent
        intent = self._detect_intent(message, context)

        # 3. Get current PDCA stage
        pdca_stage = self._get_pdca_stage(conversation_id, intent)

        # 4. Retrieve relevant knowledge (RAG)
        knowledge = await self._retrieve_knowledge(message, context)

        # 5. Delegate to engine
        engine_result = await self._delegate_to_engine(intent, context, knowledge)

        # 6. Update PDCA stage
        next_stage = self._advance_pdca(conversation_id, intent, engine_result)

        # 7. Format response
        response = self._format_response(engine_result, pdca_stage, knowledge)

        return response

    @abstractmethod
    def _detect_intent(self, message: str, context: Dict[str, Any]) -> str:
        """
        Detect user intent from message

        Must be implemented by subclass
        Returns: intent string (e.g., 'analyze_risk', 'calculate_rto')
        """
        pass

    @abstractmethod
    async def _delegate_to_engine(
        self,
        intent: str,
        context: Dict[str, Any],
        knowledge: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Delegate work to Engine based on intent

        Must be implemented by subclass
        Returns: Engine execution result
        """
        pass

    def _update_memory(
        self,
        conversation_id: str,
        message: str,
        history: List[Dict[str, str]]
    ):
        """Update conversation memory"""
        if conversation_id not in self.conversation_memory:
            self.conversation_memory[conversation_id] = {
                'messages': [],
                'context': {},
                'pdca_stage': 'plan'
            }

        self.conversation_memory[conversation_id]['messages'].append({
            'role': 'user',
            'content': message
        })

        # Keep last 10 messages
        if len(self.conversation_memory[conversation_id]['messages']) > 10:
            self.conversation_memory[conversation_id]['messages'] = \
                self.conversation_memory[conversation_id]['messages'][-10:]

    def _get_pdca_stage(self, conversation_id: str, intent: str) -> str:
        """Get current PDCA stage"""
        if self.pdca_manager:
            return self.pdca_manager.get_current_stage(conversation_id)

        # Fallback: simple mapping
        if conversation_id not in self.conversation_memory:
            return 'plan'
        return self.conversation_memory[conversation_id].get('pdca_stage', 'plan')

    def _advance_pdca(
        self,
        conversation_id: str,
        intent: str,
        engine_result: Dict[str, Any]
    ) -> str:
        """Advance PDCA stage based on intent and result"""
        if self.pdca_manager:
            return self.pdca_manager.advance_to_next_stage(
                conversation_id, intent, engine_result
            )

        # Fallback: simple progression
        stage_progression = {
            'plan': 'do',
            'do': 'check',
            'check': 'act',
            'act': 'plan'
        }

        current = self._get_pdca_stage(conversation_id, intent)
        next_stage = stage_progression.get(current, 'plan')

        if conversation_id in self.conversation_memory:
            self.conversation_memory[conversation_id]['pdca_stage'] = next_stage

        return next_stage

    async def _retrieve_knowledge(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge using RAG"""
        if not self.rag_pipeline:
            return []

        try:
            results = await self.rag_pipeline.retrieve(
                query=message,
                context=context,
                top_k=3
            )
            return results
        except Exception as e:
            print(f"RAG retrieval error: {e}")
            return []

    def _format_response(
        self,
        engine_result: Dict[str, Any],
        pdca_stage: str,
        knowledge: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Format response for UI

        Returns standardized response format
        """
        return {
            'response': engine_result.get('response', ''),
            'actions': engine_result.get('actions', []),
            'pdca_stage': pdca_stage,
            'analysis_data': engine_result.get('data', {}),
            'metadata': {
                'analyzed_at': engine_result.get('timestamp'),
                'confidence': engine_result.get('confidence', 0.0),
                'knowledge_used': len(knowledge) > 0
            }
        }

    def _suggest_actions(self, intent: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Suggest next actions based on intent and data

        Override in subclass for specific actions
        """
        return []
