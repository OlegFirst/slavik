#!/usr/bin/env python3
"""
Temporal Worker for MIO Manager v2.0
=====================================

Runs Temporal Worker that executes MIO Manager workflows.

Workflows:
- ObservationWorkflow (continuous monitoring)
- ReactionWorkflow (automated response)
- ReportingWorkflow (scheduled reports)
- ControlWorkflow (task monitoring)

Activities:
- discover_services
- analyze_problems
- execute_action
- publish_problems_to_eventbus
- generate_report
- publish_report_to_brain
- monitor_task_progress

Usage:
    python run_worker.py

Environment:
    TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, TEMPORAL_API_KEY
    (loaded from /Users/MD/AI-Platform-ISO/.env)
"""

import asyncio
import sys
from pathlib import Path
import logging

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from temporalio.worker import Worker
from client_provider import get_temporal_client

# Import workflows
from temporal_workflows.observation_workflow import (
    ObservationWorkflow,
    discover_services,
    analyze_problems,
    publish_problems_to_eventbus
)
from temporal_workflows.reaction_workflow import (
    ReactionWorkflow,
    classify_problem,
    execute_action,
    escalate_to_brain
)
from temporal_workflows.reporting_workflow import (
    ReportingWorkflow,
    generate_report,
    publish_report_to_brain
)
from temporal_workflows.control_workflow import (
    ControlWorkflow,
    monitor_task_progress,
    handle_task_timeout
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Task queue name
TASK_QUEUE = "mio-manager-tasks"


async def main() -> None:
    """
    Run Temporal Worker for MIO Manager.

    Registers all workflows and activities, then runs the worker.
    """
    logger.info("🚀 Starting MIO Manager Temporal Worker...")

    try:
        # Connect to Temporal
        client = await get_temporal_client()
        logger.info(f"✅ Connected to Temporal")
        logger.info(f"   Namespace: {client.namespace}")
        logger.info(f"   Task Queue: {TASK_QUEUE}")

        # Create worker
        logger.info("📦 Registering workflows and activities...")

        worker = Worker(
            client,
            task_queue=TASK_QUEUE,
            workflows=[
                ObservationWorkflow,
                ReactionWorkflow,
                ReportingWorkflow,
                ControlWorkflow
            ],
            activities=[
                # ObservationWorkflow activities
                discover_services,
                analyze_problems,
                publish_problems_to_eventbus,
                # ReactionWorkflow activities
                classify_problem,
                execute_action,
                escalate_to_brain,
                # ReportingWorkflow activities
                generate_report,
                publish_report_to_brain,
                # ControlWorkflow activities
                monitor_task_progress,
                handle_task_timeout
            ]
        )

        logger.info("✅ Worker configured")
        logger.info("   Workflows:")
        logger.info("     - ObservationWorkflow (continuous monitoring)")
        logger.info("     - ReactionWorkflow (automated response)")
        logger.info("     - ReportingWorkflow (scheduled reports)")
        logger.info("     - ControlWorkflow (task monitoring)")
        logger.info("   Activities: 10 registered")

        # Run worker (blocks until interrupted)
        logger.info("🏃 Worker running... (Ctrl+C to stop)")
        await worker.run()

    except KeyboardInterrupt:
        logger.info("\n👋 Worker stopped by user")

    except Exception as e:
        logger.error(f"❌ Worker failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
