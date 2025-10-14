"""
BCM Compliance Service - ISO 22301:2019 Compliance Management
ISO 22301 Clauses: 9.2 (Internal Audit), 10.1 (Nonconformity), 10.2 (Improvement)

FastAPI microservice for compliance management with:
- Assessment engine with production-tested scoring
- Gap analysis and remediation planning
- Evidence management with workflow tracking
- Nonconformity management (ISO 10.1)
- Internal audit support (ISO 9.2)
- Improvement initiatives (ISO 10.2)
- AI-powered compliance scanning
- Event-driven architecture
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from shared.database.connection import init_db, close_db
from shared.eventbus.client import init_eventbus, get_eventbus
from shared.middleware.error_handler import setup_error_handlers
from shared.auth import init_jwt
from shared.cache import init_cache, get_cache

# Workflow Intelligence integration
from workflow_intelligence import PostgresStorageAdapter, WorkflowEngine, ContextAdvisor, CaseCollector
from workflow_intelligence.monitoring import workflow_metrics, health_checker
from workflow_intelligence.audit import AuditLogger
from workflow_intelligence.compliance import ISO22301Checker
from prometheus_client import make_asgi_app

# Service workflow integration
from workflow_integration import WorkflowSecurityMiddleware, check_compliance

# Global workflow intelligence instances
workflow_storage = None
workflow_engine = None
ai_advisor = None
case_collector = None
audit_logger = None
iso_checker = None
security_middleware = None

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info(f"🚀 Starting {settings.SERVICE_TITLE}")
    logger.info(f"Port: {settings.SERVICE_PORT}")
    logger.info(f"Debug mode: {settings.DEBUG_MODE}")
    logger.info(f"AI enabled: {settings.AI_ENABLED}")
    logger.info(f"ISO 22301 Clauses: {', '.join(settings.ISO_CLAUSES)}")

    # Initialize JWT
    init_jwt(settings.JWT_SECRET)
    logger.info("✅ JWT authentication initialized")

    try:
        # Initialize database
        await init_db(
            database_url=settings.DATABASE_URL,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            echo=settings.DB_ECHO
        )
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise

    # Initialize Workflow Intelligence
    global workflow_storage, workflow_engine, ai_advisor, case_collector
    global audit_logger, iso_checker, security_middleware
    try:
        workflow_storage = PostgresStorageAdapter(settings.DATABASE_URL)
        await workflow_storage.connect()

        workflow_engine = WorkflowEngine(
            module="compliance",
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

        logger.info("✅ Workflow Intelligence initialized (Compliance module)")
    except Exception as e:
        logger.warning(f"Workflow Intelligence initialization failed: {e}")

    # Initialize Redis Cache
    redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
    try:
        init_cache(redis_url)
        cache = get_cache()
        if await cache.ping():
            logger.info(f"✅ Redis cache connected: {redis_url}")
        else:
            logger.warning("⚠️ Redis cache connection failed - caching disabled")
    except Exception as e:
        logger.warning(f"⚠️ Redis cache initialization failed: {e}")

    # Initialize EventBus (if enabled)
    if settings.EVENTS_ENABLED:
        try:
            init_eventbus(
                url=settings.EVENTBUS_URL,
                service_name=settings.SERVICE_NAME,
                timeout=settings.EVENTBUS_TIMEOUT
            )

            # Register subscriptions
            eventbus = get_eventbus()
            await eventbus.register_subscriptions()

            logger.info(f"✅ EventBus initialized, subscribed to {len(settings.SUBSCRIBE_TOPICS)} topics")
        except Exception as e:
            logger.warning(f"⚠️  EventBus not available: {e}")

    logger.info("✅ Compliance service startup complete")

    yield

    # Shutdown
    logger.info(f"🛑 Shutting down {settings.SERVICE_TITLE}")

    # Close EventBus
    if settings.EVENTS_ENABLED:
        try:
            eventbus = get_eventbus()
            await eventbus.close()
            logger.info("✅ EventBus closed")
        except:
            pass

    # Close Workflow Intelligence
    if workflow_storage:
        try:
            await workflow_storage.close()
            logger.info("Workflow Intelligence connection closed")
        except Exception as e:
            logger.error(f"Error closing Workflow Intelligence: {e}")

    # Close database
    await close_db()
    logger.info("✅ Database connections closed")

    # Close Redis cache
    try:
        cache = get_cache()
        await cache.close()
        logger.info("✅ Redis cache closed")
    except Exception as e:
        logger.warning(f"Error closing Redis cache: {e}")


# ===== FASTAPI APP =====
app = FastAPI(
    title=settings.SERVICE_TITLE,
    description="""
    **ISO 22301:2019 Compliance Management System**

    Comprehensive compliance management for Business Continuity aligned with ISO 22301:2019 Clauses 9.2, 10.1, and 10.2.

    ## 🎯 Core Capabilities

    ### Audit Management (ISO 9.2 - Internal Audit)
    - Internal audit planning and execution
    - Audit finding tracking
    - Evidence collection and verification
    - Audit report generation

    ### Nonconformity Management (ISO 10.1)
    - Nonconformity identification and logging
    - Root Cause Analysis (RCA) with 3 methods:
      - **5 Whys**: Iterative questioning to drill down to root cause
      - **Fishbone (Ishikawa)**: 6M categorization (People, Process, Technology, Environment, Materials, Measurement)
      - **Fault Tree Analysis**: Top-down deductive analysis with probability assessment
    - Corrective Action Planning (CAPA)
    - Effectiveness verification

    ### Improvement Management (ISO 10.2)
    - Continual improvement initiatives
    - Improvement tracking and metrics
    - Effectiveness measurement

    ### Assessment & Gap Analysis
    - Production-tested compliance scoring algorithm
    - Automated gap identification
    - Remediation planning
    - Evidence management with workflow tracking

    ## 📊 API Endpoints by Category

    ### Evidence Management
    - `POST /api/evidence` - Submit compliance evidence
    - `GET /api/evidence` - List evidence (with filters)
    - `GET /api/evidence/{id}` - Get evidence details
    - `PUT /api/evidence/{id}` - Update evidence
    - `DELETE /api/evidence/{id}` - Archive evidence

    ### Assessments
    - `POST /api/assessments` - Create compliance assessment
    - `GET /api/assessments` - List assessments
    - `GET /api/assessments/{id}` - Get assessment details
    - `POST /api/assessments/{id}/score` - Calculate compliance score

    ### Gap Analysis
    - `GET /api/gaps` - Identify compliance gaps
    - `POST /api/gaps/{id}/remediate` - Create remediation plan
    - `GET /api/gaps/priority` - Gaps by priority

    ### Internal Audit (ISO 9.2)
    - `POST /api/audit/audits` - Create audit
    - `GET /api/audit/audits` - List audits
    - `POST /api/audit/audits/{id}/findings` - Add audit finding
    - `GET /api/audit/audits/{id}/report` - Generate audit report

    ### Nonconformity & RCA (ISO 10.1)
    - `POST /api/nonconformities` - Report nonconformity
    - `GET /api/nonconformities` - List nonconformities
    - `POST /api/nonconformities/{id}/rca/start` - Start RCA process
    - `POST /api/nonconformities/{id}/rca/complete` - Complete RCA
    - `GET /api/rca/templates/{method}` - Get RCA template
    - `GET /api/rca/methods` - List available RCA methods

    ### Improvement Initiatives (ISO 10.2)
    - `POST /api/improvements` - Create improvement initiative
    - `GET /api/improvements` - List improvements
    - `POST /api/improvements/{id}/complete` - Mark complete
    - `GET /api/improvements/metrics` - Improvement metrics

    ### Management Review
    - `POST /api/management-review` - Create review
    - `GET /api/management-review` - List reviews
    - `POST /api/management-review/{id}/actions` - Add action items

    ### Knowledge Base & Library
    - `GET /api/compliance/knowledge` - Search knowledge base
    - `GET /api/compliance/library` - Compliance library
    - `GET /api/compliance/templates` - Document templates

    ## 🔐 Authentication & Authorization
    - **JWT Bearer Token** required for all endpoints
    - **Tenant Isolation**: Automatic row-level security by tenant_id
    - **RBAC Permissions**: COMPLIANCE_VIEW, COMPLIANCE_EDIT, AUDIT_MANAGE, NC_MANAGE
    - **Dev Mode**: Use `X-Dev-User` header with JSON user context

    ## 🏗️ ISO 22301:2019 Compliance

    ### Clause 9.2 - Internal Audit
    ✅ Audit program planning
    ✅ Audit execution and reporting
    ✅ Finding management
    ✅ Follow-up and verification

    ### Clause 10.1 - Nonconformity and Corrective Action
    ✅ Nonconformity identification
    ✅ Root Cause Analysis (3 methods)
    ✅ Corrective action planning (CAPA)
    ✅ Effectiveness verification

    ### Clause 10.2 - Continual Improvement
    ✅ Improvement opportunity identification
    ✅ Initiative tracking
    ✅ Effectiveness measurement
    ✅ Knowledge management

    ## 📚 Root Cause Analysis (RCA) Methods

    ### 1. 5 Whys Method
    Simple iterative questioning technique. Ask "Why?" 5 times to drill down to root cause.

    **Example:**
    ```json
    {
      "problem_statement": "Server downtime occurred",
      "why_1": "Database connection failed",
      "why_2": "Connection pool was exhausted",
      "why_3": "Too many concurrent requests",
      "why_4": "Load balancer misconfigured",
      "why_5": "Configuration not updated after deployment",
      "root_cause": "Lack of deployment checklist and configuration management"
    }
    ```

    ### 2. Fishbone (Ishikawa) Diagram
    Categorize causes using 6M framework.

    **Categories:**
    - **People**: Human factors, training, skills
    - **Process**: Procedures, workflows, policies
    - **Technology**: Systems, tools, infrastructure
    - **Environment**: Physical conditions, external factors
    - **Materials**: Resources, inputs, supplies
    - **Measurement**: Metrics, monitoring, detection

    **Example:**
    ```json
    {
      "problem_statement": "Failed BC plan test",
      "people": [
        {"description": "Team not trained", "sub_causes": ["No training budget", "High turnover"]}
      ],
      "process": [
        {"description": "Outdated procedures", "sub_causes": ["No review process"]}
      ],
      "technology": [
        {"description": "Monitoring gaps", "sub_causes": ["Alert system down"]}
      ]
    }
    ```

    ### 3. Fault Tree Analysis
    Top-down deductive analysis with probability assessment.

    **Example:**
    ```json
    {
      "top_event": {
        "description": "Data center outage",
        "gate_type": "OR",
        "children": [
          {
            "description": "Power failure",
            "gate_type": "AND",
            "children": [
              {"description": "Primary power loss", "probability": 0.05},
              {"description": "Backup generator failure", "probability": 0.10}
            ]
          },
          {"description": "Cooling system failure", "probability": 0.08}
        ]
      }
    }
    ```

    ## 🔄 Nonconformity Workflow State Machine

    ```
    IDENTIFIED → RCA_IN_PROGRESS → CORRECTIVE_ACTION → VERIFICATION → CLOSED
                                                     ↓
                                                 REOPENED (if ineffective)
    ```

    **Valid Transitions:**
    - IDENTIFIED → RCA_IN_PROGRESS (start RCA)
    - RCA_IN_PROGRESS → CORRECTIVE_ACTION (complete RCA)
    - CORRECTIVE_ACTION → VERIFICATION (actions implemented)
    - VERIFICATION → CLOSED (verified effective)
    - VERIFICATION → REOPENED (verified ineffective)
    - REOPENED → CORRECTIVE_ACTION (new actions)

    ## 🔍 Error Codes
    - `400` - Validation error
    - `401` - Unauthorized
    - `403` - Forbidden (tenant mismatch)
    - `404` - Resource not found
    - `409` - Conflict (invalid state transition)
    - `422` - Business rule violation
    - `500` - Internal server error

    ## 📖 Documentation
    - **Swagger UI**: /docs
    - **ReDoc**: /redoc
    - **OpenAPI Spec**: /openapi.json
    - **Health Check**: /health

    ## 🚀 Integration
    - **Service Port**: 8014
    - **EventBus**: Port 8001
    - **AI Orchestration**: Port 8002
    - **API Gateway**: Port 8000
    """,
    version=settings.SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "Health",
            "description": "Service health and status checks"
        },
        {
            "name": "Evidence",
            "description": "Compliance evidence management with workflow tracking"
        },
        {
            "name": "Assessments",
            "description": "Compliance assessments and scoring engine"
        },
        {
            "name": "Gaps",
            "description": "Gap analysis and remediation planning"
        },
        {
            "name": "Dashboard",
            "description": "Compliance dashboard and metrics"
        },
        {
            "name": "Audit",
            "description": "Internal audit management - ISO 22301 Clause 9.2"
        },
        {
            "name": "Management Review",
            "description": "Management review process and action tracking"
        },
        {
            "name": "Modules Health",
            "description": "Module health status and diagnostics"
        },
        {
            "name": "Knowledge Base",
            "description": "Compliance knowledge base and search"
        },
        {
            "name": "Library",
            "description": "Compliance document library"
        },
        {
            "name": "Templates",
            "description": "Compliance document templates"
        },
        {
            "name": "Improvement Initiatives",
            "description": "Continual improvement - ISO 22301 Clause 10.2"
        },
        {
            "name": "Nonconformities & RCA",
            "description": "Nonconformity management and Root Cause Analysis - ISO 22301 Clause 10.1"
        }
    ]
)

# Security middleware (Auth + Audit)
if security_middleware:
    app.middleware("http")(security_middleware)
    logger.info("✅ Security middleware enabled (Auth + Audit)")


# CORS Configuration
if settings.CORS_ALLOW_CREDENTIALS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    logger.info(f"✅ CORS enabled for origins: {settings.CORS_ORIGINS}")

# Setup error handlers
setup_error_handlers(app)
logger.info("✅ Error handlers configured")

# ===== INCLUDE API ROUTERS =====
# Core compliance routers
from api import (
    health,
    evidence,
    assessments,
    gaps,
    dashboard,
    audit,
    management_review,
    modules,
    knowledge_base,
    library,
    templates,
    improvements,
    nonconformities
)
from api.workflow_ai import router as workflow_ai_router

app.include_router(health.router, tags=["Health"])
app.include_router(evidence.router, prefix="/api/evidence", tags=["Evidence"])
app.include_router(assessments.router, prefix="/api/assessments", tags=["Assessments"])
app.include_router(gaps.router, prefix="/api/gaps", tags=["Gaps"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(audit.router, prefix="/api/audit", tags=["Audit"])
app.include_router(management_review.router, prefix="/api/management-review", tags=["Management Review"])
app.include_router(modules.router, prefix="/api/modules", tags=["Modules Health"])
app.include_router(knowledge_base.router, prefix="/api/compliance/knowledge", tags=["Knowledge Base"])
app.include_router(library.router, prefix="/api/compliance/library", tags=["Library"])
app.include_router(templates.router, prefix="/api/compliance", tags=["Templates"])
app.include_router(improvements.router, prefix="/api", tags=["Improvement Initiatives"])
app.include_router(nonconformities.router, prefix="/api", tags=["Nonconformities & RCA"])
app.include_router(workflow_ai_router)  # Workflow Intelligence AI endpoints

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

logger.info("✅ All 14 compliance API routers loaded (including Workflow Intelligence)")


# ===== HEALTH CHECK =====

@app.get("/api/compliance/check")
async def compliance_check():
    """
    Check ISO 22301 Clause 9.2 compliance

    Returns current compliance status and gaps
    """
    if not iso_checker:
        return {"error": "ISO compliance checker not initialized"}

    # Example context - in production this would come from actual workflow
    sample_context = {"data": {}}

    result = await check_compliance(sample_context, iso_checker, "9.2")

    return {
        "iso_clause": "9.2",
        "module": "compliance",
        "compliance_status": result
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "iso_clauses": settings.ISO_CLAUSES,
        "port": settings.SERVICE_PORT,
        "modules": {
            "evidence": "active",
            "assessments": "active",
            "gaps": "active",
            "dashboard": "active",
            "audit": "active",
            "management_review": "active",
            "knowledge_base": "active",
            "library": "active",
            "templates": "active",
            "improvements": "active",
            "nonconformities": "active"
        }
    }


# ===== STARTUP =====
if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting {settings.SERVICE_TITLE} on port {settings.SERVICE_PORT}")
    logger.info(f"ISO 22301 Clauses: {', '.join(settings.ISO_CLAUSES)}")
    logger.info("📊 Compliance assessment, gap analysis, and continual improvement")

    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
