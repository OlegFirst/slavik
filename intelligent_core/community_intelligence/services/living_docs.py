"""
Living Documentation Service - Community Intelligence Integration

Community-driven documentation that evolves with expert annotations,
AI synthesis, and real-world case examples.
"""

import uuid
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.database import CommunityAnnotation, SynthesizedGuidance


class LivingDocumentationService:
    """
    Community-driven documentation that evolves

    Workflow:
    1. Experts annotate clauses with interpretations
    2. AI synthesizes official + community + cases
    3. Result: living, practical guidance
    """

    def __init__(
        self,
        db: AsyncSession,
        knowledge_graph,
        case_library,
        llm_client
    ):
        self.db = db
        self.kg = knowledge_graph
        self.cases = case_library
        self.llm = llm_client

    async def add_annotation(
        self,
        user_id: str,
        clause_id: str,
        interpretation: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Expert adds interpretation to clause

        Context includes:
        - industry: healthcare, finance, etc
        - org_size: small, medium, large
        - practical_examples: real examples
        """

        annotation = CommunityAnnotation(
            id=uuid.uuid4(),
            clause_id=clause_id,
            standard=context.get('standard', 'ISO22301'),
            author_id=uuid.UUID(user_id),
            interpretation=interpretation,
            industry_specific=context.get('industry'),
            organization_size=context.get('org_size'),
            practical_examples=context.get('examples', [])
        )

        self.db.add(annotation)
        await self.db.commit()

        # Trigger synthesis
        await self.synthesize_clause(clause_id)

        return str(annotation.id)

    async def vote_annotation(
        self,
        user_id: str,
        annotation_id: str,
        vote: str  # 'up', 'down', 'helpful'
    ):
        """Vote on annotation quality"""

        annotation = await self.db.get(CommunityAnnotation, uuid.UUID(annotation_id))

        if vote == 'up':
            annotation.upvotes += 1
        elif vote == 'down':
            annotation.downvotes += 1
        elif vote == 'helpful':
            annotation.helpful_count += 1

        await self.db.commit()

        # Re-synthesize if significant voting
        if annotation.upvotes + annotation.downvotes > 10:
            await self.synthesize_clause(annotation.clause_id)

    async def synthesize_clause(self, clause_id: str):
        """
        AI synthesizes unified view from all sources

        Sources:
        1. Official standard text (from Neo4j)
        2. Community interpretations (filtered by quality)
        3. Real case examples (from Case Library)
        4. Open questions (from discussions)
        """

        # 1. Get official text
        official = await self.kg.get_clause(clause_id)

        # 2. Get community interpretations (sorted by quality)
        result = await self.db.execute(
            select(CommunityAnnotation)
            .where(CommunityAnnotation.clause_id == clause_id)
            .order_by(
                (CommunityAnnotation.upvotes - CommunityAnnotation.downvotes).desc(),
                CommunityAnnotation.helpful_count.desc()
            )
            .limit(10)
        )
        interpretations = result.scalars().all()

        # 3. Get real cases addressing this clause
        cases = await self.cases.find_cases_addressing_clause(clause_id)

        # 4. Build synthesis prompt
        prompt = self._build_synthesis_prompt(
            official,
            interpretations,
            cases
        )

        # 5. AI synthesis
        synthesis = await self.llm.generate(
            prompt=prompt,
            temperature=0.3,  # Factual
            max_tokens=2000
        )

        # 6. Parse structured output
        unified = self._parse_synthesis(synthesis)

        # 7. Save or update
        existing = await self.db.execute(
            select(SynthesizedGuidance)
            .where(SynthesizedGuidance.clause_id == clause_id)
        )
        guidance = existing.scalar_one_or_none()

        if guidance:
            guidance.unified_guidance = unified['guidance']
            guidance.practical_steps = unified['steps']
            guidance.common_pitfalls = unified['pitfalls']
            guidance.success_patterns = unified['patterns']
            guidance.synthesis_version += 1
            guidance.synthesized_at = datetime.utcnow()
        else:
            guidance = SynthesizedGuidance(
                clause_id=clause_id,
                official_text=official.text,
                unified_guidance=unified['guidance'],
                practical_steps=unified['steps'],
                common_pitfalls=unified['pitfalls'],
                success_patterns=unified['patterns'],
                sources_count=len(interpretations) + len(cases)
            )
            self.db.add(guidance)

        await self.db.commit()

    def _build_synthesis_prompt(
        self,
        official,
        interpretations: List[CommunityAnnotation],
        cases: List
    ) -> str:
        """Build prompt for AI synthesis"""

        prompt = f"""Create unified, practical guidance for ISO 22301 clause {official.id}.

OFFICIAL REQUIREMENT:
{official.text}

COMMUNITY INTERPRETATIONS ({len(interpretations)} experts):
"""

        for i, interp in enumerate(interpretations, 1):
            industry = interp.industry_specific or 'general'
            score = interp.upvotes - interp.downvotes

            prompt += f"""
{i}. Expert ({industry}, score: {score}):
{interp.interpretation}
"""

            if interp.practical_examples:
                prompt += f"   Examples: {interp.practical_examples}\n"

        prompt += f"""

REAL-WORLD APPLICATIONS ({len(cases)} cases):
"""

        for i, case in enumerate(cases[:5], 1):  # Top 5 cases
            prompt += f"""
{i}. {case.organization_context.industry} organization:
   What they did: {case.success_patterns[0] if case.success_patterns else 'N/A'}
   Outcome: {'Success' if case.metrics.completed_successfully else 'Failed'}
"""

        prompt += """

TASK: Synthesize into clear, practical guidance with 4 sections:

1. CLEAR EXPLANATION (what requirement means in plain language)
2. PRACTICAL STEPS (how to meet it, step-by-step)
3. COMMON PITFALLS (what mistakes to avoid)
4. SUCCESS PATTERNS (what works based on real cases)

Format as JSON:
{
  "guidance": "...",
  "steps": ["step 1", "step 2", ...],
  "pitfalls": ["pitfall 1", ...],
  "patterns": ["pattern 1", ...]
}
"""

        return prompt

    def _parse_synthesis(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM JSON response"""
        import json

        # Strip markdown if present
        response = llm_response.strip()
        if response.startswith('```json'):
            response = response[7:]
        if response.endswith('```'):
            response = response[:-3]

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback: return as plain text
            return {
                'guidance': llm_response,
                'steps': [],
                'pitfalls': [],
                'patterns': []
            }

    async def get_living_documentation(
        self,
        clause_id: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Get living documentation for clause with context filtering

        Args:
            clause_id: ISO clause ID
            context: Optional context (industry, org_size, etc)

        Returns:
            Dict with synthesized guidance + relevant examples
        """
        # Get synthesized guidance
        result = await self.db.execute(
            select(SynthesizedGuidance)
            .where(SynthesizedGuidance.clause_id == clause_id)
        )
        guidance = result.scalar_one_or_none()

        if not guidance:
            # No synthesis yet - trigger it
            await self.synthesize_clause(clause_id)
            return await self.get_living_documentation(clause_id, context)

        # Get community annotations (filtered by context if provided)
        query = select(CommunityAnnotation).where(
            CommunityAnnotation.clause_id == clause_id
        )

        if context:
            if context.get('industry'):
                query = query.where(
                    CommunityAnnotation.industry_specific == context['industry']
                )
            if context.get('org_size'):
                query = query.where(
                    CommunityAnnotation.organization_size == context['org_size']
                )

        query = query.order_by(
            (CommunityAnnotation.upvotes - CommunityAnnotation.downvotes).desc()
        ).limit(5)

        result = await self.db.execute(query)
        annotations = result.scalars().all()

        # Get real cases
        cases = await self.cases.find_cases_addressing_clause(
            clause_id,
            context=context
        )

        return {
            'clause_id': clause_id,
            'official_text': guidance.official_text,
            'unified_guidance': guidance.unified_guidance,
            'practical_steps': guidance.practical_steps,
            'common_pitfalls': guidance.common_pitfalls,
            'success_patterns': guidance.success_patterns,
            'community_annotations': [
                {
                    'interpretation': a.interpretation,
                    'industry': a.industry_specific,
                    'org_size': a.organization_size,
                    'examples': a.practical_examples,
                    'score': a.upvotes - a.downvotes,
                    'helpful_count': a.helpful_count
                }
                for a in annotations
            ],
            'real_world_cases': [
                {
                    'title': c.title,
                    'industry': c.organization_context.industry,
                    'outcome': 'Success' if c.metrics.completed_successfully else 'Challenges',
                    'key_learnings': c.lessons_learned[:3]
                }
                for c in cases[:3]
            ],
            'metadata': {
                'synthesis_version': guidance.synthesis_version,
                'last_synthesized': guidance.synthesized_at.isoformat(),
                'sources_count': guidance.sources_count,
                'community_contributors': len(annotations)
            }
        }

    async def get_next_steps_for_organization(
        self,
        org_id: str,
        count: int = 3
    ) -> List[Dict]:
        """
        AI-powered next steps recommendation based on:
        - Organization's current progress
        - Similar organizations' journeys
        - Community wisdom
        """
        # Get organization context
        org_context = await self._get_org_context(org_id)

        # Find similar organizations
        similar_orgs = await self._find_similar_organizations(org_context)

        # Analyze successful paths
        successful_paths = await self._analyze_successful_paths(similar_orgs)

        # Generate personalized recommendations
        prompt = f"""Based on organization context and community intelligence:

ORGANIZATION CONTEXT:
- Industry: {org_context['industry']}
- Size: {org_context['size']}
- Current BCM maturity: {org_context['maturity_level']}
- Completed clauses: {org_context['completed_clauses']}

SIMILAR ORGANIZATIONS' SUCCESSFUL PATHS:
{self._format_successful_paths(successful_paths)}

TASK: Recommend {count} highest-impact next steps.

For each step, provide:
1. What to do (clear action)
2. Why it matters (expected impact)
3. How long it takes (effort estimate)
4. What resources needed
5. Success examples from community

Format as JSON array.
"""

        recommendations = await self.llm.generate(
            prompt=prompt,
            temperature=0.4,
            max_tokens=1500
        )

        return self._parse_recommendations(recommendations)

    async def search_living_docs(
        self,
        query: str,
        filters: Dict[str, Any] = None
    ) -> List[Dict]:
        """
        Semantic search across living documentation

        Args:
            query: Natural language search query
            filters: Optional filters (standard, industry, etc)

        Returns:
            List of relevant guidance entries
        """
        # TODO: Implement vector search using embeddings
        # For now, simple text search

        # Search in synthesized guidance
        # This is placeholder - should use proper vector search
        results = []

        return results

    async def get_topic_overview(
        self,
        topic: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate overview for BCM topic (e.g., "BIA", "Incident Response")

        Combines:
        - Relevant ISO clauses
        - Community best practices
        - Real case examples
        - Step-by-step guidance
        """

        # Map topic to relevant clauses
        relevant_clauses = await self._get_clauses_for_topic(topic)

        # Get community wisdom for each clause
        all_guidance = []
        for clause in relevant_clauses:
            guidance = await self.get_living_documentation(
                clause.id,
                context=context
            )
            all_guidance.append(guidance)

        # Get cases related to topic
        topic_cases = await self.cases.search_by_topic(topic, context=context)

        # Synthesize topic overview
        prompt = f"""Create comprehensive overview for BCM topic: {topic}

RELEVANT ISO 22301 REQUIREMENTS:
{self._format_clauses(relevant_clauses)}

COMMUNITY GUIDANCE:
{self._format_community_guidance(all_guidance)}

REAL-WORLD CASES ({len(topic_cases)}):
{self._format_cases_summary(topic_cases)}

TASK: Create practical overview with:
1. WHAT IS IT (clear definition)
2. WHY IT MATTERS (business value)
3. HOW TO IMPLEMENT (step-by-step)
4. COMMON CHALLENGES (pitfalls to avoid)
5. SUCCESS FACTORS (what works)
6. RECOMMENDED RESOURCES

Format as JSON.
"""

        overview = await self.llm.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=2500
        )

        parsed = self._parse_topic_overview(overview)

        return {
            'topic': topic,
            'overview': parsed,
            'relevant_clauses': [c.id for c in relevant_clauses],
            'case_examples': [
                {
                    'title': c.title,
                    'industry': c.organization_context.industry,
                    'outcome_summary': c.outcome_summary
                }
                for c in topic_cases[:5]
            ],
            'community_contributors': sum(
                g['metadata']['community_contributors']
                for g in all_guidance
            )
        }

    # Private helper methods

    async def _get_org_context(self, org_id: str) -> Dict[str, Any]:
        """Get organization context for recommendations"""
        # TODO: Integrate with organization service
        return {
            'org_id': org_id,
            'industry': 'Technology',
            'size': 'Medium',
            'maturity_level': 'Developing',
            'completed_clauses': []
        }

    async def _find_similar_organizations(
        self,
        org_context: Dict
    ) -> List[str]:
        """Find organizations with similar profile"""
        # TODO: Implement similarity matching
        # For now, simple filter by industry + size
        return []

    async def _analyze_successful_paths(
        self,
        org_ids: List[str]
    ) -> List[Dict]:
        """Analyze implementation paths of successful organizations"""
        # TODO: Implement path analysis from case library
        return []

    def _format_successful_paths(self, paths: List[Dict]) -> str:
        """Format successful paths for prompt"""
        if not paths:
            return "No similar organization data available."

        formatted = ""
        for i, path in enumerate(paths[:3], 1):
            formatted += f"{i}. {path}\n"

        return formatted

    def _parse_recommendations(self, llm_response: str) -> List[Dict]:
        """Parse AI recommendations response"""
        import json

        response = llm_response.strip()
        if response.startswith('```json'):
            response = response[7:]
        if response.endswith('```'):
            response = response[:-3]

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return []

    async def _get_clauses_for_topic(self, topic: str) -> List:
        """Map topic to relevant ISO clauses"""
        # TODO: Implement topic → clause mapping in knowledge graph
        # For now, return empty list
        return []

    def _format_clauses(self, clauses: List) -> str:
        """Format clauses for prompt"""
        if not clauses:
            return "No specific clauses mapped."

        formatted = ""
        for clause in clauses:
            formatted += f"- {clause.id}: {clause.title}\n"

        return formatted

    def _format_community_guidance(self, guidance_list: List[Dict]) -> str:
        """Format community guidance for prompt"""
        formatted = ""
        for g in guidance_list:
            formatted += f"\nClause {g['clause_id']}:\n"
            formatted += f"Guidance: {g['unified_guidance'][:200]}...\n"
            if g['success_patterns']:
                formatted += f"Success patterns: {', '.join(g['success_patterns'][:2])}\n"

        return formatted

    def _format_cases_summary(self, cases: List) -> str:
        """Format cases summary for prompt"""
        if not cases:
            return "No cases available."

        formatted = ""
        for i, case in enumerate(cases[:5], 1):
            formatted += f"{i}. {case.title} ({case.organization_context.industry})\n"
            formatted += f"   Outcome: {'Success' if case.metrics.completed_successfully else 'Challenges'}\n"

        return formatted

    def _parse_topic_overview(self, llm_response: str) -> Dict[str, Any]:
        """Parse topic overview response"""
        import json

        response = llm_response.strip()
        if response.startswith('```json'):
            response = response[7:]
        if response.endswith('```'):
            response = response[:-3]

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                'definition': llm_response,
                'value': '',
                'implementation': [],
                'challenges': [],
                'success_factors': [],
                'resources': []
            }
