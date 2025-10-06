"""
Collective Intelligence Pattern - Extracted from Odoo ai_organ_coordinator.py

Multi-organ coordination and collective decision making with:
- Organ lifecycle management (dormant → learning → active → wise)
- Cross-organ communication
- Weighted confidence scoring
- Context-based organ selection
- Collective wisdom accumulation
- Organism evolution

Original Source: bcm_ai_control/models/ai_organ_coordinator.py
Extracted: 2025-10-05
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# ========== Enums and Data Models ==========

class OrganLifecycleState(Enum):
    """Lifecycle states for AI organs"""
    DORMANT = "dormant"  # Not yet activated
    LEARNING = "learning"  # In training phase
    ACTIVE = "active"  # Fully operational
    WISE = "wise"  # With accumulated experience


class DecisionContext(Enum):
    """Types of decisions requiring collective intelligence"""
    RISK_ASSESSMENT = "risk_assessment"
    INCIDENT_RESPONSE = "incident_response"
    SCENARIO_PLANNING = "scenario_planning"
    COMPLIANCE_CHECK = "compliance_check"
    TRAINING_DESIGN = "training_design"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    GENERAL = "general"


@dataclass
class AIOrganInfo:
    """Information about an AI organ"""
    organ_type: str
    name: str
    provider: str  # 'anthropic', 'local', etc.
    status: OrganLifecycleState = OrganLifecycleState.LEARNING
    health_score: float = 0.6
    personality: str = ""


@dataclass
class OrganInput:
    """Input from a single AI organ"""
    organ_type: str
    response: Dict[str, Any]
    confidence: float
    timestamp: str


@dataclass
class CollectiveDecision:
    """Result of collective decision making"""
    decision_type: str
    collective_confidence: float
    contributing_organs: int
    decision_factors: List[Dict[str, Any]]
    synthesis_method: str
    timestamp: str
    organism_consciousness: float
    recommendation: Optional[str] = None


# ========== Communication Channels ==========

class OrganCommunicationChannels:
    """EventBus channels for cross-organ communication"""

    CHANNELS = [
        'ai_organ_coordination',      # Coordination between organs
        'memory_synchronization',     # Sync shared memory
        'pattern_sharing',            # Share learned patterns
        'collective_decision_making',  # Multi-organ decisions
        'emergency_broadcasts'        # Critical alerts
    ]

    @classmethod
    def get_all_channels(cls) -> List[str]:
        """Get all communication channel names"""
        return cls.CHANNELS.copy()


# ========== Organ Registry ==========

class AIOrganRegistry:
    """
    Registry of AI organs with their configurations

    Standard BCM platform has 10 specialized organs
    """

    DEFAULT_ORGANS = [
        AIOrganInfo(
            organ_type='governance_brain',
            name='🧠 Governance Brain',
            provider='anthropic',
            personality='Strategic decision making and governance'
        ),
        AIOrganInfo(
            organ_type='emergency_response',
            name='🚨 Emergency Response',
            provider='local',
            personality='Rapid incident response'
        ),
        AIOrganInfo(
            organ_type='impact_oracle',
            name='🔮 Impact Oracle',
            provider='local',
            personality='Predictive impact analysis'
        ),
        AIOrganInfo(
            organ_type='scenario_creator',
            name='🎭 Scenario Creator',
            provider='local',
            personality='Creative scenario generation'
        ),
        AIOrganInfo(
            organ_type='risk_advisor',
            name='⚠️ Risk Advisor',
            provider='local',
            personality='Risk assessment and FAIR analysis'
        ),
        AIOrganInfo(
            organ_type='compliance_guardian',
            name='🛡️ Compliance Guardian',
            provider='local',
            personality='ISO 22301 compliance checking'
        ),
        AIOrganInfo(
            organ_type='performance_analyst',
            name='📈 Performance Analyst',
            provider='local',
            personality='Performance metrics and trends'
        ),
        AIOrganInfo(
            organ_type='learning_coach',
            name='🎓 Learning Coach',
            provider='local',
            personality='Competency assessment and training'
        ),
        AIOrganInfo(
            organ_type='plan_generator',
            name='📋 Plan Generator',
            provider='local',
            personality='BCM plan creation and optimization'
        ),
        AIOrganInfo(
            organ_type='lifecycle_monitor',
            name='📊 Lifecycle Monitor',
            provider='local',
            personality='Organ health monitoring'
        ),
    ]

    def __init__(self):
        self.organs: Dict[str, AIOrganInfo] = {}
        self._load_default_organs()

    def _load_default_organs(self):
        """Load default organ configurations"""
        for organ in self.DEFAULT_ORGANS:
            self.register_organ(organ)

    def register_organ(self, organ: AIOrganInfo):
        """Register an AI organ"""
        self.organs[organ.organ_type] = organ
        logger.info(f"Registered organ: {organ.name}")

    def get_organ(self, organ_type: str) -> AIOrganInfo:
        """Get organ information"""
        if organ_type not in self.organs:
            raise ValueError(f"Organ {organ_type} not registered")
        return self.organs[organ_type]

    def get_active_organs(self) -> List[AIOrganInfo]:
        """Get all active organs"""
        return [
            organ for organ in self.organs.values()
            if organ.status in [OrganLifecycleState.ACTIVE, OrganLifecycleState.WISE]
        ]

    def activate_organ(self, organ_type: str):
        """Activate an organ (move to active state)"""
        organ = self.get_organ(organ_type)
        organ.status = OrganLifecycleState.ACTIVE
        logger.info(f"Activated organ: {organ.name}")


# ========== Context-Based Organ Selection ==========

class OrganSelectionStrategy:
    """
    Determines which organs should participate in a decision based on context

    Different decision types require different specialist combinations
    """

    ORGAN_REQUIREMENTS = {
        DecisionContext.RISK_ASSESSMENT: [
            'risk_advisor',
            'impact_oracle',
            'governance_brain'
        ],
        DecisionContext.INCIDENT_RESPONSE: [
            'emergency_response',
            'impact_oracle',
            'plan_generator'
        ],
        DecisionContext.SCENARIO_PLANNING: [
            'scenario_creator',
            'impact_oracle',
            'risk_advisor'
        ],
        DecisionContext.COMPLIANCE_CHECK: [
            'compliance_guardian',
            'governance_brain'
        ],
        DecisionContext.TRAINING_DESIGN: [
            'learning_coach',
            'scenario_creator'
        ],
        DecisionContext.PERFORMANCE_ANALYSIS: [
            'performance_analyst',
            'impact_oracle'
        ],
        DecisionContext.GENERAL: [
            'governance_brain',
            'impact_oracle'
        ]
    }

    @classmethod
    def get_required_organs(cls, context_type: DecisionContext) -> List[str]:
        """Get list of organs required for a decision context"""
        return cls.ORGAN_REQUIREMENTS.get(
            context_type,
            cls.ORGAN_REQUIREMENTS[DecisionContext.GENERAL]
        ).copy()


# ========== Weighted Confidence Scoring ==========

class WeightedConfidenceScorer:
    """
    Calculates weighted confidence scores for collective decisions

    Organs have different weights based on decision context
    """

    ORGAN_WEIGHTS = {
        DecisionContext.RISK_ASSESSMENT: {
            'risk_advisor': 0.4,
            'impact_oracle': 0.3,
            'governance_brain': 0.3
        },
        DecisionContext.INCIDENT_RESPONSE: {
            'emergency_response': 0.5,
            'impact_oracle': 0.3,
            'plan_generator': 0.2
        },
        DecisionContext.SCENARIO_PLANNING: {
            'scenario_creator': 0.4,
            'impact_oracle': 0.3,
            'risk_advisor': 0.3
        },
        DecisionContext.COMPLIANCE_CHECK: {
            'compliance_guardian': 0.6,
            'governance_brain': 0.4
        },
        DecisionContext.GENERAL: {
            'governance_brain': 0.3,
            'impact_oracle': 0.2
        }
    }

    @classmethod
    def get_organ_weight(cls, organ_type: str, context: DecisionContext) -> float:
        """Get weight for an organ in specific context"""
        context_weights = cls.ORGAN_WEIGHTS.get(
            context,
            cls.ORGAN_WEIGHTS[DecisionContext.GENERAL]
        )
        return context_weights.get(organ_type, 0.1)  # Default weight = 0.1

    @classmethod
    def calculate_weighted_confidence(
        cls,
        organ_inputs: List[OrganInput],
        context: DecisionContext
    ) -> float:
        """
        Calculate weighted confidence from multiple organ inputs

        Returns: Weighted confidence score (0.0 - 1.0)
        """
        total_weighted_confidence = 0.0
        total_weight = 0.0

        for organ_input in organ_inputs:
            weight = cls.get_organ_weight(organ_input.organ_type, context)
            total_weighted_confidence += organ_input.confidence * weight
            total_weight += weight

        if total_weight == 0:
            return 0.5  # Default confidence

        return total_weighted_confidence / total_weight


# ========== Collective Decision Synthesizer ==========

class CollectiveDecisionSynthesizer:
    """
    Synthesizes collective decisions from multiple AI organ inputs

    Combines weighted confidence scoring with decision factors
    """

    def __init__(self, organism_consciousness: float = 0.7):
        self.organism_consciousness = organism_consciousness
        self.scorer = WeightedConfidenceScorer()

    def synthesize(
        self,
        organ_inputs: List[OrganInput],
        context: DecisionContext
    ) -> CollectiveDecision:
        """
        Synthesize collective decision from organ inputs

        Args:
            organ_inputs: Inputs from participating organs
            context: Decision context type

        Returns:
            Collective decision with confidence and factors
        """
        # Calculate weighted confidence
        collective_confidence = self.scorer.calculate_weighted_confidence(
            organ_inputs,
            context
        )

        # Build decision factors
        decision_factors = []
        for organ_input in organ_inputs:
            weight = self.scorer.get_organ_weight(organ_input.organ_type, context)

            decision_factors.append({
                'organ': organ_input.organ_type,
                'input': organ_input.response,
                'confidence': organ_input.confidence,
                'weight': weight,
                'timestamp': organ_input.timestamp
            })

        # Generate recommendation if confidence is high
        recommendation = None
        if collective_confidence > 0.8:
            recommendation = self._generate_recommendation(decision_factors, context)

        return CollectiveDecision(
            decision_type=context.value,
            collective_confidence=collective_confidence,
            contributing_organs=len(organ_inputs),
            decision_factors=decision_factors,
            synthesis_method='weighted_confidence',
            timestamp=datetime.now().isoformat(),
            organism_consciousness=self.organism_consciousness,
            recommendation=recommendation
        )

    def _generate_recommendation(
        self,
        decision_factors: List[Dict[str, Any]],
        context: DecisionContext
    ) -> str:
        """Generate human-readable recommendation from decision factors"""
        # Simple template-based recommendation
        highest_confidence_factor = max(
            decision_factors,
            key=lambda f: f['confidence']
        )

        return (
            f"Based on {len(decision_factors)} organ analysis with "
            f"{highest_confidence_factor['organ']} as primary advisor "
            f"(confidence: {highest_confidence_factor['confidence']:.0%})"
        )


# ========== Collective Wisdom Tracker ==========

class CollectiveWisdomTracker:
    """
    Tracks and accumulates collective wisdom from decisions

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
            'context_type': decision.decision_type,
            'decision_confidence': decision.collective_confidence,
            'organs_involved': decision.contributing_organs,
            'timestamp': decision.timestamp
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
            'Improved cross-organ communication',
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


# ========== Usage Example ==========

async def example_collective_decision():
    """Example of collective decision making"""

    # Setup
    registry = AIOrganRegistry()
    synthesizer = CollectiveDecisionSynthesizer(organism_consciousness=0.7)
    wisdom_tracker = CollectiveWisdomTracker()

    # Get required organs for risk assessment
    context = DecisionContext.RISK_ASSESSMENT
    required_organs = OrganSelectionStrategy.get_required_organs(context)

    # Simulate organ inputs
    organ_inputs = [
        OrganInput(
            organ_type='risk_advisor',
            response={'risk_level': 'high', 'recommendation': 'Immediate action required'},
            confidence=0.85,
            timestamp=datetime.now().isoformat()
        ),
        OrganInput(
            organ_type='impact_oracle',
            response={'predicted_impact': '$500K', 'timeframe': '48h'},
            confidence=0.82,
            timestamp=datetime.now().isoformat()
        ),
        OrganInput(
            organ_type='governance_brain',
            response={'strategic_priority': 'critical', 'board_approval': 'required'},
            confidence=0.90,
            timestamp=datetime.now().isoformat()
        ),
    ]

    # Synthesize collective decision
    decision = synthesizer.synthesize(organ_inputs, context)

    print(f"Collective Confidence: {decision.collective_confidence:.0%}")
    print(f"Contributing Organs: {decision.contributing_organs}")
    print(f"Recommendation: {decision.recommendation}")

    # Record in wisdom
    wisdom_tracker.record_decision(decision, {'organization': 'org_123'})

    # Check if should evolve
    if wisdom_tracker.should_evolve():
        new_capabilities = OrganismEvolution.evolve_capabilities(
            synthesizer.organism_consciousness
        )
        print(f"🌟 Organism evolved! New capabilities: {new_capabilities}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_collective_decision())
