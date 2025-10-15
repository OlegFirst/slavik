"""
Organization Journey Predictor (with ACE learning!)

Predicts future BCM journey milestones based on similar organizations.

Magic Features:
- 90-day timeline prediction
- Confidence scoring
- Expert recommendations
- Cost estimation
- Challenge forecasting
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID
from collections import defaultdict
import numpy as np
from dataclasses import dataclass
import logging
import sys

# Add platform root for ACE integration
sys.path.insert(0, '/Users/MD/AI-Platform-ISO')
from shared.ace_integration import ACEIntegration

logger = logging.getLogger(__name__)


@dataclass
class OrganizationContext:
    """Organization context for prediction"""
    org_id: UUID
    industry: str
    size: int  # Number of employees
    maturity_level: int  # 1-5
    current_stage: str
    started_at: datetime
    workflows_completed: List[str]
    resources: Dict[str, Any]
    region: str = "unknown"


@dataclass
class PredictedMilestone:
    """Predicted future milestone"""
    milestone: str
    predicted_start_date: datetime
    predicted_duration_days: int
    confidence: float  # 0-1
    reasoning: str
    recommended_experts: List[Dict[str, Any]]
    estimated_cost: Dict[str, Any]
    challenges: List[Dict[str, Any]]


@dataclass
class CertificationPrediction:
    """Certification timeline prediction"""
    predicted_certification_date: datetime
    months_remaining: float
    success_probability: float
    confidence: float
    based_on_orgs_count: int
    key_factors: List[str]


class JourneyPredictor:
    """
    Predicts organization's BCM journey timeline

    Uses pattern matching + basic ML to predict:
    - Next milestones
    - Timeline to certification
    - Resource needs
    - Likely challenges
    """

    def __init__(self, case_library):
        """
        Initialize predictor

        Args:
            case_library: Access to historical journey data
        """
        # ACE Integration for continuous learning
        self.ace = ACEIntegration(module_name="predictive_intelligence")

        self.case_library = case_library
        self.min_similar_orgs = 3
        self.min_similarity_score = 0.5

    async def predict_next_milestones(
        self,
        org_context: OrganizationContext,
        horizon_days: int = 90
    ) -> List[PredictedMilestone]:
        """
        Predict next milestones in organization's journey (with ACE learning!)

        Args:
            org_context: Current organization context
            horizon_days: Prediction horizon (default 90 days)

        Returns:
            List of predicted milestones with confidence scores
        """

        logger.info(
            f"Predicting journey for org {org_context.org_id}, "
            f"horizon: {horizon_days} days"
        )

        # Use ACE for continuous learning of prediction patterns!
        result = await self.ace.execute_with_learning(
            task_type=f"predict_journey_{org_context.industry}",
            base_context={
                "org_id": str(org_context.org_id),
                "industry": org_context.industry,
                "size": org_context.size,
                "maturity_level": org_context.maturity_level,
                "current_stage": org_context.current_stage,
                "horizon_days": horizon_days
            },
            execute_fn=self._predict_next_milestones_impl,
            org_context=org_context,
            horizon_days=horizon_days
        )

        return result.get('milestones', [])

    async def _predict_next_milestones_impl(
        self,
        context: Dict[str, Any],
        org_context: OrganizationContext,
        horizon_days: int
    ) -> Dict[str, Any]:
        """Internal prediction implementation (called by ACE)"""

        # ACE provides enhanced context with learned strategies!
        strategies = context.get('playbook_strategies', [])
        patterns_learned = context.get('known_patterns', [])

        if strategies:
            logger.info(f"🎯 ACE enhanced: {len(strategies)} strategies, {len(patterns_learned)} patterns")

        # Step 1: Find similar organizations
        similar_orgs = await self._find_similar_organizations(org_context)

        if len(similar_orgs) < self.min_similar_orgs:
            logger.warning(
                f"Insufficient similar organizations: {len(similar_orgs)} "
                f"(need {self.min_similar_orgs})"
            )
            return {
                'milestones': [],
                'effectiveness': 0.0
            }

        logger.info(f"Found {len(similar_orgs)} similar organizations")

        # Step 2: Analyze journey patterns
        patterns = await self._analyze_journey_patterns(similar_orgs)

        # Step 3: Generate predictions
        milestones = self._predict_milestones(
            org_context,
            patterns,
            similar_orgs,
            horizon_days
        )

        logger.info(f"Generated {len(milestones)} milestone predictions")

        # Calculate effectiveness based on confidence scores
        if milestones:
            avg_confidence = sum(m.confidence for m in milestones) / len(milestones)
            effectiveness = min(avg_confidence * 1.2, 1.0)  # Boost confidence slightly
        else:
            effectiveness = 0.0

        return {
            'milestones': milestones,
            'effectiveness': effectiveness
        }

    async def predict_certification_timeline(
        self,
        org_context: OrganizationContext
    ) -> Optional[CertificationPrediction]:
        """
        Predict when organization will achieve ISO 22301 certification (with ACE learning!)

        Args:
            org_context: Current organization context

        Returns:
            Certification prediction or None if insufficient data
        """

        logger.info(f"Predicting certification for org {org_context.org_id}")

        # Use ACE for continuous learning of certification predictions!
        result = await self.ace.execute_with_learning(
            task_type=f"predict_certification_{org_context.industry}",
            base_context={
                "org_id": str(org_context.org_id),
                "industry": org_context.industry,
                "size": org_context.size,
                "maturity_level": org_context.maturity_level,
                "current_stage": org_context.current_stage
            },
            execute_fn=self._predict_certification_impl,
            org_context=org_context
        )

        return result.get('prediction')

    async def _predict_certification_impl(
        self,
        context: Dict[str, Any],
        org_context: OrganizationContext
    ) -> Dict[str, Any]:
        """Internal certification prediction implementation (called by ACE)"""

        # ACE provides enhanced context!
        strategies = context.get('playbook_strategies', [])
        if strategies:
            logger.info(f"🎯 ACE enhanced certification prediction with {len(strategies)} strategies")

        # Find similar successful organizations
        similar_orgs = await self._find_similar_organizations(
            org_context,
            certified_only=True
        )

        if len(similar_orgs) < self.min_similar_orgs:
            logger.warning("Insufficient certified organizations for prediction")
            return {
                'prediction': None,
                'effectiveness': 0.0
            }

        # Calculate statistics
        cert_times = [org.get('time_to_cert_months', 0) for org in similar_orgs]
        avg_months = np.mean(cert_times)
        std_months = np.std(cert_times)

        # Adjust for current progress
        current_progress = self._calculate_progress(org_context)
        avg_progress_at_current = self._get_avg_progress_at_stage(
            similar_orgs,
            org_context.current_stage
        )

        if avg_progress_at_current > 0:
            progress_ratio = current_progress / avg_progress_at_current
        else:
            progress_ratio = 1.0

        # Remaining time estimation
        remaining_months = avg_months * (1 - current_progress)

        # Success probability (ratio of successful certifications)
        all_similar = await self._find_similar_organizations(
            org_context,
            certified_only=False
        )
        success_rate = len(similar_orgs) / max(len(all_similar), 1)

        # Confidence (inverse of variance)
        if avg_months > 0:
            confidence = 1 - min(std_months / avg_months, 0.5)
        else:
            confidence = 0.5

        # Predicted date
        predicted_date = datetime.utcnow() + timedelta(days=remaining_months * 30)

        # Key success factors
        key_factors = self._extract_success_factors(similar_orgs)

        prediction = CertificationPrediction(
            predicted_certification_date=predicted_date,
            months_remaining=round(remaining_months, 1),
            success_probability=round(success_rate, 2),
            confidence=round(confidence, 2),
            based_on_orgs_count=len(similar_orgs),
            key_factors=key_factors
        )

        logger.info(
            f"Certification predicted: {predicted_date.strftime('%Y-%m')} "
            f"(confidence: {prediction.confidence})"
        )

        # Effectiveness = confidence (ACE will learn to improve!)
        return {
            'prediction': prediction,
            'effectiveness': confidence
        }

    async def _find_similar_organizations(
        self,
        org_context: OrganizationContext,
        certified_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Find organizations similar to given context

        Similarity based on:
        - Industry (30%)
        - Size (25%)
        - Maturity level (20%)
        - Resources (15%)
        - Region (10%)
        """

        # Get all historical journeys from case library
        all_journeys = await self.case_library.get_all_journeys()

        if certified_only:
            all_journeys = [j for j in all_journeys if j.get('certification_achieved')]

        # Calculate similarity scores
        scored_orgs = []
        for journey in all_journeys:
            similarity = self._calculate_similarity(org_context, journey)

            if similarity >= self.min_similarity_score:
                scored_orgs.append({
                    **journey,
                    'similarity_score': similarity
                })

        # Sort by similarity
        scored_orgs.sort(key=lambda x: x['similarity_score'], reverse=True)

        # Return top matches
        return scored_orgs[:50]  # Max 50 for performance

    def _calculate_similarity(
        self,
        org: OrganizationContext,
        journey: Dict[str, Any]
    ) -> float:
        """
        Calculate similarity score between organization and historical journey

        Returns: 0-1 score
        """

        score = 0.0

        # Industry match (30%)
        journey_industry = journey.get('industry', '').lower()
        if org.industry.lower() == journey_industry:
            score += 0.30
        elif self._is_related_industry(org.industry, journey_industry):
            score += 0.15

        # Size similarity (25%)
        journey_size = journey.get('size', 0)
        if journey_size > 0 and org.size > 0:
            size_ratio = min(org.size, journey_size) / max(org.size, journey_size)
            score += 0.25 * size_ratio

        # Maturity level (20%)
        journey_maturity = journey.get('maturity_level', 0)
        if journey_maturity > 0:
            maturity_diff = abs(org.maturity_level - journey_maturity)
            score += 0.20 * max(0, 1 - (maturity_diff / 4))

        # Resources (15%)
        journey_resources = journey.get('resources', {})
        if org.resources.get('budget') == journey_resources.get('budget'):
            score += 0.10
        if org.resources.get('dedicated_team') == journey_resources.get('dedicated_team'):
            score += 0.05

        # Region (10%)
        journey_region = journey.get('region', 'unknown')
        if org.region == journey_region:
            score += 0.10
        elif org.region != 'unknown' and journey_region != 'unknown':
            score += 0.05  # Same continent/general region

        return round(score, 2)

    def _is_related_industry(self, industry1: str, industry2: str) -> bool:
        """Check if industries are related"""

        RELATED_INDUSTRIES = {
            'healthcare': ['medical', 'hospital', 'clinic', 'pharma'],
            'finance': ['banking', 'insurance', 'fintech'],
            'technology': ['it', 'software', 'telecom'],
            'manufacturing': ['production', 'industrial'],
        }

        industry1 = industry1.lower()
        industry2 = industry2.lower()

        for primary, related in RELATED_INDUSTRIES.items():
            if industry1 == primary and industry2 in related:
                return True
            if industry2 == primary and industry1 in related:
                return True

        return False

    async def _analyze_journey_patterns(
        self,
        similar_orgs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze journey patterns from similar organizations

        Returns patterns: next stages, durations, challenges
        """

        patterns = {
            'next_stages': defaultdict(list),
            'stage_durations': defaultdict(list),
            'challenges': defaultdict(int),
            'success_factors': defaultdict(int),
            'expert_usage': defaultdict(list)
        }

        for org in similar_orgs:
            journey = org.get('journey', [])

            for i, stage in enumerate(journey):
                stage_name = stage.get('stage', 'unknown')

                # Next stage tracking
                if i < len(journey) - 1:
                    next_stage = journey[i + 1]
                    next_name = next_stage.get('stage', 'unknown')

                    # Calculate gap between stages
                    completed = datetime.fromisoformat(stage.get('completed', ''))
                    started_next = datetime.fromisoformat(next_stage.get('started', ''))
                    gap_days = (started_next - completed).days

                    patterns['next_stages'][stage_name].append({
                        'next': next_name,
                        'gap_days': gap_days,
                        'duration': next_stage.get('duration_days', 0)
                    })

                # Duration tracking
                duration = stage.get('duration_days', 0)
                if duration > 0:
                    patterns['stage_durations'][stage_name].append(duration)

                # Expert usage
                if stage.get('expert_used'):
                    patterns['expert_usage'][stage_name].append({
                        'specialty': stage.get('expert_specialty'),
                        'helpful': stage.get('expert_helpful', True)
                    })

            # Challenges
            for challenge in org.get('challenges', []):
                patterns['challenges'][challenge] += 1

            # Success factors (from successful orgs)
            if org.get('success_rate', 0) > 0.8:
                for factor in org.get('success_factors', []):
                    patterns['success_factors'][factor] += 1

        return dict(patterns)

    def _predict_milestones(
        self,
        org_context: OrganizationContext,
        patterns: Dict[str, Any],
        similar_orgs: List[Dict[str, Any]],
        horizon_days: int
    ) -> List[PredictedMilestone]:
        """
        Generate milestone predictions from patterns

        Uses statistical analysis of similar organizations
        """

        milestones = []
        current_date = datetime.utcnow()
        current_stage = org_context.current_stage

        # Get next stage data
        next_stage_data = patterns['next_stages'].get(current_stage, [])

        if not next_stage_data:
            logger.warning(f"No pattern data for stage: {current_stage}")
            return []

        # Aggregate by next stage
        next_stages = defaultdict(list)
        for data in next_stage_data:
            next_stages[data['next']].append(data)

        # For each potential next stage
        for stage, occurrences in next_stages.items():
            frequency = len(occurrences) / len(next_stage_data)

            # Filter low-frequency stages (< 30%)
            if frequency < 0.3:
                continue

            # Statistics
            gaps = [o['gap_days'] for o in occurrences]
            durations = [o['duration'] for o in occurrences]

            avg_gap = np.mean(gaps)
            std_gap = np.std(gaps)
            avg_duration = np.mean(durations)

            # Predicted start date
            predicted_start = current_date + timedelta(days=avg_gap)

            # Skip if beyond horizon
            days_until = (predicted_start - current_date).days
            if days_until > horizon_days:
                continue

            # Confidence calculation
            # Higher frequency + lower variance = higher confidence
            variance_penalty = min(std_gap / max(avg_gap, 1), 0.5)
            confidence = frequency * (1 - variance_penalty)

            # Reasoning text
            reasoning = (
                f"{int(frequency * 100)}% of similar organizations started {stage} "
                f"{int(avg_gap)}±{int(std_gap)} days after {current_stage}"
            )

            # Get expert recommendations
            expert_data = patterns['expert_usage'].get(stage, [])
            recommended_experts = self._recommend_experts(stage, expert_data, org_context)

            # Estimate cost
            estimated_cost = self._estimate_cost(stage, avg_duration, org_context)

            # Predict challenges
            challenges = self._predict_challenges(stage, patterns, similar_orgs)

            milestone = PredictedMilestone(
                milestone=stage,
                predicted_start_date=predicted_start,
                predicted_duration_days=int(avg_duration),
                confidence=round(confidence, 2),
                reasoning=reasoning,
                recommended_experts=recommended_experts,
                estimated_cost=estimated_cost,
                challenges=challenges
            )

            milestones.append(milestone)

        # Sort by start date
        milestones.sort(key=lambda m: m.predicted_start_date)

        return milestones

    def _recommend_experts(
        self,
        stage: str,
        expert_data: List[Dict],
        org_context: OrganizationContext
    ) -> List[Dict[str, Any]]:
        """Recommend experts for stage"""

        if not expert_data:
            return []

        # Count helpful experts by specialty
        specialty_counts = defaultdict(int)
        for usage in expert_data:
            if usage.get('helpful', True):
                specialty = usage.get('specialty', 'general')
                specialty_counts[specialty] += 1

        # Top 3 specialties
        top_specialties = sorted(
            specialty_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        recommendations = []
        for specialty, count in top_specialties:
            recommendations.append({
                'specialty': specialty,
                'usage_count': count,
                'helpful_rate': count / len(expert_data),
                'industry_specific': org_context.industry
            })

        return recommendations

    def _estimate_cost(
        self,
        stage: str,
        duration_days: int,
        org_context: OrganizationContext
    ) -> Dict[str, Any]:
        """Estimate cost for milestone"""

        # Base cost per day (rough estimates)
        BASE_COSTS = {
            'bia': 200,  # $200/day
            'risk': 250,
            'governance': 150,
            'planning': 200,
            'plans': 180,
            'response': 160,
            'validation': 220,
            'compliance': 300
        }

        base_cost_per_day = BASE_COSTS.get(stage, 200)
        estimated_total = base_cost_per_day * duration_days

        # Adjust for organization size
        if org_context.size > 500:
            estimated_total *= 1.3
        elif org_context.size < 50:
            estimated_total *= 0.7

        return {
            'estimated_min': int(estimated_total * 0.8),
            'estimated_max': int(estimated_total * 1.2),
            'currency': 'USD',
            'includes': ['internal_staff_time', 'tools', 'templates'],
            'excludes': ['external_consultant']
        }

    def _predict_challenges(
        self,
        stage: str,
        patterns: Dict[str, Any],
        similar_orgs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Predict likely challenges for stage"""

        # Get challenges from similar orgs
        all_challenges = patterns.get('challenges', {})

        # Filter relevant to stage
        stage_challenges = []
        for org in similar_orgs:
            for challenge in org.get('challenges', []):
                if challenge.get('stage') == stage:
                    stage_challenges.append(challenge)

        if not stage_challenges:
            return []

        # Count frequency
        challenge_counts = defaultdict(int)
        for challenge in stage_challenges:
            challenge_counts[challenge.get('type', 'unknown')] += 1

        # Top 3 challenges
        top_challenges = sorted(
            challenge_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        predictions = []
        for challenge_type, count in top_challenges:
            probability = count / len(similar_orgs)

            predictions.append({
                'challenge_type': challenge_type,
                'probability': round(probability, 2),
                'frequency': count,
                'mitigation_strategies': self._get_mitigation_strategies(challenge_type)
            })

        return predictions

    def _get_mitigation_strategies(self, challenge_type: str) -> List[str]:
        """Get mitigation strategies for challenge"""

        STRATEGIES = {
            'resource_constraints': [
                'Allocate dedicated time blocks',
                'Prioritize critical path activities',
                'Consider part-time external support'
            ],
            'stakeholder_engagement': [
                'Schedule executive sponsor sessions',
                'Create clear communication plan',
                'Demonstrate quick wins'
            ],
            'data_availability': [
                'Start with available data, iterate',
                'Use templates and examples',
                'Leverage automated tools'
            ],
            'complexity': [
                'Break into smaller phases',
                'Use proven frameworks',
                'Engage experienced consultant'
            ]
        }

        return STRATEGIES.get(challenge_type, [
            'Review similar case studies',
            'Consult with expert',
            'Leverage platform resources'
        ])

    def _calculate_progress(self, org_context: OrganizationContext) -> float:
        """Calculate current progress (0-1)"""

        # Simplified progress calculation
        STAGE_WEIGHTS = {
            'governance': 0.10,
            'bia': 0.15,
            'risk': 0.15,
            'planning': 0.15,
            'plans': 0.20,
            'response': 0.10,
            'validation': 0.10,
            'compliance': 0.05
        }

        total_progress = 0.0
        for completed in org_context.workflows_completed:
            total_progress += STAGE_WEIGHTS.get(completed, 0.05)

        return min(total_progress, 1.0)

    def _get_avg_progress_at_stage(
        self,
        similar_orgs: List[Dict[str, Any]],
        stage: str
    ) -> float:
        """Get average progress when orgs reached this stage"""

        progresses = []
        for org in similar_orgs:
            journey = org.get('journey', [])
            for i, s in enumerate(journey):
                if s.get('stage') == stage:
                    # Progress = proportion of journey completed
                    progress = i / len(journey)
                    progresses.append(progress)
                    break

        return np.mean(progresses) if progresses else 0.5

    def _extract_success_factors(
        self,
        similar_orgs: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract key success factors from similar orgs"""

        factor_counts = defaultdict(int)

        for org in similar_orgs:
            for factor in org.get('success_factors', []):
                factor_counts[factor] += 1

        # Top 5 factors
        top_factors = sorted(
            factor_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return [factor for factor, _ in top_factors]
