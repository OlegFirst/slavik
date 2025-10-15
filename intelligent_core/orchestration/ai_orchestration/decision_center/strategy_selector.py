"""
Strategy Selector
=================

Selects best strategy for handling situations.

Strategy sources (in order of preference):
1. Procedural Memory: Learned patterns from ML models
2. Case Library: Historical successful cases
3. AI Generation: Generate new strategy using AI

Each strategy has:
- Action: What to do
- Rationale: Why this action
- Confidence: How confident (0-1)
- Source: Where it came from _ Learned from: Which cases informed it
"""

import logging
from typing import List, Optional
from datetime import datetime

from ..models import (
    Strategy, Priority, FullContext, PriorityLevel
)

logger = logging.getLogger(__name__)


class StrategySelector:
    """
    Selects best strategy from multiple sources.

    Strategy selection flow:
    1. Check procedural memory for learned patterns
    2. Search case library for similar situations
    3. Generate new strategy using AI
    4. Rank strategies by confidence and relevance
    5. Return top N strategies

    Example:
        ```python
        selector = StrategySelector()
        await selector.initialize(memory)

        strategies = await selector.select_strategies(context, priority)
        best = strategies[0]
        print(f"Best strategy: {best.action} (confidence: {best.confidence})")
        ```
    """

    def __init__(self):
        self.memory = None
        self.initialized = False

    async def initialize(self, memory) -> None:
        """
        Initialize strategy selector.

        Args:
            memory: DistributedMemory instance
        """
        self.memory = memory
        self.initialized = True
        logger.info("StrategySelector initialized")

    async def select_strategies(
        self,
        context: FullContext,
        priority: Priority,
        max_strategies: int = 5
    ) -> List[Strategy]:
        """
        Select best strategies for situation.

        Args:
            context: Full context
            priority: Priority assessment
            max_strategies: Maximum strategies to return

        Returns:
            List[Strategy]: Ranked list of strategies (best first)

        Example:
            ```python
            strategies = await selector.select_strategies(context, priority)
            for strategy in strategies:
                print(f"- {strategy.action}: {strategy.rationale}")
            ```
        """
        logger.debug("Selecting strategies...")

        all_strategies = []

        # 1. Get strategies from procedural memory
        procedural_strategies = await self._get_procedural_strategies(context)
        all_strategies.extend(procedural_strategies)
        logger.debug(f"Found {len(procedural_strategies)} procedural strategies")

        # 2. Get strategies from case library
        case_strategies = await self._get_case_strategies(context)
        all_strategies.extend(case_strategies)
        logger.debug(f"Found {len(case_strategies)} case-based strategies")

        # 3. Generate new strategy if needed
        if len(all_strategies) < 3:
            generated = await self._generate_strategy(context, priority)
            if generated:
                all_strategies.append(generated)
                logger.debug("Generated new AI strategy")

        # 4. Rank strategies
        ranked = self._rank_strategies(all_strategies, context, priority)

        # 5. Return top N
        top_strategies = ranked[:max_strategies]
        logger.info(f"Selected {len(top_strategies)} strategies")

        return top_strategies

    async def _get_procedural_strategies(
        self,
        context: FullContext
    ) -> List[Strategy]:
        """
        Get strategies from procedural memory (ML models).

        This would use trained ML models that learned patterns.
        For now, returns stub.
        """
        try:
            if not self.memory:
                return []

            # TODO: Query ML models from procedural memory
            # For now, return empty
            logger.debug("Procedural memory query (stub)")
            return []

        except Exception as e:
            logger.error(f"Error getting procedural strategies: {e}")
            return []

    async def _get_case_strategies(
        self,
        context: FullContext
    ) -> List[Strategy]:
        """
        Get strategies from similar cases in case library.

        Uses vector similarity to find similar situations
        and extract successful strategies.
        """
        try:
            strategies = []

            # Get similar situations from context
            for similar in context.similar_situations:
                if similar.get('successful', False):
                    strategy = Strategy(
                        action=similar.get('action', 'unknown'),
                        rationale=similar.get('rationale', 'Based on similar case'),
                        confidence=similar.get('confidence', 0.7),
                        source='case_library',
                        learned_from=[similar.get('case_id', 'unknown')],
                        metadata=similar
                    )
                    strategies.append(strategy)

            return strategies

        except Exception as e:
            logger.error(f"Error getting case strategies: {e}")
            return []

    async def _generate_strategy(
        self,
        context: FullContext,
        priority: Priority
    ) -> Optional[Strategy]:
        """
        Generate new strategy using AI.

        This would use LLM to analyze context and generate strategy.
        For now, returns rule-based fallback.
        """
        try:
            # Rule-based fallback strategy
            action = self._determine_fallback_action(context, priority)
            rationale = self._generate_fallback_rationale(context, priority, action)

            return Strategy(
                action=action,
                rationale=rationale,
                confidence=0.6,  # Lower confidence for generated strategies
                source='ai_generated',
                learned_from=[],
                metadata={
                    'generated_at': datetime.utcnow().isoformat(),
                    'method': 'rule_based_fallback'
                }
            )

        except Exception as e:
            logger.error(f"Error generating strategy: {e}")
            return None

    def _determine_fallback_action(
        self,
        context: FullContext,
        priority: Priority
    ) -> str:
        """Determine fallback action based on rules."""
        # Critical priority = immediate action
        if priority.level == PriorityLevel.CRITICAL:
            return "escalate_to_human_immediately"

        # Platform down = escalate
        if context.platform_state.get('status') == 'down':
            return "escalate_platform_outage"

        # Many active workflows = delegate to workflow specialist
        if len(context.workflows) > 10:
            return "delegate_to_workflow_specialist"

        # High risk = wait and monitor
        if priority.reasoning.get('risk_level', 0) > 70:
            return "wait_and_monitor_with_alerts"

        # Default = analyze and recommend
        return "analyze_and_recommend_action"

    def _generate_fallback_rationale(
        self,
        context: FullContext,
        priority: Priority,
        action: str
    ) -> str:
        """Generate rationale for fallback action."""
        factors = []

        if priority.level == PriorityLevel.CRITICAL:
            factors.append("critical priority level")

        if context.platform_state.get('status') in ['degraded', 'down']:
            factors.append(f"platform status: {context.platform_state.get('status')}")

        if len(context.workflows) > 10:
            factors.append(f"{len(context.workflows)} active workflows")

        if len(context.recent_events) > 50:
            factors.append(f"high event activity ({len(context.recent_events)} events)")

        if factors:
            return f"Recommended based on: {', '.join(factors)}"
        else:
            return "Standard procedure for this situation type"

    def _rank_strategies(
        self,
        strategies: List[Strategy],
        context: FullContext,
        priority: Priority
    ) -> List[Strategy]:
        """
        Rank strategies by relevance and confidence.

        Ranking factors:
        - Confidence score (40%)
        - Source reliability (30%)
        - Recency of learned cases (20%)
        - Priority alignment (10%)
        """
        if not strategies:
            return []

        # Calculate ranking score for each strategy
        for strategy in strategies:
            score = 0.0

            # Confidence (40%)
            score += strategy.confidence * 0.4

            # Source reliability (30%)
            source_weights = {
                'procedural_memory': 1.0,  # Learned patterns = most reliable
                'case_library': 0.8,       # Historical cases = reliable
                'ai_generated': 0.6        # Generated = less reliable
            }
            score += source_weights.get(strategy.source, 0.5) * 0.3

            # Recency (20%) - prefer recent learnings
            if strategy.learned_from:
                score += 0.2
            else:
                score += 0.1

            # Priority alignment (10%)
            if priority.level == PriorityLevel.CRITICAL:
                if 'escalate' in strategy.action.lower() or 'immediate' in strategy.action.lower():
                    score += 0.1

            # Store score in metadata
            strategy.metadata['ranking_score'] = score

        # Sort by ranking score (descending)
        ranked = sorted(
            strategies,
            key=lambda s: s.metadata.get('ranking_score', 0),
            reverse=True
        )

        return ranked
