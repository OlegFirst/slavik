"""
Event Predictor - Предсказание будущих событий и gaps

Функции:
- Предсказание будущих gaps
- Прогноз необходимости событий
- Аномалии в event flow
- Упреждающие рекомендации
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class EventPrediction:
    """Предсказание о событии"""
    prediction_type: str  # 'future_gap', 'anomaly', 'opportunity'
    event_name: Optional[str]
    probability: float  # 0-1
    estimated_date: str
    reasoning: str
    recommended_action: str


class EventPredictor:
    """
    Предиктивная система для событий

    Возможности:
    - Предсказывает будущие gaps
    - Обнаруживает аномалии
    - Находит возможности для оптимизации
    """

    def __init__(self, learner=None):
        self.learner = learner
        self.prediction_history = []

    async def predict_future_gaps(
        self,
        current_gaps: List[Dict],
        historical_trend: List[Dict],
        days_ahead: int = 7
    ) -> List[EventPrediction]:
        """
        Предсказывает будущие gaps

        Args:
            current_gaps: Текущие gaps
            historical_trend: История gaps
            days_ahead: Горизонт предсказания

        Returns:
            List predictions
        """
        logger.info(f" Predicting gaps for next {days_ahead} days...")

        predictions = []

        # Анализ тренда
        if len(historical_trend) >= 7:
            # Вычисляем скорость роста gaps
            recent = historical_trend[-7:]
            gap_counts = [len(h.get('gaps', [])) for h in recent]

            if len(gap_counts) > 1:
                growth_rate = (gap_counts[-1] - gap_counts[0]) / len(gap_counts)

                if growth_rate > 0.5:  # Растёт быстро
                    predictions.append(EventPrediction(
                        prediction_type='future_gap',
                        event_name=None,
                        probability=0.75,
                        estimated_date=(datetime.utcnow() + timedelta(days=days_ahead)).isoformat(),
                        reasoning=f"Gap count growing at {growth_rate:.1f} per day",
                        recommended_action="Proactive gap fixing session planned"
                    ))

        # Предсказание конкретных типов gaps
        gap_types = {}
        for gap in current_gaps:
            gap_type = gap.get('gap_type', 'unknown')
            gap_types[gap_type] = gap_types.get(gap_type, 0) + 1

        # Самый частый тип gap вероятно продолжит появляться
        if gap_types:
            most_common_type = max(gap_types, key=gap_types.get)
            probability = min(gap_types[most_common_type] / sum(gap_types.values()) + 0.2, 0.95)

            predictions.append(EventPrediction(
                prediction_type='future_gap',
                event_name=f"New {most_common_type}",
                probability=probability,
                estimated_date=(datetime.utcnow() + timedelta(days=3)).isoformat(),
                reasoning=f"{most_common_type} gaps are most common ({gap_types[most_common_type]} currently)",
                recommended_action=f"Prepare templates for {most_common_type} fixes"
            ))

        self.prediction_history.extend(predictions)
        return predictions

    async def detect_anomalies(
        self,
        current_state: Dict,
        historical_baseline: List[Dict]
    ) -> List[EventPrediction]:
        """
        Обнаруживает аномалии в событиях

        Args:
            current_state: Текущее состояние
            historical_baseline: Исторический baseline

        Returns:
            List anomalies
        """
        logger.info(" Detecting anomalies...")

        anomalies = []

        if not historical_baseline or len(historical_baseline) < 7:
            return anomalies

        # Вычисляем средние и отклонения
        critical_gaps = [
            len([g for g in h.get('gaps', []) if g.get('severity') == 'critical'])
            for h in historical_baseline
        ]

        avg_critical = sum(critical_gaps) / len(critical_gaps)
        current_critical = len([
            g for g in current_state.get('gaps', [])
            if g.get('severity') == 'critical'
        ])

        # Проверка на спайк
        if current_critical > avg_critical * 2:
            anomalies.append(EventPrediction(
                prediction_type='anomaly',
                event_name=None,
                probability=0.9,
                estimated_date=datetime.utcnow().isoformat(),
                reasoning=f"Critical gaps spiked: {current_critical} (avg: {avg_critical:.1f})",
                recommended_action="Immediate investigation required"
            ))

        return anomalies

    async def find_opportunities(
        self,
        current_events: List[Dict],
        learner_patterns: Optional[List] = None
    ) -> List[EventPrediction]:
        """
        Находит возможности для оптимизации

        Args:
            current_events: Текущие события
            learner_patterns: Паттерны от learner

        Returns:
            List opportunities
        """
        logger.info(" Finding optimization opportunities...")

        opportunities = []

        # Находим часто используемые события без subscribers
        for event in current_events:
            publishers = event.get('publishers', [])
            subscribers = event.get('subscribers', [])

            if len(publishers) >= 2 and len(subscribers) == 0:
                opportunities.append(EventPrediction(
                    prediction_type='opportunity',
                    event_name=event['name'],
                    probability=0.7,
                    estimated_date=datetime.utcnow().isoformat(),
                    reasoning=f"Event published by {len(publishers)} services but no subscribers",
                    recommended_action="Add centralized subscriber for analytics/audit"
                ))

        return opportunities

    async def get_prediction_accuracy(self) -> Dict:
        """Возвращает точность предсказаний"""

        if not self.prediction_history:
            return {'accuracy': 0, 'total_predictions': 0}

        # TODO: Сравнить предсказания с реальностью
        # Требует хранения фактических результатов

        return {
            'total_predictions': len(self.prediction_history),
            'accuracy': 0.75,  # Placeholder
            'by_type': {
                'future_gap': 0.7,
                'anomaly': 0.85,
                'opportunity': 0.6
            }
        }
