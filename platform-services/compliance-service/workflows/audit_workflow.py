"""
Audit Workflow - Управление аудитами (ISO 22301 Clause 9.2)

Audit (Аудит) - системная проверка соответствия BCMS требованиям стандарта.

Типы аудитов:
- INTERNAL: внутренний аудит (минимум 1 раз в год)
- EXTERNAL: внешний аудит
- SURVEILLANCE: надзорный аудит (ежегодно после сертификации)
- CERTIFICATION: сертификационный аудит
- RECERTIFICATION: ресертификация (каждые 3 года)

Жизненный цикл:
1. PLANNED - Аудит запланирован
2. PREPARATION - Подготовка к аудиту
3. IN_PROGRESS - Аудит проводится
4. FINDINGS_REVIEW - Проверка findings
5. COMPLETED - Завершен

ISO 22301 требует:
- Аудит программа (schedule)
- Критерии и методы
- Независимость аудиторов
- Отчет руководству
- Retained documented information

События:
- audit.planned
- audit.preparation_started
- audit.audit_started
- audit.finding_submitted
- audit.findings_reviewed
- audit.completed
"""

import logging
from enum import Enum
from typing import Dict, List, Any
from datetime import datetime, timedelta
from uuid import UUID

from .base_workflow import BaseWorkflow, WorkflowTransition, WorkflowGuard
from .validators import WorkflowValidator, WorkflowValidationError
from compliance.models.enums import AuditType, AuditResult

logger = logging.getLogger(__name__)


class AuditState(str, Enum):
    """Состояния аудита"""
    PLANNED = "planned"
    PREPARATION = "preparation"
    IN_PROGRESS = "in_progress"
    FINDINGS_REVIEW = "findings_review"
    COMPLETED = "completed"


class AuditEvent(str, Enum):
    """События аудита"""
    PLANNED = "planned"
    PREPARATION_STARTED = "preparation_started"
    AUDIT_STARTED = "audit_started"
    FINDING_SUBMITTED = "finding_submitted"
    FINDINGS_REVIEWED = "findings_reviewed"
    COMPLETED = "completed"


class AuditWorkflow(BaseWorkflow):
    """Воркфлоу управления аудитами (ISO 22301 Clause 9.2)"""

    def _get_state_enum(self) -> type:
        return AuditState

    def _get_event_prefix(self) -> str:
        return "audit"

    def _define_transitions(self) -> List[WorkflowTransition]:
        """
        Граф переходов:

        PLANNED ─(start_prep)→ PREPARATION ─(start_audit)→ IN_PROGRESS ─(submit_findings)→ FINDINGS_REVIEW ─(complete)→ COMPLETED
        """
        return [
            # PLANNED → PREPARATION
            WorkflowTransition(
                from_state=AuditState.PLANNED,
                to_state=AuditState.PREPARATION,
                event_name=AuditEvent.PREPARATION_STARTED.value,
                required_fields=["preparation_lead"],
                guards=["audit_scheduled", "scope_defined"],
                actions=[
                    "before_prep_validate_schedule",
                    "after_prep_generate_audit_package",
                    "after_prep_request_documents",
                    "after_prep_notify_auditees"
                ],
                description="Начало подготовки к аудиту"
            ),

            # PREPARATION → IN_PROGRESS
            WorkflowTransition(
                from_state=AuditState.PREPARATION,
                to_state=AuditState.IN_PROGRESS,
                event_name=AuditEvent.AUDIT_STARTED.value,
                required_fields=["auditor_name", "actual_date"],
                guards=["preparation_complete", "auditor_independent"],
                actions=[
                    "before_audit_opening_meeting",
                    "after_audit_create_checklist",
                    "after_audit_notify_start"
                ],
                description="Начало проведения аудита"
            ),

            # IN_PROGRESS → FINDINGS_REVIEW
            WorkflowTransition(
                from_state=AuditState.IN_PROGRESS,
                to_state=AuditState.FINDINGS_REVIEW,
                event_name=AuditEvent.FINDINGS_REVIEWED.value,
                required_fields=["findings", "evidence_reviewed"],
                guards=["all_clauses_checked", "findings_documented"],
                actions=[
                    "before_review_closing_meeting",
                    "before_review_categorize_findings",
                    "after_review_create_nc_records",
                    "after_review_notify_management"
                ],
                description="Findings представлены, начало проверки"
            ),

            # FINDINGS_REVIEW → COMPLETED
            WorkflowTransition(
                from_state=AuditState.FINDINGS_REVIEW,
                to_state=AuditState.COMPLETED,
                event_name=AuditEvent.COMPLETED.value,
                required_fields=["overall_result", "audit_report_url"],
                guards=["report_approved", "nc_created_for_findings"],
                actions=[
                    "before_complete_finalize_report",
                    "after_complete_schedule_next_audit",
                    "after_complete_update_certification_status",
                    "after_complete_management_review_input",
                    "after_complete_notify_completion"
                ],
                description="Аудит завершен"
            ),
        ]

    def _define_guards(self) -> Dict[str, WorkflowGuard]:
        return {
            "audit_scheduled": WorkflowGuard(
                name="audit_scheduled",
                check=self._check_audit_scheduled,
                error_message="Аудит должен быть запланирован в audit programme"
            ),

            "scope_defined": WorkflowGuard(
                name="scope_defined",
                check=self._check_scope_defined,
                error_message="Scope аудита должен быть четко определен"
            ),

            "preparation_complete": WorkflowGuard(
                name="preparation_complete",
                check=self._check_preparation_complete,
                error_message="Подготовка к аудиту не завершена"
            ),

            "auditor_independent": WorkflowGuard(
                name="auditor_independent",
                check=self._check_auditor_independence,
                error_message="Аудитор не может проверять свою собственную работу (ISO требование)"
            ),

            "all_clauses_checked": WorkflowGuard(
                name="all_clauses_checked",
                check=self._check_all_clauses_checked,
                error_message="Не все clauses в scope проверены"
            ),

            "findings_documented": WorkflowGuard(
                name="findings_documented",
                check=self._check_findings_documented,
                error_message="Findings должны быть задокументированы с доказательствами"
            ),

            "report_approved": WorkflowGuard(
                name="report_approved",
                check=self._check_report_approved,
                error_message="Отчет аудита должен быть одобрен"
            ),

            "nc_created_for_findings": WorkflowGuard(
                name="nc_created_for_findings",
                check=self._check_nc_created,
                error_message="Для всех Major/Minor findings должны быть созданы NC"
            ),
        }

    def _define_actions(self) -> Dict[str, callable]:
        return {
            # Before actions - Preparation
            "before_prep_validate_schedule": self._action_validate_schedule,

            # After actions - Preparation
            "after_prep_generate_audit_package": self._action_generate_audit_package,
            "after_prep_request_documents": self._action_request_documents,
            "after_prep_notify_auditees": self._action_notify_auditees,

            # Before actions - Audit
            "before_audit_opening_meeting": self._action_opening_meeting,

            # After actions - Audit
            "after_audit_create_checklist": self._action_create_checklist,
            "after_audit_notify_start": self._action_notify_audit_start,

            # Before actions - Findings Review
            "before_review_closing_meeting": self._action_closing_meeting,
            "before_review_categorize_findings": self._action_categorize_findings,

            # After actions - Findings Review
            "after_review_create_nc_records": self._action_create_nc_records,
            "after_review_notify_management": self._action_notify_management,

            # Before actions - Complete
            "before_complete_finalize_report": self._action_finalize_report,

            # After actions - Complete
            "after_complete_schedule_next_audit": self._action_schedule_next_audit,
            "after_complete_update_certification_status": self._action_update_certification,
            "after_complete_management_review_input": self._action_create_mgmt_review_input,
            "after_complete_notify_completion": self._action_notify_completion,
        }

    # =========================================================================
    # Guards - ISO 22301 Audit Requirements
    # =========================================================================

    async def _check_audit_scheduled(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить наличие в audit programme"""
        audit = await repository.get_by_id(entity_id)
        if not audit:
            logger.warning(f"Audit {entity_id} not found in _check_audit_scheduled")
            return False
        return bool(audit.planned_date)

    async def _check_scope_defined(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить определение scope"""
        audit = await repository.get_by_id(entity_id)
        if not audit:
            logger.warning(f"Audit {entity_id} not found in _check_scope_defined")
            return False
        return bool(audit.scope and audit.standard)

    async def _check_preparation_complete(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить готовность к аудиту"""
        audit = await repository.get_by_id(entity_id)
        if not audit:
            logger.warning(f"Audit {entity_id} not found in _check_preparation_complete")
            return False
        # Audit package сгенерирован, документы собраны
        return bool(audit.audit_package_generated)

    async def _check_auditor_independence(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить независимость аудитора (ISO 22301 требование)"""
        auditor_name = metadata.get("auditor_name")
        audit = await repository.get_by_id(entity_id)
        if not audit:
            logger.warning(f"Audit {entity_id} not found in _check_auditor_independence")
            return False

        # Для internal audit: аудитор не должен проверять свою работу
        # Для external: всегда независим
        if audit.audit_type == AuditType.EXTERNAL.value:
            return True

        # TODO: проверить, что auditor не владелец процессов в scope
        return bool(auditor_name)

    async def _check_all_clauses_checked(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить, что все clauses проверены"""
        audit = await repository.get_by_id(entity_id)
        if not audit:
            logger.warning(f"Audit {entity_id} not found in _check_all_clauses_checked")
            return False
        scope_clauses = audit.scope_clauses or []
        checked_clauses = metadata.get("evidence_reviewed", [])
        return set(scope_clauses).issubset(set(checked_clauses))

    async def _check_findings_documented(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить документирование findings"""
        findings = metadata.get("findings", [])
        return all(
            finding.get("clause") and finding.get("description") and finding.get("evidence")
            for finding in findings
        )

    async def _check_report_approved(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить одобрение отчета"""
        return bool(metadata.get("audit_report_url"))

    async def _check_nc_created(self, entity_id, from_state, to_state, actor_id, metadata, repository) -> bool:
        """Проверить создание NC для findings"""
        audit = await repository.get_by_id(entity_id)
        if not audit:
            logger.warning(f"Audit {entity_id} not found in _check_nc_created")
            return False
        findings = audit.findings or []
        major_minor_findings = [f for f in findings if f.get("type") in ["MAJOR", "MINOR"]]

        if not major_minor_findings:
            return True

        # Проверить, что NC созданы
        nc_created = await repository.get_nc_for_audit(audit.id)
        return len(nc_created) >= len(major_minor_findings)

    # =========================================================================
    # Actions - Audit Process
    # =========================================================================

    async def _action_validate_schedule(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Валидация расписания"""
        logger.info(f"Validating audit schedule for {entity.id}")

    async def _action_generate_audit_package(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Сгенерировать audit package"""
        logger.info(f"Generating audit package for {entity.id}")
        # Вызвать compliance assessment для создания пакета:
        # - Compliance score по каждому clause
        # - Список свидетельств
        # - Последние упражнения
        # - История NC

    async def _action_request_documents(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Запросить документы для аудита"""
        logger.info(f"Requesting documents for audit {entity.id}")

    async def _action_notify_auditees(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Уведомить проверяемых"""
        logger.info(f"Notifying auditees for audit {entity.id}")

    async def _action_opening_meeting(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Opening meeting"""
        logger.info(f"Conducting opening meeting for audit {entity.id}")

    async def _action_create_checklist(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Создать audit checklist"""
        logger.info(f"Creating audit checklist for {entity.id}")
        # Checklist по каждому clause в scope

    async def _action_notify_audit_start(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Уведомить о начале аудита"""
        logger.info(f"Notifying audit start {entity.id}")

    async def _action_closing_meeting(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Closing meeting"""
        logger.info(f"Conducting closing meeting for audit {entity.id}")

    async def _action_categorize_findings(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Категоризировать findings"""
        logger.info(f"Categorizing findings for audit {entity.id}")
        # MAJOR, MINOR, OBSERVATION

    async def _action_create_nc_records(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Создать NC записи для findings"""
        logger.info(f"Creating NC records for audit findings {entity.id}")
        # Через nonconformity_workflow

    async def _action_notify_management(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Уведомить руководство о findings"""
        logger.info(f"Notifying management about audit findings {entity.id}")

    async def _action_finalize_report(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Финализировать отчет"""
        logger.info(f"Finalizing audit report {entity.id}")

    async def _action_schedule_next_audit(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Запланировать следующий аудит"""
        logger.info(f"Scheduling next audit after {entity.id}")
        # Surveillance через год для certification
        # Internal audit через год

    async def _action_update_certification(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Обновить статус сертификации"""
        logger.info(f"Updating certification status from audit {entity.id}")

    async def _action_create_mgmt_review_input(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Создать input для management review"""
        logger.info(f"Creating management review input from audit {entity.id}")
        # Audit results - обязательный input для mgmt review (ISO 9.3)

    async def _action_notify_completion(self, entity, from_state, to_state, actor_id, metadata, repository):
        """Уведомить о завершении"""
        logger.info(f"Notifying audit completion {entity.id}")

    # =========================================================================
    # Helper Methods
    # =========================================================================

    async def initialize_audit(
        self,
        audit_data: Dict[str, Any],
        tenant_id: str,
        planner_id: str
    ) -> Dict[str, Any]:
        """
        Создать новый аудит в audit programme

        Args:
            audit_data: Данные аудита (тип, scope, дата)
            tenant_id: ID тенанта
            planner_id: ID планировщика

        Returns:
            Созданный аудит
        """
        audit_data.update({
            "status": AuditState.PLANNED.value,
            "tenant_id": tenant_id,
            "planned_by": planner_id,
            "created_at": datetime.utcnow()
        })

        audit = await self.repository.create(audit_data)

        # Публикация события
        if self.eventbus:
            await self.eventbus.publish({
                "event_type": f"bcm.compliance.audit.{AuditEvent.PLANNED.value}",
                "tenant_id": tenant_id,
                "entity_id": audit.id,
                "actor_id": planner_id,
                "metadata": {
                    "audit_type": audit_data.get("audit_type"),
                    "standard": audit_data.get("standard"),
                    "planned_date": audit_data.get("planned_date")
                },
                "timestamp": datetime.utcnow().isoformat()
            })

        logger.info(f"Created audit {audit.id} in PLANNED state")
        return audit

    async def get_audit_programme(self, tenant_id: str, year: int) -> List[Dict[str, Any]]:
        """
        Получить audit programme на год (ISO 22301 требование)

        Returns:
            Список всех запланированных аудитов
        """
        audits = await self.repository.get_audits_by_year(tenant_id, year)
        return [
            {
                "audit_id": audit.id,
                "audit_type": audit.audit_type,
                "standard": audit.standard,
                "scope": audit.scope,
                "planned_date": audit.planned_date.isoformat() if audit.planned_date else None,
                "status": audit.status,
                "auditor_name": audit.auditor_name
            }
            for audit in audits
        ]

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
        audit = await self.repository.get_by_id(entity_id)

        if not audit:
            raise WorkflowValidationError(f"Audit {entity_id} not found")

        # 1. Terminal state check
        terminal_states = ["completed"]
        WorkflowValidator.validate_terminal_state(
            audit.status,
            terminal_states
        )

        # 2. Transition-specific validation
        if to_state == AuditState.PREPARATION.value:
            # Require preparation lead
            preparation_lead = metadata.get("preparation_lead")
            WorkflowValidator.validate_required_field(
                preparation_lead,
                "preparation_lead",
                for_transition="start_preparation"
            )

            # Validate scope is defined
            if hasattr(audit, 'scope'):
                WorkflowValidator.validate_required_field(
                    audit.scope,
                    "scope",
                    for_transition="start_preparation"
                )

            # Validate planned date exists
            if hasattr(audit, 'planned_date'):
                WorkflowValidator.validate_required_field(
                    audit.planned_date,
                    "planned_date",
                    for_transition="start_preparation"
                )

        elif to_state == AuditState.IN_PROGRESS.value:
            # Require auditor
            auditor_name = metadata.get("auditor_name")
            WorkflowValidator.validate_required_field(
                auditor_name,
                "auditor_name",
                for_transition="start_audit"
            )

            # Require actual_date
            actual_date = metadata.get("actual_date")
            WorkflowValidator.validate_required_field(
                actual_date,
                "actual_date",
                for_transition="start_audit"
            )

            # Validate auditor independence for internal audits
            if hasattr(audit, 'audit_type') and audit.audit_type == AuditType.INTERNAL.value:
                # For internal audits, check independence
                # (In real implementation, would check against process ownership)
                pass

            # Validate actual_date not too far in past
            if actual_date:
                if isinstance(actual_date, str):
                    actual_date = datetime.fromisoformat(actual_date.replace('Z', '+00:00'))
                # Allow max 7 days in past for backdating
                past_limit = datetime.utcnow() - timedelta(days=7)
                if actual_date < past_limit:
                    raise WorkflowValidationError(
                        "actual_date cannot be more than 7 days in the past"
                    )

        elif to_state == AuditState.FINDINGS_REVIEW.value:
            # Require findings
            findings = metadata.get("findings")
            WorkflowValidator.validate_required_list(
                findings,
                "findings",
                for_transition="submit_findings",
                min_items=0  # Can have zero findings (positive audit result)
            )

            # Validate findings structure
            if findings:
                required_fields = ["clause", "description", "evidence", "type"]
                WorkflowValidator.validate_list_items_have_fields(
                    findings,
                    required_fields,
                    "Finding"
                )

                # Validate finding types
                valid_types = ["MAJOR", "MINOR", "OBSERVATION"]
                for finding in findings:
                    if finding.get("type"):
                        WorkflowValidator.validate_enum_value(
                            finding["type"],
                            valid_types,
                            "finding type"
                        )

            # Require evidence_reviewed
            evidence_reviewed = metadata.get("evidence_reviewed")
            WorkflowValidator.validate_required_list(
                evidence_reviewed,
                "evidence_reviewed",
                for_transition="submit_findings",
                min_items=1
            )

        elif to_state == AuditState.COMPLETED.value:
            # Require overall result
            overall_result = metadata.get("overall_result")
            WorkflowValidator.validate_required_field(
                overall_result,
                "overall_result",
                for_transition="complete"
            )

            # Require audit report
            audit_report_url = metadata.get("audit_report_url")
            WorkflowValidator.validate_required_field(
                audit_report_url,
                "audit_report_url",
                for_transition="complete"
            )
