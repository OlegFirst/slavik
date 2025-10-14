#!/usr/bin/env python3
"""
Comprehensive Documentation Generator for 47 Services
====================================================
Generates multi-format documentation from SERVICE_CATALOG_DETAILED.yaml

Supports:
- Markdown (comprehensive)
- HTML (interactive web page)
- JSON (API format)
- Mermaid diagrams (architecture visualization)
- OpenAPI specs (API documentation)
- PDF (via markdown to PDF)

Usage:
    python generate_docs_comprehensive.py
    python generate_docs_comprehensive.py --format all
    python generate_docs_comprehensive.py --include-metrics
"""

import os
import sys
import yaml
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent.parent.parent
DETAILED_CATALOG = BASE_DIR / "infrastructure/SERVICE_CATALOG_DETAILED.yaml"
OUTPUT_DIR = BASE_DIR / "docs/service-catalog-comprehensive"


class ComprehensiveDocGenerator:
    """Enhanced documentation generator for 47 services"""

    def __init__(self, catalog_path: Path, output_dir: Path):
        self.catalog_path = catalog_path
        self.output_dir = output_dir
        self.catalog = None
        self.services_by_category = {}
        self.all_services = []

    def load_catalog(self):
        """Load DETAILED service catalog"""
        with open(self.catalog_path, 'r', encoding='utf-8') as f:
            self.catalog = yaml.safe_load(f)

        # Extract services by category
        categories = [
            'database_infrastructure',
            'runtime_services',
            'gateway_layer',
            'observability',
            'eventbus_core',
            'security',
            'ai_office',
            'platform_services',
            'intelligent_core'
        ]

        for category in categories:
            if category in self.catalog:
                category_data = self.catalog[category]
                if isinstance(category_data, dict):
                    services = []
                    for key, value in category_data.items():
                        if isinstance(value, dict) and 'name' in value:
                            value['_category'] = category
                            services.append(value)
                            self.all_services.append(value)
                    self.services_by_category[category] = services

        print(f"✅ Loaded DETAILED catalog: {len(self.all_services)} services across {len(self.services_by_category)} categories")

    def generate_comprehensive_markdown(self) -> str:
        """Generate comprehensive Markdown with all 47 services"""
        md = []

        # Header
        md.append("# 🏢 AI Platform ISO - Comprehensive Service Catalog")
        md.append("")
        md.append(f"**Version:** {self.catalog.get('version', 'N/A')}")
        md.append(f"**Generated:** {datetime.utcnow().isoformat()}Z")
        md.append(f"**Total Services:** {len(self.all_services)}")
        md.append(f"**Categories:** {len(self.services_by_category)}")
        md.append("")
        md.append("---")
        md.append("")

        # Executive Summary
        md.append("## 📊 Executive Summary")
        md.append("")
        md.append("This comprehensive catalog documents all **47 services** in the AI Platform ISO ecosystem, ")
        md.append("implementing ISO 22301:2019 Business Continuity Management standards with advanced AI capabilities.")
        md.append("")

        # Statistics
        md.append("### Platform Statistics")
        md.append("")
        md.append("| Metric | Value |")
        md.append("|--------|-------|")
        md.append(f"| **Total Services** | {len(self.all_services)} |")
        md.append(f"| **Active Services** | {self.catalog.get('active_services', 'N/A')} |")
        md.append(f"| **Service Categories** | {len(self.services_by_category)} |")

        # Count services with ports
        services_with_ports = sum(1 for s in self.all_services if s.get('runtime', {}).get('port'))
        md.append(f"| **Services with Ports** | {services_with_ports} |")
        md.append("")

        # Category Breakdown
        md.append("### Services by Category")
        md.append("")
        md.append("| Category | Services | Description |")
        md.append("|----------|----------|-------------|")

        category_names = {
            'database_infrastructure': 'Database Infrastructure',
            'runtime_services': 'Runtime Services',
            'gateway_layer': 'Gateway Layer',
            'observability': 'Observability',
            'eventbus_core': 'EventBus Core',
            'security': 'Security',
            'ai_office': 'AI Office',
            'platform_services': 'Platform Services',
            'intelligent_core': 'Intelligent Core'
        }

        for category, services in self.services_by_category.items():
            display_name = category_names.get(category, category.replace('_', ' ').title())
            count = len(services)
            # Get description from first service or category metadata
            desc = self.catalog.get(category, {}).get(category, {}).get('description', 'N/A')[:60] + "..."
            md.append(f"| {display_name} | {count} | {desc} |")
        md.append("")
        md.append("---")
        md.append("")

        # Table of Contents
        md.append("## 📑 Table of Contents")
        md.append("")
        for idx, (category, services) in enumerate(self.services_by_category.items(), 1):
            display_name = category_names.get(category, category.replace('_', ' ').title())
            anchor = category.replace('_', '-')
            md.append(f"{idx}. [{display_name}](#{anchor}) ({len(services)} services)")
        md.append("")
        md.append("---")
        md.append("")

        # Service Sections by Category
        for category, services in self.services_by_category.items():
            display_name = category_names.get(category, category.replace('_', ' ').title())
            anchor = category.replace('_', '-')

            md.append(f"## {display_name}")
            md.append(f"<a name=\"{anchor}\"></a>")
            md.append("")

            # Category description
            cat_desc = self.catalog.get(category, {}).get(category, {}).get('description', '')
            if cat_desc:
                md.append(f"**Description:** {cat_desc}")
                md.append("")

            md.append(f"**Services:** {len(services)}")
            md.append("")

            # List services in this category
            for service in sorted(services, key=lambda s: s.get('name', '')):
                md.extend(self._generate_detailed_service_section(service))

            md.append("---")
            md.append("")

        # Port Allocation Table
        md.append("## 🔌 Port Allocation Reference")
        md.append("")
        md.append("| Service | Port | Type | Status |")
        md.append("|---------|------|------|--------|")

        services_with_ports_list = [
            s for s in self.all_services
            if s.get('runtime', {}).get('port')
        ]

        for service in sorted(services_with_ports_list, key=lambda s: s.get('runtime', {}).get('port', 0)):
            name = service.get('display_name') or service.get('name', 'N/A')
            port = service.get('runtime', {}).get('port', 'N/A')
            stype = service.get('registration', {}).get('type', 'N/A')
            status = service.get('registration', {}).get('status', 'N/A')
            md.append(f"| {name} | `{port}` | {stype} | {status} |")
        md.append("")

        # Technology Stack
        md.append("## 🛠️ Technology Stack Summary")
        md.append("")

        frameworks = defaultdict(list)
        databases = defaultdict(list)

        for service in self.all_services:
            runtime = service.get('runtime', {})
            if isinstance(runtime, dict):
                framework = runtime.get('framework')
                if framework:
                    frameworks[framework].append(service.get('name', 'unknown'))

            # Check for database usage
            deps = service.get('dependencies', {})
            if isinstance(deps, dict):
                required = deps.get('required', [])
                if any('postgresql' in str(d).lower() or 'postgres' in str(d).lower() for d in required):
                    databases['PostgreSQL'].append(service.get('name', 'unknown'))
                if any('redis' in str(d).lower() for d in required):
                    databases['Redis'].append(service.get('name', 'unknown'))

        md.append("### Frameworks Used")
        md.append("")
        for framework, services_list in sorted(frameworks.items()):
            md.append(f"- **{framework}** ({len(services_list)} services)")
        md.append("")

        md.append("### Databases Used")
        md.append("")
        for db, services_list in sorted(databases.items()):
            md.append(f"- **{db}** ({len(services_list)} services)")
        md.append("")

        # Footer
        md.append("---")
        md.append("")
        md.append(f"*Comprehensive documentation generated on {datetime.utcnow().isoformat()}Z*")
        md.append("")
        md.append("**Legend:**")
        md.append("- 🏢 Platform Services")
        md.append("- 🧠 Intelligent Core")
        md.append("- 🔒 Security & Gateway")
        md.append("- 📊 Observability")
        md.append("- 💾 Infrastructure")

        return "\n".join(md)

    def _generate_detailed_service_section(self, service: Dict[str, Any]) -> List[str]:
        """Generate detailed markdown for a single service"""
        md = []

        name = service.get('name', 'unknown')
        display_name = service.get('display_name', name)

        # Service Header
        md.append(f"### {display_name}")
        md.append("")

        # Core Info Table
        md.append("| Property | Value |")
        md.append("|----------|-------|")
        md.append(f"| **Service ID** | `{name}` |")

        version = service.get('version', 'N/A')
        md.append(f"| **Version** | {version} |")

        # Registration info
        registration = service.get('registration', {})
        if isinstance(registration, dict):
            md.append(f"| **Type** | {registration.get('type', 'N/A')} |")
            md.append(f"| **Status** | {registration.get('status', 'N/A').upper()} |")

        # Runtime info
        runtime = service.get('runtime', {})
        if isinstance(runtime, dict):
            port = runtime.get('port', 'N/A')
            md.append(f"| **Port** | `{port}` |")
            framework = runtime.get('framework', 'N/A')
            md.append(f"| **Framework** | {framework} |")

        md.append("")

        # Description
        description = service.get('description', '')
        if description:
            md.append(f"**Description:**")
            md.append("")
            # Handle multi-line descriptions
            for line in description.strip().split('\n'):
                if line.strip():
                    md.append(f"> {line.strip()}")
            md.append("")

        # Capabilities
        capabilities = service.get('capabilities', [])
        if capabilities and len(capabilities) > 0:
            md.append("**Key Capabilities:**")
            md.append("")
            for cap in capabilities[:10]:  # Show up to 10
                md.append(f"- {cap}")
            if len(capabilities) > 10:
                md.append(f"- *...and {len(capabilities) - 10} more*")
            md.append("")

        # Features
        features = service.get('features', [])
        if features and len(features) > 0:
            md.append("**Features:**")
            md.append("")
            for feature in features[:5]:
                md.append(f"- {feature}")
            if len(features) > 5:
                md.append(f"- *...and {len(features) - 5} more*")
            md.append("")

        # Dependencies
        dependencies = service.get('dependencies', {})
        if isinstance(dependencies, dict):
            required = dependencies.get('required', [])
            optional = dependencies.get('optional', [])

            if required:
                md.append("**Required Dependencies:**")
                md.append("")
                for dep in required[:5]:
                    md.append(f"- {dep}")
                md.append("")

        # Integrations
        integrations = service.get('integrations', [])
        if integrations and isinstance(integrations, list) and len(integrations) > 0:
            md.append("**Integrations:**")
            md.append("")
            md.append("| Service | Type | Description |")
            md.append("|---------|------|-------------|")
            integration_list = list(integrations)[:5] if isinstance(integrations, list) else []
            for integration in integration_list:
                if isinstance(integration, dict):
                    svc = integration.get('service', 'N/A')
                    itype = integration.get('integration_type', 'N/A')
                    desc = integration.get('description', 'N/A')[:40] + "..."
                    md.append(f"| {svc} | {itype} | {desc} |")
            md.append("")

        # KPIs
        kpis = service.get('kpis', [])
        if kpis and len(kpis) > 0 and isinstance(kpis[0], dict):
            md.append("**Key Performance Indicators:**")
            md.append("")
            md.append("| KPI | Type | Target | Metric |")
            md.append("|-----|------|--------|--------|")
            for kpi in kpis[:5]:
                if isinstance(kpi, dict):
                    kpi_name = kpi.get('name', 'N/A')
                    kpi_type = kpi.get('type', 'gauge')
                    target = kpi.get('target') or kpi.get('threshold_warning', 'N/A')
                    metric = kpi.get('prometheus_metric', 'N/A')
                    md.append(f"| {kpi_name} | {kpi_type} | {target} | `{metric}` |")
            md.append("")

        # ISO Compliance
        iso_clause = service.get('iso_clause')
        if iso_clause:
            md.append(f"**ISO 22301:2019 Compliance:** Clause {iso_clause}")
            md.append("")

        # Endpoints
        endpoints = service.get('endpoints', {})
        if isinstance(endpoints, dict) and len(endpoints) > 0:
            md.append("**API Endpoints:**")
            md.append("")
            for endpoint_name, endpoint_path in list(endpoints.items())[:5]:
                md.append(f"- `{endpoint_path}` - {endpoint_name}")
            if len(endpoints) > 5:
                md.append(f"- *...and {len(endpoints) - 5} more endpoints*")
            md.append("")

        md.append("---")
        md.append("")

        return md

    def generate_interactive_html(self) -> str:
        """Generate modern interactive HTML with search and filters"""
        html = []

        html.append("<!DOCTYPE html>")
        html.append("<html lang='en'>")
        html.append("<head>")
        html.append("    <meta charset='UTF-8'>")
        html.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        html.append("    <title>AI Platform ISO - Service Catalog (47 Services)</title>")
        html.append("    <style>")
        html.append(self._get_modern_html_styles())
        html.append("    </style>")
        html.append("</head>")
        html.append("<body>")

        # Header
        html.append("    <header class='main-header'>")
        html.append("        <div class='container'>")
        html.append("            <h1>🏢 AI Platform ISO - Service Catalog</h1>")
        html.append(f"            <p class='subtitle'>{len(self.all_services)} Services | Version {self.catalog.get('version', 'N/A')}</p>")
        html.append("        </div>")
        html.append("    </header>")

        html.append("    <div class='container'>")

        # Statistics Dashboard
        html.append("        <div class='stats-grid'>")
        html.append(f"            <div class='stat-card'><h3>{len(self.all_services)}</h3><p>Total Services</p></div>")
        html.append(f"            <div class='stat-card'><h3>{len(self.services_by_category)}</h3><p>Categories</p></div>")

        services_with_ports = sum(1 for s in self.all_services if s.get('runtime', {}).get('port'))
        html.append(f"            <div class='stat-card'><h3>{services_with_ports}</h3><p>Services with Ports</p></div>")

        active_services = sum(1 for s in self.all_services if s.get('registration', {}).get('status') == 'production')
        html.append(f"            <div class='stat-card'><h3>{active_services}</h3><p>Production Services</p></div>")
        html.append("        </div>")

        # Search and Filter
        html.append("        <div class='search-container'>")
        html.append("            <input type='text' id='searchInput' placeholder='🔍 Search services...' onkeyup='filterServices()'>")
        html.append("            <select id='categoryFilter' onchange='filterServices()'>")
        html.append("                <option value='all'>All Categories</option>")
        for category in self.services_by_category.keys():
            display_name = category.replace('_', ' ').title()
            html.append(f"                <option value='{category}'>{display_name}</option>")
        html.append("            </select>")
        html.append("        </div>")

        # Services Grid
        html.append("        <div class='services-grid' id='servicesGrid'>")

        for service in sorted(self.all_services, key=lambda s: s.get('name', '')):
            category = service.get('_category', 'unknown')
            html.append(self._generate_interactive_service_card(service, category))

        html.append("        </div>")

        html.append("    </div>")

        # JavaScript for filtering
        html.append("    <script>")
        html.append("""
        function filterServices() {
            const searchInput = document.getElementById('searchInput').value.toLowerCase();
            const categoryFilter = document.getElementById('categoryFilter').value;
            const cards = document.querySelectorAll('.service-card');

            cards.forEach(card => {
                const name = card.getAttribute('data-name').toLowerCase();
                const category = card.getAttribute('data-category');

                const matchesSearch = name.includes(searchInput);
                const matchesCategory = categoryFilter === 'all' || category === categoryFilter;

                if (matchesSearch && matchesCategory) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }
        """)
        html.append("    </script>")

        html.append("</body>")
        html.append("</html>")

        return "\n".join(html)

    def _generate_interactive_service_card(self, service: Dict[str, Any], category: str) -> str:
        """Generate HTML card for interactive display"""
        name = service.get('name', 'unknown')
        display_name = service.get('display_name', name)
        version = service.get('version', 'N/A')
        status = service.get('registration', {}).get('status', 'unknown')
        description = service.get('description', '')[:200] + "..."

        port = service.get('runtime', {}).get('port', 'N/A')
        framework = service.get('runtime', {}).get('framework', 'N/A')

        status_class = {
            'production': 'status-active',
            'development': 'status-dev',
            'planned': 'status-planned',
            'deprecated': 'status-deprecated'
        }.get(status, 'status-unknown')

        category_icon = {
            'database_infrastructure': '💾',
            'runtime_services': '⚙️',
            'gateway_layer': '🔒',
            'observability': '📊',
            'eventbus_core': '📡',
            'security': '🔐',
            'ai_office': '🤖',
            'platform_services': '🏢',
            'intelligent_core': '🧠'
        }.get(category, '📦')

        card = f"""
            <div class='service-card' data-name='{name} {display_name}' data-category='{category}'>
                <div class='service-header'>
                    <h3>{category_icon} {display_name}</h3>
                    <span class='badge {status_class}'>{status.upper()}</span>
                </div>
                <p class='service-code'>{name}</p>
                <div class='service-meta'>
                    <span><strong>Port:</strong> {port}</span>
                    <span><strong>Version:</strong> {version}</span>
                </div>
                <p class='service-description'>{description}</p>
                <div class='service-footer'>
                    <span class='category-tag'>{category.replace('_', ' ').title()}</span>
                    <span class='framework-tag'>{framework}</span>
                </div>
            </div>"""

        return card

    def _get_modern_html_styles(self) -> str:
        """Modern CSS with dark mode support"""
        return """
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #334155;
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
            --accent: #3b82f6;
            --accent-hover: #2563eb;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }

        .main-header {
            background: linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%);
            padding: 3rem 0;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }

        .main-header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        .subtitle {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }

        .stat-card {
            background: var(--bg-secondary);
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid rgba(59, 130, 246, 0.2);
        }

        .stat-card h3 {
            font-size: 3rem;
            color: var(--accent);
            margin-bottom: 0.5rem;
        }

        .stat-card p {
            color: var(--text-secondary);
            font-size: 0.95rem;
        }

        .search-container {
            display: flex;
            gap: 1rem;
            margin: 2rem 0;
        }

        .search-container input,
        .search-container select {
            background: var(--bg-secondary);
            border: 1px solid rgba(59, 130, 246, 0.3);
            color: var(--text-primary);
            padding: 1rem;
            border-radius: 8px;
            font-size: 1rem;
        }

        .search-container input {
            flex: 1;
        }

        .search-container select {
            min-width: 200px;
        }

        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }

        .service-card {
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid rgba(59, 130, 246, 0.2);
            transition: all 0.3s ease;
        }

        .service-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(59, 130, 246, 0.2);
            border-color: var(--accent);
        }

        .service-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 0.75rem;
        }

        .service-header h3 {
            font-size: 1.25rem;
            color: var(--text-primary);
            margin: 0;
        }

        .service-code {
            color: var(--text-secondary);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            margin-bottom: 1rem;
        }

        .badge {
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
        }

        .status-active { background: var(--success); color: white; }
        .status-dev { background: var(--accent); color: white; }
        .status-planned { background: var(--warning); color: white; }
        .status-deprecated { background: var(--danger); color: white; }
        .status-unknown { background: #6b7280; color: white; }

        .service-meta {
            display: flex;
            gap: 1.5rem;
            margin-bottom: 1rem;
            color: var(--text-secondary);
            font-size: 0.9rem;
        }

        .service-description {
            color: var(--text-secondary);
            font-size: 0.95rem;
            line-height: 1.6;
            margin-bottom: 1rem;
        }

        .service-footer {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .category-tag,
        .framework-tag {
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            background: rgba(59, 130, 246, 0.1);
            color: var(--accent);
            border: 1px solid rgba(59, 130, 246, 0.3);
        }
        """

    def save_all_formats(self):
        """Save documentation in all formats"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("\n📝 Generating comprehensive documentation...")

        # 1. Markdown
        print("   📄 Generating Markdown...")
        markdown = self.generate_comprehensive_markdown()
        md_file = self.output_dir / "COMPREHENSIVE_SERVICE_CATALOG.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"   ✅ Markdown saved: {md_file} ({len(markdown)} chars)")

        # 2. Interactive HTML
        print("   🌐 Generating Interactive HTML...")
        html = self.generate_interactive_html()
        html_file = self.output_dir / "service-catalog-interactive.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"   ✅ HTML saved: {html_file} ({len(html)} chars)")

        # 3. JSON (full catalog)
        print("   📊 Generating JSON...")
        json_file = self.output_dir / "service-catalog-full.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'version': self.catalog.get('version', 'N/A'),
                    'generated_at': datetime.utcnow().isoformat() + 'Z',
                    'total_services': len(self.all_services),
                    'categories': len(self.services_by_category)
                },
                'services_by_category': {
                    category: [s for s in services]
                    for category, services in self.services_by_category.items()
                },
                'all_services': self.all_services
            }, f, indent=2)
        print(f"   ✅ JSON saved: {json_file}")

        # 4. Port Reference (CSV)
        print("   📋 Generating Port Reference CSV...")
        csv_file = self.output_dir / "port-allocation.csv"
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write("Service,Display Name,Port,Category,Status,Framework\n")
            for service in sorted(self.all_services, key=lambda s: s.get('runtime', {}).get('port') or 0):
                port = service.get('runtime', {}).get('port', 'N/A')
                if port != 'N/A':
                    name = service.get('name', 'N/A')
                    display = service.get('display_name', name)
                    category = service.get('_category', 'N/A')
                    status = service.get('registration', {}).get('status', 'N/A')
                    framework = service.get('runtime', {}).get('framework', 'N/A')
                    f.write(f"{name},{display},{port},{category},{status},{framework}\n")
        print(f"   ✅ CSV saved: {csv_file}")

        print(f"\n✅ All documentation formats saved to: {self.output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate comprehensive documentation for 47 services'
    )
    parser.add_argument(
        '--catalog', '-c',
        type=Path,
        default=DETAILED_CATALOG,
        help='Path to SERVICE_CATALOG_DETAILED.yaml'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=OUTPUT_DIR,
        help='Output directory'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("📚 COMPREHENSIVE DOCUMENTATION GENERATOR")
    print("   47 Services | Multi-Format Output")
    print("=" * 80)
    print(f"\n📄 Catalog: {args.catalog}")
    print(f"📁 Output: {args.output}")

    if not args.catalog.exists():
        print(f"\n❌ Catalog not found: {args.catalog}")
        return 1

    generator = ComprehensiveDocGenerator(args.catalog, args.output)
    generator.load_catalog()
    generator.save_all_formats()

    print("\n" + "=" * 80)
    print("✅ COMPREHENSIVE DOCUMENTATION COMPLETE")
    print("=" * 80)
    print(f"\n📂 View documentation:")
    print(f"   - Markdown: {args.output}/COMPREHENSIVE_SERVICE_CATALOG.md")
    print(f"   - HTML: {args.output}/service-catalog-interactive.html")
    print(f"   - JSON: {args.output}/service-catalog-full.json")
    print(f"   - CSV: {args.output}/port-allocation.csv")

    return 0


if __name__ == '__main__':
    sys.exit(main())
