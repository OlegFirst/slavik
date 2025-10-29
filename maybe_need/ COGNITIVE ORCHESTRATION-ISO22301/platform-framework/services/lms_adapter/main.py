"""
LMS Adapter Service - Multi-LMS Integration
ISO 22301 BCM Platform LMS Management (Moodle, Open edX, Canvas)
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import asyncio
import json
import os
import httpx
import uuid
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
EVENTBUS_URL = os.getenv("EVENTBUS_URL", "http://localhost:8001")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8081,http://localhost:8069").split(",")

# LMS Configuration Models
class LMSConfig(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=255)
    lms_type: str = Field(..., description="moodle, openedx, canvas")
    base_url: HttpUrl
    api_key: str = Field(..., min_length=1)
    api_secret: Optional[str] = None
    tenant_id: str = Field(..., min_length=1)
    is_active: bool = Field(default=True)
    settings: Dict[str, Any] = Field(default={})

class Course(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    instructor: Optional[str] = None
    duration_hours: Optional[int] = None
    enrollment_count: Optional[int] = None
    completion_rate: Optional[float] = None
    lms_course_id: str
    lms_type: str
    is_active: bool = Field(default=True)

class Enrollment(BaseModel):
    id: Optional[str] = None
    course_id: str
    user_id: str
    user_email: str
    enrolled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress_percent: Optional[float] = 0.0
    status: str = Field(default="ENROLLED")  # ENROLLED, IN_PROGRESS, COMPLETED, DROPPED
    grade: Optional[float] = None
    certificate_url: Optional[str] = None

# Abstract LMS Adapter
class LMSAdapter(ABC):
    def __init__(self, config: LMSConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=30.0)
    
    @abstractmethod
    async def authenticate(self) -> bool:
        pass
    
    @abstractmethod
    async def get_courses(self) -> List[Course]:
        pass
    
    @abstractmethod
    async def get_course(self, course_id: str) -> Course:
        pass
    
    @abstractmethod
    async def enroll_user(self, course_id: str, user_email: str) -> Enrollment:
        pass
    
    @abstractmethod
    async def get_user_enrollments(self, user_email: str) -> List[Enrollment]:
        pass
    
    @abstractmethod
    async def get_user_progress(self, course_id: str, user_email: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def launch_course(self, course_id: str, user_email: str) -> str:
        pass

# Moodle Adapter
class MoodleAdapter(LMSAdapter):
    async def authenticate(self) -> bool:
        try:
            response = await self.client.get(
                f"{self.config.base_url}/webservice/rest/server.php",
                params={
                    "wstoken": self.config.api_key,
                    "wsfunction": "core_webservice_get_site_info",
                    "moodlewsrestformat": "json"
                }
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Moodle authentication failed: {e}")
            return False
    
    async def get_courses(self) -> List[Course]:
        try:
            response = await self.client.get(
                f"{self.config.base_url}/webservice/rest/server.php",
                params={
                    "wstoken": self.config.api_key,
                    "wsfunction": "core_course_get_courses",
                    "moodlewsrestformat": "json"
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch courses")
            
            courses_data = response.json()
            courses = []
            
            for course_data in courses_data:
                course = Course(
                    id=str(uuid.uuid4()),
                    title=course_data.get("fullname", ""),
                    description=course_data.get("summary", ""),
                    category=course_data.get("categoryname"),
                    lms_course_id=str(course_data.get("id")),
                    lms_type="moodle",
                    enrollment_count=course_data.get("enrolledusercount", 0)
                )
                courses.append(course)
            
            return courses
        except Exception as e:
            logger.error(f"Failed to get Moodle courses: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_course(self, course_id: str) -> Course:
        # Implementation for getting specific course
        courses = await self.get_courses()
        for course in courses:
            if course.lms_course_id == course_id:
                return course
        raise HTTPException(status_code=404, detail="Course not found")
    
    async def enroll_user(self, course_id: str, user_email: str) -> Enrollment:
        try:
            # First, find or create user
            user_response = await self.client.get(
                f"{self.config.base_url}/webservice/rest/server.php",
                params={
                    "wstoken": self.config.api_key,
                    "wsfunction": "core_user_get_users_by_field",
                    "field": "email",
                    "values[0]": user_email,
                    "moodlewsrestformat": "json"
                }
            )
            
            users = user_response.json()
            if not users:
                raise HTTPException(status_code=404, detail="User not found")
            
            user_id = users[0]["id"]
            
            # Enroll user in course
            enroll_response = await self.client.post(
                f"{self.config.base_url}/webservice/rest/server.php",
                data={
                    "wstoken": self.config.api_key,
                    "wsfunction": "enrol_manual_enrol_users",
                    "enrolments[0][roleid]": 5,  # Student role
                    "enrolments[0][userid]": user_id,
                    "enrolments[0][courseid]": course_id,
                    "moodlewsrestformat": "json"
                }
            )
            
            if enroll_response.status_code == 200:
                enrollment = Enrollment(
                    id=str(uuid.uuid4()),
                    course_id=course_id,
                    user_id=str(user_id),
                    user_email=user_email,
                    enrolled_at=datetime.utcnow(),
                    status="ENROLLED"
                )
                return enrollment
            else:
                raise HTTPException(status_code=500, detail="Enrollment failed")
                
        except Exception as e:
            logger.error(f"Moodle enrollment failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_user_enrollments(self, user_email: str) -> List[Enrollment]:
        # Implementation for getting user enrollments
        return []
    
    async def get_user_progress(self, course_id: str, user_email: str) -> Dict[str, Any]:
        # Implementation for getting user progress
        return {"progress_percent": 0.0, "status": "ENROLLED"}
    
    async def launch_course(self, course_id: str, user_email: str) -> str:
        # Generate SSO launch URL
        return f"{self.config.base_url}/course/view.php?id={course_id}"

# Open edX Adapter
class OpenEdXAdapter(LMSAdapter):
    async def authenticate(self) -> bool:
        try:
            response = await self.client.post(
                f"{self.config.base_url}/oauth2/access_token",
                data={
                    "client_id": self.config.settings.get("client_id"),
                    "client_secret": self.config.api_secret,
                    "grant_type": "client_credentials"
                }
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                return True
            return False
        except Exception as e:
            logger.error(f"Open edX authentication failed: {e}")
            return False
    
    async def get_courses(self) -> List[Course]:
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self.client.get(
                f"{self.config.base_url}/api/courses/v1/courses/",
                headers=headers
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch courses")
            
            courses_data = response.json()
            courses = []
            
            for course_data in courses_data.get("results", []):
                course = Course(
                    id=str(uuid.uuid4()),
                    title=course_data.get("name", ""),
                    description=course_data.get("short_description", ""),
                    lms_course_id=course_data.get("course_id"),
                    lms_type="openedx"
                )
                courses.append(course)
            
            return courses
        except Exception as e:
            logger.error(f"Failed to get Open edX courses: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_course(self, course_id: str) -> Course:
        courses = await self.get_courses()
        for course in courses:
            if course.lms_course_id == course_id:
                return course
        raise HTTPException(status_code=404, detail="Course not found")
    
    async def enroll_user(self, course_id: str, user_email: str) -> Enrollment:
        # Implementation for Open edX enrollment
        enrollment = Enrollment(
            id=str(uuid.uuid4()),
            course_id=course_id,
            user_id=user_email,
            user_email=user_email,
            enrolled_at=datetime.utcnow(),
            status="ENROLLED"
        )
        return enrollment
    
    async def get_user_enrollments(self, user_email: str) -> List[Enrollment]:
        return []
    
    async def get_user_progress(self, course_id: str, user_email: str) -> Dict[str, Any]:
        return {"progress_percent": 0.0, "status": "ENROLLED"}
    
    async def launch_course(self, course_id: str, user_email: str) -> str:
        return f"{self.config.base_url}/courses/{course_id}/courseware/"

# Canvas Adapter
class CanvasAdapter(LMSAdapter):
    async def authenticate(self) -> bool:
        try:
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            response = await self.client.get(
                f"{self.config.base_url}/api/v1/accounts/self",
                headers=headers
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Canvas authentication failed: {e}")
            return False
    
    async def get_courses(self) -> List[Course]:
        try:
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            response = await self.client.get(
                f"{self.config.base_url}/api/v1/courses",
                headers=headers
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch courses")
            
            courses_data = response.json()
            courses = []
            
            for course_data in courses_data:
                course = Course(
                    id=str(uuid.uuid4()),
                    title=course_data.get("name", ""),
                    lms_course_id=str(course_data.get("id")),
                    lms_type="canvas",
                    enrollment_count=course_data.get("total_students", 0)
                )
                courses.append(course)
            
            return courses
        except Exception as e:
            logger.error(f"Failed to get Canvas courses: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_course(self, course_id: str) -> Course:
        courses = await self.get_courses()
        for course in courses:
            if course.lms_course_id == course_id:
                return course
        raise HTTPException(status_code=404, detail="Course not found")
    
    async def enroll_user(self, course_id: str, user_email: str) -> Enrollment:
        # Implementation for Canvas enrollment
        enrollment = Enrollment(
            id=str(uuid.uuid4()),
            course_id=course_id,
            user_id=user_email,
            user_email=user_email,
            enrolled_at=datetime.utcnow(),
            status="ENROLLED"
        )
        return enrollment
    
    async def get_user_enrollments(self, user_email: str) -> List[Enrollment]:
        return []
    
    async def get_user_progress(self, course_id: str, user_email: str) -> Dict[str, Any]:
        return {"progress_percent": 0.0, "status": "ENROLLED"}
    
    async def launch_course(self, course_id: str, user_email: str) -> str:
        return f"{self.config.base_url}/courses/{course_id}"

# LMS Factory
class LMSFactory:
    @staticmethod
    def create_adapter(config: LMSConfig) -> LMSAdapter:
        if config.lms_type == "moodle":
            return MoodleAdapter(config)
        elif config.lms_type == "openedx":
            return OpenEdXAdapter(config)
        elif config.lms_type == "canvas":
            return CanvasAdapter(config)
        else:
            raise ValueError(f"Unsupported LMS type: {config.lms_type}")

# LMS Manager
class LMSManager:
    def __init__(self):
        self.configs: Dict[str, LMSConfig] = {}
        self.adapters: Dict[str, LMSAdapter] = {}
    
    async def add_lms_config(self, config: LMSConfig) -> str:
        config_id = config.id or str(uuid.uuid4())
        config.id = config_id
        
        # Create adapter and test connection
        adapter = LMSFactory.create_adapter(config)
        if not await adapter.authenticate():
            raise HTTPException(status_code=400, detail="LMS authentication failed")
        
        self.configs[config_id] = config
        self.adapters[config_id] = adapter
        
        logger.info(f"Added LMS config {config_id}: {config.name} ({config.lms_type})")
        return config_id
    
    async def get_adapter(self, config_id: str) -> LMSAdapter:
        if config_id not in self.adapters:
            raise HTTPException(status_code=404, detail="LMS configuration not found")
        return self.adapters[config_id]
    
    async def publish_event(self, event_type: str, tenant_id: str, data: Dict[str, Any]):
        """Publish event to EventBus"""
        try:
            async with httpx.AsyncClient() as client:
                await client.post(f"{EVENTBUS_URL}/api/events/publish", json={
                    "event_type": event_type,
                    "tenant_id": tenant_id,
                    "data": data
                })
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")

# Global LMS manager
lms_manager = LMSManager()

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting LMS Adapter Service...")
    yield
    logger.info("Shutting down LMS Adapter Service...")

# Create FastAPI app
app = FastAPI(
    title="BCM LMS Adapter Service",
    description="Multi-LMS integration for ISO 22301 BCM Platform",
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
    return {"status": "healthy", "service": "lms_adapter"}

# LMS Configuration Management
@app.post("/api/lms/configs")
async def add_lms_config(config: LMSConfig):
    config_id = await lms_manager.add_lms_config(config)
    return {"config_id": config_id, "status": "configured"}

@app.get("/api/lms/configs")
async def get_lms_configs(tenant_id: str):
    configs = [
        config for config in lms_manager.configs.values()
        if config.tenant_id == tenant_id
    ]
    return {"configs": configs}

# Course Management
@app.get("/api/lms/{config_id}/courses")
async def get_courses(config_id: str):
    adapter = await lms_manager.get_adapter(config_id)
    courses = await adapter.get_courses()
    return {"courses": courses}

@app.get("/api/lms/{config_id}/courses/{course_id}")
async def get_course(config_id: str, course_id: str):
    adapter = await lms_manager.get_adapter(config_id)
    course = await adapter.get_course(course_id)
    return {"course": course}

# Enrollment Management
@app.post("/api/lms/{config_id}/courses/{course_id}/enroll")
async def enroll_user(
    config_id: str,
    course_id: str,
    user_email: str,
    tenant_id: str
):
    adapter = await lms_manager.get_adapter(config_id)
    enrollment = await adapter.enroll_user(course_id, user_email)
    
    # Publish event
    await lms_manager.publish_event("lms.user.enrolled", tenant_id, {
        "config_id": config_id,
        "course_id": course_id,
        "user_email": user_email,
        "enrollment_id": enrollment.id
    })
    
    return {"enrollment": enrollment}

@app.get("/api/lms/{config_id}/users/{user_email}/enrollments")
async def get_user_enrollments(config_id: str, user_email: str):
    adapter = await lms_manager.get_adapter(config_id)
    enrollments = await adapter.get_user_enrollments(user_email)
    return {"enrollments": enrollments}

@app.get("/api/lms/{config_id}/courses/{course_id}/progress/{user_email}")
async def get_user_progress(config_id: str, course_id: str, user_email: str):
    adapter = await lms_manager.get_adapter(config_id)
    progress = await adapter.get_user_progress(course_id, user_email)
    return {"progress": progress}

# Course Launch (SSO)
@app.get("/api/lms/{config_id}/courses/{course_id}/launch")
async def launch_course(config_id: str, course_id: str, user_email: str, tenant_id: str):
    adapter = await lms_manager.get_adapter(config_id)
    launch_url = await adapter.launch_course(course_id, user_email)
    
    # Publish event
    await lms_manager.publish_event("lms.course.launched", tenant_id, {
        "config_id": config_id,
        "course_id": course_id,
        "user_email": user_email,
        "launch_url": launch_url
    })
    
    return {"launch_url": launch_url}

# Training Progress Sync
@app.post("/api/lms/{config_id}/sync/progress")
async def sync_training_progress(config_id: str, tenant_id: str):
    """Sync all training progress for tenant"""
    adapter = await lms_manager.get_adapter(config_id)
    
    # This would typically sync progress for all enrolled users
    # Implementation depends on LMS capabilities
    
    await lms_manager.publish_event("lms.progress.synced", tenant_id, {
        "config_id": config_id,
        "sync_timestamp": datetime.utcnow().isoformat()
    })
    
    return {"status": "synced"}

# Mock Data Endpoints for Testing
from mock_data import get_mock_lms_configs, get_mock_courses, get_mock_enrollments, get_mock_training_paths, get_mock_competency_matrix, get_mock_learning_analytics

@app.get("/api/lms/mock/configs")
async def get_mock_lms_config_data():
    """Get mock LMS configuration data for testing"""
    return {"mock_configs": get_mock_lms_configs()}

@app.get("/api/lms/mock/courses")
async def get_mock_course_data():
    """Get mock course data for testing"""
    return {"mock_courses": get_mock_courses()}

@app.get("/api/lms/mock/enrollments")
async def get_mock_enrollment_data():
    """Get mock enrollment data for testing"""
    return {"mock_enrollments": get_mock_enrollments()}

@app.get("/api/lms/mock/training-paths")
async def get_mock_training_path_data():
    """Get mock training path data for testing"""
    return {"training_paths": get_mock_training_paths()}

@app.get("/api/lms/mock/competency-matrix")
async def get_mock_competency_data():
    """Get mock competency matrix for BCM roles"""
    return {"competency_matrix": get_mock_competency_matrix()}

@app.get("/api/lms/mock/analytics")
async def get_mock_analytics_data():
    """Get mock learning analytics data"""
    return {"learning_analytics": get_mock_learning_analytics()}

@app.post("/api/lms/mock/setup-demo-config")
async def setup_demo_lms_config(tenant_id: str, lms_type: str = "moodle"):
    """Setup demo LMS configuration for testing"""
    mock_configs = get_mock_lms_configs()
    demo_config = next((config for config in mock_configs if config["lms_type"] == lms_type), mock_configs[0])
    demo_config["tenant_id"] = tenant_id
    
    from main import LMSConfig
    config = LMSConfig(**demo_config)
    config_id = await lms_manager.add_lms_config(config)
    
    return {
        "status": "configured",
        "config_id": config_id,
        "lms_type": demo_config["lms_type"],
        "description": f"Demo {lms_type} LMS configuration setup"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)