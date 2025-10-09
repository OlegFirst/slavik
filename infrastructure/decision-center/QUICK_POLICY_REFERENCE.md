# Quick Policy Reference Card

**For:** Decision Center Implementation Team
**Date:** 2025-10-09

---

## AI Foundation Policies (Quick Reference)

### LLM Selection
```yaml
strategic_analysis → claude-opus-4
content_generation → claude-3-5-sonnet
quick_tasks → claude-3-5-haiku
```

**Fallback:** Claude → GPT → Local
**Rate Limit:** 50 req/min
**Cost Alert:** 80% of $100 daily budget

---

### RAG Quality Gates
```yaml
min_results: 3
source_priority:
  ISO: 1.0    # Authoritative
  BCI: 0.95   # Semi-authoritative
  Cases: 0.8  # Practical
  Community: 0.7  # Peer input
```

**Action:** <3 results → Human Review

---

### ML Model Thresholds
```yaml
training: min 50 samples
confidence: <0.6 → Human Review
stuck_prob: >0.7 → Escalate
anomaly: >2.5 std dev → Investigate
```

---

## Workflow Intelligence Policies (Quick Reference)

### Rule Severity → Action
```yaml
CRITICAL (Constitution): BLOCK
HIGH (Mandatory): ESCALATE (≥3 violations)
MEDIUM (Best Practice): WARN
LOW (Recommendation): LOG
```

---

### BIA Constitution Rules (BLOCK on violation)
1. No RTO < 1h without justification (Tier 1)
2. Financial impact required (all processes)
3. Tier 1 dependency mapping (≥2 deps, people+tech)

---

### BIA Mandatory Rules (ESCALATE on violation)
1. Minimum 3 processes
2. At least 1 Tier 1 process
3. All impact types (financial, operational, reputational, regulatory)
4. RTO rationale (≥30 chars)

---

### Temporal Workflow Policies
```yaml
Retry: 3 attempts, exponential (1s → 2s → 4s → 8s)
Timeout: 10 min (activities), 24h (approvals)
Rollback: Auto on failure (compensating txns)
```

**Approval Required:**
- Severity = CRITICAL
- Cost > $100
- Production destructive changes

---

### Recovery Workflows
```yaml
database_failure → DatabaseRecoverySaga (300s)
cascade_failure → CascadeRecovery (CRITICAL, sequential)
eventbus_failure → EventBusRecovery (180s, fallback)
api_gateway_failure → GatewayRecovery (120s)
```

---

## Decision Center Integration (When to Call)

### Call ai-foundation When:
- ✅ Need AI-assisted analysis
- ✅ Complex scenario recommendation
- ✅ Knowledge retrieval required
- ✅ Predictive analytics needed

### Call workflow_intelligence When:
- ✅ Multi-step recovery required
- ✅ Distributed transaction coordination
- ✅ Governance validation before action
- ✅ Complex rollback needed

---

## Quick Decision Matrix

| Scenario | AI Foundation | Workflow Intelligence | Decision Center Action |
|----------|---------------|----------------------|------------------------|
| Simple query | LLM (Haiku) | N/A | Direct response |
| Strategic decision | LLM (Opus) + RAG | Governance validation | Check budget → Call AI → Validate rules |
| Service failure | Anomaly detection | Recovery workflow | Detect → Trigger Temporal saga |
| Workflow stuck | ML prediction | Event subscription | Predict → Escalate if >0.7 |
| Policy violation | N/A | Rules engine | Validate → BLOCK/ESCALATE/WARN |
| Multi-service op | N/A | CrossServiceWorkflow | Trigger → Monitor → Audit |

---

## Emergency Overrides

**Allow when:**
- Emergency incident (CRITICAL)
- Executive approval (CTO/Compliance Officer)
- 24-hour expiry

**Audit:**
- Log all overrides
- Weekly review required
- Max 5 overrides/day

---

## Cost Controls

| Threshold | Action |
|-----------|--------|
| $80/day | Alert admin |
| $100/day | Auto-downgrade non-critical |
| $500/day | Hard reject |

---

## Escalation Paths

| Trigger | Escalate To |
|---------|-------------|
| CRITICAL violation | Operations + Compliance |
| 3+ HIGH violations | Supervisor |
| AI stuck prediction >0.7 | Domain expert |
| Budget exceeded | Financial admin |
| Repeated failures (3x) | Engineering lead |

---

## Audit Retention

| Data Type | Retention |
|-----------|-----------|
| AI query logs | 90 days |
| Compliance decisions | 365 days |
| Workflow events | 90 days |
| Cost records | 365 days |
| Training data | 730 days |

---

## File Locations

**Full Documentation:**
`/infrastructure/decision-center/POLICY_INTEGRATION_FROM_AI_CORE.md`

**Summary:**
`/infrastructure/decision-center/POLICY_EXTRACTION_SUMMARY.md`

**Policies YAML:**
`/infrastructure/decision-center/policies.yaml`

**Source Systems:**
- `/intelligent-core/ai-foundation/` (AI policies)
- `/intelligent-core/workflow_intelligence/` (Workflow policies)

---

## Quick Commands

```bash
# View full policy document
cat /infrastructure/decision-center/POLICY_INTEGRATION_FROM_AI_CORE.md

# Check current policies
cat /infrastructure/decision-center/policies.yaml

# Test policy evaluation
python /infrastructure/decision-center/test_policies.py

# View ai-foundation LLM router
cat /intelligent-core/ai-foundation/llm/llm_router.py

# View workflow governance rules
cat /intelligent-core/workflow_intelligence/governance/bia_rules.py
```

---

## Implementation Checklist

### Phase 2 (Short-term: 2-4 weeks)
- [ ] Copy YAML from POLICY_INTEGRATION_FROM_AI_CORE.md to policies.yaml
- [ ] Implement PolicyEngine class (load YAML, evaluate rules)
- [ ] Add override mechanism with audit
- [ ] Write unit tests for policy evaluation
- [ ] Integration test with mock AI/workflow calls

### Phase 3 (Medium-term: 1-2 months)
- [ ] Create AIFoundationClient wrapper
- [ ] Enforce budget before AI calls
- [ ] Validate RAG quality gates
- [ ] Log all AI interactions to audit trail
- [ ] Add cost tracking dashboard

### Phase 4 (Long-term: 3-6 months)
- [ ] Integrate Temporal client for workflows
- [ ] Subscribe to workflow EventBus
- [ ] Enforce governance rules on transitions
- [ ] Auto-trigger recovery workflows
- [ ] Full audit trail integration

---

**Print this and keep it handy during implementation!**
