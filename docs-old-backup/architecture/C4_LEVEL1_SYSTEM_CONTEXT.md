# C4 Model - Level 1: System Context

**AI-Platform-ISO - Business Continuity Management Platform**

---

## 📊 System Context Diagram

```mermaid
graph TB
    subgraph "External Users"
        BCM_MANAGER[BCM Manager]
        AUDITOR[Auditor]
        EXEC[Executive]
        ADMIN[Platform Admin]
    end

    subgraph "AI-Platform-ISO"
        PLATFORM[AI BCM Platform<br/>38 microservices<br/>Python/FastAPI]
    end

    subgraph "External Systems"
        TEMPORAL[Temporal Cloud<br/>Workflow Orchestration<br/>eu-west-3]
        SUPABASE[Supabase<br/>PostgreSQL Database<br/>eu-north-1]
        QDRANT[Qdrant Cloud<br/>Vector Database<br/>eu-west-1]
        REDIS[Upstash Redis<br/>Cache & EventBus<br/>us-east-1]

        SMTP[Email Provider<br/>SMTP]
        TWILIO[Twilio<br/>SMS Service]
        FIREBASE[Firebase<br/>Push Notifications]

        GITHUB[GitHub<br/>Repository Management]
        PARTISIA[Partisia Blockchain<br/>Smart Contracts]
    end

    BCM_MANAGER -->|Manages BCM| PLATFORM
    AUDITOR -->|Audits Compliance| PLATFORM
    EXEC -->|Views Dashboards| PLATFORM
    ADMIN -->|Administers System| PLATFORM

    PLATFORM -->|Orchestrates Workflows| TEMPORAL
    PLATFORM -->|Stores Data| SUPABASE
    PLATFORM -->|Semantic Search| QDRANT
    PLATFORM -->|Caching & Events| REDIS

    PLATFORM -->|Sends Email| SMTP
    PLATFORM -->|Sends SMS| TWILIO
    PLATFORM -->|Push Notifications| FIREBASE

    PLATFORM -->|Integration| GITHUB
    PLATFORM -->|Blockchain| PARTISIA

    style PLATFORM fill:#4A90E2,stroke:#2E5C8A,stroke-width:3px,color:#fff
    style TEMPORAL fill:#7B68EE,stroke:#4B0082,color:#fff
    style SUPABASE fill:#3ECF8E,stroke:#2E8B57,color:#fff
    style QDRANT fill:#FF6B6B,stroke:#DC143C,color:#fff
    style REDIS fill:#DC382D,stroke:#8B0000,color:#fff
```

---

## 📋 Components Overview

### Core Platform (38 Services)
- **4** AI Foundation services (brain)
- **5** AI Microservices (ML/intelligence)
- **12** Platform Services (business logic)
- **17** Infrastructure Services

### External Dependencies (9 Systems)
- **3** Managed cloud services (Temporal, Supabase, Qdrant)
- **3** Notification providers (Email, SMS, Push)
- **3** Integration platforms (Redis, GitHub, Partisia)

---

## 🔗 System Boundaries

| System | Type | Region | Purpose |
|--------|------|--------|---------|
| **AI-Platform-ISO** | Core | - | BCM management platform |
| **Temporal Cloud** | Orchestration | eu-west-3 | Workflow engine |
| **Supabase** | Database | eu-north-1 | PostgreSQL + Auth |
| **Qdrant Cloud** | Vector DB | eu-west-1 | Semantic search |
| **Upstash Redis** | Cache | us-east-1 | Event bus + cache |
| **Email/SMS/Push** | Notifications | - | Alert delivery |
| **GitHub** | Code Repository | - | Version control |
| **Partisia** | Blockchain | - | Audit trail |

---

## 👥 User Personas

### BCM Manager
- Creates BIA analyses
- Manages risk assessments
- Coordinates incident response
- Designs BC exercises

### Auditor
- Reviews compliance status
- Generates audit reports
- Validates BC plans
- Tracks non-conformities

### Executive
- Views KPI dashboards
- Monitors BCM maturity
- Reviews risk posture
- Approves BC strategies

### Platform Admin
- Manages users & tenants
- Configures workflows
- Monitors system health
- Reviews security logs

---

## 🔄 Key Interactions

### User → Platform
1. User authenticates (JWT)
2. Platform validates permissions
3. Request routed through API Gateway
4. Service processes request
5. Response returned to user

### Platform → External Systems
1. **Temporal Cloud:** Workflow orchestration (BIA, Incident, Exercise)
2. **Supabase:** Data persistence (9 schemas, 43 migrations)
3. **Qdrant:** Vector search (ISO knowledge, workflow cases)
4. **Redis:** Event publishing (workflow events, system events)
5. **Notifications:** Alerts (email/SMS/push for incidents)

---

## 📊 Traffic Flows

```mermaid
sequenceDiagram
    participant User
    participant Gateway as API Gateway
    participant Service as Platform Service
    participant WF as Workflow Intelligence
    participant DB as Supabase
    participant Temporal as Temporal Cloud

    User->>Gateway: HTTPS Request
    Gateway->>Gateway: Authenticate (JWT)
    Gateway->>Gateway: Rate Limit Check
    Gateway->>Service: Forward Request
    Service->>WF: Get AI Recommendation
    WF->>Temporal: Orchestrate Workflow
    Temporal-->>WF: Workflow Result
    WF->>DB: Store Result
    DB-->>WF: Confirmation
    WF-->>Service: AI Recommendation
    Service-->>Gateway: Response
    Gateway-->>User: HTTPS Response
```

---

## 🚀 Deployment View

```mermaid
graph LR
    subgraph "Production Environment"
        subgraph "Europe North 1"
            DB[(Supabase<br/>PostgreSQL)]
        end

        subgraph "Europe West 1"
            VDB[(Qdrant<br/>Vector DB)]
        end

        subgraph "Europe West 3"
            TC[Temporal<br/>Cloud]
        end

        subgraph "US East 1"
            REDIS[(Redis<br/>Cache)]
        end

        subgraph "Platform Services"
            AI[AI Foundation<br/>4 services]
            AIS[AI Services<br/>5 services]
            PS[Platform Services<br/>12 services]
            INFRA[Infrastructure<br/>17 services]
        end
    end

    AI --> DB
    AI --> VDB
    AI --> TC
    AI --> REDIS

    AIS --> DB
    AIS --> VDB

    PS --> AI
    PS --> AIS
    PS --> DB

    INFRA --> DB
    INFRA --> REDIS

    style DB fill:#3ECF8E,stroke:#2E8B57,color:#fff
    style VDB fill:#FF6B6B,stroke:#DC143C,color:#fff
    style TC fill:#7B68EE,stroke:#4B0082,color:#fff
    style REDIS fill:#DC382D,stroke:#8B0000,color:#fff
```

---

## 📈 Scale & Performance

| Metric | Current | Target |
|--------|---------|--------|
| **Services** | 38 | 50+ |
| **Databases** | 2 | 2 |
| **Users** | Development | 1000+ |
| **Requests/sec** | Low | 100+ |
| **Availability** | Development | 99.9% |

---

## 🔒 Security Boundaries

```mermaid
graph TB
    subgraph "Public Internet"
        USER[Users]
    end

    subgraph "Security Layer"
        WAF[WAF]
        AUTH[Auth Service]
    end

    subgraph "Application Layer"
        GATEWAY[API Gateway<br/>JWT + Rate Limit]
        SERVICES[Microservices<br/>RLS + Permissions]
    end

    subgraph "Data Layer"
        DB[(Database<br/>RLS Policies)]
        SECRETS[Secrets Manager]
    end

    USER --> WAF
    WAF --> AUTH
    AUTH --> GATEWAY
    GATEWAY --> SERVICES
    SERVICES --> DB
    SERVICES --> SECRETS

    style WAF fill:#FF6B6B,stroke:#DC143C,color:#fff
    style AUTH fill:#FFA500,stroke:#FF8C00,color:#fff
    style GATEWAY fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style DB fill:#3ECF8E,stroke:#2E8B57,color:#fff
```

---

## 📝 Notes

- This is **Level 1** - System Context (highest level)
- See **C4_LEVEL2_CONTAINERS.md** for microservices architecture
- All external systems are managed services (no ops required)
- Multi-region deployment for resilience

---

**Next:** [Level 2 - Containers (Microservices)](C4_LEVEL2_CONTAINERS.md)
