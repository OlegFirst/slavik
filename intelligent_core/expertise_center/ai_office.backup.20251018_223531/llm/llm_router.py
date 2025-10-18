"""
LLM Router

Routes LLM queries to best available provider
"""

import os
import logging
from typing import Optional
from enum import Enum


logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Available LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class LLMRouter:
    """
    Routes LLM queries to available providers

    Priority:
    1. Anthropic Claude (if API key available)
    2. OpenAI GPT (if API key available)
    3. Ollama (local fallback)
    """

    def __init__(self):
        self.provider = self._detect_provider()
        self.client = self._initialize_client()

        logger.info(f"LLM Router initialized with provider: {self.provider}")

    def _detect_provider(self) -> LLMProvider:
        """Detect which LLM provider to use"""

        # Check for Anthropic API key
        if os.getenv("ANTHROPIC_API_KEY"):
            return LLMProvider.ANTHROPIC

        # Check for OpenAI API key
        if os.getenv("OPENAI_API_KEY"):
            return LLMProvider.OPENAI

        # Default to Ollama (local)
        return LLMProvider.OLLAMA

    def _initialize_client(self):
        """Initialize LLM client based on provider"""

        if self.provider == LLMProvider.ANTHROPIC:
            try:
                import anthropic
                return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            except ImportError:
                logger.warning("Anthropic package not installed. Falling back to OpenAI.")
                self.provider = LLMProvider.OPENAI

        if self.provider == LLMProvider.OPENAI:
            try:
                import openai
                openai.api_key = os.getenv("OPENAI_API_KEY")
                return openai
            except ImportError:
                logger.warning("OpenAI package not installed. Falling back to Ollama.")
                self.provider = LLMProvider.OLLAMA

        if self.provider == LLMProvider.OLLAMA:
            try:
                import httpx
                return httpx.AsyncClient(base_url="http://localhost:11434")
            except ImportError:
                logger.error("httpx not available for Ollama. LLM queries will fail.")
                return None

        return None

    async def query(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Query LLM with system and user prompts

        Args:
            system_prompt: System instruction
            user_prompt: User query
            temperature: Creativity (0.0-1.0)
            max_tokens: Maximum response length

        Returns:
            LLM response text
        """

        if not self.client:
            return "[ERROR] No LLM provider available"

        try:
            if self.provider == LLMProvider.ANTHROPIC:
                return await self._query_anthropic(system_prompt, user_prompt, temperature, max_tokens)
            elif self.provider == LLMProvider.OPENAI:
                return await self._query_openai(system_prompt, user_prompt, temperature, max_tokens)
            elif self.provider == LLMProvider.OLLAMA:
                return await self._query_ollama(system_prompt, user_prompt, temperature, max_tokens)
        except Exception as e:
            logger.error(f"LLM query failed: {e}")
            return f"[ERROR] LLM query failed: {str(e)}"

    async def _query_anthropic(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Query Anthropic Claude"""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",  # Latest Claude model
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        return response.content[0].text

    async def _query_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Query OpenAI GPT"""

        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",  # Latest GPT-4 model
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        return response.choices[0].message.content

    async def _query_ollama(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Query Ollama (local LLM)"""

        # Combine system and user prompts for Ollama
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        response = await self.client.post(
            "/api/generate",
            json={
                "model": "llama3.2",  # Default Ollama model
                "prompt": full_prompt,
                "temperature": temperature,
                "stream": False
            },
            timeout=60.0
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("response", "[ERROR] Empty response from Ollama")
        else:
            return f"[ERROR] Ollama returned status {response.status_code}"

    def get_provider_info(self) -> dict:
        """Get information about current LLM provider"""
        return {
            "provider": self.provider.value,
            "available": self.client is not None,
            "model": self._get_model_name()
        }

    def _get_model_name(self) -> str:
        """Get model name based on provider"""
        if self.provider == LLMProvider.ANTHROPIC:
            return "claude-3-5-sonnet-20241022"
        elif self.provider == LLMProvider.OPENAI:
            return "gpt-4-turbo-preview"
        elif self.provider == LLMProvider.OLLAMA:
            return "llama3.2"
        return "unknown"
