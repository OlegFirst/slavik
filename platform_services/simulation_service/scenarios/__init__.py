"""
BCM Scenario Management

Scenario templates, generators, and library for BCM exercises.
"""

from .templates import (
    get_template,
    list_templates,
    AVAILABLE_TEMPLATES
)

__all__ = [
    "get_template",
    "list_templates",
    "AVAILABLE_TEMPLATES",
]
