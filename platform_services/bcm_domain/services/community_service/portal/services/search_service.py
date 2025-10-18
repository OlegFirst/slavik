"""
Search Service - Full-Text Search
PostgreSQL full-text search for knowledge articles
"""

from typing import List, Optional, Tuple
from sqlalchemy import select, func, text, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import KnowledgeArticle


class SearchService:
    """
    Full-text search for knowledge articles

    MVP: PostgreSQL full-text search with ts_rank
    Phase 2: Elasticsearch integration for advanced features
    """

    async def search_articles(
        self,
        db: AsyncSession,
        query: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        verified_only: bool = False,
        published_only: bool = True,
        tenant_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[dict], int]:
        """
        Full-text search articles with PostgreSQL

        Args:
            db: Database session
            query: Search query
            category: Filter by category
            tags: Filter by tags
            verified_only: Only show verified articles
            published_only: Only show published articles
            tenant_id: Filter by tenant (None for public only)
            page: Page number (1-indexed)
            page_size: Results per page

        Returns:
            Tuple of (results list, total count)
        """
        # Build search query with ts_rank for relevance scoring
        search_vector = func.to_tsvector(
            'english',
            func.concat(
                KnowledgeArticle.title,
                ' ',
                KnowledgeArticle.summary,
                ' ',
                KnowledgeArticle.content
            )
        )
        search_query_ts = func.plainto_tsquery('english', query)

        # Base query with relevance score
        stmt = select(
            KnowledgeArticle,
            func.ts_rank(search_vector, search_query_ts).label('relevance_score')
        ).where(
            search_vector.op('@@')(search_query_ts)
        )

        # Apply filters
        filters = []

        if published_only:
            filters.append(KnowledgeArticle.published == True)

        if verified_only:
            filters.append(KnowledgeArticle.verification_status == 'verified')

        if category:
            filters.append(KnowledgeArticle.category == category)

        if tags:
            # JSONB contains all specified tags
            for tag in tags:
                filters.append(
                    KnowledgeArticle.tags.op('@>')(f'["{tag}"]')
                )

        # Tenant filtering (public or specific tenant)
        if tenant_id:
            filters.append(
                or_(
                    KnowledgeArticle.tenant_id == tenant_id,
                    KnowledgeArticle.tenant_id.is_(None)
                )
            )
        else:
            filters.append(KnowledgeArticle.tenant_id.is_(None))

        if filters:
            stmt = stmt.where(and_(*filters))

        # Order by relevance
        stmt = stmt.order_by(text('relevance_score DESC'))

        # Get total count (before pagination)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Pagination
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        # Execute query
        result = await db.execute(stmt)
        rows = result.all()

        # Format results
        results = []
        for article, relevance_score in rows:
            results.append({
                'article': article,
                'relevance_score': float(relevance_score)
            })

        return results, total

    async def get_popular_tags(
        self,
        db: AsyncSession,
        limit: int = 20,
        published_only: bool = True
    ) -> List[Tuple[str, int]]:
        """
        Get most popular tags with usage counts

        Args:
            db: Database session
            limit: Maximum number of tags
            published_only: Only count published articles

        Returns:
            List of (tag, count) tuples
        """
        # This requires unnesting JSONB array
        # PostgreSQL: jsonb_array_elements_text(tags)

        query = text("""
            SELECT tag, COUNT(*) as count
            FROM portal.knowledge_articles,
                 jsonb_array_elements_text(tags) as tag
            WHERE published = :published
            GROUP BY tag
            ORDER BY count DESC
            LIMIT :limit
        """)

        result = await db.execute(
            query,
            {'published': published_only, 'limit': limit}
        )

        return [(row[0], row[1]) for row in result.all()]

    async def get_related_articles(
        self,
        db: AsyncSession,
        article_id: int,
        limit: int = 5
    ) -> List[KnowledgeArticle]:
        """
        Find related articles based on tags and category

        Args:
            db: Database session
            article_id: Source article ID
            limit: Maximum number of results

        Returns:
            List of related articles
        """
        # Get source article
        result = await db.execute(
            select(KnowledgeArticle).where(KnowledgeArticle.id == article_id)
        )
        source_article = result.scalar_one_or_none()

        if not source_article:
            return []

        # Find articles with similar tags or same category
        stmt = select(KnowledgeArticle).where(
            and_(
                KnowledgeArticle.id != article_id,
                KnowledgeArticle.published == True,
                or_(
                    KnowledgeArticle.category == source_article.category,
                    KnowledgeArticle.tags.op('&&')(source_article.tags)  # JSONB overlap
                )
            )
        ).order_by(
            KnowledgeArticle.usefulness_score.desc()
        ).limit(limit)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def autocomplete_search(
        self,
        db: AsyncSession,
        partial_query: str,
        limit: int = 10
    ) -> List[str]:
        """
        Autocomplete search suggestions based on article titles

        Args:
            db: Database session
            partial_query: Partial search query
            limit: Maximum suggestions

        Returns:
            List of title suggestions
        """
        stmt = select(KnowledgeArticle.title).where(
            and_(
                KnowledgeArticle.published == True,
                KnowledgeArticle.title.ilike(f'%{partial_query}%')
            )
        ).order_by(
            KnowledgeArticle.view_count.desc()
        ).limit(limit)

        result = await db.execute(stmt)
        return [row[0] for row in result.all()]
