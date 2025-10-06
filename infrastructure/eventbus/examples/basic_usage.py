"""
Basic EventBus Usage Example
=============================

Simple example showing EventBus publish/subscribe.
"""

import asyncio
from infrastructure.eventbus import create_eventbus, Event, EventPriority


async def main():
    """Run basic EventBus example."""

    # Create in-memory event bus
    bus = create_eventbus('memory')

    print("EventBus Example Started\n")

    # Define event handler
    async def handle_workflow_event(event: Event):
        print(f"📨 Received: {event.type}")
        print(f"   Data: {event.data}")
        print(f"   Source: {event.source}")
        print(f"   Tenant: {event.tenant_id}")
        print()

    # Subscribe to all workflow events
    print("Subscribing to 'workflow.*' events...\n")
    await bus.subscribe('workflow.*', handle_workflow_event)

    # Publish some events
    events = [
        Event.create(
            event_type='workflow.started',
            data={'workflow_id': 'bia_001', 'stage': 'identify_processes'},
            source='workflow-engine',
            tenant_id='tenant_healthcare_123'
        ),
        Event.create(
            event_type='workflow.stage_changed',
            data={'workflow_id': 'bia_001', 'from': 'identify', 'to': 'analyze'},
            source='workflow-engine',
            tenant_id='tenant_healthcare_123',
            priority=EventPriority.HIGH
        ),
        Event.create(
            event_type='workflow.completed',
            data={'workflow_id': 'bia_001', 'duration_seconds': 3600},
            source='workflow-engine',
            tenant_id='tenant_healthcare_123'
        ),
        Event.create(
            event_type='bia.process_created',  # Won't match 'workflow.*'
            data={'process_id': 123},
            source='bia-service',
            tenant_id='tenant_healthcare_123'
        ),
    ]

    print("Publishing events...\n")
    for event in events:
        await bus.publish(event)

    # Give handlers time to process
    await asyncio.sleep(0.2)

    # Show statistics
    stats = await bus.get_stats()
    print("\n📊 Statistics:")
    print(f"   Published: {stats['published']}")
    print(f"   Consumed: {stats['consumed']}")
    print(f"   Errors: {stats['errors']}")

    # Cleanup
    await bus.close()
    print("\n✅ Done!")


if __name__ == '__main__':
    asyncio.run(main())
