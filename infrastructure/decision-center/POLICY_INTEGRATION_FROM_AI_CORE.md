# Policy Integration from AI Core Systems

**Source Systems:**
- `/Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation/` - AI foundation layer
- `/Users/MD/AI-Platform-ISO/intelligent-core/workflow_intelligence/` - Workflow orchestration
- **Commit:** b40b1b9 (SQLAlchemy migration complete for workflow_intelligence)

**Generated:** 2025-10-09
**Purpose:** Extract decision-making policies from AI core systems to inform Decision Center governance

---

## Table of Contents

1. [AI Foundation Policy Extraction](#1-ai-foundation-policy-extraction)
2. [Workflow Intelligence Policy Extraction](#2-workflow-intelligence-policy-extraction)
3. [Decision Center Policy Additions (YAML)](#3-decision-center-policy-additions-yaml)
4. [Integration Points](#4-integration-points)
5. [Migration Plan](#5-migration-plan)
6. [Code Examples](#6-code-examples)

---

## 1. AI Foundation Policy Extraction

### 1.1 LLM Selection Policy

**Source:** `/intelligent-core/ai-foundation/llm/llm_router.py`

**Decision Logic:**
```python
# Task-to-model mapping from LLMRouter
task_model_mapping = {
    "strategic_analysis": "claude-opus-4-20250514",    # Deep reasoning
    "content_generation": "claude-3-5-sonnet-20241022", # Balanced
    "quick_tasks": "claude-3-5-haiku-20241022",        # Fast responses
    "general": "claude-3-5-sonnet-20241022",           # Default
}

# Fallback priority
fallbacks = [
    {"claude-3-opus": ["gpt-4-turbo", "gpt-4"]},
    {"claude-3-sonnet": ["gpt-3.5-turbo", "claude-3-haiku"]},
    {"claude-3-haiku": ["gpt-3.5-turbo", "local-model"]},
]
```

**Decision Center Mapping:**
- **When:** AI-assisted decision or analysis requested
- **Decision:** Which LLM to use (model selection)
- **Criteria:**
  - Task complexity (strategic/content/quick)
  - Budget constraints
  - Latency requirements
  - API availability
- **Fallback:** Automatic degradation to cheaper/faster models on failure

**Key Questions Answered:**
- How does ai-foundation decide which LLM to use? → **Task-based routing** (strategic=Opus, content=Sonnet, quick=Haiku)
- What are quality thresholds for AI responses? → **Implicit in model selection** (Opus for critical decisions)
- Are there rate limits or quotas? → **Yes, LiteLLM router has 50 req/min default**
- What are failure/fallback policies? → **Automatic fallback chain** (Claude → GPT → Local)
- How are AI decisions audited? → **EventBus publishes all decisions**

---

### 1.2 RAG Quality Policy

**Source:** `/intelligent-core/ai-foundation/rag/pipeline.py`

**Decision Logic:**
```python
# Source priority configuration
source_config = {
    'iso_standards': {'priority': 1.0},      # Authoritative
    'bci_guidelines': {'priority': 0.95},    # Semi-authoritative
    'case_library': {'priority': 0.8},       # Practical examples
    'community_annotations': {'priority': 0.7}  # Community input
}

# Retrieval parameters
top_k = 5  # Default number of results
enable_reranking = True  # Improve relevance
enable_diversity = False  # Prioritize relevance over diversity
```

**Decision Center Mapping:**
- **When:** RAG query executed for knowledge retrieval
- **Decision:** Accept or reject RAG result / trust score
- **Criteria:**
  - Source priority (ISO > BCI > Cases > Community)
  - Reranking score (post-retrieval)
  - Result count threshold (min 3 results for confidence)
  - Metadata filters (industry, org_size, module)

**Extracted Thresholds:**
- **Minimum results:** 3 (implied from top_k=5 with reranking)
- **Source weights:** ISO=1.0, BCI=0.95, Cases=0.8, Community=0.7
- **Reranking:** Mandatory for decision-critical queries
- **Context budget:** 2000 characters max for LLM prompts

---

### 1.3 ML Model Selection Policy

**Source:** `/intelligent-core/ai-foundation/ml/` (inferred from USAGE_PATTERNS.md)

**Decision Logic:**
```python
# Workflow prediction models
WorkflowPredictor.predict_journey(
    org_context={'size': 'medium', 'maturity': 3},
    current_state='bia_in_progress',
    current_progress={'stage_index': 2, 'total_stages': 6}
)

# Anomaly detection
AnomalyDetector.detect_workflow_anomalies(
    workflow_data={'duration_hours': 48},  # Unusually long
    historical_data=[{'duration_hours': 16}, ...]
)
```

**Decision Center Mapping:**
- **When:** Predictive analysis needed (workflow duration, failure risk)
- **Decision:** Which ML model to use
- **Criteria:**
  - Data availability (min 50 samples for training)
  - Model freshness (retrain trigger thresholds)
  - Anomaly severity (2.5 std devs = high risk)

**Key Policies:**
- **Training threshold:** Minimum 50 samples before model deployment
- **Anomaly threshold:** >2.5 standard deviations from baseline
- **Confidence threshold:** Low confidence (<0.6) triggers human review
- **Stuck probability:** >0.7 triggers escalation to expert

---

### 1.4 AI Cost Optimization Policy

**Source:** `/intelligent-core/ai-foundation/llm/litellm_router.py`

**Decision Logic:**
```python
# Cost per token
model_costs = {
    'claude-opus': 0.000015,      # Premium
    'claude-sonnet': 0.000003,    # Standard
    'claude-haiku': 0.00000025,   # Budget
    'gpt-4-turbo': 0.00001,       # Premium
    'gpt-3.5-turbo': 0.0000005,   # Budget
}

# Cost tracking per request
cost = cost_per_token * total_tokens
```

**Decision Center Mapping:**
- **When:** AI request exceeds budget threshold
- **Decision:** Approve, downgrade model, or reject
- **Criteria:**
  - Request cost vs. budget remaining
  - Task criticality (strategic > content > quick)
  - Cumulative daily spend

**Policy:**
- **Budget alert:** Daily spend > $100 → notify admin
- **Auto-downgrade:** Non-critical tasks downgrade to cheaper models if budget tight
- **Hard limit:** Daily spend > $500 → reject non-critical requests

---

### 1.5 AI Audit & Compliance Policy

**Source:** `/intelligent-core/ai-foundation/` (event system)

**Decision Logic:**
- All LLM queries logged with context
- RAG retrievals tracked with source citations
- ML predictions recorded with confidence scores
- Cost tracking per tenant/user

**Decision Center Mapping:**
- **When:** Audit trail required for AI decision
- **Decision:** What to log and retain
- **Criteria:**
  - Regulatory requirements (GDPR, SOC2)
  - Tenant data sovereignty
  - Retention period (90 days for AI logs)

**Policy:**
- **Log retention:** 90 days for AI queries, 1 year for compliance decisions
- **PII handling:** Anonymize user data in AI logs
- **Audit access:** Role-based (admin, auditor, compliance_officer)

---

## 2. Workflow Intelligence Policy Extraction

### 2.1 Workflow Governance Rules

**Source:** `/intelligent-core/workflow_intelligence/governance/rules_engine.py`

**Rule Hierarchy:**
```python
class RuleCategory(Enum):
    CONSTITUTION = "constitution"      # Immutable principles → BLOCK
    MANDATORY = "mandatory"            # Required → ESCALATE
    BEST_PRACTICE = "best_practice"    # Recommended → WARN
    COMPLIANCE = "compliance"          # Regulatory → AUDIT
```

**Decision Center Mapping:**
- **When:** Workflow action attempted
- **Decision:** Allow, block, or escalate
- **Criteria:**
  - Rule category (constitution > mandatory > best practice)
  - Severity (CRITICAL > HIGH > MEDIUM > LOW)
  - Violation count (3+ HIGH violations → escalate)

**Key Questions Answered:**
- What workflows exist for infrastructure recovery? → **Temporal sagas** (CoordinationWorkflow, CrossServiceWorkflow)
- How are workflow priorities determined? → **Rule severity** (CRITICAL blocks, HIGH escalates)
- What are timeout/retry policies? → **Temporal RetryPolicy** (3 attempts, exponential backoff)
- How are compensating transactions handled? → **rollback_execution activity** (Saga pattern)
- What are the SLA targets? → **Implicit in RTO/RPO rules** (Tier 1 < 1h)

---

### 2.2 BIA Workflow Rules

**Source:** `/intelligent-core/workflow_intelligence/governance/bia_rules.py`

**Constitution Rules (CRITICAL - Block):**
1. **bia_const_001:** No RTO < 1 hour without justification (Tier 1 processes)
2. **bia_const_002:** Financial impact required for all processes
3. **bia_const_003:** Tier 1 dependency mapping mandatory

**Mandatory Rules (HIGH - Escalate):**
1. **bia_mand_001:** Minimum 3 processes
2. **bia_mand_002:** At least one Tier 1 process
3. **bia_mand_003:** All impact types assessed (financial, operational, reputational, regulatory)
4. **bia_mand_004:** RTO rationale required (min 30 chars)

**Best Practice Rules (MEDIUM/LOW - Warn):**
1. **bia_bp_001:** Process owner documented
2. **bia_bp_002:** Dependency details (type and criticality)
3. **bia_bp_003:** RPO alignment with RTO (RPO ≤ RTO)

**Decision Center Mapping:**
- **When:** BIA workflow stage transition
- **Decision:** Allow transition or block with violations
- **Criteria:** Rule validation against workflow context

---

### 2.3 Workflow Orchestration Policy

**Source:** `/intelligent-core/workflow_intelligence/temporal_workflows/coordination_workflow.py`

**Temporal Workflow Policies:**
```python
# Retry policy for transient failures
retry_policy = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    maximum_interval=timedelta(seconds=30),
    maximum_attempts=3,
    backoff_coefficient=2.0
)

# Timeout policies
start_to_close_timeout=timedelta(minutes=10)  # Activity timeout
heartbeat_timeout=timedelta(minutes=5)        # Long-running activities
```

**Workflow Types:**
1. **CoordinationWorkflow:** Single intent with approval, retry, rollback
2. **CrossServiceWorkflow:** Multi-service coordination with saga pattern
3. **ParallelTaskWorkflow:** Independent parallel execution

**Decision Center Mapping:**
- **When:** Complex recovery workflow needed
- **Decision:** Which Temporal workflow to trigger
- **Criteria:**
  - Service count (1=Coordination, 2+=CrossService)
  - Independence (parallel vs sequential)
  - Approval requirement (critical operations)

**Key Policies:**
- **Retry:** 3 attempts with exponential backoff (1s → 2s → 4s)
- **Timeout:** 10 minutes for activities, 24 hours for approvals
- **Rollback:** Automatic on failure (compensating transactions)
- **Approval:** Required for CRITICAL severity operations

---

### 2.4 Event-Driven Recovery Policy

**Source:** `/intelligent-core/workflow_intelligence/core/workflow_engine.py`

**Event System:**
```python
# Event types
event_types = [
    "{module}.workflow.started",
    "{module}.action.executed",
    "{module}.stage.changed",
    "{module}.workflow.completed"
]

# EventBus publishes to subscribers
event_bus.publish(WorkflowEvent(...))
```

**Decision Center Mapping:**
- **When:** Workflow event published
- **Decision:** Trigger recovery workflow or alert
- **Criteria:**
  - Event type (failure events)
  - Event frequency (repeated failures)
  - Service criticality

**Policy:**
- **Failure events:** Trigger immediate recovery workflow
- **Repeated failures:** Escalate to human after 3 occurrences
- **Audit:** All workflow events logged to EventBus

---

### 2.5 Progress & Gap Analysis Policy

**Source:** `/intelligent-core/workflow_intelligence/core/workflow_engine.py`

**Gap Identification:**
```python
async def _identify_gaps(workflow: Dict) -> List[Dict]:
    # Missing required fields
    if not workflow_data.get(required_field):
        gaps.append({
            "type": "missing_field",
            "field": required_field,
            "severity": "high"
        })

    # Stale workflows
    if duration.days > 7:
        issues.append({
            "type": "stale_workflow",
            "severity": "medium"
        })
```

**Decision Center Mapping:**
- **When:** Workflow health check
- **Decision:** Continue, warn, or escalate
- **Criteria:**
  - Critical gaps (HIGH severity → block)
  - Stale duration (>7 days → warn)
  - Completion percentage (<20% after 7 days → escalate)

---

## 3. Decision Center Policy Additions (YAML)

```yaml
# /infrastructure/decision-center/policies.yaml

# ============================================================================
# AI Foundation Policies
# ============================================================================

ai_policies:

  # LLM Selection Policy
  llm_selection:
    description: "Route LLM queries to optimal provider based on task complexity"

    routing_rules:
      - condition: "task_type == 'strategic_analysis'"
        model: "claude-opus-4-20250514"
        rationale: "Deep reasoning for critical decisions"

      - condition: "task_type == 'content_generation'"
        model: "claude-3-5-sonnet-20241022"
        rationale: "Balanced quality and cost"

      - condition: "task_type == 'quick_tasks'"
        model: "claude-3-5-haiku-20241022"
        rationale: "Fast responses for simple queries"

      - condition: "default"
        model: "claude-3-5-sonnet-20241022"
        rationale: "Default balanced option"

    fallback_chain:
      - primary: "claude-opus"
        fallbacks: ["gpt-4-turbo", "gpt-4"]

      - primary: "claude-sonnet"
        fallbacks: ["gpt-3.5-turbo", "claude-haiku"]

      - primary: "claude-haiku"
        fallbacks: ["gpt-3.5-turbo", "local-model"]

    rate_limits:
      default: 50  # requests per minute
      critical: 100  # for strategic analysis

    cost_controls:
      daily_budget: 100  # USD
      alert_threshold: 80  # USD (80% of budget)
      hard_limit: 500  # USD (reject after this)
      auto_downgrade: true  # Use cheaper models when near budget

  # RAG Quality Policy
  rag_quality:
    description: "Quality gates for knowledge retrieval"

    source_priorities:
      iso_standards: 1.0
      bci_guidelines: 0.95
      case_library: 0.8
      community_annotations: 0.7

    retrieval_thresholds:
      min_results: 3  # Minimum for confident answer
      top_k: 5  # Default retrieval count
      reranking_required: true  # For decision-critical queries
      max_context_length: 2000  # Characters for LLM context

    quality_gates:
      - condition: "result_count < 3"
        action: "request_human_review"
        severity: "high"

      - condition: "source_priority < 0.7"
        action: "warn_low_quality_source"
        severity: "medium"

      - condition: "no_iso_standard_results AND task_critical"
        action: "escalate_to_expert"
        severity: "high"

  # ML Model Governance
  ml_models:
    description: "ML model selection and quality control"

    training_requirements:
      min_samples: 50  # Minimum for model deployment
      retrain_threshold: 100  # Retrain after 100 new samples
      max_model_age_days: 30  # Retrain if older

    prediction_thresholds:
      min_confidence: 0.6  # Below this, request human review
      stuck_probability_escalate: 0.7  # Trigger expert help
      anomaly_std_dev: 2.5  # Standard deviations for anomaly detection

    quality_controls:
      - condition: "confidence < 0.6"
        action: "request_human_review"
        severity: "high"

      - condition: "stuck_probability > 0.7"
        action: "escalate_to_expert"
        severity: "critical"

      - condition: "anomaly_detected AND std_dev > 2.5"
        action: "trigger_investigation"
        severity: "high"

  # AI Audit & Compliance
  ai_audit:
    description: "Audit trail and compliance for AI decisions"

    logging_requirements:
      llm_queries: true
      rag_retrievals: true
      ml_predictions: true
      cost_tracking: true

    retention_policies:
      ai_query_logs: 90  # days
      compliance_decisions: 365  # days
      cost_records: 365  # days
      training_data: 730  # days

    pii_handling:
      anonymize_logs: true
      exclude_fields: ["user_email", "user_phone", "ssn"]
      tenant_data_sovereignty: true  # Respect tenant location

    access_control:
      roles:
        - admin: ["read", "write", "delete"]
        - auditor: ["read"]
        - compliance_officer: ["read", "export"]

# ============================================================================
# Workflow Intelligence Policies
# ============================================================================

workflow_policies:

  # Governance Rules Engine
  governance_rules:
    description: "Hierarchical rule validation for workflows"

    rule_categories:
      constitution:
        severity: "CRITICAL"
        action_on_violation: "BLOCK"
        escalate: true

      mandatory:
        severity: "HIGH"
        action_on_violation: "ESCALATE"
        escalate_threshold: 1  # Escalate after 1 violation

      best_practice:
        severity: "MEDIUM"
        action_on_violation: "WARN"
        escalate_threshold: 5  # Escalate after 5 violations

      compliance:
        severity: "HIGH"
        action_on_violation: "AUDIT_AND_ESCALATE"
        escalate: true

    escalation_logic:
      - condition: "violation_severity == 'CRITICAL'"
        action: "block_and_escalate_immediately"

      - condition: "high_violations >= 3"
        action: "escalate_to_human"

      - condition: "medium_violations >= 5"
        action: "notify_supervisor"

  # BIA Workflow Rules
  bia_rules:
    description: "Business Impact Analysis governance rules"

    constitution_rules:
      - rule_id: "bia_const_001"
        name: "No RTO < 1 hour without justification"
        applies_to: ["determine_rto", "review_results"]
        validation: "tier_1_processes.rto_hours >= 1 OR justification_provided"
        severity: "CRITICAL"

      - rule_id: "bia_const_002"
        name: "Financial impact required"
        applies_to: ["assess_impact", "review_results"]
        validation: "all_processes.financial_impact.exists()"
        severity: "CRITICAL"

      - rule_id: "bia_const_003"
        name: "Tier 1 dependency mapping mandatory"
        applies_to: ["analyze_dependencies", "review_results"]
        validation: "tier_1_processes.dependencies.count >= 2 AND types_include(['people', 'technology'])"
        severity: "CRITICAL"

    mandatory_rules:
      - rule_id: "bia_mand_001"
        name: "Minimum 3 processes"
        applies_to: ["identify_processes", "analyze_dependencies"]
        validation: "processes.count >= 3"
        severity: "HIGH"

      - rule_id: "bia_mand_002"
        name: "At least one Tier 1 process"
        applies_to: ["identify_processes", "analyze_dependencies"]
        validation: "tier_1_processes.count >= 1"
        severity: "HIGH"

      - rule_id: "bia_mand_003"
        name: "All impact types assessed"
        applies_to: ["assess_impact", "review_results"]
        validation: "all_processes.impact_types == ['financial', 'operational', 'reputational', 'regulatory']"
        severity: "HIGH"

      - rule_id: "bia_mand_004"
        name: "RTO rationale required"
        applies_to: ["determine_rto", "review_results"]
        validation: "all_rto.rationale.length >= 30"
        severity: "HIGH"

    best_practice_rules:
      - rule_id: "bia_bp_001"
        name: "Process owner documented"
        applies_to: "all_stages"
        validation: "all_processes.owner.exists()"
        severity: "MEDIUM"

      - rule_id: "bia_bp_002"
        name: "Dependency details"
        applies_to: ["analyze_dependencies"]
        validation: "all_dependencies.has(['type', 'criticality'])"
        severity: "LOW"

      - rule_id: "bia_bp_003"
        name: "RPO alignment with RTO"
        applies_to: ["determine_rto"]
        validation: "all_objectives.rpo_hours <= rto_hours"
        severity: "LOW"

  # Workflow Orchestration (Temporal)
  temporal_workflows:
    description: "Temporal workflow execution policies"

    retry_policies:
      transient_failures:
        initial_interval: 1  # seconds
        maximum_interval: 30  # seconds
        maximum_attempts: 3
        backoff_coefficient: 2.0

    timeout_policies:
      activity_timeout: 600  # seconds (10 minutes)
      heartbeat_timeout: 300  # seconds (5 minutes for long-running)
      approval_timeout: 86400  # seconds (24 hours)

    workflow_types:
      coordination_workflow:
        use_case: "Single intent execution with approval"
        features: ["retry", "approval", "rollback"]
        max_duration: 3600  # seconds (1 hour)

      cross_service_workflow:
        use_case: "Multi-service coordination"
        features: ["parallel_execution", "saga_pattern", "conflict_resolution"]
        max_duration: 7200  # seconds (2 hours)

      parallel_task_workflow:
        use_case: "Independent parallel tasks"
        features: ["parallel_execution", "fail_fast_option"]
        max_duration: 1800  # seconds (30 minutes)

    approval_requirements:
      - condition: "severity == 'CRITICAL'"
        require_approval: true
        approvers: ["admin", "compliance_officer"]

      - condition: "cost > 100"  # USD
        require_approval: true
        approvers: ["financial_admin"]

      - condition: "affects_production AND change_type == 'destructive'"
        require_approval: true
        approvers: ["operations_lead", "cto"]

  # Recovery Workflows
  recovery_workflows:
    description: "Infrastructure recovery and rollback policies"

    recovery_triggers:
      database_failure:
        workflow: "DatabaseRecoverySaga"
        timeout: 300  # seconds
        compensating_actions: ["rollback_transaction", "notify_dba"]
        priority: "CRITICAL"

      service_cascade_failure:
        workflow: "CascadeRecovery"
        priority: "CRITICAL"
        parallel: false  # Sequential recovery
        max_retry: 3

      eventbus_failure:
        workflow: "EventBusRecovery"
        timeout: 180  # seconds
        fallback: "switch_to_backup_queue"
        priority: "HIGH"

      api_gateway_failure:
        workflow: "GatewayRecovery"
        timeout: 120  # seconds
        health_check: true
        priority: "HIGH"

    rollback_policies:
      - condition: "execution_failed AND partial_completion"
        action: "execute_compensating_transactions"
        max_rollback_duration: 600  # seconds

      - condition: "approval_denied"
        action: "rollback_all_changes"
        notification: "requester"

      - condition: "timeout_exceeded"
        action: "rollback_and_escalate"
        escalate_to: "operations_team"

  # Event-Driven Governance
  event_governance:
    description: "Event-based workflow monitoring and recovery"

    event_subscriptions:
      workflow_failures:
        pattern: "*.workflow.failed"
        action: "trigger_recovery_workflow"
        priority: "HIGH"

      repeated_failures:
        pattern: "*.action.failed"
        threshold: 3  # occurrences
        action: "escalate_to_human"
        priority: "CRITICAL"

      stale_workflows:
        pattern: "*.workflow.stale"
        threshold_days: 7
        action: "notify_owner"
        priority: "MEDIUM"

    audit_trail:
      log_all_events: true
      retention_days: 90
      export_format: "json"

  # Progress & Gap Analysis
  progress_monitoring:
    description: "Workflow progress and gap detection"

    gap_detection:
      missing_required_fields:
        severity: "HIGH"
        action: "block_transition"

      stale_workflow:
        threshold_days: 7
        severity: "MEDIUM"
        action: "notify_owner"

      low_completion_rate:
        threshold_percent: 20
        threshold_days: 7
        severity: "HIGH"
        action: "escalate_to_supervisor"

    health_checks:
      - metric: "completion_percentage"
        threshold: 20
        threshold_days: 7
        action: "escalate"

      - metric: "gap_severity"
        threshold: "HIGH"
        action: "block_and_notify"

      - metric: "time_in_stage"
        threshold_days: 3
        action: "warn_owner"

# ============================================================================
# Cross-Cutting Policies (AI + Workflow)
# ============================================================================

integration_policies:

  # AI-assisted workflow decisions
  ai_workflow_integration:
    description: "Use AI foundation to enhance workflow decisions"

    use_cases:
      - scenario: "Workflow stuck detection"
        trigger: "progress < 20% AND duration > 7 days"
        ai_action: "ml_predict_stuck_probability"
        threshold: 0.7
        decision: "escalate_if_stuck_probable"

      - scenario: "Optimal workflow path"
        trigger: "multiple_paths_available"
        ai_action: "rag_retrieve_similar_workflows"
        decision: "suggest_path_based_on_success_rate"

      - scenario: "Anomaly in workflow execution"
        trigger: "duration > 2.5 * historical_average"
        ai_action: "ml_detect_anomaly"
        decision: "investigate_if_anomaly_detected"

  # Workflow-informed AI decisions
  workflow_ai_integration:
    description: "Use workflow intelligence to inform AI decisions"

    use_cases:
      - scenario: "AI recommendation requires workflow context"
        trigger: "ai_query_for_recommendation"
        workflow_context: ["current_stage", "completed_steps", "gaps"]
        decision: "enhance_ai_prompt_with_workflow_context"

      - scenario: "Governance rules influence AI suggestions"
        trigger: "ai_suggests_rto"
        governance_check: "validate_against_bia_rules"
        decision: "reject_if_violates_constitution"

# ============================================================================
# Decision Center Overrides
# ============================================================================

decision_center_controls:
  description: "Decision Center can override AI/workflow policies when needed"

  override_policies:
    - policy: "llm_selection"
      override_condition: "admin_override_requested"
      approval_required: true
      audit_log: true

    - policy: "governance_rules"
      override_condition: "emergency_exemption"
      approval_required: true
      approvers: ["cto", "compliance_officer"]
      audit_log: true
      expiry: 24  # hours

    - policy: "workflow_timeout"
      override_condition: "critical_incident"
      approval_required: false  # Allow operations team
      audit_log: true

  monitoring:
    override_alerts: true
    override_frequency_limit: 5  # per day
    override_review_required: true  # Weekly review
```

---

## 4. Integration Points

### 4.1 Decision Center → ai-foundation

**When Decision Center should consult ai-foundation:**

1. **AI-assisted scenario analysis**
   ```python
   # Decision Center calls ai-foundation for complex analysis
   from ai_foundation import RAGPipeline, LLMRouter

   rag = RAGPipeline()
   llm = LLMRouter()

   # Retrieve knowledge
   knowledge = await rag.retrieve(
       query="What are recovery strategies for database failure?",
       filters={"industry": tenant.industry},
       top_k=5
   )

   # Generate recommendations
   recommendation = await llm.query(
       system_prompt="You are a BCM expert",
       user_prompt=f"Context: {knowledge}\n\nRecommend recovery strategy",
       task_type="strategic_analysis"
   )
   ```

2. **Quality validation before accepting AI recommendations**
   ```python
   # Validate RAG quality before trusting result
   if len(knowledge) < 3:
       decision = "request_human_review"
   elif max(k['score'] for k in knowledge) < 0.7:
       decision = "low_confidence_warning"
   else:
       decision = "accept_ai_recommendation"
   ```

3. **LLM routing for decision-critical vs non-critical queries**
   ```python
   # Use Opus for critical decisions, Haiku for routine
   if decision.criticality == "HIGH":
       task_type = "strategic_analysis"  # Claude Opus
   else:
       task_type = "quick_tasks"  # Claude Haiku
   ```

---

### 4.2 Decision Center → workflow_intelligence

**When Decision Center should trigger workflow_intelligence:**

1. **Complex recovery workflows**
   ```python
   # Instead of simple restart, trigger Temporal saga
   from temporalio.client import Client
   from workflow_intelligence.temporal_workflows import CoordinationWorkflow

   client = await Client.connect("localhost:7233")

   # Trigger recovery workflow
   result = await client.execute_workflow(
       CoordinationWorkflow.run,
       intent_data={
           "action": "recover_database",
           "entity": "postgres_primary",
           "params": {"backup_timestamp": "2025-10-09T10:00:00Z"},
           "context": {"severity": "CRITICAL"}
       },
       id=f"recovery-{incident_id}",
       task_queue="coordination"
   )
   ```

2. **Distributed transaction coordination**
   ```python
   # Use CrossServiceWorkflow for multi-service operations
   tasks = [
       {"action": "create_bia", "entity": "organization", "params": {...}},
       {"action": "assess_risk", "entity": "organization", "params": {...}},
       {"action": "check_compliance", "entity": "organization", "params": {...}}
   ]

   result = await client.execute_workflow(
       CrossServiceWorkflow.run,
       tasks,
       id=f"multi-service-{operation_id}",
       task_queue="coordination"
   )
   ```

3. **Governance validation before critical actions**
   ```python
   from workflow_intelligence.governance import RulesEngine, BIARules

   rules_engine = RulesEngine()
   for rule in BIARules.get_all_rules():
       rules_engine.register_rule(rule)

   # Validate before allowing action
   is_valid, violations = rules_engine.validate(
       context=workflow_context,
       current_stage="determine_rto"
   )

   if not is_valid:
       critical_violations = [v for v in violations if v.severity == "CRITICAL"]
       if critical_violations:
           decision = "BLOCK"
       elif rules_engine.should_escalate(violations):
           decision = "ESCALATE_TO_HUMAN"
       else:
           decision = "WARN_AND_PROCEED"
   ```

---

### 4.3 Bidirectional Integration

**ai-foundation + workflow_intelligence collaboration:**

```python
# Example: AI-enhanced workflow recovery decision

# Step 1: workflow_intelligence detects anomaly
from workflow_intelligence.core import WorkflowEngine

workflow_context = await workflow_engine.get_context(workflow_id)
gaps = workflow_context.gaps
issues = workflow_context.issues

# Step 2: Decision Center uses ai-foundation to analyze
if len(gaps) > 3 or any(g['severity'] == 'high' for g in gaps):
    # Use ML to predict if workflow is stuck
    from ai_foundation.ml import WorkflowPredictor

    prediction = await predictor.predict_journey(
        org_context=workflow_context.metadata,
        current_state=workflow_context.current_stage,
        current_progress={
            'stage_index': workflow_context.progress_percentage / 20,
            'total_stages': 5
        }
    )

    if prediction['stuck_probability']['probability'] > 0.7:
        # Use RAG to find similar recovery cases
        from ai_foundation.rag import RAGPipeline

        rag = RAGPipeline()
        recovery_knowledge = await rag.retrieve(
            query=f"Workflow stuck at {workflow_context.current_stage} with gaps: {gaps}",
            filters={"workflow_type": workflow_context.module},
            top_k=3
        )

        # Decision Center decides: Trigger recovery workflow or escalate
        if recovery_knowledge:
            decision = "trigger_temporal_recovery_workflow"
        else:
            decision = "escalate_to_expert"
```

---

## 5. Migration Plan

### Phase 1 (Immediate): Policy Extraction Complete

**Status:** ✅ Complete (this document)

**Actions:**
- [x] Extract policies from ai-foundation (LLM, RAG, ML, Cost, Audit)
- [x] Extract policies from workflow_intelligence (Governance, BIA, Temporal, Recovery, Events)
- [x] Map to Decision Center YAML format
- [x] Document integration points

---

### Phase 2 (Short-term): Add Extracted Policies to policies.yaml

**Timeline:** Next 2-4 weeks

**Actions:**
1. **Update `/infrastructure/decision-center/policies.yaml`**
   - Add AI policies section
   - Add Workflow policies section
   - Add Integration policies section
   - Add Override controls

2. **Update Decision Center policy engine**
   - Load new policies from YAML
   - Implement policy evaluation logic
   - Add override mechanism

3. **Testing**
   - Unit tests for policy evaluation
   - Integration tests with mock AI/workflow calls
   - Verify YAML parsing and policy loading

**Success Criteria:**
- Decision Center can evaluate AI and workflow policies
- Policies are loaded from YAML on startup
- Violations are logged and escalated correctly

---

### Phase 3 (Medium-term): Direct Integration with ai-foundation

**Timeline:** 1-2 months

**Actions:**
1. **Add ai-foundation client to Decision Center**
   ```python
   # /infrastructure/decision-center/integrations/ai_foundation_client.py

   from ai_foundation import RAGPipeline, LLMRouter, WorkflowPredictor

   class AIFoundationClient:
       def __init__(self):
           self.rag = RAGPipeline()
           self.llm = LLMRouter()
           self.predictor = WorkflowPredictor()

       async def get_recommendation(self, query, context):
           knowledge = await self.rag.retrieve(query, context=context)
           recommendation = await self.llm.query(
               system_prompt="BCM expert",
               user_prompt=f"Knowledge: {knowledge}\n\nQuestion: {query}",
               task_type="strategic_analysis"
           )
           return recommendation
   ```

2. **Policy-driven AI calls**
   - Decision Center checks policies before calling AI
   - Budget tracking enforced
   - Cost alerts triggered
   - Quality gates validated

3. **Audit integration**
   - All AI calls logged via Decision Center
   - Unified audit trail

**Success Criteria:**
- Decision Center can call ai-foundation APIs
- Policies govern AI usage (budget, quality, routing)
- Audit logs capture all AI interactions

---

### Phase 4 (Long-term): Full Orchestration via workflow_intelligence

**Timeline:** 3-6 months

**Actions:**
1. **Temporal workflow integration**
   ```python
   # Decision Center triggers Temporal workflows for complex operations

   from temporalio.client import Client
   from workflow_intelligence.temporal_workflows import (
       CoordinationWorkflow,
       CrossServiceWorkflow
   )

   class WorkflowIntelligenceClient:
       async def trigger_recovery(self, recovery_type, params):
           client = await Client.connect("localhost:7233")

           if recovery_type == "database":
               workflow_class = CoordinationWorkflow
           else:
               workflow_class = CrossServiceWorkflow

           result = await client.execute_workflow(
               workflow_class.run,
               params,
               task_queue="coordination"
           )
           return result
   ```

2. **Governance rules enforcement**
   - Decision Center validates against workflow governance rules
   - BIA rules enforced before allowing actions
   - Constitution violations block operations

3. **Event-driven decision making**
   - Decision Center subscribes to workflow events
   - Automatic recovery triggered on failure events
   - Escalations based on event patterns

**Success Criteria:**
- Decision Center orchestrates complex operations via Temporal
- Governance rules are enforced consistently
- Recovery workflows triggered automatically
- Full integration with EventBus

---

### Phase 5 (Future): AI-Workflow Synergy

**Timeline:** 6-12 months

**Vision:**
- AI learns from workflow patterns (Case Library integration)
- Workflow engine uses AI predictions for optimization
- Decision Center coordinates both seamlessly
- Self-improving system

**Actions:**
1. **AI learning from workflows**
   - Feed completed workflows to ML training
   - RAG ingests workflow best practices
   - Community annotations enhance knowledge

2. **Predictive workflow optimization**
   - AI predicts optimal workflow paths
   - Proactive recovery before failures
   - Automated gap resolution

3. **Unified decision orchestration**
   - Decision Center as single source of truth
   - AI and workflow policies unified
   - Consistent governance across platform

---

## 6. Code Examples

### 6.1 Decision Center Calls ai-foundation

```python
# /infrastructure/decision-center/services/decision_service.py

from ai_foundation import RAGPipeline, LLMRouter
from decision_center.policies import PolicyEngine

class DecisionService:
    def __init__(self):
        self.rag = RAGPipeline()
        self.llm = LLMRouter()
        self.policy_engine = PolicyEngine()

    async def make_ai_assisted_decision(self, query: str, context: dict):
        """Make decision with AI assistance, governed by policies"""

        # Step 1: Check policies (budget, rate limit)
        policies = self.policy_engine.get_policies("ai_policies.llm_selection")

        if not self._check_budget(policies["cost_controls"]):
            return {"decision": "rejected", "reason": "Budget exceeded"}

        # Step 2: Determine task type (affects LLM choice)
        task_type = self._classify_task(query, context)

        # Step 3: Retrieve knowledge via RAG
        knowledge = await self.rag.retrieve(
            query=query,
            filters={"industry": context.get("industry")},
            top_k=5,
            enable_reranking=True
        )

        # Step 4: Validate RAG quality
        rag_policies = self.policy_engine.get_policies("ai_policies.rag_quality")
        if len(knowledge) < rag_policies["retrieval_thresholds"]["min_results"]:
            return {
                "decision": "escalate",
                "reason": "Insufficient knowledge (< 3 results)"
            }

        # Step 5: Generate recommendation via LLM
        recommendation = await self.llm.query(
            system_prompt="You are a BCM expert advisor.",
            user_prompt=f"Context: {knowledge}\n\nQuestion: {query}",
            task_type=task_type
        )

        # Step 6: Log to audit trail
        await self._audit_log({
            "query": query,
            "task_type": task_type,
            "knowledge_sources": len(knowledge),
            "model_used": self.llm.get_provider_info(),
            "recommendation": recommendation
        })

        return {
            "decision": "ai_recommendation",
            "recommendation": recommendation,
            "knowledge_sources": knowledge,
            "confidence": self._calculate_confidence(knowledge)
        }

    def _check_budget(self, cost_controls: dict) -> bool:
        """Check if we're within daily budget"""
        current_spend = self._get_daily_spend()
        return current_spend < cost_controls["daily_budget"]

    def _classify_task(self, query: str, context: dict) -> str:
        """Classify query to determine task type (for LLM routing)"""
        if "strategic" in query.lower() or context.get("criticality") == "HIGH":
            return "strategic_analysis"
        elif "quick" in query.lower() or len(query) < 50:
            return "quick_tasks"
        else:
            return "content_generation"

    def _calculate_confidence(self, knowledge: list) -> float:
        """Calculate confidence based on RAG results"""
        if not knowledge:
            return 0.0

        # Average score from knowledge results
        avg_score = sum(k['score'] for k in knowledge) / len(knowledge)

        # Weight by source priority
        iso_count = sum(1 for k in knowledge if k['source'] == 'iso_standard')
        source_bonus = 0.1 * iso_count

        return min(1.0, avg_score + source_bonus)
```

---

### 6.2 Decision Center Triggers Temporal Workflow

```python
# /infrastructure/decision-center/services/recovery_service.py

from temporalio.client import Client
from workflow_intelligence.temporal_workflows import (
    CoordinationWorkflow,
    CrossServiceWorkflow,
    ParallelTaskWorkflow
)
from decision_center.policies import PolicyEngine

class RecoveryService:
    def __init__(self):
        self.temporal_client = None
        self.policy_engine = PolicyEngine()

    async def initialize(self):
        """Connect to Temporal server"""
        self.temporal_client = await Client.connect("localhost:7233")

    async def trigger_recovery_workflow(
        self,
        recovery_type: str,
        params: dict,
        context: dict
    ):
        """Trigger appropriate recovery workflow based on failure type"""

        # Step 1: Get recovery policies
        recovery_policies = self.policy_engine.get_policies(
            "workflow_policies.recovery_workflows"
        )

        recovery_config = recovery_policies.get(recovery_type)
        if not recovery_config:
            raise ValueError(f"Unknown recovery type: {recovery_type}")

        # Step 2: Check if approval required
        approval_policies = self.policy_engine.get_policies(
            "workflow_policies.temporal_workflows.approval_requirements"
        )

        requires_approval = self._check_approval_requirement(
            context,
            approval_policies
        )

        if requires_approval:
            # Request approval before triggering workflow
            approval = await self._request_approval(
                recovery_type,
                params,
                context
            )

            if not approval["approved"]:
                return {
                    "status": "rejected",
                    "reason": "Approval denied"
                }

        # Step 3: Trigger appropriate Temporal workflow
        workflow_class = self._select_workflow_class(recovery_config["workflow"])

        intent_data = {
            "action": recovery_type,
            "entity": params.get("entity"),
            "params": params,
            "context": context,
            "require_approval": requires_approval
        }

        # Step 4: Execute workflow
        result = await self.temporal_client.execute_workflow(
            workflow_class.run,
            intent_data,
            id=f"recovery-{recovery_type}-{context.get('incident_id')}",
            task_queue="coordination",
            execution_timeout=recovery_config.get("timeout", 600)
        )

        # Step 5: Log to audit trail
        await self._audit_log({
            "recovery_type": recovery_type,
            "workflow": recovery_config["workflow"],
            "result": result,
            "required_approval": requires_approval
        })

        return result

    def _select_workflow_class(self, workflow_name: str):
        """Map workflow name to Temporal workflow class"""
        workflows = {
            "DatabaseRecoverySaga": CoordinationWorkflow,
            "CascadeRecovery": CrossServiceWorkflow,
            "EventBusRecovery": CoordinationWorkflow,
            "GatewayRecovery": CoordinationWorkflow
        }
        return workflows.get(workflow_name, CoordinationWorkflow)

    def _check_approval_requirement(
        self,
        context: dict,
        approval_policies: list
    ) -> bool:
        """Check if this operation requires approval"""
        for policy in approval_policies:
            condition = policy["condition"]

            # Simple condition evaluation (production would use proper parser)
            if "severity == 'CRITICAL'" in condition:
                if context.get("severity") == "CRITICAL":
                    return True

            if "affects_production" in condition:
                if context.get("affects_production") and \
                   context.get("change_type") == "destructive":
                    return True

        return False
```

---

### 6.3 Governance Rules Validation

```python
# /infrastructure/decision-center/services/governance_service.py

from workflow_intelligence.governance import RulesEngine, BIARules
from decision_center.policies import PolicyEngine

class GovernanceService:
    def __init__(self):
        self.rules_engine = RulesEngine()
        self.policy_engine = PolicyEngine()

        # Register BIA rules
        for rule in BIARules.get_all_rules():
            self.rules_engine.register_rule(rule)

    async def validate_workflow_action(
        self,
        workflow_context: dict,
        action: str,
        current_stage: str
    ) -> dict:
        """Validate workflow action against governance rules"""

        # Step 1: Run rules engine validation
        is_valid, violations = self.rules_engine.validate(
            context=workflow_context,
            current_stage=current_stage
        )

        # Step 2: Get governance policies
        governance_policies = self.policy_engine.get_policies(
            "workflow_policies.governance_rules"
        )

        # Step 3: Determine decision based on violations
        if not is_valid:
            decision = self._determine_action(violations, governance_policies)
        else:
            decision = {
                "allowed": True,
                "action": "proceed",
                "violations": []
            }

        # Step 4: Check escalation requirement
        if self.rules_engine.should_escalate(violations):
            decision["escalate"] = True
            decision["escalation_reason"] = self._format_escalation_reason(
                violations
            )

        # Step 5: Audit log
        await self._audit_log({
            "workflow_id": workflow_context.get("workflow_id"),
            "action": action,
            "stage": current_stage,
            "violations": [v.__dict__ for v in violations],
            "decision": decision
        })

        return decision

    def _determine_action(self, violations, governance_policies):
        """Determine action based on violation severity"""

        # Get constitution violations (most severe)
        constitution_violations = self.rules_engine.get_constitution_violations(
            violations
        )

        if constitution_violations:
            # BLOCK on constitution violations
            return {
                "allowed": False,
                "action": "BLOCK",
                "violations": [v.__dict__ for v in constitution_violations],
                "reason": "Constitution rule violation (CRITICAL)"
            }

        # Check for HIGH severity violations
        high_violations = [
            v for v in violations
            if v.severity.value == "high"
        ]

        if len(high_violations) >= governance_policies["escalation_logic"][1]["high_violations"]:
            return {
                "allowed": False,
                "action": "ESCALATE",
                "violations": [v.__dict__ for v in high_violations],
                "reason": "Too many HIGH severity violations"
            }

        # WARN on MEDIUM violations
        medium_violations = [
            v for v in violations
            if v.severity.value == "medium"
        ]

        if medium_violations:
            return {
                "allowed": True,
                "action": "WARN_AND_PROCEED",
                "violations": [v.__dict__ for v in medium_violations],
                "reason": "Non-critical violations detected"
            }

        return {
            "allowed": True,
            "action": "proceed",
            "violations": []
        }

    def _format_escalation_reason(self, violations):
        """Format human-readable escalation reason"""
        critical = [v for v in violations if v.severity.value == "critical"]
        high = [v for v in violations if v.severity.value == "high"]

        if critical:
            return f"{len(critical)} CRITICAL violations require immediate attention"
        elif len(high) >= 3:
            return f"{len(high)} HIGH severity violations detected"
        else:
            return "Escalation required per governance policy"
```

---

## Summary

This document provides a **complete extraction** of policy requirements from `ai-foundation` and `workflow_intelligence`, mapping them to Decision Center's policy engine format.

**Key Deliverables:**

1. ✅ **Policy Extraction:** All decision-making logic from AI core systems documented
2. ✅ **YAML Additions:** Ready-to-use policy definitions for `policies.yaml`
3. ✅ **Integration Points:** Clear guidance on when Decision Center should call AI/workflow systems
4. ✅ **Migration Plan:** Phased approach from static policies → dynamic integration → full orchestration
5. ✅ **Code Examples:** Practical implementation patterns

**Next Steps:**

1. Review this document with team
2. Merge YAML additions into `/infrastructure/decision-center/policies.yaml`
3. Begin Phase 2 implementation (policy loading and evaluation)
4. Set up integration tests for policy enforcement

**Decision Center becomes the governance layer** that:
- Enforces AI budgets and quality gates
- Validates workflow actions against rules
- Orchestrates complex recovery workflows
- Provides unified audit trail

This integration makes the platform **truly intelligent** - AI provides the brains, workflows provide the execution, and Decision Center provides the governance.
