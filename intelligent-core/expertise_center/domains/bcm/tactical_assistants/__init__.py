"""
BCM Tactical Assistants - AI Digital Colleagues

12 Tactical Assistants covering all platform services:
- BIA Specialist
- Risk Analyst
- Compliance Copilot
- Incident Advisor
- Plan Generator
- Project Manager
- Exercise Designer
- Documents Specialist (with living-docs integration)
- Governance Specialist
- Validation Specialist
- Community Specialist (with community intelligence integration)
- Learning Specialist (with learning system integration)
"""

from .bia_specialist import BIASpecialistAI
from .risk_analyst import RiskAnalystAI
from .compliance_copilot import ComplianceCopilotAI
from .incident_advisor import IncidentAdvisorAI
from .plan_generator import PlanGeneratorAI
from .project_manager import ProjectManagerAI
from .exercise_designer import ExerciseDesignerAI
from .documents_specialist import DocumentsSpecialistAI
from .governance_specialist import GovernanceSpecialistAI
from .validation_specialist import ValidationSpecialistAI
from .community_specialist import CommunitySpecialistAI
from .learning_specialist import LearningSpecialistAI

__all__ = [
    "BIASpecialistAI",
    "RiskAnalystAI",
    "ComplianceCopilotAI",
    "IncidentAdvisorAI",
    "PlanGeneratorAI",
    "ProjectManagerAI",
    "ExerciseDesignerAI",
    "DocumentsSpecialistAI",
    "GovernanceSpecialistAI",
    "ValidationSpecialistAI",
    "CommunitySpecialistAI",
    "LearningSpecialistAI",
]
