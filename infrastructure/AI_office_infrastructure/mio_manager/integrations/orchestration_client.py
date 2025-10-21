#!/usr/bin/env python3
"""
Orchestration Client - Интеграция с AI Orchestration
====================================================

Подключает MIO Manager к intelligent-core/orchestration для:
- AI task planning (ai-orchestration)
- Task coordination (coordination-center)

Это дополнительный клиент к orchestrator_client.py.

orchestrator_client.py → Infrastructure Orchestrator (execution)
orchestration_client.py → AI Orchestration (planning/coordination)

ВОПРОСЫ ДЛЯ ОБСУЖДЕНИЯ:
========================

1. Нужен ли этот клиент MIO Manager?
   - Или это лишняя связь?
   - Какова правильная архитектура?

2. Роль AI Orchestration:
   - Кто должен его вызывать?
   - MIO Manager или кто-то другой?
"""

import httpx
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class OrchestrationClient:
    """
    Client для взаимодействия с AI Orchestration components.

    Integrates with:
    1. ai-orchestration (Port 8060) - AI task planning
    2. coordination-center (Port 8065) - Task coordination
    """

    def __init__(
        self,
        ai_orchestration_url: str = "http://localhost:8060",
        coordination_center_url: str = "http://localhost:8065"
    ):
        self.ai_orchestration_url = ai_orchestration_url
        self.coordination_center_url = coordination_center_url
        self.client = httpx.AsyncClient(timeout=30.0)

    # ========================================================================
    # AI Orchestration - Intelligent Task Planning
    # ========================================================================

    async def plan_task(self, task_description: Dict) -> Dict:
        """
        Request AI-powered task planning.

        AI Orchestration analyzes task and creates execution plan:
        - Resource optimization
        - Priority assessment
        - Dependency resolution
        - Intelligent routing

        Args:
            task_description: Task details
                - type: Task type
                - description: Human description
                - context: Task context
                - constraints: Constraints

        Returns:
            Execution plan with steps, priorities, resources
        """
        logger.info(f" Requesting AI task planning: {task_description.get('type')}")

        try:
            response = await self.client.post(
                f"{self.ai_orchestration_url}/api/v1/plan",
                json=task_description
            )

            if response.status_code == 200:
                plan = response.json()
                logger.info(f" Task plan created: {len(plan.get('steps', []))} steps")
                return {
                    'success': True,
                    'plan': plan
                }
            else:
                return {
                    'success': False,
                    'error': f'AI Orchestration returned {response.status_code}'
                }

        except Exception as e:
            logger.error(f" Task planning failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def optimize_resources(self, tasks: List[Dict]) -> Dict:
        """
        Request resource optimization for multiple tasks.

        AI Orchestration analyzes tasks and optimizes:
        - Parallel execution opportunities
        - Resource allocation
        - Load balancing
        - Scheduling

        Args:
            tasks: List of tasks to optimize

        Returns:
            Optimized execution schedule
        """
        logger.info(f" Requesting resource optimization for {len(tasks)} tasks")

        try:
            response = await self.client.post(
                f"{self.ai_orchestration_url}/api/v1/optimize",
                json={'tasks': tasks}
            )

            if response.status_code == 200:
                schedule = response.json()
                logger.info(f" Optimized schedule created")
                return {
                    'success': True,
                    'schedule': schedule
                }
            else:
                return {
                    'success': False,
                    'error': f'Optimization failed: {response.status_code}'
                }

        except Exception as e:
            logger.error(f" Resource optimization failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def assess_priority(self, task: Dict, context: Dict) -> Dict:
        """
        Request AI priority assessment.

        AI Orchestration evaluates task priority based on:
        - Business impact
        - Urgency
        - Dependencies
        - Current platform state

        Args:
            task: Task to assess
            context: Platform context (alerts, metrics, etc.)

        Returns:
            Priority assessment with score and reasoning
        """
        logger.info(f" Requesting priority assessment")

        try:
            response = await self.client.post(
                f"{self.ai_orchestration_url}/api/v1/priority",
                json={
                    'task': task,
                    'context': context
                }
            )

            if response.status_code == 200:
                assessment = response.json()
                logger.info(f" Priority: {assessment.get('priority_score')}")
                return {
                    'success': True,
                    'assessment': assessment
                }
            else:
                return {
                    'success': False,
                    'error': f'Priority assessment failed: {response.status_code}'
                }

        except Exception as e:
            logger.error(f" Priority assessment failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # Coordination Center - Cross-Service Coordination
    # ========================================================================

    async def coordinate_workflow(self, workflow: Dict) -> Dict:
        """
        Request workflow coordination.

        Coordination Center manages:
        - Cross-service orchestration
        - State management
        - Workflow execution
        - Error recovery

        Args:
            workflow: Workflow definition
                - workflow_id: Workflow ID
                - steps: List of workflow steps
                - services: Involved services

        Returns:
            Coordination result
        """
        logger.info(f" Requesting workflow coordination: {workflow.get('workflow_id')}")

        try:
            response = await self.client.post(
                f"{self.coordination_center_url}/api/v1/coordinate",
                json=workflow
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f" Workflow coordination started")
                return {
                    'success': True,
                    'coordination': result
                }
            else:
                return {
                    'success': False,
                    'error': f'Coordination failed: {response.status_code}'
                }

        except Exception as e:
            logger.error(f" Workflow coordination failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_workflow_status(self, workflow_id: str) -> Dict:
        """
        Get workflow execution status.

        Args:
            workflow_id: Workflow ID

        Returns:
            Workflow status
        """
        try:
            response = await self.client.get(
                f"{self.coordination_center_url}/api/v1/workflows/{workflow_id}"
            )

            if response.status_code == 200:
                return {
                    'success': True,
                    'status': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'Status check failed: {response.status_code}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def track_execution(self, task_id: str) -> Dict:
        """
        Track task execution across services.

        Args:
            task_id: Task ID

        Returns:
            Execution tracking info
        """
        try:
            response = await self.client.get(
                f"{self.coordination_center_url}/api/v1/tasks/{task_id}/track"
            )

            if response.status_code == 200:
                return {
                    'success': True,
                    'tracking': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'Tracking failed: {response.status_code}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # State Management
    # ========================================================================

    async def save_state(self, workflow_id: str, state: Dict) -> Dict:
        """
        Save workflow state.

        Args:
            workflow_id: Workflow ID
            state: State to save

        Returns:
            Save result
        """
        try:
            response = await self.client.post(
                f"{self.coordination_center_url}/api/v1/workflows/{workflow_id}/state",
                json=state
            )

            if response.status_code == 200:
                return {
                    'success': True,
                    'saved': True
                }
            else:
                return {
                    'success': False,
                    'error': f'State save failed: {response.status_code}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def restore_state(self, workflow_id: str) -> Dict:
        """
        Restore workflow state.

        Args:
            workflow_id: Workflow ID

        Returns:
            Restored state
        """
        try:
            response = await self.client.get(
                f"{self.coordination_center_url}/api/v1/workflows/{workflow_id}/state"
            )

            if response.status_code == 200:
                return {
                    'success': True,
                    'state': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'State restore failed: {response.status_code}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # Health Checks
    # ========================================================================

    async def health_check(self) -> Dict:
        """
        Check health of orchestration components.

        Returns:
            Health status
        """
        results = {
            'ai_orchestration': False,
            'coordination_center': False
        }

        try:
            # Check AI Orchestration
            response = await self.client.get(
                f"{self.ai_orchestration_url}/health",
                timeout=5.0
            )
            results['ai_orchestration'] = response.status_code == 200
        except Exception:
            pass

        try:
            # Check Coordination Center
            response = await self.client.get(
                f"{self.coordination_center_url}/health",
                timeout=5.0
            )
            results['coordination_center'] = response.status_code == 200
        except Exception:
            pass

        return {
            'success': True,
            'components': results,
            'all_healthy': all(results.values())
        }

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
