"""
Integration with ai-foundation (RAG + LLM)
Использует СУЩЕСТВУЮЩИЕ RAG pipeline и LLM router
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# Add ai-foundation to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ai-foundation"))

try:
    from rag.pipeline import RAGPipeline
    from rag.qdrant_client import QdrantClient
    from llm.llm_router import LLMRouter
    RAG_LLM_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️  RAG/LLM not available: {e}")
    RAG_LLM_AVAILABLE = False

logger = logging.getLogger(__name__)


class AIIntegration:
    """
    Интеграция с ai-foundation (RAG + LLM)

    ЧТО ИСПОЛЬЗУЕТ (УЖЕ СУЩЕСТВУЕТ):
    - RAGPipeline: поиск похожих случаев через Qdrant
    - QdrantClient: vector database (347+ кейсов)
    - LLMRouter: Claude/GPT для анализа

    ЧТО ДЕЛАЕТ:
    - ИЩЕТ решения через RAG (не hardcoded правила)
    - АНАЛИЗИРУЕТ через LLM (не простые if/else)
    - ИСПОЛЬЗУЕТ 347+ кейсов для обучения
    """

    def __init__(self):
        if RAG_LLM_AVAILABLE:
            try:
                self.rag_pipeline = RAGPipeline()
                self.qdrant = QdrantClient()
                self.llm_router = LLMRouter()
                logger.info("✅ AI integration initialized (RAG + LLM available)")
            except Exception as e:
                logger.error(f"❌ Failed to initialize AI components: {e}")
                RAG_LLM_AVAILABLE = False

        if not RAG_LLM_AVAILABLE:
            logger.warning("⚠️  Running without RAG/LLM (fallback to rules)")
            self.rag_pipeline = None

    async def find_similar_solutions(
        self,
        issue_description: str,
        context: Dict[str, Any] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Найти похожие решения через RAG

        ИСПОЛЬЗУЕТ: RAGPipeline + Qdrant (УЖЕ СУЩЕСТВУЮТ)
        НЕ: PostgreSQL поиск
        """
        if not self.rag_pipeline:
            return []

        try:
            # ИСПОЛЬЗОВАТЬ СУЩЕСТВУЮЩИЙ RAG PIPELINE
            similar_cases = await self.rag_pipeline.retrieve_similar({
                "query": issue_description,
                "collection": "bcm_patterns",  # Паттерны из Collective
                "top_k": top_k,
                "min_score": 0.65,  # Минимальная похожесть
                "metadata_filter": {
                    "domain": "system_bcm",
                    "verified": True  # Только проверенные решения
                }
            })

            logger.info(f"✅ Found {len(similar_cases)} similar solutions via RAG")

            # Обогатить контекстом
            enriched_solutions = []
            for case in similar_cases:
                enriched_solutions.append({
                    "solution": case.get("solution"),
                    "similarity_score": case.get("score", 0),
                    "previous_effectiveness": case.get("effectiveness", 0),
                    "usage_count": case.get("metadata", {}).get("usage_count", 0),
                    "last_success": case.get("metadata", {}).get("last_used_at"),
                    "context": case.get("metadata", {})
                })

            return enriched_solutions

        except Exception as e:
            logger.error(f"❌ RAG search failed: {e}")
            return []

    async def analyze_with_llm(
        self,
        situation: Dict[str, Any],
        similar_cases: List[Dict[str, Any]] = None,
        expert_insights: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Глубокий анализ через LLM

        ИСПОЛЬЗУЕТ: LLMRouter (Claude/GPT) (УЖЕ СУЩЕСТВУЕТ)
        НЕ: Hardcoded правила
        """
        if not self.llm_router:
            return self._fallback_analysis(situation)

        try:
            # Подготовить промпт с контекстом
            prompt = self._build_analysis_prompt(
                situation,
                similar_cases or [],
                expert_insights or []
            )

            # ИСПОЛЬЗОВАТЬ СУЩЕСТВУЮЩИЙ LLM ROUTER
            response = await self.llm_router.complete({
                "model": "claude-3-5-sonnet",  # Или GPT-4
                "messages": [
                    {
                        "role": "system",
                        "content": """You are an expert in Business Continuity Management (BCM)
                        and platform reliability. Analyze situations and provide actionable,
                        prioritized recommendations based on ISO 22301 best practices."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,  # Более детерминированный
                "max_tokens": 2000
            })

            # Парсинг ответа LLM
            analysis = self._parse_llm_response(response)

            logger.info(f"✅ LLM analysis completed ({len(analysis.get('recommendations', []))} recommendations)")

            return {
                "analysis": analysis,
                "model_used": "claude-3-5-sonnet",
                "confidence": analysis.get("confidence", 0.85),
                "sources": {
                    "similar_cases": len(similar_cases) if similar_cases else 0,
                    "expert_insights": len(expert_insights) if expert_insights else 0
                }
            }

        except Exception as e:
            logger.error(f"❌ LLM analysis failed: {e}")
            return self._fallback_analysis(situation)

    async def generate_comprehensive_insights(
        self,
        cycle_results: Dict[str, Any],
        patterns: List[Dict[str, Any]],
        expert_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Генерация комплексных insights через RAG + LLM

        КОМБИНИРУЕТ:
        1. RAG: Поиск похожих случаев
        2. LLM: Глубокий анализ с контекстом
        3. Expert: Консультации AI-специалистов
        """
        # 1. RAG: Найти похожие случаи
        issue_description = self._describe_current_situation(cycle_results, patterns)
        similar_solutions = await self.find_similar_solutions(
            issue_description,
            context=cycle_results
        )

        # 2. LLM: Анализ с полным контекстом
        llm_analysis = await self.analyze_with_llm(
            situation={
                "cycle_results": cycle_results,
                "detected_patterns": patterns
            },
            similar_cases=similar_solutions,
            expert_insights=expert_analysis.get("strategic", {}).get("insights", [])
        )

        # 3. Объединить всё
        comprehensive_insights = {
            "rag_findings": {
                "similar_cases_found": len(similar_solutions),
                "proven_solutions": [s["solution"] for s in similar_solutions[:3]],
                "avg_effectiveness": self._avg_effectiveness(similar_solutions)
            },
            "llm_analysis": llm_analysis["analysis"],
            "expert_validation": expert_analysis,
            "final_recommendations": self._prioritize_recommendations(
                rag_solutions=similar_solutions,
                llm_recommendations=llm_analysis["analysis"].get("recommendations", []),
                expert_recommendations=expert_analysis.get("strategic", {}).get("recommendations", [])
            ),
            "confidence_score": self._calculate_confidence(
                similar_solutions,
                llm_analysis,
                expert_analysis
            )
        }

        return comprehensive_insights

    async def index_pattern_in_qdrant(
        self,
        pattern: Dict[str, Any],
        effectiveness: float = None
    ) -> bool:
        """
        Индексировать паттерн в Qdrant для будущего RAG поиска

        ИСПОЛЬЗУЕТ: QdrantClient (УЖЕ СУЩЕСТВУЕТ)
        """
        if not self.qdrant:
            return False

        try:
            # ИСПОЛЬЗОВАТЬ СУЩЕСТВУЮЩИЙ QDRANT CLIENT
            await self.qdrant.index_document({
                "collection": "bcm_patterns",
                "document": {
                    "text": self._pattern_to_text(pattern),
                    "metadata": {
                        "pattern_type": pattern.get("type"),
                        "confidence": pattern.get("confidence_score", 0.7),
                        "effectiveness": effectiveness,
                        "domain": "system_bcm",
                        "indexed_at": datetime.utcnow().isoformat()
                    }
                }
            })

            logger.info(f"✅ Pattern indexed in Qdrant for RAG")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to index in Qdrant: {e}")
            return False

    def _build_analysis_prompt(
        self,
        situation: Dict[str, Any],
        similar_cases: List[Dict[str, Any]],
        expert_insights: List[Dict[str, Any]]
    ) -> str:
        """Построить промпт для LLM анализа"""
        prompt = f"""
Analyze the following Platform BCM situation and provide recommendations:

## Current Situation
{self._format_situation(situation)}

## Similar Historical Cases ({len(similar_cases)} found)
{self._format_similar_cases(similar_cases)}

## Expert AI Specialist Insights
{self._format_expert_insights(expert_insights)}

## Your Task
Based on ISO 22301 best practices and the context above, provide:

1. **Root Cause Analysis**: What's causing the issues?
2. **Prioritized Recommendations**: Top 5 actions (ordered by impact/effort)
3. **Predicted Impact**: What happens if we don't act?
4. **Success Probability**: Likelihood each recommendation will work
5. **Implementation Timeline**: Quick wins vs. long-term fixes

Format your response as JSON with these fields:
- root_causes: [list of identified causes]
- recommendations: [list of {action, priority, impact, effort, success_probability}]
- predicted_impact: {if_no_action, if_action_taken}
- timeline: {quick_wins, medium_term, long_term}
- confidence: overall confidence score (0-1)
"""
        return prompt

    def _format_situation(self, situation: Dict[str, Any]) -> str:
        """Форматировать текущую ситуацию"""
        cycle_results = situation.get("cycle_results", {})
        patterns = situation.get("detected_patterns", [])

        return f"""
- RTO Compliance: {cycle_results.get('rto_compliance_rate', 'N/A')}%
- Platform Health: {cycle_results.get('platform_health_score', 'N/A')}%
- Cycle Duration: {cycle_results.get('duration_seconds', 'N/A')}s
- Insights Generated: {cycle_results.get('insights_generated', 0)}
- Detected Patterns: {len(patterns)} ({', '.join([p.get('type', 'unknown') for p in patterns])})
"""

    def _format_similar_cases(self, similar_cases: List[Dict[str, Any]]) -> str:
        """Форматировать похожие случаи"""
        if not similar_cases:
            return "No similar cases found in knowledge base."

        formatted = []
        for i, case in enumerate(similar_cases[:3], 1):
            formatted.append(f"""
Case {i} (similarity: {case.get('similarity_score', 0):.2f}):
- Solution: {case.get('solution', 'N/A')}
- Effectiveness: {case.get('previous_effectiveness', 0):.1f}%
- Used {case.get('usage_count', 0)} times successfully
""")

        return "\n".join(formatted)

    def _format_expert_insights(self, expert_insights: List[Dict[str, Any]]) -> str:
        """Форматировать insights от экспертов"""
        if not expert_insights:
            return "No expert insights available."

        formatted = []
        for i, insight in enumerate(expert_insights[:3], 1):
            formatted.append(f"""
Insight {i}:
- Type: {insight.get('type', 'N/A')}
- Description: {insight.get('description', 'N/A')}
- Recommendation: {insight.get('recommendation', 'N/A')}
""")

        return "\n".join(formatted)

    def _parse_llm_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Парсинг ответа LLM"""
        import json

        content = response.get("content", "")

        try:
            # Попытка парсить JSON из ответа
            # LLM часто возвращает JSON в code block
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
                return json.loads(json_str)
            else:
                return json.loads(content)
        except:
            # Fallback: простой парсинг
            return {
                "root_causes": ["LLM response parsing failed"],
                "recommendations": [{
                    "action": content[:200],
                    "priority": "medium"
                }],
                "confidence": 0.5
            }

    def _prioritize_recommendations(
        self,
        rag_solutions: List[Dict[str, Any]],
        llm_recommendations: List[Dict[str, Any]],
        expert_recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Приоритизация рекомендаций из всех источников

        Вес источников:
        - RAG (proven solutions): 0.4
        - LLM (analysis): 0.3
        - Experts (specialist insights): 0.3
        """
        all_recommendations = []

        # RAG solutions (проверенные)
        for sol in rag_solutions:
            all_recommendations.append({
                "source": "RAG (proven solution)",
                "action": sol.get("solution"),
                "priority": "high" if sol.get("previous_effectiveness", 0) > 80 else "medium",
                "confidence": sol.get("similarity_score", 0) * 0.4,
                "effectiveness_history": sol.get("previous_effectiveness", 0)
            })

        # LLM recommendations (анализ)
        for rec in llm_recommendations:
            all_recommendations.append({
                "source": "LLM (analysis)",
                "action": rec.get("action"),
                "priority": rec.get("priority", "medium"),
                "confidence": rec.get("success_probability", 0.7) * 0.3,
                "impact": rec.get("impact"),
                "effort": rec.get("effort")
            })

        # Expert recommendations (специалисты)
        for rec in expert_recommendations:
            all_recommendations.append({
                "source": "AI Specialist",
                "action": rec.get("recommendation", rec),
                "priority": rec.get("priority", "medium"),
                "confidence": 0.3  # Baseline confidence для экспертов
            })

        # Сортировка по приоритету и confidence
        priority_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        all_recommendations.sort(
            key=lambda r: (
                priority_order.get(r.get("priority", "medium"), 2),
                r.get("confidence", 0)
            ),
            reverse=True
        )

        return all_recommendations[:10]  # Top 10

    def _calculate_confidence(
        self,
        rag_solutions: List[Dict[str, Any]],
        llm_analysis: Dict[str, Any],
        expert_analysis: Dict[str, Any]
    ) -> float:
        """Рассчитать общую уверенность в рекомендациях"""
        confidences = []

        # RAG confidence
        if rag_solutions:
            avg_rag_score = sum(s.get("similarity_score", 0) for s in rag_solutions) / len(rag_solutions)
            confidences.append(avg_rag_score)

        # LLM confidence
        llm_confidence = llm_analysis.get("confidence", 0.7)
        confidences.append(llm_confidence)

        # Expert confidence
        expert_confidence = expert_analysis.get("strategic", {}).get("confidence", 0.8)
        confidences.append(expert_confidence)

        return sum(confidences) / len(confidences) if confidences else 0.6

    def _describe_current_situation(
        self,
        cycle_results: Dict[str, Any],
        patterns: List[Dict[str, Any]]
    ) -> str:
        """Описать текущую ситуацию для RAG поиска"""
        description_parts = []

        # Основные метрики
        rto = cycle_results.get("rto_compliance_rate", 100)
        health = cycle_results.get("platform_health_score", 100)
        duration = cycle_results.get("duration_seconds", 0)

        if rto < 95:
            description_parts.append(f"RTO compliance degraded to {rto}%")
        if health < 90:
            description_parts.append(f"Platform health score dropped to {health}%")
        if duration > 25:
            description_parts.append(f"BCM cycle duration increased to {duration}s")

        # Паттерны
        for pattern in patterns:
            description_parts.append(f"Detected pattern: {pattern.get('type', 'unknown')}")

        return " | ".join(description_parts) if description_parts else "Normal operation"

    def _pattern_to_text(self, pattern: Dict[str, Any]) -> str:
        """Конвертировать паттерн в текст для индексации"""
        return f"{pattern.get('type', 'pattern')}: {pattern.get('description', '')} (confidence: {pattern.get('confidence_score', 0)})"

    def _avg_effectiveness(self, solutions: List[Dict[str, Any]]) -> float:
        """Средняя эффективность найденных решений"""
        if not solutions:
            return 0.0

        effectiveness_values = [s.get("previous_effectiveness", 0) for s in solutions]
        return sum(effectiveness_values) / len(effectiveness_values)

    def _fallback_analysis(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """Упрощенный анализ если LLM недоступен"""
        cycle_results = situation.get("cycle_results", {})

        recommendations = []
        if cycle_results.get("rto_compliance_rate", 100) < 95:
            recommendations.append({
                "action": "Review and optimize recovery procedures",
                "priority": "high",
                "impact": "high",
                "effort": "medium"
            })

        if cycle_results.get("platform_health_score", 100) < 90:
            recommendations.append({
                "action": "Investigate degraded services",
                "priority": "high",
                "impact": "high",
                "effort": "low"
            })

        return {
            "root_causes": ["Metrics degradation (fallback analysis)"],
            "recommendations": recommendations,
            "confidence": 0.5
        }


# Export
__all__ = ["AIIntegration"]
