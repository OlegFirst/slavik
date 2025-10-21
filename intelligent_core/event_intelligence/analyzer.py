"""
Event Analyzer - Интеллектуальный анализ событий

Функции:
- Глубокий анализ event patterns
- Определение важности событий
- Обнаружение антипаттернов
- Рекомендации на основе AI
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class EventAnalysis:
    """Результат анализа события"""
    event_name: str
    importance_score: float  # 0-1
    usage_pattern: str  # 'critical', 'frequent', 'rare', 'unused'
    recommendations: List[str]
    ai_insights: str


class EventAnalyzer:
    """
    AI-powered анализатор событий

    Возможности:
    - Определяет важность события для системы
    - Анализирует паттерны использования
    - Находит связи между событиями
    - Даёт рекомендации на основе AI
    """

    def __init__(self):
        self.analysis_history = []

    async def analyze_event(
        self,
        event_name: str,
        publishers: List[str],
        subscribers: List[str],
        historical_data: Optional[Dict] = None
    ) -> EventAnalysis:
        """
        Глубокий анализ одного события

        Args:
            event_name: Имя события
            publishers: Список publishers
            subscribers: Список subscribers
            historical_data: Исторические данные (опционально)

        Returns:
            EventAnalysis с результатами
        """
        logger.info(f" Analyzing event: {event_name}")

        # Вычисляем importance score
        importance = self._calculate_importance(
            len(publishers),
            len(subscribers),
            historical_data
        )

        # Определяем usage pattern
        pattern = self._determine_usage_pattern(
            len(publishers),
            len(subscribers)
        )

        # Генерируем рекомендации
        recommendations = self._generate_recommendations(
            event_name,
            publishers,
            subscribers,
            importance,
            pattern
        )

        # AI insights
        insights = self._generate_ai_insights(
            event_name,
            importance,
            pattern
        )

        analysis = EventAnalysis(
            event_name=event_name,
            importance_score=importance,
            usage_pattern=pattern,
            recommendations=recommendations,
            ai_insights=insights
        )

        # Сохраняем в историю
        self.analysis_history.append(analysis)

        return analysis

    def _calculate_importance(
        self,
        publisher_count: int,
        subscriber_count: int,
        historical_data: Optional[Dict]
    ) -> float:
        """Вычисляет важность события (0-1)"""

        # Базовая формула
        base_score = 0.0

        # Факторы важности:
        # 1. Количество publishers (max 0.3)
        if publisher_count > 0:
            base_score += min(publisher_count * 0.15, 0.3)

        # 2. Количество subscribers (max 0.4)
        if subscriber_count > 0:
            base_score += min(subscriber_count * 0.1, 0.4)

        # 3. Баланс pub/sub (max 0.3)
        if publisher_count > 0 and subscriber_count > 0:
            ratio = min(publisher_count, subscriber_count) / max(publisher_count, subscriber_count)
            base_score += ratio * 0.3

        # TODO: Добавить ML-модель для более точной оценки
        # if historical_data:
        #     ml_score = self.ml_model.predict(historical_data)
        #     base_score = (base_score + ml_score) / 2

        return min(base_score, 1.0)

    def _determine_usage_pattern(
        self,
        publisher_count: int,
        subscriber_count: int
    ) -> str:
        """Определяет паттерн использования"""

        if publisher_count == 0 and subscriber_count == 0:
            return 'unused'

        if publisher_count >= 3 or subscriber_count >= 3:
            return 'critical'

        if publisher_count >= 1 and subscriber_count >= 1:
            return 'frequent'

        return 'rare'

    def _generate_recommendations(
        self,
        event_name: str,
        publishers: List[str],
        subscribers: List[str],
        importance: float,
        pattern: str
    ) -> List[str]:
        """Генерирует рекомендации"""

        recommendations = []

        # Если нет publishers
        if not publishers:
            recommendations.append(
                f"️ Add publisher for '{event_name}' or remove from schema"
            )

        # Если нет subscribers но есть publishers
        if publishers and not subscribers:
            if importance > 0.5:
                recommendations.append(
                    f" Consider adding subscribers for high-importance event '{event_name}'"
                )

        # Если критичное событие
        if pattern == 'critical':
            recommendations.append(
                f" Critical event '{event_name}' - ensure proper error handling"
            )
            recommendations.append(
                f" Add monitoring and alerts for '{event_name}'"
            )

        # Если не используется
        if pattern == 'unused':
            recommendations.append(
                f"️ Event '{event_name}' is unused - consider removing"
            )

        return recommendations

    def _generate_ai_insights(
        self,
        event_name: str,
        importance: float,
        pattern: str
    ) -> str:
        """Генерирует AI insights"""

        # Простая эвристика (TODO: заменить на LLM)

        if importance > 0.8:
            return f" AI Analysis: '{event_name}' is a core system event with high business value. Prioritize stability and monitoring."

        if importance > 0.5:
            return f" AI Analysis: '{event_name}' has medium importance. Good candidate for reactive processing."

        if pattern == 'unused':
            return f" AI Analysis: '{event_name}' appears to be legacy or over-engineered. Consider deprecation."

        return f" AI Analysis: '{event_name}' has low importance. Implement only if explicitly needed."

    async def analyze_domain(self, domain: str, events: List[Dict]) -> Dict:
        """Анализирует все события в домене"""

        logger.info(f" Analyzing domain: {domain}")

        analyses = []
        for event_data in events:
            analysis = await self.analyze_event(
                event_data['name'],
                event_data.get('publishers', []),
                event_data.get('subscribers', [])
            )
            analyses.append(analysis)

        # Агрегированная статистика по домену
        avg_importance = sum(a.importance_score for a in analyses) / len(analyses) if analyses else 0

        patterns = defaultdict(int)
        for a in analyses:
            patterns[a.usage_pattern] += 1

        return {
            'domain': domain,
            'total_events': len(analyses),
            'avg_importance': avg_importance,
            'patterns': dict(patterns),
            'analyses': analyses,
            'domain_health': self._calculate_domain_health(analyses)
        }

    def _calculate_domain_health(self, analyses: List[EventAnalysis]) -> str:
        """Оценка здоровья домена"""

        if not analyses:
            return 'unknown'

        # Процент critical/frequent событий
        active_events = sum(
            1 for a in analyses
            if a.usage_pattern in ['critical', 'frequent']
        )

        health_ratio = active_events / len(analyses)

        if health_ratio > 0.7:
            return 'healthy'
        elif health_ratio > 0.4:
            return 'moderate'
        else:
            return 'needs_attention'
