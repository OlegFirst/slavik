# -*- coding: utf-8 -*-
"""
Moodle-BCM Webhook Handler
Handles webhooks from Moodle LMS to sync training data with BCM Platform
"""
import os
import json
import hmac
import hashlib
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional
import structlog
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

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

class MoodleWebhookHandler:
    """Handle Moodle webhooks and sync with BCM Platform"""
    
    def __init__(self, bcm_api_url: str, bcm_api_key: str):
        self.bcm_api_url = bcm_api_url.rstrip('/')
        self.bcm_api_key = bcm_api_key
        
    def verify_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        if not signature.startswith('sha256='):
            return False
            
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, f'sha256={expected_signature}')
    
    async def handle_course_completion(self, webhook_data: Dict[str, Any]) -> bool:
        """Handle course completion event"""
        try:
            user_id = webhook_data.get('userid')
            course_id = webhook_data.get('courseid')
            completion_data = webhook_data.get('completion', {})
            
            logger.info("Processing course completion", 
                       user_id=user_id, course_id=course_id)
            
            # Prepare BCM API payload
            bcm_payload = {
                'event_type': 'training_completed',
                'training_data': {
                    'moodle_user_id': user_id,
                    'moodle_course_id': course_id,
                    'completion_date': completion_data.get('timecompleted'),
                    'grade': completion_data.get('grade'),
                    'status': 'completed',
                    'certificate_issued': completion_data.get('certificate', False)
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # Send to BCM Platform
            return await self._send_to_bcm(bcm_payload, 'training/completion')
            
        except Exception as e:
            logger.error("Failed to handle course completion", error=str(e))
            return False
    
    async def handle_user_enrolled(self, webhook_data: Dict[str, Any]) -> bool:
        """Handle user enrollment event"""
        try:
            user_id = webhook_data.get('userid')
            course_id = webhook_data.get('courseid')
            role_id = webhook_data.get('roleid')
            
            logger.info("Processing user enrollment", 
                       user_id=user_id, course_id=course_id, role_id=role_id)
            
            # Map Moodle role to BCM role
            bcm_role = self._map_moodle_role(role_id)
            
            bcm_payload = {
                'event_type': 'training_enrolled',
                'enrollment_data': {
                    'moodle_user_id': user_id,
                    'moodle_course_id': course_id,
                    'bcm_role': bcm_role,
                    'enrollment_date': webhook_data.get('timeenrolled'),
                    'status': 'enrolled'
                },
                'timestamp': datetime.now().isoformat()
            }
            
            return await self._send_to_bcm(bcm_payload, 'training/enrollment')
            
        except Exception as e:
            logger.error("Failed to handle user enrollment", error=str(e))
            return False
    
    async def handle_competency_achieved(self, webhook_data: Dict[str, Any]) -> bool:
        """Handle competency achievement event"""
        try:
            user_id = webhook_data.get('userid')
            competency_id = webhook_data.get('competencyid')
            proficient = webhook_data.get('proficient', False)
            
            logger.info("Processing competency achievement", 
                       user_id=user_id, competency_id=competency_id, proficient=proficient)
            
            bcm_payload = {
                'event_type': 'competency_achieved',
                'competency_data': {
                    'moodle_user_id': user_id,
                    'moodle_competency_id': competency_id,
                    'proficient': proficient,
                    'achievement_date': webhook_data.get('timecreated'),
                    'grade': webhook_data.get('grade'),
                    'reviewer_id': webhook_data.get('reviewerid')
                },
                'timestamp': datetime.now().isoformat()
            }
            
            return await self._send_to_bcm(bcm_payload, 'competency/achievement')
            
        except Exception as e:
            logger.error("Failed to handle competency achievement", error=str(e))
            return False
    
    async def handle_grade_updated(self, webhook_data: Dict[str, Any]) -> bool:
        """Handle grade update event"""
        try:
            user_id = webhook_data.get('userid')
            course_id = webhook_data.get('courseid')
            item_id = webhook_data.get('itemid')
            grade = webhook_data.get('finalgrade')
            
            logger.info("Processing grade update", 
                       user_id=user_id, course_id=course_id, grade=grade)
            
            bcm_payload = {
                'event_type': 'training_graded',
                'grade_data': {
                    'moodle_user_id': user_id,
                    'moodle_course_id': course_id,
                    'moodle_item_id': item_id,
                    'final_grade': grade,
                    'graded_date': webhook_data.get('timemodified'),
                    'grader_id': webhook_data.get('usermodified')
                },
                'timestamp': datetime.now().isoformat()
            }
            
            return await self._send_to_bcm(bcm_payload, 'training/grade')
            
        except Exception as e:
            logger.error("Failed to handle grade update", error=str(e))
            return False
    
    async def handle_certificate_issued(self, webhook_data: Dict[str, Any]) -> bool:
        """Handle certificate issued event"""
        try:
            user_id = webhook_data.get('userid')
            course_id = webhook_data.get('courseid')
            certificate_code = webhook_data.get('code')
            
            logger.info("Processing certificate issuance", 
                       user_id=user_id, certificate_code=certificate_code)
            
            bcm_payload = {
                'event_type': 'certificate_issued',
                'certificate_data': {
                    'moodle_user_id': user_id,
                    'moodle_course_id': course_id,
                    'certificate_code': certificate_code,
                    'issue_date': webhook_data.get('timecreated'),
                    'expires_date': webhook_data.get('expires'),
                    'download_url': webhook_data.get('download_url')
                },
                'timestamp': datetime.now().isoformat()
            }
            
            return await self._send_to_bcm(bcm_payload, 'training/certificate')
            
        except Exception as e:
            logger.error("Failed to handle certificate issuance", error=str(e))
            return False
    
    def _map_moodle_role(self, role_id: int) -> str:
        """Map Moodle role ID to BCM role"""
        role_mapping = {
            5: 'bcm_student',
            4: 'bcm_student',  # Non-editing teacher
            3: 'bcm_trainer',  # Editing teacher
            2: 'bcm_manager',  # Course creator
            1: 'bcm_auditor'   # Manager
        }
        return role_mapping.get(role_id, 'bcm_student')
    
    async def _send_to_bcm(self, payload: Dict[str, Any], endpoint: str) -> bool:
        """Send webhook data to BCM Platform"""
        try:
            url = f"{self.bcm_api_url}/api/integrations/moodle/{endpoint}"
            headers = {
                'Authorization': f'Bearer {self.bcm_api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'Moodle-BCM-Webhook/1.0'
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            
            logger.info("Successfully sent webhook to BCM Platform", 
                       endpoint=endpoint, status_code=response.status_code)
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error("Failed to send webhook to BCM Platform", 
                        endpoint=endpoint, error=str(e))
            return False


# FastAPI app for webhook receiver
app = FastAPI(
    title="Moodle-BCM Webhook Receiver",
    description="Receives webhooks from Moodle LMS and syncs with BCM Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global webhook handler
webhook_handler: Optional[MoodleWebhookHandler] = None

@app.on_event("startup")
async def startup_event():
    """Initialize webhook handler on startup"""
    global webhook_handler
    
    bcm_api_url = os.getenv('BCM_API_URL', 'http://localhost:8069')
    bcm_api_key = os.getenv('BCM_API_KEY')
    
    if not bcm_api_key:
        logger.error("BCM_API_KEY environment variable is required")
        raise RuntimeError("Missing BCM API key")
    
    webhook_handler = MoodleWebhookHandler(bcm_api_url, bcm_api_key)
    logger.info("Moodle webhook receiver initialized")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "service": "moodle-webhook-receiver"
    }

@app.post("/webhook/moodle")
async def handle_moodle_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Main webhook endpoint for Moodle events"""
    if not webhook_handler:
        raise HTTPException(status_code=503, detail="Webhook handler not initialized")
    
    try:
        # Get raw payload
        payload = await request.body()
        
        # Verify signature if secret is provided
        webhook_secret = os.getenv('MOODLE_WEBHOOK_SECRET')
        if webhook_secret:
            signature = request.headers.get('X-Moodle-Signature', '')
            if not webhook_handler.verify_signature(payload, signature, webhook_secret):
                raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Parse JSON payload
        webhook_data = json.loads(payload.decode('utf-8'))
        event_name = webhook_data.get('eventname', '')
        
        logger.info("Received Moodle webhook", event=event_name, 
                   data_keys=list(webhook_data.keys()))
        
        # Process webhook in background based on event type
        if event_name == 'core\\event\\course_completed':
            background_tasks.add_task(
                webhook_handler.handle_course_completion, webhook_data
            )
        elif event_name == 'core\\event\\user_enrolment_created':
            background_tasks.add_task(
                webhook_handler.handle_user_enrolled, webhook_data
            )
        elif event_name == 'core\\event\\competency_user_competency_rated':
            background_tasks.add_task(
                webhook_handler.handle_competency_achieved, webhook_data
            )
        elif event_name == 'core\\event\\user_graded':
            background_tasks.add_task(
                webhook_handler.handle_grade_updated, webhook_data
            )
        elif event_name == 'mod_customcert\\event\\certificate_issued':
            background_tasks.add_task(
                webhook_handler.handle_certificate_issued, webhook_data
            )
        else:
            logger.warning("Unknown Moodle event", event=event_name)
        
        return {
            "status": "accepted",
            "event": event_name,
            "timestamp": datetime.now().isoformat()
        }
        
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON payload", error=str(e))
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error("Failed to process webhook", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/moodle/test")
async def test_webhook():
    """Test webhook endpoint"""
    if not webhook_handler:
        raise HTTPException(status_code=503, detail="Webhook handler not initialized")
    
    # Send test data to BCM Platform
    test_payload = {
        'event_type': 'webhook_test',
        'test_data': {
            'message': 'Moodle webhook receiver test',
            'timestamp': datetime.now().isoformat()
        }
    }
    
    success = await webhook_handler._send_to_bcm(test_payload, 'test')
    
    return {
        "status": "success" if success else "failed",
        "message": "Test webhook sent to BCM Platform"
    }

if __name__ == "__main__":
    # Load configuration
    port = int(os.getenv('PORT', '8093'))
    host = os.getenv('HOST', '0.0.0.0')
    log_level = os.getenv('LOG_LEVEL', 'info').lower()
    
    # Run server
    uvicorn.run(
        "webhooks:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=False,
        access_log=True
    )
