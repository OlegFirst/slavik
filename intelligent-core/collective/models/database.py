"""
Database Models for Collective Agent Networks

Tables:
- collective_agents: Temporary AI agents from multiple orgs
- collective_agent_messages: Chat history
- stuck_detection_logs: Tracking of stuck organizations
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean, Enum as SQLEnum, Text, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum

# Enums

class AgentStatus(str, enum.Enum):
    """Status of collective agent"""
    ACTIVE = "active"
    EXPIRED = "expired"
    ARCHIVED = "archived"

# Models

class CollectiveAgent:
    """
    Collective Agent - Temporary AI created from multiple organizations

    Privacy guarantees:
    - Source organizations NEVER revealed
    - All data anonymized before aggregation
    - Expires after 7 days
    """

    __tablename__ = "collective_agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requesting_org_id = Column(UUID(as_uuid=True), nullable=False)  # Who requested help
    problem_type = Column(String(100), nullable=False)  # e.g., "supply_chain_complexity"

    # Source information (anonymized)
    source_org_count = Column(Integer, nullable=False)  # Number of orgs contributing
    source_org_types = Column(ARRAY(String), nullable=False)  # e.g., ["healthcare_medium", "hospital_large"]

    # Agent configuration
    system_prompt = Column(Text, nullable=False)  # LLM system prompt with privacy rules
    approaches_data = Column(JSON, nullable=False)  # Anonymized approaches from source orgs

    # Status and lifecycle
    status = Column(SQLEnum(AgentStatus), nullable=False, default=AgentStatus.ACTIVE)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)  # Auto-expire after 7 days

    # Usage stats
    message_count = Column(Integer, nullable=False, default=0)
    last_interaction = Column(DateTime, nullable=True)


class CollectiveAgentMessage:
    """
    Chat messages with Collective Agent

    Stored for conversation continuity
    Archived when agent expires
    """

    __tablename__ = "collective_agent_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("collective_agents.id"), nullable=False)

    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)

    metadata = Column(JSON, nullable=True)  # Confidence scores, etc.
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class StuckDetectionLog:
    """
    Log of stuck organization detections

    Tracks when organizations detected as stuck and recommendations offered
    """

    __tablename__ = "stuck_detection_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), nullable=False)
    module = Column(String(50), nullable=True)

    # Detection results
    stuck_score = Column(Integer, nullable=False)
    signals = Column(JSON, nullable=False)  # All signals that contributed

    # Recommendations
    recommendations = Column(JSON, nullable=False)

    # Outcome
    help_offered = Column(Boolean, nullable=False, default=False)
    help_accepted = Column(Boolean, nullable=False, default=False)
    collective_agent_created = Column(UUID(as_uuid=True), nullable=True)

    detected_at = Column(DateTime, nullable=False, default=datetime.utcnow)
