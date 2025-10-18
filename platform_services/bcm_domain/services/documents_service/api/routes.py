"""
API Routes for Documents Service
All FastAPI endpoints

Based on: BCM/documents/main.py endpoints (lines 279-1543)
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os

from config import settings
from models.database import (
    Document, DocumentAccess, DocumentShare, DocumentApproval,
    DocumentComparison, DocumentRetentionPolicy,
    DocumentType, DocumentStatus, DocumentClassification,
    AccessAction, SharePermission, ApprovalStatus,
    get_applicable_retention_policy
)
from models.domain import (
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentDetailResponse,
    DocumentShareCreate, ApprovalRequestCreate, RetentionPolicyCreate,
    DocumentListResponse
)
from repositories.repository import (
    DocumentRepository, DocumentAccessRepository, DocumentShareRepository,
    DocumentApprovalRepository, DocumentComparisonRepository, RetentionPolicyRepository
)
from services.document_service import DocumentService
from workflows.lifecycle_workflow import (
    DocumentLifecycleAction, execute_lifecycle_transition, get_workflow_summary
)
from workflows.approval_workflow import (
    ApprovalWorkflowAction, calculate_approval_priority, calculate_approval_due_date,
    execute_approval_transition, get_approval_workflow_summary
)
from workflows.retention_workflow import get_retention_status
from core.comparator import DocumentComparator
from integrations import (
    get_plan_documents, check_plan_document_completeness,
    get_policy_documents, get_iso_clause_coverage,
    get_validation_documents_summary
)

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Import shared database dependency
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))
from shared.database import get_db

async def get_document_service(db: AsyncSession = Depends(get_db)) -> DocumentService:
    """Get document service instance"""
    return DocumentService(
        db=db,
        storage_path=settings.STORAGE_PATH,
        max_file_size=settings.MAX_FILE_SIZE,
        openai_api_key=settings.OPENAI_API_KEY
    )


# ============================================================================
# DOCUMENT CRUD ENDPOINTS
# ============================================================================

@router.post("/documents", response_model=DocumentResponse, status_code=201)
async def create_document(
    doc: DocumentCreate,
    service: DocumentService = Depends(get_document_service)
):
    """Create a new document (metadata only)"""
    document = await service.create_document(doc)
    return document


@router.post("/documents/{document_id}/upload")
async def upload_document_file(
    document_id: int,
    file: UploadFile = File(...),
    user_id: str = Query(...),
    auto_process: bool = Query(True),
    service: DocumentService = Depends(get_document_service)
):
    """Upload file for document and optionally auto-process"""
    try:
        document, processing_result = await service.upload_file(
            document_id=document_id,
            file=file,
            user_id=user_id,
            auto_process=auto_process
        )

        return {
            "document_id": document.document_id,
            "file_name": document.file_name,
            "file_size": document.file_size,
            "file_hash": document.file_hash,
            "processing_completed": auto_process,
            "processing_result": processing_result,
            "message": "File uploaded and processed successfully" if auto_process else "File uploaded successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/documents/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: int,
    user_id: str = Query(...),
    service: DocumentService = Depends(get_document_service)
):
    """Get document by ID"""
    try:
        document = await service.get_document(document_id, user_id)
        return document
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: int,
    user_id: str = Query(...),
    service: DocumentService = Depends(get_document_service)
):
    """Download document file"""
    try:
        document, file_path = await service.get_document_for_download(
            document_id=document_id,
            user_id=user_id
        )

        return FileResponse(
            path=file_path,
            filename=document.file_name,
            media_type=document.mime_type or 'application/octet-stream'
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    tenant_id: str = Query(...),
    document_type: Optional[DocumentType] = None,
    status: Optional[DocumentStatus] = None,
    classification: Optional[DocumentClassification] = None,
    owner_id: Optional[str] = None,
    department: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    service: DocumentService = Depends(get_document_service)
):
    """List documents with filtering"""
    try:
        result = await service.list_documents(
            tenant_id=tenant_id,
            status=status,
            doc_type=document_type,
            category=classification,
            owner_id=owner_id,
            department=department,
            search=search,
            skip=skip,
            limit=limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.patch("/documents/{document_id}")
async def update_document(
    document_id: int,
    updates: DocumentUpdate,
    user_id: str = Query(...),
    service: DocumentService = Depends(get_document_service)
):
    """Update document metadata"""
    try:
        document = await service.update_document(document_id, updates, user_id)
        return document
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    user_id: str = Query(...),
    reason: Optional[str] = None,
    service: DocumentService = Depends(get_document_service)
):
    """Soft delete document"""
    try:
        await service.delete_document(document_id, user_id, reason)
        return {"message": "Document deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# LIFECYCLE WORKFLOW ENDPOINTS
# ============================================================================

@router.post("/documents/{document_id}/workflow/{action}")
async def execute_workflow_action_endpoint(
    document_id: int,
    action: DocumentLifecycleAction,
    user_id: str = Query(...),
    notes: Optional[str] = None,
    service: DocumentService = Depends(get_document_service)
):
    """Execute workflow action on document"""
    try:
        result = await service.execute_workflow_action(
            document_id=document_id,
            action=action.value,
            user_id=user_id,
            notes=notes
        )

        result["message"] = f"Document {action.value.replace('_', ' ')} successfully"
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow action failed: {str(e)}")


@router.get("/documents/{document_id}/workflow/status")
async def get_workflow_status_endpoint(
    document_id: int,
    service: DocumentService = Depends(get_document_service)
):
    """Get workflow status and available actions for document"""
    try:
        summary = await service.get_workflow_status(document_id)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")


# ============================================================================
# VERSION CONTROL ENDPOINTS
# ============================================================================

@router.post("/documents/{document_id}/version")
async def create_new_version(
    document_id: int,
    user_id: str = Query(...),
    version_notes: Optional[str] = None,
    service: DocumentService = Depends(get_document_service)
):
    """Create new version of document"""
    try:
        new_doc = await service.create_new_version(document_id, user_id, version_notes)
        return {
            "new_document_id": new_doc.document_id,
            "new_version": new_doc.version,
            "message": "New version created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/documents/{document_id}/versions")
async def get_document_versions_endpoint(
    document_id: int,
    service: DocumentService = Depends(get_document_service)
):
    """Get all versions of a document"""
    try:
        # First get the document to get its document_code
        document = await service.get_document(document_id, user_id="system")
        result = await service.get_document_versions(document.document_code)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get versions: {str(e)}")


@router.post("/documents/compare")
async def compare_documents_endpoint(
    source_id: int,
    target_id: int,
    user_id: str = Query("system"),
    service: DocumentService = Depends(get_document_service)
):
    """Compare two document versions"""
    try:
        comparison_result = await service.compare_documents(
            source_id=source_id,
            target_id=target_id,
            user_id=user_id
        )
        return comparison_result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


# ============================================================================
# SHARING ENDPOINTS
# ============================================================================

@router.post("/documents/{document_id}/share")
async def share_document_endpoint(
    document_id: int,
    share_data: DocumentShareCreate,
    user_id: str = Query(...),
    service: DocumentService = Depends(get_document_service)
):
    """Share document with user or email"""
    try:
        share = await service.share_document(
            document_id=document_id,
            recipient_id=share_data.shared_with_user_id,
            recipient_name=share_data.shared_with_email,
            permission_level=share_data.permission_level,
            expiry_date=share_data.expires_at,
            user_id=user_id,
            can_reshare=share_data.can_reshare,
            share_message=share_data.share_message
        )
        return share
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Share failed: {str(e)}")


@router.get("/documents/{document_id}/shares")
async def get_document_shares_endpoint(
    document_id: int,
    service: DocumentService = Depends(get_document_service)
):
    """Get all shares for a document"""
    try:
        shares = await service.get_document_shares(document_id)
        return shares
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get shares: {str(e)}")


# ============================================================================
# APPROVAL ENDPOINTS
# ============================================================================

@router.post("/documents/{document_id}/approvals")
async def request_approval_endpoint(
    document_id: int,
    approval_data: ApprovalRequestCreate,
    user_id: str = Query(...),
    service: DocumentService = Depends(get_document_service)
):
    """Request document approval"""
    try:
        result = await service.request_approval(
            document_id=document_id,
            approver_id=approval_data.approver_id,
            approver_name=approval_data.approver_role,
            notes=approval_data.notes,
            user_id=user_id,
            sla_hours=approval_data.sla_hours
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Approval request failed: {str(e)}")


@router.post("/approvals/{approval_id}/respond")
async def respond_to_approval_endpoint(
    approval_id: int,
    action: ApprovalWorkflowAction,
    user_id: str = Query(...),
    notes: Optional[str] = None,
    service: DocumentService = Depends(get_document_service)
):
    """Respond to approval request"""
    try:
        result = await service.respond_to_approval(
            approval_id=approval_id,
            action=action.value,
            notes=notes,
            user_id=user_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Approval response failed: {str(e)}")


@router.get("/documents/{document_id}/approvals")
async def get_document_approvals_endpoint(
    document_id: int,
    service: DocumentService = Depends(get_document_service)
):
    """Get all approval requests for document"""
    try:
        result = await service.get_document_approvals(document_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get approvals: {str(e)}")


# ============================================================================
# RETENTION POLICY ENDPOINTS
# ============================================================================

@router.post("/retention-policies", status_code=201)
async def create_retention_policy_endpoint(
    policy_data: RetentionPolicyCreate,
    user_id: str = Query(...),
    service: DocumentService = Depends(get_document_service)
):
    """Create document retention policy"""
    try:
        policy = await service.create_retention_policy(
            policy_data=policy_data.dict(),
            user_id=user_id
        )
        return policy
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create retention policy: {str(e)}")


@router.get("/retention-policies")
async def list_retention_policies_endpoint(
    tenant_id: str = Query(...),
    is_active: Optional[bool] = True,
    service: DocumentService = Depends(get_document_service)
):
    """List retention policies for tenant"""
    try:
        policies = await service.list_retention_policies(
            tenant_id=tenant_id,
            is_active=is_active
        )
        return policies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list retention policies: {str(e)}")


@router.get("/documents/{document_id}/retention")
async def get_document_retention_status_endpoint(
    document_id: int,
    service: DocumentService = Depends(get_document_service)
):
    """Get retention status for document"""
    try:
        status = await service.get_retention_status(document_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get retention status: {str(e)}")


# ============================================================================
# INTEGRATION ENDPOINTS
# ============================================================================

@router.get("/plans/{plan_id}/documents")
async def get_documents_for_plan(
    plan_id: int,
    tenant_id: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Get all documents linked to a plan"""
    documents = await get_plan_documents(plan_id, tenant_id, db)
    return {
        "plan_id": plan_id,
        "document_count": len(documents),
        "documents": documents
    }


@router.get("/iso-coverage")
async def get_iso_coverage(
    tenant_id: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Get ISO 22301 clause coverage"""
    return await get_iso_clause_coverage(tenant_id, db)


# ============================================================================
# ACCESS LOG ENDPOINTS
# ============================================================================

@router.get("/documents/{document_id}/access-log")
async def get_document_access_log_endpoint(
    document_id: int,
    action_type: Optional[AccessAction] = None,
    user_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    service: DocumentService = Depends(get_document_service)
):
    """Get access log for document"""
    try:
        logs = await service.get_document_access_log(
            document_id=document_id,
            action_type=action_type,
            user_id=user_id,
            skip=skip,
            limit=limit
        )
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get access log: {str(e)}")
