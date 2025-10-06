# Workflow Definitions (YAML)

Declarative workflow definitions for BCM processes following ISO 22301:2019.

## 📁 Available Workflows

### 1. [bia_process.yaml](bia_process.yaml)
**Business Impact Analysis** - ISO 22301:2019 Clause 8.2.2

**Stages:**
1. `identify_processes` - Identify critical business processes (Creative Zone)
2. `analyze_dependencies` - Map process dependencies (Creative Zone)
3. `assess_impact` - Quantify disruption impacts (Creative Zone)
4. `determine_rto` - Set recovery objectives (Creative Zone)
5. `review_results` - Validate and approve (Checkpoint)
6. `completed` - BIA finalized

**Duration:** 14-30 days
**Checkpoints:** 5
**Creative Zones:** 4

---

### 2. [risk_assessment.yaml](risk_assessment.yaml)
**Risk Assessment** - ISO 22301:2019 Clause 8.2.3

**Stages:**
1. `identify_threats` - Identify potential threats (Creative Zone)
2. `assess_risks` - Calculate risk scores (Checkpoint)
3. `prioritize_risks` - Rank and categorize (Creative Zone)
4. `plan_treatments` - Develop mitigation plans (Creative Zone)
5. `review_approve` - Final approval (Checkpoint)
6. `completed` - Assessment finalized

**Duration:** 10-21 days
**Checkpoints:** 4
**Creative Zones:** 3

---

### 3. [planning_process.yaml](planning_process.yaml)
**BC Strategy & Planning** - ISO 22301:2019 Clause 8.3, 8.4

**Stages:**
1. `develop_strategies` - Design recovery strategies (Creative Zone)
2. `document_procedures` - Create detailed procedures (Creative Zone)
3. `plan_testing` - Schedule exercises (Checkpoint)
4. `review_approve` - Final approval (Checkpoint)
5. `completed` - Plans approved

**Duration:** 21-45 days
**Checkpoints:** 4
**Creative Zones:** 2

---

## 🏗️ YAML Structure

Each workflow definition contains:

```yaml
workflow:
  id: workflow_id
  name: Human-readable name
  version: 2.0
  module: module_name
  description: |
    Detailed description

metadata:
  iso_standard: ISO standard reference
  clause: Specific clause
  estimated_duration_days: X-Y
  prerequisites: [list of required workflows]

constitution:
  core_principles:
    - Immutable principles that cannot be violated
  forbidden_actions:
    - Actions AI/users cannot perform

stages:
  - id: stage_id
    name: Stage name
    order: 1
    type: creative_zone | checkpoint | final

    description: What this stage does

    objectives:
      - List of goals

    entry_criteria:
      - What must be true to enter

    exit_criteria:
      type: checkpoint | validation
      checkpoint_id: checkpoint_id
      rules:
        - List of rules to validate

    creative_zone:  # Only for creative_zone type
      creativity_level: low | medium | high
      allowed_approaches:
        - Approved methods
      guidance: |
        Instructions for AI advisor

    required_data:
      - field_name:
          type: string | number | enum | array
          required: true/false
          validation: constraints

ai_advisor:
  enabled: true/false
  proactive: true/false
  triggers:
    - Conditions when AI should act
  capabilities:
    - What AI can do

case_library:
  collect_events: true/false
  events_to_collect:
    - List of events to track
  success_criteria:
    - What defines successful completion

integrations:
  eventbus:
    publish_all_events: true/false
    subscribe_to:
      - Events to listen for
```

---

## 🎯 Key Concepts

### Checkpoints vs Creative Zones

**Checkpoints** (🔒 Strict Validation):
- Mandatory validation before proceeding
- Rules must all pass
- Cannot bypass
- Examples: Data completeness, regulatory requirements

**Creative Zones** (🎨 AI Freedom):
- AI has flexibility in HOW to help
- Multiple approaches allowed
- Guidance provides boundaries
- Examples: Suggesting processes, analyzing risks

### Constitution

Defines immutable principles that apply throughout workflow:
- **Core Principles**: Never violate (e.g., "RTO < 1h needs justification")
- **Forbidden Actions**: Cannot be performed

### Creativity Levels

- **LOW**: AI suggests from templates, minimal variation
- **MEDIUM**: AI can adapt approaches, combine methods
- **HIGH**: AI explores alternatives, creative problem-solving

---

## 🔌 Integration with Workflow Engine

### Loading Workflow Definition

```python
from workflow_intelligence.governance.yaml_workflows import YAMLWorkflowLoader

# Load workflow definition
loader = YAMLWorkflowLoader()
workflow_def = loader.load('workflows/definitions/bia_process.yaml')

# Initialize workflow engine with definition
from workflow_intelligence.core.workflow_engine import WorkflowEngine

engine = WorkflowEngine(
    module='bia',
    workflow_definition=workflow_def,
    tenant_id='tenant_123'
)

# Start workflow
await engine.start(workflow_id='bia-456')

# Check if can proceed to next stage
can_proceed = await engine.can_advance_to('analyze_dependencies')

# Transition
await engine.transition_to('analyze_dependencies')
```

### Checkpoint Validation

```python
from workflow_intelligence.governance.checkpoint_manager import CheckpointManager

checkpoint_mgr = CheckpointManager(rules_engine, creative_zones)

# Validate at checkpoint
result = await checkpoint_mgr.validate_checkpoint(
    checkpoint_id='bia_cp_001',
    workflow_data=current_data,
    stage='identify_processes'
)

if result.passed:
    # Can proceed
    await engine.transition_to('analyze_dependencies')
else:
    # Show violations
    print(f"Violations: {result.violations}")
    if result.requires_escalation:
        # Notify admin
        await notify_admin(result)
```

### AI Advisor Integration

```python
from workflow_intelligence.integration.ai_context_builder import AIContextBuilder

# AI automatically gets workflow definition context
context = await ai_context_builder.build_for_state(
    workflow_id='bia-456',
    state='identify_processes',
    tenant_id='tenant_123'
)

# Context includes:
# - Current stage creative zone guidance
# - Allowed approaches
# - Success criteria
# - Similar cases from case library
```

---

## 📊 Event Publishing

When workflow transitions occur, events published to EventBus:

```python
# Event published on stage change
{
  'event_type': 'workflow.state_changed',
  'data': {
    'workflow_id': 'bia-456',
    'from_state': 'identify_processes',
    'to_state': 'analyze_dependencies',
    'checkpoint_passed': 'bia_cp_001',
    'module': 'bia'
  }
}

# Event published on checkpoint failure
{
  'event_type': 'workflow.checkpoint_failed',
  'data': {
    'workflow_id': 'bia-456',
    'checkpoint_id': 'bia_cp_001',
    'violations': [...],
    'requires_escalation': true
  }
}
```

---

## 🧪 Testing Workflow Definitions

```python
# Validate YAML syntax and structure
from workflow_intelligence.governance.yaml_workflows import YAMLWorkflowValidator

validator = YAMLWorkflowValidator()
errors = validator.validate('workflows/definitions/bia_process.yaml')

if errors:
    print(f"Validation errors: {errors}")
else:
    print("✅ Workflow definition valid")

# Test stage transitions
assert workflow_def.can_transition('identify_processes', 'analyze_dependencies')
assert not workflow_def.can_transition('identify_processes', 'completed')

# Test checkpoint rules
checkpoint = workflow_def.get_checkpoint('bia_cp_001')
assert 'bia_mand_001' in checkpoint.rules
```

---

## 🔄 Workflow Lifecycle

```
1. Load YAML definition
   ↓
2. Initialize WorkflowEngine with definition
   ↓
3. Start workflow (creates instance)
   ↓
4. User works through stages
   ↓
5. Each transition:
   - Check entry criteria
   - Validate data
   - If checkpoint: run validation
   - Publish events
   - Update state
   ↓
6. Completion:
   - Create case for case library
   - Trigger dependent workflows
   - Update compliance status
```

---

## 📝 Creating New Workflow Definitions

1. **Copy template** (use bia_process.yaml as reference)
2. **Define stages** in logical order
3. **Mark checkpoints** where validation critical
4. **Identify creative zones** where AI can help
5. **Document data requirements** for each stage
6. **Set exit criteria** for progression
7. **Configure AI advisor** capabilities
8. **Test with validator**

---

## 🎓 Best Practices

1. **Checkpoints at critical decision points**
   - Before commitment (budget approval)
   - Before risk (production changes)
   - Before compliance (regulatory submission)

2. **Creative zones where judgment matters**
   - Problem diagnosis
   - Solution design
   - Risk assessment
   - Strategy selection

3. **Clear exit criteria**
   - Measurable conditions
   - Specific thresholds
   - Explicit requirements

4. **Actionable data requirements**
   - Required vs optional clear
   - Validation rules explicit
   - Calculated fields documented

5. **AI guidance is specific**
   - Not "help user"
   - But "suggest typical processes from case library for {industry}"

---

## 📚 References

- **ISO 22301:2019** - Security and resilience — Business continuity management systems
- **BCI GPG 2018** - Good Practice Guidelines
- **ISO 31000:2018** - Risk management guidelines

---

**Version:** 2.0
**Created:** October 2025
**Status:** Production Ready ✅
