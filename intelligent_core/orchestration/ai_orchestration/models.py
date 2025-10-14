"""
AI Orchestrator Data Models
============================

Core data structures for decision-making system.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum


class PriorityLevel(Enum):
    """Priority levels for decisions."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ActionType(Enum):
    """Types of actions the orchestrator can take."""
    AUTO_RESOLVE = "auto_resolve"
    DELEGATE = "delegate"
    ESCALATE_HUMAN = "escalate_to_human"
    WAIT_AND_MONITOR = "wait_and_monitor"
    EMERGENCY_STOP = "emergency_stop"


class MemoryType(Enum):
    """Types of memory in the system."""
    WORKING = "working"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    PROCEDURAL = "procedural"


@dataclass
class Priority:
    """
    Priority assessment for a situation.

    Attributes:
        level: Priority level
        score: Numeric score (0-100)
        reasoning: Breakdown of priority factors
    """
    level: PriorityLevel
    score: float
    reasoning: Dict[str, float] = field(default_factory=dict)

    @classmethod
    def from_score(cls, score: float, reasoning: Dict[str, float]) -> 'Priority':
        """Create priority from numeric score."""
        if score >= 90:
            level = PriorityLevel.CRITICAL
        elif score >= 70:
            level = PriorityLevel.HIGH
        elif score >= 40:
            level = PriorityLevel.MEDIUM
        else:
            level = PriorityLevel.LOW

        return cls(level=level, score=score, reasoning=reasoning)


@dataclass
class Strategy:
    """
    A proposed strategy for handling a situation.

    Attributes:
        action: What to do
        rationale: Why this strategy
        confidence: Confidence level (0-1)
        source: Where strategy came from
        learned_from: Cases this was learned from
    """
    action: str
    rationale: str
    confidence: float
    source: str  # 'procedural_memory', 'case_library', 'ai_generated'
    learned_from: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Decision:
    """
    Final decision made by orchestrator.

    Attributes:
        action: Action type
        rationale: Why this decision
        priority: Priority level
        confidence: Confidence (0-1)
        strategies_considered: All strategies that were evaluated
        governance_approved: Whether governance validated
        safety_approved: Whether safety checks passed
        learned_from: Cases used to inform decision
    """
    action: ActionType
    rationale: str
    priority: PriorityLevel
    confidence: float = 0.0
    strategies_considered: List[Strategy] = field(default_factory=list)
    governance_approved: bool = False
    safety_approved: bool = False
    learned_from: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'action': self.action.value,
            'rationale': self.rationale,
            'priority': self.priority.value,
            'confidence': self.confidence,
            'governance_approved': self.governance_approved,
            'safety_approved': self.safety_approved,
            'learned_from': self.learned_from,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class FullContext:
    """
    Complete context for decision-making.

    Aggregates information from all sources:
    - Current platform state
    - Active workflows
    - Recent events
    - Historical similar situations
    - Industry trends
    - Regulatory context
    - Predictions
    - Governance constraints
    """
    # Current state
    platform_state: Dict[str, Any]
    workflows: List[Dict[str, Any]]

    # Temporal context
    recent_events: List[Dict[str, Any]]
    similar_situations: List[Dict[str, Any]]

    # External context
    industry_trends: List[Dict[str, Any]] = field(default_factory=list)
    regulatory_changes: List[Dict[str, Any]] = field(default_factory=list)

    # Intelligence
    predictions: Dict[str, Any] = field(default_factory=dict)

    # Constraints
    governance_rules: List[Dict[str, Any]] = field(default_factory=list)

    # Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SafetyConcern:
    """A safety concern identified by safety monitor."""
    type: str  # 'constitution_violation', 'infinite_loop', 'hallucination', etc.
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    recommended_action: str = "escalate_to_human"


@dataclass
class SafetyResult:
    """
    Result of safety validation.

    Attributes:
        safe: Whether action is safe to execute
        concerns: List of identified concerns
        constitution_check: Constitution validation result
        loop_check: Loop detection result
        hallucination_check: Hallucination detection result
    """
    safe: bool
    concerns: List[SafetyConcern] = field(default_factory=list)
    constitution_check: bool = True
    loop_check: bool = True
    hallucination_check: bool = True

    def has_critical_concerns(self) -> bool:
        """Check if any critical concerns exist."""
        return any(c.severity == 'critical' for c in self.concerns)

    def get_blocking_concerns(self) -> List[SafetyConcern]:
        """Get concerns that block execution."""
        return [c for c in self.concerns if c.severity in ['critical', 'high']]


@dataclass
class Memory:
    """A memory item in the system."""
    id: str
    type: MemoryType
    content: Dict[str, Any]
    timestamp: datetime
    importance: float  # 0-1
    access_count: int = 0
    last_accessed: Optional[datetime] = None


@dataclass
class Loop:
    """Detected loop pattern."""
    pattern: str
    repeat_count: int
    duration: float  # seconds
    actions: List[str]
    suggestion: str = "break_loop_or_escalate"


@dataclass
class HallucinationScore:
    """Result of hallucination detection."""
    confidence: float  # 0-1, higher = more likely hallucinating
    evidence: List[Dict[str, Any]] = field(default_factory=list)

    def is_hallucinating(self, threshold: float = 0.7) -> bool:
        """Check if confidence exceeds threshold."""
        return self.confidence >= threshold
