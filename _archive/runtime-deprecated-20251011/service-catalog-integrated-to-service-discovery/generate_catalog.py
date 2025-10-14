#!/usr/bin/env python3
"""
Auto-Catalog Generation Script
Scans all SERVICE_INFO.yaml files and generates unified service-catalog.yaml
for Service Discovery v2.0 integration.

Usage:
    python generate_catalog.py
    python generate_catalog.py --output custom-catalog.yaml
    python generate_catalog.py --validate-only
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Base directory for AI-Platform-ISO
BASE_DIR = Path(__file__).parent.parent.parent.parent
PLATFORM_SERVICES_DIR = BASE_DIR / "platform-services"
INTELLIGENT_CORE_DIR = BASE_DIR / "intelligent-core"
OUTPUT_FILE = BASE_DIR / "infrastructure/runtime/service-catalog/service-catalog.yaml"


class CatalogGenerator:
    """Generates unified service catalog from individual SERVICE_INFO.yaml files"""

    def __init__(self):
        self.services = []
        self.errors = []

    def scan_directory(self, directory: Path, category: str) -> List[Dict[str, Any]]:
        """Scan directory for SERVICE_INFO.yaml files"""
        found_services = []

        if not directory.exists():
            self.errors.append(f"Directory not found: {directory}")
            return found_services

        print(f"📂 Scanning {category}: {directory}")

        # Walk through all subdirectories
        for service_dir in directory.iterdir():
            if not service_dir.is_dir():
                continue

            # Look for SERVICE_INFO.yaml in service directory
            service_info_path = service_dir / "SERVICE_INFO.yaml"

            # For orchestration, check nested path
            if not service_info_path.exists() and service_dir.name == "orchestration":
                service_info_path = service_dir / "ai-orchestration" / "SERVICE_INFO.yaml"

            if service_info_path.exists():
                try:
                    with open(service_info_path, 'r', encoding='utf-8') as f:
                        service_data = yaml.safe_load(f)

                    # Add category metadata
                    service_data['_category'] = category
                    service_data['_source_file'] = str(service_info_path.relative_to(BASE_DIR))

                    found_services.append(service_data)
                    print(f"  ✅ {service_data.get('name', 'unknown')} ({service_data.get('runtime', {}).get('port', 'N/A')})")

                except Exception as e:
                    error_msg = f"Error reading {service_info_path}: {e}"
                    self.errors.append(error_msg)
                    print(f"  ❌ {error_msg}")

        return found_services

    def generate_catalog(self) -> Dict[str, Any]:
        """Generate unified catalog structure"""

        # Scan platform services
        platform_services = self.scan_directory(PLATFORM_SERVICES_DIR, "platform-services")

        # Scan intelligent core services
        intelligent_core_services = self.scan_directory(INTELLIGENT_CORE_DIR, "intelligent-core")

        # Combine all services
        all_services = platform_services + intelligent_core_services

        # Calculate statistics
        total_services = len(all_services)
        active_services = len([s for s in all_services if s.get('status') == 'active'])
        planned_services = len([s for s in all_services if s.get('status') == 'planned'])

        # Count total endpoints
        total_endpoints = 0
        for service in all_services:
            endpoints = service.get('endpoints', {})
            if isinstance(endpoints, dict):
                # Count API endpoints from features
                features = service.get('features', [])
                for feature in features:
                    if isinstance(feature, dict):
                        total_endpoints += feature.get('endpoints', 0)
            elif isinstance(endpoints, int):
                total_endpoints += endpoints

        # Port allocation
        platform_ports = sorted([
            s.get('runtime', {}).get('port')
            for s in platform_services
            if s.get('runtime', {}).get('port')
        ])

        intelligent_ports = sorted([
            s.get('runtime', {}).get('port')
            for s in intelligent_core_services
            if s.get('runtime', {}).get('port')
        ])

        # Build catalog structure
        catalog = {
            'metadata': {
                'platform_name': 'AI-Platform-ISO',
                'version': '2.0.0',
                'generated_at': datetime.utcnow().isoformat() + 'Z',
                'total_services': total_services,
                'categories': 2,
                'schema_version': '1.0.0',
                'generator': 'generate_catalog.py',
            },

            'platform_services': {
                'description': 'Business Continuity Management platform services implementing ISO 22301 requirements',
                'total': len(platform_services),
                'services': platform_services,
            },

            'intelligent_core': {
                'description': 'Intelligent automation and AI services for platform intelligence',
                'total': len(intelligent_core_services),
                'services': intelligent_core_services,
            },

            'statistics': {
                'by_status': {
                    'active': active_services,
                    'planned': planned_services,
                    'deprecated': 0,
                },
                'by_category': {
                    'platform-services': len(platform_services),
                    'intelligent-core': len(intelligent_core_services),
                },
                'port_allocation': {
                    'platform_services': self._format_port_range(platform_ports),
                    'intelligent_core': self._format_port_range(intelligent_ports),
                },
                'total_endpoints': f"{total_endpoints}+",
            },

            'technology_stack': {
                'languages': ['Python 3.11+'],
                'frameworks': ['FastAPI (all services)', 'SQLAlchemy (async)', 'Pydantic 2.4+'],
                'databases': ['PostgreSQL 14+ (primary)', 'Redis 7+ (caching, queues)'],
                'messaging': ['RabbitMQ 3.12+ (EventBus)'],
                'ai_ml': ['OpenAI GPT', 'Anthropic Claude', 'scikit-learn', 'spaCy'],
                'monitoring': ['Prometheus (metrics)', 'Grafana (dashboards)'],
                'standards': ['ISO 22301:2019', 'BPMN 2.0', 'ISO/IEC/IEEE 26514:2022'],
            },
        }

        # Add service discovery info
        catalog['service_discovery'] = {
            'url': 'http://localhost:8500',
            'api': '/v2/catalog/services',
            'health_checks': '/health (all services)',
            'integration': 'Service Discovery v2.0',
        }

        # Add monitoring info
        catalog['monitoring'] = {
            'prometheus': 'http://localhost:9090',
            'grafana': 'http://localhost:3000',
            'metrics_endpoint': '/metrics (all services)',
        }

        return catalog

    def _format_port_range(self, ports: List[int]) -> str:
        """Format port list into readable range string"""
        if not ports:
            return "N/A"

        if len(ports) == 1:
            return str(ports[0])

        # Find consecutive ranges
        ranges = []
        start = ports[0]
        end = ports[0]

        for port in ports[1:]:
            if port == end + 1:
                end = port
            else:
                if start == end:
                    ranges.append(str(start))
                else:
                    ranges.append(f"{start}-{end}")
                start = end = port

        # Add final range
        if start == end:
            ranges.append(str(start))
        else:
            ranges.append(f"{start}-{end}")

        return ", ".join(ranges)

    def validate_catalog(self, catalog: Dict[str, Any]) -> bool:
        """Validate catalog structure and data"""
        validation_errors = []

        # Check required top-level keys
        required_keys = ['metadata', 'platform_services', 'intelligent_core', 'statistics']
        for key in required_keys:
            if key not in catalog:
                validation_errors.append(f"Missing required key: {key}")

        # Validate services
        all_services = (
            catalog.get('platform_services', {}).get('services', []) +
            catalog.get('intelligent_core', {}).get('services', [])
        )

        for service in all_services:
            name = service.get('name', 'unknown')

            # Check required service fields
            required_service_fields = ['name', 'display_name', 'version', 'description', 'status', 'type']
            for field in required_service_fields:
                if field not in service:
                    validation_errors.append(f"Service '{name}' missing required field: {field}")

            # Validate runtime config
            runtime = service.get('runtime', {})
            if not runtime:
                validation_errors.append(f"Service '{name}' missing runtime configuration")
            elif 'port' not in runtime:
                validation_errors.append(f"Service '{name}' missing port in runtime config")

        # Print validation results
        if validation_errors:
            print("\n❌ VALIDATION FAILED:")
            for error in validation_errors:
                print(f"  - {error}")
            return False
        else:
            print("\n✅ VALIDATION PASSED")
            print(f"  - Total services: {len(all_services)}")
            print(f"  - Active services: {catalog['statistics']['by_status']['active']}")
            print(f"  - Planned services: {catalog['statistics']['by_status']['planned']}")
            return True

    def save_catalog(self, catalog: Dict[str, Any], output_path: Path):
        """Save catalog to YAML file"""
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write YAML with custom formatting
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("# " + "=" * 60 + "\n")
                f.write("# UNIFIED SERVICE CATALOG\n")
                f.write("# AI Platform ISO - Complete Service Registry\n")
                f.write("# " + "=" * 60 + "\n")
                f.write(f"# Auto-generated: true\n")
                f.write(f"# Generated at: {catalog['metadata']['generated_at']}\n")
                f.write(f"# Schema version: {catalog['metadata']['schema_version']}\n")
                f.write(f"# Total services: {catalog['metadata']['total_services']}\n")
                f.write("\n")

                yaml.dump(catalog, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

            print(f"\n✅ Catalog saved to: {output_path}")
            print(f"   Size: {output_path.stat().st_size / 1024:.2f} KB")

        except Exception as e:
            print(f"\n❌ Error saving catalog: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(
        description='Generate unified service catalog from SERVICE_INFO.yaml files'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=OUTPUT_FILE,
        help='Output file path (default: service-catalog.yaml)'
    )
    parser.add_argument(
        '--validate-only', '-v',
        action='store_true',
        help='Only validate existing catalog without regenerating'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress output except errors'
    )

    args = parser.parse_args()

    if not args.quiet:
        print("=" * 70)
        print("🔧 SERVICE CATALOG GENERATOR")
        print("=" * 70)

    generator = CatalogGenerator()

    # Validate existing catalog if requested
    if args.validate_only:
        if args.output.exists():
            with open(args.output, 'r', encoding='utf-8') as f:
                existing_catalog = yaml.safe_load(f)

            is_valid = generator.validate_catalog(existing_catalog)
            sys.exit(0 if is_valid else 1)
        else:
            print(f"❌ Catalog not found: {args.output}")
            sys.exit(1)

    # Generate catalog
    if not args.quiet:
        print("\n📋 Generating catalog...\n")

    catalog = generator.generate_catalog()

    # Validate
    if not generator.validate_catalog(catalog):
        print("\n❌ Generated catalog failed validation")
        sys.exit(1)

    # Save
    generator.save_catalog(catalog, args.output)

    # Print errors if any
    if generator.errors:
        print("\n⚠️  Warnings/Errors during generation:")
        for error in generator.errors:
            print(f"  - {error}")

    if not args.quiet:
        print("\n" + "=" * 70)
        print("✅ CATALOG GENERATION COMPLETE")
        print("=" * 70)
        print(f"\n📁 Output: {args.output}")
        print(f"📊 Services: {catalog['metadata']['total_services']}")
        print(f"🏃 Active: {catalog['statistics']['by_status']['active']}")
        print(f"📝 Planned: {catalog['statistics']['by_status']['planned']}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
