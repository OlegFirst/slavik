# Simulation Engines & Modeling Tools

## Available Engines

### 1. **SimPy** - Process-Based Discrete Event Simulation
**Status:** ✅ Planned
**Use Cases:**
- Resource modeling (queues, servers, resources)
- Process flows
- Service systems
- Manufacturing simulations

**Features:**
- Python-based
- Easy to learn
- Good for resource contention modeling
- Supports priorities and interruptions

**When to Use:**
- Modeling business processes
- Resource allocation problems
- Queue analysis
- Service time optimization

---

### 2. **JaamSim** - Industrial-Grade 3D Simulation
**Status:** ✅ Planned (Already have code to refactor)
**Use Cases:**
- Complex industrial processes
- Supply chain modeling
- Manufacturing systems
- Hospital workflows

**Features:**
- 3D visualization
- Drag-and-drop model building
- Statistical analysis
- Comprehensive reporting

**When to Use:**
- Need visual representation
- Complex workflows
- Stakeholder presentations
- Detailed process analysis

---

### 3. **Monte Carlo** - Statistical Simulation
**Status:** ✅ Planned
**Use Cases:**
- Risk analysis
- Financial modeling
- Probability estimation
- Uncertainty quantification

**Features:**
- Random sampling
- Statistical distributions
- Confidence intervals
- Sensitivity analysis

**When to Use:**
- Dealing with uncertainty
- Risk assessment
- Portfolio optimization
- Decision under uncertainty

---

### 4. **What-If Analysis** - Simple Scenario Testing
**Status:** ✅ Planned
**Use Cases:**
- Quick impact analysis
- Decision support
- Scenario comparison
- Strategy evaluation

**Features:**
- Fast execution
- Simple configuration
- Easy to understand
- Multiple scenario comparison

**When to Use:**
- Need quick answers
- Comparing alternatives
- Strategic planning
- Sensitivity testing

---

### 5. **Workflow Engine** - Platform Testing
**Status:** ✅ Planned
**Use Cases:**
- Internal platform testing
- Workflow validation
- Integration testing
- System behavior verification

**Features:**
- Real platform integration
- Actual workflow execution
- Live data
- True end-to-end testing

**When to Use:**
- Testing platform features
- Validating workflows
- Integration testing
- Real system behavior

---

## Modeling Approaches

### 1. Discrete Event Simulation (DES)
**Description:** Models system as sequence of discrete events
**Tools:** SimPy, JaamSim
**Best For:**
- Processes with distinct events
- Queuing systems
- Manufacturing
- Logistics

### 2. System Dynamics
**Description:** Models feedback loops and accumulations
**Tools:** Future integration (Vensim, Stella)
**Best For:**
- Policy analysis
- Long-term trends
- Feedback systems
- Strategic planning

### 3. Agent-Based Modeling (ABM)
**Description:** Individual agents with behaviors
**Tools:** Future integration (Mesa, NetLogo)
**Best For:**
- Social systems
- Emergent behavior
- Decentralized systems
- Complex adaptive systems

### 4. Monte Carlo Simulation
**Description:** Random sampling from probability distributions
**Tools:** Monte Carlo engine
**Best For:**
- Risk analysis
- Uncertainty quantification
- Financial modeling
- Probability estimation

### 5. What-If Analysis
**Description:** Scenario testing with parameter variations
**Tools:** What-If engine
**Best For:**
- Quick comparisons
- Strategic alternatives
- Sensitivity analysis
- Decision support

---

## Engine Selection Guide

### By Task Type

**Business Process Analysis:**
- Primary: SimPy
- Alternative: JaamSim (if visualization needed)

**Disaster Recovery / BCM:**
- Primary: What-If
- Alternative: Monte Carlo (for probabilistic analysis)

**Supply Chain:**
- Primary: JaamSim
- Alternative: SimPy

**Cyber Security:**
- Primary: What-If
- Alternative: Monte Carlo (for risk analysis)

**Pandemic Response:**
- Primary: Agent-Based (future)
- Alternative: System Dynamics (future)

**Platform Testing:**
- Primary: Workflow Engine
- Alternative: None (specialized)

### By Complexity Level

**Low Complexity (1-2):**
- What-If Analysis
- Simple Monte Carlo

**Medium Complexity (3):**
- SimPy
- Monte Carlo with correlations

**High Complexity (4-5):**
- JaamSim
- Advanced SimPy models
- Workflow Engine (real platform)

### By Required Output

**Need Visualization:**
- JaamSim (3D)
- SimPy with animation

**Need Statistical Analysis:**
- Monte Carlo
- SimPy with statistical output

**Need Quick Answer:**
- What-If
- Simple Monte Carlo

**Need Detailed Logs:**
- SimPy
- Workflow Engine

---

## Implementation Roadmap

### Phase 1 (MVP) - CURRENT
- ✅ Engine interface design
- ⏳ SimPy wrapper
- ⏳ What-If engine
- ⏳ Monte Carlo engine

### Phase 2 (Enhanced)
- ⏳ JaamSim refactoring
- ⏳ Workflow Engine integration
- ⏳ Advanced visualization

### Phase 3 (Advanced)
- ⏳ System Dynamics integration
- ⏳ Agent-Based Modeling
- ⏳ Custom engine support

---

## Theory of Change Integration

All engines should support Theory of Change modeling:

**Inputs → Activities → Outputs → Outcomes → Impact**

Each engine can model different parts:
- **What-If:** Quick pathway testing
- **Monte Carlo:** Probability of outcomes
- **SimPy:** Detailed activity modeling
- **JaamSim:** Complete pathway visualization
- **ABM:** Emergent outcomes from agent behavior

See: `/catalogs/theory-of-change/` for detailed ToC templates

---

## Technical Architecture

### Engine Interface

All engines implement common interface:

```python
class SimulationEngine(ABC):
    @abstractmethod
    async def initialize(self, config: EngineConfig) -> bool:
        pass

    @abstractmethod
    async def run(self, scenario: Scenario) -> SimulationResult:
        pass

    @abstractmethod
    async def pause(self) -> bool:
        pass

    @abstractmethod
    async def resume(self) -> bool:
        pass

    @abstractmethod
    async def stop(self) -> bool:
        pass

    @abstractmethod
    async def get_status(self) -> Dict:
        pass
```

### Engine Manager

Orchestrates engine lifecycle:
- Engine selection
- Initialization
- Execution
- Monitoring
- Cleanup

---

## Configuration Examples

### SimPy Configuration
```yaml
engine: simpy
parameters:
  duration: 3600
  resources:
    - name: "servers"
      capacity: 5
  processes:
    - name: "customer_service"
      arrival_rate: 10
```

### Monte Carlo Configuration
```yaml
engine: monte_carlo
parameters:
  iterations: 10000
  distributions:
    - variable: "recovery_time"
      type: "normal"
      mean: 240
      std: 60
  confidence_level: 0.95
```

### What-If Configuration
```yaml
engine: what_if
parameters:
  scenarios:
    - name: "best_case"
      recovery_time: 120
    - name: "worst_case"
      recovery_time: 480
  baseline: "expected_case"
```

---

## Performance Considerations

### Engine Performance Profiles

**Fastest:**
1. What-If (< 1 second)
2. Simple Monte Carlo (< 10 seconds)
3. SimPy (seconds to minutes)

**Moderate:**
4. Complex Monte Carlo (minutes)
5. JaamSim (minutes)

**Slowest:**
6. Workflow Engine (depends on real workflows)

### Optimization Tips

1. **Use appropriate engine for task**
2. **Limit simulation duration**
3. **Reduce number of entities/events**
4. **Use sampling for large populations**
5. **Cache similar scenarios**

---

## Resources & Documentation

### SimPy
- Documentation: https://simpy.readthedocs.io/
- Examples: https://simpy.readthedocs.io/en/latest/examples/

### JaamSim
- Website: https://jaamsim.com/
- Documentation: https://jaamsim.com/docs/

### Monte Carlo
- Theory: https://en.wikipedia.org/wiki/Monte_Carlo_method
- Applications: Risk analysis, Finance, Engineering

### Theory of Change
- See: `/catalogs/theory-of-change/README.md`

---

## Future Enhancements

### Planned
- [ ] Hybrid simulations (multiple engines)
- [ ] Real-time collaborative simulation
- [ ] VR/AR visualization
- [ ] ML-powered parameter optimization
- [ ] Quantum simulation integration (long-term)

### Research Areas
- Digital Twin synchronization
- Federated simulation across organizations
- Blockchain-based result verification
- AI agents as simulation participants

---

*Last Updated: 2025-10-12*
*Simulation & Modeling Service*
