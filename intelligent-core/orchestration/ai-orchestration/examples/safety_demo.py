"""
Safety System Demo
==================

Demonstrates safety monitoring features.
"""

import asyncio
import logging
from .models import (
    Decision, FullContext, ActionType, PriorityLevel
)
from .safety import (
    SafetyMonitor, ConstitutionEnforcer, LoopDetector,
    HallucinationDetector, ControlMonitor
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def demo_constitution():
    """Demonstrate constitution enforcement."""
    logger.info("\n=== Constitution Enforcement Demo ===")

    enforcer = ConstitutionEnforcer()
    await enforcer.initialize()

    # Show constitution rules
    logger.info("Constitution Rules:")
    for rule in enforcer.get_constitution():
        logger.info(f"  - {rule['rule']} (severity: {rule['severity']})")

    # Test 1: Low confidence without escalation (SHOULD BLOCK)
    logger.info("\nTest 1: Low confidence without escalation")
    decision1 = Decision(
        action=ActionType.AUTO_RESOLVE,
        rationale="Trying to auto-resolve",
        priority=PriorityLevel.MEDIUM,
        confidence=0.5  # Below 0.7 threshold
    )

    context = FullContext(
        platform_state={},
        workflows=[],
        recent_events=[],
        similar_situations=[]
    )

    result1 = await enforcer.validate(decision1, context)
    logger.info(f"Safe: {result1.safe}")
    if not result1.safe:
        for concern in result1.concerns:
            logger.warning(f"  ⚠️  {concern.description}")

    # Test 2: High confidence (SHOULD PASS)
    logger.info("\nTest 2: High confidence")
    decision2 = Decision(
        action=ActionType.AUTO_RESOLVE,
        rationale="Auto-resolving with high confidence",
        priority=PriorityLevel.MEDIUM,
        confidence=0.95
    )

    result2 = await enforcer.validate(decision2, context)
    logger.info(f"Safe: {result2.safe} ✅")


async def demo_loop_detection():
    """Demonstrate loop detection."""
    logger.info("\n=== Loop Detection Demo ===")

    detector = LoopDetector()
    await detector.initialize()

    # Simulate repeated actions
    decision = Decision(
        action=ActionType.WAIT_AND_MONITOR,
        rationale="Waiting...",
        priority=PriorityLevel.LOW,
        confidence=0.8
    )

    context = FullContext(
        platform_state={},
        workflows=[],
        recent_events=[],
        similar_situations=[]
    )

    logger.info("Simulating repeated actions...")
    for i in range(6):
        result = await detector.check(decision, context)
        logger.info(f"  Iteration {i+1}: Safe={result.safe}")

        if not result.safe:
            for concern in result.concerns:
                logger.warning(f"  🔄 LOOP DETECTED: {concern.description}")
            break


async def demo_full_safety_monitor():
    """Demonstrate full safety monitoring."""
    logger.info("\n=== Full Safety Monitor Demo ===")

    monitor = SafetyMonitor()
    await monitor.initialize()

    # Safe decision
    logger.info("\nTest 1: Safe decision")
    decision1 = Decision(
        action=ActionType.DELEGATE,
        rationale="Delegating to specialist",
        priority=PriorityLevel.MEDIUM,
        confidence=0.85
    )

    context = FullContext(
        platform_state={'status': 'operational'},
        workflows=[],
        recent_events=[],
        similar_situations=[]
    )

    result1 = await monitor.validate(decision1, context)
    logger.info(f"Overall safe: {result1.safe} ✅")
    logger.info(f"  Constitution: {result1.constitution_check}")
    logger.info(f"  Loop check: {result1.loop_check}")
    logger.info(f"  Hallucination check: {result1.hallucination_check}")

    # Unsafe decision
    logger.info("\nTest 2: Unsafe decision (low confidence)")
    decision2 = Decision(
        action=ActionType.AUTO_RESOLVE,
        rationale="Trying to auto-resolve",
        priority=PriorityLevel.CRITICAL,
        confidence=0.3
    )

    result2 = await monitor.validate(decision2, context)
    logger.info(f"Overall safe: {result2.safe}")
    if not result2.safe:
        logger.warning("  ⚠️  Safety concerns detected:")
        for concern in result2.get_blocking_concerns():
            logger.warning(f"    - {concern.description}")


async def main():
    """Run all safety demos."""
    logger.info("=== AI Orchestrator Safety System Demo ===")

    await demo_constitution()
    await demo_loop_detection()
    await demo_full_safety_monitor()

    logger.info("\n=== Demo Complete ===")


if __name__ == '__main__':
    asyncio.run(main())
