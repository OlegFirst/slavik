"""
BCM Domain Package
==================

Business Continuity Management domain for ISO 22301:2019 compliance.

This package consolidates all BCM-related functionality:
- Services: 12 BCM platform services
- AI Colleagues: 9 BCM AI assistants
- Knowledge: ISO 22301, BCI GPG, scenarios
- Workflows: BCM-specific process definitions
- Knowledge Quality Manager: Intelligent knowledge management

Architecture:
    bcm_domain/
    ├── services/           # BCM Platform Services (12 services)  MIGRATED
    ├── ai_colleagues/      # BCM AI Colleagues (9 assistants)  MIGRATED
    ├── knowledge/          # BCM Knowledge Base
    ├── workflows/          # BCM Workflow Definitions
    └── knowledge_quality_manager/  # Knowledge QA  MIGRATED

Integration:
    - Uses intelligent_core/ai_foundation for RAG, LLM, ML
    - Uses intelligent_core/workflow_intelligence for workflow engine
    - Uses infrastructure/eventbus for event choreography
    - Uses infrastructure/decision_center for governance

Example:
    ```python
    from platform_services.bcm_domain.ai_colleagues import BIASpecialistAI
    from platform_services.bcm_domain.services import SERVICES

    # Use BIA AI Colleague
    bia_ai = BIASpecialistAI(rag_pipeline=rag, config=config)
    response = await bia_ai.process_message("Help me determine RTO for critical process")

    # Access service metadata
    bia_service_info = SERVICES["bia_service"]
    print(f"BIA Service: {bia_service_info['name']} on port {bia_service_info['port']}")
    ```

Migration Status:
     Phase 1-3: Structure & AI Colleagues (COMPLETE)
     Phase 4: Services Migration (COMPLETE)
     Phase 5: KQM Migration (COMPLETE)
    ⏳ Phase 6: Cleanup (In Progress)

    This package consolidates functionality previously scattered across:
    - intelligent_core/expertise_center/ai_office/ВСМ-colleagues/ → ai_colleagues/
    - platform_services/bia_service → services/bia_service/
    - platform_services/AI_services_management → knowledge_quality_manager/

Version: 2.0.0 (Post-Migration)
ISO Compliance: ISO 22301:2019
Status: Production Ready
"""

__version__ = "2.0.0"
__iso_compliance__ = "ISO 22301:2019"

# Domain metadata
DOMAIN_NAME = "bcm"
DOMAIN_TITLE = "Business Continuity Management"
DOMAIN_STANDARDS = ["ISO 22301:2019", "ISO 22313:2020", "BCI GPG 2018"]

# Import key components for easy access
from .services import SERVICES
from .ai_colleagues import (
    BIASpecialistAI,
    RiskAnalystAI,
    ComplianceCopilot,
    ExerciseDesignerAI,
    IncidentAdvisorAI,
    PlanGeneratorAI,
    ProjectManagerAI,
    ProjectIntelligenceAI,
    ColleagueCoordinator,
)

__all__ = [
    # Metadata
    "DOMAIN_NAME",
    "DOMAIN_TITLE",
    "DOMAIN_STANDARDS",

    # Services
    "SERVICES",

    # AI Colleagues
    "BIASpecialistAI",
    "RiskAnalystAI",
    "ComplianceCopilot",
    "ExerciseDesignerAI",
    "IncidentAdvisorAI",
    "PlanGeneratorAI",
    "ProjectManagerAI",
    "ProjectIntelligenceAI",
    "ColleagueCoordinator",
]

# Migration complete banner
print("""
╔═══════════════════════════════════════════════════════════════╗
║                    BCM DOMAIN v2.0.0                          ║
║            Business Continuity Management Package              ║
╠═══════════════════════════════════════════════════════════════╣
║   12 Services Migrated                                      ║
║   9 AI Colleagues Migrated                                  ║
║   Knowledge Quality Manager Migrated                        ║
║   ISO 22301:2019 Compliant                                  ║
╚═══════════════════════════════════════════════════════════════╝
""")
