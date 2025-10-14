"""
Process-Based Gap Analysis Engine

Analyzes BCM process coverage from exercise results
Maps to ISO 22301 requirements
"""

import logging
from typing import Dict, Any, List, Optional
from collections import defaultdict
import statistics
from learning_knowledge.monitoring.metrics import (
    track_gap_analysis,
    track_learning_operation
)

logger = logging.getLogger(__name__)


class ProcessGapAnalyzer:
    """
    Analyzes BCM process coverage from exercises

    Identifies:
    - Which process steps are tested
    - Success rates per step
    - Coverage gaps
    - Improvement priorities
    """

    def __init__(self):
        # Standard BCM processes (ISO 22301 aligned)
        self.standard_processes = {
            'incident_detection': {
                'name': 'Incident Detection & Notification',
                'iso_clause': '8.4',
                'steps': [
                    {'order': 1, 'name': 'Detect incident', 'required': True},
                    {'order': 2, 'name': 'Assess initial severity', 'required': True},
                    {'order': 3, 'name': 'Notify key personnel', 'required': True},
                    {'order': 4, 'name': 'Activate alert system', 'required': True}
                ]
            },
            'incident_response': {
                'name': 'Incident Response',
                'iso_clause': '8.4',
                'steps': [
                    {'order': 1, 'name': 'Assess incident impact', 'required': True},
                    {'order': 2, 'name': 'Activate response team', 'required': True},
                    {'order': 3, 'name': 'Execute initial response', 'required': True},
                    {'order': 4, 'name': 'Establish command center', 'required': False}
                ]
            },
            'escalation': {
                'name': 'Escalation Process',
                'iso_clause': '8.4',
                'steps': [
                    {'order': 1, 'name': 'Determine escalation criteria', 'required': True},
                    {'order': 2, 'name': 'Escalate to management', 'required': True},
                    {'order': 3, 'name': 'Escalate to executive', 'required': True},
                    {'order': 4, 'name': 'Engage external support', 'required': False}
                ]
            },
            'communication': {
                'name': 'Crisis Communication',
                'iso_clause': '8.4.3',
                'steps': [
                    {'order': 1, 'name': 'Activate communication plan', 'required': True},
                    {'order': 2, 'name': 'Notify internal stakeholders', 'required': True},
                    {'order': 3, 'name': 'Notify external stakeholders', 'required': True},
                    {'order': 4, 'name': 'Media management', 'required': False}
                ]
            },
            'backup_activation': {
                'name': 'Backup Systems Activation',
                'iso_clause': '8.4.2',
                'steps': [
                    {'order': 1, 'name': 'Assess backup need', 'required': True},
                    {'order': 2, 'name': 'Activate backup systems', 'required': True},
                    {'order': 3, 'name': 'Verify backup functionality', 'required': True},
                    {'order': 4, 'name': 'Switch to backup operations', 'required': True}
                ]
            },
            'recovery': {
                'name': 'Recovery & Restoration',
                'iso_clause': '8.4.2',
                'steps': [
                    {'order': 1, 'name': 'Assess recovery readiness', 'required': True},
                    {'order': 2, 'name': 'Execute recovery plan', 'required': True},
                    {'order': 3, 'name': 'Restore normal operations', 'required': True},
                    {'order': 4, 'name': 'Validate recovery', 'required': True}
                ]
            }
        }

    @track_gap_analysis
    @track_learning_operation(engine="process_gap_analyzer", operation="analyze_process_coverage")
    def analyze_process_coverage(
        self,
        scenario_type: str,
        exercise_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze BCM process coverage for a scenario type

        Returns:
            Coverage analysis with gaps and priorities
        """
        if not exercise_results:
            return {
                'scenario_type': scenario_type,
                'error': 'No exercise results to analyze'
            }

        # Filter results for this scenario
        scenario_results = [r for r in exercise_results if r.get('scenario_type') == scenario_type]

        if not scenario_results:
            return {
                'scenario_type': scenario_type,
                'error': f'No exercises found for scenario type: {scenario_type}'
            }

        # Analyze each process
        process_coverage = {}

        for process_id, process_def in self.standard_processes.items():
            coverage = self._analyze_process_steps(
                process_id,
                process_def,
                scenario_results
            )
            process_coverage[process_id] = coverage

        # Calculate overall metrics
        overall_gap_score = self._calculate_overall_gap_score(process_coverage)

        # Identify critical gaps
        critical_gaps = self._identify_critical_gaps(process_coverage)

        # Generate improvement priorities
        improvement_priorities = self._generate_improvement_priorities(process_coverage, critical_gaps)

        return {
            'scenario_type': scenario_type,
            'total_exercises': len(scenario_results),
            'process_coverage': process_coverage,
            'overall_gap_score': overall_gap_score,
            'critical_gaps': critical_gaps,
            'improvement_priorities': improvement_priorities
        }

    def _analyze_process_steps(
        self,
        process_id: str,
        process_def: Dict[str, Any],
        exercise_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze coverage for each step in a process"""
        steps = process_def['steps']
        step_coverage = {}

        for step in steps:
            step_name = step['name']

            # Count how many times this step was tested
            tested_count = 0
            success_count = 0

            for result in exercise_results:
                # Check if step was mentioned in objectives or key issues
                objectives_met = result.get('objectives_met', [])
                key_issues = result.get('key_issues', [])

                step_tested = any(step_name.lower() in obj.lower() for obj in objectives_met)
                step_failed = any(step_name.lower() in issue.lower() for issue in key_issues)

                if step_tested or step_failed:
                    tested_count += 1

                    if step_tested and not step_failed:
                        success_count += 1

            # Calculate success rate
            success_rate = (success_count / tested_count * 100) if tested_count > 0 else 0

            step_coverage[f"step_{step['order']}"] = {
                'name': step_name,
                'required': step['required'],
                'tested': tested_count,
                'success': success_count,
                'success_rate': round(success_rate, 2),
                'status': self._assess_step_status(success_rate, tested_count, step['required'])
            }

        # Calculate process-level metrics
        tested_steps = [s for s in step_coverage.values() if s['tested'] > 0]
        avg_success_rate = statistics.mean([s['success_rate'] for s in tested_steps]) if tested_steps else 0

        return {
            'process_name': process_def['name'],
            'iso_clause': process_def['iso_clause'],
            'step_coverage': step_coverage,
            'total_steps': len(steps),
            'tested_steps': len(tested_steps),
            'avg_success_rate': round(avg_success_rate, 2),
            'coverage_percentage': round((len(tested_steps) / len(steps) * 100), 2) if steps else 0
        }

    def _assess_step_status(self, success_rate: float, tested_count: int, required: bool) -> str:
        """Assess step status"""
        if tested_count == 0:
            return 'critical' if required else 'untested'
        elif success_rate >= 80:
            return 'strong'
        elif success_rate >= 60:
            return 'adequate'
        elif success_rate >= 40:
            return 'weak'
        else:
            return 'critical'

    def _calculate_overall_gap_score(self, process_coverage: Dict[str, Any]) -> float:
        """
        Calculate overall gap score (0-100)

        100 = no gaps, 0 = many gaps
        """
        if not process_coverage:
            return 0

        scores = []

        for process_data in process_coverage.values():
            # Weight by coverage percentage and success rate
            coverage_pct = process_data['coverage_percentage']
            success_rate = process_data['avg_success_rate']

            # Combined score
            process_score = (coverage_pct * 0.4 + success_rate * 0.6)
            scores.append(process_score)

        return round(statistics.mean(scores), 2) if scores else 0

    def _identify_critical_gaps(self, process_coverage: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify critical process gaps"""
        gaps = []

        for process_id, process_data in process_coverage.items():
            step_coverage = process_data['step_coverage']

            for step_id, step_data in step_coverage.items():
                if step_data['status'] == 'critical':
                    gaps.append({
                        'process': process_data['process_name'],
                        'process_id': process_id,
                        'step': step_data['name'],
                        'issue': 'Not tested' if step_data['tested'] == 0 else f"Low success rate ({step_data['success_rate']}%)",
                        'iso_clause': process_data['iso_clause'],
                        'required': step_data['required']
                    })

        # Sort by required first, then by process
        gaps.sort(key=lambda x: (not x['required'], x['process']))

        return gaps

    def _generate_improvement_priorities(
        self,
        process_coverage: Dict[str, Any],
        critical_gaps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate prioritized improvement actions"""
        priorities = []

        # Priority 1: Critical gaps in required steps
        critical_required = [g for g in critical_gaps if g['required']]
        if critical_required:
            for gap in critical_required[:3]:  # Top 3
                priorities.append({
                    'priority': 'critical',
                    'action': f"Address critical gap in {gap['process']}: {gap['step']}",
                    'rationale': f"{gap['issue']} - ISO {gap['iso_clause']} requirement",
                    'recommended_exercises': self._recommend_exercises_for_gap(gap)
                })

        # Priority 2: Low coverage processes
        low_coverage = [
            (pid, pdata) for pid, pdata in process_coverage.items()
            if pdata['coverage_percentage'] < 50
        ]
        low_coverage.sort(key=lambda x: x[1]['coverage_percentage'])

        for process_id, process_data in low_coverage[:2]:  # Top 2
            priorities.append({
                'priority': 'high',
                'action': f"Increase coverage for {process_data['process_name']}",
                'rationale': f"Only {process_data['coverage_percentage']}% of steps tested",
                'recommended_exercises': [f"Full {process_data['process_name']} exercise"]
            })

        # Priority 3: Low success rate processes
        low_success = [
            (pid, pdata) for pid, pdata in process_coverage.items()
            if pdata['avg_success_rate'] < 70 and pdata['coverage_percentage'] > 0
        ]
        low_success.sort(key=lambda x: x[1]['avg_success_rate'])

        for process_id, process_data in low_success[:2]:  # Top 2
            priorities.append({
                'priority': 'medium',
                'action': f"Improve performance in {process_data['process_name']}",
                'rationale': f"Success rate only {process_data['avg_success_rate']}%",
                'recommended_exercises': [f"Focused drill on {process_data['process_name']}"]
            })

        return priorities[:5]  # Top 5 priorities

    def _recommend_exercises_for_gap(self, gap: Dict[str, Any]) -> List[str]:
        """Recommend exercises to address a gap"""
        process = gap['process_id']
        step = gap['step']

        exercises = [
            f"Tabletop exercise focusing on {step}",
            f"Walkthrough of {gap['process']} with emphasis on {step}",
            f"Mini-drill specifically for {step}"
        ]

        return exercises


class ProcessCoverageMatrix:
    """
    Generates BCM Process Coverage Matrix

    Visual heatmap of process coverage across scenarios
    """

    def __init__(self, gap_analyzer: ProcessGapAnalyzer):
        self.gap_analyzer = gap_analyzer

    @track_learning_operation(engine="process_coverage_matrix", operation="generate_coverage_matrix")
    def generate_coverage_matrix(
        self,
        exercise_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate coverage matrix

        Process (rows) x Scenario Type (columns)
        """
        if not exercise_results:
            return {'error': 'No exercise results'}

        # Get unique scenario types
        scenario_types = list(set(r.get('scenario_type') for r in exercise_results if r.get('scenario_type')))

        # Build matrix
        matrix = []

        for process_id, process_def in self.gap_analyzer.standard_processes.items():
            row = {
                'process_id': process_id,
                'process_name': process_def['name'],
                'iso_clause': process_def['iso_clause'],
                'coverage_by_scenario': {}
            }

            for scenario in scenario_types:
                scenario_results = [r for r in exercise_results if r.get('scenario_type') == scenario]
                coverage = self.gap_analyzer._analyze_process_steps(
                    process_id,
                    process_def,
                    scenario_results
                )

                row['coverage_by_scenario'][scenario] = {
                    'coverage_percentage': coverage['coverage_percentage'],
                    'success_rate': coverage['avg_success_rate'],
                    'status': self._assess_cell_status(coverage)
                }

            # Overall process coverage
            all_coverage = self.gap_analyzer._analyze_process_steps(
                process_id,
                process_def,
                exercise_results
            )

            row['overall_coverage'] = all_coverage['coverage_percentage']
            row['overall_success_rate'] = all_coverage['avg_success_rate']

            matrix.append(row)

        # Sort by overall coverage (lowest first = highest priority)
        matrix.sort(key=lambda x: x['overall_coverage'])

        return {
            'scenario_types': scenario_types,
            'matrix': matrix,
            'summary': self._generate_matrix_summary(matrix, scenario_types)
        }

    def _assess_cell_status(self, coverage: Dict[str, Any]) -> str:
        """Assess matrix cell status"""
        cov_pct = coverage['coverage_percentage']
        success_rate = coverage['avg_success_rate']

        if cov_pct == 0:
            return 'untested'
        elif cov_pct >= 75 and success_rate >= 80:
            return 'strong'
        elif cov_pct >= 50 and success_rate >= 60:
            return 'adequate'
        elif cov_pct >= 25:
            return 'weak'
        else:
            return 'critical'

    def _generate_matrix_summary(
        self,
        matrix: List[Dict[str, Any]],
        scenario_types: List[str]
    ) -> Dict[str, Any]:
        """Generate summary statistics for matrix"""
        total_cells = len(matrix) * len(scenario_types)

        status_counts = {
            'strong': 0,
            'adequate': 0,
            'weak': 0,
            'critical': 0,
            'untested': 0
        }

        for row in matrix:
            for scenario in scenario_types:
                status = row['coverage_by_scenario'].get(scenario, {}).get('status', 'untested')
                status_counts[status] = status_counts.get(status, 0) + 1

        return {
            'total_cells': total_cells,
            'status_distribution': status_counts,
            'coverage_health': self._assess_overall_health(status_counts, total_cells),
            'top_gaps': [
                {
                    'process': row['process_name'],
                    'coverage': row['overall_coverage']
                }
                for row in matrix[:3]  # Bottom 3 (lowest coverage)
            ]
        }

    def _assess_overall_health(self, status_counts: Dict[str, int], total: int) -> str:
        """Assess overall matrix health"""
        critical_pct = (status_counts.get('critical', 0) + status_counts.get('untested', 0)) / total * 100

        if critical_pct >= 40:
            return 'poor'
        elif critical_pct >= 20:
            return 'needs_improvement'
        elif critical_pct >= 10:
            return 'good'
        else:
            return 'excellent'
