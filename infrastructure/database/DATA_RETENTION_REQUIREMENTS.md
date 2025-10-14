# 📦 DATA RETENTION & ARCHIVING - REQUIREMENTS

**Дата**: 2025-10-11
**Статус**: ⚠️ Not Implemented (Required!)
**Приоритет**: HIGH (для ISO 22301 compliance)

---

## 🎯 ТЕКУЩАЯ СИТУАЦИЯ

### ✅ Что уже есть (DB Intelligence):

**DB Intelligence Specialist** (Port 8050) следит за:
- ✅ Dead rows detection (мёртвые данные)
- ✅ VACUUM execution (очистка)
- ✅ Table sizes monitoring
- ✅ Last vacuum/analyze timestamps

**Файл**: `/Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/db-intelligence/`

### ❌ Чего НЕТ (требуется добавить):

- ❌ **Data Retention Policies** - автоматическое удаление старых данных
- ❌ **Archive Strategy** - перенос данных в архив
- ❌ **Partitioning** - разбиение больших таблиц по датам
- ❌ **Lifecycle Management** - управление жизненным циклом данных
- ❌ **Compliance Reports** - отчёты по хранению (ISO 22301)

---

## 📋 ТРЕБОВАНИЯ ISO 22301

### Clause 7.5.3 - Control of documented information

**Документированная информация должна:**
1. ✅ Быть доступна и подходящая для использования
2. ✅ Адекватно защищена (encryption, RLS)
3. ⚠️ **Храниться и сохраняться определённый период** ← НЕТ!
4. ⚠️ **Контролироваться изменения** ← Частично
5. ⚠️ **Архивироваться или удаляться** ← НЕТ!

### Clause 8.5 - Monitoring and Review

**Требования к данным мониторинга:**
- ✅ Мониторинг производительности
- ⚠️ Хранение логов минимум 90 дней ← Не реализовано!
- ⚠️ Архивация исторических данных ← Не реализовано!

---

## 🏗️ АРХИТЕКТУРА РЕШЕНИЯ

### Вариант 1: Расширить DB Intelligence (рекомендуется)

**Добавить модуль Data Retention в существующий сервис:**

```
db-intelligence/ (Port 8050)
├── db_intelligence_service.py   - Core monitoring
├── retention_manager.py          - NEW! Data retention policies
├── archive_service.py            - NEW! Archive old data
├── partitioning_manager.py       - NEW! Table partitioning
└── compliance_reporter.py        - NEW! Compliance reports
```

**Преимущества:**
- ✅ Единая точка управления БД
- ✅ Переиспользование существующего мониторинга
- ✅ Меньше микросервисов

**Недостатки:**
- 🟡 Один сервис выполняет много функций

### Вариант 2: Отдельный Data Retention Service

**Создать новый микросервис:**

```
data-retention-service/ (Port 8060)
├── retention_policies.py         - Policy engine
├── archive_scheduler.py          - Archive scheduling
├── partition_manager.py          - Partition management
├── compliance_reporter.py        - ISO compliance reports
└── api.py                        - REST API
```

**Преимущества:**
- ✅ Separation of concerns
- ✅ Независимое масштабирование
- ✅ Специализированный сервис

**Недостатки:**
- 🔴 Дублирование кода с DB Intelligence
- 🔴 Еще один сервис для поддержки

---

## 🎯 РЕКОМЕНДАЦИЯ: Вариант 1 (расширить DB Intelligence)

**Обоснование:**
1. DB Intelligence уже мониторит таблицы
2. Логически связанные функции
3. Меньше overhead

---

## 📝 RETENTION POLICIES (что нужно хранить)

### 1. Audit Logs (audit.security_events)

```yaml
policy:
  retention: 365 days  # 1 year for compliance
  archive_after: 90 days  # Archive to cold storage
  partition_by: created_at (monthly)

actions:
  - Delete logs older than 365 days
  - Archive logs 90-365 days to S3/MinIO
  - Keep only 90 days in hot database
```

### 2. Business Impact Analysis (bia.*)

```yaml
policy:
  retention: 7 years  # Legal requirement
  archive_after: 2 years  # Archive inactive
  partition_by: created_at (yearly)

actions:
  - Never delete (7 year retention)
  - Archive > 2 years to archive DB
  - Keep active data in main DB
```

### 3. Compliance Reports (compliance.*)

```yaml
policy:
  retention: 10 years  # ISO 22301 requirement
  archive_after: 3 years
  partition_by: report_date (yearly)

actions:
  - Keep 10 years minimum
  - Archive > 3 years
  - Compressed storage for old reports
```

### 4. Workflow Execution Logs (workflow_intelligence.*)

```yaml
policy:
  retention: 180 days  # 6 months
  archive_after: 30 days
  partition_by: started_at (monthly)

actions:
  - Delete logs > 180 days
  - Archive 30-180 days
  - Keep only 30 days hot
```

### 5. Learning System Data (learning.*)

```yaml
policy:
  retention: 3 years
  archive_after: 1 year
  partition_by: created_at (yearly)

actions:
  - Keep 3 years for ML training
  - Archive > 1 year to data lake
  - Active learning in main DB
```

### 6. Temporary Data (session, cache)

```yaml
policy:
  retention: 7 days
  archive_after: never
  partition_by: none

actions:
  - Auto-delete > 7 days
  - No archiving (temp data)
  - Cleanup daily
```

---

## 💻 IMPLEMENTATION PLAN

### Phase 1: Retention Policies (Week 1)

**Day 1-2: Define Policies**
```python
# /infrastructure/database/retention/policies.py

from enum import Enum
from dataclasses import dataclass
from datetime import timedelta

class RetentionPolicy(Enum):
    AUDIT_LOGS = "audit_logs"
    BIA_DATA = "bia_data"
    COMPLIANCE = "compliance"
    WORKFLOW_LOGS = "workflow_logs"
    LEARNING_DATA = "learning_data"
    TEMP_DATA = "temp_data"

@dataclass
class PolicyConfig:
    schema: str
    table: str
    retention_days: int
    archive_after_days: int
    partition_by: str  # column name
    partition_interval: str  # 'daily', 'monthly', 'yearly'

    # Actions
    auto_delete: bool = True
    auto_archive: bool = True
    compress_archive: bool = True

# Policy definitions
RETENTION_POLICIES = {
    RetentionPolicy.AUDIT_LOGS: PolicyConfig(
        schema="audit",
        table="security_events",
        retention_days=365,
        archive_after_days=90,
        partition_by="created_at",
        partition_interval="monthly"
    ),

    RetentionPolicy.BIA_DATA: PolicyConfig(
        schema="bia",
        table="*",  # All tables
        retention_days=365 * 7,  # 7 years
        archive_after_days=365 * 2,  # 2 years
        partition_by="created_at",
        partition_interval="yearly",
        auto_delete=False  # Never delete BIA data
    ),

    RetentionPolicy.WORKFLOW_LOGS: PolicyConfig(
        schema="workflow_intelligence",
        table="workflow_executions",
        retention_days=180,
        archive_after_days=30,
        partition_by="started_at",
        partition_interval="monthly"
    ),

    RetentionPolicy.TEMP_DATA: PolicyConfig(
        schema="public",
        table="sessions",
        retention_days=7,
        archive_after_days=0,  # No archive
        partition_by="created_at",
        partition_interval="daily",
        auto_archive=False
    )
}
```

**Day 3-4: Archive Service**
```python
# /infrastructure/database/retention/archive_service.py

import boto3  # For S3 archive
from datetime import datetime, timedelta
from sqlalchemy import text

class ArchiveService:
    """Archive old data to cold storage"""

    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.archive_bucket = "bcm-platform-archives"

    async def archive_table_data(
        self,
        schema: str,
        table: str,
        cutoff_date: datetime,
        compress: bool = True
    ):
        """
        Archive data older than cutoff_date

        1. Export data to CSV/Parquet
        2. Upload to S3
        3. Delete from main DB
        4. Log archive event
        """
        # Export query
        export_query = f"""
        COPY (
            SELECT * FROM {schema}.{table}
            WHERE created_at < '{cutoff_date}'
        ) TO STDOUT WITH CSV HEADER
        """

        # Execute export
        data = await self.export_data(export_query)

        # Compress if needed
        if compress:
            data = self.compress_gzip(data)

        # Upload to S3
        archive_key = f"archives/{schema}/{table}/{cutoff_date.year}/{cutoff_date.month}.csv.gz"
        self.s3_client.put_object(
            Bucket=self.archive_bucket,
            Key=archive_key,
            Body=data
        )

        # Delete from main DB
        delete_query = f"""
        DELETE FROM {schema}.{table}
        WHERE created_at < '{cutoff_date}'
        """
        await self.execute_query(delete_query)

        # Log event
        await self.log_archive_event(schema, table, cutoff_date, archive_key)
```

**Day 5: Partitioning Manager**
```python
# /infrastructure/database/retention/partitioning_manager.py

class PartitioningManager:
    """Manage table partitioning for performance"""

    async def create_partition(
        self,
        schema: str,
        table: str,
        partition_column: str,
        interval: str  # 'monthly', 'yearly'
    ):
        """Create partitioned table"""

        # Create parent table
        create_parent = f"""
        CREATE TABLE {schema}.{table} (
            -- columns...
            {partition_column} TIMESTAMPTZ NOT NULL
        ) PARTITION BY RANGE ({partition_column});
        """

        # Create partitions for next 12 months
        for i in range(12):
            start_date = datetime.now() + timedelta(days=30*i)
            end_date = start_date + timedelta(days=30)

            partition_name = f"{table}_{start_date.year}_{start_date.month:02d}"

            create_partition = f"""
            CREATE TABLE {schema}.{partition_name}
            PARTITION OF {schema}.{table}
            FOR VALUES FROM ('{start_date}') TO ('{end_date}');
            """

            await self.execute_query(create_partition)

    async def auto_create_future_partitions(self):
        """Automatically create partitions for future months"""
        # Cron job: runs monthly
        # Creates partitions for next 3 months
        pass
```

---

### Phase 2: Automation (Week 2)

**Celery Tasks для автоматизации:**

```python
# /infrastructure/database/retention/tasks.py

from celery import Celery
from celery.schedules import crontab

app = Celery('data_retention')

@app.task
def daily_cleanup():
    """Run daily - cleanup temp data"""
    # Delete sessions > 7 days
    # Delete temp files
    pass

@app.task
def monthly_archive():
    """Run monthly - archive old data"""
    # Archive audit logs > 90 days
    # Archive workflow logs > 30 days
    pass

@app.task
def yearly_compliance_report():
    """Run yearly - generate compliance report"""
    # Count archived records
    # Verify retention policies
    # Generate ISO 22301 report
    pass

# Schedule
app.conf.beat_schedule = {
    'daily-cleanup': {
        'task': 'daily_cleanup',
        'schedule': crontab(hour=3, minute=0)  # 3 AM daily
    },
    'monthly-archive': {
        'task': 'monthly_archive',
        'schedule': crontab(day_of_month=1, hour=2)  # 1st of month, 2 AM
    },
    'yearly-compliance': {
        'task': 'yearly_compliance_report',
        'schedule': crontab(month_of_year=1, day_of_month=1)  # Jan 1st
    }
}
```

---

### Phase 3: Compliance Reporting (Week 3)

**ISO 22301 Compliance Dashboard:**

```python
# /infrastructure/database/retention/compliance_reporter.py

class ComplianceReporter:
    """Generate compliance reports for ISO 22301"""

    async def generate_retention_report(self) -> dict:
        """Generate data retention compliance report"""

        report = {
            "report_date": datetime.now().isoformat(),
            "retention_policies": [],
            "compliance_status": "compliant",
            "issues": []
        }

        for policy_name, policy in RETENTION_POLICIES.items():
            # Check each policy
            status = await self.check_policy_compliance(policy)

            report["retention_policies"].append({
                "policy": policy_name.value,
                "schema": policy.schema,
                "table": policy.table,
                "retention_days": policy.retention_days,
                "oldest_record_days": status["oldest_record_days"],
                "archived_count": status["archived_count"],
                "compliant": status["compliant"]
            })

            if not status["compliant"]:
                report["compliance_status"] = "non_compliant"
                report["issues"].append({
                    "policy": policy_name.value,
                    "issue": status["issue"]
                })

        return report
```

---

## 🔧 TECHNICAL DETAILS

### Database Partitioning

**Пример для audit.security_events:**

```sql
-- Create parent table
CREATE TABLE audit.security_events (
    id UUID DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    -- other columns...
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE audit.security_events_2025_01
    PARTITION OF audit.security_events
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE audit.security_events_2025_02
    PARTITION OF audit.security_events
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- ... (create for next 12 months)

-- Auto-create future partitions (pg_partman extension)
CREATE EXTENSION IF NOT EXISTS pg_partman;

SELECT create_parent(
    'audit.security_events',
    'created_at',
    'native',
    'monthly',
    p_premake := 3  -- Create 3 months ahead
);
```

### Archive to S3/MinIO

```python
# Archive old partitions
import boto3

s3 = boto3.client('s3')

# Export partition to CSV
export_query = """
COPY audit.security_events_2024_01 TO STDOUT WITH CSV HEADER
"""

csv_data = execute_query(export_query)

# Upload to S3
s3.put_object(
    Bucket='bcm-archives',
    Key='audit/security_events/2024/01.csv.gz',
    Body=gzip.compress(csv_data)
)

# Drop partition
DROP TABLE audit.security_events_2024_01;
```

---

## 📊 MONITORING & ALERTING

### Metrics to Track

```yaml
Retention Metrics:
  - data_retention_oldest_record_days (by table)
  - data_retention_archived_records_total
  - data_retention_deleted_records_total
  - data_retention_policy_violations_count
  - data_retention_archive_size_bytes

Alerts:
  - 🚨 Policy violation (data older than retention)
  - 🚨 Archive failure
  - 🚨 Partition creation failure
  - ⚠️ Archive storage > 80% capacity
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Data Retention & Archiving",
    "panels": [
      {
        "title": "Oldest Record by Table",
        "type": "table",
        "targets": [{
          "expr": "data_retention_oldest_record_days"
        }]
      },
      {
        "title": "Archived Records (Last 30 Days)",
        "type": "graph",
        "targets": [{
          "expr": "rate(data_retention_archived_records_total[30d])"
        }]
      },
      {
        "title": "Policy Compliance Status",
        "type": "stat",
        "targets": [{
          "expr": "data_retention_policy_violations_count"
        }]
      }
    ]
  }
}
```

---

## ✅ CHECKLIST - Implementation

### Phase 1: Retention Policies (Week 1)
```bash
□ Define retention policies for all schemas
□ Create PolicyConfig dataclass
□ Implement ArchiveService
□ Implement PartitioningManager
□ Test on staging database
```

### Phase 2: Automation (Week 2)
```bash
□ Create Celery tasks
□ Schedule daily cleanup (temp data)
□ Schedule monthly archive (old data)
□ Schedule partition creation
□ Test automated workflows
```

### Phase 3: Compliance (Week 3)
```bash
□ Implement ComplianceReporter
□ Generate retention reports
□ Create Grafana dashboard
□ Set up alerting
□ ISO 22301 audit readiness
```

---

## 🎯 NEXT STEPS

1. **Immediate** (сегодня):
   - [ ] Review этот документ
   - [ ] Решить: расширить DB Intelligence или создать отдельный сервис
   - [ ] Создать GitHub Issue для tracking

2. **Week 1** (критично):
   - [ ] Внедрить retention policies
   - [ ] Создать archive service
   - [ ] Настроить partitioning для audit таблиц

3. **Week 2-3** (важно):
   - [ ] Автоматизация через Celery
   - [ ] Compliance reporting
   - [ ] Grafana dashboard

---

**Создано**: 2025-10-11
**Статус**: 📝 Requirements Defined
**Действие**: Нужно начать implementation Week 1
**Связанные документы**:
- [DB Intelligence README](/Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/db-intelligence/README.md)
- [Security Strategy](/Users/MD/AI-Platform-ISO/infrastructure/database/SECURITY_IMPLEMENTATION_STRATEGY.md)

---

**END OF REQUIREMENTS**
