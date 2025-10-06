# Frontend Technical Specification - Complete Summary

**Document Version:** 2.0.0
**Document Generated:** 2025-10-02
**Last Updated:** 2025-10-02
**Services Analyzed:** Portal Service (Port 8031) & Marketplace Service (Port 8032)

---

## 🎯 Overview

This document provides a **COMPLETE** analysis of all API endpoints, features, and integration flows in the Portal and Marketplace services to guide frontend development for the BCM Platform.

### ✅ What's Included (COMPLETE)

1. **Knowledge Center (Центр знаний)** - Full-featured BCM knowledge base
2. **Case Studies (Кейсы)** - Real project case studies from Marketplace
3. **Scenarios (Сценарии)** - BCM exercise scenario marketplace
4. **Community Forum** - Discussion, moderation, gamification
5. **Marketplace** - BCM consultant marketplace
6. **Cross-Service Integrations** - Complete data flow documentation

### ❌ What's Missing (Planned)

1. **Simulations (Симуляции)** - Interactive BCM simulations (NOT IMPLEMENTED)

---

## Services

1. **Portal Service** - Knowledge Center, Scenario Marketplace & Community Forum
2. **Marketplace Service** - Professional Marketplace for BCM Consultants (Uber for BCM)

---

## Portal Service (Port 8031)

### Service Components

#### 1. Knowledge Hub (14 endpoints)
- **Article Management:** Create, read, update, search articles
- **Voting System:** Upvote/downvote articles
- **Bookmarking:** Save articles for later
- **AI Generation:** Generate articles from exercises
- **Verification:** Expert review for AI-generated content
- **Forum Integration:** Create discussions about articles

**Key Features:**
- Full-text search with PostgreSQL ts_rank
- Multi-tenancy support (public + tenant articles)
- Markdown content with HTML rendering
- Article verification workflow
- ISO 22301 clause mapping

#### 2. Community Forum (17 endpoints)
- **Topics & Posts:** Create, read, update topics and nested posts
- **Voting:** Upvote/downvote topics and posts
- **Moderation:** Flag content, moderation queue, resolve flags
- **Gamification:** Reputation points, levels, badges, leaderboards
- **Solution Marking:** Mark best answers for questions

**Key Features:**
- Reputation system (5 levels: newbie → legend)
- Badge system (certification, achievement, special)
- Content moderation workflow
- Nested replies support
- Topic locking and pinning

#### 3. Scenario Marketplace (6 endpoints)
- **Scenario Catalog:** Browse BCM exercise scenarios
- **Scenario Details:** Full scenario with injects and objectives
- **Deployment:** Deploy scenarios as exercises
- **Reviews:** Rate and review scenarios

**Key Features:**
- Filter by type, industry, threat
- ISO 22301 clause mapping
- Deployment tracking
- Rating system

---

## Marketplace Service (Port 8032)

### Service Components

#### 1. Specialists (12 endpoints)
- **Profile Management:** Create, update, view profiles
- **Certifications:** Add/remove professional certifications
- **Portfolio:** Showcase past work
- **Search:** Advanced filtering by skills, location, rating
- **Verification:** Admin verification system
- **Portal Integration:** View community reputation and knowledge articles

**Key Features:**
- Profile completion percentage
- Verified badge system
- Multi-dimensional search
- Certification management
- Portfolio showcase
- Community reputation display

#### 2. Projects (12 endpoints)
- **Project Management:** Create, update, publish, complete, cancel
- **Search:** Filter by service type, budget, location, skills
- **Lifecycle:** draft → open → in_progress → completed/cancelled
- **Proposals:** View proposals for projects
- **Portal Integration:** Related BCM scenarios
- **Statistics:** Project analytics

**Key Features:**
- 7 service types (BIA, BCM Plan, Risk Assessment, ISO 22301, etc.)
- Budget types (hourly, fixed, retainer)
- Work location (remote, onsite, hybrid)
- Urgency levels
- Scenario recommendations

#### 3. Proposals (9 endpoints)
- **Submission:** Specialists submit proposals
- **Management:** Update, delete, withdraw proposals
- **Client Actions:** Accept/reject proposals
- **Statistics:** Track proposal success rates

**Key Features:**
- One proposal per specialist per project
- Critical hiring transaction (accept → auto-reject others)
- Proposal withdrawal with reason
- Performance tracking

#### 4. Reviews (9 endpoints)
- **Review Creation:** Clients review specialists
- **Multi-dimensional Ratings:** Overall + 4 category ratings
- **Specialist Response:** Respond to reviews
- **Statistics:** Rating distribution and averages
- **Moderation:** Admin can hide/verify reviews

**Key Features:**
- 5-star rating system
- Category ratings (communication, quality, professionalism, timeliness)
- Public/private reviews
- Specialist response capability
- Review statistics and analytics

---

## Critical User Flows

### Portal Flows

1. **Knowledge Discovery**
   - Search → Read → Bookmark → Vote → Discuss

2. **Expert Content Creation**
   - Create → Publish → Community engagement → Reputation

3. **AI Content Generation**
   - Exercise completion → AI generation → Expert verification → Publication

4. **Scenario Deployment**
   - Browse → Filter → View details → Deploy → Review

5. **Forum Participation**
   - Browse → Create/Reply → Vote → Mark solution → Earn reputation

### Marketplace Flows

1. **Specialist Onboarding**
   - Create profile → Add skills/certs → Admin verification → Eligible for work

2. **Client Posts Project**
   - Draft → Fill details → Publish → Specialist proposals

3. **Specialist Submits Proposal**
   - Search projects → View details → Write proposal → Submit

4. **Client Hires Specialist** ⭐ **CRITICAL FLOW**
   - Review proposals → Compare specialists → Accept → Auto-reject others → Project starts

5. **Project Completion & Review**
   - Complete work → Mark complete → Create Portal article → Client reviews → Specialist responds

---

## Integration Points

### Portal ↔ Marketplace

1. **Marketplace → Portal**
   - Display specialist's forum reputation
   - Show related knowledge articles
   - Community badges on specialist profiles

2. **Portal → Marketplace**
   - Related marketplace projects on scenarios
   - Project recommendations from Portal content
   - Cross-service user reputation

### Shared Infrastructure

- **Authentication:** JWT tokens via Clients Service
- **Multi-tenancy:** Shared tenant_id model
- **EventBus:** Event-driven integration (20+ event types)
- **User Profiles:** Consistent user data across services

---

## Authentication & Authorization

### Authentication Method
- JWT Bearer Token in Authorization header
- Token validation via Clients Service
- User data includes: user_id, tenant_id, user_type, role

### Authorization Levels

| Level | Access |
|-------|--------|
| **public** | No auth required - browse content |
| **user** | Basic authenticated user |
| **client** | Post projects, hire specialists, write reviews |
| **specialist** | Create profile, view projects |
| **verified_specialist** | Submit proposals (verified required) |
| **admin** | Full access, moderation, verification |

---

## Data Models Overview

### Portal Key Models

- **ArticleResponse:** Full article with metadata, votes, bookmarks
- **TopicResponse:** Forum topic with posts, votes, solution
- **PostResponse:** Forum post with votes, nested replies
- **ScenarioResponse:** Scenario with injects, objectives, ISO mapping
- **ReputationResponse:** User reputation, level, badges

### Marketplace Key Models

- **SpecialistResponse:** Profile with skills, rating, portfolio
- **ProjectResponse:** Project details, status, budget, requirements
- **ProposalResponse:** Proposal with budget, timeline, attachments
- **ReviewResponse:** Multi-dimensional review with specialist response

---

## Frontend Implementation Guidelines

### Pagination
- Standard pattern: `page` and `page_size` query params
- Default: page=1, page_size=20
- Max page_size: 100
- Response includes: items, total, page, page_size, total_pages

### Filtering
- **Arrays:** Comma-separated values (e.g., "skills=BIA,BCM,ISO22301")
- **Booleans:** true/false
- **Enums:** Exact string match from defined values
- **Ranges:** min_* and max_* for numeric ranges

### Markdown Content
- Input fields: content, bio, description
- Server provides: content_html (rendered)
- Use markdown editor component in frontend

### User-Specific Data
- Fields like `is_bookmarked`, `user_vote` only when authenticated
- Always check for null/undefined
- Conditionally render based on authentication state

### Error Handling

| Code | Meaning | Frontend Action |
|------|---------|-----------------|
| 400 | Bad Request | Show validation errors |
| 401 | Unauthorized | Redirect to login |
| 403 | Forbidden | Show permission error |
| 404 | Not Found | Show not found page |
| 422 | Business Logic Error | Show specific error message |
| 500 | Server Error | Show generic error, contact support |

---

## Recommended Frontend Page Structure

### Portal Pages
```
/knowledge              - Knowledge Hub home
/knowledge/articles     - Article list with filters
/knowledge/articles/:slug - Article detail
/knowledge/search       - Search results
/knowledge/bookmarks    - My bookmarks

/forum                  - Forum home
/forum/categories/:id   - Category topics
/forum/topics/:id       - Topic detail
/forum/leaderboard      - Community leaderboard

/scenarios              - Scenario marketplace
/scenarios/:id          - Scenario detail

/profile/:userId        - User profile with reputation
```

### Marketplace Pages
```
/marketplace            - Marketplace home
/projects               - Browse all projects
/projects/create        - Create project (client)
/projects/:id           - Project detail
/projects/my            - My projects (client)

/specialists            - Browse specialists
/specialists/:id        - Specialist profile
/specialists/profile    - My profile (specialist)

/proposals              - My proposals (specialist)
/reviews/my             - My reviews (client)
```

---

## State Management Recommendations

### Global State
- **Authentication:** user token, profile, permissions
- **Tenant Context:** current tenant_id
- **User Preferences:** bookmarks, votes, notification settings

### Cached Data
- Forum categories
- Badge definitions
- Enum values (service types, statuses, etc.)

### API State
- Use React Query, SWR, or similar for:
  - Automatic caching
  - Background refetching
  - Optimistic updates
  - Pagination support

---

## Enum Values Reference

### Service Types
`bia`, `bcm_plan`, `risk_assessment`, `iso_22301`, `training`, `exercise`, `consulting`

### Project Statuses
`draft`, `open`, `in_progress`, `completed`, `cancelled`

### Proposal Statuses
`pending`, `accepted`, `rejected`, `withdrawn`

### Urgency Levels
`low`, `medium`, `high`, `urgent`

### Work Locations
`remote`, `onsite`, `hybrid`

### Budget Types
`hourly`, `fixed`, `retainer`, `negotiable`

### Availability Statuses
`available`, `busy`, `unavailable`

### Verification Statuses
`pending`, `verified`, `rejected`

### Reputation Levels
`newbie`, `contributor`, `expert`, `guru`, `legend`

### Scenario Types
`tabletop`, `functional`, `full_scale`

---

## API Endpoint Count Summary

| Service | Component | Endpoints | Auth Required | Public |
|---------|-----------|-----------|---------------|--------|
| Portal | Knowledge Hub | 14 | 7 | 7 |
| Portal | Forum | 17 | 10 | 7 |
| Portal | Scenarios | 6 | 2 | 4 |
| **Portal Total** | | **37** | **19** | **18** |
| Marketplace | Specialists | 12 | 7 | 5 |
| Marketplace | Projects | 12 | 6 | 6 |
| Marketplace | Proposals | 9 | 9 | 0 |
| Marketplace | Reviews | 9 | 3 | 6 |
| **Marketplace Total** | | **42** | **25** | **17** |
| **GRAND TOTAL** | | **79** | **44** | **35** |

---

## 📊 Complete Feature Matrix

### Knowledge Center (Центр знаний)
**Status:** ✅ **FULLY IMPLEMENTED**

- ✅ Article CRUD operations
- ✅ AI article generation from exercises
- ✅ Verification workflow (pending → verified/rejected)
- ✅ Full-text search with relevance scoring
- ✅ Bookmarking system
- ✅ Voting system (upvote/downvote)
- ✅ Usefulness score calculation
- ✅ Forum integration (discuss articles)
- ✅ ISO 22301 clause mapping
- ✅ Multi-tenancy support
- ✅ Markdown content rendering

### Case Studies (Кейсы)
**Status:** ✅ **IMPLEMENTED** (as Portfolio Items in Marketplace)

- ✅ Portfolio item management
- ✅ Case study content (title, description, deliverables, outcomes)
- ✅ Media support (images, documents)
- ✅ Public/private visibility control
- ✅ Integration with completed projects
- ✅ Conversion to Portal knowledge articles
- ✅ Display on specialist profiles
- ✅ Client name (with anonymization option)
- ✅ Industry and project type categorization
- ✅ Timeline tracking (start/end dates, duration)

### Scenarios (Сценарии)
**Status:** ✅ **FULLY IMPLEMENTED**

- ✅ Scenario catalog browsing
- ✅ Filtering (by type, industry, threat)
- ✅ Deployment to Validation module as exercises
- ✅ Rating and review system
- ✅ ISO 22301 clause mapping
- ✅ Injects and learning objectives
- ✅ Deployment tracking
- ✅ Average rating calculation
- ✅ View count tracking

### Simulations (Симуляции)
**Status:** ❌ **NOT IMPLEMENTED - PLANNED**
**Priority:** HIGH

#### Planned Features:
- ❌ Interactive crisis scenarios
- ❌ Branching decision trees
- ❌ Real-time collaboration
- ❌ Performance metrics and scoring
- ❌ Simulation replay and analysis
- ❌ Team-based exercises
- ❌ Integration with Scenario Marketplace
- ❌ Results → Knowledge articles

#### Technical Requirements:
- New microservice for simulation engine
- WebSocket server for real-time updates
- State management for simulation progress
- Frontend: Interactive decision UI, timers, collaboration interface
- Backend: Scoring algorithm, integration with Portal/Validation

### Community Forum
**Status:** ✅ **FULLY IMPLEMENTED**

- ✅ Topics and nested posts
- ✅ Voting on topics and posts
- ✅ Content moderation (flagging, queue, actions)
- ✅ Reputation system (5 levels: newbie → legend)
- ✅ Badge system (certification, achievement, special)
- ✅ Leaderboards
- ✅ Solution marking
- ✅ Category organization
- ✅ ISO clause mapping

### Marketplace
**Status:** ✅ **FULLY IMPLEMENTED**

- ✅ Specialist profiles with verification
- ✅ Profile completion percentage
- ✅ Project posting (full lifecycle)
- ✅ Proposal system
- ✅ Multi-dimensional review system
- ✅ Certification management
- ✅ Portfolio/case studies
- ✅ Community reputation display
- ✅ Portal integration

---

## 🔄 Complete Data Flows

### Flow 1: Project → Case Study → Knowledge Article

1. Client posts project in Marketplace (draft)
2. Client publishes project (draft → open)
3. Specialist submits proposal
4. Client accepts proposal (open → in_progress)
5. Specialist completes work
6. Client marks project complete (in_progress → completed)
7. **Specialist adds to portfolio as case study**
8. **Specialist optionally shares as Portal knowledge article**
9. Article created with metadata: `source=marketplace_project`
10. Article tagged: `['marketplace', 'case_study', 'project_ID']`
11. Article published in Knowledge Center
12. Community discovers and votes on article
13. Specialist gains reputation from engagement
14. Article links back to specialist profile

### Flow 2: Scenario → Exercise Deployment

1. User browses Scenario Marketplace
2. User filters by type, industry, threat
3. User views scenario details
4. User deploys scenario to Validation module
5. Exercise created with injects and objectives
6. User runs exercise
7. User reviews scenario with rating
8. OPTIONALLY: User generates knowledge article from exercise
9. AI analyzes results and creates draft
10. Specialist verifies article
11. Article published and linked to scenario

### Flow 3: Knowledge Discovery Journey

1. User searches Knowledge Center
2. System returns ranked results
3. User filters by verified/ISO clause
4. User reads article, view count increments
5. User upvotes helpful content
6. User bookmarks for later
7. User starts forum discussion
8. Community engages, earns reputation

---

## 🚀 Next Steps for Frontend Development

### Phase 1: Core Infrastructure
1. **Authentication Setup**
   - Implement JWT token management
   - Create authentication context/provider
   - Handle token refresh and logout

2. **API Client Setup**
   - Create axios instances for each service
   - Implement request/response interceptors
   - Add error handling middleware

3. **Type Definitions**
   - Generate TypeScript types from schemas
   - Create API response interfaces
   - Define request payload types

### Phase 2: Knowledge Center
4. **Knowledge Center Pages**
   - Article list with search and filters
   - Article detail page
   - Bookmarks page
   - Article creation/editing
   - AI generation flow

### Phase 3: Marketplace & Case Studies
5. **Marketplace Pages**
   - Specialist profiles with portfolio
   - Case study display components
   - Project listing and details
   - Proposal management
   - Review system

### Phase 4: Scenarios & Forum
6. **Scenario Pages**
   - Scenario marketplace
   - Deployment flow
   - Review system

7. **Forum Pages**
   - Topic list and detail
   - Post creation and replies
   - Moderation interface
   - Leaderboard

### Phase 5: Integration & Polish
8. **Cross-Service Features**
   - Case study → article conversion
   - Scenario → exercise deployment
   - Community reputation display

9. **Component Library**
   - Markdown editor
   - Rating/review components
   - Pagination
   - Filter components
   - Badge/reputation displays

10. **Testing**
    - Unit tests for API clients
    - Integration tests for critical flows
    - E2E tests for user journeys

---

## Additional Resources

- **Full API Specification:** See `FRONTEND_TECHNICAL_SPECIFICATION.json`
- **Service Documentation:** Portal `/docs` and Marketplace `/docs`
- **Health Endpoints:**
  - Portal: `http://localhost:8031/health`
  - Marketplace: `http://localhost:8032/health`

---

## 📝 Implementation Summary

### ✅ What's Built and Ready
- **Knowledge Center (Центр знаний)** - Complete with 14 endpoints
- **Case Studies (Кейсы)** - Implemented as Portfolio Items with conversion to articles
- **Scenarios (Сценарии)** - Complete with 6 endpoints, deployment, and reviews
- **Community Forum** - Complete with 17 endpoints, gamification, moderation
- **Marketplace** - Complete with 42 endpoints, full lifecycle
- **Cross-Service Integration** - Portal ↔ Marketplace flows documented

### ❌ What's Missing
- **Simulations (Симуляции)** - Interactive BCM training simulations (HIGH PRIORITY)

### 📈 Statistics
- **Total Endpoints:** 79 (37 Portal + 42 Marketplace)
- **Authenticated Endpoints:** 44
- **Public Endpoints:** 35
- **User Flows Documented:** 12+
- **Data Models Defined:** 10+
- **Integration Flows:** 3 major flows fully documented

### 🎯 Frontend Team Action Items

1. **PRIORITY 1:** Implement Knowledge Center with search, bookmarks, voting
2. **PRIORITY 2:** Build Marketplace with specialist profiles and portfolio/case studies
3. **PRIORITY 3:** Create Scenario marketplace with deployment flow
4. **PRIORITY 4:** Implement Forum with reputation and badges
5. **PRIORITY 5:** Build cross-service integrations (case study → article, scenario → exercise)
6. **FUTURE:** Plan and implement Simulations module (new microservice required)

### 📚 Key Integration Points to Implement

1. **Project Completion → Portfolio Item**
   - Marketplace endpoint: `POST /api/marketplace/specialists/{id}/portfolio`
   - Display on specialist profile

2. **Portfolio Item → Knowledge Article**
   - Portal endpoint: `POST /api/portal/knowledge/articles`
   - Tag with `source=marketplace_project`

3. **Scenario Deployment → Exercise**
   - Portal endpoint: `POST /api/portal/scenarios/{id}/deploy`
   - Calls Validation module API

4. **Exercise Completion → Knowledge Article**
   - Portal endpoint: `POST /api/portal/knowledge/ai-generate`
   - Requires verification workflow

5. **Community Reputation → Specialist Profile**
   - Portal endpoint: `GET /api/portal/forum/reputation/{user_id}`
   - Display on Marketplace profile

---

**Document Version:** 2.0.0 (COMPLETE EDITION)
**Last Updated:** 2025-10-02
**Maintained By:** Platform Development Team

**Completeness Status:** ✅ All existing features documented | ❌ Simulations module pending implementation
