# Quick Start Guide - Shared Utilities

## 5-Minute Integration

### 1. Install Development Dependencies

```bash
cd /Users/MD/AI-Platform-ISO/platform-services/your-service
pip install -r requirements-dev.txt
```

### 2. Update Your Service

```python
# your-service/main.py
from fastapi import FastAPI
from shared import setup_logging, comprehensive_healthcheck

# Setup logging (do this FIRST)
logger = setup_logging("your-service", "INFO")

app = FastAPI()

# Add health check
@app.get("/health")
async def health():
    return await comprehensive_healthcheck(
        db_check=check_db,          # Your DB check function
        redis_check=check_redis,    # Your Redis check function (optional)
        service_name="your-service"
    )

# Use logging in startup
@app.on_event("startup")
async def startup():
    logger.info("Service starting up...")

# Use logging in endpoints
@app.get("/api/endpoint")
async def endpoint():
    logger.info("Processing request")
    # Your code here
    return {"status": "ok"}
```

### 3. Test It

```bash
# Start your service
python main.py

# Test health check
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2025-10-08T...",
#   "service": "your-service",
#   "checks": {...}
# }
```

## Common Patterns

### Pattern 1: Database Check

```python
async def check_db():
    """Check database connectivity"""
    try:
        await db.execute("SELECT 1")
    except Exception as e:
        raise ConnectionError(f"Database check failed: {e}")
```

### Pattern 2: Redis Check

```python
async def check_redis():
    """Check Redis connectivity"""
    try:
        await redis.ping()
    except Exception as e:
        raise ConnectionError(f"Redis check failed: {e}")
```

### Pattern 3: Qdrant Check

```python
async def check_qdrant():
    """Check Qdrant connectivity"""
    try:
        await qdrant_client.get_collections()
    except Exception as e:
        raise ConnectionError(f"Qdrant check failed: {e}")
```

### Pattern 4: Logging at Different Levels

```python
logger.debug("Detailed debugging info")      # Development only
logger.info("Normal operations")             # General info
logger.warning("Something unusual")          # Potential issues
logger.error("Error occurred")               # Errors
logger.critical("Critical failure")          # Critical issues
```

## Development Workflow

```bash
# 1. Install dev dependencies
pip install -r requirements-dev.txt

# 2. Format code
black .

# 3. Lint code
ruff check .

# 4. Type check
mypy .

# 5. Security scan
bandit -r . -ll

# 6. Run tests
pytest --cov=.

# 7. Generate coverage report
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

## Troubleshooting

### Import Error?

```python
# Make sure you're in platform-services directory
import sys
sys.path.insert(0, '/Users/MD/AI-Platform-ISO/platform-services')
from shared import setup_logging
```

### Health Check Returns Unhealthy?

Check logs for specific error:
```python
logger.error(f"Health check failed: {error}")
```

### Need File Logging?

```python
from shared.logging_config import setup_file_logging

logger = setup_file_logging(
    service_name="your-service",
    log_level="INFO",
    log_file="/var/log/your-service.log"
)
```

## Cheat Sheet

| Task | Command |
|------|---------|
| Setup logging | `logger = setup_logging("service", "INFO")` |
| Health check | `await comprehensive_healthcheck(...)` |
| Simple health | `await simple_healthcheck("service")` |
| Format code | `black .` |
| Lint | `ruff check .` |
| Type check | `mypy .` |
| Test | `pytest` |
| Coverage | `pytest --cov=.` |

## Next Steps

1. ✅ Install development dependencies
2. ✅ Add logging to your service
3. ✅ Implement health check endpoint
4. ✅ Run code quality checks
5. ✅ Write tests
6. ✅ Document your API

## Full Documentation

- **Usage Examples:** See `USAGE_EXAMPLE.py`
- **Detailed Guide:** See `README.md`
- **Implementation Report:** See `../DEV_INFRASTRUCTURE_COMPLETE.md`

---

**Time to integrate:** ~5 minutes
**Difficulty:** Easy
**Status:** Production Ready
