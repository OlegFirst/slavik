"""
L2 Subsystem Generator

Generates test scenarios for platform subsystems.
Uses golden_standard_l2.yaml template.
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


class L2SubsystemGenerator(BaseGenerator):
    """
    Generator for L2 Subsystem scenarios.

    Creates test scenarios for platform subsystems:
    - AI Office
    - Gateway & Security
    - Runtime Infrastructure
    - Intelligent Core subsystems
    - BCM Modules
    - Integration Layer
    """

    def __init__(self, template_loader, registry, output_dir: str = "generated/l2"):
        super().__init__(
            template_loader=template_loader,
            registry=registry,
            output_dir=output_dir,
            level=2
        )

    def _get_catalog(self) -> List[Dict[str, Any]]:
        """
        Get catalog of subsystems.

        Returns:
            List of 12 subsystem definitions
        """
        return [
            # === AI Office (Orchestration & Coordination) ===
            {
                "name": "ai-office",
                "description": "AI agent coordination and intelligent orchestration",
                "criticality": "critical",
                "services": [
                    "mio-manager",
                    "ai-orchestrator",
                    "analytics-specialist",
                    "agent-router",
                    "ai-event-manager",
                    "devops-agent",
                    "project-agent",
                    "db-intelligence",
                    "scenario-orchestrator"
                ],
                "responsibilities": [
                    "Agent lifecycle management",
                    "Task coordination",
                    "Intelligent routing",
                    "System analytics",
                    "Workflow orchestration"
                ],
                "external_dependencies": ["postgresql", "redis", "temporal"],
                "key_integrations": ["eventbus", "service-discovery", "intelligent-core"]
            },

            # === Gateway & Security ===
            {
                "name": "gateway-security",
                "description": "API gateway, authentication, and security services",
                "criticality": "critical",
                "services": [
                    "api-gateway",
                    "auth-service",
                    "secrets-manager",
                    "rate-limiter"
                ],
                "responsibilities": [
                    "API routing and load balancing",
                    "Authentication and authorization",
                    "Secret management",
                    "Rate limiting and DDoS protection"
                ],
                "external_dependencies": ["postgresql", "redis", "vault"],
                "key_integrations": ["all-services"]
            },

            # === Runtime Infrastructure ===
            {
                "name": "runtime-infrastructure",
                "description": "Core platform runtime services",
                "criticality": "critical",
                "services": [
                    "eventbus",
                    "service-discovery",
                    "message-queue",
                    "realtime-websocket",
                    "balancer-service"
                ],
                "responsibilities": [
                    "Event choreography",
                    "Service registration and discovery",
                    "Asynchronous messaging",
                    "Real-time communication",
                    "Load balancing"
                ],
                "external_dependencies": ["redis", "rabbitmq", "consul"],
                "key_integrations": ["all-services"]
            },

            # === Observability ===
            {
                "name": "observability",
                "description": "Monitoring, metrics, and observability",
                "criticality": "high",
                "services": [
                    "prometheus",
                    "grafana",
                    "loki",
                    "tempo",
                    "alertmanager"
                ],
                "responsibilities": [
                    "Metrics collection",
                    "Log aggregation",
                    "Distributed tracing",
                    "Alerting",
                    "Visualization"
                ],
                "external_dependencies": ["postgresql", "s3"],
                "key_integrations": ["all-services"]
            },

            # === Intelligent Core - AI Foundation ===
            {
                "name": "ai-foundation",
                "description": "Core AI capabilities: LLM, RAG, Learning",
                "criticality": "high",
                "services": [
                    "llm-router",
                    "rag-service",
                    "learning-system",
                    "knowledge-base"
                ],
                "responsibilities": [
                    "LLM provider routing",
                    "RAG pipeline execution",
                    "Learning and knowledge management",
                    "Knowledge base maintenance"
                ],
                "external_dependencies": ["openai", "anthropic", "qdrant", "postgresql"],
                "key_integrations": ["ai-office", "workflow-intelligence"]
            },

            # === Intelligent Core - Community Intelligence ===
            {
                "name": "community-intelligence",
                "description": "Community contributions and collective intelligence",
                "criticality": "medium",
                "services": [
                    "community-service",
                    "collective-agents",
                    "contribution-tracking"
                ],
                "responsibilities": [
                    "Community knowledge aggregation",
                    "Contribution anonymization",
                    "Collective intelligence patterns",
                    "Reputation management"
                ],
                "external_dependencies": ["postgresql", "qdrant"],
                "key_integrations": ["learning-system", "knowledge-base"]
            },

            # === Intelligent Core - Workflow Intelligence ===
            {
                "name": "workflow-intelligence",
                "description": "Workflow execution and process intelligence",
                "criticality": "high",
                "services": [
                    "workflow-engine",
                    "pdca-lifecycle",
                    "process-analytics",
                    "simulation-service"
                ],
                "responsibilities": [
                    "Workflow orchestration",
                    "PDCA cycle management",
                    "Process analytics",
                    "Scenario simulation"
                ],
                "external_dependencies": ["temporal", "postgresql"],
                "key_integrations": ["system-bcm", "predictive-service"]
            },

            # === Intelligent Core - Predictive Intelligence ===
            {
                "name": "predictive-intelligence",
                "description": "Predictive analytics and forecasting",
                "criticality": "medium",
                "services": [
                    "predictive-service",
                    "event-intelligence"
                ],
                "responsibilities": [
                    "Risk forecasting",
                    "Impact prediction",
                    "Trend analysis",
                    "Event correlation"
                ],
                "external_dependencies": ["postgresql", "redis"],
                "key_integrations": ["workflow-intelligence", "system-bcm"]
            },

            # === BCM Modules ===
            {
                "name": "bcm-modules",
                "description": "Business Continuity Management functional modules",
                "criticality": "high",
                "services": [
                    "system-bcm-service",
                    "bia-service",
                    "risk-service",
                    "strategy-service",
                    "response-service",
                    "validation-service",
                    "document-service"
                ],
                "responsibilities": [
                    "BCM workflow coordination",
                    "Business Impact Analysis",
                    "Risk assessment",
                    "Strategy planning",
                    "Incident response",
                    "Validation and testing",
                    "Document management"
                ],
                "external_dependencies": ["postgresql", "s3"],
                "key_integrations": ["workflow-intelligence", "ai-foundation"]
            },

            # === Governance & Compliance ===
            {
                "name": "governance-compliance",
                "description": "Governance, audit, and compliance management",
                "criticality": "high",
                "services": [
                    "governance-service",
                    "audit-service",
                    "compliance-tracking"
                ],
                "responsibilities": [
                    "Policy management",
                    "Audit trail",
                    "Compliance verification",
                    "Regulatory reporting"
                ],
                "external_dependencies": ["postgresql"],
                "key_integrations": ["bcm-modules", "document-service"]
            },

            # === Integration Layer ===
            {
                "name": "integration-layer",
                "description": "External integrations and connectors",
                "criticality": "medium",
                "services": [
                    "mcp-server",
                    "github-integration",
                    "slack-integration",
                    "email-service"
                ],
                "responsibilities": [
                    "MCP protocol integration",
                    "GitHub connectivity",
                    "Communication channels",
                    "External API connectors"
                ],
                "external_dependencies": ["github", "slack", "smtp"],
                "key_integrations": ["ai-office", "notification-service"]
            },

            # === User Interface Layer ===
            {
                "name": "interface-layer",
                "description": "Web interfaces and UI services",
                "criticality": "high",
                "services": [
                    "bcm-workspace",
                    "admin-control-center",
                    "executive-dashboard",
                    "learning-portal"
                ],
                "responsibilities": [
                    "User interaction",
                    "Data visualization",
                    "Form management",
                    "Real-time updates"
                ],
                "external_dependencies": ["cdn"],
                "key_integrations": ["api-gateway", "realtime-websocket"]
            }
        ]

    def _build_context(self, subsystem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build template context from subsystem definition.

        Args:
            subsystem: Subsystem definition

        Returns:
            Context for template placeholder replacement
        """
        return {
            "subsystem_name": subsystem["name"],
            "subsystem_description": subsystem["description"],
            "criticality": subsystem["criticality"],
            "services": ", ".join(subsystem["services"]),
            "service_count": len(subsystem["services"]),
            "responsibilities": "; ".join(subsystem["responsibilities"]),
            "external_dependencies": ", ".join(subsystem["external_dependencies"]),
            "key_integrations": ", ".join(subsystem["key_integrations"])
        }

    def _get_template_name(self, item: Dict[str, Any]) -> str:
        """
        Get template name for subsystem.

        Args:
            item: Subsystem definition

        Returns:
            Template filename
        """
        return "golden_standard_l2.yaml"


async def main():
    """Run L2 Subsystem Generator standalone."""
    from template_loader import TemplateLoader
    from storage.registry import ScenarioRegistry

    print("="*70)
    print("L2 SUBSYSTEM GENERATOR")
    print("="*70)

    # Initialize components
    loader = TemplateLoader(templates_dir="templates")
    registry = ScenarioRegistry()

    # Create generator
    generator = L2SubsystemGenerator(
        template_loader=loader,
        registry=registry,
        output_dir="generated/l2"
    )

    # Generate all scenarios
    scenario_ids = await generator.generate_all()

    # Print results
    stats = generator.get_statistics()
    print(f"\n✅ Generated {stats['generated']}/{stats['total']} subsystem scenarios")
    print(f"📁 Saved to: generated/l2/")
    print(f"🎯 Scenario IDs: {len(scenario_ids)}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(main())
