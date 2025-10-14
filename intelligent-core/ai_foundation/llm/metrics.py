"""
📊 Prometheus Metrics for LLM Router

Tracks:
- LLM requests (count, latency, status)
- Token usage (prompt, completion, total)
- Cost tracking (USD per provider/model)
- Routing decisions (provider selection, reasoning)
- Model performance (latency by model, error rates)
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

# LLM Request Metrics
llm_requests_total = Counter(
    'ai_foundation_llm_requests_total',
    'Total number of LLM requests',
    ['provider', 'model', 'status']
)

llm_request_duration_seconds = Histogram(
    'ai_foundation_llm_request_duration_seconds',
    'LLM request duration in seconds',
    ['provider', 'model'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

llm_errors_total = Counter(
    'ai_foundation_llm_errors_total',
    'Total number of LLM errors',
    ['provider', 'model', 'error_type']
)

# Token Usage Metrics
llm_tokens_used_total = Counter(
    'ai_foundation_llm_tokens_used_total',
    'Total tokens used',
    ['provider', 'model', 'type']  # type: prompt/completion/total
)

llm_tokens_per_request = Histogram(
    'ai_foundation_llm_tokens_per_request',
    'Tokens used per request',
    ['provider', 'model', 'type'],
    buckets=[0, 100, 500, 1000, 2000, 4000, 8000, 16000]
)

llm_context_length = Histogram(
    'ai_foundation_llm_context_length',
    'Context length sent to LLM',
    ['provider', 'model'],
    buckets=[0, 500, 1000, 2000, 4000, 8000, 16000, 32000]
)

# Cost Metrics
llm_cost_usd_total = Counter(
    'ai_foundation_llm_cost_usd_total',
    'Total cost in USD',
    ['provider', 'model']
)

llm_cost_per_request_usd = Histogram(
    'ai_foundation_llm_cost_per_request_usd',
    'Cost per request in USD',
    ['provider', 'model'],
    buckets=[0.0001, 0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

# Routing Metrics
llm_routing_decisions_total = Counter(
    'ai_foundation_llm_routing_decisions_total',
    'Total routing decisions made',
    ['selected_provider', 'reason']
)

llm_provider_availability = Gauge(
    'ai_foundation_llm_provider_availability',
    'Provider availability (1=available, 0=unavailable)',
    ['provider']
)

llm_routing_latency_seconds = Histogram(
    'ai_foundation_llm_routing_latency_seconds',
    'Time spent on routing decision',
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1]
)

# Model Performance Metrics
llm_model_latency_p50 = Gauge(
    'ai_foundation_llm_model_latency_p50_seconds',
    'P50 latency by model',
    ['provider', 'model']
)

llm_model_latency_p95 = Gauge(
    'ai_foundation_llm_model_latency_p95_seconds',
    'P95 latency by model',
    ['provider', 'model']
)

llm_model_error_rate = Gauge(
    'ai_foundation_llm_model_error_rate',
    'Error rate by model (0-1)',
    ['provider', 'model']
)

# Streaming Metrics
llm_streaming_chunks_total = Counter(
    'ai_foundation_llm_streaming_chunks_total',
    'Total streaming chunks received',
    ['provider', 'model']
)

llm_streaming_time_to_first_token_seconds = Histogram(
    'ai_foundation_llm_streaming_time_to_first_token_seconds',
    'Time to first token in streaming',
    ['provider', 'model'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Cache Metrics
llm_cache_hits_total = Counter(
    'ai_foundation_llm_cache_hits_total',
    'Number of LLM cache hits',
    ['provider', 'model']
)

llm_cache_misses_total = Counter(
    'ai_foundation_llm_cache_misses_total',
    'Number of LLM cache misses',
    ['provider', 'model']
)

# System Info
llm_system_info = Info(
    'ai_foundation_llm_system',
    'LLM system information'
)

# Health Status
llm_health_status = Gauge(
    'ai_foundation_llm_health_status',
    'LLM component health status (1=healthy, 0=unhealthy)',
    ['provider']
)


# ============================================================================
# DECORATORS FOR AUTOMATIC METRICS
# ============================================================================

def track_llm_request(provider: str, model: str):
    """Decorator to track LLM requests"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                response = await func(*args, **kwargs)

                # Track successful request
                duration = time.time() - start_time
                llm_request_duration_seconds.labels(
                    provider=provider,
                    model=model
                ).observe(duration)

                llm_requests_total.labels(
                    provider=provider,
                    model=model,
                    status='success'
                ).inc()

                # Track token usage if available
                if hasattr(response, 'usage'):
                    usage = response.usage

                    if hasattr(usage, 'prompt_tokens'):
                        llm_tokens_used_total.labels(
                            provider=provider,
                            model=model,
                            type='prompt'
                        ).inc(usage.prompt_tokens)

                        llm_tokens_per_request.labels(
                            provider=provider,
                            model=model,
                            type='prompt'
                        ).observe(usage.prompt_tokens)

                    if hasattr(usage, 'completion_tokens'):
                        llm_tokens_used_total.labels(
                            provider=provider,
                            model=model,
                            type='completion'
                        ).inc(usage.completion_tokens)

                        llm_tokens_per_request.labels(
                            provider=provider,
                            model=model,
                            type='completion'
                        ).observe(usage.completion_tokens)

                    if hasattr(usage, 'total_tokens'):
                        llm_tokens_used_total.labels(
                            provider=provider,
                            model=model,
                            type='total'
                        ).inc(usage.total_tokens)

                        llm_tokens_per_request.labels(
                            provider=provider,
                            model=model,
                            type='total'
                        ).observe(usage.total_tokens)

                        # Calculate and track cost
                        cost = calculate_cost(provider, model, usage)
                        if cost > 0:
                            llm_cost_usd_total.labels(
                                provider=provider,
                                model=model
                            ).inc(cost)

                            llm_cost_per_request_usd.labels(
                                provider=provider,
                                model=model
                            ).observe(cost)

                logger.info(
                    f"LLM request completed: {provider}/{model} "
                    f"(duration={duration:.3f}s)"
                )

                return response

            except Exception as e:
                duration = time.time() - start_time
                llm_request_duration_seconds.labels(
                    provider=provider,
                    model=model
                ).observe(duration)

                error_type = type(e).__name__
                llm_requests_total.labels(
                    provider=provider,
                    model=model,
                    status='error'
                ).inc()

                llm_errors_total.labels(
                    provider=provider,
                    model=model,
                    error_type=error_type
                ).inc()

                logger.error(f"LLM request failed: {provider}/{model} - {e}")
                raise

        return wrapper
    return decorator


def track_routing_decision(func: Callable):
    """Decorator to track routing decisions"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            decision = await func(*args, **kwargs)

            # Track routing latency
            duration = time.time() - start_time
            llm_routing_latency_seconds.observe(duration)

            # Track routing decision
            provider = decision.get('provider', 'unknown')
            reason = decision.get('reason', 'default')

            llm_routing_decisions_total.labels(
                selected_provider=provider,
                reason=reason
            ).inc()

            return decision

        except Exception as e:
            duration = time.time() - start_time
            llm_routing_latency_seconds.observe(duration)
            raise

    return wrapper


def track_streaming(provider: str, model: str):
    """Decorator to track streaming responses"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            first_token_time = None
            chunk_count = 0

            try:
                async for chunk in func(*args, **kwargs):
                    if first_token_time is None:
                        first_token_time = time.time() - start_time
                        llm_streaming_time_to_first_token_seconds.labels(
                            provider=provider,
                            model=model
                        ).observe(first_token_time)

                    chunk_count += 1
                    llm_streaming_chunks_total.labels(
                        provider=provider,
                        model=model
                    ).inc()

                    yield chunk

            except Exception as e:
                logger.error(f"Streaming error: {e}")
                raise

        return wrapper
    return decorator


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def calculate_cost(provider: str, model: str, usage) -> float:
    """
    Calculate cost based on token usage

    Pricing as of 2025 (approximate):
    """
    pricing = {
        'openai': {
            'gpt-4o': {'prompt': 0.005 / 1000, 'completion': 0.015 / 1000},
            'gpt-4-turbo': {'prompt': 0.01 / 1000, 'completion': 0.03 / 1000},
            'gpt-3.5-turbo': {'prompt': 0.0005 / 1000, 'completion': 0.0015 / 1000},
        },
        'anthropic': {
            'claude-3-opus': {'prompt': 0.015 / 1000, 'completion': 0.075 / 1000},
            'claude-3-sonnet': {'prompt': 0.003 / 1000, 'completion': 0.015 / 1000},
            'claude-3-haiku': {'prompt': 0.00025 / 1000, 'completion': 0.00125 / 1000},
        }
    }

    if provider not in pricing or model not in pricing[provider]:
        return 0.0

    model_pricing = pricing[provider][model]
    prompt_cost = usage.prompt_tokens * model_pricing['prompt']
    completion_cost = usage.completion_tokens * model_pricing['completion']

    return prompt_cost + completion_cost


def update_provider_availability(provider: str, available: bool):
    """
    Update provider availability metric

    Args:
        provider: Provider name
        available: Availability status
    """
    llm_provider_availability.labels(provider=provider).set(1 if available else 0)


def track_cache_hit(provider: str, model: str, hit: bool):
    """
    Track cache hit/miss

    Args:
        provider: Provider name
        model: Model name
        hit: Whether it was a cache hit
    """
    if hit:
        llm_cache_hits_total.labels(provider=provider, model=model).inc()
    else:
        llm_cache_misses_total.labels(provider=provider, model=model).inc()


def set_llm_health(provider: str, healthy: bool):
    """
    Set health status for LLM provider

    Args:
        provider: Provider name (openai, anthropic, etc.)
        healthy: Health status
    """
    llm_health_status.labels(provider=provider).set(1 if healthy else 0)


# ============================================================================
# INITIALIZATION
# ============================================================================

def init_llm_metrics():
    """Initialize LLM metrics with system info"""

    llm_system_info.info({
        'version': '1.0.0',
        'module': 'llm',
        'platform': 'AI-Platform-ISO',
        'providers': 'openai,anthropic',
        'router': 'adaptive',
        'cache': 'redis'
    })

    # Set initial health status
    for provider in ['openai', 'anthropic']:
        llm_health_status.labels(provider=provider).set(0)
        llm_provider_availability.labels(provider=provider).set(0)

    logger.info("✅ LLM Prometheus metrics initialized")


# Initialize on module import
init_llm_metrics()
