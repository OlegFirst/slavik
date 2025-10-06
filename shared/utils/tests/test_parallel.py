"""
Unit Tests for Parallel Processing Utilities

Tests for parallel_map, batched_process, and other parallel processing functions.
"""

import pytest
import asyncio
from typing import List
from datetime import datetime

from shared.utils.parallel import (
    parallel_map,
    batched_process,
    gather_with_semaphore,
    parallel_map_with_progress,
    OperationStatus,
    BulkOperationReport,
    ProgressTracker
)


# ==================== TEST FIXTURES ====================

@pytest.fixture
def sample_data() -> List[int]:
    """Sample data for testing"""
    return list(range(1, 21))  # 1 to 20


@pytest.fixture
def large_sample_data() -> List[int]:
    """Large sample data for performance testing"""
    return list(range(1, 101))  # 1 to 100


# ==================== HELPER FUNCTIONS ====================

async def simple_async_func(x: int) -> int:
    """Simple async function that doubles input"""
    await asyncio.sleep(0.01)  # Simulate async work
    return x * 2


async def failing_async_func(x: int) -> int:
    """Async function that fails for even numbers"""
    await asyncio.sleep(0.01)
    if x % 2 == 0:
        raise ValueError(f"Cannot process even number: {x}")
    return x * 2


async def slow_async_func(x: int) -> int:
    """Slow async function for timeout testing"""
    await asyncio.sleep(2)  # 2 seconds - will timeout
    return x * 2


async def batch_process_func(batch: List[int]) -> List[int]:
    """Process a batch of items"""
    await asyncio.sleep(0.05)
    return [x * 2 for x in batch]


# ==================== PARALLEL_MAP TESTS ====================

@pytest.mark.asyncio
async def test_parallel_map_success(sample_data):
    """Test parallel_map with all successful operations"""
    report = await parallel_map(
        items=sample_data,
        func=simple_async_func,
        max_concurrency=5
    )

    assert isinstance(report, BulkOperationReport)
    assert report.total_count == len(sample_data)
    assert report.success_count == len(sample_data)
    assert report.failure_count == 0
    assert report.timeout_count == 0
    assert report.success_rate == 100.0

    # Verify results
    for result in report.results:
        assert result.status == OperationStatus.SUCCESS
        assert result.result == result.input_data * 2


@pytest.mark.asyncio
async def test_parallel_map_partial_failure(sample_data):
    """Test parallel_map with partial failures"""
    report = await parallel_map(
        items=sample_data,
        func=failing_async_func,
        max_concurrency=5,
        continue_on_error=True
    )

    assert report.total_count == len(sample_data)
    assert report.success_count == 10  # Only odd numbers succeed
    assert report.failure_count == 10  # Even numbers fail
    assert report.success_rate == 50.0

    # Verify failures
    failures = report.failures
    assert len(failures) == 10
    for failure in failures:
        assert failure.status == OperationStatus.FAILURE
        assert "Cannot process even number" in failure.error


@pytest.mark.asyncio
async def test_parallel_map_timeout():
    """Test parallel_map with timeout"""
    data = [1, 2, 3]

    report = await parallel_map(
        items=data,
        func=slow_async_func,
        max_concurrency=2,
        timeout_per_item=0.5,  # 0.5 second timeout
        continue_on_error=True
    )

    assert report.total_count == len(data)
    assert report.timeout_count == len(data)  # All should timeout

    # Verify timeout status
    for result in report.results:
        assert result.status == OperationStatus.TIMEOUT
        assert "timed out" in result.error.lower()


@pytest.mark.asyncio
async def test_parallel_map_empty_list():
    """Test parallel_map with empty input"""
    report = await parallel_map(
        items=[],
        func=simple_async_func,
        max_concurrency=5
    )

    assert report.total_count == 0
    assert report.success_count == 0
    assert report.failure_count == 0


@pytest.mark.asyncio
async def test_parallel_map_concurrency_limit(large_sample_data):
    """Test that parallel_map respects concurrency limit"""
    max_concurrent = 10

    # Track concurrent executions
    concurrent_count = 0
    max_concurrent_seen = 0
    lock = asyncio.Lock()

    async def tracked_func(x: int) -> int:
        nonlocal concurrent_count, max_concurrent_seen

        async with lock:
            concurrent_count += 1
            max_concurrent_seen = max(max_concurrent_seen, concurrent_count)

        await asyncio.sleep(0.05)

        async with lock:
            concurrent_count -= 1

        return x * 2

    report = await parallel_map(
        items=large_sample_data,
        func=tracked_func,
        max_concurrency=max_concurrent
    )

    assert report.success_count == len(large_sample_data)
    # Max concurrent should not exceed limit (allow small margin for race conditions)
    assert max_concurrent_seen <= max_concurrent + 1


# ==================== BATCHED_PROCESS TESTS ====================

@pytest.mark.asyncio
async def test_batched_process_success(sample_data):
    """Test batched_process with successful operations"""
    report = await batched_process(
        items=sample_data,
        func=batch_process_func,
        batch_size=5,
        max_concurrency=2
    )

    assert report.total_count == len(sample_data)
    assert report.success_count == len(sample_data)
    assert report.failure_count == 0

    # Verify results
    for result in report.results:
        assert result.status == OperationStatus.SUCCESS
        assert result.result == result.input_data * 2


@pytest.mark.asyncio
async def test_batched_process_batch_sizes():
    """Test batched_process creates correct number of batches"""
    data = list(range(1, 26))  # 25 items

    batches_processed = []

    async def tracking_batch_func(batch: List[int]) -> List[int]:
        batches_processed.append(len(batch))
        return [x * 2 for x in batch]

    await batched_process(
        items=data,
        func=tracking_batch_func,
        batch_size=10,
        max_concurrency=2
    )

    # Should create 3 batches: 10, 10, 5
    assert len(batches_processed) == 3
    assert batches_processed[0] == 10
    assert batches_processed[1] == 10
    assert batches_processed[2] == 5


# ==================== GATHER_WITH_SEMAPHORE TESTS ====================

@pytest.mark.asyncio
async def test_gather_with_semaphore():
    """Test gather_with_semaphore executes all tasks"""
    tasks = [simple_async_func(i) for i in range(1, 11)]

    results = await gather_with_semaphore(
        tasks=tasks,
        max_concurrency=3
    )

    assert len(results) == 10
    for i, result in enumerate(results, start=1):
        assert result == i * 2


@pytest.mark.asyncio
async def test_gather_with_semaphore_timeout():
    """Test gather_with_semaphore with timeout"""
    tasks = [slow_async_func(i) for i in range(1, 4)]

    with pytest.raises(asyncio.TimeoutError):
        await gather_with_semaphore(
            tasks=tasks,
            max_concurrency=2,
            timeout=0.5  # 0.5 second timeout
        )


# ==================== PROGRESS TRACKER TESTS ====================

def test_progress_tracker_initialization():
    """Test ProgressTracker initialization"""
    tracker = ProgressTracker(total=100, update_interval=10)

    assert tracker.total == 100
    assert tracker.completed == 0
    assert tracker.failed == 0
    assert tracker.update_interval == 10


def test_progress_tracker_update():
    """Test ProgressTracker update"""
    tracker = ProgressTracker(total=10, update_interval=5)

    # Track progress updates
    updates = []

    def callback(data):
        updates.append(data)

    tracker.add_callback(callback)

    # Update progress
    for i in range(10):
        tracker.update(success=(i % 2 == 0))

    assert tracker.completed == 10
    assert tracker.failed == 5  # Half failed

    # Should have 2 updates (at 5 and 10)
    assert len(updates) == 2

    # Check last update
    last_update = updates[-1]
    assert last_update["completed"] == 10
    assert last_update["total"] == 10
    assert last_update["failed"] == 5
    assert last_update["progress_pct"] == 100.0


@pytest.mark.asyncio
async def test_parallel_map_with_progress(sample_data):
    """Test parallel_map_with_progress tracks progress"""
    progress_updates = []

    def progress_callback(data):
        progress_updates.append(data)

    report = await parallel_map_with_progress(
        items=sample_data,
        func=simple_async_func,
        max_concurrency=5,
        progress_callback=progress_callback,
        update_interval=5
    )

    assert report.success_count == len(sample_data)

    # Should have progress updates
    assert len(progress_updates) > 0

    # Last update should show completion
    last_update = progress_updates[-1]
    assert last_update["completed"] == len(sample_data)
    assert last_update["progress_pct"] == 100.0


# ==================== BULK OPERATION REPORT TESTS ====================

def test_bulk_operation_report_properties():
    """Test BulkOperationReport computed properties"""
    from shared.utils.parallel import OperationResult

    results = [
        OperationResult(
            index=0,
            input_data=1,
            status=OperationStatus.SUCCESS,
            result=2
        ),
        OperationResult(
            index=1,
            input_data=2,
            status=OperationStatus.FAILURE,
            error="Test error"
        ),
        OperationResult(
            index=2,
            input_data=3,
            status=OperationStatus.SUCCESS,
            result=6
        )
    ]

    report = BulkOperationReport(
        total_count=3,
        success_count=2,
        failure_count=1,
        timeout_count=0,
        cancelled_count=0,
        total_duration_ms=1000.0,
        results=results
    )

    assert report.success_rate == pytest.approx(66.67, rel=0.1)
    assert len(report.successes) == 2
    assert len(report.failures) == 1

    # Check failures
    failure = report.failures[0]
    assert failure.status == OperationStatus.FAILURE
    assert failure.error == "Test error"


# ==================== PERFORMANCE TESTS ====================

@pytest.mark.asyncio
async def test_parallel_map_performance(large_sample_data):
    """Test parallel_map performance improvement over sequential"""
    start_time = datetime.now()

    report = await parallel_map(
        items=large_sample_data,
        func=simple_async_func,
        max_concurrency=10
    )

    parallel_duration = (datetime.now() - start_time).total_seconds()

    assert report.success_count == len(large_sample_data)

    # Parallel execution should be significantly faster than sequential
    # Sequential would take 100 * 0.01 = 1 second minimum
    # Parallel with concurrency=10 should take ~0.1-0.2 seconds
    assert parallel_duration < 0.5  # Should complete in under 0.5 seconds


@pytest.mark.asyncio
async def test_batched_process_performance(large_sample_data):
    """Test batched_process handles large datasets efficiently"""
    start_time = datetime.now()

    report = await batched_process(
        items=large_sample_data,
        func=batch_process_func,
        batch_size=20,
        max_concurrency=3
    )

    duration = (datetime.now() - start_time).total_seconds()

    assert report.success_count == len(large_sample_data)

    # Should complete reasonably quickly
    assert duration < 1.0  # Should complete in under 1 second
