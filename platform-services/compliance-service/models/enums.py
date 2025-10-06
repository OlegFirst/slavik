"""
Enums for Compliance Module

Централизованные перечисления для всех моделей
"""

from enum import Enum


class ComplianceStandard(str, Enum):
    """Стандарты соответствия"""
    ISO_22301 = "iso_22301"
    ISO_27001 = "iso_27001"
    BCI_GPG = "bci_gpg"
    SOX = "sarbanes_oxley"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    CMS = "cms_emergency_prep"
    JOINT_COMMISSION = "joint_commission"
    NIST = "nist_framework"
    COBIT = "cobit"
    CUSTOM = "custom"


class ComplianceStatus(str, Enum):
    """Статусы соответствия"""
    COMPLIANT = "compliant"  # ≥90%
    PARTIAL = "partial_compliance"  # 70-89%
    NON_COMPLIANT = "non_compliant"  # <70%
    NOT_ASSESSED = "not_assessed"
    PENDING_REVIEW = "pending_review"


class Severity(str, Enum):
    """Уровни серьезности"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RequirementCategory(str, Enum):
    """Категории требований (ISO 22301)"""
    GOVERNANCE = "governance"  # Clauses 4-5-6
    RISK_MANAGEMENT = "risk_management"  # Clause 8.2.3
    BUSINESS_CONTINUITY = "business_continuity"  # Clause 8.3-8.4
    INCIDENT_MANAGEMENT = "incident_management"  # Clause 8.4.2
    DOCUMENTATION = "documentation"  # Clause 7.5
    TRAINING = "training"  # Clause 7.2
    MONITORING = "monitoring"  # Clause 9.1
    AUDIT = "audit"  # Clause 9.2
    IMPROVEMENT = "improvement"  # Clause 10
    TESTING = "testing"  # Clause 8.5


class EvidenceType(str, Enum):
    """Типы свидетельств"""
    POLICY = "policy"
    PROCEDURE = "procedure"
    PLAN = "plan"
    RECORD = "record"
    REPORT = "report"
    CERTIFICATE = "certificate"
    TRAINING_RECORD = "training_record"
    EXERCISE_REPORT = "exercise_report"
    MEETING_MINUTES = "meeting_minutes"
    AUDIT_REPORT = "audit_report"
    ASSESSMENT = "assessment"
    OTHER = "other"


class AssessmentType(str, Enum):
    """Типы оценок"""
    REGULAR = "regular"
    SELF = "self_assessment"
    PRE_AUDIT = "pre_audit"
    POST_INCIDENT = "post_incident"
    POST_EXERCISE = "post_exercise"


class GapPriority(str, Enum):
    """Приоритеты пробелов"""
    P1_CRITICAL = "p1_critical"  # Блокер для сертификации
    P2_HIGH = "p2_high"  # Высокий риск
    P3_MEDIUM = "p3_medium"  # Средний риск
    P4_LOW = "p4_low"  # Низкий риск


class NCType(str, Enum):
    """Типы несоответствий"""
    MAJOR = "major"  # Отсутствие или полный сбой процесса
    MINOR = "minor"  # Изолированный лапсус
    OBSERVATION = "observation"  # Потенциал для улучшения


class NCSource(str, Enum):
    """Источник обнаружения NC"""
    INTERNAL_AUDIT = "internal_audit"
    EXTERNAL_AUDIT = "external_audit"
    MANAGEMENT_REVIEW = "management_review"
    INCIDENT = "incident"
    EXERCISE = "exercise"
    MONITORING = "monitoring"
    SELF_ASSESSMENT = "self_assessment"


class AuditType(str, Enum):
    """Типы аудитов"""
    INTERNAL = "internal"
    EXTERNAL = "external"
    SURVEILLANCE = "surveillance"
    CERTIFICATION = "certification"
    RECERTIFICATION = "recertification"


class AuditResult(str, Enum):
    """Результаты аудита"""
    PASS = "pass"
    CONDITIONAL_PASS = "conditional_pass"
    FAIL = "fail"
    PENDING = "pending"


class RCAMethod(str, Enum):
    """Методы Root Cause Analysis"""
    FIVE_WHYS = "5_whys"
    FISHBONE = "fishbone"
    FAULT_TREE = "fault_tree"
    PARETO = "pareto"
    BARRIER_ANALYSIS = "barrier_analysis"
