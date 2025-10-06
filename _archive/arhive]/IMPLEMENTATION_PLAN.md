# Implementation Plan - AI-Platform-ISO Community Service

**Created:** 2025-10-02
**Status:** 🚀 Ready to Execute
**Priority:** Backend First → Frontend Second

---

## 📊 Current Status Summary

### ✅ COMPLETED (100%)
1. **Community Service Migration**
   - Portal Service (8031) - 38 endpoints ✅
   - Marketplace Service (8032) - 46 endpoints ✅
   - Supabase integration ✅
   - Database migrations applied ✅
   - Services running and tested ✅

2. **Architecture & Documentation**
   - Complete architecture blueprint ✅
   - INTELLIGENCE service analysis ✅
   - Learning service analysis ✅
   - Frontend analysis (bcm-marketplace) ✅
   - UI/UX master blueprint (130+ screens) ✅

### ⏳ IN PROGRESS (0%)
- Nothing currently running

### 📋 TODO
1. Backend: Learning Service migration
2. Backend: Simulations integration
3. Frontend: Copy and adapt bcm-marketplace
4. Frontend: Create missing components

---

## 🎯 Implementation Strategy

### Phase 1: Backend Completion (Priority)
**Goal:** All 130+ API endpoints ready and tested

### Phase 2: Frontend Implementation
**Goal:** Working MVP with all core features

### Phase 3: Testing & Polish
**Goal:** Production-ready platform

---

## 📝 PHASE 1: Backend Completion (Days 1-2)

### Task 1.1: Migrate Learning Service ⚡ HIGH PRIORITY
**Time:** 4-6 hours
**Location:** `/Users/MD/AI-Platform-ISO/platform-services/learning-service/`

**Steps:**
1. Create directory structure
   ```bash
   mkdir -p /Users/MD/AI-Platform-ISO/platform-services/learning-service
   ```

2. Copy Learning Service from old project
   ```bash
   cp -r /Users/MD/ISO-22301—копия/services/SERVICES/BCM/learning/* \
         /Users/MD/AI-Platform-ISO/platform-services/learning-service/
   ```

3. Update database connection to use Supabase
   - File: `database/connection.py`
   - Change from local PostgreSQL to Supabase
   - Update connection string
   - Add SSL configuration

4. Create database migration
   - File: `migrations/002_learning_schema.sql`
   - Tables:
     - learning.training_programs
     - learning.training_enrollments
     - learning.competency_assessments
     - learning.awareness_campaigns
     - learning.training_templates
     - learning.user_achievements
   - Include 88 reference records + 52 BCI GPG records

5. Apply migration to Supabase
   ```bash
   cd /Users/MD/AI-Platform-ISO/platform-services/learning-service
   python3 migrations/apply_migration.py
   ```

6. Update main.py configuration
   - Port: 8033
   - EventBus URL
   - Supabase credentials from .env

7. Test all 26 endpoints
   ```bash
   cd learning-service
   python3 -m uvicorn main:app --host 0.0.0.0 --port 8033 --reload
   ```

8. Verify with curl/Postman
   - POST /api/learning/programs
   - GET /api/learning/programs
   - POST /api/learning/enrollments
   - GET /api/learning/competency

**Checklist:**
- [ ] Directory created
- [ ] Files copied
- [ ] Database connection updated
- [ ] Migration created
- [ ] Migration applied
- [ ] Service starts without errors
- [ ] All 26 endpoints responding
- [ ] EventBus integration working

---

### Task 1.2: Integrate Simulations into Portal ⚡ HIGH PRIORITY
**Time:** 6-8 hours
**Location:** `/Users/MD/AI-Platform-ISO/platform-services/community-service/portal/`

**Steps:**

1. Copy simulation API routers
   ```bash
   # Source
   /Users/MD/ISO-22301—копия/services/SERVICES/INTELLIGENCE/simulation/api/

   # Destination
   /Users/MD/AI-Platform-ISO/platform-services/community-service/portal/api/simulations/
   ```

   Files to copy:
   - simulation_router.py
   - scenario_router.py
   - execution_router.py
   - scenario_library_router.py
   - __init__.py

2. Copy simulation engines
   ```bash
   # Source
   /Users/MD/ISO-22301—копия/services/SERVICES/INTELLIGENCE/simulation/engines/

   # Destination
   /Users/MD/AI-Platform-ISO/platform-services/community-service/portal/engines/
   ```

   Files:
   - base_engine.py
   - what_if_engine.py
   - monte_carlo_engine.py
   - scenario_engine.py
   - __init__.py

3. Copy simulation models
   ```bash
   # Source
   /Users/MD/ISO-22301—копия/services/SERVICES/INTELLIGENCE/simulation/models/

   # Destination
   /Users/MD/AI-Platform-ISO/platform-services/community-service/portal/database/
   ```

   File:
   - simulation_model.py (merge with existing models.py)

4. Update imports in routers
   ```python
   # Change from:
   from models.simulation_model import Simulation

   # To:
   from database.models import Simulation, Scenario, SimulationExecution, SimulationResult
   ```

5. Register routers in portal/main.py
   ```python
   from api.simulations import (
       simulation_router,
       scenario_router,
       execution_router,
       scenario_library_router
   )

   app.include_router(simulation_router.router, prefix="/api/simulations", tags=["Simulations"])
   app.include_router(scenario_router.router, prefix="/api/simulations", tags=["Scenarios"])
   app.include_router(execution_router.router, prefix="/api/simulations", tags=["Execution"])
   app.include_router(scenario_library_router.router, prefix="/api/simulations", tags=["Library"])
   ```

6. Create simulation schema migration
   ```bash
   # Create file
   /Users/MD/AI-Platform-ISO/platform-services/community-service/migrations/003_simulation_schema.sql
   ```

   Tables:
   - simulation.simulations
   - simulation.scenarios
   - simulation.executions
   - simulation.results

7. Apply migration
   ```bash
   cd /Users/MD/AI-Platform-ISO/platform-services/community-service
   python3 migrations/apply_migration.py --file 003_simulation_schema.sql
   ```

8. Update shared database connection
   - Add simulation schema to search_path
   - File: `shared/database/connection.py`
   ```python
   "search_path": "portal,marketplace,simulation,public"
   ```

9. Test simulation endpoints
   ```bash
   # Portal service should auto-reload
   # Test at http://localhost:8031/api/simulations/
   ```

10. Verify endpoints:
    - POST /api/simulations/simulations
    - GET /api/simulations/simulations
    - POST /api/simulations/scenarios
    - POST /api/simulations/simulations/{id}/run
    - GET /api/simulations/library

**Checklist:**
- [ ] API routers copied
- [ ] Engines copied
- [ ] Models merged
- [ ] Imports updated
- [ ] Routers registered in main.py
- [ ] Migration created
- [ ] Migration applied
- [ ] All 20+ endpoints responding
- [ ] Engines working (What-If, Monte Carlo, Scenario)
- [ ] Scenario library accessible

---

### Task 1.3: Add News & Events Endpoints 🔶 MEDIUM PRIORITY
**Time:** 2-3 hours
**Location:** `/Users/MD/AI-Platform-ISO/platform-services/community-service/portal/`

**Steps:**

1. Database already has tables:
   - portal.news_items ✅
   - portal.event_items ✅

2. Create API routers
   - File: `portal/api/news_router.py`
   - File: `portal/api/events_router.py`

3. Implement CRUD endpoints

   **News Endpoints:**
   - POST /api/news - Create news item
   - GET /api/news - List news (filters: category, date)
   - GET /api/news/{id} - Get news item
   - PATCH /api/news/{id} - Update news
   - DELETE /api/news/{id} - Delete news

   **Events Endpoints:**
   - POST /api/events - Create event
   - GET /api/events - List events (filters: type, date, location)
   - GET /api/events/{id} - Get event details
   - POST /api/events/{id}/register - Register for event
   - GET /api/events/{id}/attendees - Get attendees
   - PATCH /api/events/{id} - Update event
   - DELETE /api/events/{id} - Delete event

4. Register in main.py
   ```python
   from api import news_router, events_router

   app.include_router(news_router.router, prefix="/api/news", tags=["News"])
   app.include_router(events_router.router, prefix="/api/events", tags=["Events"])
   ```

5. Test endpoints

**Checklist:**
- [ ] news_router.py created
- [ ] events_router.py created
- [ ] CRUD operations implemented
- [ ] Routers registered
- [ ] Endpoints tested
- [ ] EventBus integration (optional)

---

### Task 1.4: Backend Testing & Documentation 🔶 MEDIUM PRIORITY
**Time:** 2-3 hours

**Steps:**

1. Test all services with Postman/curl
   - Portal (8031): 58 endpoints (38 + 20)
   - Marketplace (8032): 46 endpoints
   - Learning (8033): 26 endpoints
   - **Total: 130 endpoints**

2. Create API documentation
   - Update OpenAPI/Swagger docs
   - Add examples for each endpoint
   - Document authentication requirements

3. Test cross-service integration
   - Portal → Marketplace (case studies)
   - Learning → Portal (knowledge articles)
   - Simulations → Learning (certificates)

4. Performance testing
   - Load test with 100 concurrent requests
   - Check database connection pooling
   - Verify caching works

5. Create Postman collection
   - Export all endpoints
   - Add environment variables
   - Share with team

**Checklist:**
- [ ] All endpoints tested manually
- [ ] API docs updated
- [ ] Cross-service calls working
- [ ] Performance acceptable
- [ ] Postman collection exported

---

## 📝 PHASE 2: Frontend Implementation (Days 3-5)

### Task 2.1: Copy & Setup Frontend ⚡ HIGH PRIORITY
**Time:** 2-3 hours

**Steps:**

1. Copy bcm-marketplace to AI-Platform-ISO
   ```bash
   cp -r /Users/MD/ISO-22301—копия/services/SERVICES/frontend/bcm-marketplace \
         /Users/MD/AI-Platform-ISO/frontend/
   ```

2. Rename and cleanup
   ```bash
   cd /Users/MD/AI-Platform-ISO/frontend/
   mv bcm-marketplace bcm-platform
   cd bcm-platform
   rm -rf node_modules .next
   ```

3. Update package.json
   ```json
   {
     "name": "bcm-platform",
     "version": "1.0.0"
   }
   ```

4. Install dependencies
   ```bash
   npm install
   # or
   pnpm install
   ```

5. Create .env.local
   ```bash
   NEXT_PUBLIC_PORTAL_URL=http://localhost:8031
   NEXT_PUBLIC_MARKETPLACE_URL=http://localhost:8032
   NEXT_PUBLIC_LEARNING_URL=http://localhost:8033
   NEXT_PUBLIC_WS_URL=ws://localhost:8031
   ```

6. Test dev server
   ```bash
   npm run dev
   # Open http://localhost:3000
   ```

**Checklist:**
- [ ] Frontend copied
- [ ] Dependencies installed
- [ ] .env.local configured
- [ ] Dev server running
- [ ] No build errors

---

### Task 2.2: Update API Client ⚡ HIGH PRIORITY
**Time:** 3-4 hours
**Location:** `frontend/bcm-platform/src/lib/api/`

**Steps:**

1. Create API client structure
   ```
   src/lib/api/
   ├── client.ts          # Base axios client
   ├── transformers.ts    # snake_case ↔ camelCase
   ├── portal.ts          # Portal API
   ├── marketplace.ts     # Marketplace API
   ├── learning.ts        # Learning API (NEW)
   └── simulations.ts     # Simulations API (NEW)
   ```

2. Update base client (client.ts)
   ```typescript
   export const portalClient = axios.create({
     baseURL: process.env.NEXT_PUBLIC_PORTAL_URL || 'http://localhost:8031',
     timeout: 30000
   })

   export const marketplaceClient = axios.create({
     baseURL: process.env.NEXT_PUBLIC_MARKETPLACE_URL || 'http://localhost:8032',
     timeout: 30000
   })

   export const learningClient = axios.create({
     baseURL: process.env.NEXT_PUBLIC_LEARNING_URL || 'http://localhost:8033',
     timeout: 30000
   })
   ```

3. Create transformers.ts
   ```typescript
   // Transform response from snake_case to camelCase
   export const transformResponse = (data: any): any => {
     // Implementation
   }

   // Transform request from camelCase to snake_case
   export const transformRequest = (data: any): any => {
     // Implementation
   }
   ```

4. Add interceptors to all clients
   ```typescript
   portalClient.interceptors.response.use(
     (response) => {
       response.data = transformResponse(response.data)
       return response
     }
   )
   ```

5. Create API endpoints files

   **portal.ts:**
   ```typescript
   export const portalAPI = {
     // Knowledge
     getArticles: (params) => portalClient.get('/api/knowledge/articles', { params }),
     getArticle: (id) => portalClient.get(`/api/knowledge/articles/${id}`),

     // Forum
     getTopics: (params) => portalClient.get('/api/forum/topics', { params }),
     getTopic: (id) => portalClient.get(`/api/forum/topics/${id}`),

     // News
     getNews: (params) => portalClient.get('/api/news', { params }),

     // Events
     getEvents: (params) => portalClient.get('/api/events', { params }),
   }
   ```

   **simulations.ts:**
   ```typescript
   export const simulationsAPI = {
     // Simulations
     createSimulation: (data) => portalClient.post('/api/simulations/simulations', data),
     listSimulations: (params) => portalClient.get('/api/simulations/simulations', { params }),

     // Execution
     runSimulation: (id) => portalClient.post(`/api/simulations/simulations/${id}/run`),
     getStatus: (id) => portalClient.get(`/api/simulations/simulations/${id}/status`),

     // Library
     getScenarioLibrary: (params) => portalClient.get('/api/simulations/library', { params }),
     getScenario: (id) => portalClient.get(`/api/simulations/library/${id}`),
   }
   ```

   **learning.ts:**
   ```typescript
   export const learningAPI = {
     // Programs
     getPrograms: (params) => learningClient.get('/api/learning/programs', { params }),
     getProgram: (id) => learningClient.get(`/api/learning/programs/${id}`),

     // Enrollments
     enroll: (data) => learningClient.post('/api/learning/enrollments', data),
     getMyEnrollments: () => learningClient.get('/api/learning/enrollments'),

     // Gamification
     getLeaderboard: () => learningClient.get('/api/learning/leaderboard'),
     getMyAchievements: () => learningClient.get('/api/learning/achievements/me'),
   }
   ```

6. Test API calls
   ```bash
   # In browser console
   fetch('http://localhost:8031/api/knowledge/articles')
   ```

**Checklist:**
- [ ] API client files created
- [ ] Transformers implemented
- [ ] Interceptors added
- [ ] All endpoint functions created
- [ ] API calls working from browser

---

### Task 2.3: Update Existing Components ⚡ HIGH PRIORITY
**Time:** 2-3 hours
**Location:** `frontend/bcm-platform/src/components/`

**Steps:**

1. Update KnowledgeHub.tsx
   - Replace mock data with API calls
   - Use `portalAPI.getArticles()`
   - Add React Query hooks
   - Add loading states

2. Update CommunityForum.tsx
   - Use `portalAPI.getTopics()`
   - Add pagination
   - Add real-time updates (optional)

3. Update CaseStudies.tsx
   - Use `marketplaceAPI.getCaseStudies()`
   - Connect to portfolio API

4. Update ExpertDirectory.tsx
   - Use `marketplaceAPI.getSpecialists()`
   - Connect filters to API

5. Test all components
   ```bash
   npm run dev
   # Navigate to each page
   ```

**Checklist:**
- [ ] KnowledgeHub connected to API
- [ ] CommunityForum connected to API
- [ ] CaseStudies connected to API
- [ ] ExpertDirectory connected to API
- [ ] All components loading real data
- [ ] No console errors

---

### Task 2.4: Create Missing Components 🔶 MEDIUM PRIORITY
**Time:** 8-12 hours

**Priority Order:**

1. **News Component** (1-2 hours)
   - Location: `src/components/portal/News.tsx`
   - Features: List view, detail modal, filters
   - API: `portalAPI.getNews()`

2. **Events Component** (1-2 hours)
   - Location: `src/components/portal/Events.tsx`
   - Features: Calendar view, list view, registration
   - API: `portalAPI.getEvents()`

3. **Simulations Components** (4-6 hours)
   - SimulationWizard.tsx - Create simulation
   - SimulationList.tsx - My simulations
   - SimulationRunner.tsx - Run simulation (complex!)
   - ScenarioLibrary.tsx - Browse scenarios
   - API: `simulationsAPI.*`

4. **Learning Components** (4-6 hours)
   - ProgramCatalog.tsx - Browse courses
   - ProgramDetail.tsx - Course details
   - CoursePlayer.tsx - Watch lessons (complex!)
   - MyLearning.tsx - Dashboard
   - ProgressTracker.tsx - Progress widget
   - LeaderboardWidget.tsx - Gamification
   - API: `learningAPI.*`

5. **Dashboard Components** (2-3 hours)
   - DashboardOverview.tsx - Main dashboard
   - ProfileEditor.tsx - Edit profile
   - MessagesCenter.tsx - Chat (if time permits)

**Checklist:**
- [ ] News component created & tested
- [ ] Events component created & tested
- [ ] Simulations components created & tested
- [ ] Learning components created & tested
- [ ] Dashboard components created & tested

---

### Task 2.5: Routing & Navigation ⚡ HIGH PRIORITY
**Time:** 2-3 hours

**Steps:**

1. Update app routing structure
   ```
   src/app/
   ├── (public)/
   │   ├── page.tsx              # Homepage
   │   ├── knowledge/
   │   ├── community/
   │   ├── news/                 # NEW
   │   └── events/               # NEW
   │
   ├── (marketplace)/
   │   ├── specialists/
   │   └── projects/
   │
   ├── (learning)/               # NEW
   │   ├── programs/
   │   ├── my-learning/
   │   └── course/[id]/player/
   │
   ├── (simulations)/            # NEW
   │   ├── page.tsx
   │   ├── library/
   │   ├── my/
   │   └── run/[id]/
   │
   └── (dashboard)/
       ├── page.tsx
       ├── profile/
       └── messages/
   ```

2. Update global navigation
   - File: `src/components/layout/Navigation.tsx`
   - Add Learning, Simulations, News links

3. Create breadcrumbs component
   - File: `src/components/layout/Breadcrumbs.tsx`

4. Test navigation
   - All links working
   - No 404 errors

**Checklist:**
- [ ] All routes created
- [ ] Navigation updated
- [ ] Breadcrumbs implemented
- [ ] No broken links

---

## 📝 PHASE 3: Testing & Polish (Day 6)

### Task 3.1: Integration Testing 🔶 MEDIUM PRIORITY
**Time:** 2-3 hours

**Tests:**

1. User Flows Testing
   - Sign up → Enroll in course → Complete lesson
   - Browse specialists → Contact → Hire
   - Create simulation → Run → View results
   - Post forum topic → Reply → Upvote

2. Cross-service Testing
   - Knowledge article → Related course
   - Specialist portfolio → Case studies
   - Forum reputation → Learning XP

3. Error Handling
   - Network errors
   - Invalid inputs
   - Unauthorized access

**Checklist:**
- [ ] All user flows tested
- [ ] Cross-service integration working
- [ ] Error handling graceful
- [ ] No console errors

---

### Task 3.2: Performance Optimization 🔵 LOW PRIORITY
**Time:** 2-3 hours

**Optimizations:**

1. Code Splitting
   - Lazy load heavy components
   - Dynamic imports for routes

2. Image Optimization
   - Use Next.js Image component
   - Add blur placeholders
   - Lazy load images

3. API Caching
   - React Query cache configuration
   - Stale-while-revalidate

4. Bundle Size
   - Analyze with `npm run build`
   - Remove unused dependencies

**Checklist:**
- [ ] Code splitting implemented
- [ ] Images optimized
- [ ] Caching configured
- [ ] Bundle size < 500KB

---

### Task 3.3: Documentation 🔵 LOW PRIORITY
**Time:** 1-2 hours

**Docs to create:**

1. README.md for frontend
   - Setup instructions
   - Environment variables
   - Development workflow

2. API documentation
   - Endpoint descriptions
   - Request/response examples

3. Deployment guide
   - Build instructions
   - Environment setup
   - Docker configuration

**Checklist:**
- [ ] README.md created
- [ ] API docs complete
- [ ] Deployment guide written

---

## 📊 Time Estimates Summary

### Backend (Phase 1): 14-20 hours
- Learning Service: 4-6 hours
- Simulations Integration: 6-8 hours
- News/Events: 2-3 hours
- Testing: 2-3 hours

### Frontend (Phase 2): 19-27 hours
- Setup: 2-3 hours
- API Client: 3-4 hours
- Update Components: 2-3 hours
- New Components: 8-12 hours
- Routing: 2-3 hours
- Testing: 2-3 hours

### Polish (Phase 3): 5-8 hours
- Integration Testing: 2-3 hours
- Performance: 2-3 hours
- Documentation: 1-2 hours

### **TOTAL: 38-55 hours (5-7 working days)**

---

## 🎯 Success Criteria

### Backend Complete When:
- [ ] All 130 endpoints responding
- [ ] All database schemas created
- [ ] All services running (8031, 8032, 8033)
- [ ] Cross-service integration working
- [ ] API documentation updated

### Frontend Complete When:
- [ ] All pages accessible
- [ ] All components connected to API
- [ ] Real data loading (no mock data)
- [ ] User flows working end-to-end
- [ ] Mobile responsive
- [ ] No console errors

### Production Ready When:
- [ ] All tests passing
- [ ] Performance optimized
- [ ] Documentation complete
- [ ] Deployment scripts ready
- [ ] Monitoring configured

---

## 🚀 Quick Start Commands (After Context Restore)

### Backend
```bash
# Terminal 1: Portal (includes Simulations)
cd /Users/MD/AI-Platform-ISO/platform-services/community-service/portal
python3 -m uvicorn main:app --host 0.0.0.0 --port 8031 --reload

# Terminal 2: Marketplace
cd /Users/MD/AI-Platform-ISO/platform-services/community-service/marketplace
python3 -m uvicorn main:app --host 0.0.0.0 --port 8032 --reload

# Terminal 3: Learning (after migration)
cd /Users/MD/AI-Platform-ISO/platform-services/learning-service
python3 -m uvicorn main:app --host 0.0.0.0 --port 8033 --reload
```

### Frontend
```bash
cd /Users/MD/AI-Platform-ISO/frontend/bcm-platform
npm run dev
# Open http://localhost:3000
```

### Test Endpoints
```bash
# Portal
curl http://localhost:8031/health
curl http://localhost:8031/api/knowledge/articles

# Marketplace
curl http://localhost:8032/health
curl http://localhost:8032/api/specialists

# Learning
curl http://localhost:8033/health
curl http://localhost:8033/api/learning/programs

# Simulations (in Portal)
curl http://localhost:8031/api/simulations/library
```

---

## 📋 Context Restore Checklist

When resuming work, verify:

- [ ] All background services stopped
- [ ] Database connections working
- [ ] .env files configured
- [ ] Dependencies installed
- [ ] No port conflicts

Review documents:
- [ ] COMPLETE_ARCHITECTURE_DRAFT.md
- [ ] UI_ARCHITECTURE_BLUEPRINT.md
- [ ] INTELLIGENCE_SERVICE_ANALYSIS.md
- [ ] FRONTEND_ANALYSIS.md
- [ ] COMMUNITY_SERVICE_MIGRATION.md

---

## 🎯 Next Session Start Point

**Start with:** Task 1.1 - Migrate Learning Service

**Command:**
```bash
mkdir -p /Users/MD/AI-Platform-ISO/platform-services/learning-service
cp -r /Users/MD/ISO-22301—копия/services/SERVICES/BCM/learning/* \
      /Users/MD/AI-Platform-ISO/platform-services/learning-service/
```

---

**Plan Status:** ✅ READY TO EXECUTE
**Estimated Completion:** 5-7 days (1 person) or 3-4 days (2 people)
**First Task:** Learning Service Migration
**Priority:** Backend → Frontend → Polish

---

**Created:** 2025-10-02
**Last Updated:** 2025-10-02
**Version:** 1.0.0
