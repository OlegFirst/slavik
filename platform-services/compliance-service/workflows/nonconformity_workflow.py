"""
Nonconformity Workflow - Управление несоответствиями (NC)

Несоответствие (Nonconformity) - невыполнение требования (ISO 22301 Clause 10.1).

Критическое отличие от Gap:
- Gap: выявлен недостаток, можно устранить просто
- NC: серьезное несоответствие, требует Root Cause Analysis

Типы NC:
- MAJOR: отсутствие или полный сбой процесса BCMS
- MINOR: изолированный лапсус в соответствии
- OBSERVATION: потенциал для улучшения

Жизненный цикл (ISO 22301 требует):
1. OPEN - Несоответствие зафиксировано
2. ROOT_CAUSE_ANALYSIS - Анализ первопричин (обязательно!)
3. CORRECTIVE_ACTION - Выполнение корректирующих действий
4. VERIFICATION - Проверка эффективности (обязательно!)
5. CLOSED - Закрыто (причина устранена)

События:
- nc.created
- nc.rca_started
- nc.rca_completed
- nc.action_planned
- nc.action_in_progress
- nc.verification_requested
- nc.verified
- nc.closed
"""

import logging
from enum import Enum
from typing import Dict, List, Any
from datetime import datetime
from uuid import UUID

from .base_workflow import BaseWorkflow, WorkflowTransition, WorkflowGuard
from .validators import WorkflowValidator, WorkflowValidationError
from compliance.models.enums import NCType, NCSource, RCAMethod
from compliance.services.rca_templates import RCATemplateFactory, RCAAnalyzer

logger = logging.getLogger(__name__)


class NCState(str, Enum):
    """Состояния несоответствия"""
    OPEN = "open"
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"
    CORRECTIVE_ACTION = "corrective_action"
    VERIFICATION = "verification"
    CLOSED = "closed"


class NCEvent(str, Enum):
    """События NC"""
    CREATED = "created"
    RCA_STARTED = "rca_started"
    RCA_COMPLETED = "rca_completed"
    ACTION_PLANNED = "action_planned"
    VERIFICATION_REQUESTED = "verification_requested"
    VERIFIED = "verified"
    CLOSED = "closed"


class NonconformityWorkflow(BaseWorkflow):
    """Воркфлоу управления несоответствиями (ISO 22301 Clause 10.1)"""

    def _get_state_enum(self) -> type:
        return NCState

    def _get_event_prefix(self) -> str:
        return "nonconformity"

    def _define_transitions(self) -> List[WorkflowTransition]:
        """
        Граф переходов (строго по ISO 22301):

        OPEN ─(start_rca)→ ROOT_CAUSE_ANALYSIS ─(complete_rca)→ CORRECTIVE_ACTION ─(request_verification)→ VERIFICATION ─(verify)→ CLOSED
        """
        return [
            # OPEN → ROOT_CAUSE_ANALYSIS
            WorkflowTransition(
                from_state=NCState.OPEN,
                to_state=NCState.ROOT_CAUSE_ANALYSIS,
                event_name=NCEvent.RCA_STARTED.value,
                required_fields=["rca_lead", "rca_team", "rca_method"],
                guards=["rca_lead_qualified"],
                actions=[
                    "before_rca_prepare_data",
                    "after_rca_create_investigation_tasks",
                    "after_rca_notify_team"
                ],
                description="Начало анализа первопричин (RCA)"
            ),

            # ROOT_CAUSE_ANALYSIS → CORRECTIVE_ACTION
            WorkflowTransition(
                from_state=NCState.ROOT_CAUSE_ANALYSIS,
                to_state=NCState.CORRECTIVE_ACTION,
                event_name=NCEvent.RCA_COMPLETED.value,
                required_fields=["root_causes", "corrective_actions"],
                guards=["rca_documented", "actions_address_root_causes"],
                actions=[
                    "before_action_validate_completeness",
                    "after_action_assign_responsibilities",
                    "after_action_set_deadlines",
                    "after_action_notify_owners"
                ],
                description="RCA завершен, начало корректирующих действий"
            ),

            # CORRECTIVE_ACTION → VERIFICATION
            WorkflowTransition(
                from_state=NCState.CORRECTIVE_ACTION,
                to_state=NCState.VERIFICATION,
                event_name=NCEvent.VERIFICATION_REQUESTED.value,
                required_fields=["actions_completed", "evidence_ids"],
                guards=["all_actions_completed", "has_evidence_for_each_action"],
                actions=[
                    "before_verification_prepare_package",
                    "after_verification_assign_verifier",
                    "after_verification_notify_verifier"
                ],
                description="Действия выполнены, запрос верификации"
            ),

            # VERIFICATION → CLOSED
            WorkflowTransition(
                from_state=NCState.VERIFICATION,
                to_state=NCState.CLOSED,
                event_name=NCEvent.VERIFIED.value,
                required_fields=["verification_result", "verified_by", "effectiveness_confirmed"],
                guards=["verifier_qualified", "root_cause_eliminated"],
                actions=[
                    "before_close_final_review",
                    "after_close_update_bcms",
                    "after_close_document_lessons_learned",
                    "after_close_notify_stakeholders"
                ],
                description="Эффективность подтверждена, NC закрыто"
            ),
        ]

    def _define_guards(self) -> Dict[str, WorkflowGuard]:
        return {
            "rca_lead_qualified": WorkflowGuard(
                name="rca_lead_qualified",
                check=self._check_rca_lead_qualified,
                error_message="RCA lead должен иметь квалификацию для проведения анализа"
            ),

            "rca_documented": WorkflowGuard(
                name="rca_documented",
                check=self._check_rca_documented,
                error_message="RCA должен быть полностью задокументирован (5 Whys, Fishbone, etc.)"
            ),

            "actions_address_root_causes": WorkflowGuard(
                name="actions_address_root_causes",
                check=self._check_actions_address_causes,
                error_message="Корректирующие действия должны устранять первопричины, а не симптомы"
            ),

            "all_actions_completed": WorkflowGuard(
                name="all_actions_completed",
                check=self._check_all_actions_completed,
                error_message="Все корректирующие действия должны быть завершены"
            ),

            "has_evidence_for_each_action": WorkflowGuard(
                name="has_evidence_for_each_action",
                check=self._check_evidence_for_actions,
                error_message="Для каждого действия требуется свидетельство выполнения"
            ),

            "verifier_qualified": WorkflowGuard(
                name="verifier_qualified",
                check=self._check_verifier_qualified,
                error_message="Верификатор должен быть квалифицирован и независим"
            ),

            "root_cause_eliminated": WorkflowGuard(
                name="root_cause_eliminated",
                check=self._check_root_cause_eliminated,
                error_message="Верификатор должен подтвердить устранение первопричины"
            ),
        }

    def _define_actions(self) -> Dict[str, callable]:
        return {
            # Before actions - RCA
            "before_rca_prepare_data": self._action_prepare_rca_data,

            # After actions - RCA
            "after_rca_create_investigation_tasks": self._action_create_investigation_tasks,
            "after_rca_notify_team": self._action_notify_rca_team,

            # Before actions - Corrective Action
            "before_action_validate_completeness": self._action_validate_action_plan,

            # After actions - Corrective Action
            "after_action_assign_responsibilities": self._action_assign_action_owners,
            "after_action_set_deadlines": self._action_set_action_deadlines,
            "after_action_notify_owners": self._action_notify_action_owners,

            # Before actions - Verification
            "before_verification_prepare_package": self._action_prepare_verification_package,

            # After actions - Verification
            "after_verification_assign_verifier": self._action_assign_verifier,
            "after_verification_notify_verifier": self._action_notify_verifier,

            # Before actions - Close
            "before_close_final_review": self._action_final_review,

            # After actions - Close
            "after_close_update_bcms": self._action_update_bcms_documentation,
            "after_close_document_lessons_learned": self._action_document_lessons_learned,
            "after_close_notify_stakeholders": self._action_notify_closure,
        }

    # =========================================================================
    # Guards - ISO 22301 Compliance Checks
    # =========================================================================

    async def _check_rca_lead_qualified(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить квалификацию RCA lead"""
        # TODO: проверка через training records / competency matrix
        return bool(metadata.get("rca_lead"))

    async def _check_rca_documented(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить документирование RCA"""
        root_causes = metadata.get("root_causes", [])
        rca_method = metadata.get("rca_method")
        return len(root_causes) > 0 and rca_method in ["5_whys", "fishbone", "fault_tree"]

    async def _check_actions_address_causes(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить, что действия устраняют причины, а не симптомы"""
        actions = metadata.get("corrective_actions", [])
        root_causes = metadata.get("root_causes", [])

        if not actions or not root_causes:
            return False

        # Каждая root cause должна иметь хотя бы одно action
        causes_addressed = set()
        for action in actions:
            addresses = action.get("addresses_cause_id")
            if addresses:
                causes_addressed.add(addresses)

        cause_ids = {cause.get("id") for cause in root_causes}
        return causes_addressed >= cause_ids  # Все причины покрыты

    async def _check_all_actions_completed(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить завершение всех действий"""
        nc = await repository.get_by_id(entity_id)
        if not nc:
            logger.warning(f"NC {entity_id} not found in _check_all_actions_completed")
            return False
        actions = nc.corrective_actions
        return all(action.get("status") == "completed" for action in actions)

    async def _check_evidence_for_actions(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить наличие свидетельств для всех действий"""
        evidence_ids = metadata.get("evidence_ids", [])
        nc = await repository.get_by_id(entity_id)
        if not nc:
            logger.warning(f"NC {entity_id} not found in _check_evidence_for_actions")
            return False
        actions = nc.corrective_actions
        return len(evidence_ids) >= len(actions)

    async def _check_verifier_qualified(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить квалификацию верификатора"""
        # Верификатор не должен быть исполнителем действий (независимость)
        verified_by = metadata.get("verified_by")
        nc = await repository.get_by_id(entity_id)
        if not nc:
            logger.warning(f"NC {entity_id} not found in _check_verifier_qualified")
            return False
        action_owners = {action.get("owner") for action in nc.corrective_actions}
        return verified_by not in action_owners

    async def _check_root_cause_eliminated(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить подтверждение устранения причины"""
        return metadata.get("effectiveness_confirmed") is True

    # =========================================================================
    # Actions - ISO 22301 Mandatory Steps
    # =========================================================================

    async def _action_prepare_rca_data(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Подготовить данные для RCA"""
        logger.info(f"Preparing RCA data for NC {entity.id}")
        # Собрать все данные: инцидент, аудит, контекст

    async def _action_create_investigation_tasks(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Создать задачи для investigation"""
        logger.info(f"Creating investigation tasks for NC {entity.id}")

    async def _action_notify_rca_team(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Уведомить RCA team"""
        logger.info(f"Notifying RCA team for NC {entity.id}")

    async def _action_validate_action_plan(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Валидация плана действий"""
        logger.info(f"Validating corrective action plan for NC {entity.id}")
        # AI может помочь проверить полноту

    async def _action_assign_action_owners(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Назначить ответственных за действия"""
        logger.info(f"Assigning action owners for NC {entity.id}")

    async def _action_set_action_deadlines(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Установить дедлайны"""
        logger.info(f"Setting deadlines for corrective actions NC {entity.id}")

    async def _action_notify_action_owners(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Уведомить владельцев действий"""
        logger.info(f"Notifying action owners for NC {entity.id}")

    async def _action_prepare_verification_package(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Подготовить пакет для верификации"""
        logger.info(f"Preparing verification package for NC {entity.id}")
        # Собрать все свидетельства, RCA, действия

    async def _action_assign_verifier(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Назначить верификатора"""
        logger.info(f"Assigning verifier for NC {entity.id}")

    async def _action_notify_verifier(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Уведомить верификатора"""
        logger.info(f"Notifying verifier for NC {entity.id}")

    async def _action_final_review(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Финальный review перед закрытием"""
        logger.info(f"Final review for NC {entity.id}")

    async def _action_update_bcms_documentation(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Обновить документацию BCMS"""
        logger.info(f"Updating BCMS documentation based on NC {entity.id}")
        # Если NC выявило недостаток процесса, обновить процедуры

    async def _action_document_lessons_learned(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Документировать lessons learned"""
        logger.info(f"Documenting lessons learned from NC {entity.id}")
        # Добавить в knowledge base для предотвращения повторения

    async def _action_notify_closure(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Уведомить о закрытии"""
        logger.info(f"Notifying stakeholders about NC closure {entity.id}")

    # =========================================================================
    # Helper Methods - AI Integration
    # =========================================================================

    async def ai_assist_rca(
        self,
        nc_id: str,
        nc_description: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        AI-помощь в проведении Root Cause Analysis

        Args:
            nc_id: ID несоответствия
            nc_description: Описание проблемы
            context: Дополнительный контекст (инцидент, аудит, etc.)

        Returns:
            Предложения AI для RCA:
            - Возможные первопричины
            - Вопросы для 5 Whys
            - Структура Fishbone диаграммы
        """
        logger.info(f"Requesting AI assistance for RCA of NC {nc_id}")
        # TODO: интеграция с AI orchestration
        # Использовать COMPLEX модель (DeepSeek) для RCA

        return {
            "suggested_root_causes": [],
            "five_whys_questions": [],
            "fishbone_categories": []
        }

    async def ai_validate_corrective_actions(
        self,
        root_causes: List[Dict[str, Any]],
        proposed_actions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        AI-валидация корректирующих действий

        Проверяет:
        - Все ли root causes адресованы
        - Достаточно ли действий
        - Не устраняют ли они только симптомы

        Returns:
            Результат валидации и рекомендации
        """
        logger.info("AI validating corrective actions")
        # TODO: AI orchestration
        return {
            "validation_passed": True,
            "coverage_score": 0.85,
            "recommendations": []
        }

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
        nc = await self.repository.get_by_id(entity_id)

        if not nc:
            raise WorkflowValidationError(f"Nonconformity {entity_id} not found")

        # 1. Terminal state check
        terminal_states = ["closed"]
        WorkflowValidator.validate_terminal_state(
            nc.status,
            terminal_states
        )

        # 2. Transition-specific validation
        if to_state == NCState.ROOT_CAUSE_ANALYSIS.value:
            # Require RCA lead
            rca_lead = metadata.get("rca_lead")
            WorkflowValidator.validate_required_field(
                rca_lead,
                "rca_lead",
                for_transition="start_rca"
            )

            # Require RCA method
            rca_method = metadata.get("rca_method")
            WorkflowValidator.validate_required_field(
                rca_method,
                "rca_method",
                for_transition="start_rca"
            )

            # Validate RCA method is valid
            valid_methods = ["5_whys", "fishbone", "fault_tree", "pareto"]
            if rca_method:
                WorkflowValidator.validate_enum_value(
                    rca_method,
                    valid_methods,
                    "rca_method"
                )

            # Validate identified_date is not in future
            if hasattr(nc, 'identified_date') and nc.identified_date:
                WorkflowValidator.validate_future_date(
                    nc.identified_date,
                    "identified_date"
                )

        elif to_state == NCState.CORRECTIVE_ACTION.value:
            # Require root causes
            root_causes = metadata.get("root_causes")
            WorkflowValidator.validate_required_list(
                root_causes,
                "root_causes",
                for_transition="complete_rca",
                min_items=1
            )

            # Require corrective actions
            corrective_actions = metadata.get("corrective_actions")
            WorkflowValidator.validate_required_list(
                corrective_actions,
                "corrective_actions",
                for_transition="complete_rca",
                min_items=1
            )

            # Validate each corrective action has owner and deadline
            if corrective_actions:
                WorkflowValidator.validate_list_items_have_fields(
                    corrective_actions,
                    ["owner", "deadline", "description"],
                    "Corrective action"
                )

                # Validate each action addresses a root cause
                for idx, action in enumerate(corrective_actions):
                    if not action.get("addresses_cause_id"):
                        raise WorkflowValidationError(
                            f"Corrective action {idx} must specify which root cause it addresses"
                        )

        elif to_state == NCState.VERIFICATION.value:
            # Require evidence_ids
            evidence_ids = metadata.get("evidence_ids")
            WorkflowValidator.validate_required_list(
                evidence_ids,
                "evidence_ids",
                for_transition="request_verification",
                min_items=1
            )

            # Require actions_completed flag
            actions_completed = metadata.get("actions_completed")
            if not actions_completed:
                raise WorkflowValidationError(
                    "All corrective actions must be completed before requesting verification"
                )

            # Validate all corrective actions are marked as completed
            if hasattr(nc, 'corrective_actions') and nc.corrective_actions:
                incomplete_actions = [
                    action for action in nc.corrective_actions
                    if action.get("status") != "completed"
                ]
                if incomplete_actions:
                    raise WorkflowValidationError(
                        f"Found {len(incomplete_actions)} incomplete corrective actions. "
                        f"All actions must be completed before verification."
                    )

        elif to_state == NCState.CLOSED.value:
            # Require verification result
            verification_result = metadata.get("verification_result")
            WorkflowValidator.validate_required_field(
                verification_result,
                "verification_result",
                for_transition="verify"
            )

            # Require verified_by
            verified_by = metadata.get("verified_by")
            WorkflowValidator.validate_required_field(
                verified_by,
                "verified_by",
                for_transition="verify"
            )

            # Require effectiveness confirmation
            effectiveness_confirmed = metadata.get("effectiveness_confirmed")
            if not effectiveness_confirmed:
                raise WorkflowValidationError(
                    "Effectiveness must be confirmed before closing NC"
                )

            # Ensure verifier is not same as action owner (independence)
            if hasattr(nc, 'corrective_actions') and nc.corrective_actions:
                action_owners = {action.get("owner") for action in nc.corrective_actions}
                if verified_by in action_owners:
                    raise WorkflowValidationError(
                        "Verifier cannot be the same person who performed corrective actions (independence violation)"
                    )

    # =========================================================================
    # RCA Template Integration - ISO 22301 Clause 10.1
    # =========================================================================

    async def start_rca(
        self,
        nc_id: UUID,
        rca_method: RCAMethod,
        rca_lead: str,
        rca_team: List[str],
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Start RCA process with template.

        Creates appropriate RCA template based on method.

        Args:
            nc_id: Nonconformity ID
            rca_method: RCA method (5_whys, fishbone, fault_tree)
            rca_lead: Person leading the RCA
            rca_team: Team members participating in RCA
            tenant_id: Tenant identifier

        Returns:
            RCA start confirmation with template
        """
        nc = await self.repository.get_by_id(nc_id)
        if not nc or nc.tenant_id != tenant_id:
            raise ValueError("NC not found or access denied")

        # Create RCA template
        template = RCATemplateFactory.create_template(
            method=rca_method,
            problem_statement=nc.description
        )

        # Update NC with RCA metadata
        await self.repository.update(nc_id, {
            "rca_method": rca_method.value,
            "rca_lead": rca_lead,
            "rca_team": rca_team,
            "rca_started_at": datetime.utcnow(),
            "metadata": {
                "rca_template": RCATemplateFactory.template_to_dict(template)
            }
        })

        # Transition to RCA state
        await self.transition(
            nc_id,
            NCState.OPEN,
            NCState.ROOT_CAUSE_ANALYSIS,
            actor_id=rca_lead,
            tenant_id=tenant_id,
            metadata={
                "rca_method": rca_method.value,
                "rca_lead": rca_lead,
                "rca_team": rca_team
            }
        )

        logger.info(f"RCA started for NC {nc_id} using {rca_method.value} method")

        return {
            "nc_id": str(nc_id),
            "rca_method": rca_method.value,
            "template": RCATemplateFactory.template_to_dict(template),
            "instructions": self._get_template_instructions(rca_method)
        }

    async def complete_rca(
        self,
        nc_id: UUID,
        completed_template: Dict[str, Any],
        actor_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Complete RCA with filled template.

        Extracts root causes and generates summary.

        Args:
            nc_id: Nonconformity ID
            completed_template: Filled RCA template data
            actor_id: Person completing the RCA
            tenant_id: Tenant identifier

        Returns:
            RCA completion confirmation with root causes
        """
        nc = await self.repository.get_by_id(nc_id)
        if not nc or nc.tenant_id != tenant_id:
            raise ValueError("NC not found or access denied")

        if not nc.rca_method:
            raise ValueError("RCA method not set. Start RCA first.")

        # Extract root causes
        root_causes = RCAAnalyzer.extract_root_causes(
            method=nc.rca_method,
            template_data=completed_template
        )

        # Generate summary
        summary = RCAAnalyzer.generate_summary(
            method=nc.rca_method,
            template_data=completed_template
        )

        # Update NC
        await self.repository.update(nc_id, {
            "root_causes": [
                {"id": str(i), "description": cause, "evidence": ""}
                for i, cause in enumerate(root_causes)
            ],
            "rca_completed_at": datetime.utcnow(),
            "metadata": {
                "rca_template": completed_template,
                "rca_summary": summary
            }
        })

        # Transition to CORRECTIVE_ACTION state
        await self.transition(
            nc_id,
            NCState.ROOT_CAUSE_ANALYSIS,
            NCState.CORRECTIVE_ACTION,
            actor_id=actor_id,
            tenant_id=tenant_id,
            metadata={
                "root_causes": [
                    {"id": str(i), "description": cause, "evidence": ""}
                    for i, cause in enumerate(root_causes)
                ],
                "corrective_actions": [],  # Will be planned next
                "rca_method": nc.rca_method.value
            }
        )

        logger.info(f"RCA completed for NC {nc_id}, identified {len(root_causes)} root causes")

        return {
            "nc_id": str(nc_id),
            "root_causes": root_causes,
            "summary": summary,
            "next_step": "Plan corrective actions to address root causes"
        }

    def _get_template_instructions(self, method: RCAMethod) -> str:
        """Get instructions for RCA template"""
        instructions = {
            RCAMethod.FIVE_WHYS: "Ask 'Why?' 5 times to drill down to root cause. Each answer becomes the next question.",
            RCAMethod.FISHBONE: "Categorize causes into People, Process, Technology, Environment, Materials, Measurement. Add sub-causes for depth.",
            RCAMethod.FAULT_TREE: "Build tree of contributing factors with AND/OR gates and probabilities (0.0-1.0)"
        }
        return instructions.get(method, "Complete the RCA template")
