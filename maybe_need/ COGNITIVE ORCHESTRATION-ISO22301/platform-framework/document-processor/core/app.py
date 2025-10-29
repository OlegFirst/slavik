"""
Document Processor Adapter for BCM Platform

Processes documents uploaded via portal and analyzes them for:
- ISO 22301 compliance scoring
- Clause extraction and mapping
- Gap analysis and recommendations
- Evidence categorization
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime

from config import Config
from models import DocumentAnalysisResult, DocumentUpload, DocumentStatus
from services.eventbus import EventBusService
from services.document_processor import DocumentProcessorService
from services.processor import DocumentProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BCM Document Processor Adapter",
    description="Document analysis and compliance scoring for BCM Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
eventbus_service: EventBusService = None
document_service: DocumentProcessorService = None
processor: DocumentProcessor = None
config = Config()

@app.on_event("startup")
async def startup():
    """Initialize services and event subscriptions"""
    global eventbus_service, document_service, processor
    
    logger.info("Starting Document Processor Adapter...")
    
    # Initialize services
    eventbus_service = EventBusService(config)
    document_service = DocumentProcessorService(config)
    processor = DocumentProcessor(eventbus_service, document_service)
    
    # Subscribe to relevant events
    await eventbus_service.subscribe("bcm.doc.uploaded", processor.handle_document_uploaded)
    await eventbus_service.subscribe("bcm.evidence.uploaded", processor.handle_evidence_uploaded)
    
    logger.info("Document Processor Adapter started successfully")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    if eventbus_service:
        await eventbus_service.disconnect()
    logger.info("Document Processor Adapter shut down")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    dependencies = {
        "eventbus": "healthy" if eventbus_service and eventbus_service.is_connected() else "unhealthy",
        "document_service": "healthy" if document_service else "unhealthy"
    }
    
    status = "healthy" if all(dep == "healthy" for dep in dependencies.values()) else "unhealthy"
    
    return {
        "status": status,
        "service": "document-processor",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": dependencies
    }

@app.post("/api/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    tenant_id: str = Form(...),
    document_type: str = Form(default="general"),
    description: Optional[str] = Form(default=None),
    audit_id: Optional[str] = Form(default=None),
    user_id: Optional[str] = Form(default=None)
):
    """Upload document for analysis"""
    try:
        # Validate file type
        allowed_types = ['pdf', 'docx', 'doc', 'txt']
        file_extension = file.filename.split('.')[-1].lower()
        
        if file_extension not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"File type .{file_extension} not supported. Allowed: {allowed_types}"
            )
        
        # Read file content
        content = await file.read()
        
        # Create document record
        document_upload = DocumentUpload(
            filename=file.filename,
            content_type=file.content_type,
            size=len(content),
            tenant_id=tenant_id,
            document_type=document_type,
            description=description,
            audit_id=audit_id,
            user_id=user_id
        )
        
        # Store document and get document_id
        document_id = await document_service.store_document(document_upload, content)
        
        # Publish upload event
        await eventbus_service.publish({
            "event_type": "bcm.doc.uploaded",
            "tenant_id": tenant_id,
            "data": {
                "document_id": document_id,
                "filename": file.filename,
                "document_type": document_type,
                "description": description,
                "audit_id": audit_id,
                "user_id": user_id,
                "size": len(content)
            }
        })
        
        return {
            "status": "success",
            "document_id": document_id,
            "message": "Document uploaded successfully. Analysis will begin shortly."
        }
        
    except Exception as e:
        logger.error(f"Document upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents/{document_id}/status")
async def get_document_status(document_id: str, tenant_id: str):
    """Get document analysis status"""
    try:
        status = await document_service.get_document_status(document_id, tenant_id)
        return status
    except Exception as e:
        logger.error(f"Failed to get document status: {str(e)}")
        raise HTTPException(status_code=404, detail="Document not found")

@app.get("/api/documents/{document_id}/analysis")
async def get_document_analysis(document_id: str, tenant_id: str):
    """Get document analysis results"""
    try:
        analysis = await document_service.get_analysis_result(document_id, tenant_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return analysis
    except Exception as e:
        logger.error(f"Failed to get document analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/documents/compare")
async def compare_documents(
    tenant_id: str = Form(...),
    document_id_1: str = Form(...),
    document_id_2: str = Form(...),
    comparison_type: str = Form(default="compliance")
):
    """Compare two documents for compliance gaps"""
    try:
        comparison_result = await document_service.compare_documents(
            document_id_1, document_id_2, tenant_id, comparison_type
        )
        
        # Publish comparison event
        await eventbus_service.publish({
            "event_type": "bcm.doc.compared",
            "tenant_id": tenant_id,
            "data": {
                "document_id_1": document_id_1,
                "document_id_2": document_id_2,
                "comparison_type": comparison_type,
                "result": comparison_result
            }
        })
        
        return comparison_result
        
    except Exception as e:
        logger.error(f"Document comparison failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents/search")
async def search_documents(
    tenant_id: str,
    query: Optional[str] = None,
    document_type: Optional[str] = None,
    audit_id: Optional[str] = None,
    min_score: Optional[float] = None,
    limit: int = 10,
    offset: int = 0
):
    """Search documents by various criteria"""
    try:
        search_params = {
            "tenant_id": tenant_id,
            "query": query,
            "document_type": document_type,
            "audit_id": audit_id,
            "min_score": min_score,
            "limit": limit,
            "offset": offset
        }
        
        results = await document_service.search_documents(search_params)
        return results
        
    except Exception as e:
        logger.error(f"Document search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/documents/{document_id}/reanalyze")
async def reanalyze_document(document_id: str, tenant_id: str):
    """Trigger re-analysis of a document"""
    try:
        # Verify document exists and belongs to tenant
        status = await document_service.get_document_status(document_id, tenant_id)
        if not status:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Publish re-analysis event
        await eventbus_service.publish({
            "event_type": "bcm.doc.reanalyze_requested",
            "tenant_id": tenant_id,
            "data": {
                "document_id": document_id,
                "requested_by": "api"
            }
        })
        
        return {
            "status": "success",
            "message": "Document re-analysis initiated"
        }
        
    except Exception as e:
        logger.error(f"Document re-analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8003,
        log_level="info"
    )
