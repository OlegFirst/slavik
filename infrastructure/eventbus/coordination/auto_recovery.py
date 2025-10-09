"""
Auto-Recovery Service (Phase 1 - Task 1.2, Enhanced in Phase 1.1)
==================================================================

Listens to health events and recovers failed services automatically.

Features:
- Subscribes to infrastructure.health.unhealthy events
- Executes recovery strategies (restart, failover, circuit_breaker)
- Retry logic with exponential backoff
- Recovery history tracking
- Publishes recovery events
- ESCALATION MECHANISM (Phase 1.1):
  * Escalates to humans when recovery fails
  * Stops auto-recovery after escalation
  * Pattern detection for repeated failures
  * Critical service prioritization

Events:
- Subscribes: infrastructure.health.unhealthy, infrastructure.health.degraded
- Publishes: infrastructure.recovery.started, infrastructure.recovery.completed,
             infrastructure.recovery.failed, infrastructure.escalation.created
"""

import logging
import asyncio
from typing import Dict, Callable, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RecoveryStrategy:
    """Recovery strategy configuration for a service"""
    service_name: str
    strategy_type: str  # restart, failover, circuit_breaker
    max_attempts: int = 3
    backoff_seconds: int = 5
    recovery_function: Optional[Callable] = None


class AutoRecovery:
    """
    Auto-Recovery Service

    Monitors health events and automatically recovers failed services.

    Example:
        ```python
        from infrastructure.eventbus import create_eventbus

        bus = create_eventbus('redis')
        recovery = AutoRecovery(bus)

        # Register recovery strategy
        await recovery.register_strategy(RecoveryStrategy(
            service_name='api_gateway',
            strategy_type='restart',
            max_attempts=3,
            backoff_seconds=10
        ))

        # Start auto-recovery
        await recovery.start()
        ```
    """

    def __init__(self, eventbus, decision_center=None, escalation_manager=None):
        """
        Initialize Auto-Recovery Service

        Args:
            eventbus: EventBus instance (IEventBus)
            decision_center: Optional InfrastructureDecisionCenter instance (Phase 1.1)
            escalation_manager: Optional EscalationManager instance (Phase 1.1)
        """
        self.eventbus = eventbus
        self.decision_center = decision_center
        self.escalation_manager = escalation_manager
        self.strategies: Dict[str, RecoveryStrategy] = {}
        self.recovery_in_progress: Dict[str, bool] = {}
        self.recovery_history: Dict[str, list] = {}
        self.degraded_timers: Dict[str, datetime] = {}  # Track when service became degraded
        self.recovery_start_times: Dict[str, datetime] = {}  # Track when recovery started (for escalation)
        self.running = False
        logger.info(f"AutoRecovery initialized (decision_center={'enabled' if decision_center else 'disabled'}, escalation_manager={'enabled' if escalation_manager else 'disabled'})")

    async def start(self):
        """Start auto-recovery service - subscribe to health events"""
        self.running = True

        # Subscribe to health events
        await self.eventbus.subscribe('infrastructure.health.unhealthy', self._handle_unhealthy)
        await self.eventbus.subscribe('infrastructure.health.degraded', self._handle_degraded)

        logger.info("✅ AutoRecovery started - listening for health events")

    async def stop(self):
        """Stop auto-recovery service"""
        self.running = False
        logger.info("AutoRecovery stopped")

    async def register_strategy(self, strategy: RecoveryStrategy):
        """
        Register recovery strategy for a service

        Args:
            strategy: RecoveryStrategy configuration
        """
        self.strategies[strategy.service_name] = strategy
        self.recovery_history[strategy.service_name] = []
        logger.info(f"Registered {strategy.strategy_type} recovery for {strategy.service_name}")

    async def _handle_unhealthy(self, event):
        """
        Handle unhealthy service event

        Args:
            event: Event with service health status
        """
        service_name = event.data['service_name']
        logger.warning(f"🚨 Service {service_name} is UNHEALTHY - triggering recovery")

        await self._trigger_recovery(service_name, event)

    async def _handle_degraded(self, event):
        """
        Handle degraded service event

        For degraded services, wait 60 seconds before recovering
        (gives service time to self-recover)

        Args:
            event: Event with service health status
        """
        service_name = event.data['service_name']
        logger.info(f"⚠️  Service {service_name} is DEGRADED - monitoring closely")

        # Track when service became degraded
        if service_name not in self.degraded_timers:
            self.degraded_timers[service_name] = datetime.utcnow()
            logger.info(f"Starting 60s grace period for {service_name}")

            # Schedule check after 60 seconds
            await asyncio.sleep(60)

            # Check if still degraded (and hasn't become healthy or already recovering)
            if service_name in self.degraded_timers and not self.recovery_in_progress.get(service_name, False):
                logger.warning(f"Service {service_name} degraded for >60s - triggering recovery")
                await self._trigger_recovery(service_name, event)

            # Clear timer
            if service_name in self.degraded_timers:
                del self.degraded_timers[service_name]
        else:
            # Already tracking - service still degraded
            elapsed = (datetime.utcnow() - self.degraded_timers[service_name]).total_seconds()
            logger.info(f"Service {service_name} degraded for {elapsed:.0f}s")

    async def _trigger_recovery(self, service_name: str, trigger_event):
        """
        Trigger recovery for a service

        Args:
            service_name: Name of the service to recover
            trigger_event: Event that triggered recovery
        """
        # Check if recovery already in progress
        if self.recovery_in_progress.get(service_name, False):
            logger.warning(f"Recovery already in progress for {service_name} - skipping")
            return

        # Check if recovery is blocked by escalation (Phase 1.1)
        if self.escalation_manager and not self.escalation_manager.is_recovery_allowed(service_name):
            logger.warning(f"❌ Recovery BLOCKED for {service_name} - escalation in progress")
            return

        # Get recovery strategy
        strategy = self.strategies.get(service_name)
        if not strategy:
            logger.error(f"❌ No recovery strategy registered for {service_name}")
            return

        self.recovery_in_progress[service_name] = True
        self.recovery_start_times[service_name] = datetime.utcnow()  # Track start time for escalation

        # Publish recovery started event
        from infrastructure.eventbus import Event
        await self.eventbus.publish(Event.create(
            event_type='infrastructure.recovery.started',
            data={
                'service_name': service_name,
                'strategy': strategy.strategy_type,
                'max_attempts': strategy.max_attempts,
                'trigger': trigger_event.data
            },
            source='auto_recovery',
            tenant_id='system',
            correlation_id=trigger_event.id
        ))

        logger.info(f"🔧 Starting {strategy.strategy_type} recovery for {service_name}")

        # Execute recovery with retries
        success = await self._execute_recovery(strategy)

        # Record history
        recovery_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'strategy': strategy.strategy_type,
            'success': success,
            'trigger_status': trigger_event.data['status'],
            'trigger_message': trigger_event.data.get('message')
        }
        self.recovery_history[service_name].append(recovery_record)

        # Publish recovery result
        if success:
            await self.eventbus.publish(Event.create(
                event_type='infrastructure.recovery.completed',
                data={
                    'service_name': service_name,
                    'strategy': strategy.strategy_type,
                    'attempts_used': recovery_record.get('attempts_used', 1)
                },
                source='auto_recovery',
                tenant_id='system',
                correlation_id=trigger_event.id
            ))
            logger.info(f"✅ Recovery SUCCESSFUL for {service_name}")
        else:
            await self.eventbus.publish(Event.create(
                event_type='infrastructure.recovery.failed',
                data={
                    'service_name': service_name,
                    'strategy': strategy.strategy_type,
                    'attempts': strategy.max_attempts,
                    'reason': 'Max retries exceeded'
                },
                source='auto_recovery',
                tenant_id='system',
                correlation_id=trigger_event.id
            ))
            logger.error(f"❌ Recovery FAILED for {service_name} after {strategy.max_attempts} attempts")

        self.recovery_in_progress[service_name] = False

    async def _execute_recovery(self, strategy: RecoveryStrategy) -> bool:
        """
        Execute recovery with retries and escalation checks (Phase 1.1)

        Args:
            strategy: RecoveryStrategy to execute

        Returns:
            bool: True if recovery successful, False otherwise
        """
        service_name = strategy.service_name
        recovery_start_time = self.recovery_start_times.get(service_name, datetime.utcnow())

        for attempt in range(1, strategy.max_attempts + 1):
            logger.info(f"Recovery attempt {attempt}/{strategy.max_attempts} for {service_name}")

            # NEW: Check with Decision Center BEFORE attempting recovery (Phase 1.1)
            if self.decision_center:
                decision, can_proceed = await self.decision_center.decide_recovery_action(
                    service_name=service_name,
                    action_type=strategy.strategy_type,
                    current_attempt=attempt
                )

                if not can_proceed:
                    logger.warning(
                        f"Recovery BLOCKED by Decision Center for {service_name}: "
                        f"{decision.reasoning}"
                    )
                    # Audit log already done by Decision Center
                    # Stop recovery - escalation may have been created
                    return False

            # Check if should escalate BEFORE attempting recovery (Phase 1.1)
            if self.escalation_manager and attempt > 1:  # Don't escalate on first attempt
                should_escalate, reason = self.escalation_manager.should_escalate(
                    service_name=service_name,
                    current_attempts=attempt,
                    recovery_start_time=recovery_start_time,
                    is_still_unhealthy=True  # Still attempting recovery
                )

                if should_escalate:
                    logger.warning(f"🚨 ESCALATING {service_name} - {reason.value}")

                    # Calculate recovery duration
                    recovery_duration = (datetime.utcnow() - recovery_start_time).total_seconds()

                    # Create escalation
                    await self.escalation_manager.escalate(
                        service_name=service_name,
                        reason=reason,
                        recovery_attempts=attempt - 1,  # Attempts made so far
                        recovery_duration=recovery_duration,
                        metadata={
                            'strategy': strategy.strategy_type,
                            'max_attempts': strategy.max_attempts,
                            'last_attempt': attempt - 1
                        }
                    )

                    # STOP recovery - escalation manager has taken over
                    logger.warning(f"🛑 Stopping auto-recovery for {service_name} - escalated to humans")
                    return False

            try:
                if strategy.recovery_function:
                    # Execute custom recovery function
                    await strategy.recovery_function(service_name)
                else:
                    # Default recovery based on type
                    await self._default_recovery(strategy)

                # Wait for service to come back up
                wait_time = strategy.backoff_seconds
                logger.info(f"Waiting {wait_time}s for service to recover...")
                await asyncio.sleep(wait_time)

                # In production, would check service health here
                # For now, assume success after wait
                logger.info(f"✅ Attempt {attempt} completed")
                return True

            except Exception as e:
                logger.error(f"❌ Recovery attempt {attempt} failed: {e}")

                # Record failure for pattern detection
                if self.escalation_manager:
                    self.escalation_manager.record_failure(service_name)

                if attempt < strategy.max_attempts:
                    # Exponential backoff
                    wait_time = strategy.backoff_seconds * (2 ** (attempt - 1))
                    logger.info(f"Waiting {wait_time}s before next attempt...")
                    await asyncio.sleep(wait_time)

        # All attempts failed - check if should escalate
        if self.escalation_manager:
            recovery_duration = (datetime.utcnow() - recovery_start_time).total_seconds()

            from infrastructure.decision_center.escalation_manager import EscalationReason

            logger.warning(f"🚨 All recovery attempts failed for {service_name} - ESCALATING")

            await self.escalation_manager.escalate(
                service_name=service_name,
                reason=EscalationReason.MAX_ATTEMPTS_REACHED,
                recovery_attempts=strategy.max_attempts,
                recovery_duration=recovery_duration,
                metadata={
                    'strategy': strategy.strategy_type,
                    'all_attempts_failed': True
                }
            )

        return False

    async def _default_recovery(self, strategy: RecoveryStrategy):
        """
        Default recovery actions by strategy type

        Args:
            strategy: RecoveryStrategy to execute
        """
        if strategy.strategy_type == 'restart':
            logger.info(f"🔄 Restarting {strategy.service_name}...")
            # TODO: Call Docker restart or systemctl restart
            # For demo, just log
            await asyncio.sleep(1)

        elif strategy.strategy_type == 'failover':
            logger.info(f"🔀 Failing over {strategy.service_name}...")
            # TODO: Redirect traffic to backup instance
            await asyncio.sleep(1)

        elif strategy.strategy_type == 'circuit_breaker':
            logger.info(f"⚡ Opening circuit breaker for {strategy.service_name}...")
            # TODO: Stop sending traffic, use fallback
            await asyncio.sleep(1)

        else:
            logger.warning(f"Unknown strategy type: {strategy.strategy_type}")

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get recovery statistics

        Returns:
            Dict with recovery stats
        """
        total_recoveries = sum(len(h) for h in self.recovery_history.values())
        successful_recoveries = sum(
            len([r for r in h if r['success']])
            for h in self.recovery_history.values()
        )

        return {
            'running': self.running,
            'registered_strategies': len(self.strategies),
            'recovery_in_progress': sum(self.recovery_in_progress.values()),
            'total_recoveries': total_recoveries,
            'successful_recoveries': successful_recoveries,
            'success_rate': (successful_recoveries / total_recoveries * 100) if total_recoveries > 0 else 0,
            'history_by_service': {
                service: {
                    'total': len(history),
                    'successful': len([r for r in history if r['success']]),
                    'latest': history[-1] if history else None
                }
                for service, history in self.recovery_history.items()
            }
        }
