"""
Medium Load Test Scenario
==========================

Simulates normal production load for performance validation.

Configuration:
- 50 concurrent users
- 5 users spawned per second
- 10 minute duration
- ~10,000 total target requests

Usage:
    locust -f load_tests/scenario_medium.py --host=http://localhost --users 50 --spawn-rate 5 --run-time 10m
"""

from locust import HttpUser, task, between, events
import json
import random

DEV_USER_HEADER = {
    'X-Dev-User': json.dumps({
        'user_id': 'medium-load-user',
        'tenant_id': 'medium-load-tenant'
    })
}


class MediumLoadUser(HttpUser):
    """Medium load user simulating normal production traffic"""

    wait_time = between(1, 3)  # Faster interaction

    def on_start(self):
        """Initialize test data"""
        self.bia_service = "http://localhost:8012"
        self.compliance_service = "http://localhost:8014"
        self.planning_service = "http://localhost:8011"
        self.plans_service = "http://localhost:8023"
        self.process_ids = []
        self.audit_ids = []
        self.strategy_ids = []
        self.plan_ids = []

        # Create initial test data
        self._create_initial_data()

    def _create_initial_data(self):
        """Create some initial test data"""
        # Create BIA processes
        for i in range(2):
            process_data = {
                "name": f"Medium Load Process {random.randint(1000, 9999)}",
                "description": "Medium load test",
                "criticality": "HIGH",
                "rto_hours": 4,
                "rpo_hours": 2,
                "mtpd_hours": 8
            }

            response = self.client.post(
                f"{self.bia_service}/api/bia/processes",
                json=process_data,
                headers=DEV_USER_HEADER
            )

            if response.status_code == 201:
                self.process_ids.append(response.json()["id"])

    @task(25)
    def view_bia_processes(self):
        """View BIA processes list"""
        self.client.get(
            f"{self.bia_service}/api/bia/processes",
            headers=DEV_USER_HEADER,
            name="BIA: List Processes"
        )

    @task(20)
    def view_process_detail(self):
        """View process details"""
        if self.process_ids:
            process_id = random.choice(self.process_ids)
            self.client.get(
                f"{self.bia_service}/api/bia/processes/{process_id}",
                headers=DEV_USER_HEADER,
                name="BIA: Get Process"
            )

    @task(15)
    def view_audits(self):
        """View compliance audits"""
        self.client.get(
            f"{self.compliance_service}/api/v1/audits",
            headers=DEV_USER_HEADER,
            name="Compliance: List Audits"
        )

    @task(15)
    def view_strategies(self):
        """View planning strategies"""
        self.client.get(
            f"{self.planning_service}/api/v1/strategies",
            headers=DEV_USER_HEADER,
            name="Planning: List Strategies"
        )

    @task(15)
    def view_plans(self):
        """View plans"""
        self.client.get(
            f"{self.plans_service}/api/v1/plans",
            headers=DEV_USER_HEADER,
            name="Plans: List Plans"
        )

    @task(10)
    def create_bia_process(self):
        """Create BIA process"""
        process_data = {
            "name": f"Medium Process {random.randint(1000, 9999)}",
            "description": "Medium load test",
            "criticality": random.choice(["CRITICAL", "HIGH", "MEDIUM", "LOW"]),
            "rto_hours": random.randint(1, 24),
            "rpo_hours": random.randint(1, 12),
            "mtpd_hours": random.randint(4, 48),
            "financial_impact": {
                "1_hour": random.randint(10000, 100000),
                "4_hours": random.randint(40000, 400000),
                "24_hours": random.randint(100000, 1000000)
            }
        }

        response = self.client.post(
            f"{self.bia_service}/api/bia/processes",
            json=process_data,
            headers=DEV_USER_HEADER,
            name="BIA: Create Process"
        )

        if response.status_code == 201:
            self.process_ids.append(response.json()["id"])

    @task(8)
    def create_audit(self):
        """Create compliance audit"""
        audit_data = {
            "audit_type": "internal",
            "scope": f"Audit Scope {random.randint(1000, 9999)}",
            "auditor": "Medium Load User",
            "start_date": "2025-10-01",
            "end_date": "2025-10-15"
        }

        response = self.client.post(
            f"{self.compliance_service}/api/v1/audits",
            json=audit_data,
            headers=DEV_USER_HEADER,
            name="Compliance: Create Audit"
        )

        if response.status_code == 201:
            self.audit_ids.append(response.json()["id"])

    @task(8)
    def create_strategy(self):
        """Create planning strategy"""
        strategy_data = {
            "name": f"Strategy {random.randint(1000, 9999)}",
            "description": "Medium load test strategy",
            "objectives": ["Improve resilience", "Reduce RTO"],
            "scope": "IT Services",
            "timeline_months": random.randint(6, 24)
        }

        response = self.client.post(
            f"{self.planning_service}/api/v1/strategies",
            json=strategy_data,
            headers=DEV_USER_HEADER,
            name="Planning: Create Strategy"
        )

        if response.status_code == 201:
            self.strategy_ids.append(response.json()["id"])

    @task(8)
    def create_plan(self):
        """Create plan"""
        plan_data = {
            "name": f"Plan {random.randint(1000, 9999)}",
            "plan_type": random.choice(["incident_response", "disaster_recovery", "business_continuity"]),
            "description": "Medium load test plan",
            "scope": "IT Infrastructure",
            "activation_criteria": ["System outage", "Critical failure"]
        }

        response = self.client.post(
            f"{self.plans_service}/api/v1/plans",
            json=plan_data,
            headers=DEV_USER_HEADER,
            name="Plans: Create Plan"
        )

        if response.status_code == 201:
            self.plan_ids.append(response.json()["id"])

    @task(5)
    def update_process(self):
        """Update BIA process"""
        if self.process_ids:
            process_id = random.choice(self.process_ids)
            update_data = {
                "rto_hours": random.randint(1, 24),
                "rpo_hours": random.randint(1, 12)
            }

            self.client.put(
                f"{self.bia_service}/api/bia/processes/{process_id}",
                json=update_data,
                headers=DEV_USER_HEADER,
                name="BIA: Update Process"
            )

    @task(3)
    def bulk_create_processes(self):
        """Bulk create processes"""
        processes = []
        for i in range(5):
            processes.append({
                "name": f"Bulk Process {random.randint(1000, 9999)}",
                "description": "Bulk creation test",
                "criticality": random.choice(["HIGH", "MEDIUM"]),
                "rto_hours": 8,
                "rpo_hours": 4,
                "mtpd_hours": 16
            })

        response = self.client.post(
            f"{self.bia_service}/api/bia/processes/bulk",
            json={"processes": processes},
            headers=DEV_USER_HEADER,
            name="BIA: Bulk Create"
        )

        if response.status_code in [201, 207]:
            data = response.json()
            if "created" in data:
                for item in data["created"]:
                    self.process_ids.append(item["id"])

    @task(2)
    def generate_reports(self):
        """Generate reports"""
        report_types = [
            ("summary", "Summary Report"),
            ("critical-processes", "Critical Processes"),
            ("dependencies", "Dependencies Map")
        ]

        report_type, report_name = random.choice(report_types)
        self.client.get(
            f"{self.bia_service}/api/bia/reports/{report_type}",
            headers=DEV_USER_HEADER,
            name=f"BIA: {report_name}"
        )


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("=" * 80)
    print("MEDIUM LOAD TEST STARTED")
    print("Configuration: 50 users, 5/sec spawn rate, 10 min duration")
    print("Expected: ~10,000 total requests")
    print("=" * 80)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("=" * 80)
    print("MEDIUM LOAD TEST COMPLETED")
    stats = environment.stats
    print(f"Total Requests: {stats.total.num_requests}")
    print(f"Total Failures: {stats.total.num_failures}")
    print(f"Average Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"P95 Response Time: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"P99 Response Time: {stats.total.get_response_time_percentile(0.99):.2f}ms")
    print(f"Requests/sec: {stats.total.total_rps:.2f}")

    if stats.total.num_requests > 0:
        failure_rate = (stats.total.num_failures / stats.total.num_requests) * 100
        print(f"Failure Rate: {failure_rate:.2f}%")
    print("=" * 80)
