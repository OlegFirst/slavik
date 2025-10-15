"""
ACE Integration Helper
======================

Universal ACE integration for all platform modules.

Usage:
    from shared.ace_integration import ACEIntegration

    ace = ACEIntegration(module_name="scenario_intelligence")

    # Option 1: Full workflow
    result = await ace.execute_with_learning(
        task_type="scenario_generation_L1",
        base_context={"module": "bia"},
        execute_fn=my_task_function
    )

    # Option 2: Manual control
    context = await ace.generate_context("task_type", base_context)
    result = await my_task(context)
    await ace.reflect_and_curate("task_type", trajectory, result)
"""

import os
import logging
from typing import Dict, Any, Callable, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ACEIntegration:
    """
    Universal ACE Integration for all platform modules

    Automatically integrates continuous learning via ACE Service
    """

    def __init__(self, module_name: str, ace_url: Optional[str] = None):
        """
        Initialize ACE Integration

        Args:
            module_name: Name of the module (e.g., 'scenario_intelligence')
            ace_url: ACE Service URL (default: from env or localhost:8060)
        """
        self.module_name = module_name
        self.ace_url = ace_url or os.getenv('ACE_SERVICE_URL', 'http://localhost:8060')
        self.enabled = os.getenv('ACE_ENABLED', 'true').lower() == 'true'
        self.client = None

        if self.enabled:
            try:
                # Lazy import to avoid dependency issues
                import sys
                sys.path.insert(0, '/Users/MD/AI-Platform-ISO')
                from infrastructure.ace_service.ace_client import ACEClient

                self.client = ACEClient(base_url=self.ace_url)
                logger.info(f"✅ ACE Integration enabled for {module_name}")
            except Exception as e:
                logger.warning(f"⚠️  ACE Integration disabled: {e}")
                self.enabled = False
        else:
            logger.info(f"ACE Integration disabled for {module_name} (ACE_ENABLED=false)")

    async def execute_with_learning(
        self,
        task_type: str,
        base_context: Dict[str, Any],
        execute_fn: Callable,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute task with full ACE learning workflow

        Steps:
        1. Generate enhanced context from playbook
        2. Execute task
        3. Reflect on trajectory
        4. Curate playbook

        Args:
            task_type: Task identifier (e.g., "scenario_generation_L1")
            base_context: Base context for task
            execute_fn: Async function to execute the task
            **kwargs: Additional arguments for execute_fn

        Returns:
            Task result with ACE metadata
        """
        if not self.enabled or not self.client:
            # Execute without ACE
            return await execute_fn(base_context, **kwargs)

        try:
            return await self.client.ace_workflow(
                task_type=task_type,
                base_context=base_context,
                execute_task_fn=execute_fn,
                module_name=self.module_name,
                **kwargs
            )
        except Exception as e:
            logger.error(f"ACE workflow error, falling back: {e}")
            # Fallback to executing without ACE
            return await execute_fn(base_context, **kwargs)

    async def generate_context(
        self,
        task_type: str,
        base_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate enhanced context with playbook strategies

        Args:
            task_type: Task identifier
            base_context: Base context

        Returns:
            Enhanced context with playbook knowledge
        """
        if not self.enabled or not self.client:
            return base_context

        try:
            return await self.client.generate_context(
                task_type=task_type,
                base_context=base_context,
                module_name=self.module_name
            )
        except Exception as e:
            logger.error(f"ACE generate_context error: {e}")
            return base_context

    async def reflect_and_curate(
        self,
        task_type: str,
        trajectory: Dict[str, Any],
        result: Dict[str, Any]
    ):
        """
        Reflect on execution and curate playbook

        Args:
            task_type: Task identifier
            trajectory: Execution trajectory
            result: Task result
        """
        if not self.enabled or not self.client:
            return

        try:
            # Reflect
            insights = await self.client.reflect_on_trajectory(
                task_type=task_type,
                trajectory=trajectory,
                module_name=self.module_name
            )

            # Curate
            await self.client.curate_playbook(
                task_type=task_type,
                insights=insights,
                module_name=self.module_name
            )
        except Exception as e:
            logger.error(f"ACE reflect_and_curate error: {e}")

    async def get_playbook_stats(self, task_type: str) -> Optional[Dict[str, Any]]:
        """Get statistics for specific playbook"""
        if not self.enabled or not self.client:
            return None

        try:
            return await self.client.get_playbook_stats(
                task_type=task_type,
                module_name=self.module_name
            )
        except Exception as e:
            logger.error(f"Error fetching playbook stats: {e}")
            return None

    async def close(self):
        """Close ACE client connection"""
        if self.client:
            try:
                await self.client.close()
            except Exception as e:
                logger.error(f"Error closing ACE client: {e}")


# ============================================================================
# Convenience Functions
# ============================================================================

_ace_instances: Dict[str, ACEIntegration] = {}


def get_ace_integration(module_name: str) -> ACEIntegration:
    """
    Get or create ACE Integration instance for module

    Args:
        module_name: Module name

    Returns:
        ACEIntegration instance
    """
    if module_name not in _ace_instances:
        _ace_instances[module_name] = ACEIntegration(module_name)

    return _ace_instances[module_name]


async def execute_with_ace(
    module_name: str,
    task_type: str,
    base_context: Dict[str, Any],
    execute_fn: Callable,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to execute task with ACE learning

    Usage:
        from shared.ace_integration import execute_with_ace

        result = await execute_with_ace(
            module_name="scenario_intelligence",
            task_type="scenario_generation_L1",
            base_context={"module": "bia"},
            execute_fn=generate_scenario
        )
    """
    ace = get_ace_integration(module_name)
    return await ace.execute_with_learning(task_type, base_context, execute_fn, **kwargs)
