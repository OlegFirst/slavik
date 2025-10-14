# Community Intelligence Service - Technical Specification

**Version:** 1.0.0
**Port:** 8030
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Services](#core-services)
4. [Database Schema](#database-schema)
5. [API Reference](#api-reference)
6. [Integration Points](#integration-points)
7. [Configuration](#configuration)
8. [Deployment](#deployment)

---

## Overview

### Purpose

Community Intelligence Service transforms passive case collection into active community-driven knowledge creation. The service enables organizations to contribute their BCM experiences, undergo peer review, earn reputation, and build a searchable case library that benefits the entire community.

### Key Features

- **Automated Case Capture:** Workflow completion triggers contribution offers
- **Peer Review System:** Smart matching of reviewers based on expertise
- **Reputation Economy:** Points-based gamification incentivizing quality contributions
- **Case Library:** Searchable repository of best practices
- **Privacy-Preserving:** Anonymization of sensitive organizational data

### Value Proposition

Organizations benefit from:
- Learning from peer experiences without direct consultation
- Building reputation as BCM experts
- Contributing to community knowledge base
- Accessing vetted, high-quality case studies

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│            Community Intelligence Service                    │
│                    (Port 8030)                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  API Layer                                                  │
│  ├── Contributions API                                      │
│  ├── Peer Reviews API                                       │
│  ├── Reputation API                                         │
│  └── Case Library API                                       │
│                                                             │
│  Service Layer                                              │
│  ├── Contribution Service                                   │
│  ├── Peer Review Service                                    │
│  ├── Reputation Engine                                      │
│  ├── Anonymizer Service                                     │
│  ├── Workflow Integration Service                           │
│  └── Case Library Bridge                                    │
│                                                             │
│  Event Integration                                          │
│  ├── Workflow Completion Subscriber                         │
│  └── Event Publishers                                       │
│                                                             │
│  Data Layer                                                 │
│  ├── PostgreSQL (Contributions, Reviews, Reputation)        │
│  ├── Redis (Cache)                                          │
│  └── EventBus Integration                                   │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
Workflow Service                Community Intelligence          Case Library
      |                                 |                            |
      |-- workflow_completed ---------->|                            |
      |                                 |                            |
      |                          Extract case data                  |
      |                          Apply anonymization                |
      |                                 |                            |
      |                          Offer contribution                 |
      |<-------- contribution_offer ----|                            |
      |                                 |                            |
User accepts                            |                            |
      |-- submit_contribution --------->|                            |
      |                                 |                            |
      |                          Create contribution                |
      |                          Assign 3 reviewers                 |
      |                                 |                            |
Reviewers notified                      |                            |
      |<-------- review_request --------|                            |
      |                                 |                            |
Reviews submitted                       |                            |
      |-- submit_reviews -------------->|                            |
      |                                 |                            |
      |                          Aggregate reviews                  |
      |                          Calculate scores                   |
      |                                 |                            |
2/3 approve                             |                            |
      |                          Update reputation                  |
      |                          Publish to library                 |
      |                                 |-- publish_case ----------->|
      |                                 |                            |
      |<-------- contribution_published-|                            |
```

---

## Core Services

### 1. Contribution Service

**Purpose:** Manage lifecycle of community contributions from creation to publication.

**Responsibilities:**
- Accept contribution submissions
- Validate contribution data
- Apply anonymization rules
- Track contribution status
- Handle contribution updates and deletions

**Key Methods:**

```python
class ContributionService:
    async def create_contribution(
        self,
        user_id: UUID,
        module: str,
        case_data: dict,
        auto_anonymize: bool = True
    ) -> Contribution:
        """
        Create new contribution

        Args:
            user_id: Contributing user ID
            module: BCM module (bia, risk, governance, etc.)
            case_data: Workflow results and metadata
            auto_anonymize: Apply anonymization automatically

        Returns:
            Created contribution with status 'pending_review'

        Process:
            1. Validate case_data structure
            2. Apply anonymization if enabled
            3. Create contribution record
            4. Trigger peer review assignment
            5. Notify user
        """

    async def get_user_contributions(
        self,
        user_id: UUID,
        status: Optional[str] = None
    ) -> List[Contribution]:
        """Get all contributions by user, optionally filtered by status"""

    async def delete_contribution(
        self,
        contribution_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete contribution (only if not yet published)

        Rules:
            - Can delete: draft, pending_review, in_review
            - Cannot delete: published, rejected
        """
```

**Data Model:**

```python
class Contribution:
    id: UUID
    user_id: UUID
    module: str  # bia, risk, governance, response, compliance
    case_data: dict  # Anonymized workflow results
    metadata: dict  # Context: industry, org_size, duration, etc.
    status: str  # draft, pending_review, in_review, published, rejected
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    review_score: Optional[float]  # Average from peer reviews
```

---

### 2. Peer Review Service

**Purpose:** Coordinate peer review process with smart reviewer matching.

**Reviewer Matching Algorithm:**

```python
class ReviewerMatcher:
    async def assign_reviewers(
        self,
        contribution: Contribution,
        count: int = 3
    ) -> List[UUID]:
        """
        Smart reviewer assignment based on:

        1. Expertise Score (50%):
           - Module expertise level (1-10)
           - Historical review quality
           - Domain knowledge

        2. Availability (30%):
           - Current pending reviews < threshold
           - Recent activity
           - Response time history

        3. Diversity (20%):
           - Different organizations
           - Geographic diversity
           - Industry diversity

        Returns:
            List of 3 reviewer user IDs
        """

        candidates = await self.get_eligible_reviewers(
            module=contribution.module,
            exclude_user=contribution.user_id
        )

        scored_candidates = []
        for candidate in candidates:
            score = (
                0.5 * await self.calculate_expertise_score(candidate, contribution) +
                0.3 * await self.calculate_availability_score(candidate) +
                0.2 * await self.calculate_diversity_score(candidate, contribution)
            )
            scored_candidates.append((candidate, score))

        # Select top 3
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return [candidate for candidate, score in scored_candidates[:count]]
```

**Review Submission:**

```python
class PeerReviewService:
    async def submit_review(
        self,
        contribution_id: UUID,
        reviewer_id: UUID,
        quality_score: int,  # 1-10
        feedback: str,
        recommendation: str  # approve, reject, revise
    ) -> Review:
        """
        Submit peer review

        Validation:
            - Reviewer must be assigned to this contribution
            - Quality score must be 1-10
            - Feedback required if recommendation is reject/revise

        Process:
            1. Validate reviewer assignment
            2. Create review record
            3. Update contribution review count
            4. If 3 reviews collected:
               - Calculate aggregate score
               - Determine approval (2/3 threshold)
               - Update reputation
               - Publish to case library if approved
        """
```

**Review Data Model:**

```python
class Review:
    id: UUID
    contribution_id: UUID
    reviewer_id: UUID
    quality_score: int  # 1-10
    feedback: str
    recommendation: str  # approve, reject, revise
    submitted_at: datetime

    # Detailed scoring (optional)
    completeness_score: Optional[int]  # 1-10
    clarity_score: Optional[int]  # 1-10
    usefulness_score: Optional[int]  # 1-10
```

**Approval Logic:**

```python
async def check_approval(contribution_id: UUID) -> bool:
    """
    Determine if contribution approved

    Rules:
        - Need exactly 3 reviews
        - At least 2/3 must recommend 'approve'
        - Average quality_score must be >= 6.0

    Returns:
        True if approved, False otherwise
    """
    reviews = await get_reviews(contribution_id)

    if len(reviews) != 3:
        return False

    approvals = sum(1 for r in reviews if r.recommendation == 'approve')
    avg_score = sum(r.quality_score for r in reviews) / 3

    return approvals >= 2 and avg_score >= 6.0
```

---

### 3. Reputation Engine

**Purpose:** Calculate and manage user reputation based on contributions and reviews.

**Reputation Points System:**

```python
REPUTATION_POINTS = {
    # Contributions
    'contribution_created': 5,
    'contribution_published': 50,
    'contribution_high_quality': 25,  # quality_score >= 9.0
    'contribution_rejected': -10,

    # Reviews
    'review_submitted': 3,
    'review_high_quality': 10,  # detailed, helpful feedback
    'review_consensus': 5,  # agrees with majority

    # Usage
    'case_helpful_vote': 2,  # someone found your case helpful
    'case_used': 1,  # your case viewed

    # Moderation
    'spam_detected': -100,
    'quality_violation': -25
}
```

**Module Expertise Levels:**

```python
class ExpertiseLevel:
    NOVICE = 1      # 0-99 points
    BEGINNER = 2    # 100-249 points
    INTERMEDIATE = 3  # 250-499 points
    ADVANCED = 4    # 500-999 points
    EXPERT = 5      # 1000-2499 points
    MASTER = 6      # 2500-4999 points
    AUTHORITY = 7   # 5000-9999 points
    LEGEND = 8      # 10000+ points
```

**Reputation Calculation:**

```python
class ReputationEngine:
    async def update_reputation(
        self,
        user_id: UUID,
        action: str,
        module: str,
        metadata: dict = None
    ) -> int:
        """
        Update user reputation

        Args:
            user_id: User to update
            action: Action performed (see REPUTATION_POINTS)
            module: BCM module (for module-specific expertise)
            metadata: Additional context

        Returns:
            New total reputation points

        Process:
            1. Calculate points for action
            2. Apply multipliers (streaks, badges, etc.)
            3. Update global reputation
            4. Update module-specific expertise
            5. Check for level up
            6. Award badges if earned
            7. Update leaderboard
        """

    async def get_user_reputation(
        self,
        user_id: UUID
    ) -> dict:
        """
        Get user reputation summary

        Returns:
            {
                'total_points': int,
                'global_rank': int,
                'level': int,
                'badges': List[Badge],
                'expertise_by_module': {
                    'bia': {'points': int, 'level': int},
                    'risk': {'points': int, 'level': int},
                    ...
                },
                'stats': {
                    'contributions_published': int,
                    'reviews_submitted': int,
                    'helpful_votes_received': int
                }
            }
        """
```

**Leaderboard:**

```python
async def get_leaderboard(
    module: Optional[str] = None,
    timeframe: str = 'all_time',  # all_time, month, week
    limit: int = 50
) -> List[dict]:
    """
    Get reputation leaderboard

    Args:
        module: Optional module filter (bia, risk, etc.)
        timeframe: Time window for ranking
        limit: Number of top users to return

    Returns:
        List of users sorted by reputation:
        [
            {
                'user_id': UUID,
                'username': str,  # anonymized if privacy settings
                'points': int,
                'rank': int,
                'level': int,
                'badge': str  # highest badge earned
            },
            ...
        ]
    """
```

---

### 4. Anonymizer Service

**Purpose:** Remove or generalize personally identifiable and competitively sensitive information from contributions.

**Anonymization Rules:**

```python
class AnonymizerService:
    ANONYMIZATION_RULES = {
        # Organization Info
        'org_name': 'REDACT',
        'org_address': 'GENERALIZE_REGION',
        'org_domain': 'REDACT',
        'org_emails': 'REDACT',

        # People
        'author_name': 'REDACT',
        'contact_name': 'REDACT',
        'stakeholder_names': 'REDACT',

        # Identifiers
        'case_id': 'GENERATE_NEW',
        'workflow_id': 'GENERATE_NEW',
        'timestamps': 'GENERALIZE_DATE',

        # Sensitive Data
        'revenue': 'GENERALIZE_RANGE',
        'employee_count': 'GENERALIZE_RANGE',
        'budget': 'GENERALIZE_RANGE',
        'vendor_names': 'GENERALIZE_TYPE',
        'customer_names': 'REDACT',

        # Process-Specific
        'process_names': 'KEEP',  # Generic names OK
        'criticality_scores': 'KEEP',
        'rto_values': 'KEEP',
        'dependencies': 'ANONYMIZE_ENTITIES'
    }

    async def anonymize_case(
        self,
        case_data: dict,
        org_context: dict
    ) -> dict:
        """
        Apply anonymization rules to case data

        Args:
            case_data: Raw workflow results
            org_context: Organization metadata

        Returns:
            Anonymized case data safe for public consumption

        Process:
            1. Scan for PII patterns (regex, NER)
            2. Apply rule-based anonymization
            3. Generalize sensitive values
            4. Validate anonymization quality
            5. Return anonymized data
        """

        anonymized = {}

        # Organization context
        anonymized['organization'] = {
            'industry': org_context['industry'],
            'size_category': self.categorize_size(org_context['employee_count']),
            'region': self.generalize_region(org_context['location'])
        }

        # Case content
        for key, value in case_data.items():
            rule = self.ANONYMIZATION_RULES.get(key, 'KEEP')
            anonymized[key] = self.apply_rule(rule, value, key)

        # Validation
        if not self.validate_anonymization(anonymized):
            raise AnonymizationError("PII detected after anonymization")

        return anonymized
```

**Generalization Functions:**

```python
def categorize_size(employee_count: int) -> str:
    """Generalize organization size"""
    if employee_count < 50:
        return 'small (1-49)'
    elif employee_count < 250:
        return 'medium (50-249)'
    elif employee_count < 1000:
        return 'large (250-999)'
    else:
        return 'enterprise (1000+)'

def generalize_region(location: str) -> str:
    """Generalize geographic location"""
    # City -> Region mapping
    REGION_MAP = {
        'Seattle': 'Pacific Northwest',
        'Portland': 'Pacific Northwest',
        'San Francisco': 'West Coast',
        'Los Angeles': 'West Coast',
        'New York': 'Northeast',
        'Boston': 'Northeast',
        # ...
    }
    return REGION_MAP.get(location, 'Unknown')

def generalize_revenue(revenue: float) -> str:
    """Generalize revenue to ranges"""
    if revenue < 1_000_000:
        return 'under $1M'
    elif revenue < 10_000_000:
        return '$1M-$10M'
    elif revenue < 50_000_000:
        return '$10M-$50M'
    elif revenue < 100_000_000:
        return '$50M-$100M'
    else:
        return 'over $100M'
```

---

### 5. Workflow Integration Service

**Purpose:** Integrate with platform workflow service to capture completed workflows and offer contribution.

**Event Subscription:**

```python
class WorkflowCompletionHandler:
    async def handle_workflow_completed(
        self,
        event: dict
    ):
        """
        Handle workflow_completed event

        Event structure:
        {
            'event_type': 'workflow_completed',
            'workflow_id': UUID,
            'workflow_type': str,  # bia, risk, governance, etc.
            'org_id': UUID,
            'user_id': UUID,
            'results': dict,  # Workflow outputs
            'metadata': dict,
            'timestamp': datetime
        }

        Process:
            1. Extract workflow results
            2. Check user contribution settings
            3. If auto-contribute enabled:
               - Create contribution automatically
            4. Else:
               - Send contribution offer notification
               - Wait for user acceptance
        """

        workflow_id = event['workflow_id']
        user_id = event['user_id']

        # Check user settings
        settings = await self.get_user_contribution_settings(user_id)

        if settings.get('auto_contribute', False):
            # Auto-create contribution
            contribution = await self.create_contribution_from_workflow(
                workflow_id=workflow_id,
                user_id=user_id,
                auto_anonymize=settings.get('auto_anonymize', True)
            )
            logger.info(f"Auto-created contribution {contribution.id} from workflow {workflow_id}")
        else:
            # Offer contribution
            await self.send_contribution_offer(
                user_id=user_id,
                workflow_id=workflow_id
            )
```

**Contribution Extraction:**

```python
async def create_contribution_from_workflow(
    self,
    workflow_id: UUID,
    user_id: UUID,
    auto_anonymize: bool = True
) -> Contribution:
    """
    Extract contribution data from completed workflow

    Process:
        1. Fetch workflow results from workflow service
        2. Extract relevant case data
        3. Fetch organization context
        4. Apply anonymization if enabled
        5. Create contribution
        6. Trigger peer review assignment
    """

    # Fetch workflow
    workflow = await self.workflow_service.get_workflow(workflow_id)

    # Extract case data
    case_data = {
        'workflow_type': workflow.type,
        'results': workflow.results,
        'success_indicators': workflow.success_indicators,
        'challenges': workflow.challenges,
        'lessons_learned': workflow.lessons_learned,
        'duration_days': workflow.duration_days,
        'team_size': workflow.team_size
    }

    # Fetch org context
    org = await self.get_organization(workflow.org_id)
    org_context = {
        'industry': org.industry,
        'employee_count': org.size,
        'location': org.location,
        'maturity_level': org.bcm_maturity
    }

    # Anonymize
    if auto_anonymize:
        case_data = await self.anonymizer.anonymize_case(case_data, org_context)

    # Create contribution
    contribution = await self.contribution_service.create_contribution(
        user_id=user_id,
        module=workflow.type,
        case_data=case_data,
        auto_anonymize=False  # Already anonymized
    )

    return contribution
```

---

### 6. Case Library Bridge

**Purpose:** Publish approved contributions to centralized case library for platform-wide access.

**Publication Flow:**

```python
class CaseLibraryBridge:
    async def publish_contribution(
        self,
        contribution: Contribution
    ):
        """
        Publish approved contribution to case library

        Requirements:
            - Contribution status must be 'published'
            - Must have passed peer review
            - Must be anonymized

        Process:
            1. Validate contribution ready for publication
            2. Transform to case library format
            3. Call case library API to create case
            4. Update contribution with case_library_id
            5. Publish contribution_published event
        """

        if contribution.status != 'published':
            raise ValueError("Only published contributions can be added to library")

        # Transform to case library format
        case = {
            'module': contribution.module,
            'industry': contribution.case_data['organization']['industry'],
            'size_category': contribution.case_data['organization']['size_category'],
            'region': contribution.case_data['organization']['region'],
            'content': contribution.case_data,
            'quality_score': contribution.review_score,
            'tags': self.extract_tags(contribution),
            'metadata': contribution.metadata
        }

        # Publish to case library
        case_library_id = await self.case_library_api.create_case(case)

        # Update contribution
        await self.update_contribution_case_library_id(
            contribution.id,
            case_library_id
        )

        # Publish event
        await self.eventbus.publish({
            'event_type': 'contribution_published',
            'contribution_id': contribution.id,
            'case_library_id': case_library_id,
            'user_id': contribution.user_id,
            'module': contribution.module
        })
```

**Case Library API Integration:**

```python
class CaseLibraryAPI:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={'Authorization': f'Bearer {api_key}'}
        )

    async def create_case(self, case: dict) -> UUID:
        """Create case in case library"""
        response = await self.client.post('/api/v1/cases', json=case)
        response.raise_for_status()
        return UUID(response.json()['case_id'])

    async def update_case(self, case_id: UUID, updates: dict):
        """Update existing case"""
        response = await self.client.patch(f'/api/v1/cases/{case_id}', json=updates)
        response.raise_for_status()

    async def delete_case(self, case_id: UUID):
        """Delete case from library"""
        response = await self.client.delete(f'/api/v1/cases/{case_id}')
        response.raise_for_status()
```

---

## Database Schema

### Core Tables

```sql
-- Contributions
CREATE TABLE community_contributions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    module TEXT NOT NULL,  -- bia, risk, governance, response, compliance
    case_data JSONB NOT NULL,
    metadata JSONB,
    status TEXT NOT NULL DEFAULT 'pending_review',
    -- Status values: draft, pending_review, in_review, published, rejected
    review_score NUMERIC(3,1),
    case_library_id UUID,  -- Reference to case in case library
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ,

    CONSTRAINT valid_status CHECK (status IN (
        'draft', 'pending_review', 'in_review', 'published', 'rejected'
    )),
    CONSTRAINT valid_review_score CHECK (review_score >= 1.0 AND review_score <= 10.0)
);

CREATE INDEX idx_contributions_user ON community_contributions(user_id);
CREATE INDEX idx_contributions_module ON community_contributions(module);
CREATE INDEX idx_contributions_status ON community_contributions(status);
CREATE INDEX idx_contributions_published ON community_contributions(published_at) WHERE status = 'published';

-- Peer Reviews
CREATE TABLE community_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contribution_id UUID NOT NULL REFERENCES community_contributions(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES users(id),
    quality_score INT NOT NULL,
    completeness_score INT,
    clarity_score INT,
    usefulness_score INT,
    feedback TEXT,
    recommendation TEXT NOT NULL,
    -- Recommendation values: approve, reject, revise
    submitted_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT valid_quality_score CHECK (quality_score >= 1 AND quality_score <= 10),
    CONSTRAINT valid_recommendation CHECK (recommendation IN ('approve', 'reject', 'revise')),
    CONSTRAINT unique_reviewer_per_contribution UNIQUE(contribution_id, reviewer_id)
);

CREATE INDEX idx_reviews_contribution ON community_reviews(contribution_id);
CREATE INDEX idx_reviews_reviewer ON community_reviews(reviewer_id);

-- Reviewer Assignments
CREATE TABLE reviewer_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contribution_id UUID NOT NULL REFERENCES community_contributions(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES users(id),
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    notified_at TIMESTAMPTZ,
    status TEXT DEFAULT 'pending',
    -- Status values: pending, accepted, declined, completed

    CONSTRAINT unique_assignment UNIQUE(contribution_id, reviewer_id)
);

CREATE INDEX idx_assignments_reviewer ON reviewer_assignments(reviewer_id, status);
CREATE INDEX idx_assignments_contribution ON reviewer_assignments(contribution_id);

-- Reputation
CREATE TABLE user_reputation (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    total_points INT DEFAULT 0,
    global_rank INT,
    level INT DEFAULT 1,
    expertise JSONB DEFAULT '{}',
    -- expertise structure:
    -- {
    --   "bia": {"points": 100, "level": 2},
    --   "risk": {"points": 50, "level": 1},
    --   ...
    -- }
    badges JSONB DEFAULT '[]',
    stats JSONB DEFAULT '{}',
    -- stats structure:
    -- {
    --   "contributions_published": 5,
    --   "reviews_submitted": 12,
    --   "helpful_votes_received": 34
    -- }
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_reputation_rank ON user_reputation(global_rank);
CREATE INDEX idx_reputation_points ON user_reputation(total_points DESC);

-- Reputation Transactions
CREATE TABLE reputation_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    action TEXT NOT NULL,
    points INT NOT NULL,
    module TEXT,
    reference_id UUID,  -- contribution_id or review_id
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_transactions_user ON reputation_transactions(user_id, created_at DESC);
CREATE INDEX idx_transactions_action ON reputation_transactions(action);

-- User Contribution Settings
CREATE TABLE user_contribution_settings (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    auto_contribute BOOLEAN DEFAULT FALSE,
    auto_anonymize BOOLEAN DEFAULT TRUE,
    notification_preferences JSONB DEFAULT '{}',
    privacy_level TEXT DEFAULT 'anonymous',
    -- Privacy levels: anonymous, pseudonymous, identified
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Indexes for Performance

```sql
-- Contribution queries
CREATE INDEX idx_contributions_user_status ON community_contributions(user_id, status);
CREATE INDEX idx_contributions_module_published ON community_contributions(module, published_at)
    WHERE status = 'published';

-- Review queries
CREATE INDEX idx_reviews_pending ON reviewer_assignments(reviewer_id)
    WHERE status = 'pending';
CREATE INDEX idx_reviews_contribution_status ON community_reviews(contribution_id, submitted_at);

-- Reputation queries
CREATE INDEX idx_reputation_module_points ON user_reputation USING gin(expertise);
CREATE INDEX idx_transactions_user_module ON reputation_transactions(user_id, module, created_at DESC);
```

---

## API Reference

### Contributions API

#### Create Contribution

```http
POST /api/v1/community/contributions
Content-Type: application/json
Authorization: Bearer {token}

{
    "module": "bia",
    "case_data": {
        "workflow_type": "bia",
        "organization": {
            "industry": "healthcare",
            "size_category": "medium (50-249)",
            "region": "Pacific Northwest"
        },
        "results": {
            "processes_identified": 25,
            "critical_processes": 8,
            "rto_range": "1-24 hours",
            "dependencies_mapped": true
        },
        "challenges": [
            "Difficulty identifying indirect dependencies",
            "Stakeholder engagement"
        ],
        "lessons_learned": [
            "Start with high-level process mapping",
            "Involve process owners early"
        ],
        "duration_days": 45,
        "team_size": 3
    },
    "metadata": {
        "tags": ["healthcare", "bia", "supply_chain"],
        "difficulty": "intermediate"
    }
}

Response 201:
{
    "contribution_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "pending_review",
    "created_at": "2025-10-05T12:00:00Z",
    "reviewers_assigned": 3
}

Response 400:
{
    "error": "validation_error",
    "details": {
        "case_data": ["Required field missing: organization.industry"]
    }
}
```

#### Get User Contributions

```http
GET /api/v1/community/contributions/my?status=published
Authorization: Bearer {token}

Response 200:
[
    {
        "contribution_id": "550e8400-e29b-41d4-a716-446655440000",
        "module": "bia",
        "status": "published",
        "review_score": 8.7,
        "created_at": "2025-10-01T12:00:00Z",
        "published_at": "2025-10-04T15:30:00Z",
        "helpful_votes": 12,
        "views": 87
    },
    ...
]
```

#### Preview Anonymization

```http
POST /api/v1/community/contributions/preview-anonymization
Content-Type: application/json
Authorization: Bearer {token}

{
    "case_data": {
        "organization": {
            "name": "Memorial Hospital Seattle",
            "employees": 250,
            "location": "Seattle, WA"
        },
        "author": "John Smith",
        "contact": "john.smith@hospital.com"
    }
}

Response 200:
{
    "anonymized": {
        "organization": {
            "industry": "healthcare",
            "size_category": "medium (50-249)",
            "region": "Pacific Northwest"
        }
    },
    "removed_fields": [
        "organization.name",
        "author",
        "contact"
    ],
    "warnings": []
}
```

#### Delete Contribution

```http
DELETE /api/v1/community/contributions/{contribution_id}
Authorization: Bearer {token}

Response 200:
{
    "message": "Contribution deleted successfully"
}

Response 403:
{
    "error": "cannot_delete",
    "message": "Published contributions cannot be deleted"
}
```

---

### Peer Reviews API

#### Submit Review

```http
POST /api/v1/community/reviews
Content-Type: application/json
Authorization: Bearer {token}

{
    "contribution_id": "550e8400-e29b-41d4-a716-446655440000",
    "quality_score": 9,
    "completeness_score": 9,
    "clarity_score": 8,
    "usefulness_score": 10,
    "feedback": "Excellent case study with clear lessons learned. The dependency mapping approach is particularly valuable. Minor suggestion: add more detail about stakeholder interview process.",
    "recommendation": "approve"
}

Response 201:
{
    "review_id": "660e8400-e29b-41d4-a716-446655440000",
    "contribution_id": "550e8400-e29b-41d4-a716-446655440000",
    "submitted_at": "2025-10-05T12:00:00Z",
    "reputation_earned": 13
}

Response 400:
{
    "error": "validation_error",
    "details": {
        "quality_score": ["Must be between 1 and 10"]
    }
}
```

#### Get Pending Reviews

```http
GET /api/v1/community/reviews/pending
Authorization: Bearer {token}

Response 200:
[
    {
        "contribution_id": "550e8400-e29b-41d4-a716-446655440000",
        "module": "bia",
        "submitted_at": "2025-10-01T12:00:00Z",
        "due_date": "2025-10-08T12:00:00Z",
        "preview": {
            "industry": "healthcare",
            "size_category": "medium (50-249)",
            "tags": ["bia", "supply_chain"]
        }
    },
    ...
]
```

#### Get My Reviews

```http
GET /api/v1/community/reviews/my?status=completed
Authorization: Bearer {token}

Response 200:
[
    {
        "review_id": "660e8400-e29b-41d4-a716-446655440000",
        "contribution_id": "550e8400-e29b-41d4-a716-446655440000",
        "module": "bia",
        "quality_score": 9,
        "recommendation": "approve",
        "submitted_at": "2025-10-05T12:00:00Z",
        "reputation_earned": 13,
        "contribution_status": "published"
    },
    ...
]
```

---

### Reputation API

#### Get User Reputation

```http
GET /api/v1/community/reputation/{user_id}

Response 200:
{
    "user_id": "770e8400-e29b-41d4-a716-446655440000",
    "total_points": 1250,
    "global_rank": 42,
    "level": 5,
    "level_name": "Expert",
    "badges": [
        {
            "id": "contributor",
            "name": "Active Contributor",
            "description": "Published 10+ contributions",
            "earned_at": "2025-09-15T12:00:00Z"
        },
        {
            "id": "reviewer",
            "name": "Dedicated Reviewer",
            "description": "Completed 50+ peer reviews",
            "earned_at": "2025-09-28T12:00:00Z"
        }
    ],
    "expertise_by_module": {
        "bia": {
            "points": 550,
            "level": 5,
            "level_name": "Expert",
            "contributions": 8,
            "reviews": 25
        },
        "risk": {
            "points": 325,
            "level": 4,
            "level_name": "Advanced",
            "contributions": 4,
            "reviews": 15
        },
        "governance": {
            "points": 175,
            "level": 3,
            "level_name": "Intermediate",
            "contributions": 2,
            "reviews": 10
        }
    },
    "stats": {
        "contributions_submitted": 14,
        "contributions_published": 12,
        "reviews_submitted": 68,
        "helpful_votes_received": 145,
        "cases_viewed": 892,
        "member_since": "2025-05-01T00:00:00Z"
    },
    "next_level": {
        "level": 6,
        "level_name": "Master",
        "points_required": 2500,
        "points_remaining": 1250
    }
}
```

#### Get Module Expertise

```http
GET /api/v1/community/reputation/{user_id}/expertise/bia

Response 200:
{
    "module": "bia",
    "points": 550,
    "level": 5,
    "level_name": "Expert",
    "module_rank": 15,
    "percentile": 92,
    "contributions": {
        "total": 8,
        "published": 7,
        "rejected": 0,
        "pending": 1,
        "avg_quality_score": 8.4
    },
    "reviews": {
        "total": 25,
        "approved": 22,
        "rejected": 2,
        "consensus_rate": 0.88
    },
    "badges": [
        {
            "id": "bia_specialist",
            "name": "BIA Specialist",
            "description": "Published 5+ BIA contributions with avg score 8+",
            "earned_at": "2025-08-20T12:00:00Z"
        }
    ]
}
```

#### Get Global Leaderboard

```http
GET /api/v1/community/reputation/leaderboard/global?timeframe=month&limit=10

Response 200:
{
    "timeframe": "month",
    "period": "2025-10",
    "leaderboard": [
        {
            "rank": 1,
            "user_id": "770e8400-e29b-41d4-a716-446655440000",
            "username": "bcm_expert_42",  // anonymized or real based on privacy settings
            "points": 1250,
            "points_this_period": 320,
            "level": 5,
            "level_name": "Expert",
            "top_badge": "Master Contributor",
            "contributions_this_period": 3,
            "reviews_this_period": 12
        },
        ...
    ]
}
```

#### Get Module Leaderboard

```http
GET /api/v1/community/reputation/leaderboard/bia?limit=25

Response 200:
{
    "module": "bia",
    "leaderboard": [
        {
            "rank": 1,
            "user_id": "770e8400-e29b-41d4-a716-446655440000",
            "username": "bcm_expert_42",
            "points": 550,
            "level": 5,
            "level_name": "Expert",
            "contributions": 8,
            "avg_quality_score": 8.4
        },
        ...
    ]
}
```

#### Get Reputation Transactions

```http
GET /api/v1/community/reputation/transactions/{user_id}?limit=50

Response 200:
[
    {
        "transaction_id": "880e8400-e29b-41d4-a716-446655440000",
        "action": "contribution_published",
        "points": 50,
        "module": "bia",
        "reference_id": "550e8400-e29b-41d4-a716-446655440000",
        "created_at": "2025-10-04T15:30:00Z",
        "description": "Contribution published to case library"
    },
    {
        "transaction_id": "990e8400-e29b-41d4-a716-446655440000",
        "action": "contribution_high_quality",
        "points": 25,
        "module": "bia",
        "reference_id": "550e8400-e29b-41d4-a716-446655440000",
        "created_at": "2025-10-04T15:30:00Z",
        "description": "High quality contribution (score 9.0+)"
    },
    ...
]
```

---

### Case Library API

#### Search Cases

```http
GET /api/v1/community/cases/search?module=bia&industry=healthcare&min_quality=8.0&limit=20

Response 200:
{
    "total": 47,
    "page": 1,
    "page_size": 20,
    "cases": [
        {
            "case_id": "aa0e8400-e29b-41d4-a716-446655440000",
            "module": "bia",
            "industry": "healthcare",
            "size_category": "medium (50-249)",
            "region": "Pacific Northwest",
            "quality_score": 8.7,
            "published_at": "2025-10-04T15:30:00Z",
            "helpful_votes": 12,
            "views": 87,
            "tags": ["bia", "supply_chain", "dependency_mapping"],
            "summary": "Comprehensive BIA for healthcare organization with focus on supply chain dependencies..."
        },
        ...
    ]
}
```

#### Get Case Details

```http
GET /api/v1/community/cases/{case_id}

Response 200:
{
    "case_id": "aa0e8400-e29b-41d4-a716-446655440000",
    "module": "bia",
    "organization": {
        "industry": "healthcare",
        "size_category": "medium (50-249)",
        "region": "Pacific Northwest"
    },
    "content": {
        "workflow_type": "bia",
        "results": {
            "processes_identified": 25,
            "critical_processes": 8,
            "rto_range": "1-24 hours",
            "dependencies_mapped": true
        },
        "challenges": [
            "Difficulty identifying indirect dependencies",
            "Stakeholder engagement"
        ],
        "lessons_learned": [
            "Start with high-level process mapping",
            "Involve process owners early"
        ],
        "duration_days": 45,
        "team_size": 3
    },
    "quality_score": 8.7,
    "published_at": "2025-10-04T15:30:00Z",
    "helpful_votes": 12,
    "views": 87,
    "tags": ["bia", "supply_chain", "dependency_mapping"],
    "reviews_summary": {
        "total_reviews": 3,
        "avg_completeness": 9.0,
        "avg_clarity": 8.3,
        "avg_usefulness": 9.3
    }
}
```

#### Get Similar Cases for Workflow

```http
GET /api/v1/community/cases/similar/for-workflow?module=bia&industry=healthcare&size_category=medium&limit=5

Response 200:
[
    {
        "case_id": "aa0e8400-e29b-41d4-a716-446655440000",
        "similarity_score": 0.92,
        "quality_score": 8.7,
        "tags": ["bia", "supply_chain"],
        "summary": "BIA for medium healthcare organization..."
    },
    ...
]
```

#### Get Case Library Stats

```http
GET /api/v1/community/cases/stats/overview

Response 200:
{
    "total_cases": 342,
    "by_module": {
        "bia": 87,
        "risk": 76,
        "governance": 54,
        "response": 65,
        "compliance": 60
    },
    "by_industry": {
        "healthcare": 95,
        "finance": 78,
        "manufacturing": 62,
        "retail": 43,
        "other": 64
    },
    "avg_quality_score": 8.2,
    "total_helpful_votes": 2847,
    "total_views": 18392,
    "top_contributors": [
        {
            "user_id": "770e8400-e29b-41d4-a716-446655440000",
            "username": "bcm_expert_42",
            "contributions": 12
        },
        ...
    ]
}
```

---

## Integration Points

### EventBus Integration

**Published Events:**

```python
# Contribution lifecycle events
'contribution_created'
'contribution_submitted_for_review'
'contribution_approved'
'contribution_rejected'
'contribution_published'
'contribution_deleted'

# Review events
'review_assigned'
'review_submitted'
'review_completed'

# Reputation events
'reputation_updated'
'level_up'
'badge_earned'

# Case library events
'case_published'
'case_helpful_vote'
```

**Subscribed Events:**

```python
# From workflow service
'workflow_completed'
'workflow_updated'

# From user service
'user_created'
'user_preferences_updated'
```

**Event Structures:**

```python
# workflow_completed
{
    'event_type': 'workflow_completed',
    'workflow_id': UUID,
    'workflow_type': 'bia',  # or risk, governance, etc.
    'org_id': UUID,
    'user_id': UUID,
    'results': dict,
    'metadata': dict,
    'timestamp': datetime
}

# contribution_published
{
    'event_type': 'contribution_published',
    'contribution_id': UUID,
    'case_library_id': UUID,
    'user_id': UUID,
    'module': 'bia',
    'quality_score': 8.7,
    'timestamp': datetime
}

# reputation_updated
{
    'event_type': 'reputation_updated',
    'user_id': UUID,
    'action': 'contribution_published',
    'points_earned': 50,
    'total_points': 1250,
    'old_level': 4,
    'new_level': 5,
    'timestamp': datetime
}
```

---

### Case Library Service Integration

**API Client:**

```python
class CaseLibraryClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={'Authorization': f'Bearer {api_key}'}
        )

    async def create_case(self, case: dict) -> UUID:
        response = await self.client.post('/api/v1/cases', json=case)
        response.raise_for_status()
        return UUID(response.json()['case_id'])

    async def search_cases(
        self,
        module: str = None,
        industry: str = None,
        min_quality: float = None,
        tags: List[str] = None,
        limit: int = 20
    ) -> List[dict]:
        params = {}
        if module:
            params['module'] = module
        if industry:
            params['industry'] = industry
        if min_quality:
            params['min_quality'] = min_quality
        if tags:
            params['tags'] = ','.join(tags)
        params['limit'] = limit

        response = await self.client.get('/api/v1/cases/search', params=params)
        response.raise_for_status()
        return response.json()['cases']
```

---

### Workflow Service Integration

**Workflow completion handler:**

```python
async def handle_workflow_completed(event: dict):
    """
    Handle workflow_completed event from workflow service

    Process:
        1. Extract workflow data
        2. Check user contribution settings
        3. Create contribution offer or auto-create
    """

    workflow_id = event['workflow_id']
    user_id = event['user_id']

    # Check if user has auto-contribute enabled
    settings = await get_user_contribution_settings(user_id)

    if settings.auto_contribute:
        # Auto-create contribution
        contribution = await create_contribution_from_workflow(
            workflow_id=workflow_id,
            user_id=user_id,
            auto_anonymize=settings.auto_anonymize
        )
        logger.info(f"Auto-created contribution {contribution.id}")
    else:
        # Send contribution offer notification
        await send_contribution_offer(
            user_id=user_id,
            workflow_id=workflow_id,
            workflow_type=event['workflow_type']
        )
```

---

## Configuration

### Environment Variables

```bash
# Service
PORT=8030
DEBUG=false

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/bcm_platform
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=xxx

# Redis Cache
REDIS_URL=redis://localhost:6379

# EventBus
EVENTBUS_URL=http://localhost:8001

# Case Library Integration
CASE_LIBRARY_URL=http://localhost:8032
CASE_LIBRARY_API_KEY=xxx

# Workflow Service Integration
WORKFLOW_SERVICE_URL=http://localhost:8020

# AI (for anonymization validation, NER)
ANTHROPIC_API_KEY=sk-xxx

# Peer Review Settings
REVIEWERS_PER_CONTRIBUTION=3
REVIEW_DEADLINE_DAYS=7
MIN_APPROVAL_THRESHOLD=0.67  # 2/3 must approve

# Reputation Settings
REPUTATION_POINTS_CONTRIBUTION_PUBLISHED=50
REPUTATION_POINTS_CONTRIBUTION_HIGH_QUALITY=25
REPUTATION_POINTS_REVIEW_SUBMITTED=3
REPUTATION_POINTS_REVIEW_HIGH_QUALITY=10

# Privacy Settings
ANONYMIZATION_STRICT_MODE=true
MIN_ORG_SIZE_CATEGORY_SIZE=10  # Minimum orgs per size category

# Notifications
NOTIFICATION_SERVICE_URL=http://localhost:8035
```

### Application Configuration

```python
# config.py
from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Service
    PORT: int = 8030
    DEBUG: bool = False
    SERVICE_NAME: str = "community-intelligence"

    # Database
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # Cache
    REDIS_URL: str = "redis://localhost:6379"

    # EventBus
    EVENTBUS_URL: str = "http://localhost:8001"

    # External Services
    CASE_LIBRARY_URL: str = "http://localhost:8032"
    CASE_LIBRARY_API_KEY: str
    WORKFLOW_SERVICE_URL: str = "http://localhost:8020"
    NOTIFICATION_SERVICE_URL: str = "http://localhost:8035"

    # AI
    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    # Peer Review
    REVIEWERS_PER_CONTRIBUTION: int = 3
    REVIEW_DEADLINE_DAYS: int = 7
    MIN_APPROVAL_THRESHOLD: float = 0.67  # 2/3
    MIN_QUALITY_SCORE: float = 6.0

    # Reputation
    REPUTATION_POINTS: dict = {
        'contribution_created': 5,
        'contribution_published': 50,
        'contribution_high_quality': 25,
        'contribution_rejected': -10,
        'review_submitted': 3,
        'review_high_quality': 10,
        'review_consensus': 5,
        'case_helpful_vote': 2,
        'case_used': 1,
        'spam_detected': -100,
        'quality_violation': -25
    }

    # Privacy
    ANONYMIZATION_STRICT_MODE: bool = True
    MIN_ORG_SIZE_CATEGORY_SIZE: int = 10

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

## Deployment

### Local Development

```bash
# Prerequisites
python 3.11+
postgresql 15+
redis 7+

# Setup
git clone <repository>
cd intelligent-core/community_intelligence

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Apply database migration
psql $DATABASE_URL -f ../../infrastructure/database/migrations_source/040_community_intelligence.sql

# Run service
python main.py

# Service available at http://localhost:8030
# API docs at http://localhost:8030/docs
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8030

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8030/health || exit 1

# Run application
CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  community-intelligence:
    build: .
    ports:
      - "8030:8030"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379
      - EVENTBUS_URL=http://eventbus:8001
      - CASE_LIBRARY_URL=http://case-library:8032
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - redis
      - postgres
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=bcm_platform
      - POSTGRES_USER=bcm_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  redis_data:
  postgres_data:
```

### Production Deployment

**Requirements:**
- Kubernetes cluster or cloud platform (AWS, GCP, Azure)
- PostgreSQL RDS or managed database
- Redis ElastiCache or managed cache
- Load balancer with SSL termination
- Monitoring and logging infrastructure

**Kubernetes Example:**

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: community-intelligence
  namespace: bcm-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: community-intelligence
  template:
    metadata:
      labels:
        app: community-intelligence
    spec:
      containers:
      - name: community-intelligence
        image: bcm-platform/community-intelligence:latest
        ports:
        - containerPort: 8030
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: connection-string
        - name: REDIS_URL
          value: redis://redis-service:6379
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: anthropic
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8030
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8030
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: community-intelligence
  namespace: bcm-platform
spec:
  selector:
    app: community-intelligence
  ports:
  - port: 80
    targetPort: 8030
  type: LoadBalancer
```

---

## Monitoring and Observability

### Key Metrics

**Service Health:**
- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate
- Service uptime

**Business Metrics:**
- Contributions submitted per day
- Contributions published per day
- Reviews completed per day
- Average review turnaround time
- Contribution approval rate
- Active reviewers count
- Case library growth rate

**Quality Metrics:**
- Average contribution quality score
- Review consensus rate
- Contribution rejection reasons
- Anonymization failures

### Logging

```python
import logging
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Usage
logger.info(
    "contribution_created",
    contribution_id=str(contribution_id),
    user_id=str(user_id),
    module=module,
    auto_anonymize=auto_anonymize
)
```

### Health Checks

```python
@app.get("/health")
async def health_check():
    """
    Comprehensive health check

    Checks:
        - Database connectivity
        - Redis connectivity
        - EventBus connectivity
        - External service availability
    """

    health = {
        "status": "healthy",
        "service": "community-intelligence",
        "version": "1.0.0",
        "checks": {}
    }

    # Database
    try:
        await db.execute("SELECT 1")
        health["checks"]["database"] = "healthy"
    except Exception as e:
        health["checks"]["database"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"

    # Redis
    try:
        await redis.ping()
        health["checks"]["redis"] = "healthy"
    except Exception as e:
        health["checks"]["redis"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"

    # EventBus
    try:
        response = await httpx.get(f"{settings.EVENTBUS_URL}/health", timeout=5.0)
        health["checks"]["eventbus"] = "healthy" if response.status_code == 200 else "unhealthy"
    except Exception as e:
        health["checks"]["eventbus"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"

    # Case Library
    try:
        response = await httpx.get(f"{settings.CASE_LIBRARY_URL}/health", timeout=5.0)
        health["checks"]["case_library"] = "healthy" if response.status_code == 200 else "unhealthy"
    except Exception as e:
        health["checks"]["case_library"] = f"unhealthy: {str(e)}"
        # Non-critical, don't mark as degraded

    return health
```

---

## Testing

### Unit Tests

```python
# tests/test_contribution_service.py
import pytest
from services.contribution_service import ContributionService

@pytest.fixture
async def contribution_service():
    return ContributionService(db=mock_db, anonymizer=mock_anonymizer)

@pytest.mark.asyncio
async def test_create_contribution_with_anonymization(contribution_service):
    """Test contribution creation with auto-anonymization"""

    case_data = {
        "organization": {
            "name": "Test Hospital",
            "employees": 250
        }
    }

    contribution = await contribution_service.create_contribution(
        user_id=UUID("..."),
        module="bia",
        case_data=case_data,
        auto_anonymize=True
    )

    assert contribution.status == "pending_review"
    assert "name" not in contribution.case_data["organization"]
    assert contribution.case_data["organization"]["size_category"] == "medium (50-249)"

@pytest.mark.asyncio
async def test_cannot_delete_published_contribution(contribution_service):
    """Test that published contributions cannot be deleted"""

    contribution = await contribution_service.get_contribution(UUID("..."))
    contribution.status = "published"

    with pytest.raises(PermissionError):
        await contribution_service.delete_contribution(
            contribution_id=contribution.id,
            user_id=contribution.user_id
        )
```

### Integration Tests

```python
# tests/test_peer_review_flow.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_full_peer_review_flow():
    """Test complete peer review workflow"""

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create contribution
        response = await client.post(
            "/api/v1/community/contributions",
            json={"module": "bia", "case_data": {...}},
            headers={"Authorization": "Bearer user1_token"}
        )
        assert response.status_code == 201
        contribution_id = response.json()["contribution_id"]

        # Get assigned reviewers
        response = await client.get(
            f"/api/v1/community/contributions/{contribution_id}",
            headers={"Authorization": "Bearer user1_token"}
        )
        reviewers = response.json()["reviewers_assigned"]
        assert len(reviewers) == 3

        # Submit 3 reviews (2 approve, 1 reject)
        for i, reviewer_token in enumerate([reviewer1_token, reviewer2_token, reviewer3_token]):
            recommendation = "approve" if i < 2 else "reject"
            response = await client.post(
                "/api/v1/community/reviews",
                json={
                    "contribution_id": contribution_id,
                    "quality_score": 8,
                    "feedback": "Test feedback",
                    "recommendation": recommendation
                },
                headers={"Authorization": f"Bearer {reviewer_token}"}
            )
            assert response.status_code == 201

        # Check contribution status
        response = await client.get(
            f"/api/v1/community/contributions/{contribution_id}",
            headers={"Authorization": "Bearer user1_token"}
        )
        contribution = response.json()
        assert contribution["status"] == "published"  # 2/3 approved
        assert contribution["case_library_id"] is not None
```

---

## Security Considerations

### Data Privacy

**PII Protection:**
- Automatic anonymization of organization names, people, contact info
- Manual review of anonymization before publication
- Strict validation to prevent PII leakage

**Access Control:**
- Users can only edit/delete their own contributions
- Reviewers assigned by system, not user-chosen
- Case library access is public, but contributions are attributed

### API Security

**Authentication:**
- JWT-based authentication for all endpoints
- Token expiration and refresh
- Role-based access control (RBAC)

**Rate Limiting:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/community/contributions")
@limiter.limit("10/hour")  # Max 10 contributions per hour
async def create_contribution(...):
    ...

@app.post("/api/v1/community/reviews")
@limiter.limit("30/hour")  # Max 30 reviews per hour
async def submit_review(...):
    ...
```

**Input Validation:**
- Pydantic models for request validation
- SQL injection prevention (parameterized queries)
- XSS prevention (content sanitization)

### Spam Prevention

**Detection:**
```python
async def detect_spam(contribution: dict, user_id: UUID) -> bool:
    """
    Detect potential spam contributions

    Signals:
        - Duplicate content
        - Low quality (very short, no lessons learned)
        - Rapid submissions (>5 per hour)
        - Generic/template content
    """

    # Check for duplicates
    similar = await find_similar_contributions(contribution)
    if similar and similar.similarity_score > 0.95:
        return True

    # Check submission rate
    recent = await get_recent_contributions(user_id, hours=1)
    if len(recent) > 5:
        return True

    # Check quality
    if len(contribution.get('lessons_learned', '')) < 50:
        return True

    return False
```

---

## Performance Optimization

### Database Optimization

**Indexes:**
- Covering indexes for common queries
- Partial indexes for filtered queries
- GIN indexes for JSONB columns

**Query Optimization:**
```sql
-- Use covering index for leaderboard
CREATE INDEX idx_reputation_leaderboard ON user_reputation(total_points DESC)
INCLUDE (user_id, level, badges);

-- Partial index for active reviews
CREATE INDEX idx_pending_reviews ON reviewer_assignments(reviewer_id, assigned_at)
WHERE status = 'pending';

-- GIN index for JSONB search
CREATE INDEX idx_case_data_gin ON community_contributions USING gin(case_data);
```

### Caching Strategy

**Redis Caching:**
```python
class CacheService:
    async def get_leaderboard(
        self,
        module: Optional[str] = None,
        timeframe: str = 'all_time'
    ) -> List[dict]:
        """Get leaderboard with caching"""

        cache_key = f"leaderboard:{module or 'global'}:{timeframe}"

        # Try cache
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)

        # Calculate
        leaderboard = await self.calculate_leaderboard(module, timeframe)

        # Cache for 5 minutes
        await redis.setex(
            cache_key,
            300,  # 5 minutes
            json.dumps(leaderboard)
        )

        return leaderboard
```

**Cache Invalidation:**
```python
async def invalidate_leaderboard_cache(module: str = None):
    """Invalidate leaderboard cache when reputation changes"""

    keys_to_delete = [
        f"leaderboard:{module or 'global'}:all_time",
        f"leaderboard:{module or 'global'}:month",
        f"leaderboard:{module or 'global'}:week"
    ]

    await redis.delete(*keys_to_delete)
```

---

## Troubleshooting

### Common Issues

**Issue:** Reviewers not being assigned
```
Symptom: Contribution created but no reviewers assigned
Cause: Insufficient eligible reviewers for module
Solution:
  - Check eligible reviewer count: SELECT COUNT(*) FROM user_reputation WHERE expertise->'{module}'->>'points'::int > 100
  - Lower expertise threshold or expand reviewer pool
  - Notify admins to recruit reviewers for module
```

**Issue:** Reviews not triggering publication
```
Symptom: 3 reviews submitted but contribution not published
Cause: Approval threshold not met or quality score too low
Solution:
  - Check review recommendations: SELECT recommendation, quality_score FROM community_reviews WHERE contribution_id = '...'
  - Verify 2/3 approval and avg score >= 6.0
  - If threshold not met, contribution should be rejected
```

**Issue:** Anonymization failures
```
Symptom: PII detected after anonymization
Cause: New PII patterns not covered by rules
Solution:
  - Review anonymization logs for detected patterns
  - Update ANONYMIZATION_RULES in AnonymizerService
  - Add new regex patterns or NER models
  - Test on sample data before deploying
```

---

## Future Enhancements

### Planned Features

**V2.0 - Advanced Review:**
- AI-assisted review quality checking
- Automated spam detection
- Batch review workflows
- Review templates and checklists

**V2.1 - Enhanced Discovery:**
- Semantic search for cases
- Recommendation engine (similar cases)
- Trending topics and patterns
- Automated tagging with AI

**V2.2 - Community Features:**
- Discussion threads on cases
- Expert Q&A
- Mentorship matching
- Community events and challenges

**V2.3 - Analytics:**
- Contribution analytics dashboard
- Impact metrics (cases used, problems solved)
- ROI tracking for contributors
- Predictive quality scoring

---

## Appendix

### Glossary

**Contribution:** User-submitted case study from completed BCM workflow

**Peer Review:** Quality evaluation of contribution by expert reviewers

**Reputation:** Points-based measure of user expertise and activity

**Anonymization:** Process of removing PII and sensitive data from contributions

**Case Library:** Centralized repository of published contributions

**Module:** BCM domain area (BIA, Risk, Governance, Response, Compliance)

**Quality Score:** Numerical rating (1-10) of contribution quality from peer reviews

**Expertise Level:** User's proficiency in a module based on reputation points

---

### API Response Codes

**Success:**
- 200 OK - Request successful
- 201 Created - Resource created
- 204 No Content - Successful deletion

**Client Errors:**
- 400 Bad Request - Invalid input
- 401 Unauthorized - Authentication required
- 403 Forbidden - Insufficient permissions
- 404 Not Found - Resource not found
- 409 Conflict - Resource conflict (e.g., duplicate)
- 422 Unprocessable Entity - Validation failed
- 429 Too Many Requests - Rate limit exceeded

**Server Errors:**
- 500 Internal Server Error - Unexpected server error
- 502 Bad Gateway - Upstream service error
- 503 Service Unavailable - Service temporarily down

---

**Document Version:** 1.0.0
**Last Updated:** 2025-10-05
**Maintained By:** Platform Team
