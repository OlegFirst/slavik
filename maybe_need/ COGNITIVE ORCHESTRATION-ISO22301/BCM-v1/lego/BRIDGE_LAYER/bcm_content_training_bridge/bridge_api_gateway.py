"""
BCM Content Training Bridge API Gateway
FastAPI service providing REST API for bridge module integration
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import httpx
import json
import os
import redis
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="BCM Content Training Bridge Gateway",
    description="API Gateway for BCM Content & Training Bridge Module Integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs from environment
ODOO_URL = os.getenv("ODOO_URL", "http://odoo:8069")
ODOO_DB = os.getenv("ODOO_DB", "bcm_db")
SCENARIO_ORCHESTRATOR_URL = os.getenv("SCENARIO_ORCHESTRATOR_URL", "http://scenario_orchestrator:8085")
EXERCISE_SIMULATOR_URL = os.getenv("EXERCISE_SIMULATOR_URL", "http://exercise_simulators:8094")
DIGITAL_TWIN_URL = os.getenv("DIGITAL_TWIN_URL", "http://digital-twin-platform:3000")

# Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

# =====================================================
# GAMIFICATION BRIDGE ENDPOINTS
# =====================================================

class GamificationAction(BaseModel):
    user_id: int
    action_type: str  # create, review, use, rate
    content_type: str  # bcm.template, bcm.scenario
    content_id: int
    metadata: Optional[Dict] = {}

@app.post("/api/bridge/gamification/award-points")
async def award_gamification_points(action: GamificationAction):
    """Award points for BCM content actions through gamification bridge"""
    try:
        logger.info(f"Awarding points: {action.action_type} for user {action.user_id}")

        # Point values based on action type
        point_values = {
            'create': 50,
            'review': 20,
            'use': 10,
            'rate': 5,
            'improve': 30,
            'share': 15
        }

        points = point_values.get(action.action_type, 10)

        # Store in Redis for tracking
        redis_key = f"gamification:user:{action.user_id}:points"
        redis_client.incrby(redis_key, points)

        # Track achievement progress
        achievement_key = f"gamification:user:{action.user_id}:actions:{action.action_type}"
        action_count = redis_client.incr(achievement_key)

        # Check for achievements
        achievements_earned = []
        if action_count == 10 and action.action_type == 'create':
            achievements_earned.append("Content Creator")
        elif action_count == 25 and action.action_type == 'review':
            achievements_earned.append("Expert Reviewer")

        # Update Odoo if connected
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{ODOO_URL}/api/v1/gamification/award",
                    json={
                        "user_id": action.user_id,
                        "points": points,
                        "action": action.action_type,
                        "achievements": achievements_earned
                    }
                )
        except Exception as e:
            logger.warning(f"Could not update Odoo gamification: {e}")

        return {
            "status": "success",
            "points_awarded": points,
            "total_points": int(redis_client.get(redis_key) or 0),
            "achievements_earned": achievements_earned,
            "action_count": action_count
        }

    except Exception as e:
        logger.error(f"Gamification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bridge/gamification/leaderboard")
async def get_gamification_leaderboard(limit: int = 10):
    """Get gamification leaderboard"""
    try:
        # Get all user points from Redis
        pattern = "gamification:user:*:points"
        keys = redis_client.keys(pattern)

        leaderboard = []
        for key in keys:
            user_id = key.split(':')[2]
            points = int(redis_client.get(key) or 0)
            leaderboard.append({
                "user_id": user_id,
                "points": points
            })

        # Sort by points
        leaderboard.sort(key=lambda x: x['points'], reverse=True)

        return {
            "status": "success",
            "leaderboard": leaderboard[:limit],
            "total_participants": len(leaderboard)
        }

    except Exception as e:
        logger.error(f"Leaderboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================================================
# E-LEARNING BRIDGE ENDPOINTS
# =====================================================

class LearningConversion(BaseModel):
    template_id: int
    template_type: str  # policy, procedure, assessment
    target_format: str  # slide, quiz, course
    metadata: Optional[Dict] = {}

@app.post("/api/bridge/learning/convert-template")
async def convert_template_to_learning(conversion: LearningConversion):
    """Convert BCM template to e-learning content"""
    try:
        logger.info(f"Converting template {conversion.template_id} to {conversion.target_format}")

        # Generate learning content based on template type
        learning_content = {
            "template_id": conversion.template_id,
            "format": conversion.target_format,
            "created_at": datetime.now().isoformat()
        }

        if conversion.target_format == "slide":
            learning_content["slides"] = _generate_slides(conversion.template_type)
        elif conversion.target_format == "quiz":
            learning_content["questions"] = _generate_quiz_questions(conversion.template_type)
        elif conversion.target_format == "course":
            learning_content["modules"] = _generate_course_modules(conversion.template_type)

        # Store conversion in Redis
        redis_key = f"learning:template:{conversion.template_id}:{conversion.target_format}"
        redis_client.set(redis_key, json.dumps(learning_content))

        return {
            "status": "success",
            "learning_content": learning_content,
            "access_url": f"/api/bridge/learning/content/{conversion.template_id}/{conversion.target_format}"
        }

    except Exception as e:
        logger.error(f"Learning conversion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bridge/learning/paths")
async def get_learning_paths():
    """Get available BCM learning paths"""
    return {
        "status": "success",
        "learning_paths": [
            {
                "id": "beginner",
                "name": "BCM Beginner",
                "modules": ["bcm_basics", "risk_assessment", "incident_response"],
                "duration_hours": 10,
                "certification": "BCM Foundation"
            },
            {
                "id": "practitioner",
                "name": "BCM Practitioner",
                "modules": ["advanced_planning", "exercise_design", "recovery_strategies"],
                "duration_hours": 20,
                "certification": "BCM Practitioner"
            },
            {
                "id": "expert",
                "name": "BCM Expert",
                "modules": ["crisis_leadership", "program_management", "audit_compliance"],
                "duration_hours": 30,
                "certification": "BCM Expert"
            }
        ]
    }

# =====================================================
# CALENDAR BRIDGE ENDPOINTS
# =====================================================

class CalendarEvent(BaseModel):
    event_type: str  # review, exercise, training
    content_id: int
    scheduled_date: str
    duration_hours: float
    participants: List[int]
    recurrence: Optional[str] = None  # daily, weekly, monthly

@app.post("/api/bridge/calendar/schedule")
async def schedule_calendar_event(event: CalendarEvent, background_tasks: BackgroundTasks):
    """Schedule BCM event through calendar bridge"""
    try:
        logger.info(f"Scheduling {event.event_type} for {event.scheduled_date}")

        # Create calendar event
        calendar_event = {
            "id": f"bcm_{event.event_type}_{datetime.now().timestamp()}",
            "type": event.event_type,
            "content_id": event.content_id,
            "scheduled_date": event.scheduled_date,
            "duration_hours": event.duration_hours,
            "participants": event.participants,
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }

        # Store in Redis
        redis_key = f"calendar:event:{calendar_event['id']}"
        redis_client.set(redis_key, json.dumps(calendar_event))

        # Add to background task for reminder
        background_tasks.add_task(schedule_reminder, calendar_event)

        # Sync with Odoo calendar if available
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{ODOO_URL}/api/v1/calendar/event",
                    json=calendar_event
                )
        except Exception as e:
            logger.warning(f"Could not sync with Odoo calendar: {e}")

        return {
            "status": "success",
            "event_id": calendar_event['id'],
            "calendar_event": calendar_event
        }

    except Exception as e:
        logger.error(f"Calendar scheduling error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================================================
# SCENARIO CREATION BRIDGE
# =====================================================

@app.post("/api/bridge/scenario/ai-create")
async def create_ai_scenario(category: str, complexity: int = 3):
    """Create AI scenario through bridge to scenario orchestrator"""
    try:
        logger.info(f"Creating AI scenario: {category} with complexity {complexity}")

        # Forward to scenario orchestrator
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SCENARIO_ORCHESTRATOR_URL}/scenarios/generate",
                json={
                    "category": category,
                    "complexity": complexity,
                    "duration_hours": 4,
                    "participants": 10,
                    "creativity_boost": True
                },
                timeout=60.0
            )

            if response.status_code == 200:
                scenario_data = response.json()

                # Track in Redis
                redis_key = f"scenarios:created:{scenario_data.get('scenario_id')}"
                redis_client.set(redis_key, json.dumps(scenario_data))

                return {
                    "status": "success",
                    "scenario": scenario_data,
                    "bridge_tracking_id": redis_key
                }
            else:
                raise HTTPException(status_code=response.status_code, detail="Scenario creation failed")

    except Exception as e:
        logger.error(f"Scenario creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================================================
# LEARNING ANALYTICS
# =====================================================

@app.get("/api/bridge/analytics/dashboard")
async def get_analytics_dashboard():
    """Get comprehensive analytics dashboard"""
    try:
        # Aggregate data from Redis
        gamification_keys = redis_client.keys("gamification:user:*:points")
        total_points = sum(int(redis_client.get(k) or 0) for k in gamification_keys)

        learning_keys = redis_client.keys("learning:template:*")
        calendar_keys = redis_client.keys("calendar:event:*")
        scenario_keys = redis_client.keys("scenarios:created:*")

        return {
            "status": "success",
            "analytics": {
                "gamification": {
                    "total_users": len(gamification_keys),
                    "total_points_awarded": total_points,
                    "avg_points_per_user": total_points / max(len(gamification_keys), 1)
                },
                "learning": {
                    "templates_converted": len(learning_keys),
                    "learning_paths_active": 3
                },
                "calendar": {
                    "events_scheduled": len(calendar_keys),
                    "upcoming_events": min(len(calendar_keys), 5)
                },
                "scenarios": {
                    "ai_generated": len(scenario_keys),
                    "categories_covered": ["cyber", "epidemic", "blackout", "supply", "natural"]
                },
                "timestamp": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def _generate_slides(template_type: str) -> List[Dict]:
    """Generate slide structure based on template type"""
    base_slides = [
        {"title": "Introduction", "content": f"Introduction to {template_type}"},
        {"title": "Key Concepts", "content": f"Core concepts of {template_type}"},
        {"title": "Best Practices", "content": f"Best practices for {template_type}"},
        {"title": "Case Studies", "content": f"Real-world examples of {template_type}"},
        {"title": "Summary", "content": f"Key takeaways from {template_type}"}
    ]
    return base_slides

def _generate_quiz_questions(template_type: str) -> List[Dict]:
    """Generate quiz questions based on template type"""
    return [
        {
            "question": f"What is the primary purpose of {template_type}?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct": 0
        },
        {
            "question": f"Which of the following is a key component of {template_type}?",
            "options": ["Component A", "Component B", "Component C", "Component D"],
            "correct": 1
        },
        {
            "question": f"When should {template_type} be reviewed?",
            "options": ["Monthly", "Quarterly", "Annually", "As needed"],
            "correct": 2
        }
    ]

def _generate_course_modules(template_type: str) -> List[Dict]:
    """Generate course module structure"""
    return [
        {"module": 1, "name": f"{template_type} Fundamentals", "duration_hours": 2},
        {"module": 2, "name": f"{template_type} Implementation", "duration_hours": 3},
        {"module": 3, "name": f"{template_type} Assessment", "duration_hours": 1}
    ]

async def schedule_reminder(event: Dict):
    """Background task to schedule event reminders"""
    try:
        logger.info(f"Scheduling reminder for event {event['id']}")
        # Implementation for reminder scheduling
        await asyncio.sleep(1)  # Placeholder
    except Exception as e:
        logger.error(f"Reminder scheduling error: {e}")

# =====================================================
# HEALTH & STATUS ENDPOINTS
# =====================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "bcm_content_training_bridge",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "BCM Content Training Bridge API Gateway",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "gamification": "/api/bridge/gamification",
            "learning": "/api/bridge/learning",
            "calendar": "/api/bridge/calendar",
            "analytics": "/api/bridge/analytics"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8096)