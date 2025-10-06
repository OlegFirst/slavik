"""
Integrations Package for Documents Service

Cross-module integration helpers for Plans, Governance, and Validation modules.
"""

from .plans import (
    get_plan_documents,
    get_plan_documents_by_code,
    get_plan_template_documents,
    check_plan_document_completeness,
    link_document_to_plan,
    unlink_document_from_plan,
    get_plan_document_status,
    PLAN_TEMPLATE_DOCUMENTS,
)

from .governance import (
    get_policy_documents,
    get_policy_document_by_code,
    get_policy_documentation_requirements,
    check_policy_compliance_documentation,
    link_document_to_policy,
    get_iso_clause_coverage,
    POLICY_REQUIRED_DOCUMENTS,
)

from .validation import (
    create_exercise_report_document,
    get_exercise_reports,
    get_audit_evidence_documents,
    link_document_to_audit,
    create_audit_report_document,
    create_management_review_document,
    get_validation_documents_summary,
)

__all__ = [
    # Plans
    'get_plan_documents',
    'get_plan_documents_by_code',
    'get_plan_template_documents',
    'check_plan_document_completeness',
    'link_document_to_plan',
    'unlink_document_from_plan',
    'get_plan_document_status',
    'PLAN_TEMPLATE_DOCUMENTS',

    # Governance
    'get_policy_documents',
    'get_policy_document_by_code',
    'get_policy_documentation_requirements',
    'check_policy_compliance_documentation',
    'link_document_to_policy',
    'get_iso_clause_coverage',
    'POLICY_REQUIRED_DOCUMENTS',

    # Validation
    'create_exercise_report_document',
    'get_exercise_reports',
    'get_audit_evidence_documents',
    'link_document_to_audit',
    'create_audit_report_document',
    'create_management_review_document',
    'get_validation_documents_summary',
]
