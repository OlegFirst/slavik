"""
L1 Application Generator

Generates test scenarios for user-facing applications.
Uses golden_standard_l1_application.yaml template.
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any
import sys

# Add intelligent-core to path for templates/storage
intelligent_core_path = Path(__file__).parent.parent.parent.parent.parent / "intelligent-core" / "scenario-intelligence"
sys.path.insert(0, str(intelligent_core_path))

from generators.base_generator import BaseGenerator

logger = logging.getLogger(__name__)


class L1ApplicationGenerator(BaseGenerator):
    """
    Generator for L1 Application scenarios.

    Creates test scenarios for all user-facing applications:
    - Web interfaces
    - Admin tools
    - Specialist workspaces
    - Mobile apps
    """

    def __init__(self, template_loader, registry, output_dir: str = "generated/l1/applications"):
        super().__init__(
            template_loader=template_loader,
            registry=registry,
            output_dir=output_dir,
            level=1
        )

    def _get_catalog(self) -> List[Dict[str, Any]]:
        """
        Get catalog of user applications.

        Returns:
            List of 16 application definitions
        """
        return [
            # === BCM Professional Applications ===
            {
                "name": "bcm-workspace",
                "type": "web_application",
                "user_role": "bcm_specialist",
                "criticality": "high",
                "subsystem": "interface",
                "features": [
                    "bia_creation",
                    "risk_assessment",
                    "strategy_planning",
                    "document_management",
                    "compliance_tracking"
                ],
                "integrations": ["system-bcm-service", "document-service", "validation-service"],
                "auth_methods": ["jwt", "oauth2"],
                "supported_platforms": ["web", "tablet"]
            },
            {
                "name": "auditor-toolkit",
                "type": "web_application",
                "user_role": "auditor",
                "criticality": "high",
                "subsystem": "interface",
                "features": [
                    "audit_planning",
                    "evidence_collection",
                    "compliance_verification",
                    "report_generation",
                    "finding_tracking"
                ],
                "integrations": ["governance-service", "document-service", "validation-service"],
                "auth_methods": ["jwt", "mfa"],
                "supported_platforms": ["web", "desktop"]
            },
            {
                "name": "consultant-platform",
                "type": "web_application",
                "user_role": "consultant",
                "criticality": "medium",
                "subsystem": "interface",
                "features": [
                    "multi_client_management",
                    "template_customization",
                    "white_label_branding",
                    "client_reporting",
                    "knowledge_sharing"
                ],
                "integrations": ["system-bcm-service", "learning-system", "document-service"],
                "auth_methods": ["jwt", "saml"],
                "supported_platforms": ["web"]
            },
            {
                "name": "executive-dashboard",
                "type": "web_application",
                "user_role": "executive",
                "criticality": "high",
                "subsystem": "interface",
                "features": [
                    "executive_summary",
                    "kpi_visualization",
                    "risk_overview",
                    "compliance_status",
                    "strategic_insights"
                ],
                "integrations": ["analytics-specialist", "system-bcm-service", "predictive-service"],
                "auth_methods": ["jwt", "sso"],
                "supported_platforms": ["web", "mobile", "tablet"]
            },

            # === Administrative Applications ===
            {
                "name": "admin-control-center",
                "type": "web_application",
                "user_role": "platform_admin",
                "criticality": "critical",
                "subsystem": "interface",
                "features": [
                    "user_management",
                    "organization_setup",
                    "system_configuration",
                    "service_monitoring",
                    "infrastructure_control"
                ],
                "integrations": ["api-gateway", "mio-manager", "service-discovery", "analytics-specialist"],
                "auth_methods": ["jwt", "mfa", "totp"],
                "supported_platforms": ["web", "desktop"]
            },
            {
                "name": "ai-office-control",
                "type": "web_application",
                "user_role": "ai_operator",
                "criticality": "high",
                "subsystem": "ai_office",
                "features": [
                    "agent_monitoring",
                    "task_coordination",
                    "performance_metrics",
                    "agent_configuration",
                    "workflow_management"
                ],
                "integrations": ["mio-manager", "ai-orchestrator", "analytics-specialist"],
                "auth_methods": ["jwt", "api_key"],
                "supported_platforms": ["web"]
            },

            # === Learning & Knowledge Applications ===
            {
                "name": "learning-portal",
                "type": "web_application",
                "user_role": "learner",
                "criticality": "medium",
                "subsystem": "intelligent_core",
                "features": [
                    "course_catalog",
                    "interactive_training",
                    "competency_tracking",
                    "certification_management",
                    "gamification"
                ],
                "integrations": ["learning-system", "knowledge-base", "community-intelligence"],
                "auth_methods": ["jwt", "oauth2"],
                "supported_platforms": ["web", "mobile"]
            },
            {
                "name": "knowledge-base-ui",
                "type": "web_application",
                "user_role": "knowledge_worker",
                "criticality": "medium",
                "subsystem": "intelligent_core",
                "features": [
                    "document_search",
                    "rag_assistant",
                    "case_library",
                    "best_practices",
                    "regulatory_guides"
                ],
                "integrations": ["knowledge-base", "rag-service", "document-service"],
                "auth_methods": ["jwt"],
                "supported_platforms": ["web"]
            },

            # === Community & Collaboration Applications ===
            {
                "name": "community-hub",
                "type": "web_application",
                "user_role": "community_member",
                "criticality": "low",
                "subsystem": "community",
                "features": [
                    "discussion_forums",
                    "knowledge_sharing",
                    "peer_support",
                    "contribution_tracking",
                    "reputation_system"
                ],
                "integrations": ["community-intelligence", "learning-system"],
                "auth_methods": ["jwt", "oauth2", "anonymous"],
                "supported_platforms": ["web", "mobile"]
            },
            {
                "name": "collaboration-workspace",
                "type": "web_application",
                "user_role": "team_member",
                "criticality": "medium",
                "subsystem": "interface",
                "features": [
                    "real_time_collaboration",
                    "document_co_editing",
                    "task_management",
                    "team_communication",
                    "version_control"
                ],
                "integrations": ["document-service", "realtime-websocket", "notification-service"],
                "auth_methods": ["jwt"],
                "supported_platforms": ["web", "desktop"]
            },

            # === Specialized Tools ===
            {
                "name": "scenario-simulator",
                "type": "web_application",
                "user_role": "bcm_specialist",
                "criticality": "medium",
                "subsystem": "intelligent_core",
                "features": [
                    "scenario_creation",
                    "simulation_execution",
                    "impact_analysis",
                    "results_visualization",
                    "report_generation"
                ],
                "integrations": ["simulation-service", "predictive-service", "analytics-specialist"],
                "auth_methods": ["jwt"],
                "supported_platforms": ["web"]
            },
            {
                "name": "response-coordinator",
                "type": "web_application",
                "user_role": "incident_manager",
                "criticality": "critical",
                "subsystem": "bcm_modules",
                "features": [
                    "incident_declaration",
                    "team_activation",
                    "communication_management",
                    "action_tracking",
                    "status_reporting"
                ],
                "integrations": ["response-service", "notification-service", "realtime-websocket"],
                "auth_methods": ["jwt", "mfa"],
                "supported_platforms": ["web", "mobile"]
            },

            # === Integration & Developer Tools ===
            {
                "name": "developer-portal",
                "type": "web_application",
                "user_role": "developer",
                "criticality": "medium",
                "subsystem": "interface",
                "features": [
                    "api_documentation",
                    "api_testing",
                    "sdk_downloads",
                    "integration_guides",
                    "webhook_management"
                ],
                "integrations": ["api-gateway", "mcp-server", "github-integration"],
                "auth_methods": ["jwt", "api_key", "oauth2"],
                "supported_platforms": ["web"]
            },
            {
                "name": "integration-studio",
                "type": "web_application",
                "user_role": "integration_specialist",
                "criticality": "medium",
                "subsystem": "integration",
                "features": [
                    "connector_configuration",
                    "data_mapping",
                    "transformation_rules",
                    "sync_monitoring",
                    "error_handling"
                ],
                "integrations": ["api-gateway", "mcp-server", "eventbus"],
                "auth_methods": ["jwt", "api_key"],
                "supported_platforms": ["web"]
            },

            # === Mobile Applications ===
            {
                "name": "bcm-mobile",
                "type": "mobile_application",
                "user_role": "field_user",
                "criticality": "medium",
                "subsystem": "interface",
                "features": [
                    "offline_mode",
                    "quick_assessments",
                    "photo_documentation",
                    "push_notifications",
                    "location_tracking"
                ],
                "integrations": ["api-gateway", "document-service", "notification-service"],
                "auth_methods": ["jwt", "biometric"],
                "supported_platforms": ["ios", "android"]
            },
            {
                "name": "incident-responder-mobile",
                "type": "mobile_application",
                "user_role": "first_responder",
                "criticality": "high",
                "subsystem": "bcm_modules",
                "features": [
                    "emergency_alerts",
                    "quick_actions",
                    "team_communication",
                    "status_updates",
                    "offline_procedures"
                ],
                "integrations": ["response-service", "notification-service", "realtime-websocket"],
                "auth_methods": ["jwt", "pin", "biometric"],
                "supported_platforms": ["ios", "android"]
            }
        ]

    def _build_context(self, app: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build template context from application definition.

        Args:
            app: Application definition

        Returns:
            Context for template placeholder replacement
        """
        return {
            "application_name": app["name"],
            "application_type": app["type"],
            "user_role": app["user_role"],
            "criticality": app["criticality"],
            "subsystem_name": app["subsystem"],
            "features": ", ".join(app["features"]),
            "integrations": ", ".join(app["integrations"]),
            "auth_methods": ", ".join(app["auth_methods"]),
            "platforms": ", ".join(app["supported_platforms"]),
            "feature_count": len(app["features"]),
            "integration_count": len(app["integrations"])
        }

    def _get_template_name(self, item: Dict[str, Any]) -> str:
        """
        Get template name for application.

        Args:
            item: Application definition

        Returns:
            Template filename
        """
        return "golden_standard_l1_application.yaml"


async def main():
    """Run L1 Application Generator standalone."""
    from template_loader import TemplateLoader
    from storage.registry import ScenarioRegistry

    print("="*70)
    print("L1 APPLICATION GENERATOR")
    print("="*70)

    # Initialize components
    loader = TemplateLoader(templates_dir="templates")
    registry = ScenarioRegistry()

    # Create generator
    generator = L1ApplicationGenerator(
        template_loader=loader,
        registry=registry,
        output_dir="generated/l1/applications"
    )

    # Generate all scenarios
    scenario_ids = await generator.generate_all()

    # Print results
    stats = generator.get_statistics()
    print(f"\n✅ Generated {stats['generated']}/{stats['total']} application scenarios")
    print(f"📁 Saved to: generated/l1/applications/")
    print(f"🎯 Scenario IDs: {len(scenario_ids)}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(main())
