"""
Knowledge Quality Manager (KQM) - Main Service

Orchestrates knowledge management:
1. Scenario generation (auto)
2. Knowledge monitoring
3. Compliance validation
4. Gap detection
5. Quality assurance

Port: 8090
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import asyncio

from config.settings import settings
from tools.scenario_generator import ScenarioGenerator
from analytics.knowledge_monitor import KnowledgeMonitor
from validation.compliance_controller import ComplianceController

# Prometheus metrics
from prometheus_client import Counter, Gauge, CollectorRegistry, generate_latest, REGISTRY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
scenario_generator = None
knowledge_monitor = None
compliance_controller = None
orchestrator_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    global scenario_generator, knowledge_monitor, compliance_controller, orchestrator_task

    logger.info(" Starting Knowledge Quality Manager...")

    # Initialize components
    scenario_generator = ScenarioGenerator()
    knowledge_monitor = KnowledgeMonitor()
    compliance_controller = ComplianceController()

    logger.info(" Components initialized")

    # Start orchestration cycle (background task)
    orchestrator_task = asyncio.create_task(run_orchestration_cycle())
    logger.info(" Orchestration cycle started")

    yield

    # Shutdown
    logger.info(" Shutting down Knowledge Quality Manager...")
    if orchestrator_task:
        orchestrator_task.cancel()


async def run_orchestration_cycle():
    """Main 24-hour orchestration cycle"""

    logger.info(" Orchestration cycle: Starting...")

    while True:
        try:
            logger.info(" Cycle: Assessing knowledge state...")

            # 1. MONITOR current state
            knowledge_state = await knowledge_monitor.assess()
            logger.info(f"   Coverage: {knowledge_state.coverage.iso_coverage:.1%}")
            logger.info(f"   Quality: {knowledge_state.quality.validation_rate:.1%}")

            # 2. DETECT gaps
            gaps = await knowledge_monitor.detect_gaps()
            logger.info(f"   Gaps detected: {len(gaps)}")

            # 3. PRIORITIZE (top 10)
            priorities = sorted(gaps, key=lambda x: x.priority, reverse=True)[:10]
            logger.info(f"   Prioritized: {len(priorities)} gaps")

            # 4. GENERATE scenarios
            if priorities:
                logger.info(" Generating scenarios...")
                new_scenarios = await scenario_generator.generate(priorities)
                logger.info(f"   Generated: {len(new_scenarios)} scenarios")

                # 5. VALIDATE
                logger.info(" Validating scenarios...")
                validated = await compliance_controller.validate(new_scenarios)
                approved = [s for s in validated if s.status == 'approved']
                logger.info(f"   Approved: {len(approved)}/{len(validated)}")

                # 6. STORE (auto-save in generator)
                logger.info(f"   Stored: {len(approved)} scenarios")

            # 7. REPORT metrics
            await knowledge_monitor.report_metrics()

            logger.info(" Cycle complete. Sleeping 24 hours...")
            await asyncio.sleep(86400)  # 24 hours

        except asyncio.CancelledError:
            logger.info("Orchestration cycle cancelled")
            break
        except Exception as e:
            logger.error(f"Orchestration cycle error: {e}", exc_info=True)
            await asyncio.sleep(3600)  # Retry in 1 hour


# Create FastAPI app
app = FastAPI(
    title="Knowledge Quality Manager",
    description="""
    **Intelligent Knowledge Management Service**

    Manages platform knowledge through:
    -  Auto-scenario generation
    -  Knowledge monitoring
    -  Compliance validation
    -  Gap detection
    -  Quality assurance

    ## Features
    - **Scenario Generator**: Auto-creates scenarios from standards, capabilities, user needs
    - **Knowledge Monitor**: Tracks coverage, quality, usage
    - **Compliance Controller**: Validates ISO/NIST/WHO compliance
    - **Predictive**: Anticipates knowledge needs

    ## Architecture
    ```
    Standards + Platform + Users
           ↓
    Gap Detection + Prioritization
           ↓
    LLM Generation + Expert Validation
           ↓
    RAG + File System + Redis
    ```

    ## Integration
    - **AI Foundation**: RAG, LLM, Embeddings
    - **Expertise Center**: Domain specialists
    - **Community Intelligence**: k=5 patterns
    - **Predictive**: Future needs
    - **DB Intelligence**: Storage optimization
    """,
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

# Prometheus Metrics - use custom registry to avoid duplicates on reload
kqm_registry = CollectorRegistry()
kqm_scenarios_total = Gauge(
    'kqm_scenarios_total',
    'Total number of scenarios in knowledge base',
    registry=kqm_registry
)
kqm_gaps_detected = Gauge(
    'kqm_gaps_detected',
    'Number of knowledge gaps detected',
    registry=kqm_registry
)
kqm_iso_coverage = Gauge(
    'kqm_iso_coverage',
    'ISO 22301 clause coverage percentage (0-100)',
    registry=kqm_registry
)
kqm_platform_coverage = Gauge(
    'kqm_platform_coverage',
    'Platform service coverage percentage (0-100)',
    registry=kqm_registry
)
kqm_generation_count = Counter(
    'kqm_generation_count_total',
    'Total scenarios generated',
    ['source_type'],
    registry=kqm_registry
)
kqm_avg_confidence = Gauge(
    'kqm_avg_confidence',
    'Average confidence score of scenarios (0-1)',
    registry=kqm_registry
)
kqm_knowledge_value = Gauge(
    'kqm_knowledge_value',
    'Total economic value of knowledge base',
    registry=kqm_registry
)
kqm_rag_searches = Counter(
    'kqm_rag_searches_total',
    'Total RAG searches performed',
    registry=kqm_registry
)


# ===== ENDPOINTS =====

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "knowledge-quality-manager",
        "port": settings.SERVICE_PORT,
        "version": "1.0.0"
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # Update metrics from current state
    if knowledge_monitor:
        try:
            state = await knowledge_monitor.assess()

            # Update gauges
            kqm_scenarios_total.set(state.coverage.total_scenarios)
            kqm_gaps_detected.set(len(await knowledge_monitor.detect_gaps()))
            kqm_iso_coverage.set(state.coverage.iso_coverage * 100)
            kqm_platform_coverage.set(state.coverage.platform_coverage * 100)
            kqm_avg_confidence.set(state.quality.avg_confidence)

            # Knowledge value (if generator available)
            if scenario_generator:
                kqm_knowledge_value.set(scenario_generator.knowledge_value)

        except Exception as e:
            logger.warning(f"Metrics update error: {e}")

    # Generate Prometheus metrics
    return Response(
        content=generate_latest(kqm_registry),
        media_type="text/plain"
    )


@app.get("/api/kqm/status")
async def get_status():
    """Get KQM status"""
    if knowledge_monitor:
        state = await knowledge_monitor.assess()
        return {
            "status": "running",
            "knowledge_state": state.dict(),
            "orchestration": "active"
        }
    return {"status": "initializing"}


@app.get("/api/kqm/knowledge/coverage")
async def get_knowledge_coverage():
    """Get knowledge coverage metrics"""
    if knowledge_monitor:
        coverage = await knowledge_monitor.assess_coverage()
        return coverage.dict()
    return {"error": "Monitor not initialized"}


@app.get("/api/kqm/knowledge/gaps")
async def get_knowledge_gaps():
    """Get detected knowledge gaps"""
    if knowledge_monitor:
        gaps = await knowledge_monitor.detect_gaps()
        return {
            "total_gaps": len(gaps),
            "by_type": {
                "standard": len([g for g in gaps if g.type == "standard_requirement"]),
                "capability": len([g for g in gaps if g.type == "platform_capability"]),
                "user_request": len([g for g in gaps if g.type == "user_request"])
            },
            "top_priorities": [g.dict() for g in sorted(gaps, key=lambda x: x.priority, reverse=True)[:10]]
        }
    return {"error": "Monitor not initialized"}


@app.post("/api/kqm/scenarios/generate")
async def generate_scenarios(gap_ids: list[str] = None):
    """Manually trigger scenario generation"""
    if not scenario_generator:
        return {"error": "Generator not initialized"}

    # Get gaps
    if gap_ids:
        gaps = await knowledge_monitor.get_gaps_by_ids(gap_ids)
    else:
        all_gaps = await knowledge_monitor.detect_gaps()
        gaps = sorted(all_gaps, key=lambda x: x.priority, reverse=True)[:5]

    # Generate
    scenarios = await scenario_generator.generate(gaps)

    # Validate
    validated = await compliance_controller.validate(scenarios)

    return {
        "generated": len(scenarios),
        "validated": len(validated),
        "approved": len([s for s in validated if s.status == 'approved']),
        "scenarios": [s.dict() for s in validated]
    }


@app.get("/api/kqm/compliance/status")
async def get_compliance_status():
    """Get compliance status across standards"""
    if compliance_controller:
        status = await compliance_controller.get_compliance_status()
        return status
    return {"error": "Controller not initialized"}


@app.get("/api/kqm/analytics/metrics")
async def get_metrics():
    """Get comprehensive metrics"""
    if knowledge_monitor:
        metrics = await knowledge_monitor.get_all_metrics()
        return metrics
    return {"error": "Monitor not initialized"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Knowledge Quality Manager",
        "version": "1.0.0",
        "status": "operational",
        "description": "Intelligent knowledge management for BCM platform",
        "endpoints": {
            "health": "/health",
            "status": "/api/kqm/status",
            "knowledge": "/api/kqm/knowledge/*",
            "scenarios": "/api/kqm/scenarios/*",
            "compliance": "/api/kqm/compliance/*",
            "analytics": "/api/kqm/analytics/*"
        },
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f" Starting Knowledge Quality Manager on port {settings.SERVICE_PORT}")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=True,
        log_level="info"
    )
