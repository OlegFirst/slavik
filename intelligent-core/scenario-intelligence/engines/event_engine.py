"""
Event Engine - Event Storming Implementation

Обрабатывает асинхронные события (pub/sub)
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventBus:
    """
    Простая реализация Event Bus (in-memory pub/sub)

    В production можно заменить на Redis Pub/Sub, Kafka, RabbitMQ
    """

    def __init__(self):
        self.subscribers = {}  # event_type -> [callbacks]

    async def publish(self, event_type: str, event: Dict[str, Any]):
        """Опубликовать событие"""

        logger.debug(f"    📡 Publishing event: {event_type}")

        if event_type in self.subscribers:
            callbacks = self.subscribers[event_type]

            # Вызвать все подписчики асинхронно
            await asyncio.gather(*[
                callback(event)
                for callback in callbacks
            ], return_exceptions=True)

    async def subscribe(self, event_type: str, callback: Callable):
        """Подписаться на событие"""

        if event_type not in self.subscribers:
            self.subscribers[event_type] = []

        self.subscribers[event_type].append(callback)
        logger.debug(f"    📨 Subscribed to event: {event_type}")

    def unsubscribe(self, event_type: str, callback: Callable):
        """Отписаться от события"""

        if event_type in self.subscribers:
            if callback in self.subscribers[event_type]:
                self.subscribers[event_type].remove(callback)


# Global Event Bus instance
global_event_bus = EventBus()


class EventEngine:
    """
    Движок для асинхронных событий (Event Storming)

    Поддерживает:
    - Domain Events (emits)
    - Event Subscriptions (triggered_by)
    - Policies (автоматические реакции)
    """

    def __init__(self):
        self.event_bus = global_event_bus
        self.subscriptions_registry = {}  # scenario_id -> [event_types]

    async def emit_events(
        self,
        events: List[Dict[str, Any]],
        context: Dict[str, Any]
    ):
        """
        Испустить события (emits)

        Args:
            events: Список конфигураций событий
            context: Контекст для резолва переменных
        """

        for event_config in events:
            event_type = event_config.get('event_type')

            if not event_type:
                logger.warning("    ⚠️  Event without event_type, skipping")
                continue

            # Resolve payload
            payload = self._resolve_payload(
                event_config.get('payload', {}),
                context
            )

            # Создать событие
            event = {
                'type': event_type,
                'aggregate': event_config.get('aggregate'),
                'aggregate_id': event_config.get('aggregate_id'),
                'payload': payload,
                'timestamp': datetime.utcnow().isoformat(),
                'correlation_id': context.get('correlation_id', str(uuid.uuid4())),
                'subscribers': event_config.get('subscribers', [])
            }

            logger.info(f"    📡 Emitting event: {event_type}")

            # Опубликовать в Event Bus
            await self.event_bus.publish(event_type, event)

    async def subscribe_scenario(
        self,
        scenario_id: str,
        event_types: List[str]
    ):
        """
        Подписать сценарий на события

        Args:
            scenario_id: ID сценария
            event_types: Список типов событий
        """

        if scenario_id not in self.subscriptions_registry:
            self.subscriptions_registry[scenario_id] = []

        for event_type in event_types:
            if event_type not in self.subscriptions_registry[scenario_id]:
                self.subscriptions_registry[scenario_id].append(event_type)

                # Подписаться в Event Bus
                await self.event_bus.subscribe(
                    event_type,
                    lambda event: self._handle_event(event, scenario_id)
                )

                logger.info(f"  📨 Scenario {scenario_id} subscribed to {event_type}")

    async def _handle_event(
        self,
        event: Dict[str, Any],
        scenario_id: str
    ):
        """
        Обработать событие - запустить сценарий

        Args:
            event: Событие
            scenario_id: ID сценария который нужно запустить
        """

        logger.info(f"  🎯 Event {event['type']} triggered scenario: {scenario_id}")

        try:
            # Загрузить сценарий
            from storage.registry import ScenarioRegistry
            registry = ScenarioRegistry()
            scenario = await registry.get_scenario_by_id(scenario_id)

            if not scenario:
                logger.error(f"    ❌ Scenario {scenario_id} not found")
                return

            # Запустить сценарий с событием в контексте
            from .scenario_engine import ScenarioEngine
            engine = ScenarioEngine()

            await engine.execute_scenario(
                scenario,
                context={'event': event}
            )

        except Exception as e:
            logger.error(f"    ❌ Failed to handle event: {e}", exc_info=True)

    def _resolve_payload(
        self,
        payload: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve переменных в payload
        """

        resolved = {}

        for key, value in payload.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                var_path = value[2:-2].strip()
                resolved_value = self._get_from_context(var_path, context)
                resolved[key] = resolved_value if resolved_value is not None else value
            elif isinstance(value, dict):
                resolved[key] = self._resolve_payload(value, context)
            else:
                resolved[key] = value

        return resolved

    def _get_from_context(
        self,
        path: str,
        context: Dict[str, Any]
    ) -> Any:
        """Получить значение из контекста по пути"""

        parts = path.split('.')
        value = context

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
                if value is None:
                    return None
            else:
                return None

        return value


# Test
async def main():
    """Test Event Engine"""

    event_engine = EventEngine()

    # Подписать тестовый сценарий на событие
    await event_engine.subscribe_scenario(
        scenario_id='test-scenario',
        event_types=['user.bia.created']
    )

    # Испустить событие
    await event_engine.emit_events(
        events=[
            {
                'event_type': 'user.bia.created',
                'aggregate': 'BIAAssessment',
                'aggregate_id': 'bia_123',
                'payload': {
                    'bia_id': 'bia_123',
                    'user_id': 'user_456',
                    'org_id': 'hospital_1'
                }
            }
        ],
        context={}
    )

    # Дать время на обработку
    await asyncio.sleep(1)

    print("\n✅ Event Engine test completed")


if __name__ == "__main__":
    asyncio.run(main())
