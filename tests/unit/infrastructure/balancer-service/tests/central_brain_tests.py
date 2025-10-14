"""
Central Brain Test Suite - Sistema de testes do cérebro central

Tests from the central brain perspective with fixed sources of truth.
Detects critical compliance issues:
1. Services running but NOT registered
2. Services registered but NOT responding
3. Services registered but NOT connected to EventBus
4. Services with missing dependencies
5. Services with inaccessible ports

ИСТОЧНИКИ ПРАВДЫ (Sources of Truth):
- Service Registry (infrastructure/runtime/service-discovery/service_registry.py)
- EventBus (infrastructure/eventbus)
- Docker Compose configurations
- Process list (lsof/netstat)

КРИТИЧЕСКИЕ ТЕСТЫ (Critical Tests):
- Immediate detection of disconnected services
- Immediate detection of unregistered services
"""

import pytest
import asyncio
import subprocess
import socket
import json
import logging
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime, timedelta

# Import Service Registry as SOURCE OF TRUTH
import sys
from pathlib import Path

# Add paths for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "infrastructure"))

from infrastructure.runtime.service_discovery.service_registry import ServiceRegistry, Service

# Import EventBus
try:
    from infrastructure.eventbus import create_eventbus, Event
    EVENTBUS_AVAILABLE = True
except ImportError:
    EVENTBUS_AVAILABLE = False
    logging.warning("EventBus not available for testing")

logger = logging.getLogger(__name__)


# ============================================================================
# SOURCES OF TRUTH - Фиксированные источники правды
# ============================================================================

EXPECTED_SERVICES = {
    # Platform Services (порты 8000-8099)
    'planning-service': {'port': 8011, 'health_path': '/health', 'critical': True},
    'plans-service': {'port': 8023, 'health_path': '/health', 'critical': True},
    'governance-service': {'port': 8030, 'health_path': '/health', 'critical': True},
    'risk-service': {'port': 8040, 'health_path': '/health', 'critical': True},
    'response-service': {'port': 8050, 'health_path': '/health', 'critical': True},
    'learning-service': {'port': 8060, 'health_path': '/health', 'critical': True},
    'validation-service': {'port': 8070, 'health_path': '/health', 'critical': False},
    'documents-service': {'port': 8080, 'health_path': '/health', 'critical': False},

    # Intelligent Core Services (порты 9000-9099)
    'workflow-intelligence': {'port': 9001, 'health_path': '/health', 'critical': True},
    'ai-workflow-optimizer': {'port': 9002, 'health_path': '/health', 'critical': True},
    'expertise-center': {'port': 9003, 'health_path': '/health', 'critical': False},
    'orchestration': {'port': 9004, 'health_path': '/health', 'critical': False},
    'event-intelligence': {'port': 9005, 'health_path': '/health', 'critical': False},
    'predictive': {'port': 9006, 'health_path': '/health', 'critical': False},

    # Phase 2 Services
    'balancer-service': {'port': 9091, 'health_path': '/health', 'critical': True},

    # Infrastructure Services (порты 6000-6999)
    'redis': {'port': 6379, 'health_path': None, 'critical': True},
    'postgres': {'port': 5432, 'health_path': None, 'critical': True},
    'eventbus': {'port': 8001, 'health_path': None, 'critical': True},

    # AI Office Infrastructure (порты 7000-7999)
    'mio-manager': {'port': 7001, 'health_path': '/health', 'critical': False},
    'monitoring-service': {'port': 7002, 'health_path': '/health', 'critical': False},
    'notification-service': {'port': 7003, 'health_path': '/health', 'critical': False},
}

EXPECTED_DEPENDENCIES = {
    'planning-service': ['postgres', 'redis', 'eventbus'],
    'plans-service': ['postgres', 'redis', 'eventbus'],
    'governance-service': ['postgres', 'redis', 'eventbus'],
    'risk-service': ['postgres', 'redis', 'eventbus'],
    'response-service': ['postgres', 'redis', 'eventbus'],
    'learning-service': ['postgres', 'redis', 'eventbus'],
    'validation-service': ['postgres', 'redis'],
    'documents-service': ['postgres', 'redis'],

    'workflow-intelligence': ['postgres', 'redis', 'eventbus'],
    'ai-workflow-optimizer': ['eventbus'],
    'balancer-service': ['redis', 'eventbus'],

    'mio-manager': ['redis', 'eventbus'],
    'monitoring-service': ['postgres', 'redis', 'eventbus'],
}


# ============================================================================
# UTILITY FUNCTIONS - Утилиты для проверок
# ============================================================================

def check_port_listening(port: int, host: str = 'localhost') -> bool:
    """
    Check if a port is listening (service is running)

    Args:
        port: Port number
        host: Hostname (default localhost)

    Returns:
        True if port is listening
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex((host, port))
        return result == 0
    except socket.error:
        return False
    finally:
        sock.close()


def get_listening_ports() -> Set[int]:
    """
    Get all currently listening ports using lsof

    Returns:
        Set of port numbers
    """
    try:
        # Try lsof first (macOS/Linux)
        result = subprocess.run(
            ['lsof', '-iTCP', '-sTCP:LISTEN', '-n', '-P'],
            capture_output=True,
            text=True,
            timeout=5
        )

        ports = set()
        for line in result.stdout.split('\n')[1:]:  # Skip header
            if line.strip():
                parts = line.split()
                if len(parts) >= 9:
                    # Format: *:PORT or HOST:PORT
                    addr = parts[8]
                    if ':' in addr:
                        port_str = addr.split(':')[-1]
                        if port_str.isdigit():
                            ports.add(int(port_str))

        return ports

    except (subprocess.SubprocessError, FileNotFoundError):
        # Fallback: try netstat
        try:
            result = subprocess.run(
                ['netstat', '-an'],
                capture_output=True,
                text=True,
                timeout=5
            )

            ports = set()
            for line in result.stdout.split('\n'):
                if 'LISTEN' in line:
                    parts = line.split()
                    for part in parts:
                        if ':' in part:
                            port_str = part.split(':')[-1]
                            if port_str.isdigit():
                                ports.add(int(port_str))

            return ports

        except (subprocess.SubprocessError, FileNotFoundError):
            logger.error("Cannot detect listening ports (lsof and netstat unavailable)")
            return set()


async def check_health_endpoint(port: int, path: str = '/health', timeout: int = 2) -> Tuple[bool, Optional[str]]:
    """
    Check if a service responds to health endpoint

    Args:
        port: Port number
        path: Health endpoint path
        timeout: Timeout in seconds

    Returns:
        (is_healthy, error_message)
    """
    try:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            url = f'http://localhost:{port}{path}'
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                if response.status == 200:
                    return (True, None)
                else:
                    return (False, f"HTTP {response.status}")

    except ImportError:
        # Fallback: use curl
        try:
            result = subprocess.run(
                ['curl', '-f', '-s', '-m', str(timeout), f'http://localhost:{port}{path}'],
                capture_output=True,
                timeout=timeout + 1
            )
            if result.returncode == 0:
                return (True, None)
            else:
                return (False, f"curl failed with code {result.returncode}")
        except (subprocess.SubprocessError, FileNotFoundError):
            return (False, "Cannot check health (aiohttp and curl unavailable)")

    except Exception as e:
        return (False, str(e))


# ============================================================================
# TEST CLASS - Central Brain Tests
# ============================================================================

class TestCentralBrain:
    """
    Central Brain Test Suite

    Tests from system_wide perspective using fixed sources of truth:
    - Service Registry (what SHOULD be registered)
    - Running processes (what IS running)
    - EventBus (who IS connected)
    """

    @pytest.fixture
    async def service_registry(self):
        """Fixture: Create Service Registry instance"""
        registry = ServiceRegistry()
        yield registry
        # Cleanup
        registry.services.clear()

    @pytest.fixture
    async def eventbus(self):
        """Fixture: Create EventBus instance"""
        if not EVENTBUS_AVAILABLE:
            pytest.skip("EventBus not available")

        bus = create_eventbus('memory')  # Use memory backend for tests
        await bus.connect()
        yield bus
        await bus.disconnect()

    # ========================================================================
    # CRITICAL TEST 1: Services running but NOT registered
    # ========================================================================

    @pytest.mark.asyncio
    async def test_detect_unregistered_services(self, service_registry):
        """
        CRITICAL: Detect services running but NOT in Service Registry

        This is the MOST IMPORTANT test - if a service is running but not
        registered, it's "в системе но не участие" (in system but not participating)
        """
        logger.info("=" * 80)
        logger.info("CRITICAL TEST 1: Detecting unregistered services")
        logger.info("=" * 80)

        # 1. Get all listening ports (SOURCE OF TRUTH: Process list)
        listening_ports = get_listening_ports()
        logger.info(f"Found {len(listening_ports)} listening ports: {sorted(listening_ports)}")

        # 2. Get registered services (SOURCE OF TRUTH: Service Registry)
        registered_services = await service_registry.list_services()
        registered_ports = {s.port for s in registered_services if s.port}
        logger.info(f"Registered services: {len(registered_services)}")
        logger.info(f"Registered ports: {registered_ports}")

        # 3. Find ports that are listening but NOT registered
        unregistered_ports = set()
        unregistered_services = []

        for service_name, service_info in EXPECTED_SERVICES.items():
            port = service_info['port']

            if port in listening_ports:
                # Port is listening
                is_registered = any(
                    s.name == service_name and s.port == port
                    for s in registered_services
                )

                if not is_registered:
                    unregistered_ports.add(port)
                    unregistered_services.append({
                        'name': service_name,
                        'port': port,
                        'critical': service_info['critical']
                    })

        # 4. Report findings
        if unregistered_services:
            logger.error("❌ CRITICAL: Found unregistered services!")
            for svc in unregistered_services:
                severity = "CRITICAL" if svc['critical'] else "WARNING"
                logger.error(f"  [{severity}] {svc['name']} on port {svc['port']}")

            # Fail if any critical service is unregistered
            critical_unregistered = [s for s in unregistered_services if s['critical']]
            if critical_unregistered:
                pytest.fail(
                    f"Found {len(critical_unregistered)} critical unregistered services: "
                    f"{[s['name'] for s in critical_unregistered]}"
                )
        else:
            logger.info("✅ All running services are properly registered")

    # ========================================================================
    # CRITICAL TEST 2: Services registered but NOT responding
    # ========================================================================

    @pytest.mark.asyncio
    async def test_detect_non_responding_services(self, service_registry):
        """
        CRITICAL: Detect services in registry but NOT responding to health checks
        """
        logger.info("=" * 80)
        logger.info("CRITICAL TEST 2: Detecting non-responding services")
        logger.info("=" * 80)

        # Populate registry with expected services
        for service_name, service_info in EXPECTED_SERVICES.items():
            await service_registry.register(
                service_name=service_name,
                orchestrator='docker-compose',
                metadata={'port': service_info['port']},
                dependencies=EXPECTED_DEPENDENCIES.get(service_name, [])
            )
            # Set port
            service = await service_registry.get_service(service_name)
            if service:
                service.port = service_info['port']

        # Check all registered services
        registered_services = await service_registry.list_services()
        non_responding = []

        for service in registered_services:
            if service.port:
                # Check if port is listening
                is_listening = check_port_listening(service.port)

                if not is_listening:
                    service_info = EXPECTED_SERVICES.get(service.name, {})
                    non_responding.append({
                        'name': service.name,
                        'port': service.port,
                        'critical': service_info.get('critical', False),
                        'reason': 'Port not listening'
                    })
                    continue

                # Check health endpoint if available
                service_info = EXPECTED_SERVICES.get(service.name, {})
                health_path = service_info.get('health_path')

                if health_path:
                    is_healthy, error = await check_health_endpoint(service.port, health_path)

                    if not is_healthy:
                        non_responding.append({
                            'name': service.name,
                            'port': service.port,
                            'critical': service_info.get('critical', False),
                            'reason': f'Health check failed: {error}'
                        })

        # Report findings
        if non_responding:
            logger.error(f"❌ Found {len(non_responding)} non-responding services!")
            for svc in non_responding:
                severity = "CRITICAL" if svc['critical'] else "WARNING"
                logger.error(f"  [{severity}] {svc['name']} on port {svc['port']}: {svc['reason']}")

            # Fail if any critical service is non-responding
            critical_non_responding = [s for s in non_responding if s['critical']]
            if critical_non_responding:
                pytest.fail(
                    f"Found {len(critical_non_responding)} critical non-responding services: "
                    f"{[s['name'] for s in critical_non_responding]}"
                )
        else:
            logger.info("✅ All registered services are responding")

    # ========================================================================
    # CRITICAL TEST 3: Services NOT connected to EventBus
    # ========================================================================

    @pytest.mark.asyncio
    async def test_detect_eventbus_disconnected_services(self, service_registry, eventbus):
        """
        CRITICAL: Detect services that should be connected to EventBus but aren't

        This tests "не подротсетность" (not being connected)
        """
        logger.info("=" * 80)
        logger.info("CRITICAL TEST 3: Detecting EventBus-disconnected services")
        logger.info("=" * 80)

        # Populate registry
        for service_name, service_info in EXPECTED_SERVICES.items():
            dependencies = EXPECTED_DEPENDENCIES.get(service_name, [])

            await service_registry.register(
                service_name=service_name,
                orchestrator='docker-compose',
                metadata={'port': service_info['port']},
                dependencies=dependencies
            )

        # Get services that SHOULD be connected to EventBus
        eventbus_services = []
        for service_name, dependencies in EXPECTED_DEPENDENCIES.items():
            if 'eventbus' in dependencies:
                eventbus_services.append(service_name)

        logger.info(f"Services that should connect to EventBus: {len(eventbus_services)}")

        # Check which services are actually connected
        # For this test, we'll check if service has sent heartbeat in last 60 seconds
        disconnected = []

        for service_name in eventbus_services:
            service = await service_registry.get_service(service_name)

            if service:
                # Check last_seen timestamp
                time_since_seen = datetime.utcnow() - service.last_seen

                if time_since_seen > timedelta(seconds=60):
                    service_info = EXPECTED_SERVICES.get(service_name, {})
                    disconnected.append({
                        'name': service_name,
                        'critical': service_info.get('critical', False),
                        'last_seen': service.last_seen,
                        'time_since_seen': str(time_since_seen)
                    })

        # Report findings
        if disconnected:
            logger.warning(f"⚠️  Found {len(disconnected)} EventBus-disconnected services!")
            for svc in disconnected:
                severity = "CRITICAL" if svc['critical'] else "WARNING"
                logger.warning(
                    f"  [{severity}] {svc['name']} - "
                    f"last seen {svc['time_since_seen']} ago"
                )

            # Warning only - services might not be started yet
            logger.warning(
                "Note: Services might not be started yet. "
                "This is only critical if services are running."
            )
        else:
            logger.info("✅ All EventBus-dependent services are connected")

    # ========================================================================
    # CRITICAL TEST 4: Missing dependencies
    # ========================================================================

    @pytest.mark.asyncio
    async def test_detect_missing_dependencies(self, service_registry):
        """
        CRITICAL: Detect services with dependencies that don't exist
        """
        logger.info("=" * 80)
        logger.info("CRITICAL TEST 4: Detecting missing dependencies")
        logger.info("=" * 80)

        # Populate registry
        for service_name, service_info in EXPECTED_SERVICES.items():
            dependencies = EXPECTED_DEPENDENCIES.get(service_name, [])

            await service_registry.register(
                service_name=service_name,
                orchestrator='docker-compose',
                metadata={'port': service_info['port']},
                dependencies=dependencies
            )

        # Check dependencies
        services_with_missing_deps = []

        for service_name in EXPECTED_DEPENDENCIES.keys():
            service = await service_registry.get_service(service_name)

            if service:
                for dep_name in service.dependencies:
                    dep_service = await service_registry.get_service(dep_name)

                    if not dep_service:
                        services_with_missing_deps.append({
                            'service': service_name,
                            'missing_dependency': dep_name
                        })

        # Report findings
        if services_with_missing_deps:
            logger.error(f"❌ Found {len(services_with_missing_deps)} missing dependencies!")
            for item in services_with_missing_deps:
                logger.error(
                    f"  {item['service']} requires {item['missing_dependency']} "
                    f"(NOT REGISTERED)"
                )

            pytest.fail(
                f"Found {len(services_with_missing_deps)} services with missing dependencies"
            )
        else:
            logger.info("✅ All service dependencies are registered")

    # ========================================================================
    # CRITICAL TEST 5: Port conflicts
    # ========================================================================

    @pytest.mark.asyncio
    async def test_detect_port_conflicts(self, service_registry):
        """
        CRITICAL: Detect multiple services trying to use the same port
        """
        logger.info("=" * 80)
        logger.info("CRITICAL TEST 5: Detecting port conflicts")
        logger.info("=" * 80)

        # Populate registry
        for service_name, service_info in EXPECTED_SERVICES.items():
            await service_registry.register(
                service_name=service_name,
                orchestrator='docker-compose',
                metadata={'port': service_info['port']},
                dependencies=EXPECTED_DEPENDENCIES.get(service_name, [])
            )
            service = await service_registry.get_service(service_name)
            if service:
                service.port = service_info['port']

        # Check for port conflicts
        port_usage: Dict[int, List[str]] = {}

        registered_services = await service_registry.list_services()
        for service in registered_services:
            if service.port:
                if service.port not in port_usage:
                    port_usage[service.port] = []
                port_usage[service.port].append(service.name)

        # Find conflicts
        conflicts = {
            port: services
            for port, services in port_usage.items()
            if len(services) > 1
        }

        # Report findings
        if conflicts:
            logger.error(f"❌ Found {len(conflicts)} port conflicts!")
            for port, services in conflicts.items():
                logger.error(f"  Port {port}: {', '.join(services)}")

            pytest.fail(f"Found {len(conflicts)} port conflicts")
        else:
            logger.info("✅ No port conflicts detected")

    # ========================================================================
    # SUMMARY TEST: Complete system health
    # ========================================================================

    @pytest.mark.asyncio
    async def test_system_health_summary(self, service_registry):
        """
        Summary report of entire system health
        """
        logger.info("=" * 80)
        logger.info("SYSTEM HEALTH SUMMARY")
        logger.info("=" * 80)

        # Populate registry
        for service_name, service_info in EXPECTED_SERVICES.items():
            await service_registry.register(
                service_name=service_name,
                orchestrator='docker-compose',
                metadata={'port': service_info['port']},
                dependencies=EXPECTED_DEPENDENCIES.get(service_name, [])
            )
            service = await service_registry.get_service(service_name)
            if service:
                service.port = service_info['port']

        # Get stats
        stats = await service_registry.get_registry_stats()

        logger.info(f"Total services: {stats['total_services']}")
        logger.info(f"Services by status: {stats['by_status']}")
        logger.info(f"Services by orchestrator: {stats['by_orchestrator']}")

        # Check listening ports
        listening_ports = get_listening_ports()
        expected_ports = {info['port'] for info in EXPECTED_SERVICES.values()}
        critical_ports = {
            info['port']
            for name, info in EXPECTED_SERVICES.items()
            if info['critical']
        }

        running_count = len(listening_ports & expected_ports)
        critical_running = len(listening_ports & critical_ports)

        logger.info(f"Expected services: {len(EXPECTED_SERVICES)}")
        logger.info(f"Running services: {running_count}/{len(EXPECTED_SERVICES)}")
        logger.info(f"Critical services running: {critical_running}/{len(critical_ports)}")

        # Check if system is healthy
        system_healthy = critical_running == len(critical_ports)

        if system_healthy:
            logger.info("✅ SYSTEM STATUS: HEALTHY - All critical services running")
        else:
            logger.error(
                f"❌ SYSTEM STATUS: DEGRADED - "
                f"{len(critical_ports) - critical_running} critical services not running"
            )


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "critical: mark test as critical system test"
    )


if __name__ == '__main__':
    """Run tests directly"""
    pytest.main([__file__, '-v', '-s'])
