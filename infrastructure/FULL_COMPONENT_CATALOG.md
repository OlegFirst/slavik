# Infrastructure Component Catalog
**Generated:** 2025-10-08
**Total Components:** 35+
**Running Services:** 1 detected
**Integration Status:** Mixed (Partially integrated)

---

## Executive Summary

### Component Statistics
- **Services (with main.py):** 11
- **Libraries/Tools:** 9
- **Infrastructure Components:** 8
- **Configuration-only:** 7

### Status Overview
- **Running:** 1 service (workflow_intelligence on port 8020)
- **Stopped/Not Started:** 10 services
- **No Main (Library):** 15 components
- **Deprecated:** 1 component

### Integration Health
- **Fully Integrated:** 8 components (23%)
- **Partially Integrated:** 12 components (34%)
- **Not Integrated:** 15 components (43%)

---

## I. AI-OFFICE INFRASTRUCTURE (9 Components)
> AI-powered management and operations services

### 1.1 MIO Manager (AI Monitoring & Observability)
**Component:** mio-manager
- **Path:** `/infrastructure/AI-office-infrastructure/mio-manager`
- **Type:** service
- **Port:** 8046
- **Status:** stopped (not running)
- **Main File:** `/infrastructure/AI-office-infrastructure/mio-manager/main.py`

**Purpose:**
- Central management hub for platform monitoring
- Coordinates Automation Toolkit for infrastructure analysis
- Manages API Gateway and service discovery
- Reports to monitoring systems
- Creates remediation tasks

**Dependencies:**
- FastAPI, prometheus-client
- Automation Toolkit (internal)
- Orchestrator Client (internal)
- Gateway Manager (internal)
- Workflow Intelligence Client
- Predictive Client
- Coordination Center Client
- Compliance Monitoring Client
- EventBus Client
- AI Event Manager Client
- DevOps Agent Client
- SmartScheduler (internal)
- AI Intelligence Layer (AICoordinator, DecisionEngine, LearningTracker)

**Integration Points:**
- ✅ AI Orchestrator (REST API)
- ✅ API Gateway (management API)
- ✅ Automation Toolkit
- ✅ Workflow Intelligence (port 8020)
- ✅ Predictive Service
- ✅ Coordination Center
- ✅ Compliance Monitoring
- ✅ EventBus (Redis Streams)
- ✅ AI Event Manager (port 8055)
- ✅ DevOps Agent (port 8060)
- ✅ Prometheus metrics at /metrics
- ⚠️ Database: PostgreSQL (Supabase)
- ⚠️ Redis: for state caching

**Notes:**
- **Version:** 2.0 with AI Intelligence Layer
- Enhanced with SmartScheduler and deep analysis cycles
- Includes reaction system (escalation manager, action executor)
- Battle-ready monitoring and automation

---

### 1.2 DB Intelligence (Database Monitoring Specialist)
**Component:** db-intelligence
- **Path:** `/infrastructure/AI-office-infrastructure/db-intelligence`
- **Type:** service
- **Port:** 8050
- **Status:** stopped (not running)
- **Main File:** `/infrastructure/AI-office-infrastructure/db-intelligence/main.py`

**Purpose:**
- AI-powered database monitoring and optimization
- Query performance analysis (pg_stat_statements)
- Slow query detection and optimization suggestions
- Security monitoring (RLS, SQL injection, DOS protection)
- Health monitoring and alerting
- Prometheus metrics export

**Dependencies:**
- FastAPI, asyncpg, sqlalchemy
- AI Foundation (LLM, RAG)
- Prometheus client

**Integration Points:**
- ✅ PostgreSQL (Supabase) - monitored database
- ✅ EventBus - async alerts, pub/sub notifications
- ✅ AI Orchestrator - sync commands, service coordination
- ✅ AI Foundation - LLM analysis, RAG enrichment
- ✅ Prometheus - metrics at /metrics/prometheus
- 📊 Grafana - visualizations

**Notes:**
- **Moved from:** `/infrastructure/database/` to AI-Office
- Now an AI colleague in Infrastructure Management Office
- Dual integration: EventBus + Direct Orchestrator API
- Production ready

---

### 1.3 AI Event Manager
**Component:** ai-event-manager
- **Path:** `/infrastructure/AI-office-infrastructure/ai-event-manager`
- **Type:** service
- **Port:** 8055
- **Status:** stopped (not running)
- **Main File:** `/infrastructure/AI-office-infrastructure/ai-event-manager/main.py`

**Purpose:**
- Infrastructure service for event management
- AI-powered event analysis and recommendations
- Learning from developer feedback
- Future event prediction
- Real-time dashboard and statistics

**Dependencies:**
- FastAPI
- intelligent_core.event_intelligence (EventAnalyzer, EventLearner, EventPredictor)
- tools.event_intelligence (EventIntelligenceSystem, EventIntelligenceMonitor)
- prometheus-client

**Integration Points:**
- ✅ Event Intelligence System (analysis engine)
- ✅ Prometheus metrics at /metrics
- ⚠️ EventBus catalog (reads from)
- ⚠️ MIO Manager (coordinates with)
- ❌ Database (not yet implemented)

**Notes:**
- Uses intelligent-core for AI analysis
- Uses tools for event scanning
- Provides REST API for recommendations
- Learning system tracks feedback

---

### 1.4 Analytics Specialist
**Component:** analytics-specialist
- **Path:** `/infrastructure/AI-office-infrastructure/analytics-specialist`
- **Type:** service
- **Port:** 8051
- **Status:** stopped (not running)
- **Main File:** `/infrastructure/AI-office-infrastructure/analytics-specialist/main.py`

**Purpose:**
- 6th AI Colleague in AI Office - Platform Intelligence Expert
- Analyzes platform health (processes, metrics, dependencies)
- Detects bottlenecks, conflicts, and anomalies
- Generates insights and recommendations
- Reports to MIO Manager for coordination
- Provides context to AI Orchestrator for decision-making

**Dependencies:**
- FastAPI
- MIOManagerClient
- ProcessAnalyticsClient (internal)
- Tools: metrics_discovery, dependency_mapper

**Integration Points:**
- ✅ MIO Manager (port 8046) - reports to, sends heartbeat
- ⚠️ Process Analytics (configured but not verified)
- ⚠️ AI Orchestrator (coordinates with)
- ⚠️ Agent Router (coordinates with)
- ⚠️ Project Agent (coordinates with)

**Background Tasks:**
- Daily health check (09:00, configurable)
- Continuous improvement scan (every hour, configurable)
- Heartbeat to MIO (every 5 minutes)

**Notes:**
- **Competency Levels:** junior → middle → senior → expert
- Web UI for tools management at /ui
- Provides platform-wide intelligence

---

### 1.5 DevOps Agent
**Component:** devops-agent
- **Path:** `/infrastructure/AI-office-infrastructure/devops-agent`
- **Type:** service
- **Port:** 8060
- **Status:** stopped (not running)
- **Main File:** `/infrastructure/AI-office-infrastructure/devops-agent/api/main.py`

**Purpose:**
- AI Digital Colleague for DevOps operations
- Infrastructure scanning and monitoring
- Issue detection and automated fixes
- Report generation

**Dependencies:**
- FastAPI
- DevOpsAgent (internal agent class)
- RAG pipeline
- LLM
- EventBus
- Workflow Intelligence

**Integration Points:**
- ⚠️ RAG pipeline (for context)
- ⚠️ LLM (for analysis)
- ⚠️ EventBus (for events)
- ⚠️ Workflow Intelligence (for coordination)

**Capabilities:**
- Full infrastructure scans (events, containers, deployments)
- Report management (latest, history)
- Statistics tracking (scans, issues, fixes)

**Notes:**
- REST API for trigger scans
- Stores statistics in agent instance
- Integration status checked on /status endpoint

---

### 1.6 Agent Router
**Component:** agent-router
- **Path:** `/infrastructure/AI-office-infrastructure/agent-router`
- **Type:** library
- **Port:** N/A
- **Status:** no-main (library component)
- **Main File:** None

**Purpose:**
- Routes requests to appropriate AI agents
- Coordinates between different agent types
- Load balancing and failover

**Dependencies:**
- N/A (requirements.txt exists)

**Integration Points:**
- ⚠️ Multiple AI agents
- ⚠️ AI Orchestrator

**Notes:**
- Has docker-compose.yml
- Configuration-based routing

---

### 1.7 Project Agent
**Component:** project-agent
- **Path:** `/infrastructure/AI-office-infrastructure/project-agent`
- **Type:** tool/CLI
- **Port:** N/A
- **Status:** no-main (CLI tool)
- **Main File:** None (CLI via `agent/cli.py`)

**Purpose:**
- Project analysis and compliance checking
- BPMN/YAML processing
- Changelog generation
- Documentation synchronization
- Domain detection
- Code indexing
- Quality, security, testing modules

**Dependencies:**
- CLI framework
- BPMN/YAML parsers
- Domain detector
- Quality/security/testing analyzers

**Integration Points:**
- 📁 Local filesystem (project scanning)
- 📄 Documentation systems
- ⚠️ Version control (git)

**Notes:**
- Installable package (setup.py, setup.cfg)
- Test project included at `test-project/`
- Generates reports in JSON/Markdown

---

### 1.8 Orchestrator
**Component:** orchestrator
- **Path:** `/infrastructure/AI-office-infrastructure/orchestrator`
- **Type:** library
- **Port:** N/A
- **Status:** no-main (library component)
- **Main File:** None

**Purpose:**
- Workflow execution and coordination
- Task scheduling
- Service orchestration

**Dependencies:**
- N/A

**Integration Points:**
- ⚠️ All managed services
- ⚠️ MIO Manager

**Notes:**
- Has executors/ subdirectory
- Core orchestration logic

---

### 1.9 AI Office Summary Dashboard
**Component:** ai-office (potential)
- **Path:** Not found as separate service
- **Status:** Distributed across components above
- **Notes:** The "AI Office" appears to be a conceptual grouping of the above services rather than a single service.

---

## II. DATABASE INFRASTRUCTURE (5 Components)
> Centralized data storage and caching

### 2.1 PostgreSQL (Supabase)
**Component:** postgresql
- **Path:** `/infrastructure/database/postgresql`
- **Type:** database
- **Port:** 5432 (Supabase-hosted)
- **Status:** running (cloud-hosted)
- **Main File:** N/A (managed service)

**Purpose:**
- Primary relational database for entire platform
- Multi-tenant with RLS (Row-Level Security)
- 29 schemas, 43 migrations applied

**Schemas:**
- Core: public, core, core_auth, auth, extensions, graphql (6)
- BCM Modules: bcm, bia, risk, governance, compliance, validation (6)
- Intelligent Core: intelligence, workflow_intelligence, domain_intelligence, learning, workflow, community (6)
- Domains: response, simulation, portal, marketplace, seh (5)
- System: vault, audit, storage, realtime, extensions, graphql_public (6)

**Dependencies:**
- Supabase cloud platform

**Integration Points:**
- ✅ All platform services (universal dependency)
- ✅ DB Intelligence (monitoring)
- ✅ Supabase Auth
- ✅ Supabase Storage
- ✅ Supabase Realtime

**Managers:**
- DatabaseManager (`managers/db_manager.py`) - connection pooling, RLS
- SupabaseManager (`managers/supabase_client.py`) - Supabase client wrapper

**Notes:**
- **URL:** `postgresql://postgres.xxx:password@aws-1-eu-north-1.pooler.supabase.com:5432/postgres`
- Production ready, 100% coverage
- See `/infrastructure/database/README.md` for details

---

### 2.2 Qdrant Vector Database
**Component:** vector-db
- **Path:** `/infrastructure/database/vector-db`
- **Type:** vector database
- **Port:** 6333 (cloud-hosted)
- **Status:** running (cloud-hosted in eu-west-1)
- **Main File:** N/A (managed service)

**Purpose:**
- Vector embeddings storage for RAG (Retrieval-Augmented Generation)
- Semantic search
- AI memory and knowledge base

**Collections:**
1. **knowledge_base** (1536 dims) - ISO standards, best practices, domain knowledge
2. **workflow_cases** (1536 dims) - Historical workflows, case studies, process templates
3. **ai_memory** (1536 dims) - Agent memory, conversation history, context retention

**Dependencies:**
- OpenAI text-embedding-3-small (embedding model)

**Integration Points:**
- ✅ AI Foundation (RAG pipeline)
- ✅ Workflow Intelligence (case search)
- ✅ Expertise Center (knowledge retrieval)

**Client:**
- QdrantVectorDB (`qdrant/client.py`)
- Config: `qdrant/config.py`
- Init script: `qdrant/init_collections.py`

**Notes:**
- **URL:** `https://xxx.eu-west-1-0.aws.cloud.qdrant.io`
- Production ready
- See `/infrastructure/database/vector-db/README.md`

---

### 2.3 Redis Cache
**Component:** redis
- **Path:** `/infrastructure/database/redis`
- **Type:** in-memory cache
- **Port:** 6379 (local Docker) + Upstash backup
- **Status:** running (Docker container: platform-redis)
- **Main File:** N/A (Docker service)

**Purpose:**
- Session storage
- Rate limiting
- Cache layer
- EventBus backend
- State storage

**Dependencies:**
- Docker
- Redis image

**Integration Points:**
- ✅ API Gateway (rate limiting, sessions)
- ✅ EventBus (Redis Streams backend)
- ✅ All services (cache layer)
- ✅ Workflow Intelligence (state caching)

**Managers:**
- CacheManager (`postgresql/managers/cache_manager.py`) - key-value storage, TTL
- RateLimiter (`postgresql/managers/rate_limiter.py`) - sliding window rate limiting
- RedisClient (`postgresql/managers/redis_client.py`)

**Deployment:**
- Local: `redis://localhost:6379`
- Upstash backup: `redis://:token@redis-endpoint.upstash.io:port`

**Notes:**
- docker-compose.yml available
- Production ready
- Upstash provides cloud backup

---

### 2.4 RabbitMQ Message Broker
**Component:** rabbitmq (planned)
- **Path:** `/infrastructure/runtime/message-queue`
- **Type:** message broker
- **Port:** 5673 (planned, standard 5672)
- **Status:** configured but not verified running
- **Main File:** N/A (Docker service)

**Purpose:**
- Asynchronous message delivery
- Task queue
- Pub/Sub patterns
- Notification delivery

**Dependencies:**
- Docker
- RabbitMQ image

**Integration Points:**
- ⚠️ Notification Service (email/sms queues)
- ⚠️ EventBus (alternative backend)
- ⚠️ Background tasks

**Manager:**
- RabbitMQManager (`message-queue/rabbitmq_manager.py`)

**Queues (planned):**
- notifications.email
- notifications.sms
- notifications.push
- notifications.webhook

**Notes:**
- README.md exists
- requirements.txt exists
- Not yet production deployed

---

### 2.5 Database Managers (Library)
**Component:** database-managers
- **Path:** `/infrastructure/database/postgresql/managers`
- **Type:** library
- **Port:** N/A
- **Status:** library (imported by services)

**Components:**
- `db_manager.py` - DatabaseManager, connection pooling, transactions, RLS
- `supabase_client.py` - SupabaseManager, Supabase client wrapper
- `cache_manager.py` - CacheManager, Redis cache abstraction
- `rate_limiter.py` - RateLimiter, sliding window rate limiting
- `redis_client.py` - RedisClient, Redis connection
- `session_store.py` - SessionStore, user sessions

**Purpose:**
- Provide unified database access layer
- Abstract connection management
- Handle multi-tenancy via RLS

**Integration Points:**
- ✅ All platform services (universal import)
- ✅ PostgreSQL
- ✅ Redis
- ✅ Supabase

**Notes:**
- Core library, no standalone service
- Well-tested (test files exist)

---

## III. GATEWAY & SECURITY (3 Components)
> API routing, authentication, and security

### 3.1 API Gateway
**Component:** api-gateway
- **Path:** `/infrastructure/gateway/api-gateway`
- **Type:** service
- **Port:** 8000
- **Status:** stopped (not running)
- **Main File:** `/infrastructure/gateway/api-gateway/main.py`

**Purpose:**
- Production-grade API gateway
- JWT authentication
- Redis-based rate limiting
- PostgreSQL audit logging
- Circuit breaker protection
- AI-powered management
- Auto-discovery of services
- Self-healing capabilities

**Protects:** 15 microservices including:
- Coordination Center (8004)
- AI Foundation (8030)
- Workflow Intelligence (8020)
- Community Intelligence (8031)
- BIA, Risk, Compliance services (8012-8014)
- Documents, Response, Validation (8015-8017)
- Governance, Planning, Plans (8018-8020)
- Learning, Community services (8021-8022)
- Monitoring (MIO Manager 8046)
- Notification (8035)

**Dependencies:**
- FastAPI, uvicorn, httpx
- structlog
- prometheus-fastapi-instrumentator
- Redis (rate limiting)
- PostgreSQL (audit logs)

**Middleware:**
- AuthenticationMiddleware (JWT)
- RateLimitMiddleware (Redis)
- AuditLogMiddleware (PostgreSQL)
- SecurityHeadersMiddleware
- RequestIDMiddleware
- CORS

**Configuration:** `config.py`
- JWT settings
- Redis URL
- Database URL
- Rate limits (100 req/60s, VIP 500 req/60s)
- Circuit breaker settings
- Backend service mapping
- AI Manager integration (port 8032)
- Health check settings
- Security headers

**Integration Points:**
- ✅ Redis (rate limiting, caching)
- ✅ PostgreSQL (audit logs)
- ✅ AI Manager (port 8032) - intelligent management
- ✅ Service Discovery - auto-discovery of backends
- ✅ Health Checker - monitors backend health
- ✅ Prometheus - metrics at /metrics
- ⚠️ Auth Service (port 8001) - authentication

**Routing:**
- ServiceRouter (`routing/router.py`) - routes to backend services
- HealthChecker (`routing/health_checker.py`) - backend health monitoring
- LoadBalancer (`routing/load_balancer.py`)

**Endpoints:**
- `/health` - gateway health check
- `/api/v1/gateway/ai/analyze` - AI analysis
- `/api/v1/gateway/ai/optimize` - AI optimization
- `/api/v1/gateway/services` - service discovery
- `/{path:path}` - proxy to backend services
- `/docs`, `/redoc` - API documentation

**Notes:**
- **Version:** 1.0.0
- Production-ready
- Self-healing via AI Manager
- Comprehensive middleware stack
- See README.md for details

---

### 3.2 Auth Service
**Component:** auth-service
- **Path:** `/infrastructure/security/auth`
- **Type:** service
- **Port:** 8001
- **Status:** stopped (not running)
- **Main File:** `/infrastructure/security/auth/main.py`

**Purpose:**
- Standalone authentication service
- JWT token generation and validation
- User signup and login
- Supabase Auth integration

**Dependencies:**
- FastAPI
- JWT (python-jose)
- bcrypt
- Supabase client

**Integration Points:**
- ✅ Supabase Auth - backend authentication
- ✅ PostgreSQL - user data
- ⚠️ API Gateway - used by gateway for auth
- ⚠️ All services - token validation

**Endpoints:**
- `/health` - health check
- `/auth/login` - user login (returns JWT)
- `/auth/signup` - user signup
- `/auth/me` - get current user info
- `/auth/logout` - logout user

**Configuration:**
- JWT_SECRET_KEY (required)
- JWT_ALGORITHM (HS256)
- JWT_EXPIRE_MINUTES (1440 = 24 hours)
- SUPABASE_URL
- SUPABASE_SERVICE_KEY
- CORS_ORIGINS

**Notes:**
- **Version:** 1.0.0
- Production ready
- Minimal dependencies (standalone)
- Uses Supabase for user management

---

### 3.3 Secrets Manager (Library)
**Component:** secrets-manager
- **Path:** `/infrastructure/security/secrets-manager`
- **Type:** library
- **Port:** N/A
- **Status:** library (not a service)

**Purpose:**
- HashiCorp Vault integration
- Secret storage and retrieval
- Credential management

**Dependencies:**
- hvac (HashiCorp Vault client)

**Integration Points:**
- ⚠️ All services (for credential access)
- ⚠️ HashiCorp Vault server

**Files:**
- `vault_manager.py` - VaultManager class
- `requirements.txt`

**Notes:**
- README.md exists
- Not currently running as service
- Used by services for secrets

---

## IV. RUNTIME SERVICES (3 Components)
> Real-time communications and service discovery

### 4.1 Real-time WebSocket Service
**Component:** realtime-websocket
- **Path:** `/infrastructure/runtime/realtime-websocket`
- **Type:** service
- **Port:** 8050 (default, configurable)
- **Status:** stopped (not running)
- **Main File:** `/infrastructure/runtime/realtime-websocket/main.py`

**Purpose:**
- Real-time WebSocket communications
- Live updates and collaborative features
- Chat messaging
- Notification broadcasting
- User presence tracking

**Dependencies:**
- FastAPI
- WebSocket
- SQLAlchemy (PostgreSQL)
- Redis (async)
- Pydantic

**Database Models:**
- ChatMessage - chat history
- UserSession - active sessions
- NotificationLog - notification tracking

**Message Types:**
- user_message
- system_notification
- process_update
- incident_alert
- status_change
- heartbeat
- user_joined, user_left
- typing
- file_upload

**Channel Types:**
- general
- incidents
- processes
- alerts
- training
- compliance
- private

**Integration Points:**
- ✅ PostgreSQL - message storage, sessions
- ✅ Redis - message caching (optional)
- ⚠️ Frontend - WebSocket clients

**Endpoints:**
- `/health` - health check
- `/ws/{channel_id}` - WebSocket connection
- `/api/v1/notifications/broadcast` - broadcast notification
- `/api/v1/channels/{channel_id}/users` - channel users
- `/api/v1/channels/{channel_id}/messages` - message history
- `/api/v1/stats` - real-time statistics
- `/` - test page (HTML)

**Features:**
- ConnectionManager - manages WebSocket connections
- Per-user connection limits (default 5)
- Message retention (24 hours in Redis)
- Broadcast to channel or specific users
- Typing indicators
- Heartbeat mechanism

**Configuration:**
- DATABASE_URL (PostgreSQL)
- REDIS_URL or UPSTASH_REDIS_URL
- MAX_CONNECTIONS_PER_USER (5)
- MESSAGE_RETENTION_HOURS (24)

**Notes:**
- **Version:** 1.0.0
- Production ready
- Redis optional (degrades gracefully)
- Test UI included

---

### 4.2 Service Discovery
**Component:** service-discovery
- **Path:** `/infrastructure/runtime/service-discovery`
- **Type:** library
- **Port:** N/A
- **Status:** library (not a service)

**Purpose:**
- Service registration and discovery
- Health monitoring
- Load balancing
- ISO service mapping

**Files:**
- `service_registry.py` - ServiceRegistry class
- `health_monitor.py` - HealthMonitor
- `iso_service_map.py` - ISO standards mapping

**Dependencies:**
- Python standard library

**Integration Points:**
- ⚠️ API Gateway - service discovery
- ⚠️ All services - registration
- ⚠️ Health monitoring systems

**Notes:**
- README.md exists
- Core library for service mesh

---

### 4.3 Message Queue (RabbitMQ)
**Component:** message-queue
- **Path:** `/infrastructure/runtime/message-queue`
- **Type:** library/service
- **Port:** 5673 (configured)
- **Status:** library (Docker service planned)

**Purpose:**
- RabbitMQ integration
- Asynchronous messaging
- Task queuing

**Files:**
- `rabbitmq_manager.py` - RabbitMQManager class
- `requirements.txt`

**Dependencies:**
- pika (RabbitMQ client)

**Integration Points:**
- ⚠️ Notification Service - delivery queues
- ⚠️ Background workers

**Notes:**
- README.md exists
- Container: platform-rabbitmq (planned)

---

## V. OBSERVABILITY (2 Components)
> Monitoring, logging, and alerting

### 5.1 Notification Service
**Component:** notification-service
- **Path:** `/infrastructure/observability/notification-service`
- **Type:** service
- **Port:** 8035
- **Status:** stopped (not running)
- **Main File:** `/infrastructure/observability/notification-service/main.py`

**Purpose:**
- Multi-channel notification delivery
- Email, SMS, Push, Webhook notifications
- Notification history and statistics
- Async delivery via RabbitMQ

**Dependencies:**
- FastAPI
- Supabase (PostgreSQL) - notification history
- Redis - caching and queues
- RabbitMQ (optional) - async processing
- Prometheus client - metrics
- SMTP (email), SMS gateway, push providers

**Integration Points:**
- ✅ Supabase PostgreSQL - notification logs
- ✅ Redis - caching, rate limiting
- ⚠️ RabbitMQ - async delivery queues
- ⚠️ SMTP server - email delivery
- ⚠️ SMS gateway - SMS delivery
- ⚠️ Push notification services
- ✅ Prometheus - metrics at /metrics

**Endpoints:**
- `/health` - health check
- `/email/send` - send email
- `/sms/send` - send SMS
- `/push/send` - send push notification
- `/webhook/send` - send webhook
- `/notifications/history` - notification history
- `/notifications/stats` - statistics
- `/metrics` - Prometheus metrics

**Notification Channels:**
- Email (via SMTP)
- SMS (stub, needs integration)
- Push (stub, needs integration)
- Webhook (stub, needs integration)

**Database Table:** `notifications`
- channel, recipients, message, subject, title
- severity, status, metadata
- created_at, sent_at, updated_at
- error_message

**Configuration:**
- SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
- REDIS_URL
- RABBITMQ_URL (optional)
- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
- PORT (8035)

**Notes:**
- **Version:** 1.0.0
- Gracefully degrades (Supabase optional, RabbitMQ optional)
- Background tasks for async processing
- Prometheus metrics

---

### 5.2 Observability Stack (Prometheus, Grafana, Loki)
**Component:** observability
- **Path:** `/infrastructure/observability`
- **Type:** configuration
- **Port:** Multiple (Prometheus 9090, Grafana 3000, AlertManager 9093, etc.)
- **Status:** configured (docker-compose ready)

**Purpose:**
- Platform-wide monitoring
- Metrics collection (Prometheus)
- Visualization (Grafana)
- Log aggregation (Loki)
- Alerting (AlertManager)

**Components:**
- Prometheus - metrics scraping and storage
- Grafana - dashboards and visualization
- Loki - log aggregation
- Promtail - log shipping
- AlertManager - alert routing
- Blackbox Exporter - endpoint monitoring

**Configuration Files:**
- `config/prometheus/prometheus.yml` - scrape configs
- `config/alertmanager/alertmanager.yml` - alert routing
- `config/grafana/` - Grafana config
- `config/loki/loki-config.yaml` - Loki config
- `config/promtail/promtail-config.yaml` - log collection
- `docker-compose.monitoring.yml` - Docker Compose

**Dashboards:**
- `dashboards/` - Grafana dashboard definitions
- `grafana/dashboards/` - Additional dashboards

**Exporters:**
- `exporters/` - Custom Prometheus exporters (Python)
- `exporters/requirements.txt`

**Scripts:**
- `scripts/` - Automation scripts

**Integration Points:**
- ✅ All services - metrics endpoints
- ✅ Docker containers - log collection
- ✅ AlertManager - alert notifications

**Notes:**
- Complete monitoring stack
- Ready for deployment
- See docker-compose.monitoring.yml

---

## VI. INTEGRATION SERVICES (3 Components)
> External integrations and protocols

### 6.1 GitHub Integration
**Component:** github-integration
- **Path:** `/infrastructure/integration/github-integration`
- **Type:** service
- **Port:** 8001 (conflicts with auth service!)
- **Status:** stopped (not running)
- **Main File:** `/infrastructure/integration/github-integration/main.py`

**Purpose:**
- GitHub App webhooks
- GitHub Copilot Extension token exchange
- Proxy endpoints for GitHub Copilot Skills

**Dependencies:**
- FastAPI
- httpx (HTTP client)

**Integration Points:**
- ⚠️ GitHub webhooks
- ⚠️ GitHub Copilot
- ⚠️ AI Orchestrator (proxies to port 8000)

**Endpoints:**
- `/` - service info
- `/github/webhook` - GitHub webhook handler
- `/auth/token-exchange` - Copilot token exchange
- `/claude/analyze-changes` - proxy to AI Orchestrator
- `/claude/generate-config` - proxy to AI Orchestrator
- `/deployment/history` - proxy to AI Orchestrator
- `/claude/analyze-deployment` - proxy to AI Orchestrator
- `/deployment/orchestrate` - proxy to AI Orchestrator

**Configuration:**
- GITHUB_APP_ID

**Notes:**
- **Version:** 1.0.0
- Port conflict with auth service (both 8001)
- Proxies GitHub Copilot requests to ai_orchestrator
- README.md, Dockerfile exist

---

### 6.2 MCP Server (Model Context Protocol)
**Component:** mcp-server
- **Path:** `/infrastructure/integration/mcp-server`
- **Type:** service
- **Port:** N/A (protocol server)
- **Status:** library/service (not verified running)

**Purpose:**
- Model Context Protocol implementation
- BCM Collective MCP integration
- AI agent coordination protocol

**Files:**
- `bcm_collective_mcp.py` - MCP server implementation
- `requirements.txt`

**Dependencies:**
- MCP SDK

**Integration Points:**
- ⚠️ AI agents
- ⚠️ BCM Collective

**Notes:**
- README.md exists
- Specialized protocol for AI coordination

---

### 6.3 Partisia Contracts (Blockchain)
**Component:** partisia-contracts
- **Path:** `/infrastructure/integration/partisia-contracts`
- **Type:** smart contracts
- **Port:** N/A
- **Status:** smart contract code

**Purpose:**
- Blockchain smart contracts
- Collective intelligence on Partisia blockchain
- Decentralized coordination

**Files:**
- `collective_intelligence.pbc` - Partisia smart contract

**Integration Points:**
- ⚠️ Partisia blockchain
- ⚠️ Collective intelligence system

**Notes:**
- README.md exists
- Advanced feature, not core infrastructure

---

## VII. EVENTBUS (1 Component)
> Event-driven architecture foundation

### 7.1 EventBus System
**Component:** eventbus
- **Path:** `/infrastructure/eventbus`
- **Type:** library + catalog
- **Port:** N/A (library, uses Redis 6379 or in-memory)
- **Status:** library (imported by services)

**Purpose:**
- Clean architecture event system
- Pluggable backend (memory, Redis Streams, RabbitMQ planned)
- Type-safe events
- Wildcard subscriptions
- Consumer groups (load balancing)
- Automatic retry logic

**Structure:**
- `core/` - Event model, IEventBus interface
  - `events.py` - Event class, EventPriority
  - `interface.py` - IEventBus abstract base
- `backends/` - Backend implementations
  - `memory.py` - In-memory backend (MVP, testing)
  - `redis_streams.py` - Redis Streams backend (production)
- `factory.py` - create_eventbus()
- `config.py` - Configuration
- `subscribers/` - Subscriber base classes
  - `base.py` - BaseSubscriber
- `examples/` - Usage examples
- `tests/` - Unit tests
- `event-catalog/` - EventCatalog UI (Node.js app)
- `events/` - Event definitions and visualizer

**Dependencies:**
- redis (for Redis backend)
- pydantic (for Event model)

**Integration Points:**
- ✅ Redis Streams - production backend
- ✅ MIO Manager - event subscriptions
- ✅ AI Event Manager - event publishing
- ✅ DevOps Agent - event coordination
- ⚠️ All services - potential subscribers

**Event Model:**
- Event class with id, type, data, source, timestamp
- EventPriority: LOW, NORMAL, HIGH, CRITICAL
- Metadata: tenant_id, correlation_id, retry_count, max_retries

**Backends:**
- **Memory:** Zero dependencies, instant startup, single process only
- **Redis Streams:** Persistence, consumer groups, ACK mechanism, multi-process
- **RabbitMQ:** Planned

**Features:**
- Wildcard subscriptions (`workflow.*`, `*`)
- Consumer groups (load balancing)
- Automatic retry with exponential backoff
- Event serialization (to_dict, from_dict)
- Statistics (published, consumed, errors)

**Event Catalog:**
- Node.js application for event visualization
- Located at `event-catalog/`
- Interactive documentation

**Notes:**
- **Architecture:** Clean, backend-agnostic
- Production-ready with Redis Streams
- Comprehensive README.md
- Well-tested

---

## VIII. TOOLS & AUTOMATION (6 Components)
> Development tools, analyzers, and automation

### 8.1 Automation Toolkit (Analyzers)
**Component:** analyzers
- **Path:** `/infrastructure/tools/analyzers`
- **Type:** tool library
- **Port:** N/A
- **Status:** library (CLI tools)

**Purpose:**
- AST analysis (functions, classes, endpoints)
- Dependency mapping
- Code complexity analysis (Radon)
- Security scanning (Bandit)
- Quality analysis (Pylint)

**Tools:**
- `ast_analyzer.py` - extract functions, classes, API endpoints
- `dependency_mapper.py` - build dependency graph, detect circular deps

**Reports Generated:**
- `reports/ast_analysis.json` - JSON data
- `reports/ast_analysis.md` - Markdown report
- `reports/dependencies.json` - dependency list
- `reports/dependencies.md` - dependency report
- `reports/dependency_graph.png` - graph visualization
- `reports/dependency_graph.graphml` - Gephi/Cytoscape format
- `reports/circular_dependencies.json` - circular deps
- `reports/security_scan.json` - Bandit results
- `reports/pylint_report.json` - Pylint results

**Configuration:**
- `config/analysis_config.yaml`

**Integration Points:**
- ⚠️ MIO Manager (uses for platform analysis)
- 📁 Codebase (scans filesystem)

**Notes:**
- README.md comprehensive
- See `/infrastructure/tools/README.md`
- Requires: radon, pylint, bandit, networkx, matplotlib, plotly

---

### 8.2 Doc Generators
**Component:** doc-generators
- **Path:** `/infrastructure/tools/doc-generators`
- **Type:** tool library
- **Port:** N/A
- **Status:** library (CLI tools)

**Purpose:**
- API documentation generation from OpenAPI
- UI blueprint generation
- Markdown documentation
- Postman collections

**Tools:**
- `api_docs_generator.py` - Markdown from OpenAPI specs
- `ui_blueprint_gen.py` - UI blueprints for frontend

**Generated Docs:**
- `docs/api/` - API documentation
  - `README.md` - index
  - `{service}.md` - per-service docs
  - `postman_collection.json` - Postman import
- `docs/ui/` - UI blueprints
  - `index.html` - navigation
  - `{service}_blueprint.html` - UI screens
  - `{service}_spec.json` - JSON specifications

**Integration Points:**
- 📄 Running services (fetches OpenAPI specs)
- 📁 Filesystem (writes documentation)

**Notes:**
- Generates UI screens: List, Create, Detail, Edit, Custom Actions
- Comprehensive README.md

---

### 8.3 Dashboards
**Component:** dashboards
- **Path:** `/infrastructure/tools/dashboards`
- **Type:** tool library
- **Port:** N/A
- **Status:** library (generates HTML)

**Purpose:**
- Interactive visualization of platform metrics
- Dependency network graphs
- Endpoint maps
- Module statistics

**Tools:**
- `module_dashboard.py` - generates 3 HTML dashboards

**Generated Dashboards:**
- `reports/dashboard.html` - general statistics
- `reports/endpoint_map.html` - Sunburst diagram of endpoints
- `reports/dependency_network.html` - interactive network graph

**Dependencies:**
- Plotly (interactive charts)

**Integration Points:**
- 📊 Analyzer reports (reads JSON)
- 🌐 Browser (opens HTML)

**Notes:**
- Requires AST and dependency analysis to run first

---

### 8.4 Docker Management
**Component:** docker-management
- **Path:** `/infrastructure/tools/docker-management`
- **Type:** library
- **Port:** N/A
- **Status:** library

**Purpose:**
- Docker container management
- Service orchestration
- Container lifecycle

**Files:**
- `docker_manager.py` - DockerManager class
- `__init__.py`

**Integration Points:**
- 🐳 Docker daemon
- ⚠️ MIO Manager (uses for service management)

**Notes:**
- README.md exists

---

### 8.5 VS Code Extension
**Component:** vscode-extension
- **Path:** `/infrastructure/tools/vscode-extension`
- **Type:** IDE extension
- **Port:** N/A
- **Status:** development/planned

**Purpose:**
- VS Code integration
- Code snippets
- Platform navigation
- Developer tools

**Notes:**
- README.md exists
- Development tooling

---

### 8.6 Auto-Generated Configs
**Component:** auto-generated
- **Path:** `/infrastructure/tools/auto-generated`
- **Type:** configuration
- **Port:** N/A
- **Status:** generated files

**Purpose:**
- Auto-generated Docker Compose files
- Service configuration
- Infrastructure as Code

**Files:**
- `docker-generated/` - multiple docker-compose files
  - `docker-compose.gateway.yml`
  - `docker-compose.observability.yml`
  - `docker-compose.integration.yml`
  - `docker-compose.full.yml`
  - `docker-compose.runtime.yml`
- `auto-generated/` - improved configs
  - `docker-compose.auto.yml`
  - `docker-compose.improved.yml`

**Integration Points:**
- 🐳 Docker Compose
- 📁 Infrastructure deployment

**Notes:**
- Generated by automation scripts
- See `/infrastructure/docker-compose.full-infrastructure.yml`

---

## IX. DEPRECATED (1 Component)

### 9.1 Unified Database Gateway (DEPRECATED)
**Component:** unified_database_gateway
- **Path:** `/infrastructure/gateway/_deprecated_unified_database_gateway`
- **Type:** service (deprecated)
- **Port:** N/A
- **Status:** deprecated (replaced by API Gateway)
- **Main File:** `main.py`

**Purpose:**
- Old unified database access gateway
- Replaced by current API Gateway + database managers

**Notes:**
- **DO NOT USE**
- Kept for reference only
- Use `/infrastructure/gateway/api-gateway` instead

---

## Summary Tables

### Services by Port

| Port | Service | Status | Integration |
|------|---------|--------|-------------|
| 5432 | PostgreSQL (Supabase) | ✅ Running (cloud) | ✅ Fully integrated |
| 6333 | Qdrant Vector DB | ✅ Running (cloud) | ✅ Fully integrated |
| 6379 | Redis | ✅ Running (Docker) | ✅ Fully integrated |
| 5673 | RabbitMQ | ⚠️ Configured | ⚠️ Partially integrated |
| 8000 | API Gateway | ⏸️ Stopped | ⚠️ Partially integrated |
| 8001 | Auth Service | ⏸️ Stopped | ⚠️ Partially integrated |
| 8001 | GitHub Integration | ⏸️ Stopped (port conflict!) | ❌ Not integrated |
| 8020 | Workflow Intelligence | ✅ Running | ✅ Fully integrated |
| 8035 | Notification Service | ⏸️ Stopped | ⚠️ Partially integrated |
| 8046 | MIO Manager | ⏸️ Stopped | ✅ Fully integrated |
| 8050 | DB Intelligence | ⏸️ Stopped | ✅ Fully integrated |
| 8050 | Real-time WebSocket | ⏸️ Stopped (port conflict!) | ⚠️ Partially integrated |
| 8051 | Analytics Specialist | ⏸️ Stopped | ⚠️ Partially integrated |
| 8055 | AI Event Manager | ⏸️ Stopped | ⚠️ Partially integrated |
| 8060 | DevOps Agent | ⏸️ Stopped | ⚠️ Partially integrated |

### Port Conflicts Detected
- **Port 8001:** Auth Service vs GitHub Integration
- **Port 8050:** DB Intelligence vs Real-time WebSocket

### Not Integrated Components (15)

1. **Agent Router** - library, no active integration
2. **Project Agent** - CLI tool, filesystem only
3. **Orchestrator** - library, no active service
4. **RabbitMQ** - configured but not verified
5. **Secrets Manager** - library, not actively used
6. **Service Discovery** - library, not actively used
7. **Message Queue** - library, not actively used
8. **GitHub Integration** - stopped, port conflict
9. **MCP Server** - not verified running
10. **Partisia Contracts** - blockchain, not core infra
11. **Docker Management** - library
12. **VS Code Extension** - development only
13. **Auto-Generated Configs** - generated files
14. **Deprecated Gateway** - do not use
15. **Analyzers/Tools** - CLI tools, not services

### Recommendations

#### Critical Issues
1. **Port Conflicts:**
   - Change GitHub Integration to different port (suggest 8002)
   - Change Real-time WebSocket to different port (suggest 8053)

2. **Start Core Services:**
   - Start API Gateway (port 8000) - critical for platform
   - Start Auth Service (port 8001) - required by gateway
   - Start MIO Manager (port 8046) - platform monitoring hub
   - Start DB Intelligence (port 8050) - database monitoring

3. **Verify Infrastructure:**
   - Confirm RabbitMQ is running (port 5673)
   - Test Redis connection (port 6379)

#### Integration Gaps
1. **MCP Server** - verify if needed, document integration
2. **Service Discovery** - integrate with API Gateway
3. **Secrets Manager** - integrate with services for credentials
4. **RabbitMQ** - complete integration with Notification Service

#### Documentation Needs
1. Service startup order
2. Environment variable consolidation
3. Dependency mapping between services
4. Health check endpoints registry

---

**Report Generated:** 2025-10-08
**Analysis Tool:** Claude Code Agent
**Infrastructure Version:** Mixed (1.0.0 - 2.0)
