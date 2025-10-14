"""
Prometheus Metrics for Simulation Service

Defines and exports all KPIs from SERVICE_INFO.yaml:
- simulation_executions_total (counter)
- simulation_success_rate (gauge)
- simulation_duration_seconds (histogram)
- scenario_generation_quality_score (gauge)
- simulation_active_count (gauge)
- simulation_error_rate (gauge)
"""

from prometheus_client import Counter, Gauge, Histogram, Info
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# SERVICE INFO
# =============================================================================

service_info = Info(
    "simulation_service",
    "Simulation service information"
)

service_info.info({
    "version": "2.0.0",
    "type": "platform_service",
    "engines": "7",
    "api_endpoints": "31"
})


# =============================================================================
# KPI 1: simulation_executions_total (Counter)
# =============================================================================

simulation_executions_total = Counter(
    "simulation_executions_total",
    "Total number of simulation executions",
    labelnames=["simulation_type", "engine", "status", "tenant_id"]
)


# =============================================================================
# KPI 2: simulation_success_rate (Gauge)
# =============================================================================

simulation_success_count = Counter(
    "simulation_success_count",
    "Number of successful simulations",
    labelnames=["simulation_type", "tenant_id"]
)

simulation_failure_count = Counter(
    "simulation_failure_count",
    "Number of failed simulations",
    labelnames=["simulation_type", "tenant_id"]
)

simulation_success_rate = Gauge(
    "simulation_success_rate",
    "Percentage of successful simulation executions",
    labelnames=["simulation_type", "tenant_id"]
)


# =============================================================================
# KPI 3: simulation_duration_seconds (Histogram)
# =============================================================================

simulation_duration_seconds = Histogram(
    "simulation_duration_seconds",
    "Simulation execution duration in seconds",
    labelnames=["simulation_type", "engine", "tenant_id"],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600]
)


# =============================================================================
# KPI 4: scenario_generation_quality_score (Gauge)
# =============================================================================

scenario_generation_quality_score = Gauge(
    "scenario_generation_quality_score",
    "AI-generated scenario quality score (0-1)",
    labelnames=["scenario_category", "complexity", "tenant_id"]
)

scenario_generation_count = Counter(
    "scenario_generation_count",
    "Number of AI-generated scenarios",
    labelnames=["scenario_category", "complexity", "tenant_id"]
)


# =============================================================================
# KPI 5: simulation_active_count (Gauge)
# =============================================================================

simulation_active_count = Gauge(
    "simulation_active_count",
    "Number of currently running simulations",
    labelnames=["tenant_id"]
)


# =============================================================================
# KPI 6: simulation_error_rate (Gauge)
# =============================================================================

simulation_error_count = Counter(
    "simulation_error_count",
    "Number of simulation errors",
    labelnames=["error_type", "simulation_type", "tenant_id"]
)

simulation_error_rate = Gauge(
    "simulation_error_rate",
    "Percentage of failed operations",
    labelnames=["tenant_id"]
)


# =============================================================================
# ADDITIONAL METRICS (Operational)
# =============================================================================

api_requests_total = Counter(
    "simulation_api_requests_total",
    "Total API requests",
    labelnames=["method", "endpoint", "status_code"]
)

api_request_duration_seconds = Histogram(
    "simulation_api_request_duration_seconds",
    "API request duration in seconds",
    labelnames=["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10]
)

eventbus_events_published = Counter(
    "simulation_eventbus_events_published_total",
    "EventBus events published",
    labelnames=["event_type", "tenant_id"]
)

eventbus_events_received = Counter(
    "simulation_eventbus_events_received_total",
    "EventBus events received",
    labelnames=["event_type", "tenant_id"]
)

database_operations_total = Counter(
    "simulation_database_operations_total",
    "Database operations",
    labelnames=["operation", "table", "status"]
)

database_operation_duration_seconds = Histogram(
    "simulation_database_operation_duration_seconds",
    "Database operation duration in seconds",
    labelnames=["operation", "table"],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 2]
)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def record_simulation_execution(
    simulation_type: str,
    engine: str,
    status: str,
    duration_seconds: float,
    tenant_id: str = "default"
):
    """
    Record simulation execution metrics

    Args:
        simulation_type: Type of simulation
        engine: Engine used
        status: Status (completed, failed, cancelled)
        duration_seconds: Duration in seconds
        tenant_id: Tenant ID
    """
    # Total executions
    simulation_executions_total.labels(
        simulation_type=simulation_type,
        engine=engine,
        status=status,
        tenant_id=tenant_id
    ).inc()

    # Duration
    simulation_duration_seconds.labels(
        simulation_type=simulation_type,
        engine=engine,
        tenant_id=tenant_id
    ).observe(duration_seconds)

    # Success/failure counters
    if status == "completed":
        simulation_success_count.labels(
            simulation_type=simulation_type,
            tenant_id=tenant_id
        ).inc()
    elif status == "failed":
        simulation_failure_count.labels(
            simulation_type=simulation_type,
            tenant_id=tenant_id
        ).inc()

    logger.debug(f"Recorded simulation execution: {simulation_type} ({status})")


def record_scenario_generation(
    category: str,
    complexity: int,
    quality_score: float,
    tenant_id: str = "default"
):
    """
    Record scenario generation metrics

    Args:
        category: Scenario category
        complexity: Complexity level (1-5)
        quality_score: Quality score (0-1)
        tenant_id: Tenant ID
    """
    scenario_generation_count.labels(
        scenario_category=category,
        complexity=str(complexity),
        tenant_id=tenant_id
    ).inc()

    scenario_generation_quality_score.labels(
        scenario_category=category,
        complexity=str(complexity),
        tenant_id=tenant_id
    ).set(quality_score)

    logger.debug(f"Recorded scenario generation: {category} (quality: {quality_score})")


def update_active_simulations(count: int, tenant_id: str = "default"):
    """
    Update active simulation count

    Args:
        count: Number of active simulations
        tenant_id: Tenant ID
    """
    simulation_active_count.labels(tenant_id=tenant_id).set(count)


def record_error(
    error_type: str,
    simulation_type: str = "unknown",
    tenant_id: str = "default"
):
    """
    Record simulation error

    Args:
        error_type: Type of error
        simulation_type: Type of simulation
        tenant_id: Tenant ID
    """
    simulation_error_count.labels(
        error_type=error_type,
        simulation_type=simulation_type,
        tenant_id=tenant_id
    ).inc()

    logger.debug(f"Recorded error: {error_type}")


def calculate_success_rate(tenant_id: str = "default"):
    """
    Calculate and update success rate

    Args:
        tenant_id: Tenant ID
    """
    # This should be called periodically (e.g., every minute)
    # For now, it's a placeholder - actual calculation would need to
    # track counts over time windows
    pass


def record_api_request(
    method: str,
    endpoint: str,
    status_code: int,
    duration_seconds: float
):
    """
    Record API request metrics

    Args:
        method: HTTP method
        endpoint: API endpoint
        status_code: HTTP status code
        duration_seconds: Request duration
    """
    api_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status_code=str(status_code)
    ).inc()

    api_request_duration_seconds.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration_seconds)


def record_eventbus_event(event_type: str, direction: str, tenant_id: str = "default"):
    """
    Record EventBus event

    Args:
        event_type: Event type
        direction: "published" or "received"
        tenant_id: Tenant ID
    """
    if direction == "published":
        eventbus_events_published.labels(
            event_type=event_type,
            tenant_id=tenant_id
        ).inc()
    elif direction == "received":
        eventbus_events_received.labels(
            event_type=event_type,
            tenant_id=tenant_id
        ).inc()


def record_database_operation(
    operation: str,
    table: str,
    status: str,
    duration_seconds: float
):
    """
    Record database operation metrics

    Args:
        operation: Operation type (select, insert, update, delete)
        table: Table name
        status: Status (success, error)
        duration_seconds: Operation duration
    """
    database_operations_total.labels(
        operation=operation,
        table=table,
        status=status
    ).inc()

    database_operation_duration_seconds.labels(
        operation=operation,
        table=table
    ).observe(duration_seconds)
