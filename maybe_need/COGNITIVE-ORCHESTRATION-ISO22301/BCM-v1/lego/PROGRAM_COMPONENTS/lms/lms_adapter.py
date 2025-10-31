"""
LMS Adapter for Moodle/Open edX Integration
Handles training management, course enrollment, and progress tracking
"""

import asyncio
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LMSProvider(str, Enum):
    MOODLE = "moodle"
    OPENEDX = "openedx"
    CANVAS = "canvas"


class CourseStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class EnrollmentStatus(str, Enum):
    ENROLLED = "enrolled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DROPPED = "dropped"


class Course(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    category: str = "BCM"
    duration_hours: int = 8
    status: CourseStatus = CourseStatus.DRAFT
    instructor: Optional[str] = None
    capacity: int = 50
    enrolled: int = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    bcm_modules: List[str] = Field(default_factory=list)
    iso_compliance: List[str] = Field(default_factory=lambda: ["ISO 22301:2019"])


class Enrollment(BaseModel):
    course_id: str
    user_id: str
    tenant_id: str
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)
    status: EnrollmentStatus = EnrollmentStatus.ENROLLED
    progress: float = 0.0
    completed_modules: List[str] = Field(default_factory=list)
    completion_date: Optional[datetime] = None
    certificate_url: Optional[str] = None


class TrainingPlan(BaseModel):
    id: str
    tenant_id: str
    name: str
    description: Optional[str] = None
    courses: List[str] = Field(default_factory=list)
    target_roles: List[str] = Field(default_factory=list)
    mandatory: bool = False
    deadline: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LMSAdapter:
    """Adapter for integrating with Learning Management Systems"""
    
    def __init__(self, config: Dict[str, Any]):
        self.provider = LMSProvider(config.get("provider", "moodle"))
        self.base_url = config.get("base_url", "http://localhost:8006")
        self.api_key = config.get("api_key", "")
        self.eventbus_url = config.get("eventbus_url", "http://localhost:8001")
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc, tb):
        await self.client.aclose()
    
    async def publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish training events to EventBus"""
        try:
            event = {
                "event_type": event_type,
                "tenant_id": data.get("tenant_id", "demo"),
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "lms_adapter"
            }
            
            response = await self.client.post(
                f"{self.eventbus_url}/api/events/publish",
                json=event
            )
            response.raise_for_status()
            logger.info(f"Published event: {event_type}")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
    
    # Course Management
    async def create_course(self, course: Course) -> Course:
        """Create a new training course"""
        try:
            # Provider-specific API call
            if self.provider == LMSProvider.MOODLE:
                response = await self._moodle_create_course(course)
            elif self.provider == LMSProvider.OPENEDX:
                response = await self._openedx_create_course(course)
            else:
                response = course.dict()
            
            # Publish event
            await self.publish_event("bcm.training.course_created", {
                "course_id": course.id,
                "title": course.title,
                "category": course.category,
                "tenant_id": "demo"
            })
            
            return Course(**response)
        except Exception as e:
            logger.error(f"Failed to create course: {e}")
            raise
    
    async def get_courses(self, tenant_id: str, category: Optional[str] = None) -> List[Course]:
        """Get available courses"""
        try:
            # Mock data for demonstration
            courses = [
                Course(
                    id="BCM-101",
                    title="BCM Fundamentals",
                    description="Introduction to Business Continuity Management",
                    category="BCM",
                    duration_hours=16,
                    status=CourseStatus.PUBLISHED,
                    instructor="Dr. Smith",
                    enrolled=25,
                    bcm_modules=["risk_assessment", "bia", "strategy"],
                    iso_compliance=["ISO 22301:2019", "ISO 31000:2018"]
                ),
                Course(
                    id="BCM-201",
                    title="Crisis Management",
                    description="Advanced crisis response and communication",
                    category="BCM",
                    duration_hours=24,
                    status=CourseStatus.PUBLISHED,
                    instructor="Prof. Johnson",
                    enrolled=15,
                    bcm_modules=["crisis_response", "communication", "recovery"],
                    iso_compliance=["ISO 22301:2019"]
                ),
                Course(
                    id="BCM-301",
                    title="BCM Auditor Training",
                    description="Internal audit procedures for BCM",
                    category="BCM",
                    duration_hours=40,
                    status=CourseStatus.PUBLISHED,
                    instructor="Ms. Davis",
                    enrolled=8,
                    bcm_modules=["audit", "compliance", "improvement"],
                    iso_compliance=["ISO 22301:2019", "ISO 19011:2018"]
                )
            ]
            
            if category:
                courses = [c for c in courses if c.category == category]
            
            return courses
        except Exception as e:
            logger.error(f"Failed to get courses: {e}")
            return []
    
    # Enrollment Management
    async def enroll_user(self, course_id: str, user_id: str, tenant_id: str) -> Enrollment:
        """Enroll user in a course"""
        try:
            enrollment = Enrollment(
                course_id=course_id,
                user_id=user_id,
                tenant_id=tenant_id
            )
            
            # Provider-specific enrollment
            if self.provider == LMSProvider.MOODLE:
                await self._moodle_enroll_user(enrollment)
            elif self.provider == LMSProvider.OPENEDX:
                await self._openedx_enroll_user(enrollment)
            
            # Publish event
            await self.publish_event("bcm.training.user_enrolled", {
                "course_id": course_id,
                "user_id": user_id,
                "tenant_id": tenant_id
            })
            
            return enrollment
        except Exception as e:
            logger.error(f"Failed to enroll user: {e}")
            raise
    
    async def get_user_enrollments(self, user_id: str, tenant_id: str) -> List[Enrollment]:
        """Get user's course enrollments"""
        try:
            # Mock data
            enrollments = [
                Enrollment(
                    course_id="BCM-101",
                    user_id=user_id,
                    tenant_id=tenant_id,
                    status=EnrollmentStatus.IN_PROGRESS,
                    progress=65.0,
                    completed_modules=["risk_assessment", "bia"]
                ),
                Enrollment(
                    course_id="BCM-201",
                    user_id=user_id,
                    tenant_id=tenant_id,
                    status=EnrollmentStatus.ENROLLED,
                    progress=0.0
                )
            ]
            return enrollments
        except Exception as e:
            logger.error(f"Failed to get enrollments: {e}")
            return []
    
    async def update_progress(self, enrollment_id: str, progress: float, 
                            completed_modules: List[str]) -> Enrollment:
        """Update course progress"""
        try:
            # Update enrollment
            enrollment = Enrollment(
                course_id="BCM-101",
                user_id="user123",
                tenant_id="demo",
                status=EnrollmentStatus.IN_PROGRESS if progress < 100 else EnrollmentStatus.COMPLETED,
                progress=progress,
                completed_modules=completed_modules
            )
            
            if progress >= 100:
                enrollment.completion_date = datetime.utcnow()
                enrollment.certificate_url = f"/certificates/{enrollment_id}.pdf"
                
                # Publish completion event
                await self.publish_event("bcm.training.course_completed", {
                    "course_id": enrollment.course_id,
                    "user_id": enrollment.user_id,
                    "tenant_id": enrollment.tenant_id,
                    "certificate_url": enrollment.certificate_url
                })
            
            return enrollment
        except Exception as e:
            logger.error(f"Failed to update progress: {e}")
            raise
    
    # Training Plans
    async def create_training_plan(self, plan: TrainingPlan) -> TrainingPlan:
        """Create a training plan for roles/departments"""
        try:
            # Publish event
            await self.publish_event("bcm.training.plan_created", {
                "plan_id": plan.id,
                "name": plan.name,
                "courses": plan.courses,
                "target_roles": plan.target_roles,
                "mandatory": plan.mandatory,
                "tenant_id": plan.tenant_id
            })
            
            return plan
        except Exception as e:
            logger.error(f"Failed to create training plan: {e}")
            raise
    
    async def get_training_plans(self, tenant_id: str) -> List[TrainingPlan]:
        """Get training plans for tenant"""
        try:
            plans = [
                TrainingPlan(
                    id="TP-001",
                    tenant_id=tenant_id,
                    name="BCM Team Training",
                    description="Mandatory training for BCM team members",
                    courses=["BCM-101", "BCM-201", "BCM-301"],
                    target_roles=["bcm_manager", "bcm_coordinator"],
                    mandatory=True,
                    deadline=datetime(2025, 12, 31)
                ),
                TrainingPlan(
                    id="TP-002",
                    tenant_id=tenant_id,
                    name="Executive Awareness",
                    description="BCM awareness for executives",
                    courses=["BCM-101"],
                    target_roles=["executive", "director"],
                    mandatory=False
                )
            ]
            return plans
        except Exception as e:
            logger.error(f"Failed to get training plans: {e}")
            return []
    
    # Provider-specific implementations
    async def _moodle_create_course(self, course: Course) -> Dict:
        """Moodle-specific course creation"""
        # Implement Moodle REST API call
        return course.dict()
    
    async def _openedx_create_course(self, course: Course) -> Dict:
        """Open edX-specific course creation"""
        # Implement Open edX API call
        return course.dict()
    
    async def _moodle_enroll_user(self, enrollment: Enrollment):
        """Moodle-specific enrollment"""
        pass
    
    async def _openedx_enroll_user(self, enrollment: Enrollment):
        """Open edX-specific enrollment"""
        pass
    
    # Analytics
    async def get_training_metrics(self, tenant_id: str) -> Dict[str, Any]:
        """Get training metrics for dashboard"""
        try:
            metrics = {
                "total_courses": 3,
                "active_enrollments": 45,
                "completion_rate": 72.5,
                "avg_progress": 58.3,
                "certifications_issued": 28,
                "upcoming_deadlines": 2,
                "overdue_trainings": 1,
                "compliance_status": {
                    "compliant": 85,
                    "non_compliant": 15
                }
            }
            return metrics
        except Exception as e:
            logger.error(f"Failed to get training metrics: {e}")
            return {}


# FastAPI service endpoint
if __name__ == "__main__":
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    
    app = FastAPI(title="LMS Adapter Service")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    config = {
        "provider": "moodle",
        "base_url": "http://localhost:8006",
        "eventbus_url": "http://localhost:8001"
    }
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "lms_adapter"}
    
    @app.get("/api/courses")
    async def get_courses(tenant_id: str = "demo", category: Optional[str] = None):
        async with LMSAdapter(config) as adapter:
            courses = await adapter.get_courses(tenant_id, category)
            return {"courses": [c.dict() for c in courses]}
    
    @app.post("/api/enroll")
    async def enroll(course_id: str, user_id: str, tenant_id: str = "demo"):
        async with LMSAdapter(config) as adapter:
            enrollment = await adapter.enroll_user(course_id, user_id, tenant_id)
            return enrollment.dict()
    
    @app.get("/api/enrollments/{user_id}")
    async def get_enrollments(user_id: str, tenant_id: str = "demo"):
        async with LMSAdapter(config) as adapter:
            enrollments = await adapter.get_user_enrollments(user_id, tenant_id)
            return {"enrollments": [e.dict() for e in enrollments]}
    
    @app.get("/api/metrics")
    async def get_metrics(tenant_id: str = "demo"):
        async with LMSAdapter(config) as adapter:
            metrics = await adapter.get_training_metrics(tenant_id)
            return metrics
    
    uvicorn.run(app, host="0.0.0.0", port=8006)
