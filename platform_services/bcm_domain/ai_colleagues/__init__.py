"""
BCM AI Colleagues
=================

Intelligent AI assistants specialized in Business Continuity Management.

This package provides 9 BCM AI colleagues:
- BIA Specialist: RTO/RPO determination, impact assessment
- Risk Analyst: Risk identification, threat assessment
- Compliance Copilot: ISO 22301 compliance, gap analysis
- Exercise Designer: BC exercise planning, scenario design
- Incident Advisor: Incident response, recovery coordination
- Plan Generator: BC plan creation, procedure development
- Project Manager: BCM project management, task coordination
- Project Intelligence: Project analytics, status reporting

Architecture:
    All colleagues extend BaseAIColleague and use:
    - RAG Pipeline from ai_foundation
    - LLM Router for text generation
    - Intent Analyzer for query understanding
    - Colleague Coordinator for routing

Example:
    ```python
    from platform_services.bcm_domain.ai_colleagues import (
        BIASpecialistAI,
        RiskAnalystAI,
        ColleagueCoordinator
    )
    from intelligent_core.ai_foundation import RAGPipeline

    # Initialize colleagues
    rag = RAGPipeline(config={...})
    bia_ai = BIASpecialistAI(rag_pipeline=rag, config={...})
    risk_ai = RiskAnalystAI(rag_pipeline=rag, config={...})

    # Use coordinator for auto-routing
    coordinator = ColleagueCoordinator(
        rag_pipeline=rag,
        colleagues={
            "bia_specialist": bia_ai,
            "risk_analyst": risk_ai,
        }
    )

    # Auto-routes to appropriate colleague
    response = await coordinator.process_query(
        "What should be the RTO for payment processing?"
    )
    # Routes to BIA Specialist automatically
    ```

Migration Note:
    Migrated from: intelligent_core/expertise_center/ai_office/ВСМ-colleagues/
    New location: platform_services/bcm_domain/ai_colleagues/
"""

# Base classes
from .base.base_colleague import BaseAIColleague, AssistantContext, AssistantMessage

# AI Colleagues
from .bia_specialist.bia_specialist import BIASpecialistAI
from .risk_analyst.risk_analyst import RiskAnalystAI
from .compliance_copilot.compliance_copilot import ComplianceCopilot
from .exercise_designer.exercise_designer import ExerciseDesignerAI
from .incident_advisor.incident_advisor import IncidentAdvisorAI
from .plan_generator.plan_generator import PlanGeneratorAI
from .project_manager.project_manager import ProjectManagerAI
from .project_intelligence.main import ProjectIntelligenceAI

# Coordinator
from .coordinator.colleague_coordinator import ColleagueCoordinator, ColleagueType

__all__ = [
    # Base classes
    "BaseAIColleague",
    "AssistantContext",
    "AssistantMessage",

    # AI Colleagues
    "BIASpecialistAI",
    "RiskAnalystAI",
    "ComplianceCopilot",
    "ExerciseDesignerAI",
    "IncidentAdvisorAI",
    "PlanGeneratorAI",
    "ProjectManagerAI",
    "ProjectIntelligenceAI",

    # Coordinator
    "ColleagueCoordinator",
    "ColleagueType",
]

# Version info
__version__ = "1.0.0"
__bcm_colleagues_count__ = 8
