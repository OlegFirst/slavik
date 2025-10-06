"""
Events Package for Documents Service

Exports EventBus client, handlers, and publishers for event-driven architecture.
"""

from .eventbus import (
    EventBus,
    DocumentEvents,
    initialize_eventbus,
    get_eventbus,
    publish_document_event,
)

from .handlers import (
    handle_plan_created,
    handle_plan_activated,
    handle_exercise_completed,
    handle_policy_updated,
    handle_audit_started,
    handle_training_scheduled,
    EVENT_HANDLERS,
    get_handler,
)

from .publishers import (
    publish_document_uploaded,
    publish_document_approved,
    publish_document_rejected,
    publish_document_published,
    publish_document_archived,
    publish_document_expired,
    publish_document_shared,
    publish_document_version_created,
    publish_batch_operation,
    should_publish_event,
)

__all__ = [
    # EventBus
    'EventBus',
    'DocumentEvents',
    'initialize_eventbus',
    'get_eventbus',
    'publish_document_event',

    # Handlers
    'handle_plan_created',
    'handle_plan_activated',
    'handle_exercise_completed',
    'handle_policy_updated',
    'handle_audit_started',
    'handle_training_scheduled',
    'EVENT_HANDLERS',
    'get_handler',

    # Publishers
    'publish_document_uploaded',
    'publish_document_approved',
    'publish_document_rejected',
    'publish_document_published',
    'publish_document_archived',
    'publish_document_expired',
    'publish_document_shared',
    'publish_document_version_created',
    'publish_batch_operation',
    'should_publish_event',
]
