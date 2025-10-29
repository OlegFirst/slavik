"""Pydantic models for Document Processor Adapter"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    """Supported document types"""
    POLICY = "policy"
    PROCEDURE = "procedure"
    PLAN = "plan"
    EVIDENCE = "evidence"
    CERTIFICATE = "certificate"
    REPORT = "report"
    TEMPLATE = "template"
    GENERAL = "general"

class DocumentStatus(str, Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing" 
    ANALYZED = "analyzed"
    FAILED = "failed"
    ARCHIVED = "archived"

class AnalysisEngine(str, Enum):
    """Available analysis engines"""
    LOCAL = "local"
    OPENAI = "openai"
    AZURE = "azure"

class DocumentUpload(BaseModel):
    """Document upload request model"""
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type")
    size: int = Field(..., ge=1, description="File size in bytes")
    tenant_id: str = Field(..., description="Tenant identifier")
    document_type: DocumentType = Field(default=DocumentType.GENERAL)
    description: Optional[str] = Field(None, description="Document description")
    audit_id: Optional[str] = Field(None, description="Associated audit ID")
    user_id: Optional[str] = Field(None, description="Uploader user ID")
    tags: List[str] = Field(default_factory=list, description="Document tags")
    
    @validator('filename')
    def validate_filename(cls, v):
        """Validate filename format"""
        if not v or len(v.strip()) == 0:
            raise ValueError('Filename cannot be empty')
        
        # Check for potentially dangerous characters
        dangerous_chars = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
        if any(char in v for char in dangerous_chars):
            raise ValueError('Filename contains invalid characters')
        
        return v.strip()
    
    @validator('size')
    def validate_size(cls, v):
        """Validate file size"""
        max_size = 50 * 1024 * 1024  # 50MB
        if v > max_size:
            raise ValueError(f'File size exceeds maximum allowed ({max_size} bytes)')
        return v

class ISOClause(BaseModel):
    """ISO 22301 clause model"""
    clause_number: str = Field(..., description="Clause identifier (e.g., '4.1')")
    title: str = Field(..., description="Clause title")
    description: str = Field(..., description="Clause description")
    requirements: List[str] = Field(default_factory=list, description="Specific requirements")
    keywords: List[str] = Field(default_factory=list, description="Keywords for matching")

class ComplianceScore(BaseModel):
    """Compliance scoring model"""
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall compliance score")
    clause_scores: Dict[str, float] = Field(default_factory=dict, description="Per-clause scores")
    coverage: float = Field(..., ge=0.0, le=1.0, description="Coverage percentage")
    gaps: List[str] = Field(default_factory=list, description="Identified gaps")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")

class DocumentAnalysisResult(BaseModel):
    """Complete document analysis result"""
    document_id: str = Field(..., description="Unique document identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    status: DocumentStatus = Field(..., description="Analysis status")
    
    # Content Analysis
    content_summary: Optional[str] = Field(None, description="Document summary")
    word_count: Optional[int] = Field(None, description="Total word count")
    language: Optional[str] = Field(None, description="Detected language")
    
    # Compliance Analysis
    compliance_score: Optional[ComplianceScore] = Field(None, description="ISO 22301 compliance")
    iso_clauses_found: List[ISOClause] = Field(default_factory=list, description="Identified clauses")
    
    # Quality Metrics
    readability_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Readability index")
    structure_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Document structure quality")
    
    # Extracted Entities
    key_terms: List[str] = Field(default_factory=list, description="Important terms identified")
    processes: List[str] = Field(default_factory=list, description="Business processes mentioned")
    risks: List[str] = Field(default_factory=list, description="Risks identified")
    controls: List[str] = Field(default_factory=list, description="Controls identified")
    
    # Metadata
    analysis_engine: AnalysisEngine = Field(..., description="Engine used for analysis")
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    processing_time: Optional[float] = Field(None, description="Analysis time in seconds")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Analysis confidence")
    
    # Error Information
    errors: List[str] = Field(default_factory=list, description="Processing errors")
    warnings: List[str] = Field(default_factory=list, description="Processing warnings")

class DocumentMetadata(BaseModel):
    """Document metadata model"""
    document_id: str = Field(..., description="Unique document identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type")
    size: int = Field(..., description="File size in bytes")
    document_type: DocumentType = Field(..., description="Document type")
    description: Optional[str] = Field(None, description="Document description")
    audit_id: Optional[str] = Field(None, description="Associated audit ID")
    user_id: Optional[str] = Field(None, description="Uploader user ID")
    tags: List[str] = Field(default_factory=list, description="Document tags")
    
    # Timestamps
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    analyzed_at: Optional[datetime] = Field(None, description="Analysis completion time")
    
    # Status
    status: DocumentStatus = Field(default=DocumentStatus.UPLOADED)
    version: int = Field(default=1, description="Document version")
    
    # Storage Information
    storage_path: Optional[str] = Field(None, description="File storage path")
    checksum: Optional[str] = Field(None, description="File checksum for integrity")

class DocumentComparison(BaseModel):
    """Document comparison result"""
    document_id_1: str = Field(..., description="First document ID")
    document_id_2: str = Field(..., description="Second document ID")
    tenant_id: str = Field(..., description="Tenant identifier")
    comparison_type: str = Field(default="compliance", description="Type of comparison")
    
    # Similarity Metrics
    content_similarity: float = Field(..., ge=0.0, le=1.0, description="Content similarity score")
    structure_similarity: float = Field(..., ge=0.0, le=1.0, description="Structure similarity")
    compliance_gap: float = Field(..., ge=0.0, le=1.0, description="Compliance score difference")
    
    # Detailed Analysis
    common_sections: List[str] = Field(default_factory=list, description="Sections found in both")
    unique_to_first: List[str] = Field(default_factory=list, description="Unique to first document")
    unique_to_second: List[str] = Field(default_factory=list, description="Unique to second document")
    
    # Recommendations
    merge_suggestions: List[str] = Field(default_factory=list, description="Merge recommendations")
    improvement_areas: List[str] = Field(default_factory=list, description="Areas for improvement")
    
    # Metadata
    comparison_date: datetime = Field(default_factory=datetime.utcnow)
    processing_time: Optional[float] = Field(None, description="Comparison time in seconds")

class SearchQuery(BaseModel):
    """Document search query model"""
    tenant_id: str = Field(..., description="Tenant identifier")
    query: Optional[str] = Field(None, description="Text search query")
    document_type: Optional[DocumentType] = Field(None, description="Filter by document type")
    audit_id: Optional[str] = Field(None, description="Filter by audit ID")
    user_id: Optional[str] = Field(None, description="Filter by uploader")
    tags: List[str] = Field(default_factory=list, description="Filter by tags")
    min_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum compliance score")
    max_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Maximum compliance score")
    date_from: Optional[datetime] = Field(None, description="Filter from date")
    date_to: Optional[datetime] = Field(None, description="Filter to date")
    limit: int = Field(default=10, ge=1, le=100, description="Results limit")
    offset: int = Field(default=0, ge=0, description="Results offset")

class SearchResult(BaseModel):
    """Search results model"""
    total_count: int = Field(..., description="Total matching documents")
    documents: List[DocumentMetadata] = Field(..., description="Found documents")
    query: SearchQuery = Field(..., description="Original search query")
    search_time: float = Field(..., description="Search execution time")

class EventData(BaseModel):
    """Event data model for EventBus integration"""
    event_type: str = Field(..., description="Event type identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    document_id: Optional[str] = Field(None, description="Document identifier")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event payload")
    correlation_id: Optional[str] = Field(None, description="Correlation identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ProcessingTask(BaseModel):
    """Background processing task model"""
    task_id: str = Field(..., description="Unique task identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    document_id: str = Field(..., description="Document identifier")
    task_type: str = Field(..., description="Task type (analyze, compare, etc.)")
    status: str = Field(default="pending", description="Task status")
    progress: float = Field(default=0.0, ge=0.0, le=1.0, description="Task progress")
    started_at: Optional[datetime] = Field(None, description="Task start time")
    completed_at: Optional[datetime] = Field(None, description="Task completion time")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result data")
