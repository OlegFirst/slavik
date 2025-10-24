"""
Risk Register Template Generator

Provides:
- Risk Register template (ISO 22301 Clause 8.2.3)
"""

from ..models import DocumentTemplate, DocumentSection


def create_risk_register_template() -> DocumentTemplate:
    """Создать шаблон Risk Register"""
    template = DocumentTemplate(
        id="risk_register_v1",
        name="Risk Register",
        version="1.0",
        description="Реестр рисков непрерывности бизнеса",
        document_type="risk_register",
        iso_clause="8.2.3",
        required_variables=[
            "organization_name",
            "register_date",
            "risks"
        ]
    )

    template.header_template = """
# RISK REGISTER

**Organization:** {{organization_name}}
**Date:** {{register_date}}
**Version:** {{version}}

---
"""

    section1 = DocumentSection(
        id="risk_list",
        title="1. Identified Risks",
        content_template="""
{{risks}}

### Risk Matrix

| Likelihood / Impact | 1 (Low) | 2 | 3 | 4 | 5 (High) |
|---------------------|---------|---|---|---|----------|
| **5 (Almost Certain)** | {{risk_5_1}} | {{risk_5_2}} | {{risk_5_3}} | {{risk_5_4}} | {{risk_5_5}} |
| **4 (Likely)** | {{risk_4_1}} | {{risk_4_2}} | {{risk_4_3}} | {{risk_4_4}} | {{risk_4_5}} |
| **3 (Possible)** | {{risk_3_1}} | {{risk_3_2}} | {{risk_3_3}} | {{risk_3_4}} | {{risk_3_5}} |
| **2 (Unlikely)** | {{risk_2_1}} | {{risk_2_2}} | {{risk_2_3}} | {{risk_2_4}} | {{risk_2_5}} |
| **1 (Rare)** | {{risk_1_1}} | {{risk_1_2}} | {{risk_1_3}} | {{risk_1_4}} | {{risk_1_5}} |
""",
        required=True,
        order=1
    )

    section2 = DocumentSection(
        id="treatment_plan",
        title="2. Risk Treatment Plan",
        content_template="""
{{treatment_plan}}
""",
        required=True,
        order=2
    )

    template.add_section(section1)
    template.add_section(section2)

    return template
