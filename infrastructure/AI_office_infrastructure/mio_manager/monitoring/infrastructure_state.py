"""
Infrastructure State Monitoring - UNIFIED MONITORING SYSTEM

Объединяет:
- Infrastructure state (ex central-brain)
- Resource tracking (from mio-manager)
- Service health (from service-discovery)
- Metrics (from Prometheus)
- Compliance (from project-manager)

Публикует всё в EventBus для координации с:
- balancer-service
- mio-manager
- orchestrator
- все остальные сервисы
"""

from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class InfrastructureState:
    """
    Полное состояние инфраструктуры

    Объединяет данные из:
    - Project Manager (порты, БД, метрики)
    - MIO Manager (ресурсы CPU/память)
    - Service Discovery (health checks)
    - Prometheus (метрики сервисов)
    """
    timestamp: datetime

    # Порты
    ports_available: int
    ports_used: int

    # Мониторинг
    prometheus_available: bool
    grafana_available: bool
    services_with_metrics: int

    # База данных
    postgres_available: bool
    redis_available: bool
    services_with_db: int

    # Сервисы
    total_services: int
    healthy_services: int
    unhealthy_services: int

    # Ресурсы (from mio-manager)
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None

    # Покрытие
    monitoring_coverage: float = 0.0  # 0-1
    database_coverage: float = 0.0    # 0-1
    health_check_coverage: float = 0.0  # 0-1


# ============================================================================
# UNIFIED MONITORING SYSTEM
# ============================================================================

class InfrastructureStateMonitor:
    """
    UNIFIED Infrastructure State Monitor

    ЕДИНАЯ СИСТЕМА МОНИТОРИНГА для всей платформы.

    Координация:
    1. Собирает данные из разных источников
    2. Объединяет в единое состояние
    3. Публикует в EventBus
    4. Принимает стратегические решения
    5. Отправляет рекомендации

    EventBus Events (ПУБЛИКУЕТ):
    - platform.infrastructure.state_updated (каждые 60s)
    - platform.infrastructure.emergency (critical issues)
    - platform.infrastructure.strategy_recommended (scaling strategy)
    - platform.infrastructure.resource_deficit (low resources)
    - platform.infrastructure.service_unhealthy (service down)

    EventBus Events (СЛУШАЕТ):
    - platform.service.registered (new service)
    - platform.service.unregistered (service down)
    - platform.resources.snapshot (from mio-manager)
    """

    def __init__(self, eventbus, config: Dict):
        """
        Args:
            eventbus: EventBus instance (для publishing)
            config: {
                'project_manager_enabled': bool,
                'mio_manager_enabled': bool,
                'service_discovery_enabled': bool,
                'prometheus_enabled': bool,
                'monitor_interval': int (seconds, default 60)
            }
        """
        self.eventbus = eventbus
        self.config = config

        # Current state
        self.current_state: Optional[InfrastructureState] = None
        self.state_history: List[InfrastructureState] = []
        self.max_history = 100

        # Integration clients (опционально, если доступны)
        self.project_manager = None
        self.mio_manager = None
        self.service_discovery = None
        self.prometheus = None

        # Monitoring task
        self.monitoring_task = None
        self.running = False

        logger.info("InfrastructureStateMonitor initialized")


    # ========================================================================
    # DATA COLLECTION from Multiple Sources
    # ========================================================================

    async def collect_state_from_devops_agent(self) -> Dict:
        """
        Собрать состояние из DevOps Agent (compliance checks)

        Previously: collect_state_from_project_manager()
        Now: DevOps Agent includes platform compliance toolkit

        Returns: {
            'ports_used': int,
            'prometheus_available': bool,
            'postgres_available': bool,
            'redis_available': bool,
            'services_with_metrics': int,
            'services_with_db': int,
            'total_services': int
        }
        """
        try:
            # Import DevOps Agent compliance toolkit
            import sys
            from pathlib import Path
            project_root = Path(__file__).parents[4]
            sys.path.insert(0, str(project_root / 'infrastructure' / 'AI-office-infrastructure' / 'devops-agent'))

            from tools import ComplianceRunner
            runner = ComplianceRunner()
            state_data = runner.export_state_for_mio_manager()

            # Extract data from compliance checks
            compliance_checks = state_data.get('compliance_checks', {})

            # Priority 1: Ports
            ports_check = compliance_checks.get('priority_1_ports', {})
            ports_used = ports_check.get('ports_used', 0)

            # Priority 2: Metrics
            metrics_check = compliance_checks.get('priority_2_metrics', {})
            prometheus_available = metrics_check.get('prometheus_available', False)
            grafana_available = metrics_check.get('grafana_available', False)
            services_with_metrics = metrics_check.get('services_with_metrics', 0)

            # Priority 3: Database
            db_check = compliance_checks.get('priority_3_database', {})
            postgres_available = db_check.get('postgres_available', False)
            redis_available = db_check.get('redis_available', False)
            services_with_db = db_check.get('services_connected', 0)

            total_services = max(
                metrics_check.get('total_services', 0),
                db_check.get('total_services', 0)
            )

            return {
                'ports_used': ports_used,
                'prometheus_available': prometheus_available,
                'grafana_available': grafana_available,
                'postgres_available': postgres_available,
                'redis_available': redis_available,
                'services_with_metrics': services_with_metrics,
                'services_with_db': services_with_db,
                'total_services': total_services,
                'overall_status': state_data.get('overall_status', 'UNKNOWN'),
                'summary': state_data.get('summary', {})
            }
        except Exception as e:
            logger.error(f"Failed to collect from DevOps Agent: {e}")
            return {}

    # Legacy compatibility
    async def collect_state_from_project_manager(self) -> Dict:
        """
        Legacy method - redirects to DevOps Agent

        DEPRECATED: Use collect_state_from_devops_agent() instead
        """
        logger.warning("collect_state_from_project_manager() is deprecated, use collect_state_from_devops_agent()")
        return await self.collect_state_from_devops_agent()


    async def collect_resources_from_mio_manager(self) -> Dict:
        """
        Собрать ресурсы из MIO Manager

        Returns: {
            'cpu_usage': float (0-1),
            'memory_usage': float (0-1),
            'disk_usage': float (0-1)
        }
        """
        try:
            # TODO: Call MIO Manager API or get from EventBus cache
            # For now, placeholder
            return {
                'cpu_usage': 0.0,
                'memory_usage': 0.0,
                'disk_usage': 0.0
            }
        except Exception as e:
            logger.error(f"Failed to collect from mio manager: {e}")
            return {}


    async def collect_health_from_service_discovery(self) -> Dict:
        """
        Собрать health checks из Service Discovery

        Returns: {
            'healthy_services': int,
            'unhealthy_services': int
        }
        """
        try:
            # TODO: Call Service Discovery API
            return {
                'healthy_services': 0,
                'unhealthy_services': 0
            }
        except Exception as e:
            logger.error(f"Failed to collect from service discovery: {e}")
            return {}


    # ========================================================================
    # STATE UPDATE with EventBus Publishing
    # ========================================================================

    async def update_state(self):
        """
        ГЛАВНЫЙ МЕТОД: Собрать состояние из всех источников и опубликовать
        """
        logger.info("Collecting infrastructure state from all sources...")

        # Collect from all sources
        pm_data = await self.collect_state_from_project_manager()
        mio_data = await self.collect_resources_from_mio_manager()
        sd_data = await self.collect_health_from_service_discovery()

        # Combine into unified state
        state = InfrastructureState(
            timestamp=datetime.utcnow(),
            ports_available=100 - pm_data.get('ports_used', 0),  # TODO: calculate properly
            ports_used=pm_data.get('ports_used', 0),
            prometheus_available=pm_data.get('prometheus_available', False),
            grafana_available=pm_data.get('grafana_available', False),
            services_with_metrics=pm_data.get('services_with_metrics', 0),
            postgres_available=pm_data.get('postgres_available', False),
            redis_available=pm_data.get('redis_available', False),
            services_with_db=pm_data.get('services_with_db', 0),
            total_services=pm_data.get('total_services', 0),
            healthy_services=sd_data.get('healthy_services', 0),
            unhealthy_services=sd_data.get('unhealthy_services', 0),
            cpu_usage=mio_data.get('cpu_usage'),
            memory_usage=mio_data.get('memory_usage'),
            disk_usage=mio_data.get('disk_usage'),
            monitoring_coverage=self._calculate_monitoring_coverage(pm_data),
            database_coverage=self._calculate_database_coverage(pm_data),
            health_check_coverage=self._calculate_health_coverage(sd_data, pm_data)
        )

        # Store
        self.current_state = state
        self.state_history.append(state)
        if len(self.state_history) > self.max_history:
            self.state_history = self.state_history[-self.max_history:]

        # PUBLISH to EventBus ✨
        await self._publish_state_updated(state)

        # Check for critical issues
        await self._check_and_publish_emergency(state)

        logger.info(f"State updated: {state.total_services} services, "
                   f"{state.monitoring_coverage*100:.0f}% monitoring coverage")


    async def _publish_state_updated(self, state: InfrastructureState):
        """Publish state_updated event to EventBus"""
        try:
            await self.eventbus.publish(
                'platform.infrastructure.state_updated',
                {
                    'state': asdict(state),
                    'timestamp': state.timestamp.isoformat()
                },
                priority='normal'
            )
            logger.debug("Published platform.infrastructure.state_updated")
        except Exception as e:
            logger.error(f"Failed to publish state_updated: {e}")


    async def _check_and_publish_emergency(self, state: InfrastructureState):
        """Check for critical issues and publish emergency event"""
        emergencies = []

        if not state.postgres_available:
            emergencies.append({
                'type': 'database_unavailable',
                'resource': 'postgres',
                'severity': 'critical'
            })

        if not state.redis_available:
            emergencies.append({
                'type': 'database_unavailable',
                'resource': 'redis',
                'severity': 'critical'
            })

        if not state.prometheus_available:
            emergencies.append({
                'type': 'monitoring_unavailable',
                'resource': 'prometheus',
                'severity': 'high'
            })

        if state.cpu_usage and state.cpu_usage > 0.9:
            emergencies.append({
                'type': 'resource_exhausted',
                'resource': 'cpu',
                'severity': 'high',
                'usage': state.cpu_usage
            })

        if state.memory_usage and state.memory_usage > 0.9:
            emergencies.append({
                'type': 'resource_exhausted',
                'resource': 'memory',
                'severity': 'high',
                'usage': state.memory_usage
            })

        # Publish each emergency
        for emergency in emergencies:
            try:
                await self.eventbus.publish(
                    'platform.infrastructure.emergency',
                    {
                        **emergency,
                        'state': asdict(state),
                        'timestamp': datetime.utcnow().isoformat()
                    },
                    priority='high'
                )
                logger.warning(f"Published emergency: {emergency['type']} - {emergency['resource']}")
            except Exception as e:
                logger.error(f"Failed to publish emergency: {e}")


    # ========================================================================
    # STRATEGIC DECISIONS (from central-brain logic)
    # ========================================================================

    def suggest_scaling_strategy(self) -> Dict:
        """
        Предложить стратегию масштабирования

        ЛОГИКА от central-brain (rule-based, но с EventBus publishing)
        """
        if not self.current_state:
            return {'strategy': 'unknown', 'reason': 'State not collected'}

        state = self.current_state

        # Emergency: Critical databases down
        if not state.postgres_available or not state.redis_available:
            return {
                'strategy': 'emergency',
                'priority': 'critical',
                'action': 'Restore critical databases immediately',
                'reason': 'Critical databases unavailable'
            }

        # High: Monitoring down
        if not state.prometheus_available:
            return {
                'strategy': 'monitoring_recovery',
                'priority': 'high',
                'action': 'Restore Prometheus monitoring',
                'reason': 'System running blind without monitoring'
            }

        # Medium: Low monitoring coverage
        if state.monitoring_coverage < 0.5:
            return {
                'strategy': 'improve_monitoring',
                'priority': 'medium',
                'action': 'Connect more services to Prometheus',
                'reason': f'Only {state.monitoring_coverage*100:.0f}% services monitored'
            }

        # Medium: Low DB coverage
        if state.database_coverage < 0.7:
            return {
                'strategy': 'improve_database_connectivity',
                'priority': 'medium',
                'action': 'Connect more services to databases',
                'reason': f'Only {state.database_coverage*100:.0f}% services connected to DB'
            }

        # High: Resource exhaustion
        if state.cpu_usage and state.cpu_usage > 0.85:
            return {
                'strategy': 'scale_resources',
                'priority': 'high',
                'action': 'Scale CPU resources or optimize services',
                'reason': f'CPU usage at {state.cpu_usage*100:.0f}%'
            }

        if state.memory_usage and state.memory_usage > 0.85:
            return {
                'strategy': 'scale_resources',
                'priority': 'high',
                'action': 'Scale memory resources or optimize services',
                'reason': f'Memory usage at {state.memory_usage*100:.0f}%'
            }

        # All good
        return {
            'strategy': 'maintain',
            'priority': 'low',
            'action': 'Maintain current state',
            'reason': 'System operating normally'
        }


    async def publish_strategy(self):
        """Generate and publish scaling strategy"""
        strategy = self.suggest_scaling_strategy()

        try:
            await self.eventbus.publish(
                'platform.infrastructure.strategy_recommended',
                {
                    'strategy': strategy,
                    'timestamp': datetime.utcnow().isoformat()
                },
                priority='normal'
            )
            logger.info(f"Published strategy: {strategy['strategy']} ({strategy['priority']})")
        except Exception as e:
            logger.error(f"Failed to publish strategy: {e}")


    # ========================================================================
    # CONTINUOUS MONITORING
    # ========================================================================

    async def start_continuous_monitoring(self):
        """Start continuous monitoring loop"""
        self.running = True
        interval = self.config.get('monitor_interval', 60)

        logger.info(f"Starting continuous monitoring (interval: {interval}s)")

        while self.running:
            try:
                # Update state
                await self.update_state()

                # Publish strategy
                await self.publish_strategy()

                # Sleep
                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                logger.info("Monitoring cancelled")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(5)  # Short pause on error


    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()


    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _calculate_monitoring_coverage(self, pm_data: Dict) -> float:
        """Calculate monitoring coverage percentage"""
        total = pm_data.get('total_services', 0)
        monitored = pm_data.get('services_with_metrics', 0)
        return monitored / total if total > 0 else 0.0

    def _calculate_database_coverage(self, pm_data: Dict) -> float:
        """Calculate database coverage percentage"""
        total = pm_data.get('total_services', 0)
        connected = pm_data.get('services_with_db', 0)
        return connected / total if total > 0 else 0.0

    def _calculate_health_coverage(self, sd_data: Dict, pm_data: Dict) -> float:
        """Calculate health check coverage percentage"""
        total = pm_data.get('total_services', 0)
        healthy = sd_data.get('healthy_services', 0)
        unhealthy = sd_data.get('unhealthy_services', 0)
        checked = healthy + unhealthy
        return checked / total if total > 0 else 0.0


    def get_available_resources(self) -> Dict:
        """Get available resources (API helper)"""
        if not self.current_state:
            return {'available': False, 'reason': 'State not collected'}

        state = self.current_state
        return {
            'available': True,
            'timestamp': state.timestamp.isoformat(),
            'can_allocate_port': state.ports_available > 10,
            'monitoring_available': state.prometheus_available and state.grafana_available,
            'monitoring_coverage': state.monitoring_coverage,
            'databases_available': state.postgres_available and state.redis_available,
            'database_coverage': state.database_coverage,
            'total_services': state.total_services,
            'healthy_services': state.healthy_services,
            'unhealthy_services': state.unhealthy_services,
            'system_healthy': (
                state.postgres_available and
                state.redis_available and
                state.prometheus_available and
                (state.cpu_usage or 0) < 0.85 and
                (state.memory_usage or 0) < 0.85
            )
        }


    def can_deploy_new_service(self, service_name: str,
                               requires_db: bool = True,
                               requires_metrics: bool = True) -> tuple[bool, str]:
        """Check if new service can be deployed"""
        if not self.current_state:
            return False, "Infrastructure state unknown"

        state = self.current_state

        if requires_db and not state.postgres_available:
            return False, "PostgreSQL unavailable"

        if requires_db and not state.redis_available:
            return False, "Redis unavailable"

        if requires_metrics and not state.prometheus_available:
            return False, "Prometheus unavailable (monitoring impossible)"

        if state.ports_available < 5:
            return False, "Insufficient free ports"

        if state.cpu_usage and state.cpu_usage > 0.85:
            return False, f"CPU usage too high ({state.cpu_usage*100:.0f}%)"

        if state.memory_usage and state.memory_usage > 0.85:
            return False, f"Memory usage too high ({state.memory_usage*100:.0f}%)"

        return True, "All required resources available"
