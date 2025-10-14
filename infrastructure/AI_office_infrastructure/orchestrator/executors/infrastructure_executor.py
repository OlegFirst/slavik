"""
Infrastructure Executor - Исполнитель infrastructure задач

Функции:
- Deploy services
- Restart services
- Stop services
- Health checks
"""

import logging
import subprocess
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class InfrastructureExecutor:
    """
    Исполнитель infrastructure-related задач

    Возможности:
    - Deployment через docker-compose
    - Service restart
    - Service stop
    - Health monitoring
    """

    def __init__(self, workspace_root: str = "/Users/MD/AI-Platform-ISO"):
        self.workspace_root = Path(workspace_root)
        self.deployment_dir = self.workspace_root / 'infrastructure' / 'deployment'

    async def deploy(self, layer: str = "full", use_ai: bool = True) -> Dict:
        """
        Deploy infrastructure layer

        Args:
            layer: Layer to deploy (gateway/runtime/observability/full)
            use_ai: Use AI orchestration

        Returns:
            Deployment result
        """
        logger.info(f"🚀 Deploying layer: {layer}")

        try:
            compose_file = self.deployment_dir / 'generated' / f'docker-compose.{layer}.yml'

            if not compose_file.exists():
                return {
                    'success': False,
                    'error': f'Compose file not found: {compose_file}'
                }

            # Deploy via docker-compose
            result = subprocess.run(
                ['docker-compose', '-f', str(compose_file), 'up', '-d'],
                cwd=str(compose_file.parent),
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info(f"✅ Layer {layer} deployed successfully")
                return {
                    'success': True,
                    'layer': layer,
                    'output': result.stdout
                }
            else:
                logger.error(f"❌ Deployment failed: {result.stderr}")
                return {
                    'success': False,
                    'error': result.stderr
                }

        except Exception as e:
            logger.error(f"❌ Error deploying: {e}")
            return {'success': False, 'error': str(e)}

    async def restart_service(self, service: str) -> Dict:
        """
        Restart a specific service

        Args:
            service: Service name

        Returns:
            Restart result
        """
        logger.info(f"🔄 Restarting service: {service}")

        try:
            result = subprocess.run(
                ['docker', 'restart', service],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info(f"✅ Service {service} restarted")
                return {
                    'success': True,
                    'service': service,
                    'output': result.stdout
                }
            else:
                logger.error(f"❌ Restart failed: {result.stderr}")
                return {
                    'success': False,
                    'error': result.stderr
                }

        except Exception as e:
            logger.error(f"❌ Error restarting: {e}")
            return {'success': False, 'error': str(e)}

    async def stop_service(self, service: str) -> Dict:
        """
        Stop a specific service

        Args:
            service: Service name

        Returns:
            Stop result
        """
        logger.info(f"🛑 Stopping service: {service}")

        try:
            result = subprocess.run(
                ['docker', 'stop', service],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info(f"✅ Service {service} stopped")
                return {
                    'success': True,
                    'service': service,
                    'output': result.stdout
                }
            else:
                logger.error(f"❌ Stop failed: {result.stderr}")
                return {
                    'success': False,
                    'error': result.stderr
                }

        except Exception as e:
            logger.error(f"❌ Error stopping: {e}")
            return {'success': False, 'error': str(e)}

    async def health_check(self, service: str) -> Dict:
        """
        Check health of a service

        Args:
            service: Service name

        Returns:
            Health status
        """
        try:
            result = subprocess.run(
                ['docker', 'ps', '--filter', f'name={service}', '--format', '{{.Status}}'],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                status = result.stdout.strip()
                is_healthy = 'Up' in status

                return {
                    'success': True,
                    'service': service,
                    'status': status,
                    'healthy': is_healthy
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr
                }

        except Exception as e:
            return {'success': False, 'error': str(e)}
