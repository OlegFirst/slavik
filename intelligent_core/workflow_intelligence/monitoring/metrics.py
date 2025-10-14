"""
Prometheus Metrics for Workflow Intelligence

Tracks:
- Performance (latency, throughput)
- Quality (accuracy, relevance)
- Business (cases collected, learning growth)
- Health (errors, availability)
"""

from prometheus_client import Counter, Histogram, Gauge, Summary
from functools import wraps
import time
from typing import Optional
import asyncio


# ============================================================================
# PERFORMANCE METRICS
# ============================================================================

# Workflow Actions
workflow_actions_total = Counter(
    'workflow_intelligence_actions_total',
    'Total workflow actions executed',
    ['module', 'action', 'status']
)

workflow_action_duration = Histogram(
    'workflow_intelligence_action_duration_seconds',
    'Workflow action execution time',
    ['module', 'action'],
    buckets=[.001, .005, .01, .025, .05, .1, .25, .5, 1.0, 2.5, 5.0, 10.0]
)

# Database Operations
db_query_duration = Histogram(
    'workflow_intelligence_db_query_duration_seconds',
    'Database query execution time',
    ['operation', 'table'],
    buckets=[.001, .005, .01, .025, .05, .1, .25, .5, 1.0]
)

db_queries_total = Counter(
    'workflow_intelligence_db_queries_total',
    'Total database queries',
    ['operation', 'table', 'status']
)

# Cache Performance
cache_hits_total = Counter(
    'workflow_intelligence_cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

cache_misses_total = Counter(
    'workflow_intelligence_cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

# ============================================================================
# QUALITY METRICS
# ============================================================================

# AI Advice Quality
ai_advice_requests_total = Counter(
    'workflow_intelligence_ai_advice_total',
    'Total AI advice requests',
    ['module', 'status']
)

ai_advice_accepted_total = Counter(
    'workflow_intelligence_ai_advice_accepted_total',
    'AI advice accepted by users',
    ['module']
)

ai_advice_relevance = Gauge(
    'workflow_intelligence_ai_advice_relevance',
    'AI advice relevance score (0-1)',
    ['module']
)

# Similar Cases Quality
similar_cases_found = Histogram(
    'workflow_intelligence_similar_cases_found',
    'Number of similar cases found',
    ['module'],
    buckets=[0, 1, 2, 3, 5, 10, 20, 50]
)

similar_cases_relevance = Gauge(
    'workflow_intelligence_similar_cases_relevance',
    'Average relevance score of similar cases',
    ['module']
)

# Benchmark Accuracy
benchmark_calculations_total = Counter(
    'workflow_intelligence_benchmark_calculations_total',
    'Total benchmark calculations',
    ['module', 'industry']
)

benchmark_sample_size = Gauge(
    'workflow_intelligence_benchmark_sample_size',
    'Number of cases used for benchmark',
    ['module', 'industry']
)

# ============================================================================
# BUSINESS METRICS
# ============================================================================

# Case Collection
cases_collected_total = Counter(
    'workflow_intelligence_cases_collected_total',
    'Total cases collected for learning',
    ['module', 'success']
)

case_collection_duration = Histogram(
    'workflow_intelligence_case_collection_duration_seconds',
    'Case collection time',
    ['module'],
    buckets=[.01, .05, .1, .25, .5, 1.0, 2.0]
)

# Learning Growth
total_cases_library = Gauge(
    'workflow_intelligence_total_cases',
    'Total cases in library',
    ['module']
)

learning_coverage = Gauge(
    'workflow_intelligence_learning_coverage',
    'Learning coverage by industry/size',
    ['module', 'industry', 'org_size']
)

# Cross-Service Learning
cross_service_queries_total = Counter(
    'workflow_intelligence_cross_service_queries_total',
    'Queries across different modules',
    ['from_module', 'to_module']
)

# ============================================================================
# HEALTH METRICS
# ============================================================================

# Errors
errors_total = Counter(
    'workflow_intelligence_errors_total',
    'Total errors by type',
    ['error_type', 'module', 'operation']
)

# Database Connection Pool
db_connections_active = Gauge(
    'workflow_intelligence_db_connections_active',
    'Active database connections'
)

db_connections_idle = Gauge(
    'workflow_intelligence_db_connections_idle',
    'Idle database connections'
)

# Storage
storage_size_bytes = Gauge(
    'workflow_intelligence_storage_size_bytes',
    'Storage size in bytes',
    ['table']
)

# Service Health
service_health = Gauge(
    'workflow_intelligence_service_health',
    'Service health status (1=healthy, 0=unhealthy)',
    ['component']
)

# ============================================================================
# ML METRICS
# ============================================================================

# Predictions
ml_predictions_total = Counter(
    'workflow_intelligence_ml_predictions_total',
    'Total ML predictions made',
    ['prediction_type', 'module']
)

ml_prediction_confidence = Histogram(
    'workflow_intelligence_ml_prediction_confidence',
    'ML prediction confidence scores',
    ['prediction_type'],
    buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

ml_prediction_accuracy = Gauge(
    'workflow_intelligence_ml_prediction_accuracy',
    'ML prediction accuracy over time',
    ['prediction_type']
)

# Model Performance
ml_model_training_duration = Histogram(
    'workflow_intelligence_ml_model_training_duration_seconds',
    'ML model training time',
    ['model_type'],
    buckets=[1, 5, 10, 30, 60, 300, 600, 1800]
)


# ============================================================================
# WORKFLOW METRICS CLASS
# ============================================================================

class WorkflowMetrics:
    """Centralized metrics tracking for Workflow Intelligence"""

    @staticmethod
    def track_action(module: str, action: str, duration: float, success: bool):
        """Track workflow action execution"""
        status = "success" if success else "error"
        workflow_actions_total.labels(module=module, action=action, status=status).inc()
        workflow_action_duration.labels(module=module, action=action).observe(duration)

    @staticmethod
    def track_db_query(operation: str, table: str, duration: float, success: bool):
        """Track database query"""
        status = "success" if success else "error"
        db_queries_total.labels(operation=operation, table=table, status=status).inc()
        db_query_duration.labels(operation=operation, table=table).observe(duration)

    @staticmethod
    def track_cache(cache_type: str, hit: bool):
        """Track cache hit/miss"""
        if hit:
            cache_hits_total.labels(cache_type=cache_type).inc()
        else:
            cache_misses_total.labels(cache_type=cache_type).inc()

    @staticmethod
    def track_ai_advice(module: str, success: bool, accepted: bool = False):
        """Track AI advice request and acceptance"""
        status = "success" if success else "error"
        ai_advice_requests_total.labels(module=module, status=status).inc()
        if accepted:
            ai_advice_accepted_total.labels(module=module).inc()

    @staticmethod
    def track_case_collection(module: str, success: bool, duration: float):
        """Track case collection"""
        status = "success" if success else "failed"
        cases_collected_total.labels(module=module, success=status).inc()
        case_collection_duration.labels(module=module).observe(duration)

    @staticmethod
    def track_benchmark(module: str, industry: str, sample_size: int):
        """Track benchmark calculation"""
        benchmark_calculations_total.labels(module=module, industry=industry).inc()
        benchmark_sample_size.labels(module=module, industry=industry).set(sample_size)

    @staticmethod
    def track_error(error_type: str, module: str, operation: str):
        """Track error"""
        errors_total.labels(error_type=error_type, module=module, operation=operation).inc()

    @staticmethod
    def update_library_size(module: str, total: int):
        """Update total cases in library"""
        total_cases_library.labels(module=module).set(total)

    @staticmethod
    def update_db_pool(active: int, idle: int):
        """Update database connection pool metrics"""
        db_connections_active.set(active)
        db_connections_idle.set(idle)

    @staticmethod
    def set_health(component: str, healthy: bool):
        """Set component health status"""
        service_health.labels(component=component).set(1 if healthy else 0)


# Global instance
workflow_metrics = WorkflowMetrics()


# ============================================================================
# DECORATORS
# ============================================================================

def track_workflow_action(module: str, action: str):
    """Decorator to track workflow action execution"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            success = False
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                workflow_metrics.track_error(
                    error_type=type(e).__name__,
                    module=module,
                    operation=action
                )
                raise
            finally:
                duration = time.time() - start
                workflow_metrics.track_action(module, action, duration, success)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            success = False
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                workflow_metrics.track_error(
                    error_type=type(e).__name__,
                    module=module,
                    operation=action
                )
                raise
            finally:
                duration = time.time() - start
                workflow_metrics.track_action(module, action, duration, success)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def track_case_collection(module: str):
    """Decorator to track case collection"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            success = False
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            finally:
                duration = time.time() - start
                workflow_metrics.track_case_collection(module, success, duration)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            # Sync version
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start = time.time()
                success = False
                try:
                    result = func(*args, **kwargs)
                    success = True
                    return result
                finally:
                    duration = time.time() - start
                    workflow_metrics.track_case_collection(module, success, duration)
            return sync_wrapper

    return decorator


def track_benchmark_calculation(module: str, industry: str):
    """Decorator to track benchmark calculation"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            # Track sample size if available in result
            if result and hasattr(result, 'total_cases'):
                workflow_metrics.track_benchmark(module, industry, result.total_cases)
            return result
        return wrapper
    return decorator


def track_ai_advice(module: str):
    """Decorator to track AI advice requests"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            success = False
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            finally:
                workflow_metrics.track_ai_advice(module, success)
        return wrapper
    return decorator
