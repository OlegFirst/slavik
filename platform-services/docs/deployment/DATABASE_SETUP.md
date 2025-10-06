# Database Setup Guide

## Overview

This guide provides comprehensive instructions for setting up and configuring PostgreSQL databases for the BCM Platform. The platform uses PostgreSQL 15+ as its primary relational database.

## Database Architecture

### Database Structure

The BCM Platform uses a multi-database architecture:

```
PostgreSQL Server (postgres:5432)
├── bcm_platform (main database)
│   ├── Planning Service tables
│   ├── Plans Service tables
│   ├── BIA Service tables
│   └── Compliance Service tables
├── planning (optional dedicated database)
├── plans (optional dedicated database)
├── governance
├── risk
├── response
└── learning
```

### Database Users and Permissions

```
bcm_user (service account)
├── CONNECT privilege on all databases
├── CREATE privilege on schemas
├── Full CRUD on owned tables
└── EXECUTE on functions

bcm_admin (administrative account)
├── SUPERUSER privileges
├── Database creation and deletion
└── User management

bcm_readonly (reporting/analytics)
├── SELECT privilege on all tables
└── No write permissions
```

## PostgreSQL Installation

### Docker Installation (Recommended)

The platform includes PostgreSQL in `docker-compose.yml`:

```yaml
postgres:
  image: postgres:15-alpine
  container_name: bcm-postgres
  environment:
    POSTGRES_DB: bcm_platform
    POSTGRES_USER: bcm_user
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    POSTGRES_MULTIPLE_DATABASES: planning,plans,governance,risk,response,learning
  ports:
    - "5432:5432"
  volumes:
    - postgres_data:/var/lib/postgresql/data
    - ./scripts/init-databases.sh:/docker-entrypoint-initdb.d/init-databases.sh
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U bcm_user -d bcm_platform"]
    interval: 10s
    timeout: 5s
    retries: 5
```

### Native Installation (Ubuntu/Debian)

```bash
# Add PostgreSQL APT repository
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# Install PostgreSQL 15
sudo apt-get update
sudo apt-get install -y postgresql-15 postgresql-contrib-15

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify installation
psql --version
```

### Native Installation (RHEL/CentOS)

```bash
# Install PostgreSQL repository
sudo dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm

# Disable built-in PostgreSQL module
sudo dnf -qy module disable postgresql

# Install PostgreSQL 15
sudo dnf install -y postgresql15-server postgresql15-contrib

# Initialize database
sudo /usr/pgsql-15/bin/postgresql-15-setup initdb

# Start PostgreSQL
sudo systemctl start postgresql-15
sudo systemctl enable postgresql-15
```

## Database Creation

### Using Docker

The `init-databases.sh` script automatically creates all databases on first container start:

```bash
#!/bin/bash
# /Users/MD/AI-Platform-ISO/platform-services/scripts/init-databases.sh

set -e

# Create multiple databases from POSTGRES_MULTIPLE_DATABASES environment variable
if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    echo "Creating multiple databases: $POSTGRES_MULTIPLE_DATABASES"
    for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
        echo "Creating database: $db"
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
            CREATE DATABASE $db;
            GRANT ALL PRIVILEGES ON DATABASE $db TO $POSTGRES_USER;
EOSQL
    done
fi
```

Start the database:

```bash
# Start PostgreSQL container
docker-compose up -d postgres

# Verify databases were created
docker-compose exec postgres psql -U bcm_user -d bcm_platform -c "\l"
```

### Manual Database Creation

If setting up manually:

```sql
-- Connect as superuser
psql -U postgres

-- Create main database
CREATE DATABASE bcm_platform
    WITH
    OWNER = bcm_user
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Create additional databases
CREATE DATABASE planning OWNER bcm_user;
CREATE DATABASE plans OWNER bcm_user;
CREATE DATABASE governance OWNER bcm_user;
CREATE DATABASE risk OWNER bcm_user;
CREATE DATABASE response OWNER bcm_user;
CREATE DATABASE learning OWNER bcm_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE bcm_platform TO bcm_user;
GRANT ALL PRIVILEGES ON DATABASE planning TO bcm_user;
GRANT ALL PRIVILEGES ON DATABASE plans TO bcm_user;
```

## User and Permission Setup

### Create Database Users

```sql
-- Create service account (main user)
CREATE USER bcm_user WITH PASSWORD '<SECURE_PASSWORD>';

-- Create admin account (for administration)
CREATE USER bcm_admin WITH PASSWORD '<ADMIN_PASSWORD>' SUPERUSER CREATEDB CREATEROLE;

-- Create read-only user (for reporting/analytics)
CREATE USER bcm_readonly WITH PASSWORD '<READONLY_PASSWORD>';

-- Grant database connection privileges
GRANT CONNECT ON DATABASE bcm_platform TO bcm_user;
GRANT CONNECT ON DATABASE bcm_platform TO bcm_readonly;
GRANT CONNECT ON DATABASE planning TO bcm_user;
GRANT CONNECT ON DATABASE plans TO bcm_user;
```

### Configure Permissions

```sql
-- Connect to bcm_platform database
\c bcm_platform

-- Grant schema privileges
GRANT USAGE ON SCHEMA public TO bcm_user;
GRANT CREATE ON SCHEMA public TO bcm_user;

-- Grant read-only access to bcm_readonly
GRANT USAGE ON SCHEMA public TO bcm_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO bcm_readonly;

-- Auto-grant SELECT on future tables to bcm_readonly
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO bcm_readonly;

-- Ensure bcm_user owns all objects
ALTER SCHEMA public OWNER TO bcm_user;
```

### Password Security

Generate strong passwords:

```bash
# Generate 32-character secure password
openssl rand -base64 32

# Or using Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Connection Pooling Configuration

### PgBouncer Setup (Recommended for Production)

PgBouncer is a lightweight connection pooler for PostgreSQL:

```bash
# Install PgBouncer
sudo apt-get install pgbouncer

# Configure PgBouncer (/etc/pgbouncer/pgbouncer.ini)
```

**pgbouncer.ini:**
```ini
[databases]
bcm_platform = host=localhost port=5432 dbname=bcm_platform
planning = host=localhost port=5432 dbname=planning
plans = host=localhost port=5432 dbname=plans

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
admin_users = bcm_admin
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
max_db_connections = 100
server_idle_timeout = 600
```

**userlist.txt:**
```
"bcm_user" "<MD5_HASHED_PASSWORD>"
"bcm_admin" "<MD5_HASHED_PASSWORD>"
```

Generate MD5 password:
```bash
echo -n "<PASSWORD>bcm_user" | md5sum
```

### Application-Level Connection Pooling

Configure in application (SQLAlchemy example):

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "postgresql+asyncpg://bcm_user:password@postgres:5432/bcm_platform",
    poolclass=QueuePool,
    pool_size=20,              # Number of permanent connections
    max_overflow=10,           # Additional connections when needed
    pool_timeout=30,           # Timeout waiting for connection
    pool_recycle=3600,         # Recycle connections after 1 hour
    pool_pre_ping=True,        # Verify connection health before use
    echo_pool=True             # Log pool events (disable in production)
)
```

## Performance Tuning

### PostgreSQL Configuration

Edit `/etc/postgresql/15/main/postgresql.conf` (or use environment variables in Docker):

```conf
# Memory Configuration
shared_buffers = 256MB              # 25% of system RAM (for 1GB RAM system)
effective_cache_size = 768MB        # 75% of system RAM
work_mem = 16MB                     # Memory per sort/hash operation
maintenance_work_mem = 128MB        # Memory for VACUUM, CREATE INDEX

# Checkpoint Configuration
checkpoint_completion_target = 0.9
wal_buffers = 16MB
checkpoint_timeout = 15min
max_wal_size = 1GB
min_wal_size = 80MB

# Connection Configuration
max_connections = 100               # Adjust based on workload
superuser_reserved_connections = 3

# Query Planner
random_page_cost = 1.1             # For SSD storage (4.0 for HDD)
effective_io_concurrency = 200     # For SSD storage (2 for HDD)

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d.log'
log_min_duration_statement = 1000  # Log queries slower than 1s
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0

# Autovacuum (important for performance)
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 1min
autovacuum_vacuum_scale_factor = 0.1
autovacuum_analyze_scale_factor = 0.05
```

### Apply Configuration Changes

```bash
# Docker
docker-compose restart postgres

# Native installation
sudo systemctl restart postgresql-15

# Verify configuration
docker-compose exec postgres psql -U bcm_user -c "SHOW shared_buffers;"
docker-compose exec postgres psql -U bcm_user -c "SHOW effective_cache_size;"
```

### Performance Analysis Tools

```sql
-- Find slow queries
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Find missing indexes
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    seq_tup_read / seq_scan AS avg_tuples_per_scan
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC
LIMIT 10;

-- Check table bloat
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Index Creation and Optimization

### Recommended Indexes

Based on common query patterns, create these indexes:

```sql
-- Planning Service Indexes
CREATE INDEX idx_planning_status ON planning_objectives(status);
CREATE INDEX idx_planning_org ON planning_objectives(organization_id);
CREATE INDEX idx_planning_created ON planning_objectives(created_at DESC);
CREATE INDEX idx_planning_updated ON planning_objectives(updated_at DESC);

-- Plans Service Indexes
CREATE INDEX idx_plans_status ON bcm_plans(status);
CREATE INDEX idx_plans_version ON bcm_plans(plan_id, version DESC);
CREATE INDEX idx_plans_active ON bcm_plans(is_active) WHERE is_active = true;
CREATE INDEX idx_plans_org ON bcm_plans(organization_id);

-- BIA Service Indexes
CREATE INDEX idx_bia_criticality ON business_impact_assessments(criticality);
CREATE INDEX idx_bia_rto ON business_impact_assessments(rto_hours);
CREATE INDEX idx_bia_process ON business_impact_assessments(process_id);

-- Compliance Service Indexes
CREATE INDEX idx_compliance_status ON compliance_assessments(status);
CREATE INDEX idx_compliance_framework ON compliance_assessments(framework);
CREATE INDEX idx_compliance_date ON compliance_assessments(assessment_date DESC);

-- Composite indexes for common queries
CREATE INDEX idx_planning_org_status ON planning_objectives(organization_id, status);
CREATE INDEX idx_plans_org_active ON bcm_plans(organization_id, is_active);
```

### Index Maintenance

```sql
-- Rebuild indexes (during maintenance window)
REINDEX TABLE planning_objectives;
REINDEX TABLE bcm_plans;

-- Or rebuild all indexes in database
REINDEX DATABASE bcm_platform;

-- Analyze tables to update statistics
ANALYZE planning_objectives;
ANALYZE bcm_plans;

-- Or analyze entire database
ANALYZE;
```

## Database Migrations

### Migration Strategy

The BCM Platform services handle migrations automatically using Alembic (Python) or similar tools.

**Manual Migration Example (Planning Service):**

```python
# planning_service/migrations/versions/001_initial_schema.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'planning_objectives',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('status', sa.String(50)),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
    )

    op.create_index('idx_planning_status', 'planning_objectives', ['status'])
    op.create_index('idx_planning_org', 'planning_objectives', ['organization_id'])

def downgrade():
    op.drop_index('idx_planning_org')
    op.drop_index('idx_planning_status')
    op.drop_table('planning_objectives')
```

### Running Migrations

```bash
# Run migrations (automatic on service start)
docker-compose up -d planning-service

# Or manually
docker-compose exec planning-service alembic upgrade head

# Check migration status
docker-compose exec planning-service alembic current

# Rollback migration
docker-compose exec planning-service alembic downgrade -1
```

## Backup Configuration

### Automated Backup Setup

**Backup Script (`/etc/cron.daily/postgres-backup.sh`):**

```bash
#!/bin/bash
set -e

BACKUP_DIR="/var/backups/postgresql"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup all databases
docker-compose exec -T postgres pg_dumpall -U bcm_user | gzip > "$BACKUP_DIR/all_databases_$TIMESTAMP.sql.gz"

# Backup individual databases
for db in bcm_platform planning plans governance risk response learning; do
    docker-compose exec -T postgres pg_dump -U bcm_user $db | gzip > "$BACKUP_DIR/${db}_$TIMESTAMP.sql.gz"
done

# Backup schemas only (for quick restore structure)
docker-compose exec -T postgres pg_dump -U bcm_user --schema-only bcm_platform | gzip > "$BACKUP_DIR/schema_$TIMESTAMP.sql.gz"

# Remove old backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Upload to S3 (optional)
# aws s3 sync $BACKUP_DIR s3://your-bucket/postgres-backups/

echo "Backup completed: $TIMESTAMP"
```

Make executable:
```bash
chmod +x /etc/cron.daily/postgres-backup.sh
```

### Point-in-Time Recovery (PITR)

Enable WAL archiving for PITR:

**postgresql.conf:**
```conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/wal_archive/%f'
archive_timeout = 300  # Archive every 5 minutes
```

**Restore from PITR:**
```bash
# 1. Stop PostgreSQL
docker-compose stop postgres

# 2. Restore base backup
tar -xzf base_backup.tar.gz -C /var/lib/postgresql/data

# 3. Create recovery.conf
cat > /var/lib/postgresql/data/recovery.conf <<EOF
restore_command = 'cp /var/lib/postgresql/wal_archive/%f %p'
recovery_target_time = '2024-10-03 12:00:00'
EOF

# 4. Start PostgreSQL (will enter recovery mode)
docker-compose start postgres
```

## Replication Setup (Optional)

### Streaming Replication

**Master Configuration (postgresql.conf):**
```conf
wal_level = replica
max_wal_senders = 3
wal_keep_size = 1GB
synchronous_commit = on
```

**Create replication user:**
```sql
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD '<REPLICATION_PASSWORD>';
```

**pg_hba.conf (allow replication connections):**
```
host    replication     replicator      <REPLICA_IP>/32       md5
```

**Replica Setup:**
```bash
# On replica server, create base backup from master
pg_basebackup -h master_host -U replicator -D /var/lib/postgresql/data -P -R -X stream

# Start replica
docker-compose start postgres
```

**Verify Replication:**
```sql
-- On master
SELECT * FROM pg_stat_replication;

-- On replica
SELECT pg_is_in_recovery();  -- Should return 't' (true)
```

## Monitoring and Maintenance

### Database Health Checks

```sql
-- Check database size
SELECT
    datname AS database,
    pg_size_pretty(pg_database_size(datname)) AS size
FROM pg_database
WHERE datname NOT IN ('template0', 'template1')
ORDER BY pg_database_size(datname) DESC;

-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS index_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- Check active connections
SELECT
    datname,
    count(*) AS connections,
    max(backend_start) AS oldest_connection
FROM pg_stat_activity
GROUP BY datname;

-- Check long-running queries
SELECT
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query,
    state
FROM pg_stat_activity
WHERE state != 'idle'
  AND now() - pg_stat_activity.query_start > interval '5 minutes'
ORDER BY duration DESC;
```

### Vacuum and Analyze

```bash
# Manual vacuum (during low-traffic periods)
docker-compose exec postgres psql -U bcm_user -d bcm_platform -c "VACUUM VERBOSE ANALYZE;"

# Check vacuum stats
docker-compose exec postgres psql -U bcm_user -d bcm_platform -c "
    SELECT
        schemaname,
        tablename,
        last_vacuum,
        last_autovacuum,
        last_analyze,
        last_autoanalyze,
        n_dead_tup
    FROM pg_stat_user_tables
    ORDER BY n_dead_tup DESC
    LIMIT 10;"
```

## Security Hardening

### SSL/TLS Encryption

**Enable SSL in PostgreSQL:**

```conf
# postgresql.conf
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
ssl_ca_file = '/etc/ssl/certs/ca.crt'
```

**Enforce SSL connections (pg_hba.conf):**
```
# Require SSL for all connections
hostssl    all             all             0.0.0.0/0               md5
```

**Client connection with SSL:**
```bash
psql "postgresql://bcm_user@postgres:5432/bcm_platform?sslmode=require"
```

### Encryption at Rest

**Enable data encryption (PostgreSQL 15+):**

```bash
# Install pgcrypto extension
docker-compose exec postgres psql -U bcm_user -d bcm_platform -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"

# Use encrypted columns
CREATE TABLE sensitive_data (
    id SERIAL PRIMARY KEY,
    encrypted_value BYTEA
);

-- Insert encrypted data
INSERT INTO sensitive_data (encrypted_value)
VALUES (pgp_sym_encrypt('sensitive data', 'encryption_key'));

-- Query encrypted data
SELECT pgp_sym_decrypt(encrypted_value, 'encryption_key')
FROM sensitive_data;
```

### Audit Logging

Enable pgAudit extension:

```bash
# Install pgaudit
docker-compose exec postgres psql -U bcm_user -d bcm_platform -c "CREATE EXTENSION IF NOT EXISTS pgaudit;"

# Configure logging
ALTER SYSTEM SET pgaudit.log = 'write, ddl';
ALTER SYSTEM SET pgaudit.log_catalog = off;
SELECT pg_reload_conf();
```

## Troubleshooting

### Common Issues

**Connection Refused:**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Verify port is open
netstat -tuln | grep 5432
```

**Too Many Connections:**
```sql
-- Check current connections
SELECT count(*) FROM pg_stat_activity;

-- Kill idle connections
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND state_change < now() - interval '1 hour';

-- Increase max_connections
ALTER SYSTEM SET max_connections = 200;
SELECT pg_reload_conf();
```

**Slow Queries:**
```sql
-- Enable query timing
\timing on

-- Explain query plan
EXPLAIN ANALYZE SELECT * FROM planning_objectives WHERE status = 'active';

-- Check for missing indexes
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public';
```

**Disk Space Issues:**
```bash
# Check disk usage
docker-compose exec postgres df -h

# Check database sizes
docker-compose exec postgres psql -U bcm_user -c "
    SELECT pg_database.datname,
           pg_size_pretty(pg_database_size(pg_database.datname)) AS size
    FROM pg_database;"

# Vacuum to reclaim space
docker-compose exec postgres psql -U bcm_user -d bcm_platform -c "VACUUM FULL;"
```

## Related Documentation

- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Environment Configuration](./ENVIRONMENT_CONFIGURATION.md)
- [Backup and DR Guide](./BACKUP_DR_GUIDE.md)
- [Performance Tuning](./PERFORMANCE_TUNING.md)

---

**Last Updated:** 2024-10-03
**Document Owner:** Database Engineering Team
