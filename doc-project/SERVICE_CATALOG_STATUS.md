# AI Office Infrastructure - Service Catalog & Status

**Created**: 2025-10-10
**Last Updated**: 2025-10-10
**Status**: 🔄 In Progress - Starting Services

---

## 📊 Service Inventory

| # | Service | Port | Status | Has Requirements | Has Main | Notes |
|---|---------|------|--------|------------------|----------|-------|
| 1 | **orchestrator** | 8045 | ⏸️ Not Started | ✅ | ✅ | AI Orchestrator - координатор |
| 2 | **mio-manager** | 8046 | ⏸️ Not Started | ✅ | ✅ | МиО Manager - resource coordinator |
| 3 | **analytics-specialist** | 8056 | ⏸️ Not Started | ✅ | ✅ | ⚠️ **ML/Analytics specialist** |
| 4 | **db-intelligence** | 8051 | ⏸️ Not Started | ✅ | ✅ | ⚠️ **DB specialist** |
| 5 | **ai-event-manager** | 8050 | ⏸️ Not Started | ✅ | ✅ | Event manager |
| 6 | **agent-router** | 8047 | ⏸️ Not Started | ✅ | ✅ | Agent router |
| 7 | **project-agent** | 8048 | ⏸️ Not Started | ✅ | ✅ | Project management agent |
| 8 | **devops-agent** | 8049 | ⏸️ Not Started | ✅ | ✅ | DevOps agent |

**Total Services**: 8
**Ready to Start**: 8/8 (100%)

---

## 🎯 Service Details

### 1. Orchestrator (Port 8045)
**Path**: `/infrastructure/AI-office-infrastructure/orchestrator/`
**Role**: AI Orchestration and coordination
**Dependencies**:
- fastapi, uvicorn
- httpx
- redis
- supabase

**Key Features**:
- AI request routing
- Service registration
- Health monitoring

---

### 2. MIO Manager (Port 8046)
**Path**: `/infrastructure/AI-office-infrastructure/mio-manager/`
**Role**: Resource management and coordination
**Dependencies**:
- fastapi, uvicorn
- httpx
- redis
- supabase
- prometheus-client

**Key Features**:
- Resource tracking (Phase 2 integration)
- Service coordination
- EventBus integration

---

### 3. Analytics Specialist (Port 8056) ⚠️
**Path**: `/infrastructure/AI-office-infrastructure/analytics-specialist/`
**Role**: Platform Intelligence Expert - AI Colleague #6
**Dependencies**:
- fastapi==0.109.0
- uvicorn==0.27.0
- httpx==0.26.0
- redis==5.0.1
- supabase==2.3.0
- prometheus-client==0.19.0

**Key Features**:
- Platform health analysis
- Bottleneck detection
- Metrics discovery
- Dependency mapping
- Daily health checks
- Continuous improvement scans

**Potential Issues**:
- ⚠️ Requires ML/analytics capabilities
- May need sklearn, pandas, numpy (not in requirements.txt)

---

### 4. DB Intelligence (Port 8051) ⚠️
**Path**: `/infrastructure/AI-office-infrastructure/db-intelligence/`
**Role**: Database monitoring and optimization
**Dependencies**:
- fastapi==0.104.1
- uvicorn==0.24.0
- sqlalchemy[asyncio]==2.0.23
- asyncpg==0.29.0
- psycopg2-binary==2.9.9
- httpx==0.25.2
- psutil==5.9.6
- supabase==2.3.0

**Key Features**:
- Query monitoring
- Performance analysis
- Optimization suggestions
- Health monitoring
- Table statistics

**Potential Issues**:
- ⚠️ Needs PostgreSQL/Supabase connection
- ⚠️ Requires DB access credentials

---

### 5. AI Event Manager (Port 8050)
**Path**: `/infrastructure/AI-office-infrastructure/ai-event-manager/`
**Role**: Event management and processing
**Dependencies**:
- fastapi, uvicorn
- redis
- httpx

**Key Features**:
- EventBus integration
- Event routing
- Event processing

---

### 6. Agent Router (Port 8047)
**Path**: `/infrastructure/AI-office-infrastructure/agent-router/`
**Role**: Route requests to appropriate agents
**Dependencies**:
- fastapi, uvicorn
- httpx
- redis

**Key Features**:
- Request routing
- Agent selection
- Load balancing

---

### 7. Project Agent (Port 8048)
**Path**: `/infrastructure/AI-office-infrastructure/project-agent/`
**Role**: Project management and coordination
**Dependencies**:
- fastapi, uvicorn
- httpx
- supabase

**Key Features**:
- Project tracking
- Task management
- Status reporting

---

### 8. DevOps Agent (Port 8049)
**Path**: `/infrastructure/AI-office-infrastructure/devops-agent/`
**Role**: DevOps automation and deployment
**Dependencies**:
- fastapi, uvicorn
- httpx
- docker (Python client)

**Key Features**:
- Deployment automation
- Infrastructure management
- CI/CD integration

---

## ⚠️ Identified Issues

### Issue #1: Analytics Specialist - Missing ML Dependencies
**Service**: `analytics-specialist` (Port 8056)
**Problem**: Requirements.txt не содержит ML библиотеки
**Impact**: Аналитические функции могут не работать

**Missing**:
```
pandas
numpy
scikit-learn
matplotlib (опционально)
```

**Solution**: Добавить в requirements.txt

---

### Issue #2: DB Intelligence - Требуется DB Connection
**Service**: `db-intelligence` (Port 8051)
**Problem**: Требуются credentials для PostgreSQL/Supabase
**Impact**: Сервис не запустится без DB

**Required Env Vars**:
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=xxx
```

**Solution**: Настроить .env файл

---

### Issue #3: Test Specialist - Not Found
**Service**: Specialist для тестирования
**Problem**: Нет отдельного сервиса для тестов
**Impact**: Может отсутствовать автоматизированное тестирование

**Possible Solutions**:
1. Тесты интегрированы в другие сервисы
2. Отдельный test-runner сервис не реализован
3. Тесты запускаются через CI/CD

**Action**: Поиск тестов в проекте

---

## 🔧 Prerequisites for Startup

### Required Infrastructure:
- [x] Python 3.9+
- [ ] Redis (Port 6379) - для EventBus
- [ ] PostgreSQL / Supabase - для persistence
- [ ] .env файлы с credentials

### Environment Variables Needed:
```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/bcm_db
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-key-here

# Redis/EventBus
REDIS_URL=redis://localhost:6379
EVENTBUS_BACKEND=redis

# AI Services
OPENAI_API_KEY=sk-xxx (if needed)
ANTHROPIC_API_KEY=sk-ant-xxx (if needed)

# Service URLs (for inter-service communication)
ORCHESTRATOR_URL=http://localhost:8045
MIO_MANAGER_URL=http://localhost:8046
# ... etc
```

---

## 🚀 Startup Sequence (Recommended)

### Phase 1: Core Infrastructure
1. **Start Redis** (if not running)
   ```bash
   docker run -d -p 6379:6379 redis:7-alpine
   ```

2. **Start PostgreSQL** (if not using Supabase)
   ```bash
   docker run -d -p 5432:5432 \
     -e POSTGRES_PASSWORD=postgres \
     -e POSTGRES_DB=bcm_db \
     postgres:15
   ```

### Phase 2: Core Services
3. **Orchestrator** (8045) - First, as coordinator
   ```bash
   cd infrastructure/AI-office-infrastructure/orchestrator
   pip install -r requirements.txt
   python main.py
   ```

4. **MIO Manager** (8046) - Resource coordinator
   ```bash
   cd infrastructure/AI-office-infrastructure/mio-manager
   pip install -r requirements.txt
   python main.py
   ```

5. **AI Event Manager** (8050) - Event handling
   ```bash
   cd infrastructure/AI-office-infrastructure/ai-event-manager
   pip install -r requirements.txt
   python main.py
   ```

### Phase 3: Specialists (Fix Issues First!)
6. **Analytics Specialist** (8056) - After fixing requirements
7. **DB Intelligence** (8051) - After DB setup

### Phase 4: Agents
8. **Agent Router** (8047)
9. **Project Agent** (8048)
10. **DevOps Agent** (8049)

---

## 📋 Next Steps

### Immediate (Phase 1):
- [ ] Fix `analytics-specialist/requirements.txt` - добавить ML библиотеки
- [ ] Check `db-intelligence` DB connection requirements
- [ ] Find test specialist or test infrastructure
- [ ] Setup .env files for all services
- [ ] Start Redis container

### Short-term (Phase 2):
- [ ] Start Orchestrator
- [ ] Start MIO Manager
- [ ] Test service registration
- [ ] Verify health endpoints

### Medium-term (Phase 3):
- [ ] Start all services
- [ ] Test inter-service communication
- [ ] Monitor logs for errors
- [ ] Create service status dashboard

---

## 🔍 Testing Checklist

For each service after start:
- [ ] Service starts without errors
- [ ] Health endpoint responds (`GET /health`)
- [ ] Registers with orchestrator (if applicable)
- [ ] Publishes metrics (`GET /metrics`)
- [ ] Logs show no critical errors

---

**Status**: 📝 Catalog created, ready to start fixing issues and launching services
**Next**: Fix `analytics-specialist` requirements.txt

---

## 📝 Recent Changes (2025-10-10)

### Infrastructure Refactoring

#### Policy Engine (formerly decision-center)
**Location**: `/infrastructure/policy-engine/`
**Type**: Library Module
**Status**: ✅ Production Ready (v1.1.0)

**Changes**:
- ✅ Renamed from `decision-center` to `policy-engine` (2025-10-10)
- ✅ Archived Phase 1.1 documentation to `_docs_archive_phase1/`
- ✅ Updated all imports across codebase
- ✅ Created professional README

**Purpose**: YAML-based infrastructure governance
- Policy management (RTO/RPO, thresholds, compliance)
- Decision authority for infrastructure actions
- ISO 22301 compliance auditing
- Integration with AI Orchestrator via `PolicyAwareOrchestrator`

**Not a Service**: This is a library used by other services, not a standalone service with port.

---

#### Balancer Service
**Location**: `/infrastructure/balancer-service/`
**Type**: Runtime Service
**Status**: ✅ Ready to Run
**Port**: 9091 (Prometheus metrics)

**Purpose**: Orchestrates Phase 2 AI balancers from `intelligent-core/ai-foundation/balancer/`
- System Balancer (global balancing)
- Impact Evidence Tracker (rational dimension)
- Predictive ROI Optimizer (intuitive + pragmatic)
- Three-Dimensional Balancer (3D balance)

**Integration**: EventBus-based, listens for imbalance events

---

