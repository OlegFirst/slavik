"""
ACE Client Library
==================

Клиентская библиотека для использования ACE Service из любого модуля платформы.

Usage:
    from infrastructure.ace_service.ace_client import ACEClient

    ace = ACEClient()

    # Generate enhanced context
    context = await ace.generate_context(
        task_type="scenario_generation_L1",
        base_context={"module": "bia", "operation": "assess"}
    )

    # Reflect on trajectory
    insights = await ace.reflect_on_trajectory(
        task_type="scenario_generation_L1",
        trajectory={...}
    )

    # Curate playbook
    playbook = await ace.curate_playbook(
        task_type="scenario_generation_L1",
        insights=insights
    )
"""

import os
import logging
from typing import Dict, Any, Optional, List
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)


class ACEClient:
    """Client for ACE Service"""

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize ACE Client

        Args:
            base_url: ACE Service URL (default: from env or localhost:8050)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or os.getenv(
            'ACE_SERVICE_URL',
            'http://localhost:8050'
        )
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None

        logger.info(f"ACE Client initialized: {self.base_url}")

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def _ensure_session(self):
        """Ensure session is created"""
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=self.timeout)

    async def close(self):
        """Close client session"""
        if self.session:
            await self.session.close()
            self.session = None

    # ========================================================================
    # Core ACE Methods
    # ========================================================================

    async def generate_context(
        self,
        task_type: str,
        base_context: Dict[str, Any],
        module_name: Optional[str] = None,
        domain_knowledge: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate enhanced context with evolving playbook (GENERATOR)

        Args:
            task_type: Task type identifier
            base_context: Base context dictionary
            module_name: Optional module name
            domain_knowledge: Optional domain knowledge

        Returns:
            Enhanced context with playbook strategies, patterns, knowledge
        """
        await self._ensure_session()

        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/ace/generate-context",
                json={
                    "task_type": task_type,
                    "base_context": base_context,
                    "module_name": module_name,
                    "domain_knowledge": domain_knowledge
                }
            ) as response:
                response.raise_for_status()
                data = await response.json()

                if data.get('success'):
                    return data.get('enhanced_context', base_context)
                else:
                    logger.warning(f"ACE generation failed, using base context")
                    return base_context

        except Exception as e:
            logger.error(f"ACE generate_context error: {e}")
            # Fallback to base context
            return base_context

    async def reflect_on_trajectory(
        self,
        task_type: str,
        trajectory: Dict[str, Any],
        module_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze trajectory and identify insights (REFLECTOR)

        Args:
            task_type: Task type
            trajectory: Execution trajectory
            module_name: Optional module name

        Returns:
            Insights dictionary
        """
        await self._ensure_session()

        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/ace/reflect",
                json={
                    "task_type": task_type,
                    "trajectory": trajectory,
                    "module_name": module_name
                }
            ) as response:
                response.raise_for_status()
                data = await response.json()

                if data.get('success'):
                    return data.get('insights', {})
                else:
                    return {}

        except Exception as e:
            logger.error(f"ACE reflect error: {e}")
            return {}

    async def curate_playbook(
        self,
        task_type: str,
        insights: Dict[str, Any],
        module_name: Optional[str] = None,
        preserve_knowledge: bool = True
    ) -> Dict[str, Any]:
        """
        Update playbook incrementally (CURATOR)

        Args:
            task_type: Task type
            insights: Insights from reflector
            module_name: Optional module name
            preserve_knowledge: Preserve existing knowledge

        Returns:
            Updated playbook
        """
        await self._ensure_session()

        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/ace/curate",
                json={
                    "task_type": task_type,
                    "insights": insights,
                    "module_name": module_name,
                    "preserve_knowledge": preserve_knowledge
                }
            ) as response:
                response.raise_for_status()
                data = await response.json()

                if data.get('success'):
                    return data.get('playbook', {})
                else:
                    return {}

        except Exception as e:
            logger.error(f"ACE curate error: {e}")
            return {}

    # ========================================================================
    # Helper Methods - Full ACE Workflow
    # ========================================================================

    async def ace_workflow(
        self,
        task_type: str,
        base_context: Dict[str, Any],
        execute_task_fn,
        module_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute full ACE workflow:
        1. Generate enhanced context
        2. Execute task
        3. Reflect on trajectory
        4. Curate playbook

        Args:
            task_type: Task type
            base_context: Base context
            execute_task_fn: Async function to execute task
            module_name: Optional module name
            **kwargs: Additional arguments for task execution

        Returns:
            Task result with ACE metadata
        """
        start_time = datetime.utcnow()

        try:
            # 1. GENERATOR - Enhanced context
            enhanced_context = await self.generate_context(
                task_type=task_type,
                base_context=base_context,
                module_name=module_name
            )

            # 2. EXECUTE - Run task with enhanced context
            result = await execute_task_fn(enhanced_context, **kwargs)

            # 3. REFLECTOR - Analyze trajectory
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            trajectory = {
                'input_context': enhanced_context,
                'output_result': result,
                'execution_time_ms': execution_time,
                'success': result.get('success', False),
                'effectiveness': result.get('effectiveness', 0.8),
                'validation': result.get('validation', {}),
                'metadata': result.get('metadata', {})
            }

            insights = await self.reflect_on_trajectory(
                task_type=task_type,
                trajectory=trajectory,
                module_name=module_name
            )

            # 4. CURATOR - Update playbook
            updated_playbook = await self.curate_playbook(
                task_type=task_type,
                insights=insights,
                module_name=module_name
            )

            # Add ACE metadata to result
            result['ace_metadata'] = {
                'playbook_updated': True,
                'insights': insights,
                'strategies_count': len(updated_playbook.get('strategies', [])),
                'patterns_count': len(updated_playbook.get('patterns', []))
            }

            return result

        except Exception as e:
            logger.error(f"ACE workflow error: {e}")
            # Return result without ACE enhancement
            return {
                'success': False,
                'error': str(e),
                'ace_metadata': {
                    'playbook_updated': False,
                    'error': 'ACE workflow failed'
                }
            }

    # ========================================================================
    # Monitoring & Analytics
    # ========================================================================

    async def get_playbook_stats(
        self,
        task_type: str,
        module_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get statistics for specific playbook"""
        await self._ensure_session()

        try:
            params = {}
            if module_name:
                params['module_name'] = module_name

            async with self.session.get(
                f"{self.base_url}/api/v1/ace/playbook/{task_type}/stats",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('stats')
                else:
                    return None

        except Exception as e:
            logger.error(f"Error fetching playbook stats: {e}")
            return None

    async def get_all_playbooks(self) -> List[Dict[str, Any]]:
        """Get statistics for all playbooks"""
        await self._ensure_session()

        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/ace/playbooks"
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get('playbooks', [])

        except Exception as e:
            logger.error(f"Error fetching all playbooks: {e}")
            return []

    async def get_analytics(self) -> Dict[str, Any]:
        """Get ACE analytics and monitoring data"""
        await self._ensure_session()

        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/ace/analytics"
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get('analytics', {})

        except Exception as e:
            logger.error(f"Error fetching analytics: {e}")
            return {}

    async def health_check(self) -> bool:
        """Check if ACE Service is healthy"""
        await self._ensure_session()

        try:
            async with self.session.get(
                f"{self.base_url}/health"
            ) as response:
                return response.status == 200

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# ============================================================================
# Singleton Pattern
# ============================================================================

_ace_client: Optional[ACEClient] = None


def get_ace_client(base_url: Optional[str] = None) -> ACEClient:
    """
    Get global ACE Client instance

    Args:
        base_url: Optional ACE Service URL

    Returns:
        ACEClient instance
    """
    global _ace_client

    if _ace_client is None:
        _ace_client = ACEClient(base_url=base_url)

    return _ace_client


# ============================================================================
# Convenience Functions
# ============================================================================

async def generate_context(
    task_type: str,
    base_context: Dict[str, Any],
    module_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function for generating enhanced context

    Usage:
        from infrastructure.ace_service.ace_client import generate_context

        context = await generate_context(
            task_type="scenario_generation",
            base_context={"module": "bia"}
        )
    """
    client = get_ace_client()
    return await client.generate_context(task_type, base_context, module_name)


async def ace_workflow(
    task_type: str,
    base_context: Dict[str, Any],
    execute_task_fn,
    module_name: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for full ACE workflow

    Usage:
        from infrastructure.ace_service.ace_client import ace_workflow

        async def my_task(context):
            # Your task implementation
            return {"success": True, "result": "..."}

        result = await ace_workflow(
            task_type="my_task",
            base_context={"input": "..."},
            execute_task_fn=my_task
        )
    """
    client = get_ace_client()
    return await client.ace_workflow(
        task_type, base_context, execute_task_fn, module_name, **kwargs
    )
