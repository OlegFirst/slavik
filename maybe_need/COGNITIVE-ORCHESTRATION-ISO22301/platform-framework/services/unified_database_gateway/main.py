#!/usr/bin/env python3
"""
Centralized Database Gateway for BCM Platform
Единая точка доступа ко всем базам данных: PostgreSQL, Redis, MongoDB, RabbitMQ, Supabase
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import asyncpg
import redis.asyncio as redis
import motor.motor_asyncio
import aio_pika
from supabase import create_client, Client
import httpx
import os
import json
import time
from datetime import datetime
import logging
import hashlib
import secrets

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("unified_db_gateway")

app = FastAPI(
    title="BCM Unified Database Gateway",
    description="Centralized access point for all BCM databases",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Database configurations
class DatabaseConfig:
    # Odoo Database - главная база данных платформы
    ODOO_DB_URL = os.getenv("ODOO_DB_URL", "postgresql://odoo:postgres123@postgres:5432/bcm_platform")
    ODOO_API_URL = os.getenv("ODOO_API_URL", "http://odoo:8069")
    ODOO_DB_NAME = os.getenv("ODOO_DB_NAME", "bcm_platform")

    # Дополнительные базы данных
    POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://odoo:postgres123@postgres:5432/bcm_platform")
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://mongodb:27017")
    RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://bcm:bcm123@rabbitmq:5672/")
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Request/Response models
class DatabaseOperation(BaseModel):
    database: str  # postgres, redis, mongodb, rabbitmq, supabase, odoo
    operation: str  # select, insert, update, delete, cache_get, cache_set, publish, subscribe, odoo_search, odoo_create, odoo_write, odoo_read
    table: Optional[str] = None
    collection: Optional[str] = None
    key: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    where: Optional[Dict[str, Any]] = None
    tenant_id: Optional[str] = None
    ttl: Optional[int] = None
    # Odoo-specific fields
    model: Optional[str] = None  # Odoo model name
    domain: Optional[List] = None  # Odoo domain filter
    ids: Optional[List[int]] = None  # Odoo record IDs
    fields: Optional[List[str]] = None  # Fields to read/write
    context: Optional[Dict[str, Any]] = None  # Odoo context

class OdooAuthRequest(BaseModel):
    username: str
    password: str
    database: Optional[str] = None

class OdooAuthResponse(BaseModel):
    user_id: int
    session_id: str
    user_context: Dict[str, Any]
    company_id: int
    partner_id: int

class HealthStatus(BaseModel):
    database: str
    status: str  # online, offline, degraded
    response_time: Optional[float] = None
    error: Optional[str] = None
    last_checked: datetime

# Connection managers
class DatabaseConnections:
    def __init__(self):
        self.postgres_pool = None
        self.odoo_postgres_pool = None
        self.redis_client = None
        self.mongo_client = None
        self.mongo_db = None
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None
        self.supabase_client = None
        self.odoo_sessions = {}  # Store active Odoo sessions

    async def initialize(self):
        """Initialize all database connections"""
        try:
            # PostgreSQL (дополнительная)
            self.postgres_pool = await asyncpg.create_pool(DatabaseConfig.POSTGRES_URL)
            logger.info("✅ PostgreSQL connected")

            # Odoo PostgreSQL (главная база)
            self.odoo_postgres_pool = await asyncpg.create_pool(DatabaseConfig.ODOO_DB_URL)
            logger.info("✅ Odoo PostgreSQL connected")

            # Redis
            self.redis_client = redis.from_url(DatabaseConfig.REDIS_URL)
            await self.redis_client.ping()
            logger.info("✅ Redis connected")

            # MongoDB
            if DatabaseConfig.MONGODB_URL:
                self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(DatabaseConfig.MONGODB_URL)
                self.mongo_db = self.mongo_client.bcm_documents
                logger.info("✅ MongoDB connected")

            # RabbitMQ
            self.rabbitmq_connection = await aio_pika.connect_robust(DatabaseConfig.RABBITMQ_URL)
            self.rabbitmq_channel = await self.rabbitmq_connection.channel()
            logger.info("✅ RabbitMQ connected")

            # Supabase
            if DatabaseConfig.SUPABASE_URL and DatabaseConfig.SUPABASE_KEY:
                self.supabase_client = create_client(DatabaseConfig.SUPABASE_URL, DatabaseConfig.SUPABASE_KEY)
                logger.info("✅ Supabase connected")

        except Exception as e:
            logger.error(f"❌ Database initialization error: {e}")
            raise

    async def close(self):
        """Close all connections"""
        if self.postgres_pool:
            await self.postgres_pool.close()
        if self.odoo_postgres_pool:
            await self.odoo_postgres_pool.close()
        if self.redis_client:
            await self.redis_client.close()
        if self.mongo_client:
            self.mongo_client.close()
        if self.rabbitmq_connection:
            await self.rabbitmq_connection.close()

# Global connections instance
db_connections = DatabaseConnections()

@app.on_event("startup")
async def startup_event():
    """Initialize database connections on startup"""
    await db_connections.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown"""
    await db_connections.close()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check for the gateway"""
    return {
        "status": "healthy",
        "service": "unified_database_gateway",
        "timestamp": datetime.now().isoformat(),
        "databases": ["odoo", "postgres", "redis", "mongodb", "rabbitmq", "supabase"]
    }

@app.get("/health/databases", response_model=List[HealthStatus])
async def check_all_databases():
    """Check health of all databases"""
    health_results = []

    # Odoo PostgreSQL health
    start_time = time.time()
    try:
        async with db_connections.odoo_postgres_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        response_time = (time.time() - start_time) * 1000
        health_results.append(HealthStatus(
            database="odoo",
            status="online",
            response_time=response_time,
            last_checked=datetime.now()
        ))
    except Exception as e:
        health_results.append(HealthStatus(
            database="odoo",
            status="offline",
            error=str(e),
            last_checked=datetime.now()
        ))

    # PostgreSQL health
    start_time = time.time()
    try:
        async with db_connections.postgres_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        response_time = (time.time() - start_time) * 1000
        health_results.append(HealthStatus(
            database="postgres",
            status="online",
            response_time=response_time,
            last_checked=datetime.now()
        ))
    except Exception as e:
        health_results.append(HealthStatus(
            database="postgres",
            status="offline",
            error=str(e),
            last_checked=datetime.now()
        ))

    # Redis health
    start_time = time.time()
    try:
        await db_connections.redis_client.ping()
        response_time = (time.time() - start_time) * 1000
        health_results.append(HealthStatus(
            database="redis",
            status="online",
            response_time=response_time,
            last_checked=datetime.now()
        ))
    except Exception as e:
        health_results.append(HealthStatus(
            database="redis",
            status="offline",
            error=str(e),
            last_checked=datetime.now()
        ))

    # MongoDB health
    start_time = time.time()
    try:
        if db_connections.mongo_client:
            await db_connections.mongo_client.admin.command("ping")
            response_time = (time.time() - start_time) * 1000
            health_results.append(HealthStatus(
                database="mongodb",
                status="online",
                response_time=response_time,
                last_checked=datetime.now()
            ))
        else:
            health_results.append(HealthStatus(
                database="mongodb",
                status="offline",
                error="Not configured",
                last_checked=datetime.now()
            ))
    except Exception as e:
        health_results.append(HealthStatus(
            database="mongodb",
            status="offline",
            error=str(e),
            last_checked=datetime.now()
        ))

    # RabbitMQ health
    try:
        if db_connections.rabbitmq_connection.is_closed:
            health_results.append(HealthStatus(
                database="rabbitmq",
                status="offline",
                error="Connection closed",
                last_checked=datetime.now()
            ))
        else:
            health_results.append(HealthStatus(
                database="rabbitmq",
                status="online",
                last_checked=datetime.now()
            ))
    except Exception as e:
        health_results.append(HealthStatus(
            database="rabbitmq",
            status="offline",
            error=str(e),
            last_checked=datetime.now()
        ))

    # Supabase health
    try:
        if db_connections.supabase_client:
            # Simple health check via auth
            response = db_connections.supabase_client.auth.get_session()
            health_results.append(HealthStatus(
                database="supabase",
                status="online",
                last_checked=datetime.now()
            ))
        else:
            health_results.append(HealthStatus(
                database="supabase",
                status="offline",
                error="Not configured",
                last_checked=datetime.now()
            ))
    except Exception as e:
        health_results.append(HealthStatus(
            database="supabase",
            status="offline",
            error=str(e),
            last_checked=datetime.now()
        ))

    return health_results

@app.post("/query")
async def execute_query(operation: DatabaseOperation):
    """Execute unified database operation"""
    try:
        if operation.database == "postgres":
            return await execute_postgres_operation(operation)
        elif operation.database == "redis":
            return await execute_redis_operation(operation)
        elif operation.database == "mongodb":
            return await execute_mongodb_operation(operation)
        elif operation.database == "rabbitmq":
            return await execute_rabbitmq_operation(operation)
        elif operation.database == "supabase":
            return await execute_supabase_operation(operation)
        elif operation.database == "odoo":
            return await execute_odoo_operation(operation)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported database: {operation.database}")

    except Exception as e:
        logger.error(f"Query execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def execute_postgres_operation(operation: DatabaseOperation):
    """Execute PostgreSQL operation"""
    async with db_connections.postgres_pool.acquire() as conn:
        if operation.operation == "select":
            if operation.where:
                where_clause = " AND ".join([f"{k} = ${i+1}" for i, k in enumerate(operation.where.keys())])
                query = f"SELECT * FROM {operation.table} WHERE {where_clause}"
                result = await conn.fetch(query, *operation.where.values())
            else:
                query = f"SELECT * FROM {operation.table} LIMIT 100"
                result = await conn.fetch(query)
            return [dict(row) for row in result]

        elif operation.operation == "insert":
            columns = list(operation.data.keys())
            placeholders = [f"${i+1}" for i in range(len(columns))]
            query = f"INSERT INTO {operation.table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)}) RETURNING *"
            result = await conn.fetchrow(query, *operation.data.values())
            return dict(result)

        elif operation.operation == "update":
            set_clause = ", ".join([f"{k} = ${i+1}" for i, k in enumerate(operation.data.keys())])
            where_clause = " AND ".join([f"{k} = ${len(operation.data)+i+1}" for i, k in enumerate(operation.where.keys())])
            query = f"UPDATE {operation.table} SET {set_clause} WHERE {where_clause} RETURNING *"
            result = await conn.fetchrow(query, *operation.data.values(), *operation.where.values())
            return dict(result) if result else None

        elif operation.operation == "delete":
            where_clause = " AND ".join([f"{k} = ${i+1}" for i, k in enumerate(operation.where.keys())])
            query = f"DELETE FROM {operation.table} WHERE {where_clause}"
            await conn.execute(query, *operation.where.values())
            return {"deleted": True}

async def execute_redis_operation(operation: DatabaseOperation):
    """Execute Redis operation"""
    if operation.operation == "cache_get":
        result = await db_connections.redis_client.get(operation.key)
        return json.loads(result) if result else None

    elif operation.operation == "cache_set":
        ttl = operation.ttl or 3600  # Default 1 hour
        await db_connections.redis_client.setex(operation.key, ttl, json.dumps(operation.data))
        return {"cached": True, "key": operation.key}

async def execute_mongodb_operation(operation: DatabaseOperation):
    """Execute MongoDB operation"""
    collection = db_connections.mongo_db[operation.collection]

    if operation.operation == "select":
        cursor = collection.find(operation.where or {}).limit(100)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results

    elif operation.operation == "insert":
        result = await collection.insert_one(operation.data)
        return {"inserted_id": str(result.inserted_id)}

    elif operation.operation == "update":
        result = await collection.update_many(operation.where, {"$set": operation.data})
        return {"modified_count": result.modified_count}

    elif operation.operation == "delete":
        result = await collection.delete_many(operation.where)
        return {"deleted_count": result.deleted_count}

async def execute_rabbitmq_operation(operation: DatabaseOperation):
    """Execute RabbitMQ operation"""
    if operation.operation == "publish":
        exchange = await db_connections.rabbitmq_channel.declare_exchange(
            "bcm.events", aio_pika.ExchangeType.TOPIC, durable=True
        )

        message = aio_pika.Message(
            json.dumps(operation.data).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )

        routing_key = operation.key or "bcm.general"
        await exchange.publish(message, routing_key=routing_key)
        return {"published": True, "routing_key": routing_key}

async def execute_supabase_operation(operation: DatabaseOperation):
    """Execute Supabase operation"""
    if not db_connections.supabase_client:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    if operation.operation == "select":
        query = db_connections.supabase_client.table(operation.table).select("*")
        if operation.where:
            for key, value in operation.where.items():
                query = query.eq(key, value)
        result = query.execute()
        return result.data

    elif operation.operation == "insert":
        result = db_connections.supabase_client.table(operation.table).insert(operation.data).execute()
        return result.data

    elif operation.operation == "update":
        query = db_connections.supabase_client.table(operation.table).update(operation.data)
        if operation.where:
            for key, value in operation.where.items():
                query = query.eq(key, value)
        result = query.execute()
        return result.data

async def execute_odoo_operation(operation: DatabaseOperation):
    """Execute Odoo operation through direct database access or JSON-RPC"""

    if operation.operation in ["odoo_search", "odoo_read", "odoo_create", "odoo_write"]:
        # Use Odoo JSON-RPC API
        return await execute_odoo_rpc_operation(operation)
    else:
        # Direct database access for performance
        return await execute_odoo_direct_operation(operation)

async def execute_odoo_rpc_operation(operation: DatabaseOperation):
    """Execute Odoo operation via JSON-RPC API"""
    async with httpx.AsyncClient() as client:
        # Authentication endpoint
        auth_url = f"{DatabaseConfig.ODOO_API_URL}/web/session/authenticate"

        # Default admin credentials for integration
        auth_data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": DatabaseConfig.ODOO_DB_NAME,
                "login": "admin",
                "password": "admin"
            },
            "id": 1
        }

        # Authenticate
        auth_response = await client.post(auth_url, json=auth_data)
        auth_result = auth_response.json()

        if not auth_result.get("result") or not auth_result["result"].get("uid"):
            raise HTTPException(status_code=401, detail="Odoo authentication failed")

        session_id = auth_result["result"]["session_id"]
        uid = auth_result["result"]["uid"]

        # Execute operation
        api_url = f"{DatabaseConfig.ODOO_API_URL}/web/dataset/call_kw"

        if operation.operation == "odoo_search":
            api_data = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "model": operation.model,
                    "method": "search",
                    "args": [operation.domain or []],
                    "kwargs": {
                        "context": operation.context or {},
                        "limit": 100
                    }
                },
                "id": 2
            }
        elif operation.operation == "odoo_read":
            api_data = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "model": operation.model,
                    "method": "read",
                    "args": [operation.ids or []],
                    "kwargs": {
                        "fields": operation.fields or [],
                        "context": operation.context or {}
                    }
                },
                "id": 3
            }
        elif operation.operation == "odoo_create":
            api_data = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "model": operation.model,
                    "method": "create",
                    "args": [operation.data],
                    "kwargs": {
                        "context": operation.context or {}
                    }
                },
                "id": 4
            }
        elif operation.operation == "odoo_write":
            api_data = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "model": operation.model,
                    "method": "write",
                    "args": [operation.ids, operation.data],
                    "kwargs": {
                        "context": operation.context or {}
                    }
                },
                "id": 5
            }

        # Make API call with session
        headers = {"Cookie": f"session_id={session_id}"}
        response = await client.post(api_url, json=api_data, headers=headers)
        result = response.json()

        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"]["message"])

        return {"data": result.get("result"), "success": True}

async def execute_odoo_direct_operation(operation: DatabaseOperation):
    """Execute direct PostgreSQL operation on Odoo database"""
    async with db_connections.odoo_postgres_pool.acquire() as conn:
        if operation.operation == "select":
            if operation.where:
                where_clause = " AND ".join([f"{k} = ${i+1}" for i, k in enumerate(operation.where.keys())])
                query = f"SELECT * FROM {operation.table} WHERE {where_clause}"
                result = await conn.fetch(query, *operation.where.values())
            else:
                query = f"SELECT * FROM {operation.table} LIMIT 100"
                result = await conn.fetch(query)
            return [dict(row) for row in result]

        elif operation.operation == "insert":
            columns = list(operation.data.keys())
            placeholders = [f"${i+1}" for i in range(len(columns))]
            query = f"INSERT INTO {operation.table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)}) RETURNING *"
            result = await conn.fetchrow(query, *operation.data.values())
            return dict(result)

# Odoo Authentication Endpoints
@app.post("/auth/odoo", response_model=OdooAuthResponse)
async def authenticate_odoo(auth_request: OdooAuthRequest):
    """Authenticate with Odoo and return session info"""
    async with httpx.AsyncClient() as client:
        auth_url = f"{DatabaseConfig.ODOO_API_URL}/web/session/authenticate"

        auth_data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": auth_request.database or DatabaseConfig.ODOO_DB_NAME,
                "login": auth_request.username,
                "password": auth_request.password
            },
            "id": 1
        }

        try:
            response = await client.post(auth_url, json=auth_data)
            result = response.json()

            if result.get("error"):
                raise HTTPException(status_code=401, detail="Invalid credentials")

            if not result.get("result") or not result["result"].get("uid"):
                raise HTTPException(status_code=401, detail="Authentication failed")

            session_data = result["result"]
            session_id = secrets.token_urlsafe(32)

            # Store session in memory (для production использовать Redis)
            db_connections.odoo_sessions[session_id] = {
                "uid": session_data["uid"],
                "user_context": session_data.get("user_context", {}),
                "company_id": session_data.get("company_id"),
                "partner_id": session_data.get("partner_id"),
                "odoo_session_id": session_data.get("session_id"),
                "expires_at": time.time() + 3600  # 1 hour
            }

            return OdooAuthResponse(
                user_id=session_data["uid"],
                session_id=session_id,
                user_context=session_data.get("user_context", {}),
                company_id=session_data.get("company_id", 1),
                partner_id=session_data.get("partner_id", 1)
            )

        except httpx.RequestError as e:
            logger.error(f"Odoo authentication error: {e}")
            raise HTTPException(status_code=503, detail="Odoo service unavailable")

@app.get("/auth/odoo/session/{session_id}")
async def get_odoo_session(session_id: str):
    """Get Odoo session info"""
    session = db_connections.odoo_sessions.get(session_id)
    if not session or session["expires_at"] < time.time():
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return {"session": session, "valid": True}

@app.delete("/auth/odoo/session/{session_id}")
async def logout_odoo_session(session_id: str):
    """Logout Odoo session"""
    if session_id in db_connections.odoo_sessions:
        del db_connections.odoo_sessions[session_id]

    return {"logged_out": True}

# Metrics and monitoring
@app.get("/metrics")
async def get_metrics():
    """Get database performance metrics"""
    health_status = await check_all_databases()

    return {
        "databases": {
            db.database: {
                "status": db.status,
                "response_time": db.response_time,
                "last_checked": db.last_checked
            } for db in health_status
        },
        "gateway": {
            "status": "healthy",
            "uptime": time.time(),
            "version": "1.0.0"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="info")