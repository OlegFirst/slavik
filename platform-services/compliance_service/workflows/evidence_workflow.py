"""
Evidence Workflow - Управление жизненным циклом свидетельств соответствия

Свидетельство (Evidence) - документальное подтверждение выполнения требования стандарта.

Жизненный цикл:
1. DRAFT - Черновик, создается пользователем
2. SUBMITTED - Отправлено на проверку
3. UNDER_REVIEW - Проверяется compliance officer
4. VERIFIED - Проверено и принято
5. REJECTED - Отклонено (возврат в DRAFT)
6. ARCHIVED - Устаревшее свидетельство

События:
- evidence.created - Создано новое свидетельство
- evidence.submitted - Отправлено на проверку
- evidence.review_started - Начата проверка
- evidence.verified - Верифицировано
- evidence.rejected - Отклонено
- evidence.archived - Архивировано
"""

import logging
from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID

from .base_workflow import BaseWorkflow, WorkflowTransition, WorkflowGuard
from .validators import WorkflowValidator, WorkflowValidationError

logger = logging.getLogger(__name__)


class EvidenceState(str, Enum):
    """Состояния свидетельства"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class EvidenceEvent(str, Enum):
    """События свидетельства"""
    CREATED = "created"
    SUBMITTED = "submitted"
    REVIEW_STARTED = "review_started"
    VERIFIED = "verified"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class EvidenceWorkflow(BaseWorkflow):
    """Воркфлоу управления свидетельствами"""

    def _get_state_enum(self) -> type:
        return EvidenceState

    def _get_event_prefix(self) -> str:
        return "evidence"

    def _define_transitions(self) -> List[WorkflowTransition]:
        """
        Граф переходов состояний:

        DRAFT ─(submit)→ SUBMITTED ─(start_review)→ UNDER_REVIEW ─┬─(verify)→ VERIFIED ─(archive)→ ARCHIVED
          ↑                                                         │
          └─────────────────────(reject)────────────────────────────┘
        """
        return [
            # DRAFT → SUBMITTED
            WorkflowTransition(
                from_state=EvidenceState.DRAFT,
                to_state=EvidenceState.SUBMITTED,
                event_name=EvidenceEvent.SUBMITTED.value,
                required_fields=["submitter_comment"],
                guards=["has_required_documents", "has_valid_requirement"],
                actions=["before_submit_validation", "after_submit_notification"],
                description="Отправка свидетельства на проверку"
            ),

            # SUBMITTED → UNDER_REVIEW
            WorkflowTransition(
                from_state=EvidenceState.SUBMITTED,
                to_state=EvidenceState.UNDER_REVIEW,
                event_name=EvidenceEvent.REVIEW_STARTED.value,
                required_fields=["reviewer_id"],
                guards=["reviewer_has_permission"],
                actions=["after_assign_reviewer"],
                description="Начало проверки свидетельства"
            ),

            # UNDER_REVIEW → VERIFIED
            WorkflowTransition(
                from_state=EvidenceState.UNDER_REVIEW,
                to_state=EvidenceState.VERIFIED,
                event_name=EvidenceEvent.VERIFIED.value,
                required_fields=["verification_comment", "verified_by"],
                guards=["reviewer_is_assigned"],
                actions=[
                    "before_verify_check_completeness",
                    "after_verify_update_requirement_coverage",
                    "after_verify_notify_submitter"
                ],
                description="Верификация свидетельства"
            ),

            # UNDER_REVIEW → REJECTED
            WorkflowTransition(
                from_state=EvidenceState.UNDER_REVIEW,
                to_state=EvidenceState.REJECTED,
                event_name=EvidenceEvent.REJECTED.value,
                required_fields=["rejection_reason", "rejected_by"],
                guards=["reviewer_is_assigned"],
                actions=["after_reject_notify_submitter", "after_reject_create_action_item"],
                description="Отклонение свидетельства"
            ),

            # REJECTED → DRAFT (переработка)
            WorkflowTransition(
                from_state=EvidenceState.REJECTED,
                to_state=EvidenceState.DRAFT,
                event_name="reworked",
                required_fields=[],
                guards=[],
                actions=["after_rework_clear_rejection"],
                description="Возврат на доработку"
            ),

            # VERIFIED → ARCHIVED (устарело)
            WorkflowTransition(
                from_state=EvidenceState.VERIFIED,
                to_state=EvidenceState.ARCHIVED,
                event_name=EvidenceEvent.ARCHIVED.value,
                required_fields=["archive_reason"],
                guards=[],
                actions=[
                    "before_archive_create_snapshot",
                    "after_archive_update_requirement_coverage"
                ],
                description="Архивирование устаревшего свидетельства"
            ),
        ]

    def _define_guards(self) -> Dict[str, WorkflowGuard]:
        """Определение guards - условий для переходов"""
        return {
            "has_required_documents": WorkflowGuard(
                name="has_required_documents",
                check=self._check_has_documents,
                error_message="Свидетельство должно иметь хотя бы один документ"
            ),

            "has_valid_requirement": WorkflowGuard(
                name="has_valid_requirement",
                check=self._check_valid_requirement,
                error_message="Требование не существует или неактивно"
            ),

            "reviewer_has_permission": WorkflowGuard(
                name="reviewer_has_permission",
                check=self._check_reviewer_permission,
                error_message="Пользователь не имеет прав для проверки свидетельств"
            ),

            "reviewer_is_assigned": WorkflowGuard(
                name="reviewer_is_assigned",
                check=self._check_reviewer_assigned,
                error_message="Проверяющий не назначен"
            ),
        }

    def _define_actions(self) -> Dict[str, callable]:
        """Определение actions - действий при переходах"""
        return {
            # Before actions
            "before_submit_validation": self._action_validate_before_submit,
            "before_verify_check_completeness": self._action_check_completeness,
            "before_archive_create_snapshot": self._action_create_snapshot,

            # After actions
            "after_submit_notification": self._action_notify_reviewers,
            "after_assign_reviewer": self._action_assign_reviewer,
            "after_verify_update_requirement_coverage": self._action_update_coverage_verified,
            "after_verify_notify_submitter": self._action_notify_submitter_verified,
            "after_reject_notify_submitter": self._action_notify_submitter_rejected,
            "after_reject_create_action_item": self._action_create_rejection_action,
            "after_rework_clear_rejection": self._action_clear_rejection_data,
            "after_archive_update_requirement_coverage": self._action_update_coverage_archived,
        }

    # =========================================================================
    # Guards Implementation
    # =========================================================================

    async def _check_has_documents(
        self,
        entity_id: str,
        from_state: Enum,
        to_state: Enum,
        actor_id: str,
        metadata: Dict[str, Any],
        repository
    ) -> bool:
        """Проверить, что есть хотя бы один документ"""
        evidence = await repository.get_by_id(entity_id)
        if not evidence:
            logger.warning(f"Evidence {entity_id} not found in _check_has_documents")
            return False
        return bool(evidence.document_id or evidence.document_references)

    async def _check_valid_requirement(
        self,
        entity_id: str,
        from_state: Enum,
        to_state: Enum,
        actor_id: str,
        metadata: Dict[str, Any],
        repository
    ) -> bool:
        """Проверить, что требование существует и активно"""
        evidence = await repository.get_by_id(entity_id)
        if not evidence:
            logger.warning(f"Evidence {entity_id} not found in _check_valid_requirement")
            return False
        requirement = await repository.get_requirement(evidence.requirement_id)
        return requirement is not None and requirement.is_active

    async def _check_reviewer_permission(
        self,
        entity_id: str,
        from_state: Enum,
        to_state: Enum,
        actor_id: str,
        metadata: Dict[str, Any],
        repository
    ) -> bool:
        """Проверить права проверяющего"""
        reviewer_id = metadata.get("reviewer_id")
        # TODO: интеграция с auth service для проверки ролей
        # Временно: проверяем, что reviewer_id не пустой
        return bool(reviewer_id)

    async def _check_reviewer_assigned(
        self,
        entity_id: str,
        from_state: Enum,
        to_state: Enum,
        actor_id: str,
        metadata: Dict[str, Any],
        repository
    ) -> bool:
        """Проверить, что reviewer назначен"""
        evidence = await repository.get_by_id(entity_id)
        if not evidence:
            logger.warning(f"Evidence {entity_id} not found in _check_reviewer_assigned")
            return False
        return bool(evidence.reviewer_id)

    # =========================================================================
    # Actions Implementation
    # =========================================================================

    async def _action_validate_before_submit(
        self,
        entity,
        from_state: Enum,
        to_state: Enum,
        actor_id: str,
        metadata: Dict[str, Any],
        repository
    ):
        """Валидация перед отправкой"""
        logger.info(f"Validating evidence {entity.id} before submit")
        # Дополнительные проверки если нужны

    async def _action_notify_reviewers(
        self,
        entity,
        from_state: Enum,
        to_state: Enum,
        actor_id: str,
        metadata: Dict[str, Any],
        repository
    ):
        """Уведомить проверяющих о новом свидетельстве"""
        logger.info(f"Notifying reviewers about evidence {entity.id}")
        # TODO: интеграция с notification service
        # await notification_service.send(
        #     to=compliance_officers,
        #     subject=f"New evidence submitted: {entity.title}",
        #     body=metadata.get("submitter_comment")
        # )

    async def _action_assign_reviewer(
        self,
        entity,
        from_state: Enum,
        to_state: Enum,
        actor_id: str,
        metadata: Dict[str, Any],
        repository
    ):
        """Назначить проверяющего"""
        reviewer_id = metadata.get("reviewer_id")
        await repository.update_field(entity.id, "reviewer_id", reviewer_id)
        await repository.update_field(entity.id, "review_started_at", datetime.utcnow())
        logger.info(f"Assigned reviewer {reviewer_id} to evidence {entity.id}")

    async def _action_check_completeness(
        self,
        entity,
        from_state: Enum,
        to_state: Enum,
        actor_id: str,
        metadata: Dict[str, Any],
        repository
    ):
        """Проверить полноту свидетельства"""
        logger.info(f"Checking completeness of evidence {entity.id}")
        # Можно добавить AI-анализ полноты

    async def _action_update_coverage_verified(
        self,
        entity,
        from_state: Enum,
        to_state: Enum,
        actor_id: str,
        metadata: Dict[str, Any],
        repository
    ):
        """Обновить покрытие требования после верификации"""
        logger.info(f"Updating requirement coverage for verified evidence {entity.id}")
        await repository.update_requirement_coverage(
            requirement_id=entity.requirement_id,
            evidence_id=entity.id,
            action="add"
        )

    async def _action_notify_submitter_verified(
        self,
        entity,
        from_state: Enum,
        to_state: Enum,
        actor_id: str,
        metadata: Dict[str, Any],
        repository
    ):
        """Уведомить автора о верификации"""
        logger.info(f"Notifying submitter about verified evidence {entity.id}")
        # TODO: notification service

    async def _action_notify_submitter_rejected(
        self,
        entity,
        from_state: Enum,
        to_state: Enum,
        actor_id: str,
        metadata: Dict[str, Any],
        repository
    ):
        """Уведомить автора об отклонении"""
        logger.info(f"Notifying submitter about rejected evidence {entity.id}")
        # TODO: notification service

    async def _action_create_rejection_action(
        self,
        entity,
        from_state: Enum,
        to_state: Enum,
        actor_id: str,
        metadata: Dict[str, Any],
        repository
    ):
        """Создать action item для исправления"""
        logger.info(f"Creating action item for rejected evidence {entity.id}")
        # TODO: создать задачу в gap workflow

    async def _action_clear_rejection_data(
        self,
        entity,
        from_state: Enum,
        to_state: Enum,
        actor_id: str,
        metadata: Dict[str, Any],
        repository
    ):
        """Очистить данные об отклонении при возврате в DRAFT"""
        await repository.update_field(entity.id, "rejection_reason", None)
        await repository.update_field(entity.id, "rejected_by", None)
        await repository.update_field(entity.id, "rejected_at", None)
        logger.info(f"Cleared rejection data for evidence {entity.id}")

    async def _action_create_snapshot(
        self,
        entity,
        from_state: Enum,
        to_state: Enum,
        actor_id: str,
        metadata: Dict[str, Any],
        repository
    ):
        """Создать snapshot перед архивированием"""
        logger.info(f"Creating snapshot for evidence {entity.id}")
        # TODO: сохранить snapshot в отдельную таблицу

    async def _action_update_coverage_archived(
        self,
        entity,
        from_state: Enum,
        to_state: Enum,
        actor_id: str,
        metadata: Dict[str, Any],
        repository
    ):
        """Обновить покрытие требования после архивации"""
        logger.info(f"Updating requirement coverage for archived evidence {entity.id}")
        await repository.update_requirement_coverage(
            requirement_id=entity.requirement_id,
            evidence_id=entity.id,
            action="remove"
        )

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
        evidence = await self.repository.get_by_id(entity_id)

        if not evidence:
            raise WorkflowValidationError(f"Evidence {entity_id} not found")

        # 1. Terminal state check
        terminal_states = ["archived"]
        WorkflowValidator.validate_terminal_state(
            evidence.status,
            terminal_states
        )

        # 2. Transition-specific validation
        if to_state == EvidenceState.SUBMITTED.value or from_state == EvidenceState.DRAFT.value and to_state == EvidenceState.SUBMITTED.value:
            # Require document or reference
            if not evidence.document_id and not evidence.document_reference:
                raise WorkflowValidationError(
                    "Cannot submit evidence without document_id or document_reference"
                )

            # Validate title
            WorkflowValidator.validate_required_field(
                evidence.title,
                "title",
                for_transition="submit"
            )

            # Validate requirement exists
            if evidence.requirement_id:
                # Validate requirement reference (basic check)
                WorkflowValidator.validate_required_field(
                    evidence.requirement_id,
                    "requirement_id",
                    for_transition="submit"
                )

        elif to_state == EvidenceState.VERIFIED.value:
            # Require reviewer
            reviewer_id = metadata.get("verified_by") or evidence.reviewer_id
            WorkflowValidator.validate_required_field(
                reviewer_id,
                "reviewer_id",
                for_transition="verify"
            )

            # Validate dates
            if evidence.validity_period_start and evidence.validity_period_end:
                WorkflowValidator.validate_date_sequence(
                    evidence.validity_period_start,
                    evidence.validity_period_end,
                    ("validity_period_start", "validity_period_end")
                )

            # Ensure validity period doesn't start in the past for new evidence
            if evidence.validity_period_start:
                # Allow some tolerance for backdating (e.g., 30 days)
                past_tolerance = datetime.utcnow() - timedelta(days=30)
                if evidence.validity_period_start < past_tolerance:
                    raise WorkflowValidationError(
                        f"validity_period_start cannot be more than 30 days in the past"
                    )

        elif to_state == EvidenceState.REJECTED.value:
            # Require rejection reason from metadata
            rejection_reason = metadata.get("rejection_reason")
            WorkflowValidator.validate_required_field(
                rejection_reason,
                "rejection_reason",
                for_transition="reject"
            )

        elif to_state == EvidenceState.ARCHIVED.value:
            # Require archive reason
            archive_reason = metadata.get("archive_reason")
            WorkflowValidator.validate_required_field(
                archive_reason,
                "archive_reason",
                for_transition="archive"
            )

            # Can only archive from VERIFIED state
            if evidence.status != EvidenceState.VERIFIED.value:
                raise WorkflowValidationError(
                    f"Cannot archive evidence from state '{evidence.status}'. "
                    f"Must be in VERIFIED state."
                )

    # =========================================================================
    # Helper Methods
    # =========================================================================

    async def initialize_evidence(
        self,
        evidence_data: Dict[str, Any],
        tenant_id: str,
        creator_id: str
    ) -> Dict[str, Any]:
        """
        Создать новое свидетельство в состоянии DRAFT

        Args:
            evidence_data: Данные свидетельства
            tenant_id: ID тенанта
            creator_id: ID создателя

        Returns:
            Созданное свидетельство
        """
        evidence_data.update({
            "status": EvidenceState.DRAFT.value,
            "tenant_id": tenant_id,
            "created_by": creator_id,
            "created_at": datetime.utcnow()
        })

        evidence = await self.repository.create(evidence_data)

        # Публикация события создания
        if self.eventbus:
            await self.eventbus.publish({
                "event_type": f"bcm.compliance.evidence.{EvidenceEvent.CREATED.value}",
                "tenant_id": tenant_id,
                "entity_id": evidence.id,
                "actor_id": creator_id,
                "metadata": {"requirement_id": evidence_data.get("requirement_id")},
                "timestamp": datetime.utcnow().isoformat()
            })

        logger.info(f"Created evidence {evidence.id} in DRAFT state")
        return evidence

    async def get_workflow_status(self, evidence_id: str) -> Dict[str, Any]:
        """
        Получить текущий статус воркфлоу для свидетельства

        Returns:
            Dict с информацией о текущем состоянии и доступных переходах
        """
        evidence = await self.repository.get_by_id(evidence_id)
        if not evidence:
            raise ValueError(f"Evidence {evidence_id} not found")

        current_state = EvidenceState(evidence.status)
        available_transitions = self.get_available_transitions(current_state)

        return {
            "evidence_id": evidence_id,
            "current_state": current_state.value,
            "available_transitions": available_transitions,
            "reviewer_id": evidence.reviewer_id,
            "verification_status": {
                "verified_at": evidence.verified_at.isoformat() if evidence.verified_at else None,
                "verified_by": evidence.verified_by,
            },
            "metadata": {
                "created_at": evidence.created_at.isoformat(),
                "updated_at": evidence.updated_at.isoformat(),
                "requirement_id": evidence.requirement_id,
            }
        }
