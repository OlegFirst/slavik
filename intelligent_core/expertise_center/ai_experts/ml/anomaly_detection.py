"""
Anomaly Detection

Detects anomalies in workflow progression and user behavior.
"""

from typing import Dict, Any, List, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Anomaly Detector

    Detects unusual patterns in:
    - Workflow progression (unusually slow/fast)
    - User behavior (unusual activity patterns)
    - Data quality (suspicious data entries)
    """

    def __init__(self, sensitivity: float = 0.8):
        """
        Initialize anomaly detector

        Args:
            sensitivity: Detection sensitivity (0-1, higher = more sensitive)
        """
        self.sensitivity = sensitivity
        self.baseline_stats = {}

    async def detect_workflow_anomalies(
        self,
        workflow_data: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Detect workflow progression anomalies

        Args:
            workflow_data: Current workflow data
            historical_data: Historical workflows for baseline

        Returns:
            Anomaly detection results
        """

        anomalies = []

        # Check duration anomaly
        duration_anomaly = self._check_duration_anomaly(
            workflow_data,
            historical_data
        )
        if duration_anomaly:
            anomalies.append(duration_anomaly)

        # Check stagnation anomaly
        stagnation_anomaly = self._check_stagnation(workflow_data)
        if stagnation_anomaly:
            anomalies.append(stagnation_anomaly)

        # Check activity pattern anomaly
        activity_anomaly = self._check_activity_pattern(workflow_data)
        if activity_anomaly:
            anomalies.append(activity_anomaly)

        # Overall risk assessment
        risk_level = 'high' if len(anomalies) >= 2 else 'medium' if len(anomalies) == 1 else 'low'

        return {
            'anomalies_detected': len(anomalies),
            'anomalies': anomalies,
            'risk_level': risk_level,
            'recommendations': self._generate_anomaly_recommendations(anomalies)
        }

    def _check_duration_anomaly(
        self,
        workflow_data: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]]
    ) -> Optional[Dict[str, Any]]:
        """Check if workflow duration is anomalous"""

        current_duration = workflow_data.get('duration_hours', 0)
        stage = workflow_data.get('current_stage', 'unknown')

        if not historical_data:
            # No baseline - use heuristics
            expected_duration = self._get_expected_duration(workflow_data)

            if current_duration > expected_duration * 2:
                return {
                    'type': 'duration',
                    'severity': 'high',
                    'description': f'Stage duration ({current_duration}h) significantly exceeds expected ({expected_duration}h)',
                    'recommendation': 'Review for blockers or complexity issues'
                }

            return None

        # Calculate baseline from historical data
        historical_durations = [
            h.get('duration_hours', 0)
            for h in historical_data
            if h.get('stage') == stage and h.get('duration_hours')
        ]

        if not historical_durations:
            return None

        mean_duration = np.mean(historical_durations)
        std_duration = np.std(historical_durations)

        # Check if current duration is outlier (> 2 std devs)
        z_score = (current_duration - mean_duration) / std_duration if std_duration > 0 else 0

        if abs(z_score) > 2:
            severity = 'high' if abs(z_score) > 3 else 'medium'

            return {
                'type': 'duration',
                'severity': severity,
                'description': f'Stage duration ({current_duration}h) is {abs(z_score):.1f} std devs from baseline ({mean_duration:.1f}h)',
                'z_score': round(z_score, 2),
                'recommendation': 'Investigate cause of unusual duration'
            }

        return None

    def _check_stagnation(self, workflow_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check for workflow stagnation"""

        days_in_current_stage = workflow_data.get('days_in_current_stage', 0)
        last_activity_days = workflow_data.get('days_since_last_activity', 0)

        # Stagnation thresholds
        if days_in_current_stage > 14:
            return {
                'type': 'stagnation',
                'severity': 'high',
                'description': f'Workflow has been in current stage for {days_in_current_stage} days',
                'recommendation': 'Schedule review meeting to identify blockers'
            }

        if last_activity_days > 7:
            return {
                'type': 'inactivity',
                'severity': 'medium',
                'description': f'No activity for {last_activity_days} days',
                'recommendation': 'Re-engage stakeholders and restart progress'
            }

        return None

    def _check_activity_pattern(self, workflow_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check for unusual activity patterns"""

        activities = workflow_data.get('recent_activities', [])

        if not activities:
            return None

        # Check for burst activity (many activities in short time)
        if len(activities) > 20:
            # Check if all within 24 hours
            timestamps = [a.get('timestamp') for a in activities if a.get('timestamp')]

            if len(timestamps) >= 2:
                # Simple check: if many activities, might be unusual
                return {
                    'type': 'activity_burst',
                    'severity': 'low',
                    'description': f'{len(activities)} activities recorded recently',
                    'recommendation': 'Verify data quality and user actions'
                }

        return None

    def _get_expected_duration(self, workflow_data: Dict[str, Any]) -> float:
        """Get expected duration based on heuristics"""

        org_size = workflow_data.get('org_size', 'medium')
        maturity = workflow_data.get('org_maturity', 3)

        base_hours = {
            'small': 8,
            'medium': 16,
            'large': 32
        }.get(org_size, 16)

        maturity_multiplier = {
            1: 1.5,
            2: 1.2,
            3: 1.0,
            4: 0.8,
            5: 0.6
        }.get(maturity, 1.0)

        return base_hours * maturity_multiplier

    def _generate_anomaly_recommendations(
        self,
        anomalies: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations for detected anomalies"""

        recommendations = []

        for anomaly in anomalies:
            if anomaly.get('recommendation'):
                recommendations.append(anomaly['recommendation'])

        if not recommendations:
            recommendations.append('No anomalies detected - workflow progressing normally')

        return recommendations

    async def detect_data_quality_issues(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect data quality issues

        Args:
            data: Data to check

        Returns:
            Data quality assessment
        """

        issues = []

        # Check for missing required fields
        required_fields = ['org_size', 'industry', 'current_stage']
        missing_fields = [f for f in required_fields if not data.get(f)]

        if missing_fields:
            issues.append({
                'type': 'missing_data',
                'severity': 'medium',
                'description': f'Missing required fields: {", ".join(missing_fields)}',
                'recommendation': 'Complete missing information'
            })

        # Check for invalid values
        if data.get('org_maturity') and not (1 <= data['org_maturity'] <= 5):
            issues.append({
                'type': 'invalid_value',
                'severity': 'low',
                'description': 'Maturity level should be 1-5',
                'recommendation': 'Correct maturity level'
            })

        # Check for inconsistent data
        if data.get('stage_index', 0) > data.get('total_stages', 0):
            issues.append({
                'type': 'inconsistency',
                'severity': 'high',
                'description': 'Stage index exceeds total stages',
                'recommendation': 'Verify workflow configuration'
            })

        quality_score = max(0, 100 - (len(issues) * 20))

        return {
            'quality_score': quality_score,
            'issues_detected': len(issues),
            'issues': issues,
            'status': 'good' if quality_score >= 80 else 'fair' if quality_score >= 60 else 'poor'
        }

    def update_baseline(self, historical_data: List[Dict[str, Any]]):
        """
        Update baseline statistics

        Args:
            historical_data: Historical workflow data
        """

        # Calculate baseline statistics per stage
        stages = {}

        for data in historical_data:
            stage = data.get('stage', 'unknown')
            duration = data.get('duration_hours')

            if stage not in stages:
                stages[stage] = []

            if duration:
                stages[stage].append(duration)

        # Calculate stats
        for stage, durations in stages.items():
            if durations:
                self.baseline_stats[stage] = {
                    'mean': np.mean(durations),
                    'std': np.std(durations),
                    'median': np.median(durations),
                    'count': len(durations)
                }

        logger.info(f"Baseline updated with {len(historical_data)} records across {len(stages)} stages")
