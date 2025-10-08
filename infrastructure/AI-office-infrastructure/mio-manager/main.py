#!/usr/bin/env python3
"""
AI MIO Manager - Intelligent Monitoring & Observability Manager
Port: 8046

Управляющий центр платформы:
- Запускает Automation Toolkit для анализа
- Управляет API Gateway
- Формирует задачи для исправлений
- Отчитывается в систему мониторинга
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager
import logging

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from config import settings
from integrations.automation_toolkit import AutomationToolkitManager
from integrations.orchestrator_client import OrchestratorClient
from integrations.gateway_manager import GatewayManager
from integrations.workflow_intelligence_client import WorkflowIntelligenceClient
from integrations.predictive_client import PredictiveClient
from integrations.workflow_optimizer_client import WorkflowOptimizerClient
from integrations.coordination_center_client import CoordinationCenterClient
from integrations.compliance_monitoring_client import ComplianceMonitoringClient
from integrations.eventbus_client import EventBusClient, DefaultEventHandlers
from integrations.ai_event_manager_client import AIEventManagerClient
from integrations.devops_agent_client import DevOpsAgentClient
from scheduler.automation_jobs import start_scheduler, stop_scheduler
from scheduler.smart_scheduler import SmartScheduler
from api import routes
from database import init_database

# AI Intelligence components
from intelligence.ai_coordinator import AICoordinator
from intelligence.decision_engine import DecisionEngine
from intelligence.learning_tracker import LearningTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global instances
toolkit_manager = None
orchestrator_client = None
gateway_manager = None

# Integration clients (v2.0)
brain_client = None
predictive_client = None
optimizer_client = None
coordinator_client = None
compliance_client = None
eventbus_client = None
ai_event_manager_client = None
smart_scheduler = None

# AI Intelligence instances
ai_coordinator = None
decision_engine = None
learning_tracker = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    global toolkit_manager, orchestrator_client, gateway_manager
    global brain_client, predictive_client, optimizer_client, coordinator_client, compliance_client, eventbus_client, ai_event_manager_client, devops_agent_client, smart_scheduler
    global ai_coordinator, decision_engine, learning_tracker

    logger.info("🚀 AI MIO Manager v2.0 starting...")
    logger.info("   🧠 Enhanced with AI Intelligence Layer")
    logger.info("   📊 Battle-Ready Monitoring & Automation")

    # Initialize database
    init_database()
    logger.info("   ✅ Database initialized")

    # Initialize AI Intelligence Layer
    try:
        ai_coordinator = AICoordinator()
        decision_engine = DecisionEngine()
        learning_tracker = LearningTracker()
        logger.info("   ✅ AI Intelligence Layer initialized")

        if ai_coordinator.enabled:
            logger.info("   🧠 AI-powered decision making enabled")
        else:
            logger.warning("   ⚠️  AI Foundation not available - using fallback mode")
    except Exception as e:
        logger.error(f"   ❌ AI Intelligence initialization failed: {e}")
        logger.warning("   ⚠️  Running without AI Intelligence")

    # Initialize Automation Toolkit Manager
    toolkit_manager = AutomationToolkitManager()
    logger.info("   ✅ Automation Toolkit Manager initialized")

    # Initialize Orchestrator Client
    orchestrator_client = OrchestratorClient(
        orchestrator_url=settings.ORCHESTRATOR_URL
    )
    logger.info("   ✅ Orchestrator Client initialized")

    # Initialize Gateway Manager
    gateway_manager = GatewayManager(
        gateway_url=settings.GATEWAY_URL
    )
    logger.info("   ✅ Gateway Manager initialized")

    # Initialize v2.0 Integration Clients
    logger.info("   🔌 Initializing v2.0 integration clients...")

    brain_client = WorkflowIntelligenceClient(
        workflow_intelligence_url=settings.WORKFLOW_INTELLIGENCE_URL
    )
    logger.info("   ✅ Brain Client (workflow_intelligence) initialized")

    predictive_client = PredictiveClient(
        base_url=settings.PREDICTIVE_URL
    )
    logger.info("   ✅ Predictive Client initialized")

    optimizer_client = WorkflowOptimizerClient(
        optimizer_url=settings.OPTIMIZER_URL
    )
    logger.info("   ✅ Optimizer Client initialized")

    coordinator_client = CoordinationCenterClient(
        coordination_url=settings.COORDINATION_CENTER_URL
    )
    logger.info("   ✅ Coordination Center Client initialized")

    # Initialize Compliance Monitoring Client
    compliance_client = ComplianceMonitoringClient(
        base_url=settings.COMPLIANCE_MONITORING_URL
    )
    logger.info("   ✅ Compliance Monitoring Client initialized")

    # Initialize AI Event Manager Client
    ai_event_manager_client = AIEventManagerClient(
        base_url=settings.AI_EVENT_MANAGER_URL
    )
    logger.info("   ✅ AI Event Manager Client initialized")

    # Initialize DevOps Agent Client
    devops_agent_client = DevOpsAgentClient(
        base_url=settings.DEVOPS_AGENT_URL
    )
    logger.info("   ✅ DevOps Agent Client initialized")

    # Initialize EventBus Client (v2.0 - критично!)
    logger.info("   📡 Initializing EventBus Client...")
    eventbus_client = EventBusClient(
        backend='redis',  # or 'memory' for testing
        redis_url=settings.REDIS_URL if hasattr(settings, 'REDIS_URL') else 'redis://localhost:6379'
    )
    await eventbus_client.initialize()
    logger.info("   ✅ EventBus Client initialized")

    # Setup Event Handlers
    from reaction.escalation_manager import EscalationManager
    from reaction.action_executor import ActionExecutor

    escalation_manager = EscalationManager(brain_client)
    action_executor = ActionExecutor()

    event_handlers = DefaultEventHandlers(
        escalation_manager=escalation_manager,
        action_executor=action_executor
    )

    # Subscribe to events from other services
    await eventbus_client.subscribe_to_problems(event_handlers.handle_problem_detected)
    await eventbus_client.subscribe_to_tasks(event_handlers.handle_task_completed)
    await eventbus_client.subscribe_to_directives(event_handlers.handle_directive_issued)
    await eventbus_client.subscribe_to_deployments(event_handlers.handle_service_deployed)
    await eventbus_client.subscribe_to_alerts(event_handlers.handle_alert_triggered)

    # Start EventBus consumer
    await eventbus_client.start_consumer()
    logger.info("   ✅ EventBus subscriptions active")

    # Initialize SmartScheduler (v2.0 - критично!)
    logger.info("   🗓️  Initializing SmartScheduler...")
    smart_scheduler = SmartScheduler(
        workflow_intelligence_client=brain_client,
        predictive_client=predictive_client,
        optimizer_client=optimizer_client,
        coordination_center_client=coordinator_client,
        compliance_monitoring_client=compliance_client,
        automation_toolkit_manager=toolkit_manager,
        ai_event_manager_client=ai_event_manager_client,
        devops_agent_client=devops_agent_client
    )
    await smart_scheduler.start()
    logger.info("   ✅ SmartScheduler started with all cycles")

    # Start legacy automation scheduler (for backward compatibility)
    start_scheduler(
        toolkit_manager=toolkit_manager,
        orchestrator_client=orchestrator_client,
        gateway_manager=gateway_manager
    )
    logger.info("   ✅ Legacy automation scheduler started")

    # Initial service discovery
    discovery_result = await toolkit_manager.discover_services()
    logger.info(f"   📊 Discovered {discovery_result['total_services']} services")
    logger.info(f"   📈 Coverage: {discovery_result['coverage']['percentage']:.1f}%")

    logger.info("✅ AI MIO Manager v2.0 ready on port 8046")
    logger.info("   🧠 Intelligent, Self-Managing, Conversational")
    logger.info("   👀 Platform Eyes with Deep Analysis Cycles")

    yield

    # Shutdown
    logger.info("👋 AI MIO Manager v2.0 shutting down...")

    # Stop SmartScheduler
    if smart_scheduler:
        await smart_scheduler.stop()
        logger.info("   ✅ SmartScheduler stopped")

    # Stop legacy scheduler
    stop_scheduler()
    logger.info("   ✅ Legacy scheduler stopped")

    # Close integration clients
    if eventbus_client:
        await eventbus_client.close()
    if brain_client:
        await brain_client.close()
    if predictive_client:
        await predictive_client.close()
    if optimizer_client:
        await optimizer_client.close()
    if coordinator_client:
        await coordinator_client.close()
    if compliance_client:
        await compliance_client.close()
    if ai_event_manager_client:
        await ai_event_manager_client.close()
    logger.info("   ✅ Integration clients closed")

    # Export learning data
    if learning_tracker:
        export_path = Path(__file__).parent / 'learning_data' / 'export.json'
        learning_tracker.export_learning_data(str(export_path))
        logger.info("   ✅ Learning data exported")


# FastAPI app
app = FastAPI(
    title="AI MIO Manager",
    description="Intelligent Monitoring & Observability Manager - Управляющий центр платформы",
    version="1.0.0",
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

# Include routes
app.include_router(routes.router)

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "mio-manager",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8046,
        reload=True
    )
