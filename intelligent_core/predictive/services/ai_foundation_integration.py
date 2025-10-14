"""
AI Foundation Integration for Predictive Service

Integrates RAG Pipeline and LLM Router from ai_foundation:
- RAG: Retrieves historical journey patterns and demand forecasts
- LLM: Generates proactive recommendations with context
- Pattern storage: Learns from successful predictions
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


class PredictiveAIFoundation:
    """
    AI Foundation integration for Predictive Service

    Provides:
    - RAG-enhanced journey prediction
    - LLM-powered proactive recommendations
    - Pattern storage for prediction learning
    """

    def __init__(self):
        self.rag: Optional[RAGPipeline] = None
        self.llm: Optional[LLMRouter] = None

    async def initialize(self):
        """Initialize AI Foundation components"""

        try:
            # Initialize RAG for historical pattern retrieval
            self.rag = RAGPipeline()
            logger.info("✅ RAG Pipeline initialized for Predictive Service")

            # Initialize LLM Router for recommendation generation
            self.llm = LLMRouter()
            logger.info("✅ LLM Router initialized for Predictive Service")

        except Exception as e:
            logger.error(f"❌ AI Foundation initialization failed: {e}")
            raise

    async def retrieve_similar_journeys(
        self,
        org_context: Dict[str, Any],
        current_milestone: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar organization journeys from RAG

        Args:
            org_context: Organization context (industry, size, region, etc.)
            current_milestone: Current milestone/stage
            top_k: Number of similar journeys to retrieve

        Returns:
            List of similar journeys with relevance scores
        """

        if not self.rag:
            logger.warning("RAG not initialized, skipping journey retrieval")
            return []

        # Build search query
        search_query = f"""
        Organization Journey Prediction

        Current Context:
        - Industry: {org_context.get('industry', 'unknown')}
        - Size: {org_context.get('size', 'unknown')}
        - Region: {org_context.get('region', 'unknown')}
        - Current Milestone: {current_milestone}

        Find similar organization journeys to predict next milestones.
        """

        try:
            similar_journeys = await self.rag.retrieve(
                query=search_query,
                context={
                    "domain": "predictive",
                    "task": "journey_prediction",
                    "org_context": org_context
                },
                top_k=top_k,
                filters={"source_type": "journey_patterns", "milestone": current_milestone},
                enable_reranking=True
            )

            logger.info(f"📚 Retrieved {len(similar_journeys)} similar journeys from RAG")

            return similar_journeys

        except Exception as e:
            logger.warning(f"RAG journey retrieval failed: {e}")
            return []

    async def retrieve_demand_patterns(
        self,
        expertise_domain: str,
        timeframe: str = "next_month",
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve expert demand patterns from RAG

        Args:
            expertise_domain: Domain of expertise (e.g., "bia", "risk_assessment")
            timeframe: Prediction timeframe
            top_k: Number of patterns to retrieve

        Returns:
            List of demand patterns
        """

        if not self.rag:
            logger.warning("RAG not initialized")
            return []

        search_query = f"""
        Expert Demand Forecast

        Domain: {expertise_domain}
        Timeframe: {timeframe}

        Find historical demand patterns for this expertise domain.
        """

        try:
            patterns = await self.rag.retrieve(
                query=search_query,
                context={"domain": "predictive", "task": "demand_forecast"},
                top_k=top_k,
                filters={"source_type": "demand_patterns", "expertise_domain": expertise_domain},
                enable_reranking=True
            )

            logger.info(f"📊 Retrieved {len(patterns)} demand patterns from RAG")

            return patterns

        except Exception as e:
            logger.warning(f"RAG demand pattern retrieval failed: {e}")
            return []

    async def generate_proactive_recommendations(
        self,
        org_context: Dict[str, Any],
        upcoming_milestones: List[Dict],
        similar_journeys: List[Dict] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> Dict[str, Any]:
        """
        Generate proactive recommendations using LLM Router

        Args:
            org_context: Organization context
            upcoming_milestones: Predicted upcoming milestones
            similar_journeys: Similar journeys from RAG (optional)
            temperature: Sampling temperature
            max_tokens: Maximum response tokens

        Returns:
            {
                'recommendations': List[Dict],
                'confidence': float,
                'reasoning': str
            }
        """

        if not self.llm:
            logger.error("LLM Router not initialized")
            return {'recommendations': [], 'confidence': 0.0}

        # Build enriched context with RAG knowledge
        knowledge_context = ""
        if similar_journeys:
            knowledge_context = "SIMILAR ORGANIZATION JOURNEYS:\n"
            for i, journey in enumerate(similar_journeys[:3], 1):
                knowledge_context += f"{i}. {journey.get('content', '')}\n"

        # Build system prompt
        system_prompt = f"""You are a Predictive Analytics expert for BCM (Business Continuity Management).

Your task is to generate proactive recommendations for organizations based on their upcoming milestones.

{knowledge_context}

CURRENT ORGANIZATION:
- Industry: {org_context.get('industry')}
- Size: {org_context.get('size')}
- Region: {org_context.get('region')}

UPCOMING MILESTONES:
{self._format_milestones(upcoming_milestones)}

Generate specific, actionable recommendations to help the organization prepare for these milestones.
"""

        user_prompt = """Based on the organization's context and upcoming milestones, provide:

1. Top 3 proactive recommendations (specific actions to take now)
2. Resources to prepare (documents, tools, expertise)
3. Potential risks to mitigate
4. Timeline for preparation

Format as structured JSON."""

        try:
            response_text = await self.llm.query(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                task_type="content_generation",
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Parse recommendations
            recommendations = self._parse_recommendations(response_text)

            # Calculate confidence
            confidence = self._calculate_confidence(similar_journeys, upcoming_milestones)

            logger.info(f"✅ Generated {len(recommendations)} proactive recommendations, confidence: {confidence:.2f}")

            return {
                'recommendations': recommendations,
                'confidence': confidence,
                'reasoning': response_text
            }

        except Exception as e:
            logger.error(f"❌ LLM recommendation generation failed: {e}")
            return {'recommendations': [], 'confidence': 0.0}

    async def store_successful_prediction(
        self,
        org_context: Dict,
        predicted_milestone: str,
        actual_milestone: str,
        accuracy: float
    ):
        """
        Store successful prediction pattern in RAG for learning

        Args:
            org_context: Organization context
            predicted_milestone: What was predicted
            actual_milestone: What actually happened
            accuracy: Prediction accuracy (0-1)
        """

        if not self.rag:
            return

        if accuracy < 0.7:
            logger.debug(f"Skipping low accuracy prediction storage: {accuracy:.2f}")
            return

        # Format as learnable pattern
        pattern_text = f"""
        PREDICTIVE PATTERN - Journey Prediction

        Organization Context:
        - Industry: {org_context.get('industry')}
        - Size: {org_context.get('size')}
        - Region: {org_context.get('region')}

        Prediction:
        - Predicted: {predicted_milestone}
        - Actual: {actual_milestone}
        - Accuracy: {accuracy:.2%}

        Success Pattern:
        This prediction was accurate because the organization followed typical patterns
        for {org_context.get('industry')} organizations in {org_context.get('region')}.
        """

        try:
            await self.rag.ingest_documents(
                documents=[{
                    "text": pattern_text,
                    "metadata": {
                        "source_type": "journey_patterns",
                        "milestone": predicted_milestone,
                        "industry": org_context.get('industry'),
                        "accuracy": accuracy,
                        "success": True,
                        "timestamp": str(datetime.now())
                    }
                }],
                source_type="journey_patterns"
            )

            logger.info(f"💾 Stored successful prediction pattern: {predicted_milestone} ({accuracy:.2%})")

        except Exception as e:
            logger.warning(f"Failed to store pattern in RAG: {e}")

    async def store_demand_pattern(
        self,
        expertise_domain: str,
        demand_data: Dict,
        forecast_accuracy: float
    ):
        """
        Store expert demand pattern for learning

        Args:
            expertise_domain: Expertise domain
            demand_data: Demand statistics
            forecast_accuracy: Forecast accuracy
        """

        if not self.rag or forecast_accuracy < 0.7:
            return

        pattern_text = f"""
        DEMAND PATTERN - Expert Demand Forecast

        Expertise Domain: {expertise_domain}

        Demand Statistics:
        - Peak Period: {demand_data.get('peak_period')}
        - Average Demand: {demand_data.get('avg_demand')}
        - Forecast Accuracy: {forecast_accuracy:.2%}

        Pattern:
        Demand for {expertise_domain} expertise typically peaks during {demand_data.get('peak_period')}.
        """

        try:
            await self.rag.ingest_documents(
                documents=[{
                    "text": pattern_text,
                    "metadata": {
                        "source_type": "demand_patterns",
                        "expertise_domain": expertise_domain,
                        "accuracy": forecast_accuracy,
                        "timestamp": str(datetime.now())
                    }
                }],
                source_type="demand_patterns"
            )

            logger.info(f"💾 Stored demand pattern: {expertise_domain}")

        except Exception as e:
            logger.warning(f"Failed to store demand pattern: {e}")

    def _format_milestones(self, milestones: List[Dict]) -> str:
        """Format milestones for prompt"""
        formatted = []
        for m in milestones:
            formatted.append(f"- {m.get('name')}: {m.get('description')} (ETA: {m.get('eta_days')} days)")
        return "\n".join(formatted)

    def _parse_recommendations(self, response_text: str) -> List[Dict]:
        """Parse LLM response into structured recommendations"""
        # Simplified parsing - real implementation would use JSON parsing
        recommendations = []

        # Extract key recommendations from text
        if "recommendation" in response_text.lower():
            lines = response_text.split('\n')
            for line in lines:
                if any(keyword in line.lower() for keyword in ['prepare', 'review', 'schedule', 'contact']):
                    recommendations.append({
                        'action': line.strip(),
                        'priority': 'medium',
                        'type': 'proactive'
                    })

        return recommendations[:5]  # Top 5

    def _calculate_confidence(self, similar_journeys: List, upcoming_milestones: List) -> float:
        """Calculate prediction confidence"""
        base_confidence = 0.7

        # More similar journeys = higher confidence
        if similar_journeys:
            journey_count = len(similar_journeys)
            if journey_count >= 5:
                base_confidence += 0.15
            elif journey_count >= 3:
                base_confidence += 0.10

        # Multiple upcoming milestones = more data = higher confidence
        if len(upcoming_milestones) >= 3:
            base_confidence += 0.05

        return min(1.0, round(base_confidence, 2))


# Singleton instance
_ai_foundation = None

async def get_predictive_ai_foundation() -> PredictiveAIFoundation:
    """Get or create PredictiveAIFoundation singleton"""

    global _ai_foundation

    if _ai_foundation is None:
        _ai_foundation = PredictiveAIFoundation()
        await _ai_foundation.initialize()

    return _ai_foundation
