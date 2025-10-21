"""
Learning Needs Collector

Автоматический сбор потребностей в обучении из множественных источников
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class LearningNeedsCollector:
    """
    Автоматический сбор потребностей в обучении

    Источники:
    1. Результаты упражнений (gaps → needs)
    2. Анализ компетенций (low scores → needs)
    3. ISO требования (compliance → needs)
    4. User requests (explicit needs)
    5. Emerging threats (new scenarios → needs)
    6. Industry benchmarks (gaps to industry → needs)
    """

    def __init__(self):
        self.urgency_weights = {
            'critical': 100,
            'high': 75,
            'medium': 50,
            'low': 25
        }

        # ISO 22301 required competencies
        self.iso_required_competencies = {
            '8.5': {  # Exercising and testing
                'name': 'Exercise Facilitation',
                'min_score': 75,
                'description': 'Ability to plan and conduct BCM exercises'
            },
            '8.3': {  # BIA
                'name': 'BIA Execution',
                'min_score': 80,
                'description': 'Conducting Business Impact Analysis'
            },
            '8.2': {  # Risk Assessment
                'name': 'Risk Assessment',
                'min_score': 75,
                'description': 'BCM risk assessment methodology'
            },
            '7.5': {  # Communication
                'name': 'Crisis Communication',
                'min_score': 70,
                'description': 'Crisis communication procedures'
            }
        }

    def collect_all_needs(
        self,
        exercise_results: List[Dict[str, Any]] = None,
        user_competencies: List[Dict[str, Any]] = None,
        user_requests: List[Dict[str, Any]] = None,
        industry_benchmarks: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Собрать потребности из всех источников

        Returns:
            {
                'needs': [...],
                'prioritized_needs': [...],
                'training_plan': {...},
                'statistics': {...}
            }
        """
        all_needs = []

        # Source 1: Exercise results
        if exercise_results:
            exercise_needs = self.collect_needs_from_exercises(exercise_results)
            all_needs.extend(exercise_needs)
            logger.info(f" Collected {len(exercise_needs)} needs from exercises")

        # Source 2: Competencies
        if user_competencies:
            competency_needs = self.collect_needs_from_competencies(user_competencies)
            all_needs.extend(competency_needs)
            logger.info(f" Collected {len(competency_needs)} needs from competencies")

        # Source 3: ISO requirements
        iso_needs = self.collect_needs_from_regulations(user_competencies or [])
        all_needs.extend(iso_needs)
        logger.info(f" Collected {len(iso_needs)} needs from ISO requirements")

        # Source 4: User requests
        if user_requests:
            request_needs = self.collect_needs_from_user_requests(user_requests)
            all_needs.extend(request_needs)
            logger.info(f" Collected {len(request_needs)} needs from user requests")

        # Source 5: Industry benchmarks
        if industry_benchmarks:
            benchmark_needs = self.collect_needs_from_benchmarks(industry_benchmarks)
            all_needs.extend(benchmark_needs)
            logger.info(f" Collected {len(benchmark_needs)} needs from benchmarks")

        # Prioritize
        prioritized = self.prioritize_needs(all_needs)

        # Generate training plan
        training_plan = self.generate_training_plan(prioritized)

        # Statistics
        stats = self._calculate_statistics(all_needs, prioritized)

        return {
            'needs': all_needs,
            'prioritized_needs': prioritized,
            'training_plan': training_plan,
            'statistics': stats,
            'collected_at': datetime.now().isoformat()
        }

    def collect_needs_from_exercises(
        self,
        exercise_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Из пробелов в упражнениях → потребности

        Gap: "Slow escalation process"
        → Need: "Training on escalation procedures"
        """
        needs = []
        gap_frequency = defaultdict(int)
        gap_users = defaultdict(set)

        # Analyze gaps
        for result in exercise_results:
            for issue in result.get('key_issues', []):
                gap_frequency[issue] += 1

                # Track affected users
                participants = result.get('participants', [])
                if isinstance(participants, list):
                    for user in participants:
                        gap_users[issue].add(user)

        # Convert to needs
        for gap, frequency in gap_frequency.items():
            urgency = self._assess_gap_urgency(frequency, len(exercise_results))

            needs.append({
                'id': f"need_exercise_{hash(gap) % 10000}",
                'source': 'exercise_gap',
                'gap': gap,
                'need_type': 'skill_improvement',
                'urgency': urgency,
                'frequency': frequency,
                'affected_users': list(gap_users[gap]),
                'affected_user_count': len(gap_users[gap]),
                'recommended_training': self._map_gap_to_training(gap),
                'created_at': datetime.now().isoformat()
            })

        return needs

    def collect_needs_from_competencies(
        self,
        user_competencies: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Из низких компетенций → потребности

        Competency: "BIA Execution: 45%"
        → Need: "BIA methodology training"
        """
        needs = []

        for user_comp in user_competencies:
            user_id = user_comp.get('user_id')
            competencies = user_comp.get('core_competencies', {})

            for competency_key, comp_data in competencies.items():
                if isinstance(comp_data, dict):
                    score = comp_data.get('score', 0)
                else:
                    score = comp_data

                # Threshold: <70 = needs improvement
                if score < 70:
                    gap = 70 - score
                    urgency = self._assess_competency_urgency(score)

                    needs.append({
                        'id': f"need_comp_{user_id}_{competency_key}",
                        'source': 'low_competency',
                        'competency': competency_key,
                        'current_score': score,
                        'target_score': 80,
                        'gap': gap,
                        'user_id': user_id,
                        'urgency': urgency,
                        'recommended_training': self._map_competency_to_training(competency_key),
                        'created_at': datetime.now().isoformat()
                    })

        return needs

    def collect_needs_from_regulations(
        self,
        user_competencies: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Из требований ISO 22301 → потребности

        ISO Clause 8.5: "Exercising and testing"
        → Need: "Training on exercise facilitation"
        """
        needs = []

        # Check each ISO requirement
        for clause, requirement in self.iso_required_competencies.items():
            competency_key = requirement['name'].lower().replace(' ', '_')
            min_required_score = requirement['min_score']

            # Check if ANY user has low score in this competency
            users_below_threshold = []

            for user_comp in user_competencies:
                user_id = user_comp.get('user_id')
                competencies = user_comp.get('core_competencies', {})

                comp_data = competencies.get(competency_key, {})
                if isinstance(comp_data, dict):
                    score = comp_data.get('score', 0)
                else:
                    score = comp_data

                if score < min_required_score:
                    users_below_threshold.append({
                        'user_id': user_id,
                        'score': score,
                        'gap': min_required_score - score
                    })

            if users_below_threshold:
                avg_gap = statistics.mean([u['gap'] for u in users_below_threshold])

                needs.append({
                    'id': f"need_iso_{clause}",
                    'source': 'regulatory_requirement',
                    'iso_clause': clause,
                    'requirement': requirement['description'],
                    'competency': competency_key,
                    'min_required_score': min_required_score,
                    'users_affected': len(users_below_threshold),
                    'avg_gap': round(avg_gap, 2),
                    'urgency': 'critical',  # ISO compliance is always critical
                    'recommended_training': self._map_iso_to_training(clause),
                    'created_at': datetime.now().isoformat()
                })

        return needs

    def collect_needs_from_user_requests(
        self,
        user_requests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Явные запросы пользователей

        User: "Хочу научиться проводить BIA"
        → Need: "BIA execution training"
        """
        needs = []

        for request in user_requests:
            needs.append({
                'id': f"need_request_{request.get('id', hash(request.get('description')))}",
                'source': 'user_request',
                'user_id': request.get('user_id'),
                'request': request.get('description'),
                'urgency': request.get('priority', 'medium'),
                'recommended_training': self._analyze_request(request.get('description')),
                'created_at': request.get('created_at', datetime.now().isoformat())
            })

        return needs

    def collect_needs_from_benchmarks(
        self,
        industry_benchmarks: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Из сравнения с индустрией → потребности

        Your score: 72, Industry median: 80
        → Need: "Improve to industry standard"
        """
        needs = []

        your_performance = industry_benchmarks.get('your_performance', {})
        benchmark = industry_benchmarks.get('benchmark', {})

        for metric, your_score in your_performance.items():
            industry_score = benchmark.get(metric, {}).get('median')

            if industry_score and your_score < industry_score:
                gap = industry_score - your_score

                needs.append({
                    'id': f"need_benchmark_{metric}",
                    'source': 'industry_benchmark',
                    'metric': metric,
                    'your_score': your_score,
                    'industry_median': industry_score,
                    'gap': gap,
                    'urgency': 'medium',
                    'recommended_training': f"Training to reach industry standard in {metric}",
                    'created_at': datetime.now().isoformat()
                })

        return needs

    def prioritize_needs(self, all_needs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Приоритизация потребностей

        Критерии:
        - Urgency (critical > high > medium > low)
        - Impact (сколько пользователей затронуто)
        - Compliance risk (ISO требования)
        - Business impact (критичность процесса)
        """
        for need in all_needs:
            # Calculate priority score
            urgency_score = self.urgency_weights.get(need.get('urgency', 'medium'), 50)
            impact_score = self._calculate_impact_score(need)
            compliance_score = self._calculate_compliance_score(need)
            business_score = self._calculate_business_score(need)

            total_score = (
                urgency_score * 0.3 +
                impact_score * 0.3 +
                compliance_score * 0.25 +
                business_score * 0.15
            )

            need['priority_score'] = round(total_score, 2)

        # Sort by priority score
        prioritized = sorted(all_needs, key=lambda n: n['priority_score'], reverse=True)

        return prioritized

    def generate_training_plan(
        self,
        prioritized_needs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Генерация учебного плана

        Распределение по временным рамкам:
        - immediate: критичные (в течение недели)
        - short_term: высокий приоритет (1-4 недели)
        - medium_term: средний приоритет (1-3 месяца)
        - long_term: низкий приоритет (> 3 месяцев)
        """
        plan = {
            'immediate': [],      # P-score >= 80
            'short_term': [],     # P-score 60-79
            'medium_term': [],    # P-score 40-59
            'long_term': []       # P-score < 40
        }

        for need in prioritized_needs:
            score = need.get('priority_score', 0)
            timeframe = self._determine_timeframe(score)

            plan[timeframe].append({
                'need_id': need.get('id'),
                'training': need.get('recommended_training'),
                'source': need.get('source'),
                'urgency': need.get('urgency'),
                'priority_score': score,
                'assigned_to': self._get_assigned_users(need),
                'estimated_duration': self._estimate_training_duration(need),
                'deadline': self._calculate_deadline(timeframe)
            })

        # Add summary
        plan['summary'] = {
            'total_needs': len(prioritized_needs),
            'immediate_count': len(plan['immediate']),
            'short_term_count': len(plan['short_term']),
            'medium_term_count': len(plan['medium_term']),
            'long_term_count': len(plan['long_term']),
            'generated_at': datetime.now().isoformat()
        }

        return plan

    # Helper methods

    def _assess_gap_urgency(self, frequency: int, total_exercises: int) -> str:
        """Assess urgency based on gap frequency"""
        rate = frequency / total_exercises if total_exercises > 0 else 0

        if rate >= 0.6:  # 60%+ exercises
            return 'critical'
        elif rate >= 0.4:
            return 'high'
        elif rate >= 0.2:
            return 'medium'
        else:
            return 'low'

    def _assess_competency_urgency(self, score: float) -> str:
        """Assess urgency based on competency score"""
        if score < 50:
            return 'critical'
        elif score < 60:
            return 'high'
        elif score < 70:
            return 'medium'
        else:
            return 'low'

    def _map_gap_to_training(self, gap: str) -> str:
        """Map exercise gap to training recommendation"""
        gap_lower = gap.lower()

        mappings = {
            'escalation': 'Escalation Procedures Training',
            'communication': 'Crisis Communication Workshop',
            'backup': 'Backup Systems Activation Training',
            'assessment': 'BIA Methodology Course',
            'coordination': 'Team Coordination in Crisis Training'
        }

        for keyword, training in mappings.items():
            if keyword in gap_lower:
                return training

        return f"Training to address: {gap}"

    def _map_competency_to_training(self, competency: str) -> str:
        """Map competency to training recommendation"""
        mappings = {
            'bia_execution': 'BIA Execution Masterclass',
            'risk_assessment': 'BCM Risk Assessment Training',
            'exercise_facilitation': 'Exercise Planning & Facilitation Course',
            'audit_management': 'ISO 22301 Audit Management Training',
            'plan_development': 'BC Plan Development Workshop',
            'incident_response': 'Incident Response Training',
            'crisis_communication': 'Crisis Communication Masterclass'
        }

        return mappings.get(competency, f"Training for {competency.replace('_', ' ').title()}")

    def _map_iso_to_training(self, clause: str) -> str:
        """Map ISO clause to training"""
        mappings = {
            '8.5': 'ISO 22301 Clause 8.5: Exercising and Testing',
            '8.3': 'ISO 22301 Clause 8.3: Business Impact Analysis',
            '8.2': 'ISO 22301 Clause 8.2: Risk Assessment',
            '7.5': 'ISO 22301 Clause 7.5: Communication'
        }

        return mappings.get(clause, f"ISO 22301 Clause {clause} Training")

    def _analyze_request(self, description: str) -> str:
        """Analyze user request and recommend training"""
        desc_lower = description.lower()

        if 'bia' in desc_lower:
            return 'BIA Execution Training'
        elif 'risk' in desc_lower:
            return 'Risk Assessment Training'
        elif 'exercise' in desc_lower or 'drill' in desc_lower:
            return 'Exercise Facilitation Training'
        elif 'audit' in desc_lower:
            return 'Audit Management Training'
        else:
            return f"Training based on request: {description}"

    def _calculate_impact_score(self, need: Dict[str, Any]) -> float:
        """Calculate impact score (0-100)"""
        affected_count = need.get('affected_user_count', need.get('users_affected', 1))

        # More users = higher impact
        if affected_count >= 10:
            return 100
        elif affected_count >= 5:
            return 75
        elif affected_count >= 2:
            return 50
        else:
            return 25

    def _calculate_compliance_score(self, need: Dict[str, Any]) -> float:
        """Calculate compliance risk score (0-100)"""
        if need.get('source') == 'regulatory_requirement':
            return 100  # ISO requirements always max score
        elif need.get('source') == 'exercise_gap' and need.get('frequency', 0) >= 5:
            return 75  # Recurring gaps = compliance risk
        else:
            return 25

    def _calculate_business_score(self, need: Dict[str, Any]) -> float:
        """Calculate business impact score (0-100)"""
        # Business-critical competencies
        critical_competencies = ['bia_execution', 'incident_response', 'crisis_communication']

        competency = need.get('competency', '')
        if competency in critical_competencies:
            return 100

        # Critical gaps
        gap = need.get('gap', '')
        if 'critical' in str(gap).lower():
            return 90

        return 50

    def _determine_timeframe(self, priority_score: float) -> str:
        """Determine training timeframe based on priority score"""
        if priority_score >= 80:
            return 'immediate'
        elif priority_score >= 60:
            return 'short_term'
        elif priority_score >= 40:
            return 'medium_term'
        else:
            return 'long_term'

    def _get_assigned_users(self, need: Dict[str, Any]) -> List[str]:
        """Get users assigned to this training need"""
        if 'user_id' in need:
            return [need['user_id']]
        elif 'affected_users' in need:
            return need['affected_users']
        else:
            return []

    def _estimate_training_duration(self, need: Dict[str, Any]) -> str:
        """Estimate training duration"""
        gap = need.get('gap', 0)

        if isinstance(gap, (int, float)):
            if gap >= 30:
                return '3-5 days'
            elif gap >= 20:
                return '2-3 days'
            elif gap >= 10:
                return '1-2 days'
            else:
                return '4-8 hours'

        return '1-2 days'  # Default

    def _calculate_deadline(self, timeframe: str) -> str:
        """Calculate training deadline"""
        now = datetime.now()

        deadlines = {
            'immediate': now + timedelta(days=7),
            'short_term': now + timedelta(days=28),
            'medium_term': now + timedelta(days=90),
            'long_term': now + timedelta(days=180)
        }

        return deadlines.get(timeframe, now + timedelta(days=30)).isoformat()

    def _calculate_statistics(
        self,
        all_needs: List[Dict[str, Any]],
        prioritized_needs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate statistics about collected needs"""
        sources = defaultdict(int)
        urgencies = defaultdict(int)

        for need in all_needs:
            sources[need.get('source')] += 1
            urgencies[need.get('urgency')] += 1

        return {
            'total_needs': len(all_needs),
            'by_source': dict(sources),
            'by_urgency': dict(urgencies),
            'avg_priority_score': round(
                statistics.mean([n.get('priority_score', 0) for n in prioritized_needs]),
                2
            ) if prioritized_needs else 0,
            'top_priority': prioritized_needs[0] if prioritized_needs else None
        }
