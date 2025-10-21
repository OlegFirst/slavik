#!/usr/bin/env python3
"""
Automatic Service Registration Tool
Автоматически регистрирует новые сервисы в каталоге
"""

import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import subprocess
import sys

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
CATALOGS_DIR = REPO_ROOT / "catalogs"
PLATFORM_SERVICES_CATALOG = CATALOGS_DIR / "platform-services"


class PortManager:
    """Управление портами и проверка доступности"""

    # Port ranges by service type
    PORT_RANGES = {
        'platform_services': (8000, 8099),
        'intelligent_core': (8100, 8199),
        'infrastructure': (8200, 8299),
        'integration': (8300, 8399),
        'monitoring': (9000, 9099),
        'databases': (5000, 5099),
    }

    def __init__(self):
        self.used_ports = self._scan_used_ports()

    def _scan_used_ports(self) -> List[int]:
        """Сканирует все используемые порты из каталогов"""
        used_ports = []

        # Scan all YAML files in catalogs
        for yaml_file in CATALOGS_DIR.rglob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)

                # Extract ports from different structures
                ports = self._extract_ports_from_yaml(data)
                used_ports.extend(ports)

            except Exception as e:
                print(f"️  Error reading {yaml_file}: {e}")

        return sorted(set(used_ports))

    def _extract_ports_from_yaml(self, data: Any, ports: Optional[List[int]] = None) -> List[int]:
        """Рекурсивно извлекает порты из YAML структуры"""
        if ports is None:
            ports = []

        if isinstance(data, dict):
            # Check for 'port' key
            if 'port' in data and isinstance(data['port'], int):
                ports.append(data['port'])

            # Check for 'runtime' section
            if 'runtime' in data and isinstance(data['runtime'], dict):
                if 'port' in data['runtime'] and isinstance(data['runtime']['port'], int):
                    ports.append(data['runtime']['port'])

            # Recurse into nested dicts
            for value in data.values():
                self._extract_ports_from_yaml(value, ports)

        elif isinstance(data, list):
            for item in data:
                self._extract_ports_from_yaml(item, ports)

        return ports

    def get_next_available_port(self, service_type: str = 'platform_services') -> int:
        """Возвращает следующий свободный порт для типа сервиса"""
        if service_type not in self.PORT_RANGES:
            service_type = 'platform_services'

        start, end = self.PORT_RANGES[service_type]

        for port in range(start, end + 1):
            if port not in self.used_ports:
                return port

        raise ValueError(f"No available ports in range {start}-{end} for {service_type}")

    def is_port_available(self, port: int) -> bool:
        """Проверяет доступность порта"""
        if port in self.used_ports:
            return False

        # Check if port is actually free on the system
        try:
            result = subprocess.run(
                ['lsof', '-i', f':{port}'],
                capture_output=True,
                text=True
            )
            return result.returncode != 0  # 0 means port is in use
        except:
            # If lsof not available, just check catalog
            return port not in self.used_ports

    def get_port_suggestions(self, service_type: str, count: int = 3) -> List[int]:
        """Предлагает несколько свободных портов"""
        suggestions = []
        start, end = self.PORT_RANGES.get(service_type, (8000, 8099))

        for port in range(start, end + 1):
            if self.is_port_available(port):
                suggestions.append(port)
                if len(suggestions) >= count:
                    break

        return suggestions

    def print_port_usage_report(self):
        """Выводит отчет по использованию портов"""
        print("\n" + "=" * 70)
        print(" PORT USAGE REPORT")
        print("=" * 70)

        for service_type, (start, end) in self.PORT_RANGES.items():
            range_ports = [p for p in self.used_ports if start <= p <= end]
            total = end - start + 1
            used = len(range_ports)
            available = total - used

            print(f"\n{service_type.upper()}")
            print(f"  Range: {start}-{end}")
            print(f"  Used: {used}/{total} ({used/total*100:.1f}%)")
            print(f"  Available: {available}")
            if range_ports:
                print(f"  Used ports: {', '.join(map(str, sorted(range_ports)[:10]))}")

        print("\n" + "=" * 70 + "\n")


class ServiceRegistrar:
    """Автоматическая регистрация сервисов в каталоге"""

    def __init__(self):
        self.port_manager = PortManager()

    def create_service_entry(
        self,
        service_name: str,
        service_type: str,
        description: str,
        port: Optional[int] = None,
        component: str = "platform_services",
        **kwargs
    ) -> Dict[str, Any]:
        """Создает запись сервиса для каталога"""

        # Auto-assign port if not provided
        if port is None:
            port = self.port_manager.get_next_available_port(component)

        # Validate port
        if not self.port_manager.is_port_available(port):
            raise ValueError(f"Port {port} is already in use!")

        # Base service entry
        entry = {
            'name': service_name,
            'display_name': kwargs.get('display_name', service_name.replace('_', ' ').title()),
            'registration': {
                'type': service_type,
                'status': kwargs.get('status', 'development'),
                'port': port,
                'version': kwargs.get('version', '1.0.0'),
                'environment': kwargs.get('environment', 'development'),
                'created_date': datetime.now().strftime('%Y-%m-%d'),
            },
            'description': description,
            'purpose': kwargs.get('purpose', []),
            'capabilities': kwargs.get('capabilities', []),
            'runtime': {
                'port': port,
                'protocol': kwargs.get('protocol', 'HTTP/REST'),
                'framework': kwargs.get('framework', 'FastAPI'),
                'language': kwargs.get('language', 'Python 3.11+'),
                'health_endpoint': '/health',
                'metrics_endpoint': '/metrics',
            },
            'dependencies': {
                'required': kwargs.get('required_deps', []),
                'optional': kwargs.get('optional_deps', []),
            },
            'deployment': {
                'location': kwargs.get('location', f'/infrastructure/{service_name}/'),
                'startup': {
                    'command': f'python main.py',
                    'environment_vars': kwargs.get('env_vars', []),
                },
            },
            'kpis': kwargs.get('kpis', []),
            'monitoring': {
                'health_check': f'curl http://localhost:{port}/health',
                'metrics': f'curl http://localhost:{port}/metrics',
                'prometheus_job': service_name,
            },
        }

        return {service_name: entry}

    def register_service(
        self,
        service_name: str,
        service_type: str,
        description: str,
        **kwargs
    ) -> str:
        """Регистрирует сервис в каталоге"""

        print(f"\n{'=' * 70}")
        print(f" REGISTERING SERVICE: {service_name}")
        print(f"{'=' * 70}\n")

        # Create service entry
        entry = self.create_service_entry(
            service_name=service_name,
            service_type=service_type,
            description=description,
            **kwargs
        )

        port = entry[service_name]['registration']['port']

        # Determine catalog file
        catalog_file = PLATFORM_SERVICES_CATALOG / f"{service_name}.yaml"

        # Save to catalog
        catalog_file.parent.mkdir(parents=True, exist_ok=True)

        with open(catalog_file, 'w') as f:
            f.write(f"# {service_name} - Service Catalog Entry\n")
            f.write(f"# Auto-generated by service-registry tool\n")
            f.write(f"# Created: {datetime.now().isoformat()}\n\n")
            yaml.dump(entry, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        print(f" Service registered: {catalog_file}")
        print(f" Port assigned: {port}")
        print(f" Health check: http://localhost:{port}/health")
        print(f"\n{'=' * 70}\n")

        return str(catalog_file)

    def update_main_catalog(self, service_name: str, category: str = "platform_services"):
        """Обновляет главный каталог SERVICE_CATALOG_DETAILED.yaml"""

        main_catalog_file = PLATFORM_SERVICES_CATALOG / "SERVICE_CATALOG_DETAILED.yaml"

        if not main_catalog_file.exists():
            print(f"️  Main catalog not found: {main_catalog_file}")
            return

        # Load main catalog
        with open(main_catalog_file, 'r') as f:
            catalog = yaml.safe_load(f) or {}

        # Update service count
        if category not in catalog:
            catalog[category] = {}

        # Add reference to individual service file
        catalog[category][service_name] = {
            '_reference': f"./{service_name}.yaml",
            'status': 'registered',
            'registered_at': datetime.now().isoformat(),
        }

        # Update metadata
        catalog['total_services'] = sum(
            len(services) for key, services in catalog.items()
            if isinstance(services, dict) and key not in ['version', 'generated_date', 'total_services']
        )
        catalog['generated_date'] = datetime.now().isoformat()

        # Save updated catalog
        with open(main_catalog_file, 'w') as f:
            yaml.dump(catalog, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        print(f" Updated main catalog: {main_catalog_file}")

    def create_service_template(
        self,
        service_name: str,
        port: int,
        location: str
    ) -> str:
        """Создает шаблон кода сервиса"""

        service_dir = REPO_ROOT / location
        service_dir.mkdir(parents=True, exist_ok=True)

        # Create main.py
        main_py = service_dir / "main.py"
        main_py_content = f'''"""
{service_name.replace('_', ' ').title()} Service

Auto-generated service template
Port: {port}
"""

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import logging
import os
import uvicorn

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
PORT = {port}
HOST = "0.0.0.0"

# Create FastAPI app
app = FastAPI(
    title="{service_name.replace('_', ' ').title()} Service",
    description="Auto-generated service",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {{
        "status": "healthy",
        "service": "{service_name}",
        "version": "1.0.0",
        "port": PORT
    }}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
async def root():
    """Root endpoint"""
    return {{
        "service": "{service_name.replace('_', ' ').title()}",
        "version": "1.0.0",
        "port": PORT,
        "endpoints": {{
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs"
        }}
    }}


if __name__ == "__main__":
    logger.info(f" Starting {{service_name}} on port {{PORT}}")
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
'''

        main_py.write_text(main_py_content)

        # Create requirements.txt
        requirements_txt = service_dir / "requirements.txt"
        requirements_txt.write_text("""fastapi==0.104.1
uvicorn==0.24.0
prometheus-client==0.19.0
pydantic==2.5.0
python-dotenv==1.0.0
""")

        # Create README.md
        readme_md = service_dir / "README.md"
        readme_md.write_text(f"""# {service_name.replace('_', ' ').title()} Service

Auto-generated service template.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
python main.py
```

## Endpoints

- Health: `http://localhost:{port}/health`
- Metrics: `http://localhost:{port}/metrics`
- Docs: `http://localhost:{port}/docs`

## Configuration

- Port: {port}
- Service: {service_name}
- Status: Development
""")

        print(f" Created service template: {service_dir}")
        print(f"   - main.py")
        print(f"   - requirements.txt")
        print(f"   - README.md")

        return str(service_dir)


def interactive_registration():
    """Интерактивная регистрация сервиса"""

    registrar = ServiceRegistrar()

    print("\n" + "=" * 70)
    print(" INTERACTIVE SERVICE REGISTRATION")
    print("=" * 70 + "\n")

    # Get service details
    service_name = input("Service name (e.g., my_service): ").strip()
    if not service_name:
        print(" Service name is required!")
        return

    service_type = input("Service type (learning_infrastructure/ai_core/platform/integration): ").strip() or "platform"
    description = input("Description: ").strip() or f"{service_name} service"
    component = input("Component (platform_services/intelligent_core/infrastructure): ").strip() or "platform_services"

    # Port selection
    print(f"\n Suggested ports for {component}:")
    suggestions = registrar.port_manager.get_port_suggestions(component, 5)
    for i, port in enumerate(suggestions, 1):
        print(f"  {i}. Port {port}")

    port_choice = input(f"\nSelect port (1-{len(suggestions)}) or enter custom: ").strip()

    try:
        if port_choice.isdigit() and 1 <= int(port_choice) <= len(suggestions):
            port = suggestions[int(port_choice) - 1]
        else:
            port = int(port_choice)
    except:
        port = registrar.port_manager.get_next_available_port(component)
        print(f"Using auto-assigned port: {port}")

    # Location
    default_location = f"infrastructure/{service_name}"
    location = input(f"Service location (default: {default_location}): ").strip() or default_location

    # Create service template?
    create_template = input("\nCreate service code template? (y/n): ").strip().lower() == 'y'

    # Register
    print("\n Registering service...")

    catalog_file = registrar.register_service(
        service_name=service_name,
        service_type=service_type,
        description=description,
        port=port,
        component=component,
        location=location,
    )

    # Update main catalog
    registrar.update_main_catalog(service_name, component)

    # Create template if requested
    if create_template:
        service_dir = registrar.create_service_template(service_name, port, location)
        print(f"\n Service template created at: {service_dir}")

    print("\n Registration complete!")
    print(f"\n Catalog entry: {catalog_file}")
    print(f" Health check: http://localhost:{port}/health")
    print(f"\nNext steps:")
    print(f"  1. cd {REPO_ROOT / location}")
    print(f"  2. pip install -r requirements.txt")
    print(f"  3. python main.py")


def main():
    """Main entry point"""

    if len(sys.argv) > 1:
        if sys.argv[1] == "ports":
            # Show port usage report
            pm = PortManager()
            pm.print_port_usage_report()
        elif sys.argv[1] == "register":
            # Interactive registration
            interactive_registration()
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Usage: auto_register_service.py [ports|register]")
    else:
        # Default: interactive registration
        interactive_registration()


if __name__ == "__main__":
    main()
