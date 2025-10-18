"""
Pydantic Domain Models for Documents Service
API Request/Response schemas

Based on: BCM/documents/main.py Pydantic models (lines 193-273)
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr

from .database import (
    DocumentType, DocumentStatus, DocumentClassification,
    SharePermission, ApprovalStatus, TagType, RetentionTrigger
)


# ============================================================================
# DOCUMENT SCHEMAS
# ============================================================================

class DocumentCreate(BaseModel):
    """Create document request"""
    tenant_id: str
    title: str
    description: Optional[str] = None
    document_type: DocumentType
    classification: DocumentClassification = DocumentClassification.INTERNAL
    is_controlled: bool = False
    requires_approval: bool = False
    owner_id: str
    department: Optional[str] = None
    process_area: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_metadata: Optional[Dict[str, Any]] = None


class DocumentUpdate(BaseModel):
    """Update document request"""
    title: Optional[str] = None
    description: Optional[str] = None
    document_type: Optional[DocumentType] = None
    classification: Optional[DocumentClassification] = None
    department: Optional[str] = None
    process_area: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(BaseModel):
    """Document response"""
    document_id: int
    tenant_id: str
    document_code: str
    title: str
    description: Optional[str]
    document_type: DocumentType
    version: str
    status: DocumentStatus
    classification: DocumentClassification
    owner_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentDetailResponse(BaseModel):
    """Detailed document response with all fields"""
    document_id: int
    tenant_id: str
    document_code: str
    title: str
    description: Optional[str]
    document_type: DocumentType
    version: str
    status: DocumentStatus
    classification: DocumentClassification

    # File information
    file_name: str
    file_size: Optional[int]
    file_type: Optional[str]
    page_count: Optional[int]
    word_count: Optional[int]

    # Ownership
    owner_id: str
    department: Optional[str]
    process_area: Optional[str]

    # Metadata
    tags: Optional[List[str]]
    iso_clauses: Optional[List[str]]
    bci_practices: Optional[List[str]]

    # Dates
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime]
    published_at: Optional[datetime]
    archived_at: Optional[datetime]

    # Retention
    retention_years: Optional[int]
    expiration_date: Optional[datetime]
    is_permanent: bool

    class Config:
        from_attributes = True


# ============================================================================
# SHARING SCHEMAS
# ============================================================================

class DocumentShareCreate(BaseModel):
    """Create document share"""
    shared_with_user_id: Optional[str] = None
    shared_with_email: Optional[EmailStr] = None
    permission_level: SharePermission = SharePermission.VIEW
    can_reshare: bool = False
    expires_at: Optional[datetime] = None
    share_message: Optional[str] = None


class DocumentShareResponse(BaseModel):
    """Document share response"""
    share_id: int
    document_id: int
    shared_by_user_id: str
    shared_with_user_id: Optional[str]
    shared_with_email: Optional[str]
    permission_level: SharePermission
    can_reshare: bool
    is_active: bool
    expires_at: Optional[datetime]
    shared_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# APPROVAL SCHEMAS
# ============================================================================

class ApprovalRequestCreate(BaseModel):
    """Create approval request"""
    approver_id: str
    approver_role: str
    sla_hours: int = 48
    notes: Optional[str] = None


class ApprovalResponse(BaseModel):
    """Approval response"""
    approval_id: int
    document_id: int
    approval_stage: int
    approver_id: str
    approver_role: str
    approval_status: ApprovalStatus
    decision_notes: Optional[str]
    requested_at: datetime
    responded_at: Optional[datetime]
    due_date: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# RETENTION SCHEMAS
# ============================================================================

class RetentionPolicyCreate(BaseModel):
    """Create retention policy"""
    tenant_id: str
    policy_name: str
    description: Optional[str] = None
    document_type: Optional[DocumentType] = None
    department: Optional[str] = None
    classification: Optional[DocumentClassification] = None
    retention_years: int
    is_permanent: bool = False
    trigger_type: RetentionTrigger = RetentionTrigger.CREATION_DATE
    archive_after_days: Optional[int] = None
    destroy_after_days: Optional[int] = None
    require_review_before_destruction: bool = True
    compliance_frameworks: Optional[List[str]] = None


class RetentionPolicyResponse(BaseModel):
    """Retention policy response"""
    policy_id: int
    tenant_id: str
    policy_name: str
    description: Optional[str]
    document_type: Optional[DocumentType]
    department: Optional[str]
    classification: Optional[DocumentClassification]
    retention_years: int
    is_permanent: bool
    trigger_type: RetentionTrigger
    archive_after_days: Optional[int]
    destroy_after_days: Optional[int]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# TAG SCHEMAS
# ============================================================================

class TagCreate(BaseModel):
    """Create tag"""
    tenant_id: str
    tag_name: str
    tag_type: TagType
    description: Optional[str] = None
    color: Optional[str] = None
    parent_tag_id: Optional[int] = None


class TagResponse(BaseModel):
    """Tag response"""
    tag_id: int
    tenant_id: str
    tag_name: str
    tag_type: TagType
    description: Optional[str]
    color: Optional[str]
    usage_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# WORKFLOW SCHEMAS
# ============================================================================

class WorkflowActionRequest(BaseModel):
    """Execute workflow action"""
    user_id: str
    notes: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class WorkflowStatusResponse(BaseModel):
    """Workflow status response"""
    current_state: str
    available_actions: List[str]
    checks: Dict[str, Any]
    is_controlled: bool
    requires_approval: bool


# ============================================================================
# COMPARISON SCHEMAS
# ============================================================================

class DocumentComparisonRequest(BaseModel):
    """Document comparison request"""
    source_id: int
    target_id: int


class DocumentComparisonResponse(BaseModel):
    """Document comparison response"""
    comparison_id: int
    source_document_id: int
    target_document_id: int
    similarity_score: float
    text_added: int
    text_removed: int
    text_modified: int
    changes_summary: Optional[str]
    compared_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# LIST/PAGINATION SCHEMAS
# ============================================================================

class DocumentListResponse(BaseModel):
    """Paginated document list response"""
    items: List[DocumentResponse]
    total: int
    skip: int
    limit: int


class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(0, ge=0)
    limit: int = Field(50, ge=1, le=100)
