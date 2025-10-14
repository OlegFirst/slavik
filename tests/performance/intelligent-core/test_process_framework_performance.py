"""
Performance tests for Process Framework

Tests performance characteristics including:
- Process creation throughput
- Step execution latency
- Validation performance
- Database operation performance
- Memory usage patterns
- Concurrent process handling

Run with: pytest tests/performance/intelligent-core/test_process_framework_performance.py -v
"""

import pytest
import asyncio
import time
import statistics
import psutil
import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import sys

# Add path to intelligent-core modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "intelligent-core" / "workflow_intelligence"))

from process_framework import (
    ProcessFramework,
    ProcessDefinition,
    ProcessStep,
    ProcessInstance,
    ProcessStatus,
    StepType,
    FormField,
    FieldValidation,
    ValidationRule,
    get_process_framework
)


# Test configuration
PERFORMANCE_THRESHOLDS = {
    "process_creation_time_ms": 100,  # Process creation should be < 100ms
    "step_execution_time_ms": 100,  # Step execution should be < 100ms
    "validation_time_ms": 50,  # Validation should be < 50ms
    "instance_save_time_ms": 50,  # Database save should be < 50ms
    "query_time_ms": 100,  # Database query should be < 100ms
    "max_memory_increase_mb": 100,  # Memory increase should be < 100MB
    "process_throughput_per_second": 10,  # At least 10 processes/second
}


@dataclass
class PerformanceMetrics:
    """Performance test metrics"""
    total_operations: int
    successful_operations: int
    failed_operations: int
    min_latency_ms: float
    max_latency_ms: float
    mean_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput_ops: float
    duration_seconds: float
    memory_start_mb: float
    memory_end_mb: float
    memory_delta_mb: float


class PerformanceTester:
    """Helper class for performance testing"""

    def __init__(self):
        self.latencies: List[float] = []
        self.success_count = 0
        self.failure_count = 0
        self.start_time = 0
        self.end_time = 0
        self.memory_start = 0
        self.memory_end = 0

    def start_monitoring(self):
        """Start performance monitoring"""
        self.start_time = time.time()
        process = psutil.Process(os.getpid())
        self.memory_start = process.memory_info().rss / 1024 / 1024  # MB

    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.end_time = time.time()
        process = psutil.Process(os.getpid())
        self.memory_end = process.memory_info().rss / 1024 / 1024  # MB

    def record_operation(self, latency_ms: float, success: bool):
        """Record an operation result"""
        self.latencies.append(latency_ms)
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

    def get_metrics(self) -> PerformanceMetrics:
        """Calculate performance metrics"""
        duration = self.end_time - self.start_time

        return PerformanceMetrics(
            total_operations=self.success_count + self.failure_count,
            successful_operations=self.success_count,
            failed_operations=self.failure_count,
            min_latency_ms=min(self.latencies) if self.latencies else 0,
            max_latency_ms=max(self.latencies) if self.latencies else 0,
            mean_latency_ms=statistics.mean(self.latencies) if self.latencies else 0,
            median_latency_ms=statistics.median(self.latencies) if self.latencies else 0,
            p95_latency_ms=self._percentile(self.latencies, 95) if self.latencies else 0,
            p99_latency_ms=self._percentile(self.latencies, 99) if self.latencies else 0,
            throughput_ops=self.success_count / duration if duration > 0 else 0,
            duration_seconds=duration,
            memory_start_mb=self.memory_start,
            memory_end_mb=self.memory_end,
            memory_delta_mb=self.memory_end - self.memory_start
        )

    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * (percentile / 100))
        return sorted_data[min(index, len(sorted_data) - 1)]


# Test fixtures

@pytest.fixture
def temp_processes_dir():
    """Create temporary directory for process definitions"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def process_framework(temp_processes_dir):
    """Create ProcessFramework instance"""
    return ProcessFramework(temp_processes_dir)


@pytest.fixture
def sample_process_definition():
    """Create a sample process definition for testing"""
    process = ProcessDefinition(
        id="test_process",
        name="Test Process",
        version="1.0",
        description="Test process for performance testing",
        category="testing",
        created_at=datetime.now()
    )

    # Add start step
    start_step = ProcessStep(
        id="start",
        name="Start Step",
        step_type=StepType.FORM_INPUT,
        description="Initial data collection",
        form_fields=[
            FormField(
                name="organization",
                label="Organization Name",
                field_type="text",
                required=True,
                validations=[
                    FieldValidation(
                        rule=ValidationRule.REQUIRED,
                        value=True,
                        error_message="Organization is required"
                    )
                ]
            ),
            FormField(
                name="email",
                label="Email",
                field_type="email",
                required=True,
                validations=[
                    FieldValidation(
                        rule=ValidationRule.PATTERN,
                        value=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
                        error_message="Invalid email format"
                    )
                ]
            )
        ],
        next_steps=["analysis"]
    )

    # Add analysis step
    analysis_step = ProcessStep(
        id="analysis",
        name="Analysis Step",
        step_type=StepType.ANALYSIS,
        description="Perform analysis",
        form_fields=[
            FormField(
                name="analysis_results",
                label="Analysis Results",
                field_type="textarea",
                required=True
            )
        ],
        next_steps=["end"]
    )

    # Add end step
    end_step = ProcessStep(
        id="end",
        name="End Step",
        step_type=StepType.VALIDATION,
        description="Process completion",
        form_fields=[]
    )

    process.add_step(start_step)
    process.add_step(analysis_step)
    process.add_step(end_step)

    process.start_step_id = "start"
    process.end_step_ids = ["end"]

    return process


# Performance Tests

@pytest.mark.performance
class TestProcessThroughput:
    """Test Process Framework throughput"""

    def test_process_creation_throughput(self, process_framework, sample_process_definition):
        """Test creating 100 processes in less than 10 seconds"""
        tester = PerformanceTester()
        tester.start_monitoring()

        num_processes = 100

        # Register the base process
        process_framework.register_process(sample_process_definition)

        # Create instances
        for i in range(num_processes):
            start = time.time()
            try:
                instance = process_framework.start_process(
                    process_id="test_process",
                    started_by=f"user_{i}",
                    initial_data={"test": f"data_{i}"}
                )
                latency_ms = (time.time() - start) * 1000
                success = instance is not None
                tester.record_operation(latency_ms, success)
            except Exception as e:
                latency_ms = (time.time() - start) * 1000
                tester.record_operation(latency_ms, False)

        tester.stop_monitoring()
        metrics = tester.get_metrics()

        # Print metrics
        print(f"\n=== Process Creation Throughput Test ===")
        print(f"Total Processes: {metrics.total_operations}")
        print(f"Successful: {metrics.successful_operations}")
        print(f"Failed: {metrics.failed_operations}")
        print(f"Throughput: {metrics.throughput_ops:.2f} processes/s")
        print(f"Mean Latency: {metrics.mean_latency_ms:.2f} ms")
        print(f"P95 Latency: {metrics.p95_latency_ms:.2f} ms")
        print(f"P99 Latency: {metrics.p99_latency_ms:.2f} ms")
        print(f"Memory Delta: {metrics.memory_delta_mb:.2f} MB")
        print(f"Duration: {metrics.duration_seconds:.2f} seconds")

        # Assertions
        assert metrics.successful_operations == num_processes, "All process creations should succeed"
        assert metrics.duration_seconds < 10, "Should create 100 processes in less than 10 seconds"
        assert metrics.mean_latency_ms < PERFORMANCE_THRESHOLDS["process_creation_time_ms"], \
            f"Mean latency {metrics.mean_latency_ms:.2f}ms exceeds threshold {PERFORMANCE_THRESHOLDS['process_creation_time_ms']}ms"
        assert metrics.throughput_ops >= PERFORMANCE_THRESHOLDS["process_throughput_per_second"], \
            f"Throughput {metrics.throughput_ops:.2f} ops/s is below threshold {PERFORMANCE_THRESHOLDS['process_throughput_per_second']} ops/s"

    @pytest.mark.asyncio
    async def test_concurrent_process_execution(self, process_framework, sample_process_definition):
        """Test executing 10 concurrent processes"""
        tester = PerformanceTester()
        tester.start_monitoring()

        # Register process
        process_framework.register_process(sample_process_definition)

        num_concurrent = 10
        instances = []

        # Create instances
        for i in range(num_concurrent):
            instance = process_framework.start_process(
                process_id="test_process",
                started_by=f"user_{i}",
                initial_data={"test": f"data_{i}"}
            )
            instances.append(instance)

        # Execute first step concurrently
        async def execute_step(instance):
            start = time.time()
            try:
                success, error, next_step = process_framework.execute_step(
                    instance_id=instance.id,
                    step_data={
                        "organization": "Test Org",
                        "email": "test@example.com"
                    },
                    executed_by="test_user"
                )
                latency_ms = (time.time() - start) * 1000
                tester.record_operation(latency_ms, success)
            except Exception as e:
                latency_ms = (time.time() - start) * 1000
                tester.record_operation(latency_ms, False)

        # Execute concurrently
        await asyncio.gather(*[execute_step(inst) for inst in instances])

        tester.stop_monitoring()
        metrics = tester.get_metrics()

        # Print metrics
        print(f"\n=== Concurrent Process Execution Test ===")
        print(f"Concurrent Processes: {num_concurrent}")
        print(f"Successful: {metrics.successful_operations}")
        print(f"Failed: {metrics.failed_operations}")
        print(f"Mean Latency: {metrics.mean_latency_ms:.2f} ms")
        print(f"P95 Latency: {metrics.p95_latency_ms:.2f} ms")
        print(f"P99 Latency: {metrics.p99_latency_ms:.2f} ms")

        # Assertions
        assert metrics.successful_operations == num_concurrent, "All concurrent executions should succeed"
        assert metrics.mean_latency_ms < PERFORMANCE_THRESHOLDS["step_execution_time_ms"], \
            f"Mean latency {metrics.mean_latency_ms:.2f}ms exceeds threshold"


@pytest.mark.performance
class TestStepExecutionLatency:
    """Test step execution latency"""

    def test_single_step_latency(self, process_framework, sample_process_definition):
        """Test that single step execution averages less than 100ms"""
        tester = PerformanceTester()
        tester.start_monitoring()

        # Register process
        process_framework.register_process(sample_process_definition)

        num_iterations = 50

        for i in range(num_iterations):
            # Create instance
            instance = process_framework.start_process(
                process_id="test_process",
                started_by="test_user",
                initial_data={}
            )

            # Execute step
            start = time.time()
            try:
                success, error, next_step = process_framework.execute_step(
                    instance_id=instance.id,
                    step_data={
                        "organization": f"Test Org {i}",
                        "email": f"test{i}@example.com"
                    },
                    executed_by="test_user"
                )
                latency_ms = (time.time() - start) * 1000
                tester.record_operation(latency_ms, success)
            except Exception as e:
                latency_ms = (time.time() - start) * 1000
                tester.record_operation(latency_ms, False)

        tester.stop_monitoring()
        metrics = tester.get_metrics()

        # Print metrics
        print(f"\n=== Single Step Latency Test ===")
        print(f"Iterations: {num_iterations}")
        print(f"Min Latency: {metrics.min_latency_ms:.2f} ms")
        print(f"Max Latency: {metrics.max_latency_ms:.2f} ms")
        print(f"Mean Latency: {metrics.mean_latency_ms:.2f} ms")
        print(f"Median Latency: {metrics.median_latency_ms:.2f} ms")
        print(f"P95 Latency: {metrics.p95_latency_ms:.2f} ms")
        print(f"P99 Latency: {metrics.p99_latency_ms:.2f} ms")

        # Assertions
        assert metrics.mean_latency_ms < PERFORMANCE_THRESHOLDS["step_execution_time_ms"], \
            f"Mean step latency {metrics.mean_latency_ms:.2f}ms exceeds threshold {PERFORMANCE_THRESHOLDS['step_execution_time_ms']}ms"
        assert metrics.p95_latency_ms < PERFORMANCE_THRESHOLDS["step_execution_time_ms"] * 1.5, \
            "P95 latency should be within 1.5x of threshold"

    def test_validation_latency(self, sample_process_definition):
        """Test that validation takes less than 50ms on average"""
        tester = PerformanceTester()
        tester.start_monitoring()

        num_iterations = 100
        start_step = sample_process_definition.get_step("start")

        test_data = {
            "organization": "Test Organization",
            "email": "test@example.com"
        }

        for i in range(num_iterations):
            start = time.time()
            try:
                is_valid, errors = start_step.validate_input(test_data)
                latency_ms = (time.time() - start) * 1000
                tester.record_operation(latency_ms, is_valid)
            except Exception as e:
                latency_ms = (time.time() - start) * 1000
                tester.record_operation(latency_ms, False)

        tester.stop_monitoring()
        metrics = tester.get_metrics()

        # Print metrics
        print(f"\n=== Validation Latency Test ===")
        print(f"Iterations: {num_iterations}")
        print(f"Min Latency: {metrics.min_latency_ms:.4f} ms")
        print(f"Max Latency: {metrics.max_latency_ms:.4f} ms")
        print(f"Mean Latency: {metrics.mean_latency_ms:.4f} ms")
        print(f"P95 Latency: {metrics.p95_latency_ms:.4f} ms")
        print(f"P99 Latency: {metrics.p99_latency_ms:.4f} ms")

        # Assertions
        assert metrics.mean_latency_ms < PERFORMANCE_THRESHOLDS["validation_time_ms"], \
            f"Mean validation latency {metrics.mean_latency_ms:.2f}ms exceeds threshold {PERFORMANCE_THRESHOLDS['validation_time_ms']}ms"


@pytest.mark.performance
class TestDatabaseOperations:
    """Test database operation performance"""

    def test_instance_save_performance(self, process_framework, sample_process_definition):
        """Test that instance save operations take less than 50ms"""
        tester = PerformanceTester()
        tester.start_monitoring()

        # Register process
        process_framework.register_process(sample_process_definition)

        num_iterations = 100

        for i in range(num_iterations):
            start = time.time()
            try:
                # Create and save instance
                instance = process_framework.start_process(
                    process_id="test_process",
                    started_by=f"user_{i}",
                    initial_data={"iteration": i}
                )

                # Update instance data (simulating save)
                instance.update_data({"additional_field": f"value_{i}"})

                latency_ms = (time.time() - start) * 1000
                success = instance is not None
                tester.record_operation(latency_ms, success)
            except Exception as e:
                latency_ms = (time.time() - start) * 1000
                tester.record_operation(latency_ms, False)

        tester.stop_monitoring()
        metrics = tester.get_metrics()

        # Print metrics
        print(f"\n=== Instance Save Performance Test ===")
        print(f"Iterations: {num_iterations}")
        print(f"Mean Latency: {metrics.mean_latency_ms:.2f} ms")
        print(f"P95 Latency: {metrics.p95_latency_ms:.2f} ms")
        print(f"P99 Latency: {metrics.p99_latency_ms:.2f} ms")
        print(f"Throughput: {metrics.throughput_ops:.2f} ops/s")

        # Assertions
        assert metrics.mean_latency_ms < PERFORMANCE_THRESHOLDS["instance_save_time_ms"], \
            f"Mean save latency {metrics.mean_latency_ms:.2f}ms exceeds threshold {PERFORMANCE_THRESHOLDS['instance_save_time_ms']}ms"

    def test_query_performance(self, process_framework, sample_process_definition):
        """Test that query operations take less than 100ms"""
        tester = PerformanceTester()

        # Register process and create instances
        process_framework.register_process(sample_process_definition)

        # Create 50 instances
        instances = []
        for i in range(50):
            instance = process_framework.start_process(
                process_id="test_process",
                started_by=f"user_{i}",
                initial_data={"test": f"data_{i}"}
            )
            instances.append(instance)

        tester.start_monitoring()

        # Query instances
        num_queries = 100
        for i in range(num_queries):
            start = time.time()
            try:
                # Query instance
                instance_id = instances[i % len(instances)].id
                queried_instance = process_framework.instances.get(instance_id)

                # Get process status
                status = process_framework.get_process_status(instance_id)

                latency_ms = (time.time() - start) * 1000
                success = queried_instance is not None and status is not None
                tester.record_operation(latency_ms, success)
            except Exception as e:
                latency_ms = (time.time() - start) * 1000
                tester.record_operation(latency_ms, False)

        tester.stop_monitoring()
        metrics = tester.get_metrics()

        # Print metrics
        print(f"\n=== Query Performance Test ===")
        print(f"Queries: {num_queries}")
        print(f"Mean Latency: {metrics.mean_latency_ms:.2f} ms")
        print(f"P95 Latency: {metrics.p95_latency_ms:.2f} ms")
        print(f"P99 Latency: {metrics.p99_latency_ms:.2f} ms")
        print(f"Throughput: {metrics.throughput_ops:.2f} queries/s")

        # Assertions
        assert metrics.mean_latency_ms < PERFORMANCE_THRESHOLDS["query_time_ms"], \
            f"Mean query latency {metrics.mean_latency_ms:.2f}ms exceeds threshold {PERFORMANCE_THRESHOLDS['query_time_ms']}ms"


@pytest.mark.performance
class TestMemoryUsage:
    """Test memory usage patterns"""

    def test_memory_growth_under_load(self, process_framework, sample_process_definition):
        """Test that memory growth is less than 100MB under load"""
        process = psutil.Process(os.getpid())
        memory_start = process.memory_info().rss / 1024 / 1024  # MB

        # Register process
        process_framework.register_process(sample_process_definition)

        # Create many instances
        num_instances = 500
        instances = []

        for i in range(num_instances):
            instance = process_framework.start_process(
                process_id="test_process",
                started_by=f"user_{i}",
                initial_data={
                    "test_data": f"data_{i}",
                    "large_field": "x" * 1000  # 1KB of data
                }
            )
            instances.append(instance)

            # Execute step
            if i % 2 == 0:  # Execute half of them
                try:
                    process_framework.execute_step(
                        instance_id=instance.id,
                        step_data={
                            "organization": f"Org {i}",
                            "email": f"test{i}@example.com"
                        },
                        executed_by="test_user"
                    )
                except Exception:
                    pass

        memory_end = process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = memory_end - memory_start

        print(f"\n=== Memory Growth Under Load Test ===")
        print(f"Instances Created: {num_instances}")
        print(f"Memory Start: {memory_start:.2f} MB")
        print(f"Memory End: {memory_end:.2f} MB")
        print(f"Memory Delta: {memory_delta:.2f} MB")
        print(f"Memory per Instance: {memory_delta / num_instances:.4f} MB")

        # Assertions
        assert memory_delta < PERFORMANCE_THRESHOLDS["max_memory_increase_mb"], \
            f"Memory increase {memory_delta:.2f}MB exceeds threshold {PERFORMANCE_THRESHOLDS['max_memory_increase_mb']}MB"

    def test_process_memory_cleanup(self, process_framework, sample_process_definition):
        """Test memory cleanup after process completion"""
        process = psutil.Process(os.getpid())

        # Register process
        process_framework.register_process(sample_process_definition)

        # Initial memory
        memory_samples = []
        memory_samples.append(process.memory_info().rss / 1024 / 1024)

        # Create and complete processes
        num_cycles = 10
        for cycle in range(num_cycles):
            # Create instances
            instances = []
            for i in range(50):
                instance = process_framework.start_process(
                    process_id="test_process",
                    started_by=f"user_{i}",
                    initial_data={"cycle": cycle, "iteration": i}
                )
                instances.append(instance)

            # Complete processes
            for instance in instances:
                try:
                    # Execute all steps to completion
                    process_framework.execute_step(
                        instance_id=instance.id,
                        step_data={
                            "organization": "Test Org",
                            "email": "test@example.com"
                        },
                        executed_by="test_user"
                    )
                except Exception:
                    pass

            # Sample memory after each cycle
            memory_samples.append(process.memory_info().rss / 1024 / 1024)

        # Calculate memory growth trend
        memory_start = memory_samples[0]
        memory_end = memory_samples[-1]
        memory_growth = memory_end - memory_start

        print(f"\n=== Memory Cleanup Test ===")
        print(f"Cycles: {num_cycles}")
        print(f"Memory Start: {memory_start:.2f} MB")
        print(f"Memory End: {memory_end:.2f} MB")
        print(f"Total Growth: {memory_growth:.2f} MB")
        print(f"Memory Samples: {[f'{m:.2f}' for m in memory_samples]}")

        # Memory should not grow significantly over cycles
        assert memory_growth < PERFORMANCE_THRESHOLDS["max_memory_increase_mb"], \
            f"Memory growth {memory_growth:.2f}MB over {num_cycles} cycles exceeds threshold"


@pytest.mark.performance
@pytest.mark.slow
class TestStressScenarios:
    """Stress test scenarios"""

    def test_large_scale_process_execution(self, process_framework, sample_process_definition):
        """Test executing 1000 processes end-to-end"""
        tester = PerformanceTester()
        tester.start_monitoring()

        # Register process
        process_framework.register_process(sample_process_definition)

        num_processes = 1000
        completed = 0
        failed = 0

        for i in range(num_processes):
            start = time.time()
            try:
                # Create instance
                instance = process_framework.start_process(
                    process_id="test_process",
                    started_by=f"user_{i}",
                    initial_data={"test": f"data_{i}"}
                )

                # Execute first step
                success, error, next_step = process_framework.execute_step(
                    instance_id=instance.id,
                    step_data={
                        "organization": f"Org {i}",
                        "email": f"test{i}@example.com"
                    },
                    executed_by="test_user"
                )

                latency_ms = (time.time() - start) * 1000

                if success:
                    completed += 1
                    tester.record_operation(latency_ms, True)
                else:
                    failed += 1
                    tester.record_operation(latency_ms, False)

            except Exception as e:
                latency_ms = (time.time() - start) * 1000
                failed += 1
                tester.record_operation(latency_ms, False)

            # Progress indicator
            if (i + 1) % 100 == 0:
                print(f"Progress: {i + 1}/{num_processes} processes")

        tester.stop_monitoring()
        metrics = tester.get_metrics()

        print(f"\n=== Large Scale Process Execution Test ===")
        print(f"Total Processes: {num_processes}")
        print(f"Completed: {completed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {completed / num_processes * 100:.2f}%")
        print(f"Total Duration: {metrics.duration_seconds:.2f} seconds")
        print(f"Throughput: {metrics.throughput_ops:.2f} processes/s")
        print(f"Mean Latency: {metrics.mean_latency_ms:.2f} ms")
        print(f"P95 Latency: {metrics.p95_latency_ms:.2f} ms")
        print(f"P99 Latency: {metrics.p99_latency_ms:.2f} ms")
        print(f"Memory Delta: {metrics.memory_delta_mb:.2f} MB")

        # Assertions
        assert completed >= num_processes * 0.95, "At least 95% success rate required"
        assert metrics.memory_delta_mb < PERFORMANCE_THRESHOLDS["max_memory_increase_mb"] * 2, \
            "Memory growth should be reasonable even under stress"

    @pytest.mark.asyncio
    async def test_high_concurrency_stress(self, process_framework, sample_process_definition):
        """Test high concurrency with 100 concurrent processes"""
        tester = PerformanceTester()
        tester.start_monitoring()

        # Register process
        process_framework.register_process(sample_process_definition)

        num_concurrent = 100

        async def execute_full_process(process_id: str):
            start = time.time()
            try:
                # Create instance
                instance = process_framework.start_process(
                    process_id="test_process",
                    started_by=f"user_{process_id}",
                    initial_data={"test": process_id}
                )

                # Execute step
                success, error, next_step = process_framework.execute_step(
                    instance_id=instance.id,
                    step_data={
                        "organization": f"Org {process_id}",
                        "email": f"test{process_id}@example.com"
                    },
                    executed_by="test_user"
                )

                latency_ms = (time.time() - start) * 1000
                tester.record_operation(latency_ms, success)

            except Exception as e:
                latency_ms = (time.time() - start) * 1000
                tester.record_operation(latency_ms, False)

        # Execute concurrently
        tasks = [execute_full_process(f"proc_{i}") for i in range(num_concurrent)]
        await asyncio.gather(*tasks)

        tester.stop_monitoring()
        metrics = tester.get_metrics()

        print(f"\n=== High Concurrency Stress Test ===")
        print(f"Concurrent Processes: {num_concurrent}")
        print(f"Successful: {metrics.successful_operations}")
        print(f"Failed: {metrics.failed_operations}")
        print(f"Success Rate: {metrics.successful_operations / num_concurrent * 100:.2f}%")
        print(f"Duration: {metrics.duration_seconds:.2f} seconds")
        print(f"Mean Latency: {metrics.mean_latency_ms:.2f} ms")
        print(f"P95 Latency: {metrics.p95_latency_ms:.2f} ms")
        print(f"P99 Latency: {metrics.p99_latency_ms:.2f} ms")

        # Assertions
        assert metrics.successful_operations >= num_concurrent * 0.90, \
            "At least 90% success rate required under high concurrency"


if __name__ == "__main__":
    # Run pytest tests
    pytest.main([__file__, "-v", "-m", "performance"])
