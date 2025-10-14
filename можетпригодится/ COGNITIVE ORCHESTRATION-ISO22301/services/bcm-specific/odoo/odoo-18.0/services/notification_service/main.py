"""
BCM Platform - Notification Service

Микросервис для отправки уведомлений:
- Email уведомления
- SMS уведомления  
- Push уведомления
- Webhook уведомления
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import redis
import pika
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Подключения к внешним сервисам
redis_client = None
rabbitmq_connection = None

@app.on_event("startup")
async def startup_event():
    """Инициализация подключений при старте"""
    global redis_client, rabbitmq_connection
    
    try:
        # Redis подключение
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/2")
        redis_client = redis.from_url(redis_url)
        
        # RabbitMQ подключение
        rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        rabbitmq_connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
        
        logger.info("✅ Notification Service запущен успешно")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Закрытие подключений при остановке"""
    if rabbitmq_connection:
        rabbitmq_connection.close()

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
async def send_email(notification: EmailNotification):
    """Отправка email уведомления"""
    try:
        # TODO: Реализовать отправку email
        logger.info(f"📧 Отправка email: {notification.subject} -> {notification.to}")
        
        # Заглушка - сохранение в Redis для разработки
        email_data = {
            "type": "email",
            "to": notification.to,
            "subject": notification.subject,
            "body": notification.body,
            "status": "sent"
        }
        
        redis_client.lpush("notifications:sent", str(email_data))
        
        return {
            "status": "success",
            "message": "Email отправлен успешно",
            "recipients": len(notification.to)
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка отправки email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sms/send")
async def send_sms(notification: SMSNotification):
    """Отправка SMS уведомления"""
    try:
        # TODO: Реализовать отправку SMS
        logger.info(f"📱 Отправка SMS: {notification.message} -> {notification.to}")
        
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
        logger.error(f"❌ Ошибка отправки SMS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/push/send")
async def send_push(notification: PushNotification):
    """Отправка push уведомления"""
    try:
        # TODO: Реализовать push уведомления
        logger.info(f"🔔 Отправка push: {notification.title} -> {notification.user_ids}")
        
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
        logger.error(f"❌ Ошибка отправки push: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/send")
async def send_webhook(notification: WebhookNotification):
    """Отправка webhook уведомления"""
    try:
        # TODO: Реализовать webhook отправку
        logger.info(f"🌐 Отправка webhook: {notification.url}")
        
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
        logger.error(f"❌ Ошибка отправки webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notifications/history")
async def get_notification_history(limit: int = 100):
    """История отправленных уведомлений"""
    try:
        history = redis_client.lrange("notifications:sent", 0, limit-1)
        return {
            "status": "success",
            "history": [eval(item.decode()) for item in history],
            "count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    uvicorn.run(app, host="0.0.0.0", port=8000)
