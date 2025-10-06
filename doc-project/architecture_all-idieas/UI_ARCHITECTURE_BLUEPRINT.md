# BCM Platform - UI Architecture Blueprint (God-Level Design)

**Designer:** Claude Code (Architect Mode: God-Level 🏛️)
**Date:** 2025-10-02
**Status:** 🎨 MASTER DESIGN - Complete UX/UI Architecture

---

## 🎯 Platform Vision

**BCM Platform** = LinkedIn + Coursera + Udemy + AWS Marketplace для BCM специалистов

### Core User Journeys:

1. **Learner Journey** - "Я хочу стать BCM экспертом"
2. **Specialist Journey** - "Я ищу проекты и клиентов"
3. **Client Journey** - "Мне нужен BCM консультант"
4. **Community Journey** - "Я хочу делиться знаниями"

---

## 🗺️ Complete Sitemap & Navigation

```
┌─────────────────────────────────────────────────────────────────┐
│                      GLOBAL NAVIGATION                           │
├─────────────────────────────────────────────────────────────────┤
│ Logo  [🏠 Главная] [📚 Знания] [💼 Эксперты] [🎓 Обучение]      │
│       [🎮 Симуляции] [💬 Сообщество] [📰 Новости] [👤 Профиль]  │
└─────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                    HOMEPAGE (/)                                 │
└────────────────────────────────────────────────────────────────┘
├── Hero Section
│   ├── Главный заголовок + CTA
│   ├── Поиск (универсальный)
│   └── Quick Actions (3 карточки)
│
├── Platform Overview (4 секции)
│   ├── 📚 База знаний
│   ├── 🎓 Обучение
│   ├── 💼 Marketplace
│   └── 🎮 Симуляции
│
├── Stats Bar (метрики платформы)
│   ├── 1,234 экспертов
│   ├── 5,678 статей
│   ├── 2,345 курсов
│   └── 890 проектов
│
├── Featured Content
│   ├── Популярные курсы (3 карточки)
│   ├── Топ статьи (3 карточки)
│   └── Топ эксперты (3 карточки)
│
└── CTA Section (призыв к регистрации)

┌────────────────────────────────────────────────────────────────┐
│              📚 KNOWLEDGE CENTER (/knowledge)                   │
└────────────────────────────────────────────────────────────────┘
├── Header
│   ├── Title + Subtitle
│   ├── Search bar (фильтры)
│   └── [+ Создать статью] button
│
├── Sidebar Filters (sticky)
│   ├── ISO Clause (checkboxes)
│   ├── Article Type (radio)
│   ├── Difficulty (radio)
│   ├── Verified Only (toggle)
│   └── My Bookmarks (toggle)
│
├── Content Grid (3 columns)
│   └── Article Cards
│       ├── Thumbnail image
│       ├── Title + Summary
│       ├── Author (avatar + name)
│       ├── ISO clause badge
│       ├── Stats (👁️ views, 👍 votes, 🔖 saves)
│       ├── Verified badge (if verified)
│       └── Tags
│
└── Article Detail Modal (/knowledge/{id})
    ├── Header
    │   ├── Title
    │   ├── Author info + Follow button
    │   ├── Actions (👍 Vote, 🔖 Save, 🚩 Report, 💬 Discuss)
    │   └── ISO clause + Verified badge
    │
    ├── Article Content (Markdown rendered)
    │   ├── Table of Contents (sticky)
    │   └── Rich content with code blocks
    │
    ├── Related Articles (3 cards)
    ├── Comments Section
    │   └── Discussion threads
    │
    └── Sidebar (sticky)
        ├── Quick Stats
        ├── Author Profile Card
        └── Related Courses

┌────────────────────────────────────────────────────────────────┐
│              💼 MARKETPLACE (/marketplace)                      │
└────────────────────────────────────────────────────────────────┘
├── Header
│   ├── Title "Find BCM Experts"
│   ├── Search bar
│   └── [Post Project] button (clients)
│       [Become Specialist] button (guests)
│
├── Tabs Navigation
│   ├── 👨‍💼 Specialists (default)
│   ├── 💼 Projects
│   ├── 📚 Case Studies
│   └── ⭐ Reviews
│
├── [TAB: Specialists] (/marketplace/specialists)
│   │
│   ├── Filters Sidebar (sticky)
│   │   ├── Specialization (multi-select)
│   │   ├── Industry (multi-select)
│   │   ├── Location (country, city)
│   │   ├── Availability (checkboxes)
│   │   ├── Hourly Rate (slider)
│   │   ├── Rating (stars)
│   │   ├── Verified Only (toggle)
│   │   └── Remote/Onsite (checkboxes)
│   │
│   ├── Sort Options
│   │   ├── Relevance
│   │   ├── Rating (high → low)
│   │   ├── Hourly Rate (low → high)
│   │   ├── Projects Completed
│   │   └── Recently Active
│   │
│   └── Specialist Cards (2 columns)
│       ├── Avatar + Verified badge
│       ├── Name + Title
│       ├── Location + Availability dot
│       ├── Rating (stars) + Reviews count
│       ├── Hourly rate
│       ├── Specializations (badges)
│       ├── Key certifications (icons)
│       ├── Stats (projects, years exp)
│       ├── Top skills (3 tags)
│       └── [View Profile] [Contact] buttons
│
├── [TAB: Projects] (/marketplace/projects)
│   │
│   ├── Filters Sidebar
│   │   ├── Project Status
│   │   ├── Budget Range
│   │   ├── Project Type
│   │   └── Industry
│   │
│   └── Project Cards
│       ├── Client (company + location)
│       ├── Title + Description (truncated)
│       ├── Budget + Timeline
│       ├── Skills Required (tags)
│       ├── Proposals count
│       ├── Status badge
│       └── [View Details] [Submit Proposal]
│
├── [TAB: Case Studies] (/marketplace/cases)
│   │
│   └── Case Study Cards (masonry layout)
│       ├── Featured image
│       ├── Title
│       ├── Specialist (avatar + name)
│       ├── Client Industry
│       ├── Project Type badge
│       ├── Key Results (metrics)
│       ├── Tags
│       └── [Read Case Study]
│
└── [TAB: Reviews] (/marketplace/reviews)
    │
    └── Review Cards (timeline)
        ├── Reviewer (avatar + name)
        ├── Specialist (avatar + name)
        ├── Rating (stars)
        ├── Project title
        ├── Review text
        ├── Date
        └── Helpful votes

┌────────────────────────────────────────────────────────────────┐
│      /marketplace/specialists/{id} - SPECIALIST PROFILE         │
└────────────────────────────────────────────────────────────────┘
├── Hero Section
│   ├── Cover Image (blur background)
│   ├── Avatar (large, centered)
│   ├── Name + Title
│   ├── Location + Availability status
│   ├── Rating (stars) + Reviews count
│   ├── Verified badge
│   └── Actions
│       ├── [💬 Contact] (primary)
│       ├── [🔖 Save]
│       ├── [📤 Share]
│       └── [🚩 Report]
│
├── Stats Bar
│   ├── ⭐ 4.9 Rating
│   ├── 🏆 87 Projects
│   ├── 💬 45 Reviews
│   ├── 📅 5 Years
│   └── ✅ 98% Success
│
├── Main Content (2 columns)
│   │
│   ├── LEFT COLUMN (wide)
│   │   │
│   │   ├── About Section
│   │   │   ├── Bio (rich text)
│   │   │   └── [Read More] expandable
│   │   │
│   │   ├── Specializations & Skills
│   │   │   ├── Primary Specializations (large badges)
│   │   │   └── Skills (tags cloud)
│   │   │
│   │   ├── Certifications
│   │   │   └── Certification Cards
│   │   │       ├── Logo + Name
│   │   │       ├── Issuing Organization
│   │   │       ├── Issue Date - Expiry
│   │   │       ├── Credential ID
│   │   │       └── Verified badge
│   │   │
│   │   ├── Portfolio / Case Studies
│   │   │   └── Portfolio Item Cards
│   │   │       ├── Thumbnail
│   │   │       ├── Project Title
│   │   │       ├── Client Industry
│   │   │       ├── Description
│   │   │       ├── Key Achievements
│   │   │       ├── Duration + Team Size
│   │   │       └── [View Details]
│   │   │
│   │   ├── Services Offered
│   │   │   └── Service Cards
│   │   │       ├── Service Name + Icon
│   │   │       ├── Description
│   │   │       ├── Pricing (hourly/fixed)
│   │   │       ├── Duration estimate
│   │   │       ├── Delivery mode (remote/onsite)
│   │   │       └── [Request Quote]
│   │   │
│   │   ├── Community Contributions
│   │   │   ├── Knowledge Articles (3 latest)
│   │   │   ├── Forum Posts (3 latest)
│   │   │   └── Reputation Score + Level
│   │   │
│   │   └── Reviews Section
│   │       ├── Reviews Summary (rating breakdown)
│   │       └── Review Cards (paginated)
│   │           ├── Reviewer (avatar + name)
│   │           ├── Rating (stars)
│   │           ├── Project title
│   │           ├── Review text
│   │           ├── Date
│   │           └── Specialist response (if any)
│   │
│   └── RIGHT COLUMN (sidebar, sticky)
│       │
│       ├── Contact Card
│       │   ├── Hourly Rate (big, bold)
│       │   ├── Availability Calendar
│       │   ├── [📧 Contact] button (primary)
│       │   ├── [💼 Hire] button
│       │   └── Response time: ~2 hours
│       │
│       ├── Quick Stats Card
│       │   ├── Projects Completed
│       │   ├── On-Time Delivery
│       │   ├── Repeat Clients
│       │   └── Avg. Project Value
│       │
│       ├── Industries Served
│       │   └── Industry badges
│       │
│       ├── Languages
│       │   └── Language + Proficiency
│       │
│       ├── Work Preferences
│       │   ├── Remote: Yes
│       │   ├── Onsite: Available
│       │   ├── Travel: Willing
│       │   └── Timezone: UTC+3
│       │
│       └── Similar Specialists (3 cards)
│           └── Mini specialist cards

┌────────────────────────────────────────────────────────────────┐
│                🎓 LEARNING PLATFORM (/learning)                 │
└────────────────────────────────────────────────────────────────┘
├── Header
│   ├── Title "BCM Learning Platform"
│   ├── Search bar
│   └── [My Learning] button (if logged in)
│
├── Hero Section
│   ├── Featured Banner
│   │   ├── Headline "Master BCM Skills"
│   │   ├── Stats (X courses, Y students, Z certified)
│   │   └── [Start Learning] CTA
│   │
│   └── Learning Paths (4 cards)
│       ├── 🎯 Beginner Path
│       ├── 📊 Intermediate Path
│       ├── 🚀 Advanced Path
│       └── 🏆 Expert Path
│
├── Tabs Navigation
│   ├── 📚 All Courses (default)
│   ├── 🎯 Learning Paths
│   ├── 🏆 Certifications
│   └── 📝 Templates
│
├── [TAB: All Courses] (/learning/programs)
│   │
│   ├── Filters Sidebar (sticky)
│   │   ├── BCI Level (checkboxes)
│   │   ├── Program Type (checkboxes)
│   │   ├── ISO Clause (select)
│   │   ├── Duration (slider)
│   │   ├── Difficulty (radio)
│   │   ├── Certification (toggle)
│   │   ├── Price (slider)
│   │   └── Status (Active/Coming Soon)
│   │
│   ├── Sort Options
│   │   ├── Relevance
│   │   ├── Most Popular
│   │   ├── Highest Rated
│   │   ├── Newest
│   │   └── Duration (short → long)
│   │
│   └── Course Cards (3 columns)
│       ├── Thumbnail image
│       ├── BCI Level badge
│       ├── Title
│       ├── Instructor (avatar + name)
│       ├── Rating (stars) + Enrolled count
│       ├── Duration + Modules count
│       ├── Difficulty badge
│       ├── Price (or "Free")
│       ├── Key Learning Objectives (3 bullets)
│       ├── Certification badge (if awarded)
│       ├── Progress bar (if enrolled)
│       └── [Enroll Now] or [Continue Learning]
│
├── [TAB: Learning Paths] (/learning/paths)
│   │
│   └── Learning Path Cards (vertical timeline)
│       ├── Path Name + Icon
│       ├── Description
│       ├── Level + Duration
│       ├── Courses Count
│       ├── Skills You'll Gain (badges)
│       ├── Career Outcomes
│       ├── Curriculum (collapsible)
│       │   └── Course modules (checkmarks if completed)
│       └── [Start Path] or [Continue]
│
├── [TAB: Certifications] (/learning/certifications)
│   │
│   └── Certification Cards (2 columns)
│       ├── Certificate Icon/Badge
│       ├── Certification Name
│       ├── Issuing Organization (BCI/ISO)
│       ├── Description
│       ├── Requirements (list)
│       ├── Passing Score
│       ├── Validity Period
│       ├── Prerequisites (if any)
│       ├── Enrolled count
│       └── [View Requirements] [Start]
│
└── [TAB: Templates] (/learning/templates)
    │
    └── Template Cards (3 columns)
        ├── Template Icon
        ├── Title
        ├── Category
        ├── Description
        ├── ISO Clause
        ├── Downloads count
        ├── Rating
        ├── File type (DOCX, PDF, XLSX)
        └── [Preview] [Download]

┌────────────────────────────────────────────────────────────────┐
│         /learning/programs/{id} - COURSE DETAIL PAGE            │
└────────────────────────────────────────────────────────────────┘
├── Hero Section
│   ├── Breadcrumbs
│   ├── Course Title
│   ├── Subtitle
│   ├── Instructor (avatar + name + credentials)
│   ├── Rating (stars) + Reviews + Enrolled
│   ├── Last Updated
│   ├── Duration + Modules + Language
│   └── BCI Level + Certification badges
│
├── Video Preview (if available)
│   └── Course Intro Video + Thumbnail
│
├── Main Content (2 columns)
│   │
│   ├── LEFT COLUMN (wide)
│   │   │
│   │   ├── Tabs Navigation
│   │   │   ├── 📖 Overview (default)
│   │   │   ├── 📚 Curriculum
│   │   │   ├── 👨‍🏫 Instructor
│   │   │   └── ⭐ Reviews
│   │   │
│   │   ├── [TAB: Overview]
│   │   │   ├── Course Description (rich text)
│   │   │   ├── What You'll Learn (checkmarks list)
│   │   │   ├── Prerequisites (if any)
│   │   │   ├── Target Audience
│   │   │   ├── Skills You'll Gain (badges)
│   │   │   └── ISO 22301 Mapping
│   │   │
│   │   ├── [TAB: Curriculum]
│   │   │   └── Sections (expandable accordion)
│   │   │       └── Lessons
│   │   │           ├── Lesson Title
│   │   │           ├── Type icon (video/text/quiz)
│   │   │           ├── Duration
│   │   │           ├── Completed checkmark (if enrolled)
│   │   │           └── [Preview] (if allowed)
│   │   │
│   │   ├── [TAB: Instructor]
│   │   │   ├── Instructor Photo + Bio
│   │   │   ├── Credentials & Certifications
│   │   │   ├── Teaching Stats
│   │   │   │   ├── Courses: 12
│   │   │   │   ├── Students: 3,456
│   │   │   │   ├── Reviews: 890
│   │   │   │   └── Rating: 4.8
│   │   │   ├── [Follow Instructor]
│   │   │   └── Other Courses (3 cards)
│   │   │
│   │   └── [TAB: Reviews]
│   │       ├── Rating Summary (bars)
│   │       ├── Sort Options
│   │       └── Review Cards (paginated)
│   │           ├── Reviewer (avatar + name)
│   │           ├── Rating (stars)
│   │           ├── Review text
│   │           ├── Date
│   │           ├── Helpful votes
│   │           └── [👍 Helpful] button
│   │
│   └── RIGHT COLUMN (sidebar, sticky)
│       │
│       ├── Enrollment Card
│       │   ├── Price (or "Free")
│       │   ├── Discount badge (if any)
│       │   ├── [🎓 Enroll Now] button (primary)
│       │   ├── [🔖 Save for Later]
│       │   ├── [🎁 Gift Course]
│       │   └── "30-day money-back guarantee"
│       │
│       ├── Course Includes
│       │   ├── ⏱️ 12 hours video
│       │   ├── 📄 45 articles
│       │   ├── 📥 12 resources
│       │   ├── 📱 Mobile access
│       │   ├── 🏆 Certificate
│       │   └── ♾️ Lifetime access
│       │
│       ├── Quick Stats Card
│       │   ├── Enrolled: 1,234
│       │   ├── Completion: 85%
│       │   ├── Rating: 4.8/5
│       │   └── Last Updated: 2 weeks ago
│       │
│       └── Related Courses (3 mini cards)

┌────────────────────────────────────────────────────────────────┐
│         /learning/my-learning - MY LEARNING DASHBOARD           │
└────────────────────────────────────────────────────────────────┘
├── Header
│   ├── "My Learning Dashboard"
│   ├── User Stats (XP, Level, Streak)
│   └── [Browse Courses] button
│
├── Overview Cards (4 cards)
│   ├── 📚 Enrolled: 8 courses
│   ├── ✅ Completed: 12 courses
│   ├── 🏆 Certificates: 5
│   └── 🔥 Streak: 14 days
│
├── Tabs Navigation
│   ├── 📖 In Progress (default)
│   ├── ✅ Completed
│   ├── 🔖 Saved
│   └── 🏆 Achievements
│
├── [TAB: In Progress]
│   │
│   └── Course Cards (2 columns)
│       ├── Thumbnail
│       ├── Title
│       ├── Progress Bar (%) + "Continue from Lesson 5"
│       ├── Next Deadline (if any)
│       ├── Time spent / Total time
│       ├── [Continue Learning] button
│       └── [•••] menu (Unenroll, Move to Saved)
│
├── [TAB: Completed]
│   │
│   └── Course Cards (3 columns)
│       ├── Thumbnail
│       ├── Title
│       ├── Completed date
│       ├── Final Score
│       ├── Certificate badge
│       ├── [View Certificate] button
│       └── [Review Course]
│
├── [TAB: Saved]
│   │
│   └── Course Cards (same as Browse view)
│       └── [Remove from Saved] [Enroll Now]
│
└── [TAB: Achievements]
    │
    ├── Progress Overview
    │   ├── Current Level: 🏆 Expert (Level 12)
    │   ├── XP Progress Bar (2,450 / 3,000)
    │   ├── Learning Streak: 🔥 14 days
    │   └── Next Milestone: 550 XP to Level 13
    │
    ├── Badges Earned (grid)
    │   └── Badge Cards
    │       ├── Badge Icon (large)
    │       ├── Badge Name
    │       ├── Description
    │       ├── Earned Date
    │       ├── Rarity (Common/Rare/Epic/Legendary)
    │       └── XP Value
    │
    ├── Leaderboard Widget
    │   ├── Your Rank: #45 of 1,234
    │   ├── Top 10 Users (mini list)
    │   └── [View Full Leaderboard]
    │
    └── Recent Activity Timeline
        └── Activity Items
            ├── Icon + Description
            ├── XP Earned
            └── Timestamp

┌────────────────────────────────────────────────────────────────┐
│         /learning/course-player/{id} - COURSE PLAYER            │
└────────────────────────────────────────────────────────────────┘
├── Top Bar (sticky)
│   ├── [← Back to Course] button
│   ├── Course Title
│   ├── Progress: 45% (12/26 lessons)
│   └── [Mark Complete] [Next Lesson →]
│
├── Main Layout (3 columns)
│   │
│   ├── LEFT SIDEBAR (collapsible, 300px)
│   │   ├── Course Curriculum
│   │   │   └── Sections (accordion)
│   │   │       └── Lessons (list)
│   │   │           ├── ✓ Completed (green)
│   │   │           ├── ▶ Current (blue, active)
│   │   │           └── • Locked (gray)
│   │   │
│   │   └── Footer
│   │       ├── Progress Bar
│   │       └── [< Collapse] button
│   │
│   ├── CENTER CONTENT (main, responsive)
│   │   │
│   │   ├── Lesson Header
│   │   │   ├── Lesson Number + Title
│   │   │   ├── Duration
│   │   │   └── Actions (🔖 Save, 📝 Notes, 🚩 Report)
│   │   │
│   │   ├── Content Area (depends on type)
│   │   │   │
│   │   │   ├── [IF VIDEO]
│   │   │   │   ├── Video Player (16:9)
│   │   │   │   │   ├── Custom controls
│   │   │   │   │   ├── Playback speed
│   │   │   │   │   ├── Subtitles/CC
│   │   │   │   │   ├── Quality selector
│   │   │   │   │   └── Picture-in-Picture
│   │   │   │   │
│   │   │   │   └── Video Transcript (expandable)
│   │   │   │       └── Timestamped text (clickable)
│   │   │   │
│   │   │   ├── [IF ARTICLE/TEXT]
│   │   │   │   ├── Rich Text Content
│   │   │   │   │   ├── Headings
│   │   │   │   │   ├── Images
│   │   │   │   │   ├── Code blocks
│   │   │   │   │   └── Callouts
│   │   │   │   │
│   │   │   │   └── Reading Progress Bar
│   │   │   │
│   │   │   ├── [IF QUIZ/ASSESSMENT]
│   │   │   │   ├── Quiz Header
│   │   │   │   │   ├── Questions: 10
│   │   │   │   │   ├── Time Limit: 30 min
│   │   │   │   │   └── Passing Score: 70%
│   │   │   │   │
│   │   │   │   ├── Question Card (1 at a time)
│   │   │   │   │   ├── Question Number
│   │   │   │   │   ├── Question Text
│   │   │   │   │   ├── Answer Options (radio/checkbox)
│   │   │   │   │   └── [Submit Answer]
│   │   │   │   │
│   │   │   │   ├── Answer Feedback (after submit)
│   │   │   │   │   ├── Correct/Incorrect
│   │   │   │   │   ├── Explanation
│   │   │   │   │   └── [Next Question]
│   │   │   │   │
│   │   │   │   └── Quiz Results (after completion)
│   │   │   │       ├── Score: 85% (9/10)
│   │   │   │       ├── Pass/Fail status
│   │   │   │       ├── Time Taken
│   │   │   │       ├── Review Answers (expandable)
│   │   │   │       └── [Retake Quiz] [Next Lesson]
│   │   │   │
│   │   │   └── [IF EXERCISE/LAB]
│   │   │       ├── Exercise Instructions
│   │   │       ├── Code Editor (if coding exercise)
│   │   │       ├── File Upload (if document)
│   │   │       ├── [Submit for Review]
│   │   │       └── Submission History
│   │   │
│   │   ├── Resources Section (expandable)
│   │   │   └── Downloadable Files
│   │   │       ├── PDF slides
│   │   │       ├── Templates
│   │   │       ├── Code samples
│   │   │       └── Additional readings
│   │   │
│   │   └── Discussion Section
│   │       ├── Q&A Thread
│   │       ├── [Ask Question] button
│   │       └── Questions/Answers (threaded)
│   │
│   └── RIGHT SIDEBAR (optional, 250px)
│       │
│       ├── Notes Panel (toggleable)
│       │   ├── My Notes (timestamped for video)
│       │   ├── [Add Note] textarea
│       │   └── Notes List
│       │
│       ├── Bookmarks (lesson markers)
│       │
│       └── Help Widget
│           ├── [💬 Ask Instructor]
│           ├── [🤖 AI Assistant]
│           └── [📞 Support]
│
└── Bottom Navigation (sticky)
    ├── [← Previous Lesson]
    ├── Progress Indicator (dots)
    └── [Next Lesson →]

┌────────────────────────────────────────────────────────────────┐
│         🎮 SIMULATIONS PLATFORM (/simulations)                  │
└────────────────────────────────────────────────────────────────┘
├── Header
│   ├── "BCM Simulations & Exercises"
│   ├── Subtitle "Test your preparedness"
│   └── [+ Create Simulation] button
│
├── Hero Banner
│   ├── Featured Simulation
│   ├── Stats (X simulations run, Y avg score)
│   └── [Try Featured Simulation]
│
├── Tabs Navigation
│   ├── 🎮 Run Simulation (default)
│   ├── 📚 Scenario Library
│   ├── 📊 My Simulations
│   └── 📈 Analytics
│
├── [TAB: Run Simulation] (/simulations/new)
│   │
│   └── Simulation Wizard (stepper)
│       │
│       ├── STEP 1: Choose Simulation Type
│       │   └── Type Cards (3 options)
│       │       ├── 🔍 What-If Analysis
│       │       │   ├── Description
│       │       │   ├── Use cases
│       │       │   ├── Duration: ~15 min
│       │       │   └── [Select]
│       │       │
│       │       ├── 🎲 Monte Carlo Simulation
│       │       │   ├── Description
│       │       │   ├── Use cases
│       │       │   ├── Duration: ~30 min
│       │       │   └── [Select]
│       │       │
│       │       └── 🎯 BCM Scenario Exercise
│       │           ├── Description
│       │           ├── Use cases
│       │           ├── Duration: 2-8 hours
│       │           └── [Select]
│       │
│       ├── STEP 2: Configure Parameters
│       │   ├── Simulation Name (input)
│       │   ├── Description (textarea)
│       │   │
│       │   ├── [IF What-If]
│       │   │   ├── Select Scenario (dropdown)
│       │   │   ├── Impact Variables (checkboxes)
│       │   │   └── Time Horizon (slider)
│       │   │
│       │   ├── [IF Monte Carlo]
│       │   │   ├── Risk Variables (multi-select)
│       │   │   ├── Probability Distributions
│       │   │   ├── Iterations (slider: 1000-10000)
│       │   │   └── Confidence Level (slider: 90-99%)
│       │   │
│       │   └── [IF Scenario Exercise]
│       │       ├── Select from Library (search)
│       │       ├── OR Upload Custom Scenario
│       │       ├── Team Size (number)
│       │       ├── Duration (hours)
│       │       └── Difficulty (slider)
│       │
│       ├── STEP 3: Review & Launch
│       │   ├── Summary Card
│       │   │   ├── Type + Name
│       │   │   ├── Parameters
│       │   │   ├── Estimated Duration
│       │   │   └── Participants (if team)
│       │   │
│       │   └── Actions
│       │       ├── [< Back] [Save Draft] [Launch →]
│       │       └── "Start simulation now or schedule"
│       │
│       └── STEP 4: Simulation Running
│           └── (Navigate to Simulation Runner)
│
├── [TAB: Scenario Library] (/simulations/library)
│   │
│   ├── Filters Sidebar
│   │   ├── Threat Type (multi-select)
│   │   │   ├── 🔒 Cyber Attack
│   │   │   ├── 🌪️ Natural Disaster
│   │   │   ├── 🦠 Pandemic
│   │   │   ├── 📦 Supply Chain
│   │   │   ├── 🏗️ Infrastructure
│   │   │   └── 👤 Human Error
│   │   │
│   │   ├── Complexity Level
│   │   │   ├── Beginner
│   │   │   ├── Intermediate
│   │   │   ├── Advanced
│   │   │   └── Expert
│   │   │
│   │   ├── Duration (slider)
│   │   ├── Industry (multi-select)
│   │   └── ISO Clause (select)
│   │
│   └── Scenario Cards (grid, 3 columns)
│       ├── Scenario Icon/Image
│       ├── Title
│       ├── Threat Type badge
│       ├── Complexity badge
│       ├── Description (truncated)
│       ├── Stats
│       │   ├── Duration: 4 hours
│       │   ├── Injects: 12
│       │   ├── Used: 234 times
│       │   └── Rating: 4.7
│       ├── Learning Objectives (3 bullets)
│       └── [View Details] [Use Scenario]
│
├── [TAB: My Simulations] (/simulations/my)
│   │
│   ├── Status Filters (pills)
│   │   ├── All
│   │   ├── Draft
│   │   ├── Running
│   │   ├── Completed
│   │   └── Failed
│   │
│   └── Simulation Cards (table view)
│       ├── Simulation Name
│       ├── Type icon
│       ├── Status badge
│       ├── Created Date
│       ├── Duration / Progress
│       ├── Score (if completed)
│       ├── Actions
│       │   ├── [▶ Resume] (if running)
│       │   ├── [📊 View Results] (if completed)
│       │   ├── [📋 Clone]
│       │   └── [🗑️ Delete]
│       └── [•••] menu
│
└── [TAB: Analytics] (/simulations/analytics)
    │
    ├── Overview Cards (4 cards)
    │   ├── Total Simulations: 45
    │   ├── Avg. Score: 78%
    │   ├── Time Invested: 87 hours
    │   └── Certifications: 3
    │
    ├── Charts Section
    │   ├── Performance Trend (line chart)
    │   ├── Simulation Types Breakdown (pie)
    │   ├── Threat Types Coverage (bar)
    │   └── Competency Heatmap
    │
    └── Recommendations
        ├── "Focus on Cyber scenarios"
        ├── "Practice more What-If analysis"
        └── [Suggested Scenarios] (3 cards)

┌────────────────────────────────────────────────────────────────┐
│     /simulations/run/{id} - SIMULATION RUNNER (LIVE)            │
└────────────────────────────────────────────────────────────────┘
├── Top Bar (sticky, dark theme)
│   ├── Simulation Name
│   ├── Timer (⏱️ 02:34:15 / 04:00:00)
│   ├── Progress (45% complete)
│   ├── [⏸️ Pause] [⏹️ Stop] buttons
│   └── [👥 Team] [💬 Chat] [📞 Help]
│
├── Main Layout (depends on simulation type)
│   │
│   ├── [IF SCENARIO EXERCISE]
│   │   │
│   │   ├── Timeline View (horizontal)
│   │   │   ├── Hour markers
│   │   │   ├── Current time indicator
│   │   │   ├── Inject markers (clickable)
│   │   │   └── Milestone markers
│   │   │
│   │   ├── Situation Board (main area)
│   │   │   ├── Current Situation Card (large)
│   │   │   │   ├── Situation Description
│   │   │   │   ├── Severity Level
│   │   │   │   ├── Time Remaining
│   │   │   │   └── Required Actions
│   │   │   │
│   │   │   ├── Active Injects (cards)
│   │   │   │   └── Inject Card
│   │   │   │       ├── Inject Type (email, call, alert)
│   │   │   │       ├── Sender/Source
│   │   │   │       ├── Message Content
│   │   │   │       ├── Priority badge
│   │   │   │       ├── Received Time
│   │   │   │       └── [Respond] [Escalate] [Archive]
│   │   │   │
│   │   │   └── Response Panel
│   │   │       ├── Your Response (textarea)
│   │   │       ├── Action Type (dropdown)
│   │   │       ├── Assign To (if team)
│   │   │       └── [Submit Response]
│   │   │
│   │   ├── Right Sidebar (resources, 300px)
│   │   │   ├── Scenario Info
│   │   │   │   ├── Objective
│   │   │   │   ├── Success Criteria
│   │   │   │   └── Available Resources
│   │   │   │
│   │   │   ├── Team Status (if multiplayer)
│   │   │   │   └── Team Members
│   │   │   │       ├── Avatar + Name
│   │   │   │       ├── Role
│   │   │   │       ├── Status dot
│   │   │   │       └── Actions count
│   │   │   │
│   │   │   ├── Documents Library (expandable)
│   │   │   │   ├── BCP Document
│   │   │   │   ├── Contact Lists
│   │   │   │   ├── Procedures
│   │   │   │   └── Templates
│   │   │   │
│   │   │   └── Notes Panel
│   │   │       ├── Quick Notes
│   │   │       └── Decision Log
│   │   │
│   │   └── Bottom Panel (collapsible)
│   │       ├── Activity Log (timeline)
│   │       │   └── Log Entries
│   │       │       ├── Timestamp
│   │       │       ├── Actor
│   │       │       ├── Action
│   │       │       └── Result
│   │       │
│   │       └── Chat (if team)
│   │           ├── Chat Messages
│   │           └── Input + Send
│   │
│   ├── [IF WHAT-IF ANALYSIS]
│   │   │
│   │   ├── Scenario Canvas (center)
│   │   │   ├── Visual Diagram
│   │   │   │   ├── Process nodes
│   │   │   │   ├── Dependencies (arrows)
│   │   │   │   ├── Impact areas (highlighted)
│   │   │   │   └── Interactive (hover for details)
│   │   │   │
│   │   │   └── Variable Controls (bottom)
│   │   │       ├── Variable Sliders
│   │   │       ├── Toggle Switches
│   │   │       └── [Run Analysis] button
│   │   │
│   │   ├── Results Panel (right)
│   │   │   ├── Impact Summary
│   │   │   │   ├── Overall Impact Score
│   │   │   │   ├── Affected Processes
│   │   │   │   └── Critical Issues
│   │   │   │
│   │   │   ├── Charts
│   │   │   │   ├── Impact Over Time
│   │   │   │   └── Process Dependencies
│   │   │   │
│   │   │   └── Recommendations
│   │   │       └── Action Cards
│   │   │
│   │   └── History (left sidebar)
│   │       └── Previous Analyses
│   │           ├── Timestamp
│   │           ├── Variables Changed
│   │           ├── Result Summary
│   │           └── [Restore]
│   │
│   └── [IF MONTE CARLO]
│       │
│       ├── Configuration Panel (left)
│       │   ├── Risk Variables
│       │   │   └── Variable Cards
│       │   │       ├── Name
│       │   │       ├── Distribution Type
│       │   │       ├── Parameters (min, max, mean)
│       │   │       └── [Edit]
│       │   │
│       │   ├── Simulation Settings
│       │   │   ├── Iterations
│       │   │   ├── Confidence Level
│       │   │   └── Random Seed
│       │   │
│       │   └── [▶ Run Simulation] button
│       │
│       ├── Results Dashboard (center)
│       │   │
│       │   ├── Running Status (if in progress)
│       │   │   ├── Progress Bar
│       │   │   ├── Iterations: 3,456 / 10,000
│       │   │   ├── Time Remaining: 2:34
│       │   │   └── [⏸️ Pause] [⏹️ Stop]
│       │   │
│       │   └── Results (when complete)
│       │       ├── Key Metrics Cards
│       │       │   ├── Mean
│       │       │   ├── Median
│       │       │   ├── Std Deviation
│       │       │   └── Confidence Intervals
│       │       │
│       │       ├── Distribution Chart
│       │       │   └── Histogram + PDF curve
│       │       │
│       │       ├── Cumulative Distribution
│       │       │   └── CDF chart
│       │       │
│       │       └── Risk Breakdown
│       │           └── Tornado Chart
│       │
│       └── Export & Share (right)
│           ├── [📊 Export Results]
│           │   ├── PDF Report
│           │   ├── Excel Data
│           │   └── JSON Raw
│           │
│           ├── [📤 Share]
│           └── [💾 Save Simulation]
│
└── Completion Modal (overlay)
    ├── Congratulations Header
    ├── Final Score / Results
    ├── Performance Breakdown
    │   ├── Decision Quality: 85%
    │   ├── Response Time: 92%
    │   ├── Resource Usage: 78%
    │   └── Team Collaboration: 88%
    ├── Achievements Unlocked (badges)
    ├── XP Earned: +250 XP
    ├── Certificate (if threshold met)
    ├── Recommendations
    └── Actions
        ├── [📊 View Detailed Report]
        ├── [📤 Share Results]
        ├── [🔁 Try Again]
        └── [✓ Done]

┌────────────────────────────────────────────────────────────────┐
│         💬 COMMUNITY FORUM (/community)                         │
└────────────────────────────────────────────────────────────────┘
├── Header
│   ├── "BCM Community Forum"
│   ├── Search bar
│   └── [+ New Topic] button (primary)
│
├── Categories Navigation (tabs)
│   ├── 📌 All Topics (default)
│   ├── ❓ Questions
│   ├── 💡 Discussions
│   ├── 📢 Announcements
│   └── 🔥 Trending
│
├── Filters Sidebar (sticky)
│   ├── Category (checkboxes)
│   │   ├── General BCM
│   │   ├── ISO 22301
│   │   ├── BCI GPG
│   │   ├── Risk Management
│   │   ├── Incident Response
│   │   └── Career & Jobs
│   │
│   ├── Status
│   │   ├── All
│   │   ├── Unanswered
│   │   ├── Solved ✓
│   │   └── Pinned 📌
│   │
│   ├── Tags (popular tags cloud)
│   └── [Clear Filters]
│
├── Sort Options (dropdown)
│   ├── Latest Activity
│   ├── Newest Topics
│   ├── Most Views
│   ├── Most Replies
│   └── Highest Voted
│
├── Topic List (main area)
│   │
│   └── Topic Card (list item)
│       ├── LEFT: Topic Metadata
│       │   ├── 📌 Pinned badge (if pinned)
│       │   ├── ✓ Solved badge (if solved)
│       │   ├── 🔒 Locked badge (if locked)
│       │   ├── Vote Count (large)
│       │   │   ├── ▲ Upvote button
│       │   │   ├── Number
│       │   │   └── ▼ Downvote button
│       │   └── View Count (👁️ 1,234)
│       │
│       ├── CENTER: Topic Content
│       │   ├── Title (link to topic)
│       │   ├── Excerpt (1-2 lines)
│       │   ├── Tags (badges)
│       │   ├── Author
│       │   │   ├── Avatar (small)
│       │   │   ├── Name
│       │   │   ├── Reputation Level badge
│       │   │   └── Posted time
│       │   │
│       │   └── Category badge
│       │
│       └── RIGHT: Engagement Stats
│           ├── Replies count (💬 24)
│           ├── Last Reply
│           │   ├── Avatar (tiny)
│           │   ├── Name
│           │   └── Time
│           └── Participants count (3 avatars)
│
├── Pagination (bottom)
│   └── [< Prev] [1] [2] [3] ... [10] [Next >]
│
└── Sidebar (right, 300px)
    │
    ├── Create Topic CTA
    │   ├── "Have a question?"
    │   └── [+ Start Discussion]
    │
    ├── Forum Stats Card
    │   ├── 📊 Topics: 12,345
    │   ├── 💬 Posts: 45,678
    │   ├── 👥 Members: 3,456
    │   └── 🆕 Today: 23 new
    │
    ├── Top Contributors (This Week)
    │   └── User List (5 users)
    │       ├── Avatar + Name
    │       ├── Reputation
    │       ├── Posts this week
    │       └── Badge
    │
    └── Trending Topics (5 topics)
        └── Mini Topic Cards
            ├── Title (link)
            ├── Replies count
            └── Trend indicator (🔥)

┌────────────────────────────────────────────────────────────────┐
│         /community/topic/{id} - TOPIC DETAIL PAGE               │
└────────────────────────────────────────────────────────────────┘
├── Breadcrumbs
│   └── Forum / Category / Topic Title
│
├── Topic Header
│   ├── Title (large)
│   ├── Status Badges
│   │   ├── ✓ Solved (if solved)
│   │   ├── 📌 Pinned (if pinned)
│   │   └── 🔒 Locked (if locked)
│   ├── Category + Tags
│   ├── Posted by (author) + Time
│   └── Actions Bar
│       ├── [👍 Vote] (with count)
│       ├── [🔖 Follow Topic]
│       ├── [🔗 Share]
│       ├── [🚩 Report]
│       └── [•••] More (Edit, Pin, Lock - if moderator)
│
├── Main Content (2 columns)
│   │
│   ├── LEFT COLUMN (wide)
│   │   │
│   │   ├── Original Post (OP)
│   │   │   │
│   │   │   ├── Post Card
│   │   │   │   ├── Author Sidebar
│   │   │   │   │   ├── Avatar (large)
│   │   │   │   │   ├── Name + Role badge
│   │   │   │   │   ├── Reputation Score
│   │   │   │   │   ├── Level Badge
│   │   │   │   │   ├── Member Since
│   │   │   │   │   ├── Posts: 234
│   │   │   │   │   └── [View Profile]
│   │   │   │   │
│   │   │   │   ├── Post Content
│   │   │   │   │   ├── Rich Text (Markdown)
│   │   │   │   │   ├── Code Blocks
│   │   │   │   │   ├── Images
│   │   │   │   │   ├── Attachments
│   │   │   │   │   └── Edited indicator (if edited)
│   │   │   │   │
│   │   │   │   └── Post Actions
│   │   │   │       ├── Vote Buttons (▲ 45 ▼)
│   │   │   │       ├── [💬 Reply]
│   │   │   │       ├── [🔗 Share]
│   │   │   │       ├── [🚩 Report]
│   │   │   │       └── [✏️ Edit] (if author/mod)
│   │   │   │
│   │   │   └── Linked Knowledge
│   │   │       └── "Related Articles" (if any)
│   │   │
│   │   ├── Replies Header
│   │   │   ├── "24 Replies"
│   │   │   └── Sort: [Best] [Newest] [Oldest]
│   │   │
│   │   ├── Reply Cards (threaded)
│   │   │   │
│   │   │   └── Reply Card (same structure as OP)
│   │   │       ├── Author Sidebar (compact)
│   │   │       ├── Reply Content
│   │   │       ├── Actions
│   │   │       └── Nested Replies (indented)
│   │   │           └── "Show 3 more replies"
│   │   │
│   │   ├── Solution Badge (if marked as solution)
│   │   │   └── "✓ Accepted Solution" (green banner)
│   │   │
│   │   └── Reply Editor (bottom)
│   │       ├── Markdown Editor
│   │       │   ├── Toolbar (bold, italic, link, image, code)
│   │       │   ├── Textarea
│   │       │   └── Preview Tab
│   │       │
│   │       ├── [📎 Attach File]
│   │       └── [Post Reply] button (primary)
│   │
│   └── RIGHT SIDEBAR (300px, sticky)
│       │
│       ├── Topic Stats Card
│       │   ├── Created: 2 days ago
│       │   ├── Last Activity: 3 hours ago
│       │   ├── Views: 1,234
│       │   ├── Replies: 24
│       │   ├── Participants: 8
│       │   └── Solved: Yes ✓
│       │
│       ├── Author Info Card
│       │   ├── Avatar + Name
│       │   ├── Reputation: 2,450
│       │   ├── Level: Expert
│       │   ├── Badges (3 recent)
│       │   └── [View Full Profile]
│       │
│       ├── Related Topics (5 topics)
│       │   └── Mini Topic Cards
│       │
│       └── Suggested Actions
│           ├── [📚 Read Knowledge Article]
│           ├── [🎓 Take Related Course]
│           └── [🎮 Try Simulation]
│
└── Bottom Actions
    ├── [← Back to Forum]
    └── [🔔 Subscribe to Topic]

┌────────────────────────────────────────────────────────────────┐
│         📰 NEWS & EVENTS (/news, /events)                       │
└────────────────────────────────────────────────────────────────┘
├── [PAGE: News] (/news)
│   │
│   ├── Header
│   │   ├── "BCM News & Updates"
│   │   └── [🔔 Subscribe to Newsletter]
│   │
│   ├── Featured News (hero)
│   │   ├── Large Featured Image
│   │   ├── Category badge
│   │   ├── Title (large)
│   │   ├── Summary
│   │   ├── Author + Date
│   │   └── [Read More]
│   │
│   ├── Filters (horizontal pills)
│   │   ├── All News
│   │   ├── Platform Updates
│   │   ├── Industry News
│   │   ├── Regulations
│   │   └── Community
│   │
│   └── News Grid (3 columns)
│       │
│       └── News Card
│           ├── Image
│           ├── Category badge
│           ├── Title
│           ├── Summary (2 lines)
│           ├── Author + Date
│           ├── Read Time
│           └── [Read More]
│
└── [PAGE: Events] (/events)
    │
    ├── Header
    │   ├── "Upcoming BCM Events"
    │   ├── Calendar View Toggle
    │   └── [+ Submit Event]
    │
    ├── View Switcher (tabs)
    │   ├── 📅 Upcoming (default)
    │   ├── 🕒 Past Events
    │   └── 📍 My Events
    │
    ├── Filters
    │   ├── Event Type
    │   │   ├── Webinar
    │   │   ├── Conference
    │   │   ├── Workshop
    │   │   ├── Training
    │   │   └── Networking
    │   ├── Date Range (calendar)
    │   ├── Location (online/onsite)
    │   └── Price (free/paid)
    │
    └── Events List
        │
        └── Event Card (timeline layout)
            ├── Date Badge (large, left)
            │   ├── Month
            │   └── Day
            │
            ├── Event Details (center)
            │   ├── Title
            │   ├── Organizer + Logo
            │   ├── Time + Duration
            │   ├── Location/Platform
            │   ├── Event Type badge
            │   ├── Description (2 lines)
            │   ├── Speakers (avatars)
            │   └── Tags
            │
            ├── Attendance (right)
            │   ├── 👥 234 attending
            │   ├── Price (or "Free")
            │   └── [Register] button
            │
            └── [View Details]

┌────────────────────────────────────────────────────────────────┐
│         👤 USER DASHBOARD - PERSONAL CABINET                    │
└────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    DASHBOARD LAYOUT STRUCTURE                    │
├─────────────────────────────────────────────────────────────────┤
│ [GLOBAL NAV]  [Logo] [Main Menu] [Notifications] [Avatar Menu]  │
├─────────────────────────────────────────────────────────────────┤
│ LEFT SIDEBAR       │  MAIN CONTENT AREA                          │
│ (250px, fixed)     │  (responsive, scrollable)                   │
│                    │                                             │
│ [User Quick Info]  │  [Page Content]                             │
│                    │                                             │
│ Navigation Menu:   │  - Dynamic based on selected menu item      │
│ • Dashboard        │  - Cards, tables, charts                    │
│ • My Profile       │  - Forms, wizards                           │
│ • My Learning      │  - Data grids                               │
│ • My Simulations   │                                             │
│ • My Projects      │                                             │
│ • Messages         │                                             │
│ • Settings         │                                             │
│                    │                                             │
│ [Upgrade CTA]      │  [Floating Action Button] (if applicable)   │
└────────────────────┴─────────────────────────────────────────────┘

// ПОЛНАЯ СТРУКТУРА ЛИЧНОГО КАБИНЕТА //

/dashboard
├── LEFT SIDEBAR (persistent)
│   │
│   ├── User Quick Card
│   │   ├── Avatar (medium)
│   │   ├── Name
│   │   ├── Role/Title
│   │   ├── Level Badge (🏆 Expert Lvl 12)
│   │   ├── XP Progress Bar (mini)
│   │   └── [Switch Role] (if multiple)
│   │
│   ├── Navigation Menu
│   │   │
│   │   ├── 🏠 Dashboard (default)
│   │   ├── 👤 My Profile
│   │   ├── 📚 My Learning
│   │   ├── 🎮 My Simulations
│   │   ├── 💼 My Projects
│   │   │   ├── (if Specialist) Projects & Proposals
│   │   │   └── (if Client) Posted Projects
│   │   ├── 💬 Messages (badge with unread count)
│   │   ├── 📊 Analytics
│   │   ├── ⚙️ Settings
│   │   └── ❓ Help & Support
│   │
│   ├── Quick Actions
│   │   ├── [+ New Project]
│   │   ├── [+ Start Simulation]
│   │   └── [+ Ask Question]
│   │
│   └── Upgrade CTA (if free plan)
│       ├── "Unlock Premium"
│       ├── Benefits list (3 items)
│       └── [Upgrade Now]
│
└── MAIN CONTENT AREA (changes based on menu selection)

┌────────────────────────────────────────────────────────────────┐
│         /dashboard - MAIN DASHBOARD (OVERVIEW)                  │
└────────────────────────────────────────────────────────────────┘
├── Welcome Header
│   ├── "Welcome back, [Name]! 👋"
│   ├── Current date + time
│   └── Quick stats badges
│
├── Quick Stats Row (4 cards)
│   ├── 🎓 Courses: 8 active
│   ├── 🎮 Simulations: 12 completed
│   ├── 💼 Projects: 3 active
│   └── 🏆 XP: 2,450 (+50 this week)
│
├── Main Grid (2 columns)
│   │
│   ├── LEFT COLUMN (wider)
│   │   │
│   │   ├── Activity Feed Card
│   │   │   ├── "Recent Activity"
│   │   │   └── Timeline
│   │   │       ├── [Today]
│   │   │       │   ├── Completed lesson "BIA Analysis"
│   │   │       │   ├── Earned badge "Quick Learner"
│   │   │       │   └── Posted reply in forum
│   │   │       │
│   │   │       ├── [Yesterday]
│   │   │       │   ├── Started course "ISO 22301"
│   │   │       │   └── Submitted proposal
│   │   │       │
│   │   │       └── [View All Activity]
│   │   │
│   │   ├── Continue Learning Card
│   │   │   ├── "Pick up where you left off"
│   │   │   └── Course Progress Cards (2-3)
│   │   │       ├── Thumbnail + Title
│   │   │       ├── Progress: 65%
│   │   │       ├── Next: "Lesson 8 - RTO"
│   │   │       └── [Continue]
│   │   │
│   │   └── Active Projects Card (if specialist)
│   │       ├── "Your Active Projects"
│   │       └── Project Cards (3 max)
│   │           ├── Client name + avatar
│   │           ├── Project title
│   │           ├── Status badge
│   │           ├── Deadline: 5 days
│   │           ├── Progress: 45%
│   │           └── [View Project]
│   │
│   └── RIGHT COLUMN (narrower)
│       │
│       ├── Achievements Widget
│       │   ├── "Recent Achievements"
│       │   ├── Latest Badges (3 badges)
│       │   │   └── Badge Icon + Name
│       │   └── [View All Achievements]
│       │
│       ├── Leaderboard Widget
│       │   ├── "Your Ranking"
│       │   ├── Your Position: #45 of 1,234
│       │   ├── XP to next rank: 150 XP
│       │   ├── Top 3 Users (mini list)
│       │   └── [View Full Leaderboard]
│       │
│       ├── Upcoming Events
│       │   ├── "This Week"
│       │   └── Event List (3 events)
│       │       ├── Date + Time
│       │       ├── Event Title
│       │       └── [Remind Me]
│       │
│       └── Notifications Panel
│           ├── "Recent Notifications"
│           └── Notification Items (5 latest)
│               ├── Icon + Text
│               ├── Time
│               └── [Mark Read]
│
└── Recommended Actions Card
    ├── "Suggested for You"
    └── Action Cards (horizontal scroll)
        ├── "Complete BIA course - 35% done"
        ├── "Try Monte Carlo simulation"
        ├── "Update your profile to 100%"
        └── "Join webinar tomorrow"

┌────────────────────────────────────────────────────────────────┐
│         /dashboard/profile - MY PROFILE (EDIT MODE)             │
└────────────────────────────────────────────────────────────────┘
├── Header
│   ├── "My Profile"
│   └── [Preview Public Profile] button
│
├── Profile Completion Card (sticky top)
│   ├── Progress Circle (78%)
│   ├── "Your profile is 78% complete"
│   ├── Checklist (expandable)
│   │   ├── ✓ Basic info
│   │   ├── ✓ Profile photo
│   │   ├── ✓ Bio
│   │   ├── ✓ Skills
│   │   ├── ⏳ Certifications (add 2 more)
│   │   └── ⏳ Portfolio (add 3 projects)
│   └── [Complete Now]
│
├── Tabs Navigation
│   ├── 📝 Basic Info (default)
│   ├── 💼 Professional (if Specialist)
│   ├── 🎓 Certifications
│   ├── 📁 Portfolio
│   ├── 🔐 Privacy
│   └── 🔔 Notifications
│
├── [TAB: Basic Info]
│   │
│   └── Form Sections (cards)
│       │
│       ├── Profile Photo Section
│       │   ├── Current Avatar (large)
│       │   ├── [Upload New] [Remove]
│       │   └── "Max 5MB, JPG or PNG"
│       │
│       ├── Personal Information
│       │   ├── Full Name*
│       │   ├── Email* (verified badge)
│       │   ├── Phone (optional)
│       │   ├── Date of Birth
│       │   ├── Gender
│       │   └── Location
│       │       ├── Country
│       │       ├── City
│       │       └── Timezone (auto-detected)
│       │
│       ├── Professional Title & Bio
│       │   ├── Title/Headline* (80 chars)
│       │   ├── Bio (rich text editor, 500 words)
│       │   └── Character counter
│       │
│       ├── Languages
│       │   ├── [+ Add Language]
│       │   └── Language Entries
│       │       ├── Language (dropdown)
│       │       ├── Proficiency (slider)
│       │       └── [Remove]
│       │
│       └── [Save Changes] [Cancel]
│
├── [TAB: Professional] (Specialists only)
│   │
│   └── Form Sections
│       │
│       ├── Availability
│       │   ├── Status (radio)
│       │   │   ├── ○ Available for work
│       │   │   ├── ○ Busy (limited availability)
│       │   │   └── ○ Not available
│       │   ├── Weekly Hours (slider: 0-40)
│       │   └── Response Time (dropdown)
│       │
│       ├── Rates & Pricing
│       │   ├── Hourly Rate*
│       │   │   ├── Amount (input)
│       │   │   └── Currency (select)
│       │   ├── Minimum Project Budget
│       │   └── "Displayed publicly"
│       │
│       ├── Specializations*
│       │   ├── [+ Add Specialization]
│       │   └── Multi-select dropdown
│       │       ├── BCP Development
│       │       ├── Risk Management
│       │       ├── Crisis Management
│       │       └── (12 more...)
│       │
│       ├── Industries Served
│       │   ├── [+ Add Industry]
│       │   └── Multi-select
│       │
│       ├── Skills & Technologies
│       │   ├── [+ Add Skill]
│       │   └── Skills Pills (removable)
│       │
│       └── Work Preferences
│           ├── Remote Work (toggle)
│           ├── Onsite Work (toggle)
│           ├── Willing to Travel (toggle)
│           └── Preferred Project Duration
│
├── [TAB: Certifications]
│   │
│   └── Certifications Manager
│       ├── [+ Add Certification]
│       │
│       └── Certification Cards (list)
│           │
│           └── Certification Card
│               ├── Edit Mode / View Mode toggle
│               │
│               ├── [Edit Mode]
│               │   ├── Certification Name*
│               │   ├── Issuing Organization*
│               │   ├── Issue Date*
│               │   ├── Expiry Date (optional)
│               │   ├── Credential ID
│               │   ├── Credential URL
│               │   ├── Logo Upload
│               │   ├── [Save] [Cancel] [Delete]
│               │   └── Verification Status
│               │       ├── "Pending verification"
│               │       └── [Request Verification]
│               │
│               └── [View Mode]
│                   ├── Logo + Name
│                   ├── Organization
│                   ├── Dates
│                   ├── Credential ID
│                   ├── Verified badge (if verified)
│                   ├── [View Credential] (external link)
│                   └── [✏️ Edit] [🗑️ Delete]
│
├── [TAB: Portfolio]
│   │
│   └── Portfolio Manager
│       ├── [+ Add Project]
│       │
│       └── Portfolio Item Cards (draggable grid)
│           │
│           └── Portfolio Card
│               ├── [Edit Mode]
│               │   ├── Project Name*
│               │   ├── Client/Organization
│               │   ├── Industry
│               │   ├── Date Range*
│               │   ├── Your Role*
│               │   ├── Project Type (dropdown)
│               │   ├── Description* (rich text, 300 words)
│               │   ├── Key Achievements* (bullets)
│               │   ├── Team Size (number)
│               │   ├── Technologies/Methods Used
│               │   ├── Media
│               │   │   ├── Featured Image
│               │   │   ├── Gallery (5 images max)
│               │   │   └── Attachments (PDF)
│               │   ├── Featured (toggle) - pin to top
│               │   └── [Save] [Cancel] [Delete]
│               │
│               └── [View Mode]
│                   ├── Featured banner (if featured)
│                   ├── Thumbnail
│                   ├── Title
│                   ├── Client + Date
│                   ├── Description (truncated)
│                   ├── [Edit] [Delete] [Reorder ⋮⋮]
│                   └── Visibility toggle (Public/Private)
│
├── [TAB: Privacy]
│   │
│   └── Privacy Settings (cards)
│       │
│       ├── Profile Visibility
│       │   ├── Who can see your profile?
│       │   │   ├── ○ Everyone (Public)
│       │   │   ├── ○ Logged-in users only
│       │   │   └── ○ Private (hidden)
│       │   │
│       │   ├── Show my real name (toggle)
│       │   ├── Show my email (toggle)
│       │   └── Show my location (toggle)
│       │
│       ├── Activity Privacy
│       │   ├── Show my activity feed (toggle)
│       │   ├── Show courses I'm taking (toggle)
│       │   ├── Show my achievements (toggle)
│       │   └── Show leaderboard ranking (toggle)
│       │
│       ├── Contact Preferences
│       │   ├── Who can message me?
│       │   │   ├── ○ Anyone
│       │   │   ├── ○ Verified users only
│       │   │   └── ○ No one
│       │   │
│       │   └── Allow contact from clients (toggle)
│       │
│       └── Data & Privacy
│           ├── [Download My Data]
│           ├── [Delete Account] (warning)
│           └── Privacy Policy link
│
└── [TAB: Notifications]
    │
    └── Notification Preferences (cards)
        │
        ├── Email Notifications
        │   ├── New Messages (toggle)
        │   ├── New Project Invites (toggle)
        │   ├── Course Updates (toggle)
        │   ├── Forum Replies (toggle)
        │   ├── Weekly Digest (toggle)
        │   └── Marketing Emails (toggle)
        │
        ├── Push Notifications
        │   ├── Enable Push (master toggle)
        │   ├── New Messages
        │   ├── Mentions
        │   ├── Project Updates
        │   └── Learning Reminders
        │
        ├── In-App Notifications
        │   └── (Same categories as email)
        │
        └── Notification Frequency
            ├── ○ Real-time
            ├── ○ Daily digest
            └── ○ Weekly digest

┌────────────────────────────────────────────────────────────────┐
│         /dashboard/messages - MESSAGING CENTER                  │
└────────────────────────────────────────────────────────────────┘
├── Layout (3 columns)
│   │
│   ├── LEFT: Conversations List (300px)
│   │   │
│   │   ├── Header
│   │   │   ├── "Messages"
│   │   │   └── [+ New Message]
│   │   │
│   │   ├── Tabs
│   │   │   ├── All (default)
│   │   │   ├── Unread (badge count)
│   │   │   └── Archived
│   │   │
│   │   ├── Search Conversations
│   │   │
│   │   └── Conversation List
│   │       │
│   │       └── Conversation Card
│   │           ├── Avatar (with online dot)
│   │           ├── Name
│   │           ├── Last Message (truncated)
│   │           ├── Timestamp
│   │           ├── Unread badge (if unread)
│   │           └── [Active/Selected state]
│   │
│   ├── CENTER: Chat Window (flexible)
│   │   │
│   │   ├── Chat Header
│   │   │   ├── Participant Info
│   │   │   │   ├── Avatar
│   │   │   │   ├── Name + Status
│   │   │   │   └── Last seen / Active now
│   │   │   │
│   │   │   └── Actions
│   │   │       ├── [📞 Call] (future)
│   │   │       ├── [🔍 Search in Chat]
│   │   │       ├── [⋯ More]
│   │   │       └── [✕ Close] (mobile)
│   │   │
│   │   ├── Messages Area (scrollable)
│   │   │   │
│   │   │   └── Message Bubbles
│   │   │       ├── [Sent] (right aligned, blue)
│   │   │       │   ├── Text content
│   │   │       │   ├── Attachments
│   │   │       │   ├── Timestamp
│   │   │       │   └── Status (✓ sent, ✓✓ read)
│   │   │       │
│   │   │       └── [Received] (left aligned, gray)
│   │   │           ├── Avatar (small)
│   │   │           ├── Text content
│   │   │           ├── Attachments
│   │   │           └── Timestamp
│   │   │
│   │   ├── Typing Indicator
│   │   │   └── "[Name] is typing..."
│   │   │
│   │   └── Message Input
│   │       ├── [📎 Attach]
│   │       ├── [😊 Emoji]
│   │       ├── Text Input (multiline)
│   │       └── [Send] button
│   │
│   └── RIGHT: Participant Info Sidebar (250px, collapsible)
│       │
│       ├── Profile Card
│       │   ├── Avatar (large)
│       │   ├── Name + Title
│       │   ├── Verified badge
│       │   ├── Rating (if specialist)
│       │   └── [View Full Profile]
│       │
│       ├── Quick Actions
│       │   ├── [💼 Hire for Project]
│       │   ├── [🎓 View Courses] (if instructor)
│       │   └── [🚩 Report]
│       │
│       ├── Shared Media & Files
│       │   ├── Photos (grid)
│       │   └── Files (list)
│       │
│       └── Chat Settings
│           ├── [🔇 Mute Conversation]
│           ├── [📁 Archive]
│           └── [🗑️ Delete Chat]
│
└── New Message Modal (overlay)
    ├── "New Message"
    ├── To: (search/select users)
    ├── Subject (optional)
    ├── Message (textarea)
    └── [Send] [Cancel]

---

## 🎨 Design System Guidelines

### Color Palette
```
Primary:     #2563EB (Blue 600)
Secondary:   #7C3AED (Purple 600)
Success:     #059669 (Green 600)
Warning:     #D97706 (Amber 600)
Error:       #DC2626 (Red 600)
Info:        #0891B2 (Cyan 600)

Gray Scale:
50:  #F9FAFB
100: #F3F4F6
200: #E5E7EB
300: #D1D5DB
400: #9CA3AF
500: #6B7280
600: #4B5563
700: #374151
800: #1F2937
900: #111827
```

### Typography
```
Headings: Inter (Google Font)
Body:     Inter
Code:     JetBrains Mono

Sizes:
h1: 2.5rem (40px) - bold
h2: 2rem (32px) - bold
h3: 1.5rem (24px) - semibold
h4: 1.25rem (20px) - semibold
body: 1rem (16px) - regular
small: 0.875rem (14px) - regular
```

### Spacing (Tailwind units)
```
xs:  0.5rem (8px)
sm:  0.75rem (12px)
md:  1rem (16px)
lg:  1.5rem (24px)
xl:  2rem (32px)
2xl: 3rem (48px)
```

### Border Radius
```
sm: 0.25rem (4px) - buttons, badges
md: 0.5rem (8px) - cards, inputs
lg: 0.75rem (12px) - larger cards
xl: 1rem (16px) - modals
full: 9999px - pills, avatars
```

### Shadows
```
sm:  0 1px 2px rgba(0,0,0,0.05)
md:  0 4px 6px rgba(0,0,0,0.07)
lg:  0 10px 15px rgba(0,0,0,0.1)
xl:  0 20px 25px rgba(0,0,0,0.15)
```

### Components Library (shadcn/ui)
```
✅ Ready to use:
- Button (primary, secondary, outline, ghost)
- Card
- Badge
- Avatar
- Input, Textarea
- Select, Multi-select
- Checkbox, Radio, Switch
- Tabs
- Dialog, Modal
- Dropdown Menu
- Progress Bar
- Slider
- Toast Notifications
- Accordion
- Separator
- Label
- Tooltip
- Skeleton Loader
- Data Table
```

---

## 🚀 Responsive Breakpoints

```typescript
breakpoints: {
  'sm': '640px',   // Mobile landscape, small tablets
  'md': '768px',   // Tablets
  'lg': '1024px',  // Laptops
  'xl': '1280px',  // Desktops
  '2xl': '1536px'  // Large desktops
}

Layout Rules:
- Mobile First approach
- 3 columns → 2 columns (lg) → 1 column (md)
- Sidebar collapsible on mobile (hamburger menu)
- Stack cards vertically on mobile
- Horizontal scroll for tables/grids on mobile
```

---

## 🔐 User Roles & Access Control

### Role Matrix

| Feature                  | Guest | Learner | Specialist | Client | Moderator | Admin |
|--------------------------|-------|---------|------------|--------|-----------|-------|
| View Knowledge           | ✅    | ✅      | ✅         | ✅     | ✅        | ✅    |
| Create Knowledge         | ❌    | ✅      | ✅         | ✅     | ✅        | ✅    |
| View Forum               | ✅    | ✅      | ✅         | ✅     | ✅        | ✅    |
| Post in Forum            | ❌    | ✅      | ✅         | ✅     | ✅        | ✅    |
| Moderate Forum           | ❌    | ❌      | ❌         | ❌     | ✅        | ✅    |
| Enroll in Courses        | ❌    | ✅      | ✅         | ✅     | ✅        | ✅    |
| View Simulations         | ❌    | ✅      | ✅         | ✅     | ✅        | ✅    |
| Run Simulations          | ❌    | ✅      | ✅         | ✅     | ✅        | ✅    |
| View Specialists         | ✅    | ✅      | ✅         | ✅     | ✅        | ✅    |
| Become Specialist        | ❌    | ✅      | ✅         | ❌     | ❌        | ❌    |
| Post Projects            | ❌    | ❌      | ❌         | ✅     | ❌        | ✅    |
| Submit Proposals         | ❌    | ❌      | ✅         | ❌     | ❌        | ❌    |
| Manage Users             | ❌    | ❌      | ❌         | ❌     | ❌        | ✅    |
| Platform Settings        | ❌    | ❌      | ❌         | ❌     | ❌        | ✅    |

---

## 🧭 Navigation Flows

### Guest → Registered User (Learner)
```
Homepage → [Sign Up]
    ↓
Registration Wizard
    ├── Step 1: Email + Password
    ├── Step 2: Profile Info (name, location)
    ├── Step 3: Interests (select topics)
    └── Step 4: Welcome Tutorial
    ↓
Dashboard → Welcome Modal
    ├── Quick Tour (6 steps)
    └── Suggested First Actions
```

### Learner → Specialist Upgrade
```
Dashboard → [Become a Specialist]
    ↓
Specialist Onboarding Wizard
    ├── Step 1: Verify Identity
    ├── Step 2: Professional Info
    │   ├── Title, Bio
    │   ├── Specializations
    │   └── Hourly Rate
    ├── Step 3: Certifications (min 1)
    ├── Step 4: Portfolio (min 1 project)
    ├── Step 5: Background Check (optional)
    └── Step 6: Review & Submit
    ↓
[Under Review] status (1-3 days)
    ↓
[Approved] → Full Specialist Access
    └── Welcome Email + Onboarding Checklist
```

### Client Onboarding
```
Homepage → [Post a Project]
    ↓
(If not registered)
Quick Registration
    ├── Email, Password
    ├── Company Name
    └── Basic Info
    ↓
Post Project Wizard
    ├── Step 1: Project Details
    │   ├── Title, Description
    │   ├── Skills Required
    │   └── Budget & Timeline
    ├── Step 2: Requirements
    │   └── Deliverables
    ├── Step 3: Preferences
    │   └── Specialist criteria
    └── Step 4: Publish
    ↓
Project Published → Wait for Proposals
```

---

## 📱 Mobile-First Design Adaptations

### Mobile Navigation (< 768px)
```
┌─────────────────────────────────────┐
│ [☰] Logo         [🔍] [🔔] [👤]    │ ← Top bar (sticky)
└─────────────────────────────────────┘

[☰] Hamburger Menu (slide-in sidebar)
    ├── 🏠 Home
    ├── 📚 Knowledge
    ├── 🎓 Learning
    ├── 💼 Marketplace
    ├── 🎮 Simulations
    ├── 💬 Community
    ├── ──────────
    ├── 👤 Profile
    ├── 💬 Messages (3)
    ├── ⚙️ Settings
    └── 🚪 Logout
```

### Mobile Card Design
- Stack vertically
- Full width
- Larger touch targets (min 44px)
- Swipe actions (left/right)
- Pull-to-refresh

### Mobile Forms
- One field per row
- Native inputs (date, time pickers)
- Sticky Submit button at bottom
- Auto-save drafts

---

## ⚡ Performance & Optimization

### Loading Strategies
```typescript
// Code splitting
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Learning = lazy(() => import('./pages/Learning'))

// Image optimization
<Image
  src="/path/to/image.jpg"
  width={800}
  height={600}
  loading="lazy"
  placeholder="blur"
/>

// API data caching (React Query)
const { data } = useQuery('courses', fetchCourses, {
  staleTime: 5 * 60 * 1000, // 5 minutes
  cacheTime: 10 * 60 * 1000  // 10 minutes
})
```

### Bundle Size Optimization
- Tree shaking
- Code splitting per route
- Dynamic imports for heavy components
- Remove unused shadcn components

### SEO Optimization
- Server-side rendering (Next.js)
- Meta tags per page
- Open Graph images
- Sitemap.xml
- robots.txt

---

## 🎯 Key User Journeys (Full Flows)

### Journey 1: "I want to learn BCM"
```
Guest User
  ↓
1. Visit Homepage
  ↓
2. Click "Browse Courses" or "Get Started"
  ↓
3. View Course Catalog (can browse without login)
  ↓
4. Click on Course → View Details
  ↓
5. [Enroll Now] → Prompted to Sign Up/Login
  ↓
6. Register Account → Quick Form
  ↓
7. Complete Enrollment → Payment (if paid)
  ↓
8. Start Learning → Course Player
  ↓
9. Complete Lessons → Track Progress
  ↓
10. Take Assessment → Pass/Fail
  ↓
11. Earn Certificate → Download/Share
  ↓
12. Earn Badges & XP → Level Up
  ↓
13. Explore More Courses → Repeat
```

### Journey 2: "I need a BCM consultant"
```
Client (new)
  ↓
1. Visit Homepage
  ↓
2. Click "Find Experts" or "Post Project"
  ↓
3. Browse Specialists
  ↓
4. Filter by: Specialization, Location, Rate
  ↓
5. View Specialist Profile
  ↓
6. Review Portfolio, Certifications, Reviews
  ↓
7. [Contact] → Prompted to Register
  ↓
8. Quick Client Registration
  ↓
9. Send Message or [Hire Directly]
  ↓
10. Create Project Brief
  ↓
11. Post Project → Wait for Proposals
  ↓
12. Review Proposals (3-10 received)
  ↓
13. Compare Specialists
  ↓
14. Accept Proposal → Contract
  ↓
15. Project Kickoff → Milestones
  ↓
16. Track Progress → Messages
  ↓
17. Project Completion
  ↓
18. Leave Review → Rate Specialist
  ↓
19. Request Case Study (optional)
```

### Journey 3: "I want to test my BCM preparedness"
```
Registered User
  ↓
1. Dashboard → Click "Simulations"
  ↓
2. View Simulation Platform
  ↓
3. Choose:
   a) Pre-built Scenario (Library)
   b) Create Custom Simulation
  ↓
4. [If Library] Browse Scenarios
   ├── Filter by Threat Type
   └── Select Scenario
  ↓
5. Configure Parameters
   ├── Team Size
   ├── Duration
   └── Difficulty
  ↓
6. Launch Simulation
  ↓
7. Receive Injects (email, calls, alerts)
  ↓
8. Make Decisions → Submit Responses
  ↓
9. Track Timeline → Progress through scenario
  ↓
10. Complete Simulation → Time Runs Out
  ↓
11. View Results Dashboard
   ├── Decision Quality Score
   ├── Response Time
   ├── Resource Usage
   └── Overall Performance
  ↓
12. Review Debrief
   ├── What Went Well
   ├── Areas for Improvement
   └── Recommendations
  ↓
13. Earn Badge (if threshold met)
  ↓
14. Download Report (PDF)
  ↓
15. Share Results (optional)
  ↓
16. Try Another Scenario or Advanced Version
```

---

## 🎨 Interaction Patterns

### Hover States
- Cards: Slight elevation + shadow
- Buttons: Darken by 10%
- Links: Underline appears
- Images: Slight zoom (1.05x)

### Click/Tap Feedback
- Buttons: Scale down (0.95x) + ripple effect
- Cards: Quick scale down then up
- Icons: Bounce animation

### Loading States
- Skeleton loaders for cards
- Spinner for buttons
- Progress bar for page loads
- Shimmer effect for images

### Empty States
- Friendly illustration
- Clear message "No items yet"
- Primary action button
- Helpful tips/suggestions

### Error States
- Red border on invalid inputs
- Inline error messages
- Toast notifications for API errors
- Retry button for failed loads

---

## 🔔 Notifications & Alerts

### Types
1. **Success** (green) - Action completed
2. **Error** (red) - Something went wrong
3. **Warning** (amber) - Caution required
4. **Info** (blue) - General information

### Placement
- **Toast** (bottom-right) - Temporary (3-5s)
- **Banner** (top) - Important, persistent
- **Inline** (within form/card) - Field-specific
- **Modal** (center) - Critical actions

### Examples
```typescript
// Success
toast.success('Course enrollment successful!')

// Error
toast.error('Failed to save changes. Please try again.')

// Warning
banner.warning('Your certificate expires in 30 days')

// Info
toast.info('New course available: Advanced BCM')
```

---

## 🎯 Call-to-Action Strategy

### Primary CTAs (Blue, prominent)
- "Enroll Now"
- "Start Learning"
- "Contact Specialist"
- "Post Project"
- "Launch Simulation"

### Secondary CTAs (White/Gray, outlined)
- "Learn More"
- "View Details"
- "Save for Later"
- "Preview"

### Tertiary CTAs (Text links)
- "Skip for now"
- "Cancel"
- "Back"

### CTA Placement Rules
1. One primary CTA per card/section
2. Right-aligned (LTR languages)
3. Sufficient padding (min 16px)
4. Descriptive text ("Start Course" > "Continue")

---

## 📊 Analytics & Tracking Events

### Key Events to Track
```javascript
// User Actions
- page_view
- sign_up
- login
- logout

// Learning
- course_enroll
- lesson_start
- lesson_complete
- quiz_submit
- certificate_earned

// Marketplace
- specialist_view
- contact_specialist
- project_post
- proposal_submit

// Simulations
- simulation_start
- simulation_complete
- scenario_download

// Community
- article_view
- forum_post
- comment_post
- vote_cast

// Engagement
- search_query
- filter_apply
- share_content
- download_file
```

---

## 🚀 Next Steps for Implementation

### Phase 1: Foundation (Week 1)
1. Setup Next.js project with TypeScript
2. Install dependencies (shadcn/ui, React Query, Zustand)
3. Setup Tailwind CSS + Design System
4. Create Layout components
5. Implement Authentication flow

### Phase 2: Core Pages (Week 2-3)
1. Homepage
2. Knowledge Center
3. Learning Platform
4. Marketplace (Specialists)
5. Dashboard (basic)

### Phase 3: Advanced Features (Week 4-5)
1. Simulations Platform
2. Community Forum
3. Messaging System
4. Complete Dashboard
5. Profile Management

### Phase 4: Polish & Launch (Week 6)
1. Mobile responsiveness
2. Accessibility (a11y)
3. Performance optimization
4. E2E testing
5. Production deployment

---

**Architecture Status:** 🎨 COMPLETE - God-Level Design
**Ready for:** Frontend Implementation
**Estimated Timeline:** 6 weeks to MVP
**Team Required:** 2 frontend devs + 1 designer

---

**Created by:** Claude Code (Architect Mode: GOD 🏛️)
**Date:** 2025-10-02
**Version:** 1.0.0 - MASTER BLUEPRINT
