"""
Event Publishers
Публикация событий в EventBus
"""

from shared.eventbus import get_eventbus
from typing import Dict, Any


async def publish_program_created(program_id: int, tenant_id: str, program_code: str):
    """Publish program created event"""
    eventbus = get_eventbus()
    await eventbus.publish(
        "learning.program.created",
        {
            "program_id": program_id,
            "tenant_id": tenant_id,
            "program_code": program_code,
        }
    )


async def publish_enrollment_completed(enrollment_id: int, tenant_id: str, person_id: str):
    """Publish enrollment completed event"""
    eventbus = get_eventbus()
    await eventbus.publish(
        "learning.enrollment.completed",
        {
            "enrollment_id": enrollment_id,
            "tenant_id": tenant_id,
            "person_id": person_id,
        }
    )


async def publish_certification_issued(
    enrollment_id: int,
    tenant_id: str,
    person_id: str,
    certification_number: str
):
    """Publish certification issued event"""
    eventbus = get_eventbus()
    await eventbus.publish(
        "learning.certification.issued",
        {
            "enrollment_id": enrollment_id,
            "tenant_id": tenant_id,
            "person_id": person_id,
            "certification_number": certification_number,
        }
    )
