"""
Workflow ML Subsystem
=====================

Machine Learning subsystem specific to workflow intelligence domain.

This is an EXAMPLE implementation showing how each module should
have its own ML subsystem with domain-specific logic.

Domain: workflow
Capabilities:
- Workflow duration prediction
- Bottleneck detection
- Task priority optimization
- Process efficiency analysis

Legacy:
- CrossModuleLearning (deprecated, use WorkflowMLSubsystem)
"""

from .workflow_ml_subsystem import WorkflowMLSubsystem

# Legacy import - will be deprecated
try:
    from .cross_module_learning import CrossModuleLearning
    __all__ = ['WorkflowMLSubsystem', 'CrossModuleLearning']
except ImportError:
    __all__ = ['WorkflowMLSubsystem']
