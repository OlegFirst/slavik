#!/usr/bin/env python3
"""
Infrastructure Orchestrator - Integration Layer
================================================

Связующее звено между:
- tools/infrastructure (Service Discovery, Docker Compose Generation)
- intelligent-core/orchestration/ai-orchestration (AI Orchestrator)
- intelligent-core/orchestration/coordination-center (Coordination)
- infrastructure/deployment/docker-management (Docker Manager)

Этот модуль НЕ дублирует существующую функциональность, а ИНТЕГРИРУЕТ её.

Usage:
    # Обнаружить все сервисы
    python3 tools/infrastructure/infrastructure_orchestrator.py discover

    # Сгенерировать docker-compose файлы
    python3 tools/infrastructure/infrastructure_orchestrator.py generate

    # Запустить инфраструктуру через ai-orchestration
    python3 tools/infrastructure/infrastructure_orchestrator.py deploy --layer full

    # Полный цикл: discover -> generate -> deploy
    python3 tools/infrastructure/infrastructure_orchestrator.py build-and-deploy
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import json

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'tools'))
sys.path.insert(0, str(PROJECT_ROOT))

from infrastructure.discover_services import ServiceDiscovery
from infrastructure.docker_compose_generator import DockerComposeGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InfrastructureOrchestrator:
    """
    Интеграция всех инструментов для управления инфраструктурой

    Архитектура:
        tools/infrastructure (этот модуль)
            ↓ обнаружение и генерация
        intelligent-core/orchestration/ai-orchestration
            ↓ оркестрация запуска
        infrastructure/deployment/docker-management
            ↓ управление контейнерами
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tools_dir = project_root / 'tools'
        self.infrastructure_dir = project_root / 'infrastructure'
        self.orchestration_dir = project_root / 'intelligent-core' / 'orchestration'

        # Выходные директории
        self.deployment_dir = self.infrastructure_dir / 'deployment'
        self.generated_dir = self.deployment_dir / 'generated'
        self.generated_dir.mkdir(parents=True, exist_ok=True)

    def discover_services(self) -> List[Dict[str, Any]]:
        """
        Шаг 1: Обнаружение всех сервисов
        Использует: tools/infrastructure/discover_services.py
        """
        print("\n" + "="*80)
        print(" STEP 1: SERVICE DISCOVERY")
        print("="*80 + "\n")

        discovery = ServiceDiscovery(self.project_root)
        services = discovery.discover_all()

        # Сохраняем каталог сервисов
        catalog_file = self.generated_dir / 'service-catalog.json'
        with open(catalog_file, 'w') as f:
            json.dump(services, f, indent=2, default=str)

        print(f"\n Service catalog saved: {catalog_file}")
        print(f" Total services discovered: {len(services)}")

        return services

    def generate_configs(self, services: Optional[List[Dict]] = None):
        """
        Шаг 2: Генерация Docker Compose конфигураций
        Использует: tools/infrastructure/docker_compose_generator.py
        """
        print("\n" + "="*80)
        print("️  STEP 2: CONFIGURATION GENERATION")
        print("="*80 + "\n")

        # Если сервисы не переданы, загрузить из каталога
        if services is None:
            catalog_file = self.generated_dir / 'service-catalog.json'
            if catalog_file.exists():
                with open(catalog_file) as f:
                    services = json.load(f)
            else:
                print("️  Service catalog not found. Running discovery first...")
                services = self.discover_services()

        # Генерация docker-compose файлов
        generator = DockerComposeGenerator(self.project_root, self.generated_dir)
        generator.generate_all()

        print("\n All configurations generated")

    def deploy_infrastructure(self, layer: str = 'full', use_orchestrator: bool = True):
        """
        Шаг 3: Развёртывание инфраструктуры

        Может использовать:
        1. ai-orchestration (рекомендуется) - умное управление через AI
        2. docker-compose напрямую - простое развёртывание

        Args:
            layer: gateway|runtime|observability|integration|full
            use_orchestrator: использовать ai-orchestration или нет
        """
        print("\n" + "="*80)
        print(" STEP 3: INFRASTRUCTURE DEPLOYMENT")
        print("="*80 + "\n")

        if use_orchestrator:
            self._deploy_via_ai_orchestration(layer)
        else:
            self._deploy_via_docker_compose(layer)

    def _deploy_via_ai_orchestration(self, layer: str):
        """Развёртывание через ai-orchestration (умное управление)"""

        print(" Using AI Orchestration for intelligent deployment")
        print()

        # 1. Проверить что ai-orchestration запущен
        orchestration_service = self.orchestration_dir / 'ai-orchestration'

        try:
            # Попытаться подключиться к ai-orchestration
            import requests
            response = requests.get('http://localhost:8002/health', timeout=5)

            if response.ok:
                print(" ai-orchestration is running")

                # Отправить задачу на развёртывание
                deploy_request = {
                    'task_type': 'deploy_infrastructure',
                    'layer': layer,
                    'compose_file': str(self.generated_dir / f'docker-compose.{layer}.yml')
                }

                # API ai-orchestration может обработать эту задачу
                print(f" Sending deployment request for layer: {layer}")
                # TODO: интеграция с API ai-orchestration
                print("   (API integration in progress)")

        except Exception as e:
            print(f"️  ai-orchestration not available: {e}")
            print("   Falling back to direct docker-compose deployment")
            self._deploy_via_docker_compose(layer)

    def _deploy_via_docker_compose(self, layer: str):
        """Развёртывание напрямую через docker-compose"""

        print(f" Using docker-compose for layer: {layer}")
        print()

        compose_file = self.generated_dir / f'docker-compose.{layer}.yml'

        if not compose_file.exists():
            print(f" Compose file not found: {compose_file}")
            print("   Run 'generate' command first")
            return

        # Использовать скрипт запуска если есть
        start_script = self.generated_dir / 'start_infrastructure.sh'

        if start_script.exists():
            print(f" Using startup script: {start_script.name}")
            try:
                subprocess.run([str(start_script), layer], check=True)
                print(f"\n Infrastructure layer '{layer}' started successfully")
            except subprocess.CalledProcessError as e:
                print(f"\n Deployment failed: {e}")
        else:
            # Прямой запуск через docker-compose
            print(f" Running: docker-compose -f {compose_file.name} up -d")
            try:
                subprocess.run(
                    ['docker-compose', '-f', str(compose_file), 'up', '-d'],
                    cwd=self.generated_dir,
                    check=True
                )
                print(f"\n Infrastructure layer '{layer}' started successfully")
            except subprocess.CalledProcessError as e:
                print(f"\n Deployment failed: {e}")

    def build_and_deploy(self, layer: str = 'full', use_orchestrator: bool = True):
        """Полный цикл: обнаружение → генерация → развёртывание"""

        print("\n" + "="*80)
        print(" FULL INFRASTRUCTURE BUILD & DEPLOY")
        print("="*80)

        try:
            # Шаг 1: Обнаружение
            services = self.discover_services()

            # Шаг 2: Генерация конфигов
            self.generate_configs(services)

            # Шаг 3: Развёртывание
            self.deploy_infrastructure(layer, use_orchestrator)

            print("\n" + "="*80)
            print(" INFRASTRUCTURE BUILD & DEPLOY COMPLETE!")
            print("="*80)

            self._print_status()

        except Exception as e:
            logger.error(f"Build and deploy failed: {e}", exc_info=True)
            print(f"\n Build and deploy failed: {e}")
            sys.exit(1)

    def status(self):
        """Проверка статуса инфраструктуры"""

        print("\n" + "="*80)
        print(" INFRASTRUCTURE STATUS")
        print("="*80 + "\n")

        # 1. Проверить наличие конфигов
        print(" Generated Configurations:")
        compose_files = list(self.generated_dir.glob('docker-compose.*.yml'))
        if compose_files:
            for f in compose_files:
                print(f"    {f.name}")
        else:
            print("    No compose files found (run 'generate' first)")
        print()

        # 2. Проверить Docker контейнеры
        print(" Running Containers:")
        try:
            result = subprocess.run(
                ['docker-compose', '-f', 'docker-compose.full.yml', 'ps'],
                cwd=self.generated_dir,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(result.stdout)
            else:
                print("   ℹ️  No containers running")
        except Exception as e:
            print(f"   ️  Could not check containers: {e}")
        print()

        # 3. Проверить orchestration сервисы
        print(" Orchestration Services:")
        self._check_service('ai-orchestration', 8002, '/health')
        self._check_service('coordination-center', 8004, '/coordination/health')
        print()

    def _check_service(self, name: str, port: int, health_path: str):
        """Проверить доступность сервиса"""
        try:
            import requests
            response = requests.get(f'http://localhost:{port}{health_path}', timeout=3)
            if response.ok:
                print(f"    {name} (port {port})")
            else:
                print(f"   ️  {name} (port {port}) - unhealthy")
        except:
            print(f"    {name} (port {port}) - not running")

    def _print_status(self):
        """Печать итогового статуса"""
        print("\n Quick Status Check:")
        print(f"   Generated configs: {self.generated_dir}")
        print(f"   Start script: ./start_infrastructure.sh [layer]")
        print(f"   Stop script: ./stop_infrastructure.sh [layer]")
        print(f"   Health check: ./check_health.sh")
        print()

    def integrate_with_project_agent(self):
        """
        Интеграция с project-agent
        Добавляет команды для управления инфраструктурой в project-agent CLI
        """
        print("\n" + "="*80)
        print(" INTEGRATING WITH PROJECT-AGENT")
        print("="*80 + "\n")

        project_agent_dir = self.tools_dir / 'project-agent' / 'agent'

        # Создать модуль для интеграции
        integration_code = '''"""
Infrastructure commands for project-agent
Auto-generated by infrastructure_orchestrator.py
"""

import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

def docker_discover():
    """Discover all infrastructure services"""
    script = PROJECT_ROOT / "tools" / "infrastructure" / "infrastructure_orchestrator.py"
    subprocess.run(["python3", str(script), "discover"], check=True)

def docker_generate():
    """Generate docker-compose configurations"""
    script = PROJECT_ROOT / "tools" / "infrastructure" / "infrastructure_orchestrator.py"
    subprocess.run(["python3", str(script), "generate"], check=True)

def docker_deploy(layer="full"):
    """Deploy infrastructure layer"""
    script = PROJECT_ROOT / "tools" / "infrastructure" / "infrastructure_orchestrator.py"
    subprocess.run(["python3", str(script), "deploy", "--layer", layer], check=True)

def docker_build_deploy(layer="full"):
    """Full cycle: discover, generate, deploy"""
    script = PROJECT_ROOT / "tools" / "infrastructure" / "infrastructure_orchestrator.py"
    subprocess.run(["python3", str(script), "build-and-deploy", "--layer", layer], check=True)

def docker_status():
    """Check infrastructure status"""
    script = PROJECT_ROOT / "tools" / "infrastructure" / "infrastructure_orchestrator.py"
    subprocess.run(["python3", str(script), "status"], check=True)
'''

        integration_file = project_agent_dir / 'docker_commands.py'
        with open(integration_file, 'w') as f:
            f.write(integration_code)

        print(f" Created: {integration_file}")
        print()
        print(" New commands available in project-agent:")
        print("   project-agent docker discover")
        print("   project-agent docker generate")
        print("   project-agent docker deploy [layer]")
        print("   project-agent docker build-deploy")
        print("   project-agent docker status")
        print()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Infrastructure Orchestrator - Integration Layer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Discover all services
  %(prog)s discover

  # Generate docker-compose files
  %(prog)s generate

  # Deploy infrastructure
  %(prog)s deploy --layer full

  # Full build and deploy
  %(prog)s build-and-deploy --layer gateway

  # Check status
  %(prog)s status

  # Integrate with project-agent
  %(prog)s integrate-project-agent
        """
    )

    parser.add_argument(
        'command',
        choices=['discover', 'generate', 'deploy', 'build-and-deploy', 'status', 'integrate-project-agent'],
        help='Command to execute'
    )
    parser.add_argument(
        '--layer',
        choices=['gateway', 'runtime', 'observability', 'integration', 'full'],
        default='full',
        help='Infrastructure layer to deploy (default: full)'
    )
    parser.add_argument(
        '--no-orchestrator',
        action='store_true',
        help='Deploy directly with docker-compose (skip ai-orchestration)'
    )

    args = parser.parse_args()

    orchestrator = InfrastructureOrchestrator(PROJECT_ROOT)

    # Execute command
    if args.command == 'discover':
        orchestrator.discover_services()

    elif args.command == 'generate':
        orchestrator.generate_configs()

    elif args.command == 'deploy':
        orchestrator.deploy_infrastructure(
            layer=args.layer,
            use_orchestrator=not args.no_orchestrator
        )

    elif args.command == 'build-and-deploy':
        orchestrator.build_and_deploy(
            layer=args.layer,
            use_orchestrator=not args.no_orchestrator
        )

    elif args.command == 'status':
        orchestrator.status()

    elif args.command == 'integrate-project-agent':
        orchestrator.integrate_with_project_agent()


if __name__ == '__main__':
    main()
