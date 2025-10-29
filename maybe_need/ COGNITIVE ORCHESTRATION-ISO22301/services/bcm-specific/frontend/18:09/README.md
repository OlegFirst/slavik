# BCM Platform Launch Guide

## Quick Start

### Prerequisites
- Node.js 18+ 
- npm 9+
- Docker & Docker Compose

### Launch Options

#### 🚀 Easy Launch (Recommended)
```bash
cd /Users/MD/ISO-22301
chmod +x launch-bcm-platform.sh
./launch-bcm-platform.sh
```

Then select your preferred option:
1. **User Platform Only** - Business users interface (port 5173)
2. **Admin Panel Only** - System administration (port 3001)  
3. **Both Platforms** - Complete frontend experience
4. **Backend Services** - Start Docker services only
5. **Full Stack** - Complete system with all services

### Manual Launch

#### User Platform
```bash
cd /Users/MD/ISO-22301/frontend/web_portal_enhanced
chmod +x start-user-platform.sh
./start-user-platform.sh
```

#### Admin Panel  
```bash
cd /Users/MD/ISO-22301/frontend/admin_panel
npm install
npm run dev
```

#### Backend Services
```bash
cd /Users/MD/ISO-22301
docker-compose up -d
```

## Platform Overview

### User Platform (Port 5173)
**Target Users**: Business users, BCM teams, department heads
**Features**:
- Real-time BCM Dashboard with AI insights
- 25 BCM modules (Risk Assessment, BCP Development, etc.)
- AI-powered business continuity management
- Live activity feed and notifications
- Interactive BCM workflow tools

**Key Modules**:
- Risk Assessment & Analysis
- Business Impact Analysis (BIA)
- Business Continuity Plan (BCP) Development
- Incident Management & Response
- Crisis Management Center
- BCM Training & Exercises
- Compliance & Audit Management
- Recovery Planning & Testing

### Admin Panel (Port 3001)  
**Target Users**: System administrators, DevOps, IT teams
**Features**:
- AI Organisms monitoring (10 digital BCM organs)
- System health & performance metrics
- Service management & control
- Real-time monitoring integration
- MCP server status & tools
- Platform configuration & settings

## Service Architecture

### Frontend Services
- **User Platform**: Vue.js 3 + TypeScript + Tailwind CSS (Port 5173)
- **Admin Panel**: React + TypeScript + Tailwind CSS (Port 3001)

### Backend Services (Docker)
- **BCM Core (Odoo)**: Main business logic (Port 8069)
- **AI Orchestrator**: AI system coordination (Port 8000)
- **BIA Engine**: Business impact analysis (Port 8082) 
- **Document Processor**: File processing (Port 8083)
- **EventBus**: Real-time events (Port 8001)
- **Community Service**: Collaboration (Port 8084)

### Monitoring Stack
- **Grafana**: Dashboards & visualization (Port 3000)
- **Prometheus**: Metrics collection (Port 9090)
- **AlertManager**: Alert management (Port 9093)

### Databases
- **PostgreSQL**: Main database (Port 5432)
- **Redis**: Caching & sessions (Port 6379)
- **Supabase**: External data & auth

## Data Flow

### Real-time Data Integration
The platform automatically detects available services and adapts:

**Full Integration** (All services running):
- Live metrics from Prometheus
- Real BCM data from Odoo core
- AI insights from orchestrator
- Real-time events via WebSocket

**Partial Integration** (Some services available):
- Mixed real/mock data
- Graceful degradation
- Service health indicators

**Offline Mode** (No backend services):
- Enhanced mock data
- Full UI functionality
- Development-ready experience

### API Endpoints
- **Health Checks**: `/health` on each service
- **Metrics**: `/api/v1/metrics/*`  
- **BCM Data**: `/api/v1/bcm/*`
- **AI Services**: `/api/v1/ai/*`
- **Real-time**: WebSocket on port 8001

## Development Features

### Hot Reload & Live Updates
- Frontend changes reflect immediately
- Backend API changes detected automatically
- Real-time data refresh (30-second intervals)
- WebSocket live updates when available

### Debug & Development Tools
- API request/response logging
- Service health monitoring
- Mock data fallbacks
- Browser DevTools integration
- TypeScript type checking

### Environment Configuration
Both platforms use `.env` files for configuration:
- API endpoints
- Feature flags  
- Service timeouts
- Debug settings
- Real-time update intervals

## Troubleshooting

### Common Issues

**Port Already in Use**:
```bash
# Kill processes on specific ports
lsof -ti:5173 | xargs kill -9  # User platform
lsof -ti:3001 | xargs kill -9  # Admin panel
```

**Services Not Starting**:
```bash
# Check Docker status
docker-compose ps
docker-compose logs [service-name]

# Restart specific service
docker-compose restart [service-name]
```

**API Connection Issues**:
- Check service health: `curl http://localhost:8000/health`
- Verify .env configuration
- Check browser console for CORS errors
- Ensure services started in correct order

**Dependencies Issues**:
```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Platform URLs Quick Reference

| Service | URL | Purpose |
|---------|-----|---------|
| User Platform | http://localhost:5173 | Main business interface |
| Admin Panel | http://localhost:3001 | System administration |
| BCM Core | http://localhost:8069 | Business logic & data |
| AI Orchestrator | http://localhost:8000 | AI system control |
| Grafana | http://localhost:3000 | Monitoring dashboards |
| Prometheus | http://localhost:9090 | Metrics collection |

### Logs & Monitoring
- **Frontend logs**: Browser DevTools Console
- **Backend logs**: `docker-compose logs -f [service]`
- **Admin panel logs**: `tail -f admin.log`
- **System metrics**: Grafana dashboards
- **Health checks**: Built into both platforms

## Next Steps

After launching the platform:

1. **Explore User Platform**: Navigate to http://localhost:5173
   - Review the enhanced dashboard with real-time data
   - Test BCM modules and AI integration
   - Check activity feed and notifications

2. **Monitor System Health**: Visit http://localhost:3001  
   - Check AI organisms status
   - Monitor system metrics
   - Review service health

3. **Configure & Customize**:
   - Adjust .env settings for your environment
   - Configure API endpoints if services run elsewhere  
   - Set up monitoring alerts and thresholds

The platform automatically adapts to available services, so you can start with just frontend development and add backend services as needed.
