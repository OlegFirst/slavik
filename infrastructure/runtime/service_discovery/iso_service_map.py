"""
ISO 22301 Service Registry Mapping

Complete mapping of all 12 BCM Platform services to ISO 22301 clauses.

Extracted from: intelligent-core/platform-orchestrator/platform_orchestrator.py
Date: 2025-10-04
"""

from typing import Dict, Any

# ISO 22301 Service Registry - ALL 12 SERVICES
ISO_SERVICE_REGISTRY: Dict[str, Dict[str, Any]] = {
    # Core BCM Services (ISO 22301)
    "planning": {
        "name": "Planning Service",
        "url": "http://localhost:8011",
        "module": "planning",
        "iso_clause": "8.3",
        "component": "bcm-strategy",
        "has_workflow_intelligence": True,
        "description": "Business Continuity Strategy & Planning"
    },
    "plans": {
        "name": "Plans Service",
        "url": "http://localhost:8023",
        "module": "plans",
        "iso_clause": "8.4",
        "component": "bcm-plans",
        "has_workflow_intelligence": True,
        "description": "Business Continuity Plans & Procedures"
    },
    "bia": {
        "name": "BIA Service",
        "url": "http://localhost:8012",
        "module": "bia",
        "iso_clause": "8.2.2",
        "component": "bcm-bia",
        "has_workflow_intelligence": True,
        "description": "Business Impact Analysis"
    },
    "compliance": {
        "name": "Compliance Service",
        "url": "http://localhost:8014",
        "module": "compliance",
        "iso_clause": "9.2, 10.1, 10.2",
        "component": "bcm-compliance",
        "has_workflow_intelligence": True,
        "description": "Compliance Audits & Improvement"
    },
    "risk": {
        "name": "Risk Service",
        "url": "http://localhost:8013",
        "module": "risk",
        "iso_clause": "8.2.3",
        "component": "bcm-risk",
        "has_workflow_intelligence": True,
        "description": "Risk Assessment & Treatment"
    },
    "response": {
        "name": "Response Service",
        "url": "http://localhost:8015",
        "module": "response",
        "iso_clause": "8.4.5",
        "component": "bcm-incident",
        "has_workflow_intelligence": True,
        "description": "Incident Response & Management"
    },
    "validation": {
        "name": "Validation Service",
        "url": "http://localhost:8016",
        "module": "validation",
        "iso_clause": "8.4.6",
        "component": "bcm-testing",
        "has_workflow_intelligence": True,
        "description": "Exercise & Testing"
    },
    "documents": {
        "name": "Documents Service",
        "url": "http://localhost:8017",
        "module": "documents",
        "iso_clause": "7.5",
        "component": "bcm-documentation",
        "has_workflow_intelligence": True,
        "description": "Document Control & Management"
    },
    "learning": {
        "name": "Learning Service",
        "url": "http://localhost:8018",
        "module": "learning",
        "iso_clause": "7.2",
        "component": "bcm-competence",
        "has_workflow_intelligence": True,
        "description": "Training & Competence"
    },
    "governance": {
        "name": "Governance Service",
        "url": "http://localhost:8019",
        "module": "governance",
        "iso_clause": "5.3, 7.1, 7.3",
        "component": "bcm-governance",
        "has_workflow_intelligence": True,
        "description": "Roles, Resources & Communication"
    },

    # Storage & Infrastructure
    "file": {
        "name": "File Service",
        "url": "http://localhost:8020",
        "module": "file",
        "iso_clause": "7.5.3",
        "component": "storage",
        "has_workflow_intelligence": False,
        "description": "File Storage & Asset Management"
    },

    # Community Services
    "portal": {
        "name": "Community Portal",
        "url": "http://localhost:8031",
        "module": "portal",
        "iso_clause": "7.4",
        "component": "bcm-communication",
        "has_workflow_intelligence": False,
        "description": "Knowledge Base & Forums"
    },
    "marketplace": {
        "name": "Community Marketplace",
        "url": "http://localhost:8032",
        "module": "marketplace",
        "iso_clause": "7.1",
        "component": "bcm-resources",
        "has_workflow_intelligence": False,
        "description": "Specialists & Project Marketplace"
    }
}


def get_services_by_component(component: str) -> Dict[str, Dict[str, Any]]:
    """Get all services for a specific component"""
    return {
        key: config
        for key, config in ISO_SERVICE_REGISTRY.items()
        if config["component"] == component
    }


def get_services_with_workflow_intelligence() -> Dict[str, Dict[str, Any]]:
    """Get all services that have Workflow Intelligence"""
    return {
        key: config
        for key, config in ISO_SERVICE_REGISTRY.items()
        if config["has_workflow_intelligence"]
    }


def get_services_by_iso_clause(clause: str) -> Dict[str, Dict[str, Any]]:
    """Get all services that implement a specific ISO clause"""
    return {
        key: config
        for key, config in ISO_SERVICE_REGISTRY.items()
        if clause in config["iso_clause"].split(", ")
    }


def get_service_count_by_category() -> Dict[str, int]:
    """Get service counts by category"""
    by_component = {}
    for config in ISO_SERVICE_REGISTRY.values():
        component = config["component"]
        by_component[component] = by_component.get(component, 0) + 1

    return {
        "total_services": len(ISO_SERVICE_REGISTRY),
        "core_bcm": 10,
        "community": 2,
        "storage": 1,
        "workflow_intelligence_services": len(get_services_with_workflow_intelligence()),
        "by_component": by_component
    }
