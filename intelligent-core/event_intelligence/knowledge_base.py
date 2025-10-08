"""
Event Intelligence Knowledge Base - Integration Layer

Интеграция с ai-foundation/learning-knowledge для работы с Knowledge Base
Адаптирует KnowledgeBaseClient для нужд event_intelligence
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import sys

# Add ai-foundation to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "ai-foundation" / "learning-knowledge"))

try:
    from learning.engines.knowledge_base_connector import (
        KnowledgeBaseClient,
        KnowledgeAutoCreator,
        EnhancedKnowledgeIntegrator
    )
    KNOWLEDGE_BASE_AVAILABLE = True
except ImportError:
    KNOWLEDGE_BASE_AVAILABLE = False
    logging.warning("⚠️ ai-foundation/learning-knowledge not available, using stub")

logger = logging.getLogger(__name__)


class EventKnowledgeBase:
    """
    Knowledge Base для Event Intelligence

    Использует ai-foundation/learning-knowledge для:
    - Хранения информации о событиях
    - Накопления знаний о паттернах
    - Обучения на исторических данных
    - Генерации рекомендаций
    """

    def __init__(self, kb_base_url: str = "http://localhost:8040"):
        """
        Args:
            kb_base_url: URL Knowledge Base Service
        """
        self.kb_base_url = kb_base_url

        if KNOWLEDGE_BASE_AVAILABLE:
            self.integrator = EnhancedKnowledgeIntegrator(kb_base_url)
            self.kb_client = self.integrator.kb_client
            self.auto_creator = self.integrator.auto_creator
            logger.info("✅ Event Knowledge Base initialized with ai-foundation integration")
        else:
            self.integrator = None
            self.kb_client = None
            self.auto_creator = None
            logger.warning("⚠️ Event Knowledge Base running in stub mode")

        # Local fallback storage
        self.local_knowledge = {
            'events': {},
            'patterns': {},
            'insights': {}
        }

    async def store_event_analysis(
        self,
        event_name: str,
        analysis: Dict[str, Any]
    ) -> Optional[str]:
        """
        Сохранить анализ события в Knowledge Base

        Args:
            event_name: Имя события
            analysis: Результаты анализа (EventAnalysis)

        Returns:
            ID созданной статьи или None
        """
        if not KNOWLEDGE_BASE_AVAILABLE or not self.kb_client:
            logger.debug(f"Storing {event_name} analysis locally (KB unavailable)")
            self.local_knowledge['events'][event_name] = analysis
            return f"local_{event_name}"

        # Создать статью в KB
        article_data = {
            'title': f"Event Analysis: {event_name}",
            'content': self._format_analysis_content(event_name, analysis),
            'type': 'event_analysis',
            'domain': 'EventIntelligence',
            'category': 'analysis',
            'tags': [
                'event',
                'analysis',
                analysis.get('usage_pattern', 'unknown'),
                f"importance_{int(analysis.get('importance_score', 0) * 100)}"
            ],
            'metadata': {
                'event_name': event_name,
                'importance_score': analysis.get('importance_score', 0),
                'usage_pattern': analysis.get('usage_pattern', 'unknown'),
                'auto_generated': True,
                'source': 'event_intelligence'
            }
        }

        try:
            article_id = await self.kb_client.create_article(article_data)
            logger.info(f"✅ Stored analysis for '{event_name}' in KB: {article_id}")
            return article_id
        except Exception as e:
            logger.error(f"❌ Failed to store analysis: {e}")
            # Fallback to local storage
            self.local_knowledge['events'][event_name] = analysis
            return f"local_{event_name}"

    async def store_pattern(
        self,
        pattern_id: str,
        pattern_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Сохранить обнаруженный паттерн

        Args:
            pattern_id: ID паттерна
            pattern_data: Данные паттерна (Pattern)

        Returns:
            ID созданной статьи
        """
        if not KNOWLEDGE_BASE_AVAILABLE or not self.kb_client:
            self.local_knowledge['patterns'][pattern_id] = pattern_data
            return f"local_pattern_{pattern_id}"

        article_data = {
            'title': f"Event Pattern: {pattern_data.get('description', pattern_id)}",
            'content': self._format_pattern_content(pattern_data),
            'type': 'event_pattern',
            'domain': 'EventIntelligence',
            'category': 'pattern',
            'tags': [
                'pattern',
                pattern_data.get('pattern_type', 'unknown'),
                f"confidence_{int(pattern_data.get('confidence', 0) * 100)}"
            ],
            'metadata': {
                'pattern_id': pattern_id,
                'pattern_type': pattern_data.get('pattern_type'),
                'confidence': pattern_data.get('confidence', 0),
                'examples_count': len(pattern_data.get('examples', [])),
                'source': 'event_intelligence'
            }
        }

        try:
            article_id = await self.kb_client.create_article(article_data)
            logger.info(f"✅ Stored pattern '{pattern_id}' in KB: {article_id}")
            return article_id
        except Exception as e:
            logger.error(f"❌ Failed to store pattern: {e}")
            self.local_knowledge['patterns'][pattern_id] = pattern_data
            return f"local_pattern_{pattern_id}"

    async def get_similar_events(
        self,
        event_name: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Найти похожие события в Knowledge Base

        Args:
            event_name: Имя события для поиска
            limit: Максимум результатов

        Returns:
            Список похожих событий
        """
        if not KNOWLEDGE_BASE_AVAILABLE or not self.kb_client:
            logger.debug("Using local knowledge for similar events search")
            # Simple local search
            return list(self.local_knowledge['events'].values())[:limit]

        try:
            results = await self.kb_client.search(
                query=event_name,
                filters={'type': 'event_analysis'},
                limit=limit
            )
            logger.info(f"Found {len(results)} similar events for '{event_name}'")
            return results
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return []

    async def get_relevant_patterns(
        self,
        event_name: str,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Получить релевантные паттерны для события

        Args:
            event_name: Имя события
            limit: Максимум паттернов

        Returns:
            Список релевантных паттернов
        """
        if not KNOWLEDGE_BASE_AVAILABLE or not self.kb_client:
            return list(self.local_knowledge['patterns'].values())[:limit]

        try:
            results = await self.kb_client.search(
                query=event_name,
                filters={'type': 'event_pattern'},
                limit=limit
            )
            return results
        except Exception as e:
            logger.error(f"❌ Pattern search failed: {e}")
            return []

    async def get_learning_stats(self) -> Dict[str, Any]:
        """
        Получить статистику обучения

        Returns:
            Статистика Knowledge Base
        """
        if not KNOWLEDGE_BASE_AVAILABLE:
            return {
                'events_stored': len(self.local_knowledge['events']),
                'patterns_stored': len(self.local_knowledge['patterns']),
                'insights_stored': len(self.local_knowledge['insights']),
                'storage_mode': 'local'
            }

        # TODO: Implement real KB stats query
        return {
            'events_stored': 'N/A',
            'patterns_stored': 'N/A',
            'kb_connected': KNOWLEDGE_BASE_AVAILABLE,
            'kb_url': self.kb_base_url,
            'storage_mode': 'knowledge_base'
        }

    def _format_analysis_content(
        self,
        event_name: str,
        analysis: Dict[str, Any]
    ) -> str:
        """Форматирует результаты анализа в markdown контент"""

        importance = analysis.get('importance_score', 0)
        pattern = analysis.get('usage_pattern', 'unknown')
        recommendations = analysis.get('recommendations', [])
        insights = analysis.get('ai_insights', '')

        content = f"""# Event Analysis: {event_name}

## 📊 Важность События

**Importance Score:** {importance:.2f}/1.00

**Usage Pattern:** {pattern.upper()}

## 🤖 AI Insights

{insights}

## 💡 Рекомендации

"""
        for idx, rec in enumerate(recommendations, 1):
            content += f"{idx}. {rec}\n"

        content += f"""

## 📈 История Анализа

Этот анализ был выполнен системой Event Intelligence для оценки важности и паттернов использования события.

---

*Auto-generated by Event Intelligence System*
*Event: {event_name}*
"""

        return content

    def _format_pattern_content(self, pattern_data: Dict[str, Any]) -> str:
        """Форматирует паттерн в markdown контент"""

        pattern_type = pattern_data.get('pattern_type', 'unknown')
        description = pattern_data.get('description', 'No description')
        confidence = pattern_data.get('confidence', 0)
        examples = pattern_data.get('examples', [])

        content = f"""# Event Pattern: {description}

## 🔍 Тип Паттерна

**Type:** {pattern_type.upper()}

**Confidence Level:** {confidence:.0%}

## 📝 Описание

{description}

## 📊 Примеры

"""
        for idx, example in enumerate(examples, 1):
            content += f"{idx}. `{example}`\n"

        content += f"""

## 💡 Применение

Этот паттерн был обнаружен при анализе событий и может быть использован для:
- Предсказания поведения похожих событий
- Улучшения рекомендаций
- Обучения на исторических данных

---

*Auto-detected by Event Intelligence System*
*Confidence: {confidence:.0%}*
"""

        return content


# Stub implementation when ai-foundation is not available
class StubKnowledgeBase(EventKnowledgeBase):
    """Заглушка для тестирования без ai-foundation"""

    def __init__(self, kb_base_url: str = "http://localhost:8040"):
        super().__init__(kb_base_url)
        logger.info("🔶 Using Stub Knowledge Base (ai-foundation not available)")


# Export main class
__all__ = ['EventKnowledgeBase', 'KNOWLEDGE_BASE_AVAILABLE']
