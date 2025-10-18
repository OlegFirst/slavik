"""
Templates API - Document Templates & BPMN Workflows

Ported from: /services/SERVICES/bcm_templates (Odoo module)

Provides:
- Document templates (policies, procedures, plans, reports)
- BPMN 2.0 workflow templates (exercises, audits, incident response)
- Form templates (BIA, risk assessment, evaluations)
- AI-powered template generation
"""

from fastapi import APIRouter, HTTPException, Header, Depends
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..templates.models import (
    Template,
    TemplateCreate,
    TemplateUpdate,
    TemplateCategory,
    TemplateType,
    TemplateRenderRequest,
    AIGenerateRequest
)

router = APIRouter()


@router.get("/templates")
async def list_templates(
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    category: Optional[TemplateCategory] = None,
    template_type: Optional[TemplateType] = None,
    iso_clause: Optional[str] = None,
    active_only: bool = True
):
    """
    List all templates with optional filters

    Filters:
    - category: document, workflow, form, checklist, report
    - template_type: policy, procedure, tabletop_exercise, etc.
    - iso_clause: Filter by ISO 22301 clause
    - active_only: Only return active templates
    """
    # TODO: Implement database query
    # For now, return example templates

    example_templates = [
        {
            "id": "tpl-001",
            "name": "BCM Policy Template",
            "category": "document",
            "template_type": "policy",
            "iso_clause": "5.2",
            "description": "Standard BCM policy template aligned with ISO 22301 Clause 5.2",
            "usage_count": 45,
            "is_ai_enhanced": True
        },
        {
            "id": "tpl-002",
            "name": "Tabletop Exercise Workflow",
            "category": "workflow",
            "template_type": "tabletop_exercise",
            "iso_clause": "8.5",
            "description": "BPMN 2.0 workflow for conducting tabletop exercises",
            "usage_count": 28,
            "is_ai_enhanced": False
        },
        {
            "id": "tpl-003",
            "name": "BIA Assessment Form",
            "category": "form",
            "template_type": "bia_form",
            "iso_clause": "8.2.2",
            "description": "Structured BIA assessment form with JSON schema",
            "usage_count": 67,
            "is_ai_enhanced": False
        },
        {
            "id": "tpl-004",
            "name": "Business Continuity Plan Template",
            "category": "document",
            "template_type": "plan",
            "iso_clause": "8.4",
            "description": "Comprehensive BC plan template with sections for all ISO requirements",
            "usage_count": 52,
            "is_ai_enhanced": True
        },
        {
            "id": "tpl-005",
            "name": "Full-Scale Exercise Workflow",
            "category": "workflow",
            "template_type": "full_scale_exercise",
            "iso_clause": "8.5",
            "description": "Complex BPMN workflow for full-scale exercises with JaamSim simulation integration",
            "usage_count": 15,
            "is_ai_enhanced": False
        }
    ]

    # Apply filters
    filtered = example_templates
    if category:
        filtered = [t for t in filtered if t["category"] == category.value]
    if template_type:
        filtered = [t for t in filtered if t["template_type"] == template_type.value]
    if iso_clause:
        filtered = [t for t in filtered if t["iso_clause"] == iso_clause]

    return {
        "tenant_id": tenant_id,
        "total": len(filtered),
        "filters": {
            "category": category,
            "template_type": template_type,
            "iso_clause": iso_clause
        },
        "templates": filtered
    }


@router.post("/templates")
async def create_template(
    template: TemplateCreate,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    user_id: str = Header(..., alias="X-User-ID")
):
    """
    Create new template

    Supports:
    - Document templates (HTML content)
    - BPMN workflows (XML)
    - Form templates (JSON schema)
    """
    # TODO: Implement database creation

    return {
        "message": "Template created successfully",
        "template_id": "tpl-new-001",
        "name": template.name,
        "category": template.category,
        "template_type": template.template_type
    }


@router.get("/templates/{template_id}")
async def get_template(
    template_id: str,
    tenant_id: str = Header(..., alias="X-Tenant-ID")
):
    """
    Get template by ID with full content
    """
    # TODO: Implement database query

    # Example for BCM Policy template
    if template_id == "tpl-001":
        return {
            "id": "tpl-001",
            "name": "BCM Policy Template",
            "category": "document",
            "template_type": "policy",
            "iso_clause": "5.2",
            "description": "Standard BCM policy template aligned with ISO 22301 Clause 5.2",
            "content": """
<h1>Business Continuity Management Policy</h1>

<h2>1. Purpose</h2>
<p>This policy establishes the framework for {{organization_name}}'s Business Continuity Management System (BCMS) in accordance with ISO 22301:2019.</p>

<h2>2. Scope</h2>
<p>This policy applies to {{scope_statement}}</p>

<h2>3. Policy Statement</h2>
<p>{{organization_name}} is committed to:</p>
<ul>
  <li>Maintaining business continuity capabilities</li>
  <li>Protecting stakeholder interests</li>
  <li>Ensuring resilience of critical operations</li>
</ul>

<h2>4. Responsibilities</h2>
<p>{{leadership_commitment}}</p>
            """,
            "variables": [
                "organization_name",
                "scope_statement",
                "leadership_commitment"
            ],
            "usage_count": 45,
            "is_ai_enhanced": True,
            "ai_prompt": "Generate ISO 22301 compliant BCM policy for organization"
        }

    raise HTTPException(status_code=404, detail=f"Template {template_id} not found")


@router.put("/templates/{template_id}")
async def update_template(
    template_id: str,
    template: TemplateUpdate,
    tenant_id: str = Header(..., alias="X-Tenant-ID")
):
    """
    Update existing template
    """
    # TODO: Implement database update

    return {
        "message": "Template updated successfully",
        "template_id": template_id
    }


@router.post("/templates/{template_id}/render")
async def render_template(
    template_id: str,
    render_request: TemplateRenderRequest,
    tenant_id: str = Header(..., alias="X-Tenant-ID")
):
    """
    Render template with provided variables

    Example:
    POST /templates/tpl-001/render
    {
      "variables": {
        "organization_name": "Acme Corp",
        "scope_statement": "All critical business operations",
        "leadership_commitment": "CEO John Doe commits..."
      }
    }

    Returns: Rendered HTML/content with variables replaced
    """
    # TODO: Implement template rendering with Jinja2 or similar

    return {
        "template_id": template_id,
        "rendered_content": "<h1>BCM Policy for Acme Corp</h1>...",
        "variables_used": list(render_request.variables.keys())
    }


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: str,
    tenant_id: str = Header(..., alias="X-Tenant-ID")
):
    """
    Delete (archive) template
    """
    # TODO: Implement soft delete (set active=False)

    return {
        "message": "Template deleted successfully",
        "template_id": template_id
    }


@router.get("/templates/category/{category}")
async def get_templates_by_category(
    category: TemplateCategory,
    tenant_id: str = Header(..., alias="X-Tenant-ID")
):
    """
    Get all templates in a category

    Categories:
    - document: Policies, procedures, plans
    - workflow: BPMN workflows
    - form: Assessment forms
    - checklist: Checklists
    - report: Report templates
    """
    # Redirect to list_templates with filter
    return await list_templates(tenant_id=tenant_id, category=category)


@router.get("/templates/iso-clause/{clause}")
async def get_templates_by_iso_clause(
    clause: str,
    tenant_id: str = Header(..., alias="X-Tenant-ID")
):
    """
    Get all templates for specific ISO 22301 clause

    Example: /templates/iso-clause/8.4 returns all plan templates
    """
    return await list_templates(tenant_id=tenant_id, iso_clause=clause)


@router.post("/templates/generate")
async def generate_template_with_ai(
    request: AIGenerateRequest,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    user_id: str = Header(..., alias="X-User-ID")
):
    """
    Generate template content using AI

    Example:
    POST /templates/generate
    {
      "template_type": "policy",
      "prompt": "Generate BCM policy for healthcare organization with 500 employees",
      "iso_clause": "5.2",
      "context": {
        "industry": "healthcare",
        "size": "medium",
        "compliance_requirements": ["HIPAA", "ISO 22301"]
      }
    }

    Returns: AI-generated template content
    """
    # TODO: Integrate with AI Orchestration service (port 8002)

    return {
        "message": "AI generation in progress",
        "template_type": request.template_type,
        "estimated_time": "30-60 seconds",
        "note": "AI integration requires AI Orchestration service (port 8002)"
    }


@router.get("/templates/bpmn/{workflow_type}")
async def get_bpmn_workflow(
    workflow_type: str,
    tenant_id: str = Header(..., alias="X-Tenant-ID")
):
    """
    Get BPMN 2.0 workflow template

    Workflow types:
    - tabletop_exercise
    - functional_exercise
    - full_scale_exercise
    - incident_response
    - compliance_audit
    - risk_assessment
    """
    # Example: return tabletop exercise BPMN
    if workflow_type == "tabletop_exercise":
        # This would come from templates/data/bpmn_workflow_templates.xml
        return {
            "workflow_type": "tabletop_exercise",
            "name": "Tabletop Exercise Workflow",
            "description": "Standard BPMN workflow for tabletop exercises with discussion phases",
            "iso_clause": "8.5",
            "bpmn_xml": """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL">
  <process id="tabletop_exercise" name="Tabletop Exercise Workflow">
    <startEvent id="exercise_start" name="Exercise Started"/>
    <userTask id="participant_briefing" name="Participant Briefing"/>
    <userTask id="scenario_presentation" name="Present Scenario"/>
    <userTask id="discussion_phase" name="Discussion Phase"/>
    <userTask id="decision_making" name="Decision Making"/>
    <userTask id="exercise_evaluation" name="Exercise Evaluation"/>
    <serviceTask id="generate_report" name="Generate Exercise Report"/>
    <endEvent id="exercise_complete" name="Exercise Completed"/>
  </process>
</definitions>""",
            "needs_simulation": False,
            "usage_count": 28
        }

    raise HTTPException(status_code=404, detail=f"BPMN workflow {workflow_type} not found")


@router.post("/templates/{template_id}/verify")
async def verify_template_integrity(
    template_id: str,
    tenant_id: str = Header(..., alias="X-Tenant-ID")
):
    """
    Verify template integrity

    Checks:
    - BPMN XML is valid
    - Form schema is valid JSON
    - Required variables are defined
    - ISO clause mapping is correct
    """
    # TODO: Implement verification logic

    return {
        "template_id": template_id,
        "verification_status": "valid",
        "checks": {
            "xml_valid": True,
            "schema_valid": True,
            "variables_defined": True,
            "iso_mapping_correct": True
        }
    }


@router.get("/templates/{template_id}/usage-stats")
async def get_template_usage_stats(
    template_id: str,
    tenant_id: str = Header(..., alias="X-Tenant-ID")
):
    """
    Get usage statistics for template

    Returns:
    - Total usage count
    - Last used date
    - Most common variables used
    - Success rate (for workflows)
    """
    # TODO: Implement stats query

    return {
        "template_id": template_id,
        "usage_count": 45,
        "last_used": "2025-10-01T15:30:00Z",
        "avg_rendering_time_ms": 250,
        "common_variables": [
            {"variable": "organization_name", "usage": 45},
            {"variable": "scope_statement", "usage": 43},
            {"variable": "leadership_commitment", "usage": 40}
        ]
    }
