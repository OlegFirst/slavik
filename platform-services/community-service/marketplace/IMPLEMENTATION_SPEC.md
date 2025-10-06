# Marketplace Service - Implementation Specification

**Port:** 8032
**Status:** 🚧 25% Complete (Foundation Ready)
**Next:** Implement Pydantic schemas → Services → API

---

## ✅ DONE (Foundation)

1. **Database Schema** (`database/migrations/001_marketplace_schema.sql`)
   - 6 tables: specialists, certifications, portfolio_items, projects, proposals, reviews
   - 8 ENUMs, 3 triggers

2. **SQLAlchemy Models** (`database/models.py`)
   - Specialist, Certification, PortfolioItem
   - Project, Proposal, Review
   - All relationships configured

3. **Infrastructure**
   - Directory structure
   - database/connection.py
   - README.md

---

## 🎯 TODO (Next Steps)

### Step 1: Pydantic Schemas
**File:** `schemas/specialist.py`, `schemas/project.py`, etc.

```python
# schemas/specialist.py
class SpecialistBase(BaseModel):
    name: str
    title: Optional[str]
    bio: Optional[str]
    years_experience: int = 0
    hourly_rate: Optional[Decimal]
    specializations: List[str] = []
    industries: List[str] = []
    availability_status: AvailabilityStatus

class SpecialistCreate(SpecialistBase):
    user_id: UUID

class SpecialistUpdate(BaseModel):
    # All fields optional

class SpecialistResponse(SpecialistBase):
    id: int
    user_id: UUID
    rating: Decimal
    total_reviews: int
    is_verified: bool
    created_at: datetime
```

### Step 2: Services Layer
**File:** `services/specialist_service.py`

```python
class SpecialistService:
    async def create_specialist(db, data: SpecialistCreate) -> Specialist
    async def get_specialist(db, specialist_id: int) -> Specialist
    async def update_specialist(db, specialist_id: int, data) -> Specialist
    async def list_specialists(db, filters, pagination) -> List[Specialist]
    async def search_specialists(db, skills, location, rating_min) -> List[Specialist]
    async def verify_specialist(db, specialist_id, admin_id) -> Specialist
```

### Step 3: API Endpoints
**File:** `api/specialists.py`

```python
@router.post("/specialists")  # Create profile
@router.get("/specialists")  # List/search
@router.get("/specialists/{id}")  # Get one
@router.put("/specialists/{id}")  # Update
@router.post("/specialists/{id}/verify")  # Verify
@router.get("/specialists/{id}/certifications")
@router.post("/specialists/{id}/certifications")
@router.get("/specialists/{id}/portfolio")
@router.post("/specialists/{id}/portfolio")
```

### Step 4: EventBus Integration
**File:** `integrations/eventbus_client.py`

```python
# Events to emit:
- marketplace.specialist.created
- marketplace.specialist.verified
- marketplace.project.created
- marketplace.proposal.submitted
- marketplace.proposal.accepted
- marketplace.review.created
```

### Step 5: Main App
**File:** `main.py`

```python
from fastapi import FastAPI
from api import specialists, projects, proposals, reviews

app = FastAPI(title="Marketplace Service", port=8032)
app.include_router(specialists.router)
app.include_router(projects.router)
app.include_router(proposals.router)
app.include_router(reviews.router)
```

### Step 6: Docker
**Files:** `Dockerfile`, `requirements.txt`, `docker-compose.yml`

### Step 7: Gateway Registration
**File:** `/PLATFORM/gateway/main.py`

```python
SERVICE_REGISTRY = {
    # ...
    "marketplace": {
        "url": "http://localhost:8032",
        "health": "/health",
        "prefix": "/api/community/marketplace"
    }
}
```

---

## 📋 Models Reference (from database/models.py)

### Specialist
- user_id, tenant_id, name, title, bio
- years_experience, hourly_rate
- specializations, industries, skills (JSONB)
- availability_status, timezone
- country, state, city, remote_available
- rating, total_reviews, completed_projects
- is_verified

### Project
- client_id, tenant_id, title, description
- service_type, urgency
- budget_type, budget_min, budget_max
- required_skills (JSONB)
- work_location, status
- selected_proposal_id, selected_specialist_id

### Proposal
- project_id, specialist_id
- cover_letter, proposed_rate
- estimated_duration_hours
- status, viewed_by_client

### Review
- project_id, specialist_id, reviewer_id
- rating (1-5)
- review_text
- communication_rating, quality_rating, etc.

---

## 🔗 Integration Points

### Clients Service (8030)
- Authentication (JWT)
- user_id references
- Tenant context

### Portal Service (8031)
- Expert badges sync
- Reputation integration

### EventBus (8001)
- Publish marketplace events
- Subscribe to user events

### Gateway (8000)
- Route `/api/community/marketplace/*`

---

## 📝 Implementation Order

1. ✅ Database schema - DONE
2. ✅ Models - DONE
3. → **Pydantic schemas** (START HERE)
4. → Services (SpecialistService first)
5. → API (Specialists endpoints first)
6. → Repeat for Projects, Proposals, Reviews
7. → EventBus integration
8. → main.py + Dockerfile
9. → Gateway registration
10. → Testing

---

## 🎯 Quick Reference from BCM_1

**Source:** `/COMMUNITY/BCM_1/bcm_community/models/`
- `bcm_specialist.py` (228 lines) - Specialist model reference
- `bcm_marketplace.py` (388 lines) - Project model reference
- `bcm_project_tracking.py` (243 lines) - Additional logic

**Key fields from BCM_1:**
- Service types: consulting, assessment, bia, planning, training, audit, implementation, crisis_support
- Urgency: low, medium, high, urgent
- Budget types: hourly, fixed, negotiable
- Work location: remote, onsite, hybrid

---

## 📦 Requirements.txt Template

```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
pydantic==2.5.0
python-multipart==0.0.6
httpx==0.25.1
```

---

## 🚀 Deployment Commands

```bash
# Apply migration
docker exec -i bcm-postgres psql -U bcm_user -d bcm_platform < database/migrations/001_marketplace_schema.sql

# Run service
cd marketplace/
uvicorn main:app --host 0.0.0.0 --port 8032 --reload
```

---

**Current Status:** Foundation ready (database + models)
**Next Action:** Create Pydantic schemas
**Location:** `/SERVICES/COMMUNITY/marketplace/`
**Estimated:** 2-3 weeks for full MVP
