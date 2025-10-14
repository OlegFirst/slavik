"""
Knowledge Analytics Models

Track usage and effectiveness of knowledge articles
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

from .article import UsageType


@dataclass
class KnowledgeUsageRecord:
    """Record of knowledge article usage"""
    article_id: str
    usage_type: UsageType
    user_id: Optional[str]
    context: str  # What problem/task was being solved
    timestamp: datetime = field(default_factory=datetime.now)
    was_helpful: Optional[bool] = None  # User feedback
    feedback_comment: Optional[str] = None


@dataclass
class QualityMetrics:
    """Quality metrics for knowledge articles"""
    total_articles: int
    avg_quality_score: float
    high_quality_count: int  # score >= 8
    low_quality_count: int  # score < 5
    unused_articles: int  # usage_count == 0
    most_used_articles: List[Dict[str, any]]


@dataclass
class KnowledgeAnalytics:
    """
    Analytics for knowledge base performance
    """
    # Usage stats
    total_usage: int = 0
    usage_by_type: Dict[str, int] = field(default_factory=dict)
    usage_by_category: Dict[str, int] = field(default_factory=dict)

    # Quality stats
    quality_metrics: Optional[QualityMetrics] = None

    # Trends
    usage_trend_7d: List[int] = field(default_factory=list)  # Last 7 days
    usage_trend_30d: List[int] = field(default_factory=list)  # Last 30 days

    # Top performers
    top_articles: List[Dict[str, any]] = field(default_factory=list)
    top_categories: List[Dict[str, any]] = field(default_factory=list)

    # Problem areas
    low_rated_articles: List[Dict[str, any]] = field(default_factory=list)
    articles_needing_update: List[str] = field(default_factory=list)

    def get_usage_growth_rate(self) -> float:
        """Calculate usage growth rate (7d vs previous 7d)"""
        if len(self.usage_trend_7d) < 14:
            return 0.0

        current_week = sum(self.usage_trend_7d[-7:])
        previous_week = sum(self.usage_trend_7d[-14:-7])

        if previous_week == 0:
            return 100.0 if current_week > 0 else 0.0

        return ((current_week - previous_week) / previous_week) * 100
