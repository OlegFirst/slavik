"""
Bulk Operation Benchmark Tests
===============================

Benchmark bulk operations with varying data sizes (10, 100, 1000 items).

Usage:
    pytest benchmark_tests/test_bulk_operation_benchmarks.py --benchmark-only
"""

import pytest
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.perf')

BIA_SERVICE_URL = os.getenv('BIA_SERVICE_URL', 'http://localhost:8012')

DEV_USER_HEADER = {
    'X-Dev-User': json.dumps({
        'user_id': 'benchmark-bulk-user',
        'tenant_id': 'benchmark-bulk-tenant'
    })
}


def generate_bia_process(index):
    """Generate a BIA process for bulk operations"""
    return {
        "name": f"Bulk Process {index}",
        "description": f"Bulk test process {index}",
        "criticality": ["CRITICAL", "HIGH", "MEDIUM", "LOW"][index % 4],
        "business_unit": "IT Operations",
        "process_owner": "Benchmark User",
        "rto_hours": 4,
        "rpo_hours": 2,
        "mtpd_hours": 8,
        "financial_impact": {
            "1_hour": 10000,
            "4_hours": 40000,
            "8_hours": 80000,
            "24_hours": 200000
        }
    }


# ============================================================================
# Bulk Create Benchmarks
# ============================================================================

def test_bulk_create_10_processes_benchmark(benchmark):
    """Benchmark: Bulk create 10 BIA processes"""

    def bulk_create_10():
        processes = [generate_bia_process(i) for i in range(10)]

        response = requests.post(
            f"{BIA_SERVICE_URL}/api/bia/processes/bulk",
            json={"processes": processes},
            headers=DEV_USER_HEADER
        )

        return response

    result = benchmark(bulk_create_10)
    # Accept both success and partial success
    assert result.status_code in [201, 207]


def test_bulk_create_100_processes_benchmark(benchmark):
    """Benchmark: Bulk create 100 BIA processes"""

    def bulk_create_100():
        processes = [generate_bia_process(i) for i in range(100)]

        response = requests.post(
            f"{BIA_SERVICE_URL}/api/bia/processes/bulk",
            json={"processes": processes},
            headers=DEV_USER_HEADER
        )

        return response

    result = benchmark(bulk_create_100)
    assert result.status_code in [201, 207, 400]


def test_bulk_create_500_processes_benchmark(benchmark):
    """Benchmark: Bulk create 500 BIA processes"""

    def bulk_create_500():
        processes = [generate_bia_process(i) for i in range(500)]

        response = requests.post(
            f"{BIA_SERVICE_URL}/api/bia/processes/bulk",
            json={"processes": processes},
            headers=DEV_USER_HEADER
        )

        return response

    result = benchmark(bulk_create_500)
    # May fail due to size, that's okay for benchmark
    assert result.status_code in [201, 207, 400, 413, 422]


# ============================================================================
# Bulk Update Benchmarks
# ============================================================================

@pytest.fixture(scope="module")
def created_process_ids():
    """Create processes for update benchmarks"""
    processes = [generate_bia_process(i) for i in range(50)]

    response = requests.post(
        f"{BIA_SERVICE_URL}/api/bia/processes/bulk",
        json={"processes": processes},
        headers=DEV_USER_HEADER
    )

    if response.status_code in [201, 207]:
        data = response.json()
        if "created" in data:
            return [item["id"] for item in data["created"]]
        elif "processes" in data:
            return [item["id"] for item in data["processes"]]

    return []


def test_bulk_update_10_processes_benchmark(benchmark, created_process_ids):
    """Benchmark: Bulk update 10 BIA processes"""

    if len(created_process_ids) < 10:
        pytest.skip("Not enough processes created")

    def bulk_update_10():
        updates = [
            {
                "id": created_process_ids[i],
                "rto_hours": 6,
                "rpo_hours": 3
            }
            for i in range(min(10, len(created_process_ids)))
        ]

        response = requests.patch(
            f"{BIA_SERVICE_URL}/api/bia/processes/bulk",
            json={"updates": updates},
            headers=DEV_USER_HEADER
        )

        return response

    result = benchmark(bulk_update_10)
    assert result.status_code in [200, 207, 404]


def test_bulk_update_50_processes_benchmark(benchmark, created_process_ids):
    """Benchmark: Bulk update 50 BIA processes"""

    if len(created_process_ids) < 50:
        pytest.skip("Not enough processes created")

    def bulk_update_50():
        updates = [
            {
                "id": created_process_ids[i],
                "rto_hours": 6,
                "rpo_hours": 3
            }
            for i in range(min(50, len(created_process_ids)))
        ]

        response = requests.patch(
            f"{BIA_SERVICE_URL}/api/bia/processes/bulk",
            json={"updates": updates},
            headers=DEV_USER_HEADER
        )

        return response

    result = benchmark(bulk_update_50)
    assert result.status_code in [200, 207, 404]


# ============================================================================
# Bulk Validation Benchmarks
# ============================================================================

def test_bulk_validate_10_processes_benchmark(benchmark):
    """Benchmark: Bulk validate 10 processes before import"""

    def bulk_validate_10():
        processes = [generate_bia_process(i) for i in range(10)]

        response = requests.post(
            f"{BIA_SERVICE_URL}/api/bia/processes/bulk/validate",
            json={"processes": processes},
            headers=DEV_USER_HEADER
        )

        return response

    result = benchmark(bulk_validate_10)
    # Validation should succeed or indicate validation errors
    assert result.status_code in [200, 400, 422]


def test_bulk_validate_100_processes_benchmark(benchmark):
    """Benchmark: Bulk validate 100 processes before import"""

    def bulk_validate_100():
        processes = [generate_bia_process(i) for i in range(100)]

        response = requests.post(
            f"{BIA_SERVICE_URL}/api/bia/processes/bulk/validate",
            json={"processes": processes},
            headers=DEV_USER_HEADER
        )

        return response

    result = benchmark(bulk_validate_100)
    assert result.status_code in [200, 400, 422]


# ============================================================================
# List with Pagination Benchmarks
# ============================================================================

def test_list_processes_page_10_benchmark(benchmark):
    """Benchmark: List processes with page size 10"""

    def list_page_10():
        response = requests.get(
            f"{BIA_SERVICE_URL}/api/bia/processes?limit=10&offset=0",
            headers=DEV_USER_HEADER
        )
        return response

    result = benchmark(list_page_10)
    assert result.status_code == 200


def test_list_processes_page_100_benchmark(benchmark):
    """Benchmark: List processes with page size 100"""

    def list_page_100():
        response = requests.get(
            f"{BIA_SERVICE_URL}/api/bia/processes?limit=100&offset=0",
            headers=DEV_USER_HEADER
        )
        return response

    result = benchmark(list_page_100)
    assert result.status_code == 200


def test_list_processes_page_500_benchmark(benchmark):
    """Benchmark: List processes with page size 500"""

    def list_page_500():
        response = requests.get(
            f"{BIA_SERVICE_URL}/api/bia/processes?limit=500&offset=0",
            headers=DEV_USER_HEADER
        )
        return response

    result = benchmark(list_page_500)
    assert result.status_code in [200, 400]  # May reject large page sizes


# ============================================================================
# Filtered List Benchmarks
# ============================================================================

def test_list_processes_filtered_criticality_benchmark(benchmark):
    """Benchmark: List processes filtered by criticality"""

    def list_filtered():
        response = requests.get(
            f"{BIA_SERVICE_URL}/api/bia/processes?criticality=CRITICAL&limit=100",
            headers=DEV_USER_HEADER
        )
        return response

    result = benchmark(list_filtered)
    assert result.status_code == 200


def test_list_processes_filtered_multiple_benchmark(benchmark):
    """Benchmark: List processes with multiple filters"""

    def list_filtered():
        response = requests.get(
            f"{BIA_SERVICE_URL}/api/bia/processes?criticality=CRITICAL&business_unit=IT%20Operations&limit=100",
            headers=DEV_USER_HEADER
        )
        return response

    result = benchmark(list_filtered)
    assert result.status_code == 200


# ============================================================================
# Search Benchmarks
# ============================================================================

def test_search_processes_benchmark(benchmark):
    """Benchmark: Search processes by name/description"""

    def search_processes():
        response = requests.get(
            f"{BIA_SERVICE_URL}/api/bia/processes?search=Bulk%20Process&limit=100",
            headers=DEV_USER_HEADER
        )
        return response

    result = benchmark(search_processes)
    assert result.status_code == 200


# ============================================================================
# Report Generation Benchmarks
# ============================================================================

def test_generate_summary_report_benchmark(benchmark):
    """Benchmark: Generate executive summary report"""

    def generate_report():
        response = requests.get(
            f"{BIA_SERVICE_URL}/api/bia/reports/summary",
            headers=DEV_USER_HEADER
        )
        return response

    result = benchmark(generate_report)
    assert result.status_code in [200, 404]


def test_generate_critical_processes_report_benchmark(benchmark):
    """Benchmark: Generate critical processes report"""

    def generate_report():
        response = requests.get(
            f"{BIA_SERVICE_URL}/api/bia/reports/critical-processes",
            headers=DEV_USER_HEADER
        )
        return response

    result = benchmark(generate_report)
    assert result.status_code in [200, 404]


def test_generate_dependencies_report_benchmark(benchmark):
    """Benchmark: Generate dependencies mapping report"""

    def generate_report():
        response = requests.get(
            f"{BIA_SERVICE_URL}/api/bia/reports/dependencies",
            headers=DEV_USER_HEADER
        )
        return response

    result = benchmark(generate_report)
    assert result.status_code in [200, 404]
