#!/usr/bin/env python3
"""
Temporal Worker for Coordination Center Workflows
==================================================

Runs Coordination, CrossService, and ParallelTask workflows.

Setup:
1. Install: pip install temporalio httpx
2. Start Temporal: temporal server start-dev
3. Start Coordination Center: cd coordination-center && python main.py
4. Run this worker: python coordination_worker.py

Configuration:
- TEMPORAL_ADDRESS: Temporal server address (default: localhost:7233)
- TEMPORAL_NAMESPACE: Namespace (default: default)
- TEMPORAL_TASK_QUEUE: Task queue name (default: coordination-queue)
- COORDINATION_CENTER_URL: Coordination Center URL (default: http://localhost:8004)
- MAX_CONCURRENT_ACTIVITIES: Max concurrent activities (default: 100)
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from temporalio.client import Client
from temporalio.worker import Worker

# Import workflows and activities
from intelligent_core.workflow_intelligence.temporal_workflows.coordination_workflow import (
    CoordinationWorkflow,
    CrossServiceWorkflow,
    ParallelTaskWorkflow,
    coordination_activities,
    inject_dependencies
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Run Coordination Worker"""

    # Configuration from environment
    temporal_address = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
    temporal_namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
    task_queue = os.getenv("TEMPORAL_TASK_QUEUE", "coordination-queue")
    coordination_center_url = os.getenv("COORDINATION_CENTER_URL", "http://localhost:8004")
    max_concurrent_activities = int(os.getenv("MAX_CONCURRENT_ACTIVITIES", "100"))

    logger.info("="*60)
    logger.info("COORDINATION CENTER TEMPORAL WORKER")
    logger.info("="*60)
    logger.info(f"Temporal Address: {temporal_address}")
    logger.info(f"Namespace: {temporal_namespace}")
    logger.info(f"Task Queue: {task_queue}")
    logger.info(f"Coordination Center: {coordination_center_url}")
    logger.info(f"Max Concurrent Activities: {max_concurrent_activities}")
    logger.info("="*60)

    # Inject dependencies
    logger.info("Injecting dependencies...")
    inject_dependencies(coordination_center_url=coordination_center_url)

    # Connect to Temporal
    logger.info(f"Connecting to Temporal at {temporal_address}...")
    try:
        client = await Client.connect(
            temporal_address,
            namespace=temporal_namespace
        )
        logger.info("✅ Connected to Temporal")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Temporal: {e}")
        logger.error("   Make sure Temporal server is running:")
        logger.error("   > temporal server start-dev")
        return

    # Verify Coordination Center is reachable
    logger.info(f"Checking Coordination Center at {coordination_center_url}...")
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as http_client:
            response = await http_client.get(f"{coordination_center_url}/coordination/health")
            if response.status_code == 200:
                logger.info("✅ Coordination Center is healthy")
            else:
                logger.warning(f"⚠️ Coordination Center returned {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Cannot reach Coordination Center: {e}")
        logger.error("   Make sure Coordination Center is running:")
        logger.error("   > cd intelligent-core/orchestration/coordination-center")
        logger.error("   > python main.py")
        logger.warning("   Worker will continue but workflows may fail!")

    # Create worker
    logger.info("Creating Temporal worker...")
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[
            CoordinationWorkflow,
            CrossServiceWorkflow,
            ParallelTaskWorkflow
        ],
        activities=coordination_activities,
        max_concurrent_activities=max_concurrent_activities
    )

    logger.info("="*60)
    logger.info("Worker started successfully!")
    logger.info("="*60)
    logger.info("Registered Workflows:")
    logger.info("  - CoordinationWorkflow (single intent execution)")
    logger.info("  - CrossServiceWorkflow (multi-service coordination)")
    logger.info("  - ParallelTaskWorkflow (parallel bulk operations)")
    logger.info("")
    logger.info("Registered Activities:")
    logger.info("  - intent_execution")
    logger.info("  - task_distribution")
    logger.info("  - service_coordination")
    logger.info("  - status_aggregation")
    logger.info("  - conflict_resolution")
    logger.info("  - approval_request")
    logger.info("  - rollback_execution")
    logger.info("="*60)
    logger.info("🔄 Worker is now polling for tasks...")
    logger.info("   Press Ctrl+C to stop")
    logger.info("="*60)

    # Run worker
    try:
        await worker.run()
    except KeyboardInterrupt:
        logger.info("\n⏹️ Worker stopped by user")
    except Exception as e:
        logger.error(f"❌ Worker error: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Goodbye!")
