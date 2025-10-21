"""
LLM Router

Routes LLM queries to best available provider with async support
"""

import os
import sys
import logging
from typing import Optional, Dict, Any
from enum import Enum

# Add VaultClient to path
sys.path.insert(0, '/Users/MD/AI-Platform-ISO/infrastructure/security/secrets-management')

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Available LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class LLMRouter:
    """
    Routes LLM queries to available providers with task-specific routing

    Task Routing:
    - strategic_analysis: Claude Opus (complex reasoning)
    - content_generation: Claude Sonnet (balanced)
    - quick_tasks: Claude Haiku or GPT-3.5 (fast)
    - embeddings: OpenAI text-embedding-3-large

    Priority:
    1. Anthropic Claude (if API key available)
    2. OpenAI GPT (if API key available)
    3. Ollama (local fallback)
    """

    def __init__(self):
        # Load API keys from Vault (fallback to env vars for backwards compatibility)
        try:
            from vault_client import get_secret
            try:
                self.anthropic_key = get_secret("anthropic-api-key")
                logger.info(" Loaded ANTHROPIC_API_KEY from Vault")
            except:
                self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
                if self.anthropic_key:
                    logger.warning("️  Using ANTHROPIC_API_KEY from .env (migrate to Vault)")
        except ImportError:
            self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            logger.warning("️  VaultClient not available, using .env")

        self.openai_key = os.getenv("OPENAI_API_KEY")

        self.anthropic_client = None
        self.openai_client = None

        self._initialize_clients()

        logger.info(f"LLM Router initialized - Anthropic: {bool(self.anthropic_client)}, OpenAI: {bool(self.openai_client)}")

    def _initialize_clients(self):
        """Initialize all available LLM clients"""

        # Initialize Anthropic if key available
        if self.anthropic_key:
            try:
                from anthropic import AsyncAnthropic
                self.anthropic_client = AsyncAnthropic(api_key=self.anthropic_key)
                logger.info("Anthropic client initialized")
            except ImportError:
                logger.warning("anthropic package not installed. Install with: pip install anthropic")

        # Initialize OpenAI if key available
        if self.openai_key:
            try:
                from openai import AsyncOpenAI
                self.openai_client = AsyncOpenAI(api_key=self.openai_key)
                logger.info("OpenAI client initialized")
            except ImportError:
                logger.warning("openai package not installed. Install with: pip install openai")

    def _select_model(self, task_type: str = "general") -> tuple[str, Any]:
        """
        Select best model for task type

        Returns: (model_name, client)
        """

        # Strategic analysis: Claude Opus (most powerful)
        if task_type == "strategic_analysis":
            if self.anthropic_client:
                return ("claude-opus-4-20250514", self.anthropic_client)
            elif self.openai_client:
                return ("gpt-4-turbo-preview", self.openai_client)

        # Content generation: Claude Sonnet (balanced)
        elif task_type == "content_generation":
            if self.anthropic_client:
                return ("claude-3-5-sonnet-20241022", self.anthropic_client)
            elif self.openai_client:
                return ("gpt-4-turbo-preview", self.openai_client)

        # Quick tasks: Claude Haiku (fast)
        elif task_type == "quick_tasks":
            if self.anthropic_client:
                return ("claude-3-5-haiku-20241022", self.anthropic_client)
            elif self.openai_client:
                return ("gpt-3.5-turbo", self.openai_client)

        # Default: Best available
        else:
            if self.anthropic_client:
                return ("claude-3-5-sonnet-20241022", self.anthropic_client)
            elif self.openai_client:
                return ("gpt-4-turbo-preview", self.openai_client)

        raise RuntimeError("No LLM provider available. Set ANTHROPIC_API_KEY or OPENAI_API_KEY")

    async def query(
        self,
        system_prompt: str,
        user_prompt: str,
        task_type: str = "general",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Query LLM with automatic model selection

        Args:
            system_prompt: System instruction
            user_prompt: User query
            task_type: Type of task (strategic_analysis, content_generation, quick_tasks, general)
            temperature: Creativity (0.0-1.0)
            max_tokens: Maximum response length

        Returns:
            LLM response text
        """

        try:
            model_name, client = self._select_model(task_type)

            if isinstance(client, type(self.anthropic_client)):
                return await self._query_anthropic(model_name, system_prompt, user_prompt, temperature, max_tokens)
            else:
                return await self._query_openai(model_name, system_prompt, user_prompt, temperature, max_tokens)
        except Exception as e:
            logger.error(f"LLM query failed: {e}")
            return f"[ERROR] LLM query failed: {str(e)}"

    async def _query_anthropic(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Query Anthropic Claude"""

        response = await self.anthropic_client.messages.create(
            model=model,
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
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Query OpenAI GPT"""

        response = await self.openai_client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        return response.choices[0].message.content

    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings using OpenAI

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """

        if not self.openai_client:
            raise RuntimeError("OpenAI client required for embeddings. Set OPENAI_API_KEY")

        response = await self.openai_client.embeddings.create(
            model="text-embedding-3-large",
            input=texts
        )

        return [item.embedding for item in response.data]

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about available LLM providers"""
        return {
            "anthropic": {
                "available": self.anthropic_client is not None,
                "models": ["claude-opus-4-20250514", "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"]
            },
            "openai": {
                "available": self.openai_client is not None,
                "models": ["gpt-4-turbo-preview", "gpt-3.5-turbo", "text-embedding-3-large"]
            }
        }
