"""
Organization Database Models
"""

from sqlalchemy import Column, Integer, String, Boolean, Date, Text, ARRAY, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, INET
from sqlalchemy.sql import func

from database.models import Base


class Organization(Base):
    """Organization/Tenant Model"""

    __tablename__ = "organizations"
    __table_args__ = {'schema': 'core'}

    id = Column(String(255), primary_key=True)

    # Basic Info
    name = Column(String(500), nullable=False, index=True)
    legal_name = Column(String(500))

    # Classification
    industry = Column(String(100), index=True)
    organization_size = Column(String(50))
    organization_type = Column(String(50))

    # Location
    country = Column(String(100))
    city = Column(String(200))
    address = Column(Text)
    timezone = Column(String(100))

    # Contact
    primary_contact_name = Column(String(255))
    primary_contact_email = Column(String(255))
    primary_contact_phone = Column(String(50))
    website = Column(String(500))

    # BCM Program Info
    bcm_maturity_level = Column(String(50))
    iso22301_certified = Column(Boolean, default=False)
    certification_date = Column(Date)
    certification_body = Column(String(255))

    # Compliance & Standards
    applicable_standards = Column(JSONB, default=[])
    regulatory_requirements = Column(JSONB, default=[])

    # Business Context
    critical_services = Column(JSONB, default=[])
    key_dependencies = Column(JSONB, default=[])
    risk_appetite = Column(String(50))

    # Subscription & Licensing
    subscription_tier = Column(String(50), index=True)
    subscription_status = Column(String(50), default='active', index=True)
    subscription_start_date = Column(Date)
    subscription_end_date = Column(Date)
    max_users = Column(Integer, default=10)

    # Features & Modules
    enabled_modules = Column(JSONB, default=[])
    feature_flags = Column(JSONB, default={})

    # Configuration
    settings = Column(JSONB, default={})
    branding = Column(JSONB, default={})

    # Status
    is_active = Column(Boolean, default=True, index=True)
    onboarding_completed = Column(Boolean, default=False)
    onboarding_completed_at = Column(TIMESTAMP(timezone=True))

    # Metadata
    notes = Column(Text)
    tags = Column(JSONB, default=[])

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(255))
    updated_by = Column(String(255))

    def __repr__(self):
        return f"<Organization(id='{self.id}', name='{self.name}', tier='{self.subscription_tier}')>"


class OrganizationUser(Base):
    """Organization Users Junction Table"""

    __tablename__ = "organization_users"
    __table_args__ = {'schema': 'core'}

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String(255), ForeignKey('core.organizations.id', ondelete='CASCADE'),
                            nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)

    # Role in Organization
    role = Column(String(50), nullable=False)
    title = Column(String(255))
    department = Column(String(255))

    # Permissions
    permissions = Column(JSONB, default=[])

    # Status
    is_primary_contact = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, index=True)
    invited_at = Column(TIMESTAMP(timezone=True))
    joined_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_active_at = Column(TIMESTAMP(timezone=True))

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<OrganizationUser(org='{self.organization_id}', user='{self.user_id}', role='{self.role}')>"


class OrganizationAuditLog(Base):
    """Organization Audit Log"""

    __tablename__ = "organization_audit_log"
    __table_args__ = {'schema': 'core'}

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String(255), ForeignKey('core.organizations.id', ondelete='CASCADE'),
                            nullable=False, index=True)

    # Event Info
    event_type = Column(String(100), nullable=False, index=True)
    event_category = Column(String(50), index=True)

    # Actor
    performed_by = Column(String(255), index=True)
    performed_by_role = Column(String(50))

    # Details
    description = Column(Text)
    changes = Column(JSONB)
    org_metadata = Column(JSONB, default={})

    # Context
    ip_address = Column(INET)
    user_agent = Column(Text)

    # Timestamp
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<OrganizationAuditLog(org='{self.organization_id}', event='{self.event_type}')>"
