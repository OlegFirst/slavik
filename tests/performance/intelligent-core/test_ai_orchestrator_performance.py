"""
Performance tests for AI Orchestrator

Tests performance characteristics including:
- Throughput (requests per second)
- Latency (response times)
- Resource utilization
- Concurrent request handling
- Memory usage patterns
- Decision-making performance

Run with: pytest tests/performance/intelligent-core/test_ai_orchestrator_performance.py -v
Or use locust for load testing: locust -f test_ai_orchestrator_performance.py
"""

import pytest
import asyncio
import time
import statistics
import psutil
import os
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import httpx

# Locust imports (optional - for load testing)
try:
    from locust import HttpUser, task, between, events
    LOCUST_AVAILABLE = True
except ImportError:
    LOCUST_AVAILABLE = False


# Test configuration
ORCHESTRATOR_URL = "http://localhost:8000"
PERFORMANCE_THRESHOLDS = {
    "max_response_time_ms": 5000,  # 5 seconds
    "min_throughput_rps": 10,  # 10 requests per second
    "max_memory_increase_mb": 500,  # 500 MB
    "max_cpu_percent": 80,  # 80% CPU
}


@dataclass
class PerformanceMetrics:
    """Performance test metrics"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    min_latency_ms: float
    max_latency_ms: float
    mean_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput_rps: float
    duration_seconds: float
    memory_start_mb: float
    memory_end_mb: float
    memory_delta_mb: float
    cpu_avg_percent: float


class PerformanceTester:
    """Helper class for performance testing"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.latencies: List[float] = []
        self.success_count = 0
        self.failure_count = 0
        self.start_time = 0
        self.end_time = 0
        self.memory_start = 0
        self.memory_end = 0
        self.cpu_samples: List[float] = []

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

    def record_request(self, latency_ms: float, success: bool):
        """Record a request result"""
        self.latencies.append(latency_ms)
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

    def sample_cpu(self):
        """Sample CPU usage"""
        self.cpu_samples.append(psutil.cpu_percent(interval=0.1))

    def get_metrics(self) -> PerformanceMetrics:
        """Calculate performance metrics"""
        duration = self.end_time - self.start_time

        return PerformanceMetrics(
            total_requests=self.success_count + self.failure_count,
            successful_requests=self.success_count,
            failed_requests=self.failure_count,
            min_latency_ms=min(self.latencies) if self.latencies else 0,
            max_latency_ms=max(self.latencies) if self.latencies else 0,
            mean_latency_ms=statistics.mean(self.latencies) if self.latencies else 0,
            median_latency_ms=statistics.median(self.latencies) if self.latencies else 0,
            p95_latency_ms=self._percentile(self.latencies, 95) if self.latencies else 0,
            p99_latency_ms=self._percentile(self.latencies, 99) if self.latencies else 0,
            throughput_rps=self.success_count / duration if duration > 0 else 0,
            duration_seconds=duration,
            memory_start_mb=self.memory_start,
            memory_end_mb=self.memory_end,
            memory_delta_mb=self.memory_end - self.memory_start,
            cpu_avg_percent=statistics.mean(self.cpu_samples) if self.cpu_samples else 0
        )

    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * (percentile / 100))
        return sorted_data[min(index, len(sorted_data) - 1)]


@pytest.mark.performance
class TestOrchestratorThroughput:
    """Test AI Orchestrator throughput"""

    @pytest.mark.asyncio
    async def test_sequential_request_throughput(self):
        """Test sequential request handling"""
        tester = PerformanceTester(ORCHESTRATOR_URL)
        tester.start_monitoring()

        num_requests = 100
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i in range(num_requests):
                request_data = {
                    "task_id": f"perf_test_{i}",
                    "task_type": "analysis",
                    "priority": "normal"
                }

                start = time.time()
                try:
                    response = await client.post(
                        f"{ORCHESTRATOR_URL}/orchestrate",
                        json=request_data
                    )
                    latency_ms = (time.time() - start) * 1000
                    success = response.status_code in [200, 201]
                    tester.record_request(latency_ms, success)
                except Exception:
                    latency_ms = (time.time() - start) * 1000
                    tester.record_request(latency_ms, False)

                # Sample CPU periodically
                if i % 10 == 0:
                    tester.sample_cpu()

        tester.stop_monitoring()
        metrics = tester.get_metrics()

        # Print metrics
        print(f"\n=== Sequential Throughput Test ===")
        print(f"Total Requests: {metrics.total_requests}")
        print(f"Successful: {metrics.successful_requests}")
        print(f"Failed: {metrics.failed_requests}")
        print(f"Throughput: {metrics.throughput_rps:.2f} req/s")
        print(f"Mean Latency: {metrics.mean_latency_ms:.2f} ms")
        print(f"P95 Latency: {metrics.p95_latency_ms:.2f} ms")
        print(f"P99 Latency: {metrics.p99_latency_ms:.2f} ms")
        print(f"Memory Delta: {metrics.memory_delta_mb:.2f} MB")
        print(f"CPU Average: {metrics.cpu_avg_percent:.2f}%")

        # Assertions
        assert metrics.successful_requests >= num_requests * 0.95  # 95% success rate
        assert metrics.throughput_rps >= PERFORMANCE_THRESHOLDS["min_throughput_rps"]
        assert metrics.p95_latency_ms <= PERFORMANCE_THRESHOLDS["max_response_time_ms"]

    @pytest.mark.asyncio
    async def test_concurrent_request_throughput(self):
        """Test concurrent request handling"""
        tester = PerformanceTester(ORCHESTRATOR_URL)
        tester.start_monitoring()

        num_concurrent = 50
        async with httpx.AsyncClient(timeout=30.0) as client:

            async def make_request(request_id: int):
                request_data = {
                    "task_id": f"concurrent_test_{request_id}",
                    "task_type": "analysis",
                    "priority": "normal"
                }

                start = time.time()
                try:
                    response = await client.post(
                        f"{ORCHESTRATOR_URL}/orchestrate",
                        json=request_data
                    )
                    latency_ms = (time.time() - start) * 1000
                    success = response.status_code in [200, 201]
                    tester.record_request(latency_ms, success)
                except Exception:
                    latency_ms = (time.time() - start) * 1000
                    tester.record_request(latency_ms, False)

            # Execute concurrently
            tasks = [make_request(i) for i in range(num_concurrent)]
            await asyncio.gather(*tasks)

        tester.stop_monitoring()
        metrics = tester.get_metrics()

        # Print metrics
        print(f"\n=== Concurrent Throughput Test ===")
        print(f"Concurrent Requests: {num_concurrent}")
        print(f"Successful: {metrics.successful_requests}")
        print(f"Failed: {metrics.failed_requests}")
        print(f"Throughput: {metrics.throughput_rps:.2f} req/s")
        print(f"Mean Latency: {metrics.mean_latency_ms:.2f} ms")
        print(f"P95 Latency: {metrics.p95_latency_ms:.2f} ms")
        print(f"P99 Latency: {metrics.p99_latency_ms:.2f} ms")

        # Assertions
        assert metrics.successful_requests >= num_concurrent * 0.9  # 90% success rate
        assert metrics.p95_latency_ms <= PERFORMANCE_THRESHOLDS["max_response_time_ms"]


@pytest.mark.performance
class TestOrchestratorLatency:
    """Test AI Orchestrator response times"""

    @pytest.mark.asyncio
    async def test_decision_making_latency(self):
        """Test decision-making latency"""
        latencies = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            for i in range(50):
                request_data = {
                    "task_id": f"latency_test_{i}",
                    "task_type": "decision",
                    "priority": "high"
                }

                start = time.time()
                try:
                    response = await client.post(
                        f"{ORCHESTRATOR_URL}/orchestrate",
                        json=request_data
                    )
                    if response.status_code in [200, 201]:
                        latency_ms = (time.time() - start) * 1000
                        latencies.append(latency_ms)
                except Exception:
                    pass

        if latencies:
            mean_latency = statistics.mean(latencies)
            p95_latency = PerformanceTester._percentile(latencies, 95)
            p99_latency = PerformanceTester._percentile(latencies, 99)

            print(f"\n=== Decision Latency Test ===")
            print(f"Mean Latency: {mean_latency:.2f} ms")
            print(f"P95 Latency: {p95_latency:.2f} ms")
            print(f"P99 Latency: {p99_latency:.2f} ms")

            # Assertions
            assert mean_latency <= PERFORMANCE_THRESHOLDS["max_response_time_ms"]
            assert p99_latency <= PERFORMANCE_THRESHOLDS["max_response_time_ms"] * 1.5

    @pytest.mark.asyncio
    async def test_health_check_latency(self):
        """Test health check endpoint latency"""
        latencies = []

        async with httpx.AsyncClient(timeout=5.0) as client:
            for _ in range(100):
                start = time.time()
                try:
                    response = await client.get(f"{ORCHESTRATOR_URL}/health")
                    if response.status_code == 200:
                        latency_ms = (time.time() - start) * 1000
                        latencies.append(latency_ms)
                except Exception:
                    pass

        if latencies:
            mean_latency = statistics.mean(latencies)
            max_latency = max(latencies)

            print(f"\n=== Health Check Latency ===")
            print(f"Mean: {mean_latency:.2f} ms")
            print(f"Max: {max_latency:.2f} ms")

            # Health checks should be very fast
            assert mean_latency <= 100  # 100ms
            assert max_latency <= 500  # 500ms


@pytest.mark.performance
class TestOrchestratorMemory:
    """Test AI Orchestrator memory usage"""

    @pytest.mark.asyncio
    async def test_memory_growth_under_load(self):
        """Test memory growth under sustained load"""
        process = psutil.Process(os.getpid())
        memory_start = process.memory_info().rss / 1024 / 1024  # MB

        # Sustained load
        num_requests = 500
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i in range(num_requests):
                request_data = {
                    "task_id": f"memory_test_{i}",
                    "task_type": "analysis"
                }

                try:
                    await client.post(
                        f"{ORCHESTRATOR_URL}/orchestrate",
                        json=request_data
                    )
                except Exception:
                    pass

                # Small delay to avoid overwhelming
                if i % 50 == 0:
                    await asyncio.sleep(0.1)

        memory_end = process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = memory_end - memory_start

        print(f"\n=== Memory Growth Test ===")
        print(f"Memory Start: {memory_start:.2f} MB")
        print(f"Memory End: {memory_end:.2f} MB")
        print(f"Memory Delta: {memory_delta:.2f} MB")
        print(f"Requests: {num_requests}")

        # Memory should not grow excessively
        assert memory_delta <= PERFORMANCE_THRESHOLDS["max_memory_increase_mb"]

    @pytest.mark.asyncio
    async def test_memory_stability(self):
        """Test memory stability over time"""
        process = psutil.Process(os.getpid())
        memory_samples = []

        # Take samples over time
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i in range(10):
                # Make some requests
                for j in range(10):
                    try:
                        await client.post(
                            f"{ORCHESTRATOR_URL}/orchestrate",
                            json={"task_id": f"stability_{i}_{j}"}
                        )
                    except Exception:
                        pass

                # Sample memory
                memory_mb = process.memory_info().rss / 1024 / 1024
                memory_samples.append(memory_mb)
                await asyncio.sleep(0.5)

        # Calculate memory variance
        if len(memory_samples) > 1:
            memory_variance = statistics.variance(memory_samples)
            print(f"\n=== Memory Stability Test ===")
            print(f"Samples: {len(memory_samples)}")
            print(f"Mean: {statistics.mean(memory_samples):.2f} MB")
            print(f"Variance: {memory_variance:.2f}")

            # Variance should be low (stable memory)
            assert memory_variance <= 1000  # Low variance


@pytest.mark.performance
class TestOrchestratorCPU:
    """Test AI Orchestrator CPU usage"""

    @pytest.mark.asyncio
    async def test_cpu_usage_under_load(self):
        """Test CPU usage under load"""
        cpu_samples = []

        # Generate load while monitoring CPU
        async with httpx.AsyncClient(timeout=30.0) as client:

            async def monitor_cpu():
                for _ in range(20):
                    cpu_samples.append(psutil.cpu_percent(interval=0.1))
                    await asyncio.sleep(0.5)

            async def generate_load():
                for i in range(100):
                    try:
                        await client.post(
                            f"{ORCHESTRATOR_URL}/orchestrate",
                            json={"task_id": f"cpu_test_{i}"}
                        )
                    except Exception:
                        pass

            # Run concurrently
            await asyncio.gather(monitor_cpu(), generate_load())

        if cpu_samples:
            cpu_avg = statistics.mean(cpu_samples)
            cpu_max = max(cpu_samples)

            print(f"\n=== CPU Usage Test ===")
            print(f"Average CPU: {cpu_avg:.2f}%")
            print(f"Max CPU: {cpu_max:.2f}%")

            # CPU should not be consistently maxed out
            assert cpu_avg <= PERFORMANCE_THRESHOLDS["max_cpu_percent"]


@pytest.mark.performance
@pytest.mark.slow
class TestOrchestratorStress:
    """Stress tests for AI Orchestrator"""

    @pytest.mark.asyncio
    async def test_sustained_high_load(self):
        """Test sustained high load"""
        tester = PerformanceTester(ORCHESTRATOR_URL)
        tester.start_monitoring()

        duration_seconds = 60  # 1 minute
        end_time = time.time() + duration_seconds

        async with httpx.AsyncClient(timeout=30.0) as client:
            request_counter = 0

            while time.time() < end_time:
                request_data = {
                    "task_id": f"stress_test_{request_counter}",
                    "task_type": "analysis"
                }

                start = time.time()
                try:
                    response = await client.post(
                        f"{ORCHESTRATOR_URL}/orchestrate",
                        json=request_data
                    )
                    latency_ms = (time.time() - start) * 1000
                    success = response.status_code in [200, 201]
                    tester.record_request(latency_ms, success)
                except Exception:
                    latency_ms = (time.time() - start) * 1000
                    tester.record_request(latency_ms, False)

                request_counter += 1

                # Sample CPU periodically
                if request_counter % 50 == 0:
                    tester.sample_cpu()

                await asyncio.sleep(0.01)  # Small delay

        tester.stop_monitoring()
        metrics = tester.get_metrics()

        print(f"\n=== Sustained Load Test ===")
        print(f"Duration: {metrics.duration_seconds:.2f} seconds")
        print(f"Total Requests: {metrics.total_requests}")
        print(f"Throughput: {metrics.throughput_rps:.2f} req/s")
        print(f"Success Rate: {metrics.successful_requests / metrics.total_requests * 100:.2f}%")
        print(f"Mean Latency: {metrics.mean_latency_ms:.2f} ms")
        print(f"P95 Latency: {metrics.p95_latency_ms:.2f} ms")

        # System should remain stable under sustained load
        assert metrics.successful_requests / metrics.total_requests >= 0.95  # 95% success


# Locust Load Testing (optional)

if LOCUST_AVAILABLE:
    class OrchestratorUser(HttpUser):
        """Locust user for load testing"""
        wait_time = between(1, 3)
        host = ORCHESTRATOR_URL

        @task(3)
        def orchestrate_analysis(self):
            """Orchestrate analysis task"""
            self.client.post("/orchestrate", json={
                "task_id": f"locust_{time.time()}",
                "task_type": "analysis",
                "priority": "normal"
            })

        @task(2)
        def orchestrate_decision(self):
            """Orchestrate decision task"""
            self.client.post("/orchestrate", json={
                "task_id": f"locust_decision_{time.time()}",
                "task_type": "decision",
                "priority": "high"
            })

        @task(1)
        def health_check(self):
            """Check health"""
            self.client.get("/health")


# Pytest fixtures

@pytest.fixture(scope="session")
async def orchestrator_service():
    """Ensure orchestrator service is running"""
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{ORCHESTRATOR_URL}/health")
            if response.status_code == 200:
                return True
        except Exception:
            pytest.skip("Orchestrator service not running")
    return False


@pytest.fixture(autouse=True)
async def wait_for_service(orchestrator_service):
    """Wait for service before each test"""
    await asyncio.sleep(0.5)


if __name__ == "__main__":
    # Run pytest tests
    pytest.main([__file__, "-v", "-m", "performance"])

    # Instructions for Locust
    if LOCUST_AVAILABLE:
        print("\n" + "="*60)
        print("To run Locust load tests:")
        print(f"  locust -f {__file__} --host {ORCHESTRATOR_URL}")
        print("="*60)
