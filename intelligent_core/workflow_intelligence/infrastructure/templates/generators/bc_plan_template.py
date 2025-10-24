"""
Business Continuity Plan Template Generator

Provides:
- BC Plan template (ISO 22301 Clause 8.4)
"""

from ..models import DocumentTemplate, DocumentSection


def create_bc_plan_template() -> DocumentTemplate:
    """Создать шаблон Business Continuity Plan"""
    template = DocumentTemplate(
        id="bc_plan_v1",
        name="Business Continuity Plan",
        version="1.0",
        description="План обеспечения непрерывности бизнеса",
        document_type="bc_plan",
        iso_clause="8.4",
        required_variables=[
            "organization_name",
            "plan_date",
            "scope",
            "critical_functions",
            "recovery_strategies",
            "roles_responsibilities",
            "contact_list",
            "recovery_procedures"
        ]
    )

    template.header_template = """
# BUSINESS CONTINUITY PLAN

**Organization:** {{organization_name}}
**Date:** {{plan_date}}
**Version:** {{version}}
**Status:** {{status}}

---

**Plan Owner:** {{plan_owner}}
**Review Frequency:** {{review_frequency}}
**Last Updated:** {{last_updated}}

---
"""

    # Sections
    sections = [
        DocumentSection(
            id="introduction",
            title="1. Introduction",
            content_template="{{introduction}}",
            order=1
        ),
        DocumentSection(
            id="scope",
            title="2. Scope",
            content_template="{{scope}}",
            order=2
        ),
        DocumentSection(
            id="critical_functions",
            title="3. Critical Business Functions",
            content_template="{{critical_functions}}",
            order=3
        ),
        DocumentSection(
            id="recovery_strategies",
            title="4. Recovery Strategies",
            content_template="{{recovery_strategies}}",
            order=4
        ),
        DocumentSection(
            id="roles",
            title="5. Roles and Responsibilities",
            content_template="""
### 5.1 Incident Management Team

{{incident_management_team}}

### 5.2 Recovery Teams

{{recovery_teams}}

### 5.3 Contact List

{{contact_list}}
""",
            order=5
        ),
        DocumentSection(
            id="procedures",
            title="6. Recovery Procedures",
            content_template="{{recovery_procedures}}",
            order=6
        ),
        DocumentSection(
            id="communication",
            title="7. Communication Plan",
            content_template="{{communication_plan}}",
            order=7
        ),
        DocumentSection(
            id="testing",
            title="8. Testing and Maintenance",
            content_template="""
### 8.1 Testing Schedule

{{testing_schedule}}

### 8.2 Plan Maintenance

{{plan_maintenance}}
""",
            order=8
        )
    ]

    for section in sections:
        template.add_section(section)

    return template
