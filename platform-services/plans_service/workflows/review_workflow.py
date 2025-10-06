"""
Plan Review Workflow
ISO 22301 Clause 8.4 - Plan review and maintenance
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum

from ..models.domain import ReviewFrequency, ReviewType


def calculate_next_review_date(
    last_review_date: datetime,
    frequency: str
) -> datetime:
    """Calculate next review date based on frequency"""
    if frequency == ReviewFrequency.MONTHLY.value:
        return last_review_date + timedelta(days=30)
    elif frequency == ReviewFrequency.QUARTERLY.value:
        return last_review_date + timedelta(days=90)
    elif frequency == ReviewFrequency.SEMIANNUALLY.value:
        return last_review_date + timedelta(days=180)
    elif frequency == ReviewFrequency.ANNUALLY.value:
        return last_review_date + timedelta(days=365)
    else:
        return last_review_date + timedelta(days=365)


def is_review_due(plan: Any) -> bool:
    """Check if plan review is due"""
    if not plan.next_review_date:
        return False
    return plan.next_review_date <= datetime.utcnow()


def get_review_status(plan: Any) -> Dict[str, Any]:
    """Get plan review status"""
    review_due = is_review_due(plan)
    days_overdue = 0

    if review_due and plan.next_review_date:
        days_overdue = (datetime.utcnow() - plan.next_review_date).days

    return {
        "review_due": review_due,
        "days_overdue": days_overdue,
        "last_review_date": plan.last_review_date,
        "next_review_date": plan.next_review_date,
        "review_frequency": plan.review_frequency.value if plan.review_frequency else None,
        "status": "overdue" if days_overdue > 30 else "due" if review_due else "current"
    }


class ReviewTriggerType(str, Enum):
    """Review trigger types"""
    SCHEDULED = "scheduled"
    POST_EXERCISE = "post_exercise"
    POST_INCIDENT = "post_incident"
    ORGANIZATIONAL_CHANGE = "organizational_change"
    AD_HOC = "ad_hoc"


def should_trigger_review(
    plan: Any,
    trigger_type: ReviewTriggerType,
    **kwargs
) -> bool:
    """Determine if review should be triggered"""
    if trigger_type == ReviewTriggerType.SCHEDULED:
        return is_review_due(plan)

    elif trigger_type == ReviewTriggerType.POST_EXERCISE:
        # Always review after exercise
        return True

    elif trigger_type == ReviewTriggerType.POST_INCIDENT:
        # Review if plan was activated during incident
        incident_id = kwargs.get("incident_id")
        if incident_id and plan.activations:
            return any(
                a.triggered_by_incident_id == incident_id
                for a in plan.activations
            )
        return False

    elif trigger_type == ReviewTriggerType.ORGANIZATIONAL_CHANGE:
        # Review if significant organizational change
        return True

    return False


class ReviewWorkflowAction(str, Enum):
    """Review workflow actions"""
    START_REVIEW = "start_review"
    COMPLETE_REVIEW = "complete_review"
    IDENTIFY_CHANGES = "identify_changes"
    CREATE_NEW_VERSION = "create_new_version"
    APPROVE_REVIEW = "approve_review"


def execute_review_transition(
    review: Any,
    action: ReviewWorkflowAction,
    user_id: str,
    **kwargs
) -> tuple[bool, Optional[str], Dict[str, Any]]:
    """Execute review workflow transition"""
    update_dict = {}

    if action == ReviewWorkflowAction.START_REVIEW:
        update_dict["review_status"] = "in_progress"
        update_dict["started_by"] = user_id
        update_dict["started_at"] = datetime.utcnow()

    elif action == ReviewWorkflowAction.COMPLETE_REVIEW:
        update_dict["review_status"] = "completed"
        update_dict["completed_at"] = datetime.utcnow()
        update_dict["findings"] = kwargs.get("findings")
        update_dict["recommendations"] = kwargs.get("recommendations")

    elif action == ReviewWorkflowAction.IDENTIFY_CHANGES:
        update_dict["review_status"] = "changes_required"
        update_dict["action_items"] = kwargs.get("action_items", [])

    elif action == ReviewWorkflowAction.APPROVE_REVIEW:
        update_dict["approved"] = True
        update_dict["approved_by_user_id"] = user_id
        update_dict["approval_date"] = datetime.utcnow()

    return True, None, update_dict


def generate_review_checklist(plan: Any) -> List[Dict[str, Any]]:
    """Generate review checklist based on plan type"""
    checklist = [
        {
            "item": "Verify plan objectives are still valid",
            "category": "content",
            "mandatory": True
        },
        {
            "item": "Confirm scope is accurate and complete",
            "category": "content",
            "mandatory": True
        },
        {
            "item": "Review and update contact lists",
            "category": "contacts",
            "mandatory": True
        },
        {
            "item": "Verify resource availability",
            "category": "resources",
            "mandatory": True
        },
        {
            "item": "Check if RTO/RPO targets are achievable",
            "category": "objectives",
            "mandatory": True
        },
        {
            "item": "Review procedures for accuracy",
            "category": "procedures",
            "mandatory": True
        },
        {
            "item": "Update based on lessons learned from tests/incidents",
            "category": "improvement",
            "mandatory": True
        },
        {
            "item": "Verify compliance with ISO 22301",
            "category": "compliance",
            "mandatory": True
        }
    ]

    # Add plan-type specific items
    if plan.plan_type.value == "disaster_recovery":
        checklist.append({
            "item": "Verify backup and recovery procedures",
            "category": "technical",
            "mandatory": True
        })

    if plan.plan_type.value == "crisis_communication":
        checklist.append({
            "item": "Review communication templates and channels",
            "category": "communication",
            "mandatory": True
        })

    return checklist


def calculate_review_priority(plan: Any) -> str:
    """Calculate review priority based on various factors"""
    priority_score = 0

    # Factor 1: Overdue reviews
    if is_review_due(plan):
        review_status = get_review_status(plan)
        if review_status["days_overdue"] > 60:
            priority_score += 10
        elif review_status["days_overdue"] > 30:
            priority_score += 5

    # Factor 2: Plan priority
    if plan.priority.value == "critical":
        priority_score += 5
    elif plan.priority.value == "high":
        priority_score += 3

    # Factor 3: Recent activations
    if plan.activations:
        recent_activations = [
            a for a in plan.activations
            if (datetime.utcnow() - a.activation_datetime).days <= 90
        ]
        priority_score += len(recent_activations) * 2

    # Factor 4: Time since last review
    if plan.last_review_date:
        days_since_review = (datetime.utcnow() - plan.last_review_date).days
        if days_since_review > 365:
            priority_score += 8

    # Determine priority level
    if priority_score >= 15:
        return "urgent"
    elif priority_score >= 8:
        return "high"
    elif priority_score >= 3:
        return "medium"
    else:
        return "low"
