# Community Intelligence - Integration Guide

Руководство по интеграции Community Intelligence в основную платформу.

## 🎯 Overview

Community Intelligence Foundation добавляет:
- **Case Contributions**: Пользователи делятся опытом
- **Peer Review**: Качественная проверка сообщества
- **Reputation System**: Мотивация и доверие
- **Living Documentation**: Эволюционирующие руководства
- **Predictive Timeline**: ML-прогнозы journey

## 📋 Prerequisites

1. **Database**: PostgreSQL 14+ с Supabase
2. **Python**: 3.10+
3. **Existing modules**:
   - Workflow Engine (для получения текущего состояния)
   - Case Library (для хранения одобренных кейсов)
   - Knowledge Graph (для стандартов)
   - LLM Service (для синтеза)

## 🔧 Installation Steps

### 1. Apply Database Migration

```bash
cd infrastructure/database

# Review migration
cat migrations_source/037_community_intelligence.sql

# Apply via Supabase CLI
supabase db push

# OR apply directly
psql $DATABASE_URL -f migrations_source/037_community_intelligence.sql
```

### 2. Install Dependencies

```bash
cd intelligent-core/community_intelligence
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# .env
COMMUNITY_REVIEWERS_PER_CONTRIBUTION=3
COMMUNITY_REVIEW_DEADLINE_DAYS=7
COMMUNITY_MIN_REPUTATION_TO_REVIEW=100
COMMUNITY_K_ANONYMITY=5
COMMUNITY_SYNTHESIS_TEMPERATURE=0.3
```

### 4. Initialize Services

```python
# intelligent-core/main.py или app factory

from community_intelligence import (
    ContributionService,
    LivingDocumentationService,
    PredictiveTimelineService,
    SmartAnonymizer
)
from community_intelligence.api import router as community_router

# Add to FastAPI app
app.include_router(community_router)

# Initialize services (with dependency injection)
async def get_contribution_service(
    db: AsyncSession = Depends(get_db),
    case_library = Depends(get_case_library),
    anonymizer = Depends(get_anonymizer)
):
    return ContributionService(db, anonymizer, case_library)
```

## 🔌 Integration Points

### 1. Workflow Engine Integration

**When workflow completes** → Offer to contribute case

```python
# In workflow completion handler

from community_intelligence import ContributionService

async def on_workflow_complete(workflow_instance):
    # Extract case data
    case_data = {
        "organization_context": workflow_instance.org_context,
        "module": workflow_instance.module,
        "journey": workflow_instance.journey_history,
        "metrics": workflow_instance.metrics,
        "success_patterns": workflow_instance.extract_patterns()
    }

    # Offer contribution
    await notify_user_contribute_case(
        user_id=workflow_instance.user_id,
        case_data=case_data
    )
```

### 2. Case Library Integration

**Approved contributions** → Add to library

```python
# In ContributionService._approve_contribution()

# Already implemented:
case_id = await self.case_library.add_community_case(
    contribution.case_data,
    metadata={
        'contributed_by': str(contribution.contributor_id),
        'contribution_id': str(contribution.id),
        'review_scores': [r.quality_score for r in reviews],
        'community_source': True
    }
)
```

### 3. Knowledge Graph Integration

**Synthesizing guidance** → Get official texts

```python
# In LivingDocumentationService.synthesize_clause()

official = await self.kg.get_clause(clause_id)

# Returns:
# {
#   "id": "4.1",
#   "text": "The organization shall understand...",
#   "standard": "ISO22301",
#   "section": "Context of the organization"
# }
```

### 4. LLM Service Integration

**Synthesis** → Generate unified guidance

```python
# In LivingDocumentationService

synthesis = await self.llm.generate(
    prompt=synthesis_prompt,
    temperature=0.3,
    max_tokens=2000
)
```

### 5. ML Predictor Integration

**Timeline prediction** → Use similarity models

```python
# In PredictiveTimelineService

ml_forecast = await self.ml.predict_journey(
    current_state=current,
    similar_journeys=similar
)

# Expected ML model outputs:
# - stage_sequence: [StageTransition, ...]
# - predicted_needs: [ResourceNeed, ...]
# - confidence: float
```

## 🎨 UI Integration Points

### 1. Workflow Completion Screen

```typescript
// After workflow complete

<WorkflowComplete>
  <SuccessSummary />
  <ContributeButton onClick={openContributeModal}>
    Share your experience with the community
  </ContributeButton>
</WorkflowComplete>
```

### 2. Case Contribution Modal

```typescript
<ContributeModal>
  <AnonymizationPreview
    original={caseData}
    anonymized={anonymizedData}
    riskScore={0.3}
  />
  <ConsentCheckbox>
    I confirm this data is anonymized and can be shared
  </ConsentCheckbox>
  <SubmitButton />
</ContributeModal>
```

### 3. Peer Review Dashboard

```typescript
<ReviewDashboard>
  <PendingReviews count={3} />
  <ReviewCard>
    <AnonymizedCase data={contribution.case_data} />
    <ReviewForm>
      <QualityScore min={1} max={10} />
      <CriteriaChecklist />
      <FeedbackText />
      <ApproveButton />
    </ReviewForm>
  </ReviewCard>
</ReviewDashboard>
```

### 4. Reputation Profile

```typescript
<UserProfile>
  <ReputationWidget
    level="contributor"
    points={340}
    expertise={{bia: 75, risk: 50}}
    badges={["First Contribution", "Quality Reviewer"]}
  />
  <ActivityFeed />
</UserProfile>
```

### 5. Living Documentation Viewer

```typescript
<ClauseViewer clauseId="4.1">
  <OfficialText />
  <SynthesizedGuidance>
    <UnifiedExplanation />
    <PracticalSteps />
    <CommonPitfalls />
    <SuccessPatterns />
  </SynthesizedGuidance>

  <CommunityAnnotations>
    <Annotation
      author="expert_123"
      upvotes={15}
      downvotes={2}
    />
    <VoteButtons />
  </CommunityAnnotations>

  <AddAnnotationButton />
</ClauseViewer>
```

### 6. Predictive Timeline

```typescript
<OrganizationDashboard>
  <PredictiveTimeline
    events={predictedEvents}
    milestones={milestones}
    criticalPath={criticalPath}
  />

  <SimilarOrgInsights
    avgDuration={45}
    commonChallenges={challenges}
    successFactors={factors}
  />
</OrganizationDashboard>
```

## 🔔 Notification Integration

### Events to notify:

```python
# notification_service.py

COMMUNITY_EVENTS = {
    'REVIEW_ASSIGNED': {
        'template': 'review_assigned',
        'channels': ['email', 'in_app']
    },
    'CASE_APPROVED': {
        'template': 'case_approved',
        'channels': ['email', 'in_app']
    },
    'REPUTATION_LEVEL_UP': {
        'template': 'level_up',
        'channels': ['in_app', 'push']
    },
    'ANNOTATION_UPVOTED': {
        'template': 'annotation_upvoted',
        'channels': ['in_app']
    }
}
```

## 🧪 Testing Integration

```bash
# Run integration tests
pytest intelligent-core/community_intelligence/tests/ -v

# Test with real database (local)
ENVIRONMENT=test pytest intelligent-core/community_intelligence/tests/

# Load test peer review flow
locust -f tests/load/test_peer_review.py
```

## 📊 Monitoring & Metrics

Add to observability stack:

```python
# Prometheus metrics

community_contributions_submitted = Counter(
    'community_contributions_submitted_total',
    'Total case contributions submitted'
)

community_reviews_completed = Counter(
    'community_reviews_completed_total',
    'Total peer reviews completed'
)

community_synthesis_duration = Histogram(
    'community_synthesis_duration_seconds',
    'Time to synthesize guidance'
)

# Track in service methods
@community_contributions_submitted.count_exceptions()
async def submit_case(...):
    ...
```

## 🔐 Security Checklist

- [ ] RLS policies applied (migration 037)
- [ ] Anonymization risk threshold enforced (< 0.7)
- [ ] JWT authentication on all endpoints
- [ ] Rate limiting on contribution submission
- [ ] Input validation on all user content
- [ ] XSS protection on community content
- [ ] CSRF tokens on forms

## 🚀 Deployment

### 1. Database

```bash
# Production migration
supabase db push --db-url $PROD_DATABASE_URL
```

### 2. Backend

```bash
# Deploy with new module
docker build -t ai-platform-iso/intelligent-core:latest .
docker push ai-platform-iso/intelligent-core:latest

kubectl apply -f k8s/community-intelligence/
```

### 3. Feature Flags

```python
# feature_flags.py

COMMUNITY_INTELLIGENCE = {
    'enabled': True,
    'case_contributions': True,
    'peer_review': True,
    'living_docs': True,
    'predictive_timeline': True  # Beta
}
```

## 📈 Rollout Plan

### Phase 1: Beta (Week 1-2)
- Enable for power users (level: expert, master)
- Limited to 10 contributions/day
- Monitor anonymization quality

### Phase 2: General Availability (Week 3-4)
- Enable for all users (level: contributor+)
- Full rate limits
- Launch marketing campaign

### Phase 3: Optimization (Month 2)
- ML model tuning based on data
- UI improvements from feedback
- Performance optimization

## 🐛 Troubleshooting

### Issue: Reviews not being assigned

```python
# Check reviewer pool
SELECT count(*) FROM user_reputation
WHERE total_points >= 100
AND expertise->>'bia' >= '50';

# If < 3: Lower thresholds temporarily
COMMUNITY_MIN_REPUTATION_TO_REVIEW=50
```

### Issue: Synthesis failing

```python
# Check LLM service
await llm_client.health_check()

# Verify knowledge graph connection
await kg.get_clause("4.1")

# Check case library
await case_library.find_cases_addressing_clause("4.1")
```

### Issue: High anonymization risk

```python
# Review anonymizer config
COMMUNITY_K_ANONYMITY=10  # Increase
COMMUNITY_MAX_RISK_SCORE=0.5  # Stricter

# Manual review queue
SELECT * FROM case_contributions
WHERE case_data->>'risk_score'::float > 0.7;
```

## 📞 Support

- **Documentation**: `/doc-project/community_intelligence/`
- **API Docs**: `https://api.platform.com/docs#community`
- **Slack**: `#community-intelligence`
- **Email**: `community@ai-platform-iso.com`

---

**Ready to empower your community! 🚀**
