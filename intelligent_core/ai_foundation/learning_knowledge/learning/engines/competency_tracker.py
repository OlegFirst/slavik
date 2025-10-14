"""
Competency Tracking Engine

Tracks individual and team BCM competencies with skills decay analysis
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from learning_knowledge.monitoring.metrics import (
    track_competency_assessment,
    track_learning_operation
)

logger = logging.getLogger(__name__)


class CompetencyTracker:
    """
    Tracks user competencies across BCM domains

    Core Competencies:
    - BIA Execution
    - Risk Assessment
    - Exercise Facilitation
    - Audit Management
    - Plan Development
    - Incident Response
    """

    def __init__(self):
        self.competency_weights = {
            'bia_execution': 1.0,
            'risk_assessment': 1.0,
            'exercise_facilitation': 1.2,  # Higher weight
            'audit_management': 1.3,  # Higher weight
            'plan_development': 1.0,
            'incident_response': 1.1
        }

        self.decay_thresholds = {
            'low': 30,      # < 30 days since last exercise
            'medium': 90,   # 30-90 days
            'high': 180,    # 90-180 days
            'critical': 365 # > 180 days
        }

    @track_competency_assessment
    @track_learning_operation(engine="competency_tracker", operation="calculate_user_competency")
    def calculate_user_competency(
        self,
        user_id: str,
        exercise_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive user competency profile

        Returns:
            Competency profile with scores, trends, decay risk
        """
        if not exercise_results:
            return self._empty_profile(user_id)

        # Filter results for this user
        user_results = [r for r in exercise_results if r.get('participant_user_id') == user_id]

        if not user_results:
            return self._empty_profile(user_id)

        # Calculate core competencies
        core_competencies = self._calculate_core_competencies(user_results)

        # Calculate scenario-specific competencies
        scenario_competencies = self._calculate_scenario_competencies(user_results)

        # Calculate overall metrics
        scores = [r.get('overall_score', 0) for r in user_results]
        avg_score = statistics.mean(scores) if scores else 0

        # Calculate improvement trend
        improvement_trend = self._calculate_improvement_trend(scores)

        # Skills decay analysis
        last_exercise = max(r.get('conducted_at', datetime.min) for r in user_results)
        decay_analysis = self._analyze_decay_risk(last_exercise)

        return {
            'user_id': user_id,
            'core_competencies': core_competencies,
            'scenario_competencies': scenario_competencies,
            'total_exercises': len(user_results),
            'avg_exercise_score': round(avg_score, 2),
            'improvement_trend': improvement_trend,
            'decay_risk': decay_analysis,
            'certifications': [],  # To be populated from external data
            'last_exercise_date': last_exercise.isoformat() if last_exercise != datetime.min else None
        }

    def _calculate_core_competencies(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate scores for core BCM competencies"""
        competencies = {}

        # BIA Execution (from BIA_related exercises)
        bia_results = [r for r in results if 'bia' in r.get('exercise_type', '').lower()]
        if bia_results:
            competencies['bia_execution'] = {
                'score': round(statistics.mean([r.get('overall_score', 0) for r in bia_results]), 2),
                'exercise_count': len(bia_results)
            }

        # Risk Assessment
        risk_results = [r for r in results if 'risk' in r.get('exercise_type', '').lower()]
        if risk_results:
            competencies['risk_assessment'] = {
                'score': round(statistics.mean([r.get('overall_score', 0) for r in risk_results]), 2),
                'exercise_count': len(risk_results)
            }

        # Exercise Facilitation (from facilitated exercises)
        facilitation_results = [r for r in results if r.get('role') == 'facilitator']
        if facilitation_results:
            competencies['exercise_facilitation'] = {
                'score': round(statistics.mean([r.get('overall_score', 0) for r in facilitation_results]), 2),
                'exercises_facilitated': len(facilitation_results)
            }

        # Incident Response (from incident exercises)
        incident_results = [r for r in results if r.get('scenario_type', '') in ['cyber', 'physical', 'operational']]
        if incident_results:
            competencies['incident_response'] = {
                'score': round(statistics.mean([r.get('overall_score', 0) for r in incident_results]), 2),
                'incidents_handled': len(incident_results)
            }

        return competencies

    def _calculate_scenario_competencies(self, results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate competency per scenario type"""
        scenario_scores = defaultdict(list)

        for result in results:
            scenario_type = result.get('scenario_type')
            score = result.get('overall_score', 0)

            if scenario_type:
                scenario_scores[scenario_type].append(score)

        return {
            scenario: round(statistics.mean(scores), 2)
            for scenario, scores in scenario_scores.items()
        }

    def _calculate_improvement_trend(self, scores: List[float]) -> float:
        """
        Calculate improvement trend

        Positive = improving, Negative = declining
        """
        if len(scores) < 2:
            return 0.0

        # Compare first half vs second half
        mid = len(scores) // 2
        first_half = statistics.mean(scores[:mid])
        second_half = statistics.mean(scores[mid:])

        return round(second_half - first_half, 2)

    def _analyze_decay_risk(self, last_exercise_date: datetime) -> Dict[str, Any]:
        """Analyze skills decay risk based on time since last exercise"""
        if last_exercise_date == datetime.min:
            return {
                'risk_level': 'unknown',
                'days_since_last': None,
                'recommendation': 'No exercise history'
            }

        days_since = (datetime.now() - last_exercise_date).days

        if days_since <= self.decay_thresholds['low']:
            risk_level = 'low'
            recommendation = 'Skills are fresh'
        elif days_since <= self.decay_thresholds['medium']:
            risk_level = 'medium'
            recommendation = 'Consider scheduling refresher exercise'
        elif days_since <= self.decay_thresholds['high']:
            risk_level = 'high'
            recommendation = 'Refresher exercise recommended soon'
        else:
            risk_level = 'critical'
            recommendation = 'URGENT: Skills decay likely, immediate refresher needed'

        return {
            'risk_level': risk_level,
            'days_since_last': days_since,
            'recommendation': recommendation
        }

    def _empty_profile(self, user_id: str) -> Dict[str, Any]:
        """Return empty competency profile"""
        return {
            'user_id': user_id,
            'core_competencies': {},
            'scenario_competencies': {},
            'total_exercises': 0,
            'avg_exercise_score': 0,
            'improvement_trend': 0,
            'decay_risk': {
                'risk_level': 'unknown',
                'days_since_last': None,
                'recommendation': 'No exercise history'
            },
            'certifications': [],
            'last_exercise_date': None
        }


class TeamCompetencyAnalyzer:
    """
    Analyzes team competency coverage

    Identifies gaps, backup coverage, training needs
    """

    def __init__(self):
        self.critical_capabilities = [
            'BIA Execution',
            'Risk Assessment',
            'Exercise Facilitation',
            'Audit Management',
            'Plan Development',
            'Incident Response',
            'Crisis Communication',
            'Recovery Management'
        ]

    @track_learning_operation(engine="team_competency_analyzer", operation="analyze_team_coverage")
    def analyze_team_coverage(
        self,
        team_name: str,
        user_competencies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze team competency coverage

        Returns:
            Coverage analysis with gaps and recommendations
        """
        if not user_competencies:
            return {
                'team_name': team_name,
                'coverage_summary': 'No competency data',
                'gaps': [],
                'recommendations': ['Build team competency baseline']
            }

        coverage_matrix = []
        critical_gaps = []

        for capability in self.critical_capabilities:
            capability_key = capability.lower().replace(' ', '_')

            # Find users with this capability
            capable_users = []

            for user in user_competencies:
                user_score = user.get('core_competencies', {}).get(capability_key, {}).get('score', 0)

                if user_score >= 70:  # Competent threshold
                    capable_users.append({
                        'user_id': user['user_id'],
                        'score': user_score
                    })

            # Sort by score
            capable_users.sort(key=lambda x: x['score'], reverse=True)

            # Determine coverage status
            if len(capable_users) == 0:
                coverage_status = 'none'
                gap_severity = 'critical'
                critical_gaps.append(capability)
            elif len(capable_users) == 1:
                coverage_status = 'weak'
                gap_severity = 'high'
            elif len(capable_users) == 2:
                coverage_status = 'adequate'
                gap_severity = 'medium'
            else:
                coverage_status = 'strong'
                gap_severity = 'low'

            coverage_matrix.append({
                'capability': capability,
                'coverage_status': coverage_status,
                'gap_severity': gap_severity,
                'primary_user': capable_users[0] if capable_users else None,
                'backup_users': capable_users[1:3] if len(capable_users) > 1 else [],
                'total_capable': len(capable_users)
            })

        # Generate recommendations
        recommendations = self._generate_team_recommendations(coverage_matrix, user_competencies)

        return {
            'team_name': team_name,
            'total_members': len(user_competencies),
            'coverage_matrix': coverage_matrix,
            'critical_gaps': critical_gaps,
            'critical_gap_count': len(critical_gaps),
            'recommendations': recommendations
        }

    def _generate_team_recommendations(
        self,
        coverage_matrix: List[Dict[str, Any]],
        user_competencies: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate team improvement recommendations"""
        recommendations = []

        # Critical gaps
        critical_caps = [c for c in coverage_matrix if c['gap_severity'] == 'critical']
        if critical_caps:
            recommendations.append(
                f"CRITICAL: Train team members on {', '.join([c['capability'] for c in critical_caps[:3]])}"
            )

        # High priority gaps
        high_caps = [c for c in coverage_matrix if c['gap_severity'] == 'high']
        if high_caps:
            recommendations.append(
                f"HIGH PRIORITY: Develop backup coverage for {', '.join([c['capability'] for c in high_caps[:2]])}"
            )

        # Skills decay
        users_at_risk = [u for u in user_competencies if u.get('decay_risk', {}).get('risk_level') in ['high', 'critical']]
        if users_at_risk:
            recommendations.append(
                f"Schedule refresher exercises for {len(users_at_risk)} team members at risk of skills decay"
            )

        # Cross-training
        single_coverage = [c for c in coverage_matrix if c['total_capable'] == 1]
        if single_coverage:
            recommendations.append(
                f"Implement cross-training program for capabilities with single-person coverage"
            )

        return recommendations if recommendations else ['Team competency coverage is strong']


class RoleGapAnalyzer:
    """
    Analyzes competency gaps for specific roles

    Compares required vs actual competencies
    """

    def __init__(self):
        # Role competency requirements (configurable)
        self.role_requirements = {
            'BCM Manager': {
                'bia_execution': 85,
                'risk_assessment': 85,
                'plan_development': 90,
                'exercise_facilitation': 80,
                'audit_management': 85
            },
            'BCM Coordinator': {
                'bia_execution': 75,
                'risk_assessment': 75,
                'exercise_facilitation': 80,
                'plan_development': 70
            },
            'Incident Commander': {
                'incident_response': 90,
                'crisis_communication': 85,
                'exercise_facilitation': 75
            },
            'Recovery Coordinator': {
                'recovery_management': 85,
                'plan_development': 80,
                'incident_response': 75
            }
        }

    @track_learning_operation(engine="role_gap_analyzer", operation="analyze_role_gaps")
    def analyze_role_gaps(
        self,
        role_name: str,
        user_competencies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze gaps for a specific role

        Returns:
            Gap analysis with training recommendations
        """
        required = self.role_requirements.get(role_name, {})

        if not required:
            return {
                'role_name': role_name,
                'error': f'No competency requirements defined for role: {role_name}'
            }

        # Aggregate actual competencies from all users in role
        actual_competencies = {}

        for competency in required.keys():
            scores = []

            for user in user_competencies:
                user_score = user.get('core_competencies', {}).get(competency, {}).get('score', 0)
                if user_score > 0:
                    scores.append(user_score)

            actual_competencies[competency] = round(statistics.mean(scores), 2) if scores else 0

        # Calculate gaps
        gaps = []
        critical_gaps = 0
        high_gaps = 0

        for competency, required_score in required.items():
            actual_score = actual_competencies.get(competency, 0)
            gap = required_score - actual_score

            if gap > 0:
                severity = self._assess_gap_severity(gap)

                gaps.append({
                    'competency': competency,
                    'required': required_score,
                    'actual': actual_score,
                    'gap': round(gap, 2),
                    'severity': severity
                })

                if severity == 'critical':
                    critical_gaps += 1
                elif severity == 'high':
                    high_gaps += 1

        # Sort gaps by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        gaps.sort(key=lambda x: (severity_order.get(x['severity'], 4), -x['gap']))

        # Generate training plan
        training_plan = self._generate_training_plan(gaps)

        return {
            'role_name': role_name,
            'user_count': len(user_competencies),
            'required_competencies': required,
            'actual_competencies': actual_competencies,
            'gaps': gaps,
            'critical_gaps': critical_gaps,
            'high_gaps': high_gaps,
            'training_plan': training_plan
        }

    def _assess_gap_severity(self, gap: float) -> str:
        """Assess gap severity"""
        if gap >= 30:
            return 'critical'
        elif gap >= 20:
            return 'high'
        elif gap >= 10:
            return 'medium'
        else:
            return 'low'

    def _generate_training_plan(self, gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate training plan to close gaps"""
        plan = []

        for gap in gaps:
            if gap['severity'] in ['critical', 'high']:
                plan.append({
                    'priority': gap['severity'],
                    'competency': gap['competency'],
                    'target_improvement': gap['gap'],
                    'recommended_actions': [
                        f"Intensive training program for {gap['competency']}",
                        f"Target: {gap['required']} (current: {gap['actual']})",
                        f"Conduct {self._estimate_exercises_needed(gap['gap'])} practice exercises",
                        f"Assign mentor with {gap['competency']} expertise"
                    ],
                    'estimated_duration_weeks': self._estimate_training_duration(gap['gap'])
                })

        return plan

    def _estimate_exercises_needed(self, gap: float) -> int:
        """Estimate number of exercises needed to close gap"""
        # Rough estimate: 1 exercise improves score by ~5 points
        return max(int(gap / 5), 1)

    def _estimate_training_duration(self, gap: float) -> int:
        """Estimate training duration in weeks"""
        # Rough estimate: 1 week per 10 points gap
        return max(int(gap / 10), 1)
