"""
Supply Chain BCM - API Endpoints
8 endpoints for supplier management and supply chain resilience

EY Research: Organizations with ISO 22301 recover from supply chain disruptions 20% faster
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Query

from supply_chain_schemas import (
    # Request/Response schemas
    SupplierCreate, SupplierUpdate, SupplierResponse, SupplierListResponse,
    SupplierDisruptionCreate, SupplierDisruptionUpdate, SupplierDisruptionResponse,

    # Analysis schemas
    SupplierRiskProfile, SPOFSupplier, SupplyChainRiskMap,
    BCMAssessment, WhatIfScenario, WhatIfResult, SupplyChainSummary,

    # Enums
    SupplierCriticalityLevel, SupplierStatus, DisruptionType
)
from shared.exceptions import EntityNotFoundError, DuplicateResourceException

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/bia/supply-chain", tags=["Supply Chain BCM"])

# ===== IN-MEMORY STORAGE (Replace with DB in production) =====
suppliers_db: Dict[int, Dict] = {}
disruptions_db: Dict[int, Dict] = {}
next_supplier_id = 1
next_disruption_id = 1


# ============================================================================
# ENDPOINT 1: CREATE SUPPLIER
# ============================================================================

@router.post("/suppliers", response_model=SupplierResponse, status_code=201)
async def create_supplier(supplier: SupplierCreate):
    """
    Create new supplier profile

    **ISO 22301:** Extended dependency management for supply chain risks
    **Use Case:** Register critical suppliers for BCM tracking
    """
    global next_supplier_id

    # Check for duplicate supplier_code
    existing = [s for s in suppliers_db.values()
                if s['tenant_id'] == supplier.tenant_id and s['supplier_code'] == supplier.supplier_code]
    if existing:
        raise DuplicateResourceException(
            message=f"Supplier with code '{supplier.supplier_code}' already exists for this tenant",
            details={"supplier_code": supplier.supplier_code, "tenant_id": supplier.tenant_id}
        )

    # Create supplier
    supplier_data = supplier.model_dump()
    supplier_data['id'] = next_supplier_id
    supplier_data['created_at'] = datetime.utcnow()
    supplier_data['updated_at'] = datetime.utcnow()
    supplier_data['created_by'] = 'system'  # TODO: Get from auth

    suppliers_db[next_supplier_id] = supplier_data
    next_supplier_id += 1

    logger.info(f"Created supplier {supplier_data['id']}: {supplier.supplier_name} (criticality: {supplier.criticality_level})")

    return SupplierResponse(**supplier_data)


# ============================================================================
# ENDPOINT 2: LIST SUPPLIERS
# ============================================================================

@router.get("/suppliers", response_model=SupplierListResponse)
async def list_suppliers(
    tenant_id: str = Query(...),
    criticality_level: Optional[SupplierCriticalityLevel] = None,
    status: Optional[SupplierStatus] = None,
    single_point_of_failure: Optional[bool] = None,
    has_iso22301_certification: Optional[bool] = None,
    country: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    List suppliers with filtering

    **Filters:**
    - criticality_level: critical, high, medium, low
    - status: active, inactive, at_risk, under_review
    - single_point_of_failure: true/false (SPOF flag)
    - has_iso22301_certification: true/false
    - country: Filter by country
    """
    # Filter suppliers
    filtered = [
        s for s in suppliers_db.values()
        if s['tenant_id'] == tenant_id
        and (criticality_level is None or s['criticality_level'] == criticality_level)
        and (status is None or s['status'] == status)
        and (single_point_of_failure is None or s['single_point_of_failure'] == single_point_of_failure)
        and (has_iso22301_certification is None or s['has_iso22301_certification'] == has_iso22301_certification)
        and (country is None or s.get('country') == country)
    ]

    total = len(filtered)
    paginated = filtered[offset:offset + limit]

    return SupplierListResponse(
        total=total,
        suppliers=[SupplierResponse(**s) for s in paginated],
        filters_applied={
            "criticality_level": criticality_level,
            "status": status,
            "single_point_of_failure": single_point_of_failure,
            "has_iso22301_certification": has_iso22301_certification,
            "country": country
        }
    )


# ============================================================================
# ENDPOINT 3: GET SUPPLIER
# ============================================================================

@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: int,
    tenant_id: str = Query(...)
):
    """Get supplier by ID"""
    if supplier_id not in suppliers_db:
        raise EntityNotFoundError("Supplier", str(supplier_id))

    supplier = suppliers_db[supplier_id]

    # Tenant check
    if supplier['tenant_id'] != tenant_id:
        raise EntityNotFoundError("Supplier", str(supplier_id))

    return SupplierResponse(**supplier)


# ============================================================================
# ENDPOINT 4: UPDATE SUPPLIER
# ============================================================================

@router.patch("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: int,
    updates: SupplierUpdate,
    tenant_id: str = Query(...)
):
    """Update supplier information"""
    if supplier_id not in suppliers_db:
        raise EntityNotFoundError("Supplier", str(supplier_id))

    supplier = suppliers_db[supplier_id]

    # Tenant check
    if supplier['tenant_id'] != tenant_id:
        raise EntityNotFoundError("Supplier", str(supplier_id))

    # Update fields
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        supplier[key] = value

    supplier['updated_at'] = datetime.utcnow()

    logger.info(f"Updated supplier {supplier_id}")

    return SupplierResponse(**supplier)


# ============================================================================
# ENDPOINT 5: SUPPLIER RISK PROFILE
# ============================================================================

@router.get("/suppliers/{supplier_id}/risk-profile", response_model=SupplierRiskProfile)
async def get_supplier_risk_profile(
    supplier_id: int,
    tenant_id: str = Query(...)
):
    """
    Calculate comprehensive risk profile for supplier

    **Risk Factors:**
    - Criticality risk (0-100)
    - SPOF risk (0 or 100)
    - Financial stability risk
    - BCM maturity risk
    - Reliability risk
    - Alternative availability risk
    - Disruption frequency risk (last 12 months)

    **Overall Risk Score:** Weighted average of all factors
    """
    if supplier_id not in suppliers_db:
        raise EntityNotFoundError("Supplier", str(supplier_id))

    supplier = suppliers_db[supplier_id]

    if supplier['tenant_id'] != tenant_id:
        raise EntityNotFoundError("Supplier", str(supplier_id))

    # Calculate risk factors (0-100 scale, higher = more risk)

    # 1. Criticality Risk
    criticality_map = {"critical": 100, "high": 75, "medium": 50, "low": 25}
    criticality_risk = criticality_map.get(supplier['criticality_level'], 50)

    # 2. SPOF Risk
    spof_risk = 100 if supplier['single_point_of_failure'] else 0

    # 3. Financial Risk
    financial_map = {"at_risk": 100, "weak": 75, "adequate": 25, "strong": 0}
    financial_risk = financial_map.get(supplier.get('financial_stability'), 50)

    # 4. BCM Maturity Risk
    bcm_maturity_risk = 0 if supplier['has_iso22301_certification'] else 50

    # 5. Reliability Risk
    reliability_score = supplier.get('reliability_score')
    reliability_risk = (100 - reliability_score) if reliability_score is not None else 50

    # 6. Alternative Availability Risk
    alt_count = len(supplier.get('alternative_suppliers', []))
    if alt_count == 0:
        alternative_risk = 100
    elif alt_count == 1:
        alternative_risk = 50
    elif alt_count >= 2:
        alternative_risk = 25
    else:
        alternative_risk = 75

    # 7. Disruption Frequency Risk (last 12 months)
    cutoff_date = datetime.utcnow() - timedelta(days=365)
    recent_disruptions = [
        d for d in disruptions_db.values()
        if d['supplier_id'] == supplier_id and d['disruption_date'] >= cutoff_date
    ]
    disruption_frequency_risk = min(len(recent_disruptions) * 20, 100)

    # Overall Risk Score (weighted average)
    weights = {
        'criticality': 0.25,
        'spof': 0.20,
        'financial': 0.15,
        'bcm_maturity': 0.10,
        'reliability': 0.15,
        'alternative': 0.10,
        'disruption': 0.05
    }

    overall_risk_score = (
        criticality_risk * weights['criticality'] +
        spof_risk * weights['spof'] +
        financial_risk * weights['financial'] +
        bcm_maturity_risk * weights['bcm_maturity'] +
        reliability_risk * weights['reliability'] +
        alternative_risk * weights['alternative'] +
        disruption_frequency_risk * weights['disruption']
    )

    # Risk Level
    if overall_risk_score >= 75:
        risk_level = "critical"
        recommendation = "URGENT: Immediate action required. Identify alternatives, negotiate SLAs, conduct BCM assessment."
    elif overall_risk_score >= 50:
        risk_level = "high"
        recommendation = "HIGH PRIORITY: Develop mitigation plan within 30 days. Consider backup suppliers."
    elif overall_risk_score >= 25:
        risk_level = "medium"
        recommendation = "MONITOR: Regular reviews recommended. Consider diversification strategies."
    else:
        risk_level = "low"
        recommendation = "MAINTAIN: Continue normal monitoring and relationship management."

    return SupplierRiskProfile(
        supplier_id=supplier_id,
        supplier_name=supplier['supplier_name'],
        supplier_code=supplier['supplier_code'],
        criticality_risk=criticality_risk,
        spof_risk=spof_risk,
        financial_risk=financial_risk,
        bcm_maturity_risk=bcm_maturity_risk,
        reliability_risk=reliability_risk,
        alternative_availability_risk=alternative_risk,
        disruption_frequency_risk=disruption_frequency_risk,
        overall_risk_score=round(overall_risk_score, 2),
        risk_level=risk_level,
        recommendation=recommendation,
        analysis_date=datetime.utcnow()
    )


# ============================================================================
# ENDPOINT 6: SINGLE POINTS OF FAILURE (SPOF)
# ============================================================================

@router.get("/single-points-of-failure", response_model=List[SPOFSupplier])
async def identify_single_points_of_failure(
    tenant_id: str = Query(...)
):
    """
    Identify Single Points of Failure (SPOF) in supply chain

    **SPOF Definition:** Critical suppliers with no viable alternatives

    **Priority:** These are HIGHEST RISK suppliers requiring immediate attention
    """
    # Get all active suppliers with SPOF flag or critical with no alternatives
    spof_suppliers = []

    for supplier in suppliers_db.values():
        if supplier['tenant_id'] != tenant_id or supplier['status'] != 'active':
            continue

        is_spof = (
            supplier['single_point_of_failure'] or
            (supplier['criticality_level'] in ['critical', 'high'] and len(supplier.get('alternative_suppliers', [])) == 0)
        )

        if is_spof:
            # Get disruption stats
            cutoff_date = datetime.utcnow() - timedelta(days=365)
            disruptions = [
                d for d in disruptions_db.values()
                if d['supplier_id'] == supplier['id'] and d['disruption_date'] >= cutoff_date
            ]

            disruption_count = len(disruptions)
            avg_downtime = sum(d.get('downtime_hours', 0) for d in disruptions) / disruption_count if disruption_count > 0 else None
            total_impact = sum(d.get('financial_impact', 0) for d in disruptions)

            # Calculate risk score (simplified)
            risk_score = 100 if supplier['single_point_of_failure'] else 75
            risk_score += disruption_count * 5  # Increase by 5 per disruption
            risk_score = min(risk_score, 100)

            recommendation = f"CRITICAL SPOF: Find alternative suppliers immediately. " \
                           f"{disruption_count} disruptions in last 12 months. " \
                           f"Consider dual-sourcing strategy."

            spof_suppliers.append(SPOFSupplier(
                id=supplier['id'],
                supplier_code=supplier['supplier_code'],
                supplier_name=supplier['supplier_name'],
                criticality_level=supplier['criticality_level'],
                alternative_count=len(supplier.get('alternative_suppliers', [])),
                dependent_process_count=len(supplier.get('dependent_processes', [])),
                bcm_assessment_score=supplier.get('bcm_assessment_score'),
                disruption_count_12m=disruption_count,
                avg_downtime_hours=avg_downtime,
                total_financial_impact_12m=total_impact,
                risk_score=risk_score,
                recommendation=recommendation
            ))

    # Sort by risk score descending
    spof_suppliers.sort(key=lambda x: x.risk_score, reverse=True)

    logger.info(f"Identified {len(spof_suppliers)} SPOF suppliers for tenant {tenant_id}")

    return spof_suppliers


# ============================================================================
# ENDPOINT 7: RECORD SUPPLIER DISRUPTION
# ============================================================================

@router.post("/disruptions", response_model=SupplierDisruptionResponse, status_code=201)
async def record_supplier_disruption(disruption: SupplierDisruptionCreate):
    """
    Record supplier disruption for lessons learned

    **Purpose:** Track supply chain incidents and improve resilience
    """
    global next_disruption_id

    # Verify supplier exists
    if disruption.supplier_id not in suppliers_db:
        raise EntityNotFoundError("Supplier", str(disruption.supplier_id))

    supplier = suppliers_db[disruption.supplier_id]
    if supplier['tenant_id'] != disruption.tenant_id:
        raise EntityNotFoundError("Supplier", str(disruption.supplier_id))

    # Create disruption
    disruption_data = disruption.model_dump()
    disruption_data['id'] = next_disruption_id
    disruption_data['created_at'] = datetime.utcnow()
    disruption_data['updated_at'] = datetime.utcnow()
    disruption_data['created_by'] = 'system'

    # Calculate resolution time if resolved
    if disruption.resolution_date:
        delta = disruption.resolution_date - disruption.disruption_date
        disruption_data['resolution_time_hours'] = int(delta.total_seconds() / 3600)
    else:
        disruption_data['resolution_time_hours'] = None

    disruptions_db[next_disruption_id] = disruption_data
    next_disruption_id += 1

    logger.info(f"Recorded disruption {disruption_data['id']} for supplier {disruption.supplier_id} (type: {disruption.disruption_type}, severity: {disruption.severity})")

    return SupplierDisruptionResponse(**disruption_data)


# ============================================================================
# ENDPOINT 8: WHAT-IF ANALYSIS
# ============================================================================

@router.post("/what-if-analysis", response_model=WhatIfResult)
async def perform_what_if_analysis(
    scenario: WhatIfScenario,
    tenant_id: str = Query(...)
):
    """
    Perform what-if scenario analysis for supply chain disruption

    **Purpose:** Model impact of supplier failure and identify mitigation strategies

    **Example Scenarios:**
    - What if our critical cloud provider goes down for 24 hours?
    - What if our primary medical supplies distributor goes bankrupt?
    - What if a cyber attack hits our top 3 IT vendors?
    """
    # Validate all suppliers exist
    affected_suppliers = []
    for supplier_id in scenario.affected_supplier_ids:
        if supplier_id not in suppliers_db:
            raise EntityNotFoundError("Supplier", str(supplier_id))

        supplier = suppliers_db[supplier_id]
        if supplier['tenant_id'] != tenant_id:
            raise EntityNotFoundError("Supplier", str(supplier_id))

        affected_suppliers.append(supplier)

    # Analyze impact
    affected_processes_set = set()
    total_financial_impact = 0.0

    for supplier in affected_suppliers:
        # Add dependent processes
        affected_processes_set.update(supplier.get('dependent_processes', []))

        # Estimate financial impact (placeholder logic)
        # In production, this would query BIA processes for actual impact data
        if supplier['criticality_level'] == 'critical':
            estimated_impact_per_hour = 10000
        elif supplier['criticality_level'] == 'high':
            estimated_impact_per_hour = 5000
        elif supplier['criticality_level'] == 'medium':
            estimated_impact_per_hour = 2000
        else:
            estimated_impact_per_hour = 500

        total_financial_impact += estimated_impact_per_hour * scenario.assumed_duration_hours

    # Find available alternatives
    available_alternatives = []
    total_transition_time = 0
    total_capacity_available = 0

    for supplier in affected_suppliers:
        alternatives = supplier.get('alternative_suppliers', [])
        for alt in alternatives:
            available_alternatives.append({
                "supplier_id": alt['supplier_id'],
                "can_replace": alt['can_replace'],
                "transition_time_days": alt['transition_time_days'],
                "capacity_percentage": alt['capacity_percentage']
            })
            total_transition_time = max(total_transition_time, alt['transition_time_days'] * 24)  # hours
            total_capacity_available += alt['capacity_percentage']

    # Calculate capacity gap
    required_capacity = len(affected_suppliers) * 100  # 100% per supplier
    capacity_gap = max(0, required_capacity - total_capacity_available)

    # Generate recommendations
    immediate_actions = []
    medium_term_actions = []
    long_term_actions = []

    if len(available_alternatives) == 0:
        immediate_actions.append("CRITICAL: No alternatives available! Activate emergency procurement.")
        immediate_actions.append("Engage executive leadership immediately")
        immediate_actions.append("Assess manual workarounds for critical processes")
    else:
        immediate_actions.append(f"Activate {len(available_alternatives)} alternative suppliers")
        immediate_actions.append(f"Estimated transition time: {total_transition_time} hours")

    if capacity_gap > 0:
        immediate_actions.append(f"Capacity gap: {capacity_gap:.0f}% - prioritize critical processes")
        medium_term_actions.append("Identify additional backup suppliers to close capacity gap")

    medium_term_actions.append("Conduct post-incident review and update BCPs")
    medium_term_actions.append("Update supplier risk assessments")

    long_term_actions.append("Diversify supplier base to reduce SPOF risk")
    long_term_actions.append("Require ISO 22301 certification for critical suppliers")
    long_term_actions.append("Implement supply chain monitoring and early warning system")

    return WhatIfResult(
        scenario_name=scenario.scenario_name,
        affected_suppliers=[{
            "id": s['id'],
            "name": s['supplier_name'],
            "criticality": s['criticality_level']
        } for s in affected_suppliers],
        affected_processes=[{"id": pid} for pid in affected_processes_set],
        total_processes_impacted=len(affected_processes_set),
        estimated_financial_impact=total_financial_impact,
        estimated_downtime_hours=scenario.assumed_duration_hours,
        available_alternatives=available_alternatives,
        transition_time_required=total_transition_time,
        capacity_gap=capacity_gap,
        immediate_actions=immediate_actions,
        medium_term_actions=medium_term_actions,
        long_term_actions=long_term_actions,
        analysis_date=datetime.utcnow()
    )


# ============================================================================
# BONUS ENDPOINT: SUPPLY CHAIN SUMMARY
# ============================================================================

@router.get("/summary", response_model=SupplyChainSummary)
async def get_supply_chain_summary(
    tenant_id: str = Query(...)
):
    """
    Get comprehensive supply chain summary statistics

    **Includes:**
    - Total suppliers, active, critical, SPOF
    - BCM certification stats
    - Disruption history (last 12 months)
    - Top risks requiring attention
    """
    suppliers = [s for s in suppliers_db.values() if s['tenant_id'] == tenant_id]

    total_suppliers = len(suppliers)
    active_suppliers = len([s for s in suppliers if s['status'] == 'active'])
    critical_suppliers = len([s for s in suppliers if s['criticality_level'] in ['critical', 'high']])
    spof_count = len([s for s in suppliers if s['single_point_of_failure']])
    suppliers_with_iso22301 = len([s for s in suppliers if s['has_iso22301_certification']])
    suppliers_with_bcm = len([s for s in suppliers if s['has_bcm_program']])

    # Calculate averages
    reliability_scores = [s['reliability_score'] for s in suppliers if s.get('reliability_score') is not None]
    avg_reliability = sum(reliability_scores) / len(reliability_scores) if reliability_scores else None

    bcm_scores = [s['bcm_assessment_score'] for s in suppliers if s.get('bcm_assessment_score') is not None]
    avg_bcm_score = sum(bcm_scores) / len(bcm_scores) if bcm_scores else None

    # Disruption stats (last 12 months)
    cutoff_date = datetime.utcnow() - timedelta(days=365)
    recent_disruptions = [d for d in disruptions_db.values() if d['disruption_date'] >= cutoff_date]

    total_disruptions_12m = len(recent_disruptions)
    total_downtime_hours_12m = sum(d.get('downtime_hours', 0) for d in recent_disruptions)
    total_financial_impact_12m = sum(d.get('financial_impact', 0) for d in recent_disruptions)

    # Top 5 critical suppliers
    critical_sorted = sorted(
        [s for s in suppliers if s['criticality_level'] in ['critical', 'high']],
        key=lambda x: ('critical', 'high').index(x['criticality_level'])
    )[:5]

    top_5_critical = [{
        "id": s['id'],
        "name": s['supplier_name'],
        "criticality": s['criticality_level'],
        "spof": s['single_point_of_failure']
    } for s in critical_sorted]

    # Suppliers needing attention
    needing_attention = [
        {
            "id": s['id'],
            "name": s['supplier_name'],
            "reason": "Single Point of Failure with no alternatives"
        }
        for s in suppliers
        if s['single_point_of_failure'] and len(s.get('alternative_suppliers', [])) == 0
    ]

    return SupplyChainSummary(
        tenant_id=tenant_id,
        total_suppliers=total_suppliers,
        active_suppliers=active_suppliers,
        critical_suppliers=critical_suppliers,
        spof_count=spof_count,
        suppliers_with_iso22301=suppliers_with_iso22301,
        suppliers_with_bcm=suppliers_with_bcm,
        avg_reliability_score=round(avg_reliability, 2) if avg_reliability else None,
        avg_bcm_assessment_score=round(avg_bcm_score, 2) if avg_bcm_score else None,
        total_disruptions_12m=total_disruptions_12m,
        total_downtime_hours_12m=total_downtime_hours_12m,
        total_financial_impact_12m=total_financial_impact_12m,
        top_5_critical_suppliers=top_5_critical,
        suppliers_needing_attention=needing_attention,
        summary_date=datetime.utcnow()
    )
