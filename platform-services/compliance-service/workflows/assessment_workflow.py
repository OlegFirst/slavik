"""
Assessment Workflow - Управление оценками соответствия

Оценка (Assessment) - периодическая проверка соответствия требованиям стандарта.

Жизненный цикл:
1. PLANNED - Запланирована оценка
2. IN_PROGRESS - Оценка выполняется
3. REVIEW - Результаты на проверке
4. COMPLETED - Завершена успешно
5. CANCELLED - Отменена

Типы оценок:
- REGULAR - Регулярная внутренняя оценка
- SELF - Самооценка
- PRE_AUDIT - Подготовка к аудиту
- POST_INCIDENT - После инцидента

События:
- assessment.planned
- assessment.started
- assessment.evidence_analyzed
- assessment.gap_identified
- assessment.review_requested
- assessment.completed
- assessment.cancelled
"""

import logging
from enum import Enum
from typing import Dict, List, Any
from datetime import datetime
from uuid import UUID

from .base_workflow import BaseWorkflow, WorkflowTransition, WorkflowGuard
from .validators import WorkflowValidator, WorkflowValidationError
from compliance.models.enums import AssessmentType

logger = logging.getLogger(__name__)


class AssessmentState(str, Enum):
    """Состояния оценки"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AssessmentEvent(str, Enum):
    """События оценки"""
    PLANNED = "planned"
    STARTED = "started"
    REVIEW_REQUESTED = "review_requested"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AssessmentWorkflow(BaseWorkflow):
    """Воркфлоу управления оценками соответствия"""

    def _get_state_enum(self) -> type:
        return AssessmentState

    def _get_event_prefix(self) -> str:
        return "assessment"

    def _define_transitions(self) -> List[WorkflowTransition]:
        """
        Граф переходов:

        PLANNED ─(start)→ IN_PROGRESS ─(request_review)→ REVIEW ─(complete)→ COMPLETED
           │
           └─────────────────(cancel)──────────────────────────────→ CANCELLED
        """
        return [
            # PLANNED → IN_PROGRESS
            WorkflowTransition(
                from_state=AssessmentState.PLANNED,
                to_state=AssessmentState.IN_PROGRESS,
                event_name=AssessmentEvent.STARTED.value,
                required_fields=["assessor_id", "start_date"],
                guards=["has_valid_scope", "assessor_assigned"],
                actions=[
                    "before_start_validate_prerequisites",
                    "after_start_create_assessment_tasks",
                    "after_start_notify_stakeholders"
                ],
                description="Начало выполнения оценки"
            ),

            # IN_PROGRESS → REVIEW
            WorkflowTransition(
                from_state=AssessmentState.IN_PROGRESS,
                to_state=AssessmentState.REVIEW,
                event_name=AssessmentEvent.REVIEW_REQUESTED.value,
                required_fields=["reviewer_id", "preliminary_results"],
                guards=["all_requirements_assessed", "gaps_documented"],
                actions=[
                    "before_review_calculate_scores",
                    "before_review_generate_report",
                    "after_review_notify_reviewer"
                ],
                description="Отправка результатов на проверку"
            ),

            # REVIEW → COMPLETED
            WorkflowTransition(
                from_state=AssessmentState.REVIEW,
                to_state=AssessmentState.COMPLETED,
                event_name=AssessmentEvent.COMPLETED.value,
                required_fields=["approval_comment", "approved_by"],
                guards=["reviewer_approved"],
                actions=[
                    "before_complete_finalize_report",
                    "after_complete_create_gaps",
                    "after_complete_update_compliance_dashboard",
                    "after_complete_notify_stakeholders"
                ],
                description="Завершение оценки"
            ),

            # PLANNED → CANCELLED
            WorkflowTransition(
                from_state=AssessmentState.PLANNED,
                to_state=AssessmentState.CANCELLED,
                event_name=AssessmentEvent.CANCELLED.value,
                required_fields=["cancellation_reason"],
                guards=[],
                actions=["after_cancel_notify_stakeholders"],
                description="Отмена запланированной оценки"
            ),

            # IN_PROGRESS → CANCELLED
            WorkflowTransition(
                from_state=AssessmentState.IN_PROGRESS,
                to_state=AssessmentState.CANCELLED,
                event_name=AssessmentEvent.CANCELLED.value,
                required_fields=["cancellation_reason"],
                guards=[],
                actions=["after_cancel_cleanup_tasks", "after_cancel_notify_stakeholders"],
                description="Отмена выполняющейся оценки"
            ),
        ]

    def _define_guards(self) -> Dict[str, WorkflowGuard]:
        return {
            "has_valid_scope": WorkflowGuard(
                name="has_valid_scope",
                check=self._check_valid_scope,
                error_message="Scope оценки не определен или некорректен"
            ),

            "assessor_assigned": WorkflowGuard(
                name="assessor_assigned",
                check=self._check_assessor_assigned,
                error_message="Assessor не назначен"
            ),

            "all_requirements_assessed": WorkflowGuard(
                name="all_requirements_assessed",
                check=self._check_all_requirements_assessed,
                error_message="Не все требования в scope оценены"
            ),

            "gaps_documented": WorkflowGuard(
                name="gaps_documented",
                check=self._check_gaps_documented,
                error_message="Обнаруженные пробелы должны быть задокументированы"
            ),

            "reviewer_approved": WorkflowGuard(
                name="reviewer_approved",
                check=self._check_reviewer_approved,
                error_message="Reviewer должен одобрить результаты"
            ),
        }

    def _define_actions(self) -> Dict[str, callable]:
        return {
            # Before actions
            "before_start_validate_prerequisites": self._action_validate_prerequisites,
            "before_review_calculate_scores": self._action_calculate_scores,
            "before_review_generate_report": self._action_generate_report,
            "before_complete_finalize_report": self._action_finalize_report,

            # After actions
            "after_start_create_assessment_tasks": self._action_create_tasks,
            "after_start_notify_stakeholders": self._action_notify_start,
            "after_review_notify_reviewer": self._action_notify_reviewer,
            "after_complete_create_gaps": self._action_create_gap_records,
            "after_complete_update_compliance_dashboard": self._action_update_dashboard,
            "after_complete_notify_stakeholders": self._action_notify_completion,
            "after_cancel_cleanup_tasks": self._action_cleanup_tasks,
            "after_cancel_notify_stakeholders": self._action_notify_cancellation,
        }

    # =========================================================================
    # Guards
    # =========================================================================

    async def _check_valid_scope(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить корректность scope"""
        assessment = await repository.get_by_id(entity_id)
        if not assessment:
            logger.warning(f"Assessment {entity_id} not found in _check_valid_scope")
            return False
        return bool(assessment.standard and assessment.scope_clauses)

    async def _check_assessor_assigned(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить назначение assessor"""
        return bool(metadata.get("assessor_id"))

    async def _check_all_requirements_assessed(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить, что все требования оценены"""
        assessment = await repository.get_by_id(entity_id)
        if not assessment:
            logger.warning(f"Assessment {entity_id} not found in _check_all_requirements_assessed")
            return False
        # Получить все требования в scope
        requirements = await repository.get_requirements_in_scope(assessment.id)
        # Проверить, что для каждого есть результат
        assessed = await repository.get_assessed_requirements(assessment.id)
        return len(requirements) == len(assessed)

    async def _check_gaps_documented(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить документирование пробелов"""
        # Если есть несоответствия, они должны быть документированы
        assessment = await repository.get_by_id(entity_id)
        if not assessment:
            logger.warning(f"Assessment {entity_id} not found in _check_gaps_documented")
            return False
        if assessment.overall_score < 70:  # Порог compliance
            gaps = await repository.get_gaps_for_assessment(assessment.id)
            return len(gaps) > 0
        return True

    async def _check_reviewer_approved(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить одобрение reviewer"""
        return "approved_by" in metadata and metadata.get("approved_by")

    # =========================================================================
    # Actions
    # =========================================================================

    async def _action_validate_prerequisites(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Валидация prerequisites перед началом"""
        logger.info(f"Validating prerequisites for assessment {entity.id}")

    async def _action_create_tasks(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Создать задачи для оценки"""
        logger.info(f"Creating assessment tasks for {entity.id}")
        # Создать задачи для каждого требования в scope

    async def _action_notify_start(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Уведомить о начале оценки"""
        logger.info(f"Notifying stakeholders about assessment start {entity.id}")

    async def _action_calculate_scores(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Рассчитать compliance scores"""
        logger.info(f"Calculating compliance scores for {entity.id}")
        # Вызвать assessment_engine для расчета

    async def _action_generate_report(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Сгенерировать предварительный отчет"""
        logger.info(f"Generating preliminary report for {entity.id}")

    async def _action_notify_reviewer(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Уведомить reviewer"""
        logger.info(f"Notifying reviewer for {entity.id}")

    async def _action_finalize_report(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Финализировать отчет"""
        logger.info(f"Finalizing report for {entity.id}")

    async def _action_create_gap_records(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Создать записи о пробелах в gap workflow"""
        logger.info(f"Creating gap records for {entity.id}")
        # Получить gaps из результатов и создать через gap_workflow

    async def _action_update_dashboard(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Обновить compliance dashboard"""
        logger.info(f"Updating compliance dashboard with results from {entity.id}")

    async def _action_notify_completion(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Уведомить о завершении"""
        logger.info(f"Notifying stakeholders about completion of {entity.id}")

    async def _action_cleanup_tasks(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Очистить незавершенные задачи"""
        logger.info(f"Cleaning up tasks for cancelled assessment {entity.id}")

    async def _action_notify_cancellation(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Уведомить об отмене"""
        logger.info(f"Notifying stakeholders about cancellation of {entity.id}")

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
        assessment = await self.repository.get_by_id(entity_id)

        if not assessment:
            raise WorkflowValidationError(f"Assessment {entity_id} not found")

        # 1. Terminal state check
        terminal_states = ["completed", "cancelled"]
        WorkflowValidator.validate_terminal_state(
            assessment.status,
            terminal_states
        )

        # 2. Transition-specific validation
        if to_state == AssessmentState.IN_PROGRESS.value:
            # Require assessor
            assessor_id = metadata.get("assessor_id")
            WorkflowValidator.validate_required_field(
                assessor_id,
                "assessor_id",
                for_transition="start"
            )

            # Require start_date
            start_date = metadata.get("start_date")
            WorkflowValidator.validate_required_field(
                start_date,
                "start_date",
                for_transition="start"
            )

            # Validate scope_clauses not empty
            if hasattr(assessment, 'scope_clauses'):
                WorkflowValidator.validate_required_list(
                    assessment.scope_clauses,
                    "scope_clauses",
                    for_transition="start",
                    min_items=1
                )

            # Validate standard is set
            if hasattr(assessment, 'standard'):
                WorkflowValidator.validate_required_field(
                    assessment.standard,
                    "standard",
                    for_transition="start"
                )

        elif to_state == AssessmentState.REVIEW.value:
            # Require reviewer
            reviewer_id = metadata.get("reviewer_id")
            WorkflowValidator.validate_required_field(
                reviewer_id,
                "reviewer_id",
                for_transition="request_review"
            )

            # Require preliminary_results
            preliminary_results = metadata.get("preliminary_results")
            WorkflowValidator.validate_required_field(
                preliminary_results,
                "preliminary_results",
                for_transition="request_review"
            )

        elif to_state == AssessmentState.COMPLETED.value:
            # Require approval
            approved_by = metadata.get("approved_by")
            WorkflowValidator.validate_required_field(
                approved_by,
                "approved_by",
                for_transition="complete"
            )

            # Require approval comment
            approval_comment = metadata.get("approval_comment")
            WorkflowValidator.validate_required_field(
                approval_comment,
                "approval_comment",
                for_transition="complete"
            )

            # Check completion_date is after start_date
            if hasattr(assessment, 'start_date') and assessment.start_date:
                completion_date = metadata.get("completion_date") or datetime.utcnow()
                if isinstance(completion_date, str):
                    completion_date = datetime.fromisoformat(completion_date.replace('Z', '+00:00'))
                WorkflowValidator.validate_date_sequence(
                    assessment.start_date,
                    completion_date,
                    ("start_date", "completion_date")
                )

        elif to_state == AssessmentState.CANCELLED.value:
            # Require cancellation reason
            cancellation_reason = metadata.get("cancellation_reason")
            WorkflowValidator.validate_required_field(
                cancellation_reason,
                "cancellation_reason",
                for_transition="cancel"
            )
