# AI Assistant Guardrails - PDCA Conductor Safety Framework

## Core Safety Principles

The BCM PDCA Conductor operates under strict safety constraints to ensure responsible AI behavior within business continuity management systems. These guardrails protect organizational data, prevent unauthorized actions, and maintain compliance with security standards.

## Access Control Guardrails

### Multi-Tenancy Enforcement
```python
def validate_tenant_access(user_context, requested_tenant_id):
    """CRITICAL: Validate every request includes valid tenant_id"""
    if not requested_tenant_id:
        raise SecurityError("tenant_id required for all operations")
    
    user_tenants = user_context.get("allowed_tenants", [])
    if requested_tenant_id not in user_tenants:
        raise PermissionError(f"Access denied to tenant {requested_tenant_id}")
    
    # Log access attempts for audit
    log_access_attempt(user_context.user_id, requested_tenant_id, "granted")
    return True
```

**Enforcement Points**:
- ✅ Every API call MUST include `tenant_id` parameter
- ✅ All KPI queries scoped by `Company-ID` header
- ✅ Event history filtered by tenant ownership
- ✅ Document analysis restricted to tenant documents
- ❌ NEVER access cross-tenant data
- ❌ NEVER suggest actions outside user's tenant scope

### Permission-Based Actions
```python
ACTION_PERMISSIONS = {
    "check_status": ["user", "admin", "bcm_manager"],
    "plan_generate_draft": ["bcm_manager", "admin"],
    "incident_draft_response": ["incident_manager", "bcm_manager", "admin"],
    "audit_summarize": ["auditor", "bcm_manager", "admin"],
    "schedule_exercise": ["exercise_coordinator", "bcm_manager", "admin"],
    "management_review_prepare": ["bcm_manager", "admin"]
}

def check_action_permission(user_role, requested_action):
    """Validate user role allows requested action"""
    allowed_roles = ACTION_PERMISSIONS.get(requested_action, ["admin"])
    return user_role in allowed_roles
```

**Permission Guardrails**:
- ✅ Validate user role before suggesting actions
- ✅ Provide role-appropriate recommendations
- ✅ Clear messaging when permissions insufficient
- ❌ NEVER attempt actions beyond user role
- ❌ NEVER bypass role-based access controls

## Data Protection Guardrails

### Sensitive Information Handling
```python
SENSITIVE_FIELDS = [
    "password", "api_key", "token", "secret", "credential",
    "ssn", "tax_id", "financial_account", "personal_email",
    "phone_number", "home_address", "salary", "medical_info"
]

def sanitize_data_for_logging(data):
    """Remove sensitive information before logging"""
    if isinstance(data, dict):
        return {
            k: "***REDACTED***" if any(field in k.lower() for field in SENSITIVE_FIELDS) 
               else sanitize_data_for_logging(v)
            for k, v in data.items()
        }
    elif isinstance(data, str):
        # Mask potential sensitive patterns
        import re
        data = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', 'XXX-XX-XXXX', data)  # SSN
        data = re.sub(r'\b\d{16}\b', 'XXXX-XXXX-XXXX-XXXX', data)  # Credit card
        return data
    return data
```

**Data Handling Rules**:
- ✅ Sanitize all log outputs
- ✅ Never store sensitive data in assistant memory
- ✅ Redact PII from activity events
- ✅ Use secure headers for API communication
- ❌ NEVER log passwords, tokens, or credentials
- ❌ NEVER expose internal system details to users

### Data Retention Limits
```python
ASSISTANT_MEMORY_LIMITS = {
    "conversation_ttl": 3600,  # 1 hour
    "kpi_cache_ttl": 300,      # 5 minutes
    "event_buffer_max": 100,   # Last 100 events only
    "decision_history": 50     # Last 50 decisions
}

def enforce_memory_limits():
    """Clear expired data from assistant memory"""
    current_time = time.time()
    if (current_time - last_kpi_fetch) > ASSISTANT_MEMORY_LIMITS["kpi_cache_ttl"]:
        clear_kpi_cache()
    
    prune_event_buffer(ASSISTANT_MEMORY_LIMITS["event_buffer_max"])
    prune_decision_history(ASSISTANT_MEMORY_LIMITS["decision_history"])
```

## Action Safety Guardrails

### Draft-Only Operations
```python
def execute_action_safely(action_type, action_data, user_context):
    """CRITICAL: All actions must be draft-only"""
    
    # Allowed action types that generate drafts only
    DRAFT_ACTIONS = [
        "plan_generate_draft", "incident_draft_response", 
        "audit_summarize", "exercise_schedule", "capa_create"
    ]
    
    if action_type not in DRAFT_ACTIONS:
        raise SecurityError(f"Action {action_type} not in approved draft-only list")
    
    # Ensure draft flag is set
    action_data["draft_mode"] = True
    action_data["requires_approval"] = True
    action_data["created_by"] = "assistant"
    
    return orchestrator_api_call(action_type, action_data, user_context)
```

**Action Safety Rules**:
- ✅ ALL actions must create drafts requiring human approval
- ✅ NO direct database modifications allowed
- ✅ NO automatic activation of plans or procedures
- ✅ Clear indication of draft status to users
- ❌ NEVER execute actions without human approval
- ❌ NEVER modify live BCM configurations directly

### Rate Limiting and Throttling
```python
RATE_LIMITS = {
    "api_calls_per_minute": 60,
    "orchestrator_calls_per_hour": 100,
    "kpi_requests_per_hour": 20,
    "document_analysis_per_day": 50
}

class RateLimiter:
    def __init__(self):
        self.call_history = defaultdict(list)
    
    def check_rate_limit(self, user_id, action_type):
        now = time.time()
        limit_window = RATE_LIMITS.get(f"{action_type}_window", 3600)
        max_calls = RATE_LIMITS.get(f"{action_type}_max", 10)
        
        # Clean old entries
        self.call_history[user_id] = [
            t for t in self.call_history[user_id] 
            if (now - t) < limit_window
        ]
        
        if len(self.call_history[user_id]) >= max_calls:
            raise RateLimitError(f"Rate limit exceeded for {action_type}")
        
        self.call_history[user_id].append(now)
```

## Input Validation Guardrails

### Parameter Sanitization
```python
def validate_and_sanitize_input(intent, parameters, user_context):
    """Validate all user inputs before processing"""
    
    # Required parameter validation
    REQUIRED_PARAMS = {
        "plan_generate_draft": ["process_id"],
        "incident_draft_response": ["incident_id", "severity"],
        "audit_summarize": ["finding_ids"],
        "schedule_exercise": ["exercise_type", "process_id"]
    }
    
    required = REQUIRED_PARAMS.get(intent, [])
    for param in required:
        if param not in parameters or not parameters[param]:
            raise ValidationError(f"Required parameter {param} missing")
    
    # Sanitize string inputs
    for key, value in parameters.items():
        if isinstance(value, str):
            # Remove potentially dangerous characters
            parameters[key] = re.sub(r'[<>"\']', '', value)
            # Limit string length
            parameters[key] = value[:1000]  # Max 1000 chars
    
    # Validate tenant_id matches user context
    if "tenant_id" in parameters:
        validate_tenant_access(user_context, parameters["tenant_id"])
    
    return parameters
```

**Input Safety Rules**:
- ✅ Validate all parameters before processing
- ✅ Sanitize user inputs to prevent injection attacks
- ✅ Enforce parameter type and format constraints
- ✅ Limit input string lengths
- ❌ NEVER trust user input without validation
- ❌ NEVER execute unsanitized parameters

### SQL Injection Prevention
```python
def safe_query_builder(filters, user_context):
    """Build queries safely with parameterization"""
    
    # Always use parameterized queries - NEVER string concatenation
    ALLOWED_FILTERS = {
        "tenant_id": str,
        "process_id": str,
        "severity": ["low", "medium", "high", "critical"],
        "status": ["open", "in_progress", "resolved", "closed"],
        "date_range": "date_range"
    }
    
    safe_filters = {}
    for key, value in filters.items():
        if key not in ALLOWED_FILTERS:
            continue  # Skip unknown filters
        
        expected_type = ALLOWED_FILTERS[key]
        if isinstance(expected_type, list):  # Enum validation
            if value not in expected_type:
                continue
        elif expected_type == str:
            value = str(value)[:100]  # Limit length
        
        safe_filters[key] = value
    
    return safe_filters
```

## System Integration Guardrails

### API Call Safety
```python
def safe_api_call(endpoint, method, data, headers, timeout=10):
    """Make API calls with safety checks"""
    
    # Validate endpoint is in allowed list
    ALLOWED_ENDPOINTS = [
        "/bcm/kpi", "/api/events/history", "/api/events/publish",
        "/api/recommendations", "/api/audit/summarize",
        "/api/ai/decisions/pending", "/api/documents/*/analysis"
    ]
    
    endpoint_allowed = any(
        fnmatch.fnmatch(endpoint, pattern) 
        for pattern in ALLOWED_ENDPOINTS
    )
    
    if not endpoint_allowed:
        raise SecurityError(f"Endpoint {endpoint} not in allowed list")
    
    # Enforce HTTPS for external calls
    if not endpoint.startswith(('https://', 'http://localhost', 'http://127.0.0.1')):
        raise SecurityError("Only HTTPS endpoints allowed for external calls")
    
    # Set security headers
    headers.update({
        "User-Agent": "BCM-PDCA-Assistant/1.0",
        "X-Requested-By": "assistant",
        "X-Request-ID": generate_request_id()
    })
    
    try:
        response = requests.request(
            method, endpoint, json=data, headers=headers, 
            timeout=timeout, verify=True
        )
        return response
    except requests.exceptions.SSLError:
        raise SecurityError("SSL certificate verification failed")
```

### Event Publishing Safety
```python
def safe_event_publish(event_type, data, tenant_id, correlation_id):
    """Safely publish events with validation"""
    
    # Validate event type format
    ALLOWED_EVENT_PATTERNS = [
        "assistant.activity", "assistant.error", "assistant.status"
    ]
    
    if not any(event_type.startswith(pattern) for pattern in ALLOWED_EVENT_PATTERNS):
        raise SecurityError(f"Event type {event_type} not allowed")
    
    # Sanitize event data
    safe_data = sanitize_data_for_logging(data)
    
    # Add security metadata
    event_payload = {
        "event_type": event_type,
        "tenant_id": tenant_id,
        "data": safe_data,
        "correlation_id": correlation_id,
        "source": "assistant",
        "timestamp": datetime.utcnow().isoformat(),
        "security_level": "internal"
    }
    
    return publish_to_eventbus(event_payload)
```

## Error Handling Guardrails

### Safe Error Responses
```python
def handle_error_safely(error, user_context):
    """Handle errors without exposing sensitive information"""
    
    # Never expose internal error details to users
    SAFE_ERROR_MESSAGES = {
        "PermissionError": "You don't have permission to perform this action.",
        "ValidationError": "The provided information is invalid.",
        "RateLimitError": "You've exceeded the rate limit. Please try again later.",
        "TimeoutError": "The operation timed out. Please try again.",
        "ServiceError": "A service is temporarily unavailable."
    }
    
    error_type = type(error).__name__
    safe_message = SAFE_ERROR_MESSAGES.get(error_type, 
                                          "An unexpected error occurred.")
    
    # Log full error details securely (without sensitive data)
    log_assistant_error({
        "error_type": error_type,
        "safe_message": safe_message,
        "tenant_id": user_context.get("tenant_id"),
        "user_id": user_context.get("user_id"),
        "timestamp": datetime.utcnow().isoformat(),
        "correlation_id": generate_correlation_id()
    })
    
    return {
        "error": True,
        "message": safe_message,
        "suggestion": "Please contact your system administrator if the problem persists."
    }
```

### Circuit Breaker Pattern
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    def call_service(self, service_func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half_open"
            else:
                raise ServiceUnavailableError("Circuit breaker open")
        
        try:
            result = service_func(*args, **kwargs)
            if self.state == "half_open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            
            raise e
```

## Compliance and Audit Guardrails

### Activity Logging Requirements
```python
def log_assistant_activity(intent, action_data, result, user_context):
    """Log all assistant activities for compliance"""
    
    activity_log = {
        "event_type": "assistant.activity",
        "tenant_id": user_context["tenant_id"],
        "user_id": user_context["user_id"],
        "data": {
            "intent": intent,
            "action_requested": action_data.get("action_type"),
            "parameters": sanitize_data_for_logging(action_data),
            "result_status": result.get("status", "unknown"),
            "confidence_score": result.get("confidence", 0.0),
            "decision_rationale": result.get("rationale"),
            "correlation_id": generate_correlation_id(),
            "ip_address": get_client_ip(user_context),
            "user_agent": get_user_agent(user_context)
        },
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0"
    }
    
    # Store in secure audit log
    publish_to_audit_log(activity_log)
```

**Audit Requirements**:
- ✅ Log ALL assistant actions and decisions
- ✅ Include user identification and tenant context
- ✅ Record decision rationale and confidence
- ✅ Maintain correlation IDs for tracing
- ✅ Store logs in tamper-evident format
- ❌ NEVER modify or delete audit logs

### Data Retention Compliance
```python
DATA_RETENTION_POLICIES = {
    "assistant_activities": "7_years",  # ISO 22301 compliance
    "user_interactions": "3_years",    # Privacy regulation
    "error_logs": "1_year",           # Technical troubleshooting
    "performance_metrics": "2_years",  # Operational analysis
    "temporary_cache": "24_hours"     # Performance optimization
}

def enforce_data_retention():
    """Automatically purge data per retention policies"""
    current_time = datetime.utcnow()
    
    for data_type, retention_period in DATA_RETENTION_POLICIES.items():
        if retention_period == "24_hours":
            cutoff = current_time - timedelta(hours=24)
        elif retention_period == "1_year":
            cutoff = current_time - timedelta(days=365)
        # ... implement other periods
        
        purge_expired_data(data_type, cutoff)
```

## Emergency Safety Measures

### Kill Switch Implementation
```python
def check_emergency_stop():
    """Check for emergency stop conditions"""
    
    # Check for emergency stop signals
    emergency_conditions = [
        check_security_breach_indicators(),
        check_system_overload(),
        check_compliance_violations(),
        check_admin_stop_signal()
    ]
    
    if any(emergency_conditions):
        engage_emergency_stop()
        return True
    
    return False

def engage_emergency_stop():
    """Immediately halt all assistant operations"""
    
    # Stop all API calls
    disable_api_access()
    
    # Clear sensitive data from memory
    clear_all_caches()
    
    # Log emergency stop
    log_emergency_event({
        "event_type": "assistant.emergency_stop",
        "timestamp": datetime.utcnow().isoformat(),
        "reason": "Safety guardrail triggered"
    })
    
    # Notify administrators
    send_emergency_notification()
```

### Rollback Capabilities
```python
def safe_rollback(correlation_id):
    """Rollback assistant actions if problems detected"""
    
    # Find all actions for correlation ID
    related_actions = get_actions_by_correlation(correlation_id)
    
    for action in related_actions:
        if action["status"] == "draft":
            # Mark draft as cancelled
            cancel_draft(action["draft_id"])
        elif action["status"] == "requested":
            # Cancel pending request
            cancel_orchestrator_request(action["request_id"])
    
    # Log rollback activity
    log_rollback_event(correlation_id, related_actions)
```

## Monitoring and Alerting

### Anomaly Detection
```python
def detect_anomalous_behavior(user_context, action_pattern):
    """Monitor for unusual assistant usage patterns"""
    
    anomaly_indicators = [
        check_unusual_volume(user_context["user_id"]),
        check_off_hours_usage(user_context["timestamp"]),
        check_rapid_fire_requests(user_context["session_id"]),
        check_privilege_escalation_attempts(action_pattern),
        check_cross_tenant_probing(user_context["tenant_id"])
    ]
    
    if any(anomaly_indicators):
        alert_security_team({
            "user_id": user_context["user_id"],
            "tenant_id": user_context["tenant_id"],
            "anomaly_type": anomaly_indicators,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Temporarily increase monitoring for this user
        enable_enhanced_monitoring(user_context["user_id"])
```

**Monitoring Thresholds**:
- 🚨 >100 API calls per hour
- 🚨 Off-hours usage (outside 6 AM - 10 PM local time)
- 🚨 >10 failed authentication attempts
- 🚨 Attempts to access unauthorized tenants
- 🚨 Repeated system error patterns

---

## Guardrail Enforcement

These guardrails are enforced at multiple layers:

1. **Input Layer**: Validate and sanitize all user inputs
2. **Logic Layer**: Ensure business rule compliance
3. **Integration Layer**: Secure API calls and event publishing
4. **Output Layer**: Safe error handling and response formatting
5. **Audit Layer**: Comprehensive logging and monitoring

**Critical**: Any violation of these guardrails must result in immediate action termination and security alert generation. The safety and security of organizational BCM data is paramount.
