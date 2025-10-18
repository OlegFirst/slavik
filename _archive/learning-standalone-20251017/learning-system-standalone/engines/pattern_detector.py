"""
Pattern Detection Engine

Detects patterns from exercise results, simulations, AI analyses
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import statistics

logger = logging.getLogger(__name__)


class PatternDetector:
    """
    Detects patterns in BCM learning data

    Pattern types:
    - Recurring failures
    - Success patterns
    - Performance trends
    - Anomalies
    """

    def __init__(self):
        self.min_occurrences = 3  # Minimum occurrences to consider a pattern
        self.confidence_threshold = 0.7  # Minimum confidence

    def detect_patterns(self, exercise_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect all pattern types from exercise results

        Returns:
            List of detected patterns
        """
        if not exercise_results:
            return []

        patterns = []

        # Detect different pattern types
        patterns.extend(self._detect_failure_patterns(exercise_results))
        patterns.extend(self._detect_success_patterns(exercise_results))
        patterns.extend(self._detect_trend_patterns(exercise_results))
        patterns.extend(self._detect_anomaly_patterns(exercise_results))

        # Filter by confidence
        patterns = [p for p in patterns if p.get('confidence', 0) >= self.confidence_threshold]

        logger.info(f"Detected {len(patterns)} patterns from {len(exercise_results)} exercise results")

        return patterns

    def _detect_failure_patterns(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect recurring failure patterns"""
        patterns = []

        # Aggregate all issues
        all_issues = []
        for result in results:
            issues = result.get('key_issues', [])
            all_issues.extend(issues)

        # Count issue frequency
        issue_counts = Counter(all_issues)

        # Identify frequent issues
        for issue, count in issue_counts.items():
            if count >= self.min_occurrences:
                confidence = min(count / len(results), 1.0)

                patterns.append({
                    'pattern_type': 'failure',
                    'pattern_category': 'exercise',
                    'pattern_name': f"Recurring Issue: {issue}",
                    'description': f"This issue has occurred in {count} out of {len(results)} exercises",
                    'occurrence_count': count,
                    'confidence': confidence,
                    'severity': self._assess_severity(count, len(results)),
                    'affected_areas': self._extract_affected_areas(results, issue),
                    'recommended_actions': [
                        f"Investigate root cause of '{issue}'",
                        f"Develop mitigation strategy",
                        f"Add training on this specific issue"
                    ]
                })

        return patterns

    def _detect_success_patterns(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect successful response patterns"""
        patterns = []

        # Aggregate all strengths
        all_strengths = []
        for result in results:
            strengths = result.get('strengths', [])
            all_strengths.extend(strengths)

        # Count strength frequency
        strength_counts = Counter(all_strengths)

        # Identify consistent strengths
        for strength, count in strength_counts.items():
            if count >= self.min_occurrences:
                confidence = min(count / len(results), 1.0)

                patterns.append({
                    'pattern_type': 'success',
                    'pattern_category': 'exercise',
                    'pattern_name': f"Consistent Strength: {strength}",
                    'description': f"This strength demonstrated in {count} out of {len(results)} exercises",
                    'occurrence_count': count,
                    'confidence': confidence,
                    'severity': 'low',  # Success patterns are low severity
                    'recommended_actions': [
                        f"Document best practices for '{strength}'",
                        f"Share success across organization",
                        f"Build on this strength for advanced scenarios"
                    ]
                })

        return patterns

    def _detect_trend_patterns(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect performance trends over time"""
        patterns = []

        if len(results) < 3:
            return patterns

        # Sort by date
        sorted_results = sorted(results, key=lambda x: x.get('conducted_at', datetime.min))

        # Extract scores over time
        scores = [r.get('overall_score', 0) for r in sorted_results]

        # Calculate trend
        if len(scores) >= 3:
            # Simple linear trend detection
            avg_first_half = statistics.mean(scores[:len(scores)//2])
            avg_second_half = statistics.mean(scores[len(scores)//2:])

            trend_direction = "improving" if avg_second_half > avg_first_half else "declining"
            trend_magnitude = abs(avg_second_half - avg_first_half)

            if trend_magnitude > 5:  # Significant trend (>5 points change)
                patterns.append({
                    'pattern_type': 'trend',
                    'pattern_category': 'exercise',
                    'pattern_name': f"Performance {trend_direction.capitalize()}",
                    'description': f"Exercise scores have been {trend_direction} (Δ {trend_magnitude:.1f} points)",
                    'occurrence_count': len(results),
                    'confidence': min(trend_magnitude / 20, 1.0),
                    'severity': 'high' if trend_direction == 'declining' else 'low',
                    'evidence_data': {
                        'avg_first_half': avg_first_half,
                        'avg_second_half': avg_second_half,
                        'trend_direction': trend_direction
                    },
                    'recommended_actions': [
                        f"Investigate cause of {trend_direction} performance",
                        f"{'Address declining areas' if trend_direction == 'declining' else 'Reinforce improvements'}",
                        f"Monitor trend continuation"
                    ]
                })

        return patterns

    def _detect_anomaly_patterns(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalous results"""
        patterns = []

        if len(results) < 5:
            return patterns

        # Extract scores
        scores = [r.get('overall_score', 0) for r in results]

        if len(scores) < 5:
            return patterns

        # Calculate statistics
        mean_score = statistics.mean(scores)
        stdev_score = statistics.stdev(scores) if len(scores) > 1 else 0

        # Detect outliers (>2 standard deviations)
        for result in results:
            score = result.get('overall_score', 0)

            if stdev_score > 0:
                z_score = abs((score - mean_score) / stdev_score)

                if z_score > 2:
                    patterns.append({
                        'pattern_type': 'anomaly',
                        'pattern_category': 'exercise',
                        'pattern_name': f"Anomalous Result: {result.get('exercise_name', 'Unknown')}",
                        'description': f"Score {score} significantly differs from average {mean_score:.1f}",
                        'occurrence_count': 1,
                        'confidence': min(z_score / 3, 1.0),
                        'severity': 'medium',
                        'evidence_data': {
                            'score': score,
                            'mean': mean_score,
                            'stdev': stdev_score,
                            'z_score': z_score
                        },
                        'recommended_actions': [
                            f"Investigate why this exercise was {'unusually good' if score > mean_score else 'unusually poor'}",
                            f"Review scenario difficulty",
                            f"Check for external factors"
                        ]
                    })

        return patterns

    def _assess_severity(self, count: int, total: int) -> str:
        """Assess severity based on occurrence rate"""
        rate = count / total if total > 0 else 0

        if rate >= 0.7:
            return 'critical'
        elif rate >= 0.5:
            return 'high'
        elif rate >= 0.3:
            return 'medium'
        else:
            return 'low'

    def _extract_affected_areas(self, results: List[Dict[str, Any]], issue: str) -> List[str]:
        """Extract areas affected by an issue"""
        affected = set()

        for result in results:
            if issue in result.get('key_issues', []):
                # Extract scenario type, roles, etc.
                scenario_type = result.get('scenario_type', 'unknown')
                affected.add(f"scenario:{scenario_type}")

                roles = result.get('roles_involved', [])
                for role in roles:
                    affected.add(f"role:{role}")

        return list(affected)[:5]  # Top 5


class ScenarioAnalyzer:
    """
    Analyzes scenario performance over time

    Builds scenario-specific learning models
    """

    def analyze_scenario(self, scenario_type: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze all executions of a scenario type

        Returns:
            Aggregated scenario learning data
        """
        if not results:
            return {}

        # Filter results for this scenario type
        scenario_results = [r for r in results if r.get('scenario_type') == scenario_type]

        if not scenario_results:
            return {}

        # Calculate aggregated metrics
        scores = [r.get('overall_score', 0) for r in scenario_results]
        response_times = [r.get('response_time_minutes', 0) for r in scenario_results if r.get('response_time_minutes')]

        # Success threshold (e.g., 70%)
        success_threshold = 70
        successes = sum(1 for s in scores if s >= success_threshold)

        # Extract common issues and strengths
        all_issues = []
        all_strengths = []

        for r in scenario_results:
            all_issues.extend(r.get('key_issues', []))
            all_strengths.extend(r.get('strengths', []))

        issue_counts = Counter(all_issues)
        strength_counts = Counter(all_strengths)

        # Calculate improvement trend
        if len(scores) >= 2:
            first_half_avg = statistics.mean(scores[:len(scores)//2])
            second_half_avg = statistics.mean(scores[len(scores)//2:])
            improvement = second_half_avg - first_half_avg
        else:
            improvement = 0

        return {
            'scenario_type': scenario_type,
            'execution_count': len(scenario_results),
            'avg_score': statistics.mean(scores) if scores else 0,
            'avg_response_time': statistics.mean(response_times) if response_times else None,
            'success_rate': (successes / len(scenario_results)) * 100 if scenario_results else 0,
            'common_failures': [{'issue': issue, 'count': count} for issue, count in issue_counts.most_common(5)],
            'common_strengths': [{'strength': strength, 'count': count} for strength, count in strength_counts.most_common(5)],
            'improvement_trend': improvement,
            'recommended_improvements': self._generate_recommendations(issue_counts, scores),
            'first_execution': min(r.get('conducted_at') for r in scenario_results),
            'last_execution': max(r.get('conducted_at') for r in scenario_results)
        }

    def _generate_recommendations(self, issue_counts: Counter, scores: List[float]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []

        # Address most common issues
        if issue_counts:
            top_issue = issue_counts.most_common(1)[0][0]
            recommendations.append(f"Focus training on: {top_issue}")

        # Performance-based recommendations
        if scores:
            avg_score = statistics.mean(scores)

            if avg_score < 60:
                recommendations.append("Consider simplifying scenario or increasing preparation time")
            elif avg_score < 75:
                recommendations.append("Provide additional pre-exercise briefing materials")
            elif avg_score >= 85:
                recommendations.append("Increase scenario complexity to maintain challenge")

        return recommendations
