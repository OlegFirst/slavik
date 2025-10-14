# System BCM Service - Directory Structure

**Date**: 2025-10-11
**Status**: ✅ Organized and Production Ready

---

## 📁 Directory Organization

### Root Directory
```
/intelligent-core/system-bcm-service/
├── README.md                        # Main service documentation (21KB)
├── INTEGRATION_COMPLETE.md          # Integration status (25KB)
├── PLATFORM_INTEGRATION.md          # Integration guide (24KB)
├── INTEGRATION_DIAGRAM.md           # Architecture diagrams (51KB)
├── FULL_AI_CORE_INTEGRATION.md      # AI Core details (26KB)
├── INTEGRATION_PLAN.md              # Implementation plan (24KB)
├── DIRECTORY_STRUCTURE.md           # This file
│
├── main.py                          # Service entry point (28KB)
├── system_bcm_client.py             # Client library
├── docker-compose.yml               # Multi-container deployment
├── Dockerfile                       # Service image
├── requirements.txt                 # Python dependencies
├── .env                             # Environment configuration (10KB)
├── .env.example                     # Configuration template
│
├── docs/                            # Reference documentation
│   ├── README.md                    # Documentation index
│   ├── COMPLETE_DEPLOYMENT_GUIDE.md # Deployment guide
│   ├── CRITICAL_ANALYSIS.md         # Architecture analysis
│   ├── FINAL_SUMMARY.md             # Project summary
│   ├── GITHUB_SETUP.md              # Repository setup
│   └── archive/                     # Historical documentation
│       ├── AUTOMATION_COMPLETE.md
│       ├── COMMANDS_REFERENCE.md
│       ├── DATABASE_COMPLETE.md
│       ├── FINAL_COMPLETE_SUMMARY.md
│       ├── INTEGRATION_CHECKLIST.md
│       ├── INTEGRATION_FILES_SUMMARY.md
│       ├── MAKEFILE_EXPLAINED.md
│       ├── METRICS_VERIFICATION.md
│       └── README.github.md
│
├── scripts/                         # Automation scripts
│   ├── README.md                    # Scripts documentation
│   ├── integrate-with-platform.sh   # Auto-integration (12KB)
│   ├── validate-deployment.sh       # Validation tests (14KB)
│   ├── health-check.sh              # Health monitoring (13KB)
│   └── start.sh                     # Service startup (3.3KB)
│
├── scenarios/                       # BCM scenarios
│   ├── platform_bia.json            # Business Impact Analysis
│   ├── platform_risks.json          # Risk scenarios
│   ├── recovery_procedures.json     # Recovery procedures
│   └── resource_priorities.json     # Resource allocation
│
├── engines/                         # Core engines
│   ├── __init__.py
│   ├── bia_engine.py
│   ├── risk_engine.py
│   ├── recovery_engine.py
│   ├── priority_engine.py
│   └── system_bcm_coordinator.py
│
├── instincts/                       # Self-monitoring
│   ├── __init__.py
│   └── survival.py                  # Survival instinct
│
├── database/                        # Database migrations
│   ├── migrate.sh
│   ├── migrations/
│   └── schema.sql
│
├── grafana/                         # Monitoring dashboards
│   ├── dashboards/
│   └── provisioning/
│
├── prometheus/                      # Metrics collection
│   └── prometheus.yml
│
└── frontend/                        # UI (optional)
    ├── FRONTEND_ARCHITECTURE.md
    └── src/
```

---

## 📊 File Organization Principles

### Root Level (Production Essentials)
**Purpose**: Quick access to critical files for deployment and operation

**Contains**:
- Service entry point (main.py)
- Core configuration (docker-compose.yml, .env)
- Key integration documentation (6 MD files)
- README (main documentation)

**Rationale**: Everything needed to deploy and understand the service in one glance

---

### docs/ (Reference Documentation)
**Purpose**: Detailed guides, analysis, and historical records

**Contains**:
- **Active docs**: Deployment guides, architecture analysis
- **Archive**: Process documentation from development

**Rationale**:
- Keeps root clean while preserving all documentation
- Archive preserves development history without cluttering main view
- Easy navigation: `docs/` for guides, `docs/archive/` for history

---

### scripts/ (Automation)
**Purpose**: All executable automation scripts

**Contains**:
- Integration automation
- Validation testing
- Health monitoring
- Service management

**Rationale**:
- Single location for all scripts
- Includes own README with usage instructions
- Executable permissions managed in one place

---

### scenarios/ (BCM Data)
**Purpose**: Business Continuity scenarios and configurations

**Contains**:
- Platform BIA (7 critical processes)
- Risk scenarios (12 risks)
- Recovery procedures (7 procedures)
- Resource priorities (3-tier allocation)

**Rationale**: Separates data from code, easy to update scenarios

---

### engines/ (Core Logic)
**Purpose**: Business logic engines

**Contains**: BIA, Risk, Recovery, Priority engines + Coordinator

---

### instincts/ (Self-Monitoring)
**Purpose**: Self-awareness and adaptation logic

**Contains**: Survival instinct monitoring

---

## 📈 Metrics

### Documentation
- **Root**: 6 files, 171KB (essential integration docs)
- **docs/**: 5 files + archive (reference and history)
- **Total**: 194KB across all documentation

### Scripts
- **4 automation scripts**: 42KB total
- All with comprehensive documentation

### Code
- **main.py**: 28KB (FastAPI service)
- **Engines**: 5 files, ~60KB
- **Total**: ~100KB production code

---

## 🎯 Navigation Guide

### "I want to deploy the service"
1. Read: `README.md` (quick start)
2. Run: `scripts/integrate-with-platform.sh`
3. Validate: `scripts/validate-deployment.sh`

### "I want to understand the architecture"
1. Read: `INTEGRATION_DIAGRAM.md` (visual architecture)
2. Read: `PLATFORM_INTEGRATION.md` (integration details)
3. Read: `docs/CRITICAL_ANALYSIS.md` (design decisions)

### "I want to learn about specific components"
1. AI Integration: `FULL_AI_CORE_INTEGRATION.md`
2. Implementation: `INTEGRATION_PLAN.md`
3. Status: `INTEGRATION_COMPLETE.md`

### "I want deployment help"
1. Read: `docs/COMPLETE_DEPLOYMENT_GUIDE.md`
2. Scripts: `scripts/README.md`
3. Troubleshooting: `docs/CRITICAL_ANALYSIS.md`

### "I want to see development history"
1. Archive: `docs/archive/` (9 historical documents)
2. Git log: `git log --oneline -- .`

---

## 🔄 Maintenance

### Adding New Documentation
- **Integration docs**: Root level (if critical for deployment)
- **Reference docs**: `docs/` (guides, analysis)
- **Process docs**: `docs/archive/` (development artifacts)

### Adding New Scripts
- **All scripts**: `scripts/` directory
- Update: `scripts/README.md` with usage

### Updating Scenarios
- Edit files in: `scenarios/`
- Reload: Restart service or API call

---

## ✅ Organization Benefits

### Before Cleanup
```
Root directory:
- 19 MD files (mixed purpose)
- 4 shell scripts
- Core files
- No clear structure
```

**Problems**:
- Hard to find specific docs
- Unclear what's essential vs historical
- Scripts mixed with documentation
- No navigation guide

### After Cleanup
```
Root directory:
- 6 essential MD files (integration)
- Core service files only
- Clear subdirectories:
  - docs/ (reference)
  - docs/archive/ (history)
  - scripts/ (automation)
```

**Benefits**:
- ✅ Clear purpose for each file
- ✅ Easy navigation
- ✅ Essential files at top level
- ✅ History preserved but organized
- ✅ Documentation in each subdirectory

---

## 📝 File Inventory

### Root Level Files (Essential)
1. **README.md** (21KB) - Main documentation
2. **INTEGRATION_COMPLETE.md** (25KB) - Integration status
3. **PLATFORM_INTEGRATION.md** (24KB) - Integration guide
4. **INTEGRATION_DIAGRAM.md** (51KB) - Architecture diagrams
5. **FULL_AI_CORE_INTEGRATION.md** (26KB) - AI Core details
6. **INTEGRATION_PLAN.md** (24KB) - Implementation plan
7. **DIRECTORY_STRUCTURE.md** - This file

**Total**: 171KB essential documentation

### docs/ (Reference)
1. **README.md** - Documentation index
2. **COMPLETE_DEPLOYMENT_GUIDE.md** (20KB)
3. **CRITICAL_ANALYSIS.md** (22KB)
4. **FINAL_SUMMARY.md** (19KB)
5. **GITHUB_SETUP.md** (11KB)

**Total**: 72KB reference docs

### docs/archive/ (Historical)
9 historical documents, ~100KB

### scripts/
1. **README.md** - Scripts documentation
2. **integrate-with-platform.sh** (12KB)
3. **validate-deployment.sh** (14KB)
4. **health-check.sh** (13KB)
5. **start.sh** (3.3KB)

**Total**: 42KB automation

---

## 🚀 Quick Reference

### Most Important Files
1. **README.md** - Start here
2. **scripts/integrate-with-platform.sh** - Deploy
3. **INTEGRATION_COMPLETE.md** - Status
4. **docs/COMPLETE_DEPLOYMENT_GUIDE.md** - Help

### Directory Shortcuts
```bash
# Main docs
cd /Users/MD/AI-Platform-ISO/intelligent-core/system-bcm-service

# Scripts
cd scripts/

# Reference docs
cd docs/

# History
cd docs/archive/

# Scenarios
cd scenarios/
```

---

**Last Updated**: 2025-10-11
**Organization Status**: ✅ Complete
**Total Files**: 52 (organized)
**Total Size**: ~400KB (docs + code + configs)

**Philosophy**:
> "Clarity through organization. Everything has its place,
> and everything in its place has a purpose."
