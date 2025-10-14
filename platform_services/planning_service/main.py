"""
Planning Service - Main Application
ISO 22301 Clause 8.3 - Business Continuity Strategy

Port: 8011
Endpoints: 8
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import httpx

from .config import settings
from .database import init_db, close_db
from .api.routes import router as strategy_router
from .api.health import router as health_router
from .api.metrics import router as metrics_router
from .api.workflow_ai import router as workflow_ai_router
from .api.error_handlers import (
    validation_exception_handler,
    generic_exception_handler,
    value_error_handler
)
from .api.rate_limit import rate_limit_middleware
from shared.cache import init_cache, get_cache

# Workflow Intelligence integration
from workflow_intelligence import PostgresStorageAdapter, WorkflowEngine, ContextAdvisor, CaseCollector
from workflow_intelligence.monitoring import workflow_metrics, health_checker
from workflow_intelligence.audit import AuditLogger
from workflow_intelligence.compliance import ISO22301Checker

# Planning Service workflow integration
from .workflow_integration import WorkflowSecurityMiddleware, check_planning_compliance

# Prometheus metrics
from prometheus_client import make_asgi_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global workflow intelligence instances
workflow_storage = None
workflow_engine = None
ai_advisor = None
case_collector = None
audit_logger = None
iso_checker = None
security_middleware = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Planning Service starting up...")

    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")

        # Initialize Redis Cache
        redis_url = getattr(settings, 'REDIS_URL', 'redis://redis:6379/0')
        try:
            init_cache(redis_url)
            cache = get_cache()
            if await cache.ping():
                logger.info(f"Redis cache connected: {redis_url}")
            else:
                logger.warning("Redis cache connection failed - caching disabled")
        except Exception as e:
            logger.warning(f"Redis cache initialization failed: {e}")

        # Initialize Workflow Intelligence
        global workflow_storage, workflow_engine, ai_advisor, case_collector
        global audit_logger, iso_checker, security_middleware
        try:
            workflow_storage = PostgresStorageAdapter(settings.DATABASE_URL)
            await workflow_storage.connect()

            workflow_engine = WorkflowEngine(
                module="planning",
                storage_adapter=workflow_storage
            )

            # AI Advisor (optional - requires LLM client)
            # ai_advisor = ContextAdvisor(
            #     workflow_engine=workflow_engine,
            #     llm_client=None  # Add Claude/OpenAI client if needed
            # )

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

            logger.info("✅ Workflow Intelligence initialized (Planning module)")
        except Exception as e:
            logger.warning(f"Workflow Intelligence initialization failed: {e}")

        # Register with orchestrator
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{settings.ORCHESTRATOR_URL}/services/register",
                    json={
                        "name": settings.SERVICE_NAME,
                        "port": settings.SERVICE_PORT,
                        "health_endpoint": "/health",
                        "iso_clauses": ["8.3"],
                        "bci_practices": ["PP4"],
                    },
                    timeout=5.0
                )
            logger.info("Registered with orchestrator")
        except Exception as e:
            logger.warning(f"Could not register with orchestrator: {e}")

        # Subscribe to events via EventBus
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{settings.EVENTBUS_URL}/subscribe",
                    json={
                        "service": settings.SERVICE_NAME,
                        "topics": [
                            "bia.analysis.completed",  # Listen for BIA completions
                            "risk.assessment.completed",  # Listen for risk assessments
                        ]
                    },
                    timeout=5.0
                )
            logger.info("Subscribed to EventBus topics")
        except Exception as e:
            logger.warning(f"Could not subscribe to EventBus: {e}")

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Planning Service shutting down...")

    # Close Workflow Intelligence
    if workflow_storage:
        try:
            await workflow_storage.close()
            logger.info("Workflow Intelligence connection closed")
        except Exception as e:
            logger.error(f"Error closing Workflow Intelligence: {e}")

    try:
        # Unregister from orchestrator
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{settings.ORCHESTRATOR_URL}/services/unregister",
                json={"name": settings.SERVICE_NAME},
                timeout=5.0
            )
        logger.info("Unregistered from orchestrator")
    except Exception as e:
        logger.warning(f"Could not unregister from orchestrator: {e}")

    # Close database
    await close_db()
    logger.info("Database connections closed")

    # Close Redis cache
    try:
        cache = get_cache()
        await cache.close()
        logger.info("Redis cache closed")
    except Exception as e:
        logger.warning(f"Error closing Redis cache: {e}")


# Create FastAPI app
app = FastAPI(
    title="BCM Planning Service",
    description="""
    **Business Continuity Planning Service - ISO 22301:2019 Clause 8.3**

    Strategy development and selection service aligned with ISO 22301:2019 Clause 8.3 requirements.

    ## 🎯 Core Features
    - **Strategy Development**: Create and manage BC strategies based on BIA results
    - **Cost-Benefit Analysis**: NPV, ROI, Payback Period calculations
    - **Resource Planning**: Personnel, technology, facility requirements
    - **Approval Workflow**: Draft → Review → Approved state machine
    - **Financial Modeling**: Multi-year TCO and benefit projections

    ## 📊 API Endpoints

    ### Strategy Management
    - `POST /api/strategies` - Create BC strategy
    - `GET /api/strategies` - List strategies (with filters)
    - `GET /api/strategies/{id}` - Get strategy details
    - `PUT /api/strategies/{id}` - Update strategy (draft only)
    - `DELETE /api/strategies/{id}` - Archive strategy

    ### Financial Analysis
    - `POST /api/strategies/{id}/cost-benefit` - Calculate cost-benefit analysis
      - **NPV**: Net Present Value calculation
      - **ROI**: Return on Investment percentage
      - **Payback Period**: Time to recover investment

    ### Workflow
    - `POST /api/strategies/{id}/submit-review` - Submit for review (Draft → Review)
    - `POST /api/strategies/{id}/approve` - Approve strategy (Review → Approved)

    ## 🔐 Authentication
    - **JWT Bearer Token** required
    - **Tenant Isolation**: Automatic filtering by tenant_id from JWT
    - **RBAC**: STRATEGY_CREATE, STRATEGY_VIEW, STRATEGY_APPROVE permissions

    ## 🏗️ ISO 22301:2019 Clause 8.3 Compliance

    ✅ **Strategy Selection Criteria**
    - Based on BIA results (RTO/RPO requirements)
    - Cost-benefit analysis
    - Resource availability
    - Regulatory requirements

    ✅ **Strategy Types**
    - DO_NOTHING: Accept the risk
    - MANUAL_WORKAROUND: Temporary manual procedures
    - RECIPROCAL_ARRANGEMENT: Agreement with another organization
    - GRADUAL_RECOVERY: Restore over time
    - INTERMEDIATE_RECOVERY: Moderate recovery speed
    - FAST_RECOVERY: Hot standby, rapid recovery
    - IMMEDIATE_RECOVERY: Real-time failover

    ✅ **Resource Planning**
    - Personnel requirements
    - Technology infrastructure
    - Facilities and workspace
    - Third-party services

    ## 💰 Financial Calculations

    ### Net Present Value (NPV)
    ```
    NPV = Σ (Benefit_t - Cost_t) / (1 + discount_rate)^t
    ```

    ### Return on Investment (ROI)
    ```
    ROI = ((Total Benefits - Total Costs) / Total Costs) × 100%
    ```

    ### Payback Period
    ```
    Time when Cumulative_Benefits >= Total_Investment
    ```

    ## 📚 Request/Response Examples

    ### Create Strategy
    ```json
    {
      "tenant_id": "tenant-123",
      "name": "Payment System Recovery Strategy",
      "strategy_type": "FAST_RECOVERY",
      "description": "Hot standby for payment processing",
      "target_rto_hours": 2,
      "target_rpo_hours": 1,
      "estimated_cost": 500000,
      "implementation_timeline_days": 90
    }
    ```

    ### Cost-Benefit Analysis
    ```json
    {
      "analysis_period_years": 3,
      "discount_rate": 0.08,
      "implementation_cost": 500000,
      "annual_operating_cost": 150000,
      "annual_benefit": 800000,
      "one_time_costs": [
        {"description": "Infrastructure", "amount": 300000},
        {"description": "Training", "amount": 50000}
      ],
      "recurring_costs": [
        {"description": "Maintenance", "annual_amount": 100000},
        {"description": "Support", "annual_amount": 50000}
      ]
    }
    ```

    ### Cost-Benefit Response
    ```json
    {
      "npv": 1234567.89,
      "roi_percentage": 145.6,
      "payback_period_months": 18,
      "break_even_year": 2,
      "total_cost_3yr": 950000,
      "total_benefit_3yr": 2400000,
      "recommendation": "APPROVE - Positive NPV and ROI > 100%",
      "risk_factors": ["Assumes 95% uptime", "Benefit estimate based on historical downtime"]
    }
    ```

    ## 🔍 Error Codes
    - `400` - Validation error
    - `401` - Unauthorized
    - `403` - Forbidden (tenant mismatch)
    - `404` - Strategy not found
    - `409` - Invalid state transition
    - `422` - Business rule violation

    ## 📖 Documentation
    - **Swagger UI**: /docs
    - **ReDoc**: /redoc
    - **Health Check**: /health

    ## 🚀 Integration
    - **Service Port**: 8011
    - **EventBus**: Port 8001
    - **Listens to**: bia.analysis.completed, risk.assessment.completed
    """,
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "strategies",
            "description": "BC Strategy management - ISO 22301 Clause 8.3"
        },
        {
            "name": "health",
            "description": "Service health and metrics"
        }
    ]
)

# Security middleware (Auth + Audit)
if security_middleware:
    app.middleware("http")(security_middleware)

# Rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# CORS middleware - Secure configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

# Register error handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(strategy_router, prefix="/api")
app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(workflow_ai_router)  # Workflow Intelligence AI endpoints

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "iso_clauses": ["8.3"],
        "bci_practices": ["PP4"],
        "port": settings.SERVICE_PORT,
    }


# Compliance endpoint
@app.get("/api/compliance/check")
async def compliance_check():
    """
    Check ISO 22301 Clause 8.3 compliance

    Returns current compliance status and gaps
    """
    if not iso_checker:
        return {
            "error": "ISO compliance checker not initialized"
        }

    # Example context - in production this would come from actual workflow
    sample_context = {
        "data": {
            "objectives_documented": True,
            "measurable_targets": True,
            "action_plan": True,
            "responsibilities_assigned": True
        }
    }

    result = await check_planning_compliance(sample_context, iso_checker)

    return {
        "iso_clause": "8.3",
        "module": "planning",
        "compliance_status": result
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "BCM Planning Service",
        "version": "1.0.0",
        "status": "operational",
        "description": "Business Continuity Strategy Development - ISO 22301 Clause 8.3",
        "port": settings.SERVICE_PORT,
        "docs": "/docs",
        "health": "/health",
        "security": {
            "auth": "JWT Bearer Token",
            "audit_logging": "Enabled" if audit_logger else "Disabled",
            "tenant_isolation": "RLS + Application Layer"
        },
        "iso_compliance": {
            "clause_8_3": "Business Continuity Strategies",
            "compliance_endpoint": "/api/compliance/check"
        },
        "api_endpoints": {
            "strategies": "/api/strategies - Strategy management",
            "cost_benefit": "/api/strategies/{id}/cost-benefit - Cost-benefit analysis",
            "approval": "/api/strategies/{id}/approve - Strategy approval",
            "compliance": "/api/compliance/check - ISO 22301 compliance check"
        }
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting Planning Service on port {settings.SERVICE_PORT}")
    logger.info("ISO 22301 Clause 8.3 - Business Continuity Strategy")
    logger.info("BCI PP4 - Solutions Design")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=True,
        log_level="info"
    )
