"""
LLM Router
Routes requests to available LLM providers (Anthropic Claude, OpenAI GPT)
"""
from typing import Dict, List, Optional, Any
import os
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI


class LLMRouter:
    """
    Routes LLM requests to available providers

    Priority:
    1. Anthropic Claude (claude-3-5-sonnet-20241022)
    2. OpenAI GPT (gpt-4-turbo-preview)
    3. Fallback: local/mock
    """

    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize available LLM clients"""
        # Anthropic
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            self.anthropic_client = AsyncAnthropic(api_key=anthropic_key)

        # OpenAI
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self.openai_client = AsyncOpenAI(api_key=openai_key)

    async def generate(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate text using available LLM

        Args:
            system: System prompt
            user: User prompt
            temperature: Sampling temperature
            max_tokens: Max response tokens

        Returns:
            Generated text
        """
        # Try Anthropic first
        if self.anthropic_client:
            try:
                return await self._generate_anthropic(
                    system, user, temperature, max_tokens
                )
            except Exception as e:
                print(f"Anthropic error: {e}, falling back to OpenAI")

        # Try OpenAI
        if self.openai_client:
            try:
                return await self._generate_openai(
                    system, user, temperature, max_tokens
                )
            except Exception as e:
                print(f"OpenAI error: {e}")
                raise

        raise ValueError("No LLM providers available")

    async def _generate_anthropic(
        self,
        system: str,
        user: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate using Anthropic Claude"""
        response = await self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[
                {"role": "user", "content": user}
            ]
        )

        return response.content[0].text

    async def _generate_openai(
        self,
        system: str,
        user: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate using OpenAI GPT"""
        response = await self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ]
        )

        return response.choices[0].message.content

    async def generate_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate with tool calling support

        Args:
            messages: Conversation messages
            tools: Tool definitions
            temperature: Sampling temperature

        Returns:
            Response with tool calls
        """
        # Try Anthropic first (supports tools)
        if self.anthropic_client:
            try:
                response = await self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4000,
                    temperature=temperature,
                    messages=messages,
                    tools=tools
                )

                # Extract tool calls
                tool_calls = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_calls.append({
                            'id': block.id,
                            'name': block.name,
                            'input': block.input
                        })

                return {
                    'content': response.content,
                    'tool_calls': tool_calls,
                    'stop_reason': response.stop_reason
                }
            except Exception as e:
                print(f"Anthropic tool calling error: {e}")

        # OpenAI fallback
        if self.openai_client:
            # Convert to OpenAI format
            openai_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool["input_schema"]
                    }
                }
                for tool in tools
            ]

            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                tools=openai_tools,
                temperature=temperature
            )

            tool_calls = []
            if response.choices[0].message.tool_calls:
                for tc in response.choices[0].message.tool_calls:
                    tool_calls.append({
                        'id': tc.id,
                        'name': tc.function.name,
                        'input': tc.function.arguments
                    })

            return {
                'content': response.choices[0].message.content,
                'tool_calls': tool_calls,
                'stop_reason': response.choices[0].finish_reason
            }

        raise ValueError("No LLM providers available for tool calling")

    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        providers = []
        if self.anthropic_client:
            providers.append('anthropic')
        if self.openai_client:
            providers.append('openai')
        return providers

    async def health_check(self) -> Dict[str, bool]:
        """Check health of LLM providers"""
        health = {}

        # Anthropic
        if self.anthropic_client:
            try:
                await self._generate_anthropic(
                    system="You are a helpful assistant",
                    user="Hi",
                    temperature=0.7,
                    max_tokens=10
                )
                health['anthropic'] = True
            except Exception:
                health['anthropic'] = False

        # OpenAI
        if self.openai_client:
            try:
                await self._generate_openai(
                    system="You are a helpful assistant",
                    user="Hi",
                    temperature=0.7,
                    max_tokens=10
                )
                health['openai'] = True
            except Exception:
                health['openai'] = False

        return health
