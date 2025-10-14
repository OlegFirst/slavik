"""
Deployment Manager - Simple deployment logic without AI

Merged from /services/deployer/main.py
Provides basic deployment functionality as alternative to AI-powered deployment
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class DeploymentManager:
    """
    Simple deployment manager

    Provides basic deployment functionality:
    - Sequential service deployment
    - Health checking
    - Auto-restart on failure
    - Deployment tracking

    Note: For AI-powered deployment, use AIDevOpsEngine in ai/ module
    """

    def __init__(self, docker_manager, health_monitor, service_registry):
        self.docker_manager = docker_manager
        self.health_monitor = health_monitor
        self.service_registry = service_registry
        self.deployment_history = []

        logger.info("DeploymentManager initialized")

    async def deploy_services(self, service_order: List[str],
                             timeout_per_service: int = 300) -> Dict[str, Any]:
        """
        Deploy services sequentially

        Args:
            service_order: List of service names in deployment order
            timeout_per_service: Timeout for each service in seconds

        Returns:
            Deployment result dictionary
        """
        logger.info(f"Starting deployment of {len(service_order)} services")

        start_time = datetime.utcnow()
        deployed = []
        failed = []

        for service_name in service_order:
            logger.info(f"Deploying {service_name}...")

            try:
                # Start service
                success = await self._deploy_single_service(
                    service_name,
                    timeout=timeout_per_service
                )

                if success:
                    deployed.append(service_name)
                    logger.info(f"✓ {service_name} deployed successfully")
                else:
                    failed.append(service_name)
                    logger.error(f"✗ {service_name} deployment failed")

            except Exception as e:
                logger.error(f"Error deploying {service_name}: {e}")
                failed.append(service_name)

        elapsed = (datetime.utcnow() - start_time).total_seconds()

        result = {
            'deployment_id': f"deploy_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'status': 'success' if not failed else 'partial',
            'services_deployed': deployed,
            'services_failed': failed,
            'execution_time_seconds': int(elapsed),
            'started_at': start_time.isoformat(),
            'completed_at': datetime.utcnow().isoformat()
        }

        # Store in history
        self.deployment_history.append(result)

        logger.info(f"Deployment completed: {len(deployed)}/{len(service_order)} services")

        return result

    async def _deploy_single_service(self, service_name: str,
                                     timeout: int = 300) -> bool:
        """
        Deploy single service with health checking

        Args:
            service_name: Name of the service
            timeout: Timeout in seconds

        Returns:
            True if deployed successfully
        """
        # Start Docker service
        started = await self.docker_manager.start_service(service_name)
        if not started:
            return False

        # Wait for healthy with timeout
        start_time = datetime.utcnow()

        while (datetime.utcnow() - start_time).total_seconds() < timeout:
            # Check health
            status = await self.docker_manager.get_container_status(service_name)

            if status and status.is_healthy():
                # Update registry
                await self.service_registry.update_status(service_name, "running")
                await self.service_registry.update_health(service_name, "healthy")
                return True

            # Wait before next check
            await asyncio.sleep(10)

        logger.warning(f"Service {service_name} started but not healthy after {timeout}s")
        return False

    async def restart_service(self, service_name: str) -> bool:
        """
        Restart a service

        Args:
            service_name: Name of the service

        Returns:
            True if restarted successfully
        """
        logger.info(f"Restarting service: {service_name}")

        try:
            # Restart via docker manager
            success = await self.docker_manager.restart_service(service_name)

            if success:
                # Wait for healthy
                await asyncio.sleep(10)

                status = await self.docker_manager.get_container_status(service_name)
                if status and status.is_healthy():
                    await self.service_registry.update_status(service_name, "running")
                    await self.service_registry.update_health(service_name, "healthy")
                    logger.info(f"Service {service_name} restarted successfully")
                    return True
                else:
                    logger.warning(f"Service {service_name} restarted but not healthy")
                    return False
            else:
                logger.error(f"Failed to restart {service_name}")
                return False

        except Exception as e:
            logger.error(f"Error restarting {service_name}: {e}")
            return False

    async def stop_service(self, service_name: str) -> bool:
        """
        Stop a service

        Args:
            service_name: Name of the service

        Returns:
            True if stopped successfully
        """
        logger.info(f"Stopping service: {service_name}")

        try:
            success = await self.docker_manager.stop_service(service_name)

            if success:
                await self.service_registry.update_status(service_name, "stopped")
                logger.info(f"Service {service_name} stopped")
                return True
            else:
                logger.error(f"Failed to stop {service_name}")
                return False

        except Exception as e:
            logger.error(f"Error stopping {service_name}: {e}")
            return False

    async def get_deployment_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get deployment history

        Args:
            limit: Maximum number of records to return

        Returns:
            List of deployment records
        """
        return self.deployment_history[-limit:]

    async def get_deployment_stats(self) -> Dict[str, Any]:
        """
        Get deployment statistics

        Returns:
            Dictionary with statistics
        """
        if not self.deployment_history:
            return {
                'total_deployments': 0,
                'success_rate': 0.0,
                'avg_execution_time': 0
            }

        total = len(self.deployment_history)
        successful = sum(1 for d in self.deployment_history if d['status'] == 'success')
        avg_time = sum(d['execution_time_seconds'] for d in self.deployment_history) / total

        return {
            'total_deployments': total,
            'successful_deployments': successful,
            'failed_deployments': total - successful,
            'success_rate': round(successful / total * 100, 2),
            'avg_execution_time_seconds': int(avg_time),
            'latest_deployment': self.deployment_history[-1] if self.deployment_history else None
        }