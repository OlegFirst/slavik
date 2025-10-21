"""
Event Subscriber Example
=========================

Example showing how to create event subscribers for different use cases.

This demonstrates the event-driven architecture pattern where:
- State Machine publishes events
- EventBus distributes to subscribers
- Subscribers react independently
"""

import asyncio
from infrastructure.eventbus import create_eventbus, Event, EventPriority
from infrastructure.eventbus.subscribers import BaseSubscriber


# ============================================================================
# EXAMPLE 1: Case Collector Subscriber
# ============================================================================

class CaseCollectorSubscriber(BaseSubscriber):
    """
    Records workflow history for case library.

    Subscribes to:
        - workflow.state_changed → record state transition
        - workflow.action.* → record all actions
        - workflow.completed → finalize case
    """

    def __init__(self):
        super().__init__()
        self.transitions = []
        self.actions = []

    async def setup_subscriptions(self, eventbus):
        """Setup subscriptions."""
        await self.subscribe(
            eventbus,
            'workflow.state_changed',
            self.handle_state_changed
        )

        await self.subscribe(
            eventbus,
            'workflow.action.*',
            self.handle_action
        )

        await self.subscribe(
            eventbus,
            'workflow.completed',
            self.handle_completed
        )

    async def handle_state_changed(self, event: Event):
        """Record state transition."""
        transition = {
            'workflow_id': event.data['workflow_id'],
            'from_state': event.data['from_state'],
            'to_state': event.data['to_state'],
            'timestamp': event.timestamp
        }

        self.transitions.append(transition)
        print(f" Case Collector: Recorded transition {transition['from_state']} → {transition['to_state']}")

    async def handle_action(self, event: Event):
        """Record action taken."""
        action = {
            'workflow_id': event.data['workflow_id'],
            'action': event.data['action'],
            'timestamp': event.timestamp
        }

        self.actions.append(action)
        print(f" Case Collector: Recorded action {event.type}")

    async def handle_completed(self, event: Event):
        """Finalize case."""
        workflow_id = event.data['workflow_id']
        print(f" Case Collector: Workflow {workflow_id} completed")
        print(f"   - {len(self.transitions)} transitions")
        print(f"   - {len(self.actions)} actions")


# ============================================================================
# EXAMPLE 2: AI Advisor Subscriber
# ============================================================================

class AIAdvisorSubscriber(BaseSubscriber):
    """
    Prepares AI context and provides proactive help.

    Subscribes to:
        - workflow.state_changed → prepare context
        - workflow.validation_failed → suggest fixes
    """

    async def setup_subscriptions(self, eventbus):
        """Setup subscriptions."""
        await self.subscribe(
            eventbus,
            'workflow.state_changed',
            self.handle_state_changed
        )

        await self.subscribe(
            eventbus,
            'workflow.validation_failed',
            self.handle_validation_failed
        )

    async def handle_state_changed(self, event: Event):
        """Prepare AI context for new state."""
        to_state = event.data['to_state']
        print(f" AI Advisor: Preparing context for state '{to_state}'")

        # Simulate context preparation
        await asyncio.sleep(0.1)
        print(f" AI Advisor: Context ready for '{to_state}'")

    async def handle_validation_failed(self, event: Event):
        """Suggest fixes for validation errors."""
        errors = event.data.get('errors', [])
        print(f" AI Advisor: Analyzing {len(errors)} validation errors")

        # Simulate generating suggestions
        await asyncio.sleep(0.1)

        # Publish suggestions back to EventBus
        # (In real implementation, would use eventbus from closure or DI)
        print(f" AI Advisor: Generated fix suggestions")


# ============================================================================
# EXAMPLE 3: Analytics Subscriber
# ============================================================================

class AnalyticsSubscriber(BaseSubscriber):
    """
    Collects metrics from workflow events.

    Subscribes to:
        - workflow.* → all workflow events
    """

    def __init__(self):
        super().__init__()
        self.metrics = {}

    async def setup_subscriptions(self, eventbus):
        """Setup subscriptions."""
        await self.subscribe(
            eventbus,
            'workflow.*',
            self.handle_workflow_event
        )

    async def handle_workflow_event(self, event: Event):
        """Record metrics."""
        # Increment counter
        metric_key = f"workflow.events.{event.type}"
        self.metrics[metric_key] = self.metrics.get(metric_key, 0) + 1

        print(f" Analytics: {event.type} (total: {self.metrics[metric_key]})")


# ============================================================================
# EXAMPLE 4: Notification Subscriber
# ============================================================================

class NotificationSubscriber(BaseSubscriber):
    """
    Sends notifications to users.

    Subscribes to:
        - workflow.milestone_reached → celebrate!
        - workflow.validation_failed → alert user
    """

    async def setup_subscriptions(self, eventbus):
        """Setup subscriptions."""
        await self.subscribe(
            eventbus,
            'workflow.milestone_reached',
            self.handle_milestone
        )

        await self.subscribe(
            eventbus,
            'workflow.validation_failed',
            self.handle_validation_failed
        )

    async def handle_milestone(self, event: Event):
        """Celebrate milestone."""
        milestone = event.data['milestone']
        print(f" Notification:  Milestone reached - {milestone}")

    async def handle_validation_failed(self, event: Event):
        """Alert about validation errors."""
        error_count = len(event.data.get('errors', []))
        print(f" Notification: ️  {error_count} validation errors")


# ============================================================================
# EXAMPLE 5: Audit Logger Subscriber
# ============================================================================

class AuditSubscriber(BaseSubscriber):
    """
    Records all events for compliance.

    Subscribes to:
        - * → ALL events
    """

    def __init__(self):
        super().__init__()
        self.audit_log = []

    async def setup_subscriptions(self, eventbus):
        """Setup subscriptions."""
        await self.subscribe(
            eventbus,
            '*',  # All events
            self.handle_any_event
        )

    async def handle_any_event(self, event: Event):
        """Log every event."""
        self.audit_log.append({
            'event_id': event.id,
            'event_type': event.type,
            'source': event.source,
            'timestamp': event.timestamp
        })

        # Don't print (too noisy), but log silently


# ============================================================================
# MAIN DEMO
# ============================================================================

async def main():
    """
    Demonstrate event-driven architecture with subscribers.
    """

    print("Event Subscribers Example")
    print("=" * 60)
    print()

    # 1. Create EventBus
    bus = create_eventbus('memory')

    # 2. Create subscribers
    case_collector = CaseCollectorSubscriber()
    ai_advisor = AIAdvisorSubscriber()
    analytics = AnalyticsSubscriber()
    notifications = NotificationSubscriber()
    audit = AuditSubscriber()

    # 3. Setup subscriptions
    print("Setting up subscribers...")
    await case_collector.setup_subscriptions(bus)
    await ai_advisor.setup_subscriptions(bus)
    await analytics.setup_subscriptions(bus)
    await notifications.setup_subscriptions(bus)
    await audit.setup_subscriptions(bus)

    print(f" {case_collector.get_subscription_count()} subscriptions for CaseCollector")
    print(f" {ai_advisor.get_subscription_count()} subscriptions for AIAdvisor")
    print(f" {analytics.get_subscription_count()} subscriptions for Analytics")
    print(f" {notifications.get_subscription_count()} subscriptions for Notifications")
    print(f" {audit.get_subscription_count()} subscriptions for Audit")
    print()

    # 4. Simulate workflow events
    print("Simulating workflow events...")
    print("-" * 60)
    print()

    # Event 1: State changed
    event1 = Event.create(
        event_type='workflow.state_changed',
        data={
            'workflow_id': 'bia_001',
            'from_state': 'identify_processes',
            'to_state': 'analyze_dependencies'
        },
        source='workflow-engine',
        tenant_id='tenant_123'
    )
    await bus.publish(event1)
    await asyncio.sleep(0.2)  # Let handlers process
    print()

    # Event 2: Action taken
    event2 = Event.create(
        event_type='workflow.action.process_added',
        data={
            'workflow_id': 'bia_001',
            'action': 'add_process',
            'process_name': 'Emergency Department'
        },
        source='workflow-engine',
        tenant_id='tenant_123'
    )
    await bus.publish(event2)
    await asyncio.sleep(0.2)
    print()

    # Event 3: Milestone reached
    event3 = Event.create(
        event_type='workflow.milestone_reached',
        data={
            'workflow_id': 'bia_001',
            'milestone': 'Critical Processes Identified'
        },
        source='workflow-engine',
        tenant_id='tenant_123',
        priority=EventPriority.HIGH
    )
    await bus.publish(event3)
    await asyncio.sleep(0.2)
    print()

    # Event 4: Validation failed
    event4 = Event.create(
        event_type='workflow.validation_failed',
        data={
            'workflow_id': 'bia_001',
            'errors': [
                'Missing RTO for process X',
                'No dependencies mapped for tier 1 process'
            ]
        },
        source='workflow-engine',
        tenant_id='tenant_123',
        priority=EventPriority.HIGH
    )
    await bus.publish(event4)
    await asyncio.sleep(0.2)
    print()

    # Event 5: Workflow completed
    event5 = Event.create(
        event_type='workflow.completed',
        data={
            'workflow_id': 'bia_001',
            'duration_days': 5,
            'success': True
        },
        source='workflow-engine',
        tenant_id='tenant_123'
    )
    await bus.publish(event5)
    await asyncio.sleep(0.2)
    print()

    # 5. Show statistics
    print("-" * 60)
    print("Statistics:")
    print()

    bus_stats = await bus.get_stats()
    print(f" EventBus:")
    print(f"   Published: {bus_stats['published']}")
    print(f"   Consumed: {bus_stats['consumed']}")
    print(f"   Errors: {bus_stats['errors']}")
    print()

    print(f" Analytics metrics: {analytics.metrics}")
    print(f" Audit log entries: {len(audit.audit_log)}")
    print()

    # 6. Cleanup
    print("Cleaning up...")
    await case_collector.cleanup(bus)
    await ai_advisor.cleanup(bus)
    await analytics.cleanup(bus)
    await notifications.cleanup(bus)
    await audit.cleanup(bus)
    await bus.close()

    print(" Done!")


if __name__ == '__main__':
    asyncio.run(main())
