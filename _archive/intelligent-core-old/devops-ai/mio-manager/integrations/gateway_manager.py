#!/usr/bin/env python3
"""
Gateway Manager - Управление API Gateway / Intelligent Gateway
"""

import httpx
from typing import Dict, List, Optional


class GatewayManager:
    """Client для управления API Gateway"""

    def __init__(self, gateway_url: str = "http://localhost:8000"):
        self.gateway_url = gateway_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def register_service(self, service_config: Dict) -> Dict:
        """
        Регистрация нового сервиса в Gateway
        """
        try:
            response = await self.client.post(
                f"{self.gateway_url}/api/services/register",
                json=service_config
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'status': 'error',
                    'message': f'Gateway returned {response.status_code}'
                }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    async def update_routing(self, service_name: str, routing_config: Dict) -> Dict:
        """
        Обновление маршрутизации для сервиса
        """
        try:
            response = await self.client.put(
                f"{self.gateway_url}/api/routing/{service_name}",
                json=routing_config
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {'status': 'error', 'message': f'Status {response.status_code}'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def get_service_health(self, service_name: str) -> Dict:
        """
        Проверка health сервиса через Gateway
        """
        try:
            response = await self.client.get(
                f"{self.gateway_url}/api/services/{service_name}/health"
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {'status': 'unhealthy', 'code': response.status_code}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def enable_circuit_breaker(self, service_name: str) -> Dict:
        """
        Включить Circuit Breaker для сервиса
        """
        try:
            response = await self.client.post(
                f"{self.gateway_url}/api/services/{service_name}/circuit-breaker/enable"
            )

            return {'status': 'enabled' if response.status_code == 200 else 'failed'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def disable_circuit_breaker(self, service_name: str) -> Dict:
        """
        Выключить Circuit Breaker для сервиса
        """
        try:
            response = await self.client.post(
                f"{self.gateway_url}/api/services/{service_name}/circuit-breaker/disable"
            )

            return {'status': 'disabled' if response.status_code == 200 else 'failed'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
