# Extracted Concepts for Living System Integration

**Source**: User's existing projects (ACIS, Game of Existence, Goal System, Strategic Planning)
**Date**: 2025-10-09
**Purpose**: Apply proven patterns to Living System Architecture

## Key Concepts Extracted

### 1. Initiative Levels (from ACIS)

**Pattern**: Adaptive stimulation of initiative with configurable levels

**Levels**:
- MINIMUM: Strict adherence to instructions
- BALANCED: Moderate initiative with alternatives
- PROACTIVE: Active task expansion and improvements
- INNOVATIVE: Maximum creative freedom

**Application to Living System**:
```python
class InitiativeLevel(Enum):
    CONSERVATIVE = "conservative"  # Stick to proven patterns
    BALANCED = "balanced"          # Try variations of known patterns
    EXPERIMENTAL = "experimental"  # Test new approaches
    CREATIVE = "creative"          # Invent novel solutions
```

**Integration Point**: Wishlist System prioritization
- Conservative when resources low
- Experimental when resources abundant
- Automatic adjustment based on success rate

### 2. Motivation Modeling (from ACIS)

**Pattern**: Internal motivation based on psychological principles

**Components**:
- Autonomy (self-direction)
- Competence (mastery)
- Relatedness (connection)
- Purpose (meaning)

**Application to Living System**:
Already partially implemented in 7 base instincts, but can enhance:

```python
class MotivationEngine:
    """
    Internal motivation driver

    Influences:
    - Which needs in wishlist are prioritized
    - How aggressively to pursue goals
    - When to experiment vs stick to known
    """

    def __init__(self):
        self.autonomy_score = 0.5      # How much control over decisions
        self.competence_score = 0.5    # How capable at tasks
        self.relatedness_score = 0.5   # Connection to other systems/users
        self.purpose_score = 0.5       # Alignment with core values

    def calculate_drive_strength(self, need: Need) -> float:
        """Calculate how motivated to pursue this need"""
        # Autonomy needs are intrinsically motivating
        if need.type == "self_actualization":
            return 0.5 + (0.5 * self.autonomy_score)

        # Competence needs driven by mastery desire
        if need.type == "learning":
            return 0.5 + (0.5 * self.competence_score)

        # Purpose-aligned needs get boost
        if need.alignment_score > 0.8:
            return 0.5 + (0.5 * self.purpose_score)

        return 0.5
```

### 3. Game Loop with Drives (from Game of Existence)

**Pattern**: Dynamic cycle combining existential core, drive engines, and goal system

**Key Insight**: Three-layer architecture
1. **Existential Core**: Who am I? (survival, growth, purpose dimensions)
2. **Drive Engines**: What do I need? (energy management, motivation)
3. **Goal System**: What am I trying to achieve? (concrete objectives)

**Already Implemented in Our System**:
- ✅ Survival Instinct → Existential Core (survival dimension)
- ⏳ Need to add Growth and Purpose dimensions
- ✅ Memory System → Learning capability
- ⏳ Need Goal System

**Enhancement**:
```python
class ExistentialDimensions:
    """
    Three fundamental dimensions of existence
    """

    def __init__(self):
        self.survival_level = 1.0      # 0-1: Health of core functions
        self.growth_level = 0.5        # 0-1: Learning and capability expansion
        self.purpose_level = 0.5       # 0-1: Alignment with core mission

    def get_dominant_dimension(self) -> str:
        """Which dimension needs most attention"""
        dimensions = {
            'survival': self.survival_level,
            'growth': self.growth_level,
            'purpose': self.purpose_level
        }
        # Return dimension with LOWEST score (needs most attention)
        return min(dimensions.items(), key=lambda x: x[1])[0]

    def assess_balance(self) -> float:
        """How balanced are the three dimensions"""
        values = [self.survival_level, self.growth_level, self.purpose_level]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        # Low variance = balanced
        return 1.0 - min(variance, 1.0)
```

### 4. Goal Hierarchy (from Goal System)

**Pattern**: Hierarchical goal management with decomposition and conflict resolution

**Key Features**:
- Parent-child goal relationships
- Priority levels (low, medium, high, critical)
- Dependency tracking
- Conflict detection (circular, resource, deadline)
- Progress tracking

**Application to Living System**:
This is exactly what we need for Wishlist System!

```python
class WishlistItem:
    """
    A need/desire in the system wishlist

    Similar to Goal from existing system but adapted for needs
    """

    def __init__(
        self,
        description: str,
        need_type: str,  # "survival", "growth", "purpose"
        urgency: float,  # 0-1
        resource_cost: ResourceCost,
        parent_id: Optional[str] = None
    ):
        self.id = str(uuid.uuid4())
        self.description = description
        self.need_type = need_type
        self.urgency = urgency
        self.resource_cost = resource_cost
        self.parent_id = parent_id
        self.children: List[str] = []
        self.dependencies: List[str] = []
        self.status = "pending"  # pending, active, completed, obsolete
        self.created_at = time.time()
        self.deadline: Optional[float] = None

    def calculate_priority(self, current_resources: Resources) -> float:
        """
        Calculate priority considering:
        - Urgency
        - Resource availability
        - Dependencies met
        """
        priority = self.urgency

        # Reduce priority if resources unavailable
        if not current_resources.can_afford(self.resource_cost):
            priority *= 0.5

        # Increase priority if deadline approaching
        if self.deadline:
            time_remaining = self.deadline - time.time()
            if time_remaining < 3600:  # Less than 1 hour
                priority *= 1.5

        return min(priority, 1.0)
```

### 5. Conflict Resolution (from Goal System)

**Pattern**: Systematic detection and resolution of conflicts

**Conflict Types**:
1. **Circular Dependencies**: A depends on B, B depends on A
2. **Resource Conflicts**: Multiple high-priority items competing for same resources
3. **Deadline Conflicts**: Dependencies can't complete before deadline

**Application**:
```python
class ConflictResolver:
    """
    Resolve conflicts in Wishlist
    """

    def detect_circular_dependencies(
        self,
        items: Dict[str, WishlistItem]
    ) -> List[Tuple[str, str]]:
        """Find circular dependencies"""
        conflicts = []

        for item_id, item in items.items():
            for dep_id in item.dependencies:
                if dep_id in items:
                    dep_item = items[dep_id]
                    if item_id in dep_item.dependencies:
                        conflicts.append((item_id, dep_id))

        return conflicts

    def resolve_circular_dependency(
        self,
        item1_id: str,
        item2_id: str,
        items: Dict[str, WishlistItem]
    ) -> str:
        """
        Resolve by removing lower-priority dependency
        """
        item1 = items[item1_id]
        item2 = items[item2_id]

        # Remove dependency from lower-urgency item
        if item1.urgency < item2.urgency:
            item1.dependencies.remove(item2_id)
            return f"Removed {item1_id} -> {item2_id}"
        else:
            item2.dependencies.remove(item1_id)
            return f"Removed {item2_id} -> {item1_id}"

    def detect_resource_conflicts(
        self,
        items: Dict[str, WishlistItem],
        current_resources: Resources
    ) -> List[Dict[str, Any]]:
        """Find items that exceed available resources"""
        conflicts = []

        # Get all high-urgency items
        urgent_items = [
            item for item in items.values()
            if item.urgency > 0.8 and item.status == "pending"
        ]

        # Calculate total resource demand
        total_demand = Resources()
        for item in urgent_items:
            total_demand += item.resource_cost

        # Check if demand exceeds supply
        if total_demand > current_resources:
            conflicts.append({
                "type": "resource_shortage",
                "demanded": total_demand.to_dict(),
                "available": current_resources.to_dict(),
                "competing_items": [item.id for item in urgent_items]
            })

        return conflicts
```

### 6. Strategic Planning (from Strategy System)

**Pattern**: Multi-level planning (strategic, tactical, operational)

**Levels**:
- **Strategic**: Long-term vision (months-years)
- **Tactical**: Medium-term plans (weeks-months)
- **Operational**: Short-term execution (hours-days)

**Application to Living System**:

Currently we have:
- Game Loop = Operational (seconds-minutes)
- Survival Instinct = Tactical (minutes-hours)
- Missing: Strategic layer

**Enhancement**:
```python
class StrategyLayer:
    """
    Strategic planning for long-term system evolution

    Complements:
    - Game Loop (operational)
    - Survival Instinct (tactical)
    """

    def __init__(self):
        self.long_term_goals: List[StrategicGoal] = []
        self.evaluation_interval = 86400.0  # 24 hours
        self.last_evaluation = 0.0

    async def evaluate_strategic_position(self) -> Dict[str, Any]:
        """
        Evaluate system's strategic position

        Considers:
        - Capability growth over time
        - Achievement of long-term goals
        - Alignment with core purpose
        - Resource trajectory
        """
        now = time.time()
        if now - self.last_evaluation < self.evaluation_interval:
            return {}

        self.last_evaluation = now

        # Get historical data
        capability_trend = self._analyze_capability_trend()
        resource_trend = self._analyze_resource_trend()
        goal_progress = self._analyze_goal_progress()

        # Assess strategic health
        strategic_health = {
            'capability_growth': capability_trend['growth_rate'],
            'resource_sustainability': resource_trend['sustainability'],
            'goal_achievement_rate': goal_progress['completion_rate'],
            'overall_score': 0.0
        }

        strategic_health['overall_score'] = (
            capability_trend['growth_rate'] * 0.4 +
            resource_trend['sustainability'] * 0.3 +
            goal_progress['completion_rate'] * 0.3
        )

        return strategic_health

    def adjust_strategic_direction(self, health: Dict[str, Any]):
        """
        Adjust long-term direction based on strategic health
        """
        if health['capability_growth'] < 0.3:
            # Not growing enough - prioritize learning
            self._boost_learning_priority()

        if health['resource_sustainability'] < 0.5:
            # Resources declining - focus on efficiency
            self._increase_efficiency_focus()

        if health['goal_achievement_rate'] < 0.4:
            # Goals not being met - reassess feasibility
            self._reassess_goal_feasibility()
```

### 7. Resource-Aware Decision Making

**Pattern**: Decisions weighted by resource costs and availability

**Key Insight**: From user's note about learning costs creating deficit

**Implementation**:
```python
class ResourceAwareDecisionMaker:
    """
    Make decisions considering resource constraints
    """

    def __init__(self, current_resources: Resources):
        self.current_resources = current_resources
        self.resource_history: List[Resources] = []
        self.decision_history: List[Decision] = []

    def should_pursue_action(
        self,
        action: Action,
        expected_benefit: float
    ) -> bool:
        """
        Decide if action is worth pursuing

        Considers:
        - Resource cost vs availability
        - Expected benefit
        - Historical success rate
        - Current resource trajectory
        """
        # Can we afford it?
        if not self.current_resources.can_afford(action.resource_cost):
            return False

        # Calculate cost-benefit ratio
        resource_cost_value = self._calculate_resource_value(action.resource_cost)
        roi = expected_benefit / resource_cost_value if resource_cost_value > 0 else 0

        # Check if ROI meets threshold
        if roi < 1.5:  # Need 50% return to justify
            return False

        # Check resource trajectory
        resource_trend = self._calculate_resource_trend()
        if resource_trend < 0 and action.resource_cost.high():
            # Resources declining and action is expensive - be conservative
            return False

        return True

    def _calculate_resource_value(self, cost: ResourceCost) -> float:
        """Convert resource cost to single value"""
        return (
            cost.cpu_cycles * 0.3 +
            cost.memory_mb * 0.2 +
            cost.disk_io * 0.1 +
            cost.network_bandwidth * 0.1 +
            cost.time_seconds * 0.3
        )

    def _calculate_resource_trend(self) -> float:
        """
        Calculate resource availability trend

        Returns:
            +1.0: Resources increasing rapidly
            0.0: Resources stable
            -1.0: Resources declining rapidly
        """
        if len(self.resource_history) < 2:
            return 0.0

        recent = self.resource_history[-10:]  # Last 10 measurements

        # Simple linear regression
        values = [r.total_value() for r in recent]
        n = len(values)
        x = list(range(n))

        slope = (n * sum(x[i] * values[i] for i in range(n)) - sum(x) * sum(values)) / \
                (n * sum(x[i]**2 for i in range(n)) - sum(x)**2)

        # Normalize slope to -1 to +1 range
        return max(min(slope / 100.0, 1.0), -1.0)
```

## Integration Plan

### Phase 2 Enhancements (Next)

Based on extracted concepts, enhance Phase 2:

#### 1. Add Existential Dimensions
```
File: /intelligent-core/ai-foundation/existential/dimensions.py
- Track survival, growth, purpose levels
- Calculate dominant dimension
- Assess balance
```

#### 2. Enhanced Wishlist System
```
File: /intelligent-core/coordination-center/wishlist/wishlist_system.py
- Hierarchical needs (parent-child)
- Dependency tracking
- Conflict detection and resolution
- Priority calculation with resources
- Deadline management
```

#### 3. Motivation Engine
```
File: /intelligent-core/ai-foundation/motivation/motivation_engine.py
- Autonomy, Competence, Relatedness, Purpose scores
- Drive strength calculation
- Initiative level adaptation
```

#### 4. Strategic Planning Layer
```
File: /intelligent-core/ai-foundation/strategy/strategy_layer.py
- Long-term goal management
- Strategic position evaluation
- Direction adjustment
- Capability/resource trend analysis
```

#### 5. Resource-Aware Decision Making
```
File: /intelligent-core/coordination-center/decision/resource_aware.py
- ROI calculation
- Resource trend analysis
- Should-pursue logic
- Cost-benefit evaluation
```

### Quick Wins (Can Implement Now)

1. **Add Existential Dimensions to Survival Instinct**
   - Extend to track growth and purpose in addition to survival
   - 50 lines of code

2. **Add Conflict Detection to Memory System**
   - Detect when patterns contradict
   - 100 lines of code

3. **Add Initiative Levels to Game Loop**
   - Conservative/Balanced/Experimental/Creative modes
   - Adjust based on success rate
   - 75 lines of code

4. **Add Resource Trend Tracking**
   - Simple moving average of resource usage
   - Predict resource availability
   - 50 lines of code

## Code Examples to Reuse

### Goal Hierarchy Pattern
```python
# From user's Goal System - proven pattern
class HierarchicalItem:
    def __init__(self, parent_id: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.parent_id = parent_id
        self.children: List[str] = []

    def add_child(self, child_id: str):
        self.children.append(child_id)

    def remove_child(self, child_id: str):
        if child_id in self.children:
            self.children.remove(child_id)
```

### Conflict Resolution Pattern
```python
# From user's Goal System - proven pattern
def detect_conflicts(items: Dict[str, Item]) -> List[Conflict]:
    conflicts = []

    # Circular dependencies
    for item in items.values():
        for dep_id in item.dependencies:
            if dep_id in items and item.id in items[dep_id].dependencies:
                conflicts.append(Conflict("circular", [item.id, dep_id]))

    return conflicts

def resolve_conflict(conflict: Conflict, items: Dict[str, Item]):
    if conflict.type == "circular":
        # Remove lower-priority dependency
        item1, item2 = conflict.involved_items
        if items[item1].priority < items[item2].priority:
            items[item1].dependencies.remove(item2)
        else:
            items[item2].dependencies.remove(item1)
```

### Motivation Scoring Pattern
```python
# From ACIS - proven pattern
def calculate_motivation_score(factors: Dict[str, float]) -> float:
    """
    Combine multiple motivation factors
    """
    weights = {
        'autonomy': 0.3,
        'competence': 0.25,
        'relatedness': 0.15,
        'purpose': 0.3
    }

    score = sum(factors[k] * weights[k] for k in weights if k in factors)
    return min(max(score, 0.0), 1.0)
```

## Summary

Extracted 7 key patterns from user's existing work:

1. **Initiative Levels** → Apply to Wishlist prioritization
2. **Motivation Modeling** → Add to drive system
3. **Game Loop with Drives** → Enhance with 3 dimensions
4. **Goal Hierarchy** → Use for Wishlist structure
5. **Conflict Resolution** → Add to Wishlist and Memory
6. **Strategic Planning** → Add strategic layer above Survival
7. **Resource-Aware Decisions** → Make all decisions resource-conscious

All patterns are **proven in production** in user's systems. Can confidently reuse.

Next step: Implement enhancements to Phase 2 using these patterns.
