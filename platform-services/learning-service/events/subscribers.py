"""
Event Subscribers
Подписка на события других сервисов
"""

from shared.eventbus import get_eventbus
import logging

logger = logging.getLogger(__name__)


async def setup_subscriptions():
    """Setup event subscriptions"""
    eventbus = get_eventbus()

    # Subscribe to governance events
    @eventbus.subscribe("governance.organization.created")
    async def on_organization_created(event):
        """When organization created, можно создать default training programs"""
        logger.info(f"Organization created: {event.data.get('org_id')}")
        # TODO: Create default training programs

    @eventbus.subscribe("governance.person.added")
    async def on_person_added(event):
        """When person added to org, можно авто-назначить обязательные тренинги"""
        logger.info(f"Person added: {event.data.get('person_id')}")
        # TODO: Auto-enroll in mandatory trainings
