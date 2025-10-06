"""
Models Package - Documents Service
"""

# Database models
from .database import (
    Base,
    Document,
    DocumentAccess,
    DocumentShare,
    DocumentApproval,
    DocumentTag,
    DocumentTagAssociation,
    DocumentComparison,
    DocumentRetentionPolicy,
    # Enums
    DocumentType,
    DocumentStatus,
    DocumentClassification,
    AccessAction,
    SharePermission,
    ApprovalStatus,
    TagType,
    RetentionTrigger,
    # Helper functions
    calculate_expiration_date,
    get_applicable_retention_policy,
)

# Domain/Pydantic models
from .domain import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentDetailResponse,
    DocumentShareCreate,
    DocumentShareResponse,
    ApprovalRequestCreate,
    ApprovalResponse,
    RetentionPolicyCreate,
    RetentionPolicyResponse,
    TagCreate,
    TagResponse,
    WorkflowActionRequest,
    WorkflowStatusResponse,
    DocumentComparisonRequest,
    DocumentComparisonResponse,
    DocumentListResponse,
    PaginationParams,
)

__all__ = [
    # Database models
    "Base",
    "Document",
    "DocumentAccess",
    "DocumentShare",
    "DocumentApproval",
    "DocumentTag",
    "DocumentTagAssociation",
    "DocumentComparison",
    "DocumentRetentionPolicy",
    # Enums
    "DocumentType",
    "DocumentStatus",
    "DocumentClassification",
    "AccessAction",
    "SharePermission",
    "ApprovalStatus",
    "TagType",
    "RetentionTrigger",
    # Functions
    "calculate_expiration_date",
    "get_applicable_retention_policy",
    # Domain models
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentResponse",
    "DocumentDetailResponse",
    "DocumentShareCreate",
    "DocumentShareResponse",
    "ApprovalRequestCreate",
    "ApprovalResponse",
    "RetentionPolicyCreate",
    "RetentionPolicyResponse",
    "TagCreate",
    "TagResponse",
    "WorkflowActionRequest",
    "WorkflowStatusResponse",
    "DocumentComparisonRequest",
    "DocumentComparisonResponse",
    "DocumentListResponse",
    "PaginationParams",
]
