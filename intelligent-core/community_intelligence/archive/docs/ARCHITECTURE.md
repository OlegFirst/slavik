# Community Intelligence Service - Architecture

**Version:** 1.0
**Date:** 2025-10-04
**Port:** 8030

---

## 🎯 PURPOSE

Transform passive case collection into active community-driven knowledge creation through:
- **Workflow Integration:** Auto-capture success stories
- **Peer Review:** Quality assurance through expert validation
- **Reputation Economy:** Incentivize contributions
- **Case Library:** Searchable knowledge base

---

## 🏗️ ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│              Community Intelligence Service                  │
│                      (Port 8030)                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            API Layer (FastAPI)                       │  │
│  │  - Contribution endpoints                            │  │
│  │  - Peer review endpoints                             │  │
│  │  - Reputation endpoints                              │  │
│  │  - Case library search                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Business Logic Services                      │  │
│  │  - ContributionService (existing)                    │  │
│  │  - PeerReviewService (NEW)                           │  │
│  │  - ReputationEngine (NEW)                            │  │
│  │  - WorkflowIntegrationService (NEW)                  │  │
│  │  - CaseLibraryService (enhanced)                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Event Handlers                            │  │
│  │  - workflow.*.completed → offer contribution         │  │
│  │  - case.contribution.submitted → assign reviewers    │  │
│  │  - review.submitted → check completion               │  │
│  │  - case.approved → update reputation                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Data Layer                              │  │
│  │  - PostgreSQL (contributions, reviews, reputation)   │  │
│  │  - Redis (cache, notifications)                      │  │
│  │  - EventBus (async communication)                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         ↓                    ↓                    ↓
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Workflow      │  │  Marketplace    │  │  Notification   │
│  Intelligence   │  │    Service      │  │    Service      │
│   (Consumer)    │  │   (Consumer)    │  │   (Consumer)    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## 📊 DATA MODEL

### Core Tables (community schema)

```sql
-- Case contributions
CREATE TABLE community.case_contributions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contributor_id UUID NOT NULL REFERENCES auth.users(id),
    org_id UUID NOT NULL,

    -- Case data
    case_data JSONB NOT NULL,  -- Anonymized workflow data
    module VARCHAR(50) NOT NULL,  -- 'bia', 'risk', 'governance', etc.
    tags TEXT[] DEFAULT '{}',
    original_org_type VARCHAR(100),

    -- Review process
    status VARCHAR(50) DEFAULT 'pending_review',  -- pending_review, in_review, approved, rejected
    reviewers UUID[] DEFAULT '{}',  -- Assigned reviewer IDs
    review_deadline TIMESTAMP,

    -- Approval
    approved_at TIMESTAMP,
    added_to_library BOOLEAN DEFAULT false,
    library_case_id UUID,

    -- Metadata
    submitted_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Peer reviews
CREATE TABLE community.peer_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contribution_id UUID NOT NULL REFERENCES community.case_contributions(id),
    reviewer_id UUID NOT NULL REFERENCES auth.users(id),

    -- Review decision
    approved BOOLEAN NOT NULL,
    quality_score INTEGER CHECK (quality_score BETWEEN 1 AND 10),

    -- Detailed feedback
    feedback TEXT,
    suggested_improvements TEXT,

    -- Quality checks
    anonymization_ok BOOLEAN DEFAULT true,
    relevance_ok BOOLEAN DEFAULT true,
    completeness_ok BOOLEAN DEFAULT true,
    lessons_clear BOOLEAN DEFAULT true,

    -- Metadata
    reviewed_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- User reputation (enhanced)
CREATE TABLE community.user_reputation (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id),
    org_id UUID NOT NULL,

    -- Total points
    total_points INTEGER DEFAULT 0,
    level VARCHAR(50) DEFAULT 'newcomer',  -- newcomer, contributor, expert, master

    -- Module-specific expertise
    expertise JSONB DEFAULT '{}',  -- {"bia": 150, "risk": 80}

    -- Contribution metrics
    contribution_points INTEGER DEFAULT 0,
    contributions_count INTEGER DEFAULT 0,
    cases_approved INTEGER DEFAULT 0,
    cases_rejected INTEGER DEFAULT 0,
    avg_case_quality DECIMAL(3,2) DEFAULT 0.0,
    first_contribution TIMESTAMP,

    -- Review metrics
    review_points INTEGER DEFAULT 0,
    reviews_count INTEGER DEFAULT 0,
    helpful_reviews_count INTEGER DEFAULT 0,

    -- Marketplace impact
    marketplace_priority INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Reputation transactions
CREATE TABLE community.reputation_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id),

    -- Transaction details
    points INTEGER NOT NULL,
    reason VARCHAR(100) NOT NULL,  -- 'case_approved', 'peer_review', etc.
    related_contribution_id UUID REFERENCES community.case_contributions(id),

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔄 WORKFLOWS

### Workflow 1: Case Contribution

```
1. User completes BIA workflow
   ↓
2. EventBus: 'workflow.bia.completed'
   ↓
3. WorkflowIntegrationService.on_workflow_completed()
   - Checks if user opted-in to share
   - Auto-collects case data from workflow
   ↓
4. ContributionService.submit_case()
   - Anonymizes data
   - Creates contribution record
   - Assigns 3 peer reviewers (smart matching)
   - Publishes 'case.contribution.submitted'
   ↓
5. NotificationService: Emails sent to reviewers
```

### Workflow 2: Peer Review

```
1. Reviewer receives notification
   ↓
2. Reviewer views contribution (anonymized)
   ↓
3. Reviewer submits review:
   - Approved: Yes/No
   - Quality score: 1-10
   - Feedback: Text
   - Quality checks: 4 booleans
   ↓
4. PeerReviewService.submit_review()
   - Saves review
   - Awards +5 reputation to reviewer
   - Publishes 'review.submitted'
   ↓
5. PeerReviewService.check_completion()
   - If 3 reviews received:
     - 2+ approve → approve_contribution()
     - Otherwise → reject_contribution()
```

### Workflow 3: Contribution Approval

```
1. PeerReviewService.approve_contribution()
   ↓
2. Add to Case Library
   - CaseLibraryService.add_community_case()
   - Store in workflow_intelligence.cases table
   ↓
3. Award reputation
   - Calculate points: 50 * (avg_quality_score / 10)
   - ReputationEngine.award_points()
   - Update expertise in module
   ↓
4. Update contribution record
   - status = 'approved'
   - library_case_id = new_case_id
   ↓
5. Notify contributor
   - "Your case approved! +42 reputation points"
   ↓
6. Publish 'case.approved' event
   - Marketplace can boost specialist priority
```

---

## 🔌 API ENDPOINTS

### Contribution Management

```
POST   /api/v1/community/contributions
       - Submit new contribution
       - Body: {case_data, module, opt_in_to_share}

GET    /api/v1/community/contributions/{contribution_id}
       - Get contribution details (for reviewers)

GET    /api/v1/community/contributions/my
       - Get user's contributions with status

DELETE /api/v1/community/contributions/{contribution_id}
       - Withdraw contribution (before approval)
```

### Peer Review

```
POST   /api/v1/community/reviews
       - Submit peer review
       - Body: {contribution_id, approved, quality_score, feedback, ...}

GET    /api/v1/community/reviews/pending
       - Get contributions pending user's review

GET    /api/v1/community/reviews/my
       - Get user's submitted reviews
```

### Reputation

```
GET    /api/v1/community/reputation/{user_id}
       - Get user reputation profile

GET    /api/v1/community/reputation/leaderboard
       - Get top contributors (by module or overall)

GET    /api/v1/community/reputation/transactions/{user_id}
       - Get reputation transaction history
```

### Case Library

```
GET    /api/v1/community/cases/search
       - Search cases by module, industry, tags
       - Query params: module, industry, tags, min_quality, limit

GET    /api/v1/community/cases/{case_id}
       - Get case details (anonymized)

GET    /api/v1/community/cases/similar
       - Find similar cases for current workflow
       - Body: {org_context, current_workflow_state}
```

---

## 🎯 SMART REVIEWER ASSIGNMENT

### Algorithm

```python
def assign_reviewers(contribution, count=3):
    """
    Smart matching criteria:
    1. Expertise: reputation.expertise[module] >= 50
    2. Diversity: different org_id than contributor
    3. Availability: pending_reviews < 5
    4. Quality: high helpful_reviews_count preferred
    5. Freshness: recent activity preferred
    """

    candidates = db.query("""
        SELECT u.user_id, u.expertise, u.pending_reviews_count
        FROM community.user_reputation u
        WHERE u.expertise->:module >= 50
          AND u.user_id != :contributor_id
          AND u.org_id != :contributor_org_id
          AND u.pending_reviews_count < 5
        ORDER BY
          u.expertise->:module DESC,
          u.helpful_reviews_count DESC,
          u.last_activity_at DESC
        LIMIT :count * 3
    """)

    # Select top 3
    return candidates[:count]
```

---

## 💎 REPUTATION CALCULATION

### Points Awarded

```python
REPUTATION_POINTS = {
    # Contributions
    'case_submitted': 10,           # Just for submitting
    'case_approved': 50,             # Base points on approval
    'case_quality_bonus': lambda score: int(50 * (score / 10)),  # 0-50 bonus

    # Reviews
    'peer_review': 5,                # Per review submitted
    'helpful_review': 10,            # When contributor marks helpful

    # Achievements
    'first_contribution': 25,
    'first_review': 10,
    '10_approved_cases': 100,
    '100_reviews': 200,
}

def calculate_level(total_points):
    if total_points >= 2000: return 'master'
    if total_points >= 500: return 'expert'
    if total_points >= 100: return 'contributor'
    return 'newcomer'
```

### Expertise Tracking

```python
def update_expertise(user_id, module, points):
    """
    Track module-specific expertise

    Example:
    user.expertise = {
        'bia': 150,      # 3 approved BIA cases
        'risk': 80,      # 1 approved risk case + 4 reviews
        'governance': 25 # 5 reviews
    }
    """

    user = get_reputation(user_id)
    current = user.expertise.get(module, 0)
    user.expertise[module] = current + points

    # Update marketplace priority
    user.marketplace_priority = calculate_priority(user)
```

---

## 🔔 NOTIFICATIONS

### Events Published

```python
EVENTS = {
    'case.contribution.submitted': {
        'data': {
            'contribution_id': UUID,
            'contributor_id': UUID,
            'module': str,
            'reviewers': [UUID]
        },
        'subscribers': ['notification-service']
    },

    'case.review.assigned': {
        'data': {
            'contribution_id': UUID,
            'reviewer_id': UUID,
            'deadline': datetime
        },
        'subscribers': ['notification-service']
    },

    'case.approved': {
        'data': {
            'contribution_id': UUID,
            'contributor_id': UUID,
            'library_case_id': UUID,
            'reputation_earned': int
        },
        'subscribers': ['marketplace-service', 'notification-service']
    },

    'reputation.level_up': {
        'data': {
            'user_id': UUID,
            'old_level': str,
            'new_level': str,
            'total_points': int
        },
        'subscribers': ['notification-service', 'gamification-service']
    }
}
```

---

## 🔒 SECURITY

### Anonymization

```python
def anonymize_case_data(case_data):
    """
    Remove identifying information:
    - Organization name → org type (e.g., "hospital_200beds")
    - Employee names → roles (e.g., "BCM Manager")
    - Specific locations → regions (e.g., "Northeast US")
    - Exact dates → relative (e.g., "Q3 2024")
    - IP addresses → removed
    - Proprietary data → removed
    """

    anonymized = {
        'org_context': {
            'type': extract_org_type(case_data.org),
            'industry': case_data.industry,
            'size': categorize_size(case_data.employee_count),
            'region': generalize_location(case_data.location)
        },
        'workflow': case_data.workflow,  # Keep workflow structure
        'metrics': case_data.metrics,    # Keep numerical data
        'success_patterns': case_data.success_patterns,
        'challenges': case_data.challenges
    }

    return anonymized
```

### Access Control

```python
# Who can see what:

CONTRIBUTION_ACCESS = {
    'pending_review': ['contributor', 'assigned_reviewers', 'admins'],
    'in_review': ['contributor', 'assigned_reviewers', 'admins'],
    'approved': ['all_users'],  # Public in case library
    'rejected': ['contributor', 'admins']
}

# RLS policies
"""
CREATE POLICY contribution_access ON community.case_contributions
    FOR SELECT
    USING (
        status = 'approved'  -- All can see approved
        OR contributor_id = auth.uid()  -- Contributors see own
        OR auth.uid() = ANY(reviewers)  -- Reviewers see assigned
        OR is_admin(auth.uid())  -- Admins see all
    );
"""
```

---

## 📈 METRICS

### Service Health

```python
PROMETHEUS_METRICS = {
    'contributions_total': Counter('Total contributions submitted'),
    'contributions_approved': Counter('Approved contributions'),
    'contributions_rejected': Counter('Rejected contributions'),
    'reviews_submitted': Counter('Peer reviews submitted'),
    'reputation_points_awarded': Counter('Total reputation points'),
    'case_library_size': Gauge('Total cases in library'),
    'active_reviewers': Gauge('Users with pending reviews'),
    'avg_review_time': Histogram('Time to complete review')
}
```

---

## 🧪 TESTING STRATEGY

### Unit Tests
- Service methods (ContributionService, PeerReviewService, etc.)
- Anonymization logic
- Reputation calculations
- Reviewer assignment algorithm

### Integration Tests
- API endpoints
- EventBus integration
- Database transactions
- Case Library integration

### E2E Tests
- Full contribution workflow
- Peer review process
- Reputation updates
- Notification delivery

---

## 🚀 DEPLOYMENT

### Dependencies
```
- PostgreSQL (Supabase)
- Redis (Upstash)
- EventBus service
- Notification service (optional)
- Workflow Intelligence service
```

### Environment Variables
```
SERVICE_NAME=community-intelligence
PORT=8030

DATABASE_URL=...
REDIS_URL=...
EVENTBUS_URL=http://localhost:8001

# AI for anonymization validation
ANTHROPIC_API_KEY=...

# Thresholds
MIN_REVIEWERS=3
PEER_REVIEW_DEADLINE_DAYS=7
MIN_EXPERTISE_FOR_REVIEW=50
```

---

**Ready for implementation!** 🔥
