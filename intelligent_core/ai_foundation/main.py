"""
AI Foundation Service
Port: 8040
"""

import logging
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import uvicorn

# Add shared event_bus to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.event_bus import init_event_bus, get_event_bus

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PORT = 8040
HOST = "0.0.0.0"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info(" Starting AI Foundation Service")

    # Initialize EventBus
    try:
        await init_event_bus(
            service_name="ai-foundation",
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379")
        )
        logger.info(" EventBus initialized")
    except Exception as e:
        logger.warning(f"️ EventBus init failed: {e}")

    yield

    # Shutdown
    bus = get_event_bus()
    if bus:
        await bus.close()
    logger.info(" AI Foundation Service stopped")

app = FastAPI(
    lifespan=lifespan,
    title="AI Foundation Service",
    description="Core AI capabilities (LLM, RAG, ML)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-foundation", "version": "1.0.0"}

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    return {
        "service": "AI Foundation",
        "version": "1.0.0",
        "port": PORT,
        "capabilities": ["llm", "rag", "ml", "learning"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
