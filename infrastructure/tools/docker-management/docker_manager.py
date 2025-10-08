"""
Docker Manager - Docker API wrapper
Handles container lifecycle: start, stop, restart, logs, status
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging
import subprocess
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class ContainerStatus:
    """Container status information"""
    name: str
    status: str  # running, stopped, restarting, exited, created
    health: Optional[str] = None  # healthy, unhealthy, starting, none
    uptime_seconds: Optional[int] = None
    ports: Dict[str, Any] = field(default_factory=dict)
    image: Optional[str] = None
    labels: Dict[str, str] = field(default_factory=dict)

    def is_running(self) -> bool:
        """Check if container is running"""
        return self.status == "running"

    def is_healthy(self) -> bool:
        """Check if container is healthy"""
        return self.health == "healthy" or (self.health is None and self.is_running())


class DockerManager:
    """
    Docker API wrapper for container management

    Uses both docker-py client and docker-compose CLI
    """

    def __init__(self, use_docker_client: bool = True):
        self.docker_client = None
        self.use_docker_client = use_docker_client
        self.compose_file = "docker-compose.yml"
        self.project_name = "iso-22301"

        logger.info("DockerManager initialized")

        # Try to connect to Docker
        if use_docker_client:
            try:
                import docker
                self.docker_client = docker.from_env()
                logger.info("Connected to Docker daemon")
            except Exception as e:
                logger.warning(f"Could not connect to Docker daemon: {e}")
                logger.info("Will use docker-compose CLI instead")

    async def start_service(self, service_name: str, timeout: int = 300) -> bool:
        """
        Start a Docker service

        Args:
            service_name: Name of the service
            timeout: Timeout in seconds

        Returns:
            True if started successfully
        """
        logger.info(f"Starting service: {service_name}")

        try:
            # Use docker-compose
            result = await asyncio.create_subprocess_exec(
                "docker-compose", "-f", self.compose_file,
                "up", "-d", service_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(
                result.communicate(),
                timeout=timeout
            )

            if result.returncode == 0:
                logger.info(f"Service {service_name} started successfully")
                return True
            else:
                stderr_text = stderr.decode() if stderr else ""
                logger.error(f"Failed to start {service_name}: {stderr_text}")
                return False

        except asyncio.TimeoutError:
            logger.error(f"Timeout starting {service_name} after {timeout}s")
            return False
        except Exception as e:
            logger.error(f"Error starting {service_name}: {e}")
            return False

    async def stop_service(self, service_name: str, timeout: int = 60) -> bool:
        """
        Stop a Docker service

        Args:
            service_name: Name of the service
            timeout: Timeout in seconds

        Returns:
            True if stopped successfully
        """
        logger.info(f"Stopping service: {service_name}")

        try:
            result = await asyncio.create_subprocess_exec(
                "docker-compose", "-f", self.compose_file,
                "stop", service_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(
                result.communicate(),
                timeout=timeout
            )

            if result.returncode == 0:
                logger.info(f"Service {service_name} stopped successfully")
                return True
            else:
                stderr_text = stderr.decode() if stderr else ""
                logger.error(f"Failed to stop {service_name}: {stderr_text}")
                return False

        except asyncio.TimeoutError:
            logger.error(f"Timeout stopping {service_name} after {timeout}s")
            # Force kill
            await self._force_stop(service_name)
            return False
        except Exception as e:
            logger.error(f"Error stopping {service_name}: {e}")
            return False

    async def restart_service(self, service_name: str, timeout: int = 60) -> bool:
        """
        Restart a Docker service

        Args:
            service_name: Name of the service
            timeout: Timeout in seconds

        Returns:
            True if restarted successfully
        """
        logger.info(f"Restarting service: {service_name}")

        try:
            result = await asyncio.create_subprocess_exec(
                "docker-compose", "-f", self.compose_file,
                "restart", service_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(
                result.communicate(),
                timeout=timeout
            )

            if result.returncode == 0:
                logger.info(f"Service {service_name} restarted successfully")
                return True
            else:
                stderr_text = stderr.decode() if stderr else ""
                logger.error(f"Failed to restart {service_name}: {stderr_text}")
                return False

        except asyncio.TimeoutError:
            logger.error(f"Timeout restarting {service_name} after {timeout}s")
            return False
        except Exception as e:
            logger.error(f"Error restarting {service_name}: {e}")
            return False

    async def get_container_status(self, service_name: str) -> Optional[ContainerStatus]:
        """
        Get container status

        Args:
            service_name: Name of the service

        Returns:
            ContainerStatus or None if not found
        """
        if self.docker_client:
            return await self._get_status_via_client(service_name)
        else:
            return await self._get_status_via_cli(service_name)

    async def _get_status_via_client(self, service_name: str) -> Optional[ContainerStatus]:
        """Get status using docker-py client"""
        try:
            container_name = f"{self.project_name}-{service_name}-1"

            # Run in executor to avoid blocking
            container = await asyncio.get_event_loop().run_in_executor(
                None,
                self.docker_client.containers.get,
                container_name
            )

            # Get container details
            attrs = container.attrs
            state = attrs.get('State', {})

            status = ContainerStatus(
                name=service_name,
                status=state.get('Status', 'unknown'),
                health=state.get('Health', {}).get('Status'),
                image=attrs.get('Config', {}).get('Image'),
                ports=attrs.get('NetworkSettings', {}).get('Ports', {})
            )

            # Calculate uptime
            started_at = state.get('StartedAt')
            if started_at:
                start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                uptime = (datetime.utcnow() - start_time).total_seconds()
                status.uptime_seconds = int(uptime)

            return status

        except Exception as e:
            logger.warning(f"Could not get status for {service_name}: {e}")
            return None

    async def _get_status_via_cli(self, service_name: str) -> Optional[ContainerStatus]:
        """Get status using docker-compose CLI"""
        try:
            result = await asyncio.create_subprocess_exec(
                "docker-compose", "-f", self.compose_file,
                "ps", service_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await result.communicate()
            output = stdout.decode() if stdout else ""

            # Parse output (simple parsing)
            lines = output.strip().split('\n')
            if len(lines) < 2:
                return None

            # Look for service in output
            for line in lines[1:]:
                if service_name in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        status_str = parts[1].lower()
                        return ContainerStatus(
                            name=service_name,
                            status="running" if "up" in status_str else "stopped"
                        )

            return None

        except Exception as e:
            logger.warning(f"Could not get status via CLI for {service_name}: {e}")
            return None

    async def get_container_logs(self, service_name: str, tail: int = 100) -> List[str]:
        """
        Get container logs

        Args:
            service_name: Name of the service
            tail: Number of lines to retrieve

        Returns:
            List of log lines
        """
        try:
            result = await asyncio.create_subprocess_exec(
                "docker-compose", "-f", self.compose_file,
                "logs", "--tail", str(tail), service_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await result.communicate()
            output = stdout.decode() if stdout else ""

            lines = output.strip().split('\n')
            return lines

        except Exception as e:
            logger.error(f"Error getting logs for {service_name}: {e}")
            return []

    async def list_services(self) -> List[str]:
        """
        List all services in docker-compose

        Returns:
            List of service names
        """
        try:
            result = await asyncio.create_subprocess_exec(
                "docker-compose", "-f", self.compose_file,
                "config", "--services",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await result.communicate()
            output = stdout.decode() if stdout else ""

            services = [s.strip() for s in output.strip().split('\n') if s.strip()]
            return services

        except Exception as e:
            logger.error(f"Error listing services: {e}")
            return []

    async def _force_stop(self, service_name: str) -> bool:
        """Force stop a service using kill"""
        try:
            result = await asyncio.create_subprocess_exec(
                "docker-compose", "-f", self.compose_file,
                "kill", service_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            await result.communicate()
            logger.warning(f"Force killed service: {service_name}")
            return result.returncode == 0

        except Exception as e:
            logger.error(f"Error force stopping {service_name}: {e}")
            return False

    async def scale_service(self, service_name: str, replicas: int) -> bool:
        """
        Scale a service to N replicas

        Args:
            service_name: Name of the service
            replicas: Number of replicas

        Returns:
            True if scaled successfully
        """
        try:
            result = await asyncio.create_subprocess_exec(
                "docker-compose", "-f", self.compose_file,
                "up", "-d", "--scale", f"{service_name}={replicas}", service_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await result.communicate()

            if result.returncode == 0:
                logger.info(f"Scaled {service_name} to {replicas} replicas")
                return True
            else:
                stderr_text = stderr.decode() if stderr else ""
                logger.error(f"Failed to scale {service_name}: {stderr_text}")
                return False

        except Exception as e:
            logger.error(f"Error scaling {service_name}: {e}")
            return False

    async def execute_in_container(self, service_name: str,
                                   command: List[str]) -> Optional[str]:
        """
        Execute command in container

        Args:
            service_name: Name of the service
            command: Command to execute

        Returns:
            Command output or None
        """
        try:
            cmd = ["docker-compose", "-f", self.compose_file, "exec", "-T", service_name] + command

            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await result.communicate()
            output = stdout.decode() if stdout else ""

            if result.returncode == 0:
                return output
            else:
                stderr_text = stderr.decode() if stderr else ""
                logger.error(f"Command failed in {service_name}: {stderr_text}")
                return None

        except Exception as e:
            logger.error(f"Error executing command in {service_name}: {e}")
            return None

    def close(self) -> None:
        """Close Docker client connection"""
        if self.docker_client:
            try:
                self.docker_client.close()
                logger.info("Closed Docker client connection")
            except Exception as e:
                logger.error(f"Error closing Docker client: {e}")
