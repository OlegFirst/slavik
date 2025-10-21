"""
BCM Platform - Notification Service

Микросервис для отправки уведомлений:
- Email уведомления
- SMS уведомления
- Push уведомления
- Webhook уведомления

Интеграции:
- Supabase PostgreSQL - хранение истории уведомлений
- Redis - кэширование и очереди
- RabbitMQ - асинхронная доставка
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import redis
import pika
import os
import logging
import json
import asyncio
import httpx
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
notifications_sent = Counter(
    'notifications_sent_total',
    'Total notifications sent',
    ['channel', 'status']
)
notifications_duration = Histogram(
    'notification_duration_seconds',
    'Time spent processing notification',
    ['channel']
)

app = FastAPI(
    title="BCM Notification Service",
    description="Сервис уведомлений для BCM Platform",
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

# Модели данных
class EmailNotification(BaseModel):
    to: List[EmailStr]
    subject: str
    body: str
    html_body: Optional[str] = None
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None

class SMSNotification(BaseModel):
    to: List[str]
    message: str

class PushNotification(BaseModel):
    user_ids: List[int]
    title: str
    message: str
    data: Optional[dict] = None

class WebhookNotification(BaseModel):
    url: str
    method: str = "POST"
    payload: dict
    headers: Optional[dict] = None

# Global connections
redis_client: Optional[redis.Redis] = None
rabbitmq_connection: Optional[pika.BlockingConnection] = None
rabbitmq_channel: Optional[pika.channel.Channel] = None
supabase: Optional[Client] = None

@app.on_event("startup")
async def startup_event():
    """Инициализация подключений при старте"""
    global redis_client, rabbitmq_connection, rabbitmq_channel, supabase

    try:
        # Supabase подключение
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if supabase_url and supabase_key:
            supabase = create_client(supabase_url, supabase_key)
            logger.info(" Connected to Supabase PostgreSQL")
        else:
            logger.warning("️  Supabase not configured - notifications will only be cached in Redis")

        # Redis подключение
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            redis_client.ping()
            logger.info(" Connected to Redis")
        else:
            logger.error(" Redis URL not configured")
            raise Exception("REDIS_URL is required")

        # RabbitMQ подключение (optional)
        rabbitmq_url = os.getenv("RABBITMQ_URL")
        if rabbitmq_url:
            rabbitmq_connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
            rabbitmq_channel = rabbitmq_connection.channel()

            # Declare notification queues
            rabbitmq_channel.queue_declare(queue='notifications.email', durable=True)
            rabbitmq_channel.queue_declare(queue='notifications.sms', durable=True)
            rabbitmq_channel.queue_declare(queue='notifications.push', durable=True)
            rabbitmq_channel.queue_declare(queue='notifications.webhook', durable=True)

            logger.info(" Connected to RabbitMQ")
        else:
            logger.info("ℹ️  RabbitMQ not configured (direct delivery only)")

        logger.info(" Notification Service started successfully")

    except Exception as e:
        logger.error(f" Startup error: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Закрытие подключений при остановке"""
    if rabbitmq_connection:
        rabbitmq_connection.close()
    if redis_client:
        redis_client.close()
    logger.info(" Notification Service stopped")

# ============================================
# Helper Functions
# ============================================

async def save_notification_to_db(
    channel: str,
    recipients: List[str],
    message: str,
    subject: Optional[str] = None,
    title: Optional[str] = None,
    severity: str = "info",
    metadata: Optional[Dict] = None
) -> str:
    """Save notification to Supabase database"""
    try:
        if not supabase:
            logger.warning("Supabase not configured, skipping DB save")
            return None

        notification_data = {
            "channel": channel,
            "recipients": json.dumps(recipients),
            "message": message,
            "subject": subject,
            "title": title,
            "severity": severity,
            "status": "pending",
            "metadata": json.dumps(metadata or {}),
            "created_at": datetime.now().isoformat()
        }

        result = supabase.table("notifications").insert(notification_data).execute()

        if result.data:
            notification_id = result.data[0]["id"]
            logger.info(f" Notification saved to DB: {notification_id}")
            return notification_id
        else:
            logger.error("Failed to save notification to DB")
            return None

    except Exception as e:
        logger.error(f"Error saving notification to DB: {e}")
        return None


async def update_notification_status(
    notification_id: str,
    status: str,
    error_message: Optional[str] = None
):
    """Update notification status in database"""
    try:
        if not supabase or not notification_id:
            return

        update_data = {
            "status": status,
            "updated_at": datetime.now().isoformat()
        }

        if status == "sent":
            update_data["sent_at"] = datetime.now().isoformat()

        if error_message:
            update_data["error_message"] = error_message

        supabase.table("notifications").update(update_data).eq("id", notification_id).execute()
        logger.info(f" Notification {notification_id} status updated to {status}")

    except Exception as e:
        logger.error(f"Error updating notification status: {e}")


async def cache_notification_in_redis(
    channel: str,
    data: Dict,
    ttl: int = 86400  # 24 hours
):
    """Cache notification in Redis for quick access"""
    try:
        if not redis_client:
            return

        key = f"notification:{channel}:{datetime.now().timestamp()}"
        redis_client.setex(key, ttl, json.dumps(data))

        # Also add to sorted set for history
        redis_client.zadd(
            f"notifications:{channel}:history",
            {key: datetime.now().timestamp()}
        )

        # Trim history to last 1000 items
        redis_client.zremrangebyrank(f"notifications:{channel}:history", 0, -1001)

    except Exception as e:
        logger.error(f"Error caching notification in Redis: {e}")


async def publish_to_rabbitmq(
    queue_name: str,
    message: Dict
):
    """Publish notification to RabbitMQ queue for async processing"""
    try:
        if not rabbitmq_channel:
            logger.info("RabbitMQ not available, processing directly")
            return False

        rabbitmq_channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type='application/json'
            )
        )

        logger.info(f" Message published to RabbitMQ queue: {queue_name}")
        return True

    except Exception as e:
        logger.error(f"Error publishing to RabbitMQ: {e}")
        return False

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Проверка Redis
        redis_client.ping()
        
        return {
            "status": "healthy",
            "service": "notification_service",
            "version": "1.0.0",
            "components": {
                "redis": "connected",
                "rabbitmq": "connected" if rabbitmq_connection else "disconnected"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {e}")

@app.post("/email/send")
async def send_email(notification: EmailNotification, background_tasks: BackgroundTasks):
    """Отправка email уведомления"""
    start_time = datetime.now()

    try:
        logger.info(f" Отправка email: {notification.subject} -> {notification.to}")

        # 1. Save to database
        notification_id = await save_notification_to_db(
            channel="email",
            recipients=notification.to,
            message=notification.body,
            subject=notification.subject,
            severity="info"
        )

        # 2. Cache in Redis
        await cache_notification_in_redis("email", {
            "id": notification_id,
            "to": notification.to,
            "subject": notification.subject,
            "body": notification.body,
            "timestamp": datetime.now().isoformat()
        })

        # 3. Publish to RabbitMQ for async processing
        published = await publish_to_rabbitmq("notifications.email", {
            "id": notification_id,
            "to": notification.to,
            "subject": notification.subject,
            "body": notification.body,
            "html_body": notification.html_body,
            "cc": notification.cc,
            "bcc": notification.bcc
        })

        if not published:
            # Direct processing if RabbitMQ not available
            background_tasks.add_task(process_email_notification, notification, notification_id)

        # 4. Update metrics
        duration = (datetime.now() - start_time).total_seconds()
        notifications_duration.labels(channel="email").observe(duration)
        notifications_sent.labels(channel="email", status="success").inc()

        # 5. Update status
        await update_notification_status(notification_id, "sent")

        return {
            "status": "success",
            "message": "Email queued for delivery",
            "notification_id": notification_id,
            "recipients": len(notification.to)
        }

    except Exception as e:
        logger.error(f" Ошибка отправки email: {e}")
        notifications_sent.labels(channel="email", status="failed").inc()

        if notification_id:
            await update_notification_status(notification_id, "failed", str(e))

        raise HTTPException(status_code=500, detail=str(e))


async def process_email_notification(notification: EmailNotification, notification_id: str):
    """Background task to actually send email"""
    try:
        # TODO: Implement actual SMTP sending
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")

        if all([smtp_host, smtp_user, smtp_password]):
            # Actual SMTP sending would go here
            logger.info(f" Sending email via SMTP: {smtp_host}")
            # ... SMTP implementation ...

        logger.info(f" Email processed successfully: {notification_id}")

    except Exception as e:
        logger.error(f" Error processing email: {e}")
        await update_notification_status(notification_id, "failed", str(e))

@app.post("/sms/send")
async def send_sms(notification: SMSNotification):
    """Отправка SMS уведомления"""
    try:
        # TODO: Реализовать отправку SMS
        logger.info(f"Отправка SMS: {notification.message} -> {notification.to}")
        
        # Заглушка
        sms_data = {
            "type": "sms",
            "to": notification.to,
            "message": notification.message,
            "status": "sent"
        }
        
        redis_client.lpush("notifications:sent", str(sms_data))
        
        return {
            "status": "success", 
            "message": "SMS отправлено успешно",
            "recipients": len(notification.to)
        }
        
    except Exception as e:
        logger.error(f"Ошибка отправки SMS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/push/send")
async def send_push(notification: PushNotification):
    """Отправка push уведомления"""
    try:
        # TODO: Реализовать push уведомления
        logger.info(f"Отправка push: {notification.title} -> {notification.user_ids}")
        
        # Заглушка
        push_data = {
            "type": "push",
            "user_ids": notification.user_ids,
            "title": notification.title,
            "message": notification.message,
            "status": "sent"
        }
        
        redis_client.lpush("notifications:sent", str(push_data))
        
        return {
            "status": "success",
            "message": "Push уведомление отправлено",
            "recipients": len(notification.user_ids)
        }
        
    except Exception as e:
        logger.error(f"Ошибка отправки push: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/send")
async def send_webhook(notification: WebhookNotification):
    """Отправка webhook уведомления"""
    try:
        # TODO: Реализовать webhook отправку
        logger.info(f"Отправка webhook: {notification.url}")
        
        # Заглушка
        webhook_data = {
            "type": "webhook",
            "url": notification.url,
            "payload": notification.payload,
            "status": "sent"
        }
        
        redis_client.lpush("notifications:sent", str(webhook_data))
        
        return {
            "status": "success",
            "message": "Webhook отправлен успешно"
        }
        
    except Exception as e:
        logger.error(f"Ошибка отправки webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notifications/history")
async def get_notification_history(
    limit: int = 100,
    channel: Optional[str] = None,
    status: Optional[str] = None
):
    """История отправленных уведомлений"""
    try:
        if supabase:
            # Get from Supabase database
            query = supabase.table("notifications").select("*")

            if channel:
                query = query.eq("channel", channel)

            if status:
                query = query.eq("status", status)

            result = query.order("created_at", desc=True).limit(limit).execute()

            return {
                "status": "success",
                "source": "database",
                "history": result.data,
                "count": len(result.data)
            }
        else:
            # Fallback to Redis
            history_keys = redis_client.zrevrange(
                f"notifications:{channel or '*'}:history",
                0,
                limit - 1
            )

            history = []
            for key in history_keys:
                data = redis_client.get(key)
                if data:
                    history.append(json.loads(data))

            return {
                "status": "success",
                "source": "redis_cache",
                "history": history,
                "count": len(history)
            }

    except Exception as e:
        logger.error(f"Error fetching notification history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notifications/stats")
async def get_notification_stats():
    """Статистика уведомлений"""
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not configured")

        # Get stats from database
        result = supabase.rpc("get_notification_stats").execute()

        return {
            "status": "success",
            "stats": result.data
        }

    except Exception as e:
        logger.error(f"Error fetching notification stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    """Главная страница API"""
    return {
        "service": "BCM Notification Service",
        "version": "1.0.0",
        "description": "Микросервис для отправки уведомлений",
        "endpoints": {
            "email": "/email/send",
            "sms": "/sms/send", 
            "push": "/push/send",
            "webhook": "/webhook/send",
            "history": "/notifications/history",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8035))  # Changed from 8000 to 8035
    uvicorn.run(app, host="0.0.0.0", port=port)
