#!/usr/bin/env python3
"""
GitHub Pages Documentation Generator
Автоматически обновляет docs/ из catalogs/ и других источников
"""

import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import sys

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
CATALOGS_DIR = REPO_ROOT / "catalogs"
DOCS_DIR = REPO_ROOT / "docs"
INFRASTRUCTURE_DIR = REPO_ROOT / "infrastructure"


class DocsGenerator:
    """Main documentation generator"""

    def __init__(self):
        self.stats = {
            "services_count": 0,
            "subsystems_count": 0,
            "systems_count": 0,
            "last_updated": datetime.now().isoformat()
        }

    def load_yaml(self, file_path: Path) -> Dict:
        """Load YAML file safely"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"️  Error loading {file_path}: {e}")
            return {}

    def load_json(self, file_path: Path) -> Dict:
        """Load JSON file safely"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"️  Error loading {file_path}: {e}")
            return {}

    def parse_service_catalog(self) -> Dict[str, Any]:
        """Parse SERVICE_CATALOG_DETAILED.yaml"""
        catalog_path = CATALOGS_DIR / "platform-services" / "SERVICE_CATALOG_DETAILED.yaml"

        if not catalog_path.exists():
            print(f" Service catalog not found: {catalog_path}")
            return {}

        print(f" Reading service catalog: {catalog_path}")
        catalog = self.load_yaml(catalog_path)

        # Count services
        total_services = 0
        services_by_category = {}

        for category, services in catalog.items():
            if category in ['version', 'generated_date', 'total_services', 'active_services', 'deprecated_services']:
                continue

            if isinstance(services, dict):
                category_count = len(services)
                total_services += category_count
                services_by_category[category] = {
                    'count': category_count,
                    'services': list(services.keys())
                }

        self.stats['services_count'] = total_services

        return {
            'version': catalog.get('version', '3.0.0'),
            'generated_date': catalog.get('generated_date'),
            'total_services': total_services,
            'categories': services_by_category,
            'raw_data': catalog
        }

    def parse_subsystems_catalog(self) -> Dict[str, Any]:
        """Parse SUBSYSTEMS_CATALOG.yaml"""
        catalog_path = CATALOGS_DIR / "subsystems" / "SUBSYSTEMS_CATALOG.yaml"

        if not catalog_path.exists():
            print(f" Subsystems catalog not found: {catalog_path}")
            return {}

        print(f" Reading subsystems catalog: {catalog_path}")
        catalog = self.load_yaml(catalog_path)

        subsystems = catalog.get('subsystems', [])
        self.stats['subsystems_count'] = len(subsystems)

        return {
            'version': catalog.get('version', '1.0.0'),
            'total': len(subsystems),
            'subsystems': subsystems
        }

    def parse_systems_catalog(self) -> Dict[str, Any]:
        """Parse SYSTEMS_CATALOG.yaml"""
        catalog_path = CATALOGS_DIR / "systems" / "SYSTEMS_CATALOG.yaml"

        if not catalog_path.exists():
            print(f" Systems catalog not found: {catalog_path}")
            return {}

        print(f" Reading systems catalog: {catalog_path}")
        catalog = self.load_yaml(catalog_path)

        # Try both 'functional_systems' and 'systems' keys
        systems = catalog.get('functional_systems', catalog.get('systems', []))
        self.stats['systems_count'] = len(systems)

        return {
            'version': catalog.get('version', '1.0.0'),
            'total': len(systems),
            'systems': systems
        }

    def parse_user_applications(self) -> Dict[str, Any]:
        """Parse USER_APPLICATIONS_CATALOG.yaml"""
        catalog_path = CATALOGS_DIR / "business-services" / "USER_APPLICATIONS_CATALOG.yaml"

        if not catalog_path.exists():
            print(f"️  User applications catalog not found: {catalog_path}")
            return {}

        print(f" Reading user applications catalog: {catalog_path}")
        catalog = self.load_yaml(catalog_path)

        return catalog

    def generate_stats_json(self, data: Dict[str, Any]) -> None:
        """Generate stats.json for JavaScript consumption"""
        stats_file = DOCS_DIR / "assets" / "stats.json"

        # Extract subsystem names
        subsystem_names = []
        if isinstance(data['subsystems']['subsystems'], list):
            subsystem_names = [s.get('name', s.get('id', '')) for s in data['subsystems']['subsystems']]

        # Extract system names
        system_names = []
        if isinstance(data['systems']['systems'], list):
            system_names = [s.get('name', s.get('id', '')) for s in data['systems']['systems']]

        stats = {
            "generated_at": datetime.now().isoformat(),
            "services": {
                "total": data['services']['total_services'],
                "platform": data['services']['total_services'] - 16,  # Minus user apps
                "applications": 16,
                "by_category": data['services']['categories']
            },
            "subsystems": {
                "total": data['subsystems']['total'],
                "list": subsystem_names
            },
            "systems": {
                "total": data['systems']['total'],
                "list": system_names
            },
            "ports": self.extract_ports(data['services']['raw_data'])
        }

        stats_file.parent.mkdir(parents=True, exist_ok=True)

        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        print(f" Generated: {stats_file}")

    def extract_ports(self, catalog: Dict) -> Dict[str, int]:
        """Extract port numbers from service catalog"""
        ports = {}

        for category, services in catalog.items():
            if category in ['version', 'generated_date', 'total_services', 'active_services', 'deprecated_services']:
                continue

            if isinstance(services, dict):
                for service_name, service_data in services.items():
                    if isinstance(service_data, dict):
                        runtime = service_data.get('runtime', {})
                        if isinstance(runtime, dict) and 'port' in runtime:
                            port = runtime['port']
                            if isinstance(port, int):
                                ports[service_name] = port

        return ports

    def generate_service_list_html(self, data: Dict[str, Any]) -> str:
        """Generate HTML for service list"""
        services = data['services']
        html_parts = []

        html_parts.append('<div class="services-grid">')

        for category, info in services['categories'].items():
            category_title = category.replace('_', ' ').title()

            html_parts.append(f'''
            <div class="service-category">
                <h3>{category_title}</h3>
                <p class="service-count">{info['count']} services</p>
                <ul class="service-list">
            ''')

            for service_name in sorted(info['services']):
                display_name = service_name.replace('_', ' ').replace('-', ' ').title()
                html_parts.append(f'<li>{display_name}</li>')

            html_parts.append('</ul></div>')

        html_parts.append('</div>')

        return '\n'.join(html_parts)

    def update_index_stats(self, data: Dict[str, Any]) -> None:
        """Update stats in index.html"""
        index_file = DOCS_DIR / "index.html"

        if not index_file.exists():
            print(f"️  index.html not found: {index_file}")
            return

        # Read current content
        content = index_file.read_text(encoding='utf-8')

        # Update stats
        stats = data['services']
        total_services = stats['total_services']

        # Simple string replacement for stats
        # Find and replace stats section
        import re

        # Update service count
        content = re.sub(
            r'<h4>\d+</h4>\s*<p>Platform Services</p>',
            f'<h4>{total_services}</h4>\n            <p>Platform Services</p>',
            content
        )

        # Update AI modules count (assuming intelligent_core category)
        ai_count = 17  # From intelligent_core
        content = re.sub(
            r'<h4>\d+</h4>\s*<p>AI Modules</p>',
            f'<h4>{ai_count}</h4>\n            <p>AI Modules</p>',
            content
        )

        # Write back
        index_file.write_text(content, encoding='utf-8')
        print(f" Updated: {index_file}")

    def generate_all(self) -> None:
        """Generate all documentation"""
        print("=" * 70)
        print(" DOCUMENTATION GENERATOR")
        print("=" * 70)
        print()

        # Parse all catalogs
        print(" Parsing catalogs...")
        services = self.parse_service_catalog()
        subsystems = self.parse_subsystems_catalog()
        systems = self.parse_systems_catalog()
        applications = self.parse_user_applications()

        data = {
            'services': services,
            'subsystems': subsystems,
            'systems': systems,
            'applications': applications
        }

        print()
        print(" Statistics:")
        print(f"  • Services: {services['total_services']}")
        print(f"  • Subsystems: {subsystems['total']}")
        print(f"  • Systems: {systems['total']}")
        print()

        # Generate outputs
        print(" Generating documentation...")
        self.generate_stats_json(data)
        self.update_index_stats(data)

        print()
        print("=" * 70)
        print(" DOCUMENTATION GENERATION COMPLETE!")
        print("=" * 70)
        print()
        print("Generated files:")
        print(f"  • {DOCS_DIR / 'assets' / 'stats.json'}")
        print(f"  • Updated {DOCS_DIR / 'index.html'}")
        print()
        print(f"Last updated: {self.stats['last_updated']}")
        print()


def main():
    """Main entry point"""
    generator = DocsGenerator()

    try:
        generator.generate_all()
        return 0
    except Exception as e:
        print(f" Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
