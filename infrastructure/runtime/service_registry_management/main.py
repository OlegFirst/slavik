"""
Service Registry Management Service

REST API для автоматической регистрации и управления сервисами в платформе.

Функции:
- Автоматическая регистрация новых сервисов в каталоге
- Управление портами и предотвращение конфликтов
- Генерация шаблонов кода (FastAPI)
- Интеграция с Service Discovery
- Мониторинг и KPIs

Port: 8200 (infrastructure range: 8200-8299)
"""

import os
import yaml
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
import uvicorn
import httpx

# Configuration
PORT = int(os.getenv("SERVICE_REGISTRY_PORT", 8200))
HOST = "0.0.0.0"
REPO_ROOT = Path(os.getenv("REPO_ROOT", "/Users/MD/AI-Platform-ISO"))
CATALOGS_DIR = REPO_ROOT / "catalogs"
PLATFORM_SERVICES_CATALOG = CATALOGS_DIR / "platform-services"

# Service Discovery integration
SERVICE_DISCOVERY_URL = os.getenv("SERVICE_DISCOVERY_URL", "http://localhost:8500")
ENABLE_SERVICE_DISCOVERY = os.getenv("ENABLE_SERVICE_DISCOVERY", "true").lower() == "true"

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus Metrics
service_registrations_total = Counter(
    'service_registry_registrations_total',
    'Total number of service registrations',
    ['service_type', 'status']
)
active_services_count = Gauge(
    'service_registry_active_services',
    'Number of active registered services'
)
port_usage_gauge = Gauge(
    'service_registry_port_usage',
    'Port usage by service type',
    ['service_type']
)
registration_duration = Histogram(
    'service_registry_registration_duration_seconds',
    'Time to register a service'
)
port_conflicts_total = Counter(
    'service_registry_port_conflicts_total',
    'Total port conflicts detected'
)
template_generations_total = Counter(
    'service_registry_template_generations_total',
    'Total service templates generated'
)

# Port ranges by service type
PORT_RANGES = {
    'platform_services': (8000, 8099),
    'intelligent_core': (8100, 8199),
    'infrastructure': (8200, 8299),
    'integration': (8300, 8399),
    'monitoring': (9000, 9099),
    'databases': (5000, 5099),
}

# FastAPI app
app = FastAPI(
    title="Service Registry Management",
    description="Автоматическая регистрация и управление сервисами в AI Platform",
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


# ===================================
# Models
# ===================================

class ServiceType(str, Enum):
    LEARNING_INFRASTRUCTURE = "learning_infrastructure"
    AI_CORE = "ai_core"
    PLATFORM = "platform"
    INTEGRATION = "integration"
    INFRASTRUCTURE = "infrastructure"


class ComponentType(str, Enum):
    PLATFORM_SERVICES = "platform_services"
    INTELLIGENT_CORE = "intelligent_core"
    INFRASTRUCTURE = "infrastructure"


class ServiceRegistrationRequest(BaseModel):
    service_name: str = Field(..., description="Имя сервиса (например, my_service)")
    service_type: ServiceType = Field(..., description="Тип сервиса")
    description: str = Field(..., description="Описание сервиса")
    component: ComponentType = Field(default=ComponentType.PLATFORM_SERVICES, description="Компонент платформы")
    port: Optional[int] = Field(None, description="Порт (автоматически назначается если не указан)")
    location: Optional[str] = Field(None, description="Расположение в проекте")
    create_template: bool = Field(default=False, description="Создать шаблон кода")

    # Optional metadata
    purpose: List[str] = Field(default_factory=list, description="Назначение сервиса")
    capabilities: List[str] = Field(default_factory=list, description="Возможности сервиса")
    dependencies: List[str] = Field(default_factory=list, description="Зависимости")


class PortSuggestion(BaseModel):
    port: int
    available: bool
    in_catalog: bool
    in_system: bool


class PortUsageStats(BaseModel):
    service_type: str
    range_start: int
    range_end: int
    total_ports: int
    used_ports: int
    available_ports: int
    usage_percent: float
    used_port_list: List[int]


class ServiceRegistrationResponse(BaseModel):
    success: bool
    service_name: str
    catalog_file: str
    port: int
    health_check_url: str
    template_created: bool
    template_location: Optional[str] = None
    message: str


# ===================================
# Port Management
# ===================================

class PortManager:
    """Управление портами и проверка доступности"""

    def __init__(self):
        self.used_ports = self._scan_used_ports()
        logger.info(f"PortManager initialized with {len(self.used_ports)} used ports")

    def _scan_used_ports(self) -> List[int]:
        """Сканирует все используемые порты из каталогов"""
        used_ports = []

        try:
            # Scan all YAML files in catalogs
            for yaml_file in CATALOGS_DIR.rglob("*.yaml"):
                try:
                    with open(yaml_file, 'r') as f:
                        data = yaml.safe_load(f)

                    # Extract ports from different structures
                    ports = self._extract_ports_from_yaml(data)
                    used_ports.extend(ports)

                except Exception as e:
                    logger.warning(f"Error reading {yaml_file}: {e}")

        except Exception as e:
            logger.error(f"Error scanning catalogs: {e}")

        # Filter out None values and return unique sorted list
        return sorted(set(p for p in used_ports if p is not None))

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
        if service_type not in PORT_RANGES:
            service_type = 'platform_services'

        start, end = PORT_RANGES[service_type]

        for port in range(start, end + 1):
            if port not in self.used_ports:
                return port

        raise ValueError(f"No available ports in range {start}-{end} for {service_type}")

    def is_port_available(self, port: int) -> bool:
        """Проверяет доступность порта"""
        return port not in self.used_ports

    def get_port_suggestions(self, service_type: str, count: int = 5) -> List[PortSuggestion]:
        """Предлагает несколько свободных портов"""
        suggestions = []
        start, end = PORT_RANGES.get(service_type, (8000, 8099))

        for port in range(start, end + 1):
            if len(suggestions) >= count:
                break

            available = self.is_port_available(port)
            if available:
                suggestions.append(PortSuggestion(
                    port=port,
                    available=True,
                    in_catalog=False,
                    in_system=False
                ))

        return suggestions

    def get_usage_stats(self) -> Dict[str, PortUsageStats]:
        """Возвращает статистику использования портов"""
        stats = {}

        for service_type, (start, end) in PORT_RANGES.items():
            range_ports = [p for p in self.used_ports if start <= p <= end]
            total = end - start + 1
            used = len(range_ports)
            available = total - used

            stats[service_type] = PortUsageStats(
                service_type=service_type,
                range_start=start,
                range_end=end,
                total_ports=total,
                used_ports=used,
                available_ports=available,
                usage_percent=round((used / total * 100) if total > 0 else 0, 1),
                used_port_list=sorted(range_ports)[:10]  # First 10 used ports
            )

            # Update Prometheus metrics
            port_usage_gauge.labels(service_type=service_type).set(used)

        return stats


# ===================================
# Service Registrar
# ===================================

class ServiceRegistrar:
    """Автоматическая регистрация сервисов в каталоге"""

    def __init__(self, port_manager: PortManager):
        self.port_manager = port_manager

    async def register_in_service_discovery(self, service_name: str, port: int, service_type: str) -> bool:
        """Регистрирует сервис в Service Discovery"""
        if not ENABLE_SERVICE_DISCOVERY:
            logger.info("Service Discovery integration disabled")
            return False

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Register in Service Discovery (Consul-compatible endpoint)
                response = await client.post(
                    f"{SERVICE_DISCOVERY_URL}/v1/agent/service/register",
                    json={
                        "service_id": f"{service_name}-{port}",
                        "service_name": service_name,
                        "host": "localhost",
                        "port": port,
                        "tags": [service_type, "auto-registered"],
                        "meta": {
                            "registered_by": "service-registry-management",
                            "registered_at": datetime.now().isoformat(),
                            "auto_generated": "true"
                        }
                    }
                )

                if response.status_code == 200:
                    logger.info(f"✅ Service {service_name} registered in Service Discovery")
                    return True
                else:
                    logger.warning(f"⚠️  Service Discovery registration failed: {response.status_code}")
                    return False

        except Exception as e:
            logger.warning(f"⚠️  Could not register in Service Discovery: {e}")
            return False

    def create_catalog_entry(self, request: ServiceRegistrationRequest, port: int) -> Dict[str, Any]:
        """Создает запись для каталога"""

        location = request.location or f"infrastructure/{request.service_name}"

        entry = {
            request.service_name: {
                'name': request.service_name,
                'display_name': request.service_name.replace('_', ' ').title(),
                'registration': {
                    'type': request.service_type.value,
                    'status': 'development',
                    'port': port,
                    'version': '1.0.0',
                    'environment': 'development',
                    'created_date': datetime.now().strftime('%Y-%m-%d'),
                },
                'description': request.description,
                'purpose': request.purpose,
                'capabilities': request.capabilities,
                'runtime': {
                    'port': port,
                    'protocol': 'HTTP/REST',
                    'framework': 'FastAPI',
                    'language': 'Python 3.11+',
                    'health_endpoint': '/health',
                    'metrics_endpoint': '/metrics',
                },
                'dependencies': {
                    'required': request.dependencies,
                    'optional': [],
                },
                'deployment': {
                    'location': f'/{location}/',
                    'startup': {
                        'command': 'python main.py',
                        'environment_vars': [],
                    },
                },
                'kpis': [],
                'monitoring': {
                    'health_check': f'curl http://localhost:{port}/health',
                    'metrics': f'curl http://localhost:{port}/metrics',
                    'prometheus_job': request.service_name,
                },
            }
        }

        return entry

    async def register_service(self, request: ServiceRegistrationRequest) -> ServiceRegistrationResponse:
        """Регистрирует сервис в каталоге"""

        with registration_duration.time():
            try:
                # Assign port
                if request.port:
                    if not self.port_manager.is_port_available(request.port):
                        port_conflicts_total.inc()
                        raise HTTPException(
                            status_code=409,
                            detail=f"Port {request.port} is already in use"
                        )
                    port = request.port
                else:
                    port = self.port_manager.get_next_available_port(request.component.value)

                # Create catalog entry
                entry = self.create_catalog_entry(request, port)

                # Save to catalog
                catalog_file = PLATFORM_SERVICES_CATALOG / f"{request.service_name}.yaml"
                catalog_file.parent.mkdir(parents=True, exist_ok=True)

                with open(catalog_file, 'w') as f:
                    f.write(f"# {request.service_name} - Service Catalog Entry\n")
                    f.write(f"# Auto-generated by Service Registry Management\n")
                    f.write(f"# Created: {datetime.now().isoformat()}\n\n")
                    yaml.dump(entry, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

                # Update metrics
                service_registrations_total.labels(
                    service_type=request.service_type.value,
                    status='success'
                ).inc()

                # Create template if requested
                template_location = None
                if request.create_template:
                    template_location = self.create_service_template(request, port)
                    template_generations_total.inc()

                # Register in Service Discovery
                await self.register_in_service_discovery(
                    service_name=request.service_name,
                    port=port,
                    service_type=request.service_type.value
                )

                logger.info(f"✅ Service registered: {request.service_name} on port {port}")

                return ServiceRegistrationResponse(
                    success=True,
                    service_name=request.service_name,
                    catalog_file=str(catalog_file),
                    port=port,
                    health_check_url=f"http://localhost:{port}/health",
                    template_created=request.create_template,
                    template_location=template_location,
                    message=f"Service {request.service_name} successfully registered on port {port}"
                )

            except HTTPException:
                raise
            except Exception as e:
                service_registrations_total.labels(
                    service_type=request.service_type.value,
                    status='error'
                ).inc()
                logger.error(f"Failed to register service: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    def create_service_template(self, request: ServiceRegistrationRequest, port: int) -> str:
        """Создает шаблон кода сервиса"""

        location = request.location or f"infrastructure/{request.service_name}"
        service_dir = REPO_ROOT / location
        service_dir.mkdir(parents=True, exist_ok=True)

        # Create main.py
        main_py = service_dir / "main.py"
        main_py_content = f'''"""
{request.service_name.replace('_', ' ').title()} Service

{request.description}

Port: {port}
Auto-generated by Service Registry Management
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
PORT = int(os.getenv("PORT", {port}))
HOST = "0.0.0.0"

# Create FastAPI app
app = FastAPI(
    title="{request.service_name.replace('_', ' ').title()} Service",
    description="{request.description}",
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
        "service": "{request.service_name}",
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
        "service": "{request.service_name.replace('_', ' ').title()}",
        "description": "{request.description}",
        "version": "1.0.0",
        "port": PORT,
        "endpoints": {{
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs"
        }}
    }}


if __name__ == "__main__":
    logger.info(f"🚀 Starting {request.service_name} on port {{PORT}}")
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
        readme_md.write_text(f"""# {request.service_name.replace('_', ' ').title()} Service

{request.description}

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

- **Port**: {port}
- **Service**: {request.service_name}
- **Type**: {request.service_type.value}
- **Component**: {request.component.value}

## Purpose

{chr(10).join('- ' + p for p in request.purpose) if request.purpose else '- To be defined'}

## Capabilities

{chr(10).join('- ' + c for c in request.capabilities) if request.capabilities else '- To be defined'}

---

Auto-generated by Service Registry Management
""")

        logger.info(f"✅ Created service template: {service_dir}")

        return str(service_dir)


# ===================================
# Global instances
# ===================================

port_manager = PortManager()
service_registrar = ServiceRegistrar(port_manager)


# ===================================
# API Endpoints
# ===================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "service-registry-management",
        "version": "1.0.0",
        "port": PORT,
        "catalogs_dir": str(CATALOGS_DIR),
        "total_services": len(port_manager.used_ports)
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # Update active services count
    active_services_count.set(len(port_manager.used_ports))

    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Service Registry Management",
        "version": "1.0.0",
        "port": PORT,
        "description": "Автоматическая регистрация и управление сервисами в AI Platform",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs",
            "port_usage": "/api/v1/ports/usage",
            "port_suggestions": "/api/v1/ports/suggestions/{service_type}",
            "register_service": "POST /api/v1/services/register"
        }
    }


@app.get("/api/v1/ports/usage", response_model=Dict[str, PortUsageStats])
async def get_port_usage():
    """Получить статистику использования портов"""
    return port_manager.get_usage_stats()


@app.get("/api/v1/ports/suggestions/{service_type}", response_model=List[PortSuggestion])
async def get_port_suggestions(service_type: str, count: int = 5):
    """Получить предложения свободных портов"""
    if service_type not in PORT_RANGES:
        raise HTTPException(status_code=400, detail=f"Unknown service type: {service_type}")

    return port_manager.get_port_suggestions(service_type, count)


@app.post("/api/v1/services/register", response_model=ServiceRegistrationResponse)
async def register_service(request: ServiceRegistrationRequest):
    """Зарегистрировать новый сервис"""
    return await service_registrar.register_service(request)


@app.get("/api/v1/services/stats")
async def get_service_stats():
    """Получить статистику сервисов"""
    port_stats = port_manager.get_usage_stats()

    total_services = len(port_manager.used_ports)
    total_capacity = sum(stats.total_ports for stats in port_stats.values())
    total_used = sum(stats.used_ports for stats in port_stats.values())
    total_available = sum(stats.available_ports for stats in port_stats.values())

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "total_services": total_services,
        "total_capacity": total_capacity,
        "total_used": total_used,
        "total_available": total_available,
        "usage_percent": round((total_used / total_capacity * 100) if total_capacity > 0 else 0, 1),
        "by_type": {k: v.dict() for k, v in port_stats.items()}
    }


if __name__ == "__main__":
    logger.info(f"🚀 Starting Service Registry Management on port {PORT}")
    logger.info(f"📁 Catalogs directory: {CATALOGS_DIR}")
    logger.info(f"📊 Total services in catalog: {len(port_manager.used_ports)}")

    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
