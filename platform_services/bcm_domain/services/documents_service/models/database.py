"""
Documents Module Database Models
ISO 22301 Clause 7.5 - Documented Information

Implements 8 core models:
- Document: Main document entity with lifecycle management
- DocumentAccess: Audit trail for all document interactions
- DocumentShare: Document sharing and collaboration
- DocumentApproval: Approval workflow tracking
- DocumentTag: Taxonomy and categorization
- DocumentTagAssociation: Many-to-many relationship
- DocumentComparison: Version comparison and diff tracking
- DocumentRetentionPolicy: Compliance and retention rules

Based on: BCM_1 document_processor-обьедененный + document_management
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean,
    ForeignKey, JSON, Enum as SQLEnum, Index, UniqueConstraint,
    Float, BigInteger
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Import shared Base
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))
from shared.database import Base


# ============================================================================
# ENUMS
# ============================================================================

class DocumentType(str, PyEnum):
    """Document type classification"""
    # ISO 22301 Core Documents
    POLICY = "policy"                           # 5.2, 5.3
    PROCEDURE = "procedure"                     # 8.1, 8.4
    PLAN = "plan"                               # 8.4
    RISK_ASSESSMENT = "risk_assessment"         # 8.2.3
    BIA = "bia"                                 # 8.2
    EXERCISE_REPORT = "exercise_report"         # 8.5
    AUDIT_REPORT = "audit_report"               # 9.2
    MANAGEMENT_REVIEW = "management_review"     # 9.3

    # Supporting Documents
    FORM = "form"
    TEMPLATE = "template"
    CHECKLIST = "checklist"
    CONTACT_LIST = "contact_list"
    COMMUNICATION = "communication"
    TRAINING_MATERIAL = "training_material"
    EVIDENCE = "evidence"
    CONTRACT = "contract"
    SOP = "sop"

    # General
    REPORT = "report"
    PRESENTATION = "presentation"
    SPREADSHEET = "spreadsheet"
    OTHER = "other"


class DocumentStatus(str, PyEnum):
    """Document lifecycle status"""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"
    OBSOLETE = "obsolete"


class DocumentClassification(str, PyEnum):
    """Security classification"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    HIGHLY_RESTRICTED = "highly_restricted"


class AccessAction(str, PyEnum):
    """Audit trail action types"""
    CREATED = "created"
    UPDATED = "updated"
    VIEWED = "viewed"
    DOWNLOADED = "downloaded"
    SHARED = "shared"
    DELETED = "deleted"
    RESTORED = "restored"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    VERSION_CREATED = "version_created"


class SharePermission(str, PyEnum):
    """Document sharing permissions"""
    VIEW = "view"
    COMMENT = "comment"
    EDIT = "edit"
    ADMIN = "admin"


class ApprovalStatus(str, PyEnum):
    """Approval workflow status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    RECALLED = "recalled"


class TagType(str, PyEnum):
    """Tag categorization"""
    ISO_CLAUSE = "iso_clause"           # ISO 22301 clause mapping
    BCI_PRACTICE = "bci_practice"       # BCI GPG mapping
    DEPARTMENT = "department"
    PROCESS = "process"
    RISK_CATEGORY = "risk_category"
    KEYWORD = "keyword"
    CUSTOM = "custom"


class RetentionTrigger(str, PyEnum):
    """Retention policy trigger"""
    CREATION_DATE = "creation_date"
    APPROVAL_DATE = "approval_date"
    PUBLICATION_DATE = "publication_date"
    LAST_MODIFIED = "last_modified"
    CUSTOM_DATE = "custom_date"


# ============================================================================
# MODEL 1: DOCUMENT (Main Entity)
# ============================================================================

class Document(Base):
    """
    Main document entity with full lifecycle management.

    Based on:
    - BCM_1/document_management/main.py (lines 70-142)
    - BCM_1/document_processor-обьедененный/models/document.py (lines 12-89)

    Covers:
    - ISO 22301 Clause 7.5 (Documented Information)
    - Version control and change tracking
    - Multi-tenant isolation
    - AI/ML metadata enrichment
    - Full-text search support
    """
    __tablename__ = "documents"
    __table_args__ = (
        Index('idx_tenant_status', 'tenant_id', 'status'),
        Index('idx_tenant_type', 'tenant_id', 'document_type'),
        Index('idx_created_at', 'created_at'),
        Index('idx_expiration_date', 'expiration_date'),
        Index('idx_next_review_date', 'next_review_date'),
        {'schema': 'documents'}
    )

    # Primary Key
    document_id = Column(Integer, primary_key=True, index=True)

    # Multi-tenancy
    tenant_id = Column(String(100), nullable=False, index=True)

    # Document Identification
    document_code = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    document_type = Column(SQLEnum(DocumentType), nullable=False)

    # Version Control
    version = Column(String(20), default='1.0', nullable=False)
    parent_id = Column(Integer, ForeignKey('documents.documents.document_id'), nullable=True)
    is_latest = Column(Boolean, default=True, nullable=False)
    version_notes = Column(Text)

    # Lifecycle
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.DRAFT, nullable=False)

    # File Information
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(1000), nullable=False)  # S3/local path
    file_size = Column(BigInteger)  # bytes
    file_type = Column(String(50))  # pdf, docx, xlsx, etc.
    mime_type = Column(String(100))
    file_hash = Column(String(64))  # SHA-256 for integrity

    # Content Extraction (from document_processor.py)
    extracted_text = Column(Text)  # Full text extraction
    page_count = Column(Integer)
    word_count = Column(Integer)

    # AI/ML Metadata (from document_processor.py lines 347-428)
    ai_summary = Column(Text)  # OpenAI generated summary
    key_phrases = Column(JSON)  # TF-IDF extracted phrases
    named_entities = Column(JSON)  # spaCy NER: {"PERSON": [], "ORG": [], "DATE": []}
    iso_clauses = Column(JSON)  # Mapped ISO 22301 clauses: ["4.1", "5.2"]
    bci_practices = Column(JSON)  # Mapped BCI GPG practices: ["PP1", "PP5"]
    compliance_frameworks = Column(JSON)  # ["ISO 22301", "HIPAA"]

    # Classification & Security
    classification = Column(SQLEnum(DocumentClassification),
                          default=DocumentClassification.INTERNAL)
    is_controlled = Column(Boolean, default=False)  # ISO controlled document
    requires_approval = Column(Boolean, default=False)

    # Ownership & Responsibility
    owner_id = Column(String(100), nullable=False, index=True)  # User ID
    created_by = Column(String(100), nullable=False)
    department = Column(String(100))
    process_area = Column(String(100))

    # Dates
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = Column(DateTime)
    published_at = Column(DateTime)
    archived_at = Column(DateTime)

    # Review & Retention (ISO 22301 requirement)
    review_frequency_days = Column(Integer, default=365)  # Annual review
    next_review_date = Column(DateTime)
    last_reviewed_at = Column(DateTime)
    last_reviewed_by = Column(String(100))

    retention_years = Column(Integer, default=7)  # ISO default
    expiration_date = Column(DateTime)
    is_permanent = Column(Boolean, default=False)

    # Search & Discovery
    tags = Column(JSON)  # Quick tags: ["bcm", "crisis", "plan"]
    custom_metadata = Column(JSON)  # Flexible additional fields

    # Relationships
    children = relationship("Document",
                          backref="parent",
                          remote_side=[document_id])
    access_logs = relationship("DocumentAccess", back_populates="document")
    shares = relationship("DocumentShare", back_populates="document")
    approvals = relationship("DocumentApproval", back_populates="document")
    tag_associations = relationship("DocumentTagAssociation", back_populates="document")
    comparisons_as_source = relationship("DocumentComparison",
                                        foreign_keys="DocumentComparison.source_document_id",
                                        back_populates="source_document")
    comparisons_as_target = relationship("DocumentComparison",
                                        foreign_keys="DocumentComparison.target_document_id",
                                        back_populates="target_document")

    def __repr__(self):
        return f"<Document {self.document_code} v{self.version} - {self.title[:50]}>"


# ============================================================================
# MODEL 2: DOCUMENT ACCESS (Audit Trail)
# ============================================================================

class DocumentAccess(Base):
    """
    Complete audit trail for document interactions.

    Based on:
    - BCM_1/document_management/main.py (lines 143-157)

    Covers:
    - ISO 22301 Clause 7.5.3 (Control of documented information)
    - HIPAA audit requirements
    - Security compliance
    """
    __tablename__ = "document_access"
    __table_args__ = (
        Index('idx_document_accessed', 'document_id', 'accessed_at'),
        Index('idx_user_accessed', 'user_id', 'accessed_at'),
        Index('idx_action_type', 'action_type', 'accessed_at'),
        {'schema': 'documents'}
    )

    # Primary Key
    access_id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    document_id = Column(Integer, ForeignKey('documents.documents.document_id'), nullable=False)

    # Access Information
    user_id = Column(String(100), nullable=False, index=True)
    action_type = Column(SQLEnum(AccessAction), nullable=False)

    # Audit Details
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    location = Column(String(200))  # Geographic location if available

    # Context
    changes_made = Column(JSON)  # {"field": "status", "old": "draft", "new": "approved"}
    reason = Column(Text)  # For approval/rejection

    # Timestamp
    accessed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationship
    document = relationship("Document", back_populates="access_logs")

    def __repr__(self):
        return f"<DocumentAccess {self.action_type} by {self.user_id} at {self.accessed_at}>"


# ============================================================================
# MODEL 3: DOCUMENT SHARE (Collaboration)
# ============================================================================

class DocumentShare(Base):
    """
    Document sharing and collaboration tracking.

    Based on:
    - BCM_1/document_management/main.py (lines 159-180)

    Covers:
    - Controlled distribution
    - Permission management
    - Time-limited access
    """
    __tablename__ = "document_shares"
    __table_args__ = (
        Index('idx_document_shared', 'document_id', 'shared_at'),
        Index('idx_recipient', 'shared_with_user_id', 'is_active'),
        UniqueConstraint('document_id', 'shared_with_user_id', name='uq_doc_user_share'),
        {'schema': 'documents'}
    )

    # Primary Key
    share_id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    document_id = Column(Integer, ForeignKey('documents.documents.document_id'), nullable=False)

    # Sharing Information
    shared_by_user_id = Column(String(100), nullable=False)
    shared_with_user_id = Column(String(100), nullable=False, index=True)
    shared_with_email = Column(String(255))  # For external shares

    # Permissions
    permission_level = Column(SQLEnum(SharePermission), default=SharePermission.VIEW)
    can_reshare = Column(Boolean, default=False)

    # Access Control
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)  # Time-limited access

    # Tracking
    shared_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    accessed_at = Column(DateTime)  # First access
    last_accessed_at = Column(DateTime)  # Most recent access
    access_count = Column(Integer, default=0)

    # Notes
    share_message = Column(Text)

    # Relationship
    document = relationship("Document", back_populates="shares")

    def __repr__(self):
        return f"<DocumentShare {self.document_id} → {self.shared_with_user_id} ({self.permission_level})>"


# ============================================================================
# MODEL 4: DOCUMENT APPROVAL (Workflow)
# ============================================================================

class DocumentApproval(Base):
    """
    Approval workflow tracking for controlled documents.

    Based on:
    - BCM_1/document_management/main.py (lines 182-205)

    Covers:
    - ISO 22301 controlled document approval
    - Multi-stage approval chains
    - Rejection and rework tracking
    """
    __tablename__ = "document_approvals"
    __table_args__ = (
        Index('idx_document_approval', 'document_id', 'approval_status'),
        Index('idx_approver', 'approver_id', 'approval_status'),
        Index('idx_approval_stage', 'approval_stage', 'approval_status'),
        {'schema': 'documents'}
    )

    # Primary Key
    approval_id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    document_id = Column(Integer, ForeignKey('documents.documents.document_id'), nullable=False)

    # Approval Chain
    approval_stage = Column(Integer, default=1)  # Multi-stage: 1, 2, 3...
    approver_id = Column(String(100), nullable=False, index=True)
    approver_role = Column(String(100))  # "Technical Reviewer", "Management Approval"

    # Status
    approval_status = Column(SQLEnum(ApprovalStatus),
                            default=ApprovalStatus.PENDING,
                            nullable=False)

    # Decision
    decision_notes = Column(Text)
    suggested_changes = Column(JSON)  # [{"section": "3.2", "comment": "Add detail"}]

    # Dates
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    responded_at = Column(DateTime)
    due_date = Column(DateTime)

    # Notifications
    reminder_sent = Column(Boolean, default=False)
    reminder_sent_at = Column(DateTime)

    # Relationship
    document = relationship("Document", back_populates="approvals")

    def __repr__(self):
        return f"<DocumentApproval {self.document_id} Stage {self.approval_stage} - {self.approval_status}>"


# ============================================================================
# MODEL 5: DOCUMENT TAG (Taxonomy)
# ============================================================================

class DocumentTag(Base):
    """
    Tag taxonomy for document organization and discovery.

    Based on:
    - BCM_1/document_processor/document_processor.py (lines 513-546)

    Covers:
    - ISO 22301 clause mapping
    - BCI GPG practice mapping
    - Department/process organization
    - Custom taxonomies
    """
    __tablename__ = "document_tags"
    __table_args__ = (
        UniqueConstraint('tenant_id', 'tag_name', 'tag_type', name='uq_tenant_tag'),
        Index('idx_tag_type', 'tag_type'),
        {'schema': 'documents'}
    )

    # Primary Key
    tag_id = Column(Integer, primary_key=True, index=True)

    # Multi-tenancy
    tenant_id = Column(String(100), nullable=False, index=True)

    # Tag Information
    tag_name = Column(String(100), nullable=False)
    tag_type = Column(SQLEnum(TagType), nullable=False)

    # Hierarchy (for nested tags)
    parent_tag_id = Column(Integer, ForeignKey('documents.document_tags.tag_id'), nullable=True)

    # Metadata
    description = Column(Text)
    color = Column(String(7))  # Hex color: #FF5733
    icon = Column(String(50))  # Icon identifier

    # Standards Mapping
    iso_clause = Column(String(10))  # "7.5.3" for ISO tags
    bci_practice = Column(String(10))  # "PP5" for BCI tags

    # Usage Tracking
    usage_count = Column(Integer, default=0)  # How many documents use this tag

    # Dates
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(100))

    # Relationships
    children = relationship("DocumentTag",
                          backref="parent",
                          remote_side=[tag_id])
    document_associations = relationship("DocumentTagAssociation", back_populates="tag")

    def __repr__(self):
        return f"<DocumentTag {self.tag_name} ({self.tag_type})>"


# ============================================================================
# MODEL 6: DOCUMENT TAG ASSOCIATION (Many-to-Many)
# ============================================================================

class DocumentTagAssociation(Base):
    """
    Many-to-many relationship between documents and tags.

    Based on:
    - BCM_1/document_processor/document_processor.py (lines 548-565)
    """
    __tablename__ = "document_tag_associations"
    __table_args__ = (
        UniqueConstraint('document_id', 'tag_id', name='uq_doc_tag'),
        Index('idx_doc_tags', 'document_id'),
        Index('idx_tag_docs', 'tag_id'),
        {'schema': 'documents'}
    )

    # Primary Key
    association_id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    document_id = Column(Integer, ForeignKey('documents.documents.document_id'), nullable=False)
    tag_id = Column(Integer, ForeignKey('documents.document_tags.tag_id'), nullable=False)

    # Association Metadata
    applied_by = Column(String(100))  # User or "AI"
    confidence_score = Column(Float)  # 0.0-1.0 for AI-applied tags
    is_verified = Column(Boolean, default=False)  # Human-verified AI tag

    # Dates
    applied_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="tag_associations")
    tag = relationship("DocumentTag", back_populates="document_associations")

    def __repr__(self):
        return f"<DocumentTagAssociation doc:{self.document_id} ↔ tag:{self.tag_id}>"


# ============================================================================
# MODEL 7: DOCUMENT COMPARISON (Version Diff)
# ============================================================================

class DocumentComparison(Base):
    """
    Document version comparison and diff tracking.

    Based on:
    - BCM_1/document-processor/models.py (lines 87-125)

    Covers:
    - Version control and change tracking
    - Automated diff generation
    - Change summary for reviews
    """
    __tablename__ = "document_comparisons"
    __table_args__ = (
        Index('idx_source_target', 'source_document_id', 'target_document_id'),
        Index('idx_compared_at', 'compared_at'),
        {'schema': 'documents'}
    )

    # Primary Key
    comparison_id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    source_document_id = Column(Integer,
                               ForeignKey('documents.documents.document_id'),
                               nullable=False)
    target_document_id = Column(Integer,
                               ForeignKey('documents.documents.document_id'),
                               nullable=False)

    # Comparison Metadata
    comparison_type = Column(String(50))  # "version_diff", "similar_content"

    # Diff Results (from document_processor/services/comparator.py lines 45-102)
    similarity_score = Column(Float)  # 0.0-1.0
    text_added = Column(Integer)  # Characters added
    text_removed = Column(Integer)  # Characters removed
    text_modified = Column(Integer)  # Characters modified

    # Detailed Diff
    diff_json = Column(JSON)  # Structured diff: [{"op": "add", "line": 45, "text": "..."}]
    changes_summary = Column(Text)  # Human-readable summary

    # Structural Changes
    sections_added = Column(JSON)  # ["3.4 New Section"]
    sections_removed = Column(JSON)  # ["2.1 Old Section"]
    sections_modified = Column(JSON)  # ["1.2 Updated Section"]

    # Metadata Changes
    metadata_changes = Column(JSON)  # {"owner": {"old": "A", "new": "B"}}

    # Execution
    compared_by = Column(String(100))
    compared_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processing_time_ms = Column(Integer)  # Performance tracking

    # Relationships
    source_document = relationship("Document",
                                  foreign_keys=[source_document_id],
                                  back_populates="comparisons_as_source")
    target_document = relationship("Document",
                                  foreign_keys=[target_document_id],
                                  back_populates="comparisons_as_target")

    def __repr__(self):
        return f"<DocumentComparison {self.source_document_id}→{self.target_document_id} ({self.similarity_score:.2f})>"


# ============================================================================
# MODEL 8: DOCUMENT RETENTION POLICY (Compliance)
# ============================================================================

class DocumentRetentionPolicy(Base):
    """
    Document retention policies for compliance.

    Based on:
    - BCM_1/document_management/main.py (lines 207-235)

    Covers:
    - ISO 22301 retention requirements (3-7 years)
    - HIPAA requirements (6+ years)
    - Automated archival and destruction
    - Legal holds
    """
    __tablename__ = "document_retention_policies"
    __table_args__ = (
        UniqueConstraint('tenant_id', 'policy_name', name='uq_tenant_policy'),
        Index('idx_document_type', 'document_type'),
        {'schema': 'documents'}
    )

    # Primary Key
    policy_id = Column(Integer, primary_key=True, index=True)

    # Multi-tenancy
    tenant_id = Column(String(100), nullable=False, index=True)

    # Policy Identification
    policy_name = Column(String(200), nullable=False)
    description = Column(Text)

    # Scope
    document_type = Column(SQLEnum(DocumentType))  # NULL = applies to all types
    department = Column(String(100))  # NULL = applies to all departments
    classification = Column(SQLEnum(DocumentClassification))  # NULL = all classifications

    # Retention Rules
    retention_years = Column(Integer, nullable=False)
    is_permanent = Column(Boolean, default=False)

    # Trigger
    trigger_type = Column(SQLEnum(RetentionTrigger),
                         default=RetentionTrigger.CREATION_DATE,
                         nullable=False)

    # Actions
    archive_after_days = Column(Integer)  # Move to archive storage
    destroy_after_days = Column(Integer)  # Permanent deletion
    require_review_before_destruction = Column(Boolean, default=True)

    # Legal Hold
    allow_legal_hold = Column(Boolean, default=True)
    legal_hold_contact = Column(String(200))  # Who to notify for holds

    # Compliance Frameworks
    compliance_frameworks = Column(JSON)  # ["ISO 22301", "HIPAA"]
    regulatory_requirements = Column(Text)  # Legal citations

    # Policy Metadata
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=100)  # Higher priority wins if multiple match

    # Dates
    effective_from = Column(DateTime, nullable=False)
    effective_until = Column(DateTime)  # NULL = indefinite
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(100), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<DocumentRetentionPolicy {self.policy_name} ({self.retention_years}y)>"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_expiration_date(
    retention_policy: DocumentRetentionPolicy,
    trigger_date: datetime
) -> Optional[datetime]:
    """
    Calculate document expiration date based on retention policy.

    Args:
        retention_policy: The applicable retention policy
        trigger_date: The date that triggers retention calculation

    Returns:
        Expiration datetime or None if permanent retention
    """
    if retention_policy.is_permanent:
        return None

    years = retention_policy.retention_years
    expiration = trigger_date + timedelta(days=years * 365)

    return expiration


def get_applicable_retention_policy(
    tenant_id: str,
    document: Document,
    policies: List[DocumentRetentionPolicy]
) -> Optional[DocumentRetentionPolicy]:
    """
    Find the most specific applicable retention policy for a document.

    Priority order (highest to lowest):
    1. Type + Department + Classification match
    2. Type + Department match
    3. Type + Classification match
    4. Type match
    5. Department match
    6. Classification match
    7. Global policy (no filters)

    Args:
        tenant_id: Tenant identifier
        document: Document to find policy for
        policies: List of active retention policies

    Returns:
        Most specific applicable policy or None
    """
    # Filter to active policies for this tenant
    active_policies = [
        p for p in policies
        if p.tenant_id == tenant_id
        and p.is_active
        and p.effective_from <= datetime.utcnow()
        and (p.effective_until is None or p.effective_until >= datetime.utcnow())
    ]

    # Calculate specificity score for each policy
    scored_policies = []
    for policy in active_policies:
        score = 0

        # Check if policy matches document
        if policy.document_type and policy.document_type != document.document_type:
            continue
        if policy.department and policy.department != document.department:
            continue
        if policy.classification and policy.classification != document.classification:
            continue

        # Calculate specificity score
        if policy.document_type:
            score += 100
        if policy.department:
            score += 10
        if policy.classification:
            score += 1

        # Add priority
        score += policy.priority

        scored_policies.append((score, policy))

    if not scored_policies:
        return None

    # Return highest scoring policy
    scored_policies.sort(key=lambda x: x[0], reverse=True)
    return scored_policies[0][1]
