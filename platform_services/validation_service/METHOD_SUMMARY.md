# KPI Service and Audit Service - Method Summary

## KPI Service Methods (12 total)

### Public Methods (9)

| Method | Type | Parameters | Returns | Description |
|--------|------|------------|---------|-------------|
| `create_kpi` | async | kpi_data: Dict | KPIDB | Create new KPI with threshold validation |
| `record_measurement` | async | kpi_id, value, measured_by, [optional params] | KPIMeasurementDB | Record measurement, update status, create alerts |
| `get_kpi_trend` | async | kpi_id, period_days=90 | Dict | Get trend analysis with measurements |
| `get_dashboard` | async | tenant_id | Dict | Get KPI dashboard summary with status breakdown |
| `create_alert` | async | kpi, value, severity | KPIAlertDB | Create threshold breach alert |
| `acknowledge_alert` | async | alert_id, user_id, notes | KPIAlertDB | Acknowledge KPI alert with notes |
| `list_kpis` | async | tenant_id, category_id, status | List[KPIDB] | List KPIs with optional filters |
| `get_kpi` | async | kpi_id | Optional[KPIDB] | Get single KPI by ID |
| `update_kpi` | async | kpi_id, updates | KPIDB | Update KPI with threshold validation |

### Private Methods (3)

| Method | Type | Parameters | Returns | Description |
|--------|------|------------|---------|-------------|
| `_validate_thresholds` | sync | kpi_data | None | Validate threshold configuration based on direction |
| `_update_kpi_trend` | async | kpi_id | None | Update KPI trend from recent measurements |
| `_generate_alert_message` | sync | kpi, value, severity | str | Generate contextual alert message |

---

## Audit Service Methods (14 total)

### Public Methods (13)

| Method | Type | Parameters | Returns | Description |
|--------|------|------------|---------|-------------|
| `create_audit` | async | audit_data: Dict | AuditPlanDB | Create audit plan with scope validation |
| `start_fieldwork` | async | audit_id | AuditPlanDB | Start audit with workflow validation |
| `complete_fieldwork` | async | audit_id | AuditPlanDB | Complete fieldwork with validation |
| `draft_report` | async | audit_id | AuditPlanDB | Move to report draft status |
| `add_finding` | async | audit_id, finding_data | AuditFindingDB | Add finding with auto-CAPA for major findings |
| `generate_report` | async | audit_id | Dict | Generate comprehensive report with ISO analysis |
| `close_audit` | async | audit_id | AuditPlanDB | Close audit after reporting |
| `issue_report` | async | audit_id, report_content | AuditPlanDB | Issue audit report with validation |
| `list_audits` | async | tenant_id, status, audit_type | List[AuditPlanDB] | List audits with optional filters |
| `get_audit` | async | audit_id | Optional[AuditPlanDB] | Get single audit by ID |
| `get_audit_findings` | async | audit_id | List[AuditFindingDB] | Get all findings for an audit |
| `update_audit` | async | audit_id, updates | AuditPlanDB | Update audit details |
| `get_audit_statistics` | async | tenant_id, from_date, to_date | Dict | Get audit statistics for period |

### Private Methods (1)

| Method | Type | Parameters | Returns | Description |
|--------|------|------------|---------|-------------|
| `_auto_create_capa_for_finding` | async | audit, finding | CAPADB | Auto-create CAPA for major findings |

---

## Workflow Integration

### KPI Service Workflow Calls

| Workflow Function | Source | Purpose |
|-------------------|--------|---------|
| `calculate_kpi_status()` | workflows/kpi_calculations.py | Calculate performance status from thresholds |
| `calculate_kpi_trend()` | workflows/kpi_calculations.py | Analyze trend direction from measurements |
| `get_kpi_summary()` | workflows/kpi_calculations.py | Generate KPI summary statistics |

### Audit Service Workflow Calls

| Workflow Function | Source | Purpose |
|-------------------|--------|---------|
| `can_start_audit()` | workflows/audit_workflow.py | Validate audit can start |
| `can_complete_fieldwork()` | workflows/audit_workflow.py | Validate fieldwork completion |
| `can_issue_report()` | workflows/audit_workflow.py | Validate report can be issued |

---

## Repository Integration

### KPI Service Repository Calls

| Repository Method | Entity | Purpose |
|-------------------|--------|---------|
| `create_kpi()` | KPI | Create new KPI record |
| `get_kpi()` | KPI | Get KPI by ID |
| `get_kpi_by_code()` | KPI | Check for duplicate codes |
| `update_kpi()` | KPI | Update KPI fields |
| `list_kpis()` | KPI | List with filters |
| `create_kpi_measurement()` | KPIMeasurement | Record measurement |
| `get_kpi_measurements()` | KPIMeasurement | Get measurement history |
| `create_kpi_alert()` | KPIAlert | Create alert |
| `update_alert()` | KPIAlert | Update alert status |

### Audit Service Repository Calls

| Repository Method | Entity | Purpose |
|-------------------|--------|---------|
| `create_audit()` | AuditPlan | Create audit plan |
| `get_audit()` | AuditPlan | Get audit by ID |
| `update_audit()` | AuditPlan | Update audit fields |
| `list_audits()` | AuditPlan | List with filters |
| `create_audit_finding()` | AuditFinding | Create finding |
| `list_audit_findings()` | AuditFinding | Get audit findings |
| `create_capa()` | CAPA | Auto-create CAPA |

---

## Error Handling

### KPI Service Exceptions

| Validation | Error Message | Raised When |
|------------|---------------|-------------|
| Duplicate KPI | "KPI code {code} already exists" | Create with existing code |
| Invalid thresholds | "For higher_better KPIs: critical < warning < target" | Thresholds violate direction rules |
| KPI not found | "KPI not found" | Invalid kpi_id |
| Alert not found | "Alert not found" | Invalid alert_id |

### Audit Service Exceptions

| Validation | Error Message | Raised When |
|------------|---------------|-------------|
| Missing scope | "Audit scope must be defined" | Create without scope |
| Cannot start | "Lead auditor must be assigned before starting" | Start without auditor |
| Cannot complete | "Audit should have at least one finding" | Complete without findings |
| Wrong status | "Audit must be reported before closing" | Close before reporting |
| Audit not found | "Audit not found" | Invalid audit_id |

---

## Business Rules Implemented

### KPI Service Business Rules

1. **Threshold Validation:**
   - Higher Better: critical < warning < target
   - Lower Better: target < warning < critical
   - Target Value: tolerance-based evaluation

2. **Automatic Alert Creation:**
   - Warning status → Warning alert
   - Critical status → Critical alert
   - Alert includes current value, threshold, and target

3. **Trend Calculation:**
   - Requires minimum 2 measurements
   - Uses last 3 measurements for analysis
   - Compares recent average to older average
   - >5% change = improving/declining

4. **Status Calculation:**
   - Automatic on every measurement
   - Based on performance direction
   - Updates KPI current_status field

### Audit Service Business Rules

1. **Workflow State Transitions:**
   - PLANNED → IN_PROGRESS (via start_fieldwork)
   - IN_PROGRESS → FIELDWORK_COMPLETE (via complete_fieldwork)
   - FIELDWORK_COMPLETE → REPORT_DRAFT (via draft_report)
   - REPORT_DRAFT → REPORTED (via issue_report)
   - REPORTED → CLOSED (via close_audit)

2. **Finding Auto-Actions:**
   - Major findings → Auto-create CAPA
   - Update audit finding counts
   - Track corrective action requirements

3. **Report Generation:**
   - ISO clause coverage analysis
   - Findings grouped by severity
   - Statistics and summaries
   - CAPA tracking

4. **Validation Gates:**
   - Start: Must have auditor, scope, criteria
   - Complete: Must have findings
   - Issue: Must have report content, CAPAs for major findings

---

## Performance Characteristics

### KPI Service
- **Database Queries per Operation:**
  - create_kpi: 2 queries (check duplicate + create)
  - record_measurement: 4-5 queries (get KPI + create measurement + update KPI + optional alert + trend update)
  - get_kpi_trend: 2 queries (get KPI + get measurements)
  - get_dashboard: 1 query (list all KPIs)

### Audit Service
- **Database Queries per Operation:**
  - create_audit: 1 query (create)
  - start_fieldwork: 2 queries (get + update)
  - add_finding: 4 queries (get audit + create finding + update audit + optional CAPA)
  - generate_report: 2 queries (get audit + get findings)

---

## Code Statistics

| Metric | KPI Service | Audit Service | Total |
|--------|-------------|---------------|-------|
| Lines of Code | 452 | 521 | 973 |
| Public Methods | 9 | 13 | 22 |
| Private Methods | 3 | 1 | 4 |
| Total Methods | 12 | 14 | 26 |
| Imports | 8 modules | 8 modules | - |
| Classes | 1 | 1 | 2 |
| Documentation Lines | ~120 | ~140 | ~260 |
| Code-to-Doc Ratio | ~3.8:1 | ~3.7:1 | ~3.7:1 |

---

## Test Coverage Recommendations

### KPI Service Tests Needed
1. Threshold validation (all directions)
2. Measurement recording and status calculation
3. Alert creation on threshold breach
4. Trend analysis with various data patterns
5. Dashboard aggregation
6. Update validation

### Audit Service Tests Needed
1. Workflow state transitions
2. Validation gate enforcement
3. Finding addition and counting
4. Auto-CAPA creation
5. Report generation with ISO analysis
6. Statistics calculation

---

**Last Updated:** 2025-10-03  
**Status:** Production Ready  
**Review:** Pending
