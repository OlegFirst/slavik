#!/usr/bin/env python3
"""
Test EventBus connection and publish a test event
"""

import asyncio
import sys
sys.path.insert(0, '/Users/MD/AI-Platform-ISO')

async def test_eventbus():
    try:
        from shared.eventbus import init_eventbus

        # Initialize EventBus
        eventbus = init_eventbus(
            rabbitmq_url="amqp://bcm_platform:bcm_secure_2024@localhost:5673/",
            exchange_name="bcm_events"
        )

        print(" EventBus client initialized")

        # Connect
        await eventbus.connect()
        print(" Connected to RabbitMQ")

        # Check connection
        if eventbus.is_connected():
            print(" Connection verified")
        else:
            print(" Not connected")
            return

        # Publish test event
        success = await eventbus.publish(
            event_type="system.test",
            event_data={
                "message": "EventBus integration test",
                "source": "test_script"
            },
            tenant_id="test-tenant"
        )

        if success:
            print(" Test event published successfully")
        else:
            print(" Failed to publish test event")

        # Disconnect
        await eventbus.disconnect()
        print(" Disconnected from RabbitMQ")

        print("\n EventBus Integration Test PASSED!")
        return True

    except Exception as e:
        print(f" EventBus test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_eventbus())
    sys.exit(0 if result else 1)
