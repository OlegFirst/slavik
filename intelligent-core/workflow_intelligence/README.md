# Workflow Intelligence Engine

**Status:** ✅ Temporal Cloud Connected
**Version:** 1.0.0
**Python:** 3.11.13
**Temporal SDK:** 1.18.1

---

## 🎯 Overview

**Workflow Intelligence Engine** - это МОЗГ всей BCM платформы.

**Из `арх2.md`:**
> "Это единственный компонент, который НЕЛЬЗЯ заменить позже. Определяет как работают ВСЕ остальные компоненты."

**Powered by:** [Temporal Cloud](https://cloud.temporal.io)

---

## ✅ Setup Status

- [x] Python 3.11.13 installed
- [x] Temporal CLI 1.4.1 installed (`~/bin/temporal`)
- [x] Temporal Python SDK 1.18.1 installed
- [x] Temporal Cloud account created
- [x] Temporal Cloud connected ✅
- [ ] Core Workflow Engine (Phase 2, Day 1-4)
- [ ] Case Library (Phase 2, Day 5-8)
- [ ] Governance System (Phase 2, Day 9-11)
- [ ] BIA Workflow (Phase 2, Day 12-14)

---

## 🚀 Quick Start

### View Temporal Cloud UI
**Dashboard:** https://cloud.temporal.io
**Namespace:** `quickstart-maxdemch-73cb5509.r3gxp`

**Current Status:** "No data detected" - нормально, пока не запущен workflow

### Activate Environment
```bash
cd intelligent-core/workflow_intelligence
source venv/bin/activate
```

### Test Temporal Cloud Connection
```bash
python test_temporal_connection.py
```

### Run Sample Worker
```bash
cd temporal-sample
python run_worker.py
```

### Run Sample Workflow
```bash
# In another terminal
cd temporal-sample
python run_workflow.py

# Then refresh https://cloud.temporal.io to see workflow!
```

---

## 📁 Structure

```
workflow_intelligence/
├── README.md                      # This file
├── TEMPORAL_SETUP_COMPLETE.md     # Setup documentation
├── requirements.txt               # Dependencies
├── venv/                          # Virtual environment (Python 3.11)
├── temporal-sample/               # Sample project for learning
│
├── test_temporal_connection.py   # Connection test
│
└── TO CREATE (Phase 2):
    ├── core/                      # Core Workflow Engine
    │   ├── workflows/
    │   │   └── bia_workflow.py   # BIA Workflow on Temporal
    │   ├── activities/
    │   │   └── bia_activities.py # BIA Activities
    │   └── state_machine/
    │       └── state_machine.py  # State Machine logic
    │
    ├── case_library/              # Case Library (self-learning)
    │   ├── models.py
    │   ├── collector.py
    │   ├── repository.py
    │   └── search.py
    │
    ├── governance/                # Governance System
    │   ├── rules_engine.py
    │   ├── checkpoints.py
    │   └── creative_zones.py
    │
    └── definitions/               # Workflow Definitions
        └── bia/
            └── bia_workflow.yaml
```

---

## 🔧 Temporal Cloud Configuration

**Namespace:** `quickstart-maxdemch-73cb5509.r3gxp`
**Region:** `europe-west3` (GCP)
**Address:** `europe-west3.gcp.api.temporal.io:7233`

**Environment Variables** (in `.env`):
```bash
TEMPORAL_API_KEY=...
TEMPORAL_NAMESPACE=quickstart-maxdemch-73cb5509.r3gxp
TEMPORAL_ADDRESS=europe-west3.gcp.api.temporal.io:7233
```

---

## 📚 Next Steps

**Follow Phase 2 from:**
[/infrastructure/CORRECT_SETUP_WITH_TEMPORAL.md](../../infrastructure/CORRECT_SETUP_WITH_TEMPORAL.md)

**Timeline:** 8-12 дней
- Day 1-4: Core Workflow Engine на Temporal
- Day 5-8: Case Library + Semantic Search (Qdrant)
- Day 9-11: Governance System (Rules, Checkpoints, Creative Zones)
- Day 12-14: BIA Workflow Definition + Testing

---

## 🔗 Resources

- **Temporal Cloud:** https://cloud.temporal.io
- **Python SDK Docs:** https://docs.temporal.io/dev-guide/python
- **Sample Project:** https://github.com/temporalio/money-transfer-project-template-python
- **Architecture:** [/doc-project/м/арх2.md](../../doc-project/м/арх2.md)

---

**Last Updated:** 2025-10-06
**Ready to build! 🚀**

---

## 📊 Temporal UI

**See:** [TEMPORAL_CLOUD_INTEGRATION.md](TEMPORAL_CLOUD_INTEGRATION.md)

### Cloud UI (Recommended) ✅
- **URL:** https://cloud.temporal.io
- **Features:** Workflow visualization, history, monitoring
- **Status:** Already accessible, no installation needed

### Local UI (Optional)
- Can install via Docker if needed
- Not required for Cloud workflows
- See TEMPORAL_CLOUD_INTEGRATION.md for details

**Temporal UI НЕ устанавливается в проект как сервис** - он hosted by Temporal Cloud.

