"""
Workflow Definitions

Standard workflow definitions for:
- Business Continuity Management (BCM) processes
- Governance workflows
- Compliance workflows
"""

from .bcm_processes import (
    create_bia_process,
    create_risk_assessment_process,
    create_bc_plan_process,
    register_all_bcm_processes
)

__all__ = [
    "create_bia_process",
    "create_risk_assessment_process",
    "create_bc_plan_process",
    "register_all_bcm_processes"
]
