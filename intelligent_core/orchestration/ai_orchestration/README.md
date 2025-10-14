# AI Orchestrator - The Brain of BCM Platform

The AI Orchestrator is the autonomous decision-making system at the heart of the BCM Platform. It aggregates context from all platform sources, assesses priority, selects strategies, validates safety, and executes or delegates decisions.

## Features

### 🧠 Intelligent Decision-Making
- **Context Aggregation**: Collects data from workflows, events, databases, and external sources
- **Priority Assessment**: Multi-factor priority scoring (business impact, time sensitivity, risk, compliance)
- **Strategy Selection**: Learns from historical cases and procedural memory
- **Safety Validation**: Constitutional rules, loop detection, hallucination checking

### 💾 4-Layer Memory System
1. **Working Memory** (Redis) - Current context, TTL 1 hour
2. **Short-Term Memory** (PostgreSQL) - Last 30 days of decisions
3. **Long-Term Memory** (Case Library + Vector DB) - Permanent case storage
4. **Procedural Memory** (ML Models) - Learned patterns and strategies

### 🛡️ Safety-First Architecture
- **Constitution Rules**: Immutable safety rules that cannot be bypassed
- **Loop Detection**: Prevents infinite loops and oscillations
- **Hallucination Detection**: Identifies AI-generated fabrications
- **Control Monitoring**: Prevents runaway AI and scope creep

### 🌱 Self-Evolution (3 Levels)
- **Level 1: Data Evolution** (Daily, automatic) - Learn from new cases
- **Level 2: Model Evolution** (Weekly, automatic) - Retrain ML models
- **Level 3: Code Evolution** (Monthly, human review required) - Suggest code improvements

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from intelligent_core.ai_orchestration import AIOrchestrator

# Initialize orchestrator
orchestrator = AIOrchestrator()
await orchestrator.initialize()

# Make decision
situation = {
    'workflow_stuck': True,
    'workflow_id': 'bia_001',
    'stuck_duration_minutes': 30
}

decision = await orchestrator.decide(situation, tenant_id='your_tenant')
print(f"Action: {decision.action.value}")
print(f"Rationale: {decision.rationale}")
print(f"Confidence: {decision.confidence:.2f}")

# Execute decision
result = await orchestrator.execute(decision)
```

### Run Examples

```bash
# Basic usage example
python examples/basic_usage.py

# Safety system demo
python examples/safety_demo.py
```

## Architecture

```
AIOrchestrator (Main)
│
├── DecisionCenter
│   ├── ContextAggregator     # Collects context from all sources
│   ├── PriorityEngine         # Assesses priority level
│   ├── StrategySelector       # Selects best strategy
│   └── DelegationManager      # Delegates to specialists
│
├── DistributedMemory
│   ├── WorkingMemory          # Redis (1 hour TTL)
│   ├── ShortTermMemory        # PostgreSQL (30 days)
│   ├── LongTermMemory         # Case Library (permanent)
│   └── ProceduralMemory       # ML models (learned patterns)
│
├── SafetyMonitor
│   ├── ConstitutionEnforcer   # Immutable rules
│   ├── LoopDetector           # Infinite loop detection
│   ├── HallucinationDetector  # AI hallucination check
│   └── ControlMonitor         # Loss of control prevention
│
└── EvolutionEngine
    ├── DataEvolution          # Daily (automatic)
    ├── ModelEvolution         # Weekly (automatic)
    └── CodeEvolution          # Monthly (human review)
```

## Configuration

### Event Bus Backend

```python
# In-memory (development)
orchestrator = AIOrchestrator(event_bus_backend='memory')

# Redis (production)
orchestrator = AIOrchestrator(event_bus_backend='redis')
```

### Enable/Disable Features

```python
orchestrator = AIOrchestrator(
    event_bus_backend='redis',
    enable_safety=True,      # Enable safety monitoring
    enable_evolution=True    # Enable self-evolution
)
```

## Safety Constitution

The orchestrator enforces immutable safety rules:

1. **Never modify user data without explicit permission**
2. **Never delete audit trail**
3. **Never modify production code without human review**
4. **Always escalate when confidence < 70%**
5. **Never bypass governance rules**
6. **Never expose sensitive data**
7. **Always maintain data integrity**

These rules **CANNOT** be changed by the AI or any automatic process.

## Decision Flow

```
1. Situation arrives
   ↓
2. Aggregate full context (platform state, workflows, events, history)
   ↓
3. Assess priority (business impact, time sensitivity, risk, compliance)
   ↓
4. Select strategies (from memory or generate new)
   ↓
5. Create decision (action, rationale, confidence)
   ↓
6. Safety validation (constitution, loops, hallucinations, control)
   ↓
7. Execute or delegate
   ↓
8. Store outcome for learning
```

## Memory Consolidation

Memory automatically consolidates across layers:

- **Working → Short-term**: After 1 hour
- **Short-term → Long-term**: After 30 days (if important)
- **Patterns → Procedural**: Continuous learning

## Evolution Cycles

### Data Evolution (Daily)
- Consolidate new cases
- Update case library
- Extract patterns
- Clean old data

### Model Evolution (Weekly)
- Retrain ML models
- A/B test new versions
- Auto-rollback if performance degrades
- Track performance metrics

### Code Evolution (Monthly)
- Analyze code performance
- Generate improvement suggestions
- Create pull requests
- **REQUIRES HUMAN REVIEW** before deployment

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_orchestrator.py -v
pytest tests/test_safety.py -v
```

## API Reference

### AIOrchestrator

Main orchestrator class.

**Methods:**
- `initialize()` - Initialize all components
- `decide(situation, tenant_id)` - Make decision for situation
- `execute(decision)` - Execute a decision
- `shutdown()` - Cleanup and shutdown
- `get_stats()` - Get orchestrator statistics

### Decision

Decision model with action, rationale, confidence, and metadata.

**Attributes:**
- `action: ActionType` - Action to take
- `rationale: str` - Why this decision
- `priority: PriorityLevel` - Priority level
- `confidence: float` - Confidence (0-1)
- `safety_approved: bool` - Passed safety checks

### ActionType (Enum)

- `AUTO_RESOLVE` - Automatically resolve the issue
- `DELEGATE` - Delegate to specialist agent
- `ESCALATE_HUMAN` - Escalate to human operator
- `WAIT_AND_MONITOR` - Wait and monitor situation
- `EMERGENCY_STOP` - Emergency stop all operations

## Contributing

1. All code changes require human review
2. Follow existing code style
3. Add tests for new features
4. Update documentation

## License

See platform LICENSE file.

## Support

For issues and questions, contact the platform team.
