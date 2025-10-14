# Component Quick Reference
**Generated:** 2025-10-11
**Quick lookup for components analyzed**

---

## INTEGRATION SERVICES

### 1. GitHub Integration (8001 → 8085)
- **Path:** `/infrastructure/integration/github-integration`
- **Type:** Service
- **Port:** 8001 ⚠️ CONFLICT → Change to 8085
- **Status:** Stopped
- **Purpose:** GitHub webhooks, Copilot proxy to AI Orchestrator
- **Main:** `main.py` (100 lines)
- **Config:** `config.py` (127 lines)
- **Integration:** EventBus (Redis), PostgreSQL, AI Orchestrator
- **Action Required:** Fix port conflict

### 2. MCP Server - BCM Collective (stdio)
- **Path:** `/infrastructure/integration/mcp-server`
- **Type:** Protocol server
- **Port:** stdio (MCP protocol)
- **Status:** Experimental
- **Purpose:** Privacy-preserving collective intelligence, Partisia Blockchain
- **Main:** `bcm_collective_mcp.py` (679 lines)
- **Features:**
  - 7 resources (patterns, benchmarks, best-practices)
  - 3 tools (query_collective_wisdom, get_anonymous_benchmark, verify)
  - 3 prompts (ask_collective, compare_with_peers, stuck_on_bcm)
- **Integration:** Claude Desktop (MCP), Partisia (placeholder)
- **Action Required:** Implement Partisia SDK or deprecate

### 3. MCP Server - HTTP (8064)
- **Path:** `/infrastructure/integration/mcp-server`
- **Type:** Service
- **Port:** 8064
- **Status:** Skeleton
- **Purpose:** HTTP wrapper for MCP v1 API
- **Main:** `main.py` (34 lines)
- **Integration:** None (placeholder)
- **Action Required:** Complete implementation or deprecate

### 4. Partisia Contracts (8065)
- **Path:** `/infrastructure/integration/partisia-contracts`
- **Type:** Service
- **Port:** 8065
- **Status:** Skeleton
- **Purpose:** Blockchain smart contract integration
- **Main:** `main.py` (38 lines)
- **Integration:** None (placeholder)
- **Action Required:** Implement blockchain or deprecate

---

## POLICY ENGINE (Governance Layer)

### 5. Policy Engine ✅ PRODUCTION READY
- **Path:** `/infrastructure/policy-engine`
- **Type:** Library + REST API
- **Port:** 9091 (Governance API), N/A (library)
- **Status:** Production Ready
- **Version:** 1.1.0
- **Purpose:** Central governance, YAML policies, decision authority

#### Core Components (6 files, ~3,800 lines)

**PolicyEngine** (`policy_engine.py` - 539 lines):
- YAML policy management
- Hot reload
- Threshold queries
- Compliance checking

**InfrastructureDecisionCenter** (`decision_center.py` - 607 lines):
- Recovery decisions
- Optimization decisions
- Escalation management
- Approval workflows

**EscalationManager** (`escalation_manager.py` - 624 lines):
- Escalation triggers (max attempts, timeout, pattern detection)
- Operator notifications
- Incident tickets
- Auto-recovery control

**Governance API** (`governance_api.py` - 573 lines):
- REST API (13 endpoints)
- Decision management
- Escalation management
- Policy reload
- Audit trail

**Wishlist Integration** (`wishlist_integration.py` - 320 lines):
- Phase 2: Postpone decisions
- Background executor
- Resource-aware prioritization

**Additional:**
- `policy_models.py` (~320 lines) - Pydantic models
- `policy_validator.py` (~350 lines) - Validation
- `audit_logger.py` (~500 lines) - ISO 22301 audit

#### Key Features
- ✅ Hot reload without restart
- ✅ Type-safe (Pydantic)
- ✅ ISO 22301 compliant
- ✅ Full audit trail
- ✅ EventBus integration
- ✅ Approval workflows

#### Integration
- ✅ YAML policies
- ✅ EventBus (Redis)
- ✅ AI Orchestrator
- ⚠️ PostgreSQL (optional audit)
- ✅ Notification Service

---

## BALANCER SERVICE

### 6. Balancer Service (9091 → 9092)
- **Path:** `/infrastructure/balancer-service`
- **Type:** Service
- **Port:** 9091 ⚠️ CONFLICT → Change to 9092
- **Status:** Stopped (MVP)
- **Version:** 2.4.0
- **Purpose:** Global brain, 3D balancing, infrastructure-aware decisions

#### Architecture
```
SystemBalancer (GLOBAL BRAIN)
    ├── ImpactEvidenceTracker (RATIONAL)
    ├── PredictiveROIOptimizer (INTUITIVE + PRAGMATIC)
    └── ThreeDimensionalBalancer (3D BALANCE)
```

#### Event Subscriptions (7)
- `platform.bcm.imbalance_detected` - Survival Instinct
- `platform.resources.snapshot` - Resource Tracker
- `platform.resources.deficit` - Resource Tracker
- `platform.infrastructure.state_updated` - AI Event Manager (NEW)
- `platform.infrastructure.emergency` - AI Event Manager (NEW)
- `platform.infrastructure.strategy_recommended` - AI Event Manager (NEW)
- `platform.infrastructure.wishlist_updated` - Wishlist System (Phase 2)

#### Infrastructure Awareness (Phase 2.1 - NEW)
- CPU usage monitoring (conservative if > 85%)
- Database availability checks
- Monitoring coverage validation
- Emergency mode switching
- Strategic alignment with AI Event Manager

#### Integration
- ✅ EventBus (Redis Streams)
- ✅ intelligent-core/balancer
- ✅ AI Event Manager (Phase 2.1)
- ✅ Prometheus metrics

#### Action Required
- Fix port to 9092
- Testing phase
- Monitor performance

---

## PORT MAP

| Port | Component | Status | Action |
|------|-----------|--------|--------|
| 8001 | github-integration | Stopped | → Change to 8085 |
| 8064 | mcp-server (HTTP) | Stopped | ✅ OK |
| 8065 | partisia-contracts | Stopped | ✅ OK |
| 9091 | policy-engine (API) | Stopped | ✅ OK |
| 9091 | balancer-service (metrics) | Stopped | → Change to 9092 |
| stdio | mcp-server (protocol) | Protocol | ✅ OK |

---

## STATUS SUMMARY

### Production Ready ✅
- **policy-engine** (v1.1.0)
  - Library + REST API
  - ISO 22301 compliant
  - Hot reload supported
  - 3,800 lines of production code

### Testing Phase ⚠️
- **balancer-service** (v2.4.0 MVP)
  - Phase 2.1 complete
  - Infrastructure-aware
  - Event-driven integration
  - Needs port fix (9092)

### Needs Fixes ❌
- **github-integration**
  - Port conflict (8001 → 8085)
  - Test AI Orchestrator proxy
  - Verify EventBus integration

### Experimental/Deprecation Candidates 🔬
- **mcp-server (BCM Collective)**
  - Advanced concept
  - Partisia placeholder
  - Implement SDK or deprecate

- **mcp-server (HTTP)**
  - Basic skeleton
  - AI model not connected
  - Complete or deprecate

- **partisia-contracts**
  - No blockchain connection
  - Future feature
  - Low priority

---

## INTEGRATION PATTERNS

### Policy Engine Usage
```python
from infrastructure.policy_engine import initialize_policy_engine

engine = initialize_policy_engine("policies.yaml")
policy = engine.get_recovery_policy("database")
compliance = engine.check_compliance("restart", "api_gateway")
```

### Balancer Service Events
```python
# Publish to balancer
await eventbus.publish(Event.create(
    event_type='platform.bcm.imbalance_detected',
    data={'service': 'api', 'health_score': 45.0},
    source='survival_instinct'
))
```

### GitHub Integration Proxy
```python
# GitHub Copilot → GitHub Integration → AI Orchestrator
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://ai_orchestrator:8000/claude/analyze-changes",
        json=body
    )
```

---

## NEXT ACTIONS

### Immediate (Week 1)
- [ ] Fix github-integration port (8001 → 8085)
- [ ] Fix balancer-service port (9091 → 9092)
- [ ] Update docker-compose configs
- [ ] Update service-catalog.yaml

### Short Term (Week 2-3)
- [ ] Test policy-engine API
- [ ] Test balancer-service Phase 2.1
- [ ] Verify github-integration proxy
- [ ] Decide on MCP/Partisia fate

### Medium Term (Month 1-2)
- [ ] Deploy policy-engine
- [ ] Deploy balancer-service
- [ ] Deploy github-integration
- [ ] Monitor and optimize

---

**Full Analysis:** See `DETAILED_COMPONENT_ANALYSIS.md`
**Last Updated:** 2025-10-11
