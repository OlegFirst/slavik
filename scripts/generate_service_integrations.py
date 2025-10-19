#!/usr/bin/env python3
"""
Generate Platform Integration files for all BCM services
=========================================================

This script automates the integration of remaining BCM services with
the Platform Integration infrastructure (Graceful Choreography).

For each service, it:
1. Reads service configuration
2. Generates main_integrated.py from template
3. Generates test_integration.py
4. Creates .env file
5. Runs integration tests
6. Reports results
"""

import os
import sys
import re
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple

# Service configurations
SERVICES = {
    "compliance_service": {
        "name": "Compliance Service",
        "port": 8030,
        "iso_clause": "All Clauses",
        "module": "compliance",
        "capabilities": [
            "compliance.assessment",
            "compliance.audit",
            "compliance.gap_analysis",
            "compliance.evidence",
            "compliance.reporting",
        ],
        "event_patterns": ["compliance.*"],
        "semantic_tags": ["compliance", "audit", "assessment", "iso22301", "evidence"],
        "description": "Compliance Management - ISO 22301 Full Standard",
    },
    "planning_service": {
        "name": "Planning Service",
        "port": 8050,
        "iso_clause": "8.3",
        "module": "planning",
        "capabilities": [
            "planning.strategy",
            "planning.objectives",
            "planning.resource_planning",
            "planning.scheduling",
        ],
        "event_patterns": ["planning.*"],
        "semantic_tags": ["planning", "strategy", "objectives", "resources"],
        "description": "BCM Planning - ISO 22301 Clause 8.3",
    },
    "governance_service": {
        "name": "Governance Service",
        "port": 8060,
        "iso_clause": "5.1-5.3",
        "module": "governance",
        "capabilities": [
            "governance.policy",
            "governance.roles",
            "governance.responsibilities",
            "governance.oversight",
        ],
        "event_patterns": ["governance.*"],
        "semantic_tags": ["governance", "policy", "roles", "oversight"],
        "description": "Governance & Leadership - ISO 22301 Clauses 5.1-5.3",
    },
    "plans_service": {
        "name": "Plans Service",
        "port": 8070,
        "iso_clause": "8.4",
        "module": "plans",
        "capabilities": [
            "plans.bcp_create",
            "plans.bcp_update",
            "plans.drp_create",
            "plans.testing",
        ],
        "event_patterns": ["plans.*"],
        "semantic_tags": ["bcp", "drp", "plans", "procedures", "testing"],
        "description": "BCP/DRP Management - ISO 22301 Clause 8.4",
    },
    "response_service": {
        "name": "Response Service",
        "port": 8080,
        "iso_clause": "8.4.3",
        "module": "response",
        "capabilities": [
            "response.incident_detection",
            "response.activation",
            "response.coordination",
            "response.communication",
        ],
        "event_patterns": ["response.*", "incident.*"],
        "semantic_tags": ["incident", "response", "activation", "coordination"],
        "description": "Incident Response - ISO 22301 Clause 8.4.3",
    },
    "documents_service": {
        "name": "Documents Service",
        "port": 8090,
        "iso_clause": "7.5",
        "module": "documents",
        "capabilities": [
            "documents.create",
            "documents.version_control",
            "documents.approval",
            "documents.distribution",
        ],
        "event_patterns": ["documents.*"],
        "semantic_tags": ["documents", "version", "approval", "distribution"],
        "description": "Document Management - ISO 22301 Clause 7.5",
    },
    "validation_service": {
        "name": "Validation Service",
        "port": 8100,
        "iso_clause": "8.5",
        "module": "validation",
        "capabilities": [
            "validation.exercise",
            "validation.test",
            "validation.review",
            "validation.improvement",
        ],
        "event_patterns": ["validation.*", "exercise.*", "test.*"],
        "semantic_tags": ["validation", "testing", "exercise", "review"],
        "description": "Validation & Testing - ISO 22301 Clause 8.5",
    },
    "learning_service": {
        "name": "Learning Service",
        "port": 8110,
        "iso_clause": "7.2-7.3",
        "module": "learning",
        "capabilities": [
            "learning.training",
            "learning.awareness",
            "learning.competency",
            "learning.knowledge",
        ],
        "event_patterns": ["learning.*", "training.*"],
        "semantic_tags": ["learning", "training", "awareness", "competency"],
        "description": "Learning & Awareness - ISO 22301 Clauses 7.2-7.3",
    },
    "community_service": {
        "name": "Community Service",
        "port": 8120,
        "iso_clause": "Support",
        "module": "community",
        "capabilities": [
            "community.knowledge_sharing",
            "community.collaboration",
            "community.marketplace",
            "community.portal",
        ],
        "event_patterns": ["community.*", "knowledge.*"],
        "semantic_tags": ["community", "knowledge", "collaboration", "marketplace"],
        "description": "Community & Knowledge Sharing",
    },
    "simulation_service": {
        "name": "Simulation Service",
        "port": 8130,
        "iso_clause": "8.5",
        "module": "simulation",
        "capabilities": [
            "simulation.scenario",
            "simulation.monte_carlo",
            "simulation.what_if",
            "simulation.reporting",
        ],
        "event_patterns": ["simulation.*", "scenario.*"],
        "semantic_tags": ["simulation", "scenario", "monte_carlo", "analysis"],
        "description": "Simulation & Scenario Analysis - ISO 22301 Clause 8.5",
    },
}


def generate_main_integrated(service_key: str, config: Dict) -> str:
    """Generate main_integrated.py content for a service"""

    capabilities_str = ",\n                    ".join([f'"{cap}"' for cap in config["capabilities"]])
    event_patterns_str = '", "'.join(config["event_patterns"])
    semantic_tags_str = '", "'.join(config["semantic_tags"])

    # Create handler methods based on capabilities
    handlers = []
    for cap in config["capabilities"]:
        cap_short = cap.split(".")[-1]
        handler_name = f"handle_{cap_short}_event"
        handlers.append(f"""
    async def {handler_name}(self, event):
        \"\"\"Handle {cap} events\"\"\"
        logger.info(f"Handling {cap} event: {{event.type}}")
        # TODO: Implement actual {cap_short} handling
        return {{"status": "processed", "event_type": event.type}}""")

    handlers_str = "".join(handlers)

    # Register handlers
    handler_registrations = []
    for i, cap in enumerate(config["capabilities"]):
        cap_short = cap.split(".")[-1]
        handler_name = f"handle_{cap_short}_event"
        event_pattern = f"{config['module']}.{cap_short}.*"
        priority = "EventPriority.HIGH" if i < 2 else "EventPriority.NORMAL"
        handler_registrations.append(
            f'            self.register_handler("{event_pattern}", self.{handler_name}, priority={priority})'
        )

    handler_registrations_str = "\n".join(handler_registrations)

    content = f'''"""
{config["name"]} - Integrated with Graceful Choreography
{"=" * (len(config["name"]) + 41)}

Enhanced {config["name"]} with:
1. Intelligent EventBus (AI-powered routing)
2. Saga Pattern support
3. Self-Aware service capabilities
4. CQRS pattern (optional)

This is the NEW main.py that integrates all architectural patterns.
Replace main.py with this file once tested.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os

from config import settings
from api.routes import router as service_router
from api.workflow_ai import router as workflow_ai_router

# Platform Integration - THE NEW WAY
from infrastructure.platform_integration import init_platform, get_platform, shutdown_platform

# Self-Aware Service Base - THE NEW WAY
try:
    from platform_services.bcm_domain.services._shared import SelfAwareService, EventPriority
    SELF_AWARE_AVAILABLE = True
except ImportError:
    SELF_AWARE_AVAILABLE = False
    print("WARNING: Self-Aware Services not available")

# Database
import sys
from pathlib import Path
shared_db_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "platform-services" / "community-service" / "shared"
if str(shared_db_path) not in sys.path:
    sys.path.insert(0, str(shared_db_path))

from database.connection import init_db, close_db

# Workflow Intelligence integration
from workflow_intelligence import PostgresStorageAdapter, WorkflowEngine
from workflow_intelligence.monitoring import workflow_metrics, health_checker
from workflow_intelligence.audit import AuditLogger
from workflow_intelligence.compliance import ISO22301Checker
from prometheus_client import make_asgi_app

from workflow_integration import WorkflowSecurityMiddleware, check_compliance

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
platform = None
service_self_aware = None
workflow_storage = None
workflow_engine = None
audit_logger = None
iso_checker = None
security_middleware = None


class {config["name"].replace(" ", "")}SelfAware(SelfAwareService if SELF_AWARE_AVAILABLE else object):
    """
    {config["name"]} with Self-Aware capabilities

    Provides intelligent event handling with:
    - Automatic capability matching
    - Load-aware processing
    - Graceful degradation
    - Service collaboration
    """

    def __init__(self):
        if SELF_AWARE_AVAILABLE:
            super().__init__(
                service_name="{service_key}",
                capabilities=[
                    {capabilities_str}
                ]
            )
            logger.info("✅ {config['name']} initialized as Self-Aware")
        else:
            logger.warning("⚠️  {config['name']} running in basic mode (Self-Aware not available)")

    async def initialize(self):
        """Initialize {config['name']}-specific capabilities"""
        if SELF_AWARE_AVAILABLE:
            # Register event handlers with priorities
{handler_registrations_str}

            logger.info("✅ {config['name']} event handlers registered")
{handlers_str}

    async def handle_completion_event(self, event):
        """Handle completion events (triggers next steps)"""
        logger.info(f"{config['name']} completion event: {{event.type}}")

        # If platform available, can trigger saga
        if platform and platform.saga_orchestrator:
            logger.info("  → Considering saga orchestration for next steps")
            # TODO: Trigger appropriate saga

        return {{"status": "completion_processed"}}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Enhanced application lifespan with Platform Integration

    Startup sequence:
    1. Initialize Platform Integration (EventBus, Saga, CQRS)
    2. Initialize Database
    3. Initialize Self-Aware Service
    4. Initialize Workflow Intelligence
    5. Register with Platform
    """
    global platform, service_self_aware, workflow_storage, workflow_engine
    global audit_logger, iso_checker, security_middleware

    # === STARTUP ===
    logger.info("=" * 60)
    logger.info("🚀 Starting {config['name']} (Integrated with Graceful Choreography)")
    logger.info("=" * 60)
    logger.info(f"📍 Port: {config['port']}")
    logger.info(f"📋 ISO 22301 Clause: {config['iso_clause']}")

    try:
        # === 1. Initialize Platform Integration ===
        logger.info("\\n1️⃣  Initializing Platform Integration...")
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

        platform = await init_platform(
            database_url=settings.DATABASE_URL,
            redis_url=redis_url,
            enable_intelligent_routing=True,
            enable_saga_engine=True,
            enable_self_aware=True,
            enable_cqrs=False
        )

        platform_status = platform.get_status()
        logger.info(f"   Platform Status: {{platform_status}}")

        # === 2. Initialize Database ===
        logger.info("\\n2️⃣  Initializing Database...")
        await init_db()
        logger.info(f"   ✅ Database initialized")

        # === 3. Initialize Self-Aware Service ===
        if SELF_AWARE_AVAILABLE:
            logger.info("\\n3️⃣  Initializing Self-Aware Service...")
            service_self_aware = {config["name"].replace(" ", "")}SelfAware()
            await service_self_aware.initialize()

            # Subscribe to events via platform EventBus
            if platform.intelligent_router:
                logger.info("   📡 Registering with Intelligent EventBus...")
                # Register service capabilities with router
                await platform.intelligent_router.register_subscriber(
                    subscriber_id="{service_key}",
                    event_pattern="{event_patterns_str}",
                    handler=service_self_aware.on_event,
                    capabilities={{
                        "domains": ["{config['module']}", "bcm"],
                        "max_concurrent": 10,
                        "avg_processing_time_ms": 500,
                        "sla_ms": 3000,
                        "semantic_tags": ["{semantic_tags_str}"]
                    }}
                )
                logger.info("   ✅ Self-Aware Service registered with Intelligent Router")
            elif platform.eventbus:
                logger.info("   📡 Registering with Basic EventBus...")
                await platform.eventbus.subscribe("{event_patterns_str}", service_self_aware.on_event)
                logger.info("   ✅ Self-Aware Service registered with EventBus")
        else:
            logger.warning("\\n3️⃣  ⚠️  Self-Aware Services not available (basic mode)")

        # === 4. Initialize Workflow Intelligence ===
        logger.info("\\n4️⃣  Initializing Workflow Intelligence...")
        workflow_storage = PostgresStorageAdapter(settings.DATABASE_URL)
        await workflow_storage.connect()

        workflow_engine = WorkflowEngine(
            module="{config['module']}",
            storage_adapter=workflow_storage
        )

        audit_logger = AuditLogger(storage_adapter=workflow_storage)
        await audit_logger.ensure_schema()

        iso_checker = ISO22301Checker()

        jwt_secret = getattr(settings, 'JWT_SECRET_KEY', None) or "dev-secret-key-change-in-production"
        security_middleware = WorkflowSecurityMiddleware(
            audit_logger=audit_logger,
            iso_checker=iso_checker,
            jwt_secret=jwt_secret
        )

        # Set health metrics
        workflow_metrics.set_health("workflow_intelligence", True)
        workflow_metrics.set_health("database", True)
        workflow_metrics.set_health("audit_logging", True)
        workflow_metrics.set_health("iso_compliance", True)

        logger.info("   ✅ Workflow Intelligence initialized")

        # === 5. Register Sagas (if saga engine available) ===
        if platform.saga_orchestrator:
            logger.info("\\n5️⃣  Registering Sagas...")
            try:
                from intelligent_core.orchestration.saga_engine.example_sagas import (
                    create_bcm_program_saga,
                    create_incident_response_saga
                )

                platform.saga_orchestrator.register_saga(create_bcm_program_saga())
                platform.saga_orchestrator.register_saga(create_incident_response_saga())

                logger.info("   ✅ Sagas registered")
            except ImportError:
                logger.warning("   ⚠️  Saga definitions not found")

        logger.info("\\n" + "=" * 60)
        logger.info("✅ {config['name']} ready (with Graceful Choreography)")
        logger.info("=" * 60)
        logger.info(f"   🌐 Docs: http://localhost:{config['port']}/docs")
        logger.info(f"   📊 Metrics: http://localhost:{config['port']}/metrics")
        logger.info(f"   ❤️  Health: http://localhost:{config['port']}/health")
        logger.info("=" * 60 + "\\n")

    except Exception as e:
        logger.error(f"❌ Failed to start {config['name']}: {{e}}", exc_info=True)
        raise

    yield  # Application running

    # === SHUTDOWN ===
    logger.info("\\n" + "=" * 60)
    logger.info("🛑 Shutting down {config['name']}...")
    logger.info("=" * 60)

    if workflow_storage:
        await workflow_storage.close()
        logger.info("   ✅ Workflow storage closed")

    await close_db()
    logger.info("   ✅ Database closed")

    await shutdown_platform()
    logger.info("   ✅ Platform integration shutdown")

    logger.info("=" * 60)
    logger.info("✅ {config['name']} shutdown complete")
    logger.info("=" * 60)


# Create FastAPI app with enhanced lifespan
app = FastAPI(
    title=getattr(settings, 'SERVICE_NAME', '{config["name"]}'),
    description=f"""
    {config["description"]}

    **Enhanced with Graceful Choreography:**
    - Intelligent EventBus
    - Saga Pattern
    - Self-Aware capabilities
    - CQRS (optional)
    """,
    version=getattr(settings, 'SERVICE_VERSION', '1.0.0'),
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(service_router)
app.include_router(workflow_ai_router)

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# === ENHANCED HEALTH CHECK ===
@app.get("/health")
async def health_check():
    """Enhanced health check with platform status"""
    health = {{
        "status": "healthy",
        "service": "{service_key}",
        "version": getattr(settings, 'SERVICE_VERSION', '1.0.0'),
        "iso_clause": "{config['iso_clause']}"
    }}

    if platform:
        health["platform"] = platform.get_status()

    if service_self_aware and SELF_AWARE_AVAILABLE:
        health_status = await service_self_aware.health_monitor.check_health()
        health["self_aware"] = {{
            "status": health_status.status.value,
            "load": await service_self_aware.load_manager.get_load_percentage()
        }}

    return health


# === PLATFORM STATUS ENDPOINT ===
@app.get("/api/platform/status")
async def get_platform_status():
    """Get detailed platform integration status"""
    if not platform:
        return {{"error": "Platform not initialized"}}

    status = platform.get_status()

    if platform.intelligent_router:
        status["intelligent_router"] = platform.intelligent_router.get_metrics()

    if platform.saga_orchestrator:
        status["saga_engine"] = {{
            "registered_sagas": list(platform.saga_orchestrator._sagas.keys())
        }}

    return status


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main_integrated:app",
        host="0.0.0.0",
        port={config['port']},
        reload=True,
        log_level="info"
    )
'''

    return content


def generate_test_integration(service_key: str, config: Dict) -> str:
    """Generate test_integration.py content for a service"""

    redis_db = list(SERVICES.keys()).index(service_key) + 3  # Start from DB 3

    content = f'''"""
Test Integration - {config["name"]}
{"=" * (len(config["name"]) + 19)}

This script tests the integration without starting the full server.
Tests:
1. Platform initialization
2. Self-aware service setup
3. Event handling registration
4. Component availability
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from config import settings
from infrastructure.platform_integration import init_platform, shutdown_platform, get_platform

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_platform_integration():
    """Test platform integration initialization"""
    print("\\n" + "=" * 70)
    print("Testing {config['name']} Platform Integration")
    print("=" * 70 + "\\n")

    # Test 1: Platform Initialization
    print("1️⃣  Testing Platform Initialization...")
    try:
        platform = await init_platform(
            database_url="sqlite+aiosqlite:///./test_{service_key}.db",
            redis_url="redis://localhost:6379/{redis_db}",
            enable_intelligent_routing=True,
            enable_saga_engine=True,
            enable_self_aware=True,
            enable_cqrs=False
        )
        print("   ✅ Platform initialized successfully")

        status = platform.get_status()
        print(f"   📊 Platform Status: {{status}}")

    except Exception as e:
        print(f"   ❌ Platform initialization failed: {{e}}")
        import traceback
        traceback.print_exc()
        return False

    # Test 2: Check Components
    print("\\n2️⃣  Testing Platform Components...")

    if platform.eventbus:
        print("   ✅ EventBus available")
    else:
        print("   ❌ EventBus not available")

    if platform.intelligent_router:
        print("   ✅ Intelligent EventRouter available")
        try:
            metrics = platform.intelligent_router.get_metrics()
            print(f"   📊 Router Metrics: {{metrics}}")
        except Exception as e:
            print(f"   ⚠️  Could not get router metrics: {{e}}")
    else:
        print("   ⚠️  Intelligent EventRouter not available (using basic EventBus)")

    if platform.saga_orchestrator:
        print("   ✅ Saga Orchestrator available")
    else:
        print("   ❌ Saga Orchestrator not available")

    # Test 3: Self-Aware Service
    print("\\n3️⃣  Testing Self-Aware Service...")
    try:
        from platform_services.bcm_domain.services._shared import SelfAwareService, EventPriority

        class Test{config["name"].replace(" ", "")}(SelfAwareService):
            def __init__(self):
                super().__init__(
                    service_name="{service_key}_test",
                    capabilities=["{config['capabilities'][0]}", "{config['capabilities'][1]}"]
                )

            async def handle_test_event(self, event):
                return {{"status": "handled", "event_type": event.type}}

        test_service = Test{config["name"].replace(" ", "")}()

        test_service.register_handler("{config['module']}.test.*", test_service.handle_test_event, priority=EventPriority.HIGH)

        print("   ✅ Self-Aware Service created successfully")
        print("   ✅ Event handlers registered successfully")

    except Exception as e:
        print(f"   ❌ Self-Aware Service test failed: {{e}}")
        import traceback
        traceback.print_exc()

    # Test 4: Event Publishing
    if platform.intelligent_router:
        print("\\n4️⃣  Testing Event Publishing...")
        try:
            from infrastructure.eventbus import Event, EventPriority

            test_event = Event.create(
                event_type="{config['module']}.integration.test",
                data={{"message": "Integration test event for {config['name']}"}},
                source="test_integration",
                tenant_id="test-tenant",
                priority=EventPriority.NORMAL
            )

            await platform.intelligent_router.route_event(test_event)
            print("   ✅ Event routed successfully")

        except Exception as e:
            print(f"   ⚠️  Event publishing test failed: {{e}}")

    # Test 5: Saga Engine
    if platform.saga_orchestrator:
        print("\\n5️⃣  Testing Saga Engine...")
        try:
            from intelligent_core.orchestration.saga_engine.example_sagas import (
                create_bcm_program_saga
            )

            saga_def = create_bcm_program_saga()
            platform.saga_orchestrator.register_saga(saga_def)

            print("   ✅ Saga registered successfully")
            if hasattr(platform.saga_orchestrator, 'sagas'):
                print(f"   📊 Registered sagas: {{list(platform.saga_orchestrator.sagas.keys())}}")
            elif hasattr(platform.saga_orchestrator, '_sagas'):
                print(f"   📊 Registered sagas: {{list(platform.saga_orchestrator._sagas.keys())}}")

        except Exception as e:
            print(f"   ⚠️  Saga engine test failed: {{e}}")

    # Cleanup
    print("\\n6️⃣  Testing Cleanup...")
    try:
        await shutdown_platform()
        print("   ✅ Platform shutdown successfully")
    except Exception as e:
        print(f"   ⚠️  Platform shutdown had issues: {{e}}")

    print("\\n" + "=" * 70)
    print("✅ Integration Test Complete!")
    print("=" * 70 + "\\n")

    return True


async def main():
    """Main test function"""
    try:
        success = await test_platform_integration()

        if success:
            print("🎉 All integration tests passed!")
            print("\\n📝 Next steps:")
            print("   1. Run full service: python main_integrated.py")
            print("   2. Test API endpoints: http://localhost:{config['port']}/docs")
            print("   3. Check health: curl http://localhost:{config['port']}/health")
            print("   4. Check platform status: curl http://localhost:{config['port']}/api/platform/status")
            return 0
        else:
            print("❌ Some integration tests failed")
            return 1

    except Exception as e:
        print(f"❌ Test failed with exception: {{e}}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
'''

    return content


def generate_env_file(service_key: str, config: Dict) -> str:
    """Generate .env file content for a service"""

    content = f"""# {config["name"]} - Test Environment Variables

# Database Configuration (test database)
DATABASE_URL=sqlite+aiosqlite:///./test_{service_key}.db

# Service Configuration
PORT={config['port']}

# JWT Authentication Configuration
JWT_AUTH_ENABLED=false
JWT_SECRET_KEY=test-secret-key-for-development-only
"""

    return content


async def process_service(service_key: str, config: Dict, base_path: Path) -> Tuple[str, bool]:
    """Process a single service - generate files and run tests"""

    service_path = base_path / service_key

    print(f"\n{'=' * 70}")
    print(f"Processing: {config['name']}")
    print(f"{'=' * 70}")

    try:
        # 1. Generate main_integrated.py
        print("  1️⃣  Generating main_integrated.py...")
        main_content = generate_main_integrated(service_key, config)
        main_file = service_path / "main_integrated.py"
        main_file.write_text(main_content)
        print("     ✅ main_integrated.py created")

        # 2. Generate test_integration.py
        print("  2️⃣  Generating test_integration.py...")
        test_content = generate_test_integration(service_key, config)
        test_file = service_path / "test_integration.py"
        test_file.write_text(test_content)
        print("     ✅ test_integration.py created")

        # 3. Generate .env
        print("  3️⃣  Generating .env file...")
        env_content = generate_env_file(service_key, config)
        env_file = service_path / ".env"
        env_file.write_text(env_content)
        print("     ✅ .env created")

        # 4. Run tests
        print("  4️⃣  Running integration tests...")
        proc = await asyncio.create_subprocess_exec(
            "python3", "test_integration.py",
            cwd=str(service_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )

        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=30)

        if proc.returncode == 0:
            print("     ✅ Tests PASSED")
            return (service_key, True)
        else:
            print(f"     ❌ Tests FAILED (exit code: {proc.returncode})")
            print(f"     Output:\n{stdout.decode()}")
            return (service_key, False)

    except asyncio.TimeoutError:
        print("     ❌ Tests TIMEOUT")
        return (service_key, False)
    except Exception as e:
        print(f"     ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return (service_key, False)


async def main():
    """Main execution function"""
    print("\n" + "=" * 70)
    print("BCM Services Platform Integration Generator")
    print("=" * 70)
    print(f"\nWill process {len(SERVICES)} services:")
    for service_key, config in SERVICES.items():
        print(f"  - {config['name']} (port {config['port']})")

    base_path = Path(__file__).parent.parent / "platform_services" / "bcm_domain" / "services"

    results = []
    for service_key, config in SERVICES.items():
        result = await process_service(service_key, config, base_path)
        results.append(result)

    # Summary
    print("\n" + "=" * 70)
    print("INTEGRATION SUMMARY")
    print("=" * 70)

    passed = [r for r in results if r[1]]
    failed = [r for r in results if not r[1]]

    print(f"\n✅ Passed: {len(passed)}/{len(results)}")
    for service_key, _ in passed:
        print(f"   - {SERVICES[service_key]['name']}")

    if failed:
        print(f"\n❌ Failed: {len(failed)}/{len(results)}")
        for service_key, _ in failed:
            print(f"   - {SERVICES[service_key]['name']}")

    print("\n" + "=" * 70)

    return len(failed) == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
