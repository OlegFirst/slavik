# System BCM Service - Documentation

**Date**: 2025-10-11
**Service Version**: 1.0.0
**Status**: Production Ready (100%)

---

## 📚 Documentation Structure

### Core Documentation (Root Level)

Located in: `/intelligent-core/system-bcm-service/`

- **README.md** - Main service overview and quick start
- **INTEGRATION_COMPLETE.md** - Full integration status report
- **PLATFORM_INTEGRATION.md** - Integration guide with platform services
- **INTEGRATION_DIAGRAM.md** - Architecture diagrams and flows
- **FULL_AI_CORE_INTEGRATION.md** - AI Core integration details
- **INTEGRATION_PLAN.md** - Implementation plan and phases

### Reference Documentation (This Folder)

- **COMPLETE_DEPLOYMENT_GUIDE.md** - Step-by-step deployment instructions
- **CRITICAL_ANALYSIS.md** - Design decisions and architecture analysis
- **FINAL_SUMMARY.md** - Complete project summary
- **GITHUB_SETUP.md** - GitHub repository setup guide

### Archive (Historical)

Located in: `./archive/`

Process documentation and intermediate reports:
- AUTOMATION_COMPLETE.md
- COMMANDS_REFERENCE.md
- DATABASE_COMPLETE.md
- FINAL_COMPLETE_SUMMARY.md
- INTEGRATION_CHECKLIST.md
- INTEGRATION_FILES_SUMMARY.md
- MAKEFILE_EXPLAINED.md
- METRICS_VERIFICATION.md
- README.github.md

---

## 🚀 Quick Start

1. **Read Main README**: `../README.md`
2. **Review Integration Status**: `../INTEGRATION_COMPLETE.md`
3. **Deploy**: `../scripts/integrate-with-platform.sh`
4. **Validate**: `../scripts/validate-deployment.sh`

---

## 🏗️ What is System BCM Service?

**System BCM Service** is a meta-service that applies Business Continuity Management (BCM) to the platform itself.

### Purpose
- Self-application of BCM principles
- Auto-recovery for platform services (7 procedures)
- Practice learning from real incidents
- Platform health monitoring (23 services)
- Insight generation and auto-improvement

### Key Features
- **Port**: 8050
- **Auto-Recovery**: 7 automated procedures with RTO tracking
- **Monitoring**: Prometheus + Grafana + 20+ metrics
- **EventBus**: Redis Streams integration (4 subscriptions, 5 publications)
- **Learning**: Practice learning engine with confidence scoring
- **Integration**: 6 infrastructure + 12 platform + 11 intelligent services

---

## 📊 Architecture

```
Infrastructure (6 components)
├── Redis (6379) - EventBus
├── PostgreSQL (5432) - Database
├── Qdrant (6333) - Vector DB
├── Prometheus (9090) - Metrics
├── Grafana (3000) - Dashboards
└── RabbitMQ (5672) - Message Queue

Platform Services (12 services, 8001-8012)
├── BIA, Risk, Compliance, Planning
├── Response, Documents, Governance
└── Validation, Learning, BCM Coordination, Community, Monitoring

Intelligent Core (11 modules, 8031-8050)
├── Predictive, Collective Intelligence
├── Expertise Center, Workflow Intelligence
├── Community, Event Intelligence
├── Workflow Engine
└── System BCM Service (8050) ← THIS SERVICE
```

---

## 🔧 Scripts

Located in: `../scripts/`

- **integrate-with-platform.sh** - Full integration automation (8 phases)
- **validate-deployment.sh** - Comprehensive testing (40+ tests)
- **health-check.sh** - Quick health verification
- **start.sh** - Service startup

---

## 📈 Current Status

**Created**: October 9, 2025
**Last Modified**: October 10, 2025 22:45
**Completion**: 100%
**Running**: No (ready to deploy)
**Port**: 8050 (available)

### Integration Status
✅ Phase 1: Core Service (740 lines, EventBus, 7 procedures)
✅ Phase 2: Integration (Service Discovery, Auto-recovery)
✅ Phase 3: Monitoring (Prometheus, Grafana, Alerts)
✅ Phase 4: Documentation (194KB, 8 MD files)
✅ Phase 5: Automation (3 shell scripts, 12KB+)
✅ Phase 6: Scenarios (4 JSON files, 78KB)

---

## 🆚 vs KQM (Knowledge Quality Manager)

System BCM and KQM are **different services**:

| Aspect | System BCM | KQM |
|--------|------------|-----|
| **Created** | Oct 9, 2025 | Oct 11, 2025 |
| **Port** | 8050 | 8090 |
| **Purpose** | Platform self-BCM | Knowledge management |
| **Scope** | Health, recovery, learning | Scenarios, gaps, ISO compliance |
| **Auto-recovery** | ✅ 7 procedures | ❌ No |
| **EventBus** | ✅ Full integration | ❌ No |
| **Status** | Ready (not running) | Running |

They can work **together**:
- KQM manages knowledge quality
- System BCM ensures platform health
- Both use EventBus for communication

---

## 💡 Deployment Options

### Option 1: Auto Deploy (Recommended)
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/system-bcm-service
./scripts/integrate-with-platform.sh
```

### Option 2: Manual Deploy
```bash
# 1. Start dependencies
docker-compose up -d redis postgres prometheus grafana

# 2. Start service
python main.py

# 3. Verify
curl http://localhost:8050/health
```

### Option 3: Later
Service is ready but not critical. Can deploy when:
- Need auto-recovery for platform
- Want platform health monitoring
- Ready for practice learning

---

## 📖 Recommended Reading Order

1. **Quick Start**: `../README.md` (21KB)
2. **Status**: `../INTEGRATION_COMPLETE.md` (25KB)
3. **Integration**: `../PLATFORM_INTEGRATION.md` (24KB)
4. **Architecture**: `../INTEGRATION_DIAGRAM.md` (51KB)
5. **AI Details**: `../FULL_AI_CORE_INTEGRATION.md` (26KB)
6. **Deployment**: `COMPLETE_DEPLOYMENT_GUIDE.md` (20KB)
7. **Analysis**: `CRITICAL_ANALYSIS.md` (22KB)

---

**Total Documentation**: 194KB across 8 core files + 9 archived files
**Scripts**: 4 automation scripts (42KB)
**Code**: main.py (28KB), coordinator (15KB), instincts (12KB)

**Philosophy**: Living service that learns from practice, not theory ✨
