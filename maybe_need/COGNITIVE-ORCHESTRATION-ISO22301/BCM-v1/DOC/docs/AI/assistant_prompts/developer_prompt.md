# Developer Integration Prompt - BCM PDCA Conductor

## Integration Architecture

The AI Assistant operates as an orchestration layer that coordinates between existing BCM Platform services without direct database access. All operations follow the **Event-Driven Integration Pattern**.

## Core Integration Pattern

### Step 1: State Assessment
```python
# Get current KPIs and system state
GET /bcm/kpi
Headers: {"Company-ID": tenant_id}
Response: {
    "bia_coverage": 0.64,
    "plans_up_to_date": 0.72,
    "capa_on_time": 0.90,
    "incident_response_time": 4.5,
    "exercise_completion": 0.85,
    "training_completion": 0.78
}
```

### Step 2: Historical Context
```python
# Get recent event history for context
GET /api/events/history?tenant_id={tenant_id}&limit=50&event_type=bcm.*
Response: {
    "events": [
        {
            "event_type": "bcm.incident.opened",
            "tenant_id": "demo_hospital", 
            "data": {"incident_id": "INC-001", "severity": "high"},
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

### Step 3: Decision Making
```python
# Analyze KPIs + Events → Determine next PDCA step
decision_logic = {
    "critical_incidents": len([e for e in events if e.data.severity in ["high", "critical"]]),
    "bia_gap": 1.0 - current_kpis.bia_coverage,
    "plan_gap": 1.0 - current_kpis.plans_up_to_date,
    "overdue_capa": get_overdue_capa_count(),
    "last_exercise": get_days_since_last_exercise()
}

# Priority matrix
if decision_logic.critical_incidents > 0:
    recommended_action = "incident_draft_response"
elif decision_logic.overdue_capa > 0:
    recommended_action = "audit_summarize"  
elif decision_logic.bia_gap > 0.2:
    recommended_action = "plan_generate_bia"
elif decision_logic.plan_gap > 0.3:
    recommended_action = "plan_generate_draft"
```

### Step 4: Action Execution
```python
# Execute recommended action via Orchestrator
POST /api/recommendations
Headers: {"Content-Type": "application/json"}
Body: {
    "context": "pdca_conductor",
    "data": {
        "action_type": "plan_generation",
        "process_id": "EHR",
        "rationale": "plan_outdated_185_days"
    },
    "tenant_id": tenant_id,
    "user_id": assistant_user_id
}

Response: {
    "recommendation": "Generate BCP draft for EHR process",
    "confidence": 0.92,
    "decision_id": "dec_12345"
}
```

### Step 5: Event Monitoring
```python
# Wait for confirmation events via SSE/WebSocket
# Connect to: /api/events/stream?tenant_id={tenant_id}

expected_events = {
    "plan_generation": ["bcm.plan.draft_generated", "bcm.ai.decision.approved"],
    "incident_response": ["bcm.incident.response_generated"],
    "audit_summary": ["bcm.audit.gap_found", "bcm.capa.created"],
    "exercise_schedule": ["bcm.exercise.scheduled"]
}

# Monitor for 30 seconds, then timeout with fallback message
```

### Step 6: Activity Logging
```python
# Log all assistant activities
POST /api/events/publish
Body: {
    "event_type": "assistant.activity",
    "tenant_id": tenant_id,
    "data": {
        "intent": "plan_generate_draft",
        "reason": "Plans up-to-date metric at 72%, EHR plan 185 days old",
        "actions": [
            {
                "type": "orchestrator_call",
                "endpoint": "/api/recommendations", 
                "params": {"process_id": "EHR", "action_type": "plan_generation"}
            }
        ],
        "status": "requested",
        "decision_id": "dec_12345",
        "correlation_id": f"assistant_{timestamp}_{random_id}"
    },
    "correlation_id": correlation_id
}
```

## API Contract Specifications

### Odoo KPI Endpoint (READ-ONLY)
```http
GET /bcm/kpi HTTP/1.1
Host: odoo-instance:8069
Company-ID: {tenant_id}

Response Codes:
- 200: Success with KPI data
- 404: No KPI data found for tenant
- 403: Access denied for tenant
```

### EventBus Endpoints
```http
# Get historical events
GET /api/events/history HTTP/1.1
Host: eventbus:8001
Query Parameters:
- tenant_id: required
- event_type: optional filter (bcm.*, assistant.*)  
- limit: default 50, max 200
- from_date, to_date: optional date range

# Real-time event stream (READ-ONLY for assistant)
GET /api/events/stream HTTP/1.1
Host: eventbus:8001
Query Parameters:
- tenant_id: required
Connection: Keep-Alive, SSE

# Publish assistant activity
POST /api/events/publish HTTP/1.1
Host: eventbus:8001
Content-Type: application/json
```

### Orchestrator Action Endpoints
```http
# Generate recommendations/drafts
POST /api/recommendations HTTP/1.1  
Host: orchestrator:8002
Content-Type: application/json
Body: RecommendationRequest

# Audit evidence summarization
POST /api/audit/summarize HTTP/1.1
Host: orchestrator:8002  
Content-Type: application/json
Body: AuditSummaryRequest

# Get pending AI decisions
GET /api/ai/decisions/pending HTTP/1.1
Host: orchestrator:8002
Query Parameters:
- tenant_id: required
```

### Document Processor Integration
```http
# Document analysis status  
GET /api/documents/{doc_id}/analysis HTTP/1.1
Host: document-processor:8003
Query Parameters:
- tenant_id: required

# Document search
GET /api/documents/search HTTP/1.1  
Host: document-processor:8003
Query Parameters:
- tenant_id: required
- document_type: optional
- min_score: optional compliance score filter
```

## Error Handling Patterns

### Network/Service Errors
```python
def call_service_with_retry(url, data, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code in [503, 504, 502]:
                # Service temporarily unavailable, retry
                time.sleep(2 ** attempt)
                continue
            else:
                # Permanent error, don't retry
                break
        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                return {"error": "Service timeout", "fallback": "manual_steps"}
        except requests.exceptions.ConnectionError:
            if attempt == max_retries - 1:
                return {"error": "Service unavailable", "fallback": "contact_admin"}
    
    return {"error": "Service error", "fallback": "try_again_later"}
```

### Data Validation
```python
def validate_tenant_access(tenant_id, user_context):
    """Ensure user has access to tenant data"""
    if not tenant_id:
        raise ValueError("tenant_id required for all operations")
    
    user_tenants = user_context.get("allowed_tenants", [])
    if tenant_id not in user_tenants:
        raise PermissionError(f"Access denied to tenant {tenant_id}")

def validate_kpi_data(kpi_response):
    """Validate KPI data structure"""
    required_fields = ["bia_coverage", "plans_up_to_date", "capa_on_time"]
    for field in required_fields:
        if field not in kpi_response:
            return {"error": f"Missing {field} in KPI data", "fallback": "partial_analysis"}
    return kpi_response
```

## Workflow Integration Examples

### BIA Workflow Integration
```python
async def execute_bia_workflow(tenant_id, process_id):
    # 1. Check current BIA status
    process_info = await get_process_info(process_id, tenant_id)
    
    # 2. Call BIA computation via Orchestrator
    bia_request = {
        "context": "bia_analysis", 
        "data": {"process_id": process_id},
        "tenant_id": tenant_id
    }
    
    decision = await call_orchestrator("/api/recommendations", bia_request)
    
    # 3. Wait for BIA completion event
    await wait_for_event("bcm.bia.completed", decision.get("correlation_id"))
    
    # 4. Log assistant activity
    await log_assistant_activity({
        "intent": "plan_generate_bia",
        "reason": f"BIA missing for critical process {process_id}",
        "actions": [{"type": "bia_computation", "process_id": process_id}],
        "status": "completed"
    })
```

### Incident Response Integration
```python
async def execute_incident_response(tenant_id, incident_id):
    # 1. Get incident details
    events = await get_event_history(tenant_id, f"bcm.incident.*")
    incident_events = [e for e in events if e.data.incident_id == incident_id]
    
    # 2. Generate response via Orchestrator
    response_request = {
        "context": "incident_response",
        "data": {
            "incident_id": incident_id,
            "severity": incident_events[0].data.severity,
            "type": incident_events[0].data.type
        },
        "tenant_id": tenant_id
    }
    
    decision = await call_orchestrator("/api/recommendations", response_request)
    
    # 3. Monitor for response generation
    await wait_for_event("bcm.incident.response_generated", decision.correlation_id)
```

## Performance Considerations

### Caching Strategy
```python
# Cache KPI data for 5 minutes to reduce API calls
kpi_cache = {
    "data": None,
    "timestamp": None,
    "ttl": 300  # 5 minutes
}

def get_cached_kpis(tenant_id):
    now = time.time()
    if (kpi_cache["data"] and 
        kpi_cache["timestamp"] and 
        (now - kpi_cache["timestamp"]) < kpi_cache["ttl"]):
        return kpi_cache["data"]
    
    # Fetch fresh data
    fresh_kpis = fetch_kpis_from_odoo(tenant_id)
    kpi_cache.update({
        "data": fresh_kpis,
        "timestamp": now
    })
    return fresh_kpis
```

### Concurrent Operations
```python
async def parallel_data_gathering(tenant_id):
    """Gather multiple data sources concurrently"""
    tasks = [
        fetch_kpis_from_odoo(tenant_id),
        get_event_history(tenant_id, limit=50),
        get_pending_decisions(tenant_id),
        get_overdue_capa(tenant_id)
    ]
    
    kpis, events, decisions, capa = await asyncio.gather(*tasks)
    
    return {
        "kpis": kpis,
        "recent_events": events, 
        "pending_decisions": decisions,
        "overdue_capa": capa
    }
```

## Security Implementation

### Authentication Headers
```python
def get_auth_headers(user_context):
    """Generate authentication headers for service calls"""
    return {
        "Authorization": f"Bearer {user_context.jwt_token}",
        "X-User-ID": user_context.user_id,
        "X-Tenant-ID": user_context.tenant_id,
        "Content-Type": "application/json"
    }
```

### Data Sanitization  
```python
def sanitize_for_logging(data):
    """Remove sensitive information before logging"""
    sensitive_fields = ["password", "api_key", "token", "email", "phone"]
    
    if isinstance(data, dict):
        return {
            k: "***REDACTED***" if k.lower() in sensitive_fields else sanitize_for_logging(v) 
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [sanitize_for_logging(item) for item in data]
    else:
        return data
```

## Testing Integration

### Mock Service Responses
```python
# For development/testing environments
MOCK_RESPONSES = {
    "/bcm/kpi": {
        "bia_coverage": 0.75,
        "plans_up_to_date": 0.80,
        "capa_on_time": 0.90
    },
    "/api/events/history": {
        "events": [
            {
                "event_type": "bcm.incident.opened",
                "tenant_id": "test_tenant",
                "data": {"incident_id": "TEST-001", "severity": "medium"}
            }
        ]
    }
}

def get_mock_response(endpoint):
    return MOCK_RESPONSES.get(endpoint, {"error": "Mock not found"})
```

This integration pattern ensures the AI Assistant remains within its boundaries while effectively orchestrating PDCA workflows across the BCM Platform architecture.
