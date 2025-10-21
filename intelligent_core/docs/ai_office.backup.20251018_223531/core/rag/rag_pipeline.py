"""
RAG Pipeline

Complete Retrieval-Augmented Generation pipeline that:
1. Analyzes intent
2. Retrieves context from BCM modules
3. Builds enhanced prompt
4. Calls Claude API
5. Returns answer + actions
"""

import logging
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from core.adapters import AnthropicAdapter
from core.intent import IntentAnalyzer, IntentResult
from core.rag.context_retriever import ContextRetriever, RetrievedContext

logger = logging.getLogger(__name__)


class RAGResult(BaseModel):
    """Result from RAG pipeline"""
    answer: str
    confidence: float
    intent: Dict[str, Any]
    context_used: List[Dict[str, Any]]
    suggested_actions: List[Dict[str, Any]]
    model_used: str
    tokens_used: int


class RAGPipeline:
    """
    Complete RAG pipeline for BCM Intelligence.

    Workflow:
    User Query → Intent Analysis → Context Retrieval → Prompt Building → Claude API → Answer
    """

    def __init__(
        self,
        bcm_module_urls: Dict[str, str],
        anthropic_api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
        max_context_items: int = 10,
        retrieval_timeout: int = 10
    ):
        """
        Initialize RAG pipeline.

        Args:
            bcm_module_urls: Dict of module_name -> base_url
            anthropic_api_key: Anthropic API key
            model: Claude model to use
            max_context_items: Max context items to retrieve
            retrieval_timeout: Timeout for context retrieval
        """
        # Initialize components
        self.claude = AnthropicAdapter(
            api_key=anthropic_api_key,
            model=model
        )
        self.intent_analyzer = IntentAnalyzer()
        self.context_retriever = ContextRetriever(
            module_urls=bcm_module_urls,
            timeout=retrieval_timeout,
            max_items_per_module=max_context_items // 2  # Split across modules
        )

        self.max_context_items = max_context_items

        logger.info("RAG Pipeline initialized")

    async def process_query(
        self,
        query: str,
        tenant_id: str = "demo",
        conversation_history: Optional[List[Dict]] = None,
        system_prompt: Optional[str] = None
    ) -> RAGResult:
        """
        Process user query through complete RAG pipeline.

        Args:
            query: User's question or request
            tenant_id: Tenant identifier
            conversation_history: Previous messages
            system_prompt: Optional system prompt override

        Returns:
            RAGResult with answer and metadata
        """
        logger.info(f"Processing query: {query[:100]}...")

        # Step 1: Analyze intent
        intent_result = self.intent_analyzer.analyze(query, conversation_history)
        logger.info(f"Intent detected: {intent_result.intent_type} (confidence: {intent_result.confidence})")

        # Step 2: Retrieve context (if needed)
        retrieved_contexts = []
        if intent_result.requires_context:
            # Determine which modules to query
            target_modules = self._determine_target_modules(intent_result)

            logger.info(f"Retrieving context from modules: {target_modules}")
            retrieved_contexts = await self.context_retriever.retrieve(
                query=query,
                target_modules=target_modules,
                intent=intent_result.dict(),
                tenant_id=tenant_id,
                entities=intent_result.entities
            )
            logger.info(f"Retrieved {len(retrieved_contexts)} context items")

        # Step 3: Build prompt with context
        enhanced_prompt = self._build_prompt(
            query=query,
            intent=intent_result,
            contexts=retrieved_contexts
        )

        # Step 4: Generate response with Claude
        if not system_prompt:
            system_prompt = self._build_system_prompt(intent_result)

        claude_response = await self.claude.generate(
            user_message=enhanced_prompt,
            system_prompt=system_prompt
        )

        # Step 5: Extract suggested actions from response
        suggested_actions = self._extract_actions(
            claude_response['content'],
            intent_result
        )

        # Step 6: Build result
        return RAGResult(
            answer=claude_response['content'],
            confidence=intent_result.confidence,
            intent=intent_result.dict(),
            context_used=[
                {
                    "module": ctx.module,
                    "items_count": len(ctx.data),
                    "score": ctx.score
                }
                for ctx in retrieved_contexts
            ],
            suggested_actions=suggested_actions,
            model_used=claude_response['model_used'],
            tokens_used=claude_response['tokens_used']
        )

    def _determine_target_modules(self, intent: IntentResult) -> List[str]:
        """
        Determine which BCM modules to query based on intent.

        Args:
            intent: Intent analysis result

        Returns:
            List of module names to query
        """
        # If module explicitly detected, use it
        if intent.module != "general":
            return [intent.module]

        # Otherwise, use intent-based routing
        intent_type = intent.intent_type

        module_map = {
            "analyze_risk": ["risk", "bia"],
            "analyze_bia": ["bia", "risk"],
            "assess_compliance": ["compliance", "governance"],
            "create_plan": ["plans", "planning", "bia"],
            "design_exercise": ["validation", "plans"],
            "query_info": ["governance", "compliance"],  # General info
            "get_status": ["governance"],
            "list_items": [intent.module] if intent.module != "general" else ["risk", "plans"],
        }

        # Get modules for this intent type
        modules = module_map.get(intent_type, [])

        # If still no modules, query general ones
        if not modules:
            modules = ["governance", "compliance"]

        return modules

    def _build_prompt(
        self,
        query: str,
        intent: IntentResult,
        contexts: List[RetrievedContext]
    ) -> str:
        """
        Build enhanced prompt with retrieved context.

        Args:
            query: Original query
            intent: Intent analysis
            contexts: Retrieved contexts

        Returns:
            Enhanced prompt string
        """
        parts = []

        # Add context if available
        if contexts:
            parts.append("**Relevant BCM Data:**\n")

            for ctx in contexts[:self.max_context_items]:
                parts.append(f"**From {ctx.module.upper()} module:**")

                for item in ctx.data:
                    # Format item based on module
                    formatted = self._format_context_item(item, ctx.module)
                    parts.append(formatted)

                parts.append("")  # Blank line

        # Add entities if extracted
        if intent.entities:
            parts.append(f"**Extracted Entities:** {intent.entities}\n")

        # Add user query
        parts.append("**User Query:**")
        parts.append(query)

        return "\n".join(parts)

    def _format_context_item(self, item: Dict[str, Any], module: str) -> str:
        """
        Format context item for prompt.

        Args:
            item: Data item from module
            module: Module name

        Returns:
            Formatted string
        """
        # Risk module
        if module == "risk":
            return (
                f"- Risk: {item.get('title', 'N/A')} "
                f"(Priority: {item.get('priority', 'N/A')}, "
                f"Likelihood: {item.get('likelihood', 'N/A')}, "
                f"Impact: {item.get('impact', 'N/A')})"
            )

        # BIA module
        elif module == "bia":
            return (
                f"- Process: {item.get('name', 'N/A')} "
                f"(RTO: {item.get('rto', 'N/A')}, "
                f"RPO: {item.get('rpo', 'N/A')}, "
                f"Criticality: {item.get('criticality', 'N/A')})"
            )

        # Plans module
        elif module == "plans":
            return (
                f"- Plan: {item.get('name', 'N/A')} "
                f"(Status: {item.get('status', 'N/A')}, "
                f"Type: {item.get('type', 'N/A')})"
            )

        # Compliance module
        elif module == "compliance":
            return (
                f"- Requirement: {item.get('requirement', 'N/A')} "
                f"(Status: {item.get('status', 'N/A')}, "
                f"Gap: {item.get('gap_description', 'N/A')})"
            )

        # Response module
        elif module == "response":
            return (
                f"- Incident: {item.get('title', 'N/A')} "
                f"(Severity: {item.get('severity', 'N/A')}, "
                f"Status: {item.get('status', 'N/A')})"
            )

        # Default format
        else:
            # Try to extract key fields
            title = item.get('title') or item.get('name') or item.get('id', 'Item')
            description = item.get('description', '')[:100]
            return f"- {title}: {description}"

    def _build_system_prompt(self, intent: IntentResult) -> str:
        """
        Build system prompt based on intent.

        Args:
            intent: Intent analysis

        Returns:
            System prompt string
        """
        base_prompt = (
            "You are an expert BCM (Business Continuity Management) consultant "
            "with deep knowledge of ISO 22301:2019 standard. "
            "You help organizations build resilience and ensure business continuity.\n\n"
        )

        # Add intent-specific instructions
        intent_type = intent.intent_type

        if "analyze" in intent_type:
            base_prompt += (
                "Provide thorough analysis with:\n"
                "- Clear findings based on provided data\n"
                "- Risk assessment using FAIR methodology where applicable\n"
                "- Specific recommendations\n"
                "- Next steps\n\n"
            )

        elif "create" in intent_type or "generate" in intent_type:
            base_prompt += (
                "When generating plans or documents:\n"
                "- Follow ISO 22301:2019 requirements\n"
                "- Use provided context data\n"
                "- Include specific, actionable steps\n"
                "- Reference relevant standards\n\n"
            )

        elif "recommend" in intent_type or "suggest" in intent_type:
            base_prompt += (
                "Provide recommendations that are:\n"
                "- Specific and actionable\n"
                "- Based on best practices\n"
                "- Prioritized by impact\n"
                "- Aligned with ISO 22301\n\n"
            )

        # General guidelines
        base_prompt += (
            "Guidelines:\n"
            "- Use clear, professional language\n"
            "- Reference specific data from context when available\n"
            "- Be concise but comprehensive\n"
            "- Suggest concrete next actions\n"
            "- Format responses with markdown for readability"
        )

        return base_prompt

    def _extract_actions(
        self,
        response_text: str,
        intent: IntentResult
    ) -> List[Dict[str, Any]]:
        """
        Extract suggested actions from Claude's response.

        Args:
            response_text: Claude's response
            intent: Intent analysis

        Returns:
            List of suggested actions
        """
        actions = []

        # Simple extraction - look for numbered lists or bullet points
        # In future, could use more sophisticated NLP or structured output

        lines = response_text.split('\n')

        for line in lines:
            line = line.strip()

            # Check for action indicators
            if any(indicator in line.lower() for indicator in [
                'next step', 'recommend', 'should', 'action', 'task'
            ]):
                # Extract action
                # Remove numbering/bullets
                action_text = line.lstrip('0123456789.-*• ')

                if len(action_text) > 10:  # Valid action
                    actions.append({
                        "title": action_text[:100],
                        "description": action_text,
                        "priority": "medium",
                        "type": intent.intent_type
                    })

        # Limit to top 5 actions
        return actions[:5]
