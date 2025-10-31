"""
Document Processor Service - FastAPI
ISO 22301 BCM Platform Document Analysis and Compliance Mapping
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, Depends, Header
from validators.document_validator import validate_document, validate_documents_batch, DocumentValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import json
import os
import uuid
import aiofiles
import httpx
from pathlib import Path
import logging
from contextlib import asynccontextmanager

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
EVENTBUS_URL = os.getenv("EVENTBUS_URL", "http://localhost:8001")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8081,http://localhost:8069").split(",")

# API key and file settings
API_KEY = os.getenv("DOCUMENT_PROCESSOR_API_KEY", "")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default
ALLOWED_MIME_TYPES = os.getenv(
    "ALLOWED_MIME_TYPES",
    "application/pdf,text/plain,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
).split(",")

# Document storage
documents = {}
analyses = {}


def verify_token(x_api_key: str = Header(None)):
    """Simple API key verification"""
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")
    return x_api_key

# Models
class DocumentMetadata(BaseModel):
    id: str
    filename: str
    size: int
    content_type: str
    uploaded_at: datetime
    tenant_id: str
    status: str = "uploaded"
    category: Optional[str] = None

class AnalysisRequest(BaseModel):
    document_id: str
    tenant_id: str
    analysis_type: str = "iso_compliance"

class AnalysisResult(BaseModel):
    id: str
    document_id: str
    analysis_type: str
    iso_mapping: Dict[str, Any]
    compliance_score: float
    key_phrases: List[str]
    findings: List[str]
    recommendations: List[str]
    created_at: datetime
    status: str = "completed"

class ComparisonRequest(BaseModel):
    document1_id: str
    document2_id: str
    tenant_id: str
    comparison_type: str = "compliance"

class ComparisonResult(BaseModel):
    id: str
    document1_id: str
    document2_id: str
    similarity_score: float
    differences: List[Dict[str, Any]]
    common_elements: List[str]
    compliance_gaps: List[Dict[str, Any]]
    created_at: datetime

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Document Processor service...")
    
    # Create upload directory
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Upload directory: {UPLOAD_DIR}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Document Processor service...")

# Create FastAPI app
app = FastAPI(
    title="BCM Document Processor Service",
    description="Document analysis and compliance mapping for ISO 22301 BCM Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "document_processor",
        "documents_count": len(documents),
        "analyses_count": len(analyses)
    }

# Upload document
@app.post("/api/documents/upload", response_model=DocumentMetadata)
async def upload_document(
    try:
        document_metadata = validate_document(file.file.read(), file.filename)
        file.file.seek(0)  # Сбрасываем указатель файла в начало
    except DocumentValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    tenant_id: str = Form(...),
    category: Optional[str] = Form(None),
    file: UploadFile = File(...),
    token: str = Depends(verify_token)
):
    try:
        # Validate MIME type
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        if file.spool_max_size and file.spool_max_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")

        # Generate document ID
        doc_id = f"doc_{uuid.uuid4()}"

        # Save file in chunks
        file_path = UPLOAD_DIR / f"{doc_id}_{file.filename}"
        size = 0
        chunk_size = 1024 * 1024  # 1MB
        async with aiofiles.open(file_path, 'wb') as f:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    raise HTTPException(status_code=400, detail="File too large")
                await f.write(chunk)

        # Create metadata
        metadata = DocumentMetadata(
            id=doc_id,
            filename=file.filename,
            size=size,
            content_type=file.content_type,
            uploaded_at=datetime.utcnow(),
            tenant_id=tenant_id,
            category=category
        )
        
        documents[doc_id] = metadata
        
        # Send event to EventBus
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{EVENTBUS_URL}/api/events/publish",
                json={
                    "event_type": "bcm.document.uploaded",
                    "tenant_id": tenant_id,
                    "data": {
                        "document_id": doc_id,
                        "filename": file.filename,
                        "size": size,
                        "category": category
                    }
                }
            )
        
        logger.info(f"Document uploaded: {doc_id} - {file.filename}")
        return metadata
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# List documents
@app.get("/api/documents", response_model=List[DocumentMetadata])
async def list_documents(
    tenant_id: str,
    category: Optional[str] = None,
    status: Optional[str] = None,
    token: str = Depends(verify_token)
):
    try:
        filtered_docs = []
        for doc in documents.values():
            if doc.tenant_id != tenant_id:
                continue
            if category and doc.category != category:
                continue
            if status and doc.status != status:
                continue
            filtered_docs.append(doc)
        
        # Sort by upload date (newest first)
        filtered_docs.sort(key=lambda x: x.uploaded_at, reverse=True)
        return filtered_docs
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get document details
@app.get("/api/documents/{document_id}", response_model=DocumentMetadata)
async def get_document(document_id: str, tenant_id: str, token: str = Depends(verify_token)):
    try:
        doc = documents.get(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        if doc.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return doc
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analyze document
@app.post("/api/documents/analyze", response_model=AnalysisResult)
async def analyze_document(request: AnalysisRequest, background_tasks: BackgroundTasks, token: str = Depends(verify_token)):
    try:
        # Check if document exists
        doc = documents.get(request.document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        if doc.tenant_id != request.tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Start analysis in background
        analysis_id = f"analysis_{uuid.uuid4()}"
        background_tasks.add_task(perform_analysis, analysis_id, request)
        
        # Return immediate response
        result = AnalysisResult(
            id=analysis_id,
            document_id=request.document_id,
            analysis_type=request.analysis_type,
            iso_mapping={},
            compliance_score=0.0,
            key_phrases=[],
            findings=[],
            recommendations=[],
            created_at=datetime.utcnow(),
            status="processing"
        )
        
        analyses[analysis_id] = result
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get analysis status/results
@app.get("/api/documents/analysis/{analysis_id}", response_model=AnalysisResult)
async def get_analysis(analysis_id: str, tenant_id: str, token: str = Depends(verify_token)):
    try:
        analysis = analyses.get(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Check tenant access through document
        doc = documents.get(analysis.document_id)
        if doc and doc.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Compare documents
@app.post("/api/documents/compare", response_model=ComparisonResult)
async def compare_documents(request: ComparisonRequest, token: str = Depends(verify_token)):
    try:
        # Check documents exist and belong to tenant
        doc1 = documents.get(request.document1_id)
        doc2 = documents.get(request.document2_id)
        
        if not doc1 or not doc2:
            raise HTTPException(status_code=404, detail="One or both documents not found")
        
        if doc1.tenant_id != request.tenant_id or doc2.tenant_id != request.tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Perform comparison (mock implementation)
        comparison_id = f"comparison_{uuid.uuid4()}"
        
        result = ComparisonResult(
            id=comparison_id,
            document1_id=request.document1_id,
            document2_id=request.document2_id,
            similarity_score=0.85,  # Mock score
            differences=[
                {
                    "section": "Risk Assessment",
                    "doc1_content": "Annual review required",
                    "doc2_content": "Semi-annual review required",
                    "severity": "medium"
                }
            ],
            common_elements=[
                "Business Impact Analysis methodology",
                "Incident response procedures",
                "Recovery strategies"
            ],
            compliance_gaps=[
                {
                    "requirement": "ISO 22301:2019 Section 8.4.2",
                    "gap": "Missing documentation of exercise results",
                    "priority": "high"
                }
            ],
            created_at=datetime.utcnow()
        )
        
        # Send event
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{EVENTBUS_URL}/api/events/publish",
                json={
                    "event_type": "bcm.document.comparison_completed",
                    "tenant_id": request.tenant_id,
                    "data": {
                        "comparison_id": comparison_id,
                        "document1_id": request.document1_id,
                        "document2_id": request.document2_id,
                        "similarity_score": result.similarity_score
                    }
                }
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background analysis function
async def perform_analysis(analysis_id: str, request: AnalysisRequest):
    """Perform document analysis in background"""
    try:
        await asyncio.sleep(2)  # Simulate processing time
        
        # Mock analysis results
        iso_mapping = {
            "4.1": {"coverage": 85, "sections": ["Context", "Stakeholder needs"]},
            "5.2": {"coverage": 92, "sections": ["Policy", "Leadership commitment"]},
            "8.4": {"coverage": 78, "sections": ["Business Continuity Procedures"]},
            "9.1": {"coverage": 95, "sections": ["Performance evaluation", "Monitoring"]}
        }
        
        key_phrases = [
            "business continuity",
            "risk assessment", 
            "recovery procedures",
            "stakeholder communication",
            "performance monitoring"
        ]
        
        findings = [
            "Document demonstrates strong leadership commitment (Section 5.2)",
            "Business impact analysis methodology is well documented",
            "Recovery time objectives clearly defined",
            "Missing documentation for exercise evaluation (Section 9.3)"
        ]
        
        recommendations = [
            "Add formal exercise evaluation procedures",
            "Include external stakeholder communication protocols",
            "Document management review processes",
            "Enhance risk assessment criteria"
        ]
        
        # Calculate compliance score
        total_coverage = sum(section["coverage"] for section in iso_mapping.values())
        compliance_score = total_coverage / len(iso_mapping)
        
        # Update analysis result
        analysis = analyses[analysis_id]
        analysis.iso_mapping = iso_mapping
        analysis.compliance_score = compliance_score
        analysis.key_phrases = key_phrases
        analysis.findings = findings
        analysis.recommendations = recommendations
        analysis.status = "completed"
        
        # Send completion event
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{EVENTBUS_URL}/api/events/publish",
                json={
                    "event_type": "bcm.document.analysis_completed",
                    "tenant_id": request.tenant_id,
                    "data": {
                        "analysis_id": analysis_id,
                        "document_id": request.document_id,
                        "compliance_score": compliance_score,
                        "findings_count": len(findings)
                    }
                }
            )
        
        logger.info(f"Analysis completed: {analysis_id}")
        
    except Exception as e:
        logger.error(f"Error in background analysis: {e}")
        if analysis_id in analyses:
            analyses[analysis_id].status = "failed"

# Statistics endpoint
@app.get("/api/documents/stats")
async def get_document_stats(tenant_id: str, token: str = Depends(verify_token)):
    try:
        tenant_docs = [doc for doc in documents.values() if doc.tenant_id == tenant_id]
        tenant_analyses = [
            analysis for analysis in analyses.values()
            if documents.get(analysis.document_id, {}).tenant_id == tenant_id
        ]
        
        # Category breakdown
        categories = {}
        for doc in tenant_docs:
            cat = doc.category or "uncategorized"
            categories[cat] = categories.get(cat, 0) + 1
        
        # Average compliance score
        completed_analyses = [a for a in tenant_analyses if a.status == "completed"]
        avg_compliance = 0
        if completed_analyses:
            avg_compliance = sum(a.compliance_score for a in completed_analyses) / len(completed_analyses)
        
        return {
            "tenant_id": tenant_id,
            "total_documents": len(tenant_docs),
            "total_analyses": len(tenant_analyses),
            "average_compliance_score": round(avg_compliance, 2),
            "categories": categories,
            "recent_uploads": len([d for d in tenant_docs if (datetime.utcnow() - d.uploaded_at).days <= 7])
        }
        
    except Exception as e:
        logger.error(f"Error getting document stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
