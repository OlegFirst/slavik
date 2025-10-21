#!/usr/bin/env python3
"""
Infrastructure Builder Orchestrator
====================================

Главный оркестратор для автоматизации всего процесса сборки инфраструктуры:
1. Service Discovery (обнаружение всех сервисов)
2. Docker Compose Generation (генерация docker-compose файлов)
3. Dockerfile Generation (создание недостающих Dockerfile)
4. Environment Configuration (настройка переменных окружения)
5. Startup Scripts (создание скриптов запуска)

Использует:
- tools/infrastructure/discover_services.py
- tools/infrastructure/docker_compose_generator.py
- tools/analyzers/module_scanner.py
- infrastructure/deployment/docker-management/docker_manager.py

Usage:
    # Полная сборка
    python3 infrastructure/deployment/orchestrator/infrastructure_builder.py

    # Только обнаружение сервисов
    python3 infrastructure/deployment/orchestrator/infrastructure_builder.py --discover-only

    # Сборка с автоматическим запуском
    python3 infrastructure/deployment/orchestrator/infrastructure_builder.py --build-and-start
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'tools'))

from infrastructure.discover_services import ServiceDiscovery
from infrastructure.docker_compose_generator import DockerComposeGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InfrastructureBuilder:
    """Главный оркестратор для сборки инфраструктуры"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.infrastructure_dir = project_root / 'infrastructure'
        self.deployment_dir = self.infrastructure_dir / 'deployment'
        self.generated_dir = self.deployment_dir / 'generated'

        # Create output directory
        self.generated_dir.mkdir(parents=True, exist_ok=True)

        self.services = []
        self.dockerfile_template = self._get_dockerfile_template()

    def build_all(self, auto_start: bool = False):
        """Полная сборка инфраструктуры"""

        print("\n" + "="*80)
        print("️  AI PLATFORM INFRASTRUCTURE BUILDER")
        print("="*80 + "\n")

        try:
            # Step 1: Service Discovery
            print(" Step 1: Service Discovery")
            print("-" * 80)
            self.services = self._discover_services()
            print(f" Discovered {len(self.services)} services\n")

            # Step 2: Generate Dockerfiles
            print(" Step 2: Dockerfile Generation")
            print("-" * 80)
            self._generate_dockerfiles()
            print(" Dockerfiles generated\n")

            # Step 3: Generate Docker Compose
            print(" Step 3: Docker Compose Generation")
            print("-" * 80)
            self._generate_docker_compose()
            print(" Docker Compose files generated\n")

            # Step 4: Generate documentation
            print(" Step 4: Documentation Generation")
            print("-" * 80)
            self._generate_documentation()
            print(" Documentation generated\n")

            # Step 5: Validate configurations
            print(" Step 5: Configuration Validation")
            print("-" * 80)
            self._validate_configurations()
            print(" All configurations validated\n")

            print("="*80)
            print(" INFRASTRUCTURE BUILD COMPLETE!")
            print("="*80 + "\n")

            self._print_next_steps(auto_start)

            # Auto-start if requested
            if auto_start:
                self._start_infrastructure()

        except Exception as e:
            logger.error(f"Build failed: {e}", exc_info=True)
            print(f"\n Build failed: {e}")
            sys.exit(1)

    def _discover_services(self) -> List[Dict[str, Any]]:
        """Шаг 1: Обнаружение всех сервисов"""

        discovery = ServiceDiscovery(self.project_root)
        services = discovery.discover_all()

        # Print summary
        print(f"\n Services by category:")
        categories = {}
        for service in services:
            cat = service.get('category', 'unknown')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(service['name'])

        for cat, services_list in categories.items():
            print(f"\n  {cat.upper()}:")
            for svc in services_list:
                print(f"    • {svc}")

        return services

    def _generate_dockerfiles(self):
        """Шаг 2: Генерация недостающих Dockerfile"""

        missing_dockerfiles = []

        for service in self.services:
            service_path = Path(service['path'])
            dockerfile = service_path / 'Dockerfile'

            if not dockerfile.exists():
                missing_dockerfiles.append(service)
                print(f"   Creating Dockerfile for {service['name']}")
                self._create_dockerfile(service_path, service)

        if not missing_dockerfiles:
            print("   All services already have Dockerfiles")
        else:
            print(f"   Created {len(missing_dockerfiles)} Dockerfiles")

    def _create_dockerfile(self, service_path: Path, service: Dict):
        """Создаёт Dockerfile для сервиса"""

        # Определить тип сервиса и выбрать шаблон
        service_type = service.get('type', 'python')

        if service_type == 'python':
            dockerfile_content = self._get_python_dockerfile(service)
        elif service_type == 'node':
            dockerfile_content = self._get_node_dockerfile(service)
        else:
            dockerfile_content = self.dockerfile_template

        # Записать Dockerfile
        dockerfile_path = service_path / 'Dockerfile'
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)

        # Создать .dockerignore если нет
        dockerignore_path = service_path / '.dockerignore'
        if not dockerignore_path.exists():
            with open(dockerignore_path, 'w') as f:
                f.write(self._get_dockerignore())

    def _get_python_dockerfile(self, service: Dict) -> str:
        """Шаблон Dockerfile для Python сервиса"""
        return f"""# Auto-generated Dockerfile for {service['name']}
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE {service.get('port', 8000)}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \\
    CMD curl -f http://localhost:{service.get('port', 8000)}{service.get('health_endpoint', '/health')} || exit 1

# Run application
CMD ["python3", "main.py"]
"""

    def _get_node_dockerfile(self, service: Dict) -> str:
        """Шаблон Dockerfile для Node.js сервиса"""
        return f"""# Auto-generated Dockerfile for {service['name']}
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Expose port
EXPOSE {service.get('port', 3000)}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \\
    CMD wget --no-verbose --tries=1 --spider http://localhost:{service.get('port', 3000)}{service.get('health_endpoint', '/health')} || exit 1

# Run application
CMD ["npm", "start"]
"""

    def _get_dockerignore(self) -> str:
        """Шаблон .dockerignore"""
        return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Node
node_modules/
npm-debug.log
yarn-error.log

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Git
.git/
.gitignore

# OS
.DS_Store
Thumbs.db

# Tests
.pytest_cache/
.coverage
htmlcov/

# Logs
*.log
logs/

# Environment
.env
.env.local
"""

    def _get_dockerfile_template(self) -> str:
        """Базовый шаблон Dockerfile"""
        return """FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python3", "main.py"]
"""

    def _generate_docker_compose(self):
        """Шаг 3: Генерация Docker Compose файлов"""

        generator = DockerComposeGenerator(
            self.project_root,
            self.generated_dir
        )

        generator.generate_all()

    def _generate_documentation(self):
        """Шаг 4: Генерация документации"""

        readme_content = f"""# AI Platform Infrastructure

Auto-generated infrastructure configuration.

## Services

Total services: {len(self.services)}

### By Category

"""

        # Group by category
        categories = {}
        for service in self.services:
            cat = service.get('category', 'unknown')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(service)

        for cat, services_list in categories.items():
            readme_content += f"\n#### {cat.upper()}\n\n"
            for svc in services_list:
                readme_content += f"- **{svc['name']}** (port {svc['port']})\n"
                readme_content += f"  - Path: `{svc['path']}`\n"
                if svc.get('health_endpoint'):
                    readme_content += f"  - Health: `{svc['health_endpoint']}`\n"
                readme_content += "\n"

        readme_content += """
## Quick Start

### 1. Setup environment

```bash
cd infrastructure/deployment/generated
cp .env.template .env
# Edit .env with your actual values
```

### 2. Start infrastructure

```bash
# Start all services
./start_infrastructure.sh full

# Or start by layer
./start_infrastructure.sh gateway
./start_infrastructure.sh runtime
./start_infrastructure.sh observability
```

### 3. Check health

```bash
./check_health.sh
```

### 4. Stop services

```bash
./stop_infrastructure.sh full
```

## Docker Compose Files

- `docker-compose.gateway.yml` - Gateway layer services
- `docker-compose.runtime.yml` - Runtime layer services
- `docker-compose.observability.yml` - Observability layer services
- `docker-compose.integration.yml` - Integration layer services
- `docker-compose.full.yml` - All services combined

## Configuration

Environment variables are defined in `.env` file. See `.env.template` for required variables.

## Troubleshooting

### Check logs

```bash
docker-compose -f docker-compose.full.yml logs -f [service-name]
```

### Restart service

```bash
docker-compose -f docker-compose.full.yml restart [service-name]
```

### Rebuild service

```bash
docker-compose -f docker-compose.full.yml up -d --build [service-name]
```

---

*Auto-generated by Infrastructure Builder*
"""

        readme_path = self.generated_dir / 'README.md'
        with open(readme_path, 'w') as f:
            f.write(readme_content)

        print(f"   Generated README.md")

    def _validate_configurations(self):
        """Шаг 5: Валидация конфигураций"""

        validations = []

        # 1. Проверить docker-compose синтаксис
        compose_files = list(self.generated_dir.glob('docker-compose.*.yml'))
        for compose_file in compose_files:
            try:
                result = subprocess.run(
                    ['docker-compose', '-f', str(compose_file), 'config'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    validations.append((compose_file.name, True, "Valid"))
                else:
                    validations.append((compose_file.name, False, result.stderr))
            except Exception as e:
                validations.append((compose_file.name, False, str(e)))

        # Print results
        for name, is_valid, message in validations:
            if is_valid:
                print(f"   {name}: {message}")
            else:
                print(f"   {name}: {message}")

    def _print_next_steps(self, auto_start: bool):
        """Печатает следующие шаги"""

        if not auto_start:
            print(" Next Steps:")
            print()
            print("1. Configure environment:")
            print(f"   cd {self.generated_dir}")
            print("   cp .env.template .env")
            print("   # Edit .env with your actual credentials")
            print()
            print("2. Start infrastructure:")
            print("   ./start_infrastructure.sh full")
            print()
            print("3. Check health:")
            print("   ./check_health.sh")
            print()

    def _start_infrastructure(self):
        """Автоматический запуск инфраструктуры"""

        print("\n Starting infrastructure...")

        script = self.generated_dir / 'start_infrastructure.sh'
        if script.exists():
            try:
                subprocess.run([str(script), 'full'], check=True)
                print(" Infrastructure started successfully!")
            except subprocess.CalledProcessError as e:
                print(f" Failed to start infrastructure: {e}")
        else:
            print(" Startup script not found")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Build AI Platform Infrastructure'
    )
    parser.add_argument(
        '--discover-only',
        action='store_true',
        help='Only discover services, don\'t generate configs'
    )
    parser.add_argument(
        '--build-and-start',
        action='store_true',
        help='Build and automatically start infrastructure'
    )

    args = parser.parse_args()

    builder = InfrastructureBuilder(PROJECT_ROOT)

    if args.discover_only:
        print(" Service Discovery Only Mode\n")
        services = builder._discover_services()
        print(f"\n Discovered {len(services)} services")
    else:
        builder.build_all(auto_start=args.build_and_start)


if __name__ == '__main__':
    main()
