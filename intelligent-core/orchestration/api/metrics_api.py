"""
Metrics API (Phase 1 - Task 1.5)
=================================

Exposes Prometheus metrics via HTTP endpoint.

Features:
- Prometheus scrape endpoint (/metrics)
- Human-readable summary (/metrics/summary)
- Health check (/health)

Port: 9091 (as per PORT_MAP_FOR_PHASE1.md)

Usage:
    ```bash
    # Run standalone
    python -m intelligent_core.orchestration.api.metrics_api

    # Access metrics
    curl http://localhost:9091/metrics        # Prometheus format
    curl http://localhost:9091/metrics/summary  # JSON summary
    curl http://localhost:9091/health          # Health check
    ```

Prometheus Configuration:
    ```yaml
    scrape_configs:
      - job_name: 'metrics-api'
        static_configs:
          - targets: ['localhost:9091']
        metrics_path: '/metrics'
    ```
"""

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, REGISTRY
import logging
import time
from datetime import datetime

# Import metrics from orchestrator
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from intelligent_core.orchestration.ai_orchestration.monitoring.metrics import orchestrator_metrics
except ImportError:
    orchestrator_metrics = None
    logging.warning("Could not import orchestrator_metrics - some metrics may not be available")

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Metrics API",
    description="Prometheus metrics endpoint for AI Platform infrastructure",
    version="1.0.0"
)

# Track start time
START_TIME = time.time()


@app.get("/metrics")
def prometheus_metrics():
    """
    Prometheus scrape endpoint

    Returns all registered Prometheus metrics in Prometheus exposition format.

    Example:
        ```bash
        curl http://localhost:9091/metrics
        ```

    Returns:
        Response: Prometheus metrics in text format
    """
    return Response(
        generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/metrics/summary")
async def metrics_summary():
    """
    Human-readable metrics summary

    Returns a JSON summary of key metrics for easier consumption.

    Example:
        ```bash
        curl http://localhost:9091/metrics/summary | jq
        ```

    Returns:
        JSONResponse: Summary of key metrics
    """
    uptime_seconds = time.time() - START_TIME

    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_hours": round(uptime_seconds / 3600, 2),
        "system": {
            "uptime_seconds": uptime_seconds,
            "metrics_endpoint": "/metrics",
            "health_endpoint": "/health"
        }
    }

    # Add orchestrator metrics if available
    if orchestrator_metrics:
        try:
            # Try to get key metrics from orchestrator
            summary["orchestrator"] = {
                "note": "Orchestrator metrics available at /metrics endpoint"
            }
        except Exception as e:
            logger.error(f"Error getting orchestrator metrics: {e}")

    return JSONResponse(content=summary)


@app.get("/health")
def health():
    """
    Health check endpoint

    Returns the health status of the Metrics API service.

    Example:
        ```bash
        curl http://localhost:9091/health
        ```

    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "service": "metrics_api",
        "port": 9091,
        "uptime_seconds": time.time() - START_TIME,
        "endpoints": {
            "metrics": "/metrics",
            "summary": "/metrics/summary",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/")
def root():
    """
    Root endpoint - redirects to docs

    Returns:
        dict: Service information
    """
    return {
        "service": "Metrics API",
        "version": "1.0.0",
        "phase": "Phase 1 - Infrastructure Integration",
        "endpoints": {
            "metrics": "GET /metrics - Prometheus metrics",
            "summary": "GET /metrics/summary - Human-readable summary",
            "health": "GET /health - Health check",
            "docs": "GET /docs - API documentation"
        },
        "prometheus_config": {
            "job_name": "metrics-api",
            "targets": ["localhost:9091"],
            "metrics_path": "/metrics"
        }
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("=" * 70)
    logger.info("Starting Metrics API (Phase 1)")
    logger.info("=" * 70)
    logger.info("Port: 9091")
    logger.info("Endpoints:")
    logger.info("  - GET /metrics        - Prometheus metrics")
    logger.info("  - GET /metrics/summary - JSON summary")
    logger.info("  - GET /health          - Health check")
    logger.info("  - GET /docs            - API documentation")
    logger.info("=" * 70)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9091,
        log_level="info"
    )
