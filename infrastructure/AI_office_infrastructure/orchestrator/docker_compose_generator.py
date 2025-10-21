#!/usr/bin/env python3
"""
Docker Compose Generator for Infrastructure Services
=====================================================

Автоматически генерирует docker-compose файлы для всех инфраструктурных сервисов
на основе анализа кода и обнаруженных сервисов.

Использует:
- discover_services.py - обнаружение сервисов
- module_scanner.py - анализ кода
- dependency_validator.py - граф зависимостей

Генерирует:
- docker-compose.gateway.yml
- docker-compose.runtime.yml
- docker-compose.observability.yml
- docker-compose.integration.yml
- docker-compose.full.yml

Usage:
    python3 tools/infrastructure/docker_compose_generator.py
    python3 tools/infrastructure/docker_compose_generator.py --layer gateway
    python3 tools/infrastructure/docker_compose_generator.py --output infrastructure/deployment
"""

import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.discover_services import ServiceDiscovery


class DockerComposeGenerator:
    """Генератор docker-compose конфигураций по слоям"""

    # Определение слоёв и их портов по умолчанию
    LAYERS = {
        'gateway': {
            'services': ['api-gateway', 'unified-database-gateway', 'intelligent-gateway'],
            'network': 'gateway-network',
            'port_range': '8000-8099'
        },
        'runtime': {
            'services': ['realtime-websocket', 'eventbus', 'message-queue', 'service-discovery'],
            'network': 'runtime-network',
            'port_range': '8100-8199'
        },
        'observability': {
            'services': ['monitoring', 'mio-manager', 'notification-service', 'prometheus', 'grafana'],
            'network': 'observability-network',
            'port_range': '9000-9199'
        },
        'integration': {
            'services': ['github-integration', 'process-mining-service', 'deployment-service'],
            'network': 'integration-network',
            'port_range': '8200-8299'
        }
    }

    def __init__(self, project_root: Path, output_dir: Path):
        self.project_root = project_root
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Обнаружить все сервисы
        self.discovery = ServiceDiscovery(project_root)
        self.all_services = self.discovery.discover_all()

        # Классифицировать по слоям
        self.services_by_layer = self._classify_services()

    def _classify_services(self) -> Dict[str, List[Dict]]:
        """Классифицирует сервисы по слоям"""
        classified = {layer: [] for layer in self.LAYERS.keys()}

        for service in self.all_services:
            service_name = service['name']

            # Определить слой на основе имени и пути
            for layer, config in self.LAYERS.items():
                # Проверяем по имени сервиса
                if any(layer_service in service_name for layer_service in config['services']):
                    classified[layer].append(service)
                    break
                # Проверяем по пути
                if layer in service.get('path', ''):
                    classified[layer].append(service)
                    break

        return classified

    def generate_all(self):
        """Генерирует все docker-compose файлы"""
        print("\n️  Docker Compose Generator")
        print("=" * 60)

        # 1. Генерировать compose файлы по слоям
        compose_files = []
        for layer in self.LAYERS.keys():
            if self.services_by_layer[layer]:
                filepath = self.generate_layer(layer)
                compose_files.append(filepath)
                print(f" {layer}: {filepath.name}")

        # 2. Генерировать full compose (объединяет все слои)
        full_file = self.generate_full(compose_files)
        print(f" full: {full_file.name}")

        # 3. Генерировать .env.template
        env_file = self.generate_env_template()
        print(f" environment: {env_file.name}")

        # 4. Генерировать startup скрипты
        startup_scripts = self.generate_startup_scripts()
        for script in startup_scripts:
            print(f" script: {script.name}")

        print("\n" + "=" * 60)
        print(" All configurations generated successfully!")
        print(f" Output directory: {self.output_dir}")

    def generate_layer(self, layer_name: str) -> Path:
        """Генерирует docker-compose файл для конкретного слоя"""
        services = self.services_by_layer[layer_name]
        layer_config = self.LAYERS[layer_name]

        compose = {
            'version': '3.8',
            'services': {},
            'networks': {
                layer_config['network']: {
                    'driver': 'bridge'
                }
            },
            'volumes': {}
        }

        for service in services:
            compose['services'][service['name']] = self._build_service_config(
                service, layer_config
            )

            # Добавить volumes если нужны
            if service.get('requires_volume'):
                volume_name = f"{service['name']}-data"
                compose['volumes'][volume_name] = {}

        # Сохранить файл
        output_file = self.output_dir / f"docker-compose.{layer_name}.yml"
        with open(output_file, 'w') as f:
            yaml.dump(compose, f, default_flow_style=False, sort_keys=False)

        return output_file

    def _build_service_config(self, service: Dict, layer_config: Dict) -> Dict:
        """Собирает конфигурацию для одного сервиса"""
        service_path = Path(service['path'])

        config = {
            'container_name': service['name'],
            'build': {
                'context': str(service_path),
                'dockerfile': 'Dockerfile'
            },
            'ports': [f"{service['port']}:{service['port']}"],
            'environment': self._build_environment(service),
            'networks': [layer_config['network']],
            'restart': 'unless-stopped',
            'healthcheck': {
                'test': f"curl -f http://localhost:{service['port']}{service.get('health_endpoint', '/health')} || exit 1",
                'interval': '30s',
                'timeout': '10s',
                'retries': 3,
                'start_period': '40s'
            },
            'logging': {
                'driver': 'json-file',
                'options': {
                    'max-size': '10m',
                    'max-file': '3'
                }
            }
        }

        # Добавить зависимости если есть
        if service.get('dependencies'):
            config['depends_on'] = self._build_depends_on(service['dependencies'])

        # Добавить volumes если нужны
        if service.get('requires_volume'):
            volume_name = f"{service['name']}-data"
            config['volumes'] = [f"{volume_name}:/data"]

        return config

    def _build_environment(self, service: Dict) -> List[str]:
        """Собирает environment переменные для сервиса"""
        env = []

        # Базовые переменные
        env.append(f"SERVICE_NAME={service['name']}")
        env.append(f"SERVICE_PORT={service['port']}")

        # Добавить переменные из анализа кода
        for var_name in service.get('environment', []):
            env.append(f"{var_name}=${{{{var_name}}}}")

        return env

    def _build_depends_on(self, dependencies: List[str]) -> Dict:
        """Собирает depends_on с health checks"""
        depends = {}
        for dep in dependencies:
            depends[dep] = {
                'condition': 'service_healthy'
            }
        return depends

    def generate_full(self, layer_files: List[Path]) -> Path:
        """Генерирует полный docker-compose который включает все слои"""

        compose = {
            'version': '3.8',
            'services': {},
            'networks': {
                'platform-network': {
                    'driver': 'bridge',
                    'name': 'ai-platform-network'
                }
            },
            'volumes': {}
        }

        # Объединить все сервисы из всех слоёв
        for layer_name, services in self.services_by_layer.items():
            for service in services:
                service_config = self._build_service_config(
                    service,
                    {'network': 'platform-network'}
                )
                compose['services'][service['name']] = service_config

                # Volumes
                if service.get('requires_volume'):
                    volume_name = f"{service['name']}-data"
                    compose['volumes'][volume_name] = {}

        # Добавить внешние зависимости (PostgreSQL, Redis, Qdrant)
        compose['services'].update(self._add_external_dependencies())

        # Сохранить
        output_file = self.output_dir / "docker-compose.full.yml"
        with open(output_file, 'w') as f:
            # Добавить комментарий в начало
            f.write(f"# Auto-generated Docker Compose configuration\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Total services: {len(compose['services'])}\n\n")
            yaml.dump(compose, f, default_flow_style=False, sort_keys=False)

        return output_file

    def _add_external_dependencies(self) -> Dict:
        """Добавляет external dependencies (для локальной разработки)"""
        return {
            'postgres': {
                'image': 'postgres:15-alpine',
                'container_name': 'ai-platform-postgres',
                'environment': [
                    'POSTGRES_DB=${POSTGRES_DB:-ai_platform}',
                    'POSTGRES_USER=${POSTGRES_USER:-postgres}',
                    'POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-postgres}'
                ],
                'ports': ['5432:5432'],
                'volumes': ['postgres-data:/var/lib/postgresql/data'],
                'networks': ['platform-network'],
                'healthcheck': {
                    'test': 'pg_isready -U postgres',
                    'interval': '10s',
                    'timeout': '5s',
                    'retries': 5
                }
            },
            'redis': {
                'image': 'redis:7-alpine',
                'container_name': 'ai-platform-redis',
                'ports': ['6379:6379'],
                'networks': ['platform-network'],
                'healthcheck': {
                    'test': 'redis-cli ping',
                    'interval': '10s',
                    'timeout': '5s',
                    'retries': 5
                }
            }
        }

    def generate_env_template(self) -> Path:
        """Генерирует .env.template файл"""

        env_vars = set()

        # Собрать все environment переменные из всех сервисов
        for services in self.services_by_layer.values():
            for service in services:
                env_vars.update(service.get('environment', []))

        # Базовые переменные
        base_vars = [
            "# Database Configuration",
            "POSTGRES_DB=ai_platform",
            "POSTGRES_USER=postgres",
            "POSTGRES_PASSWORD=change_me_in_production",
            "DATABASE_URL=postgresql://postgres:change_me_in_production@postgres:5432/ai_platform",
            "",
            "# Redis Configuration",
            "REDIS_URL=redis://redis:6379/0",
            "",
            "# Supabase (Cloud)",
            "SUPABASE_URL=https://your-project.supabase.co",
            "SUPABASE_KEY=your-supabase-key",
            "",
            "# Qdrant (Cloud)",
            "QDRANT_URL=https://your-cluster.qdrant.io",
            "QDRANT_API_KEY=your-qdrant-key",
            "",
            "# Authentication",
            "JWT_SECRET=change_me_to_random_string",
            "JWT_ALGORITHM=HS256",
            "",
            "# LLM Configuration",
            "ANTHROPIC_API_KEY=your-anthropic-key",
            "",
            "# Service-specific variables",
        ]

        # Добавить переменные из сервисов
        for var in sorted(env_vars):
            if var not in ['SERVICE_NAME', 'SERVICE_PORT']:
                base_vars.append(f"{var}=")

        output_file = self.output_dir / ".env.template"
        with open(output_file, 'w') as f:
            f.write('\n'.join(base_vars))

        return output_file

    def generate_startup_scripts(self) -> List[Path]:
        """Генерирует скрипты для запуска"""
        scripts = []

        # 1. Скрипт запуска по слоям
        script_content = """#!/bin/bash
# Auto-generated startup script for AI Platform Infrastructure
# Usage: ./start_infrastructure.sh [layer]
#   layer: gateway|runtime|observability|integration|full

set -e

LAYER=${1:-full}
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo " Starting AI Platform Infrastructure - Layer: $LAYER"
echo ""

# Check if .env exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "️  .env file not found. Copying from template..."
    cp "$SCRIPT_DIR/.env.template" "$SCRIPT_DIR/.env"
    echo "️  Please edit .env and set your actual values!"
    exit 1
fi

# Start the appropriate layer
case $LAYER in
    gateway)
        echo " Starting Gateway layer..."
        docker-compose -f docker-compose.gateway.yml up -d
        ;;
    runtime)
        echo " Starting Runtime layer..."
        docker-compose -f docker-compose.runtime.yml up -d
        ;;
    observability)
        echo "️  Starting Observability layer..."
        docker-compose -f docker-compose.observability.yml up -d
        ;;
    integration)
        echo " Starting Integration layer..."
        docker-compose -f docker-compose.integration.yml up -d
        ;;
    full)
        echo " Starting all services..."
        docker-compose -f docker-compose.full.yml up -d
        ;;
    *)
        echo " Unknown layer: $LAYER"
        echo "Valid layers: gateway, runtime, observability, integration, full"
        exit 1
        ;;
esac

echo ""
echo " Services started successfully!"
echo ""
echo " Check status: docker-compose -f docker-compose.$LAYER.yml ps"
echo " View logs: docker-compose -f docker-compose.$LAYER.yml logs -f"
echo " Stop services: ./stop_infrastructure.sh $LAYER"
"""

        start_script = self.output_dir / "start_infrastructure.sh"
        with open(start_script, 'w') as f:
            f.write(script_content)
        start_script.chmod(0o755)
        scripts.append(start_script)

        # 2. Скрипт остановки
        stop_content = """#!/bin/bash
# Auto-generated stop script for AI Platform Infrastructure

set -e

LAYER=${1:-full}
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo " Stopping AI Platform Infrastructure - Layer: $LAYER"

case $LAYER in
    gateway|runtime|observability|integration|full)
        docker-compose -f "docker-compose.$LAYER.yml" down
        ;;
    all)
        echo " Stopping all layers..."
        for layer in gateway runtime observability integration full; do
            if [ -f "docker-compose.$layer.yml" ]; then
                docker-compose -f "docker-compose.$layer.yml" down 2>/dev/null || true
            fi
        done
        ;;
    *)
        echo " Unknown layer: $LAYER"
        exit 1
        ;;
esac

echo " Services stopped successfully!"
"""

        stop_script = self.output_dir / "stop_infrastructure.sh"
        with open(stop_script, 'w') as f:
            f.write(stop_content)
        stop_script.chmod(0o755)
        scripts.append(stop_script)

        # 3. Скрипт проверки здоровья
        health_content = """#!/bin/bash
# Health check script for all services

echo " Checking service health..."
echo ""

docker-compose -f docker-compose.full.yml ps

echo ""
echo "Detailed health checks:"
echo ""

for container in $(docker-compose -f docker-compose.full.yml ps -q); do
    name=$(docker inspect --format='{{.Name}}' $container | sed 's/^\\///')
    health=$(docker inspect --format='{{.State.Health.Status}}' $container 2>/dev/null || echo "no healthcheck")
    status=$(docker inspect --format='{{.State.Status}}' $container)

    if [ "$status" = "running" ]; then
        if [ "$health" = "healthy" ]; then
            echo " $name - $status ($health)"
        elif [ "$health" = "no healthcheck" ]; then
            echo " $name - $status (no healthcheck)"
        else
            echo "️  $name - $status ($health)"
        fi
    else
        echo " $name - $status"
    fi
done
"""

        health_script = self.output_dir / "check_health.sh"
        with open(health_script, 'w') as f:
            f.write(health_content)
        health_script.chmod(0o755)
        scripts.append(health_script)

        return scripts


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate Docker Compose configurations')
    parser.add_argument('--layer', help='Generate only specific layer')
    parser.add_argument('--output', default='infrastructure/deployment/generated',
                       help='Output directory for generated files')

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / args.output

    generator = DockerComposeGenerator(project_root, output_dir)

    if args.layer:
        if args.layer in generator.LAYERS:
            filepath = generator.generate_layer(args.layer)
            print(f" Generated: {filepath}")
        else:
            print(f" Unknown layer: {args.layer}")
            print(f"Available layers: {', '.join(generator.LAYERS.keys())}")
    else:
        generator.generate_all()


if __name__ == '__main__':
    main()
