"""
📚 Documentation Evolution Engine

Self-evolving documentation that learns from user interactions.

MAGIC:
- Learns from every user interaction
- Detects knowledge gaps automatically
- Improves unclear content with AI
- Generates new topics on demand
- Quality improves over time

Example:
>>> engine = DocumentationEvolutionEngine()
>>>
>>> # User reads page
>>> await engine.track_interaction(
...     page="rto-calculation",
...     user_id="user-123",
...     time_spent=45,  # seconds
...     helpful_vote=False
... )
>>>
>>> # Engine detects low quality
>>> improvements = await engine.detect_improvements_needed()
>>> # [{"page": "rto-calculation", "issue": "too_short", "priority": "high"}]
>>>
>>> # AI rewrites
>>> new_content = await engine.improve_content(
...     page="rto-calculation",
...     issues=["too_short", "no_examples"],
...     user_context={"industry": "healthcare", "level": "beginner"}
... )
>>>
>>> # Deploy improved version
>>> await engine.deploy_improvement(page="rto-calculation", content=new_content)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio
import logging

logger = logging.getLogger(__name__)

class DocumentationEvolutionEngine:
    """
    Self-evolving documentation system

    Continuously learns and improves from:
    - User interactions
    - Search patterns
    - Feedback
    - Usage analytics
    """

    def __init__(
        self,
        db,
        ai_client,
        collective_intelligence
    ):
        self.db = db
        self.ai = ai_client
        self.collective = collective_intelligence

        # Analytics storage
        self.page_analytics = defaultdict(lambda: {
            'views': 0,
            'avg_time': 0,
            'helpful_votes': 0,
            'not_helpful_votes': 0,
            'searches_leading_here': [],
            'exit_rate': 0
        })

        logger.info("📚 Documentation Evolution Engine initialized")

    async def track_interaction(
        self,
        page_id: str,
        user_id: str,
        event_type: str,  # view, search, vote, exit
        metadata: Dict[str, Any]
    ):
        """
        Track user interaction with documentation

        Every interaction helps system learn
        """

        interaction = {
            'page_id': page_id,
            'user_id': user_id,
            'event_type': event_type,
            'metadata': metadata,
            'timestamp': datetime.utcnow()
        }

        # Store interaction
        await self._store_interaction(interaction)

        # Update analytics
        await self._update_analytics(page_id, event_type, metadata)

        # Real-time learning
        if event_type == 'vote' and metadata.get('vote') == 'not_helpful':
            # Immediate flag for review
            await self._flag_for_improvement(page_id, reason="negative_feedback")

    async def detect_improvements_needed(self) -> List[Dict[str, Any]]:
        """
        Detect which documentation pages need improvement

        Analyzes:
        - Low engagement (bounce rate, time spent)
        - Negative feedback
        - Search queries without results
        - Confusion patterns

        Returns prioritized list of improvements
        """

        improvements = []

        for page_id, analytics in self.page_analytics.items():
            issues = []
            priority = 0

            # Check 1: Low time spent
            if analytics['avg_time'] < 30 and analytics['views'] > 10:
                issues.append("too_short_or_confusing")
                priority += 2

            # Check 2: High bounce rate
            if analytics['exit_rate'] > 0.7:
                issues.append("not_meeting_expectations")
                priority += 3

            # Check 3: Negative feedback
            total_votes = analytics['helpful_votes'] + analytics['not_helpful_votes']
            if total_votes > 5:
                helpful_ratio = analytics['helpful_votes'] / total_votes
                if helpful_ratio < 0.4:
                    issues.append("low_quality_content")
                    priority += 5  # High priority!

            # Check 4: No examples
            content = await self._get_page_content(page_id)
            if not self._has_examples(content):
                issues.append("missing_examples")
                priority += 1

            if issues:
                improvements.append({
                    'page_id': page_id,
                    'issues': issues,
                    'priority': priority,
                    'analytics': analytics
                })

        # Sort by priority
        improvements.sort(key=lambda x: -x['priority'])

        logger.info(f"🔍 Detected {len(improvements)} pages needing improvement")

        return improvements

    async def improve_content(
        self,
        page_id: str,
        issues: List[str],
        user_context: Optional[Dict] = None
    ) -> str:
        """
        Improve documentation content using AI

        AI rewrites based on:
        - Identified issues
        - User context (industry, level)
        - Collective intelligence (real examples)
        - Best practices
        """

        # Get current content
        current_content = await self._get_page_content(page_id)

        # Get examples from collective intelligence
        examples = await self._get_relevant_examples(page_id, user_context)

        # Build AI prompt
        prompt = self._build_improvement_prompt(
            current_content=current_content,
            issues=issues,
            examples=examples,
            user_context=user_context
        )

        # AI generates improved content
        improved_content = await self.ai.generate(
            prompt=prompt,
            temperature=0.3,  # More focused
            max_tokens=2000
        )

        logger.info(f"✨ Content improved for {page_id}")

        return improved_content

    async def detect_knowledge_gaps(self) -> List[Dict[str, Any]]:
        """
        Detect missing documentation topics

        Analyzes:
        - Search queries with no results
        - Questions users ask
        - Common stuck points
        """

        gaps = []

        # Get searches without results
        failed_searches = await self._get_failed_searches(days=7)

        # Cluster similar searches
        clusters = self._cluster_searches(failed_searches)

        for cluster in clusters:
            if cluster['count'] >= 3:  # Minimum 3 users searched for this
                gaps.append({
                    'topic': cluster['topic'],
                    'search_queries': cluster['queries'],
                    'user_count': cluster['count'],
                    'priority': cluster['count']  # More searches = higher priority
                })

        logger.info(f"🔍 Detected {len(gaps)} knowledge gaps")

        return gaps

    async def generate_missing_topic(
        self,
        topic: str,
        search_queries: List[str],
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate new documentation topic using AI

        Creates complete new page:
        - Introduction
        - Step-by-step guide
        - Examples
        - Related topics
        """

        # Get relevant knowledge
        collective_wisdom = await self.collective.query_collective_wisdom(
            problem_type=self._extract_problem_type(topic),
            org_context=user_context or {}
        )

        # Build comprehensive prompt
        prompt = f"""Generate documentation for: {topic}

Users are searching for:
{chr(10).join(f'- {q}' for q in search_queries)}

Create comprehensive guide with:
1. Clear explanation (what, why, when)
2. Step-by-step instructions
3. Concrete examples
4. Common pitfalls
5. Related topics

Use collective wisdom:
{collective_wisdom}

Context: {user_context}

Write in friendly, accessible style. Use examples heavily.
"""

        # AI generates content
        content = await self.ai.generate(
            prompt=prompt,
            temperature=0.5,
            max_tokens=3000
        )

        return {
            'topic': topic,
            'content': content,
            'generated_at': datetime.utcnow(),
            'source': 'ai_generated',
            'based_on_searches': search_queries
        }

    async def personalize_content(
        self,
        page_id: str,
        user_context: Dict[str, Any]
    ) -> str:
        """
        Personalize documentation for specific user

        Adjusts:
        - Examples (industry-specific)
        - Complexity level (beginner vs expert)
        - Terminology (familiar to user)
        """

        # Get base content
        base_content = await self._get_page_content(page_id)

        # Get user's experience level
        user_level = await self._infer_user_level(user_context['user_id'])

        # Get industry-specific examples
        industry_examples = await self._get_industry_examples(
            page_id,
            user_context.get('industry')
        )

        # AI personalizes
        prompt = f"""Personalize this documentation:

{base_content}

User context:
- Industry: {user_context.get('industry')}
- Experience level: {user_level}
- Current task: {user_context.get('current_task')}

Replace generic examples with {user_context.get('industry')}-specific ones:
{industry_examples}

Adjust complexity for {user_level} level.

Keep structure, improve relevance.
"""

        personalized = await self.ai.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=2000
        )

        return personalized

    async def run_continuous_improvement(self):
        """
        Continuous improvement loop

        Runs forever:
        1. Analyze interactions
        2. Detect improvements needed
        3. Generate improvements
        4. A/B test
        5. Deploy winners
        6. Repeat
        """

        logger.info("🔄 Starting continuous improvement loop")

        while True:
            try:
                # Detect improvements needed
                improvements = await self.detect_improvements_needed()

                # Process top priority items
                for improvement in improvements[:5]:  # Top 5
                    page_id = improvement['page_id']
                    issues = improvement['issues']

                    logger.info(f"🔧 Improving {page_id}: {issues}")

                    # Generate improved version
                    new_content = await self.improve_content(
                        page_id=page_id,
                        issues=issues
                    )

                    # A/B test (50% users see new version)
                    await self._start_ab_test(
                        page_id=page_id,
                        variant_a=await self._get_page_content(page_id),
                        variant_b=new_content,
                        split=0.5
                    )

                # Detect knowledge gaps
                gaps = await self.detect_knowledge_gaps()

                # Generate missing topics
                for gap in gaps[:3]:  # Top 3 gaps
                    logger.info(f"📝 Generating new topic: {gap['topic']}")

                    new_topic = await self.generate_missing_topic(
                        topic=gap['topic'],
                        search_queries=gap['search_queries']
                    )

                    # Create new page
                    await self._create_new_page(new_topic)

                # Sleep for 1 hour
                await asyncio.sleep(3600)

            except Exception as e:
                logger.error(f"❌ Improvement loop error: {e}")
                await asyncio.sleep(300)  # Retry in 5 minutes

    # ================================================
    # HELPER METHODS
    # ================================================

    def _build_improvement_prompt(
        self,
        current_content: str,
        issues: List[str],
        examples: List[Dict],
        user_context: Optional[Dict]
    ) -> str:
        """Build AI prompt for content improvement"""

        issues_text = "\n".join(f"- {issue}" for issue in issues)
        examples_text = "\n".join(
            f"Example {i+1}:\n{ex['content']}"
            for i, ex in enumerate(examples[:3])
        )

        prompt = f"""Improve this documentation:

CURRENT CONTENT:
{current_content}

ISSUES TO FIX:
{issues_text}

USE THESE REAL EXAMPLES:
{examples_text}

TARGET AUDIENCE:
{user_context}

REQUIREMENTS:
1. Fix all identified issues
2. Add concrete examples (using real data above)
3. Make it engaging and practical
4. Keep it concise but complete
5. Use friendly, accessible language

IMPROVED VERSION:
"""

        return prompt

    async def _get_relevant_examples(
        self,
        page_id: str,
        user_context: Optional[Dict]
    ) -> List[Dict]:
        """Get relevant examples from collective intelligence"""

        # Map page to problem type
        problem_type = self._page_to_problem_type(page_id)

        if not problem_type:
            return []

        # Query collective intelligence
        wisdom = await self.collective.query_collective_wisdom(
            problem_type=problem_type,
            org_context=user_context or {},
            min_cases=3
        )

        # Extract examples
        examples = []
        for pattern in wisdom.get('patterns', []):
            examples.append({
                'content': pattern.get('description'),
                'frequency': pattern.get('frequency'),
                'confidence': pattern.get('confidence')
            })

        return examples

    def _page_to_problem_type(self, page_id: str) -> Optional[str]:
        """Map documentation page to problem type"""

        mapping = {
            'rto-calculation': 'rto_determination',
            'process-identification': 'critical_process_prioritization',
            'dependency-mapping': 'supply_chain_complexity',
            'executive-engagement': 'executive_engagement',
        }

        return mapping.get(page_id)

    async def _get_page_content(self, page_id: str) -> str:
        """Get current page content"""
        # Placeholder - query database
        return f"Content for {page_id}"

    def _has_examples(self, content: str) -> bool:
        """Check if content has examples"""
        return 'example' in content.lower() or 'for instance' in content.lower()

    async def _store_interaction(self, interaction: Dict):
        """Store interaction in database"""
        # Placeholder - save to DB
        pass

    async def _update_analytics(
        self,
        page_id: str,
        event_type: str,
        metadata: Dict
    ):
        """Update page analytics"""

        analytics = self.page_analytics[page_id]

        if event_type == 'view':
            analytics['views'] += 1
            time_spent = metadata.get('time_spent', 0)
            # Update rolling average
            analytics['avg_time'] = (
                (analytics['avg_time'] * (analytics['views'] - 1) + time_spent)
                / analytics['views']
            )

        elif event_type == 'vote':
            if metadata.get('vote') == 'helpful':
                analytics['helpful_votes'] += 1
            else:
                analytics['not_helpful_votes'] += 1

        elif event_type == 'exit':
            analytics['exit_rate'] = (
                (analytics['exit_rate'] * (analytics['views'] - 1) + 1)
                / analytics['views']
            )

    async def _flag_for_improvement(self, page_id: str, reason: str):
        """Flag page for immediate review"""
        logger.warning(f"🚩 {page_id} flagged: {reason}")
        # Could trigger immediate improvement

    async def _get_failed_searches(self, days: int) -> List[Dict]:
        """Get search queries that returned no results"""
        # Placeholder
        return [
            {'query': 'tier 3 supplier dependencies', 'count': 15},
            {'query': 'bcm for remote work', 'count': 12},
            {'query': 'pandemic bia', 'count': 10}
        ]

    def _cluster_searches(self, searches: List[Dict]) -> List[Dict]:
        """Cluster similar search queries"""
        # Simple implementation - group by keywords
        # In production: Use embeddings

        clusters = []
        for search in searches:
            # Extract topic from query
            topic = search['query'].split()[0:3]  # First 3 words
            topic_str = ' '.join(topic)

            clusters.append({
                'topic': topic_str,
                'queries': [search['query']],
                'count': search['count']
            })

        return clusters

    def _extract_problem_type(self, topic: str) -> str:
        """Extract problem type from topic"""
        # Simple keyword matching
        if 'supplier' in topic.lower() or 'dependency' in topic.lower():
            return 'supply_chain_complexity'
        elif 'rto' in topic.lower() or 'recovery' in topic.lower():
            return 'rto_determination'
        else:
            return 'general_bcm_challenge'

    async def _get_industry_examples(
        self,
        page_id: str,
        industry: Optional[str]
    ) -> List[Dict]:
        """Get industry-specific examples"""
        # Query collective intelligence filtered by industry
        return []

    async def _infer_user_level(self, user_id: str) -> str:
        """Infer user's experience level"""
        # Analyze user's interaction history
        # Placeholder
        return "beginner"  # or "intermediate", "expert"

    async def _start_ab_test(
        self,
        page_id: str,
        variant_a: str,
        variant_b: str,
        split: float
    ):
        """Start A/B test"""
        logger.info(f"🔬 Starting A/B test for {page_id}")
        # Implement A/B testing logic

    async def _create_new_page(self, topic_data: Dict):
        """Create new documentation page"""
        logger.info(f"📄 Creating new page: {topic_data['topic']}")
        # Save to database
