"""
BCM Platform Event Bus
Centralized event management for all BCM modules
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
from sqlalchemy import create_engine, Column, String, DateTime, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)
Base = declarative_base()


class EventType(Enum):
    """BCM Platform Event Types"""
    # Client Events
    CLIENT_CREATED = "bcm.client.created"
    CLIENT_UPDATED = "bcm.client.updated"
    
    # Context Events  
    CONTEXT_IMPORTED = "bcm.context.imported"
    PROCESS_IDENTIFIED = "bcm.process.identified"
    CRITICAL_PROCESS_DETECTED = "bcm.critical_process.detected"
    
    # BIA Events
    BIA_STARTED = "bcm.bia.started"
    BIA_COMPLETED = "bcm.bia.completed"
    BIA_METRICS_CALCULATED = "bcm.bia.metrics_calculated"
    
    # Plan Events
    PLAN_GENERATED = "bcm.plan.generated"
    PLAN_APPROVED = "bcm.plan.approved"
    PLAN_REJECTED = "bcm.plan.rejected"
    PLAN_UPDATED = "bcm.plan.updated"
    
    # Training Events
    TRAINING_SCHEDULED = "bcm.training.scheduled"
    TRAINING_COMPLETED = "bcm.training.completed"
    TRAINING_FAILED = "bcm.training.failed"
    
    # Incident Events
    INCIDENT_OPENED = "bcm.incident.opened"
    INCIDENT_ESCALATED = "bcm.incident.escalated"
    INCIDENT_RESOLVED = "bcm.incident.resolved"
    
    # Exercise Events
    EXERCISE_SCHEDULED = "bcm.exercise.scheduled"
    EXERCISE_STARTED = "bcm.exercise.started"
    EXERCISE_COMPLETED = "bcm.exercise.completed"
    EXERCISE_OVERDUE = "bcm.exercise.overdue"
    
    # Audit Events
    AUDIT_SCHEDULED = "bcm.audit.scheduled"
    AUDIT_STARTED = "bcm.audit.started"
    AUDIT_FINDINGS = "bcm.audit.findings"
    AUDIT_COMPLETED = "bcm.audit.completed"
    
    # KPI Events
    KPI_CALCULATED = "bcm.kpi.calculated"
    KPI_THRESHOLD_BREACH = "bcm.kpi.threshold_breach"
    
    # Governance Events
    MANAGEMENT_REVIEW_SCHEDULED = "bcm.governance.review_scheduled"
    MANAGEMENT_REVIEW_COMPLETED = "bcm.governance.review_completed"
    POLICY_UPDATED = "bcm.governance.policy_updated"


@dataclass
class Event:
    """BCM Event Structure"""
    id: str
    type: EventType
    timestamp: datetime
    actor: str  # User or system that triggered the event
    tenant_id: str
    module: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert event to dictionary"""
        return {
            'id': self.id,
            'type': self.type.value,
            'timestamp': self.timestamp.isoformat(),
            'actor': self.actor,
            'tenant_id': self.tenant_id,
            'module': self.module,
            'data': self.data,
            'metadata': self.metadata,
            'correlation_id': self.correlation_id
        }


class EventStore(Base):
    """Database model for event storage"""
    __tablename__ = 'bcm_events'
    
    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    actor = Column(String, nullable=False)
    tenant_id = Column(String, nullable=False)
    module = Column(String, nullable=False)
    data = Column(JSON, nullable=False)
    metadata = Column(JSON)
    correlation_id = Column(String)
    processed = Column(Integer, default=0)


class EventBus:
    """Central Event Bus for BCM Platform"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", 
                 db_url: str = "postgresql://localhost/bcm_events"):
        self.redis_url = redis_url
        self.db_url = db_url
        self.redis_client: Optional[redis.Redis] = None
        self.db_engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.db_engine)
        self.handlers: Dict[EventType, List[Callable]] = {}
        self.running = False
        
        # Create tables
        Base.metadata.create_all(self.db_engine)
    
    async def connect(self):
        """Connect to Redis and database"""
        self.redis_client = await redis.from_url(self.redis_url)
        logger.info("EventBus connected to Redis and Database")
    
    async def disconnect(self):
        """Disconnect from services"""
        if self.redis_client:
            await self.redis_client.close()
        logger.info("EventBus disconnected")
    
    def register_handler(self, event_type: EventType, handler: Callable):
        """Register an event handler"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        logger.info(f"Registered handler for {event_type.value}")
    
    def unregister_handler(self, event_type: EventType, handler: Callable):
        """Unregister an event handler"""
        if event_type in self.handlers:
            self.handlers[event_type].remove(handler)
    
    async def publish(self, event: Event):
        """Publish an event to the bus"""
        try:
            # Store in database
            session = self.Session()
            db_event = EventStore(
                id=event.id,
                type=event.type.value,
                timestamp=event.timestamp,
                actor=event.actor,
                tenant_id=event.tenant_id,
                module=event.module,
                data=event.data,
                metadata=event.metadata,
                correlation_id=event.correlation_id
            )
            session.add(db_event)
            session.commit()
            session.close()
            
            # Publish to Redis for real-time processing
            if self.redis_client:
                await self.redis_client.publish(
                    f"bcm_events:{event.tenant_id}",
                    json.dumps(event.to_dict())
                )
            
            # Call registered handlers
            if event.type in self.handlers:
                for handler in self.handlers[event.type]:
                    asyncio.create_task(self._call_handler(handler, event))
            
            logger.info(f"Published event: {event.type.value} - {event.id}")
            
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            raise
    
    async def _call_handler(self, handler: Callable, event: Event):
        """Call event handler with error handling"""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            logger.error(f"Error in handler for {event.type.value}: {e}")
    
    async def subscribe(self, tenant_id: str, callback: Callable):
        """Subscribe to events for a specific tenant"""
        if not self.redis_client:
            await self.connect()
        
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe(f"bcm_events:{tenant_id}")
        
        async for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    event_data = json.loads(message['data'])
                    await callback(event_data)
                except Exception as e:
                    logger.error(f"Error processing subscription message: {e}")
    
    async def get_events(self, tenant_id: str, 
                         event_type: Optional[EventType] = None,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         limit: int = 100) -> List[Event]:
        """Retrieve events from the store"""
        session = self.Session()
        query = session.query(EventStore).filter(
            EventStore.tenant_id == tenant_id
        )
        
        if event_type:
            query = query.filter(EventStore.type == event_type.value)
        
        if start_date:
            query = query.filter(EventStore.timestamp >= start_date)
        
        if end_date:
            query = query.filter(EventStore.timestamp <= end_date)
        
        query = query.order_by(EventStore.timestamp.desc()).limit(limit)
        
        events = []
        for db_event in query.all():
            event = Event(
                id=db_event.id,
                type=EventType(db_event.type),
                timestamp=db_event.timestamp,
                actor=db_event.actor,
                tenant_id=db_event.tenant_id,
                module=db_event.module,
                data=db_event.data,
                metadata=db_event.metadata,
                correlation_id=db_event.correlation_id
            )
            events.append(event)
        
        session.close()
        return events
    
    async def replay_events(self, tenant_id: str, 
                           event_type: EventType,
                           handler: Callable):
        """Replay historical events for processing"""
        events = await self.get_events(tenant_id, event_type)
        for event in events:
            await self._call_handler(handler, event)
    
    def get_event_stats(self, tenant_id: str) -> Dict[str, int]:
        """Get event statistics for a tenant"""
        session = self.Session()
        stats = {}
        
        for event_type in EventType:
            count = session.query(EventStore).filter(
                EventStore.tenant_id == tenant_id,
                EventStore.type == event_type.value
            ).count()
            stats[event_type.value] = count
        
        session.close()
        return stats


# Singleton instance
event_bus = EventBus()


# Helper functions for common event patterns
async def emit_bia_completed(tenant_id: str, actor: str, 
                            bia_results: Dict[str, Any]):
    """Emit BIA completed event"""
    import uuid
    event = Event(
        id=str(uuid.uuid4()),
        type=EventType.BIA_COMPLETED,
        timestamp=datetime.utcnow(),
        actor=actor,
        tenant_id=tenant_id,
        module="bcm_bia",
        data=bia_results,
        metadata={"version": "1.0"}
    )
    await event_bus.publish(event)


async def emit_incident_opened(tenant_id: str, actor: str,
                              incident_data: Dict[str, Any]):
    """Emit incident opened event"""
    import uuid
    event = Event(
        id=str(uuid.uuid4()),
        type=EventType.INCIDENT_OPENED,
        timestamp=datetime.utcnow(),
        actor=actor,
        tenant_id=tenant_id,
        module="bcm_incident",
        data=incident_data,
        metadata={"severity": incident_data.get("severity", "medium")}
    )
    await event_bus.publish(event)


async def emit_plan_approved(tenant_id: str, actor: str,
                            plan_data: Dict[str, Any]):
    """Emit plan approved event"""
    import uuid
    event = Event(
        id=str(uuid.uuid4()),
        type=EventType.PLAN_APPROVED,
        timestamp=datetime.utcnow(),
        actor=actor,
        tenant_id=tenant_id,
        module="bcm_plans",
        data=plan_data,
        metadata={"plan_type": plan_data.get("type", "BCP")}
    )
    await event_bus.publish(event)
