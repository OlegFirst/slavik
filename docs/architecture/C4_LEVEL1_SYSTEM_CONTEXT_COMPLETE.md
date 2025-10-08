# C4 Model - Level 1: System Context (Complete)
## AI-Platform-ISO - Системный контекст

**Auto-generated from real codebase**
**Last updated:** 2025-10-06

---

## Что это?

Level 1 показывает **ЧТО** система делает с точки зрения внешних пользователей и систем.

**"Птичий взгляд" на систему:**
- Кто использует систему?
- С какими внешними системами она интегрируется?
- Какие основные функции предоставляет?

---

## 1. Полная диаграмма системного контекста

```mermaid
graph TB
    subgraph "Организация"
        BCM[BCM Manager<br/>👤 Управляет планами<br/>непрерывности бизнеса]
        COMP[Compliance Officer<br/>👤 Отслеживает<br/>соответствие стандартам]
        ADMIN[System Admin<br/>👤 Управляет<br/>инфраструктурой]
        EXEC[Executive<br/>👤 Принимает<br/>стратегические решения]
        ANALYST[Risk Analyst<br/>👤 Оценивает<br/>риски]
    end

    subgraph "AI-Platform-ISO System"
        PLATFORM[AI-Platform-ISO<br/>🤖 AI-powered BCM Platform<br/>━━━━━━━━━━━━━━━━<br/>• Business Continuity Management<br/>• ISO 22301 Compliance<br/>• Risk Assessment & BIA<br/>• AI-driven Optimization<br/>• Living Documentation]
    end

    subgraph "External Systems & Services"
        TEMPORAL[Temporal Cloud<br/>🔄 Workflow Orchestration<br/>eu-west-3.gcp]
        SUPABASE[Supabase<br/>💾 PostgreSQL Database<br/>eu-north-1]
        QDRANT[Qdrant Cloud<br/>🔍 Vector Search<br/>eu-west-1]
        REDIS[Upstash Redis<br/>⚡ Cache & Streams<br/>us-east-1]
        GITHUB[GitHub<br/>📚 Code Repository<br/>& Integration]
        EMAIL[Email Service<br/>📧 SMTP<br/>Notifications]
        SMS[SMS Gateway<br/>📱 Twilio<br/>Alerts]
        ANTHROPIC[Anthropic Claude<br/>🧠 AI Assistants<br/>API]
    end

    %% Пользователи → Платформа
    BCM -->|Создает и управляет<br/>планами BCM| PLATFORM
    COMP -->|Проверяет соответствие<br/>ISO 22301| PLATFORM
    ADMIN -->|Настраивает систему<br/>и мониторит| PLATFORM
    EXEC -->|Просматривает дашборды<br/>и отчеты| PLATFORM
    ANALYST -->|Проводит анализ<br/>рисков и BIA| PLATFORM

    %% Платформа → Внешние системы
    PLATFORM -->|Orchestrates workflows<br/>via gRPC| TEMPORAL
    PLATFORM -->|Stores/queries data<br/>via REST API| SUPABASE
    PLATFORM -->|Semantic search<br/>via gRPC| QDRANT
    PLATFORM -->|Caching & events<br/>via Redis protocol| REDIS
    PLATFORM -->|Syncs code & issues<br/>via GitHub API| GITHUB
    PLATFORM -->|Sends notifications<br/>via SMTP| EMAIL
    PLATFORM -->|Sends alerts<br/>via REST API| SMS
    PLATFORM -->|AI assistance<br/>via REST API| ANTHROPIC

    style BCM fill:#e3f2fd
    style COMP fill:#e3f2fd
    style ADMIN fill:#e3f2fd
    style EXEC fill:#e3f2fd
    style ANALYST fill:#e3f2fd

    style PLATFORM fill:#f3e5f5,stroke:#9c27b0,stroke-width:4px

    style TEMPORAL fill:#fff3e0
    style SUPABASE fill:#e8f5e9
    style QDRANT fill:#fce4ec
    style REDIS fill:#ffebee
    style GITHUB fill:#e1f5fe
    style EMAIL fill:#f3e5f5
    style SMS fill:#fff9c4
    style ANTHROPIC fill:#f3e5f5
```

---

## 2. Роли пользователей

| Роль | Ответственность | Основные действия |
|------|----------------|-------------------|
| **BCM Manager** | Управление непрерывностью бизнеса | • Создание BCM планов<br/>• Управление инцидентами<br/>• Проведение учений<br/>• Активация планов реагирования |
| **Compliance Officer** | Соответствие стандартам | • Проверка ISO 22301<br/>• Аудит документации<br/>• Отслеживание требований<br/>• Генерация отчетов |
| **System Admin** | Администрирование системы | • Настройка пользователей<br/>• Мониторинг инфраструктуры<br/>• Управление интеграциями<br/>• Резервное копирование |
| **Executive** | Стратегические решения | • Просмотр дашбордов<br/>• Анализ KPI<br/>• Утверждение планов<br/>• Распределение ресурсов |
| **Risk Analyst** | Управление рисками | • Оценка рисков<br/>• BIA (Business Impact Analysis)<br/>• Анализ уязвимостей<br/>• Рекомендации по митигации |

---

## 3. Внешние системы

### 3.1 Критические зависимости (Critical Path)

| Система | Провайдер | Назначение | Регион | SLA |
|---------|-----------|------------|--------|-----|
| **Temporal Cloud** | Temporal.io | Оркестрация AI-workflow | eu-west-3.gcp | 99.9% |
| **Supabase** | Supabase | PostgreSQL база данных | eu-north-1 | 99.95% |
| **Qdrant Cloud** | Qdrant | Vector search для RAG | eu-west-1 | 99.9% |
| **Upstash Redis** | Upstash | Cache + Event Streams | us-east-1 | 99.99% |

### 3.2 Интеграции (Optional)

| Система | Назначение | Протокол |
|---------|------------|----------|
| **GitHub** | Синхронизация кода, Issues, Projects | REST API + Webhooks |
| **Email (SMTP)** | Уведомления пользователей | SMTP |
| **SMS (Twilio)** | Критические алерты | REST API |
| **Anthropic Claude** | AI ассистенты (12 экспертов) | REST API |

---

## 4. Основные функции платформы

```mermaid
mindmap
  root((AI-Platform-ISO))
    BCM Management
      Business Impact Analysis
      Risk Assessment
      Recovery Plans
      Crisis Response
    Compliance
      ISO 22301
      Audit Trail
      Policy Management
      Compliance Tracking
    AI Intelligence
      Workflow Optimization
      Predictive Analytics
      12 Expert Assistants
      Smart Recommendations
    Documentation
      Living Docs
      Templates
      Version Control
      Smart Search
    Collaboration
      Community Intelligence
      Case Sharing
      Multi-Agent
      Stakeholder Management
```

---

## 5. Ключевые use cases

### 5.1 Создание BIA (Business Impact Analysis)

```mermaid
sequenceDiagram
    actor Analyst as Risk Analyst
    participant Platform as AI-Platform-ISO
    participant AI as AI Engine
    participant DB as Supabase

    Analyst->>Platform: Start BIA wizard
    Platform->>AI: Request AI assistance
    AI->>Analyst: Ask clarifying questions
    Analyst->>Platform: Provide business context
    Platform->>AI: Analyze impact
    AI->>AI: Generate recommendations
    AI->>Platform: Return BIA draft
    Platform->>Analyst: Display BIA with AI suggestions
    Analyst->>Platform: Review & approve
    Platform->>DB: Save BIA
    Platform->>Analyst: BIA saved ✅
```

### 5.2 Активация плана реагирования

```mermaid
sequenceDiagram
    actor BCM as BCM Manager
    participant Platform as AI-Platform-ISO
    participant Temporal as Temporal Cloud
    participant Notify as Notification Service

    BCM->>Platform: Activate response plan
    Platform->>Temporal: Start incident workflow
    Temporal->>Temporal: Execute plan steps
    Temporal->>Notify: Send notifications
    Notify->>Notify: SMS to crisis team
    Notify->>Notify: Email to stakeholders
    Platform->>BCM: Plan activated ✅
    Platform->>BCM: Real-time progress tracking
```

### 5.3 Compliance audit

```mermaid
sequenceDiagram
    actor Officer as Compliance Officer
    participant Platform as AI-Platform-ISO
    participant AI as AI Engine
    participant DB as Supabase

    Officer->>Platform: Request ISO 22301 audit
    Platform->>DB: Query all requirements
    DB->>Platform: Return compliance data
    Platform->>AI: Analyze gaps
    AI->>AI: Generate recommendations
    AI->>Platform: Return audit report
    Platform->>Officer: Display report with gaps
    Officer->>Platform: Export to PDF
    Platform->>Officer: PDF downloaded ✅
```

---

## 6. Границы системы (System Boundaries)

### Что ВНУТРИ платформы:

✅ **Business Logic:**
- BIA Service
- Risk Service
- Compliance Service
- Governance Service
- Documents Service
- Response Service
- Validation Service
- Learning Service
- Planning Service
- Plans Service
- Living Docs

✅ **AI Foundation:**
- Workflow Intelligence (THE BRAIN)
- AI Workflow Optimizer
- Workflow Engine (BPMN 2.0)
- Expertise Center (12 AI assistants)
- Community Intelligence
- Collective Agents
- Predictive Service

✅ **Infrastructure:**
- API Gateway
- Database Gateway
- EventBus
- Monitoring
- Auth Service

### Что ВНЕ платформы:

❌ **External Services:**
- Temporal Cloud (workflow orchestration)
- Supabase (database hosting)
- Qdrant Cloud (vector search)
- Upstash Redis (cache)
- GitHub (code repository)
- Email/SMS providers
- Anthropic Claude API

---

## 7. Интеграционные точки (Integration Points)

| Точка интеграции | Протокол | Направление | Назначение |
|------------------|----------|-------------|------------|
| **API Gateway :8000** | HTTPS/REST | Inbound | Прием всех API запросов |
| **Temporal gRPC** | gRPC | Outbound | Отправка workflow activities |
| **Supabase REST API** | HTTPS/REST | Bidirectional | CRUD операции с данными |
| **Qdrant gRPC** | gRPC | Bidirectional | Vector search queries |
| **Redis Protocol** | Redis | Bidirectional | Cache + Event Streams |
| **GitHub Webhooks** | HTTPS/Webhooks | Inbound | События из GitHub |
| **SMTP** | SMTP | Outbound | Отправка email |
| **Twilio API** | HTTPS/REST | Outbound | Отправка SMS |
| **Claude API** | HTTPS/REST | Outbound | AI assistance requests |

---

## 8. Non-Functional Requirements

| Категория | Требование | Метрика |
|-----------|------------|---------|
| **Availability** | Высокая доступность | 99.5% uptime |
| **Performance** | Быстрый отклик API | < 200ms (p95) |
| **Scalability** | Горизонтальное масштабирование | 1000+ concurrent users |
| **Security** | Безопасность данных | JWT + OAuth2 + RBAC |
| **Compliance** | ISO 22301 | Full compliance |
| **Data Residency** | EU data residency | EU-only regions |
| **Backup** | Автоматическое резервирование | Daily backups |
| **Disaster Recovery** | Восстановление | RPO 1h, RTO 4h |

---

## 9. Security Context

```mermaid
graph LR
    subgraph "Public Internet"
        USER[User Browser]
    end

    subgraph "DMZ"
        WAF[Web Application<br/>Firewall]
        APIGW[API Gateway<br/>:8000]
    end

    subgraph "Application Network (Private)"
        PLATFORM[AI-Platform-ISO<br/>Services]
    end

    subgraph "Data Network (Private)"
        DB[(Databases)]
    end

    subgraph "External Cloud (TLS)"
        CLOUD[Cloud Services<br/>Temporal, Supabase, etc.]
    end

    USER -->|HTTPS| WAF
    WAF -->|JWT Validation| APIGW
    APIGW -->|Internal Network| PLATFORM
    PLATFORM -->|Encrypted| DB
    PLATFORM -->|TLS 1.3| CLOUD

    style USER fill:#ffcdd2
    style WAF fill:#fff3e0
    style APIGW fill:#fff9c4
    style PLATFORM fill:#e8f5e9
    style DB fill:#e1f5fe
    style CLOUD fill:#f3e5f5
```

---

## 10. Deployment Context

```mermaid
graph TB
    subgraph "Development"
        DEV[Developer Workstation<br/>Docker Compose]
    end

    subgraph "Staging"
        STAGE[Staging Environment<br/>Docker Swarm]
    end

    subgraph "Production"
        PROD[Production Environment<br/>Kubernetes (Planned)]
    end

    subgraph "Cloud Services"
        TEMPORAL[Temporal Cloud]
        SUPABASE[Supabase]
        QDRANT[Qdrant]
        REDIS[Upstash Redis]
    end

    DEV -->|CI/CD| STAGE
    STAGE -->|CI/CD| PROD

    PROD --> TEMPORAL
    PROD --> SUPABASE
    PROD --> QDRANT
    PROD --> REDIS

    style DEV fill:#e3f2fd
    style STAGE fill:#fff3e0
    style PROD fill:#e8f5e9,stroke:#4caf50,stroke-width:3px
```

---

## Summary

**AI-Platform-ISO** - это AI-powered платформа для управления непрерывностью бизнеса (BCM) и соответствия стандарту ISO 22301.

**Ключевые характеристики:**
- 🤖 **AI-driven**: 12 экспертных ассистентов на базе Claude
- 🔄 **Workflow-based**: Temporal Cloud для оркестрации
- 📊 **Data-intensive**: PostgreSQL + Vector search
- ⚡ **Event-driven**: Redis Streams для асинхронной коммуникации
- 🔒 **Secure**: JWT + OAuth2 + RBAC
- 🌍 **EU-compliant**: Все данные в EU регионах

**Основные пользователи:**
- BCM Managers (управление планами)
- Compliance Officers (аудит соответствия)
- Risk Analysts (оценка рисков)
- System Admins (администрирование)
- Executives (стратегические решения)

**Внешние зависимости:**
- Temporal Cloud (workflow orchestration) - CRITICAL
- Supabase (database) - CRITICAL
- Qdrant (vector search)
- Upstish Redis (cache + events)
- GitHub, Email, SMS, Anthropic Claude

---

**Generated:** 2025-10-06
**Next Level:** [C4 Level 2 - Containers](C4_LEVEL2_CONTAINERS.md)
