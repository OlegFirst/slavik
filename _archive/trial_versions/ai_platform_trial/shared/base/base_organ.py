"""
Base Organ Class

Unified base for all AI organs in the platform
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging
import asyncio

logger = logging.getLogger(__name__)


class BaseOrgan(ABC):
    """
    Base class for all AI Organs

    Organs are execution workers that perform heavy computations.
    They work autonomously on delegated tasks from Experts.

    Like body organs:
    - Brain (Expert) delegates to Heart/Lungs (Organs)
    - Organs do heavy lifting
    - Organs report back to Brain
    """

    def __init__(
        self,
        name: str,
        segment: str,  # 'governance', 'platform', or 'domain'
        function: str,
        description: str,
        llm_client: Any = None,
        max_concurrent_tasks: int = 5
    ):
        """
        Initialize Organ

        Args:
            name: Organ name (e.g., "Impact Oracle")
            segment: Segment this organ belongs to
            function: What this organ does
            description: Detailed description
            llm_client: AI client for computations
            max_concurrent_tasks: Max parallel tasks
        """
        self.name = name
        self.segment = segment
        self.function = function
        self.description = description
        self.llm_client = llm_client
        self.max_concurrent_tasks = max_concurrent_tasks
        self.logger = logger

        # Task queue and execution
        self.task_queue = asyncio.Queue()
        self.active_tasks = 0
        self.is_running = False

        # Metrics
        self.tasks_processed = 0
        self.avg_processing_time = 0.0
        self.success_rate = 1.0

    @abstractmethod
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task

        Args:
            task: Task specification

        Returns:
            Processing result
        """
        pass

    async def start(self):
        """Start organ processing loop"""
        self.is_running = True
        self.logger.info(f"Organ '{self.name}' started")

        # Start worker tasks
        workers = [
            asyncio.create_task(self._worker())
            for _ in range(self.max_concurrent_tasks)
        ]

        await asyncio.gather(*workers)

    async def stop(self):
        """Stop organ processing"""
        self.is_running = False
        self.logger.info(f"Organ '{self.name}' stopped")

    async def _worker(self):
        """Worker that processes tasks from queue"""
        while self.is_running:
            try:
                # Get task from queue (with timeout to allow graceful shutdown)
                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )

                self.active_tasks += 1

                # Process task
                await self._safe_process(task)

                self.active_tasks -= 1
                self.task_queue.task_done()

            except asyncio.TimeoutError:
                # No tasks in queue, continue loop
                continue
            except Exception as e:
                self.logger.error(f"Worker error in organ '{self.name}': {e}")
                self.active_tasks -= 1

    async def submit_task(self, task: Dict[str, Any]) -> asyncio.Future:
        """
        Submit task to organ for processing

        Args:
            task: Task specification

        Returns:
            Future that will contain the result
        """
        future = asyncio.Future()
        task_with_future = {
            "task": task,
            "future": future
        }

        await self.task_queue.put(task_with_future)

        return future

    async def _safe_process(self, task_with_future: Dict[str, Any]):
        """
        Process task with error handling and metrics

        Args:
            task_with_future: Task with future for result
        """
        import time

        task = task_with_future["task"]
        future = task_with_future["future"]

        start_time = time.time()

        try:
            # Process task
            result = await self.process(task)

            # Track success
            processing_time = time.time() - start_time
            self._track_task(success=True, processing_time=processing_time)

            # Set result
            future.set_result({
                "success": True,
                "result": result,
                "processing_time": processing_time
            })

        except Exception as e:
            # Track failure
            processing_time = time.time() - start_time
            self._track_task(success=False, processing_time=processing_time)

            self.logger.error(f"Organ '{self.name}' task failed: {e}")

            # Set error
            future.set_exception(e)

    def _track_task(self, success: bool, processing_time: float):
        """Track task metrics"""
        self.tasks_processed += 1

        # Update average processing time
        if self.avg_processing_time == 0:
            self.avg_processing_time = processing_time
        else:
            self.avg_processing_time = (
                self.avg_processing_time * 0.9 + processing_time * 0.1
            )

        # Update success rate
        if success:
            self.success_rate = self.success_rate * 0.95 + 1.0 * 0.05
        else:
            self.success_rate = self.success_rate * 0.95 + 0.0 * 0.05

    async def _query_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7
    ) -> str:
        """
        Query LLM for computations

        Args:
            system_prompt: System instruction
            user_prompt: User query
            temperature: LLM temperature

        Returns:
            LLM response
        """
        if not self.llm_client:
            return f"[MOCK] {self.name} computation result"

        try:
            response = await self.llm_client.query(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature
            )
            return response
        except Exception as e:
            self.logger.error(f"LLM query failed in organ '{self.name}': {e}")
            raise

    def get_status(self) -> Dict[str, Any]:
        """Get organ status"""
        return {
            "name": self.name,
            "segment": self.segment,
            "function": self.function,
            "is_running": self.is_running,
            "active_tasks": self.active_tasks,
            "queued_tasks": self.task_queue.qsize(),
            "metrics": {
                "tasks_processed": self.tasks_processed,
                "avg_processing_time": self.avg_processing_time,
                "success_rate": self.success_rate
            }
        }

    def get_info(self) -> Dict[str, Any]:
        """Get organ information"""
        return {
            "name": self.name,
            "segment": self.segment,
            "function": self.function,
            "description": self.description,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "metrics": {
                "tasks_processed": self.tasks_processed,
                "avg_processing_time": self.avg_processing_time,
                "success_rate": self.success_rate
            }
        }
