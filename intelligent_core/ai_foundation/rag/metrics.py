"""
 Prometheus Metrics for RAG Pipeline

Tracks:
- RAG search operations (latency, results count, relevance)
- Embedding generation (latency, model usage)
- Qdrant operations (query latency, collection sizes)
- Reranking operations (latency, score distribution)
- Cache hits/misses
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

# RAG Search Metrics
rag_search_duration_seconds = Histogram(
    'ai_foundation_rag_search_duration_seconds',
    'Time spent on RAG search operations',
    ['collection', 'query_type'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

rag_search_results_count = Histogram(
    'ai_foundation_rag_search_results_count',
    'Number of results returned from RAG search',
    ['collection'],
    buckets=[0, 1, 5, 10, 20, 50, 100]
)

rag_search_relevance_score = Histogram(
    'ai_foundation_rag_search_relevance_score',
    'Relevance score distribution for RAG searches',
    ['collection'],
    buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

rag_searches_total = Counter(
    'ai_foundation_rag_searches_total',
    'Total number of RAG searches',
    ['collection', 'status']
)

# Embedding Generation Metrics
embedding_generation_duration_seconds = Histogram(
    'ai_foundation_embedding_generation_duration_seconds',
    'Time spent generating embeddings',
    ['model'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

embedding_generations_total = Counter(
    'ai_foundation_embedding_generations_total',
    'Total number of embeddings generated',
    ['model', 'status']
)

embedding_vector_dimension = Gauge(
    'ai_foundation_embedding_vector_dimension',
    'Dimension of embedding vectors',
    ['model']
)

embedding_cache_hits_total = Counter(
    'ai_foundation_embedding_cache_hits_total',
    'Number of embedding cache hits',
    ['model']
)

embedding_cache_misses_total = Counter(
    'ai_foundation_embedding_cache_misses_total',
    'Number of embedding cache misses',
    ['model']
)

# Qdrant Operations Metrics
qdrant_query_duration_seconds = Histogram(
    'ai_foundation_qdrant_query_duration_seconds',
    'Time spent on Qdrant queries',
    ['operation', 'collection'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

qdrant_operations_total = Counter(
    'ai_foundation_qdrant_operations_total',
    'Total number of Qdrant operations',
    ['operation', 'collection', 'status']
)

qdrant_collection_size = Gauge(
    'ai_foundation_qdrant_collection_size',
    'Number of vectors in Qdrant collection',
    ['collection']
)

qdrant_collection_disk_usage_bytes = Gauge(
    'ai_foundation_qdrant_collection_disk_usage_bytes',
    'Disk usage of Qdrant collection in bytes',
    ['collection']
)

# Reranking Metrics
reranking_duration_seconds = Histogram(
    'ai_foundation_reranking_duration_seconds',
    'Time spent reranking results',
    ['reranker_type'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0]
)

reranking_operations_total = Counter(
    'ai_foundation_reranking_operations_total',
    'Total number of reranking operations',
    ['reranker_type', 'status']
)

reranking_score_improvement = Histogram(
    'ai_foundation_reranking_score_improvement',
    'Score improvement after reranking',
    ['reranker_type'],
    buckets=[-0.5, -0.3, -0.1, 0.0, 0.1, 0.3, 0.5, 1.0]
)

# Retrieval Metrics
retrieval_context_size_tokens = Histogram(
    'ai_foundation_retrieval_context_size_tokens',
    'Size of retrieved context in tokens',
    ['collection'],
    buckets=[0, 100, 500, 1000, 2000, 4000, 8000]
)

retrieval_sources_count = Histogram(
    'ai_foundation_retrieval_sources_count',
    'Number of sources in retrieved context',
    ['collection'],
    buckets=[0, 1, 2, 5, 10, 20, 50]
)

# System Info
rag_system_info = Info(
    'ai_foundation_rag_system',
    'RAG system information'
)

# Health Status
rag_health_status = Gauge(
    'ai_foundation_rag_health_status',
    'RAG component health status (1=healthy, 0=unhealthy)',
    ['component']
)


# ============================================================================
# DECORATORS FOR AUTOMATIC METRICS
# ============================================================================

def track_rag_search(collection: str, query_type: str = 'hybrid'):
    """Decorator to track RAG search operations"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                results = await func(*args, **kwargs)

                # Track successful search
                duration = time.time() - start_time
                rag_search_duration_seconds.labels(
                    collection=collection,
                    query_type=query_type
                ).observe(duration)

                rag_searches_total.labels(
                    collection=collection,
                    status='success'
                ).inc()

                # Track results count
                result_count = len(results) if isinstance(results, list) else 0
                rag_search_results_count.labels(
                    collection=collection
                ).observe(result_count)

                # Track average relevance score
                if results and isinstance(results, list) and hasattr(results[0], 'score'):
                    avg_score = sum(r.score for r in results) / len(results)
                    rag_search_relevance_score.labels(
                        collection=collection
                    ).observe(avg_score)

                logger.info(
                    f"RAG search completed: {result_count} results "
                    f"(collection={collection}, duration={duration:.3f}s)"
                )

                return results

            except Exception as e:
                duration = time.time() - start_time
                rag_search_duration_seconds.labels(
                    collection=collection,
                    query_type=query_type
                ).observe(duration)

                rag_searches_total.labels(
                    collection=collection,
                    status='error'
                ).inc()

                logger.error(f"RAG search failed: {e}")
                raise

        return wrapper
    return decorator


def track_embedding_generation(model: str):
    """Decorator to track embedding generation"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                # Check cache first
                cache_hit = kwargs.get('_cache_hit', False)

                embeddings = await func(*args, **kwargs)

                # Track successful generation
                duration = time.time() - start_time
                embedding_generation_duration_seconds.labels(
                    model=model
                ).observe(duration)

                embedding_generations_total.labels(
                    model=model,
                    status='success'
                ).inc()

                # Track cache hits/misses
                if cache_hit:
                    embedding_cache_hits_total.labels(model=model).inc()
                else:
                    embedding_cache_misses_total.labels(model=model).inc()

                # Track vector dimension
                if embeddings and len(embeddings) > 0:
                    if isinstance(embeddings, list):
                        dimension = len(embeddings[0]) if isinstance(embeddings[0], (list, tuple)) else len(embeddings)
                    else:
                        dimension = len(embeddings)
                    embedding_vector_dimension.labels(model=model).set(dimension)

                return embeddings

            except Exception as e:
                duration = time.time() - start_time
                embedding_generation_duration_seconds.labels(
                    model=model
                ).observe(duration)

                embedding_generations_total.labels(
                    model=model,
                    status='error'
                ).inc()

                raise

        return wrapper
    return decorator


def track_qdrant_operation(operation: str, collection: str):
    """Decorator to track Qdrant operations"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)

                # Track successful operation
                duration = time.time() - start_time
                qdrant_query_duration_seconds.labels(
                    operation=operation,
                    collection=collection
                ).observe(duration)

                qdrant_operations_total.labels(
                    operation=operation,
                    collection=collection,
                    status='success'
                ).inc()

                return result

            except Exception as e:
                duration = time.time() - start_time
                qdrant_query_duration_seconds.labels(
                    operation=operation,
                    collection=collection
                ).observe(duration)

                qdrant_operations_total.labels(
                    operation=operation,
                    collection=collection,
                    status='error'
                ).inc()

                raise

        return wrapper
    return decorator


def track_reranking(reranker_type: str = 'cohere'):
    """Decorator to track reranking operations"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(results, *args, **kwargs):
            start_time = time.time()

            try:
                # Get original scores
                original_scores = [r.score for r in results] if results else []
                original_avg = sum(original_scores) / len(original_scores) if original_scores else 0

                reranked_results = await func(results, *args, **kwargs)

                # Track successful reranking
                duration = time.time() - start_time
                reranking_duration_seconds.labels(
                    reranker_type=reranker_type
                ).observe(duration)

                reranking_operations_total.labels(
                    reranker_type=reranker_type,
                    status='success'
                ).inc()

                # Track score improvement
                if reranked_results:
                    reranked_scores = [r.score for r in reranked_results]
                    reranked_avg = sum(reranked_scores) / len(reranked_scores)
                    improvement = reranked_avg - original_avg

                    reranking_score_improvement.labels(
                        reranker_type=reranker_type
                    ).observe(improvement)

                return reranked_results

            except Exception as e:
                duration = time.time() - start_time
                reranking_duration_seconds.labels(
                    reranker_type=reranker_type
                ).observe(duration)

                reranking_operations_total.labels(
                    reranker_type=reranker_type,
                    status='error'
                ).inc()

                raise

        return wrapper
    return decorator


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def update_collection_metrics(qdrant_client, collection_name: str):
    """
    Update collection size and disk usage metrics

    Args:
        qdrant_client: Qdrant client instance
        collection_name: Name of the collection
    """
    try:
        collection_info = await qdrant_client.get_collection(collection_name)

        # Update collection size
        if hasattr(collection_info, 'vectors_count'):
            qdrant_collection_size.labels(
                collection=collection_name
            ).set(collection_info.vectors_count)

        # Update disk usage if available
        if hasattr(collection_info, 'disk_usage'):
            qdrant_collection_disk_usage_bytes.labels(
                collection=collection_name
            ).set(collection_info.disk_usage)

    except Exception as e:
        logger.error(f"Failed to update collection metrics: {e}")


def set_rag_health(component: str, healthy: bool):
    """
    Set health status for RAG component

    Args:
        component: Component name (embeddings, qdrant, reranking, pipeline)
        healthy: Health status
    """
    rag_health_status.labels(component=component).set(1 if healthy else 0)


# ============================================================================
# INITIALIZATION
# ============================================================================

def init_rag_metrics():
    """Initialize RAG metrics with system info"""

    rag_system_info.info({
        'version': '1.0.0',
        'module': 'rag',
        'platform': 'AI-Platform-ISO',
        'embedding_models': 'voyage-2,openai-text-embedding-3-small',
        'vector_db': 'qdrant',
        'reranker': 'cohere'
    })

    # Set initial health status
    for component in ['embeddings', 'qdrant', 'reranking', 'pipeline']:
        rag_health_status.labels(component=component).set(0)

    logger.info(" RAG Prometheus metrics initialized")


# Initialize on module import
init_rag_metrics()
