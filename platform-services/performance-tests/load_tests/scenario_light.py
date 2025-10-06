"""
Light Load Test Scenario
=========================

Simulates light production load for baseline performance testing.

Configuration:
- 10 concurrent users
- 1 user spawned per second
- 5 minute duration
- 1000 total target requests

Usage:
    locust -f load_tests/scenario_light.py --host=http://localhost --users 10 --spawn-rate 1 --run-time 5m
"""

from locust import HttpUser, task, between, events
import json
import random

DEV_USER_HEADER = {
    'X-Dev-User': json.dumps({
        'user_id': 'light-load-user',
        'tenant_id': 'light-load-tenant'
    })
}


class LightLoadUser(HttpUser):
    """Light load user simulating normal production usage"""

    wait_time = between(2, 5)  # Wait 2-5 seconds between tasks

    def on_start(self):
        """Initialize test data"""
        self.bia_service = "http://localhost:8012"
        self.compliance_service = "http://localhost:8014"
        self.planning_service = "http://localhost:8011"
        self.plans_service = "http://localhost:8023"
        self.process_ids = []

    @task(20)
    def view_bia_processes(self):
        """Most common: View BIA processes list"""
        self.client.get(
            f"{self.bia_service}/api/bia/processes",
            headers=DEV_USER_HEADER,
            name="BIA: List Processes"
        )

    @task(15)
    def view_process_detail(self):
        """Common: View single process details"""
        if self.process_ids:
            process_id = random.choice(self.process_ids)
            self.client.get(
                f"{self.bia_service}/api/bia/processes/{process_id}",
                headers=DEV_USER_HEADER,
                name="BIA: Get Process"
            )

    @task(10)
    def view_audits(self):
        """View compliance audits"""
        self.client.get(
            f"{self.compliance_service}/api/v1/audits",
            headers=DEV_USER_HEADER,
            name="Compliance: List Audits"
        )

    @task(10)
    def view_strategies(self):
        """View planning strategies"""
        self.client.get(
            f"{self.planning_service}/api/v1/strategies",
            headers=DEV_USER_HEADER,
            name="Planning: List Strategies"
        )

    @task(10)
    def view_plans(self):
        """View plans"""
        self.client.get(
            f"{self.plans_service}/api/v1/plans",
            headers=DEV_USER_HEADER,
            name="Plans: List Plans"
        )

    @task(5)
    def create_bia_process(self):
        """Occasional: Create new BIA process"""
        process_data = {
            "name": f"Light Load Process {random.randint(1000, 9999)}",
            "description": "Light load test process",
            "criticality": random.choice(["CRITICAL", "HIGH", "MEDIUM", "LOW"]),
            "rto_hours": random.randint(1, 24),
            "rpo_hours": random.randint(1, 12),
            "mtpd_hours": random.randint(4, 48)
        }

        response = self.client.post(
            f"{self.bia_service}/api/bia/processes",
            json=process_data,
            headers=DEV_USER_HEADER,
            name="BIA: Create Process"
        )

        if response.status_code == 201:
            self.process_ids.append(response.json()["id"])

    @task(3)
    def update_process(self):
        """Rare: Update existing process"""
        if self.process_ids:
            process_id = random.choice(self.process_ids)
            update_data = {"rto_hours": random.randint(1, 24)}

            self.client.put(
                f"{self.bia_service}/api/bia/processes/{process_id}",
                json=update_data,
                headers=DEV_USER_HEADER,
                name="BIA: Update Process"
            )

    @task(2)
    def health_checks(self):
        """Regular: Health check monitoring"""
        services = [
            (self.bia_service, "BIA"),
            (self.compliance_service, "Compliance"),
            (self.planning_service, "Planning"),
            (self.plans_service, "Plans")
        ]

        service_url, service_name = random.choice(services)
        self.client.get(
            f"{service_url}/health",
            name=f"{service_name}: Health Check"
        )


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("=" * 80)
    print("LIGHT LOAD TEST STARTED")
    print("Configuration: 10 users, 1/sec spawn rate, 5 min duration")
    print("Expected: ~1000 total requests")
    print("=" * 80)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("=" * 80)
    print("LIGHT LOAD TEST COMPLETED")
    stats = environment.stats
    print(f"Total Requests: {stats.total.num_requests}")
    print(f"Total Failures: {stats.total.num_failures}")
    print(f"Average Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"P95 Response Time: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"Requests/sec: {stats.total.total_rps:.2f}")
    print("=" * 80)
