#!/usr/bin/env python3
"""
Automatic Service Discovery Tool
=================================

Автоматически обнаруживает все сервисы в проекте и генерирует
конфигурации для infrastructure на основе анализа кода.

Использует существующие analyzers:
- module_scanner.py
- api_mapper.py
- dependency_validator.py

Usage:
    python3 tools/infrastructure/discover_services.py

Output:
    - service-catalog.json
    - docker-compose.auto-generated.yml
    - prometheus.auto-generated.yml
    - api-gateway-routes.json
"""

import json
import yaml
import ast
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import subprocess

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class ServiceDiscovery:
    """Автоматическое обнаружение сервисов в проекте"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.services = []

    def discover_all(self) -> List[Dict[str, Any]]:
        """Сканирует весь проект и находит все сервисы"""
        print("🔍 Discovering services in project...")

        # Scan intelligent-core modules
        self._scan_directory(self.project_root / 'intelligent-core', 'core')

        # Scan infrastructure services
        self._scan_directory(self.project_root / 'infrastructure', 'infrastructure')

        # Scan platform-services
        if (self.project_root / 'platform-services').exists():
            self._scan_directory(self.project_root / 'platform-services', 'platform')

        print(f"\n✅ Found {len(self.services)} services")
        return self.services

    def _scan_directory(self, base_dir: Path, category: str):
        """Сканирует директорию на наличие сервисов"""
        if not base_dir.exists():
            return

        for item in base_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.') and not item.name.startswith('_'):
                service = self._analyze_service(item, category)
                if service:
                    self.services.append(service)
                    print(f"  ✓ {service['name']} (port {service['port']})")

    def _analyze_service(self, service_path: Path, category: str) -> Optional[Dict[str, Any]]:
        """Глубокий анализ одного сервиса"""

        # 1. Найти entry point (main.py, app.py, __init__.py)
        main_file = self._find_main_file(service_path)
        if not main_file:
            return None

        # 2. Извлечь информацию из кода
        port = self._extract_port(main_file)
        if not port:
            # Попробовать найти в requirements или README
            port = self._guess_port_from_context(service_path, category)

        # 3. Найти API endpoints
        endpoints = self._find_endpoints(service_path)

        # 4. Извлечь environment variables
        env_vars = self._extract_env_vars(service_path)

        # 5. Определить зависимости
        dependencies = self._analyze_dependencies(service_path)

        # 6. Определить тип сервиса
        service_type = self._detect_service_type(service_path, main_file)

        return {
            'name': service_path.name.replace('_', '-'),
            'display_name': service_path.name.replace('_', ' ').title(),
            'path': str(service_path.relative_to(self.project_root)),
            'category': category,
            'type': service_type,
            'port': port,
            'endpoints': endpoints[:10],  # Limit to first 10
            'environment': list(env_vars)[:20],  # Limit to first 20
            'dependencies': dependencies,
            'health_check': self._find_health_endpoint(endpoints),
            'metrics_endpoint': '/metrics',
            'has_dockerfile': (service_path / 'Dockerfile').exists(),
            'has_requirements': (service_path / 'requirements.txt').exists(),
        }

    def _find_main_file(self, service_path: Path) -> Optional[Path]:
        """Находит главный файл сервиса"""
        candidates = ['main.py', 'app.py', '__main__.py', 'server.py']

        for candidate in candidates:
            main_file = service_path / candidate
            if main_file.exists():
                return main_file

        # Поиск в подпапках
        for py_file in service_path.glob('**/main.py'):
            return py_file

        for py_file in service_path.glob('**/app.py'):
            return py_file

        return None

    def _extract_port(self, main_file: Path) -> Optional[int]:
        """Извлекает порт из кода"""
        try:
            content = main_file.read_text()

            # Pattern 1: uvicorn main:app --port 8000
            match = re.search(r'--port[=\s]+(\d+)', content)
            if match:
                return int(match.group(1))

            # Pattern 2: app.run(port=8000)
            match = re.search(r'port\s*=\s*(\d+)', content)
            if match:
                return int(match.group(1))

            # Pattern 3: PORT = 8000
            match = re.search(r'PORT\s*=\s*(\d+)', content)
            if match:
                return int(match.group(1))

            # Pattern 4: os.getenv('PORT', 8000)
            match = re.search(r'getenv\([\'"]PORT[\'"]\s*,\s*(\d+)', content)
            if match:
                return int(match.group(1))

        except Exception as e:
            pass

        return None

    def _guess_port_from_context(self, service_path: Path, category: str) -> int:
        """Угадывает порт на основе контекста"""
        name = service_path.name

        # Known services
        port_map = {
            'api-gateway': 8000,
            'ai-foundation': 9001,
            'workflow_intelligence': 9002,
            'workflow-intelligence': 9002,
            'expertise-center': 9003,
            'bia-service': 8010,
            'risk-service': 8011,
            'compliance-service': 8012,
            'prometheus': 9090,
            'grafana': 3000,
            'redis': 6379,
        }

        if name in port_map:
            return port_map[name]

        # Default by category
        if category == 'infrastructure':
            return 8500
        elif category == 'core':
            return 9000
        elif category == 'platform':
            return 8010

        return 8000

    def _find_endpoints(self, service_path: Path) -> List[Dict[str, str]]:
        """Находит все API endpoints в сервисе"""
        endpoints = []

        for py_file in service_path.glob('**/*.py'):
            try:
                content = py_file.read_text()

                # FastAPI patterns
                patterns = [
                    r'@app\.(get|post|put|delete|patch)\([\'"]([^\'"]+)',
                    r'@router\.(get|post|put|delete|patch)\([\'"]([^\'"]+)',
                ]

                for pattern in patterns:
                    for match in re.finditer(pattern, content):
                        endpoints.append({
                            'method': match.group(1).upper(),
                            'path': match.group(2)
                        })

            except Exception:
                continue

        return endpoints

    def _extract_env_vars(self, service_path: Path) -> set:
        """Извлекает все environment variables из кода"""
        env_vars = set()

        for py_file in service_path.glob('**/*.py'):
            try:
                content = py_file.read_text()

                # Find os.getenv() and os.environ[] calls
                patterns = [
                    r'os\.getenv\([\'"]([^\'"]+)',
                    r'os\.environ\[[\'"]([^\'"]+)',
                    r'getenv\([\'"]([^\'"]+)',
                ]

                for pattern in patterns:
                    for match in re.finditer(pattern, content):
                        env_vars.add(match.group(1))

            except Exception:
                continue

        return env_vars

    def _analyze_dependencies(self, service_path: Path) -> List[str]:
        """Анализирует зависимости сервиса"""
        deps = []

        # Check imports
        for py_file in service_path.glob('**/*.py'):
            try:
                content = py_file.read_text()

                # Find imports from other services
                if 'from infrastructure' in content:
                    deps.append('infrastructure-services')
                if 'from intelligent_core' in content or 'from ai_foundation' in content:
                    deps.append('ai-foundation')
                if 'from workflow_intelligence' in content:
                    deps.append('workflow-intelligence')
                if 'from shared' in content:
                    deps.append('shared-libraries')

            except Exception:
                continue

        return list(set(deps))

    def _detect_service_type(self, service_path: Path, main_file: Optional[Path]) -> str:
        """Определяет тип сервиса"""
        name = service_path.name.lower()

        if 'gateway' in name:
            return 'gateway'
        elif 'database' in name or 'db' in name:
            return 'database'
        elif 'ai' in name or 'intelligence' in name or 'workflow' in name:
            return 'ai-service'
        elif 'prometheus' in name or 'grafana' in name or 'monitoring' in name:
            return 'observability'
        elif 'eventbus' in name or 'queue' in name or 'websocket' in name:
            return 'runtime'
        else:
            return 'application'

    def _find_health_endpoint(self, endpoints: List[Dict[str, str]]) -> str:
        """Находит health check endpoint"""
        for ep in endpoints:
            if 'health' in ep['path'].lower():
                return ep['path']

        return '/health'  # default

    def save_catalog(self, output_file: Path):
        """Сохраняет service catalog в JSON"""
        catalog = {
            'version': '1.0.0',
            'generated_at': '2025-10-07',
            'total_services': len(self.services),
            'services': self.services
        }

        with open(output_file, 'w') as f:
            json.dump(catalog, f, indent=2)

        print(f"\n💾 Service catalog saved: {output_file}")

    def generate_docker_compose(self, output_file: Path):
        """Генерирует docker-compose.yml"""
        compose = {
            'version': '3.8',
            'services': {},
            'networks': {
                'bcm-network': {
                    'driver': 'bridge'
                }
            }
        }

        for service in self.services:
            if service['type'] in ['ai-service', 'application', 'gateway']:
                compose['services'][service['name']] = {
                    'build': service['path'],
                    'container_name': f"bcm-{service['name']}",
                    'ports': [f"{service['port']}:{service['port']}"],
                    'environment': [f"{var}=${{{var}}}" for var in service['environment']],
                    'networks': ['bcm-network'],
                    'restart': 'unless-stopped',
                    'healthcheck': {
                        'test': f"curl -f http://localhost:{service['port']}{service['health_check']} || exit 1",
                        'interval': '30s',
                        'timeout': '10s',
                        'retries': 3,
                        'start_period': '40s'
                    }
                }

                if service['dependencies']:
                    compose['services'][service['name']]['depends_on'] = service['dependencies']

        with open(output_file, 'w') as f:
            yaml.dump(compose, f, default_flow_style=False, sort_keys=False)

        print(f"💾 Docker Compose saved: {output_file}")

    def generate_prometheus_config(self, output_file: Path):
        """Генерирует prometheus.yml"""
        config = {
            'global': {
                'scrape_interval': '15s',
                'evaluation_interval': '15s'
            },
            'scrape_configs': []
        }

        for service in self.services:
            config['scrape_configs'].append({
                'job_name': service['name'],
                'static_configs': [{
                    'targets': [f"localhost:{service['port']}"],
                    'labels': {
                        'category': service['category'],
                        'type': service['type']
                    }
                }],
                'metrics_path': service['metrics_endpoint'],
                'scrape_interval': '30s'
            })

        with open(output_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)

        print(f"💾 Prometheus config saved: {output_file}")

    def generate_gateway_routes(self, output_file: Path):
        """Генерирует маршруты для API Gateway"""
        routes = {}

        for service in self.services:
            if service['type'] in ['ai-service', 'application']:
                for endpoint in service['endpoints']:
                    # Map endpoint to service
                    path_prefix = f"/{service['name']}"
                    routes[path_prefix] = f"http://localhost:{service['port']}"

        with open(output_file, 'w') as f:
            json.dump(routes, f, indent=2)

        print(f"💾 Gateway routes saved: {output_file}")


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent.parent

    print("=" * 60)
    print("🔍 Automatic Service Discovery")
    print("=" * 60)

    # Create discovery instance
    discovery = ServiceDiscovery(project_root)

    # Discover all services
    services = discovery.discover_all()

    # Create output directory
    output_dir = project_root / 'infrastructure' / 'auto-generated'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate all configs
    print("\n🏗️ Generating infrastructure configs...")

    discovery.save_catalog(output_dir / 'service-catalog.json')
    discovery.generate_docker_compose(output_dir / 'docker-compose.auto.yml')
    discovery.generate_prometheus_config(output_dir / 'prometheus.auto.yml')
    discovery.generate_gateway_routes(output_dir / 'gateway-routes.auto.json')

    print("\n" + "=" * 60)
    print("✅ Service discovery complete!")
    print("=" * 60)
    print(f"\nGenerated files in: {output_dir}")
    print("  - service-catalog.json")
    print("  - docker-compose.auto.yml")
    print("  - prometheus.auto.yml")
    print("  - gateway-routes.auto.json")
    print("\nNext steps:")
    print("  1. Review generated configs")
    print("  2. Test: docker-compose -f infrastructure/auto-generated/docker-compose.auto.yml config")
    print("  3. Deploy: docker-compose -f infrastructure/auto-generated/docker-compose.auto.yml up -d")


if __name__ == '__main__':
    main()
