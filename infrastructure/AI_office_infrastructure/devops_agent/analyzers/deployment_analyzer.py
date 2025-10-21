#!/usr/bin/env python3
"""
Deployment Analyzer

Monitors deployment status, detects port conflicts, checks service health
"""

import subprocess
import re
import logging
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PortConflict:
    """Port conflict information"""
    port: int
    service1: str
    service2: str
    severity: str = "high"


@dataclass
class ServiceStatus:
    """Service health status"""
    name: str
    port: int
    healthy: bool
    response_time_ms: float
    error: str = ""


class DeploymentAnalyzer:
    """Analyzes deployment status and health"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.port_registry: Dict[int, List[str]] = {}

    def scan_port_configurations(self) -> Dict[int, List[str]]:
        """Scan all service configurations for port usage"""
        logger.info(" Scanning port configurations...")

        # Scan Python services
        for main_file in self.project_root.rglob("main.py"):
            if "venv" in str(main_file) or "node_modules" in str(main_file):
                continue

            content = main_file.read_text()
            service_name = main_file.parent.name

            # Extract port
            port_match = re.search(r'(?:port|PORT)["\s]*[:=]["\s]*(\d+)', content)
            if port_match:
                port = int(port_match.group(1))
                if port not in self.port_registry:
                    self.port_registry[port] = []
                self.port_registry[port].append(service_name)

        logger.info(f" Found {len(self.port_registry)} ports in use")
        return self.port_registry

    def detect_port_conflicts(self) -> List[PortConflict]:
        """Detect port conflicts"""
        if not self.port_registry:
            self.scan_port_configurations()

        conflicts = []
        for port, services in self.port_registry.items():
            if len(services) > 1:
                conflicts.append(PortConflict(
                    port=port,
                    service1=services[0],
                    service2=services[1],
                    severity="high"
                ))

        if conflicts:
            logger.warning(f"️  Found {len(conflicts)} port conflicts!")
            for c in conflicts:
                logger.warning(f"   Port {c.port}: {c.service1} vs {c.service2}")

        return conflicts

    def check_services_health(self) -> List[ServiceStatus]:
        """Check health of running services"""
        logger.info(" Checking services health...")

        statuses = []

        for port, services in self.port_registry.items():
            for service_name in services:
                status = self._check_service_health(service_name, port)
                statuses.append(status)

        healthy_count = len([s for s in statuses if s.healthy])
        logger.info(f" {healthy_count}/{len(statuses)} services healthy")

        return statuses

    def _check_service_health(self, service_name: str, port: int) -> ServiceStatus:
        """Check health of a single service"""
        import time

        url = f"http://localhost:{port}/health"

        try:
            import httpx

            start_time = time.time()
            response = httpx.get(url, timeout=3.0)
            response_time = (time.time() - start_time) * 1000  # ms

            healthy = response.status_code == 200

            return ServiceStatus(
                name=service_name,
                port=port,
                healthy=healthy,
                response_time_ms=response_time
            )

        except Exception as e:
            return ServiceStatus(
                name=service_name,
                port=port,
                healthy=False,
                response_time_ms=0,
                error=str(e)
            )

    def suggest_available_port(self, preferred_range: tuple = (8000, 9000)) -> int:
        """Suggest an available port"""
        if not self.port_registry:
            self.scan_port_configurations()

        used_ports = set(self.port_registry.keys())

        for port in range(preferred_range[0], preferred_range[1]):
            if port not in used_ports:
                return port

        raise ValueError(f"No available ports in range {preferred_range}")

    def check_docker_services(self) -> List[Dict]:
        """Check Docker container status"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}:{{.Ports}}:{{.Status}}"],
                capture_output=True,
                text=True
            )

            services = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                parts = line.split(':')
                if len(parts) >= 3:
                    services.append({
                        "name": parts[0],
                        "ports": parts[1],
                        "status": parts[2]
                    })

            return services

        except FileNotFoundError:
            logger.warning("Docker not installed or not in PATH")
            return []
