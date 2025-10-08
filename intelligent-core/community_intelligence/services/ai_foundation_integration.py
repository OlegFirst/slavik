"""
AI Foundation Integration for Community Intelligence

Integrates RAG Pipeline and LLM Router from ai-foundation:
- RAG: Retrieves similar case studies and community patterns
- LLM: Generates insights from community contributions
- Pattern storage: Stores successful community insights
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import sys

# Add ai-foundation to path
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root / "intelligent-core" / "ai-foundation"))

from rag.pipeline import RAGPipeline
from llm.llm_router import LLMRouter

logger = logging.getLogger(__name__)


class CommunityAIFoundation:
    """
    AI Foundation integration for Community Intelligence

    Provides:
    - RAG-enhanced case study retrieval
    - LLM-powered insight generation from community contributions
    - Pattern storage for community learning
    - Best practice synthesis
    """

    def __init__(self):
        self.rag: Optional[RAGPipeline] = None
        self.llm: Optional[LLMRouter] = None

    async def initialize(self):
        """Initialize AI Foundation components"""

        try:
            # Initialize RAG for community knowledge retrieval
            self.rag = RAGPipeline()
            logger.info("✅ RAG Pipeline initialized for Community Intelligence")

            # Initialize LLM Router for insight generation
            self.llm = LLMRouter()
            logger.info("✅ LLM Router initialized for Community Intelligence")

        except Exception as e:
            logger.error(f"❌ AI Foundation initialization failed: {e}")
            raise

    async def retrieve_similar_case_studies(
        self,
        problem_domain: str,
        industry: str = None,
        organization_size: str = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar case studies from RAG knowledge base

        Args:
            problem_domain: Problem domain (e.g., "business_continuity", "risk_management")
            industry: Industry filter (optional)
            organization_size: Organization size filter (optional)
            top_k: Number of similar cases to retrieve

        Returns:
            List of similar case studies with relevance scores
        """

        if not self.rag:
            logger.warning("RAG not initialized, skipping case study retrieval")
            return []

        # Build search query
        search_query = f"""
        Problem Domain: {problem_domain}

        Looking for case studies from:
        Industry: {industry or 'any'}
        Organization Size: {organization_size or 'any'}

        Find successful case studies and best practices from the community.
        """

        try:
            similar_cases = await self.rag.retrieve(
                query=search_query,
                context={
                    "domain": "community_intelligence",
                    "problem_domain": problem_domain,
                    "industry": industry
                },
                top_k=top_k,
                filters={"source_type": "community_case_studies", "problem_domain": problem_domain},
                enable_reranking=True
            )

            logger.info(f"📚 Retrieved {len(similar_cases)} similar case studies from RAG")

            return similar_cases

        except Exception as e:
            logger.warning(f"RAG case study retrieval failed: {e}")
            return []

    async def retrieve_community_patterns(
        self,
        pattern_type: str,
        context: Dict[str, Any] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve community best practice patterns from RAG

        Args:
            pattern_type: Type of pattern (e.g., "implementation", "governance", "training")
            context: Additional context filters
            top_k: Number of patterns to retrieve

        Returns:
            List of community patterns
        """

        if not self.rag:
            logger.warning("RAG not initialized")
            return []

        search_query = f"""
        Community Best Practice Pattern

        Pattern Type: {pattern_type}

        Find successful implementation patterns shared by the community.
        """

        try:
            patterns = await self.rag.retrieve(
                query=search_query,
                context={"domain": "community_intelligence", "pattern_type": pattern_type},
                top_k=top_k,
                filters={"source_type": "community_patterns", "pattern_type": pattern_type},
                enable_reranking=True
            )

            logger.info(f"🔍 Retrieved {len(patterns)} community patterns from RAG")

            return patterns

        except Exception as e:
            logger.warning(f"RAG pattern retrieval failed: {e}")
            return []

    async def retrieve_expert_insights(
        self,
        topic: str,
        expertise_domain: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve expert insights from community specialists

        Args:
            topic: Topic of interest
            expertise_domain: Domain of expertise
            top_k: Number of insights to retrieve

        Returns:
            List of expert insights
        """

        if not self.rag:
            logger.warning("RAG not initialized")
            return []

        search_query = f"""
        Expert Insights Needed

        Topic: {topic}
        Expertise Domain: {expertise_domain}

        Find relevant expert insights and recommendations from community specialists.
        """

        try:
            insights = await self.rag.retrieve(
                query=search_query,
                context={"domain": "community_intelligence", "expertise": expertise_domain},
                top_k=top_k,
                filters={"source_type": "expert_insights", "expertise_domain": expertise_domain},
                enable_reranking=True
            )

            logger.info(f"💡 Retrieved {len(insights)} expert insights from RAG")

            return insights

        except Exception as e:
            logger.warning(f"RAG expert insight retrieval failed: {e}")
            return []

    async def generate_community_insight(
        self,
        contributions: List[Dict[str, Any]],
        topic: str,
        similar_cases: List[Dict] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Generate insights from community contributions using LLM Router

        Args:
            contributions: List of community contributions
            topic: Topic/theme of the contributions
            similar_cases: Similar cases from RAG (optional)
            temperature: Sampling temperature
            max_tokens: Maximum response tokens

        Returns:
            {
                'insight': str,
                'key_themes': List[str],
                'confidence': float,
                'recommendations': List[str]
            }
        """

        if not self.llm:
            logger.error("LLM Router not initialized")
            return {'insight': '', 'key_themes': [], 'confidence': 0.0}

        # Build enriched context with RAG knowledge
        knowledge_context = ""
        if similar_cases:
            knowledge_context = "SIMILAR CASE STUDIES:\n"
            for i, case in enumerate(similar_cases[:3], 1):
                knowledge_context += f"{i}. {case.get('content', '')}\n"

        # Build system prompt
        system_prompt = f"""You are a Community Intelligence Analyst for BCM (Business Continuity Management).

Your task is to synthesize insights from multiple community contributions and identify patterns, best practices, and recommendations.

{knowledge_context}

TOPIC:
{topic}

COMMUNITY CONTRIBUTIONS:
{self._format_contributions(contributions)}

Analyze these contributions and generate actionable insights for the community.
"""

        user_prompt = """Analyze the community contributions and provide:

1. Key insight/synthesis (1-2 paragraphs)
2. Main themes identified (3-5 themes)
3. Best practices extracted
4. Actionable recommendations for the community
5. Potential gaps or areas needing more exploration

Format as structured analysis with clear sections."""

        try:
            response_text = await self.llm.query(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                task_type="content_generation",
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Parse insight
            insight_data = self._parse_insight(response_text)

            # Calculate confidence
            confidence = self._calculate_insight_confidence(contributions, similar_cases)

            logger.info(f"✅ Generated community insight with {len(insight_data.get('key_themes', []))} themes, confidence: {confidence:.2f}")

            return {
                'insight': response_text,
                'key_themes': insight_data.get('key_themes', []),
                'confidence': confidence,
                'recommendations': insight_data.get('recommendations', [])
            }

        except Exception as e:
            logger.error(f"❌ LLM insight generation failed: {e}")
            return {'insight': '', 'key_themes': [], 'confidence': 0.0}

    async def generate_best_practice_synthesis(
        self,
        case_studies: List[Dict],
        domain: str,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> Dict[str, Any]:
        """
        Generate best practice synthesis from case studies using LLM Router

        Args:
            case_studies: List of case studies to synthesize
            domain: Domain/topic
            temperature: Sampling temperature
            max_tokens: Maximum response tokens

        Returns:
            {
                'synthesis': str,
                'best_practices': List[str],
                'confidence': float
            }
        """

        if not self.llm:
            logger.error("LLM Router not initialized")
            return {'synthesis': '', 'best_practices': [], 'confidence': 0.0}

        system_prompt = f"""You are a Best Practice Analyst for the BCM community.

Your task is to synthesize best practices from multiple case studies.

DOMAIN:
{domain}

CASE STUDIES:
{self._format_case_studies(case_studies)}

Extract common patterns, success factors, and actionable best practices.
"""

        user_prompt = """Synthesize best practices from these case studies:

1. Common success patterns (what worked across multiple cases)
2. Top 5 best practices (ranked by frequency and impact)
3. Critical success factors
4. Common pitfalls to avoid
5. Implementation guidance

Format as practical, actionable guidance."""

        try:
            response_text = await self.llm.query(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                task_type="content_generation",
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Parse best practices
            best_practices = self._parse_best_practices(response_text)

            # Calculate confidence
            confidence = self._calculate_synthesis_confidence(case_studies)

            logger.info(f"✅ Generated best practice synthesis with {len(best_practices)} practices, confidence: {confidence:.2f}")

            return {
                'synthesis': response_text,
                'best_practices': best_practices,
                'confidence': confidence
            }

        except Exception as e:
            logger.error(f"❌ LLM best practice synthesis failed: {e}")
            return {'synthesis': '', 'best_practices': [], 'confidence': 0.0}

    async def store_successful_case_study(
        self,
        problem_domain: str,
        organization_context: Dict,
        solution_approach: str,
        outcomes: Dict[str, Any],
        lessons_learned: List[str]
    ):
        """
        Store successful case study in RAG for community learning

        Args:
            problem_domain: Problem domain addressed
            organization_context: Context about the organization
            solution_approach: How the problem was solved
            outcomes: Measurable outcomes and results
            lessons_learned: Key lessons from the case
        """

        if not self.rag:
            return

        # Format as learnable case study
        case_text = f"""
        COMMUNITY CASE STUDY

        Problem Domain: {problem_domain}

        Organization Context:
        - Industry: {organization_context.get('industry', 'N/A')}
        - Size: {organization_context.get('size', 'N/A')}
        - Region: {organization_context.get('region', 'N/A')}

        Solution Approach:
        {solution_approach}

        Outcomes:
        - Success Rate: {outcomes.get('success_rate', 'N/A')}
        - Time to Implementation: {outcomes.get('implementation_time', 'N/A')}
        - Impact: {outcomes.get('impact', 'N/A')}

        Lessons Learned:
        {chr(10).join(f'- {lesson}' for lesson in lessons_learned)}

        Key Success Factors:
        - Community-validated approach
        - Real-world implementation
        - Measurable outcomes
        """

        try:
            await self.rag.ingest_documents(
                documents=[{
                    "text": case_text,
                    "metadata": {
                        "source_type": "community_case_studies",
                        "problem_domain": problem_domain,
                        "industry": organization_context.get('industry'),
                        "success": True,
                        "timestamp": str(datetime.now())
                    }
                }],
                source_type="community_case_studies"
            )

            logger.info(f"💾 Stored community case study: {problem_domain}")

        except Exception as e:
            logger.warning(f"Failed to store case study in RAG: {e}")

    async def store_community_pattern(
        self,
        pattern_type: str,
        pattern_description: str,
        validated_by: int,
        success_rate: float,
        context: Dict[str, Any]
    ):
        """
        Store community best practice pattern for learning

        Args:
            pattern_type: Type of pattern
            pattern_description: Description of the pattern
            validated_by: Number of organizations that validated this pattern
            success_rate: Success rate (0-1)
            context: Additional context
        """

        if not self.rag or success_rate < 0.7:
            return

        pattern_text = f"""
        COMMUNITY BEST PRACTICE PATTERN

        Pattern Type: {pattern_type}

        Description:
        {pattern_description}

        Validation:
        - Validated by {validated_by} organizations
        - Success Rate: {success_rate:.1%}

        Context:
        - Domain: {context.get('domain', 'N/A')}
        - Complexity: {context.get('complexity', 'N/A')}

        Pattern Effectiveness:
        This pattern has been successfully applied by {validated_by} organizations
        with a {success_rate:.1%} success rate, making it a reliable best practice.
        """

        try:
            await self.rag.ingest_documents(
                documents=[{
                    "text": pattern_text,
                    "metadata": {
                        "source_type": "community_patterns",
                        "pattern_type": pattern_type,
                        "validated_by": validated_by,
                        "success_rate": success_rate,
                        "timestamp": str(datetime.now())
                    }
                }],
                source_type="community_patterns"
            )

            logger.info(f"💾 Stored community pattern: {pattern_type} ({success_rate:.1%} success)")

        except Exception as e:
            logger.warning(f"Failed to store community pattern: {e}")

    async def store_expert_insight(
        self,
        expert_id: str,
        expertise_domain: str,
        insight: str,
        topic: str,
        validation_score: float
    ):
        """
        Store expert insight for community knowledge base

        Args:
            expert_id: Expert identifier
            expertise_domain: Domain of expertise
            insight: The expert insight/recommendation
            topic: Topic addressed
            validation_score: Community validation score (0-1)
        """

        if not self.rag or validation_score < 0.6:
            return

        insight_text = f"""
        EXPERT INSIGHT - Community Specialist

        Expertise Domain: {expertise_domain}
        Topic: {topic}

        Insight:
        {insight}

        Validation:
        - Community Validation Score: {validation_score:.1%}
        - Expert Credentials: Verified specialist in {expertise_domain}

        Application:
        This expert insight has been validated by the community and provides
        actionable guidance for {topic} in the context of {expertise_domain}.
        """

        try:
            await self.rag.ingest_documents(
                documents=[{
                    "text": insight_text,
                    "metadata": {
                        "source_type": "expert_insights",
                        "expertise_domain": expertise_domain,
                        "topic": topic,
                        "validation_score": validation_score,
                        "timestamp": str(datetime.now())
                    }
                }],
                source_type="expert_insights"
            )

            logger.info(f"💾 Stored expert insight: {expertise_domain} - {topic}")

        except Exception as e:
            logger.warning(f"Failed to store expert insight: {e}")

    # ===== INTERNAL HELPERS =====

    def _format_contributions(self, contributions: List[Dict]) -> str:
        """Format contributions for prompt"""
        formatted = []
        for i, contrib in enumerate(contributions[:10], 1):
            formatted.append(f"""
            Contribution {i}:
            Author: {contrib.get('author_type', 'Anonymous')}
            Content: {contrib.get('content', '')}
            Upvotes: {contrib.get('upvotes', 0)}
            """)
        return "\n".join(formatted)

    def _format_case_studies(self, case_studies: List[Dict]) -> str:
        """Format case studies for prompt"""
        formatted = []
        for i, case in enumerate(case_studies[:5], 1):
            formatted.append(f"""
            Case Study {i}:
            {case.get('content', '')}
            """)
        return "\n".join(formatted)

    def _parse_insight(self, response_text: str) -> Dict:
        """Parse LLM response into structured insight"""
        # Simplified parsing
        key_themes = []
        recommendations = []

        lines = response_text.split('\n')
        for line in lines:
            if 'theme' in line.lower() or 'pattern' in line.lower():
                key_themes.append(line.strip())
            if 'recommend' in line.lower() or 'should' in line.lower():
                recommendations.append(line.strip())

        return {
            'key_themes': key_themes[:5],
            'recommendations': recommendations[:5]
        }

    def _parse_best_practices(self, response_text: str) -> List[str]:
        """Parse best practices from LLM response"""
        best_practices = []

        lines = response_text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['practice', 'ensure', 'implement', 'establish']):
                practice = line.strip()
                if practice and len(practice) > 10:
                    best_practices.append(practice)

        return best_practices[:7]  # Top 7

    def _calculate_insight_confidence(self, contributions: List, similar_cases: List) -> float:
        """Calculate insight confidence"""
        base_confidence = 0.7

        # More contributions = higher confidence
        contrib_count = len(contributions)
        if contrib_count >= 10:
            base_confidence += 0.15
        elif contrib_count >= 5:
            base_confidence += 0.10
        elif contrib_count < 3:
            base_confidence -= 0.15

        # Similar cases add confidence
        if similar_cases and len(similar_cases) >= 3:
            base_confidence += 0.10

        return min(1.0, round(base_confidence, 2))

    def _calculate_synthesis_confidence(self, case_studies: List) -> float:
        """Calculate synthesis confidence"""
        base_confidence = 0.75

        case_count = len(case_studies)
        if case_count >= 5:
            base_confidence += 0.15
        elif case_count >= 3:
            base_confidence += 0.10
        elif case_count < 2:
            base_confidence -= 0.20

        return min(1.0, round(base_confidence, 2))


# Singleton instance
_ai_foundation = None

async def get_community_ai_foundation() -> CommunityAIFoundation:
    """Get or create CommunityAIFoundation singleton"""

    global _ai_foundation

    if _ai_foundation is None:
        _ai_foundation = CommunityAIFoundation()
        await _ai_foundation.initialize()

    return _ai_foundation
