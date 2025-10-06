# Marketplace Service

**Port:** 8032
**Purpose:** Professional Marketplace для BCM консультантов ("Uber for BCM Consultants")

---

## 🎯 Overview

Marketplace Service - это профессиональный маркетплейс, соединяющий BCM специалистов с компаниями.

**Аналоги:** Upwork, Toptal (но для BCM)

**Базируется на:** BCM_1 Odoo modules (`bcm_marketplace.py`, `bcm_specialist.py`)

---

## ✅ Progress

### Completed:
- [x] Database schema design (001_marketplace_schema.sql)
- [x] SQLAlchemy models (based on BCM_1)
- [x] Database connection setup
- [ ] Pydantic schemas (in progress)
- [ ] Services layer
- [ ] API endpoints
- [ ] EventBus integration
- [ ] Docker configuration
- [ ] Gateway registration

---

## 📊 Database Schema

**Schema:** `marketplace.*`

**Tables:**
1. `specialists` - Specialist profiles
2. `certifications` - Specialist certifications
3. `portfolio_items` - Portfolio projects
4. `projects` - Service requests (from clients)
5. `proposals` - Proposals from specialists
6. `reviews` - Reviews & ratings

**Total:** 6 tables, 8 ENUMs, 3 triggers

---

## 🔑 Key Features

### Specialists
- Professional profiles
- Skills & certifications
- Portfolio showcase
- Availability calendar
- Verification system
- Rating & reviews

### Projects (Service Requests)
- Project posting by clients
- Detailed requirements
- Budget management
- Timeline planning
- Proposal collection

### Proposals
- Specialist bids
- Custom pricing
- Timeline estimates
- Methodology description

### Reviews
- 5-star rating system
- Category ratings (communication, quality, etc.)
- Verified reviews
- Specialist responses

---

## 🗄️ Models (SQLAlchemy)

### Specialist
```python
class Specialist(Base):
    - user_id (UUID) - from Clients service
    - name, title, bio
    - years_experience
    - hourly_rate
    - specializations (JSONB)
    - industries (JSONB)
    - skills (JSONB)
    - availability_status
    - rating, total_reviews
    - is_verified
```

### Project
```python
class Project(Base):
    - client_id (UUID)
    - title, description
    - service_type (ENUM)
    - urgency (ENUM)
    - budget_type, budget_min, budget_max
    - required_skills (JSONB)
    - work_location (ENUM)
    - status (ENUM)
```

### Proposal
```python
class Proposal(Base):
    - project_id
    - specialist_id
    - cover_letter
    - proposed_rate
    - estimated_duration_hours
    - status (ENUM)
```

### Review
```python
class Review(Base):
    - project_id
    - specialist_id
    - reviewer_id (UUID)
    - rating (1-5)
    - review_text
    - category_ratings
```

---

## 📡 API Endpoints (Planned)

### Specialists
- `POST /api/marketplace/specialists` - Create profile
- `GET /api/marketplace/specialists` - Browse specialists
- `GET /api/marketplace/specialists/{id}` - Get specialist
- `PUT /api/marketplace/specialists/{id}` - Update profile
- `POST /api/marketplace/specialists/{id}/verify` - Request verification

### Projects
- `POST /api/marketplace/projects` - Create project
- `GET /api/marketplace/projects` - Browse projects
- `GET /api/marketplace/projects/{id}` - Get project
- `PUT /api/marketplace/projects/{id}` - Update project
- `DELETE /api/marketplace/projects/{id}` - Cancel project

### Proposals
- `POST /api/marketplace/projects/{id}/proposals` - Submit proposal
- `GET /api/marketplace/proposals` - My proposals
- `PUT /api/marketplace/proposals/{id}` - Update proposal
- `POST /api/marketplace/proposals/{id}/accept` - Accept proposal
- `POST /api/marketplace/proposals/{id}/reject` - Reject proposal

### Reviews
- `POST /api/marketplace/specialists/{id}/reviews` - Leave review
- `GET /api/marketplace/specialists/{id}/reviews` - Get reviews

**Total:** ~35-40 endpoints

---

## 🔔 Events

Marketplace will emit events to EventBus:

### Specialist Events
- `marketplace.specialist.created`
- `marketplace.specialist.verified`
- `marketplace.specialist.profile_updated`

### Project Events
- `marketplace.project.created`
- `marketplace.project.published`
- `marketplace.project.completed`

### Proposal Events
- `marketplace.proposal.submitted`
- `marketplace.proposal.accepted`
- `marketplace.proposal.rejected`

### Review Events
- `marketplace.review.created`
- `marketplace.specialist.rating_updated`

---

## 🗂️ Project Structure

```
marketplace/
├── database/
│   ├── __init__.py
│   ├── connection.py       ✅ Done
│   ├── models.py           ✅ Done
│   └── migrations/
│       └── 001_marketplace_schema.sql  ✅ Done
├── services/
│   ├── specialist_service.py
│   ├── project_service.py
│   ├── proposal_service.py
│   └── review_service.py
├── api/
│   ├── specialists.py
│   ├── projects.py
│   ├── proposals.py
│   └── reviews.py
├── schemas/
│   ├── specialist.py
│   ├── project.py
│   ├── proposal.py
│   └── review.py
├── integrations/
│   └── eventbus_client.py
├── main.py
├── requirements.txt
├── Dockerfile
└── README.md               ✅ This file
```

---

## 🚀 Deployment

### Prerequisites
- PostgreSQL 15+ with bcm_platform database
- Clients Service running (for authentication)
- EventBus running (for events)

### Apply Migrations

```bash
docker exec -i bcm-postgres psql -U bcm_user -d bcm_platform < database/migrations/001_marketplace_schema.sql
```

### Run Service

```bash
cd marketplace/
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8032 --reload
```

### With Docker

```bash
docker-compose up -d marketplace
```

---

## 🔗 Integration

### With Clients Service (Auth)
- User authentication via JWT
- User profile integration
- Tenant context

### With Portal Service
- Expert verification sync
- Knowledge Hub expert badges
- Forum reputation integration

### With EventBus
- Emit marketplace events
- Subscribe to user events

### With Gateway
- Accessible via `/api/community/marketplace/*`
- Rate limiting
- Request logging

---

## 📊 Based on BCM_1

Marketplace Service is based on proven Odoo modules from BCM_1:

**Source files:**
- `bcm_marketplace.py` (388 lines) - Service requests
- `bcm_specialist.py` (228 lines) - Specialist profiles
- `bcm_project_tracking.py` (243 lines) - Project management

**What we're using:**
- ✅ Database schema structure
- ✅ Business logic (service types, urgency, budget types)
- ✅ Specialist profile fields
- ✅ Project request workflow
- ✅ Proposal system design

**What we're improving:**
- ➕ FastAPI instead of Odoo
- ➕ SQLAlchemy models instead of Odoo ORM
- ➕ JSONB for flexible fields (skills, specializations)
- ➕ EventBus integration
- ➕ Microservices architecture

---

## 🎯 Next Steps

1. ✅ Database schema - DONE
2. ✅ SQLAlchemy models - DONE
3. → Pydantic schemas
4. → Services layer
5. → API endpoints
6. → EventBus integration
7. → Docker configuration
8. → Gateway registration
9. → Testing
10. → Documentation

---

**Status:** 🚧 In Development (25% complete)
**Based on:** BCM_1 Odoo Modules
**Estimated completion:** 2-3 weeks
