# Environment Configuration Guide

## Overview

This guide provides detailed configuration for all environment variables used in the BCM Platform. Proper environment configuration is critical for security, performance, and reliability in production.

## Configuration Management Strategy

### Development vs Production

**Development:**
- Use `.env` file for local configuration
- Default passwords acceptable
- Debug logging enabled
- Relaxed CORS policies

**Production:**
- Use secret management system (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault)
- Strong, unique passwords for all services
- INFO or WARNING log level
- Strict CORS whitelist

### Secret Management

We recommend using a dedicated secret management system for production:

**HashiCorp Vault:**
```bash
# Store secrets
vault kv put secret/bcm/postgres password="<secure_password>"
vault kv put secret/bcm/jwt private_key=@jwt_private.key
vault kv put secret/bcm/jwt public_key=@jwt_public.key

# Retrieve in deployment
export POSTGRES_PASSWORD=$(vault kv get -field=password secret/bcm/postgres)
```

**AWS Secrets Manager:**
```bash
# Store secrets
aws secretsmanager create-secret --name bcm/postgres/password --secret-string "<secure_password>"

# Retrieve in deployment
export POSTGRES_PASSWORD=$(aws secretsmanager get-secret-value --secret-id bcm/postgres/password --query SecretString --output text)
```

**Docker Secrets (Swarm/Kubernetes):**
```bash
# Create secret
echo "secure_password" | docker secret create postgres_password -

# Reference in docker-compose.yml
secrets:
  - postgres_password
```

## Core Infrastructure Configuration

### PostgreSQL Database

```bash
# Database Server Configuration
POSTGRES_HOST=postgres                    # Hostname (use 'localhost' if not using Docker)
POSTGRES_PORT=5432                        # Default PostgreSQL port
POSTGRES_DB=bcm_platform                  # Primary database name
POSTGRES_USER=bcm_user                    # Database user
POSTGRES_PASSWORD=<CHANGE_IN_PRODUCTION>  # REQUIRED: Strong password (min 16 chars)

# Additional Databases (auto-created by init script)
POSTGRES_MULTIPLE_DATABASES=planning,plans,governance,risk,response,learning

# Connection Pool Configuration
POSTGRES_MAX_CONNECTIONS=100              # Maximum simultaneous connections
POSTGRES_POOL_SIZE=20                     # Connection pool size per service
POSTGRES_POOL_TIMEOUT=30                  # Connection timeout in seconds
POSTGRES_POOL_RECYCLE=3600                # Recycle connections after N seconds

# Performance Tuning (PostgreSQL 15+)
POSTGRES_SHARED_BUFFERS=256MB             # RAM for caching (25% of system RAM)
POSTGRES_EFFECTIVE_CACHE_SIZE=1GB         # OS + PostgreSQL cache estimate
POSTGRES_WORK_MEM=16MB                    # Memory for sorting/hashing per operation
POSTGRES_MAINTENANCE_WORK_MEM=128MB       # Memory for maintenance operations
POSTGRES_WAL_BUFFERS=8MB                  # Write-ahead log buffer size

# Connection String (used by services)
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
```

**Production Password Requirements:**
- Minimum 16 characters
- Mix of uppercase, lowercase, numbers, and special characters
- No dictionary words
- Rotate every 90 days

**Example Strong Password Generation:**
```bash
# Generate secure password (Linux/macOS)
openssl rand -base64 32

# Or using Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Redis Configuration

```bash
# Redis Server Configuration
REDIS_HOST=redis                          # Hostname
REDIS_PORT=6379                           # Default Redis port
REDIS_PASSWORD=                           # Optional: Set for production
REDIS_DB=0                                # Database number (0-15)

# Connection String
REDIS_URL=redis://:${REDIS_PASSWORD}@${REDIS_HOST}:${REDIS_PORT}/${REDIS_DB}

# Cache Configuration
REDIS_CACHE_TTL=3600                      # Default cache TTL in seconds
REDIS_MAX_CONNECTIONS=50                  # Maximum connections per service
REDIS_SOCKET_TIMEOUT=5                    # Socket timeout in seconds
REDIS_SOCKET_CONNECT_TIMEOUT=5            # Connection timeout in seconds

# Memory Configuration
REDIS_MAXMEMORY=1gb                       # Maximum memory usage
REDIS_MAXMEMORY_POLICY=allkeys-lru        # Eviction policy (LRU recommended)

# Persistence (Production)
REDIS_SAVE_ENABLED=true                   # Enable RDB snapshots
REDIS_SAVE_INTERVAL=900 1 300 10 60 10000 # Save after: 900s if 1 key, 300s if 10 keys, 60s if 10000 keys
REDIS_AOF_ENABLED=true                    # Enable Append-Only File
```

**Redis Security Best Practices:**
```bash
# Enable password protection
redis-cli CONFIG SET requirepass "your-strong-password"

# Disable dangerous commands (in redis.conf)
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
```

### EventBus Configuration

```bash
# EventBus Server Configuration
EVENTBUS_URL=http://eventbus:8001         # EventBus endpoint
EVENTBUS_TIMEOUT=30                       # Request timeout in seconds
EVENTBUS_RETRY_ATTEMPTS=3                 # Number of retry attempts
EVENTBUS_RETRY_DELAY=1                    # Delay between retries in seconds

# Alternative: RabbitMQ Configuration (for production)
RABBITMQ_HOST=rabbitmq                    # RabbitMQ hostname
RABBITMQ_PORT=5672                        # AMQP port
RABBITMQ_USER=bcm_user                    # RabbitMQ user
RABBITMQ_PASSWORD=<CHANGE_IN_PRODUCTION>  # RabbitMQ password
RABBITMQ_VHOST=/bcm                       # Virtual host
RABBITMQ_URL=amqp://${RABBITMQ_USER}:${RABBITMQ_PASSWORD}@${RABBITMQ_HOST}:${RABBITMQ_PORT}/${RABBITMQ_VHOST}

# Message Configuration
EVENTBUS_MAX_MESSAGE_SIZE=1048576         # 1MB max message size
EVENTBUS_QUEUE_SIZE=1000                  # Maximum queue size
```

## Service-Specific Configuration

### Planning Service (Port 8011)

```bash
# Service Identity
SERVICE_NAME=planning_service
SERVICE_PORT=8011
SERVICE_VERSION=1.0.0

# Database (dedicated database recommended for production)
DATABASE_URL=postgresql+asyncpg://bcm_user:${POSTGRES_PASSWORD}@postgres:5432/planning

# Redis (dedicated DB number)
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# Authentication
JWT_PUBLIC_KEY=<BASE64_ENCODED_PUBLIC_KEY>
JWT_ALGORITHM=RS256

# EventBus
EVENTBUS_URL=http://eventbus:8001

# Business Logic
MAX_PLANNING_DURATION_DAYS=365            # Maximum planning horizon
DEFAULT_REVIEW_PERIOD_DAYS=90             # Default review frequency
AUTO_ARCHIVE_DAYS=730                     # Archive plans after 2 years

# Performance
CACHE_ENABLED=true
CACHE_TTL_SECONDS=3600
MAX_QUERY_LIMIT=1000                      # Maximum records per query
```

### Plans Service (Port 8023)

```bash
# Service Identity
SERVICE_NAME=plans_service
SERVICE_PORT=8023
SERVICE_VERSION=1.0.0

# Database
DATABASE_URL=postgresql+asyncpg://bcm_user:${POSTGRES_PASSWORD}@postgres:5432/plans

# Redis (different DB number)
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/1

# Authentication
JWT_PUBLIC_KEY=<BASE64_ENCODED_PUBLIC_KEY>
JWT_ALGORITHM=RS256

# EventBus
EVENTBUS_URL=http://eventbus:8001

# Service Dependencies
PLANNING_SERVICE_URL=http://planning-service:8011

# Business Logic
MAX_PLAN_VERSIONS=50                      # Keep last 50 versions
PLAN_APPROVAL_REQUIRED=true               # Require approval for activation
AUTO_VERSION_ON_CHANGE=true               # Auto-increment version on edits

# File Upload (if applicable)
MAX_UPLOAD_SIZE_MB=10
ALLOWED_FILE_TYPES=pdf,doc,docx,xlsx
UPLOAD_PATH=/var/bcm/uploads

# Performance
CACHE_ENABLED=true
CACHE_TTL_SECONDS=1800
```

### BIA Service (Port 8012)

```bash
# Service Identity
SERVICE_NAME=bia_service
SERVICE_PORT=8012
SERVICE_VERSION=1.0.0

# Database
DATABASE_URL=postgresql+asyncpg://bcm_user:${POSTGRES_PASSWORD}@postgres:5432/bcm_platform

# Authentication
JWT_SECRET=${JWT_SECRET}                  # Shared secret or use JWT_PUBLIC_KEY

# EventBus (RabbitMQ format)
EVENTBUS_URL=amqp://guest:guest@rabbitmq:5672/

# Business Logic
DEFAULT_RTO_HOURS=24                      # Default Recovery Time Objective
DEFAULT_RPO_HOURS=4                       # Default Recovery Point Objective
IMPACT_CALCULATION_METHOD=weighted        # Options: weighted, max, average
AUTO_CALCULATE_MTPD=true                  # Auto-calculate Maximum Tolerable Period of Disruption

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Compliance Service (Port 8014)

```bash
# Service Identity
SERVICE_NAME=compliance_service
SERVICE_PORT=8014
SERVICE_VERSION=1.0.0

# Database
DATABASE_URL=postgresql+asyncpg://bcm_user:${POSTGRES_PASSWORD}@postgres:5432/bcm_platform

# Authentication
JWT_SECRET=${JWT_SECRET}

# EventBus
EVENTBUS_URL=amqp://guest:guest@rabbitmq:5672/

# Compliance Configuration
COMPLIANCE_FRAMEWORK=ISO22301:2019        # Primary framework
AUDIT_RETENTION_YEARS=7                   # Keep audit logs for 7 years
AUTO_COMPLIANCE_CHECK=true                # Automatic compliance checking
COMPLIANCE_CHECK_SCHEDULE=0 2 * * *       # Daily at 2 AM (cron format)

# Notifications
COMPLIANCE_ALERT_EMAIL=compliance@yourdomain.com
SEND_COMPLIANCE_REPORTS=true
REPORT_SCHEDULE=0 9 * * MON               # Weekly on Monday at 9 AM

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Monitoring Service (Port 8045)

```bash
# Service Configuration
SERVICE_PORT=8045

# Monitoring Configuration
LOG_DIR=/var/log/bcm
CHECK_INTERVAL_SECONDS=30                 # Health check frequency
METRICS_RETENTION_HOURS=24                # Keep metrics for 24 hours
ALERT_COOLDOWN_MINUTES=15                 # Minimum time between duplicate alerts

# Service Endpoints to Monitor
MONITORED_SERVICES=planning-service:8011,plans-service:8023,bia-service:8012,compliance-service:8014

# Alert Configuration
ALERT_EMAIL=alerts@yourdomain.com
NOTIFICATION_SERVICE_URL=http://notification-service:8035
PAGERDUTY_API_KEY=<PAGERDUTY_KEY>
PAGERDUTY_ROUTING_KEY=<ROUTING_KEY>

# Thresholds
CPU_ALERT_THRESHOLD=80                    # Alert if CPU > 80%
MEMORY_ALERT_THRESHOLD=85                 # Alert if Memory > 85%
DISK_ALERT_THRESHOLD=90                   # Alert if Disk > 90%
ERROR_RATE_THRESHOLD=5                    # Alert if error rate > 5%
RESPONSE_TIME_THRESHOLD_MS=5000           # Alert if response time > 5s
```

## Security Configuration

### JWT (JSON Web Token) Configuration

**Production JWT Setup (RSA 4096):**

```bash
# Generate RSA key pair
openssl genrsa -out jwt_private.key 4096
openssl rsa -in jwt_private.key -pubout -out jwt_public.key

# Base64 encode for environment variables (single line, no line breaks)
JWT_PRIVATE_KEY=$(cat jwt_private.key | base64 -w 0)  # Linux
JWT_PRIVATE_KEY=$(cat jwt_private.key | base64)       # macOS

JWT_PUBLIC_KEY=$(cat jwt_public.key | base64 -w 0)    # Linux
JWT_PUBLIC_KEY=$(cat jwt_public.key | base64)         # macOS

# JWT Configuration
JWT_ALGORITHM=RS256                       # Use RSA 256 for production
JWT_EXPIRATION_HOURS=24                   # Token expires after 24 hours
JWT_REFRESH_ENABLED=true                  # Enable refresh tokens
JWT_REFRESH_EXPIRATION_DAYS=30            # Refresh token lifetime
JWT_ISSUER=bcm-platform                   # Token issuer
JWT_AUDIENCE=bcm-services                 # Token audience
```

**Alternative: Shared Secret (HS256 - Less Secure):**
```bash
# Generate strong secret
JWT_SECRET=$(openssl rand -base64 64)
JWT_ALGORITHM=HS256
```

### CORS (Cross-Origin Resource Sharing)

```bash
# Production CORS Configuration
ALLOWED_ORIGINS=https://bcm.yourdomain.com,https://app.yourdomain.com
ALLOWED_METHODS=GET,POST,PUT,DELETE,PATCH
ALLOWED_HEADERS=Content-Type,Authorization,X-Request-ID
EXPOSE_HEADERS=X-Total-Count,X-Page,X-Per-Page
ALLOW_CREDENTIALS=true
MAX_AGE_SECONDS=3600                      # Preflight cache duration
```

**Development CORS (Permissive):**
```bash
ALLOWED_ORIGINS=*                         # WARNING: Never use in production
ALLOWED_METHODS=*
ALLOWED_HEADERS=*
```

### Rate Limiting

```bash
# Rate Limiting Configuration
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=1000                  # Requests per period
RATE_LIMIT_PERIOD=3600                    # Period in seconds (1 hour)
RATE_LIMIT_STRATEGY=sliding-window        # Options: fixed-window, sliding-window, token-bucket

# Per-Endpoint Rate Limits (optional)
RATE_LIMIT_AUTH_REQUESTS=10               # Login attempts per minute
RATE_LIMIT_AUTH_PERIOD=60
RATE_LIMIT_API_REQUESTS=100               # API calls per minute
RATE_LIMIT_API_PERIOD=60

# Rate Limit Response
RATE_LIMIT_HEADERS=true                   # Include X-RateLimit-* headers
RATE_LIMIT_STATUS_CODE=429                # HTTP status for rate limited requests
```

### SSL/TLS Configuration

```bash
# SSL Certificate Paths (if terminating SSL at application)
SSL_ENABLED=true
SSL_CERT_PATH=/etc/ssl/certs/bcm.crt
SSL_KEY_PATH=/etc/ssl/private/bcm.key
SSL_CA_PATH=/etc/ssl/certs/ca-bundle.crt

# SSL Configuration
SSL_PROTOCOLS=TLSv1.2,TLSv1.3            # Only secure protocols
SSL_CIPHERS=ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384

# HTTP Strict Transport Security (HSTS)
HSTS_ENABLED=true
HSTS_MAX_AGE=31536000                     # 1 year
HSTS_INCLUDE_SUBDOMAINS=true
HSTS_PRELOAD=true
```

## Logging Configuration

```bash
# Log Level
LOG_LEVEL=INFO                            # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Log Format
LOG_FORMAT=json                           # Options: json, text
LOG_TIMESTAMP_FORMAT=iso8601              # ISO 8601 format

# Log Output
LOG_OUTPUT=stdout                         # stdout, file, both
LOG_FILE_PATH=/var/log/bcm/service.log    # If LOG_OUTPUT includes 'file'
LOG_FILE_MAX_SIZE_MB=100                  # Rotate when file reaches size
LOG_FILE_MAX_BACKUPS=10                   # Keep 10 old log files
LOG_FILE_COMPRESS=true                    # Compress rotated logs

# Request Logging
LOG_REQUESTS=true                         # Log all HTTP requests
LOG_REQUEST_BODY=false                    # Log request bodies (WARNING: may log sensitive data)
LOG_RESPONSE_BODY=false                   # Log response bodies
REQUEST_ID_HEADER=X-Request-ID            # Header for request tracking

# Sensitive Data Masking
LOG_MASK_SENSITIVE=true                   # Mask sensitive fields in logs
LOG_SENSITIVE_FIELDS=password,token,secret,api_key,jwt
```

## Monitoring and Metrics

```bash
# Prometheus Metrics
METRICS_ENABLED=true
METRICS_PORT=9100                         # Metrics endpoint port (separate from main app)
METRICS_PATH=/metrics                     # Metrics endpoint path

# Metric Collection
COLLECT_SYSTEM_METRICS=true               # CPU, memory, disk
COLLECT_APPLICATION_METRICS=true          # Request rate, errors, latency
COLLECT_BUSINESS_METRICS=true             # Domain-specific metrics
METRICS_INTERVAL_SECONDS=15               # Collection interval

# Distributed Tracing (Optional - Jaeger/Zipkin)
TRACING_ENABLED=false
TRACING_BACKEND=jaeger                    # jaeger, zipkin
TRACING_ENDPOINT=http://jaeger:14268/api/traces
TRACING_SAMPLE_RATE=0.1                   # Sample 10% of requests
```

## Email/Notification Configuration

```bash
# SMTP Configuration
SMTP_ENABLED=true
SMTP_HOST=smtp.gmail.com                  # SMTP server
SMTP_PORT=587                             # SMTP port (587 for TLS, 465 for SSL)
SMTP_USE_TLS=true
SMTP_USERNAME=notifications@yourdomain.com
SMTP_PASSWORD=<SMTP_PASSWORD>
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=BCM Platform

# Email Templates
EMAIL_TEMPLATE_PATH=/app/templates/email
EMAIL_LOGO_URL=https://yourdomain.com/logo.png

# Notification Settings
NOTIFICATION_RETRY_ATTEMPTS=3
NOTIFICATION_RETRY_DELAY=60               # Seconds between retries
NOTIFICATION_BATCH_SIZE=50                # Send emails in batches
```

## Application Configuration

```bash
# Application Environment
ENVIRONMENT=production                    # development, staging, production
DEBUG=false                               # NEVER true in production
TESTING=false

# Application Timezone
TZ=UTC                                    # Always use UTC for consistency

# Feature Flags
FEATURE_ADVANCED_BIA=true
FEATURE_COMPLIANCE_AUTOMATION=true
FEATURE_WORKFLOW_ENGINE=true
FEATURE_API_V2=false                      # Beta features

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# File Storage
STORAGE_BACKEND=local                     # local, s3, azure, gcs
STORAGE_PATH=/var/bcm/storage
# S3 Configuration (if STORAGE_BACKEND=s3)
AWS_ACCESS_KEY_ID=<AWS_KEY>
AWS_SECRET_ACCESS_KEY=<AWS_SECRET>
AWS_REGION=us-east-1
AWS_S3_BUCKET=bcm-platform-storage
```

## Complete Production .env Template

```bash
#============================================
# BCM Platform Production Configuration
#============================================

# Environment
ENVIRONMENT=production
DEBUG=false
TZ=UTC

#--------------------------------------------
# Database Configuration
#--------------------------------------------
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=bcm_platform
POSTGRES_USER=bcm_user
POSTGRES_PASSWORD=<CHANGE_ME_SECURE_PASSWORD>
POSTGRES_MULTIPLE_DATABASES=planning,plans,governance,risk,response,learning
DATABASE_URL=postgresql+asyncpg://bcm_user:<PASSWORD>@postgres:5432/bcm_platform

# Database Performance
POSTGRES_POOL_SIZE=20
POSTGRES_MAX_CONNECTIONS=100
POSTGRES_SHARED_BUFFERS=256MB
POSTGRES_EFFECTIVE_CACHE_SIZE=1GB

#--------------------------------------------
# Redis Configuration
#--------------------------------------------
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=<CHANGE_ME_REDIS_PASSWORD>
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
REDIS_MAXMEMORY=1gb
REDIS_MAXMEMORY_POLICY=allkeys-lru

#--------------------------------------------
# JWT Authentication
#--------------------------------------------
JWT_ALGORITHM=RS256
JWT_PUBLIC_KEY=<BASE64_ENCODED_PUBLIC_KEY>
JWT_PRIVATE_KEY=<BASE64_ENCODED_PRIVATE_KEY>
JWT_EXPIRATION_HOURS=24
JWT_ISSUER=bcm-platform
JWT_AUDIENCE=bcm-services

#--------------------------------------------
# Service URLs
#--------------------------------------------
PLANNING_SERVICE_URL=http://planning-service:8011
PLANS_SERVICE_URL=http://plans-service:8023
BIA_SERVICE_URL=http://bia-service:8012
COMPLIANCE_SERVICE_URL=http://compliance-service:8014
EVENTBUS_URL=http://eventbus:8001

#--------------------------------------------
# Security
#--------------------------------------------
ALLOWED_ORIGINS=https://bcm.yourdomain.com,https://app.yourdomain.com
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_PERIOD=3600
SSL_ENABLED=true

#--------------------------------------------
# Logging
#--------------------------------------------
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_REQUESTS=true
LOG_MASK_SENSITIVE=true

#--------------------------------------------
# Monitoring
#--------------------------------------------
METRICS_ENABLED=true
ALERT_EMAIL=alerts@yourdomain.com
PAGERDUTY_API_KEY=<PAGERDUTY_KEY>

#--------------------------------------------
# Email/SMTP
#--------------------------------------------
SMTP_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=notifications@yourdomain.com
SMTP_PASSWORD=<SMTP_PASSWORD>
SMTP_FROM_EMAIL=noreply@yourdomain.com

#============================================
# End of Configuration
#============================================
```

## Environment Validation

Before deploying, validate your environment configuration:

```bash
#!/bin/bash
# validate_env.sh

echo "Validating environment configuration..."

# Check required variables
REQUIRED_VARS=(
    "POSTGRES_PASSWORD"
    "JWT_PUBLIC_KEY"
    "ALLOWED_ORIGINS"
    "ALERT_EMAIL"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "ERROR: $var is not set"
        exit 1
    fi
done

# Check password strength
if [ ${#POSTGRES_PASSWORD} -lt 16 ]; then
    echo "WARNING: POSTGRES_PASSWORD should be at least 16 characters"
fi

# Check if DEBUG is disabled
if [ "$DEBUG" = "true" ]; then
    echo "ERROR: DEBUG must be false in production"
    exit 1
fi

echo "Environment validation passed!"
```

## Secret Rotation

Schedule regular secret rotation:

```bash
# Rotate database password (example)
# 1. Generate new password
NEW_PASSWORD=$(openssl rand -base64 32)

# 2. Update in database
psql -U bcm_user -c "ALTER USER bcm_user WITH PASSWORD '$NEW_PASSWORD';"

# 3. Update in secret manager
vault kv put secret/bcm/postgres password="$NEW_PASSWORD"

# 4. Restart services with new configuration
docker-compose restart
```

**Recommended Rotation Schedule:**
- Database passwords: Every 90 days
- JWT keys: Every 180 days
- API keys: Every 90 days
- SSL certificates: Before expiration (usually annually)

## Related Documentation

- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Security Guide](./SECURITY_GUIDE.md)
- [Docker Deployment](./DOCKER_DEPLOYMENT.md)

---

**Last Updated:** 2024-10-03
**Document Owner:** Platform Engineering Team
