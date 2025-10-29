# -*- coding: utf-8 -*-
"""
Moodle-BCM Bridge Service
Main service that provides Moodle LMS integration endpoints for BCM Platform
"""
import os
import json
import logging
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional
import structlog
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import uvicorn

from moodle_client import MoodleClient, MoodleUser, MoodleCourse, BCMMoodleIntegration

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
class BCMUserRequest(BaseModel):
    login: str
    password: str
    first_name: str
    last_name: str
    email: EmailStr
    company_id: str
    department: Optional[str] = None
    job_title: Optional[str] = None
    city: Optional[str] = ""
    country_code: str = "UA"
    timezone: str = "Europe/Kiev"

class BCMTrainingRequest(BaseModel):
    name: str
    code: str
    description: str
    category_id: int = 1
    competency_areas: List[str] = []
    duration_hours: Optional[float] = None
    start_date: Optional[int] = None
    end_date: Optional[int] = None
    max_participants: Optional[int] = None
    is_mandatory: bool = False
    certification_required: bool = False
    company_id: str

class BCMEnrollmentRequest(BaseModel):
    user_id: int
    course_id: int
    role: str = "bcm_student"
    start_date: Optional[int] = None
    end_date: Optional[int] = None

class BCMTrainingUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[int] = None
    end_date: Optional[int] = None
    visible: Optional[bool] = None

class BCMCompetencyAssessment(BaseModel):
    user_id: int
    competency_id: str
    assessment_score: float
    assessment_date: Optional[int] = None
    assessor_id: Optional[int] = None
    evidence_notes: Optional[str] = None
    company_id: str

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
    title="Moodle-BCM Bridge Service",
    description="Integration service between Moodle LMS and BCM Platform",
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
moodle_client: Optional[MoodleClient] = None
bcm_integration: Optional[BCMMoodleIntegration] = None

@app.on_event("startup")
async def startup_event():
    """Initialize clients on startup"""
    global moodle_client, bcm_integration
    
    logger.info("Initializing Moodle-BCM Bridge Service")
    
    # Initialize Moodle client
    moodle_url = os.getenv('MOODLE_URL', 'http://localhost')
    moodle_token = os.getenv('MOODLE_TOKEN')
    
    if not moodle_token:
        logger.error("MOODLE_TOKEN environment variable is required")
        raise RuntimeError("Missing Moodle token")
    
    moodle_client = MoodleClient(
        url=moodle_url,
        token=moodle_token,
        verify_ssl=os.getenv('VERIFY_SSL', 'true').lower() == 'true'
    )
    
    # Initialize BCM integration
    bcm_webhook_url = os.getenv('BCM_WEBHOOK_URL')
    bcm_integration = BCMMoodleIntegration(
        moodle_client=moodle_client,
        bcm_webhook_url=bcm_webhook_url
    )
    
    # Test connection
    try:
        site_info = moodle_client.get_site_info()
        logger.info("Connected to Moodle", site=site_info.get('sitename', 'Unknown'))
    except Exception as e:
        logger.error("Failed to connect to Moodle", error=str(e))
        raise
    
    logger.info("Bridge service initialized successfully")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    moodle_status = "unknown"
    if moodle_client:
        try:
            moodle_client.get_site_info()
            moodle_status = "connected"
        except:
            moodle_status = "disconnected"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "moodle": moodle_status,
            "bcm_integration": bcm_integration is not None
        }
    }

@app.post("/api/v1/user/create")
async def create_bcm_user(
    request: BCMUserRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Create BCM user in Moodle LMS"""
    if not bcm_integration:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info("Creating BCM user in Moodle", 
                   email=request.email, company=request.company_id)
        
        # Check if user already exists
        existing_user = moodle_client.get_user_by_email(request.email)
        if existing_user:
            return {
                "status": "exists",
                "message": "User already exists",
                "user_id": existing_user['id'],
                "username": existing_user['username']
            }
        
        # Convert request to user data
        user_data = request.dict()
        
        # Create user in background
        background_tasks.add_task(_create_user_task, user_data)
        
        return {
            "status": "accepted",
            "message": "User creation initiated",
            "email": request.email
        }
        
    except Exception as e:
        logger.error("Failed to create BCM user", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/training/create")
async def create_bcm_training(
    request: BCMTrainingRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Create BCM training course in Moodle"""
    if not bcm_integration:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info("Creating BCM training course", 
                   name=request.name, code=request.code)
        
        # Check if course already exists
        shortname = f"BCM-{request.code}"
        existing_course = moodle_client.get_course_by_shortname(shortname)
        if existing_course:
            return {
                "status": "exists",
                "message": "Training course already exists",
                "course_id": existing_course['id'],
                "shortname": existing_course['shortname']
            }
        
        # Convert request to course data
        training_data = request.dict()
        
        # Create course in background
        background_tasks.add_task(_create_training_task, training_data)
        
        return {
            "status": "accepted",
            "message": "Training course creation initiated",
            "code": request.code
        }
        
    except Exception as e:
        logger.error("Failed to create BCM training", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/enrollment/create")
async def enroll_user_in_training(
    request: BCMEnrollmentRequest,
    api_key: str = Depends(verify_api_key)
):
    """Enroll BCM user in training course"""
    if not bcm_integration:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info("Enrolling user in training", 
                   user_id=request.user_id, course_id=request.course_id)
        
        success = bcm_integration.enroll_bcm_user(
            user_id=request.user_id,
            course_id=request.course_id,
            role=request.role
        )
        
        if success:
            return {
                "status": "success",
                "message": "User enrolled successfully",
                "user_id": request.user_id,
                "course_id": request.course_id,
                "role": request.role
            }
        else:
            raise HTTPException(status_code=500, detail="Enrollment failed")
            
    except Exception as e:
        logger.error("Failed to enroll user", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/user/{user_id}/progress")
async def get_user_training_progress(
    user_id: int,
    course_id: Optional[int] = Query(None),
    api_key: str = Depends(verify_api_key)
):
    """Get user training progress"""
    if not moodle_client:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        if course_id:
            # Get progress for specific course
            completion = moodle_client.get_course_completions(course_id)
            grades = moodle_client.get_user_grades(course_id, user_id)
            
            return {
                "user_id": user_id,
                "course_id": course_id,
                "completion": completion,
                "grades": grades
            }
        else:
            # Get overall progress - would need additional API calls
            return {
                "user_id": user_id,
                "overall_progress": "Not implemented - specify course_id"
            }
            
    except Exception as e:
        logger.error("Failed to get user progress", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/company/{company_id}/training-analytics")
async def get_company_training_analytics(
    company_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get training analytics for BCM company"""
    if not bcm_integration:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        analytics = bcm_integration.get_bcm_training_progress(company_id)
        
        return {
            "company_id": company_id,
            "analytics": analytics,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get training analytics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/competency/assess")
async def assess_user_competency(
    request: BCMCompetencyAssessment,
    api_key: str = Depends(verify_api_key)
):
    """Assess user competency"""
    if not bcm_integration:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info("Assessing user competency", 
                   user_id=request.user_id, competency=request.competency_id)
        
        # This would integrate with Moodle competency system
        assessment_result = {
            "user_id": request.user_id,
            "competency_id": request.competency_id,
            "score": request.assessment_score,
            "status": "competent" if request.assessment_score >= 0.7 else "not_competent",
            "assessment_date": request.assessment_date or int(time.time()),
            "assessor_id": request.assessor_id,
            "evidence": request.evidence_notes
        }
        
        return {
            "status": "success",
            "assessment": assessment_result
        }
        
    except Exception as e:
        logger.error("Failed to assess competency", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/competency/framework/sync")
async def sync_bcm_competency_framework(
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Sync BCM competency framework to Moodle"""
    if not bcm_integration:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info("Syncing BCM competency framework")
        
        # Sync in background
        background_tasks.add_task(_sync_competency_framework_task)
        
        return {
            "status": "accepted",
            "message": "Competency framework sync initiated"
        }
        
    except Exception as e:
        logger.error("Failed to sync competency framework", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/courses")
async def list_bcm_courses(
    company_id: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    api_key: str = Depends(verify_api_key)
):
    """List BCM training courses"""
    if not moodle_client:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # This would require custom Moodle web service or database query
        # For now, return placeholder
        courses = {
            "courses": [],
            "total": 0,
            "filters": {
                "company_id": company_id,
                "category": category
            },
            "message": "Course listing requires custom Moodle web service"
        }
        
        return courses
        
    except Exception as e:
        logger.error("Failed to list courses", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/metrics")
async def get_metrics(api_key: str = Depends(verify_api_key)):
    """Get service metrics"""
    try:
        metrics = {
            "service": "moodle-bcm-bridge",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "status": "healthy"
        }
        
        # Moodle connection status
        if moodle_client:
            try:
                site_info = moodle_client.get_site_info()
                metrics["moodle_connection"] = "connected"
                metrics["moodle_site"] = site_info.get('sitename', 'Unknown')
                metrics["moodle_version"] = site_info.get('release', 'Unknown')
            except:
                metrics["moodle_connection"] = "disconnected"
        else:
            metrics["moodle_connection"] = "not_initialized"
        
        return metrics
        
    except Exception as e:
        logger.error("Failed to get metrics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Background tasks
async def _create_user_task(user_data: Dict):
    """Background task to create user"""
    try:
        result = bcm_integration.create_bcm_user(user_data)
        logger.info("BCM user created successfully", 
                   user_id=result.get('id'), 
                   username=result.get('username'))
    except Exception as e:
        logger.error("Failed to create BCM user in background", error=str(e))

async def _create_training_task(training_data: Dict):
    """Background task to create training course"""
    try:
        result = bcm_integration.create_bcm_training_course(training_data)
        logger.info("BCM training created successfully", 
                   course_id=result.get('id'), 
                   shortname=result.get('shortname'))
    except Exception as e:
        logger.error("Failed to create BCM training in background", error=str(e))

async def _sync_competency_framework_task():
    """Background task to sync competency framework"""
    try:
        result = bcm_integration.sync_bcm_competencies()
        logger.info("BCM competency framework synced successfully", 
                   framework_id=result.get('framework', {}).get('id'))
    except Exception as e:
        logger.error("Failed to sync competency framework in background", error=str(e))

if __name__ == "__main__":
    # Load configuration
    port = int(os.getenv('PORT', '8092'))
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
