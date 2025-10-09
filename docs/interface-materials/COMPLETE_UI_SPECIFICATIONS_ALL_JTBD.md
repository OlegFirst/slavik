# Complete UI Specifications: All 7 JTBD

**Date**: 2025-10-09
**Version**: FINAL - Ready for Implementation
**Scope**: Detailed UI mockups, user flows, components for ALL 7 Jobs-to-be-Done

---

## 📐 HOMEPAGE: Entry Point for All JTBD

### Layout Structure

```
┌────────────────────────────────────────────────────────────┐
│  LOGO        [Search]      Solutions  Resources   Sign In  │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                                                              │
│    🚀 AI-Powered Business Continuity Platform               │
│                                                              │
│    What brings you here today?                              │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ 🎓 Get       │  │ 🔍 Find      │  │ 📚 Learn     │     │
│  │ ISO 22301   │  │ BCM          │  │ BCM          │     │
│  │ Certified   │  │ Services     │  │ Skills       │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│        #1                 #5                 #3             │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ 🛠️  Work     │  │ 🔬 Model     │  │ 🚨 IN       │     │
│  │ as BCM      │  │ Scenarios    │  │ CRISIS      │     │
│  │ Expert      │  │ (Twin)       │  │ NOW!        │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│        #2                 #6                 #7             │
│                                                              │
│  ✅ 2,450 Organizations  ✅ 487 Experts  ✅ 8,900 Students │
│                                                              │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  How It Works                                               │
│                                                              │
│  For Organizations:                                         │
│  1→ 2→ 3→  [Journey → AI Tools → Certificate]             │
│                                                              │
│  For Experts:                                               │
│  1→ 2→ 3→  [Profile → Match Clients → Earn]               │
│                                                              │
│  For Learners:                                              │
│  1→ 2→ 3→  [Learn → Practice → Get Hired]                 │
└────────────────────────────────────────────────────────────┘
```

---

## 🎓 JTBD #1: Get ISO 22301 Certified

### Entry Flow

```mermaid
graph LR
    A[Homepage: Click "Get Certified"] --> B[Assessment Quiz]
    B --> C[Roadmap Preview]
    C --> D{Sign Up}
    D --> E[Onboarding]
    E --> F[Dashboard]
```

### Assessment Quiz Page (`/certification/assessment`)

```
┌────────────────────────────────────────────────────────────┐
│  ← Back to Home                                    [Skip]  │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                                                              │
│  📋 BCM Readiness Assessment                                │
│                                                              │
│  Help us create your personalized certification roadmap     │
│  (2 minutes, 8 questions)                                   │
│                                                              │
│  Progress: ████████░░░░ 60% (Question 5 of 8)              │
│                                                              │
│  ──────────────────────────────────────────────────────────│
│                                                              │
│  Q5: Do you have documented business impact analysis?       │
│                                                              │
│    ○ Yes, comprehensive BIA for all critical processes      │
│    ○ Yes, but incomplete or outdated                        │
│    ● No, not yet (SELECTED)                                 │
│    ○ Not sure                                               │
│                                                              │
│  💡 AI Insight: "Based on similar organizations, expect     │
│      BIA to take 3-4 weeks with our AI-guided wizard."      │
│                                                              │
│                          [← Previous]  [Next →]             │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

### Roadmap Preview Page (`/certification/roadmap`)

```
┌────────────────────────────────────────────────────────────┐
│  🎯 Your Personalized ISO 22301 Certification Roadmap       │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                                                              │
│  Based on your assessment:                                  │
│                                                              │
│  Organization: Medium-sized (200 employees)                 │
│  Industry: Manufacturing                                    │
│  BCM Maturity: Beginner (20% complete)                      │
│                                                              │
│  ✨ Your estimated timeline: 18 weeks                       │
│  💰 Estimated cost: €6,794 (vs €50,000+ traditional)       │
│                                                              │
│  ──────────────────────────────────────────────────────────│
│                                                              │
│  📅 12-Week Journey:                                        │
│                                                              │
│  Week 1-4: Business Impact Analysis (BIA)                   │
│  ┌────────────────────────────────────────┐                │
│  │ ✅ Planning & Scoping      (Week 1)    │                │
│  │ 🔄 Conduct Interviews      (Week 2-3)  │ ← AI Assisted  │
│  │ ⏳ Analysis & Reporting    (Week 4)    │                │
│  │                                         │                │
│  │ Tasks: 12 | Est. Time: 40 hours        │                │
│  │ 💡 AI saves you: ~28 hours              │                │
│  └────────────────────────────────────────┘                │
│                                                              │
│  Week 5-8: BC Plans & Risk Management                       │
│  ┌────────────────────────────────────────┐                │
│  │ ⏳ Risk Assessment         (Week 5)    │                │
│  │ ⏳ Write BC Plans          (Week 6-7)  │ ← AI Generator │
│  │ ⏳ Test Plans              (Week 8)    │ ← Digital Twin │
│  └────────────────────────────────────────┘                │
│                                                              │
│  Week 9-10: Testing & Exercises                             │
│  Week 11-12: Documentation & Audit Prep                     │
│                                                              │
│  ──────────────────────────────────────────────────────────│
│                                                              │
│  💰 Cost Breakdown:                                         │
│                                                              │
│  Platform (6 months):        €1,794                         │
│  Auditor (marketplace):      €5,000                         │
│  ────────────────────                                       │
│  Total:                      €6,794                         │
│                                                              │
│  vs Traditional consulting:  €50,000+                       │
│  Your savings:               €43,206  (87%)                 │
│                                                              │
│                                                              │
│           [Start Free Trial] [Talk to Expert]               │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

### Certification Dashboard (`/certification/dashboard`)

```
┌────────────────────────────────────────────────────────────┐
│  LOGO    Dashboard  Journey  Marketplace  Help    [Profile] │
└────────────────────────────────────────────────────────────┘

┌──────────────────────┬─────────────────────────────────────┐
│                      │                                      │
│  📊 Navigation       │  🎯 ISO 22301 Certification Journey  │
│                      │                                      │
│  ✅ Dashboard        │  Week 2 of 18 | 12% Complete        │
│  🎯 Journey          │                                      │
│  📋 Tasks            │  Progress: ███░░░░░░░░░░░░░░░░░     │
│  💬 AI Assistant     │                                      │
│  🛒 Marketplace      │  Current Phase: BIA                  │
│  📚 Resources        │  Next Milestone: Complete 5 dept BIAs│
│  ⚙️  Settings        │                                      │
│                      │  ────────────────────────────────────│
│                      │                                      │
│  📅 This Week        │  📌 This Week's Tasks:               │
│                      │                                      │
│  Week 2: BIA Phase   │  ✅ 1. BIA Planning (2h) DONE       │
│                      │  🔄 2. Finance Dept BIA (in progress)│
│  Tasks: 4            │     └─ Interview scheduled (Oct 10)  │
│  Due: Oct 15         │  ⏳ 3. IT Dept BIA                   │
│                      │  ⏳ 4. Operations BIA                │
│  On track ✅         │                                      │
│                      │  [View All Tasks →]                  │
│  ────────────────    │                                      │
│                      │  ────────────────────────────────────│
│  💡 AI Coach         │                                      │
│                      │  🤖 AI Recommendations:              │
│  "You're ahead of    │                                      │
│  schedule! Consider  │  💡 Your BIA quality score: 8.5/10   │
│  starting BC Plans   │     Great documentation! Consider:   │
│  next week."         │     - Add financial impact data      │
│                      │     - Validate RTO with stakeholders │
│  [Ask AI →]          │                                      │
│                      │  💡 Similar organizations completed   │
│                      │     BIA in 3.2 weeks (you: 2 weeks)  │
│                      │                                      │
│                      │  [Get AI Help]                       │
│                      │                                      │
│                      │  ────────────────────────────────────│
│                      │                                      │
│                      │  🎬 Quick Actions:                   │
│                      │                                      │
│                      │  [Continue BIA Wizard →]             │
│                      │  [Schedule Review Meeting]           │
│                      │  [Hire Expert (Marketplace)]         │
│                      │  [Generate Progress Report]          │
│                      │                                      │
└──────────────────────┴─────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  📈 Certification Progress by Clause                        │
│                                                              │
│  Clause 4: Context                   ████████░░ 80%         │
│  Clause 5: Leadership                ██████░░░░ 60%         │
│  Clause 6: Planning                  ████░░░░░░ 40%         │
│  Clause 8: Operation                 ██░░░░░░░░ 20%  ← BIA  │
│  Clause 9: Performance               ░░░░░░░░░░  0%         │
│  Clause 10: Improvement              ░░░░░░░░░░  0%         │
│                                                              │
│  Overall Compliance: 25%  (Target 100% by Week 18)          │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

### BIA Wizard - Step 2: Interview with AI (`/bia/interview`)

```
┌────────────────────────────────────────────────────────────┐
│  BIA Wizard: Finance Department                             │
│  Step 2 of 6: Conduct Interview                             │
└────────────────────────────────────────────────────────────┘

┌──────────────────────┬─────────────────────────────────────┐
│                      │                                      │
│  📋 Interview        │  🎙️ Live Interview Session          │
│     Progress         │                                      │
│                      │  Interviewing: Maria (Finance Mgr)   │
│  Progress: 60%       │  Started: 10:30 AM                   │
│  ████████░░░░        │  Duration: 25 minutes                │
│                      │                                      │
│  Sections:           │  ────────────────────────────────────│
│  ✅ Overview         │                                      │
│  ✅ Processes        │  💬 Interview Transcript:            │
│  🔄 Dependencies     │                                      │
│  ⏳ Impact           │  You: "What is the RTO target for    │
│  ⏳ Resources        │        month-end closing?"           │
│  ⏳ Recovery         │                                      │
│                      │  Maria: "We need to complete within  │
│  ────────────────    │         3 days after month end."     │
│                      │                                      │
│  🤖 AI Assistant     │  🤖 AI Analysis:                     │
│     Active           │     ✓ RTO identified: 72 hours       │
│                      │     ⚠️ Benchmark: Similar orgs use   │
│  💡 "Ask about       │        48 hours. Consider if 72h is  │
│      disaster        │        competitive.                  │
│      scenarios"      │                                      │
│                      │  💡 Suggested follow-up:             │
│  [Toggle AI]         │     "What happens if RTO is missed?" │
│                      │                                      │
│                      │  [Use This Question]                 │
│                      │                                      │
│                      │  ────────────────────────────────────│
│                      │                                      │
│                      │  Your Questions:                     │
│                      │  ┌────────────────────────────────┐ │
│                      │  │ [Type your question...]        │ │
│                      │  │                                │ │
│                      │  └────────────────────────────────┘ │
│                      │                                      │
│                      │  Maria's Response:                   │
│                      │  ┌────────────────────────────────┐ │
│                      │  │ [Record answer...]             │ │
│                      │  │                                │ │
│                      │  └────────────────────────────────┘ │
│                      │                                      │
│                      │  [Save & Continue →]                 │
│                      │                                      │
└──────────────────────┴─────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  🎯 AI Insights (Real-time)                                 │
│                                                              │
│  ✅ Good coverage: Financial processes well documented      │
│  ⚠️ Missing: Discussion of backup personnel                 │
│  💡 Suggestion: Ask about manual workaround procedures      │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

### Evidence Package Generator (`/certification/evidence`)

```
┌────────────────────────────────────────────────────────────┐
│  📦 ISO 22301 Evidence Package                              │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                                                              │
│  🤖 AI Auto-Collection Complete                             │
│                                                              │
│  Found: 127 documents across platform                       │
│  Organized by: ISO 22301 clause                             │
│  Last updated: Oct 9, 2025 15:30                            │
│                                                              │
│  ────────────────────────────────────────────────────────────│
│                                                              │
│  📂 Clause 4: Context of the Organization (12 docs)         │
│                                                              │
│  ✅ 4.1 Understanding the organization                      │
│     └─ organization_profile.pdf                             │
│     └─ stakeholder_analysis.xlsx                            │
│                                                              │
│  ✅ 4.2 Understanding needs and expectations                │
│     └─ stakeholder_requirements.docx                        │
│                                                              │
│  ✅ 4.3 Determining the scope of BCMS                       │
│     └─ bcms_scope_statement.pdf                             │
│                                                              │
│  [Expand All] [Preview Package]                             │
│                                                              │
│  ────────────────────────────────────────────────────────────│
│                                                              │
│  📂 Clause 8: Operation (47 docs) ⭐ Most Content           │
│                                                              │
│  ✅ 8.2 Business Impact Analysis (12)                       │
│     └─ Finance_BIA_Report.pdf                               │
│     └─ IT_BIA_Report.pdf                                    │
│     └─ Operations_BIA_Report.pdf                            │
│     └─ ... 9 more files                                     │
│                                                              │
│  ✅ 8.3 Risk Assessment (8)                                 │
│  ✅ 8.4 Business Continuity Plans (15)                      │
│  ✅ 8.5 Exercise and Testing (5)                            │
│                                                              │
│  ────────────────────────────────────────────────────────────│
│                                                              │
│  🎯 Audit Readiness Score: 94/100 ✅                        │
│                                                              │
│  ✅ Documentation: 100%  (127/127 required docs)            │
│  ✅ Evidence Quality: 98%  (AI review)                      │
│  ⚠️ Management Review: 80%  (1 item pending)                │
│  ✅ Completeness: 92%                                       │
│                                                              │
│  Minor Gaps:                                                 │
│  - Management review signature (Clause 9.3)                 │
│  - Exercise report Q4 incomplete (Clause 8.5)               │
│                                                              │
│  ────────────────────────────────────────────────────────────│
│                                                              │
│  📤 Export Options:                                         │
│                                                              │
│  [📦 Download ZIP (encrypted)]                              │
│  [☁️  Share with Auditor (secure link, 30 days)]           │
│  [📧 Email Package]                                         │
│  [🖨️  Print Checklist]                                      │
│                                                              │
│  ────────────────────────────────────────────────────────────│
│                                                              │
│  💡 Ready for audit?                                        │
│                                                              │
│  [Find Certified Auditor →] [Schedule Pre-Audit]            │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

---

## 🔍 JTBD #2: Simplify Auditor Work

### Auditor Dashboard (`/auditor/dashboard`)

```
┌────────────────────────────────────────────────────────────┐
│  LOGO    Dashboard  Clients  Services  Profile    [Wallet] │
└────────────────────────────────────────────────────────────┘

┌──────────────────────┬─────────────────────────────────────┐
│                      │  💰 Earnings Overview                │
│  👤 Maria Sokolova   │                                      │
│  ⭐ 4.9 (89 reviews) │  This Month: €12,500                 │
│  🏆 Top 5% Auditor   │  YTD: €87,000                        │
│                      │  Trend: +45% vs last year            │
│  ────────────────    │                                      │
│                      │  ┌──────────┬──────────┬──────────┐ │
│  📊 Quick Stats      │  │ Audits   │ Pre-Audit│ Consult  │ │
│                      │  │ €9,000   │ €2,400   │ €1,100   │ │
│  3 Completed         │  │ (3)      │ (2)      │ (7h)     │ │
│  3 In Progress       │  └──────────┴──────────┴──────────┘ │
│  2 Upcoming          │                                      │
│  5 New Requests      │  Platform Fee (12%): €1,875          │
│                      │  Net Earnings: €10,625 💸            │
│  🤖 AI Saved You:    │                                      │
│  67 hours this mo    │  ────────────────────────────────────│
│  (€10,050 value)     │                                      │
│                      │  📅 Active Clients                   │
│  [View Report]       │                                      │
│                      │  🔄 In Progress:                     │
│                      │                                      │
│                      │  1. Acme Corp - Pre-audit            │
│                      │     Due: Oct 15 | Progress: 60%      │
│                      │     [Continue →]                     │
│                      │                                      │
│                      │  2. Beta LLC - Full audit            │
│                      │     Scheduled: Oct 20 | Prep: 80%    │
│                      │     [Review Evidence]                │
│                      │                                      │
│                      │  3. Gamma Inc - Consultation         │
│                      │     Ongoing | Next call: Oct 12      │
│                      │     [Join Meeting]                   │
│                      │                                      │
│                      │  ────────────────────────────────────│
│                      │                                      │
│                      │  📬 New Booking Requests (5)         │
│                      │                                      │
│                      │  1. Delta Ltd - Full Audit           │
│                      │     Budget: €4,500 | Date: Nov 5     │
│                      │     Industry: Healthcare             │
│                      │     [Accept] [Decline] [Negotiate]   │
│                      │                                      │
│                      │  2. Epsilon SA - Gap Analysis        │
│                      │     Budget: €900 | ASAP              │
│                      │     Industry: Finance                │
│                      │     [Quick Accept] [View Details]    │
│                      │                                      │
│                      │  [View All Requests →]               │
│                      │                                      │
└──────────────────────┴─────────────────────────────────────┘
```

### AI Audit Assistant - Document Analysis (`/auditor/client/acme/analysis`)

```
┌────────────────────────────────────────────────────────────┐
│  Client: Acme Corp | Pre-Audit Analysis                     │
└────────────────────────────────────────────────────────────┘

┌──────────────────────┬─────────────────────────────────────┐
│                      │  🤖 AI Document Analysis              │
│  📂 Evidence Package │                                      │
│                      │  Status: ✅ Analysis Complete        │
│  127 documents       │  Time: 45 seconds                    │
│  2,450 pages         │  Accuracy: 94%                       │
│                      │                                      │
│  Received: Oct 8     │  ────────────────────────────────────│
│  Analyzed: Oct 9     │                                      │
│                      │  📊 Compliance Score: 78/100         │
│  ────────────────    │                                      │
│                      │  ┌──────────────────────────────┐   │
│  🔍 Filter           │  │ ████████░░░░░░░ 78%          │   │
│                      │  └──────────────────────────────┘   │
│  [ ] Strong Areas    │                                      │
│  [x] Gaps (12)       │  Clause Breakdown:                   │
│  [ ] Missing (3)     │  ✅ Clause 4: Context       100%     │
│                      │  ✅ Clause 5: Leadership     90%     │
│  ────────────────    │  ⚠️ Clause 6: Planning       75%     │
│                      │  ✅ Clause 8: Operation      85%     │
│  📄 Document Types   │  ⚠️ Clause 9: Performance    45%  ⚠️ │
│                      │  ✅ Clause 10: Improvement   80%     │
│  [x] BIAs (12)       │                                      │
│  [ ] Risks (8)       │  ────────────────────────────────────│
│  [ ] Plans (15)      │                                      │
│  [ ] Exercises (5)   │  ⚠️ CRITICAL GAPS FOUND (3)         │
│                      │                                      │
│                      │  1. Clause 8.5: Insufficient Testing │
│                      │     Evidence: Only 3 exercises found │
│                      │     Required: Min 1 per year         │
│                      │     Found: exercise_2023.pdf,        │
│                      │            exercise_2024_q1.pdf,     │
│                      │            exercise_2024_q2.pdf      │
│                      │     Gap: Q3/Q4 2024 missing          │
│                      │                                      │
│                      │     💡 Recommendation:               │
│                      │     Request evidence of Q3/Q4 2024   │
│                      │     exercises. If not conducted,     │
│                      │     minor non-conformance likely.    │
│                      │                                      │
│                      │     [Add to Audit Checklist]         │
│                      │     [Generate Follow-up Email]       │
│                      │                                      │
│                      │  2. Clause 9.3: Management Review    │
│                      │     Evidence: mgmt_review_2024.pdf   │
│                      │     Issue: CEO signature missing     │
│                      │            (page 12, signature line) │
│                      │                                      │
│                      │     💡 Recommendation:               │
│                      │     Obtain CEO signature before      │
│                      │     audit. Otherwise, document       │
│                      │     approval via email/minutes.      │
│                      │                                      │
│                      │     [Flag for Client]                │
│                      │                                      │
│                      │  3. Clause 8.3: Risk Treatment       │
│                      │     Evidence: risk_register.xlsx     │
│                      │     Issue: 2 high risks without      │
│                      │            treatment plans           │
│                      │            (rows 15, 23)             │
│                      │                                      │
│                      │     Risk #15: Cyber attack (L:4, I:5)│
│                      │     Risk #23: Key supplier (L:3, I:5)│
│                      │                                      │
│                      │     💡 Recommendation:               │
│                      │     Request treatment plans or       │
│                      │     justification for acceptance.    │
│                      │                                      │
│                      │     [Add to Findings]                │
│                      │                                      │
│                      │  ────────────────────────────────────│
│                      │                                      │
│                      │  ❌ MISSING DOCUMENTS (1)            │
│                      │                                      │
│                      │  - External audit report             │
│                      │    (Clause 9.2.2 - optional but      │
│                      │     recommended)                     │
│                      │                                      │
│                      │  ────────────────────────────────────│
│                      │                                      │
│                      │  ✅ STRONG AREAS (4)                 │
│                      │                                      │
│                      │  • Clause 4: Excellent context docs  │
│                      │  • Clause 8.2: Comprehensive BIAs    │
│                      │  • Clause 8.4: Well-structured plans │
│                      │  • Documentation quality: High       │
│                      │                                      │
│                      │  ────────────────────────────────────│
│                      │                                      │
│                      │  🎬 Quick Actions:                   │
│                      │                                      │
│                      │  [Generate Pre-Audit Report (PDF)]   │
│                      │  [Email Client with Gaps]            │
│                      │  [Schedule Audit Date]               │
│                      │  [Start Interview Questions]         │
│                      │                                      │
└──────────────────────┴─────────────────────────────────────┘
```

### AI Interview Transcript & Notes (`/auditor/client/acme/interview`)

```
┌────────────────────────────────────────────────────────────┐
│  🎙️ Live Interview: Finance Manager                        │
│  [●REC] 00:15:34  | Auto-transcription: ON | AI Notes: ON  │
└────────────────────────────────────────────────────────────┘

┌──────────────────────┬─────────────────────────────────────┐
│                      │  💬 Transcript                       │
│  📝 AI Notes         │                                      │
│     (Auto-generated) │  [00:15] Maria (Auditor):            │
│                      │  "How often do you review RTO        │
│  ✅ RTO Review       │   targets for critical processes?"   │
│     Frequency        │                                      │
│     Confirmed        │  [00:22] Finance Manager:            │
│     └─ Quarterly     │  "We review them quarterly. Last     │
│        (compliant)   │   review was in August."             │
│                      │                                      │
│  ⚠️ BC Plan Approval │  🤖 AI Auto-Note:                    │
│     Process          │  ✓ Frequency: Quarterly = Good       │
│     └─ Dept head     │  ✓ Recent: August (2 months ago)     │
│        approves      │  ✓ Compliance: Meets ISO requirement │
│        (gap!)        │  📝 Action: Request Aug review doc   │
│                      │                                      │
│  📌 Follow-ups       │  ──────────────────────────────────  │
│     Generated        │                                      │
│     └─ Q: ISO        │  [00:45] Maria:                      │
│        requires      │  "Who approves changes to BC plans?" │
│        top mgmt      │                                      │
│        approval      │  [00:50] Finance Manager:            │
│                      │  "Usually the department head        │
│  ────────────────    │   approves any changes."             │
│                      │                                      │
│  🎯 Key Findings     │  🤖 AI Flag:                         │
│     (3)              │  ⚠️ ISO 22301 GAP DETECTED           │
│                      │                                      │
│  1. RTO review: ✅   │  Clause 8.4.3 requires top           │
│  2. Approval: ⚠️     │  management approval for BC plans.   │
│  3. Testing: ⏳      │  Department head approval may not    │
│                      │  meet this requirement.              │
│                      │                                      │
│                      │  💡 Suggested Follow-up:             │
│                      │  "Can you show me the approval       │
│                      │   process documentation? Does the    │
│                      │   CEO or COO review major changes?"  │
│                      │                                      │
│                      │  [Use This Question]                 │
│                      │  [Add to Findings]                   │
│                      │                                      │
│                      │  ──────────────────────────────────  │
│                      │                                      │
│                      │  [01:05] Maria:                      │
│                      │  [Using AI suggestion]               │
│                      │  "Can you show me the approval       │
│                      │   process documentation?"            │
│                      │                                      │
│                      │  [01:12] Finance Manager:            │
│                      │  "We have a policy document that     │
│                      │   outlines this. I can send it."     │
│                      │                                      │
│                      │  🤖 AI Note:                         │
│                      │  ✓ Action item: Request policy doc   │
│                      │  📎 Auto-added to evidence checklist │
│                      │                                      │
└──────────────────────┴─────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  📄 AI-Generated Interview Summary (Real-time)              │
│                                                              │
│  Key Findings:                                               │
│  ✅ RTO review process: Compliant (quarterly)               │
│  ⚠️ BC plan approval: Gap (dept vs top mgmt)                │
│  📝 Evidence requested: Approval policy document            │
│                                                              │
│  Time saved by AI: 15 minutes (auto notes + suggestions)    │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

---

## 📚 JTBD #3: Learn BCM Skills

### Learning Dashboard (`/learn/dashboard`)

```
┌────────────────────────────────────────────────────────────┐
│  LOGO    Courses  Cases  Practice  Career  Profile  [Help] │
└────────────────────────────────────────────────────────────┘

┌──────────────────────┬─────────────────────────────────────┐
│                      │  🎓 Your Learning Path               │
│  👤 Dmitry P.        │                                      │
│  🎯 Goal: BCM        │  BCM Professional Certification      │
│     Consultant       │                                      │
│                      │  Week 8 of 24 | 35% Complete         │
│  ────────────────    │                                      │
│                      │  Progress: ████████░░░░░░░░░░       │
│  📊 Your Progress    │                                      │
│                      │  ────────────────────────────────────│
│  Courses: 35%        │                                      │
│  ██████░░░░░         │  📚 Current Module:                  │
│                      │                                      │
│  Practice: 60%       │  Module 2: BIA Deep Dive             │
│  ███████████░        │  Progress: 60% | Score: 87%          │
│                      │                                      │
│  Cases: 10/347       │  ┌──────────────────────────────┐   │
│  ██░░░░░░░░░         │  │ ✅ BIA Methodology (90%)     │   │
│                      │  │ ✅ RTO/RPO Analysis (85%)    │   │
│  Skill Level:        │  │ 🔄 Dependency Mapping (60%) │   │
│  Intermediate        │  │ ⏳ Practice Case             │   │
│  ██████░░░░░         │  │ ⏳ Module Quiz               │   │
│                      │  └──────────────────────────────┘   │
│  ────────────────    │                                      │
│                      │  [Continue Learning →]               │
│  🏆 Achievements     │                                      │
│                      │  ────────────────────────────────────│
│  🎖️ BIA Basics      │                                      │
│  🎖️ 10 Cases Done   │  📌 This Week's Plan:                │
│  ⏳ Risk Expert      │                                      │
│     (locked)         │  Mon: Complete Dependency Mapping    │
│                      │       video (45 min)                 │
│                      │                                      │
│  ────────────────    │  Tue: Read Case A47 (Healthcare)     │
│                      │       (1 hour)                       │
│  💡 AI Tutor         │                                      │
│                      │  Wed: Practice: Mock BIA             │
│  "Based on your      │       (2 hours)                      │
│  progress, try       │                                      │
│  Case #A47 next.     │  Thu: Module 2 Quiz                  │
│  It demonstrates     │       (30 min)                       │
│  BIA in a real       │                                      │
│  crisis."            │  Fri: Review & move to Module 3      │
│                      │                                      │
│  [Ask AI →]          │  [Adjust Schedule]                   │
│                      │                                      │
└──────────────────────┴─────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  🔥 Recommended for You                                     │
│                                                              │
│  📋 Case #A47: Healthcare Ransomware Attack                 │
│  ⭐⭐⭐ Intermediate | 2 hours | 4.8/5 (1,240 students)    │
│                                                              │
│  "Perfect for your Module 2 progress. See BIA in action!"   │
│                                                              │
│  [Start Case →]                                             │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

### Case Study Explorer (`/learn/cases/A47`)

```
┌────────────────────────────────────────────────────────────┐
│  ← Back to Cases                          [Save] [Share]    │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                                                              │
│  📋 Case #A47: Healthcare Ransomware Attack                 │
│                                                              │
│  Industry: Healthcare | Difficulty: ⭐⭐⭐ Intermediate     │
│  Duration: 2 hours | Completed by: 1,240 students           │
│  Rating: 4.8/5 | Learning Focus: BIA, Crisis Response       │
│                                                              │
│  ────────────────────────────────────────────────────────────│
│                                                              │
│  📖 Case Overview:                                          │
│                                                              │
│  Organization: 250-bed hospital (anonymized)                │
│  Scenario: Ransomware encrypted EHR system                  │
│  Date: March 2024                                           │
│                                                              │
│  Real Data:                                                  │
│  • RTO Target: 4 hours                                      │
│  • Actual Recovery: 6 hours                                 │
│  • Financial Impact: $450,000                               │
│  • Patients Affected: 8,500                                 │
│  • Downtime: Critical systems offline for 6 hours           │
│                                                              │
│  ────────────────────────────────────────────────────────────│
│                                                              │
│  🎯 What You'll Learn:                                      │
│                                                              │
│  ✓ How BIA helps identify critical systems (EHR RTO: 4h)    │
│  ✓ Crisis team activation and decision-making               │
│  ✓ Communication strategy (patients, staff, regulators)     │
│  ✓ Technical recovery steps and challenges                  │
│  ✓ Financial impact calculation methodology                 │
│  ✓ Lessons learned and BC plan improvements                 │
│                                                              │
│  ────────────────────────────────────────────────────────────│
│                                                              │
│  📚 Available Materials:                                    │
│                                                              │
│  📄 Timeline of Events (interactive)                        │
│  📄 Crisis Communication Log (47 messages)                  │
│  📄 Recovery Procedures Used                                │
│  📄 Post-Incident Report (12 pages)                         │
│  📊 Financial Impact Analysis (detailed breakdown)          │
│  🎥 Video: Crisis Commander Interview (15 min)             │
│                                                              │
│  ────────────────────────────────────────────────────────────│
│                                                              │
│  🎮 Learning Modes:                                         │
│                                                              │
│  ┌───────────────────────┬───────────────────────┐         │
│  │  📖 Study Mode        │  🎮 Practice Mode     │         │
│  │                       │                       │         │
│  │  Read the case,       │  "You are the BCM     │         │
│  │  explore materials,   │  Manager. Make        │         │
│  │  learn at your pace   │  decisions, see       │         │
│  │                       │  consequences."       │         │
│  │                       │                       │         │
│  │  [Start Study →]      │  [Start Practice →]   │         │
│  └───────────────────────┴───────────────────────┘         │
│                                                              │
│  ────────────────────────────────────────────────────────────│
│                                                              │
│  💬 Student Reviews:                                        │
│                                                              │
│  ⭐⭐⭐⭐⭐ "Excellent case! The financial impact          │
│            analysis helped me understand BIA value."        │
│            - Anna K., BCM Student                           │
│                                                              │
│  ⭐⭐⭐⭐⭐ "Practice mode is incredible. I made wrong       │
│            decisions and learned why!"                      │
│            - Pavel M., IT Manager                           │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

### Practice Sandbox (`/learn/sandbox`)

```
┌────────────────────────────────────────────────────────────┐
│  🏢 Practice Organization: TechCorp                         │
│  Your Mission: Build complete BCM program from scratch      │
└────────────────────────────────────────────────────────────┘

┌──────────────────────┬─────────────────────────────────────┐
│                      │  🏢 TechCorp Profile                 │
│  🎯 Your Mission     │                                      │
│                      │  Industry: Software Development      │
│  Build BCM program   │  Size: 150 employees                 │
│  from zero to ISO    │  Revenue: $12M/year                  │
│  22301 ready         │  Locations: 3 offices (HQ + 2 remote)│
│                      │  Products: SaaS platform             │
│  Progress: 40%       │                                      │
│  ████████░░░░        │  Current State:                      │
│                      │  ❌ No BCM program                   │
│  ────────────────    │  ⚠️ 2 incidents last year (8h down) │
│                      │  ✅ CEO wants ISO 22301              │
│  📋 Completed        │  💰 Budget: $50K                     │
│                      │                                      │
│  ✅ BIA for IT       │  ────────────────────────────────────│
│     (Score: 8.5/10)  │                                      │
│  ✅ BIA for Sales    │  🎯 Current Task:                    │
│     (Score: 7.2/10)  │                                      │
│  🔄 BIA for Ops      │  Conduct BIA for Operations Dept     │
│     (in progress)    │                                      │
│                      │  ┌──────────────────────────────┐   │
│  ⏳ To Do            │  │ 🎙️ Interview: Ops Manager    │   │
│                      │  │                              │   │
│  ⏳ Risk Assessment  │  │ Ask questions to identify:   │   │
│  ⏳ BC Plans         │  │ • Critical processes         │   │
│  ⏳ Exercises        │  │ • RTO/RPO targets            │   │
│                      │  │ • Dependencies               │   │
│  ────────────────    │  │ • Impact of downtime         │   │
│                      │  └──────────────────────────────┘   │
│  🤖 AI Feedback      │                                      │
│                      │  Virtual Stakeholder: Jane (Ops Mgr) │
│  Your IT BIA:        │                                      │
│  8.5/10 ✅           │  You: "What is your main process?"   │
│                      │                                      │
│  ✅ Strong:          │  Jane: "We handle customer support   │
│  - Process ID        │        tickets and onboarding."      │
│  - Interviews        │                                      │
│                      │  [Multiple choice:]                  │
│  ⚠️ Improve:         │  Your next question:                 │
│  - RTO calc          │  ○ What is the RTO target?           │
│    methodology       │  ○ How many tickets per day?         │
│                      │  ○ What happens if system is down?   │
│  ❌ Missing:         │  ○ Who are your key personnel?       │
│  - Financial         │                                      │
│    impact quant      │  💡 AI Hint: Ask about impact first  │
│                      │                                      │
│  [Review Case        │  [Select Answer]                     │
│   #A23 for help]     │                                      │
│                      │  ────────────────────────────────────│
│                      │                                      │
│                      │  🎯 Your Sandbox Tools:              │
│                      │                                      │
│                      │  [BIA Wizard] [Risk Tool]            │
│                      │  [Plan Generator] [Exercise Builder] │
│                      │                                      │
│                      │  All tools work on TechCorp data     │
│                      │  AI grades your work in real-time    │
│                      │                                      │
└──────────────────────┴─────────────────────────────────────┘
```

---

## 🛒 JTBD #5: Find Affordable BCM Services

### Marketplace: Service Browser (`/marketplace`)

```
┌────────────────────────────────────────────────────────────┐
│  LOGO    Services  Experts  My Projects  Help    [Sign In] │
└────────────────────────────────────────────────────────────┘

┌──────────────────────┬─────────────────────────────────────┐
│                      │  🛒 BCM Services Marketplace         │
│  🔍 Filters          │                                      │
│                      │  Find verified BCM experts at        │
│  Service Type:       │  affordable prices                   │
│  ☑ BIA Facilitation  │                                      │
│  ☐ BC Plan Writing   │  87 services available               │
│  ☐ Risk Assessment   │                                      │
│  ☐ Training          │  ────────────────────────────────────│
│  ☐ Gap Analysis      │                                      │
│  ☐ Audit Prep        │  🎯 Popular Services:                │
│                      │                                      │
│  Budget:             │  1. BIA Facilitation                 │
│  €800 - €2,500       │     €800-2,500 | 2-4 weeks           │
│  [€€€€€€░░░░]       │     87 providers                     │
│                      │                                      │
│  Rating:             │  2. BC Plan Writing                  │
│  ⭐⭐⭐⭐+ only      │     €1,200-3,500 | 1-3 weeks          │
│                      │     64 providers                     │
│  Location:           │                                      │
│  [ ] Remote          │  3. ISO 22301 Gap Analysis           │
│  [ ] EU              │     €500-1,500 | 1 week              │
│  [ ] CIS             │     92 providers                     │
│  [ ] Global          │                                      │
│                      │  ────────────────────────────────────│
│  Experience:         │                                      │
│  [ ] 5+ years        │  👤 Featured Expert:                 │
│  [ ] 10+ years       │                                      │
│                      │  ┌──────────────────────────────┐   │
│  Industry:           │  │ Olga Ivanova               │   │
│  ☑ Manufacturing     │  │ ⭐ 4.8 (43 reviews)         │   │
│  ☐ Healthcare        │  │                             │   │
│  ☐ Finance           │  │ 🎓 CBCP, ISO 22301          │   │
│  ☐ IT                │  │ 💼 8 years, 120+ projects   │   │
│                      │  │ 📍 Remote + EU travel       │   │
│  ────────────────    │  │                             │   │
│                      │  │ Service: BIA Facilitation   │   │
│  🛡️ Platform        │  │ Price: €1,500               │   │
│     Guarantee        │  │                             │   │
│                      │  │ Package Includes:           │   │
│  ✅ Verified         │  │ ✅ Kick-off workshop (4h)   │   │
│     credentials      │  │ ✅ Interview templates      │   │
│  ✅ Escrow payment   │  │ ✅ 5 department BIAs        │   │
│  ✅ Quality reviews  │  │ ✅ Dependency mapping       │   │
│  ✅ Dispute          │  │ ✅ Executive report         │   │
│     resolution       │  │ ✅ Platform integration     │   │
│  ✅ Money-back       │  │                             │   │
│                      │  │ Delivery: 3 weeks           │   │
│                      │  │ Revisions: 2 rounds         │   │
│                      │  │                             │   │
│                      │  │ Recent Review:              │   │
│                      │  │ "Excellent work. Completed  │   │
│                      │  │  our BIA in 2.5 weeks!"     │   │
│                      │  │  - Pavel K.                 │   │
│                      │  │                             │   │
│                      │  │ [View Profile]  [Hire Now]  │   │
│                      │  └──────────────────────────────┘   │
│                      │                                      │
│                      │  ────────────────────────────────────│
│                      │                                      │
│                      │  💡 Not sure what you need?          │
│                      │                                      │
│                      │  [Post Your Request] - Get proposals │
│                      │  from multiple experts in 48 hours   │
│                      │                                      │
└──────────────────────┴─────────────────────────────────────┘
```

### Project Workspace (`/marketplace/project/12345`)

```
┌────────────────────────────────────────────────────────────┐
│  Project: BIA for Sergey's Manufacturing                    │
│  Expert: Olga Ivanova | Status: 🔄 In Progress (Week 2)    │
└────────────────────────────────────────────────────────────┘

┌──────────────────────┬─────────────────────────────────────┐
│                      │  📊 Project Overview                 │
│  💰 Payment          │                                      │
│     Milestones       │  Budget: €2,000                      │
│                      │  Timeline: Oct 10 - Nov 7 (4 weeks)  │
│  €2,000 total        │  Progress: 40% ████████░░░░         │
│                      │                                      │
│  ✅ Milestone 1      │  ────────────────────────────────────│
│     Kick-off         │                                      │
│     €400             │  💰 Payment Status:                  │
│     PAID Oct 10      │                                      │
│                      │  ┌──────────────────────────────┐   │
│  🔄 Milestone 2      │  │ ✅ Milestone 1: Kick-off     │   │
│     Interviews       │  │    €400 | Paid Oct 10        │   │
│     €800             │  │                              │   │
│     IN REVIEW        │  │ Deliverable: Workshop slides │   │
│                      │  │ Status: APPROVED ✅          │   │
│  Olga submitted:     │  └──────────────────────────────┘   │
│  Oct 24              │                                      │
│                      │  ┌──────────────────────────────┐   │
│  Deliverables:       │  │ 🔄 Milestone 2: Interviews   │   │
│  - Interview         │  │    €800 | In Review          │   │
│    transcripts (5)   │  │                              │   │
│  - Initial findings  │  │ Due: Oct 24                  │   │
│                      │  │ Submitted: Oct 24 (on time!) │   │
│  [Review] [Approve]  │  │                              │   │
│  [Request Changes]   │  │ Deliverables:                │   │
│                      │  │ 📄 Interview_Finance.pdf     │   │
│  ⏳ Milestone 3      │  │ 📄 Interview_IT.pdf          │   │
│     Draft Report     │  │ 📄 Interview_Ops.pdf         │   │
│     €600             │  │ 📄 Interview_Sales.pdf       │   │
│     Due: Oct 31      │  │ 📄 Interview_Logistics.pdf   │   │
│                      │  │ 📄 Initial_findings.docx     │   │
│  ⏳ Milestone 4      │  │                              │   │
│     Final Report     │  │ [📥 Download All]            │   │
│     €200             │  │                              │   │
│     Due: Nov 7       │  │ Quality Check:               │   │
│                      │  │ ✅ All 5 interviews complete │   │
│  ────────────────    │  │ ✅ Findings documented       │   │
│                      │  │ ✅ On schedule               │   │
│  📊 Activity         │  │                              │   │
│                      │  │ [✅ Approve & Release €800]  │   │
│  Oct 10: Kick-off    │  │ [📝 Request Changes]         │   │
│  Oct 15: Interview 1 │  └──────────────────────────────┘   │
│  Oct 17: Interview 2 │                                      │
│  Oct 20: Interview 3 │  ────────────────────────────────────│
│  Oct 22: Interview 4 │                                      │
│  Oct 24: Interview 5 │  💬 Project Chat                     │
│  Oct 24: Milestone 2 │                                      │
│         submitted    │  Olga (Oct 24, 10:30):               │
│                      │  "Completed all interviews. Key      │
│                      │   finding: Line #2 has 30min RTO     │
│                      │   but no backup power. Recommend?"   │
│                      │                                      │
│                      │  Sergey (Oct 24, 14:15):             │
│                      │  "We have generator but no auto-     │
│                      │   switch. Is manual OK?"             │
│                      │                                      │
│                      │  Olga (Oct 24, 15:00):               │
│                      │  "For 30min RTO, need auto-switch.   │
│                      │   Manual = 15-20min delay. Suggest   │
│                      │   revise RTO to 1 hour OR install    │
│                      │   auto-transfer switch (~€5K)."      │
│                      │                                      │
│                      │  ┌────────────────────────────────┐ │
│                      │  │ [Type your message...]         │ │
│                      │  └────────────────────────────────┘ │
│                      │                                      │
│                      │  [📞 Schedule Call] [📎 Attach File] │
│                      │                                      │
└──────────────────────┴─────────────────────────────────────┘
```

---

## 🔬 JTBD #6: Digital Twin Modeling

### Digital Twin Lab (`/digital-twin`)

```
┌────────────────────────────────────────────────────────────┐
│  LOGO    Twin Status  Scenarios  Simulations  Insights     │
└────────────────────────────────────────────────────────────┘

┌──────────────────────┬─────────────────────────────────────┐
│                      │  🔬 Your Digital Twin                │
│  🏢 Beta Mfg Inc.    │                                      │
│                      │  Status: ✅ Synchronized             │
│  Twin Status:        │  Last Sync: Oct 9, 2025 14:30       │
│  ✅ Active           │  Next Sync: Oct 10, 2025 02:00       │
│                      │                                      │
│  Coverage:           │  ────────────────────────────────────│
│  ████████████ 94%    │                                      │
│                      │  📊 Twin Coverage:                   │
│  Data Sources (5):   │                                      │
│  ✅ ERP              │  ✅ Business Processes: 127 (100%)   │
│  ✅ CMDB             │  ✅ IT Systems: 450 (98%)            │
│  ✅ HR System        │  ✅ Employees: 1,200 (100%)          │
│  ✅ Financial DB     │  ✅ Facilities: 45 (100%)            │
│  ⚠️ Network (95%)    │  ⚠️ Suppliers: 230 (85%)             │
│                      │                                      │
│  ────────────────    │  Twin Accuracy: 94%                  │
│                      │  (validated against real incidents)  │
│  📈 Usage This Mo    │                                      │
│                      │  ────────────────────────────────────│
│  Simulations: 47     │                                      │
│  What-Ifs: 125       │  🎬 Quick Actions:                   │
│  Insights: 18        │                                      │
│                      │  [▶️ Run New Simulation]             │
│  ROI:                │  [🔧 Create Scenario]                │
│  €8.5M insights      │  [📊 View Insights Report]           │
│  from last sim       │  [⚙️ Manage Data Sources]            │
│                      │                                      │
│  ────────────────    │  ────────────────────────────────────│
│                      │                                      │
│  🎯 Scenarios        │  📚 Scenario Library:                │
│                      │                                      │
│  Pre-Built: 15       │  ⭐ Pre-Built Scenarios:             │
│  Custom: 12          │                                      │
│                      │  1. 🔒 Ransomware Attack (IT)        │
│  Recent:             │  2. 🔥 Factory Fire (Physical)       │
│  1. Factory Fire     │  3. 💼 Key Supplier Bankrupt         │
│  2. Cyber DDoS       │  4. 🦠 Pandemic (People)             │
│  3. Supplier Fail    │  5. 🌐 Cyber DDoS Attack             │
│                      │  6. 🌪️ Natural Disaster              │
│                      │  7. ⚡ Power Outage                   │
│                      │  8. 💾 Data Breach                   │
│                      │  9. 🚚 Supply Chain Disruption       │
│                      │  10. 👥 Key Person Loss              │
│                      │                                      │
│                      │  [View All 15 →]                     │
│                      │                                      │
│                      │  💡 Custom Scenarios: 12             │
│                      │                                      │
│                      │  [+ Create New Scenario]             │
│                      │                                      │
└──────────────────────┴─────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  📊 Recent Simulation Results                               │
│                                                              │
│  🔥 Factory Fire - Building A (Run: Oct 5, 2025)           │
│  Impact: $22.5M over 6 months | Recommendation: Dual-source │
│  Savings: $20M (avoided) | Status: IMPLEMENTED ✅           │
│                                                              │
│  [View Full Report →]                                       │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

### Simulation Runner - Active (`/digital-twin/simulation/active`)

```
┌────────────────────────────────────────────────────────────┐
│  🎮 ACTIVE SIMULATION: Factory Fire - Building A            │
│  [⏸️ PAUSED] T+6 hours | Speed: 10x | Checkpoint: Auto     │
└────────────────────────────────────────────────────────────┘

┌──────────────────────┬─────────────────────────────────────┐
│                      │  🔥 Scenario Status                  │
│  🎬 Controls         │                                      │
│                      │  Event: Fire in Building A           │
│  [▶️ Resume]         │  Location: Production Line 2         │
│  [⏸️ Pause]          │  Start: Monday 10:30 AM              │
│  [⏹️ Stop]           │  Elapsed: 6 hours (simulation)       │
│  [⏭️ Skip to +12h]   │  Status: Fire controlled, assessing  │
│                      │                                      │
│  Speed:              │  ────────────────────────────────────│
│  [1x][5x][●10x][50x] │                                      │
│                      │  💰 FINANCIAL IMPACT (Current)       │
│  ────────────────    │                                      │
│                      │  Total Loss: $2.4M                   │
│  💾 Checkpoints      │                                      │
│                      │  ├─ Production stopped: $1.8M        │
│  Auto-save: ON       │  ├─ Building damage: $500K           │
│                      │  └─ Overtime costs: $100K            │
│  ✅ T+0h            │                                      │
│  ✅ T+2h            │  Projected (if continues):           │
│  ✅ T+4h            │  6 months: $22.5M                    │
│  ✅ T+6h (current)  │                                      │
│                      │  ────────────────────────────────────│
│  [💾 Save Now]       │                                      │
│  [📂 Load...]        │  📦 PRODUCTION STATUS                │
│                      │                                      │
│  ────────────────    │  Overall Capacity: 40% (vs 100%)     │
│                      │                                      │
│  📊 Metrics          │  ├─ Line A (Bldg A): ❌ STOPPED     │
│     Tracking         │  ├─ Line B (Bldg A): ❌ STOPPED     │
│                      │  ├─ Line C (Bldg B): ✅ 40% capacity │
│  💰 Financial        │  └─ Line D (Bldg B): ❌ STOPPED      │
│  📦 Production       │      (dependency on Line B)          │
│  👥 People           │                                      │
│  🚨 Customers        │  Revenue Impact: $125K/day lost      │
│  📈 Reputation       │                                      │
│                      │  ────────────────────────────────────│
│                      │                                      │
│                      │  👥 PEOPLE STATUS                    │
│                      │                                      │
│                      │  Total Staff: 450                    │
│                      │                                      │
│                      │  ├─ Building A (evacuated): 180      │
│                      │  │   ├─ Relocated to Bldg B: 90 (50%)│
│                      │  │   ├─ Remote work: 54 (30%)        │
│                      │  │   └─ Idle: 36 (20%)               │
│                      │  │                                   │
│                      │  └─ Other buildings: 270 (operating) │
│                      │                                      │
│                      │  ────────────────────────────────────│
│                      │                                      │
│                      │  🚨 CUSTOMER IMPACT                  │
│                      │                                      │
│                      │  Orders Affected: 245                │
│                      │                                      │
│                      │  ├─ Critical clients: 12             │
│                      │  ├─ Delayed shipments: 200           │
│                      │  └─ Cancelled: 33                    │
│                      │                                      │
│                      │  Reputation: -25% ⚠️                 │
│                      │  Contractual Penalties: $800K est    │
│                      │                                      │
└──────────────────────┴─────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  🔧 WHAT-IF ANALYSIS                                        │
│                                                              │
│  Test different recovery strategies:                         │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Option A: Use Building B only (40% capacity)       │   │
│  │                                                      │   │
│  │ Cost: $0 additional                                 │   │
│  │ Revenue: $45K/day (vs $125K normal)                │   │
│  │ Catch-up time: Never (permanent 60% loss)          │   │
│  │ Customer satisfaction: 30%                          │   │
│  │                                                      │   │
│  │ [Run Simulation →]                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Option B: Outsource production                      │   │
│  │                                                      │   │
│  │ Cost: $2M setup + $200K/month                       │   │
│  │ Timeline: 3 weeks to start                          │   │
│  │ Revenue: $100K/day (80% capacity)                   │   │
│  │ Catch-up time: 9 months                             │   │
│  │ Customer satisfaction: 70%                          │   │
│  │                                                      │   │
│  │ [Run Simulation →]                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ⭐ Option C: Activate Building C (RECOMMENDED)      │   │
│  │                                                      │   │
│  │ Cost: $500K rush setup                              │   │
│  │ Timeline: 2 weeks (vs 2 months planned)             │   │
│  │ Revenue: $110K/day (88% capacity)                   │   │
│  │ Catch-up time: 6 months                             │   │
│  │ Customer satisfaction: 85%                          │   │
│  │                                                      │   │
│  │ 💰 Expected Savings: $15M (vs Option B)             │   │
│  │ 🎯 AI Confidence: 92%                               │   │
│  │                                                      │   │
│  │ [▶️ RUN THIS SIMULATION]                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  [+ Create Custom Option]                                   │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

---

## 🚨 JTBD #7: Crisis Recovery (EMERGENCY)

### Emergency Landing Page (`/crisis/emergency`)

```
┌────────────────────────────────────────────────────────────┐
│              🚨 EMERGENCY RESPONSE MODE 🚨                  │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                                                              │
│                                                              │
│             We understand you're in crisis.                  │
│                                                              │
│         AI will help you recover - RIGHT NOW.                │
│                                                              │
│             ⚡ First 48 hours: FREE ⚡                        │
│                                                              │
│                                                              │
│  What you get immediately (no payment required):             │
│                                                              │
│  ✅ AI crisis plan generated in 5 minutes                   │
│  ✅ Step-by-step recovery guidance                          │
│  ✅ Real-time AI support (unlimited queries)                │
│  ✅ Crisis Command Center access                            │
│  ✅ Expert on-call (optional, first hour FREE)              │
│                                                              │
│  ────────────────────────────────────────────────────────────│
│                                                              │
│  ⏱️ Time is critical. Let's start immediately.              │
│                                                              │
│                                                              │
│            [🚨 ACTIVATE EMERGENCY MODE →]                   │
│                                                              │
│            (No signup required, takes 2 minutes)             │
│                                                              │
│                                                              │
│  ────────────────────────────────────────────────────────────│
│                                                              │
│  💬 "They helped us recover from ransomware in 3.5 hours.    │
│      Saved our company $1.9M. Forever grateful."            │
│      - Anton K., Operations Director                         │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

### Emergency Assessment (`/crisis/emergency/assess`)

```
┌────────────────────────────────────────────────────────────┐
│  ⚡ EMERGENCY CRISIS ASSESSMENT                             │
│  Answer 5 questions (2 minutes) → Get AI recovery plan      │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                                                              │
│  Progress: ████████░░ 80% (Question 4 of 5)                │
│                                                              │
│  ────────────────────────────────────────────────────────────│
│                                                              │
│  Q4: What is your critical priority right now?               │
│                                                              │
│  [Text area - pre-filled from user:]                         │
│  "Restore customer database within 4 hours. All customer     │
│   data encrypted by ransomware 2 hours ago."                │
│                                                              │
│                                                              │
│  🤖 AI detected:                                            │
│  • Crisis type: Ransomware attack (IT)                      │
│  • Time elapsed: 2 hours                                    │
│  • RTO target: 4 hours (2 hours remaining!)                 │
│  • Critical system: Customer database                       │
│  • Severity: CRITICAL (Tier 1)                              │
│                                                              │
│                                                              │
│                                   [← Back]  [Next (Q5) →]    │
│                                                              │
│  ────────────────────────────────────────────────────────────│
│                                                              │
│  ⏱️ Estimated plan generation: 30 seconds after Q5          │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

### AI Emergency Recovery Plan (`/crisis/emergency/plan`)

```
┌────────────────────────────────────────────────────────────┐
│  🤖 AI EMERGENCY RECOVERY PLAN                              │
│  Generated in 47 seconds | Crisis ID: #2025-1009-001        │
└────────────────────────────────────────────────────────────┘

┌──────────────────────┬─────────────────────────────────────┐
│                      │  🚨 CRISIS SUMMARY                   │
│  📋 Plan Navigator   │                                      │
│                      │  Type: Ransomware Attack             │
│  ⚡ IMMEDIATE        │  Target: Customer Database           │
│     (Next 30 min)    │  Time Elapsed: 2 hours               │
│                      │  RTO Target: 4 hours (2h remaining!) │
│  1. ⚠️ Isolate       │  Severity: CRITICAL (Tier 1)        │
│  2. 📞 Notify        │                                      │
│  3. 🔍 Assess        │  ────────────────────────────────────│
│                      │                                      │
│  🔧 SHORT-TERM       │  ⚡ IMMEDIATE ACTIONS                │
│     (30min - 4h)     │     (NEXT 30 MINUTES)                │
│                      │                                      │
│  4. 💾 Restore       │  ┌──────────────────────────────┐   │
│  5. 🛡️ Harden       │  │ 1. ⚠️ ISOLATE SYSTEMS       │   │
│  6. 📢 Communicate   │  │    (URGENT - DO THIS NOW!)   │   │
│                      │  │                              │   │
│  📊 MEDIUM-TERM      │  │ Action: Disconnect network   │   │
│     (4-24h)          │  │ to stop ransomware spread    │   │
│                      │  │                              │   │
│  7. 🔬 Forensics     │  │ Who: IT on-call (calling...) │   │
│  8. 📊 Damage        │  │ How: Run these commands:     │   │
│                      │  │                              │   │
│  🛠️ NEXT STEPS      │  │ [EXACT COMMANDS:]            │   │
│     (24h+)           │  │ ssh firewall.company.com     │   │
│                      │  │ sudo iptables -A INPUT -j    │   │
│  9. 🛠️ Permanent     │  │      DROP                    │   │
│  10. 📋 Review       │  │ sudo iptables -A OUTPUT -j   │   │
│                      │  │      DROP                    │   │
│  ────────────────    │  │                              │   │
│                      │  │ ⏱️ Time limit: 5 minutes     │   │
│  ⏱️ Progress         │  │                              │   │
│                      │  │ ⚠️ If not done: Backup will  │   │
│  [ ] Step 1          │  │    be encrypted (game over!) │   │
│  [ ] Step 2          │  │                              │   │
│  ...                 │  │ [✅ Mark Complete]           │   │
│                      │  │ [🆘 Need Help]               │   │
│  Estimated:          │  │ [❌ Can't Do This]           │   │
│  3h 45min total      │  └──────────────────────────────┘   │
│                      │                                      │
│  On track for RTO ✅ │  ┌──────────────────────────────┐   │
│                      │  │ 2. 📞 NOTIFY STAKEHOLDERS    │   │
│                      │  │                              │   │
│                      │  │ AI Auto-Calling:             │   │
│                      │  │ ✅ CEO (voicemail left)      │   │
│                      │  │ ✅ IT Dir (joined app)       │   │
│                      │  │ ✅ Comms Mgr (answered)      │   │
│                      │  │ ⏳ Legal (calling...)        │   │
│                      │  │                              │   │
│                      │  │ Your task:                   │   │
│                      │  │ Brief team (script below):   │   │
│                      │  │                              │   │
│                      │  │ "Ransomware attack. All      │   │
│                      │  │  servers down. Following     │   │
│                      │  │  AI plan. ETA 4h recovery.   │   │
│                      │  │  IT: Lead recovery           │   │
│                      │  │  Comms: Draft message        │   │
│                      │  │  Legal: Data breach?"        │   │
│                      │  │                              │   │
│                      │  │ [Auto-Send Brief]            │   │
│                      │  └──────────────────────────────┘   │
│                      │                                      │
│                      │  [Expand All Steps →]                │
│                      │                                      │
└──────────────────────┴─────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  🆘 NEED EXPERT HELP?                                       │
│                                                              │
│  Emergency consultants available NOW:                        │
│                                                              │
│  👤 Igor K. - Ransomware Specialist                         │
│  ⭐ 4.9 | 50+ ransomware recoveries                         │
│  💰 €500/hour (FIRST HOUR FREE)                             │
│  📞 Available: NOW (2 min response)                         │
│  [📞 CALL NOW]                                              │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

### Crisis Command Center (`/crisis/active/12345`)

```
┌────────────────────────────────────────────────────────────┐
│  🚨 CRISIS COMMAND CENTER                                   │
│  Crisis #2025-1009-001 | Ransomware Attack | T+3h 25min    │
└────────────────────────────────────────────────────────────┘

┌──────────┬──────────────────┬──────────────────────────────┐
│          │                  │                               │
│  📊 LIVE │  💰 IMPACT       │  🎯 RECOVERY STATUS           │
│  METRICS │                  │                               │
│          │  Current Loss:   │  RTO Target: 4h               │
│  Time:   │  $512K           │  Elapsed: 3h 25min            │
│  3h 25m  │                  │  Remaining: 35 min            │
│          │  Rate:           │                               │
│  RTO:    │  $150K/hour      │  Progress: ██████████████░ 85%│
│  35 min  │                  │                               │
│  left    │  If delayed 1h:  │  Status: ✅ On Track          │
│          │  +$150K          │                               │
│          │                  │  Current Step:                │
│  Team:   │  ────────────    │  Step 4.3: Database restore   │
│  5       │                  │  (90 min remaining)           │
│  active  │  🚨 CUSTOMERS    │                               │
│          │                  │  ────────────────────────────  │
│  Steps:  │  Affected:       │                               │
│  8/10    │  3,200           │  🤖 AI COMMANDER              │
│          │                  │                               │
│          │  Notified:       │  Current Recommendations:     │
│          │  ✅ Yes          │                               │
│          │                  │  ✅ Network isolated          │
│          │  Satisfaction:   │  ✅ Team activated            │
│          │  72% (ok)        │  🔄 Restore in progress       │
│          │                  │  ⏳ Next: Validate data       │
│          │                  │                               │
│          │                  │  PREDICTIONS:                 │
│          │                  │  • 85% chance RTO met         │
│          │  • Impact: $512K │  • Final loss: ~$520K         │
│          │                  │  • Reputation: Minor (-5%)    │
│          │                  │                               │
│          │                  │  [Get AI Advice]              │
│          │                  │                               │
└──────────┴──────────────────┴──────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  📋 RECOVERY CHECKLIST (Live)                               │
│                                                              │
│  ✅ 1. Isolate systems (Completed 00:04 - 4 min)            │
│  ✅ 2. Notify stakeholders (Completed 00:15 - 15 min)       │
│  ✅ 3. Assess backups (Completed 00:25 - 10 min)            │
│  🔄 4. Restore from backup (In Progress 01:35 - 90 min)     │
│     ├─ ✅ 4.1 Prepare clean server (45 min)                 │
│     ├─ ✅ 4.2 Mount backup tape (15 min)                    │
│     ├─ 🔄 4.3 Restore database (35 min elapsed, 55 left)    │
│     └─ ⏳ 4.4 Validate integrity                            │
│  ⏳ 5. Harden systems                                        │
│  ⏳ 6. Communicate recovery                                  │
│                                                              │
│  ────────────────────────────────────────────────────────────│
│                                                              │
│  💬 TEAM CHAT (Real-time)                                   │
│                                                              │
│  [15:30] IT Director: "Restore 60% complete, looking good"  │
│  [15:32] AI: "Excellent progress. Prepare validation team." │
│  [15:35] BCM Mgr: "Legal says no breach notification yet"   │
│  [15:37] You: "Comms, draft recovery announcement"          │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │ [Type message...]                                  │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ────────────────────────────────────────────────────────────│
│                                                              │
│  📊 DECISION LOG (Audit Trail)                              │
│                                                              │
│  [00:04] DECISION: Isolate network (AI recommended) ✅      │
│  [00:15] DECISION: Use backup tape (not cloud) ✅           │
│  [00:25] DECISION: Accept 3h data loss ✅                   │
│  [01:35] DECISION: Start restore (validated tape) ✅        │
│                                                              │
│  All decisions timestamped and logged for audit              │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

---

## 📊 SUMMARY: UI Implementation Priorities

### Phase 1: MVP (3 months)
1. **JTBD #1**: Certification Dashboard + BIA Wizard
2. **JTBD #7**: Emergency Response (viral growth!)
3. Basic Marketplace (auditor listings)

### Phase 2: Marketplace (3 months)
4. **JTBD #5**: Full marketplace (services, projects)
5. **JTBD #2**: Auditor AI tools (document analysis)

### Phase 3: Learning & Premium (6 months)
6. **JTBD #3**: Learning platform (courses, cases, sandbox)
7. **JTBD #6**: Digital Twin Lab (premium tier)

---

**Status**: ✅ COMPLETE - Ready for Mockup/Development
**Next Action**: Create Figma mockups based on these specifications
**Expected Impact**: 10x conversion, service-driven UX, clear value prop

