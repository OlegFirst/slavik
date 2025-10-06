# PROJECT MEMORY - AI-POWERED BCM PLATFORM

**For:** Quick context recovery for any team member (human or AI)
**Last Updated:** 2025-10-04

---

## QUICK START (5 MINUTE READ)

### What Is This Project?

AI-powered platform for ISO 22301 Business Continuity Management, specialized for healthcare.

**Unique Features:**
- Self-learning from successful workflows (Case Library)
- AI has managed autonomy (Rules + Checkpoints + Creative Zones)
- Workflow Intelligence Engine tracks every step
- Event-driven architecture

### Current Status

**Code Completion:** 65-70%
**Main Challenge:** Integration, not missing code

**What Works:**
- 10 BCM services (BIA, Risk, Planning, etc.) - fully coded
- Workflow Intelligence Engine - extracted and ready
- Infrastructure code - complete
- Database migrations - 024/033 applied

**What Needs Work:**
- Apply remaining 9 migrations
- Deploy Neo4j + RabbitMQ
- Create unified docker-compose
- Connect services together
- Build frontend

---

## PROJECT STRUCTURE

```
AI-Platform-ISO/
├── infrastructure/              # Foundation (DB, cache, EventBus)
├── platform-services/           # 10 BCM services (complete)
├── intelligent-core/            # AI and Workflow Intelligence
├── shared/                      # 51 reusable libraries
├── human-interface/             # API Gateway + Frontend (skeleton)
├── EXTRACTED_FROM_SESSION/      # Unique code from design sessions
└── ARCHITECTURE_FINAL_SPEC.md   # THE TRUTH (read this!)
```

---

## KEY DECISIONS MADE

### Architecture Decisions

**1. Cloud vs Local Infrastructure**
- Decision: Hybrid
- PostgreSQL: Supabase (cloud) - already deployed
- Redis: Upstash (cloud) - already deployed
- Neo4j: Local Docker (for dev), Cloud (for prod)
- RabbitMQ: Local Docker

**2. Orchestrators - Multiple Versions Issue**
- Decision: DON'T TOUCH YET
- Why: No final architecture for orchestration layer
- When: After infrastructure is deployed and we see real needs

**3. EventBus - Two Implementations**
- Decision: Use /infrastructure/event-bus/ (with RabbitMQ)
- Why: More production-ready, has fallback to Redis
- Action: Archive /infrastructure/eventbus/ (simpler version)

**4. Workflow Intelligence - Three Copies**
- Decision: Use /intelligent-core/workflow_intelligence/
- Action: Archive duplicates
- Note: Complete version extracted to /EXTRACTED_FROM_SESSION/

**5. Database Strategy**
- Decision: One Supabase instance with multiple schemas (for MVP)
- Future: 3 separate instances (System, Platform, Business)
- Current: Continue with existing setup

### Development Workflow Decisions

**1. No Timeline Estimates**
- Rule: Don't put "2-3 days", "Week 1", etc. in documents
- Why: Creates false expectations, distracts from real work
- Exception: Only if MD explicitly asks for estimate

**2. No Emojis in Code/Docs**
- Rule: No emojis in production code, technical docs, architecture specs
- Why: This is ISO 22301 platform, professional context
- Exception: Can use in chat/TODOs if helpful

**3. Agent vs Coordinator Roles**
- MD launches agents, not Claude
- Claude (coordinator) gives task specifications
- Claude reviews agent work
- Claude makes strategic decisions

**4. Work Sessions**
- Max 3-4 hours continuous work before break
- If stuck, ask MD immediately (don't waste time)
- At 10-15% tokens remaining, stop and document state

---

## WHAT NOT TO DO

### Code Anti-Patterns

**1. Don't Rewrite Existing Code**
- If code exists and works, use it as-is
- Only modify if integrating or fixing bugs
- Claude in terminal has history of rewriting code instead of using it

**2. Don't Create Duplicates**
- Before creating new file, search if it exists
- If similar exists, extend/modify, don't duplicate

**3. Don't Ignore Existing Architecture**
- Read ARCHITECTURE_FINAL_SPEC.md first
- Follow established patterns
- Propose changes if pattern is wrong, don't just ignore

### Process Anti-Patterns

**1. Don't Make All Decisions at Once**
- Architecture is complex, some decisions need infrastructure first
- Example: Orchestrator strategy - wait until we deploy and see needs

**2. Don't Over-Plan**
- Don't create 6-month roadmaps
- Focus on next concrete step
- Adjust based on reality, not plans

**3. Don't Work Alone**
- If stuck >30 min, ask MD
- If uncertain about decision, ask MD
- Better to ask than to waste hours

---

## COMMON MISTAKES & HOW TO AVOID

### Mistake 1: "I'll Just Rebuild This Better"

**Symptom:** Claude sees existing code, thinks "I can do better", rewrites from scratch.

**Problem:**
- Loses MD's 3 days of context
- Breaks integrations
- Wastes time

**Solution:**
- Read existing code first
- Understand why it was written that way
- If improvement needed, discuss with MD first

**Example:**
```
Bad:  "I'll create a new Workflow Engine from scratch"
Good: "The existing Workflow Engine at /intelligent-core/workflow_intelligence/
       has X and Y. Should we use it or is there a reason to replace?"
```

### Mistake 2: Long Sessions Without Checkpoints

**Symptom:** Claude works 48+ hours straight, context drifts, starts making errors.

**Problem:**
- Loses track of what was done
- Makes inconsistent decisions
- Hard to recover if something breaks

**Solution:**
- Every 3-4 hours: Update PROJECT_MEMORY.md
- Document what was done, what's next
- Fresh start with clear context is better than degraded long session

### Mistake 3: Ignoring Duplicates

**Symptom:** Multiple versions of same component in different folders.

**Problem:**
- Confusion about which version to use
- Wasted effort maintaining multiple versions
- Integration bugs

**Solution:**
- Before creating new component, search: `find . -name "*component_name*"`
- If duplicate exists, figure out which is correct
- Archive wrong version, use correct one

---

## RECOVERY PROCEDURES

### If Claude Restarts (Lost Context)

**Step 1:** Read these files in order (15 minutes)
1. PROJECT_MEMORY.md (this file) - Quick context
2. ARCHITECTURE_FINAL_SPEC.md - System understanding
3. AUDIT_REPORT_2025-10-03.md - Current state
4. Latest TODO list - What was being worked on

**Step 2:** Ask MD
- "I've read the context files. What was I working on last?"
- "Any blockers or issues I should know about?"

**Step 3:** Continue work
- Don't start from scratch
- Pick up where previous session left off
- Update PROJECT_MEMORY with new progress

### If MD Restarts (Forgot Context)

**Step 1:** Read
1. ARCHITECTURE_FINAL_SPEC.md - Remind of system design
2. Latest progress notes in PROJECT_MEMORY

**Step 2:** Quick status check
```bash
# Check what services are running
docker ps

# Check database migration status
psql $DATABASE_URL -c "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 5;"

# Check git status
git status
```

**Step 3:** Ask Claude
- "What did we complete yesterday?"
- "What's the current blocker?"
- "What's next on the plan?"

---

## CRITICAL PATHS

### Path 1: Infrastructure First (Current Priority)

```
1. Complete database migrations (025-033)
   ↓
2. Deploy Neo4j + RabbitMQ (docker-compose)
   ↓
3. Deploy EventBus service
   ↓
4. Verify all infrastructure health checks pass
```

**Why Critical:**
- All services depend on this
- Can't test services without infrastructure
- Blocked until this completes

### Path 2: First Working Service (After Infrastructure)

```
1. BIA Service connects to database
   ↓
2. BIA Service connects to EventBus
   ↓
3. Workflow Intelligence integrated
   ↓
4. Can create BIA via API
   ↓
5. Can get AI advice
```

**Why Critical:**
- Proves the architecture works
- Template for integrating other 9 services
- Demonstrates unique value (AI + Workflow Intelligence)

### Path 3: Full BCM Integration (After BIA Works)

```
1. Integrate remaining 9 services
   ↓
2. Enable event-driven flows (BIA → Risk → Planning)
   ↓
3. Deploy Neo4j with ISO 22301 data
   ↓
4. Case Library starts learning
```

---

## FILE LOCATIONS CHEAT SHEET

### Documentation
- Main architecture: `/ARCHITECTURE_FINAL_SPEC.md`
- This file: `/PROJECT_MEMORY.md`
- Current audit: `/AUDIT_REPORT_2025-10-03.md`
- Extracted code: `/EXTRACTED_FROM_SESSION/`

### Code
- BCM services: `/platform-services/*/`
- Workflow Intelligence: `/intelligent-core/workflow_intelligence/`
- EventBus: `/infrastructure/event-bus/`
- API Gateway: `/human-interface/api-gateway/`
- Shared libraries: `/shared/`

### Infrastructure
- Database migrations: `/infrastructure/database/migrations_source/`
- Database managers: `/infrastructure/database/managers/`
- Environment config: `/.env`

### Plans & Specs
- Infrastructure plan: `/ACTION_PLAN_INFRASTRUCTURE.md`
- Phase 1 status: `/PHASE_1_REAL_STATE.md`
- Extraction plan: `/EXTRACTION_PLAN.md`

---

## TEAM WORKING AGREEMENTS

### Communication

**When Claude (Coordinator) Speaks:**
- Direct, concise, technical
- No marketing speak or hype
- No unnecessary apologies or preamble
- Admit when stuck or uncertain

**When MD Speaks:**
- Provides context and priorities
- Makes final decisions
- Stops Claude if going wrong direction
- Launches agents for mechanical tasks

**When Agent Speaks:**
- Reports task completion
- Lists what was done
- Flags any errors or blockers
- Asks for next task

### Decision-Making

**Strategic Decisions (Claude makes):**
- Which component to use when duplicates exist
- How to structure code/modules
- Technical architecture patterns
- Integration approaches

**Business Decisions (MD makes):**
- Project priorities
- Resource allocation
- When to ship/deploy
- Feature inclusion/exclusion

**Tactical Decisions (Agents make):**
- None - agents follow instructions exactly
- If unclear, agent asks coordinator

---

## VERSION HISTORY

### 2025-10-04: Foundation Session
- Created ARCHITECTURE_FINAL_SPEC.md
- Extracted all code from SESSION_SUMMARY.md (9 modules, 3,441 lines)
- Created PROJECT_MEMORY.md (this file)
- Completed audit of project
- Identified: 65-70% code complete, integration is main task

**Key Decisions:**
- Use existing Supabase + Upstash (cloud)
- Deploy Neo4j + RabbitMQ (local docker)
- Don't touch orchestrators yet
- Use event-bus (with RabbitMQ)
- Complete migrations 025-033

**Next Session Goals:**
- Apply migrations 025-033
- Create docker-compose.infrastructure.yml
- Deploy and verify all infrastructure

---

## GLOSSARY

**BIA** - Business Impact Analysis (ISO 22301 Clause 8.2.2)
**BCM** - Business Continuity Management
**RLS** - Row Level Security (PostgreSQL tenant isolation)
**RTO** - Recovery Time Objective (how fast to recover)
**RPO** - Recovery Point Objective (how much data loss acceptable)
**MTPD** - Maximum Tolerable Period of Disruption
**PDCA** - Plan-Do-Check-Act (ISO management cycle)
**MCP** - Model Context Protocol (Claude integration)
**Workflow Intelligence** - Core system tracking workflow state + AI context
**Case Library** - Self-learning database of successful workflows
**Managed Autonomy** - AI freedom within governance boundaries

---

## EMERGENCY CONTACTS

**When Things Go Wrong:**

**Database Issues:**
- Check: /.env for DATABASE_URL
- Verify: Can connect with `psql $DATABASE_URL`
- Rollback: Migrations have DOWN scripts if needed

**Service Won't Start:**
- Check: logs in service directory
- Verify: Dependencies (DB, Redis) are up
- Check: Port not already in use

**Lost Context:**
- Read: This file (PROJECT_MEMORY.md)
- Read: ARCHITECTURE_FINAL_SPEC.md
- Ask: MD for current status

**Unsure What To Do:**
- Stop and ask MD
- Don't waste time guessing
- Better to ask than to go wrong direction

---

**Remember:** This is a marathon, not a sprint. Steady, thoughtful progress beats rushed chaos.

---

**End of Memory Document**
