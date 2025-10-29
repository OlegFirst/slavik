# Grafana/Prometheus Monitoring Stack for BCM Platform

Comprehensive monitoring, alerting, and observability solution for the Business Continuity Management Platform, providing real-time insights into system health, business continuity metrics, and compliance tracking.

## 🏗️ Architecture

```
BCM Platform → Prometheus → Grafana Dashboards
     ↓              ↑              ↑
   Metrics      AlertManager → Notifications
     ↓              ↑              ↑
 Loki Logs ←→ Promtail ←→ Log Aggregation
```

## 🚀 Features

### ✅ Comprehensive Monitoring
- **BCM Platform metrics** - Application performance and business metrics
- **System monitoring** - CPU, memory, disk, network metrics
- **Database monitoring** - PostgreSQL performance and health
- **Integration services** - TheHive, Moodle bridge health
- **Container monitoring** - Docker container metrics and logs

### ✅ Business Continuity Dashboards
- **Incident response** metrics and RTO/RPO tracking
- **Training compliance** monitoring and reporting
- **Plan review status** and compliance alerts
- **Exercise tracking** and effectiveness metrics
- **Stakeholder engagement** analytics

### ✅ Intelligent Alerting
- **Multi-channel notifications** - Email, Slack, PagerDuty
- **Severity-based routing** - Critical alerts to on-call team
- **Business continuity alerts** - RTO breach, compliance issues
- **Alert inhibition** - Reduce noise with smart suppression
- **Escalation policies** - Progressive alert escalation

### ✅ Log Aggregation & Analysis
- **Centralized logging** with Loki and Promtail
- **Structured log parsing** for BCM Platform components
- **Security event logging** with audit trail
- **Compliance logging** for ISO 22301 requirements
- **Log-based alerting** for security and compliance events

## 📦 Components

### 1. Prometheus Server
- **Metrics collection** from BCM Platform and integrations
- **Time-series database** with 30-day retention
- **Alert evaluation** based on business rules
- **Service discovery** for dynamic environments

### 2. Grafana Dashboards
- **BCM Platform Overview** - Executive dashboard
- **System Resources** - Infrastructure monitoring
- **Business Continuity** - BCM-specific metrics
- **Integration Services** - TheHive, Moodle monitoring
- **Security & Compliance** - Audit and compliance tracking

### 3. AlertManager
- **Alert routing** by severity and component
- **Notification channels** - Email, Slack, PagerDuty
- **Inhibition rules** to reduce alert fatigue
- **Silencing** for maintenance windows

### 4. Exporters & Collectors
- **Node Exporter** - System metrics
- **cAdvisor** - Container metrics
- **PostgreSQL Exporter** - Database metrics
- **Redis Exporter** - Cache metrics
- **Blackbox Exporter** - Endpoint monitoring

### 5. Log Stack
- **Loki** - Log aggregation and storage
- **Promtail** - Log collection and forwarding
- **Log parsing** - Structured log extraction
- **Log-based alerts** - Real-time log monitoring

## 🛠️ Setup & Deployment

### Prerequisites
- Docker & Docker Compose
- BCM Platform running
- Network access between monitoring and BCM services

### 1. Environment Configuration
```bash
# Copy and configure environment
cp .env.example .env

# Configure required variables
GRAFANA_ADMIN_PASSWORD=secure_admin_password
GRAFANA_DB_PASSWORD=secure_db_password
BCM_DB_USER=odoo
BCM_DB_PASSWORD=your_bcm_db_password
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
SMTP_HOST=smtp.your-domain.com
SMTP_USERNAME=alerts@your-domain.com
SMTP_PASSWORD=your_smtp_password
PAGERDUTY_BCM_CRITICAL_KEY=your_pagerduty_key
```

### 2. Deploy Monitoring Stack
```bash
# Start all monitoring services
docker-compose -f docker-compose.monitoring.yml up -d

# Check service health
docker-compose -f docker-compose.monitoring.yml ps

# View service logs
docker-compose -f docker-compose.monitoring.yml logs -f grafana
```

### 3. Access Dashboards
```bash
# Grafana Dashboard
open http://localhost:3000
# Default login: admin / (configured password)

# Prometheus
open http://localhost:9090

# AlertManager
open http://localhost:9093
```

### 4. Import BCM Dashboards
```bash
# Dashboards are automatically provisioned
# Additional dashboards can be imported via Grafana UI
# Dashboard IDs: 
# - BCM Platform Overview: bcm-overview
# - System Resources: system-resources
# - Business Continuity: bcm-business
```

## 📊 Key Metrics & KPIs

### BCM Platform Business Metrics
```promql
# Active incidents by severity
bcm_incidents_total{severity="critical"}

# Training compliance percentage
bcm_training_compliance_percentage

# RTO/RPO compliance
bcm_incident_rto_compliance_ratio

# Plan review status
bcm_plans_review_overdue_total

# Exercise completion rate
bcm_exercises_completion_rate

# Stakeholder engagement
bcm_stakeholder_engagement_score
```

### System Performance Metrics
```promql
# Application response time
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_requests_total{code=~"5.."}[5m])

# Database connections
pg_stat_activity_count

# System resources
100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

### Integration Health Metrics
```promql
# Service availability
up{job=~".*bridge|.*webhook"}

# Integration response time
probe_duration_seconds

# Integration error rate
rate(integration_requests_total{status="error"}[5m])
```

## 🚨 Alerting Rules

### Critical Business Continuity Alerts
- **BCM Critical Incident Created** - Immediate response required
- **RTO Threshold Breached** - Recovery time objective exceeded
- **Training Compliance Low** - Below regulatory threshold
- **Plan Review Overdue** - Compliance risk identified

### System Health Alerts
- **BCM Platform Down** - Core service unavailable
- **Database Connection Issues** - Data access problems
- **High Response Time** - Performance degradation
- **Resource Exhaustion** - CPU/Memory/Disk critical

### Integration Service Alerts
- **TheHive Integration Down** - Incident management affected
- **Moodle Integration Down** - Training system unavailable
- **Webhook Delivery Failed** - Data synchronization issues
- **SSL Certificate Expiry** - Security risk identified

## 📈 Dashboard Overview

### BCM Platform Executive Dashboard
- **Service Health Overview** - All-green status display
- **Active Incidents Counter** - Real-time incident tracking
- **Training Compliance Gauge** - Current compliance percentage
- **Response Time Trends** - Performance over time
- **Recent Alerts List** - Latest system alerts

### Business Continuity Dashboard
- **Incident Response Metrics** - MTTR, RTO compliance
- **Training Analytics** - Completion rates by department
- **Plan Management** - Review status and updates
- **Exercise Tracking** - Scheduled and completed exercises
- **Stakeholder Engagement** - Communication effectiveness

### System Resources Dashboard
- **Infrastructure Health** - CPU, Memory, Disk utilization
- **Database Performance** - Query performance, connections
- **Container Metrics** - Docker container resources
- **Network Performance** - Bandwidth and latency
- **Storage Analytics** - Disk usage and I/O performance

## 🔐 Security & Compliance

### Security Monitoring
- **Authentication failures** tracking and alerting
- **Unauthorized access** attempts monitoring
- **Data access patterns** anomaly detection
- **Privilege escalation** alerts
- **API abuse** detection and prevention

### Compliance Reporting
- **Audit trail** completeness and integrity
- **Data retention** policy compliance
- **Access log** completeness for ISO 22301
- **Incident response** time compliance
- **Training record** completeness and accuracy

## 🔧 Troubleshooting

### Common Issues

#### Prometheus Connection Issues
```bash
# Check Prometheus service
curl http://localhost:9090/-/healthy

# Verify target discovery
curl http://localhost:9090/api/v1/targets

# Check configuration
docker exec bcm-prometheus promtool check config /etc/prometheus/prometheus.yml
```

#### Grafana Dashboard Issues
```bash
# Check Grafana logs
docker logs bcm-grafana

# Verify datasource connectivity
curl -u admin:password http://localhost:3000/api/health

# Test Prometheus datasource
curl -u admin:password http://localhost:3000/api/datasources/proxy/1/api/v1/query?query=up
```

#### AlertManager Issues
```bash
# Check AlertManager status
curl http://localhost:9093/-/healthy

# Verify alert routing
curl http://localhost:9093/api/v1/alerts

# Test notification channels
curl -XPOST http://localhost:9093/api/v1/alerts -d @test-alert.json
```

#### Loki Log Issues
```bash
# Check Loki health
curl http://localhost:3100/ready

# Verify log ingestion
curl http://localhost:3100/loki/api/v1/labels

# Test log queries
curl 'http://localhost:3100/loki/api/v1/query?query={job="bcm-platform"}'
```

## 🚀 Production Deployment

### High Availability Setup
- **Prometheus clustering** with remote storage
- **Grafana clustering** with external database
- **AlertManager clustering** with gossip protocol
- **Loki clustering** with object storage backend
- **Load balancing** for dashboard access

### Backup & Recovery
- **Prometheus data** backup with remote storage
- **Grafana configuration** backup and versioning
- **Alert rule** backup and version control
- **Dashboard export** and import procedures
- **Log data** retention and archiving

### Security Hardening
- **TLS encryption** for all communication
- **Authentication** with LDAP/SSO integration
- **Authorization** with role-based access control
- **Network segmentation** for monitoring services
- **Secret management** with external vaults

---

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [AlertManager Configuration](https://prometheus.io/docs/alerting/latest/configuration/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [BCM Platform Metrics API](../../../docs/api/metrics/)
