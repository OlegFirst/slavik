"""
Risk Management Service - Main Application
ISO 22301:2019 Clause 8.2.3 - Risk Assessment

Port: 8040
"""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Add shared database to Python path
shared_db_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "platform-services" / "community-service" / "shared"
if str(shared_db_path) not in sys.path:
    sys.path.insert(0, str(shared_db_path))

from database.connection import init_db, close_db
from api.routes import router
from config import settings

# Workflow Intelligence imports
from workflow_intelligence import PostgresStorageAdapter, WorkflowEngine, CaseCollector
from workflow_intelligence.monitoring import workflow_metrics, health_checker
from workflow_intelligence.audit import AuditLogger
from workflow_intelligence.compliance import ISO22301Checker
from prometheus_client import make_asgi_app

# Service workflow integration
from workflow_integration import WorkflowSecurityMiddleware, check_compliance
from prometheus_client import make_asgi_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Workflow Intelligence global instances
workflow_storage = None
workflow_engine = None
case_collector = None
audit_logger = None
iso_checker = None
security_middleware = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global workflow_storage, workflow_engine, case_collector
    global audit_logger, iso_checker, security_middleware

    # Startup
    logger.info("🚀 Risk Management Service starting...")
    await init_db()
    logger.info("✅ Database initialized")

    # Initialize Workflow Intelligence
    try:
        workflow_storage = PostgresStorageAdapter(settings.DATABASE_URL)
        await workflow_storage.connect()

        workflow_engine = WorkflowEngine(
            module="risk",
            storage_adapter=workflow_storage
        )

        case_collector = CaseCollector(storage_adapter=workflow_storage)
        # Initialize Audit Logger
        audit_logger = AuditLogger(storage_adapter=workflow_storage)
        await audit_logger.ensure_schema()
        logger.info("✅ Audit logging initialized")

        # Initialize ISO Compliance Checker
        iso_checker = ISO22301Checker()
        logger.info("✅ ISO 22301 compliance checker initialized")

        # Initialize Security Middleware
        jwt_secret = getattr(settings, 'JWT_SECRET', 'dev-secret-key-change-in-production')
        security_middleware = WorkflowSecurityMiddleware(
            audit_logger=audit_logger,
            iso_checker=iso_checker,
            jwt_secret=jwt_secret
        )
        logger.info("✅ Security middleware initialized")

        

        # Set health metrics
        workflow_metrics.set_health("workflow_intelligence", True)
        workflow_metrics.set_health("database", True)
        workflow_metrics.set_health("audit_logging", True)
        workflow_metrics.set_health("iso_compliance", True)

        logger.info("✅ Workflow Intelligence initialized (risk module)")
    except Exception as e:
        logger.warning(f"Workflow Intelligence initialization failed: {e}")

    logger.info(f"✅ Risk Management Service ready on port {settings.PORT}")
    yield

    # Shutdown
    logger.info("🛑 Risk Management Service shutting down...")

    # Close Workflow Intelligence
    if workflow_storage:
        try:
            await workflow_storage.close()
            logger.info("Workflow Intelligence connection closed")
        except Exception as e:
            logger.error(f"Error closing Workflow Intelligence: {e}")

    await close_db()
    logger.info("✅ Database connections closed")


# Create FastAPI app
app = FastAPI(
    title=settings.SERVICE_NAME,
    description="""
    Risk Management Capability - ISO 22301:2019 Clause 8.2.3

    **Features:**
    - Risk Assessment (Likelihood × Impact)
    - FAIR Quantitative Analysis
    - Monte Carlo Simulation
    - Risk Treatment Plans
    - Risk Heat Maps & Reports

    **Risk Matrix:**
    - Likelihood: 1-5 (Rare to Almost Certain)
    - Impact: 1-5 (Insignificant to Catastrophic)
    - Risk Score: Likelihood × Impact (1-25)

    **Treatment Strategies:**
    - Avoid: Eliminate the risk
    - Mitigate: Reduce likelihood/impact
    - Transfer: Insurance, outsourcing
    - Accept: Accept the risk
    """,
    version=settings.SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
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
app.include_router(router)

# Include Workflow AI router
from api.workflow_ai import router as workflow_ai_router
app.include_router(workflow_ai_router)

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# ============================================================================
# Health Check
# ============================================================================


@app.get("/api/compliance/check")
async def compliance_check():
    """
    Check ISO 22301 Clause 8.2.3 compliance

    Returns current compliance status and gaps
    """
    if not iso_checker:
        return {"error": "ISO compliance checker not initialized"}

    # Example context - in production this would come from actual workflow
    sample_context = {"data": {}}

    result = await check_compliance(sample_context, iso_checker, "8.2.3")

    return {
        "iso_clause": "8.2.3",
        "module": "risk",
        "compliance_status": result
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "risk-management",
        "status": "healthy",
        "version": settings.SERVICE_VERSION,
        "iso_standard": "ISO 22301:2019 Clause 8.2.3"
    }


@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": settings.SERVICE_NAME,
        "description": "Risk Management Capability for BCM Platform",
        "version": settings.SERVICE_VERSION,
        "iso_compliance": "ISO 22301:2019 Clause 8.2.3",
        "capabilities": {
            "risk_assessment": "5×5 Risk Matrix (Likelihood × Impact)",
            "fair_analysis": "Factor Analysis of Information Risk (Quantitative)",
            "monte_carlo": "Monte Carlo Simulation (Probability Distribution)",
            "treatment_planning": "Risk Treatment & Mitigation Plans",
            "reporting": "Risk Heat Maps, Reports & Analytics"
        },
        "endpoints": {
            "api": "/api/v1/risk",
            "documentation": "/docs",
            "health": "/health"
        },
        "risk_severity_levels": {
            "critical": "Score ≥ 20",
            "high": "Score 15-19",
            "medium": "Score 8-14",
            "low": "Score < 8"
        }
    }


# ============================================================================
# Run with: uvicorn main:app --host 0.0.0.0 --port 8040 --reload
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True if os.getenv("DEBUG") == "true" else False
    )
