#!/usr/bin/env python3
"""
Complete Platform Architecture Map Generator

Purpose: Generate comprehensive JSON map of entire AI-Platform-ISO platform
- Discovers all services, modules, infrastructure components
- Maps dependencies, APIs, events, business logic
- Outputs structured JSON for visualization, planning, UI development

Usage:
    python generate-complete-platform-map.py --output platform-map.json
    python generate-complete-platform-map.py --format mermaid --output architecture.mmd
    python generate-complete-platform-map.py --format markdown --output ARCHITECTURE_MAP.md
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import re

# Base paths
BASE_DIR = Path("/Users/MD/AI-Platform-ISO")
INTELLIGENT_CORE_DIR = BASE_DIR / "intelligent-core"
PLATFORM_SERVICES_DIR = BASE_DIR / "platform-services"
INFRASTRUCTURE_DIR = BASE_DIR / "infrastructure"


class PlatformMapper:
    """Generate complete platform architecture map"""

    def __init__(self):
        self.platform_map = {
            "version": "2.0.0",
            "generated_at": "2025-10-09",
            "platform_name": "AI-Platform-ISO",
            "description": "Business Continuity Management Platform with AI",
            "layers": {},
            "services": [],
            "modules": [],
            "infrastructure": [],
            "dependencies": [],
            "apis": [],
            "events": [],
            "ports": {},
            "documentation": {}
        }

    def discover_intelligent_core(self):
        """Discover all intelligent-core modules"""
        print("Discovering intelligent-core modules...")
        modules = []

        if not INTELLIGENT_CORE_DIR.exists():
            return modules

        # Known modules with metadata
        module_metadata = {
            "ai-foundation": {
                "port": None,
                "description": "Multi-model LLM orchestration, RAG pipeline, ML predictions",
                "capabilities": ["LLM routing", "RAG", "ML models", "Self-learning"],
                "dependencies": ["Qdrant", "Redis", "PostgreSQL"]
            },
            "workflow_intelligence": {
                "port": 8037,
                "description": "Workflow orchestration with Temporal Cloud",
                "capabilities": ["Temporal workflows", "Orchestration", "State management"],
                "dependencies": ["Temporal Cloud", "EventBus", "PostgreSQL"]
            },
            "expertise-center": {
                "port": 8036,
                "description": "14 domain specialists and tactical assistants",
                "capabilities": ["BIA specialist", "Risk specialist", "Compliance specialist", "14 total"],
                "dependencies": ["ai-foundation", "EventBus"]
            },
            "collective": {
                "port": 8032,
                "description": "Collective intelligence with privacy-preserving agents",
                "capabilities": ["Case library (347+)", "k-anonymity (k=5)", "Pattern matching"],
                "dependencies": ["Qdrant", "PostgreSQL"]
            },
            "predictive": {
                "port": 8031,
                "description": "Risk forecasting and scenario simulation",
                "capabilities": ["Timeline prediction", "Certification forecasting", "Challenge prediction"],
                "dependencies": ["ai-foundation", "PostgreSQL"]
            },
            "community_intelligence": {
                "port": 8038,
                "description": "Community knowledge and peer learning",
                "capabilities": ["Community learning", "Peer collaboration"],
                "dependencies": ["EventBus", "PostgreSQL"]
            },
            "event_intelligence": {
                "port": 8039,
                "description": "Real-time event pattern detection",
                "capabilities": ["Pattern learning", "Anomaly detection", "Event sequences"],
                "dependencies": ["EventBus", "Redis"]
            },
            "orchestration": {
                "port": None,
                "description": "Service coordination and cognitive loop",
                "capabilities": ["Cognitive Loop (6 steps)", "MONITOR-UNDERSTAND-DECIDE-ACT-MEASURE-LEARN"],
                "dependencies": ["EventBus", "Redis", "ai-foundation"]
            },
            "ai_workflow_optimizer": {
                "port": None,
                "description": "Workflow optimization with AI",
                "capabilities": ["Workflow analysis", "Optimization suggestions"],
                "dependencies": ["workflow_intelligence", "ai-foundation"]
            },
            "workflow-engine": {
                "port": 8041,
                "description": "BPMN workflow execution engine",
                "capabilities": ["BPMN execution", "Process automation"],
                "dependencies": ["EventBus"]
            },
            "system-bcm-service": {
                "port": 8050,
                "description": "Production BCM self-application service",
                "capabilities": ["Platform BIA", "Risk assessment", "Auto-recovery (7 procedures)", "Practice learning", "Real-time monitoring"],
                "dependencies": ["EventBus", "Redis", "Prometheus", "ai-foundation"],
                "status": " Production-ready"
            }
        }

        for module_name, metadata in module_metadata.items():
            module_path = INTELLIGENT_CORE_DIR / module_name
            if module_path.exists():
                module = {
                    "name": module_name,
                    "type": "intelligent-core-module",
                    "path": str(module_path.relative_to(BASE_DIR)),
                    "port": metadata["port"],
                    "description": metadata["description"],
                    "capabilities": metadata["capabilities"],
                    "dependencies": metadata["dependencies"],
                    "has_docs": (module_path / "docs").exists(),
                    "has_readme": (module_path / "README.md").exists(),
                    "main_file": self._find_main_file(module_path)
                }
                modules.append(module)

                if metadata["port"]:
                    self.platform_map["ports"][str(metadata["port"])] = {
                        "service": module_name,
                        "type": "intelligent-core",
                        "description": metadata["description"]
                    }

        self.platform_map["modules"] = modules
        return modules

    def discover_platform_services(self):
        """Discover all platform services"""
        print("Discovering platform services...")
        services = []

        if not PLATFORM_SERVICES_DIR.exists():
            return services

        # Known services with ISO mapping
        service_metadata = {
            "bia-service": {
                "port": 8001,
                "iso_clause": "8.2",
                "description": "Business Impact Analysis service",
                "capabilities": ["BIA planning", "Data collection", "Dependency mapping", "RTO/RPO analysis"]
            },
            "risk-service": {
                "port": 8002,
                "iso_clause": "8.3",
                "description": "Risk Assessment & Treatment service",
                "capabilities": ["Risk assessment", "Treatment planning", "Risk monitoring"]
            },
            "compliance-service": {
                "port": 8003,
                "iso_clause": "9.1",
                "description": "ISO 22301 Compliance Monitoring",
                "capabilities": ["Real-time compliance", "Gap analysis", "Evidence collection", "Audit prep"]
            },
            "planning-service": {
                "port": 8004,
                "iso_clause": "8.4",
                "description": "BC Plan Development & Journey Planning",
                "capabilities": ["Journey planning", "BC plans", "Timeline prediction", "Exercise planning"]
            },
            "response-service": {
                "port": 8005,
                "iso_clause": "8.4",
                "description": "Incident Response & Crisis Management",
                "capabilities": ["Incident detection", "Plan activation", "RTO tracking", "Crisis coordination"]
            },
            "documents-service": {
                "port": 8006,
                "iso_clause": "7.5",
                "description": "Document Management & Living Docs",
                "capabilities": ["Living docs", "Version control", "Templates", "Collaboration"]
            },
            "governance-service": {
                "port": 8007,
                "iso_clause": "5.0",
                "description": "Leadership & Governance",
                "capabilities": ["Policy management", "Management review", "Stakeholder engagement"]
            },
            "validation-service": {
                "port": 8008,
                "iso_clause": "8.5",
                "description": "Exercise & Testing",
                "capabilities": ["Exercise planning", "Digital twin", "Scenario generation", "AAR"]
            },
            "learning-service": {
                "port": 8009,
                "iso_clause": "7.3",
                "description": "Training & Awareness",
                "capabilities": ["Training programs", "Certification tracking", "Awareness campaigns"]
            },
            "bcm-coordination-service": {
                "port": 8010,
                "iso_clause": None,
                "description": "Cross-service BCM coordination",
                "capabilities": ["Service orchestration", "Workflow coordination"]
            },
            "community-service": {
                "port": 8011,
                "iso_clause": None,
                "description": "Community & Knowledge sharing",
                "capabilities": ["Community forums", "Knowledge sharing", "Peer learning"]
            },
            "monitoring": {
                "port": 8012,
                "iso_clause": "9.0",
                "description": "Performance Monitoring & Analytics",
                "capabilities": ["Real-time monitoring", "Metrics", "Dashboards", "Alerting"]
            }
        }

        for service_name, metadata in service_metadata.items():
            service_path = PLATFORM_SERVICES_DIR / service_name
            if service_path.exists():
                service = {
                    "name": service_name,
                    "type": "platform-service",
                    "path": str(service_path.relative_to(BASE_DIR)),
                    "port": metadata["port"],
                    "iso_clause": metadata["iso_clause"],
                    "description": metadata["description"],
                    "capabilities": metadata["capabilities"],
                    "has_docs": (service_path / "docs").exists(),
                    "has_readme": (service_path / "README.md").exists(),
                    "main_file": self._find_main_file(service_path)
                }
                services.append(service)

                if metadata["port"]:
                    self.platform_map["ports"][str(metadata["port"])] = {
                        "service": service_name,
                        "type": "platform-service",
                        "iso_clause": metadata["iso_clause"],
                        "description": metadata["description"]
                    }

        self.platform_map["services"] = services
        return services

    def discover_infrastructure(self):
        """Discover infrastructure components"""
        print("Discovering infrastructure components...")
        infrastructure = []

        components = {
            "eventbus": {
                "type": "messaging",
                "technology": "Redis Streams + RabbitMQ",
                "port": "6379 (Redis), 5672 (RabbitMQ)",
                "description": "Event-driven messaging system",
                "patterns": ["Event Choreography", "Saga", "Event Sourcing", "Dead Letter Queue"]
            },
            "database": {
                "type": "storage",
                "technology": "PostgreSQL + Supabase",
                "port": "5432",
                "description": "Multi-tenant relational database with RLS",
                "capabilities": ["Multi-tenancy", "Row-Level Security", "Migrations", "Backup"]
            },
            "observability": {
                "type": "monitoring",
                "technology": "Prometheus + Grafana",
                "port": "9090 (Prometheus), 3000 (Grafana)",
                "description": "Metrics, monitoring, alerting",
                "capabilities": ["Metrics collection", "Dashboards", "Alerting", "Tracing"]
            },
            "security": {
                "type": "security",
                "technology": "Vault + JWT",
                "port": "8200 (Vault)",
                "description": "Secrets management, authentication, authorization",
                "capabilities": ["Secrets storage", "JWT authentication", "RBAC", "Encryption"]
            },
            "gateway": {
                "type": "api-gateway",
                "technology": "FastAPI",
                "port": "8000",
                "description": "Unified API gateway and routing",
                "capabilities": ["Request routing", "Load balancing", "Rate limiting", "Authentication"]
            },
            "vector-db": {
                "type": "storage",
                "technology": "Qdrant",
                "port": "6333",
                "description": "Vector database for RAG pipeline",
                "capabilities": ["Vector search", "Hybrid search", "Collections", "Filtering"]
            }
        }

        for component_name, metadata in components.items():
            component_path = INFRASTRUCTURE_DIR / component_name
            component = {
                "name": component_name,
                "type": "infrastructure",
                "subtype": metadata["type"],
                "technology": metadata["technology"],
                "port": metadata["port"],
                "description": metadata["description"],
                "capabilities": metadata.get("capabilities", []),
                "patterns": metadata.get("patterns", []),
                "has_docs": component_path.exists() and (component_path / "README.md").exists()
            }
            infrastructure.append(component)

        self.platform_map["infrastructure"] = infrastructure
        return infrastructure

    def map_dependencies(self):
        """Map service dependencies"""
        print("Mapping dependencies...")
        dependencies = []

        # Module dependencies
        for module in self.platform_map["modules"]:
            for dep in module.get("dependencies", []):
                dependencies.append({
                    "from": module["name"],
                    "to": dep,
                    "type": "uses"
                })

        # Service dependencies (services use modules)
        common_service_deps = ["EventBus", "PostgreSQL", "ai-foundation", "expertise-center"]
        for service in self.platform_map["services"]:
            for dep in common_service_deps:
                dependencies.append({
                    "from": service["name"],
                    "to": dep,
                    "type": "uses"
                })

        self.platform_map["dependencies"] = dependencies
        return dependencies

    def map_documentation(self):
        """Map all documentation locations"""
        print("Mapping documentation...")

        docs_map = {
            "platform_docs": {
                "path": "docs/",
                "files": [
                    "INDEX.md",
                    "README.md",
                    "EXECUTIVE_SUMMARY.md",
                    "GETTING_STARTED.md",
                    "DEPLOYMENT_GUIDE.md",
                    "STANDARDS_COMPLIANCE.md",
                    "ARCHITECTURE.md",
                    "API_REFERENCE.md",
                    "COMPLETE_DOCUMENTATION_MAP.md"
                ],
                "size": "~350 KB",
                "file_count": 9
            },
            "comprehensive_docs": {
                "path": "comprehensive-platform-docs/",
                "files": [
                    "AI_FOUNDATION_CAPABILITIES.md",
                    "AI_ORCHESTRATION_CAPABILITIES.md",
                    "DOMAIN_EXPERTISE_CAPABILITIES.md",
                    "PREDICTIVE_INTELLIGENCE_CAPABILITIES.md",
                    "INFRASTRUCTURE_ORCHESTRATION_COMPLETE.md",
                    "BUSINESS_PROCESS_SCENARIOS_COMPLETE.md",
                    "ALL_USAGE_SCENARIOS_CATALOG.md",
                    "MASTER_INDEX.md"
                ],
                "size": "~426 KB",
                "file_count": 8,
                "description": "570+ usage scenarios, AI capabilities, 18 infrastructure patterns"
            },
            "infrastructure_tools": {
                "path": "infrastructure/tools/",
                "categories": {
                    "catalogs": ["TOOLS_CATALOG_INDEX.md", "TOOLS_COMPREHENSIVE_CATALOG.md"],
                    "analyzers": 10,
                    "generators": 5,
                    "scripts": 8
                },
                "size": "~187 KB",
                "description": "Automation tools, analyzers, documentation generators"
            },
            "archive": {
                "path": "_archive/docs-old-backup/",
                "sections": 13,
                "file_count": 111,
                "size": "~2.1 MB",
                "description": "Historical documentation for reference"
            },
            "module_docs": {
                "path": "intelligent-core/{module}/docs/",
                "pattern": "Each module has: ARCHITECTURE.md, TECHNICAL_SPECIFICATION.md, BUSINESS_LOGIC.md, API.md, INTEGRATION.md, DEPLOYMENT.md",
                "estimated_files": 98
            },
            "service_docs": {
                "path": "platform-services/{service}/docs/",
                "pattern": "Each service has: TECHNICAL_SPECIFICATION.md, API.md, BUSINESS_LOGIC.md, INTEGRATION.md, DEPLOYMENT.md",
                "estimated_files": 72
            }
        }

        self.platform_map["documentation"] = docs_map
        return docs_map

    def _find_main_file(self, path: Path) -> str:
        """Find main.py or app.py in path"""
        if (path / "main.py").exists():
            return "main.py"
        if (path / "app.py").exists():
            return "app.py"
        if (path / "service" / "main.py").exists():
            return "service/main.py"
        return None

    def generate_map(self) -> Dict[str, Any]:
        """Generate complete platform map"""
        print("\n=== Generating Complete Platform Map ===\n")

        # Discover all components
        self.discover_intelligent_core()
        self.discover_platform_services()
        self.discover_infrastructure()

        # Map relationships
        self.map_dependencies()
        self.map_documentation()

        # Add layer structure
        self.platform_map["layers"] = {
            "1_infrastructure": {
                "name": "Infrastructure Layer",
                "components": [c["name"] for c in self.platform_map["infrastructure"]],
                "description": "Core infrastructure: EventBus, Database, Security, Observability"
            },
            "2_intelligent_core": {
                "name": "Intelligent Core Layer",
                "components": [m["name"] for m in self.platform_map["modules"]],
                "description": "AI modules: LLM routing, RAG, Specialists, Orchestration"
            },
            "3_platform_services": {
                "name": "Platform Services Layer",
                "components": [s["name"] for s in self.platform_map["services"]],
                "description": "BCM services mapped to ISO 22301 clauses"
            },
            "4_integration": {
                "name": "Integration Layer",
                "components": ["API Gateway", "EventBus", "WebSocket"],
                "description": "External integrations and APIs"
            }
        }

        # Summary statistics
        self.platform_map["statistics"] = {
            "total_services": len(self.platform_map["services"]),
            "total_modules": len(self.platform_map["modules"]),
            "total_infrastructure_components": len(self.platform_map["infrastructure"]),
            "total_dependencies": len(self.platform_map["dependencies"]),
            "total_ports": len(self.platform_map["ports"]),
            "total_documentation_files": "~320+",
            "iso_clauses_covered": 10
        }

        return self.platform_map

    def export_json(self, output_path: str):
        """Export map as JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.platform_map, f, indent=2, ensure_ascii=False)
        print(f"\n JSON map exported to: {output_path}")

    def export_markdown(self, output_path: str):
        """Export map as Markdown"""
        md = ["# AI-Platform-ISO: Complete Platform Map\n"]
        md.append(f"**Generated**: {self.platform_map['generated_at']}")
        md.append(f"**Version**: {self.platform_map['version']}\n")

        md.append("## Platform Statistics\n")
        stats = self.platform_map["statistics"]
        for key, value in stats.items():
            md.append(f"- **{key.replace('_', ' ').title()}**: {value}")

        md.append("\n## Layers\n")
        for layer_id, layer in self.platform_map["layers"].items():
            md.append(f"### {layer['name']}")
            md.append(f"{layer['description']}\n")
            md.append(f"**Components**: {', '.join(layer['components'])}\n")

        md.append("\n## Services\n")
        for service in self.platform_map["services"]:
            md.append(f"### {service['name']}")
            md.append(f"- **Port**: {service['port']}")
            md.append(f"- **ISO Clause**: {service['iso_clause']}")
            md.append(f"- **Description**: {service['description']}")
            md.append(f"- **Capabilities**: {', '.join(service['capabilities'])}\n")

        md.append("\n## Modules\n")
        for module in self.platform_map["modules"]:
            md.append(f"### {module['name']}")
            if module['port']:
                md.append(f"- **Port**: {module['port']}")
            md.append(f"- **Description**: {module['description']}")
            md.append(f"- **Capabilities**: {', '.join(module['capabilities'])}\n")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md))
        print(f" Markdown map exported to: {output_path}")

    def export_mermaid(self, output_path: str):
        """Export map as Mermaid diagram"""
        mmd = ["graph TB\n"]

        # Infrastructure layer
        mmd.append("    subgraph Infrastructure")
        for comp in self.platform_map["infrastructure"]:
            mmd.append(f"        {comp['name']}[{comp['name']}]")
        mmd.append("    end\n")

        # Intelligent core layer
        mmd.append("    subgraph IntelligentCore[Intelligent Core]")
        for module in self.platform_map["modules"][:5]:  # Limit for readability
            mmd.append(f"        {module['name']}[{module['name']}]")
        mmd.append("    end\n")

        # Platform services layer
        mmd.append("    subgraph PlatformServices[Platform Services]")
        for service in self.platform_map["services"][:5]:  # Limit for readability
            mmd.append(f"        {service['name']}[{service['name']}]")
        mmd.append("    end\n")

        # Dependencies (sample)
        mmd.append("    %% Sample dependencies")
        mmd.append("    ai-foundation --> eventbus")
        mmd.append("    ai-foundation --> database")
        mmd.append("    expertise-center --> ai-foundation")
        mmd.append("    bia-service --> ai-foundation")
        mmd.append("    bia-service --> expertise-center")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(mmd))
        print(f" Mermaid diagram exported to: {output_path}")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate complete platform architecture map")
    parser.add_argument("--output", default="platform-map.json", help="Output file path")
    parser.add_argument("--format", choices=["json", "markdown", "mermaid"], default="json", help="Output format")

    args = parser.parse_args()

    # Generate map
    mapper = PlatformMapper()
    platform_map = mapper.generate_map()

    # Export based on format
    if args.format == "json":
        mapper.export_json(args.output)
    elif args.format == "markdown":
        mapper.export_markdown(args.output)
    elif args.format == "mermaid":
        mapper.export_mermaid(args.output)

    # Print summary
    print("\n" + "="*60)
    print("PLATFORM MAP GENERATION COMPLETE")
    print("="*60)
    print(f"\nTotal Services: {len(platform_map['services'])}")
    print(f"Total Modules: {len(platform_map['modules'])}")
    print(f"Total Infrastructure Components: {len(platform_map['infrastructure'])}")
    print(f"Total Dependencies: {len(platform_map['dependencies'])}")
    print(f"Total Ports Mapped: {len(platform_map['ports'])}")
    print(f"\n Documentation: {platform_map['statistics']['total_documentation_files']} files")
    print(f" ISO 22301 Clauses: {platform_map['statistics']['iso_clauses_covered']}")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
