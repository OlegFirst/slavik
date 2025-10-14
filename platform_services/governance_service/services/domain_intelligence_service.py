"""
Domain Intelligence API - STAGE 4
8 endpoints for industry knowledge & domain classification
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from domain_schemas import (
    TenantDomainClassification, TenantDomainResponse,
    KnowledgeResponse, TemplateResponse, BenchmarkResponse,
    DomainRecommendation, RecommendationsResponse,
    IndustryInfo, AvailableIndustriesResponse
)
from database import get_db
from database.domain_models import Tenant, IndustryKnowledge, DomainTemplate, IndustryBenchmark
from eventbus_client import publish_tenant_classified, publish_knowledge_used, publish_template_accessed, publish_benchmark_compared
from audit_logger import log_tenant_classified, log_knowledge_accessed, log_template_accessed, log_benchmark_compared, log_recommendation_generated

router = APIRouter(prefix="/api/governance/domain", tags=["Domain Intelligence"])


# ============================================================================
# ENDPOINT 1: CLASSIFY TENANT DOMAIN
# ============================================================================

@router.patch("/tenant/classify", response_model=TenantDomainResponse)
async def classify_tenant_domain(
    tenant_id: str = Query(...),
    classification: TenantDomainClassification = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Classify tenant's industry domain

    **Purpose:** Set organization type, industry, size for intelligent recommendations

    **Example:**
    ```json
    {
      "organizational_type": "healthcare_provider",
      "industry_domain": "healthcare",
      "sub_domain": "hospital",
      "company_size": "large",
      "geographic_scope": "US",
      "regulatory_requirements": ["HIPAA", "Joint Commission"]
    }
    ```
    """

    # Check if tenant exists
    stmt = select(Tenant).where(Tenant.id == tenant_id)
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()

    if not tenant:
        # Create new tenant
        tenant = Tenant(
            id=tenant_id,
            organizational_type=classification.organizational_type.value,
            industry_domain=classification.industry_domain.value,
            sub_domain=classification.sub_domain,
            company_size=classification.company_size.value,
            geographic_scope=classification.geographic_scope,
            regulatory_requirements=classification.regulatory_requirements,
            domain_classified_at=datetime.utcnow(),
            domain_classified_by='system'  # TODO: from auth
        )
        db.add(tenant)
    else:
        # Update existing tenant
        tenant.organizational_type = classification.organizational_type.value
        tenant.industry_domain = classification.industry_domain.value
        tenant.sub_domain = classification.sub_domain
        tenant.company_size = classification.company_size.value
        tenant.geographic_scope = classification.geographic_scope
        tenant.regulatory_requirements = classification.regulatory_requirements
        tenant.domain_classified_at = datetime.utcnow()
        tenant.domain_classified_by = 'system'

    await db.commit()
    await db.refresh(tenant)

    # Publish event to EventBus
    await publish_tenant_classified(
        tenant_id=tenant.id,
        organizational_type=tenant.organizational_type,
        industry_domain=tenant.industry_domain,
        sub_domain=tenant.sub_domain,
        company_size=tenant.company_size,
        classified_by=tenant.domain_classified_by
    )

    # Log audit event
    await log_tenant_classified(
        db=db,
        tenant_id=tenant.id,
        industry=tenant.industry_domain,
        sub_domain=tenant.sub_domain,
        company_size=tenant.company_size,
        user_id=tenant.domain_classified_by
    )

    return TenantDomainResponse(
        tenant_id=tenant.id,
        organizational_type=tenant.organizational_type,
        industry_domain=tenant.industry_domain,
        sub_domain=tenant.sub_domain,
        company_size=tenant.company_size,
        geographic_scope=tenant.geographic_scope,
        regulatory_requirements=tenant.regulatory_requirements or [],
        domain_classified_at=tenant.domain_classified_at,
        domain_classified_by=tenant.domain_classified_by
    )


# ============================================================================
# ENDPOINT 2: GET TENANT DOMAIN
# ============================================================================

@router.get("/tenant", response_model=TenantDomainResponse)
async def get_tenant_domain(
    tenant_id: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Get tenant's domain classification"""

    stmt = select(Tenant).where(Tenant.id == tenant_id)
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()

    if not tenant:
        # Return empty classification
        return TenantDomainResponse(
            tenant_id=tenant_id,
            organizational_type=None,
            industry_domain=None,
            sub_domain=None,
            company_size=None,
            geographic_scope=None,
            regulatory_requirements=[],
            domain_classified_at=None,
            domain_classified_by=None
        )

    return TenantDomainResponse(
        tenant_id=tenant.id,
        organizational_type=tenant.organizational_type,
        industry_domain=tenant.industry_domain,
        sub_domain=tenant.sub_domain,
        company_size=tenant.company_size,
        geographic_scope=tenant.geographic_scope,
        regulatory_requirements=tenant.regulatory_requirements or [],
        domain_classified_at=tenant.domain_classified_at,
        domain_classified_by=tenant.domain_classified_by
    )


# ============================================================================
# ENDPOINT 3: GET DOMAIN KNOWLEDGE
# ============================================================================

@router.get("/knowledge", response_model=List[KnowledgeResponse])
async def get_domain_knowledge(
    industry: str = Query(...),
    sub_domain: Optional[str] = None,
    knowledge_type: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get industry-specific knowledge

    **Use Cases:**
    - Get typical RTOs for healthcare EHR systems
    - Get common risks for financial services
    - Get regulatory requirements for manufacturing

    **Filters:**
    - `industry`: healthcare, financial, manufacturing, etc.
    - `sub_domain`: hospital, bank, automotive, etc.
    - `knowledge_type`: typical_rto, common_risk, regulatory_requirement, etc.
    """

    # Build query
    conditions = [
        IndustryKnowledge.industry == industry,
        IndustryKnowledge.is_active == True
    ]

    if sub_domain:
        conditions.append(IndustryKnowledge.sub_domain == sub_domain)

    if knowledge_type:
        conditions.append(IndustryKnowledge.knowledge_type == knowledge_type)

    stmt = select(IndustryKnowledge).where(and_(*conditions))

    # Sort by confidence level (using CASE in order_by)
    # High confidence first, then by usage count
    stmt = stmt.order_by(
        IndustryKnowledge.confidence_level.desc(),
        IndustryKnowledge.usage_count.desc()
    ).limit(limit)

    result = await db.execute(stmt)
    items = result.scalars().all()

    return [KnowledgeResponse.from_orm(k) for k in items]


# ============================================================================
# ENDPOINT 4: GET DOMAIN TEMPLATES
# ============================================================================

@router.get("/templates", response_model=List[TemplateResponse])
async def get_domain_templates(
    industry: str = Query(...),
    template_type: Optional[str] = None,
    complexity_level: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get industry-specific templates

    **Template Types:**
    - `bcp_plan` - Business Continuity Plan templates
    - `exercise_scenario` - Exercise scenarios
    - `risk_catalog` - Industry risk catalogs
    - `bia_process` - BIA process templates
    - `checklist` - Compliance checklists

    **Example:** Get all exercise scenarios for healthcare
    ```
    GET /api/governance/domain/templates?industry=healthcare&template_type=exercise_scenario
    ```
    """

    # Build query
    conditions = [
        DomainTemplate.industry == industry,
        DomainTemplate.is_active == True
    ]

    if template_type:
        conditions.append(DomainTemplate.template_type == template_type)

    if complexity_level:
        conditions.append(DomainTemplate.complexity_level == complexity_level)

    stmt = select(DomainTemplate).where(and_(*conditions))

    # Sort by rating (nulls last), then usage count
    stmt = stmt.order_by(
        DomainTemplate.rating.desc().nullslast(),
        DomainTemplate.usage_count.desc()
    ).limit(limit)

    result = await db.execute(stmt)
    items = result.scalars().all()

    return [TemplateResponse.from_orm(t) for t in items]


# ============================================================================
# ENDPOINT 5: GET BENCHMARKS
# ============================================================================

@router.get("/benchmarks/{metric_name}", response_model=BenchmarkResponse)
async def get_industry_benchmark(
    metric_name: str,
    industry: str = Query(...),
    sub_domain: Optional[str] = None,
    company_size: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get industry benchmark for specific metric

    **Common Metrics:**
    - `rto_ehr_system` - RTO for EHR systems (healthcare)
    - `plan_currency_rate` - % plans reviewed in last 12 months
    - `exercise_frequency` - Exercises per year
    - `bia_completion_rate` - % critical processes with BIA

    **Returns:** Statistical distribution (p25, median, p75)

    **Example:**
    ```
    GET /api/governance/domain/benchmarks/rto_ehr_system?industry=healthcare&sub_domain=hospital

    Response:
    {
      "metric_name": "rto_ehr_system",
      "median_value": 4.0,
      "percentile_25": 2.0,
      "percentile_75": 6.0,
      "unit_of_measure": "hours",
      "sample_size": 150
    }
    ```
    """

    # Build query
    conditions = [
        IndustryBenchmark.metric_name == metric_name,
        IndustryBenchmark.industry == industry,
        IndustryBenchmark.is_active == True
    ]

    if sub_domain:
        conditions.append(IndustryBenchmark.sub_domain == sub_domain)

    if company_size:
        conditions.append(IndustryBenchmark.company_size_filter == company_size)

    stmt = select(IndustryBenchmark).where(and_(*conditions))
    result = await db.execute(stmt)
    benchmark = result.scalar_one_or_none()

    if not benchmark:
        raise HTTPException(
            status_code=404,
            detail=f"Benchmark '{metric_name}' not found for industry '{industry}'"
        )

    return BenchmarkResponse.from_orm(benchmark)


# ============================================================================
# ENDPOINT 6: GET RECOMMENDATIONS FOR TENANT
# ============================================================================

@router.get("/recommendations", response_model=RecommendationsResponse)
async def get_tenant_recommendations(
    tenant_id: str = Query(...),
    context_type: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-enhanced recommendations for tenant based on their domain

    **Context Types:**
    - `bia` - Recommendations for Business Impact Analysis
    - `risk` - Risk assessment recommendations
    - `planning` - BC planning recommendations
    - `exercise` - Exercise scenario recommendations

    **Returns:** Top recommendations with relevance scores

    **Example:**
    ```
    GET /api/governance/domain/recommendations?tenant_id=hospital_001&context_type=bia

    Response:
    {
      "tenant_id": "hospital_001",
      "industry": "healthcare",
      "recommendations": [
        {
          "title": "EHR System RTO",
          "knowledge_type": "typical_rto",
          "knowledge_data": {"typical_rto_hours": 4, ...},
          "relevance_score": 95.0,
          "reasoning": "Based on 150 similar hospitals"
        }
      ]
    }
    ```
    """

    # Get tenant domain
    tenant_stmt = select(Tenant).where(Tenant.id == tenant_id)
    tenant_result = await db.execute(tenant_stmt)
    tenant = tenant_result.scalar_one_or_none()

    if not tenant or not tenant.industry_domain:
        raise HTTPException(
            status_code=404,
            detail=f"Tenant '{tenant_id}' domain not classified. Use PATCH /tenant/classify first."
        )

    industry = tenant.industry_domain
    sub_domain = tenant.sub_domain

    # Get relevant knowledge
    conditions = [
        IndustryKnowledge.industry == industry,
        IndustryKnowledge.is_active == True
    ]

    if sub_domain:
        conditions.append(IndustryKnowledge.sub_domain == sub_domain)

    if context_type:
        conditions.append(IndustryKnowledge.knowledge_type.like(f'%{context_type}%'))

    stmt = select(IndustryKnowledge).where(and_(*conditions))
    result = await db.execute(stmt)
    knowledge_items = result.scalars().all()

    # Calculate relevance scores
    recommendations = []
    confidence_scores = {'verified': 100, 'high': 85, 'medium': 70, 'low': 50}

    for k in knowledge_items:
        base_score = confidence_scores.get(k.confidence_level, 70)
        usage_boost = min(k.usage_count * 0.5, 15)  # Up to +15 for usage
        relevance_score = min(base_score + usage_boost, 100)

        recommendations.append(DomainRecommendation(
            knowledge_id=k.id,
            title=k.title,
            knowledge_type=k.knowledge_type,
            description=k.description,
            knowledge_data=k.knowledge_data,
            relevance_score=round(relevance_score, 2),
            reasoning=f"Based on {k.source or 'industry data'}"
        ))

    # Sort by relevance
    recommendations.sort(key=lambda x: x.relevance_score, reverse=True)

    return RecommendationsResponse(
        tenant_id=tenant_id,
        industry=industry,
        sub_domain=sub_domain,
        context_type=context_type,
        recommendations=recommendations[:limit],
        total_count=len(recommendations),
        generated_at=datetime.utcnow()
    )


# ============================================================================
# ENDPOINT 7: LIST AVAILABLE INDUSTRIES
# ============================================================================

@router.get("/industries", response_model=AvailableIndustriesResponse)
async def list_available_industries(db: AsyncSession = Depends(get_db)):
    """
    List all available industries with knowledge coverage

    **Purpose:** Show which industries have knowledge/templates/benchmarks

    **Returns:**
    ```json
    {
      "industries": [
        {
          "industry": "healthcare",
          "knowledge_items": 45,
          "templates": 12,
          "benchmarks": 8,
          "sub_domains": ["hospital", "clinic", "pharmacy"]
        }
      ],
      "total_industries": 5
    }
    ```
    """

    # Aggregate knowledge by industry
    knowledge_stmt = select(
        IndustryKnowledge.industry,
        func.count(IndustryKnowledge.id).label('knowledge_count'),
        func.array_agg(func.distinct(IndustryKnowledge.sub_domain)).label('sub_domains')
    ).where(
        IndustryKnowledge.is_active == True
    ).group_by(IndustryKnowledge.industry)

    knowledge_result = await db.execute(knowledge_stmt)
    knowledge_data = {row.industry: {'count': row.knowledge_count, 'sub_domains': row.sub_domains}
                      for row in knowledge_result}

    # Aggregate templates by industry
    templates_stmt = select(
        DomainTemplate.industry,
        func.count(DomainTemplate.id).label('template_count')
    ).where(
        DomainTemplate.is_active == True
    ).group_by(DomainTemplate.industry)

    templates_result = await db.execute(templates_stmt)
    templates_data = {row.industry: row.template_count for row in templates_result}

    # Aggregate benchmarks by industry
    benchmarks_stmt = select(
        IndustryBenchmark.industry,
        func.count(IndustryBenchmark.id).label('benchmark_count')
    ).where(
        IndustryBenchmark.is_active == True
    ).group_by(IndustryBenchmark.industry)

    benchmarks_result = await db.execute(benchmarks_stmt)
    benchmarks_data = {row.industry: row.benchmark_count for row in benchmarks_result}

    # Build industry info list
    industries = []
    all_industries = set(knowledge_data.keys()) | set(templates_data.keys()) | set(benchmarks_data.keys())

    for ind in all_industries:
        sub_domains = knowledge_data.get(ind, {}).get('sub_domains', []) or []
        # Filter out None values
        sub_domains = [sd for sd in sub_domains if sd is not None]

        industries.append(IndustryInfo(
            industry=ind,
            knowledge_items=knowledge_data.get(ind, {}).get('count', 0),
            templates=templates_data.get(ind, 0),
            benchmarks=benchmarks_data.get(ind, 0),
            sub_domains=sorted(sub_domains)
        ))

    # Sort by knowledge items
    industries.sort(key=lambda x: x.knowledge_items, reverse=True)

    return AvailableIndustriesResponse(
        industries=industries,
        total_industries=len(industries)
    )


# ============================================================================
# ENDPOINT 8: GET ORGANIZATIONAL TYPES (Helper)
# ============================================================================

@router.get("/organizational-types")
async def get_organizational_types():
    """
    Get available organizational types for classification

    **Returns:** List of valid organizational types
    """
    return {
        "organizational_types": [
            {"value": "for_profit", "label": "For-Profit Organization"},
            {"value": "non_profit", "label": "Non-Profit Organization"},
            {"value": "government", "label": "Government Agency"},
            {"value": "educational", "label": "Educational Institution"},
            {"value": "healthcare_provider", "label": "Healthcare Provider"},
            {"value": "financial_institution", "label": "Financial Institution"},
            {"value": "other", "label": "Other"}
        ],
        "company_sizes": [
            {"value": "micro", "label": "Micro (1-10 employees)"},
            {"value": "small", "label": "Small (11-50 employees)"},
            {"value": "medium", "label": "Medium (51-250 employees)"},
            {"value": "large", "label": "Large (251-1000 employees)"},
            {"value": "enterprise", "label": "Enterprise (1000+ employees)"}
        ],
        "industries": [
            {"value": "healthcare", "label": "Healthcare"},
            {"value": "financial", "label": "Financial Services"},
            {"value": "manufacturing", "label": "Manufacturing"},
            {"value": "retail", "label": "Retail"},
            {"value": "it", "label": "IT & Technology"},
            {"value": "energy", "label": "Energy & Utilities"},
            {"value": "transport", "label": "Transportation & Logistics"},
            {"value": "government", "label": "Government"},
            {"value": "education", "label": "Education"},
            {"value": "other", "label": "Other"}
        ]
    }
