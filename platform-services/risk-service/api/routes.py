"""
Risk Management - API Routes
ISO 22301:2019 Clause 8.2.3
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
import sys
from pathlib import Path

# Add shared database to Python path
shared_db_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "platform-services" / "community-service" / "shared"
if str(shared_db_path) not in sys.path:
    sys.path.insert(0, str(shared_db_path))

# Add shared models to path
shared_models_path = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "shared"
if str(shared_models_path) not in sys.path:
    sys.path.insert(0, str(shared_models_path))

# Direct import from common module
import importlib.util
spec = importlib.util.spec_from_file_location("common", shared_models_path / "models" / "common.py")
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
User = common.User

from database.connection import get_db
from models.domain import (
    Risk,
    RiskReport,
    FAIRAnalysis,
    MonteCarloSimulation,
    RiskTreatmentPlan
)
from services.business_logic import RiskService
from auth.dependencies import get_current_user


router = APIRouter(prefix="/api/v1/risk", tags=["Risk Management"])


# =============================================================================
# Risk CRUD
# =============================================================================

@router.post("/assessments", response_model=Risk, status_code=201)
async def create_risk(
    risk: Risk,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new risk assessment

    **ISO 22301:2019 Clause 8.2.3**
    - Identify and assess risks
    - Determine likelihood and impact

    **Authentication**: Requires valid JWT token
    """
    service = RiskService(db)
    return await service.create_risk(risk)


@router.get("/assessments", response_model=List[Risk])
async def list_risks(
    category: Optional[str] = None,
    status: Optional[str] = None,
    min_score: Optional[int] = Query(None, ge=1, le=25),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all risk assessments for organization

    **Filters:**
    - category: operational, financial, strategic, compliance, reputational, cybersecurity, natural_disaster
    - status: identified, analyzing, treated, monitoring, closed
    - min_score: Minimum inherent risk score (1-25)

    **Authentication**: Requires valid JWT token. Returns risks for user's organization only.
    """
    service = RiskService(db)
    # Use organization_id from JWT token
    organization_id = UUID(current_user.tenant_id)
    return await service.list_risks(
        organization_id=organization_id,
        category=category,
        status=status,
        min_score=min_score,
        skip=skip,
        limit=limit
    )


@router.get("/assessments/{risk_id}", response_model=Risk)
async def get_risk(
    risk_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get risk assessment by ID

    **Authentication**: Requires valid JWT token
    """
    service = RiskService(db)
    risk = await service.get_risk(risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk


@router.put("/assessments/{risk_id}", response_model=Risk)
async def update_risk(
    risk_id: UUID,
    risk_update: Risk,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update risk assessment

    **Authentication**: Requires valid JWT token
    """
    service = RiskService(db)
    risk = await service.update_risk(risk_id, risk_update)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk


@router.delete("/assessments/{risk_id}", status_code=204)
async def delete_risk(
    risk_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete (soft delete) risk assessment

    **Authentication**: Requires valid JWT token
    """
    service = RiskService(db)
    success = await service.delete_risk(risk_id)
    if not success:
        raise HTTPException(status_code=404, detail="Risk not found")


# =============================================================================
# Risk Analysis
# =============================================================================

@router.post("/assessments/{risk_id}/fair-analysis", response_model=FAIRAnalysis)
async def perform_fair_analysis(
    risk_id: UUID,
    fair_data: FAIRAnalysis,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform FAIR (Factor Analysis of Information Risk) quantitative analysis

    **FAIR Methodology:**
    - Loss Event Frequency = Threat Event Frequency × Vulnerability
    - Annual Loss Expectancy = LEF × Average Loss Magnitude
    - Results in risk rating: low, medium, high, critical

    **Authentication**: Requires valid JWT token
    """
    service = RiskService(db)
    return await service.perform_fair_analysis(risk_id, fair_data)


@router.get("/assessments/{risk_id}/fair-analysis", response_model=FAIRAnalysis)
async def get_fair_analysis(
    risk_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get latest FAIR analysis for risk

    **Authentication**: Requires valid JWT token
    """
    service = RiskService(db)
    analysis = await service.get_fair_analysis(risk_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="FAIR analysis not found")
    return analysis


@router.post("/assessments/{risk_id}/monte-carlo", response_model=MonteCarloSimulation)
async def run_monte_carlo_simulation(
    risk_id: UUID,
    simulation: MonteCarloSimulation,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Run Monte Carlo simulation for risk

    **Monte Carlo Method:**
    - Runs thousands of iterations with variable inputs
    - Produces probability distribution of outcomes
    - Returns mean, median, 95th and 99th percentiles

    **Authentication**: Requires valid JWT token
    """
    service = RiskService(db)
    return await service.run_monte_carlo(risk_id, simulation)


@router.get("/assessments/{risk_id}/monte-carlo", response_model=MonteCarloSimulation)
async def get_monte_carlo_results(
    risk_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get latest Monte Carlo simulation results

    **Authentication**: Requires valid JWT token
    """
    service = RiskService(db)
    results = await service.get_monte_carlo_results(risk_id)
    if not results:
        raise HTTPException(status_code=404, detail="Monte Carlo results not found")
    return results


# =============================================================================
# Risk Treatment
# =============================================================================

@router.post("/assessments/{risk_id}/treatment-plans", response_model=RiskTreatmentPlan)
async def create_treatment_plan(
    risk_id: UUID,
    plan: RiskTreatmentPlan,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create risk treatment plan

    **Treatment Strategies:**
    - Avoid: Eliminate the risk
    - Mitigate: Reduce likelihood/impact
    - Transfer: Insurance, outsourcing
    - Accept: Accept the risk

    **Authentication**: Requires valid JWT token
    """
    service = RiskService(db)
    return await service.create_treatment_plan(risk_id, plan)


@router.get("/assessments/{risk_id}/treatment-plans", response_model=List[RiskTreatmentPlan])
async def list_treatment_plans(
    risk_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all treatment plans for risk

    **Authentication**: Requires valid JWT token
    """
    service = RiskService(db)
    return await service.list_treatment_plans(risk_id)


@router.put("/treatment-plans/{plan_id}", response_model=RiskTreatmentPlan)
async def update_treatment_plan(
    plan_id: UUID,
    plan_update: RiskTreatmentPlan,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update treatment plan

    **Authentication**: Requires valid JWT token
    """
    service = RiskService(db)
    plan = await service.update_treatment_plan(plan_id, plan_update)
    if not plan:
        raise HTTPException(status_code=404, detail="Treatment plan not found")
    return plan


# =============================================================================
# Risk Reports
# =============================================================================

@router.get("/reports", response_model=RiskReport)
async def generate_risk_report(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate comprehensive risk report for organization

    **Report Includes:**
    - Total risk count by severity (critical/high/medium/low)
    - Top risks by score
    - Risk distribution by category
    - Treatment status breakdown
    - Trend analysis

    **Authentication**: Requires valid JWT token. Generates report for user's organization only.
    """
    service = RiskService(db)
    # Use organization_id from JWT token
    organization_id = UUID(current_user.tenant_id)
    return await service.generate_risk_report(organization_id)


@router.get("/assessments/{risk_id}/matrix-position")
async def get_risk_matrix_position(
    risk_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get risk position in 5x5 risk matrix

    Returns likelihood (1-5) and impact (1-5) coordinates

    **Authentication**: Requires valid JWT token
    """
    service = RiskService(db)
    risk = await service.get_risk(risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")

    return {
        "risk_id": risk_id,
        "likelihood": risk.likelihood,
        "impact": risk.impact,
        "inherent_score": risk.inherent_risk_score,
        "residual_likelihood": risk.residual_likelihood,
        "residual_impact": risk.residual_impact,
        "residual_score": risk.residual_risk_score,
        "severity": service.get_risk_severity(risk.inherent_risk_score)
    }


# =============================================================================
# Risk Aggregations
# =============================================================================

@router.get("/risk-heat-map")
async def get_risk_heat_map(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get risk heat map data (5x5 matrix with risk counts)

    **Authentication**: Requires valid JWT token. Returns heat map for user's organization only.
    """
    service = RiskService(db)
    # Use organization_id from JWT token
    organization_id = UUID(current_user.tenant_id)
    return await service.get_risk_heat_map(organization_id)


@router.get("/risk-trends")
async def get_risk_trends(
    days: int = Query(90, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get risk trends over time

    Shows how risk profile has changed over specified period

    **Authentication**: Requires valid JWT token. Returns trends for user's organization only.
    """
    service = RiskService(db)
    # Use organization_id from JWT token
    organization_id = UUID(current_user.tenant_id)
    return await service.get_risk_trends(organization_id, days)
