#!/usr/bin/env python3
"""
Improved Docker Compose Generator
==================================

Генерирует production-ready docker-compose.yml с:
- Profiles (dev, prod, observability)
- Networks
- Volumes
- Health checks
- Dependencies
- Resource limits

Usage:
    python3 tools/infrastructure/generate_improved_compose.py
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any


class ImprovedComposeGenerator:
    """Генерирует улучшенный Docker Compose"""

    def __init__(self, catalog_file: Path):
        self.catalog = self._load_catalog(catalog_file)
        self.services = self.catalog['services']

    def _load_catalog(self, catalog_file: Path) -> Dict:
        """Загружает service catalog"""
        with open(catalog_file) as f:
            return json.load(f)

    def generate(self) -> Dict[str, Any]:
        """Генерирует полный Docker Compose конфиг"""

        compose = {
            'version': '3.8',
            'services': {},
            'networks': self._generate_networks(),
            'volumes': self._generate_volumes()
        }

        # Группируем сервисы по типам
        core_services = [s for s in self.services if s['category'] == 'core']
        infra_services = [s for s in self.services if s['category'] == 'infrastructure']
        platform_services = [s for s in self.services if s['category'] == 'platform']

        # Генерируем сервисы с правильными profiles
        for service in core_services:
            compose['services'][service['name']] = self._generate_service(
                service,
                profiles=['dev', 'prod', 'core']
            )

        for service in infra_services:
            # Infrastructure services отдельно по типам
            if service['type'] == 'observability':
                profiles = ['dev', 'prod', 'observability']
            elif service['type'] == 'gateway':
                profiles = ['dev', 'prod']
            elif service['type'] == 'runtime':
                profiles = ['dev', 'prod']
            else:
                profiles = ['dev']

            compose['services'][service['name']] = self._generate_service(
                service,
                profiles=profiles
            )

        for service in platform_services:
            compose['services'][service['name']] = self._generate_service(
                service,
                profiles=['dev', 'prod', 'platform']
            )

        return compose

    def _generate_service(self, service: Dict, profiles: List[str]) -> Dict[str, Any]:
        """Генерирует конфигурацию одного сервиса"""

        config = {
            'container_name': f"bcm-{service['name']}",
            'profiles': profiles,
        }

        # Build или image
        if service['has_dockerfile']:
            config['build'] = {
                'context': f"../{service['path']}",
                'dockerfile': 'Dockerfile'
            }
        else:
            # Генерируем простой Dockerfile if missing
            config['build'] = {
                'context': f"../{service['path']}",
                'dockerfile': 'Dockerfile.auto'
            }

        # Ports
        config['ports'] = [f"{service['port']}:{service['port']}"]

        # Environment
        env_vars = service.get('environment', [])
        config['environment'] = [f"{var}=${{{var}}}" for var in env_vars]

        # Networks
        config['networks'] = ['bcm-network']

        # Volumes (если нужно persistence)
        if self._needs_volume(service):
            config['volumes'] = [f"{service['name']}-data:/data"]

        # Dependencies
        if service.get('dependencies'):
            config['depends_on'] = {}
            for dep in service['dependencies']:
                # Конвертируем название зависимости в service name
                dep_name = dep.replace('_', '-').lower()
                if dep_name.endswith('-libraries'):
                    continue  # shared libraries не сервис
                config['depends_on'][dep_name] = {
                    'condition': 'service_healthy'
                }

        # Health check
        config['healthcheck'] = {
            'test': f"curl -f http://localhost:{service['port']}{service['health_check']} || exit 1",
            'interval': '30s',
            'timeout': '10s',
            'retries': 3,
            'start_period': '40s'
        }

        # Resource limits
        config['deploy'] = {
            'resources': {
                'limits': self._get_resource_limits(service),
                'reservations': self._get_resource_reservations(service)
            }
        }

        # Restart policy
        config['restart'] = 'unless-stopped'

        # Logging
        config['logging'] = {
            'driver': 'json-file',
            'options': {
                'max-size': '10m',
                'max-file': '3'
            }
        }

        # Labels (для Prometheus service discovery)
        config['labels'] = {
            'prometheus.scrape': 'true',
            'prometheus.port': str(service['port']),
            'prometheus.path': service['metrics_endpoint'],
            'service.category': service['category'],
            'service.type': service['type']
        }

        return config

    def _needs_volume(self, service: Dict) -> bool:
        """Определяет нужен ли volume"""
        # Database services need volumes
        if service['type'] == 'database':
            return True
        # Observability services (prometheus, grafana)
        if service['type'] == 'observability':
            return True
        return False

    def _get_resource_limits(self, service: Dict) -> Dict[str, str]:
        """Определяет resource limits на основе типа сервиса"""
        # AI services need more resources
        if service['type'] == 'ai-service':
            return {
                'cpus': '2.0',
                'memory': '4G'
            }
        # Gateway services
        elif service['type'] == 'gateway':
            return {
                'cpus': '1.0',
                'memory': '2G'
            }
        # Database services
        elif service['type'] == 'database':
            return {
                'cpus': '2.0',
                'memory': '8G'
            }
        # Default
        else:
            return {
                'cpus': '0.5',
                'memory': '1G'
            }

    def _get_resource_reservations(self, service: Dict) -> Dict[str, str]:
        """Определяет resource reservations"""
        limits = self._get_resource_limits(service)
        return {
            'cpus': str(float(limits['cpus']) * 0.5),
            'memory': str(int(limits['memory'][:-1]) // 2) + limits['memory'][-1]
        }

    def _generate_networks(self) -> Dict[str, Any]:
        """Генерирует networks конфигурацию"""
        return {
            'bcm-network': {
                'driver': 'bridge',
                'name': 'bcm-network',
                'ipam': {
                    'config': [{
                        'subnet': '172.20.0.0/16'
                    }]
                }
            },
            'monitoring-network': {
                'driver': 'bridge',
                'name': 'monitoring-network'
            }
        }

    def _generate_volumes(self) -> Dict[str, Any]:
        """Генерирует volumes конфигурацию"""
        volumes = {}

        # Добавляем volumes для сервисов которым нужно persistence
        for service in self.services:
            if self._needs_volume(service):
                volumes[f"{service['name']}-data"] = {
                    'driver': 'local'
                }

        return volumes

    def save(self, output_file: Path):
        """Сохраняет конфигурацию"""
        compose = self.generate()

        with open(output_file, 'w') as f:
            yaml.dump(compose, f, default_flow_style=False, sort_keys=False)

        print(f"💾 Improved Docker Compose saved: {output_file}")

        # Также сохраняем README с инструкциями
        self._save_readme(output_file.parent)

    def _save_readme(self, output_dir: Path):
        """Сохраняет README с инструкциями"""
        readme_content = """# Docker Compose Usage Guide

## Profiles

This Docker Compose uses **profiles** to control which services start:

### Available Profiles:

1. **`dev`** - All services for development
2. **`prod`** - Production services only (no dev tools)
3. **`core`** - Only core AI modules (ai-foundation, workflow-intelligence, expertise-center)
4. **`platform`** - Only platform services (BIA, Risk, Compliance, etc.)
5. **`observability`** - Only monitoring stack (Prometheus, Grafana, etc.)

## Usage Examples

### Start everything (development):
```bash
docker-compose --profile dev up -d
```

### Start only core modules:
```bash
docker-compose --profile core up -d
```

### Start core + observability:
```bash
docker-compose --profile core --profile observability up -d
```

### Production deployment:
```bash
docker-compose --profile prod up -d
```

### Only monitoring stack:
```bash
docker-compose --profile observability up -d
```

## Networks

All services are in `bcm-network` (172.20.0.0/16)

Service-to-service communication:
```python
# From one service to another
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get('http://ai-foundation:9001/health')
```

## Volumes

Persistent volumes for:
- Database services
- Prometheus (metrics data)
- Grafana (dashboards)

## Health Checks

All services have health checks. Check status:
```bash
docker-compose ps
```

## Logs

View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ai-foundation

# Last 100 lines
docker-compose logs --tail=100
```

## Stop Services

```bash
# Stop all
docker-compose down

# Stop but keep volumes
docker-compose down -v

# Stop specific profile
docker-compose --profile observability down
```

## Resource Limits

Services have resource limits:
- AI services: 2 CPU, 4GB RAM
- Gateway: 1 CPU, 2GB RAM
- Other: 0.5 CPU, 1GB RAM

Adjust in docker-compose.improved.yml if needed.
"""

        readme_file = output_dir / 'DOCKER_COMPOSE_USAGE.md'
        readme_file.write_text(readme_content)
        print(f"📖 Usage guide saved: {readme_file}")


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent.parent

    print("=" * 60)
    print("🏗️ Generating Improved Docker Compose")
    print("=" * 60)

    # Load catalog
    catalog_file = project_root / 'infrastructure' / 'auto-generated' / 'service-catalog.json'

    if not catalog_file.exists():
        print("❌ service-catalog.json not found!")
        print("Run: python3 tools/infrastructure/discover_services.py first")
        return

    # Generate improved compose
    generator = ImprovedComposeGenerator(catalog_file)

    output_file = project_root / 'infrastructure' / 'auto-generated' / 'docker-compose.improved.yml'
    generator.save(output_file)

    print("\n" + "=" * 60)
    print("✅ Improved Docker Compose generated!")
    print("=" * 60)
    print("\nTest it:")
    print(f"  docker-compose -f {output_file} config")
    print("\nStart development:")
    print(f"  docker-compose -f {output_file} --profile dev up -d")
    print("\nStart only core modules:")
    print(f"  docker-compose -f {output_file} --profile core up -d")


if __name__ == '__main__':
    main()
