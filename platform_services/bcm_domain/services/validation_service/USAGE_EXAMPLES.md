# KPI Service and Audit Service Usage Examples

This document provides comprehensive usage examples for the KPI Service and Audit Service implementations.

## KPI Service Usage

### 1. Create KPI Service Instance

```python
from repositories.repository import ValidationRepository
from services.kpi_service import KPIService
from models.domain import PerformanceDirection, MeasurementFrequency

# Initialize repository and service
repo = ValidationRepository(db_session)
kpi_service = KPIService(repo)
```

### 2. Create a New KPI

```python
# Example: Create RTO Achievement KPI
kpi_data = {
    "tenant_id": "acme-corp",
    "kpi_code": "RTO_ACHIEVEMENT",
    "kpi_name": "% RTO Objectives Achieved in Tests",
    "category_id": 1,
    "description": "Percentage of Recovery Time Objectives achieved during BC exercises",
    "objective": "Ensure 95% of critical processes meet RTO targets during testing",
    "measurement_unit": "%",
    "calculation_method": "(RTOs Met / Total RTOs Tested) * 100",
    "data_source": "Exercise results database",
    "target_value": 95.0,
    "warning_threshold": 85.0,
    "critical_threshold": 70.0,
    "performance_direction": PerformanceDirection.HIGHER_BETTER,
    "measurement_frequency": MeasurementFrequency.MONTHLY,
    "owner_id": "user-123",
    "owner_name": "Jane Smith",
    "iso_clause": "8.5"
}

try:
    kpi = await kpi_service.create_kpi(kpi_data)
    print(f"Created KPI: {kpi.id} - {kpi.kpi_name}")
except ValueError as e:
    print(f"Error: {e}")
```

### 3. Record KPI Measurement

```python
from models.domain import DataQuality, CollectionMethod

# Record a measurement
try:
    measurement = await kpi_service.record_measurement(
        kpi_id=kpi.id,
        value=92.5,
        measured_by="user-123",
        notes="Q1 2025 exercise results - 37 out of 40 RTOs met",
        data_quality=DataQuality.HIGH,
        collection_method=CollectionMethod.AUTOMATED
    )
    print(f"Recorded measurement: {measurement.value}% - Status: {measurement.status}")
except ValueError as e:
    print(f"Error: {e}")
```

### 4. Get KPI Trend Analysis

```python
# Get 90-day trend
trend_data = await kpi_service.get_kpi_trend(
    kpi_id=kpi.id,
    period_days=90
)

print(f"KPI: {trend_data['kpi_name']}")
print(f"Current Value: {trend_data['current_value']}%")
print(f"Status: {trend_data['current_status']}")
print(f"Trend: {trend_data['trend']}")
print(f"Target: {trend_data['target_value']}%")
print(f"Measurements in period: {trend_data['measurement_count']}")

for m in trend_data['measurements'][:5]:  # Show last 5
    print(f"  {m['measurement_date']}: {m['value']}% - {m['status']}")
```

### 5. Get KPI Dashboard

```python
# Get complete dashboard for tenant
dashboard = await kpi_service.get_dashboard(tenant_id="acme-corp")

print(f"Total KPIs: {dashboard['total_kpis']}")
print(f"Status Summary:")
print(f"  Excellent: {dashboard['status_summary']['excellent']}")
print(f"  Good: {dashboard['status_summary']['good']}")
print(f"  Warning: {dashboard['status_summary']['warning']}")
print(f"  Critical: {dashboard['status_summary']['critical']}")
print(f"  No Data: {dashboard['status_summary']['no_data']}")

print("\nKPI Details:")
for kpi in dashboard['kpis']:
    print(f"  {kpi['kpi_code']}: {kpi['current_value']} {kpi['measurement_unit']} - {kpi['status']}")
```

### 6. Handle KPI Alerts

```python
# Alerts are automatically created when thresholds are breached
# during record_measurement()

# Acknowledge an alert
alert = await kpi_service.acknowledge_alert(
    alert_id=1,
    user_id="user-123",
    notes="Root cause identified: test environment configuration issue. Corrective action initiated."
)
print(f"Alert acknowledged by {alert.acknowledged_by} at {alert.acknowledged_at}")
```

### 7. Update KPI Configuration

```python
# Update KPI thresholds
updates = {
    "target_value": 97.0,
    "warning_threshold": 90.0,
    "critical_threshold": 75.0
}

try:
    updated_kpi = await kpi_service.update_kpi(kpi_id=kpi.id, updates=updates)
    print(f"Updated KPI thresholds: Target={updated_kpi.target_value}%")
except ValueError as e:
    print(f"Error: {e}")
```

---

## Audit Service Usage

### 1. Create Audit Service Instance

```python
from repositories.repository import ValidationRepository
from services.audit_service import AuditService
from models.domain import AuditType

# Initialize repository and service
repo = ValidationRepository(db_session)
audit_service = AuditService(repo)
```

### 2. Create an Audit Plan

```python
from datetime import datetime, timedelta

# Create internal compliance audit
audit_data = {
    "tenant_id": "acme-corp",
    "audit_code": "AUD-2025-001",
    "audit_name": "ISO 22301 Internal Compliance Audit - Q1 2025",
    "description": "Comprehensive review of BCMS compliance with ISO 22301:2019",
    "audit_type": AuditType.COMPLIANCE,
    "audit_scope": "All BCMS processes across IT, Operations, and Customer Service departments",
    "iso_clauses_covered": [
        "4.1", "4.2", "4.3", "5.1", "5.2", "6.1", "6.2",
        "8.1", "8.2", "8.3", "8.4", "8.5",
        "9.1", "9.2", "9.3", "10.1", "10.2"
    ],
    "processes_covered": [
        "Business Impact Analysis",
        "Risk Assessment",
        "BC Strategy Development",
        "Exercise Program",
        "Incident Response"
    ],
    "planned_date": datetime(2025, 3, 15),
    "planned_duration_hours": 24.0,
    "lead_auditor": "user-456",
    "lead_auditor_name": "John Auditor",
    "audit_team": [
        {"user_id": "user-457", "name": "Sarah Reviewer", "role": "Auditor"},
        {"user_id": "user-458", "name": "Mike Inspector", "role": "Technical Specialist"}
    ],
    "audit_criteria": [
        "ISO 22301:2019 requirements",
        "Company BCMS policy v2.1",
        "BCI Good Practice Guidelines 2023"
    ],
    "checklist_items": [
        "Review BC Policy approval and communication",
        "Verify BIA documentation completeness",
        "Assess exercise program compliance",
        "Review incident response procedures"
    ]
}

try:
    audit = await audit_service.create_audit(audit_data)
    print(f"Created Audit: {audit.id} - {audit.audit_name}")
    print(f"Status: {audit.status}")
except ValueError as e:
    print(f"Error: {e}")
```

### 3. Start Audit Fieldwork

```python
# Start the audit (with workflow validation)
try:
    audit = await audit_service.start_fieldwork(audit_id=audit.id)
    print(f"Audit started: {audit.status}")
    print(f"Start date: {audit.actual_start_date}")
except ValueError as e:
    print(f"Cannot start audit: {e}")
```

### 4. Add Audit Findings

```python
from models.domain import FindingType, FindingSeverity

# Add a major finding
finding_data = {
    "tenant_id": "acme-corp",
    "finding_number": "F-001",
    "finding_type": FindingType.MAJOR_NONCONFORMITY,
    "severity": FindingSeverity.MAJOR,
    "iso_clause": "8.5",
    "title": "BC Plans Not Tested Annually",
    "description": (
        "During document review, it was found that 15 out of 42 business continuity plans "
        "have not been tested in the last 12 months, violating the company policy requirement "
        "for annual testing of all critical process BC plans."
    ),
    "evidence": (
        "Exercise database query results showing last test dates. "
        "Reviewed plans: CRM-BC-001 (last tested 18 months ago), "
        "ORDER-BC-003 (last tested 14 months ago), etc."
    ),
    "requirement": (
        "ISO 22301:2019 clause 8.5: The organization shall exercise and test its business "
        "continuity plans and procedures at planned intervals. Company Policy BCM-001 "
        "requires annual testing of all critical process BC plans."
    ),
    "corrective_action_required": True,
    "assigned_to": "user-789",
    "due_date": datetime.utcnow() + timedelta(days=30)
}

finding = await audit_service.add_finding(audit_id=audit.id, finding_data=finding_data)
print(f"Added finding: {finding.finding_number} - {finding.title}")
print(f"Severity: {finding.severity}")
print(f"CAPA Required: {finding.corrective_action_required}")

# Add a minor finding
minor_finding_data = {
    "tenant_id": "acme-corp",
    "finding_number": "F-002",
    "finding_type": FindingType.MINOR_NONCONFORMITY,
    "severity": FindingSeverity.MINOR,
    "iso_clause": "9.1",
    "title": "KPI Dashboard Not Updated Monthly",
    "description": "KPI dashboard shows last update was 6 weeks ago, not the required monthly frequency.",
    "evidence": "Dashboard timestamp: 2025-01-15. Current date: 2025-03-01.",
    "requirement": "Company procedure requires monthly KPI reporting.",
    "corrective_action_required": True,
    "assigned_to": "user-234",
    "due_date": datetime.utcnow() + timedelta(days=14)
}

minor_finding = await audit_service.add_finding(audit_id=audit.id, finding_data=minor_finding_data)
print(f"Added finding: {minor_finding.finding_number}")
```

### 5. Complete Fieldwork and Draft Report

```python
# Complete fieldwork
audit = await audit_service.complete_fieldwork(audit_id=audit.id)
print(f"Fieldwork completed: {audit.status}")

# Move to draft report
audit = await audit_service.draft_report(audit_id=audit.id)
print(f"Report drafting: {audit.status}")
```

### 6. Generate Audit Report

```python
# Generate comprehensive audit report
report = await audit_service.generate_report(audit_id=audit.id)

print(f"Audit Report: {report['audit']['audit_code']}")
print(f"Audit Type: {report['audit']['audit_type']}")
print(f"Lead Auditor: {report['audit']['lead_auditor']}")
print(f"\nScope:")
print(f"  ISO Clauses: {', '.join(report['scope']['iso_clauses'])}")
print(f"  Processes: {len(report['scope']['processes'])}")

print(f"\nFindings Summary:")
print(f"  Total Findings: {report['findings_summary']['total']}")
print(f"  Major Nonconformities: {report['findings_summary']['major_nonconformities']}")
print(f"  Minor Nonconformities: {report['findings_summary']['minor_nonconformities']}")
print(f"  Observations: {report['findings_summary']['observations']}")

print(f"\nISO Clause Analysis:")
for clause, analysis in report['iso_clause_analysis'].items():
    print(f"  Clause {clause}: {analysis['total']} findings (Major: {analysis['major']}, Minor: {analysis['minor']})")

print(f"\nDetailed Findings:")
for finding in report['findings']:
    print(f"  {finding['finding_number']}: {finding['title']}")
    print(f"    Severity: {finding['severity']}")
    print(f"    ISO Clause: {finding['iso_clause']}")
    print(f"    CA Required: {finding['corrective_action_required']}")

print(f"\nCorrective Actions:")
print(f"  Required: {report['corrective_actions']['required']}")
print(f"  Completed: {report['corrective_actions']['completed']}")
```

### 7. Issue and Close Audit

```python
# Issue the report
report_content = """
AUDIT REPORT: ISO 22301 Internal Compliance Audit - Q1 2025

EXECUTIVE SUMMARY:
The audit identified significant compliance gaps in BC plan testing and KPI monitoring.
Immediate corrective action is required to address major nonconformities.

SCOPE: All BCMS processes across IT, Operations, and Customer Service
FINDINGS: 2 Major, 3 Minor, 5 Observations
CONCLUSION: BCMS requires improvement to achieve full ISO 22301 compliance.

RECOMMENDATIONS:
1. Implement automated exercise scheduling system
2. Enhance KPI monitoring procedures
3. Conduct refresher training for BC plan owners
"""

audit = await audit_service.issue_report(
    audit_id=audit.id,
    report_content=report_content
)
print(f"Report issued: {audit.status}")
print(f"Report date: {audit.report_date}")

# Close the audit (after CAPAs are addressed)
audit = await audit_service.close_audit(audit_id=audit.id)
print(f"Audit closed: {audit.status}")
```

### 8. Get Audit Statistics

```python
from datetime import datetime

# Get audit statistics for Q1 2025
stats = await audit_service.get_audit_statistics(
    tenant_id="acme-corp",
    from_date=datetime(2025, 1, 1),
    to_date=datetime(2025, 3, 31)
)

print(f"Audit Statistics for Q1 2025:")
print(f"Total Audits: {stats['total_audits']}")
print(f"Completed: {stats['completed_audits']}")
print(f"Completion Rate: {stats['completion_rate']:.1f}%")
print(f"\nFindings:")
print(f"  Total: {stats['findings']['total']}")
print(f"  Major: {stats['findings']['major']}")
print(f"  Minor: {stats['findings']['minor']}")
print(f"  Observations: {stats['findings']['observations']}")
print(f"\nBy Type:")
for audit_type, count in stats['by_type'].items():
    print(f"  {audit_type}: {count}")
```

---

## Integration Examples

### Using Both Services Together

```python
# Example: Link KPI alerts to audit findings

# 1. KPI breach triggers investigation
kpi_trend = await kpi_service.get_kpi_trend(kpi_id=1, period_days=90)

if kpi_trend['current_status'] == 'critical':
    # 2. Create focused audit
    audit_data = {
        "tenant_id": "acme-corp",
        "audit_code": f"AUD-KPI-{kpi_trend['kpi_code']}",
        "audit_name": f"Investigation: {kpi_trend['kpi_name']} Critical Status",
        "audit_type": AuditType.PROCESS,
        "audit_scope": f"Root cause analysis for KPI {kpi_trend['kpi_code']} critical breach",
        "planned_date": datetime.utcnow(),
        "planned_duration_hours": 8.0,
        "lead_auditor": "user-999",
        "lead_auditor_name": "Incident Investigator"
    }

    audit = await audit_service.create_audit(audit_data)
    print(f"Created investigation audit: {audit.audit_code}")
```

### End-to-End Workflow

```python
async def complete_audit_cycle(tenant_id: str):
    """Complete audit lifecycle from planning to closure"""

    # 1. Create audit plan
    audit = await audit_service.create_audit({
        "tenant_id": tenant_id,
        "audit_code": "AUD-2025-DEMO",
        "audit_name": "Demo Audit",
        "audit_type": AuditType.COMPLIANCE,
        "audit_scope": "Demo scope",
        "planned_date": datetime.utcnow(),
        "planned_duration_hours": 8.0,
        "lead_auditor": "auditor-1",
        "lead_auditor_name": "Lead Auditor",
        "audit_criteria": ["ISO 22301:2019"]
    })

    # 2. Start fieldwork
    audit = await audit_service.start_fieldwork(audit.id)

    # 3. Add findings
    finding = await audit_service.add_finding(audit.id, {
        "tenant_id": tenant_id,
        "finding_number": "F-001",
        "finding_type": FindingType.OBSERVATION,
        "severity": FindingSeverity.OBSERVATION,
        "title": "Demo finding",
        "description": "Description",
        "evidence": "Evidence",
        "requirement": "Requirement"
    })

    # 4. Complete fieldwork
    audit = await audit_service.complete_fieldwork(audit.id)

    # 5. Draft report
    audit = await audit_service.draft_report(audit.id)

    # 6. Generate report
    report = await audit_service.generate_report(audit.id)

    # 7. Issue report
    audit = await audit_service.issue_report(audit.id, "Audit report content")

    # 8. Close audit
    audit = await audit_service.close_audit(audit.id)

    return audit, report
```

---

## Error Handling Examples

```python
# KPI Service Error Handling
try:
    kpi = await kpi_service.create_kpi(kpi_data)
except ValueError as e:
    if "already exists" in str(e):
        print("Duplicate KPI code - use different code")
    elif "threshold" in str(e):
        print("Invalid threshold configuration")
    else:
        print(f"Validation error: {e}")

# Audit Service Error Handling
try:
    audit = await audit_service.start_fieldwork(audit_id)
except ValueError as e:
    if "Lead auditor must be assigned" in str(e):
        print("Assign lead auditor before starting")
    elif "Audit scope must be defined" in str(e):
        print("Define audit scope before starting")
    else:
        print(f"Cannot start audit: {e}")
```

---

## Best Practices

### KPI Service
1. **Threshold Configuration**: Always validate thresholds match performance direction
2. **Regular Measurements**: Establish automated measurement collection where possible
3. **Alert Management**: Acknowledge alerts promptly with root cause analysis
4. **Trend Analysis**: Review trends monthly to identify declining performance early

### Audit Service
1. **Complete Planning**: Define scope, criteria, and team before starting
2. **Document Evidence**: Always include specific evidence for findings
3. **Workflow Compliance**: Follow the audit workflow states in order
4. **CAPA Integration**: Major findings automatically create CAPAs for tracking

### Integration
1. **KPI-Driven Audits**: Use KPI alerts to trigger focused process audits
2. **Audit-Based KPIs**: Create KPIs from recurring audit findings
3. **Continuous Improvement**: Link CAPA completion to KPI improvements
