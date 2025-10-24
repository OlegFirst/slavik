"""
Base Learning Subsystem - Reference Implementation
===================================================

Reference implementation of ILearningSubsystem using pattern detection and rule generation.

This provides basic self-learning capabilities that other modules can extend:
1. Pattern detection from historical data
2. Rule generation from patterns
3. Feedback-based learning
4. Prediction from learned patterns

Other modules should implement ILearningSubsystem with their own domain logic,
not just reuse this implementation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import uuid
from collections import defaultdict, Counter
import json

from ..protocols import ILearningSubsystem, LearningDataStandard


logger = logging.getLogger(__name__)


class BaseLearningSub system(ILearningSubsystem):
    """
    Reference Learning subsystem implementation.

    Provides basic pattern detection and rule generation capabilities.
    Uses statistical analysis and frequency-based pattern detection.

    Domain: 'base' - General-purpose Learning
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize base learning subsystem.

        Args:
            storage_path: Path to persist learned patterns (optional)
        """
        self.name = "base_learning"
        self.domain = "base"
        self.version = "1.0.0"
        self.storage_path = storage_path

        # In-memory storage for patterns and rules
        self.patterns: Dict[str, Dict[str, Any]] = {}
        self.rules: Dict[str, Dict[str, Any]] = {}
        self.learning_history: List[Dict[str, Any]] = []

        # Track health
        self._last_learning = None
        self._last_pattern_detection = None
        self._error_count = 0
        self._learning_count = 0
        self._pattern_count = 0
        self._rule_count = 0

        # Load persisted patterns if available
        if storage_path:
            self._load_from_storage()

        logger.info(f"BaseLearningSubsystem initialized: {self.name}")

    def get_metadata(self) -> Dict[str, Any]:
        """Return subsystem metadata."""
        return {
            'name': self.name,
            'domain': self.domain,
            'version': self.version,
            'capabilities': [
                'pattern_detection',
                'rule_generation',
                'anomaly_learning',
                'feedback_learning'
            ],
            'learning_modes': [
                'unsupervised',
                'supervised',
                'reinforcement'
            ],
            'status': 'active',
            'pattern_count': len(self.patterns)
        }

    def learn_from_data(
        self,
        data: List[Dict[str, Any]],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Learn patterns from provided data.

        Args:
            data: Training data (events/observations)
            config: Learning configuration

        Returns:
            dict: Learning result in standard format
        """
        try:
            config = config or {}
            mode = config.get('mode', 'unsupervised')
            min_confidence = config.get('min_pattern_confidence', 0.7)

            patterns_found = []

            if mode == 'unsupervised':
                # Unsupervised pattern detection
                patterns_found = self._detect_patterns_unsupervised(data, min_confidence)

            elif mode == 'supervised':
                # Supervised learning with feedback
                feedback = config.get('feedback', {})
                patterns_found = self._learn_supervised(data, feedback, min_confidence)

            elif mode == 'reinforcement':
                # Reinforcement learning
                patterns_found = self._learn_reinforcement(data, min_confidence)

            else:
                raise ValueError(f"Unknown learning mode: {mode}")

            # Store learned patterns
            for pattern in patterns_found:
                self.patterns[pattern['id']] = pattern
                self._pattern_count += 1

            # Generate rules from patterns
            rules_generated = self._generate_rules_from_patterns(patterns_found)

            self._last_learning = datetime.utcnow()
            self._learning_count += 1

            # Record learning event
            self.learning_history.append({
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'mode': mode,
                'data_size': len(data),
                'patterns_found': len(patterns_found),
                'rules_generated': rules_generated
            })

            return LearningDataStandard.format_learning_result(
                subsystem_name=self.name,
                domain=self.domain,
                patterns_found=len(patterns_found),
                patterns=patterns_found,
                rules_generated=rules_generated
            )

        except Exception as e:
            logger.error(f"Learning error in BaseLearningSubsystem: {e}")
            self._error_count += 1
            return LearningDataStandard.format_learning_result(
                subsystem_name=self.name,
                domain=self.domain,
                patterns_found=0,
                patterns=[],
                rules_generated=0
            )

    def _detect_patterns_unsupervised(
        self,
        data: List[Dict[str, Any]],
        min_confidence: float
    ) -> List[Dict[str, Any]]:
        """Detect patterns using unsupervised methods."""
        patterns = []

        # Pattern 1: Frequency-based patterns
        # Detect common sequences or co-occurrences
        patterns.extend(self._detect_frequency_patterns(data, min_confidence))

        # Pattern 2: Time-based patterns
        # Detect temporal patterns
        patterns.extend(self._detect_temporal_patterns(data, min_confidence))

        # Pattern 3: Correlation patterns
        # Detect correlated attributes
        patterns.extend(self._detect_correlation_patterns(data, min_confidence))

        return patterns

    def _detect_frequency_patterns(
        self,
        data: List[Dict[str, Any]],
        min_confidence: float
    ) -> List[Dict[str, Any]]:
        """Detect patterns based on frequency."""
        patterns = []

        # Count attribute value frequencies
        attribute_counts = defaultdict(Counter)
        for item in data:
            for key, value in item.items():
                if isinstance(value, (str, int, bool)):
                    attribute_counts[key][value] += 1

        # Find high-frequency patterns
        for attribute, value_counts in attribute_counts.items():
            total = sum(value_counts.values())
            for value, count in value_counts.most_common(5):
                frequency = count / total
                if frequency >= min_confidence:
                    pattern_id = str(uuid.uuid4())
                    patterns.append(
                        LearningDataStandard.format_pattern(
                            pattern_id=pattern_id,
                            description=f"High frequency: {attribute}={value} occurs {frequency:.1%} of the time",
                            confidence=frequency,
                            frequency=count,
                            conditions={attribute: value},
                            actions={'expect_high_frequency': True}
                        )
                    )

        return patterns

    def _detect_temporal_patterns(
        self,
        data: List[Dict[str, Any]],
        min_confidence: float
    ) -> List[Dict[str, Any]]:
        """Detect time-based patterns."""
        patterns = []

        # Look for timestamp field
        timestamped_data = [
            item for item in data
            if 'timestamp' in item or 'created_at' in item or 'time' in item
        ]

        if not timestamped_data:
            return patterns

        # Detect patterns like "peak hours", "quiet periods"
        # This is a simplified implementation
        pattern_id = str(uuid.uuid4())
        patterns.append(
            LearningDataStandard.format_pattern(
                pattern_id=pattern_id,
                description="Temporal pattern detected in data distribution",
                confidence=0.75,
                frequency=len(timestamped_data),
                conditions={'has_timestamp': True},
                actions={'consider_time_factor': True}
            )
        )

        return patterns

    def _detect_correlation_patterns(
        self,
        data: List[Dict[str, Any]],
        min_confidence: float
    ) -> List[Dict[str, Any]]:
        """Detect correlated attributes."""
        patterns = []

        # Find attribute pairs that co-occur frequently
        if len(data) < 10:
            return patterns

        # Simplified correlation detection
        attribute_pairs = defaultdict(int)
        for item in data:
            keys = list(item.keys())
            for i, key1 in enumerate(keys):
                for key2 in keys[i+1:]:
                    pair = tuple(sorted([key1, key2]))
                    attribute_pairs[pair] += 1

        total = len(data)
        for pair, count in attribute_pairs.items():
            correlation = count / total
            if correlation >= min_confidence:
                pattern_id = str(uuid.uuid4())
                patterns.append(
                    LearningDataStandard.format_pattern(
                        pattern_id=pattern_id,
                        description=f"Correlation: {pair[0]} and {pair[1]} co-occur {correlation:.1%} of the time",
                        confidence=correlation,
                        frequency=count,
                        conditions={'has_both': list(pair)},
                        actions={'use_together': True}
                    )
                )

        return patterns

    def _learn_supervised(
        self,
        data: List[Dict[str, Any]],
        feedback: Dict[str, Any],
        min_confidence: float
    ) -> List[Dict[str, Any]]:
        """Learn with human feedback."""
        # Start with unsupervised detection
        patterns = self._detect_patterns_unsupervised(data, min_confidence)

        # Adjust confidence based on feedback
        for pattern in patterns:
            pattern_type = pattern['description'].split(':')[0]
            if pattern_type in feedback:
                adjustment = feedback[pattern_type]
                pattern['confidence'] *= adjustment

        return patterns

    def _learn_reinforcement(
        self,
        data: List[Dict[str, Any]],
        min_confidence: float
    ) -> List[Dict[str, Any]]:
        """Reinforcement learning."""
        # Look for reward/outcome signals in data
        patterns = []

        positive_outcomes = [item for item in data if item.get('outcome') == 'success']
        negative_outcomes = [item for item in data if item.get('outcome') == 'failure']

        if positive_outcomes:
            # Learn from successes
            success_patterns = self._detect_patterns_unsupervised(
                positive_outcomes,
                min_confidence
            )
            for pattern in success_patterns:
                pattern['description'] = f"Success pattern: {pattern['description']}"
                pattern['actions']['outcome'] = 'success'
            patterns.extend(success_patterns)

        if negative_outcomes:
            # Learn from failures
            failure_patterns = self._detect_patterns_unsupervised(
                negative_outcomes,
                min_confidence
            )
            for pattern in failure_patterns:
                pattern['description'] = f"Failure pattern: {pattern['description']}"
                pattern['actions']['outcome'] = 'failure'
                pattern['actions']['avoid'] = True
            patterns.extend(failure_patterns)

        return patterns

    def _generate_rules_from_patterns(self, patterns: List[Dict[str, Any]]) -> int:
        """Generate actionable rules from patterns."""
        rules_generated = 0

        for pattern in patterns:
            # Generate rule from pattern
            rule_id = str(uuid.uuid4())

            # Convert pattern conditions to rule condition
            conditions = pattern['conditions']
            condition_str = " AND ".join([f"{k}=={v}" for k, v in conditions.items()])

            # Convert pattern actions to rule action
            actions = pattern['actions']
            action_str = json.dumps(actions)

            rule = LearningDataStandard.format_rule(
                rule_id=rule_id,
                name=f"Rule from {pattern['id'][:8]}",
                description=f"Auto-generated from pattern: {pattern['description']}",
                condition=condition_str,
                action=action_str,
                confidence=pattern['confidence'],
                priority=int(pattern['confidence'] * 100)
            )

            self.rules[rule_id] = rule
            self._rule_count += 1
            rules_generated += 1

        return rules_generated

    def detect_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect patterns without learning (no state change).

        Args:
            data: Data to analyze

        Returns:
            dict: Detected patterns
        """
        try:
            # Detect patterns without storing them
            patterns = self._detect_patterns_unsupervised(data, min_confidence=0.5)

            # Detect anomalies (data points that don't match patterns)
            anomalies = self._detect_anomalies(data, patterns)

            self._last_pattern_detection = datetime.utcnow()

            return {
                'subsystem': self.name,
                'domain': self.domain,
                'patterns': patterns,
                'anomalies': anomalies,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }

        except Exception as e:
            logger.error(f"Pattern detection error: {e}")
            return {
                'subsystem': self.name,
                'domain': self.domain,
                'patterns': [],
                'anomalies': [],
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }

    def _detect_anomalies(
        self,
        data: List[Dict[str, Any]],
        patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect anomalies (data points that don't fit patterns)."""
        anomalies = []

        # Simple anomaly detection: items that don't match any pattern
        for item in data:
            matches_pattern = False
            for pattern in patterns:
                conditions = pattern['conditions']
                if all(item.get(k) == v for k, v in conditions.items()):
                    matches_pattern = True
                    break

            if not matches_pattern and patterns:  # Only if we have patterns to compare
                anomalies.append({
                    'data': item,
                    'reason': 'Does not match any learned pattern',
                    'severity': 'low'
                })

        return anomalies

    def generate_rules(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate actionable rules from patterns.

        Args:
            patterns: List of patterns

        Returns:
            dict: Generated rules
        """
        try:
            rules_generated = self._generate_rules_from_patterns(patterns)

            # Get most recently generated rules
            recent_rules = list(self.rules.values())[-rules_generated:]

            return {
                'subsystem': self.name,
                'domain': self.domain,
                'rules': recent_rules,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }

        except Exception as e:
            logger.error(f"Rule generation error: {e}")
            return {
                'subsystem': self.name,
                'domain': self.domain,
                'rules': [],
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }

    def apply_feedback(
        self,
        pattern_id: str,
        feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply human feedback to improve learning.

        Args:
            pattern_id: ID of pattern
            feedback: Feedback data

        Returns:
            dict: Feedback application result
        """
        try:
            if pattern_id not in self.patterns:
                return {
                    'success': False,
                    'pattern_id': pattern_id,
                    'error': 'Pattern not found',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }

            pattern = self.patterns[pattern_id]

            # Apply feedback
            correct = feedback.get('correct', True)
            rating = feedback.get('rating', 3)  # 1-5 scale
            corrections = feedback.get('corrections', {})

            # Adjust confidence based on feedback
            if not correct:
                pattern['confidence'] *= 0.5  # Reduce confidence
            else:
                # Boost confidence based on rating
                boost = (rating - 3) * 0.1  # -0.2 to +0.2
                pattern['confidence'] = min(1.0, pattern['confidence'] + boost)

            # Apply corrections
            if corrections:
                if 'description' in corrections:
                    pattern['description'] = corrections['description']
                if 'conditions' in corrections:
                    pattern['conditions'].update(corrections['conditions'])
                if 'actions' in corrections:
                    pattern['actions'].update(corrections['actions'])

            new_confidence = pattern['confidence']

            return {
                'success': True,
                'pattern_id': pattern_id,
                'updated': True,
                'new_confidence': new_confidence,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }

        except Exception as e:
            logger.error(f"Feedback application error: {e}")
            return {
                'success': False,
                'pattern_id': pattern_id,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }

    def get_learned_patterns(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve learned patterns with optional filtering.

        Args:
            filters: Optional filters

        Returns:
            dict: Patterns matching filters
        """
        try:
            patterns = list(self.patterns.values())

            # Apply filters
            if filters:
                min_confidence = filters.get('min_confidence')
                if min_confidence:
                    patterns = [p for p in patterns if p['confidence'] >= min_confidence]

                min_frequency = filters.get('min_frequency')
                if min_frequency:
                    patterns = [p for p in patterns if p['frequency'] >= min_frequency]

                category = filters.get('category')
                if category:
                    patterns = [p for p in patterns if category in p['description']]

            return {
                'subsystem': self.name,
                'domain': self.domain,
                'patterns': patterns,
                'total_count': len(patterns),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }

        except Exception as e:
            logger.error(f"Pattern retrieval error: {e}")
            return {
                'subsystem': self.name,
                'domain': self.domain,
                'patterns': [],
                'total_count': 0,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }

    def predict_from_patterns(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make prediction based on learned patterns.

        Args:
            context: Current context

        Returns:
            dict: Prediction based on patterns
        """
        try:
            # Find patterns that match context
            matching_patterns = []
            for pattern in self.patterns.values():
                conditions = pattern['conditions']
                if all(context.get(k) == v for k, v in conditions.items()):
                    matching_patterns.append(pattern)

            if not matching_patterns:
                return {
                    'subsystem': self.name,
                    'domain': self.domain,
                    'prediction': None,
                    'confidence': 0.0,
                    'matching_patterns': [],
                    'explanation': 'No matching patterns found',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }

            # Use highest confidence pattern for prediction
            best_pattern = max(matching_patterns, key=lambda p: p['confidence'])

            prediction = best_pattern['actions']
            confidence = best_pattern['confidence']
            matching_ids = [p['id'] for p in matching_patterns]

            return {
                'subsystem': self.name,
                'domain': self.domain,
                'prediction': prediction,
                'confidence': confidence,
                'matching_patterns': matching_ids,
                'explanation': best_pattern['description'],
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }

        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                'subsystem': self.name,
                'domain': self.domain,
                'prediction': None,
                'confidence': 0.0,
                'matching_patterns': [],
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }

    def register_with_coordinator(self, coordinator: Any) -> bool:
        """
        Register this subsystem with the central coordinator.

        Args:
            coordinator: SubsystemCoordinator instance

        Returns:
            bool: True if registration successful
        """
        try:
            return coordinator.register_learning(self.name, self)
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False

    def get_health_status(self) -> Dict[str, Any]:
        """Return current health status."""
        error_rate = (
            self._error_count / max(self._learning_count, 1)
            if self._learning_count > 0
            else 0.0
        )

        healthy = error_rate < 0.1

        # Calculate learning rate (patterns per day)
        learning_rate = 0.0
        if self.learning_history:
            recent_history = [
                event for event in self.learning_history
                if datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                > datetime.now() - timedelta(days=1)
            ]
            learning_rate = sum(event['patterns_found'] for event in recent_history)

        return {
            'healthy': healthy,
            'status': 'healthy' if healthy else 'degraded',
            'last_learning': (
                self._last_learning.isoformat() + 'Z'
                if self._last_learning else None
            ),
            'last_pattern_detection': (
                self._last_pattern_detection.isoformat() + 'Z'
                if self._last_pattern_detection else None
            ),
            'pattern_count': len(self.patterns),
            'rule_count': len(self.rules),
            'learning_rate': learning_rate,
            'error_rate': error_rate,
            'issues': [] if healthy else [f'High error rate: {error_rate:.2%}']
        }

    def get_capabilities(self) -> List[str]:
        """Return list of capabilities."""
        return [
            'pattern_detection',
            'rule_generation',
            'anomaly_detection',
            'feedback_learning'
        ]

    def _load_from_storage(self):
        """Load persisted patterns from storage."""
        if not self.storage_path:
            return

        try:
            import os
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.patterns = data.get('patterns', {})
                    self.rules = data.get('rules', {})
                    self._pattern_count = len(self.patterns)
                    self._rule_count = len(self.rules)
                    logger.info(f"Loaded {self._pattern_count} patterns from storage")
        except Exception as e:
            logger.error(f"Error loading from storage: {e}")

    def save_to_storage(self):
        """Persist patterns to storage."""
        if not self.storage_path:
            return

        try:
            import os
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

            data = {
                'patterns': self.patterns,
                'rules': self.rules,
                'metadata': self.get_metadata(),
                'saved_at': datetime.utcnow().isoformat() + 'Z'
            }

            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {len(self.patterns)} patterns to storage")
        except Exception as e:
            logger.error(f"Error saving to storage: {e}")
