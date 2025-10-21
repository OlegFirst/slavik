"""
AI Foundation Integration for Collective Intelligence

Integrates RAG Pipeline and LLM Router from ai_foundation:
- RAG: Retrieves similar case studies before agent creation
- LLM: Uses unified router for response generation with automatic task routing
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import sys

# Add ai-foundation to path
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root / "intelligent-core" / "ai-foundation"))

from rag.pipeline import RAGPipeline
from llm.llm_router import LLMRouter

logger = logging.getLogger(__name__)


class CollectiveAIFoundation:
    """
    AI Foundation integration for Collective Intelligence

    Provides:
    - RAG-enhanced case retrieval
    - LLM Router for response generation
    - Knowledge storage for learning
    """

    def __init__(self):
        self.rag: Optional[RAGPipeline] = None
        self.llm: Optional[LLMRouter] = None

    async def initialize(self):
        """Initialize AI Foundation components"""

        try:
            # Initialize RAG for knowledge retrieval
            self.rag = RAGPipeline()
            logger.info(" RAG Pipeline initialized for Collective Intelligence")

            # Initialize LLM Router for response generation
            self.llm = LLMRouter()
            logger.info(" LLM Router initialized for Collective Intelligence")

        except Exception as e:
            logger.error(f" AI Foundation initialization failed: {e}")
            raise

    async def retrieve_similar_cases(
        self,
        problem_type: str,
        requesting_org_context: Dict[str, Any],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar cases from RAG knowledge base

        Enhances case retrieval with semantic search

        Args:
            problem_type: Type of problem (e.g., "supply_chain_complexity")
            requesting_org_context: Context about requesting org (industry, size, etc.)
            top_k: Number of similar cases to retrieve

        Returns:
            List of similar cases with relevance scores
        """

        if not self.rag:
            logger.warning("RAG not initialized, skipping enhanced retrieval")
            return []

        # Build search query
        search_query = f"""
        Problem: {problem_type}

        Looking for successful approaches from organizations similar to:
        Industry: {requesting_org_context.get('industry', 'any')}
        Size: {requesting_org_context.get('size', 'any')}
        Region: {requesting_org_context.get('region', 'any')}

        Find cases where organizations successfully solved this problem.
        """

        try:
            similar_cases = await self.rag.retrieve(
                query=search_query,
                context={
                    "domain": "collective_intelligence",
                    "problem_type": problem_type,
                    "requesting_org": requesting_org_context
                },
                top_k=top_k,
                filters={"source_type": "collective_cases", "problem_type": problem_type},
                enable_reranking=True
            )

            logger.info(f" Retrieved {len(similar_cases)} similar cases from RAG")

            return similar_cases

        except Exception as e:
            logger.warning(f"RAG retrieval failed: {e}")
            return []

    async def generate_collective_response(
        self,
        system_prompt: str,
        conversation_history: List[Dict[str, str]],
        user_message: str,
        approaches: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Generate collective agent response using LLM Router

        Uses ai-foundation LLM Router for:
        - Automatic model selection
        - Built-in retry logic
        - Metrics tracking

        Args:
            system_prompt: Agent system prompt with privacy instructions
            conversation_history: Previous messages
            user_message: Current user question
            approaches: Anonymized approaches from source orgs
            temperature: Sampling temperature
            max_tokens: Maximum response tokens

        Returns:
            {
                'message': str,
                'confidence': float,
                'model_used': str
            }
        """

        if not self.llm:
            logger.error("LLM Router not initialized")
            return {
                'message': "I apologize, but I'm currently unable to generate responses.",
                'confidence': 0.0,
                'model_used': 'none'
            }

        #  STEP 1: Enrich context with RAG knowledge (optional enhancement)
        # This allows the agent to reference similar patterns from knowledge base

        enriched_context = system_prompt

        if self.rag and len(approaches) > 0:
            # Retrieve relevant patterns from RAG
            pattern_query = f"collective wisdom patterns for {user_message}"

            try:
                patterns = await self.rag.retrieve(
                    query=pattern_query,
                    context={"task": "collective_response"},
                    top_k=3,
                    filters={"source_type": "collective_patterns"},
                    enable_reranking=True
                )

                if patterns:
                    pattern_context = self._format_patterns(patterns)
                    enriched_context += f"\n\n=== RELEVANT PATTERNS FROM KNOWLEDGE BASE ===\n{pattern_context}"

            except Exception as e:
                logger.warning(f"Pattern retrieval failed: {e}")

        #  STEP 2: Build message history
        messages = []

        for msg in conversation_history:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })

        messages.append({
            'role': 'user',
            'content': user_message
        })

        #  STEP 3: Generate response using LLM Router
        try:
            response_text = await self.llm.query(
                system_prompt=enriched_context,
                user_prompt=self._build_user_prompt(messages),
                task_type="content_generation",  # LLM Router will select best model
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Calculate confidence
            confidence = self._estimate_confidence(response_text, approaches)

            logger.info(f" Generated collective response: {len(response_text)} chars, confidence: {confidence}")

            return {
                'message': response_text,
                'confidence': confidence,
                'model_used': 'llm_router'
            }

        except Exception as e:
            logger.error(f" LLM generation failed: {e}")
            return {
                'message': "I apologize, but I encountered an error generating a response.",
                'confidence': 0.0,
                'model_used': 'error'
            }

    async def store_successful_pattern(
        self,
        problem_type: str,
        approaches: List[Dict],
        successful_conversation: List[Dict],
        outcome: str
    ):
        """
        Store successful collective pattern in RAG for future learning

        Allows the system to learn from successful collective agent interactions

        Args:
            problem_type: Type of problem solved
            approaches: Approaches that were synthesized
            successful_conversation: Full conversation that was helpful
            outcome: Outcome/resolution
        """

        if not self.rag:
            return

        # Format as learnable pattern
        pattern_text = f"""
        COLLECTIVE INTELLIGENCE PATTERN

        Problem Type: {problem_type}
        Number of Organizations: {len(approaches)}

        Successful Synthesis:
        {self._format_conversation(successful_conversation)}

        Outcome:
        {outcome}

        Key Success Factors:
        - Aggregated knowledge from {len(approaches)} organizations
        - Privacy-preserving collective wisdom
        - Actionable advice based on real experiences
        """

        try:
            await self.rag.ingest_documents(
                documents=[{
                    "text": pattern_text,
                    "metadata": {
                        "source_type": "collective_patterns",
                        "problem_type": problem_type,
                        "org_count": len(approaches),
                        "success": True,
                        "timestamp": str(datetime.now())
                    }
                }],
                source_type="collective_patterns"
            )

            logger.info(f" Stored successful collective pattern: {problem_type}")

        except Exception as e:
            logger.warning(f"Failed to store pattern in RAG: {e}")

    # ===== BACKWARD COMPATIBILITY =====

    async def generate(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Backward-compatible generate method

        For compatibility with existing collective_agent_service.py
        Returns just the message text (not full dict)
        """

        if not self.llm:
            return "I apologize, but I'm currently unable to generate responses."

        try:
            # Use LLM Router
            user_prompt = self._build_user_prompt(messages)

            response_text = await self.llm.query(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                task_type="content_generation",
                temperature=temperature,
                max_tokens=max_tokens
            )

            return response_text

        except Exception as e:
            logger.error(f" Generation failed: {e}")
            return "I apologize, but I encountered an error. Please try again."

    # ===== INTERNAL HELPERS =====

    def _format_patterns(self, patterns: List[Dict]) -> str:
        """Format RAG patterns for context"""

        if not patterns:
            return "No similar patterns found."

        formatted = []
        for i, pattern in enumerate(patterns, 1):
            formatted.append(f"""
            Pattern {i} (Relevance: {pattern.get('score', 0.0):.2f}):
            {pattern.get('content', '')}
            """)

        return "\n".join(formatted)

    def _build_user_prompt(self, messages: List[Dict]) -> str:
        """Build user prompt from conversation history"""

        # Format as conversation
        conversation = []
        for msg in messages:
            role = "User" if msg['role'] == 'user' else "Agent"
            conversation.append(f"{role}: {msg['content']}")

        return "\n\n".join(conversation)

    def _estimate_confidence(self, response: str, approaches: List[Dict]) -> float:
        """
        Estimate confidence from response and source approaches

        Higher confidence when:
        - More source organizations
        - Specific statistics mentioned
        - Definitive language
        - Response length appropriate
        """

        base_confidence = 0.7

        # More orgs = higher confidence
        org_count = len(approaches)
        if org_count >= 7:
            base_confidence += 0.15
        elif org_count >= 5:
            base_confidence += 0.10
        elif org_count < 5:
            base_confidence -= 0.20

        # Check response characteristics
        response_lower = response.lower()

        # High confidence indicators
        high_conf_phrases = [
            'organizations typically',
            'most organizations',
            'out of',
            'the common pattern',
            'successfully addressed'
        ]

        for phrase in high_conf_phrases:
            if phrase in response_lower:
                base_confidence += 0.05

        # Low confidence indicators
        low_conf_phrases = [
            'might',
            'possibly',
            'unclear',
            'difficult to say',
            'varies significantly'
        ]

        for phrase in low_conf_phrases:
            if phrase in response_lower:
                base_confidence -= 0.10

        # Response length
        if len(response) < 100:
            base_confidence -= 0.15
        elif len(response) > 500:
            base_confidence += 0.05

        # Cap at 0.3 - 1.0
        return max(0.3, min(1.0, round(base_confidence, 2)))

    def _format_conversation(self, messages: List[Dict]) -> str:
        """Format conversation for storage"""

        formatted = []
        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            formatted.append(f"{role.upper()}: {content}")

        return "\n\n".join(formatted)


# Singleton instance
_ai_foundation = None

async def get_collective_ai_foundation() -> CollectiveAIFoundation:
    """Get or create CollectiveAIFoundation singleton"""

    global _ai_foundation

    if _ai_foundation is None:
        _ai_foundation = CollectiveAIFoundation()
        await _ai_foundation.initialize()

    return _ai_foundation
