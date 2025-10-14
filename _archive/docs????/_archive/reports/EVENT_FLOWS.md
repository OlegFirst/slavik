# Event Flow Diagrams
## BCM Platform - Event-Driven Choreography

**Version:** 2.0
**Last Updated:** 2025-10-09
**Purpose:** Visual documentation of event-driven service choreography

---

## Table of Contents

- [Overview](#overview)
- [Primary Flows](#primary-flows)
  - [BIA → Risk → Planning Flow](#bia--risk--planning-flow)
  - [Compliance Gap → Remediation Flow](#compliance-gap--remediation-flow)
  - [Exercise → Improvement Flow](#exercise--improvement-flow)
  - [Crisis → Response → Recovery Flow](#crisis--response--recovery-flow)
- [Service Interaction Matrix](#service-interaction-matrix)
- [Event Timing and Dependencies](#event-timing-and-dependencies)
- [Error Handling and Retries](#error-handling-and-retries)

---

## Overview

This document visualizes the event-driven choreography between services in the BCM platform. Each flow shows how events cascade through the system to trigger automated actions without central orchestration.

**Choreography Principles:**
- **No Central Orchestrator**: Services react to events independently
- **Loose Coupling**: Services don't call each other's APIs
- **Event-Driven**: All integration happens through EventBus
- **Autonomous**: Each service owns its business logic
- **Resilient**: Failed events are retried, services recover independently

---

## Primary Flows

### BIA → Risk → Planning Flow

**Description:** The core business continuity workflow. BIA assessment triggers automatic risk identification and BC plan creation.

**Business Value:**
- Automates risk assessment based on critical processes
- Ensures BC plans exist for high-risk scenarios
- Reduces manual coordination between teams

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     BIA → RISK → PLANNING FLOW                          │
│                                                                          │
│  User Action                Event                    Service Reaction   │
└─────────────────────────────────────────────────────────────────────────┘

 [User]
   │
   │ Complete BIA Assessment
   ↓
 ┌─────────────┐
 │ BIA Service │
 └─────────────┘
   │
   │ Publishes: bia.assessment.completed
   │ {
   │   assessment_id: "bia-001",
   │   processes: [
   │     { process_id: "p1", criticality: "critical", rto: 4 },
   │     { process_id: "p2", criticality: "high", rto: 8 }
   │   ],
   │   critical_process_count: 2
   │ }
   │
   ├──────────────────┬────────────────────────┐
   │                  │                        │
   ↓                  ↓                        ↓
┌──────────────┐  ┌──────────────┐   ┌────────────────┐
│ Risk Service │  │Planning Svc  │   │ Audit Service  │
└──────────────┘  └──────────────┘   └────────────────┘
   │                  │
   │ Subscribes to:   │ Subscribes to:
   │ bia.assessment   │ bia.assessment
   │ .completed       │ .completed
   │                  │
   │ AI Analysis:     │ Analyze recovery
   │ - Critical       │ requirements:
   │   processes      │ - RTO < 4h → Hot site
   │ - Tight RTOs     │ - RTO < 24h → Warm site
   │ - Dependencies   │ - RTO > 24h → Cold site
   │                  │
   │ Publishes:       │ Publishes:
   │ risk.suggestion  │ plan.strategy
   │ .generated       │ .proposed
   │ {                │ {
   │   suggested_     │   process_id: "p1",
   │   risks: [       │   strategy: "hot_site",
   │     {            │   priority: "critical"
   │       title:     │ }
   │       "Disrup    │
   │       tion...",  │
   │       severity:  │
   │       "high"     │
   │     }            │
   │   ]              │
   │ }                │
   │                  │
   │                  │
   │ Risk Service     │
   │ creates risks    │
   │ from suggestions │
   │                  │
   │ Publishes:       │
   │ risk.assessment  │
   │ .completed       │
   │ {                │
   │   risks: [       │
   │     {            │
   │       risk_id:   │
   │       "r1",      │
   │       severity:  │
   │       "critical" │
   │     }            │
   │   ],             │
   │   high_risk_     │
   │   count: 1       │
   │ }                │
   │                  │
   │                  ↓
   │              ┌──────────────┐
   │              │Planning Svc  │
   │              └──────────────┘
   │                  │
   │                  │ Subscribes to:
   │                  │ risk.assessment
   │                  │ .completed
   │                  │
   │                  │ Auto-create BC
   │                  │ plans for high
   │                  │ risks:
   │                  │ - Risk r1 →
   │                  │   Plan p1
   │                  │
   │                  │ Publishes:
   │                  │ plan.created
   │                  │ {
   │                  │   plan_id: "pl1",
   │                  │   plan_type:
   │                  │   "business_
   │                  │   continuity",
   │                  │   priority:
   │                  │   "critical"
   │                  │ }
   │                  │
   │                  ↓
   │              [Plan Created]
   │
   ↓
[Risks Created]


TIMING:
─────────
BIA Assessment Complete → Risk Suggestions: < 1 second
Risk Assessment Complete → BC Plans Created: < 2 seconds
Total Flow Time: < 5 seconds

RETRY POLICY:
────────────
- Events retried up to 3 times
- Exponential backoff: 1s, 2s, 4s
- Dead letter queue after max retries

ERROR HANDLING:
──────────────
- If Risk service fails: BIA still completes, manual risk creation needed
- If Planning service fails: Risk assessment completes, manual plan creation
- All failures logged to audit service
```

---

### Compliance Gap → Remediation Flow

**Description:** Automated remediation planning when compliance gaps are identified.

**Business Value:**
- Ensures compliance gaps are tracked and remediated
- Creates accountability through plan assignment
- Links compliance to risk management

```
┌─────────────────────────────────────────────────────────────────────────┐
│                 COMPLIANCE GAP → REMEDIATION FLOW                        │
└─────────────────────────────────────────────────────────────────────────┘

 [Auditor]
   │
   │ Identify Compliance Gap
   ↓
 ┌─────────────────────┐
 │ Compliance Service  │
 └─────────────────────┘
   │
   │ Publishes: compliance.gap.identified
   │ {
   │   gap_id: "gap-001",
   │   requirement_id: "iso-8.2.2",
   │   severity: "high",
   │   description: "Missing BIA for critical processes"
   │ }
   │
   ├──────────────────┬────────────────────┐
   │                  │                    │
   ↓                  ↓                    ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│Planning Svc  │  │ Risk Service │  │ Alert Svc    │
└──────────────┘  └──────────────┘  └──────────────┘
   │                  │                    │
   │ Create           │ Assess             │ Notify
   │ Remediation      │ Compliance         │ Management
   │ Plan             │ Risk               │
   │                  │                    │
   │ Publishes:       │ Publishes:         │
   │ plan.created     │ risk.identified    │
   │                  │                    │
   ↓                  ↓                    ↓
 [Remediation]   [Risk Created]       [Alert Sent]


DEPENDENCIES:
────────────
- Compliance Service → Planning Service
- Compliance Service → Risk Service
- Both run in parallel (no blocking)
```

---

### Exercise → Improvement Flow

**Description:** Continuous improvement based on exercise results.

**Business Value:**
- Identifies gaps through realistic testing
- Drives plan updates and training needs
- Closes the continuous improvement loop

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   EXERCISE → IMPROVEMENT FLOW                            │
└─────────────────────────────────────────────────────────────────────────┘

 [Exercise Team]
   │
   │ Complete Exercise
   ↓
 ┌─────────────────┐
 │ Exercise Service│
 └─────────────────┘
   │
   │ Publishes: exercise.completed
   │ {
   │   exercise_id: "ex-001",
   │   success_rate: 0.75,
   │   gaps_identified: ["rto_breach", "communication_failure"]
   │ }
   │
   │ Publishes: exercise.gap.identified (for each gap)
   │ {
   │   exercise_id: "ex-001",
   │   gap_type: "rto_breach",
   │   severity: "high",
   │   description: "Recovery took 6h, RTO is 4h"
   │ }
   │
   ├──────────────────┬────────────────────┬────────────────┐
   │                  │                    │                │
   ↓                  ↓                    ↓                ↓
┌──────────────┐  ┌──────────────┐  ┌──────────┐  ┌───────────────┐
│Planning Svc  │  │Training Svc  │  │Audit Svc │  │Governance Svc │
└──────────────┘  └──────────────┘  └──────────┘  └───────────────┘
   │                  │
   │ Update plans     │ Create training
   │ based on gaps    │ for failures
   │                  │
   │ Publishes:       │ Publishes:
   │ plan.updated     │ learning.program
   │                  │ .created
   │                  │
   ↓                  ↓
 [Plan Updated]   [Training Created]


IMPROVEMENT CYCLE:
─────────────────
Test → Identify Gaps → Update Plans → Train → Retest
```

---

### Crisis → Response → Recovery Flow

**Description:** Real-time crisis management and recovery coordination.

**Business Value:**
- Rapid response to incidents
- Coordinated recovery across teams
- Real-time tracking and reporting

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  CRISIS → RESPONSE → RECOVERY FLOW                       │
└─────────────────────────────────────────────────────────────────────────┘

 [Incident Manager]
   │
   │ Declare Crisis
   ↓
 ┌───────────────┐
 │ Crisis Service│
 └───────────────┘
   │
   │ Publishes: crisis.declared
   │ {
   │   crisis_id: "crisis-001",
   │   crisis_type: "cyber_attack",
   │   severity: "critical"
   │ }
   │
   ├──────────────────┬────────────────────┬────────────────┐
   │                  │                    │                │
   ↓                  ↓                    ↓                ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│Planning Svc  │  │Response Svc  │  │Notification  │  │Coordination  │
└──────────────┘  └──────────────┘  │   Service    │  │   Service    │
   │                  │              └──────────────┘  └──────────────┘
   │ Activate BC      │ Mobilize              │                │
   │ Plan             │ Response Team         │ Mass           │ Start
   │                  │                       │ Notification   │ Crisis Mgmt
   │ Publishes:       │ Publishes:            │                │
   │ plan.activated   │ response.team         │                │
   │                  │ .mobilized            │                │
   │                  │                       │                │
   │                  │ Execute Recovery      │                │
   │                  │ Actions               │                │
   │                  │                       │                │
   │                  │ Publishes:            │                │
   │                  │ response.recovery     │                │
   │                  │ .completed            │                │
   │                  │                       │                │
   │                  ↓                       │                │
   │              ┌───────────────┐           │                │
   │              │ Crisis Service│           │                │
   │              └───────────────┘           │                │
   │                  │                       │                │
   │                  │ Publishes:            │                │
   │                  │ crisis.resolved       │                │
   │                  │ {                     │                │
   │                  │   crisis_id:          │                │
   │                  │   "crisis-001",       │                │
   │                  │   duration: 240,      │                │
   │                  │   summary: "..."      │                │
   │                  │ }                     │                │
   │                  │                       │                │
   │                  ├───────────────────────┼────────────────┤
   │                  │                       │                │
   │                  ↓                       ↓                ↓
   │              [Audit Log]          [Stakeholders]    [Post-Incident]
   │                                    [Notified]        [Review]
   ↓
[Plan Deactivated]


CRITICAL TIMING:
───────────────
Crisis Declared → Plan Activated: < 30 seconds
Crisis Declared → Team Mobilized: < 1 minute
Crisis Declared → Stakeholders Notified: < 2 minutes

PRIORITY:
────────
All crisis events use CRITICAL priority for immediate processing
```

---

## Service Interaction Matrix

This matrix shows which services publish and subscribe to which events.

```
┌────────────────────────┬─────────┬──────────┬──────────┬─────────────┬────────────┐
│ Event Type             │   BIA   │   Risk   │ Planning │ Compliance  │  Exercise  │
│                        │ Service │ Service  │ Service  │  Service    │  Service   │
├────────────────────────┼─────────┼──────────┼──────────┼─────────────┼────────────┤
│ bia.assessment         │   PUB   │   SUB    │   SUB    │             │            │
│ .completed             │         │          │          │             │            │
├────────────────────────┼─────────┼──────────┼──────────┼─────────────┼────────────┤
│ bia.critical.process   │   PUB   │   SUB    │   SUB    │             │            │
│ .identified            │         │          │          │             │            │
├────────────────────────┼─────────┼──────────┼──────────┼─────────────┼────────────┤
│ bia.criticality        │   PUB   │   SUB    │          │             │            │
│ .changed               │         │          │          │             │            │
├────────────────────────┼─────────┼──────────┼──────────┼─────────────┼────────────┤
│ risk.assessment        │         │   PUB    │   SUB    │             │            │
│ .completed             │         │          │          │             │            │
├────────────────────────┼─────────┼──────────┼──────────┼─────────────┼────────────┤
│ risk.severity          │         │   PUB    │   SUB    │             │            │
│ .changed               │         │          │          │             │            │
├────────────────────────┼─────────┼──────────┼──────────┼─────────────┼────────────┤
│ risk.mitigation        │         │   PUB    │   SUB    │             │            │
│ .proposed              │         │          │          │             │            │
├────────────────────────┼─────────┼──────────┼──────────┼─────────────┼────────────┤
│ plan.created           │         │          │   PUB    │             │            │
├────────────────────────┼─────────┼──────────┼──────────┼─────────────┼────────────┤
│ plan.activated         │         │          │   PUB    │             │            │
├────────────────────────┼─────────┼──────────┼──────────┼─────────────┼────────────┤
│ plan.tested            │         │          │   PUB    │             │    SUB     │
├────────────────────────┼─────────┼──────────┼──────────┼─────────────┼────────────┤
│ compliance.gap         │         │   SUB    │   SUB    │    PUB      │            │
│ .identified            │         │          │          │             │            │
├────────────────────────┼─────────┼──────────┼──────────┼─────────────┼────────────┤
│ exercise.completed     │   SUB   │          │   SUB    │             │    PUB     │
├────────────────────────┼─────────┼──────────┼──────────┼─────────────┼────────────┤
│ exercise.gap           │         │          │   SUB    │             │    PUB     │
│ .identified            │         │          │          │             │            │
└────────────────────────┴─────────┴──────────┴──────────┴─────────────┴────────────┘

PUB = Publishes this event
SUB = Subscribes to this event
```

---

## Event Timing and Dependencies

### Event Processing Times

Average time from event publication to handler completion:

```
Event Type                          Avg Processing Time    Max Acceptable Time
──────────────────────────────────────────────────────────────────────────────
bia.assessment.completed            500ms                  5s
risk.suggestion.generated           200ms                  2s
risk.assessment.completed           800ms                  5s
plan.created                        300ms                  3s
compliance.gap.identified           400ms                  3s
exercise.completed                  1s                     10s
crisis.declared                     100ms                  1s (CRITICAL)
plan.activated                      150ms                  1s (CRITICAL)
```

### Dependency Chain

Shows the longest event chains and their total expected time:

```
1. BIA → Risk → Planning (Complete Flow)
   bia.assessment.completed (500ms)
   → risk.suggestion.generated (200ms)
   → risk.assessment.completed (800ms)
   → plan.created (300ms)
   ────────────────────────────────────
   Total: ~1.8 seconds

2. Compliance → Risk & Planning (Parallel)
   compliance.gap.identified (400ms)
   ├→ risk.identified (200ms)
   └→ plan.created (300ms)
   ────────────────────────────────────
   Total: ~600ms (parallel execution)

3. Exercise → Improvements (Multiple outputs)
   exercise.completed (1s)
   ├→ plan.updated (300ms)
   ├→ learning.program.created (400ms)
   └→ audit record (100ms)
   ────────────────────────────────────
   Total: ~1.4 seconds (parallel)

4. Crisis → Recovery (Time-Critical)
   crisis.declared (100ms)
   ├→ plan.activated (150ms)
   ├→ response.team.mobilized (200ms)
   └→ notification sent (100ms)
   ────────────────────────────────────
   Total: ~350ms (critical path)
```

---

## Error Handling and Retries

### Retry Strategy

```
Attempt    Delay      Total Elapsed    Action
─────────────────────────────────────────────────
1          0s         0s               Initial attempt
2          1s         1s               First retry
3          2s         3s               Second retry
4          4s         7s               Final retry
Failed     -          -                Move to Dead Letter Queue
```

### Circuit Breaker

Services implement circuit breakers to prevent cascade failures:

```
State        Condition                    Action
───────────────────────────────────────────────────────────────
CLOSED       Normal operation             Process all events
OPEN         >50% failures in 1 min       Reject events, return error
HALF_OPEN    After 30s cooldown           Try 1 request to test
             If success → CLOSED
             If failure → OPEN (60s)
```

### Dead Letter Queue Handling

Events that fail after max retries go to DLQ:

```
┌──────────────┐
│  Event Fails │
│  3x Retries  │
└──────────────┘
       │
       │ After max retries
       ↓
┌──────────────┐
│ Dead Letter  │
│    Queue     │
└──────────────┘
       │
       │ Alert sent to ops team
       ↓
┌──────────────┐
│   Manual     │
│  Inspection  │
└──────────────┘
       │
       ├─→ Fix issue & replay event
       ├─→ Discard if invalid
       └─→ Create incident if system issue
```

### Monitoring and Alerts

Critical metrics monitored:

- **Event Processing Rate**: events/second per service
- **Event Latency**: p50, p95, p99 processing time
- **Error Rate**: % of failed events
- **Retry Rate**: % of events requiring retries
- **DLQ Size**: number of failed events in DLQ
- **Circuit Breaker State**: open/closed per service

---

## Best Practices

### 1. Event Design
- ✅ Include all necessary data in event payload
- ✅ Use past tense for event names (completed, not complete)
- ✅ Include correlation_id for tracing
- ✅ Keep events immutable
- ❌ Don't reference data that might change

### 2. Handler Implementation
- ✅ Make handlers idempotent
- ✅ Handle events quickly (< 5s)
- ✅ Log all event processing
- ✅ Validate event data
- ❌ Don't make external API calls synchronously
- ❌ Don't process heavy computations in handlers

### 3. Error Handling
- ✅ Catch and log all exceptions
- ✅ Return success even if handler fails (unless business critical)
- ✅ Use dead letter queues for failed events
- ✅ Monitor DLQ size
- ❌ Don't retry indefinitely
- ❌ Don't throw exceptions for business logic failures

### 4. Testing
- ✅ Test event handlers in isolation
- ✅ Test complete flows end-to-end
- ✅ Test failure scenarios (timeouts, invalid data)
- ✅ Test event ordering
- ✅ Test concurrent events

---

## Troubleshooting

### Common Issues

**Issue: Events not being processed**
- Check: EventBus connection
- Check: Subscription registered correctly
- Check: Handler not throwing exceptions
- Check: Circuit breaker not open

**Issue: Slow event processing**
- Check: Handler doing heavy computation
- Check: Handler making synchronous API calls
- Check: Database connection pool exhausted
- Check: Event payload too large

**Issue: Events processed multiple times**
- Check: Handler is idempotent
- Check: Not using auto-acknowledge before processing
- Check: Handler timeout too short

**Issue: Events lost**
- Check: Persistence enabled on EventBus
- Check: Consumers using durable queues
- Check: Not using auto-acknowledge
- Check: Dead letter queue configured

---

**Generated by:** Agent 3 - Choreography Implementation Specialist
**Last Updated:** 2025-10-09
