#!/usr/bin/env python3
"""
Update service-catalog-comprehensive page with latest data
"""

import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

REPO_ROOT = Path(__file__).parent.parent.parent
CATALOGS_DIR = REPO_ROOT / "catalogs"
DOCS_DIR = REPO_ROOT / "docs"


def load_yaml(file_path: Path) -> Dict:
    """Load YAML file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def generate_service_markdown(catalog: Dict) -> str:
    """Generate comprehensive markdown for all services"""
    lines = []

    lines.append("# 🏢 Comprehensive Service Catalog\n")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
    lines.append(f"**Version**: {catalog.get('version', '3.0.0')}\n")
    lines.append(f"**Total Services**: {catalog.get('total_services', 'N/A')}\n")
    lines.append("\n---\n")

    # Process each category
    for category, services in catalog.items():
        if category in ['version', 'generated_date', 'total_services', 'active_services', 'deprecated_services']:
            continue

        if not isinstance(services, dict):
            continue

        # Category header
        category_title = category.replace('_', ' ').title()
        lines.append(f"\n## {category_title}\n")
        lines.append(f"**Services in category**: {len(services)}\n")

        # Each service
        for service_name, service_data in services.items():
            if not isinstance(service_data, dict):
                continue

            lines.append(f"\n### {service_data.get('display_name', service_name)}\n")

            # Description
            description = service_data.get('description', '').strip()
            if description:
                lines.append(f"{description}\n")

            # Runtime info
            runtime = service_data.get('runtime', {})
            if runtime:
                lines.append("\n**Runtime:**\n")
                if 'port' in runtime:
                    lines.append(f"- Port: `{runtime['port']}`\n")
                if 'protocol' in runtime:
                    lines.append(f"- Protocol: {runtime['protocol']}\n")
                if 'url' in runtime:
                    url = runtime['url']
                    # Mask passwords in URLs
                    if '<password>' not in url and '@' in url:
                        url = url.replace(':' + url.split(':')[2].split('@')[0], ':<password>')
                    lines.append(f"- URL: `{url}`\n")

            # Capabilities
            capabilities = service_data.get('capabilities', [])
            if capabilities:
                lines.append("\n**Capabilities:**\n")
                for cap in capabilities[:5]:  # Limit to 5
                    lines.append(f"- {cap}\n")
                if len(capabilities) > 5:
                    lines.append(f"- ... and {len(capabilities) - 5} more\n")

            # Features
            features = service_data.get('features', [])
            if features:
                lines.append("\n**Features:**\n")
                for feat in features[:5]:
                    lines.append(f"- {feat}\n")
                if len(features) > 5:
                    lines.append(f"- ... and {len(features) - 5} more\n")

            # Dependencies
            dependencies = service_data.get('dependencies', {})
            if dependencies:
                required = dependencies.get('required', [])
                if required:
                    lines.append("\n**Required Dependencies:**\n")
                    for dep in required:
                        lines.append(f"- {dep}\n")

            # KPIs
            kpis = service_data.get('kpis', [])
            if kpis:
                lines.append("\n**Key Performance Indicators:**\n")
                for kpi in kpis[:3]:
                    if isinstance(kpi, dict):
                        kpi_name = kpi.get('name', 'Unknown')
                        kpi_desc = kpi.get('description', '')
                        lines.append(f"- **{kpi_name}**: {kpi_desc}\n")

            lines.append("\n---\n")

    return ''.join(lines)


def update_comprehensive_page():
    """Update the comprehensive service catalog page"""
    catalog_path = CATALOGS_DIR / "platform-services" / "SERVICE_CATALOG_DETAILED.yaml"

    if not catalog_path.exists():
        print(f"❌ Service catalog not found: {catalog_path}")
        return

    print(f"📖 Reading service catalog...")
    catalog = load_yaml(catalog_path)

    print(f"🔨 Generating markdown...")
    markdown = generate_service_markdown(catalog)

    # Save markdown
    output_md = DOCS_DIR / "service-catalog-comprehensive" / "COMPREHENSIVE_SERVICE_CATALOG.md"
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(markdown, encoding='utf-8')

    print(f"✅ Updated: {output_md}")

    # Also save as JSON for JavaScript
    output_json = DOCS_DIR / "service-catalog-comprehensive" / "service-catalog-full.json"
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"✅ Updated: {output_json}")


if __name__ == "__main__":
    update_comprehensive_page()
    print("\n✅ Service catalog page updated successfully!")
