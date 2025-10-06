# 🛡️ SECURITY IMPLEMENTATION ROADMAP

**Timeline:** 3 weeks
**Status:** Not started
**Priority:** URGENT

---

## 📅 WEEK 1: API GATEWAY + AUTHENTICATION

### Day 1-2: API Gateway Setup
**Goal:** Implement centralized API Gateway

**Tasks:**
- [ ] Choose technology (FastAPI vs Kong vs Traefik)
- [ ] Create gateway service structure
- [ ] Configure routing rules
- [ ] Add health check endpoint
- [ ] Docker + Kubernetes manifests

**Deliverables:**
- `security/api-gateway/main.py`
- `security/api-gateway/Dockerfile`
- Gateway running on port 8000

---

### Day 3-4: JWT Authentication
**Goal:** Secure all service endpoints

**Tasks:**
- [ ] Create JWT auth middleware
- [ ] Integrate with auth-service (port TBD)
- [ ] Token validation logic
- [ ] Public endpoints whitelist
- [ ] Error handling (401, 403)

**Deliverables:**
- `security/api-gateway/auth_middleware.py`
- All requests require valid JWT
- Auth-service integration working

---

### Day 5: Rate Limiting
**Goal:** Prevent DDoS and abuse

**Tasks:**
- [ ] Redis-based rate limiter
- [ ] Sliding window algorithm
- [ ] Per-user rate limits
- [ ] Per-IP rate limits
- [ ] Rate limit headers (X-RateLimit-*)

**Deliverables:**
- `security/api-gateway/rate_limiter.py`
- Redis integration
- 100 requests/minute per user

---

## 📅 WEEK 2: PERSISTENT SECURITY

### Day 1-2: Audit Logging to PostgreSQL
**Goal:** Persistent, queryable audit trail

**Tasks:**
- [ ] Create audit_logs table
- [ ] Migrate AuditLogger from memory to PostgreSQL
- [ ] Index for fast queries
- [ ] Retention policy (90 days)
- [ ] Query API endpoints

**Database Schema:**
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id VARCHAR(255),
    action VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    tenant_id VARCHAR(255) NOT NULL,
    details JSONB,
    status VARCHAR(50) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_tenant_id ON audit_logs(tenant_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_execution_id ON audit_logs(execution_id);
```

**Deliverables:**
- `persistent-security/audit_logger.py`
- PostgreSQL migration
- Coordination Center updated

---

### Day 3: Rate Limiter to Redis
**Goal:** Distributed, persistent rate limiting

**Tasks:**
- [ ] Migrate RateLimiter from memory to Redis
- [ ] Sliding window with Redis sorted sets
- [ ] TTL-based cleanup
- [ ] Atomic operations
- [ ] Cluster-ready

**Redis Implementation:**
```python
# Sliding window rate limiter
async def check_rate_limit(user_id: str, window_seconds: int = 60, max_requests: int = 100):
    now = time.time()
    window_start = now - window_seconds

    key = f"rate_limit:{user_id}"

    # Remove old entries
    await redis.zremrangebyscore(key, 0, window_start)

    # Count requests in window
    count = await redis.zcard(key)

    if count >= max_requests:
        return False, "Rate limit exceeded"

    # Add current request
    await redis.zadd(key, {str(now): now})
    await redis.expire(key, window_seconds)

    return True, None
```

**Deliverables:**
- `persistent-security/rate_limiter_redis.py`
- Redis integration
- Load test passing

---

### Day 4-5: Update Coordination Center
**Goal:** Use new persistent security components

**Tasks:**
- [ ] Replace in-memory AuditLogger
- [ ] Replace in-memory RateLimiter
- [ ] Update SecurityLayer
- [ ] Migration script for existing data (if any)
- [ ] Integration tests

**Deliverables:**
- coordination-center updated
- Tests passing
- No data loss

---

## 📅 WEEK 3: SECRETS + HARDENING

### Day 1-2: Secrets Management
**Goal:** Secure storage of sensitive data

**Option A: HashiCorp Vault**
```bash
# Install Vault
docker run -d --name vault \
  -p 8200:8200 \
  vault:latest

# Initialize
vault operator init

# Store secrets
vault kv put secret/bcm/postgres password="$(openssl rand -base64 32)"
vault kv put secret/bcm/jwt secret="$(openssl rand -base64 64)"
vault kv put secret/bcm/redis password="$(openssl rand -base64 32)"
```

**Option B: Kubernetes External Secrets**
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: bcm-secrets
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: bcm-secrets
    creationPolicy: Owner
  data:
    - secretKey: postgres_password
      remoteRef:
        key: secret/bcm/postgres
        property: password
```

**Tasks:**
- [ ] Choose secrets solution (Vault vs K8s vs Cloud)
- [ ] Setup infrastructure
- [ ] Migrate secrets from .env
- [ ] Update all services to read from secrets store
- [ ] Rotate all secrets
- [ ] Document secrets management

**Deliverables:**
- Secrets infrastructure running
- All services using secure secrets
- Documentation

---

### Day 3: Security Headers Middleware
**Goal:** Protect against common web attacks

**Headers to implement:**
```python
SECURITY_HEADERS = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}
```

**Tasks:**
- [ ] Create security headers middleware
- [ ] Add to API Gateway
- [ ] Configure per-service CSP
- [ ] Test with security scanner

**Deliverables:**
- `security-headers/middleware.py`
- All services protected
- Security scan passing

---

### Day 4: CORS Configuration
**Goal:** Lock down cross-origin access

**Tasks:**
- [ ] Define allowed origins per environment
- [ ] Update CORS middleware in all services
- [ ] Test with frontend
- [ ] Document CORS policy

**Configuration:**
```python
# Production
ALLOWED_ORIGINS = [
    "https://app.bcm-platform.com",
    "https://admin.bcm-platform.com"
]

# Staging
ALLOWED_ORIGINS = [
    "https://staging.bcm-platform.com"
]

# Development
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080"
]
```

**Deliverables:**
- CORS properly configured
- No "*" wildcards in production
- Frontend integration working

---

### Day 5: Security Audit + Penetration Testing
**Goal:** Validate security implementation

**Tasks:**
- [ ] Run OWASP ZAP scan
- [ ] Run security linters (bandit, safety)
- [ ] Test authentication bypass
- [ ] Test rate limiting
- [ ] Test SQL injection
- [ ] Test XSS vulnerabilities
- [ ] Document findings
- [ ] Fix critical issues

**Tools:**
```bash
# Python security
pip install bandit safety
bandit -r infrastructure/
safety check

# OWASP ZAP
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:8000

# SQLMap (SQL injection testing)
sqlmap -u "http://localhost:8000/api/endpoint?param=value"
```

**Deliverables:**
- Security audit report
- All critical/high issues fixed
- Penetration test passing

---

## 📊 SUCCESS METRICS

### Security Score: **Target 9/10**

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Authentication | 2/10 🔴 | - | 9/10 🟢 |
| Authorization | 3/10 🔴 | - | 9/10 🟢 |
| Audit Logging | 2/10 🔴 | - | 9/10 🟢 |
| Rate Limiting | 3/10 🔴 | - | 9/10 🟢 |
| Secrets Mgmt | 2/10 🔴 | - | 9/10 🟢 |
| CORS | 2/10 🔴 | - | 8/10 🟢 |
| Headers | 4/10 🟡 | - | 9/10 🟢 |
| **OVERALL** | **4/10** 🔴 | - | **9/10** 🟢 |

---

## 🎯 DELIVERABLES CHECKLIST

### Week 1
- [ ] API Gateway service
- [ ] JWT auth middleware
- [ ] Redis rate limiter
- [ ] Gateway tests
- [ ] Documentation

### Week 2
- [ ] PostgreSQL audit logs
- [ ] Redis rate limiter
- [ ] Coordination Center migration
- [ ] Migration tests
- [ ] Documentation

### Week 3
- [ ] Secrets management
- [ ] Security headers
- [ ] CORS configuration
- [ ] Security audit
- [ ] Final documentation

---

## 🚨 RISKS & MITIGATION

### Risk 1: Breaking existing clients
**Mitigation:**
- Gradual rollout with feature flags
- Backwards compatibility period
- Clear migration guide for clients

### Risk 2: Performance impact (auth checks)
**Mitigation:**
- JWT verification is fast (~1ms)
- Redis rate limiting is fast (~2ms)
- Connection pooling to auth-service
- Cache JWT public keys

### Risk 3: Secrets migration errors
**Mitigation:**
- Test in staging first
- Keep .env as backup during migration
- Automated validation scripts
- Rollback plan

---

## 📖 DOCUMENTATION

### Required Documentation:
1. **API Gateway Guide**
   - How to call secured endpoints
   - JWT token format
   - Rate limit headers
   - Error responses

2. **Security Best Practices**
   - How to generate secure secrets
   - How to rotate credentials
   - How to audit access
   - Incident response procedure

3. **Developer Guide**
   - How to add new endpoints
   - How to configure CORS
   - How to test locally
   - How to debug auth issues

---

**Status:** Ready to start ✅
**Next Step:** Begin Week 1, Day 1 (API Gateway setup)
