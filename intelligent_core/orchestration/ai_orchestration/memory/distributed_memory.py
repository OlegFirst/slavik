"""
Distributed Memory
==================

Unified interface for 4-layer memory system.

Memory Types:
- Working: Redis (1 hour TTL)
- Short-term: PostgreSQL (30 days)
- Long-term: Case Library (permanent)
- Procedural: ML models (learned patterns)
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .working_memory import WorkingMemory
from .short_term_memory import ShortTermMemory
from .long_term_memory import LongTermMemory
from .procedural_memory import ProceduralMemory
from ..models import Memory, MemoryType

logger = logging.getLogger(__name__)


class DistributedMemory:
    """
    Unified interface for distributed memory system.

    Provides automatic routing to appropriate memory layer based on:
    - Recency (working vs short-term)
    - Importance (short-term vs long-term)
    - Pattern type (procedural)

    Example:
        ```python
        memory = DistributedMemory()
        await memory.initialize()

        # Store recent event
        await memory.store_event(event)

        # Retrieve similar situations
        similar = await memory.find_similar(situation)
        ```
    """

    def __init__(self):
        # Initialize all memory layers
        self.working_memory = WorkingMemory()
        self.short_term_memory = ShortTermMemory()
        self.long_term_memory = LongTermMemory()
        self.procedural_memory = ProceduralMemory()

        self.initialized = False

    async def initialize(self) -> None:
        """Initialize all memory layers."""
        try:
            await self.working_memory.initialize()
            logger.info("✅ Working memory initialized")

            await self.short_term_memory.initialize()
            logger.info("✅ Short-term memory initialized")

            await self.long_term_memory.initialize()
            logger.info("✅ Long-term memory initialized")

            await self.procedural_memory.initialize()
            logger.info("✅ Procedural memory initialized")

            self.initialized = True
            logger.info("Distributed memory system initialized")

        except Exception as e:
            logger.error(f"Failed to initialize memory: {e}")
            raise

    async def store(
        self,
        memory_type: MemoryType,
        key: str,
        value: Any,
        importance: float = 0.5
    ) -> bool:
        """
        Store item in appropriate memory layer.

        Args:
            memory_type: Type of memory to use
            key: Storage key
            value: Data to store
            importance: Importance score (0-1)

        Returns:
            bool: Success status

        Example:
            ```python
            await memory.store(
                MemoryType.WORKING,
                'current_workflow',
                workflow_data,
                importance=0.8
            )
            ```
        """
        try:
            if memory_type == MemoryType.WORKING:
                return await self.working_memory.store(key, value)

            elif memory_type == MemoryType.SHORT_TERM:
                return await self.short_term_memory.store(key, value, importance)

            elif memory_type == MemoryType.LONG_TERM:
                return await self.long_term_memory.store(key, value, importance)

            elif memory_type == MemoryType.PROCEDURAL:
                return await self.procedural_memory.store_pattern(key, value)

            else:
                logger.error(f"Unknown memory type: {memory_type}")
                return False

        except Exception as e:
            logger.error(f"Error storing in memory: {e}")
            return False

    async def retrieve(
        self,
        memory_type: MemoryType,
        key: str
    ) -> Optional[Any]:
        """
        Retrieve item from memory layer.

        Args:
            memory_type: Type of memory
            key: Storage key

        Returns:
            Retrieved value or None

        Example:
            ```python
            workflow = await memory.retrieve(
                MemoryType.WORKING,
                'current_workflow'
            )
            ```
        """
        try:
            if memory_type == MemoryType.WORKING:
                return await self.working_memory.retrieve(key)

            elif memory_type == MemoryType.SHORT_TERM:
                return await self.short_term_memory.retrieve(key)

            elif memory_type == MemoryType.LONG_TERM:
                return await self.long_term_memory.retrieve(key)

            elif memory_type == MemoryType.PROCEDURAL:
                return await self.procedural_memory.retrieve_pattern(key)

            else:
                logger.error(f"Unknown memory type: {memory_type}")
                return None

        except Exception as e:
            logger.error(f"Error retrieving from memory: {e}")
            return None

    async def find_similar(
        self,
        situation: Dict[str, Any],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar situations across all memory layers.

        Args:
            situation: Current situation
            limit: Maximum results

        Returns:
            List of similar situations

        Example:
            ```python
            similar = await memory.find_similar(
                {'workflow_stuck': True, 'error': 'timeout'},
                limit=5
            )
            ```
        """
        results = []

        # Check working memory
        recent = await self.working_memory.find_recent_similar(situation)
        results.extend(recent[:limit])

        # Check long-term memory (case library)
        if len(results) < limit:
            cases = await self.long_term_memory.search_similar(situation, limit)
            results.extend(cases)

        # Deduplicate and limit
        unique = self._deduplicate(results)
        return unique[:limit]

    async def consolidate(self) -> Dict[str, int]:
        """
        Consolidate memories across layers.

        Moves important items:
        - Working → Short-term (after 1 hour)
        - Short-term → Long-term (after 30 days)
        - Patterns → Procedural (learned)

        Returns:
            dict: Consolidation statistics
        """
        logger.info("Starting memory consolidation...")

        stats = {
            'working_to_short_term': 0,
            'short_term_to_long_term': 0,
            'patterns_learned': 0
        }

        try:
            # Consolidate short-term to long-term
            count = await self.short_term_memory.consolidate_to_long_term(
                self.long_term_memory
            )
            stats['short_term_to_long_term'] = count

            logger.info(f"Memory consolidation complete: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error during consolidation: {e}")
            return stats

    async def close(self) -> None:
        """Close all memory connections."""
        await self.working_memory.close()
        await self.short_term_memory.close()
        await self.long_term_memory.close()
        await self.procedural_memory.close()
        logger.info("Distributed memory closed")

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            'working': self.working_memory.get_stats(),
            'short_term': self.short_term_memory.get_stats(),
            'long_term': self.long_term_memory.get_stats(),
            'procedural': self.procedural_memory.get_stats()
        }

    def _deduplicate(
        self,
        items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate items."""
        seen = set()
        unique = []

        for item in items:
            # Use ID or hash as dedup key
            key = item.get('id') or str(hash(str(item)))
            if key not in seen:
                seen.add(key)
                unique.append(item)

        return unique
