#!/usr/bin/env python3
"""
Example: Create BIA Process using the BCM Platform API

This example demonstrates:
- JWT authentication (or dev mode with X-Dev-User header)
- Creating a comprehensive BIA process
- Error handling
- Response parsing

ISO 22301:2019 Clause 8.2.2 - Business Impact Analysis
"""

import requests
import json
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8012"
TENANT_ID = "tenant-123"
USER_ID = "user-456"

# Development mode authentication (replace with JWT in production)
DEV_USER_HEADER = {
    "X-Dev-User": json.dumps({
        "sub": USER_ID,
        "tenant_id": TENANT_ID,
        "permissions": ["BIA_CREATE", "BIA_VIEW"]
    })
}

# For production, use JWT Bearer token:
# HEADERS = {
#     "Authorization": f"Bearer {jwt_token}",
#     "Content-Type": "application/json"
# }

def create_bia_process(process_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create a BIA process

    Args:
        process_data: BIA process data conforming to BIAProcessCreate schema

    Returns:
        Created BIA process or None if failed
    """
    url = f"{BASE_URL}/api/bia/processes"
    headers = {
        **DEV_USER_HEADER,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=process_data, headers=headers)
        response.raise_for_status()

        bia_process = response.json()
        print(f" BIA Process created successfully!")
        print(f"   ID: {bia_process.get('id')}")
        print(f"   Name: {bia_process.get('name')}")
        print(f"   Criticality: {bia_process.get('criticality')}")
        print(f"   RTO: {bia_process.get('rto_hours')} hours")

        return bia_process

    except requests.exceptions.HTTPError as e:
        print(f" HTTP Error: {e}")
        if e.response is not None:
            print(f"   Status Code: {e.response.status_code}")
            print(f"   Response: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f" Request Error: {e}")
    except Exception as e:
        print(f" Unexpected Error: {e}")

    return None


def get_bia_process(process_id: int) -> Optional[Dict[str, Any]]:
    """Get BIA process by ID"""
    url = f"{BASE_URL}/api/bia/processes/{process_id}"
    params = {"tenant_id": TENANT_ID}
    headers = {**DEV_USER_HEADER}

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f" Error fetching process: {e}")
        return None


def main():
    """Main execution"""
    print("=" * 60)
    print("BCM Platform - Create BIA Process Example")
    print("=" * 60)
    print()

    # Example 1: Critical Payment Processing System
    payment_process = {
        "tenant_id": TENANT_ID,
        "name": "Payment Processing System",
        "description": "Core payment processing for customer transactions",
        "department": "Finance Operations",
        "process_owner": "jane.smith@company.com",

        # Criticality Assessment (ISO 22301:2019 Clause 8.2.2)
        "criticality": "CRITICAL",
        "criticality_score": 5,

        # Recovery Objectives (Hours)
        "rto_hours": 2,   # Recovery Time Objective
        "rpo_hours": 1,   # Recovery Point Objective
        "mtpd_hours": 4,  # Maximum Tolerable Period of Disruption

        # Financial Impact over Time
        "financial_impact": {
            "1_hour": 50000,
            "4_hours": 200000,
            "8_hours": 500000,
            "24_hours": 1200000,
            "3_days": 3000000,
            "1_week": 5000000
        },

        # Operational Impact
        "operational_impact": {
            "1_hour": "Delayed transactions, customer complaints",
            "4_hours": "Major service disruption, regulatory breach risk",
            "24_hours": "Complete payment service failure, significant reputational damage"
        },

        # Dependencies
        "dependencies": [
            {
                "type": "technology",
                "name": "Payment Gateway API",
                "criticality": 5,
                "required": True
            },
            {
                "type": "technology",
                "name": "Database Cluster",
                "criticality": 5,
                "required": True
            },
            {
                "type": "people",
                "name": "Payment Operations Team",
                "criticality": 4,
                "required": True
            },
            {
                "type": "supplier",
                "name": "Payment Processor (Stripe)",
                "criticality": 5,
                "required": True
            }
        ],

        # Industry Context
        "industry": "FINANCIAL_SERVICES",
        "geographical_scope": "NATIONAL",

        # Impact Types
        "reputational_impact": "HIGH",
        "regulatory_impact": "HIGH",

        # ISO 22301 Compliance Fields
        "compliance_objective": "Maintain payment processing capability with <2hr RTO to meet regulatory requirements",
        "legal_regulatory_requirements": [
            "PCI-DSS - Payment Card Industry Data Security Standard",
            "SOX - Sarbanes-Oxley Act",
            "GDPR - Data protection for EU customers"
        ],

        # Resource Requirements
        "personnel_requirements": {
            "minimum_staff": 3,
            "critical_roles": ["Payment Ops Manager", "System Administrator", "DBA"],
            "backup_personnel": ["john.doe@company.com", "bob.smith@company.com"]
        },

        "technology_requirements": {
            "primary_systems": ["Payment Gateway", "Database", "Load Balancer"],
            "backup_systems": ["Hot Standby DB", "Failover Gateway"],
            "network_requirements": "Redundant network paths, minimum 1Gbps"
        },

        "facility_requirements": {
            "primary_location": "Main Data Center",
            "alternate_location": "DR Site - Cloud Region US-East",
            "workspace_needs": "Remote access capability for 5 team members"
        },

        # Recovery Strategy
        "recovery_strategy": {
            "approach": "Hot standby with automatic failover",
            "description": "Active-passive database replication with payment gateway load balancing",
            "estimated_cost": 500000,
            "implementation_timeline_days": 90
        },

        # Alternative Procedures
        "alternative_procedures": [
            {
                "name": "Manual Payment Processing",
                "description": "Process payments manually via backup terminal",
                "limitations": "Limited to 10 transactions/hour, no automated reconciliation",
                "activation_criteria": "If automated system unavailable for >1 hour"
            }
        ],

        # Peak Period Considerations
        "peak_period_rto_hours": 1,
        "peak_periods": ["End of month", "Black Friday", "Holiday season"]
    }

    print("Creating BIA Process: Payment Processing System")
    print("-" * 60)
    process = create_bia_process(payment_process)

    if process:
        print()
        print(" Process Details:")
        print(f"   Tenant: {process.get('tenant_id')}")
        print(f"   Industry: {process.get('industry')}")
        print(f"   Dependencies: {len(process.get('dependencies', []))}")
        print()

        # Fetch the created process to verify
        print("Verifying created process...")
        fetched = get_bia_process(process.get('id'))
        if fetched:
            print(" Process verified successfully!")

    print()
    print("=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
