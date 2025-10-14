# Community Service - Integration Plan with Learning & Governance

**Дата:** 2025-10-03
**Статус:** Ready to Start
**Готовность Community Service:** 60-70% (нужна интеграция)

---

## 📊 Текущее состояние

### ✅ Что работает:
1. **Portal Service (8031)** - Knowledge Hub, Forum, Scenarios
2. **Marketplace Service (8032)** - BCM Specialists, Projects, Reviews
3. **Database** - Supabase PostgreSQL (schemas: portal, marketplace)
4. **Basic EventBus** - Публикует события (но не подписывается)
5. **Basic Auth** - Использует Clients Service (8030)

### ⚠️ Что нужно исправить:

#### 1. **Authentication Pattern Mismatch**
**Проблема:** Community использует HTTP вызовы к Clients Service для каждой проверки токена
```python
# Сейчас (медленно)
from integrations.clients_client import ClientsClient
user = await clients_client.validate_token(token)  # HTTP call каждый раз!

# Нужно (быстро)
from shared.auth.dependencies import get_current_user
user = get_current_user(token)  # Локальная JWT проверка
```

#### 2. **EventBus Pattern Mismatch**
**Проблема:** Custom HTTP client вместо shared EventBus library
```python
# Сейчас
from integrations.eventbus_client import eventbus_client
await eventbus_client.article_created(...)

# Нужно
from shared.eventbus import get_eventbus
eventbus = get_eventbus()
await eventbus.publish("portal.knowledge.article_created", {...})
```

#### 3. **Нет Event Subscriptions**
**Проблема:** Portal/Marketplace только публикуют события, но не слушают Learning/Governance
**Нужно:** Создать `events/subscribers.py` как в Learning/Governance

#### 4. **Нет Service Clients**
**Проблема:** Не могут вызывать API Learning/Governance напрямую
**Нужно:** HTTP клиенты для service-to-service communication

---

## 🔗 Integration Points

### Portal ↔ Learning Service

| Feature | Event/API | Priority |
|---------|-----------|----------|
| **Competency в Forum Profile** | API: GET /learning/persons/{id}/competencies | 🔴 High |
| **Training → Knowledge Article** | Event: learning.training.completed | 🔴 High |
| **Certification → Forum Badge** | Event: learning.certification.issued | 🔴 High |
| **Article → Training Resource** | API: POST /learning/resources | 🟡 Medium |

**Event Flow:**
```
Learning: training.completed
  ↓
Portal: Award "Knowledgeable" badge
Portal: Suggest creating article about topic
Portal: Update author competency display
```

### Portal ↔ Governance Service

| Feature | Event/API | Priority |
|---------|-----------|----------|
| **Policy References in Articles** | API: GET /governance/policies | 🔴 High |
| **Role-Based Forum Moderation** | API: GET /governance/roles/{person_id} | 🔴 High |
| **Policy Update → Forum Discussion** | Event: governance.policy.updated | 🟡 Medium |
| **Scenario → ISO Clause Mapping** | API: GET /governance/policies?iso_clause=X | 🟡 Medium |

**Event Flow:**
```
Governance: policy.created
  ↓
Portal: Create forum category for discussion
Portal: Suggest knowledge articles
```

### Marketplace ↔ Learning Service

| Feature | Event/API | Priority |
|---------|-----------|----------|
| **Specialist Certifications** | API: GET /learning/persons/{id}/certifications | 🔴 High |
| **Competency Matching** | API: GET /learning/competencies | 🔴 High |
| **Auto-Update Certs** | Event: learning.certification.issued | 🔴 High |
| **Training Requirements** | API: GET /learning/programs | 🟡 Medium |

**Event Flow:**
```
Learning: certification.issued
  ↓
Marketplace: Update specialist profile
Marketplace: Recalculate competency score
Marketplace: Notify matching projects
```

### Marketplace ↔ Governance Service

| Feature | Event/API | Priority |
|---------|-----------|----------|
| **Specialist Verification** | API: GET /governance/roles/{person_id} | 🔴 High |
| **Auto-Create Specialist Profile** | Event: governance.person.role_assigned | 🟡 Medium |
| **Project Approval Workflow** | API: POST /governance/approvals | 🟡 Medium |

**Event Flow:**
```
Governance: person.role_assigned (role="bcm_specialist")
  ↓
Marketplace: Auto-create specialist profile
Marketplace: Set verification status
```

---

## 📋 Implementation Plan (5 Phases)

### **Phase 1: Infrastructure Alignment** (2-3 days)
**Цель:** Привести к единым паттернам с Learning/Governance

#### Tasks:
1. ✅ **Update requirements.txt**
   ```bash
   # Add to portal/requirements.txt and marketplace/requirements.txt
   ../../../shared
   python-jose[cryptography]>=3.3.0
   passlib[bcrypt]>=1.7.4
   ```
   **Time:** 30 min
   **Complexity:** Simple

2. ✅ **Fix import paths**
   ```python
   # Change in portal/main.py, marketplace/main.py
   sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))
   ```
   **Time:** 1 hour
   **Complexity:** Simple

3. ✅ **Replace auth with shared library**
   ```python
   # Delete: portal/integrations/clients_client.py
   # Update: portal/api/dependencies.py
   from shared.auth.dependencies import get_current_user_dep, require_role
   ```
   **Time:** 4-6 hours
   **Complexity:** Medium

4. ✅ **Replace EventBus with shared library**
   ```python
   # Delete: portal/integrations/eventbus_client.py
   # Update: portal/main.py
   from shared.eventbus import init_eventbus, get_eventbus
   ```
   **Time:** 6-8 hours
   **Complexity:** Medium

5. ✅ **Test basic functionality**
   - Services start without errors
   - Auth works
   - Events publish
   **Time:** 2-3 hours

**Total Phase 1:** 14-19 hours (2-3 days)

---

### **Phase 2: Event Integration** (2-3 days)
**Цель:** Enable event-driven communication

#### Tasks:
1. ✅ **Create Portal event subscribers**
   ```python
   # New file: portal/events/subscribers.py
   from shared.eventbus import get_eventbus

   async def setup_subscriptions():
       eventbus = get_eventbus()

       @eventbus.subscribe("learning.training.completed")
       async def on_training_completed(event):
           # Award forum badge
           # Update author competency
           pass

       @eventbus.subscribe("learning.certification.issued")
       async def on_certification_issued(event):
           # Grant "Verified Expert" status
           pass

       @eventbus.subscribe("governance.policy.created")
       async def on_policy_created(event):
           # Create forum discussion
           pass
   ```
   **Time:** 4-5 hours
   **Complexity:** Medium

2. ✅ **Create Marketplace event subscribers**
   ```python
   # New file: marketplace/events/subscribers.py
   @eventbus.subscribe("learning.certification.issued")
   async def on_certification_issued(event):
       # Update specialist certifications
       pass

   @eventbus.subscribe("governance.person.role_assigned")
   async def on_role_assigned(event):
       # Auto-create specialist if role=bcm_specialist
       pass
   ```
   **Time:** 3-4 hours
   **Complexity:** Medium

3. ✅ **Update shared library event types**
   ```python
   # shared/eventbus/types.py (if exists)
   PORTAL_ARTICLE_CREATED = "portal.knowledge.article_created"
   MARKETPLACE_SPECIALIST_VERIFIED = "marketplace.specialist.verified"
   ```
   **Time:** 30 min

4. ✅ **Test event flows**
   - Create training → Portal receives event
   - Issue certification → Marketplace updates
   **Time:** 2-3 hours

**Total Phase 2:** 10-13 hours (2 days)

---

### **Phase 3: API Integration** (2-3 days)
**Цель:** Service-to-service API calls

#### Tasks:
1. ✅ **Create Learning client for Portal**
   ```python
   # New file: portal/integrations/learning_client.py
   import httpx

   class LearningClient:
       async def get_person_competencies(self, person_id: str):
           async with httpx.AsyncClient() as client:
               response = await client.get(
                   f"http://localhost:8021/api/v1/learning/persons/{person_id}/competencies"
               )
               return response.json()
   ```
   **Time:** 2-3 hours

2. ✅ **Create Governance client for Portal**
   ```python
   # New file: portal/integrations/governance_client.py
   class GovernanceClient:
       async def get_policies(self, iso_clause: str = None):
           ...
   ```
   **Time:** 2-3 hours

3. ✅ **Create Learning client for Marketplace**
   ```python
   # New file: marketplace/integrations/learning_client.py
   class LearningClient:
       async def get_person_certifications(self, person_id: str):
           ...
   ```
   **Time:** 2-3 hours

4. ✅ **Create Governance client for Marketplace**
   ```python
   # New file: marketplace/integrations/governance_client.py
   class GovernanceClient:
       async def get_person_roles(self, person_id: str):
           ...
   ```
   **Time:** 2-3 hours

5. ✅ **Update API endpoints to use clients**
   - Forum profile shows competencies
   - Specialist profile shows certifications
   **Time:** 4-5 hours

**Total Phase 3:** 12-17 hours (2 days)

---

### **Phase 4: Database Extensions** (1.5-2 days)
**Цель:** Add cross-service relationships

#### Tasks:
1. ✅ **Add columns to Portal models**
   ```python
   # portal/database/models.py
   class KnowledgeArticle(Base):
       # ... existing fields ...
       related_training_program_id = Column(Integer, nullable=True)
       related_policy_id = Column(Integer, nullable=True)
       required_competency_level = Column(String(50))
   ```
   **Time:** 1-2 hours

2. ✅ **Add columns to Marketplace models**
   ```python
   # marketplace/database/models.py
   class Specialist(Base):
       # ... existing fields ...
       verified_by_role_id = Column(Integer, nullable=True)
       competency_scores = Column(JSONB, default={})
   ```
   **Time:** 1-2 hours

3. ✅ **Create junction tables**
   ```python
   # New tables
   article_competencies  # Links articles to competency areas
   scenario_policies     # Links scenarios to policies
   specialist_competencies  # Links specialists to competencies
   ```
   **Time:** 2-3 hours

4. ✅ **Write migration scripts**
   ```sql
   -- migrations/007_add_integration_columns.sql
   ALTER TABLE portal.knowledge_articles
   ADD COLUMN related_training_program_id INTEGER;
   ```
   **Time:** 2-3 hours

5. ✅ **Test migrations**
   **Time:** 1-2 hours

**Total Phase 4:** 7-12 hours (1.5 days)

---

### **Phase 5: Feature Implementation** (2.5-3 days)
**Цель:** User-facing integration features

#### Tasks:
1. ✅ **Competencies in Forum Profiles**
   ```python
   # Show user competencies from Learning Service
   @router.get("/forum/users/{user_id}/profile")
   async def get_user_profile(user_id: str):
       learning_client = LearningClient()
       competencies = await learning_client.get_person_competencies(user_id)
       # Display in profile
   ```
   **Time:** 3-4 hours

2. ✅ **Link Articles to Training**
   ```python
   # Allow linking articles to training programs
   @router.post("/knowledge/articles")
   async def create_article(
       article: ArticleCreate,
       related_training_id: int = None
   ):
       # Save with training link
   ```
   **Time:** 3-4 hours

3. ✅ **Specialist Certifications Display**
   ```python
   # Show certifications in marketplace profile
   @router.get("/specialists/{specialist_id}")
   async def get_specialist(specialist_id: str):
       learning_client = LearningClient()
       certs = await learning_client.get_person_certifications(specialist_id)
       # Include in response
   ```
   **Time:** 3-4 hours

4. ✅ **Policy References in Articles**
   ```python
   # Link articles to governance policies
   @router.get("/knowledge/articles/{article_id}")
   async def get_article(article_id: int):
       governance_client = GovernanceClient()
       policies = await governance_client.get_policies(
           iso_clause=article.iso_clause
       )
       # Show related policies
   ```
   **Time:** 3-4 hours

5. ✅ **Competency-Based Matching**
   ```python
   # Match specialists to projects by competencies
   @router.post("/projects/{project_id}/match-specialists")
   async def match_specialists(project_id: int):
       # Use competency data from Learning Service
       # Find matching specialists
   ```
   **Time:** 4-5 hours

**Total Phase 5:** 16-21 hours (2.5 days)

---

## ⏱️ Total Estimates

| Phase | Time | Complexity | Risk |
|-------|------|------------|------|
| Phase 1: Infrastructure | 14-19 hours | Medium | Medium |
| Phase 2: Events | 10-13 hours | Medium | Low |
| Phase 3: API Clients | 12-17 hours | Medium | Medium |
| Phase 4: Database | 7-12 hours | Medium | High |
| Phase 5: Features | 16-21 hours | Medium-High | Low |
| **TOTAL** | **59-82 hours** | **Medium** | **Medium** |

**Календарное время:** 8-11 рабочих дней (2 недели)

---

## ✅ Success Criteria

### Phase 1 Complete:
- ✅ Both services start with shared library
- ✅ JWT auth works via shared.auth
- ✅ Events publish via shared.eventbus
- ✅ All existing endpoints work

### Phase 2 Complete:
- ✅ Portal receives Learning events
- ✅ Marketplace receives Learning events
- ✅ Event handlers execute successfully
- ✅ Event logs show proper flow

### Phase 3 Complete:
- ✅ Portal fetches competencies from Learning
- ✅ Marketplace fetches certifications
- ✅ Error handling in place
- ✅ Caching implemented

### Phase 4 Complete:
- ✅ Migrations run successfully
- ✅ Foreign keys created
- ✅ Rollback tested
- ✅ Data integrity verified

### Phase 5 Complete:
- ✅ Forum shows competencies
- ✅ Marketplace shows certifications
- ✅ Articles link to policies/training
- ✅ All features documented

---

## 🚀 Quick Start

### Начать Phase 1:

```bash
# 1. Update requirements
cd /Users/MD/AI-Platform-ISO/platform-services/community-service/portal
# Edit requirements.txt, add shared library

# 2. Install dependencies
pip install -r requirements.txt

# 3. Test imports
python3 -c "from shared.auth.jwt_handler import verify_token; print('OK')"

# 4. Start refactoring
# - Replace clients_client.py with shared.auth
# - Replace eventbus_client.py with shared.eventbus
```

### Проверка прогресса:

```bash
# Test after each phase
python3 -m pytest tests/integration/

# Manual testing
curl http://localhost:8031/health
curl http://localhost:8032/health
```

---

## 📚 Related Docs

- **Learning Service:** `/platform-services/learning-service/`
- **Governance Service:** `/platform-services/governance-service/`
- **Shared Library:** `/shared/`
- **EventBus Events:** See `shared/eventbus/types.py`

---

**Next Step:** Start Phase 1 - Infrastructure Alignment

**Created:** 2025-10-03
**Status:** Ready to implement
