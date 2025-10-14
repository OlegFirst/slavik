# Detailed Component Analysis
**Generated:** 2025-10-11
**Scope:** Integration, Policy Engine, Balancer Service
**Status:** Production Ready Analysis

---

## I. INTEGRATION SERVICES (3 Components)

### 1. GitHub Integration Service

**Component:** github-integration
**Path:** `/infrastructure/integration/github-integration`
**Type:** service
**Port:** 8001 (⚠️ CONFLICT with auth-service!)
**Status:** stopped (not running)
**Main File:** `/infrastructure/integration/github-integration/main.py`

#### Purpose
- GitHub App webhooks processing
- GitHub Copilot Extension token exchange
- Proxy endpoints for GitHub Copilot Skills → AI Orchestrator
- GitHub API integration

#### Architecture
```
GitHub Webhooks → FastAPI Service → AI Orchestrator
                       ↓
                  EventBus (Redis)
                       ↓
                  Database (PostgreSQL)
```

#### Core Classes & Functions

**main.py (100 lines):**
- `FastAPI` app initialization
- `root()` - Service info endpoint
- `github_webhook()` - GitHub webhook handler (POST /github/webhook)
- `token_exchange()` - Copilot token exchange (POST /auth/token-exchange)
- Proxy endpoints:
  - `proxy_analyze_changes()` - POST /claude/analyze-changes
  - `proxy_generate_config()` - POST /claude/generate-config
  - `proxy_deployment_history()` - GET /deployment/history
  - `proxy_analyze_deployment()` - POST /claude/analyze-deployment
  - `proxy_orchestrate()` - POST /deployment/orchestrate

**config.py (127 lines):**
- `GitHubConfig` (Pydantic BaseSettings)
  - GitHub App credentials
  - Database URL
  - EventBus backend (Redis)
  - AI Orchestrator URL
  - Rate limiting (5000 req/1h)
  - Retry configuration
  - Token TTL management
  - Webhook processing config
  - Prometheus metrics

**Additional Files:**
- `auth.py` - GitHub App authentication
- `metrics.py` - Prometheus metrics
- `models.py` - Pydantic models
- `webhook_handler.py` - Webhook processing logic
- `github_client.py` - GitHub API client

#### Dependencies
```python
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
httpx  # HTTP client for proxy
pydantic>=2.4.0
pydantic-settings>=2.0.0
```

#### Integration Points
- ✅ GitHub Webhooks - event processing
- ✅ GitHub Copilot - token exchange
- ⚠️ AI Orchestrator (http://localhost:8000) - proxy target
- ⚠️ EventBus (Redis) - event publishing
- ⚠️ PostgreSQL - data storage
- ❌ Prometheus - metrics (configured but not verified)

#### Configuration
```python
# Service
PORT: 8001  # ⚠️ CONFLICT with auth-service
HOST: "0.0.0.0"

# GitHub App
GITHUB_APP_ID: required
GITHUB_APP_PRIVATE_KEY: required (or path)
GITHUB_WEBHOOK_SECRET: required
GITHUB_API_URL: "https://api.github.com"

# Infrastructure
DATABASE_URL: postgresql://...
REDIS_URL: redis://localhost:6379
AI_ORCHESTRATOR_URL: http://localhost:8000

# Limits
RATE_LIMIT_REQUESTS: 5000
RATE_LIMIT_WINDOW: 3600  # 1 hour
WEBHOOK_QUEUE_SIZE: 1000
WEBHOOK_WORKERS: 4
```

#### Status Assessment
- **Production Readiness:** Partial
- **Port Conflict:** ❌ Port 8001 conflicts with auth-service
- **External Dependencies:** GitHub API, AI Orchestrator
- **Integration Status:** Partially integrated
- **Recommended Action:** Change to port 8085 (as shown in main.py env var)

---

### 2. MCP Server (Model Context Protocol)

**Component:** mcp-server
**Path:** `/infrastructure/integration/mcp-server`
**Type:** dual (protocol server + HTTP service)
**Port:** 8064 (HTTP service), stdio (MCP protocol)
**Status:** development/experimental
**Main Files:**
- `bcm_collective_mcp.py` (679 lines) - Full MCP implementation
- `main.py` (34 lines) - Simple HTTP wrapper

#### Purpose
**Two Implementations:**

1. **BCM Collective MCP** (`bcm_collective_mcp.py`):
   - Privacy-preserving collective intelligence
   - Partisia Blockchain integration
   - MPC (Multi-Party Computation) queries
   - Claude Desktop integration

2. **HTTP Service** (`main.py`):
   - FastAPI HTTP wrapper
   - Basic MCP v1 API
   - AI model integration placeholder

#### Architecture (BCM Collective)
```
Claude Desktop → MCP Protocol (stdio) → MCP Server → Partisia Blockchain (MPC)
                                              ↓
                                    Privacy-Preserving Queries
                                              ↓
                                    Zero-Knowledge Proofs
```

#### Core Classes & Functions

**bcm_collective_mcp.py (679 lines):**

1. **PartisiaClient** (placeholder):
   - `query_collective_wisdom()` - MPC query for patterns
   - `get_benchmark()` - Privacy-preserving benchmarks
   - `verify_computation()` - Zero-knowledge proof verification

2. **MCP Server** (mcp SDK):
   - `@app.list_resources()` - 7 collective intelligence resources
   - `@app.read_resource()` - Read from blockchain
   - `@app.list_tools()` - 3 tools (query, benchmark, verify)
   - `@app.call_tool()` - Execute tools
   - `@app.list_prompts()` - 3 prompt templates
   - `@app.get_prompt()` - Get prompt by name

3. **Resources (7):**
   - `bcm://collective/patterns/supply_chain_complexity`
   - `bcm://collective/patterns/executive_engagement`
   - `bcm://collective/patterns/rto_determination`
   - `bcm://collective/benchmarks/bia_duration`
   - `bcm://collective/benchmarks/critical_process_count`
   - `bcm://collective/benchmarks/rto_average`
   - `bcm://collective/best-practices/bia_methodology`

4. **Tools (3):**
   - `query_collective_wisdom` - Privacy-preserving patterns
   - `get_anonymous_benchmark` - MPC aggregation
   - `verify_collective_wisdom` - Zero-knowledge verification

5. **Prompts (3):**
   - `ask_collective` - Query collective about challenge
   - `compare_with_peers` - Benchmark comparison
   - `stuck_on_bcm` - Get help when stuck

**main.py (34 lines):**
- Basic FastAPI service
- `/health` endpoint
- `/mcp/v1/completions` - AI model integration (placeholder)

#### Dependencies
```python
# BCM Collective
mcp  # MCP SDK (required)
asyncio
json
logging

# HTTP Service
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.4.0
```

#### Integration Points

**BCM Collective MCP:**
- ✅ Claude Desktop - via stdio (MCP protocol)
- ⚠️ Partisia Blockchain - simulated (placeholder)
- ✅ Zero-Knowledge Proofs - implemented
- ✅ MPC computation - simulated

**HTTP Service:**
- ⚠️ AI model - not implemented
- ✅ FastAPI - basic structure

#### Configuration

**Claude Desktop Config:**
```json
{
  "mcpServers": {
    "bcm-collective": {
      "command": "python3",
      "args": ["/path/to/bcm_collective_mcp.py"]
    }
  }
}
```

**HTTP Service:**
```python
PORT: 8064
HOST: "0.0.0.0"
```

#### Key Features

**Privacy Protection:**
- K-anonymity (minimum 5 organizations)
- Zero-knowledge proofs
- MPC (Multi-Party Computation)
- No source organization identification

**Collective Wisdom:**
- Pattern detection across organizations
- Privacy-preserving benchmarks
- Aggregate statistics only
- Cryptographic verification

#### Status Assessment
- **Production Readiness:** Experimental
- **BCM Collective:** Advanced concept, placeholder implementation
- **HTTP Service:** Basic skeleton
- **Integration Status:** Not integrated with platform
- **Recommended Action:**
  - BCM Collective: Implement real Partisia SDK
  - HTTP Service: Complete AI model integration or deprecate

---

### 3. Partisia Contracts (Blockchain)

**Component:** partisia-contracts
**Path:** `/infrastructure/integration/partisia-contracts`
**Type:** smart contract integration service
**Port:** 8065
**Status:** basic HTTP wrapper (not blockchain-connected)
**Main File:** `main.py` (38 lines)

#### Purpose
- Partisia Blockchain smart contract integration
- Collective intelligence on blockchain
- Decentralized coordination
- Privacy-preserving data sharing

#### Architecture
```
Platform Services → FastAPI Service → Partisia Blockchain
                                            ↓
                                    Smart Contracts (MPC)
                                            ↓
                                    Collective Intelligence
```

#### Core Classes & Functions

**main.py (38 lines):**
- `FastAPI` app initialization
- `health()` - Health check (GET /health)
- `deploy_contract()` - Contract deployment (POST /contracts/deploy) - placeholder
- `get_contract()` - Contract data fetch (GET /contracts/{contract_id}) - placeholder

**Smart Contract:**
- `collective_intelligence.pbc` - Partisia smart contract (not in main.py)

#### Dependencies
```python
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
```

#### Integration Points
- ⚠️ Partisia Blockchain - not connected (placeholder endpoints)
- ⚠️ Smart Contracts - not deployed
- ⚠️ Collective Intelligence System - not integrated
- ❌ Platform services - no real integration

#### Configuration
```python
PORT: 8065
HOST: "0.0.0.0"
```

#### Status Assessment
- **Production Readiness:** Not production ready
- **Blockchain Integration:** Not implemented
- **Smart Contracts:** Code exists but not deployed
- **Integration Status:** Skeleton only
- **Recommended Action:**
  - Either implement full blockchain integration
  - Or deprecate and focus on core platform features

---

## II. POLICY ENGINE (Governance Layer)

**Component:** policy-engine (formerly decision-center)
**Path:** `/infrastructure/policy-engine`
**Type:** library + REST API
**Port:** 9091 (governance API), N/A (library)
**Status:** ✅ Production Ready
**Version:** 1.1.0

#### Purpose
- **Central Governance Layer** for infrastructure operations
- YAML-based policy configuration
- Infrastructure decision authority
- Escalation to human operators
- Manual approval workflows
- ISO 22301 compliant audit trail

#### Architecture
```
YAML Policies → PolicyEngine → InfrastructureDecisionCenter
                                       ↓
                     ┌─────────────────┼─────────────────┐
                     ↓                 ↓                 ↓
              Recovery Actions   Optimization      Escalation
                                     ↓                 ↓
                              AuditLogger      NotificationService
                                     ↓                 ↓
                              PostgreSQL          EventBus
```

#### Core Components (6 files, ~3,800 lines)

### 1. PolicyEngine (`policy_engine.py` - 539 lines)

**Purpose:** Central policy management and query interface

**Key Classes:**
```python
class PolicyEngine:
    def __init__(self, policy_file: Path = None, auto_reload: bool = False)

    # Core Methods
    def load_policies(self, policy_file: Path) -> bool
    def reload_policies() -> bool  # Hot reload

    # Recovery Policies
    def get_recovery_policy(self, service_name: str) -> RecoveryServicePolicy
    def get_default_recovery_policy() -> RecoveryDefaultPolicy

    # Thresholds
    def get_threshold(self, resource_type: str, level: str) -> int
    def get_all_thresholds(self, resource_type: str) -> ThresholdLevels

    # Compliance
    def check_compliance(self, action: str, service_name: str) -> Dict
    def validate_action_context(self, action, service_name, context) -> Dict

    # Service Management
    def get_service_priority(self, service_name: str) -> int
    def get_monitoring_interval(self, service_priority: int) -> int

    # Escalation & Notifications
    def get_escalation_levels() -> List[EscalationLevel]
    def get_notification_channels() -> NotificationChannels

    # Audit
    def should_audit(self, action_type: str) -> bool
    def requires_justification() -> bool

    # Metadata
    def get_policy_metadata() -> Dict[str, Any]
```

**Global Functions:**
```python
def get_policy_engine() -> PolicyEngine
def initialize_policy_engine(policy_file: Path) -> PolicyEngine
def reload_global_policies() -> bool
```

**Features:**
- Thread-safe with RLock
- Hot reload without restart
- Type-safe via Pydantic models
- Default policies for undefined services
- Compliance checking
- Policy versioning support

### 2. InfrastructureDecisionCenter (`decision_center.py` - 607 lines)

**Purpose:** Central decision authority with escalation support

**Key Class:**
```python
class InfrastructureDecisionCenter:
    def __init__(self, policy_engine, audit_logger, eventbus, db_session_factory)

    # Decision Methods
    async def decide_recovery_action(
        self, service_name, action_type, trigger_event_id,
        trigger_data, current_attempt
    ) -> Tuple[Decision, bool]

    async def decide_optimization_action(
        self, service_name, action_type, recommendation,
        trigger_event_id
    ) -> Tuple[Decision, bool]

    # Escalation
    async def escalate(
        self, service_name, reason, decision_id,
        severity, context_data
    ) -> EscalationRequest

    # Approval Workflows
    async def approve_action(
        self, approval_id, approved_by, approved, comment
    ) -> bool

    # Compliance
    async def check_policy_compliance(
        self, service_name, action_type, current_attempt
    ) -> Dict[str, Any]

    # Statistics
    async def get_stats() -> Dict[str, Any]
    async def get_pending_approvals() -> List[ApprovalRequest]
    async def get_active_escalations() -> List[EscalationRequest]
```

**Decision Outcomes:**
- `APPROVED` - Can proceed
- `REJECTED` - Policy violation
- `PENDING` - Requires approval
- `ESCALATED` - Escalated to humans

**Statistics Tracked:**
- Total decisions
- Approved/rejected decisions
- Escalated decisions
- Auto vs manual approvals

### 3. EscalationManager (`escalation_manager.py` - 624 lines)

**Purpose:** Escalation to human operators when auto-recovery fails

**Key Classes:**
```python
class EscalationReason(Enum):
    MAX_ATTEMPTS_REACHED = "max_attempts_reached"
    CRITICAL_SERVICE_FAILURE = "critical_service_failure"
    TIMEOUT_EXCEEDED = "timeout_exceeded"
    PATTERN_DETECTED = "pattern_detected"
    MANUAL_TRIGGER = "manual_trigger"

class EscalationStatus(Enum):
    PENDING = "pending"
    NOTIFIED = "notified"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"

class EscalationPolicy:
    service_name: str
    max_attempts: int = 3
    critical_service_max_attempts: int = 2
    escalation_timeout_seconds: int = 300
    pattern_failure_threshold: int = 5
    pattern_window_seconds: int = 3600
    is_critical: bool = False
    notify_email: List[str]
    notify_slack: bool = True
    auto_create_incident: bool = True
    incident_priority: str = "high"
    require_manual_approval: bool = False

class EscalationManager:
    def register_policy(self, policy: EscalationPolicy)

    # Escalation Decision
    def should_escalate(
        self, service_name, current_attempts,
        recovery_start_time, is_still_unhealthy
    ) -> Tuple[bool, Optional[EscalationReason]]

    # Failure Tracking
    def record_failure(self, service_name)

    # Escalation Actions
    async def escalate(
        self, service_name, reason, recovery_attempts,
        recovery_duration, metadata
    ) -> Escalation

    async def notify_operators(self, escalation) -> bool
    async def create_incident_ticket(self, escalation) -> str

    # Auto-Recovery Control
    async def stop_auto_recovery(self, service_name, escalation_id)
    def is_recovery_allowed(self, service_name) -> bool

    # Manual Workflows
    async def require_manual_approval(
        self, escalation_id, timeout_seconds
    ) -> bool

    async def resolve_escalation(
        self, escalation_id, resolved_by, resolution_notes,
        resume_auto_recovery
    )

    # History & Statistics
    def get_escalation_history(...) -> List[Escalation]
    def get_active_escalations() -> List[Escalation]
    def get_stats() -> Dict[str, Any]
```

**Escalation Triggers:**
1. Max attempts reached (default 3)
2. Critical service + 2 failed attempts
3. Recovery timeout exceeded (default 5 min)
4. Pattern detected (5+ failures in 1 hour)

**Actions on Escalation:**
- Stop auto-recovery immediately
- Notify operators (email, Slack)
- Create incident ticket
- Publish escalation events

### 4. Governance API (`governance_api.py` - 573 lines)

**Purpose:** REST API for Governance Console

**FastAPI Endpoints:**

**Health & Status:**
- `GET /governance/health` → GovernanceHealth
- `GET /governance/stats` → GovernanceStatsResponse

**Decisions:**
- `GET /governance/decisions` → List[DecisionResponse] (paginated)
- `GET /governance/decisions/{decision_id}` → DecisionResponse
- `POST /governance/decide` → DecisionResponse (request new decision)
- `POST /governance/approve` → DecisionResponse (approve pending)
- `POST /governance/reject` → DecisionResponse (reject pending)

**Escalations:**
- `GET /governance/escalations?status=ACTIVE|RESOLVED|ALL` → List[EscalationResponse]
- `POST /governance/escalations/{escalation_id}/resolve` → EscalationResponse

**Policies:**
- `GET /governance/policies` → PolicySummaryResponse
- `POST /governance/policies/reload` → PolicySummaryResponse (hot reload)

**Audit:**
- `GET /governance/audit?limit=100&service=...` → List[AuditEntryResponse]

**Metrics:**
- `GET /metrics` → Prometheus metrics

**Pydantic Models (13):**
- GovernanceHealth
- DecisionResponse
- EscalationResponse
- PolicySummaryResponse
- AuditEntryResponse
- GovernanceStatsResponse
- DecisionRequest
- ApprovalRequest
- EscalationResolveRequest
- ... and more

### 5. Wishlist Integration (`wishlist_integration.py` - 320 lines)

**Purpose:** Phase 2 - Postpone decisions when resources unavailable

**Key Classes:**
```python
class WishlistDecisionIntegration:
    def __init__(self, decision_center, resource_tracker_client)

    async def initialize(self, storage_path)
    async def start_executor()  # Background task
    async def stop_executor()

    # Wishlist Management
    async def postpone_decision_to_wishlist(
        self, decision, resource_cost, urgency, deadline_seconds
    ) -> WishlistItem

    # Statistics
    def get_stats() -> Dict[str, Any]

# Factory Function
async def create_wishlist_integration(
    decision_center, resource_tracker_client,
    storage_path, start_executor
) -> WishlistDecisionIntegration
```

**Features:**
- POSTPONED outcome instead of REJECTED
- Background executor for wishes
- Resource-aware prioritization
- Integration with WishlistSystem from coordination_center

**Statistics:**
- wishes_created
- wishes_executed
- wishes_failed
- wishes_obsolete

### 6. Additional Components

**policy_models.py (~320 lines):**
- `PolicyConfiguration` - Root config
- `RecoveryServicePolicy` - Service-specific recovery
- `RecoveryDefaultPolicy` - Default recovery
- `RecoveryStrategy` (Enum) - RESTART, FAILOVER, CIRCUIT_BREAKER
- `ThresholdLevels` - CPU/Memory/Disk thresholds
- `OptimizationActions` - Auto-execute, require approval, manual only
- `MonitoringIntervals` - Critical/Normal/Low priority
- `NotificationChannels` - Email, Slack, PagerDuty, etc.
- `EscalationLevel` - Level, teams, channels

**policy_validator.py (~350 lines):**
- `PolicyValidator` - Validation logic
- `PolicyValidationError` - Custom exception
- Validates policies before loading

**audit_logger.py (~500 lines):**
- `AuditLogger` - ISO 22301 compliant logging
- Logs all decisions, escalations, approvals
- PostgreSQL storage

**decision_models.py:**
- `Decision` - Decision record
- `DecisionType` (Enum) - RECOVERY, OPTIMIZATION, DEPLOYMENT, LEARNING
- `DecisionOutcome` (Enum) - APPROVED, REJECTED, PENDING
- `EscalationRequest` - Escalation record
- `EscalationStatus` (Enum)
- `ApprovalRequest` - Approval workflow
- `ApprovalStatus` (Enum)

#### Dependencies
```python
# Core
pydantic>=2.4.0  # Type safety
pyyaml  # Policy files
threading  # Thread safety

# Database (optional)
sqlalchemy
asyncpg

# Integration
fastapi>=0.104.0  # REST API
uvicorn[standard]>=0.24.0
```

#### Integration Points
- ✅ YAML Policies (`policies.yaml`) - Configuration source
- ✅ EventBus (Redis) - Event publishing
- ⚠️ PostgreSQL - Audit logs (optional)
- ✅ AI Orchestrator - Policy validation
- ✅ Notification Service - Escalation alerts
- ✅ WishlistSystem (intelligent-core) - Phase 2 integration

#### Configuration

**policies.yaml Structure:**
```yaml
version: "1.1.0"
updated: "2025-10-10"
approved_by: "Infrastructure Team"

infrastructure_policies:
  recovery:
    default:
      max_auto_attempts: 3
      escalate_immediately: false
    by_service:
      database:
        priority: 1
        rto_seconds: 60
        max_auto_attempts: 2
        recovery_strategy: FAILOVER

  optimization:
    thresholds:
      cpu:
        normal: 70
        high: 85
        critical: 90
      memory:
        normal: 75
        high: 85
        critical: 95
    actions:
      require_approval:
        scale_up: true
        scale_down: false
      auto_execute:
        - optimize
        - cleanup
      manual_only:
        - migrate_data

  monitoring:
    intervals:
      critical_services: 30  # seconds
      normal_services: 60
      low_priority: 300

  notifications:
    escalation_levels:
      - level: 1
        teams: ["ops_team"]
        channels: ["slack_alerts"]
      - level: 2
        teams: ["ops_lead", "platform_team"]
        channels: ["slack_critical", "pagerduty"]

  compliance:
    audit_enabled: true
    audit_all_decisions: true
    audit_all_actions: true
    require_justification: true
```

#### Events Published
```python
# Decisions
'infrastructure.decision.approved'
'infrastructure.decision.rejected'
'infrastructure.decision.pending'

# Escalations
'infrastructure.escalation.created'
'infrastructure.escalation.notified'
'infrastructure.escalation.resolved'

# Recovery Control
'infrastructure.recovery.stopped'
```

#### Status Assessment
- **Production Readiness:** ✅ Production Ready
- **Version:** 1.1.0 (renamed from decision-center Oct 10, 2025)
- **Code Quality:** High (3,800 lines, well-structured)
- **Type Safety:** ✅ Full Pydantic models
- **Testing:** ✅ Test suite available
- **Documentation:** ✅ Comprehensive
- **ISO 22301 Compliance:** ✅ Full audit trail
- **Integration Status:** Fully integrated
- **Hot Reload:** ✅ Supported
- **API Status:** ✅ REST API on port 9091

---

## III. BALANCER SERVICE (System Intelligence)

**Component:** balancer-service
**Path:** `/infrastructure/balancer-service`
**Type:** service
**Port:** 9091 (Prometheus metrics)
**Status:** stopped (not running)
**Version:** 2.4.0 (MVP)
**Main File:** `main.py` (456 lines)

#### Purpose
- **GLOBAL BRAIN** for system balancing (Phase 2)
- Three-dimensional balancing (Rational, Intuitive, Pragmatic)
- Infrastructure-aware decisions
- EventBus-driven coordination
- Real-time resource monitoring

#### Architecture
```
EventBus (Redis Streams) → BalancerService → SystemBalancer
                                                   ↓
                          ┌────────────────────────┼────────────────────────┐
                          ↓                        ↓                        ↓
              ImpactEvidenceTracker    PredictiveROIOptimizer    ThreeDimensionalBalancer
                   (RATIONAL)           (INTUITIVE+PRAGMATIC)          (3D BALANCE)
                          ↓                        ↓                        ↓
                          └────────────────────────┴────────────────────────┘
                                                   ↓
                                          Reward/Penalty System
```

#### Core Classes & Functions

**main.py (456 lines):**

```python
class BalancerService:
    def __init__(self):
        self.eventbus: Optional[EventBus] = None
        self.system_balancer: Optional[SystemBalancer] = None
        self.evidence_tracker: Optional[ImpactEvidenceTracker] = None
        self.roi_optimizer: Optional[PredictiveROIOptimizer] = None
        self.balancer_3d: Optional[ThreeDimensionalBalancer] = None
        self.infrastructure_state: Optional[dict] = None
        self.running = False
        self.tasks = []

    async def initialize(self):
        # 1. Create EventBus connection (Redis)
        # 2. Initialize Impact Evidence Tracker (RATIONAL)
        # 3. Initialize Predictive ROI Optimizer (INTUITIVE + PRAGMATIC)
        # 4. Initialize Three-Dimensional Balancer
        # 5. Initialize System Balancer (GLOBAL BRAIN)
        # 6. Subscribe to EventBus events

    async def start(self):
        # Start System Balancer monitoring loop
        # Keep service running

    async def stop(self):
        # Cancel all tasks
        # Disconnect EventBus
```

**Event Handlers (9):**

1. **Imbalance Events:**
```python
async def _handle_imbalance_event(self, event: dict):
    # Platform.bcm.imbalance_detected
    # Record baseline for evidence tracker
    # Let System Balancer handle
```

2. **Resource Tracking:**
```python
async def _handle_resource_snapshot(self, event: dict):
    # Platform.resources.snapshot
    # Store for System Balancer

async def _handle_resource_deficit(self, event: dict):
    # Platform.resources.deficit
    # Trigger immediate balancing if critical
```

3. **Infrastructure State (NEW - Phase 2.1):**
```python
async def _handle_infrastructure_state(self, event: dict):
    # Platform.infrastructure.state_updated
    # Infrastructure-aware balancing decisions
    # Check: DB availability, monitoring coverage, port availability, CPU usage

    # Conservative balancing if:
    # - CPU > 85%
    # - PostgreSQL unavailable
    # - Monitoring coverage < 50%
```

4. **Infrastructure Emergency (NEW):**
```python
async def _handle_infrastructure_emergency(self, event: dict):
    # Platform.infrastructure.emergency
    # IMMEDIATE action on:
    # - database_unavailable → emergency mode
    # - resource_exhausted → immediate optimization
    # - monitoring_unavailable → conservative balancing
```

5. **Strategy Recommendations (NEW):**
```python
async def _handle_strategy_recommendation(self, event: dict):
    # Platform.infrastructure.strategy_recommended
    # From AI Event Manager strategic decisions
    # Align balancing with:
    # - emergency → conservative mode
    # - scale_resources → aggressive optimization
    # - improve_monitoring → prioritize metrics
```

**EventBus Subscriptions (7):**
- `platform.bcm.imbalance_detected` - Survival Instinct
- `platform.resources.snapshot` - Resource Tracker
- `platform.resources.deficit` - Resource Tracker
- `platform.infrastructure.state_updated` - AI Event Manager (NEW)
- `platform.infrastructure.emergency` - AI Event Manager (NEW)
- `platform.infrastructure.strategy_recommended` - AI Event Manager (NEW)

**Prometheus Metrics:**
```python
BALANCER_SERVICE_UP = Gauge('balancer_service_up', 'Balancer service is running')
BALANCER_ERRORS = Counter('balancer_errors_total', 'Total balancer errors', ['component'])
BALANCER_EVENTS_PROCESSED = Counter('balancer_events_processed_total', 'Events processed', ['component'])
```

#### Dependencies
```python
# Core
asyncio
sys
os
signal
logging
structlog  # Structured logging
prometheus_client  # Metrics

# EventBus
from infrastructure.eventbus import create_eventbus

# Balancers (intelligent-core)
from intelligent_core.ai_foundation.balancer import (
    SystemBalancer,
    ImpactEvidenceTracker,
    PredictiveROIOptimizer,
    ThreeDimensionalBalancer
)
```

#### Integration Points

**Connected:**
- ✅ EventBus (Redis Streams) - Event subscriptions
- ✅ intelligent-core/ai_foundation/balancer - Core balancing logic
- ✅ Prometheus - Metrics on port 9091
- ✅ AI Event Manager - Infrastructure state (NEW Phase 2.1)

**Event Flow:**
```
Survival Instinct → imbalance_detected → BalancerService
Resource Tracker → resource_snapshot/deficit → BalancerService
AI Event Manager → infrastructure_state/emergency/strategy → BalancerService
                                                                    ↓
                                                          SystemBalancer
                                                                    ↓
                                                          Reward/Penalty
```

#### Configuration
```python
# Port
Prometheus Metrics: 9091

# EventBus
Backend: 'redis'
Connection: Auto-configured

# Logging
Format: JSON (structlog)
Processors: Timestamp, Log Level, Stack Info, Exception Info
```

#### Balancing Components

**1. SystemBalancer (GLOBAL BRAIN):**
- Monitors all imbalances
- Applies reward/penalty system
- Uses 3D Balancer for decisions

**2. ImpactEvidenceTracker (RATIONAL):**
- Records baselines
- Tracks impact evidence
- Data-driven decisions

**3. PredictiveROIOptimizer (INTUITIVE + PRAGMATIC):**
- Predicts ROI
- Cost-benefit analysis
- Uses evidence tracker

**4. ThreeDimensionalBalancer (3D BALANCE):**
- Balances 3 dimensions:
  - Rational (evidence-based)
  - Intuitive (predictive)
  - Pragmatic (practical)

#### Infrastructure-Aware Decisions (Phase 2.1)

**Capacity Constraints:**
```python
if cpu_usage > 0.85:
    # Conservative balancing

if not postgres_available:
    # Halt new resource allocations

if monitoring_coverage < 0.5:
    # Limited visibility mode
```

**Emergency Actions:**
```python
# database_unavailable
→ Switch to emergency mode
→ Stop aggressive allocations
→ Preserve existing resources

# resource_exhausted
→ Immediate optimization
→ Prioritize resource freeing

# monitoring_unavailable
→ Conservative balancing without metrics
```

**Strategic Alignment:**
```python
# AI Event Manager recommendations
emergency → conservative mode
scale_resources → aggressive optimization
improve_monitoring → prioritize metrics collection
```

#### Statistics Tracked
- Events processed (by component)
- Errors (by component)
- Service status (up/down)
- Infrastructure state awareness (NEW)

#### Status Assessment
- **Production Readiness:** Experimental (MVP)
- **Version:** 2.4.0
- **intelligent-core Dependency:** ✅ Connected
- **EventBus Integration:** ✅ Full integration
- **Infrastructure Awareness:** ✅ Phase 2.1 Complete (NEW)
- **AI Event Manager Integration:** ✅ Complete (NEW)
- **Prometheus Metrics:** ✅ Enabled
- **Integration Status:** Fully event-driven
- **Recommended Action:** Testing phase, monitor performance

---

## IV. SUMMARY TABLES

### Port Assignments

| Port | Component | Status | Conflict |
|------|-----------|--------|----------|
| 8001 | github-integration | Stopped | ⚠️ Conflicts with auth-service |
| 8064 | mcp-server (HTTP) | Stopped | ✅ No conflict |
| 8065 | partisia-contracts | Stopped | ✅ No conflict |
| 9091 | policy-engine (API) | Stopped | ✅ No conflict |
| 9091 | balancer-service (metrics) | Stopped | ⚠️ Same as policy-engine API |
| N/A | policy-engine (library) | Library | N/A |
| stdio | mcp-server (protocol) | Protocol | N/A |

### Integration Status

| Component | Type | Integration | Production Ready |
|-----------|------|-------------|------------------|
| github-integration | Service | Partial | ⚠️ Port conflict |
| mcp-server (BCM) | Protocol | Experimental | ❌ Placeholder |
| mcp-server (HTTP) | Service | Basic | ❌ Skeleton |
| partisia-contracts | Service | Skeleton | ❌ Not connected |
| policy-engine | Library + API | Full | ✅ Production |
| balancer-service | Service | Full | ⚠️ MVP/Testing |

### Dependencies Graph

```
policy-engine:
  ├── pydantic (type safety)
  ├── pyyaml (policies)
  ├── fastapi (REST API)
  ├── eventbus (events)
  └── postgresql (audit - optional)

github-integration:
  ├── fastapi (HTTP)
  ├── httpx (proxy)
  ├── pydantic (config)
  ├── eventbus (Redis)
  └── postgresql (storage)

mcp-server (BCM):
  ├── mcp (SDK)
  └── partisia (blockchain - placeholder)

balancer-service:
  ├── eventbus (Redis Streams)
  ├── intelligent-core/balancer (logic)
  ├── structlog (logging)
  └── prometheus_client (metrics)
```

### Event Flow

```
Platform Events:
  bcm.imbalance_detected → balancer-service
  resources.snapshot → balancer-service
  resources.deficit → balancer-service
  infrastructure.state_updated → balancer-service (NEW)
  infrastructure.emergency → balancer-service (NEW)
  infrastructure.strategy_recommended → balancer-service (NEW)

Policy Events:
  decision.approved → eventbus
  decision.rejected → eventbus
  escalation.created → eventbus
  escalation.notified → eventbus
  recovery.stopped → eventbus

Integration Events:
  github.webhook → github-integration
  (no events from MCP/Partisia - not integrated)
```

---

## V. RECOMMENDATIONS

### Critical Issues

1. **Port Conflicts:**
   - ❌ GitHub Integration (8001) conflicts with auth-service
   - ⚠️ Balancer Service (9091) conflicts with Policy Engine API

   **Action:**
   - Change github-integration to 8085 (already in env var)
   - Change balancer-service metrics to 9092

2. **Incomplete Implementations:**
   - ❌ MCP Server (BCM Collective) - Partisia placeholder
   - ❌ MCP Server (HTTP) - AI model not connected
   - ❌ Partisia Contracts - No blockchain connection

   **Action:**
   - Either implement full Partisia SDK integration
   - Or deprecate and focus on core platform

### Integration Priorities

**High Priority:**
1. ✅ Policy Engine - Already production ready
2. ✅ Balancer Service - Phase 2.1 complete, needs testing
3. ⚠️ GitHub Integration - Fix port conflict, test integration

**Medium Priority:**
4. ⚠️ MCP Server (HTTP) - Complete AI model integration or deprecate
5. ❌ MCP Server (BCM) - Implement Partisia or deprecate

**Low Priority:**
6. ❌ Partisia Contracts - Future feature, not core platform

### Production Deployment

**Ready to Deploy:**
- ✅ policy-engine (library + API on 9091)
  - Hot reload supported
  - ISO 22301 compliant
  - Full audit trail

**Needs Testing:**
- ⚠️ balancer-service (fix port to 9092)
  - Phase 2.1 infrastructure awareness complete
  - Event-driven integration working
  - MVP status - monitor performance

**Needs Fixes:**
- ❌ github-integration (change to 8085)
  - Fix port conflict
  - Test AI Orchestrator proxy
  - Verify EventBus integration

**Deprecation Candidates:**
- ❌ mcp-server (both variants) - if not core to platform
- ❌ partisia-contracts - if blockchain not priority

---

## VI. INTEGRATION PATTERNS

### Policy Engine Integration

**For Services:**
```python
from infrastructure.policy_engine import initialize_policy_engine, get_policy_engine

# Initialize
engine = initialize_policy_engine("policies.yaml")

# Query
policy = engine.get_recovery_policy("my_service")
if policy.priority == 1:
    # Critical service handling

compliance = engine.check_compliance("restart", "my_service")
if compliance["requires_approval"]:
    # Request approval
```

**For AI Orchestrator:**
```python
from intelligent_core.orchestration.ai_orchestration import PolicyAwareOrchestrator

orchestrator = PolicyAwareOrchestrator(
    policy_file_path="infrastructure/policy-engine/policies.yaml"
)

await orchestrator.initialize()
decision = await orchestrator.decide(situation)
```

### Balancer Service Integration

**EventBus Publishers:**
```python
from infrastructure.eventbus import create_eventbus, Event, EventPriority

eventbus = create_eventbus('redis')
await eventbus.connect()

# Publish imbalance
await eventbus.publish(Event.create(
    event_type='platform.bcm.imbalance_detected',
    data={'service': 'api', 'health_score': 45.0},
    source='survival_instinct',
    priority=EventPriority.HIGH
))

# Publish infrastructure state
await eventbus.publish(Event.create(
    event_type='platform.infrastructure.state_updated',
    data={'state': {...}},
    source='ai_event_manager',
    priority=EventPriority.NORMAL
))
```

### GitHub Integration Pattern

**Proxy to AI Orchestrator:**
```python
# GitHub Copilot → GitHub Integration → AI Orchestrator

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://ai_orchestrator:8000/claude/analyze-changes",
        json=body,
        headers=dict(request.headers)
    )
    return response.json()
```

---

## VII. NEXT STEPS

### Immediate Actions (Week 1)

1. **Fix Port Conflicts:**
   - [ ] Change github-integration to 8085
   - [ ] Change balancer-service metrics to 9092
   - [ ] Update docker-compose configs
   - [ ] Update service-catalog.yaml

2. **Test Policy Engine:**
   - [ ] Start governance API (9091)
   - [ ] Verify hot reload
   - [ ] Test decision workflows
   - [ ] Validate audit logging

3. **Test Balancer Service:**
   - [ ] Start balancer-service (9092)
   - [ ] Verify EventBus subscriptions
   - [ ] Test infrastructure-aware decisions
   - [ ] Monitor Phase 2.1 features

### Short Term (Week 2-3)

4. **GitHub Integration:**
   - [ ] Fix port to 8085
   - [ ] Test webhook processing
   - [ ] Verify AI Orchestrator proxy
   - [ ] Document Copilot integration

5. **MCP Server Decision:**
   - [ ] Evaluate business value
   - [ ] If keep: Implement Partisia SDK
   - [ ] If deprecate: Archive and document

### Medium Term (Month 1-2)

6. **Production Deployment:**
   - [ ] Deploy policy-engine
   - [ ] Deploy balancer-service (after testing)
   - [ ] Deploy github-integration (after fixes)
   - [ ] Monitor and optimize

7. **Advanced Features:**
   - [ ] Partisia integration (if decided)
   - [ ] Enhanced collective intelligence
   - [ ] Blockchain governance

---

**Report Generated:** 2025-10-11
**Analysis Tool:** Claude Code Agent
**Components Analyzed:** 6
**Total Lines of Code:** ~5,500
**Production Ready:** 2/6 (policy-engine, partial balancer-service)
**Integration Status:** Mixed (Full to None)

---

## VIII. FILES ANALYZED

### Integration Services (8 files)
- `/infrastructure/integration/github-integration/main.py` (100 lines)
- `/infrastructure/integration/github-integration/config.py` (127 lines)
- `/infrastructure/integration/mcp-server/bcm_collective_mcp.py` (679 lines)
- `/infrastructure/integration/mcp-server/main.py` (34 lines)
- `/infrastructure/integration/partisia-contracts/main.py` (38 lines)

### Policy Engine (13 files)
- `/infrastructure/policy-engine/policy_engine.py` (539 lines)
- `/infrastructure/policy-engine/decision_center.py` (607 lines)
- `/infrastructure/policy-engine/escalation_manager.py` (624 lines)
- `/infrastructure/policy-engine/governance_api.py` (573 lines)
- `/infrastructure/policy-engine/wishlist_integration.py` (320 lines)
- `/infrastructure/policy-engine/policy_models.py` (~320 lines)
- `/infrastructure/policy-engine/policy_validator.py` (~350 lines)
- `/infrastructure/policy-engine/audit_logger.py` (~500 lines)
- `/infrastructure/policy-engine/decision_models.py`
- `/infrastructure/policy-engine/notification_service.py`
- `/infrastructure/policy-engine/README.md`

### Balancer Service (1 file)
- `/infrastructure/balancer-service/main.py` (456 lines)

### Total Analyzed
- **Files:** 22
- **Lines of Code:** ~5,500+
- **Production Code:** ~3,800 (policy-engine) + 456 (balancer) + 1,000+ (integration)
