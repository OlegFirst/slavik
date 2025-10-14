# Диаграмма архитектуры системы мониторинга

**Version**: 2.0
**Date**: October 11, 2025

## Full System Architecture

```mermaid
graph TB
    subgraph "Services Layer"
        S1[Platform Services<br/>27 services]
        S2[Intelligent Core<br/>10 services]
        S3[Infrastructure<br/>~7 services]
        S4[Interface<br/>3 services]
    end

    subgraph "Metrics Collection"
        PROM[Prometheus<br/>:9090<br/>Scraper + Storage]
        GRAF[Grafana<br/>:3000<br/>Visualization]
    end

    subgraph "Service Discovery v2.0 :8500"
        CATALOG[Service Catalog<br/>service-catalog.yaml<br/>27 templates]
        REGISTRY[Service Registry<br/>Runtime state]
        UNIFIED[Unified View<br/>catalog + runtime]
        EB_INT[EventBus Integration]
    end

    subgraph "MIO Manager EYES :8046"
        direction TB
        EH[Event Handlers<br/>SD events]

        subgraph "Phase 2.1 Observers"
            MCO[MetricsCoverageObserver<br/>every 5 min]
            MHC[MetricsHealthChecker<br/>every 1 min]
        end

        subgraph "Phase 2.2 Intelligence Future"
            EGD[EventGapDetector]
            MLPM[MLModelPerformanceMonitor]
            SOD[StuckOrganizationDetector]
            CCD[CoordinationConflictDetector]
            EQM[ExpertiseQualityMonitor]
        end

        SCHED[SmartScheduler<br/>APScheduler]
    end

    subgraph "EventBus"
        EVENTS[Event Channels<br/>platform.monitoring.*<br/>platform.mio.*<br/>platform.brain.*<br/>platform.devops.*]
    end

    subgraph "Decision & Action Layer"
        BRAIN[Brain AI Event Manager<br/>:8043<br/>Decisions]
        DEVOPS[DevOps Agent<br/>Auto-fixes]
        ANALYTICS[Analytics Specialist<br/>:8041<br/>Analysis]
    end

    %% Metrics flow
    S1 -->|/metrics| PROM
    S2 -->|/metrics| PROM
    S3 -->|/metrics| PROM
    S4 -.->|no metrics| PROM

    PROM -->|scrape| GRAF

    %% Service Discovery flow
    S1 -->|register| REGISTRY
    S2 -->|register| REGISTRY
    S3 -->|register| REGISTRY

    CATALOG -->|templates| UNIFIED
    REGISTRY -->|runtime data| UNIFIED

    %% Service Discovery events
    EB_INT -->|service_registered| EVENTS
    EB_INT -->|service_disconnected| EVENTS
    EB_INT -->|critical_timeout| EVENTS

    %% MIO observations
    UNIFIED -->|GET /v2/catalog/services| MCO
    PROM -->|GET /api/v1/targets| MCO
    PROM -->|GET /api/v1/targets| MHC

    MCO -->|observations| EVENTS
    MHC -->|observations| EVENTS

    %% Event handling
    EVENTS -->|subscribe| EH
    EH -->|trigger checks| MCO
    EH -->|trigger checks| MHC

    SCHED -->|schedule| MCO
    SCHED -->|schedule| MHC

    %% Decision flow
    EVENTS -->|subscribe| BRAIN
    EVENTS -->|subscribe| ANALYTICS
    EVENTS -->|subscribe| DEVOPS

    BRAIN -->|decisions| EVENTS
    DEVOPS -->|action_completed| EVENTS

    %% Styling
    classDef services fill:#e1f5ff,stroke:#01579b
    classDef prometheus fill:#fff9c4,stroke:#f57f17
    classDef discovery fill:#f3e5f5,stroke:#4a148c
    classDef mio fill:#e8f5e9,stroke:#1b5e20
    classDef eventbus fill:#fce4ec,stroke:#880e4f
    classDef decision fill:#fff3e0,stroke:#e65100

    class S1,S2,S3,S4 services
    class PROM,GRAF prometheus
    class CATALOG,REGISTRY,UNIFIED,EB_INT discovery
    class EH,MCO,MHC,EGD,MLPM,SOD,CCD,EQM,SCHED mio
    class EVENTS eventbus
    class BRAIN,DEVOPS,ANALYTICS decision
```

## Event Flow Diagrams

### 1. New Service Registration Flow

```mermaid
sequenceDiagram
    participant SVC as New Service
    participant SD as Service Discovery v2
    participant EB as EventBus
    participant MIO as MIO Manager EYES
    participant PROM as Prometheus
    participant BRAIN as Brain
    participant DA as DevOps Agent

    Note over SVC: Service starts
    SVC->>SD: POST /register {service_name, port, ...}
    SD->>SD: Update registry
    SD->>EB: publish(service_registered)

    Note over EB: Event broadcast
    EB->>MIO: service_registered event

    Note over MIO: Event Handler triggered
    MIO->>PROM: GET /api/v1/targets (check if monitored)
    PROM-->>MIO: targets list

    alt Service NOT in Prometheus
        MIO->>MIO: Check metrics endpoint accessibility
        MIO->>EB: publish(service_not_monitored_observed)

        EB->>BRAIN: service_not_monitored_observed
        BRAIN->>BRAIN: AI analysis (Claude)
        BRAIN->>EB: publish(decision_made: add_to_prometheus)

        EB->>DA: decision_made event
        DA->>DA: Update prometheus.yml
        DA->>PROM: POST /-/reload
        DA->>EB: publish(action_completed)
    else Service already monitored
        MIO->>EB: publish(service_monitoring_ok)
    end
```

### 2. Metrics Coverage Observation Cycle

```mermaid
sequenceDiagram
    participant SCHED as SmartScheduler
    participant MCO as MetricsCoverageObserver
    participant SD as Service Discovery v2
    participant PROM as Prometheus
    participant EB as EventBus
    participant BRAIN as Brain

    Note over SCHED: Every 5 minutes
    SCHED->>MCO: _observe_metrics_coverage()

    MCO->>SD: GET /v2/catalog/services
    SD-->>MCO: unified_services[]

    MCO->>PROM: GET /api/v1/targets
    PROM-->>MCO: prometheus_targets[]

    MCO->>MCO: Compare lists<br/>Calculate coverage

    alt Coverage < 100%
        MCO->>EB: publish(metrics_coverage_observed)<br/>{coverage: 85%, missing: 4}

        loop For each missing service
            MCO->>EB: publish(service_not_monitored_observed)
        end

        EB->>BRAIN: coverage observation
        BRAIN->>BRAIN: Analyze trend<br/>Decide if action needed
    else Coverage = 100%
        MCO->>EB: publish(metrics_coverage_observed)<br/>{coverage: 100%}
    end
```

### 3. Metrics Health Check Cycle

```mermaid
sequenceDiagram
    participant SCHED as SmartScheduler
    participant MHC as MetricsHealthChecker
    participant PROM as Prometheus
    participant EB as EventBus
    participant BRAIN as Brain
    participant NS as Notification Service

    Note over SCHED: Every 1 minute
    SCHED->>MHC: _check_metrics_health()

    MHC->>PROM: GET /api/v1/targets
    PROM-->>MHC: targets[] with health info

    loop For each target
        MHC->>MHC: Check:<br/>- endpoint_reachable?<br/>- last_scrape fresh?<br/>- scrape_error?<br/>- scrape_duration OK?
    end

    MHC->>MHC: Categorize:<br/>healthy / warning / critical

    alt Critical issues detected
        MHC->>EB: publish(metrics_health_issue_observed)<br/>{severity: critical, issues: [...]}

        EB->>BRAIN: health issue event
        BRAIN->>BRAIN: AI analysis<br/>Decide severity
        BRAIN->>EB: publish(decision_made: notify_oncall)

        EB->>NS: notification decision
        NS->>NS: Send Slack + PagerDuty
    else All healthy
        MHC->>EB: publish(metrics_health_observed)<br/>{overall_health: healthy}
    end
```

## Component Interaction Matrix

| Component | Produces Events | Consumes Events | External APIs |
|-----------|----------------|-----------------|---------------|
| **Service Discovery v2** | service_registered<br/>service_disconnected<br/>critical_timeout | - | - |
| **MIO Manager** | metrics_coverage_observed<br/>service_not_monitored_observed<br/>metrics_health_observed<br/>metrics_health_issue_observed | service_registered<br/>service_disconnected<br/>critical_timeout | Prometheus API<br/>SD v2 API |
| **Brain** | decision_made | platform.mio.*<br/>platform.monitoring.* | Anthropic AI API |
| **DevOps Agent** | action_completed | decision_made | Prometheus reload<br/>Docker API<br/>Git API |
| **Analytics** | - | All events | PostgreSQL |
| **Notification** | - | decision_made (notify) | Slack API<br/>PagerDuty API |

## Technology Stack

### MIO Manager (EYES)
```python
# Core framework
fastapi              # Web framework
uvicorn[standard]    # ASGI server
pydantic             # Data validation

# Scheduling
apscheduler          # Job scheduling

# HTTP clients
httpx                # Async HTTP client

# Event infrastructure
redis                # EventBus backend
asyncpg              # PostgreSQL for persistence

# Metrics
prometheus-client    # Prometheus exporter
```

### Service Discovery v2.0
```python
fastapi
pydantic
pydantic-settings
sqlalchemy           # ORM
asyncpg              # PostgreSQL driver
redis                # Registry cache
httpx                # Service health checks
pyyaml               # Catalog loading
```

### Prometheus
```yaml
# Time-series database
prometheus:2.x

# Exporters
node-exporter        # System metrics
postgres-exporter    # PostgreSQL metrics
custom exporters     # Service-specific
```

## Data Models

### UnifiedService (Service Discovery)
```python
@dataclass
class UnifiedService:
    # From catalog (static)
    name: str
    type: str
    business_process: str
    kpis: List[str]
    expected_port: Optional[int]
    metrics_endpoint: Optional[str]
    health_endpoint: Optional[str]

    # From runtime (dynamic)
    runtime_status: ServiceStatus
    registration_status: RegistrationStatus
    orchestrator: Optional[str]
    actual_port: Optional[int]
    health_status: Optional[str]
    last_seen: Optional[datetime]
```

### MetricsCoverageObservation (MIO)
```python
@dataclass
class MetricsCoverageObservation:
    timestamp: datetime
    coverage_percentage: float
    total_registered_services: int
    monitored_services: int
    not_monitored_services: int
    unknown_services: int
    not_monitored_list: List[str]
    unknown_list: List[str]
    recommendation: str
```

### MetricsHealthObservation (MIO)
```python
@dataclass
class MetricsHealthObservation:
    timestamp: datetime
    total_services: int
    healthy_services: int
    warning_services: int
    critical_services: int
    unreachable_services: int
    service_healths: List[ServiceMetricsHealth]
    overall_health: str  # healthy/degraded/critical
    critical_issues: List[str]
    recommendation: str
```

## Configuration

### MIO Manager Settings
```python
# config.py
class Settings(BaseSettings):
    # Service info
    SERVICE_NAME: str = "mio-manager"
    SERVICE_PORT: int = 8046

    # External services
    PROMETHEUS_URL: str = "http://prometheus:9090"
    SERVICE_DISCOVERY_URL: str = "http://service-discovery:8500"
    EVENTBUS_URL: str = "http://eventbus:3001"

    # Observation intervals
    COVERAGE_CHECK_INTERVAL_MINUTES: int = 5
    HEALTH_CHECK_INTERVAL_MINUTES: int = 1

    # Thresholds
    SCRAPE_FRESHNESS_THRESHOLD_SECONDS: int = 120
    CRITICAL_COVERAGE_THRESHOLD_PERCENT: float = 80.0
```

### Service Discovery Settings
```python
class Settings(BaseSettings):
    # Catalog
    CATALOG_PATH: str = "/app/service-catalog/service-catalog.yaml"
    CATALOG_VERSION: str = "2.0.0"

    # Registry
    REGISTRY_REDIS_URL: str = "redis://redis:6379/0"
    HEARTBEAT_TIMEOUT_SECONDS: int = 60

    # EventBus
    EVENTBUS_URL: str = "http://eventbus:3001"
    PUBLISH_EVENTS: bool = True
```

## Deployment

### Docker Compose Services
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    depends_on:
      - prometheus

  service-discovery:
    build: ./service-discovery
    ports:
      - "8500:8500"
    environment:
      - EVENTBUS_URL=http://eventbus:3001
    depends_on:
      - redis
      - postgres
      - eventbus

  mio-manager:
    build: ./mio-manager
    ports:
      - "8046:8046"
    environment:
      - PROMETHEUS_URL=http://prometheus:9090
      - SERVICE_DISCOVERY_URL=http://service-discovery:8500
      - EVENTBUS_URL=http://eventbus:3001
    depends_on:
      - prometheus
      - service-discovery
      - eventbus

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=ai_platform
      - POSTGRES_USER=platform
      - POSTGRES_PASSWORD=secret
```

## Monitoring Dashboards

### Grafana Dashboards

#### 1. Platform Overview
- Total services (from Service Discovery)
- Service health distribution
- Metrics coverage percentage
- EventBus activity

#### 2. MIO Manager Dashboard
- Observation cycles status
- Coverage trend (last 24h)
- Health issues detected
- Events published rate

#### 3. Service Discovery Dashboard
- Registered services
- Missing services alert
- Unknown services alert
- Registration events rate

## Alerts & Rules

### Prometheus Alert Rules
```yaml
groups:
  - name: monitoring_coverage
    rules:
      - alert: LowMetricsCoverage
        expr: mio_metrics_coverage_percentage < 90
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low metrics coverage: {{ $value }}%"

      - alert: CriticalMetricsCoverage
        expr: mio_metrics_coverage_percentage < 80
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "CRITICAL: Metrics coverage below 80%"

  - name: service_health
    rules:
      - alert: ServiceMetricsUnhealthy
        expr: mio_unhealthy_services_count > 0
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "{{ $value }} services have unhealthy metrics"

      - alert: ServiceMetricsUnreachable
        expr: mio_unreachable_endpoints_count > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "{{ $value }} metrics endpoints unreachable"
```

---

**Last Updated**: October 11, 2025
**Diagram Version**: 2.0
**Mermaid Compatible**: ✅ Yes
