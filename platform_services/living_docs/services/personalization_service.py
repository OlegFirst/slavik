"""
 Documentation Personalization Service

Makes documentation personal for EVERY user.

Same topic, completely different experience based on:
- Industry (healthcare vs finance vs manufacturing)
- Role (executive vs BCM manager vs IT admin)
- Experience level (beginner vs expert)
- Current context (what they're doing right now)
- Learning style (visual vs text vs interactive)

Example:
>>> personalizer = PersonalizationService()
>>>
>>> # Hospital administrator (expert)
>>> content = await personalizer.personalize(
...     page_id="rto-calculation",
...     user_id="admin-123"
... )
>>> # Returns: Advanced healthcare-specific guide
>>>
>>> # Small clinic owner (beginner)
>>> content = await personalizer.personalize(
...     page_id="rto-calculation",
...     user_id="clinic-456"
... )
>>> # Returns: Simple step-by-step wizard with examples
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PersonalizationService:
    """
    Personalizes documentation for each user

    Netflix-style personalization for BCM docs!
    """

    def __init__(
        self,
        db,
        ai_client,
        analytics_service,
        collective_intelligence
    ):
        self.db = db
        self.ai = ai_client
        self.analytics = analytics_service
        self.collective = collective_intelligence

        logger.info(" Personalization Service initialized")

    async def personalize(
        self,
        page_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Personalize documentation page for user

        Returns completely customized content
        """

        # Build user profile
        profile = await self.build_user_profile(user_id)

        # Get base content
        base_content = await self._get_base_content(page_id)

        # Personalize content
        personalized = await self._personalize_content(
            base_content=base_content,
            profile=profile,
            page_id=page_id
        )

        # Add personalized recommendations
        recommendations = await self._get_next_steps(user_id, profile)

        # Add relevant examples
        examples = await self._get_personalized_examples(
            page_id=page_id,
            profile=profile
        )

        return {
            'content': personalized,
            'examples': examples,
            'next_steps': recommendations,
            'personalization': {
                'industry': profile['industry'],
                'level': profile['experience_level'],
                'customized_for': profile['user_type']
            }
        }

    async def build_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Build comprehensive user profile

        Analyzes:
        - Explicit info (org, role)
        - Behavioral patterns (what they read, how long, what they ask)
        - Skill level inference
        - Learning preferences
        """

        # Get explicit profile
        user = await self._get_user_data(user_id)

        # Get organization context
        org = await self._get_organization_data(user['org_id'])

        # Analyze behavior
        behavior = await self.analytics.get_user_behavior(user_id, days=30)

        # Infer experience level
        experience_level = await self._infer_experience_level(user_id, behavior)

        # Infer learning style
        learning_style = await self._infer_learning_style(user_id, behavior)

        # Get current context
        current_task = await self._get_current_task(user_id)

        profile = {
            # Explicit
            'user_id': user_id,
            'user_type': user.get('role', 'user'),  # executive, manager, admin
            'industry': org.get('industry', 'general'),
            'org_size': org.get('size', 'medium'),
            'region': org.get('region', 'unknown'),

            # Inferred
            'experience_level': experience_level,  # beginner, intermediate, expert
            'learning_style': learning_style,  # visual, textual, interactive, mixed

            # Context
            'current_task': current_task,  # what they're working on now
            'completed_workflows': behavior.get('completed_workflows', []),
            'time_on_platform': behavior.get('total_time_minutes', 0),
            'preferred_topics': behavior.get('top_topics', []),

            # Preferences
            'prefers_examples': behavior.get('example_clicks', 0) > 5,
            'prefers_video': behavior.get('video_plays', 0) > 3,
            'prefers_interactive': behavior.get('tool_usage', 0) > 5
        }

        return profile

    async def _personalize_content(
        self,
        base_content: str,
        profile: Dict[str, Any],
        page_id: str
    ) -> str:
        """
        Personalize content using AI

        Transforms base content based on user profile
        """

        # Build personalization prompt
        prompt = f"""Personalize this documentation for specific user:

BASE CONTENT:
{base_content}

USER PROFILE:
- Industry: {profile['industry']}
- Organization size: {profile['org_size']}
- Role: {profile['user_type']}
- Experience level: {profile['experience_level']}
- Current task: {profile['current_task']}
- Learning style: {profile['learning_style']}

PERSONALIZATION REQUIREMENTS:

1. INDUSTRY EXAMPLES:
   - Replace generic examples with {profile['industry']}-specific ones
   - Use terminology familiar to {profile['industry']} professionals
   - Reference industry-specific challenges

2. COMPLEXITY LEVEL:
   - Adjust for {profile['experience_level']} level
   - {"Add explanations for basics" if profile['experience_level'] == 'beginner' else "Skip basics, focus on advanced concepts"}
   - {"Use simple language" if profile['experience_level'] == 'beginner' else "Use professional terminology"}

3. FORMAT:
   - {"Add visual diagrams" if profile['learning_style'] in ['visual', 'mixed'] else "Focus on text explanations"}
   - {"Include interactive elements" if profile['prefers_interactive'] else "Provide static examples"}
   - {"Suggest video walkthrough" if profile['prefers_video'] else "Detailed written guide"}

4. CONTEXT:
   - Relate to their current task: {profile['current_task']}
   - Reference their organization size: {profile['org_size']}
   - Suggest next steps relevant to their progress

Keep structure and accuracy. Make it feel custom-made for THIS user.

PERSONALIZED VERSION:
"""

        # AI generates personalized version
        personalized = await self.ai.generate(
            prompt=prompt,
            temperature=0.4,
            max_tokens=2500
        )

        logger.info(f" Content personalized for {profile['user_type']} in {profile['industry']}")

        return personalized

    async def _get_personalized_examples(
        self,
        page_id: str,
        profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get examples personalized for user

        Queries collective intelligence for industry-specific examples
        """

        # Map page to problem type
        problem_type = self._page_to_problem_type(page_id)

        if not problem_type:
            return []

        # Query collective intelligence with user context
        wisdom = await self.collective.query_collective_wisdom(
            problem_type=problem_type,
            org_context={
                'industry': profile['industry'],
                'size': profile['org_size'],
                'region': profile['region']
            },
            min_cases=3
        )

        # Format examples
        examples = []
        for i, pattern in enumerate(wisdom.get('patterns', [])[:3]):
            examples.append({
                'id': f"example-{i+1}",
                'title': pattern.get('pattern_name', '').replace('_', ' ').title(),
                'description': pattern.get('description', ''),
                'frequency': pattern.get('frequency', ''),
                'confidence': pattern.get('confidence', 0),
                'industry_specific': True,
                'source': f"{wisdom.get('privacy', {}).get('source_count', 0)} similar organizations"
            })

        return examples

    async def _get_next_steps(
        self,
        user_id: str,
        profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get personalized next steps

        Based on:
        - Current task
        - Completed workflows
        - User's progress
        """

        current_task = profile['current_task']
        completed = profile['completed_workflows']

        next_steps = []

        # Task-specific recommendations
        if current_task == 'bia':
            if 'process_identification' not in completed:
                next_steps.append({
                    'action': 'identify_critical_processes',
                    'title': 'Identify Your Critical Processes',
                    'description': f'Start your BIA by identifying critical processes for a {profile["org_size"]} {profile["industry"]} organization',
                    'tool': 'interactive_process_wizard',
                    'estimated_time': '15-30 minutes'
                })
            elif 'dependency_mapping' not in completed:
                next_steps.append({
                    'action': 'map_dependencies',
                    'title': 'Map Process Dependencies',
                    'description': 'Identify what each critical process depends on',
                    'tool': 'dependency_mapper',
                    'estimated_time': '30-60 minutes'
                })
            elif 'rto_calculation' not in completed:
                next_steps.append({
                    'action': 'calculate_rto',
                    'title': 'Determine Recovery Objectives',
                    'description': 'Calculate RTO for each critical process',
                    'tool': 'rto_calculator',
                    'estimated_time': '20-40 minutes'
                })

        # Add learning recommendations
        if profile['experience_level'] == 'beginner':
            next_steps.append({
                'action': 'learn',
                'title': 'BCM Fundamentals Course',
                'description': 'Build strong foundation in BCM concepts',
                'tool': 'learning_path',
                'estimated_time': '2-3 hours'
            })

        return next_steps[:3]  # Top 3

    async def _infer_experience_level(
        self,
        user_id: str,
        behavior: Dict[str, Any]
    ) -> str:
        """
        Infer user's experience level

        Signals:
        - Time on platform (more = likely experienced)
        - Pages visited (advanced topics = expert)
        - Questions asked (basic questions = beginner)
        - Workflow completion speed
        - Tool usage patterns
        """

        score = 0

        # Check 1: Time on platform
        total_time = behavior.get('total_time_minutes', 0)
        if total_time > 600:  # 10+ hours
            score += 3
        elif total_time > 120:  # 2+ hours
            score += 1

        # Check 2: Advanced topic views
        advanced_topics = ['iso22301', 'advanced_risk', 'integration', 'testing']
        viewed_topics = behavior.get('top_topics', [])
        advanced_views = sum(1 for topic in viewed_topics if any(adv in topic for adv in advanced_topics))
        score += advanced_views

        # Check 3: Workflow completion
        completed_count = len(behavior.get('completed_workflows', []))
        if completed_count >= 5:
            score += 3
        elif completed_count >= 2:
            score += 1

        # Check 4: Tool usage (experts use tools more)
        tool_usage = behavior.get('tool_usage', 0)
        if tool_usage > 10:
            score += 2

        # Determine level
        if score >= 7:
            return 'expert'
        elif score >= 3:
            return 'intermediate'
        else:
            return 'beginner'

    async def _infer_learning_style(
        self,
        user_id: str,
        behavior: Dict[str, Any]
    ) -> str:
        """
        Infer user's learning style

        Signals:
        - Video plays (visual learner)
        - Example clicks (practical learner)
        - Tool usage (interactive learner)
        - Reading time (textual learner)
        """

        video_plays = behavior.get('video_plays', 0)
        example_clicks = behavior.get('example_clicks', 0)
        tool_usage = behavior.get('tool_usage', 0)
        avg_reading_time = behavior.get('avg_reading_time', 0)

        scores = {
            'visual': video_plays * 2,
            'textual': avg_reading_time // 30,  # Convert seconds to score
            'interactive': tool_usage,
            'practical': example_clicks
        }

        # Find dominant style
        if max(scores.values()) == 0:
            return 'mixed'

        dominant = max(scores.items(), key=lambda x: x[1])[0]

        # Check if mixed (multiple high scores)
        high_scores = [k for k, v in scores.items() if v >= max(scores.values()) * 0.7]
        if len(high_scores) > 1:
            return 'mixed'

        return dominant

    async def _get_current_task(self, user_id: str) -> Optional[str]:
        """Get user's current active task"""
        # Query database for active workflow
        # Placeholder
        return 'bia'  # or 'response_planning', 'testing', etc.

    def _page_to_problem_type(self, page_id: str) -> Optional[str]:
        """Map page ID to problem type"""
        mapping = {
            'rto-calculation': 'rto_determination',
            'process-identification': 'critical_process_prioritization',
            'dependency-mapping': 'supply_chain_complexity',
            'executive-engagement': 'executive_engagement',
            'risk-assessment': 'risk_identification'
        }
        return mapping.get(page_id)

    async def _get_base_content(self, page_id: str) -> str:
        """Get base documentation content"""
        # Query database
        # Placeholder
        return f"Base content for {page_id}"

    async def _get_user_data(self, user_id: str) -> Dict:
        """Get user data from database"""
        # Placeholder
        return {
            'role': 'manager',
            'org_id': 'org-123'
        }

    async def _get_organization_data(self, org_id: str) -> Dict:
        """Get organization data"""
        # Placeholder
        return {
            'industry': 'healthcare',
            'size': 'medium',
            'region': 'pacific_northwest'
        }


class UserJourneyPersonalizer:
    """
    Personalizes entire user journey

    Not just single pages - entire learning path
    """

    def __init__(self, personalization_service):
        self.personalizer = personalization_service

    async def get_personalized_journey(
        self,
        user_id: str,
        goal: str  # e.g., "complete_bia", "iso_certification"
    ) -> Dict[str, Any]:
        """
        Get personalized learning/workflow journey

        Adapts entire path based on user profile
        """

        profile = await self.personalizer.build_user_profile(user_id)

        # Build journey based on goal and profile
        if goal == 'complete_bia':
            journey = await self._build_bia_journey(profile)
        elif goal == 'iso_certification':
            journey = await self._build_iso_journey(profile)
        else:
            journey = await self._build_custom_journey(goal, profile)

        return journey

    async def _build_bia_journey(self, profile: Dict) -> Dict[str, Any]:
        """
        Build personalized BIA journey

        Different paths for:
        - Beginner vs expert
        - Small clinic vs large hospital
        - With vs without external help
        """

        steps = []

        if profile['experience_level'] == 'beginner':
            # Add foundational steps
            steps.append({
                'id': 'bcm_basics',
                'title': 'BCM Fundamentals',
                'type': 'learning',
                'estimated_time': '1 hour',
                'required': True
            })

        # Core BIA steps (personalized)
        steps.extend([
            {
                'id': 'process_id',
                'title': f'Identify Critical Processes ({profile["industry"]})',
                'type': 'interactive_tool',
                'estimated_time': '30-60 min',
                'industry_specific': True
            },
            {
                'id': 'impact_analysis',
                'title': 'Analyze Business Impact',
                'type': 'guided_workflow',
                'estimated_time': '1-2 hours'
            },
            {
                'id': 'rto_rpo',
                'title': 'Determine Recovery Objectives',
                'type': 'calculator_tool',
                'estimated_time': '30-45 min'
            }
        ])

        if profile['org_size'] in ['large', 'enterprise']:
            # Add complexity for large orgs
            steps.append({
                'id': 'dependency_mapping',
                'title': 'Map Inter-Department Dependencies',
                'type': 'advanced_tool',
                'estimated_time': '2-3 hours'
            })

        return {
            'goal': 'complete_bia',
            'personalized_for': profile,
            'total_estimated_time': self._calculate_total_time(steps),
            'steps': steps,
            'completion_percentage': await self._get_completion_percentage(
                profile['user_id'],
                steps
            )
        }

    def _calculate_total_time(self, steps: List[Dict]) -> str:
        """Calculate total estimated time"""
        # Simple implementation
        return "4-8 hours"

    async def _get_completion_percentage(
        self,
        user_id: str,
        steps: List[Dict]
    ) -> float:
        """Calculate journey completion percentage"""
        # Check which steps completed
        # Placeholder
        return 0.35  # 35% complete
