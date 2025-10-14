"""
Performance Evaluator - Оценка производительности и эффективности

МиО Manager использует этот модуль для:
- Оценки производительности каждого сервиса
- Расчета эффективности системы
- Выявления bottlenecks
- Расчета ROI метрик
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class ServicePerformance:
    """Оценка производительности одного сервиса"""
    service_name: str
    response_time_p95: float  # ms
    throughput: float  # req/s
    error_rate: float  # 0-1
    cpu_efficiency: float  # 0-1 (throughput/cpu)
    memory_efficiency: float  # 0-1
    health_score: float  # 0-100
    bottleneck_detected: bool
    bottleneck_type: Optional[str] = None  # 'cpu', 'memory', 'io', 'network'
    recommendation: str = ""


@dataclass
class SystemPerformance:
    """Оценка эффективности всей системы"""
    timestamp: datetime
    overall_health: float  # 0-100
    total_throughput: float
    avg_response_time: float
    system_error_rate: float
    resource_utilization: float  # 0-1
    bottlenecks: List[str]
    capacity_remaining: float  # 0-1
    efficiency_score: float  # 0-100
    roi_score: float  # 0-100
    service_performances: List[ServicePerformance]


class PerformanceEvaluator:
    """
    Оценивает производительность и эффективность системы

    МиО Manager использует для:
    - Мониторинга производительности каждого сервиса
    - Оценки эффективности использования ресурсов
    - Выявления bottlenecks и проблем
    - Расчета ROI и business value
    """

    def __init__(self, prometheus_url: str, eventbus):
        self.prometheus_url = prometheus_url
        self.eventbus = eventbus
        self.service_history: Dict[str, List[ServicePerformance]] = {}
        self.max_history = 100

    # ========================================================================
    # Service Performance Evaluation
    # ========================================================================

    async def evaluate_service_performance(self, service_name: str, metrics: Optional[Dict] = None) -> ServicePerformance:
        """
        Оценить производительность одного сервиса

        Args:
            service_name: Название сервиса
            metrics: Метрики (если уже собраны), иначе будут получены из Prometheus

        Returns:
            ServicePerformance с оценкой производительности
        """
        try:
            # Get metrics if not provided
            if not metrics:
                metrics = await self._get_service_metrics(service_name)

            # Calculate efficiency scores
            cpu_efficiency = self._calculate_cpu_efficiency(metrics)
            memory_efficiency = self._calculate_memory_efficiency(metrics)

            # Calculate health score (0-100)
            health_score = self._calculate_health_score(metrics)

            # Detect bottleneck
            bottleneck_type = self._detect_bottleneck(metrics)

            # Generate recommendation
            recommendation = self._generate_recommendation(metrics, bottleneck_type, health_score)

            performance = ServicePerformance(
                service_name=service_name,
                response_time_p95=metrics.get('response_time_p95', 0),
                throughput=metrics.get('throughput', 0),
                error_rate=metrics.get('error_rate', 0),
                cpu_efficiency=cpu_efficiency,
                memory_efficiency=memory_efficiency,
                health_score=health_score,
                bottleneck_detected=bottleneck_type is not None,
                bottleneck_type=bottleneck_type,
                recommendation=recommendation
            )

            # Store in history
            if service_name not in self.service_history:
                self.service_history[service_name] = []
            self.service_history[service_name].append(performance)
            if len(self.service_history[service_name]) > self.max_history:
                self.service_history[service_name] = self.service_history[service_name][-self.max_history:]

            return performance

        except Exception as e:
            logger.error(f"Failed to evaluate service {service_name}: {e}")
            # Return default performance
            return ServicePerformance(
                service_name=service_name,
                response_time_p95=0,
                throughput=0,
                error_rate=0,
                cpu_efficiency=0,
                memory_efficiency=0,
                health_score=50.0,
                bottleneck_detected=False,
                recommendation="Unable to evaluate - metrics unavailable"
            )

    # ========================================================================
    # System Performance Evaluation
    # ========================================================================

    async def evaluate_system_performance(self, infrastructure_state) -> SystemPerformance:
        """
        Оценить эффективность всей системы

        Args:
            infrastructure_state: InfrastructureState от InfrastructureStateMonitor

        Returns:
            SystemPerformance с оценкой системы
        """
        try:
            # Get list of services (placeholder - should come from service discovery)
            services = self._get_active_services(infrastructure_state)

            # Evaluate each service
            service_performances = []
            for service_name in services:
                perf = await self.evaluate_service_performance(service_name)
                service_performances.append(perf)

            if not service_performances:
                # No services to evaluate
                return self._get_default_system_performance()

            # Calculate system-wide metrics
            overall_health = sum(p.health_score for p in service_performances) / len(service_performances)
            total_throughput = sum(p.throughput for p in service_performances)
            avg_response_time = sum(p.response_time_p95 for p in service_performances) / len(service_performances)
            system_error_rate = sum(p.error_rate for p in service_performances) / len(service_performances)

            # Detect system bottlenecks
            bottlenecks = [p.service_name for p in service_performances if p.bottleneck_detected]

            # Calculate resource utilization
            resource_utilization = infrastructure_state.cpu_usage or 0.0

            # Calculate capacity remaining
            capacity_remaining = 1.0 - resource_utilization

            # Calculate efficiency score
            efficiency_score = self._calculate_efficiency_score(
                service_performances,
                infrastructure_state
            )

            # Calculate ROI score
            roi_score = self._calculate_roi_score(
                service_performances,
                infrastructure_state
            )

            return SystemPerformance(
                timestamp=datetime.utcnow(),
                overall_health=overall_health,
                total_throughput=total_throughput,
                avg_response_time=avg_response_time,
                system_error_rate=system_error_rate,
                resource_utilization=resource_utilization,
                bottlenecks=bottlenecks,
                capacity_remaining=capacity_remaining,
                efficiency_score=efficiency_score,
                roi_score=roi_score,
                service_performances=service_performances
            )

        except Exception as e:
            logger.error(f"Failed to evaluate system performance: {e}")
            return self._get_default_system_performance()

    # ========================================================================
    # EventBus Publishing
    # ========================================================================

    async def publish_evaluation(self, system_performance: SystemPerformance):
        """Публикация оценки производительности в EventBus"""
        try:
            await self.eventbus.publish(
                'platform.mio.performance_evaluation',
                {
                    'evaluation': asdict(system_performance),
                    'timestamp': system_performance.timestamp.isoformat(),
                    'summary': {
                        'overall_health': system_performance.overall_health,
                        'efficiency_score': system_performance.efficiency_score,
                        'bottlenecks_count': len(system_performance.bottlenecks),
                        'capacity_remaining': system_performance.capacity_remaining
                    }
                },
                priority='normal'
            )
            logger.info(f"Published performance evaluation: health={system_performance.overall_health:.1f}, "
                       f"efficiency={system_performance.efficiency_score:.1f}")
        except Exception as e:
            logger.error(f"Failed to publish evaluation: {e}")

    # ========================================================================
    # Helper Methods
    # ========================================================================

    async def _get_service_metrics(self, service_name: str) -> Dict:
        """Get service metrics from Prometheus (placeholder)"""
        # TODO: Implement Prometheus API call
        return {
            'response_time_p95': 100.0,  # ms
            'throughput': 10.0,  # req/s
            'error_rate': 0.01,  # 1%
            'cpu_usage': 0.3,
            'memory_usage': 0.5
        }

    def _get_active_services(self, infrastructure_state) -> List[str]:
        """Get list of active services (placeholder)"""
        # TODO: Get from service discovery
        return [
            'ai-event-manager',
            'balancer-service',
            'analytics-specialist',
            'mio-manager'
        ]

    def _calculate_cpu_efficiency(self, metrics: Dict) -> float:
        """Calculate CPU efficiency (throughput per CPU unit)"""
        cpu_usage = metrics.get('cpu_usage', 0.01)
        throughput = metrics.get('throughput', 0)
        return min(throughput / max(cpu_usage, 0.01), 100.0)

    def _calculate_memory_efficiency(self, metrics: Dict) -> float:
        """Calculate memory efficiency (throughput per memory unit)"""
        memory_usage = metrics.get('memory_usage', 0.01)
        throughput = metrics.get('throughput', 0)
        return min(throughput / max(memory_usage, 0.01), 100.0)

    def _calculate_health_score(self, metrics: Dict) -> float:
        """
        Calculate service health score (0-100)

        Based on:
        - Response time (40%)
        - Error rate (40%)
        - Resource usage (20%)
        """
        # Response time score (lower is better)
        response_time = metrics.get('response_time_p95', 0)
        if response_time < 50:
            response_score = 100
        elif response_time < 200:
            response_score = 100 - (response_time - 50) / 1.5
        elif response_time < 1000:
            response_score = 50 - (response_time - 200) / 16
        else:
            response_score = 0

        # Error rate score (lower is better)
        error_rate = metrics.get('error_rate', 0)
        error_score = max(0, 100 - error_rate * 1000)

        # Resource usage score (moderate is best)
        cpu_usage = metrics.get('cpu_usage', 0)
        if 0.3 < cpu_usage < 0.7:
            resource_score = 100
        elif cpu_usage < 0.3:
            resource_score = 70 + cpu_usage * 100
        else:
            resource_score = max(0, 100 - (cpu_usage - 0.7) * 200)

        # Weighted average
        health_score = (response_score * 0.4 + error_score * 0.4 + resource_score * 0.2)
        return max(0, min(100, health_score))

    def _detect_bottleneck(self, metrics: Dict) -> Optional[str]:
        """Detect bottleneck type"""
        cpu = metrics.get('cpu_usage', 0)
        memory = metrics.get('memory_usage', 0)
        error_rate = metrics.get('error_rate', 0)
        response_time = metrics.get('response_time_p95', 0)

        if cpu > 0.8:
            return 'cpu'
        elif memory > 0.8:
            return 'memory'
        elif response_time > 1000:
            return 'io'
        elif error_rate > 0.05:
            return 'errors'

        return None

    def _generate_recommendation(self, metrics: Dict, bottleneck_type: Optional[str], health_score: float) -> str:
        """Generate performance recommendation"""
        if health_score > 90:
            return "Excellent performance - maintain current configuration"

        if bottleneck_type == 'cpu':
            return "CPU bottleneck detected - consider scaling horizontally or optimizing CPU-intensive operations"
        elif bottleneck_type == 'memory':
            return "Memory bottleneck detected - investigate memory leaks or increase allocation"
        elif bottleneck_type == 'io':
            return "High latency detected - investigate database queries or external API calls"
        elif bottleneck_type == 'errors':
            return "High error rate - investigate application errors and fix bugs"

        if health_score < 70:
            return "Performance degraded - investigate recent changes and resource usage"

        return "Good performance - monitor for continued stability"

    def _calculate_efficiency_score(self, service_performances: List[ServicePerformance],
                                   infrastructure_state) -> float:
        """
        Calculate overall system efficiency (0-100)

        Based on:
        - Resource utilization vs throughput
        - Service health scores
        - Bottleneck presence
        """
        if not service_performances:
            return 50.0

        # Average service health
        avg_health = sum(p.health_score for p in service_performances) / len(service_performances)

        # Resource efficiency
        cpu_usage = infrastructure_state.cpu_usage or 0.5
        total_throughput = sum(p.throughput for p in service_performances)
        resource_efficiency = min(total_throughput / max(cpu_usage, 0.1), 100)

        # Bottleneck penalty
        bottleneck_count = sum(1 for p in service_performances if p.bottleneck_detected)
        bottleneck_penalty = bottleneck_count * 5  # -5 points per bottleneck

        # Calculate final score
        efficiency = (avg_health * 0.5 + resource_efficiency * 0.5) - bottleneck_penalty

        return max(0, min(100, efficiency))

    def _calculate_roi_score(self, service_performances: List[ServicePerformance],
                            infrastructure_state) -> float:
        """
        Calculate ROI score (0-100)

        Based on:
        - Value delivered (throughput, uptime)
        - Resources consumed (CPU, memory)
        """
        if not service_performances:
            return 50.0

        # Value delivered
        total_throughput = sum(p.throughput for p in service_performances)
        avg_uptime = 1.0 - (sum(p.error_rate for p in service_performances) / len(service_performances))

        # Resources consumed
        cpu_usage = infrastructure_state.cpu_usage or 0.5
        memory_usage = infrastructure_state.memory_usage or 0.5

        # ROI = Value / Cost
        value = total_throughput * avg_uptime
        cost = (cpu_usage + memory_usage) / 2

        roi = min(value / max(cost, 0.1), 100)

        return max(0, min(100, roi))

    def _get_default_system_performance(self) -> SystemPerformance:
        """Return default system performance when evaluation fails"""
        return SystemPerformance(
            timestamp=datetime.utcnow(),
            overall_health=50.0,
            total_throughput=0.0,
            avg_response_time=0.0,
            system_error_rate=0.0,
            resource_utilization=0.0,
            bottlenecks=[],
            capacity_remaining=1.0,
            efficiency_score=50.0,
            roi_score=50.0,
            service_performances=[]
        )
