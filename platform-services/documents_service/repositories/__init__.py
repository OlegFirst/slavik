"""
Repositories Package - Data Access Layer
"""

from .repository import (
    DocumentRepository,
    DocumentAccessRepository,
    DocumentShareRepository,
    DocumentApprovalRepository,
    DocumentTagRepository,
    DocumentComparisonRepository,
    RetentionPolicyRepository,
)

__all__ = [
    "DocumentRepository",
    "DocumentAccessRepository",
    "DocumentShareRepository",
    "DocumentApprovalRepository",
    "DocumentTagRepository",
    "DocumentComparisonRepository",
    "RetentionPolicyRepository",
]
