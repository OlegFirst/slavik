"""
Heavy Load Test Scenario
=========================

Simulates peak production load for stress testing.

Configuration:
- 100 concurrent users
- 10 users spawned per second
- 15 minute duration
- ~50,000 total target requests

Usage:
    locust -f load_tests/scenario_heavy.py --host=http://localhost --users 100 --spawn-rate 10 --run-time 15m
"""

from locust import HttpUser, task, between, events
import json
import random

DEV_USER_HEADER = {
    'X-Dev-User': json.dumps({
        'user_id': 'heavy-load-user',
        'tenant_id': 'heavy-load-tenant'
    })
}


class HeavyLoadUser(HttpUser):
    """Heavy load user simulating peak production traffic"""

    wait_time = between(0.5, 2)  # Fast interaction - peak load

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
        """Create initial test data"""
        # Create BIA processes
        for i in range(3):
            process_data = {
                "name": f"Heavy Load Process {random.randint(10000, 99999)}",
                "description": "Heavy load test",
                "criticality": "CRITICAL",
                "rto_hours": 2,
                "rpo_hours": 1,
                "mtpd_hours": 4
            }

            response = self.client.post(
                f"{self.bia_service}/api/bia/processes",
                json=process_data,
                headers=DEV_USER_HEADER
            )

            if response.status_code == 201:
                self.process_ids.append(response.json()["id"])

    @task(30)
    def view_bia_processes(self):
        """High frequency: View BIA processes"""
        self.client.get(
            f"{self.bia_service}/api/bia/processes?limit=50",
            headers=DEV_USER_HEADER,
            name="BIA: List Processes"
        )

    @task(25)
    def view_process_detail(self):
        """High frequency: View process details"""
        if self.process_ids:
            process_id = random.choice(self.process_ids)
            self.client.get(
                f"{self.bia_service}/api/bia/processes/{process_id}",
                headers=DEV_USER_HEADER,
                name="BIA: Get Process"
            )

    @task(20)
    def view_audits(self):
        """View compliance audits"""
        self.client.get(
            f"{self.compliance_service}/api/v1/audits?limit=50",
            headers=DEV_USER_HEADER,
            name="Compliance: List Audits"
        )

    @task(20)
    def view_strategies(self):
        """View planning strategies"""
        self.client.get(
            f"{self.planning_service}/api/v1/strategies?limit=50",
            headers=DEV_USER_HEADER,
            name="Planning: List Strategies"
        )

    @task(20)
    def view_plans(self):
        """View plans"""
        self.client.get(
            f"{self.plans_service}/api/v1/plans?limit=50",
            headers=DEV_USER_HEADER,
            name="Plans: List Plans"
        )

    @task(15)
    def create_bia_process(self):
        """Create BIA process"""
        process_data = {
            "name": f"Heavy Process {random.randint(10000, 99999)}",
            "description": "Heavy load test process",
            "criticality": random.choice(["CRITICAL", "HIGH", "MEDIUM"]),
            "business_unit": random.choice(["IT", "Finance", "Operations", "HR"]),
            "process_owner": f"User {random.randint(1, 100)}",
            "rto_hours": random.randint(1, 24),
            "rpo_hours": random.randint(1, 12),
            "mtpd_hours": random.randint(4, 48),
            "financial_impact": {
                "1_hour": random.randint(10000, 200000),
                "4_hours": random.randint(40000, 800000),
                "8_hours": random.randint(80000, 1600000),
                "24_hours": random.randint(200000, 4000000)
            },
            "dependencies": [
                {
                    "type": "technology",
                    "name": f"System {random.randint(1, 50)}",
                    "criticality": random.randint(1, 5)
                }
            ]
        }

        response = self.client.post(
            f"{self.bia_service}/api/bia/processes",
            json=process_data,
            headers=DEV_USER_HEADER,
            name="BIA: Create Process"
        )

        if response.status_code == 201:
            self.process_ids.append(response.json()["id"])

    @task(12)
    def create_audit(self):
        """Create compliance audit"""
        audit_data = {
            "audit_type": random.choice(["internal", "external", "certification"]),
            "scope": f"Heavy Load Audit {random.randint(10000, 99999)}",
            "auditor": f"Auditor {random.randint(1, 20)}",
            "start_date": "2025-10-01",
            "end_date": "2025-10-30",
            "findings": []
        }

        response = self.client.post(
            f"{self.compliance_service}/api/v1/audits",
            json=audit_data,
            headers=DEV_USER_HEADER,
            name="Compliance: Create Audit"
        )

        if response.status_code == 201:
            self.audit_ids.append(response.json()["id"])

    @task(12)
    def create_strategy(self):
        """Create planning strategy"""
        strategy_data = {
            "name": f"Heavy Strategy {random.randint(10000, 99999)}",
            "description": "Heavy load test strategy",
            "objectives": [
                "Improve resilience",
                "Reduce RTO",
                "Enhance recovery capabilities"
            ],
            "scope": random.choice(["IT Services", "Business Operations", "Enterprise"]),
            "timeline_months": random.randint(12, 36)
        }

        response = self.client.post(
            f"{self.planning_service}/api/v1/strategies",
            json=strategy_data,
            headers=DEV_USER_HEADER,
            name="Planning: Create Strategy"
        )

        if response.status_code == 201:
            self.strategy_ids.append(response.json()["id"])

    @task(12)
    def create_plan(self):
        """Create plan"""
        plan_data = {
            "name": f"Heavy Plan {random.randint(10000, 99999)}",
            "plan_type": random.choice([
                "incident_response",
                "disaster_recovery",
                "business_continuity",
                "crisis_management"
            ]),
            "description": "Heavy load test plan",
            "scope": random.choice(["IT Infrastructure", "Business Operations", "Enterprise"]),
            "activation_criteria": [
                "System outage",
                "Critical failure",
                "Security breach"
            ],
            "procedures": [
                {
                    "name": f"Procedure {i}",
                    "step_number": i + 1,
                    "description": f"Step {i + 1} description",
                    "responsible_role": random.choice(["Manager", "Team Lead", "Specialist"]),
                    "estimated_duration_minutes": random.randint(15, 120)
                }
                for i in range(3)
            ]
        }

        response = self.client.post(
            f"{self.plans_service}/api/v1/plans",
            json=plan_data,
            headers=DEV_USER_HEADER,
            name="Plans: Create Plan"
        )

        if response.status_code == 201:
            self.plan_ids.append(response.json()["id"])

    @task(10)
    def update_process(self):
        """Update BIA process"""
        if self.process_ids:
            process_id = random.choice(self.process_ids)
            update_data = {
                "rto_hours": random.randint(1, 24),
                "rpo_hours": random.randint(1, 12),
                "mtpd_hours": random.randint(4, 48)
            }

            self.client.put(
                f"{self.bia_service}/api/bia/processes/{process_id}",
                json=update_data,
                headers=DEV_USER_HEADER,
                name="BIA: Update Process"
            )

    @task(8)
    def update_plan(self):
        """Update plan"""
        if self.plan_ids:
            plan_id = random.choice(self.plan_ids)
            update_data = {
                "description": f"Updated description {random.randint(1, 10000)}"
            }

            self.client.put(
                f"{self.plans_service}/api/v1/plans/{plan_id}",
                json=update_data,
                headers=DEV_USER_HEADER,
                name="Plans: Update Plan"
            )

    @task(5)
    def bulk_create_processes(self):
        """Bulk create processes"""
        processes = []
        for i in range(10):
            processes.append({
                "name": f"Bulk Heavy {random.randint(10000, 99999)}",
                "description": "Bulk creation under heavy load",
                "criticality": random.choice(["HIGH", "MEDIUM"]),
                "rto_hours": 8,
                "rpo_hours": 4,
                "mtpd_hours": 16
            })

        response = self.client.post(
            f"{self.bia_service}/api/bia/processes/bulk",
            json={"processes": processes},
            headers=DEV_USER_HEADER,
            name="BIA: Bulk Create (10)"
        )

        if response.status_code in [201, 207]:
            data = response.json()
            if "created" in data:
                for item in data["created"]:
                    self.process_ids.append(item["id"])

    @task(3)
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

    @task(2)
    def search_processes(self):
        """Search processes"""
        search_terms = ["Process", "Critical", "IT", "Finance", "Operations"]
        term = random.choice(search_terms)

        self.client.get(
            f"{self.bia_service}/api/bia/processes?search={term}&limit=50",
            headers=DEV_USER_HEADER,
            name="BIA: Search Processes"
        )


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("=" * 80)
    print("HEAVY LOAD TEST STARTED")
    print("Configuration: 100 users, 10/sec spawn rate, 15 min duration")
    print("Expected: ~50,000 total requests")
    print("WARNING: This is a heavy load test - monitor system resources")
    print("=" * 80)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("=" * 80)
    print("HEAVY LOAD TEST COMPLETED")
    stats = environment.stats
    print(f"Total Requests: {stats.total.num_requests}")
    print(f"Total Failures: {stats.total.num_failures}")
    print(f"Average Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"Median Response Time: {stats.total.get_response_time_percentile(0.50):.2f}ms")
    print(f"P95 Response Time: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"P99 Response Time: {stats.total.get_response_time_percentile(0.99):.2f}ms")
    print(f"Requests/sec: {stats.total.total_rps:.2f}")

    if stats.total.num_requests > 0:
        failure_rate = (stats.total.num_failures / stats.total.num_requests) * 100
        print(f"Failure Rate: {failure_rate:.2f}%")

        # Performance assessment
        p95 = stats.total.get_response_time_percentile(0.95)
        if p95 < 200:
            print("✅ Performance: EXCELLENT (P95 < 200ms)")
        elif p95 < 500:
            print("✅ Performance: GOOD (P95 < 500ms)")
        elif p95 < 1000:
            print("⚠️  Performance: ACCEPTABLE (P95 < 1000ms)")
        else:
            print("❌ Performance: POOR (P95 > 1000ms)")

    print("=" * 80)
