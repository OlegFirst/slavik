---
layout: page
title: "Platform Architecture"
permalink: /architecture/
---
<link rel="stylesheet" href="/ISO-22301/assets/css/unified-styles.min.css">

<div class="architecture-container">
  <div class="hero-section">
    <h1>Enterprise Architecture</h1>
    <p>Comprehensive enterprise-grade Business Continuity Management platform built on Odoo Community CRM with 32 integrated microservices for scalable, intelligent BCM operations</p>
  </div>

  <h2 class="section-title">Platform Architecture Overview</h2>

  <p>The platform follows a layered architecture pattern built on <strong>Odoo 18.0 Community Edition</strong> as the core business logic foundation, extended with specialized BCM modules and supported by a distributed microservices ecosystem.</p>

  <div class="architecture-diagram">
    <h3 style="color: #2563eb; margin-bottom: 1rem;">System Architecture Diagram</h3>
    <pre style="font-family: 'Courier New', monospace; font-size: 0.85rem; line-height: 1.4; text-align: left; color: #334155;">
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              PRESENTATION LAYER                                      │
├─────────────────────┬─────────────────────┬─────────────────────┬───────────────────┤
│   Admin Dashboard   │    Expert Portal    │  Manager Interface  │   Mobile Apps     │
│     (React)         │     (Next.js)       │      (Vue.js)       │  (React Native)   │
└─────────────────────┴─────────────────────┴─────────────────────┴───────────────────┘
                                        │
                              ┌─────────▼─────────┐
                              │    API Gateway    │
                              │   (Port: 8080)    │
                              └─────────┬─────────┘
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            BUSINESS LOGIC LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                          Odoo 18.0 Community Core                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │  bcm_core   │ │  bcm_risk   │ │   bcm_bia   │ │  bcm_plans  │ │bcm_incident │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │bcm_exercise │ │ bcm_audit   │ │bcm_training │ │bcm_comm...  │ │   [+19 more]│   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                              ┌─────────▼─────────┐
                              │    Event Bus      │
                              │   (RabbitMQ)      │
                              └─────────┬─────────┘
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           MICROSERVICES LAYER                                        │
├─────────────────────┬─────────────────────┬─────────────────────┬───────────────────┤
│    Core Services    │   AI Services       │  Infrastructure     │  Integration      │
│  ┌───────────────┐  │  ┌───────────────┐  │  ┌───────────────┐  │  ┌─────────────┐ │
│  │ BIA Engine    │  │  │ AI Orchestr.  │  │  │ Auth Service  │  │  │ Doc Proc.   │ │
│  │ (Port: 8082)  │  │  │ (Port: 8000)  │  │  │ (Port: 8005)  │  │  │(Port: 8083) │ │
│  └───────────────┘  │  └───────────────┘  │  └───────────────┘  │  └─────────────┘ │
│  ┌───────────────┐  │  ┌───────────────┐  │  ┌───────────────┐  │  ┌─────────────┐ │
│  │ Risk Assess.  │  │  │ Predictive    │  │  │ Notification  │  │  │ Compliance  │ │
│  │ (Port: 8081)  │  │  │ (Port: 8087)  │  │  │ (Port: 8004)  │  │  │(Port: 8084) │ │
│  └───────────────┘  │  └───────────────┘  │  └───────────────┘  │  └─────────────┘ │
│     [+6 more]       │     [+4 more]       │     [+6 more]       │   [+8 more]     │
└─────────────────────┴─────────────────────┴─────────────────────┴───────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                               DATA LAYER                                             │
├─────────────────────┬─────────────────────┬─────────────────────┬───────────────────┤
│   PostgreSQL 15     │    Redis Cache      │   MinIO Storage     │   Vector DB       │
│  (Transactional)    │   (Session/Cache)   │  (Documents/Files)  │ (AI Embeddings)   │
└─────────────────────┴─────────────────────┴─────────────────────┴───────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          INFRASTRUCTURE LAYER                                        │
├─────────────────────┬─────────────────────┬─────────────────────┬───────────────────┤
│      Docker         │     Kubernetes      │     Monitoring      │    Security       │
│   (Containers)      │   (Orchestration)   │   (Observability)   │   (Zero Trust)    │
└─────────────────────┴─────────────────────┴─────────────────────┴───────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           INTEGRATION LAYER                                          │
├─────────────────────┬─────────────────────┬─────────────────────┬───────────────────┤
│       SAP           │    Microsoft 365    │    Salesforce       │   ServiceNow      │
│  (ERP Systems)      │   (Collaboration)   │     (CRM)           │    (ITSM)         │
└─────────────────────┴─────────────────────┴─────────────────────┴───────────────────┘
    </pre>
  </div>

  <h3 class="subsection-title">Architecture Principles</h3>

  <ul style="margin: 1.5rem 0; line-height: 1.8;">
    <li><strong>Layered Architecture</strong>: Clear separation of concerns with defined interfaces between layers</li>
    <li><strong>Microservices Pattern</strong>: Domain-driven design with bounded contexts and autonomous services</li>
    <li><strong>Event-Driven Communication</strong>: Asynchronous messaging via RabbitMQ with event sourcing</li>
    <li><strong>API-First Design</strong>: RESTful APIs with OpenAPI specifications and GraphQL for flexible queries</li>
    <li><strong>Cloud-Native Infrastructure</strong>: Containerized deployment with Kubernetes orchestration</li>
    <li><strong>Security by Design</strong>: Zero-trust architecture with end-to-end encryption and OAuth 2.0/OIDC</li>
  </ul>

  <div class="metrics-grid">
    <div class="metric-card">
      <div class="metric-value">32</div>
      <div class="metric-label">Microservices</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">28</div>
      <div class="metric-label">BCM Modules</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">6</div>
      <div class="metric-label">Architecture Layers</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">15+</div>
      <div class="metric-label">External Integrations</div>
    </div>
  </div>

  <h2 class="section-title">Business Logic Layer - BCM Modules</h2>

  <p>28 purpose-built Odoo modules designed specifically for business continuity management in accordance with ISO 22301:2019 standard. Each module follows the Odoo MVC pattern with integrated security, workflow engine, and API endpoints.</p>

  <h3 class="subsection-title">Module Architecture Details</h3>

  <ul style="margin: 1.5rem 0; line-height: 1.8;">
    <li><strong>Module Structure</strong>: Python-based Odoo modules following MVC pattern with models, views, controllers, and security definitions</li>
    <li><strong>Database Design</strong>: Multi-tenant PostgreSQL schemas with row-level security, optimized indexes, and partitioning for time-series data</li>
    <li><strong>Inter-Module Communication</strong>: Service bus pattern using Odoo's internal messaging system and RabbitMQ for external events</li>
    <li><strong>Workflow Engine</strong>: State machine implementation with automated transitions, approval chains, and rollback capabilities</li>
    <li><strong>API Layer</strong>: XML-RPC and JSON-RPC endpoints for external integration, REST API wrapper for modern applications</li>
  </ul>

  <div class="modules-grid">
    <div class="module-card">
      <div class="module-header">
        <span class="module-name">bcm_core</span>
        <span class="module-status">PRODUCTION</span>
      </div>
      <p class="module-description">Core BCM system providing fundamental functionality and integration of all components</p>
      <ul class="module-features">
        <li>BCM organizational structure management</li>
        <li>Role-based access control model</li>
        <li>Centralized configuration management</li>
        <li>Module integration API</li>
      </ul>
    </div>

    <div class="module-card">
      <div class="module-header">
        <span class="module-name">bcm_risk</span>
        <span class="module-status">PRODUCTION</span>
      </div>
      <p class="module-description">Comprehensive risk assessment and management with AI-powered predictive analytics</p>
      <ul class="module-features">
        <li>Organizational risk catalog</li>
        <li>Probability and impact matrix</li>
        <li>AI-powered risk trend analysis</li>
        <li>Automated change notifications</li>
      </ul>
    </div>

    <div class="module-card">
      <div class="module-header">
        <span class="module-name">bcm_bia</span>
        <span class="module-status">PRODUCTION</span>
      </div>
      <p class="module-description">Business Impact Analysis with critical process identification and dependency mapping</p>
      <ul class="module-features">
        <li>Critical process identification</li>
        <li>RTO/RPO/MTPD calculations</li>
        <li>Dependencies and relationships</li>
        <li>Resource requirements analysis</li>
      </ul>
    </div>

    <div class="module-card">
      <div class="module-header">
        <span class="module-name">bcm_plans</span>
        <span class="module-status">PRODUCTION</span>
      </div>
      <p class="module-description">Creation and management of business continuity plans with automated validation</p>
      <ul class="module-features">
        <li>Recovery plan templates</li>
        <li>Version control and change management</li>
        <li>Automated plan validation</li>
        <li>Procedure integration</li>
      </ul>
    </div>

    <div class="module-card">
      <div class="module-header">
        <span class="module-name">bcm_incident</span>
        <span class="module-status">PRODUCTION</span>
      </div>
      <p class="module-description">Real-time incident and crisis management with automated escalation</p>
      <ul class="module-features">
        <li>Automated escalation workflows</li>
        <li>Command center interface</li>
        <li>Action and decision tracking</li>
        <li>Alert system integration</li>
      </ul>
    </div>

    <div class="module-card">
      <div class="module-header">
        <span class="module-name">bcm_exercise</span>
        <span class="module-status">PRODUCTION</span>
      </div>
      <p class="module-description">Exercise planning and execution with AI-powered scenario simulation</p>
      <ul class="module-features">
        <li>Exercise scenario library</li>
        <li>AI-generated incident scenarios</li>
        <li>Effectiveness assessment</li>
        <li>Reports and recommendations</li>
      </ul>
    </div>

    <div class="module-card">
      <div class="module-header">
        <span class="module-name">bcm_audit</span>
        <span class="module-status">PRODUCTION</span>
      </div>
      <p class="module-description">ISO 22301 compliance audit and continuous improvement framework</p>
      <ul class="module-features">
        <li>ISO 22301:2019 checklists</li>
        <li>Automated compliance checking</li>
        <li>Corrective action plans</li>
        <li>BCM maturity metrics</li>
      </ul>
    </div>

    <div class="module-card">
      <div class="module-header">
        <span class="module-name">bcm_training</span>
        <span class="module-status">BETA</span>
      </div>
      <p class="module-description">Staff training and awareness programs with interactive learning</p>
      <ul class="module-features">
        <li>BCM and crisis management courses</li>
        <li>Interactive simulations</li>
        <li>Knowledge testing</li>
        <li>Professional certification</li>
      </ul>
    </div>

    <div class="module-card">
      <div class="module-header">
        <span class="module-name">bcm_communication</span>
        <span class="module-status">PRODUCTION</span>
      </div>
      <p class="module-description">Crisis communications and stakeholder management with multi-channel delivery</p>
      <ul class="module-features">
        <li>Communication matrix</li>
        <li>Message templates</li>
        <li>Multi-channel broadcasting</li>
        <li>Delivery tracking</li>
      </ul>
    </div>
  </div>

  <h2 class="section-title">Microservices Layer</h2>

  <p>32 specialized microservices providing scalability, fault tolerance, and platform flexibility. Services are containerized with Docker and orchestrated by Kubernetes for autonomous scaling and self-healing capabilities.</p>

  <div class="architecture-diagram">
    <h3 style="color: #2563eb; margin-bottom: 1rem;">Service Communication Diagram</h3>
    <pre style="font-family: 'Courier New', monospace; font-size: 0.85rem; line-height: 1.4; text-align: left; color: #334155;">
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          MICROSERVICES COMMUNICATION                             │
└─────────────────────────────────────────────────────────────────────────────────┘

    API Gateway (8080)
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
Core Services   AI Services
    │               │
    ├─BIA Engine────┼─AI Orchestrator
    ├─Risk Assess.──┼─Predictive Analytics
    ├─Incident Mgmt─┼─Decision Support
    └─Recovery Orch─┼─Knowledge Graph
                    └─Scenario Generator
           │               │
           ▼               ▼
    ┌─────────────────────────────┐
    │       Event Bus             │
    │     (RabbitMQ)              │
    └─────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
Infrastructure  Integration  Data Layer
 Services        Services     Services
        │          │             │
   ┌────┴────┐ ┌───┴───┐    ┌────┴────┐
   │Auth     │ │Doc    │    │PostgreSQL│
   │Service  │ │Proc.  │    │Redis    │
   │         │ │       │    │MinIO    │
   └─────────┘ └───────┘    └─────────┘
    </pre>
  </div>

  <h3 class="subsection-title">Technical Implementation Details</h3>

  <ul style="margin: 1.5rem 0; line-height: 1.8;">
    <li><strong>Service Framework</strong>: Python FastAPI for async operations, Node.js Express for real-time features, Go for high-performance services</li>
    <li><strong>Service Discovery</strong>: Consul for service registry, health checking, and configuration management</li>
    <li><strong>Load Balancing</strong>: NGINX Plus with dynamic upstream configuration and circuit breaker patterns</li>
    <li><strong>Message Queue</strong>: RabbitMQ clusters with federation, priority queues, and dead letter exchanges</li>
    <li><strong>Observability Stack</strong>: Prometheus metrics, Jaeger distributed tracing, ELK stack for centralized logging</li>
    <li><strong>Deployment Strategy</strong>: Blue-green deployments, canary releases, feature flags via LaunchDarkly</li>
  </ul>

  <h3 class="subsection-title">Core Business Services</h3>

  <div class="services-grid">
    <div class="service-card">
      <div class="service-name">BIA Engine Service</div>
      <div class="service-port">Port: 8082</div>
      <p class="service-description">Business Impact Analysis engine calculating process criticality, determining RTO/RPO values, analyzing component dependencies with graph algorithms.</p>
    </div>

    <div class="service-card">
      <div class="service-name">Risk Assessment Service</div>
      <div class="service-port">Port: 8081</div>
      <p class="service-description">Risk assessment service with ML models using XGBoost and neural networks. Predicts probabilities, evaluates impact, generates risk heat maps.</p>
    </div>

    <div class="service-card">
      <div class="service-name">Incident Management Service</div>
      <div class="service-port">Port: 8003</div>
      <p class="service-description">Real-time incident management with WebSocket connections. Automated classification using NLP, intelligent escalation, response coordination.</p>
    </div>

    <div class="service-card">
      <div class="service-name">Document Processor</div>
      <div class="service-port">Port: 8083</div>
      <p class="service-description">BCM document processing with OCR via Tesseract, NLP entity extraction, Git-based versioning, Elasticsearch full-text search.</p>
    </div>

    <div class="service-card">
      <div class="service-name">Compliance Service</div>
      <div class="service-port">Port: 8084</div>
      <p class="service-description">Standards compliance monitoring with automated checks via policy-as-code, report generation using Jasper Reports, requirements traceability matrix.</p>
    </div>

    <div class="service-card">
      <div class="service-name">Recovery Orchestrator</div>
      <div class="service-port">Port: 8086</div>
      <p class="service-description">Recovery process orchestration using Apache Airflow DAGs. Automated runbooks, team coordination via WebRTC, real-time progress monitoring.</p>
    </div>
  </div>

  <h3 class="subsection-title">AI and Analytics Services</h3>

  <div class="services-grid">
    <div class="service-card">
      <div class="service-name">AI Orchestrator</div>
      <div class="service-port">Port: 8000</div>
      <p class="service-description">Central AI operations coordinator. Manages ML models, distributes computational tasks, optimizes resource utilization across AI services.</p>
    </div>

    <div class="service-card">
      <div class="service-name">Scenario Generator</div>
      <div class="service-port">Port: 8085</div>
      <p class="service-description">Crisis scenario generation and simulation engine. Creates realistic crisis scenarios for training and testing using ML algorithms.</p>
    </div>

    <div class="service-card">
      <div class="service-name">Predictive Analytics</div>
      <div class="service-port">Port: 8087</div>
      <p class="service-description">Predictive analytics engine. Forecasts incidents 72-96 hours ahead, analyzes trends, provides early warning systems.</p>
    </div>

    <div class="service-card">
      <div class="service-name">Decision Support Engine</div>
      <div class="service-port">Port: 8088</div>
      <p class="service-description">Data-driven decision support system. Provides recommendations, evaluates alternatives, analyzes potential consequences.</p>
    </div>

    <div class="service-card">
      <div class="service-name">Knowledge Graph Service</div>
      <div class="service-port">Port: 8089</div>
      <p class="service-description">Organizational knowledge graph. Maps relationships between assets, processes, risks with automatic data enrichment.</p>
    </div>

    <div class="service-card">
      <div class="service-name">Pattern Recognition</div>
      <div class="service-port">Port: 8092</div>
      <p class="service-description">Pattern recognition and anomaly detection. Identifies unusual patterns in system behavior and potential security threats.</p>
    </div>
  </div>

  <h3 class="subsection-title">Infrastructure Services</h3>

  <div class="services-grid">
    <div class="service-card">
      <div class="service-name">Event Bus Service</div>
      <div class="service-port">RabbitMQ: 5672</div>
      <p class="service-description">Asynchronous service communication. Pub/Sub patterns, guaranteed delivery, horizontal scalability with message persistence.</p>
    </div>

    <div class="service-card">
      <div class="service-name">Authentication Service</div>
      <div class="service-port">Keycloak: 8005</div>
      <p class="service-description">Centralized authentication and authorization. SSO, LDAP/AD integration, MFA, session management, OAuth 2.0/OIDC.</p>
    </div>

    <div class="service-card">
      <div class="service-name">Notification Service</div>
      <div class="service-port">Port: 8004</div>
      <p class="service-description">Multi-channel notification delivery. Email, SMS, Push notifications, Webhooks with priority queuing and templates.</p>
    </div>

    <div class="service-card">
      <div class="service-name">Monitoring Service</div>
      <div class="service-port">Port: 8090</div>
      <p class="service-description">Platform monitoring and observability. Performance metrics, distributed logging, tracing, alerting with Prometheus/Grafana.</p>
    </div>

    <div class="service-card">
      <div class="service-name">Backup Service</div>
      <div class="service-port">Port: 8091</div>
      <p class="service-description">Automated backup and recovery. Incremental backups, point-in-time recovery, cross-region replication.</p>
    </div>

    <div class="service-card">
      <div class="service-name">API Gateway</div>
      <div class="service-port">Port: 8080</div>
      <p class="service-description">Single API entry point. Request routing, rate limiting, caching, security policies, load balancing.</p>
    </div>
  </div>

  <h2 class="section-title">Data Layer</h2>

  <p>Multi-tier data architecture supporting structured and unstructured data with optimized storage, caching, and search capabilities</p>

  <div class="architecture-diagram">
    <h3 style="color: #2563eb; margin-bottom: 1rem;">Data Flow Architecture</h3>
    <pre style="font-family: 'Courier New', monospace; font-size: 0.85rem; line-height: 1.4; text-align: left; color: #334155;">
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER ARCHITECTURE                             │
└─────────────────────────────────────────────────────────────────────────────────┘

    Application Services
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
Write Path     Read Path
    │             │
    ▼             ▼
┌─────────────────────────────────────────┐  ┌─────────────────────────────────────┐
│           PRIMARY STORAGE               │  │            CACHE LAYER              │
├─────────────────────────────────────────┤  ├─────────────────────────────────────┤
│  PostgreSQL 15 (Primary Database)      │  │      Redis Cluster                  │
│  ├─ BCM Transactional Data             │  │  ├─ Session Storage                │
│  ├─ User Management                     │  │  ├─ Query Cache                    │
│  ├─ Workflow States                     │  │  ├─ Real-time Data                │
│  ├─ Audit Logs                         │  │  └─ Rate Limiting                 │
│  └─ Configuration                       │  └─────────────────────────────────────┘
└─────────────────────────────────────────┘             │
           │                                              │
           ▼                                              ▼
┌─────────────────────────────────────────┐  ┌─────────────────────────────────────┐
│          OBJECT STORAGE                 │  │          SEARCH ENGINE              │
├─────────────────────────────────────────┤  ├─────────────────────────────────────┤
│        MinIO Cluster                    │  │      Elasticsearch                  │
│  ├─ Document Files                      │  │  ├─ Full-text Search               │
│  ├─ Report Archives                     │  │  ├─ Log Analytics                  │
│  ├─ Backup Files                        │  │  ├─ Business Intelligence          │
│  ├─ Media Assets                        │  │  └─ Real-time Dashboards          │
│  └─ Export Data                         │  └─────────────────────────────────────┘
└─────────────────────────────────────────┘             │
           │                                              │
           ▼                                              ▼
┌─────────────────────────────────────────┐  ┌─────────────────────────────────────┐
│         VECTOR DATABASE                 │  │         MESSAGE QUEUE               │
├─────────────────────────────────────────┤  ├─────────────────────────────────────┤
│        Qdrant/Weaviate                  │  │       RabbitMQ Cluster              │
│  ├─ AI Model Embeddings                 │  │  ├─ Event Streaming                │
│  ├─ Semantic Search                     │  │  ├─ Task Queues                    │
│  ├─ Knowledge Graph                     │  │  ├─ Notification Delivery          │
│  └─ ML Feature Store                    │  │  └─ Dead Letter Queues            │
└─────────────────────────────────────────┘  └─────────────────────────────────────┘
    </pre>
  </div>

  <h3 class="subsection-title">Data Architecture Components</h3>

  <div class="services-grid">
    <div class="service-card">
      <div class="service-name">PostgreSQL Primary</div>
      <div class="service-port">Port: 5432</div>
      <p class="service-description">Primary transactional database with ACID compliance, multi-tenant schemas, row-level security, and automated backups.</p>
    </div>

    <div class="service-card">
      <div class="service-name">Redis Cache Cluster</div>
      <div class="service-port">Port: 6379</div>
      <p class="service-description">High-performance in-memory cache for sessions, query results, and real-time data with Redis Cluster for high availability.</p>
    </div>

    <div class="service-card">
      <div class="service-name">MinIO Object Storage</div>
      <div class="service-port">Port: 9000</div>
      <p class="service-description">S3-compatible object storage for documents, reports, backups, and media with versioning and lifecycle policies.</p>
    </div>

    <div class="service-card">
      <div class="service-name">Elasticsearch Engine</div>
      <div class="service-port">Port: 9200</div>
      <p class="service-description">Full-text search and analytics engine for document search, log analysis, and business intelligence dashboards.</p>
    </div>

    <div class="service-card">
      <div class="service-name">Vector Database</div>
      <div class="service-port">Port: 6333</div>
      <p class="service-description">Vector database for AI embeddings, semantic search, knowledge graphs, and machine learning feature storage.</p>
    </div>

    <div class="service-card">
      <div class="service-name">Event Streaming</div>
      <div class="service-port">Port: 5672</div>
      <p class="service-description">Message broker for event-driven architecture with guaranteed delivery, routing, and dead letter handling.</p>
    </div>
  </div>

  <h2 class="section-title">Infrastructure Layer</h2>

  <p>Cloud-native infrastructure built on container orchestration with comprehensive monitoring, security, and deployment automation</p>

  <div class="layer-section">
    <h3 class="layer-title">Container Orchestration</h3>
    <p>Kubernetes-based platform with automated scaling, rolling deployments, and self-healing capabilities</p>
    <div class="tech-stack-grid">
      <div class="tech-item">Kubernetes 1.28+</div>
      <div class="tech-item">Docker Containers</div>
      <div class="tech-item">Helm Charts</div>
      <div class="tech-item">Istio Service Mesh</div>
    </div>
  </div>

  <div class="layer-section">
    <h3 class="layer-title">Monitoring & Observability</h3>
    <p>Comprehensive monitoring stack with metrics, logging, tracing, and alerting</p>
    <div class="tech-stack-grid">
      <div class="tech-item">Prometheus Metrics</div>
      <div class="tech-item">Grafana Dashboards</div>
      <div class="tech-item">Jaeger Tracing</div>
      <div class="tech-item">ELK Stack Logging</div>
    </div>
  </div>

  <div class="layer-section">
    <h3 class="layer-title">Security & Compliance</h3>
    <p>Zero-trust security model with end-to-end encryption and compliance automation</p>
    <div class="tech-stack-grid">
      <div class="tech-item">HashiCorp Vault</div>
      <div class="tech-item">Keycloak SSO</div>
      <div class="tech-item">Open Policy Agent</div>
      <div class="tech-item">Falco Runtime Security</div>
    </div>
  </div>

  <div class="layer-section">
    <h3 class="layer-title">CI/CD & DevOps</h3>
    <p>Automated deployment pipeline with infrastructure as code and GitOps practices</p>
    <div class="tech-stack-grid">
      <div class="tech-item">GitLab CI/CD</div>
      <div class="tech-item">ArgoCD GitOps</div>
      <div class="tech-item">Terraform IaC</div>
      <div class="tech-item">SonarQube Quality</div>
    </div>
  </div>

  <h2 class="section-title">Presentation Layer</h2>

  <p>Multi-interface architecture providing specialized user experiences for different stakeholder groups</p>

  <div class="layer-section">
    <h3 class="layer-title">User Interfaces</h3>
    <p>Role-based interfaces optimized for different user workflows and responsibilities</p>
    <div class="tech-stack-grid">
      <div class="tech-item">Admin Dashboard (React)</div>
      <div class="tech-item">Expert Portal (Next.js)</div>
      <div class="tech-item">Manager Interface (Vue.js)</div>
      <div class="tech-item">Mobile Apps (React Native)</div>
    </div>
  </div>

  <h2 class="section-title">Integration Layer</h2>

  <p>Comprehensive integration ecosystem connecting with enterprise systems, security tools, and external services through standardized APIs and connectors</p>

  <div class="architecture-diagram">
    <h3 style="color: #2563eb; margin-bottom: 1rem;">Integration Architecture</h3>
    <pre style="font-family: 'Courier New', monospace; font-size: 0.85rem; line-height: 1.4; text-align: left; color: #334155;">
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            INTEGRATION ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────────────────┘

                          BCM Platform Core
                               │
                    ┌──────────┼──────────┐
                    │          │          │
                    ▼          ▼          ▼
           ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
           │ API Gateway │ │Event Bridge │ │Message Queue│
           │             │ │             │ │             │
           └─────────────┘ └─────────────┘ └─────────────┘
                    │          │          │
         ┌──────────┼──────────┼──────────┼──────────┐
         │          │          │          │          │
         ▼          ▼          ▼          ▼          ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Enterprise  │ │ Security &  │ │Cloud Service│ │  Standards  │ │   Telco &   │
│  Systems    │ │ Monitoring  │ │ Providers   │ │ & Compliance│ │Communication│
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
       │               │               │               │               │
   ┌───┴───┐       ┌───┴───┐       ┌───┴───┐       ┌───┴───┐       ┌───┴───┐
   │ SAP   │       │Grafana│       │  AWS  │       │ISO    │       │Twilio │
   │MS 365 │       │Elastic│       │Azure  │       │NIST   │       │Teams  │
   │SF/SN  │       │TheHive│       │ GCP   │       │COBIT  │       │Slack  │
   └───────┘       └───────┘       └───────┘       └───────┘       └───────┘
    </pre>
  </div>

  <div class="integration-section">
    <h3 class="subsection-title">Enterprise Systems Integration</h3>
    <div class="integration-grid">
      <div class="integration-item">
        <div class="integration-logo">SAP</div>
        <div class="integration-details">
          <h4>SAP ERP Integration</h4>
          <p>Master data synchronization, financial data</p>
        </div>
      </div>
      <div class="integration-item">
        <div class="integration-logo">MS</div>
        <div class="integration-details">
          <h4>Microsoft 365</h4>
          <p>Document management, Teams collaboration</p>
        </div>
      </div>
      <div class="integration-item">
        <div class="integration-logo">SF</div>
        <div class="integration-details">
          <h4>Salesforce CRM</h4>
          <p>Customer data, contact management</p>
        </div>
      </div>
      <div class="integration-item">
        <div class="integration-logo">SN</div>
        <div class="integration-details">
          <h4>ServiceNow ITSM</h4>
          <p>IT incident management, change control</p>
        </div>
      </div>
      <div class="integration-item">
        <div class="integration-logo">OR</div>
        <div class="integration-details">
          <h4>Oracle Database</h4>
          <p>Legacy system data extraction</p>
        </div>
      </div>
      <div class="integration-item">
        <div class="integration-logo">AD</div>
        <div class="integration-details">
          <h4>Active Directory</h4>
          <p>User authentication, LDAP integration</p>
        </div>
      </div>
    </div>

    <h3 class="subsection-title">Security & Monitoring Integration</h3>
    <div class="integration-grid">
      <div class="integration-item">
        <div class="integration-logo">TH</div>
        <div class="integration-details">
          <h4>TheHive Platform</h4>
          <p>Security incident response coordination</p>
        </div>
      </div>
      <div class="integration-item">
        <div class="integration-logo">GR</div>
        <div class="integration-details">
          <h4>Grafana Analytics</h4>
          <p>Performance metrics and dashboards</p>
        </div>
      </div>
      <div class="integration-item">
        <div class="integration-logo">EL</div>
        <div class="integration-details">
          <h4>Elastic Stack</h4>
          <p>Log analysis and business intelligence</p>
        </div>
      </div>
      <div class="integration-item">
        <div class="integration-logo">PR</div>
        <div class="integration-details">
          <h4>Prometheus</h4>
          <p>Infrastructure monitoring and alerting</p>
        </div>
      </div>
      <div class="integration-item">
        <div class="integration-logo">SP</div>
        <div class="integration-details">
          <h4>Splunk SIEM</h4>
          <p>Security information and event management</p>
        </div>
      </div>
      <div class="integration-item">
        <div class="integration-logo">VL</div>
        <div class="integration-details">
          <h4>Vault Secrets</h4>
          <p>Secrets management and encryption</p>
        </div>
      </div>
    </div>

    <h3 class="subsection-title">Communication & Notification Integration</h3>
    <div class="integration-grid">
      <div class="integration-item">
        <div class="integration-logo">TW</div>
        <div class="integration-details">
          <h4>Twilio Communications</h4>
          <p>SMS, voice calls, emergency notifications</p>
        </div>
      </div>
      <div class="integration-item">
        <div class="integration-logo">SL</div>
        <div class="integration-details">
          <h4>Slack Workspace</h4>
          <p>Team collaboration, automated updates</p>
        </div>
      </div>
      <div class="integration-item">
        <div class="integration-logo">EM</div>
        <div class="integration-details">
          <h4>Email Services</h4>
          <p>SMTP/Exchange integration</p>
        </div>
      </div>
      <div class="integration-item">
        <div class="integration-logo">WH</div>
        <div class="integration-details">
          <h4>Webhook APIs</h4>
          <p>Custom system notifications</p>
        </div>
      </div>
    </div>
  </div>

  <h2 class="section-title">Architecture Benefits & Technical Advantages</h2>

  <div class="modules-grid">
    <div class="module-card">
      <div class="module-name">Evolutionary Architecture</div>
      <p class="module-description">Built on proven Odoo CRM foundation, evolved with BCM specialization, enhanced with AI services, progressing toward autonomous ecosystem</p>
    </div>

    <div class="module-card">
      <div class="module-name">Hybrid Architecture Model</div>
      <p class="module-description">Combines monolithic Odoo core for stability with microservices for innovation, scalability, and independent deployment cycles</p>
    </div>

    <div class="module-card">
      <div class="module-name">Cloud-Native Design</div>
      <p class="module-description">Container-first architecture with Kubernetes orchestration, enabling auto-scaling, self-healing, and multi-cloud deployment</p>
    </div>

    <div class="module-card">
      <div class="module-name">API-First Integration</div>
      <p class="module-description">Comprehensive API ecosystem supporting REST, GraphQL, and gRPC protocols for seamless third-party integrations</p>
    </div>

    <div class="module-card">
      <div class="module-name">Event-Driven Architecture</div>
      <p class="module-description">Asynchronous event processing with RabbitMQ ensuring loose coupling, fault tolerance, and horizontal scalability</p>
    </div>

    <div class="module-card">
      <div class="module-name">Enterprise-Grade Security</div>
      <p class="module-description">Zero-trust security model with end-to-end encryption, multi-factor authentication, and comprehensive audit trails</p>
    </div>

    <div class="module-card">
      <div class="module-name">Multi-Tenant Architecture</div>
      <p class="module-description">Designed for SaaS deployment with tenant isolation, resource optimization, and configuration customization</p>
    </div>

    <div class="module-card">
      <div class="module-name">Observability & Monitoring</div>
      <p class="module-description">Comprehensive monitoring stack with Prometheus metrics, distributed tracing, and centralized logging for operational excellence</p>
    </div>
  </div>

<div style="background: #f8fafc; border-top: 2px solid #e2e8f0; padding: 3rem 2rem; margin: 4rem -2rem -2rem -2rem; text-align: center;">
  <div style="max-width: 1200px; margin: 0 auto;">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 2rem; margin-bottom: 2rem;">
      <a href="#" style="background: white; color: #2563eb; padding: 0.75rem 1.5rem; border-radius: 0.5rem; text-decoration: none; box-shadow: 0 2px 8px rgba(0,0,0,0.1); font-weight: 600;">Back to Top</a>

      <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
        <a href="/ISO-22301/" style="background: white; color: #2563eb; padding: 0.75rem 1.5rem; border-radius: 0.5rem; text-decoration: none; box-shadow: 0 2px 8px rgba(0,0,0,0.1); font-weight: 600;">Previous</a>
        <a href="/ISO-22301/scenarios" style="background: #2563eb; color: white; padding: 0.75rem 1.5rem; border-radius: 0.5rem; text-decoration: none; box-shadow: 0 2px 8px rgba(0,0,0,0.1); font-weight: 600;">Next</a>
      </div>
    </div>

    <div style="color: #64748b; font-size: 0.875rem; margin-top: 2rem;">
      <p>ISO 22301 BCM Platform © 2024 | <a href="https://github.com/SEH-foundation/ISO-22301" style="color: #2563eb;">GitHub</a> | <a href="/ISO-22301/" style="color: #2563eb;">Home</a></p>
    </div>
  </div>
</div>

</div>