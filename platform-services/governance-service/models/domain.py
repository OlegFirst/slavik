"""
Domain Intelligence - Pydantic Schemas
Clean, validated API request/response models
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


# ===== ENUMS =====

class OrganizationalType(str, Enum):
    FOR_PROFIT = "for_profit"
    NON_PROFIT = "non_profit"
    GOVERNMENT = "government"
    EDUCATIONAL = "educational"
    HEALTHCARE_PROVIDER = "healthcare_provider"
    FINANCIAL_INSTITUTION = "financial_institution"
    OTHER = "other"


class CompanySize(str, Enum):
    MICRO = "micro"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class IndustryDomain(str, Enum):
    HEALTHCARE = "healthcare"
    FINANCIAL = "financial"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    IT = "it"
    ENERGY = "energy"
    TRANSPORT = "transport"
    GOVERNMENT = "government"
    EDUCATION = "education"
    OTHER = "other"


# ===== TENANT DOMAIN CLASSIFICATION =====

class TenantDomainClassification(BaseModel):
    """Classify tenant's industry domain"""
    organizational_type: OrganizationalType
    industry_domain: IndustryDomain
    sub_domain: Optional[str] = None
    company_size: CompanySize
    geographic_scope: Optional[str] = None
    regulatory_requirements: List[str] = []


class TenantDomainResponse(BaseModel):
    """Tenant domain classification response"""
    tenant_id: str
    organizational_type: Optional[str]
    industry_domain: Optional[str]
    sub_domain: Optional[str]
    company_size: Optional[str]
    geographic_scope: Optional[str]
    regulatory_requirements: List[str] = []
    domain_classified_at: Optional[datetime]
    domain_classified_by: Optional[str]

    class Config:
        from_attributes = True


# ===== INDUSTRY KNOWLEDGE =====

class KnowledgeCreate(BaseModel):
    """Create industry knowledge"""
    industry: str
    sub_domain: Optional[str] = None
    knowledge_type: str
    title: str
    description: Optional[str] = None
    knowledge_data: Dict[str, Any]
    source: Optional[str] = None
    confidence_level: str = "medium"
    tags: List[str] = []


class KnowledgeResponse(BaseModel):
    """Industry knowledge response"""
    id: int
    industry: str
    sub_domain: Optional[str]
    knowledge_type: str
    title: str
    description: Optional[str]
    knowledge_data: Dict[str, Any]
    source: Optional[str]
    confidence_level: Optional[str]
    usage_count: int
    is_active: bool
    tags: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ===== DOMAIN TEMPLATES =====

class TemplateResponse(BaseModel):
    """Domain template response"""
    id: int
    industry: str
    sub_domain: Optional[str]
    template_type: str
    template_name: str
    template_code: str
    description: Optional[str]
    complexity_level: Optional[str]
    template_data: Dict[str, Any]
    usage_count: int
    rating: Optional[float]
    version: str
    tags: List[str]

    class Config:
        from_attributes = True


# ===== BENCHMARKS =====

class BenchmarkResponse(BaseModel):
    """Industry benchmark response"""
    id: int
    industry: str
    sub_domain: Optional[str]
    metric_name: str
    sample_size: int
    median_value: Optional[float]
    percentile_25: Optional[float]
    percentile_75: Optional[float]
    unit_of_measure: Optional[str]
    metric_description: Optional[str]
    confidence_level: Optional[str]

    class Config:
        from_attributes = True


# ===== RECOMMENDATIONS =====

class DomainRecommendation(BaseModel):
    """AI-enhanced domain recommendation"""
    knowledge_id: int
    title: str
    knowledge_type: str
    description: Optional[str]
    knowledge_data: Dict[str, Any]
    relevance_score: float
    reasoning: Optional[str] = None


class RecommendationsResponse(BaseModel):
    """Domain recommendations for tenant"""
    tenant_id: str
    industry: str
    sub_domain: Optional[str]
    context_type: Optional[str]
    recommendations: List[DomainRecommendation]
    total_count: int
    generated_at: datetime


# ===== LOOKUPS =====

class IndustryInfo(BaseModel):
    """Available industry information"""
    industry: str
    knowledge_items: int
    templates: int
    benchmarks: int
    sub_domains: List[str] = []


class AvailableIndustriesResponse(BaseModel):
    """List of available industries"""
    industries: List[IndustryInfo]
    total_industries: int
