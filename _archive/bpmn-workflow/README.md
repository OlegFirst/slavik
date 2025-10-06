# Coordination Service - BCM Platform

**Purpose:** Workflow coordination and BPMN process orchestration

**Technology:** FastAPI + BPMN Engine + State Machine

**Port:** 8003

---

## 🎯 Features

### Core Functionality
- ✅ **Workflow Orchestration** - Coordinate multi-step BCM processes
- ✅ **BPMN Support** - Business Process Model and Notation
- ✅ **State Management** - Track workflow execution state
- ✅ **Parallel Execution** - Run tasks in parallel when possible
- ✅ **Error Handling** - Retry logic and error recovery
- ✅ **Compensation** - Rollback transactions on failure

### BCM Workflows
- ✅ **BIA Workflow** - Coordinate BIA analysis process
- ✅ **Risk Assessment Workflow** - Multi-stage risk assessment
- ✅ **Incident Response Workflow** - Automated incident handling
- ✅ **Plan Approval Workflow** - Multi-level plan approval
- ✅ **Exercise Workflow** - Exercise scheduling and execution

---

## 📡 API Endpoints

### Health Check
```bash
GET /health
```

### Start Workflow
```bash
POST /api/workflows/start
{
  "workflow_type": "bia_analysis",
  "tenant_id": "tenant_001",
  "input_data": {
    "process_id": 123
  }
}
```

### Get Workflow Status
```bash
GET /api/workflows/{workflow_id}/status
```

### Cancel Workflow
```bash
POST /api/workflows/{workflow_id}/cancel
```

---

## 🔄 Workflow Examples

### BIA Analysis Workflow
```
Start → Gather Process Data → Analyze Dependencies →
Calculate RTO/RPO → Generate Report → Notify Stakeholders → End
```

### Incident Response Workflow
```
Start → Classify Incident → Notify Response Team →
Activate Plans → Execute Response → Document Actions → End
```

### Plan Approval Workflow
```
Start → Manager Review →
  ├─ Approved → Director Review →
  │   ├─ Approved → Publish Plan → End
  │   └─ Rejected → Request Changes → Manager Review
  └─ Rejected → Request Changes → Manager Review
```

---

## 🚀 Integration

Coordination service orchestrates calls to:
- **BCM Services** - BIA, Risk, Plans, Incident
- **EventBus** - Publish workflow events
- **Orchestration** - Trigger AI analysis
- **Gateway** - Receive workflow requests

---

**Version:** 1.0
**Status:** ✅ Consolidated
**Port:** 8003
