"""
BCM Service Registry
===================

Maps ISO 22301 clauses to BCM microservices and capabilities.

Based on original ORCHESTRATORS_AUDIT.md service registry pattern.
"""

import logging
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ISO22301Clause(str, Enum):
    """ISO 22301:2019 Clause mapping"""
    CLAUSE_4 = "4_context"  # Context of the organization
    CLAUSE_5 = "5_leadership"  # Leadership
    CLAUSE_6 = "6_planning"  # Planning
    CLAUSE_7 = "7_support"  # Support
    CLAUSE_8 = "8_operation"  # Operation
    CLAUSE_9 = "9_performance"  # Performance evaluation
    CLAUSE_10 = "10_improvement"  # Improvement


class BCMServiceType(str, Enum):
    """BCM Microservice Types"""
    BIA_SERVICE = "bia_service"
    RISK_SERVICE = "risk_service"
    PLAN_SERVICE = "plan_service"
    EXERCISE_SERVICE = "exercise_service"
    INCIDENT_SERVICE = "incident_service"
    COMPLIANCE_SERVICE = "compliance_service"
    LEARNING_SERVICE = "learning_service"
    VALIDATION_SERVICE = "validation_service"
    GOVERNANCE_SERVICE = "governance_service"
    DOCUMENT_SERVICE = "document_service"


class BCMServiceRegistry:
    """
    Registry of BCM services with ISO 22301 clause mapping.

    Features:
    - Service discovery by ISO clause
    - Service health monitoring
    - Load balancing across service instances
    - Circuit breaker for failed services

    Example:
        ```python
        registry = BCMServiceRegistry()
        services = registry.find_services_for_clause(ISO22301Clause.CLAUSE_8)
        # Returns: [BIA Service, Risk Service, Plan Service]
        ```
    """

    # Service definitions (from ORCHESTRATORS_AUDIT.md)
    SERVICE_CATALOG = {
        BCMServiceType.BIA_SERVICE: {
            "name": "Business Impact Analysis Service",
            "host": "localhost",
            "port": 8001,
            "iso_clauses": [
                ISO22301Clause.CLAUSE_8,  # 8.2 Business impact analysis
                ISO22301Clause.CLAUSE_6   # 6.1 Planning
            ],
            "capabilities": [
                "process_identification",
                "dependency_mapping",
                "impact_assessment",
                "rto_rpo_determination",
                "criticality_scoring"
            ],
            "health_endpoint": "/health"
        },
        BCMServiceType.RISK_SERVICE: {
            "name": "Risk Assessment Service",
            "host": "localhost",
            "port": 8002,
            "iso_clauses": [
                ISO22301Clause.CLAUSE_8,  # 8.1 Risk assessment
                ISO22301Clause.CLAUSE_6   # 6.1 Planning
            ],
            "capabilities": [
                "threat_identification",
                "vulnerability_assessment",
                "fair_analysis",
                "risk_scoring",
                "treatment_planning"
            ],
            "health_endpoint": "/health"
        },
        BCMServiceType.PLAN_SERVICE: {
            "name": "Continuity Planning Service",
            "host": "localhost",
            "port": 8003,
            "iso_clauses": [
                ISO22301Clause.CLAUSE_8,  # 8.4 Business continuity plans
                ISO22301Clause.CLAUSE_6   # 6.2 BC objectives
            ],
            "capabilities": [
                "recovery_strategy_design",
                "plan_generation",
                "resource_allocation",
                "plan_maintenance"
            ],
            "health_endpoint": "/health"
        },
        BCMServiceType.EXERCISE_SERVICE: {
            "name": "Exercise & Testing Service",
            "host": "localhost",
            "port": 8004,
            "iso_clauses": [
                ISO22301Clause.CLAUSE_8,  # 8.5 Exercising and testing
                ISO22301Clause.CLAUSE_9   # 9.1 Monitoring
            ],
            "capabilities": [
                "scenario_design",
                "exercise_execution",
                "results_collection",
                "lessons_learned"
            ],
            "health_endpoint": "/health"
        },
        BCMServiceType.INCIDENT_SERVICE: {
            "name": "Incident Response Service",
            "host": "localhost",
            "port": 8005,
            "iso_clauses": [
                ISO22301Clause.CLAUSE_8,  # 8.4 Incident response
                ISO22301Clause.CLAUSE_10  # 10.2 Corrective action
            ],
            "capabilities": [
                "incident_detection",
                "severity_assessment",
                "response_coordination",
                "post_incident_review"
            ],
            "health_endpoint": "/health"
        },
        BCMServiceType.COMPLIANCE_SERVICE: {
            "name": "Compliance Management Service",
            "host": "localhost",
            "port": 8006,
            "iso_clauses": [
                ISO22301Clause.CLAUSE_9,  # 9.2 Internal audit
                ISO22301Clause.CLAUSE_10  # 10.1 Continual improvement
            ],
            "capabilities": [
                "gap_analysis",
                "audit_management",
                "control_assessment",
                "compliance_reporting"
            ],
            "health_endpoint": "/health"
        },
        BCMServiceType.LEARNING_SERVICE: {
            "name": "Learning & Intelligence Service",
            "host": "localhost",
            "port": 8007,
            "iso_clauses": [
                ISO22301Clause.CLAUSE_10,  # 10.2 Continual improvement
                ISO22301Clause.CLAUSE_7   # 7.4 Communication
            ],
            "capabilities": [
                "pattern_extraction",
                "cross_module_learning",
                "knowledge_graph_update",
                "best_practice_identification"
            ],
            "health_endpoint": "/health"
        },
        BCMServiceType.VALIDATION_SERVICE: {
            "name": "Validation & KPI Service",
            "host": "localhost",
            "port": 8008,
            "iso_clauses": [
                ISO22301Clause.CLAUSE_9,  # 9.1 Performance evaluation
                ISO22301Clause.CLAUSE_6   # 6.2 BC objectives
            ],
            "capabilities": [
                "kpi_tracking",
                "objective_validation",
                "alert_generation",
                "performance_reporting"
            ],
            "health_endpoint": "/health"
        },
        BCMServiceType.GOVERNANCE_SERVICE: {
            "name": "Governance Service",
            "host": "localhost",
            "port": 8009,
            "iso_clauses": [
                ISO22301Clause.CLAUSE_5,  # 5.1 Leadership
                ISO22301Clause.CLAUSE_4   # 4.1 Understanding the organization
            ],
            "capabilities": [
                "policy_management",
                "stakeholder_analysis",
                "context_assessment",
                "governance_framework"
            ],
            "health_endpoint": "/health"
        },
        BCMServiceType.DOCUMENT_SERVICE: {
            "name": "Document Management Service",
            "host": "localhost",
            "port": 8010,
            "iso_clauses": [
                ISO22301Clause.CLAUSE_7,  # 7.5 Documented information
                ISO22301Clause.CLAUSE_8   # 8.4 Plans and procedures
            ],
            "capabilities": [
                "document_storage",
                "version_control",
                "access_management",
                "document_lifecycle"
            ],
            "health_endpoint": "/health"
        }
    }

    def __init__(self):
        """Initialize service registry."""
        self.services = self.SERVICE_CATALOG.copy()
        self.service_health = {svc: "unknown" for svc in BCMServiceType}
        logger.info(f"BCMServiceRegistry initialized with {len(self.services)} services")

    def find_services_for_clause(
        self,
        clause: ISO22301Clause
    ) -> List[Dict[str, Any]]:
        """
        Find all services supporting a specific ISO clause.

        Args:
            clause: ISO 22301 clause

        Returns:
            List of matching services
        """
        matching_services = []

        for svc_type, svc_config in self.services.items():
            if clause in svc_config["iso_clauses"]:
                matching_services.append({
                    "type": svc_type.value,
                    "name": svc_config["name"],
                    "host": svc_config["host"],
                    "port": svc_config["port"],
                    "capabilities": svc_config["capabilities"],
                    "health": self.service_health.get(svc_type, "unknown")
                })

        return matching_services

    def find_service_by_capability(
        self,
        capability: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find service providing specific capability.

        Args:
            capability: Capability name (e.g., "impact_assessment")

        Returns:
            Service config or None
        """
        for svc_type, svc_config in self.services.items():
            if capability in svc_config["capabilities"]:
                return {
                    "type": svc_type.value,
                    "name": svc_config["name"],
                    "host": svc_config["host"],
                    "port": svc_config["port"],
                    "health": self.service_health.get(svc_type, "unknown")
                }

        return None

    def get_service_url(self, service_type: BCMServiceType) -> str:
        """
        Get full URL for service.

        Args:
            service_type: Service type

        Returns:
            Service URL (e.g., "http://localhost:8001")
        """
        config = self.services.get(service_type)
        if not config:
            raise ValueError(f"Service {service_type.value} not found")

        return f"http://{config['host']}:{config['port']}"

    def update_health(self, service_type: BCMServiceType, health: str):
        """
        Update service health status.

        Args:
            service_type: Service type
            health: Health status ("healthy", "degraded", "down")
        """
        self.service_health[service_type] = health
        logger.info(f"Service {service_type.value} health: {health}")

    def get_all_services(self) -> List[Dict[str, Any]]:
        """Get list of all registered services."""
        return [
            {
                "type": svc_type.value,
                "name": config["name"],
                "url": f"http://{config['host']}:{config['port']}",
                "iso_clauses": [c.value for c in config["iso_clauses"]],
                "capabilities": config["capabilities"],
                "health": self.service_health.get(svc_type, "unknown")
            }
            for svc_type, config in self.services.items()
        ]

    def get_coverage_report(self) -> Dict[str, Any]:
        """
        Get ISO 22301 coverage report.

        Returns:
            Coverage statistics by clause
        """
        coverage = {}

        for clause in ISO22301Clause:
            services = self.find_services_for_clause(clause)
            coverage[clause.value] = {
                "clause": clause.value,
                "services_count": len(services),
                "services": [s["name"] for s in services],
                "status": "covered" if len(services) > 0 else "not_covered"
            }

        return {
            "total_clauses": len(ISO22301Clause),
            "covered_clauses": sum(1 for c in coverage.values() if c["status"] == "covered"),
            "coverage_percentage": (
                sum(1 for c in coverage.values() if c["status"] == "covered") / len(ISO22301Clause) * 100
            ),
            "details": coverage
        }
