# AI Orchestrator Deployment Guide

## Prerequisites

- Python 3.10+
- PostgreSQL 14+ (Supabase)
- Redis 7+
- Docker (optional)

## Environment Setup

### 1. Environment Variables

Create `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/bcm_platform
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0

# EventBus
EVENTBUS_BACKEND=redis  # or 'memory' for development

# Logging
LOG_LEVEL=INFO

# Features
ENABLE_SAFETY=true
ENABLE_EVOLUTION=true
```

### 2. Install Dependencies

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/ai-orchestration

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup

The orchestrator will auto-create required tables on first run:
- `ai_orchestrator_memory_short_term`
- `ai_orchestrator_decisions`

No manual database setup required.

### 4. Redis Setup

Ensure Redis is running:

```bash
# Check Redis
redis-cli ping
# Should return: PONG

# Or start Redis with Docker
docker run -d -p 6379:6379 redis:7-alpine
```

## Deployment Options

### Option 1: Standalone Process

```python
import asyncio
from intelligent_core.ai_orchestration import AIOrchestrator

async def main():
    orchestrator = AIOrchestrator(
        event_bus_backend='redis',
        enable_safety=True,
        enable_evolution=True
    )
    
    await orchestrator.initialize()
    
    # Keep running
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        await orchestrator.shutdown()

if __name__ == '__main__':
    asyncio.run(main())
```

### Option 2: FastAPI Integration

```python
from fastapi import FastAPI
from intelligent_core.ai_orchestration import AIOrchestrator

app = FastAPI()
orchestrator = None

@app.on_event("startup")
async def startup():
    global orchestrator
    orchestrator = AIOrchestrator()
    await orchestrator.initialize()

@app.on_event("shutdown")
async def shutdown():
    await orchestrator.shutdown()

@app.post("/api/orchestrator/decide")
async def make_decision(situation: dict, tenant_id: str):
    decision = await orchestrator.decide(situation, tenant_id)
    return decision.to_dict()
```

### Option 3: Docker Container

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy module
COPY . .

# Set environment
ENV PYTHONUNBUFFERED=1

# Run
CMD ["python", "orchestrator_service.py"]
```

```bash
# Build
docker build -t ai-orchestrator:latest .

# Run
docker run -d \
  --name ai-orchestrator \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_HOST=redis \
  ai-orchestrator:latest
```

## Configuration

### Safety Settings

```python
# Disable safety for testing (NOT RECOMMENDED FOR PRODUCTION)
orchestrator = AIOrchestrator(enable_safety=False)

# Enable with custom thresholds (advanced)
from intelligent_core.ai_orchestration.safety import SafetyMonitor

monitor = SafetyMonitor()
# Customize thresholds here
```

### Evolution Settings

```python
# Disable evolution
orchestrator = AIOrchestrator(enable_evolution=False)

# Manual evolution trigger
result = await orchestrator.evolution_engine.run_evolution_cycle()
```

### Memory Settings

```python
# Custom memory retention
from intelligent_core.ai_orchestration.memory import ShortTermMemory

memory = ShortTermMemory()
memory.RETENTION_DAYS = 60  # Default: 30 days
```

## Monitoring

### Health Check

```python
# Check initialization
if orchestrator.initialized:
    print("Orchestrator ready")

# Get statistics
stats = orchestrator.get_stats()
print(f"Decisions made: {stats['decisions_made']}")
print(f"Safety blocks: {stats['safety_blocks']}")
```

### Logging

The orchestrator uses Python's logging framework:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Module loggers
logger = logging.getLogger('intelligent_core.ai_orchestration')
```

## Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=intelligent_core.ai_orchestration --cov-report=html

# Specific test
pytest tests/test_orchestrator.py::test_orchestrator_decide -v
```

### Quick Import Test

```bash
python test_quick.py
```

## Production Checklist

- [ ] PostgreSQL database configured and accessible
- [ ] Redis server running and accessible
- [ ] Environment variables set correctly
- [ ] Dependencies installed
- [ ] Tests passing
- [ ] Logging configured
- [ ] Monitoring in place
- [ ] Safety monitoring enabled
- [ ] Evolution enabled (if desired)
- [ ] Database tables created
- [ ] Redis connection verified

## Troubleshooting

### Import Errors

```bash
# Verify imports
python test_quick.py

# Check PYTHONPATH
export PYTHONPATH=/Users/MD/AI-Platform-ISO:$PYTHONPATH
```

### Database Connection Errors

```python
# Test database connection
from infrastructure.database.managers.supabase_client import supabase_manager

await supabase_manager.connect()
health = await supabase_manager.health_check()
print(health)
```

### Redis Connection Errors

```python
# Test Redis connection
from infrastructure.database.managers.redis_client import redis_manager

await redis_manager.connect()
is_healthy = await redis_manager.health_check()
print(f"Redis healthy: {is_healthy}")
```

### Memory Errors

```bash
# Increase memory limits
export PYTHONMAXMEMORY=2G
```

## Scaling

### Horizontal Scaling

Multiple orchestrator instances can run in parallel:
- Use EventBus consumer groups
- Each instance processes different events
- Shared Redis and PostgreSQL

### Performance Tuning

```python
# Adjust cache TTLs
from intelligent_core.ai_orchestration.memory import WorkingMemory

memory = WorkingMemory()
memory.DEFAULT_TTL = 7200  # 2 hours instead of 1

# Limit context aggregation
from intelligent_core.ai_orchestration.decision_center import ContextAggregator

aggregator = ContextAggregator()
# Customize limits here
```

## Maintenance

### Memory Cleanup

```bash
# Manual cleanup of old data
python -c "
import asyncio
from intelligent_core.ai_orchestration.memory import ShortTermMemory

async def cleanup():
    memory = ShortTermMemory()
    await memory.initialize()
    count = await memory.cleanup_old()
    print(f'Cleaned up {count} old items')

asyncio.run(cleanup())
"
```

### Evolution Cycles

```bash
# Trigger manual evolution
python -c "
import asyncio
from intelligent_core.ai_orchestration.evolution import EvolutionEngine
from intelligent_core.ai_orchestration.memory import DistributedMemory

async def evolve():
    memory = DistributedMemory()
    await memory.initialize()
    
    engine = EvolutionEngine()
    await engine.initialize(memory)
    
    result = await engine.run_evolution_cycle()
    print(result)

asyncio.run(evolve())
"
```

## Security

### Constitution Rules

The 7 constitution rules are immutable and enforced at runtime:
1. No user data modification without permission
2. No audit trail deletion
3. No production code changes without review
4. Escalate when confidence < 70%
5. No governance bypass
6. No sensitive data exposure
7. Maintain data integrity

### Access Control

Ensure proper access control to:
- PostgreSQL database
- Redis server
- Environment variables
- Deployment credentials

## Support

For issues:
1. Check logs
2. Verify environment variables
3. Test database/Redis connections
4. Run import tests
5. Check GitHub issues (if applicable)

## Upgrade Guide

When upgrading:
1. Backup database
2. Review CHANGELOG
3. Update dependencies
4. Run tests
5. Deploy to staging first
6. Monitor for issues
