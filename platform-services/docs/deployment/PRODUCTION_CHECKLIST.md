# Production Deployment Checklist

## Pre-Deployment Checklist

### Security Configuration
- [ ] JWT RSA keys generated (4096-bit) and securely stored
- [ ] PostgreSQL password changed from default (min 16 chars, complex)
- [ ] Redis password configured
- [ ] Grafana admin password changed from default
- [ ] All secrets stored in HashiCorp Vault or AWS Secrets Manager
- [ ] SSL/TLS certificates obtained (Let's Encrypt or commercial CA)
- [ ] Certificate auto-renewal configured
- [ ] Firewall rules configured (UFW/iptables)
- [ ] fail2ban installed and configured
- [ ] SSH key-based authentication enabled
- [ ] Root login disabled
- [ ] VPN or bastion host configured for admin access

### Infrastructure Setup
- [ ] Production servers/VMs provisioned
- [ ] DNS A records configured
- [ ] Load balancer configured (nginx/traefik/AWS ALB)
- [ ] CDN configured (if applicable)
- [ ] Backup storage configured (S3/NFS/backup server)
- [ ] Monitoring alerts configured (PagerDuty/Opsgenie)
- [ ] Log aggregation configured (ELK/CloudWatch/Loki)
- [ ] Disk space sufficient (min 100GB, recommended 500GB)
- [ ] RAM adequate (min 16GB, recommended 32GB)
- [ ] CPU cores adequate (min 8, recommended 16)

### Database Configuration
- [ ] PostgreSQL 15+ installed
- [ ] Databases created (bcm_platform, planning, plans, etc.)
- [ ] Database users created with proper permissions
- [ ] Connection pooling configured (PgBouncer recommended)
- [ ] Database indexes created
- [ ] postgresql.conf tuned for production
- [ ] Database encryption at rest enabled
- [ ] SSL/TLS enabled for database connections
- [ ] pg_hba.conf configured to enforce SSL
- [ ] pgaudit extension installed for audit logging
- [ ] Automated backup configured
- [ ] Backup restoration tested
- [ ] Point-in-Time Recovery (PITR) configured
- [ ] Database replication configured (optional)

### Application Configuration
- [ ] Environment variables configured (.env.production)
- [ ] CORS whitelist configured for production domains
- [ ] Rate limiting configured and tested
- [ ] Email/SMTP configuration tested
- [ ] EventBus/RabbitMQ configured
- [ ] Redis cache configured with persistence
- [ ] All service health endpoints verified
- [ ] API documentation updated
- [ ] Service dependencies documented

### Docker Configuration
- [ ] Docker Engine 24.0+ installed
- [ ] Docker Compose 2.20+ installed
- [ ] Production docker-compose.yml reviewed
- [ ] Resource limits configured (CPU, memory)
- [ ] Health checks configured for all services
- [ ] Restart policies set to 'always'
- [ ] Logging driver configured (json-file with rotation)
- [ ] Volume backups tested
- [ ] Images tagged with version numbers
- [ ] Images pushed to private registry

### Monitoring Setup
- [ ] Prometheus installed and configured
- [ ] Grafana installed and configured
- [ ] Grafana dashboards imported
- [ ] Alert rules configured
- [ ] Alert notification channels configured
- [ ] Monitoring service deployed
- [ ] Metrics endpoints verified
- [ ] Log rotation configured
- [ ] Disk space alerts configured
- [ ] Service down alerts configured
- [ ] High error rate alerts configured
- [ ] Database connection alerts configured

### Testing
- [ ] Health check endpoints tested
- [ ] Authentication flow tested
- [ ] Authorization (RBAC) tested
- [ ] Database migrations tested
- [ ] API endpoints tested (Postman/curl)
- [ ] Load testing completed
- [ ] Security scan completed (Trivy, OWASP ZAP)
- [ ] Dependency scan completed
- [ ] Backup and restore tested
- [ ] Failover tested (if HA configured)
- [ ] Disaster recovery plan tested

### Documentation
- [ ] Deployment guide reviewed
- [ ] Runbook created for common operations
- [ ] Troubleshooting guide updated
- [ ] Architecture diagrams created
- [ ] API documentation published
- [ ] Database schema documented
- [ ] Environment variables documented
- [ ] Incident response procedures documented
- [ ] Escalation contacts documented
- [ ] Maintenance procedures documented

### Team Preparation
- [ ] Operations team trained
- [ ] On-call rotation scheduled
- [ ] Access credentials distributed securely
- [ ] Communication channels established (Slack, email)
- [ ] Incident management system configured
- [ ] Post-deployment support plan in place

## Deployment Checklist

### Pre-Deployment Steps
- [ ] Code freeze announced
- [ ] Deployment maintenance window scheduled
- [ ] Stakeholders notified
- [ ] Backup of current production taken
- [ ] Database backup verified
- [ ] Rollback plan documented
- [ ] Deployment runbook reviewed
- [ ] Team on standby (on-call available)

### Deployment Execution
- [ ] Pull latest code from repository
- [ ] Build Docker images with version tags
- [ ] Tag images (version, latest, stable)
- [ ] Push images to registry
- [ ] Stop current services gracefully
- [ ] Start infrastructure services (postgres, redis)
- [ ] Wait for health checks (30-60s)
- [ ] Run database migrations
- [ ] Start application services (planning, plans, bia, compliance)
- [ ] Wait for health checks (30-60s)
- [ ] Start monitoring services (prometheus, grafana)
- [ ] Verify all containers running
- [ ] Check logs for errors

### Post-Deployment Verification
- [ ] All services responding to health checks
- [ ] Database connections successful
- [ ] Redis cache operational
- [ ] Authentication working (login test)
- [ ] API endpoints responding
- [ ] Metrics collecting in Prometheus
- [ ] Grafana dashboards showing data
- [ ] Logs aggregating properly
- [ ] Alerts functional (test alert)
- [ ] Email notifications working
- [ ] SSL certificates valid
- [ ] Load balancer health checks passing
- [ ] Performance baseline captured

### Smoke Tests
- [ ] User login successful
- [ ] Create planning objective
- [ ] Create BCM plan
- [ ] Update plan status
- [ ] Create BIA assessment
- [ ] Run compliance check
- [ ] Generate report
- [ ] View metrics in Grafana
- [ ] Receive alert notification (test)

### Performance Verification
- [ ] Response times acceptable (<500ms for most endpoints)
- [ ] Database query performance acceptable
- [ ] Cache hit rate > 80%
- [ ] CPU usage < 50% at baseline
- [ ] Memory usage < 60% at baseline
- [ ] Disk I/O normal
- [ ] Network latency acceptable

## Post-Deployment Checklist

### Immediate Actions (First Hour)
- [ ] Monitor logs for errors
- [ ] Check error rates in Grafana
- [ ] Verify all health checks green
- [ ] Monitor CPU and memory usage
- [ ] Check database connections
- [ ] Verify backup job scheduled
- [ ] Test critical user workflows
- [ ] Communicate deployment success to stakeholders

### First 24 Hours
- [ ] Monitor error rates continuously
- [ ] Check performance metrics
- [ ] Review slow query logs
- [ ] Verify scheduled jobs running
- [ ] Check disk space trends
- [ ] Monitor alert frequency
- [ ] Review audit logs
- [ ] Gather user feedback
- [ ] Document any issues encountered

### First Week
- [ ] Performance tuning based on metrics
- [ ] Optimize slow queries
- [ ] Adjust resource limits if needed
- [ ] Fine-tune alert thresholds
- [ ] Review and update documentation
- [ ] Conduct post-deployment retrospective
- [ ] Update runbook with lessons learned
- [ ] Schedule security audit

## Rollback Checklist

### When to Rollback
- [ ] Critical security vulnerability discovered
- [ ] Data corruption detected
- [ ] Service unavailability > SLA
- [ ] High error rate (>5%)
- [ ] Performance degradation (>50% slower)
- [ ] Data loss risk identified

### Rollback Steps
- [ ] Announce rollback to team
- [ ] Stop current services
- [ ] Restore previous Docker images
- [ ] Restore database from backup (if needed)
- [ ] Start previous version services
- [ ] Verify rollback successful
- [ ] Run smoke tests
- [ ] Monitor for stability
- [ ] Document rollback reason
- [ ] Create incident report

## Security Hardening Checklist

### System Security
- [ ] OS patches up to date
- [ ] Unnecessary services disabled
- [ ] SSH hardened (key-only, non-standard port)
- [ ] Fail2ban monitoring SSH
- [ ] File permissions reviewed
- [ ] SELinux/AppArmor enabled
- [ ] Audit logging enabled
- [ ] Time synchronization (NTP) configured

### Application Security
- [ ] Input validation on all endpoints
- [ ] SQL injection protection verified
- [ ] XSS protection enabled
- [ ] CSRF protection enabled
- [ ] Security headers configured
- [ ] Rate limiting tested
- [ ] Session management secure
- [ ] Password hashing verified (bcrypt)

### Network Security
- [ ] Firewall rules minimal and documented
- [ ] DDoS protection enabled
- [ ] WAF configured (if applicable)
- [ ] VPN for admin access
- [ ] Network segmentation implemented
- [ ] Internal services not exposed publicly
- [ ] TLS 1.2+ enforced
- [ ] Weak ciphers disabled

## Compliance Checklist

### ISO 22301 Requirements
- [ ] Business Impact Analysis completed
- [ ] Risk Assessment documented
- [ ] BCM Plans created and approved
- [ ] Recovery strategies defined
- [ ] Exercise and testing schedule established
- [ ] Management review conducted
- [ ] Internal audit planned
- [ ] Continual improvement process defined

### Data Protection
- [ ] GDPR compliance reviewed (if applicable)
- [ ] Data retention policy implemented
- [ ] Data deletion procedures tested
- [ ] Privacy policy updated
- [ ] Consent management implemented
- [ ] Data export functionality tested
- [ ] Data breach procedures documented

### Audit and Compliance
- [ ] Audit logging comprehensive
- [ ] Audit logs tamper-proof
- [ ] Compliance reports automated
- [ ] Access logs retained (min 1 year)
- [ ] Change management process followed
- [ ] Compliance dashboard configured

## Maintenance Schedule

### Daily
- [ ] Check service health
- [ ] Review error logs
- [ ] Monitor disk space
- [ ] Verify backups completed

### Weekly
- [ ] Review performance metrics
- [ ] Check security alerts
- [ ] Update dependencies (if needed)
- [ ] Review and clear old logs

### Monthly
- [ ] Review and update documentation
- [ ] Conduct security scan
- [ ] Review access logs
- [ ] Update SSL certificates (if needed)
- [ ] Capacity planning review

### Quarterly
- [ ] Disaster recovery drill
- [ ] Security audit
- [ ] Performance review
- [ ] Documentation review
- [ ] Dependency updates
- [ ] Secret rotation

## Emergency Contacts

### Primary Contacts
- **Platform Lead:** [Name] - [Phone] - [Email]
- **On-Call Engineer:** [Name] - [Phone] - [Email]
- **Backup On-Call:** [Name] - [Phone] - [Email]
- **Database Admin:** [Name] - [Phone] - [Email]
- **Security Team:** [Email] - [Slack Channel]

### Escalation Path
1. On-Call Engineer (Response: 15 min)
2. Platform Lead (Response: 30 min)
3. Engineering Manager (Response: 1 hour)
4. CTO/VP Engineering (Response: 2 hours)

### External Contacts
- **Infrastructure Provider:** [Contact Info]
- **DNS Provider:** [Contact Info]
- **SSL Certificate Authority:** [Contact Info]
- **Managed Services:** [Contact Info]

## Sign-off

### Deployment Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Platform Lead | | | |
| Security Lead | | | |
| Operations Lead | | | |
| Engineering Manager | | | |

### Deployment Confirmation

**Deployment Date:** _______________
**Deployment Time:** _______________
**Version Deployed:** _______________
**Deployed By:** _______________

**Verification:**
- [ ] All checklist items completed
- [ ] No critical issues identified
- [ ] Performance within acceptable range
- [ ] Security verification passed
- [ ] Backup verified
- [ ] Monitoring operational
- [ ] Team notified

**Notes:**
```
[Add any deployment notes, issues encountered, or deviations from plan]
```

---

**Last Updated:** 2024-10-03
**Document Owner:** Platform Engineering Team
**Next Review:** Quarterly
