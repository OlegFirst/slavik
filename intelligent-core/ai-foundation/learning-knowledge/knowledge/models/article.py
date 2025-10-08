"""
Knowledge Article Models

Extracted from Odoo bcm_ai_consultant/models/knowledge_base.py
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import List, Optional, Dict, Any


class KnowledgeCategory(Enum):
    """Categories of BCM knowledge"""
    ISO22301 = "iso22301"
    BEST_PRACTICES = "best_practices"
    PROCEDURES = "procedures"
    TEMPLATES = "templates"
    CASE_STUDIES = "case_studies"
    REGULATIONS = "regulations"
    INDUSTRY_SPECIFIC = "industry_specific"


class KnowledgeType(Enum):
    """Types of knowledge content"""
    TEXT = "text"
    DOCUMENT = "document"
    TEMPLATE = "template"
    CHECKLIST = "checklist"
    FAQ = "faq"


class DomainType(Enum):
    """Organization domain types"""
    ALL = "all"
    CORPORATE = "corporate"
    GOVERNMENT = "government"
    NPO = "npo"
    CRITICAL_INFRASTRUCTURE = "critical_infrastructure"


class UsageType(Enum):
    """Types of knowledge usage"""
    REFERENCED = "referenced"
    QUOTED = "quoted"
    TEMPLATE_USED = "template_used"
    PROCEDURE_FOLLOWED = "procedure_followed"


@dataclass
class KnowledgeArticle:
    """
    Knowledge base article with metadata and quality tracking
    """
    id: str
    name: str
    category: KnowledgeCategory
    knowledge_type: KnowledgeType

    # Content
    content: str  # HTML or markdown
    summary: str
    keywords: List[str] = field(default_factory=list)

    # Metadata
    author: str = "System"
    source: Optional[str] = None  # Original source (e.g., "ISO 22301:2019")
    domain_applicability: DomainType = DomainType.ALL
    industry_specific: Optional[str] = None  # e.g., "healthcare", "finance"

    # Quality metrics
    quality_score: float = 0.0  # 0-10
    effectiveness_rating: float = 0.0  # 0-10
    usage_count: int = 0
    helpful_votes: int = 0
    not_helpful_votes: int = 0

    # Timestamps
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None

    # Tags and classification
    tags: List[str] = field(default_factory=list)
    related_articles: List[str] = field(default_factory=list)  # IDs of related articles

    # Access control
    is_public: bool = True
    required_role: Optional[str] = None

    def calculate_quality_score(self) -> float:
        """Calculate overall quality score based on metrics"""
        if self.usage_count == 0:
            return self.effectiveness_rating

        # Helpful ratio
        total_votes = self.helpful_votes + self.not_helpful_votes
        helpful_ratio = self.helpful_votes / total_votes if total_votes > 0 else 0.5

        # Combine effectiveness and helpful ratio
        score = (self.effectiveness_rating * 0.6) + (helpful_ratio * 10 * 0.4)

        return round(min(score, 10.0), 1)

    def mark_as_used(self, usage_type: UsageType):
        """Mark article as used"""
        self.usage_count += 1
        self.last_used = datetime.now()

    def add_feedback(self, helpful: bool):
        """Add user feedback"""
        if helpful:
            self.helpful_votes += 1
        else:
            self.not_helpful_votes += 1

        # Recalculate quality score
        self.quality_score = self.calculate_quality_score()
