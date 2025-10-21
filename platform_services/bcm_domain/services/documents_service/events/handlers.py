"""
Event Handlers for Documents Service
Handles events from other BCM modules

Handles:
- bcm.plan.created → Create template documents for plan
- bcm.exercise.completed → Create exercise report document
- bcm.policy.updated → Notify about related documents
- bcm.audit.started → Prepare evidence documents
- bcm.training.scheduled → Link training materials
"""

from typing import Dict, Any
from datetime import datetime
import httpx


# ============================================================================
# PLAN EVENT HANDLERS
# ============================================================================

async def handle_plan_created(event_data: Dict[str, Any]):
    """
    Handle plan creation event.

    When a plan is created, automatically create template documents:
    - Plan document (the plan itself)
    - Procedures checklist
    - Contact list template
    - Communication template

    Event data:
        plan_id: int
        plan_code: str
        plan_name: str
        plan_type: str
        tenant_id: str
        created_by: str
    """
    print(f" Handling plan.created: {event_data.get('plan_code')}")

    plan_id = event_data.get("plan_id")
    plan_code = event_data.get("plan_code")
    plan_name = event_data.get("plan_name")
    plan_type = event_data.get("plan_type")
    tenant_id = event_data.get("tenant_id")
    created_by = event_data.get("created_by")

    # Template documents to create
    templates = [
        {
            "title": f"{plan_name} - Main Document",
            "document_type": "plan",
            "description": f"Main plan document for {plan_name}",
        },
        {
            "title": f"{plan_name} - Procedures Checklist",
            "document_type": "checklist",
            "description": f"Step-by-step procedures for {plan_name}",
        },
        {
            "title": f"{plan_name} - Contact List",
            "document_type": "contact_list",
            "description": f"Emergency contacts for {plan_name}",
        },
        {
            "title": f"{plan_name} - Communication Templates",
            "document_type": "communication",
            "description": f"Communication templates for {plan_name}",
        }
    ]

    # Create documents via API
    async with httpx.AsyncClient() as client:
        for template in templates:
            try:
                response = await client.post(
                    "http://localhost:8024/api/documents/documents",
                    json={
                        "tenant_id": tenant_id,
                        "title": template["title"],
                        "description": template["description"],
                        "document_type": template["document_type"],
                        "classification": "internal",
                        "is_controlled": True,
                        "owner_id": created_by,
                        "custom_metadata": {
                            "linked_to": "plan",
                            "plan_id": plan_id,
                            "plan_code": plan_code,
                            "auto_created": True
                        }
                    },
                    timeout=10.0
                )

                if response.status_code == 201:
                    doc_data = response.json()
                    print(f"   Created: {template['title']} (ID: {doc_data['document_id']})")
                else:
                    print(f"  ️  Failed to create: {template['title']}")

            except Exception as e:
                print(f"   Error creating {template['title']}: {e}")

    print(f" Plan documents created for: {plan_code}")


async def handle_plan_activated(event_data: Dict[str, Any]):
    """
    Handle plan activation event.

    When a plan is activated, update related documents:
    - Mark documents as "in use"
    - Log activation in document access log

    Event data:
        plan_id: int
        plan_code: str
        activated_by: str
        activated_at: str (ISO datetime)
    """
    print(f" Handling plan.activated: {event_data.get('plan_code')}")

    plan_id = event_data.get("plan_id")
    plan_code = event_data.get("plan_code")

    # Find all documents linked to this plan
    async with httpx.AsyncClient() as client:
        try:
            # Search for documents with this plan_id in custom_metadata
            response = await client.get(
                "http://localhost:8024/api/documents/documents",
                params={
                    "tenant_id": event_data.get("tenant_id", ""),
                    "search": plan_code,
                    "limit": 100
                },
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                documents = data.get("items", [])

                print(f"  Found {len(documents)} documents for plan {plan_code}")

                # Could add activation marker to documents here
                # For now, just log
                for doc in documents:
                    print(f"   {doc['title']} (ID: {doc['document_id']})")

        except Exception as e:
            print(f"   Error finding plan documents: {e}")


# ============================================================================
# EXERCISE EVENT HANDLERS
# ============================================================================

async def handle_exercise_completed(event_data: Dict[str, Any]):
    """
    Handle exercise completion event.

    When an exercise is completed, create exercise report document.

    Event data:
        exercise_id: int
        exercise_code: str
        exercise_name: str
        exercise_type: str
        tenant_id: str
        completed_by: str
        completed_at: str
        results: dict (observations, lessons_learned, action_items)
    """
    print(f" Handling exercise.completed: {event_data.get('exercise_code')}")

    exercise_id = event_data.get("exercise_id")
    exercise_code = event_data.get("exercise_code")
    exercise_name = event_data.get("exercise_name")
    tenant_id = event_data.get("tenant_id")
    completed_by = event_data.get("completed_by")
    results = event_data.get("results", {})

    # Create exercise report document
    report_title = f"Exercise Report - {exercise_name}"
    report_description = f"""
Exercise Report for {exercise_name} ({exercise_code})

Completed: {event_data.get('completed_at')}

Key Observations:
{chr(10).join('- ' + obs for obs in results.get('observations', [])[:5])}

Lessons Learned:
{chr(10).join('- ' + lesson for lesson in results.get('lessons_learned', [])[:5])}

Action Items:
{chr(10).join('- ' + action for action in results.get('action_items', [])[:5])}
    """.strip()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8024/api/documents/documents",
                json={
                    "tenant_id": tenant_id,
                    "title": report_title,
                    "description": report_description,
                    "document_type": "exercise_report",
                    "classification": "internal",
                    "is_controlled": True,
                    "requires_approval": True,
                    "owner_id": completed_by,
                    "custom_metadata": {
                        "linked_to": "exercise",
                        "exercise_id": exercise_id,
                        "exercise_code": exercise_code,
                        "auto_created": True,
                        "results": results
                    }
                },
                timeout=10.0
            )

            if response.status_code == 201:
                doc_data = response.json()
                print(f"   Exercise report created: ID {doc_data['document_id']}")
            else:
                print(f"  ️  Failed to create exercise report")

        except Exception as e:
            print(f"   Error creating exercise report: {e}")


# ============================================================================
# POLICY EVENT HANDLERS
# ============================================================================

async def handle_policy_updated(event_data: Dict[str, Any]):
    """
    Handle policy update event.

    When a policy is updated, check for related documents:
    - Find documents that reference this policy
    - Flag them for review

    Event data:
        policy_id: int
        policy_code: str
        policy_name: str
        tenant_id: str
        updated_by: str
        changes: dict
    """
    print(f" Handling policy.updated: {event_data.get('policy_code')}")

    policy_code = event_data.get("policy_code")
    tenant_id = event_data.get("tenant_id")

    # Find documents that might reference this policy
    # (Documents with policy type or mentioning policy in title)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "http://localhost:8024/api/documents/documents",
                params={
                    "tenant_id": tenant_id,
                    "search": policy_code,
                    "limit": 100
                },
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                documents = data.get("items", [])

                print(f"  Found {len(documents)} documents related to policy {policy_code}")

                # Could flag these for review
                # For now, just log
                for doc in documents:
                    print(f"   May need review: {doc['title']} (ID: {doc['document_id']})")

        except Exception as e:
            print(f"   Error finding policy documents: {e}")


# ============================================================================
# AUDIT EVENT HANDLERS
# ============================================================================

async def handle_audit_started(event_data: Dict[str, Any]):
    """
    Handle audit start event.

    When an audit starts, prepare evidence documents:
    - Find documents relevant to audit scope
    - Create collection folder

    Event data:
        audit_id: int
        audit_code: str
        audit_scope: str
        iso_clauses: list
        tenant_id: str
        started_by: str
    """
    print(f" Handling audit.started: {event_data.get('audit_code')}")

    audit_id = event_data.get("audit_id")
    audit_code = event_data.get("audit_code")
    iso_clauses = event_data.get("iso_clauses", [])
    tenant_id = event_data.get("tenant_id")

    # Find documents for audit scope
    # Documents with ISO clauses matching audit scope
    print(f"  Audit scope: {', '.join(iso_clauses)}")
    print(f"  Preparing evidence documents...")

    # Could create audit evidence collection document here
    # For now, just log
    print(f"   Audit evidence preparation for: {audit_code}")


# ============================================================================
# TRAINING EVENT HANDLERS
# ============================================================================

async def handle_training_scheduled(event_data: Dict[str, Any]):
    """
    Handle training scheduled event.

    When training is scheduled, link training materials:
    - Find relevant training documents
    - Notify trainer

    Event data:
        training_id: int
        training_code: str
        training_topic: str
        tenant_id: str
        scheduled_by: str
    """
    print(f" Handling training.scheduled: {event_data.get('training_code')}")

    training_code = event_data.get("training_code")
    training_topic = event_data.get("training_topic")
    tenant_id = event_data.get("tenant_id")

    # Find training materials
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "http://localhost:8024/api/documents/documents",
                params={
                    "tenant_id": tenant_id,
                    "document_type": "training_material",
                    "search": training_topic,
                    "limit": 50
                },
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                materials = data.get("items", [])

                print(f"  Found {len(materials)} training materials for: {training_topic}")

                for material in materials:
                    print(f"   {material['title']} (ID: {material['document_id']})")

        except Exception as e:
            print(f"   Error finding training materials: {e}")


# ============================================================================
# HANDLER REGISTRY
# ============================================================================

EVENT_HANDLERS = {
    "bcm.plan.created": handle_plan_created,
    "bcm.plan.activated": handle_plan_activated,
    "bcm.exercise.completed": handle_exercise_completed,
    "bcm.policy.updated": handle_policy_updated,
    "bcm.audit.started": handle_audit_started,
    "bcm.training.scheduled": handle_training_scheduled,
}


def get_handler(event_type: str):
    """Get handler function for event type"""
    return EVENT_HANDLERS.get(event_type)
