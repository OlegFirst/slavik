"""
Document Templates Infrastructure

Exports:
- Models: DocumentSection, DocumentTemplate
- Library: DocumentTemplateLibrary, get_document_library
- Generators: create_bia_report_template, create_risk_register_template, create_bc_plan_template
"""

from .models import (
    DocumentSection,
    DocumentTemplate
)

from .library import (
    DocumentTemplateLibrary,
    get_document_library
)

from .generators import (
    create_bia_report_template,
    create_risk_register_template,
    create_bc_plan_template
)

__all__ = [
    # Models
    "DocumentSection",
    "DocumentTemplate",
    # Library
    "DocumentTemplateLibrary",
    "get_document_library",
    # Generators
    "create_bia_report_template",
    "create_risk_register_template",
    "create_bc_plan_template"
]
