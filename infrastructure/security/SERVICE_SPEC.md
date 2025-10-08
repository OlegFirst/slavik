# Security Infrastructure - Service Specification

**Last Updated:** 2025-10-07
**Status:** Production Ready (with noted gaps)
**Version:** 1.0.0

---

## Назначение

Централизованная инфраструктура безопасности для платформы BCM:
- **Authentication Service** - JWT-based аутентификация с Supabase
- **API Gateway** - Entry point с auth, rate limiting, audit
- **Secrets Manager** - HashiCorp Vault для управления секретами
- **Security Headers** - HTTP security middleware

---

## Технологии

### Authentication
- **Framework:** FastAPI
- **Auth Method:** JWT (HS256/RS256)
- **Provider:** Supabase Auth
- **Session Store:** Redis
- **Password Hashing:** bcrypt

### API Gateway
- **Framework:** FastAPI
- **Auth:** JWT middleware
- **Rate Limiting:** Redis (Sliding Window)
- **Audit:** PostgreSQL (Batch writes)

### Secrets Management
- **Technology:** HashiCorp Vault 1.15+
- **Client:** hvac (Python)
- **Features:** KV secrets, Dynamic DB creds, Encryption as a Service
- **Deployment:** Docker container

---

## Структура

```
security/
├── auth/                           # Authentication Service
│   ├── auth_service.py                 # Main service
│   ├── test_auth_service.py            # Tests
│   └── README.md
│
├── secrets-manager/                # HashiCorp Vault
│   ├── vault_manager.py                # Vault Python client
│   ├── requirements.txt
│   └── README.md
│
├── secrets-management/             # Setup guides
│   └── SETUP_GUIDE.md                  # Vault setup guide
│
├── README.md                       # Security overview
└── SECURITY_ROADMAP.md             # Implementation roadmap
```

---

## Authentication Service

### Purpose
Централизованная аутентификация и управление пользователями.

### Features
- **JWT Token Generation** - Access + Refresh tokens
- **Supabase Integration** - Sync с Supabase Auth
- **RLS Context** - Set tenant_id для Row Level Security
- **Session Management** - Redis session store
- **Password Management** - bcrypt hashing
- **Role-Based Access Control** - admin, user, viewer, api

### API Endpoints

**POST /auth/login**
```json
{
  "email": "user@example.com",
  "password": "password",
  "organization_domain": "optional"
}

Response:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "user"
  },
  "organization": {...}
}
```

**POST /auth/signup**
```json
{
  "email": "user@example.com",
  "password": "password",
  "full_name": "John Doe",
  "organization_name": "Acme Corp"
}
```

**GET /auth/me**
- Requires: Authorization header
- Returns: Current user info

**POST /auth/refresh**
```json
{
  "refresh_token": "eyJ..."
}
```

**POST /auth/logout**
- Revokes tokens and clears session

### JWT Token Structure

```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "user",
  "tenant_id": "tenant_uuid",
  "organization_id": "org_uuid",
  "exp": 1633024800,
  "iat": 1632938400,
  "jti": "token_id"
}
```

### Configuration

```bash
# Environment variables
JWT_SECRET_KEY=<generate-strong-secret>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440  # 24 hours

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...

# Redis
REDIS_URL=redis://localhost:6379

# Database
DATABASE_URL=postgresql://...

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Usage

**Python Client:**
```python
import httpx

# Login
response = httpx.post('http://localhost:8001/auth/login', json={
    'email': 'user@example.com',
    'password': 'password'
})

data = response.json()
access_token = data['access_token']

# Use token
headers = {'Authorization': f'Bearer {access_token}'}
response = httpx.get('http://localhost:8000/api/v1/bia/processes', headers=headers)
```

**JavaScript Client:**
```javascript
// Login
const response = await fetch('http://localhost:8001/auth/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        email: 'user@example.com',
        password: 'password'
    })
});

const {access_token} = await response.json();

// Use token
const data = await fetch('http://localhost:8000/api/v1/bia/processes', {
    headers: {'Authorization': `Bearer ${access_token}`}
});
```

---

## Secrets Manager (HashiCorp Vault)

### Purpose
Безопасное хранение и управление секретами (API keys, passwords, tokens).

### Features
- **KV Secrets v2** - Versioned static secrets
- **Dynamic Secrets** - Temporary database credentials
- **Encryption as a Service** - Transit engine для шифрования данных
- **Token Management** - Token lifecycle, renewal, revocation
- **Audit Logging** - Все операции логируются
- **Auto-renewal** - Automatic lease renewal

### Setup

```bash
# Run Vault (Dev mode)
docker run -d \
  --name vault \
  -p 8200:8200 \
  -e VAULT_DEV_ROOT_TOKEN_ID=root-token \
  hashicorp/vault:1.15 server -dev

# Production setup
docker run -d \
  --name vault \
  -p 8200:8200 \
  -v vault-data:/vault/data \
  hashicorp/vault:1.15 server -config=/vault/config/vault.hcl
```

### Usage

**KV Secrets:**
```python
from vault_manager import get_vault_manager

vault = get_vault_manager(
    url="http://localhost:8200",
    token="root-token"
)

# Write secret
vault.write_secret("database/postgres", {
    "host": "localhost",
    "port": 5432,
    "username": "admin",
    "password": "super-secret-password"
})

# Read secret
db_config = vault.read_secret("database/postgres")
print(f"DB Password: {db_config['password']}")

# List secrets
secrets = vault.list_secrets("database")
# Returns: ["postgres", "mysql", "redis"]

# Delete secret
vault.delete_secret("database/old-db")
```

**Encryption as a Service:**
```python
# Create encryption key
vault.create_encryption_key(
    name="customer-data-key",
    key_type="aes256-gcm96"
)

# Encrypt data
plaintext = "John Doe, SSN: 123-45-6789"
ciphertext = vault.encrypt("customer-data-key", plaintext)
# Output: vault:v1:8SDd3WHDOj...

# Decrypt data
decrypted = vault.decrypt("customer-data-key", ciphertext)
# Output: John Doe, SSN: 123-45-6789
```

**Dynamic Database Credentials:**
```python
# Configure database connection
vault.configure_database(
    name="bcm-postgres",
    plugin_name="postgresql-database-plugin",
    connection_url="postgresql://{{username}}:{{password}}@localhost:5432/bcm",
    allowed_roles=["readonly", "readwrite"],
    username="vault",
    password="vault-password"
)

# Create role
vault.create_database_role(
    name="readonly",
    db_name="bcm-postgres",
    creation_statements=[
        "CREATE USER '{{name}}' WITH PASSWORD '{{password}}';",
        "GRANT SELECT ON ALL TABLES IN SCHEMA public TO '{{name}}';"
    ],
    default_ttl="1h",
    max_ttl="24h"
)

# Get temporary credentials
creds = vault.get_database_credentials("readonly")
# Returns: {'username': 'v-root-readonly-AbC123...', 'password': 'XyZ789...'}
# Credentials expire in 1 hour!
```

**Token Management:**
```python
# Create token
app_token = vault.create_token(
    policies=["app-read", "app-write"],
    ttl="24h",
    renewable=True
)

# Renew token
renewed = vault.renew_token(app_token['client_token'], increment="24h")

# Revoke token
vault.revoke_token(app_token['client_token'])
```

### Security Best Practices

1. **Never use Dev mode in production**
2. **Initialize and unseal Vault properly**
3. **Use AppRole or K8s auth instead of root token**
4. **Enable audit logging**
5. **Regular key rotation**
6. **Backup Vault data**
7. **Use TLS for all connections**

---

## API Gateway Security

### Features (from gateway/SERVICE_SPEC.md)
- JWT Authentication
- Rate Limiting (Redis)
- Audit Logging (PostgreSQL)
- RBAC Authorization
- Circuit Breaker
- Security Headers

### Security Headers

```python
{
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}
```

### Rate Limiting

**Algorithm:** Sliding Window (Redis)
- Default: 100 req/60s
- VIP: 500 req/60s
- Burst: +20 requests

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1633024800
```

### Audit Logging

**Logged Events:**
- All API requests
- Authentication attempts
- Authorization failures
- Rate limit violations
- Errors

**Schema:**
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMPTZ,
    user_id UUID,
    tenant_id UUID,
    method VARCHAR(10),
    path VARCHAR(500),
    status_code INTEGER,
    response_time_ms INTEGER,
    ip_address INET,
    user_agent TEXT
);
```

---

## Configuration

### Authentication Service

```bash
# Auth Service
JWT_SECRET_KEY=<generate-64-char-secret>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...

# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=<if-required>

# Database
DATABASE_URL=postgresql://...

# CORS
CORS_ORIGINS=http://localhost:3000
```

### Vault

```bash
# Vault
VAULT_ADDR=http://localhost:8200
VAULT_TOKEN=<vault-token>  # Use AppRole in production

# Mount point
VAULT_MOUNT_POINT=secret  # KV v2
```

### API Gateway

```bash
# JWT
JWT_SECRET=<same-as-auth-service>
JWT_ALGORITHM=HS256

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Audit
AUDIT_ENABLED=true
AUDIT_RETENTION_DAYS=90

# Database
DATABASE_URL=postgresql://...

# Redis
REDIS_URL=redis://localhost:6379
```

---

## Развертывание

### Docker Compose

```yaml
version: '3.8'

services:
  # Auth Service
  auth-service:
    build: ./auth
    ports:
      - "8001:8001"
    environment:
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
    depends_on:
      - redis
      - postgres

  # Vault
  vault:
    image: hashicorp/vault:1.15
    ports:
      - "8200:8200"
    volumes:
      - vault-data:/vault/data
      - ./vault-config.hcl:/vault/config/vault.hcl
    cap_add:
      - IPC_LOCK
    command: server -config=/vault/config/vault.hcl

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

volumes:
  vault-data:
  redis-data:
```

### Standalone

```bash
# Auth Service
cd infrastructure/security/auth
pip install -r requirements.txt
python auth_service.py

# Vault
docker run -d -p 8200:8200 \
  -e VAULT_DEV_ROOT_TOKEN_ID=root-token \
  hashicorp/vault:1.15 server -dev
```

---

## Безопасность

### Critical Security Measures

1. **JWT Secrets:**
   - Generate: `python -c "import secrets; print(secrets.token_urlsafe(64))"`
   - Never commit to git
   - Rotate regularly (90 days)
   - Use RS256 for production (public/private key)

2. **Password Hashing:**
   - Algorithm: bcrypt (rounds=12)
   - Never store plaintext passwords
   - Enforce password complexity

3. **Token Expiration:**
   - Access token: 24 hours
   - Refresh token: 30 days
   - Implement token revocation list

4. **HTTPS Only:**
   - Force HTTPS in production
   - HSTS header enabled
   - Certificate pinning

5. **Rate Limiting:**
   - Prevent brute force attacks
   - DDoS protection
   - Per-user and per-IP limits

6. **Audit Logging:**
   - Log all auth events
   - Monitor for suspicious activity
   - Retention: 90 days minimum

7. **Secrets Management:**
   - Use Vault for all secrets
   - Never hardcode secrets
   - Regular secret rotation
   - Encrypt secrets at rest

---

## Мониторинг

### Auth Service Metrics

```promql
# Login attempts
rate(auth_login_attempts_total[5m])

# Failed logins
rate(auth_login_failures_total[5m])

# Token generations
rate(auth_tokens_generated_total[5m])

# Active sessions
auth_active_sessions
```

### Vault Metrics

```bash
# Vault status
curl http://localhost:8200/v1/sys/health

# Sealed status
curl http://localhost:8200/v1/sys/seal-status

# Metrics (requires auth)
curl -H "X-Vault-Token: $VAULT_TOKEN" \
  http://localhost:8200/v1/sys/metrics
```

### Security Alerts

```yaml
# AlertManager rules
- alert: HighFailedLogins
  expr: rate(auth_login_failures_total[5m]) > 10
  labels:
    severity: warning
  annotations:
    summary: "High rate of failed logins"

- alert: VaultSealed
  expr: vault_core_unsealed == 0
  labels:
    severity: critical
  annotations:
    summary: "Vault is sealed!"

- alert: RateLimitExceeded
  expr: rate(gateway_rate_limit_exceeded_total[5m]) > 100
  labels:
    severity: warning
  annotations:
    summary: "High rate of rate limit violations"
```

---

## Проблемы/TODO

### Critical Issues

1. **RS256 Migration:**
   - [ ] Migrate from HS256 to RS256 (public/private keys)
   - [ ] Implement key rotation
   - [ ] Create key management process

2. **Token Revocation:**
   - [ ] Implement token blacklist (Redis)
   - [ ] Add revocation endpoint
   - [ ] Background cleanup job

3. **MFA (Multi-Factor Authentication):**
   - [ ] Add TOTP support (Google Authenticator)
   - [ ] SMS OTP integration
   - [ ] Recovery codes

### Improvements Needed

1. **Authentication:**
   - [ ] Add OAuth2 support (Google, GitHub)
   - [ ] Implement SSO (SAML)
   - [ ] Add API key authentication для M2M
   - [ ] Implement password reset flow
   - [ ] Add account lockout после N failed attempts

2. **Authorization:**
   - [ ] Fine-grained permissions (beyond roles)
   - [ ] Resource-based access control
   - [ ] Policy engine (OPA integration)
   - [ ] Attribute-based access control (ABAC)

3. **Secrets Management:**
   - [ ] Auto-rotate secrets
   - [ ] Integrate with cloud KMS (AWS/Azure)
   - [ ] Add secret scanning в CI/CD
   - [ ] Implement secret expiration policies

4. **Audit & Compliance:**
   - [ ] GDPR compliance features
   - [ ] SOC2 compliance logging
   - [ ] Automated security scans
   - [ ] Penetration testing integration

5. **Infrastructure:**
   - [ ] WAF (Web Application Firewall)
   - [ ] IDS/IPS integration
   - [ ] DDoS protection (Cloudflare)
   - [ ] Security information and event management (SIEM)

---

## Security Checklist

### Production Deployment

- [ ] **Secrets:** All secrets in Vault, none in code/env files
- [ ] **HTTPS:** Force HTTPS, HSTS enabled
- [ ] **JWT:** Use RS256, rotate keys regularly
- [ ] **Passwords:** Strong policy (12+ chars, complexity)
- [ ] **Rate Limiting:** Enabled on all endpoints
- [ ] **Audit Logging:** All auth events logged
- [ ] **CORS:** Whitelist only, no wildcards
- [ ] **Security Headers:** All headers configured
- [ ] **MFA:** Available for admin accounts
- [ ] **Token Expiration:** Access 24h, Refresh 30d
- [ ] **Session Timeout:** Idle timeout 30min
- [ ] **Firewall:** Restrict to trusted IPs
- [ ] **Monitoring:** Security alerts configured
- [ ] **Backup:** Vault data backed up daily
- [ ] **Updates:** Security patches applied

---

## Quick Reference

### Generate JWT Secret

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### Test Login

```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

### Store Secret in Vault

```bash
vault kv put secret/database/postgres \
  host=localhost \
  port=5432 \
  username=admin \
  password=secret
```

### Read Secret from Vault

```bash
vault kv get secret/database/postgres
```

### Check Auth Service Health

```bash
curl http://localhost:8001/health
```

### Vault Health Check

```bash
curl http://localhost:8200/v1/sys/health
```

---

**STATUS:** Production Ready (with improvements needed)
**READY FOR:** MVP deployment
**BLOCKERS:** MFA, RS256 migration recommended before full production
