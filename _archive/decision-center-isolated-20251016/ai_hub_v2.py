"""
AI Intelligence Hub - Production Version with Real AI Integration

Features:
- Real Anthropic Claude integration (Tier 1/2)
- Multi-tier AI routing
- Cost tracking
- Fallback to heuristics if API unavailable
- Smart model selection
"""

import logging
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from .anthropic_client import AnthropicClient, ClaudeModel, ClaudeResponse

logger = logging.getLogger(__name__)


class AITier(Enum):
    """AI Model Tiers"""
    TIER1_STRATEGIC = "tier1_strategic"       # Claude Opus, GPT-4
    TIER2_OPERATIONAL = "tier2_operational"   # Claude Sonnet (primary)
    TIER3_QUICK = "tier3_quick"               # Claude Haiku, GPT-3.5
    TIER4_CUSTOM = "tier4_custom"             # Fine-tuned custom model


@dataclass
class AIResponse:
    """
    AI consultation response

    Attributes:
        recommendation: Recommended action
        confidence: Confidence score (0-1)
        reasoning: Explanation
        model_used: Which model was used
        tier: AI tier used
        latency_ms: Response time in milliseconds
        cost_usd: Cost in USD (0 for heuristic fallback)
    """
    recommendation: str
    confidence: float
    reasoning: str
    model_used: str
    tier: AITier
    latency_ms: int
    cost_usd: float = 0.0


class AIIntelligenceHub:
    """
    AI Intelligence Hub - Production Version

    Multi-tier AI routing with real Anthropic Claude integration:
    - Tier 1 (Strategic): Claude Opus for complex decisions
    - Tier 2 (Operational): Claude Sonnet for daily operations (primary)
    - Tier 3 (Quick): Claude Haiku for fast responses
    - Tier 4 (Custom): Custom model (future)

    Fallback to heuristics if API key not configured.

    Usage:
        hub = AIIntelligenceHub(
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
            tier1_enabled=True,
            tier2_enabled=True,
            tier3_enabled=True
        )

        response = await hub.consult(
            problem="Database repeatedly failing after restart",
            context={"recovery_attempts": 3},
            service="database",
            action="restart",
            complexity="high"
        )

        print(f"Recommendation: {response.recommendation}")
        print(f"Confidence: {response.confidence}")
        print(f"Cost: ${response.cost_usd:.4f}")
    """

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        tier1_enabled: bool = False,
        tier2_enabled: bool = True,   # Sonnet is primary
        tier3_enabled: bool = True,   # Haiku for quick
        tier4_enabled: bool = False,
        enable_fallback: bool = True
    ):
        """
        Initialize AI Intelligence Hub

        Args:
            anthropic_api_key: Anthropic API key (or set ANTHROPIC_API_KEY env)
            tier1_enabled: Enable Tier 1 (Claude Opus - expensive)
            tier2_enabled: Enable Tier 2 (Claude Sonnet - recommended)
            tier3_enabled: Enable Tier 3 (Claude Haiku - fast)
            tier4_enabled: Enable Tier 4 (Custom model - future)
            enable_fallback: Enable heuristic fallback if AI unavailable
        """
        self.tier1_enabled = tier1_enabled
        self.tier2_enabled = tier2_enabled
        self.tier3_enabled = tier3_enabled
        self.tier4_enabled = tier4_enabled
        self.enable_fallback = enable_fallback

        # Initialize Anthropic client
        self.anthropic_client = None
        if anthropic_api_key or tier1_enabled or tier2_enabled or tier3_enabled:
            try:
                self.anthropic_client = AnthropicClient(
                    api_key=anthropic_api_key,
                    requests_per_minute=50
                )
                logger.info(
                    "AI Hub initialized with Anthropic Claude "
                    f"[T1={tier1_enabled}, T2={tier2_enabled}, T3={tier3_enabled}]"
                )
            except Exception as e:
                logger.warning(f"Anthropic client initialization failed: {e}")
                if not enable_fallback:
                    raise

        if not self.anthropic_client and not enable_fallback:
            raise ValueError("No AI provider configured and fallback disabled")

        if not self.anthropic_client:
            logger.warning("No AI provider configured - using heuristic fallback")

    async def consult(
        self,
        problem: str,
        context: Dict[str, Any],
        service: str,
        action: str,
        complexity: str = "medium"
    ) -> AIResponse:
        """
        Consult AI for decision recommendation

        Args:
            problem: Problem description
            context: System context
            service: Service name
            action: Proposed action
            complexity: Complexity level (low/medium/high)

        Returns:
            AI response with recommendation
        """
        logger.info(
            f"AI consultation: {service}.{action} (complexity={complexity})"
        )

        start_time = time.time()

        # Select appropriate tier
        tier = self._select_tier(complexity, context)

        # Try real AI if available
        if self.anthropic_client:
            try:
                response = await self._consult_claude(
                    problem=problem,
                    context=context,
                    service=service,
                    action=action,
                    tier=tier
                )

                latency_ms = int((time.time() - start_time) * 1000)
                logger.info(
                    f"AI consultation complete: {tier.value}, "
                    f"{response.model_used}, "
                    f"${response.cost_usd:.4f}, {latency_ms}ms"
                )

                return response

            except Exception as e:
                logger.error(f"AI consultation failed: {e}")

                if not self.enable_fallback:
                    raise

                logger.warning("Falling back to heuristic analysis")

        # Fallback to heuristics
        return self._heuristic_consultation(
            problem=problem,
            context=context,
            service=service,
            action=action,
            tier=tier
        )

    def _select_tier(self, complexity: str, context: Dict[str, Any]) -> AITier:
        """
        Select appropriate AI tier based on complexity

        Tier selection logic:
        - Tier 1 (Opus): High complexity, critical decisions
        - Tier 2 (Sonnet): Medium complexity, daily operations (primary)
        - Tier 3 (Haiku): Low complexity, quick responses
        - Tier 4 (Custom): Simple patterns (future)

        Args:
            complexity: Complexity level
            context: Request context

        Returns:
            Selected AI tier
        """
        # Check recovery attempts - high attempts = high complexity
        attempts = context.get("recovery_attempts", 0)
        if attempts >= 3:
            complexity = "high"

        # Tier 4: Custom model for simple patterns (future)
        if self.tier4_enabled and complexity == "low":
            logger.debug("Selected Tier 4: Custom model")
            return AITier.TIER4_CUSTOM

        # Tier 1: Opus for high complexity
        if self.tier1_enabled and complexity == "high":
            logger.debug("Selected Tier 1: Claude Opus (strategic)")
            return AITier.TIER1_STRATEGIC

        # Tier 2: Sonnet for medium complexity (primary workhorse)
        if self.tier2_enabled and complexity in ["medium", "high"]:
            logger.debug("Selected Tier 2: Claude Sonnet (operational)")
            return AITier.TIER2_OPERATIONAL

        # Tier 3: Haiku for low complexity / fast response
        if self.tier3_enabled:
            logger.debug("Selected Tier 3: Claude Haiku (quick)")
            return AITier.TIER3_QUICK

        # Fallback to Tier 2 if available
        if self.tier2_enabled:
            logger.warning("Fallback to Tier 2: Claude Sonnet")
            return AITier.TIER2_OPERATIONAL

        # Last resort
        logger.warning("No tier available, using fallback")
        return AITier.TIER3_QUICK

    async def _consult_claude(
        self,
        problem: str,
        context: Dict[str, Any],
        service: str,
        action: str,
        tier: AITier
    ) -> AIResponse:
        """
        Consult Claude API for decision

        Args:
            problem: Problem description
            context: Context
            service: Service name
            action: Proposed action
            tier: Selected tier

        Returns:
            AI response
        """
        # Map tier to Claude model
        tier_to_model = {
            AITier.TIER1_STRATEGIC: ClaudeModel.OPUS,
            AITier.TIER2_OPERATIONAL: ClaudeModel.SONNET,
            AITier.TIER3_QUICK: ClaudeModel.HAIKU
        }

        model = tier_to_model.get(tier, ClaudeModel.SONNET)

        # Build system prompt for BCM decision making
        system_prompt = """You are an AI decision assistant for a Business Continuity Management (BCM) platform following ISO 22301 standards.

Your role is to provide intelligent recommendations for infrastructure recovery decisions.

Guidelines:
- Analyze the situation carefully
- Consider recovery attempts history
- Assess risk vs benefit
- Provide clear recommendation
- Explain reasoning
- Give confidence score (0.0-1.0)

Output format (JSON):
{
  "recommendation": "approve_restart|escalate|investigate|wait_and_retry",
  "reasoning": "Detailed explanation...",
  "confidence": 0.85
}"""

        # Build user prompt
        attempts = context.get("recovery_attempts", 0)
        downtime = context.get("downtime_seconds", 0)

        user_prompt = f"""SITUATION:
Service: {service}
Proposed Action: {action}
Problem: {problem}

CONTEXT:
- Recovery attempts: {attempts}
- Downtime: {downtime}s
- Recent failures: {len(context.get('recent_failures', []))}

ANALYSIS REQUIRED:
Should we {action} {service}?

Consider:
1. Is this action safe given the recovery attempts?
2. What are the risks?
3. Should we escalate to human instead?
4. What's the confidence level?

Provide recommendation in JSON format."""

        # Query Claude
        claude_response = await self.anthropic_client.query(
            prompt=user_prompt,
            model=model,
            system_prompt=system_prompt,
            temperature=0.3,  # Lower for more consistent decisions
            max_tokens=1024,
            context=context
        )

        # Parse response
        recommendation, reasoning, confidence = self._parse_claude_response(
            claude_response.content,
            action
        )

        return AIResponse(
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning,
            model_used=claude_response.model,
            tier=tier,
            latency_ms=claude_response.latency_ms,
            cost_usd=claude_response.cost_usd
        )

    def _parse_claude_response(
        self,
        content: str,
        action: str
    ) -> tuple[str, str, float]:
        """
        Parse Claude response

        Args:
            content: Claude response content
            action: Proposed action

        Returns:
            (recommendation, reasoning, confidence)
        """
        import json
        import re

        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())

                recommendation = data.get("recommendation", f"approve_{action}")
                reasoning = data.get("reasoning", content[:500])
                confidence = float(data.get("confidence", 0.7))

                return recommendation, reasoning, min(confidence, 1.0)

        except Exception as e:
            logger.warning(f"Failed to parse Claude JSON: {e}")

        # Fallback: extract from text
        content_lower = content.lower()

        if "escalate" in content_lower or "human" in content_lower:
            recommendation = "escalate"
            confidence = 0.6
        elif "investigate" in content_lower:
            recommendation = "investigate"
            confidence = 0.7
        elif "wait" in content_lower or "retry" in content_lower:
            recommendation = "wait_and_retry"
            confidence = 0.7
        elif "approve" in content_lower or "recommend" in content_lower:
            recommendation = f"approve_{action}"
            confidence = 0.8
        else:
            recommendation = f"approve_{action}"
            confidence = 0.5

        reasoning = content[:500] if len(content) > 500 else content

        return recommendation, reasoning, confidence

    def _heuristic_consultation(
        self,
        problem: str,
        context: Dict[str, Any],
        service: str,
        action: str,
        tier: AITier
    ) -> AIResponse:
        """
        Fallback heuristic consultation (when AI unavailable)

        Args:
            problem: Problem description
            context: Context
            service: Service name
            action: Proposed action
            tier: Selected tier

        Returns:
            Heuristic AI response
        """
        problem_lower = problem.lower()
        attempts = context.get("recovery_attempts", 0)

        # Heuristic logic
        if "repeated failure" in problem_lower or attempts >= 3:
            recommendation = "escalate"
            reasoning = f"Repeated failures detected ({attempts} attempts). Manual intervention recommended."
            confidence = 0.75

        elif any(word in problem_lower for word in ["memory", "cpu", "disk"]):
            if action == "restart":
                recommendation = "approve_restart"
                reasoning = "Resource exhaustion detected. Restart will clear memory leaks."
                confidence = 0.80
            elif action == "scale_up":
                recommendation = "approve_scale"
                reasoning = "Resource exhaustion indicates capacity issue. Scaling recommended."
                confidence = 0.70
            else:
                recommendation = f"approve_{action}"
                reasoning = f"Resource issue detected. {action} may help."
                confidence = 0.65

        elif any(word in problem_lower for word in ["timeout", "network", "connection"]):
            recommendation = "wait_and_retry"
            reasoning = "Network issue detected. Temporary glitch likely. Wait and retry."
            confidence = 0.70

        elif "unknown" in problem_lower:
            recommendation = "escalate"
            reasoning = "Unknown issue type. Low confidence. Human expertise needed."
            confidence = 0.40

        else:
            recommendation = f"approve_{action}"
            reasoning = f"Standard {action} operation for {service}. Within normal parameters."
            confidence = 0.65

        return AIResponse(
            recommendation=recommendation,
            confidence=confidence,
            reasoning=f"[HEURISTIC FALLBACK] {reasoning}",
            model_used="heuristic_fallback",
            tier=tier,
            latency_ms=10,  # Very fast
            cost_usd=0.0    # Free
        )

    async def get_tier_status(self) -> Dict[str, Any]:
        """
        Get AI tier status and usage

        Returns:
            Tier status information
        """
        status = {
            "tier1_strategic": {
                "enabled": self.tier1_enabled,
                "model": "claude-opus",
                "provider": "anthropic",
                "cost_per_1k_tokens": 0.015  # Input
            },
            "tier2_operational": {
                "enabled": self.tier2_enabled,
                "model": "claude-sonnet-3.5",
                "provider": "anthropic",
                "cost_per_1k_tokens": 0.003  # Input
            },
            "tier3_quick": {
                "enabled": self.tier3_enabled,
                "model": "claude-haiku-3.5",
                "provider": "anthropic",
                "cost_per_1k_tokens": 0.0008  # Input
            },
            "tier4_custom": {
                "enabled": self.tier4_enabled,
                "model": "custom-bcm-v1",
                "provider": "internal",
                "cost_per_1k_tokens": 0.0
            }
        }

        # Add usage stats if Anthropic client available
        if self.anthropic_client:
            usage_stats = self.anthropic_client.get_usage_stats()
            status["usage"] = usage_stats
            status["api_available"] = True
        else:
            status["api_available"] = False
            status["fallback_mode"] = "heuristics"

        return status

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics from Anthropic client"""
        if self.anthropic_client:
            return self.anthropic_client.get_usage_stats()
        return {
            "total_requests": 0,
            "total_cost_usd": 0.0,
            "mode": "heuristic_fallback"
        }


# Export
__all__ = ["AIIntelligenceHub", "AITier", "AIResponse"]
