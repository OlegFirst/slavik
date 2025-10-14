"""
Integration with ai-foundation/learning-knowledge
Использует СУЩЕСТВУЮЩИЕ компоненты для pattern detection и learning
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Add ai-foundation to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ai-foundation"))

from learning_knowledge.learning.engines.pattern_detector import PatternDetector
from learning_knowledge.learning.engines.knowledge_base_connector import KnowledgeBaseConnector
from learning_knowledge.learning.practice_learning import PracticeLearningEngine

logger = logging.getLogger(__name__)


class LearningIntegration:
    """
    Интеграция с ai-foundation/learning-knowledge

    ЧТО ИСПОЛЬЗУЕТ (УЖЕ СУЩЕСТВУЕТ):
    - PatternDetector: обнаружение паттернов
    - KnowledgeBaseConnector: сохранение в Qdrant
    - PracticeLearningEngine: обучение на практике

    ЧТО ДЕЛАЕТ:
    - НЕ дублирует логику
    - ИСПОЛЬЗУЕТ существующие движки
    - КООРДИНИРУЕТ их работу для System BCM
    """

    def __init__(self):
        try:
            self.pattern_detector = PatternDetector()
            self.kb_connector = KnowledgeBaseConnector()
            self.practice_learning = PracticeLearningEngine()
            logger.info("✅ Learning integration initialized (using existing components)")
        except Exception as e:
            logger.error(f"❌ Failed to initialize learning integration: {e}")
            # Fallback to basic mode
            self.pattern_detector = None
            self.kb_connector = None
            self.practice_learning = None

    async def detect_patterns(self, bcm_cycles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Обнаружить паттерны в BCM циклах

        ИСПОЛЬЗУЕТ: PatternDetector (УЖЕ СУЩЕСТВУЕТ)
        НЕ: Свою логику pattern detection
        """
        if not self.pattern_detector:
            logger.warning("⚠️  Pattern detector not available, using fallback")
            return self._fallback_pattern_detection(bcm_cycles)

        try:
            # Подготовить данные для pattern detector
            pattern_data = {
                "data": bcm_cycles,
                "domain": "system_bcm",
                "features": [
                    "duration_seconds",
                    "rto_compliance_rate",
                    "platform_health_score",
                    "insights_generated",
                    "improvements_applied"
                ],
                "window_size": 10,  # Анализировать последние 10 циклов
                "confidence_threshold": 0.7
            }

            # ИСПОЛЬЗОВАТЬ СУЩЕСТВУЮЩИЙ DETECTOR
            patterns = await self.pattern_detector.detect(pattern_data)

            logger.info(f"✅ Detected {len(patterns)} patterns using PatternDetector")

            # Обогатить паттерны BCM-специфичным контекстом
            enriched_patterns = []
            for pattern in patterns:
                enriched_patterns.append({
                    **pattern,
                    "bcm_context": {
                        "domain": "platform_bcm",
                        "detected_at": datetime.utcnow().isoformat(),
                        "source": "system-bcm-service"
                    }
                })

            return enriched_patterns

        except Exception as e:
            logger.error(f"❌ Pattern detection failed: {e}")
            return self._fallback_pattern_detection(bcm_cycles)

    async def save_to_knowledge_base(self, patterns: List[Dict[str, Any]]) -> bool:
        """
        Сохранить паттерны в knowledge base (Qdrant)

        ИСПОЛЬЗУЕТ: KnowledgeBaseConnector (УЖЕ СУЩЕСТВУЕТ)
        НЕ: Свою базу данных
        """
        if not self.kb_connector:
            logger.warning("⚠️  Knowledge base connector not available")
            return False

        try:
            # ИСПОЛЬЗОВАТЬ СУЩЕСТВУЮЩИЙ CONNECTOR
            result = await self.kb_connector.save_patterns({
                "patterns": patterns,
                "collection": "bcm_patterns",  # Коллекция в Qdrant
                "metadata": {
                    "source": "system-bcm",
                    "timestamp": datetime.utcnow().isoformat()
                }
            })

            logger.info(f"✅ Saved {len(patterns)} patterns to knowledge base (Qdrant)")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save to knowledge base: {e}")
            return False

    async def learn_from_practice(
        self,
        cycle_results: Dict[str, Any],
        effectiveness_score: float
    ) -> Dict[str, Any]:
        """
        Обучение на практике из результатов BCM цикла

        ИСПОЛЬЗУЕТ: PracticeLearningEngine (УЖЕ СУЩЕСТВУЕТ)
        НЕ: Свою логику practice learning
        """
        if not self.practice_learning:
            logger.warning("⚠️  Practice learning engine not available")
            return {"status": "skipped"}

        try:
            # Подготовить learning case
            learning_case = {
                "domain": "system_bcm",
                "action_taken": cycle_results.get("improvements_applied", []),
                "outcome": {
                    "rto_compliance": cycle_results.get("rto_compliance_rate"),
                    "health_score": cycle_results.get("platform_health_score"),
                    "effectiveness": effectiveness_score
                },
                "context": {
                    "platform_state": cycle_results.get("bia_results"),
                    "detected_risks": cycle_results.get("risk_results"),
                    "recovery_executed": cycle_results.get("recovery_results")
                },
                "timestamp": datetime.utcnow().isoformat()
            }

            # ИСПОЛЬЗОВАТЬ СУЩЕСТВУЮЩИЙ PRACTICE LEARNING
            learning_result = await self.practice_learning.learn_from_case(learning_case)

            logger.info(f"✅ Practice learning completed: {learning_result.get('insights_count', 0)} insights")

            return learning_result

        except Exception as e:
            logger.error(f"❌ Practice learning failed: {e}")
            return {"status": "error", "error": str(e)}

    async def get_historical_insights(
        self,
        context: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Получить исторические insights из knowledge base

        ИСПОЛЬЗУЕТ: KnowledgeBaseConnector для поиска
        """
        if not self.kb_connector:
            return []

        try:
            # Поиск похожих случаев
            insights = await self.kb_connector.search_similar({
                "query": context,
                "collection": "bcm_insights",
                "limit": limit,
                "min_score": 0.6
            })

            return insights

        except Exception as e:
            logger.error(f"❌ Failed to get historical insights: {e}")
            return []

    def _fallback_pattern_detection(self, bcm_cycles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Упрощенное обнаружение паттернов (если основной детектор недоступен)
        """
        patterns = []

        if len(bcm_cycles) < 2:
            return patterns

        # Простые паттерны
        recent_cycles = bcm_cycles[-5:]

        # Паттерн: постоянно медленные циклы
        avg_duration = sum(c.get("duration_seconds", 0) for c in recent_cycles) / len(recent_cycles)
        if avg_duration > 25:  # Целевое время 30s, но хотим быстрее
            patterns.append({
                "type": "slow_cycles",
                "description": f"Average cycle duration {avg_duration:.1f}s exceeds optimal",
                "confidence": 0.8,
                "recommendation": "Investigate phase bottlenecks"
            })

        # Паттерн: снижение RTO compliance
        rto_rates = [c.get("rto_compliance_rate", 100) for c in recent_cycles if c.get("rto_compliance_rate")]
        if rto_rates and sum(rto_rates) / len(rto_rates) < 95:
            patterns.append({
                "type": "rto_degradation",
                "description": "RTO compliance rate below target (95%)",
                "confidence": 0.9,
                "recommendation": "Review recovery procedures and timeouts"
            })

        return patterns


# Export
__all__ = ["LearningIntegration"]
