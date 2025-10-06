# BCM Learning Service

**ISO 22301:2019 Clauses 7.2 & 7.3 - Competence & Awareness**
**BCI GPG Practice 2 (PP2: Embracing BC)**

## Overview

The Learning Service provides comprehensive training, competency, and awareness management for Business Continuity Management (BCM) aligned with ISO 22301 standards and BCI Good Practice Guidelines.

### Core Features

- 🎓 **Training Programs** - Create and manage BCM training programs (basic → expert levels)
- 📊 **Competency Assessment** - Identify and track competency gaps (ISO 7.2)
- 📢 **Awareness Campaigns** - Run organization-wide awareness initiatives (ISO 7.3)
- 🏆 **Gamification** - Points, achievements, leaderboards, and learning streaks
- 📄 **Template Library** - Reusable training content and scenarios
- 📈 **Analytics** - Track completion rates, effectiveness, and compliance

## Architecture

```
learning/
├── main.py                          # FastAPI application (26 endpoints)
├── database/
│   ├── models.py                    # SQLAlchemy models (6 core models)
│   ├── connection.py                # Async DB connection
│   ├── init_db.sql                  # PostgreSQL schema
│   ├── learning_seed.sql            # 88 reference records
│   └── bci_gpg_training_seed.sql    # 52 BCI GPG records
├── workflows/
│   ├── training_workflow.py         # State machine: enrolled → certified
│   └── gamification_workflow.py     # Points, achievements, streaks
└── requirements.txt
```

## Database Schema

**PostgreSQL Schema**: `learning.*`

### Core Tables

1. **training_programs** - Training course catalog
2. **training_enrollments** - Individual enrollment tracking
3. **competency_assessments** - Competency gap analysis
4. **awareness_campaigns** - ISO 7.3 campaigns
5. **training_templates** - Template library
6. **user_achievements** - Gamification tracking

### Multi-Tenancy

Row Level Security (RLS) enforced on all tables via `tenant_id`.

## API Endpoints

### Training Programs (5 endpoints)

```bash
POST   /api/learning/programs          # Create training program
GET    /api/learning/programs          # List programs (filters: status, type, bci_level)
GET    /api/learning/programs/{id}     # Get program details
PATCH  /api/learning/programs/{id}     # Update program
DELETE /api/learning/programs/{id}     # Archive program
```

### Training Enrollments (7 endpoints)

```bash
POST   /api/learning/enrollments                    # Enroll in program
GET    /api/learning/enrollments                    # List enrollments
POST   /api/learning/enrollments/{id}/start         # Start training
PATCH  /api/learning/enrollments/{id}/progress      # Update progress
POST   /api/learning/enrollments/{id}/complete      # Complete training
POST   /api/learning/enrollments/{id}/assess        # Submit assessment
POST   /api/learning/enrollments/{id}/certify       # Issue certification
```

#### Enrollment State Machine

```
ENROLLED → IN_PROGRESS → COMPLETED → CERTIFIED
    ↓                                      ↓
WITHDRAWN                              FAILED
                                          ↓
                                    (re-enroll)
```

### Competency Assessments (4 endpoints)

```bash
POST   /api/learning/competency                     # Create assessment
GET    /api/learning/competency                     # List assessments
GET    /api/learning/competency/gaps                # Gap analysis report
PATCH  /api/learning/competency/{id}/close-gap      # Close gap
```

**Competency Levels**: Basic → Intermediate → Advanced → Expert

### Awareness Campaigns (3 endpoints)

```bash
POST   /api/learning/campaigns          # Create campaign (ISO 7.3)
GET    /api/learning/campaigns          # List campaigns
PATCH  /api/learning/campaigns/{id}     # Update campaign
```

### Templates (1 endpoint)

```bash
GET    /api/learning/templates          # List training templates
```

### Gamification (5 endpoints)

```bash
POST   /api/learning/gamification/award-points      # Award points
GET    /api/learning/gamification/leaderboard       # Top 10 leaderboard
GET    /api/learning/gamification/achievements/{person_id}
GET    /api/learning/gamification/streak/{person_id}
GET    /api/learning/gamification/level/{person_id}
```

## ISO 22301 Compliance Mapping

| ISO Clause | Requirement | Implementation |
|------------|-------------|----------------|
| **7.2** | Competence | `competency_assessments` table, gap analysis |
| **7.2.1** | Determine competence | Competency areas, required levels |
| **7.2.2** | Training plans | `training_programs`, enrollment tracking |
| **7.2.3** | Evidence | Assessment records, certifications |
| **7.3** | Awareness | `awareness_campaigns` table |
| **7.3.1** | BC awareness | Campaign types, target groups |
| **7.3.2** | Communication | Communication channels tracking |

## BCI GPG Compliance

### Practice 2 (PP2: Embracing BC)

| Component | Implementation |
|-----------|----------------|
| **Training Levels** | Basic → Intermediate → Advanced → Specialist → Leadership |
| **Target Audiences** | All staff, line managers, BC team, BC professionals, executives |
| **Competency Framework** | 11 competency areas across all 6 PP |
| **Awareness Programs** | 8 campaign types (onboarding, annual, role-based, etc.) |
| **Effectiveness** | KPIs: completion rate, assessment scores, participation |

### BCI Training Levels

```python
'basic_awareness'    # 1-2 hours  | All staff
'intermediate'       # 4-8 hours  | Line managers
'advanced'           # 16-24 hrs  | BC team members
'specialist'         # 40-80 hrs  | BC professionals
'leadership'         # 8-16 hrs   | Executives
```

## Gamification System

### Points Actions (21 types)

```python
training_complete: 100 pts
certification_earned: 500 pts
assessment_excellence: 100 pts  # 90%+ score
gap_closed: 200 pts
competency_level_up: 150 pts
mentor_session: 75 pts
daily_login: 2 pts
```

### Achievements (19 types)

- **Training**: First training, 7-day streak, 30-day streak, perfect score
- **Competency**: Master level, gap closer, skill collector
- **Contribution**: Content creator, template master, quality reviewer
- **Team**: Team player, department champion, awareness ambassador
- **Certification**: ISO certified, BC professional

### Levels (7 tiers)

```python
0     → Beginner
100   → Learner
500   → Practitioner
1000  → Professional
2500  → Expert
5000  → Master
10000 → Champion
```

## Healthcare Compliance

Supports healthcare-specific requirements:

- **CMS Emergency Preparedness Rule** - Annual training
- **Joint Commission Standards** - Cross-training requirements
- **CDC/WHO** - Pandemic response training
- **HIPAA** - Incident response training

## Installation & Setup

### 1. Install Dependencies

```bash
cd /Users/MD/ISO-22301—копия/services/SERVICES/BCM/learning
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Run schema initialization
psql -h localhost -U postgres -d bcm_platform -f database/init_db.sql

# Load seed data
psql -h localhost -U postgres -d bcm_platform -f database/learning_seed.sql
psql -h localhost -U postgres -d bcm_platform -f database/bci_gpg_training_seed.sql
```

### 3. Environment Variables

```bash
export DATABASE_URL="postgresql+asyncpg://bcm_user:password@localhost:5432/bcm_platform"
export PORT=8021
export EVENTBUS_URL="http://localhost:8001"
```

### 4. Run Service

```bash
# Development
python main.py

# Production (with uvicorn)
uvicorn main:app --host 0.0.0.0 --port 8021 --workers 4
```

## Usage Examples

### Create Training Program

```bash
curl -X POST http://localhost:8021/api/learning/programs \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "org_001",
    "program_code": "BCM_BASIC_2024",
    "program_name": "BCM Basic Awareness Training",
    "program_type": "bcm_awareness",
    "bci_training_level": "basic_awareness",
    "duration_hours": 2,
    "passing_score": 70,
    "certification_awarded": true
  }'
```

### Enroll in Training

```bash
curl -X POST http://localhost:8021/api/learning/enrollments \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "org_001",
    "program_id": 1,
    "person_id": "user_123",
    "person_name": "John Doe",
    "person_email": "john@example.com",
    "department": "IT"
  }'
```

### Complete Full Training Journey

```bash
# 1. Start training
curl -X POST http://localhost:8021/api/learning/enrollments/1/start

# 2. Update progress
curl -X PATCH http://localhost:8021/api/learning/enrollments/1/progress \
  -d '{"progress_percentage": 100}'

# 3. Complete training
curl -X POST http://localhost:8021/api/learning/enrollments/1/complete

# 4. Submit assessment
curl -X POST http://localhost:8021/api/learning/enrollments/1/assess \
  -d '{"assessment_score": 85}'

# 5. Issue certification
curl -X POST http://localhost:8021/api/learning/enrollments/1/certify
```

### Create Competency Assessment

```bash
curl -X POST http://localhost:8021/api/learning/competency \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "org_001",
    "person_id": "user_123",
    "person_name": "John Doe",
    "competency_area": "incident_response",
    "required_level": "advanced",
    "current_level": "intermediate"
  }'
```

### Get Gap Analysis

```bash
curl http://localhost:8021/api/learning/competency/gaps?tenant_id=org_001
```

### Create Awareness Campaign

```bash
curl -X POST http://localhost:8021/api/learning/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "org_001",
    "campaign_name": "BCM Awareness Week 2024",
    "campaign_type": "annual_awareness",
    "target_groups": ["all_staff", "management"],
    "communication_channels": ["email", "intranet", "posters"],
    "start_date": "2024-10-01T00:00:00Z",
    "end_date": "2024-10-07T23:59:59Z"
  }'
```

### Get Leaderboard

```bash
curl http://localhost:8021/api/learning/gamification/leaderboard?tenant_id=org_001&limit=10
```

## Workflows

### Training Enrollment Workflow

Implemented in `workflows/training_workflow.py`:

```python
# State validation
can_start_training(enrollment)        # enrolled → in_progress
can_complete_training(enrollment)     # in_progress → completed
can_issue_certification(enrollment)   # completed → certified

# Data validation
validate_enrollment_data(data)
validate_progress_update(progress)
validate_assessment_score(score, passing_score)
```

### Gamification Workflow

Implemented in `workflows/gamification_workflow.py`:

```python
# Points
calculate_points(action_code)
award_points(person_id, action_code, context)

# Achievements
check_achievements(person_id, person_stats)

# Streaks
calculate_streak(person_id, activity_dates)

# Levels
calculate_level(total_points)
```

## Data Model

### TrainingProgram

```python
{
  "program_code": "BCM_BASIC_2024",
  "program_name": "BCM Basic Awareness",
  "program_type": "bcm_awareness",
  "bci_training_level": "basic_awareness",
  "duration_hours": 2,
  "learning_objectives": [...],
  "curriculum": [...],
  "assessment_required": true,
  "passing_score": 70,
  "certification_awarded": true,
  "status": "published"
}
```

### TrainingEnrollment

```python
{
  "program_id": 1,
  "person_id": "user_123",
  "status": "in_progress",
  "progress_percentage": 75,
  "modules_completed": [...],
  "assessment_score": null,
  "certification_issued": false,
  "points_earned": 110
}
```

### CompetencyAssessment

```python
{
  "person_id": "user_123",
  "competency_area": "incident_response",
  "required_level": "advanced",
  "current_level": "intermediate",
  "gap_exists": true,
  "gap_severity": "medium",
  "training_required": true,
  "recommended_programs": [...]
}
```

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Async tests
pytest -v tests/test_workflows.py
```

## Monitoring

Health check endpoint:

```bash
curl http://localhost:8021/health

Response:
{
  "status": "healthy",
  "service": "learning",
  "version": "1.0.0",
  "timestamp": "2024-10-01T12:00:00Z"
}
```

## Integration Points

### Event Bus

Publishes events to `http://localhost:8001`:

- `training.enrolled`
- `training.completed`
- `certification.issued`
- `competency.gap_identified`
- `achievement.unlocked`

### External Systems

- **Governance Service** - Competency requirements from roles
- **Analysis Service** - Risk-based training needs
- **Incident Service** - Post-incident training recommendations

## Seed Data Summary

### Reference Tables (140 records)

1. **competency_areas** (10) - incident_response, business_continuity, risk_assessment...
2. **learning_styles** (6) - adaptive, intensive, supportive...
3. **program_types** (8) - bcm_awareness, role_based, certification_prep...
4. **template_types** (14) - forms, checklists, documents...
5. **scenario_categories** (10) - crisis, exercises, playbooks...
6. **achievement_types** (19) - first_training, streak_7, competency_master...
7. **points_actions** (21) - training_complete, gap_closed, mentor_session...
8. **bci_training_levels** (5) - basic → leadership
9. **healthcare_training_types** (8) - CMS, Joint Commission, WHO...
10. **bci_competency_framework** (11) - PP2 competencies
11. **awareness_campaign_types** (8) - onboarding, annual, role-based...
12. **assessment_methods** (10) - self-assessment, manager, peer...
13. **training_kpis** (10) - completion rate, effectiveness...

## License

Proprietary - BCM Platform

## Support

For issues or questions, contact the BCM Platform team.

---

**Service Status**: ✅ Production Ready
**ISO 22301 Coverage**: 100% (Clauses 7.2 & 7.3)
**BCI GPG Coverage**: 100% (Practice 2)
**Total Endpoints**: 26
**Database Tables**: 6 core + 13 reference
