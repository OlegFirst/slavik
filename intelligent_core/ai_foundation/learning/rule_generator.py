"""
Rule Generator

Generates new rules based on extracted patterns.
"""

from typing import Dict, Any
import logging
import uuid

logger = logging.getLogger(__name__)


class RuleGenerator:
    """
    Rule Generator

    Generates actionable rules from patterns for human approval.
    """

    def __init__(self):
        """Initialize rule generator"""
        pass

    async def generate_rule(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate rule from pattern

        Args:
            pattern: Extracted pattern

        Returns:
            Generated rule
        """

        pattern_type = pattern.get('type')

        if pattern_type == 'successful_strategy':
            return self._generate_strategy_rule(pattern)
        elif pattern_type == 'common_challenge':
            return self._generate_challenge_rule(pattern)
        elif pattern_type == 'optimal_sequence':
            return self._generate_sequence_rule(pattern)
        else:
            return self._generate_generic_rule(pattern)

    def _generate_strategy_rule(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Generate rule from successful strategy pattern"""

        context = pattern.get('context', {})
        strategies = pattern.get('strategies', [])

        rule_text = f"For {context.get('industry')} organizations of {context.get('org_size')} size "
        rule_text += f"in {context.get('module')} module, recommended strategies: "
        rule_text += ", ".join(strategies)

        return {
            'id': str(uuid.uuid4()),
            'type': 'recommendation',
            'pattern_type': 'successful_strategy',
            'rule_text': rule_text,
            'conditions': context,
            'recommendations': strategies,
            'evidence': {
                'pattern_frequency': pattern.get('frequency', 0),
                'success_rate': pattern.get('success_rate', 0.0)
            }
        }

    def _generate_challenge_rule(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Generate rule from challenge pattern"""

        challenge = pattern.get('challenge', '')
        resolution = pattern.get('resolution', '')
        context = pattern.get('context', {})

        rule_text = f"When encountering '{challenge}' in {context.get('module')} module, "
        rule_text += f"recommended resolution: {resolution}"

        return {
            'id': str(uuid.uuid4()),
            'type': 'troubleshooting',
            'pattern_type': 'common_challenge',
            'rule_text': rule_text,
            'conditions': {
                'challenge_type': challenge,
                'module': context.get('module')
            },
            'resolution': resolution,
            'evidence': {
                'pattern_frequency': pattern.get('frequency', 0),
                'success_rate': pattern.get('success_rate', 0.0)
            }
        }

    def _generate_sequence_rule(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Generate rule from sequence pattern"""

        sequence = pattern.get('sequence', [])
        context = pattern.get('context', {})

        rule_text = f"Optimal workflow sequence for {context.get('module')} module: "
        rule_text += " → ".join(sequence)

        return {
            'id': str(uuid.uuid4()),
            'type': 'workflow_optimization',
            'pattern_type': 'optimal_sequence',
            'rule_text': rule_text,
            'conditions': {
                'module': context.get('module')
            },
            'sequence': sequence,
            'evidence': {
                'pattern_frequency': pattern.get('frequency', 0),
                'success_rate': pattern.get('success_rate', 0.0)
            }
        }

    def _generate_generic_rule(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Generate generic rule"""

        return {
            'id': str(uuid.uuid4()),
            'type': 'general',
            'pattern_type': pattern.get('type', 'unknown'),
            'rule_text': f"Pattern detected: {pattern.get('signature')}",
            'conditions': pattern.get('context', {}),
            'evidence': {
                'pattern_frequency': pattern.get('frequency', 0),
                'success_rate': pattern.get('success_rate', 0.0)
            }
        }
