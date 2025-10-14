"""
Anthropic Claude API Adapter

Refactored from existing AnthropicGovernanceBrain to be general-purpose.
Maintains proven async httpx implementation with fallback mechanism.
"""

import os
import logging
from typing import Dict, List, Optional, Any
import httpx

logger = logging.getLogger(__name__)


class AnthropicAdapter:
    """
    General-purpose adapter for Anthropic Claude API.

    Supports:
    - Multiple Claude models (Sonnet 3.5, Haiku, Opus)
    - Async HTTP calls via httpx
    - System prompts + user messages
    - Context injection
    - Usage tracking
    - Error handling with fallback
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        timeout: float = 120.0
    ):
        """
        Initialize Anthropic adapter.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Claude model to use
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-1.0)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment or parameters")

        self.base_url = 'https://api.anthropic.com/v1'
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        logger.info(f"Initialized Anthropic adapter with model: {self.model}")

    async def generate(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate response from Claude API.

        Args:
            user_message: User's query or prompt
            system_prompt: Optional system instruction
            context: Optional context data to inject into prompt
            temperature: Override default temperature
            max_tokens: Override default max_tokens

        Returns:
            Dict with:
                - content: Generated text
                - model_used: Model name
                - tokens_used: Token count
                - finish_reason: Stop reason
                - success: True if successful
        """
        try:
            # Build enhanced prompt with context if provided
            enhanced_message = self._build_message(user_message, context)

            # Prepare API request
            payload = {
                'model': self.model,
                'max_tokens': max_tokens or self.max_tokens,
                'temperature': temperature or self.temperature,
                'messages': [
                    {'role': 'user', 'content': enhanced_message}
                ]
            }

            # Add system prompt if provided
            if system_prompt:
                payload['system'] = system_prompt

            # Make API call
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f'{self.base_url}/messages',
                    headers={
                        'x-api-key': self.api_key,
                        'content-type': 'application/json',
                        'anthropic-version': '2023-06-01'
                    },
                    json=payload,
                    timeout=self.timeout
                )

                # Handle response
                if response.status_code == 200:
                    result = response.json()

                    # Extract content (handle both text and content blocks)
                    content = self._extract_content(result)

                    return {
                        'content': content,
                        'model_used': self.model,
                        'tokens_used': result.get('usage', {}).get('output_tokens', 0),
                        'input_tokens': result.get('usage', {}).get('input_tokens', 0),
                        'finish_reason': result.get('stop_reason', 'unknown'),
                        'success': True
                    }
                else:
                    logger.error(f"Claude API error: {response.status_code} - {response.text}")
                    return self._fallback_response(
                        f"API error: {response.status_code}",
                        user_message
                    )

        except httpx.TimeoutException:
            logger.error(f"Claude API timeout after {self.timeout}s")
            return self._fallback_response("Request timeout", user_message)

        except Exception as e:
            logger.error(f"Unexpected error calling Claude API: {str(e)}", exc_info=True)
            return self._fallback_response(str(e), user_message)

    async def generate_with_conversation(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate response from conversation history.

        Args:
            messages: List of {"role": "user"|"assistant", "content": "..."}
            system_prompt: Optional system instruction
            temperature: Override default temperature
            max_tokens: Override default max_tokens

        Returns:
            Same format as generate()
        """
        try:
            payload = {
                'model': self.model,
                'max_tokens': max_tokens or self.max_tokens,
                'temperature': temperature or self.temperature,
                'messages': messages
            }

            if system_prompt:
                payload['system'] = system_prompt

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f'{self.base_url}/messages',
                    headers={
                        'x-api-key': self.api_key,
                        'content-type': 'application/json',
                        'anthropic-version': '2023-06-01'
                    },
                    json=payload,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    result = response.json()
                    content = self._extract_content(result)

                    return {
                        'content': content,
                        'model_used': self.model,
                        'tokens_used': result.get('usage', {}).get('output_tokens', 0),
                        'input_tokens': result.get('usage', {}).get('input_tokens', 0),
                        'finish_reason': result.get('stop_reason', 'unknown'),
                        'success': True
                    }
                else:
                    logger.error(f"Claude API error: {response.status_code}")
                    return self._fallback_response(
                        f"API error: {response.status_code}",
                        messages[-1].get('content', '')
                    )

        except Exception as e:
            logger.error(f"Error in conversation generation: {str(e)}", exc_info=True)
            return self._fallback_response(str(e), messages[-1].get('content', ''))

    def _build_message(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Build enhanced message with context injection.

        Args:
            user_message: Original user message
            context: Optional context data

        Returns:
            Enhanced message with context
        """
        if not context:
            return user_message

        # Build context section
        context_parts = []

        if 'retrieved_documents' in context:
            context_parts.append("**Relevant BCM Context:**")
            for doc in context['retrieved_documents']:
                context_parts.append(f"- {doc.get('content', '')}")

        if 'tenant_data' in context:
            context_parts.append(f"\n**Organization Context:** {context['tenant_data']}")

        if 'intent' in context:
            context_parts.append(f"\n**Detected Intent:** {context['intent']}")

        if 'module' in context:
            context_parts.append(f"**BCM Module:** {context['module']}")

        # Combine context + user message
        if context_parts:
            return "\n".join(context_parts) + f"\n\n**User Query:** {user_message}"

        return user_message

    def _extract_content(self, api_response: Dict[str, Any]) -> str:
        """
        Extract text content from Claude API response.

        Args:
            api_response: Raw API response

        Returns:
            Extracted text content
        """
        content = api_response.get('content', [])

        if isinstance(content, list) and len(content) > 0:
            # Handle content blocks format
            return content[0].get('text', '')
        elif isinstance(content, str):
            # Handle direct string format
            return content

        return ""

    def _fallback_response(self, error: str, user_message: str) -> Dict[str, Any]:
        """
        Generate fallback response when Claude API fails.

        Args:
            error: Error description
            user_message: Original user message

        Returns:
            Fallback response dict
        """
        return {
            'content': (
                f"I apologize, but I'm currently unable to process your request due to: {error}. "
                "Please try again in a moment, or contact support if the issue persists."
            ),
            'model_used': 'fallback',
            'tokens_used': 0,
            'input_tokens': 0,
            'finish_reason': 'error',
            'success': False,
            'error': error
        }

    async def test_connection(self) -> bool:
        """
        Test connection to Claude API.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            result = await self.generate(
                user_message="Hello, this is a connection test.",
                max_tokens=10
            )
            return result['success']
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
