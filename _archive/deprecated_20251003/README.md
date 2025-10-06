# Archived Files - October 3, 2025

## Reason for Archival
These files are deprecated and no longer needed in the active project structure.

## Files Archived

### Empty Placeholder Files
- **Create** (0 bytes) - Empty placeholder file
- **Run** (0 bytes) - Empty placeholder file
- **Link** (0 bytes) - Empty placeholder file

**Reason**: These were likely placeholder files created during initial project setup and are no longer needed.

### Migration Scripts
- **add_auth_to_routers.py** (6.1 KB)
  - Purpose: One-time script to add authentication to compliance routers
  - Status: Migration completed
  - **Reason**: Script already executed, functionality now integrated into code

### Deprecated Configuration
- **docker-compose.yml** (8.6 KB)
  - Original location: `/Users/MD/AI-Platform-ISO/docker-compose.yml`
  - Purpose: Old infrastructure-level Docker Compose configuration
  - **Reason**: Replaced by `/Users/MD/AI-Platform-ISO/platform-services/docker-compose.yml`

  Key differences from current version:
  - Used generic service names (intelligent-core, etc.)
  - Different database configuration
  - Less specific to BCM platform services
  - Current version has Planning, Plans, BIA, Compliance, Monitoring services

## Active Files (NOT Archived)

These files in `platform-services/` remain active:
- ✅ **platform-services/docker-compose.yml** - Current BCM services configuration
- ✅ **platform-services/start.sh** - Service startup script
- ✅ **platform-services/stop.sh** - Service shutdown script
- ✅ **platform-services/logs.sh** - Log viewing script
- ✅ **platform-services/status.sh** - Service status checker

## Restoration

If you need to restore these files:
```bash
cd /Users/MD/AI-Platform-ISO/_archive/deprecated_20251003
cp [filename] /Users/MD/AI-Platform-ISO/
```

## Safe to Delete?

**YES** - All files in this archive can be safely deleted after a backup period (recommend keeping for 30 days as precaution).

---
**Archived by**: Claude Code AI Assistant
**Date**: October 3, 2025
**Project**: BCM Platform - ISO 22301 Implementation
