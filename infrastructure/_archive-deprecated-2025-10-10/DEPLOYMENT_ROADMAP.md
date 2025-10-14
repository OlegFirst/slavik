# 🚀 AI-Platform BCM - Complete Deployment Roadmap

**Version:** 1.0
**Date:** 2025-10-06
**Status:** Production Deployment Plan

---

## 📋 Содержание

1. [Phase 0: Prerequisites](#phase-0-prerequisites)
2. [Phase 1: Foundation Layer](#phase-1-foundation-layer)
3. [Phase 2: Infrastructure Services](#phase-2-infrastructure-services)
4. [Phase 3: Shared Libraries](#phase-3-shared-libraries)
5. [Phase 4: Platform Services](#phase-4-platform-services)
6. [Phase 5: Intelligent Core](#phase-5-intelligent-core)
7. [Phase 6: Human Interface](#phase-6-human-interface)
8. [Phase 7: Production Hardening](#phase-7-production-hardening)

---

## Phase 0: Prerequisites

**Цель:** Подготовить окружение и проверить все зависимости

**Время:** 2-3 часа

### 0.1 System Requirements ✅

```bash
# Check versions
docker --version          # >= 24.0
docker-compose --version  # >= 2.20
python3 --version         # >= 3.11
psql --version            # >= 14
redis-cli --version       # >= 7.0

# Check available resources
docker system df          # Disk space
free -h                   # Memory (min 8GB)
nproc                     # CPU cores (min 4)
```

**Критерии успеха:**
- ✅ Docker и Docker Compose установлены
- ✅ Python 3.11+ установлен
- ✅ PostgreSQL client (psql) установлен
- ✅ Redis CLI установлен
- ✅ Минимум 8GB RAM, 4 CPU cores, 50GB disk

---

### 0.2 Clone Repository ✅

```bash
# Clone project
git clone <repo-url>
cd AI-Platform-ISO

# Verify structure
ls -la

# Should see:
# - infrastructure/
# - shared/
# - platform-services/
# - intelligent-core/
# - .env.example
# - docker-compose.yml
```

**Критерии успеха:**
- ✅ Репозиторий склонирован
- ✅ Все папки на месте

---

### 0.3 Environment Configuration ✅

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Минимальная конфигурация для старта:**
```bash
# Database (Supabase)
DATABASE_URL=postgresql://postgres.xxx:password@xxx.supabase.co:5432/postgres

# Redis
REDIS_URL=redis://localhost:6379

# Qdrant Cloud
QDRANT_URL=https://xxx.eu-west-1-0.aws.cloud.qdrant.io
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Auth
JWT_SECRET=generate-random-secret-here-min-32-chars
JWT_ALGORITHM=HS256

# AI (optional for infrastructure testing)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

**Критерии успеха:**
- ✅ `.env` файл создан
- ✅ Все критичные переменные заполнены
- ✅ JWT_SECRET сгенерирован (min 32 символа)

---

## Phase 1: Foundation Layer

**Цель:** Запустить базовые инфраструктурные сервисы

**Время:** 3-4 часа

### 1.1 Start Database & Redis ✅

```bash
# Start core services
docker-compose up -d postgres redis

# Wait for services to be ready
sleep 10

# Verify PostgreSQL
psql $DATABASE_URL -c "SELECT version();"

# Verify Redis
redis-cli -u $REDIS_URL ping
# Expected: PONG
```

**Критерии успеха:**
- ✅ PostgreSQL container запущен
- ✅ Redis container запущен
- ✅ psql подключается к БД
- ✅ redis-cli получает PONG

**Troubleshooting:**
```bash
# If connection fails
docker-compose logs postgres
docker-compose logs redis

# Check containers
docker-compose ps
```

---

### 1.2 Apply Database Migrations ✅

```bash
cd infrastructure/database

# Test connection first
python -c "
from managers.supabase_client import get_supabase_client
client = get_supabase_client()
print('✅ Supabase connection OK')
"

# Apply all migrations (006-041)
python apply_migrations_simple.py

# Or apply manually
psql $DATABASE_URL -f migrations_source/006_bia_risk_schemas.sql
psql $DATABASE_URL -f migrations_source/007_governance_audit_schemas.sql
# ... continue for all migrations
```

**Критерии успеха:**
- ✅ Все 36 миграций применены (006-041)
- ✅ Таблицы созданы (users, organizations, bia_risks, etc.)
- ✅ RLS policies настроены
- ✅ Indexes созданы

**Verify:**
```bash
# Check tables
psql $DATABASE_URL -c "\dt"

# Should see:
# - users
# - organizations
# - bia_critical_functions
# - risk_assessments
# - compliance_frameworks
# - ... etc
```

---

### 1.3 Initialize Qdrant Vector DB ✅

```bash
cd infrastructure/vector-db

# Install dependencies
pip install -r requirements.txt

# Test connection
python test_connection.py
# Expected: ✅ Connected successfully!

# Initialize collections
python qdrant/init_collections.py
# Creates: knowledge_base, workflow_cases, ai_memory
```

**Критерии успеха:**
- ✅ Qdrant Cloud подключен
- ✅ 3 коллекции созданы:
  - knowledge_base (1536-dim, Cosine)
  - workflow_cases (1536-dim, Cosine)
  - ai_memory (1536-dim, Cosine)

**Verify:**
```python
from qdrant import QdrantVectorDB

db = QdrantVectorDB()
info = db.get_collection_info("knowledge_base")
print(info)
# Should show: status=green, vectors_count=0
```

---

### 1.4 Setup Redis Cache & Session Store ✅

```bash
cd infrastructure/database

# Test Redis managers
python test_redis_managers.py

# Expected output:
# ✅ Cache Manager: OK
# ✅ Session Store: OK
# ✅ Rate Limiter: OK
```

**Критерии успеха:**
- ✅ Redis cache работает
- ✅ Session store работает
- ✅ Rate limiter работает

---

## Phase 2: Infrastructure Services

**Цель:** Запустить критичные infrastructure сервисы

**Время:** 6-8 часов

### 2.1 EventBus Service ✅

```bash
cd infrastructure/eventbus

# Install dependencies
pip install -r requirements.txt

# Configure transport
export EVENTBUS_TRANSPORT=redis
export REDIS_URL=redis://localhost:6379

# Run tests
pytest tests/ -v

# Start EventBus
python -m eventbus.main

# In another terminal, test publish/subscribe
python -c "
import asyncio
from eventbus import EventBus

async def test():
    eb = EventBus()
    await eb.connect()

    # Subscribe
    async def handler(event):
        print(f'Received: {event}')

    await eb.subscribe('test.topic', handler)

    # Publish
    await eb.publish('test.topic', {'msg': 'Hello EventBus!'})

    await asyncio.sleep(1)

asyncio.run(test())
"
```

**Критерии успеха:**
- ✅ EventBus подключен к Redis
- ✅ Publish/Subscribe работает
- ✅ Events доставляются

**Документация:** [eventbus/QUICKSTART.md](eventbus/QUICKSTART.md)

---

### 2.2 API Gateway ✅

```bash
cd infrastructure/security/api-gateway

# Install dependencies
pip install -r requirements.txt

# Configure
export JWT_SECRET=$JWT_SECRET
export DATABASE_URL=$DATABASE_URL
export REDIS_URL=$REDIS_URL

# Start API Gateway
uvicorn main:app --host 0.0.0.0 --port 3001

# Test (in another terminal)
curl http://localhost:3001/health
# Expected: {"status": "healthy"}

# Test auth
curl -X POST http://localhost:3001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'
```

**Критерии успеха:**
- ✅ API Gateway запущен на порту 3001
- ✅ Health check работает
- ✅ JWT authentication работает
- ✅ Rate limiting активен

---

### 2.3 Monitoring Stack ✅

```bash
cd infrastructure/monitoring

# Start Prometheus + Grafana
docker-compose up -d

# Wait for startup
sleep 10

# Access dashboards
open http://localhost:9090   # Prometheus
open http://localhost:3002   # Grafana (admin/changeme)

# Verify Prometheus targets
curl http://localhost:9090/api/v1/targets
```

**Критерии успеха:**
- ✅ Prometheus запущен (port 9090)
- ✅ Grafana запущен (port 3002)
- ✅ Targets configured
- ✅ Metrics собираются

**Документация:** [monitoring/README.md](monitoring/README.md)

---

### 2.4 Service Discovery ✅

```bash
cd infrastructure/service-discovery

# Install dependencies
pip install -r requirements.txt

# Start Service Discovery
python main.py

# Register a service
curl -X POST http://localhost:8500/v1/agent/service/register \
  -d '{
    "ID": "bia-service-1",
    "Name": "bia-service",
    "Port": 8001,
    "Check": {
      "HTTP": "http://localhost:8001/health",
      "Interval": "30s"
    }
  }'

# List services
curl http://localhost:8500/v1/catalog/services
```

**Критерии успеха:**
- ✅ Service Discovery запущен
- ✅ Health checks работают
- ✅ Service registry работает

---

### 2.5 Notification Service ⚠️

```bash
cd infrastructure/notification-service

# Configure SMTP
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=your-email@gmail.com
export SMTP_PASSWORD=your-app-password

# Configure Slack (optional)
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx

# Install dependencies
pip install -r requirements.txt

# Start service
uvicorn main:app --port 8010

# Test email
curl -X POST http://localhost:8010/send/email \
  -H "Content-Type: application/json" \
  -d '{
    "to": "test@example.com",
    "subject": "Test",
    "body": "Hello from BCM Platform!"
  }'
```

**Критерии успеха:**
- ✅ Notification service запущен
- ✅ Email отправка работает
- ✅ Slack integration (optional) работает

**Документация:** [notification-service/QUICK_START.md](notification-service/QUICK_START.md)

---

### 2.6 WebSocket Service ⚠️

```bash
cd infrastructure/realtime-websocket

# Install dependencies
pip install -r requirements.txt

# Start WebSocket server
uvicorn main:app --host 0.0.0.0 --port 8001

# Test WebSocket connection (in browser console)
const ws = new WebSocket('ws://localhost:8001/ws');
ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Received:', e.data);
ws.send(JSON.stringify({ type: 'ping' }));
```

**Критерии успеха:**
- ✅ WebSocket server запущен (port 8001)
- ✅ Client connections работают
- ✅ Broadcast работает

**Документация:** [realtime-websocket/README.md](realtime-websocket/README.md)

---

## Phase 3: Shared Libraries

**Цель:** Подготовить shared libraries для использования в сервисах

**Время:** 2-3 часа

### 3.1 Install Shared Dependencies ✅

```bash
cd shared/

# Install all dependencies
pip install -r requirements.txt

# Or install from project root
cd ..
pip install -e shared/
```

**Критерии успеха:**
- ✅ Все зависимости установлены
- ✅ Shared library доступна для импорта

---

### 3.2 Test Shared Modules ✅

```bash
# Test database module
python -c "
from shared.database import get_db
import asyncio

async def test():
    db = await get_db()
    result = await db.fetch_one('SELECT 1 as test')
    print(f'✅ Database: {result}')

asyncio.run(test())
"

# Test auth module
python -c "
from shared.auth import create_jwt_token, verify_jwt_token

token = create_jwt_token({'sub': 'user-123'})
print(f'Token: {token}')

payload = verify_jwt_token(token)
print(f'✅ Auth: {payload}')
"

# Test cache module
python -c "
from shared.cache import get_cache
import asyncio

async def test():
    cache = await get_cache()
    await cache.set('test_key', 'test_value')
    value = await cache.get('test_key')
    print(f'✅ Cache: {value}')

asyncio.run(test())
"

# Test EventBus client
python -c "
from shared.eventbus import EventBusClient
import asyncio

async def test():
    eb = EventBusClient()
    await eb.connect()
    await eb.publish('test.topic', {'msg': 'test'})
    print('✅ EventBus client: OK')

asyncio.run(test())
"
```

**Критерии успеха:**
- ✅ Database module работает
- ✅ Auth module работает
- ✅ Cache module работает
- ✅ EventBus client работает

---

### 3.3 Test Integrations ✅

```bash
# Test RAG Connector
python -c "
from shared.integrations.rag_connector import RAGConnector
import asyncio

async def test():
    rag = RAGConnector()
    # Test search (will be empty initially)
    results = await rag.search('test query', collection='knowledge_base')
    print(f'✅ RAG Connector: {len(results)} results')

asyncio.run(test())
"

# Test Knowledge Client
python -c "
from shared.integrations.knowledge_client import KnowledgeClient

client = KnowledgeClient()
# Test will initialize connection
print('✅ Knowledge Client: OK')
"
```

**Критерии успеха:**
- ✅ RAG Connector работает с Qdrant
- ✅ Knowledge Client инициализируется

---

## Phase 4: Platform Services

**Цель:** Запустить бизнес-сервисы (12 microservices)

**Время:** 8-10 часов

### 4.1 BIA Service ✅

```bash
cd platform-services/bia-service

# Install dependencies
pip install -r requirements.txt

# Configure environment
export DATABASE_URL=$DATABASE_URL
export REDIS_URL=$REDIS_URL
export EVENTBUS_URL=$EVENTBUS_URL

# Run migrations (if any)
alembic upgrade head

# Start service
uvicorn main:app --host 0.0.0.0 --port 8001

# Test health
curl http://localhost:8001/health

# Test API
curl http://localhost:8001/api/bia/critical-functions
```

**Критерии успеха:**
- ✅ BIA Service запущен (port 8001)
- ✅ Health check работает
- ✅ API endpoints отвечают
- ✅ Database integration работает
- ✅ EventBus integration работает

---

### 4.2 Risk Service ✅

```bash
cd platform-services/risk-service

# Install & configure
pip install -r requirements.txt
export DATABASE_URL=$DATABASE_URL

# Start service
uvicorn main:app --port 8002

# Test
curl http://localhost:8002/health
curl http://localhost:8002/api/risks
```

**Критерии успеха:**
- ✅ Risk Service запущен (port 8002)
- ✅ API endpoints работают

---

### 4.3 Compliance Service ✅

```bash
cd platform-services/compliance-service

# Setup & start
pip install -r requirements.txt
uvicorn main:app --port 8003

# Test
curl http://localhost:8003/health
curl http://localhost:8003/api/compliance/frameworks
```

**Критерии успеха:**
- ✅ Compliance Service запущен (port 8003)

---

### 4.4 Documents Service ✅

```bash
cd platform-services/documents-service

# Setup & start
pip install -r requirements.txt
uvicorn main:app --port 8004

# Test with vector search
curl -X POST http://localhost:8004/api/documents/search \
  -H "Content-Type: application/json" \
  -d '{"query": "business continuity plan"}'
```

**Критерии успеха:**
- ✅ Documents Service запущен (port 8004)
- ✅ Vector search работает с Qdrant

---

### 4.5 Remaining Services ✅

**Запустить последовательно:**

```bash
# Response Service (port 8005)
cd platform-services/response-service && uvicorn main:app --port 8005

# Validation Service (port 8006)
cd platform-services/validation-service && uvicorn main:app --port 8006

# Governance Service (port 8007)
cd platform-services/governance-service && uvicorn main:app --port 8007

# Planning Service (port 8008)
cd platform-services/planning_service && uvicorn main:app --port 8008

# Plans Service (port 8009)
cd platform-services/plans_service && uvicorn main:app --port 8009

# Learning Service (port 8010)
cd platform-services/learning-service && uvicorn main:app --port 8010

# Community Service (port 8011)
cd platform-services/community-service && uvicorn main:app --port 8011
```

**Verify all services:**
```bash
# Check all health endpoints
for port in {8001..8011}; do
  echo "Checking port $port..."
  curl http://localhost:$port/health
done
```

**Критерии успеха:**
- ✅ Все 11 platform services запущены
- ✅ Все health checks зеленые
- ✅ Service Discovery видит все сервисы

---

## Phase 5: Intelligent Core

**Цель:** Запустить AI intelligence layer

**Время:** 6-8 часов

### 5.1 Workflow Intelligence ✅

```bash
cd intelligent-core/workflow_intelligence

# Install dependencies
pip install -r requirements.txt

# Configure
export DATABASE_URL=$DATABASE_URL
export REDIS_URL=$REDIS_URL
export QDRANT_URL=$QDRANT_URL
export OPENAI_API_KEY=$OPENAI_API_KEY

# Start Workflow Engine
uvicorn main:app --port 9001

# Test workflow execution
curl -X POST http://localhost:9001/workflows/execute \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "bia_workflow",
    "context": {
      "organization_id": "org-123"
    }
  }'
```

**Критерии успеха:**
- ✅ Workflow Engine запущен
- ✅ Workflow execution работает
- ✅ AI integration работает

---

### 5.2 AI Experts ✅

```bash
cd intelligent-core/ai_experts

# Install dependencies
pip install -r requirements.txt

# Start AI Experts service
uvicorn main:app --port 9002

# Test expert query
curl -X POST http://localhost:9002/experts/query \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "bcm",
    "question": "What are the key requirements for BIA?"
  }'
```

**Критерии успеха:**
- ✅ AI Experts запущен
- ✅ Domain experts отвечают
- ✅ Knowledge base integration работает

---

### 5.3 Coordination Center ✅

```bash
cd intelligent-core/coordination-center

# Install & start
pip install -r requirements.txt
uvicorn main:app --port 8004

# Test coordination
curl -X POST http://localhost:8004/coordinate \
  -H "Content-Type: application/json" \
  -d '{
    "task": "analyze_bia",
    "context": {}
  }'
```

**Критерии успеха:**
- ✅ Coordination Center запущен
- ✅ AI → Tools посредник работает

---

### 5.4 Learning System ✅

```bash
cd intelligent-core/learning-system

# Start learning service
pip install -r requirements.txt
uvicorn main:app --port 9003

# Test learning
curl -X POST http://localhost:9003/learn \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "workflow_completed",
    "outcome": "success",
    "metrics": {...}
  }'
```

**Критерии успеха:**
- ✅ Learning System запущен
- ✅ Learning from events работает

---

### 5.5 Predictive Services ✅

```bash
cd intelligent-core/predictive

# Start predictive service
pip install -r requirements.txt
uvicorn main:app --port 9004

# Test prediction
curl -X POST http://localhost:9004/predict \
  -H "Content-Type: application/json" \
  -d '{
    "prediction_type": "risk_likelihood",
    "context": {...}
  }'
```

**Критерии успеха:**
- ✅ Predictive Services запущены
- ✅ Predictions работают

---

## Phase 6: Human Interface

**Цель:** Запустить user-facing interfaces

**Время:** 4-6 часов

### 6.1 API Gateway (Human Interface) ✅

```bash
cd human-interface/api-gateway

# Install dependencies
npm install

# Configure
cp .env.example .env
# Edit .env with backend URLs

# Start API Gateway
npm run dev

# Access
open http://localhost:3000/api/docs
```

**Критерии успеха:**
- ✅ API Gateway запущен
- ✅ GraphQL/REST endpoints работают
- ✅ Swagger/OpenAPI docs доступны

---

### 6.2 Web Application ✅

```bash
cd human-interface/web-app

# Install dependencies
npm install

# Configure
cp .env.local.example .env.local
# Edit with API URLs

# Start development server
npm run dev

# Access
open http://localhost:3001
```

**Критерии успеха:**
- ✅ Web App запущен
- ✅ Login работает
- ✅ Dashboard загружается
- ✅ API calls успешны

---

## Phase 7: Production Hardening

**Цель:** Production-ready configuration

**Время:** 8-12 часов

### 7.1 Secrets Management ✅

```bash
cd infrastructure/secrets-manager

# Start Vault
docker-compose up -d vault

# Initialize Vault
vault operator init

# Unseal Vault
vault operator unseal <key1>
vault operator unseal <key2>
vault operator unseal <key3>

# Migrate secrets from .env to Vault
python migrate_secrets.py
```

**Критерии успеха:**
- ✅ Vault запущен и unsealed
- ✅ Secrets мигрированы из .env
- ✅ Services используют Vault для secrets

---

### 7.2 SSL/TLS Configuration ✅

```bash
# Generate SSL certificates
certbot certonly --standalone -d your-domain.com

# Configure nginx
cd infrastructure/security/nginx
cp nginx.conf.example nginx.conf
# Edit with SSL paths

# Start nginx
docker-compose up -d nginx
```

**Критерии успеха:**
- ✅ SSL certificates получены
- ✅ HTTPS работает
- ✅ HTTP → HTTPS redirect настроен

---

### 7.3 Production Database Setup ✅

```bash
# Database backups
cd infrastructure/database

# Setup automated backups
crontab -e
# Add: 0 3 * * * /path/to/backup_script.sh

# Setup replication (if needed)
# Configure read replicas in Supabase dashboard
```

**Критерии успеха:**
- ✅ Automated backups настроены
- ✅ Backup restoration tested
- ✅ Replication configured (if needed)

---

### 7.4 Monitoring & Alerting ✅

```bash
cd infrastructure/monitoring

# Configure Grafana dashboards
# Import dashboards from grafana-dashboards/

# Setup alerting rules
cp prometheus/alerts.yml.example prometheus/alerts.yml
# Configure alerts

# Setup alert notifications (Slack, PagerDuty, etc.)
```

**Критерии успеха:**
- ✅ Grafana dashboards настроены
- ✅ Prometheus alerts работают
- ✅ Alert notifications доставляются

---

### 7.5 Load Balancing & Scaling ✅

```bash
# Configure load balancer
cd infrastructure/intelligent-gateway

# Setup HAProxy/nginx for load balancing
# Configure upstream servers

# Test scaling
docker-compose up -d --scale bia-service=3
```

**Критерии успеха:**
- ✅ Load balancer настроен
- ✅ Services scale горизонтально
- ✅ Health checks работают

---

### 7.6 Final Production Checklist ✅

**Security:**
- [ ] All secrets в Vault (не в .env)
- [ ] SSL/TLS enabled на всех endpoints
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] JWT rotation configured
- [ ] Database connections encrypted

**Reliability:**
- [ ] Automated backups running
- [ ] Backup restoration tested
- [ ] Health checks на всех сервисах
- [ ] Circuit breakers configured
- [ ] Retry policies настроены

**Monitoring:**
- [ ] Prometheus metrics собираются
- [ ] Grafana dashboards настроены
- [ ] Alerts configured
- [ ] Logging aggregation работает
- [ ] Distributed tracing enabled

**Performance:**
- [ ] Database indexes created
- [ ] Redis caching enabled
- [ ] CDN configured (for static assets)
- [ ] Connection pooling optimized
- [ ] Query optimization done

**Compliance:**
- [ ] Audit logging enabled
- [ ] Data retention policies configured
- [ ] GDPR compliance checked
- [ ] ISO 27001 requirements met

---

## 📊 Deployment Timeline Summary

| Phase | Task | Time | Status |
|-------|------|------|--------|
| **Phase 0** | Prerequisites | 2-3h | ⏳ |
| **Phase 1** | Foundation (DB, Redis, Qdrant) | 3-4h | ⏳ |
| **Phase 2** | Infrastructure Services | 6-8h | ⏳ |
| **Phase 3** | Shared Libraries | 2-3h | ⏳ |
| **Phase 4** | Platform Services (12) | 8-10h | ⏳ |
| **Phase 5** | Intelligent Core | 6-8h | ⏳ |
| **Phase 6** | Human Interface | 4-6h | ⏳ |
| **Phase 7** | Production Hardening | 8-12h | ⏳ |
| **TOTAL** | | **40-54h** | **~1-2 weeks** |

---

## 🚀 Quick Commands Reference

### Start Everything (Development)
```bash
# Terminal 1: Infrastructure
docker-compose up -d

# Terminal 2: EventBus
cd infrastructure/eventbus && python -m eventbus.main

# Terminal 3: API Gateway
cd infrastructure/security/api-gateway && uvicorn main:app --port 3001

# Terminal 4: Platform Services (script)
./scripts/start_all_services.sh

# Terminal 5: Intelligent Core
./scripts/start_intelligent_core.sh

# Terminal 6: Web App
cd human-interface/web-app && npm run dev
```

### Stop Everything
```bash
# Stop all Docker containers
docker-compose down

# Kill all Python services
pkill -f uvicorn

# Kill all Node services
pkill -f "npm run dev"
```

### Health Check All Services
```bash
./scripts/health_check_all.sh
```

---

## 📞 Support

**Документация:**
- [OVERVIEW.md](OVERVIEW.md) - Architecture
- [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md) - Technical details
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick reference

**Issues?**
- Check [TECHNICAL_GUIDE.md - Troubleshooting](TECHNICAL_GUIDE.md#troubleshooting)
- Review service-specific README
- Check [архив/](архив/) for historical context

---

**Last Updated:** 2025-10-06
**Version:** 1.0
