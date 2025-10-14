"""
Short-Term Memory
=================

PostgreSQL-based memory for:
- Recent decisions (last 30 days)
- Execution results
- Temporary cases

Auto-cleanup: Items older than 30 days
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json

from sqlalchemy import text
from infrastructure.database.managers.supabase_client import supabase_manager
from .models import Decision, FullContext

logger = logging.getLogger(__name__)


class ShortTermMemory:
    """
    PostgreSQL-based short-term memory.

    Features:
    - Persistent storage (survives restarts)
    - 30-day retention
    - Fast retrieval
    - Structured queries

    Example:
        ```python
        memory = ShortTermMemory()
        await memory.initialize()

        # Store decision
        await memory.store_decision(decision, context)

        # Retrieve recent decisions
        decisions = await memory.get_recent_decisions(limit=10)
        ```
    """

    # Retention period (30 days)
    RETENTION_DAYS = 30

    def __init__(self):
        self.db = supabase_manager
        self.initialized = False

    async def initialize(self) -> None:
        """Initialize short-term memory."""
        # Ensure database is connected
        if not self.db.engine:
            await self.db.connect()

        # Create table if not exists
        await self._create_tables()

        self.initialized = True
        logger.info("ShortTermMemory initialized")

    async def store(
        self,
        key: str,
        value: Any,
        importance: float = 0.5
    ) -> bool:
        """
        Store item in short-term memory.

        Args:
            key: Storage key
            value: Data to store
            importance: Importance score (0-1)

        Returns:
            bool: Success status
        """
        try:
            async with self.db.get_session() as session:
                query = text("""
                    INSERT INTO ai_orchestrator_memory_short_term
                    (key, value, importance, created_at)
                    VALUES (:key, :value, :importance, :created_at)
                    ON CONFLICT (key) DO UPDATE
                    SET value = :value, importance = :importance, updated_at = :created_at
                """)

                await session.execute(query, {
                    'key': key,
                    'value': json.dumps(value),
                    'importance': importance,
                    'created_at': datetime.utcnow()
                })
                await session.commit()

            return True

        except Exception as e:
            logger.error(f"Error storing in short-term memory: {e}")
            return False

    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve item from short_term memory."""
        try:
            async with self.db.get_session() as session:
                query = text("""
                    SELECT value FROM ai_orchestrator_memory_short_term
                    WHERE key = :key
                    AND created_at > :cutoff
                """)

                result = await session.execute(query, {
                    'key': key,
                    'cutoff': datetime.utcnow() - timedelta(days=self.RETENTION_DAYS)
                })

                row = result.fetchone()
                if row:
                    return json.loads(row[0])

            return None

        except Exception as e:
            logger.error(f"Error retrieving from short_term memory: {e}")
            return None

    async def store_decision(
        self,
        decision: Decision,
        context: FullContext
    ) -> bool:
        """
        Store decision with context.

        Args:
            decision: Decision made
            context: Context used for decision

        Returns:
            bool: Success status
        """
        try:
            async with self.db.get_session() as session:
                query = text("""
                    INSERT INTO ai_orchestrator_decisions
                    (decision_id, action, rationale, priority, confidence,
                     safety_approved, context_data, created_at)
                    VALUES (:decision_id, :action, :rationale, :priority, :confidence,
                            :safety_approved, :context_data, :created_at)
                """)

                await session.execute(query, {
                    'decision_id': str(id(decision)),
                    'action': decision.action.value,
                    'rationale': decision.rationale,
                    'priority': decision.priority.value,
                    'confidence': decision.confidence,
                    'safety_approved': decision.safety_approved,
                    'context_data': json.dumps({
                        'workflows': len(context.workflows),
                        'events': len(context.recent_events),
                        'similar': len(context.similar_situations)
                    }),
                    'created_at': decision.timestamp
                })
                await session.commit()

            return True

        except Exception as e:
            logger.error(f"Error storing decision: {e}")
            return False

    async def store_execution_result(
        self,
        situation: Dict[str, Any],
        decision: Decision,
        result: Dict[str, Any]
    ) -> bool:
        """Store execution result for learning."""
        try:
            # Store as generic item
            key = f"execution:{id(decision)}"
            value = {
                'situation': situation,
                'decision': decision.to_dict(),
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            }

            return await self.store(key, value, importance=0.7)

        except Exception as e:
            logger.error(f"Error storing execution result: {e}")
            return False

    async def get_recent_decisions(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent decisions."""
        try:
            async with self.db.get_session() as session:
                query = text("""
                    SELECT decision_id, action, rationale, priority, confidence,
                           safety_approved, created_at
                    FROM ai_orchestrator_decisions
                    WHERE created_at > :cutoff
                    ORDER BY created_at DESC
                    LIMIT :limit
                """)

                result = await session.execute(query, {
                    'cutoff': datetime.utcnow() - timedelta(days=self.RETENTION_DAYS),
                    'limit': limit
                })

                decisions = []
                for row in result:
                    decisions.append({
                        'decision_id': row[0],
                        'action': row[1],
                        'rationale': row[2],
                        'priority': row[3],
                        'confidence': row[4],
                        'safety_approved': row[5],
                        'created_at': row[6].isoformat() if row[6] else None
                    })

                return decisions

        except Exception as e:
            logger.error(f"Error getting recent decisions: {e}")
            return []

    async def consolidate_to_long_term(
        self,
        long_term_memory
    ) -> int:
        """
        Consolidate important items to long-term memory.

        Args:
            long_term_memory: LongTermMemory instance

        Returns:
            int: Number of items consolidated
        """
        try:
            # Get important items older than 7 days
            async with self.db.get_session() as session:
                query = text("""
                    SELECT key, value, importance
                    FROM ai_orchestrator_memory_short_term
                    WHERE importance > 0.7
                    AND created_at < :cutoff
                    AND created_at > :retention_cutoff
                """)

                result = await session.execute(query, {
                    'cutoff': datetime.utcnow() - timedelta(days=7),
                    'retention_cutoff': datetime.utcnow() - timedelta(days=self.RETENTION_DAYS)
                })

                count = 0
                for row in result:
                    key, value, importance = row
                    value_data = json.loads(value)

                    # Store in long-term
                    success = await long_term_memory.store(key, value_data, importance)
                    if success:
                        count += 1

                logger.info(f"Consolidated {count} items to long-term memory")
                return count

        except Exception as e:
            logger.error(f"Error consolidating to long-term: {e}")
            return 0

    async def cleanup_old(self) -> int:
        """Remove items older than retention period."""
        try:
            async with self.db.get_session() as session:
                query = text("""
                    DELETE FROM ai_orchestrator_memory_short_term
                    WHERE created_at < :cutoff
                """)

                result = await session.execute(query, {
                    'cutoff': datetime.utcnow() - timedelta(days=self.RETENTION_DAYS)
                })
                await session.commit()

                count = result.rowcount
                logger.info(f"Cleaned up {count} old items")
                return count

        except Exception as e:
            logger.error(f"Error cleaning up old items: {e}")
            return 0

    async def close(self) -> None:
        """Close short-term memory (no-op, DB managed globally)."""
        pass

    def get_stats(self) -> Dict[str, Any]:
        """Get short-term memory statistics."""
        return {
            'type': 'short_term',
            'backend': 'postgresql',
            'retention_days': self.RETENTION_DAYS,
            'initialized': self.initialized
        }

    async def _create_tables(self) -> None:
        """Create tables if they don't exist."""
        try:
            async with self.db.get_session() as session:
                # Memory table
                await session.execute(text("""
                    CREATE TABLE IF NOT EXISTS ai_orchestrator_memory_short_term (
                        id SERIAL PRIMARY KEY,
                        key TEXT UNIQUE NOT NULL,
                        value JSONB NOT NULL,
                        importance FLOAT DEFAULT 0.5,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """))

                # Decisions table
                await session.execute(text("""
                    CREATE TABLE IF NOT EXISTS ai_orchestrator_decisions (
                        id SERIAL PRIMARY KEY,
                        decision_id TEXT NOT NULL,
                        action TEXT NOT NULL,
                        rationale TEXT,
                        priority INTEGER,
                        confidence FLOAT,
                        safety_approved BOOLEAN,
                        context_data JSONB,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """))

                await session.commit()

        except Exception as e:
            logger.error(f"Error creating tables: {e}")
