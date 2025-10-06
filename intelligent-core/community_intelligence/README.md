# Community Intelligence Service

**Port:** 8030
**Status:** Production Ready
**Version:** 1.0.0

## Documentation

All technical documentation is located in the [`docs/`](docs/) folder:
- **[Technical Specification](docs/TECHNICAL_SPECIFICATION.md)** - Comprehensive technical documentation
- **[Analysis and Improvements](docs/ANALYSIS_AND_IMPROVEMENTS.md)** - Production readiness assessment and recommendations

Archived documentation can be found in [`archive/docs/`](archive/docs/).

---

## 🎯 Purpose

Transforms passive case collection into **active community-driven knowledge creation** through:

- **Workflow Integration:** Auto-capture success stories from completed workflows
- **Peer Review:** Quality assurance through expert validation
- **Reputation Economy:** Gamification to incentivize contributions
- **Case Library:** Searchable knowledge base of best practices

---

## 🏗️ Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

```
Workflow Completion
    ↓
Auto-offer Contribution (or auto-submit if opted-in)
    ↓
Anonymize Case Data
    ↓
Assign 3 Peer Reviewers (smart matching)
    ↓
Reviews Collected (quality scored 1-10)
    ↓
2/3 Approve → Case Library + Reputation
    ↓
AI uses cases to help future users
```

---

## ⚡ Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
EVENTBUS_URL=http://localhost:8001
ANTHROPIC_API_KEY=...
```

### 2. Database Migration

```bash
# Apply migration
psql $DATABASE_URL -f ../../infrastructure/database/migrations_source/040_community_intelligence.sql
```

### 3. Run Service

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
python main.py
```

Service starts on **http://localhost:8030**

### 4. API Documentation

Visit **http://localhost:8030/docs** for interactive Swagger UI

---

## 📡 API Endpoints

### Contributions

```
POST   /api/v1/community/contributions
GET    /api/v1/community/contributions/my
GET    /api/v1/community/contributions/{id}
DELETE /api/v1/community/contributions/{id}
POST   /api/v1/community/contributions/preview-anonymization
POST   /api/v1/community/contributions/from-workflow/{workflow_id}
```

### Peer Reviews

```
POST   /api/v1/community/reviews
GET    /api/v1/community/reviews/pending
GET    /api/v1/community/reviews/my
GET    /api/v1/community/reviews/{id}
```

### Reputation

```
GET    /api/v1/community/reputation/{user_id}
GET    /api/v1/community/reputation/{user_id}/expertise/{module}
GET    /api/v1/community/reputation/leaderboard/global
GET    /api/v1/community/reputation/leaderboard/{module}
GET    /api/v1/community/reputation/transactions/{user_id}
```

### Case Library

```
GET    /api/v1/community/cases/search
GET    /api/v1/community/cases/{id}
GET    /api/v1/community/cases/similar/for-workflow
GET    /api/v1/community/cases/stats/overview
```

---

## 🚀 Deployment

See main README for deployment instructions.

---

**Built with ❤️ for the BCM community**
