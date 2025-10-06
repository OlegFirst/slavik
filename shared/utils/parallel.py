"""
Parallel Processing Utilities for BCM Platform

Provides utilities for parallel processing of bulk operations across services:
- parallel_map: Process list of items in parallel with configurable concurrency
- batched_process: Process items in batches
- gather_with_semaphore: Control concurrent tasks with semaphore
- Error handling with partial success reporting
- Progress tracking for long operations
"""

import asyncio
import logging
from typing import TypeVar, List, Callable, Awaitable, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

T = TypeVar('T')
R = TypeVar('R')


class OperationStatus(str, Enum):
    """Status of a parallel operation"""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class OperationResult:
    """Result of a single operation in parallel processing"""
    index: int
    input_data: Any
    status: OperationStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: Optional[float] = None


@dataclass
class BulkOperationReport:
    """Report for bulk operation execution"""
    total_count: int
    success_count: int
    failure_count: int
    timeout_count: int
    cancelled_count: int
    total_duration_ms: float
    results: List[OperationResult]

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage"""
        if self.total_count == 0:
            return 0.0
        return (self.success_count / self.total_count) * 100

    @property
    def failures(self) -> List[OperationResult]:
        """Get only failed operations"""
        return [r for r in self.results if r.status == OperationStatus.FAILURE]

    @property
    def successes(self) -> List[OperationResult]:
        """Get only successful operations"""
        return [r for r in self.results if r.status == OperationStatus.SUCCESS]


async def parallel_map(
    items: List[T],
    func: Callable[[T], Awaitable[R]],
    max_concurrency: int = 10,
    timeout_per_item: Optional[float] = None,
    continue_on_error: bool = True
) -> BulkOperationReport:
    """
    Process list of items in parallel with configurable concurrency.

    Args:
        items: List of items to process
        func: Async function to apply to each item
        max_concurrency: Maximum number of concurrent operations (default: 10)
        timeout_per_item: Timeout in seconds for each operation (optional)
        continue_on_error: Continue processing if individual items fail (default: True)

    Returns:
        BulkOperationReport with results and statistics

    Example:
        async def process_item(item: dict) -> dict:
            # Process item
            return result

        report = await parallel_map(
            items=data_list,
            func=process_item,
            max_concurrency=10,
            timeout_per_item=30.0
        )

        print(f"Success rate: {report.success_rate}%")
        print(f"Failures: {len(report.failures)}")
    """
    start_time = datetime.now()
    semaphore = asyncio.Semaphore(max_concurrency)
    results: List[OperationResult] = []

    async def process_with_semaphore(index: int, item: T) -> OperationResult:
        """Process single item with semaphore control"""
        async with semaphore:
            op_start = datetime.now()

            try:
                if timeout_per_item:
                    result = await asyncio.wait_for(
                        func(item),
                        timeout=timeout_per_item
                    )
                else:
                    result = await func(item)

                duration = (datetime.now() - op_start).total_seconds() * 1000

                return OperationResult(
                    index=index,
                    input_data=item,
                    status=OperationStatus.SUCCESS,
                    result=result,
                    duration_ms=duration
                )

            except asyncio.TimeoutError:
                duration = (datetime.now() - op_start).total_seconds() * 1000
                logger.warning(f"Operation {index} timed out after {timeout_per_item}s")

                return OperationResult(
                    index=index,
                    input_data=item,
                    status=OperationStatus.TIMEOUT,
                    error=f"Operation timed out after {timeout_per_item}s",
                    duration_ms=duration
                )

            except asyncio.CancelledError:
                duration = (datetime.now() - op_start).total_seconds() * 1000
                logger.warning(f"Operation {index} was cancelled")

                return OperationResult(
                    index=index,
                    input_data=item,
                    status=OperationStatus.CANCELLED,
                    error="Operation was cancelled",
                    duration_ms=duration
                )

            except Exception as e:
                duration = (datetime.now() - op_start).total_seconds() * 1000
                error_msg = f"{type(e).__name__}: {str(e)}"
                logger.error(f"Operation {index} failed: {error_msg}")

                if not continue_on_error:
                    raise

                return OperationResult(
                    index=index,
                    input_data=item,
                    status=OperationStatus.FAILURE,
                    error=error_msg,
                    duration_ms=duration
                )

    # Execute all operations in parallel
    tasks = [process_with_semaphore(i, item) for i, item in enumerate(items)]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    # Calculate statistics
    total_duration = (datetime.now() - start_time).total_seconds() * 1000

    success_count = sum(1 for r in results if r.status == OperationStatus.SUCCESS)
    failure_count = sum(1 for r in results if r.status == OperationStatus.FAILURE)
    timeout_count = sum(1 for r in results if r.status == OperationStatus.TIMEOUT)
    cancelled_count = sum(1 for r in results if r.status == OperationStatus.CANCELLED)

    return BulkOperationReport(
        total_count=len(items),
        success_count=success_count,
        failure_count=failure_count,
        timeout_count=timeout_count,
        cancelled_count=cancelled_count,
        total_duration_ms=total_duration,
        results=results
    )


async def batched_process(
    items: List[T],
    func: Callable[[List[T]], Awaitable[List[R]]],
    batch_size: int = 100,
    max_concurrency: int = 3,
    timeout_per_batch: Optional[float] = None
) -> BulkOperationReport:
    """
    Process items in batches for efficiency.

    Useful for database bulk operations where processing N items at once
    is more efficient than N individual operations.

    Args:
        items: List of items to process
        func: Async function that processes a batch and returns results
        batch_size: Number of items per batch (default: 100)
        max_concurrency: Maximum number of concurrent batches (default: 3)
        timeout_per_batch: Timeout in seconds for each batch (optional)

    Returns:
        BulkOperationReport with results and statistics

    Example:
        async def process_batch(batch: List[dict]) -> List[dict]:
            # Use bulk_insert_mappings or similar
            return results

        report = await batched_process(
            items=data_list,
            func=process_batch,
            batch_size=100,
            max_concurrency=3
        )
    """
    # Split items into batches
    batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]

    logger.info(f"Processing {len(items)} items in {len(batches)} batches (size={batch_size})")

    # Process batches in parallel
    async def process_batch_wrapper(batch_index: int, batch: List[T]) -> List[OperationResult]:
        """Process a batch and convert to OperationResults"""
        batch_start = datetime.now()

        try:
            if timeout_per_batch:
                results = await asyncio.wait_for(
                    func(batch),
                    timeout=timeout_per_batch
                )
            else:
                results = await func(batch)

            duration = (datetime.now() - batch_start).total_seconds() * 1000
            avg_duration = duration / len(batch)

            # Convert batch results to OperationResults
            operation_results = []
            for i, (item, result) in enumerate(zip(batch, results)):
                global_index = batch_index * batch_size + i
                operation_results.append(OperationResult(
                    index=global_index,
                    input_data=item,
                    status=OperationStatus.SUCCESS,
                    result=result,
                    duration_ms=avg_duration
                ))

            return operation_results

        except asyncio.TimeoutError:
            logger.warning(f"Batch {batch_index} timed out after {timeout_per_batch}s")

            # Mark all items in batch as timeout
            operation_results = []
            for i, item in enumerate(batch):
                global_index = batch_index * batch_size + i
                operation_results.append(OperationResult(
                    index=global_index,
                    input_data=item,
                    status=OperationStatus.TIMEOUT,
                    error=f"Batch operation timed out after {timeout_per_batch}s"
                ))

            return operation_results

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"Batch {batch_index} failed: {error_msg}")

            # Mark all items in batch as failed
            operation_results = []
            for i, item in enumerate(batch):
                global_index = batch_index * batch_size + i
                operation_results.append(OperationResult(
                    index=global_index,
                    input_data=item,
                    status=OperationStatus.FAILURE,
                    error=error_msg
                ))

            return operation_results

    # Process batches with concurrency control
    report = await parallel_map(
        items=list(enumerate(batches)),
        func=lambda x: process_batch_wrapper(x[0], x[1]),
        max_concurrency=max_concurrency,
        timeout_per_item=timeout_per_batch
    )

    # Flatten results
    all_results = []
    for batch_result in report.results:
        if batch_result.result:
            all_results.extend(batch_result.result)

    # Recalculate statistics
    success_count = sum(1 for r in all_results if r.status == OperationStatus.SUCCESS)
    failure_count = sum(1 for r in all_results if r.status == OperationStatus.FAILURE)
    timeout_count = sum(1 for r in all_results if r.status == OperationStatus.TIMEOUT)
    cancelled_count = sum(1 for r in all_results if r.status == OperationStatus.CANCELLED)

    return BulkOperationReport(
        total_count=len(items),
        success_count=success_count,
        failure_count=failure_count,
        timeout_count=timeout_count,
        cancelled_count=cancelled_count,
        total_duration_ms=report.total_duration_ms,
        results=all_results
    )


async def gather_with_semaphore(
    tasks: List[Awaitable[R]],
    max_concurrency: int = 10,
    timeout: Optional[float] = None
) -> List[R]:
    """
    Execute multiple coroutines with controlled concurrency.

    Similar to asyncio.gather but with semaphore-based concurrency control.

    Args:
        tasks: List of coroutines to execute
        max_concurrency: Maximum number of concurrent operations
        timeout: Overall timeout for all operations (optional)

    Returns:
        List of results in same order as input tasks

    Example:
        tasks = [fetch_data(id) for id in ids]
        results = await gather_with_semaphore(tasks, max_concurrency=5)
    """
    semaphore = asyncio.Semaphore(max_concurrency)

    async def run_with_semaphore(task: Awaitable[R]) -> R:
        async with semaphore:
            return await task

    controlled_tasks = [run_with_semaphore(task) for task in tasks]

    if timeout:
        return await asyncio.wait_for(
            asyncio.gather(*controlled_tasks),
            timeout=timeout
        )
    else:
        return await asyncio.gather(*controlled_tasks)


class ProgressTracker:
    """
    Track progress of long-running parallel operations.

    Provides callbacks for progress updates during bulk processing.
    """

    def __init__(self, total: int, update_interval: int = 10):
        """
        Initialize progress tracker.

        Args:
            total: Total number of items to process
            update_interval: Report progress every N items (default: 10)
        """
        self.total = total
        self.completed = 0
        self.failed = 0
        self.update_interval = update_interval
        self.start_time = datetime.now()
        self.callbacks: List[Callable[[Dict[str, Any]], None]] = []

    def add_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add progress callback function"""
        self.callbacks.append(callback)

    def update(self, success: bool = True):
        """Update progress counter"""
        self.completed += 1
        if not success:
            self.failed += 1

        # Report progress at intervals
        if self.completed % self.update_interval == 0 or self.completed == self.total:
            self._report_progress()

    def _report_progress(self):
        """Report current progress to callbacks"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        progress_pct = (self.completed / self.total) * 100 if self.total > 0 else 0
        items_per_sec = self.completed / elapsed if elapsed > 0 else 0

        eta_seconds = 0
        if items_per_sec > 0 and self.completed < self.total:
            remaining = self.total - self.completed
            eta_seconds = remaining / items_per_sec

        progress_data = {
            "completed": self.completed,
            "total": self.total,
            "failed": self.failed,
            "progress_pct": progress_pct,
            "elapsed_seconds": elapsed,
            "items_per_second": items_per_sec,
            "eta_seconds": eta_seconds
        }

        logger.info(
            f"Progress: {self.completed}/{self.total} ({progress_pct:.1f}%) - "
            f"Failed: {self.failed} - "
            f"Rate: {items_per_sec:.1f} items/sec - "
            f"ETA: {eta_seconds:.0f}s"
        )

        for callback in self.callbacks:
            try:
                callback(progress_data)
            except Exception as e:
                logger.error(f"Progress callback failed: {e}")


async def parallel_map_with_progress(
    items: List[T],
    func: Callable[[T], Awaitable[R]],
    max_concurrency: int = 10,
    timeout_per_item: Optional[float] = None,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    update_interval: int = 10
) -> BulkOperationReport:
    """
    Process items in parallel with progress tracking.

    Args:
        items: List of items to process
        func: Async function to apply to each item
        max_concurrency: Maximum concurrent operations
        timeout_per_item: Timeout per operation
        progress_callback: Function to call with progress updates
        update_interval: Report progress every N items

    Returns:
        BulkOperationReport with results
    """
    tracker = ProgressTracker(total=len(items), update_interval=update_interval)

    if progress_callback:
        tracker.add_callback(progress_callback)

    # Wrap function to track progress
    async def tracked_func(item: T) -> R:
        try:
            result = await func(item)
            tracker.update(success=True)
            return result
        except Exception as e:
            tracker.update(success=False)
            raise

    return await parallel_map(
        items=items,
        func=tracked_func,
        max_concurrency=max_concurrency,
        timeout_per_item=timeout_per_item
    )
