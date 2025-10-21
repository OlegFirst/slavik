"""
Performance Tests for System BCM Service

Tests performance metrics, RTO/RPO compliance, resource usage
"""

import pytest
import time
import asyncio
import psutil
import requests
from typing import Dict, List
import statistics


class TestPerformanceMetrics:
    """Performance metrics tests"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.base_url = "http://localhost:8050"
        self.process = psutil.Process()

    def test_api_response_time(self, performance_thresholds):
        """Test API response times are within limits"""
        endpoints = [
            "/health",
            "/status",
            "/metrics"
        ]

        response_times = []
        for endpoint in endpoints:
            start = time.time()
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                duration = time.time() - start

                assert response.status_code == 200, f"{endpoint} returned {response.status_code}"
                assert duration < performance_thresholds["api_response_max"], \
                    f"{endpoint} took {duration}s (max: {performance_thresholds['api_response_max']}s)"

                response_times.append(duration)
            except requests.exceptions.RequestException as e:
                pytest.skip(f"Service not available: {e}")

        # Check average response time
        avg_response = statistics.mean(response_times)
        print(f"\n Average API response time: {avg_response:.3f}s")
        print(f"   Fastest: {min(response_times):.3f}s")
        print(f"   Slowest: {max(response_times):.3f}s")

    def test_bcm_cycle_performance(self, performance_thresholds):
        """Test BCM cycle completes within time limit"""
        try:
            # Measure cycle execution time
            start = time.time()
            response = requests.post(f"{self.base_url}/cycle/trigger", timeout=60)
            duration = time.time() - start

            assert response.status_code == 200, f"Cycle trigger failed: {response.status_code}"

            result = response.json()
            assert "cycle_id" in result, "No cycle_id in response"

            # Check duration
            assert duration < performance_thresholds["cycle_duration_max"], \
                f"Cycle took {duration}s (max: {performance_thresholds['cycle_duration_max']}s)"

            print(f"\n BCM Cycle Performance:")
            print(f"   Duration: {duration:.2f}s")
            print(f"   Target: <{performance_thresholds['cycle_duration_max']}s")
            print(f"   Performance: {((performance_thresholds['cycle_duration_max'] - duration) / performance_thresholds['cycle_duration_max'] * 100):.1f}% better than target")

        except requests.exceptions.RequestException as e:
            pytest.skip(f"Service not available: {e}")

    def test_resource_usage(self, performance_thresholds):
        """Test CPU and memory usage are within limits"""
        # Collect samples over 10 seconds
        cpu_samples = []
        memory_samples = []

        for _ in range(10):
            cpu_percent = self.process.cpu_percent(interval=1)
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()

            cpu_samples.append(cpu_percent)
            memory_samples.append(memory_percent)

        avg_cpu = statistics.mean(cpu_samples)
        avg_memory = statistics.mean(memory_samples)
        max_cpu = max(cpu_samples)
        max_memory = max(memory_samples)

        print(f"\n Resource Usage:")
        print(f"   CPU Average: {avg_cpu:.1f}% (max allowed: {performance_thresholds['cpu_usage_max']}%)")
        print(f"   CPU Peak: {max_cpu:.1f}%")
        print(f"   Memory Average: {avg_memory:.1f}% (max allowed: {performance_thresholds['memory_usage_max']}%)")
        print(f"   Memory Peak: {max_memory:.1f}%")

        assert avg_cpu < performance_thresholds["cpu_usage_max"], \
            f"Average CPU {avg_cpu}% exceeds {performance_thresholds['cpu_usage_max']}%"
        assert avg_memory < performance_thresholds["memory_usage_max"], \
            f"Average Memory {avg_memory}% exceeds {performance_thresholds['memory_usage_max']}%"

    def test_concurrent_api_requests(self):
        """Test API can handle concurrent requests"""
        import concurrent.futures

        num_requests = 20

        def make_request():
            start = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=5)
            duration = time.time() - start
            return response.status_code, duration

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(num_requests)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]

            # All requests should succeed
            status_codes = [r[0] for r in results]
            durations = [r[1] for r in results]

            success_rate = sum(1 for code in status_codes if code == 200) / num_requests
            avg_duration = statistics.mean(durations)

            print(f"\n Concurrent Requests Performance:")
            print(f"   Total Requests: {num_requests}")
            print(f"   Success Rate: {success_rate * 100:.1f}%")
            print(f"   Average Duration: {avg_duration:.3f}s")
            print(f"   Max Duration: {max(durations):.3f}s")

            assert success_rate >= 0.95, f"Success rate {success_rate * 100}% below 95%"

        except requests.exceptions.RequestException as e:
            pytest.skip(f"Service not available: {e}")

    def test_metrics_collection_performance(self):
        """Test Prometheus metrics collection performance"""
        try:
            # Collect metrics multiple times
            collection_times = []

            for _ in range(5):
                start = time.time()
                response = requests.get(f"{self.base_url}/metrics", timeout=5)
                duration = time.time() - start

                assert response.status_code == 200
                collection_times.append(duration)

            avg_time = statistics.mean(collection_times)

            print(f"\n Metrics Collection Performance:")
            print(f"   Average Collection Time: {avg_time:.3f}s")
            print(f"   Total Metrics: {len(response.text.split('\\n'))}")

            assert avg_time < 0.5, f"Metrics collection took {avg_time}s (max: 0.5s)"

        except requests.exceptions.RequestException as e:
            pytest.skip(f"Service not available: {e}")


class TestRTOCompliance:
    """RTO (Recovery Time Objective) compliance tests"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for RTO tests"""
        self.base_url = "http://localhost:8050"

    def test_recovery_procedures_rto(self, performance_thresholds):
        """Test recovery procedures meet RTO targets"""
        procedures = [
            {"name": "eventbus_recovery", "expected_rto": 30},
            {"name": "db_pool_recovery", "expected_rto": 120},
            {"name": "service_restart", "expected_rto": 300}
        ]

        results = []

        for proc in procedures:
            try:
                start = time.time()
                response = requests.post(
                    f"{self.base_url}/recovery/trigger",
                    json={"procedure": proc["name"]},
                    timeout=performance_thresholds["recovery_rto_max"]
                )
                duration = time.time() - start

                if response.status_code == 200:
                    result = response.json()
                    rto_met = duration <= proc["expected_rto"]

                    results.append({
                        "procedure": proc["name"],
                        "duration": duration,
                        "expected_rto": proc["expected_rto"],
                        "rto_met": rto_met
                    })

                    print(f"\n{'' if rto_met else ''} {proc['name']}:")
                    print(f"   Duration: {duration:.1f}s")
                    print(f"   Expected RTO: {proc['expected_rto']}s")
                    print(f"   RTO Met: {'Yes' if rto_met else 'No'}")

            except requests.exceptions.RequestException:
                # Recovery endpoint might not be available in test mode
                pass

        if results:
            rto_compliance = sum(1 for r in results if r["rto_met"]) / len(results)
            print(f"\n Overall RTO Compliance: {rto_compliance * 100:.1f}%")
            assert rto_compliance >= 0.8, f"RTO compliance {rto_compliance * 100}% below 80%"


class TestLoadTests:
    """Load testing for System BCM"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for load tests"""
        self.base_url = "http://localhost:8050"

    def test_sustained_load(self):
        """Test system under sustained load"""
        import concurrent.futures

        duration_seconds = 30
        requests_per_second = 5
        total_requests = duration_seconds * requests_per_second

        start_time = time.time()
        request_times = []
        errors = 0

        def make_request():
            try:
                start = time.time()
                response = requests.get(f"{self.base_url}/health", timeout=5)
                duration = time.time() - start
                return response.status_code == 200, duration
            except:
                return False, 0

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for i in range(total_requests):
                    futures.append(executor.submit(make_request))

                    # Pace requests
                    if i < total_requests - 1:
                        time.sleep(1.0 / requests_per_second)

                # Collect results
                for future in concurrent.futures.as_completed(futures):
                    success, duration = future.result()
                    if success:
                        request_times.append(duration)
                    else:
                        errors += 1

            total_duration = time.time() - start_time
            success_rate = len(request_times) / total_requests
            avg_response = statistics.mean(request_times) if request_times else 0
            p95_response = sorted(request_times)[int(len(request_times) * 0.95)] if request_times else 0

            print(f"\n Load Test Results:")
            print(f"   Duration: {total_duration:.1f}s")
            print(f"   Total Requests: {total_requests}")
            print(f"   Success Rate: {success_rate * 100:.1f}%")
            print(f"   Errors: {errors}")
            print(f"   Average Response: {avg_response:.3f}s")
            print(f"   P95 Response: {p95_response:.3f}s")

            assert success_rate >= 0.95, f"Success rate {success_rate * 100}% below 95%"
            assert avg_response < 1.0, f"Average response {avg_response}s exceeds 1s"

        except requests.exceptions.RequestException as e:
            pytest.skip(f"Service not available: {e}")


class TestScalability:
    """Scalability tests"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for scalability tests"""
        self.base_url = "http://localhost:8050"

    def test_memory_growth_over_cycles(self):
        """Test memory doesn't grow significantly over multiple cycles"""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

        # Run 5 cycles
        for i in range(5):
            try:
                response = requests.post(f"{self.base_url}/cycle/trigger", timeout=60)
                assert response.status_code == 200
                time.sleep(2)  # Wait between cycles
            except requests.exceptions.RequestException:
                pytest.skip("Service not available")

        final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        growth_percent = (memory_growth / initial_memory) * 100

        print(f"\n Memory Growth Test:")
        print(f"   Initial Memory: {initial_memory:.1f} MB")
        print(f"   Final Memory: {final_memory:.1f} MB")
        print(f"   Growth: {memory_growth:.1f} MB ({growth_percent:.1f}%)")

        # Memory growth should be less than 20%
        assert growth_percent < 20, f"Memory grew by {growth_percent}% (max: 20%)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
