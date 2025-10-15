"""
Anthropic Claude Client for Decision Center

Production-ready client for Anthropic Claude API with:
- Multi-model support (Sonnet, Haiku, Opus)
- Cost tracking
- Rate limiting
- Error handling + fallback
- Async support
"""

import asyncio
import httpx
import logging
import os
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ClaudeModel(Enum):
    """Claude model variants"""
    SONNET = "claude-3-5-sonnet-20241022"      # Tier 2: Balanced (primary)
    HAIKU = "claude-3-5-haiku-20241022"        # Tier 3: Fast & cheap
    OPUS = "claude-3-opus-20240229"            # Tier 1: Most capable


@dataclass
class ClaudeResponse:
    """
    Claude API response

    Attributes:
        content: Response text
        model: Model used
        input_tokens: Input tokens used
        output_tokens: Output tokens used
        latency_ms: Response time in milliseconds
        cost_usd: Estimated cost in USD
    """
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cost_usd: float


class AnthropicClient:
    """
    Anthropic Claude API Client

    Features:
    - Multi-model support (Sonnet, Haiku, Opus)
    - Automatic retry with exponential backoff
    - Rate limiting
    - Cost tracking
    - Usage statistics
    - Fallback mechanisms

    Usage:
        client = AnthropicClient(api_key=os.getenv('ANTHROPIC_API_KEY'))

        response = await client.query(
            prompt="Should we restart database after 3 attempts?",
            model=ClaudeModel.SONNET,
            system_prompt="You are a BCM decision assistant"
        )

        print(f"Response: {response.content}")
        print(f"Cost: ${response.cost_usd:.4f}")
    """

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        ClaudeModel.OPUS: {
            "input": 15.0,   # $15 per 1M input tokens
            "output": 75.0   # $75 per 1M output tokens
        },
        ClaudeModel.SONNET: {
            "input": 3.0,    # $3 per 1M input tokens
            "output": 15.0   # $15 per 1M output tokens
        },
        ClaudeModel.HAIKU: {
            "input": 0.8,    # $0.80 per 1M input tokens
            "output": 4.0    # $4 per 1M output tokens
        }
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.anthropic.com",
        timeout: float = 60.0,
        max_retries: int = 3,
        requests_per_minute: int = 50
    ):
        """
        Initialize Anthropic client

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            base_url: API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            requests_per_minute: Rate limit (requests per minute)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.requests_per_minute = requests_per_minute

        # Rate limiting
        self.request_times = []

        # Usage tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.total_requests = 0

        if not self.api_key:
            logger.warning(
                "Anthropic API key not configured. "
                "Set ANTHROPIC_API_KEY environment variable."
            )

        logger.info(f"Anthropic client initialized (rate limit: {requests_per_minute}/min)")

    async def query(
        self,
        prompt: str,
        model: ClaudeModel = ClaudeModel.SONNET,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        context: Optional[Dict[str, Any]] = None
    ) -> ClaudeResponse:
        """
        Query Claude API

        Args:
            prompt: User prompt
            model: Claude model to use
            system_prompt: System prompt (optional)
            temperature: Temperature (0.0-1.0, lower = more deterministic)
            max_tokens: Maximum output tokens
            context: Additional context (optional)

        Returns:
            ClaudeResponse object

        Raises:
            Exception: If API call fails after all retries
        """
        if not self.api_key:
            raise ValueError("Anthropic API key not configured")

        # Rate limiting check
        await self._wait_for_rate_limit()

        start_time = time.time()

        # Build messages
        messages = []

        # Add context if provided
        if context:
            import json
            context_str = json.dumps(context, indent=2)
            prompt_with_context = f"Context:\n{context_str}\n\nQuery:\n{prompt}"
        else:
            prompt_with_context = prompt

        messages.append({
            "role": "user",
            "content": prompt_with_context
        })

        # Prepare request payload
        payload = {
            "model": model.value,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }

        # Add system prompt if provided
        if system_prompt:
            payload["system"] = system_prompt

        # Retry loop
        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/v1/messages",
                        headers={
                            "x-api-key": self.api_key,
                            "content-type": "application/json",
                            "anthropic-version": "2023-06-01"
                        },
                        json=payload,
                        timeout=self.timeout
                    )

                    if response.status_code == 200:
                        result = response.json()

                        # Extract response
                        content = result["content"][0]["text"]
                        usage = result.get("usage", {})
                        input_tokens = usage.get("input_tokens", 0)
                        output_tokens = usage.get("output_tokens", 0)

                        # Calculate cost
                        cost = self._calculate_cost(model, input_tokens, output_tokens)

                        # Calculate latency
                        latency_ms = int((time.time() - start_time) * 1000)

                        # Update statistics
                        self._update_stats(input_tokens, output_tokens, cost)

                        logger.info(
                            f"Claude API success: {model.name}, "
                            f"{input_tokens}+{output_tokens} tokens, "
                            f"${cost:.4f}, {latency_ms}ms"
                        )

                        return ClaudeResponse(
                            content=content,
                            model=model.value,
                            input_tokens=input_tokens,
                            output_tokens=output_tokens,
                            latency_ms=latency_ms,
                            cost_usd=cost
                        )

                    elif response.status_code == 429:
                        # Rate limited
                        retry_after = int(response.headers.get("retry-after", 60))
                        logger.warning(
                            f"Rate limited (attempt {attempt}/{self.max_retries}). "
                            f"Retry after {retry_after}s"
                        )

                        if attempt < self.max_retries:
                            await asyncio.sleep(retry_after)
                            continue
                        else:
                            raise Exception(f"Rate limit exceeded after {attempt} attempts")

                    else:
                        error_text = response.text
                        logger.error(
                            f"Claude API error {response.status_code}: {error_text}"
                        )

                        if attempt < self.max_retries:
                            # Exponential backoff
                            wait_time = 2 ** attempt
                            logger.info(f"Retrying in {wait_time}s...")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            raise Exception(
                                f"API error {response.status_code}: {error_text}"
                            )

            except httpx.TimeoutException:
                logger.error(f"Request timeout (attempt {attempt}/{self.max_retries})")

                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    raise Exception("Request timeout after all retries")

            except Exception as e:
                logger.error(f"Unexpected error: {e}")

                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    raise

        # Should not reach here
        raise Exception("All retry attempts failed")

    async def _wait_for_rate_limit(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()

        # Remove requests older than 1 minute
        self.request_times = [
            t for t in self.request_times
            if now - t < 60
        ]

        # Check if we're at the limit
        if len(self.request_times) >= self.requests_per_minute:
            # Wait until oldest request is > 1 minute old
            oldest = self.request_times[0]
            wait_time = 60 - (now - oldest) + 1  # +1 for safety

            if wait_time > 0:
                logger.warning(
                    f"Rate limit reached ({self.requests_per_minute}/min). "
                    f"Waiting {wait_time:.1f}s..."
                )
                await asyncio.sleep(wait_time)

        # Record this request
        self.request_times.append(time.time())

    def _calculate_cost(
        self,
        model: ClaudeModel,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Calculate cost in USD

        Args:
            model: Claude model used
            input_tokens: Input tokens
            output_tokens: Output tokens

        Returns:
            Cost in USD
        """
        pricing = self.PRICING[model]

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def _update_stats(self, input_tokens: int, output_tokens: int, cost: float):
        """Update usage statistics"""
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += cost
        self.total_requests += 1

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics

        Returns:
            Usage statistics dictionary
        """
        total_tokens = self.total_input_tokens + self.total_output_tokens

        return {
            "total_requests": self.total_requests,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": total_tokens,
            "total_cost_usd": round(self.total_cost, 4),
            "average_cost_per_request": (
                round(self.total_cost / self.total_requests, 4)
                if self.total_requests > 0
                else 0.0
            ),
            "average_tokens_per_request": (
                int(total_tokens / self.total_requests)
                if self.total_requests > 0
                else 0
            )
        }

    def reset_stats(self):
        """Reset usage statistics"""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.total_requests = 0

        logger.info("Usage statistics reset")


# Export
__all__ = ["AnthropicClient", "ClaudeModel", "ClaudeResponse"]
