# Troubleshooting Guide

## Common Issues and Solutions

### Service Won't Start

**Symptoms:** Container exits immediately or won't start

**Diagnosis:**
```bash
# Check container status
docker compose ps

# View logs
docker compose logs service-name

# Check for port conflicts
sudo lsof -i :8011
sudo netstat -tuln | grep 8011
```

**Solutions:**
1. **Port already in use:**
   ```bash
   # Kill process using the port
   sudo kill -9 $(lsof -ti:8011)
   # Or change port in docker-compose.yml
   ```

2. **Environment variables missing:**
   ```bash
   # Verify .env file exists and contains required vars
   cat .env | grep -E "POSTGRES_PASSWORD|JWT_PUBLIC_KEY"
   ```

3. **Image build failed:**
   ```bash
   # Rebuild without cache
   docker compose build --no-cache service-name
   ```

### Database Connection Errors

**Symptoms:** "Connection refused" or "Could not connect to server"

**Diagnosis:**
```bash
# Check PostgreSQL is running
docker compose ps postgres

# Test connection
docker compose exec postgres pg_isready -U bcm_user

# Check logs
docker compose logs postgres
```

**Solutions:**
1. **PostgreSQL not ready:**
   ```bash
   # Wait for health check
   docker compose up -d postgres
   sleep 30
   docker compose exec postgres pg_isready
   ```

2. **Wrong credentials:**
   ```bash
   # Verify credentials match .env
   docker compose exec postgres psql -U bcm_user -d bcm_platform
   ```

3. **Database doesn't exist:**
   ```bash
   # Create database
   docker compose exec postgres psql -U bcm_user -c "CREATE DATABASE bcm_platform;"
   ```

### High CPU/Memory Usage

**Symptoms:** Slow response times, system freeze

**Diagnosis:**
```bash
# Check container resource usage
docker stats

# Check system resources
top
htop
free -h
df -h
```

**Solutions:**
1. **Increase resource limits:**
   ```yaml
   # docker-compose.yml
   deploy:
     resources:
       limits:
         cpus: '2.0'
         memory: 2G
   ```

2. **Optimize PostgreSQL:**
   ```sql
   -- Check slow queries
   SELECT query, calls, mean_exec_time
   FROM pg_stat_statements
   ORDER BY mean_exec_time DESC
   LIMIT 10;

   -- Run VACUUM
   VACUUM ANALYZE;
   ```

3. **Clear Redis cache:**
   ```bash
   docker compose exec redis redis-cli FLUSHDB
   ```

### Slow Queries

**Symptoms:** Timeouts, slow API responses

**Diagnosis:**
```sql
-- Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 1000; -- Log queries > 1s
SELECT pg_reload_conf();

-- View slow queries
SELECT * FROM pg_stat_activity WHERE state != 'idle' AND now() - query_start > interval '5 seconds';
```

**Solutions:**
1. **Add missing indexes:**
   ```sql
   -- Find missing indexes
   SELECT schemaname, tablename, seq_scan, seq_tup_read
   FROM pg_stat_user_tables
   WHERE seq_scan > 0
   ORDER BY seq_tup_read DESC
   LIMIT 10;

   -- Create index
   CREATE INDEX idx_table_column ON table_name(column_name);
   ```

2. **Optimize query:**
   ```sql
   EXPLAIN ANALYZE SELECT ...;
   ```

### Authentication Failures

**Symptoms:** 401 Unauthorized, JWT errors

**Diagnosis:**
```bash
# Check JWT configuration
docker compose exec planning-service env | grep JWT

# Test token generation
curl -X POST http://localhost:8011/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'
```

**Solutions:**
1. **JWT keys mismatch:**
   ```bash
   # Verify JWT_PUBLIC_KEY matches JWT_PRIVATE_KEY
   # Regenerate keys if needed
   openssl genrsa -out jwt_private.key 4096
   openssl rsa -in jwt_private.key -pubout -out jwt_public.key
   ```

2. **Token expired:**
   ```bash
   # Increase JWT_EXPIRATION_HOURS
   export JWT_EXPIRATION_HOURS=24
   ```

### Docker Issues

**Out of Disk Space:**
```bash
# Clean up Docker resources
docker system prune -a --volumes

# Check disk usage
docker system df

# Remove specific items
docker volume ls -qf dangling=true | xargs docker volume rm
docker image prune -a
```

**Network Issues:**
```bash
# Recreate network
docker network rm bcm-network
docker compose up -d

# DNS issues
docker exec container_name cat /etc/resolv.conf
```

**Container Restart Loop:**
```bash
# Check logs
docker logs container_name --tail 100

# Disable restart policy temporarily
docker update --restart=no container_name

# Debug with shell
docker compose run --rm service-name sh
```

### Redis Connection Issues

**Symptoms:** Cache errors, timeouts

**Diagnosis:**
```bash
# Test connection
docker compose exec redis redis-cli ping

# Check memory
docker compose exec redis redis-cli INFO memory

# Monitor commands
docker compose exec redis redis-cli MONITOR
```

**Solutions:**
```bash
# Restart Redis
docker compose restart redis

# Clear cache
docker compose exec redis redis-cli FLUSHALL

# Check password
docker compose exec redis redis-cli -a your_password ping
```

### Health Check Failures

**Symptoms:** Container marked unhealthy

**Diagnosis:**
```bash
# Check health status
docker inspect --format='{{json .State.Health}}' container_name | jq

# Manual health check
curl -v http://localhost:8011/health
```

**Solutions:**
```bash
# Increase health check timeout
# In docker-compose.yml:
healthcheck:
  timeout: 30s
  start_period: 120s

# Check logs during health check
docker compose logs -f service-name
```

### Migration Failures

**Symptoms:** Database schema errors

**Diagnosis:**
```bash
# Check migration status
docker compose exec planning-service alembic current

# View migration history
docker compose exec planning-service alembic history
```

**Solutions:**
```bash
# Run migrations manually
docker compose exec planning-service alembic upgrade head

# Rollback migration
docker compose exec planning-service alembic downgrade -1

# Reset and re-run
docker compose exec planning-service alembic downgrade base
docker compose exec planning-service alembic upgrade head
```

## Diagnostic Commands

### System Information
```bash
# OS and kernel
uname -a
cat /etc/os-release

# Disk space
df -h
du -sh /var/lib/docker

# Memory
free -h
cat /proc/meminfo

# CPU
lscpu
top -bn1 | head -20
```

### Docker Diagnostics
```bash
# Docker version
docker version
docker info

# Container status
docker compose ps
docker ps -a

# Resource usage
docker stats --no-stream

# Network
docker network ls
docker network inspect bcm-network

# Volumes
docker volume ls
docker volume inspect platform-services_postgres_data
```

### Service Diagnostics
```bash
# All service health
./docs/deployment/scripts/health_check.sh --verbose

# Database
docker compose exec postgres psql -U bcm_user -c "\l"
docker compose exec postgres psql -U bcm_user -d bcm_platform -c "\dt"

# Redis
docker compose exec redis redis-cli INFO
docker compose exec redis redis-cli DBSIZE

# Application logs
docker compose logs --tail=100 -f planning-service
```

## Emergency Procedures

### Complete System Restart
```bash
# 1. Stop all services
docker compose down

# 2. Clean up (optional)
docker system prune -f

# 3. Start infrastructure
docker compose up -d postgres redis

# 4. Wait for health
sleep 30

# 5. Start services
docker compose up -d
```

### Restore from Backup
```bash
# Use restore script
./docs/deployment/scripts/restore.sh <timestamp>

# Or manual restore
docker compose down
docker compose up -d postgres
sleep 20
zcat /var/backups/bcm/backup.sql.gz | docker compose exec -T postgres psql -U bcm_user
docker compose up -d
```

### Rollback Deployment
```bash
# Stop current version
docker compose down

# Pull previous version
docker pull bcm/planning-service:previous-version

# Update docker-compose.yml with previous version tag
# Start services
docker compose up -d
```

## Getting Help

If issues persist:

1. **Collect diagnostic information:**
   ```bash
   ./docs/deployment/scripts/health_check.sh --verbose > diagnostics.txt
   docker compose logs > service_logs.txt
   docker system df > disk_usage.txt
   ```

2. **Contact support:**
   - Platform Team: platform-support@yourdomain.com
   - On-Call: Check PagerDuty
   - Emergency: Call platform lead

3. **Create incident report:**
   - Document symptoms
   - Steps to reproduce
   - Logs and error messages
   - Actions taken

---

**Last Updated:** 2024-10-03
