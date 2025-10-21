"""
EventBus ← → Celery Bridge
===========================

Listens to EventBus events and triggers Celery tasks
"""
import asyncio
import logging
from typing import Dict, Any

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from shared.eventbus import init_eventbus, get_eventbus
from tasks import learning_tasks, batch_tasks, prediction_tasks

logger = logging.getLogger(__name__)


class EventBusCeleryBridge:
    """
    Bridge between EventBus and Celery

    Listens to events and triggers appropriate tasks
    """

    def __init__(self):
        self.eventbus = None
        self.event_handlers = self._setup_handlers()

    def _setup_handlers(self) -> Dict[str, Any]:
        """Map events to Celery tasks"""

        return {
            # Learning events
            'case.completed': learning_tasks.learn_from_case,
            'model.update_requested': learning_tasks.update_all_models,
            'pattern.extraction_requested': learning_tasks.extract_patterns,

            # Batch processing events
            'document.batch_analysis_requested': self._handle_batch_analysis,

            # Prediction events
            'prediction.requested': prediction_tasks.generate_daily_predictions,
            'simulation.requested': prediction_tasks.run_monte_carlo_simulation,
            'forecast.requested': prediction_tasks.forecast_resource_needs,
        }

    async def start(self):
        """Start listening to EventBus"""

        rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5673/")
        self.eventbus = init_eventbus(rabbitmq_url)
        await self.eventbus.connect()

        logger.info(" EventBus ← → Celery Bridge started")

        # Subscribe to all events
        for event_type, handler in self.event_handlers.items():
            asyncio.create_task(
                self.eventbus.subscribe(event_type, self._create_wrapper(handler))
            )
            logger.info(f"   Subscribed: {event_type} → {handler.__name__}")

    def _create_wrapper(self, celery_task):
        """Wrap Celery task for EventBus"""

        async def wrapper(event):
            logger.info(f" Event received: {event.type} → triggering {celery_task.name}")

            try:
                # Trigger Celery task
                result = celery_task.delay(**event.data)

                logger.info(f" Task queued: {result.id}")

            except Exception as e:
                logger.error(f" Failed to queue task: {e}")

        return wrapper

    async def _handle_batch_analysis(self, event):
        """Handle batch document analysis"""

        doc_ids = event.data.get('doc_ids', [])
        analyzer_type = event.data.get('analyzer_type', 'compliance')

        logger.info(f" Batch analysis requested: {len(doc_ids)} documents")

        # Trigger parallel batch processing
        result = batch_tasks.batch_analyze_documents(doc_ids, analyzer_type)

        logger.info(f" Batch job queued: {result.id}")


async def main():
    """Run bridge"""
    bridge = EventBusCeleryBridge()
    await bridge.start()

    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info(" Shutting down bridge...")


if __name__ == '__main__':
    asyncio.run(main())
