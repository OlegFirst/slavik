"""
Resource Optimizer (Phase 1 - Task 1.3)
========================================

Optimizes resource allocation every 5 minutes.

Features:
- Collects resource metrics (CPU, memory, disk)
- Analyzes utilization (overutilized, underutilized, optimal)
- Generates optimization recommendations
- Publishes optimization events

Events:
- Publishes: infrastructure.optimization.completed
"""

import logging
import asyncio
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ResourceOptimizer:
    """
    Resource Optimizer Service

    Runs every 5 minutes:
    1. Collect resource metrics
    2. Analyze utilization
    3. Generate recommendations
    4. Publish events

    Example:
        ```python
        from infrastructure.eventbus import create_eventbus

        bus = create_eventbus('redis')
        optimizer = ResourceOptimizer(bus)

        await optimizer.start()  # Runs continuously every 5 min
        ```
    """

    def __init__(self, eventbus, decision_center=None):
        """
        Initialize Resource Optimizer

        Args:
            eventbus: EventBus instance (IEventBus)
            decision_center: Optional InfrastructureDecisionCenter instance (Phase 1.1)
        """
        self.eventbus = eventbus
        self.decision_center = decision_center
        self.optimization_interval = 300  # 5 minutes in seconds
        self.running = False
        self.cycles_completed = 0
        logger.info(f"ResourceOptimizer initialized (decision_center={'enabled' if decision_center else 'disabled'})")

    async def start(self):
        """Start optimization cycle"""
        self.running = True
        logger.info(" ResourceOptimizer started - running every 5 minutes")

        while self.running:
            try:
                await self._run_optimization_cycle()
                self.cycles_completed += 1
            except Exception as e:
                logger.error(f"Optimization cycle error: {e}")

            # Wait 5 minutes before next cycle
            if self.running:
                await asyncio.sleep(self.optimization_interval)

    async def stop(self):
        """Stop optimization cycle"""
        self.running = False
        logger.info("ResourceOptimizer stopped")

    async def _run_optimization_cycle(self):
        """Run single optimization cycle"""
        logger.info(f" Running resource optimization cycle #{self.cycles_completed + 1}...")

        # 1. Collect metrics
        metrics = await self._collect_metrics()

        # 2. Analyze utilization
        analysis = await self._analyze_utilization(metrics)

        # 3. Generate recommendations
        recommendations = await self._generate_recommendations(analysis)

        # 4. Calculate efficiency score
        efficiency_score = await self._calculate_efficiency_score(analysis)

        # 5. Apply recommendations (with Decision Center approval if enabled)
        if recommendations:
            await self._apply_recommendations(recommendations)

        # 6. Publish results
        from infrastructure.eventbus import Event
        await self.eventbus.publish(Event.create(
            event_type='infrastructure.optimization.completed',
            data={
                'cycle': self.cycles_completed + 1,
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': metrics,
                'analysis': analysis,
                'recommendations': recommendations,
                'efficiency_score': efficiency_score
            },
            source='resource_optimizer',
            tenant_id='system'
        ))

        logger.info(f" Optimization cycle #{self.cycles_completed + 1} completed")
        logger.info(f"   Efficiency score: {efficiency_score:.1f}/100")
        logger.info(f"   Recommendations: {len(recommendations)}")

        if recommendations:
            for rec in recommendations[:3]:  # Show top 3
                logger.info(f"   - {rec['service']}: {rec['action']} ({rec['priority']})")

    async def _collect_metrics(self) -> Dict[str, Any]:
        """
        Collect resource metrics from all services

        In production, would query Prometheus or system metrics.
        For Phase 1, returns mock data.

        Returns:
            Dict with resource metrics by service
        """
        # TODO: Replace with real Prometheus metrics
        # For now, return mock data
        metrics = {
            'cpu': {
                'eventbus': 45.0,
                'database': 72.0,
                'api_gateway': 58.0,
                'rag_pipeline': 35.0,
                'bia_service': 51.0,
                'planning_service': 42.0,
            },
            'memory': {
                'eventbus': 65.0,
                'database': 88.0,
                'api_gateway': 55.0,
                'rag_pipeline': 42.0,
                'bia_service': 68.0,
                'planning_service': 52.0,
            },
            'disk': {
                'database': 78.0,
                'documents_service': 65.0,
            }
        }

        logger.debug(f"Collected metrics for {len(set().union(*[m.keys() for m in metrics.values()]))} services")
        return metrics

    async def _analyze_utilization(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze resource utilization

        Categorizes services into:
        - overutilized: > 80%
        - underutilized: < 30%
        - optimal: 30-80%

        Args:
            metrics: Resource metrics

        Returns:
            Dict with categorized services
        """
        analysis = {
            'overutilized': [],
            'underutilized': [],
            'optimal': []
        }

        for resource_type, services in metrics.items():
            for service, utilization in services.items():
                entry = {
                    'service': service,
                    'resource': resource_type,
                    'utilization': utilization
                }

                if utilization > 80:
                    analysis['overutilized'].append(entry)
                elif utilization < 30:
                    analysis['underutilized'].append(entry)
                else:
                    analysis['optimal'].append(entry)

        logger.debug(f"Analysis: {len(analysis['overutilized'])} overutilized, "
                    f"{len(analysis['underutilized'])} underutilized, "
                    f"{len(analysis['optimal'])} optimal")

        return analysis

    async def _generate_recommendations(self, analysis: Dict[str, Any]) -> list:
        """
        Generate optimization recommendations

        Args:
            analysis: Utilization analysis

        Returns:
            List of recommendations
        """
        recommendations = []

        # Overutilized resources
        for item in analysis['overutilized']:
            action = 'scale_up' if item['utilization'] > 90 else 'optimize'
            priority = 'high' if item['utilization'] > 90 else 'medium'

            recommendations.append({
                'service': item['service'],
                'resource': item['resource'],
                'action': action,
                'priority': priority,
                'current_utilization': item['utilization'],
                'reason': f"{item['resource']} utilization at {item['utilization']:.1f}%"
            })

        # Underutilized resources
        for item in analysis['underutilized']:
            if item['utilization'] < 20:
                recommendations.append({
                    'service': item['service'],
                    'resource': item['resource'],
                    'action': 'scale_down',
                    'priority': 'low',
                    'current_utilization': item['utilization'],
                    'reason': f"{item['resource']} utilization only {item['utilization']:.1f}%"
                })

        # Sort by priority (high → medium → low)
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda r: priority_order[r['priority']])

        return recommendations

    async def _calculate_efficiency_score(self, analysis: Dict[str, Any]) -> float:
        """
        Calculate overall resource efficiency score (0-100)

        Args:
            analysis: Utilization analysis

        Returns:
            float: Efficiency score
        """
        total_resources = (
            len(analysis['overutilized']) +
            len(analysis['underutilized']) +
            len(analysis['optimal'])
        )

        if total_resources == 0:
            return 100.0

        optimal_count = len(analysis['optimal'])
        optimal_ratio = optimal_count / total_resources

        # Penalize overutilized (more critical than underutilized)
        overutilized_penalty = len(analysis['overutilized']) * 2
        underutilized_penalty = len(analysis['underutilized'])

        penalties = overutilized_penalty + underutilized_penalty
        max_penalties = total_resources * 2  # If all were overutilized

        efficiency = 100 * (1 - (penalties / max_penalties))

        return max(0, min(100, efficiency))

    async def _apply_recommendations(self, recommendations: list):
        """
        Apply optimization recommendations with Decision Center approval (Phase 1.1)

        Args:
            recommendations: List of optimization recommendations
        """
        if not self.decision_center:
            # No decision center, apply automatically (backward compatible)
            logger.info("Decision Center not enabled - applying optimizations automatically")
            for rec in recommendations:
                await self._apply_optimization(rec)
            return

        # WITH Decision Center: check each recommendation
        logger.info(f"Checking {len(recommendations)} recommendations with Decision Center...")

        for rec in recommendations:
            decision, can_proceed = await self.decision_center.decide_optimization_action(
                service_name=rec['service'],
                action_type=rec['action'],
                recommendation=rec
            )

            if can_proceed:
                logger.info(f"Optimization APPROVED: {rec['action']} for {rec['service']}")
                await self._apply_optimization(rec)
            elif decision.requires_approval:
                logger.info(f"Optimization PENDING approval: {rec['action']} for {rec['service']}")
                # Create approval request (handled by Decision Center)
                # In production, would wait for approval callback
            else:
                logger.warning(f"Optimization REJECTED: {rec['action']} for {rec['service']}")

    async def _apply_optimization(self, recommendation: Dict[str, Any]):
        """
        Apply a single optimization recommendation

        Args:
            recommendation: Optimization recommendation dict

        Note:
            In production, this would:
            - Scale up/down containers
            - Adjust resource limits
            - Trigger configuration changes
            For now, just logs the action.
        """
        service = recommendation['service']
        action = recommendation['action']
        resource = recommendation['resource']
        utilization = recommendation['current_utilization']

        logger.info(f" Applying optimization: {action} for {service} ({resource} @ {utilization:.1f}%)")

        # TODO: Implement actual optimization actions
        # Examples:
        # - Docker API to scale containers
        # - Kubernetes API to adjust replicas
        # - Update configuration files
        # - Trigger service restarts

        await asyncio.sleep(0.1)  # Simulate action
        logger.info(f" Optimization applied: {action} for {service}")

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get optimizer statistics

        Returns:
            Dict with stats
        """
        return {
            'running': self.running,
            'interval_seconds': self.optimization_interval,
            'cycles_completed': self.cycles_completed
        }
