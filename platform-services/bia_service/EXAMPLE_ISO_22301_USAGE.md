# ISO 22301:2019 Enhanced BIA Fields - Usage Examples

## Overview
This document demonstrates how to use the new ISO 22301 Clause 8.2.2 compliant fields added to the BIA module.

## Example 1: Basic BIA with ISO 22301 Fields

```python
from models.domain import BIAProcessCreate, CriticalityLevel
from models.enums import IndustryType

# Create a comprehensive BIA process with ISO 22301 fields
process = BIAProcessCreate(
    tenant_id="hospital-123",
    name="Patient Registration",
    description="Hospital patient registration and admission process",
    department="Patient Services",
    process_owner="Jane Smith",
    criticality=CriticalityLevel.HIGH,
    industry=IndustryType.HEALTHCARE,

    # Recovery Time Objectives
    rto_hours=2,
    rpo_hours=1,
    mtpd_hours=4,

    # Financial Impact
    financial_impact={
        "1_hour": 5000,
        "4_hours": 20000,
        "8_hours": 50000,
        "24_hours": 150000
    },

    # NEW: ISO 22301 Compliance Fields
    compliance_objective="Ensure patient data availability and registration continuity per HIPAA and Joint Commission requirements",

    legal_regulatory_requirements=[
        "HIPAA - Health Insurance Portability and Accountability Act",
        "Joint Commission Standards",
        "State Healthcare Licensing Requirements"
    ],

    personnel_requirements={
        "roles": ["Patient Registrar", "Admissions Nurse", "IT Support"],
        "min_staff": 2,
        "skills": ["EMR training", "HIPAA certification", "Customer service"],
        "cross_training": "All staff must be cross-trained on manual registration"
    },

    facility_requirements={
        "locations": ["Main Hospital Lobby", "Emergency Department"],
        "space": "Registration desk with 3 workstations",
        "equipment": ["Computers", "Badge printers", "Phone systems"],
        "backup_location": "Temporary registration area in cafeteria"
    },

    technology_requirements={
        "systems": ["EMR System (Epic)", "Patient Portal", "Insurance Verification"],
        "applications": ["Registration Module", "ID Badge System"],
        "data": ["Patient demographics", "Insurance information", "Medical history"],
        "network": "High-speed internet required"
    },

    information_requirements={
        "documents": ["Patient consent forms", "Insurance forms", "Privacy notices"],
        "data_sources": ["EMR database", "Insurance eligibility API"],
        "records": ["Registration logs", "Visit history"]
    },

    recovery_strategies=[
        {
            "strategy": "manual_registration",
            "description": "Paper-based registration forms",
            "cost": 0,
            "rto": 0.5,
            "capacity": 60
        },
        {
            "strategy": "backup_site",
            "description": "Secondary registration area with laptops",
            "cost": 5000,
            "rto": 2,
            "capacity": 100
        },
        {
            "strategy": "mobile_registration",
            "description": "Tablet-based registration at bedside",
            "cost": 3000,
            "rto": 1,
            "capacity": 80
        }
    ],

    alternative_procedures=[
        "Use paper registration forms with carbon copies",
        "Phone-based registration for scheduled appointments",
        "Temporary registration with follow-up data entry",
        "Emergency fast-track registration for critical patients"
    ],

    workaround_capacity=60.0,  # 60% of normal capacity with manual processes

    upstream_processes=[
        "Appointment Scheduling",
        "Insurance Pre-Authorization",
        "Patient Portal Account Creation"
    ],

    downstream_processes=[
        "Clinical Assessment",
        "Laboratory Orders",
        "Medication Administration",
        "Billing and Claims Processing"
    ],

    critical_suppliers=[
        {
            "name": "Epic Systems",
            "service": "EMR System Support",
            "rto": 4,
            "contact": "support@epic.com",
            "sla": "24/7 critical support"
        },
        {
            "name": "Badge Printer Vendor",
            "service": "ID Badge Printing System",
            "rto": 24,
            "contact": "support@badgevendor.com"
        }
    ],

    minimum_resource_level={
        "staff": 2,
        "systems": ["EMR (read-only mode)", "Paper forms"],
        "space": "1 registration desk",
        "equipment": ["1 computer", "Paper forms", "Pens"]
    },

    peak_periods=[
        {
            "period": "morning_hours",
            "time": "7:00 AM - 11:00 AM",
            "criticality": 5,
            "volume": "80% of daily registrations"
        },
        {
            "period": "month_end",
            "time": "Last 3 days of month",
            "criticality": 4,
            "volume": "Insurance renewals spike"
        }
    ],

    seasonality="Flu season (October-March) increases volume by 30%",

    bia_completion_date="2025-10-03T10:00:00",
    bia_assessor="John Doe, BCM Manager",
    bia_reviewer="Sarah Johnson, Compliance Officer",
    next_review_date="2026-04-03T10:00:00"  # 6-month review cycle
)
```

## Example 2: Minimal BIA (Backward Compatible)

```python
# Old-style BIA creation still works - new fields are optional
minimal_process = BIAProcessCreate(
    tenant_id="company-456",
    name="Email Service",
    criticality=CriticalityLevel.MODERATE,
    rto_hours=4,
    rpo_hours=2,
    mtpd_hours=8
)
# All ISO 22301 fields will default to None/empty
```

## Example 3: Updating Existing BIA with ISO Fields

```python
# Add ISO 22301 fields to existing BIA via update endpoint
updates = {
    "compliance_objective": "Maintain communication capabilities per SOX requirements",
    "recovery_strategies": [
        {
            "strategy": "cloud_failover",
            "cost": 10000,
            "rto": 1,
            "capacity": 100
        }
    ],
    "bia_completion_date": datetime.now(),
    "bia_assessor": "Compliance Team"
}
```

## Example 4: ISO Compliance Validation

```python
from models.domain import ProcessStatus

# When marking a BIA as COMPLETED, the validator checks for key ISO fields
process = BIAProcess(
    # ... basic fields ...
    status=ProcessStatus.COMPLETED,

    # These fields are validated when status = COMPLETED:
    compliance_objective="...",      # Required
    recovery_strategies=[...],       # Required
    bia_completion_date=datetime.now(),  # Required
    bia_assessor="John Doe"         # Required
)

# If any required field is missing, a warning is logged:
# "BIA process 123 marked complete but missing ISO fields: ['compliance_objective', 'recovery_strategies']"
```

## Field Categories and ISO 22301 Mapping

### 1. Compliance Tracking (Clause 8.2.2.a)
- `compliance_objective` - Why this process matters
- `legal_regulatory_requirements` - Specific mandates

### 2. Resource Requirements (Clause 8.2.2.c)
- `personnel_requirements` - People needed
- `facility_requirements` - Physical locations/equipment
- `technology_requirements` - Systems and applications
- `information_requirements` - Data and documents

### 3. Recovery Strategies (Clause 8.2.2.d)
- `recovery_strategies` - How to recover
- `alternative_procedures` - Workarounds
- `workaround_capacity` - Capability with alternatives

### 4. Dependencies (Clause 8.2.2.b)
- `upstream_processes` - Inputs
- `downstream_processes` - Outputs
- `critical_suppliers` - External dependencies

### 5. Operating Characteristics
- `minimum_resource_level` - Bare minimum to operate
- `peak_periods` - Critical operating times
- `seasonality` - Variations

### 6. Assessment Workflow
- `bia_completion_date` - When completed
- `bia_assessor` - Who performed
- `bia_reviewer` - Who reviewed
- `next_review_date` - When to review again

## Database Schema

All fields are stored in PostgreSQL with proper data types:
- Text fields: `compliance_objective`, `seasonality`, `bia_assessor`, `bia_reviewer`
- JSON fields: All complex objects (lists, dicts)
- DateTime fields: `bia_completion_date`, `next_review_date`
- Float fields: `workaround_capacity`

## API Response Example

```json
{
  "id": 123,
  "tenant_id": "hospital-123",
  "name": "Patient Registration",
  "criticality": "high",
  "rto_hours": 2,
  "rpo_hours": 1,
  "mtpd_hours": 4,

  "compliance_objective": "Ensure patient data availability per HIPAA",
  "legal_regulatory_requirements": ["HIPAA", "Joint Commission"],

  "personnel_requirements": {
    "roles": ["Registrar", "Nurse"],
    "min_staff": 2
  },

  "recovery_strategies": [
    {
      "strategy": "manual_registration",
      "cost": 0,
      "rto": 0.5
    }
  ],

  "upstream_processes": ["Appointment Scheduling"],
  "downstream_processes": ["Clinical Assessment"],

  "bia_completion_date": "2025-10-03T10:00:00",
  "bia_assessor": "John Doe, BCM Manager"
}
```

## Benefits

1. **Full ISO 22301 Compliance**: Meets all Clause 8.2.2 requirements
2. **Backward Compatible**: Existing BIAs continue to work
3. **Comprehensive Documentation**: All recovery information in one place
4. **Audit Trail**: Track who assessed, when, and next review date
5. **Operational Insight**: Peak periods and seasonality for planning
6. **Dependency Mapping**: Full upstream/downstream visibility
