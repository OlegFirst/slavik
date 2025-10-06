# ISO 22301 Compliance Data Storage

**Location:** `/infrastructure/data/compliance/`
**Purpose:** Persistent storage for ISO 22301 compliance data

This directory stores all ISO 22301 compliance data for the BCM platform.

## Directory Structure

```
/Users/MD/AI-Platform-ISO/infrastructure/data/compliance/
├── alerts/                      # Compliance alerts (JSON snapshots)
├── nonconformities/             # ISO 10.1 nonconformity records
├── audits/                      # ISO 9.2 audit tracking
├── metrics/                     # Business continuity metrics (RTO/RPO/MTPD)
├── backups/                     # Daily snapshots of all compliance data
└── automation/                  # Automation Toolkit job results
```

## Data Persistence

- **Format:** JSON files
- **Backup:** Daily snapshots at 3:00 AM
- **Retention:** 90 days for backups, forever for active data
- **Access:** ISO 22301 Compliance API (port 8045)

## File Naming Convention

- `alerts/alerts_YYYY-MM-DD.json` - Daily alert log
- `nonconformities/NC_YYYY_NNN.json` - Nonconformity records
- `audits/audit_requirements.json` - Audit tracking
- `metrics/business_metrics_YYYY-MM-DD.json` - Daily metrics
- `backups/compliance_snapshot_YYYY-MM-DD_HH-MM.json.gz` - Compressed snapshots
- `automation/service_discovery_YYYY-MM-DD_HH-MM.json` - Discovery results
- `automation/security_scan_YYYY-MM-DD_HH-MM.json` - Security scan results
- `automation/complexity_analysis_YYYY-MM-DD_HH-MM.json` - Code complexity results

## Usage

### Load compliance data on startup
```python
import aiofiles
import json

DATA_PATH = '/Users/MD/AI-Platform-ISO/infrastructure/data/compliance'

async with aiofiles.open(f'{DATA_PATH}/backups/latest.json', 'r') as f:
    data = json.loads(await f.read())
```

### Save snapshot
```python
from datetime import datetime

DATA_PATH = '/Users/MD/AI-Platform-ISO/infrastructure/data/compliance'
snapshot_file = f'{DATA_PATH}/backups/compliance_snapshot_{datetime.now().strftime("%Y-%m-%d_%H-%M")}.json.gz'
```

### Query automation results
```bash
DATA_PATH=/Users/MD/AI-Platform-ISO/infrastructure/data/compliance

ls -lh $DATA_PATH/automation/
cat $DATA_PATH/automation/service_discovery_*.json | jq '.total_services'
```

## Permissions

- Owner: Current user
- Mode: 755 (rwxr-xr-x)
- Accessible by: ISO 22301 Compliance API, Automation Toolkit
