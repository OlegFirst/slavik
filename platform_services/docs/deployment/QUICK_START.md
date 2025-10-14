# Quick Start: Production Deployment

## 5-Minute Production Setup

This guide gets you from zero to production deployment in minimal steps.

### Prerequisites Check

```bash
# Verify Docker installed
docker --version  # Should be 24.0+
docker compose version  # Should be 2.20+

# Check disk space (min 50GB free)
df -h

# Check you're in project root
pwd  # Should end with /platform-services
```

### Step 1: Generate JWT Keys (2 minutes)

```bash
# Generate RSA 4096 keys
openssl genrsa -out jwt_private.key 4096
openssl rsa -in jwt_private.key -pubout -out jwt_public.key

# Base64 encode (single line)
export JWT_PRIVATE_KEY=$(cat jwt_private.key | base64 | tr -d '\n')
export JWT_PUBLIC_KEY=$(cat jwt_public.key | base64 | tr -d '\n')

# Store securely and delete files
chmod 600 jwt_private.key
mv jwt_private.key ~/.ssh/bcm_jwt_private.key
rm jwt_public.key
```

### Step 2: Configure Environment (2 minutes)

```bash
# Copy template
cp .env.example .env

# Edit .env with required values
cat > .env << EOF
# Database
POSTGRES_PASSWORD=$(openssl rand -base64 32)
POSTGRES_USER=bcm_user
POSTGRES_DB=bcm_platform

# Redis
REDIS_PASSWORD=$(openssl rand -base64 32)

# JWT
JWT_PUBLIC_KEY=${JWT_PUBLIC_KEY}
JWT_PRIVATE_KEY=${JWT_PRIVATE_KEY}
JWT_ALGORITHM=RS256

# Grafana
GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 24)

# Monitoring
ALERT_EMAIL=alerts@yourdomain.com

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
EOF
```

### Step 3: Deploy (1 minute)

```bash
# Option A: Use automated script (recommended)
./docs/deployment/scripts/deploy.sh v1.0.0

# Option B: Manual Docker Compose
docker compose -f docker-compose.prod.yml up -d

# Wait for services to start
sleep 60
```

### Step 4: Verify Deployment

```bash
# Quick health check
./docs/deployment/scripts/health_check.sh

# Or manual check
curl http://localhost:8011/health  # Planning Service
curl http://localhost:8023/health  # Plans Service
curl http://localhost:8012/health  # BIA Service
curl http://localhost:8014/health  # Compliance Service

# Check all services running
docker compose ps
```

### Step 5: Access Services

- **Planning Service:** http://localhost:8011
- **Plans Service:** http://localhost:8023
- **BIA Service:** http://localhost:8012
- **Compliance Service:** http://localhost:8014
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000 (admin / [password from .env])

## Production Hardening (Additional 10 minutes)

### 1. Set Up nginx Reverse Proxy

```bash
# Install nginx
sudo apt-get install nginx

# Create config
sudo tee /etc/nginx/sites-available/bcm << 'EOF'
server {
    listen 80;
    server_name bcm.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name bcm.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/bcm.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bcm.yourdomain.com/privkey.pem;

    location /api/planning/ {
        proxy_pass http://localhost:8011/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/plans/ {
        proxy_pass http://localhost:8023/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# Enable and restart
sudo ln -s /etc/nginx/sites-available/bcm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 2. Configure SSL with Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d bcm.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 0 * * * certbot renew --quiet && systemctl reload nginx
```

### 3. Set Up Automated Backups

```bash
# Create backup cron job
sudo crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/bcm-platform/docs/deployment/scripts/backup.sh full

# Test backup
./docs/deployment/scripts/backup.sh full
ls -lh /var/backups/bcm/
```

### 4. Configure Firewall

```bash
# Install and configure UFW
sudo apt-get install ufw

# Allow necessary ports
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Deny direct service access
sudo ufw deny 8011/tcp
sudo ufw deny 8023/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

## Monitoring Setup (5 minutes)

### 1. Access Grafana

```bash
# Get Grafana password
grep GRAFANA_ADMIN_PASSWORD .env

# Open browser
open http://localhost:3000

# Login: admin / [password]
```

### 2. Import Dashboards

In Grafana:
1. Click "+" → Import
2. Upload: `monitoring/grafana/dashboards/bcm-overview.json`
3. Select Prometheus datasource
4. Click Import

### 3. Configure Alerts

```bash
# Edit Prometheus alerts
vim monitoring/prometheus/alerts/bcm-alerts.yml

# Reload Prometheus
curl -X POST http://localhost:9090/-/reload
```

## Common Commands

### Deployment
```bash
# Deploy new version
./docs/deployment/scripts/deploy.sh v1.1.0

# Check status
docker compose ps
./docs/deployment/scripts/health_check.sh
```

### Backup & Restore
```bash
# Backup
./docs/deployment/scripts/backup.sh full

# List backups
ls -lh /var/backups/bcm/database/

# Restore
./docs/deployment/scripts/restore.sh 20241003_120000
```

### Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f planning-service

# Last 100 lines
docker compose logs --tail=100 planning-service
```

### Restart Services
```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart planning-service

# Complete restart
docker compose down && docker compose up -d
```

## Troubleshooting Quick Fixes

### Service Won't Start
```bash
# Check logs
docker compose logs service-name

# Rebuild and restart
docker compose build --no-cache service-name
docker compose up -d service-name
```

### Database Connection Issues
```bash
# Check PostgreSQL
docker compose exec postgres pg_isready -U bcm_user

# Reset connection
docker compose restart postgres
sleep 20
docker compose restart planning-service plans-service
```

### High Memory Usage
```bash
# Check resources
docker stats

# Restart services
docker compose restart

# Clear Redis cache
docker compose exec redis redis-cli FLUSHDB
```

## Security Checklist

Before going live:
- [ ] Change all default passwords
- [ ] Enable HTTPS (nginx + Let's Encrypt)
- [ ] Configure firewall (UFW)
- [ ] Set up automated backups
- [ ] Configure monitoring alerts
- [ ] Review and test rollback procedures
- [ ] Document emergency contacts

## Next Steps

For comprehensive documentation:
1. Read [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
2. Complete [PRODUCTION_CHECKLIST.md](./PRODUCTION_CHECKLIST.md)
3. Review [SECURITY_GUIDE.md](./SECURITY_GUIDE.md)
4. Set up [CI/CD Pipeline](./CICD_PIPELINE.md)

## Support

- Documentation: [README.md](./README.md)
- Troubleshooting: [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md)
- Emergency: Check PagerDuty or contact on-call engineer

---

**You're production ready!** 🎉

The platform is deployed and running. Monitor health checks and review logs for the first 24 hours.
