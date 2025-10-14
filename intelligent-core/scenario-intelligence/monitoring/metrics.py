"""
Prometheus Metrics for Scenario Intelligence

Provides metrics for:
- Scenario generation (counts, duration, success rate)
- Scenario execution (counts, duration, success rate)
- Storage operations (queries, writes)
- EventBus events (published, received)
"""

import logging
from typing import Optional
from prometheus_client import Counter, Histogram, Gauge, Info
import time

logger = logging.getLogger(__name__)

# ===================================================
# SCENARIO GENERATION METRICS
# ===================================================

# Generation counters
scenarios_generated_total = Counter(
    'scenario_intelligence_scenarios_generated_total',
    'Total number of scenarios generated',
    ['level', 'generator', 'trigger']
)

scenarios_generation_errors_total = Counter(
    'scenario_intelligence_generation_errors_total',
    'Total number of generation errors',
    ['level', 'generator', 'error_type']
)

# Generation duration
scenarios_generation_duration_seconds = Histogram(
    'scenario_intelligence_generation_duration_seconds',
    'Duration of scenario generation in seconds',
    ['level', 'generator'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
)

# Active generations
scenarios_generation_in_progress = Gauge(
    'scenario_intelligence_generation_in_progress',
    'Number of scenario generations currently in progress',
    ['level']
)

# ===================================================
# SCENARIO EXECUTION METRICS
# ===================================================

# Execution counters
scenarios_executed_total = Counter(
    'scenario_intelligence_scenarios_executed_total',
    'Total number of scenarios executed',
    ['level', 'status']
)

scenarios_execution_steps_total = Counter(
    'scenario_intelligence_execution_steps_total',
    'Total number of execution steps',
    ['status']
)

# Execution duration
scenarios_execution_duration_seconds = Histogram(
    'scenario_intelligence_execution_duration_seconds',
    'Duration of scenario execution in seconds',
    ['level'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
)

# Active executions
scenarios_execution_in_progress = Gauge(
    'scenario_intelligence_execution_in_progress',
    'Number of scenario executions currently in progress'
)

# ===================================================
# STORAGE METRICS
# ===================================================

# Storage operations
storage_operations_total = Counter(
    'scenario_intelligence_storage_operations_total',
    'Total number of storage operations',
    ['backend', 'operation', 'status']
)

storage_operation_duration_seconds = Histogram(
    'scenario_intelligence_storage_operation_duration_seconds',
    'Duration of storage operations in seconds',
    ['backend', 'operation'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

# Storage state
scenarios_in_storage = Gauge(
    'scenario_intelligence_scenarios_in_storage',
    'Number of scenarios in storage',
    ['backend', 'level']
)

# ===================================================
# EVENTBUS METRICS
# ===================================================

# EventBus events
eventbus_events_published_total = Counter(
    'scenario_intelligence_eventbus_events_published_total',
    'Total number of EventBus events published',
    ['event_type']
)

eventbus_events_received_total = Counter(
    'scenario_intelligence_eventbus_events_received_total',
    'Total number of EventBus events received',
    ['event_type']
)

eventbus_errors_total = Counter(
    'scenario_intelligence_eventbus_errors_total',
    'Total number of EventBus errors',
    ['error_type']
)

# ===================================================
# SYSTEM METRICS
# ===================================================

# System info
system_info = Info(
    'scenario_intelligence_system_info',
    'System information'
)

# Set system info
system_info.info({
    'service': 'scenario-intelligence',
    'version': '1.0.0',
    'component': 'intelligent-core'
})

# ===================================================
# HELPER CLASSES
# ===================================================

class GenerationMetricsContext:
    """Context manager for tracking generation metrics"""

    def __init__(self, level: str, generator: str):
        self.level = level
        self.generator = generator
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        scenarios_generation_in_progress.labels(level=self.level).inc()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        scenarios_generation_in_progress.labels(level=self.level).dec()

        if exc_type is None:
            # Success
            scenarios_generation_duration_seconds.labels(
                level=self.level,
                generator=self.generator
            ).observe(duration)
        else:
            # Error
            error_type = exc_type.__name__ if exc_type else 'unknown'
            scenarios_generation_errors_total.labels(
                level=self.level,
                generator=self.generator,
                error_type=error_type
            ).inc()

        return False  # Don't suppress exceptions


class ExecutionMetricsContext:
    """Context manager for tracking execution metrics"""

    def __init__(self, level: str):
        self.level = level
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        scenarios_execution_in_progress.inc()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        scenarios_execution_in_progress.dec()

        status = 'success' if exc_type is None else 'failed'

        scenarios_execution_duration_seconds.labels(
            level=self.level
        ).observe(duration)

        scenarios_executed_total.labels(
            level=self.level,
            status=status
        ).inc()

        return False  # Don't suppress exceptions


class StorageMetricsContext:
    """Context manager for tracking storage metrics"""

    def __init__(self, backend: str, operation: str):
        self.backend = backend
        self.operation = operation
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        status = 'success' if exc_type is None else 'failed'

        storage_operations_total.labels(
            backend=self.backend,
            operation=self.operation,
            status=status
        ).inc()

        storage_operation_duration_seconds.labels(
            backend=self.backend,
            operation=self.operation
        ).observe(duration)

        return False  # Don't suppress exceptions


# ===================================================
# CONVENIENCE FUNCTIONS
# ===================================================

def record_scenario_generated(level: str, generator: str, trigger: str, count: int = 1):
    """Record scenario generation"""
    scenarios_generated_total.labels(
        level=level,
        generator=generator,
        trigger=trigger
    ).inc(count)


def record_scenario_executed(level: str, status: str, duration_seconds: float, steps_successful: int, steps_failed: int):
    """Record scenario execution"""
    scenarios_executed_total.labels(
        level=level,
        status=status
    ).inc()

    scenarios_execution_duration_seconds.labels(
        level=level
    ).observe(duration_seconds)

    scenarios_execution_steps_total.labels(
        status='success'
    ).inc(steps_successful)

    scenarios_execution_steps_total.labels(
        status='failed'
    ).inc(steps_failed)


def record_eventbus_event_published(event_type: str):
    """Record EventBus event published"""
    eventbus_events_published_total.labels(
        event_type=event_type
    ).inc()


def record_eventbus_event_received(event_type: str):
    """Record EventBus event received"""
    eventbus_events_received_total.labels(
        event_type=event_type
    ).inc()


def record_eventbus_error(error_type: str):
    """Record EventBus error"""
    eventbus_errors_total.labels(
        error_type=error_type
    ).inc()


def update_storage_count(backend: str, level: str, count: int):
    """Update scenario count in storage"""
    scenarios_in_storage.labels(
        backend=backend,
        level=level
    ).set(count)


if __name__ == "__main__":
    # Test metrics
    print("Testing Scenario Intelligence metrics...")

    # Simulate generation
    with GenerationMetricsContext(level='l1', generator='l1_platform') as ctx:
        time.sleep(0.1)
        record_scenario_generated('l1', 'l1_platform', 'manual', 5)

    # Simulate execution
    with ExecutionMetricsContext(level='l1') as ctx:
        time.sleep(0.05)
        record_scenario_executed('l1', 'success', 0.05, 3, 0)

    # Simulate storage
    with StorageMetricsContext(backend='postgres', operation='write') as ctx:
        time.sleep(0.01)

    # Simulate EventBus
    record_eventbus_event_published('scenario.generated')

    print("✅ Metrics test complete")
