"""Coordination Center - Main FastAPI application."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from api.routes import router as coordination_router


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="Coordination Center",
        description="Посредник между Intelligent Core (AI) и Execution Engine (BCM tools)",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # В продакшене указать конкретные origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(coordination_router)

    # Prometheus metrics
    Instrumentator().instrument(app).expose(app)

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "service": "Coordination Center",
            "version": "1.0.0",
            "description": "AI → Intent → Coordination → API calls → Execution Engine",
            "docs": "/docs",
            "health": "/coordination/health",
        }

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info",
    )
