"""Document processing service"""

import os
import hashlib
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging
import json
import sqlite3
import aiosqlite
from pathlib import Path

from models import (
    DocumentUpload, DocumentMetadata, DocumentStatus, DocumentAnalysisResult,
    DocumentComparison, SearchQuery, SearchResult
)

logger = logging.getLogger(__name__)

class DocumentProcessorService:
    """Service for document storage, retrieval, and processing"""
    
    def __init__(self, config):
        self.config = config
        self._ensure_storage_directories()
        self.db_path = "./documents.db"
        
    async def initialize(self):
        """Initialize database and storage"""
        await self._create_database_tables()
        
    def _ensure_storage_directories(self):
        """Create necessary storage directories"""
        if self.config.STORAGE_TYPE == "local":
            Path(self.config.STORAGE_PATH).mkdir(parents=True, exist_ok=True)
            Path(f"{self.config.STORAGE_PATH}/analysis").mkdir(parents=True, exist_ok=True)
    
    async def _create_database_tables(self):
        """Create database tables for document metadata"""
        async with aiosqlite.connect(self.db_path) as db:
            # Documents table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    document_type TEXT NOT NULL,
                    description TEXT,
                    audit_id TEXT,
                    user_id TEXT,
                    tags TEXT, -- JSON array
                    storage_path TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    status TEXT DEFAULT 'uploaded',
                    version INTEGER DEFAULT 1,
                    uploaded_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    analyzed_at TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Analysis results table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    analysis_data TEXT NOT NULL, -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents (document_id)
                )
            """)
            
            # Processing tasks table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS processing_tasks (
                    task_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    document_id TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    progress REAL DEFAULT 0.0,
                    started_at TEXT,
                    completed_at TEXT,
                    error_message TEXT,
                    result_data TEXT, -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            await db.execute("CREATE INDEX IF NOT EXISTS idx_documents_tenant ON documents(tenant_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(document_type)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_analysis_document ON analysis_results(document_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_tasks_document ON processing_tasks(document_id)")
            
            await db.commit()
    
    async def store_document(self, document_upload: DocumentUpload, content: bytes) -> str:
        """Store document and return document_id"""
        document_id = str(uuid.uuid4())
        
        try:
            # Calculate checksum
            checksum = hashlib.sha256(content).hexdigest()
            
            # Store file
            storage_path = await self._store_file_content(document_id, content, document_upload.filename)
            
            # Store metadata in database
            await self._store_document_metadata(document_id, document_upload, storage_path, checksum)
            
            logger.info(f"Stored document {document_id}: {document_upload.filename}")
            return document_id
            
        except Exception as e:
            logger.error(f"Failed to store document: {str(e)}")
            # Cleanup on error
            await self._cleanup_document_files(document_id)
            raise
    
    async def _store_file_content(self, document_id: str, content: bytes, filename: str) -> str:
        """Store file content to storage"""
        if self.config.STORAGE_TYPE == "local":
            # Create tenant-specific subdirectory
            file_extension = os.path.splitext(filename)[1]
            stored_filename = f"{document_id}{file_extension}"
            storage_path = os.path.join(self.config.STORAGE_PATH, stored_filename)
            
            with open(storage_path, 'wb') as f:
                f.write(content)
                
            return storage_path
        
        elif self.config.STORAGE_TYPE == "s3":
            # TODO: Implement S3 storage
            raise NotImplementedError("S3 storage not implemented yet")
        
        else:
            raise ValueError(f"Unsupported storage type: {self.config.STORAGE_TYPE}")
    
    async def _store_document_metadata(self, document_id: str, document_upload: DocumentUpload, storage_path: str, checksum: str):
        """Store document metadata in database"""
        now = datetime.utcnow().isoformat()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO documents (
                    document_id, tenant_id, filename, content_type, size, document_type,
                    description, audit_id, user_id, tags, storage_path, checksum,
                    status, uploaded_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                document_id, document_upload.tenant_id, document_upload.filename,
                document_upload.content_type, document_upload.size, document_upload.document_type,
                document_upload.description, document_upload.audit_id, document_upload.user_id,
                json.dumps(document_upload.tags), storage_path, checksum,
                DocumentStatus.UPLOADED, now, now
            ))
            await db.commit()
    
    async def get_document_content(self, document_id: str, tenant_id: str) -> Optional[bytes]:
        """Get document content"""
        try:
            # Get storage path from database
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT storage_path FROM documents WHERE document_id = ? AND tenant_id = ?",
                    (document_id, tenant_id)
                ) as cursor:
                    row = await cursor.fetchone()
                    
            if not row:
                return None
            
            storage_path = row[0]
            
            # Read file content
            if self.config.STORAGE_TYPE == "local":
                if os.path.exists(storage_path):
                    with open(storage_path, 'rb') as f:
                        return f.read()
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get document content: {str(e)}")
            return None
    
    async def get_document_metadata(self, document_id: str, tenant_id: str) -> Optional[DocumentMetadata]:
        """Get document metadata"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT document_id, tenant_id, filename, content_type, size, document_type,
                           description, audit_id, user_id, tags, storage_path, checksum,
                           status, version, uploaded_at, updated_at, analyzed_at
                    FROM documents 
                    WHERE document_id = ? AND tenant_id = ?
                """, (document_id, tenant_id)) as cursor:
                    row = await cursor.fetchone()
            
            if not row:
                return None
                
            return DocumentMetadata(
                document_id=row[0],
                tenant_id=row[1],
                filename=row[2],
                content_type=row[3],
                size=row[4],
                document_type=row[5],
                description=row[6],
                audit_id=row[7],
                user_id=row[8],
                tags=json.loads(row[9]) if row[9] else [],
                storage_path=row[10],
                checksum=row[11],
                status=DocumentStatus(row[12]),
                version=row[13],
                uploaded_at=datetime.fromisoformat(row[14]),
                updated_at=datetime.fromisoformat(row[15]),
                analyzed_at=datetime.fromisoformat(row[16]) if row[16] else None
            )
            
        except Exception as e:
            logger.error(f"Failed to get document metadata: {str(e)}")
            return None
    
    async def update_document_status(self, document_id: str, tenant_id: str, status: DocumentStatus):
        """Update document status"""
        try:
            now = datetime.utcnow().isoformat()
            analyzed_at = now if status == DocumentStatus.ANALYZED else None
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE documents 
                    SET status = ?, updated_at = ?, analyzed_at = COALESCE(?, analyzed_at)
                    WHERE document_id = ? AND tenant_id = ?
                """, (status.value, now, analyzed_at, document_id, tenant_id))
                await db.commit()
                
        except Exception as e:
            logger.error(f"Failed to update document status: {str(e)}")
            raise
    
    async def store_analysis_result(self, analysis_result: DocumentAnalysisResult):
        """Store document analysis result"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO analysis_results (document_id, tenant_id, analysis_data)
                    VALUES (?, ?, ?)
                """, (
                    analysis_result.document_id,
                    analysis_result.tenant_id,
                    analysis_result.json()
                ))
                await db.commit()
                
        except Exception as e:
            logger.error(f"Failed to store analysis result: {str(e)}")
            raise
    
    async def get_analysis_result(self, document_id: str, tenant_id: str) -> Optional[DocumentAnalysisResult]:
        """Get document analysis result"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT analysis_data FROM analysis_results
                    WHERE document_id = ? AND tenant_id = ?
                    ORDER BY created_at DESC LIMIT 1
                """, (document_id, tenant_id)) as cursor:
                    row = await cursor.fetchone()
            
            if not row:
                return None
                
            analysis_data = json.loads(row[0])
            return DocumentAnalysisResult(**analysis_data)
            
        except Exception as e:
            logger.error(f"Failed to get analysis result: {str(e)}")
            return None
    
    async def get_document_status(self, document_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get document processing status"""
        try:
            metadata = await self.get_document_metadata(document_id, tenant_id)
            if not metadata:
                return None
            
            # Check for processing tasks
            task_status = await self._get_latest_task_status(document_id, tenant_id)
            
            return {
                'document_id': document_id,
                'status': metadata.status.value,
                'filename': metadata.filename,
                'uploaded_at': metadata.uploaded_at.isoformat(),
                'analyzed_at': metadata.analyzed_at.isoformat() if metadata.analyzed_at else None,
                'task_status': task_status
            }
            
        except Exception as e:
            logger.error(f"Failed to get document status: {str(e)}")
            return None
    
    async def _get_latest_task_status(self, document_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get latest processing task status"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT task_id, task_type, status, progress, error_message
                    FROM processing_tasks
                    WHERE document_id = ? AND tenant_id = ?
                    ORDER BY created_at DESC LIMIT 1
                """, (document_id, tenant_id)) as cursor:
                    row = await cursor.fetchone()
            
            if not row:
                return None
                
            return {
                'task_id': row[0],
                'task_type': row[1],
                'status': row[2],
                'progress': row[3],
                'error_message': row[4]
            }
            
        except Exception as e:
            logger.error(f"Failed to get task status: {str(e)}")
            return None
    
    async def search_documents(self, search_params: Dict[str, Any]) -> SearchResult:
        """Search documents based on criteria"""
        try:
            # Build search query
            where_clauses = ["tenant_id = ?"]
            params = [search_params['tenant_id']]
            
            if search_params.get('query'):
                where_clauses.append("(filename LIKE ? OR description LIKE ?)")
                params.extend([f"%{search_params['query']}%", f"%{search_params['query']}%"])
            
            if search_params.get('document_type'):
                where_clauses.append("document_type = ?")
                params.append(search_params['document_type'])
            
            if search_params.get('audit_id'):
                where_clauses.append("audit_id = ?")
                params.append(search_params['audit_id'])
            
            where_clause = " AND ".join(where_clauses)
            
            # Get total count
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    f"SELECT COUNT(*) FROM documents WHERE {where_clause}",
                    params
                ) as cursor:
                    total_count = (await cursor.fetchone())[0]
                
                # Get documents
                async with db.execute(f"""
                    SELECT document_id, tenant_id, filename, content_type, size, document_type,
                           description, audit_id, user_id, tags, storage_path, checksum,
                           status, version, uploaded_at, updated_at, analyzed_at
                    FROM documents 
                    WHERE {where_clause}
                    ORDER BY uploaded_at DESC
                    LIMIT ? OFFSET ?
                """, params + [search_params['limit'], search_params['offset']]) as cursor:
                    rows = await cursor.fetchall()
            
            # Convert to metadata objects
            documents = []
            for row in rows:
                documents.append(DocumentMetadata(
                    document_id=row[0],
                    tenant_id=row[1],
                    filename=row[2],
                    content_type=row[3],
                    size=row[4],
                    document_type=row[5],
                    description=row[6],
                    audit_id=row[7],
                    user_id=row[8],
                    tags=json.loads(row[9]) if row[9] else [],
                    storage_path=row[10],
                    checksum=row[11],
                    status=DocumentStatus(row[12]),
                    version=row[13],
                    uploaded_at=datetime.fromisoformat(row[14]),
                    updated_at=datetime.fromisoformat(row[15]),
                    analyzed_at=datetime.fromisoformat(row[16]) if row[16] else None
                ))
            
            return SearchResult(
                total_count=total_count,
                documents=documents,
                query=SearchQuery(**search_params),
                search_time=0.0  # TODO: Implement timing
            )
            
        except Exception as e:
            logger.error(f"Failed to search documents: {str(e)}")
            raise
    
    async def compare_documents(self, doc_id_1: str, doc_id_2: str, tenant_id: str, comparison_type: str) -> DocumentComparison:
        """Compare two documents"""
        try:
            # Get both documents' analysis results
            analysis_1 = await self.get_analysis_result(doc_id_1, tenant_id)
            analysis_2 = await self.get_analysis_result(doc_id_2, tenant_id)
            
            if not analysis_1 or not analysis_2:
                raise ValueError("One or both documents have not been analyzed")
            
            # Calculate similarity metrics
            content_similarity = self._calculate_content_similarity(analysis_1, analysis_2)
            structure_similarity = self._calculate_structure_similarity(analysis_1, analysis_2)
            compliance_gap = abs(
                analysis_1.compliance_score.overall_score - 
                analysis_2.compliance_score.overall_score
            ) if analysis_1.compliance_score and analysis_2.compliance_score else 0.0
            
            # Find common and unique elements
            common_terms = set(analysis_1.key_terms) & set(analysis_2.key_terms)
            unique_to_first = set(analysis_1.key_terms) - set(analysis_2.key_terms)
            unique_to_second = set(analysis_2.key_terms) - set(analysis_1.key_terms)
            
            return DocumentComparison(
                document_id_1=doc_id_1,
                document_id_2=doc_id_2,
                tenant_id=tenant_id,
                comparison_type=comparison_type,
                content_similarity=content_similarity,
                structure_similarity=structure_similarity,
                compliance_gap=compliance_gap,
                common_sections=list(common_terms),
                unique_to_first=list(unique_to_first),
                unique_to_second=list(unique_to_second),
                merge_suggestions=["Consider combining common procedures", "Standardize terminology"],
                improvement_areas=["Update older document to match compliance level"]
            )
            
        except Exception as e:
            logger.error(f"Failed to compare documents: {str(e)}")
            raise
    
    def _calculate_content_similarity(self, analysis_1: DocumentAnalysisResult, analysis_2: DocumentAnalysisResult) -> float:
        """Calculate content similarity between two analyses"""
        # Simple similarity based on common key terms
        terms_1 = set(analysis_1.key_terms)
        terms_2 = set(analysis_2.key_terms)
        
        if not terms_1 and not terms_2:
            return 1.0
        
        intersection = len(terms_1 & terms_2)
        union = len(terms_1 | terms_2)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_structure_similarity(self, analysis_1: DocumentAnalysisResult, analysis_2: DocumentAnalysisResult) -> float:
        """Calculate structure similarity"""
        # Simple similarity based on structure scores
        score_1 = analysis_1.structure_score or 0.0
        score_2 = analysis_2.structure_score or 0.0
        
        return 1.0 - abs(score_1 - score_2)
    
    async def extract_text(self, content: bytes, content_type: str) -> str:
        """Extract text from document content"""
        try:
            if content_type == 'text/plain':
                return content.decode('utf-8')
            
            elif content_type == 'application/pdf':
                # TODO: Implement PDF text extraction using PyPDF2 or similar
                return f"[PDF Content - {len(content)} bytes]"
            
            elif content_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']:
                # TODO: Implement DOCX/DOC text extraction using python-docx
                return f"[Word Document - {len(content)} bytes]"
            
            else:
                # Try to decode as text
                try:
                    return content.decode('utf-8')
                except UnicodeDecodeError:
                    return f"[Binary Content - {len(content)} bytes]"
                    
        except Exception as e:
            logger.error(f"Failed to extract text: {str(e)}")
            return f"[Text extraction failed: {str(e)}]"
    
    async def _cleanup_document_files(self, document_id: str):
        """Clean up document files on error"""
        try:
            # TODO: Implement cleanup logic
            pass
        except Exception as e:
            logger.error(f"Failed to cleanup document files: {str(e)}")
