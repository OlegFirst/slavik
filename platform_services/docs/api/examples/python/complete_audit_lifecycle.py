#!/usr/bin/env python3
"""
Example: Complete Audit Lifecycle using Compliance Service

This example demonstrates:
- Creating an audit
- Adding findings
- Creating nonconformities from findings
- Performing Root Cause Analysis (5 Whys method)
- Creating corrective actions (CAPA)
- Tracking to closure

ISO 22301:2019 Clause 9.2 - Internal Audit
ISO 22301:2019 Clause 10.1 - Nonconformity and Corrective Action
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import uuid

# Configuration
BASE_URL = "http://localhost:8014"
TENANT_ID = "tenant-123"
USER_ID = "user-456"

DEV_USER_HEADER = {
    "X-Dev-User": json.dumps({
        "sub": USER_ID,
        "tenant_id": TENANT_ID,
        "permissions": ["AUDIT_MANAGE", "NC_MANAGE", "COMPLIANCE_EDIT"]
    })
}


def create_internal_audit(audit_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Create an internal audit (ISO 9.2)"""
    url = f"{BASE_URL}/api/audit/audits"
    headers = {**DEV_USER_HEADER, "Content-Type": "application/json"}

    try:
        response = requests.post(url, json=audit_data, headers=headers)
        response.raise_for_status()
        audit = response.json()
        print(f"✅ Audit created: {audit.get('title')}")
        print(f"   ID: {audit.get('id')}")
        print(f"   Audit Date: {audit.get('audit_date')}")
        return audit
    except Exception as e:
        print(f"❌ Error creating audit: {e}")
        return None


def add_audit_finding(audit_id: str, finding_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Add finding to audit"""
    url = f"{BASE_URL}/api/audit/audits/{audit_id}/findings"
    headers = {**DEV_USER_HEADER, "Content-Type": "application/json"}

    try:
        response = requests.post(url, json=finding_data, headers=headers)
        response.raise_for_status()
        finding = response.json()
        print(f"   ✅ Finding added: {finding.get('finding_number')}")
        return finding
    except Exception as e:
        print(f"   ❌ Error adding finding: {e}")
        return None


def create_nonconformity(nc_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Create nonconformity from audit finding (ISO 10.1)"""
    url = f"{BASE_URL}/api/nonconformities"
    headers = {**DEV_USER_HEADER, "Content-Type": "application/json"}

    try:
        response = requests.post(url, json=nc_data, headers=headers)
        response.raise_for_status()
        nc = response.json()
        print(f"   ✅ Nonconformity created: {nc.get('nc_number')}")
        print(f"      ID: {nc.get('id')}")
        print(f"      Type: {nc.get('nc_type')}")
        return nc
    except Exception as e:
        print(f"   ❌ Error creating NC: {e}")
        return None


def start_rca(nc_id: str, method: str = "5_whys") -> Optional[Dict[str, Any]]:
    """Start Root Cause Analysis (ISO 10.1)"""
    url = f"{BASE_URL}/api/nonconformities/{nc_id}/rca/start"
    params = {
        "tenant_id": TENANT_ID,
        "rca_method": method,
        "rca_lead": "john.doe@company.com"
    }
    headers = {**DEV_USER_HEADER}

    try:
        response = requests.post(url, params=params, headers=headers)
        response.raise_for_status()
        rca = response.json()
        print(f"   ✅ RCA started using {method} method")
        return rca
    except Exception as e:
        print(f"   ❌ Error starting RCA: {e}")
        return None


def complete_rca(nc_id: str, rca_template: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Complete Root Cause Analysis with findings"""
    url = f"{BASE_URL}/api/nonconformities/{nc_id}/rca/complete"
    params = {
        "tenant_id": TENANT_ID,
        "actor_id": USER_ID
    }
    headers = {**DEV_USER_HEADER, "Content-Type": "application/json"}

    payload = {
        "completed_template": rca_template,
        "actor_id": USER_ID
    }

    try:
        response = requests.post(url, json=payload, params=params, headers=headers)
        response.raise_for_status()
        result = response.json()
        print(f"   ✅ RCA completed")
        print(f"      Root causes identified: {len(result.get('data', {}).get('root_causes', []))}")
        return result
    except Exception as e:
        print(f"   ❌ Error completing RCA: {e}")
        return None


def main():
    """Execute complete audit lifecycle"""
    print("=" * 80)
    print("BCM Platform - Complete Audit Lifecycle Example")
    print("ISO 22301:2019 Clauses 9.2, 10.1, 10.2")
    print("=" * 80)
    print()

    # Step 1: Create Internal Audit
    print("📋 Step 1: Create Internal Audit (ISO 9.2)")
    print("-" * 80)

    audit_date = datetime.now().isoformat()
    audit_data = {
        "tenant_id": TENANT_ID,
        "title": "Q1 2024 ISO 22301 Internal Audit",
        "audit_type": "INTERNAL",
        "scope": "Business continuity plans, procedures, and testing - Clauses 8.4, 8.5",
        "audit_date": audit_date,
        "lead_auditor": "sarah.jones@company.com",
        "audit_team": ["mike.brown@company.com", "lisa.white@company.com"],
        "departments": ["IT Operations", "Finance", "HR"],
        "iso_clauses": ["8.4", "8.5"]
    }

    audit = create_internal_audit(audit_data)
    if not audit:
        print("Failed to create audit. Exiting.")
        return

    audit_id = audit.get('id')
    print()

    # Step 2: Add Audit Findings
    print("🔍 Step 2: Add Audit Findings")
    print("-" * 80)

    findings = [
        {
            "finding_number": "F-2024-001",
            "clause_reference": "8.4.4",
            "finding_type": "MAJOR",
            "description": "BC plan for payment processing lacks defined procedure dependencies and execution order",
            "evidence": "Reviewed BC-PLAN-001 v2.1 - procedures listed without dependency mapping",
            "recommendation": "Update all BC plans to include procedure dependency graphs and execution sequences"
        },
        {
            "finding_number": "F-2024-002",
            "clause_reference": "8.5",
            "finding_type": "MINOR",
            "description": "BC plan testing schedule not documented for all critical processes",
            "evidence": "Testing log shows payment system not tested in last 6 months",
            "recommendation": "Establish and document testing schedule aligned with RTO requirements"
        }
    ]

    created_findings = []
    for finding_data in findings:
        finding = add_audit_finding(audit_id, finding_data)
        if finding:
            created_findings.append(finding)

    print()

    # Step 3: Create Nonconformity from Major Finding
    print("⚠️  Step 3: Create Nonconformity from Major Finding (ISO 10.1)")
    print("-" * 80)

    nc_data = {
        "tenant_id": TENANT_ID,
        "nc_number": "NC-2024-001",
        "nc_type": "MAJOR",
        "source": "AUDIT",
        "source_reference": f"Audit {audit_id} - Finding F-2024-001",
        "description": "BC plan for payment processing lacks defined procedure dependencies",
        "clause_affected": "8.4.4",
        "identified_by": "sarah.jones@company.com",
        "identified_date": datetime.now().isoformat(),
        "responsible_person": "jane.smith@company.com",
        "target_closure_date": (datetime.now() + timedelta(days=30)).isoformat()
    }

    nc = create_nonconformity(nc_data)
    if not nc:
        print("Failed to create NC. Exiting.")
        return

    nc_id = nc.get('id')
    print()

    # Step 4: Perform Root Cause Analysis (5 Whys)
    print("🎯 Step 4: Root Cause Analysis - 5 Whys Method (ISO 10.1)")
    print("-" * 80)

    rca_started = start_rca(nc_id, "5_whys")
    if not rca_started:
        print("Failed to start RCA. Exiting.")
        return

    # Complete the 5 Whys analysis
    rca_template = {
        "problem_statement": "BC plan lacks procedure dependency definitions",
        "why_1": "Procedures were added individually without considering dependencies",
        "why_2": "No standard template or checklist requires dependency documentation",
        "why_3": "BC plan template doesn't include dependency mapping section",
        "why_4": "Original ISO implementation focused on procedure content, not sequence",
        "why_5": "Gap in initial ISO 22301 training - Clause 8.4.4 dependencies not emphasized",
        "root_cause": "Incomplete ISO 22301 training and inadequate plan template design"
    }

    rca_result = complete_rca(nc_id, rca_template)
    if rca_result:
        print(f"   📌 Root Cause: {rca_template['root_cause']}")

    print()

    # Step 5: Create Corrective Actions (CAPA)
    print("🔧 Step 5: Corrective Actions (CAPA)")
    print("-" * 80)

    corrective_actions = [
        {
            "action_number": "CA-2024-001",
            "description": "Update BC plan template to include mandatory 'Procedure Dependencies' section",
            "responsible": "bcm-team@company.com",
            "target_date": (datetime.now() + timedelta(days=15)).isoformat(),
            "action_type": "CORRECTIVE"
        },
        {
            "action_number": "CA-2024-002",
            "description": "Provide supplemental training on ISO 22301 Clause 8.4.4 requirements",
            "responsible": "training@company.com",
            "target_date": (datetime.now() + timedelta(days=20)).isoformat(),
            "action_type": "CORRECTIVE"
        },
        {
            "action_number": "CA-2024-003",
            "description": "Review and update all existing BC plans with dependency mapping",
            "responsible": "jane.smith@company.com",
            "target_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "action_type": "CORRECTIVE"
        }
    ]

    for action in corrective_actions:
        print(f"   📋 {action['action_number']}: {action['description']}")
        print(f"      Responsible: {action['responsible']}")
        print(f"      Due: {action['target_date'][:10]}")
        print()

    # Step 6: Track to Closure
    print("✅ Step 6: Verification and Closure")
    print("-" * 80)
    print("   After corrective actions are implemented:")
    print("   1. Verify template updated with dependency section")
    print("   2. Confirm training completed and attendance recorded")
    print("   3. Audit all BC plans for dependency documentation")
    print("   4. Verify effectiveness in next internal audit")
    print("   5. Close NC and mark as 'RESOLVED'")
    print()

    # Summary
    print("=" * 80)
    print("📊 Audit Lifecycle Summary")
    print("=" * 80)
    print(f"Audit ID: {audit_id}")
    print(f"Findings: {len(created_findings)} ({sum(1 for f in findings if f['finding_type'] == 'MAJOR')} Major, {sum(1 for f in findings if f['finding_type'] == 'MINOR')} Minor)")
    print(f"Nonconformities: 1 (NC-2024-001)")
    print(f"Root Cause Method: 5 Whys")
    print(f"Corrective Actions: {len(corrective_actions)}")
    print(f"Expected Closure: 30 days")
    print()
    print("✅ Complete audit lifecycle demonstrated successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
