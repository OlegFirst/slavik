# BCM Platform Deployment Guide

## 🚀 Production Deployment Options

### Option 1: Standard BCM Platform
```bash
# Use main docker-compose for full feature set
docker-compose up -d
```

### Option 2: Docker AI Native Platform
```bash
# Use Docker AI enhanced version
docker-compose -f docker-compose.docker-ai.yml up -d
```

### Option 3: Production Registry Deployment
```bash
# Use registry images for enterprise deployment
docker-compose -f docker-compose.production.yml up -d
```

## 📦 Available Docker Images

All images are available at `docker.io/maxde4/seh-foundation-iso-22301:tag`

### Main Platform Images
- `latest` - Latest stable BCM platform
- `v3.0-docker-ai` - Docker AI enhanced version

### Specialized Services
- `unified-ai-latest` - Multi-service AI processor
- `pdca-assistant-latest` - PDCA cycle assistant
- `ai-orchestrator-latest` - AI coordination hub

## 🔧 Environment Configuration

### Required Environment Variables
```env
DB_PASSWORD=secure_password_here
RABBITMQ_PASSWORD=secure_rabbitmq_password
KEYCLOAK_DB_PASSWORD=secure_keycloak_password
KEYCLOAK_ADMIN_PASSWORD=secure_admin_password
KEYCLOAK_CLIENT_SECRET=secure_client_secret
```

### Optional Docker AI Configuration
```env
LOCAL_LLM_ENABLED=true
GPU_ENABLED=true
DOCKER_OFFLOAD_ENDPOINT=your_gpu_cloud_endpoint
```

## 🧪 Testing Deployment

### Quick Health Check
```bash
# Test all services
curl http://localhost:8069/web/health  # Main platform
curl http://localhost:8000/health      # AI orchestrator
curl http://localhost:8010/health      # PDCA assistant
```

### Integration Tests
```bash
# Run comprehensive tests
./tests/integration/test-docker-ai.sh
```

## 🌐 Service Endpoints

- **Main BCM Platform**: http://localhost:8069
- **AI Orchestrator**: http://localhost:8000
- **PDCA Assistant**: http://localhost:8010
- **Unified AI**: http://localhost:8090
- **Keycloak Auth**: http://localhost:8080
- **Traefik Dashboard**: http://localhost:8888

## 📊 Monitoring

- Service health checks enabled for all components
- Traefik load balancer with health monitoring
- Docker restart policies configured
- Persistent volumes for data retention

## 🔒 Security

- All sensitive data in environment variables
- Keycloak SSO integration
- Network isolation with Docker bridges
- Volume encryption recommended for production

---

**Ready for enterprise deployment! 🎉**