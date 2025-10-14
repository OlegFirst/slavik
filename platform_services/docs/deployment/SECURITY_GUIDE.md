# Security Configuration Guide

## Overview

This guide provides comprehensive security configuration for the BCM Platform, covering authentication, authorization, encryption, network security, and compliance requirements.

## Security Architecture

### Defense in Depth Layers

```
┌─────────────────────────────────────────────┐
│  Layer 1: Network Security (Firewall/WAF)   │
├─────────────────────────────────────────────┤
│  Layer 2: TLS/SSL Encryption                │
├─────────────────────────────────────────────┤
│  Layer 3: API Gateway / Load Balancer       │
├─────────────────────────────────────────────┤
│  Layer 4: Authentication (JWT)              │
├─────────────────────────────────────────────┤
│  Layer 5: Authorization (RBAC)              │
├─────────────────────────────────────────────┤
│  Layer 6: Application Security              │
├─────────────────────────────────────────────┤
│  Layer 7: Database Encryption               │
├─────────────────────────────────────────────┤
│  Layer 8: Audit Logging                     │
└─────────────────────────────────────────────┘
```

## JWT Authentication

### RSA Key Generation

Generate 4096-bit RSA key pair for production:

```bash
# Generate private key
openssl genrsa -out jwt_private.key 4096

# Extract public key
openssl rsa -in jwt_private.key -pubout -out jwt_public.key

# Verify keys
openssl rsa -in jwt_private.key -check
openssl rsa -pubin -in jwt_public.key -text -noout

# Base64 encode for environment variables (single line)
JWT_PRIVATE_KEY=$(cat jwt_private.key | base64 | tr -d '\n')
JWT_PUBLIC_KEY=$(cat jwt_public.key | base64 | tr -d '\n')

# Store securely
chmod 600 jwt_private.key
chmod 644 jwt_public.key
```

### JWT Configuration

```bash
# Environment variables
JWT_ALGORITHM=RS256
JWT_EXPIRATION_HOURS=24
JWT_REFRESH_ENABLED=true
JWT_REFRESH_EXPIRATION_DAYS=30
JWT_ISSUER=bcm-platform
JWT_AUDIENCE=bcm-services
JWT_PUBLIC_KEY=<BASE64_ENCODED_PUBLIC_KEY>
JWT_PRIVATE_KEY=<BASE64_ENCODED_PRIVATE_KEY>
```

### JWT Token Structure

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_id_123",
    "email": "user@example.com",
    "roles": ["admin", "bcm_manager"],
    "permissions": ["read:plans", "write:plans", "delete:plans"],
    "organization_id": "org_456",
    "iss": "bcm-platform",
    "aud": "bcm-services",
    "exp": 1696348800,
    "iat": 1696262400,
    "jti": "unique_token_id"
  }
}
```

### Token Validation

```python
# Example token validation (Python)
import jwt
from datetime import datetime, timedelta

def validate_token(token: str, public_key: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience="bcm-services",
            issuer="bcm-platform",
            options={"verify_exp": True}
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")
```

## Secret Management

### HashiCorp Vault Integration

**Install Vault:**
```bash
# Download and install Vault
wget https://releases.hashicorp.com/vault/1.15.0/vault_1.15.0_linux_amd64.zip
unzip vault_1.15.0_linux_amd64.zip
sudo mv vault /usr/local/bin/

# Start Vault server (dev mode for testing)
vault server -dev

# Set environment
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='<dev_token>'
```

**Store Secrets:**
```bash
# Store database password
vault kv put secret/bcm/postgres \
    password="<secure_password>" \
    username="bcm_user"

# Store JWT keys
vault kv put secret/bcm/jwt \
    private_key=@jwt_private.key \
    public_key=@jwt_public.key

# Store API keys
vault kv put secret/bcm/external \
    smtp_password="<smtp_password>" \
    pagerduty_key="<pagerduty_key>"
```

**Retrieve Secrets:**
```bash
# Get single field
export POSTGRES_PASSWORD=$(vault kv get -field=password secret/bcm/postgres)

# Get all fields
vault kv get -format=json secret/bcm/postgres | jq -r '.data.data'
```

### AWS Secrets Manager

```bash
# Store secret
aws secretsmanager create-secret \
    --name bcm/postgres/password \
    --secret-string "<secure_password>"

# Retrieve secret
export POSTGRES_PASSWORD=$(aws secretsmanager get-secret-value \
    --secret-id bcm/postgres/password \
    --query SecretString \
    --output text)

# Rotate secret
aws secretsmanager rotate-secret \
    --secret-id bcm/postgres/password \
    --rotation-lambda-arn arn:aws:lambda:region:account:function:rotate
```

### Environment Variable Encryption

Use tools like `sops` or `age` to encrypt `.env` files:

```bash
# Install sops
brew install sops  # macOS
# or
wget https://github.com/mozilla/sops/releases/download/v3.8.0/sops-v3.8.0.linux

# Encrypt .env file
sops -e .env > .env.encrypted

# Decrypt for use
sops -d .env.encrypted > .env

# Use with Docker
sops -d .env.encrypted | docker-compose --env-file /dev/stdin up -d
```

## SSL/TLS Configuration

### Certificate Generation

**Self-Signed Certificate (Development):**
```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=bcm.yourdomain.com"

# Verify certificate
openssl x509 -in server.crt -text -noout
```

**Let's Encrypt (Production):**
```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d bcm.yourdomain.com -d api.yourdomain.com

# Certificates location: /etc/letsencrypt/live/bcm.yourdomain.com/
# - fullchain.pem  (certificate + intermediate)
# - privkey.pem    (private key)

# Auto-renewal cron job
0 0 * * * certbot renew --quiet && systemctl reload nginx
```

### nginx SSL Configuration

**nginx.conf:**
```nginx
server {
    listen 443 ssl http2;
    server_name bcm.yourdomain.com;

    # SSL Certificates
    ssl_certificate /etc/letsencrypt/live/bcm.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bcm.yourdomain.com/privkey.pem;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

    # Proxy to backend services
    location /api/planning/ {
        proxy_pass http://planning-service:8011/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/plans/ {
        proxy_pass http://plans-service:8023/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name bcm.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## Database Security

### Encryption at Rest

**PostgreSQL SSL Configuration:**
```bash
# Generate certificates
openssl req -new -x509 -days 365 -nodes -text \
    -out server.crt -keyout server.key \
    -subj "/CN=postgres"

chmod 600 server.key
chown postgres:postgres server.key server.crt

# Configure PostgreSQL (postgresql.conf)
ssl = on
ssl_cert_file = '/var/lib/postgresql/server.crt'
ssl_key_file = '/var/lib/postgresql/server.key'
ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL'
ssl_prefer_server_ciphers = on
```

**Enforce SSL Connections (pg_hba.conf):**
```
# Require SSL for all connections
hostssl    all             all             0.0.0.0/0               md5
hostssl    all             all             ::/0                    md5

# Reject non-SSL connections
hostnossl  all             all             0.0.0.0/0               reject
```

### Column-Level Encryption

```sql
-- Install pgcrypto extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create table with encrypted columns
CREATE TABLE sensitive_data (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    encrypted_ssn BYTEA,
    encrypted_card BYTEA,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert encrypted data
INSERT INTO sensitive_data (user_id, encrypted_ssn, encrypted_card)
VALUES (
    'user_123',
    pgp_sym_encrypt('123-45-6789', 'encryption_key'),
    pgp_sym_encrypt('4111111111111111', 'encryption_key')
);

-- Query encrypted data
SELECT
    user_id,
    pgp_sym_decrypt(encrypted_ssn, 'encryption_key') AS ssn,
    pgp_sym_decrypt(encrypted_card, 'encryption_key') AS card
FROM sensitive_data
WHERE user_id = 'user_123';
```

### Password Hashing

```python
# Use bcrypt for password hashing
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

## Network Security

### Firewall Configuration (UFW)

```bash
# Install UFW
sudo apt-get install ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (important!)
sudo ufw allow ssh
sudo ufw allow 22/tcp

# Allow HTTPS only
sudo ufw allow 443/tcp

# Allow from specific IP (admin access)
sudo ufw allow from 203.0.113.0/24 to any port 22

# Deny direct access to services (only via nginx)
sudo ufw deny 8011/tcp comment 'Planning Service - Use nginx'
sudo ufw deny 8023/tcp comment 'Plans Service - Use nginx'

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose
```

### iptables Rules

```bash
# Flush existing rules
sudo iptables -F
sudo iptables -X

# Default policies
sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP
sudo iptables -P OUTPUT ACCEPT

# Allow loopback
sudo iptables -A INPUT -i lo -j ACCEPT

# Allow established connections
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow SSH
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTPS
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Rate limiting (prevent brute force)
sudo iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m recent --set
sudo iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m recent --update --seconds 60 --hitcount 4 -j DROP

# Save rules
sudo iptables-save > /etc/iptables/rules.v4
```

### Docker Network Isolation

```yaml
# docker-compose.yml
networks:
  frontend:
    driver: bridge
    internal: false  # Internet access

  backend:
    driver: bridge
    internal: true   # No internet access

services:
  nginx:
    networks:
      - frontend
      - backend

  planning-service:
    networks:
      - backend  # No direct internet access

  postgres:
    networks:
      - backend  # Isolated from frontend
```

## Rate Limiting and DDoS Protection

### Application-Level Rate Limiting

```python
# Using Redis for rate limiting
from redis import Redis
from datetime import datetime, timedelta

def rate_limit(user_id: str, max_requests: int = 1000, period: int = 3600):
    redis = Redis(host='redis', port=6379)
    key = f"rate_limit:{user_id}:{datetime.now().hour}"

    current = redis.incr(key)
    if current == 1:
        redis.expire(key, period)

    if current > max_requests:
        raise Exception("Rate limit exceeded")

    return current
```

### nginx Rate Limiting

```nginx
# Define rate limit zones
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;

# Apply to locations
location /api/ {
    limit_req zone=api_limit burst=50 nodelay;
    limit_req_status 429;
    proxy_pass http://backend;
}

location /api/auth/login {
    limit_req zone=auth_limit burst=3 nodelay;
    limit_req_status 429;
    proxy_pass http://backend;
}
```

### Fail2Ban Configuration

```bash
# Install fail2ban
sudo apt-get install fail2ban

# Configure jail for nginx (/etc/fail2ban/jail.local)
[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 5
findtime = 600
bantime = 3600

# Create filter (/etc/fail2ban/filter.d/nginx-limit-req.conf)
[Definition]
failregex = limiting requests, excess: .* by zone ".*", client: <HOST>
ignoreregex =

# Restart fail2ban
sudo systemctl restart fail2ban
sudo fail2ban-client status nginx-limit-req
```

## Security Headers

### OWASP Recommended Headers

```nginx
# Strict-Transport-Security (HSTS)
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

# Content-Security-Policy (CSP)
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://api.yourdomain.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self';" always;

# X-Frame-Options
add_header X-Frame-Options "DENY" always;

# X-Content-Type-Options
add_header X-Content-Type-Options "nosniff" always;

# X-XSS-Protection
add_header X-XSS-Protection "1; mode=block" always;

# Referrer-Policy
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Permissions-Policy
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

## Audit Logging

### Database Audit Log

```sql
-- Install pgaudit extension
CREATE EXTENSION IF NOT EXISTS pgaudit;

-- Configure audit logging
ALTER SYSTEM SET pgaudit.log = 'write, ddl, role';
ALTER SYSTEM SET pgaudit.log_catalog = off;
ALTER SYSTEM SET pgaudit.log_parameter = on;
ALTER SYSTEM SET pgaudit.log_relation = on;
SELECT pg_reload_conf();

-- Create audit table
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    user_id VARCHAR(36),
    action VARCHAR(50),
    table_name VARCHAR(100),
    record_id VARCHAR(36),
    old_values JSONB,
    new_values JSONB,
    ip_address INET
);

-- Trigger for audit logging
CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (user_id, action, table_name, record_id, new_values)
        VALUES (current_user, 'INSERT', TG_TABLE_NAME, NEW.id, row_to_json(NEW));
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (user_id, action, table_name, record_id, old_values, new_values)
        VALUES (current_user, 'UPDATE', TG_TABLE_NAME, NEW.id, row_to_json(OLD), row_to_json(NEW));
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (user_id, action, table_name, record_id, old_values)
        VALUES (current_user, 'DELETE', TG_TABLE_NAME, OLD.id, row_to_json(OLD));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to sensitive tables
CREATE TRIGGER audit_planning_trigger
AFTER INSERT OR UPDATE OR DELETE ON planning_objectives
FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();
```

### Application Audit Log

```python
# Structured audit logging
import logging
import json
from datetime import datetime

class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger('audit')
        handler = logging.FileHandler('/var/log/bcm/audit.log')
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log(self, user_id: str, action: str, resource: str, result: str, **kwargs):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'result': result,
            **kwargs
        }
        self.logger.info(json.dumps(log_entry))

# Usage
audit = AuditLogger()
audit.log(
    user_id='user_123',
    action='CREATE',
    resource='bcm_plan',
    result='SUCCESS',
    plan_id='plan_456',
    ip_address='192.168.1.100'
)
```

## Security Scanning

### Container Security Scanning

```bash
# Scan images with Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy image bcm/planning-service:latest

# Scan with Clair
docker run -d --name clair-db postgres:11
docker run -d --name clair --link clair-db:postgres \
    -p 6060:6060 -p 6061:6061 quay.io/coreos/clair:latest

# Automated scanning in CI/CD
trivy image --severity HIGH,CRITICAL --exit-code 1 bcm/planning-service:latest
```

### Dependency Scanning

```bash
# Python dependencies
pip install safety
safety check -r requirements.txt

# Or using Snyk
npm install -g snyk
snyk test

# OWASP Dependency Check
dependency-check --project "BCM Platform" --scan ./
```

## Secret Rotation

### Automated Secret Rotation Script

```bash
#!/bin/bash
# rotate_secrets.sh

set -e

echo "Starting secret rotation..."

# 1. Generate new database password
NEW_DB_PASSWORD=$(openssl rand -base64 32)

# 2. Update in Vault
vault kv put secret/bcm/postgres password="$NEW_DB_PASSWORD"

# 3. Update PostgreSQL
docker-compose exec postgres psql -U postgres -c "ALTER USER bcm_user WITH PASSWORD '$NEW_DB_PASSWORD';"

# 4. Update environment and restart services
export POSTGRES_PASSWORD="$NEW_DB_PASSWORD"
docker-compose up -d --force-recreate

# 5. Verify
sleep 30
docker-compose exec planning-service python -c "from database import engine; engine.connect()"

echo "Secret rotation completed successfully"
```

### Rotation Schedule

| Secret Type | Rotation Frequency | Automated |
|------------|-------------------|-----------|
| Database passwords | 90 days | Yes |
| JWT keys | 180 days | Yes |
| API keys | 90 days | Manual |
| SSL certificates | Before expiry | Yes (Let's Encrypt) |
| Service accounts | 180 days | Manual |

## Compliance and Standards

### ISO 22301 Security Requirements

- A.5.1.1: Information security policies
- A.5.1.2: Review of information security policies
- A.9.2.1: User registration and de-registration
- A.9.2.2: User access provisioning
- A.9.4.1: Information access restriction
- A.10.1.1: Policy on use of cryptographic controls
- A.18.1.1: Identification of applicable legislation

### OWASP Top 10 Mitigations

1. **Broken Access Control**: Implement RBAC, validate permissions
2. **Cryptographic Failures**: Use TLS, encrypt sensitive data
3. **Injection**: Use parameterized queries, input validation
4. **Insecure Design**: Threat modeling, security review
5. **Security Misconfiguration**: Harden configurations, disable defaults
6. **Vulnerable Components**: Regular updates, dependency scanning
7. **Authentication Failures**: MFA, strong passwords, rate limiting
8. **Software and Data Integrity**: Code signing, SRI, secure CI/CD
9. **Logging Failures**: Comprehensive logging, monitoring
10. **SSRF**: Input validation, network segmentation

## Security Checklist

### Pre-Production Security Checklist

- [ ] JWT keys generated (RSA 4096)
- [ ] All default passwords changed
- [ ] SSL/TLS certificates obtained and configured
- [ ] Secrets stored in vault (not in code/env files)
- [ ] Firewall rules configured
- [ ] Rate limiting enabled
- [ ] Security headers configured
- [ ] Database encryption enabled
- [ ] Audit logging configured
- [ ] Container images scanned
- [ ] Dependencies scanned
- [ ] Penetration testing completed
- [ ] Security training completed
- [ ] Incident response plan documented
- [ ] Backup encryption verified

## Related Documentation

- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Environment Configuration](./ENVIRONMENT_CONFIGURATION.md)
- [Monitoring Guide](./MONITORING_GUIDE.md)

---

**Last Updated:** 2024-10-03
**Document Owner:** Security Team
