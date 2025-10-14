#!/usr/bin/env python3
"""
Documentation Generation Script
Generates comprehensive documentation from service-catalog.yaml and SERVICE_INFO.yaml files

Outputs:
- Markdown documentation (README.md style)
- HTML documentation (static website)
- API reference (OpenAPI specs)
- Service dependency graphs (Mermaid diagrams)

Usage:
    python generate_docs.py
    python generate_docs.py --format markdown
    python generate_docs.py --format html --output docs/
    python generate_docs.py --format all
"""

import os
import sys
import yaml
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Base directory for AI-Platform-ISO
BASE_DIR = Path(__file__).parent.parent.parent.parent
CATALOG_FILE = BASE_DIR / "infrastructure/runtime/service-catalog/service-catalog.yaml"
OUTPUT_DIR = BASE_DIR / "docs/service-catalog"


class DocumentationGenerator:
    """Generates documentation from service catalog"""

    def __init__(self, catalog_path: Path, output_dir: Path):
        self.catalog_path = catalog_path
        self.output_dir = output_dir
        self.catalog = None

    def load_catalog(self):
        """Load service catalog"""
        with open(self.catalog_path, 'r', encoding='utf-8') as f:
            self.catalog = yaml.safe_load(f)
        print(f"✅ Loaded catalog with {self.catalog['metadata']['total_services']} services")

    def generate_markdown(self) -> str:
        """Generate comprehensive Markdown documentation"""
        md = []

        # Header
        md.append("# AI Platform ISO - Service Catalog")
        md.append("")
        md.append(f"**Version:** {self.catalog['metadata']['version']}")
        md.append(f"**Generated:** {self.catalog['metadata']['generated_at']}")
        md.append(f"**Total Services:** {self.catalog['metadata']['total_services']}")
        md.append("")
        md.append("---")
        md.append("")

        # Table of Contents
        md.append("## 📑 Table of Contents")
        md.append("")
        md.append("1. [Overview](#overview)")
        md.append("2. [Platform Services](#platform-services)")
        md.append("3. [Intelligent Core](#intelligent-core)")
        md.append("4. [Statistics](#statistics)")
        md.append("5. [Technology Stack](#technology-stack)")
        md.append("6. [Service Discovery](#service-discovery)")
        md.append("7. [Monitoring](#monitoring)")
        md.append("")
        md.append("---")
        md.append("")

        # Overview
        md.append("## 🎯 Overview")
        md.append("")
        md.append("The AI Platform ISO is a comprehensive Business Continuity Management (BCM) platform ")
        md.append("implementing ISO 22301:2019 requirements with advanced AI-powered automation.")
        md.append("")

        stats = self.catalog.get('statistics', {})
        md.append("### Quick Stats")
        md.append("")
        md.append(f"- **Active Services:** {stats.get('by_status', {}).get('active', 0)}")
        md.append(f"- **Planned Services:** {stats.get('by_status', {}).get('planned', 0)}")
        md.append(f"- **Total Endpoints:** {stats.get('total_endpoints', 'N/A')}")
        md.append("")
        md.append("---")
        md.append("")

        # Platform Services
        md.append("## 🏢 Platform Services")
        md.append("")
        platform = self.catalog.get('platform_services', {})
        md.append(platform.get('description', ''))
        md.append("")
        md.append(f"**Total:** {platform.get('total', 0)} services")
        md.append("")

        for service in platform.get('services', []):
            md.extend(self._generate_service_section(service, "platform"))

        # Intelligent Core
        md.append("## 🧠 Intelligent Core")
        md.append("")
        intelligent = self.catalog.get('intelligent_core', {})
        md.append(intelligent.get('description', ''))
        md.append("")
        md.append(f"**Total:** {intelligent.get('total', 0)} services")
        md.append("")

        for service in intelligent.get('services', []):
            md.extend(self._generate_service_section(service, "intelligent"))

        # Statistics
        md.append("## 📊 Statistics")
        md.append("")

        md.append("### By Status")
        md.append("")
        md.append("| Status | Count |")
        md.append("|--------|-------|")
        by_status = stats.get('by_status', {})
        for status, count in by_status.items():
            md.append(f"| {status.capitalize()} | {count} |")
        md.append("")

        md.append("### By Category")
        md.append("")
        md.append("| Category | Count |")
        md.append("|----------|-------|")
        by_category = stats.get('by_category', {})
        for category, count in by_category.items():
            md.append(f"| {category} | {count} |")
        md.append("")

        # Technology Stack
        md.append("## 🛠️ Technology Stack")
        md.append("")

        tech_stack = self.catalog.get('technology_stack', {})

        for category, items in tech_stack.items():
            md.append(f"### {category.replace('_', ' ').title()}")
            md.append("")
            for item in items:
                md.append(f"- {item}")
            md.append("")

        # Service Discovery
        md.append("## 🔍 Service Discovery")
        md.append("")

        discovery = self.catalog.get('service_discovery', {})
        md.append(f"- **URL:** {discovery.get('url', 'N/A')}")
        md.append(f"- **API:** {discovery.get('api', 'N/A')}")
        md.append(f"- **Health Checks:** {discovery.get('health_checks', 'N/A')}")
        md.append(f"- **Integration:** {discovery.get('integration', 'N/A')}")
        md.append("")

        # Monitoring
        md.append("## 📈 Monitoring")
        md.append("")

        monitoring = self.catalog.get('monitoring', {})
        md.append(f"- **Prometheus:** {monitoring.get('prometheus', 'N/A')}")
        md.append(f"- **Grafana:** {monitoring.get('grafana', 'N/A')}")
        md.append(f"- **Metrics Endpoint:** {monitoring.get('metrics_endpoint', 'N/A')}")
        md.append("")

        md.append("---")
        md.append("")
        md.append(f"*Generated on {datetime.utcnow().isoformat()}Z*")

        return "\n".join(md)

    def _generate_service_section(self, service: Dict[str, Any], category: str) -> List[str]:
        """Generate markdown section for a service"""
        md = []

        name = service.get('name', 'unknown')
        display_name = service.get('display_name', name)
        version = service.get('version', 'N/A')
        status = service.get('status', 'unknown')

        # Service header
        md.append(f"### {display_name}")
        md.append("")

        # Metadata table
        md.append("| Property | Value |")
        md.append("|----------|-------|")
        md.append(f"| **Name** | `{name}` |")
        md.append(f"| **Version** | {version} |")
        md.append(f"| **Status** | {status.upper()} |")
        md.append(f"| **Type** | {service.get('type', 'N/A')} |")

        runtime = service.get('runtime', {})
        if isinstance(runtime, dict):
            md.append(f"| **Port** | {runtime.get('port', 'N/A')} |")
            md.append(f"| **Framework** | {runtime.get('framework', 'N/A')} |")

        md.append("")

        # Description
        description = service.get('description', '')
        if description:
            md.append(f"**Description:** {description}")
            md.append("")

        # Capabilities
        capabilities = service.get('capabilities', [])
        if capabilities:
            md.append("**Capabilities:**")
            md.append("")
            for cap in capabilities[:5]:  # Show first 5
                md.append(f"- {cap}")
            if len(capabilities) > 5:
                md.append(f"- ... and {len(capabilities) - 5} more")
            md.append("")

        # KPIs
        kpis = service.get('kpis', [])
        if kpis and isinstance(kpis[0], dict):
            md.append("**Key KPIs:**")
            md.append("")
            md.append("| KPI | Target |")
            md.append("|-----|--------|")
            for kpi in kpis[:5]:  # Show first 5
                if isinstance(kpi, dict):
                    md.append(f"| {kpi.get('name', 'N/A')} | {kpi.get('target', 'N/A')} |")
            md.append("")

        # ISO Clause (for platform services)
        iso_clause = service.get('iso_clause')
        if iso_clause:
            md.append(f"**ISO 22301 Clause:** {iso_clause}")
            md.append("")

        # Source file
        source_file = service.get('_source_file')
        if source_file:
            md.append(f"**Source:** `{source_file}`")
            md.append("")

        md.append("---")
        md.append("")

        return md

    def generate_html(self) -> str:
        """Generate HTML documentation"""
        html = []

        html.append("<!DOCTYPE html>")
        html.append("<html lang='en'>")
        html.append("<head>")
        html.append("    <meta charset='UTF-8'>")
        html.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        html.append("    <title>AI Platform ISO - Service Catalog</title>")
        html.append("    <style>")
        html.append(self._get_html_styles())
        html.append("    </style>")
        html.append("</head>")
        html.append("<body>")
        html.append("    <div class='container'>")

        # Header
        html.append("        <header>")
        html.append("            <h1>🚀 AI Platform ISO - Service Catalog</h1>")
        html.append(f"            <p class='subtitle'>Version {self.catalog['metadata']['version']} | "
                    f"{self.catalog['metadata']['total_services']} Services</p>")
        html.append("        </header>")

        # Statistics
        stats = self.catalog.get('statistics', {})
        html.append("        <div class='stats-grid'>")
        html.append(f"            <div class='stat-card'><h3>{stats.get('by_status', {}).get('active', 0)}</h3><p>Active Services</p></div>")
        html.append(f"            <div class='stat-card'><h3>{stats.get('by_status', {}).get('planned', 0)}</h3><p>Planned Services</p></div>")
        html.append(f"            <div class='stat-card'><h3>{stats.get('total_endpoints', 'N/A')}</h3><p>Total Endpoints</p></div>")
        html.append("        </div>")

        # Platform Services
        html.append("        <section>")
        html.append("            <h2>🏢 Platform Services</h2>")
        platform = self.catalog.get('platform_services', {})
        html.append(f"            <p>{platform.get('description', '')}</p>")
        html.append("            <div class='services-grid'>")
        for service in platform.get('services', []):
            html.append(self._generate_service_card_html(service))
        html.append("            </div>")
        html.append("        </section>")

        # Intelligent Core
        html.append("        <section>")
        html.append("            <h2>🧠 Intelligent Core</h2>")
        intelligent = self.catalog.get('intelligent_core', {})
        html.append(f"            <p>{intelligent.get('description', '')}</p>")
        html.append("            <div class='services-grid'>")
        for service in intelligent.get('services', []):
            html.append(self._generate_service_card_html(service))
        html.append("            </div>")
        html.append("        </section>")

        # Footer
        html.append("        <footer>")
        html.append(f"            <p>Generated on {datetime.utcnow().isoformat()}Z</p>")
        html.append("        </footer>")

        html.append("    </div>")
        html.append("</body>")
        html.append("</html>")

        return "\n".join(html)

    def _generate_service_card_html(self, service: Dict[str, Any]) -> str:
        """Generate HTML card for a service"""
        name = service.get('name', 'unknown')
        display_name = service.get('display_name', name)
        version = service.get('version', 'N/A')
        status = service.get('status', 'unknown')
        description = service.get('description', '')[:150] + "..."

        runtime = service.get('runtime', {})
        port = runtime.get('port', 'N/A') if isinstance(runtime, dict) else 'N/A'

        status_class = 'status-active' if status == 'active' else 'status-planned'

        card = f"""
                <div class='service-card'>
                    <div class='service-header'>
                        <h3>{display_name}</h3>
                        <span class='badge {status_class}'>{status.upper()}</span>
                    </div>
                    <p class='service-meta'><strong>Port:</strong> {port} | <strong>Version:</strong> {version}</p>
                    <p class='service-description'>{description}</p>
                </div>"""

        return card

    def _get_html_styles(self) -> str:
        """Get CSS styles for HTML documentation"""
        return """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        header { text-align: center; margin-bottom: 40px; }
        header h1 { font-size: 2.5rem; color: #2c3e50; margin-bottom: 10px; }
        .subtitle { color: #7f8c8d; font-size: 1.1rem; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }
        .stat-card { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
        .stat-card h3 { font-size: 2.5rem; color: #3498db; margin-bottom: 10px; }
        .stat-card p { color: #7f8c8d; font-size: 0.9rem; }
        section { margin-bottom: 50px; }
        section h2 { font-size: 2rem; color: #2c3e50; margin-bottom: 20px; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        .services-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; margin-top: 30px; }
        .service-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: transform 0.2s; }
        .service-card:hover { transform: translateY(-5px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }
        .service-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .service-header h3 { font-size: 1.3rem; color: #2c3e50; }
        .badge { padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
        .status-active { background: #2ecc71; color: white; }
        .status-planned { background: #f39c12; color: white; }
        .service-meta { color: #7f8c8d; font-size: 0.85rem; margin-bottom: 10px; }
        .service-description { color: #34495e; font-size: 0.95rem; line-height: 1.6; }
        footer { text-align: center; margin-top: 60px; padding-top: 20px; border-top: 1px solid #ecf0f1; color: #7f8c8d; }
        """

    def generate_mermaid_diagram(self) -> str:
        """Generate Mermaid service dependency diagram"""
        mermaid = []

        mermaid.append("```mermaid")
        mermaid.append("graph TB")
        mermaid.append("    %% AI Platform ISO - Service Architecture")
        mermaid.append("")

        # Platform Services
        mermaid.append("    subgraph Platform Services")
        platform = self.catalog.get('platform_services', {})
        for service in platform.get('services', []):
            name = service.get('name', 'unknown')
            display_name = service.get('display_name', name)
            mermaid.append(f"        {name}[\"{display_name}\"]")

        mermaid.append("    end")
        mermaid.append("")

        # Intelligent Core
        mermaid.append("    subgraph Intelligent Core")
        intelligent = self.catalog.get('intelligent_core', {})
        for service in intelligent.get('services', []):
            name = service.get('name', 'unknown')
            display_name = service.get('display_name', name)
            mermaid.append(f"        {name}[\"{display_name}\"]")

        mermaid.append("    end")
        mermaid.append("")

        # Add some key dependencies (sample)
        mermaid.append("    %% Key Dependencies")
        mermaid.append("    ai-orchestration --> workflow-engine")
        mermaid.append("    ai-orchestration --> event_intelligence")
        mermaid.append("    ai-orchestration --> predictive")
        mermaid.append("    response-service --> plans_service")
        mermaid.append("    compliance-service --> governance-service")
        mermaid.append("    compliance-service --> risk-service")

        mermaid.append("```")

        return "\n".join(mermaid)

    def save_documentation(self, format_type: str):
        """Save generated documentation to files"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if format_type in ['markdown', 'all']:
            markdown = self.generate_markdown()
            md_file = self.output_dir / "SERVICE_CATALOG.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"✅ Markdown documentation saved: {md_file}")

        if format_type in ['html', 'all']:
            html = self.generate_html()
            html_file = self.output_dir / "service-catalog.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✅ HTML documentation saved: {html_file}")

        if format_type in ['mermaid', 'all']:
            mermaid = self.generate_mermaid_diagram()
            mermaid_file = self.output_dir / "architecture-diagram.md"
            with open(mermaid_file, 'w', encoding='utf-8') as f:
                f.write(mermaid)
            print(f"✅ Mermaid diagram saved: {mermaid_file}")

        # Always save JSON version for programmatic access
        json_file = self.output_dir / "service-catalog.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.catalog, f, indent=2)
        print(f"✅ JSON documentation saved: {json_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate documentation from service catalog'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['markdown', 'html', 'mermaid', 'all'],
        default='all',
        help='Documentation format to generate'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=OUTPUT_DIR,
        help='Output directory for generated documentation'
    )
    parser.add_argument(
        '--catalog', '-c',
        type=Path,
        default=CATALOG_FILE,
        help='Path to service-catalog.yaml'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("📚 DOCUMENTATION GENERATOR")
    print("=" * 70)
    print(f"\n📄 Catalog: {args.catalog}")
    print(f"📁 Output: {args.output}")
    print(f"🎨 Format: {args.format}\n")

    if not args.catalog.exists():
        print(f"❌ Catalog not found: {args.catalog}")
        print("   Run generate_catalog.py first to create the catalog")
        return 1

    generator = DocumentationGenerator(args.catalog, args.output)
    generator.load_catalog()

    print("\n📝 Generating documentation...")
    generator.save_documentation(args.format)

    print("\n" + "=" * 70)
    print("✅ DOCUMENTATION GENERATION COMPLETE")
    print("=" * 70)
    print(f"\n📂 Documentation available at: {args.output}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
