"""
Knowledge Base Models

Data models for structured knowledge management
Extracted from Odoo bcm_ai_consultant
"""

from .article import (
    KnowledgeArticle,
    KnowledgeCategory,
    KnowledgeType,
    DomainType,
    UsageType
)
from .analytics import (
    KnowledgeUsageRecord,
    KnowledgeAnalytics,
    QualityMetrics
)

__all__ = [
    'KnowledgeArticle',
    'KnowledgeCategory',
    'KnowledgeType',
    'DomainType',
    'UsageType',
    'KnowledgeUsageRecord',
    'KnowledgeAnalytics',
    'QualityMetrics',
]
