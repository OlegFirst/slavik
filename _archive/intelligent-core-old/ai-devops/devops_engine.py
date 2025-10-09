"""
DevOps Engine - AI-powered deployment orchestration

Simplified version - provides AI deployment capabilities
For production: integrate with Temporal or Prefect
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class DevOpsEngine:
    """AI-powered DevOps automation"""

    def __init__(self, docker_manager, service_registry):
        self.docker_manager = docker_manager
        self.service_registry = service_registry
        self.deployment_history = []

        logger.info("DevOpsEngine initialized")

    async def orchestrate_deployment(self, services: List[str]) -> Dict[str, Any]:
        """
        AI-orchestrated deployment

        Args:
            services: List of services to deploy

        Returns:
            Deployment result
        """
        logger.info(f"AI orchestrating deployment of {len(services)} services")

        # AI analyzes dependencies
        ordered_services = await self._analyze_dependencies(services)

        # Deploy in optimal order
        deployed = []
        failed = []

        for service in ordered_services:
            success = await self.docker_manager.start_service(service)
            if success:
                deployed.append(service)
            else:
                failed.append(service)

                # AI decides: continue or stop?
                if await self._should_continue(service, failed):
                    logger.info(f"AI decision: Continue despite {service} failure")
                else:
                    logger.warning(f"AI decision: Stop deployment due to {service} failure")
                    break

        result = {
            'deployment_id': f"ai_deploy_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'services_deployed': deployed,
            'services_failed': failed,
            'ai_decisions': []
        }

        self.deployment_history.append(result)

        return result

    async def _analyze_dependencies(self, services: List[str]) -> List[str]:
        """
        AI analyzes service dependencies and returns optimal order

        Args:
            services: List of service names

        Returns:
            Optimally ordered list
        """
        # Simple heuristic: database services first, then apps
        priority_order = ['postgres', 'redis', 'rabbitmq']

        ordered = []

        # Add priority services first
        for svc in priority_order:
            if svc in services:
                ordered.append(svc)

        # Add remaining services
        for svc in services:
            if svc not in ordered:
                ordered.append(svc)

        logger.info(f"AI ordered services: {ordered}")

        return ordered

    async def _should_continue(self, failed_service: str, all_failed: List[str]) -> bool:
        """
        AI decides whether to continue deployment after failure

        Args:
            failed_service: Service that just failed
            all_failed: All failed services so far

        Returns:
            True to continue, False to stop
        """
        # Critical services: stop immediately
        critical = ['postgres', 'redis']

        if failed_service in critical:
            logger.warning(f"{failed_service} is critical - stopping deployment")
            return False

        # Too many failures: stop
        if len(all_failed) >= 3:
            logger.warning(f"Too many failures ({len(all_failed)}) - stopping")
            return False

        # Otherwise continue
        return True
