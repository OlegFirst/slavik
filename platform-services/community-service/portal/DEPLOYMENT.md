# Portal Service - Deployment Guide

## 📋 Prerequisites

- PostgreSQL 15+ running
- Docker (optional, for containerized deployment)
- Python 3.11+ (for local development)

---

## 🗄️ Database Setup

### 1. Apply Migrations

**Using the migration script:**

```bash
cd /Users/MD/ISO-22301—копия/services/SERVICES/COMMUNITY/portal

# Set database credentials (optional, defaults shown)
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=bcm_platform
export DB_USER=bcm_user
export DB_PASSWORD=bcm_password

# Run migrations
./scripts/apply_migrations.sh
```

**Or manually with psql:**

```bash
export PGPASSWORD=bcm_password

psql -h localhost -U bcm_user -d bcm_platform -f database/migrations/001_initial_portal_schema.sql
psql -h localhost -U bcm_user -d bcm_platform -f database/migrations/002_add_scenarios.sql
psql -h localhost -U bcm_user -d bcm_platform -f database/migrations/003_add_forum.sql
```

**Or using Docker exec:**

```bash
docker exec -i bcm-postgres psql -U bcm_user -d bcm_platform < database/migrations/001_initial_portal_schema.sql
docker exec -i bcm-postgres psql -U bcm_user -d bcm_platform < database/migrations/002_add_scenarios.sql
docker exec -i bcm-postgres psql -U bcm_user -d bcm_platform < database/migrations/003_add_forum.sql
```

### 2. Verify Schema

```bash
export PGPASSWORD=bcm_password
psql -h localhost -U bcm_user -d bcm_platform -c "\dt portal.*"
```

Expected output:
```
                  List of relations
 Schema |         Name          | Type  |   Owner
--------+-----------------------+-------+-----------
 portal | article_bookmarks     | table | bcm_user
 portal | article_votes         | table | bcm_user
 portal | badges                | table | bcm_user
 portal | forum_categories      | table | bcm_user
 portal | forum_posts           | table | bcm_user
 portal | forum_topics          | table | bcm_user
 portal | knowledge_articles    | table | bcm_user
 portal | moderation_flags      | table | bcm_user
 portal | post_votes            | table | bcm_user
 portal | reputation_events     | table | bcm_user
 portal | scenario_reviews      | table | bcm_user
 portal | scenarios             | table | bcm_user
 portal | topic_votes           | table | bcm_user
 portal | user_badges           | table | bcm_user
 portal | user_reputation       | table | bcm_user
```

---

## 🚀 Deployment Options

### Option 1: Docker (Recommended)

```bash
cd /Users/MD/ISO-22301—копия/services/SERVICES/COMMUNITY/portal

# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f portal

# Check health
curl http://localhost:8031/health
```

### Option 2: Local Development

```bash
cd /Users/MD/ISO-22301—копия/services/SERVICES/COMMUNITY/portal

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql+asyncpg://bcm_user:bcm_password@localhost:5432/bcm_platform
export CLIENTS_SERVICE_URL=http://localhost:8030
export VALIDATION_SERVICE_URL=http://localhost:8022
export AI_ORCHESTRATOR_URL=http://localhost:8000
export PORT=8031
export DEBUG=true

# Run service
uvicorn main:app --host 0.0.0.0 --port 8031 --reload
```

### Option 3: Production (with Platform)

See Platform Integration section below.

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://bcm_user:bcm_password@localhost:5432/bcm_platform

# Service URLs
CLIENTS_SERVICE_URL=http://localhost:8030
VALIDATION_SERVICE_URL=http://localhost:8022
AI_ORCHESTRATOR_URL=http://localhost:8000

# Server
PORT=8031
DEBUG=true

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Logging
LOG_LEVEL=INFO
```

---

## 🧪 Testing Deployment

### 1. Health Check

```bash
curl http://localhost:8031/health
```

Expected response:
```json
{
  "service": "portal",
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. API Documentation

Open in browser:
- Swagger UI: http://localhost:8031/docs
- ReDoc: http://localhost:8031/redoc

### 3. Test Endpoints

**Get forum categories:**
```bash
curl http://localhost:8031/api/portal/forum/categories
```

**Get knowledge articles:**
```bash
curl http://localhost:8031/api/portal/knowledge/articles
```

**Get scenarios:**
```bash
curl http://localhost:8031/api/portal/scenarios
```

---

## 🌐 Platform Integration

### ✅ Gateway Integration Complete

Portal Service is **fully integrated** with the Platform Gateway (Port 8000).

**Gateway Routing:**

Portal endpoints are accessible through Gateway at:
- `http://gateway:8000/api/community/portal/knowledge/*`
- `http://gateway:8000/api/community/portal/scenarios/*`
- `http://gateway:8000/api/community/portal/forum/*`

**Service Registry:**

Portal is registered in `/PLATFORM/gateway/main.py`:
```python
"portal": {
    "url": os.getenv("PORTAL_URL", "http://localhost:8031"),
    "health": "/health",
    "prefix": "/api/community/portal"
}
```

**EventBus Integration:**

Portal emits events for all activities (articles, scenarios, forum, gamification).
See: [PLATFORM_INTEGRATION.md](./PLATFORM_INTEGRATION.md)

**Full Platform Deployment:**

```bash
cd /Users/MD/ISO-22301—копия/services/SERVICES/PLATFORM

# Start entire Platform (Gateway, EventBus, Portal, Clients, Database)
docker-compose -f docker-compose.platform.yml up -d

# Check all services
curl http://localhost:8000/api/services
```

📖 **Complete Integration Guide:** [PLATFORM_INTEGRATION.md](./PLATFORM_INTEGRATION.md)

---

## 📊 Monitoring

### Logs

```bash
# Docker
docker-compose logs -f portal

# Local
tail -f logs/portal.log
```

### Metrics

Portal service exposes standard FastAPI metrics that can be scraped by Prometheus.

### Database Monitoring

```bash
# Check table sizes
export PGPASSWORD=bcm_password
psql -h localhost -U bcm_user -d bcm_platform -c "
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'portal'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

---

## 🔄 Rollback

If you need to rollback migrations:

```bash
# Rollback scripts are in migration files as comments
# Example for forum:
export PGPASSWORD=bcm_password
psql -h localhost -U bcm_user -d bcm_platform << 'EOF'
-- Drop tables in reverse order
DROP TABLE IF EXISTS portal.reputation_events CASCADE;
DROP TABLE IF EXISTS portal.user_badges CASCADE;
DROP TABLE IF EXISTS portal.badges CASCADE;
-- ... (see 003_add_forum.sql rollback section)
EOF
```

---

## 🐛 Troubleshooting

### Issue: Cannot connect to database

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check connection
export PGPASSWORD=bcm_password
psql -h localhost -U bcm_user -d bcm_platform -c "SELECT 1"
```

### Issue: Migration fails

```bash
# Check if schema exists
export PGPASSWORD=bcm_password
psql -h localhost -U bcm_user -d bcm_platform -c "\dn"

# Check if tables already exist
psql -h localhost -U bcm_user -d bcm_platform -c "\dt portal.*"
```

### Issue: Service won't start

```bash
# Check logs
docker-compose logs portal

# Check port is not in use
lsof -i :8031

# Verify dependencies are installed
pip list | grep fastapi
```

---

## 📚 Next Steps

1. ✅ Apply database migrations
2. ✅ Start Portal service
3. ✅ Verify health check
4. → Integrate with Platform Gateway
5. → Configure EventBus for Portal events
6. → Setup monitoring and alerts

**Ready for Platform Integration!** 🚀
