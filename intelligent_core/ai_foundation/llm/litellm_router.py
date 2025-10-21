"""
LiteLLM Router - Production-Ready Multi-LLM Orchestration
==========================================================

Features:
- Automatic fallbacks (Claude → GPT → Local)
- Load balancing
- Cost optimization
- Rate limit handling
- Caching
- Streaming support
"""
import os
import logging
from typing import Dict, Any, List, Optional, AsyncIterator
from datetime import datetime
import litellm
from litellm import Router
from litellm.caching import Cache

logger = logging.getLogger(__name__)

# Enable LiteLLM logging
litellm.set_verbose = True


class LiteLLMRouter:
    """
    Production LLM Router with fallbacks and optimization

    Usage:
        router = LiteLLMRouter()
        response = await router.complete(
            messages=[{"role": "user", "content": "Hello"}],
            task_type="analysis"  # or "generation", "chat", "embedding"
        )
    """

    def __init__(self):
        """Initialize router with model configurations"""

        # Model configurations by tier
        self.model_configs = self._build_model_configs()

        # Initialize router
        self.router = Router(
            model_list=self.model_configs,

            # Fallback strategy
            fallbacks=[
                # Tier 1 (Premium): Claude Opus, GPT-4
                {"claude-3-opus": ["gpt-4-turbo", "gpt-4"]},
                {"gpt-4-turbo": ["claude-3-opus", "gpt-4"]},

                # Tier 2 (Standard): Claude Sonnet, GPT-3.5
                {"claude-3-sonnet": ["gpt-3.5-turbo", "claude-3-haiku"]},
                {"gpt-3.5-turbo": ["claude-3-sonnet"]},

                # Tier 3 (Fast): Claude Haiku, Local
                {"claude-3-haiku": ["gpt-3.5-turbo", "local-model"]},
            ],

            # Retry settings
            num_retries=3,
            timeout=120,  # 2 minutes

            # Load balancing
            routing_strategy="least-busy",  # or "simple-shuffle", "latency-based-routing"

            # Redis cache (optional)
            cache_responses=True,
            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", 6379)),
            cache_kwargs={
                "ttl": 3600,  # 1 hour cache
                "namespace": "litellm_cache"
            }
        )

        # Task-to-model mapping
        self.task_model_mapping = {
            "analysis": "claude-3-opus",      # Deep analysis
            "generation": "claude-3-sonnet",  # Content generation
            "chat": "claude-3-sonnet",        # Interactive chat
            "quick": "claude-3-haiku",        # Fast responses
            "embedding": "text-embedding-3",  # Embeddings
            "cheap": "gpt-3.5-turbo",         # Cost-optimized
        }

        logger.info(" LiteLLM Router initialized with fallbacks")

    def _build_model_configs(self) -> List[Dict]:
        """Build model configurations from environment"""

        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        configs = []

        # Claude models
        if anthropic_key:
            configs.extend([
                {
                    "model_name": "claude-3-opus",
                    "litellm_params": {
                        "model": "claude-3-opus-20240229",
                        "api_key": anthropic_key,
                        "max_tokens": 4096,
                        "temperature": 0.7,
                    },
                    "model_info": {
                        "tier": "premium",
                        "cost_per_token": 0.000015,
                        "max_input_tokens": 200000,
                        "supports_streaming": True,
                    }
                },
                {
                    "model_name": "claude-3-sonnet",
                    "litellm_params": {
                        "model": "claude-3-sonnet-20240229",
                        "api_key": anthropic_key,
                        "max_tokens": 4096,
                        "temperature": 0.7,
                    },
                    "model_info": {
                        "tier": "standard",
                        "cost_per_token": 0.000003,
                        "max_input_tokens": 200000,
                        "supports_streaming": True,
                    }
                },
                {
                    "model_name": "claude-3-haiku",
                    "litellm_params": {
                        "model": "claude-3-haiku-20240307",
                        "api_key": anthropic_key,
                        "max_tokens": 4096,
                        "temperature": 0.7,
                    },
                    "model_info": {
                        "tier": "fast",
                        "cost_per_token": 0.00000025,
                        "max_input_tokens": 200000,
                        "supports_streaming": True,
                    }
                },
            ])

        # OpenAI models
        if openai_key:
            configs.extend([
                {
                    "model_name": "gpt-4-turbo",
                    "litellm_params": {
                        "model": "gpt-4-turbo-preview",
                        "api_key": openai_key,
                        "max_tokens": 4096,
                        "temperature": 0.7,
                    },
                    "model_info": {
                        "tier": "premium",
                        "cost_per_token": 0.00001,
                        "max_input_tokens": 128000,
                    }
                },
                {
                    "model_name": "gpt-3.5-turbo",
                    "litellm_params": {
                        "model": "gpt-3.5-turbo",
                        "api_key": openai_key,
                        "max_tokens": 4096,
                        "temperature": 0.7,
                    },
                    "model_info": {
                        "tier": "standard",
                        "cost_per_token": 0.0000005,
                        "max_input_tokens": 16000,
                    }
                },
            ])

        return configs

    async def complete(
        self,
        messages: List[Dict[str, str]],
        task_type: str = "analysis",
        model: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Complete chat with automatic fallbacks

        Args:
            messages: Chat messages
            task_type: Type of task (determines model selection)
            model: Override model selection
            stream: Enable streaming
            **kwargs: Additional litellm parameters

        Returns:
            Response dict with content, model used, cost, etc.
        """

        # Select model based on task type
        if not model:
            model = self.task_model_mapping.get(task_type, "claude-3-sonnet")

        logger.info(f" LLM Request: {task_type} → {model}")

        start_time = datetime.utcnow()

        try:
            if stream:
                return self._complete_streaming(messages, model, **kwargs)
            else:
                response = await self.router.acompletion(
                    model=model,
                    messages=messages,
                    **kwargs
                )

                end_time = datetime.utcnow()
                latency = (end_time - start_time).total_seconds()

                # Extract response
                content = response.choices[0].message.content
                model_used = response.model

                # Calculate cost
                usage = response.usage
                cost = self._calculate_cost(model_used, usage.total_tokens)

                logger.info(f" LLM Response: {model_used} | {latency:.2f}s | ${cost:.4f}")

                return {
                    "content": content,
                    "model": model_used,
                    "usage": {
                        "prompt_tokens": usage.prompt_tokens,
                        "completion_tokens": usage.completion_tokens,
                        "total_tokens": usage.total_tokens,
                    },
                    "cost": cost,
                    "latency": latency,
                    "cached": response._hidden_params.get("cache_hit", False),
                    "timestamp": datetime.utcnow().isoformat()
                }

        except Exception as e:
            logger.error(f" LLM Request failed: {e}")
            raise

    async def _complete_streaming(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream LLM response"""

        response = await self.router.acompletion(
            model=model,
            messages=messages,
            stream=True,
            **kwargs
        )

        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def _calculate_cost(self, model: str, total_tokens: int) -> float:
        """Calculate cost based on model and tokens"""

        # Find model config
        for config in self.model_configs:
            if config["model_name"] in model or config["litellm_params"]["model"] in model:
                cost_per_token = config["model_info"].get("cost_per_token", 0)
                return cost_per_token * total_tokens

        return 0.0

    async def embed(self, text: str, model: str = "text-embedding-3") -> List[float]:
        """Generate embeddings"""

        response = await self.router.aembedding(
            model=model,
            input=text
        )

        return response.data[0].embedding

    def get_model_health(self) -> Dict[str, Any]:
        """Get health status of all models"""

        health = {}
        for config in self.model_configs:
            model_name = config["model_name"]
            # Check if model is responding
            # This is placeholder - implement actual health check
            health[model_name] = {
                "status": "healthy",
                "tier": config["model_info"]["tier"],
                "cost_per_token": config["model_info"]["cost_per_token"]
            }

        return health


# Singleton instance
_router_instance: Optional[LiteLLMRouter] = None

def get_litellm_router() -> LiteLLMRouter:
    """Get global LiteLLM router instance"""
    global _router_instance
    if _router_instance is None:
        _router_instance = LiteLLMRouter()
    return _router_instance
