"""
SQLAlchemy models для Case Library

Database schema для хранения workflow cases, events и embeddings
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class WorkflowCaseDB(Base):
    """Database model for workflow cases"""
    __tablename__ = 'workflow_cases'

    # Primary key
    case_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic info
    module = Column(String(50), nullable=False, index=True)
    workflow_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default='completed')

    # Organization context (anonymized)
    org_industry = Column(String(100), nullable=False, index=True)
    org_size = Column(String(20), nullable=False, index=True)
    org_maturity = Column(String(20), nullable=False, index=True)
    org_region = Column(String(50))
    org_regulatory = Column(JSONB)  # Array of strings

    # Journey
    journey = Column(JSONB, nullable=False)  # Array of workflow steps

    # Metrics
    duration_days = Column(Float, nullable=False, index=True)
    processes_count = Column(Integer)
    ai_usage_count = Column(Integer, index=True)
    user_satisfaction = Column(Float)
    challenges_count = Column(Integer)
    success = Column(Boolean, nullable=False, index=True)

    # Patterns and lessons
    success_patterns = Column(JSONB)  # Array of strings
    lessons_learned = Column(JSONB)   # Array of strings

    # ML features
    features = Column(JSONB)

    # Vector embedding for semantic search (если используем pgvector)
    # embedding = Column(Vector(1536))  # OpenAI ada-002 dimension

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Indexes
    __table_args__ = (
        # Composite indexes for common queries
        Index('idx_industry_size_module', 'org_industry', 'org_size', 'module'),
        Index('idx_success_duration', 'success', 'duration_days'),
    )

class WorkflowEventDB(Base):
    """Raw workflow events for case compilation"""
    __tablename__ = 'workflow_events'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Context
    org_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    workflow_id = Column(String(100), nullable=False, index=True)
    module = Column(String(50), nullable=False, index=True)

    # Event
    event_type = Column(String(100), nullable=False, index=True)
    event_data = Column(JSONB, nullable=False)

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        Index('idx_org_module_time', 'org_id', 'module', 'timestamp'),
    )

class CaseEmbeddingDB(Base):
    """Embeddings для semantic search"""
    __tablename__ = 'case_embeddings'

    case_id = Column(UUID(as_uuid=True), primary_key=True)

    # Text representation для embedding
    text_content = Column(Text, nullable=False)

    # Embedding (зависит от используемой vector DB)
    # Если pgvector:
    # embedding = Column(Vector(1536))

    # Если внешний vector DB (Pinecone/Weaviate), то только metadata:
    vector_db_id = Column(String(100))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
