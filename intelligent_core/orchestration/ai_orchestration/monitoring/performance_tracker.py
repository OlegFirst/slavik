"""
Performance Tracker
===================

Automated performance tracking and statistics collection for orchestrator.
"""

import time
import psutil
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque, defaultdict
import logging

from .metrics import orchestrator_metrics

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """
    Automated performance tracker

    Tracks and aggregates orchestrator performance metrics in real-time.
    Provides statistical analysis and performance insights.
    """

    def __init__(self, window_size: int = 3600):
        """
        Initialize performance tracker

        Args:
            window_size: Time window in seconds for rolling statistics (default: 1 hour)
        """
        self.window_size = window_size
        self.start_time = time.time()

        # Rolling windows for statistics
        self.request_times = deque(maxlen=10000)  # Last 10k requests
        self.task_times = deque(maxlen=10000)
        self.error_counts = defaultdict(int)
        self.task_stats = defaultdict(lambda: {
            'total': 0,
            'success': 0,
            'failure': 0,
            'total_duration': 0.0,
            'total_tokens': 0
        })

        # Agent tracking
        self.agent_stats = defaultdict(lambda: {
            'tasks_completed': 0,
            'total_duration': 0.0,
            'last_active': None,
            'idle_time': 0.0
        })

        # LLM tracking
        self.llm_stats = defaultdict(lambda: {
            'calls': 0,
            'tokens': 0,
            'cost': 0.0,
            'total_latency': 0.0
        })

        # Queue tracking
        self.queue_history = deque(maxlen=1000)

        # SLA tracking
        self.sla_violations = []

        # Background task for resource monitoring
        self._monitoring_task = None
        self._running = False

    async def start(self):
        """Start background monitoring"""
        if self._running:
            logger.warning("Performance tracker already running")
            return

        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitor_resources())
        logger.info("✅ Performance tracker started")

    async def stop(self):
        """Stop background monitoring"""
        self._running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Performance tracker stopped")

    async def _monitor_resources(self):
        """Background task to monitor system resources"""
        while self._running:
            try:
                # Update CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                orchestrator_metrics.orchestrator_cpu_usage.set(cpu_percent)

                # Update memory usage
                memory = psutil.virtual_memory()
                orchestrator_metrics.orchestrator_memory_usage.set(memory.used)

                # Update uptime
                orchestrator_metrics.update_uptime()

                await asyncio.sleep(10)  # Update every 10 seconds
            except Exception as e:
                logger.error(f"Error in resource monitoring: {e}")
                await asyncio.sleep(10)

    def track_request(self, method: str, endpoint: str, status: int, duration: float):
        """Track HTTP request"""
        self.request_times.append({
            'timestamp': time.time(),
            'method': method,
            'endpoint': endpoint,
            'status': status,
            'duration': duration
        })

        orchestrator_metrics.track_request(method, endpoint, status, duration)

    def track_task(
        self,
        task_type: str,
        agent: str,
        status: str,
        duration: float,
        tokens_used: int = 0,
        cost: float = 0.0
    ):
        """Track task execution"""
        # Update task statistics
        stats = self.task_stats[task_type]
        stats['total'] += 1
        if status == 'success':
            stats['success'] += 1
        else:
            stats['failure'] += 1
        stats['total_duration'] += duration
        stats['total_tokens'] += tokens_used

        # Update agent statistics
        agent_stat = self.agent_stats[agent]
        agent_stat['tasks_completed'] += 1
        agent_stat['total_duration'] += duration
        agent_stat['last_active'] = time.time()

        # Track in deque
        self.task_times.append({
            'timestamp': time.time(),
            'task_type': task_type,
            'agent': agent,
            'status': status,
            'duration': duration,
            'tokens': tokens_used,
            'cost': cost
        })

        # Update Prometheus metrics
        orchestrator_metrics.track_task(task_type, agent, status, duration, tokens_used)

        # Update success rate
        success_rate = (stats['success'] / stats['total']) * 100 if stats['total'] > 0 else 0
        orchestrator_metrics.update_success_rate(task_type, success_rate)

        # Track cost
        if cost > 0:
            orchestrator_metrics.orchestrator_cost.labels(resource_type='llm').inc(cost)

    def track_llm_call(
        self,
        model: str,
        provider: str,
        status: str,
        latency: float,
        tokens: int,
        cost: float = 0.0
    ):
        """Track LLM API call"""
        stats = self.llm_stats[f"{provider}/{model}"]
        stats['calls'] += 1
        stats['tokens'] += tokens
        stats['cost'] += cost
        stats['total_latency'] += latency

        orchestrator_metrics.track_llm_call(model, provider, status, latency, tokens)

    def track_agent_idle(self, agent_name: str, idle_duration: float):
        """Track agent idle time"""
        self.agent_stats[agent_name]['idle_time'] += idle_duration
        orchestrator_metrics.orchestrator_agent_idle_time.labels(agent_name=agent_name).inc(idle_duration)

    def track_queue(self, length: int, priority: str = 'normal'):
        """Track queue length"""
        self.queue_history.append({
            'timestamp': time.time(),
            'length': length,
            'priority': priority
        })
        orchestrator_metrics.update_queue_metrics(length, priority)

    def track_sla_violation(self, sla_type: str, severity: str, details: str):
        """Track SLA violation"""
        violation = {
            'timestamp': time.time(),
            'sla_type': sla_type,
            'severity': severity,
            'details': details
        }
        self.sla_violations.append(violation)
        orchestrator_metrics.track_sla_violation(sla_type, severity)

    def get_statistics(self, window_minutes: int = 60) -> Dict[str, Any]:
        """
        Get performance statistics for the specified time window

        Args:
            window_minutes: Time window in minutes (default: 60)

        Returns:
            Dictionary with comprehensive statistics
        """
        cutoff_time = time.time() - (window_minutes * 60)

        # Filter recent requests
        recent_requests = [r for r in self.request_times if r['timestamp'] > cutoff_time]
        recent_tasks = [t for t in self.task_times if t['timestamp'] > cutoff_time]

        # Calculate statistics
        stats = {
            'timestamp': datetime.utcnow().isoformat(),
            'window_minutes': window_minutes,
            'uptime_seconds': time.time() - self.start_time,

            # Performance metrics
            'performance': {
                'total_requests': len(recent_requests),
                'requests_per_minute': len(recent_requests) / window_minutes if window_minutes > 0 else 0,
                'avg_latency': sum(r['duration'] for r in recent_requests) / len(recent_requests) if recent_requests else 0,
                'p95_latency': self._percentile([r['duration'] for r in recent_requests], 95),
                'p99_latency': self._percentile([r['duration'] for r in recent_requests], 99),
            },

            # Task statistics
            'tasks': {
                'total': len(recent_tasks),
                'success': len([t for t in recent_tasks if t['status'] == 'success']),
                'failure': len([t for t in recent_tasks if t['status'] != 'success']),
                'success_rate': (len([t for t in recent_tasks if t['status'] == 'success']) / len(recent_tasks) * 100) if recent_tasks else 0,
                'avg_duration': sum(t['duration'] for t in recent_tasks) / len(recent_tasks) if recent_tasks else 0,
                'total_tokens': sum(t.get('tokens', 0) for t in recent_tasks),
                'total_cost': sum(t.get('cost', 0.0) for t in recent_tasks),
            },

            # Agent statistics
            'agents': self._get_agent_statistics(),

            # LLM statistics
            'llm': self._get_llm_statistics(),

            # Queue statistics
            'queue': self._get_queue_statistics(cutoff_time),

            # Resource usage
            'resources': {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_used_mb': psutil.virtual_memory().used / (1024 * 1024),
            },

            # SLA compliance
            'sla': {
                'violations': len([v for v in self.sla_violations if v['timestamp'] > cutoff_time]),
                'compliance_rate': self._calculate_sla_compliance(cutoff_time),
            }
        }

        return stats

    def get_task_statistics_by_type(self) -> Dict[str, Any]:
        """Get statistics broken down by task type"""
        return {
            task_type: {
                'total': stats['total'],
                'success': stats['success'],
                'failure': stats['failure'],
                'success_rate': (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0,
                'avg_duration': stats['total_duration'] / stats['total'] if stats['total'] > 0 else 0,
                'avg_tokens': stats['total_tokens'] / stats['total'] if stats['total'] > 0 else 0,
            }
            for task_type, stats in self.task_stats.items()
        }

    def get_agent_performance(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        return {
            agent_name: {
                'tasks_completed': stats['tasks_completed'],
                'avg_duration': stats['total_duration'] / stats['tasks_completed'] if stats['tasks_completed'] > 0 else 0,
                'utilization': self._calculate_agent_utilization(agent_name, stats),
                'idle_time_seconds': stats['idle_time'],
                'last_active': datetime.fromtimestamp(stats['last_active']).isoformat() if stats['last_active'] else None,
            }
            for agent_name, stats in self.agent_stats.items()
        }

    def _get_agent_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            'total_agents': len(self.agent_stats),
            'active_agents': len([s for s in self.agent_stats.values() if s['last_active'] and time.time() - s['last_active'] < 300]),
            'avg_utilization': sum(self._calculate_agent_utilization(name, stats) for name, stats in self.agent_stats.items()) / len(self.agent_stats) if self.agent_stats else 0,
        }

    def _get_llm_statistics(self) -> Dict[str, Any]:
        """Get LLM statistics"""
        return {
            model: {
                'calls': stats['calls'],
                'total_tokens': stats['tokens'],
                'total_cost': stats['cost'],
                'avg_latency': stats['total_latency'] / stats['calls'] if stats['calls'] > 0 else 0,
            }
            for model, stats in self.llm_stats.items()
        }

    def _get_queue_statistics(self, cutoff_time: float) -> Dict[str, Any]:
        """Get queue statistics"""
        recent_queue = [q for q in self.queue_history if q['timestamp'] > cutoff_time]
        if not recent_queue:
            return {'avg_length': 0, 'max_length': 0, 'current_length': 0}

        return {
            'avg_length': sum(q['length'] for q in recent_queue) / len(recent_queue),
            'max_length': max(q['length'] for q in recent_queue),
            'current_length': recent_queue[-1]['length'] if recent_queue else 0,
        }

    def _calculate_agent_utilization(self, agent_name: str, stats: Dict) -> float:
        """Calculate agent utilization percentage"""
        if stats['tasks_completed'] == 0:
            return 0.0

        uptime = time.time() - self.start_time
        active_time = stats['total_duration']
        return (active_time / uptime * 100) if uptime > 0 else 0.0

    def _calculate_sla_compliance(self, cutoff_time: float) -> float:
        """Calculate SLA compliance rate"""
        recent_violations = len([v for v in self.sla_violations if v['timestamp'] > cutoff_time])
        recent_tasks = len([t for t in self.task_times if t['timestamp'] > cutoff_time])

        if recent_tasks == 0:
            return 100.0

        return ((recent_tasks - recent_violations) / recent_tasks * 100)

    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * (percentile / 100))
        return sorted_data[min(index, len(sorted_data) - 1)]

    def reset_statistics(self):
        """Reset all statistics"""
        self.request_times.clear()
        self.task_times.clear()
        self.error_counts.clear()
        self.task_stats.clear()
        self.agent_stats.clear()
        self.llm_stats.clear()
        self.queue_history.clear()
        self.sla_violations.clear()
        self.start_time = time.time()
        logger.info("📊 Statistics reset")


# Global performance tracker instance
performance_tracker = PerformanceTracker()
