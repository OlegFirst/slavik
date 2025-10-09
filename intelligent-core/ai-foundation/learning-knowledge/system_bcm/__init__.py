"""
System BCM - Platform Self-Application of Business Continuity Management

This module applies BCM principles to the platform ITSELF:
- Executes BIA for platform infrastructure
- Assesses platform's own risks
- Configures auto-recovery procedures
- Manages resource priorities

The platform learns resilience through PRACTICE, not theory.
"""

from .system_bcm import (
    SystemBCM,
    execute_self_bia,
    assess_own_risks,
    setup_recovery,
    apply_priorities
)

__all__ = [
    'SystemBCM',
    'execute_self_bia',
    'assess_own_risks',
    'setup_recovery',
    'apply_priorities'
]
