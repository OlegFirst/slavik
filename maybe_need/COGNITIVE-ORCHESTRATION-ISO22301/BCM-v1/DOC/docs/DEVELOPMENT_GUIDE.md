# BCM Platform - Development Environment Guide

## 🚀 Quick Start

### Essential Commands
- `dev-shortcuts` - Show all available development commands
- `health-check` - Check status of all services
- `quick-start` - Start core infrastructure (PostgreSQL + Redis)
- `make up` - Start all BCM platform services

### Development Workflow

1. **Verify Setup** (run this first):
   ```bash
   health-check
   bcm-test
   ```

2. **Start Services**:
   ```bash
   quick-start        # Start PostgreSQL + Redis
   make up           # Start all services
   ```

3. **Development**:
   ```bash
   make dev-frontend  # Vue.js development server
   make dev-backend   # Python development servers
   make logs         # View service logs
   ```

4. **Testing**:
   ```bash
   bcm-test          # Run tests
   make smoke        # Quick health check
   ```

### Space Management
```bash
cleanup-disk       # Clean all caches
space             # Check disk usage
```

### Service URLs
- Frontend: http://localhost:8081
- AI Orchestrator: http://localhost:8000/docs
- EventBus API: http://localhost:8001/docs  
- Odoo BCM: http://localhost:8069

### Troubleshooting
- Container issues: `make down && make up`
- Space issues: `cleanup-disk`
- Service issues: `health-check && make logs`

Run `dev-shortcuts` for complete command reference.
