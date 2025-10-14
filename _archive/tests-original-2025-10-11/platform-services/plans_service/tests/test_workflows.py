"""
Workflow Tests
Tests for plan lifecycle workflow transitions
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from plans_service.workflows.plan_lifecycle import (
    PlanWorkflowAction,
    execute_plan_transition,
    get_workflow_summary
)
from plans_service.models.domain import PlanStatus


class TestPlanWorkflow:
    """Test suite for plan workflow transitions"""

    def test_draft_to_review_transition(self):
        """Test DRAFT → UNDER_REVIEW transition"""
        # Create mock plan with required attributes
        plan = Mock()
        plan.status = PlanStatus.DRAFT
        plan.objective = "Valid objective for the plan"
        plan.scope = "Valid scope for the plan"
        plan.procedures = [Mock()]  # At least one procedure

        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.SUBMIT_FOR_REVIEW,
            user_id="user_001"
        )

        assert success is True
        assert error is None
        assert update_dict["status"] == PlanStatus.UNDER_REVIEW
        assert "submitted_for_review_at" in update_dict

    def test_draft_to_review_missing_objective(self):
        """Test DRAFT → UNDER_REVIEW fails without objective"""
        plan = Mock()
        plan.status = PlanStatus.DRAFT
        plan.objective = None  # Missing objective
        plan.scope = "Valid scope"
        plan.procedures = [Mock()]

        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.SUBMIT_FOR_REVIEW,
            user_id="user_001"
        )

        assert success is False
        assert error is not None
        assert "objective and scope" in error

    def test_draft_to_review_missing_scope(self):
        """Test DRAFT → UNDER_REVIEW fails without scope"""
        plan = Mock()
        plan.status = PlanStatus.DRAFT
        plan.objective = "Valid objective"
        plan.scope = None  # Missing scope
        plan.procedures = [Mock()]

        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.SUBMIT_FOR_REVIEW,
            user_id="user_001"
        )

        assert success is False
        assert error is not None
        assert "objective and scope" in error

    def test_draft_to_review_no_procedures(self):
        """Test DRAFT → UNDER_REVIEW fails without procedures"""
        plan = Mock()
        plan.status = PlanStatus.DRAFT
        plan.objective = "Valid objective"
        plan.scope = "Valid scope"
        plan.procedures = []  # No procedures

        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.SUBMIT_FOR_REVIEW,
            user_id="user_001"
        )

        assert success is False
        assert error is not None
        assert "at least one procedure" in error

    def test_review_to_approved_transition(self):
        """Test UNDER_REVIEW → APPROVED transition"""
        plan = Mock()
        plan.status = PlanStatus.UNDER_REVIEW

        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.APPROVE,
            user_id="approver_001",
            approval_notes="Plan looks good"
        )

        assert success is True
        assert error is None
        assert update_dict["status"] == PlanStatus.APPROVED
        assert update_dict["approved_by_user_id"] == "approver_001"
        assert "approval_date" in update_dict
        assert update_dict["approval_notes"] == "Plan looks good"

    def test_review_to_draft_transition(self):
        """Test UNDER_REVIEW → DRAFT transition (rejection)"""
        plan = Mock()
        plan.status = PlanStatus.UNDER_REVIEW

        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.REJECT,
            user_id="reviewer_001"
        )

        assert success is True
        assert error is None
        assert update_dict["status"] == PlanStatus.DRAFT

    def test_approved_to_active_transition(self):
        """Test APPROVED → ACTIVE transition"""
        plan = Mock()
        plan.status = PlanStatus.APPROVED
        plan.contact_lists = [Mock()]  # At least one contact list

        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.ACTIVATE,
            user_id="user_001"
        )

        assert success is True
        assert error is None
        assert update_dict["status"] == PlanStatus.ACTIVE
        assert "activated_at" in update_dict
        assert update_dict["activated_by"] == "user_001"

    def test_approved_to_active_no_contacts(self):
        """Test APPROVED → ACTIVE fails without contact lists"""
        plan = Mock()
        plan.status = PlanStatus.APPROVED
        plan.contact_lists = []  # No contact lists

        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.ACTIVATE,
            user_id="user_001"
        )

        assert success is False
        assert error is not None
        assert "contact list" in error

    def test_active_to_approved_transition(self):
        """Test ACTIVE → APPROVED transition (deactivation)"""
        plan = Mock()
        plan.status = PlanStatus.ACTIVE

        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.DEACTIVATE,
            user_id="user_001"
        )

        assert success is True
        assert error is None
        assert update_dict["status"] == PlanStatus.APPROVED
        assert "deactivated_at" in update_dict

    def test_approved_to_archived_transition(self):
        """Test APPROVED → ARCHIVED transition"""
        plan = Mock()
        plan.status = PlanStatus.APPROVED

        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.ARCHIVE,
            user_id="user_001"
        )

        assert success is True
        assert error is None
        assert update_dict["status"] == PlanStatus.ARCHIVED

    def test_active_to_archived_transition(self):
        """Test ACTIVE → ARCHIVED transition"""
        plan = Mock()
        plan.status = PlanStatus.ACTIVE

        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.ARCHIVE,
            user_id="user_001"
        )

        assert success is True
        assert error is None
        assert update_dict["status"] == PlanStatus.ARCHIVED

    def test_invalid_transition_draft_to_approved(self):
        """Test invalid state transition raises error"""
        plan = Mock()
        plan.status = PlanStatus.DRAFT

        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.APPROVE,
            user_id="user_001"
        )

        assert success is False
        assert error is not None
        assert "Cannot" in error or "approve" in error.lower()

    def test_invalid_transition_draft_to_activate(self):
        """Test another invalid transition"""
        plan = Mock()
        plan.status = PlanStatus.DRAFT

        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.ACTIVATE,
            user_id="user_001"
        )

        assert success is False
        assert error is not None

    def test_approval_requires_review(self):
        """Test cannot approve draft plan directly"""
        plan = Mock()
        plan.status = PlanStatus.DRAFT

        # Try to approve without going through review
        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.APPROVE,
            user_id="user_001"
        )

        assert success is False
        assert error is not None

    def test_update_dict_includes_timestamp(self):
        """Test all transitions include updated_at timestamp"""
        plan = Mock()
        plan.status = PlanStatus.UNDER_REVIEW

        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.APPROVE,
            user_id="user_001"
        )

        assert "updated_at" in update_dict
        assert isinstance(update_dict["updated_at"], datetime)

    def test_update_dict_includes_user(self):
        """Test all transitions include updated_by user"""
        plan = Mock()
        plan.status = PlanStatus.UNDER_REVIEW

        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.APPROVE,
            user_id="user_123"
        )

        assert update_dict["updated_by"] == "user_123"

    def test_workflow_summary_draft(self):
        """Test workflow summary for draft plan"""
        plan = Mock()
        plan.status = PlanStatus.DRAFT
        plan.submitted_for_review_at = None
        plan.approval_date = None
        plan.approved_by_user_id = None

        summary = get_workflow_summary(plan)

        assert summary["current_status"] == "draft"
        assert summary["can_submit_review"] is True
        assert summary["can_approve"] is False
        assert summary["can_reject"] is False
        assert summary["can_activate"] is False
        assert summary["is_editable"] is True

    def test_workflow_summary_under_review(self):
        """Test workflow summary for plan under review"""
        plan = Mock()
        plan.status = PlanStatus.UNDER_REVIEW
        plan.submitted_for_review_at = datetime.utcnow()
        plan.approval_date = None
        plan.approved_by_user_id = None

        summary = get_workflow_summary(plan)

        assert summary["current_status"] == "under_review"
        assert summary["can_submit_review"] is False
        assert summary["can_approve"] is True
        assert summary["can_reject"] is True
        assert summary["can_activate"] is False
        assert summary["is_editable"] is False

    def test_workflow_summary_approved(self):
        """Test workflow summary for approved plan"""
        plan = Mock()
        plan.status = PlanStatus.APPROVED
        plan.submitted_for_review_at = datetime.utcnow()
        plan.approval_date = datetime.utcnow()
        plan.approved_by_user_id = "approver_001"

        summary = get_workflow_summary(plan)

        assert summary["current_status"] == "approved"
        assert summary["can_submit_review"] is False
        assert summary["can_approve"] is False
        assert summary["can_activate"] is True
        assert summary["can_archive"] is True
        assert summary["is_editable"] is False

    def test_workflow_summary_active(self):
        """Test workflow summary for active plan"""
        plan = Mock()
        plan.status = PlanStatus.ACTIVE
        plan.submitted_for_review_at = datetime.utcnow()
        plan.approval_date = datetime.utcnow()
        plan.approved_by_user_id = "approver_001"
        plan.activated_at = datetime.utcnow()

        summary = get_workflow_summary(plan)

        assert summary["current_status"] == "active"
        assert summary["can_deactivate"] is True
        assert summary["can_archive"] is True
        assert summary["is_editable"] is False

    def test_archived_no_transitions(self):
        """Test archived plan has no available transitions"""
        plan = Mock()
        plan.status = PlanStatus.ARCHIVED

        # Try any action
        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.ACTIVATE,
            user_id="user_001"
        )

        assert success is False
        assert error is not None

    def test_complete_workflow_path(self):
        """Test complete workflow from draft to active"""
        plan = Mock()

        # Start: DRAFT
        plan.status = PlanStatus.DRAFT
        plan.objective = "Test objective"
        plan.scope = "Test scope"
        plan.procedures = [Mock()]

        # Step 1: Submit for review
        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.SUBMIT_FOR_REVIEW,
            user_id="user_001"
        )
        assert success is True
        plan.status = update_dict["status"]

        # Step 2: Approve
        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.APPROVE,
            user_id="approver_001"
        )
        assert success is True
        plan.status = update_dict["status"]

        # Step 3: Activate
        plan.contact_lists = [Mock()]
        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.ACTIVATE,
            user_id="user_001"
        )
        assert success is True
        assert update_dict["status"] == PlanStatus.ACTIVE

    def test_rejection_workflow_path(self):
        """Test rejection and resubmission workflow"""
        plan = Mock()

        # Start: DRAFT → REVIEW
        plan.status = PlanStatus.DRAFT
        plan.objective = "Test objective"
        plan.scope = "Test scope"
        plan.procedures = [Mock()]

        success, _, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.SUBMIT_FOR_REVIEW,
            user_id="user_001"
        )
        assert success is True
        plan.status = update_dict["status"]

        # Reject back to DRAFT
        success, _, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.REJECT,
            user_id="reviewer_001"
        )
        assert success is True
        assert update_dict["status"] == PlanStatus.DRAFT

        # Can resubmit
        success, _, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.SUBMIT_FOR_REVIEW,
            user_id="user_001"
        )
        assert success is True
        assert update_dict["status"] == PlanStatus.UNDER_REVIEW
