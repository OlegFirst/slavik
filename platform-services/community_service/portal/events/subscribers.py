"""
Portal Service - Event Subscribers
Handles events from Learning and Governance services
"""

import sys
from pathlib import Path

# Add shared library to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "shared"))

import logging
from typing import Dict, Any
from shared.eventbus import get_eventbus
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db

logger = logging.getLogger(__name__)


# ============================================================================
# Learning Service Events
# ============================================================================

async def on_training_completed(event_data: Dict[str, Any]):
    """
    Handle training completion event from Learning Service

    Actions:
    - Award forum badge "Knowledgeable" to user
    - Update author competency display in forum
    - Suggest creating knowledge article about training topic

    Event: learning.training.completed
    Data: {
        "enrollment_id": int,
        "person_id": str,
        "program_id": int,
        "program_name": str,
        "tenant_id": str
    }
    """
    try:
        person_id = event_data.get("person_id")
        program_name = event_data.get("program_name")
        tenant_id = event_data.get("tenant_id")

        logger.info(f"🎓 Training completed: {person_id} finished '{program_name}'")

        # PHASE 5: Award forum badge and update reputation
        async for db in get_db():
            try:
                from services.reputation_service import ReputationService
                from database.models import Badge, UserBadge, UserReputation
                from sqlalchemy import select

                reputation_service = ReputationService()

                # Get or create reputation record
                reputation = await reputation_service.get_or_create_reputation(db, person_id)

                # Award reputation points for completing training
                await reputation_service.award_points(
                    db=db,
                    user_id=person_id,
                    event_type='training_completed',
                    points=50  # Base points for training completion
                )

                # Check if "Knowledgeable" badge exists, create if not
                badge_result = await db.execute(
                    select(Badge).where(Badge.badge_code == 'knowledgeable')
                )
                badge = badge_result.scalar_one_or_none()

                if not badge:
                    badge = Badge(
                        badge_code='knowledgeable',
                        badge_name='Knowledgeable',
                        badge_type='achievement',
                        description='Completed a training program',
                        icon='🎓'
                    )
                    db.add(badge)
                    await db.flush()

                # Award badge if user doesn't have it yet
                existing_badge = await db.execute(
                    select(UserBadge).where(
                        UserBadge.user_id == person_id,
                        UserBadge.badge_id == badge.id
                    )
                )
                if not existing_badge.scalar_one_or_none():
                    user_badge = UserBadge(
                        user_id=person_id,
                        badge_id=badge.id,
                        earned_for=f"Completed training: {program_name}"
                    )
                    db.add(user_badge)
                    reputation.badges_earned += 1

                await db.commit()
                logger.info(f"✅ Awarded 'Knowledgeable' badge to {person_id}")

            except Exception as db_error:
                logger.error(f"Database error in training.completed handler: {db_error}")
                await db.rollback()
            finally:
                break

        logger.info(f"✅ Processed training.completed event for {person_id}")

    except Exception as e:
        logger.error(f"❌ Error processing training.completed: {e}")


async def on_certification_issued(event_data: Dict[str, Any]):
    """
    Handle certification issued event from Learning Service

    Actions:
    - Grant "Verified Expert" badge in forum
    - Increase reputation score
    - Display certification in user profile

    Event: learning.certification.issued
    Data: {
        "enrollment_id": int,
        "person_id": str,
        "certification_number": str,
        "certification_name": str,
        "tenant_id": str
    }
    """
    try:
        person_id = event_data.get("person_id")
        cert_number = event_data.get("certification_number")
        cert_name = event_data.get("certification_name", "Professional Certification")

        logger.info(f"🏆 Certification issued: {person_id} earned '{cert_name}' ({cert_number})")

        # PHASE 5: Award "Verified Expert" badge and increase reputation
        async for db in get_db():
            try:
                from services.reputation_service import ReputationService
                from database.models import Badge, UserBadge
                from sqlalchemy import select

                reputation_service = ReputationService()

                # Get or create reputation record
                reputation = await reputation_service.get_or_create_reputation(db, person_id)

                # Award significant reputation points for certification
                await reputation_service.award_points(
                    db=db,
                    user_id=person_id,
                    event_type='certification_earned',
                    points=200  # High value for certification
                )

                # Check if "Verified Expert" badge exists
                badge_result = await db.execute(
                    select(Badge).where(Badge.badge_code == 'verified_expert')
                )
                badge = badge_result.scalar_one_or_none()

                if not badge:
                    badge = Badge(
                        badge_code='verified_expert',
                        badge_name='Verified Expert',
                        badge_type='certification',
                        description='Earned a professional certification',
                        icon='🏆'
                    )
                    db.add(badge)
                    await db.flush()

                # Award badge (allow multiple certifications)
                user_badge = UserBadge(
                    user_id=person_id,
                    badge_id=badge.id,
                    earned_for=f"Earned certification: {cert_name} ({cert_number})"
                )
                db.add(user_badge)
                reputation.badges_earned += 1

                # Update certifications count (Phase 4 column)
                reputation.certifications_count += 1
                reputation.last_certification_date = event_data.get('issued_date')

                await db.commit()
                logger.info(f"✅ Awarded 'Verified Expert' badge and 200 points to {person_id}")

            except Exception as db_error:
                logger.error(f"Database error in certification.issued handler: {db_error}")
                await db.rollback()
            finally:
                break

        logger.info(f"✅ Processed certification.issued event for {person_id}")

    except Exception as e:
        logger.error(f"❌ Error processing certification.issued: {e}")


async def on_program_published(event_data: Dict[str, Any]):
    """
    Handle training program published event from Learning Service

    Actions:
    - Create knowledge article template about the program
    - Add to "Training Resources" category

    Event: learning.program.published
    Data: {
        "program_id": int,
        "program_code": str,
        "program_name": str,
        "tenant_id": str
    }
    """
    try:
        program_id = event_data.get("program_id")
        program_name = event_data.get("program_name")

        logger.info(f"📚 Training program published: '{program_name}' (ID: {program_id})")

        # TODO Phase 5: Auto-create knowledge article about program

        logger.info(f"✅ Processed program.published event")

    except Exception as e:
        logger.error(f"❌ Error processing program.published: {e}")


# ============================================================================
# Governance Service Events
# ============================================================================

async def on_policy_created(event_data: Dict[str, Any]):
    """
    Handle policy created event from Governance Service

    Actions:
    - Create forum discussion category for the policy
    - Suggest knowledge articles about policy implementation
    - Notify relevant users

    Event: governance.policy.created
    Data: {
        "policy_id": int,
        "policy_code": str,
        "title": str,
        "policy_type": str,
        "iso_clause": str,
        "tenant_id": str
    }
    """
    try:
        policy_id = event_data.get("policy_id")
        title = event_data.get("title")
        policy_type = event_data.get("policy_type")
        iso_clause = event_data.get("iso_clause")

        logger.info(f"📋 Policy created: '{title}' (Type: {policy_type}, ISO: {iso_clause})")

        # TODO Phase 5: Create forum category for policy discussion
        # TODO Phase 5: Suggest knowledge articles

        logger.info(f"✅ Processed policy.created event")

    except Exception as e:
        logger.error(f"❌ Error processing policy.created: {e}")


async def on_policy_published(event_data: Dict[str, Any]):
    """
    Handle policy published event from Governance Service

    Actions:
    - Create announcement in forum
    - Link to related knowledge articles
    - Update policy references in existing articles

    Event: governance.policy.published
    Data: {
        "policy_id": int,
        "title": str,
        "effective_date": str,
        "tenant_id": str
    }
    """
    try:
        policy_id = event_data.get("policy_id")
        title = event_data.get("title")
        effective_date = event_data.get("effective_date")

        logger.info(f"📢 Policy published: '{title}' (Effective: {effective_date})")

        # TODO Phase 5: Create forum announcement
        # TODO Phase 5: Update article references

        logger.info(f"✅ Processed policy.published event")

    except Exception as e:
        logger.error(f"❌ Error processing policy.published: {e}")


async def on_role_assigned(event_data: Dict[str, Any]):
    """
    Handle role assigned event from Governance Service

    Actions:
    - Update forum moderator permissions
    - Display role badge in forum
    - Grant role-specific forum access

    Event: governance.role.assigned
    Data: {
        "person_id": str,
        "role_code": str,
        "role_name": str,
        "tenant_id": str
    }
    """
    try:
        person_id = event_data.get("person_id")
        role_name = event_data.get("role_name")
        role_code = event_data.get("role_code")

        logger.info(f"👤 Role assigned: {person_id} → {role_name} ({role_code})")

        # TODO Phase 5: Update forum permissions
        # TODO Phase 5: Add role badge to profile

        logger.info(f"✅ Processed role.assigned event")

    except Exception as e:
        logger.error(f"❌ Error processing role.assigned: {e}")


# ============================================================================
# Subscriber Setup
# ============================================================================

async def setup_subscriptions():
    """
    Register all event subscribers with EventBus

    Call this during application startup in main.py
    """
    try:
        eventbus = get_eventbus()

        # Learning Service events
        eventbus.subscribe("learning.training.completed", on_training_completed)
        eventbus.subscribe("learning.certification.issued", on_certification_issued)
        eventbus.subscribe("learning.program.published", on_program_published)

        # Governance Service events
        eventbus.subscribe("governance.policy.created", on_policy_created)
        eventbus.subscribe("governance.policy.published", on_policy_published)
        eventbus.subscribe("governance.role.assigned", on_role_assigned)

        logger.info("✅ Portal event subscribers registered:")
        logger.info("   - learning.training.completed")
        logger.info("   - learning.certification.issued")
        logger.info("   - learning.program.published")
        logger.info("   - governance.policy.created")
        logger.info("   - governance.policy.published")
        logger.info("   - governance.role.assigned")

    except Exception as e:
        logger.error(f"❌ Failed to setup event subscriptions: {e}")
        raise
