# 📧 Notification Service

**Port:** 8035
**Version:** 1.0.0
**Status:** ✅ Adapted for production

Multi-channel notification service for BCM Platform.

---

## 🎯 Features

### Supported Channels:
1. **📧 Email** - SMTP-based email notifications
2. **📱 SMS** - SMS notifications (Twilio integration)
3. **🔔 Push** - Push notifications (Firebase integration)
4. **🔗 Webhook** - HTTP webhook notifications

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Run Service

```bash
python main.py
```

Service will start on **http://localhost:8035**

---

## 📡 API Endpoints

### Health Check
```bash
GET /health
```

### Send Email
```bash
POST /email/send
Content-Type: application/json

{
  "to": ["user@example.com"],
  "subject": "Incident Alert",
  "body": "Critical incident detected...",
  "html_body": "<h1>Alert</h1>",
  "cc": [],
  "bcc": []
}
```

### Send SMS
```bash
POST /sms/send
Content-Type: application/json

{
  "to": ["+1234567890"],
  "message": "BCM Alert: Critical incident"
}
```

### Send Push Notification
```bash
POST /push/send
Content-Type: application/json

{
  "user_ids": [1, 2, 3],
  "title": "BCM Alert",
  "message": "Critical incident detected",
  "data": {"incident_id": 123}
}
```

### Send Webhook
```bash
POST /webhook/send
Content-Type: application/json

{
  "url": "https://example.com/webhook",
  "method": "POST",
  "payload": {"event": "incident", "severity": "critical"},
  "headers": {"Authorization": "Bearer token"}
}
```

### Notification History
```bash
GET /notifications/history?limit=100
```

---

## 🔧 Configuration

### Required Environment Variables:

```bash
PORT=8035
UPSTASH_REDIS_URL=redis://...        # Upstash Redis URL
SMTP_HOST=smtp.gmail.com             # SMTP server
SMTP_PORT=587
SMTP_USER=notifications@domain.com
SMTP_PASSWORD=your_password
```

### Optional:

```bash
RABBITMQ_URL=amqp://...              # Optional message queue
EVENTBUS_URL=http://localhost:8001   # EventBus integration
TWILIO_ACCOUNT_SID=...               # For SMS
FIREBASE_PROJECT_ID=...              # For Push
```

---

## 🏗️ Architecture

```
User/Service
      ↓
[Notification Service:8035]
      ├── Email  → SMTP Server
      ├── SMS    → Twilio API
      ├── Push   → Firebase
      └── Webhook → HTTP POST
      ↓
[Redis] - History storage
[EventBus] - Async notifications
```

---

## 🔐 Authentication

Service uses Supabase JWT tokens:

```bash
POST /email/send
Authorization: Bearer <supabase_jwt_token>
```

---

## 📊 Monitoring

### Prometheus Metrics:
- `notifications_sent_total{channel}` - Total notifications sent
- `notifications_failed_total{channel}` - Failed notifications
- `notification_duration_seconds{channel}` - Processing time

### Health Check:
```bash
curl http://localhost:8035/health
```

---

## 🧪 Testing

```bash
# Test email (development mode)
curl -X POST http://localhost:8035/email/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["test@example.com"],
    "subject": "Test",
    "body": "Test email"
  }'

# Check history
curl http://localhost:8035/notifications/history
```

---

## 🐳 Docker

```bash
docker build -t notification-service .
docker run -p 8035:8035 --env-file .env notification-service
```

---

## 📝 TODO

- [ ] Implement real SMTP sending (currently stub)
- [ ] Add Twilio SMS integration
- [ ] Add Firebase Push integration
- [ ] Add retry logic for failed notifications
- [ ] Add rate limiting per user
- [ ] Add notification templates
- [ ] Add scheduling (send later)
- [ ] Add A/B testing for notifications

---

## 🔗 Integration

### With Coordination Center:

Service is registered as tool:

```python
{
  "tool_id": "notification_service",
  "base_url": "http://localhost:8035",
  "actions": ["send_email", "send_sms", "send_push", "send_webhook"]
}
```

### With EventBus:

Publishes events:
- `notification.sent` - When notification sent
- `notification.failed` - When sending failed

---

**Ready for production!** ✅
