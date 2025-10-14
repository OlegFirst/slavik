# Learning Service - Frontend Technical Specification

**Version:** 1.0
**Date:** 2025-10-01
**Target Framework:** React 18+ / Next.js 14+
**Backend API:** Learning Service (Port 8021)

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Page Structure](#page-structure)
3. [Component Specifications](#component-specifications)
4. [UI/UX Design System](#uiux-design-system)
5. [State Management](#state-management)
6. [API Integration](#api-integration)
7. [Wireframes](#wireframes)
8. [Technical Requirements](#technical-requirements)
9. [Gamification UI](#gamification-ui)

---

## 🏗️ Architecture Overview

### Frontend Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           React 18 / Next.js 14 App Router          │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│       ┌──────────────────┴──────────────────┐              │
│       │                                     │              │
│  ┌────▼─────┐                         ┌────▼──────┐       │
│  │  Pages   │                         │ Components│       │
│  │/learning │                         │ Library   │       │
│  │/training │                         │ Shared UI │       │
│  │/competency│                        │Gamification│      │
│  └──────────┘                         └───────────┘       │
│       │                                                    │
│  ┌────▼──────────────────────────────────────┐           │
│  │     State Management (Zustand)            │           │
│  │  - trainingStore                          │           │
│  │  - competencyStore                        │           │
│  │  - gamificationStore                      │           │
│  │  - userProgressStore                      │           │
│  └───────────────────────────────────────────┘           │
│       │                                                    │
│  ┌────▼──────────────────────────────────────┐           │
│  │     API Client (Axios/Fetch)              │           │
│  │  - learningApi.ts                         │           │
│  └───────────────────────────────────────────┘           │
│       │                                                    │
│  ┌────▼──────────────────────────────────────┐           │
│  │     Learning Service REST API             │           │
│  │     http://localhost:8021/api/learning    │           │
│  └───────────────────────────────────────────┘           │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### Recommended Tech Stack

**Core:**
- **Framework:** Next.js 14+ (App Router)
- **Language:** TypeScript 5+
- **Styling:** Tailwind CSS 3+ + shadcn/ui components
- **State:** Zustand (lightweight state management)
- **Forms:** React Hook Form + Zod validation
- **API:** Axios with interceptors
- **Charts:** Recharts (for progress charts)
- **Tables:** TanStack Table v8
- **Rich Text:** TipTap (for training content)
- **Date:** date-fns
- **Icons:** Lucide React

**Additional:**
- **Video Player:** react-player (for training videos)
- **PDF Viewer:** react-pdf (for training materials)
- **Notifications:** react-hot-toast
- **Confetti:** canvas-confetti (for achievements)
- **Progress:** react-circular-progressbar
- **Badges:** Custom SVG components

---

## 📄 Page Structure

### Navigation Hierarchy

```
BCM Platform
└── Learning & Development
    ├── 📊 Dashboard (My Learning Home)
    ├── 🎓 Training Programs
    │   ├── Browse Catalog
    │   ├── My Enrollments
    │   ├── Program Detail
    │   └── Training Player
    ├── 📈 Competency Management
    │   ├── My Competencies
    │   ├── Gap Analysis
    │   ├── Development Plan
    │   └── Evidence Upload
    ├── 📢 Awareness Campaigns
    │   ├── Active Campaigns
    │   ├── Campaign Calendar
    │   └── Participation Tracking
    ├── 🏆 Gamification
    │   ├── My Achievements
    │   ├── Leaderboard
    │   ├── Points History
    │   └── Badges Collection
    └── 📊 Reports (Admin)
        ├── Training Analytics
        ├── Competency Dashboard
        ├── Compliance Reports
        └── ROI Analysis
```

---

## 📄 Detailed Page Specifications

### 1. Learning Dashboard (My Learning Home)

**Route:** `/learning`
**Purpose:** Central hub for learner's training journey
**User Roles:** All authenticated users

#### Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│  🎓 My Learning Dashboard                    👤 John Doe    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  🏆 Gamification Header                              │  │
│  │  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌────────┐ │  │
│  │  │ Level 4 │  │ 2,350 pts│  │ 🔥 15   │  │ 12/19  │ │  │
│  │  │Profess. │  │          │  │ streak  │  │badges  │ │  │
│  │  └─────────┘  └──────────┘  └─────────┘  └────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌────────────────────┐  ┌────────────────────────────┐   │
│  │ Continue Learning  │  │   Upcoming Deadlines       │   │
│  ├────────────────────┤  ├────────────────────────────┤   │
│  │ ▶ BCM Fundamentals │  │ ⏰ ISO 22301 Exam          │   │
│  │   Progress: 67%    │  │    Due in 3 days           │   │
│  │   [Continue]       │  │                            │   │
│  │                    │  │ 📋 Quarterly Assessment    │   │
│  │ ▶ Incident Response│  │    Due in 12 days          │   │
│  │   Progress: 23%    │  │                            │   │
│  │   [Continue]       │  └────────────────────────────┘   │
│  └────────────────────┘                                    │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 📚 Recommended for You                               │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │ [Card] Crisis Communications    [Card] Risk Mgmt     │  │
│  │ 4 hrs | Intermediate             6 hrs | Advanced    │  │
│  │ [Enroll]                         [Enroll]            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 📊 My Progress Overview                              │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │ Completed: 8 courses  |  In Progress: 2             │  │
│  │ Certifications: 3     |  Competency Score: 78%      │  │
│  │ [View Detailed Analytics]                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 🎯 Competency Gaps                                   │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │ ⚠️ Incident Response: Intermediate → Advanced        │  │
│  │    [View Training Plan]                              │  │
│  │                                                       │  │
│  │ ⚠️ Business Impact Analysis: Basic → Intermediate    │  │
│  │    [View Training Plan]                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

#### Components Needed

1. **GamificationHeader**
   - Level badge with progress ring
   - Points counter with animation
   - Streak flame icon with counter
   - Achievements/badges progress

2. **ContinueLearningCard**
   - Training thumbnail
   - Progress bar (0-100%)
   - Last module indicator
   - Estimated time remaining
   - "Continue" CTA button

3. **DeadlineWidget**
   - Countdown timer
   - Priority indicator (urgent/soon/upcoming)
   - Direct link to training/assessment

4. **RecommendationCard**
   - Training thumbnail
   - Duration, level, rating
   - "Why recommended" tooltip
   - Enroll button

5. **ProgressSummaryPanel**
   - Metrics cards (completed, in progress, certified)
   - Sparkline charts
   - Link to detailed analytics

6. **CompetencyGapAlert**
   - Gap severity indicator
   - Current vs required level
   - Recommended training path
   - Action button

---

### 2. Training Programs Catalog

**Route:** `/learning/programs`
**Purpose:** Browse and search available training programs

#### Layout

```
┌─────────────────────────────────────────────────────────────┐
│  🎓 Training Programs                    🔍 [Search...]     │
├─────────────────────────────────────────────────────────────┤
│  Filters:                                                   │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ All Levels ▼│  │ All Types   ▼│  │ Sort: Popular  ▼│   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐│
│  │ 📚 BCM Fundamental Awareness                           ││
│  │ ⭐⭐⭐⭐⭐ 4.8 (256 reviews)                              ││
│  │ ⏱ 2 hours  |  📊 Basic Awareness  |  🎓 Certification  ││
│  │ Description: Introduction to Business Continuity...    ││
│  │ [View Details]  [Enroll Now]                           ││
│  └────────────────────────────────────────────────────────┘│
│                                                             │
│  ┌────────────────────────────────────────────────────────┐│
│  │ 🚨 Incident Response Advanced                          ││
│  │ ⭐⭐⭐⭐ 4.6 (128 reviews)                               ││
│  │ ⏱ 16 hours  |  📊 Advanced  |  🎓 ISO 22301 Aligned   ││
│  │ Description: Comprehensive incident management...      ││
│  │ [View Details]  [Enroll Now]                           ││
│  └────────────────────────────────────────────────────────┘│
│                                                             │
│  [Load More...]                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Components

1. **TrainingCatalogFilters**
   - Multi-select filters (level, type, duration)
   - Search autocomplete
   - Sort dropdown
   - Active filters chips

2. **ProgramCard**
   - Thumbnail/icon
   - Rating stars + count
   - Metadata (duration, level, certification)
   - Description preview
   - Enrollment status badge
   - Action buttons

3. **ProgramDetailModal**
   - Full description
   - Curriculum outline
   - Learning objectives
   - Prerequisites
   - Instructor info
   - Reviews section
   - Enrollment form

---

### 3. Training Player (Learning Experience)

**Route:** `/learning/programs/{id}/learn`
**Purpose:** Immersive training delivery interface

#### Layout

```
┌─────────────────────────────────────────────────────────────┐
│  [← Back]  BCM Fundamentals > Module 2: Risk Assessment    │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────┐                                             │
│  │ SIDEBAR    │  ┌────────────────────────────────────┐    │
│  │            │  │                                    │    │
│  │ ✅ Intro   │  │     📹 Video Content Area          │    │
│  │ ▶️ Risk    │  │                                    │    │
│  │   Assessment│  │     [Video Player]                │    │
│  │ ⭕ BIA      │  │                                    │    │
│  │ ⭕ Testing  │  │                                    │    │
│  │ ⭕ Quiz     │  │                                    │    │
│  │            │  └────────────────────────────────────┘    │
│  │            │                                             │
│  │            │  ┌────────────────────────────────────┐    │
│  │ Progress:  │  │ 📝 Lesson Notes                    │    │
│  │ ████░░ 67% │  │ - Key point 1                      │    │
│  │            │  │ - Key point 2                      │    │
│  │ 🏆 +50 pts │  │ [Download PDF]                     │    │
│  │   on finish│  └────────────────────────────────────┘    │
│  └────────────┘                                             │
│                  [< Previous]  [Mark Complete]  [Next >]    │
└─────────────────────────────────────────────────────────────┘
```

#### Components

1. **CurriculumSidebar**
   - Module list with completion status
   - Progress bar
   - Points preview
   - Collapsible sections

2. **ContentPlayer**
   - Video player with controls
   - PDF viewer
   - Interactive quiz renderer
   - SCORM content iframe

3. **LessonNotes**
   - Collapsible notes panel
   - Download/print option
   - Key takeaways
   - Additional resources links

4. **NavigationControls**
   - Previous/Next buttons
   - "Mark Complete" button
   - Progress auto-save indicator

---

### 4. Competency Management Dashboard

**Route:** `/learning/competency`
**Purpose:** View and manage competency assessments

#### Layout

```
┌─────────────────────────────────────────────────────────────┐
│  📈 My Competency Profile                    [+ New Self-Assessment]│
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 📊 Competency Overview                               │   │
│  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐│   │
│  │ │   78%    │ │    5     │ │    2     │ │   93%    ││   │
│  │ │ Overall  │ │ Advanced │ │   Gaps   │ │ On track ││   │
│  │ └──────────┘ └──────────┘ └──────────┘ └──────────┘│   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🎯 Competency Areas                                  │   │
│  ├────────────────────┬─────────┬──────────┬───────────┤   │
│  │ Area               │ Current │ Required │ Status    │   │
│  ├────────────────────┼─────────┼──────────┼───────────┤   │
│  │ Incident Response  │ Interm. │ Advanced │ ⚠️ Gap    │   │
│  │ [Progress: ████░░░ 60%]      │ [View Plan]          │   │
│  ├────────────────────┼─────────┼──────────┼───────────┤   │
│  │ Risk Assessment    │ Advanced│ Advanced │ ✅ Met    │   │
│  │ [Progress: ██████ 100%]      │ [Maintain]           │   │
│  ├────────────────────┼─────────┼──────────┼───────────┤   │
│  │ Business Continuity│ Basic   │ Interm.  │ ⚠️ Gap    │   │
│  │ [Progress: ██░░░░ 30%]       │ [View Plan]          │   │
│  └────────────────────┴─────────┴──────────┴───────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 📋 Development Plan                                  │   │
│  │ ✅ Complete "Advanced Incident Response" (In progress)│  │
│  │ 📅 Scheduled: BCP Fundamentals - Nov 15              │   │
│  │ 📚 Recommended: ISO 22301 Certification Course       │   │
│  │ [View Full Development Plan]                         │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

#### Components

1. **CompetencyOverviewCards**
   - Metric cards with icons
   - Circular progress indicators
   - Trend arrows (improving/declining)

2. **CompetencyMatrix Table**
   - Sortable/filterable table
   - Status badges (met/gap/in-progress)
   - Progress bars per row
   - Action buttons (View Plan, Add Evidence)

3. **DevelopmentPlanTimeline**
   - Vertical timeline layout
   - Status icons (completed/in-progress/scheduled)
   - Due dates
   - Quick actions

4. **GapAnalysisChart**
   - Radar chart showing competencies
   - Current vs Required overlay
   - Interactive tooltips

---

### 5. Gamification Hub

**Route:** `/learning/achievements`
**Purpose:** Showcase achievements, points, and leaderboard

#### Layout

```
┌─────────────────────────────────────────────────────────────┐
│  🏆 Achievements & Rewards                                  │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Your Progress                                        │   │
│  │ ┌────────────────────────────────────────────────┐  │   │
│  │ │  Level 4: Professional    [████████░░] 82%     │  │   │
│  │ │  2,350 / 2,500 points to Level 5: Expert       │  │   │
│  │ └────────────────────────────────────────────────┘  │   │
│  │                                                      │   │
│  │ 🔥 Current Streak: 15 days    🏅 Total Badges: 12/19│  │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🎖️ Recent Achievements                               │   │
│  │ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                     │   │
│  │ │ 🏆  │ │ 🌟  │ │ 🎯  │ │ 📚  │                     │   │
│  │ │First│ │Streak│ │Gap  │ │Master│                    │   │
│  │ │Cert │ │  7  │ │Closer│ │Level │                    │   │
│  │ │+500 │ │ +50 │ │ +200│ │ +150 │                    │   │
│  │ └─────┘ └─────┘ └─────┘ └─────┘                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 📊 Leaderboard (This Month)                          │   │
│  ├──────┬─────────────────────┬──────────┬──────────┐  │   │
│  │ Rank │ Name                │ Points   │ Level    │  │   │
│  ├──────┼─────────────────────┼──────────┼──────────┤  │   │
│  │ 🥇 1 │ Sarah Johnson       │ 4,250    │ Expert   │  │   │
│  │ 🥈 2 │ Mike Chen           │ 3,890    │ Expert   │  │   │
│  │ 🥉 3 │ Emily Rodriguez     │ 3,120    │ Pro      │  │   │
│  │ ... 4│ Ahmed Al-Farsi      │ 2,890    │ Pro      │  │   │
│  │ ➡️ 5 │ You - John Doe      │ 2,350    │ Pro      │  │   │
│  │    6 │ Lisa Anderson       │ 2,100    │ Pract.   │  │   │
│  │    7 │ David Kim           │ 1,950    │ Pract.   │  │   │
│  └──────┴─────────────────────┴──────────┴──────────┘  │   │
│  [View Full Leaderboard]                                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🎁 Available Badges (7 more to unlock)               │   │
│  │ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐            │   │
│  │ │ 🔒  │ │ 🔒  │ │ 🔒  │ │ 🔒  │ │ 🔒  │            │   │
│  │ │30Day│ │Team │ │Mentor│ │ISO  │ │Perfect│           │   │
│  │ │Streak│ │Player│ │     │ │Cert │ │Score │            │   │
│  │ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘            │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

#### Components

1. **LevelProgressBar**
   - Animated progress bar
   - Current level badge
   - Points to next level
   - Level up animation

2. **StreakCounter**
   - Flame icon with animation
   - Streak count
   - Calendar heatmap (optional)
   - Streak milestones

3. **AchievementCard**
   - Badge icon (earned/locked)
   - Achievement name
   - Points value
   - Unlock criteria
   - Earned date
   - Celebration animation on unlock

4. **LeaderboardTable**
   - Rank with medals (top 3)
   - User avatars
   - Points and level
   - Highlight current user
   - Time period filter

5. **BadgeCollection**
   - Grid layout
   - Locked/unlocked states
   - Hover tooltips
   - Progress bars for partial achievements

---

### 6. Awareness Campaigns

**Route:** `/learning/campaigns`
**Purpose:** Track awareness campaigns participation

#### Layout

```
┌─────────────────────────────────────────────────────────────┐
│  📢 Awareness Campaigns                   [Filter: Active ▼]│
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🔴 ACTIVE  BCM Awareness Week 2024                   │   │
│  │ Oct 1-7, 2024  |  Target: All Staff                  │   │
│  │                                                       │   │
│  │ Your Participation:  ████░░░ 67%                     │   │
│  │ ✅ Attended Kickoff Webinar                          │   │
│  │ ✅ Completed Quiz                                    │   │
│  │ ⭕ Pending: Tabletop Exercise (Oct 5)                │   │
│  │                                                       │   │
│  │ [View Campaign Details]  [Complete Activities]       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🟡 UPCOMING  Cybersecurity Awareness                 │   │
│  │ Oct 15-22, 2024  |  Target: IT Department            │   │
│  │ [Register Interest]  [View Details]                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ ✅ COMPLETED  Pandemic Preparedness                  │   │
│  │ Sep 1-15, 2024  |  Participation: 100%               │   │
│  │ [View Certificate]  [View Materials]                 │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

#### Components

1. **CampaignCard**
   - Status badge (active/upcoming/completed)
   - Date range
   - Target audience
   - Participation progress
   - Activity checklist
   - Action buttons

2. **CampaignCalendar**
   - Monthly view
   - Campaign markers
   - Hover tooltips
   - Click to filter

3. **ParticipationTracker**
   - Activity checklist
   - Completion percentage
   - Points earned
   - Certificate download

---

## 🎨 UI/UX Design System

### Color Palette

**Learning Theme Colors:**
```css
/* Primary - Educational Blue */
--learning-primary: #3B82F6;       /* Blue 500 */
--learning-primary-hover: #2563EB; /* Blue 600 */
--learning-primary-light: #DBEAFE; /* Blue 100 */

/* Success - Achievement Green */
--success: #10B981;                /* Emerald 500 */
--success-light: #D1FAE5;          /* Emerald 100 */

/* Warning - Gap/Urgent Orange */
--warning: #F59E0B;                /* Amber 500 */
--warning-light: #FEF3C7;          /* Amber 100 */

/* Gamification - Gold/Trophy */
--gold: #FBBF24;                   /* Amber 400 */
--silver: #94A3B8;                 /* Slate 400 */
--bronze: #CD7F32;                 /* Bronze */

/* Levels */
--level-beginner: #6B7280;         /* Gray 500 */
--level-learner: #3B82F6;          /* Blue 500 */
--level-practitioner: #8B5CF6;     /* Violet 500 */
--level-professional: #EC4899;     /* Pink 500 */
--level-expert: #EF4444;           /* Red 500 */
--level-master: #7C3AED;           /* Purple 600 */
--level-champion: #F59E0B;         /* Amber 500 */

/* Competency Levels */
--comp-basic: #93C5FD;             /* Blue 300 */
--comp-intermediate: #60A5FA;      /* Blue 400 */
--comp-advanced: #3B82F6;          /* Blue 500 */
--comp-expert: #1D4ED8;            /* Blue 700 */

/* Neutrals */
--gray-50: #F9FAFB;
--gray-100: #F3F4F6;
--gray-200: #E5E7EB;
--gray-600: #4B5563;
--gray-900: #111827;
```

### Typography

```css
/* Headings */
h1 { font-size: 2rem; font-weight: 700; } /* Dashboard titles */
h2 { font-size: 1.5rem; font-weight: 600; } /* Section headers */
h3 { font-size: 1.25rem; font-weight: 600; } /* Card titles */

/* Body */
body { font-size: 1rem; line-height: 1.5; }
.text-sm { font-size: 0.875rem; } /* Metadata */
.text-xs { font-size: 0.75rem; } /* Labels */

/* Font Families */
--font-sans: 'Inter', system-ui, sans-serif;
--font-display: 'Cal Sans', 'Inter', sans-serif; /* For gamification */
```

### Icons

**Lucide React Icons:**
- 🎓 `GraduationCap` - Training
- 📊 `BarChart3` - Competency
- 🏆 `Trophy` - Achievements
- 🎯 `Target` - Goals
- 📢 `Megaphone` - Campaigns
- ⚡ `Zap` - Streak
- 🌟 `Star` - Rating
- 📚 `BookOpen` - Catalog
- ✅ `CheckCircle` - Completed
- 🔒 `Lock` - Locked
- 🔥 `Flame` - Streak
- 📈 `TrendingUp` - Progress

### Component Variants

**Buttons:**
```tsx
// Primary CTA
<Button variant="primary" size="lg">Enroll Now</Button>

// Secondary
<Button variant="secondary">View Details</Button>

// Success (Achievement)
<Button variant="success">Claim Badge</Button>

// Outline
<Button variant="outline">Learn More</Button>
```

**Badges:**
```tsx
// Status
<Badge variant="success">Completed</Badge>
<Badge variant="warning">In Progress</Badge>
<Badge variant="info">Enrolled</Badge>

// Level
<Badge variant="level-expert">Expert</Badge>

// Achievement
<Badge variant="gold">🏆 New!</Badge>
```

**Progress Bars:**
```tsx
// Standard
<Progress value={67} className="h-2" />

// With label
<Progress value={67} label="67% Complete" />

// Multi-color (competency)
<Progress value={80} variant="competency" level="advanced" />
```

---

## 🔄 State Management

### Zustand Store Structure

#### 1. Training Store

```typescript
// stores/trainingStore.ts

interface TrainingState {
  // Enrollments
  enrollments: Enrollment[];
  currentEnrollment: Enrollment | null;
  enrollmentLoading: boolean;

  // Programs
  programs: TrainingProgram[];
  programsFilter: ProgramFilter;

  // Learning Player
  currentModule: Module | null;
  playerProgress: PlayerProgress;

  // Actions
  fetchEnrollments: () => Promise<void>;
  enrollInProgram: (programId: number) => Promise<void>;
  updateProgress: (enrollmentId: number, progress: number) => Promise<void>;
  completeModule: (moduleId: number) => Promise<void>;
  submitAssessment: (enrollmentId: number, score: number) => Promise<void>;
}

const useTrainingStore = create<TrainingState>((set, get) => ({
  enrollments: [],
  currentEnrollment: null,
  enrollmentLoading: false,
  programs: [],
  programsFilter: {
    level: null,
    type: null,
    search: ''
  },
  currentModule: null,
  playerProgress: {
    currentTime: 0,
    duration: 0,
    completed: false
  },

  fetchEnrollments: async () => {
    set({ enrollmentLoading: true });
    const data = await learningApi.getEnrollments();
    set({ enrollments: data, enrollmentLoading: false });
  },

  enrollInProgram: async (programId) => {
    const enrollment = await learningApi.enrollInProgram(programId);
    set(state => ({
      enrollments: [...state.enrollments, enrollment]
    }));
  },

  updateProgress: async (enrollmentId, progress) => {
    await learningApi.updateProgress(enrollmentId, progress);
    set(state => ({
      enrollments: state.enrollments.map(e =>
        e.id === enrollmentId ? { ...e, progress_percentage: progress } : e
      )
    }));
  },

  // ... more actions
}));
```

#### 2. Competency Store

```typescript
// stores/competencyStore.ts

interface CompetencyState {
  assessments: CompetencyAssessment[];
  gaps: CompetencyGap[];
  developmentPlan: DevelopmentPlanItem[];
  loading: boolean;

  // Actions
  fetchAssessments: () => Promise<void>;
  fetchGaps: () => Promise<void>;
  createAssessment: (data: CompetencyAssessmentCreate) => Promise<void>;
  closeGap: (assessmentId: number, evidence: Evidence) => Promise<void>;
}

const useCompetencyStore = create<CompetencyState>((set) => ({
  assessments: [],
  gaps: [],
  developmentPlan: [],
  loading: false,

  fetchAssessments: async () => {
    set({ loading: true });
    const data = await learningApi.getCompetency();
    set({ assessments: data, loading: false });
  },

  fetchGaps: async () => {
    const gaps = await learningApi.getCompetencyGaps();
    set({ gaps });
  },

  createAssessment: async (data) => {
    const assessment = await learningApi.createCompetency(data);
    set(state => ({
      assessments: [...state.assessments, assessment]
    }));
  },

  closeGap: async (assessmentId, evidence) => {
    await learningApi.closeGap(assessmentId, evidence);
    await get().fetchGaps(); // Refresh
  }
}));
```

#### 3. Gamification Store

```typescript
// stores/gamificationStore.ts

interface GamificationState {
  userLevel: UserLevel;
  achievements: Achievement[];
  leaderboard: LeaderboardEntry[];
  streak: StreakData;
  loading: boolean;

  // Actions
  fetchUserLevel: (personId: string) => Promise<void>;
  fetchAchievements: (personId: string) => Promise<void>;
  fetchLeaderboard: (limit?: number) => Promise<void>;
  fetchStreak: (personId: string) => Promise<void>;
  awardPoints: (action: string, context: any) => Promise<void>;
}

const useGamificationStore = create<GamificationState>((set) => ({
  userLevel: null,
  achievements: [],
  leaderboard: [],
  streak: null,
  loading: false,

  fetchUserLevel: async (personId) => {
    const level = await learningApi.getUserLevel(personId);
    set({ userLevel: level });
  },

  fetchAchievements: async (personId) => {
    const achievements = await learningApi.getAchievements(personId);
    set({ achievements });
  },

  fetchLeaderboard: async (limit = 10) => {
    const leaderboard = await learningApi.getLeaderboard(limit);
    set({ leaderboard });
  },

  fetchStreak: async (personId) => {
    const streak = await learningApi.getStreak(personId);
    set({ streak });
  },

  awardPoints: async (action, context) => {
    await learningApi.awardPoints(action, context);
    // Refresh user level and achievements
    await Promise.all([
      get().fetchUserLevel(context.person_id),
      get().fetchAchievements(context.person_id)
    ]);
  }
}));
```

#### 4. User Progress Store (Computed)

```typescript
// stores/userProgressStore.ts

interface UserProgressState {
  // Computed metrics
  completedCount: number;
  inProgressCount: number;
  certificationCount: number;
  overallProgress: number;

  // Derived from other stores
  calculateMetrics: () => void;
}

const useUserProgressStore = create<UserProgressState>((set) => ({
  completedCount: 0,
  inProgressCount: 0,
  certificationCount: 0,
  overallProgress: 0,

  calculateMetrics: () => {
    const { enrollments } = useTrainingStore.getState();

    const completed = enrollments.filter(e => e.status === 'CERTIFIED').length;
    const inProgress = enrollments.filter(e => e.status === 'IN_PROGRESS').length;
    const certified = enrollments.filter(e => e.certification_issued).length;

    const overall = enrollments.length > 0
      ? enrollments.reduce((sum, e) => sum + e.progress_percentage, 0) / enrollments.length
      : 0;

    set({
      completedCount: completed,
      inProgressCount: inProgress,
      certificationCount: certified,
      overallProgress: overall
    });
  }
}));
```

---

## 🔌 API Integration

### API Client Setup

```typescript
// lib/learningApi.ts

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_LEARNING_API_URL || 'http://localhost:8021';
const TENANT_ID = process.env.NEXT_PUBLIC_TENANT_ID || 'demo';

const client = axios.create({
  baseURL: `${API_BASE_URL}/api/learning`,
  headers: {
    'Content-Type': 'application/json',
  },
  params: {
    tenant_id: TENANT_ID, // Auto-include in all requests
  },
});

// Interceptor for auth token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor for error handling
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const learningApi = {
  // =====================================================
  // TRAINING PROGRAMS
  // =====================================================

  // Get all training programs
  getPrograms: (filters?: ProgramFilters) =>
    client.get<TrainingProgram[]>('/programs', { params: filters })
      .then(res => res.data),

  // Get single program
  getProgram: (id: number) =>
    client.get<TrainingProgram>(`/programs/${id}`)
      .then(res => res.data),

  // Create program (admin)
  createProgram: (data: ProgramCreate) =>
    client.post<TrainingProgram>('/programs', data)
      .then(res => res.data),

  // =====================================================
  // TRAINING ENROLLMENTS
  // =====================================================

  // Get user's enrollments
  getEnrollments: (filters?: EnrollmentFilters) =>
    client.get<Enrollment[]>('/enrollments', { params: filters })
      .then(res => res.data),

  // Enroll in program
  enrollInProgram: (data: EnrollmentCreate) =>
    client.post<Enrollment>('/enrollments', data)
      .then(res => res.data),

  // Start training
  startTraining: (enrollmentId: number) =>
    client.post<Enrollment>(`/enrollments/${enrollmentId}/start`)
      .then(res => res.data),

  // Update progress
  updateProgress: (enrollmentId: number, progress: number) =>
    client.patch<Enrollment>(`/enrollments/${enrollmentId}/progress`, {
      progress_percentage: progress
    }).then(res => res.data),

  // Complete training
  completeTraining: (enrollmentId: number) =>
    client.post<Enrollment>(`/enrollments/${enrollmentId}/complete`)
      .then(res => res.data),

  // Submit assessment
  submitAssessment: (enrollmentId: number, score: number) =>
    client.post<Enrollment>(`/enrollments/${enrollmentId}/assess`, {
      assessment_score: score
    }).then(res => res.data),

  // Issue certification
  issueCertification: (enrollmentId: number) =>
    client.post<Enrollment>(`/enrollments/${enrollmentId}/certify`)
      .then(res => res.data),

  // =====================================================
  // COMPETENCY MANAGEMENT
  // =====================================================

  // Get competency assessments
  getCompetency: (filters?: CompetencyFilters) =>
    client.get<CompetencyAssessment[]>('/competency', { params: filters })
      .then(res => res.data),

  // Create assessment
  createCompetency: (data: CompetencyAssessmentCreate) =>
    client.post<CompetencyAssessment>('/competency', data)
      .then(res => res.data),

  // Get gap analysis
  getCompetencyGaps: (filters?: { person_id?: string }) =>
    client.get<CompetencyGap[]>('/competency/gaps', { params: filters })
      .then(res => res.data),

  // Close gap
  closeGap: (assessmentId: number, data: CloseGapRequest) =>
    client.patch<CompetencyAssessment>(`/competency/${assessmentId}/close-gap`, data)
      .then(res => res.data),

  // =====================================================
  // AWARENESS CAMPAIGNS
  // =====================================================

  // Get campaigns
  getCampaigns: (filters?: CampaignFilters) =>
    client.get<AwarenessCampaign[]>('/campaigns', { params: filters })
      .then(res => res.data),

  // Create campaign (admin)
  createCampaign: (data: CampaignCreate) =>
    client.post<AwarenessCampaign>('/campaigns', data)
      .then(res => res.data),

  // Update campaign
  updateCampaign: (id: number, data: CampaignUpdate) =>
    client.patch<AwarenessCampaign>(`/campaigns/${id}`, data)
      .then(res => res.data),

  // =====================================================
  // GAMIFICATION
  // =====================================================

  // Award points
  awardPoints: (data: AwardPointsRequest) =>
    client.post('/gamification/award-points', data)
      .then(res => res.data),

  // Get leaderboard
  getLeaderboard: (limit: number = 10) =>
    client.get<LeaderboardEntry[]>('/gamification/leaderboard', {
      params: { limit }
    }).then(res => res.data),

  // Get user achievements
  getAchievements: (personId: string) =>
    client.get<UserAchievement[]>(`/gamification/achievements/${personId}`)
      .then(res => res.data),

  // Get user streak
  getStreak: (personId: string) =>
    client.get<StreakData>(`/gamification/streak/${personId}`)
      .then(res => res.data),

  // Get user level
  getUserLevel: (personId: string) =>
    client.get<UserLevel>(`/gamification/level/${personId}`)
      .then(res => res.data),

  // =====================================================
  // TEMPLATES
  // =====================================================

  // Get training templates
  getTemplates: (filters?: TemplateFilters) =>
    client.get<TrainingTemplate[]>('/templates', { params: filters })
      .then(res => res.data),
};
```

### TypeScript Types

```typescript
// types/learning.ts

export interface TrainingProgram {
  id: number;
  tenant_id: string;
  program_code: string;
  program_name: string;
  program_type: ProgramType;
  bci_training_level: BCITrainingLevel;
  duration_hours: number;
  learning_objectives: string[];
  curriculum: CurriculumItem[];
  prerequisites: string[];
  assessment_required: boolean;
  passing_score: number;
  certification_awarded: boolean;
  status: ProgramStatus;
  created_at: string;
  updated_at: string;
}

export type ProgramType =
  | 'bcm_awareness'
  | 'role_based'
  | 'technical_skills'
  | 'incident_response'
  | 'crisis_management'
  | 'certification_prep'
  | 'compliance_training'
  | 'leadership';

export type BCITrainingLevel =
  | 'basic_awareness'
  | 'intermediate'
  | 'advanced'
  | 'specialist'
  | 'leadership';

export type ProgramStatus =
  | 'draft'
  | 'published'
  | 'archived';

export interface Enrollment {
  id: number;
  tenant_id: string;
  program_id: number;
  person_id: string;
  person_name: string;
  person_email: string;
  department: string;
  status: EnrollmentStatus;
  enrolled_at: string;
  started_at?: string;
  completed_at?: string;
  certified_at?: string;
  progress_percentage: number;
  modules_completed: string[];
  assessment_score?: number;
  certification_issued: boolean;
  certification_number?: string;
  points_earned: number;
}

export type EnrollmentStatus =
  | 'ENROLLED'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'CERTIFIED'
  | 'WITHDRAWN'
  | 'FAILED';

export interface CompetencyAssessment {
  id: number;
  tenant_id: string;
  person_id: string;
  person_name: string;
  competency_area: string;
  required_level: CompetencyLevel;
  current_level: CompetencyLevel;
  gap_exists: boolean;
  gap_severity: 'low' | 'medium' | 'high';
  evidence_type?: EvidenceType;
  evidence_details: Record<string, any>;
  training_required: boolean;
  recommended_programs: number[];
  assessment_date: string;
  gap_closed: boolean;
  gap_closed_date?: string;
}

export type CompetencyLevel =
  | 'basic'
  | 'intermediate'
  | 'advanced'
  | 'expert';

export type EvidenceType =
  | 'training'
  | 'certification'
  | 'experience'
  | 'assessment';

export interface UserLevel {
  person_id: string;
  person_name: string;
  total_points: number;
  current_level: Level;
  current_level_name: string;
  points_in_current_level: number;
  points_to_next_level: number;
  next_level_name: string;
  progress_to_next_level: number;
}

export type Level =
  | 'beginner'
  | 'learner'
  | 'practitioner'
  | 'professional'
  | 'expert'
  | 'master'
  | 'champion';

export interface Achievement {
  achievement_type: string;
  achievement_name: string;
  description: string;
  icon: string;
  points_value: number;
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';
}

export interface UserAchievement extends Achievement {
  earned: boolean;
  earned_date?: string;
  progress?: number; // For progressive achievements
}

export interface LeaderboardEntry {
  rank: number;
  person_id: string;
  person_name: string;
  total_points: number;
  current_level: string;
  achievements_count: number;
}

export interface StreakData {
  person_id: string;
  current_streak_days: number;
  longest_streak_days: number;
  last_activity_date: string;
  streak_active: boolean;
}

export interface AwarenessCampaign {
  id: number;
  tenant_id: string;
  campaign_name: string;
  campaign_type: CampaignType;
  description: string;
  start_date: string;
  end_date: string;
  target_groups: string[];
  communication_channels: string[];
  activities: CampaignActivity[];
  participation_metrics: Record<string, number>;
  status: 'planned' | 'active' | 'completed' | 'cancelled';
}

export type CampaignType =
  | 'onboarding'
  | 'annual_awareness'
  | 'role_based'
  | 'compliance_reminder'
  | 'incident_lessons'
  | 'regulatory_update'
  | 'culture_building'
  | 'special_event';
```

---

## 📱 Responsive Design

### Breakpoints

```css
/* Mobile first approach */
sm: 640px   /* Small devices */
md: 768px   /* Tablets */
lg: 1024px  /* Laptops */
xl: 1280px  /* Desktops */
2xl: 1536px /* Large screens */
```

### Mobile Adaptations

**Dashboard:**
- Stack cards vertically
- Collapse sidebar on mobile
- Bottom navigation for main sections

**Training Player:**
- Full-screen video on mobile
- Sticky navigation bar at bottom
- Collapsible curriculum sidebar

**Leaderboard:**
- Horizontal scroll for table
- Simplified view (rank, name, points only)
- Tap to expand full details

**Competency Matrix:**
- Card view instead of table
- Swipeable cards
- Tap to view details

---

## ⚡ Performance Optimizations

### Code Splitting

```typescript
// Lazy load heavy components
const TrainingPlayer = dynamic(() => import('@/components/TrainingPlayer'), {
  loading: () => <LoadingSpinner />,
  ssr: false
});

const CompetencyChart = dynamic(() => import('@/components/CompetencyChart'), {
  loading: () => <ChartSkeleton />
});
```

### Data Fetching

```typescript
// Use SWR for caching
import useSWR from 'swr';

function useEnrollments() {
  const { data, error, mutate } = useSWR(
    '/api/learning/enrollments',
    learningApi.getEnrollments,
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000, // 1 minute
    }
  );

  return {
    enrollments: data,
    isLoading: !error && !data,
    isError: error,
    mutate
  };
}
```

### Image Optimization

```tsx
// Use Next.js Image component
import Image from 'next/image';

<Image
  src="/badges/first-training.svg"
  alt="First Training Achievement"
  width={80}
  height={80}
  priority={false}
  loading="lazy"
/>
```

---

## 🧪 Testing Strategy

### Unit Tests

```typescript
// __tests__/components/AchievementCard.test.tsx

import { render, screen } from '@testing-library/react';
import { AchievementCard } from '@/components/AchievementCard';

describe('AchievementCard', () => {
  it('renders locked achievement', () => {
    render(<AchievementCard achievement={mockAchievement} earned={false} />);
    expect(screen.getByText('🔒')).toBeInTheDocument();
  });

  it('renders earned achievement with date', () => {
    render(<AchievementCard achievement={mockAchievement} earned={true} earnedDate="2024-10-01" />);
    expect(screen.getByText('Earned')).toBeInTheDocument();
  });
});
```

### Integration Tests

```typescript
// __tests__/pages/training-player.test.tsx

import { renderWithProviders } from '@/test-utils';
import TrainingPlayer from '@/pages/learning/programs/[id]/learn';

test('completes module and updates progress', async () => {
  const { user } = renderWithProviders(<TrainingPlayer />);

  // Watch video
  await user.click(screen.getByRole('button', { name: 'Play' }));

  // Complete module
  await user.click(screen.getByRole('button', { name: 'Mark Complete' }));

  // Verify progress updated
  expect(screen.getByText('Progress: 33%')).toBeInTheDocument();
});
```

### E2E Tests (Playwright)

```typescript
// e2e/learning-journey.spec.ts

import { test, expect } from '@playwright/test';

test('complete full training journey', async ({ page }) => {
  await page.goto('/learning/programs');

  // Browse catalog
  await page.click('text=BCM Fundamentals');
  await page.click('button:has-text("Enroll Now")');

  // Start training
  await page.click('button:has-text("Start Training")');

  // Complete modules
  for (let i = 0; i < 5; i++) {
    await page.click('button:has-text("Mark Complete")');
    await page.click('button:has-text("Next")');
  }

  // Submit assessment
  await page.fill('input[name="answer-1"]', 'A');
  await page.click('button:has-text("Submit Assessment")');

  // Verify certification
  await expect(page.locator('text=Congratulations!')).toBeVisible();
  await expect(page.locator('text=🏆 +500 points')).toBeVisible();
});
```

---

## 🚀 Implementation Roadmap

### Phase 1: Core Learning (4 weeks)

**Week 1: Foundation**
- [ ] Setup Next.js project with TypeScript
- [ ] Configure Tailwind CSS + shadcn/ui
- [ ] Setup Zustand stores
- [ ] Create API client with auth

**Week 2: Training Catalog & Enrollment**
- [ ] Training catalog page with filters
- [ ] Program detail modal
- [ ] Enrollment flow
- [ ] My Enrollments page

**Week 3: Training Player**
- [ ] Video player component
- [ ] Curriculum sidebar
- [ ] Progress tracking
- [ ] Assessment quiz component

**Week 4: Dashboard**
- [ ] Learning dashboard layout
- [ ] Continue learning cards
- [ ] Recommendations engine
- [ ] Progress summary widgets

### Phase 2: Competency & Gamification (3 weeks)

**Week 5: Competency Management**
- [ ] Competency dashboard
- [ ] Gap analysis table
- [ ] Development plan timeline
- [ ] Evidence upload

**Week 6: Gamification UI**
- [ ] Points & level system
- [ ] Achievement cards
- [ ] Leaderboard table
- [ ] Streak tracker
- [ ] Badge collection

**Week 7: Awareness Campaigns**
- [ ] Campaign listing
- [ ] Campaign calendar
- [ ] Participation tracker
- [ ] Campaign activities

### Phase 3: Admin & Analytics (2 weeks)

**Week 8: Admin Features**
- [ ] Program creation form
- [ ] Campaign management
- [ ] User management
- [ ] Bulk enrollment

**Week 9: Analytics & Reports**
- [ ] Training analytics dashboard
- [ ] Competency reports
- [ ] ROI calculations
- [ ] Export to PDF/Excel

### Phase 4: Polish & Testing (2 weeks)

**Week 10: UX Polish**
- [ ] Animations & transitions
- [ ] Loading states
- [ ] Error handling
- [ ] Mobile responsive
- [ ] Accessibility (WCAG 2.1)

**Week 11: Testing & Deployment**
- [ ] Unit tests (80% coverage)
- [ ] Integration tests
- [ ] E2E tests (critical paths)
- [ ] Performance optimization
- [ ] Production deployment

---

## 📚 Additional Resources

### Design References

- **Duolingo** - Gamification UX patterns
- **LinkedIn Learning** - Course player UI
- **Coursera** - Certificate display
- **Khan Academy** - Progress tracking

### Component Libraries

- **shadcn/ui** - https://ui.shadcn.com/
- **Radix UI** - https://www.radix-ui.com/
- **Headless UI** - https://headlessui.com/

### Icons & Illustrations

- **Lucide Icons** - https://lucide.dev/
- **Heroicons** - https://heroicons.com/
- **unDraw Illustrations** - https://undraw.co/

---

## 🎯 Success Metrics

### User Engagement
- Training completion rate > 80%
- Average session duration > 15 minutes
- Return rate > 60%

### Performance
- Initial page load < 2s
- Time to interactive < 3s
- Lighthouse score > 90

### Accessibility
- WCAG 2.1 AA compliance
- Keyboard navigation support
- Screen reader compatible

---

**Document Version:** 1.0
**Last Updated:** 2025-10-01
**Prepared By:** AI Assistant
**Status:** ✅ Ready for Implementation
