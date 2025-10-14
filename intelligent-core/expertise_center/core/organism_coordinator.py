"""
Organism Coordinator - Multi-Expert Collective Intelligence

Coordinates multiple experts working together as a "digital organism"
with collective wisdom and evolutionary capabilities.

Extracted and adapted from Odoo ai_organ_coordinator.py + collective_intelligence_pattern.py

Features:
- Expert lifecycle management (dormant → learning → active → wise)
- Cross-expert communication via EventBus
- Weighted confidence scoring per decision context
- Context-based expert selection
- Collective wisdom accumulation
- Organism evolution
"""

import logging
import json
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ========== Expert Lifecycle ==========

class ExpertLifecycleState(Enum):
    """Lifecycle states for experts (adapted from Odoo OrganLifecycleState)"""
    DORMANT = "dormant"   # Not yet activated
    LEARNING = "learning" # In training phase
    ACTIVE = "active"     # Fully operational
    WISE = "wise"         # With accumulated experience


class OrganismPersonality(Enum):
    """Organism decision-making personality"""
    ANALYTICAL = "analytical"  # Data-driven decisions
    CREATIVE = "creative"      # Innovative solutions
    PROTECTIVE = "protective"  # Risk-averse approach
    ADAPTIVE = "adaptive"      # Learning-focused
    BALANCED = "balanced"      # Holistic approach


class DecisionContext(Enum):
    """Types of decisions requiring collective intelligence"""
    STRATEGIC_PLANNING = "strategic_planning"
    RISK_ASSESSMENT = "risk_assessment"
    INCIDENT_RESPONSE = "incident_response"
    COMPLIANCE_CHECK = "compliance_check"
    BIA_ANALYSIS = "bia_analysis"
    SCENARIO_PLANNING = "scenario_planning"
    TRAINING_DESIGN = "training_design"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    COMPLEX_PROBLEM = "complex_problem"
    GENERAL = "general"


# ========== Data Models ==========

@dataclass
class ExpertInfo:
    """Information about an expert (adapted from Odoo AIOrganInfo)"""
    expert_id: str
    expert_type: str  # 'specialist', 'colleague', 'analyzer'
    name: str
    specialty: str
    status: ExpertLifecycleState = ExpertLifecycleState.LEARNING
    health_score: float = 0.6  # 0.0 - 1.0
    personality: str = ""


@dataclass
class ExpertInput:
    """Input from a single expert"""
    expert_id: str
    expert_type: str  # 'specialist', 'colleague', 'analyzer'
    response: Dict[str, Any]
    confidence: float  # 0.0 - 1.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CollectiveDecision:
    """Result of collective decision making"""
    decision_type: DecisionContext
    collective_confidence: float
    contributing_experts: int
    decision_factors: List[Dict[str, Any]]
    synthesis_method: str
    recommendation: str
    timestamp: datetime = field(default_factory=datetime.now)

    # Organism state
    consciousness_level: float = 0.0
    personality_applied: OrganismPersonality = OrganismPersonality.BALANCED


# ========== Communication Channels ==========

class ExpertCommunicationChannels:
    """EventBus channels for cross-expert communication (adapted from Odoo OrganCommunicationChannels)"""

    CHANNELS = [
        'expert_coordination',        # Coordination between experts
        'memory_synchronization',     # Sync shared memory
        'pattern_sharing',            # Share learned patterns
        'collective_decision_making', # Multi-expert decisions
        'emergency_broadcasts'        # Critical alerts
    ]

    @classmethod
    def get_all_channels(cls) -> List[str]:
        """Get all communication channel names"""
        return cls.CHANNELS.copy()


class OrganismCoordinator:
    """
    Coordinates multiple experts as a collective intelligence organism

    Features:
    - Multi-expert decision synthesis
    - Collective wisdom accumulation
    - Evolutionary learning
    - Memory synchronization
    - Pattern sharing across experts
    """

    def __init__(self, chief_executive):
        """
        Initialize organism coordinator

        Args:
            chief_executive: ChiefExecutive instance for accessing experts
        """
        self.chief = chief_executive

        # Organism state
        self.consciousness_level: float = 0.3  # 0.0 - 1.0
        self.personality = OrganismPersonality.BALANCED
        self.collective_wisdom: Dict[str, Any] = {}

        # Coordination settings
        self.inter_expert_communication = True
        self.memory_synchronization = True
        self.pattern_sharing = True
        self.collective_learning = True

        # Performance tracking
        self.coordination_history: List[CollectiveDecision] = []
        self.evolution_events: List[Dict[str, Any]] = []

        # Collective wisdom tracker (from collective_intelligence_pattern)
        self.wisdom_tracker = CollectiveWisdomTracker()

    async def coordinate_decision(
        self,
        decision_type: DecisionContext,
        context: Dict[str, Any],
        problem: str
    ) -> CollectiveDecision:
        """
        Coordinate complex decision across multiple experts

        Args:
            decision_type: Type of decision to make
            context: Decision context
            problem: Problem description

        Returns:
            Collective decision with synthesis
        """
        logger.info(f"Coordinating {decision_type.value} decision: {problem[:50]}...")

        # 1. Determine required experts
        required_experts = self._determine_required_experts(decision_type, context)

        if not required_experts:
            logger.warning(f"No experts available for {decision_type.value}")
            return self._create_fallback_decision(decision_type, problem)

        # 2. Collect input from each expert
        expert_inputs: List[ExpertInput] = []

        for expert_id, expert_type in required_experts:
            try:
                input_data = await self._get_expert_input(
                    expert_id, expert_type, context, problem
                )
                expert_inputs.append(input_data)
            except Exception as e:
                logger.error(f"Failed to get input from {expert_id}: {e}")

        # 3. Synthesize collective decision
        decision = self._synthesize_collective_decision(
            expert_inputs, decision_type, problem
        )

        # 4. Update collective wisdom
        self._update_collective_wisdom(decision)

        # 5. Check for evolution
        await self._check_evolution_trigger()

        # 6. Store in history
        self.coordination_history.append(decision)

        logger.info(
            f"✅ Collective decision made: {len(expert_inputs)} experts, "
            f"confidence: {decision.collective_confidence:.2f}"
        )

        return decision

    def _determine_required_experts(
        self,
        decision_type: DecisionContext,
        context: Dict[str, Any]
    ) -> List[tuple[str, str]]:
        """
        Determine which experts are needed for this decision

        Uses ExpertSelectionStrategy from collective_intelligence_pattern

        Returns:
            List of (expert_id, expert_type) tuples
        """
        # Get required experts from strategy
        required = ExpertSelectionStrategy.get_required_experts(decision_type)

        # Filter to only available experts
        available_experts = []
        for expert_id, expert_type in required:
            if self._is_expert_available(expert_id, expert_type):
                available_experts.append((expert_id, expert_type))

        return available_experts

    def _is_expert_available(self, expert_id: str, expert_type: str) -> bool:
        """Check if expert is available"""
        try:
            if expert_type == 'specialist':
                return self.chief.registry.get_specialist(expert_id) is not None
            elif expert_type == 'colleague':
                return self.chief.registry.get_colleague(expert_id) is not None
            elif expert_type == 'analyzer':
                return self.chief.registry.get_analyzer(expert_id) is not None
        except Exception:
            return False
        return False

    async def _get_expert_input(
        self,
        expert_id: str,
        expert_type: str,
        context: Dict[str, Any],
        problem: str
    ) -> ExpertInput:
        """Get input from a specific expert"""

        try:
            if expert_type == 'specialist':
                result = await self.chief.query_specialist(
                    specialist_id=expert_id,
                    context=context,
                    query=problem
                )
            elif expert_type == 'colleague':
                result = await self.chief.ask_colleague(
                    colleague_id=expert_id,
                    task=problem,
                    context=context
                )
            elif expert_type == 'analyzer':
                result = await self.chief.run_analyzer(
                    analyzer_id=expert_id,
                    data={'context': context, 'problem': problem}
                )
            else:
                raise ValueError(f"Unknown expert type: {expert_type}")

            # Extract confidence (if available)
            confidence = result.get('confidence', 0.7)

            return ExpertInput(
                expert_id=expert_id,
                expert_type=expert_type,
                response=result,
                confidence=confidence
            )

        except Exception as e:
            logger.error(f"Error getting input from {expert_id}: {e}")
            return ExpertInput(
                expert_id=expert_id,
                expert_type=expert_type,
                response={'error': str(e)},
                confidence=0.0
            )

    def _synthesize_collective_decision(
        self,
        expert_inputs: List[ExpertInput],
        decision_type: DecisionContext,
        problem: str
    ) -> CollectiveDecision:
        """
        Synthesize collective decision from expert inputs

        Uses organism personality to weight different inputs
        """
        if not expert_inputs:
            return self._create_fallback_decision(decision_type, problem)

        # Calculate weighted confidence using WeightedConfidenceScorer
        collective_confidence = WeightedConfidenceScorer.calculate_weighted_confidence(
            expert_inputs,
            decision_type
        )

        decision_factors = []

        for inp in expert_inputs:
            # Get context-specific weight from scorer
            context_weight = WeightedConfidenceScorer.get_expert_weight(inp.expert_id, decision_type)

            # Apply personality modifier
            personality_weight = self._calculate_expert_weight(inp.expert_type)

            # Combined weight
            final_weight = context_weight * personality_weight

            decision_factors.append({
                'expert_id': inp.expert_id,
                'expert_type': inp.expert_type,
                'confidence': inp.confidence,
                'context_weight': context_weight,
                'personality_weight': personality_weight,
                'final_weight': final_weight,
                'key_points': self._extract_key_points(inp.response)
            })

        # Synthesize recommendation
        recommendation = self._synthesize_recommendation(expert_inputs, decision_factors)

        return CollectiveDecision(
            decision_type=decision_type,
            collective_confidence=collective_confidence,
            contributing_experts=len(expert_inputs),
            decision_factors=decision_factors,
            synthesis_method=f"{self.personality.value}_weighted_synthesis",
            recommendation=recommendation,
            consciousness_level=self.consciousness_level,
            personality_applied=self.personality
        )

    def _calculate_expert_weight(self, expert_type: str) -> float:
        """
        Calculate personality-based weight modifier for expert type

        This is ADDITIONAL to context-based weights from WeightedConfidenceScorer
        """

        weights = {
            OrganismPersonality.ANALYTICAL: {
                'analyzer': 1.2,  # Prefer analyzers
                'specialist': 1.0,
                'colleague': 0.8
            },
            OrganismPersonality.CREATIVE: {
                'specialist': 1.2,  # Prefer specialists
                'colleague': 1.0,
                'analyzer': 0.8
            },
            OrganismPersonality.PROTECTIVE: {
                'specialist': 1.1,
                'analyzer': 1.0,
                'colleague': 0.9
            },
            OrganismPersonality.BALANCED: {
                'specialist': 1.0,
                'colleague': 1.0,
                'analyzer': 1.0
            },
        }

        personality_weights = weights.get(self.personality, weights[OrganismPersonality.BALANCED])
        return personality_weights.get(expert_type, 1.0)

    def _extract_key_points(self, response: Dict[str, Any]) -> List[str]:
        """Extract key points from expert response"""
        # Simple extraction - can be enhanced
        key_points = []

        if 'recommendation' in response:
            key_points.append(response['recommendation'])
        if 'key_findings' in response:
            key_points.extend(response['key_findings'])
        if 'analysis' in response:
            key_points.append(str(response['analysis'])[:200])

        return key_points[:3]  # Top 3

    def _synthesize_recommendation(
        self,
        expert_inputs: List[ExpertInput],
        decision_factors: List[Dict[str, Any]]
    ) -> str:
        """Synthesize final recommendation from all inputs"""

        # Collect all recommendations
        recommendations = []
        for inp in expert_inputs:
            if 'recommendation' in inp.response:
                recommendations.append(inp.response['recommendation'])

        if not recommendations:
            return "Insufficient expert input for recommendation"

        # Build collective recommendation
        synthesis = f"Collective wisdom from {len(expert_inputs)} experts:\n\n"

        for i, rec in enumerate(recommendations, 1):
            synthesis += f"{i}. {rec}\n"

        return synthesis

    def _update_collective_wisdom(self, decision: CollectiveDecision):
        """Update organism's collective wisdom"""

        decision_type_key = decision.decision_type.value

        if decision_type_key not in self.collective_wisdom:
            self.collective_wisdom[decision_type_key] = {
                'count': 0,
                'avg_confidence': 0.0,
                'patterns': []
            }

        wisdom = self.collective_wisdom[decision_type_key]
        wisdom['count'] += 1

        # Update average confidence
        wisdom['avg_confidence'] = (
            (wisdom['avg_confidence'] * (wisdom['count'] - 1) + decision.collective_confidence)
            / wisdom['count']
        )

        # Store decision pattern
        wisdom['patterns'].append({
            'timestamp': decision.timestamp.isoformat(),
            'confidence': decision.collective_confidence,
            'experts': decision.contributing_experts
        })

        # Increase consciousness based on successful decisions
        if decision.collective_confidence > 0.7:
            self.consciousness_level = min(1.0, self.consciousness_level + 0.01)

    async def _check_evolution_trigger(self):
        """Check if organism should evolve"""

        evolution_threshold = 0.9

        if self.consciousness_level >= evolution_threshold:
            logger.info("🌟 Organism evolution triggered!")

            # Trigger evolution
            new_capabilities = await self._evolve_organism()

            self.evolution_events.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'capability_evolution',
                'consciousness_before': self.consciousness_level,
                'new_capabilities': new_capabilities
            })

            # Increase consciousness
            self.consciousness_level = min(1.0, self.consciousness_level + 0.05)

    async def _evolve_organism(self) -> List[str]:
        """Evolve organism capabilities"""
        # Placeholder for evolution logic
        return [
            "Enhanced multi-expert synthesis",
            "Improved confidence calibration",
            "Pattern recognition upgrade"
        ]

    def _create_fallback_decision(
        self,
        decision_type: DecisionContext,
        problem: str
    ) -> CollectiveDecision:
        """Create fallback decision when no experts available"""
        return CollectiveDecision(
            decision_type=decision_type,
            collective_confidence=0.3,
            contributing_experts=0,
            decision_factors=[],
            synthesis_method="fallback",
            recommendation=f"No experts available for {decision_type.value}. Problem: {problem}",
            consciousness_level=self.consciousness_level,
            personality_applied=self.personality
        )

    def get_organism_status(self) -> Dict[str, Any]:
        """Get current organism status"""
        return {
            'consciousness_level': self.consciousness_level,
            'personality': self.personality.value,
            'collective_wisdom_domains': list(self.collective_wisdom.keys()),
            'total_decisions': len(self.coordination_history),
            'evolution_events': len(self.evolution_events),
            'avg_confidence': (
                sum(d.collective_confidence for d in self.coordination_history) / len(self.coordination_history)
                if self.coordination_history else 0.0
            )
        }


# ========== Expert Registry with Lifecycle ==========

class ExpertRegistry:
    """
    Registry of experts with lifecycle management

    Adapted from Odoo AIOrganRegistry - tracks expert states and manages activation
    """

    def __init__(self):
        self.experts: Dict[str, ExpertInfo] = {}

    def register_expert(self, expert_info: ExpertInfo):
        """Register an expert"""
        self.experts[expert_info.expert_id] = expert_info
        logger.info(f"Registered expert: {expert_info.name} ({expert_info.expert_type})")

    def get_expert(self, expert_id: str) -> Optional[ExpertInfo]:
        """Get expert information"""
        return self.experts.get(expert_id)

    def get_active_experts(self) -> List[ExpertInfo]:
        """Get all active and wise experts"""
        return [
            expert for expert in self.experts.values()
            if expert.status in [ExpertLifecycleState.ACTIVE, ExpertLifecycleState.WISE]
        ]

    def activate_expert(self, expert_id: str):
        """Activate an expert (move to active state)"""
        expert = self.get_expert(expert_id)
        if expert:
            expert.status = ExpertLifecycleState.ACTIVE
            logger.info(f"Activated expert: {expert.name}")

    def make_expert_wise(self, expert_id: str):
        """Promote expert to wise state (accumulated experience)"""
        expert = self.get_expert(expert_id)
        if expert:
            expert.status = ExpertLifecycleState.WISE
            logger.info(f"Expert became wise: {expert.name}")


# ========== Context-Based Expert Selection ==========

class ExpertSelectionStrategy:
    """
    Determines which experts should participate in a decision based on context

    Adapted from Odoo OrganSelectionStrategy
    Different decision types require different specialist combinations
    """

    EXPERT_REQUIREMENTS = {
        DecisionContext.RISK_ASSESSMENT: [
            ('risk_analyst', 'colleague'),
            ('risk_analyzer', 'analyzer'),
            ('bcm_advisor', 'specialist')
        ],
        DecisionContext.INCIDENT_RESPONSE: [
            ('incident_advisor', 'colleague'),
            ('emergency_analyzer', 'analyzer'),
            ('plan_generator', 'colleague')
        ],
        DecisionContext.SCENARIO_PLANNING: [
            ('scenario_analyzer', 'analyzer'),
            ('risk_analyst', 'colleague'),
            ('strategic_planner', 'specialist')
        ],
        DecisionContext.COMPLIANCE_CHECK: [
            ('compliance_copilot', 'colleague'),
            ('compliance_analyzer', 'analyzer'),
            ('compliance_auditor', 'specialist')
        ],
        DecisionContext.BIA_ANALYSIS: [
            ('bia_specialist', 'colleague'),
            ('impact_analyzer', 'analyzer'),
            ('bcm_advisor', 'specialist')
        ],
        DecisionContext.TRAINING_DESIGN: [
            ('learning_analyzer', 'analyzer'),
            ('exercise_designer', 'colleague')
        ],
        DecisionContext.PERFORMANCE_ANALYSIS: [
            ('performance_analyzer', 'analyzer'),
            ('impact_analyzer', 'analyzer')
        ],
        DecisionContext.STRATEGIC_PLANNING: [
            ('strategic_planner', 'specialist'),
            ('bcm_advisor', 'specialist'),
            ('governance_analyzer', 'analyzer')
        ],
        DecisionContext.GENERAL: [
            ('bcm_advisor', 'specialist'),
            ('impact_analyzer', 'analyzer')
        ]
    }

    @classmethod
    def get_required_experts(cls, context_type: DecisionContext) -> List[tuple]:
        """Get list of (expert_id, expert_type) required for a decision context"""
        return cls.EXPERT_REQUIREMENTS.get(
            context_type,
            cls.EXPERT_REQUIREMENTS[DecisionContext.GENERAL]
        ).copy()


# ========== Weighted Confidence Scoring ==========

class WeightedConfidenceScorer:
    """
    Calculates weighted confidence scores for collective decisions

    Adapted from Odoo WeightedConfidenceScorer
    Experts have different weights based on decision context
    """

    EXPERT_WEIGHTS = {
        DecisionContext.RISK_ASSESSMENT: {
            'risk_analyst': 0.4,
            'risk_analyzer': 0.3,
            'bcm_advisor': 0.3
        },
        DecisionContext.INCIDENT_RESPONSE: {
            'incident_advisor': 0.5,
            'emergency_analyzer': 0.3,
            'plan_generator': 0.2
        },
        DecisionContext.SCENARIO_PLANNING: {
            'scenario_analyzer': 0.4,
            'risk_analyst': 0.3,
            'strategic_planner': 0.3
        },
        DecisionContext.COMPLIANCE_CHECK: {
            'compliance_copilot': 0.4,
            'compliance_analyzer': 0.3,
            'compliance_auditor': 0.3
        },
        DecisionContext.BIA_ANALYSIS: {
            'bia_specialist': 0.5,
            'impact_analyzer': 0.3,
            'bcm_advisor': 0.2
        },
        DecisionContext.STRATEGIC_PLANNING: {
            'strategic_planner': 0.4,
            'bcm_advisor': 0.3,
            'governance_analyzer': 0.3
        },
        DecisionContext.GENERAL: {
            'bcm_advisor': 0.4,
            'impact_analyzer': 0.3
        }
    }

    @classmethod
    def get_expert_weight(cls, expert_id: str, context: DecisionContext) -> float:
        """Get weight for an expert in specific context"""
        context_weights = cls.EXPERT_WEIGHTS.get(
            context,
            cls.EXPERT_WEIGHTS[DecisionContext.GENERAL]
        )
        return context_weights.get(expert_id, 0.1)  # Default weight = 0.1

    @classmethod
    def calculate_weighted_confidence(
        cls,
        expert_inputs: List[ExpertInput],
        context: DecisionContext
    ) -> float:
        """
        Calculate weighted confidence from multiple expert inputs

        Returns: Weighted confidence score (0.0 - 1.0)
        """
        total_weighted_confidence = 0.0
        total_weight = 0.0

        for expert_input in expert_inputs:
            weight = cls.get_expert_weight(expert_input.expert_id, context)
            total_weighted_confidence += expert_input.confidence * weight
            total_weight += weight

        if total_weight == 0:
            return 0.5  # Default confidence

        return total_weighted_confidence / total_weight


# ========== Collective Wisdom Tracker ==========

class CollectiveWisdomTracker:
    """
    Tracks and accumulates collective wisdom from decisions

    Adapted from Odoo CollectiveWisdomTracker
    Builds organizational knowledge over time
    """

    def __init__(self):
        self.wisdom: Dict[str, Any] = {
            'decision_patterns': [],
            'evolution_events': [],
            'total_decisions': 0,
            'avg_confidence': 0.0
        }

    def record_decision(
        self,
        decision: CollectiveDecision,
        context: Dict[str, Any]
    ):
        """Record a decision in collective wisdom"""
        pattern = {
            'context_type': decision.decision_type.value,
            'decision_confidence': decision.collective_confidence,
            'experts_involved': decision.contributing_experts,
            'timestamp': decision.timestamp.isoformat()
        }

        self.wisdom['decision_patterns'].append(pattern)
        self.wisdom['total_decisions'] += 1

        # Keep only last 1000 patterns
        if len(self.wisdom['decision_patterns']) > 1000:
            self.wisdom['decision_patterns'] = self.wisdom['decision_patterns'][-1000:]

        # Update average confidence
        self._update_avg_confidence()

    def _update_avg_confidence(self):
        """Update average confidence metric"""
        if self.wisdom['decision_patterns']:
            confidences = [
                p['decision_confidence']
                for p in self.wisdom['decision_patterns']
            ]
            self.wisdom['avg_confidence'] = sum(confidences) / len(confidences)

    def get_wisdom(self) -> Dict[str, Any]:
        """Get collective wisdom"""
        return self.wisdom.copy()

    def should_evolve(self, consciousness_threshold: float = 0.9) -> bool:
        """Determine if organism should evolve based on accumulated wisdom"""
        return (
            self.wisdom['total_decisions'] >= 100 and
            self.wisdom['avg_confidence'] >= consciousness_threshold
        )


# ========== Organism Evolution ==========

class OrganismEvolution:
    """
    Handles organism evolution when wisdom threshold is reached

    Adapted from Odoo OrganismEvolution
    Unlocks new capabilities based on accumulated experience
    """

    @staticmethod
    def evolve_capabilities(current_consciousness: float) -> List[str]:
        """
        Generate new capabilities based on consciousness level

        Returns:
            List of new capabilities unlocked
        """
        new_capabilities = [
            'Enhanced pattern recognition',
            'Improved cross-expert communication',
            'Advanced predictive capabilities',
            'Deeper strategic insights'
        ]

        if current_consciousness >= 0.95:
            new_capabilities.extend([
                'Autonomous decision making',
                'Self-optimization protocols',
                'Emergent problem solving'
            ])

        return new_capabilities

    @staticmethod
    def increase_consciousness(
        current_level: float,
        increment: float = 0.1
    ) -> float:
        """Increase consciousness level (max 1.0)"""
        return min(1.0, current_level + increment)
