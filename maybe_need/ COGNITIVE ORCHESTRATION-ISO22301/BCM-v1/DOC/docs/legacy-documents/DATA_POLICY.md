# Data Policy - BCM Platform

## Data Retention

### Default Retention Periods
- **Event logs**: 90 days (configurable)
- **Audit trails**: 7 years (regulatory requirement)
- **Incident records**: 3 years minimum
- **BIA/BCP documents**: Permanent (versioned)
- **Exercise results**: 2 years
- **System metrics**: 30 days

### Archival Strategy
```yaml
hot_storage: 0-30 days     # Redis/PostgreSQL
warm_storage: 31-90 days   # PostgreSQL compressed
cold_storage: 91+ days     # S3/Object storage
```

## Backup Strategy

### Database Backups
- **Frequency**: Daily full + hourly incremental
- **Retention**: 30 daily, 12 monthly, 5 yearly
- **PITR (Point-in-Time Recovery)**: Last 7 days
- **RPO**: 1 hour maximum
- **RTO**: 4 hours for full restore

### Backup Procedures
```bash
# PostgreSQL PITR setup
postgresql.conf:
  wal_level = replica
  archive_mode = on
  archive_command = 'test ! -f /backup/wal/%f && cp %p /backup/wal/%f'

# Daily backup script
pg_basebackup -h localhost -D /backup/base/$(date +%Y%m%d) -Ft -z -P

# Restore procedure
pg_ctl stop
rm -rf $PGDATA/*
tar -xzf /backup/base/20250825.tar.gz -C $PGDATA
cp /backup/wal/* $PGDATA/pg_wal/
pg_ctl start
```

### Document Storage
- **Primary**: PostgreSQL + filesystem
- **Backup**: S3 with versioning enabled
- **Replication**: Cross-region for DR

## Encryption

### Data at Rest
- **Database**: Transparent Data Encryption (TDE)
- **Filesystem**: LUKS/dm-crypt on Linux
- **Object Storage**: SSE-S3 or SSE-KMS
- **Backups**: AES-256 encryption

### Data in Transit
- **External APIs**: TLS 1.3 minimum
- **Internal services**: mTLS between services
- **Database connections**: SSL required
- **Message queue**: TLS + SASL

### Key Management
```yaml
master_key: AWS KMS / HashiCorp Vault
data_keys: Rotated monthly
api_keys: Rotated quarterly
certificates: Auto-renewed via Let's Encrypt
```

## Compliance

### GDPR Requirements
- **Right to erasure**: Soft delete + hard delete after 30 days
- **Data portability**: Export in JSON/CSV formats
- **Consent tracking**: Audit log of all consents
- **Data minimization**: Only collect required fields

### ISO 27001 Controls
- A.8.2.3: Handling of assets
- A.12.3.1: Information backup
- A.18.1.3: Protection of records

### Audit Logging
```json
{
  "timestamp": "2025-08-25T10:00:00Z",
  "user_id": "usr_123",
  "action": "document.upload",
  "resource": "doc_456",
  "ip_address": "192.168.1.1",
  "result": "success",
  "metadata": {
    "file_size": 1024000,
    "document_type": "BCP"
  }
}
```

## Data Classification

| Level | Description | Examples | Controls |
|-------|------------|----------|----------|
| Public | No impact if disclosed | Marketing materials | None |
| Internal | Low impact | Procedures, templates | Access control |
| Confidential | Medium impact | Client data, BIA | Encryption + audit |
| Secret | High impact | Credentials, PII | HSM + strict access |

## Monitoring & Alerts

### Key Metrics
- Storage usage > 80%
- Backup failure
- Encryption key rotation due
- Unauthorized access attempts
- Data export requests

### Grafana Dashboards
1. **Data Volume Dashboard**
   - Storage growth rate
   - Retention compliance
   - Backup success rate

2. **Security Dashboard**
   - Encryption status
   - Access patterns
   - Anomaly detection

3. **Compliance Dashboard**
   - GDPR requests
   - Audit trail integrity
   - Data classification coverage

## Incident Response

### Data Breach Procedure
1. **Detect**: Alert within 15 minutes
2. **Contain**: Isolate affected systems
3. **Assess**: Determine scope and impact
4. **Notify**: Regulatory bodies within 72 hours
5. **Remediate**: Patch and restore services
6. **Review**: Post-incident analysis

### Recovery Procedures
```bash
# Verify backup integrity
pg_verifybackup /backup/base/20250825

# Test restore to staging
docker run -v /backup:/backup postgres:15 \
  pg_restore -d bcm_staging /backup/bcm_prod.dump

# Validate data consistency
psql -c "SELECT COUNT(*) FROM bcm_incidents"
```

## Rate Limiting

### Per-Tenant Limits
```yaml
api_calls:
  standard: 1000/hour
  premium: 10000/hour
  enterprise: unlimited

data_operations:
  upload: 100MB/file, 1GB/day
  export: 10 requests/day
  ai_analysis: 100 documents/day
```

### Implementation
```python
# Redis-based rate limiting
key = f"rate:{tenant_id}:{endpoint}"
count = redis.incr(key)
redis.expire(key, 3600)  # 1 hour window

if count > limit:
    raise RateLimitExceeded()
```

## Data Quality

### Validation Rules
- Required fields cannot be null
- Dates must be in ISO 8601 format
- Email addresses must be valid
- Phone numbers normalized to E.164

### Deduplication
- Event deduplication by event_id
- Document deduplication by hash
- Client deduplication by email/tax_id

## Contact

**Data Protection Officer**: dpo@bcm-platform.com
**Security Team**: security@bcm-platform.com
**Compliance**: compliance@bcm-platform.com

---

*Last Updated: 2025-08-25*
*Version: 1.0.0*
*Review Schedule: Quarterly*
