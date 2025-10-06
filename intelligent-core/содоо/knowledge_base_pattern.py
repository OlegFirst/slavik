"""
Knowledge Base Pattern - Extracted from Odoo bcm_ai_consultant

Structured knowledge management system for AI consultants with:
- Categorized knowledge articles
- Quality scoring and effectiveness tracking
- Multi-type content support (text, documents, templates, checklists, FAQs)
- Usage analytics and ratings
- ISO standard knowledge base
- Industry-specific knowledge

Original Source: bcm_ai_consultant/models/knowledge_base.py
Extracted: 2025-10-05
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# ========== Enums ==========

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


# ========== Data Models ==========

@dataclass
class KnowledgeArticle:
    """
    Knowledge base article

    Represents a single piece of knowledge with metadata
    """
    id: str
    name: str
    category: KnowledgeCategory
    knowledge_type: KnowledgeType

    # Content
    content: str  # HTML or markdown
    summary: str
    keywords: List[str] = field(default_factory=list)

    # Structured data
    structured_data: Optional[Dict[str, Any]] = None

    # Source and references
    source: Optional[str] = None
    reference_url: Optional[str] = None
    attachments: List[str] = field(default_factory=list)

    # Applicability
    domain_types: DomainType = DomainType.ALL
    industry_tags: List[str] = field(default_factory=list)

    # Quality
    quality_score: float = 0.0  # 0-10
    last_reviewed: Optional[date] = None
    reviewer: Optional[str] = None
    is_approved: bool = False

    # Usage statistics
    usage_count: int = 0
    effectiveness_rating: float = 0.0  # 0-5

    # System
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class KnowledgeUsage:
    """
    Tracks usage of knowledge in consultations

    Records when and how knowledge was used
    """
    knowledge_id: str
    session_id: str
    message_id: Optional[str] = None
    usage_type: UsageType = UsageType.REFERENCED
    rating: Optional[int] = None  # 1-5
    feedback: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


# ========== Knowledge Base Repository ==========

class KnowledgeBaseRepository:
    """
    Repository for BCM knowledge articles

    Manages storage, retrieval, and search of knowledge
    """

    def __init__(self):
        self.articles: Dict[str, KnowledgeArticle] = {}
        self.usage_records: List[KnowledgeUsage] = []

    def add_article(self, article: KnowledgeArticle):
        """Add knowledge article to repository"""
        self.articles[article.id] = article
        logger.info(f"Added knowledge article: {article.name}")

    def get_article(self, article_id: str) -> Optional[KnowledgeArticle]:
        """Get article by ID"""
        return self.articles.get(article_id)

    def search(
        self,
        query: str,
        category: Optional[KnowledgeCategory] = None,
        domain_type: Optional[DomainType] = None,
        limit: int = 10
    ) -> List[KnowledgeArticle]:
        """
        Search knowledge base

        Args:
            query: Search query string
            category: Filter by category
            domain_type: Filter by domain type
            limit: Maximum results

        Returns:
            List of matching articles sorted by relevance
        """
        query_lower = query.lower()
        results = []

        for article in self.articles.values():
            # Skip inactive or unapproved articles
            if not article.active or not article.is_approved:
                continue

            # Category filter
            if category and article.category != category:
                continue

            # Domain filter
            if domain_type and domain_type != DomainType.ALL:
                if article.domain_types not in [DomainType.ALL, domain_type]:
                    continue

            # Text search
            score = 0
            if query_lower in article.name.lower():
                score += 10
            if query_lower in article.summary.lower():
                score += 5
            if query_lower in article.content.lower():
                score += 3
            if any(query_lower in kw.lower() for kw in article.keywords):
                score += 7

            if score > 0:
                results.append((score, article))

        # Sort by score (primary) and effectiveness (secondary)
        results.sort(
            key=lambda x: (x[0], x[1].effectiveness_rating, x[1].usage_count),
            reverse=True
        )

        return [article for _, article in results[:limit]]

    def record_usage(self, usage: KnowledgeUsage):
        """Record knowledge usage"""
        self.usage_records.append(usage)

        # Update article statistics
        article = self.get_article(usage.knowledge_id)
        if article:
            article.usage_count += 1

            # Update effectiveness rating
            if usage.rating:
                self._update_effectiveness(article)

    def _update_effectiveness(self, article: KnowledgeArticle):
        """Update article effectiveness rating based on usage feedback"""
        # Get all usage records for this article with ratings
        rated_usages = [
            u for u in self.usage_records
            if u.knowledge_id == article.id and u.rating is not None
        ]

        if rated_usages:
            ratings = [u.rating for u in rated_usages]
            article.effectiveness_rating = sum(ratings) / len(ratings)

    def mark_reviewed(self, article_id: str, reviewer: str):
        """Mark article as reviewed and approved"""
        article = self.get_article(article_id)
        if article:
            article.last_reviewed = date.today()
            article.reviewer = reviewer
            article.is_approved = True


# ========== Default Knowledge Creator ==========

class DefaultKnowledgeCreator:
    """
    Creates default knowledge base for BCM platform

    Provides standard ISO 22301 and BCM best practices knowledge
    """

    @staticmethod
    def create_iso22301_basics() -> KnowledgeArticle:
        """Create ISO 22301 basics article"""
        return KnowledgeArticle(
            id="kb_iso22301_001",
            name="ISO 22301:2019 - Основы стандарта",
            category=KnowledgeCategory.ISO22301,
            knowledge_type=KnowledgeType.TEXT,
            content="""
<h3>ISO 22301:2019 - Системы менеджмента непрерывности бизнеса</h3>
<p>Международный стандарт, который устанавливает требования к системе управления непрерывностью бизнеса.</p>

<h4>Ключевые принципы:</h4>
<ul>
    <li>Лидерство и приверженность руководства</li>
    <li>Планирование и управление рисками</li>
    <li>Поддержка и ресурсы</li>
    <li>Операционная деятельность</li>
    <li>Оценка результатов</li>
    <li>Улучшение</li>
</ul>

<h4>Структура стандарта:</h4>
<ol>
    <li>Контекст организации (Clause 4)</li>
    <li>Лидерство (Clause 5)</li>
    <li>Планирование (Clause 6)</li>
    <li>Поддержка (Clause 7)</li>
    <li>Операционная деятельность (Clause 8)</li>
    <li>Оценка результатов (Clause 9)</li>
    <li>Улучшение (Clause 10)</li>
</ol>
            """,
            summary="Базовые принципы и требования стандарта ISO 22301:2019",
            keywords=["ISO 22301", "BCMS", "непрерывность бизнеса", "стандарт"],
            source="ISO 22301:2019",
            quality_score=9.5,
            is_approved=True
        )

    @staticmethod
    def create_bia_procedure() -> KnowledgeArticle:
        """Create BIA procedure checklist"""
        return KnowledgeArticle(
            id="kb_bia_001",
            name="Анализ влияния на бизнес (BIA)",
            category=KnowledgeCategory.PROCEDURES,
            knowledge_type=KnowledgeType.CHECKLIST,
            content="""
<h3>Этапы проведения BIA</h3>

<h4>1. Подготовка</h4>
<ul>
    <li>Определение целей BIA</li>
    <li>Формирование команды BIA</li>
    <li>Планирование интервью</li>
</ul>

<h4>2. Идентификация критически важных функций</h4>
<ol>
    <li>Определение всех бизнес-процессов организации</li>
    <li>Классификация процессов по критичности</li>
    <li>Определение владельцев процессов</li>
    <li>Документирование зависимостей</li>
</ol>

<h4>3. Анализ зависимостей</h4>
<ul>
    <li>Персонал (ключевые сотрудники)</li>
    <li>Технологии (IT-системы, оборудование)</li>
    <li>Помещения (офисы, производственные площадки)</li>
    <li>Поставщики (критичные партнеры)</li>
    <li>Информация (данные, документы)</li>
</ul>

<h4>4. Оценка временных параметров</h4>
<ul>
    <li>RTO (Recovery Time Objective) - целевое время восстановления</li>
    <li>RPO (Recovery Point Objective) - допустимая потеря данных</li>
    <li>MTPD (Maximum Tolerable Period of Disruption) - максимально допустимое время простоя</li>
</ul>

<h4>5. Расчет потенциальных потерь</h4>
<ul>
    <li>Финансовые потери (прямые и косвенные)</li>
    <li>Операционные последствия</li>
    <li>Репутационный ущерб</li>
    <li>Нормативные последствия</li>
</ul>

<h4>6. Документирование результатов</h4>
<ul>
    <li>Отчет BIA</li>
    <li>Матрица критичности процессов</li>
    <li>Карта зависимостей</li>
    <li>Рекомендации для планирования BCM</li>
</ul>
            """,
            summary="Пошаговая процедура проведения анализа влияния на бизнес",
            keywords=["BIA", "анализ влияния", "критические функции", "RTO", "RPO"],
            source="BCM Best Practices",
            quality_score=8.5,
            is_approved=True
        )

    @staticmethod
    def create_rto_guidelines() -> KnowledgeArticle:
        """Create RTO determination guidelines"""
        return KnowledgeArticle(
            id="kb_rto_001",
            name="Руководство по определению RTO",
            category=KnowledgeCategory.BEST_PRACTICES,
            knowledge_type=KnowledgeType.TEXT,
            content="""
<h3>Рекомендации по определению RTO (Recovery Time Objective)</h3>

<h4>Категории критичности и типовые RTO:</h4>

<table>
    <tr>
        <th>Уровень</th>
        <th>Описание</th>
        <th>Типовое RTO</th>
    </tr>
    <tr>
        <td>Tier 1 - Критичный</td>
        <td>Процессы, критичные для выживания организации</td>
        <td>0-4 часа</td>
    </tr>
    <tr>
        <td>Tier 2 - Важный</td>
        <td>Важные процессы с существенным влиянием</td>
        <td>4-24 часа</td>
    </tr>
    <tr>
        <td>Tier 3 - Средний</td>
        <td>Процессы с умеренным влиянием</td>
        <td>1-3 дня</td>
    </tr>
    <tr>
        <td>Tier 4 - Низкий</td>
        <td>Некритичные процессы</td>
        <td>3-7 дней</td>
    </tr>
</table>

<h4>Факторы при определении RTO:</h4>
<ul>
    <li>Финансовые потери за единицу времени</li>
    <li>Нормативные требования</li>
    <li>Репутационные риски</li>
    <li>Договорные обязательства (SLA)</li>
    <li>Зависимость других процессов</li>
</ul>

<h4>Типичные ошибки:</h4>
<ul>
    <li>RTO меньше технической возможности восстановления</li>
    <li>Игнорирование стоимости достижения RTO</li>
    <li>Отсутствие обоснования RTO</li>
    <li>RTO не согласован с RPO</li>
</ul>
            """,
            summary="Руководство по определению целевого времени восстановления",
            keywords=["RTO", "целевое время", "восстановление", "критичность"],
            source="BCI Good Practice Guidelines",
            quality_score=9.0,
            is_approved=True
        )

    @classmethod
    def create_default_knowledge_base(cls) -> List[KnowledgeArticle]:
        """Create complete default knowledge base"""
        return [
            cls.create_iso22301_basics(),
            cls.create_bia_procedure(),
            cls.create_rto_guidelines(),
        ]


# ========== Knowledge Search Engine ==========

class KnowledgeSearchEngine:
    """
    Advanced search engine for knowledge base

    Supports semantic search, filtering, and ranking
    """

    def __init__(self, repository: KnowledgeBaseRepository):
        self.repository = repository

    def search(
        self,
        query: str,
        category: Optional[KnowledgeCategory] = None,
        knowledge_type: Optional[KnowledgeType] = None,
        domain_type: Optional[DomainType] = None,
        industry: Optional[str] = None,
        limit: int = 10
    ) -> List[KnowledgeArticle]:
        """
        Advanced search with multiple filters

        Args:
            query: Search query
            category: Filter by category
            knowledge_type: Filter by type
            domain_type: Filter by domain
            industry: Filter by industry tag
            limit: Maximum results

        Returns:
            Ranked list of matching articles
        """
        # Basic search from repository
        results = self.repository.search(query, category, domain_type, limit * 2)

        # Additional filters
        if knowledge_type:
            results = [a for a in results if a.knowledge_type == knowledge_type]

        if industry:
            results = [
                a for a in results
                if industry.lower() in [tag.lower() for tag in a.industry_tags]
            ]

        return results[:limit]

    def get_related_articles(
        self,
        article_id: str,
        limit: int = 5
    ) -> List[KnowledgeArticle]:
        """
        Get articles related to a given article

        Uses keywords and category for similarity
        """
        article = self.repository.get_article(article_id)
        if not article:
            return []

        # Search by keywords
        related = []
        for keyword in article.keywords:
            found = self.repository.search(keyword, article.category, limit=limit)
            related.extend([a for a in found if a.id != article_id])

        # Remove duplicates and sort by effectiveness
        seen = set()
        unique_related = []
        for a in related:
            if a.id not in seen:
                seen.add(a.id)
                unique_related.append(a)

        unique_related.sort(key=lambda a: a.effectiveness_rating, reverse=True)
        return unique_related[:limit]


# ========== Usage Example ==========

def example_knowledge_base():
    """Example of using the knowledge base system"""

    # Create repository
    repo = KnowledgeBaseRepository()

    # Load default knowledge
    default_articles = DefaultKnowledgeCreator.create_default_knowledge_base()
    for article in default_articles:
        repo.add_article(article)

    # Create search engine
    search = KnowledgeSearchEngine(repo)

    # Search for BIA information
    results = search.search("анализ влияния", category=KnowledgeCategory.PROCEDURES)
    print(f"Found {len(results)} articles about BIA")

    # Record usage
    usage = KnowledgeUsage(
        knowledge_id="kb_bia_001",
        session_id="session_123",
        usage_type=UsageType.PROCEDURE_FOLLOWED,
        rating=5,
        feedback="Very helpful procedure!"
    )
    repo.record_usage(usage)

    # Get related articles
    related = search.get_related_articles("kb_bia_001")
    print(f"Found {len(related)} related articles")


if __name__ == "__main__":
    example_knowledge_base()
