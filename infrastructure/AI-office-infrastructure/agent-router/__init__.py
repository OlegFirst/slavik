"""
AI Agent Router Module - Enhanced v2.0

Intelligent service routing for BCM Platform with Docker AI Agent pattern
and GitHub App integration.

ИНТЕГРАЦИИ:
- Circuit Breaker для защиты от cascade failures
- Prometheus metrics для мониторинга
- Rate Limiting для защиты от перегрузки
- Advanced Load Balancing (response time based)

Extracted from: intelligent-core/orchestration/ai_agent_router.py
Date: 2025-10-04
Enhanced: 2025-10-07
"""

from .router import AIAgentRouter, AgentCapability, AgentRole, AIAgent, RateLimiter

# Optional imports
try:
    from .circuit_breaker import (
        CircuitBreaker, CircuitBreakerManager, CircuitBreakerConfig,
        CircuitBreakerOpenError, CircuitState
    )
    __all_circuit_breaker__ = [
        'CircuitBreaker', 'CircuitBreakerManager', 'CircuitBreakerConfig',
        'CircuitBreakerOpenError', 'CircuitState'
    ]
except ImportError:
    __all_circuit_breaker__ = []

try:
    from . import metrics
    __all_metrics__ = ['metrics']
except ImportError:
    __all_metrics__ = []

__all__ = [
    'AIAgentRouter', 'AgentCapability', 'AgentRole', 'AIAgent', 'RateLimiter'
] + __all_circuit_breaker__ + __all_metrics__

__version__ = "2.0.0"
