"""
Prometheus Metrics for PDCA Rules Engine

Tracks all PDCA cycle operations and performance
"""

from prometheus_client import Counter, Histogram, Gauge, Info
import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# PDCA CYCLE METRICS
# =============================================================================

# Counter: Total PDCA cycles by phase and module
pdca_cycles_total = Counter(
    'pdca_cycles_total',
    'Total PDCA cycles executed',
    ['phase', 'module', 'tenant_id']
)

# Histogram: PDCA phase duration
pdca_phase_duration_seconds = Histogram(
    'pdca_phase_duration_seconds',
    'Duration of PDCA phases in seconds',
    ['phase', 'module'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
)

# Gauge: Quality scores
pdca_quality_score = Gauge(
    'pdca_quality_score',
    'PDCA cycle quality scores',
    ['module', 'tenant_id']
)

# Counter: Lessons learned
pdca_lessons_learned_total = Counter(
    'pdca_lessons_learned_total',
    'Total lessons learned from PDCA cycles',
    ['module', 'tenant_id']
)

# Counter: Patterns detected
pdca_patterns_detected_total = Counter(
    'pdca_patterns_detected_total',
    'Total patterns detected from PDCA cycles',
    ['module', 'tenant_id']
)

# Counter: Deviations found
pdca_deviations_total = Counter(
    'pdca_deviations_total',
    'Total deviations found in CHECK phase',
    ['module', 'tenant_id']
)

# Gauge: Similar cases used for planning
pdca_similar_cases_gauge = Gauge(
    'pdca_similar_cases_used',
    'Number of similar cases used for planning',
    ['module']
)

# Histogram: Workflow duration vs benchmark deviation
pdca_duration_deviation = Histogram(
    'pdca_duration_deviation_percent',
    'Percentage deviation from benchmark duration',
    ['module'],
    buckets=[-50, -25, -10, 0, 10, 25, 50, 100, 200]
)

# Info: PDCA system status
pdca_system_info = Info(
    'pdca_system',
    'PDCA Rules Engine system information'
)


# =============================================================================
# DECORATORS FOR AUTOMATIC METRIC TRACKING
# =============================================================================

def track_pdca_phase(phase: str):
    """
    Decorator to track PDCA phase execution

    Usage:
        @track_pdca_phase("plan")
        async def plan_workflow(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract module from kwargs or args
            module = kwargs.get('module', 'unknown')
            tenant_id = 'default'

            # Get self if it's a method
            if args and hasattr(args[0], 'tenant_id'):
                tenant_id = args[0].tenant_id

            # Track start time
            start_time = time.time()

            try:
                # Execute function
                result = await func(*args, **kwargs)

                # Track success
                pdca_cycles_total.labels(
                    phase=phase,
                    module=module,
                    tenant_id=tenant_id
                ).inc()

                # Track duration
                duration = time.time() - start_time
                pdca_phase_duration_seconds.labels(
                    phase=phase,
                    module=module
                ).observe(duration)

                logger.debug(
                    f"PDCA {phase} phase completed: module={module}, "
                    f"duration={duration:.2f}s"
                )

                return result

            except Exception as e:
                logger.error(
                    f"PDCA {phase} phase failed: module={module}, error={e}"
                )
                raise

        return wrapper
    return decorator


def track_pdca_metrics(pdca_data: dict, module: str, tenant_id: str):
    """
    Track comprehensive PDCA metrics from cycle data

    Args:
        pdca_data: Complete PDCA cycle data
        module: Module name (bia, risk, etc.)
        tenant_id: Tenant ID
    """

    # Quality score
    quality_score = pdca_data.get('quality_score', 0)
    if quality_score:
        pdca_quality_score.labels(
            module=module,
            tenant_id=tenant_id
        ).set(quality_score)

    # Lessons learned
    lessons = pdca_data.get('lessons_learned', [])
    if lessons:
        pdca_lessons_learned_total.labels(
            module=module,
            tenant_id=tenant_id
        ).inc(len(lessons))

    # Patterns detected
    patterns = pdca_data.get('patterns_detected', [])
    if patterns:
        pdca_patterns_detected_total.labels(
            module=module,
            tenant_id=tenant_id
        ).inc(len(patterns))

    # Deviations
    deviations = pdca_data.get('deviations', [])
    if deviations:
        pdca_deviations_total.labels(
            module=module,
            tenant_id=tenant_id
        ).inc(len(deviations))

    # Similar cases used
    similar_cases_count = pdca_data.get('similar_cases_count', 0)
    if similar_cases_count:
        pdca_similar_cases_gauge.labels(module=module).set(similar_cases_count)

    # Duration deviation
    benchmarks = pdca_data.get('benchmarks', {})
    do_duration = pdca_data.get('do_duration', 0)

    if benchmarks and do_duration:
        median_duration = benchmarks.get('median_duration', 0)
        if median_duration > 0:
            deviation_percent = ((do_duration - median_duration) / median_duration) * 100
            pdca_duration_deviation.labels(module=module).observe(deviation_percent)

    logger.debug(
        f"PDCA metrics tracked: module={module}, "
        f"quality={quality_score}, lessons={len(lessons)}, "
        f"patterns={len(patterns)}, deviations={len(deviations)}"
    )


# =============================================================================
# SYSTEM INITIALIZATION
# =============================================================================

def initialize_pdca_metrics(tenant_id: str, version: str):
    """
    Initialize PDCA system metrics

    Args:
        tenant_id: Tenant ID
        version: PDCA version
    """
    pdca_system_info.info({
        'tenant_id': tenant_id,
        'version': version,
        'engine': 'PDCARulesEngine'
    })

    logger.info(f" PDCA metrics initialized (tenant={tenant_id}, version={version})")
