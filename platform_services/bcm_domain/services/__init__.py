"""
BCM Platform Services
====================

12 ISO 22301-compliant Business Continuity Management services.

All services have been consolidated into the bcm_domain package for:
- Better domain cohesion
- Easier multi-standard scaling
- Clear separation from infrastructure
- Unified BCM domain management

Services:
    - bia_service (8012): Business Impact Analysis (ISO 22301 Clause 8.2.2)
    - risk_service (8015): Risk Assessment (Clause 6.1)
    - compliance_service (8014): ISO 22301 Compliance (Clause 9.2, 10.1, 10.2)
    - planning_service (8011): BC Strategy & Planning (Clause 8.3)
    - governance_service (8017): Governance & Leadership (Clause 5.3, 7.1, 7.3)
    - plans_service (8023): Plans & Procedures (Clause 8.4)
    - response_service (8016): Incident Response (Clause 8.4.4)
    - documents_service (8018): Document Management (Clause 7.5)
    - validation_service (8021): Testing & Exercises (Clause 8.5)
    - learning_service (8019): Training & Awareness (Clause 7.2)
    - community_service (8020): Community & Knowledge Sharing (Clause 7.4)
    - simulation_service (8095): BC Simulations

ISO 22301 Coverage:
    Clause 4: Context of Organization → governance_service
    Clause 5: Leadership → governance_service
    Clause 6: Planning → risk_service, planning_service
    Clause 7: Support → documents_service, learning_service, community_service
    Clause 8: Operation → bia_service, plans_service, validation_service, response_service
    Clause 9: Performance Evaluation → compliance_service
    Clause 10: Improvement → compliance_service

Architecture:
    All services:
    - Are FastAPI applications
    - Use PostgreSQL via Supabase
    - Integrate with EventBus
    - Use AI Foundation (RAG, LLM, ML)
    - Support multi-tenancy (RLS)
    - Export Prometheus metrics

Example:
    Services run independently on their ports:

    ```bash
    # Start BIA Service
    cd bcm_domain/services/bia_service
    python main.py
    # → http://localhost:8012

    # Start Risk Service
    cd bcm_domain/services/risk_service
    python main.py
    # → http://localhost:8015
    ```

Service Discovery:
    Services are discovered via:
    - EventBus registration
    - SERVICE_CATALOG_DETAILED.yaml
    - Digital Twin topology discovery
    - Prometheus service discovery

Migration Note:
    Migrated from: platform_services/<service_name>/
    New location: platform_services/bcm_domain/services/<service_name>/
"""

# Service metadata
SERVICES = {
    "bia_service": {
        "name": "Business Impact Analysis Service",
        "port": 8012,
        "iso_clause": "8.2.2",
        "description": "Conducts BIA for processes and determines RTO/RPO",
    },
    "risk_service": {
        "name": "Risk Assessment Service",
        "port": 8015,
        "iso_clause": "6.1",
        "description": "Identifies and assesses risks to business continuity",
    },
    "compliance_service": {
        "name": "Compliance Service",
        "port": 8014,
        "iso_clause": "9.2, 10.1, 10.2",
        "description": "Manages ISO 22301 compliance, audits, and improvements",
    },
    "planning_service": {
        "name": "BC Planning Service",
        "port": 8011,
        "iso_clause": "8.3",
        "description": "Develops BC strategies and cost-benefit analysis",
    },
    "governance_service": {
        "name": "Governance Service",
        "port": 8017,
        "iso_clause": "5.3, 7.1, 7.3",
        "description": "Manages governance, leadership, and resource allocation",
    },
    "plans_service": {
        "name": "Plans & Procedures Service",
        "port": 8023,
        "iso_clause": "8.4",
        "description": "Creates and manages BC plans and procedures",
    },
    "response_service": {
        "name": "Incident Response Service",
        "port": 8016,
        "iso_clause": "8.4.4",
        "description": "Manages incident response and recovery coordination",
    },
    "documents_service": {
        "name": "Document Management Service",
        "port": 8018,
        "iso_clause": "7.5",
        "description": "Manages BCM documentation and version control",
    },
    "validation_service": {
        "name": "Testing & Validation Service",
        "port": 8021,
        "iso_clause": "8.5",
        "description": "Conducts BC tests, exercises, and validation",
    },
    "learning_service": {
        "name": "Learning Service",
        "port": 8019,
        "iso_clause": "7.2",
        "description": "Provides BCM training and awareness programs",
    },
    "community_service": {
        "name": "Community Service",
        "port": 8020,
        "iso_clause": "7.4",
        "description": "Enables community knowledge sharing and collaboration",
    },
    "simulation_service": {
        "name": "Simulation Service",
        "port": 8095,
        "iso_clause": "-",
        "description": "Runs BC simulations (7 simulation engines)",
    },
}

__all__ = [
    "SERVICES",
]

# Version info
__version__ = "1.0.0"
__services_count__ = len(SERVICES)
