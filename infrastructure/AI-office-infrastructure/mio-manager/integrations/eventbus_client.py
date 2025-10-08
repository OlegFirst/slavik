#!/usr/bin/env python3
"""
EventBus Client for MIO Manager
================================

Интеграция MIO Manager с EventBus для pub/sub коммуникации.

MIO Manager использует EventBus для:
- Publishing: Публикация problem_detected events
- Subscribing: Подписка на события от других сервисов

Events:
- mio.problem_detected - проблема обнаружена MIO
- mio.action_executed - действие выполнено
- mio.report_generated - отчет сгенерирован
- workflow.task_completed - задача выполнена (от coordination_center)
- workflow.directive_issued - директива от мозга
- platform.service_deployed - сервис задеплоен (от orchestration)
- platform.alert_triggered - алерт сработал (от monitoring)
"""

import sys
from pathlib import Path
import asyncio
import logging
from typing import Dict, Any, Callable, List, Optional
from datetime import datetime

# Add eventbus to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "eventbus"))

try:
    from infrastructure.eventbus import create_eventbus, Event, EventPriority, IEventBus
    EVENTBUS_AVAILABLE = True
except ImportError:
    EVENTBUS_AVAILABLE = False
    logging.warning("EventBus not available - running in fallback mode")

logger = logging.getLogger(__name__)


class EventBusClient:
    """
    Клиент для взаимодействия с EventBus.

    Provides:
    - publish() - публикация событий
    - subscribe() - подписка на события
    - start() - запуск background consumer
    - stop() - остановка consumer
    """

    def __init__(
        self,
        backend: str = 'redis',
        redis_url: str = 'redis://localhost:6379',
        consumer_group: str = 'mio-manager',
        tenant_id: str = 'platform'
    ):
        """
        Args:
            backend: 'memory' или 'redis'
            redis_url: URL Redis для production
            consumer_group: Consumer group для load balancing
            tenant_id: Tenant ID для multi-tenancy
        """
        self.backend = backend
        self.redis_url = redis_url
        self.consumer_group = consumer_group
        self.tenant_id = tenant_id

        self.bus: Optional[IEventBus] = None
        self.subscriptions: Dict[str, Callable] = {}
        self._consumer_task: Optional[asyncio.Task] = None
        self._running = False

        logger.info(
            f"EventBusClient initialized: backend={backend}, "
            f"consumer_group={consumer_group}"
        )

    async def initialize(self):
        """Инициализировать EventBus connection."""
        if not EVENTBUS_AVAILABLE:
            logger.warning("EventBus not available - skipping initialization")
            return

        try:
            if self.backend == 'redis':
                self.bus = create_eventbus('redis', redis_url=self.redis_url)
            else:
                self.bus = create_eventbus('memory')

            logger.info(f"✅ EventBus connected: {self.backend}")

        except Exception as e:
            logger.error(f"Failed to initialize EventBus: {e}")
            self.bus = None

    # ========================================================================
    # PUBLISHING
    # ========================================================================

    async def publish_problem_detected(
        self,
        problem: Dict[str, Any],
        severity: str,
        source: str = 'mio-manager'
    ) -> bool:
        """
        Publish problem_detected event.

        Args:
            problem: Проблема (type, description, context)
            severity: Серьезность (low, medium, high, critical)
            source: Источник (откуда проблема)

        Returns:
            True если успешно
        """
        return await self._publish_event(
            event_type='mio.problem_detected',
            data={
                'problem': problem,
                'severity': severity,
                'detected_at': datetime.utcnow().isoformat()
            },
            source=source,
            priority=self._severity_to_priority(severity)
        )

    async def publish_action_executed(
        self,
        action: str,
        target: str,
        result: Dict[str, Any],
        level: str
    ) -> bool:
        """
        Publish action_executed event.

        Args:
            action: Действие (restart, scale, cleanup, etc.)
            target: Цель (service name)
            result: Результат выполнения
            level: Уровень (L1, L2, L3)

        Returns:
            True если успешно
        """
        return await self._publish_event(
            event_type='mio.action_executed',
            data={
                'action': action,
                'target': target,
                'result': result,
                'level': level,
                'executed_at': datetime.utcnow().isoformat()
            },
            source='mio-manager'
        )

    async def publish_report_generated(
        self,
        report_type: str,
        report_id: str,
        summary: Dict[str, Any]
    ) -> bool:
        """
        Publish report_generated event.

        Args:
            report_type: Тип отчета (daily, weekly, monthly)
            report_id: ID отчета
            summary: Краткое содержание

        Returns:
            True если успешно
        """
        return await self._publish_event(
            event_type='mio.report_generated',
            data={
                'report_type': report_type,
                'report_id': report_id,
                'summary': summary,
                'generated_at': datetime.utcnow().isoformat()
            },
            source='mio-manager'
        )

    async def _publish_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        source: str,
        priority: EventPriority = EventPriority.NORMAL
    ) -> bool:
        """
        Внутренний метод для публикации события.

        Args:
            event_type: Тип события
            data: Данные
            source: Источник
            priority: Приоритет

        Returns:
            True если успешно
        """
        if not self.bus:
            logger.warning(f"EventBus not available - cannot publish {event_type}")
            return False

        try:
            event = Event.create(
                event_type=event_type,
                data=data,
                source=source,
                tenant_id=self.tenant_id,
                priority=priority
            )

            await self.bus.publish(event)

            logger.debug(f"✅ Published event: {event_type}")
            return True

        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            return False

    # ========================================================================
    # SUBSCRIBING
    # ========================================================================

    async def subscribe_to_problems(self, callback: Callable):
        """
        Подписаться на problem_detected события от других сервисов.

        Args:
            callback: async function(event: Event) -> None
        """
        await self._subscribe('platform.problem_detected', callback)

    async def subscribe_to_tasks(self, callback: Callable):
        """
        Подписаться на task_completed события от coordination_center.

        Args:
            callback: async function(event: Event) -> None
        """
        await self._subscribe('workflow.task_completed', callback)

    async def subscribe_to_directives(self, callback: Callable):
        """
        Подписаться на directive_issued события от workflow_intelligence.

        Args:
            callback: async function(event: Event) -> None
        """
        await self._subscribe('workflow.directive_issued', callback)

    async def subscribe_to_deployments(self, callback: Callable):
        """
        Подписаться на service_deployed события от orchestration.

        Args:
            callback: async function(event: Event) -> None
        """
        await self._subscribe('platform.service_deployed', callback)

    async def subscribe_to_alerts(self, callback: Callable):
        """
        Подписаться на alert_triggered события от monitoring.

        Args:
            callback: async function(event: Event) -> None
        """
        await self._subscribe('platform.alert_triggered', callback)

    async def _subscribe(self, event_type: str, callback: Callable):
        """
        Внутренний метод для подписки.

        Args:
            event_type: Тип события (supports wildcards: workflow.*)
            callback: async function(event: Event) -> None
        """
        if not self.bus:
            logger.warning(f"EventBus not available - cannot subscribe to {event_type}")
            return

        try:
            # Wrap callback для error handling
            async def wrapped_callback(event: Event):
                try:
                    await callback(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")

            await self.bus.subscribe(event_type, wrapped_callback)

            self.subscriptions[event_type] = wrapped_callback

            logger.info(f"✅ Subscribed to: {event_type}")

        except Exception as e:
            logger.error(f"Failed to subscribe to {event_type}: {e}")

    # ========================================================================
    # BACKGROUND CONSUMER
    # ========================================================================

    async def start_consumer(self):
        """
        Запустить background consumer для обработки событий.

        Запускает бесконечный loop для consume events.
        """
        if not self.bus:
            logger.warning("EventBus not available - cannot start consumer")
            return

        if self._running:
            logger.warning("Consumer already running")
            return

        self._running = True
        self._consumer_task = asyncio.create_task(self._consume_loop())

        logger.info("✅ EventBus consumer started")

    async def stop_consumer(self):
        """Остановить background consumer."""
        if not self._running:
            return

        self._running = False

        if self._consumer_task:
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass

        logger.info("✅ EventBus consumer stopped")

    async def _consume_loop(self):
        """
        Background loop для consume events.

        Работает пока self._running == True.
        """
        logger.info("Starting event consumption loop...")

        while self._running:
            try:
                # NOTE: EventBus subscriptions работают через callbacks,
                # поэтому здесь просто спим и держим loop alive
                await asyncio.sleep(1)

            except asyncio.CancelledError:
                break

            except Exception as e:
                logger.error(f"Error in consume loop: {e}")
                await asyncio.sleep(5)  # Backoff

        logger.info("Event consumption loop stopped")

    # ========================================================================
    # LIFECYCLE
    # ========================================================================

    async def close(self):
        """Закрыть EventBus connection."""
        await self.stop_consumer()

        if self.bus:
            await self.bus.close()
            logger.info("✅ EventBus connection closed")

    # ========================================================================
    # HELPERS
    # ========================================================================

    @staticmethod
    def _severity_to_priority(severity: str) -> EventPriority:
        """Конвертировать severity в EventPriority."""
        mapping = {
            'critical': EventPriority.HIGH,
            'high': EventPriority.HIGH,
            'medium': EventPriority.NORMAL,
            'low': EventPriority.LOW
        }
        return mapping.get(severity, EventPriority.NORMAL)


# ============================================================================
# DEFAULT HANDLERS для стандартных событий
# ============================================================================

class DefaultEventHandlers:
    """
    Default handlers для событий от других сервисов.

    Эти handlers можно переопределить или расширить.
    """

    def __init__(self, escalation_manager, action_executor):
        """
        Args:
            escalation_manager: EscalationManager для L3 эскалаций
            action_executor: ActionExecutor для L1/L2 действий
        """
        self.escalation_manager = escalation_manager
        self.action_executor = action_executor

    async def handle_problem_detected(self, event: Event):
        """
        Обработать problem_detected от других сервисов.

        Может быть от monitoring, других MIO instances, etc.
        """
        logger.info(f"📨 Received problem from {event.source}: {event.data}")

        # Проанализировать и решить, нужна ли реакция
        problem = event.data.get('problem', {})
        severity = event.data.get('severity', 'medium')

        # Если critical - эскалировать к мозгу
        if severity == 'critical':
            await self.escalation_manager.escalate_to_brain(
                problem=problem,
                severity=severity,
                context={'received_from': event.source}
            )

    async def handle_task_completed(self, event: Event):
        """
        Обработать task_completed от coordination_center.

        Задача, которую мы делегировали, выполнена.
        """
        logger.info(f"✅ Task completed: {event.data}")

        task_id = event.data.get('task_id')
        result = event.data.get('result')

        # Обновить внутреннее состояние
        # TODO: Update task tracking in DB

    async def handle_directive_issued(self, event: Event):
        """
        Обработать directive_issued от workflow_intelligence (мозга).

        Мозг дал директиву - нужно выполнить.
        """
        logger.info(f"🧠 Directive from brain: {event.data}")

        directive = event.data.get('directive', {})
        action = directive.get('action')
        parameters = directive.get('parameters', {})

        # Выполнить директиву
        if action:
            await self.action_executor.execute(
                action=action,
                context=parameters
            )

    async def handle_service_deployed(self, event: Event):
        """
        Обработать service_deployed от orchestration.

        Новый сервис задеплоен - нужно добавить в мониторинг.
        """
        logger.info(f"🚀 Service deployed: {event.data}")

        service_name = event.data.get('service_name')

        # Добавить в discovery
        # TODO: Trigger ObservationWorkflow для нового сервиса

    async def handle_alert_triggered(self, event: Event):
        """
        Обработать alert_triggered от monitoring.

        Алерт сработал - нужно проанализировать и отреагировать.
        """
        logger.info(f"🚨 Alert triggered: {event.data}")

        alert = event.data.get('alert', {})
        severity = alert.get('severity', 'medium')

        # Проанализировать и решить уровень реакции
        # L1: автоматическое действие
        # L2: быстрое расследование
        # L3: эскалация к мозгу


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

_eventbus_client: Optional[EventBusClient] = None


async def get_eventbus_client(
    backend: str = 'redis',
    redis_url: str = 'redis://localhost:6379'
) -> EventBusClient:
    """
    Получить singleton instance EventBusClient.

    Usage:
        client = await get_eventbus_client()
        await client.publish_problem_detected(problem, 'high')
    """
    global _eventbus_client

    if _eventbus_client is None:
        _eventbus_client = EventBusClient(
            backend=backend,
            redis_url=redis_url
        )
        await _eventbus_client.initialize()

    return _eventbus_client
