"""
Infrastructure Coordination (Phase 1)
======================================

Coordination services for infrastructure level.

Components:
- AutoRecovery: Automatic service recovery
- ResourceOptimizer: Resource optimization (5 min cycle)
- InfrastructureCoordinator: Main coordinator

Usage:
    ```python
    from infrastructure.eventbus.coordination import AutoRecovery, RecoveryStrategy
    from infrastructure.eventbus import create_eventbus

    bus = create_eventbus('redis')
    recovery = AutoRecovery(bus)

    await recovery.register_strategy(RecoveryStrategy(
        service_name='api_gateway',
        strategy_type='restart',
        max_attempts=3
    ))

    await recovery.start()
    ```
"""

from infrastructure.eventbus.coordination.auto_recovery import AutoRecovery, RecoveryStrategy
from infrastructure.eventbus.coordination.resource_optimizer import ResourceOptimizer

__all__ = [
    'AutoRecovery',
    'RecoveryStrategy',
    'ResourceOptimizer',
]
