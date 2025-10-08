"""
Organization Endpoints

REST API endpoints for organization/digital twin operations
"""

import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query, Request
from pydantic import BaseModel, Field

from storage import PostgreSQLStorage, RedisCache
from core.models.base import OrganizationType
from api.auth.dependencies import get_current_active_user, require_admin

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class OrganizationCreate(BaseModel):
    """Organization creation request"""
    id: str = Field(..., description="Organization ID")
    twin_id: str = Field(..., description="Digital Twin ID")
    name: str = Field(..., description="Organization name")
    canonical_name: Optional[str] = Field(None, description="Canonical name")
    org_type: OrganizationType = Field(..., description="Organization type")
    industry: Optional[str] = Field(None, description="Industry")
    employee_count: Optional[int] = Field(None, description="Employee count")
    annual_revenue: Optional[float] = Field(None, description="Annual revenue")
    annual_budget: Optional[float] = Field(None, description="Annual budget")
    headquarters: Optional[dict] = Field(None, description="Headquarters location")
    website: Optional[str] = Field(None, description="Website URL")
    description: Optional[str] = Field(None, description="Description")
    email_domain: Optional[str] = Field(None, description="Email domain")


class OrganizationUpdate(BaseModel):
    """Organization update request"""
    name: Optional[str] = None
    canonical_name: Optional[str] = None
    org_type: Optional[OrganizationType] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[float] = None
    annual_budget: Optional[float] = None
    headquarters: Optional[dict] = None
    locations: Optional[dict] = None
    contacts: Optional[dict] = None
    website: Optional[str] = None
    description: Optional[str] = None
    health_score: Optional[float] = None
    maturity_level: Optional[int] = None
    completeness_score: Optional[float] = None
    quality_score: Optional[float] = None
    risk_score: Optional[float] = None


class OrganizationResponse(BaseModel):
    """Organization response"""
    id: str
    twin_id: str
    name: str
    canonical_name: Optional[str]
    org_type: str
    industry: Optional[str]
    employee_count: Optional[int]
    annual_revenue: Optional[float]
    annual_budget: Optional[float]
    headquarters: Optional[dict]
    locations: Optional[dict]
    contacts: Optional[dict]
    website: Optional[str]
    description: Optional[str]
    health_score: float
    maturity_level: int
    completeness_score: float
    quality_score: float
    risk_score: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrganizationList(BaseModel):
    """Organization list response"""
    total: int
    items: List[OrganizationResponse]
    limit: int
    offset: int


# ============================================
# DEPENDENCIES
# ============================================

def get_storage(request: Request) -> PostgreSQLStorage:
    """Get storage dependency"""
    return request.app.state.app_state.storage


def get_cache(request: Request) -> RedisCache:
    """Get cache dependency"""
    return request.app.state.app_state.cache


# ============================================
# ENDPOINTS
# ============================================

@router.post("/", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    org: OrganizationCreate,
    storage: PostgreSQLStorage = Depends(get_storage),
    cache: RedisCache = Depends(get_cache),
    current_user = Depends(get_current_active_user)
):
    """
    Create new organization/digital twin

    Creates a new organization and initializes its digital twin
    """
    try:
        # Auto-assign tenant_id from current user
        org_data = org.model_dump()
        org_data['tenant_id'] = current_user.tenant_id

        # Create in database
        org_model = await storage.create_organization(org_data)

        # Cache it
        await cache.cache_organization(org_model.id, org.model_dump())

        logger.info(f"Created organization: {org_model.id}")

        return OrganizationResponse.model_validate(org_model)

    except Exception as e:
        logger.error(f"Failed to create organization: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    storage: PostgreSQLStorage = Depends(get_storage),
    cache: RedisCache = Depends(get_cache),
    current_user = Depends(get_current_active_user)
):
    """
    Get organization by ID

    Retrieves organization data with caching
    """
    try:
        # Try cache first
        cached = await cache.get_organization(org_id)
        if cached:
            # Verify tenant ownership from cache
            if cached.get('tenant_id') != current_user.tenant_id:
                raise HTTPException(status_code=403, detail="Not authorized to access this organization")
            logger.debug(f"Cache hit for organization: {org_id}")
            return OrganizationResponse(**cached)

        # Cache miss - get from database
        org_model = await storage.get_organization(org_id=org_id)

        if not org_model:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Verify tenant ownership
        if org_model.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this organization")

        # Cache for next time
        org_dict = {
            'id': org_model.id,
            'twin_id': org_model.twin_id,
            'name': org_model.name,
            'canonical_name': org_model.canonical_name,
            'org_type': org_model.org_type,
            'industry': org_model.industry,
            'employee_count': org_model.employee_count,
            'annual_revenue': org_model.annual_revenue,
            'annual_budget': org_model.annual_budget,
            'headquarters': org_model.headquarters,
            'locations': org_model.locations,
            'contacts': org_model.contacts,
            'website': org_model.website,
            'description': org_model.description,
            'health_score': org_model.health_score,
            'maturity_level': org_model.maturity_level,
            'completeness_score': org_model.completeness_score,
            'quality_score': org_model.quality_score,
            'risk_score': org_model.risk_score,
            'created_at': org_model.created_at.isoformat(),
            'updated_at': org_model.updated_at.isoformat()
        }
        await cache.cache_organization(org_id, org_dict)

        return OrganizationResponse.model_validate(org_model)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get organization: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/twin/{twin_id}", response_model=OrganizationResponse)
async def get_organization_by_twin_id(
    twin_id: str,
    storage: PostgreSQLStorage = Depends(get_storage),
    cache: RedisCache = Depends(get_cache),
    current_user = Depends(get_current_active_user)
):
    """
    Get organization by twin ID

    Alternative lookup by digital twin identifier
    """
    try:
        # Try cache with twin_id key
        cached = await cache.get('organization_twin', twin_id)
        if cached:
            return OrganizationResponse(**cached)

        # Get from database
        org_model = await storage.get_organization(twin_id=twin_id)

        if not org_model:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Cache with both keys
        org_dict = {
            'id': org_model.id,
            'twin_id': org_model.twin_id,
            'name': org_model.name,
            'canonical_name': org_model.canonical_name,
            'org_type': org_model.org_type,
            'industry': org_model.industry,
            'employee_count': org_model.employee_count,
            'annual_revenue': org_model.annual_revenue,
            'annual_budget': org_model.annual_budget,
            'headquarters': org_model.headquarters,
            'locations': org_model.locations,
            'contacts': org_model.contacts,
            'website': org_model.website,
            'description': org_model.description,
            'health_score': org_model.health_score,
            'maturity_level': org_model.maturity_level,
            'completeness_score': org_model.completeness_score,
            'quality_score': org_model.quality_score,
            'risk_score': org_model.risk_score,
            'created_at': org_model.created_at.isoformat(),
            'updated_at': org_model.updated_at.isoformat()
        }
        await cache.set('organization_twin', twin_id, org_dict)

        return OrganizationResponse.model_validate(org_model)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get organization by twin_id: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: str,
    updates: OrganizationUpdate,
    storage: PostgreSQLStorage = Depends(get_storage),
    cache: RedisCache = Depends(get_cache),
    current_user = Depends(get_current_active_user)
):
    """
    Update organization

    Updates organization fields and invalidates cache
    """
    try:
        # Verify ownership first
        org_model = await storage.get_organization(org_id=org_id)

        if not org_model:
            raise HTTPException(status_code=404, detail="Organization not found")

        if org_model.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this organization")

        # Update in database
        update_data = updates.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        org_model = await storage.update_organization(org_id, update_data)

        # Invalidate cache
        await cache.invalidate_organization(org_id)
        await cache.delete('organization_twin', org_model.twin_id)

        logger.info(f"Updated organization: {org_id}")

        return OrganizationResponse.model_validate(org_model)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update organization: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{org_id}", status_code=204)
async def delete_organization(
    org_id: str,
    storage: PostgreSQLStorage = Depends(get_storage),
    cache: RedisCache = Depends(get_cache),
    current_user = Depends(require_admin)
):
    """
    Delete organization

    Deletes organization and all related data (cascade)
    """
    try:
        # Get twin_id before deletion (for cache invalidation)
        org_model = await storage.get_organization(org_id=org_id)

        if not org_model:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Verify ownership (admin can only delete their tenant's orgs)
        if org_model.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this organization")

        twin_id = org_model.twin_id

        # Delete from database
        deleted = await storage.delete_organization(org_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Invalidate cache
        await cache.invalidate_organization(org_id)
        await cache.delete('organization_twin', twin_id)

        logger.info(f"Deleted organization: {org_id}")

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete organization: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=OrganizationList)
async def list_organizations(
    org_type: Optional[OrganizationType] = Query(None, description="Filter by organization type"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    name_contains: Optional[str] = Query(None, description="Filter by name (partial match)"),
    min_health_score: Optional[float] = Query(None, description="Minimum health score"),
    limit: int = Query(100, ge=1, le=1000, description="Max results"),
    offset: int = Query(0, ge=0, description="Skip results"),
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    List organizations

    Returns paginated list of organizations with optional filters
    """
    try:
        # Build filters
        filters = {}
        if org_type:
            filters['org_type'] = org_type
        if industry:
            filters['industry'] = industry
        if name_contains:
            filters['name_contains'] = name_contains
        if min_health_score is not None:
            filters['min_health_score'] = min_health_score

        # Get organizations (filtered by tenant)
        organizations = await storage.list_organizations(
            tenant_id=current_user.tenant_id,  # ← TENANT FILTER
            filters=filters,
            limit=limit,
            offset=offset
        )

        # Convert to response models
        items = [OrganizationResponse.model_validate(org) for org in organizations]

        return OrganizationList(
            total=len(items),  # TODO: Add count query
            items=items,
            limit=limit,
            offset=offset
        )

    except Exception as e:
        logger.error(f"Failed to list organizations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{org_id}/data-sources")
async def get_organization_data_sources(
    org_id: str,
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Get organization data sources

    Returns list of connected data sources for organization
    """
    try:
        # Verify organization exists
        org_model = await storage.get_organization(org_id=org_id)
        if not org_model:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Get data sources
        sources = await storage.list_data_sources(org_id)

        return {
            'organization_id': org_id,
            'twin_id': org_model.twin_id,
            'data_sources': [
                {
                    'id': src.id,
                    'source_type': src.source_type,
                    'source_id': src.source_id,
                    'last_sync': src.last_sync.isoformat() if src.last_sync else None,
                    'sync_status': src.sync_status,
                    'metadata': src.metadata
                }
                for src in sources
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get data sources: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{org_id}/insights")
async def get_ai_insights(
    org_id: str,
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Get AI-generated insights for organization

    Aggregates insights from:
    - Queue Theory analysis (BIA insights)
    - Advanced AI recommendations
    - Monte Carlo risk analysis
    - Recent simulation results

    Returns TwinInsight format compatible with frontend
    """
    try:
        from core.models.base import (
            TwinInsight, TwinInsightType, ImpactLevel, AIInsightsResponse
        )

        # Verify organization exists and tenant ownership
        org_model = await storage.get_organization(org_id=org_id)
        if not org_model:
            raise HTTPException(status_code=404, detail="Organization not found")

        if org_model.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this organization")

        insights = []

        # 1. Get health score insights
        if org_model.health_score < 50:
            insights.append(TwinInsight(
                type=TwinInsightType.WARNING,
                title="Low Organization Health Score",
                description=f"Organization health score is {org_model.health_score:.1f}/100, indicating potential issues requiring attention.",
                confidence=95.0,
                impact=ImpactLevel.HIGH,
                source="health_metrics",
                actionable=True,
                suggested_actions=[
                    "Review completeness score to identify missing data",
                    "Analyze quality score to improve data accuracy",
                    "Conduct comprehensive risk assessment"
                ],
                priority=1,
                tags=["health", "metrics"]
            ))

        # 2. Get risk score insights
        if org_model.risk_score > 70:
            insights.append(TwinInsight(
                type=TwinInsightType.RISK,
                title="Elevated Risk Level Detected",
                description=f"Organization risk score is {org_model.risk_score:.1f}/100. High-risk areas require immediate mitigation strategies.",
                confidence=90.0,
                impact=ImpactLevel.CRITICAL,
                source="risk_analysis",
                actionable=True,
                suggested_actions=[
                    "Conduct Business Impact Analysis (BIA)",
                    "Review and update risk mitigation plans",
                    "Implement additional controls for high-risk processes",
                    "Schedule risk assessment meeting with stakeholders"
                ],
                priority=1,
                tags=["risk", "critical"]
            ))

        # 3. Get data quality insights
        if org_model.quality_score < 60:
            insights.append(TwinInsight(
                type=TwinInsightType.WARNING,
                title="Data Quality Below Threshold",
                description=f"Data quality score is {org_model.quality_score:.1f}/100. Poor data quality affects analysis accuracy.",
                confidence=85.0,
                impact=ImpactLevel.MEDIUM,
                source="data_quality",
                actionable=True,
                suggested_actions=[
                    "Review data collection processes",
                    "Implement data validation rules",
                    "Schedule data quality audit",
                    "Train staff on data entry best practices"
                ],
                priority=2,
                tags=["data_quality", "operations"]
            ))

        # 4. Get maturity level insights
        if org_model.maturity_level <= 2:
            insights.append(TwinInsight(
                type=TwinInsightType.OPPORTUNITY,
                title="BCM Maturity Enhancement Opportunity",
                description=f"Organization is at maturity level {org_model.maturity_level}/5. There's significant opportunity to enhance BCM capabilities.",
                confidence=80.0,
                impact=ImpactLevel.MEDIUM,
                source="maturity_assessment",
                actionable=True,
                suggested_actions=[
                    "Develop comprehensive BIA program",
                    "Establish BCM governance structure",
                    "Conduct BCM training for key personnel",
                    "Implement regular exercise program",
                    "Document recovery procedures"
                ],
                priority=3,
                tags=["maturity", "improvement", "bcm"]
            ))

        # 5. Get recent simulation insights (if any)
        recent_simulations = await storage.list_simulations(
            twin_id=org_model.twin_id,
            limit=3
        )

        for sim in recent_simulations:
            if sim.status == "completed" and sim.impact_score and sim.impact_score > 70:
                insights.append(TwinInsight(
                    type=TwinInsightType.RISK,
                    title=f"High-Impact Scenario: {sim.scenario.value.replace('_', ' ').title()}",
                    description=f"Recent simulation shows impact score of {sim.impact_score:.1f}/100. "
                                f"Financial impact: ${sim.financial_impact:,.0f}" if sim.financial_impact else "Significant impact predicted.",
                    confidence=75.0,
                    impact=ImpactLevel.HIGH if sim.impact_score > 80 else ImpactLevel.MEDIUM,
                    source="simulation_engine",
                    actionable=True,
                    suggested_actions=sim.recommendations.get('actions', []) if isinstance(sim.recommendations, dict) else [
                        "Review simulation results in detail",
                        "Develop mitigation strategies",
                        "Update business continuity plans"
                    ],
                    priority=2,
                    tags=["simulation", sim.scenario.value]
                ))

        # 6. Recommendation for Queue Theory BIA if no BIA analyses exist
        bia_analyses = await storage.list_bia_analyses(org_id=org_id, limit=1)
        if not bia_analyses:
            insights.append(TwinInsight(
                type=TwinInsightType.RECOMMENDATION,
                title="Business Impact Analysis Recommended",
                description="No BIA analyses found. Conducting a comprehensive BIA using Queue Theory will provide mathematical insights into recovery time objectives and financial impacts.",
                confidence=95.0,
                impact=ImpactLevel.MEDIUM,
                source="system_recommendation",
                actionable=True,
                suggested_actions=[
                    "Use Queue Theory BIA endpoint: POST /api/v1/bia/queue-theory",
                    "Identify critical business processes",
                    "Determine acceptable downtime for each process",
                    "Calculate optimal RTO/RPO targets"
                ],
                priority=2,
                tags=["bia", "recommendation", "queue_theory"]
            ))

        # 7. Recommendation for AI scenario generation
        scenario_count = await storage.count_scenarios(tenant_id=current_user.tenant_id)
        if scenario_count < 3:
            insights.append(TwinInsight(
                type=TwinInsightType.OPPORTUNITY,
                title="Generate AI-Powered Exercise Scenarios",
                description="Generate realistic BCM exercise scenarios using Advanced AI. Scenarios adapt to your industry and organization context.",
                confidence=90.0,
                impact=ImpactLevel.LOW,
                source="system_recommendation",
                actionable=True,
                suggested_actions=[
                    "Use Advanced AI endpoint: POST /api/v1/scenarios/ai-generate-advanced",
                    "Start with cyber attack scenario",
                    "Run tabletop exercise with team",
                    "Submit feedback for AI learning"
                ],
                priority=3,
                tags=["ai", "scenarios", "training"]
            ))

        # Calculate summary statistics
        risk_count = sum(1 for i in insights if i.type == TwinInsightType.RISK)
        opportunity_count = sum(1 for i in insights if i.type == TwinInsightType.OPPORTUNITY)
        warning_count = sum(1 for i in insights if i.type == TwinInsightType.WARNING)
        recommendation_count = sum(1 for i in insights if i.type == TwinInsightType.RECOMMENDATION)

        # Build response
        response = AIInsightsResponse(
            organization_id=org_id,
            total_insights=len(insights),
            insights=insights,
            risk_count=risk_count,
            opportunity_count=opportunity_count,
            warning_count=warning_count,
            recommendation_count=recommendation_count
        )

        logger.info(f"Generated {len(insights)} insights for organization {org_id}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate AI insights: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
