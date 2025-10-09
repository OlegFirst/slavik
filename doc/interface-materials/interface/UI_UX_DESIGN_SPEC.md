# 🎨 UI/UX Design Specification - 7 User Journeys

**Project**: AI-Platform-ISO Multi-Journey Platform
**Date**: 2025-10-09
**Status**: Design Phase
**Version**: 1.0

---

## 📐 DESIGN PRINCIPLES

### Core Principles
1. **Journey-First Navigation** - Users think in terms of "what I want to achieve" not "what module to open"
2. **Progressive Disclosure** - Show simple first, reveal complexity on demand
3. **Context Persistence** - Remember user's journey, progress, preferences
4. **AI as Copilot** - AI assistant always available, proactive suggestions
5. **Mobile-First** - Fully responsive, works on phone/tablet/desktop

### Visual Design System
- **Color Palette**:
  - Primary: Blue (#2563EB) - Trust, professionalism
  - Certification: Green (#10B981) - Growth, success
  - Auditor: Purple (#8B5CF6) - Authority, expertise
  - Academy: Orange (#F59E0B) - Learning, energy
  - Twin: Teal (#14B8A6) - Technology, innovation
  - Crisis: Red (#EF4444) - Urgency, attention
- **Typography**:
  - Headings: Inter Bold
  - Body: Inter Regular
  - Code/Data: JetBrains Mono
- **Spacing**: 4px grid system
- **Shadows**: Layered shadows for depth
- **Animations**: Smooth 200-300ms transitions

---

## 🎯 JOURNEY 1: CERTIFICATION PATH

### Overview
**Goal**: Guide organization from "no certification" to "audit-ready" in 12-48 weeks
**User Personas**: BCM Manager, Org Admin, Compliance Officer
**Success Metric**: 80%+ readiness score, ready for auditor

---

### SCREEN 1: Gap Analysis Wizard

**URL**: `/certification/gap-analysis`

#### Layout
```
┌─────────────────────────────────────────────────────┐
│  [← Back]     ISO 22301 Gap Analysis      [Help 🤖] │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Progress: ████████░░░░░░ 8/10 Clauses Complete    │
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  📋 Clause 5: Leadership                       ││
│  │                                                 ││
│  │  5.1 Leadership and commitment                 ││
│  │  ───────────────────────────────────────────  ││
│  │                                                 ││
│  │  ❓ Has top management demonstrated           ││
│  │     commitment to BCM by:                      ││
│  │                                                 ││
│  │  ☐ Establishing BCM policy                     ││
│  │  ☐ Assigning BCM roles                         ││
│  │  ☐ Providing resources                         ││
│  │  ☐ Ensuring awareness                          ││
│  │                                                 ││
│  │  Your Answer:                                   ││
│  │  ○ Yes - Full compliance                       ││
│  │  ● Partial - Some evidence                     ││
│  │  ○ No - Not implemented                        ││
│  │                                                 ││
│  │  📝 Evidence/Details:                          ││
│  │  ┌──────────────────────────────────────────┐ ││
│  │  │ We have a draft BCM policy approved by   │ ││
│  │  │ CEO, but roles not formally assigned...  │ ││
│  │  │                                           │ ││
│  │  └──────────────────────────────────────────┘ ││
│  │                                                 ││
│  │  📎 Upload Documents (optional)                ││
│  │  [+] Add Policy, Org Chart, or Evidence       ││
│  │                                                 ││
│  │  🤖 AI Suggestion:                             ││
│  │  Based on your answer, you'll need to:        ││
│  │  1. Formalize role assignments                ││
│  │  2. Document resource allocation              ││
│  │  3. Create awareness program                  ││
│  │                                                 ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│              [← Previous]    [Next: 5.2 →]          │
│                                                      │
└─────────────────────────────────────────────────────┘
```

#### Components
- **Progress Bar**: Shows clause completion (color-coded by gap severity)
- **Clause Header**: Expandable accordion for all sub-clauses
- **Question Card**: Each requirement as a card with:
  - Question text
  - Multiple choice (Yes/Partial/No)
  - Evidence text area
  - Document upload
  - AI suggestion box (appears after answer)
- **Navigation**: Previous/Next buttons, Save draft
- **AI Help Button**: Floating button (top-right) for contextual help

#### Interactions
1. User answers questions → AI analyzes → Shows immediate feedback
2. Upload documents → AI extracts key info → Pre-fills evidence
3. Progress auto-saved every 30 seconds
4. Can skip clauses, come back later
5. On last clause → "Generate Gap Report" button appears

---

### SCREEN 2: Gap Analysis Report

**URL**: `/certification/gap-analysis/:id/report`

#### Layout
```
┌─────────────────────────────────────────────────────┐
│  Gap Analysis Report - ISO 22301                     │
│  Organization: Acme Corp | Generated: Oct 9, 2025   │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │       Overall Compliance Score                  ││
│  │                                                 ││
│  │             ╭────╮                              ││
│  │            │  58% │  👍 Good start!             ││
│  │             ╰────╯                              ││
│  │                                                 ││
│  │  ▰▰▰▰▰▰▰▰▰▰░░░░░░░░░░  58/100                  ││
│  │                                                 ││
│  │  🔴 Critical Gaps: 3                            ││
│  │  🟡 Major Gaps: 8                               ││
│  │  🟢 Minor Gaps: 5                               ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  📊 Compliance by Clause                        ││
│  │                                                 ││
│  │  4. Context          ████░░░░░░  65%            ││
│  │  5. Leadership       ███░░░░░░░  50% 🔴         ││
│  │  6. Planning         █████░░░░░  75%            ││
│  │  7. Support          ██░░░░░░░░  40% 🔴         ││
│  │  8. Operation        ████░░░░░░  60%            ││
│  │  9. Performance      ███░░░░░░░  45% 🔴         ││
│  │  10. Improvement     ████░░░░░░  65%            ││
│  │                                                 ││
│  │  [View Detailed Breakdown]                      ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  🔴 Critical Gaps (Must Fix First)              ││
│  │                                                 ││
│  │  1. Clause 5.2 - No BCM Coordinator assigned   ││
│  │     Impact: Can't proceed without ownership    ││
│  │     Recommendation: Assign full-time BCM lead  ││
│  │     Est. Time: 1 week | Cost: $5,000           ││
│  │     [View Details] [Add to Roadmap]            ││
│  │                                                 ││
│  │  2. Clause 7.2 - No training program           ││
│  │     Impact: Staff unaware of BCM procedures    ││
│  │     Recommendation: Create e-learning modules  ││
│  │     Est. Time: 4 weeks | Cost: $15,000         ││
│  │     [View Details] [Add to Roadmap]            ││
│  │                                                 ││
│  │  ... (1 more critical gap)                      ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  🤖 AI Recommendations                          ││
│  │                                                 ││
│  │  Based on your profile (Medium business,       ││
│  │  Healthcare industry), we recommend:            ││
│  │                                                 ││
│  │  • Timeline: 24 weeks to audit-ready           ││
│  │  • Budget: $45,000 - $65,000                    ││
│  │  • Priority: Fix leadership & training first   ││
│  │  • Similar orgs averaged 26 weeks              ││
│  │                                                 ││
│  │  [Generate Personalized Roadmap →]             ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  Actions:                                            │
│  [📄 Export PDF] [📊 Export Excel]                  │
│  [🗓️ Generate Roadmap] [👨‍⚖️ Find Auditor]          │
│                                                      │
└─────────────────────────────────────────────────────┘
```

#### Components
- **Score Card**: Large circular progress (58%) with emoji
- **Clause Bar Chart**: Horizontal bars, color-coded by severity
- **Gap Cards**: Expandable cards for each gap with:
  - Severity badge
  - Impact statement
  - AI recommendation
  - Time/cost estimates
  - Action buttons
- **AI Summary**: Executive summary in natural language
- **Action Bar**: Primary CTAs (Export, Roadmap, Find Auditor)

#### Interactions
1. Click clause bar → Expands detailed breakdown
2. Click gap card → Shows full analysis + supporting evidence
3. "Add to Roadmap" → Marks gap for inclusion in roadmap
4. "Generate Roadmap" → Navigates to roadmap builder
5. "Find Auditor" → Pre-fills marketplace search with requirements

---

### SCREEN 3: Certification Roadmap

**URL**: `/certification/roadmap/:id`

#### Layout
```
┌─────────────────────────────────────────────────────┐
│  Certification Roadmap - 24 Weeks to Audit-Ready    │
│  [Edit Timeline] [Assign Tasks] [Export]     [🤖]   │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Progress: ████░░░░░░░░░░░░ Week 8/24 (33%)        │
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  📊 Quick Stats                                 ││
│  │                                                 ││
│  │  Current Score: 58% → Target: 85%              ││
│  │  Budget Used: $12K / $55K                       ││
│  │  Team: 5 people assigned                       ││
│  │  Next Milestone: BIA Completion (Week 12)      ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  📅 Timeline View                                    │
│  [Gantt] [Calendar] [List]  ← View Switchers       │
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  Phase 1: Foundation (Weeks 1-6) ✅ COMPLETE   ││
│  │  ─────────────────────────────────────────────  ││
│  │                                                 ││
│  │  ✅ 1.1 Assign BCM Coordinator (Week 1)        ││
│  │     Owner: Sarah Johnson | Status: Done        ││
│  │     Deliverable: Job description, hire letter  ││
│  │                                                 ││
│  │  ✅ 1.2 Establish BCM Policy (Weeks 2-3)       ││
│  │     Owner: John Smith | Status: Done           ││
│  │     Deliverable: Approved policy document      ││
│  │                                                 ││
│  │  ✅ 1.3 Management Review Meeting (Week 4)     ││
│  │     Owner: CEO | Status: Done                  ││
│  │     Deliverable: Meeting minutes + approval    ││
│  │                                                 ││
│  │  ... (3 more tasks in Phase 1)                  ││
│  │                                                 ││
│  │  [View Phase Details]                           ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  Phase 2: BIA & Risk (Weeks 7-14) 🔵 ACTIVE    ││
│  │  ─────────────────────────────────────────────  ││
│  │                                                 ││
│  │  🔵 2.1 Conduct BIA Interviews (Weeks 7-10)    ││
│  │     Owner: BCM Team | Status: In Progress      ││
│  │     Progress: ████░░░░░░ 6/15 departments      ││
│  │                                                 ││
│  │     📋 Subtasks:                                ││
│  │     ✅ IT Department                            ││
│  │     ✅ Finance                                  ││
│  │     ✅ Operations                               ││
│  │     ✅ Sales                                    ││
│  │     ✅ HR                                       ││
│  │     ✅ Customer Support                         ││
│  │     ⏳ Legal (In Progress)                      ││
│  │     ⏳ Marketing (In Progress)                  ││
│  │     ⬜ Logistics                                ││
│  │     ⬜ R&D                                      ││
│  │     ... (5 more)                                ││
│  │                                                 ││
│  │     🚨 Alert: Legal dept overdue by 2 days     ││
│  │     [Send Reminder] [Reassign]                 ││
│  │                                                 ││
│  │  ⏳ 2.2 Analyze BIA Results (Weeks 11-12)      ││
│  │     Owner: BCM Coordinator | Status: Pending   ││
│  │     Dependencies: Complete BIA interviews      ││
│  │                                                 ││
│  │  ⏳ 2.3 Risk Assessment Workshop (Week 13)     ││
│  │     Owner: Risk Manager | Status: Scheduled    ││
│  │     Date: Nov 15, 2025 | Location: Office      ││
│  │                                                 ││
│  │  [View Phase Details]                           ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  Phase 3: Plans & Procedures (Weeks 15-18)     ││
│  │  ⏳ UPCOMING                                    ││
│  │  [Preview Tasks]                                ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  🤖 AI Insights                                 ││
│  │                                                 ││
│  │  ⚠️ You're 2 days behind schedule              ││
│  │  Recommendation: Reallocate 1 person to BIA    ││
│  │  to catch up                                    ││
│  │                                                 ││
│  │  💡 Tip: Similar orgs finished BIA in 8 weeks  ││
│  │  by using our AI Interview Assistant           ││
│  │  [Try AI Assistant]                             ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  [← Back to Report] [Export to MS Project]          │
│                                                      │
└─────────────────────────────────────────────────────┘
```

#### Components
- **Progress Bar**: Overall roadmap progress
- **Stats Dashboard**: 4 key metrics (score, budget, team, milestone)
- **View Switcher**: Gantt chart / Calendar / List view
- **Phase Accordion**: Collapsible phases with:
  - Phase status badge
  - Task list with checkboxes
  - Owner avatars
  - Progress bars for multi-step tasks
  - Alerts for overdue items
- **Task Details**: Click task → Side panel with:
  - Full description
  - Subtasks checklist
  - Comments/notes
  - File attachments
  - Timeline
- **AI Insights Card**: Proactive suggestions based on progress

#### Interactions
1. Check task → Marks complete → Progress updates
2. Click task → Opens detail panel
3. Drag-drop tasks → Reorder priority
4. Assign owner → Dropdown of team members
5. Add comment → Notification to owner
6. Alert click → Shows recommended action
7. Export → Generates MS Project / Excel file

---

### SCREEN 4: AI Document Generator

**URL**: `/certification/documents/generate`

#### Layout
```
┌─────────────────────────────────────────────────────┐
│  🤖 AI Document Generator                            │
│  [Templates] [My Documents] [Help]                   │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Step 1 of 3: Choose Template                        │
│  ───────────────────────────────────────────────────│
│                                                      │
│  Filter: [All Categories ▾] [All Clauses ▾]         │
│  Search: [Search templates...]                       │
│                                                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐│
│  │ 📄 BCM Policy│ │ 📋 BIA Report│ │ 📑 BC Plans  ││
│  │              │ │              │ │              ││
│  │ Clause: 5.3  │ │ Clause: 8.2  │ │ Clause: 8.4  ││
│  │ Time: 30 min │ │ Time: 2 hrs  │ │ Time: 4 hrs  ││
│  │              │ │              │ │              ││
│  │ 🤖 AI: Yes   │ │ 🤖 AI: Yes   │ │ 🤖 AI: Yes   ││
│  │              │ │              │ │              ││
│  │ [Generate →] │ │ [Generate →] │ │ [Generate →] ││
│  └──────────────┘ └──────────────┘ └──────────────┘│
│                                                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐│
│  │ 🔄 Risk      │ │ 📊 Exercise  │ │ 📖 Training  ││
│  │  Register    │ │  Scenario    │ │  Program     ││
│  │              │ │              │ │              ││
│  │ Clause: 6.1  │ │ Clause: 8.5  │ │ Clause: 7.2  ││
│  │ Time: 1 hr   │ │ Time: 1 hr   │ │ Time: 3 hrs  ││
│  │              │ │              │ │              ││
│  │ 🤖 AI: Yes   │ │ 🤖 AI: Yes   │ │ 🤖 AI: Yes   ││
│  │              │ │              │ │              ││
│  │ [Generate →] │ │ [Generate →] │ │ [Generate →] ││
│  └──────────────┘ └──────────────┘ └──────────────┘│
│                                                      │
│  ... (12 more templates)                             │
│                                                      │
└─────────────────────────────────────────────────────┘

After clicking "Generate" on BCM Policy:

┌─────────────────────────────────────────────────────┐
│  🤖 AI Document Generator - BCM Policy               │
│  [← Back to Templates]                               │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Step 2 of 3: AI Interview                           │
│  ───────────────────────────────────────────────────│
│                                                      │
│  I'll ask you 8 questions to personalize your BCM   │
│  Policy. This will take about 10 minutes.           │
│                                                      │
│  Progress: ████████░░░░░░ Question 5/8              │
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  🤖 AI Assistant                                ││
│  │                                                 ││
│  │  Question 5: What are your organization's      ││
│  │  critical business functions?                   ││
│  │                                                 ││
│  │  This helps me define the scope of your BCM    ││
│  │  program in the policy.                         ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  Your Answer:                                        │
│  ┌────────────────────────────────────────────────┐│
│  │ Our critical functions are:                     ││
│  │ 1. Customer support (24/7 operations)          ││
│  │ 2. Payment processing                           ││
│  │ 3. Order fulfillment                            ││
│  │ 4. IT infrastructure                            ││
│  │ 5. Data backup systems                          ││
│  │                                                 ││
│  │ [Voice Input 🎤] [Paste from BIA]              ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  💡 Suggestion: I noticed you completed a BIA.      │
│  Would you like me to import those results?         │
│  [Yes, Import] [No, Continue]                       │
│                                                      │
│              [← Previous]    [Next Question →]      │
│                                                      │
└─────────────────────────────────────────────────────┘

After answering all questions:

┌─────────────────────────────────────────────────────┐
│  🤖 AI Document Generator - BCM Policy               │
│  [← Back to Interview]                               │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Step 3 of 3: Review & Edit                          │
│  ───────────────────────────────────────────────────│
│                                                      │
│  ┌─────────────┬──────────────────────────────────┐│
│  │ Table of    │  BUSINESS CONTINUITY MANAGEMENT  ││
│  │ Contents    │  POLICY                           ││
│  │             │  Acme Corporation                ││
│  │ 1. Purpose  │  Version 1.0 | October 9, 2025   ││
│  │ 2. Scope    │  ───────────────────────────────  ││
│  │ 3. Policy   │                                   ││
│  │ 4. Roles    │  1. PURPOSE                       ││
│  │ 5. Review   │                                   ││
│  │             │  This Business Continuity         ││
│  │ [Export PDF]│  Management (BCM) Policy defines  ││
│  │ [Edit Doc]  │  Acme Corporation's commitment to ││
│  │ [Approve]   │  maintaining critical operations  ││
│  │             │  during disruptions and ensuring  ││
│  │             │  rapid recovery to normal         ││
│  │             │  operations.                      ││
│  │             │                                   ││
│  │             │  The policy establishes the       ││
│  │             │  framework for our BCM program in ││
│  │             │  accordance with ISO 22301:2019.  ││
│  │             │                                   ││
│  │             │  2. SCOPE                         ││
│  │             │                                   ││
│  │             │  This policy applies to all Acme  ││
│  │             │  Corporation employees, critical  ││
│  │             │  business functions, and third-   ││
│  │             │  party suppliers supporting:      ││
│  │             │                                   ││
│  │             │  • Customer support operations    ││
│  │             │    (24/7 service desk)            ││
│  │             │  • Payment processing systems     ││
│  │             │  • Order fulfillment operations   ││
│  │             │  • IT infrastructure and data     ││
│  │             │    centers                        ││
│  │             │  • Backup and recovery systems    ││
│  │             │                                   ││
│  │             │  ... (10 more sections)           ││
│  │             │                                   ││
│  │             │  📝 Editable inline - click to   ││
│  │             │  modify any section               ││
│  │             │                                   ││
│  │             │  🤖 AI Review:                    ││
│  │             │  ✅ Compliant with ISO 22301     ││
│  │             │  ✅ All required clauses covered  ││
│  │             │  ⚠️ Consider adding: Board        ││
│  │             │     approval signature section    ││
│  │             │                                   ││
│  └─────────────┴──────────────────────────────────┘│
│                                                      │
│  Actions:                                            │
│  [💾 Save Draft] [📤 Export PDF] [✅ Submit for     │
│  Approval] [🔄 Regenerate Section]                  │
│                                                      │
└─────────────────────────────────────────────────────┘
```

#### Components
- **Template Grid**: Cards with:
  - Icon
  - Name
  - ISO clause
  - Estimated time
  - AI availability badge
  - Generate button
- **AI Interview**:
  - Question card with context
  - Answer text area
  - Voice input option
  - Import from other modules (BIA, Risk)
  - Progress indicator
- **Document Editor**:
  - 2-column layout (TOC + Content)
  - Inline editing (click paragraph to edit)
  - AI review panel
  - Version control
  - Comments/suggestions
- **Action Bar**: Save, Export, Approve, Regenerate

#### Interactions
1. Click template → Starts AI interview
2. Answer questions → AI generates draft
3. Review → Click section to edit
4. AI suggestions → Accept/reject with one click
5. Export PDF → Downloads formatted document
6. Submit approval → Sends to designated approver
7. Regenerate section → AI rewrites based on new input

---

### SCREEN 5: Readiness Tracker Dashboard

**URL**: `/certification/readiness`

#### Layout
```
┌─────────────────────────────────────────────────────┐
│  Certification Readiness Dashboard                   │
│  Last Updated: 5 minutes ago | [Refresh] [Help 🤖]  │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │         Overall Readiness Score                 ││
│  │                                                 ││
│  │              ╭───────╮                          ││
│  │             │   78%  │  🎯 Almost there!        ││
│  │              ╰───────╯                          ││
│  │                                                 ││
│  │  Need 85% to request certification audit       ││
│  │                                                 ││
│  │  Estimated time to 85%: 6 weeks                ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  📊 Readiness by Section                        ││
│  │                                                 ││
│  │  📄 Documentation (40% weight)                  ││
│  │  ▰▰▰▰▰▰▰▰▰▰▰▰▰░░░░░░░░  92%  ✅ Excellent      ││
│  │                                                 ││
│  │  ├─ BCM Policy                       ✅ 100%    ││
│  │  ├─ BIA Report                       ✅ 100%    ││
│  │  ├─ Risk Register                    ✅ 100%    ││
│  │  ├─ BC Plans                         ⚠️  80%    ││
│  │  ├─ Procedures                       ⚠️  85%    ││
│  │  └─ Templates                        ✅  95%    ││
│  │                                                 ││
│  │  [View Details]                                 ││
│  │                                                 ││
│  │  ⚙️ Processes & Procedures (25% weight)        ││
│  │  ▰▰▰▰▰▰▰▰░░░░░░░░░░░░  75%  ⚠️ Needs work     ││
│  │                                                 ││
│  │  ├─ BIA Process                      ✅  95%    ││
│  │  ├─ Risk Assessment                  ✅  90%    ││
│  │  ├─ Incident Response                ⚠️  65%    ││
│  │  ├─ Plan Maintenance                 ⚠️  70%    ││
│  │  └─ Testing & Exercises              ❌  45%    ││
│  │                                                 ││
│  │  🚨 3 Missing Items:                            ││
│  │  • Exercise schedule not defined                ││
│  │  • Incident escalation matrix incomplete       ││
│  │  • Plan review cycle not documented            ││
│  │                                                 ││
│  │  [Fix Now]                                      ││
│  │                                                 ││
│  │  🎓 Training & Awareness (15% weight)          ││
│  │  ▰▰▰▰▰▰░░░░░░░░░░░░░░  55%  ❌ Critical gap   ││
│  │                                                 ││
│  │  ├─ BCM Team Training                ⚠️  70%    ││
│  │  ├─ General Staff Awareness          ❌  35%    ││
│  │  ├─ Crisis Team Drills               ❌  40%    ││
│  │  └─ Training Records                 ✅  85%    ││
│  │                                                 ││
│  │  🚨 Current: 42/120 staff trained (35%)        ││
│  │  🎯 Target: 108/120 staff (90%)                ││
│  │  Gap: 66 people need training                  ││
│  │                                                 ││
│  │  🤖 Recommendation: Use our e-learning         ││
│  │  platform to train 66 staff in 4 weeks         ││
│  │  [Launch Training Campaign]                     ││
│  │                                                 ││
│  │  🧪 Exercises & Testing (10% weight)           ││
│  │  ▰▰▰▰░░░░░░░░░░░░░░░░  48%  ❌ Critical gap   ││
│  │                                                 ││
│  │  ├─ Tabletop Exercises               ✅  85%    ││
│  │  ├─ Plan Walkthroughs                ⚠️  60%    ││
│  │  ├─ Full-Scale Tests                 ❌  20%    ││
│  │  └─ Exercise Reports                 ⚠️  65%    ││
│  │                                                 ││
│  │  🚨 ISO requires: Annual full-scale test       ││
│  │  Last test: Never                               ││
│  │  Next scheduled: Not scheduled                 ││
│  │                                                 ││
│  │  🤖 Recommendation: Schedule test for Week 18  ││
│  │  of your roadmap                                ││
│  │  [Schedule Exercise]                            ││
│  │                                                 ││
│  │  📋 Reviews & Audits (10% weight)              ││
│  │  ▰▰▰▰▰▰▰▰▰░░░░░░░░░░  80%  ⚠️ Good progress   ││
│  │                                                 ││
│  │  ├─ Management Reviews               ✅  90%    ││
│  │  ├─ Internal Audits                  ⚠️  75%    ││
│  │  ├─ Plan Reviews                     ⚠️  70%    ││
│  │  └─ External Assessment              ❌  0%     ││
│  │                                                 ││
│  │  🚨 No internal audit in last 6 months         ││
│  │  🎯 ISO requires: Annual internal audit        ││
│  │                                                 ││
│  │  [Schedule Internal Audit]                      ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  🚨 Alerts & Action Items                       ││
│  │                                                 ││
│  │  🔴 Critical (3)                                ││
│  │  • No full-scale exercise conducted             ││
│  │  • Staff training below 50%                     ││
│  │  • Overdue internal audit                       ││
│  │                                                 ││
│  │  🟡 Warning (5)                                 ││
│  │  • BC Plans need update                         ││
│  │  • Exercise schedule missing                    ││
│  │  • Incident procedures incomplete               ││
│  │  • Plan maintenance process undefined          ││
│  │  • Crisis team not fully trained                ││
│  │                                                 ││
│  │  [View All Alerts]                              ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  🎯 Your Path to 85% (Next 6 weeks)            ││
│  │                                                 ││
│  │  Week 1-2: Train 66 staff (35% → 90%)          ││
│  │  Expected impact: +8 points                     ││
│  │                                                 ││
│  │  Week 3: Complete BC Plans (80% → 100%)        ││
│  │  Expected impact: +2 points                     ││
│  │                                                 ││
│  │  Week 4-5: Schedule & conduct exercise         ││
│  │  Expected impact: +4 points                     ││
│  │                                                 ││
│  │  Week 6: Internal audit                         ││
│  │  Expected impact: +2 points                     ││
│  │                                                 ││
│  │  Total impact: 78% → 94% 🎉                     ││
│  │                                                 ││
│  │  [Add to Roadmap] [Auto-Schedule]              ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  When score >= 85%:                                  │
│  ┌────────────────────────────────────────────────┐│
│  │  🎉 Congratulations! You're audit-ready!        ││
│  │                                                 ││
│  │  Your organization has achieved 85%+ readiness. ││
│  │  Time to find a certified auditor!              ││
│  │                                                 ││
│  │  [Find Auditor on Marketplace →]                ││
│  └────────────────────────────────────────────────┘│
│                                                      │
└─────────────────────────────────────────────────────┘
```

#### Components
- **Overall Score**: Large circular progress with status
- **Section Breakdown**: Accordion for each section with:
  - Weight percentage
  - Progress bar
  - Sub-item checklist
  - Missing items list
  - AI recommendations
  - Action buttons
- **Alert Cards**: Color-coded severity (Red/Yellow/Green)
- **Path to Target**: Step-by-step plan with impact estimates
- **Celebration Banner**: Appears when score >= 85%

#### Interactions
1. Click section → Expands details
2. Click sub-item → Shows specific requirements
3. "Fix Now" → Navigates to relevant tool (e.g., training platform)
4. "Schedule Exercise" → Opens exercise planning wizard
5. "Add to Roadmap" → Adds tasks to certification roadmap
6. "Find Auditor" → Navigates to marketplace with filters pre-filled
7. Real-time updates as user completes tasks

---

## 📊 MEASUREMENT & ANALYTICS

### Journey 1 Success Metrics
1. **Completion Rate**:
   - % of users who complete gap analysis
   - % who generate roadmap
   - % who reach 85% readiness
   - % who find auditor

2. **Time Metrics**:
   - Time to complete gap analysis (target: <2 hours)
   - Time from start to audit-ready (target: 12-24 weeks)
   - Time to first document generated (target: <30 min)

3. **Engagement Metrics**:
   - Daily active users in certification journey
   - Documents generated per user
   - AI assistant usage rate
   - Roadmap task completion rate

4. **Business Metrics**:
   - Conversion: Free → Paid subscription
   - Marketplace bookings from certification users
   - Average certification cost savings vs manual
   - NPS score for certification journey

---

## 🎨 COMPONENT LIBRARY

### Reusable Components for Journey 1

1. **ProgressBar**: Shows completion/readiness scores
2. **ScoreCard**: Large circular progress with status
3. **PhaseAccordion**: Expandable phase/task lists
4. **GapCard**: Display gap with severity and recommendations
5. **AIChat**: AI assistant sidebar
6. **DocumentEditor**: Inline editing with TOC
7. **AlertBanner**: Critical/warning notifications
8. **TaskChecklist**: Interactive checklist with progress
9. **MetricsDashboard**: 4-metric overview grid
10. **AuditTrail**: Timeline of changes/approvals

---

---

## 🚨 JOURNEY 6: CRISIS RECOVERY PLANNER (NEW!)

### Overview
**Goal**: Upload crisis scenario → AI generates recovery plan with timeline, budget, tasks
**User Personas**: CEO, Crisis Manager, BCM Coordinator (in active incident)
**Success Metric**: Plan generated in <5 minutes, 75%+ plans successfully execute

---

### SCREEN: Crisis Data Upload & Recovery Planning

**URL**: `/crisis/recovery-planner`

#### Layout
```
┌─────────────────────────────────────────────────────┐
│  🚨 Crisis Recovery Planner                          │
│  Upload your situation → AI generates recovery plan  │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Step 1 of 4: Describe Your Crisis                   │
│  ───────────────────────────────────────────────────│
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  What happened? (Tell AI about your crisis)     ││
│  │                                                 ││
│  │  ┌──────────────────────────────────────────┐ ││
│  │  │ Our primary data center in Virginia had  │ ││
│  │  │ a catastrophic fire on Oct 8, 2025 at    │ ││
│  │  │ 2:30 AM. The entire facility is offline. │ ││
│  │  │                                           │ ││
│  │  │ Impact:                                   │ ││
│  │  │ - All customer-facing systems down       │ ││
│  │  │ - 500,000 active users cannot access     │ ││
│  │  │ - Payment processing offline             │ ││
│  │  │ - Customer support systems unavailable   │ ││
│  │  │ - Last backup: 6 hours ago               │ ││
│  │  │                                           │ ││
│  │  │ Current situation (48 hours after):      │ ││
│  │  │ - DR site activated but only 40% capacity│ ││
│  │  │ - Revenue loss: $2M/day                  │ ││
│  │  │ - 150 support tickets/hour incoming      │ ││
│  │  │ - Media coverage: negative               │ ││
│  │  │                                           │ ││
│  │  │ [Voice Input 🎤] [Paste from Report]     │ ││
│  │  └──────────────────────────────────────────┘ ││
│  │                                                 ││
│  │  🤖 AI detected:                                ││
│  │  • Incident type: IT Infrastructure Failure     ││
│  │  • Severity: Catastrophic                       ││
│  │  • Status: Partial recovery in progress         ││
│  │  • Critical timeline: <24 hours to full restore ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  📊 Upload Supporting Data (optional but        ││
│  │  helps AI generate better plan)                 ││
│  │                                                 ││
│  │  Organization Profile:                          ││
│  │  [📤 Upload] or [Import from Digital Twin]     ││
│  │  ✅ Digital Twin imported: Acme Corp            ││
│  │     - 1,200 employees                           ││
│  │     - $120M annual revenue                      ││
│  │     - 85 critical business functions            ││
│  │     - 23 IT systems                             ││
│  │                                                 ││
│  │  Current Resource Availability:                 ││
│  │  [📤 Upload] or [AI will estimate]             ││
│  │  ✅ Uploaded: resource_status.xlsx             ││
│  │     - IT team: 12/15 available                  ││
│  │     - Crisis budget: $500K approved             ││
│  │     - DR site: 40% capacity, can scale to 100% ││
│  │     - Cloud burst capacity: Ready               ││
│  │                                                 ││
│  │  Incident Timeline:                             ││
│  │  [📤 Upload] or [Paste events]                 ││
│  │  ✅ Timeline imported from incident report      ││
│  │                                                 ││
│  │  Stakeholder Requirements:                      ││
│  │  [📤 Upload] or [Skip - AI will suggest]       ││
│  │  ✅ Uploaded: stakeholder_expectations.pdf     ││
│  │     - Board: Want full restore in 72 hours     ││
│  │     - Customers: Expect compensation            ││
│  │     - Regulators: Report due in 5 days         ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│              [← Cancel]    [Generate Recovery Plan →]│
│              Takes 2-3 minutes                       │
│                                                      │
└─────────────────────────────────────────────────────┘

After clicking "Generate Recovery Plan":

┌─────────────────────────────────────────────────────┐
│  🚨 Crisis Recovery Planner - Generating...          │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Step 2 of 4: AI Analysis in Progress                │
│  ───────────────────────────────────────────────────│
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  ⏳ Analyzing your crisis...                     ││
│  │                                                 ││
│  │  ✅ Incident type classified                    ││
│  │  ✅ Searching 347 similar cases...              ││
│  │  ✅ Found 12 relevant incidents                 ││
│  │  ✅ Analyzing your organization structure       ││
│  │  ⏳ Calculating recovery timeline...            ││
│  │  ⏳ Estimating budget requirements...           ││
│  │  ⏳ Generating task breakdown...                ││
│  │  ⏳ Creating contingency plans...               ││
│  │                                                 ││
│  │  ████████████░░░░░ 75% Complete                 ││
│  │                                                 ││
│  │  Estimated time remaining: 45 seconds           ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  🤖 AI found 12 similar cases:                       │
│                                                      │
│  • Healthcare provider - DC fire (2023)              │
│    Recovery: 52 hours | Cost: $1.8M                  │
│  • E-commerce - Infrastructure failure (2024)        │
│    Recovery: 36 hours | Cost: $2.1M                  │
│  • Financial services - Catastrophic outage (2022)   │
│    Recovery: 72 hours | Cost: $3.5M                  │
│  ...                                                 │
│                                                      │
│  These will inform your recovery plan...             │
│                                                      │
└─────────────────────────────────────────────────────┘

After generation completes:

┌─────────────────────────────────────────────────────┐
│  🚨 Crisis Recovery Plan - Data Center Fire          │
│  Generated: Oct 9, 2025 3:45 PM | Confidence: 87%   │
│  [Export PDF] [Share] [Edit Plan] [Execute]  [🤖]   │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Step 3 of 4: Review AI-Generated Plan               │
│  ───────────────────────────────────────────────────│
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  📊 Executive Summary                            ││
│  │                                                 ││
│  │  Incident: Data Center Fire (Catastrophic)      ││
│  │  Current Downtime: 48 hours                     ││
│  │                                                 ││
│  │  Recovery Timeline:                              ││
│  │  • Phase 1: Immediate Stabilization (12 hrs)    ││
│  │  • Phase 2: Partial Restore (24 hrs)            ││
│  │  • Phase 3: Full Recovery (48 hrs)              ││
│  │  • Phase 4: Post-Recovery (7 days)              ││
│  │                                                 ││
│  │  Total Recovery Time: 84 hours from now         ││
│  │  Full Service Restore: Oct 12, 2025 11:45 PM   ││
│  │                                                 ││
│  │  Financial Impact:                               ││
│  │  • Recovery Costs: $650K - $850K                ││
│  │  • Revenue Loss: $6M (3 days total downtime)    ││
│  │  • Total Impact: $6.6M - $6.9M                  ││
│  │                                                 ││
│  │  Confidence: 87% (based on 12 similar cases)    ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  🎯 Three Scenarios                              ││
│  │                                                 ││
│  │  ╔════════════════════════════════════════════╗││
│  │  ║ 🟢 Best Case (30% probability)             ║││
│  │  ╚════════════════════════════════════════════╝││
│  │  Recovery Time: 60 hours                        ││
│  │  Cost: $620K                                     ││
│  │  Revenue Loss: $4M                               ││
│  │  Total Impact: $4.6M                             ││
│  │                                                 ││
│  │  Key Assumptions:                                ││
│  │  - DR site scales to 100% in 6 hours            ││
│  │  - No additional failures                        ││
│  │  - All IT staff available                        ││
│  │                                                 ││
│  │  ╔════════════════════════════════════════════╗││
│  │  ║ 🟡 Most Likely (55% probability) ✓ CURRENT ║││
│  │  ╚════════════════════════════════════════════╝││
│  │  Recovery Time: 84 hours                        ││
│  │  Cost: $750K                                     ││
│  │  Revenue Loss: $6M                               ││
│  │  Total Impact: $6.75M                            ││
│  │                                                 ││
│  │  Key Assumptions:                                ││
│  │  - DR scaling takes 12 hours                     ││
│  │  - Minor complications during recovery          ││
│  │  - 80% IT staff available                        ││
│  │                                                 ││
│  │  ╔════════════════════════════════════════════╗││
│  │  ║ 🔴 Worst Case (15% probability)            ║││
│  │  ╚════════════════════════════════════════════╝││
│  │  Recovery Time: 120 hours                       ││
│  │  Cost: $1.2M                                     ││
│  │  Revenue Loss: $10M                              ││
│  │  Total Impact: $11.2M                            ││
│  │                                                 ││
│  │  Key Assumptions:                                ││
│  │  - Major complications (data corruption)        ││
│  │  - DR site performance issues                    ││
│  │  - Staff burnout/availability issues            ││
│  │                                                 ││
│  │  [View Detailed Comparison]                      ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  📅 Recovery Timeline (Most Likely Scenario)    ││
│  │                                                 ││
│  │  Now: Oct 9, 3:45 PM                            ││
│  │  ↓                                               ││
│  │  Phase 1: Immediate Stabilization (12 hours)    ││
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    ││
│  │  Oct 9, 3:45 PM → Oct 10, 3:45 AM               ││
│  │                                                 ││
│  │  ⏰ Hour 1-2: Emergency Communications           ││
│  │     ✓ Notify all stakeholders                   ││
│  │     ✓ Activate crisis team                       ││
│  │     ✓ Issue public statement                     ││
│  │     Owner: Communications Lead                  ││
│  │     Status: ✅ Complete                          ││
│  │                                                 ││
│  │  ⏰ Hour 3-6: DR Site Scaling                    ││
│  │     □ Provision cloud resources                  ││
│  │     □ Scale DR to 80% capacity                   ││
│  │     □ Test critical systems                      ││
│  │     Owner: Infrastructure Team                  ││
│  │     Status: 🔵 In Progress (50% complete)        ││
│  │     [View Subtasks]                              ││
│  │                                                 ││
│  │  ⏰ Hour 7-12: Priority Service Restore          ││
│  │     □ Restore payment processing                 ││
│  │     □ Restore customer portal (read-only)       ││
│  │     □ Restore support ticket system              ││
│  │     Owner: Application Team                     ││
│  │     Status: ⏳ Pending (starts in 3 hours)       ││
│  │                                                 ││
│  │  Milestone: 40% → 70% service availability      ││
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    ││
│  │  ↓                                               ││
│  │  Phase 2: Partial Restore (24 hours)            ││
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    ││
│  │  Oct 10, 3:45 AM → Oct 11, 3:45 AM              ││
│  │                                                 ││
│  │  ⏰ Hour 13-18: Data Recovery                    ││
│  │     □ Restore from 6-hour-old backup            ││
│  │     □ Replay transaction logs                    ││
│  │     □ Validate data integrity                    ││
│  │     Owner: Database Team                        ││
│  │     Estimated data loss: 3-6 hours of txns      ││
│  │                                                 ││
│  │  ⏰ Hour 19-24: Secondary Services               ││
│  │     □ Restore analytics systems                  ││
│  │     □ Restore reporting tools                    ││
│  │     □ Restore admin dashboards                   ││
│  │     Owner: DevOps Team                          ││
│  │                                                 ││
│  │  ⏰ Hour 25-36: Full Functionality               ││
│  │     □ Enable all user transactions               ││
│  │     □ Restore integrations                       ││
│  │     □ Enable notifications                       ││
│  │     Owner: Application Team                     ││
│  │                                                 ││
│  │  Milestone: 70% → 95% service availability      ││
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    ││
│  │  ↓                                               ││
│  │  Phase 3: Full Recovery (48 hours)              ││
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    ││
│  │  Oct 11, 3:45 AM → Oct 13, 3:45 AM              ││
│  │                                                 ││
│  │  ⏰ Hour 37-60: Performance Optimization         ││
│  │     □ Scale to 100% capacity                     ││
│  │     □ Performance tuning                         ││
│  │     □ Load testing                               ││
│  │     Owner: SRE Team                             ││
│  │                                                 ││
│  │  ⏰ Hour 61-84: Monitoring & Stabilization       ││
│  │     □ 24/7 monitoring established                ││
│  │     □ Incident war room active                   ││
│  │     □ Rollback plans ready                       ││
│  │     Owner: Operations Team                      ││
│  │                                                 ││
│  │  Milestone: 100% service restored                ││
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    ││
│  │  ↓                                               ││
│  │  Phase 4: Post-Recovery (7 days)                ││
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    ││
│  │  Oct 13 → Oct 20                                ││
│  │                                                 ││
│  │  □ Root cause analysis                           ││
│  │  □ Lessons learned session                       ││
│  │  □ Update DR procedures                          ││
│  │  □ Rebuild primary DC (long-term)               ││
│  │  Owner: BCM Team                                ││
│  │                                                 ││
│  │  [View Gantt Chart] [Export Timeline]           ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  💰 Budget Breakdown                             ││
│  │                                                 ││
│  │  Total Estimated Cost: $750,000                 ││
│  │                                                 ││
│  │  Immediate Costs (Phase 1):                     ││
│  │  • Cloud compute (DR scaling)      $120,000     ││
│  │  • Emergency vendor support        $80,000      ││
│  │  • Overtime pay (IT staff)         $45,000      ││
│  │  • Emergency equipment purchase    $30,000      ││
│  │  Subtotal:                         $275,000     ││
│  │                                                 ││
│  │  Recovery Costs (Phase 2-3):                    ││
│  │  • Data recovery services          $150,000     ││
│  │  • Additional cloud resources      $200,000     ││
│  │  • Vendor consultants              $75,000      ││
│  │  • Network connectivity            $25,000      ││
│  │  Subtotal:                         $450,000     ││
│  │                                                 ││
│  │  Post-Recovery (Phase 4):                       ││
│  │  • Forensics investigation         $15,000      ││
│  │  • Documentation updates           $10,000      ││
│  │  Subtotal:                         $25,000      ││
│  │                                                 ││
│  │  Revenue Loss (3 days downtime):                ││
│  │  • Lost transactions               $6,000,000   ││
│  │  • Customer compensation           $500,000     ││
│  │  • Regulatory fines (estimated)    $250,000     ││
│  │  Subtotal:                         $6,750,000   ││
│  │                                                 ││
│  │  TOTAL IMPACT:                     $7,500,000   ││
│  │                                                 ││
│  │  💡 ROI Analysis:                                ││
│  │  If you had proper DR (100% capacity):          ││
│  │  Recovery: 12 hours | Cost: $1.2M               ││
│  │  Savings: $6.3M (84% reduction)                 ││
│  │                                                 ││
│  │  [View Detailed Budget] [Approve Budget]        ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  📋 Task Breakdown (156 tasks total)            ││
│  │                                                 ││
│  │  Filter: [All Phases ▾] [All Teams ▾]           ││
│  │  Sort: [By Priority ▾]                          ││
│  │                                                 ││
│  │  🔴 Critical (12 tasks)                         ││
│  │  ────────────────────────────────────────────  ││
│  │                                                 ││
│  │  ✅ TASK-001: Activate Crisis Team              ││
│  │     Phase: 1 | Owner: CEO                       ││
│  │     Due: Oct 9, 4:00 PM | Status: ✅ Complete   ││
│  │                                                 ││
│  │  🔵 TASK-002: Scale DR to 80% capacity          ││
│  │     Phase: 1 | Owner: Infrastructure Team      ││
│  │     Due: Oct 9, 9:45 PM | Status: 🔵 50% done   ││
│  │     ████████░░░░░░░░░░                          ││
│  │     Subtasks: 8/16 complete                     ││
│  │     [View Details] [Update Progress]            ││
│  │                                                 ││
│  │  ⏳ TASK-003: Restore payment processing        ││
│  │     Phase: 1 | Owner: Payment Team             ││
│  │     Due: Oct 10, 3:45 AM | Status: ⏳ Pending   ││
│  │     Dependencies: TASK-002 must complete        ││
│  │     [View Details] [Start Task]                 ││
│  │                                                 ││
│  │  ⏳ TASK-004: Issue customer communication      ││
│  │     Phase: 1 | Owner: Comms Lead               ││
│  │     Due: Oct 9, 6:00 PM | Status: ⚠️ Overdue    ││
│  │     [Escalate] [Reassign]                       ││
│  │                                                 ││
│  │  ... (8 more critical tasks)                    ││
│  │                                                 ││
│  │  🟡 High Priority (45 tasks)                    ││
│  │  [Expand]                                       ││
│  │                                                 ││
│  │  🟢 Medium Priority (78 tasks)                  ││
│  │  [Expand]                                       ││
│  │                                                 ││
│  │  ⚪ Low Priority (21 tasks)                     ││
│  │  [Expand]                                       ││
│  │                                                 ││
│  │  [Export Task List] [Import to Jira/Asana]     ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  🤖 AI Recommendations & Contingencies          ││
│  │                                                 ││
│  │  Based on 12 similar incidents, watch for:      ││
│  │                                                 ││
│  │  ⚠️ Risk 1: Data Corruption During Restore     ││
│  │  Probability: 35%                                ││
│  │  Impact: +24 hours to recovery                  ││
│  │  Mitigation:                                     ││
│  │  • Run integrity checks before restore          ││
│  │  • Keep backup of backup                        ││
│  │  • Have database experts on standby             ││
│  │  [Add to Plan]                                  ││
│  │                                                 ││
│  │  ⚠️ Risk 2: DR Site Performance Issues         ││
│  │  Probability: 45%                                ││
│  │  Impact: +12 hours to recovery                  ││
│  │  Mitigation:                                     ││
│  │  • Pre-provision 120% capacity                  ││
│  │  • Load test before cutover                     ││
│  │  • Have cloud burst plan ready                  ││
│  │  [Add to Plan]                                  ││
│  │                                                 ││
│  │  ⚠️ Risk 3: Staff Burnout                      ││
│  │  Probability: 60%                                ││
│  │  Impact: Reduced productivity, errors           ││
│  │  Mitigation:                                     ││
│  │  • Enforce 8-hour shifts with breaks            ││
│  │  • Bring in external consultants                ││
│  │  • Have backup staff list                       ││
│  │  [Add to Plan]                                  ││
│  │                                                 ││
│  │  💡 Success Factors from Similar Cases:         ││
│  │  • Daily CEO briefings (every 8 hours)          ││
│  │  • Dedicated war room (physical or virtual)     ││
│  │  • Real-time status dashboard                   ││
│  │  • Post-recovery celebration event              ││
│  │                                                 ││
│  │  [View All Recommendations]                      ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │  📢 Stakeholder Communications Plan             ││
│  │                                                 ││
│  │  Internal:                                       ││
│  │  • All staff: Email every 12 hours              ││
│  │  • Execs: Briefing every 8 hours                ││
│  │  • Board: Daily summary at 6 PM                 ││
│  │                                                 ││
│  │  External:                                       ││
│  │  • Customers: Status page updates every 2 hrs   ││
│  │  • Media: Press release (ready to send)         ││
│  │  • Regulators: Incident report by Oct 14        ││
│  │                                                 ││
│  │  [View Communication Templates]                 ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  Actions:                                            │
│  ┌────────────────────────────────────────────────┐│
│  │  ✅ Plan looks good - let's execute              ││
│  │  [Approve & Execute Plan] ← Starts command       │
│  │  center, assigns tasks, starts tracking          ││
│  │                                                 ││
│  │  📝 Need changes first                           ││
│  │  [Edit Plan] ← Modify timeline, tasks, budget   ││
│  │                                                 ││
│  │  📤 Share with team                              ││
│  │  [Export PDF] [Send to Team] [Print]            ││
│  │                                                 ││
│  │  🤖 Get alternatives                             ││
│  │  [Regenerate with Different Assumptions]        ││
│  └────────────────────────────────────────────────┘│
│                                                      │
└─────────────────────────────────────────────────────┘

After clicking "Approve & Execute":

┌─────────────────────────────────────────────────────┐
│  🚨 Crisis Command Center - ACTIVE INCIDENT          │
│  Data Center Fire | Status: Day 2 - Recovery         │
│  [Dashboard] [Tasks] [Timeline] [Comms] [Team] [🤖] │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ⏱️ LIVE STATUS                                      │
│  Recovery Progress: ████████░░░░░░ 42%              │
│  Time Elapsed: 48h 15m | Est. Remaining: 36h        │
│  Next Milestone: Partial Restore (in 9h 30m)        │
│                                                      │
│  ┌──────────────┬──────────────┬──────────────────┐│
│  │ 🔴 Critical  │ 🟡 High      │ 🟢 On Track      ││
│  │              │              │                  ││
│  │  3 tasks     │  7 tasks     │  145 tasks       ││
│  │  overdue     │  at risk     │  on schedule     ││
│  │              │              │                  ││
│  │ [View]       │ [View]       │ [View]           ││
│  └──────────────┴──────────────┴──────────────────┘│
│                                                      │
│  🔥 Active Issues:                                   │
│  • Customer comms 2hrs overdue → Escalated to CEO   │
│  • DR scaling stuck at 55% → Infrastructure team    │
│    investigating                                     │
│  • Database restore failed (try #1) → Retrying now  │
│                                                      │
│  📊 Service Status:                                  │
│  • Payment Processing: 🔴 Offline                    │
│  • Customer Portal: 🟡 Read-Only Mode                │
│  • Support System: 🟡 Limited Capacity (40%)         │
│  • Admin Tools: 🟢 Online                            │
│                                                      │
│  💰 Spend Tracking:                                  │
│  Budget Used: $312K / $750K (42%)                    │
│  Burn Rate: $6.5K/hour                               │
│  Projected Total: $742K (within budget!)             │
│                                                      │
│  👥 Team Status:                                     │
│  • 42 people actively working                        │
│  • 12 on shift, 30 on call                           │
│  • Next shift change: 6 PM (in 2h 15m)               │
│                                                      │
│  [Full Dashboard →]                                  │
│                                                      │
└─────────────────────────────────────────────────────┘
```

#### Key Features

1. **Crisis Upload**:
   - Natural language description (paste from incident report)
   - Voice input for hands-free
   - Import from Digital Twin (pre-filled org data)
   - Upload supporting docs (resource lists, timelines)

2. **AI Analysis**:
   - Searches 347 similar cases
   - Classifies incident automatically
   - Detects severity & impact
   - Estimates recovery parameters

3. **Three-Scenario Planning**:
   - Best case (optimistic)
   - Most likely (realistic) ✓ Default
   - Worst case (pessimistic)
   - Each with probability, timeline, cost

4. **Detailed Recovery Timeline**:
   - 4 phases with milestones
   - Hour-by-hour breakdown
   - Owner assignments
   - Dependencies mapped
   - Gantt chart view

5. **Budget Breakdown**:
   - Itemized costs per phase
   - Revenue loss calculation
   - Total impact projection
   - ROI analysis (vs if you had better DR)

6. **Task Management**:
   - 156 tasks auto-generated
   - Priority-based sorting
   - Real-time status updates
   - Integration with Jira/Asana

7. **Risk & Contingencies**:
   - AI-predicted risks (based on similar cases)
   - Mitigation strategies
   - Success factors from past incidents

8. **Command Center**:
   - Live dashboard when plan executes
   - Real-time progress tracking
   - Issue escalation
   - Team coordination
   - Budget burn rate monitoring

---

**Следующий шаг**: Продолжить дизайн для Journey 2-6?
Или начать имплементацию Journey 1 на основе этого дизайна?

Партнер, что скажешь? 🚀
