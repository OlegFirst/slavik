# Policy Integration Architecture

**System:** Decision Center ↔ ai-foundation ↔ workflow_intelligence
**Date:** 2025-10-09

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                       DECISION CENTER                            │
│                  (Policy Governance Layer)                       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              policies.yaml (Source of Truth)              │  │
│  │  • ai_policies                                            │  │
│  │  • workflow_policies                                      │  │
│  │  • integration_policies                                   │  │
│  │  • decision_center_controls                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  PolicyEngine                             │  │
│  │  • Load & parse YAML                                      │  │
│  │  • Evaluate rules                                         │  │
│  │  • Handle overrides                                       │  │
│  │  • Audit logging                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         ▼                    ▼                    ▼             │
│  ┌──────────┐      ┌──────────────┐      ┌─────────────┐       │
│  │ Decision │      │   Recovery   │      │ Governance  │       │
│  │ Service  │      │   Service    │      │  Service    │       │
│  └──────────┘      └──────────────┘      └─────────────┘       │
│         │                  │                    │                │
└─────────┼──────────────────┼────────────────────┼───────────────┘
          │                  │                    │
          ▼                  ▼                    ▼
    ┌─────────┐       ┌──────────┐       ┌──────────┐
    │    AI   │       │ Workflow │       │ EventBus │
    │Foundation│      │Intelligence      │          │
    └─────────┘       └──────────┘       └──────────┘
```

---

## Data Flow: AI-Assisted Decision

```
┌──────────┐
│  User    │
│ Request  │
└────┬─────┘
     │
     ▼
┌────────────────────────────────────────────────────┐
│ DECISION CENTER                                     │
│                                                     │
│ 1. Check Policies                                  │
│    ├─ Budget: $45/$100 ✅                         │
│    ├─ Rate Limit: 12/50 req/min ✅                │
│    └─ Task Type: "strategic_analysis"             │
│                                                     │
│ 2. Consult ai-foundation                          │
│    ├─ RAG: Retrieve knowledge (ISO + Cases)       │
│    │   • min_results check: 5 ✅                  │
│    │   • source_priority check: ISO=1.0 ✅        │
│    └─ LLM: Generate recommendation                 │
│        • Model: claude-opus-4 (strategic)         │
│        • Cost: $0.15 → Budget: $45.15/$100        │
│                                                     │
│ 3. Validate Quality                                │
│    ├─ Confidence: 0.85 (>0.6 threshold) ✅        │
│    ├─ Sources: 5 ISO + BCI ✅                     │
│    └─ Decision: ACCEPT_AI_RECOMMENDATION           │
│                                                     │
│ 4. Audit Log                                       │
│    ├─ Query logged (90 day retention)             │
│    ├─ Cost tracked                                 │
│    └─ Recommendation stored                        │
└────┬───────────────────────────────────────────────┘
     │
     ▼
┌────────────┐
│  Response  │
│  to User   │
└────────────┘
```

---

## Data Flow: Recovery Workflow Trigger

```
┌──────────┐
│ Service  │
│ Failure  │
└────┬─────┘
     │
     ▼
┌────────────────────────────────────────────────────┐
│ DECISION CENTER                                     │
│                                                     │
│ 1. Detect Failure                                  │
│    ├─ EventBus: "database.connection.failed"      │
│    ├─ Severity: CRITICAL                           │
│    └─ Service: postgres_primary                    │
│                                                     │
│ 2. Check Recovery Policies                        │
│    ├─ recovery_workflows.database_failure          │
│    │   • workflow: DatabaseRecoverySaga            │
│    │   • timeout: 300s                             │
│    │   • priority: CRITICAL                        │
│    └─ Approval required? YES (CRITICAL severity)  │
│                                                     │
│ 3. Request Approval                                │
│    ├─ Approvers: [operations_lead, dba]           │
│    ├─ Timeout: 15 minutes                          │
│    └─ Response: APPROVED ✅                        │
│                                                     │
│ 4. Trigger workflow_intelligence                  │
│    ├─ Workflow: CoordinationWorkflow              │
│    ├─ Action: recover_database                     │
│    ├─ Params: {backup_timestamp, rollback_plan}   │
│    └─ Execution ID: recovery-db-20251009-001      │
│                                                     │
│ 5. Monitor Execution                               │
│    ├─ Poll status every 5s                         │
│    ├─ Progress: 40% → 80% → 100%                  │
│    └─ Result: COMPLETED ✅                         │
│                                                     │
│ 6. Audit Log                                       │
│    ├─ Failure logged                               │
│    ├─ Approval logged                              │
│    ├─ Workflow execution logged                    │
│    └─ Recovery success logged                      │
└────┬───────────────────────────────────────────────┘
     │
     ▼
┌────────────┐
│  Service   │
│ Recovered  │
└────────────┘
```

---

## Data Flow: Governance Validation

```
┌──────────┐
│ Workflow │
│  Action  │
└────┬─────┘
     │
     ▼
┌────────────────────────────────────────────────────┐
│ DECISION CENTER                                     │
│                                                     │
│ 1. Load Workflow Context                           │
│    ├─ workflow_id: bia-123                         │
│    ├─ current_stage: determine_rto                 │
│    ├─ action: suggest_rto                          │
│    └─ context: {processes, objectives, ...}        │
│                                                     │
│ 2. Get Governance Rules                            │
│    ├─ workflow_policies.bia_rules                  │
│    │   • Constitution: 3 rules                     │
│    │   • Mandatory: 4 rules                        │
│    │   • Best Practice: 3 rules                    │
│    └─ Applicable to: determine_rto stage           │
│                                                     │
│ 3. Validate via workflow_intelligence             │
│    ├─ RulesEngine.validate(context, stage)         │
│    └─ Results:                                      │
│        • bia_const_001: PASS ✅                    │
│        • bia_mand_004: FAIL ❌ (no rationale)     │
│        • bia_bp_003: WARN ⚠️ (RPO > RTO)         │
│                                                     │
│ 4. Determine Action                                │
│    ├─ CRITICAL violations: 0                       │
│    ├─ HIGH violations: 1 (bia_mand_004)           │
│    └─ Decision: ESCALATE_TO_HUMAN                  │
│                                                     │
│ 5. Escalate                                        │
│    ├─ Notify: workflow_owner, supervisor           │
│    ├─ Reason: "RTO rationale missing (30+ chars)" │
│    └─ Block transition until resolved              │
│                                                     │
│ 6. Audit Log                                       │
│    ├─ Validation logged                            │
│    ├─ Violation logged                             │
│    └─ Escalation logged                            │
└────┬───────────────────────────────────────────────┘
     │
     ▼
┌────────────┐
│  User      │
│ Notified   │
└────────────┘
```

---

## Component Interactions

```
┌─────────────────────────────────────────────────────────────┐
│                     DECISION CENTER                          │
│                                                              │
│  ┌────────────┐   ┌─────────────┐   ┌──────────────┐       │
│  │ Decision   │   │  Recovery   │   │  Governance  │       │
│  │ Service    │   │  Service    │   │   Service    │       │
│  └─────┬──────┘   └──────┬──────┘   └───────┬──────┘       │
│        │                 │                   │               │
└────────┼─────────────────┼───────────────────┼──────────────┘
         │                 │                   │
    ┌────▼────┐       ┌────▼────┐         ┌────▼────┐
    │   RAG   │       │Temporal │         │  Rules  │
    │Pipeline │       │ Client  │         │ Engine  │
    └────┬────┘       └────┬────┘         └────┬────┘
         │                 │                   │
┌────────▼─────────────────▼───────────────────▼──────────┐
│                  NETWORK BOUNDARY                        │
└──────────────────────────────────────────────────────────┘
         │                 │                   │
    ┌────▼────┐       ┌────▼────┐         ┌────▼────┐
    │   AI    │       │ Temporal│         │Workflow │
    │Foundation│      │ Server  │         │ Engine  │
    │  (HTTP) │       │  (gRPC) │         │ (HTTP)  │
    └─────────┘       └─────────┘         └─────────┘
```

---

## Policy Hierarchy

```
┌──────────────────────────────────────────────────────┐
│         DECISION CENTER POLICY HIERARCHY              │
└──────────────────────────────────────────────────────┘

Level 1: CONSTITUTION (Immutable)
├─ ai_policies.llm_selection.fallback_chain
├─ workflow_policies.bia_rules.constitution_rules
└─ Action: BLOCK on violation

Level 2: MANDATORY (Required)
├─ ai_policies.rag_quality.retrieval_thresholds
├─ workflow_policies.bia_rules.mandatory_rules
├─ workflow_policies.temporal_workflows.approval_requirements
└─ Action: ESCALATE on violation

Level 3: BEST PRACTICE (Recommended)
├─ ai_policies.cost_controls.auto_downgrade
├─ workflow_policies.bia_rules.best_practice_rules
└─ Action: WARN on violation

Level 4: COMPLIANCE (Regulatory)
├─ ai_policies.ai_audit.retention_policies
├─ workflow_policies.event_governance.audit_trail
└─ Action: AUDIT_AND_ESCALATE on violation

Level 5: OVERRIDES (Emergency)
├─ decision_center_controls.override_policies
├─ Requires: Approval + Expiry (24h)
└─ Action: ALLOW_WITH_AUDIT
```

---

## Integration Patterns

### Pattern 1: Policy-Driven AI Call

```python
# Decision Center checks policies BEFORE calling AI

async def make_ai_decision(query, context):
    # 1. Check budget policy
    if not policy_engine.check("ai_policies.cost_controls"):
        return {"error": "Budget exceeded"}

    # 2. Classify task for LLM routing
    task_type = policy_engine.classify_task(query)

    # 3. Call ai-foundation with policy constraints
    result = await ai_foundation.query(
        query=query,
        task_type=task_type,  # Enforces LLM selection policy
        max_cost=policy_engine.get("ai_policies.cost_controls.per_request_limit")
    )

    # 4. Validate quality per policy
    if result.confidence < policy_engine.get("ai_policies.rag_quality.min_confidence"):
        return {"action": "request_human_review"}

    return result
```

### Pattern 2: Temporal Workflow with Governance

```python
# Decision Center validates BEFORE triggering workflow

async def trigger_recovery(failure_type, params):
    # 1. Check governance rules
    is_valid, violations = governance_service.validate(
        context=params,
        rules=policy_engine.get("workflow_policies.recovery_workflows")
    )

    if not is_valid:
        if any(v.severity == "CRITICAL" for v in violations):
            return {"action": "BLOCK", "violations": violations}

    # 2. Check if approval required
    if policy_engine.requires_approval(failure_type):
        approval = await request_approval(params)
        if not approval["approved"]:
            return {"action": "REJECTED"}

    # 3. Trigger Temporal workflow
    result = await temporal_client.execute_workflow(
        RecoveryWorkflow.run,
        params,
        timeout=policy_engine.get("workflow_policies.temporal_workflows.timeout")
    )

    return result
```

### Pattern 3: Event-Driven Policy Enforcement

```python
# Decision Center subscribes to events and enforces policies

async def handle_workflow_event(event):
    if event.type == "workflow.failed":
        # 1. Get recovery policy
        recovery_policy = policy_engine.get(
            f"workflow_policies.recovery_workflows.{event.service}_failure"
        )

        # 2. Check if auto-recovery allowed
        if recovery_policy["auto_recover"]:
            await trigger_recovery(event.service, event.data)
        else:
            # Escalate per policy
            await escalate(event, recovery_policy["escalate_to"])

    elif event.type == "ai.cost.threshold_exceeded":
        # 1. Get cost control policy
        cost_policy = policy_engine.get("ai_policies.cost_controls")

        # 2. Take action per policy
        if event.cost > cost_policy["hard_limit"]:
            await block_all_ai_calls()
        elif event.cost > cost_policy["alert_threshold"]:
            await notify_admin()
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│               Kubernetes Cluster                     │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │  decision-center (Deployment)              │    │
│  │  • Replicas: 3                             │    │
│  │  • Port: 8010                              │    │
│  │  • ConfigMap: policies.yaml                │    │
│  │  • Secrets: API keys                       │    │
│  └────┬───────────────────────────────────────┘    │
│       │                                              │
│       ├─→ ai-foundation (Service)                   │
│       │   • Host: ai-foundation.svc:8000            │
│       │   • Auth: Bearer token                      │
│       │                                              │
│       ├─→ workflow-intelligence (Service)           │
│       │   • Host: workflow-intelligence.svc:8001    │
│       │   • Auth: Bearer token                      │
│       │                                              │
│       └─→ Temporal Server (External)                │
│           • Host: temporal.example.com:7233         │
│           • Auth: mTLS                               │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │  EventBus (RabbitMQ)                       │    │
│  │  • Exchanges: workflow_events, ai_events   │    │
│  │  • Queues: decision_center_queue           │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │  PostgreSQL (Database)                     │    │
│  │  • Schema: decision_center                 │    │
│  │  • Tables: policies, audit_log, overrides  │    │
│  └────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

---

## Monitoring & Observability

```
┌─────────────────────────────────────────────────────┐
│              DECISION CENTER METRICS                 │
└─────────────────────────────────────────────────────┘

Policy Enforcement Metrics:
├─ policy_evaluations_total (counter)
├─ policy_violations_total (counter by severity)
├─ policy_overrides_total (counter)
└─ policy_evaluation_duration_seconds (histogram)

AI Integration Metrics:
├─ ai_calls_total (counter by task_type)
├─ ai_cost_daily_total (gauge)
├─ ai_budget_utilization_percent (gauge)
├─ rag_quality_score (histogram)
└─ llm_latency_seconds (histogram)

Workflow Integration Metrics:
├─ temporal_workflows_triggered_total (counter)
├─ workflow_failures_total (counter by type)
├─ recovery_workflows_success_rate (gauge)
├─ governance_validations_total (counter)
└─ escalations_total (counter by reason)

System Health Metrics:
├─ decision_center_up (gauge)
├─ ai_foundation_reachable (gauge)
├─ workflow_intelligence_reachable (gauge)
└─ temporal_server_reachable (gauge)

Alert Rules:
├─ AIBudgetExceeded: ai_cost_daily_total > 100
├─ PolicyViolationSpike: rate(policy_violations_total[5m]) > 10
├─ WorkflowFailureRate: workflow_failures_total / workflows_triggered > 0.1
└─ ServiceUnreachable: *_reachable == 0 for > 1m
```

---

## Security Model

```
┌─────────────────────────────────────────────────────┐
│          DECISION CENTER SECURITY LAYERS             │
└─────────────────────────────────────────────────────┘

Layer 1: Authentication
├─ API Gateway: JWT validation
├─ Service-to-Service: mTLS
└─ Temporal: gRPC mTLS + namespace isolation

Layer 2: Authorization (RBAC)
├─ Roles: [admin, operator, auditor, user]
├─ Permissions:
│   • admin: [read, write, delete, override]
│   • operator: [read, write, execute]
│   • auditor: [read, export]
│   • user: [read]
└─ Policy enforcement: Before every action

Layer 3: Data Security
├─ Encryption at rest: AES-256 (database)
├─ Encryption in transit: TLS 1.3
├─ PII handling: Anonymization before logging
└─ Secret management: Kubernetes Secrets + Vault

Layer 4: Audit Trail
├─ All actions logged (immutable)
├─ Retention: 365 days (compliance)
├─ Export: SIEM integration
└─ Tamper detection: Cryptographic hashing

Layer 5: Network Security
├─ Network policies: Deny-by-default
├─ Egress control: Whitelist destinations
├─ Rate limiting: Per tenant/user
└─ DDoS protection: API Gateway
```

---

## Files & Documentation

**Architecture Documentation:**
- This file: `/infrastructure/decision-center/INTEGRATION_ARCHITECTURE.md`

**Policy Documentation:**
- Full guide: `/infrastructure/decision-center/POLICY_INTEGRATION_FROM_AI_CORE.md`
- Summary: `/infrastructure/decision-center/POLICY_EXTRACTION_SUMMARY.md`
- Quick ref: `/infrastructure/decision-center/QUICK_POLICY_REFERENCE.md`

**Source Systems:**
- ai-foundation: `/intelligent-core/ai-foundation/`
- workflow_intelligence: `/intelligent-core/workflow_intelligence/`

**Policy Configuration:**
- policies.yaml: `/infrastructure/decision-center/policies.yaml`

---

**This architecture enables Decision Center to be the governance layer that coordinates AI intelligence (ai-foundation) with workflow orchestration (workflow_intelligence) through policy-driven decision making.**
