#!/usr/bin/env python3
"""
Orchestrator Client - Делегирование задач Orchestrator
"""

import httpx
from typing import Dict, Optional
from datetime import datetime


class OrchestratorClient:
    """Client для взаимодействия с AI Orchestrator"""

    def __init__(self, orchestrator_url: str = "http://localhost:8001"):
        self.orchestrator_url = orchestrator_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def delegate_task(self, task: Dict) -> Dict:
        """
        Делегировать задачу Orchestrator для выполнения
        Orchestrator решит, какой агент должен выполнить задачу
        """
        try:
            response = await self.client.post(
                f"{self.orchestrator_url}/api/tasks",
                json=task
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'status': 'error',
                    'message': f'Orchestrator returned {response.status_code}'
                }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    async def get_task_status(self, task_id: str) -> Dict:
        """Получить статус задачи"""
        try:
            response = await self.client.get(
                f"{self.orchestrator_url}/api/tasks/{task_id}"
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {'status': 'not_found'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def request_service_restart(self, service_name: str) -> Dict:
        """Запросить перезапуск сервиса через Orchestrator"""
        task = {
            'task_id': f"restart_{service_name}_{datetime.utcnow().timestamp()}",
            'type': 'service_restart',
            'service': service_name,
            'priority': 'high',
            'created_at': datetime.utcnow().isoformat()
        }

        return await self.delegate_task(task)

    async def request_config_update(self, service_name: str, config: Dict) -> Dict:
        """Запросить обновление конфигурации сервиса"""
        task = {
            'task_id': f"config_update_{service_name}_{datetime.utcnow().timestamp()}",
            'type': 'config_update',
            'service': service_name,
            'config': config,
            'priority': 'medium',
            'created_at': datetime.utcnow().isoformat()
        }

        return await self.delegate_task(task)

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
