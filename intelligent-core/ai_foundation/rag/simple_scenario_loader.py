"""
Simple Scenario Loader - Parse catalog without heavy dependencies

Parses ALL_USAGE_SCENARIOS_CATALOG.md and creates structured JSON
for later loading to RAG when Qdrant is ready.
"""

import os
import json
import logging
from typing import List, Dict
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_catalog(catalog_path: str) -> List[Dict]:
    """
    Parse ALL_USAGE_SCENARIOS_CATALOG.md into structured scenarios

    Returns:
        List of scenarios with metadata
    """
    with open(catalog_path, 'r', encoding='utf-8') as f:
        content = f.read()

    scenarios = []
    current_service = None
    current_category = None

    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Detect service headers (### 1. BIA Service - 25 сценариев)
        if line.startswith('###') and 'Service' in line and ('сценариев' in line or 'scenarios' in line.lower()):
            # Extract service name
            parts = line.split('.')
            if len(parts) > 1:
                service_part = parts[1].split('-')[0].strip()
                current_service = service_part.replace('Service', '').strip()
                logger.info(f"Found service: {current_service}")

        # Detect category headers (#### Основные сценарии)
        elif line.startswith('####'):
            current_category = line.replace('#', '').strip()

        # Detect scenario (**1.1 Start New BIA**)
        elif line.startswith('**') and '.' in line[:10] and not line.startswith('**Входы') and not line.startswith('**Input'):
            scenario_title = line.replace('**', '').strip()

            # Extract scenario details
            scenario = {
                'title': scenario_title,
                'service': current_service or 'Unknown',
                'category': current_category or 'General',
                'inputs': '',
                'outputs': '',
                'events': '',
                'components': '',
                'description': ''
            }

            # Read next lines for details
            j = i + 1
            description_lines = []
            while j < len(lines) and not lines[j].startswith('**'):
                detail_line = lines[j].strip()

                if detail_line.startswith('- Входы:') or detail_line.startswith('- Inputs:'):
                    scenario['inputs'] = detail_line.split(':', 1)[1].strip() if ':' in detail_line else ''
                elif detail_line.startswith('- Выходы:') or detail_line.startswith('- Outputs:'):
                    scenario['outputs'] = detail_line.split(':', 1)[1].strip() if ':' in detail_line else ''
                elif detail_line.startswith('- События:') or detail_line.startswith('- Events:'):
                    scenario['events'] = detail_line.split(':', 1)[1].strip() if ':' in detail_line else ''
                elif detail_line.startswith('- Компоненты:') or detail_line.startswith('- Components:'):
                    scenario['components'] = detail_line.split(':', 1)[1].strip() if ':' in detail_line else ''
                elif detail_line and not detail_line.startswith('-'):
                    description_lines.append(detail_line)

                j += 1

            scenario['description'] = ' '.join(description_lines) if description_lines else scenario_title
            scenarios.append(scenario)

        i += 1

    logger.info(f"✅ Parsed {len(scenarios)} scenarios from catalog")
    return scenarios


def save_scenarios_json(scenarios: List[Dict], output_path: str):
    """Save parsed scenarios to JSON file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(scenarios, f, ensure_ascii=False, indent=2)

    logger.info(f"✅ Saved {len(scenarios)} scenarios to {output_path}")


def generate_statistics(scenarios: List[Dict]) -> Dict:
    """Generate statistics about scenarios"""

    services = {}
    categories = {}

    for scenario in scenarios:
        service = scenario['service']
        category = scenario['category']

        services[service] = services.get(service, 0) + 1
        categories[category] = categories.get(category, 0) + 1

    return {
        'total_scenarios': len(scenarios),
        'services': services,
        'categories': categories,
        'unique_services': len(services),
        'unique_categories': len(categories)
    }


def main():
    """Main script to parse catalog"""

    # Path to catalog
    catalog_path = "/Users/MD/AI-Platform-ISO/platform-services/docs/business-scenarios/ALL_USAGE_SCENARIOS_CATALOG.md"
    output_dir = "/Users/MD/AI-Platform-ISO/platform-services/docs/business-scenarios"

    if not os.path.exists(catalog_path):
        logger.error(f"Catalog not found: {catalog_path}")
        return

    logger.info(f"📖 Reading catalog from: {catalog_path}")

    # Parse catalog
    scenarios = parse_catalog(catalog_path)

    # Save as JSON
    json_path = os.path.join(output_dir, "scenarios_parsed.json")
    save_scenarios_json(scenarios, json_path)

    # Generate statistics
    stats = generate_statistics(scenarios)
    logger.info("\n📊 Statistics:")
    logger.info(f"  Total scenarios: {stats['total_scenarios']}")
    logger.info(f"  Unique services: {stats['unique_services']}")
    logger.info(f"  Unique categories: {stats['unique_categories']}")

    logger.info("\n🎯 By Service:")
    for service, count in sorted(stats['services'].items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  {service}: {count} scenarios")

    logger.info("\n📁 By Category:")
    for category, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True)[:10]:
        logger.info(f"  {category}: {count} scenarios")

    logger.info(f"\n✅ Done! JSON saved to: {json_path}")
    logger.info(f"   File size: {os.path.getsize(json_path) / 1024:.1f} KB")

    # Create example search function
    def search_scenarios(query: str, scenarios: List[Dict]) -> List[Dict]:
        """Simple keyword search"""
        query_lower = query.lower()
        results = []

        for scenario in scenarios:
            searchable_text = f"{scenario['title']} {scenario['description']} {scenario['components']} {scenario['events']}".lower()
            if query_lower in searchable_text:
                results.append(scenario)

        return results

    # Test search
    logger.info("\n🔍 Testing search:")
    test_query = "BIA"
    results = search_scenarios(test_query, scenarios)
    logger.info(f"  Query: '{test_query}'")
    logger.info(f"  Found: {len(results)} scenarios")
    if results:
        logger.info(f"  Example: {results[0]['title']}")


if __name__ == "__main__":
    main()
