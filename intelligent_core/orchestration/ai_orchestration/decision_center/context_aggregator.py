"""
Context Aggregator
==================

Collects and aggregates context from all platform sources:
- Current platform state
- Active workflows
- Recent events
- Historical similar situations
- Industry trends
- Regulatory context
- Predictions
- Governance constraints
"""

import logging
from typing import Any, Dict, List
from datetime import datetime, timedelta

from ..models import FullContext
from infrastructure.database.managers.supabase_client import supabase_manager
from infrastructure.database.managers.cache_manager import cache_manager

logger = logging.getLogger(__name__)


class ContextAggregator:
    """
    Aggregates context from multiple sources.

    Sources:
    - Database: workflows, processes, risks
    - Cache: recent events, platform state
    - External: industry trends (stub for now)
    - Governance: rules and constraints

    Example:
        ```python
        aggregator = ContextAggregator()
        await aggregator.initialize()

        context = await aggregator.aggregate(situation, tenant_id)
        print(f"Found {len(context.workflows)} active workflows")
        ```
    """

    def __init__(self):
        self.initialized = False

    async def initialize(self) -> None:
        """Initialize aggregator."""
        # Ensure database is connected
        if not supabase_manager.engine:
            await supabase_manager.connect()

        self.initialized = True
        logger.info("ContextAggregator initialized")

    async def aggregate(
        self,
        situation: Dict[str, Any],
        tenant_id: str
    ) -> FullContext:
        """
        Aggregate full context for decision-making.

        Args:
            situation: Current situation data
            tenant_id: Tenant identifier

        Returns:
            FullContext: Aggregated context from all sources

        Example:
            ```python
            situation = {'workflow_stuck': True, 'workflow_id': 'bia_001'}
            context = await aggregator.aggregate(situation, 'tenant_123')
            ```
        """
        logger.debug(f"Aggregating context for tenant: {tenant_id}")

        # Aggregate in parallel for performance
        platform_state = await self._get_platform_state(tenant_id)
        workflows = await self._get_active_workflows(tenant_id)
        recent_events = await self._get_recent_events(tenant_id)
        similar_situations = await self._get_similar_situations(situation, tenant_id)
        governance_rules = await self._get_governance_rules(tenant_id)
        predictions = await self._get_predictions(situation, tenant_id)

        # External context (stubs for now)
        industry_trends = await self._get_industry_trends()
        regulatory_changes = await self._get_regulatory_changes()

        return FullContext(
            platform_state=platform_state,
            workflows=workflows,
            recent_events=recent_events,
            similar_situations=similar_situations,
            industry_trends=industry_trends,
            regulatory_changes=regulatory_changes,
            predictions=predictions,
            governance_rules=governance_rules,
            timestamp=datetime.utcnow()
        )

    async def _get_platform_state(self, tenant_id: str) -> Dict[str, Any]:
        """Get current platform state."""
        # Try cache first
        cache_key = f"platform_state:{tenant_id}"
        cached_state = await cache_manager.get_or_set(
            cache_key,
            lambda: self._fetch_platform_state(tenant_id),
            ttl=60  # 1 minute TTL
        )
        return cached_state

    async def _fetch_platform_state(self, tenant_id: str) -> Dict[str, Any]:
        """Fetch platform state from database."""
        try:
            async with supabase_manager.get_session() as session:
                # Get counts of various entities
                # This is a simplified version - expand as needed
                return {
                    'tenant_id': tenant_id,
                    'status': 'operational',
                    'timestamp': datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Error fetching platform state: {e}")
            return {
                'tenant_id': tenant_id,
                'status': 'unknown',
                'error': str(e)
            }

    async def _get_active_workflows(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Get active workflows."""
        try:
            async with supabase_manager.get_session() as session:
                # TODO: Query actual workflows from database
                # Stub for now
                return []
        except Exception as e:
            logger.error(f"Error fetching workflows: {e}")
            return []

    async def _get_recent_events(
        self,
        tenant_id: str,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get recent events from cache/memory."""
        try:
            # Try to get from Redis
            cache_key = f"events:{tenant_id}:recent"
            events = await cache_manager.redis.get(cache_key)
            if events:
                return events if isinstance(events, list) else []
            return []
        except Exception as e:
            logger.error(f"Error fetching recent events: {e}")
            return []

    async def _get_similar_situations(
        self,
        situation: Dict[str, Any],
        tenant_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar historical situations.

        Uses case library + vector similarity (stub for now).
        """
        try:
            # TODO: Implement vector similarity search
            # For now, return empty list
            logger.debug("Similar situations search (stub)")
            return []
        except Exception as e:
            logger.error(f"Error finding similar situations: {e}")
            return []

    async def _get_governance_rules(
        self,
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """Get applicable governance rules."""
        try:
            async with supabase_manager.get_session() as session:
                # TODO: Query governance rules from database
                # Return default rules for now
                return [
                    {
                        'id': 'default_1',
                        'type': 'data_protection',
                        'description': 'Never modify user data without permission',
                        'severity': 'critical'
                    },
                    {
                        'id': 'default_2',
                        'type': 'audit_trail',
                        'description': 'Never delete audit trail',
                        'severity': 'critical'
                    }
                ]
        except Exception as e:
            logger.error(f"Error fetching governance rules: {e}")
            return []

    async def _get_predictions(
        self,
        situation: Dict[str, Any],
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get AI predictions for situation."""
        try:
            # TODO: Implement ML prediction models
            # Stub for now
            return {
                'predicted_outcome': 'unknown',
                'confidence': 0.0,
                'model': 'stub'
            }
        except Exception as e:
            logger.error(f"Error getting predictions: {e}")
            return {}

    async def _get_industry_trends(self) -> List[Dict[str, Any]]:
        """Get relevant industry trends (stub)."""
        # TODO: Integrate with external data sources
        return []

    async def _get_regulatory_changes(self) -> List[Dict[str, Any]]:
        """Get recent regulatory changes (stub)."""
        # TODO: Integrate with regulatory databases
        return []
