#!/usr/bin/env python3
"""
Coordination Center Client
===========================

Интеграция MIO Manager с Coordination Center для делегирования задач.

Coordination Center координирует выполнение задач между различными
агентами и сервисами платформы.

Использование:
- Делегирование задач из ControlWorkflow
- Отслеживание статуса выполнения
- Координация между несколькими исполнителями
"""

import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CoordinationCenterClient:
    """
    Клиент для взаимодействия с Coordination Center.

    Coordination Center предоставляет:
    - Task delegation (делегирование задач агентам)
    - Task tracking (отслеживание прогресса)
    - Multi-agent coordination (координация между агентами)
    - Conflict resolution (разрешение конфликтов)
    """

    def __init__(self, coordination_url: str = "http://localhost:8053"):
        """
        Args:
            coordination_url: URL Coordination Center
        """
        self.base_url = coordination_url
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"CoordinationCenterClient initialized: {coordination_url}")

    async def delegate_task(
        self,
        task_type: str,
        task_data: Dict[str, Any],
        priority: str = 'medium',
        preferred_agents: Optional[List[str]] = None,
        deadline: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Делегировать задачу Coordination Center.

        Args:
            task_type: Тип задачи (fix_issue, analyze, optimize, etc.)
            task_data: Данные задачи
            priority: Приоритет (low, medium, high, critical)
            preferred_agents: Список предпочтительных агентов (опционально)
            deadline: Дедлайн выполнения (ISO format)

        Returns:
            {
                'task_id': 'TASK-20251008-001',
                'status': 'delegated',
                'assigned_to': 'agent_name',
                'estimated_completion': '2025-10-08T12:00:00Z',
                'tracking_url': '/tasks/TASK-20251008-001'
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/tasks/delegate",
                json={
                    'task_type': task_type,
                    'task_data': task_data,
                    'priority': priority,
                    'preferred_agents': preferred_agents or [],
                    'deadline': deadline,
                    'delegated_by': 'mio_manager',
                    'delegated_at': datetime.utcnow().isoformat()
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                f" Task delegated: {result.get('task_id')} → {result.get('assigned_to')}"
            )

            return result

        except httpx.HTTPStatusError as e:
            logger.error(f"Coordination Center error {e.response.status_code}: {e}")
            return {
                'task_id': None,
                'status': 'failed',
                'error': f"HTTP {e.response.status_code}"
            }

        except Exception as e:
            logger.error(f"Failed to delegate task: {e}")
            return {
                'task_id': None,
                'status': 'failed',
                'error': str(e)
            }

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Получить статус задачи.

        Args:
            task_id: ID задачи

        Returns:
            {
                'task_id': 'TASK-20251008-001',
                'status': 'in_progress',  # pending, in_progress, completed, failed
                'progress': 0.65,  # 0.0 - 1.0
                'assigned_to': 'agent_name',
                'started_at': '2025-10-08T10:00:00Z',
                'last_update': '2025-10-08T11:30:00Z',
                'result': None  # или результат если completed
            }
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/tasks/{task_id}/status"
            )
            response.raise_for_status()
            result = response.json()

            logger.debug(f"Task {task_id} status: {result.get('status')}")

            return result

        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            return {
                'task_id': task_id,
                'status': 'unknown',
                'error': str(e)
            }

    async def update_task_progress(
        self,
        task_id: str,
        progress: float,
        status_message: Optional[str] = None
    ) -> bool:
        """
        Обновить прогресс задачи.

        Args:
            task_id: ID задачи
            progress: Прогресс 0.0 - 1.0
            status_message: Сообщение о статусе

        Returns:
            True если успешно
        """
        try:
            response = await self.client.put(
                f"{self.base_url}/api/tasks/{task_id}/progress",
                json={
                    'progress': progress,
                    'status_message': status_message,
                    'updated_by': 'mio_manager',
                    'updated_at': datetime.utcnow().isoformat()
                }
            )
            response.raise_for_status()

            logger.debug(f"Updated task {task_id} progress: {progress*100:.0f}%")

            return True

        except Exception as e:
            logger.error(f"Failed to update task progress: {e}")
            return False

    async def cancel_task(
        self,
        task_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Отменить задачу.

        Args:
            task_id: ID задачи
            reason: Причина отмены

        Returns:
            {
                'task_id': 'TASK-20251008-001',
                'status': 'cancelled',
                'cancelled_at': '2025-10-08T12:00:00Z'
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/tasks/{task_id}/cancel",
                json={
                    'reason': reason,
                    'cancelled_by': 'mio_manager',
                    'cancelled_at': datetime.utcnow().isoformat()
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f" Task {task_id} cancelled: {reason}")

            return result

        except Exception as e:
            logger.error(f"Failed to cancel task: {e}")
            return {'error': str(e)}

    async def list_active_tasks(
        self,
        assigned_to: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Получить список активных задач.

        Args:
            assigned_to: Фильтр по агенту (опционально)
            priority: Фильтр по приоритету (опционально)

        Returns:
            [
                {
                    'task_id': 'TASK-20251008-001',
                    'task_type': 'fix_issue',
                    'status': 'in_progress',
                    'priority': 'high',
                    'assigned_to': 'agent_name',
                    'progress': 0.45
                }
            ]
        """
        try:
            params = {}
            if assigned_to:
                params['assigned_to'] = assigned_to
            if priority:
                params['priority'] = priority

            response = await self.client.get(
                f"{self.base_url}/api/tasks/active",
                params=params
            )
            response.raise_for_status()
            tasks = response.json()

            logger.info(f"Retrieved {len(tasks)} active tasks")

            return tasks

        except Exception as e:
            logger.error(f"Failed to list active tasks: {e}")
            return []

    async def get_agent_workload(
        self,
        agent_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Получить загруженность агента(ов).

        Args:
            agent_name: Имя конкретного агента (опционально)

        Returns:
            {
                'agent_name': 'agent_xyz',
                'active_tasks': 3,
                'pending_tasks': 5,
                'completed_today': 12,
                'avg_completion_time': '15m',
                'capacity_usage': 0.65  # 0.0 - 1.0
            }
        """
        try:
            params = {}
            if agent_name:
                params['agent'] = agent_name

            response = await self.client.get(
                f"{self.base_url}/api/agents/workload",
                params=params
            )
            response.raise_for_status()
            workload = response.json()

            logger.info(f"Agent workload retrieved")

            return workload

        except Exception as e:
            logger.error(f"Failed to get agent workload: {e}")
            return {'error': str(e)}

    async def coordinate_multi_agent_task(
        self,
        task_type: str,
        subtasks: List[Dict[str, Any]],
        coordination_strategy: str = 'parallel'
    ) -> Dict[str, Any]:
        """
        Координировать мульти-агентную задачу.

        Args:
            task_type: Тип общей задачи
            subtasks: Список подзадач для разных агентов
            coordination_strategy: Стратегия (parallel, sequential, hybrid)

        Returns:
            {
                'coordination_id': 'COORD-20251008-001',
                'status': 'coordinating',
                'subtasks': [
                    {'task_id': 'TASK-001', 'agent': 'agent1'},
                    {'task_id': 'TASK-002', 'agent': 'agent2'}
                ],
                'overall_progress': 0.0
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/coordination/multi-agent",
                json={
                    'task_type': task_type,
                    'subtasks': subtasks,
                    'coordination_strategy': coordination_strategy,
                    'initiated_by': 'mio_manager',
                    'initiated_at': datetime.utcnow().isoformat()
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                f" Multi-agent coordination started: {result.get('coordination_id')}"
            )

            return result

        except Exception as e:
            logger.error(f"Failed to coordinate multi-agent task: {e}")
            return {'error': str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """
        Проверить доступность Coordination Center.

        Returns:
            {
                'status': 'healthy',
                'service': 'coordination_center',
                'version': '1.0.0',
                'active_tasks': 15,
                'available_agents': 8
            }
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/health",
                timeout=5.0
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Coordination Center health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    async def close(self):
        """Закрыть HTTP клиент."""
        await self.client.aclose()


# Convenience instance
_coordination_client: Optional[CoordinationCenterClient] = None


def get_coordination_client(coordination_url: str = "http://localhost:8053") -> CoordinationCenterClient:
    """
    Получить singleton instance CoordinationCenterClient.

    Usage:
        client = get_coordination_client()
        result = await client.delegate_task('fix_issue', task_data)
    """
    global _coordination_client

    if _coordination_client is None:
        _coordination_client = CoordinationCenterClient(coordination_url)

    return _coordination_client
