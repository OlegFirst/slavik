"""
Database Schema for Community Intelligence Foundation

Tables:
- case_contributions: Community-submitted workflow cases
- peer_reviews: Quality reviews for contributions
- user_reputation: Multi-dimensional reputation tracking
- reputation_transactions: Audit trail for points
- community_annotations: Expert interpretations of standards
- synthesized_guidance: AI-unified documentation
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

Base = declarative_base()

class ContributionStatus(enum.Enum):
    """Contribution workflow states"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class CaseContribution(Base):
    """Community-contributed workflow cases"""
    __tablename__ = 'case_contributions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Contributor
    contributor_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    contributor_type = Column(String(50))  # consultant, auditor, bcm_manager

    # Case data (anonymized)
    case_data = Column(JSONB, nullable=False)
    original_org_type = Column(String(100))  # For matching similar orgs

    # Status
    status = Column(Enum(ContributionStatus), default=ContributionStatus.DRAFT, index=True)

    # Review
    reviewers = Column(ARRAY(UUID(as_uuid=True)))  # Assigned reviewers
    review_deadline = Column(DateTime)

    # Metadata
    submitted_at = Column(DateTime, default=datetime.utcnow, index=True)
    approved_at = Column(DateTime)
    added_to_library = Column(Boolean, default=False)
    library_case_id = Column(UUID(as_uuid=True))  # Link to case_library

    # Tags for discovery
    tags = Column(ARRAY(String))
    module = Column(String(50), index=True)

    # Relations
    reviews = relationship("PeerReview", back_populates="contribution")

class PeerReview(Base):
    """Peer reviews for case contributions"""
    __tablename__ = 'peer_reviews'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    contribution_id = Column(UUID(as_uuid=True), ForeignKey('case_contributions.id'), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Review
    approved = Column(Boolean)
    quality_score = Column(Integer)  # 1-10
    feedback = Column(Text)
    suggested_improvements = Column(JSONB)

    # Criteria
    anonymization_ok = Column(Boolean)
    relevance_ok = Column(Boolean)
    completeness_ok = Column(Boolean)
    lessons_clear = Column(Boolean)

    reviewed_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    contribution = relationship("CaseContribution", back_populates="reviews")

class UserReputation(Base):
    """Multi-dimensional reputation system"""
    __tablename__ = 'user_reputation'

    user_id = Column(UUID(as_uuid=True), primary_key=True)

    # Overall
    total_points = Column(Integer, default=0, index=True)
    level = Column(String(50), default='newcomer')  # newcomer, contributor, expert, master

    # Dimension scores
    contribution_points = Column(Integer, default=0)
    review_points = Column(Integer, default=0)
    helpfulness_points = Column(Integer, default=0)
    marketplace_rating = Column(Float)

    # Expertise areas (BCI-style categories)
    expertise = Column(JSONB, default={})  # {bcm: 85, risk: 70, ...}

    # Badges
    badges = Column(ARRAY(String))

    # Activity
    contributions_count = Column(Integer, default=0)
    reviews_count = Column(Integer, default=0)
    helpful_answers = Column(Integer, default=0)

    # Timestamps
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    first_contribution = Column(DateTime)

class ReputationTransaction(Base):
    """Audit trail for reputation changes"""
    __tablename__ = 'reputation_transactions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    points = Column(Integer, nullable=False)  # Can be negative
    reason = Column(String(100), nullable=False)

    # Context
    related_contribution_id = Column(UUID(as_uuid=True))
    related_review_id = Column(UUID(as_uuid=True))

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class CommunityAnnotation(Base):
    """Community annotations for standards/clauses"""
    __tablename__ = 'community_annotations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # What's being annotated
    clause_id = Column(String(50), nullable=False, index=True)
    standard = Column(String(50))  # ISO22301, BCI_GPG

    # Annotation
    author_id = Column(UUID(as_uuid=True), nullable=False)
    interpretation = Column(Text, nullable=False)

    # Context
    industry_specific = Column(String(100))  # healthcare, finance
    organization_size = Column(String(50))
    practical_examples = Column(JSONB)

    # Community feedback
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)

    # Status
    verified = Column(Boolean, default=False)  # Verified by high-rep user

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class SynthesizedGuidance(Base):
    """AI-synthesized guidance from multiple sources"""
    __tablename__ = 'synthesized_guidance'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    clause_id = Column(String(50), nullable=False, unique=True)

    # Sources used
    official_text = Column(Text)
    community_interpretations = Column(JSONB)  # Array of annotation IDs
    case_examples = Column(JSONB)  # Array of case IDs

    # Synthesized content
    unified_guidance = Column(Text, nullable=False)
    practical_steps = Column(JSONB)
    common_pitfalls = Column(JSONB)
    success_patterns = Column(JSONB)

    # Metadata
    synthesis_version = Column(Integer, default=1)
    synthesized_at = Column(DateTime, default=datetime.utcnow)
    sources_count = Column(Integer)
    confidence_score = Column(Float)
