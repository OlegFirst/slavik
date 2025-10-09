# Predictive Journey Service - Business Logic

**Document Version**: 1.0.0
**Last Updated**: 2025-10-09

## 1. Business Overview

### 1.1 Purpose

The Predictive Journey Service provides organizations with foresight into their business continuity management journey, enabling proactive planning, resource allocation, and risk mitigation. It transforms historical journey data into actionable intelligence.

### 1.2 Business Value

**For Organizations:**
- **Planning Certainty**: 90-day visibility into upcoming milestones
- **Resource Optimization**: Advance notice for expert booking and resource preparation
- **Cost Predictability**: Transparent cost estimates based on similar organizations
- **Risk Mitigation**: Early awareness of likely challenges with proven mitigation strategies
- **Timeline Confidence**: Data-driven certification date forecasting

**For Experts/Consultants:**
- **Demand Visibility**: Forecast upcoming project opportunities
- **Capacity Planning**: Plan availability based on predicted demand peaks
- **Geographic Insights**: Understand where demand is concentrated
- **Specialty Trends**: Identify high-demand areas

**For Platform:**
- **User Engagement**: Daily touchpoints via proactive recommendations
- **Marketplace Efficiency**: Match supply and demand proactively
- **Retention**: Demonstrate long-term value with journey visibility
- **Network Effects**: Better predictions as more journeys complete

## 2. Core Business Functions

### 2.1 Journey Timeline Prediction

#### Business Logic

Organizations follow predictable patterns in their BCM journey. By analyzing completed journeys from similar organizations, the service can forecast:

- **Next Milestones**: What activities are likely to come next
- **Timing**: When milestones will likely start
- **Duration**: How long each milestone typically takes
- **Sequence**: The order in which milestones occur

#### Pattern Matching Rules

```
Similar Organization Definition:
- Industry match (healthcare → healthcare)
- Comparable size (200 employees ≈ 250 employees)
- Similar maturity level (Level 2 ≈ Level 2)
- Comparable resources (dedicated team presence)
- Geographic proximity (same region/continent)

Minimum Similarity Threshold: 50%
Target Similar Organizations: 50
Minimum for Prediction: 3
```

#### Confidence Business Rules

**High Confidence (>0.80)**
- 50+ similar organizations
- 80%+ pattern frequency
- Low timing variance (±3 days)
- Recent data (<30 days)
- **Business Impact**: Strong recommendation, schedule now

**Medium Confidence (0.60-0.80)**
- 15-49 similar organizations
- 60-80% pattern frequency
- Moderate variance (±7 days)
- Data within 90 days
- **Business Impact**: Recommended, plan ahead

**Low Confidence (0.40-0.60)**
- 5-14 similar organizations
- 40-60% pattern frequency
- High variance (±14 days)
- Data older than 90 days
- **Business Impact**: Advisory only, requires judgment

**Insufficient Data (<0.40)**
- <5 similar organizations
- **Business Impact**: No prediction, manual planning required

### 2.2 Certification Timeline Prediction

#### Business Logic

ISO 22301 certification achievement follows a measurable pattern based on:

- **Journey Completeness**: Percentage of required milestones completed
- **Progress Pace**: Current duration vs. benchmark
- **Success Patterns**: Characteristics of successfully certified organizations
- **Risk Factors**: Indicators that correlate with certification failure

#### Success Probability Calculation

```
Success Probability Factors:
1. Milestone Completion Rate (40% weight)
   - All required milestones completed: +40%
   - Missing critical milestones: -40%

2. Timeline Adherence (30% weight)
   - On schedule vs. benchmark: +30%
   - Significantly delayed: -30%

3. Success Pattern Presence (30% weight)
   - Dedicated BCM team: +10%
   - Executive sponsorship: +10%
   - Regular progress reviews: +5%
   - External expert engagement: +5%

Base Success Rate: Industry average from similar orgs
```

#### Key Success Factors (Business Rules)

**Critical Success Factors:**
1. **Dedicated BCM Team**: 92% of certified organizations had dedicated team
2. **Executive Sponsorship**: 88% had C-level sponsor
3. **Regular Reviews**: 85% conducted bi-weekly progress reviews
4. **Expert Guidance**: 82% engaged external consultants
5. **Compliance Culture**: 78% had prior ISO certifications

### 2.3 Proactive Recommendations

#### Business Logic

The service delivers timely, actionable guidance to keep organizations on track. Recommendations are triggered based on predicted milestones and optimized for maximum impact.

#### Timing Optimization Rules

**Starting Today (0-1 days)**
- **Priority**: Critical
- **Message**: "Action required now"
- **Content**: Immediate next steps, quick-start guides
- **Business Rationale**: Prevent delays, ensure readiness

**Preparation Phase (1-3 days)**
- **Priority**: High
- **Message**: "Prepare now"
- **Content**: Prerequisites, resource gathering, team scheduling
- **Business Rationale**: Enable smooth start, avoid scrambling

**One Week Notice (4-7 days)**
- **Priority**: Medium
- **Message**: "Coming up soon"
- **Content**: Awareness, high-level planning, expert booking
- **Business Rationale**: Allow adequate planning time

**Future Awareness (8+ days)**
- **Priority**: Low
- **Message**: "On the horizon"
- **Content**: Strategic planning, resource budgeting
- **Business Rationale**: Long-term visibility

#### Resource Recommendation Logic

```
For each predicted milestone:
  1. Identify resource type (template, guide, tool, expert)
  2. Filter by organization context (industry, size)
  3. Prioritize by:
     - Relevance to milestone
     - Usage frequency in similar organizations
     - Success correlation
  4. Limit to top 3-5 resources per milestone

Resource Types:
- Templates: Pre-built documents (BIA worksheet, risk register)
- Videos: Tutorials and best practice demonstrations
- Case Studies: Examples from 5 similar organizations
- Tools: Calculators, assessment forms, automation scripts
- Guides: Step-by-step methodology documentation
- Experts: Consultants with relevant specialty
```

### 2.4 Expert Demand Forecasting

#### Business Logic

By aggregating journey predictions across all active organizations, the service forecasts expert demand to optimize marketplace efficiency.

#### Aggregation Rules

```
For each specialty (BIA, Risk, Planning, etc.):
  1. Collect journey predictions for all organizations
  2. Extract expert needs from each milestone
  3. Group by time window (weekly buckets)
  4. Aggregate by:
     - Specialty
     - Geographic region
     - Industry vertical
  5. Calculate confidence from underlying predictions
```

#### Shortage Detection Logic

```
Shortage Ratio = Forecasted Demand / Available Supply

Critical Shortage (Ratio > 5.0):
  - Alert platform recruitment team
  - Notify existing experts of high demand
  - Suggest pricing optimization

High Shortage (Ratio > 2.0):
  - Weekly notifications to specialists
  - Highlight opportunity in marketplace
  - Enable proactive outreach

Balanced Market (Ratio 0.8-2.0):
  - Standard marketplace operation
  - Regular demand updates

Oversupply (Ratio < 0.8):
  - Suggest specialists expand to related areas
  - Highlight competitive landscape
```

#### Specialist Notifications

**Weekly Digest Content:**
- Total projects expected in specialist's areas
- Peak weeks for demand
- Geographic distribution
- Industry breakdown
- Confidence scores
- Comparison to previous forecasts

### 2.5 Challenge Prediction and Mitigation

#### Business Logic

Organizations encounter predictable challenges at each milestone. By analyzing failure patterns and obstacles from similar journeys, the service provides early warnings and proven mitigation strategies.

#### Challenge Identification Rules

```
For each milestone:
  1. Query similar organizations for recorded challenges
  2. Calculate challenge frequency
  3. Filter challenges with probability > 30%
  4. Rank by frequency * impact
  5. Map to pre-defined mitigation strategies
```

#### Common Challenges by Milestone

**BIA (Business Impact Analysis)**
- Data availability (45% probability)
  - **Mitigation**: Start with available data, use industry templates
- Stakeholder engagement (38% probability)
  - **Mitigation**: Executive sponsor sends mandate, schedule interviews
- Scope creep (32% probability)
  - **Mitigation**: Define clear boundaries upfront, phase approach

**Risk Assessment**
- Incident data gaps (52% probability)
  - **Mitigation**: Use industry benchmarks, expert consultation
- Quantification complexity (41% probability)
  - **Mitigation**: Start with qualitative, use FAIR framework
- Resource constraints (35% probability)
  - **Mitigation**: Prioritize critical processes, external support

**BC Planning**
- Strategy alignment (48% probability)
  - **Mitigation**: Executive workshops, clear RTOs/RPOs
- Resource identification (44% probability)
  - **Mitigation**: Cross-functional teams, inventory analysis
- Plan complexity (39% probability)
  - **Mitigation**: Template-based approach, phased development

### 2.6 Cost Estimation

#### Business Logic

Organizations need budget visibility for planning and resource allocation. The service provides cost estimates based on historical data from similar organizations.

#### Cost Calculation Rules

```python
# Base cost per milestone (internal staff time)
BASE_COSTS = {
    'bia': 200 USD/day,
    'risk_assessment': 250 USD/day,
    'governance': 150 USD/day,
    'planning': 200 USD/day,
    'validation': 220 USD/day,
    'compliance': 300 USD/day
}

# Duration from similar organizations
duration_days = statistical_average(similar_orgs.duration)

# Base estimate
base_cost = BASE_COSTS[milestone] * duration_days

# Size adjustment
if org.size == 'large' (500+ employees):
    adjusted_cost = base_cost * 1.30  # +30%
elif org.size == 'small' (<50 employees):
    adjusted_cost = base_cost * 0.70  # -30%
else:
    adjusted_cost = base_cost  # Medium size baseline

# Variance (±20% range)
min_cost = adjusted_cost * 0.80
max_cost = adjusted_cost * 1.20

# External expert costs (if recommended)
expert_cost = expert_daily_rate * estimated_days_needed
```

#### Cost Presentation Rules

- Always show as a range (min-max)
- Separate internal vs. external costs
- Provide currency and cost basis
- Include cost-benefit context (e.g., "82% of orgs found this investment worthwhile")
- Offer comparison to industry benchmarks

## 3. Business Workflows

### 3.1 New Organization Onboarding

```
1. Organization completes BIA
   ↓
2. System triggers journey prediction
   ↓
3. Generate 90-day timeline
   ↓
4. Send welcome email with:
   - Your predicted journey
   - Certification timeline estimate
   - First recommended actions
   ↓
5. Schedule first daily digest
   ↓
6. Publish prediction.forecast_generated event
```

### 3.2 Daily Digest Workflow

```
Daily at 8:00 AM:

1. Query all active organizations
   ↓
2. For each organization:
   - Get cached journey prediction
   - Filter milestones within 7 days
   - Identify required preparations
   - Select relevant resources
   ↓
3. Generate personalized email:
   - Upcoming milestones
   - Action items
   - Resource links
   - Expert recommendations
   ↓
4. Batch send via Notification Service
   ↓
5. Log delivery metrics
   ↓
6. Update engagement tracking
```

### 3.3 Milestone Completion Workflow

```
1. Workflow completion event received
   ↓
2. Update organization's journey state
   ↓
3. Re-calculate predictions (now more accurate)
   ↓
4. Compare actual vs. predicted:
   - Duration variance
   - Timeline adherence
   - Success/failure outcomes
   ↓
5. Update pattern database (learning)
   ↓
6. Adjust confidence scores
   ↓
7. Publish updated predictions
   ↓
8. Trigger next milestone preparation email
```

### 3.4 Expert Demand Forecast Workflow

```
Weekly on Monday:

1. Aggregate all organization predictions
   ↓
2. Extract expert needs by specialty
   ↓
3. Group by week and geography
   ↓
4. Calculate demand forecast
   ↓
5. Identify peak weeks
   ↓
6. Detect shortage areas
   ↓
7. Send specialist notifications:
   - "5 BIA projects expected in healthcare next month"
   - Peak week: October 18
   - Regions: Northeast, West Coast
   ↓
8. Alert recruitment team if shortages detected
   ↓
9. Publish demand forecast event
```

## 4. Business Rules Reference

### 4.1 Prediction Generation Rules

| Rule | Condition | Action |
|------|-----------|--------|
| Minimum Data | <3 similar organizations | Return "insufficient data" error |
| Low Confidence | Confidence <0.5 | Add disclaimer, mark as advisory |
| High Variance | Std dev >40% of mean | Widen prediction range, lower confidence |
| Outdated Data | Data >180 days old | Apply recency penalty to confidence |
| Pattern Threshold | Frequency <30% | Exclude pattern from predictions |

### 4.2 Recommendation Timing Rules

| Days Until | Priority | Notification Channel | Content Type |
|------------|----------|---------------------|--------------|
| 0-1 | Critical | Email + SMS | Immediate actions |
| 2-3 | High | Email | Preparation steps |
| 4-7 | Medium | Email (daily digest) | Awareness, planning |
| 8-14 | Low | Email (weekly digest) | Strategic planning |
| 15+ | Info | Platform notification | Future visibility |

### 4.3 Expert Matching Rules

| Factor | Weight | Matching Logic |
|--------|--------|----------------|
| Specialty | 40% | Exact match required |
| Industry Experience | 30% | Same industry preferred |
| Organization Size | 15% | Similar size experience |
| Success Rate | 10% | >85% client satisfaction |
| Availability | 5% | Can start within predicted timeframe |

### 4.4 Cost Accuracy Rules

- Show ranges (±20%) not exact numbers
- Update estimates quarterly based on actual data
- Separate internal vs. external costs
- Provide cost-benefit context
- Include industry benchmark comparison

## 5. Success Metrics

### 5.1 Prediction Accuracy

**Target**: 80% of predictions within ±7 days of actual
**Measurement**: Compare predicted start dates to actual completion dates

### 5.2 User Engagement

**Daily Digest Open Rate**: Target 45%
**Recommendation Action Rate**: Target 35% (users take recommended action)
**Expert Booking from Forecasts**: Target 25%

### 5.3 Business Impact

**Timeline Adherence**: Organizations using predictions complete 20% faster
**Resource Efficiency**: 30% reduction in last-minute resource scrambling
**Expert Utilization**: 40% better capacity planning for specialists
**Certification Success Rate**: 15% higher for organizations using predictions

## 6. Decision Framework

### 6.1 When to Show Predictions

**Show Prediction If:**
- Confidence ≥0.5
- Based on ≥3 similar organizations
- Pattern frequency ≥30%
- Data recency <180 days

**Show with Disclaimer If:**
- Confidence 0.4-0.5
- Based on 3-5 similar organizations
- Limited data available

**Do Not Show Prediction If:**
- Confidence <0.4
- Based on <3 similar organizations
- Pattern frequency <30%
- Contradictory patterns present

### 6.2 When to Send Proactive Recommendations

**Send Daily Digest If:**
- Organization has active journey
- At least one milestone within 14 days
- Organization opted in to notifications
- Last digest >23 hours ago (respect daily limit)

**Do Not Send If:**
- Organization paused journey
- No upcoming milestones (journey complete)
- User unsubscribed
- Sent digest in last 23 hours

### 6.3 When to Alert About Shortages

**Alert Recruitment If:**
- Shortage ratio >5.0 (critical)
- Persistent shortage >4 weeks
- High-priority specialty (BIA, Risk, Validation)

**Notify Specialists If:**
- Shortage ratio >2.0
- Demand increase >50% vs. previous month
- Geographic opportunity (specialist's region)

## 7. Business Constraints

### 7.1 Data Privacy

- Never expose organization names in similar case data
- Anonymize all PII in demand forecasts
- Aggregate data only (no individual journey exposure)
- Tenant isolation in all predictions

### 7.2 Communication Limits

- Maximum 1 daily digest per organization per day
- Maximum 1 weekly specialist forecast per specialty
- Respect unsubscribe preferences immediately
- Provide clear opt-out mechanisms

### 7.3 Prediction Limitations

- 90-day maximum prediction horizon (accuracy degrades beyond)
- Require minimum 3 similar organizations (quality threshold)
- Pattern frequency minimum 30% (avoid noise)
- Confidence floor 0.4 (below = no prediction)

---

**Document Control**
- Version: 1.0.0
- Author: AI Platform Team
- Business Owner: Product Management
- Review Date: 2025-10-09
- Next Review: 2026-01-09
