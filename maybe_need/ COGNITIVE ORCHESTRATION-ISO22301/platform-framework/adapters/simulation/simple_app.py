# -*- coding: utf-8 -*-
"""
Simple Simulation Adapter - Basic Health Check
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BCM Simulation Adapter - Simple",
    description="Basic simulation adapter for BCM Platform",
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
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "simulation_adapter_simple",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "message": "Simulation adapter running - ready for enhancement"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "BCM Simulation Adapter",
        "status": "ready",
        "endpoints": ["/health", "/simulate"]
    }

@app.post("/simulate")
async def simulate_basic():
    """Basic simulation endpoint"""
    return {
        "status": "success",
        "simulation_id": "sim_basic_001",
        "message": "Basic simulation completed"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8012)