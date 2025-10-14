"""
Gamification Engine

Badges, points, levels, leaderboards, achievements
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from collections import defaultdict

logger = logging.getLogger(__name__)


class GamificationEngine:
    """
    Core gamification engine

    Manages:
    - Points and levels
    - Badge earning
    - Streaks tracking
    - Leaderboards
    """

    def __init__(self):
        # Level thresholds
        self.levels = [
            {'level': 1, 'name': 'Novice', 'min_points': 0, 'max_points': 499},
            {'level': 2, 'name': 'Practitioner', 'min_points': 500, 'max_points': 1499},
            {'level': 3, 'name': 'Expert', 'min_points': 1500, 'max_points': 2999},
            {'level': 4, 'name': 'Master', 'min_points': 3000, 'max_points': 4999},
            {'level': 5, 'name': 'Champion', 'min_points': 5000, 'max_points': 999999}
        ]

        # Points awarded for activities
        self.point_values = {
            'exercise_completion': 100,
            'perfect_score': 100,  # Bonus for 90+ score
            'pattern_resolution': 150,
            'knowledge_contribution': 75,
            'badge_earned': 50,
            'streak_milestone': 100,
            'first_in_category': 200
        }

    def calculate_profile(
        self,
        user_id: str,
        activity_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive gamification profile

        Returns:
            Profile with points, level, badges, streaks
        """
        if not activity_history:
            return self._empty_profile(user_id)

        # Calculate total points
        total_points = self._calculate_total_points(activity_history)

        # Determine level
        level_info = self._determine_level(total_points)

        # Check for earned badges
        badges = self._check_badges_earned(activity_history)

        # Calculate streaks
        streak_info = self._calculate_streaks(activity_history)

        # Activity summary
        summary = self._summarize_activities(activity_history)

        return {
            'user_id': user_id,
            'total_points': total_points,
            'level': level_info['level'],
            'level_name': level_info['name'],
            'points_to_next_level': level_info['points_to_next'],
            'progress_to_next_level': level_info['progress_percentage'],
            'badges': badges,
            'badge_count': len(badges),
            'current_streak_days': streak_info['current_streak'],
            'longest_streak_days': streak_info['longest_streak'],
            'last_activity_date': streak_info['last_activity'],
            'achievements': [],  # Populated separately
            'activity_summary': summary
        }

    def _calculate_total_points(self, activities: List[Dict[str, Any]]) -> int:
        """Calculate total points from activity history"""
        total = 0

        for activity in activities:
            activity_type = activity.get('type')
            points = 0

            if activity_type == 'exercise_completion':
                points = self.point_values['exercise_completion']

                # Bonus for perfect score
                if activity.get('score', 0) >= 90:
                    points += self.point_values['perfect_score']

            elif activity_type == 'pattern_resolution':
                points = self.point_values['pattern_resolution']

            elif activity_type == 'knowledge_contribution':
                points = self.point_values['knowledge_contribution']

            elif activity_type == 'badge_earned':
                # Badge points already included in badge definition
                points = activity.get('badge_points', self.point_values['badge_earned'])

            total += points

        return total

    def _determine_level(self, total_points: int) -> Dict[str, Any]:
        """Determine user level based on points"""
        for level_data in reversed(self.levels):
            if total_points >= level_data['min_points']:
                # Found the level
                next_level = None

                for lvl in self.levels:
                    if lvl['level'] == level_data['level'] + 1:
                        next_level = lvl
                        break

                if next_level:
                    points_to_next = next_level['min_points'] - total_points
                    level_range = next_level['min_points'] - level_data['min_points']
                    progress = ((total_points - level_data['min_points']) / level_range * 100) if level_range > 0 else 100
                else:
                    points_to_next = 0
                    progress = 100

                return {
                    'level': level_data['level'],
                    'name': level_data['name'],
                    'points_to_next': points_to_next,
                    'progress_percentage': round(progress, 2)
                }

        # Default to level 1
        return {
            'level': 1,
            'name': 'Novice',
            'points_to_next': 500 - total_points,
            'progress_percentage': round(total_points / 500 * 100, 2)
        }

    def _check_badges_earned(self, activities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check which badges have been earned"""
        badges = []

        # Extract exercise completions
        exercises = [a for a in activities if a.get('type') == 'exercise_completion']

        # Frequency badges
        exercise_count = len(exercises)

        if exercise_count >= 1:
            badges.append(self._create_badge_record('first_timer', activities[0].get('timestamp')))
        if exercise_count >= 10:
            badges.append(self._create_badge_record('regular_practitioner', None))
        if exercise_count >= 50:
            badges.append(self._create_badge_record('exercise_champion', None))

        # Performance badges
        for exercise in exercises:
            score = exercise.get('score', 0)

            if 60 <= score < 70:
                if not self._has_badge(badges, 'bronze_response'):
                    badges.append(self._create_badge_record('bronze_response', exercise.get('timestamp')))
            elif 70 <= score < 80:
                if not self._has_badge(badges, 'silver_response'):
                    badges.append(self._create_badge_record('silver_response', exercise.get('timestamp')))
            elif 80 <= score < 90:
                if not self._has_badge(badges, 'gold_response'):
                    badges.append(self._create_badge_record('gold_response', exercise.get('timestamp')))
            elif score >= 90:
                if not self._has_badge(badges, 'platinum_response'):
                    badges.append(self._create_badge_record('platinum_response', exercise.get('timestamp')))

        # Improvement badges
        if len(exercises) >= 2:
            scores = [e.get('score', 0) for e in exercises]
            max_improvement = max([scores[i] - scores[i-1] for i in range(1, len(scores))])

            if max_improvement >= 20 and not self._has_badge(badges, 'rising_star'):
                badges.append(self._create_badge_record('rising_star', None))
            if max_improvement >= 30 and not self._has_badge(badges, 'rapid_learner'):
                badges.append(self._create_badge_record('rapid_learner', None))

        # Specialty badges (scenario-specific)
        scenario_stats = defaultdict(lambda: {'count': 0, 'high_scores': 0})

        for exercise in exercises:
            scenario = exercise.get('scenario_type')
            score = exercise.get('score', 0)

            if scenario:
                scenario_stats[scenario]['count'] += 1
                if score >= 75:
                    scenario_stats[scenario]['high_scores'] += 1

        for scenario, stats in scenario_stats.items():
            if stats['high_scores'] >= 5:
                badge_id = f"{scenario}_expert"
                if not self._has_badge(badges, badge_id):
                    badges.append(self._create_badge_record(badge_id, None))

        return badges

    def _calculate_streaks(self, activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate activity streaks"""
        if not activities:
            return {
                'current_streak': 0,
                'longest_streak': 0,
                'last_activity': None
            }

        # Sort activities by date
        sorted_activities = sorted(activities, key=lambda x: x.get('timestamp', datetime.min))

        # Extract unique activity dates
        activity_dates = list(set(
            a.get('timestamp').date() if isinstance(a.get('timestamp'), datetime) else a.get('timestamp')
            for a in sorted_activities
            if a.get('timestamp')
        ))
        activity_dates.sort()

        if not activity_dates:
            return {
                'current_streak': 0,
                'longest_streak': 0,
                'last_activity': None
            }

        # Calculate current streak
        today = date.today()
        current_streak = 0

        for i in range(len(activity_dates) - 1, -1, -1):
            activity_date = activity_dates[i]
            expected_date = today - (today - activity_date)

            if (today - activity_date).days <= current_streak + 1:
                current_streak += 1
            else:
                break

        # Calculate longest streak
        longest_streak = 0
        temp_streak = 1

        for i in range(1, len(activity_dates)):
            if (activity_dates[i] - activity_dates[i-1]).days == 1:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 1

        return {
            'current_streak': current_streak,
            'longest_streak': max(longest_streak, current_streak),
            'last_activity': activity_dates[-1].isoformat() if activity_dates else None
        }

    def _summarize_activities(self, activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize activity counts"""
        summary = {
            'exercises_completed': 0,
            'patterns_resolved': 0,
            'knowledge_contributions': 0,
            'total_activities': len(activities)
        }

        for activity in activities:
            activity_type = activity.get('type')

            if activity_type == 'exercise_completion':
                summary['exercises_completed'] += 1
            elif activity_type == 'pattern_resolution':
                summary['patterns_resolved'] += 1
            elif activity_type == 'knowledge_contribution':
                summary['knowledge_contributions'] += 1

        return summary

    def _create_badge_record(self, badge_id: str, earned_at: Optional[datetime]) -> Dict[str, Any]:
        """Create badge record"""
        # Badge metadata (would come from database)
        badge_meta = {
            'first_timer': {'category': 'frequency', 'name': 'First Timer'},
            'regular_practitioner': {'category': 'frequency', 'name': 'Regular Practitioner'},
            'exercise_champion': {'category': 'frequency', 'name': 'Exercise Champion'},
            'bronze_response': {'category': 'performance', 'name': 'Bronze Response'},
            'silver_response': {'category': 'performance', 'name': 'Silver Response'},
            'gold_response': {'category': 'performance', 'name': 'Gold Response'},
            'platinum_response': {'category': 'performance', 'name': 'Platinum Response'},
            'rising_star': {'category': 'improvement', 'name': 'Rising Star'},
            'rapid_learner': {'category': 'improvement', 'name': 'Rapid Learner'}
        }

        meta = badge_meta.get(badge_id, {'category': 'specialty', 'name': badge_id.replace('_', ' ').title()})

        return {
            'badge_id': badge_id,
            'name': meta['name'],
            'category': meta['category'],
            'earned_at': earned_at.isoformat() if earned_at else datetime.now().isoformat()
        }

    def _has_badge(self, badges: List[Dict[str, Any]], badge_id: str) -> bool:
        """Check if badge already earned"""
        return any(b['badge_id'] == badge_id for b in badges)

    def _empty_profile(self, user_id: str) -> Dict[str, Any]:
        """Empty gamification profile"""
        return {
            'user_id': user_id,
            'total_points': 0,
            'level': 1,
            'level_name': 'Novice',
            'points_to_next_level': 500,
            'progress_to_next_level': 0,
            'badges': [],
            'badge_count': 0,
            'current_streak_days': 0,
            'longest_streak_days': 0,
            'last_activity_date': None,
            'achievements': [],
            'activity_summary': {
                'exercises_completed': 0,
                'patterns_resolved': 0,
                'knowledge_contributions': 0,
                'total_activities': 0
            }
        }


class LeaderboardGenerator:
    """
    Generates leaderboards

    Types:
    - Global (all users)
    - Team (specific team)
    - Monthly/Quarterly (time-based)
    - Scenario-specific
    """

    def __init__(self):
        pass

    def generate_global_leaderboard(
        self,
        user_profiles: List[Dict[str, Any]],
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Generate global leaderboard by total points"""
        if not user_profiles:
            return []

        # Sort by total points
        sorted_users = sorted(
            user_profiles,
            key=lambda x: x.get('total_points', 0),
            reverse=True
        )

        # Build leaderboard
        leaderboard = []

        for rank, profile in enumerate(sorted_users[:limit], start=1):
            leaderboard.append({
                'rank': rank,
                'user_id': profile.get('user_id'),
                'total_points': profile.get('total_points', 0),
                'level': profile.get('level', 1),
                'level_name': profile.get('level_name', 'Novice'),
                'badge_count': profile.get('badge_count', 0),
                'current_streak': profile.get('current_streak_days', 0)
            })

        return leaderboard

    def generate_monthly_leaderboard(
        self,
        user_activities: Dict[str, List[Dict[str, Any]]],
        year: int,
        month: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Generate monthly leaderboard"""
        monthly_scores = {}

        for user_id, activities in user_activities.items():
            # Filter activities for this month
            monthly_activities = [
                a for a in activities
                if isinstance(a.get('timestamp'), datetime) and
                a.get('timestamp').year == year and
                a.get('timestamp').month == month
            ]

            if monthly_activities:
                # Calculate points for this month
                points = sum(
                    100 if a.get('type') == 'exercise_completion' else
                    150 if a.get('type') == 'pattern_resolution' else
                    75 if a.get('type') == 'knowledge_contribution' else 0
                    for a in monthly_activities
                )

                monthly_scores[user_id] = {
                    'user_id': user_id,
                    'points': points,
                    'activities': len(monthly_activities)
                }

        # Sort and rank
        sorted_users = sorted(
            monthly_scores.values(),
            key=lambda x: x['points'],
            reverse=True
        )

        leaderboard = []

        for rank, user_data in enumerate(sorted_users[:limit], start=1):
            leaderboard.append({
                'rank': rank,
                'user_id': user_data['user_id'],
                'monthly_points': user_data['points'],
                'monthly_activities': user_data['activities']
            })

        return leaderboard

    def generate_scenario_leaderboard(
        self,
        user_activities: Dict[str, List[Dict[str, Any]]],
        scenario_type: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Generate scenario-specific leaderboard"""
        scenario_scores = {}

        for user_id, activities in user_activities.items():
            # Filter for this scenario
            scenario_activities = [
                a for a in activities
                if a.get('type') == 'exercise_completion' and
                a.get('scenario_type') == scenario_type
            ]

            if scenario_activities:
                avg_score = sum(a.get('score', 0) for a in scenario_activities) / len(scenario_activities)

                scenario_scores[user_id] = {
                    'user_id': user_id,
                    'avg_score': round(avg_score, 2),
                    'exercise_count': len(scenario_activities),
                    'best_score': max(a.get('score', 0) for a in scenario_activities)
                }

        # Sort by avg score
        sorted_users = sorted(
            scenario_scores.values(),
            key=lambda x: (x['avg_score'], x['exercise_count']),
            reverse=True
        )

        leaderboard = []

        for rank, user_data in enumerate(sorted_users[:limit], start=1):
            leaderboard.append({
                'rank': rank,
                'user_id': user_data['user_id'],
                'avg_score': user_data['avg_score'],
                'exercise_count': user_data['exercise_count'],
                'best_score': user_data['best_score']
            })

        return leaderboard
