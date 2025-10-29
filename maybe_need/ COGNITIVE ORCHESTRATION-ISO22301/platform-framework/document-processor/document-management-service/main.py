#!/usr/bin/env python3
"""
Document Management Service
Comprehensive document management with version control, collaboration, and compliance tracking
"""

import os
import uuid
import hashlib
import mimetypes
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from pathlib import Path
import json
import logging

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Integer, Text, JSON, LargeBinary, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel, Field
import aiofiles
import aiofiles.os
from enum import Enum

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bcm_docs")
STORAGE_PATH = os.getenv("STORAGE_PATH", "/Users/MD/ISO-22301/storage/documents")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "100000000"))  # 100MB
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "pdf,docx,xlsx,pptx,txt,md,png,jpg,jpeg,zip").split(",")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure storage directory exists
Path(STORAGE_PATH).mkdir(parents=True, exist_ok=True)

# FastAPI app
app = FastAPI(
    title="Document Management Service",
    description="Enterprise document management with version control and compliance",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class DocumentType(str, Enum):
    POLICY = "policy"
    PROCEDURE = "procedure"
    FORM = "form"
    TEMPLATE = "template"
    MANUAL = "manual"
    REPORT = "report"
    INCIDENT = "incident"
    PLAN = "plan"
    TRAINING = "training"
    COMPLIANCE = "compliance"
    OTHER = "other"

class DocumentStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"

class AccessLevel(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class ActionType(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    VIEWED = "viewed"
    DOWNLOADED = "downloaded"
    SHARED = "shared"
    DELETED = "deleted"
    RESTORED = "restored"
    APPROVED = "approved"
    REJECTED = "rejected"

# Database Models
class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False, index=True)
    description = Column(Text)
    document_type = Column(String, nullable=False, index=True)
    status = Column(String, default=DocumentStatus.DRAFT, index=True)
    access_level = Column(String, default=AccessLevel.INTERNAL, index=True)

    # File information
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    file_hash = Column(String, nullable=False, index=True)
    storage_path = Column(String, nullable=False)

    # Metadata
    version = Column(String, default="1.0")
    parent_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    tags = Column(JSON)  # List of tags
    metadata_info = Column(JSON)  # Additional metadata

    # Ownership and tracking
    created_by = Column(String, nullable=False)
    updated_by = Column(String)
    approved_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime)
    expires_at = Column(DateTime)

    # Compliance
    compliance_frameworks = Column(JSON)  # ISO 22301, etc.
    retention_period_days = Column(Integer, default=2555)  # 7 years default
    is_deleted = Column(Boolean, default=False)

    # Relationships
    versions = relationship("Document", remote_side=[parent_id])
    access_logs = relationship("DocumentAccess", back_populates="document")

class DocumentAccess(Base):
    __tablename__ = "document_access"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False)
    ip_address = Column(String)
    user_agent = Column(String)
    accessed_at = Column(DateTime, default=datetime.utcnow, index=True)
    session_id = Column(String)
    additional_data = Column(JSON)

    # Relationship
    document = relationship("Document", back_populates="access_logs")

class DocumentShare(Base):
    __tablename__ = "document_shares"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    shared_by = Column(String, nullable=False)
    shared_with = Column(String, nullable=False)
    permission = Column(String, default="read")  # read, write, admin
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

# Pydantic Models
class DocumentMetadata(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    document_type: DocumentType
    access_level: AccessLevel = AccessLevel.INTERNAL
    tags: List[str] = []
    compliance_frameworks: List[str] = []
    retention_period_days: int = 2555
    expires_at: Optional[datetime] = None

class DocumentResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    document_type: str
    status: str
    access_level: str
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    version: str
    tags: List[str]
    created_by: str
    created_at: str
    updated_at: str
    approved_at: Optional[str]
    expires_at: Optional[str]
    compliance_frameworks: List[str]

class DocumentSearchRequest(BaseModel):
    query: Optional[str] = None
    document_type: Optional[DocumentType] = None
    status: Optional[DocumentStatus] = None
    access_level: Optional[AccessLevel] = None
    tags: List[str] = []
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    limit: int = Field(default=50, le=1000)
    offset: int = Field(default=0, ge=0)

class DocumentUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    document_type: Optional[DocumentType] = None
    access_level: Optional[AccessLevel] = None
    tags: Optional[List[str]] = None
    compliance_frameworks: Optional[List[str]] = None
    expires_at: Optional[datetime] = None

class DocumentShareRequest(BaseModel):
    shared_with: str
    permission: str = "read"
    expires_at: Optional[datetime] = None

# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility functions
def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of file"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    extension = filename.split(".")[-1].lower() if "." in filename else ""
    return extension in ALLOWED_EXTENSIONS

def generate_storage_path(document_id: str, filename: str) -> str:
    """Generate storage path for document"""
    # Create directory structure: YYYY/MM/DD/document_id/
    now = datetime.utcnow()
    date_path = now.strftime("%Y/%m/%d")
    dir_path = Path(STORAGE_PATH) / date_path / document_id
    dir_path.mkdir(parents=True, exist_ok=True)
    return str(dir_path / filename)

async def log_document_access(
    db: Session,
    document_id: str,
    user_id: str,
    action: ActionType,
    ip_address: str = None,
    user_agent: str = None,
    additional_data: Dict = None
):
    """Log document access"""
    try:
        access_log = DocumentAccess(
            document_id=document_id,
            user_id=user_id,
            action=action.value,
            ip_address=ip_address,
            user_agent=user_agent,
            additional_data=additional_data
        )
        db.add(access_log)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log document access: {e}")
        db.rollback()

# Document Management Service
class DocumentManager:
    def __init__(self, db: Session):
        self.db = db

    async def create_document(
        self,
        file: UploadFile,
        metadata: DocumentMetadata,
        user_id: str
    ) -> DocumentResponse:
        """Create new document"""
        try:
            # Validate file
            if not is_allowed_file(file.filename):
                raise HTTPException(
                    status_code=400,
                    detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                )

            if file.size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
                )

            # Generate document ID and storage path
            doc_id = uuid.uuid4()
            storage_path = generate_storage_path(str(doc_id), file.filename)

            # Save file to storage
            async with aiofiles.open(storage_path, "wb") as f:
                content = await file.read()
                await f.write(content)

            # Calculate file hash
            file_hash = calculate_file_hash(storage_path)

            # Check for duplicates
            existing = self.db.query(Document).filter(
                Document.file_hash == file_hash,
                Document.is_deleted == False
            ).first()

            if existing:
                # Remove the duplicate file
                os.remove(storage_path)
                raise HTTPException(
                    status_code=409,
                    detail=f"Document already exists: {existing.title}"
                )

            # Create document record
            document = Document(
                id=doc_id,
                title=metadata.title,
                description=metadata.description,
                document_type=metadata.document_type.value,
                access_level=metadata.access_level.value,
                filename=file.filename,
                original_filename=file.filename,
                file_size=file.size,
                mime_type=file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream",
                file_hash=file_hash,
                storage_path=storage_path,
                tags=metadata.tags,
                compliance_frameworks=metadata.compliance_frameworks,
                retention_period_days=metadata.retention_period_days,
                expires_at=metadata.expires_at,
                created_by=user_id,
                updated_by=user_id
            )

            self.db.add(document)
            self.db.commit()

            # Log access
            await log_document_access(
                self.db, str(doc_id), user_id, ActionType.CREATED
            )

            return self._to_response(document)

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating document: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create document: {str(e)}")

    def search_documents(self, search_request: DocumentSearchRequest) -> Dict[str, Any]:
        """Search documents with filters"""
        try:
            query = self.db.query(Document).filter(Document.is_deleted == False)

            # Apply filters
            if search_request.query:
                search_term = f"%{search_request.query}%"
                query = query.filter(
                    Document.title.ilike(search_term) |
                    Document.description.ilike(search_term)
                )

            if search_request.document_type:
                query = query.filter(Document.document_type == search_request.document_type.value)

            if search_request.status:
                query = query.filter(Document.status == search_request.status.value)

            if search_request.access_level:
                query = query.filter(Document.access_level == search_request.access_level.value)

            if search_request.created_after:
                query = query.filter(Document.created_at >= search_request.created_after)

            if search_request.created_before:
                query = query.filter(Document.created_at <= search_request.created_before)

            # Count total results
            total_count = query.count()

            # Apply pagination and ordering
            documents = query.order_by(Document.created_at.desc()).offset(
                search_request.offset
            ).limit(search_request.limit).all()

            return {
                "documents": [self._to_response(doc) for doc in documents],
                "total_count": total_count,
                "limit": search_request.limit,
                "offset": search_request.offset,
                "has_more": (search_request.offset + len(documents)) < total_count
            }

        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

    def get_document(self, document_id: str, user_id: str) -> DocumentResponse:
        """Get document by ID"""
        try:
            document = self.db.query(Document).filter(
                Document.id == document_id,
                Document.is_deleted == False
            ).first()

            if not document:
                raise HTTPException(status_code=404, detail="Document not found")

            # Log access
            asyncio.create_task(log_document_access(
                self.db, document_id, user_id, ActionType.VIEWED
            ))

            return self._to_response(document)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")

    def update_document(
        self,
        document_id: str,
        update_request: DocumentUpdateRequest,
        user_id: str
    ) -> DocumentResponse:
        """Update document metadata"""
        try:
            document = self.db.query(Document).filter(
                Document.id == document_id,
                Document.is_deleted == False
            ).first()

            if not document:
                raise HTTPException(status_code=404, detail="Document not found")

            # Update fields
            if update_request.title is not None:
                document.title = update_request.title
            if update_request.description is not None:
                document.description = update_request.description
            if update_request.document_type is not None:
                document.document_type = update_request.document_type.value
            if update_request.access_level is not None:
                document.access_level = update_request.access_level.value
            if update_request.tags is not None:
                document.tags = update_request.tags
            if update_request.compliance_frameworks is not None:
                document.compliance_frameworks = update_request.compliance_frameworks
            if update_request.expires_at is not None:
                document.expires_at = update_request.expires_at

            document.updated_by = user_id
            document.updated_at = datetime.utcnow()

            self.db.commit()

            # Log access
            asyncio.create_task(log_document_access(
                self.db, document_id, user_id, ActionType.UPDATED
            ))

            return self._to_response(document)

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating document: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to update document: {str(e)}")

    def delete_document(self, document_id: str, user_id: str) -> Dict[str, str]:
        """Soft delete document"""
        try:
            document = self.db.query(Document).filter(
                Document.id == document_id,
                Document.is_deleted == False
            ).first()

            if not document:
                raise HTTPException(status_code=404, detail="Document not found")

            document.is_deleted = True
            document.updated_by = user_id
            document.updated_at = datetime.utcnow()

            self.db.commit()

            # Log access
            asyncio.create_task(log_document_access(
                self.db, document_id, user_id, ActionType.DELETED
            ))

            return {"message": "Document deleted successfully"}

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting document: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

    def _to_response(self, document: Document) -> DocumentResponse:
        """Convert Document model to response"""
        return DocumentResponse(
            id=str(document.id),
            title=document.title,
            description=document.description,
            document_type=document.document_type,
            status=document.status,
            access_level=document.access_level,
            filename=document.filename,
            original_filename=document.original_filename,
            file_size=document.file_size,
            mime_type=document.mime_type,
            version=document.version,
            tags=document.tags or [],
            created_by=document.created_by,
            created_at=document.created_at.isoformat(),
            updated_at=document.updated_at.isoformat(),
            approved_at=document.approved_at.isoformat() if document.approved_at else None,
            expires_at=document.expires_at.isoformat() if document.expires_at else None,
            compliance_frameworks=document.compliance_frameworks or []
        )

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "document-management",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/v1/documents", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(None),
    document_type: DocumentType = Form(...),
    access_level: AccessLevel = Form(AccessLevel.INTERNAL),
    tags: str = Form("[]"),  # JSON string
    compliance_frameworks: str = Form("[]"),  # JSON string
    retention_period_days: int = Form(2555),
    user_id: str = Form("system"),
    db: Session = Depends(get_db)
):
    """Upload new document"""
    try:
        # Parse JSON fields
        tags_list = json.loads(tags) if tags else []
        compliance_list = json.loads(compliance_frameworks) if compliance_frameworks else []

        metadata = DocumentMetadata(
            title=title,
            description=description,
            document_type=document_type,
            access_level=access_level,
            tags=tags_list,
            compliance_frameworks=compliance_list,
            retention_period_days=retention_period_days
        )

        manager = DocumentManager(db)
        return await manager.create_document(file, metadata, user_id)

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in tags or compliance_frameworks")
    except Exception as e:
        logger.error(f"Error in upload_document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/documents/search")
async def search_documents(
    search_request: DocumentSearchRequest,
    db: Session = Depends(get_db)
):
    """Search documents"""
    manager = DocumentManager(db)
    return manager.search_documents(search_request)

@app.get("/api/v1/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    user_id: str = Query("system"),
    db: Session = Depends(get_db)
):
    """Get document by ID"""
    manager = DocumentManager(db)
    return manager.get_document(document_id, user_id)

@app.get("/api/v1/documents/{document_id}/download")
async def download_document(
    document_id: str,
    user_id: str = Query("system"),
    db: Session = Depends(get_db)
):
    """Download document file"""
    try:
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.is_deleted == False
        ).first()

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        if not os.path.exists(document.storage_path):
            raise HTTPException(status_code=404, detail="File not found on storage")

        # Log access
        await log_document_access(
            db, document_id, user_id, ActionType.DOWNLOADED
        )

        return FileResponse(
            path=document.storage_path,
            filename=document.original_filename,
            media_type=document.mime_type
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading document: {e}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.put("/api/v1/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    update_request: DocumentUpdateRequest,
    user_id: str = Query("system"),
    db: Session = Depends(get_db)
):
    """Update document metadata"""
    manager = DocumentManager(db)
    return manager.update_document(document_id, update_request, user_id)

@app.delete("/api/v1/documents/{document_id}")
async def delete_document(
    document_id: str,
    user_id: str = Query("system"),
    db: Session = Depends(get_db)
):
    """Delete document"""
    manager = DocumentManager(db)
    return manager.delete_document(document_id, user_id)

@app.get("/api/v1/documents/{document_id}/access-logs")
async def get_document_access_logs(
    document_id: str,
    limit: int = Query(50, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get document access logs"""
    try:
        # Verify document exists
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Get access logs
        logs = db.query(DocumentAccess).filter(
            DocumentAccess.document_id == document_id
        ).order_by(DocumentAccess.accessed_at.desc()).offset(offset).limit(limit).all()

        return {
            "document_id": document_id,
            "access_logs": [
                {
                    "id": str(log.id),
                    "user_id": log.user_id,
                    "action": log.action,
                    "accessed_at": log.accessed_at.isoformat(),
                    "ip_address": log.ip_address,
                    "user_agent": log.user_agent
                }
                for log in logs
            ],
            "limit": limit,
            "offset": offset
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting access logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get access logs: {str(e)}")

@app.get("/api/v1/documents/stats")
async def get_document_stats(db: Session = Depends(get_db)):
    """Get document statistics"""
    try:
        total_documents = db.query(Document).filter(Document.is_deleted == False).count()

        stats_by_type = {}
        for doc_type in DocumentType:
            count = db.query(Document).filter(
                Document.document_type == doc_type.value,
                Document.is_deleted == False
            ).count()
            stats_by_type[doc_type.value] = count

        stats_by_status = {}
        for status in DocumentStatus:
            count = db.query(Document).filter(
                Document.status == status.value,
                Document.is_deleted == False
            ).count()
            stats_by_status[status.value] = count

        # Recent activity
        recent_documents = db.query(Document).filter(
            Document.is_deleted == False
        ).order_by(Document.created_at.desc()).limit(5).all()

        return {
            "total_documents": total_documents,
            "by_type": stats_by_type,
            "by_status": stats_by_status,
            "recent_documents": [
                {
                    "id": str(doc.id),
                    "title": doc.title,
                    "type": doc.document_type,
                    "created_at": doc.created_at.isoformat()
                }
                for doc in recent_documents
            ]
        }

    except Exception as e:
        logger.error(f"Error getting document stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

# Database initialization
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Document management database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8083")))