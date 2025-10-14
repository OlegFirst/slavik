#!/usr/bin/env python3
"""
Orchestrator Client - Делегирование задач Unified Orchestrator

МиО Manager использует этот клиент для делегирования:
- Infrastructure tasks (deploy/restart/stop)
- Event tasks (fix gaps, add publishers/subscribers)
- Code tasks (refactoring, fixes)
- Database tasks (migrations)
"""

import httpx
from typing import Dict, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OrchestratorClient:
    """
    Client для взаимодействия с Unified Orchestrator

    Unified Orchestrator - универсальный исполнитель задач.
    МиО Manager формулирует задачи, Orchestrator их выполняет.
    """

    def __init__(self, orchestrator_url: str = "http://localhost:8090"):
        self.orchestrator_url = orchestrator_url
        self.client = httpx.AsyncClient(timeout=30.0)

    # ========================================================================
    # Infrastructure Tasks
    # ========================================================================

    async def deploy_service(self, layer: str = "full", use_ai: bool = True) -> Dict:
        """
        Развернуть инфраструктурный слой

        Args:
            layer: Какой слой развернуть (gateway, runtime, observability, full)
            use_ai: Использовать ли ai-orchestration

        Returns:
            Deployment result
        """
        logger.info(f"🚀 Requesting deploy: layer={layer}, use_ai={use_ai}")

        try:
            response = await self.client.post(
                f"{self.orchestrator_url}/api/v1/deploy",
                json={
                    "layer": layer,
                    "use_ai_orchestration": use_ai,
                    "force_rebuild": False
                }
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'status': 'error',
                    'message': f'Orchestrator returned {response.status_code}'
                }

        except Exception as e:
            logger.error(f"❌ Deploy request failed: {e}")
            return {'status': 'error', 'message': str(e)}

    async def request_service_restart(self, service_name: str) -> Dict:
        """
        Запросить перезапуск сервиса

        Args:
            service_name: Service name

        Returns:
            Restart result
        """
        logger.info(f"🔄 Requesting restart: {service_name}")

        task = {
            'task_type': 'infrastructure',
            'action': 'restart',
            'parameters': {
                'service': service_name
            }
        }

        return await self.execute_task(task)

    async def get_infrastructure_status(self) -> Dict:
        """Получить статус инфраструктуры"""
        try:
            response = await self.client.get(
                f"{self.orchestrator_url}/api/v1/status"
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {'status': 'error', 'message': f'Status code: {response.status_code}'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    # ========================================================================
    # Event Tasks (НОВОЕ)
    # ========================================================================

    async def fix_event_gap(self, gap: Dict) -> Dict:
        """
        Фиксит одиночный event gap

        Args:
            gap: Gap dict with event_name, gap_type, severity, service, file_path, recommendation

        Returns:
            Fix result
        """
        logger.info(f"🔧 Requesting event gap fix: {gap.get('event_name')}")

        try:
            response = await self.client.post(
                f"{self.orchestrator_url}/api/v1/events/fix-gap",
                json=gap
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'status': 'error',
                    'message': f'Fix gap failed: {response.status_code}'
                }

        except Exception as e:
            logger.error(f"❌ Fix gap request failed: {e}")
            return {'status': 'error', 'message': str(e)}

    async def fix_multiple_event_gaps(self, gaps: List[Dict]) -> Dict:
        """
        Фиксит multiple event gaps

        Args:
            gaps: List of gap dicts

        Returns:
            Summary result
        """
        logger.info(f"🔧 Requesting fix for {len(gaps)} event gaps")

        try:
            response = await self.client.post(
                f"{self.orchestrator_url}/api/v1/events/fix-gaps",
                json=gaps,
                timeout=120.0  # Longer timeout для multiple gaps
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'status': 'error',
                    'message': f'Fix gaps failed: {response.status_code}'
                }

        except Exception as e:
            logger.error(f"❌ Fix gaps request failed: {e}")
            return {'status': 'error', 'message': str(e)}

    async def add_publisher(
        self,
        service: str,
        event: str,
        file_path: str,
        method_name: str,
        position: str = "end"
    ) -> Dict:
        """
        Добавляет publisher в код

        Args:
            service: Service name
            event: Event name
            file_path: File path
            method_name: Method name
            position: Position (start/end/before_return)

        Returns:
            Add result
        """
        logger.info(f"➕ Requesting add publisher: {event} in {service}/{method_name}")

        try:
            response = await self.client.post(
                f"{self.orchestrator_url}/api/v1/events/add-publisher",
                params={
                    'service': service,
                    'event': event,
                    'file_path': file_path,
                    'method_name': method_name,
                    'position': position
                }
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'status': 'error',
                    'message': f'Add publisher failed: {response.status_code}'
                }

        except Exception as e:
            logger.error(f"❌ Add publisher request failed: {e}")
            return {'status': 'error', 'message': str(e)}

    async def add_subscriber(
        self,
        service: str,
        event: str,
        file_path: str,
        handler_name: Optional[str] = None
    ) -> Dict:
        """
        Добавляет subscriber в код

        Args:
            service: Service name
            event: Event name
            file_path: File path
            handler_name: Handler name (auto-generated if None)

        Returns:
            Add result
        """
        logger.info(f"➕ Requesting add subscriber: {event} in {service}")

        try:
            response = await self.client.post(
                f"{self.orchestrator_url}/api/v1/events/add-subscriber",
                params={
                    'service': service,
                    'event': event,
                    'file_path': file_path,
                    'handler_name': handler_name
                }
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'status': 'error',
                    'message': f'Add subscriber failed: {response.status_code}'
                }

        except Exception as e:
            logger.error(f"❌ Add subscriber request failed: {e}")
            return {'status': 'error', 'message': str(e)}

    async def create_event_pr(self, branch_name: Optional[str] = None) -> Dict:
        """
        Создает PR с event изменениями

        Args:
            branch_name: Branch name (auto-generated if None)

        Returns:
            PR result
        """
        logger.info("📤 Requesting create PR with event changes")

        try:
            params = {'branch_name': branch_name} if branch_name else {}
            response = await self.client.post(
                f"{self.orchestrator_url}/api/v1/events/create-pr",
                params=params
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'status': 'error',
                    'message': f'Create PR failed: {response.status_code}'
                }

        except Exception as e:
            logger.error(f"❌ Create PR request failed: {e}")
            return {'status': 'error', 'message': str(e)}

    async def rollback_event_changes(self) -> Dict:
        """
        Откатывает event изменения

        Returns:
            Rollback result
        """
        logger.info("🔄 Requesting rollback event changes")

        try:
            response = await self.client.post(
                f"{self.orchestrator_url}/api/v1/events/rollback"
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'status': 'error',
                    'message': f'Rollback failed: {response.status_code}'
                }

        except Exception as e:
            logger.error(f"❌ Rollback request failed: {e}")
            return {'status': 'error', 'message': str(e)}

    # ========================================================================
    # Unified Task Execution (НОВОЕ)
    # ========================================================================

    async def execute_task(self, task: Dict) -> Dict:
        """
        Универсальное выполнение задачи

        Args:
            task: Task dict with 'task_type', 'action', 'parameters'

        task_type может быть:
        - 'infrastructure': Infrastructure tasks (deploy/restart/stop)
        - 'event': Event tasks (fix_gap/add_publisher/add_subscriber)
        - 'code': Code tasks (refactoring/fixes)
        - 'database': Database tasks (migrations)

        Returns:
            Execution result
        """
        logger.info(f"🎯 Requesting task execution: {task.get('task_type')} - {task.get('action')}")

        try:
            response = await self.client.post(
                f"{self.orchestrator_url}/api/v1/tasks/execute",
                json=task
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'status': 'error',
                    'message': f'Task execution failed: {response.status_code}'
                }

        except Exception as e:
            logger.error(f"❌ Task execution request failed: {e}")
            return {'status': 'error', 'message': str(e)}

    # ========================================================================
    # Legacy Methods (для обратной совместимости)
    # ========================================================================

    async def delegate_task(self, task: Dict) -> Dict:
        """
        Legacy метод - теперь роутится к execute_task

        Args:
            task: Task dict

        Returns:
            Execution result
        """
        # Конвертируем старый формат к новому
        if 'task_type' not in task:
            # Определяем task_type по 'type'
            legacy_type = task.get('type', 'infrastructure')

            if legacy_type == 'service_restart':
                new_task = {
                    'task_type': 'infrastructure',
                    'action': 'restart',
                    'parameters': {
                        'service': task.get('service')
                    }
                }
            elif legacy_type == 'config_update':
                new_task = {
                    'task_type': 'infrastructure',
                    'action': 'config_update',
                    'parameters': {
                        'service': task.get('service'),
                        'config': task.get('config')
                    }
                }
            else:
                # Fallback к старому формату
                new_task = task

            return await self.execute_task(new_task)
        else:
            return await self.execute_task(task)

    async def get_task_status(self, task_id: str) -> Dict:
        """
        Получить статус задачи (legacy)

        TODO: Implement task tracking in Orchestrator
        """
        logger.warning("get_task_status not yet implemented in Unified Orchestrator")
        return {'status': 'not_implemented'}

    async def request_config_update(self, service_name: str, config: Dict) -> Dict:
        """
        Запросить обновление конфигурации сервиса (legacy)

        Args:
            service_name: Service name
            config: Config dict

        Returns:
            Update result
        """
        task = {
            'task_type': 'infrastructure',
            'action': 'config_update',
            'parameters': {
                'service': service_name,
                'config': config
            }
        }

        return await self.execute_task(task)

    # ========================================================================
    # Health Check
    # ========================================================================

    async def health_check(self) -> bool:
        """Проверить доступность оркестратора"""
        try:
            response = await self.client.get(
                f"{self.orchestrator_url}/health",
                timeout=5.0
            )
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
