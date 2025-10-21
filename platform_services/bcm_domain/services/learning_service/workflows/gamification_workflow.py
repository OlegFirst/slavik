"""
Gamification Workflow
Points, achievements, badges, and streak management

Integrates with:
- learning_seed.sql: achievement_types, points_actions
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

class ActionCategory(str, Enum):
    """Action categories for points"""
    TRAINING = "training"
    COMPETENCY = "competency"
    AWARENESS = "awareness"
    CONTENT = "content"
    COLLABORATION = "collaboration"
    ENGAGEMENT = "engagement"

# Points mapping (synced with points_actions seed data)
POINTS_MAP = {
    # Training actions
    'training_start': 10,
    'training_complete': 100,
    'assessment_pass': 50,
    'assessment_excellence': 100,  # 90%+
    'certification_earned': 500,

    # Competency actions
    'competency_level_up': 150,
    'gap_identified': 25,
    'gap_closed': 200,

    # Awareness actions
    'awareness_participate': 25,
    'awareness_survey': 15,

    # Content actions
    'content_create': 50,
    'content_review': 10,
    'content_use': 5,
    'content_rate': 3,

    # Collaboration actions
    'help_peer': 50,
    'mentor_session': 75,
    'team_challenge': 100,

    # Engagement actions
    'daily_login': 2,
    'streak_milestone': 25,
    'share_knowledge': 20,
}

# Achievement thresholds
ACHIEVEMENT_THRESHOLDS = {
    # Training achievements
    'first_training': {'condition': 'training_complete', 'count': 1, 'points': 50},
    'training_streak_7': {'condition': 'consecutive_days_training', 'count': 7, 'points': 100},
    'training_streak_30': {'condition': 'consecutive_days_training', 'count': 30, 'points': 500},
    'perfect_score': {'condition': 'assessment_score', 'threshold': 100, 'points': 200},
    'fast_learner': {'condition': 'training_duration', 'threshold': 0.5, 'points': 150},  # 50% faster than avg

    # Competency achievements
    'competency_master': {'condition': 'expert_level', 'count': 1, 'points': 300},
    'gap_closer': {'condition': 'gap_closed', 'count': 1, 'points': 200},
    'skill_collector': {'condition': 'competent_areas', 'count': 5, 'points': 400},

    # Contribution achievements
    'content_creator': {'condition': 'content_created', 'count': 1, 'points': 50},
    'template_master': {'condition': 'templates_created', 'count': 10, 'points': 250},
    'scenario_expert': {'condition': 'scenarios_created', 'count': 5, 'points': 100},
    'quality_reviewer': {'condition': 'reviews_provided', 'count': 20, 'points': 200},
    'power_user': {'condition': 'system_usage_days', 'count': 60, 'points': 150},
    'mentor': {'condition': 'mentoring_sessions', 'count': 10, 'points': 300},

    # Certification achievements
    'iso_certified': {'condition': 'iso_certification', 'count': 1, 'points': 1000},
    'bc_professional': {'condition': 'advanced_training', 'count': 3, 'points': 500},

    # Team achievements
    'team_player': {'condition': 'team_challenges', 'count': 5, 'points': 75},
    'department_champion': {'condition': 'department_rank', 'rank': 1, 'points': 400},
    'awareness_ambassador': {'condition': 'awareness_promoted', 'count': 10, 'points': 150},
}

def calculate_points(action_code: str) -> int:
    """Get points for an action"""
    return POINTS_MAP.get(action_code, 0)

def award_points(person_id: str, action_code: str, context: dict = None) -> dict:
    """
    Award points for an action
    Returns: {'points': int, 'total_points': int, 'achievements_unlocked': list}
    """
    points = calculate_points(action_code)

    # Bonus multipliers
    if context:
        # Streak bonus
        if 'streak_count' in context and context['streak_count'] > 7:
            multiplier = 1 + (min(context['streak_count'], 30) * 0.01)  # Up to 30% bonus
            points = int(points * multiplier)

        # Excellence bonus (for assessments)
        if 'score' in context and context['score'] >= 90:
            points += POINTS_MAP.get('assessment_excellence', 0)

    return {
        'points': points,
        'action_code': action_code,
        'context': context,
    }

def check_achievements(person_id: str, person_stats: dict) -> List[dict]:
    """
    Check if any achievements should be unlocked
    person_stats: dict with user statistics
    Returns: list of unlocked achievements
    """
    unlocked = []

    for achievement_code, criteria in ACHIEVEMENT_THRESHOLDS.items():
        condition = criteria['condition']

        # Check if condition is met
        met = False
        if condition in person_stats:
            if 'count' in criteria:
                met = person_stats[condition] >= criteria['count']
            elif 'threshold' in criteria:
                met = person_stats[condition] >= criteria['threshold']
            elif 'rank' in criteria:
                met = person_stats.get(condition) == criteria['rank']

        if met and not person_stats.get(f'achieved_{achievement_code}', False):
            unlocked.append({
                'achievement_code': achievement_code,
                'points': criteria['points'],
                'condition_met': condition,
            })

    return unlocked

def calculate_streak(person_id: str, activity_dates: List[datetime]) -> dict:
    """
    Calculate learning streak
    Returns: {'current_streak': int, 'longest_streak': int, 'is_active': bool}
    """
    if not activity_dates:
        return {'current_streak': 0, 'longest_streak': 0, 'is_active': False}

    # Sort dates
    dates = sorted(set(d.date() for d in activity_dates))

    current_streak = 1
    longest_streak = 1
    temp_streak = 1

    for i in range(1, len(dates)):
        diff = (dates[i] - dates[i-1]).days

        if diff == 1:  # Consecutive day
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 1

    # Check if streak is active (last activity was today or yesterday)
    today = datetime.now().date()
    is_active = dates[-1] in [today, today - timedelta(days=1)]

    if is_active:
        # Calculate current streak from most recent date
        current_streak = 1
        for i in range(len(dates) - 2, -1, -1):
            if (dates[i+1] - dates[i]).days == 1:
                current_streak += 1
            else:
                break

    return {
        'current_streak': current_streak if is_active else 0,
        'longest_streak': longest_streak,
        'is_active': is_active,
        'last_activity': dates[-1] if dates else None,
    }

def get_leaderboard_rank(person_id: str, tenant_id: str, all_scores: Dict[str, int]) -> int:
    """Get person's rank in leaderboard"""
    sorted_scores = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
    for rank, (pid, score) in enumerate(sorted_scores, start=1):
        if pid == person_id:
            return rank
    return len(sorted_scores) + 1

def calculate_level(total_points: int) -> dict:
    """
    Calculate user level based on total points
    Returns: {'level': int, 'title': str, 'next_level_points': int}
    """
    # Level thresholds
    levels = [
        (0, 'Beginner'),
        (100, 'Learner'),
        (500, 'Practitioner'),
        (1000, 'Professional'),
        (2500, 'Expert'),
        (5000, 'Master'),
        (10000, 'Champion'),
    ]

    current_level = 0
    current_title = 'Beginner'
    next_threshold = 100

    for threshold, title in reversed(levels):
        if total_points >= threshold:
            current_level = levels.index((threshold, title)) + 1
            current_title = title
            # Find next level
            next_idx = levels.index((threshold, title)) + 1
            if next_idx < len(levels):
                next_threshold = levels[next_idx][0]
            else:
                next_threshold = None
            break

    return {
        'level': current_level,
        'title': current_title,
        'points': total_points,
        'next_level_points': next_threshold,
        'progress_to_next': ((total_points - levels[current_level-1][0]) /
                            (next_threshold - levels[current_level-1][0]) * 100) if next_threshold else 100,
    }

def get_badge_color(achievement_level: str) -> str:
    """Get badge color for achievement level"""
    colors = {
        'bronze': '#CD7F32',
        'silver': '#C0C0C0',
        'gold': '#FFD700',
        'platinum': '#E5E4E2',
    }
    return colors.get(achievement_level, '#808080')

def get_badge_icon(achievement_code: str) -> str:
    """Get badge icon for achievement"""
    icons = {
        'first_training': '',
        'training_streak_7': '',
        'training_streak_30': '',
        'perfect_score': '',
        'fast_learner': '',
        'competency_master': '',
        'gap_closer': '',
        'skill_collector': '',
        'content_creator': '️',
        'template_master': '',
        'scenario_expert': '',
        'quality_reviewer': '️',
        'power_user': '️',
        'mentor': '',
        'iso_certified': '',
        'bc_professional': '',
        'team_player': '',
        'department_champion': '',
        'awareness_ambassador': '',
    }
    return icons.get(achievement_code, '️')
