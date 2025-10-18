"""
Document Service - Business Logic Layer
Handles document lifecycle and processing operations

Based on: BCM/documents/main.py business logic
"""

import hashlib
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import Document, DocumentStatus, DocumentType, AccessAction
from models.domain import DocumentCreate, DocumentUpdate
from repositories.repository import DocumentRepository, DocumentAccessRepository
from core.extractor import DocumentExtractor, clean_extracted_text
from core.classifier import DocumentClassifier
from core.analyzer import DocumentAnalyzer


class DocumentService:
    """Service for document operations"""

    def __init__(
        self,
        db: AsyncSession,
        storage_path: str,
        max_file_size: int,
        openai_api_key: Optional[str] = None
    ):
        self.db = db
        self.storage_path = storage_path
        self.max_file_size = max_file_size

        # Initialize processors
        self.extractor = DocumentExtractor()
        self.classifier = DocumentClassifier()
        self.analyzer = DocumentAnalyzer(openai_api_key=openai_api_key)

        # Repositories
        self.doc_repo = DocumentRepository(db)
        self.access_repo = DocumentAccessRepository(db)

    async def create_document(self, doc_data: DocumentCreate) -> Document:
        """Create a new document (metadata only)"""
        # Generate unique document code
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        doc_code = f"DOC-{doc_data.tenant_id[:4].upper()}-{timestamp}"

        # Create document
        new_doc = Document(
            tenant_id=doc_data.tenant_id,
            document_code=doc_code,
            title=doc_data.title,
            description=doc_data.description,
            document_type=doc_data.document_type,
            classification=doc_data.classification,
            is_controlled=doc_data.is_controlled,
            requires_approval=doc_data.requires_approval,
            owner_id=doc_data.owner_id,
            created_by=doc_data.owner_id,
            department=doc_data.department,
            process_area=doc_data.process_area,
            tags=doc_data.tags or [],
            custom_metadata=doc_data.custom_metadata or {},
            status=DocumentStatus.DRAFT,
            version='1.0',
            is_latest=True,
            file_name='',
            file_path='',
        )

        document = await self.doc_repo.create(new_doc)

        # Log access
        await self.access_repo.log_access(
            document_id=document.document_id,
            user_id=doc_data.owner_id,
            action_type=AccessAction.CREATED
        )

        return document

    async def upload_file(
        self,
        document_id: int,
        file: UploadFile,
        user_id: str,
        auto_process: bool = True
    ) -> Tuple[Document, Dict[str, Any]]:
        """Upload file for document and optionally process it"""
        # Get document
        document = await self.doc_repo.get_by_id(document_id)
        if not document:
            raise ValueError("Document not found")

        # Read and validate file
        content = await file.read()
        file_size = len(content)

        if file_size > self.max_file_size:
            raise ValueError(
                f"File too large. Maximum size is {self.max_file_size / 1024 / 1024}MB"
            )

        # Calculate file hash
        file_hash = hashlib.sha256(content).hexdigest()

        # Determine storage path
        tenant_dir = Path(self.storage_path) / document.tenant_id
        tenant_dir.mkdir(parents=True, exist_ok=True)

        file_path = tenant_dir / f"{document.document_code}_{file.filename}"

        # Save file
        with open(file_path, 'wb') as f:
            f.write(content)

        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file.filename)

        # Update document
        document.file_name = file.filename
        document.file_path = str(file_path)
        document.file_size = file_size
        document.file_type = Path(file.filename).suffix.lower().lstrip('.')
        document.mime_type = mime_type
        document.file_hash = file_hash

        # Auto-process if requested
        processing_result = {}
        if auto_process:
            processing_result = await self._process_document(document, str(file_path))

        document = await self.doc_repo.update(document)

        # Log access
        await self.access_repo.log_access(
            document_id=document.document_id,
            user_id=user_id,
            action_type=AccessAction.UPDATED,
            changes_made={'action': 'file_uploaded', 'filename': file.filename}
        )

        return document, processing_result

    async def _process_document(self, document: Document, file_path: str) -> Dict[str, Any]:
        """Auto-process document: extract, classify, analyze"""
        result = {
            'extraction_success': False,
            'classification_success': False,
            'analysis_success': False
        }

        try:
            # Extract text
            extraction_result = self.extractor.extract(file_path)

            if extraction_result.get('success'):
                extracted_text = extraction_result.get('text', '')
                document.extracted_text = clean_extracted_text(extracted_text)
                document.page_count = extraction_result.get('page_count')
                document.word_count = extraction_result.get('word_count')
                result['extraction_success'] = True

                # Classify document
                classification_result = self.classifier.classify(
                    text=document.extracted_text,
                    title=document.title
                )

                # Update classification (if confidence high enough)
                if classification_result['type_confidence'] >= 0.7:
                    document.document_type = classification_result['document_type']
                    document.classification = classification_result['suggested_classification']

                document.iso_clauses = classification_result['iso_clauses']
                document.bci_practices = classification_result['bci_practices']
                document.is_controlled = classification_result['is_controlled']
                document.requires_approval = classification_result['requires_approval']

                if classification_result['department']:
                    document.department = classification_result['department']
                if classification_result['process_area']:
                    document.process_area = classification_result['process_area']

                result['classification_success'] = True
                result['classification'] = classification_result

                # Analyze with NLP
                analysis_result = self.analyzer.analyze(
                    text=document.extracted_text[:50000],  # Limit text
                    extract_entities=True,
                    extract_keywords=True,
                    summarize=bool(self.analyzer.openai_client),
                    analyze_readability=True
                )

                document.named_entities = analysis_result.get('entities', {})
                document.key_phrases = analysis_result.get('key_phrases', [])[:20]
                document.ai_summary = analysis_result.get('summary')

                result['analysis_success'] = True
                result['analysis'] = {
                    'entities_count': len(analysis_result.get('entities', {})),
                    'key_phrases_count': len(analysis_result.get('key_phrases', [])),
                    'has_summary': bool(analysis_result.get('summary'))
                }

        except Exception as e:
            result['error'] = str(e)

        return result

    async def get_document(self, document_id: int, user_id: str) -> Document:
        """Get document by ID"""
        document = await self.doc_repo.get_by_id(document_id)
        if not document:
            raise ValueError("Document not found")

        # Log access
        await self.access_repo.log_access(
            document_id=document.document_id,
            user_id=user_id,
            action_type=AccessAction.VIEWED
        )

        return document

    async def update_document(
        self,
        document_id: int,
        updates: DocumentUpdate,
        user_id: str
    ) -> Document:
        """Update document metadata"""
        document = await self.doc_repo.get_by_id(document_id)
        if not document:
            raise ValueError("Document not found")

        # Track changes
        changes = {}

        # Update fields
        if updates.title is not None:
            changes['title'] = {'old': document.title, 'new': updates.title}
            document.title = updates.title

        if updates.description is not None:
            changes['description'] = {'old': document.description, 'new': updates.description}
            document.description = updates.description

        if updates.document_type is not None:
            changes['document_type'] = {'old': document.document_type, 'new': updates.document_type}
            document.document_type = updates.document_type

        if updates.classification is not None:
            changes['classification'] = {'old': document.classification, 'new': updates.classification}
            document.classification = updates.classification

        if updates.department is not None:
            document.department = updates.department

        if updates.process_area is not None:
            document.process_area = updates.process_area

        if updates.tags is not None:
            document.tags = updates.tags

        if updates.custom_metadata is not None:
            document.custom_metadata = updates.custom_metadata

        document = await self.doc_repo.update(document)

        # Log access
        await self.access_repo.log_access(
            document_id=document.document_id,
            user_id=user_id,
            action_type=AccessAction.UPDATED,
            changes_made=changes
        )

        return document

    async def delete_document(
        self,
        document_id: int,
        user_id: str,
        reason: Optional[str] = None
    ) -> bool:
        """Soft delete document"""
        document = await self.doc_repo.get_by_id(document_id)
        if not document:
            raise ValueError("Document not found")

        # Update status to archived (soft delete)
        document.status = DocumentStatus.ARCHIVED
        document.archived_at = datetime.utcnow()
        await self.doc_repo.update(document)

        # Log access
        await self.access_repo.log_access(
            document_id=document.document_id,
            user_id=user_id,
            action_type=AccessAction.DELETED,
            reason=reason
        )

        return True

    async def create_new_version(
        self,
        document_id: int,
        user_id: str,
        version_notes: Optional[str] = None
    ) -> Document:
        """Create new version of document"""
        old_doc = await self.doc_repo.get_by_id(document_id)
        if not old_doc:
            raise ValueError("Document not found")

        # Parse version and increment
        version_parts = old_doc.version.split('.')
        major = int(version_parts[0])
        minor = int(version_parts[1]) if len(version_parts) > 1 else 0
        new_version = f"{major}.{minor + 1}"

        # Mark old version as not latest
        old_doc.is_latest = False
        await self.doc_repo.update(old_doc)

        # Create new version
        new_doc = Document(
            tenant_id=old_doc.tenant_id,
            document_code=old_doc.document_code,
            title=old_doc.title,
            description=old_doc.description,
            document_type=old_doc.document_type,
            version=new_version,
            parent_id=old_doc.document_id,
            is_latest=True,
            version_notes=version_notes,
            status=DocumentStatus.DRAFT,
            file_name=old_doc.file_name,
            file_path=old_doc.file_path,
            file_size=old_doc.file_size,
            file_type=old_doc.file_type,
            mime_type=old_doc.mime_type,
            file_hash=old_doc.file_hash,
            classification=old_doc.classification,
            is_controlled=old_doc.is_controlled,
            requires_approval=old_doc.requires_approval,
            owner_id=old_doc.owner_id,
            created_by=user_id,
            department=old_doc.department,
            process_area=old_doc.process_area,
            tags=old_doc.tags,
            custom_metadata=old_doc.custom_metadata,
        )

        new_doc = await self.doc_repo.create(new_doc)

        # Log access
        await self.access_repo.log_access(
            document_id=new_doc.document_id,
            user_id=user_id,
            action_type=AccessAction.VERSION_CREATED
        )

        return new_doc

    async def list_documents(
        self,
        tenant_id: str,
        status: Optional[DocumentStatus] = None,
        doc_type: Optional[DocumentType] = None,
        category: Optional[DocumentClassification] = None,
        tags: Optional[list] = None,
        search: Optional[str] = None,
        owner_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        department: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Dict[str, Any]:
        """List documents with filtering"""
        documents = await self.doc_repo.list(
            tenant_id=tenant_id,
            document_type=doc_type,
            status=status,
            classification=category,
            owner_id=owner_id,
            department=department,
            search=search,
            skip=skip,
            limit=limit
        )

        total = await self.doc_repo.count(
            tenant_id=tenant_id,
            document_type=doc_type,
            status=status
        )

        return {
            "items": documents,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    async def get_document_for_download(
        self,
        document_id: int,
        user_id: str
    ) -> Tuple[Document, str]:
        """Get document for download and return document + file path"""
        document = await self.doc_repo.get_by_id(document_id)
        if not document:
            raise ValueError("Document not found")

        if not document.file_path or not Path(document.file_path).exists():
            raise ValueError("Document file not found")

        # Log access
        await self.access_repo.log_access(
            document_id=document.document_id,
            user_id=user_id,
            action_type=AccessAction.DOWNLOADED
        )

        return document, document.file_path

    async def execute_workflow_action(
        self,
        document_id: int,
        action: str,
        user_id: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute workflow action on document"""
        from workflows.lifecycle_workflow import DocumentLifecycleAction, execute_lifecycle_transition

        document = await self.doc_repo.get_by_id(document_id)
        if not document:
            raise ValueError("Document not found")

        # Execute transition
        success, error, transition_data = execute_lifecycle_transition(
            document=document,
            action=DocumentLifecycleAction(action),
            user_id=user_id,
            notes=notes
        )

        if not success:
            raise ValueError(error)

        # Update document status
        document.status = DocumentStatus(transition_data['new_state'])

        # Update dates based on action
        if 'approved_at' in transition_data:
            document.approved_at = datetime.utcnow()
        if 'published_at' in transition_data:
            document.published_at = datetime.utcnow()
        if 'archived_at' in transition_data:
            document.archived_at = datetime.utcnow()

        await self.doc_repo.update(document)

        # Log access
        await self.access_repo.log_access(
            document_id=document.document_id,
            user_id=user_id,
            action_type=AccessAction(action),
            reason=notes
        )

        return {
            "document_id": document.document_id,
            "previous_status": transition_data['previous_state'],
            "new_status": transition_data['new_state'],
            "action": action,
            "performed_at": transition_data['performed_at']
        }

    async def get_workflow_status(self, document_id: int) -> Dict[str, Any]:
        """Get workflow status for document"""
        from workflows.lifecycle_workflow import get_workflow_summary

        document = await self.doc_repo.get_by_id(document_id)
        if not document:
            raise ValueError("Document not found")

        return get_workflow_summary(document)

    async def get_document_versions(self, document_code: str) -> Dict[str, Any]:
        """Get all versions of a document"""
        versions = await self.doc_repo.get_versions(document_code)

        if not versions:
            raise ValueError("Document not found")

        current = next((v for v in versions if v.is_latest), versions[0])

        return {
            "document_code": document_code,
            "current_version": current.version,
            "total_versions": len(versions),
            "versions": versions
        }

    async def compare_documents(
        self,
        source_id: int,
        target_id: int,
        user_id: str
    ) -> Dict[str, Any]:
        """Compare two document versions"""
        from core.comparator import DocumentComparator
        from repositories.repository import DocumentComparisonRepository

        source_doc = await self.doc_repo.get_by_id(source_id)
        target_doc = await self.doc_repo.get_by_id(target_id)

        if not source_doc or not target_doc:
            raise ValueError("One or both documents not found")

        # Compare
        comparator = DocumentComparator()
        comparison_result = comparator.compare(
            source_text=source_doc.extracted_text or '',
            target_text=target_doc.extracted_text or '',
            source_metadata={
                'title': source_doc.title,
                'version': source_doc.version,
                'owner': source_doc.owner_id,
            },
            target_metadata={
                'title': target_doc.title,
                'version': target_doc.version,
                'owner': target_doc.owner_id,
            }
        )

        # Save comparison
        comp_repo = DocumentComparisonRepository(self.db)
        comparison = DocumentComparison(
            source_document_id=source_id,
            target_document_id=target_id,
            comparison_type='version_diff',
            similarity_score=comparison_result['similarity_score'],
            text_added=comparison_result['text_added'],
            text_removed=comparison_result['text_removed'],
            text_modified=comparison_result['text_modified'],
            diff_json=comparison_result['diff'][:1000],
            changes_summary=comparison_result['changes_summary'],
            structural_changes=comparison_result.get('structural_changes', {}),
            metadata_changes=comparison_result.get('metadata_changes', {}),
            compared_by=user_id,
            compared_at=datetime.utcnow()
        )

        await comp_repo.create(comparison)

        return comparison_result

    async def share_document(
        self,
        document_id: int,
        recipient_id: Optional[str],
        recipient_name: Optional[str],
        permission_level: SharePermission,
        expiry_date: Optional[datetime],
        user_id: str,
        can_reshare: bool = False,
        share_message: Optional[str] = None
    ) -> DocumentShare:
        """Share document with user"""
        from repositories.repository import DocumentShareRepository

        document = await self.doc_repo.get_by_id(document_id)
        if not document:
            raise ValueError("Document not found")

        if not recipient_id and not recipient_name:
            raise ValueError("Must provide recipient_id or recipient_name")

        share_repo = DocumentShareRepository(self.db)
        share = DocumentShare(
            document_id=document_id,
            shared_by_user_id=user_id,
            shared_with_user_id=recipient_id,
            shared_with_email=recipient_name,
            permission_level=permission_level,
            can_reshare=can_reshare,
            expires_at=expiry_date,
            share_message=share_message,
            is_active=True
        )

        share = await share_repo.create(share)

        # Log access
        await self.access_repo.log_access(
            document_id=document_id,
            user_id=user_id,
            action_type=AccessAction.SHARED
        )

        return share

    async def get_document_shares(self, document_id: int) -> list:
        """Get all shares for a document"""
        from repositories.repository import DocumentShareRepository

        share_repo = DocumentShareRepository(self.db)
        return await share_repo.get_document_shares(document_id)

    async def request_approval(
        self,
        document_id: int,
        approver_id: str,
        approver_name: str,
        notes: Optional[str],
        user_id: str,
        sla_hours: int = 72
    ) -> Dict[str, Any]:
        """Request document approval"""
        from repositories.repository import DocumentApprovalRepository
        from workflows.approval_workflow import (
            calculate_approval_priority, calculate_approval_due_date
        )

        document = await self.doc_repo.get_by_id(document_id)
        if not document:
            raise ValueError("Document not found")

        approval_repo = DocumentApprovalRepository(self.db)

        # Calculate priority and due date
        priority = calculate_approval_priority(document)
        due_date = calculate_approval_due_date(
            requested_at=datetime.utcnow(),
            sla_hours=sla_hours
        )

        # Create approval request
        approval = DocumentApproval(
            document_id=document_id,
            approval_stage=1,
            approver_id=approver_id,
            approver_role=approver_name,
            approval_status=ApprovalStatus.PENDING,
            decision_notes=notes,
            requested_at=datetime.utcnow(),
            due_date=due_date
        )

        approval = await approval_repo.create(approval)

        return {
            "approval_id": approval.approval_id,
            "approver_id": approval.approver_id,
            "due_date": approval.due_date,
            "priority": priority.value,
            "message": "Approval requested successfully"
        }

    async def respond_to_approval(
        self,
        approval_id: int,
        action: str,
        notes: Optional[str],
        user_id: str
    ) -> Dict[str, Any]:
        """Respond to approval request"""
        from repositories.repository import DocumentApprovalRepository
        from workflows.approval_workflow import (
            ApprovalWorkflowAction, execute_approval_transition
        )

        approval_repo = DocumentApprovalRepository(self.db)
        approval = await approval_repo.get_by_id(approval_id)

        if not approval:
            raise ValueError("Approval request not found")

        # Execute approval transition
        success, error, transition_data = execute_approval_transition(
            approval=approval,
            action=ApprovalWorkflowAction(action),
            user_id=user_id,
            notes=notes
        )

        if not success:
            raise ValueError(error)

        # Update approval
        approval.approval_status = ApprovalStatus(transition_data['new_state'])
        approval.decision_notes = notes
        approval.responded_at = datetime.utcnow()

        await approval_repo.update(approval)

        return {
            "approval_id": approval.approval_id,
            "action": action,
            "status": approval.approval_status.value,
            "message": f"Approval {action} successfully"
        }

    async def get_document_approvals(self, document_id: int) -> Dict[str, Any]:
        """Get all approval requests for document"""
        from repositories.repository import DocumentApprovalRepository
        from workflows.approval_workflow import get_approval_workflow_summary

        document = await self.doc_repo.get_by_id(document_id)
        if not document:
            raise ValueError("Document not found")

        approval_repo = DocumentApprovalRepository(self.db)
        approvals = await approval_repo.get_document_approvals(document_id)
        summary = get_approval_workflow_summary(document, list(approvals))

        return {
            "approvals": approvals,
            "workflow_summary": summary
        }

    async def create_retention_policy(
        self,
        policy_data: Dict[str, Any],
        user_id: str
    ) -> DocumentRetentionPolicy:
        """Create document retention policy"""
        from repositories.repository import RetentionPolicyRepository

        policy_repo = RetentionPolicyRepository(self.db)

        policy = DocumentRetentionPolicy(
            tenant_id=policy_data['tenant_id'],
            policy_name=policy_data['policy_name'],
            description=policy_data.get('description'),
            document_type=policy_data.get('document_type'),
            department=policy_data.get('department'),
            classification=policy_data.get('classification'),
            retention_years=policy_data['retention_years'],
            is_permanent=policy_data.get('is_permanent', False),
            trigger_type=policy_data['trigger_type'],
            archive_after_days=policy_data.get('archive_after_days'),
            destroy_after_days=policy_data.get('destroy_after_days'),
            require_review_before_destruction=policy_data.get('require_review_before_destruction', True),
            compliance_frameworks=policy_data.get('compliance_frameworks', []),
            is_active=True,
            effective_from=datetime.utcnow(),
            created_by=user_id
        )

        return await policy_repo.create(policy)

    async def list_retention_policies(
        self,
        tenant_id: str,
        is_active: Optional[bool] = True
    ) -> list:
        """List retention policies for tenant"""
        from repositories.repository import RetentionPolicyRepository

        policy_repo = RetentionPolicyRepository(self.db)
        return await policy_repo.list(tenant_id=tenant_id, is_active=is_active)

    async def get_retention_status(self, document_id: int) -> Dict[str, Any]:
        """Get retention status for document"""
        from repositories.repository import RetentionPolicyRepository
        from workflows.retention_workflow import get_retention_status
        from models.database import get_applicable_retention_policy

        document = await self.doc_repo.get_by_id(document_id)
        if not document:
            raise ValueError("Document not found")

        # Get applicable retention policies
        policy_repo = RetentionPolicyRepository(self.db)
        policies = await policy_repo.list(tenant_id=document.tenant_id, is_active=True)

        # Find applicable policy
        applicable_policy = get_applicable_retention_policy(
            tenant_id=document.tenant_id,
            document=document,
            policies=policies
        )

        # Get retention status
        return get_retention_status(document, applicable_policy)

    async def get_document_access_log(
        self,
        document_id: int,
        action_type: Optional[AccessAction] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list:
        """Get access log for document"""
        logs = await self.access_repo.get_document_log(
            document_id=document_id,
            action_type=action_type,
            user_id=user_id,
            skip=skip,
            limit=limit
        )
        return logs
