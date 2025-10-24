"""
Document Template Generators

Provides factory functions for creating standard document templates:
- BIA Report Template
- Risk Register Template
- Business Continuity Plan Template
"""

from .bia_template import create_bia_report_template
from .risk_template import create_risk_register_template
from .bc_plan_template import create_bc_plan_template

__all__ = [
    "create_bia_report_template",
    "create_risk_register_template",
    "create_bc_plan_template"
]
