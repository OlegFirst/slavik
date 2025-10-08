"""
Unified Service Client for Microservices Communication
"""

import logging
from typing import Dict, Any, Optional, Literal
import httpx

from .config import ServiceConfig
from .registry import ServiceRegistry
from .health import ServiceHealthMonitor

logger = logging.getLogger(__name__)


class ServiceClient:
    """
    Unified API client for microservices

    Provides:
    - Standardized request methods (GET, POST, PUT, DELETE)
    - Authentication handling
    - Error handling with retries
    - File upload support
    - Timeout management
    - Health monitoring
    """

    def __init__(self, registry: ServiceRegistry):
        """
        Initialize service client

        Args:
            registry: Service registry for service discovery
        """
        self.registry = registry
        self.health_monitor = ServiceHealthMonitor()

    async def request(
        self,
        service_type: str,
        endpoint: str,
        method: Literal['GET', 'POST', 'PUT', 'DELETE'] = 'GET',
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to a microservice

        Args:
            service_type: Service identifier (e.g., 'predictive')
            endpoint: API endpoint path (e.g., '/predictions/journey')
            method: HTTP method
            data: JSON data to send (for POST/PUT)
            files: Files to upload (for POST)
            params: Query parameters
            timeout: Request timeout (overrides config default)
            headers: Additional headers

        Returns:
            Response JSON as dict

        Raises:
            ValueError: If service not found
            httpx.HTTPError: If request fails
        """
        config = self.registry.get_service(service_type)
        url = f"{config.get_full_url()}{endpoint}"

        # Build headers
        request_headers = headers or {}
        if config.api_key:
            request_headers['Authorization'] = f'Bearer {config.api_key}'

        request_timeout = timeout or config.timeout

        try:
            async with httpx.AsyncClient() as client:
                if method == 'GET':
                    response = await client.get(
                        url,
                        headers=request_headers,
                        params=params,
                        timeout=request_timeout
                    )

                elif method == 'POST':
                    if files:
                        # File upload - don't set Content-Type (httpx handles it)
                        response = await client.post(
                            url,
                            headers=request_headers,
                            data=data,
                            files=files,
                            params=params,
                            timeout=request_timeout
                        )
                    else:
                        # JSON data
                        request_headers['Content-Type'] = 'application/json'
                        response = await client.post(
                            url,
                            headers=request_headers,
                            json=data,
                            params=params,
                            timeout=request_timeout
                        )

                elif method == 'PUT':
                    request_headers['Content-Type'] = 'application/json'
                    response = await client.put(
                        url,
                        headers=request_headers,
                        json=data,
                        params=params,
                        timeout=request_timeout
                    )

                elif method == 'DELETE':
                    response = await client.delete(
                        url,
                        headers=request_headers,
                        params=params,
                        timeout=request_timeout
                    )

                response.raise_for_status()

                # Try to parse JSON, fall back to text
                try:
                    return response.json()
                except Exception:
                    return {'text': response.text, 'status_code': response.status_code}

        except httpx.HTTPError as e:
            logger.error(
                f"Request to {service_type} ({config.name}) failed: "
                f"{method} {endpoint} - {e}"
            )
            raise

    # ========== Health Monitoring ==========

    async def check_service_health(self, service_type: str) -> bool:
        """
        Check health of a specific service

        Args:
            service_type: Service type identifier

        Returns:
            True if healthy, False otherwise
        """
        config = self.registry.get_service(service_type)
        return await self.health_monitor.check_health(config)

    async def check_all_services_health(self) -> Dict[str, bool]:
        """
        Check health of all registered services

        Returns:
            Dict mapping service_type to health status
        """
        configs = self.registry.get_all_configs()
        return await self.health_monitor.check_all_services(configs)

    def get_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Get current health status of all services"""
        return self.health_monitor.get_health_status()

    def get_unhealthy_services(self) -> list[str]:
        """Get list of unhealthy service types"""
        return self.health_monitor.get_unhealthy_services()

    # ========== Convenience Methods for Common Services ==========

    async def get_journey_prediction(self, org_id: str) -> Dict[str, Any]:
        """Get journey prediction from Predictive service"""
        return await self.request(
            'predictive',
            f'/api/v1/predictions/journey/{org_id}',
            method='GET'
        )

    async def create_collective_agent(self, problem: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create collective agent from Collective service"""
        return await self.request(
            'collective',
            '/api/v1/agents/create',
            method='POST',
            data={'problem': problem, 'context': context}
        )

    async def submit_case_contribution(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit case contribution to Community Intelligence"""
        return await self.request(
            'community_intelligence',
            '/api/v1/contributions/submit',
            method='POST',
            data=case_data
        )
