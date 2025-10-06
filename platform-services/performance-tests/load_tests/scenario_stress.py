"""
Stress Test Scenario
====================

Gradual load increase to identify breaking point and performance degradation.

Configuration:
- Gradual increase from 10 to 200 users
- 5 users spawned per second
- 20 minute duration
- Identifies system limits and degradation patterns

Usage:
    locust -f load_tests/scenario_stress.py --host=http://localhost --users 200 --spawn-rate 5 --run-time 20m
"""

from locust import HttpUser, task, between, events, LoadTestShape
import json
import random
import time

DEV_USER_HEADER = {
    'X-Dev-User': json.dumps({
        'user_id': 'stress-test-user',
        'tenant_id': 'stress-test-tenant'
    })
}


class StressTestShape(LoadTestShape):
    """
    Custom load shape for stress testing.
    Gradually increases load to find breaking point.
    """

    stages = [
        {"duration": 120, "users": 10, "spawn_rate": 2},   # 2 min: 10 users
        {"duration": 240, "users": 25, "spawn_rate": 3},   # 4 min: 25 users
        {"duration": 360, "users": 50, "spawn_rate": 5},   # 6 min: 50 users
        {"duration": 480, "users": 75, "spawn_rate": 5},   # 8 min: 75 users
        {"duration": 600, "users": 100, "spawn_rate": 5},  # 10 min: 100 users
        {"duration": 720, "users": 125, "spawn_rate": 5},  # 12 min: 125 users
        {"duration": 840, "users": 150, "spawn_rate": 5},  # 14 min: 150 users
        {"duration": 960, "users": 175, "spawn_rate": 5},  # 16 min: 175 users
        {"duration": 1080, "users": 200, "spawn_rate": 5}, # 18 min: 200 users
        {"duration": 1200, "users": 200, "spawn_rate": 0}, # 20 min: hold at 200
    ]

    def tick(self):
        """Define custom load shape"""
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])

        return None


class StressTestUser(HttpUser):
    """Stress test user for breaking point identification"""

    wait_time = between(0.5, 1.5)  # Aggressive interaction

    def on_start(self):
        """Initialize test data"""
        self.bia_service = "http://localhost:8012"
        self.compliance_service = "http://localhost:8014"
        self.planning_service = "http://localhost:8011"
        self.plans_service = "http://localhost:8023"
        self.process_ids = []
        self.audit_ids = []

    @task(35)
    def view_bia_processes(self):
        """Very high frequency: View BIA processes"""
        with self.client.get(
            f"{self.bia_service}/api/bia/processes?limit=100",
            headers=DEV_USER_HEADER,
            name="BIA: List Processes",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed: {response.status_code}")
            elif response.elapsed.total_seconds() > 2:
                response.failure(f"Too slow: {response.elapsed.total_seconds():.2f}s")

    @task(30)
    def view_process_detail(self):
        """High frequency: View process details"""
        if self.process_ids:
            process_id = random.choice(self.process_ids)
            with self.client.get(
                f"{self.bia_service}/api/bia/processes/{process_id}",
                headers=DEV_USER_HEADER,
                name="BIA: Get Process",
                catch_response=True
            ) as response:
                if response.status_code != 200:
                    response.failure(f"Failed: {response.status_code}")
                elif response.elapsed.total_seconds() > 1:
                    response.failure(f"Too slow: {response.elapsed.total_seconds():.2f}s")

    @task(25)
    def view_audits(self):
        """View compliance audits"""
        with self.client.get(
            f"{self.compliance_service}/api/v1/audits?limit=100",
            headers=DEV_USER_HEADER,
            name="Compliance: List Audits",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed: {response.status_code}")

    @task(25)
    def view_strategies(self):
        """View planning strategies"""
        with self.client.get(
            f"{self.planning_service}/api/v1/strategies?limit=100",
            headers=DEV_USER_HEADER,
            name="Planning: List Strategies",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed: {response.status_code}")

    @task(25)
    def view_plans(self):
        """View plans"""
        with self.client.get(
            f"{self.plans_service}/api/v1/plans?limit=100",
            headers=DEV_USER_HEADER,
            name="Plans: List Plans",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed: {response.status_code}")

    @task(20)
    def create_bia_process(self):
        """Create BIA process"""
        process_data = {
            "name": f"Stress Test {random.randint(100000, 999999)}",
            "description": "Stress test process",
            "criticality": random.choice(["CRITICAL", "HIGH", "MEDIUM"]),
            "business_unit": random.choice(["IT", "Finance", "Operations"]),
            "rto_hours": random.randint(1, 24),
            "rpo_hours": random.randint(1, 12),
            "mtpd_hours": random.randint(4, 48),
            "financial_impact": {
                "1_hour": random.randint(50000, 500000),
                "4_hours": random.randint(200000, 2000000),
                "24_hours": random.randint(1000000, 10000000)
            }
        }

        with self.client.post(
            f"{self.bia_service}/api/bia/processes",
            json=process_data,
            headers=DEV_USER_HEADER,
            name="BIA: Create Process",
            catch_response=True
        ) as response:
            if response.status_code == 201:
                self.process_ids.append(response.json()["id"])
            elif response.status_code not in [400, 409, 422]:
                response.failure(f"Unexpected status: {response.status_code}")

    @task(15)
    def create_audit(self):
        """Create compliance audit"""
        audit_data = {
            "audit_type": random.choice(["internal", "external"]),
            "scope": f"Stress Audit {random.randint(100000, 999999)}",
            "auditor": f"Auditor {random.randint(1, 50)}",
            "start_date": "2025-10-01",
            "end_date": "2025-10-30"
        }

        with self.client.post(
            f"{self.compliance_service}/api/v1/audits",
            json=audit_data,
            headers=DEV_USER_HEADER,
            name="Compliance: Create Audit",
            catch_response=True
        ) as response:
            if response.status_code == 201:
                self.audit_ids.append(response.json()["id"])
            elif response.status_code not in [400, 422]:
                response.failure(f"Unexpected status: {response.status_code}")

    @task(15)
    def create_strategy(self):
        """Create planning strategy"""
        strategy_data = {
            "name": f"Stress Strategy {random.randint(100000, 999999)}",
            "description": "Stress test strategy",
            "objectives": ["Test objective"],
            "scope": "IT",
            "timeline_months": 12
        }

        with self.client.post(
            f"{self.planning_service}/api/v1/strategies",
            json=strategy_data,
            headers=DEV_USER_HEADER,
            name="Planning: Create Strategy",
            catch_response=True
        ) as response:
            if response.status_code not in [201, 400, 422]:
                response.failure(f"Unexpected status: {response.status_code}")

    @task(15)
    def create_plan(self):
        """Create plan"""
        plan_data = {
            "name": f"Stress Plan {random.randint(100000, 999999)}",
            "plan_type": "incident_response",
            "description": "Stress test plan",
            "scope": "IT Infrastructure",
            "activation_criteria": ["Test criteria"]
        }

        with self.client.post(
            f"{self.plans_service}/api/v1/plans",
            json=plan_data,
            headers=DEV_USER_HEADER,
            name="Plans: Create Plan",
            catch_response=True
        ) as response:
            if response.status_code not in [201, 400, 422]:
                response.failure(f"Unexpected status: {response.status_code}")

    @task(10)
    def update_operations(self):
        """Update operations"""
        if self.process_ids:
            process_id = random.choice(self.process_ids)
            update_data = {"rto_hours": random.randint(1, 24)}

            with self.client.put(
                f"{self.bia_service}/api/bia/processes/{process_id}",
                json=update_data,
                headers=DEV_USER_HEADER,
                name="BIA: Update Process",
                catch_response=True
            ) as response:
                if response.status_code not in [200, 404]:
                    response.failure(f"Unexpected status: {response.status_code}")

    @task(8)
    def bulk_operations(self):
        """Bulk create operations"""
        processes = []
        for i in range(20):
            processes.append({
                "name": f"Bulk Stress {random.randint(100000, 999999)}",
                "description": "Bulk stress test",
                "criticality": "MEDIUM",
                "rto_hours": 8,
                "rpo_hours": 4,
                "mtpd_hours": 16
            })

        with self.client.post(
            f"{self.bia_service}/api/bia/processes/bulk",
            json={"processes": processes},
            headers=DEV_USER_HEADER,
            name="BIA: Bulk Create (20)",
            catch_response=True
        ) as response:
            if response.status_code in [201, 207]:
                data = response.json()
                if "created" in data:
                    for item in data["created"]:
                        self.process_ids.append(item["id"])
            elif response.status_code not in [400, 413, 422]:
                response.failure(f"Unexpected status: {response.status_code}")

    @task(5)
    def health_checks(self):
        """Health checks"""
        services = [
            (self.bia_service, "BIA"),
            (self.compliance_service, "Compliance"),
            (self.planning_service, "Planning"),
            (self.plans_service, "Plans")
        ]

        service_url, service_name = random.choice(services)
        with self.client.get(
            f"{service_url}/health",
            name=f"{service_name}: Health",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Service unhealthy: {response.status_code}")


# Performance tracking variables
performance_data = {
    "stage_metrics": [],
    "current_stage": 0
}


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("=" * 80)
    print("STRESS TEST STARTED")
    print("Configuration: Gradual increase 10 → 200 users over 20 minutes")
    print("Objective: Identify breaking point and performance degradation")
    print("=" * 80)
    print("\nLoad Stages:")
    for i, stage in enumerate(StressTestShape.stages):
        print(f"  Stage {i+1}: {stage['duration']//60}min → {stage['users']} users @ {stage['spawn_rate']}/sec")
    print("=" * 80)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n" + "=" * 80)
    print("STRESS TEST COMPLETED")
    print("=" * 80)

    stats = environment.stats
    print(f"\n📊 Overall Statistics:")
    print(f"  Total Requests: {stats.total.num_requests:,}")
    print(f"  Total Failures: {stats.total.num_failures:,}")
    print(f"  Average Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"  Median (P50): {stats.total.get_response_time_percentile(0.50):.2f}ms")
    print(f"  P95: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"  P99: {stats.total.get_response_time_percentile(0.99):.2f}ms")
    print(f"  Max Response Time: {stats.total.max_response_time:.2f}ms")
    print(f"  Requests/sec: {stats.total.total_rps:.2f}")

    if stats.total.num_requests > 0:
        failure_rate = (stats.total.num_failures / stats.total.num_requests) * 100
        print(f"  Failure Rate: {failure_rate:.2f}%")

        print(f"\n🎯 Performance Analysis:")

        # Breaking point analysis
        if failure_rate > 10:
            print(f"  ❌ BREAKING POINT REACHED: {failure_rate:.1f}% failure rate")
        elif failure_rate > 5:
            print(f"  ⚠️  DEGRADATION DETECTED: {failure_rate:.1f}% failure rate")
        elif failure_rate > 1:
            print(f"  ⚠️  MINOR ISSUES: {failure_rate:.1f}% failure rate")
        else:
            print(f"  ✅ STABLE PERFORMANCE: {failure_rate:.1f}% failure rate")

        # Response time analysis
        p95 = stats.total.get_response_time_percentile(0.95)
        p99 = stats.total.get_response_time_percentile(0.99)

        if p95 > 2000:
            print(f"  ❌ SEVERE LATENCY: P95 = {p95:.0f}ms (target: <500ms)")
        elif p95 > 1000:
            print(f"  ⚠️  HIGH LATENCY: P95 = {p95:.0f}ms (target: <500ms)")
        elif p95 > 500:
            print(f"  ⚠️  MODERATE LATENCY: P95 = {p95:.0f}ms (target: <500ms)")
        else:
            print(f"  ✅ GOOD LATENCY: P95 = {p95:.0f}ms (target: <500ms)")

        # Throughput analysis
        if stats.total.total_rps < 10:
            print(f"  ❌ LOW THROUGHPUT: {stats.total.total_rps:.1f} req/s")
        elif stats.total.total_rps < 50:
            print(f"  ⚠️  MODERATE THROUGHPUT: {stats.total.total_rps:.1f} req/s")
        else:
            print(f"  ✅ GOOD THROUGHPUT: {stats.total.total_rps:.1f} req/s")

    print("\n" + "=" * 80)
    print("📝 Recommendations:")
    print("  1. Review logs for errors during peak load")
    print("  2. Check database connection pool utilization")
    print("  3. Verify cache hit ratio during stress test")
    print("  4. Monitor CPU/Memory usage across services")
    print("  5. Review P99 latency for performance bottlenecks")
    print("=" * 80)
