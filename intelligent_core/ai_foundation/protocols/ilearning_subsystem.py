"""
ILearningSubsystem - Self-Learning and Pattern Recognition Subsystem Protocol
==============================================================================

Protocol interface that EVERY Learning subsystem must implement.

Examples of implementations:
- workflow_intelligence/learning/workflow_learning_subsystem.py
- expertise_center/learning/expert_learning_subsystem.py
- orchestration/learning/orchestration_learning_subsystem.py
- ai_foundation/learning/base_learning_subsystem.py (reference implementation)

Each implementation has its own:
- Pattern detection algorithms
- Learning strategies
- Rule generation logic
- Feedback loops
- Domain-specific learning objectives

But all follow this protocol for coordination.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class ILearningSubsystem(ABC):
    """
    Protocol for Learning subsystems - defines standard interface.

    Every module that has self-learning capabilities must implement this interface.
    The coordinator polls all implementations and aggregates insights.
    """

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Return subsystem metadata for discovery and coordination.

        Returns:
            dict: Metadata including:
                - name: str - Subsystem name (e.g., 'workflow_learning')
                - domain: str - Domain of expertise
                - version: str - Subsystem version
                - capabilities: List[str] - What this subsystem can learn
                - learning_modes: List[str] - Available learning modes
                - status: str - 'active', 'learning', 'idle', 'offline'
                - pattern_count: int - Number of patterns learned

        Example:
            {
                'name': 'workflow_learning',
                'domain': 'workflow',
                'version': '1.0.0',
                'capabilities': ['pattern_detection', 'rule_generation', 'anomaly_learning'],
                'learning_modes': ['supervised', 'unsupervised', 'reinforcement'],
                'status': 'active',
                'pattern_count': 487
            }
        """
        pass

    @abstractmethod
    def learn_from_data(self, data: List[Dict[str, Any]], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Learn patterns from provided data.

        Args:
            data: Training data (domain-specific events/observations)
            config: Optional learning configuration
                - mode: str - 'supervised', 'unsupervised', 'reinforcement'
                - min_pattern_confidence: float - Minimum confidence for pattern extraction
                - feedback: Optional[dict] - Human feedback for supervised learning

        Returns:
            dict: Learning result in STANDARD format
                - subsystem: str - Name of this subsystem
                - domain: str - Domain of learning
                - patterns_found: int - Number of new patterns discovered
                - patterns: List[dict] - Discovered patterns
                  Each pattern:
                    - id: str - Pattern ID
                    - description: str - Human-readable description
                    - confidence: float - Pattern confidence [0.0-1.0]
                    - frequency: int - How often pattern occurs
                    - conditions: dict - When pattern applies
                    - actions: dict - What to do when pattern detected
                - rules_generated: int - Number of new rules created
                - timestamp: str - ISO format timestamp

        Example:
            {
                'subsystem': 'workflow_learning',
                'domain': 'workflow',
                'patterns_found': 3,
                'patterns': [
                    {
                        'id': 'pattern_123',
                        'description': 'When incident severity is high, approval time increases by 40%',
                        'confidence': 0.89,
                        'frequency': 127,
                        'conditions': {'incident_severity': 'high'},
                        'actions': {'adjust_sla': True, 'notify_manager': True}
                    },
                    ...
                ],
                'rules_generated': 2,
                'timestamp': '2025-10-22T10:30:00Z'
            }
        """
        pass

    @abstractmethod
    def detect_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect patterns in provided data without learning (no state change).

        Args:
            data: Data to analyze for patterns

        Returns:
            dict: Detected patterns
                - subsystem: str
                - domain: str
                - patterns: List[dict] - Detected patterns
                - anomalies: List[dict] - Detected anomalies
                - timestamp: str
        """
        pass

    @abstractmethod
    def generate_rules(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate actionable rules from patterns.

        Args:
            patterns: List of patterns (from detect_patterns or learn_from_data)

        Returns:
            dict: Generated rules
                - subsystem: str
                - domain: str
                - rules: List[dict] - Generated rules
                  Each rule:
                    - id: str
                    - name: str
                    - description: str
                    - condition: str - When to apply (logic expression)
                    - action: str - What to do (action specification)
                    - confidence: float
                    - priority: int - Rule priority
                - timestamp: str
        """
        pass

    @abstractmethod
    def apply_feedback(self, pattern_id: str, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply human feedback to improve learning.

        Args:
            pattern_id: ID of pattern to provide feedback on
            feedback: Feedback data
                - correct: bool - Is pattern correct?
                - rating: int - 1-5 star rating
                - comments: Optional[str] - Human comments
                - corrections: Optional[dict] - Corrections to pattern

        Returns:
            dict: Feedback application result
                - success: bool
                - pattern_id: str
                - updated: bool - Whether pattern was updated
                - new_confidence: float - Updated confidence score
                - timestamp: str
        """
        pass

    @abstractmethod
    def get_learned_patterns(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieve learned patterns with optional filtering.

        Args:
            filters: Optional filters
                - min_confidence: float
                - min_frequency: int
                - category: str
                - date_range: dict

        Returns:
            dict: Patterns matching filters
                - subsystem: str
                - domain: str
                - patterns: List[dict]
                - total_count: int
                - timestamp: str
        """
        pass

    @abstractmethod
    def predict_from_patterns(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make prediction based on learned patterns.

        Args:
            context: Current context (domain-specific)

        Returns:
            dict: Prediction based on patterns
                - subsystem: str
                - domain: str
                - prediction: Any - Predicted outcome
                - confidence: float
                - matching_patterns: List[str] - Pattern IDs that contributed
                - timestamp: str
        """
        pass

    @abstractmethod
    def register_with_coordinator(self, coordinator: Any) -> bool:
        """
        Register this subsystem with the central coordinator.

        Args:
            coordinator: SubsystemCoordinator instance

        Returns:
            bool: True if registration successful
        """
        pass

    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """
        Return current health status of this subsystem.

        Returns:
            dict: Health status
                - healthy: bool
                - status: str - 'healthy', 'degraded', 'critical', 'offline'
                - last_learning: str - ISO timestamp
                - last_pattern_detection: str - ISO timestamp
                - pattern_count: int
                - rule_count: int
                - learning_rate: float - Patterns learned per day
                - error_rate: float - [0.0-1.0]
                - issues: List[str] - Any current issues
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Return list of capabilities this subsystem provides.

        Returns:
            List[str]: Capability names

        Example:
            ['pattern_detection', 'rule_generation', 'anomaly_detection', 'feedback_learning']
        """
        pass


class LearningDataStandard:
    """
    Standard data format for Learning subsystem communication.

    All subsystems should format their data according to this standard
    for coordinator aggregation.
    """

    @staticmethod
    def format_learning_result(
        subsystem_name: str,
        domain: str,
        patterns_found: int,
        patterns: List[Dict[str, Any]],
        rules_generated: int
    ) -> Dict[str, Any]:
        """
        Format learning result in standard way.

        Args:
            subsystem_name: Name of subsystem
            domain: Domain of expertise
            patterns_found: Number of patterns discovered
            patterns: List of pattern objects
            rules_generated: Number of rules created

        Returns:
            dict: Standardized learning result
        """
        return {
            'subsystem': subsystem_name,
            'domain': domain,
            'patterns_found': patterns_found,
            'patterns': patterns,
            'rules_generated': rules_generated,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

    @staticmethod
    def format_pattern(
        pattern_id: str,
        description: str,
        confidence: float,
        frequency: int,
        conditions: Dict[str, Any],
        actions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format single pattern in standard way."""
        return {
            'id': pattern_id,
            'description': description,
            'confidence': confidence,
            'frequency': frequency,
            'conditions': conditions,
            'actions': actions
        }

    @staticmethod
    def format_rule(
        rule_id: str,
        name: str,
        description: str,
        condition: str,
        action: str,
        confidence: float,
        priority: int
    ) -> Dict[str, Any]:
        """Format rule in standard way."""
        return {
            'id': rule_id,
            'name': name,
            'description': description,
            'condition': condition,
            'action': action,
            'confidence': confidence,
            'priority': priority
        }
