"""
SQLAlchemy Database Models for Compliance Module

All models use async SQLAlchemy 2.0 declarative style.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from shared.database.base import Base


class ComplianceRequirementModel(Base):
    """ISO 22301 Compliance Requirements"""
    __tablename__ = "compliance_requirements"

    __table_args__ = (
        # Tenant isolation + standard filtering
        Index('ix_req_tenant_standard', 'tenant_id', 'standard'),
        # Tenant isolation + category filtering
        Index('ix_req_tenant_category', 'tenant_id', 'category'),
        # Tenant isolation + active requirements
        Index('ix_req_tenant_active', 'tenant_id', 'is_active'),
        # Standard + category for compliance overview
        Index('ix_req_standard_category', 'standard', 'category'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(String(255), nullable=False, index=True)

    # Requirement details
    standard = Column(String(50), nullable=False)  # iso_22301, iso_27001, etc. (indexed in composite)
    clause = Column(String(20), nullable=False)  # e.g., "4.1", "8.2.2"
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)  # governance, risk_management, etc. (indexed in composite)

    # Importance
    weight = Column(Float, nullable=False, default=1.0)
    is_mandatory = Column(Boolean, nullable=False, default=True)

    # Evidence requirements
    evidence_types = Column(JSON, nullable=True)  # List of required evidence types
    min_evidence_count = Column(Integer, nullable=False, default=1)

    # Metadata
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    created_by = Column(String(255), nullable=True)

    # Relationships
    evidence = relationship("EvidenceModel", back_populates="requirement")
    gaps = relationship("GapModel", back_populates="requirement")


class EvidenceModel(Base):
    """Evidence for Compliance Requirements"""
    __tablename__ = "compliance_evidence"

    __table_args__ = (
        # Tenant isolation + status filtering
        Index('ix_evidence_tenant_status', 'tenant_id', 'status'),
        # Tenant isolation + verification status
        Index('ix_evidence_tenant_verification', 'tenant_id', 'verification_status'),
        # Tenant isolation + creation date (descending)
        Index('ix_evidence_tenant_created_desc', 'tenant_id', 'created_at'),
        # Evidence type filtering
        Index('ix_evidence_type', 'evidence_type'),
        # Reviewer workload queries
        Index('ix_evidence_reviewer', 'reviewer_id', 'status'),
        # Validity period expiration queries
        Index('ix_evidence_validity_end', 'validity_period_end'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(String(255), nullable=False, index=True)
    requirement_id = Column(UUID(as_uuid=True), ForeignKey("compliance_requirements.id"), nullable=False, index=True)

    # Document info
    document_id = Column(UUID(as_uuid=True), nullable=True)  # Link to document service
    document_reference = Column(String(500), nullable=True)
    evidence_type = Column(String(100), nullable=False)  # policy, procedure, record, etc.

    # Content
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    # Validity
    validity_period_start = Column(DateTime, nullable=True)
    validity_period_end = Column(DateTime, nullable=True)

    # Workflow status
    status = Column(String(50), nullable=False, default="draft")  # draft, submitted, under_review, verified, rejected, archived (indexed in composite)
    verification_status = Column(String(50), nullable=True)  # verified, expired, invalid (indexed in composite)
    verified_by = Column(String(255), nullable=True)
    verified_at = Column(DateTime, nullable=True)

    # Review
    reviewer_id = Column(String(255), nullable=True)
    review_started_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Metadata
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)  # indexed in composite
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow, index=True)
    created_by = Column(String(255), nullable=True)

    # Concurrency control
    version = Column(Integer, nullable=False, default=1)

    # Relationships
    requirement = relationship("ComplianceRequirementModel", back_populates="evidence")


class AssessmentModel(Base):
    """Compliance Assessments"""
    __tablename__ = "compliance_assessments"

    __table_args__ = (
        # Tenant isolation + status filtering
        Index('ix_assessment_tenant_status', 'tenant_id', 'status'),
        # Tenant isolation + standard filtering
        Index('ix_assessment_tenant_standard', 'tenant_id', 'standard'),
        # Tenant isolation + completion date (descending)
        Index('ix_assessment_tenant_completed', 'tenant_id', 'completion_date'),
        # Assessor workload queries
        Index('ix_assessment_assessor_status', 'assessor_id', 'status'),
        # Reviewer workload queries
        Index('ix_assessment_reviewer_status', 'reviewer_id', 'status'),
        # Completion date for reporting
        Index('ix_assessment_completed', 'completion_date'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(String(255), nullable=False, index=True)

    # Assessment details
    standard = Column(String(50), nullable=False)  # indexed in composite
    assessment_type = Column(String(50), nullable=False, default="regular")  # regular, self, pre_audit, etc.
    scope = Column(Text, nullable=True)
    scope_clauses = Column(JSON, nullable=True)  # List of clause IDs in scope

    # Planning
    planned_date = Column(DateTime, nullable=True)

    # Workflow status
    status = Column(String(50), nullable=False, default="draft")  # draft, in_progress, under_review, approved, completed (indexed in composite)
    assessor_id = Column(String(255), nullable=True)
    reviewer_id = Column(String(255), nullable=True)

    # Execution
    start_date = Column(DateTime, nullable=True)
    review_date = Column(DateTime, nullable=True)
    completion_date = Column(DateTime, nullable=True)  # indexed in composite

    # Results
    overall_score = Column(Float, nullable=True)  # 0-100
    compliance_status = Column(String(50), nullable=True)  # compliant, partial_compliance, non_compliant
    requirements_assessed = Column(JSON, nullable=True)  # Detailed results per requirement
    gaps_identified = Column(JSON, nullable=True)  # Summary of gaps
    recommendations = Column(JSON, nullable=True)

    # Comments
    assessment_comment = Column(Text, nullable=True)
    approval_comment = Column(Text, nullable=True)
    approved_by = Column(String(255), nullable=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow, index=True)
    created_by = Column(String(255), nullable=True)

    # Concurrency control
    version = Column(Integer, nullable=False, default=1)

    # Relationships
    gaps = relationship("GapModel", back_populates="assessment")


class GapModel(Base):
    """Compliance Gaps"""
    __tablename__ = "compliance_gaps"

    __table_args__ = (
        # Tenant isolation + severity filtering
        Index('ix_gap_tenant_severity', 'tenant_id', 'severity'),
        # Tenant isolation + status filtering
        Index('ix_gap_tenant_status', 'tenant_id', 'status'),
        # Tenant isolation + due date for deadline tracking
        Index('ix_gap_tenant_due_date', 'tenant_id', 'due_date'),
        # Assignment tracking
        Index('ix_gap_assigned_to_status', 'assigned_to', 'status'),
        # Due date for deadline queries (all tenants)
        Index('ix_gap_due_date', 'due_date'),
        # Severity for prioritization
        Index('ix_gap_severity_status', 'severity', 'status'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(String(255), nullable=False, index=True)
    requirement_id = Column(UUID(as_uuid=True), ForeignKey("compliance_requirements.id"), nullable=False, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("compliance_assessments.id"), nullable=True, index=True)

    # Gap details
    gap_description = Column(Text, nullable=False)
    severity = Column(String(50), nullable=False)  # critical, high, medium, low (indexed in composite)
    priority = Column(String(50), nullable=True)  # p1_critical, p2_high, p3_medium, p4_low

    # Coverage
    current_coverage = Column(Float, nullable=True)  # 0-100%
    target_coverage = Column(Float, nullable=False, default=100.0)

    # Workflow status
    status = Column(String(50), nullable=False, default="identified")  # identified, assigned, in_progress, resolved, verified, closed, risk_accepted (indexed in composite)

    # Impact
    impact_score = Column(Float, nullable=True)

    # Remediation
    remediation_actions = Column(JSON, nullable=True)  # List of actions
    estimated_effort = Column(String(100), nullable=True)  # "2-4 weeks", etc.
    assigned_to = Column(String(255), nullable=True)  # indexed in composite
    due_date = Column(DateTime, nullable=True)  # indexed in composite

    # Resolution
    resolution_description = Column(Text, nullable=True)
    resolved_by = Column(String(255), nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    # Verification
    evidence_id = Column(UUID(as_uuid=True), nullable=True)
    verification_comment = Column(Text, nullable=True)
    verified_by = Column(String(255), nullable=True)
    verified_at = Column(DateTime, nullable=True)

    # Risk acceptance
    risk_acceptance_justification = Column(Text, nullable=True)
    accepted_by = Column(String(255), nullable=True)
    risk_owner = Column(String(255), nullable=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow, index=True)
    created_by = Column(String(255), nullable=True)

    # Concurrency control
    version = Column(Integer, nullable=False, default=1)

    # Relationships
    requirement = relationship("ComplianceRequirementModel", back_populates="gaps")
    assessment = relationship("AssessmentModel", back_populates="gaps")


class NonconformityModel(Base):
    """Nonconformities (ISO 10.1)"""
    __tablename__ = "compliance_nonconformities"

    __table_args__ = (
        # Tenant isolation + NC type and status filtering
        Index('ix_nc_tenant_type_status', 'tenant_id', 'nc_type', 'status'),
        # Tenant isolation + status filtering
        Index('ix_nc_tenant_status', 'tenant_id', 'status'),
        # Tenant isolation + identification date (descending)
        Index('ix_nc_tenant_identified_desc', 'tenant_id', 'identified_date'),
        # RCA lead workload queries
        Index('ix_nc_rca_lead_status', 'rca_lead', 'status'),
        # RCA method analysis
        Index('ix_nc_rca_method', 'rca_method'),
        # Audit relationship
        Index('ix_nc_audit_id', 'audit_id'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(String(255), nullable=False, index=True)
    nc_number = Column(String(100), nullable=False, unique=True, index=True)

    # Links
    requirement_id = Column(UUID(as_uuid=True), ForeignKey("compliance_requirements.id"), nullable=True)
    audit_id = Column(UUID(as_uuid=True), ForeignKey("compliance_audits.id"), nullable=True)  # indexed in composite

    # NC details
    nc_type = Column(String(50), nullable=False)  # major, minor, observation (indexed in composite)
    source = Column(String(50), nullable=False)  # internal_audit, external_audit, incident, etc.
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    identified_by = Column(String(255), nullable=False)
    identified_date = Column(DateTime, nullable=False)  # indexed in composite

    # Workflow status
    status = Column(String(50), nullable=False, default="identified")  # identified, rca_in_progress, actions_planned, actions_implemented, verification, closed (indexed in composite)

    # Root Cause Analysis
    rca_lead = Column(String(255), nullable=True)
    rca_team = Column(JSON, nullable=True)  # List of user IDs
    rca_method = Column(String(50), nullable=True)  # 5_whys, fishbone, etc.
    rca_started_at = Column(DateTime, nullable=True)
    rca_completed_at = Column(DateTime, nullable=True)
    root_causes = Column(JSON, nullable=True)  # List of root causes

    # Corrective Actions
    corrective_actions = Column(JSON, nullable=True)  # List of actions
    actions_completed_at = Column(DateTime, nullable=True)

    # Verification
    evidence_ids = Column(JSON, nullable=True)  # List of evidence IDs
    verifier_id = Column(String(255), nullable=True)
    verification_requested_at = Column(DateTime, nullable=True)
    verification_result = Column(String(50), nullable=True)  # effective, not_effective
    effectiveness_confirmed = Column(Boolean, nullable=True)
    verified_by = Column(String(255), nullable=True)
    verified_at = Column(DateTime, nullable=True)

    # Closure
    closed_at = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow, index=True)
    created_by = Column(String(255), nullable=True)

    # Concurrency control
    version = Column(Integer, nullable=False, default=1)


class AuditModel(Base):
    """Audits (ISO 9.2)"""
    __tablename__ = "compliance_audits"

    __table_args__ = (
        # Tenant isolation + audit status
        Index('ix_audit_tenant_status', 'tenant_id', 'status'),
        # Tenant isolation + audit type
        Index('ix_audit_tenant_type', 'tenant_id', 'audit_type'),
        # Tenant isolation + standard
        Index('ix_audit_tenant_standard', 'tenant_id', 'standard'),
        # Planned date for scheduling
        Index('ix_audit_planned_date', 'planned_date'),
        # Auditor queries
        Index('ix_audit_auditor_status', 'auditor_name', 'status'),
        # Certification expiry tracking
        Index('ix_audit_cert_expiry', 'certification_valid_until'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(String(255), nullable=False, index=True)
    audit_number = Column(String(100), nullable=False, unique=True, index=True)

    # Audit details
    audit_type = Column(String(50), nullable=False)  # internal, external, surveillance, certification (indexed in composite)
    standard = Column(String(50), nullable=False)  # indexed in composite
    scope = Column(Text, nullable=True)
    scope_clauses = Column(JSON, nullable=True)

    # Planning
    planned_date = Column(DateTime, nullable=True)  # indexed in composite
    planned_by = Column(String(255), nullable=True)

    # Workflow status
    status = Column(String(50), nullable=False, default="planned")  # planned, preparation, in_progress, report_draft, completed, closed (indexed in composite)

    # Execution
    actual_date = Column(DateTime, nullable=True)
    completion_date = Column(DateTime, nullable=True)

    # Auditor
    auditor_name = Column(String(255), nullable=True)
    auditor_organization = Column(String(255), nullable=True)
    auditor_independent = Column(Boolean, nullable=False, default=True)

    # Preparation
    preparation_lead = Column(String(255), nullable=True)
    audit_package_generated = Column(Boolean, nullable=False, default=False)
    audit_package_url = Column(String(500), nullable=True)

    # Findings
    findings = Column(JSON, nullable=True)  # List of findings
    nc_ids = Column(JSON, nullable=True)  # List of NC IDs created from audit

    # Results
    overall_result = Column(String(50), nullable=True)  # pass, conditional_pass, fail, pending
    audit_report_url = Column(String(500), nullable=True)

    # Certification
    certification_valid_until = Column(DateTime, nullable=True)
    next_surveillance_date = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow, index=True)
    created_by = Column(String(255), nullable=True)

    # Concurrency control
    version = Column(Integer, nullable=False, default=1)

    # Relationships
    nonconformities = relationship("NonconformityModel", back_populates="audit")


# Add back_populates for NC → Audit relationship
NonconformityModel.audit = relationship("AuditModel", back_populates="nonconformities")
