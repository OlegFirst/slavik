# BIA Service - Business Impact Analysis

**ISO 22301 Clause 8.2.2**

Unified architecture microservice for comprehensive Business Impact Analysis.

---

## ✅ MIGRATION STATUS

**Source:** `/Users/MD/ISO-22301—копия/services/SERVICES/BCM/bia/main.py` (695 lines)
**Target:** `/Users/MD/AI-Platform-ISO/services/bcm/bia/` (unified architecture)
**Status:** ✅ **COMPLETE - NO FUNCTIONALITY LOST**

### What Was Preserved:
- ✅ All 8 Enums (CriticalityLevel, ProcessStatus, etc.)
- ✅ All 6 Models (BIAProcess, AIRTOSuggestion, etc.)
- ✅ All 12 BIA endpoints
- ✅ All 8 Supply Chain endpoints (supply_chain_api.py)
- ✅ All helper functions (calculate_criticality_score, etc.)
- ✅ Event publishing (bcm.bia.started, bcm.bia.completed, etc.)
- ✅ AI integration (RTO suggestions, dependency discovery)
- ✅ WHO Essential Services tiers (healthcare)
- ✅ In-memory storage (original behavior)

---

## 📁 Structure

```
bia/
├── __init__.py
├── main.py                      # FastAPI app with lifespan
├── config.py                    # Settings (inherits from shared/)
├── models/
│   ├── __init__.py
│   ├── enums.py                 # 8 Enums
│   └── domain.py                # 6 Pydantic Models
├── api/
│   ├── __init__.py
│   └── routes.py                # 12 endpoints (thin layer)
├── services/
│   ├── __init__.py
│   ├── bia_service.py           # Core business logic
│   ├── ai_service.py            # AI integration
│   └── report_service.py        # Reporting & analytics
├── repositories/
│   ├── __init__.py
│   └── bia_repository.py        # Data access (in-memory)
├── utils/
│   ├── __init__.py
│   └── calculations.py          # Helper functions
├── supply_chain_api.py          # Supply Chain BCM (619 lines)
├── supply_chain_schemas.py      # Supply Chain models (473 lines)
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### Local Development

```bash
cd /Users/MD/AI-Platform-ISO/services/bcm/bia

# Install dependencies
pip install -r requirements.txt

# Run service
python main.py
```

Service runs on **Port 8012**

### Docker

```bash
# From project root
docker-compose up bia-service
```

---

## 📡 API Endpoints (12 + 8)

### Core BIA (12 endpoints)

1. `POST /api/bia/processes` - Create BIA process
2. `GET /api/bia/processes` - List processes (with filters)
3. `GET /api/bia/processes/{id}` - Get process
4. `PUT /api/bia/processes/{id}` - Update process
5. `DELETE /api/bia/processes/{id}` - Delete process
6. `POST /api/bia/processes/{id}/complete` - Mark completed
7. `POST /api/bia/processes/{id}/suggest-rto` - AI RTO suggestion
8. `POST /api/bia/processes/{id}/discover-dependencies` - AI dependency discovery
9. `GET /api/bia/reports/summary` - Summary report
10. `GET /api/bia/reports/critical-processes` - Critical processes
11. `GET /api/bia/reports/dependencies` - Dependency graph
12. `GET /health` - Health check

### Supply Chain BCM (8 endpoints)

From `supply_chain_api.py` (integrated automatically if available)

---

## 🔧 Configuration

### Environment Variables

```bash
# Service
BIA_SERVICE_PORT=8012

# Database (future)
DATABASE_URL=postgresql+asyncpg://user:pass@host/db

# EventBus
EVENTBUS_URL=http://eventbus:8001

# AI Services
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Features
BIA_WHO_TIER_ENABLED=true
BIA_SUPPLY_CHAIN_ENABLED=true
```

### Config File

See `config.py` - inherits from `shared.config.BaseServiceSettings`

---

## 🎯 Features

### ISO 22301 Compliance
- ✅ Clause 8.2.2: Business Impact Analysis
- ✅ Criticality assessment (5-level scale)
- ✅ Recovery objectives (RTO/RPO/MTPD)
- ✅ Resource requirements
- ✅ Dependency mapping

### AI-Powered Intelligence
- ✅ AI-suggested RTO/RPO/MTPD
- ✅ Automated dependency discovery
- ✅ Industry benchmarks
- ✅ Rule-based fallbacks

### Healthcare-Specific
- ✅ WHO Essential Services tiers
- ✅ Patient safety impact levels
- ✅ Regulatory impact assessment
- ✅ Critical care process identification

### Supply Chain BCM
- ✅ 8 dedicated endpoints
- ✅ Supplier criticality analysis
- ✅ EY research integration
- ✅ 20% faster recovery metrics

---

## 📊 Data Models

### Main Models (6)
1. **BIAProcess** - Core business process
2. **BIAProcessCreate** - Creation DTO
3. **AIRTOSuggestion** - AI recommendations
4. **BIASummaryReport** - Tenant summary
5. **Dependency** - Process dependencies
6. **ImpactAssessment** - Time-based impact

### Enums (8)
1. CriticalityLevel (5 levels)
2. ProcessStatus (3 states)
3. ReputationalImpact (5 levels)
4. RegulatoryImpact (5 levels)
5. PatientSafetyImpact (5 levels - healthcare)
6. WHOTier (4 tiers - healthcare)
7. GeographicalScope (4 scopes)
8. IndustryType (10 industries)

---

## 🔄 Event Publishing

### Events Published

1. **bcm.bia.started** - BIA process created
2. **bcm.bia.completed** - BIA process completed
3. **bcm.bia.critical_process_identified** - Critical process found (score >= 4)

### Events Subscribed

1. **governance.organization.created** - Auto-create BIA template
2. **risk.critical_risk_identified** - Link to BIA process

---

## 🧪 Testing

```bash
# Check health
curl http://localhost:8012/health

# Create BIA process
curl -X POST http://localhost:8012/api/bia/processes \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_123",
    "name": "Payment Processing",
    "criticality": "critical",
    "industry": "financial",
    "rto_hours": 4,
    "rpo_hours": 1,
    "mtpd_hours": 8
  }'

# Get summary report
curl "http://localhost:8012/api/bia/reports/summary?tenant_id=tenant_123"
```

---

## 📈 Migration Notes

### From Original (695 lines monolithic)
- ✅ Split into 18 files (unified architecture)
- ✅ Services layer added (business logic separation)
- ✅ Repository pattern (data access abstraction)
- ✅ Dependency injection
- ✅ Lifespan management
- ✅ EventBus integration
- ✅ Shared config inheritance

### Storage
- **Current:** In-memory (dict-based, original behavior)
- **Future:** PostgreSQL migration planned
- **Code Ready:** Repository pattern supports easy DB swap

### What Changed
- ❌ **NOTHING!** All 12+8 endpoints work identically
- ✅ Better organized code
- ✅ Easier to test
- ✅ Easier to maintain
- ✅ Ready for team collaboration

---

## 🐛 Troubleshooting

### Import Errors
```bash
# Make sure shared/ is in PYTHONPATH
export PYTHONPATH="/Users/MD/AI-Platform-ISO:$PYTHONPATH"
```

### Supply Chain Not Loading
```bash
# Check if supply_chain_api.py exists
ls supply_chain_api.py

# Disable in config if needed
export BIA_SUPPLY_CHAIN_ENABLED=false
```

---

## ✅ Checklist: Functionality Verification

- [x] All 8 Enums present
- [x] All 6 Models present
- [x] All 12 BIA endpoints working
- [x] All 8 Supply Chain endpoints included
- [x] Event publishing works
- [x] AI integration preserved
- [x] WHO tiers calculation
- [x] Financial impact timeline
- [x] Dependency discovery
- [x] Critical process identification
- [x] Summary reports
- [x] Dependency graph
- [x] Multi-tenancy (tenant_id validation)
- [x] Access control (403 checks)
- [x] In-memory storage working

---

**Status:** ✅ Production Ready | **ISO 22301:** Clause 8.2.2 | **Port:** 8012
