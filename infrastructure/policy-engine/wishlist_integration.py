"""
Wishlist Integration для Decision Center (Phase 2)

🧠 МОЗГ принимает тактические решения о wishes:
- Когда action не может быть выполнен сейчас → добавить в wishlist
- Приоритизация wishes на основе available resources
- Выполнение wishes когда ресурсы доступны
- Политики для wishes (как для recovery/optimization)

Интеграция с существующим DecisionCenter:
- Расширяет decide_recovery_action() и decide_optimization_action()
- Добавляет POSTPONED outcome (вместо REJECTED)
- Background task для выполнения wishes
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add intelligent-core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'intelligent-core'))

try:
    from coordination_center.wishlist.wishlist_system import (
        WishlistSystem,
        WishlistItem,
        NeedType,
        ResourceCost
    )
    HAS_WISHLIST = True
except ImportError:
    HAS_WISHLIST = False
    logger = logging.getLogger(__name__)
    logger.warning("Wishlist System not available - wishlist features disabled")

from infrastructure.decision_center.decision_models import Decision, DecisionOutcome

logger = logging.getLogger(__name__)


class WishlistDecisionIntegration:
    """
    Wishlist Integration для Decision Center

    Роль: Расширяет DecisionCenter возможностью откладывать решения в wishlist
    """

    def __init__(
        self,
        decision_center,
        resource_tracker_client=None
    ):
        """
        Initialize Wishlist Integration

        Args:
            decision_center: InfrastructureDecisionCenter instance
            resource_tracker_client: Resource Tracker Client для определения available resources
        """
        self.decision_center = decision_center
        self.resource_tracker = resource_tracker_client
        self.wishlist: Optional[WishlistSystem] = None
        self.executor_task: Optional[asyncio.Task] = None
        self.running = False

        # Statistics
        self.stats = {
            'wishes_created': 0,
            'wishes_executed': 0,
            'wishes_failed': 0,
            'wishes_obsolete': 0
        }

    async def initialize(self, storage_path: Optional[str] = None):
        """Initialize Wishlist System"""
        if not HAS_WISHLIST:
            logger.warning("Wishlist System not available - skipping initialization")
            return

        self.wishlist = WishlistSystem(
            storage_path=storage_path or "/tmp/decision_center_wishlist.json",
            max_item_age_seconds=86400.0  # 24 hours
        )

        logger.info("✅ Wishlist System initialized in Decision Center")

    async def start_executor(self):
        """Start background task для выполнения wishes"""
        if not self.wishlist:
            logger.warning("Wishlist not initialized - cannot start executor")
            return

        self.running = True
        self.executor_task = asyncio.create_task(self._executor_loop())
        logger.info("✅ Wishlist executor started")

    async def stop_executor(self):
        """Stop background executor"""
        self.running = False
        if self.executor_task:
            self.executor_task.cancel()
            try:
                await self.executor_task
            except asyncio.CancelledError:
                pass
        logger.info("✅ Wishlist executor stopped")

    async def postpone_decision_to_wishlist(
        self,
        decision: Decision,
        resource_cost: ResourceCost,
        urgency: float = 0.7,
        deadline_seconds: Optional[float] = None
    ) -> WishlistItem:
        """
        Отложить решение в wishlist

        Args:
            decision: Decision object
            resource_cost: Estimated resource cost
            urgency: Urgency level (0-1)
            deadline_seconds: Deadline in seconds from now

        Returns:
            WishlistItem
        """
        if not self.wishlist:
            raise RuntimeError("Wishlist not initialized")

        # Определить need_type на основе decision_type
        need_type_map = {
            'recovery': NeedType.SURVIVAL,
            'optimization': NeedType.EFFICIENCY,
            'deployment': NeedType.GROWTH,
            'learning': NeedType.LEARNING
        }
        need_type = need_type_map.get(
            decision.decision_type.value if hasattr(decision, 'decision_type') else 'recovery',
            NeedType.EFFICIENCY
        )

        # Создать wish
        wish = self.wishlist.add_wish(
            description=f"{decision.action_type} for {decision.service_name}",
            need_type=need_type,
            urgency=urgency,
            resource_cost=resource_cost,
            deadline=deadline_seconds,
            context={
                'decision_id': decision.decision_id,
                'service_name': decision.service_name,
                'action_type': decision.action_type,
                'trigger_data': decision.trigger_data
            }
        )

        self.stats['wishes_created'] += 1

        # Update decision outcome
        decision.outcome = DecisionOutcome.PENDING
        decision.reasoning = f"Postponed to wishlist: {wish.id}"

        logger.info(f"📝 Decision postponed to wishlist: {wish.id} ({decision.service_name})")

        return wish

    async def _executor_loop(self):
        """Background loop для выполнения wishes"""
        while self.running:
            try:
                # Get available resources
                if self.resource_tracker:
                    available_dict = self.resource_tracker.get_available_resources()
                    available = ResourceCost(
                        cpu_percent=available_dict.get('cpu_percent', 50.0),
                        memory_mb=available_dict.get('memory_mb', 1024.0),
                        time_seconds=available_dict.get('time_seconds', 300.0)
                    )
                else:
                    # Default available resources
                    available = ResourceCost(
                        cpu_percent=50.0,
                        memory_mb=1024.0,
                        time_seconds=300.0
                    )

                # Get prioritized wishes
                wishes = self.wishlist.get_prioritized_wishes(available, limit=5)

                for wish in wishes:
                    # Check if can afford
                    if not wish.resource_cost.can_afford_with(available):
                        continue

                    # Execute wish
                    logger.info(f"🎯 Executing wish: {wish.description}")
                    wish.status = "active"

                    success = await self._execute_wish(wish)

                    if success:
                        self.wishlist.complete_wish(wish.id, success=True)
                        self.stats['wishes_executed'] += 1
                        logger.info(f"✅ Wish executed successfully: {wish.id}")
                    else:
                        self.wishlist.complete_wish(wish.id, success=False)
                        self.stats['wishes_failed'] += 1
                        logger.warning(f"❌ Wish execution failed: {wish.id}")

                # Cleanup obsolete
                obsolete_count = len(self.wishlist.cleanup_obsolete())
                self.stats['wishes_obsolete'] += obsolete_count

                # Resolve conflicts
                self.wishlist.detect_and_resolve_conflicts(available)

                # Wait before next check
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Wishlist executor error: {e}")
                await asyncio.sleep(30)

    async def _execute_wish(self, wish: WishlistItem) -> bool:
        """
        Execute wish

        Args:
            wish: WishlistItem to execute

        Returns:
            bool: success
        """
        try:
            context = wish.context
            service_name = context.get('service_name')
            action_type = context.get('action_type')

            if not service_name or not action_type:
                logger.warning(f"Wish {wish.id} missing service_name or action_type")
                return False

            # Map wish to decision type
            if wish.need_type == NeedType.SURVIVAL:
                # Recovery action
                decision, can_proceed = await self.decision_center.decide_recovery_action(
                    service_name=service_name,
                    action_type=action_type,
                    trigger_data=context.get('trigger_data', {}),
                    current_attempt=context.get('attempt', 1)
                )

                return can_proceed

            elif wish.need_type == NeedType.EFFICIENCY:
                # Optimization action
                decision, can_proceed = await self.decision_center.decide_optimization_action(
                    service_name=service_name,
                    action_type=action_type,
                    recommendation=context.get('trigger_data', {}),
                    trigger_event_id=context.get('decision_id')
                )

                return can_proceed

            else:
                logger.warning(f"Unknown wish need_type: {wish.need_type}")
                return False

        except Exception as e:
            logger.error(f"Error executing wish {wish.id}: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get wishlist integration statistics"""
        stats = {
            **self.stats,
            'wishlist_items': len(self.wishlist.items) if self.wishlist else 0,
            'pending_wishes': len([w for w in self.wishlist.items.values() if w.status == 'pending']) if self.wishlist else 0
        }

        if self.wishlist:
            stats['wishlist_stats'] = self.wishlist.get_stats()

        return stats


async def create_wishlist_integration(
    decision_center,
    resource_tracker_client=None,
    storage_path: Optional[str] = None,
    start_executor: bool = True
) -> WishlistDecisionIntegration:
    """
    Factory function для создания Wishlist Integration

    Args:
        decision_center: InfrastructureDecisionCenter instance
        resource_tracker_client: Resource Tracker Client
        storage_path: Path to wishlist storage
        start_executor: Whether to start background executor

    Returns:
        WishlistDecisionIntegration instance
    """
    integration = WishlistDecisionIntegration(
        decision_center=decision_center,
        resource_tracker_client=resource_tracker_client
    )

    await integration.initialize(storage_path=storage_path)

    if start_executor:
        await integration.start_executor()

    return integration
