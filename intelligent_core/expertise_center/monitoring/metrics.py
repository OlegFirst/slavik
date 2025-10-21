"""
 Prometheus Metrics for Expertise Center

Tracks:
- Analyzer operations (10 analyzers: lifecycle, impact, performance, etc.)
- Specialist calls (6 tactical assistants: bia, compliance, etc.)
- HTTP calls to external services (76 HTTP calls tracked)
- Circuit breaker states (for resilience)
- Cache performance (analyzer result caching)
"""

from prometheus_client import Counter, Histogram, Gauge, Info
import time
from functools import wraps
from typing import Callable
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# METRICS DEFINITIONS
# ============================================================================

# Analyzer Metrics (10 analyzers)
analyzer_calls_total = Counter(
    'expertise_center_analyzer_calls_total',
    'Total number of analyzer calls',
    ['analyzer_name', 'domain', 'status']
)

analyzer_duration_seconds = Histogram(
    'expertise_center_analyzer_duration_seconds',
    'Time spent in analyzer execution',
    ['analyzer_name', 'domain'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

analyzer_errors_total = Counter(
    'expertise_center_analyzer_errors_total',
    'Total number of analyzer errors',
    ['analyzer_name', 'error_type']
)

analyzer_recommendations_total = Counter(
    'expertise_center_analyzer_recommendations_total',
    'Total recommendations generated',
    ['analyzer_name', 'recommendation_type']
)

# HTTP Call Metrics (76 HTTP calls across analyzers)
analyzer_http_calls_total = Counter(
    'expertise_center_analyzer_http_calls_total',
    'Total HTTP calls made by analyzers',
    ['analyzer_name', 'target_service', 'method', 'status']
)

analyzer_http_call_duration_seconds = Histogram(
    'expertise_center_analyzer_http_call_duration_seconds',
    'HTTP call duration from analyzers',
    ['analyzer_name', 'target_service', 'method'],
    buckets=[0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Specialist Metrics (6 tactical assistants)
specialist_calls_total = Counter(
    'expertise_center_specialist_calls_total',
    'Total specialist calls',
    ['specialist_name', 'operation', 'status']
)

specialist_duration_seconds = Histogram(
    'expertise_center_specialist_duration_seconds',
    'Specialist operation duration',
    ['specialist_name', 'operation'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

specialist_results_quality = Gauge(
    'expertise_center_specialist_results_quality',
    'Quality score of specialist results (0-1)',
    ['specialist_name']
)

# Strategic Planner Metrics
strategic_plan_generations_total = Counter(
    'expertise_center_strategic_plan_generations_total',
    'Total strategic plans generated',
    ['plan_type', 'status']
)

strategic_plan_quality_score = Gauge(
    'expertise_center_strategic_plan_quality_score',
    'Quality score of strategic plans (0-1)',
    ['plan_type']
)

strategic_plan_duration_seconds = Histogram(
    'expertise_center_strategic_plan_duration_seconds',
    'Time to generate strategic plan',
    ['plan_type'],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0]
)

# Circuit Breaker Metrics (CRITICAL for resilience)
circuit_breaker_state = Gauge(
    'expertise_center_circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=open, 2=half-open)',
    ['analyzer_name', 'target_service']
)

circuit_breaker_failures_total = Counter(
    'expertise_center_circuit_breaker_failures_total',
    'Total circuit breaker failures',
    ['analyzer_name', 'target_service']
)

circuit_breaker_successes_total = Counter(
    'expertise_center_circuit_breaker_successes_total',
    'Total circuit breaker successes',
    ['analyzer_name', 'target_service']
)

circuit_breaker_timeouts_total = Counter(
    'expertise_center_circuit_breaker_timeouts_total',
    'Total circuit breaker timeouts',
    ['analyzer_name', 'target_service']
)

circuit_breaker_trips_total = Counter(
    'expertise_center_circuit_breaker_trips_total',
    'Total times circuit breaker opened',
    ['analyzer_name', 'target_service']
)

# Cache Metrics
analyzer_cache_hits_total = Counter(
    'expertise_center_analyzer_cache_hits_total',
    'Analyzer result cache hits',
    ['analyzer_name']
)

analyzer_cache_misses_total = Counter(
    'expertise_center_analyzer_cache_misses_total',
    'Analyzer result cache misses',
    ['analyzer_name']
)

analyzer_cache_size = Gauge(
    'expertise_center_analyzer_cache_size',
    'Number of items in analyzer cache',
    ['analyzer_name']
)

# Domain-Specific Metrics
domain_query_duration_seconds = Histogram(
    'expertise_center_domain_query_duration_seconds',
    'Domain query processing time',
    ['domain', 'query_type'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

domain_queries_total = Counter(
    'expertise_center_domain_queries_total',
    'Total domain queries',
    ['domain', 'query_type', 'status']
)

# AI Integration Metrics
ai_foundation_calls_total = Counter(
    'expertise_center_ai_foundation_calls_total',
    'Calls to ai-foundation',
    ['operation', 'status']
)

ai_foundation_call_duration_seconds = Histogram(
    'expertise_center_ai_foundation_call_duration_seconds',
    'ai-foundation call duration',
    ['operation'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

workflow_engine_calls_total = Counter(
    'expertise_center_workflow_engine_calls_total',
    'Calls to workflow engine',
    ['operation', 'status']
)

# System Info
expertise_system_info = Info(
    'expertise_center_system',
    'Expertise center system information'
)

# Health Status
expertise_health_status = Gauge(
    'expertise_center_health_status',
    'Component health status (1=healthy, 0=unhealthy)',
    ['component']
)


# ============================================================================
# DECORATORS FOR AUTOMATIC METRICS
# ============================================================================

def track_analyzer_call(analyzer_name: str, domain: str):
    """Decorator to track analyzer calls"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)

                # Track successful call
                duration = time.time() - start_time
                analyzer_duration_seconds.labels(
                    analyzer_name=analyzer_name,
                    domain=domain
                ).observe(duration)

                analyzer_calls_total.labels(
                    analyzer_name=analyzer_name,
                    domain=domain,
                    status='success'
                ).inc()

                # Track recommendations if available
                if isinstance(result, dict) and 'recommendations' in result:
                    recommendations = result['recommendations']
                    if isinstance(recommendations, list):
                        for rec in recommendations:
                            rec_type = rec.get('type', 'general')
                            analyzer_recommendations_total.labels(
                                analyzer_name=analyzer_name,
                                recommendation_type=rec_type
                            ).inc()

                logger.info(
                    f"Analyzer completed: {analyzer_name} "
                    f"(domain={domain}, duration={duration:.3f}s)"
                )

                return result

            except Exception as e:
                duration = time.time() - start_time
                analyzer_duration_seconds.labels(
                    analyzer_name=analyzer_name,
                    domain=domain
                ).observe(duration)

                error_type = type(e).__name__
                analyzer_calls_total.labels(
                    analyzer_name=analyzer_name,
                    domain=domain,
                    status='error'
                ).inc()

                analyzer_errors_total.labels(
                    analyzer_name=analyzer_name,
                    error_type=error_type
                ).inc()

                logger.error(f"Analyzer failed: {analyzer_name} - {e}")
                raise

        return wrapper
    return decorator


def track_specialist_call(specialist_name: str, operation: str):
    """Decorator to track specialist calls"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)

                # Track successful call
                duration = time.time() - start_time
                specialist_duration_seconds.labels(
                    specialist_name=specialist_name,
                    operation=operation
                ).observe(duration)

                specialist_calls_total.labels(
                    specialist_name=specialist_name,
                    operation=operation,
                    status='success'
                ).inc()

                # Track quality if available
                if isinstance(result, dict) and 'quality_score' in result:
                    specialist_results_quality.labels(
                        specialist_name=specialist_name
                    ).set(result['quality_score'])

                logger.info(
                    f"Specialist completed: {specialist_name}/{operation} "
                    f"(duration={duration:.3f}s)"
                )

                return result

            except Exception as e:
                duration = time.time() - start_time
                specialist_duration_seconds.labels(
                    specialist_name=specialist_name,
                    operation=operation
                ).observe(duration)

                specialist_calls_total.labels(
                    specialist_name=specialist_name,
                    operation=operation,
                    status='error'
                ).inc()

                logger.error(f"Specialist failed: {specialist_name} - {e}")
                raise

        return wrapper
    return decorator


def track_http_call(analyzer_name: str, target_service: str, method: str = 'GET'):
    """Decorator to track HTTP calls from analyzers"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                response = await func(*args, **kwargs)

                # Track successful HTTP call
                duration = time.time() - start_time
                analyzer_http_call_duration_seconds.labels(
                    analyzer_name=analyzer_name,
                    target_service=target_service,
                    method=method
                ).observe(duration)

                status = getattr(response, 'status_code', 200)
                analyzer_http_calls_total.labels(
                    analyzer_name=analyzer_name,
                    target_service=target_service,
                    method=method,
                    status=str(status)
                ).inc()

                # Track circuit breaker success
                circuit_breaker_successes_total.labels(
                    analyzer_name=analyzer_name,
                    target_service=target_service
                ).inc()

                return response

            except Exception as e:
                duration = time.time() - start_time
                analyzer_http_call_duration_seconds.labels(
                    analyzer_name=analyzer_name,
                    target_service=target_service,
                    method=method
                ).observe(duration)

                status = getattr(e, 'status_code', 500)
                analyzer_http_calls_total.labels(
                    analyzer_name=analyzer_name,
                    target_service=target_service,
                    method=method,
                    status=str(status)
                ).inc()

                # Track circuit breaker failure
                circuit_breaker_failures_total.labels(
                    analyzer_name=analyzer_name,
                    target_service=target_service
                ).inc()

                raise

        return wrapper
    return decorator


def track_strategic_plan_generation(plan_type: str):
    """Decorator to track strategic plan generation"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                plan = await func(*args, **kwargs)

                # Track successful generation
                duration = time.time() - start_time
                strategic_plan_duration_seconds.labels(
                    plan_type=plan_type
                ).observe(duration)

                strategic_plan_generations_total.labels(
                    plan_type=plan_type,
                    status='success'
                ).inc()

                # Track quality if available
                if isinstance(plan, dict) and 'quality_score' in plan:
                    strategic_plan_quality_score.labels(
                        plan_type=plan_type
                    ).set(plan['quality_score'])

                return plan

            except Exception as e:
                duration = time.time() - start_time
                strategic_plan_duration_seconds.labels(
                    plan_type=plan_type
                ).observe(duration)

                strategic_plan_generations_total.labels(
                    plan_type=plan_type,
                    status='error'
                ).inc()

                raise

        return wrapper
    return decorator


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def update_circuit_breaker_state(
    analyzer_name: str,
    target_service: str,
    state: str
):
    """
    Update circuit breaker state

    Args:
        analyzer_name: Name of the analyzer
        target_service: Target service name
        state: State (closed, open, half-open)
    """
    state_map = {
        'closed': 0,
        'open': 1,
        'half-open': 2
    }

    circuit_breaker_state.labels(
        analyzer_name=analyzer_name,
        target_service=target_service
    ).set(state_map.get(state, 0))

    # Track trip if opening
    if state == 'open':
        circuit_breaker_trips_total.labels(
            analyzer_name=analyzer_name,
            target_service=target_service
        ).inc()


def track_cache_access(analyzer_name: str, hit: bool):
    """
    Track cache hit/miss

    Args:
        analyzer_name: Name of the analyzer
        hit: Whether it was a cache hit
    """
    if hit:
        analyzer_cache_hits_total.labels(analyzer_name=analyzer_name).inc()
    else:
        analyzer_cache_misses_total.labels(analyzer_name=analyzer_name).inc()


def update_cache_size(analyzer_name: str, size: int):
    """
    Update cache size metric

    Args:
        analyzer_name: Name of the analyzer
        size: Current cache size
    """
    analyzer_cache_size.labels(analyzer_name=analyzer_name).set(size)


def set_analyzer_health(component: str, healthy: bool):
    """
    Set health status for component

    Args:
        component: Component name
        healthy: Health status
    """
    expertise_health_status.labels(component=component).set(1 if healthy else 0)


# ============================================================================
# INITIALIZATION
# ============================================================================

def init_expertise_metrics():
    """Initialize expertise center metrics with system info"""

    expertise_system_info.info({
        'version': '1.0.0',
        'module': 'expertise-center',
        'platform': 'AI-Platform-ISO',
        'analyzers': '10',
        'specialists': '6',
        'domains': 'bcm,hr,finance'
    })

    # Set initial health status for all components
    components = [
        # Analyzers
        'lifecycle_analyzer',
        'impact_analyzer',
        'performance_analyzer',
        'plan_analyzer',
        'scenario_analyzer',
        'emergency_analyzer',
        'risk_analyzer',
        'compliance_analyzer',
        'learning_analyzer',
        'governance_analyzer',
        # Specialists
        'bia_specialist',
        'compliance_specialist',
        'documents_specialist',
        'governance_specialist',
        'learning_specialist',
        'validation_specialist',
        # Strategic
        'strategic_planner'
    ]

    for component in components:
        expertise_health_status.labels(component=component).set(0)

    # Initialize circuit breaker states
    # This will be populated dynamically as analyzers make HTTP calls

    logger.info(" Expertise Center Prometheus metrics initialized")


# Initialize on module import
init_expertise_metrics()
