# 🏢 AI Platform ISO - Comprehensive Service Catalog

**Version:** 3.0.0
**Generated:** 2025-10-11T02:32:11.970266Z
**Total Services:** 41
**Categories:** 9

---

## 📊 Executive Summary

This comprehensive catalog documents all **47 services** in the AI Platform ISO ecosystem, 
implementing ISO 22301:2019 Business Continuity Management standards with advanced AI capabilities.

### Platform Statistics

| Metric | Value |
|--------|-------|
| **Total Services** | 41 |
| **Active Services** | 30 |
| **Service Categories** | 9 |
| **Services with Ports** | 38 |

### Services by Category

| Category | Services | Description |
|----------|----------|-------------|
| Database Infrastructure | 4 | N/A... |
| Runtime Services | 3 | N/A... |
| Gateway Layer | 1 | N/A... |
| Observability | 2 | N/A... |
| EventBus Core | 1 | N/A... |
| Security | 2 | N/A... |
| AI Office | 6 | N/A... |
| Platform Services | 10 | N/A... |
| Intelligent Core | 12 | N/A... |

---

## 📑 Table of Contents

1. [Database Infrastructure](#database-infrastructure) (4 services)
2. [Runtime Services](#runtime-services) (3 services)
3. [Gateway Layer](#gateway-layer) (1 services)
4. [Observability](#observability) (2 services)
5. [EventBus Core](#eventbus-core) (1 services)
6. [Security](#security) (2 services)
7. [AI Office](#ai-office) (6 services)
8. [Platform Services](#platform-services) (10 services)
9. [Intelligent Core](#intelligent-core) (12 services)

---

## Database Infrastructure
<a name="database-infrastructure"></a>

**Services:** 4

### Unified Database Access Layer

| Property | Value |
|----------|-------|
| **Service ID** | `database-managers` |
| **Version** | N/A |
| **Type** | library |
| **Status** | PRODUCTION |
| **Port** | `None` |
| **Framework** | N/A |

**Description:**

> Centralized database access library providing unified API for all database operations across the platform.

**Key Capabilities:**

- Unified database API
- Connection pooling
- Session management (Redis-based)
- Caching layer (decorator-based)
- Rate limiting (multi-strategy)
- RLS management

**Features:**

- SupabaseManager - PostgreSQL + Auth + Storage
- DatabaseManager - Sync connections, migrations
- RedisClient - Async Redis operations
- CacheManager - @cached() decorator
- RateLimiter - @rate_limit() decorator
- *...and 1 more*

**Required Dependencies:**

- PostgreSQL/Supabase
- Redis

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| ALL microservices | import | Used by every service for database acces... |
| FastAPI services | dependency_injection | get_db_session_dependency()... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| cache_hit_rate | gauge | 80 | `N/A` |
| rate_limit_blocked_total | counter | N/A | `N/A` |

---

### BCM Platform Database (PostgreSQL via Supabase)

| Property | Value |
|----------|-------|
| **Service ID** | `postgresql` |
| **Version** | N/A |
| **Type** | database |
| **Status** | PRODUCTION |
| **Port** | `5432` |
| **Framework** | N/A |

**Description:**

> Primary relational database for the entire AI-powered BCM platform. Provides 29 schemas for modular architecture with Row-Level Security (RLS) for multi-tenancy. Manages all business data, user profiles, workflows, and system state.

**Key Capabilities:**

- 29 database schemas (System, Platform, Business)
- 46 applied migrations
- Row-Level Security (RLS) for multi-tenancy
- Full BCM business logic (BIA, Risk, Governance, Compliance)
- AI memory and learning data
- Workflow orchestration state
- Audit logging and event sourcing

**Features:**

- PostgreSQL 14+ with extensions
- Connection pooling via Supabase
- Automatic backups
- Point-in-time recovery
- Real-time subscriptions (Supabase Realtime)

**Required Dependencies:**

- Supabase Cloud Platform
- PostgreSQL extensions: uuid-ossp, pg_stat_statements, pg_trgm, btree_gist

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| All platform services | database_manager | Universal database access via DatabaseMa... |
| DB Intelligence (8051) | monitoring | Performance monitoring and optimization... |
| Workflow Intelligence | dedicated_schema | workflow_intelligence schema... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| db_connections_active | gauge | 80 | `N/A` |
| db_query_duration_ms | histogram | N/A | `N/A` |
| db_table_size_bytes | gauge | N/A | `N/A` |
| db_cache_hit_rate | gauge | 95 | `N/A` |

---

### BCM Vector Search (Qdrant Cloud)

| Property | Value |
|----------|-------|
| **Service ID** | `qdrant` |
| **Version** | N/A |
| **Type** | vector_database |
| **Status** | PRODUCTION |
| **Port** | `443` |
| **Framework** | N/A |

**Description:**

> Vector database for semantic search, RAG (Retrieval-Augmented Generation), case library, and AI agent memory.

**Key Capabilities:**

- RAG document retrieval
- Semantic search across workflow cases
- Knowledge graph similarity search
- Long-term memory for AI agents

**Features:**

- 3 collections: knowledge_base, workflow_cases, ai_memory
- 1536-dimensional vectors (OpenAI ada-002)
- Cosine distance metric
- Cloud-managed (Qdrant Cloud)

**Required Dependencies:**

- Qdrant Cloud account
- OpenAI API (for embeddings)

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| RAG Connector | search | Document retrieval for LLM context... |
| Case Library | semantic_search | Find similar workflow cases... |
| AI Orchestrator | context_retrieval | Context for AI decision-making... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| vector_db_search_duration_ms | histogram | N/A | `N/A` |
| vector_db_vectors_count | gauge | N/A | `N/A` |
| vector_db_search_results_avg | gauge | N/A | `N/A` |

---

### Platform Redis Cache

| Property | Value |
|----------|-------|
| **Service ID** | `redis` |
| **Version** | N/A |
| **Type** | cache |
| **Status** | RUNNING |
| **Port** | `6379` |
| **Framework** | N/A |

**Description:**

> In-memory data store providing caching, session storage, rate limiting, and pub/sub messaging for the entire platform.

**Key Capabilities:**

- Caching layer (reduce database load)
- Session storage (user sessions)
- Rate limiting (API throttling)
- Service registry (service discovery)
- Pub/Sub messaging (optional EventBus backend)

**Features:**

- Redis 7 Alpine
- LRU eviction policy
- 512MB memory limit
- Async Python client (redis.asyncio)

**Required Dependencies:**

- Docker

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| API Gateway | rate_limiting | Rate limiting and session cache... |
| Auth Service | session_storage | User sessions and token blacklist... |
| All platform services | caching | General-purpose caching... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| redis_connections_active | gauge | N/A | `N/A` |
| redis_memory_used_bytes | gauge | 400000000 | `N/A` |
| redis_cache_hit_rate | gauge | 80 | `N/A` |
| redis_evicted_keys | counter | N/A | `N/A` |

---

---

## Runtime Services
<a name="runtime-services"></a>

**Services:** 3

### Platform Message Queue (RabbitMQ)

| Property | Value |
|----------|-------|
| **Service ID** | `message-queue` |
| **Version** | N/A |
| **Type** | infrastructure/runtime |
| **Status** | PLANNED |
| **Port** | `5672` |
| **Framework** | N/A |

**Description:**

> Asynchronous message queue for task distribution, job processing, and reliable message delivery across microservices.

**Key Capabilities:**

- Task queue management
- Job scheduling and distribution
- Dead letter queue handling
- Message persistence
- Priority queuing
- Retry mechanisms

**Features:**

- RabbitMQ backend
- Multiple queue support
- Fanout/Topic/Direct exchanges
- Message acknowledgment
- Async Python client

**Required Dependencies:**

- RabbitMQ server

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| EventBus | backend | Planned EventBus RabbitMQ backend... |
| Background Jobs | task_queue | Async job processing... |
| Workflow Engine | orchestration | Workflow task distribution... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| queue_messages_total | counter | N/A | `N/A` |
| queue_messages_pending | gauge | N/A | `N/A` |
| queue_processing_duration_ms | histogram | N/A | `N/A` |

---

### Real-time WebSocket Service

| Property | Value |
|----------|-------|
| **Service ID** | `realtime-websocket` |
| **Version** | N/A |
| **Type** | infrastructure/runtime |
| **Status** | RUNNING |
| **Port** | `8050` |
| **Framework** | N/A |

**Description:**

> Real-time communications, live updates, and collaborative features for BCM Platform. Provides WebSocket connections for chat, notifications, and event streaming.

**Key Capabilities:**

- WebSocket connections (multi-user, multi-channel)
- Real-time chat messaging
- System notifications broadcasting
- User presence tracking (online/away/busy)
- Typing indicators
- File upload notifications
- Incident alerts (real-time)
- Process status updates

**Features:**

- Connection pooling (max 5 per user)
- Redis caching (message history)
- PostgreSQL persistence (24h retention)
- Channel-based broadcasting
- User-specific messaging
- *...and 2 more*

**Required Dependencies:**

- PostgreSQL/Supabase - message persistence
- Redis - message caching

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| Admin Control Center UI | websocket_client | Real-time dashboard updates... |
| Incident Management | alerts | Real-time incident notifications... |
| Workflow Engine | status_updates | Workflow progress updates... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| websocket_connections_total | gauge | N/A | `N/A` |
| websocket_unique_users | gauge | N/A | `N/A` |
| websocket_active_channels | gauge | N/A | `N/A` |
| websocket_messages_sent_total | counter | N/A | `N/A` |
| websocket_message_delivery_latency_ms | histogram | N/A | `N/A` |

---

### Service Discovery v2.0 - Unified Catalog + Registry

| Property | Value |
|----------|-------|
| **Service ID** | `service-discovery` |
| **Version** | N/A |
| **Type** | infrastructure/runtime |
| **Status** | RUNNING |
| **Port** | `8500` |
| **Framework** | N/A |

**Description:**

> Complete service discovery, registry, health monitoring, and Service Catalog integration. Provides unified view combining static catalog with dynamic runtime data.

**Key Capabilities:**

- Service Catalog Integration (YAML templates)
- Service Registry (track runtime instances)
- Unified View (merge catalog + registry)
- Health Monitoring (Docker, HTTP, custom)
- ISO 22301 Mapping (12 services)
- Dependency Management
- Event Broadcasting (lifecycle events)
- Consul-compatible API

**Features:**

- 3 health check types: docker, http, custom
- 4 health statuses: HEALTHY, UNHEALTHY, DEGRADED, UNKNOWN
- Heartbeat monitoring (60s timeout)
- Automatic service deregistration

**Required Dependencies:**

- redis.asyncio - Registry persistence
- httpx - HTTP health checks

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| AI DevOps Engine | deployment | Uses for orchestration... |
| MIO Manager | observer | Observes service registrations... |
| Platform Orchestrator | coordination | Service lifecycle management... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| total_services | counter | N/A | `N/A` |
| healthy_services | gauge | N/A | `N/A` |
| coverage_percent | percentage | 100 | `N/A` |
| health_check_response_time | histogram_ms | N/A | `N/A` |

---

---

## Gateway Layer
<a name="gateway-layer"></a>

**Services:** 1

### AI-Powered API Gateway

| Property | Value |
|----------|-------|
| **Service ID** | `api-gateway` |
| **Version** | N/A |
| **Type** | infrastructure/gateway |
| **Status** | PRODUCTION |
| **Port** | `8000` |
| **Framework** | N/A |

**Description:**

> Unified API gateway with intelligent routing, authentication, rate limiting, and AI-powered request optimization.

**Key Capabilities:**

- Unified API entry point (single endpoint)
- JWT authentication & authorization
- Rate limiting (token bucket, sliding window, fixed window)
- Request/response logging & audit
- Load balancing (round-robin, least-connections, weighted)
- Circuit breaker pattern
- API key management
- CORS handling
- Request transformation
- Response caching

**Features:**

- 6-layer middleware stack
- AI-powered route optimization
- Automatic service discovery integration
- Health-based routing
- Metrics collection (Prometheus)
- *...and 1 more*

**Required Dependencies:**

- Service Discovery - route resolution
- Redis - rate limiting & session cache
- PostgreSQL - audit logs

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| All microservices | gateway | Routes all external requests... |
| Auth Service | authentication | JWT validation... |
| Service Discovery | routing | Dynamic service routing... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| gateway_requests_total | counter | N/A | `N/A` |
| gateway_request_duration_ms | histogram | N/A | `N/A` |
| gateway_rate_limit_exceeded_total | counter | N/A | `N/A` |
| gateway_circuit_breaker_open_total | counter | N/A | `N/A` |
| gateway_active_connections | gauge | N/A | `N/A` |

---

---

## Observability
<a name="observability"></a>

**Services:** 2

### Grafana Dashboards

| Property | Value |
|----------|-------|
| **Service ID** | `grafana` |
| **Version** | N/A |
| **Type** | observability/visualization |
| **Status** | PRODUCTION |
| **Port** | `3000` |
| **Framework** | N/A |

**Description:**

> Visualization and analytics platform with 18 pre-configured dashboards for monitoring platform health, services, and business metrics.

**Key Capabilities:**

- Interactive dashboards
- 18 pre-configured dashboards
- Multiple data sources (Prometheus, Loki, PostgreSQL)
- Alerting and notifications
- User management and RBAC

**Features:**

- Platform Overview dashboard
- Service Health dashboard
- Database Performance dashboard
- EventBus Monitoring dashboard
- AI Office Team dashboard

**Required Dependencies:**

- Prometheus - metrics data

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| Prometheus | data_source | N/A... |
| Loki | data_source | N/A... |
| PostgreSQL | data_source | N/A... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| grafana_active_users | gauge | N/A | `N/A` |
| grafana_dashboard_views_total | counter | N/A | `N/A` |

---

### Prometheus Metrics Server

| Property | Value |
|----------|-------|
| **Service ID** | `prometheus` |
| **Version** | N/A |
| **Type** | observability/metrics |
| **Status** | PRODUCTION |
| **Port** | `9090` |
| **Framework** | N/A |

**Description:**

> Time-series database and metrics collection system for platform-wide monitoring. Scrapes metrics from all services and stores them for querying and alerting.

**Key Capabilities:**

- Metrics collection via /metrics endpoints
- Time-series data storage
- PromQL query language
- Alerting rules engine
- Service discovery integration
- Federation support

**Features:**

- 50+ scrape targets configured
- 45 alert rules across 4 categories
- 15-second scrape interval
- 30-day retention period

**Required Dependencies:**

- Service Discovery - target discovery

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| All platform services | metrics_scraping | Scrapes /metrics endpoints... |
| Grafana | data_source | Provides metrics data... |
| AlertManager | alert_routing | Sends alerts... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| prometheus_tsdb_head_samples | gauge | N/A | `N/A` |
| prometheus_target_scrape_duration_seconds | histogram | N/A | `N/A` |

---

---

## EventBus Core
<a name="eventbus-core"></a>

**Services:** 1

### Platform EventBus (Clean Architecture)

| Property | Value |
|----------|-------|
| **Service ID** | `eventbus` |
| **Version** | N/A |
| **Type** | library/event_system |
| **Status** | PRODUCTION |
| **Port** | `None` |
| **Framework** | N/A |

**Description:**

> Clean architecture event system supporting choreography pattern for loosely-coupled microservices communication.

**Key Capabilities:**

- Event publishing and subscription
- Multiple backends (Memory, Redis Streams)
- Event filtering by pattern
- Async/await support
- Type-safe event definitions
- Choreography pattern enforcement

**Features:**

- 217 registered events across 12 domains
- Backend-agnostic design
- Redis Streams backend (production)
- In-memory backend (testing)
- Event replay support

**Required Dependencies:**

- Python 3.11+

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| All microservices | import | Event publishing and subscription... |
| Redis | backend | Redis Streams for persistence... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| eventbus_events_published_total | counter | N/A | `N/A` |
| eventbus_events_consumed_total | counter | N/A | `N/A` |
| eventbus_processing_duration_ms | histogram | N/A | `N/A` |

---

---

## Security
<a name="security"></a>

**Services:** 2

### Authentication & Authorization Service

| Property | Value |
|----------|-------|
| **Service ID** | `auth-service` |
| **Version** | N/A |
| **Type** | security/auth |
| **Status** | PRODUCTION |
| **Port** | `8001` |
| **Framework** | N/A |

**Description:**

> JWT-based authentication and RBAC authorization service for platform-wide access control.

**Key Capabilities:**

- User authentication (JWT tokens)
- Role-Based Access Control (RBAC)
- OAuth2 integration (planned)
- Session management
- Token refresh mechanism
- Password hashing (bcrypt)

**Features:**

- JWT access & refresh tokens
- Multi-role support
- API key management
- Token blacklisting

**Required Dependencies:**

- PostgreSQL - user storage
- Redis - token blacklist

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| API Gateway | authentication | N/A... |
| All services | authorization | N/A... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| auth_login_attempts_total | counter | N/A | `N/A` |
| auth_token_validations_total | counter | N/A | `N/A` |
| auth_failed_logins_total | counter | N/A | `N/A` |

---

### HashiCorp Vault - Secrets Manager

| Property | Value |
|----------|-------|
| **Service ID** | `vault` |
| **Version** | N/A |
| **Type** | security/secrets |
| **Status** | CONFIGURED |
| **Port** | `8200` |
| **Framework** | N/A |

**Description:**

> Centralized secrets management with encryption as a service, dynamic secrets, and audit logging.

**Key Capabilities:**

- Secrets storage (KV v2)
- Dynamic secrets generation
- Encryption as a service
- Audit logging
- Secret rotation
- Access policies

**Features:**

- Database credentials rotation
- API key storage
- Certificate management
- Transit encryption engine

**Required Dependencies:**

- Vault server (HashiCorp Cloud or self-hosted)

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| Auth Service | planned | JWT secret from Vault... |
| Database Managers | planned | Dynamic DB credentials... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| vault_secrets_read_total | counter | N/A | `N/A` |
| vault_audit_logs_total | counter | N/A | `N/A` |

---

---

## AI Office
<a name="ai-office"></a>

**Services:** 6

### Agent Router - Request Routing & Load Balancing

| Property | Value |
|----------|-------|
| **Service ID** | `agent-router` |
| **Version** | N/A |
| **Type** | ai_office/router |
| **Status** | PRODUCTION |
| **Port** | `8057` |
| **Framework** | N/A |

**Description:**

> Intelligent request routing, load balancing, and circuit breaker for AI Office team coordination.

**Key Capabilities:**

- Request routing to AI specialists
- Load balancing
- Circuit breaker pattern
- Health-based routing
- Failover handling

**Features:**

- Round-robin load balancing
- Automatic failover
- Health monitoring

**Required Dependencies:**

- Service Discovery

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| All AI Office services | routing | N/A... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| router_requests_total | counter | N/A | `N/A` |
| router_circuit_breaker_trips_total | counter | N/A | `N/A` |

---

### Analytics Specialist - Platform Intelligence

| Property | Value |
|----------|-------|
| **Service ID** | `analytics-specialist` |
| **Version** | N/A |
| **Type** | ai_office/specialist |
| **Status** | PRODUCTION |
| **Port** | `8056` |
| **Framework** | N/A |

**Description:**

> Platform-wide analytics, metrics discovery, dependency mapping, and bottleneck detection using AI-powered code analysis.

**Key Capabilities:**

- Metrics discovery (scan codebase for metrics)
- Dependency mapping (import analysis)
- API endpoint discovery
- Security scanning (code vulnerabilities)
- Bottleneck detection
- Module structure analysis (AST parsing)
- Platform intelligence aggregation

**Features:**

- AST-based code analysis
- Prometheus metrics validation
- Dependency graph generation
- API mapper (FastAPI routes)
- Security vulnerability scanner

**Required Dependencies:**

- Python AST parser

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| All microservices | code_scanning | Scans code for metrics, dependencies, AP... |
| MIO Manager | intelligence_provider | Provides platform insights... |
| Prometheus | metrics_validation | Validates metrics registration... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| analytics_scans_total | counter | N/A | `N/A` |
| analytics_metrics_discovered_total | counter | N/A | `N/A` |
| analytics_dependencies_mapped_total | counter | N/A | `N/A` |

---

### DB Intelligence - Database Performance Specialist

| Property | Value |
|----------|-------|
| **Service ID** | `db-intelligence` |
| **Version** | N/A |
| **Type** | ai_office/specialist |
| **Status** | PRODUCTION |
| **Port** | `8051` |
| **Framework** | N/A |

**Description:**

> Deep database performance analysis, query optimization, and admin operations for PostgreSQL. AI-powered recommendations using LLM + pg_stat_statements.

**Key Capabilities:**

- Query performance analysis (pg_stat_statements)
- Slow query detection and optimization
- AI-powered index recommendations (LLM)
- Table statistics monitoring (bloat, vacuum status)
- Security monitoring (RLS, SQL injection, deadlocks)
- Admin CLI operations (VACUUM, ANALYZE, REINDEX, CREATE INDEX)
- Connection pool monitoring
- Database health checks

**Features:**

- AI-powered query analysis
- EXPLAIN plan interpretation
- Concurrent index creation
- Automated VACUUM scheduling
- Dead tuple cleanup

**Required Dependencies:**

- PostgreSQL - target database
- pg_stat_statements extension

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| PostgreSQL | monitoring | Deep performance analysis... |
| MIO Manager | metrics_provider | Provides DB-specific metrics... |
| Prometheus | metrics_export | Exports DB performance metrics... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| db_slow_queries_detected_total | counter | N/A | `N/A` |
| db_optimizations_applied_total | counter | N/A | `N/A` |
| db_avg_query_duration_ms | gauge | N/A | `N/A` |
| db_table_bloat_percent | gauge | N/A | `N/A` |

---

### DevOps Agent - Infrastructure & Platform Compliance

| Property | Value |
|----------|-------|
| **Service ID** | `devops-agent` |
| **Version** | N/A |
| **Type** | ai_office/specialist |
| **Status** | PRODUCTION |
| **Port** | `8058` |
| **Framework** | N/A |

**Description:**

> AI-powered infrastructure management with platform compliance toolkit. Monitors containers, validates compliance, and provides auto-remediation.

**Key Capabilities:**

- Platform Compliance (6 priorities)
- Priority 1: Port conflict detection
- Priority 2: Metrics integration validation (Prometheus/Grafana)
- Priority 3: Database connection checks (PostgreSQL/Redis)
- Priority 4: KPI registration validation
- Priority 5: EventBus events monitoring
- Priority 6: Orchestrator control validation
- Container analysis and monitoring
- Dockerfile generation
- Event architecture scanning
- *...and 3 more*

**Features:**

- Compliance toolkit with unified runner
- Docker integration
- AI knowledge learning
- Auto-fix suggestions

**Required Dependencies:**

- Docker API
- EventBus

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| MIO Manager | compliance_provider | Provides compliance state via API... |
| Docker | container_management | Monitors containers... |
| Orchestrator | deployment | Validates deployments... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| devops_compliance_checks_total | counter | N/A | `N/A` |
| devops_issues_detected_total | counter | N/A | `N/A` |
| devops_auto_fixes_applied_total | counter | N/A | `N/A` |

---

### MIO Manager - Platform Observatory & Coordinator

| Property | Value |
|----------|-------|
| **Service ID** | `mio-manager` |
| **Version** | N/A |
| **Type** | ai_office/coordinator |
| **Status** | PRODUCTION |
| **Port** | `8046` |
| **Framework** | N/A |

**Description:**

> EYES Observatory pattern - monitors platform-wide health, coordinates AI Office team, and publishes events via EventBus (choreography pattern). Does NOT command services - observes and reports.

**Key Capabilities:**

- Platform-wide health monitoring (all services)
- Prometheus metrics coverage analysis
- Service Discovery coverage monitoring
- Infrastructure state tracking (postgres_available, redis_available)
- EventBus choreography coordination
- AI Office team coordination
- KPI aggregation and reporting

**Features:**

- EYES pattern (observe & publish, don't command)
- Real-time dashboard (FastAPI + WebSocket)
- Grafana integration
- Compliance state collection (via DevOps Agent)
- EventBus event monitoring

**Required Dependencies:**

- Service Discovery - service registry
- Prometheus - metrics scraping
- EventBus - event coordination

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| DevOps Agent | compliance_monitoring | Collects compliance state via API... |
| Service Discovery | service_tracking | Monitors service registration coverage... |
| Prometheus | metrics_aggregation | Monitors metrics coverage... |
| EventBus | choreography | Publishes observations, subscribes to pl... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| mio_services_monitored_total | gauge | N/A | `N/A` |
| mio_health_checks_total | counter | N/A | `N/A` |
| mio_events_published_total | counter | N/A | `N/A` |
| mio_platform_health_score | gauge | N/A | `N/A` |

---

### Project & Code Quality Agent

| Property | Value |
|----------|-------|
| **Service ID** | `project-agent` |
| **Version** | N/A |
| **Type** | ai_office/specialist |
| **Status** | PRODUCTION |
| **Port** | `8060` |
| **Framework** | N/A |

**Description:**

> Project management + code quality analysis + testing coverage. AI-powered test generation and compliance validation.

**Key Capabilities:**

- Project & task management
- Progress tracking and reporting
- Code security scanning
- Code quality analysis
- Testing coverage analysis
- AI-powered test generation
- Compliance checking (ISO 22301, ISO 27001, HIPAA)
- Domain detection (AI-powered)

**Features:**

- Project lifecycle management
- Security vulnerability detection
- Quality metrics collection
- Coverage reporting
- AI test generation

**Required Dependencies:**

- EventBus

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| MIO Manager | quality_provider | Provides quality metrics... |
| DevOps Agent | ci_cd | CI/CD quality gates... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| project_tests_generated_total | counter | N/A | `N/A` |
| project_coverage_percent | gauge | N/A | `N/A` |
| project_security_issues_total | counter | N/A | `N/A` |

---

---

## Platform Services
<a name="platform-services"></a>

**Services:** 10

### BIA Service - Business Impact Analysis

| Property | Value |
|----------|-------|
| **Service ID** | `bia-service` |
| **Version** | N/A |
| **Type** | platform_services/bcm |
| **Status** | PRODUCTION |
| **Port** | `8012` |
| **Framework** | FastAPI |

**Description:**

> Comprehensive Business Impact Analysis service aligned with ISO 22301:2019 Clause 8.2.2. Provides RTO/RPO/MTPD calculations, financial impact assessment, dependency mapping, and AI-powered analysis.

**Key Capabilities:**

- RTO/RPO/MTPD Calculations
- Financial Impact Assessment (1 hour to 1 month)
- Dependency Mapping (upstream/downstream)
- Critical Process Identification (automated criticality scoring)
- AI-Powered Analysis (RTO suggestions, dependency discovery)
- Multi-Industry Support (Healthcare WHO tiers, Financial, IT, etc.)
- Supply Chain BCM (critical supplier management)
- Bulk Operations (create/update/delete with partial success)

**Features:**

- 16 API endpoints
- WHO Essential Services Tier Classification (Tier 1-4)
- Patient Safety Impact Assessment (healthcare)
- Peak Period Analysis (different RTOs for peak vs normal)
- Alternative Procedures documentation
- *...and 1 more*

**Required Dependencies:**

- PostgreSQL/Supabase - BIA data persistence
- EventBus - RabbitMQ

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| Risk Service | data_provider | BIA triggers risk assessments for critic... |
| Planning Service | data_provider | BIA results drive strategy selection... |
| Governance Service | event_subscriber | Auto-create BIA template on org creation... |
| Supply Chain Module | optional_module | 8 additional endpoints for supply chain ... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| bia_processes_total | gauge | N/A | `N/A` |
| bia_critical_processes_total | gauge | N/A | `N/A` |
| bia_avg_rto_hours | gauge | N/A | `N/A` |
| bia_ai_suggestions_total | counter | N/A | `N/A` |
| bia_cache_hit_rate | gauge | 80 | `N/A` |

---

### Compliance Service

| Property | Value |
|----------|-------|
| **Service ID** | `compliance-service` |
| **Version** | 1.0.0 |
| **Type** | platform_services/compliance |
| **Status** | ACTIVE |
| **Port** | `8014` |
| **Framework** | FastAPI |

**Description:**

> Comprehensive compliance management for ISO 22301. Manages assessments, gap analysis, evidence collection, nonconformity management (RCA), internal audits, and continual improvement initiatives.

**Key Capabilities:**

- Compliance assessments against ISO 22301, HIPAA, SOC2, GDPR
- Gap analysis and remediation tracking
- Evidence collection and management
- Internal audit planning and execution (Clause 9.2)
- Nonconformity management with Root Cause Analysis (Clause 10.1)
- Corrective and preventive actions (CAPA)
- Continual improvement tracking (Clause 10.2)
- Management review support
- Compliance dashboard and reporting
- Templates library (audit plans, checklists, reports)

**Features:**

- 46 API endpoints (assessments, gaps, evidence, audits, CAPA, improvement)
- Multi-standard support (ISO 22301, HIPAA, SOC2, GDPR)
- RCA templates (5W2H, Fishbone)
- Evidence linking to requirements
- Audit scheduling and tracking

**Required Dependencies:**

- PostgreSQL 14+ - compliance data

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| Governance Service | requirements_sync | Updates compliance requirements from pol... |
| Documents Service | evidence_linking | Links evidence documents to assessments... |
| Risk Service | gap_to_risk | Creates compliance gap if control missin... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| compliance_service_requests_total | counter | > 1000/day | `N/A` |
| compliance_service_overall_score | gauge | > 85 | `N/A` |
| compliance_service_open_gaps | gauge | < 10 | `N/A` |
| compliance_service_nc_resolution_days | histogram | < 30 days | `N/A` |
| compliance_service_capa_effectiveness | gauge | > 80% | `N/A` |

**API Endpoints:**

- `http://localhost:8014` - base_url
- `/health` - health
- `/metrics` - metrics
- `/docs` - api_docs
- `/api/compliance` - api_base

---

### Documents Service

| Property | Value |
|----------|-------|
| **Service ID** | `documents-service` |
| **Version** | 1.0.0 |
| **Type** | platform_services/document_management |
| **Status** | ACTIVE |
| **Port** | `8024` |
| **Framework** | FastAPI |

**Description:**

> Enterprise document lifecycle management with AI/NLP capabilities, approval workflows, version control, and retention policies. Implements ISO 22301 Clause 7.5 - Documented Information Management.

**Key Capabilities:**

- Document lifecycle management (Draft → Review → Approved → Published → Archived)
- AI/NLP document processing (extraction, classification, analysis, summarization)
- Version control with diff comparison
- Multi-stage approval workflows (5 stages with SLAs)
- Retention policies (ISO 22301 + HIPAA compliance)
- Security classification levels (5 levels)
- Access control and audit logging
- Document sharing and collaboration
- File storage with integrity verification (SHA-256)

**Features:**

- 8 database models (Document, DocumentAccess, DocumentApproval, etc.)
- AI/NLP processors (PDFs, DOCX, Excel, OCR)
- Auto-classification (ML-based type detection)
- Extractive + AI summarization (OpenAI GPT)
- Named entity recognition (spaCy)
- *...and 2 more*

**Required Dependencies:**

- PostgreSQL 15+ - documents metadata
- File storage (local or S3-compatible)

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| Governance Service | document_linking | Creates policy documents, updates refere... |
| Plans Service | document_linking | Links plan documents... |
| Validation Service | report_generation | Creates exercise report documents... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| documents_service_requests_total | counter | > 2000/day | `N/A` |
| documents_service_total_documents | gauge | > 100 | `N/A` |
| documents_service_approval_sla_compliance | gauge | > 90% | `N/A` |
| documents_service_retention_compliance | gauge | 100% | `N/A` |
| documents_service_ai_processing_seconds | histogram | < 5s | `N/A` |

**API Endpoints:**

- `http://localhost:8024` - base_url
- `/health` - health
- `/metrics` - metrics
- `/docs` - api_docs
- `/api/documents` - api_base

---

### Governance Service

| Property | Value |
|----------|-------|
| **Service ID** | `governance-service` |
| **Version** | 2.0.0 |
| **Type** | platform_services/governance |
| **Status** | ACTIVE |
| **Port** | `8025` |
| **Framework** | FastAPI |

**Description:**

> Organizational governance framework implementation for BCM. Manages stakeholder engagement, decision-making processes, organizational context analysis, governance structures, and accountability tracking.

**Key Capabilities:**

- Stakeholder management and engagement tracking
- Governance structure definition (roles, committees)
- Decision-making process management
- Organizational context analysis (PESTLE, SWOT)
- BCM policy framework management
- Accountability and responsibility tracking
- Leadership commitment monitoring
- Governance reporting and dashboards

**Features:**

- 46 API endpoints (stakeholders, governance structures, policies, context)
- PESTLE + SWOT analysis tools
- Committee management with roles hierarchy
- Decision tracking with accountability
- EventBus choreography

**Required Dependencies:**

- PostgreSQL 14+ - governance data
- Redis 7+ - caching and session management

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| Compliance Service | gap_tracking | Creates governance action items from com... |
| Risk Service | escalation | Escalates critical risks to governance c... |
| Response Service | notification | Notifies governance stakeholders of majo... |
| Documents Service | policy_management | Creates and manages policy documents... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| governance_service_requests_total | counter | > 500/day | `N/A` |
| governance_service_active_stakeholders | gauge | > 20 | `N/A` |
| governance_service_engagement_rate | gauge | > 80% | `N/A` |
| governance_service_policy_compliance | gauge | 100% | `N/A` |
| governance_service_decision_implementation | gauge | > 85% | `N/A` |

**API Endpoints:**

- `http://localhost:8025` - base_url
- `/health` - health
- `/metrics` - metrics
- `/docs` - api_docs
- `/api/governance` - api_base

---

### Learning Service - Training & Competence Management

| Property | Value |
|----------|-------|
| **Service ID** | `learning-service` |
| **Version** | N/A |
| **Type** | platform_services/bcm |
| **Status** | PRODUCTION |
| **Port** | `8021` |
| **Framework** | FastAPI |

**Description:**

> ISO 22301 Training & Competence Management service for BCM awareness, training programs, competency assessments, and gamification.

**Key Capabilities:**

- Training Programs management
- Enrollment tracking
- Competency Assessments
- Awareness Campaigns
- Gamification (points, badges, leaderboards)
- Certification management
- Progress tracking & reporting

**Features:**

- Workflow Intelligence integration
- Audit logging
- ISO 22301 compliance checking (Clauses 7.2 & 7.3)
- EventBus choreography
- JWT authentication

**Required Dependencies:**

- PostgreSQL/Supabase - training data
- EventBus - coordination

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| Governance Service | user_sync | Sync user roles and permissions... |
| Validation Service | event_publisher | Publishes training completion events... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| learning_enrollments_total | counter | N/A | `N/A` |
| learning_completions_total | counter | N/A | `N/A` |
| learning_avg_completion_rate | gauge | 80 | `N/A` |
| learning_certification_issuances_total | counter | N/A | `N/A` |

---

### Planning Service - BC Strategy Development

| Property | Value |
|----------|-------|
| **Service ID** | `planning-service` |
| **Version** | N/A |
| **Type** | platform_services/bcm |
| **Status** | PRODUCTION |
| **Port** | `8011` |
| **Framework** | FastAPI |

**Description:**

> Business Continuity Strategy development and selection service aligned with ISO 22301:2019 Clause 8.3 requirements. Provides cost-benefit analysis, resource planning, and approval workflows for BC strategies.

**Key Capabilities:**

- BC Strategy Development (based on BIA results)
- Cost-Benefit Analysis (NPV, ROI, Payback Period)
- Resource Planning (personnel, technology, facilities)
- Approval Workflow (Draft → Review → Approved)
- Financial Modeling (multi-year TCO & benefit projections)
- Strategy Types (7 types: DO_NOTHING to IMMEDIATE_RECOVERY)

**Features:**

- Workflow Intelligence integration
- Audit logging enabled
- ISO 22301 compliance checking
- Security middleware (JWT + RLS)
- Redis caching
- *...and 1 more*

**Required Dependencies:**

- PostgreSQL/Supabase - strategy storage
- EventBus - choreography
- Orchestrator - registration

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| BIA Service | data_consumer | Listens to bia.analysis.completed events... |
| Risk Service | data_consumer | Listens to risk.assessment.completed eve... |
| Workflow Intelligence | state_management | Strategy approval workflow state machine... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| planning_strategies_created_total | counter | N/A | `N/A` |
| planning_strategies_approved_total | counter | N/A | `N/A` |
| planning_avg_cost_benefit_ratio | gauge | N/A | `N/A` |
| planning_approval_duration_hours | histogram | N/A | `N/A` |

---

### Plans Service

| Property | Value |
|----------|-------|
| **Service ID** | `plans-service` |
| **Version** | 1.0.0 |
| **Type** | platform_services/bcm |
| **Status** | ACTIVE |
| **Port** | `8023` |
| **Framework** | FastAPI |

**Description:**

> Business Continuity Plans & Procedures management service. Manages BC plans, procedures, resources, plan lifecycle, reviews, and activations. Implements ISO 22301 Clause 8.4 requirements for BC plans and procedures.

**Key Capabilities:**

- Business continuity plan management (10+ endpoints)
- Plan lifecycle workflow (Draft → Review → Approved → Active → Archived)
- Procedure management with sequencing (4 endpoints)
- Resource allocation and tracking (7 resource types: personnel, tech, facilities)
- Contact lists with call tree structure
- Plan activation tracking and metrics (real incidents)
- Plan review scheduling and workflow
- Communication templates library
- Plan templates (reusable structures)

**Features:**

- 8 database models (Plan, Procedure, PlanResource, ContactList, etc.)
- 25+ API endpoints
- EventBus integration (strategy.approved, bia.completed, incident.declared)
- Plan activation metrics tracking
- ISO 22301 Clause 8.4 full compliance

**Required Dependencies:**

- PostgreSQL 15+ - plans, procedures, resources
- EventBus - event-driven workflows

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| Planning Service | data_consumer | Creates plans from approved strategies... |
| BIA Service | data_consumer | Updates plan RTOs/RPOs from BIA results... |
| Response Service | activation | Activates plans during real incidents... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| plans_service_requests_total | counter | > 1000/day | `N/A` |
| plans_service_active_plans | gauge | > 10 | `N/A` |
| plans_service_approval_duration_seconds | histogram | < 7 days | `N/A` |
| plans_service_review_compliance_percent | gauge | > 95% | `N/A` |
| plans_service_activations_total | counter | N/A | `N/A` |

**API Endpoints:**

- `http://localhost:8023` - base_url
- `/health` - health
- `/metrics` - metrics
- `/docs` - api_docs
- `/api/plans` - api_base

---

### Response Service

| Property | Value |
|----------|-------|
| **Service ID** | `response-service` |
| **Version** | 1.0.0 |
| **Type** | platform_services/incident_response |
| **Status** | ACTIVE |
| **Port** | `8027` |
| **Framework** | FastAPI |

**Description:**

> Comprehensive incident response management. Manages incidents, response actions, response teams, communications, timeline tracking, recovery metrics (RTO/RPO), escalation, and reporting.

**Key Capabilities:**

- Incident lifecycle management (New → Active → Contained → Resolved → Closed)
- Response action tracking and assignment
- Response team management and coordination
- Incident communications log
- Chronological incident timeline
- RTO/RPO tracking and validation
- Automatic and manual incident escalation
- Real-time incident dashboard
- Comprehensive incident reports
- Post-incident review process
- *...and 1 more*

**Features:**

- 35 API endpoints (incidents, actions, teams, communications, timeline, metrics)
- Auto-escalation for critical incidents
- RTO/RPO validation
- Real-time dashboard
- EventBus integration

**Required Dependencies:**

- PostgreSQL 14+ - incident data
- Redis 7+ - real-time incident state caching
- RabbitMQ - EventBus for incident notifications

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| Plans Service | plan_activation | Activates BC plans during real incidents... |
| BIA Service | rto_rpo_validation | Gets RTO/RPO for validation... |
| Orchestrator | ai_assistance | AI-assisted incident response... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| response_service_requests_total | counter | > 500/day | `N/A` |
| response_service_active_incidents | gauge | < 5 | `N/A` |
| response_service_mttr_hours | histogram | < 4 hours | `N/A` |
| response_service_mtta_minutes | histogram | < 15 minutes | `N/A` |
| response_service_rto_achievement | gauge | > 95% | `N/A` |

**API Endpoints:**

- `http://localhost:8027` - base_url
- `/health` - health
- `/metrics` - metrics
- `/docs` - api_docs
- `/api/response` - api_base

---

### Risk Service

| Property | Value |
|----------|-------|
| **Service ID** | `risk-service` |
| **Version** | 2.0.0 |
| **Type** | platform_services/risk |
| **Status** | ACTIVE |
| **Port** | `8026` |
| **Framework** | FastAPI |

**Description:**

> Comprehensive risk management including risk identification, assessment, treatment planning, monitoring, and reporting. Provides risk matrices, heat maps, and integration with mitigation workflows.

**Key Capabilities:**

- Risk identification and cataloging
- Risk assessment (likelihood × impact matrix)
- Risk treatment planning (avoid, reduce, transfer, accept)
- Risk monitoring and tracking
- Risk heat maps and visualization
- Risk appetite and tolerance configuration
- Residual risk calculation
- Risk register management
- Risk reporting and dashboards

**Features:**

- 29 API endpoints (identification, assessment, treatment, monitoring, reporting)
- Configurable 5×5 risk matrix
- Heat map generation (up to 200 risks)
- Risk register export
- EventBus integration

**Required Dependencies:**

- PostgreSQL 14+ - risk data

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| BIA Service | impact_source | Identifies risks from BIA impacts... |
| Response Service | incident_to_risk | Creates risk from incident... |
| Plans Service | mitigation_linking | Links mitigation plans to risks... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| risk_service_requests_total | counter | > 800/day | `N/A` |
| risk_service_total_risks | gauge | N/A | `N/A` |
| risk_service_high_risks | gauge | < 10 | `N/A` |
| risk_service_treatment_coverage | gauge | > 95% | `N/A` |
| risk_service_residual_score | gauge | < 50 | `N/A` |

**API Endpoints:**

- `http://localhost:8026` - base_url
- `/health` - health
- `/metrics` - metrics
- `/docs` - api_docs
- `/api/risks` - api_base

---

### Validation Service - Exercises, Audits, Reviews & CAPA

| Property | Value |
|----------|-------|
| **Service ID** | `validation-service` |
| **Version** | N/A |
| **Type** | platform_services/bcm |
| **Status** | PRODUCTION |
| **Port** | `8022` |
| **Framework** | FastAPI |

**Description:**

> ISO 22301 Validation Module covering Exercises (8.5), Performance Monitoring (9.1), Internal Audits (9.2), Management Reviews (9.3), and Continuous Improvement & CAPA (10).

**Key Capabilities:**

- Exercise Management (tabletop, simulation, full-scale)
- Performance Monitoring & KPIs (automated collection & alerts)
- Internal Audits (ISO 9.2 compliance)
- Management Reviews (ISO 9.3 requirements)
- CAPA Management (Corrective & Preventive Actions)
- Continuous Improvement tracking
- KPI Auto-Collection (configurable intervals)
- Email Alerting (threshold-based)

**Features:**

- Workflow Intelligence integration
- Celery background tasks for KPI collection
- RabbitMQ integration
- Multi-tenancy with RLS
- KPI threshold alerts (critical/warning)
- *...and 1 more*

**Required Dependencies:**

- PostgreSQL - validation data
- RabbitMQ - message queue
- EventBus - choreography

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| Governance Service | data_consumer | Links exercises to governance policies... |
| Plans Service | data_consumer | Validates BC plans via exercises... |
| Incidents Service | event_subscriber | Creates CAPA from incidents... |
| Compliance Service | audit_reporting | N/A... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| validation_exercises_total | counter | N/A | `N/A` |
| validation_exercises_passed_total | counter | N/A | `N/A` |
| validation_audits_total | counter | N/A | `N/A` |
| validation_capa_created_total | counter | N/A | `N/A` |
| validation_capa_closed_total | counter | N/A | `N/A` |

---

---

## Intelligent Core
<a name="intelligent-core"></a>

**Services:** 12

### AI Foundation - Core AI Infrastructure

| Property | Value |
|----------|-------|
| **Service ID** | `ai-foundation` |
| **Version** | N/A |
| **Type** | intelligent_core/ai_infrastructure |
| **Status** | PRODUCTION |
| **Port** | `8040` |
| **Framework** | FastAPI |

**Description:**

> Core AI infrastructure providing LLM routing, RAG (Retrieval Augmented Generation), ML models, self-learning, and context building for all platform services.

**Key Capabilities:**

- LLM Routing (OpenAI, Anthropic, multi-provider)
- RAG Pipeline (embeddings, retrieval, reranking)
- ML Models (predictive, anomaly detection)
- Self-Learning Engine (pattern extraction, rule generation)
- Context Building (workflow, domain, tenant context)

**Features:**

- Multi-LLM support (Claude, GPT-4, etc.)
- Vector embeddings (sentence-transformers)
- Qdrant integration for RAG
- Scikit-learn ML pipelines
- Pattern extraction from workflow data
- *...and 1 more*

**Required Dependencies:**

- Qdrant - vector database for RAG
- PostgreSQL - ML model storage
- Redis - caching

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| Workflow Intelligence | ai_provider | Provides LLM analysis and RAG for workfl... |
| Expertise Center | ai_provider | Powers domain specialists with AI... |
| Community Intelligence | ai_provider | Anonymization and reviewer matching... |
| All platform services | ai_capabilities | Provides AI for BIA, Risk, Planning, etc... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| ai_foundation_llm_requests_total | counter | N/A | `N/A` |
| ai_foundation_llm_latency_ms | histogram | N/A | `N/A` |
| ai_foundation_rag_searches_total | counter | N/A | `N/A` |
| ai_foundation_ml_predictions_total | counter | N/A | `N/A` |
| ai_foundation_anomalies_detected_total | counter | N/A | `N/A` |

---

### AI Orchestrator - The Brain

| Property | Value |
|----------|-------|
| **Service ID** | `ai-orchestration` |
| **Version** | 3.0.0 |
| **Type** | intelligent_core/orchestration |
| **Status** | ACTIVE |
| **Port** | `8002` |
| **Framework** | FastAPI |

**Description:**

> Autonomous AI decision-making system with 4-layer memory, safety-first architecture, and self-evolution capabilities. Aggregates context from multiple sources, assesses priority, selects strategies from historical cases, validates safety against immutable Constitution rules, and executes or delegates decisions. Features loop detection, hallucination detection, crisis coordination, and self-evolution on 3 levels (Data daily, Model weekly, Code monthly with human review).

**Key Capabilities:**

- Autonomous decision-making with multi-factor priority scoring
- 4-layer memory system (Working Redis 1h, Short-term PostgreSQL 30d, Long-term Case Library, Procedural ML Models)
- Context aggregation from workflows, events, databases, external sources
- Strategy selection from historical cases and learned patterns
- Safety-first architecture (Constitution, Loop Detection, Hallucination Check, Control Monitor)
- Self-evolution on 3 levels (Data daily, Model weekly, Code monthly)
- Crisis coordination and emergency response
- Delegation to specialist agents
- Performance optimization and auto-tuning
- Constitutional AI governance (7 immutable rules)
- *...and 2 more*

**Features:**

- {'name': 'Decision Center', 'description': 'Context aggregation, priority assessment, strategy selection, delegation', 'endpoints': 5, 'components': ['ContextAggregator - Multi-source context collection', 'PriorityEngine - Multi-factor priority scoring', 'StrategySelector - Historical case-based strategy selection', 'DelegationManager - Specialist agent delegation']}
- {'name': '4-Layer Memory System', 'description': 'Hierarchical memory for learning and context retention', 'components': ['Working Memory (Redis, 1-hour TTL) - Current decision context', 'Short-term Memory (PostgreSQL, 30-day retention) - Recent decisions', 'Long-term Memory (Case Library) - Historical patterns and strategies', 'Procedural Memory (ML Models) - Learned decision-making procedures']}
- {'name': 'Safety Monitor', 'description': 'Multi-layer safety validation and control', 'components': ['ConstitutionEnforcer - 7 immutable rules validation', 'LoopDetector - Infinite loop and oscillation prevention', 'HallucinationDetector - AI-generated fabrication detection (5% FP rate)', 'ControlMonitor - Runaway AI and scope creep prevention']}
- {'name': 'Evolution Engine', 'description': 'Self-improvement on 3 levels', 'components': ['DataEvolution (Daily, Automatic) - Case consolidation, pattern extraction', 'ModelEvolution (Weekly, Automatic) - ML retraining, A/B testing, auto-rollback', 'CodeEvolution (Monthly, Human Review Required) - Code improvement suggestions, PR generation']}
- {'name': 'Crisis Coordinator', 'description': 'Emergency response coordination and escalation', 'endpoints': 4, 'components': ['CrisisDetector - Multi-signal crisis identification', 'ResourceAllocator - Emergency resource allocation', 'CommunicationHub - Stakeholder notification']}
- *...and 1 more*

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| orchestrator_requests_total | counter | > 2000/day | `N/A` |
| orchestrator_decision_latency_seconds | histogram | < 100ms | `N/A` |
| orchestrator_error_rate | gauge | < 1% | `N/A` |
| orchestrator_availability | gauge | > 99.9% | `N/A` |
| orchestrator_auto_resolve_success_rate | gauge | > 85% | `N/A` |

**API Endpoints:**

- `http://localhost:8002` - base_url
- `/health` - health
- `/metrics` - metrics
- `/docs` - api_docs
- `/api/v1` - api_base

---

### AI Workflow Optimizer

| Property | Value |
|----------|-------|
| **Service ID** | `ai_workflow_optimizer` |
| **Version** | 2.0.0 |
| **Type** | intelligent_core/workflow-optimization |
| **Status** | ACTIVE |
| **Port** | `8038` |
| **Framework** | FastAPI |

**Description:**

> ML-powered workflow optimization service that analyzes business process performance, identifies bottlenecks, predicts execution times, detects anomalies, and recommends optimization strategies using machine learning algorithms (Random Forest, Isolation Forest, K-Means).

**Key Capabilities:**

- ML-based workflow performance prediction (Random Forest)
- Bottleneck detection and resource optimization
- Anomaly detection using Isolation Forest
- Workflow clustering and pattern recognition (K-Means)
- Execution time forecasting with confidence intervals
- Automated optimization strategy recommendation
- Model training and auto-tuning
- Performance metrics tracking and analysis
- Historical workflow data analysis

**Features:**

- {'name': 'Performance Prediction', 'description': 'ML-based workflow execution time prediction', 'endpoints': 3, 'algorithm': 'Random Forest Regressor', 'features': ['step_count', 'resource_usage', 'data_size', 'complexity_score'], 'target': 'execution_time_seconds', 'accuracy': '> 85% (R²)', 'metrics': ['Mean Absolute Error (MAE)', 'Root Mean Squared Error (RMSE)', 'R² score']}
- {'name': 'Bottleneck Detection', 'description': 'Identify and analyze workflow bottlenecks', 'endpoints': 2, 'features': ['Step-level performance analysis', 'Resource utilization tracking', 'Critical path identification', 'Optimization recommendations']}
- {'name': 'Anomaly Detection', 'description': 'Detect unusual workflow behavior patterns', 'endpoints': 2, 'algorithm': 'Isolation Forest', 'threshold': '0.7 (anomaly score)', 'features': ['Real-time anomaly scoring', 'Historical pattern comparison', 'Alert generation for anomalies']}
- {'name': 'Workflow Clustering', 'description': 'Group similar workflows for pattern analysis', 'endpoints': 2, 'algorithm': 'K-Means clustering', 'clusters': '3-10 (auto-optimized)', 'features': ['Automatic cluster count optimization', 'Workflow similarity scoring', 'Pattern-based recommendations']}
- {'name': 'Optimization Strategies', 'description': 'Generate ML-driven optimization recommendations', 'endpoints': 3, 'strategies': ['Resource reallocation', 'Step parallelization', 'Caching opportunities', 'Timeout adjustments']}

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| workflow_optimizer_requests_total | counter | > 200/day | `N/A` |
| workflow_optimizer_prediction_r2 | gauge | > 0.85 | `N/A` |
| workflow_optimizer_response_time_ms | histogram | < 500ms | `N/A` |
| workflow_optimizer_error_rate | gauge | < 2% | `N/A` |
| workflow_optimizer_model_mae | gauge | < 10% of average execution time | `N/A` |

**API Endpoints:**

- `http://localhost:8038` - base_url
- `/health` - health
- `/metrics` - metrics
- `/docs` - api_docs
- `/api/v1` - api_base

---

### Collective Intelligence Agent Networks

| Property | Value |
|----------|-------|
| **Service ID** | `collective` |
| **Version** | 1.0.0 |
| **Type** | intelligent_core/collective-intelligence |
| **Status** | ACTIVE |
| **Port** | `8034` |
| **Framework** | FastAPI |

**Description:**

> Privacy-preserving knowledge sharing across organizations through temporary AI agents synthesized from anonymized collective wisdom. Enables organizations to benefit from proven solutions without compromising confidentiality using k-anonymity principles (minimum k=5).

**Key Capabilities:**

- Automatic stuck organization detection (7-day progress monitoring)
- Privacy-preserving collective agent creation (k-anonymity k≥5)
- Multi-layer anonymization (4 layers: org, journey, pattern, metrics)
- Temporary agent lifecycle management (7-day expiration)
- Aggregate statistical framing without source attribution
- Conversational chat interface with source protection
- Re-identification risk scoring and validation
- Success-driven case selection (≥80% success rate)
- Case library integration for solver identification

**Features:**

- {'name': 'Stuck Detection', 'description': 'Multi-signal detection of organizations requiring assistance', 'endpoints': 3, 'scoring': ['Days no progress (7+) = +3 points', 'Validation failures (5+) = +2 points', 'Low AI confidence (<0.6) = +2 points', 'Repeated questions (3+) = +1 point', 'Document review cycles (5+) = +1 point', 'Frustration score (>0.7) = +2 points'], 'thresholds': ['Score 0-3: On track', 'Score 4-6: Stuck, help recommended', 'Score 7+: Seriously stuck, immediate intervention']}
- {'name': 'Collective Agent Creation', 'description': 'Synthesize anonymous collective wisdom agents', 'endpoints': 5, 'workflow': ['Query case library (min 5 cases, ≥80% success)', 'Apply 4-layer anonymization', 'Calculate re-identification risk (must be ≤0.3)', 'Configure LLM agent with collective knowledge', 'Activate with 7-day auto-expiration']}
- {'name': 'Privacy System', 'description': 'Multi-layer privacy protection', 'endpoints': 3, 'layers': ['Layer 1: Organization anonymization', 'Layer 2: Journey anonymization', 'Layer 3: Pattern anonymization', 'Layer 4: Metric anonymization']}
- {'name': 'Chat Interface', 'description': 'Conversational interface with collective agents', 'endpoints': 2, 'features': ["Statistical framing (e.g., '5 out of 7 organizations...')", 'Source attribution prevention', 'Session management (Redis-backed)', 'Conversation audit logging']}

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| collective_agents_created_total | counter | > 50/month | `N/A` |
| collective_agents_active | gauge | 10-50 concurrent | `N/A` |
| collective_stuck_detections_total | counter | > 30/month | `N/A` |
| collective_chat_messages_total | counter | > 500/month | `N/A` |
| collective_privacy_violations_total | counter | 0 | `N/A` |

**API Endpoints:**

- `http://localhost:8034` - base_url
- `/health` - health
- `/metrics` - metrics
- `/docs` - api_docs
- `/api/v1` - api_base

---

### Community Intelligence - Peer Knowledge Sharing

| Property | Value |
|----------|-------|
| **Service ID** | `community-intelligence` |
| **Version** | N/A |
| **Type** | intelligent_core/community |
| **Status** | PRODUCTION |
| **Port** | `8030` |
| **Framework** | FastAPI |

**Description:**

> Community-driven knowledge creation service enabling peer-reviewed knowledge sharing through automated workflow integration, expert validation, reputation systems, and searchable case library.

**Key Capabilities:**

- Auto-Contribution (workflow completions → shareable cases)
- Peer Review System (smart reviewer matching, quality scoring)
- Reputation Engine (gamification, points, badges, leaderboards)
- Case Library (searchable knowledge base with anonymization)
- Event Integration (workflow triggers, EventBus publishing)

**Features:**

- Automated PII anonymization (AI-powered)
- 3-reviewer consensus with quality scoring (1-10)
- Reputation economy (points, badges)
- Full-text and semantic search
- Reviewer matching (expertise, industry, workload)
- *...and 1 more*

**Required Dependencies:**

- PostgreSQL/Supabase - contributions, reviews, reputation
- Redis - EventBus messaging
- AI Foundation - anonymization, matching

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| Workflow Intelligence | case_provider | Sends approved cases to workflow intelli... |
| AI Foundation | ai_consumer | Uses AI for anonymization and reviewer m... |
| Platform Services | event_subscriber | Listens to workflow completions... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| community_contributions_total | counter | N/A | `N/A` |
| community_reviews_total | counter | N/A | `N/A` |
| community_reputation_points | gauge | N/A | `N/A` |
| community_cases_published | counter | N/A | `N/A` |
| community_review_quality_score | histogram | N/A | `N/A` |

---

### Multi-Agent Coordination Center

| Property | Value |
|----------|-------|
| **Service ID** | `coordination-center` |
| **Version** | 1.0.0-planned |
| **Type** | intelligent_core/coordination |
| **Status** | PLANNED |
| **Port** | `8033` |
| **Framework** | FastAPI |

**Description:**

> Multi-agent coordination and collaboration hub. Manages agent teams, task allocation, inter-agent communication, and collaborative problem-solving. PLANNED for Q1 2026. Will provide dynamic team formation, intelligent task distribution, consensus building, and coordination pattern learning.

**Key Capabilities:**

- Multi-agent team formation and management
- Dynamic task allocation and scheduling
- Inter-agent communication protocols
- Collaborative problem-solving strategies
- Consensus building and conflict resolution
- Agent capability discovery and matching
- Workload balancing across agents
- Coordination pattern learning
- Agent performance tracking

**Features:**

- {'name': 'Team Formation', 'description': 'Dynamic agent team creation based on task requirements', 'endpoints': 4, 'status': 'planned'}
- {'name': 'Task Allocation', 'description': 'Intelligent task distribution among agents', 'endpoints': 5, 'status': 'planned'}
- {'name': 'Communication Hub', 'description': 'Inter-agent messaging and information sharing', 'endpoints': 6, 'status': 'planned'}
- {'name': 'Consensus Engine', 'description': 'Multi-agent decision consensus building', 'endpoints': 3, 'status': 'planned'}
- {'name': 'Performance Monitor', 'description': 'Track agent and team performance', 'endpoints': 4, 'status': 'planned'}

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| coordination_requests_total | counter | TBD | `N/A` |
| coordination_agent_utilization | gauge | > 70% | `N/A` |
| coordination_task_completion_rate | gauge | > 90% | `N/A` |
| coordination_consensus_seconds | histogram | < 30s | `N/A` |
| coordination_team_effectiveness | gauge | > 0.8 | `N/A` |

**API Endpoints:**

- `http://localhost:8033` - base_url
- `/health` - health
- `/metrics` - metrics
- `/docs` - api_docs
- `/api/coordination` - api_base

---

### Event Intelligence & Self-Healing

| Property | Value |
|----------|-------|
| **Service ID** | `event-intelligence` |
| **Version** | 2.0.0 |
| **Type** | intelligent_core/event_intelligence |
| **Status** | ACTIVE |
| **Port** | `8032` |
| **Framework** | FastAPI |

**Description:**

> Intelligent event analysis, pattern detection, domain detection, error analysis, and automated code healing for platform stability and resilience. Subscribes to all platform events, identifies patterns and anomalies, performs root cause analysis, and executes automated healing procedures. Provides predictive error forecasting and event-driven alerts.

**Key Capabilities:**

- Real-time event stream analysis (all platform events)
- Pattern detection and anomaly identification
- Domain detection (auto-classify events by business domain)
- Error analysis and root cause identification
- Automated code healing and self-repair
- Event correlation and clustering
- Predictive error forecasting
- Event-driven alerts and notifications
- Historical event analytics
- Event replay and debugging

**Features:**

- {'name': 'Event Analysis', 'description': 'Real-time analysis of platform events', 'endpoints': 5, 'components': ['Event stream processor', 'Real-time analyzer', 'Event classifier']}
- {'name': 'Pattern Detection', 'description': 'Identify patterns and anomalies in event streams', 'endpoints': 3, 'components': ['Pattern matcher', 'Anomaly detector', 'Clustering engine']}
- {'name': 'Domain Detection', 'description': 'Auto-classify events by business domain', 'endpoints': 3, 'components': ['Domain classifier (ML-based)', 'Context extractor', 'Domain rules engine']}
- {'name': 'Error Analysis', 'description': 'Root cause analysis for errors and failures', 'endpoints': 3, 'components': ['Root cause analyzer', 'Stack trace parser', 'Error correlator']}
- {'name': 'Self-Healing', 'description': 'Automated code healing and repair mechanisms', 'endpoints': 3, 'components': ['Healing procedure executor', 'Code patcher', 'Recovery validator']}

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| event_intelligence_requests_total | counter | > 5000/day | `N/A` |
| event_intelligence_response_time_ms | histogram | < 200ms | `N/A` |
| event_intelligence_error_rate | gauge | < 0.5% | `N/A` |
| event_intelligence_availability | gauge | > 99.9% | `N/A` |
| event_intelligence_pattern_accuracy | gauge | > 85% | `N/A` |

**API Endpoints:**

- `http://localhost:8032` - base_url
- `/health` - health
- `/metrics` - metrics
- `/docs` - api_docs
- `/api/events` - api_base

---

### Expertise Center - Domain Specialists & AI Assistants

| Property | Value |
|----------|-------|
| **Service ID** | `expertise-center` |
| **Version** | N/A |
| **Type** | intelligent_core/domain_expertise |
| **Status** | PRODUCTION |
| **Port** | `None` |
| **Framework** | N/A |

**Description:**

> Domain-specific expertise and specialized AI assistants for Business Continuity Management. Implements tactical assistants for BIA, compliance, governance, risk, and other BCM domains.

**Key Capabilities:**

- Domain-Specific AI Assistants (BIA, Compliance, Risk, Governance)
- Tactical BCM Specialists
- Expert Knowledge Management
- Domain-Specific RAG (specialized knowledge bases)
- AI Colleagues (BCM project intelligence)

**Features:**

- 63 Python files, 11,846 lines of code
- 58 classes, 27 functions
- 28 API endpoints
- 57 dependencies
- Tactical assistants for multiple BCM domains

**Required Dependencies:**

- AI Foundation - LLM and RAG
- PostgreSQL - domain knowledge storage

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| Platform Services | domain_expertise | Provides AI assistants to BIA, Risk, Pla... |
| AI Foundation | ai_consumer | Uses RAG and LLM for domain knowledge... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| expertise_center_queries_total | counter | N/A | `N/A` |
| expertise_center_recommendations_total | counter | N/A | `N/A` |

---

### Predictive Journey Service

| Property | Value |
|----------|-------|
| **Service ID** | `predictive` |
| **Version** | 1.0.0 |
| **Type** | intelligent_core/predictive |
| **Status** | ACTIVE |
| **Port** | `8031` |
| **Framework** | FastAPI |

**Description:**

> AI-powered forecasting for BCM journeys. Predicts milestones, certification timelines, expert demands, and challenges using pattern matching, statistical analysis, and machine learning. Generates daily proactive digest at 8:00 AM with personalized recommendations. Uses similarity-based organizational matching with confidence scoring.

**Key Capabilities:**

- 90-day journey timeline prediction (3-6 milestones)
- ISO 22301 certification date forecasting
- Expert marketplace demand forecasting
- Daily proactive digest generation (8:00 AM schedule)
- Challenge prediction with mitigation strategies
- Cost estimation (size-adjusted internal staff time)
- Similarity-based organizational matching
- Confidence scoring (frequency and variance-based)
- Prediction accuracy tracking and learning

**Features:**

- {'name': 'Journey Predictor', 'description': 'Forecasts BCM milestone timelines using similarity patterns', 'endpoints': 3, 'components': ['Similarity matcher', 'Timeline predictor', 'Milestone estimator']}
- {'name': 'Certification Predictor', 'description': 'Estimates ISO 22301 certification achievement dates', 'endpoints': 2, 'components': ['Certification timeline estimator', 'Readiness assessor']}
- {'name': 'Demand Forecaster', 'description': 'Predicts expert marketplace demand by specialty/region', 'endpoints': 3, 'components': ['Demand analyzer', 'Trend predictor', 'Capacity planner']}
- {'name': 'Proactive Recommendations', 'description': 'Daily personalized guidance and reminders', 'endpoints': 2, 'components': ['Digest generator (8:00 AM daily)', 'Recommendation engine', 'Priority ranker']}
- {'name': 'Challenge Predictor', 'description': 'Identifies likely obstacles with mitigation', 'endpoints': 2, 'components': ['Risk identifier', 'Mitigation suggester']}

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| predictive_requests_total | counter | > 300/day | `N/A` |
| predictive_response_time_ms | histogram | < 1s | `N/A` |
| predictive_error_rate | gauge | < 2% | `N/A` |
| predictive_availability | gauge | > 99.5% | `N/A` |
| predictive_accuracy | gauge | > 75% | `N/A` |

**API Endpoints:**

- `http://localhost:8031` - base_url
- `/health` - health
- `/metrics` - metrics
- `/docs` - api_docs
- `/api/predictive` - api_base

---

### System BCM Service - Platform Self-Application of Business Continuity

| Property | Value |
|----------|-------|
| **Service ID** | `system-bcm-service` |
| **Version** | N/A |
| **Type** | intelligent_core/self_application |
| **Status** | PRODUCTION |
| **Port** | `8050` |
| **Framework** | FastAPI |

**Description:**

> Production service that applies BCM to the platform itself in real-time. Continuously monitors platform health, executes BCM cycles every 24 hours, triggers automatic recovery procedures, and learns from platform operations. Fully integrated with all platform components - uses PatternDetector from learning-knowledge, consults Expertise Center (14 AI specialists), shares patterns with Collective Intelligence (347+ cases), and uses RAG+LLM for deep insights. This is NOT a demo - this is PRODUCTION!

**Key Capabilities:**

- Applies BCM to platform in real-time (24-hour continuous cycles)
- Automatic recovery procedures (7 procedures with RTO monitoring)
- Platform health monitoring (29 services + 6 infrastructure components)
- EventBus integration for platform events (4 subscriptions, 5 publications)
- Self-learning from platform operations and recovery outcomes
- AI-powered analysis (consults 14 AI specialists from Expertise Center)
- Pattern detection and knowledge sharing (Collective Intelligence)
- Prometheus metrics export & Grafana dashboards
- Manual cycle and recovery triggers via REST API
- Survival Instinct integration (self-correction)
- *...and 1 more*

**Features:**

- ✅ INTEGRATED with platform core (no duplication)
- ✅ Uses learning-knowledge/PatternDetector
- ✅ Consults 14 AI specialists from Expertise Center
- ✅ Shares patterns with Collective Intelligence (347+ cases)
- ✅ RAG + LLM analysis (Qdrant + Claude/GPT)
- *...and 6 more*

**Required Dependencies:**

- Redis EventBus - CRITICAL Tier 1 (6379)
- PostgreSQL - platform data (5432)
- learning-knowledge - PatternDetector (NO duplication!)
- Expertise Center - 14 AI specialists
- Collective Intelligence - pattern sharing (347+ cases)

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| Platform Services (12 services) | monitoring_and_recovery | Monitors BIA, Risk, Compliance, Planning... |
| Intelligent Core (11 modules) | ai_coordination | Integrated with Predictive, Collective I... |
| Infrastructure Layer (6 components) | critical_monitoring | Monitors Redis, PostgreSQL, API Gateway,... |
| learning-knowledge | pattern_detection | Uses existing PatternDetector (NO duplic... |
| Expertise Center | ai_consultation | Consults 14 domain specialists (BIA, Ris... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| system_bcm_cycles_total | counter | Incrementing every 24h | `N/A` |
| system_bcm_improvements_total | counter | Growing over time | `N/A` |
| system_bcm_patterns_shared_total | counter | N/A | `N/A` |
| system_bcm_specialists_consulted_total | counter | N/A | `N/A` |
| system_bcm_running | gauge | 1 | `N/A` |

---

### Unified Workflow Engine

| Property | Value |
|----------|-------|
| **Service ID** | `workflow-engine` |
| **Version** | 2.0.0 |
| **Type** | intelligent_core/workflow_orchestration |
| **Status** | ACTIVE |
| **Port** | `8030` |
| **Framework** | FastAPI |

**Description:**

> Domain-agnostic BPMN 2.0 workflow engine for orchestrating complex business processes. Executes workflows designed by Workflow Intelligence, provides AI-powered recommendations for stuck workflows, supports parallel/sequential tasks, conditional branching, and process analytics. Integrated with EventBus for real-time workflow events.

**Key Capabilities:**

- BPMN 2.0 workflow execution (parallel, sequential, conditional)
- Process instance lifecycle management (start, pause, resume, cancel, restart)
- Task assignment and routing (manual, automatic, AI-assisted)
- AI-powered recommendations for stuck workflows (via AI Orchestrator)
- Workflow analytics and performance metrics
- Event-driven workflow triggers (EventBus integration)
- Workflow versioning and migration
- Sub-process and nested workflow support
- Process monitoring and debugging
- Compensation and error handling
- *...and 2 more*

**Features:**

- {'name': 'BPMN 2.0 Engine', 'description': 'Full BPMN 2.0 specification compliance', 'endpoints': 10, 'components': ['Process engine core', 'Task executor', 'Event handler', 'Gateway processor']}
- {'name': 'Process Management', 'description': 'Workflow instance lifecycle and monitoring', 'endpoints': 8, 'components': ['Instance manager', 'State tracker', 'Version controller']}
- {'name': 'Task Management', 'description': 'Task assignment, routing, and completion', 'endpoints': 7, 'components': ['Task queue', 'Assignment engine', 'Completion tracker']}
- {'name': 'AI Recommendations', 'description': 'AI-powered workflow optimization and unsticking', 'endpoints': 3, 'components': ['Stuck detector', 'AI advisor client', 'Recommendation executor']}
- {'name': 'Analytics & Monitoring', 'description': 'Process analytics and performance tracking', 'endpoints': 4, 'components': ['Process metrics', 'Performance analyzer', 'Bottleneck detector']}

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| workflow_engine_requests_total | counter | > 2000/day | `N/A` |
| workflow_engine_response_time_ms | histogram | < 100ms | `N/A` |
| workflow_engine_error_rate | gauge | < 1% | `N/A` |
| workflow_engine_availability | gauge | > 99.9% | `N/A` |
| workflow_instances_active | gauge | Track trends | `N/A` |

**API Endpoints:**

- `http://localhost:8030` - base_url
- `/health` - health
- `/metrics` - metrics
- `/docs` - api_docs
- `/api/workflow` - api_base

---

### Workflow Intelligence Engine - Cognitive Backbone

| Property | Value |
|----------|-------|
| **Service ID** | `workflow-intelligence` |
| **Version** | N/A |
| **Type** | intelligent_core/orchestration |
| **Status** | PRODUCTION |
| **Port** | `8037` |
| **Framework** | FastAPI |

**Description:**

> Cognitive backbone of the AI-Platform-ISO system providing intelligent workflow orchestration, case-based reasoning, PDCA lifecycle tracking, and ML-powered recommendations for Business Continuity Management workflows.

**Key Capabilities:**

- Temporal Cloud Workflow Orchestration (durable execution)
- PDCA Lifecycle (Plan-Do-Check-Act automation)
- Goals + Rules Governance (dual-layer optimization)
- Case Library (3 types: Workflow, Community, Simulation)
- ML Cross-Module Learning (pattern transfer & success prediction)
- Benchmarking (statistical comparison with peers)
- Self-Monitoring (system validates itself every 60s)

**Features:**

- Temporal Cloud Integration (resilient workflows)
- PDCA Rules Engine (446 lines, PostgreSQL persistence)
- Goals Engine (positive optimization targets)
- Rules Engine V2 (5-tier hierarchy)
- Governance Orchestrator (unified decision center)
- *...and 4 more*

**Required Dependencies:**

- Temporal Cloud - workflow orchestration
- PostgreSQL - workflow state, PDCA cycles, cases
- Redis - EventBus messaging
- Qdrant - vector similarity search

**Integrations:**

| Service | Type | Description |
|---------|------|-------------|
| All platform services | workflow_orchestration | Orchestrates BIA, Risk, Planning, Valida... |
| AI Foundation | ai_capabilities | Uses LLM for analysis, RAG for context... |
| Community Intelligence | case_sync | Syncs approved cases to library... |
| EventBus | choreography | Publishes workflow events, PDCA events... |

**Key Performance Indicators:**

| KPI | Type | Target | Metric |
|-----|------|--------|--------|
| workflow_intelligence_cases_total | gauge | N/A | `N/A` |
| workflow_intelligence_workflows_active | gauge | N/A | `N/A` |
| workflow_intelligence_ml_predictions_total | counter | N/A | `N/A` |
| workflow_intelligence_pdca_cycles_total | counter | N/A | `N/A` |
| workflow_intelligence_case_search_duration_ms | histogram | N/A | `N/A` |

---

---

## 🔌 Port Allocation Reference

| Service | Port | Type | Status |
|---------|------|------|--------|
| BCM Vector Search (Qdrant Cloud) | `443` | vector_database | production |
| Grafana Dashboards | `3000` | observability/visualization | production |
| BCM Platform Database (PostgreSQL via Supabase) | `5432` | database | production |
| Platform Message Queue (RabbitMQ) | `5672` | infrastructure/runtime | planned |
| Platform Redis Cache | `6379` | cache | running |
| AI-Powered API Gateway | `8000` | infrastructure/gateway | production |
| Authentication & Authorization Service | `8001` | security/auth | production |
| AI Orchestrator - The Brain | `8002` | intelligent_core/orchestration | active |
| Planning Service - BC Strategy Development | `8011` | platform_services/bcm | production |
| BIA Service - Business Impact Analysis | `8012` | platform_services/bcm | production |
| Compliance Service | `8014` | platform_services/compliance | active |
| Learning Service - Training & Competence Management | `8021` | platform_services/bcm | production |
| Validation Service - Exercises, Audits, Reviews & CAPA | `8022` | platform_services/bcm | production |
| Plans Service | `8023` | platform_services/bcm | active |
| Documents Service | `8024` | platform_services/document_management | active |
| Governance Service | `8025` | platform_services/governance | active |
| Risk Service | `8026` | platform_services/risk | active |
| Response Service | `8027` | platform_services/incident_response | active |
| Community Intelligence - Peer Knowledge Sharing | `8030` | intelligent_core/community | production |
| Unified Workflow Engine | `8030` | intelligent_core/workflow_orchestration | active |
| Predictive Journey Service | `8031` | intelligent_core/predictive | active |
| Event Intelligence & Self-Healing | `8032` | intelligent_core/event_intelligence | active |
| Multi-Agent Coordination Center | `8033` | intelligent_core/coordination | planned |
| Collective Intelligence Agent Networks | `8034` | intelligent_core/collective-intelligence | active |
| Workflow Intelligence Engine - Cognitive Backbone | `8037` | intelligent_core/orchestration | production |
| AI Workflow Optimizer | `8038` | intelligent_core/workflow-optimization | active |
| AI Foundation - Core AI Infrastructure | `8040` | intelligent_core/ai_infrastructure | production |
| MIO Manager - Platform Observatory & Coordinator | `8046` | ai_office/coordinator | production |
| Real-time WebSocket Service | `8050` | infrastructure/runtime | running |
| System BCM Service - Platform Self-Application of Business Continuity | `8050` | intelligent_core/self_application | production |
| DB Intelligence - Database Performance Specialist | `8051` | ai_office/specialist | production |
| Analytics Specialist - Platform Intelligence | `8056` | ai_office/specialist | production |
| Agent Router - Request Routing & Load Balancing | `8057` | ai_office/router | production |
| DevOps Agent - Infrastructure & Platform Compliance | `8058` | ai_office/specialist | production |
| Project & Code Quality Agent | `8060` | ai_office/specialist | production |
| HashiCorp Vault - Secrets Manager | `8200` | security/secrets | configured |
| Service Discovery v2.0 - Unified Catalog + Registry | `8500` | infrastructure/runtime | running |
| Prometheus Metrics Server | `9090` | observability/metrics | production |

## 🛠️ Technology Stack Summary

### Frameworks Used

- **FastAPI** (21 services)

### Databases Used

- **PostgreSQL** (21 services)
- **Redis** (11 services)

---

*Comprehensive documentation generated on 2025-10-11T02:32:11.972909Z*

**Legend:**
- 🏢 Platform Services
- 🧠 Intelligent Core
- 🔒 Security & Gateway
- 📊 Observability
- 💾 Infrastructure