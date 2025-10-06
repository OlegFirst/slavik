"""
Basic Usage Example
===================

Demonstrates basic AI Orchestrator usage.
"""

import asyncio
import logging
from intelligent_core.ai_orchestration import AIOrchestrator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Basic orchestrator usage example."""

    # Create orchestrator
    logger.info("Creating AI Orchestrator...")
    orchestrator = AIOrchestrator(
        event_bus_backend='memory',  # Use in-memory event bus for demo
        enable_evolution=False,      # Disable evolution for demo
        enable_safety=True           # Enable safety monitoring
    )

    # Initialize
    logger.info("Initializing orchestrator...")
    await orchestrator.initialize()

    # Example 1: Workflow stuck
    logger.info("\n=== Example 1: Workflow Stuck ===")
    situation1 = {
        'workflow_stuck': True,
        'workflow_id': 'bia_001',
        'stuck_duration_minutes': 30,
        'error_message': 'Timeout waiting for user input'
    }

    decision1 = await orchestrator.decide(situation1, tenant_id='demo_tenant')
    logger.info(f"Decision: {decision1.action.value}")
    logger.info(f"Rationale: {decision1.rationale}")
    logger.info(f"Confidence: {decision1.confidence:.2f}")
    logger.info(f"Priority: {decision1.priority.name}")

    # Execute decision
    result1 = await orchestrator.execute(decision1)
    logger.info(f"Execution result: {result1}")

    # Example 2: High priority situation
    logger.info("\n=== Example 2: High Priority Situation ===")
    situation2 = {
        'platform_status': 'degraded',
        'affected_workflows': 15,
        'error_rate': 0.25
    }

    decision2 = await orchestrator.decide(situation2, tenant_id='demo_tenant')
    logger.info(f"Decision: {decision2.action.value}")
    logger.info(f"Rationale: {decision2.rationale}")
    logger.info(f"Confidence: {decision2.confidence:.2f}")
    logger.info(f"Priority: {decision2.priority.name}")

    # Example 3: Low confidence - should escalate
    logger.info("\n=== Example 3: Low Confidence (Safety Check) ===")
    situation3 = {
        'unknown_error': True,
        'error_type': 'mysterious',
        'first_occurrence': True
    }

    decision3 = await orchestrator.decide(situation3, tenant_id='demo_tenant')
    logger.info(f"Decision: {decision3.action.value}")
    logger.info(f"Rationale: {decision3.rationale}")
    logger.info(f"Confidence: {decision3.confidence:.2f}")
    logger.info(f"Safety approved: {decision3.safety_approved}")

    # Get statistics
    logger.info("\n=== Orchestrator Statistics ===")
    stats = orchestrator.get_stats()
    logger.info(f"Total decisions made: {stats['decisions_made']}")
    logger.info(f"Auto-resolved: {stats['auto_resolved']}")
    logger.info(f"Delegated: {stats['delegated']}")
    logger.info(f"Escalated to human: {stats['escalated_to_human']}")
    logger.info(f"Safety blocks: {stats['safety_blocks']}")

    # Shutdown
    logger.info("\n=== Shutting down ===")
    await orchestrator.shutdown()
    logger.info("Orchestrator shut down successfully")


if __name__ == '__main__':
    asyncio.run(main())
