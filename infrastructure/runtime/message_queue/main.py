"""
Message Queue Service - Async message broker

Provides message queue functionality for async communication between services.
Simple in-memory queue with RabbitMQ-compatible API.

Port: 8061
"""

import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict, deque
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("MESSAGE_QUEUE_PORT", "8061"))
HOST = os.getenv("MESSAGE_QUEUE_HOST", "0.0.0.0")

app = FastAPI(
    title="Message Queue Service",
    description="Async message broker for inter-service communication",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory message storage
queues: Dict[str, deque] = defaultdict(deque)
message_stats: Dict[str, int] = defaultdict(int)

class Message(BaseModel):
    queue: str
    body: Dict
    priority: Optional[int] = 0

class QueueConfig(BaseModel):
    name: str
    max_size: Optional[int] = 10000

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "message-queue",
        "version": "1.0.0",
        "active_queues": len(queues),
        "total_messages": sum(len(q) for q in queues.values())
    }

@app.post("/queues")
async def create_queue(config: QueueConfig):
    """Create a new message queue"""
    if config.name in queues:
        raise HTTPException(status_code=409, detail="Queue already exists")

    queues[config.name] = deque(maxlen=config.max_size)

    logger.info(f"Queue created: {config.name}")

    return {
        "status": "created",
        "queue": config.name
    }

@app.get("/queues")
async def list_queues():
    """List all queues"""
    return {
        "queues": [
            {
                "name": name,
                "size": len(queue),
                "messages_processed": message_stats.get(name, 0)
            }
            for name, queue in queues.items()
        ]
    }

@app.post("/messages")
async def publish_message(message: Message):
    """Publish a message to a queue"""
    if message.queue not in queues:
        queues[message.queue] = deque(maxlen=10000)

    queues[message.queue].append({
        "body": message.body,
        "priority": message.priority,
        "timestamp": datetime.now().isoformat()
    })

    message_stats[message.queue] += 1

    logger.debug(f"Message published to {message.queue}")

    return {
        "status": "published",
        "queue": message.queue
    }

@app.get("/messages/{queue_name}")
async def consume_message(queue_name: str):
    """Consume a message from a queue"""
    if queue_name not in queues or not queues[queue_name]:
        raise HTTPException(status_code=404, detail="No messages in queue")

    message = queues[queue_name].popleft()

    return {
        "message": message,
        "queue": queue_name
    }

@app.delete("/queues/{queue_name}")
async def delete_queue(queue_name: str):
    """Delete a queue"""
    if queue_name not in queues:
        raise HTTPException(status_code=404, detail="Queue not found")

    del queues[queue_name]
    logger.info(f"Queue deleted: {queue_name}")

    return {
        "status": "deleted",
        "queue": queue_name
    }

if __name__ == "__main__":
    logger.info(f"Starting Message Queue Service on {HOST}:{PORT}")
    logger.info("Note: This is an in-memory queue. For production, consider RabbitMQ or Redis.")

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    )
