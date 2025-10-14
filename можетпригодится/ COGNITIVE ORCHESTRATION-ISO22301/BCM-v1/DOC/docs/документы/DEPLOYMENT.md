# MVP System Deployment Guide

## Railway Deployment Configuration

**Note:** The `railway.json` configuration has been updated to fix the "No changed files matched patterns: src/**, config/**" error. The watchPatterns now correctly monitor the actual repository structure:
- `frontend/web_portal/src/**` - Vue.js frontend source
- `backend/**`, `services/**`, `ai_services/**` - Python backend services
- `api/**`, `adapters/**` - API and integration code
- `integrations/**/config/**`, `core/**/config/**` - Configuration files

## Quick Start (Fixed Version)

```bash
# 1. Start all services
docker compose -f docker-compose.mvp.yml up -d

# 2. Wait for containers to be healthy (30-60 seconds)
docker compose ps

# 3. Create EventBus database
docker exec bcm_postgres psql -U bcm_admin -c "CREATE DATABASE IF NOT EXISTS bcm_events;"

# 4. Fix nginx config in frontend container
docker exec bcm_frontend sh -c 'cat > /etc/nginx/nginx.conf << "EOF"
events {
    worker_connections 1024;
}
http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    server {
        listen 80;
        root /usr/share/nginx/html;
        index index.html;
        location / {
            try_files $uri $uri/ /index.html;
        }
        location /api/events/ {
            proxy_pass http://bcm_eventbus:8001/api/events/;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_buffering off;
            proxy_read_timeout 86400;
        }
        location /api/events/health {
            proxy_pass http://bcm_eventbus:8001/health;
        }
        location /api/ai/ {
            proxy_pass http://bcm_orchestrator:8002/api/ai/;
        }
    }
}
EOF'

# 5. Reload nginx
docker exec bcm_frontend nginx -s reload
```

## Services Status
- **EventBus**: http://localhost:8001 ✅
- **Orchestrator**: http://localhost:8002 ✅  
- **Frontend**: http://localhost:8081 ✅
- **Odoo**: http://localhost:8069 ✅
- **PostgreSQL**: localhost:5432 ✅
- **Redis**: localhost:6379 ✅

## Known Issues & Fixes Applied

### 1. Missing OdooView.vue Component
**Fixed**: Created `/frontend/web_portal/src/components/OdooView.vue`

### 2. PostgreSQL Init Script
**Fixed**: Created `/database/init-postgres.sh` with proper permissions

### 3. Frontend Nginx Configuration
**Fixed**: Updated nginx.conf with correct service names and proxy settings

### 4. EventBus Database Missing
**Fixed**: Created `bcm_events` database manually

## API Testing
```bash
# Test EventBus
curl http://localhost:8001/health

# Test through Frontend
curl http://localhost:8081/api/events/health

# Publish test event
curl -X POST http://localhost:8001/api/events/publish \
  -H "Content-Type: application/json" \
  -d '{"event_type":"bcm.test","tenant_id":"demo","data":{"test":true}}'

# Check Orchestrator decisions
curl "http://localhost:8002/api/ai/decisions/pending?tenant_id=demo"
```

## Architecture Overview
```
Frontend (8081) → nginx → 
  ├── EventBus (8001) → PostgreSQL
  ├── Orchestrator (8002) → PostgreSQL  
  └── Odoo (8069) → PostgreSQL

Redis (6379) ← All services
```

## Deployment Notes
- All services run in Docker network `iso-22301_bcm_network`
- Frontend uses nginx proxy to route API calls to microservices
- PostgreSQL stores events and AI decisions
- Redis handles caching and pub/sub

## Troubleshooting
If frontend shows white page:
1. Check browser console for JS errors
2. Verify API endpoints return data
3. Check nginx proxy configuration
4. Restart frontend container if needed

For Vercel deployment, use static build in `/frontend/web_portal/dist/`
