# BIA Service - Business Logic Documentation

**Version**: 1.0.0
**Date**: 2025-10-09
**ISO 22301 Clause**: 8.2.2

## Table of Contents

1. [Business Rules](#1-business-rules)
2. [Workflows](#2-workflows)
3. [State Machines](#3-state-machines)
4. [Calculation Logic](#4-calculation-logic)
5. [Decision Logic](#5-decision-logic)
6. [Validation Rules](#6-validation-rules)

## 1. Business Rules

### 1.1 Process Criticality Rules

**Rule BR-001: Criticality Classification**

Processes are classified into five criticality levels based on automated scoring:

| Criticality Level | Score Range | Description |
|-------------------|-------------|-------------|
| CRITICAL | >= 4.0 | Mission-critical, immediate impact |
| HIGH | 3.0 - 3.9 | High priority, significant impact |
| MEDIUM | 2.0 - 2.9 | Moderate priority, manageable impact |
| LOW | 1.0 - 1.9 | Low priority, minimal impact |
| NEGLIGIBLE | < 1.0 | Negligible impact |

**Rule BR-002: WHO Tier Override (Healthcare)**

For healthcare organizations with WHO tier classification enabled:
- Tier 1 processes → CRITICAL (regardless of calculated score)
- Tier 2 processes → HIGH minimum
- Tier 3 processes → MEDIUM minimum
- Tier 4 processes → No override

### 1.2 Recovery Objectives Rules

**Rule BR-003: RTO Validation**

```
RTO (Recovery Time Objective) must satisfy:
- RTO > 0
- RTO <= MTPD
- RTO should align with criticality:
  - CRITICAL: RTO <= 4 hours (recommendation)
  - HIGH: RTO <= 8 hours (recommendation)
  - MEDIUM: RTO <= 24 hours (recommendation)
```

**Rule BR-004: RPO Validation**

```
RPO (Recovery Point Objective) must satisfy:
- RPO > 0
- RPO <= RTO (data cannot be recovered slower than system)
- RPO should align with data criticality
```

**Rule BR-005: MTPD Validation**

```
MTPD (Maximum Tolerable Period of Disruption) must satisfy:
- MTPD > 0
- MTPD >= RTO
- MTPD should be based on business impact analysis
```

### 1.3 Financial Impact Rules

**Rule BR-006: Multi-Period Financial Impact**

Financial impact must be provided for all time periods:
- 1 hour
- 4 hours
- 8 hours
- 24 hours
- 1 week (168 hours)
- 1 month (720 hours)

**Rule BR-007: Impact Escalation**

```
Financial impact must be non-decreasing over time:
impact_1h <= impact_4h <= impact_8h <= impact_24h <= impact_1week <= impact_1month
```

### 1.4 Dependency Rules

**Rule BR-008: Dependency Criticality**

Dependency criticality rating (1-5 scale):
- 5: Critical - process cannot operate without it
- 4: High - significant degradation without it
- 3: Medium - partial functionality without it
- 2: Low - minor impact without it
- 1: Negligible - minimal impact without it

**Rule BR-009: Circular Dependency Detection**

The system should detect and warn about circular dependencies:
```
If Process A depends on Process B (upstream)
AND Process B depends on Process A (upstream)
THEN warn "Circular dependency detected"
```

### 1.5 Resource Requirements Rules

**Rule BR-010: Minimum Staff Levels**

Minimum staff requirements must be specified for:
- Normal operations
- Peak period operations
- Recovery operations

**Rule BR-011: Key Personnel Identification**

Critical processes (criticality >= HIGH) must identify:
- Minimum 2 key personnel roles
- Backup personnel for each role

## 2. Workflows

### 2.1 BIA Process Creation Workflow

```
┌─────────────────────────────────────────────────────────┐
│ 1. User submits BIA process creation request            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Validate JWT token and extract tenant_id            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Validate request data (Pydantic)                    │
│    - Required fields present                            │
│    - Data types correct                                 │
│    - Enums valid                                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Apply business rule validation                      │
│    - RTO <= MTPD                                        │
│    - RPO <= RTO                                         │
│    - Financial impact escalation                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 5. Calculate criticality score                         │
│    - Base score from criticality enum                   │
│    - WHO tier override (if applicable)                  │
│    - Financial impact factor                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 6. Insert into database (transaction)                  │
│    - bia_processes table                                │
│    - bia_dependencies table (if dependencies exist)     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 7. Publish event to EventBus                           │
│    - Event: bcm.bia.started                             │
│    - Payload: {process_id, tenant_id, criticality}      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 8. If criticality >= CRITICAL                          │
│    - Publish: bcm.bia.critical_process_identified       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 9. Invalidate cache                                    │
│    - Clear list cache for tenant                        │
│    - Clear summary report cache                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 10. Return created BIAProcess to client                │
└─────────────────────────────────────────────────────────┘
```

### 2.2 AI RTO Suggestion Workflow

```
┌─────────────────────────────────────────────────────────┐
│ 1. User requests AI RTO suggestion for process         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Fetch process from database                         │
│    - Verify tenant access                               │
│    - Check process exists                               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Extract process characteristics                     │
│    - Criticality level                                  │
│    - Financial impact                                   │
│    - Industry type                                      │
│    - Operational impact                                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Call AI Orchestration Service                       │
│    - Endpoint: /ai/suggest-rto                          │
│    - Payload: process characteristics                   │
│    - Timeout: 2 seconds                                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 5. Parse AI response                                   │
│    - Extract RTO/RPO/MTPD values                        │
│    - Extract reasoning                                  │
│    - Extract confidence score                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 6. Apply rule-based fallback (if AI fails)            │
│    - CRITICAL: RTO=2h, RPO=1h, MTPD=4h                 │
│    - HIGH: RTO=4h, RPO=2h, MTPD=8h                      │
│    - MEDIUM: RTO=8h, RPO=4h, MTPD=24h                   │
│    - LOW: RTO=24h, RPO=8h, MTPD=48h                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 7. Add industry benchmarks                             │
│    - Lookup industry-specific RTO standards             │
│    - Add benchmark context to response                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 8. Generate alternative scenarios                      │
│    - Conservative (lower RTO)                           │
│    - Balanced (recommended)                             │
│    - Cost-optimized (higher RTO)                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 9. Return AIRTOSuggestion to client                    │
└─────────────────────────────────────────────────────────┘
```

## 3. State Machines

### 3.1 BIA Process Status State Machine

```
┌─────────┐
│ DRAFT   │ ← Initial state when created
└────┬────┘
     │
     │ User starts working on BIA
     ▼
┌──────────────┐
│ IN_PROGRESS  │
└────┬─────────┘
     │
     │ All required fields filled + validation passed
     ▼
┌──────────┐
│COMPLETED │ ← Terminal state
└──────────┘

State Transitions:
- DRAFT → IN_PROGRESS: Automatic when user starts editing
- IN_PROGRESS → COMPLETED: Via POST /processes/{id}/complete
- IN_PROGRESS → DRAFT: Manual revert (if needed)
- COMPLETED → IN_PROGRESS: Cannot revert (data integrity)

Validation Rules per State:
- DRAFT: No validation required
- IN_PROGRESS: Partial validation (warnings only)
- COMPLETED: Full validation required (all business rules)
```

### 3.2 Dependency Resolution State Machine

```
┌─────────────┐
│ IDENTIFIED  │ ← Dependency discovered/added
└──────┬──────┘
       │
       │ Validate dependency exists
       ▼
┌─────────────┐
│  VALIDATED  │
└──────┬──────┘
       │
       │ Link to process
       ▼
┌─────────────┐
│   LINKED    │ ← Active dependency
└──────┬──────┘
       │
       │ Dependency removed or process deleted
       ▼
┌─────────────┐
│  ARCHIVED   │ ← Historical record
└─────────────┘
```

## 4. Calculation Logic

### 4.1 Criticality Score Calculation

```python
def calculate_criticality_score(process: BIAProcess) -> float:
    """
    Calculate automated criticality score (0-5 scale)

    Factors:
    1. Base criticality level (enum value)
    2. Financial impact (normalized)
    3. WHO tier (healthcare override)
    4. Regulatory impact
    5. Reputational impact
    """

    # Base score from criticality enum
    base_score_map = {
        "critical": 5.0,
        "high": 4.0,
        "medium": 3.0,
        "low": 2.0,
        "negligible": 1.0
    }
    base_score = base_score_map[process.criticality]

    # Financial impact factor (0-1 scale)
    max_impact = 10_000_000  # $10M baseline
    financial_factor = min(
        process.financial_impact.get("24_hours", 0) / max_impact,
        1.0
    )

    # Regulatory impact factor (0-1 scale)
    regulatory_map = {
        "critical": 1.0,
        "severe": 0.8,
        "high": 0.6,
        "moderate": 0.4,
        "low": 0.2
    }
    regulatory_factor = regulatory_map.get(
        process.regulatory_impact,
        0.0
    )

    # Calculate weighted score
    score = (
        base_score * 0.5 +           # 50% weight
        financial_factor * 5 * 0.3 + # 30% weight
        regulatory_factor * 5 * 0.2  # 20% weight
    )

    # WHO tier override (healthcare only)
    if process.who_tier:
        tier_minimum_score = {
            "tier_1": 5.0,  # Critical
            "tier_2": 4.0,  # High
            "tier_3": 3.0,  # Medium
            "tier_4": 2.0   # Low
        }
        min_score = tier_minimum_score.get(process.who_tier, 0)
        score = max(score, min_score)

    return round(score, 2)
```

### 4.2 Financial Impact Calculation

```python
def calculate_total_financial_impact(
    process: BIAProcess,
    disruption_hours: float
) -> float:
    """
    Calculate financial impact for specific disruption duration

    Uses interpolation between defined time periods
    """
    impact = process.financial_impact

    # Define time periods in hours
    periods = {
        1: impact.get("1_hour", 0),
        4: impact.get("4_hours", 0),
        8: impact.get("8_hours", 0),
        24: impact.get("24_hours", 0),
        168: impact.get("1_week", 0),
        720: impact.get("1_month", 0)
    }

    # Find surrounding time periods
    sorted_periods = sorted(periods.keys())

    if disruption_hours <= sorted_periods[0]:
        return periods[sorted_periods[0]]

    if disruption_hours >= sorted_periods[-1]:
        return periods[sorted_periods[-1]]

    # Linear interpolation between periods
    for i in range(len(sorted_periods) - 1):
        lower = sorted_periods[i]
        upper = sorted_periods[i + 1]

        if lower <= disruption_hours <= upper:
            # Interpolate
            ratio = (disruption_hours - lower) / (upper - lower)
            impact_lower = periods[lower]
            impact_upper = periods[upper]
            return impact_lower + (impact_upper - impact_lower) * ratio

    return 0.0
```

### 4.3 Dependency Graph Depth Calculation

```python
def calculate_dependency_depth(
    process_id: int,
    dependency_map: Dict[int, List[int]],
    visited: Set[int] = None
) -> int:
    """
    Calculate maximum dependency chain depth (upstream)

    Used to identify deepest dependencies for planning
    """
    if visited is None:
        visited = set()

    if process_id in visited:
        return 0  # Circular dependency

    visited.add(process_id)

    dependencies = dependency_map.get(process_id, [])

    if not dependencies:
        return 0

    max_depth = 0
    for dep_id in dependencies:
        depth = calculate_dependency_depth(
            dep_id,
            dependency_map,
            visited.copy()
        )
        max_depth = max(max_depth, depth + 1)

    return max_depth
```

## 5. Decision Logic

### 5.1 AI vs Rule-Based Decision

```python
def decide_rto_suggestion_method(
    ai_available: bool,
    ai_confidence: float,
    process_complexity: str
) -> str:
    """
    Decide whether to use AI or rule-based RTO suggestion

    Returns: "ai" | "rule_based" | "hybrid"
    """

    # Always use rules if AI unavailable
    if not ai_available:
        return "rule_based"

    # Use AI for complex processes with high confidence
    if process_complexity == "complex" and ai_confidence > 0.8:
        return "ai"

    # Use rules for simple processes
    if process_complexity == "simple":
        return "rule_based"

    # Use hybrid approach for medium complexity
    if ai_confidence > 0.6:
        return "hybrid"  # AI suggestion + rule validation
    else:
        return "rule_based"
```

### 5.2 Criticality Escalation Decision

```python
def should_escalate_to_critical(process: BIAProcess) -> bool:
    """
    Decide if process should be escalated to CRITICAL

    Escalation triggers:
    - Financial impact > $1M at 24 hours
    - WHO Tier 1 (healthcare)
    - Regulatory impact = critical
    - Patient safety impact = critical
    """

    # Financial threshold
    if process.financial_impact.get("24_hours", 0) > 1_000_000:
        return True

    # Healthcare critical service
    if process.who_tier == "tier_1":
        return True

    # Regulatory requirement
    if process.regulatory_impact == "critical":
        return True

    # Patient safety (healthcare only)
    if process.patient_safety_impact == "critical":
        return True

    return False
```

## 6. Validation Rules

### 6.1 Input Validation Rules

| Field | Validation Rule |
|-------|----------------|
| name | Required, 1-500 characters |
| tenant_id | Required, valid tenant format |
| criticality | Required, valid enum value |
| rto_hours | Required, > 0, <= mtpd_hours |
| rpo_hours | Required, > 0, <= rto_hours |
| mtpd_hours | Required, > 0, >= rto_hours |
| financial_impact | Required, all periods present, non-decreasing |
| dependencies | Optional, max 50 per process |
| industry | Required, valid enum value |

### 6.2 Business Validation Rules

```python
class BIABusinessValidator:
    """
    Business rule validation for BIA processes
    """

    @staticmethod
    def validate_recovery_objectives(
        rto: float,
        rpo: float,
        mtpd: float
    ) -> List[str]:
        """Validate RTO/RPO/MTPD relationships"""
        errors = []

        if rpo > rto:
            errors.append("RPO cannot exceed RTO")

        if rto > mtpd:
            errors.append("RTO cannot exceed MTPD")

        if mtpd < rto:
            errors.append("MTPD must be at least equal to RTO")

        return errors

    @staticmethod
    def validate_financial_impact(
        impact: Dict[str, float]
    ) -> List[str]:
        """Validate financial impact escalation"""
        errors = []

        periods = [
            "1_hour", "4_hours", "8_hours",
            "24_hours", "1_week", "1_month"
        ]

        # Check all periods present
        for period in periods:
            if period not in impact:
                errors.append(f"Missing financial impact for {period}")

        # Check non-decreasing
        values = [impact.get(p, 0) for p in periods]
        for i in range(len(values) - 1):
            if values[i] > values[i + 1]:
                errors.append(
                    f"Financial impact must not decrease over time"
                )
                break

        return errors
```

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-09
**Approved By**: AI Platform Team
