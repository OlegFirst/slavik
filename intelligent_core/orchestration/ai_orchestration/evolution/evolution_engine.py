"""
Evolution Engine
================

Orchestrates self-improvement across 3 levels:
1. Data Evolution (daily, automatic)
2. Model Evolution (weekly, automatic)
3. Code Evolution (monthly, human review required)
"""

import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from .data_evolution import DataEvolution
from .model_evolution import ModelEvolution
from .code_evolution import CodeEvolution

logger = logging.getLogger(__name__)


class EvolutionEngine:
    """
    Manages self-improvement across all levels.

    Evolution cycles:
    - Data: Daily (automatic)
    - Model: Weekly (automatic, monitored)
    - Code: Monthly (requires human review)

    Example:
        ```python
        engine = EvolutionEngine()
        await engine.initialize(memory)

        # Manual trigger
        result = await engine.run_evolution_cycle()

        # Check what evolved
        print(f"Data items learned: {result['data']['items_learned']}")
        print(f"Models updated: {result['model']['models_updated']}")
        print(f"Code changes proposed: {result['code']['changes_proposed']}")
        ```
    """

    def __init__(self):
        self.data_evolution = DataEvolution()
        self.model_evolution = ModelEvolution()
        self.code_evolution = CodeEvolution()

        self.initialized = False
        self.last_evolution = {
            'data': None,
            'model': None,
            'code': None
        }

        self.stats = {
            'data_cycles': 0,
            'model_cycles': 0,
            'code_cycles': 0,
            'total_improvements': 0
        }

    async def initialize(self, memory) -> None:
        """
        Initialize evolution engine.

        Args:
            memory: DistributedMemory instance
        """
        await self.data_evolution.initialize(memory)
        await self.model_evolution.initialize(memory)
        await self.code_evolution.initialize(memory)

        self.initialized = True
        logger.info("EvolutionEngine initialized")

    async def run_evolution_cycle(self) -> Dict[str, Any]:
        """
        Run evolution cycle across all levels.

        Returns:
            dict: Evolution results by level

        Example:
            ```python
            result = await engine.run_evolution_cycle()

            # Data evolution (always runs)
            print(f"Learned {result['data']['items_learned']} new items")

            # Model evolution (weekly)
            if result['model']['ran']:
                print(f"Updated {result['model']['models_updated']} models")

            # Code evolution (monthly, needs review)
            if result['code']['ran']:
                print(f"Proposed {result['code']['changes_proposed']} code changes")
                print(f"Review at: {result['code']['review_url']}")
            ```
        """
        logger.info("Starting evolution cycle...")

        results = {
            'data': {},
            'model': {},
            'code': {},
            'timestamp': datetime.utcnow().isoformat()
        }

        # Level 1: Data Evolution (daily)
        if self._should_run_data_evolution():
            logger.info("Running data evolution...")
            results['data'] = await self.data_evolution.evolve()
            self.last_evolution['data'] = datetime.utcnow()
            self.stats['data_cycles'] += 1
            logger.info(f"Data evolution complete: {results['data']}")

        # Level 2: Model Evolution (weekly)
        if self._should_run_model_evolution():
            logger.info("Running model evolution...")
            results['model'] = await self.model_evolution.evolve()
            self.last_evolution['model'] = datetime.utcnow()
            self.stats['model_cycles'] += 1
            logger.info(f"Model evolution complete: {results['model']}")

        # Level 3: Code Evolution (monthly, human review)
        if self._should_run_code_evolution():
            logger.info("Running code evolution...")
            results['code'] = await self.code_evolution.evolve()
            self.last_evolution['code'] = datetime.utcnow()
            self.stats['code_cycles'] += 1
            logger.info(f"Code evolution complete: {results['code']}")

        # Update total improvements
        self.stats['total_improvements'] += (
            results.get('data', {}).get('items_learned', 0) +
            results.get('model', {}).get('models_updated', 0) +
            results.get('code', {}).get('changes_proposed', 0)
        )

        logger.info(f"Evolution cycle complete: {self.stats}")
        return results

    async def shutdown(self) -> None:
        """Shutdown evolution engine."""
        logger.info("Shutting down evolution engine...")
        # Any cleanup needed
        pass

    def get_stats(self) -> Dict[str, Any]:
        """Get evolution statistics."""
        return {
            **self.stats,
            'last_evolution': {
                'data': self.last_evolution['data'].isoformat() if self.last_evolution['data'] else None,
                'model': self.last_evolution['model'].isoformat() if self.last_evolution['model'] else None,
                'code': self.last_evolution['code'].isoformat() if self.last_evolution['code'] else None
            }
        }

    def _should_run_data_evolution(self) -> bool:
        """Check if data evolution should run (daily)."""
        if not self.last_evolution['data']:
            return True

        elapsed = datetime.utcnow() - self.last_evolution['data']
        return elapsed > timedelta(days=1)

    def _should_run_model_evolution(self) -> bool:
        """Check if model evolution should run (weekly)."""
        if not self.last_evolution['model']:
            return True

        elapsed = datetime.utcnow() - self.last_evolution['model']
        return elapsed > timedelta(weeks=1)

    def _should_run_code_evolution(self) -> bool:
        """Check if code evolution should run (monthly)."""
        if not self.last_evolution['code']:
            return True

        elapsed = datetime.utcnow() - self.last_evolution['code']
        return elapsed > timedelta(days=30)
