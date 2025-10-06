"""
Analytics Client for Stuck Detection

Queries platform events and activity logs to detect when
organizations are stuck and need collective help.

Tracks 6 key signals:
1. Days without progress
2. Validation failure count
3. Low AI confidence scores
4. Repeated questions
5. Repeated document reviews
6. User frustration indicators
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, text, desc
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class AnalyticsClient:
    """
    Analytics client for gathering stuck detection signals

    Queries:
    - Workflow execution events
    - AI interaction logs
    - User activity logs
    - Validation events
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_last_progress_event(
        self,
        org_id: str,
        module: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get last meaningful progress event

        Progress events:
        - workflow.stage.completed
        - validation.passed
        - document.uploaded
        - process.added

        Returns:
            {
                'event_type': 'workflow.stage.completed',
                'timestamp': datetime,
                'days_ago': 5.2
            }
        """

        try:
            # Query activity/event logs
            # Adjust table name based on your schema
            query = text("""
                SELECT event_type, created_at
                FROM activity_logs
                WHERE org_id = :org_id
                AND event_type IN (
                    'workflow.stage.completed',
                    'validation.passed',
                    'document.uploaded',
                    'process.added',
                    'dependency.mapped',
                    'impact.assessed'
                )
                AND (:module IS NULL OR metadata->>'module' = :module)
                ORDER BY created_at DESC
                LIMIT 1
            """)

            result = await self.db.execute(
                query,
                {"org_id": org_id, "module": module}
            )

            row = result.fetchone()

            if row:
                timestamp = row[1]
                days_ago = (datetime.utcnow() - timestamp).total_seconds() / 86400

                return {
                    'event_type': row[0],
                    'timestamp': timestamp,
                    'days_ago': days_ago
                }

            logger.debug(f"No progress events found for org {org_id}")
            return None

        except Exception as e:
            logger.error(f"Error getting last progress event: {e}", exc_info=True)
            # Fallback: Assume no progress if error
            return None

    async def count_validation_failures(
        self,
        org_id: str,
        days: int = 7
    ) -> int:
        """
        Count validation failures in last N days

        Validation failures indicate struggle with requirements
        """

        try:
            since = datetime.utcnow() - timedelta(days=days)

            query = text("""
                SELECT COUNT(*)
                FROM activity_logs
                WHERE org_id = :org_id
                AND event_type = 'validation.failed'
                AND created_at >= :since
            """)

            result = await self.db.execute(
                query,
                {"org_id": org_id, "since": since}
            )

            count = result.scalar() or 0

            logger.debug(f"Org {org_id}: {count} validation failures in {days} days")

            return count

        except Exception as e:
            logger.error(f"Error counting validation failures: {e}", exc_info=True)
            return 0

    async def get_avg_confidence(
        self,
        org_id: str,
        days: int = 7
    ) -> float:
        """
        Get average AI confidence score

        Low confidence indicates AI is uncertain about recommendations
        """

        try:
            since = datetime.utcnow() - timedelta(days=days)

            query = text("""
                SELECT AVG((metadata->>'confidence')::float)
                FROM activity_logs
                WHERE org_id = :org_id
                AND event_type = 'ai.response'
                AND metadata->>'confidence' IS NOT NULL
                AND created_at >= :since
            """)

            result = await self.db.execute(
                query,
                {"org_id": org_id, "since": since}
            )

            avg = result.scalar()

            if avg is None:
                logger.debug(f"No AI interactions found for org {org_id}")
                return 1.0  # Assume OK if no data

            logger.debug(f"Org {org_id}: avg confidence {avg:.2f}")

            return float(avg)

        except Exception as e:
            logger.error(f"Error getting avg confidence: {e}", exc_info=True)
            return 1.0  # Assume OK on error

    async def detect_repeated_questions(
        self,
        org_id: str,
        days: int = 7
    ) -> int:
        """
        Detect repeated questions (asking same thing multiple times)

        Uses simple similarity: Same keywords appearing in questions

        Returns:
            Count of question clusters (repeated topics)
        """

        try:
            since = datetime.utcnow() - timedelta(days=days)

            # Get all questions
            query = text("""
                SELECT metadata->>'question' as question
                FROM activity_logs
                WHERE org_id = :org_id
                AND event_type = 'user.question'
                AND created_at >= :since
                ORDER BY created_at DESC
            """)

            result = await self.db.execute(
                query,
                {"org_id": org_id, "since": since}
            )

            questions = [row[0] for row in result.fetchall() if row[0]]

            if len(questions) < 2:
                return 0

            # Simple keyword-based clustering
            question_keywords = []
            for q in questions:
                # Extract keywords (simple: split and take significant words)
                words = set(
                    w.lower() for w in q.split()
                    if len(w) > 4 and w.isalpha()
                )
                question_keywords.append(words)

            # Count similar question pairs
            repeated_count = 0
            seen = set()

            for i, kw1 in enumerate(question_keywords):
                for j, kw2 in enumerate(question_keywords[i+1:], i+1):
                    # Calculate Jaccard similarity
                    if len(kw1) > 0 and len(kw2) > 0:
                        similarity = len(kw1 & kw2) / len(kw1 | kw2)
                        if similarity > 0.5 and (i, j) not in seen:
                            repeated_count += 1
                            seen.add((i, j))

            logger.debug(f"Org {org_id}: {repeated_count} repeated question patterns")

            return repeated_count

        except Exception as e:
            logger.error(f"Error detecting repeated questions: {e}", exc_info=True)
            return 0

    async def detect_repeated_doc_reviews(
        self,
        org_id: str,
        days: int = 7
    ) -> int:
        """
        Detect repeated document reviews (viewing same docs many times)

        Indicates confusion about requirements
        """

        try:
            since = datetime.utcnow() - timedelta(days=days)

            query = text("""
                SELECT metadata->>'document_id', COUNT(*)
                FROM activity_logs
                WHERE org_id = :org_id
                AND event_type = 'document.viewed'
                AND created_at >= :since
                GROUP BY metadata->>'document_id'
                HAVING COUNT(*) >= 3
            """)

            result = await self.db.execute(
                query,
                {"org_id": org_id, "since": since}
            )

            repeated_docs = result.fetchall()

            count = len(repeated_docs)

            logger.debug(
                f"Org {org_id}: {count} documents viewed 3+ times in {days} days"
            )

            return count

        except Exception as e:
            logger.error(f"Error detecting repeated doc reviews: {e}", exc_info=True)
            return 0

    async def detect_frustration(
        self,
        org_id: str,
        days: int = 7
    ) -> float:
        """
        Detect user frustration indicators

        Signals:
        - Short sessions (< 5 min) - user gives up quickly
        - Rapid back/forth navigation - confusion
        - Error/failure events

        Returns:
            Frustration score 0-1 (0 = calm, 1 = very frustrated)
        """

        try:
            since = datetime.utcnow() - timedelta(days=days)

            # Count short sessions
            short_sessions_query = text("""
                SELECT COUNT(*)
                FROM user_sessions
                WHERE org_id = :org_id
                AND created_at >= :since
                AND duration_seconds < 300
                AND duration_seconds > 10
            """)

            result = await self.db.execute(
                short_sessions_query,
                {"org_id": org_id, "since": since}
            )

            short_sessions = result.scalar() or 0

            # Count errors
            errors_query = text("""
                SELECT COUNT(*)
                FROM activity_logs
                WHERE org_id = :org_id
                AND created_at >= :since
                AND (
                    event_type LIKE '%.failed'
                    OR event_type LIKE '%.error'
                )
            """)

            result = await self.db.execute(
                errors_query,
                {"org_id": org_id, "since": since}
            )

            errors = result.scalar() or 0

            # Calculate frustration score (normalized 0-1)
            # Short sessions: each counts 0.05
            # Errors: each counts 0.1
            frustration = min(1.0, (short_sessions * 0.05) + (errors * 0.1))

            logger.debug(
                f"Org {org_id}: frustration score {frustration:.2f} "
                f"({short_sessions} short sessions, {errors} errors)"
            )

            return frustration

        except Exception as e:
            logger.error(f"Error detecting frustration: {e}", exc_info=True)
            return 0.0

    async def get_current_stage(
        self,
        org_id: str,
        module: str
    ) -> Optional[str]:
        """
        Get current workflow stage

        Returns:
            Current stage name or None
        """

        try:
            query = text("""
                SELECT metadata->>'stage'
                FROM activity_logs
                WHERE org_id = :org_id
                AND metadata->>'module' = :module
                AND (
                    event_type = 'workflow.stage.entered'
                    OR event_type = 'workflow.stage.completed'
                )
                ORDER BY created_at DESC
                LIMIT 1
            """)

            result = await self.db.execute(
                query,
                {"org_id": org_id, "module": module}
            )

            row = result.fetchone()

            if row:
                return row[0]

            return None

        except Exception as e:
            logger.error(f"Error getting current stage: {e}", exc_info=True)
            return None

    async def get_active_organizations(
        self,
        days: int = 30,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get list of active organizations for batch stuck checking

        Active = had activity in last N days

        Returns:
            List of {'org_id': str, 'last_activity': datetime}
        """

        try:
            since = datetime.utcnow() - timedelta(days=days)

            query = text("""
                SELECT DISTINCT org_id, MAX(created_at) as last_activity
                FROM activity_logs
                WHERE created_at >= :since
                GROUP BY org_id
                ORDER BY last_activity DESC
                LIMIT :limit
            """)

            result = await self.db.execute(
                query,
                {"since": since, "limit": limit}
            )

            orgs = [
                {
                    'org_id': row[0],
                    'last_activity': row[1]
                }
                for row in result.fetchall()
            ]

            logger.info(f"Found {len(orgs)} active organizations in last {days} days")

            return orgs

        except Exception as e:
            logger.error(f"Error getting active organizations: {e}", exc_info=True)
            return []

    async def get_workflow_metrics(
        self,
        org_id: str,
        module: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive workflow metrics for organization

        Returns:
            {
                'time_in_workflow_days': float,
                'stages_completed': int,
                'total_stages': int,
                'progress_percent': float,
                'validation_pass_rate': float,
                'ai_usage_count': int
            }
        """

        try:
            # Time in workflow
            start_query = text("""
                SELECT MIN(created_at)
                FROM activity_logs
                WHERE org_id = :org_id
                AND metadata->>'module' = :module
                AND event_type = 'workflow.started'
            """)

            result = await self.db.execute(
                start_query,
                {"org_id": org_id, "module": module}
            )

            start_time = result.scalar()

            if start_time:
                time_in_workflow = (datetime.utcnow() - start_time).total_seconds() / 86400
            else:
                time_in_workflow = 0.0

            # Stages completed
            stages_query = text("""
                SELECT COUNT(DISTINCT metadata->>'stage')
                FROM activity_logs
                WHERE org_id = :org_id
                AND metadata->>'module' = :module
                AND event_type = 'workflow.stage.completed'
            """)

            result = await self.db.execute(
                stages_query,
                {"org_id": org_id, "module": module}
            )

            stages_completed = result.scalar() or 0

            # Validation pass rate
            validations_query = text("""
                SELECT
                    COUNT(*) FILTER (WHERE event_type = 'validation.passed') as passed,
                    COUNT(*) FILTER (WHERE event_type = 'validation.failed') as failed
                FROM activity_logs
                WHERE org_id = :org_id
                AND metadata->>'module' = :module
                AND event_type IN ('validation.passed', 'validation.failed')
            """)

            result = await self.db.execute(
                validations_query,
                {"org_id": org_id, "module": module}
            )

            row = result.fetchone()
            passed = row[0] or 0
            failed = row[1] or 0
            total_validations = passed + failed

            pass_rate = passed / total_validations if total_validations > 0 else 1.0

            # AI usage
            ai_query = text("""
                SELECT COUNT(*)
                FROM activity_logs
                WHERE org_id = :org_id
                AND metadata->>'module' = :module
                AND event_type = 'ai.response'
            """)

            result = await self.db.execute(
                ai_query,
                {"org_id": org_id, "module": module}
            )

            ai_usage = result.scalar() or 0

            return {
                'time_in_workflow_days': round(time_in_workflow, 1),
                'stages_completed': stages_completed,
                'total_stages': 6,  # Default, varies by module
                'progress_percent': round(stages_completed / 6 * 100, 1),
                'validation_pass_rate': round(pass_rate, 2),
                'ai_usage_count': ai_usage
            }

        except Exception as e:
            logger.error(f"Error getting workflow metrics: {e}", exc_info=True)
            return {
                'time_in_workflow_days': 0.0,
                'stages_completed': 0,
                'total_stages': 6,
                'progress_percent': 0.0,
                'validation_pass_rate': 1.0,
                'ai_usage_count': 0
            }
