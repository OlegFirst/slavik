"""
BIA Report Template Generator

Provides:
- Business Impact Analysis report template (ISO 22301 Clause 8.2.2)
"""

from ..models import DocumentTemplate, DocumentSection


def create_bia_report_template() -> DocumentTemplate:
    """Создать шаблон отчета BIA"""
    template = DocumentTemplate(
        id="bia_report_v1",
        name="Business Impact Analysis Report",
        version="1.0",
        description="Стандартный отчет BIA в соответствии с ISO 22301",
        document_type="bia_report",
        iso_clause="8.2.2",
        required_variables=[
            "organization_name",
            "analysis_date",
            "prepared_by",
            "scope",
            "critical_functions",
            "rto_summary",
            "rpo_summary",
            "impact_analysis"
        ]
    )

    # Header
    template.header_template = """
# BUSINESS IMPACT ANALYSIS REPORT

**Organization:** {{organization_name}}
**Date:** {{analysis_date}}
**Prepared by:** {{prepared_by}}
**Version:** 1.0
**Status:** {{status}}

---

**Document Control:**
- Confidentiality: {{confidentiality_level}}
- Distribution: {{distribution_list}}
- Review Date: {{review_date}}

---
"""

    # Section 1: Executive Summary
    section1 = DocumentSection(
        id="executive_summary",
        title="1. Executive Summary",
        content_template="""
This Business Impact Analysis was conducted to identify critical business functions,
assess the potential impact of disruptions, and determine recovery objectives.

**Key Findings:**
{{key_findings}}

**Critical Functions Identified:** {{critical_functions_count}}

**Average RTO:** {{average_rto}} hours
**Average RPO:** {{average_rpo}} minutes
""",
        required=True,
        order=1
    )

    # Section 2: Scope and Objectives
    section2 = DocumentSection(
        id="scope_objectives",
        title="2. Scope and Objectives",
        content_template="""
### 2.1 Scope

{{scope}}

### 2.2 Objectives

The objectives of this BIA are:
{{objectives}}

### 2.3 Methodology

{{methodology}}
""",
        required=True,
        order=2
    )

    # Section 3: Critical Functions
    section3 = DocumentSection(
        id="critical_functions",
        title="3. Critical Business Functions",
        content_template="""
The following critical business functions have been identified:

{{critical_functions}}

### 3.1 Function Dependencies

{{function_dependencies}}
""",
        required=True,
        order=3,
        min_length=200
    )

    # Section 4: Impact Analysis
    section4 = DocumentSection(
        id="impact_analysis",
        title="4. Impact Analysis",
        content_template="""
### 4.1 Recovery Time Objectives (RTO)

{{rto_summary}}

### 4.2 Recovery Point Objectives (RPO)

{{rpo_summary}}

### 4.3 Financial Impact

{{financial_impact}}

### 4.4 Reputational Impact

{{reputational_impact}}

### 4.5 Regulatory Impact

{{regulatory_impact}}

### 4.6 Overall Impact Assessment

{{impact_assessment}}
""",
        required=True,
        order=4
    )

    # Section 5: Resource Requirements
    section5 = DocumentSection(
        id="resource_requirements",
        title="5. Resource Requirements",
        content_template="""
### 5.1 Personnel

{{personnel_requirements}}

### 5.2 Technology

{{technology_requirements}}

### 5.3 Facilities

{{facilities_requirements}}

### 5.4 Third-Party Dependencies

{{third_party_dependencies}}
""",
        required=True,
        order=5
    )

    # Section 6: Recommendations
    section6 = DocumentSection(
        id="recommendations",
        title="6. Recommendations",
        content_template="""
Based on this analysis, the following recommendations are made:

{{recommendations}}

### 6.1 Priority Actions

{{priority_actions}}

### 6.2 Resource Allocation

{{resource_allocation_recommendations}}
""",
        required=True,
        order=6
    )

    # Section 7: Approval
    section7 = DocumentSection(
        id="approval",
        title="7. Approval",
        content_template="""
This Business Impact Analysis has been reviewed and approved by:

**Name:** {{approver_name}}
**Position:** {{approver_position}}
**Date:** {{approval_date}}
**Signature:** _________________________

**Comments:**
{{approval_comments}}
""",
        required=True,
        order=7
    )

    # Footer
    template.footer_template = """
---

**Document Information:**
- Template: BIA Report v1.0
- Generated: {{generation_timestamp}}
- ISO 22301:2019 Clause 8.2.2 Compliant
- Confidentiality: Internal Use Only

**Next Review Date:** {{next_review_date}}
"""

    # Добавить секции
    template.add_section(section1)
    template.add_section(section2)
    template.add_section(section3)
    template.add_section(section4)
    template.add_section(section5)
    template.add_section(section6)
    template.add_section(section7)

    return template
