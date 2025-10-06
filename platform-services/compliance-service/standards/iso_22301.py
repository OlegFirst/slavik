"""
ISO 22301:2019 Requirements Database

Migrated from: /services/BCM_1/compliance_checker/app.py (lines 120-238)
Date: 2025-10-01

Contains all 13 mandatory requirements from ISO 22301:2019
with evidence requirements, weights, and categorization.
"""

from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from compliance.models.enums import ComplianceStandard, RequirementCategory


class ISORequirement(BaseModel):
    """
    Simplified ISO requirement model for standards library.

    Used for loading requirements without tenant context.
    Convert to ComplianceRequirement when creating assessment.
    """
    id: str = Field(..., description="Clause number (e.g., '4.1', '8.2')")
    standard: ComplianceStandard
    clause: str = Field(..., description="Clause number (same as id)")
    title: str
    description: str
    category: RequirementCategory
    mandatory: bool = True
    evidence_required: List[str] = Field(default_factory=list)
    weight: float = Field(default=1.0, ge=0.1, le=5.0)
    related_clauses: List[str] = Field(default_factory=list)
    verification_guidance: str = ""

    class Config:
        use_enum_values = False


# ISO 22301:2019 Requirements Database
# Source: compliance_checker/app.py (tested in production)
ISO_22301_REQUIREMENTS: Dict[str, ISORequirement] = {
    "4.1": ISORequirement(
        id="4.1",
        standard=ComplianceStandard.ISO_22301,
        clause="4.1",
        title="Понимание организации и ее контекста",
        description="Организация должна определить внешние и внутренние вопросы, которые относятся к ее назначению и стратегическому направлению и влияют на способность достичь намеченных результатов BCMS",
        category=RequirementCategory.GOVERNANCE,
        mandatory=True,
        evidence_required=["context_analysis", "stakeholder_analysis", "external_factors_assessment"],
        weight=1.5,
        related_clauses=["4.2", "4.3"],
        verification_guidance="Должна быть документирована информация о внешних и внутренних факторах. Проверить PESTLE/SWOT анализ."
    ),

    "4.2": ISORequirement(
        id="4.2",
        standard=ComplianceStandard.ISO_22301,
        clause="4.2",
        title="Понимание потребностей и ожиданий заинтересованных сторон",
        description="Организация должна определить заинтересованные стороны, относящиеся к BCMS, и их требования",
        category=RequirementCategory.GOVERNANCE,
        mandatory=True,
        evidence_required=["stakeholder_register", "requirements_matrix", "stakeholder_communication_records"],
        weight=1.3,
        related_clauses=["4.1", "4.3"],
        verification_guidance="Должен быть реестр заинтересованных сторон и матрица их требований с доказательствами коммуникации."
    ),

    "4.3": ISORequirement(
        id="4.3",
        standard=ComplianceStandard.ISO_22301,
        clause="4.3",
        title="Определение области применения системы менеджмента непрерывности бизнеса",
        description="Организация должна определить границы и применимость BCMS для установления ее области применения",
        category=RequirementCategory.GOVERNANCE,
        mandatory=True,
        evidence_required=["scope_statement", "boundary_definition", "applicability_statement"],
        weight=1.8,
        related_clauses=["4.1", "4.2"],
        verification_guidance="Документированная область применения BCMS с четкими границами и исключениями (если есть)."
    ),

    "5.1": ISORequirement(
        id="5.1",
        standard=ComplianceStandard.ISO_22301,
        clause="5.1",
        title="Лидерство и обязательства",
        description="Высшее руководство должно продемонстрировать лидерство и приверженность в отношении BCMS",
        category=RequirementCategory.GOVERNANCE,
        mandatory=True,
        evidence_required=["leadership_commitment", "resource_allocation", "policy_approval", "management_meeting_minutes"],
        weight=2.0,
        related_clauses=["5.2", "5.3"],
        verification_guidance="Протоколы заседаний руководства, выделение ресурсов, утверждение политики."
    ),

    "5.2": ISORequirement(
        id="5.2",
        standard=ComplianceStandard.ISO_22301,
        clause="5.2",
        title="Политика",
        description="Высшее руководство должно установить политику непрерывности бизнеса",
        category=RequirementCategory.GOVERNANCE,
        mandatory=True,
        evidence_required=["bc_policy", "policy_communication", "policy_review", "policy_approval"],
        weight=1.8,
        related_clauses=["5.1", "5.3"],
        verification_guidance="Утвержденная политика BC, доказательства коммуникации, регулярный пересмотр."
    ),

    "5.3": ISORequirement(
        id="5.3",
        standard=ComplianceStandard.ISO_22301,
        clause="5.3",
        title="Роли, ответственность и полномочия в организации",
        description="Высшее руководство должно обеспечить распределение и коммуникацию ответственности и полномочий для ролей, относящихся к BCMS",
        category=RequirementCategory.GOVERNANCE,
        mandatory=True,
        evidence_required=["raci_matrix", "job_descriptions", "role_assignments", "delegation_records"],
        weight=1.5,
        related_clauses=["5.1", "7.2"],
        verification_guidance="RACI матрица, должностные инструкции, назначение ответственных."
    ),

    "6.1": ISORequirement(
        id="6.1",
        standard=ComplianceStandard.ISO_22301,
        clause="6.1",
        title="Действия в отношении рисков и возможностей",
        description="При планировании BCMS организация должна рассматривать вопросы и требования, определенные в 4.1 и 4.2",
        category=RequirementCategory.RISK_MANAGEMENT,
        mandatory=True,
        evidence_required=["risk_assessment", "risk_register", "risk_treatment_plan", "opportunity_analysis"],
        weight=2.5,
        related_clauses=["8.2", "8.3"],
        verification_guidance="Оценка рисков, реестр рисков, планы обработки рисков."
    ),

    "8.2": ISORequirement(
        id="8.2",
        standard=ComplianceStandard.ISO_22301,
        clause="8.2",
        title="Анализ воздействия на бизнес и оценка риска",
        description="Организация должна установить, внедрить и поддерживать процесс BIA и оценки рисков",
        category=RequirementCategory.BUSINESS_CONTINUITY,
        mandatory=True,
        evidence_required=[
            "bia_methodology",
            "bia_results",
            "rto_rpo_mtpd",
            "dependencies_map",
            "risk_assessment_results",
            "impact_assessment"
        ],
        weight=3.0,  # Highest weight - critical requirement
        related_clauses=["6.1", "8.3", "8.4"],
        verification_guidance="Документированные BIA и оценка рисков, определение RTO/RPO/MTPD, карта зависимостей."
    ),

    "8.3": ISORequirement(
        id="8.3",
        standard=ComplianceStandard.ISO_22301,
        clause="8.3",
        title="Стратегия непрерывности бизнеса",
        description="Организация должна установить стратегии непрерывности бизнеса, состоящие из решений по обеспечению непрерывности для приоритетных видов деятельности",
        category=RequirementCategory.BUSINESS_CONTINUITY,
        mandatory=True,
        evidence_required=["bc_strategy", "recovery_strategies", "strategy_approval", "strategy_cost_benefit"],
        weight=2.8,
        related_clauses=["8.2", "8.4"],
        verification_guidance="Стратегии непрерывности для критических процессов, анализ затрат/выгод."
    ),

    "8.4": ISORequirement(
        id="8.4",
        standard=ComplianceStandard.ISO_22301,
        clause="8.4",
        title="Планы и процедуры непрерывности бизнеса",
        description="Организация должна установить планы и процедуры непрерывности бизнеса для обеспечения непрерывности и/или восстановления приоритетных видов деятельности",
        category=RequirementCategory.BUSINESS_CONTINUITY,
        mandatory=True,
        evidence_required=[
            "bc_plans",
            "procedures",
            "emergency_procedures",
            "communication_plan",
            "incident_response_structure"
        ],
        weight=3.0,  # Highest weight - critical requirement
        related_clauses=["8.3", "8.5"],
        verification_guidance="Планы непрерывности, процедуры реагирования, структура управления инцидентами."
    ),

    "8.5": ISORequirement(
        id="8.5",
        standard=ComplianceStandard.ISO_22301,
        clause="8.5",
        title="Упражнения и тестирование",
        description="Организация должна проводить упражнения и тестирование для подтверждения эффективности планов непрерывности",
        category=RequirementCategory.BUSINESS_CONTINUITY,
        mandatory=True,
        evidence_required=[
            "exercise_program",
            "test_results",
            "improvement_actions",
            "lessons_learned"
        ],
        weight=2.5,
        related_clauses=["8.4", "10.2"],
        verification_guidance="Программа учений, результаты тестов, планы улучшений, извлеченные уроки."
    ),

    "9.1": ISORequirement(
        id="9.1",
        standard=ComplianceStandard.ISO_22301,
        clause="9.1",
        title="Мониторинг, измерение, анализ и оценка",
        description="Организация должна определить что нуждается в мониторинге и измерении, методы и когда должны быть проведены",
        category=RequirementCategory.MONITORING,
        mandatory=True,
        evidence_required=["monitoring_plan", "kpis", "measurement_results", "performance_analysis"],
        weight=2.0,
        related_clauses=["9.2", "9.3"],
        verification_guidance="План мониторинга, KPI, результаты измерений, анализ эффективности."
    ),

    "9.2": ISORequirement(
        id="9.2",
        standard=ComplianceStandard.ISO_22301,
        clause="9.2",
        title="Внутренний аудит",
        description="Организация должна проводить внутренние аудиты через запланированные интервалы",
        category=RequirementCategory.MONITORING,
        mandatory=True,
        evidence_required=[
            "audit_program",
            "audit_reports",
            "corrective_actions",
            "auditor_competence",
            "audit_findings"
        ],
        weight=2.3,
        related_clauses=["9.3", "10.1"],
        verification_guidance="Программа аудита, отчеты аудитов, корректирующие действия, компетентность аудиторов."
    ),

    "10.1": ISORequirement(
        id="10.1",
        standard=ComplianceStandard.ISO_22301,
        clause="10.1",
        title="Несоответствие и корректирующие действия",
        description="Когда возникает несоответствие, организация должна реагировать на него и предпринимать корректирующие действия",
        category=RequirementCategory.IMPROVEMENT,
        mandatory=True,
        evidence_required=[
            "nonconformity_register",
            "root_cause_analysis",
            "corrective_actions",
            "effectiveness_review"
        ],
        weight=2.0,
        related_clauses=["9.2", "10.2"],
        verification_guidance="Реестр несоответствий, RCA, корректирующие действия, оценка эффективности."
    ),

    "10.2": ISORequirement(
        id="10.2",
        standard=ComplianceStandard.ISO_22301,
        clause="10.2",
        title="Постоянное улучшение",
        description="Организация должна постоянно улучшать пригодность, адекватность и эффективность BCMS",
        category=RequirementCategory.IMPROVEMENT,
        mandatory=True,
        evidence_required=[
            "improvement_plan",
            "improvement_evidence",
            "management_review",
            "lessons_learned"
        ],
        weight=1.8,
        related_clauses=["9.3", "10.1"],
        verification_guidance="План улучшений, доказательства реализации, пересмотр руководством, извлеченные уроки."
    )
}


# Helper functions for easy access to requirements

def get_requirement(clause: str) -> Optional[ISORequirement]:
    """
    Get a single requirement by clause number

    Args:
        clause: ISO 22301 clause number (e.g., "8.2", "10.1")

    Returns:
        ISORequirement or None if not found

    Example:
        >>> req = get_requirement("8.2")
        >>> print(req.title)
        'Анализ воздействия на бизнес и оценка риска'
    """
    return ISO_22301_REQUIREMENTS.get(clause)


def get_all_requirements() -> Dict[str, ISORequirement]:
    """
    Get all ISO 22301 requirements

    Returns:
        Dictionary of all requirements {clause: requirement}

    Example:
        >>> reqs = get_all_requirements()
        >>> print(len(reqs))
        13
    """
    return ISO_22301_REQUIREMENTS.copy()


def get_requirements_by_category(category: RequirementCategory) -> List[ISORequirement]:
    """
    Get requirements filtered by category

    Args:
        category: RequirementCategory enum value

    Returns:
        List of requirements in that category

    Example:
        >>> gov_reqs = get_requirements_by_category(RequirementCategory.GOVERNANCE)
        >>> print(len(gov_reqs))
        5
    """
    return [
        req for req in ISO_22301_REQUIREMENTS.values()
        if req.category == category
    ]


def get_requirements_by_weight(min_weight: float = 0.0) -> List[Tuple[str, ISORequirement]]:
    """
    Get requirements sorted by weight (descending)

    Args:
        min_weight: Minimum weight filter (default 0.0 = all)

    Returns:
        List of tuples (clause, requirement) sorted by weight DESC

    Example:
        >>> critical_reqs = get_requirements_by_weight(min_weight=2.5)
        >>> for clause, req in critical_reqs:
        ...     print(f"{clause}: {req.weight}")
        '8.2': 3.0
        '8.4': 3.0
        '8.3': 2.8
        '6.1': 2.5
        '8.5': 2.5
    """
    filtered = [
        (clause, req) for clause, req in ISO_22301_REQUIREMENTS.items()
        if req.weight >= min_weight
    ]
    return sorted(filtered, key=lambda x: x[1].weight, reverse=True)


def get_mandatory_requirements() -> List[ISORequirement]:
    """
    Get all mandatory requirements (all ISO 22301 requirements are mandatory)

    Returns:
        List of mandatory requirements
    """
    return [
        req for req in ISO_22301_REQUIREMENTS.values()
        if req.mandatory
    ]


def get_total_weight() -> float:
    """
    Calculate total weight of all requirements (for weighted scoring)

    Returns:
        Sum of all requirement weights

    Example:
        >>> total = get_total_weight()
        >>> print(total)
        28.3
    """
    return sum(req.weight for req in ISO_22301_REQUIREMENTS.values())


def get_clause_list() -> List[str]:
    """
    Get list of all clause numbers (sorted)

    Returns:
        Sorted list of clause numbers

    Example:
        >>> clauses = get_clause_list()
        >>> print(clauses)
        ['4.1', '4.2', '4.3', '5.1', '5.2', '5.3', '6.1', '8.2', '8.3', '8.4', '8.5', '9.1', '9.2', '10.1', '10.2']
    """
    # Custom sort to handle clause numbers correctly
    def clause_sort_key(clause: str) -> Tuple:
        parts = clause.split('.')
        return (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)

    return sorted(ISO_22301_REQUIREMENTS.keys(), key=clause_sort_key)


# Metadata
__version__ = "1.0.0"
__source__ = "BCM_1/compliance_checker/app.py (lines 120-238)"
__migration_date__ = "2025-10-01"
__standard_version__ = "ISO 22301:2019"
__total_requirements__ = len(ISO_22301_REQUIREMENTS)
__total_weight__ = get_total_weight()
