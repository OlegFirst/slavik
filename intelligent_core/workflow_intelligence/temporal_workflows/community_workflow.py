#!/usr/bin/env python3
"""
Community Intelligence Workflow - Temporal Durable Execution

Provides fault-tolerant workflows for Community Intelligence:
- Case contribution analysis
- Community insights generation
- Top contributor identification
- Knowledge sharing patterns
- Case quality validation

Patterns:
- Retry policies для fault tolerance
- Long-running workflows с state persistence
- Analytics aggregation
"""

import asyncio
import logging
from datetime import timedelta, datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from temporalio import workflow, activity
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError

logger = logging.getLogger(__name__)


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class CommunityInsightsConfig:
    """Configuration for community insights generation"""
    period: str = "weekly"  # 'daily', 'weekly', 'monthly'
    min_contributions: int = 5
    include_patterns: bool = True


@dataclass
class CommunityInsightsResult:
    """Result of community insights analysis"""
    insights_generated: int
    top_contributors: List[Dict]
    total_contributions: int
    avg_quality_score: float
    sharing_patterns: List[Dict]


@dataclass
class CaseContributionConfig:
    """Configuration for case contribution"""
    case_id: str
    org_id: str
    validate_quality: bool = True


# ============================================================================
# Activities
# ============================================================================

@activity.defn
async def analyze_contributions(config: CommunityInsightsConfig) -> Dict[str, Any]:
    """Analyze community contributions for period"""

    logger.info(f"📊 Analyzing community contributions: {config.period}")

    # Simulated analysis (real implementation would query database)
    result = {
        'total_contributions': 150,
        'total_contributors': 45,
        'avg_quality_score': 8.2,
        'period': config.period
    }

    return result


@activity.defn
async def identify_top_contributors(period: str, limit: int = 10) -> List[Dict]:
    """Identify top contributors for period"""

    logger.info(f"🏆 Identifying top contributors: {period}")

    # Simulated top contributors (real implementation would query database)
    contributors = [
        {'org_id': f'org-{i}', 'contributions': 20-i, 'avg_quality': 8.5-i*0.1}
        for i in range(limit)
    ]

    return contributors


@activity.defn
async def detect_sharing_patterns(contributions_data: Dict) -> List[Dict]:
    """Detect knowledge sharing patterns"""

    logger.info("🔍 Detecting sharing patterns")

    # Simulated pattern detection
    patterns = [
        {'pattern': 'cross_industry_sharing', 'frequency': 25},
        {'pattern': 'regional_collaboration', 'frequency': 18},
        {'pattern': 'domain_expertise_exchange', 'frequency': 30}
    ]

    return patterns


@activity.defn
async def generate_insights(
    contributions_data: Dict,
    top_contributors: List[Dict],
    patterns: List[Dict]
) -> List[Dict]:
    """Generate actionable insights from community data"""

    logger.info("💡 Generating community insights")

    insights = []

    # Quality insights
    if contributions_data['avg_quality_score'] > 8.0:
        insights.append({
            'type': 'quality_high',
            'severity': 'info',
            'message': f"Community quality score is excellent: {contributions_data['avg_quality_score']:.1f}/10"
        })

    # Contribution insights
    if contributions_data['total_contributions'] > 100:
        insights.append({
            'type': 'engagement_high',
            'severity': 'info',
            'message': f"High community engagement: {contributions_data['total_contributions']} contributions"
        })

    # Pattern insights
    for pattern in patterns:
        if pattern['frequency'] > 20:
            insights.append({
                'type': 'pattern_detected',
                'severity': 'info',
                'message': f"Strong pattern: {pattern['pattern']} ({pattern['frequency']} occurrences)"
            })

    return insights


@activity.defn
async def validate_case_quality(case_id: str, org_id: str) -> Dict[str, Any]:
    """Validate quality of contributed case"""

    logger.info(f"✅ Validating case quality: {case_id}")

    # Simulated validation (real implementation would check criteria)
    result = {
        'case_id': case_id,
        'quality_score': 8.5,
        'completeness': 0.95,
        'usefulness': 0.90,
        'approved': True
    }

    return result


@activity.defn
async def store_contribution(case_id: str, org_id: str, quality_data: Dict) -> str:
    """Store validated contribution in database"""

    logger.info(f"💾 Storing contribution: {case_id}")

    contribution_id = f"contrib-{case_id}"

    # Real implementation would save to database
    logger.info(f"✅ Contribution stored: {contribution_id}")

    return contribution_id


# ============================================================================
# Workflows
# ============================================================================

@workflow.defn
class CommunityInsightsWorkflow:
    """
    Weekly/Monthly community insights generation

    Analyzes contributions, identifies patterns, generates insights
    """

    @workflow.run
    async def run(self, config: CommunityInsightsConfig) -> CommunityInsightsResult:
        """
        Main workflow execution

        Steps:
        1. Analyze contributions for period
        2. Identify top contributors
        3. Detect sharing patterns
        4. Generate insights
        5. Return results
        """

        # Retry policy for all activities
        retry_policy = RetryPolicy(
            maximum_attempts=3,
            initial_interval=timedelta(seconds=1),
            backoff_coefficient=2.0,
            maximum_interval=timedelta(seconds=10)
        )

        # Step 1: Analyze contributions
        contributions_data = await workflow.execute_activity(
            analyze_contributions,
            config,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy
        )

        # Step 2: Identify top contributors
        top_contributors = await workflow.execute_activity(
            identify_top_contributors,
            args=[config.period, 10],
            start_to_close_timeout=timedelta(minutes=3),
            retry_policy=retry_policy
        )

        # Step 3: Detect patterns (if enabled)
        sharing_patterns = []
        if config.include_patterns:
            sharing_patterns = await workflow.execute_activity(
                detect_sharing_patterns,
                contributions_data,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )

        # Step 4: Generate insights
        insights = await workflow.execute_activity(
            generate_insights,
            args=[contributions_data, top_contributors, sharing_patterns],
            start_to_close_timeout=timedelta(minutes=3),
            retry_policy=retry_policy
        )

        # Build result
        result = CommunityInsightsResult(
            insights_generated=len(insights),
            top_contributors=top_contributors,
            total_contributions=contributions_data['total_contributions'],
            avg_quality_score=contributions_data['avg_quality_score'],
            sharing_patterns=sharing_patterns
        )

        logger.info(f"✅ Community insights workflow complete: {result.insights_generated} insights generated")

        return result


@workflow.defn
class CaseContributionWorkflow:
    """
    Case contribution and validation workflow

    Validates and stores contributed cases with quality checks
    """

    @workflow.run
    async def run(self, config: CaseContributionConfig) -> Dict[str, Any]:
        """
        Contribution workflow

        Steps:
        1. Validate case quality (if enabled)
        2. Store contribution
        3. Return contribution ID
        """

        retry_policy = RetryPolicy(
            maximum_attempts=3,
            initial_interval=timedelta(seconds=1),
            backoff_coefficient=2.0
        )

        # Step 1: Validate quality
        quality_data = {}
        if config.validate_quality:
            quality_data = await workflow.execute_activity(
                validate_case_quality,
                args=[config.case_id, config.org_id],
                start_to_close_timeout=timedelta(minutes=3),
                retry_policy=retry_policy
            )

            if not quality_data.get('approved'):
                raise ApplicationError(
                    f"Case quality validation failed: score {quality_data.get('quality_score')}",
                    non_retryable=True
                )

        # Step 2: Store contribution
        contribution_id = await workflow.execute_activity(
            store_contribution,
            args=[config.case_id, config.org_id, quality_data],
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=retry_policy
        )

        return {
            'contribution_id': contribution_id,
            'case_id': config.case_id,
            'org_id': config.org_id,
            'quality_score': quality_data.get('quality_score', 0),
            'status': 'approved'
        }


# ============================================================================
# Worker Registration
# ============================================================================

def register_workflows(worker):
    """Register all Community Intelligence workflows with worker"""
    worker.register_workflow(CommunityInsightsWorkflow)
    worker.register_workflow(CaseContributionWorkflow)

    logger.info("✅ Registered Community Intelligence workflows")


def register_activities(worker):
    """Register all Community Intelligence activities with worker"""
    worker.register_activity(analyze_contributions)
    worker.register_activity(identify_top_contributors)
    worker.register_activity(detect_sharing_patterns)
    worker.register_activity(generate_insights)
    worker.register_activity(validate_case_quality)
    worker.register_activity(store_contribution)

    logger.info("✅ Registered Community Intelligence activities (6 activities)")
