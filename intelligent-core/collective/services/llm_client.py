"""
LLM Client for Collective Agent Networks

Adapts Anthropic Claude API for collective agent response generation.

Features:
- Privacy-preserving system prompts
- Conversation history management
- Temperature control for consistency
- Confidence score estimation
"""

from typing import List, Dict, Any, Optional
import anthropic
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class CollectiveLLMClient:
    """
    LLM client specifically for Collective Agent conversations

    Uses Anthropic Claude with:
    - Strong privacy instructions in system prompt
    - Conversation history for context
    - Confidence estimation from response
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LLM client

        Args:
            api_key: Anthropic API key (defaults to env var)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')

        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not set - LLM client will not work")
            self.client = None
        else:
            self.client = anthropic.AsyncAnthropic(api_key=self.api_key)

    async def generate(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate LLM response

        Args:
            system_prompt: System prompt with privacy instructions
            messages: Conversation history [{'role': 'user'|'assistant', 'content': str}]
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum response tokens

        Returns:
            Generated text response
        """

        if not self.client:
            logger.error("LLM client not initialized (missing API key)")
            return "I apologize, but I'm currently unable to generate responses. Please contact support."

        try:
            logger.debug(
                f"Generating LLM response: {len(messages)} messages, "
                f"temp={temperature}, max_tokens={max_tokens}"
            )

            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Latest Sonnet model
                system=system_prompt,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Extract text from response
            text = response.content[0].text

            logger.debug(f"Generated response: {len(text)} characters")

            return text

        except anthropic.RateLimitError as e:
            logger.error(f"Rate limit error: {e}")
            return "I apologize, but I'm currently experiencing high demand. Please try again in a moment."

        except anthropic.APIError as e:
            logger.error(f"API error: {e}", exc_info=True)
            return "I apologize, but I encountered an error. Please try again."

        except Exception as e:
            logger.error(f"Unexpected error generating response: {e}", exc_info=True)
            return "I apologize, but I encountered an unexpected error. Please try again."

    async def generate_with_confidence(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Generate response with confidence estimate

        Returns:
            {
                'message': str,
                'confidence': float (0-1),
                'reasoning': str (optional)
            }
        """

        # Generate main response
        response = await self.generate(
            system_prompt=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Estimate confidence from response characteristics
        confidence = self._estimate_confidence(response, messages)

        return {
            'message': response,
            'confidence': confidence
        }

    def _estimate_confidence(
        self,
        response: str,
        messages: List[Dict[str, str]]
    ) -> float:
        """
        Estimate confidence from response characteristics

        Indicators of high confidence:
        - Specific numbers/statistics ("5 out of 7 organizations...")
        - Definitive language ("Organizations typically...", "The common pattern...")
        - No hedging words ("maybe", "possibly", "might")

        Indicators of low confidence:
        - Hedging language
        - Lack of specifics
        - Short response
        """

        response_lower = response.lower()

        confidence = 0.7  # Base confidence

        # High confidence indicators (+0.1 each)
        high_confidence_phrases = [
            'organizations typically',
            'the common pattern',
            'most organizations',
            'successfully addressed',
            'out of',  # e.g., "5 out of 7"
        ]

        for phrase in high_confidence_phrases:
            if phrase in response_lower:
                confidence += 0.05

        # Low confidence indicators (-0.1 each)
        low_confidence_phrases = [
            'might',
            'possibly',
            'perhaps',
            'unclear',
            'difficult to say',
            'varies significantly'
        ]

        for phrase in low_confidence_phrases:
            if phrase in response_lower:
                confidence -= 0.1

        # Length indicator (very short = low confidence)
        if len(response) < 100:
            confidence -= 0.2
        elif len(response) > 500:
            confidence += 0.1

        # Cap at 0.3 - 1.0 range
        confidence = max(0.3, min(1.0, confidence))

        return round(confidence, 2)

    def format_conversation_history(
        self,
        messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Format conversation history for Anthropic API

        Ensures:
        - Alternating user/assistant messages
        - No empty messages
        - Proper role names
        """

        formatted = []

        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '').strip()

            if not content:
                continue

            # Map role names
            if role in ['user', 'assistant']:
                formatted.append({
                    'role': role,
                    'content': content
                })

        return formatted

    async def enhance_system_prompt_with_privacy(
        self,
        base_prompt: str
    ) -> str:
        """
        Enhance system prompt with strong privacy instructions

        Adds:
        - Never reveal source organizations
        - Use collective language
        - Aggregate only
        """

        privacy_instructions = """

**CRITICAL PRIVACY RULES:**

1. **NEVER reveal which specific organization did what**
   - WRONG: "Organization A used workshops, Organization B used templates"
   - RIGHT: "Organizations typically used workshops or templates"

2. **Always use collective language:**
   - "Organizations that addressed this..."
   - "The common pattern across organizations..."
   - "Most organizations found that..."
   - "Organizations typically..."

3. **Speak in aggregates only:**
   - "5 out of 7 organizations used..."
   - "The majority of organizations..."
   - "Organizations usually started with..."

4. **If asked WHO specifically:**
   - Respond: "I represent collective wisdom from multiple organizations, but I cannot reveal their specific identities to protect privacy."

5. **If asked for outliers or specific details that might identify:**
   - Generalize: "Some organizations took different approaches, including..."

6. **Your identity:**
   - "I'm a Collective Agent synthesizing experience from organizations that solved this challenge."
   - NOT: "I'm Claude" or specific organization names

**Your tone should be:**
- Helpful and supportive
- Confident (you speak for multiple successful experiences)
- Respectful of user's context
- Privacy-conscious at all times
"""

        return base_prompt + privacy_instructions

    async def test_connection(self) -> bool:
        """
        Test LLM API connection

        Returns:
            True if connection works, False otherwise
        """

        if not self.client:
            return False

        try:
            # Simple test message
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )

            return len(response.content) > 0

        except Exception as e:
            logger.error(f"LLM connection test failed: {e}")
            return False

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text

        Rough estimate: ~4 characters per token
        """
        return len(text) // 4

    async def generate_streaming(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        Generate streaming response (for real-time UI)

        Yields text chunks as they're generated
        """

        if not self.client:
            yield "LLM client not initialized"
            return

        try:
            async with self.client.messages.stream(
                model="claude-3-5-sonnet-20241022",
                system=system_prompt,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Streaming error: {e}", exc_info=True)
            yield f"\n\n[Error: {str(e)}]"


class MockLLMClient:
    """
    Mock LLM client for testing without API key

    Returns canned responses
    """

    async def generate(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Generate mock response"""

        # Extract last user message
        user_messages = [m for m in messages if m['role'] == 'user']
        if not user_messages:
            return "I'm ready to help. What would you like to know?"

        last_question = user_messages[-1]['content'].lower()

        # Pattern matching for common questions
        if 'how' in last_question or 'what' in last_question:
            return """Based on collective wisdom from multiple organizations that addressed this challenge:

Organizations typically approached this in 3 main ways:

1. **Stakeholder Workshops** (5 out of 7 organizations)
   - Started with cross-functional team sessions
   - Mapped dependencies collaboratively
   - Used visual tools (whiteboards, diagrams)

2. **Industry Templates** (4 out of 7 organizations)
   - Adapted existing BCM frameworks
   - Customized to their specific context
   - Combined with internal knowledge

3. **Iterative Approach** (Most organizations)
   - Started with high-level overview
   - Gradually added detail
   - Validated with stakeholders at each step

The common pattern across successful organizations was involving stakeholders early and using visual collaboration tools."""

        elif 'why' in last_question:
            return """Organizations that successfully addressed this found several key reasons:

1. **Complexity of dependencies** - Most organizations underestimated interconnections
2. **Stakeholder availability** - Getting time with key people was challenging
3. **Data availability** - Required information wasn't always readily accessible

The organizations that overcame these challenges did so by:
- Securing executive sponsorship upfront
- Using asynchronous data collection methods
- Breaking the work into smaller, manageable phases"""

        else:
            return """I represent collective wisdom from organizations that faced similar challenges. Could you be more specific about what aspect you'd like to explore? For example:

- How did organizations approach this challenge?
- What were the common pitfalls to avoid?
- What tools or methods were most effective?

I can provide insights based on the aggregated experience of multiple successful implementations."""

    async def generate_with_confidence(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """Generate mock response with confidence"""

        message = await self.generate(system_prompt, messages, temperature, max_tokens)

        return {
            'message': message,
            'confidence': 0.85
        }

    async def test_connection(self) -> bool:
        """Mock connection test always succeeds"""
        return True
