"""
Pattern Extractor

Extracts recurring patterns from workflow data using ML techniques.
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class PatternExtractor:
    """
    Pattern Extractor

    Extracts patterns such as:
    - Successful strategies for specific scenarios
    - Common challenges and resolutions
    - Optimal workflow sequences
    - Resource allocation patterns
    """

    def __init__(self):
        """Initialize pattern extractor"""
        self.pattern_types = [
            'successful_strategy',
            'common_challenge',
            'optimal_sequence',
            'resource_pattern'
        ]

    async def extract_patterns(self, case: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract patterns from case

        Args:
            case: Workflow case data

        Returns:
            List of extracted patterns
        """

        patterns = []

        # Extract strategy patterns
        if case.get('success') and case.get('strategies_used'):
            strategy_pattern = self._extract_strategy_pattern(case)
            if strategy_pattern:
                patterns.append(strategy_pattern)

        # Extract challenge patterns
        if case.get('challenges'):
            challenge_patterns = self._extract_challenge_patterns(case)
            patterns.extend(challenge_patterns)

        # Extract sequence patterns
        if case.get('workflow_sequence'):
            sequence_pattern = self._extract_sequence_pattern(case)
            if sequence_pattern:
                patterns.append(sequence_pattern)

        return patterns

    def _extract_strategy_pattern(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """Extract successful strategy pattern"""

        strategies = case.get('strategies_used', [])
        if not strategies:
            return None

        # Create pattern signature
        context = {
            'industry': case.get('industry'),
            'org_size': case.get('org_size'),
            'module': case.get('module')
        }

        return {
            'type': 'successful_strategy',
            'signature': f"{context['industry']}_{context['org_size']}_{context['module']}",
            'context': context,
            'strategies': strategies,
            'outcome': case.get('outcomes', {}),
            'success': case.get('success', False),
            'duration_hours': case.get('duration_hours')
        }

    def _extract_challenge_patterns(self, case: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract challenge and resolution patterns"""

        challenges = case.get('challenges', [])
        patterns = []

        for challenge in challenges:
            pattern = {
                'type': 'common_challenge',
                'signature': f"{case.get('industry', 'unknown')}_{challenge.get('type', 'general')}",
                'challenge': challenge.get('description'),
                'resolution': challenge.get('resolution'),
                'context': {
                    'industry': case.get('industry'),
                    'org_size': case.get('org_size'),
                    'module': case.get('module')
                },
                'success': challenge.get('resolved', False)
            }
            patterns.append(pattern)

        return patterns

    def _extract_sequence_pattern(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """Extract workflow sequence pattern"""

        sequence = case.get('workflow_sequence', [])
        if not sequence:
            return None

        return {
            'type': 'optimal_sequence',
            'signature': f"{case.get('module', 'unknown')}_sequence",
            'sequence': sequence,
            'duration_hours': case.get('duration_hours'),
            'success': case.get('success', False),
            'context': {
                'module': case.get('module'),
                'org_size': case.get('org_size')
            }
        }
