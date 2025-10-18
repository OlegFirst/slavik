"""
Knowledge Exchange Service (Database-enabled)

PostgreSQL-backed version of Knowledge Exchange Service.
Uses CommunityRepository for database operations.

Features:
- Contribute learnings anonymously
- Query relevant learnings from similar organizations
- Track effectiveness and usage statistics
- Privacy-first design
- Persistent storage in PostgreSQL
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    Learning,
    LearningContribution,
    LearningQuery,
    LearningFeedback,
    LearningOutcome,
    IndustryType,
    OrganizationSize,
    BCMMaturityLevel,
)
from .anonymization_engine import AnonymizationEngine
from .twin_matching_engine import TwinMatchingEngine
from storage.community_repository import CommunityRepository
from storage.models import CommunityLearningModel

logger = logging.getLogger(__name__)


# ============================================
# KNOWLEDGE EXCHANGE SERVICE (DB)
# ============================================

class KnowledgeExchangeServiceDB:
    """
    Database-backed Knowledge Exchange Service

    Uses PostgreSQL via CommunityRepository
    """

    def __init__(
        self,
        db_session: AsyncSession,
        tenant_id: str,
        anonymization_engine: Optional[AnonymizationEngine] = None,
        matching_engine: Optional[TwinMatchingEngine] = None
    ):
        """
        Initialize Knowledge Exchange Service

        Args:
            db_session: SQLAlchemy async session
            tenant_id: Tenant ID for multi-tenancy
            anonymization_engine: Engine for data anonymization
            matching_engine: Engine for finding similar twins
        """
        self.repository = CommunityRepository(db_session)
        self.tenant_id = tenant_id
        self.anonymization = anonymization_engine or AnonymizationEngine()
        self.matching = matching_engine or TwinMatchingEngine()

        logger.info(f"Knowledge Exchange Service (DB) initialized for tenant: {tenant_id}")

    # ============================================
    # PUBLIC API - CONTRIBUTION
    # ============================================

    async def contribute_learning(
        self,
        twin_id: str,
        contribution: LearningContribution,
        industry: IndustryType,
        size_category: OrganizationSize,
        maturity_level: BCMMaturityLevel
    ) -> Learning:
        """
        Contribute a learning to the community pool

        Args:
            twin_id: Contributing organization twin ID (kept private)
            contribution: Learning contribution details
            industry: Organization industry (for matching)
            size_category: Organization size category
            maturity_level: BCM maturity level

        Returns:
            Created Learning (anonymized)
        """
        logger.info(f"Receiving learning contribution: {contribution.title}")

        # Anonymize content
        anonymized_title = await self.anonymization.anonymize_text(contribution.title)
        anonymized_challenge = await self.anonymization.anonymize_text(contribution.challenge)
        anonymized_solution = await self.anonymization.anonymize_text(contribution.solution)
        anonymized_outcome = await self.anonymization.anonymize_text(contribution.outcome)

        # Prepare data for database
        learning_data = {
            'learning_id': str(uuid4()),
            'tenant_id': self.tenant_id,
            'title': anonymized_title,
            'challenge': anonymized_challenge,
            'solution': anonymized_solution,
            'outcome': anonymized_outcome,
            'tags': contribution.tags if hasattr(contribution, 'tags') else [],
            'industry': industry.value,
            'size_category': size_category.value,
            'maturity_level': maturity_level.value,
            'effectiveness_score': contribution.effectiveness_score,
            'times_used': 0,
            'success_rate': 0.0,
            'average_rating': None,
            'anonymization_level': 'standard',
            'contributor_twin_id': twin_id,  # PRIVATE
            'is_verified': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }

        # Create in database
        db_learning = await self.repository.create_learning(learning_data)

        # Convert to Pydantic model for return
        learning = self._db_to_pydantic(db_learning, contribution.topic, contribution.challenge_type)

        logger.info(
            f"Learning contributed successfully: {learning.learning_id} "
            f"(topic: {learning.topic}, effectiveness: {learning.effectiveness_score:.2f})"
        )

        return learning

    async def update_learning(
        self,
        learning_id: str,
        twin_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Learning]:
        """
        Update an existing learning (only by original contributor)

        Args:
            learning_id: Learning ID
            twin_id: Twin ID (must match original contributor)
            updates: Fields to update

        Returns:
            Updated Learning or None if not authorized
        """
        # Get learning to verify ownership
        db_learning = await self.repository.get_learning(learning_id)
        if not db_learning:
            return None

        # Verify ownership
        if db_learning.contributor_twin_id != twin_id:
            logger.warning(
                f"Unauthorized learning update attempt: {learning_id} by {twin_id}"
            )
            return None

        # Anonymize text fields if present
        anonymized_updates = {}
        for field, value in updates.items():
            if field in ['title', 'challenge', 'solution', 'outcome'] and isinstance(value, str):
                anonymized_updates[field] = await self.anonymization.anonymize_text(value)
            else:
                anonymized_updates[field] = value

        # Update in database
        updated_db = await self.repository.update_learning_metrics(
            learning_id,
            **anonymized_updates
        )

        if not updated_db:
            return None

        logger.info(f"Learning updated: {learning_id}")

        return self._db_to_pydantic(updated_db, updates.get('topic'), updates.get('challenge_type'))

    # ============================================
    # PUBLIC API - DISCOVERY
    # ============================================

    async def get_relevant_learnings(
        self,
        query: LearningQuery
    ) -> List[Learning]:
        """
        Get learnings relevant to query

        Args:
            query: Learning query with context and filters

        Returns:
            List of relevant learnings sorted by relevance
        """
        logger.info(f"Querying learnings: {query.context[:50]}...")

        # Build filters for repository
        industry = query.industry.value if query.industry else None
        size_category = query.size_category.value if query.size_category else None
        maturity_level = query.maturity_level.value if query.maturity_level else None

        # Query database
        db_learnings = await self.repository.query_learnings(
            industry=industry,
            size_category=size_category,
            maturity_level=maturity_level,
            tags=query.topics if query.topics else None,
            min_effectiveness=query.min_effectiveness,
            limit=query.limit
        )

        # Convert to Pydantic models
        learnings = [self._db_to_pydantic(db_l) for db_l in db_learnings]

        # Score by relevance (semantic matching)
        scored = await self._score_relevance(learnings, query)
        scored.sort(key=lambda x: x[1], reverse=True)

        # Extract learnings
        results = [learning for learning, score in scored[:query.limit]]

        logger.info(
            f"Found {len(results)} relevant learnings "
            f"(avg effectiveness: {self._avg_effectiveness(results):.2f})"
        )

        return results

    async def get_learning_by_topic(
        self,
        topic: str,
        industry: Optional[IndustryType] = None,
        size_category: Optional[OrganizationSize] = None,
        min_effectiveness: float = 0.7,
        limit: int = 10
    ) -> List[Learning]:
        """
        Get learnings by topic

        Args:
            topic: Topic to search for
            industry: Optional industry filter
            size_category: Optional size filter
            min_effectiveness: Minimum effectiveness score
            limit: Maximum results

        Returns:
            List of learnings
        """
        # Query database with filters
        db_learnings = await self.repository.query_learnings(
            industry=industry.value if industry else None,
            size_category=size_category.value if size_category else None,
            tags=[topic],  # Use tags for topic filtering
            min_effectiveness=min_effectiveness,
            limit=limit
        )

        return [self._db_to_pydantic(db_l) for db_l in db_learnings]

    async def get_top_learnings(
        self,
        industry: Optional[IndustryType] = None,
        limit: int = 20
    ) -> List[Learning]:
        """
        Get top learnings by usage and effectiveness

        Args:
            industry: Optional industry filter
            limit: Maximum results

        Returns:
            List of top learnings
        """
        db_learnings = await self.repository.get_top_learnings(
            industry=industry.value if industry else None,
            limit=limit
        )

        return [self._db_to_pydantic(db_l) for db_l in db_learnings]

    # ============================================
    # PUBLIC API - FEEDBACK
    # ============================================

    async def submit_feedback(
        self,
        feedback: LearningFeedback,
        twin_id: str
    ) -> Learning:
        """
        Submit feedback on applied learning

        Args:
            feedback: Learning feedback
            twin_id: Twin ID providing feedback

        Returns:
            Updated Learning with new statistics
        """
        # Get current learning
        db_learning = await self.repository.get_learning(feedback.learning_id)
        if not db_learning:
            raise ValueError(f"Learning not found: {feedback.learning_id}")

        logger.info(
            f"Received feedback for learning {feedback.learning_id}: "
            f"{feedback.outcome.value} (rating: {feedback.effectiveness_rating:.2f})"
        )

        # Submit feedback to database
        feedback_data = {
            'id': str(uuid4()),
            'learning_id': feedback.learning_id,
            'twin_id': twin_id,
            'tenant_id': self.tenant_id,
            'applied': True,
            'was_helpful': feedback.outcome in [LearningOutcome.SUCCESS, LearningOutcome.PARTIAL_SUCCESS],
            'outcome_rating': feedback.effectiveness_rating,
            'comment': feedback.comments if hasattr(feedback, 'comments') else None,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }

        await self.repository.submit_feedback(feedback_data)

        # Calculate new statistics
        times_used = db_learning.times_used + 1

        # Calculate success rate
        if feedback.outcome in [LearningOutcome.SUCCESS, LearningOutcome.PARTIAL_SUCCESS]:
            successes = int(db_learning.success_rate * db_learning.times_used)
            if feedback.outcome == LearningOutcome.SUCCESS:
                successes += 1
            elif feedback.outcome == LearningOutcome.PARTIAL_SUCCESS:
                successes += 0.5

            success_rate = successes / times_used
        else:
            success_rate = (db_learning.success_rate * db_learning.times_used) / times_used

        # Update learning metrics
        updated_db = await self.repository.update_learning_metrics(
            feedback.learning_id,
            times_used=times_used,
            success_rate=success_rate
        )

        logger.info(
            f"Learning updated: times_used={times_used}, "
            f"success_rate={success_rate:.2f}"
        )

        return self._db_to_pydantic(updated_db)

    # ============================================
    # STATISTICS & ANALYTICS
    # ============================================

    async def get_community_statistics(self) -> Dict[str, Any]:
        """
        Get community-wide knowledge exchange statistics

        Returns:
            Statistics dictionary
        """
        stats = await self.repository.get_community_statistics()

        # Add timestamp
        stats['generated_at'] = datetime.utcnow().isoformat()

        return stats

    async def get_learning_statistics(
        self,
        learning_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get statistics for specific learning"""
        db_learning = await self.repository.get_learning(learning_id)
        if not db_learning:
            return None

        return {
            'learning_id': db_learning.learning_id,
            'title': db_learning.title,
            'times_used': db_learning.times_used,
            'success_rate': round(db_learning.success_rate, 2),
            'effectiveness_score': db_learning.effectiveness_score,
            'created_at': db_learning.created_at.isoformat(),
            'updated_at': db_learning.updated_at.isoformat(),
        }

    # ============================================
    # HELPER METHODS
    # ============================================

    async def _score_relevance(
        self,
        learnings: List[Learning],
        query: LearningQuery
    ) -> List[tuple[Learning, float]]:
        """
        Score learnings by relevance to query

        Returns:
            List of (learning, score) tuples
        """
        scored = []

        for learning in learnings:
            score = 0.0

            # Base score: effectiveness
            score += learning.effectiveness_score * 0.3

            # Usage score (normalized)
            usage_score = min(learning.times_used / 10.0, 1.0)
            score += usage_score * 0.2

            # Success rate
            score += learning.success_rate * 0.2

            # Context match (simple keyword matching)
            # TODO: enhance with semantic similarity
            context_lower = query.context.lower()
            if learning.topic and learning.topic.lower() in context_lower:
                score += 0.15

            if any(word in context_lower for word in learning.challenge.lower().split()[:10]):
                score += 0.1

            if any(word in context_lower for word in learning.solution.lower().split()[:10]):
                score += 0.05

            scored.append((learning, score))

        return scored

    @staticmethod
    def _avg_effectiveness(learnings: List[Learning]) -> float:
        """Calculate average effectiveness score"""
        if not learnings:
            return 0.0

        total = sum(l.effectiveness_score for l in learnings)
        return total / len(learnings)

    def _db_to_pydantic(
        self,
        db_learning: CommunityLearningModel,
        topic: Optional[str] = None,
        challenge_type: Optional[str] = None
    ) -> Learning:
        """
        Convert database model to Pydantic model

        Args:
            db_learning: Database model
            topic: Optional topic (if not in tags)
            challenge_type: Optional challenge type

        Returns:
            Pydantic Learning model
        """
        # Extract topic from tags if not provided
        if not topic and db_learning.tags:
            topic = db_learning.tags[0] if db_learning.tags else "general"
        elif not topic:
            topic = "general"

        return Learning(
            learning_id=db_learning.learning_id,
            title=db_learning.title,
            challenge=db_learning.challenge,
            solution=db_learning.solution,
            outcome=db_learning.outcome,
            effectiveness_score=db_learning.effectiveness_score,
            industry=IndustryType(db_learning.industry),
            size_category=OrganizationSize(db_learning.size_category),
            bcm_maturity=BCMMaturityLevel(db_learning.maturity_level),
            challenge_type=challenge_type or "general",
            topic=topic,
            times_used=db_learning.times_used,
            success_rate=db_learning.success_rate,
            avg_time_saved_days=None,  # TODO: add to database model
            contributed_at=db_learning.created_at,
            last_updated=db_learning.updated_at,
        )

    # ============================================
    # DATA MANAGEMENT
    # ============================================

    async def get_all_learnings(self) -> List[Learning]:
        """Get all learnings (for admin/analysis)"""
        db_learnings = await self.repository.query_learnings(limit=1000)
        return [self._db_to_pydantic(db_l) for db_l in db_learnings]

    async def get_learning_count(self) -> int:
        """Get total learning count"""
        stats = await self.repository.get_community_statistics()
        return stats.get('total_learnings', 0)

    async def delete_learning(
        self,
        learning_id: str,
        twin_id: str
    ) -> bool:
        """
        Delete a learning (only by original contributor)

        Args:
            learning_id: Learning ID
            twin_id: Twin ID (must match contributor)

        Returns:
            True if deleted, False if unauthorized or not found
        """
        # Get learning to verify ownership
        db_learning = await self.repository.get_learning(learning_id)
        if not db_learning:
            return False

        # Verify ownership
        if db_learning.contributor_twin_id != twin_id:
            logger.warning(f"Unauthorized delete attempt: {learning_id} by {twin_id}")
            return False

        # TODO: Implement delete in repository
        # For now, return False (not implemented)
        logger.warning(f"Delete not yet implemented in repository")
        return False
