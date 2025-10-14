"""
Loop Detector
=============

Detects infinite loops and repetitive patterns.

Prevents:
- Same decision repeated too many times
- Oscillating between two states
- Stuck in retry loops
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import deque

from .models import (
    Decision, FullContext, SafetyResult, SafetyConcern, Loop
)

logger = logging.getLogger(__name__)


class LoopDetector:
    """
    Detects infinite loops and repetitive patterns.

    Detection methods:
    - Action repetition (same action N times)
    - State oscillation (A→B→A→B...)
    - Time-based loops (stuck for too long)

    Example:
        ```python
        detector = LoopDetector()
        await detector.initialize()

        result = await detector.check(decision, context)
        if not result.safe:
            print(f"Loop detected: {result.concerns}")
        ```
    """

    # Thresholds
    MAX_SAME_ACTION_COUNT = 5  # Same action 5 times = loop
    MAX_OSCILLATION_COUNT = 3  # A→B→A→B→A = loop
    LOOP_DETECTION_WINDOW = 3600  # 1 hour window

    def __init__(self):
        # Track recent decisions
        self.recent_decisions: deque = deque(maxlen=100)
        self.initialized = False

    async def initialize(self) -> None:
        """Initialize loop detector."""
        self.initialized = True
        logger.info("LoopDetector initialized")

    async def check(
        self,
        decision: Decision,
        context: FullContext
    ) -> SafetyResult:
        """
        Check for loops.

        Args:
            decision: Decision to check
            context: Full context

        Returns:
            SafetyResult: Detection result
        """
        concerns: List[SafetyConcern] = []

        # Add current decision to history
        self._add_decision(decision)

        # Check for action repetition
        repetition_loop = self._detect_action_repetition(decision)
        if repetition_loop:
            concerns.append(SafetyConcern(
                type='infinite_loop',
                severity='high',
                description=f"Action '{decision.action.value}' repeated {repetition_loop.repeat_count} times",
                evidence={
                    'loop': {
                        'pattern': repetition_loop.pattern,
                        'repeat_count': repetition_loop.repeat_count,
                        'duration': repetition_loop.duration
                    }
                },
                recommended_action='break_loop_or_escalate'
            ))

        # Check for oscillation
        oscillation_loop = self._detect_oscillation()
        if oscillation_loop:
            concerns.append(SafetyConcern(
                type='infinite_loop',
                severity='high',
                description=f"Oscillating between states: {oscillation_loop.pattern}",
                evidence={
                    'loop': {
                        'pattern': oscillation_loop.pattern,
                        'repeat_count': oscillation_loop.repeat_count
                    }
                },
                recommended_action='break_loop_or_escalate'
            ))

        # Check for time-based stuck
        stuck_loop = self._detect_stuck_state(context)
        if stuck_loop:
            concerns.append(SafetyConcern(
                type='infinite_loop',
                severity='medium',
                description=f"Stuck in same state for {stuck_loop.duration:.0f} seconds",
                evidence={
                    'loop': {
                        'duration': stuck_loop.duration,
                        'suggestion': stuck_loop.suggestion
                    }
                },
                recommended_action='escalate_to_human'
            ))

        safe = len(concerns) == 0

        return SafetyResult(
            safe=safe,
            concerns=concerns,
            loop_check=safe
        )

    def _add_decision(self, decision: Decision) -> None:
        """Add decision to history."""
        self.recent_decisions.append({
            'action': decision.action.value,
            'timestamp': decision.timestamp,
            'metadata': decision.metadata
        })

    def _detect_action_repetition(
        self,
        decision: Decision
    ) -> Optional[Loop]:
        """Detect same action repeated too many times."""
        if len(self.recent_decisions) < self.MAX_SAME_ACTION_COUNT:
            return None

        # Get recent actions
        recent = list(self.recent_decisions)[-self.MAX_SAME_ACTION_COUNT:]

        # Check if all same action
        action = decision.action.value
        if all(d['action'] == action for d in recent):
            # Calculate duration
            first_time = recent[0]['timestamp']
            last_time = recent[-1]['timestamp']
            duration = (last_time - first_time).total_seconds()

            return Loop(
                pattern=f"repeat:{action}",
                repeat_count=len(recent),
                duration=duration,
                actions=[action] * len(recent),
                suggestion="Break loop by trying different action or escalating"
            )

        return None

    def _detect_oscillation(self) -> Optional[Loop]:
        """Detect oscillation between two or more states."""
        if len(self.recent_decisions) < 6:
            return None

        recent = list(self.recent_decisions)[-6:]
        actions = [d['action'] for d in recent]

        # Check for A→B→A→B pattern
        if len(set(actions)) == 2:
            # Check if alternating
            if all(actions[i] != actions[i+1] for i in range(len(actions)-1)):
                return Loop(
                    pattern=f"oscillate:{actions[0]}↔{actions[1]}",
                    repeat_count=len(actions) // 2,
                    duration=0,
                    actions=actions,
                    suggestion="Breaking oscillation loop - try third option or escalate"
                )

        return None

    def _detect_stuck_state(
        self,
        context: FullContext
    ) -> Optional[Loop]:
        """Detect stuck in same state for too long."""
        # Check workflows for stuck state
        for workflow in context.workflows:
            if workflow.get('status') == 'stuck':
                stuck_duration = workflow.get('stuck_duration_minutes', 0) * 60

                if stuck_duration > 1800:  # 30 minutes
                    return Loop(
                        pattern='stuck_workflow',
                        repeat_count=1,
                        duration=stuck_duration,
                        actions=['wait'],
                        suggestion="Workflow stuck for too long - escalate to human"
                    )

        return None

    def reset(self) -> None:
        """Reset loop detector history."""
        self.recent_decisions.clear()
        logger.info("Loop detector reset")
