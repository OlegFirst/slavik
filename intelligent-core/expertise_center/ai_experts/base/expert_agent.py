"""
Base Expert Agent Class

Foundation for all AI specialists (BCM Advisor, Compliance Auditor, Strategic Planner).
Uses Claude Sonnet 4 with RAG + Tools for specialization.
"""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import anthropic
import os

class ExpertAgent(ABC):
    """
    Base class для AI экспертов

    Специализация через:
    - System prompt (роль эксперта)
    - RAG context (релевантные знания)
    - Tools (специфичные возможности)

    Example:
        >>> advisor = BCMAdvisor(case_library, knowledge_graph)
        >>> response = await advisor.advise("How to identify critical processes?", context)
    """

    def __init__(
        self,
        name: str,
        role_description: str,
        knowledge_sources: list,
        tools: list,
        temperature: float = 0.3
    ):
        """
        Initialize expert agent

        Args:
            name: Expert name (e.g., "BCM Advisor")
            role_description: Role description
            knowledge_sources: List of knowledge sources for RAG
            tools: List of BaseTool instances
            temperature: LLM temperature (0.2-0.4 for experts)
        """
        self.name = name
        self.role = role_description
        self.temperature = temperature

        # RAG Pipeline
        try:
            from ..rag.pipeline import RAGPipeline
            self.rag_pipeline = RAGPipeline(knowledge_sources)
        except ImportError:
            self.rag_pipeline = None

        # Tools
        self.tools = {tool.name: tool for tool in tools}

        # LLM Client (Anthropic Claude)
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if api_key:
            self.llm = anthropic.AsyncAnthropic(api_key=api_key)
        else:
            self.llm = None  # Mock for development

    async def advise(
        self,
        query: str,
        context: Dict[str, Any],
        max_tokens: int = 2000
    ) -> str:
        """
        Main advisory method

        Flow:
        1. Retrieve relevant knowledge (RAG)
        2. Build specialized prompt
        3. Generate response with tools
        4. Execute tool calls if needed

        Args:
            query: User question
            context: Workflow context
            max_tokens: Max response tokens

        Returns:
            Expert advice as string
        """

        # 1. RAG retrieval
        relevant_knowledge = []
        if self.rag_pipeline:
            relevant_knowledge = await self.rag_pipeline.retrieve(
                query=query,
                context=context,
                top_k=5
            )

        # 2. Build prompt
        prompt = self._build_prompt(
            query=query,
            context=context,
            knowledge=relevant_knowledge
        )

        # 3. Generate with tools
        if not self.llm:
            # Mock response for development
            return f"[Mock Response from {self.name}] {query}"

        response = await self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            temperature=self.temperature,
            system=self._system_prompt(),
            messages=[
                {"role": "user", "content": prompt}
            ],
            tools=[t.to_anthropic_tool() for t in self.tools.values()] if self.tools else []
        )

        # 4. Execute tool calls if any
        if response.stop_reason == "tool_use":
            tool_results = await self._execute_tools(response.content)

            # Continue conversation with tool results
            final_response = await self._continue_with_tools(
                response,
                tool_results,
                max_tokens
            )
            return final_response

        # Extract text from response
        text_blocks = [block.text for block in response.content if hasattr(block, 'text')]
        return '\n'.join(text_blocks)

    def _system_prompt(self) -> str:
        """System prompt defining expert personality"""
        return f"""You are {self.name}, a {self.role}.

Your expertise:
- Deep knowledge of ISO 22301, BCI Good Practice Guidelines
- 15+ years BCM consulting experience
- Specialized in {self._specialization()}

Your style:
- Practical, actionable advice
- Reference standards by clause number (e.g., "ISO 22301:2019 Clause 8.2.2")
- Use examples from real cases when available
- Be encouraging but honest about challenges
- Explain complex concepts in simple terms

Your limitations:
- You don't make decisions for users (you suggest options)
- You provide trade-offs for different approaches
- You acknowledge uncertainty when appropriate
- You recommend human expert when beyond your scope

Always structure your advice with:
1. Direct answer to the question
2. Supporting reasoning
3. Practical next steps
4. References (standards, similar cases)
"""

    @abstractmethod
    def _specialization(self) -> str:
        """Override in subclasses to define specialization"""
        return "business continuity management"

    def _build_prompt(
        self,
        query: str,
        context: Dict[str, Any],
        knowledge: List[Dict[str, Any]]
    ) -> str:
        """Build user prompt with context and RAG knowledge"""

        prompt = f"""**User Question:**
{query}

**Workflow Context:**
- Organization: {context.get('industry', 'Unknown')} industry, {context.get('size', 'Unknown')} size
- Current Module: {context.get('module', 'Unknown')}
- Current Stage: {context.get('current_stage', 'Unknown')}
- Progress: {context.get('progress', 'Unknown')}%
"""

        if knowledge:
            prompt += "\n**Relevant Knowledge:**\n"
            for i, item in enumerate(knowledge[:5], 1):
                source = item.get('source', 'Unknown')
                content = item.get('content', '')[:300]  # Truncate

                prompt += f"\n{i}. Source: {source}\n{content}...\n"

        prompt += "\nProvide your expert advice:"

        return prompt

    async def _execute_tools(self, content: list) -> List[Dict[str, Any]]:
        """Execute tool calls from LLM response"""

        tool_results = []

        for block in content:
            if hasattr(block, 'type') and block.type == 'tool_use':
                tool_name = block.name
                tool_input = block.input

                if tool_name in self.tools:
                    try:
                        result = await self.tools[tool_name].execute(**tool_input)
                        tool_results.append({
                            'tool_use_id': block.id,
                            'content': str(result)
                        })
                    except Exception as e:
                        tool_results.append({
                            'tool_use_id': block.id,
                            'content': f"Error: {str(e)}",
                            'is_error': True
                        })

        return tool_results

    async def _continue_with_tools(
        self,
        previous_response,
        tool_results: List[Dict[str, Any]],
        max_tokens: int
    ) -> str:
        """Continue conversation with tool results"""

        if not self.llm:
            return f"[Mock] Tool results processed: {len(tool_results)} tools executed"

        # Build message history
        messages = [
            {"role": "user", "content": ""},  # Original query (simplified)
            {"role": "assistant", "content": previous_response.content},
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": result['tool_use_id'],
                        "content": result['content']
                    }
                    for result in tool_results
                ]
            }
        ]

        # Continue conversation
        final_response = await self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            temperature=self.temperature,
            system=self._system_prompt(),
            messages=messages
        )

        # Extract text
        text_blocks = [block.text for block in final_response.content if hasattr(block, 'text')]
        return '\n'.join(text_blocks)
