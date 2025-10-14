"""
Templates Module - BCM Compliance Service

Ported from: /services/SERVICES/bcm_templates (Odoo module)
Date: 2025-10-02

Provides document templates, BPMN workflows, and AI-powered content generation.
"""

from .models import (
    Template,
    TemplateCategory,
    TemplateType,
    BPMNWorkflow
)

__all__ = [
    "Template",
    "TemplateCategory",
    "TemplateType",
    "BPMNWorkflow"
]
