"""
Document Repository - Data Access Layer
Handles all database operations for documents service

Based on: BCM/documents/main.py database operations
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, func, desc

from models.database import (
    Document, DocumentAccess, DocumentShare, DocumentApproval,
    DocumentTag, DocumentTagAssociation, DocumentComparison,
    DocumentRetentionPolicy,
    DocumentType, DocumentStatus, DocumentClassification,
    AccessAction, SharePermission, ApprovalStatus
)


class DocumentRepository:
    """Repository for Document operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, document: Document) -> Document:
        """Create a new document"""
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def get_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID"""
        result = await self.db.execute(
            select(Document).where(Document.document_id == document_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, document_code: str) -> Optional[Document]:
        """Get document by code"""
        result = await self.db.execute(
            select(Document).where(Document.document_code == document_code)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        tenant_id: str,
        document_type: Optional[DocumentType] = None,
        status: Optional[DocumentStatus] = None,
        classification: Optional[DocumentClassification] = None,
        owner_id: Optional[str] = None,
        department: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Document]:
        """List documents with filtering"""
        query = select(Document).where(
            and_(
                Document.tenant_id == tenant_id,
                Document.is_latest == True
            )
        )

        # Apply filters
        if document_type:
            query = query.where(Document.document_type == document_type)
        if status:
            query = query.where(Document.status == status)
        if classification:
            query = query.where(Document.classification == classification)
        if owner_id:
            query = query.where(Document.owner_id == owner_id)
        if department:
            query = query.where(Document.department == department)
        if search:
            query = query.where(
                or_(
                    Document.title.ilike(f'%{search}%'),
                    Document.description.ilike(f'%{search}%'),
                    Document.document_code.ilike(f'%{search}%')
                )
            )

        # Order and paginate
        query = query.order_by(desc(Document.updated_at)).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(
        self,
        tenant_id: str,
        document_type: Optional[DocumentType] = None,
        status: Optional[DocumentStatus] = None
    ) -> int:
        """Count documents"""
        query = select(func.count()).select_from(Document).where(
            and_(
                Document.tenant_id == tenant_id,
                Document.is_latest == True
            )
        )

        if document_type:
            query = query.where(Document.document_type == document_type)
        if status:
            query = query.where(Document.status == status)

        result = await self.db.execute(query)
        return result.scalar()

    async def update(self, document: Document) -> Document:
        """Update document"""
        document.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def delete(self, document_id: int) -> bool:
        """Soft delete document"""
        document = await self.get_by_id(document_id)
        if document:
            document.status = DocumentStatus.ARCHIVED
            document.archived_at = datetime.utcnow()
            await self.update(document)
            return True
        return False

    async def get_versions(self, document_code: str) -> List[Document]:
        """Get all versions of a document"""
        result = await self.db.execute(
            select(Document)
            .where(Document.document_code == document_code)
            .order_by(desc(Document.created_at))
        )
        return list(result.scalars().all())


class DocumentAccessRepository:
    """Repository for DocumentAccess (audit log) operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_access(
        self,
        document_id: int,
        user_id: str,
        action_type: AccessAction,
        changes_made: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> DocumentAccess:
        """Log document access"""
        log_entry = DocumentAccess(
            document_id=document_id,
            user_id=user_id,
            action_type=action_type,
            changes_made=changes_made,
            reason=reason,
            ip_address=ip_address
        )
        self.db.add(log_entry)
        await self.db.commit()
        await self.db.refresh(log_entry)
        return log_entry

    async def get_document_log(
        self,
        document_id: int,
        action_type: Optional[AccessAction] = None,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[DocumentAccess]:
        """Get access log for document"""
        query = select(DocumentAccess).where(
            DocumentAccess.document_id == document_id
        )

        if action_type:
            query = query.where(DocumentAccess.action_type == action_type)
        if user_id:
            query = query.where(DocumentAccess.user_id == user_id)

        query = query.order_by(desc(DocumentAccess.accessed_at)).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())


class DocumentShareRepository:
    """Repository for DocumentShare operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, share: DocumentShare) -> DocumentShare:
        """Create document share"""
        self.db.add(share)
        await self.db.commit()
        await self.db.refresh(share)
        return share

    async def get_by_id(self, share_id: int) -> Optional[DocumentShare]:
        """Get share by ID"""
        result = await self.db.execute(
            select(DocumentShare).where(DocumentShare.share_id == share_id)
        )
        return result.scalar_one_or_none()

    async def get_document_shares(self, document_id: int) -> List[DocumentShare]:
        """Get all shares for a document"""
        result = await self.db.execute(
            select(DocumentShare).where(DocumentShare.document_id == document_id)
        )
        return list(result.scalars().all())

    async def deactivate(self, share_id: int) -> bool:
        """Deactivate a share"""
        share = await self.get_by_id(share_id)
        if share:
            share.is_active = False
            await self.db.commit()
            return True
        return False


class DocumentApprovalRepository:
    """Repository for DocumentApproval operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, approval: DocumentApproval) -> DocumentApproval:
        """Create approval request"""
        self.db.add(approval)
        await self.db.commit()
        await self.db.refresh(approval)
        return approval

    async def get_by_id(self, approval_id: int) -> Optional[DocumentApproval]:
        """Get approval by ID"""
        result = await self.db.execute(
            select(DocumentApproval).where(DocumentApproval.approval_id == approval_id)
        )
        return result.scalar_one_or_none()

    async def get_document_approvals(self, document_id: int) -> List[DocumentApproval]:
        """Get all approvals for a document"""
        result = await self.db.execute(
            select(DocumentApproval).where(DocumentApproval.document_id == document_id)
        )
        return list(result.scalars().all())

    async def update(self, approval: DocumentApproval) -> DocumentApproval:
        """Update approval"""
        await self.db.commit()
        await self.db.refresh(approval)
        return approval


class DocumentTagRepository:
    """Repository for DocumentTag operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, tag: DocumentTag) -> DocumentTag:
        """Create tag"""
        self.db.add(tag)
        await self.db.commit()
        await self.db.refresh(tag)
        return tag

    async def get_by_id(self, tag_id: int) -> Optional[DocumentTag]:
        """Get tag by ID"""
        result = await self.db.execute(
            select(DocumentTag).where(DocumentTag.tag_id == tag_id)
        )
        return result.scalar_one_or_none()

    async def list(self, tenant_id: str, tag_type: Optional[str] = None) -> List[DocumentTag]:
        """List tags for tenant"""
        query = select(DocumentTag).where(DocumentTag.tenant_id == tenant_id)

        if tag_type:
            query = query.where(DocumentTag.tag_type == tag_type)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def add_to_document(
        self,
        document_id: int,
        tag_id: int,
        applied_by: str,
        confidence_score: Optional[float] = None
    ) -> DocumentTagAssociation:
        """Add tag to document"""
        association = DocumentTagAssociation(
            document_id=document_id,
            tag_id=tag_id,
            applied_by=applied_by,
            confidence_score=confidence_score
        )
        self.db.add(association)

        # Increment tag usage count
        tag = await self.get_by_id(tag_id)
        if tag:
            tag.usage_count += 1

        await self.db.commit()
        await self.db.refresh(association)
        return association


class DocumentComparisonRepository:
    """Repository for DocumentComparison operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, comparison: DocumentComparison) -> DocumentComparison:
        """Create comparison"""
        self.db.add(comparison)
        await self.db.commit()
        await self.db.refresh(comparison)
        return comparison

    async def get_by_id(self, comparison_id: int) -> Optional[DocumentComparison]:
        """Get comparison by ID"""
        result = await self.db.execute(
            select(DocumentComparison).where(DocumentComparison.comparison_id == comparison_id)
        )
        return result.scalar_one_or_none()

    async def get_comparisons(
        self,
        source_id: Optional[int] = None,
        target_id: Optional[int] = None
    ) -> List[DocumentComparison]:
        """Get comparisons for documents"""
        query = select(DocumentComparison)

        if source_id:
            query = query.where(DocumentComparison.source_document_id == source_id)
        if target_id:
            query = query.where(DocumentComparison.target_document_id == target_id)

        result = await self.db.execute(query)
        return list(result.scalars().all())


class RetentionPolicyRepository:
    """Repository for DocumentRetentionPolicy operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, policy: DocumentRetentionPolicy) -> DocumentRetentionPolicy:
        """Create retention policy"""
        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)
        return policy

    async def get_by_id(self, policy_id: int) -> Optional[DocumentRetentionPolicy]:
        """Get policy by ID"""
        result = await self.db.execute(
            select(DocumentRetentionPolicy).where(DocumentRetentionPolicy.policy_id == policy_id)
        )
        return result.scalar_one_or_none()

    async def list(self, tenant_id: str, is_active: Optional[bool] = True) -> List[DocumentRetentionPolicy]:
        """List retention policies for tenant"""
        query = select(DocumentRetentionPolicy).where(
            DocumentRetentionPolicy.tenant_id == tenant_id
        )

        if is_active is not None:
            query = query.where(DocumentRetentionPolicy.is_active == is_active)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, policy: DocumentRetentionPolicy) -> DocumentRetentionPolicy:
        """Update retention policy"""
        policy.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(policy)
        return policy
