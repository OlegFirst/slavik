"""
FastAPI Integration Example
============================

Example showing how to integrate EventBus with FastAPI application.

Demonstrates:
    - EventBus lifecycle management (startup/shutdown)
    - Multiple subscribers
    - Dependency injection
    - Publishing events from API endpoints
"""

from fastapi import FastAPI, Depends
from typing import List
import asyncio

from infrastructure.eventbus import create_eventbus, Event, EventPriority, IEventBus
from infrastructure.eventbus.subscribers import BaseSubscriber


# ============================================================================
# SUBSCRIBERS
# ============================================================================

class WorkflowSubscriber(BaseSubscriber):
    """Handles workflow-related events."""

    async def setup_subscriptions(self, eventbus):
        await self.subscribe(
            eventbus,
            'workflow.*',
            self.handle_workflow_event
        )

    async def handle_workflow_event(self, event: Event):
        print(f"📝 Workflow event: {event.type}")


class NotificationSubscriber(BaseSubscriber):
    """Sends notifications."""

    async def setup_subscriptions(self, eventbus):
        await self.subscribe(
            eventbus,
            'notification.send',
            self.handle_notification
        )

    async def handle_notification(self, event: Event):
        message = event.data.get('message')
        print(f"🔔 Notification: {message}")


class AuditSubscriber(BaseSubscriber):
    """Records all events for compliance."""

    async def setup_subscriptions(self, eventbus):
        await self.subscribe(
            eventbus,
            '*',  # All events
            self.handle_any_event
        )

    async def handle_any_event(self, event: Event):
        # Silent logging (don't print, too noisy)
        pass


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(title="BCM Platform - EventBus Integration Example")


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_eventbus() -> IEventBus:
    """
    Dependency to get EventBus instance.

    Usage in endpoints:
        @app.post("/workflows")
        async def create_workflow(bus: IEventBus = Depends(get_eventbus)):
            await bus.publish(event)
    """
    return app.state.eventbus


# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup():
    """
    Initialize EventBus and subscribers on application startup.

    This is called once when FastAPI starts.
    """
    print("🚀 Starting BCM Platform...")
    print()

    # 1. Create EventBus
    # For development: use 'memory'
    # For production: use 'redis' with redis_url
    eventbus = create_eventbus(
        backend='memory',
        # For production:
        # backend='redis',
        # redis_url='redis://localhost:6379'
    )

    print("✅ EventBus created (backend: memory)")

    # 2. Initialize subscribers
    subscribers = [
        WorkflowSubscriber(),
        NotificationSubscriber(),
        AuditSubscriber()
    ]

    # 3. Setup subscriptions
    for subscriber in subscribers:
        await subscriber.setup_subscriptions(eventbus)
        sub_count = subscriber.get_subscription_count()
        print(f"✅ {subscriber.__class__.__name__}: {sub_count} subscriptions")

    # 4. Store in app state for dependency injection
    app.state.eventbus = eventbus
    app.state.subscribers = subscribers

    print()
    print("🎉 BCM Platform ready!")
    print()


@app.on_event("shutdown")
async def shutdown():
    """
    Cleanup EventBus and subscribers on application shutdown.

    This is called when FastAPI shuts down (e.g., Ctrl+C).
    """
    print()
    print("👋 Shutting down BCM Platform...")

    # Cleanup subscribers
    for subscriber in app.state.subscribers:
        await subscriber.cleanup(app.state.eventbus)

    # Close EventBus
    await app.state.eventbus.close()

    print("✅ Cleanup complete")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "BCM Platform - EventBus Integration",
        "eventbus": "active"
    }


@app.post("/workflows")
async def create_workflow(
    name: str,
    module: str,
    bus: IEventBus = Depends(get_eventbus)
):
    """
    Create workflow and publish event.

    Example:
        POST /workflows?name=BIA&module=bia_001
    """
    # Simulate workflow creation
    workflow_id = f"{module}_{name.lower()}"

    # Publish event
    event = Event.create(
        event_type='workflow.created',
        data={
            'workflow_id': workflow_id,
            'name': name,
            'module': module
        },
        source='api',
        tenant_id='tenant_default'
    )

    await bus.publish(event)

    # Also publish notification
    notification_event = Event.create(
        event_type='notification.send',
        data={
            'message': f"Workflow '{name}' created successfully"
        },
        source='api',
        tenant_id='tenant_default'
    )

    await bus.publish(notification_event)

    return {
        "status": "created",
        "workflow_id": workflow_id,
        "events_published": 2
    }


@app.post("/workflows/{workflow_id}/complete")
async def complete_workflow(
    workflow_id: str,
    bus: IEventBus = Depends(get_eventbus)
):
    """
    Complete workflow and publish event.

    Example:
        POST /workflows/bia_001/complete
    """
    # Publish completion event
    event = Event.create(
        event_type='workflow.completed',
        data={
            'workflow_id': workflow_id,
            'duration_days': 5,
            'success': True
        },
        source='api',
        tenant_id='tenant_default',
        priority=EventPriority.HIGH
    )

    await bus.publish(event)

    # Publish notification
    notification_event = Event.create(
        event_type='notification.send',
        data={
            'message': f"🎉 Workflow '{workflow_id}' completed!"
        },
        source='api',
        tenant_id='tenant_default',
        priority=EventPriority.HIGH
    )

    await bus.publish(notification_event)

    return {
        "status": "completed",
        "workflow_id": workflow_id
    }


@app.get("/stats")
async def get_stats(bus: IEventBus = Depends(get_eventbus)):
    """
    Get EventBus statistics.

    Returns:
        - Number of events published
        - Number of events consumed
        - Number of errors
    """
    stats = await bus.get_stats()

    return {
        "eventbus_stats": stats,
        "subscribers": len(app.state.subscribers)
    }


# ============================================================================
# DEMO SCRIPT
# ============================================================================

async def demo():
    """
    Demonstrate the integration without running full FastAPI server.

    This is useful for testing the setup.
    """
    print("FastAPI Integration Demo (Standalone)")
    print("=" * 60)
    print()

    # Simulate startup
    await startup()

    # Simulate API calls
    bus = app.state.eventbus

    print("Simulating API calls...")
    print("-" * 60)
    print()

    # 1. Create workflow
    print("1. Creating workflow...")
    event1 = Event.create(
        event_type='workflow.created',
        data={'workflow_id': 'bia_001', 'name': 'BIA'},
        source='api',
        tenant_id='tenant_default'
    )
    await bus.publish(event1)
    await asyncio.sleep(0.1)
    print()

    # 2. Complete workflow
    print("2. Completing workflow...")
    event2 = Event.create(
        event_type='workflow.completed',
        data={'workflow_id': 'bia_001', 'success': True},
        source='api',
        tenant_id='tenant_default'
    )
    await bus.publish(event2)
    await asyncio.sleep(0.1)
    print()

    # 3. Send notification
    print("3. Sending notification...")
    event3 = Event.create(
        event_type='notification.send',
        data={'message': 'System ready!'},
        source='api',
        tenant_id='tenant_default'
    )
    await bus.publish(event3)
    await asyncio.sleep(0.1)
    print()

    # Show stats
    print("-" * 60)
    stats = await bus.get_stats()
    print(f"📊 Statistics:")
    print(f"   Published: {stats['published']}")
    print(f"   Consumed: {stats['consumed']}")
    print(f"   Errors: {stats['errors']}")
    print()

    # Simulate shutdown
    await shutdown()


if __name__ == '__main__':
    # Run demo (not full FastAPI server)
    asyncio.run(demo())

    # To run full FastAPI server:
    # uvicorn fastapi_integration:app --reload
