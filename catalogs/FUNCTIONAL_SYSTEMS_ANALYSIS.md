# Functional Systems Analysis - AI Platform ISO 22301

**Generated:** 2025-10-12 17:57:07

**Source:** `/Users/MD/AI-Platform-ISO/infrastructure/SERVICE_CATALOG_DETAILED.yaml`

**Total Services in Catalog:** 45

**Active Services:** 30

**Deprecated Services:** 4


---


## Executive Summary


This document provides a comprehensive functional systems analysis of the AI-powered BCM (Business Continuity Management) platform. 
The platform consists of **46+ services** organized into **13 technical categories** and mapped to **19 functional systems**.


The platform implements ISO 22301 standards with AI-powered capabilities including:

- **Intelligent orchestration** with multi-agent coordination

- **Self-healing** and resilience mechanisms

- **Predictive analytics** for risk forecasting

- **Community intelligence** for peer knowledge sharing

- **Evolution & self-learning** capabilities

- **Complete BCM lifecycle** management (BIA, Risk, Plans, Response)


---


## Table of Contents


1. [Complete Service Inventory](#complete-service-inventory)

2. [Functional Systems Overview](#functional-systems-overview)

3. [Detailed Functional Systems](#detailed-functional-systems)

4. [Service Categories](#service-categories)

5. [Integration Map](#integration-map)

6. [Deployment Status](#deployment-status)

---


## 1. Complete Service Inventory


### All 46 Services by Category


### Database Infrastructure


**1. BCM Platform Database (PostgreSQL via Supabase)** ✅

- **Service Name:** `postgresql`

- **Status:** production

- **Port:** 5432

- **Description:** Primary relational database for the entire AI-powered BCM platform. Provides 29 schemas for modular architecture with Row-Level Security (RLS) for mul

- **Key Capabilities:**

  - 29 database schemas (System, Platform, Business)

  - 46 applied migrations

  - Row-Level Security (RLS) for multi-tenancy

  - Full BCM business logic (BIA, Risk, Governance, Compliance)

  - AI memory and learning data

**2. Platform Redis Cache** ✅

- **Service Name:** `redis`

- **Status:** running

- **Port:** 6379

- **Description:** In-memory data store providing caching, session storage, rate limiting, and pub/sub messaging for the entire platform.

- **Key Capabilities:**

  - Caching layer (reduce database load)

  - Session storage (user sessions)

  - Rate limiting (API throttling)

  - Service registry (service discovery)

  - Pub/Sub messaging (optional EventBus backend)

**3. BCM Vector Search (Qdrant Cloud)** ✅

- **Service Name:** `qdrant`

- **Status:** production

- **Port:** 443

- **Description:** Vector database for semantic search, RAG (Retrieval-Augmented Generation), case library, and AI agent memory.

- **Key Capabilities:**

  - RAG document retrieval

  - Semantic search across workflow cases

  - Knowledge graph similarity search

  - Long-term memory for AI agents

**4. Unified Database Access Layer** ✅

- **Service Name:** `database_managers`

- **Status:** production

- **Port:** None

- **Description:** Centralized database access library providing unified API for all database operations across the platform.

- **Key Capabilities:**

  - Unified database API

  - Connection pooling

  - Session management (Redis-based)

  - Caching layer (decorator-based)

  - Rate limiting (multi-strategy)

### Runtime Services


**5. Service Discovery v2.0 - Unified Catalog + Registry** ✅

- **Service Name:** `service_discovery`

- **Status:** running

- **Port:** 8500

- **Description:** Complete service discovery, registry, health monitoring, and Service Catalog integration. Provides unified view combining static catalog with dynamic 

- **Key Capabilities:**

  - Service Catalog Integration (YAML templates)

  - Service Registry (track runtime instances)

  - Unified View (merge catalog + registry)

  - Health Monitoring (Docker, HTTP, custom)

  - ISO 22301 Mapping (12 services)

**6. Real-time WebSocket Service** ✅

- **Service Name:** `realtime_websocket`

- **Status:** running

- **Port:** 8050

- **Description:** Real-time communications, live updates, and collaborative features for BCM Platform. Provides WebSocket connections for chat, notifications, and event

- **Key Capabilities:**

  - WebSocket connections (multi-user, multi-channel)

  - Real-time chat messaging

  - System notifications broadcasting

  - User presence tracking (online/away/busy)

  - Typing indicators

**7. Platform Message Queue (RabbitMQ)** 📋

- **Service Name:** `message_queue`

- **Status:** planned

- **Port:** 5672

- **Description:** Asynchronous message queue for task distribution, job processing, and reliable message delivery across microservices.

- **Key Capabilities:**

  - Task queue management

  - Job scheduling and distribution

  - Dead letter queue handling

  - Message persistence

  - Priority queuing

### Gateway Layer


**8. AI-Powered API Gateway** ✅

- **Service Name:** `api_gateway`

- **Status:** production

- **Port:** 8000

- **Description:** Unified API gateway with intelligent routing, authentication, rate limiting, and AI-powered request optimization.

- **Key Capabilities:**

  - Unified API entry point (single endpoint)

  - JWT authentication & authorization

  - Rate limiting (token bucket, sliding window, fixed window)

  - Request/response logging & audit

  - Load balancing (round-robin, least-connections, weighted)

### Observability


**9. Prometheus Metrics Server** ✅

- **Service Name:** `prometheus`

- **Status:** production

- **Port:** 9090

- **Description:** Time-series database and metrics collection system for platform-wide monitoring. Scrapes metrics from all services and stores them for querying and al

- **Key Capabilities:**

  - Metrics collection via /metrics endpoints

  - Time-series data storage

  - PromQL query language

  - Alerting rules engine

  - Service discovery integration

**10. Grafana Dashboards** ✅

- **Service Name:** `grafana`

- **Status:** production

- **Port:** 3000

- **Description:** Visualization and analytics platform with 18 pre-configured dashboards for monitoring platform health, services, and business metrics.

- **Key Capabilities:**

  - Interactive dashboards

  - 18 pre-configured dashboards

  - Multiple data sources (Prometheus, Loki, PostgreSQL)

  - Alerting and notifications

  - User management and RBAC

### EventBus Core


**11. Platform EventBus (Clean Architecture)** ✅

- **Service Name:** `eventbus`

- **Status:** production

- **Port:** None

- **Description:** Clean architecture event system supporting choreography pattern for loosely-coupled microservices communication.

- **Key Capabilities:**

  - Event publishing and subscription

  - Multiple backends (Memory, Redis Streams)

  - Event filtering by pattern

  - Async/await support

  - Type-safe event definitions

### Security


**12. Authentication & Authorization Service** ✅

- **Service Name:** `auth_service`

- **Status:** production

- **Port:** 8001

- **Description:** JWT-based authentication and RBAC authorization service for platform-wide access control.

- **Key Capabilities:**

  - User authentication (JWT tokens)

  - Role-Based Access Control (RBAC)

  - OAuth2 integration (planned)

  - Session management

  - Token refresh mechanism

**13. HashiCorp Vault - Secrets Manager** 🟡

- **Service Name:** `vault`

- **Status:** configured

- **Port:** 8200

- **Description:** Centralized secrets management with encryption as a service, dynamic secrets, and audit logging.

- **Key Capabilities:**

  - Secrets storage (KV v2)

  - Dynamic secrets generation

  - Encryption as a service

  - Audit logging

  - Secret rotation

### AI Office


**14. MIO Manager - Platform Observatory & Coordinator** ✅

- **Service Name:** `mio_manager`

- **Status:** production

- **Port:** 8046

- **Description:** EYES Observatory pattern - monitors platform-wide health, coordinates AI Office team, and publishes events via EventBus (choreography pattern). Does N

- **Key Capabilities:**

  - Platform-wide health monitoring (all services)

  - Prometheus metrics coverage analysis

  - Service Discovery coverage monitoring

  - Infrastructure state tracking (postgres_available, redis_available)

  - EventBus choreography coordination

**15. DB Intelligence - Database Performance Specialist** ✅

- **Service Name:** `db_intelligence`

- **Status:** production

- **Port:** 8051

- **Description:** Deep database performance analysis, query optimization, and admin operations for PostgreSQL. AI-powered recommendations using LLM + pg_stat_statements

- **Key Capabilities:**

  - Query performance analysis (pg_stat_statements)

  - Slow query detection and optimization

  - AI-powered index recommendations (LLM)

  - Table statistics monitoring (bloat, vacuum status)

  - Security monitoring (RLS, SQL injection, deadlocks)

**16. Analytics Specialist - Platform Intelligence** ✅

- **Service Name:** `analytics_specialist`

- **Status:** production

- **Port:** 8056

- **Description:** Platform-wide analytics, metrics discovery, dependency mapping, and bottleneck detection using AI-powered code analysis.

- **Key Capabilities:**

  - Metrics discovery (scan codebase for metrics)

  - Dependency mapping (import analysis)

  - API endpoint discovery

  - Security scanning (code vulnerabilities)

  - Bottleneck detection

**17. DevOps Agent - Infrastructure & Platform Compliance** ✅

- **Service Name:** `devops_agent`

- **Status:** production

- **Port:** 8058

- **Description:** AI-powered infrastructure management with platform compliance toolkit. Monitors containers, validates compliance, and provides auto-remediation.

- **Key Capabilities:**

  - Platform Compliance (6 priorities)

  - Priority 1: Port conflict detection

  - Priority 2: Metrics integration validation (Prometheus/Grafana)

  - Priority 3: Database connection checks (PostgreSQL/Redis)

  - Priority 4: KPI registration validation

**18. Project & Code Quality Agent** ✅

- **Service Name:** `project_agent`

- **Status:** production

- **Port:** 8060

- **Description:** Project management + code quality analysis + testing coverage. AI-powered test generation and compliance validation.

- **Key Capabilities:**

  - Project & task management

  - Progress tracking and reporting

  - Code security scanning

  - Code quality analysis

  - Testing coverage analysis

**19. Agent Router - Request Routing & Load Balancing** ✅

- **Service Name:** `agent_router`

- **Status:** production

- **Port:** 8057

- **Description:** Intelligent request routing, load balancing, and circuit breaker for AI Office team coordination.

- **Key Capabilities:**

  - Request routing to AI specialists

  - Load balancing

  - Circuit breaker pattern

  - Health-based routing

  - Failover handling

### Shared Libraries


**20. Shared Libraries & Utilities** 🟢

- **Service Name:** `shared`

- **Status:** active

- **Port:** N/A

- **Description:** Cross-platform shared libraries and utilities used across all services. Provides authentication, database access, EventBus integration, audit trails, 

**21. Testing Infrastructure** 🟢

- **Service Name:** `tests`

- **Status:** active

- **Port:** N/A

- **Description:** Comprehensive testing infrastructure including integration tests, unit tests, end-to-end tests, load tests, and test fixtures for all platform service

### Platform Services


**22. Planning Service - BC Strategy Development** ✅

- **Service Name:** `planning_service`

- **Status:** production

- **Port:** 8011

- **Description:** Business Continuity Strategy development and selection service aligned with ISO 22301:2019 Clause 8.3 requirements. Provides cost-benefit analysis, re

- **Key Capabilities:**

  - BC Strategy Development (based on BIA results)

  - Cost-Benefit Analysis (NPV, ROI, Payback Period)

  - Resource Planning (personnel, technology, facilities)

  - Approval Workflow (Draft → Review → Approved)

  - Financial Modeling (multi-year TCO & benefit projections)

**23. BIA Service - Business Impact Analysis** ✅

- **Service Name:** `bia_service`

- **Status:** production

- **Port:** 8012

- **Description:** Comprehensive Business Impact Analysis service aligned with ISO 22301:2019 Clause 8.2.2. Provides RTO/RPO/MTPD calculations, financial impact assessme

- **Key Capabilities:**

  - RTO/RPO/MTPD Calculations

  - Financial Impact Assessment (1 hour to 1 month)

  - Dependency Mapping (upstream/downstream)

  - Critical Process Identification (automated criticality scoring)

  - AI-Powered Analysis (RTO suggestions, dependency discovery)

**24. Learning Service - Training & Competence Management** ✅

- **Service Name:** `learning_service`

- **Status:** production

- **Port:** 8021

- **Description:** ISO 22301 Training & Competence Management service for BCM awareness, training programs, competency assessments, and gamification.

- **Key Capabilities:**

  - Training Programs management

  - Enrollment tracking

  - Competency Assessments

  - Awareness Campaigns

  - Gamification (points, badges, leaderboards)

**25. Validation Service - Exercises, Audits, Reviews & CAPA** ✅

- **Service Name:** `validation_service`

- **Status:** production

- **Port:** 8022

- **Description:** ISO 22301 Validation Module covering Exercises (8.5), Performance Monitoring (9.1), Internal Audits (9.2), Management Reviews (9.3), and Continuous Im

- **Key Capabilities:**

  - Exercise Management (tabletop, simulation, full-scale)

  - Performance Monitoring & KPIs (automated collection & alerts)

  - Internal Audits (ISO 9.2 compliance)

  - Management Reviews (ISO 9.3 requirements)

  - CAPA Management (Corrective & Preventive Actions)

**26. Plans Service** 🟢

- **Service Name:** `plans_service`

- **Status:** active

- **Port:** 8023

- **Description:** Business Continuity Plans & Procedures management service. Manages BC plans, procedures, resources, plan lifecycle, reviews, and activations. Implemen

- **Key Capabilities:**

  - Business continuity plan management (10+ endpoints)

  - Plan lifecycle workflow (Draft → Review → Approved → Active → Archived)

  - Procedure management with sequencing (4 endpoints)

  - Resource allocation and tracking (7 resource types: personnel, tech, facilities)

  - Contact lists with call tree structure

**27. Documents Service** 🟢

- **Service Name:** `documents_service`

- **Status:** active

- **Port:** 8024

- **Description:** Enterprise document lifecycle management with AI/NLP capabilities, approval workflows, version control, and retention policies. Implements ISO 22301 C

- **Key Capabilities:**

  - Document lifecycle management (Draft → Review → Approved → Published → Archived)

  - AI/NLP document processing (extraction, classification, analysis, summarization)

  - Version control with diff comparison

  - Multi-stage approval workflows (5 stages with SLAs)

  - Retention policies (ISO 22301 + HIPAA compliance)

**28. Governance Service** 🟢

- **Service Name:** `governance_service`

- **Status:** active

- **Port:** 8025

- **Description:** Organizational governance framework implementation for BCM. Manages stakeholder engagement, decision-making processes, organizational context analysis

- **Key Capabilities:**

  - Stakeholder management and engagement tracking

  - Governance structure definition (roles, committees)

  - Decision-making process management

  - Organizational context analysis (PESTLE, SWOT)

  - BCM policy framework management

**29. Compliance Service** 🟢

- **Service Name:** `compliance_service`

- **Status:** active

- **Port:** 8014

- **Description:** Comprehensive compliance management for ISO 22301. Manages assessments, gap analysis, evidence collection, nonconformity management (RCA), internal au

- **Key Capabilities:**

  - Compliance assessments against ISO 22301, HIPAA, SOC2, GDPR

  - Gap analysis and remediation tracking

  - Evidence collection and management

  - Internal audit planning and execution (Clause 9.2)

  - Nonconformity management with Root Cause Analysis (Clause 10.1)

**30. Risk Service** 🟢

- **Service Name:** `risk_service`

- **Status:** active

- **Port:** 8026

- **Description:** Comprehensive risk management including risk identification, assessment, treatment planning, monitoring, and reporting. Provides risk matrices, heat m

- **Key Capabilities:**

  - Risk identification and cataloging

  - Risk assessment (likelihood × impact matrix)

  - Risk treatment planning (avoid, reduce, transfer, accept)

  - Risk monitoring and tracking

  - Risk heat maps and visualization

**31. Response Service** 🟢

- **Service Name:** `response_service`

- **Status:** active

- **Port:** 8027

- **Description:** Comprehensive incident response management. Manages incidents, response actions, response teams, communications, timeline tracking, recovery metrics (

- **Key Capabilities:**

  - Incident lifecycle management (New → Active → Contained → Resolved → Closed)

  - Response action tracking and assignment

  - Response team management and coordination

  - Incident communications log

  - Chronological incident timeline

### Intelligent Core


**32. Workflow Intelligence Engine - Cognitive Backbone** ✅

- **Service Name:** `workflow_intelligence`

- **Status:** production

- **Port:** 8037

- **Description:** Cognitive backbone of the AI-Platform-ISO system providing intelligent workflow orchestration, case-based reasoning, PDCA lifecycle tracking, and ML-p

- **Key Capabilities:**

  - Temporal Cloud Workflow Orchestration (durable execution)

  - PDCA Lifecycle (Plan-Do-Check-Act automation)

  - Goals + Rules Governance (dual-layer optimization)

  - Case Library (3 types: Workflow, Community, Simulation)

  - ML Cross-Module Learning (pattern transfer & success prediction)

**33. AI Foundation - Core AI Infrastructure** ✅

- **Service Name:** `ai_foundation`

- **Status:** production

- **Port:** 8040

- **Description:** Core AI infrastructure providing LLM routing, RAG (Retrieval Augmented Generation), ML models, self-learning, and context building for all platform se

- **Key Capabilities:**

  - LLM Routing (OpenAI, Anthropic, multi-provider)

  - RAG Pipeline (embeddings, retrieval, reranking)

  - ML Models (predictive, anomaly detection)

  - Self-Learning Engine (pattern extraction, rule generation)

  - Context Building (workflow, domain, tenant context)

**34. Expertise Center - Domain Specialists & AI Assistants** ✅

- **Service Name:** `expertise_center`

- **Status:** production

- **Port:** None

- **Description:** Domain-specific expertise and specialized AI assistants for Business Continuity Management. Implements tactical assistants for BIA, compliance, govern

- **Key Capabilities:**

  - Domain-Specific AI Assistants (BIA, Compliance, Risk, Governance)

  - Tactical BCM Specialists

  - Expert Knowledge Management

  - Domain-Specific RAG (specialized knowledge bases)

  - AI Colleagues (BCM project intelligence)

**35. Community Intelligence - Peer Knowledge Sharing** ✅

- **Service Name:** `community_intelligence`

- **Status:** production

- **Port:** 8030

- **Description:** Community-driven knowledge creation service enabling peer-reviewed knowledge sharing through automated workflow integration, expert validation, reputa

- **Key Capabilities:**

  - Auto-Contribution (workflow completions → shareable cases)

  - Peer Review System (smart reviewer matching, quality scoring)

  - Reputation Engine (gamification, points, badges, leaderboards)

  - Case Library (searchable knowledge base with anonymization)

  - Event Integration (workflow triggers, EventBus publishing)

**36. Unified Workflow Engine** 🟢

- **Service Name:** `workflow_engine`

- **Status:** active

- **Port:** 8030

- **Description:** Domain-agnostic BPMN 2.0 workflow engine for orchestrating complex business processes. Executes workflows designed by Workflow Intelligence, provides 

- **Key Capabilities:**

  - BPMN 2.0 workflow execution (parallel, sequential, conditional)

  - Process instance lifecycle management (start, pause, resume, cancel, restart)

  - Task assignment and routing (manual, automatic, AI-assisted)

  - AI-powered recommendations for stuck workflows (via AI Orchestrator)

  - Workflow analytics and performance metrics

**37. AI Orchestrator - The Brain** 🟢

- **Service Name:** `ai_orchestration`

- **Status:** active

- **Port:** 8002

- **Description:** Autonomous AI decision-making system with 4-layer memory, safety-first architecture, and self-evolution capabilities. Aggregates context from multiple

- **Key Capabilities:**

  - Autonomous decision-making with multi-factor priority scoring

  - 4-layer memory system (Working Redis 1h, Short-term PostgreSQL 30d, Long-term Case Library, Procedural ML Models)

  - Context aggregation from workflows, events, databases, external sources

  - Strategy selection from historical cases and learned patterns

  - Safety-first architecture (Constitution, Loop Detection, Hallucination Check, Control Monitor)

**38. Event Intelligence & Self-Healing** 🟢

- **Service Name:** `event_intelligence`

- **Status:** active

- **Port:** 8032

- **Description:** Intelligent event analysis, pattern detection, domain detection, error analysis, and automated code healing for platform stability and resilience. Sub

- **Key Capabilities:**

  - Real-time event stream analysis (all platform events)

  - Pattern detection and anomaly identification

  - Domain detection (auto-classify events by business domain)

  - Error analysis and root cause identification

  - Automated code healing and self-repair

**39. Predictive Journey Service** 🟢

- **Service Name:** `predictive`

- **Status:** active

- **Port:** 8031

- **Description:** AI-powered forecasting for BCM journeys. Predicts milestones, certification timelines, expert demands, and challenges using pattern matching, statisti

- **Key Capabilities:**

  - 90-day journey timeline prediction (3-6 milestones)

  - ISO 22301 certification date forecasting

  - Expert marketplace demand forecasting

  - Daily proactive digest generation (8:00 AM schedule)

  - Challenge prediction with mitigation strategies

**40. Multi-Agent Coordination Center** 📋

- **Service Name:** `coordination_center`

- **Status:** planned

- **Port:** 8033

- **Description:** Multi-agent coordination and collaboration hub. Manages agent teams, task allocation, inter-agent communication, and collaborative problem-solving. PL

- **Key Capabilities:**

  - Multi-agent team formation and management

  - Dynamic task allocation and scheduling

  - Inter-agent communication protocols

  - Collaborative problem-solving strategies

  - Consensus building and conflict resolution

**41. Collective Intelligence Agent Networks** 🟢

- **Service Name:** `collective`

- **Status:** active

- **Port:** 8034

- **Description:** Privacy-preserving knowledge sharing across organizations through temporary AI agents synthesized from anonymized collective wisdom. Enables organizat

- **Key Capabilities:**

  - Automatic stuck organization detection (7-day progress monitoring)

  - Privacy-preserving collective agent creation (k-anonymity k≥5)

  - Multi-layer anonymization (4 layers: org, journey, pattern, metrics)

  - Temporary agent lifecycle management (7-day expiration)

  - Aggregate statistical framing without source attribution

**42. AI Workflow Optimizer** 🟢

- **Service Name:** `ai_workflow_optimizer`

- **Status:** active

- **Port:** 8038

- **Description:** ML-powered workflow optimization service that analyzes business process performance, identifies bottlenecks, predicts execution times, detects anomali

- **Key Capabilities:**

  - ML-based workflow performance prediction (Random Forest)

  - Bottleneck detection and resource optimization

  - Anomaly detection using Isolation Forest

  - Workflow clustering and pattern recognition (K-Means)

  - Execution time forecasting with confidence intervals

**43. System BCM Service - Platform Self-Application of Business Continuity** ✅

- **Service Name:** `system_bcm_service`

- **Status:** production

- **Port:** 8050

- **Description:** Production service that applies BCM to the platform itself in real-time. Continuously monitors platform health, executes BCM cycles every 24 hours, tr

- **Key Capabilities:**

  - Applies BCM to platform in real-time (24-hour continuous cycles)

  - Automatic recovery procedures (7 procedures with RTO monitoring)

  - Platform health monitoring (29 services + 6 infrastructure components)

  - EventBus integration for platform events (4 subscriptions, 5 publications)

  - Self-learning from platform operations and recovery outcomes

### Interface Layer


**44. MCP Interface - Model Context Protocol** ⚪

- **Service Name:** `mcp_interface`

- **Status:** reserved

- **Port:** N/A

- **Description:** RESERVED: Model Context Protocol (MCP) interface for standardized communication between AI models and external tools/data sources. Enables seamless in

**45. Admin Panel - System Administration** ⚪

- **Service Name:** `admin_panel`

- **Status:** reserved

- **Port:** N/A

- **Description:** RESERVED: Administrative control panel for system monitoring, configuration management, user administration, and operational oversight of the entire A

**46. Platform UI - End-User Interface** ⚪

- **Service Name:** `platform_ui`

- **Status:** reserved

- **Port:** N/A

- **Description:** RESERVED: Primary end-user interface for business continuity management, BCM workflows, compliance tracking, and all platform services. Provides intui


**Total Services Listed:** 46

---


## 2. Functional Systems Overview


The platform is organized into **19 functional systems** that work together to provide comprehensive BCM capabilities:


| # | Functional System | Purpose | Key Services |

|---|------------------|---------|--------------|

| 🚀 | **Система запуска и оркестрации (Startup & Orchestration)** | Manages service lifecycle, coordinates startup, monitors system state | `service-discovery, mio-manager, ai-orchestration` |

| 🛡️ | **Система отказоустойчивости (Resilience & Failover)** | Ensures continuous operation, recovery after failures, self-healing capabilities | `event-intelligence, system-bcm-service, api-gateway (circuit breaker)` |

| 🔒 | **Система безопасности (Security & Access Control)** | Authentication, authorization, secrets management, security audit | `auth-service, vault, api-gateway (auth)` |

| 📊 | **Система мониторинга и наблюдаемости (Monitoring & Observability)** | Metrics, logs, tracing, visualization, alerting | `prometheus, grafana, mio-manager` |

| 🔍 | **Система аналитики (Analytics & Intelligence)** | Data analysis, business intelligence, pattern detection, insights | `analytics-specialist, db-intelligence, process-analytics` |

| 💾 | **Система хранения данных (Data Storage)** | Storage of relational, cache, vector, and time-series data | `postgresql, redis, qdrant` |

| 🌐 | **API и коммуникации (API & Communication)** | HTTP API, WebSocket, message queues, sync/async communication | `api-gateway, realtime-websocket, message-queue` |

| 📚 | **Система обучения и знаний (Learning & Knowledge)** | Knowledge management, personnel training, competencies, self-learning AI | `learning-service, ai-foundation (RAG), expertise-center` |

| 🔮 | **Система предсказаний (Predictive Intelligence)** | Risk forecasting, machine learning, predictive analytics | `predictive, analytics-specialist, ai-foundation (ML)` |

| 🤖 | **AI Оркестрация (AI Orchestration)** | AI agent coordination, task distribution, collective intelligence | `ai-orchestration, agent-router, coordination-center` |

| 👥 | **Коллективный AI (Community Intelligence)** | Peer knowledge sharing, community insights, collaborative learning | `community-intelligence, collective, expertise-center` |

| 🧬 | **Система эволюции (Evolution & Self-Improvement)** | Self-learning, adaptation, automatic system improvement | `event-intelligence, ai-orchestration (evolution), learning-service` |

| 📋 | **BCM Business Logic** | BCM business logic: BIA, Risk, Plans, Governance, Compliance | `bia-service, risk-service, plans-service` |

| ⚙️ | **Workflow Management** | Business process management, workflow engine, orchestration | `workflow-intelligence, workflow-engine, ai-workflow-optimizer` |

| 📡 | **Event-Driven Architecture** | Asynchronous event processing, pub/sub, event sourcing | `eventbus, event-intelligence, realtime-websocket` |

| 🧠 | **AI Foundation Infrastructure** | Core AI capabilities: RAG, embeddings, LLM integration | `ai-foundation, qdrant (vectors), expertise-center` |

| 🔧 | **DevOps & Infrastructure** | Deployment automation, CI/CD, infrastructure management | `devops-agent, project-agent, service-discovery` |

| ✅ | **Testing & Validation** | Testing, validation, exercises, audit, CAPA | `validation-service, tests (shared), devops-agent` |

| 🖥️ | **User Interface Layer** | Web interfaces, admin panels, end-user UI | `admin-panel, platform-ui, mcp-interface` |

---


## 3. Detailed Functional Systems


### Система запуска и оркестрации (Startup & Orchestration)


**Назначение:** Управляет жизненным циклом всех сервисов платформы, координирует запуск, мониторит состояние системы и обеспечивает правильную последовательность инициализации компонентов.


**Сервисы:**

- ✅ **Service Discovery v2.0 - Unified Catalog + Registry** (`service-discovery`, port: 8500, status: running)

- ✅ **MIO Manager - Platform Observatory & Coordinator** (`mio-manager`, port: 8046, status: production)

- 🟢 **AI Orchestrator - The Brain** (`ai-orchestration`, port: 8002, status: active)

- ✅ **Agent Router - Request Routing & Load Balancing** (`agent-router`, port: 8057, status: production)

- 📋 **Multi-Agent Coordination Center** (`coordination-center`, port: 8033, status: planned)


**Ключевые возможности:**

- Service registry and discovery

- Health monitoring всех сервисов

- Lifecycle management (start/stop/restart)

- Dependency resolution

- Coordinated startup sequences

- Service catalog integration


**Зависимости:** Redis (для реестра), EventBus (для событий), PostgreSQL (для состояния)


**Критично для:** Запуск и работа всей платформы



### Система отказоустойчивости (Resilience & Failover)


**Назначение:** Обеспечивает непрерывность работы платформы через механизмы восстановления после сбоев, автоматическое исцеление и резервирование критических компонентов.


**Сервисы:**

- 🟢 **Event Intelligence & Self-Healing** (`event-intelligence`, port: 8032, status: active)

- ✅ **System BCM Service - Platform Self-Application of Business Continuity** (`system-bcm-service`, port: 8050, status: production)

- ✅ **AI-Powered API Gateway** (`api-gateway`, port: 8000, status: production)


**Ключевые возможности:**

- Self-healing mechanisms

- Circuit breaker pattern

- Automatic failover

- Health checks and recovery

- Incident detection and response

- System resilience monitoring

- BCM principles applied to platform itself


**Зависимости:** EventBus (события сбоев), Service Discovery (для failover), Monitoring (для детекции)


**Критично для:** Непрерывность работы (High Availability)



### Система безопасности (Security & Access Control)


**Назначение:** Обеспечивает защиту платформы через аутентификацию, авторизацию, управление секретами и аудит безопасности.


**Сервисы:**

- ✅ **Authentication & Authorization Service** (`auth-service`, port: 8001, status: production)

- 🟡 **HashiCorp Vault - Secrets Manager** (`vault`, port: 8200, status: configured)

- ✅ **AI-Powered API Gateway** (`api-gateway`, port: 8000, status: production)

- ✅ **DevOps Agent - Infrastructure & Platform Compliance** (`devops-agent`, port: 8058, status: production)


**Ключевые возможности:**

- JWT authentication

- RBAC authorization

- RLS (Row-Level Security) в PostgreSQL

- Secrets management (Vault)

- API key management

- Rate limiting

- Audit logging

- Security scanning


**Зависимости:** PostgreSQL (user profiles), Redis (sessions), Vault (secrets)


**Критично для:** Безопасность данных и доступа



### Система мониторинга и наблюдаемости (Monitoring & Observability)


**Назначение:** Предоставляет полную видимость состояния системы через метрики, логи, визуализацию и алертинг.


**Сервисы:**

- ✅ **Prometheus Metrics Server** (`prometheus`, port: 9090, status: production)

- ✅ **Grafana Dashboards** (`grafana`, port: 3000, status: production)

- ✅ **MIO Manager - Platform Observatory & Coordinator** (`mio-manager`, port: 8046, status: production)

- ✅ **DB Intelligence - Database Performance Specialist** (`db-intelligence`, port: 8051, status: production)

- ✅ **Analytics Specialist - Platform Intelligence** (`analytics-specialist`, port: 8056, status: production)


**Ключевые возможности:**

- Metrics collection (Prometheus)

- 18 Grafana dashboards

- 45 alert rules

- Database performance monitoring

- Platform intelligence

- KPI tracking

- Real-time health monitoring

- Distributed tracing (planned)


**Зависимости:** Service Discovery (target discovery), PostgreSQL (audit logs), Redis (cache)


**Критично для:** Observability и operational excellence



### Система аналитики (Analytics & Intelligence)


**Назначение:** Анализирует данные платформы для выявления паттернов, инсайтов и предоставления бизнес-аналитики.


**Сервисы:**

- ✅ **Analytics Specialist - Platform Intelligence** (`analytics-specialist`, port: 8056, status: production)

- ✅ **DB Intelligence - Database Performance Specialist** (`db-intelligence`, port: 8051, status: production)

- ✅ **Community Intelligence - Peer Knowledge Sharing** (`community-intelligence`, port: 8030, status: production)


**Ключевые возможности:**

- Platform analytics

- Code analysis (AST, dependency mapping)

- Database query optimization

- Pattern detection

- Performance analysis

- Business intelligence

- Peer insights


**Зависимости:** PostgreSQL (data), Prometheus (metrics), AI Foundation (ML models)


**Критично для:** Data-driven decision making



### Система хранения данных (Data Storage)


**Назначение:** Обеспечивает надежное хранение всех типов данных платформы: реляционных, кэш, векторных и временных рядов.


**Сервисы:**

- ✅ **BCM Platform Database (PostgreSQL via Supabase)** (`postgresql`, port: 5432, status: production)

- ✅ **Platform Redis Cache** (`redis`, port: 6379, status: running)

- ✅ **BCM Vector Search (Qdrant Cloud)** (`qdrant`, port: 443, status: production)

- ✅ **Unified Database Access Layer** (`database-managers`, port: None, status: production)


**Ключевые возможности:**

- 29 database schemas

- 46 applied migrations

- RLS multi-tenancy

- Cache layer (512MB Redis)

- Vector search (Qdrant Cloud)

- Connection pooling

- Session management

- Rate limiting


**Зависимости:** Supabase (PostgreSQL hosting), Qdrant Cloud (vectors)


**Критично для:** Data persistence и performance



### API и коммуникации (API & Communication)


**Назначение:** Обеспечивает все виды коммуникаций: HTTP API, WebSocket, message queues, синхронные и асинхронные взаимодействия.


**Сервисы:**

- ✅ **AI-Powered API Gateway** (`api-gateway`, port: 8000, status: production)

- ✅ **Real-time WebSocket Service** (`realtime-websocket`, port: 8050, status: running)

- 📋 **Platform Message Queue (RabbitMQ)** (`message-queue`, port: 5672, status: planned)

- ✅ **Platform EventBus (Clean Architecture)** (`eventbus`, port: None, status: production)


**Ключевые возможности:**

- Unified API entry point

- Real-time WebSocket connections

- Message queue (planned RabbitMQ)

- EventBus pub/sub

- Request routing

- Load balancing

- CORS handling

- Response caching


**Зависимости:** Service Discovery (routing), Redis (rate limiting), PostgreSQL (persistence)


**Критично для:** Communication между services и clients


### Система обучения и знаний (Learning & Knowledge)


**Назначение:** Управляет знаниями организации, обучением персонала, компетенциями и self-learning AI capabilities.


**Сервисы:**

- ✅ **Learning Service - Training & Competence Management** (`learning-service`, port: 8021, status: production)

- ✅ **AI Foundation - Core AI Infrastructure** (`ai-foundation`, port: 8040, status: production)

- ✅ **Expertise Center - Domain Specialists & AI Assistants** (`expertise-center`, port: None, status: production)

- ✅ **Community Intelligence - Peer Knowledge Sharing** (`community-intelligence`, port: 8030, status: production)


**Ключевые возможности:**

- Training programs management

- Competency tracking

- Knowledge base (RAG)

- Learning analytics

- Course recommendations

- Gamification

- Knowledge gap analysis

- Domain expertise access


**Зависимости:** PostgreSQL (training data), Qdrant (knowledge vectors), AI Foundation (embeddings)


**Критично для:** Continuous learning и competency management



### Система предсказаний (Predictive Intelligence)


**Назначение:** Прогнозирует риски, предсказывает события и предоставляет ML-powered аналитику для упреждающих действий.


**Сервисы:**

- 🟢 **Predictive Journey Service** (`predictive`, port: 8031, status: active)

- ✅ **Analytics Specialist - Platform Intelligence** (`analytics-specialist`, port: 8056, status: production)


**Ключевые возможности:**

- Risk forecasting

- Incident prediction

- Resource demand forecasting

- ML model training

- Pattern-based predictions

- Anomaly detection

- Predictive maintenance


**Зависимости:** PostgreSQL (historical data), AI Foundation (ML models), Prometheus (metrics)


**Критично для:** Proactive risk management



### AI Оркестрация (AI Orchestration)


**Назначение:** Координирует работу AI агентов, распределяет задачи, управляет коллективным интеллектом и обеспечивает intelligent decision-making.


**Сервисы:**

- 🟢 **AI Orchestrator - The Brain** (`ai-orchestration`, port: 8002, status: active)

- ✅ **Agent Router - Request Routing & Load Balancing** (`agent-router`, port: 8057, status: production)

- 📋 **Multi-Agent Coordination Center** (`coordination-center`, port: 8033, status: planned)

- 🟢 **Collective Intelligence Agent Networks** (`collective`, port: 8034, status: active)

- 🟢 **AI Workflow Optimizer** (`ai-workflow-optimizer`, port: 8038, status: active)


**Ключевые возможности:**

- Multi-agent coordination

- Task delegation

- Agent routing and load balancing

- Context aggregation

- Priority-based execution

- Strategy selection

- Memory management (short-term, distributed)

- Safety monitoring (hallucination detection, loop prevention)

- Evolution engine


**Зависимости:** Redis (memory), EventBus (coordination), Service Discovery (agent discovery)


**Критично для:** AI-powered automation и intelligent operations



### Коллективный AI (Community Intelligence)


**Назначение:** Обеспечивает peer knowledge sharing, community insights и collaborative learning между организациями.


**Сервисы:**

- ✅ **Community Intelligence - Peer Knowledge Sharing** (`community-intelligence`, port: 8030, status: production)

- 🟢 **Collective Intelligence Agent Networks** (`collective`, port: 8034, status: active)

- ✅ **Expertise Center - Domain Specialists & AI Assistants** (`expertise-center`, port: None, status: production)


**Ключевые возможности:**

- Peer knowledge sharing

- Community benchmarks

- Best practices exchange

- Collaborative learning

- Anonymous insights

- Industry patterns

- Collective problem-solving


**Зависимости:** PostgreSQL (community data), AI Foundation (analysis), Community Intelligence schema


**Критично для:** Industry collaboration и shared learning



### Система эволюции (Evolution & Self-Improvement)


**Назначение:** Обеспечивает self-learning, адаптацию и автоматическое улучшение системы через feedback loops.


**Сервисы:**

- 🟢 **Event Intelligence & Self-Healing** (`event-intelligence`, port: 8032, status: active)

- 🟢 **AI Orchestrator - The Brain** (`ai-orchestration`, port: 8002, status: active)

- ✅ **Learning Service - Training & Competence Management** (`learning-service`, port: 8021, status: production)


**Ключевые возможности:**

- Self-learning from events

- Pattern adaptation

- Performance optimization

- Evolution engine

- Feedback integration

- Automatic improvement suggestions

- System adaptation


**Зависимости:** EventBus (feedback), Monitoring (performance data), AI Foundation (ML)


**Критично для:** Continuous improvement и adaptation



### BCM Business Logic


**Назначение:** Реализует полный lifecycle BCM в соответствии с ISO 22301: BIA, Risk Management, Plan Development, Response, Governance, Compliance.


**Сервисы:**

- ✅ **BIA Service - Business Impact Analysis** (`bia-service`, port: 8012, status: production)

- 🟢 **Risk Service** (`risk-service`, port: 8026, status: active)

- 🟢 **Plans Service** (`plans-service`, port: 8023, status: active)

- 🟢 **Governance Service** (`governance-service`, port: 8025, status: active)

- 🟢 **Compliance Service** (`compliance-service`, port: 8014, status: active)

- 🟢 **Response Service** (`response-service`, port: 8027, status: active)

- ✅ **Planning Service - BC Strategy Development** (`planning-service`, port: 8011, status: production)

- 🟢 **Documents Service** (`documents-service`, port: 8024, status: active)

- ✅ **Validation Service - Exercises, Audits, Reviews & CAPA** (`validation-service`, port: 8022, status: production)

- ✅ **System BCM Service - Platform Self-Application of Business Continuity** (`system-bcm-service`, port: 8050, status: production)


**Ключевые возможности:**

- Business Impact Analysis (BIA)

- Risk Assessment & Treatment

- BC Plan Development

- Incident Response

- Governance framework

- ISO 22301 compliance

- Document management

- Validation & exercises

- CAPA (Corrective Actions)

- Platform self-application of BCM


**Зависимости:** PostgreSQL (all BCM schemas), Workflow Intelligence (processes), EventBus (incidents)


**Критично для:** Core BCM functionality и ISO 22301 compliance



### Workflow Management


**Назначение:** Управляет бизнес-процессами, обеспечивает workflow orchestration и cognitive process optimization.


**Сервисы:**

- ✅ **Workflow Intelligence Engine - Cognitive Backbone** (`workflow-intelligence`, port: 8037, status: production)

- 🟢 **Unified Workflow Engine** (`workflow-engine`, port: 8030, status: active)

- 🟢 **AI Workflow Optimizer** (`ai-workflow-optimizer`, port: 8038, status: active)


**Ключевые возможности:**

- Workflow definition & execution

- Process orchestration (Temporal)

- Cognitive workflow optimization

- State management

- Process analytics

- Workflow templates

- Long-running workflows

- Human-in-the-loop tasks


**Зависимости:** PostgreSQL (workflow state), Temporal (orchestration), AI Orchestration (cognitive)


**Критично для:** Business process automation


### Event-Driven Architecture


**Назначение:** Обеспечивает асинхронную обработку событий, pub/sub messaging и event sourcing для loose coupling между сервисами.


**Сервисы:**

- ✅ **Platform EventBus (Clean Architecture)** (`eventbus`, port: None, status: production)

- 🟢 **Event Intelligence & Self-Healing** (`event-intelligence`, port: 8032, status: active)

- ✅ **Real-time WebSocket Service** (`realtime-websocket`, port: 8050, status: running)


**Ключевые возможности:**

- Event publishing/subscribing

- Topic-based routing

- Priority queues (low, normal, high, critical)

- Event sourcing

- Real-time event streaming

- Event intelligence (pattern detection)

- Incident event handling

- WebSocket event broadcasting


**Зависимости:** Redis (optional backend), Message Queue (planned), PostgreSQL (event log)


**Критично для:** Decoupled architecture и event-driven workflows



### AI Foundation Infrastructure


**Назначение:** Предоставляет базовые AI capabilities: RAG, embeddings, LLM integration, semantic search.


**Сервисы:**

- ✅ **AI Foundation - Core AI Infrastructure** (`ai-foundation`, port: 8040, status: production)

- ✅ **BCM Vector Search (Qdrant Cloud)** (`qdrant`, port: 443, status: production)

- ✅ **Expertise Center - Domain Specialists & AI Assistants** (`expertise-center`, port: None, status: production)


**Ключевые возможности:**

- RAG (Retrieval-Augmented Generation)

- Vector embeddings (OpenAI ada-002)

- Semantic search

- Knowledge base connector

- LLM integration (OpenAI, Anthropic)

- Domain expertise AI assistants

- Context retrieval

- ML predictor


**Зависимости:** Qdrant (vectors), OpenAI API (embeddings), PostgreSQL (knowledge data)


**Критично для:** AI-powered features across platform



### DevOps & Infrastructure


**Назначение:** Автоматизирует развертывание, обеспечивает CI/CD, управляет инфраструктурой и compliance.


**Сервисы:**

- ✅ **DevOps Agent - Infrastructure & Platform Compliance** (`devops-agent`, port: 8058, status: production)

- ✅ **Project & Code Quality Agent** (`project-agent`, port: 8060, status: production)

- ✅ **Service Discovery v2.0 - Unified Catalog + Registry** (`service-discovery`, port: 8500, status: running)


**Ключевые возможности:**

- Infrastructure monitoring

- Deployment automation

- CI/CD pipeline management

- Code quality analysis

- Security scanning

- Compliance checking

- Container orchestration

- Service registration


**Зависимости:** Docker (containers), Service Discovery (orchestration), Monitoring (health checks)


**Критично для:** Platform deployment и operational automation



### Testing & Validation


**Назначение:** Обеспечивает тестирование, валидацию, учения, аудит и CAPA процессы.


**Сервисы:**

- ✅ **Validation Service - Exercises, Audits, Reviews & CAPA** (`validation-service`, port: 8022, status: production)

- 🟢 **Testing Infrastructure** (`tests`, port: N/A, status: active)

- ✅ **DevOps Agent - Infrastructure & Platform Compliance** (`devops-agent`, port: 8058, status: production)


**Ключевые возможности:**

- BC plan exercises

- Tabletop exercises

- Full-scale tests

- Audit management

- CAPA (Corrective/Preventive Actions)

- Unit/integration testing

- Security testing

- Compliance validation


**Зависимости:** PostgreSQL (test results), Workflow Engine (exercise workflows), Monitoring (validation metrics)


**Критично для:** Quality assurance и ISO 22301 exercise requirements



### User Interface Layer


**Назначение:** Предоставляет веб-интерфейсы для администрирования, управления и взаимодействия с платформой.


**Сервисы:**

- ⚪ **Admin Panel - System Administration** (`admin-panel`, port: N/A, status: reserved)

- ⚪ **Platform UI - End-User Interface** (`platform-ui`, port: N/A, status: reserved)

- ⚪ **MCP Interface - Model Context Protocol** (`mcp-interface`, port: N/A, status: reserved)


**Ключевые возможности:**

- Admin control center

- Platform management UI

- MCP (Model Context Protocol) interface

- Dashboard visualizations

- User management

- Configuration UI

- Real-time updates (WebSocket)

- Role-based UI


**Зависимости:** API Gateway (backend access), Auth Service (authentication), WebSocket (real-time)


**Критично для:** User interaction и platform administration



---


## 4. Service Categories (Technical Organization)


### 💾 Database Infrastructure


Core data storage and management layer


**Services in this category:** 4


- ✅ **BCM Platform Database (PostgreSQL via Supabase)** (port: 5432)

- ✅ **Platform Redis Cache** (port: 6379)

- ✅ **BCM Vector Search (Qdrant Cloud)** (port: 443)

- ✅ **Unified Database Access Layer** (port: None)

### ⚡ Runtime Services


Platform runtime infrastructure


**Services in this category:** 3


- ✅ **Service Discovery v2.0 - Unified Catalog + Registry** (port: 8500)

- ✅ **Real-time WebSocket Service** (port: 8050)

- 📋 **Platform Message Queue (RabbitMQ)** (port: 5672)

### 🚪 Gateway Layer


API gateway and routing


**Services in this category:** 1


- ✅ **AI-Powered API Gateway** (port: 8000)

### 📊 Observability


Monitoring, metrics, and visualization


**Services in this category:** 2


- ✅ **Prometheus Metrics Server** (port: 9090)

- ✅ **Grafana Dashboards** (port: 3000)

### 📡 EventBus Core


Event-driven messaging infrastructure


**Services in this category:** 1


- ✅ **Platform EventBus (Clean Architecture)** (port: None)

### 🔒 Security


Authentication, authorization, secrets


**Services in this category:** 2


- ✅ **Authentication & Authorization Service** (port: 8001)

- 🟡 **HashiCorp Vault - Secrets Manager** (port: 8200)

### 🤖 AI Office


AI agents and intelligent automation


**Services in this category:** 6


- ✅ **MIO Manager - Platform Observatory & Coordinator** (port: 8046)

- ✅ **DB Intelligence - Database Performance Specialist** (port: 8051)

- ✅ **Analytics Specialist - Platform Intelligence** (port: 8056)

- ✅ **DevOps Agent - Infrastructure & Platform Compliance** (port: 8058)

- ✅ **Project & Code Quality Agent** (port: 8060)

- ✅ **Agent Router - Request Routing & Load Balancing** (port: 8057)

### 📚 Shared Libraries


Common utilities and testing


**Services in this category:** 2


- 🟢 **Shared Libraries & Utilities** (port: N/A)

- 🟢 **Testing Infrastructure** (port: N/A)

### 📋 Platform Services


BCM business logic services


**Services in this category:** 10


- ✅ **Planning Service - BC Strategy Development** (port: 8011)

- ✅ **BIA Service - Business Impact Analysis** (port: 8012)

- ✅ **Learning Service - Training & Competence Management** (port: 8021)

- ✅ **Validation Service - Exercises, Audits, Reviews & CAPA** (port: 8022)

- 🟢 **Plans Service** (port: 8023)

- 🟢 **Documents Service** (port: 8024)

- 🟢 **Governance Service** (port: 8025)

- 🟢 **Compliance Service** (port: 8014)

- 🟢 **Risk Service** (port: 8026)

- 🟢 **Response Service** (port: 8027)

### 🧠 Intelligent Core


AI-powered cognitive capabilities


**Services in this category:** 12


- ✅ **Workflow Intelligence Engine - Cognitive Backbone** (port: 8037)

- ✅ **AI Foundation - Core AI Infrastructure** (port: 8040)

- ✅ **Expertise Center - Domain Specialists & AI Assistants** (port: None)

- ✅ **Community Intelligence - Peer Knowledge Sharing** (port: 8030)

- 🟢 **Unified Workflow Engine** (port: 8030)

- 🟢 **AI Orchestrator - The Brain** (port: 8002)

- 🟢 **Event Intelligence & Self-Healing** (port: 8032)

- 🟢 **Predictive Journey Service** (port: 8031)

- 📋 **Multi-Agent Coordination Center** (port: 8033)

- 🟢 **Collective Intelligence Agent Networks** (port: 8034)

- 🟢 **AI Workflow Optimizer** (port: 8038)

- ✅ **System BCM Service - Platform Self-Application of Business Continuity** (port: 8050)

### 🖥️ Interface Layer


User interfaces and admin panels


**Services in this category:** 3


- ⚪ **MCP Interface - Model Context Protocol** (port: N/A)

- ⚪ **Admin Panel - System Administration** (port: N/A)

- ⚪ **Platform UI - End-User Interface** (port: N/A)


---


## 5. Integration Map


### Key Integration Patterns


#### Database Access


All services use `database-managers` library for unified database access


```

All 46 services → database-managers → PostgreSQL/Redis/Qdrant

```


#### Event-Driven Communication


Services communicate via EventBus for loose coupling


```

25+ services pub/sub → EventBus → Redis/RabbitMQ

```


#### API Gateway Pattern


All external requests route through API Gateway


```

External clients → API Gateway → Service Discovery → Backend services

```


#### Service Discovery


Services register and discover each other dynamically


```

All services → Service Discovery (Redis registry) → Health checks

```


#### Monitoring & Metrics


All services expose /metrics endpoints for Prometheus


```

All services /metrics → Prometheus → Grafana dashboards

```


#### AI Orchestration


AI tasks route through orchestration layer


```

Requests → Agent Router → AI Orchestration → Specialized AI agents

```


#### Workflow Execution


Business processes execute via workflow engine


```

BCM services → Workflow Intelligence → Temporal → Task execution

```


#### Real-time Updates


Live updates via WebSocket connections


```

UI clients ↔ WebSocket Service ↔ EventBus → Backend services

```


---


## 6. Deployment Status


### Status Distribution


| Status | Count | Percentage | Description |

|--------|-------|------------|-------------|

| ✅ Production | 23 | 50.0% | Fully deployed and operational |

| ✅ Running | 3 | 6.5% | Currently running and active |

| 🟢 Active | 14 | 30.4% | Active and in use |

| 🟡 Configured | 1 | 2.2% | Configured but not fully deployed |

| 📋 Planned | 2 | 4.3% | Planned for future implementation |

| ⚪ Reserved | 3 | 6.5% | Reserved for future use |

| **Total** | **46** | **100%** | All services |


### Port Allocation


Services are deployed across multiple ports:


| Port | Service(s) |

|------|-----------|

| 443 | BCM Vector Search (Qdrant Cloud) |

| 3000 | Grafana Dashboards |

| 5432 | BCM Platform Database (PostgreSQL via Supabase) |

| 5672 | Platform Message Queue (RabbitMQ) |

| 6379 | Platform Redis Cache |

| 8000 | AI-Powered API Gateway |

| 8001 | Authentication & Authorization Service |

| 8002 | AI Orchestrator - The Brain |

| 8011 | Planning Service - BC Strategy Development |

| 8012 | BIA Service - Business Impact Analysis |

| 8014 | Compliance Service |

| 8021 | Learning Service - Training & Competence Management |

| 8022 | Validation Service - Exercises, Audits, Reviews & CAPA |

| 8023 | Plans Service |

| 8024 | Documents Service |

| 8025 | Governance Service |

| 8026 | Risk Service |

| 8027 | Response Service |

| 8030 | Community Intelligence - Peer Knowledge Sharing, Unified Workflow Engine |

| 8031 | Predictive Journey Service |

| 8032 | Event Intelligence & Self-Healing |

| 8033 | Multi-Agent Coordination Center |

| 8034 | Collective Intelligence Agent Networks |

| 8037 | Workflow Intelligence Engine - Cognitive Backbone |

| 8038 | AI Workflow Optimizer |

| 8040 | AI Foundation - Core AI Infrastructure |

| 8046 | MIO Manager - Platform Observatory & Coordinator |

| 8050 | Real-time WebSocket Service, System BCM Service - Platform Self-Application of Business Continuity |

| 8051 | DB Intelligence - Database Performance Specialist |

| 8056 | Analytics Specialist - Platform Intelligence |

| 8057 | Agent Router - Request Routing & Load Balancing |

| 8058 | DevOps Agent - Infrastructure & Platform Compliance |

| 8060 | Project & Code Quality Agent |

| 8200 | HashiCorp Vault - Secrets Manager |

| 8500 | Service Discovery v2.0 - Unified Catalog + Registry |

| 9090 | Prometheus Metrics Server |


### Critical Services Status


These services are critical for platform operation:


- ✅ **Database Infrastructure** (`postgresql`, port: 5432) - Status: production

- ✅ **Cache & Sessions** (`redis`, port: 6379) - Status: running

- ✅ **Event Communication** (`eventbus`, port: None) - Status: production

- ✅ **Service Registry** (`service-discovery`, port: 8500) - Status: running

- ✅ **API Entry Point** (`api-gateway`, port: 8000) - Status: production

- ✅ **Authentication** (`auth-service`, port: 8001) - Status: production

- ✅ **Platform Coordination** (`mio-manager`, port: 8046) - Status: production

- ✅ **Process Orchestration** (`workflow-intelligence`, port: 8037) - Status: production

- 🟢 **AI Coordination** (`ai-orchestration`, port: 8002) - Status: active


---


## Summary


### Platform Statistics


- **Total Services:** 46

- **Operational Services:** 40

- **Functional Systems:** 19

- **Technical Categories:** 11

- **Database Schemas:** 29

- **Grafana Dashboards:** 18

- **Prometheus Alert Rules:** 45


### Key Achievements


✅ Complete BCM lifecycle implementation (ISO 22301 compliant)

✅ AI-powered orchestration with multi-agent coordination

✅ Self-healing and resilience mechanisms

✅ Comprehensive monitoring (18 Grafana dashboards, 45 alerts)

✅ Event-driven architecture for loose coupling

✅ Unified API gateway with intelligent routing

✅ Multi-tenancy with Row-Level Security (RLS)

✅ RAG-powered knowledge management

✅ Predictive intelligence and ML capabilities

✅ Community intelligence for peer learning


### Architecture Principles


- **Microservices Architecture**: Loosely coupled services with clear boundaries

- **Event-Driven Design**: Asynchronous communication via EventBus

- **API-First**: RESTful APIs with OpenAPI documentation

- **Database per Service Pattern**: Each service manages its own schema

- **Infrastructure as Code**: Docker-based deployment

- **Observability**: Comprehensive monitoring and tracing

- **Security by Design**: Authentication, authorization, secrets management

- **AI-Powered**: Intelligent automation and decision support

- **Cloud-Native**: Designed for cloud deployment (Supabase, Qdrant Cloud)

- **ISO 22301 Compliant**: Full BCM standard implementation


---


## Next Steps


1. **Complete Planned Services**: Implement `message-queue` (RabbitMQ) and `coordination-center`

2. **Security Hardening**: Add TLS/WSS for WebSocket, implement distributed tracing

3. **Horizontal Scaling**: Configure load balancing and service replication

4. **Data Retention**: Implement archiving strategy and data retention policies

5. **Integration Tests**: Comprehensive end-to-end testing across all systems

6. **Documentation**: API documentation, user guides, and runbooks

7. **Performance Optimization**: Database query optimization, caching strategies

8. **Disaster Recovery**: Backup/restore procedures, failover testing

9. **UI Completion**: Finalize admin-panel and platform-ui interfaces

10. **Community Features**: Enable peer knowledge sharing and benchmarking


---


*This document provides a comprehensive view of all functional systems in the AI Platform ISO 22301.*

*For technical details, refer to individual service documentation.*