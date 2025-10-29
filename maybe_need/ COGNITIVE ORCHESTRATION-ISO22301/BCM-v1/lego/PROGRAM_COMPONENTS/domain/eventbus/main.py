"""
EventBus Service - FastAPI + Redis + PostgreSQL
ISO 22301 BCM Platform Event Management
"""

from fastapi import FastAPI, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import json
import os
import redis.asyncio as redis
import asyncpg
from contextlib import asynccontextmanager
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def expand_env_vars(url_string):
    """
    Expand environment variables in a URL string.
    Handles cases where ${VAR} patterns are not properly expanded by the shell or deployment environment.
    
    This function specifically addresses the issue where POSTGRES_URL contains literal ${PGPORT}
    instead of the actual port number, which causes asyncpg to fail with:
    "ValueError: invalid literal for int() with base 10: '${PGPORT}'"
    
    Args:
        url_string (str): URL that may contain ${VAR} patterns
        
    Returns:
        str: URL with all ${VAR} patterns expanded to actual values
        
    Example:
        Input:  "postgresql://user:pass@host:${PGPORT}/db"
        Output: "postgresql://user:pass@host:5432/db"
    """
    import re
    
    # Pattern to match ${VAR} format
    pattern = r'\$\{([^}]+)\}'
    
    def replace_var(match):
        var_name = match.group(1)
        # Get the environment variable value, with some common defaults
        if var_name == 'PGPORT':
            return os.getenv(var_name, '5432')
        elif var_name == 'PGHOST':
            return os.getenv(var_name, 'localhost')
        elif var_name == 'POSTGRES_USER':
            return os.getenv(var_name, 'bcm')
        elif var_name == 'POSTGRES_PASSWORD':
            return os.getenv(var_name, 'bcm_password')
        elif var_name == 'POSTGRES_DB':
            return os.getenv(var_name, 'bcm_events')
        else:
            # For any other variable, try to get it from environment
            return os.getenv(var_name, match.group(0))  # Return original if not found
    
    # Replace all ${VAR} patterns
    expanded = re.sub(pattern, replace_var, url_string)
    return expanded

# Environment variables
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
POSTGRES_URL_RAW = os.getenv("POSTGRES_URL", "postgresql://bcm:bcm_password@localhost/bcm_events")
POSTGRES_URL = expand_env_vars(POSTGRES_URL_RAW)

# Log the expansion for debugging
if POSTGRES_URL_RAW != POSTGRES_URL:
    logger.info(f"Expanded POSTGRES_URL from '{POSTGRES_URL_RAW}' to '{POSTGRES_URL}'")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8081,http://localhost:8069").split(",")

# Global connections
redis_client = None
pg_pool = None

# Event Model with JSON Schema validation
class Event(BaseModel):
    event_type: str = Field(..., description="Event type (e.g., bcm.bia.started)", min_length=3, max_length=255)
    tenant_id: str = Field(..., description="Tenant identifier", min_length=1, max_length=255)
    data: Dict[str, Any] = Field(default={}, description="Event payload")
    user_id: Optional[str] = Field(None, description="User who triggered the event", max_length=255)
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracking", max_length=255)
    event_id: Optional[str] = Field(None, description="Idempotency key for deduplication", max_length=255)
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "bcm.bia.completed",
                "tenant_id": "tenant_001",
                "data": {"bia_id": 1, "rto": 4, "rpo": 2},
                "user_id": "user_123",
                "correlation_id": "flow_456",
                "event_id": "evt_789"
            }
        }

class EventResponse(BaseModel):
    id: int
    event_type: str
    tenant_id: str
    data: Dict[str, Any]
    user_id: Optional[str]
    correlation_id: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    status: str = "published"

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client, pg_pool
    
    # Startup
    logger.info("Starting EventBus service...")
    
    # Redis connection
    redis_client = await redis.from_url(REDIS_URL)
    logger.info("Connected to Redis")
    
    # PostgreSQL connection pool with retry
    max_retries = 10
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            pg_pool = await asyncpg.create_pool(POSTGRES_URL, min_size=2, max_size=10)
            logger.info("Connected to PostgreSQL")
            break
        except Exception as e:
            logger.warning(f"PostgreSQL connection attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt == max_retries - 1:
                logger.error("Failed to connect to PostgreSQL after all retries")
                raise
            await asyncio.sleep(retry_delay)
    
    # Create events table if not exists with idempotency support
    async with pg_pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(255) NOT NULL,
                tenant_id VARCHAR(255) NOT NULL,
                data JSONB DEFAULT '{}',
                user_id VARCHAR(255),
                correlation_id VARCHAR(255),
                event_id VARCHAR(255) UNIQUE,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50) DEFAULT 'published'
            )
        ''')
        
        # Migration: Add event_id column if it doesn't exist (for backward compatibility)
        await conn.execute('''
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'events' AND column_name = 'event_id'
                ) THEN
                    ALTER TABLE events ADD COLUMN event_id VARCHAR(255) UNIQUE;
                END IF;
            END $$;
        ''')
        
        # Create indexes
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON events(event_type)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_tenant_id ON events(tenant_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON events(created_at)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_correlation_id ON events(correlation_id)')
        await conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_event_id ON events(event_id) WHERE event_id IS NOT NULL')
    logger.info("Database schema initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down EventBus service...")
    if redis_client:
        await redis_client.close()
    if pg_pool:
        await pg_pool.close()

# Create FastAPI app
app = FastAPI(
    title="BCM EventBus Service",
    description="Event management for ISO 22301 BCM Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    try:
        # Check Redis
        await redis_client.ping()
        # Check PostgreSQL
        async with pg_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {"status": "healthy", "service": "eventbus"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Publish event with idempotency
@app.post("/api/events/publish", response_model=EventResponse)
async def publish_event(event: Event):
    try:
        # Check for idempotency if event_id provided
        if event.event_id:
            async with pg_pool.acquire() as conn:
                existing = await conn.fetchrow('''
                    SELECT id, event_type, tenant_id, data, user_id, correlation_id, metadata, created_at, status
                    FROM events WHERE event_id = $1
                ''', event.event_id)
                
                if existing:
                    # Return existing event (idempotent)
                    logger.info(f"Event {event.event_id} already exists (idempotent)")
                    return EventResponse(
                        id=existing["id"],
                        event_type=existing["event_type"],
                        tenant_id=existing["tenant_id"],
                        data=json.loads(existing["data"]) if existing["data"] else {},
                        user_id=existing["user_id"],
                        correlation_id=existing["correlation_id"],
                        metadata=json.loads(existing["metadata"]) if existing["metadata"] else {},
                        created_at=existing["created_at"],
                        status=existing["status"]
                    )
        
        # Save to PostgreSQL
        async with pg_pool.acquire() as conn:
            row = await conn.fetchrow('''
                INSERT INTO events (event_type, tenant_id, data, user_id, correlation_id, event_id, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id, created_at
            ''', event.event_type, event.tenant_id, json.dumps(event.data), 
                event.user_id, event.correlation_id, event.event_id, json.dumps(event.metadata))
        
        # Prepare full event data
        event_data = {
            "id": row["id"],
            "event_type": event.event_type,
            "tenant_id": event.tenant_id,
            "data": event.data,
            "user_id": event.user_id,
            "correlation_id": event.correlation_id,
            "metadata": event.metadata,
            "created_at": row["created_at"].isoformat(),
            "status": "published"
        }
        
        # Publish to Redis
        channel = f"bcm.{event.tenant_id}"
        await redis_client.publish(channel, json.dumps(event_data))
        
        # Also publish to event type specific channel
        await redis_client.publish(event.event_type, json.dumps(event_data))
        
        logger.info(f"Event published: {event.event_type} for tenant {event.tenant_id}")
        
        return EventResponse(
            id=row["id"],
            event_type=event.event_type,
            tenant_id=event.tenant_id,
            data=event.data,
            user_id=event.user_id,
            correlation_id=event.correlation_id,
            metadata=event.metadata,
            created_at=row["created_at"],
            status="published"
        )
    except Exception as e:
        logger.error(f"Error publishing event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get event history with enhanced filters
@app.get("/api/events/history", response_model=List[EventResponse])
async def get_event_history(
    tenant_id: Optional[str] = None,
    event_type: Optional[str] = None,
    correlation_id: Optional[str] = None,
    user_id: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
):
    try:
        # Build query dynamically
        query_parts = ["SELECT * FROM events WHERE 1=1"]
        params = []
        param_counter = 1
        
        if tenant_id:
            query_parts.append(f"AND tenant_id = ${param_counter}")
            params.append(tenant_id)
            param_counter += 1
        
        if event_type:
            query_parts.append(f"AND event_type = ${param_counter}")
            params.append(event_type)
            param_counter += 1
        
        if correlation_id:
            query_parts.append(f"AND correlation_id = ${param_counter}")
            params.append(correlation_id)
            param_counter += 1
        
        if user_id:
            query_parts.append(f"AND user_id = ${param_counter}")
            params.append(user_id)
            param_counter += 1
        
        if from_date:
            query_parts.append(f"AND created_at >= ${param_counter}")
            params.append(from_date)
            param_counter += 1
        
        if to_date:
            query_parts.append(f"AND created_at <= ${param_counter}")
            params.append(to_date)
            param_counter += 1
        
        query_parts.append(f"ORDER BY created_at DESC LIMIT ${param_counter} OFFSET ${param_counter + 1}")
        params.extend([limit, offset])
        
        query = " ".join(query_parts)
        
        async with pg_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
        
        events = []
        for row in rows:
            events.append(EventResponse(
                id=row["id"],
                event_type=row["event_type"],
                tenant_id=row["tenant_id"],
                data=json.loads(row["data"]) if row["data"] else {},
                user_id=row["user_id"],
                correlation_id=row["correlation_id"],
                metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                created_at=row["created_at"],
                status=row["status"]
            ))
        
        return events
    except Exception as e:
        logger.error(f"Error fetching event history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# SSE event stream
@app.get("/api/events/stream")
async def event_stream(request: Request, tenant_id: str):
    async def generate():
        pubsub = redis_client.pubsub()
        channel = f"bcm.{tenant_id}"
        await pubsub.subscribe(channel)
        
        try:
            while True:
                if await request.is_disconnected():
                    break
                
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and message["type"] == "message":
                    data = message["data"]
                    if isinstance(data, bytes):
                        data = data.decode("utf-8")
                    yield f"data: {data}\n\n"
                else:
                    # Send heartbeat
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
                
                await asyncio.sleep(0.1)
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
    
    return StreamingResponse(generate(), media_type="text/event-stream")

# Statistics endpoint
@app.get("/api/events/stats")
async def get_event_stats(tenant_id: str):
    try:
        async with pg_pool.acquire() as conn:
            stats = await conn.fetchrow('''
                SELECT 
                    COUNT(*) as total_events,
                    COUNT(DISTINCT event_type) as unique_event_types,
                    MIN(created_at) as first_event,
                    MAX(created_at) as last_event
                FROM events
                WHERE tenant_id = $1
            ''', tenant_id)
            
            event_types = await conn.fetch('''
                SELECT event_type, COUNT(*) as count
                FROM events
                WHERE tenant_id = $1
                GROUP BY event_type
                ORDER BY count DESC
                LIMIT 10
            ''', tenant_id)
        
        return {
            "tenant_id": tenant_id,
            "total_events": stats["total_events"],
            "unique_event_types": stats["unique_event_types"],
            "first_event": stats["first_event"].isoformat() if stats["first_event"] else None,
            "last_event": stats["last_event"].isoformat() if stats["last_event"] else None,
            "top_event_types": [
                {"type": row["event_type"], "count": row["count"]} 
                for row in event_types
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching event stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket event stream (optional alternative to SSE)
@app.websocket("/api/events/ws")
async def websocket_endpoint(websocket: WebSocket, tenant_id: str):
    await websocket.accept()
    pubsub = redis_client.pubsub()
    channel = f"bcm.{tenant_id}"
    await pubsub.subscribe(channel)
    
    try:
        while True:
            try:
                # Check for Redis messages
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.1)
                if message and message["type"] == "message":
                    data = message["data"]
                    if isinstance(data, bytes):
                        data = data.decode("utf-8")
                    await websocket.send_text(data)
                else:
                    # Send heartbeat
                    await websocket.send_json({
                        "type": "heartbeat",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                # Small delay to prevent busy loop
                await asyncio.sleep(0.5)
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for tenant {tenant_id}")
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()

# Event type registry for validation
EVENT_TYPES = {
    "bcm.bia.started": {"required_fields": ["bia_id", "process_id"]},
    "bcm.bia.completed": {"required_fields": ["bia_id", "rto", "rpo", "critical_processes"]},
    "bcm.plan.draft_requested": {"required_fields": ["plan_id", "plan_type"]},
    "bcm.plan.draft_generated": {"required_fields": ["plan_id", "ai_generated"]},
    "bcm.incident.reported": {"required_fields": ["incident_id", "severity"]},
    "bcm.incident.response_generated": {"required_fields": ["incident_id", "checklist_items"]},
    "bcm.kpi.calculated": {"required_fields": ["period", "bia_coverage", "plans_up_to_date", "capa_on_time"]},
    "bcm.exercise.completed": {"required_fields": ["exercise_id", "results"]},
    "bcm.training.completed": {"required_fields": ["training_id", "attendees"]}
}

# Validate event type and data
@app.post("/api/events/validate")
async def validate_event(event: Event):
    """Validate event structure without publishing"""
    try:
        # Check if event type is registered
        if event.event_type not in EVENT_TYPES:
            return {
                "valid": False,
                "message": f"Unknown event type: {event.event_type}",
                "known_types": list(EVENT_TYPES.keys())
            }
        
        # Check required fields
        required_fields = EVENT_TYPES[event.event_type]["required_fields"]
        missing_fields = [field for field in required_fields if field not in event.data]
        
        if missing_fields:
            return {
                "valid": False,
                "message": f"Missing required fields for {event.event_type}",
                "missing_fields": missing_fields,
                "required_fields": required_fields
            }
        
        return {
            "valid": True,
            "message": "Event structure is valid",
            "event_type": event.event_type
        }
    except Exception as e:
        logger.error(f"Error validating event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
