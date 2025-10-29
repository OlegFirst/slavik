"""
Notification Service - FastAPI + Redis
ISO 22301 BCM Platform Notification Management
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import json
import os
import redis.asyncio as redis
from contextlib import asynccontextmanager
import logging
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import httpx

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
EVENTBUS_URL = os.getenv("EVENTBUS_URL", "http://localhost:8001")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8081,http://localhost:8069").split(",")

# Email settings
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "bcm@company.com")

# Telegram settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Global connections
redis_client = None

# Models
class NotificationRule(BaseModel):
    id: str
    name: str
    event_pattern: str
    tenant_id: str
    channels: List[str] = ["email"]  # email, sms, telegram, ui
    recipients: List[str] = []
    enabled: bool = True
    conditions: Dict[str, Any] = {}
    template: str = ""
    
class NotificationRequest(BaseModel):
    event_type: str
    tenant_id: str
    severity: str = "info"  # info, warning, critical
    title: str
    message: str
    recipients: Optional[List[str]] = None
    channels: Optional[List[str]] = None
    data: Dict[str, Any] = {}

class NotificationHistory(BaseModel):
    id: str
    event_type: str
    tenant_id: str
    severity: str
    title: str
    message: str
    channels: List[str]
    recipients: List[str]
    status: str = "sent"  # sent, failed, pending
    sent_at: datetime
    delivery_status: Dict[str, str] = {}

# Notification rules storage
notification_rules = {
    "incident_critical": NotificationRule(
        id="incident_critical",
        name="Critical Incident Alert",
        event_pattern="bcm.incident.reported",
        tenant_id="*",
        channels=["email", "telegram", "ui"],
        recipients=["admin@company.com"],
        conditions={"severity": "critical"},
        template="CRITICAL INCIDENT: {title}\n\nDetails: {message}\n\nImmediate action required."
    ),
    "capa_overdue": NotificationRule(
        id="capa_overdue",
        name="CAPA Overdue Alert",
        event_pattern="bcm.capa.overdue",
        tenant_id="*",
        channels=["email", "ui"],
        recipients=["manager@company.com"],
        conditions={},
        template="CAPA OVERDUE: {title}\n\nPlease review and update the corrective action."
    ),
    "exercise_scheduled": NotificationRule(
        id="exercise_scheduled",
        name="Exercise Notification",
        event_pattern="bcm.exercise.scheduled",
        tenant_id="*",
        channels=["email", "ui"],
        recipients=["team@company.com"],
        conditions={},
        template="EXERCISE SCHEDULED: {title}\n\nDate: {scheduled_date}\nParticipants: Please prepare accordingly."
    )
}

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    
    # Startup
    logger.info("Starting Notification service...")
    
    # Redis connection
    redis_client = await redis.from_url(REDIS_URL)
    logger.info("Connected to Redis")
    
    # Start event listener in background
    asyncio.create_task(event_listener())
    
    yield
    
    # Shutdown
    logger.info("Shutting down Notification service...")
    if redis_client:
        await redis_client.close()

# Create FastAPI app
app = FastAPI(
    title="BCM Notification Service",
    description="Notification management for ISO 22301 BCM Platform",
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

# Event listener for automatic notifications
async def event_listener():
    """Listen to EventBus events and trigger notifications"""
    pubsub = redis_client.pubsub()
    await pubsub.psubscribe("bcm.*")
    
    logger.info("Event listener started, subscribed to bcm.* events")
    
    async for message in pubsub.listen():
        if message["type"] == "pmessage":
            try:
                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                
                event = json.loads(data)
                await process_event_for_notifications(event)
            except Exception as e:
                logger.error(f"Error processing event for notifications: {e}")

async def process_event_for_notifications(event: Dict[str, Any]):
    """Process events and trigger matching notification rules"""
    event_type = event.get("event_type", "")
    tenant_id = event.get("tenant_id", "")
    event_data = event.get("data", {})
    
    logger.info(f"Processing event for notifications: {event_type}")
    
    # Check each notification rule
    for rule_id, rule in notification_rules.items():
        if rule.tenant_id != "*" and rule.tenant_id != tenant_id:
            continue
            
        if not rule.enabled:
            continue
            
        # Check if event matches pattern
        if rule.event_pattern not in event_type:
            continue
            
        # Check conditions
        conditions_met = True
        for key, expected_value in rule.conditions.items():
            actual_value = event_data.get(key)
            if actual_value != expected_value:
                conditions_met = False
                break
        
        if not conditions_met:
            continue
        
        # Prepare notification
        title = event_data.get("title", f"BCM Event: {event_type}")
        message = rule.template.format(
            title=title,
            message=event_data.get("description", ""),
            scheduled_date=event_data.get("scheduled_date", ""),
            severity=event_data.get("severity", "")
        )
        
        # Send notification
        notification = NotificationRequest(
            event_type=event_type,
            tenant_id=tenant_id,
            severity=event_data.get("severity", "info"),
            title=title,
            message=message,
            recipients=rule.recipients,
            channels=rule.channels,
            data=event_data
        )
        
        await send_notification(notification)

# Health check
@app.get("/health")
async def health_check():
    try:
        await redis_client.ping()
        return {
            "status": "healthy", 
            "service": "notification",
            "redis": "connected",
            "smtp_configured": bool(SMTP_USERNAME),
            "telegram_configured": bool(TELEGRAM_BOT_TOKEN)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Send notification endpoint
@app.post("/api/notifications/send")
async def send_notification_endpoint(notification: NotificationRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_notification, notification)
    return {"status": "queued", "message": "Notification queued for delivery"}

# Core notification sending function
async def send_notification(notification: NotificationRequest):
    """Send notification through specified channels"""
    notification_id = f"notif_{datetime.utcnow().timestamp()}"
    delivery_status = {}
    
    logger.info(f"Sending notification {notification_id}: {notification.title}")
    
    # Send through each channel
    for channel in notification.channels:
        try:
            if channel == "email":
                result = await send_email_notification(notification)
                delivery_status["email"] = "sent" if result else "failed"
                
            elif channel == "telegram":
                result = await send_telegram_notification(notification)
                delivery_status["telegram"] = "sent" if result else "failed"
                
            elif channel == "ui":
                result = await send_ui_notification(notification)
                delivery_status["ui"] = "sent" if result else "failed"
                
            elif channel == "sms":
                # SMS implementation would go here
                delivery_status["sms"] = "not_implemented"
                
        except Exception as e:
            logger.error(f"Error sending {channel} notification: {e}")
            delivery_status[channel] = "failed"
    
    # Store notification history
    history = NotificationHistory(
        id=notification_id,
        event_type=notification.event_type,
        tenant_id=notification.tenant_id,
        severity=notification.severity,
        title=notification.title,
        message=notification.message,
        channels=notification.channels,
        recipients=notification.recipients or [],
        sent_at=datetime.utcnow(),
        delivery_status=delivery_status
    )
    
    # You could store this in Redis or database
    logger.info(f"Notification {notification_id} processed: {delivery_status}")

async def send_email_notification(notification: NotificationRequest) -> bool:
    """Send email notification"""
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        logger.warning("SMTP not configured, skipping email notification")
        return False
        
    try:
        # Create message
        msg = MimeMultipart()
        msg['From'] = FROM_EMAIL
        msg['Subject'] = f"[BCM Alert] {notification.title}"
        
        # HTML content
        html_content = f"""
        <html>
          <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
              <div style="background-color: {'#dc3545' if notification.severity == 'critical' else '#ffc107' if notification.severity == 'warning' else '#17a2b8'}; color: white; padding: 20px; text-align: center;">
                <h2>{notification.title}</h2>
                <p>Severity: {notification.severity.upper()}</p>
              </div>
              <div style="padding: 20px; background-color: #f8f9fa;">
                <p>{notification.message.replace(chr(10), '<br>')}</p>
                <hr>
                <p><small>Event Type: {notification.event_type}</small></p>
                <p><small>Tenant: {notification.tenant_id}</small></p>
                <p><small>Time: {datetime.utcnow().isoformat()}</small></p>
              </div>
              <div style="padding: 10px; background-color: #e9ecef; text-align: center; font-size: 12px;">
                <p>This is an automated message from BCM Platform. Please do not reply.</p>
              </div>
            </div>
          </body>
        </html>
        """
        
        msg.attach(MimeText(html_content, 'html'))
        
        # Send to recipients
        recipients = notification.recipients or [FROM_EMAIL]
        msg['To'] = ', '.join(recipients)
        
        # Connect and send
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        
        for recipient in recipients:
            server.sendmail(FROM_EMAIL, recipient, msg.as_string())
        
        server.quit()
        logger.info(f"Email sent successfully to {recipients}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

async def send_telegram_notification(notification: NotificationRequest) -> bool:
    """Send Telegram notification"""
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("Telegram not configured, skipping telegram notification")
        return False
        
    try:
        # Format message for Telegram
        message = f"""
*BCM Alert*

*{notification.title}*

{notification.message}

*Details:*
• Event: `{notification.event_type}`
• Severity: `{notification.severity.upper()}`
• Tenant: `{notification.tenant_id}`
• Time: `{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}`
        """
        
        # Send to configured chat IDs (you'd need to store these)
        chat_ids = ["-1001234567890"]  # Example group chat ID
        
        async with httpx.AsyncClient() as client:
            for chat_id in chat_ids:
                response = await client.post(
                    f"{TELEGRAM_API_URL}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": message,
                        "parse_mode": "Markdown"
                    }
                )
                
                if response.status_code == 200:
                    logger.info(f"Telegram message sent to {chat_id}")
                else:
                    logger.error(f"Failed to send Telegram message: {response.text}")
                    return False
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {e}")
        return False

async def send_ui_notification(notification: NotificationRequest) -> bool:
    """Send UI notification through EventBus"""
    try:
        # Send UI notification event to EventBus
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{EVENTBUS_URL}/api/events/publish",
                json={
                    "event_type": "bcm.notification.ui",
                    "tenant_id": notification.tenant_id,
                    "data": {
                        "title": notification.title,
                        "message": notification.message,
                        "severity": notification.severity,
                        "timestamp": datetime.utcnow().isoformat(),
                        "source_event": notification.event_type
                    }
                }
            )
            
            if response.status_code == 200:
                logger.info("UI notification sent to EventBus")
                return True
            else:
                logger.error(f"Failed to send UI notification: {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"Failed to send UI notification: {e}")
        return False

# Get notification rules
@app.get("/api/notifications/rules")
async def get_notification_rules(tenant_id: Optional[str] = None):
    if tenant_id:
        filtered_rules = {
            k: v for k, v in notification_rules.items() 
            if v.tenant_id == tenant_id or v.tenant_id == "*"
        }
        return filtered_rules
    return notification_rules

# Create/Update notification rule
@app.post("/api/notifications/rules")
async def create_notification_rule(rule: NotificationRule):
    notification_rules[rule.id] = rule
    return {"status": "created", "rule_id": rule.id}

# Test notification
@app.post("/api/notifications/test")
async def test_notification(channels: List[str], tenant_id: str = "test_tenant"):
    test_notification = NotificationRequest(
        event_type="bcm.test.notification",
        tenant_id=tenant_id,
        severity="info",
        title="Test Notification",
        message="This is a test notification from BCM Platform.",
        recipients=["test@example.com"],
        channels=channels
    )
    
    await send_notification(test_notification)
    return {"status": "sent", "message": "Test notification sent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
