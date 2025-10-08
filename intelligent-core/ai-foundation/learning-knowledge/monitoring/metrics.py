"""
📊 Prometheus Metrics for Knowledge System

Tracks:
- Standards loads (count, latency, cache hits)
- Case collections (count, module distribution)
- Vector search operations (count, latency)
- API requests (count, latency, errors)
- Update checks (count, updates found)
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

# Standards Loader Metrics
standards_loads_total = Counter(
    'knowledge_standards_loads_total',
    'Total number of standard loads',
    ['standard', 'domain', 'cache_hit']
)

standards_load_duration = Histogram(
    'knowledge_standards_load_duration_seconds',
    'Time spent loading standards',
    ['standard', 'domain']
)

standards_cache_hits = Counter(
    'knowledge_standards_cache_hits_total',
    'Number of cache hits for standards',
    ['standard']
)

standards_cache_misses = Counter(
    'knowledge_standards_cache_misses_total',
    'Number of cache misses for standards',
    ['standard']
)

# Case Collector Metrics
cases_collected_total = Counter(
    'knowledge_cases_collected_total',
    'Total number of cases collected',
    ['module', 'outcome']
)

cases_collection_duration = Histogram(
    'knowledge_cases_collection_duration_seconds',
    'Time spent collecting cases',
    ['module']
)

cases_total = Gauge(
    'knowledge_cases_total',
    'Total number of cases in library',
    ['module']
)

# Vector Search Metrics
vector_searches_total = Counter(
    'knowledge_vector_searches_total',
    'Total number of vector searches',
    ['collection', 'status']
)

vector_search_duration = Histogram(
    'knowledge_vector_search_duration_seconds',
    'Time spent on vector searches',
    ['collection']
)

vector_index_operations_total = Counter(
    'knowledge_vector_index_operations_total',
    'Total number of vector indexing operations',
    ['collection', 'operation']
)

# API Metrics
api_requests_total = Counter(
    'knowledge_api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status']
)

api_request_duration = Histogram(
    'knowledge_api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

api_errors_total = Counter(
    'knowledge_api_errors_total',
    'Total number of API errors',
    ['method', 'endpoint', 'error_type']
)

# Update Monitor Metrics
update_checks_total = Counter(
    'knowledge_update_checks_total',
    'Total number of update checks',
    ['source', 'status']
)

updates_found_total = Counter(
    'knowledge_updates_found_total',
    'Total number of updates found',
    ['source']
)

update_check_duration = Histogram(
    'knowledge_update_check_duration_seconds',
    'Time spent checking for updates',
    ['source']
)

# System Info
system_info = Info(
    'knowledge_system',
    'Knowledge system information'
)

# Health Status
health_status = Gauge(
    'knowledge_health_status',
    'Health status (1=healthy, 0=unhealthy)',
    ['component']
)


# ============================================================================
# DECORATORS FOR AUTOMATIC METRICS
# ============================================================================

def track_standard_load(domain: str):
    """Decorator to track standard load operations"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(self, standard: str, *args, **kwargs):
            start_time = time.time()

            try:
                result = await func(self, standard, *args, **kwargs)

                # Track successful load
                duration = time.time() - start_time
                standards_load_duration.labels(
                    standard=standard,
                    domain=domain
                ).observe(duration)

                # Check if it was a cache hit
                cache_hit = kwargs.get('_cache_hit', False)
                standards_loads_total.labels(
                    standard=standard,
                    domain=domain,
                    cache_hit=str(cache_hit)
                ).inc()

                if cache_hit:
                    standards_cache_hits.labels(standard=standard).inc()
                else:
                    standards_cache_misses.labels(standard=standard).inc()

                return result

            except Exception as e:
                # Track failed load
                duration = time.time() - start_time
                standards_load_duration.labels(
                    standard=standard,
                    domain=domain
                ).observe(duration)

                standards_loads_total.labels(
                    standard=standard,
                    domain=domain,
                    cache_hit='false'
                ).inc()

                raise

        return wrapper
    return decorator


def track_case_collection(func: Callable):
    """Decorator to track case collection operations"""
    @wraps(func)
    async def wrapper(self, workflow_id: str, module: str, outcome: str, *args, **kwargs):
        start_time = time.time()

        try:
            result = await func(self, workflow_id, module, outcome, *args, **kwargs)

            # Track successful collection
            duration = time.time() - start_time
            cases_collection_duration.labels(module=module).observe(duration)
            cases_collected_total.labels(module=module, outcome=outcome).inc()

            logger.info(
                f"Case collected: {result['case_id']} "
                f"(module={module}, duration={duration:.2f}s)"
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            cases_collection_duration.labels(module=module).observe(duration)
            logger.error(f"Case collection failed: {e}")
            raise

    return wrapper


def track_vector_search(collection: str):
    """Decorator to track vector search operations"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(self, query: str, *args, **kwargs):
            start_time = time.time()

            try:
                results = await func(self, query, *args, **kwargs)

                # Track successful search
                duration = time.time() - start_time
                vector_search_duration.labels(collection=collection).observe(duration)
                vector_searches_total.labels(
                    collection=collection,
                    status='success'
                ).inc()

                logger.info(
                    f"Vector search: {len(results)} results "
                    f"(collection={collection}, duration={duration:.2f}s)"
                )

                return results

            except Exception as e:
                duration = time.time() - start_time
                vector_search_duration.labels(collection=collection).observe(duration)
                vector_searches_total.labels(
                    collection=collection,
                    status='error'
                ).inc()

                raise

        return wrapper
    return decorator


def track_api_request(method: str, endpoint: str):
    """Decorator to track API requests"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)

                # Track successful request
                duration = time.time() - start_time
                api_request_duration.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)

                api_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status='200'
                ).inc()

                return result

            except Exception as e:
                duration = time.time() - start_time
                api_request_duration.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)

                # Determine error type
                error_type = type(e).__name__

                # Determine status code
                status = getattr(e, 'status_code', '500')

                api_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status=str(status)
                ).inc()

                api_errors_total.labels(
                    method=method,
                    endpoint=endpoint,
                    error_type=error_type
                ).inc()

                raise

        return wrapper
    return decorator


def track_update_check(source: str):
    """Decorator to track update checks"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            start_time = time.time()

            try:
                updates = await func(self, *args, **kwargs)

                # Track successful check
                duration = time.time() - start_time
                update_check_duration.labels(source=source).observe(duration)
                update_checks_total.labels(source=source, status='success').inc()

                # Track updates found
                if updates:
                    updates_found_total.labels(source=source).inc(len(updates))
                    logger.info(f"Update check: {len(updates)} updates found from {source}")

                return updates

            except Exception as e:
                duration = time.time() - start_time
                update_check_duration.labels(source=source).observe(duration)
                update_checks_total.labels(source=source, status='error').inc()

                raise

        return wrapper
    return decorator


# ============================================================================
# LEARNING SYSTEM METRICS
# ============================================================================

# Learning Engine Operations
learning_operations_total = Counter(
    'learning_operations_total',
    'Total learning system operations',
    ['engine', 'operation', 'status']
)

learning_operation_duration = Histogram(
    'learning_operation_duration_seconds',
    'Learning operation execution time',
    ['engine', 'operation'],
    buckets=[.01, .05, .1, .25, .5, 1.0, 2.5, 5.0, 10.0]
)

# Competency Tracking
competency_assessments_total = Counter(
    'learning_competency_assessments_total',
    'Total competency assessments',
    ['status']
)

competency_score_distribution = Histogram(
    'learning_competency_score',
    'Competency score distribution',
    buckets=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
)

# Gamification
gamification_events_total = Counter(
    'learning_gamification_events_total',
    'Total gamification events',
    ['event_type']
)

badges_awarded_total = Counter(
    'learning_badges_awarded_total',
    'Total badges awarded',
    ['badge_category']
)

# Pattern Detection
patterns_detected_total = Counter(
    'learning_patterns_detected_total',
    'Total patterns detected',
    ['pattern_type', 'severity']
)

# Process Gap Analysis
gap_analyses_total = Counter(
    'learning_gap_analyses_total',
    'Total gap analyses performed',
    ['scenario_type']
)

critical_gaps_found = Gauge(
    'learning_critical_gaps_current',
    'Current number of critical gaps',
    ['scenario_type']
)


def track_learning_operation(engine: str, operation: str):
    """Decorator to track learning system operations"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False

            try:
                result = func(*args, **kwargs)
                success = True
                return result

            except Exception as e:
                logger.error(f"{engine}.{operation} failed: {e}")
                raise

            finally:
                duration = time.time() - start_time
                status = 'success' if success else 'error'

                learning_operations_total.labels(
                    engine=engine,
                    operation=operation,
                    status=status
                ).inc()

                learning_operation_duration.labels(
                    engine=engine,
                    operation=operation
                ).observe(duration)

        return wrapper
    return decorator


def track_competency_assessment(func: Callable):
    """Decorator to track competency assessments"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)

            competency_assessments_total.labels(status='success').inc()

            # Track score if available
            if isinstance(result, dict):
                avg_score = result.get('avg_exercise_score', 0)
                if avg_score > 0:
                    competency_score_distribution.observe(avg_score)

            return result

        except Exception as e:
            competency_assessments_total.labels(status='error').inc()
            raise

    return wrapper


def track_gamification_event(event_type: str):
    """Decorator to track gamification events"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            gamification_events_total.labels(event_type=event_type).inc()

            # Track badge awards specifically
            if event_type == 'badge_award' and isinstance(result, dict):
                badge_category = result.get('category', 'unknown')
                badges_awarded_total.labels(badge_category=badge_category).inc()

            return result

        return wrapper
    return decorator


def track_pattern_detection(func: Callable):
    """Decorator to track pattern detection"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        # Track detected patterns
        if isinstance(result, list):
            for pattern in result:
                if isinstance(pattern, dict):
                    pattern_type = pattern.get('pattern_type', 'unknown')
                    severity = pattern.get('severity', 'unknown')
                    patterns_detected_total.labels(
                        pattern_type=pattern_type,
                        severity=severity
                    ).inc()

        return result

    return wrapper


def track_gap_analysis(func: Callable):
    """Decorator to track gap analysis operations"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        # Track analysis
        if isinstance(result, dict):
            scenario_type = result.get('scenario_type', 'unknown')
            gap_analyses_total.labels(scenario_type=scenario_type).inc()

            # Track critical gaps
            critical_gaps = result.get('critical_gaps', [])
            if isinstance(critical_gaps, list):
                critical_gaps_found.labels(scenario_type=scenario_type).set(len(critical_gaps))

        return result

    return wrapper


# ============================================================================
# HEALTH CHECK
# ============================================================================

class HealthChecker:
    """Health status checker for knowledge system components"""

    def __init__(self):
        self.components = [
            'standards_loader',
            'case_collector',
            'vector_indexer',
            'api',
            'updater'
        ]

    async def check_health(self) -> dict:
        """
        Check health of all components

        Returns:
            Health status dict
        """
        status = {
            'overall': 'healthy',
            'components': {},
            'checked_at': time.time()
        }

        # Check each component
        for component in self.components:
            try:
                component_status = await self._check_component(component)
                status['components'][component] = component_status

                # Update health gauge
                health_status.labels(component=component).set(
                    1 if component_status == 'healthy' else 0
                )

            except Exception as e:
                status['components'][component] = f'error: {e}'
                health_status.labels(component=component).set(0)
                status['overall'] = 'degraded'

        # Overall health
        if all(s == 'healthy' for s in status['components'].values()):
            status['overall'] = 'healthy'
        elif any('error' in str(s) for s in status['components'].values()):
            status['overall'] = 'unhealthy'
        else:
            status['overall'] = 'degraded'

        return status

    async def _check_component(self, component: str) -> str:
        """Check individual component health"""

        if component == 'standards_loader':
            # Check if data path exists
            from pathlib import Path
            data_path = Path(__file__).parents[3] / "data" / "knowledge" / "standards"
            return 'healthy' if data_path.exists() else 'unavailable'

        elif component == 'case_collector':
            # Check if cases path exists
            from pathlib import Path
            cases_path = Path(__file__).parents[3] / "data" / "cases"
            return 'healthy' if cases_path.exists() else 'unavailable'

        elif component == 'vector_indexer':
            # Try to import Qdrant client
            try:
                from qdrant_client import QdrantClient
                return 'healthy'
            except ImportError:
                return 'unavailable'

        elif component == 'api':
            # API is healthy if this code is running
            return 'healthy'

        elif component == 'updater':
            # Check if updater config exists
            from pathlib import Path
            config_path = Path(__file__).parents[1] / "config" / "sources.yaml"
            return 'healthy' if config_path.exists() else 'unavailable'

        return 'unknown'


# ============================================================================
# INITIALIZATION
# ============================================================================

def init_metrics():
    """Initialize metrics with system info"""

    system_info.info({
        'version': '1.0.0',
        'module': 'knowledge-system',
        'platform': 'AI-Platform-ISO'
    })

    # Set initial health status
    for component in ['standards_loader', 'case_collector', 'vector_indexer', 'api', 'updater']:
        health_status.labels(component=component).set(0)

    logger.info("✅ Prometheus metrics initialized")


# Initialize on module import
init_metrics()
