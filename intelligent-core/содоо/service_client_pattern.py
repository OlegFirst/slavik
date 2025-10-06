"""
Service Client Pattern - Extracted from Odoo bcm_ai_service.py

Unified API client for microservices communication with:
- Service discovery and configuration
- Health monitoring
- Unified error handling
- Authentication
- Multi-method support (GET/POST/PUT/DELETE)
- File upload support

Original Source: bcm_ai_control/bcm_base/models/bcm_ai_service.py
Extracted: 2025-10-05
"""

import json
import logging
from typing import Dict, Any, Optional, Literal
from datetime import datetime
import httpx
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ServiceConfig:
    """Configuration for a BCM microservice"""
    name: str
    service_type: str
    base_url: str
    port: int
    api_key: Optional[str] = None
    timeout: int = 30
    health_endpoint: str = "/health"


class ServiceHealthMonitor:
    """
    Health monitoring for BCM microservices

    Tracks service availability and health status
    """

    def __init__(self):
        self.health_status: Dict[str, Dict[str, Any]] = {}

    async def check_health(self, config: ServiceConfig) -> bool:
        """Check if service is healthy"""
        try:
            service_url = f"{config.base_url}:{config.port}"
            health_url = f"{service_url}{config.health_endpoint}"

            async with httpx.AsyncClient() as client:
                response = await client.get(health_url, timeout=config.timeout)

                is_healthy = response.status_code == 200

                self.health_status[config.service_type] = {
                    'status': 'healthy' if is_healthy else 'unhealthy',
                    'last_check': datetime.now().isoformat(),
                    'response_code': response.status_code
                }

                return is_healthy

        except Exception as e:
            logger.error(f"Health check failed for {config.name}: {e}")
            self.health_status[config.service_type] = {
                'status': 'unhealthy',
                'last_check': datetime.now().isoformat(),
                'error': str(e)
            }
            return False

    async def check_all_services(self, configs: list[ServiceConfig]) -> Dict[str, bool]:
        """Check health of all configured services"""
        results = {}
        for config in configs:
            results[config.service_type] = await self.check_health(config)
        return results

    def get_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Get current health status of all services"""
        return self.health_status.copy()


class BCMServiceRegistry:
    """
    Service registry for BCM microservices

    Manages service configurations and discovery
    """

    # Default service configurations
    DEFAULT_CONFIGS = [
        ServiceConfig(
            name='AI Orchestrator',
            service_type='ai_orchestrator',
            base_url='http://localhost',
            port=8000
        ),
        ServiceConfig(
            name='BIA Engine',
            service_type='bia_engine',
            base_url='http://localhost',
            port=8082
        ),
        ServiceConfig(
            name='Document Processor',
            service_type='document_processor',
            base_url='http://localhost',
            port=8083
        ),
        ServiceConfig(
            name='Compliance Checker',
            service_type='compliance_checker',
            base_url='http://localhost',
            port=8084
        ),
    ]

    def __init__(self, custom_configs: Optional[list[ServiceConfig]] = None):
        self.configs: Dict[str, ServiceConfig] = {}

        # Load default or custom configs
        configs_to_load = custom_configs or self.DEFAULT_CONFIGS
        for config in configs_to_load:
            self.register_service(config)

    def register_service(self, config: ServiceConfig):
        """Register a service configuration"""
        self.configs[config.service_type] = config
        logger.info(f"Registered service: {config.name} at {config.base_url}:{config.port}")

    def get_service(self, service_type: str) -> ServiceConfig:
        """Get service configuration by type"""
        if service_type not in self.configs:
            raise ValueError(f"Service {service_type} not registered")
        return self.configs[service_type]

    def get_service_url(self, service_type: str) -> str:
        """Get full service URL"""
        config = self.get_service(service_type)
        return f"{config.base_url}:{config.port}"


class BCMServiceClient:
    """
    Unified API client for BCM microservices

    Provides:
    - Standardized request methods
    - Authentication handling
    - Error handling
    - File upload support
    - Timeout management
    """

    def __init__(self, registry: BCMServiceRegistry):
        self.registry = registry
        self.health_monitor = ServiceHealthMonitor()

    async def _make_request(
        self,
        service_type: str,
        endpoint: str,
        method: Literal['GET', 'POST', 'PUT', 'DELETE'] = 'GET',
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to a BCM microservice

        Args:
            service_type: Service identifier (e.g., 'bia_engine')
            endpoint: API endpoint path
            method: HTTP method
            data: JSON data to send
            files: Files to upload
            timeout: Request timeout (overrides config default)

        Returns:
            Response JSON as dict

        Raises:
            ValueError: If service not found
            httpx.HTTPError: If request fails
        """
        config = self.registry.get_service(service_type)
        url = f"{self.registry.get_service_url(service_type)}{endpoint}"

        headers = {}
        if config.api_key:
            headers['Authorization'] = f'Bearer {config.api_key}'

        request_timeout = timeout or config.timeout

        try:
            async with httpx.AsyncClient() as client:
                if method == 'GET':
                    response = await client.get(
                        url,
                        headers=headers,
                        timeout=request_timeout
                    )

                elif method == 'POST':
                    if files:
                        # File upload - don't set Content-Type
                        response = await client.post(
                            url,
                            headers=headers,
                            data=data,
                            files=files,
                            timeout=request_timeout
                        )
                    else:
                        # JSON data
                        headers['Content-Type'] = 'application/json'
                        response = await client.post(
                            url,
                            headers=headers,
                            json=data,
                            timeout=request_timeout
                        )

                elif method == 'PUT':
                    headers['Content-Type'] = 'application/json'
                    response = await client.put(
                        url,
                        headers=headers,
                        json=data,
                        timeout=request_timeout
                    )

                elif method == 'DELETE':
                    response = await client.delete(
                        url,
                        headers=headers,
                        timeout=request_timeout
                    )

                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Request to {service_type} failed: {e}")
            raise

    # ========== AI Orchestrator Methods ==========

    async def analyze_process_risk(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze process risk via AI Orchestrator"""
        return await self._make_request(
            'ai_orchestrator',
            '/analyze/process-risk',
            method='POST',
            data=process_data
        )

    async def classify_incident(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify incident via AI Orchestrator"""
        return await self._make_request(
            'ai_orchestrator',
            '/analyze/incident',
            method='POST',
            data=incident_data
        )

    async def process_nlp_query(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process NLP query via AI Orchestrator"""
        return await self._make_request(
            'ai_orchestrator',
            '/nlp/query',
            method='POST',
            data=query_data
        )

    # ========== BIA Engine Methods ==========

    async def compute_bia_analysis(self, bia_request: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive BIA analysis via BIA Engine"""
        return await self._make_request(
            'bia_engine',
            '/compute',
            method='POST',
            data=bia_request
        )

    async def optimize_single_process(
        self,
        process_data: Dict[str, Any],
        risk_tolerance: float = 0.05
    ) -> Dict[str, Any]:
        """Optimize single process via BIA Engine"""
        return await self._make_request(
            'bia_engine',
            f'/optimize/single-process?risk_tolerance={risk_tolerance}',
            method='POST',
            data=process_data
        )

    # ========== Document Processor Methods ==========

    async def upload_document(
        self,
        file_data: bytes,
        filename: str,
        document_type_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload and process document via Document Processor"""
        files = {'file': (filename, file_data)}
        form_data = {}

        if document_type_hint:
            form_data['document_type_hint'] = document_type_hint

        return await self._make_request(
            'document_processor',
            '/upload',
            method='POST',
            data=form_data,
            files=files
        )

    async def search_documents(
        self,
        query: str,
        document_type: Optional[str] = None,
        compliance_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search documents via Document Processor"""
        params = {'query': query}
        if document_type:
            params['document_type'] = document_type
        if compliance_level:
            params['compliance_level'] = compliance_level

        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])

        return await self._make_request(
            'document_processor',
            f'/search?{query_string}',
            method='GET'
        )

    # ========== Compliance Checker Methods ==========

    async def conduct_compliance_assessment(
        self,
        standard: str = 'iso_22301',
        assessor: str = 'system',
        scope: str = 'Full assessment'
    ) -> Dict[str, Any]:
        """Conduct compliance assessment via Compliance Checker"""
        params = {
            'standard': standard,
            'assessor': assessor,
            'scope': scope
        }
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])

        return await self._make_request(
            'compliance_checker',
            f'/assess?{query_string}',
            method='POST'
        )

    async def submit_compliance_evidence(
        self,
        evidence_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit compliance evidence"""
        return await self._make_request(
            'compliance_checker',
            '/evidence',
            method='POST',
            data=evidence_data
        )

    async def get_compliance_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get compliance analytics"""
        return await self._make_request(
            'compliance_checker',
            f'/analytics/compliance-trends?days={days}',
            method='GET'
        )

    # ========== Health Monitoring ==========

    async def check_service_health(self, service_type: str) -> bool:
        """Check health of a specific service"""
        config = self.registry.get_service(service_type)
        return await self.health_monitor.check_health(config)

    async def check_all_services_health(self) -> Dict[str, bool]:
        """Check health of all registered services"""
        configs = list(self.registry.configs.values())
        return await self.health_monitor.check_all_services(configs)

    def get_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Get current health status of all services"""
        return self.health_monitor.get_health_status()


# ========== Usage Example ==========

async def example_usage():
    """Example of using the service client"""

    # Initialize registry with default or custom configs
    registry = BCMServiceRegistry()

    # Create client
    client = BCMServiceClient(registry)

    # Check health of all services
    health_status = await client.check_all_services_health()
    print("Health Status:", health_status)

    # Use BIA Engine
    bia_result = await client.compute_bia_analysis({
        'organization_id': 'org_123',
        'processes': [...]
    })

    # Use Document Processor
    doc_result = await client.search_documents(
        query="ISO 22301 requirements",
        document_type="policy"
    )

    # Use Compliance Checker
    compliance = await client.conduct_compliance_assessment(
        standard='iso_22301'
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
