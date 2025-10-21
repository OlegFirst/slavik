"""
Load Testing Script for AI Orchestrator
========================================

Tests orchestrator performance under load:
- 10, 50, 100 concurrent decisions
- Sustained load over time
- Spike testing
- Stress testing to find breaking point

Usage:
    python load_test.py --url http://localhost:8050 --concurrency 50 --duration 60
"""

import asyncio
import aiohttp
import time
import argparse
import statistics
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class LoadTestResult:
    """Results from load test run"""
    total_requests: int
    successful: int
    failed: int
    duration_seconds: float
    requests_per_second: float
    latencies_ms: List[float]
    p50_ms: float
    p95_ms: float
    p99_ms: float
    min_ms: float
    max_ms: float
    avg_ms: float
    errors: List[str]


class OrchestratorLoadTester:
    """Load tester for AI Orchestrator"""

    def __init__(self, base_url: str = "http://localhost:8050"):
        self.base_url = base_url
        self.session: aiohttp.ClientSession = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def make_decision_request(self, workflow_id: str) -> Dict[str, Any]:
        """
        Make single decision request

        Returns:
            (latency_ms, success, error_msg)
        """
        situation = {
            'workflow_id': workflow_id,
            'workflow_stuck': True,
            'stuck_duration_minutes': 15,
            'priority': 'NORMAL',
            'test_load': True
        }

        payload = {
            'situation': situation,
            'tenant_id': 'load-test'
        }

        start = time.time()
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/decide",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                latency_ms = (time.time() - start) * 1000

                if response.status == 200:
                    await response.json()
                    return latency_ms, True, None
                else:
                    error = await response.text()
                    return latency_ms, False, f"HTTP {response.status}: {error}"

        except asyncio.TimeoutError:
            latency_ms = (time.time() - start) * 1000
            return latency_ms, False, "Timeout"
        except Exception as e:
            latency_ms = (time.time() - start) * 1000
            return latency_ms, False, str(e)

    async def run_concurrent_batch(
        self,
        batch_size: int,
        batch_id: int
    ) -> List[tuple]:
        """
        Run batch of concurrent requests

        Returns:
            List of (latency, success, error) tuples
        """
        tasks = []
        for i in range(batch_size):
            workflow_id = f"load_test_batch{batch_id}_req{i}"
            tasks.append(self.make_decision_request(workflow_id))

        return await asyncio.gather(*tasks)

    async def run_load_test(
        self,
        concurrency: int,
        duration_seconds: int,
        ramp_up_seconds: int = 0
    ) -> LoadTestResult:
        """
        Run load test

        Args:
            concurrency: Number of concurrent requests
            duration_seconds: Test duration
            ramp_up_seconds: Gradual ramp-up time

        Returns:
            LoadTestResult with metrics
        """
        print(f"\n Starting load test:")
        print(f"   Concurrency: {concurrency}")
        print(f"   Duration: {duration_seconds}s")
        print(f"   Ramp-up: {ramp_up_seconds}s")
        print(f"   Target: {self.base_url}\n")

        start_time = time.time()
        end_time = start_time + duration_seconds

        latencies: List[float] = []
        successes = 0
        failures = 0
        errors: List[str] = []

        batch_id = 0

        # Ramp-up
        if ramp_up_seconds > 0:
            print(f"⏫ Ramping up over {ramp_up_seconds}s...")
            ramp_steps = 10
            step_duration = ramp_up_seconds / ramp_steps
            step_concurrency = concurrency / ramp_steps

            for step in range(ramp_steps):
                current_concurrency = int((step + 1) * step_concurrency)
                results = await self.run_concurrent_batch(current_concurrency, batch_id)
                batch_id += 1

                for latency, success, error in results:
                    latencies.append(latency)
                    if success:
                        successes += 1
                    else:
                        failures += 1
                        if error:
                            errors.append(error)

                await asyncio.sleep(step_duration)

        # Main load test
        print(f" Running at {concurrency} concurrent requests...")

        while time.time() < end_time:
            # Run batch
            results = await self.run_concurrent_batch(concurrency, batch_id)
            batch_id += 1

            # Collect results
            for latency, success, error in results:
                latencies.append(latency)
                if success:
                    successes += 1
                else:
                    failures += 1
                    if error and error not in errors:
                        errors.append(error)

            # Progress
            elapsed = time.time() - start_time
            progress = (elapsed / duration_seconds) * 100
            print(f"   Progress: {progress:.1f}% | "
                  f"Requests: {len(latencies)} | "
                  f"Success: {successes} | "
                  f"Failed: {failures}", end='\r')

            # Small delay between batches
            await asyncio.sleep(0.1)

        print()  # New line after progress

        # Calculate metrics
        total_duration = time.time() - start_time
        total_requests = len(latencies)

        latencies.sort()

        p50_idx = int(total_requests * 0.50)
        p95_idx = int(total_requests * 0.95)
        p99_idx = int(total_requests * 0.99)

        result = LoadTestResult(
            total_requests=total_requests,
            successful=successes,
            failed=failures,
            duration_seconds=total_duration,
            requests_per_second=total_requests / total_duration,
            latencies_ms=latencies,
            p50_ms=latencies[p50_idx] if latencies else 0,
            p95_ms=latencies[p95_idx] if latencies else 0,
            p99_ms=latencies[p99_idx] if latencies else 0,
            min_ms=min(latencies) if latencies else 0,
            max_ms=max(latencies) if latencies else 0,
            avg_ms=statistics.mean(latencies) if latencies else 0,
            errors=errors[:10]  # Keep first 10 unique errors
        )

        return result

    def print_results(self, result: LoadTestResult, test_name: str = "Load Test"):
        """Print load test results"""
        print(f"\n{'='*60}")
        print(f" {test_name} Results")
        print(f"{'='*60}")

        print(f"\n Throughput:")
        print(f"   Total Requests:  {result.total_requests}")
        print(f"   Duration:        {result.duration_seconds:.2f}s")
        print(f"   Req/sec:         {result.requests_per_second:.2f}")

        print(f"\n Success Rate:")
        success_rate = (result.successful / result.total_requests * 100) if result.total_requests > 0 else 0
        print(f"   Successful:      {result.successful} ({success_rate:.1f}%)")
        print(f"   Failed:          {result.failed}")

        print(f"\n Latency (ms):")
        print(f"   Min:             {result.min_ms:.2f}ms")
        print(f"   Avg:             {result.avg_ms:.2f}ms")
        print(f"   P50:             {result.p50_ms:.2f}ms")
        print(f"   P95:             {result.p95_ms:.2f}ms")
        print(f"   P99:             {result.p99_ms:.2f}ms")
        print(f"   Max:             {result.max_ms:.2f}ms")

        # Check targets
        print(f"\n Target Compliance:")
        print(f"   P95 < 100ms:     {' PASS' if result.p95_ms < 100 else ' FAIL'} ({result.p95_ms:.2f}ms)")
        print(f"   Success > 95%:   {' PASS' if success_rate > 95 else ' FAIL'} ({success_rate:.1f}%)")

        if result.errors:
            print(f"\n Errors (first 10):")
            for error in result.errors[:10]:
                print(f"   - {error}")

        print(f"\n{'='*60}\n")

    async def run_test_suite(self):
        """Run complete test suite"""
        print("\n" + "="*60)
        print(" AI Orchestrator Load Test Suite")
        print("="*60)

        results = {}

        # Test 1: Light load (10 concurrent)
        print("\n[1/4] Light Load Test (10 concurrent)...")
        results['light'] = await self.run_load_test(
            concurrency=10,
            duration_seconds=30,
            ramp_up_seconds=5
        )
        self.print_results(results['light'], "Light Load (10 concurrent)")

        # Test 2: Medium load (50 concurrent)
        print("\n[2/4] Medium Load Test (50 concurrent)...")
        results['medium'] = await self.run_load_test(
            concurrency=50,
            duration_seconds=60,
            ramp_up_seconds=10
        )
        self.print_results(results['medium'], "Medium Load (50 concurrent)")

        # Test 3: Heavy load (100 concurrent)
        print("\n[3/4] Heavy Load Test (100 concurrent)...")
        results['heavy'] = await self.run_load_test(
            concurrency=100,
            duration_seconds=60,
            ramp_up_seconds=15
        )
        self.print_results(results['heavy'], "Heavy Load (100 concurrent)")

        # Test 4: Spike test
        print("\n[4/4] Spike Test (sudden surge to 200)...")
        results['spike'] = await self.run_load_test(
            concurrency=200,
            duration_seconds=30,
            ramp_up_seconds=0  # No ramp-up = spike
        )
        self.print_results(results['spike'], "Spike Test (200 concurrent)")

        # Summary
        self.print_summary(results)

        return results

    def print_summary(self, results: Dict[str, LoadTestResult]):
        """Print summary comparison"""
        print("\n" + "="*60)
        print(" Load Test Summary Comparison")
        print("="*60)

        print(f"\n{'Test':<20} {'Req/sec':<12} {'P95 (ms)':<12} {'Success %':<12}")
        print("-" * 60)

        for name, result in results.items():
            success_rate = (result.successful / result.total_requests * 100) if result.total_requests > 0 else 0
            print(f"{name.capitalize():<20} {result.requests_per_second:<12.2f} {result.p95_ms:<12.2f} {success_rate:<12.1f}")

        print("\n" + "="*60)

        # Overall assessment
        print("\n Assessment:")
        all_pass = all(
            r.p95_ms < 100 and (r.successful / r.total_requests > 0.95)
            for r in results.values()
        )

        if all_pass:
            print("    All tests PASSED - System ready for production")
        else:
            print("   ️  Some tests FAILED - Optimization needed")

        print()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Load test AI Orchestrator")
    parser.add_argument('--url', default='http://localhost:8050', help='Orchestrator API URL')
    parser.add_argument('--concurrency', type=int, help='Concurrent requests (for single test)')
    parser.add_argument('--duration', type=int, default=60, help='Test duration in seconds')
    parser.add_argument('--suite', action='store_true', help='Run full test suite')

    args = parser.parse_args()

    async with OrchestratorLoadTester(args.url) as tester:
        # Check if orchestrator is reachable
        try:
            async with tester.session.get(f"{args.url}/health") as response:
                if response.status != 200:
                    print(f" Orchestrator not healthy at {args.url}")
                    return
                print(f" Orchestrator healthy at {args.url}\n")
        except Exception as e:
            print(f" Cannot reach orchestrator at {args.url}: {e}")
            return

        # Run test(s)
        if args.suite:
            await tester.run_test_suite()
        elif args.concurrency:
            result = await tester.run_load_test(
                concurrency=args.concurrency,
                duration_seconds=args.duration,
                ramp_up_seconds=10
            )
            tester.print_results(result, f"Load Test ({args.concurrency} concurrent)")
        else:
            # Default: run suite
            await tester.run_test_suite()


if __name__ == "__main__":
    asyncio.run(main())
