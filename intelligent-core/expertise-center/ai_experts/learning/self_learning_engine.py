"""
Self-Learning Engine

Automatically learns from completed workflows to improve predictions and recommendations.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SelfLearningEngine:
    """
    Self-Learning Engine

    Learning workflow:
    1. Workflow completed → Auto-collect (anonymized)
    2. Extract patterns (ML)
    3. Update benchmarks
    4. IF pattern frequency > 10 AND success > 80%
       → Suggest new rule (human approval)
    """

    def __init__(
        self,
        pattern_extractor=None,
        rule_generator=None,
        min_pattern_frequency: int = 10,
        min_success_rate: float = 0.8
    ):
        """
        Initialize self-learning engine

        Args:
            pattern_extractor: PatternExtractor instance
            rule_generator: RuleGenerator instance
            min_pattern_frequency: Minimum pattern occurrences for rule generation
            min_success_rate: Minimum success rate for pattern
        """
        self.pattern_extractor = pattern_extractor
        self.rule_generator = rule_generator
        self.min_pattern_frequency = min_pattern_frequency
        self.min_success_rate = min_success_rate

        self.learned_patterns = []
        self.pending_rules = []
        self.approved_rules = []

    async def learn_from_workflow_completion(
        self,
        workflow_case: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Learn from completed workflow

        Args:
            workflow_case: Completed workflow data

        Returns:
            Learning results
        """

        logger.info(f"Learning from workflow: {workflow_case.get('id')}")

        # Step 1: Anonymize data
        anonymized_case = self._anonymize_case(workflow_case)

        # Step 2: Extract patterns
        patterns = await self._extract_patterns(anonymized_case)

        # Step 3: Update benchmarks
        await self._update_benchmarks(anonymized_case)

        # Step 4: Check if patterns warrant new rules
        suggested_rules = await self._evaluate_patterns_for_rules(patterns)

        result = {
            'case_id': workflow_case.get('id'),
            'patterns_extracted': len(patterns),
            'patterns': patterns,
            'benchmarks_updated': True,
            'suggested_rules': suggested_rules,
            'learning_status': 'success'
        }

        # Publish learning event
        await self._publish_learning_event(result)

        return result

    def _anonymize_case(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize sensitive information

        Args:
            case: Workflow case

        Returns:
            Anonymized case
        """

        anonymized = case.copy()

        # Remove PII
        sensitive_fields = [
            'user_id', 'user_name', 'user_email',
            'org_name', 'org_id', 'contact_info'
        ]

        for field in sensitive_fields:
            if field in anonymized:
                del anonymized[field]

        # Keep only aggregate/categorical data
        keep_fields = [
            'industry', 'org_size', 'maturity', 'module',
            'duration_hours', 'challenges', 'success',
            'strategies_used', 'tools_used', 'outcomes'
        ]

        anonymized = {
            k: v for k, v in anonymized.items()
            if k in keep_fields
        }

        return anonymized

    async def _extract_patterns(
        self,
        case: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract patterns from case"""

        if not self.pattern_extractor:
            from .pattern_extractor import PatternExtractor
            self.pattern_extractor = PatternExtractor()

        patterns = await self.pattern_extractor.extract_patterns(case)

        # Store patterns
        for pattern in patterns:
            self.learned_patterns.append({
                **pattern,
                'learned_at': datetime.now().isoformat()
            })

        return patterns

    async def _update_benchmarks(self, case: Dict[str, Any]):
        """Update performance benchmarks"""

        # This would update database with new benchmark data
        logger.info("Benchmarks updated (implementation pending)")

    async def _evaluate_patterns_for_rules(
        self,
        patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Evaluate if patterns should become rules

        Args:
            patterns: Extracted patterns

        Returns:
            Suggested rules
        """

        suggested_rules = []

        for pattern in patterns:
            # Count pattern frequency
            frequency = self._count_pattern_frequency(pattern)

            # Calculate success rate
            success_rate = self._calculate_pattern_success_rate(pattern)

            # Check if meets thresholds
            if frequency >= self.min_pattern_frequency and success_rate >= self.min_success_rate:
                # Generate rule
                if not self.rule_generator:
                    from .rule_generator import RuleGenerator
                    self.rule_generator = RuleGenerator()

                rule = await self.rule_generator.generate_rule(pattern)

                rule['frequency'] = frequency
                rule['success_rate'] = success_rate
                rule['status'] = 'pending_approval'

                suggested_rules.append(rule)
                self.pending_rules.append(rule)

        logger.info(f"Generated {len(suggested_rules)} rule suggestions")

        return suggested_rules

    def _count_pattern_frequency(self, pattern: Dict[str, Any]) -> int:
        """Count how many times pattern appears in learned data"""

        pattern_type = pattern.get('type')
        pattern_signature = pattern.get('signature')

        count = 0

        for learned_pattern in self.learned_patterns:
            if (learned_pattern.get('type') == pattern_type and
                learned_pattern.get('signature') == pattern_signature):
                count += 1

        return count

    def _calculate_pattern_success_rate(self, pattern: Dict[str, Any]) -> float:
        """Calculate success rate for pattern"""

        pattern_type = pattern.get('type')
        pattern_signature = pattern.get('signature')

        matching_patterns = [
            p for p in self.learned_patterns
            if (p.get('type') == pattern_type and
                p.get('signature') == pattern_signature)
        ]

        if not matching_patterns:
            return 0.0

        successful = sum(
            1 for p in matching_patterns
            if p.get('success', False)
        )

        return successful / len(matching_patterns)

    async def _publish_learning_event(self, learning_result: Dict[str, Any]):
        """Publish learning event to event bus"""

        # This would publish to event bus
        logger.info("Learning event published (implementation pending)")

    async def approve_rule(self, rule_id: str) -> Dict[str, Any]:
        """
        Approve pending rule

        Args:
            rule_id: Rule ID

        Returns:
            Approval result
        """

        # Find pending rule
        rule = next(
            (r for r in self.pending_rules if r.get('id') == rule_id),
            None
        )

        if not rule:
            return {
                'status': 'error',
                'error': 'Rule not found'
            }

        # Move to approved
        rule['status'] = 'approved'
        rule['approved_at'] = datetime.now().isoformat()

        self.approved_rules.append(rule)
        self.pending_rules = [r for r in self.pending_rules if r.get('id') != rule_id]

        logger.info(f"Rule approved: {rule_id}")

        return {
            'status': 'success',
            'rule': rule
        }

    async def reject_rule(self, rule_id: str, reason: str) -> Dict[str, Any]:
        """
        Reject pending rule

        Args:
            rule_id: Rule ID
            reason: Rejection reason

        Returns:
            Rejection result
        """

        # Remove from pending
        rule = next(
            (r for r in self.pending_rules if r.get('id') == rule_id),
            None
        )

        if not rule:
            return {
                'status': 'error',
                'error': 'Rule not found'
            }

        rule['status'] = 'rejected'
        rule['rejected_at'] = datetime.now().isoformat()
        rule['rejection_reason'] = reason

        self.pending_rules = [r for r in self.pending_rules if r.get('id') != rule_id]

        logger.info(f"Rule rejected: {rule_id}")

        return {
            'status': 'success',
            'rule': rule
        }

    def get_pending_rules(self) -> List[Dict[str, Any]]:
        """Get all pending rules"""
        return self.pending_rules

    def get_approved_rules(self) -> List[Dict[str, Any]]:
        """Get all approved rules"""
        return self.approved_rules

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""

        return {
            'total_patterns_learned': len(self.learned_patterns),
            'pending_rules': len(self.pending_rules),
            'approved_rules': len(self.approved_rules),
            'learning_active': True
        }
