"""
Platform Services Catalog

Complete catalog of 46 platform services used by L1PlatformGenerator.
"""

from typing import List, Dict, Any


def get_platform_services() -> List[Dict[str, Any]]:
    """
    Get complete platform services catalog.

    Returns:
        List of 46 platform service definitions
    """
    return [
        # Infrastructure (11 services)
        {
            "name": "service-discovery",
            "port": 8500,
            "criticality": "critical",
            "subsystem": "runtime",
            "category": "infrastructure",
            "internal_dependencies": [],
            "external_dependencies": ["consul"]
        },
        {
            "name": "eventbus",
            "port": 6379,
            "criticality": "critical",
            "subsystem": "runtime",
            "category": "infrastructure",
            "internal_dependencies": ["service-discovery"],
            "external_dependencies": ["redis"]
        },
        {
            "name": "api-gateway",
            "port": 8000,
            "criticality": "critical",
            "subsystem": "gateway",
            "category": "infrastructure",
            "internal_dependencies": ["service-discovery", "auth-service"],
            "external_dependencies": []
        },
        {
            "name": "realtime-websocket",
            "port": 8080,
            "criticality": "high",
            "subsystem": "runtime",
            "category": "infrastructure",
            "internal_dependencies": ["api-gateway", "eventbus"],
            "external_dependencies": []
        },
        {
            "name": "message-queue",
            "port": 5672,
            "criticality": "high",
            "subsystem": "runtime",
            "category": "infrastructure",
            "internal_dependencies": ["service-discovery"],
            "external_dependencies": ["rabbitmq"]
        },
        {
            "name": "balancer-service",
            "port": 8010,
            "criticality": "high",
            "subsystem": "runtime",
            "category": "infrastructure",
            "internal_dependencies": ["service-discovery"],
            "external_dependencies": []
        },
        {
            "name": "infrastructure-coordinator",
            "port": 8015,
            "criticality": "critical",
            "subsystem": "runtime",
            "category": "infrastructure",
            "internal_dependencies": ["service-discovery", "eventbus"],
            "external_dependencies": []
        },
        {
            "name": "prometheus",
            "port": 9090,
            "criticality": "high",
            "subsystem": "observability",
            "category": "infrastructure",
            "internal_dependencies": [],
            "external_dependencies": []
        },
        {
            "name": "grafana",
            "port": 3000,
            "criticality": "medium",
            "subsystem": "observability",
            "category": "infrastructure",
            "internal_dependencies": ["prometheus"],
            "external_dependencies": []
        },
        {
            "name": "loki",
            "port": 3100,
            "criticality": "medium",
            "subsystem": "observability",
            "category": "infrastructure",
            "internal_dependencies": [],
            "external_dependencies": []
        },
        {
            "name": "tempo",
            "port": 3200,
            "criticality": "medium",
            "subsystem": "observability",
            "category": "infrastructure",
            "internal_dependencies": [],
            "external_dependencies": []
        },

        # Security (3 services)
        {
            "name": "secrets-manager",
            "port": 8200,
            "criticality": "critical",
            "subsystem": "security",
            "category": "security",
            "internal_dependencies": ["service-discovery"],
            "external_dependencies": ["vault"]
        },
        {
            "name": "auth-service",
            "port": 8100,
            "criticality": "critical",
            "subsystem": "security",
            "category": "security",
            "internal_dependencies": ["secrets-manager"],
            "external_dependencies": ["keycloak"]
        },
        {
            "name": "policy-engine",
            "port": 8181,
            "criticality": "high",
            "subsystem": "security",
            "category": "security",
            "internal_dependencies": ["service-discovery"],
            "external_dependencies": []
        },

        # AI Office (8 services)
        {
            "name": "mio-manager",
            "port": 8025,
            "criticality": "critical",
            "subsystem": "ai_office",
            "category": "ai",
            "internal_dependencies": ["service-discovery", "eventbus"],
            "external_dependencies": ["postgresql", "redis"]
        },
        {
            "name": "ai-orchestrator",
            "port": 8020,
            "criticality": "critical",
            "subsystem": "ai_office",
            "category": "ai",
            "internal_dependencies": ["mio-manager", "eventbus"],
            "external_dependencies": []
        },
        {
            "name": "analytics-specialist",
            "port": 8030,
            "criticality": "high",
            "subsystem": "ai_office",
            "category": "ai",
            "internal_dependencies": ["ai-orchestrator", "eventbus"],
            "external_dependencies": ["postgresql"]
        },
        {
            "name": "devops-agent",
            "port": 8035,
            "criticality": "medium",
            "subsystem": "ai_office",
            "category": "ai",
            "internal_dependencies": ["ai-orchestrator"],
            "external_dependencies": []
        },
        {
            "name": "project-agent",
            "port": 8040,
            "criticality": "medium",
            "subsystem": "ai_office",
            "category": "ai",
            "internal_dependencies": ["ai-orchestrator"],
            "external_dependencies": []
        },
        {
            "name": "agent-router",
            "port": 8045,
            "criticality": "high",
            "subsystem": "ai_office",
            "category": "ai",
            "internal_dependencies": ["ai-orchestrator"],
            "external_dependencies": []
        },
        {
            "name": "ai-event-manager",
            "port": 8050,
            "criticality": "high",
            "subsystem": "ai_office",
            "category": "ai",
            "internal_dependencies": ["eventbus"],
            "external_dependencies": ["postgresql"]
        },
        {
            "name": "db-intelligence",
            "port": 8055,
            "criticality": "medium",
            "subsystem": "ai_office",
            "category": "ai",
            "internal_dependencies": ["ai-orchestrator"],
            "external_dependencies": ["postgresql"]
        },

        # Intelligent Core (10 services)
        {
            "name": "ai-foundation",
            "port": 9000,
            "criticality": "critical",
            "subsystem": "intelligent_core",
            "category": "ai",
            "internal_dependencies": ["eventbus"],
            "external_dependencies": ["qdrant", "openai"]
        },
        {
            "name": "workflow-intelligence",
            "port": 9010,
            "criticality": "critical",
            "subsystem": "intelligent_core",
            "category": "intelligence",
            "internal_dependencies": ["ai-foundation", "eventbus"],
            "external_dependencies": ["postgresql", "temporal"]
        },
        {
            "name": "predictive-analytics",
            "port": 9020,
            "criticality": "high",
            "subsystem": "intelligent_core",
            "category": "intelligence",
            "internal_dependencies": ["ai-foundation"],
            "external_dependencies": ["postgresql"]
        },
        {
            "name": "community-intelligence",
            "port": 9030,
            "criticality": "medium",
            "subsystem": "intelligent_core",
            "category": "intelligence",
            "internal_dependencies": ["ai-foundation"],
            "external_dependencies": ["postgresql", "qdrant"]
        },
        {
            "name": "collective-intelligence",
            "port": 9040,
            "criticality": "medium",
            "subsystem": "intelligent_core",
            "category": "intelligence",
            "internal_dependencies": ["community-intelligence"],
            "external_dependencies": ["postgresql"]
        },
        {
            "name": "scenario-intelligence",
            "port": 9050,
            "criticality": "medium",
            "subsystem": "intelligent_core",
            "category": "intelligence",
            "internal_dependencies": ["ai-foundation"],
            "external_dependencies": ["postgresql", "qdrant"]
        },
        {
            "name": "learning-system",
            "port": 9060,
            "criticality": "high",
            "subsystem": "intelligent_core",
            "category": "intelligence",
            "internal_dependencies": ["ai-foundation"],
            "external_dependencies": ["postgresql"]
        },
        {
            "name": "system-bcm",
            "port": 9070,
            "criticality": "critical",
            "subsystem": "intelligent_core",
            "category": "business",
            "internal_dependencies": ["workflow-intelligence", "eventbus"],
            "external_dependencies": ["postgresql"]
        },
        {
            "name": "expertise-center",
            "port": 9080,
            "criticality": "high",
            "subsystem": "intelligent_core",
            "category": "intelligence",
            "internal_dependencies": ["ai-foundation"],
            "external_dependencies": ["postgresql"]
        },
        {
            "name": "pdca-lifecycle",
            "port": 9090,
            "criticality": "high",
            "subsystem": "intelligent_core",
            "category": "business",
            "internal_dependencies": ["workflow-intelligence"],
            "external_dependencies": ["postgresql"]
        },

        # Integration (4 services)
        {
            "name": "github-integration",
            "port": 8300,
            "criticality": "medium",
            "subsystem": "integration",
            "category": "integration",
            "internal_dependencies": ["api-gateway"],
            "external_dependencies": ["github"]
        },
        {
            "name": "mcp-server",
            "port": 8310,
            "criticality": "medium",
            "subsystem": "integration",
            "category": "integration",
            "internal_dependencies": ["api-gateway"],
            "external_dependencies": []
        },
        {
            "name": "notification-service",
            "port": 8320,
            "criticality": "high",
            "subsystem": "integration",
            "category": "integration",
            "internal_dependencies": ["eventbus"],
            "external_dependencies": ["smtp", "slack"]
        },
        {
            "name": "webhook-service",
            "port": 8330,
            "criticality": "medium",
            "subsystem": "integration",
            "category": "integration",
            "internal_dependencies": ["api-gateway"],
            "external_dependencies": []
        },
        {
            "name": "external-api-connector",
            "port": 8340,
            "criticality": "medium",
            "subsystem": "integration",
            "category": "integration",
            "internal_dependencies": ["api-gateway"],
            "external_dependencies": []
        },

        # BCM Modules (10 services)
        {
            "name": "bia-service",
            "port": 7000,
            "criticality": "high",
            "subsystem": "bcm_modules",
            "category": "business",
            "internal_dependencies": ["system-bcm"],
            "external_dependencies": ["postgresql"]
        },
        {
            "name": "risk-service",
            "port": 7010,
            "criticality": "high",
            "subsystem": "bcm_modules",
            "category": "business",
            "internal_dependencies": ["system-bcm"],
            "external_dependencies": ["postgresql"]
        },
        {
            "name": "response-service",
            "port": 7020,
            "criticality": "critical",
            "subsystem": "bcm_modules",
            "category": "business",
            "internal_dependencies": ["system-bcm", "notification-service"],
            "external_dependencies": ["postgresql"]
        },
        {
            "name": "document-service",
            "port": 7030,
            "criticality": "high",
            "subsystem": "bcm_modules",
            "category": "business",
            "internal_dependencies": ["system-bcm"],
            "external_dependencies": ["postgresql", "s3"]
        },
        {
            "name": "validation-service",
            "port": 7040,
            "criticality": "high",
            "subsystem": "bcm_modules",
            "category": "business",
            "internal_dependencies": ["system-bcm"],
            "external_dependencies": ["postgresql"]
        },
        {
            "name": "compliance-service",
            "port": 7050,
            "criticality": "high",
            "subsystem": "bcm_modules",
            "category": "business",
            "internal_dependencies": ["system-bcm"],
            "external_dependencies": ["postgresql"]
        },
        {
            "name": "audit-service",
            "port": 7060,
            "criticality": "high",
            "subsystem": "bcm_modules",
            "category": "business",
            "internal_dependencies": ["system-bcm"],
            "external_dependencies": ["postgresql"]
        },
        {
            "name": "reporting-service",
            "port": 7070,
            "criticality": "medium",
            "subsystem": "bcm_modules",
            "category": "business",
            "internal_dependencies": ["system-bcm", "document-service"],
            "external_dependencies": ["postgresql"]
        },
        {
            "name": "organization-service",
            "port": 7080,
            "criticality": "critical",
            "subsystem": "bcm_modules",
            "category": "business",
            "internal_dependencies": ["auth-service"],
            "external_dependencies": ["postgresql"]
        },
    ]
