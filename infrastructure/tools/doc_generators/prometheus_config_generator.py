#!/usr/bin/env python3
"""
Prometheus Configuration Generator

Автоматически генерирует prometheus.yml конфигурацию на основе API map.
Обнаруживает все сервисы с /health и /metrics endpoints.

Usage:
    python3 tools/generators/prometheus_config_generator.py

Outputs:
    - infrastructure/observability/config/prometheus/prometheus-auto.yml
    - infrastructure/observability/config/prometheus/sd_configs/services.json
"""

import json
import os
import yaml
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict

# Paths
PROJECT_ROOT = Path("/Users/MD/AI-Platform-ISO")
API_MAP_PATH = PROJECT_ROOT / "tools/reports/api_map.json"
PROMETHEUS_CONFIG_DIR = PROJECT_ROOT / "infrastructure/observability/config/prometheus"
OUTPUT_CONFIG_PATH = PROMETHEUS_CONFIG_DIR / "prometheus-auto.yml"
SD_CONFIGS_DIR = PROMETHEUS_CONFIG_DIR / "sd_configs"

# Service port mapping (известные порты из документации)
KNOWN_PORTS = {
    # Platform Services
    'planning-service': 8011,
    'bia-service': 8012,
    'risk-service': 8013,
    'compliance-service': 8014,
    'response-service': 8015,
    'validation-service': 8016,
    'governance-service': 8017,
    'learning-service': 8018,
    'supply-chain-service': 8019,
    'stakeholder-service': 8020,
    'exercises-service': 8021,
    'scenario-service': 8022,
    'plans-service': 8023,
    'documents-service': 8024,

    # Community Services
    'community-portal': 8031,
    'marketplace-service': 8032,

    # Living Docs
    'living-docs': 8034,

    # Notification
    'notification-service': 8035,

    # Infrastructure
    'api-gateway': 8000,
    'eventbus': 8001,
    'orchestration': 8002,
    'realtime-websocket': 8003,
    'process-mining': 8004,
    'deployment-service': 8005,

    # Intelligent Core
    'predictive': 8030,
    'collective': 8033,
    'community-intelligence': 8030,
    'coordination-center': 8007,

    # Observability
    'monitoring': 8008,
    'mio-manager': 8009,

    # Monitoring Stack
    'prometheus': 9090,
    'grafana': 3000,
    'alertmanager': 9093,
    'loki': 3100,
    'tempo': 3200,
    'node-exporter': 9100,
}


def load_api_map() -> Dict:
    """Load API map from reports"""
    print(f"📂 Loading API map from {API_MAP_PATH}")
    with open(API_MAP_PATH, 'r') as f:
        return json.load(f)


def extract_services_from_api_map(api_map: Dict) -> Dict[str, Any]:
    """
    Extract unique services with their endpoints from API map

    Returns:
        Dict with service_name -> {
            'endpoints': [...],
            'has_health': bool,
            'has_metrics': bool,
            'file_paths': [...]
        }
    """
    services = defaultdict(lambda: {
        'endpoints': set(),
        'has_health': False,
        'has_metrics': False,
        'file_paths': set()
    })

    # Scan HTTP APIs (structure is api_map['apis']['http_apis'])
    http_apis = api_map.get('apis', {}).get('http_apis', [])
    for api in http_apis:
        file_path = api.get('file', '')

        # Determine service name from file path
        service_name = extract_service_name(file_path)
        if not service_name:
            continue

        # Track endpoint
        method = api.get('method', 'GET')
        path = api.get('path', '/')
        services[service_name]['endpoints'].add(f"{method} {path}")
        services[service_name]['file_paths'].add(file_path)

        # Check for health and metrics endpoints
        if path == '/health' or path == '/api/health':
            services[service_name]['has_health'] = True
        if path == '/metrics' or path == '/api/metrics':
            services[service_name]['has_metrics'] = True

    # Convert sets to lists for JSON serialization
    for service in services.values():
        service['endpoints'] = sorted(list(service['endpoints']))
        service['file_paths'] = sorted(list(service['file_paths']))

    return dict(services)


def extract_service_name(file_path: str) -> str:
    """Extract service name from file path"""
    # Remove project root
    path = file_path.replace('/Users/MD/AI-Platform-ISO/', '')

    # Extract service name patterns
    if 'platform-services/' in path:
        # platform-services/planning-service/... -> planning-service
        parts = path.split('platform-services/')[1].split('/')
        return parts[0] if parts else None

    elif 'infrastructure/observability/' in path:
        # infrastructure/observability/monitoring/... -> monitoring
        # infrastructure/observability/notification-service/... -> notification-service
        parts = path.split('infrastructure/observability/')[1].split('/')
        return parts[0] if parts else None

    elif 'infrastructure/gateway/' in path:
        parts = path.split('infrastructure/gateway/')[1].split('/')
        return parts[0] if parts else None

    elif 'infrastructure/runtime/' in path:
        parts = path.split('infrastructure/runtime/')[1].split('/')
        return parts[0] if parts else None

    elif 'infrastructure/integration/' in path:
        parts = path.split('infrastructure/integration/')[1].split('/')
        return parts[0] if parts else None

    elif 'intelligent-core/' in path:
        # intelligent-core/predictive/... -> predictive
        # intelligent-core/collective/... -> collective
        parts = path.split('intelligent-core/')[1].split('/')
        if parts[0] not in ['_archive', 'можетпригодится', 'ai-foundation', 'orchestration']:
            return parts[0]
        elif parts[0] == 'orchestration' and len(parts) > 1:
            return parts[1]  # coordination-center

    return None


def generate_prometheus_config(services: Dict[str, Any]) -> Dict:
    """Generate Prometheus configuration"""

    # Filter services with health or metrics endpoints
    monitorable_services = {
        name: data for name, data in services.items()
        if data['has_health'] or data['has_metrics']
    }

    print(f"\n📊 Found {len(monitorable_services)} monitorable services (with /health or /metrics)")

    scrape_configs = []

    # Add Prometheus self-monitoring
    scrape_configs.append({
        'job_name': 'prometheus',
        'static_configs': [{
            'targets': ['localhost:9090'],
            'labels': {
                'service': 'prometheus',
                'component': 'monitoring'
            }
        }]
    })

    # Add each service
    for service_name, service_data in sorted(monitorable_services.items()):
        port = KNOWN_PORTS.get(service_name, 8000)

        scrape_config = {
            'job_name': service_name,
            'scrape_interval': '15s',
            'scrape_timeout': '10s',
            'metrics_path': '/metrics',
            'static_configs': [{
                'targets': [f'{service_name}:{port}'],
                'labels': {
                    'service': service_name,
                    'has_health': str(service_data['has_health']).lower(),
                    'has_metrics': str(service_data['has_metrics']).lower()
                }
            }]
        }

        scrape_configs.append(scrape_config)

    # Build full config
    config = {
        'global': {
            'scrape_interval': '15s',
            'evaluation_interval': '15s',
            'external_labels': {
                'cluster': 'bcm-platform',
                'environment': 'production'
            }
        },
        'alerting': {
            'alertmanagers': [{
                'static_configs': [{
                    'targets': ['alertmanager:9093']
                }]
            }]
        },
        'rule_files': [
            '/etc/prometheus/rules/*.yml'
        ],
        'scrape_configs': scrape_configs
    }

    return config


def generate_service_discovery_config(services: Dict[str, Any]) -> List[Dict]:
    """Generate file-based service discovery config for Prometheus"""

    sd_targets = []

    for service_name, service_data in services.items():
        if not (service_data['has_health'] or service_data['has_metrics']):
            continue

        port = KNOWN_PORTS.get(service_name, 8000)

        target = {
            'targets': [f'{service_name}:{port}'],
            'labels': {
                'job': service_name,
                'service': service_name,
                '__metrics_path__': '/metrics',
                'has_health': str(service_data['has_health']).lower(),
                'has_metrics': str(service_data['has_metrics']).lower()
            }
        }

        sd_targets.append(target)

    return sd_targets


def main():
    """Main function"""
    print("🚀 Prometheus Configuration Generator")
    print("=" * 60)

    # Ensure output directories exist
    PROMETHEUS_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    SD_CONFIGS_DIR.mkdir(parents=True, exist_ok=True)

    # Load API map
    api_map = load_api_map()
    total_apis = len(api_map.get('apis', {}).get('http_apis', []))
    print(f"✅ Loaded {total_apis} HTTP APIs")

    # Extract services
    print("\n🔍 Extracting services from API map...")
    services = extract_services_from_api_map(api_map)
    print(f"✅ Found {len(services)} unique services")

    # Generate Prometheus config
    print("\n⚙️  Generating Prometheus configuration...")
    prom_config = generate_prometheus_config(services)

    # Write YAML config
    with open(OUTPUT_CONFIG_PATH, 'w') as f:
        yaml.dump(prom_config, f, default_flow_style=False, sort_keys=False, indent=2)
    print(f"✅ Written: {OUTPUT_CONFIG_PATH}")

    # Generate service discovery config
    print("\n⚙️  Generating service discovery config...")
    sd_config = generate_service_discovery_config(services)

    # Write service discovery JSON
    sd_output_path = SD_CONFIGS_DIR / 'services.json'
    with open(sd_output_path, 'w') as f:
        json.dump(sd_config, f, indent=2)
    print(f"✅ Written: {sd_output_path}")

    # Generate services inventory
    inventory_path = PROMETHEUS_CONFIG_DIR / 'services-inventory.json'
    with open(inventory_path, 'w') as f:
        json.dump(services, f, indent=2, default=str)
    print(f"✅ Written: {inventory_path}")

    # Summary
    print("\n📊 SUMMARY")
    print("=" * 60)
    print(f"Total services discovered: {len(services)}")
    print(f"Monitorable services: {len([s for s in services.values() if s['has_health'] or s['has_metrics']])}")
    print(f"Services with /health: {len([s for s in services.values() if s['has_health']])}")
    print(f"Services with /metrics: {len([s for s in services.values() if s['has_metrics']])}")
    print(f"\nScrape jobs configured: {len(prom_config['scrape_configs'])}")

    print("\n✅ Configuration generation complete!")
    print(f"\n📝 Next steps:")
    print(f"1. Review: {OUTPUT_CONFIG_PATH}")
    print(f"2. Copy to prometheus.yml: cp {OUTPUT_CONFIG_PATH} {PROMETHEUS_CONFIG_DIR}/prometheus.yml")
    print(f"3. Restart Prometheus: docker-compose -f infrastructure/observability/docker-compose.monitoring.yml restart prometheus")


if __name__ == '__main__':
    main()
