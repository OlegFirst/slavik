"""
Redis EventBus Example
======================

Example using Redis Streams backend.

Requirements:
    - Redis server running on localhost:6379
    - pip install redis
"""

import asyncio
from infrastructure.eventbus import create_eventbus, Event


async def main():
    """Run Redis EventBus example."""

    # Create Redis event bus
    bus = create_eventbus('redis', redis_url='redis://localhost:6379')

    print("Redis EventBus Example\n")

    # Event handler
    async def handle_event(event: Event):
        print(f"📨 Received: {event.type}")
        print(f"   Data: {event.data}")
        print()

    # Subscribe with consumer group
    print("Subscribing to 'test.event' with consumer group...\n")
    await bus.subscribe(
        'test.event',
        handle_event,
        consumer_group='example-consumers'
    )

    # Publish events
    print("Publishing 5 events...\n")
    for i in range(5):
        event = Event.create(
            event_type='test.event',
            data={'message': f'Message {i+1}'},
            source='example',
            tenant_id='tenant_123'
        )
        await bus.publish(event)

    # Let events process
    print("Processing events...")
    await asyncio.sleep(2)

    # Stats
    stats = await bus.get_stats()
    print(f"\n📊 Published: {stats['published']}, Consumed: {stats['consumed']}")

    # Cleanup
    await bus.close()
    print("\n✅ Done!")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except ImportError:
        print("❌ Redis not installed. Run: pip install redis")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Make sure Redis is running on localhost:6379")
