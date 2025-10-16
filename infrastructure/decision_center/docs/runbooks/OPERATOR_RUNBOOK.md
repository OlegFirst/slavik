# Decision Center - Operator Runbook

Comprehensive guide for operators managing Decision Center in production.

## Table of Contents

1. [Overview](#overview)
2. [Daily Operations](#daily-operations)
3. [Escalation Handling](#escalation-handling)
4. [Policy Management](#policy-management)
5. [Monitoring & Alerts](#monitoring--alerts)
6. [Troubleshooting](#troubleshooting)
7. [Incident Response](#incident-response)
8. [Maintenance](#maintenance)

---

## Overview

### What is Decision Center?

Decision Center is an AI-driven decision-making system that automates infrastructure operations while maintaining human oversight through a multi-level escalation system.

**Key Responsibilities:**
- Monitor escalations requiring human approval
- Review and adjust policies
- Investigate anomalies in decision patterns
- Respond to incidents
- Maintain system health

### System Architecture

```
Infrastructure Issues → Decision Center → AI Consultation → Automated Decision
                                      ↓
                              Escalation (if needed)
                                      ↓
                              Human Operator (YOU)
```

### Access Points

**Production:**
- Dashboard: https://decision-center.example.com
- Grafana: https://grafana.example.com
- API: https://decision-center.example.com/api/v1

**Emergency Access:**
```bash
# SSH to bastion
ssh operator@bastion.example.com

# Access Decision Center pod
kubectl exec -it -n decision-center <pod-name> -- /bin/sh
```

---

## Daily Operations

### Morning Checklist

**1. Check System Health (5 min)**

```bash
# Health check
curl https://decision-center.example.com/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0-mvp",
  "components": {
    "policy_engine": "ok",
    "decision_engine": "ok",
    "escalation_manager": "ok",
    "audit_logger": "ok",
    "ai_hub": "ok",
    "eventbus": "connected",
    "deep_ai_integration": "enabled"
  }
}
```

**2. Review Active Escalations (10 min)**

```bash
# List active escalations
curl https://decision-center.example.com/api/v1/escalations

# Or via dashboard:
# Navigate to: Dashboard → Escalations → Active
```

**Actions:**
- Review each escalation
- Approve/reject based on context
- Document decision reasoning

**3. Check Overnight Decisions (10 min)**

```bash
# Decision history (last 24 hours)
curl https://decision-center.example.com/api/v1/audit/history/all?days=1
```

**Look for:**
- Unusual approval/rejection patterns
- Repeated failures for same service
- High frequency of escalations
- AI confidence scores trending down

**4. Review Monitoring Dashboards (5 min)**

**Grafana Panels to Check:**
- Decision Request Rate (should be steady)
- Decision Latency (p95 < 1s)
- AI Tier Usage (Tier 2/3 primary, Tier 1 rare)
- Active Escalations (< 5 typical)
- Policy Check Rate

---

## Escalation Handling

### Understanding Escalation Levels

**L1 (Low Confidence):**
- AI confidence < 80%
- No clear policy match
- **SLA:** 30 minutes
- **Action:** Quick review, usually approve

**L2 (Repeated Failure):**
- Service failed 2+ times
- Pattern detected
- **SLA:** 15 minutes
- **Action:** Investigate root cause before approving

**L3 (Critical Service):**
- Database, authentication, payment systems
- **SLA:** 10 minutes
- **Action:** Careful review, verify impact

**L4 (Security/Data Risk):**
- Security incidents
- Data loss potential
- **SLA:** Immediate
- **Action:** Escalate to security team, incident response

### Escalation Response Workflow

**Step 1: Assess Urgency**

```bash
# Get escalation details
GET /api/v1/escalations/{escalation_id}

# Response includes:
{
  "escalation_id": "esc_abc123",
  "service": "database",
  "action": "restart",
  "escalation_level": "L2",
  "urgency": 4,
  "reason": "Multiple restart attempts failed",
  "context": {
    "recovery_attempts": 2,
    "downtime_seconds": 180,
    "memory_percent": 95
  }
}
```

**Step 2: Gather Context**

Check:
- Service health dashboard
- Recent deployments
- Infrastructure changes
- Related alerts

**Step 3: Make Decision**

**Approve:**
```bash
curl -X POST https://decision-center.example.com/api/v1/escalations/{escalation_id}/respond \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "operator": "john.doe@company.com",
    "resolution": "Approved restart after reviewing metrics. High memory usage (95%) is root cause. Monitoring for recurrence."
  }'
```

**Reject:**
```bash
curl -X POST https://decision-center.example.com/api/v1/escalations/{escalation_id}/respond \
  -H "Content-Type: application/json" \
  -d '{
    "approved": false,
    "operator": "john.doe@company.com",
    "resolution": "Rejected. Investigating memory leak in application code. Created ticket OPS-1234."
  }'
```

### Decision Guidelines

**Approve if:**
- ✅ Root cause is understood
- ✅ Action will resolve issue
- ✅ No data loss risk
- ✅ Impact is contained
- ✅ Rollback plan exists

**Reject if:**
- ❌ Root cause unknown
- ❌ Risk of data loss
- ❌ Cascading failure potential
- ❌ Security implications
- ❌ Better alternative exists

**Escalate to L4 if:**
- ⚠️ Security breach suspected
- ⚠️ Data integrity at risk
- ⚠️ Multiple critical services affected
- ⚠️ Outside normal failure patterns

---

## Policy Management

### Understanding Policies

Policies define automatic decision-making rules. Located in `/app/policies.yaml` or ConfigMap in K8s.

**Policy Structure:**
```yaml
services:
  database:
    auto_approve: true
    confidence_threshold: 0.85
    max_recovery_attempts: 3
    allowed_actions:
      - restart
      - failover
    blocked_actions:
      - delete
      - drop_database
    escalation_triggers:
      - repeated_failure: 3
      - downtime_minutes: 10
```

### Viewing Current Policies

```bash
# Get policies for specific service
curl https://decision-center.example.com/api/v1/policies/database

# Response:
{
  "auto_approve": true,
  "confidence_threshold": 0.85,
  "max_recovery_attempts": 3,
  "allowed_actions": ["restart", "failover"],
  "blocked_actions": ["delete", "drop_database"]
}
```

### Updating Policies

**Method 1: Edit ConfigMap (K8s)**

```bash
# Edit ConfigMap
kubectl edit configmap policies-config -n decision-center

# Reload policies in Decision Center
curl -X POST https://decision-center.example.com/api/v1/policies/reload
```

**Method 2: Edit policies.yaml (Docker)**

```bash
# Edit file
vim /path/to/policies.yaml

# Reload
curl -X POST https://decision-center.example.com/api/v1/policies/reload
```

### Common Policy Adjustments

**Scenario 1: Too Many Escalations for Service**

**Problem:** `redis` service constantly escalates
**Solution:** Lower confidence threshold

```yaml
services:
  redis:
    confidence_threshold: 0.75  # Was 0.85
```

**Scenario 2: Critical Service Needs More Scrutiny**

**Problem:** `auth-service` should never auto-approve
**Solution:** Disable auto-approval

```yaml
services:
  auth-service:
    auto_approve: false  # Always escalate
    allowed_actions: []
```

**Scenario 3: Service Stuck in Restart Loop**

**Problem:** `api-gateway` restarting repeatedly
**Solution:** Reduce max recovery attempts

```yaml
services:
  api-gateway:
    max_recovery_attempts: 2  # Was 3
```

### Policy Change Best Practices

1. **Document changes**: Always add comments explaining why
2. **Test in staging first**: Validate policy changes
3. **Monitor impact**: Check decision patterns after changes
4. **Version control**: Commit policy changes to git
5. **Communicate**: Notify team of policy updates

---

## Monitoring & Alerts

### Key Metrics to Watch

**1. Decision Request Rate**
- **Normal:** 10-50 requests/min
- **Alert:** > 100 requests/min (incident in progress)
- **Alert:** < 1 request/min (system issue)

**2. Decision Latency (p95)**
- **Normal:** < 1 second
- **Alert:** > 5 seconds (AI API slow or overloaded)

**3. Approval Rate**
- **Normal:** 70-85% auto-approved
- **Alert:** < 50% (policies too strict or service degradation)
- **Alert:** > 95% (policies too lenient)

**4. Escalation Rate**
- **Normal:** 15-30% escalated
- **Alert:** > 50% (investigate policy tuning)

**5. AI Tier Usage**
- **Normal:** 80% Tier 2 (Sonnet), 20% Tier 3 (Haiku)
- **Alert:** > 10% Tier 1 (Opus) - cost implications

**6. Active Escalations**
- **Normal:** 2-5 pending
- **Alert:** > 10 (operators may be overwhelmed)

### Grafana Dashboards

**Main Dashboard:** Decision Center Overview
- Request rate graph
- Latency gauge
- Decisions by outcome (pie chart)
- AI tier usage (stacked area)
- Active escalations (gauge)
- Policy check rate

**Drill-down Dashboards:**
- Per-service decision patterns
- AI performance metrics
- Escalation trends over time

### Alert Definitions

**Critical Alerts (PagerDuty):**

```yaml
# Decision Center Down
- alert: DecisionCenterDown
  expr: up{job="decision-center"} == 0
  for: 2m
  severity: critical
  action: "Check pod status, restart if needed"

# High Escalation Rate
- alert: HighEscalationRate
  expr: rate(escalation_requests_total[5m]) > 0.5
  for: 10m
  severity: critical
  action: "Review escalations, check for incident"

# AI API Failures
- alert: AIAPIFailures
  expr: rate(ai_tier_errors_total[5m]) > 0.1
  for: 5m
  severity: critical
  action: "Check ANTHROPIC_API_KEY, verify API status"
```

**Warning Alerts (Slack):**

```yaml
# High Decision Latency
- alert: HighDecisionLatency
  expr: histogram_quantile(0.95, decision_latency_seconds) > 3
  for: 10m
  severity: warning
  action: "Check AI API latency, database connection pool"

# Low Approval Rate
- alert: LowApprovalRate
  expr: rate(decision_requests_total{outcome="approved"}[30m]) < 0.5
  for: 30m
  severity: warning
  action: "Review recent decisions, consider policy adjustments"
```

### Log Analysis

**Key Log Patterns:**

```bash
# Find all escalations in last hour
kubectl logs -n decision-center -l app=decision-center --since=1h | grep "📤 Escalation created"

# Find all AI consultation failures
kubectl logs -n decision-center -l app=decision-center --since=1h | grep "AI consultation failed"

# Find all policy violations
kubectl logs -n decision-center -l app=decision-center --since=1h | grep "Policy violation"

# Track specific service decisions
kubectl logs -n decision-center -l app=decision-center --since=1h | grep "service=database"
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Decision Center Not Responding

**Symptoms:**
- `/health` endpoint returns 503 or times out
- No decisions being made
- Escalations not appearing

**Diagnosis:**
```bash
# Check pod status
kubectl get pods -n decision-center

# Check logs
kubectl logs -n decision-center -l app=decision-center --tail=100

# Check dependencies
kubectl get pods -n decision-center | grep -E "(postgres|redis)"
```

**Resolution:**
1. If pods are CrashLooping, check logs for error
2. If database connection fails, verify PostgreSQL is running
3. If Redis fails, check Redis pod and connectivity
4. If API key invalid, update secret and restart pods

#### Issue 2: AI Consultations Failing

**Symptoms:**
- All decisions escalate
- Logs show "AI consultation failed"
- AI status endpoint returns errors

**Diagnosis:**
```bash
# Check AI status
curl https://decision-center.example.com/api/v1/ai/status

# Expected:
{
  "tier2": {"available": true, "model": "claude-sonnet-3.5"},
  "tier3": {"available": true, "model": "claude-haiku-3.5"}
}
```

**Resolution:**
1. Verify `ANTHROPIC_API_KEY` is set correctly
2. Check Anthropic API status: https://status.anthropic.com
3. Verify API quota/limits not exceeded
4. Check network connectivity to Anthropic API
5. Enable fallback mode (heuristics) temporarily

#### Issue 3: Escalations Not Reaching Operators

**Symptoms:**
- Decisions stuck in "pending" state
- No escalations visible in dashboard
- Services waiting for approval

**Diagnosis:**
```bash
# List escalations directly
curl https://decision-center.example.com/api/v1/escalations

# Check escalation manager logs
kubectl logs -n decision-center -l app=decision-center | grep "EscalationManager"
```

**Resolution:**
1. Verify escalation notification system
2. Check escalation SLA timers
3. Review escalation assignment logic
4. Manually respond to stuck escalations

#### Issue 4: High Memory Usage

**Symptoms:**
- Pods being OOM killed
- Decision latency increasing
- Metrics showing memory leak

**Diagnosis:**
```bash
# Check pod resource usage
kubectl top pods -n decision-center

# Check memory metrics in Grafana
```

**Resolution:**
1. Increase memory limits in deployment
2. Check for memory leaks in audit logger
3. Review EventBus message queue size
4. Restart pods to clear memory

#### Issue 5: Database Connection Pool Exhausted

**Symptoms:**
- "Too many connections" errors
- Decision latency spikes
- Pods unable to connect to PostgreSQL

**Diagnosis:**
```bash
# Check active connections
kubectl exec -n decision-center postgres-0 -- psql -U decision_center -c "SELECT count(*) FROM pg_stat_activity;"

# Check max connections
kubectl exec -n decision-center postgres-0 -- psql -U decision_center -c "SHOW max_connections;"
```

**Resolution:**
1. Increase PostgreSQL max_connections
2. Tune connection pool settings in Decision Center
3. Scale down Decision Center replicas temporarily
4. Add connection pooler (PgBouncer)

---

## Incident Response

### Incident Levels

**P1 (Critical):**
- Decision Center completely down
- Multiple critical services failing
- Data loss risk
- **Response:** Immediate, all hands on deck

**P2 (High):**
- Degraded performance
- High escalation rate
- Single critical service affected
- **Response:** Within 15 minutes

**P3 (Medium):**
- Non-critical service issues
- Policy adjustments needed
- Monitoring anomalies
- **Response:** Within 1 hour

### P1 Incident Runbook

**Step 1: Assess Impact (2 min)**

```bash
# Check Decision Center health
curl https://decision-center.example.com/health

# Check active escalations
curl https://decision-center.example.com/api/v1/escalations

# Check Grafana for service impact
```

**Step 2: Notify Team (1 min)**

- Page on-call engineer
- Post to #incidents Slack channel
- Update status page

**Step 3: Immediate Mitigation (5 min)**

**If Decision Center is down:**
```bash
# Restart pods
kubectl rollout restart deployment decision-center -n decision-center

# Check pod status
kubectl get pods -n decision-center -w
```

**If database is failing:**
```bash
# Check PostgreSQL
kubectl get pods -n decision-center | grep postgres

# Restart if needed
kubectl delete pod postgres-0 -n decision-center
```

**If AI API is failing:**
```bash
# Enable fallback mode (edit ConfigMap to set AI_ENABLE_FALLBACK=true)
# Or manually approve all escalations
```

**Step 4: Investigate Root Cause (15 min)**

- Review logs from time of incident
- Check recent deployments/changes
- Review monitoring dashboards
- Identify contributing factors

**Step 5: Full Resolution**

- Fix root cause
- Verify system stability
- Clear escalation backlog
- Update runbook with learnings

**Step 6: Post-Incident**

- Write incident report
- Conduct blameless post-mortem
- Identify preventive measures
- Update monitoring/alerts

---

## Maintenance

### Regular Maintenance Tasks

**Weekly:**
- Review and archive old audit logs (> 90 days)
- Check disk usage on PostgreSQL/Redis
- Review policy effectiveness
- Update decision pattern documentation

**Monthly:**
- PostgreSQL database vacuum and analyze
- Review AI tier costs and usage
- Update operator documentation
- Test disaster recovery procedures

**Quarterly:**
- Audit decision accuracy (false positive/negative rates)
- Review and update policies based on patterns
- Security audit of secrets and access
- Load testing and capacity planning

### Database Maintenance

**Vacuum PostgreSQL:**
```bash
kubectl exec -n decision-center postgres-0 -- psql -U decision_center -c "VACUUM ANALYZE;"
```

**Check Database Size:**
```bash
kubectl exec -n decision-center postgres-0 -- psql -U decision_center -c "
SELECT pg_size_pretty(pg_database_size('decision_center'));
"
```

**Archive Old Data:**
```sql
-- Delete audit logs older than 90 days
DELETE FROM audit_logs WHERE timestamp < NOW() - INTERVAL '90 days';

-- Delete old decisions
DELETE FROM decisions WHERE decided_at < NOW() - INTERVAL '90 days';
```

### Backup Procedures

**Manual Backup:**
```bash
# PostgreSQL backup
kubectl exec -n decision-center postgres-0 -- pg_dump -U decision_center decision_center \
  | gzip > backup-$(date +%Y%m%d-%H%M%S).sql.gz

# Upload to S3
aws s3 cp backup-*.sql.gz s3://backups/decision-center/
```

**Restore from Backup:**
```bash
# Download backup
aws s3 cp s3://backups/decision-center/backup-20250101-020000.sql.gz .

# Restore
gunzip backup-20250101-020000.sql.gz
kubectl exec -i -n decision-center postgres-0 -- psql -U decision_center decision_center < backup-20250101-020000.sql
```

---

## Quick Reference

### Important URLs

- Dashboard: https://decision-center.example.com
- Grafana: https://grafana.example.com
- API Docs: https://decision-center.example.com/docs
- Status Page: https://status.example.com

### Key Contacts

- On-call Engineer: #oncall Slack, PagerDuty
- Infrastructure Team: #infrastructure Slack
- Security Team: security@example.com
- Management: escalations@example.com

### Useful Commands

```bash
# Health check
curl https://decision-center.example.com/health

# List escalations
curl https://decision-center.example.com/api/v1/escalations

# Approve escalation
curl -X POST https://decision-center.example.com/api/v1/escalations/{id}/respond \
  -d '{"approved": true, "operator": "you@example.com", "resolution": "Reason"}'

# Check logs
kubectl logs -n decision-center -l app=decision-center --tail=100 -f

# Restart
kubectl rollout restart deployment decision-center -n decision-center

# Reload policies
curl -X POST https://decision-center.example.com/api/v1/policies/reload
```

### Emergency Procedures

**If completely lost:**
1. Don't panic
2. Check #incidents Slack for context
3. Page on-call engineer
4. Manually approve all pending escalations
5. Document what you did
6. Ask for help

**Escalation Path:**
1. On-call engineer (always available)
2. Infrastructure lead
3. VP Engineering

---

## Appendix

### Decision Outcomes

- **approved**: Action auto-approved by AI
- **rejected**: Action rejected by policy or AI
- **escalated**: Requires human review
- **executed**: Action was performed
- **failed**: Action attempt failed

### AI Tiers

- **Tier 1 (Opus)**: Highest capability, most expensive, for critical decisions
- **Tier 2 (Sonnet)**: Balanced capability/cost, primary tier
- **Tier 3 (Haiku)**: Fast responses, low cost, for simple decisions
- **Tier 4 (Heuristics)**: Rule-based fallback, no AI API required

### Glossary

- **BCM**: Business Continuity Management
- **RTO**: Recovery Time Objective
- **RPO**: Recovery Point Objective
- **HPA**: Horizontal Pod Autoscaler
- **Escalation**: Decision requiring human operator approval
- **Policy**: Automated rules for decision-making
- **Consultation**: AI analysis request for a decision

---

**Document Version:** 1.0
**Last Updated:** 2025-10-16
**Maintained by:** Infrastructure Team
