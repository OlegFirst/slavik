"""
Knowledge Exchange Service

Enables anonymous sharing of best practices, learnings, and solutions
between organizations.

Features:
- Contribute learnings anonymously
- Query relevant learnings from similar organizations
- Track effectiveness and usage statistics
- Privacy-first design
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4

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

logger = logging.getLogger(__name__)


# ============================================
# KNOWLEDGE EXCHANGE SERVICE
# ============================================

class KnowledgeExchangeService:
    """
    Service for sharing and discovering best practices
    """

    def __init__(
        self,
        anonymization_engine: Optional[AnonymizationEngine] = None,
        matching_engine: Optional[TwinMatchingEngine] = None
    ):
        """
        Initialize Knowledge Exchange Service

        Args:
            anonymization_engine: Engine for data anonymization
            matching_engine: Engine for finding similar twins
        """
        self.anonymization = anonymization_engine or AnonymizationEngine()
        self.matching = matching_engine or TwinMatchingEngine()

        # In-memory storage (TODO: replace with database)
        self._learnings: Dict[str, Learning] = {}
        self._contributor_map: Dict[str, str] = {}  # learning_id → twin_id (secure)

        logger.info("Knowledge Exchange Service initialized")

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

        # Create learning
        learning = Learning(
            learning_id=str(uuid4()),
            title=anonymized_title,
            challenge=anonymized_challenge,
            solution=anonymized_solution,
            outcome=anonymized_outcome,
            effectiveness_score=contribution.effectiveness_score,
            industry=industry,
            size_category=size_category,
            bcm_maturity=maturity_level,
            challenge_type=contribution.challenge_type,
            topic=contribution.topic,
            times_used=0,
            success_rate=0.0,
            avg_time_saved_days=contribution.time_saved_estimate_days,
            contributed_at=datetime.utcnow(),
            last_updated=datetime.utcnow(),
        )

        # Store learning
        self._learnings[learning.learning_id] = learning

        # Store contributor mapping (PRIVATE - not shared)
        self._contributor_map[learning.learning_id] = twin_id

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
        # Verify ownership
        if self._contributor_map.get(learning_id) != twin_id:
            logger.warning(
                f"Unauthorized learning update attempt: {learning_id} by {twin_id}"
            )
            return None

        learning = self._learnings.get(learning_id)
        if not learning:
            return None

        # Update fields (with anonymization if text)
        for field, value in updates.items():
            if field in ['title', 'challenge', 'solution', 'outcome']:
                value = await self.anonymization.anonymize_text(value)

            if hasattr(learning, field):
                setattr(learning, field, value)

        learning.last_updated = datetime.utcnow()

        logger.info(f"Learning updated: {learning_id}")

        return learning

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

        # Get all learnings
        all_learnings = list(self._learnings.values())

        # Filter by criteria
        filtered = self._filter_learnings(all_learnings, query)

        # Score by relevance
        scored = await self._score_relevance(filtered, query)

        # Sort by relevance score
        scored.sort(key=lambda x: x[1], reverse=True)

        # Extract learnings and limit
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
        all_learnings = list(self._learnings.values())

        # Filter
        filtered = [
            l for l in all_learnings
            if l.topic == topic
            and l.effectiveness_score >= min_effectiveness
        ]

        if industry:
            filtered = [l for l in filtered if l.industry == industry]

        if size_category:
            filtered = [l for l in filtered if l.size_category == size_category]

        # Sort by effectiveness
        filtered.sort(key=lambda l: l.effectiveness_score, reverse=True)

        return filtered[:limit]

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
        all_learnings = list(self._learnings.values())

        # Filter by industry
        if industry:
            all_learnings = [l for l in all_learnings if l.industry == industry]

        # Score by combined metric: effectiveness * usage
        def combined_score(learning: Learning) -> float:
            effectiveness = learning.effectiveness_score
            usage = min(learning.times_used / 10.0, 1.0)  # Normalize usage (cap at 10)
            return effectiveness * 0.7 + usage * 0.3

        all_learnings.sort(key=combined_score, reverse=True)

        return all_learnings[:limit]

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
        learning = self._learnings.get(feedback.learning_id)
        if not learning:
            raise ValueError(f"Learning not found: {feedback.learning_id}")

        logger.info(
            f"Received feedback for learning {feedback.learning_id}: "
            f"{feedback.outcome.value} (rating: {feedback.effectiveness_rating:.2f})"
        )

        # Update statistics
        learning.times_used += 1

        # Update success rate
        if feedback.outcome in [LearningOutcome.SUCCESS, LearningOutcome.PARTIAL_SUCCESS]:
            successes = int(learning.success_rate * (learning.times_used - 1))
            if feedback.outcome == LearningOutcome.SUCCESS:
                successes += 1
            elif feedback.outcome == LearningOutcome.PARTIAL_SUCCESS:
                successes += 0.5

            learning.success_rate = successes / learning.times_used

        # Update average time saved
        if feedback.time_saved_days is not None:
            if learning.avg_time_saved_days is None:
                learning.avg_time_saved_days = feedback.time_saved_days
            else:
                # Running average
                total_days = learning.avg_time_saved_days * (learning.times_used - 1)
                total_days += feedback.time_saved_days
                learning.avg_time_saved_days = int(total_days / learning.times_used)

        learning.last_updated = datetime.utcnow()

        logger.info(
            f"Learning updated: times_used={learning.times_used}, "
            f"success_rate={learning.success_rate:.2f}"
        )

        return learning

    # ============================================
    # STATISTICS & ANALYTICS
    # ============================================

    async def get_community_statistics(self) -> Dict[str, Any]:
        """
        Get community-wide knowledge exchange statistics

        Returns:
            Statistics dictionary
        """
        all_learnings = list(self._learnings.values())

        # Group by topic
        by_topic: Dict[str, int] = {}
        for learning in all_learnings:
            by_topic[learning.topic] = by_topic.get(learning.topic, 0) + 1

        # Group by industry
        by_industry: Dict[str, int] = {}
        for learning in all_learnings:
            industry = learning.industry.value
            by_industry[industry] = by_industry.get(industry, 0) + 1

        # Calculate averages
        avg_effectiveness = self._avg_effectiveness(all_learnings)
        avg_usage = sum(l.times_used for l in all_learnings) / len(all_learnings) if all_learnings else 0
        total_applications = sum(l.times_used for l in all_learnings)

        return {
            'total_learnings': len(all_learnings),
            'learnings_by_topic': by_topic,
            'learnings_by_industry': by_industry,
            'avg_effectiveness_score': round(avg_effectiveness, 2),
            'avg_usage_per_learning': round(avg_usage, 1),
            'total_applications': total_applications,
            'top_topics': sorted(by_topic.items(), key=lambda x: x[1], reverse=True)[:5],
            'generated_at': datetime.utcnow().isoformat(),
        }

    async def get_learning_statistics(
        self,
        learning_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get statistics for specific learning"""
        learning = self._learnings.get(learning_id)
        if not learning:
            return None

        return {
            'learning_id': learning.learning_id,
            'title': learning.title,
            'topic': learning.topic,
            'times_used': learning.times_used,
            'success_rate': round(learning.success_rate, 2),
            'effectiveness_score': learning.effectiveness_score,
            'avg_time_saved_days': learning.avg_time_saved_days,
            'contributed_at': learning.contributed_at.isoformat(),
            'last_updated': learning.last_updated.isoformat(),
        }

    # ============================================
    # HELPER METHODS
    # ============================================

    def _filter_learnings(
        self,
        learnings: List[Learning],
        query: LearningQuery
    ) -> List[Learning]:
        """Filter learnings by query criteria"""
        filtered = learnings

        # Filter by effectiveness
        filtered = [
            l for l in filtered
            if l.effectiveness_score >= query.min_effectiveness
        ]

        # Filter by industry
        if query.industry:
            filtered = [l for l in filtered if l.industry == query.industry]

        # Filter by size
        if query.size_category:
            filtered = [l for l in filtered if l.size_category == query.size_category]

        # Filter by maturity
        if query.maturity_level:
            filtered = [l for l in filtered if l.bcm_maturity == query.maturity_level]

        # Filter by topics
        if query.topics:
            filtered = [l for l in filtered if l.topic in query.topics]

        return filtered

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
            if learning.topic.lower() in context_lower:
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

    # ============================================
    # DATA MANAGEMENT
    # ============================================

    def get_all_learnings(self) -> List[Learning]:
        """Get all learnings (for admin/analysis)"""
        return list(self._learnings.values())

    def get_learning_count(self) -> int:
        """Get total learning count"""
        return len(self._learnings)

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
        # Verify ownership
        if self._contributor_map.get(learning_id) != twin_id:
            logger.warning(f"Unauthorized delete attempt: {learning_id} by {twin_id}")
            return False

        if learning_id in self._learnings:
            del self._learnings[learning_id]
            del self._contributor_map[learning_id]
            logger.info(f"Learning deleted: {learning_id}")
            return True

        return False
