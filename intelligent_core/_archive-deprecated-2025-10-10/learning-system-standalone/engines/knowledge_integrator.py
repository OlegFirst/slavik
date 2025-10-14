"""
Knowledge Base Integration Engine

Maps exercise gaps to knowledge resources
Generates contextual learning paths
"""

import logging
from typing import Dict, Any, List, Optional
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


class KnowledgeIntegrator:
    """
    Integrates learning gaps with knowledge base

    Maps issues → resources
    Generates learning paths
    """

    def __init__(self):
        # Common gap keywords and their knowledge mappings
        self.gap_keyword_mappings = {
            'escalation': {
                'keywords': ['escalation', 'escalate', 'notify management', 'hierarchy'],
                'category': 'process',
                'knowledge_topics': ['Escalation Procedures', 'Incident Hierarchy', 'Management Notification']
            },
            'communication': {
                'keywords': ['communication', 'notify', 'inform', 'stakeholder'],
                'category': 'communication',
                'knowledge_topics': ['Crisis Communication', 'Stakeholder Management', 'Communication Plans']
            },
            'backup': {
                'keywords': ['backup', 'failover', 'alternate', 'recovery'],
                'category': 'technical',
                'knowledge_topics': ['Backup Systems', 'Failover Procedures', 'Recovery Strategies']
            },
            'assessment': {
                'keywords': ['assess', 'evaluate', 'analyze', 'severity'],
                'category': 'analytical',
                'knowledge_topics': ['Impact Assessment', 'BIA Methodology', 'Risk Evaluation']
            },
            'coordination': {
                'keywords': ['coordination', 'collaborate', 'team', 'roles'],
                'category': 'coordination',
                'knowledge_topics': ['Team Coordination', 'Role Definitions', 'Collaboration Best Practices']
            },
            'technical': {
                'keywords': ['technical', 'system', 'infrastructure', 'technology'],
                'category': 'technical',
                'knowledge_topics': ['Technical Response', 'System Recovery', 'IT Incident Management']
            },
            'cyber': {
                'keywords': ['cyber', 'malware', 'ransomware', 'breach', 'hacking'],
                'category': 'cyber',
                'knowledge_topics': ['Cyber Incident Response', 'Malware Handling', 'Breach Procedures']
            }
        }

    def map_gaps_to_knowledge(
        self,
        exercise_gaps: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Map exercise gaps to knowledge base resources

        Returns:
            List of knowledge mappings with recommended resources
        """
        if not exercise_gaps:
            return []

        mappings = []

        for gap in exercise_gaps:
            # Identify gap category
            gap_category = self._identify_gap_category(gap)

            if gap_category:
                mapping_data = self.gap_keyword_mappings[gap_category]

                mappings.append({
                    'gap': gap,
                    'gap_category': mapping_data['category'],
                    'knowledge_topics': mapping_data['knowledge_topics'],
                    'recommended_resources': self._get_resource_recommendations(gap_category),
                    'priority': self._assess_gap_priority(gap)
                })
            else:
                # Generic mapping
                mappings.append({
                    'gap': gap,
                    'gap_category': 'general',
                    'knowledge_topics': ['BCM Fundamentals', 'Best Practices'],
                    'recommended_resources': self._get_generic_resources(),
                    'priority': 'medium'
                })

        return mappings

    def _identify_gap_category(self, gap: str) -> Optional[str]:
        """Identify gap category from keywords"""
        gap_lower = gap.lower()

        for category, data in self.gap_keyword_mappings.items():
            if any(keyword in gap_lower for keyword in data['keywords']):
                return category

        return None

    def _assess_gap_priority(self, gap: str) -> str:
        """Assess priority of addressing a gap"""
        gap_lower = gap.lower()

        # High priority keywords
        high_priority = ['critical', 'urgent', 'failed', 'unable', 'missing']
        if any(keyword in gap_lower for keyword in high_priority):
            return 'high'

        # Medium priority keywords
        medium_priority = ['slow', 'unclear', 'delayed', 'incomplete']
        if any(keyword in gap_lower for keyword in medium_priority):
            return 'medium'

        return 'low'

    def _get_resource_recommendations(self, gap_category: str) -> List[Dict[str, Any]]:
        """Get recommended resources for a gap category"""
        # This would query actual knowledge base
        # For now, return structured recommendations

        resource_templates = {
            'escalation': [
                {'type': 'article', 'title': 'Escalation Procedures Guide', 'duration_minutes': 15, 'priority': 1},
                {'type': 'video', 'title': 'Effective Escalation in Crisis', 'duration_minutes': 10, 'priority': 2},
                {'type': 'template', 'title': 'Escalation Matrix Template', 'duration_minutes': 5, 'priority': 3}
            ],
            'communication': [
                {'type': 'article', 'title': 'Crisis Communication Best Practices', 'duration_minutes': 20, 'priority': 1},
                {'type': 'video', 'title': 'Stakeholder Communication in Crisis', 'duration_minutes': 15, 'priority': 2},
                {'type': 'checklist', 'title': 'Communication Checklist', 'duration_minutes': 5, 'priority': 3}
            ],
            'backup': [
                {'type': 'article', 'title': 'Backup System Activation', 'duration_minutes': 15, 'priority': 1},
                {'type': 'video', 'title': 'Failover Procedures Walkthrough', 'duration_minutes': 12, 'priority': 2},
                {'type': 'drill', 'title': 'Backup Activation Mini-Drill', 'duration_minutes': 30, 'priority': 3}
            ],
            'assessment': [
                {'type': 'article', 'title': 'Impact Assessment Methodology', 'duration_minutes': 25, 'priority': 1},
                {'type': 'template', 'title': 'BIA Assessment Template', 'duration_minutes': 10, 'priority': 2},
                {'type': 'video', 'title': 'Conducting Effective BIA', 'duration_minutes': 18, 'priority': 3}
            ],
            'coordination': [
                {'type': 'article', 'title': 'Team Coordination in Crisis', 'duration_minutes': 15, 'priority': 1},
                {'type': 'video', 'title': 'Role Clarity and Coordination', 'duration_minutes': 12, 'priority': 2},
                {'type': 'exercise', 'title': 'Coordination Practice Exercise', 'duration_minutes': 45, 'priority': 3}
            ],
            'technical': [
                {'type': 'article', 'title': 'Technical Incident Response', 'duration_minutes': 20, 'priority': 1},
                {'type': 'guide', 'title': 'System Recovery Procedures', 'duration_minutes': 15, 'priority': 2},
                {'type': 'video', 'title': 'IT Crisis Management', 'duration_minutes': 18, 'priority': 3}
            ],
            'cyber': [
                {'type': 'article', 'title': 'Cyber Incident Response Fundamentals', 'duration_minutes': 25, 'priority': 1},
                {'type': 'video', 'title': 'Ransomware Response Playbook', 'duration_minutes': 20, 'priority': 2},
                {'type': 'drill', 'title': 'Cyber Incident Mini-Drill', 'duration_minutes': 40, 'priority': 3}
            ]
        }

        return resource_templates.get(gap_category, self._get_generic_resources())

    def _get_generic_resources(self) -> List[Dict[str, Any]]:
        """Generic resource recommendations"""
        return [
            {'type': 'article', 'title': 'BCM Fundamentals', 'duration_minutes': 20, 'priority': 1},
            {'type': 'video', 'title': 'Business Continuity Best Practices', 'duration_minutes': 15, 'priority': 2},
            {'type': 'guide', 'title': 'ISO 22301 Overview', 'duration_minutes': 30, 'priority': 3}
        ]


class LearningPathGenerator:
    """
    Generates contextual learning paths

    Based on:
    - Identified gaps
    - Current competency level
    - Learning goals
    """

    def __init__(self, knowledge_integrator: KnowledgeIntegrator):
        self.knowledge_integrator = knowledge_integrator

    def generate_learning_path(
        self,
        user_id: str,
        exercise_gaps: List[str],
        current_competency_score: float,
        target_competency_score: float
    ) -> Dict[str, Any]:
        """
        Generate personalized learning path

        Returns:
            Structured learning path with steps
        """
        # Map gaps to knowledge
        gap_mappings = self.knowledge_integrator.map_gaps_to_knowledge(exercise_gaps)

        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        gap_mappings.sort(key=lambda x: priority_order.get(x['priority'], 3))

        # Build learning path steps
        steps = []
        total_duration = 0
        step_number = 1

        for gap_mapping in gap_mappings[:3]:  # Focus on top 3 gaps
            for resource in gap_mapping['recommended_resources']:
                steps.append({
                    'order': step_number,
                    'type': resource['type'],
                    'title': resource['title'],
                    'duration_minutes': resource['duration_minutes'],
                    'gap_addressed': gap_mapping['gap'],
                    'knowledge_topic': gap_mapping['knowledge_topics'][0] if gap_mapping['knowledge_topics'] else 'General'
                })

                total_duration += resource['duration_minutes']
                step_number += 1

        # Add practice exercise at the end
        steps.append({
            'order': step_number,
            'type': 'practice_exercise',
            'title': 'Integrated Practice Exercise',
            'duration_minutes': 60,
            'gap_addressed': 'All identified gaps',
            'knowledge_topic': 'Practical Application'
        })
        total_duration += 60

        # Add re-assessment
        steps.append({
            'order': step_number + 1,
            'type': 'reassessment',
            'title': 'Competency Re-assessment',
            'duration_minutes': 45,
            'gap_addressed': 'Measure improvement',
            'knowledge_topic': 'Validation'
        })
        total_duration += 45

        # Estimate improvement
        estimated_improvement = self._estimate_improvement(
            current_score=current_competency_score,
            target_score=target_competency_score,
            step_count=len(steps)
        )

        return {
            'user_id': user_id,
            'path_name': f"Competency Improvement Path: {current_competency_score:.0f}% → {target_competency_score:.0f}%",
            'description': f"Personalized path addressing {len(gap_mappings)} key gaps",
            'current_score': current_competency_score,
            'target_score': target_competency_score,
            'estimated_improvement': estimated_improvement,
            'steps': steps,
            'total_steps': len(steps),
            'total_duration_minutes': total_duration,
            'estimated_duration_days': self._estimate_days(total_duration)
        }

    def _estimate_improvement(
        self,
        current_score: float,
        target_score: float,
        step_count: int
    ) -> float:
        """Estimate competency improvement from learning path"""
        # Simple heuristic: each step contributes to gap closure
        gap = target_score - current_score

        # Assume 70% of gap can be closed with comprehensive path
        achievable_improvement = gap * 0.7

        return round(achievable_improvement, 2)

    def _estimate_days(self, total_minutes: int) -> int:
        """Estimate completion time in days"""
        # Assume 2 hours per day of learning
        hours_per_day = 2
        minutes_per_day = hours_per_day * 60

        days = total_minutes / minutes_per_day

        return max(int(days) + (1 if days % 1 > 0 else 0), 1)


class GapEffectivenessTracker:
    """
    Tracks effectiveness of gap→knowledge mappings

    Learns which resources best resolve which gaps
    """

    def __init__(self):
        self.effectiveness_data = defaultdict(lambda: {
            'times_recommended': 0,
            'times_resolved': 0,
            'effectiveness_score': 0
        })

    def record_recommendation(
        self,
        gap_keyword: str,
        resource_id: str
    ):
        """Record that a resource was recommended for a gap"""
        key = f"{gap_keyword}:{resource_id}"
        self.effectiveness_data[key]['times_recommended'] += 1

    def record_resolution(
        self,
        gap_keyword: str,
        resource_id: str,
        gap_resolved: bool
    ):
        """Record whether the resource resolved the gap"""
        key = f"{gap_keyword}:{resource_id}"

        if gap_resolved:
            self.effectiveness_data[key]['times_resolved'] += 1

        # Calculate effectiveness score
        data = self.effectiveness_data[key]
        if data['times_recommended'] > 0:
            data['effectiveness_score'] = (
                data['times_resolved'] / data['times_recommended'] * 100
            )

    def get_most_effective_resources(
        self,
        gap_keyword: str,
        min_recommendations: int = 3
    ) -> List[Dict[str, Any]]:
        """Get most effective resources for a gap"""
        gap_resources = [
            {
                'resource_id': key.split(':')[1],
                'effectiveness_score': data['effectiveness_score'],
                'times_recommended': data['times_recommended'],
                'times_resolved': data['times_resolved']
            }
            for key, data in self.effectiveness_data.items()
            if key.startswith(f"{gap_keyword}:") and
            data['times_recommended'] >= min_recommendations
        ]

        # Sort by effectiveness
        gap_resources.sort(key=lambda x: x['effectiveness_score'], reverse=True)

        return gap_resources

    def get_effectiveness_report(self) -> Dict[str, Any]:
        """Generate effectiveness report"""
        total_mappings = len(self.effectiveness_data)
        effective_mappings = sum(
            1 for data in self.effectiveness_data.values()
            if data['effectiveness_score'] >= 70
        )

        return {
            'total_mappings': total_mappings,
            'effective_mappings': effective_mappings,
            'effectiveness_rate': round(effective_mappings / total_mappings * 100, 2) if total_mappings > 0 else 0,
            'top_performers': sorted(
                [
                    {
                        'mapping': key,
                        'score': data['effectiveness_score']
                    }
                    for key, data in self.effectiveness_data.items()
                ],
                key=lambda x: x['score'],
                reverse=True
            )[:10]
        }
