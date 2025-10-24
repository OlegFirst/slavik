# Security Hardening Checklist - 79 → 95/100

**Date:** 2025-10-21
**Target Score:** 95/100 (from 79/100)
**Status:** IN PROGRESS

---

## 🎯 Security Score Breakdown

### Current State (79/100):
- ✅ RLS Policies: 90/100 (excellent)
- ✅ Database Structure: 85/100 (good)
- ⚠️ CORS Configuration: 40/100 (poor - wildcard origins)
- ⚠️ TLS/HTTPS Enforcement: 60/100 (partial)
- ⚠️ Secrets Management: 50/100 (plaintext in .env)
- ⚠️ JWT Configuration: 70/100 (weak secrets)

### Target State (95/100):
- ✅ RLS Policies: 90/100 (maintain)
- ✅ Database Structure: 85/100 (maintain)
- ✅ CORS Configuration: 95/100 (strict origins)
- ✅ TLS/HTTPS Enforcement: 100/100 (full enforcement)
- ✅ Secrets Management: 90/100 (Vault integration)
- ✅ JWT Configuration: 95/100 (strong secrets, rotation)

---

## 🔴 CRITICAL FIXES (HIGH PRIORITY)

### 1. CORS Configuration ⚠️ CRITICAL

**Problem:** 20+ services using `allow_origins=["*"]` (wildcard)

**Files Affected:**
- infrastructure/ace_service/main.py
- infrastructure/policy_engine/governance_api.py
- infrastructure/observability/notification_service/main.py
- infrastructure/runtime/service_discovery/main.py
- infrastructure/runtime/service_registry_management/main.py
- infrastructure/runtime/message_queue/main.py
- (14+ more files)

**Solution Created:**
✅ `/infrastructure/security/cors_config.py` - Centralized CORS configuration

**Action Required:**
```python
# BEFORE (INSECURE):
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ VULNERABLE
    allow_credentials=True,
)

# AFTER (SECURE):
from infrastructure.security.cors_config import get_fastapi_cors_middleware_params

app.add_middleware(
    CORSMiddleware,
    **get_fastapi_cors_middleware_params()  # ✅ SECURE
)
```

**Status:** ⏳ Configuration created, needs deployment to services

---

### 2. TLS/HTTPS Enforcement ⚠️ CRITICAL

**Problem:** TLS configured only in some ingresses, not enforced everywhere

**Current State:**
- ✅ orchestration-ingress.yaml: TLS enabled
- ⚠️ Other services: No TLS configuration
- ❌ Internal service communication: HTTP (not HTTPS)

**Solution:**

**A. Update All Ingress Configs:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
    - hosts:
        - api.bcm.ai
      secretName: bcm-tls-cert
```

**B. Require HTTPS in Application Code:**
```python
# Add to all FastAPI apps
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

**Status:** ⏳ Template created, needs deployment

---

### 3. Secrets Management (Vault Migration) ⚠️ CRITICAL

**Problem:** Secrets in plaintext .env files:
- ANTHROPIC_API_KEY
- OPENAI_API_KEY
- JWT_SECRET_KEY
- DATABASE_URL (contains password)
- REDIS_PASSWORD
- SUPABASE_SERVICE_ROLE_KEY

**Solution:** Supabase Vault Integration

**Step 1: Enable Vault (DONE ✅ in Supabase)**
```sql
CREATE EXTENSION IF NOT EXISTS vault;
```

**Step 2: Migrate Secrets**
```sql
-- Store secrets in Vault
SELECT vault.create_secret('sk-ant-api03-...', 'anthropic-api-key');
SELECT vault.create_secret('sk-...', 'openai-api-key');
SELECT vault.create_secret('your-jwt-secret', 'jwt-secret-key');
SELECT vault.create_secret('redis-password', 'redis-password');
```

**Step 3: Update Application Code**
```python
# infrastructure/security/vault_client.py (TO BE CREATED)
from supabase import create_client
import os

class VaultClient:
    def __init__(self):
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Only this in .env
        )

    def get_secret(self, name: str) -> str:
        """Retrieve secret from Vault"""
        result = self.supabase.rpc(
            "vault.get_secret",
            {"secret_name": name}
        ).execute()
        return result.data

# Usage:
vault = VaultClient()
anthropic_key = vault.get_secret("anthropic-api-key")
```

**Status:** ⏳ Plan created, needs implementation

---

### 4. JWT Secret Strength ⚠️ HIGH

**Problem:**
- Default JWT secrets in some configs
- No rotation mechanism
- Stored in plaintext .env

**Current JWT Secrets:**
- `dev-secret-CHANGE-IN-PRODUCTION-12345` ❌ WEAK
- Various hardcoded values ❌ INSECURE

**Solution:**

**A. Generate Strong Secrets:**
```bash
# Generate 256-bit secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Example: Xk7mP9qR3tY8wA2nF5vL1bN4cD6gH0jK9
```

**B. Store in Vault:**
```sql
SELECT vault.create_secret('Xk7mP9qR3tY8wA2nF5vL1bN4cD6gH0jK9', 'jwt-secret-key');
```

**C. Implement Rotation:**
```python
# Rotate JWT secret every 90 days
# Store both current and previous for graceful rotation
```

**Status:** ⏳ Needs implementation

---

## 🟡 MEDIUM PRIORITY

### 5. API Rate Limiting Enhancement

**Current:** Basic rate limiting in gateway
**Enhancement:** Per-endpoint, per-user rate limits

```python
# Enhanced rate limiting
RATE_LIMITS = {
    "/api/v1/auth/login": "5/minute",  # Login attempts
    "/api/v1/auth/register": "3/hour",  # Registration
    "/api/v1/*": "100/minute",  # Default
    "/api/v1/bia/*": "500/minute",  # BIA operations
}
```

**Status:** ⏳ Planned

---

### 6. Security Headers Enhancement

**Current:** Basic security headers in gateway
**Enhancement:** Complete OWASP recommended headers

```python
SECURITY_HEADERS = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "X-Permitted-Cross-Domain-Policies": "none",
}
```

**Status:** ⏳ Partial implementation, needs completion

---

### 7. Input Validation & Sanitization

**Current:** Basic Pydantic validation
**Enhancement:** SQL injection, XSS, path traversal prevention

**Created:** `/tests/security/test_security_suite.py` (has validation tests ✅)

**Needs:**
- Implement sanitization middleware
- Add to all FastAPI services
- Test against OWASP Top 10

**Status:** ⏳ Tests exist, implementation needed

---

## 🟢 LOW PRIORITY (Nice to Have)

### 8. Audit Logging Enhancement

**Current:** Basic audit logs
**Enhancement:** Complete audit trail with:
- All API requests
- Authentication events
- Data access logs
- Admin actions
- Security events

**Status:** ⏳ Planned

---

### 9. Penetration Testing

**Action:** Run automated security scanning
```bash
# OWASP ZAP scan
docker run -t owasp/zap2docker-stable zap-baseline.py -t https://api.bcm.ai

# Nmap scan
nmap -sV -sC api.bcm.ai

# SSL Labs test
https://www.ssllabs.com/ssltest/
```

**Status:** ⏳ Not started

---

### 10. Security Documentation

**Create:**
- Security incident response plan
- Vulnerability disclosure policy
- Security best practices guide
- Compliance documentation (ISO 27001, SOC 2)

**Status:** ⏳ Not started

---

## 📊 Implementation Tracking

### Phase 1: Critical Fixes (Week 1) - IN PROGRESS

| Task | Status | Assignee | Due Date |
|------|--------|----------|----------|
| 1. CORS Configuration | ✅ Config Created | SELF | 2025-10-21 |
| 1. CORS Deployment | ⏳ Pending | Agent 6 | 2025-10-22 |
| 2. TLS/HTTPS Template | ✅ Created | SELF | 2025-10-21 |
| 2. TLS Deployment | ⏳ Pending | Agent 7 | 2025-10-23 |
| 3. Vault Integration | ⏳ In Progress | SELF | 2025-10-24 |
| 4. JWT Secret Rotation | ⏳ Pending | SELF | 2025-10-24 |

### Phase 2: Medium Priority (Week 2)

| Task | Status | Due Date |
|------|--------|----------|
| 5. Enhanced Rate Limiting | ⏳ Pending | 2025-10-28 |
| 6. Security Headers | ⏳ Pending | 2025-10-28 |
| 7. Input Validation | ⏳ Pending | 2025-10-29 |

### Phase 3: Low Priority (Month 2)

| Task | Status | Due Date |
|------|--------|----------|
| 8. Audit Logging | ⏳ Pending | 2025-11-15 |
| 9. Penetration Testing | ⏳ Pending | 2025-11-20 |
| 10. Security Documentation | ⏳ Pending | 2025-11-30 |

---

## 🎯 Success Criteria

### Must Have (95/100 target):
- ✅ No wildcard CORS origins in production
- ✅ All services enforce HTTPS/TLS
- ✅ Secrets in Vault (not plaintext)
- ✅ Strong JWT secrets with rotation
- ✅ Complete security headers
- ✅ Input validation & sanitization

### Nice to Have (100/100):
- ✅ Complete audit logging
- ✅ Passed penetration testing
- ✅ Security documentation complete
- ✅ Automated security scanning in CI/CD

---

## 📝 Next Steps

### Immediate (Today):
1. ✅ Create CORS configuration module
2. ✅ Create TLS/HTTPS templates
3. ⏳ Implement Vault client
4. ⏳ Deploy CORS config to services

### This Week:
1. Complete Vault migration
2. Rotate all JWT secrets
3. Deploy TLS everywhere
4. Enhanced security headers

### This Month:
1. Penetration testing
2. Security audit
3. Compliance documentation

---

**Last Updated:** 2025-10-21
**Maintained By:** Security Team
**Review Frequency:** Weekly
**Target Completion:** 2025-10-31 (95/100)
