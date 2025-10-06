"""
Template Models - Ported from bcm_templates Odoo module

Provides:
- Document templates (policies, procedures, plans, reports)
- BPMN workflow templates (exercises, incident response, audits)
- Form templates (BIA, risk assessment, evaluation)
- Checklist templates
"""

from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class TemplateCategory(str, Enum):
    """Template categories"""
    DOCUMENT = "document"
    WORKFLOW = "workflow"
    FORM = "form"
    CHECKLIST = "checklist"
    REPORT = "report"


class TemplateType(str, Enum):
    """Specific template types"""
    # Document templates
    POLICY = "policy"
    PROCEDURE = "procedure"
    PLAN = "plan"
    BIA_REPORT = "bia_report"
    RISK_REGISTER = "risk_register"
    INCIDENT_REPORT = "incident_report"

    # BPMN workflow templates
    TABLETOP_EXERCISE = "tabletop_exercise"
    FUNCTIONAL_EXERCISE = "functional_exercise"
    FULL_SCALE_EXERCISE = "full_scale_exercise"
    INCIDENT_RESPONSE = "incident_response"
    COMPLIANCE_AUDIT = "compliance_audit"
    RISK_ASSESSMENT = "risk_assessment"

    # Form templates
    BIA_FORM = "bia_form"
    RISK_FORM = "risk_form"
    EXERCISE_FORM = "exercise_form"

    # Checklists
    EXERCISE_CHECKLIST = "exercise_checklist"
    INCIDENT_CHECKLIST = "incident_checklist"
    AUDIT_CHECKLIST = "audit_checklist"


class Template(BaseModel):
    """Base template model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str

    name: str
    description: Optional[str] = None
    notes: Optional[str] = None

    category: TemplateCategory
    template_type: TemplateType

    # Content (depends on category)
    content: Optional[str] = None  # HTML for documents
    bpmn_xml: Optional[str] = None  # BPMN 2.0 XML for workflows
    form_schema: Optional[Dict] = None  # JSON schema for forms

    # ISO 22301 compliance
    iso_clause: Optional[str] = None

    # Usage tracking
    usage_count: int = 0
    last_used: Optional[datetime] = None

    # AI enhancement
    is_ai_enhanced: bool = False
    ai_prompt: Optional[str] = None

    # Metadata
    active: bool = True
    sequence: int = 10
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None


class BPMNWorkflow(BaseModel):
    """BPMN 2.0 Workflow template"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str

    name: str
    description: str
    workflow_type: TemplateType  # Must be workflow type

    # BPMN definition
    bpmn_xml: str

    # Simulation configuration (for exercises)
    needs_simulation: bool = False
    jaamsim_config: Optional[str] = None

    # ISO compliance
    iso_clause: Optional[str] = None

    # Metadata
    usage_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TemplateCreate(BaseModel):
    """Create template request"""
    name: str
    description: Optional[str] = None
    category: TemplateCategory
    template_type: TemplateType
    content: Optional[str] = None
    bpmn_xml: Optional[str] = None
    form_schema: Optional[Dict] = None
    iso_clause: Optional[str] = None
    is_ai_enhanced: bool = False
    ai_prompt: Optional[str] = None


class TemplateUpdate(BaseModel):
    """Update template request"""
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    bpmn_xml: Optional[str] = None
    form_schema: Optional[Dict] = None
    iso_clause: Optional[str] = None
    active: Optional[bool] = None


class TemplateRenderRequest(BaseModel):
    """Render template with variables"""
    variables: Dict[str, any]


class AIGenerateRequest(BaseModel):
    """AI generation request"""
    template_type: TemplateType
    prompt: str
    iso_clause: Optional[str] = None
    context: Optional[Dict] = None


# Database model would be added to compliance/models/database.py
class TemplateModel:
    """
    SQLAlchemy model for templates table

    Should be added to compliance/models/database.py:

    class TemplateModel(Base):
        __tablename__ = "templates"
        __table_args__ = {'schema': 'compliance'}

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        tenant_id = Column(String, nullable=False, index=True)

        name = Column(String, nullable=False)
        description = Column(Text)
        notes = Column(Text)

        category = Column(Enum(TemplateCategory), nullable=False)
        template_type = Column(Enum(TemplateType), nullable=False)

        content = Column(Text)  # HTML content
        bpmn_xml = Column(Text)  # BPMN XML
        form_schema = Column(JSONB)  # JSON schema

        iso_clause = Column(String)

        usage_count = Column(Integer, default=0)
        last_used = Column(DateTime)

        is_ai_enhanced = Column(Boolean, default=False)
        ai_prompt = Column(Text)

        active = Column(Boolean, default=True)
        sequence = Column(Integer, default=10)

        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, onupdate=datetime.utcnow)
        created_by = Column(String)

        __table_args__ = (
            Index('idx_templates_tenant_category', 'tenant_id', 'category'),
            Index('idx_templates_tenant_type', 'tenant_id', 'template_type'),
            {'schema': 'compliance'}
        )
    """
    pass
