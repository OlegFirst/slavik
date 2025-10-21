"""
Safety Monitor
==============

Main safety validation orchestrator.

Runs all safety checks:
1. Constitution enforcement
2. Loop detection
3. Hallucination detection
4. Control monitoring

Blocks execution if any critical concerns found.
"""

import logging
from typing import List

from ..models import (
    Decision, FullContext, SafetyResult, SafetyConcern
)
from .constitution_enforcer import ConstitutionEnforcer
from .loop_detector import LoopDetector
from .hallucination_detector import HallucinationDetector
from .control_monitor import ControlMonitor

logger = logging.getLogger(__name__)


class SafetyMonitor:
    """
    Orchestrates all safety checks.

    Safety checks run in parallel:
    - Constitution: Check immutable rules
    - Loop detection: Detect infinite loops
    - Hallucination: Check for AI hallucinations
    - Control: Monitor for loss of control

    Example:
        ```python
        monitor = SafetyMonitor()
        await monitor.initialize()

        result = await monitor.validate(decision, context)
        if not result.safe:
            print(f"BLOCKED: {result.get_blocking_concerns()}")
        ```
    """

    def __init__(self):
        self.constitution = ConstitutionEnforcer()
        self.loop_detector = LoopDetector()
        self.hallucination_detector = HallucinationDetector()
        self.control_monitor = ControlMonitor()

        self.initialized = False
        self.stats = {
            'validations': 0,
            'blocked': 0,
            'warnings': 0
        }

    async def initialize(self) -> None:
        """Initialize safety monitor."""
        await self.constitution.initialize()
        await self.loop_detector.initialize()
        await self.hallucination_detector.initialize()
        await self.control_monitor.initialize()

        self.initialized = True
        logger.info("SafetyMonitor initialized")

    async def validate(
        self,
        decision: Decision,
        context: FullContext
    ) -> SafetyResult:
        """
        Validate decision safety.

        Args:
            decision: Decision to validate
            context: Full context

        Returns:
            SafetyResult: Validation result

        Example:
            ```python
            result = await monitor.validate(decision, context)
            if result.safe:
                # Execute decision
                pass
            else:
                # Block execution
                for concern in result.get_blocking_concerns():
                    print(f"Safety concern: {concern.description}")
            ```
        """
        logger.debug("Running safety validation...")
        self.stats['validations'] += 1

        concerns: List[SafetyConcern] = []

        # 1. Constitution check
        constitution_result = await self.constitution.validate(decision, context)
        if not constitution_result.safe:
            concerns.extend(constitution_result.concerns)
            logger.warning("Constitution check FAILED")

        # 2. Loop detection
        loop_result = await self.loop_detector.check(decision, context)
        if not loop_result.safe:
            concerns.extend(loop_result.concerns)
            logger.warning("Loop detected")

        # 3. Hallucination detection
        hallucination_result = await self.hallucination_detector.check(decision)
        if not hallucination_result.safe:
            concerns.extend(hallucination_result.concerns)
            logger.warning("Potential hallucination detected")

        # 4. Control monitoring
        control_result = await self.control_monitor.check(decision, context)
        if not control_result.safe:
            concerns.extend(control_result.concerns)
            logger.warning("Control concern detected")

        # Aggregate results
        result = SafetyResult(
            safe=len([c for c in concerns if c.severity in ['critical', 'high']]) == 0,
            concerns=concerns,
            constitution_check=constitution_result.safe,
            loop_check=loop_result.safe,
            hallucination_check=hallucination_result.safe
        )

        # Update stats
        if not result.safe:
            self.stats['blocked'] += 1
            logger.error(f"Safety validation FAILED: {len(concerns)} concerns")
        elif len(concerns) > 0:
            self.stats['warnings'] += 1
            logger.warning(f"Safety validation passed with {len(concerns)} warnings")
        else:
            logger.info(" Safety validation passed")

        return result

    def get_stats(self) -> dict:
        """Get safety statistics."""
        return self.stats
