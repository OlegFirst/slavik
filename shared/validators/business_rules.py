"""
Business Rule Validators
Domain-specific validation logic for BIA and Compliance modules
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


class BusinessValidationError(Exception):
    """Raised when business rule validation fails"""
    pass


class BusinessValidator:
    """Business rule validators for BIA and Compliance modules"""

    # =========================================================================
    # BIA MODULE VALIDATORS
    # =========================================================================

    @staticmethod
    def validate_recovery_objectives(
        rto_hours: int,
        rpo_hours: int,
        mtpd_hours: int,
        criticality: str
    ):
        """
        Validate RTO/RPO/MTPD relationships and criticality constraints

        Business Rules:
        - RPO <= RTO <= MTPD (basic sequence)
        - RTO must match criticality level:
          - CRITICAL: RTO <= 4h
          - HIGH: RTO <= 24h
          - MODERATE: RTO <= 72h
          - MINOR: RTO <= 168h (1 week)
          - LOW: RTO <= 720h (30 days)
        """

        # Basic sequence validation
        if not (rpo_hours <= rto_hours <= mtpd_hours):
            raise BusinessValidationError(
                f"Recovery objectives must follow: RPO ({rpo_hours}h) <= "
                f"RTO ({rto_hours}h) <= MTPD ({mtpd_hours}h)"
            )

        # Criticality constraints
        criticality_limits = {
            "CRITICAL": 4,
            "critical": 4,
            "HIGH": 24,
            "high": 24,
            "MODERATE": 72,
            "moderate": 72,
            "MINOR": 168,
            "minor": 168,
            "LOW": 720,
            "low": 720
        }

        max_rto = criticality_limits.get(criticality)
        if max_rto and rto_hours > max_rto:
            raise BusinessValidationError(
                f"RTO ({rto_hours}h) exceeds maximum for {criticality.upper()} "
                f"processes ({max_rto}h)"
            )

    @staticmethod
    def validate_financial_impact_timeline(
        financial_impact: Dict[str, float]
    ):
        """
        Validate financial impact increases over time

        Business Rule:
        - Impact must be monotonically increasing over time periods
        - 1_hour < 4_hours < 8_hours < 24_hours < 3_days < 1_week < 1_month
        """

        time_sequence = [
            "1_hour", "4_hours", "8_hours", "24_hours",
            "3_days", "1_week", "1_month"
        ]

        prev_value = 0
        prev_period = "start"

        for period in time_sequence:
            if period in financial_impact:
                current_value = financial_impact[period]
                if current_value < prev_value:
                    raise BusinessValidationError(
                        f"Financial impact must increase over time. "
                        f"{period} ({current_value}) < {prev_period} ({prev_value})"
                    )
                prev_value = current_value
                prev_period = period

    @staticmethod
    def validate_no_self_dependency(
        process_id: str,
        upstream: List[str],
        downstream: List[str],
        dependencies: List[Dict[str, Any]]
    ):
        """
        Prevent circular dependencies

        Business Rule:
        - A process cannot depend on itself (direct circular dependency)
        - This prevents infinite loops in dependency chains
        """

        all_deps = upstream + downstream

        # Add dependency IDs/names from dependency objects
        for dep in dependencies:
            dep_id = dep.get("id")
            dep_name = dep.get("name")
            if dep_id:
                all_deps.append(str(dep_id))
            if dep_name:
                all_deps.append(dep_name)

        if process_id in all_deps:
            raise BusinessValidationError(
                f"Process cannot depend on itself (circular dependency detected)"
            )

    @staticmethod
    def validate_critical_process_requirements(
        criticality: str,
        recovery_strategies: List[Dict[str, Any]],
        alternative_procedures: List[str],
        dependencies: List[Any]
    ):
        """
        Critical processes must have complete documentation

        Business Rules:
        - CRITICAL/HIGH processes must have:
          - At least one recovery strategy
          - At least one alternative procedure
          - Documented dependencies
        """

        if criticality.upper() in ["CRITICAL", "HIGH"]:
            if not recovery_strategies:
                raise BusinessValidationError(
                    f"{criticality.upper()} processes must have documented recovery strategies"
                )

            if not alternative_procedures:
                raise BusinessValidationError(
                    f"{criticality.upper()} processes must have alternative procedures"
                )

            if not dependencies:
                raise BusinessValidationError(
                    f"{criticality.upper()} processes must have documented dependencies"
                )

    @staticmethod
    def validate_workaround_capacity(
        workaround_capacity: Optional[float]
    ):
        """
        Validate workaround capacity is within reasonable bounds

        Business Rule:
        - Workaround capacity must be between 0% and 100%
        - Cannot exceed normal capacity
        """

        if workaround_capacity is not None:
            if workaround_capacity < 0 or workaround_capacity > 100:
                raise BusinessValidationError(
                    f"Workaround capacity must be between 0% and 100%, got {workaround_capacity}%"
                )

    @staticmethod
    def validate_who_tier_consistency(
        who_tier: Optional[str],
        rto_hours: int,
        patient_safety_impact: Optional[str]
    ):
        """
        Validate WHO tier matches RTO and patient safety impact

        Business Rules (WHO Essential Services Tiers):
        - TIER_1 (IMMEDIATE): RTO = 0, Patient Safety = LIFE_THREATENING
        - TIER_2 (URGENT): RTO <= 4h
        - TIER_3 (IMPORTANT): RTO <= 24h
        - TIER_4 (NORMAL): RTO <= 120h (5 days)
        """

        if not who_tier:
            return

        who_tier_upper = who_tier.upper()

        if who_tier_upper in ["TIER_1", "TIER1"]:  # IMMEDIATE
            if rto_hours != 0:
                raise BusinessValidationError(
                    f"WHO TIER_1 (IMMEDIATE) requires RTO = 0, got {rto_hours}h"
                )
            if patient_safety_impact and patient_safety_impact.upper() != "LIFE_THREATENING":
                raise BusinessValidationError(
                    f"WHO TIER_1 requires LIFE_THREATENING patient safety impact, "
                    f"got {patient_safety_impact}"
                )

        elif who_tier_upper in ["TIER_2", "TIER2"]:  # URGENT
            if rto_hours > 4:
                raise BusinessValidationError(
                    f"WHO TIER_2 (URGENT) requires RTO <= 4h, got {rto_hours}h"
                )

        elif who_tier_upper in ["TIER_3", "TIER3"]:  # IMPORTANT
            if rto_hours > 24:
                raise BusinessValidationError(
                    f"WHO TIER_3 (IMPORTANT) requires RTO <= 24h, got {rto_hours}h"
                )

        elif who_tier_upper in ["TIER_4", "TIER4"]:  # NORMAL
            if rto_hours > 120:
                raise BusinessValidationError(
                    f"WHO TIER_4 (NORMAL) requires RTO <= 120h, got {rto_hours}h"
                )

    @staticmethod
    def validate_minimum_staff_requirements(
        personnel_requirements: Optional[Dict[str, Any]],
        criticality: str
    ):
        """
        Validate minimum staff requirements

        Business Rule:
        - Minimum staff >= 1 (at least one person required)
        - Critical processes should have redundancy (min_staff >= 2)
        """

        if personnel_requirements:
            min_staff = personnel_requirements.get("min_staff", 1)

            if min_staff < 1:
                raise BusinessValidationError(
                    f"Minimum staff must be at least 1, got {min_staff}"
                )

            if criticality.upper() == "CRITICAL" and min_staff < 2:
                raise BusinessValidationError(
                    f"CRITICAL processes should have staff redundancy (min_staff >= 2), "
                    f"got {min_staff}"
                )

    # =========================================================================
    # COMPLIANCE MODULE VALIDATORS
    # =========================================================================

    @staticmethod
    def validate_evidence_dates(
        valid_from: Optional[datetime],
        valid_to: Optional[datetime],
        is_critical_control: bool = False
    ):
        """
        Validate evidence validity periods

        Business Rules:
        - valid_from < valid_to (if both provided)
        - Critical controls cannot have expired evidence
        """

        if valid_from and valid_to:
            if valid_from >= valid_to:
                raise BusinessValidationError(
                    f"Evidence valid_from ({valid_from.strftime('%Y-%m-%d')}) must be before "
                    f"valid_to ({valid_to.strftime('%Y-%m-%d')})"
                )

        # Critical controls cannot have expired evidence
        if is_critical_control and valid_to:
            if valid_to < datetime.utcnow():
                raise BusinessValidationError(
                    f"Critical control evidence cannot be expired. "
                    f"Valid until: {valid_to.strftime('%Y-%m-%d')}"
                )

    @staticmethod
    def validate_evidence_document_reference(
        document_id: Optional[Any],
        document_reference: Optional[str]
    ):
        """
        Validate evidence has either document or reference

        Business Rule:
        - At least one of document_id or document_reference must be provided
        - Evidence must be traceable
        """

        if not document_id and not document_reference:
            raise BusinessValidationError(
                "Evidence must have either document_id or document_reference"
            )

    @staticmethod
    def validate_assessment_dates(
        planned_date: Optional[datetime],
        actual_date: Optional[datetime],
        completion_date: Optional[datetime]
    ):
        """
        Validate assessment date sequence

        Business Rules:
        - planned_date < actual_date < completion_date
        - Dates must be in logical sequence
        """

        if planned_date and actual_date:
            if actual_date < planned_date:
                raise BusinessValidationError(
                    f"Actual date ({actual_date.strftime('%Y-%m-%d')}) cannot be before "
                    f"planned date ({planned_date.strftime('%Y-%m-%d')})"
                )

        if actual_date and completion_date:
            if completion_date < actual_date:
                raise BusinessValidationError(
                    f"Completion date ({completion_date.strftime('%Y-%m-%d')}) cannot be before "
                    f"actual start date ({actual_date.strftime('%Y-%m-%d')})"
                )

    @staticmethod
    def validate_assessment_scope(
        scope_clauses: List[str]
    ):
        """
        Validate assessment scope

        Business Rule:
        - Assessment must cover at least 1 requirement/clause
        """

        if not scope_clauses or len(scope_clauses) == 0:
            raise BusinessValidationError(
                "Assessment must cover at least 1 requirement clause"
            )

    @staticmethod
    def validate_gap_due_date(
        severity: str,
        due_date: Optional[datetime],
        assigned_date: Optional[datetime] = None
    ):
        """
        Validate gap due date based on severity SLA

        Business Rules (SLA by severity):
        - CRITICAL: Must be resolved within 7 days
        - HIGH: Must be resolved within 30 days
        - MEDIUM: Must be resolved within 90 days
        - LOW: Must be resolved within 180 days
        """

        if not due_date:
            return

        assigned_date = assigned_date or datetime.utcnow()

        # Severity-based SLA (Service Level Agreement)
        sla_days = {
            "CRITICAL": 7,
            "critical": 7,
            "HIGH": 30,
            "high": 30,
            "MEDIUM": 90,
            "medium": 90,
            "LOW": 180,
            "low": 180
        }

        max_days = sla_days.get(severity, 180)
        max_due_date = assigned_date + timedelta(days=max_days)

        if due_date > max_due_date:
            raise BusinessValidationError(
                f"{severity.upper()} severity gaps must be resolved within {max_days} days. "
                f"Due date ({due_date.strftime('%Y-%m-%d')}) exceeds maximum "
                f"({max_due_date.strftime('%Y-%m-%d')})"
            )

        # Due date should be in the future when assigning
        if due_date < assigned_date:
            raise BusinessValidationError(
                f"Gap due date ({due_date.strftime('%Y-%m-%d')}) cannot be in the past"
            )

    @staticmethod
    def validate_gap_target_coverage(
        current_coverage: Optional[float],
        target_coverage: float
    ):
        """
        Validate gap coverage values

        Business Rules:
        - Target coverage must be > current coverage (improvement required)
        - Coverage values must be 0-100%
        """

        if target_coverage < 0 or target_coverage > 100:
            raise BusinessValidationError(
                f"Target coverage must be between 0% and 100%, got {target_coverage}%"
            )

        if current_coverage is not None:
            if current_coverage < 0 or current_coverage > 100:
                raise BusinessValidationError(
                    f"Current coverage must be between 0% and 100%, got {current_coverage}%"
                )

            if target_coverage <= current_coverage:
                raise BusinessValidationError(
                    f"Target coverage ({target_coverage}%) must exceed current coverage "
                    f"({current_coverage}%) for gap remediation"
                )

    @staticmethod
    def validate_nc_root_cause_coverage(
        root_causes: List[Dict[str, Any]],
        corrective_actions: List[Dict[str, Any]]
    ):
        """
        Validate all root causes are addressed by corrective actions

        Business Rule:
        - Each root cause must have at least one corrective action
        - All identified root causes must be addressed
        """

        if not root_causes:
            return

        root_cause_ids = {rc.get("id") for rc in root_causes if rc.get("id")}
        addressed_causes = set()

        for action in corrective_actions:
            cause_id = action.get("addresses_cause_id")
            if cause_id:
                addressed_causes.add(cause_id)

        unaddressed = root_cause_ids - addressed_causes
        if unaddressed:
            raise BusinessValidationError(
                f"Root causes not addressed by corrective actions: {list(unaddressed)}"
            )

    @staticmethod
    def validate_nc_type_requires_rca(
        nc_type: str,
        rca_method: Optional[str]
    ):
        """
        MAJOR nonconformities require Root Cause Analysis

        Business Rule:
        - MAJOR NC must have RCA (5 Whys, Fishbone, Fault Tree, etc.)
        - This ensures systematic investigation of serious issues
        """

        if nc_type.upper() == "MAJOR" and not rca_method:
            raise BusinessValidationError(
                "MAJOR nonconformities require Root Cause Analysis (RCA). "
                "Use 5_whys, fishbone, fault_tree, or other RCA method."
            )

    @staticmethod
    def validate_nc_effectiveness_review(
        corrective_actions: List[Dict[str, Any]],
        actions_completed_at: Optional[datetime]
    ):
        """
        Validate effectiveness review timing

        Business Rule:
        - Effectiveness review should be conducted 90 days after completion
        - This allows time to verify sustained effectiveness
        """

        if actions_completed_at and corrective_actions:
            days_since_completion = (datetime.utcnow() - actions_completed_at).days

            # This is more of a warning than a hard validation
            # But we can enforce that review shouldn't happen immediately
            if days_since_completion < 7:
                raise BusinessValidationError(
                    "Effectiveness review should be conducted at least 7 days after "
                    "corrective actions completion to verify sustained effectiveness"
                )

    @staticmethod
    def validate_audit_independence(
        audit_type: str,
        auditor_name: Optional[str],
        process_owner: Optional[str] = None,
        auditor_independent: bool = True
    ):
        """
        Validate auditor independence

        Business Rules:
        - Internal audit: Lead auditor cannot be the process owner
        - External audit: Auditor must be marked as independent
        """

        if audit_type.upper() == "INTERNAL":
            if auditor_name and process_owner and auditor_name == process_owner:
                raise BusinessValidationError(
                    "Internal auditor cannot be the process owner (independence violation)"
                )

        elif audit_type.upper() == "EXTERNAL":
            if not auditor_independent:
                raise BusinessValidationError(
                    "External auditor must be marked as independent"
                )

    @staticmethod
    def validate_surveillance_interval(
        last_audit_date: datetime,
        next_audit_date: datetime,
        standard: str = "ISO_22301"
    ):
        """
        Validate surveillance audit interval

        Business Rule:
        - ISO 22301 requires surveillance audits within 12 months (365 days)
        - Other standards may have different intervals (max 400 days)
        """

        # ISO 22301 and most ISO standards require annual surveillance
        max_interval_days = 365 if standard == "ISO_22301" else 400

        interval = (next_audit_date - last_audit_date).days

        if interval > max_interval_days:
            raise BusinessValidationError(
                f"{standard} requires surveillance audits within {max_interval_days} days. "
                f"Current interval: {interval} days"
            )

    @staticmethod
    def validate_audit_findings_consistency(
        overall_result: str,
        major_nc_count: int,
        minor_nc_count: int
    ):
        """
        Validate audit result is consistent with findings

        Business Rules:
        - PASS: No major NCs
        - CONDITIONAL_PASS: Minor NCs only, or addressed major NCs
        - FAIL: Unresolved major NCs
        """

        if overall_result.upper() == "PASS":
            if major_nc_count > 0:
                raise BusinessValidationError(
                    f"Audit cannot PASS with {major_nc_count} major nonconformities"
                )

        elif overall_result.upper() == "FAIL":
            if major_nc_count == 0 and minor_nc_count == 0:
                raise BusinessValidationError(
                    "Audit marked as FAIL but has no nonconformities"
                )


# Additional utility validators

def validate_annual_revenue_impact(
    annual_revenue: float,
    financial_impact_24h: float
):
    """
    Validate annual revenue impact is realistic

    Business Rule:
    - 24-hour impact should not exceed annual revenue
    - This prevents unrealistic impact estimates
    """

    if financial_impact_24h > annual_revenue:
        raise BusinessValidationError(
            f"24-hour financial impact ({financial_impact_24h}) cannot exceed "
            f"annual revenue ({annual_revenue})"
        )
