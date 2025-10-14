# Simulation Service Integration with Scenario Intelligence

**Created**: 2025-10-12
**Status**: Integration Plan
**Related**: `/platform-services/simulation/scenarios/`

---

## 📋 Overview

This document describes how the **Simulation Service** integrates with the **Scenario Intelligence System** to create a powerful testing and training ecosystem.

---

## 🔗 Integration Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   Scenario Intelligence                       │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Scenario Manager                                       │  │
│  │  - Generates L1/L2/L3/L4 scenarios                     │  │
│  │  - Stores in scenario_intelligence.scenarios           │  │
│  └────────────────────────────────────────────────────────┘  │
│                           │                                   │
│                           │ EventBus                          │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Scenario Executor                                      │  │
│  │  - Executes scenarios                                   │  │
│  │  - Collects results                                     │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                           │
                           │ Publishes: scenario.execution.completed
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                   Simulation Service                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Scenario Orchestrator                                  │  │
│  │  - Converts technical scenarios to BCM exercises        │  │
│  │  - AI-generates realistic BCM scenarios                │  │
│  │  - Stores in simulation.scenarios table                │  │
│  └────────────────────────────────────────────────────────┘  │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Simulation Platform (Port 3001)                        │  │
│  │  - Tabletop exercises (2-4h)                           │  │
│  │  - Functional exercises (4-8h)                         │  │
│  │  - Full-scale exercises (1-3 days)                     │  │
│  └────────────────────────────────────────────────────────┘  │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Exercise Execution                                     │  │
│  │  - Real users participate                               │  │
│  │  - Actions logged                                       │  │
│  │  - Results collected                                    │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                           │
                           │ Publishes: simulation.exercise.completed
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                   Learning System                             │
│  - Analyzes both technical and business results              │
│  - Identifies gaps and improvement opportunities             │
│  - Feeds back to Scenario Intelligence                       │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎯 Integration Points

### 1. **Technical Scenarios → BCM Exercises**

**Flow**: L1/L2/L3 scenarios (infrastructure testing) → BCM exercises (business continuity training)

**Example**:
```yaml
# L3 Scenario: System Resilience Test
name: "Database Subsystem Failure Recovery"
type: "technical"
scenario:
  - PostgreSQL fails
  - Redis takeover activated
  - Services continue with degradation
  - Automatic recovery in 2 minutes

# Converted to BCM Exercise
title: "Data Center Primary Database Failure"
category: "infrastructure_disruption"
level: "tabletop"
duration: 2 hours
participants: [DBA, DevOps, BCM Manager, Business Unit Lead]
scenario:
  - "Your primary database has gone offline"
  - "Customer orders cannot be processed"
  - "Support team cannot access customer data"
  - "Revenue impact: $10,000/minute"
discussion_points:
  - "What is your immediate response?"
  - "Who needs to be notified?"
  - "What is the recovery procedure?"
  - "How do you communicate with customers?"
```

**Implementation**:
```python
class ScenarioToBCMConverter:
    """Converts technical scenarios to BCM exercises."""

    def convert_l3_scenario(self, scenario: Dict) -> BCMExercise:
        """
        Convert L3 functional system scenario to BCM exercise.

        Technical focus → Business impact focus
        Infrastructure failure → Business disruption
        Recovery metrics → Business continuity
        """
        return BCMExercise(
            title=self._generate_business_title(scenario),
            category=self._map_to_bcm_category(scenario),
            level=self._determine_exercise_level(scenario),
            scenario_narrative=self._create_narrative(scenario),
            discussion_points=self._extract_discussion_points(scenario),
            success_criteria=self._define_business_success(scenario)
        )
```

---

### 2. **L4 User Workflows → User Training**

**Flow**: L4 user workflow scenarios → Simulation Platform training exercises

**Example**:
```yaml
# L4 Workflow: BIA Creation
workflow_name: "Complete BIA Workflow"
user_role: "BCM Manager"
steps:
  - Login to BCM Portal
  - Navigate to BIA module
  - Create new BIA
  - Analyze dependencies
  - Calculate impact
  - Generate report

# Converted to Training Exercise
exercise_type: "guided_practice"
title: "BIA Creation Training"
duration: 1 hour
participants: [New BCM Manager]
training_steps:
  - "Watch video tutorial (10 min)"
  - "Complete guided BIA (30 min)"
  - "Review with mentor (15 min)"
  - "Take quiz (5 min)"
validation:
  - BIA completed correctly
  - All required fields filled
  - Impact calculations accurate
```

---

### 3. **AI-Generated Scenarios**

Both systems use AI for scenario generation:

**Scenario Intelligence (L4)**:
- Uses OpenAI/Claude for user workflow generation
- Context: User role, business objective, systems involved
- Output: Detailed user journey with test steps

**Simulation Service**:
- Uses existing AI orchestrator for BCM scenario generation
- Context: Industry, risk type, organization size
- Output: Realistic BCM exercise scenario with narrative

**Integration Opportunity**:
```python
class UnifiedAIScenarioGenerator:
    """Unified AI scenario generator for both systems."""

    def generate_scenario(self,
                         scenario_type: str,  # "technical" or "bcm"
                         context: Dict,
                         level: int) -> Dict:
        """
        Generate scenarios using unified AI approach.

        For technical (L1/L2/L3): Focus on infrastructure, services, integration
        For BCM (L4 + exercises): Focus on business impact, user actions, decisions
        """
        if scenario_type == "technical":
            return self._generate_technical_scenario(context, level)
        else:
            return self._generate_bcm_scenario(context, level)
```

---

## 📊 Data Flow

### Scenario Intelligence → Simulation Service

```python
# EventBus Event
{
    "event_type": "scenario.execution.completed",
    "data": {
        "scenario_id": "l3-resilience-database-001",
        "level": 3,
        "execution_results": {
            "duration": "15 minutes",
            "success": true,
            "failures_detected": ["redis_connection_timeout"],
            "recovery_time": "2m 15s"
        },
        "systems_involved": ["database_infrastructure", "runtime_services"],
        "business_impact": "medium"
    }
}

# Simulation Service subscribes and processes
@eventbus.subscribe("scenario.execution.completed")
async def convert_to_bcm_exercise(event):
    """Convert technical scenario results to BCM exercise."""

    scenario = event.data

    # Analyze technical failure for business impact
    business_impact = analyze_business_impact(scenario)

    # Generate BCM exercise
    bcm_exercise = BCMExercise(
        title=f"Business Continuity: {business_impact.title}",
        category=business_impact.category,
        level="tabletop",
        duration=2,  # hours
        scenario_narrative=generate_narrative(scenario),
        affected_systems=scenario.systems_involved,
        discussion_points=[
            "How would this impact business operations?",
            "What is the recovery priority?",
            "Who needs to be involved?",
            "What are the communication requirements?"
        ],
        learning_objectives=[
            "Understand technical → business impact mapping",
            "Practice BCM response procedures",
            "Identify gaps in continuity plans"
        ],
        source_scenario=scenario.scenario_id
    )

    # Store in simulation database
    await simulation_db.save_exercise(bcm_exercise)

    # Publish event
    await eventbus.publish("simulation.exercise.created", bcm_exercise)
```

---

### Simulation Service → Learning System

```python
# EventBus Event
{
    "event_type": "simulation.exercise.completed",
    "data": {
        "exercise_id": "bcm-ex-001",
        "title": "Data Center Primary Database Failure",
        "duration": "2 hours",
        "participants": 8,
        "results": {
            "response_time": "5 minutes",
            "correct_procedures_followed": 7,
            "missed_procedures": 1,
            "communication_effectiveness": 4.2,
            "overall_score": 8.5
        },
        "gaps_identified": [
            "Notification escalation procedure unclear",
            "Customer communication template missing"
        ],
        "source_scenario": "l3-resilience-database-001"
    }
}

# Learning System processes
@eventbus.subscribe("simulation.exercise.completed")
async def learn_from_exercise(event):
    """Extract learning from BCM exercise."""

    exercise = event.data

    # Find source technical scenario
    source_scenario = await get_scenario(exercise.source_scenario)

    # Compare technical vs business response
    learning_insights = {
        "technical_recovery_time": "2m 15s",
        "business_response_time": "5 minutes",
        "gap_reason": "Notification delay",
        "improvement_recommendation": "Automate business notifications"
    }

    # Update scenario with business learnings
    await scenario_intelligence.add_learning(
        scenario_id=source_scenario.id,
        learning_data=learning_insights
    )

    # Improve technical scenario based on business feedback
    if learning_insights.gap_reason == "Notification delay":
        await scenario_intelligence.improve_scenario(
            scenario_id=source_scenario.id,
            improvement="Add notification validation to test steps"
        )
```

---

## 🗄️ Database Schema Integration

### Scenario Intelligence Tables

```sql
CREATE TABLE scenario_intelligence.scenarios (
  id UUID PRIMARY KEY,
  level INT,  -- 1, 2, 3, 4
  name TEXT,
  content JSONB,
  -- Link to simulation exercises
  simulation_exercises UUID[] DEFAULT '{}'
);
```

### Simulation Service Tables

```sql
CREATE TABLE simulation.scenarios (
  id UUID PRIMARY KEY,
  title TEXT,
  category TEXT,
  level TEXT,  -- tabletop, functional, full-scale
  content_md TEXT,
  -- Link back to technical scenario
  source_technical_scenario UUID REFERENCES scenario_intelligence.scenarios(id)
);

CREATE TABLE simulation.exercises (
  id UUID PRIMARY KEY,
  scenario_id UUID REFERENCES simulation.scenarios(id),
  scheduled_at TIMESTAMPTZ,
  participants UUID[],
  results JSONB
);
```

---

## 🔄 Bidirectional Learning

### Technical → Business Learning

1. **Technical scenario identifies infrastructure weakness**
   - Example: Redis connection pool exhaustion under load

2. **Converted to BCM exercise**
   - "Your customer support system is slow during peak hours"

3. **Business team exercises response**
   - Identifies need for customer communication plan
   - Discovers business impact: $50K revenue at risk

4. **Feedback to technical scenario**
   - Add validation: "Check customer notification system"
   - Add metric: "Customer communication latency"
   - Increase priority: "Critical" (due to revenue impact)

### Business → Technical Learning

1. **BCM exercise reveals gap**
   - Example: "Team couldn't determine which systems were affected"

2. **Translated to technical requirement**
   - Need: "Real-time system dependency visualization"

3. **New technical scenario created**
   - L3 scenario: "System Dependency Discovery Under Failure"
   - Test: Can teams quickly identify affected systems?

4. **Technical solution implemented**
   - Improve monitoring dashboard
   - Add dependency graph to incident response

---

## 🎯 Use Cases

### Use Case 1: Automated Exercise Generation

**Trigger**: L3 resilience scenario fails

**Flow**:
```
1. Scenario Intelligence: "Database subsystem resilience test FAILED"
   - PostgreSQL crash recovery took 5 minutes (target: 2 minutes)
   - 3 services didn't handle failure gracefully

2. AI Analysis: "This is a HIGH business impact failure"
   - Revenue impact: $50,000
   - Customer impact: 5,000 users

3. Simulation Service: AUTO-GENERATE BCM exercise
   - Title: "Critical: Database Outage Response"
   - Category: "infrastructure_disruption"
   - Level: "functional" (requires real actions)
   - Participants: [DBA, DevOps, BCM Manager, CTO]

4. Schedule exercise for next week
5. Notify participants via EventBus
```

---

### Use Case 2: Training New BCM Staff

**Trigger**: New BCM Manager joins

**Flow**:
```
1. Simulation Service: Create training plan
   - Week 1: L4 workflows (user training)
     - BIA creation workflow
     - Risk assessment workflow
     - Plan development workflow

2. Execute L4 scenarios as guided tutorials
   - Scenario Intelligence provides step-by-step validation
   - User completes real workflows in test environment

3. Week 2: Tabletop exercises
   - Convert L3 scenarios to tabletop exercises
   - User participates with mentor

4. Week 3: Functional exercises
   - Full BCM response simulation
   - User leads response

5. Certification: Pass all L4 workflows + 3 exercises
```

---

### Use Case 3: Continuous Improvement Loop

**Flow**:
```
┌─────────────────────────────────────────────────────────┐
│ 1. Technical Scenario Execution                         │
│    - L3 system resilience test runs weekly              │
│    - Results stored in scenario_intelligence.executions │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Convert to BCM Exercise                              │
│    - Auto-generate quarterly BCM exercise               │
│    - Based on recent technical failures                 │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Execute BCM Exercise                                 │
│    - Business team responds to scenario                 │
│    - Actions logged, decisions recorded                 │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Analyze Results                                      │
│    - Compare technical vs business response             │
│    - Identify gaps (e.g., notification delays)          │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 5. Improve Both Systems                                 │
│    - Update technical scenario (add notification test)  │
│    - Update BCM exercise (add communication step)       │
│    - Improve monitoring (add business impact metrics)   │
└─────────────────────────────────────────────────────────┘
                         │
                         └──────► Back to step 1
```

---

## 🚀 Implementation Plan

### Phase 1: Basic Integration (Week 1)

1. **Create event subscriptions**
   - Simulation Service subscribes to `scenario.execution.completed`
   - Scenario Intelligence subscribes to `simulation.exercise.completed`

2. **Create data links**
   - Add `source_technical_scenario` to simulation.scenarios
   - Add `simulation_exercises[]` to scenario_intelligence.scenarios

3. **Test bidirectional event flow**

### Phase 2: Scenario Conversion (Week 2)

1. **Implement ScenarioToBCMConverter**
   - L3 → Tabletop exercises
   - L2 → Component failure exercises

2. **Test conversions**
   - Pick 5 L3 scenarios
   - Generate BCM exercises
   - Review with BCM experts

### Phase 3: AI Unification (Week 3-4)

1. **Create UnifiedAIScenarioGenerator**
   - Unified prompt templates
   - Context management
   - Quality validation

2. **Integrate with both services**
   - Replace separate AI generators
   - Test generation quality

### Phase 4: Learning Loop (Week 5-6)

1. **Implement learning feedback**
   - Exercise results → Technical scenarios
   - Technical failures → BCM exercises

2. **Create improvement workflows**
   - Automated scenario updates
   - Manual review process

### Phase 5: User Training (Week 7-8)

1. **L4 workflow → Training converter**
2. **Training progress tracking**
3. **Certification system**

---

## 📊 Success Metrics

### Integration Health
- **Event delivery success rate**: > 99%
- **Conversion success rate**: > 95% (scenarios → exercises)
- **Learning feedback cycle time**: < 1 week

### Business Value
- **Exercise generation time**: Reduced from 8 hours to 30 minutes
- **Training effectiveness**: +40% faster onboarding
- **Gap identification**: 3x more gaps found through combined approach

### Technical Quality
- **Scenario quality score**: > 4.0/5.0
- **Exercise realism score**: > 4.5/5.0
- **Learning application rate**: > 80% of insights applied

---

## 🔗 API Integration

### Scenario Intelligence API

```python
# GET /api/scenarios/{id}/convert-to-exercise
@app.get("/api/scenarios/{scenario_id}/convert-to-exercise")
async def convert_scenario_to_exercise(scenario_id: str):
    """Convert technical scenario to BCM exercise."""

    scenario = await scenario_db.get(scenario_id)
    exercise = await converter.convert(scenario)

    # Save to simulation service
    await simulation_api.create_exercise(exercise)

    return exercise
```

### Simulation Service API

```python
# POST /api/exercises/from-scenario
@app.post("/api/exercises/from-scenario")
async def create_exercise_from_scenario(
    scenario_id: str,
    exercise_type: str,  # tabletop, functional, full-scale
    participants: List[str]
):
    """Create BCM exercise from technical scenario."""

    # Fetch scenario from Scenario Intelligence
    scenario = await scenario_intelligence_api.get_scenario(scenario_id)

    # Convert
    exercise = await orchestrator.generate_exercise(
        scenario=scenario,
        exercise_type=exercise_type
    )

    # Schedule
    await schedule_exercise(exercise, participants)

    return exercise
```

---

## 📝 Configuration

```yaml
# scenario_intelligence/config.yaml
simulation_integration:
  enabled: true
  simulation_service_url: "http://simulation-service:3001"
  auto_convert_on_failure: true
  conversion_rules:
    - level: 3
      failure_severity: "high"
      exercise_type: "functional"
    - level: 2
      failure_severity: "critical"
      exercise_type: "tabletop"

# simulation/config.yaml
scenario_intelligence_integration:
  enabled: true
  scenario_intelligence_url: "http://scenario-manager:8050"
  subscribe_to_events:
    - "scenario.execution.completed"
    - "scenario.improved"
  publish_events:
    - "simulation.exercise.completed"
    - "simulation.gap.identified"
```

---

## 🎉 Benefits

### For Technical Teams
- **Realistic testing**: BCM exercises reveal real-world failure modes
- **Business context**: Understand business impact of technical failures
- **Continuous feedback**: Business team identifies technical gaps

### For Business Teams
- **Realistic scenarios**: Based on actual infrastructure capabilities
- **Technical validation**: Exercises reflect real system behavior
- **Measurable impact**: Technical metrics show business risk

### For Organization
- **Unified view**: Technical + business continuity in one platform
- **Cost savings**: Automated exercise generation
- **Better preparedness**: Continuous improvement loop
- **Compliance**: ISO 22301 + technical best practices

---

**Status**: ✅ Integration Plan Complete - Ready for Implementation
**Next Step**: Phase 1 implementation (Week 1)
