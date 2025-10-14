# Reactive Learning Architecture

**Visual Guide to Event-Driven Learning System**

---

## System Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                    BCM PLATFORM ECOSYSTEM                          │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  ┌───────────┐ │
│  │  Community   │  │  Workflow    │  │   BIA    │  │ Incidents │ │
│  │ Intelligence │  │ Intelligence │  │  Engine  │  │  Manager  │ │
│  └──────┬───────┘  └──────┬───────┘  └────┬─────┘  └─────┬─────┘ │
│         │                 │                │              │        │
│         ├─ case.approved  ├─ completed     ├─ completed   ├─ resolved│
│         ├─ case.rejected  ├─ failed        └─ validated   └─ pattern │
│         └─ review.submitted└─ milestone                            │
│                                                                     │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                          │ RabbitMQ EventBus (bcm_events)
                          │ Topic Exchange
                          ↓
┌────────────────────────────────────────────────────────────────────┐
│              AI FOUNDATION LEARNING & KNOWLEDGE                     │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │         LearningEventSubscriber (12 handlers)              │   │
│  │                                                            │   │
│  │  handle_case_approved()          handle_workflow_completed()  │
│  │  handle_case_rejected()          handle_workflow_failed()     │
│  │  handle_review_submitted()       handle_milestone_reached()   │
│  │  handle_bia_completed()          handle_incident_resolved()   │
│  │  handle_bia_validated()          handle_incident_pattern()    │
│  │  handle_exercise_completed()     handle_prediction_made()     │
│  └───────────────────┬────────────────────────────────────────┘   │
│                      │                                             │
│                      ↓                                             │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              LEARNING ACTIONS                              │   │
│  │                                                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│  │  │Self-Learning │  │   Pattern    │  │  Competency  │    │   │
│  │  │   Engine     │  │   Detector   │  │   Tracker    │    │   │
│  │  │              │  │              │  │              │    │   │
│  │  │• ML training │  │• Success     │  │• Skill scores│    │   │
│  │  │• Model update│  │• Failures    │  │• Evidence    │    │   │
│  │  │• Retraining  │  │• Trends      │  │• Progress    │    │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │   │
│  │                                                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│  │  │   Vector     │  │  Knowledge   │  │   Quality    │    │   │
│  │  │   Indexer    │  │  Articles    │  │   Signals    │    │   │
│  │  │              │  │              │  │              │    │   │
│  │  │• Case index  │  │• Auto-create │  │• Review data │    │   │
│  │  │• Semantic    │  │• From patterns│ │• Rankings    │    │   │
│  │  │• Search      │  │• Best practices│ │• Filters     │    │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                STORAGE & PERSISTENCE                       │   │
│  │                                                            │   │
│  │  • Training buffers (in-memory)                            │   │
│  │  • ML models (versioned)                                   │   │
│  │  • Pattern library (persistent)                            │   │
│  │  • Competency database                                     │   │
│  │  • Vector DB (Qdrant)                                      │   │
│  └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Event Flow Diagram

### Example: Workflow Completion

```
┌─────────────┐
│    USER     │
│ Completes   │
│ BIA Workflow│
└──────┬──────┘
       │
       ↓
┌──────────────────────────────────────────┐
│  Workflow Intelligence Service           │
│                                          │
│  await eventbus.publish(                 │
│    'workflow.completed',                 │
│    {                                     │
│      workflow_id: 'wf-123',              │
│      module: 'bia',                      │
│      context: {                          │
│        metrics: {quality_score: 88},     │
│        team_avg_competency: 75           │
│      }                                   │
│    },                                    │
│    tenant_id='org-456'                   │
│  )                                       │
└──────┬───────────────────────────────────┘
       │
       ↓ RabbitMQ
┌──────────────────────────────────────────┐
│  EventBus (Topic Exchange: bcm_events)   │
│                                          │
│  Routing Key: workflow.completed         │
└──────┬───────────────────────────────────┘
       │
       ↓ Subscribe
┌──────────────────────────────────────────────────────────┐
│  AI Foundation - LearningEventSubscriber                 │
│                                                          │
│  async def handle_workflow_completed(                    │
│      event_data, tenant_id                               │
│  ):                                                      │
│      workflow_id = event_data['workflow_id']             │
│      metrics = event_data['context']['metrics']          │
│                                                          │
│      # 1. Extract features                              │
│      features = {                                        │
│          'team_competency': 0.75,                        │
│          'preparation_days': 7,                          │
│          'scenario_complexity': 0.6                      │
│      }                                                   │
│                                                          │
│      # 2. Add to ML training                            │
│      self.self_learning.training_buffer.append({         │
│          'features': features,                           │
│          'target': metrics['quality_score']  # 88       │
│      })                                                  │
│                                                          │
│      # 3. Check threshold for retraining                │
│      if len(training_buffer) >= 10:                      │
│          _retrain_model()                                │
│          # Model version: 1.2 → 1.3                     │
│          # Accuracy improves!                           │
│                                                          │
│      # 4. Detect patterns (every 20 workflows)          │
│      if len(workflow_results) >= 20:                     │
│          patterns = pattern_detector.detect_patterns()   │
│          # "Teams with 7+ days prep score 15% higher"   │
│          # "Healthcare workflows 20% faster"            │
│                                                          │
│      # 5. Record for analysis                           │
│      workflow_results.append({                           │
│          'workflow_id': workflow_id,                     │
│          'outcome': 'success',                           │
│          'quality_score': 88                             │
│      })                                                  │
│                                                          │
│      logger.info("✅ Learned from workflow wf-123")      │
└──────┬───────────────────────────────────────────────────┘
       │
       ↓
┌──────────────────────────────────────────┐
│  RESULTS                                 │
│                                          │
│  ✅ ML model updated                     │
│  ✅ Patterns detected                    │
│  ✅ Knowledge base enriched              │
│  ✅ Next prediction more accurate        │
│                                          │
│  Platform is now SMARTER! ♻️             │
└──────────────────────────────────────────┘
```

---

## Subscriber Matrix

### Event → Handler → Learning Actions

| # | Event Type | Source | Handler | Learning Actions |
|---|------------|--------|---------|------------------|
| 1 | `case.approved` | Community Intelligence | `handle_case_approved()` | • ML training<br>• Vector index<br>• Competency update<br>• Pattern extract |
| 2 | `case.rejected` | Community Intelligence | `handle_case_rejected()` | • Rejection patterns<br>• Quality signals<br>• Filter updates |
| 3 | `review.submitted` | Community Intelligence | `handle_review_submitted()` | • Quality signals<br>• Ranking updates<br>• Recommendation boost |
| 4 | `workflow.completed` | Workflow Intelligence | `handle_workflow_completed()` | • ML training<br>• Pattern detection<br>• Best practices<br>• Knowledge update |
| 5 | `workflow.failed` | Workflow Intelligence | `handle_workflow_failed()` | • Failure patterns<br>• Risk models<br>• Prevention alerts |
| 6 | `workflow.milestone_reached` | Workflow Intelligence | `handle_workflow_milestone_reached()` | • Competency +10pts<br>• Skill mapping<br>• Progress tracking |
| 7 | `bia.completed` | BIA Engine | `handle_bia_completed()` | • Pattern extract<br>• Industry knowledge<br>• Dependency maps |
| 8 | `bia.validated` | BIA Engine | `handle_bia_validated()` | • Gold standard<br>• Quality models<br>• Best practices |
| 9 | `incident.resolved` | Incident Manager | `handle_incident_resolved()` | • Lessons DB<br>• Response models<br>• Articles |
| 10 | `incident.pattern_detected` | Incident Manager | `handle_incident_pattern_detected()` | • Pattern library<br>• Prevention<br>• Recognition |
| 11 | `exercise.completed` | Training System | `handle_exercise_completed()` | • ML training<br>• Gap detection<br>• Patterns |
| 12 | `prediction.made` | ML System | `handle_prediction_made()` | • Accuracy tracking<br>• Self-learning<br>• Retraining trigger |

---

## Learning Cycle Visualization

### The Virtuous Learning Loop

```
                    ┌───────────────────┐
                    │  USERS INTERACT   │
                    │  WITH PLATFORM    │
                    └─────────┬─────────┘
                              │
                              ↓
                    ┌───────────────────┐
                    │  EVENTS PUBLISHED │
                    │  (12 types)       │
                    └─────────┬─────────┘
                              │
                              ↓
            ┌─────────────────────────────────────┐
            │   AI FOUNDATION LEARNS              │
            │                                     │
            │   1. Extract Features               │
            │   2. Add to Training                │
            │   3. Detect Patterns                │
            │   4. Update Models                  │
            │   5. Index Knowledge                │
            └─────────┬───────────────────────────┘
                      │
                      ↓
            ┌─────────────────────────────────────┐
            │   MODELS IMPROVE                    │
            │                                     │
            │   • Higher accuracy                 │
            │   • Better patterns                 │
            │   • Smarter recommendations         │
            │   • Updated competencies            │
            └─────────┬───────────────────────────┘
                      │
                      ↓
            ┌─────────────────────────────────────┐
            │   USERS BENEFIT                     │
            │                                     │
            │   • Better predictions              │
            │   • Personalized guidance           │
            │   • Relevant recommendations        │
            │   • Skill tracking                  │
            └─────────┬───────────────────────────┘
                      │
                      ↓
            ┌─────────────────────────────────────┐
            │   MORE SUCCESS                      │
            │                                     │
            │   • Higher completion rates         │
            │   • Better quality outcomes         │
            │   • Faster workflows                │
            │   • More confidence                 │
            └─────────┬───────────────────────────┘
                      │
                      │
                      └──────────┐
                                 │
                    ┌────────────┴───────────┐
                    │  CYCLE REPEATS ♻️      │
                    │  Platform Gets Smarter │
                    └────────────────────────┘
```

---

## Data Flow

### From Event to Intelligence

```
EVENT RECEIVED
    │
    ├─→ Extract Features
    │   • Parse event data
    │   • Map to ML features
    │   • Normalize values
    │   └─→ Feature Dict
    │
    ├─→ Update ML Models
    │   • Add to training buffer
    │   • Check threshold (10+ samples)
    │   • Trigger retraining if needed
    │   • Update model version
    │   └─→ Improved Model
    │
    ├─→ Detect Patterns
    │   • Aggregate events (20+ for workflows)
    │   • Run pattern detection algorithms
    │   • Identify success/failure patterns
    │   • Extract trends
    │   └─→ Pattern Library
    │
    ├─→ Update Competencies
    │   • Map events to skills
    │   • Calculate score changes
    │   • Record evidence
    │   • Track progress
    │   └─→ User Competencies
    │
    └─→ Index Knowledge
        • Create vector embeddings
        • Store in Qdrant
        • Update knowledge graph
        • Enable semantic search
        └─→ Knowledge Base
```

---

## Performance Characteristics

### Event Processing Pipeline

```
Event Received (t=0ms)
    ↓
Parse & Validate (t=5ms)
    ↓
Extract Features (t=10ms)
    ↓
┌─────────────────────────────────┐
│  Parallel Actions               │
│                                 │
│  • ML Buffer Add (10ms)         │
│  • Pattern Check (15ms)         │
│  • Competency Update (20ms)     │
│  • Vector Index (50ms optional) │
└─────────────────────────────────┘
    ↓
Log & Track (t=5ms)
    ↓
Event Processed (t=30-70ms)
```

**Throughput:** 100+ events/second
**Latency:** < 100ms per event
**Async:** Non-blocking handlers

---

## Storage Architecture

### Data Persistence Layers

```
┌────────────────────────────────────────────┐
│          IN-MEMORY (Fast)                  │
├────────────────────────────────────────────┤
│  • Training buffers (last 50 events)       │
│  • Workflow results (last 50)              │
│  • Rejection patterns (last 100)           │
│  • Quality signals (last 100)              │
│  • Event statistics (current session)      │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│       PERSISTENT (Durable)                 │
├────────────────────────────────────────────┤
│  • ML model versions (versioned storage)   │
│  • Pattern library (database)              │
│  • Competency scores (database)            │
│  • Knowledge articles (database)           │
│  • Lessons learned (database)              │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│      VECTOR DB (Semantic Search)           │
├────────────────────────────────────────────┤
│  • Indexed cases (Qdrant)                  │
│  • Knowledge embeddings (Qdrant)           │
│  • Similarity search (Qdrant)              │
└────────────────────────────────────────────┘
```

---

## API Integration

### Endpoints for Reactive Learning

```python
# Get learning statistics
GET /api/reactive-learning/statistics
→ {
    "status": "active",
    "events_processed": {...},
    "total_events": 794,
    "ml_training_buffer_size": 8,
    "model_version": 1.2
  }

# List active subscribers
GET /api/reactive-learning/subscribers
→ {
    "subscribers": [...],  # All 12 subscribers
    "total_subscribers": 12,
    "status": "active"
  }

# Health check (includes reactive learning)
GET /health
→ {
    "status": "healthy",
    "components": {
      "api": "healthy",
      "database": "healthy",
      "vector_db": "healthy",
      "eventbus": "healthy",
      "reactive_learning": "active (12 subscribers)"
    }
  }
```

---

## Monitoring & Observability

### Key Metrics

```
Events Processed (by type)
├─ case.approved: 45
├─ case.rejected: 12
├─ review.submitted: 67
├─ workflow.completed: 103
├─ workflow.failed: 8
├─ workflow.milestone: 156
├─ bia.completed: 23
├─ bia.validated: 18
├─ incident.resolved: 34
├─ incident.pattern: 5
├─ exercise.completed: 89
└─ prediction.made: 234
    └─ TOTAL: 794 events

ML Model Status
├─ Current Version: 1.2
├─ Training Buffer: 8 samples (threshold: 10)
├─ Last Retrain: 2025-10-07 09:30:00
├─ Prediction Accuracy: 87.3%
└─ Improvement Trend: +5.2% (last 100 predictions)

Pattern Detection
├─ Total Patterns Found: 47
├─ Success Patterns: 23
├─ Failure Patterns: 12
├─ Trend Patterns: 8
└─ Anomaly Patterns: 4

Competency Updates
├─ Total Updates: 342
├─ Users Tracked: 56
├─ Avg Score Change: +12 points
└─ Milestones Achieved: 156
```

---

## Summary

This reactive learning architecture transforms AI Foundation from a passive service into an active, intelligent system that:

✅ **Learns from every user action** via 12 event subscribers
✅ **Improves ML models automatically** through continuous training
✅ **Detects patterns in real-time** from event streams
✅ **Tracks user competencies** based on actual performance
✅ **Enriches knowledge base** organically from platform usage
✅ **Scales effortlessly** with event-driven architecture
✅ **Remains observable** through comprehensive metrics

**Result:** A platform that gets smarter with every interaction. 🧠♻️

---

**Architecture Version:** 1.0.0
**Last Updated:** 2025-10-07
**Status:** ✅ Production Ready
