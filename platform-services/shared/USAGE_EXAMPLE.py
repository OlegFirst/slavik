"""
Example usage of shared utilities for platform services

This file demonstrates how to integrate the shared logging and health check
utilities into your service.
"""

from fastapi import FastAPI
from shared import setup_logging, comprehensive_healthcheck
import asyncio

# ============================================================================
# EXAMPLE 1: Setup Logging
# ============================================================================

# Basic setup with INFO level
logger = setup_logging("example-service", "INFO")

# With DEBUG level for development
# logger = setup_logging("example-service", "DEBUG")

# Usage
logger.info("Service initialized")
logger.debug("Debugging information")
logger.warning("Warning message")
logger.error("Error occurred")


# ============================================================================
# EXAMPLE 2: Health Check with All Dependencies
# ============================================================================

app = FastAPI()


# Define your dependency check functions
async def check_db_connection():
    """Check database connectivity"""
    # Example: await db.execute("SELECT 1")
    # Raise exception if check fails
    await asyncio.sleep(0.1)  # Simulate DB check
    # If connection fails, raise exception:
    # raise ConnectionError("Database connection failed")


async def check_redis_connection():
    """Check Redis connectivity"""
    # Example: await redis.ping()
    await asyncio.sleep(0.1)  # Simulate Redis check
    # If connection fails, raise exception:
    # raise ConnectionError("Redis connection failed")


async def check_qdrant_connection():
    """Check Qdrant connectivity"""
    # Example: await qdrant_client.get_collections()
    await asyncio.sleep(0.1)  # Simulate Qdrant check


@app.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint

    Returns:
        - status: healthy/degraded/unhealthy
        - timestamp: ISO timestamp
        - service: service name
        - checks: individual check results
    """
    return await comprehensive_healthcheck(
        db_check=check_db_connection,
        redis_check=check_redis_connection,
        qdrant_check=check_qdrant_connection,
        service_name="example-service"
    )


# ============================================================================
# EXAMPLE 3: Simple Health Check (No Dependencies)
# ============================================================================

from shared.healthcheck import simple_healthcheck


@app.get("/health/simple")
async def simple_health():
    """Simple health check without dependency checks"""
    return await simple_healthcheck(service_name="example-service")


# ============================================================================
# EXAMPLE 4: Check Individual Dependency
# ============================================================================

from shared.healthcheck import check_dependency


@app.get("/health/database")
async def database_health():
    """Check only database health"""
    return await check_dependency(
        check_func=check_db_connection,
        dependency_name="postgresql",
        timeout=5.0
    )


# ============================================================================
# EXAMPLE 5: Service Lifecycle Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Service startup"""
    logger.info("=== Example Service Starting ===")
    logger.info("Initializing database connections...")
    logger.info("Initializing Redis connections...")
    logger.info("Service ready to accept requests")


@app.on_event("shutdown")
async def shutdown_event():
    """Service shutdown"""
    logger.info("=== Example Service Shutting Down ===")
    logger.info("Closing database connections...")
    logger.info("Closing Redis connections...")
    logger.info("Shutdown complete")


# ============================================================================
# EXAMPLE 6: With File Logging (Optional)
# ============================================================================

from shared.logging_config import setup_file_logging

# Setup logging with file output
logger_with_file = setup_file_logging(
    service_name="example-service",
    log_level="INFO",
    log_file="/var/log/example-service.log"
)

logger_with_file.info("This will be logged to both console and file")


# ============================================================================
# EXAMPLE 7: Error Handling in Endpoints
# ============================================================================

@app.get("/api/example")
async def example_endpoint():
    """Example endpoint with proper logging"""
    try:
        logger.info("Processing request")
        # Your business logic here
        result = {"status": "success"}
        logger.info("Request processed successfully")
        return result
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise


# ============================================================================
# EXAMPLE 8: Running the Service
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Example Service on port 8000")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


# ============================================================================
# EXPECTED OUTPUT EXAMPLES
# ============================================================================

"""
Logging Output:
---------------
2025-10-08 09:36:45,123 - example-service - __main__ - INFO - Service initialized
2025-10-08 09:36:45,124 - example-service - __main__ - INFO - === Example Service Starting ===
2025-10-08 09:36:45,125 - example-service - __main__ - INFO - Service ready to accept requests

Health Check Response (Healthy):
---------------------------------
{
  "status": "healthy",
  "timestamp": "2025-10-08T09:36:45.123456",
  "service": "example-service",
  "checks": {
    "database": {
      "status": "ok",
      "critical": true
    },
    "redis": {
      "status": "ok",
      "critical": false
    },
    "qdrant": {
      "status": "ok",
      "critical": false
    }
  }
}

Health Check Response (Degraded - Redis Down):
-----------------------------------------------
{
  "status": "degraded",
  "timestamp": "2025-10-08T09:36:45.123456",
  "service": "example-service",
  "checks": {
    "database": {
      "status": "ok",
      "critical": true
    },
    "redis": {
      "status": "error",
      "error": "Redis connection failed",
      "critical": false
    },
    "qdrant": {
      "status": "ok",
      "critical": false
    }
  }
}

Health Check Response (Unhealthy - Database Down):
---------------------------------------------------
{
  "status": "unhealthy",
  "timestamp": "2025-10-08T09:36:45.123456",
  "service": "example-service",
  "checks": {
    "database": {
      "status": "error",
      "error": "Database connection failed",
      "critical": true
    },
    "redis": {
      "status": "ok",
      "critical": false
    },
    "qdrant": {
      "status": "ok",
      "critical": false
    }
  }
}
"""
