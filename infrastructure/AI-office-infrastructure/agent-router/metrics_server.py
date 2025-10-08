"""
Prometheus Metrics Server для AI Agent Router

Standalone HTTP сервер для экспорта метрик.
Можно запустить отдельно или интегрировать в существующий сервис.
"""

import asyncio
import logging
from fastapi import FastAPI
from prometheus_client import make_asgi_app
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management"""
    logger.info("🚀 Metrics server starting...")
    yield
    logger.info("👋 Metrics server shutting down...")


# FastAPI app
app = FastAPI(
    title="AI Agent Router Metrics",
    description="Prometheus metrics for AI Agent Router",
    version="2.0.0",
    lifespan=lifespan
)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-agent-router-metrics",
        "version": "2.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Agent Router Metrics Server",
        "version": "2.0.0",
        "endpoints": {
            "/metrics": "Prometheus metrics (scrape here)",
            "/health": "Health check"
        }
    }


def run_server(host: str = "0.0.0.0", port: int = 9090):
    """
    Run metrics server

    Args:
        host: Host to bind to
        port: Port to bind to
    """
    import uvicorn

    logger.info(f"Starting metrics server on {host}:{port}")
    logger.info(f"Metrics available at http://{host}:{port}/metrics")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    # Run standalone
    run_server(host="0.0.0.0", port=9090)
