"""
Passive Learning Database Repository

Repository для работы с данными Passive Learning System:
- Learning Events (event log)
- Learning Insights (accumulated insights)
- Organization Contexts (pre-built contexts)
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from .models import (
    LearningEventModel,
    LearningInsightModel,
    OrganizationContextModel
)

logger = logging.getLogger(__name__)


class LearningRepository:
    """
    Repository for Passive Learning database operations
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    # ============================================
    # LEARNING EVENTS
    # ============================================

    async def create_event(
        self,
        event_data: Dict[str, Any]
    ) -> LearningEventModel:
        """
        Create learning event

        Args:
            event_data: Event data

        Returns:
            Created event model
        """
        event = LearningEventModel(**event_data)
        self.session.add(event)
        await self.session.flush()

        logger.info(
            f"Created learning event: {event.event_id} "
            f"(twin={event.twin_id}, source={event.source})"
        )

        return event

    async def get_event(
        self,
        event_id: str
    ) -> Optional[LearningEventModel]:
        """Get event by ID"""
        stmt = select(LearningEventModel).where(
            LearningEventModel.event_id == event_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_events_for_twin(
        self,
        twin_id: str,
        source: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[LearningEventModel]:
        """
        Get learning events for twin

        Args:
            twin_id: Twin ID
            source: Filter by source (bia, risk, incident, etc.)
            since: Get events after this datetime
            limit: Max results

        Returns:
            List of learning events
        """
        stmt = select(LearningEventModel).where(
            LearningEventModel.twin_id == twin_id
        )

        if source:
            stmt = stmt.where(LearningEventModel.source == source)

        if since:
            stmt = stmt.where(LearningEventModel.created_at >= since)

        stmt = stmt.order_by(
            LearningEventModel.created_at.desc()
        ).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_event_count(
        self,
        twin_id: str,
        source: Optional[str] = None
    ) -> int:
        """Get count of events for twin"""
        stmt = select(func.count(LearningEventModel.event_id)).where(
            LearningEventModel.twin_id == twin_id
        )

        if source:
            stmt = stmt.where(LearningEventModel.source == source)

        count = await self.session.scalar(stmt)
        return count or 0

    async def get_event_sources(
        self,
        twin_id: str
    ) -> List[str]:
        """Get unique event sources for twin"""
        stmt = select(
            LearningEventModel.source.distinct()
        ).where(
            LearningEventModel.twin_id == twin_id
        )

        result = await self.session.execute(stmt)
        return [row[0] for row in result]

    # ============================================
    # LEARNING INSIGHTS
    # ============================================

    async def upsert_insight(
        self,
        insight_data: Dict[str, Any]
    ) -> LearningInsightModel:
        """
        Create or update learning insight

        Uses PostgreSQL INSERT ... ON CONFLICT ... UPDATE

        Args:
            insight_data: Insight data (must include twin_id and insight_type)

        Returns:
            Created or updated insight model
        """
        # PostgreSQL upsert
        stmt = insert(LearningInsightModel).values(**insight_data)

        # On conflict (twin_id, insight_type), update
        stmt = stmt.on_conflict_do_update(
            index_elements=['twin_id', 'insight_type'],
            set_={
                'insight_value': stmt.excluded.insight_value,
                'confidence': stmt.excluded.confidence,
                'source_event_count': stmt.excluded.source_event_count,
                'last_updated_from_event_id': stmt.excluded.last_updated_from_event_id,
                'updated_at': datetime.utcnow()
            }
        ).returning(LearningInsightModel)

        result = await self.session.execute(stmt)
        insight = result.scalar_one()

        await self.session.flush()

        logger.info(
            f"Upserted insight: {insight.insight_type} for twin {insight.twin_id}"
        )

        return insight

    async def get_insight(
        self,
        twin_id: str,
        insight_type: str
    ) -> Optional[LearningInsightModel]:
        """Get specific insight"""
        stmt = select(LearningInsightModel).where(
            and_(
                LearningInsightModel.twin_id == twin_id,
                LearningInsightModel.insight_type == insight_type
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_insights(
        self,
        twin_id: str
    ) -> List[LearningInsightModel]:
        """Get all insights for twin"""
        stmt = select(LearningInsightModel).where(
            LearningInsightModel.twin_id == twin_id
        ).order_by(
            LearningInsightModel.updated_at.desc()
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_insights_dict(
        self,
        twin_id: str
    ) -> Dict[str, Any]:
        """
        Get all insights as dictionary

        Returns:
            Dict mapping insight_type -> insight_value
        """
        insights = await self.get_all_insights(twin_id)

        return {
            insight.insight_type: insight.insight_value
            for insight in insights
        }

    async def delete_insight(
        self,
        twin_id: str,
        insight_type: str
    ) -> bool:
        """Delete specific insight"""
        stmt = delete(LearningInsightModel).where(
            and_(
                LearningInsightModel.twin_id == twin_id,
                LearningInsightModel.insight_type == insight_type
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    # ============================================
    # ORGANIZATION CONTEXTS (CACHE)
    # ============================================

    async def upsert_context(
        self,
        context_data: Dict[str, Any]
    ) -> OrganizationContextModel:
        """
        Create or update organization context

        Uses PostgreSQL UPSERT

        Args:
            context_data: Context data (must include twin_id)

        Returns:
            Created or updated context model
        """
        # PostgreSQL upsert
        stmt = insert(OrganizationContextModel).values(**context_data)

        # On conflict (twin_id), update all fields
        update_dict = {
            key: stmt.excluded[key]
            for key in context_data.keys()
            if key not in ['twin_id', 'tenant_id', 'created_at']
        }
        update_dict['last_updated'] = datetime.utcnow()

        stmt = stmt.on_conflict_do_update(
            index_elements=['twin_id'],
            set_=update_dict
        ).returning(OrganizationContextModel)

        result = await self.session.execute(stmt)
        context = result.scalar_one()

        await self.session.flush()

        logger.info(
            f"Upserted context for twin {context.twin_id} "
            f"(confidence={context.confidence_score:.2f})"
        )

        return context

    async def get_context(
        self,
        twin_id: str
    ) -> Optional[OrganizationContextModel]:
        """Get organization context"""
        stmt = select(OrganizationContextModel).where(
            OrganizationContextModel.twin_id == twin_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_context(
        self,
        twin_id: str
    ) -> bool:
        """Delete organization context"""
        stmt = delete(OrganizationContextModel).where(
            OrganizationContextModel.twin_id == twin_id
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def get_stale_contexts(
        self,
        older_than_hours: int = 24
    ) -> List[OrganizationContextModel]:
        """
        Get contexts that haven't been updated recently

        Args:
            older_than_hours: Consider stale if not updated in X hours

        Returns:
            List of stale contexts
        """
        cutoff = datetime.utcnow() - timedelta(hours=older_than_hours)

        stmt = select(OrganizationContextModel).where(
            OrganizationContextModel.last_updated < cutoff
        ).order_by(
            OrganizationContextModel.last_updated.asc()
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_similar_contexts(
        self,
        twin_id: str,
        limit: int = 10
    ) -> List[OrganizationContextModel]:
        """
        Get similar organization contexts

        Simple similarity based on shared attributes

        Args:
            twin_id: Reference twin ID
            limit: Max results

        Returns:
            List of similar contexts
        """
        # Get reference context
        ref_context = await self.get_context(twin_id)
        if not ref_context:
            return []

        stmt = select(OrganizationContextModel).where(
            OrganizationContextModel.twin_id != twin_id
        )

        # Filter by similar attributes
        conditions = []

        if ref_context.organizational_culture:
            conditions.append(
                OrganizationContextModel.organizational_culture ==
                ref_context.organizational_culture
            )

        if ref_context.risk_appetite:
            conditions.append(
                OrganizationContextModel.risk_appetite ==
                ref_context.risk_appetite
            )

        if ref_context.industry:
            # NOTE: This would require joining with organizations table
            # For now, skip industry filter
            pass

        if conditions:
            stmt = stmt.where(or_(*conditions))

        # Order by confidence score
        stmt = stmt.order_by(
            OrganizationContextModel.confidence_score.desc()
        ).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ============================================
    # STATISTICS
    # ============================================

    async def get_statistics(
        self,
        twin_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get learning system statistics

        Args:
            twin_id: Get stats for specific twin (None = global stats)

        Returns:
            Statistics dictionary
        """
        if twin_id:
            # Twin-specific stats
            event_count = await self.get_event_count(twin_id)
            sources = await self.get_event_sources(twin_id)
            insights = await self.get_all_insights(twin_id)
            context = await self.get_context(twin_id)

            return {
                'twin_id': twin_id,
                'total_events': event_count,
                'event_sources': sources,
                'event_source_count': len(sources),
                'total_insights': len(insights),
                'context_exists': context is not None,
                'confidence_score': context.confidence_score if context else 0.0,
                'last_updated': context.last_updated.isoformat() if context else None
            }
        else:
            # Global stats
            total_events_stmt = select(func.count(LearningEventModel.event_id))
            total_events = await self.session.scalar(total_events_stmt) or 0

            total_insights_stmt = select(func.count(LearningInsightModel.id))
            total_insights = await self.session.scalar(total_insights_stmt) or 0

            total_contexts_stmt = select(func.count(OrganizationContextModel.twin_id))
            total_contexts = await self.session.scalar(total_contexts_stmt) or 0

            avg_confidence_stmt = select(
                func.avg(OrganizationContextModel.confidence_score)
            )
            avg_confidence = await self.session.scalar(avg_confidence_stmt) or 0.0

            # Events by source
            events_by_source_stmt = select(
                LearningEventModel.source,
                func.count(LearningEventModel.event_id)
            ).group_by(LearningEventModel.source)

            source_result = await self.session.execute(events_by_source_stmt)
            events_by_source = {row[0]: row[1] for row in source_result}

            return {
                'total_events': total_events,
                'total_insights': total_insights,
                'total_contexts': total_contexts,
                'avg_confidence_score': float(avg_confidence),
                'events_by_source': events_by_source
            }
