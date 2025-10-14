"""
API Endpoint Benchmark Tests
=============================

Benchmark individual API endpoints for latency and throughput.
Measures P50, P95, P99 latency and requests per second.

Usage:
    pytest benchmark_tests/test_api_benchmarks.py --benchmark-only
    pytest benchmark_tests/test_api_benchmarks.py --benchmark-json=reports/benchmark_api.json
"""

import pytest
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.perf')

BIA_SERVICE_URL = os.getenv('BIA_SERVICE_URL', 'http://localhost:8012')
COMPLIANCE_SERVICE_URL = os.getenv('COMPLIANCE_SERVICE_URL', 'http://localhost:8014')
PLANNING_SERVICE_URL = os.getenv('PLANNING_SERVICE_URL', 'http://localhost:8011')
PLANS_SERVICE_URL = os.getenv('PLANS_SERVICE_URL', 'http://localhost:8023')

# Test headers
DEV_USER_HEADER = {
    'X-Dev-User': json.dumps({
        'user_id': 'benchmark-user',
        'tenant_id': 'benchmark-tenant'
    })
}


@pytest.fixture(scope="module")
def bia_process_id():
    """Create a BIA process for testing"""
    process_data = {
        "name": "Benchmark Process",
        "description": "Test process for benchmarking",
        "criticality": "CRITICAL",
        "rto_hours": 4,
        "rpo_hours": 2,
        "mtpd_hours": 8
    }

    response = requests.post(
        f"{BIA_SERVICE_URL}/api/bia/processes",
        json=process_data,
        headers=DEV_USER_HEADER
    )

    if response.status_code == 201:
        return response.json()["id"]
    return None


@pytest.fixture(scope="module")
def compliance_audit_id():
    """Create a compliance audit for testing"""
    audit_data = {
        "audit_type": "internal",
        "scope": "Benchmark Test",
        "auditor": "Benchmark User",
        "start_date": "2025-10-01",
        "end_date": "2025-10-15"
    }

    response = requests.post(
        f"{COMPLIANCE_SERVICE_URL}/api/v1/audits",
        json=audit_data,
        headers=DEV_USER_HEADER
    )

    if response.status_code == 201:
        return response.json()["id"]
    return None


@pytest.fixture(scope="module")
def planning_strategy_id():
    """Create a planning strategy for testing"""
    strategy_data = {
        "name": "Benchmark Strategy",
        "description": "Test strategy for benchmarking",
        "objectives": ["Test objective"],
        "scope": "IT",
        "timeline_months": 12
    }

    response = requests.post(
        f"{PLANNING_SERVICE_URL}/api/v1/strategies",
        json=strategy_data,
        headers=DEV_USER_HEADER
    )

    if response.status_code == 201:
        return response.json()["id"]
    return None


@pytest.fixture(scope="module")
def plans_plan_id():
    """Create a plan for testing"""
    plan_data = {
        "name": "Benchmark Plan",
        "plan_type": "incident_response",
        "description": "Test plan for benchmarking",
        "scope": "IT Infrastructure",
        "activation_criteria": ["Test criteria"]
    }

    response = requests.post(
        f"{PLANS_SERVICE_URL}/api/v1/plans",
        json=plan_data,
        headers=DEV_USER_HEADER
    )

    if response.status_code == 201:
        return response.json()["id"]
    return None


# ============================================================================
# BIA Service Benchmarks
# ============================================================================

def test_bia_list_processes_benchmark(benchmark):
    """Benchmark: List BIA processes"""

    def list_processes():
        response = requests.get(
            f"{BIA_SERVICE_URL}/api/bia/processes",
            headers=DEV_USER_HEADER
        )
        assert response.status_code == 200
        return response

    result = benchmark(list_processes)
    assert result.status_code == 200


def test_bia_get_process_benchmark(benchmark, bia_process_id):
    """Benchmark: Get single BIA process"""
    if not bia_process_id:
        pytest.skip("No BIA process created")

    def get_process():
        response = requests.get(
            f"{BIA_SERVICE_URL}/api/bia/processes/{bia_process_id}",
            headers=DEV_USER_HEADER
        )
        assert response.status_code == 200
        return response

    result = benchmark(get_process)
    assert result.status_code == 200


def test_bia_create_process_benchmark(benchmark):
    """Benchmark: Create BIA process"""
    process_data = {
        "name": "Benchmark Process Create",
        "description": "Test",
        "criticality": "CRITICAL",
        "rto_hours": 4,
        "rpo_hours": 2,
        "mtpd_hours": 8
    }

    def create_process():
        response = requests.post(
            f"{BIA_SERVICE_URL}/api/bia/processes",
            json=process_data,
            headers=DEV_USER_HEADER
        )
        # Note: May return 201 or error if duplicate
        return response

    result = benchmark(create_process)
    assert result.status_code in [201, 400, 409, 422]


def test_bia_update_process_benchmark(benchmark, bia_process_id):
    """Benchmark: Update BIA process"""
    if not bia_process_id:
        pytest.skip("No BIA process created")

    update_data = {"rto_hours": 6}

    def update_process():
        response = requests.put(
            f"{BIA_SERVICE_URL}/api/bia/processes/{bia_process_id}",
            json=update_data,
            headers=DEV_USER_HEADER
        )
        return response

    result = benchmark(update_process)
    assert result.status_code in [200, 404]


# ============================================================================
# Compliance Service Benchmarks
# ============================================================================

def test_compliance_list_audits_benchmark(benchmark):
    """Benchmark: List compliance audits"""

    def list_audits():
        response = requests.get(
            f"{COMPLIANCE_SERVICE_URL}/api/v1/audits",
            headers=DEV_USER_HEADER
        )
        assert response.status_code == 200
        return response

    result = benchmark(list_audits)
    assert result.status_code == 200


def test_compliance_get_audit_benchmark(benchmark, compliance_audit_id):
    """Benchmark: Get single audit"""
    if not compliance_audit_id:
        pytest.skip("No audit created")

    def get_audit():
        response = requests.get(
            f"{COMPLIANCE_SERVICE_URL}/api/v1/audits/{compliance_audit_id}",
            headers=DEV_USER_HEADER
        )
        return response

    result = benchmark(get_audit)
    assert result.status_code in [200, 404]


def test_compliance_create_audit_benchmark(benchmark):
    """Benchmark: Create audit"""
    audit_data = {
        "audit_type": "internal",
        "scope": "Benchmark Test",
        "auditor": "Benchmark User",
        "start_date": "2025-10-01",
        "end_date": "2025-10-15"
    }

    def create_audit():
        response = requests.post(
            f"{COMPLIANCE_SERVICE_URL}/api/v1/audits",
            json=audit_data,
            headers=DEV_USER_HEADER
        )
        return response

    result = benchmark(create_audit)
    assert result.status_code in [201, 400, 422]


# ============================================================================
# Planning Service Benchmarks
# ============================================================================

def test_planning_list_strategies_benchmark(benchmark):
    """Benchmark: List strategies"""

    def list_strategies():
        response = requests.get(
            f"{PLANNING_SERVICE_URL}/api/v1/strategies",
            headers=DEV_USER_HEADER
        )
        assert response.status_code == 200
        return response

    result = benchmark(list_strategies)
    assert result.status_code == 200


def test_planning_get_strategy_benchmark(benchmark, planning_strategy_id):
    """Benchmark: Get single strategy"""
    if not planning_strategy_id:
        pytest.skip("No strategy created")

    def get_strategy():
        response = requests.get(
            f"{PLANNING_SERVICE_URL}/api/v1/strategies/{planning_strategy_id}",
            headers=DEV_USER_HEADER
        )
        return response

    result = benchmark(get_strategy)
    assert result.status_code in [200, 404]


def test_planning_create_strategy_benchmark(benchmark):
    """Benchmark: Create strategy"""
    strategy_data = {
        "name": "Benchmark Strategy Create",
        "description": "Test",
        "objectives": ["Test"],
        "scope": "IT",
        "timeline_months": 12
    }

    def create_strategy():
        response = requests.post(
            f"{PLANNING_SERVICE_URL}/api/v1/strategies",
            json=strategy_data,
            headers=DEV_USER_HEADER
        )
        return response

    result = benchmark(create_strategy)
    assert result.status_code in [201, 400, 422]


# ============================================================================
# Plans Service Benchmarks
# ============================================================================

def test_plans_list_plans_benchmark(benchmark):
    """Benchmark: List plans"""

    def list_plans():
        response = requests.get(
            f"{PLANS_SERVICE_URL}/api/v1/plans",
            headers=DEV_USER_HEADER
        )
        assert response.status_code == 200
        return response

    result = benchmark(list_plans)
    assert result.status_code == 200


def test_plans_get_plan_benchmark(benchmark, plans_plan_id):
    """Benchmark: Get single plan"""
    if not plans_plan_id:
        pytest.skip("No plan created")

    def get_plan():
        response = requests.get(
            f"{PLANS_SERVICE_URL}/api/v1/plans/{plans_plan_id}",
            headers=DEV_USER_HEADER
        )
        return response

    result = benchmark(get_plan)
    assert result.status_code in [200, 404]


def test_plans_create_plan_benchmark(benchmark):
    """Benchmark: Create plan"""
    plan_data = {
        "name": "Benchmark Plan Create",
        "plan_type": "incident_response",
        "description": "Test",
        "scope": "IT Infrastructure",
        "activation_criteria": ["Test"]
    }

    def create_plan():
        response = requests.post(
            f"{PLANS_SERVICE_URL}/api/v1/plans",
            json=plan_data,
            headers=DEV_USER_HEADER
        )
        return response

    result = benchmark(create_plan)
    assert result.status_code in [201, 400, 422]


# ============================================================================
# Health Check Benchmarks
# ============================================================================

def test_bia_health_check_benchmark(benchmark):
    """Benchmark: BIA health check"""

    def health_check():
        response = requests.get(f"{BIA_SERVICE_URL}/health")
        assert response.status_code == 200
        return response

    result = benchmark(health_check)
    assert result.status_code == 200


def test_compliance_health_check_benchmark(benchmark):
    """Benchmark: Compliance health check"""

    def health_check():
        response = requests.get(f"{COMPLIANCE_SERVICE_URL}/health")
        assert response.status_code == 200
        return response

    result = benchmark(health_check)
    assert result.status_code == 200


def test_planning_health_check_benchmark(benchmark):
    """Benchmark: Planning health check"""

    def health_check():
        response = requests.get(f"{PLANNING_SERVICE_URL}/health")
        assert response.status_code == 200
        return response

    result = benchmark(health_check)
    assert result.status_code == 200


def test_plans_health_check_benchmark(benchmark):
    """Benchmark: Plans health check"""

    def health_check():
        response = requests.get(f"{PLANS_SERVICE_URL}/health")
        assert response.status_code == 200
        return response

    result = benchmark(health_check)
    assert result.status_code == 200
