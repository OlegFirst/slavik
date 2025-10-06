"""
Data Evolution
==============

Level 1 Evolution: Learn from new data (AUTOMATIC)

Activities:
- Consolidate new cases to long-term memory
- Update case library
- Extract patterns
- Clean old data

Frequency: Daily
Human Review: Not required
"""

import logging
from typing import Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DataEvolution:
    """
    Automatic data learning and consolidation.

    This is the safest level of evolution - just learning
    from data, no code or model changes.

    Example:
        ```python
        evolution = DataEvolution()
        await evolution.initialize(memory)

        result = await evolution.evolve()
        print(f"Learned {result['items_learned']} new items")
        ```
    """

    def __init__(self):
        self.memory = None
        self.initialized = False

    async def initialize(self, memory) -> None:
        """
        Initialize data evolution.

        Args:
            memory: DistributedMemory instance
        """
        self.memory = memory
        self.initialized = True
        logger.info("DataEvolution initialized")

    async def evolve(self) -> Dict[str, Any]:
        """
        Run data evolution cycle.

        Returns:
            dict: Evolution results

        Example:
            ```python
            result = await evolution.evolve()
            # {
            #     'ran': True,
            #     'items_learned': 42,
            #     'cases_added': 15,
            #     'patterns_extracted': 3,
            #     'old_data_cleaned': 100
            # }
            ```
        """
        logger.info("Running data evolution...")

        results = {
            'ran': True,
            'items_learned': 0,
            'cases_added': 0,
            'patterns_extracted': 0,
            'old_data_cleaned': 0,
            'timestamp': datetime.utcnow().isoformat()
        }

        try:
            # 1. Consolidate short-term to long-term memory
            consolidated = await self._consolidate_memory()
            results['items_learned'] = consolidated
            logger.info(f"Consolidated {consolidated} items to long-term memory")

            # 2. Extract successful cases
            cases_added = await self._extract_successful_cases()
            results['cases_added'] = cases_added
            logger.info(f"Added {cases_added} successful cases to library")

            # 3. Extract patterns
            patterns = await self._extract_patterns()
            results['patterns_extracted'] = patterns
            logger.info(f"Extracted {patterns} new patterns")

            # 4. Clean old data
            cleaned = await self._clean_old_data()
            results['old_data_cleaned'] = cleaned
            logger.info(f"Cleaned {cleaned} old items")

            logger.info(f"Data evolution complete: {results}")
            return results

        except Exception as e:
            logger.error(f"Error during data evolution: {e}")
            results['error'] = str(e)
            return results

    async def _consolidate_memory(self) -> int:
        """Consolidate important items to long-term memory."""
        try:
            if not self.memory:
                return 0

            # Consolidate from short-term to long-term
            count = await self.memory.consolidate()
            return count.get('short_term_to_long_term', 0)

        except Exception as e:
            logger.error(f"Error consolidating memory: {e}")
            return 0

    async def _extract_successful_cases(self) -> int:
        """Extract successful execution cases."""
        try:
            # Get recent successful executions
            recent_decisions = await self.memory.short_term_memory.get_recent_decisions(limit=100)

            # Filter successful ones
            successful = [
                d for d in recent_decisions
                if d.get('confidence', 0) > 0.8
            ]

            # Store in long-term as cases
            for decision in successful:
                case_id = f"case_{datetime.utcnow().timestamp()}"
                await self.memory.long_term_memory.store_case(
                    case_id=case_id,
                    situation=decision.get('metadata', {}),
                    decision=decision,
                    outcome={'success': True},
                    success=True
                )

            return len(successful)

        except Exception as e:
            logger.error(f"Error extracting cases: {e}")
            return 0

    async def _extract_patterns(self) -> int:
        """Extract patterns from recent data."""
        try:
            # TODO: Implement pattern extraction
            # For now, stub
            logger.debug("Pattern extraction (stub)")
            return 0

        except Exception as e:
            logger.error(f"Error extracting patterns: {e}")
            return 0

    async def _clean_old_data(self) -> int:
        """Clean old data from short-term memory."""
        try:
            if not self.memory:
                return 0

            # Clean items older than retention period
            count = await self.memory.short_term_memory.cleanup_old()
            return count

        except Exception as e:
            logger.error(f"Error cleaning old data: {e}")
            return 0
