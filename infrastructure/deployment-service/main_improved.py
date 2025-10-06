"""
Deployment Service - Improved Version 2.0
=========================================

Production-ready deployment service with:
- EventBus integration
- AI Orchestrator integration
- PostgreSQL persistence
- Prometheus metrics
- Multi-tenancy support
- Graceful shutdown
"""

import os
import sys
import time
import signal
import asyncio
import subprocess
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
from uuid import uuid4

import docker
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

# Local imports
from config import config
from models import (
    DeploymentRequest,
    DeploymentResponse,
    DeploymentRecord,
    DeploymentStatus,
    ServiceStatus,
    ServicesStatusResponse,
    ServiceHealthCheck,
    RestartServiceRequest
)
from events import DeploymentEventPublisher
from metrics import MetricsCollector
from ai_client import AIClient
from db import DeploymentDB

# Logging setup
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
event_publisher: DeploymentEventPublisher = None
ai_client: AIClient = None
deployment_db: DeploymentDB = None
monitoring_task: Optional[asyncio.Task] = None
shutdown_event = asyncio.Event()


class DeploymentEngine:
    """Core deployment engine with AI and EventBus integration"""

    def __init__(self):
        self.docker_client = docker.from_env()
        self.service_order = config.SERVICE_ORDER
        self.critical_services = config.CRITICAL_SERVICES
        self.monitoring_active = False

    async def deploy_platform(
        self,
        request: DeploymentRequest,
        correlation_id: Optional[str] = None
    ) -> DeploymentResponse:
        """
        Execute platform deployment with AI optimization.

        Args:
            request: DeploymentRequest
            correlation_id: Optional correlation ID for tracing

        Returns:
            DeploymentResponse
        """
        start_time = datetime.utcnow()
        deployment_id = str(uuid4())

        # Determine services to deploy
        services_to_deploy = request.services or self.service_order

        # Create deployment record
        deployment_record = DeploymentRecord(
            id=deployment_id,
            tenant_id=request.tenant_id,
            status=DeploymentStatus.IN_PROGRESS,
            strategy=request.strategy,
            requested_services=services_to_deploy,
            initiated_by="api",
            metadata=request.metadata
        )
        deployment_db.create_deployment(deployment_record)

        # Publish deployment started event
        await event_publisher.publish_deployment_started(
            deployment_id=deployment_id,
            tenant_id=request.tenant_id,
            services=services_to_deploy,
            strategy=request.strategy,
            correlation_id=correlation_id
        )

        # Record metrics
        MetricsCollector.record_deployment_started(
            request.tenant_id,
            request.strategy
        )

        deployed_services = []
        failed_services = []
        ai_strategy_used = False

        try:
            # Get AI deployment strategy if requested
            if request.strategy == "ai_optimized":
                ai_strategy_used = await self._apply_ai_strategy(
                    services_to_deploy,
                    request
                )

            # Execute deployment
            for service in services_to_deploy:
                logger.info(f"Deploying {service}...")

                # Publish service start event
                await event_publisher.publish_service_started(
                    service_name=service,
                    deployment_id=deployment_id,
                    tenant_id=request.tenant_id,
                    correlation_id=correlation_id
                )

                if await self.start_service(service):
                    # Wait for health check
                    if await self.wait_for_health(service):
                        deployed_services.append(service)
                        MetricsCollector.record_service_deployed(
                            service, "success", request.tenant_id
                        )
                        logger.info(f"✅ {service} deployed successfully")
                    else:
                        failed_services.append(service)
                        await event_publisher.publish_service_failed(
                            service_name=service,
                            deployment_id=deployment_id,
                            tenant_id=request.tenant_id,
                            error_message="Health check timeout",
                            correlation_id=correlation_id
                        )
                        MetricsCollector.record_service_deployed(
                            service, "failed", request.tenant_id
                        )

                        # Check if critical service failed
                        if service in self.critical_services:
                            logger.error(f"Critical service {service} failed")
                            if request.rollback_on_failure:
                                await self._execute_rollback(
                                    deployment_id,
                                    request.tenant_id,
                                    deployed_services,
                                    correlation_id
                                )
                            break
                else:
                    failed_services.append(service)
                    MetricsCollector.record_service_deployed(
                        service, "failed", request.tenant_id
                    )

            # Determine final status
            if not failed_services:
                status = DeploymentStatus.SUCCESS
            elif deployed_services:
                status = DeploymentStatus.PARTIAL
            else:
                status = DeploymentStatus.FAILED

            # Calculate duration
            end_time = datetime.utcnow()
            duration = int((end_time - start_time).total_seconds())

            # Update deployment record
            deployment_db.update_deployment(deployment_id, {
                "status": status.value,
                "completed_at": end_time,
                "duration_seconds": duration,
                "deployed_services": deployed_services,
                "failed_services": failed_services,
                "ai_strategy_used": ai_strategy_used
            })

            # Publish completion event
            await event_publisher.publish_deployment_completed(
                deployment_id=deployment_id,
                tenant_id=request.tenant_id,
                deployed_services=deployed_services,
                failed_services=failed_services,
                duration_seconds=duration,
                correlation_id=correlation_id
            )

            # Record metrics
            MetricsCollector.record_deployment_completed(
                request.tenant_id,
                request.strategy,
                status.value,
                duration
            )

            # Send results to AI for learning
            if ai_strategy_used:
                await ai_client.analyze_deployment_result(
                    deployment_id,
                    {
                        "status": status.value,
                        "deployed_services": deployed_services,
                        "failed_services": failed_services,
                        "duration": duration
                    }
                )

            return DeploymentResponse(
                deployment_id=deployment_id,
                status=status,
                deployed_services=deployed_services,
                failed_services=failed_services,
                execution_time=duration,
                total_services=len(services_to_deploy)
            )

        except Exception as e:
            logger.error(f"Deployment failed: {e}")

            # Update record
            deployment_db.update_deployment(deployment_id, {
                "status": DeploymentStatus.FAILED.value,
                "error_message": str(e),
                "completed_at": datetime.utcnow()
            })

            # Publish failure event
            await event_publisher.publish_deployment_failed(
                deployment_id=deployment_id,
                tenant_id=request.tenant_id,
                error_message=str(e),
                correlation_id=correlation_id
            )

            MetricsCollector.record_error("deployment_exception", "deployment")
            raise HTTPException(status_code=500, detail=str(e))

    async def _apply_ai_strategy(
        self,
        services: list,
        request: DeploymentRequest
    ) -> bool:
        """
        Get and apply AI deployment strategy.

        Returns:
            True if AI strategy was successfully applied
        """
        try:
            start_time = time.time()

            strategy = await ai_client.get_deployment_strategy(
                services=services,
                context={
                    "tenant_id": request.tenant_id,
                    "metadata": request.metadata
                }
            )

            duration = time.time() - start_time

            if strategy:
                logger.info(f"AI strategy: {strategy.strategy_type}, confidence: {strategy.confidence}")
                self.service_order = strategy.service_order
                MetricsCollector.record_ai_strategy_request(True, duration)
                return True
            else:
                logger.warning("AI strategy not available, using default")
                MetricsCollector.record_ai_strategy_request(False, duration)
                return False

        except Exception as e:
            logger.error(f"Failed to apply AI strategy: {e}")
            return False

    async def _execute_rollback(
        self,
        deployment_id: str,
        tenant_id: str,
        deployed_services: list,
        correlation_id: Optional[str] = None
    ):
        """Execute rollback of deployed services"""
        logger.warning(f"Executing rollback for deployment {deployment_id}")

        await event_publisher.publish_rollback_started(
            deployment_id=deployment_id,
            tenant_id=tenant_id,
            reason="critical_service_failure",
            correlation_id=correlation_id
        )

        rollback_success = True
        for service in reversed(deployed_services):
            try:
                logger.info(f"Rolling back {service}...")
                subprocess.run(
                    ["docker-compose", "stop", service],
                    capture_output=True,
                    timeout=30
                )
            except Exception as e:
                logger.error(f"Failed to rollback {service}: {e}")
                rollback_success = False

        await event_publisher.publish_rollback_completed(
            deployment_id=deployment_id,
            tenant_id=tenant_id,
            success=rollback_success,
            correlation_id=correlation_id
        )

        MetricsCollector.record_rollback(
            reason="critical_service_failure",
            success=rollback_success
        )

        # Update deployment record
        deployment_db.update_deployment(deployment_id, {
            "rollback_executed": True,
            "status": DeploymentStatus.ROLLED_BACK.value
        })

    async def start_service(self, service_name: str) -> bool:
        """Start a single service"""
        try:
            logger.info(f"Starting {service_name}...")
            result = subprocess.run(
                ["docker-compose", "up", service_name, "-d"],
                capture_output=True,
                text=True,
                timeout=config.SERVICE_START_TIMEOUT
            )

            if result.returncode == 0:
                logger.info(f"✅ {service_name} started")
                return True
            else:
                logger.error(f"❌ {service_name} failed: {result.stderr}")
                MetricsCollector.record_error("service_start_failed", service_name)
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"⏱️ {service_name} start timeout")
            MetricsCollector.record_error("service_start_timeout", service_name)
            return False
        except Exception as e:
            logger.error(f"❌ {service_name} start error: {e}")
            MetricsCollector.record_error("service_start_error", service_name)
            return False

    async def wait_for_health(self, service_name: str) -> bool:
        """Wait for service to become healthy"""
        max_attempts = config.HEALTH_CHECK_TIMEOUT // 10

        for attempt in range(max_attempts):
            if self.check_service_health(service_name):
                MetricsCollector.record_service_health(service_name, True)
                return True
            await asyncio.sleep(10)

        MetricsCollector.record_service_health(service_name, False)
        return False

    def check_service_health(self, service_name: str) -> bool:
        """Check if service is healthy"""
        try:
            container = self.docker_client.containers.get(f"iso-22301-{service_name}-1")
            is_healthy = container.status == "running"
            return is_healthy
        except docker.errors.NotFound:
            return False
        except Exception as e:
            logger.error(f"Health check error for {service_name}: {e}")
            return False

    async def restart_service(self, service_name: str) -> bool:
        """Restart a service"""
        logger.warning(f"Restarting {service_name}...")
        try:
            subprocess.run(
                ["docker-compose", "restart", service_name],
                capture_output=True,
                timeout=60
            )
            await asyncio.sleep(10)
            success = self.check_service_health(service_name)

            MetricsCollector.record_service_restart(service_name, success)
            return success

        except Exception as e:
            logger.error(f"Restart failed for {service_name}: {e}")
            MetricsCollector.record_service_restart(service_name, False)
            return False

    async def get_all_services_status(self) -> Dict[str, ServiceHealthCheck]:
        """Get status of all services"""
        status = {}
        for service in self.service_order:
            is_healthy = self.check_service_health(service)
            status[service] = ServiceHealthCheck(
                service_name=service,
                status=ServiceStatus.RUNNING if is_healthy else ServiceStatus.STOPPED,
                healthy=is_healthy,
                metadata={"critical": service in self.critical_services}
            )
            MetricsCollector.record_service_health(service, is_healthy)

        return status

    async def monitor_services(self):
        """Continuous service monitoring with auto-restart"""
        logger.info("Starting service monitoring...")
        self.monitoring_active = True

        while self.monitoring_active and not shutdown_event.is_set():
            try:
                for service in self.service_order:
                    if not self.check_service_health(service):
                        logger.warning(f"🚨 {service} is down - attempting restart")

                        if await self.restart_service(service):
                            logger.info(f"✅ {service} recovered")
                        else:
                            logger.error(f"❌ {service} restart failed")

                            # Alert AI Orchestrator
                            await ai_client.report_service_issue(
                                service_name=service,
                                issue_type="down",
                                details={"timestamp": datetime.utcnow().isoformat()}
                            )

                await asyncio.sleep(config.HEALTH_CHECK_INTERVAL)

            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(config.HEALTH_CHECK_INTERVAL)

        logger.info("Service monitoring stopped")


# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    global event_publisher, ai_client, deployment_db, monitoring_task

    # Startup
    logger.info(f"Starting {config.SERVICE_NAME} v{config.SERVICE_VERSION}")

    try:
        # Initialize components
        event_publisher = DeploymentEventPublisher()
        ai_client = AIClient()
        deployment_db = DeploymentDB()

        # Check AI availability
        ai_available = await ai_client.health_check()
        logger.info(f"AI Orchestrator available: {ai_available}")

        # Start monitoring task
        monitoring_task = asyncio.create_task(deployment_engine.monitor_services())

        logger.info("Deployment service ready")

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down deployment service...")
    shutdown_event.set()
    deployment_engine.monitoring_active = False

    if monitoring_task:
        monitoring_task.cancel()
        try:
            await asyncio.wait_for(monitoring_task, timeout=config.SHUTDOWN_TIMEOUT)
        except asyncio.TimeoutError:
            logger.warning("Monitoring task shutdown timeout")
        except asyncio.CancelledError:
            pass

    logger.info("Shutdown complete")


# FastAPI application
app = FastAPI(
    title="Deployment Service",
    description="Production-ready deployment orchestration with AI integration",
    version=config.SERVICE_VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics endpoint
if config.METRICS_ENABLED:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

# Deployment engine instance
deployment_engine = DeploymentEngine()


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return {
        "service": config.SERVICE_NAME,
        "version": config.SERVICE_VERSION,
        "status": "ready",
        "monitoring": deployment_engine.monitoring_active,
        "features": [
            "EventBus integration",
            "AI Orchestrator integration",
            "PostgreSQL persistence",
            "Prometheus metrics",
            "Multi-tenancy support",
            "Graceful shutdown"
        ]
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "ai_available": await ai_client.health_check()
    }


@app.post("/deploy", response_model=DeploymentResponse)
async def deploy_platform(request: DeploymentRequest):
    """Execute platform deployment"""
    try:
        result = await deployment_engine.deploy_platform(request)
        return result
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status", response_model=ServicesStatusResponse)
async def get_services_status():
    """Get status of all services"""
    services = await deployment_engine.get_all_services_status()

    healthy_count = sum(1 for s in services.values() if s.healthy)

    return ServicesStatusResponse(
        services=services,
        total_services=len(services),
        healthy_services=healthy_count,
        unhealthy_services=len(services) - healthy_count
    )


@app.post("/restart/{service_name}")
async def restart_service(service_name: str, tenant_id: str = "system"):
    """Restart specific service"""
    if service_name not in deployment_engine.service_order:
        raise HTTPException(status_code=404, detail="Service not found")

    success = await deployment_engine.restart_service(service_name)

    return {
        "service": service_name,
        "restarted": success,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/deployments/recent")
async def get_recent_deployments(tenant_id: Optional[str] = None, limit: int = 10):
    """Get recent deployment history"""
    deployments = deployment_db.get_recent_deployments(tenant_id, limit)

    return {
        "deployments": [d.dict() for d in deployments],
        "count": len(deployments)
    }


@app.get("/deployments/{deployment_id}")
async def get_deployment(deployment_id: str):
    """Get deployment by ID"""
    deployment = deployment_db.get_deployment(deployment_id)

    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    return deployment.dict()


@app.get("/deployments/stats")
async def get_deployment_stats(tenant_id: Optional[str] = None):
    """Get deployment statistics"""
    stats = deployment_db.get_deployment_stats(tenant_id)
    return stats


@app.post("/monitoring/start")
async def start_monitoring():
    """Start service monitoring"""
    if not deployment_engine.monitoring_active:
        asyncio.create_task(deployment_engine.monitor_services())
    return {"monitoring": "started"}


@app.post("/monitoring/stop")
async def stop_monitoring():
    """Stop service monitoring"""
    deployment_engine.monitoring_active = False
    return {"monitoring": "stopped"}


# Signal handlers for graceful shutdown
def handle_shutdown(sig, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {sig}, initiating graceful shutdown...")
    shutdown_event.set()
    sys.exit(0)


signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting {config.SERVICE_NAME} on {config.HOST}:{config.PORT}")

    uvicorn.run(
        app,
        host=config.HOST,
        port=config.PORT,
        log_level=config.LOG_LEVEL.lower()
    )
