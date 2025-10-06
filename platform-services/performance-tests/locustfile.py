"""
Performance Testing Suite for BCM Platform
===========================================

Locust-based load testing for 4 microservices:
- BIA Service (Port 8012)
- Compliance Service (Port 8014)
- Planning Service (Port 8011)
- Plans Service (Port 8023)

Usage:
    locust -f locustfile.py --host=http://localhost
    locust -f locustfile.py --host=http://localhost --users 50 --spawn-rate 5
"""

import json
import random
import time
from locust import HttpUser, task, between, events
from locust.contrib.fasthttp import FastHttpUser
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data templates
BIA_PROCESS_TEMPLATE = {
    "name": "Process {id}",
    "description": "Critical business process for performance testing",
    "criticality": "CRITICAL",
    "business_unit": "IT Operations",
    "process_owner": "John Doe",
    "rto_hours": 4,
    "rpo_hours": 2,
    "mtpd_hours": 8,
    "financial_impact": {
        "1_hour": 50000,
        "4_hours": 200000,
        "8_hours": 500000,
        "24_hours": 1500000
    },
    "dependencies": [
        {"type": "technology", "name": "Database Server", "criticality": 5},
        {"type": "technology", "name": "Application Server", "criticality": 5}
    ]
}

COMPLIANCE_AUDIT_TEMPLATE = {
    "audit_type": "internal",
    "scope": "ISO 22301 Clause 8",
    "auditor": "Performance Test",
    "start_date": "2025-10-01",
    "end_date": "2025-10-15",
    "findings": []
}

COMPLIANCE_NC_TEMPLATE = {
    "nc_number": "NC-{id}",
    "title": "Non-conformity {id}",
    "description": "Test NC for performance testing",
    "severity": "major",
    "clause": "8.2.2",
    "root_cause_analysis": {
        "method": "5_whys",
        "root_cause": "Inadequate process documentation",
        "corrective_action": "Implement comprehensive documentation"
    }
}

PLANNING_STRATEGY_TEMPLATE = {
    "name": "Strategy {id}",
    "description": "BCM Strategy for performance testing",
    "objectives": ["Reduce RTO", "Improve resilience"],
    "scope": "IT Services",
    "timeline_months": 12
}

PLANNING_COST_BENEFIT_TEMPLATE = {
    "strategy_id": 1,
    "investment_cost": 100000,
    "annual_operational_cost": 20000,
    "risk_reduction_percentage": 30,
    "expected_incident_cost": 500000,
    "analysis_period_years": 3
}

PLANS_PLAN_TEMPLATE = {
    "name": "Plan {id}",
    "plan_type": "incident_response",
    "description": "Performance test plan",
    "scope": "IT Infrastructure",
    "activation_criteria": ["System outage", "Critical failure"],
    "procedures": [
        {
            "name": "Initial Response",
            "step_number": 1,
            "description": "Assess situation",
            "responsible_role": "Incident Manager",
            "estimated_duration_minutes": 15
        }
    ]
}


class BIAServiceUser(FastHttpUser):
    """Load test user for BIA Service"""

    host = "http://localhost:8012"
    wait_time = between(1, 3)

    def on_start(self):
        """Setup: Create test data"""
        self.process_ids = []
        # Create initial processes
        for i in range(3):
            process_data = BIA_PROCESS_TEMPLATE.copy()
            process_data["name"] = f"Process {random.randint(1000, 9999)}"

            with self.client.post(
                "/api/bia/processes",
                json=process_data,
                headers={"X-Dev-User": '{"user_id": "perf-test-user", "tenant_id": "perf-test-tenant"}'},
                catch_response=True
            ) as response:
                if response.status_code == 201:
                    self.process_ids.append(response.json()["id"])

    @task(10)
    def get_process_list(self):
        """GET /api/bia/processes - List all processes"""
        with self.client.get(
            "/api/bia/processes",
            headers={"X-Dev-User": '{"user_id": "perf-test-user", "tenant_id": "perf-test-tenant"}'},
            name="/api/bia/processes [LIST]",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed to list processes: {response.status_code}")

    @task(15)
    def get_process_detail(self):
        """GET /api/bia/processes/{id} - Get process details"""
        if self.process_ids:
            process_id = random.choice(self.process_ids)
            with self.client.get(
                f"/api/bia/processes/{process_id}",
                headers={"X-Dev-User": '{"user_id": "perf-test-user", "tenant_id": "perf-test-tenant"}'},
                name="/api/bia/processes/{id} [GET]",
                catch_response=True
            ) as response:
                if response.status_code != 200:
                    response.failure(f"Failed to get process: {response.status_code}")

    @task(5)
    def create_process(self):
        """POST /api/bia/processes - Create new process"""
        process_data = BIA_PROCESS_TEMPLATE.copy()
        process_data["name"] = f"Process {random.randint(1000, 9999)}"

        with self.client.post(
            "/api/bia/processes",
            json=process_data,
            headers={"X-Dev-User": '{"user_id": "perf-test-user", "tenant_id": "perf-test-tenant"}'},
            name="/api/bia/processes [CREATE]",
            catch_response=True
        ) as response:
            if response.status_code == 201:
                self.process_ids.append(response.json()["id"])
            else:
                response.failure(f"Failed to create process: {response.status_code}")

    @task(3)
    def update_process(self):
        """PUT /api/bia/processes/{id} - Update process"""
        if self.process_ids:
            process_id = random.choice(self.process_ids)
            update_data = {"rto_hours": random.randint(1, 24)}

            with self.client.put(
                f"/api/bia/processes/{process_id}",
                json=update_data,
                headers={"X-Dev-User": '{"user_id": "perf-test-user", "tenant_id": "perf-test-tenant"}'},
                name="/api/bia/processes/{id} [UPDATE]",
                catch_response=True
            ) as response:
                if response.status_code != 200:
                    response.failure(f"Failed to update process: {response.status_code}")

    @task(2)
    def ai_suggest_rto(self):
        """POST /api/bia/processes/{id}/suggest-rto - AI RTO suggestion"""
        if self.process_ids:
            process_id = random.choice(self.process_ids)

            with self.client.post(
                f"/api/bia/processes/{process_id}/suggest-rto",
                headers={"X-Dev-User": '{"user_id": "perf-test-user", "tenant_id": "perf-test-tenant"}'},
                name="/api/bia/processes/{id}/suggest-rto [AI]",
                catch_response=True
            ) as response:
                if response.status_code not in [200, 404]:
                    response.failure(f"AI suggestion failed: {response.status_code}")

    @task(1)
    def bulk_create_processes(self):
        """POST /api/bia/processes/bulk - Bulk create processes"""
        processes = []
        for i in range(10):
            process = BIA_PROCESS_TEMPLATE.copy()
            process["name"] = f"Bulk Process {random.randint(1000, 9999)}"
            processes.append(process)

        with self.client.post(
            "/api/bia/processes/bulk",
            json={"processes": processes},
            headers={"X-Dev-User": '{"user_id": "perf-test-user", "tenant_id": "perf-test-tenant"}'},
            name="/api/bia/processes/bulk [CREATE]",
            catch_response=True
        ) as response:
            if response.status_code == 201:
                result = response.json()
                for item in result.get("created", []):
                    self.process_ids.append(item["id"])
            else:
                response.failure(f"Bulk create failed: {response.status_code}")


class ComplianceServiceUser(FastHttpUser):
    """Load test user for Compliance Service"""

    host = "http://localhost:8014"
    wait_time = between(1, 3)

    def on_start(self):
        """Setup: Create test data"""
        self.audit_ids = []
        self.nc_ids = []

    @task(10)
    def list_audits(self):
        """GET /api/v1/audits - List audits"""
        with self.client.get(
            "/api/v1/audits",
            headers={"X-Dev-User": '{"user_id": "perf-test-user", "tenant_id": "perf-test-tenant"}'},
            name="/api/v1/audits [LIST]",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed to list audits: {response.status_code}")

    @task(5)
    def create_audit(self):
        """POST /api/v1/audits - Create audit"""
        audit_data = COMPLIANCE_AUDIT_TEMPLATE.copy()
        audit_data["scope"] = f"Scope {random.randint(1000, 9999)}"

        with self.client.post(
            "/api/v1/audits",
            json=audit_data,
            headers={"X-Dev-User": '{"user_id": "perf-test-user", "tenant_id": "perf-test-tenant"}'},
            name="/api/v1/audits [CREATE]",
            catch_response=True
        ) as response:
            if response.status_code == 201:
                self.audit_ids.append(response.json()["id"])
            else:
                response.failure(f"Failed to create audit: {response.status_code}")

    @task(8)
    def get_audit_detail(self):
        """GET /api/v1/audits/{id} - Get audit details"""
        if self.audit_ids:
            audit_id = random.choice(self.audit_ids)
            with self.client.get(
                f"/api/v1/audits/{audit_id}",
                headers={"X-Dev-User": '{"user_id": "perf-test-user", "tenant_id": "perf-test-tenant"}'},
                name="/api/v1/audits/{id} [GET]",
                catch_response=True
            ) as response:
                if response.status_code != 200:
                    response.failure(f"Failed to get audit: {response.status_code}")

    @task(5)
    def create_nonconformity_with_rca(self):
        """POST /api/v1/nonconformities - Create NC with RCA"""
        nc_data = COMPLIANCE_NC_TEMPLATE.copy()
        nc_data["nc_number"] = f"NC-{random.randint(1000, 9999)}"

        with self.client.post(
            "/api/v1/nonconformities",
            json=nc_data,
            headers={"X-Dev-User": '{"user_id": "perf-test-user", "tenant_id": "perf-test-tenant"}'},
            name="/api/v1/nonconformities [CREATE]",
            catch_response=True
        ) as response:
            if response.status_code == 201:
                self.nc_ids.append(response.json()["id"])
            else:
                response.failure(f"Failed to create NC: {response.status_code}")

    @task(10)
    def list_nonconformities(self):
        """GET /api/v1/nonconformities - List NCs"""
        with self.client.get(
            "/api/v1/nonconformities",
            headers={"X-Dev-User": '{"user_id": "perf-test-user", "tenant_id": "perf-test-tenant"}'},
            name="/api/v1/nonconformities [LIST]",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed to list NCs: {response.status_code}")


class PlanningServiceUser(FastHttpUser):
    """Load test user for Planning Service"""

    host = "http://localhost:8011"
    wait_time = between(1, 3)

    def on_start(self):
        """Setup: Create test data"""
        self.strategy_ids = []

    @task(10)
    def list_strategies(self):
        """GET /api/v1/strategies - List strategies"""
        with self.client.get(
            "/api/v1/strategies",
            headers={"X-Dev-User": '{"user_id": "perf-test-user", "tenant_id": "perf-test-tenant"}'},
            name="/api/v1/strategies [LIST]",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed to list strategies: {response.status_code}")

    @task(5)
    def create_strategy(self):
        """POST /api/v1/strategies - Create strategy"""
        strategy_data = PLANNING_STRATEGY_TEMPLATE.copy()
        strategy_data["name"] = f"Strategy {random.randint(1000, 9999)}"

        with self.client.post(
            "/api/v1/strategies",
            json=strategy_data,
            headers={"X-Dev-User": '{"user_id": "perf-test-user", "tenant_id": "perf-test-tenant"}'},
            name="/api/v1/strategies [CREATE]",
            catch_response=True
        ) as response:
            if response.status_code == 201:
                self.strategy_ids.append(response.json()["id"])
            else:
                response.failure(f"Failed to create strategy: {response.status_code}")

    @task(8)
    def get_strategy_detail(self):
        """GET /api/v1/strategies/{id} - Get strategy details"""
        if self.strategy_ids:
            strategy_id = random.choice(self.strategy_ids)
            with self.client.get(
                f"/api/v1/strategies/{strategy_id}",
                headers={"X-Dev-User": '{"user_id": "perf-test-user", "tenant_id": "perf-test-tenant"}'},
                name="/api/v1/strategies/{id} [GET]",
                catch_response=True
            ) as response:
                if response.status_code != 200:
                    response.failure(f"Failed to get strategy: {response.status_code}")

    @task(3)
    def cost_benefit_analysis(self):
        """POST /api/v1/cost-benefit - Cost-benefit analysis"""
        analysis_data = PLANNING_COST_BENEFIT_TEMPLATE.copy()

        with self.client.post(
            "/api/v1/cost-benefit",
            json=analysis_data,
            headers={"X-Dev-User": '{"user_id": "perf-test-user", "tenant_id": "perf-test-tenant"}'},
            name="/api/v1/cost-benefit [ANALYZE]",
            catch_response=True
        ) as response:
            if response.status_code not in [200, 201]:
                response.failure(f"Cost-benefit analysis failed: {response.status_code}")


class PlansServiceUser(FastHttpUser):
    """Load test user for Plans Service"""

    host = "http://localhost:8023"
    wait_time = between(1, 3)

    def on_start(self):
        """Setup: Create test data"""
        self.plan_ids = []

    @task(10)
    def list_plans(self):
        """GET /api/v1/plans - List plans"""
        with self.client.get(
            "/api/v1/plans",
            headers={"X-Dev-User": '{"user_id": "perf-test-user", "tenant_id": "perf-test-tenant"}'},
            name="/api/v1/plans [LIST]",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed to list plans: {response.status_code}")

    @task(5)
    def create_plan(self):
        """POST /api/v1/plans - Create plan"""
        plan_data = PLANS_PLAN_TEMPLATE.copy()
        plan_data["name"] = f"Plan {random.randint(1000, 9999)}"

        with self.client.post(
            "/api/v1/plans",
            json=plan_data,
            headers={"X-Dev-User": '{"user_id": "perf-test-user", "tenant_id": "perf-test-tenant"}'},
            name="/api/v1/plans [CREATE]",
            catch_response=True
        ) as response:
            if response.status_code == 201:
                self.plan_ids.append(response.json()["id"])
            else:
                response.failure(f"Failed to create plan: {response.status_code}")

    @task(8)
    def get_plan_with_procedures(self):
        """GET /api/v1/plans/{id} - Get plan with procedures"""
        if self.plan_ids:
            plan_id = random.choice(self.plan_ids)
            with self.client.get(
                f"/api/v1/plans/{plan_id}",
                headers={"X-Dev-User": '{"user_id": "perf-test-user", "tenant_id": "perf-test-tenant"}'},
                name="/api/v1/plans/{id} [GET]",
                catch_response=True
            ) as response:
                if response.status_code != 200:
                    response.failure(f"Failed to get plan: {response.status_code}")

    @task(3)
    def update_plan(self):
        """PUT /api/v1/plans/{id} - Update plan"""
        if self.plan_ids:
            plan_id = random.choice(self.plan_ids)
            update_data = {"description": f"Updated description {random.randint(1, 1000)}"}

            with self.client.put(
                f"/api/v1/plans/{plan_id}",
                json=update_data,
                headers={"X-Dev-User": '{"user_id": "perf-test-user", "tenant_id": "perf-test-tenant"}'},
                name="/api/v1/plans/{id} [UPDATE]",
                catch_response=True
            ) as response:
                if response.status_code != 200:
                    response.failure(f"Failed to update plan: {response.status_code}")


# Event handlers for metrics collection
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Runs when load test starts"""
    logger.info("=" * 80)
    logger.info("BCM Platform Performance Test Started")
    logger.info("=" * 80)
    logger.info(f"Target Host: {environment.host}")
    logger.info(f"Number of Users: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Runs when load test stops"""
    logger.info("=" * 80)
    logger.info("BCM Platform Performance Test Completed")
    logger.info("=" * 80)

    # Log summary statistics
    stats = environment.stats
    logger.info(f"Total Requests: {stats.total.num_requests}")
    logger.info(f"Total Failures: {stats.total.num_failures}")
    logger.info(f"Average Response Time: {stats.total.avg_response_time:.2f}ms")
    logger.info(f"Requests/sec: {stats.total.total_rps:.2f}")

    if stats.total.num_requests > 0:
        failure_rate = (stats.total.num_failures / stats.total.num_requests) * 100
        logger.info(f"Failure Rate: {failure_rate:.2f}%")
