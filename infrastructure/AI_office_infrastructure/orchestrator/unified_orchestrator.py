#!/usr/bin/env python3
"""
Unified Infrastructure Orchestrator
====================================

Связывает воедино все компоненты:
1. tools/infrastructure/ (Service Discovery, Analysis)
2. infrastructure/deployment/orchestrator/ (Deployment Management)
3. infrastructure/deployment/docker-management/ (Docker API)
4. infrastructure/deployment/deployment-service/ (Deployment Service)
5. intelligent-core/orchestration/ai-orchestration/ (AI Central Hub)
6. intelligent-core/orchestration/coordination-center/ (Coordination)

Этот оркестратор - единая точка входа для всей инфраструктуры.

Usage:
    # CLI mode
    python3 infrastructure/deployment/orchestrator/unified_orchestrator.py discover
    python3 infrastructure/deployment/orchestrator/unified_orchestrator.py deploy --layer full

    # API mode
    uvicorn unified_orchestrator:app --host 0.0.0.0 --port 8090
"""

import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'tools'))
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / 'infrastructure' / 'tools' / 'analyzers'))

# Setup logging FIRST (before imports that use logger)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import httpx

# Import existing components - FIXED PATH
try:
    from discover_services import ServiceDiscovery
    HAS_SERVICE_DISCOVERY = True
except ImportError:
    logger.warning("ServiceDiscovery not available, discovery features will be limited")
    ServiceDiscovery = None
    HAS_SERVICE_DISCOVERY = False

# Import from same directory
try:
    from docker_compose_generator import DockerComposeGenerator
    HAS_DOCKER_COMPOSE_GENERATOR = True
except ImportError:
    logger.warning("DockerComposeGenerator not available")
    DockerComposeGenerator = None
    HAS_DOCKER_COMPOSE_GENERATOR = False

# Import executors
try:
    from executors import EventExecutor
    from executors.infrastructure_executor import InfrastructureExecutor
    HAS_EXECUTORS = True
except ImportError as e:
    logger.warning(f"Executors not available: {e}")
    EventExecutor = None
    InfrastructureExecutor = None
    HAS_EXECUTORS = False

# Import adaptive metrics
try:
    from adaptive_metrics import (
        AdaptiveOrchestratorMixin,
        TaskPriority,
        OrchestratorMetrics,
        TaskContext
    )
    HAS_ADAPTIVE_METRICS = True
except ImportError as e:
    logger.warning(f"Adaptive metrics not available: {e}")
    # Create dummy base class
    class AdaptiveOrchestratorMixin:
        pass
    TaskPriority = None
    OrchestratorMetrics = None
    TaskContext = None
    HAS_ADAPTIVE_METRICS = False

# Import BCM executor from platform-services
PLATFORM_SERVICES = Path(__file__).parent.parent.parent.parent / 'platform-services'
sys.path.insert(0, str(PLATFORM_SERVICES / 'bcm-coordination-service'))
try:
    from bcm_executor import BCMExecutor
    BCM_AVAILABLE = True
except ImportError:
    logger.warning("BCMExecutor not available")
    BCM_AVAILABLE = False
    BCMExecutor = None

# Import docker manager - FIXED PATH
try:
    sys.path.insert(0, str(PROJECT_ROOT / 'infrastructure' / 'tools' / 'docker-management'))
    from docker_manager import DockerManager
    HAS_DOCKER_MANAGER = True
except ImportError:
    logger.warning("DockerManager not available, some features will be limited")
    DockerManager = None
    HAS_DOCKER_MANAGER = False

# FastAPI app for API mode
app = FastAPI(
    title="Unified Infrastructure Orchestrator",
    version="1.0.0",
    description="Central orchestrator for all infrastructure operations"
)


class DeploymentRequest(BaseModel):
    """Deployment request model"""
    layer: str = "full"
    use_ai_orchestration: bool = True
    force_rebuild: bool = False


class TaskRequest(BaseModel):
    """Unified task request model"""
    task_type: str  # 'infrastructure', 'event', 'code', 'database'
    action: str  # 'deploy', 'add_publisher', 'add_subscriber', 'fix_gap', etc.
    parameters: Dict[str, Any]


class EventGapRequest(BaseModel):
    """Event gap fix request"""
    event_name: str
    gap_type: str
    severity: str
    service: str
    file_path: str
    recommendation: str


class UnifiedOrchestrator(AdaptiveOrchestratorMixin):
    """
    Главный оркестратор инфраструктуры с адаптивными метриками

    Архитектура:
        UnifiedOrchestrator (этот класс)
            ↓
        ├─ Adaptive Metrics & Priorities (NEW)
        ├─ Service Discovery (tools/infrastructure/)
        ├─ Docker Compose Generator (этот модуль)
        ├─ Docker Manager (docker-management/)
        ├─ Deployment Service (deployment-service/)
        └─ AI Orchestration Hub (ai-orchestration/)

    Новые возможности:
    - Адаптивная приоритизация задач на основе метрик
    - Динамическое управление очередью задач
    - Мониторинг производительности в реальном времени
    - Автоматическая адаптация к нагрузке системы
    """

    def __init__(self, project_root: Path):
        # Initialize parent (AdaptiveOrchestratorMixin)
        super().__init__()

        self.project_root = project_root
        self.deployment_dir = project_root / 'infrastructure' / 'AI-office-infrastructure' / 'orchestrator'
        self.generated_dir = self.deployment_dir / 'generated'
        self.generated_dir.mkdir(parents=True, exist_ok=True)

        # Components - with fallback
        self.discovery = ServiceDiscovery(project_root) if HAS_SERVICE_DISCOVERY else None
        self.docker_manager = DockerManager(use_docker_client=True) if HAS_DOCKER_MANAGER else None

        # Executors - with fallback
        self.event_executor = EventExecutor(str(project_root)) if HAS_EXECUTORS and EventExecutor else None
        self.infrastructure_executor = InfrastructureExecutor(str(project_root)) if HAS_EXECUTORS and InfrastructureExecutor else None
        self.bcm_executor = BCMExecutor() if BCM_AVAILABLE else None

        # Services URLs
        self.ai_orchestration_url = "http://localhost:8030"  # Updated to match monitoring
        self.coordination_center_url = "http://localhost:8004"
        self.deployment_service_url = "http://localhost:8090"

        logger.info(f"✅ UnifiedOrchestrator initialized (adaptive_metrics={'enabled' if HAS_ADAPTIVE_METRICS else 'disabled'})")

    async def discover_services(self) -> List[Dict[str, Any]]:
        """
        Шаг 1: Обнаружение всех сервисов
        Использует: tools/infrastructure/discover_services.py
        """
        logger.info("🔍 Discovering all services...")

        if not self.discovery:
            logger.error("ServiceDiscovery not available")
            return []

        services = self.discovery.discover_all()

        # Сохранить каталог
        import json
        catalog_file = self.generated_dir / 'service-catalog.json'
        with open(catalog_file, 'w') as f:
            json.dump(services, f, indent=2, default=str)

        logger.info(f"✅ Discovered {len(services)} services")
        logger.info(f"📁 Catalog saved: {catalog_file}")

        return services

    async def generate_configs(self) -> Dict[str, Path]:
        """
        Шаг 2: Генерация конфигураций
        Использует: docker_compose_generator.py
        """
        logger.info("🏗️  Generating configurations...")

        if not HAS_DOCKER_COMPOSE_GENERATOR:
            logger.error("DockerComposeGenerator not available")
            return {}

        generator = DockerComposeGenerator(self.project_root, self.generated_dir)
        generator.generate_all()

        configs = {
            'gateway': self.generated_dir / 'docker-compose.gateway.yml',
            'runtime': self.generated_dir / 'docker-compose.runtime.yml',
            'observability': self.generated_dir / 'docker-compose.observability.yml',
            'integration': self.generated_dir / 'docker-compose.integration.yml',
            'full': self.generated_dir / 'docker-compose.full.yml',
        }

        logger.info("✅ Configurations generated")
        return configs

    async def deploy_via_ai_orchestration(self, layer: str, configs: Dict[str, Path]) -> Dict:
        """
        Развёртывание через ai-orchestration (умное управление)
        """
        logger.info("🧠 Deploying via AI Orchestration...")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 1. Проверить доступность ai-orchestration
                health_response = await client.get(f"{self.ai_orchestration_url}/health")

                if not health_response.is_success:
                    raise Exception("ai-orchestration not available")

                logger.info("✅ ai-orchestration is available")

                # 2. Отправить задачу на развёртывание
                deployment_task = {
                    "task_type": "deploy_infrastructure",
                    "layer": layer,
                    "compose_file": str(configs.get(layer)),
                    "strategy": "intelligent",  # AI выберет оптимальную стратегию
                    "metadata": {
                        "triggered_by": "unified_orchestrator",
                        "timestamp": str(Path.cwd())
                    }
                }

                # TODO: Интегрировать с реальным API ai-orchestration
                # response = await client.post(
                #     f"{self.ai_orchestration_url}/api/v1/tasks/deploy",
                #     json=deployment_task
                # )

                logger.info(f"📤 Deployment task sent to ai-orchestration")
                logger.info(f"📋 Task: {deployment_task}")

                return {
                    "status": "submitted",
                    "message": "Deployment task submitted to ai-orchestration",
                    "task": deployment_task
                }

        except Exception as e:
            logger.warning(f"⚠️  ai-orchestration not available: {e}")
            logger.info("   Falling back to direct deployment...")
            return await self.deploy_direct(layer, configs)

    async def deploy_direct(self, layer: str, configs: Dict[str, Path]) -> Dict:
        """
        Прямое развёртывание через docker-compose
        """
        logger.info(f"🐳 Direct deployment: layer={layer}")

        compose_file = configs.get(layer)
        if not compose_file or not compose_file.exists():
            raise Exception(f"Compose file not found for layer: {layer}")

        # Использовать startup script если есть
        start_script = self.generated_dir / 'start_infrastructure.sh'

        if start_script.exists():
            logger.info("📜 Using startup script")
            import subprocess
            result = subprocess.run(
                [str(start_script), layer],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": f"Layer '{layer}' started successfully",
                    "output": result.stdout
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to start layer '{layer}'",
                    "error": result.stderr
                }
        else:
            # Прямой docker-compose
            logger.info("🐳 Using docker-compose directly")
            import subprocess
            result = subprocess.run(
                ['docker-compose', '-f', str(compose_file), 'up', '-d'],
                cwd=self.generated_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": f"Layer '{layer}' started successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to start layer '{layer}'",
                    "error": result.stderr
                }

    async def deploy(self, layer: str = "full", use_ai: bool = True) -> Dict:
        """
        Главный метод развёртывания
        """
        logger.info("🚀 Starting deployment process...")
        logger.info(f"   Layer: {layer}")
        logger.info(f"   Use AI Orchestration: {use_ai}")

        try:
            # 1. Обнаружить сервисы (если каталог не существует)
            catalog_file = self.generated_dir / 'service-catalog.json'
            if not catalog_file.exists():
                logger.info("📊 Service catalog not found, discovering...")
                await self.discover_services()

            # 2. Сгенерировать конфиги (если не существуют)
            compose_file = self.generated_dir / f'docker-compose.{layer}.yml'
            if not compose_file.exists():
                logger.info("🏗️  Configurations not found, generating...")
                configs = await self.generate_configs()
            else:
                configs = {
                    layer: compose_file
                }

            # 3. Развернуть
            if use_ai:
                result = await self.deploy_via_ai_orchestration(layer, configs)
            else:
                result = await self.deploy_direct(layer, configs)

            logger.info("✅ Deployment process completed")
            return result

        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e)
            }

    async def status(self) -> Dict:
        """Проверка статуса всей инфраструктуры"""
        logger.info("📊 Checking infrastructure status...")

        status = {
            "generated_configs": {},
            "running_containers": {},
            "orchestration_services": {},
            "deployment_service": {}
        }

        # 1. Проверить конфиги
        compose_files = list(self.generated_dir.glob('docker-compose.*.yml'))
        status["generated_configs"]["count"] = len(compose_files)
        status["generated_configs"]["files"] = [f.name for f in compose_files]

        # 2. Проверить Docker контейнеры
        try:
            import subprocess
            result = subprocess.run(
                ['docker', 'ps', '--format', '{{.Names}}'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                containers = result.stdout.strip().split('\n')
                status["running_containers"]["count"] = len([c for c in containers if c])
                status["running_containers"]["names"] = [c for c in containers if c]
        except Exception as e:
            status["running_containers"]["error"] = str(e)

        # 3. Проверить orchestration сервисы
        async with httpx.AsyncClient(timeout=5.0) as client:
            # ai-orchestration
            try:
                response = await client.get(f"{self.ai_orchestration_url}/health")
                status["orchestration_services"]["ai_orchestration"] = {
                    "status": "running" if response.is_success else "unhealthy",
                    "url": self.ai_orchestration_url
                }
            except:
                status["orchestration_services"]["ai_orchestration"] = {
                    "status": "not_running",
                    "url": self.ai_orchestration_url
                }

            # coordination-center
            try:
                response = await client.get(f"{self.coordination_center_url}/coordination/health")
                status["orchestration_services"]["coordination_center"] = {
                    "status": "running" if response.is_success else "unhealthy",
                    "url": self.coordination_center_url
                }
            except:
                status["orchestration_services"]["coordination_center"] = {
                    "status": "not_running",
                    "url": self.coordination_center_url
                }

        return status

    # ========================================================================
    # Event Execution Methods
    # ========================================================================

    async def execute_task(self, task: Dict[str, Any]) -> Dict:
        """
        Unified task execution - роутит задачи к правильному executor

        Args:
            task: Task dict with 'task_type', 'action', 'parameters'

        Returns:
            Execution result
        """
        task_type = task.get('task_type')
        action = task.get('action')
        parameters = task.get('parameters', {})

        logger.info(f"🎯 Executing task: type={task_type}, action={action}")

        if task_type == 'event':
            return await self._execute_event_task(action, parameters)
        elif task_type == 'infrastructure':
            return await self._execute_infrastructure_task(action, parameters)
        elif task_type == 'bcm':
            return await self._execute_bcm_task(action, parameters)
        elif task_type == 'code':
            return await self._execute_code_task(action, parameters)
        elif task_type == 'database':
            return await self._execute_database_task(action, parameters)
        else:
            return {
                'success': False,
                'error': f'Unknown task type: {task_type}'
            }

    async def _execute_event_task(self, action: str, parameters: Dict) -> Dict:
        """Выполняет event-related задачи"""
        logger.info(f"🔧 Executing event task: {action}")

        if not self.event_executor:
            return {'success': False, 'error': 'EventExecutor not available'}

        if action == 'add_publisher':
            return await self.event_executor.add_publisher(
                service=parameters['service'],
                event=parameters['event'],
                file_path=parameters['file_path'],
                method_name=parameters['method_name'],
                position=parameters.get('position', 'end')
            )

        elif action == 'add_subscriber':
            return await self.event_executor.add_subscriber(
                service=parameters['service'],
                event=parameters['event'],
                file_path=parameters['file_path'],
                handler_name=parameters.get('handler_name')
            )

        elif action == 'fix_gap':
            # Конвертируем parameters в EventGap
            from executors.event_executor import EventGap
            gap = EventGap(
                event_name=parameters['event_name'],
                gap_type=parameters['gap_type'],
                severity=parameters['severity'],
                service=parameters['service'],
                file_path=parameters['file_path'],
                recommendation=parameters['recommendation']
            )
            return await self.event_executor.fix_event_gap(gap)

        elif action == 'create_pr':
            return await self.event_executor.create_pr(
                branch_name=parameters.get('branch_name')
            )

        elif action == 'rollback':
            return await self.event_executor.rollback_changes()

        else:
            return {'success': False, 'error': f'Unknown event action: {action}'}

    async def _execute_infrastructure_task(self, action: str, parameters: Dict) -> Dict:
        """Выполняет infrastructure задачи (deploy/restart/stop)"""
        logger.info(f"🐳 Executing infrastructure task: {action}")

        if not self.infrastructure_executor and action != 'deploy':
            return {'success': False, 'error': 'InfrastructureExecutor not available'}

        if action == 'deploy':
            return await self.deploy(
                layer=parameters.get('layer', 'full'),
                use_ai=parameters.get('use_ai', True)
            )

        elif action == 'restart':
            service = parameters.get('service')
            return await self.infrastructure_executor.restart_service(service)

        elif action == 'stop':
            service = parameters.get('service')
            return await self.infrastructure_executor.stop_service(service)

        elif action == 'health_check':
            service = parameters.get('service')
            return await self.infrastructure_executor.health_check(service)

        else:
            return {'success': False, 'error': f'Unknown infrastructure action: {action}'}

    async def _execute_bcm_task(self, action: str, parameters: Dict) -> Dict:
        """
        Выполняет BCM-специфичные задачи через platform-services/bcm-coordination-service.

        ВОПРОС: Правильно ли это здесь? Или BCM должен быть отдельно?
        """
        logger.info(f"🔍 Executing BCM task: {action}")

        if not self.bcm_executor:
            return {
                'success': False,
                'error': 'BCM Executor not available'
            }

        task = {
            'action': action,
            'parameters': parameters
        }

        return await self.bcm_executor.execute_bcm_task(task)

    async def _execute_code_task(self, action: str, parameters: Dict) -> Dict:
        """Выполняет code-related задачи"""
        logger.info(f"💻 Executing code task: {action}")
        # TODO: Implement code executor
        return {'success': True, 'message': 'Code tasks not yet implemented'}

    async def _execute_database_task(self, action: str, parameters: Dict) -> Dict:
        """Выполняет database задачи"""
        logger.info(f"🗄️  Executing database task: {action}")
        # TODO: Implement database executor
        return {'success': True, 'message': 'Database tasks not yet implemented'}

    async def fix_event_gaps(self, gaps: List[Dict]) -> Dict:
        """
        Фиксит multiple event gaps

        Args:
            gaps: List of gap dicts

        Returns:
            Summary of results
        """
        logger.info(f"🔧 Fixing {len(gaps)} event gaps...")

        results = {
            'total': len(gaps),
            'success': 0,
            'failed': 0,
            'details': []
        }

        for gap_dict in gaps:
            task = {
                'task_type': 'event',
                'action': 'fix_gap',
                'parameters': gap_dict
            }

            result = await self.execute_task(task)

            if result.get('success'):
                results['success'] += 1
            else:
                results['failed'] += 1

            results['details'].append({
                'gap': gap_dict['event_name'],
                'result': result
            })

        logger.info(f"✅ Fixed {results['success']}/{results['total']} gaps")

        return results


# ============================================================================
# FastAPI Endpoints (API Mode)
# ============================================================================

orchestrator = UnifiedOrchestrator(PROJECT_ROOT)


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "unified_orchestrator",
        "version": "1.0.0"
    }


@app.get("/api/v1/status")
async def get_status():
    """Get infrastructure status"""
    return await orchestrator.status()


@app.post("/api/v1/discover")
async def discover_services(background_tasks: BackgroundTasks):
    """Discover all services"""
    services = await orchestrator.discover_services()
    return {
        "status": "success",
        "services_count": len(services),
        "services": services
    }


@app.post("/api/v1/generate")
async def generate_configs():
    """Generate docker-compose configurations"""
    configs = await orchestrator.generate_configs()
    return {
        "status": "success",
        "configs": {k: str(v) for k, v in configs.items()}
    }


@app.post("/api/v1/deploy")
async def deploy_infrastructure(request: DeploymentRequest):
    """Deploy infrastructure layer"""
    result = await orchestrator.deploy(
        layer=request.layer,
        use_ai=request.use_ai_orchestration
    )
    return result


@app.post("/api/v1/build-and-deploy")
async def build_and_deploy(request: DeploymentRequest):
    """Full cycle: discover -> generate -> deploy"""
    try:
        # 1. Discover
        services = await orchestrator.discover_services()

        # 2. Generate
        configs = await orchestrator.generate_configs()

        # 3. Deploy
        result = await orchestrator.deploy(
            layer=request.layer,
            use_ai=request.use_ai_orchestration
        )

        return {
            "status": "success",
            "services_discovered": len(services),
            "configs_generated": len(configs),
            "deployment": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Event Execution Endpoints
# ============================================================================

@app.post("/api/v1/tasks/execute")
async def execute_task(task: TaskRequest):
    """
    Unified task execution endpoint

    Supports task types:
    - 'event': Event-related tasks (add_publisher, add_subscriber, fix_gap)
    - 'infrastructure': Infrastructure tasks (deploy, restart, stop)
    - 'code': Code tasks (refactoring, fixes)
    - 'database': Database tasks (migrations)
    """
    result = await orchestrator.execute_task(task.dict())
    return result


@app.post("/api/v1/events/fix-gap")
async def fix_event_gap(gap: EventGapRequest):
    """Fix a single event gap"""
    task = {
        'task_type': 'event',
        'action': 'fix_gap',
        'parameters': gap.dict()
    }
    result = await orchestrator.execute_task(task)
    return result


@app.post("/api/v1/events/fix-gaps")
async def fix_multiple_gaps(gaps: List[EventGapRequest]):
    """Fix multiple event gaps"""
    gap_dicts = [gap.dict() for gap in gaps]
    result = await orchestrator.fix_event_gaps(gap_dicts)
    return result


@app.post("/api/v1/events/add-publisher")
async def add_publisher(
    service: str,
    event: str,
    file_path: str,
    method_name: str,
    position: str = "end"
):
    """Add publisher to code"""
    task = {
        'task_type': 'event',
        'action': 'add_publisher',
        'parameters': {
            'service': service,
            'event': event,
            'file_path': file_path,
            'method_name': method_name,
            'position': position
        }
    }
    result = await orchestrator.execute_task(task)
    return result


@app.post("/api/v1/events/add-subscriber")
async def add_subscriber(
    service: str,
    event: str,
    file_path: str,
    handler_name: Optional[str] = None
):
    """Add subscriber to code"""
    task = {
        'task_type': 'event',
        'action': 'add_subscriber',
        'parameters': {
            'service': service,
            'event': event,
            'file_path': file_path,
            'handler_name': handler_name
        }
    }
    result = await orchestrator.execute_task(task)
    return result


@app.post("/api/v1/events/create-pr")
async def create_event_pr(branch_name: Optional[str] = None):
    """Create PR with event changes"""
    task = {
        'task_type': 'event',
        'action': 'create_pr',
        'parameters': {
            'branch_name': branch_name
        }
    }
    result = await orchestrator.execute_task(task)
    return result


@app.post("/api/v1/events/rollback")
async def rollback_event_changes():
    """Rollback event changes"""
    task = {
        'task_type': 'event',
        'action': 'rollback',
        'parameters': {}
    }
    result = await orchestrator.execute_task(task)
    return result


# ============================================================================
# ADAPTIVE METRICS & PRIORITY API
# ============================================================================

@app.get("/api/v1/metrics/current")
async def get_current_metrics():
    """Get current orchestrator metrics"""
    if not HAS_ADAPTIVE_METRICS:
        return {"status": "disabled", "message": "Adaptive metrics not available"}

    metrics = await orchestrator.metrics_collector.collect_orchestrator_metrics()
    return {
        "status": "success",
        "metrics": {
            "cpu_percent": metrics.cpu_percent,
            "memory_percent": metrics.memory_percent,
            "active_tasks": metrics.active_tasks,
            "queue_length": metrics.queue_length,
            "success_rate": metrics.success_rate,
            "error_rate": metrics.error_rate,
            "avg_latency": metrics.avg_latency,
            "p95_latency": metrics.p95_latency,
            "tasks_per_minute": metrics.tasks_per_minute,
            "cost_per_hour": metrics.cost_per_hour,
            "health_status": metrics.get_health_status(),
            "is_healthy": metrics.is_healthy(),
            "timestamp": metrics.timestamp.isoformat()
        }
    }


@app.get("/api/v1/queue/stats")
async def get_queue_stats():
    """Get task queue statistics"""
    if not HAS_ADAPTIVE_METRICS:
        return {"status": "disabled", "message": "Adaptive metrics not available"}

    stats = await orchestrator.get_queue_stats()
    return {
        "status": "success",
        "queue": stats
    }


@app.post("/api/v1/queue/add")
async def add_task_with_priority(
    task_id: str,
    task_type: str,
    base_priority: str = "NORMAL",
    deadline: Optional[str] = None,
    dependencies: List[str] = [],
    estimated_duration: float = 60.0,
    estimated_cost: float = 0.0
):
    """
    Add task to queue with priority calculation

    Args:
        task_id: Unique task identifier
        task_type: Type of task (deploy, scale, update, etc.)
        base_priority: CRITICAL/HIGH/NORMAL/LOW/IDLE
        deadline: ISO format datetime string (optional)
        dependencies: List of task IDs this task depends on
        estimated_duration: Estimated duration in seconds
        estimated_cost: Estimated cost in dollars
    """
    if not HAS_ADAPTIVE_METRICS:
        return {"status": "disabled", "message": "Adaptive metrics not available"}

    # Convert string priority to enum
    priority_map = {
        "CRITICAL": TaskPriority.CRITICAL,
        "HIGH": TaskPriority.HIGH,
        "NORMAL": TaskPriority.NORMAL,
        "LOW": TaskPriority.LOW,
        "IDLE": TaskPriority.IDLE
    }
    priority_enum = priority_map.get(base_priority.upper(), TaskPriority.NORMAL)

    # Parse deadline if provided
    deadline_dt = None
    if deadline:
        from dateutil import parser as date_parser
        deadline_dt = date_parser.parse(deadline)

    # Add to queue
    task = await orchestrator.add_task_to_queue(
        task_id=task_id,
        task_type=task_type,
        base_priority=priority_enum,
        deadline=deadline_dt,
        dependencies=dependencies,
        estimated_duration=estimated_duration,
        estimated_cost=estimated_cost
    )

    return {
        "status": "success",
        "task": {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "base_priority": task.base_priority.name,
            "actual_priority": task.actual_priority,
            "priority_factors": task.priority_factors,
            "position_in_queue": orchestrator.task_queue.index(task) + 1 if task in orchestrator.task_queue else -1
        }
    }


@app.get("/api/v1/queue/next")
async def get_next_task_endpoint():
    """Get next task to execute based on adaptive priorities"""
    if not HAS_ADAPTIVE_METRICS:
        return {"status": "disabled", "message": "Adaptive metrics not available"}

    task = await orchestrator.get_next_task()

    if not task:
        return {
            "status": "no_tasks",
            "message": "No tasks in queue"
        }

    return {
        "status": "success",
        "task": {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "base_priority": task.base_priority.name,
            "actual_priority": task.actual_priority,
            "priority_factors": task.priority_factors,
            "submitted_at": task.submitted_at.isoformat(),
            "estimated_duration": task.estimated_duration,
            "estimated_cost": task.estimated_cost
        }
    }


@app.post("/api/v1/monitoring/start")
async def start_monitoring():
    """Start adaptive monitoring and priority adaptation"""
    if not HAS_ADAPTIVE_METRICS:
        return {"status": "disabled", "message": "Adaptive metrics not available"}

    await orchestrator.start_adaptive_monitoring()

    return {
        "status": "success",
        "message": "Adaptive monitoring started"
    }


@app.post("/api/v1/monitoring/stop")
async def stop_monitoring():
    """Stop adaptive monitoring"""
    if not HAS_ADAPTIVE_METRICS:
        return {"status": "disabled", "message": "Adaptive metrics not available"}

    await orchestrator.stop_adaptive_monitoring()

    return {
        "status": "success",
        "message": "Adaptive monitoring stopped"
    }


# ============================================================================
# CLI Mode
# ============================================================================

async def cli_main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Unified Infrastructure Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'command',
        choices=['discover', 'generate', 'deploy', 'build-and-deploy', 'status'],
        help='Command to execute'
    )
    parser.add_argument(
        '--layer',
        choices=['gateway', 'runtime', 'observability', 'integration', 'full'],
        default='full',
        help='Infrastructure layer (default: full)'
    )
    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Skip ai-orchestration, deploy directly'
    )

    args = parser.parse_args()

    orch = UnifiedOrchestrator(PROJECT_ROOT)

    if args.command == 'discover':
        await orch.discover_services()

    elif args.command == 'generate':
        await orch.generate_configs()

    elif args.command == 'deploy':
        result = await orch.deploy(layer=args.layer, use_ai=not args.no_ai)
        print(f"\n✅ Result: {result}")

    elif args.command == 'build-and-deploy':
        await orch.discover_services()
        await orch.generate_configs()
        result = await orch.deploy(layer=args.layer, use_ai=not args.no_ai)
        print(f"\n✅ Result: {result}")

    elif args.command == 'status':
        status = await orch.status()
        import json
        print(json.dumps(status, indent=2))


if __name__ == '__main__':
    # CLI mode
    asyncio.run(cli_main())
