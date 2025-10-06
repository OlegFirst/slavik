# Infrastructure Quick Reference

**Обновлено:** 2025-10-06

---

## 🚀 Quick Commands

### Start Core Services
```bash
# Start database & redis
docker-compose up -d postgres redis

# Test connections
psql $DATABASE_URL -c "SELECT 1;"
redis-cli -u $REDIS_URL ping

# Apply migrations
cd infrastructure/database && python apply_migrations_simple.py
```

### Start EventBus
```bash
cd infrastructure/eventbus
export EVENTBUS_TRANSPORT=redis
python -m eventbus.main
```

### Test Qdrant
```bash
cd infrastructure/vector-db
python test_connection.py
python qdrant/init_collections.py
```

### Start API Gateway
```bash
cd infrastructure/security/api-gateway
uvicorn main:app --host 0.0.0.0 --port 3001
```

---

## 📊 Service Status

| Service | Status | Port | Documentation |
|---------|--------|------|---------------|
| **Database** | ✅ Ready | 5432 | [database/README.md](database/README.md) |
| **Redis** | ✅ Ready | 6379 | [database/README.md](database/README.md) |
| **EventBus** | ✅ Ready | - | [eventbus/README.md](eventbus/README.md) |
| **API Gateway** | ✅ Ready | 3001 | [security/README.md](security/README.md) |
| **Vector DB** | ✅ Ready | Cloud | [vector-db/README.md](vector-db/README.md) |
| **Monitoring** | ✅ Ready | 9090, 3002 | [monitoring/README.md](monitoring/README.md) |
| **Service Discovery** | ✅ Ready | 8500 | [service-discovery/README.md](service-discovery/README.md) |
| **Notification** | ⚠️ Config | - | [notification-service/README.md](notification-service/README.md) |
| **WebSocket** | ⚠️ Config | 8001 | [realtime-websocket/README.md](realtime-websocket/README.md) |
| **Message Queue** | ⚠️ Config | 5672 | [message-queue/README.md](message-queue/README.md) |

---

## 🔑 Key Environment Variables

```bash
# Database
DATABASE_URL=postgresql://...
REDIS_URL=redis://localhost:6379

# Qdrant Cloud
QDRANT_URL=https://xxx.eu-west-1-0.aws.cloud.qdrant.io
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Auth
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256

# AI
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Notifications
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

**Full list:** See [.env.example](../.env.example)

---

## 📁 Directory Structure

```
infrastructure/
├── README.md                    # Main overview
├── INDEX.md                     # Documentation index ⭐
├── OVERVIEW.md                  # Architecture overview ⭐
├── TECHNICAL_GUIDE.md           # Developer guide ⭐
│
├── database/                    # ✅ PostgreSQL + Redis
├── eventbus/                    # ✅ Event-driven messaging
├── security/api-gateway/        # ✅ API Gateway (4,345 lines)
├── vector-db/                   # ✅ Qdrant Cloud
├── monitoring/                  # ✅ Prometheus + Grafana
├── service-discovery/           # ✅ Service registry
│
├── notification-service/        # ⚠️ Email, Slack, Telegram
├── realtime-websocket/          # ⚠️ WebSocket server
├── message-queue/               # ⚠️ RabbitMQ
├── intelligent-gateway/         # ⚠️ AI-powered routing
├── secrets-manager/             # ⚠️ HashiCorp Vault
│
├── data/compliance/             # ISO 22301 data storage
└── архив/                       # Old documentation (archived)
```

---

## 🔗 Quick Links

### Documentation
- [INDEX.md](INDEX.md) - Full documentation index
- [OVERVIEW.md](OVERVIEW.md) - Architecture overview
- [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md) - Setup & deployment

### Services
- [EventBus Quickstart](eventbus/QUICKSTART.md)
- [Qdrant Quickstart](vector-db/QUICKSTART.md)
- [Notification Quickstart](notification-service/QUICK_START.md)

### Related
- [Shared Library](../shared/) - Common code
- [Platform Services](../platform-services/) - Business services
- [Intelligent Core](../intelligent-core/) - AI components

---

## 🆘 Common Issues

### Database Connection Failed
```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1;"

# Fix: Check .env DATABASE_URL
```

### Redis Connection Failed
```bash
# Test connection
redis-cli -u $REDIS_URL ping

# Fix: Start Redis
docker-compose up -d redis
```

### EventBus Not Working
```bash
# Check transport
echo $EVENTBUS_TRANSPORT  # Should be "redis"

# Fix: Set transport
export EVENTBUS_TRANSPORT=redis
```

### Qdrant Connection Failed
```bash
# Test connection
cd infrastructure/vector-db
python test_connection.py

# Fix: Check QDRANT_URL and QDRANT_API_KEY in .env
```

### API Gateway 401
```bash
# Fix: Check JWT_SECRET in .env matches token generation
```

**More troubleshooting:** [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md#troubleshooting)

---

## 🎯 Next Steps (Priorities)

### Tier 0 - КРИТИЧНО
1. ✅ **vector-db** (Qdrant) - DONE!
2. ⏳ **notification-service** - 4-6 hours
3. ⏳ **realtime-websocket** - 6-8 hours
4. ⏳ **message-queue** - 4-6 hours

### Tier 1 - ПОЛЕЗНО
5. **secrets-manager** (Vault)
6. **intelligent-gateway**
7. **observability**

---

## 📞 Contact

**Questions?**
- Check service-specific README
- See [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md)
- Review [архив/](архив/) for historical context

---

**Last Updated:** 2025-10-06
