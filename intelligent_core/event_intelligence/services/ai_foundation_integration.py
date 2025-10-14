"""
AI Foundation Integration for Event Intelligence

Provides RAG + LLM capabilities for intelligent event analysis, prediction, and healing.

Features:
- RAG-powered event pattern retrieval
- LLM-powered event analysis and recommendations
- Pattern storage for self-learning
- Integration with analyzer, predictor, and knowledge base
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import sys

# Add ai-foundation to path
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root / "intelligent-core" / "ai-foundation"))

from rag.pipeline import RAGPipeline
from llm.llm_router import LLMRouter

logger = logging.getLogger(__name__)


class EventIntelligenceAIFoundation:
    """
    AI Foundation integration for Event Intelligence

    Combines RAG retrieval with LLM generation for:
    - Intelligent event analysis
    - Gap prediction
    - Event pattern recognition
    - Auto-healing recommendations
    """

    def __init__(self):
        self.rag: Optional[RAGPipeline] = None
        self.llm: Optional[LLMRouter] = None
        self._initialized = False

    async def initialize(self):
        """Initialize RAG and LLM components"""

        if self._initialized:
            return

        try:
            # Initialize RAG Pipeline
            self.rag = RAGPipeline()
            logger.info("✅ RAG Pipeline initialized for Event Intelligence")

            # Initialize LLM Router
            self.llm = LLMRouter()
            logger.info("✅ LLM Router initialized for Event Intelligence")

            self._initialized = True

        except Exception as e:
            logger.error(f"❌ Failed to initialize AI Foundation: {e}")
            raise

    # ============================================================
    # EVENT ANALYSIS
    # ============================================================

    async def retrieve_similar_event_patterns(
        self,
        event_name: str,
        publishers: List[str],
        subscribers: List[str]
    ) -> List[Dict]:
        """
        Retrieve similar event patterns from knowledge base

        Args:
            event_name: Event name
            publishers: Publisher list
            subscribers: Subscriber list

        Returns:
            List of similar event patterns with metadata
        """

        if not self.rag:
            await self.initialize()

        # Build search query
        search_query = f"""
        Event: {event_name}
        Publishers: {', '.join(publishers) if publishers else 'none'}
        Subscribers: {', '.join(subscribers) if subscribers else 'none'}
        """

        try:
            similar_patterns = await self.rag.retrieve(
                query=search_query,
                context={
                    "domain": "event_intelligence",
                    "task": "pattern_analysis"
                },
                top_k=5,
                filters={"source_type": "event_patterns"},
                enable_reranking=True
            )

            logger.info(f"📚 Retrieved {len(similar_patterns)} similar event patterns for {event_name}")
            return similar_patterns

        except Exception as e:
            logger.warning(f"Failed to retrieve similar patterns: {e}")
            return []

    async def generate_event_analysis(
        self,
        event_name: str,
        publishers: List[str],
        subscribers: List[str],
        importance_score: float,
        usage_pattern: str,
        similar_patterns: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate AI-powered event analysis

        Returns:
            {
                'insights': str,
                'recommendations': List[str],
                'confidence': float
            }
        """

        if not self.llm:
            await self.initialize()

        # Format similar patterns context
        patterns_context = self._format_patterns_context(similar_patterns) if similar_patterns else "No similar patterns found."

        # Build system prompt
        system_prompt = """You are an Event Intelligence AI expert specializing in event-driven architecture analysis.

Your task is to analyze events and provide:
1. Deep insights about the event's role in the system
2. Actionable recommendations for improvement
3. Potential risks and mitigation strategies

Be specific, practical, and focus on business and technical value."""

        # Build user prompt
        user_prompt = f"""
Analyze this event:

=== EVENT DETAILS ===
Event Name: {event_name}
Publishers: {', '.join(publishers) if publishers else 'None'}
Subscribers: {', '.join(subscribers) if subscribers else 'None'}
Importance Score: {importance_score:.2f} / 1.0
Usage Pattern: {usage_pattern}

=== SIMILAR PATTERNS (from knowledge base) ===
{patterns_context}

=== REQUIRED OUTPUT ===
Provide analysis in this JSON format:
{{
    "insights": "Detailed insights about the event's role and importance",
    "recommendations": ["Recommendation 1", "Recommendation 2", "Recommendation 3"],
    "risks": ["Potential risk 1", "Potential risk 2"],
    "confidence": 0.85
}}
"""

        try:
            response_text = await self.llm.query(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                task_type="code_analysis",
                temperature=0.3,  # Low for consistent analysis
                max_tokens=1000
            )

            # Parse JSON response
            import json
            analysis = json.loads(response_text)

            logger.info(f"🤖 Generated AI analysis for {event_name} (confidence: {analysis.get('confidence', 0)})")
            return analysis

        except Exception as e:
            logger.error(f"Failed to generate event analysis: {e}")
            # Fallback to simple heuristics
            return {
                'insights': f"Event '{event_name}' has {usage_pattern} usage pattern with importance {importance_score:.2f}",
                'recommendations': self._fallback_recommendations(event_name, publishers, subscribers, usage_pattern),
                'risks': [],
                'confidence': 0.3
            }

    # ============================================================
    # GAP PREDICTION
    # ============================================================

    async def retrieve_gap_patterns(
        self,
        current_gaps: List[Dict],
        gap_types: List[str]
    ) -> List[Dict]:
        """
        Retrieve historical gap patterns from knowledge base

        Args:
            current_gaps: Current gap list
            gap_types: Types of gaps detected

        Returns:
            Historical gap patterns and resolutions
        """

        if not self.rag:
            await self.initialize()

        search_query = f"""
        Gap types: {', '.join(gap_types)}
        Current gap count: {len(current_gaps)}
        """

        try:
            gap_patterns = await self.rag.retrieve(
                query=search_query,
                context={
                    "domain": "event_intelligence",
                    "task": "gap_prediction"
                },
                top_k=3,
                filters={"source_type": "gap_patterns"},
                enable_reranking=True
            )

            logger.info(f"📚 Retrieved {len(gap_patterns)} gap patterns")
            return gap_patterns

        except Exception as e:
            logger.warning(f"Failed to retrieve gap patterns: {e}")
            return []

    async def predict_future_gaps(
        self,
        current_gaps: List[Dict],
        historical_trend: List[Dict],
        gap_patterns: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Predict future event gaps using AI

        Returns:
            {
                'predictions': List[prediction objects],
                'probability': float,
                'recommended_actions': List[str]
            }
        """

        if not self.llm:
            await self.initialize()

        # Format historical trend
        trend_summary = self._format_trend_summary(historical_trend)
        patterns_context = self._format_patterns_context(gap_patterns) if gap_patterns else "No historical patterns."

        system_prompt = """You are an Event Intelligence AI expert specializing in predictive analysis.

Your task is to predict future event gaps based on:
1. Current gap state
2. Historical trends
3. Known patterns

Provide specific predictions with probability scores and actionable recommendations."""

        user_prompt = f"""
Predict future event gaps:

=== CURRENT STATE ===
Total Gaps: {len(current_gaps)}
Gap Details: {self._format_gaps(current_gaps[:5])}  # Top 5

=== HISTORICAL TREND ===
{trend_summary}

=== KNOWN PATTERNS ===
{patterns_context}

=== REQUIRED OUTPUT ===
Provide predictions in JSON format:
{{
    "predictions": [
        {{
            "gap_type": "missing_subscriber",
            "event_name": "user.registered",
            "probability": 0.75,
            "estimated_days": 3,
            "reasoning": "Based on pattern X..."
        }}
    ],
    "overall_probability": 0.65,
    "recommended_actions": ["Action 1", "Action 2"]
}}
"""

        try:
            response_text = await self.llm.query(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                task_type="prediction",
                temperature=0.4,  # Slightly higher for creative predictions
                max_tokens=1200
            )

            import json
            predictions = json.loads(response_text)

            logger.info(f"🔮 Generated {len(predictions.get('predictions', []))} gap predictions")
            return predictions

        except Exception as e:
            logger.error(f"Failed to predict gaps: {e}")
            return {
                'predictions': [],
                'overall_probability': 0.0,
                'recommended_actions': []
            }

    # ============================================================
    # AUTO-HEALING
    # ============================================================

    async def retrieve_healing_strategies(
        self,
        gap_type: str,
        event_name: str,
        service_name: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve proven healing strategies for specific gap types

        Returns:
            List of healing strategies with success rates
        """

        if not self.rag:
            await self.initialize()

        search_query = f"""
        Gap type: {gap_type}
        Event: {event_name}
        Service: {service_name or 'any'}
        """

        try:
            strategies = await self.rag.retrieve(
                query=search_query,
                context={
                    "domain": "event_intelligence",
                    "task": "auto_healing"
                },
                top_k=3,
                filters={"source_type": "healing_strategies"},
                enable_reranking=True
            )

            logger.info(f"📚 Retrieved {len(strategies)} healing strategies for {gap_type}")
            return strategies

        except Exception as e:
            logger.warning(f"Failed to retrieve healing strategies: {e}")
            return []

    async def generate_healing_code(
        self,
        gap_type: str,
        event_name: str,
        service_name: str,
        service_language: str = "python",
        healing_strategies: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate code to heal event gap

        Returns:
            {
                'code': str,
                'file_path': str,
                'instructions': str,
                'confidence': float
            }
        """

        if not self.llm:
            await self.initialize()

        strategies_context = self._format_patterns_context(healing_strategies) if healing_strategies else "No proven strategies found."

        system_prompt = f"""You are an Event Intelligence AI expert specializing in auto-healing code generation.

Your task is to generate production-ready {service_language} code to fix event architecture gaps.

Follow these principles:
1. Clean, idiomatic {service_language} code
2. Proper error handling
3. Logging and monitoring hooks
4. Type safety (when applicable)
5. Integration with existing patterns"""

        user_prompt = f"""
Generate healing code for this gap:

=== GAP DETAILS ===
Gap Type: {gap_type}
Event Name: {event_name}
Service: {service_name}
Language: {service_language}

=== PROVEN STRATEGIES ===
{strategies_context}

=== REQUIRED OUTPUT ===
Provide in JSON format:
{{
    "code": "Complete code here...",
    "file_path": "path/to/file.py",
    "instructions": "1. Step 1\\n2. Step 2...",
    "imports_needed": ["import module"],
    "confidence": 0.85
}}
"""

        try:
            response_text = await self.llm.query(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                task_type="code_generation",
                temperature=0.2,  # Very low for consistent code
                max_tokens=2000
            )

            import json
            healing_result = json.loads(response_text)

            logger.info(f"🔧 Generated healing code for {gap_type} in {service_name}")
            return healing_result

        except Exception as e:
            logger.error(f"Failed to generate healing code: {e}")
            return {
                'code': '',
                'file_path': '',
                'instructions': 'Auto-healing failed. Manual intervention required.',
                'confidence': 0.0
            }

    # ============================================================
    # PATTERN STORAGE (SELF-LEARNING)
    # ============================================================

    async def store_successful_analysis(
        self,
        event_name: str,
        publishers: List[str],
        subscribers: List[str],
        analysis_result: Dict,
        outcome: str = "success"
    ):
        """
        Store successful event analysis patterns for future learning
        """

        if not self.rag:
            await self.initialize()

        pattern_text = f"""
EVENT ANALYSIS PATTERN

Event: {event_name}
Publishers: {', '.join(publishers)}
Subscribers: {', '.join(subscribers)}

Analysis:
{analysis_result.get('insights', '')}

Recommendations:
{chr(10).join(f"- {rec}" for rec in analysis_result.get('recommendations', []))}

Outcome: {outcome}
Confidence: {analysis_result.get('confidence', 0.0)}
"""

        try:
            await self.rag.ingest_documents(
                documents=[{
                    "text": pattern_text,
                    "metadata": {
                        "source_type": "event_patterns",
                        "event_name": event_name,
                        "outcome": outcome,
                        "confidence": analysis_result.get('confidence', 0.0)
                    }
                }],
                source_type="event_patterns"
            )

            logger.info(f"💾 Stored analysis pattern for {event_name}")

        except Exception as e:
            logger.warning(f"Failed to store analysis pattern: {e}")

    async def store_gap_resolution(
        self,
        gap_type: str,
        event_name: str,
        resolution_strategy: str,
        success: bool
    ):
        """
        Store gap resolution patterns for future prediction
        """

        if not self.rag:
            await self.initialize()

        pattern_text = f"""
GAP RESOLUTION PATTERN

Gap Type: {gap_type}
Event: {event_name}
Resolution Strategy: {resolution_strategy}
Success: {success}

Details:
This pattern was {'successful' if success else 'unsuccessful'} in resolving {gap_type} gaps for {event_name} events.
"""

        try:
            await self.rag.ingest_documents(
                documents=[{
                    "text": pattern_text,
                    "metadata": {
                        "source_type": "gap_patterns",
                        "gap_type": gap_type,
                        "event_name": event_name,
                        "success": success
                    }
                }],
                source_type="gap_patterns"
            )

            logger.info(f"💾 Stored gap resolution pattern: {gap_type}")

        except Exception as e:
            logger.warning(f"Failed to store gap pattern: {e}")

    async def store_healing_strategy(
        self,
        gap_type: str,
        service_language: str,
        code: str,
        success_rate: float
    ):
        """
        Store successful healing strategies
        """

        if not self.rag:
            await self.initialize()

        strategy_text = f"""
HEALING STRATEGY

Gap Type: {gap_type}
Language: {service_language}
Success Rate: {success_rate * 100:.1f}%

Code:
{code}

This strategy has proven effective for {gap_type} gaps in {service_language} services.
"""

        try:
            await self.rag.ingest_documents(
                documents=[{
                    "text": strategy_text,
                    "metadata": {
                        "source_type": "healing_strategies",
                        "gap_type": gap_type,
                        "language": service_language,
                        "success_rate": success_rate
                    }
                }],
                source_type="healing_strategies"
            )

            logger.info(f"💾 Stored healing strategy for {gap_type}")

        except Exception as e:
            logger.warning(f"Failed to store healing strategy: {e}")

    # ============================================================
    # HELPER METHODS
    # ============================================================

    def _format_patterns_context(self, patterns: List[Dict]) -> str:
        """Format patterns for LLM context"""

        if not patterns:
            return "No patterns available."

        formatted = []
        for i, pattern in enumerate(patterns, 1):
            formatted.append(f"""
Pattern {i} (Relevance: {pattern.get('score', 0.0):.2f}):
{pattern.get('content', '')}
""")

        return "\n".join(formatted)

    def _format_trend_summary(self, historical_trend: List[Dict]) -> str:
        """Format historical trend for LLM"""

        if not historical_trend:
            return "No historical data available."

        summary = []
        for i, trend in enumerate(historical_trend[-7:], 1):  # Last 7 entries
            gap_count = len(trend.get('gaps', []))
            summary.append(f"Day {i}: {gap_count} gaps")

        return "\n".join(summary)

    def _format_gaps(self, gaps: List[Dict]) -> str:
        """Format gaps for display"""

        if not gaps:
            return "No gaps"

        formatted = []
        for gap in gaps:
            formatted.append(f"- {gap.get('gap_type', 'unknown')}: {gap.get('event_name', 'N/A')}")

        return "\n".join(formatted)

    def _fallback_recommendations(
        self,
        event_name: str,
        publishers: List[str],
        subscribers: List[str],
        usage_pattern: str
    ) -> List[str]:
        """Fallback recommendations when LLM fails"""

        recommendations = []

        if not publishers:
            recommendations.append(f"Add publisher for '{event_name}' or remove from schema")

        if publishers and not subscribers:
            recommendations.append(f"Consider adding subscribers for '{event_name}'")

        if usage_pattern == 'critical':
            recommendations.append(f"Add monitoring and alerts for critical event '{event_name}'")

        if usage_pattern == 'unused':
            recommendations.append(f"Event '{event_name}' appears unused - consider removal")

        return recommendations or ["No specific recommendations at this time"]

    async def test_connection(self) -> bool:
        """Test AI Foundation connection"""

        try:
            if not self._initialized:
                await self.initialize()

            # Test LLM
            test_response = await self.llm.query(
                system_prompt="You are a test assistant.",
                user_prompt="Respond with 'OK' if you can hear me.",
                task_type="general",
                max_tokens=10
            )

            return "OK" in test_response or len(test_response) > 0

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# ============================================================
# SINGLETON PATTERN
# ============================================================

_event_ai_foundation_instance: Optional[EventIntelligenceAIFoundation] = None


async def get_event_ai_foundation() -> EventIntelligenceAIFoundation:
    """
    Get singleton AI Foundation instance for Event Intelligence

    Returns:
        Initialized EventIntelligenceAIFoundation instance
    """

    global _event_ai_foundation_instance

    if _event_ai_foundation_instance is None:
        _event_ai_foundation_instance = EventIntelligenceAIFoundation()
        await _event_ai_foundation_instance.initialize()

    return _event_ai_foundation_instance
