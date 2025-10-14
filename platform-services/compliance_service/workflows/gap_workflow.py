"""
Gap Workflow - Управление пробелами в соответствии

Gap (Пробел) - выявленное несоответствие требованию, требующее исправления.

Жизненный цикл:
1. IDENTIFIED - Пробел выявлен (из assessment)
2. PLANNED - Запланированы действия по устранению
3. IN_PROGRESS - Выполняется устранение
4. RESOLVED - Устранен, ждет проверки
5. VERIFIED - Проверен и закрыт
6. ACCEPTED_RISK - Принят риск (не устраняется)

События:
- gap.identified
- gap.planned
- gap.progress_updated
- gap.resolved
- gap.verified
- gap.risk_accepted
"""

import logging
from enum import Enum
from typing import Dict, List, Any
from datetime import datetime
from uuid import UUID

from .base_workflow import BaseWorkflow, WorkflowTransition, WorkflowGuard
from .validators import WorkflowValidator, WorkflowValidationError

logger = logging.getLogger(__name__)


class GapState(str, Enum):
    """Состояния пробела"""
    IDENTIFIED = "identified"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    VERIFIED = "verified"
    ACCEPTED_RISK = "accepted_risk"


class GapEvent(str, Enum):
    """События пробела"""
    IDENTIFIED = "identified"
    PLANNED = "planned"
    STARTED = "started"
    RESOLVED = "resolved"
    VERIFIED = "verified"
    RISK_ACCEPTED = "risk_accepted"


class GapWorkflow(BaseWorkflow):
    """Воркфлоу управления пробелами"""

    def _get_state_enum(self) -> type:
        return GapState

    def _get_event_prefix(self) -> str:
        return "gap"

    def _define_transitions(self) -> List[WorkflowTransition]:
        """
        Граф переходов:

        IDENTIFIED ─(plan)→ PLANNED ─(start)→ IN_PROGRESS ─(resolve)→ RESOLVED ─(verify)→ VERIFIED
             │
             └───────────────(accept_risk)──────────────────────────────────────→ ACCEPTED_RISK
        """
        return [
            # IDENTIFIED → PLANNED
            WorkflowTransition(
                from_state=GapState.IDENTIFIED,
                to_state=GapState.PLANNED,
                event_name=GapEvent.PLANNED.value,
                required_fields=["remediation_actions", "assigned_to", "due_date"],
                guards=["has_valid_actions", "assignee_exists"],
                actions=[
                    "before_plan_prioritize_gap",
                    "after_plan_notify_assignee",
                    "after_plan_create_tasks"
                ],
                description="Планирование устранения пробела"
            ),

            # PLANNED → IN_PROGRESS
            WorkflowTransition(
                from_state=GapState.PLANNED,
                to_state=GapState.IN_PROGRESS,
                event_name=GapEvent.STARTED.value,
                required_fields=["started_by"],
                guards=["assignee_acknowledged"],
                actions=["after_start_track_progress"],
                description="Начало работы по устранению"
            ),

            # IN_PROGRESS → RESOLVED
            WorkflowTransition(
                from_state=GapState.IN_PROGRESS,
                to_state=GapState.RESOLVED,
                event_name=GapEvent.RESOLVED.value,
                required_fields=["resolution_description", "resolved_by", "evidence_id"],
                guards=["has_evidence", "actions_completed"],
                actions=[
                    "before_resolve_validate_evidence",
                    "after_resolve_request_verification"
                ],
                description="Пробел устранен"
            ),

            # RESOLVED → VERIFIED
            WorkflowTransition(
                from_state=GapState.RESOLVED,
                to_state=GapState.VERIFIED,
                event_name=GapEvent.VERIFIED.value,
                required_fields=["verification_comment", "verified_by"],
                guards=["verifier_has_permission", "evidence_valid"],
                actions=[
                    "before_verify_check_effectiveness",
                    "after_verify_update_requirement_coverage",
                    "after_verify_update_assessment",
                    "after_verify_notify_stakeholders"
                ],
                description="Устранение подтверждено"
            ),

            # IDENTIFIED → ACCEPTED_RISK
            WorkflowTransition(
                from_state=GapState.IDENTIFIED,
                to_state=GapState.ACCEPTED_RISK,
                event_name=GapEvent.RISK_ACCEPTED.value,
                required_fields=["risk_acceptance_justification", "accepted_by", "risk_owner"],
                guards=["has_management_approval"],
                actions=[
                    "before_accept_document_risk",
                    "after_accept_notify_stakeholders"
                ],
                description="Принятие риска (не устраняется)"
            ),
        ]

    def _define_guards(self) -> Dict[str, WorkflowGuard]:
        return {
            "has_valid_actions": WorkflowGuard(
                name="has_valid_actions",
                check=self._check_valid_actions,
                error_message="Remediation actions должны быть конкретными и выполнимыми"
            ),

            "assignee_exists": WorkflowGuard(
                name="assignee_exists",
                check=self._check_assignee_exists,
                error_message="Назначенный пользователь не существует"
            ),

            "assignee_acknowledged": WorkflowGuard(
                name="assignee_acknowledged",
                check=self._check_assignee_acknowledged,
                error_message="Assignee должен подтвердить начало работы"
            ),

            "has_evidence": WorkflowGuard(
                name="has_evidence",
                check=self._check_has_evidence,
                error_message="Требуется свидетельство устранения"
            ),

            "actions_completed": WorkflowGuard(
                name="actions_completed",
                check=self._check_actions_completed,
                error_message="Не все remediation actions выполнены"
            ),

            "verifier_has_permission": WorkflowGuard(
                name="verifier_has_permission",
                check=self._check_verifier_permission,
                error_message="Верификатор должен иметь соответствующие права"
            ),

            "evidence_valid": WorkflowGuard(
                name="evidence_valid",
                check=self._check_evidence_valid,
                error_message="Предоставленное свидетельство недостаточно"
            ),

            "has_management_approval": WorkflowGuard(
                name="has_management_approval",
                check=self._check_management_approval,
                error_message="Требуется одобрение руководства для принятия риска"
            ),
        }

    def _define_actions(self) -> Dict[str, callable]:
        return {
            # Before actions
            "before_plan_prioritize_gap": self._action_prioritize_gap,
            "before_resolve_validate_evidence": self._action_validate_evidence,
            "before_verify_check_effectiveness": self._action_check_effectiveness,
            "before_accept_document_risk": self._action_document_risk_acceptance,

            # After actions
            "after_plan_notify_assignee": self._action_notify_assignee,
            "after_plan_create_tasks": self._action_create_remediation_tasks,
            "after_start_track_progress": self._action_track_progress,
            "after_resolve_request_verification": self._action_request_verification,
            "after_verify_update_requirement_coverage": self._action_update_coverage,
            "after_verify_update_assessment": self._action_update_assessment_score,
            "after_verify_notify_stakeholders": self._action_notify_verified,
            "after_accept_notify_stakeholders": self._action_notify_risk_accepted,
        }

    # =========================================================================
    # Guards
    # =========================================================================

    async def _check_valid_actions(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить корректность remediation actions"""
        actions = metadata.get("remediation_actions", [])
        return len(actions) > 0 and all(
            action.get("description") and action.get("responsible")
            for action in actions
        )

    async def _check_assignee_exists(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить существование assignee"""
        # TODO: проверка через user service
        return bool(metadata.get("assigned_to"))

    async def _check_assignee_acknowledged(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить подтверждение assignee"""
        gap = await repository.get_by_id(entity_id)
        if not gap:
            logger.warning(f"Gap {entity_id} not found in _check_assignee_acknowledged")
            return False
        started_by = metadata.get("started_by")
        return gap.assigned_to == started_by

    async def _check_has_evidence(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить наличие свидетельства"""
        return bool(metadata.get("evidence_id"))

    async def _check_actions_completed(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить завершение всех actions"""
        gap = await repository.get_by_id(entity_id)
        if not gap:
            logger.warning(f"Gap {entity_id} not found in _check_actions_completed")
            return False
        actions = gap.remediation_actions
        return all(action.get("status") == "completed" for action in actions)

    async def _check_verifier_permission(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить права верификатора"""
        # TODO: проверка через auth service
        return bool(metadata.get("verified_by"))

    async def _check_evidence_valid(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить валидность свидетельства"""
        evidence_id = metadata.get("evidence_id")
        # TODO: проверить статус evidence через evidence workflow
        return bool(evidence_id)

    async def _check_management_approval(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить одобрение руководства"""
        # TODO: проверка роли approved_by (должен быть руководитель)
        return bool(metadata.get("accepted_by") and metadata.get("risk_owner"))

    # =========================================================================
    # Actions
    # =========================================================================

    async def _action_prioritize_gap(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Приоритизация пробела"""
        logger.info(f"Prioritizing gap {entity.id}")
        # AI может помочь с приоритизацией

    async def _action_notify_assignee(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Уведомить assignee"""
        logger.info(f"Notifying assignee for gap {entity.id}")

    async def _action_create_remediation_tasks(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Создать задачи для remediation"""
        logger.info(f"Creating remediation tasks for gap {entity.id}")

    async def _action_track_progress(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Начать отслеживание прогресса"""
        logger.info(f"Started tracking progress for gap {entity.id}")

    async def _action_validate_evidence(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Валидация свидетельства"""
        logger.info(f"Validating evidence for gap {entity.id}")

    async def _action_request_verification(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Запросить верификацию"""
        logger.info(f"Requesting verification for gap {entity.id}")

    async def _action_check_effectiveness(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Проверка эффективности устранения"""
        logger.info(f"Checking effectiveness for gap {entity.id}")

    async def _action_update_coverage(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Обновить покрытие требования"""
        logger.info(f"Updating requirement coverage after gap verification {entity.id}")

    async def _action_update_assessment_score(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Обновить compliance score в assessment"""
        logger.info(f"Updating assessment score after gap resolution {entity.id}")

    async def _action_notify_verified(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Уведомить о верификации"""
        logger.info(f"Notifying stakeholders about verified gap {entity.id}")

    async def _action_document_risk_acceptance(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Документировать принятие риска"""
        logger.info(f"Documenting risk acceptance for gap {entity.id}")

    async def _action_notify_risk_accepted(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Уведомить о принятии риска"""
        logger.info(f"Notifying stakeholders about risk acceptance for gap {entity.id}")

    # =========================================================================
    # Edge Case Validation
    # =========================================================================

    async def validate_transition_edge_cases(
        self,
        entity_id: str,
        from_state: str,
        to_state: str,
        metadata: Dict[str, Any]
    ):
        """
        Validate edge cases before state transition

        Raises:
            WorkflowValidationError: If validation fails
        """
        gap = await self.repository.get_by_id(entity_id)

        if not gap:
            raise WorkflowValidationError(f"Gap {entity_id} not found")

        # 1. Terminal state check
        terminal_states = ["verified", "accepted_risk"]
        WorkflowValidator.validate_terminal_state(
            gap.status,
            terminal_states
        )

        # 2. Transition-specific validation
        if to_state == GapState.PLANNED.value:
            # Require assigned_to
            assigned_to = metadata.get("assigned_to")
            WorkflowValidator.validate_required_field(
                assigned_to,
                "assigned_to",
                for_transition="plan"
            )

            # Require due_date
            due_date = metadata.get("due_date")
            WorkflowValidator.validate_required_field(
                due_date,
                "due_date",
                for_transition="plan"
            )

            # Due date must be in future
            if due_date:
                if isinstance(due_date, str):
                    due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                WorkflowValidator.validate_past_date(due_date, "due_date")

            # Validate remediation actions
            remediation_actions = metadata.get("remediation_actions", [])
            WorkflowValidator.validate_required_list(
                remediation_actions,
                "remediation_actions",
                for_transition="plan",
                min_items=1
            )

            # Validate each action has required fields
            WorkflowValidator.validate_list_items_have_fields(
                remediation_actions,
                ["description", "responsible"],
                "Remediation action"
            )

        elif to_state == GapState.RESOLVED.value:
            # Require resolution description
            resolution_description = metadata.get("resolution_description")
            WorkflowValidator.validate_required_field(
                resolution_description,
                "resolution_description",
                for_transition="resolve"
            )

            # Require evidence
            evidence_id = metadata.get("evidence_id")
            WorkflowValidator.validate_required_field(
                evidence_id,
                "evidence_id",
                for_transition="resolve"
            )

            # Prevent circular gap → evidence → gap references
            if evidence_id and hasattr(gap, 'id'):
                # Check if this creates a circular reference
                # (This would need evidence repository to fully validate)
                pass

        elif to_state == GapState.ACCEPTED_RISK.value:
            # Require risk acceptance justification
            justification = metadata.get("risk_acceptance_justification")
            WorkflowValidator.validate_required_field(
                justification,
                "risk_acceptance_justification",
                for_transition="accept_risk"
            )

            # Require risk owner
            risk_owner = metadata.get("risk_owner")
            WorkflowValidator.validate_required_field(
                risk_owner,
                "risk_owner",
                for_transition="accept_risk"
            )

            # Require accepted_by (management approval)
            accepted_by = metadata.get("accepted_by")
            WorkflowValidator.validate_required_field(
                accepted_by,
                "accepted_by",
                for_transition="accept_risk"
            )

        elif to_state == GapState.VERIFIED.value:
            # Require verification comment
            verification_comment = metadata.get("verification_comment")
            WorkflowValidator.validate_required_field(
                verification_comment,
                "verification_comment",
                for_transition="verify"
            )

            # Require verified_by
            verified_by = metadata.get("verified_by")
            WorkflowValidator.validate_required_field(
                verified_by,
                "verified_by",
                for_transition="verify"
            )
