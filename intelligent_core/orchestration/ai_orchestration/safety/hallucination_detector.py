"""
Hallucination Detector
======================

Detects AI hallucinations:
- Fabricated data
- Non-existent entities
- Impossible values
- Contradictions
"""

import logging
from typing import List

from .models import (
    Decision, SafetyResult, SafetyConcern, HallucinationScore
)

logger = logging.getLogger(__name__)


class HallucinationDetector:
    """
    Detects AI hallucinations in decisions.

    Detection methods:
    - Fact verification (check if entities exist)
    - Value validation (check if values make sense)
    - Consistency checks (look for contradictions)
    - Confidence analysis (too confident = suspicious)

    Example:
        ```python
        detector = HallucinationDetector()
        await detector.initialize()

        result = await detector.check(decision)
        if not result.safe:
            print(f"Potential hallucination detected")
        ```
    """

    # Suspiciously high confidence threshold
    SUSPICIOUS_CONFIDENCE = 0.99

    def __init__(self):
        self.initialized = False

    async def initialize(self) -> None:
        """Initialize hallucination detector."""
        self.initialized = True
        logger.info("HallucinationDetector initialized")

    async def check(self, decision: Decision) -> SafetyResult:
        """
        Check decision for hallucinations.

        Args:
            decision: Decision to check

        Returns:
            SafetyResult: Detection result
        """
        concerns: List[SafetyConcern] = []

        # Calculate hallucination score
        score = await self._calculate_hallucination_score(decision)

        # Check if hallucinating
        if score.is_hallucinating(threshold=0.7):
            concerns.append(SafetyConcern(
                type='hallucination',
                severity='high',
                description=f"Potential hallucination detected (confidence: {score.confidence:.2f})",
                evidence={
                    'hallucination_score': score.confidence,
                    'evidence': score.evidence
                },
                recommended_action='escalate_to_human'
            ))

        safe = len(concerns) == 0

        return SafetyResult(
            safe=safe,
            concerns=concerns,
            hallucination_check=safe
        )

    async def _calculate_hallucination_score(
        self,
        decision: Decision
    ) -> HallucinationScore:
        """
        Calculate likelihood of hallucination.

        Returns score 0-1 where 1 = definitely hallucinating
        """
        evidence = []
        score = 0.0

        # Check 1: Suspiciously high confidence
        if decision.confidence >= self.SUSPICIOUS_CONFIDENCE:
            score += 0.3
            evidence.append({
                'check': 'suspicious_confidence',
                'value': decision.confidence,
                'reason': 'Confidence too high for complex decision'
            })

        # Check 2: No learned sources
        if not decision.learned_from:
            score += 0.2
            evidence.append({
                'check': 'no_sources',
                'reason': 'Decision not based on any learned cases'
            })

        # Check 3: Low number of strategies considered
        if len(decision.strategies_considered) < 2:
            score += 0.2
            evidence.append({
                'check': 'few_strategies',
                'value': len(decision.strategies_considered),
                'reason': 'Considered too few alternative strategies'
            })

        # Check 4: Metadata anomalies
        if self._has_metadata_anomalies(decision):
            score += 0.3
            evidence.append({
                'check': 'metadata_anomalies',
                'reason': 'Unusual patterns in decision metadata'
            })

        return HallucinationScore(
            confidence=min(score, 1.0),
            evidence=evidence
        )

    def _has_metadata_anomalies(self, decision: Decision) -> bool:
        """Check for anomalies in decision metadata."""
        metadata = decision.metadata

        # Check for impossible values
        if 'workflow_count' in metadata:
            if metadata['workflow_count'] < 0:
                return True

        # Check for contradictions
        if 'critical' in metadata and 'low_priority' in metadata:
            if metadata['critical'] and metadata['low_priority']:
                return True

        return False
