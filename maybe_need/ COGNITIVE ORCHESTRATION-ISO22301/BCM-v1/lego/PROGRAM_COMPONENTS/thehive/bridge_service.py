# -*- coding: utf-8 -*-
"""
TheHive-BCM Bridge Service
Main service that provides TheHive integration endpoints for BCM Platform
"""
import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import structlog
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn

from thehive_client import TheHiveClient, TheHiveCase, TheHiveAlert, BCMTheHiveIntegration

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Pydantic models for API
class BCMIncidentRequest(BaseModel):
    incident_id: str
    name: str
    description: str
    severity: str
    incident_type: str
    business_impact: Optional[str] = None
    affected_processes: Optional[List[str]] = []
    company_id: str
    tags: Optional[List[str]] = []

class BCMExerciseRequest(BaseModel):
    exercise_id: str
    name: str
    description: str
    exercise_type: str
    scenario: Optional[str] = None
    objectives: Optional[List[str]] = []
    participants: Optional[List[str]] = []
    company_id: str

class TheHiveCaseUpdate(BaseModel):
    case_id: str
    status: Optional[str] = None
    severity: Optional[int] = None
    owner: Optional[str] = None
    tags: Optional[List[str]] = None
    resolution: Optional[str] = None

# Security
security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key for requests"""
    expected_key = os.getenv('BRIDGE_API_KEY')
    if not expected_key or credentials.credentials != expected_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return credentials.credentials

# FastAPI app
app = FastAPI(
    title="TheHive-BCM Bridge Service",
    description="Integration service between TheHive and BCM Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for clients
thehive_client: Optional[TheHiveClient] = None
bcm_integration: Optional[BCMTheHiveIntegration] = None

@app.on_event("startup")
async def startup_event():
    """Initialize clients on startup"""
    global thehive_client, bcm_integration
    
    logger.info("Initializing TheHive-BCM Bridge Service")
    
    # Initialize TheHive client
    thehive_url = os.getenv('THEHIVE_URL', 'http://localhost:9000')
    thehive_api_key = os.getenv('THEHIVE_API_KEY')
    
    if not thehive_api_key:
        logger.error("THEHIVE_API_KEY environment variable is required")
        raise RuntimeError("Missing TheHive API key")
    
    thehive_client = TheHiveClient(
        url=thehive_url,
        api_key=thehive_api_key,
        verify_ssl=os.getenv('VERIFY_SSL', 'true').lower() == 'true'
    )
    
    # Initialize BCM integration
    odoo_webhook_url = os.getenv('ODOO_WEBHOOK_URL')
    bcm_integration = BCMTheHiveIntegration(
        thehive_client=thehive_client,
        odoo_webhook_url=odoo_webhook_url
    )
    
    logger.info("Bridge service initialized successfully")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "thehive": thehive_client is not None,
            "bcm_integration": bcm_integration is not None
        }
    }

@app.post("/api/v1/incident/create-case")
async def create_case_from_incident(
    request: BCMIncidentRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Create TheHive case from BCM incident"""
    if not bcm_integration:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info("Creating TheHive case from BCM incident", 
                   incident_id=request.incident_id)
        
        # Convert request to incident data
        incident_data = request.dict()
        
        # Create case in background
        background_tasks.add_task(
            _create_incident_case_task, incident_data
        )
        
        return {
            "status": "accepted",
            "message": "Case creation initiated",
            "incident_id": request.incident_id
        }
        
    except Exception as e:
        logger.error("Failed to create case from incident", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/exercise/create-case")
async def create_case_from_exercise(
    request: BCMExerciseRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Create TheHive case from BCM exercise"""
    if not bcm_integration:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info("Creating TheHive case from BCM exercise", 
                   exercise_id=request.exercise_id)
        
        # Convert request to exercise data
        exercise_data = request.dict()
        
        # Create case in background
        background_tasks.add_task(
            _create_exercise_case_task, exercise_data
        )
        
        return {
            "status": "accepted",
            "message": "Exercise case creation initiated",
            "exercise_id": request.exercise_id
        }
        
    except Exception as e:
        logger.error("Failed to create case from exercise", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/case/{case_id}")
async def update_case(
    case_id: str,
    request: TheHiveCaseUpdate,
    api_key: str = Depends(verify_api_key)
):
    """Update TheHive case"""
    if not thehive_client:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info("Updating TheHive case", case_id=case_id)
        
        # Prepare update data
        updates = {}
        if request.status:
            updates['status'] = request.status
        if request.severity:
            updates['severity'] = request.severity
        if request.owner:
            updates['owner'] = request.owner
        if request.tags:
            updates['tags'] = request.tags
        if request.resolution:
            updates['resolutionStatus'] = request.resolution
        
        # Update case
        result = thehive_client.update_case(case_id, updates)
        
        return {
            "status": "success",
            "case_id": case_id,
            "result": result
        }
        
    except Exception as e:
        logger.error("Failed to update case", case_id=case_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/case/{case_id}")
async def get_case(
    case_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get TheHive case details"""
    if not thehive_client:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        case_data = thehive_client.get_case(case_id)
        return case_data
        
    except Exception as e:
        logger.error("Failed to get case", case_id=case_id, error=str(e))
        raise HTTPException(status_code=404, detail="Case not found")

@app.get("/api/v1/cases")
async def list_cases(
    status: Optional[str] = None,
    severity: Optional[int] = None,
    tags: Optional[str] = None,
    limit: int = 50,
    api_key: str = Depends(verify_api_key)
):
    """List TheHive cases with filters"""
    if not thehive_client:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Parse tags
        tag_list = tags.split(',') if tags else None
        
        cases = thehive_client.list_cases(
            status=status,
            severity=severity,
            tags=tag_list,
            limit=limit
        )
        
        return {
            "cases": cases,
            "count": len(cases),
            "filters": {
                "status": status,
                "severity": severity,
                "tags": tag_list
            }
        }
        
    except Exception as e:
        logger.error("Failed to list cases", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/case/{case_id}/sync")
async def sync_case_to_bcm(
    case_id: str,
    bcm_incident_id: str,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Sync TheHive case updates to BCM incident"""
    if not bcm_integration:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info("Syncing case to BCM incident", 
                   case_id=case_id, bcm_incident_id=bcm_incident_id)
        
        # Sync in background
        background_tasks.add_task(
            _sync_case_to_bcm_task, case_id, bcm_incident_id
        )
        
        return {
            "status": "accepted",
            "message": "Sync initiated",
            "case_id": case_id,
            "bcm_incident_id": bcm_incident_id
        }
        
    except Exception as e:
        logger.error("Failed to sync case", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/metrics")
async def get_metrics(api_key: str = Depends(verify_api_key)):
    """Get service metrics"""
    try:
        # Basic metrics
        metrics = {
            "service": "thehive-bcm-bridge",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "uptime": "calculated_at_runtime",  # TODO: Implement actual uptime
            "status": "healthy"
        }
        
        # TheHive connection status
        if thehive_client:
            try:
                # Test connection by getting server status
                # Note: This is a placeholder - actual implementation may vary
                metrics["thehive_connection"] = "connected"
            except:
                metrics["thehive_connection"] = "disconnected"
        else:
            metrics["thehive_connection"] = "not_initialized"
        
        return metrics
        
    except Exception as e:
        logger.error("Failed to get metrics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Background tasks
async def _create_incident_case_task(incident_data: Dict):
    """Background task to create case from incident"""
    try:
        result = bcm_integration.create_bcm_incident_case(incident_data)
        logger.info("Case created successfully", 
                   case_id=result.get('_id'), 
                   incident_id=incident_data.get('incident_id'))
    except Exception as e:
        logger.error("Failed to create incident case in background", error=str(e))

async def _create_exercise_case_task(exercise_data: Dict):
    """Background task to create case from exercise"""
    try:
        result = bcm_integration.create_bcm_exercise_case(exercise_data)
        logger.info("Exercise case created successfully", 
                   case_id=result.get('_id'), 
                   exercise_id=exercise_data.get('exercise_id'))
    except Exception as e:
        logger.error("Failed to create exercise case in background", error=str(e))

async def _sync_case_to_bcm_task(case_id: str, bcm_incident_id: str):
    """Background task to sync case to BCM"""
    try:
        result = bcm_integration.sync_case_to_bcm_incident(case_id, bcm_incident_id)
        logger.info("Case synced successfully", 
                   case_id=case_id, 
                   bcm_incident_id=bcm_incident_id)
    except Exception as e:
        logger.error("Failed to sync case in background", error=str(e))

if __name__ == "__main__":
    # Load configuration
    port = int(os.getenv('PORT', '8090'))
    host = os.getenv('HOST', '0.0.0.0')
    log_level = os.getenv('LOG_LEVEL', 'info').lower()
    
    # Run server
    uvicorn.run(
        "bridge_service:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=False,
        access_log=True
    )
