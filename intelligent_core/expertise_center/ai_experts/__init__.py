"""
AI Experts & ML Subsystem

Provides:
- AI Expert Agents (BCM Advisor, Compliance Auditor, Strategic Planner)
- RAG Pipeline (Knowledge retrieval + generation)
- ML Models (prediction, anomaly detection)
- Self-learning from Case Library
"""

__version__ = "1.0.0"

from .base.expert_agent import ExpertAgent
from .specialists.bcm_advisor import BCMAdvisor
from .specialists.compliance_auditor import ComplianceAuditor
from .specialists.strategic_planner import StrategicPlanner
from .ml.predictive_models import WorkflowPredictor
from .rag.pipeline import RAGPipeline

__all__ = [
    "ExpertAgent",
    "BCMAdvisor",
    "ComplianceAuditor",
    "StrategicPlanner",
    "WorkflowPredictor",
    "RAGPipeline"
]
