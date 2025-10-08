"""
Learning Tracker - Tracks and learns from decisions and outcomes
=================================================================

Continuous improvement through:
- Recording decision outcomes
- Pattern recognition
- Success/failure analysis
- Feedback integration
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class LearningTracker:
    """
    Tracks decisions and outcomes for continuous learning

    Features:
    - Record decision outcomes
    - Analyze success patterns
    - Identify failure patterns
    - Generate insights
    - Export learning data
    """

    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize learning tracker

        Args:
            storage_dir: Directory to store learning data
        """
        self.storage_dir = Path(storage_dir) if storage_dir else Path(__file__).parent / 'learning_data'
        self.storage_dir.mkdir(exist_ok=True)

        self.learning_examples = []
        self.patterns = defaultdict(list)

        # Load existing learning data
        self._load_learning_data()

        logger.info(f"✅ Learning Tracker initialized (storage: {self.storage_dir})")

    async def record_decision_outcome(
        self,
        decision: Dict[str, Any],
        action_executed: str,
        outcome: Dict[str, Any],
        feedback: Optional[Dict] = None
    ) -> str:
        """
        Record decision outcome for learning

        Args:
            decision: Original decision
            action_executed: Action that was executed
            outcome: Result of the action
            feedback: Optional feedback from user/system

        Returns:
            Learning example ID
        """
        try:
            example = {
                'id': f"learning_{datetime.utcnow().timestamp()}",
                'decision': decision,
                'action_executed': action_executed,
                'outcome': outcome,
                'feedback': feedback,
                'recorded_at': datetime.utcnow().isoformat(),
                'success': outcome.get('success', False),
                'impact': self._calculate_impact(outcome)
            }

            self.learning_examples.append(example)

            # Extract patterns
            await self._extract_patterns(example)

            # Save to disk
            self._save_learning_example(example)

            logger.info(f"📚 Recorded learning example: {example['id']}")

            return example['id']

        except Exception as e:
            logger.error(f"❌ Failed to record learning example: {e}")
            return ""

    async def get_insights(
        self,
        situation_type: Optional[str] = None,
        action_type: Optional[str] = None,
        min_confidence: float = 0.7
    ) -> Dict[str, Any]:
        """
        Get insights from learning history

        Args:
            situation_type: Filter by situation type
            action_type: Filter by action type
            min_confidence: Minimum confidence threshold

        Returns:
            Insights and recommendations
        """
        try:
            # Filter examples
            examples = self._filter_examples(situation_type, action_type)

            if not examples:
                return {
                    'insights': [],
                    'confidence': 0.0,
                    'sample_size': 0
                }

            # Analyze patterns
            success_patterns = self._analyze_success_patterns(examples)
            failure_patterns = self._analyze_failure_patterns(examples)

            # Calculate success rate
            successes = sum(1 for e in examples if e.get('success'))
            success_rate = successes / len(examples) if examples else 0.0

            # Generate insights
            insights = []

            if success_rate > 0.7:
                insights.append({
                    'type': 'positive',
                    'message': f"High success rate ({success_rate:.1%}) for this type of decision",
                    'confidence': success_rate
                })

            if success_rate < 0.3:
                insights.append({
                    'type': 'negative',
                    'message': f"Low success rate ({success_rate:.1%}) - consider alternative approaches",
                    'confidence': 1.0 - success_rate
                })

            # Add pattern insights
            for pattern in success_patterns[:3]:  # Top 3
                if pattern['frequency'] > 3:
                    insights.append({
                        'type': 'pattern',
                        'message': f"Pattern found: {pattern['description']}",
                        'confidence': pattern['confidence']
                    })

            return {
                'insights': insights,
                'success_rate': success_rate,
                'sample_size': len(examples),
                'success_patterns': success_patterns,
                'failure_patterns': failure_patterns,
                'generated_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Failed to generate insights: {e}")
            return {'insights': [], 'error': str(e)}

    async def get_recommendations(
        self,
        situation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations based on learning history

        Args:
            situation: Current situation

        Returns:
            List of recommendations
        """
        try:
            situation_type = situation.get('type')

            # Find similar past situations
            similar_examples = self._find_similar_situations(situation)

            if not similar_examples:
                return []

            # Analyze what worked
            recommendations = []

            # Group by action
            by_action = defaultdict(list)
            for example in similar_examples:
                action = example['action_executed']
                by_action[action].append(example)

            # Calculate success rate per action
            for action, examples in by_action.items():
                successes = sum(1 for e in examples if e.get('success'))
                success_rate = successes / len(examples)

                if success_rate > 0.5:  # More than 50% success
                    recommendations.append({
                        'action': action,
                        'confidence': success_rate,
                        'reasoning': f"Based on {len(examples)} past cases with {success_rate:.1%} success rate",
                        'sample_size': len(examples)
                    })

            # Sort by confidence
            recommendations.sort(key=lambda x: x['confidence'], reverse=True)

            return recommendations

        except Exception as e:
            logger.error(f"❌ Failed to generate recommendations: {e}")
            return []

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        if not self.learning_examples:
            return {
                'total_examples': 0,
                'success_rate': 0.0
            }

        total = len(self.learning_examples)
        successes = sum(1 for e in self.learning_examples if e.get('success'))
        success_rate = successes / total if total > 0 else 0.0

        # Recent performance (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_examples = [
            e for e in self.learning_examples
            if datetime.fromisoformat(e['recorded_at']) > week_ago
        ]

        recent_successes = sum(1 for e in recent_examples if e.get('success'))
        recent_success_rate = recent_successes / len(recent_examples) if recent_examples else 0.0

        return {
            'total_examples': total,
            'total_successes': successes,
            'overall_success_rate': success_rate,
            'recent_examples': len(recent_examples),
            'recent_success_rate': recent_success_rate,
            'improvement': recent_success_rate - success_rate,
            'patterns_identified': len(self.patterns)
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _calculate_impact(self, outcome: Dict) -> str:
        """Calculate impact of outcome"""
        if outcome.get('error') or outcome.get('failed'):
            return 'negative'
        elif outcome.get('improved') or outcome.get('fixed'):
            return 'positive'
        else:
            return 'neutral'

    async def _extract_patterns(self, example: Dict):
        """Extract patterns from example"""
        # Simple pattern extraction
        situation_type = example['decision'].get('situation')
        action = example['action_executed']
        success = example.get('success')

        pattern_key = f"{situation_type}::{action}::{success}"
        self.patterns[pattern_key].append(example['id'])

    def _filter_examples(
        self,
        situation_type: Optional[str],
        action_type: Optional[str]
    ) -> List[Dict]:
        """Filter examples by criteria"""
        examples = self.learning_examples

        if situation_type:
            examples = [
                e for e in examples
                if e['decision'].get('situation') == situation_type
            ]

        if action_type:
            examples = [
                e for e in examples
                if e['action_executed'] == action_type
            ]

        return examples

    def _analyze_success_patterns(self, examples: List[Dict]) -> List[Dict]:
        """Analyze patterns in successful examples"""
        successful = [e for e in examples if e.get('success')]

        if not successful:
            return []

        # Group by action
        by_action = defaultdict(list)
        for example in successful:
            action = example['action_executed']
            by_action[action].append(example)

        # Create patterns
        patterns = []
        for action, action_examples in by_action.items():
            if len(action_examples) >= 2:  # At least 2 examples
                patterns.append({
                    'description': f"Action '{action}' successful in {len(action_examples)} cases",
                    'action': action,
                    'frequency': len(action_examples),
                    'confidence': len(action_examples) / len(examples)
                })

        return sorted(patterns, key=lambda x: x['frequency'], reverse=True)

    def _analyze_failure_patterns(self, examples: List[Dict]) -> List[Dict]:
        """Analyze patterns in failed examples"""
        failed = [e for e in examples if not e.get('success')]

        if not failed:
            return []

        # Similar to success patterns
        by_action = defaultdict(list)
        for example in failed:
            action = example['action_executed']
            by_action[action].append(example)

        patterns = []
        for action, action_examples in by_action.items():
            if len(action_examples) >= 2:
                patterns.append({
                    'description': f"Action '{action}' failed in {len(action_examples)} cases",
                    'action': action,
                    'frequency': len(action_examples),
                    'severity': 'high' if len(action_examples) > 5 else 'medium'
                })

        return sorted(patterns, key=lambda x: x['frequency'], reverse=True)

    def _find_similar_situations(self, situation: Dict) -> List[Dict]:
        """Find similar past situations"""
        situation_type = situation.get('type')
        severity = situation.get('severity')

        similar = []
        for example in self.learning_examples:
            ex_situation = example['decision'].get('situation')
            ex_severity = example['decision'].get('severity')

            if ex_situation == situation_type:
                # Exact match
                similar.append(example)
            elif ex_severity == severity:
                # Same severity
                similar.append(example)

        return similar

    # ========================================================================
    # Persistence
    # ========================================================================

    def _save_learning_example(self, example: Dict):
        """Save learning example to disk"""
        try:
            filename = f"learning_{example['id']}.json"
            filepath = self.storage_dir / filename

            with open(filepath, 'w') as f:
                json.dump(example, f, indent=2)

        except Exception as e:
            logger.error(f"❌ Failed to save learning example: {e}")

    def _load_learning_data(self):
        """Load existing learning data"""
        try:
            if not self.storage_dir.exists():
                return

            for filepath in self.storage_dir.glob('learning_*.json'):
                with open(filepath, 'r') as f:
                    example = json.load(f)
                    self.learning_examples.append(example)

            logger.info(f"📚 Loaded {len(self.learning_examples)} learning examples")

        except Exception as e:
            logger.error(f"❌ Failed to load learning data: {e}")

    def export_learning_data(self, output_path: str) -> bool:
        """Export all learning data to file"""
        try:
            with open(output_path, 'w') as f:
                json.dump({
                    'examples': self.learning_examples,
                    'patterns': dict(self.patterns),
                    'exported_at': datetime.utcnow().isoformat()
                }, f, indent=2)

            logger.info(f"📤 Exported learning data to {output_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to export learning data: {e}")
            return False
