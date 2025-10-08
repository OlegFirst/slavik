"""
Infrastructure Deployment Orchestrator
=======================================

Unified orchestration layer for infrastructure deployment:
- Service Discovery (uses tools/infrastructure/discover_services.py)
- Docker Compose Generation
- Deployment Management
- Integration with ai-orchestration

Components:
- infrastructure_orchestrator.py - Main orchestrator
- docker_compose_generator.py - Compose file generator
- infrastructure_builder.py - Build automation
"""

from pathlib import Path

__version__ = "1.0.0"

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
INFRASTRUCTURE_ROOT = PROJECT_ROOT / "infrastructure"
DEPLOYMENT_ROOT = INFRASTRUCTURE_ROOT / "deployment"
GENERATED_ROOT = DEPLOYMENT_ROOT / "generated"

# Ensure generated directory exists
GENERATED_ROOT.mkdir(parents=True, exist_ok=True)
