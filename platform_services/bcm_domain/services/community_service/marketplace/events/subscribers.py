"""
Marketplace Service - Event Subscribers
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

async def on_certification_issued(event_data: Dict[str, Any]):
    """
    Handle certification issued event from Learning Service

    Actions:
    - Update specialist profile with new certification
    - Recalculate competency score
    - Notify matching projects
    - Increase specialist ranking

    Event: learning.certification.issued
    Data: {
        "enrollment_id": int,
        "person_id": str,
        "certification_number": str,
        "certification_name": str,
        "certification_date": str,
        "expiry_date": str,
        "tenant_id": str
    }
    """
    try:
        person_id = event_data.get("person_id")
        cert_number = event_data.get("certification_number")
        cert_name = event_data.get("certification_name", "Professional Certification")
        tenant_id = event_data.get("tenant_id")

        logger.info(f" Certification issued: {person_id} earned '{cert_name}' ({cert_number})")

        # TODO Phase 5: Find specialist by person_id
        # TODO Phase 5: Add certification to specialist.certifications JSONB
        # TODO Phase 5: Recalculate competency_scores
        # TODO Phase 5: Find matching projects and notify

        logger.info(f" Processed certification.issued event for specialist {person_id}")

    except Exception as e:
        logger.error(f" Error processing certification.issued: {e}")


async def on_training_completed(event_data: Dict[str, Any]):
    """
    Handle training completion event from Learning Service

    Actions:
    - Update specialist competency areas
    - Add to specialist skills list
    - Increase specialist experience score

    Event: learning.training.completed
    Data: {
        "enrollment_id": int,
        "person_id": str,
        "program_id": int,
        "program_name": str,
        "program_type": str,
        "competency_areas": list[str],
        "tenant_id": str
    }
    """
    try:
        person_id = event_data.get("person_id")
        program_name = event_data.get("program_name")
        competency_areas = event_data.get("competency_areas", [])

        logger.info(f" Training completed: {person_id} finished '{program_name}'")

        # TODO Phase 5: Update specialist competency_scores
        # TODO Phase 5: Add skills to specialist profile
        # TODO Phase 5: Update specialist availability if training was required

        logger.info(f" Processed training.completed event for specialist {person_id}")

    except Exception as e:
        logger.error(f" Error processing training.completed: {e}")


async def on_competence_recorded(event_data: Dict[str, Any]):
    """
    Handle competence recorded event from Governance Service

    Actions:
    - Update specialist competency matrix
    - Sync with governance competency framework
    - Update specialist matching algorithm weights

    Event: governance.competence.recorded
    Data: {
        "person_id": str,
        "competency_area": str,
        "proficiency_level": str,
        "assessed_by": str,
        "tenant_id": str
    }
    """
    try:
        person_id = event_data.get("person_id")
        competency_area = event_data.get("competency_area")
        proficiency_level = event_data.get("proficiency_level")

        logger.info(f" Competence recorded: {person_id} - {competency_area} ({proficiency_level})")

        # TODO Phase 5: Update specialist.competency_scores JSONB
        # TODO Phase 5: Recalculate matching score for active projects

        logger.info(f" Processed competence.recorded event")

    except Exception as e:
        logger.error(f" Error processing competence.recorded: {e}")


# ============================================================================
# Governance Service Events
# ============================================================================

async def on_role_assigned(event_data: Dict[str, Any]):
    """
    Handle role assigned event from Governance Service

    Actions:
    - Auto-create specialist profile if role is "bcm_specialist"
    - Set verification status based on governance role
    - Update specialist permissions

    Event: governance.role.assigned
    Data: {
        "person_id": str,
        "role_code": str,
        "role_name": str,
        "competencies": list[str],
        "tenant_id": str
    }
    """
    try:
        person_id = event_data.get("person_id")
        role_code = event_data.get("role_code")
        role_name = event_data.get("role_name")
        competencies = event_data.get("competencies", [])
        tenant_id = event_data.get("tenant_id")

        logger.info(f" Role assigned: {person_id} → {role_name} ({role_code})")

        # Special handling for BCM specialists - PHASE 5: AUTO-CREATE SPECIALIST
        if role_code in ["bcm_specialist", "bcm_consultant", "bcm_manager"]:
            logger.info(f" BCM role detected - auto-creating specialist profile")

            async for db in get_db():
                try:
                    from database.models import Specialist
                    from sqlalchemy import select
                    import uuid

                    # Check if specialist profile already exists
                    result = await db.execute(
                        select(Specialist).where(Specialist.user_id == uuid.UUID(person_id))
                    )
                    specialist = result.scalar_one_or_none()

                    if not specialist:
                        # Auto-create specialist profile
                        specialist = Specialist(
                            user_id=uuid.UUID(person_id),
                            tenant_id=uuid.UUID(tenant_id),
                            name=role_name,  # Temporary, should be updated by user
                            title=f"{role_name}",
                            bio=f"BCM Professional verified via Governance role: {role_name}",
                            is_verified=True,
                            verified_by_role_id=role_code,
                            verification_source="governance_role",
                            verification_notes=f"Auto-verified via {role_name} role assignment"
                        )
                        db.add(specialist)
                        await db.commit()
                        logger.info(f" Auto-created specialist profile for {person_id}")
                    else:
                        # Update existing specialist verification
                        specialist.is_verified = True
                        specialist.verified_by_role_id = role_code
                        specialist.verification_source = "governance_role"
                        specialist.verification_notes = f"Verified via {role_name} role assignment"
                        await db.commit()
                        logger.info(f" Updated specialist verification for {person_id}")

                except Exception as db_error:
                    logger.error(f"Database error in role.assigned handler: {db_error}")
                    await db.rollback()
                finally:
                    break

        logger.info(f" Processed role.assigned event")

    except Exception as e:
        logger.error(f" Error processing role.assigned: {e}")


async def on_role_removed(event_data: Dict[str, Any]):
    """
    Handle role removed event from Governance Service

    Actions:
    - Update specialist verification status
    - Adjust specialist permissions
    - Send notification to specialist

    Event: governance.role.removed
    Data: {
        "person_id": str,
        "role_code": str,
        "tenant_id": str
    }
    """
    try:
        person_id = event_data.get("person_id")
        role_code = event_data.get("role_code")

        logger.info(f" Role removed: {person_id} lost {role_code}")

        # If BCM role removed, update verification
        if role_code in ["bcm_specialist", "bcm_consultant", "bcm_manager"]:
            logger.info(f"️  BCM role removed - may need to update specialist verification")

            # TODO Phase 5: Update specialist.is_verified status
            # TODO Phase 5: Set verified_by_role_id = NULL

        logger.info(f" Processed role.removed event")

    except Exception as e:
        logger.error(f" Error processing role.removed: {e}")


async def on_resource_allocated(event_data: Dict[str, Any]):
    """
    Handle resource allocated event from Governance Service

    Actions:
    - Update specialist availability if resource is a person
    - Block specialist calendar for allocated period
    - Update project resource assignments

    Event: governance.resource.allocated
    Data: {
        "resource_id": int,
        "resource_type": str,
        "allocated_to": str,
        "allocation_start": str,
        "allocation_end": str,
        "tenant_id": str
    }
    """
    try:
        resource_type = event_data.get("resource_type")
        allocated_to = event_data.get("allocated_to")

        logger.info(f" Resource allocated: {resource_type} → {allocated_to}")

        # Only process if resource is a person
        if resource_type == "person":
            # TODO Phase 5: Update specialist availability_status
            # TODO Phase 5: Block calendar dates

            pass

        logger.info(f" Processed resource.allocated event")

    except Exception as e:
        logger.error(f" Error processing resource.allocated: {e}")


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
        eventbus.subscribe("learning.certification.issued", on_certification_issued)
        eventbus.subscribe("learning.training.completed", on_training_completed)
        eventbus.subscribe("governance.competence.recorded", on_competence_recorded)

        # Governance Service events
        eventbus.subscribe("governance.role.assigned", on_role_assigned)
        eventbus.subscribe("governance.role.removed", on_role_removed)
        eventbus.subscribe("governance.resource.allocated", on_resource_allocated)

        logger.info(" Marketplace event subscribers registered:")
        logger.info("   - learning.certification.issued")
        logger.info("   - learning.training.completed")
        logger.info("   - governance.competence.recorded")
        logger.info("   - governance.role.assigned")
        logger.info("   - governance.role.removed")
        logger.info("   - governance.resource.allocated")

    except Exception as e:
        logger.error(f" Failed to setup event subscriptions: {e}")
        raise
