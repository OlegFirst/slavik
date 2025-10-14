"""
L3 System Generator

Generates test scenarios for functional systems.
Uses specialized L3 templates based on system category.
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


class L3SystemGenerator(BaseGenerator):
    """
    Generator for L3 System scenarios.

    Creates test scenarios for functional systems using specialized templates:
    - Infrastructure systems
    - Security systems
    - Reliability systems
    - AI systems
    - Operations systems
    - Intelligence systems
    - Business systems
    - Orchestration systems
    - Quality systems
    - Frontend systems
    - Infrastructure management systems
    """

    def __init__(self, template_loader, registry, output_dir: str = "generated/l3"):
        super().__init__(
            template_loader=template_loader,
            registry=registry,
            output_dir=output_dir,
            level=3
        )

    def _get_catalog(self) -> List[Dict[str, Any]]:
        """
        Get catalog of functional systems.

        Returns:
            List of 19 system definitions
        """
        return [
            # === Infrastructure Systems ===
            {
                "name": "service-mesh",
                "description": "Service-to-service communication, routing, and resilience",
                "category": "infrastructure",
                "components": ["envoy-proxy", "istio-control-plane", "circuit-breaker", "retry-policy"],
                "capabilities": [
                    "Traffic management",
                    "Service discovery",
                    "Load balancing",
                    "Circuit breaking",
                    "Mutual TLS"
                ],
                "criticality": "critical",
                "integration_points": ["all-services"]
            },
            {
                "name": "event-streaming",
                "description": "High-throughput event streaming and processing",
                "category": "infrastructure",
                "components": ["kafka-brokers", "schema-registry", "stream-processors", "connectors"],
                "capabilities": [
                    "Event ingestion",
                    "Stream processing",
                    "Event replay",
                    "Schema evolution",
                    "Dead letter queues"
                ],
                "criticality": "high",
                "integration_points": ["eventbus", "workflow-intelligence"]
            },

            # === Security Systems ===
            {
                "name": "identity-access-management",
                "description": "Authentication, authorization, and identity management",
                "category": "security",
                "components": ["auth-service", "secrets-manager", "rbac-engine", "oauth-provider"],
                "capabilities": [
                    "User authentication",
                    "Role-based access control",
                    "OAuth2/OIDC flows",
                    "Secret rotation",
                    "MFA enforcement"
                ],
                "criticality": "critical",
                "integration_points": ["api-gateway", "all-services"]
            },
            {
                "name": "threat-detection",
                "description": "Security threat detection and response",
                "category": "security",
                "components": ["ids", "log-analyzer", "anomaly-detector", "threat-intelligence"],
                "capabilities": [
                    "Intrusion detection",
                    "Anomaly detection",
                    "Threat correlation",
                    "Automated response",
                    "Security alerting"
                ],
                "criticality": "high",
                "integration_points": ["observability", "api-gateway"]
            },

            # === Reliability Systems ===
            {
                "name": "disaster-recovery",
                "description": "Backup, restore, and disaster recovery",
                "category": "reliability",
                "components": ["backup-service", "restore-manager", "replication-engine", "dr-orchestrator"],
                "capabilities": [
                    "Automated backups",
                    "Point-in-time recovery",
                    "Cross-region replication",
                    "DR testing",
                    "RTO/RPO monitoring"
                ],
                "criticality": "critical",
                "integration_points": ["postgresql", "s3", "all-stateful-services"]
            },
            {
                "name": "chaos-engineering",
                "description": "Resilience testing through controlled chaos",
                "category": "reliability",
                "components": ["chaos-controller", "fault-injector", "blast-radius-limiter", "rollback-manager"],
                "capabilities": [
                    "Fault injection",
                    "Network latency simulation",
                    "Resource exhaustion",
                    "Service failure simulation",
                    "Automated recovery"
                ],
                "criticality": "medium",
                "integration_points": ["observability", "service-mesh"]
            },

            # === AI Systems ===
            {
                "name": "llm-orchestration",
                "description": "LLM provider routing and prompt management",
                "category": "ai",
                "components": ["llm-router", "prompt-manager", "token-counter", "cost-optimizer"],
                "capabilities": [
                    "Multi-provider routing",
                    "Prompt templating",
                    "Token optimization",
                    "Cost tracking",
                    "Fallback handling"
                ],
                "criticality": "high",
                "integration_points": ["ai-orchestrator", "rag-service"]
            },
            {
                "name": "rag-pipeline",
                "description": "Retrieval-augmented generation pipeline",
                "category": "ai",
                "components": ["rag-service", "qdrant", "embedding-service", "reranker"],
                "capabilities": [
                    "Document embedding",
                    "Semantic search",
                    "Context retrieval",
                    "Answer generation",
                    "Citation tracking"
                ],
                "criticality": "high",
                "integration_points": ["knowledge-base", "llm-orchestration"]
            },

            # === Operations Systems ===
            {
                "name": "cicd-pipeline",
                "description": "Continuous integration and deployment",
                "category": "operations",
                "components": ["github-actions", "docker-registry", "k8s-deployer", "rollback-manager"],
                "capabilities": [
                    "Automated testing",
                    "Docker image building",
                    "Kubernetes deployment",
                    "Blue-green deployments",
                    "Automated rollback"
                ],
                "criticality": "high",
                "integration_points": ["github-integration", "observability"]
            },
            {
                "name": "infrastructure-as-code",
                "description": "Infrastructure provisioning and management",
                "category": "operations",
                "components": ["terraform", "ansible", "helm", "gitops-controller"],
                "capabilities": [
                    "Infrastructure provisioning",
                    "Configuration management",
                    "GitOps workflows",
                    "State management",
                    "Drift detection"
                ],
                "criticality": "high",
                "integration_points": ["cicd-pipeline", "service-discovery"]
            },

            # === Intelligence Systems ===
            {
                "name": "analytics-platform",
                "description": "Data analytics and business intelligence",
                "category": "intelligence",
                "components": ["analytics-specialist", "data-warehouse", "olap-engine", "visualization"],
                "capabilities": [
                    "Data aggregation",
                    "OLAP queries",
                    "Real-time analytics",
                    "Predictive models",
                    "Dashboard generation"
                ],
                "criticality": "medium",
                "integration_points": ["postgresql", "observability"]
            },
            {
                "name": "pattern-recognition",
                "description": "Pattern detection and anomaly identification",
                "category": "intelligence",
                "components": ["pattern-detector", "ml-models", "feature-extractor", "anomaly-scorer"],
                "capabilities": [
                    "Pattern mining",
                    "Anomaly detection",
                    "Trend analysis",
                    "Correlation discovery",
                    "Alert generation"
                ],
                "criticality": "medium",
                "integration_points": ["analytics-platform", "predictive-service"]
            },

            # === Business Systems ===
            {
                "name": "bcm-lifecycle",
                "description": "Complete BCM workflow management",
                "category": "business",
                "components": ["system-bcm-service", "bia-service", "risk-service", "strategy-service"],
                "capabilities": [
                    "BIA execution",
                    "Risk assessment",
                    "Strategy development",
                    "Plan validation",
                    "Compliance tracking"
                ],
                "criticality": "critical",
                "integration_points": ["workflow-intelligence", "document-service"]
            },
            {
                "name": "multi-tenancy",
                "description": "Organization and tenant isolation",
                "category": "business",
                "components": ["tenant-manager", "isolation-enforcer", "billing-service", "resource-quotas"],
                "capabilities": [
                    "Tenant provisioning",
                    "Data isolation",
                    "Resource quotas",
                    "Usage billing",
                    "Tenant analytics"
                ],
                "criticality": "high",
                "integration_points": ["api-gateway", "postgresql"]
            },

            # === Orchestration Systems ===
            {
                "name": "ai-agent-coordination",
                "description": "Multi-agent coordination and task distribution",
                "category": "orchestration",
                "components": ["ai-orchestrator", "mio-manager", "agent-router", "task-scheduler"],
                "capabilities": [
                    "Agent lifecycle",
                    "Task distribution",
                    "Priority management",
                    "Inter-agent communication",
                    "Performance optimization"
                ],
                "criticality": "critical",
                "integration_points": ["ai-office", "eventbus"]
            },
            {
                "name": "workflow-automation",
                "description": "Workflow definition and execution",
                "category": "orchestration",
                "components": ["workflow-engine", "temporal", "pdca-lifecycle", "state-machine"],
                "capabilities": [
                    "Workflow definition",
                    "Step execution",
                    "State management",
                    "PDCA cycles",
                    "Error handling"
                ],
                "criticality": "high",
                "integration_points": ["system-bcm", "simulation-service"]
            },

            # === Quality Systems ===
            {
                "name": "testing-framework",
                "description": "Automated testing and quality assurance",
                "category": "quality",
                "components": ["unit-tests", "integration-tests", "e2e-tests", "performance-tests"],
                "capabilities": [
                    "Unit testing",
                    "Integration testing",
                    "E2E testing",
                    "Performance testing",
                    "Test reporting"
                ],
                "criticality": "high",
                "integration_points": ["cicd-pipeline", "observability"]
            },
            {
                "name": "code-quality",
                "description": "Code quality analysis and enforcement",
                "category": "quality",
                "components": ["linters", "static-analyzers", "security-scanners", "dependency-checkers"],
                "capabilities": [
                    "Code linting",
                    "Static analysis",
                    "Security scanning",
                    "Dependency auditing",
                    "Quality gates"
                ],
                "criticality": "medium",
                "integration_points": ["cicd-pipeline", "github-integration"]
            },

            # === Frontend Systems ===
            {
                "name": "ui-component-library",
                "description": "Reusable UI components and design system",
                "category": "frontend",
                "components": ["react-components", "shadcn-ui", "tailwind", "storybook"],
                "capabilities": [
                    "Component library",
                    "Design system",
                    "Accessibility",
                    "Responsive design",
                    "Theme support"
                ],
                "criticality": "medium",
                "integration_points": ["all-web-apps"]
            }
        ]

    def _build_context(self, system: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build template context from system definition.

        Args:
            system: System definition

        Returns:
            Context for template placeholder replacement
        """
        return {
            "system_name": system["name"],
            "system_description": system["description"],
            "category": system["category"],
            "components": ", ".join(system["components"]),
            "component_count": len(system["components"]),
            "capabilities": "; ".join(system["capabilities"]),
            "criticality": system["criticality"],
            "integration_points": ", ".join(system["integration_points"])
        }

    def _get_template_name(self, system: Dict[str, Any]) -> str:
        """
        Get template name for system based on category.

        Args:
            system: System definition

        Returns:
            Template filename (specialized by category)
        """
        category = system.get("category", "general")

        # Map categories to specialized templates
        template_map = {
            "infrastructure": "l3-specialized/l3_infrastructure_system.yaml",
            "security": "l3-specialized/l3_security_system.yaml",
            "reliability": "l3-specialized/l3_reliability_system.yaml",
            "ai": "l3-specialized/l3_ai_system.yaml",
            "operations": "l3-specialized/l3_operations_system.yaml",
            "intelligence": "l3-specialized/l3_intelligence_system.yaml",
            "business": "l3-specialized/l3_business_system.yaml",
            "orchestration": "l3-specialized/l3_orchestration_system.yaml",
            "quality": "l3-specialized/l3_quality_system.yaml",
            "frontend": "l3-specialized/l3_frontend_system.yaml",
            "infrastructure_management": "l3-specialized/l3_infrastructure_management_system.yaml"
        }

        return template_map.get(category, "golden_standard_l3.yaml")


async def main():
    """Run L3 System Generator standalone."""
    from template_loader import TemplateLoader
    from storage.registry import ScenarioRegistry

    print("="*70)
    print("L3 SYSTEM GENERATOR")
    print("="*70)

    # Initialize components
    loader = TemplateLoader(templates_dir="templates")
    registry = ScenarioRegistry()

    # Create generator
    generator = L3SystemGenerator(
        template_loader=loader,
        registry=registry,
        output_dir="generated/l3"
    )

    # Generate all scenarios
    scenario_ids = await generator.generate_all()

    # Print results
    stats = generator.get_statistics()
    print(f"\n✅ Generated {stats['generated']}/{stats['total']} system scenarios")
    print(f"📁 Saved to: generated/l3/")
    print(f"🎯 Scenario IDs: {len(scenario_ids)}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(main())
