"""
Organization Data Collector API
Endpoints for collecting organization data to build Digital Twins
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel, Field

from core.collectors.organization_data_collector import (
    OrganizationDataCollector,
    DataCollectionMethod,
    DataCategory
)
from storage import PostgreSQLStorage
from api.auth.dependencies import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class CollectionSessionRequest(BaseModel):
    """Start data collection session"""
    organization_id: str = Field(..., description="Organization ID")
    collection_plan: Dict[str, Any] = Field(
        ...,
        description="Collection plan with methods and categories"
    )


class CollectionSessionResponse(BaseModel):
    """Collection session response"""
    session_id: str
    organization_id: str
    status: str
    created_at: str
    workflow: Optional[Dict[str, Any]] = None


class CollectDataRequest(BaseModel):
    """Collect data request"""
    session_id: str = Field(..., description="Collection session ID")
    method: str = Field(..., description="Collection method")
    category: str = Field(..., description="Data category")
    data: Dict[str, Any] = Field(..., description="Data to collect")


class CollectDataResponse(BaseModel):
    """Collect data response"""
    collection_id: str
    session_id: str
    method: str
    category: str
    quality_score: float
    validation_passed: bool
    stored: bool
    warnings: List[str] = []


class SessionStatusResponse(BaseModel):
    """Session status response"""
    session_id: str
    organization_id: str
    status: str
    progress_percentage: float
    completed_categories: List[str]
    pending_categories: List[str]
    quality_metrics: Dict[str, Any]


# ============================================
# DEPENDENCIES
# ============================================

def get_storage() -> PostgreSQLStorage:
    """Get storage (placeholder - injected by app)"""
    pass


def get_collector() -> OrganizationDataCollector:
    """Get data collector instance"""
    return OrganizationDataCollector()


# ============================================
# ENDPOINTS
# ============================================

@router.post("/sessions", response_model=CollectionSessionResponse)
async def start_collection_session(
    request: CollectionSessionRequest,
    collector: OrganizationDataCollector = Depends(get_collector),
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Start data collection session for organization

    **Collection Plan Format:**
    ```json
    {
      "methods": ["interview", "document_analysis", "api_extraction"],
      "categories": [
        "structure",
        "processes",
        "technology",
        "financial"
      ],
      "quality_threshold": 0.7
    }
    ```

    **Multi-tenancy:** Organization must belong to user's tenant.
    """
    try:
        user_id = current_user.get('id')
        organization_id = request.organization_id

        logger.info(f"User {user_id} starting collection session for org: {organization_id}")

        # Verify organization access
        org = await storage.get_organization(id=organization_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        if org.tenant_id != current_user.get('tenant_id'):
            raise HTTPException(
                status_code=403,
                detail="Not authorized to collect data for this organization"
            )

        # Start session
        session = await collector.start_collection_session(
            organization_id=organization_id,
            collection_plan=request.collection_plan
        )

        return CollectionSessionResponse(
            session_id=session["session_id"],
            organization_id=organization_id,
            status=session["status"],
            created_at=session["created_at"],
            workflow=session.get("workflow")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start collection session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collect", response_model=CollectDataResponse)
async def collect_data(
    request: CollectDataRequest,
    collector: OrganizationDataCollector = Depends(get_collector),
    current_user = Depends(get_current_active_user)
):
    """
    Collect data using specified method and category

    **Collection Methods:**
    - interview: From stakeholder interviews
    - document_analysis: From document parsing
    - system_integration: From external systems
    - survey: From surveys
    - observation: From direct observation
    - api_extraction: From APIs
    - database_query: From databases
    - file_upload: From uploaded files

    **Data Categories:**
    - structure: Organizational structure
    - processes: Business processes
    - technology: Technology infrastructure
    - financial: Financial data
    - hr: Human resources
    - operations: Operations data
    - compliance: Compliance data
    - strategic: Strategic planning
    - performance: Performance metrics
    - stakeholders: Stakeholder information
    """
    try:
        user_id = current_user.get('id')
        session_id = request.session_id

        logger.info(
            f"User {user_id} collecting data: "
            f"session={session_id}, method={request.method}, category={request.category}"
        )

        # Parse enums
        try:
            method = DataCollectionMethod(request.method)
            category = DataCategory(request.category)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid method or category: {e}"
            )

        # Collect data
        result = await collector.collect_data(
            session_id=session_id,
            method=method,
            category=category,
            data=request.data
        )

        return CollectDataResponse(
            collection_id=result["collection_id"],
            session_id=session_id,
            method=request.method,
            category=request.category,
            quality_score=result["quality_score"],
            validation_passed=result["validation"]["passed"],
            stored=result.get("stored", False),
            warnings=result["validation"].get("warnings", [])
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to collect data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/{session_id}")
async def upload_data_file(
    session_id: str,
    category: str,
    file: UploadFile = File(...),
    collector: OrganizationDataCollector = Depends(get_collector),
    current_user = Depends(get_current_active_user)
):
    """
    Upload data file for collection

    Supports:
    - JSON files
    - CSV files
    - Excel files (.xlsx)
    - PDF documents (text extraction)

    File will be processed and data extracted based on category.
    """
    try:
        user_id = current_user.get('id')

        logger.info(f"User {user_id} uploading file: {file.filename} for session {session_id}")

        # Read file content
        content = await file.read()

        # Parse category
        try:
            data_category = DataCategory(category)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")

        # Process file based on type
        filename = file.filename.lower()

        if filename.endswith('.json'):
            import json
            data = json.loads(content)

        elif filename.endswith('.csv'):
            # CSV processing would go here
            raise HTTPException(
                status_code=501,
                detail="CSV processing not yet implemented"
            )

        elif filename.endswith('.xlsx'):
            # Excel processing would go here
            raise HTTPException(
                status_code=501,
                detail="Excel processing not yet implemented"
            )

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.filename}"
            )

        # Collect data
        result = await collector.collect_data(
            session_id=session_id,
            method=DataCollectionMethod.FILE_UPLOAD,
            category=data_category,
            data={
                "filename": file.filename,
                "content_type": file.content_type,
                "data": data
            }
        )

        return {
            "status": "processed",
            "filename": file.filename,
            "collection_id": result["collection_id"],
            "quality_score": result["quality_score"],
            "validation_passed": result["validation"]["passed"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: str,
    collector: OrganizationDataCollector = Depends(get_collector),
    current_user = Depends(get_current_active_user)
):
    """
    Get collection session status

    Returns progress and quality metrics.
    """
    try:
        logger.info(f"Getting status for session: {session_id}")

        status = await collector.get_session_status(session_id)

        if not status:
            raise HTTPException(status_code=404, detail="Session not found")

        return SessionStatusResponse(
            session_id=session_id,
            organization_id=status["organization_id"],
            status=status["status"],
            progress_percentage=status["progress_percentage"],
            completed_categories=status["completed_categories"],
            pending_categories=status["pending_categories"],
            quality_metrics=status["quality_metrics"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/complete")
async def complete_collection_session(
    session_id: str,
    collector: OrganizationDataCollector = Depends(get_collector),
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Complete collection session and finalize Digital Twin

    Validates all collected data and creates/updates Digital Twin.

    **Process:**
    1. Validate all collected data
    2. Check completeness
    3. Generate Digital Twin model
    4. Store in database
    5. Return twin_id

    Returns Digital Twin ID for further operations.
    """
    try:
        user_id = current_user.get('id')

        logger.info(f"User {user_id} completing collection session: {session_id}")

        # Complete session
        result = await collector.complete_session(session_id)

        if not result["success"]:
            return {
                "status": "incomplete",
                "session_id": session_id,
                "errors": result["errors"],
                "warnings": result.get("warnings", []),
                "message": "Session cannot be completed. Fix errors first."
            }

        # Get session data
        session_data = result["session_data"]

        # Create/update Digital Twin in database
        organization_id = session_data["organization_id"]

        org = await storage.get_organization(id=organization_id)

        if org:
            # Update existing
            await storage.update_organization(organization_id, {
                "bcm_data": session_data["collected_data"],
                "maturity_level": session_data["quality_metrics"]["overall_quality"],
                "updated_at": datetime.utcnow()
            })
        else:
            # Create new (shouldn't happen, but just in case)
            raise HTTPException(
                status_code=404,
                detail="Organization not found"
            )

        return {
            "status": "completed",
            "session_id": session_id,
            "organization_id": organization_id,
            "twin_id": org.twin_id,
            "quality_score": session_data["quality_metrics"]["overall_quality"],
            "completed_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to complete session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/collected-data")
async def get_collected_data(
    session_id: str,
    category: Optional[str] = None,
    collector: OrganizationDataCollector = Depends(get_collector),
    current_user = Depends(get_current_active_user)
):
    """
    Get collected data from session

    Optionally filter by category.
    """
    try:
        logger.info(f"Getting collected data for session: {session_id}")

        data = await collector.get_collected_data(
            session_id=session_id,
            category=category
        )

        if not data:
            raise HTTPException(status_code=404, detail="No data found")

        return {
            "session_id": session_id,
            "category_filter": category,
            "data": data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get collected data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def cancel_collection_session(
    session_id: str,
    collector: OrganizationDataCollector = Depends(get_collector),
    current_user = Depends(get_current_active_user)
):
    """
    Cancel and delete collection session

    Removes all collected data for session.
    Use when session needs to be restarted.
    """
    try:
        user_id = current_user.get('id')

        logger.info(f"User {user_id} canceling collection session: {session_id}")

        await collector.cancel_session(session_id)

        return {
            "status": "canceled",
            "session_id": session_id,
            "canceled_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to cancel session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/methods")
async def list_collection_methods(
    current_user = Depends(get_current_active_user)
):
    """
    List available data collection methods

    Returns all 8 collection methods with descriptions.
    """
    methods = [
        {
            "method": "interview",
            "name": "Stakeholder Interview",
            "description": "Collect data through structured interviews with stakeholders",
            "best_for": ["qualitative data", "organizational culture", "processes"]
        },
        {
            "method": "document_analysis",
            "name": "Document Analysis",
            "description": "Extract data from organizational documents",
            "best_for": ["policies", "procedures", "compliance documentation"]
        },
        {
            "method": "system_integration",
            "name": "System Integration",
            "description": "Import data from external systems",
            "best_for": ["ERP data", "CMDB", "monitoring systems"]
        },
        {
            "method": "survey",
            "name": "Survey",
            "description": "Collect data via surveys and questionnaires",
            "best_for": ["employee feedback", "risk perception", "awareness levels"]
        },
        {
            "method": "observation",
            "name": "Direct Observation",
            "description": "Collect data through direct observation",
            "best_for": ["workflow analysis", "facility assessment"]
        },
        {
            "method": "api_extraction",
            "name": "API Extraction",
            "description": "Extract data via APIs",
            "best_for": ["cloud services", "SaaS tools", "real-time data"]
        },
        {
            "method": "database_query",
            "name": "Database Query",
            "description": "Query data from databases",
            "best_for": ["historical data", "structured data", "analytics"]
        },
        {
            "method": "file_upload",
            "name": "File Upload",
            "description": "Upload data files (JSON, CSV, Excel)",
            "best_for": ["batch imports", "migration", "quick setup"]
        }
    ]

    return {
        "total": len(methods),
        "methods": methods
    }


@router.get("/categories")
async def list_data_categories(
    current_user = Depends(get_current_active_user)
):
    """
    List available data categories

    Returns all 10 data categories with descriptions.
    """
    categories = [
        {
            "category": "structure",
            "name": "Organizational Structure",
            "description": "Org chart, departments, reporting lines",
            "required_for": "Digital Twin foundation"
        },
        {
            "category": "processes",
            "name": "Business Processes",
            "description": "Critical processes, workflows, dependencies",
            "required_for": "BIA and impact analysis"
        },
        {
            "category": "technology",
            "name": "Technology Infrastructure",
            "description": "IT systems, applications, infrastructure",
            "required_for": "Technical recovery planning"
        },
        {
            "category": "financial",
            "name": "Financial Data",
            "description": "Revenue, costs, budgets, financial impact",
            "required_for": "Impact calculations"
        },
        {
            "category": "hr",
            "name": "Human Resources",
            "description": "Employee data, skills, key personnel",
            "required_for": "Resource planning"
        },
        {
            "category": "operations",
            "name": "Operations Data",
            "description": "Operational metrics, KPIs, performance",
            "required_for": "Baseline establishment"
        },
        {
            "category": "compliance",
            "name": "Compliance Data",
            "description": "Regulatory requirements, compliance status",
            "required_for": "Regulatory compliance"
        },
        {
            "category": "strategic",
            "name": "Strategic Planning",
            "description": "Strategic objectives, initiatives, goals",
            "required_for": "Alignment with strategy"
        },
        {
            "category": "performance",
            "name": "Performance Metrics",
            "description": "KPIs, SLAs, performance history",
            "required_for": "Trend analysis"
        },
        {
            "category": "stakeholders",
            "name": "Stakeholder Information",
            "description": "Stakeholders, contacts, relationships",
            "required_for": "Communication planning"
        }
    ]

    return {
        "total": len(categories),
        "categories": categories
    }
