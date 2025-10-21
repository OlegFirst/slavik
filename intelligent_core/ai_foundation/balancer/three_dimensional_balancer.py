"""
Three-Dimensional Balancer - Баланс между тремя измерениями

ФИЛОСОФИЯ:
Система постоянно стремится к балансу между:

1️⃣ РАЦИОНАЛЬНОЕ (Rational) - Evidence-Based
   - Доказательства из данных
   - Что БЫЛО эффективно в прошлом
   - Confidence metrics

2️⃣ ИНТУИТИВНОЕ (Intuitive) - Pattern-Based
   - Распознавание паттернов
   - Предсказание ЧТО БУДЕТ
   - "Чувство" системы

3️⃣ ПРАГМАТИЧНОЕ (Pragmatic) - ROI-Driven
   - Максимизация возврата
   - Что ВЫГОДНО делать
   - Бизнес-метрики

КЛЮЧЕВОЙ ПРИНЦИП:
Баланс между тремя измерениями НИКОГДА не идеален!
Стремление к балансу = движущая сила системы.

Иногда нужно больше рациональности (когда есть данные)
Иногда нужно больше интуиции (когда данных мало)
Иногда нужно больше прагматики (когда ресурсы ограничены)

Система САМА адаптирует веса между измерениями!
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics

logger = logging.getLogger(__name__)


class DecisionDimension(Enum):
    """Измерение принятия решения"""
    RATIONAL = "rational"      # Рациональное (данные)
    INTUITIVE = "intuitive"    # Интуитивное (паттерны)
    PRAGMATIC = "pragmatic"    # Прагматичное (ROI)


@dataclass
class DimensionWeight:
    """Вес измерения в решении"""
    rational_weight: float    # 0-1
    intuitive_weight: float   # 0-1
    pragmatic_weight: float   # 0-1

    def normalize(self):
        """Нормализовать к сумме 1.0"""
        total = self.rational_weight + self.intuitive_weight + self.pragmatic_weight
        if total == 0:
            # Default равномерное распределение
            self.rational_weight = 0.33
            self.intuitive_weight = 0.33
            self.pragmatic_weight = 0.34
        else:
            self.rational_weight /= total
            self.intuitive_weight /= total
            self.pragmatic_weight /= total

    def get_balance_score(self) -> float:
        """
        Оценить сбалансированность весов

        Идеальный баланс = 0.33/0.33/0.33 → score 1.0
        Перекос = один вес >> других → score < 0.5
        """
        # Стандартное отклонение от идеального (0.33)
        weights = [self.rational_weight, self.intuitive_weight, self.pragmatic_weight]
        deviations = [(w - 0.33) ** 2 for w in weights]
        variance = sum(deviations) / 3

        # Конвертировать variance в score (0-1)
        # variance=0 → score=1, variance=0.11 (max) → score=0
        balance_score = 1.0 - min(variance / 0.11, 1.0)

        return balance_score


@dataclass
class ThreeDimensionalDecision:
    """Решение с учетом трех измерений"""
    module_name: str

    # Входы от каждого измерения
    rational_recommendation: Dict[str, Any]
    intuitive_recommendation: Dict[str, Any]
    pragmatic_recommendation: Dict[str, Any]

    # Веса
    weights: DimensionWeight

    # Итоговое решение
    final_decision: Dict[str, Any]

    # Мета
    balance_score: float
    reasoning: str
    timestamp: float


class ThreeDimensionalBalancer:
    """
    Балансировщик трех измерений

    Интегрирует:
    - SystemBalancer (базовая балансировка)
    - ImpactEvidenceTracker (рациональность)
    - PredictiveROIOptimizer (интуиция + прагматика)

    Адаптивно находит баланс между ними
    """

    def __init__(
        self,
        impact_tracker=None,
        roi_optimizer=None,
        initial_weights: Optional[DimensionWeight] = None
    ):
        """
        Initialize Three-Dimensional Balancer

        Args:
            impact_tracker: ImpactEvidenceTracker (рациональность)
            roi_optimizer: PredictiveROIOptimizer (интуиция + прагматика)
            initial_weights: Начальные веса (по умолчанию равномерно)
        """
        self.impact_tracker = impact_tracker
        self.roi_optimizer = roi_optimizer

        # Текущие веса (адаптируются со временем)
        if initial_weights:
            self.current_weights = initial_weights
        else:
            self.current_weights = DimensionWeight(
                rational_weight=0.33,
                intuitive_weight=0.33,
                pragmatic_weight=0.34
            )

        # История решений
        self.decision_history: List[ThreeDimensionalDecision] = []

        # Статистика
        self.stats = {
            'total_decisions': 0,
            'rational_dominated': 0,
            'intuitive_dominated': 0,
            'pragmatic_dominated': 0,
            'balanced_decisions': 0,
            'avg_balance_score': 0.0
        }

        logger.info(
            f"️  Three-Dimensional Balancer initialized "
            f"(weights: R={self.current_weights.rational_weight:.2f}, "
            f"I={self.current_weights.intuitive_weight:.2f}, "
            f"P={self.current_weights.pragmatic_weight:.2f})"
        )

    def make_balanced_decision(
        self,
        module_name: str,
        context: Dict[str, Any]
    ) -> ThreeDimensionalDecision:
        """
        Принять решение с учетом ВСЕХ трех измерений

        Args:
            module_name: Имя модуля
            context: Контекст для решения

        Returns:
            ThreeDimensionalDecision with balanced recommendation
        """
        self.stats['total_decisions'] += 1

        # === 1. РАЦИОНАЛЬНОЕ ИЗМЕРЕНИЕ ===
        rational_rec = self._get_rational_recommendation(module_name, context)

        # === 2. ИНТУИТИВНОЕ ИЗМЕРЕНИЕ ===
        intuitive_rec = self._get_intuitive_recommendation(module_name, context)

        # === 3. ПРАГМАТИЧНОЕ ИЗМЕРЕНИЕ ===
        pragmatic_rec = self._get_pragmatic_recommendation(module_name, context)

        # === 4. АДАПТИРОВАТЬ ВЕСА ===
        adapted_weights = self._adapt_weights(
            rational_rec,
            intuitive_rec,
            pragmatic_rec,
            context
        )

        # === 5. КОМБИНИРОВАТЬ РЕКОМЕНДАЦИИ ===
        final_decision = self._combine_recommendations(
            rational_rec,
            intuitive_rec,
            pragmatic_rec,
            adapted_weights
        )

        # === 6. ОЦЕНИТЬ БАЛАНС ===
        balance_score = adapted_weights.get_balance_score()

        # Обновить статистику
        if balance_score > 0.8:
            self.stats['balanced_decisions'] += 1
        elif adapted_weights.rational_weight > 0.5:
            self.stats['rational_dominated'] += 1
        elif adapted_weights.intuitive_weight > 0.5:
            self.stats['intuitive_dominated'] += 1
        elif adapted_weights.pragmatic_weight > 0.5:
            self.stats['pragmatic_dominated'] += 1

        # Reasoning
        reasoning = self._generate_decision_reasoning(
            rational_rec,
            intuitive_rec,
            pragmatic_rec,
            adapted_weights,
            final_decision
        )

        decision = ThreeDimensionalDecision(
            module_name=module_name,
            rational_recommendation=rational_rec,
            intuitive_recommendation=intuitive_rec,
            pragmatic_recommendation=pragmatic_rec,
            weights=adapted_weights,
            final_decision=final_decision,
            balance_score=balance_score,
            reasoning=reasoning,
            timestamp=time.time()
        )

        self.decision_history.append(decision)
        self._update_avg_balance()

        logger.info(
            f"️  3D Decision for {module_name}: "
            f"Balance={balance_score:.2f}, "
            f"Weights(R/I/P)={adapted_weights.rational_weight:.2f}/"
            f"{adapted_weights.intuitive_weight:.2f}/"
            f"{adapted_weights.pragmatic_weight:.2f}"
        )

        return decision

    def _get_rational_recommendation(
        self,
        module_name: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Получить рациональную рекомендацию (на основе данных)

        Использует ImpactEvidenceTracker
        """
        if not self.impact_tracker:
            return {
                'confidence': 0.0,
                'recommendation': 'insufficient_data',
                'reasoning': 'No ImpactTracker available'
            }

        # Получить инсайты из истории
        insights = self.impact_tracker.get_learning_insights()

        if insights.get('insufficient_data'):
            return {
                'confidence': 0.2,
                'recommendation': 'gather_more_data',
                'reasoning': 'Insufficient historical data for rational decision'
            }

        # Рекомендация на основе success rates
        reward_success = insights.get('reward_success_rate', 0)
        penalty_success = insights.get('penalty_success_rate', 0)

        current_health = context.get('current_health', 50)

        if current_health < 50:
            # Нужна помощь → penalty
            recommendation = 'allocate_resources'
            confidence = penalty_success / 100.0
        else:
            # Здоровье OK → reward
            recommendation = 'reduce_allocation'
            confidence = reward_success / 100.0

        return {
            'confidence': confidence,
            'recommendation': recommendation,
            'reasoning': f'Based on {insights["total_interventions"]} historical interventions'
        }

    def _get_intuitive_recommendation(
        self,
        module_name: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Получить интуитивную рекомендацию (на основе паттернов)

        Использует PredictiveROIOptimizer для предсказания
        """
        if not self.roi_optimizer:
            return {
                'confidence': 0.0,
                'recommendation': 'unknown',
                'reasoning': 'No predictor available'
            }

        # Предсказать тренд
        trend = self.roi_optimizer.predict_health_trend(module_name)

        if not trend:
            return {
                'confidence': 0.3,
                'recommendation': 'monitor',
                'reasoning': 'Insufficient history for prediction'
            }

        # Рекомендация на основе тренда
        if trend.predicted_health_5min < 50:
            # Предсказываем дисбаланс → превентивные меры
            recommendation = 'preventive_allocation'
            confidence = trend.confidence
            reasoning = f'Predicts health drop to {trend.predicted_health_5min:.1f} in 5min'
        elif trend.trend_velocity < -5:
            # Деградация → нужна помощь
            recommendation = 'allocate_resources'
            confidence = trend.confidence
            reasoning = f'Negative trend: {trend.trend_velocity:.2f} health/min'
        elif trend.trend_velocity > 5:
            # Улучшение → можно снизить
            recommendation = 'reduce_allocation'
            confidence = trend.confidence
            reasoning = f'Positive trend: {trend.trend_velocity:.2f} health/min'
        else:
            # Стабильно
            recommendation = 'maintain'
            confidence = trend.confidence
            reasoning = 'Trend is stable'

        return {
            'confidence': confidence,
            'recommendation': recommendation,
            'reasoning': reasoning
        }

    def _get_pragmatic_recommendation(
        self,
        module_name: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Получить прагматичную рекомендацию (на основе ROI)

        Использует PredictiveROIOptimizer для ROI калькуляции
        """
        if not self.roi_optimizer:
            return {
                'confidence': 0.0,
                'recommendation': 'unknown',
                'reasoning': 'No ROI optimizer available'
            }

        current_health = context.get('current_health', 50)

        # Рассчитать ROI для разных вариантов
        allocate_roi = self.roi_optimizer.calculate_roi_projection(
            module_name,
            'allocate',
            allocated_cpu=40,
            allocated_memory=512,
            predicted_health_improvement=30
        )

        reduce_roi = self.roi_optimizer.calculate_roi_projection(
            module_name,
            'reduce',
            allocated_cpu=20,
            allocated_memory=256,
            predicted_health_improvement=-10  # Может ухудшиться
        )

        # Выбрать вариант с лучшим ROI
        if allocate_roi.worth_doing and allocate_roi.risk_adjusted_roi > reduce_roi.risk_adjusted_roi:
            return {
                'confidence': 0.8,
                'recommendation': 'allocate_resources',
                'reasoning': allocate_roi.reasoning,
                'roi': allocate_roi.risk_adjusted_roi
            }
        elif reduce_roi.risk_adjusted_roi > 0:
            return {
                'confidence': 0.8,
                'recommendation': 'reduce_allocation',
                'reasoning': reduce_roi.reasoning,
                'roi': reduce_roi.risk_adjusted_roi
            }
        else:
            return {
                'confidence': 0.5,
                'recommendation': 'maintain',
                'reasoning': 'No intervention has positive ROI',
                'roi': 0.0
            }

    def _adapt_weights(
        self,
        rational_rec: Dict[str, Any],
        intuitive_rec: Dict[str, Any],
        pragmatic_rec: Dict[str, Any],
        context: Dict[str, Any]
    ) -> DimensionWeight:
        """
        Адаптировать веса на основе контекста

        КЛЮЧЕВАЯ ЛОГИКА:
        - Есть много данных → больше рациональности
        - Данных мало → больше интуиции
        - Ресурсы ограничены → больше прагматики
        - Кризис → баланс всех трех
        """
        # Начать с текущих весов
        weights = DimensionWeight(
            rational_weight=self.current_weights.rational_weight,
            intuitive_weight=self.current_weights.intuitive_weight,
            pragmatic_weight=self.current_weights.pragmatic_weight
        )

        # Адаптация #1: confidence каждого измерения
        rational_conf = rational_rec.get('confidence', 0.5)
        intuitive_conf = intuitive_rec.get('confidence', 0.5)
        pragmatic_conf = pragmatic_rec.get('confidence', 0.5)

        # Больше веса измерению с высокой уверенностью
        weights.rational_weight *= (0.5 + rational_conf)
        weights.intuitive_weight *= (0.5 + intuitive_conf)
        weights.pragmatic_weight *= (0.5 + pragmatic_conf)

        # Адаптация #2: доступность ресурсов
        available_resources = context.get('available_cpu', 100)
        if available_resources < 30:
            # Ресурсы ограничены → больше прагматики (ROI важнее!)
            weights.pragmatic_weight *= 1.5
        elif available_resources > 70:
            # Ресурсов много → можно рисковать с интуицией
            weights.intuitive_weight *= 1.3

        # Адаптация #3: уровень кризиса
        current_health = context.get('current_health', 50)
        if current_health < 30:
            # КРИЗИС → нужен баланс ВСЕХ трех (не полагаться на одно)
            # Выравниваем веса к 0.33/0.33/0.33
            weights.rational_weight = (weights.rational_weight + 0.33) / 2
            weights.intuitive_weight = (weights.intuitive_weight + 0.33) / 2
            weights.pragmatic_weight = (weights.pragmatic_weight + 0.33) / 2

        # Нормализовать
        weights.normalize()

        # Обновить текущие веса (с сглаживанием)
        alpha = 0.3  # Коэффициент обучения
        self.current_weights.rational_weight = (
            (1 - alpha) * self.current_weights.rational_weight +
            alpha * weights.rational_weight
        )
        self.current_weights.intuitive_weight = (
            (1 - alpha) * self.current_weights.intuitive_weight +
            alpha * weights.intuitive_weight
        )
        self.current_weights.pragmatic_weight = (
            (1 - alpha) * self.current_weights.pragmatic_weight +
            alpha * weights.pragmatic_weight
        )
        self.current_weights.normalize()

        return weights

    def _combine_recommendations(
        self,
        rational_rec: Dict[str, Any],
        intuitive_rec: Dict[str, Any],
        pragmatic_rec: Dict[str, Any],
        weights: DimensionWeight
    ) -> Dict[str, Any]:
        """
        Комбинировать рекомендации с учетом весов

        Взвешенное голосование
        """
        # Подсчитать "голоса" за каждое действие
        votes = {
            'allocate_resources': 0.0,
            'reduce_allocation': 0.0,
            'maintain': 0.0,
            'preventive_allocation': 0.0
        }

        # Голос рационального
        rational_action = rational_rec.get('recommendation', 'maintain')
        if rational_action in votes:
            votes[rational_action] += weights.rational_weight

        # Голос интуитивного
        intuitive_action = intuitive_rec.get('recommendation', 'maintain')
        if intuitive_action in votes:
            votes[intuitive_action] += weights.intuitive_weight

        # Голос прагматичного
        pragmatic_action = pragmatic_rec.get('recommendation', 'maintain')
        if pragmatic_action in votes:
            votes[pragmatic_action] += weights.pragmatic_weight

        # Выбрать действие с наибольшим весом
        final_action = max(votes, key=votes.get)
        final_confidence = votes[final_action]

        return {
            'action': final_action,
            'confidence': final_confidence,
            'votes': votes
        }

    def _generate_decision_reasoning(
        self,
        rational_rec: Dict[str, Any],
        intuitive_rec: Dict[str, Any],
        pragmatic_rec: Dict[str, Any],
        weights: DimensionWeight,
        final_decision: Dict[str, Any]
    ) -> str:
        """Генерировать обоснование решения"""
        reasoning = f"3D DECISION: {final_decision['action']}\n"
        reasoning += f"Balance: R={weights.rational_weight:.0%} I={weights.intuitive_weight:.0%} P={weights.pragmatic_weight:.0%}\n"
        reasoning += f"- Rational: {rational_rec['recommendation']} ({rational_rec['reasoning']})\n"
        reasoning += f"- Intuitive: {intuitive_rec['recommendation']} ({intuitive_rec['reasoning']})\n"
        reasoning += f"- Pragmatic: {pragmatic_rec['recommendation']} ({pragmatic_rec['reasoning']})\n"
        reasoning += f"Final confidence: {final_decision['confidence']:.0%}"

        return reasoning

    def _update_avg_balance(self):
        """Обновить среднюю сбалансированность"""
        if not self.decision_history:
            return

        balance_scores = [d.balance_score for d in self.decision_history]
        self.stats['avg_balance_score'] = statistics.mean(balance_scores)

    def get_stats(self) -> Dict[str, Any]:
        """Статистика балансировщика"""
        return {
            **self.stats,
            'current_weights': {
                'rational': self.current_weights.rational_weight,
                'intuitive': self.current_weights.intuitive_weight,
                'pragmatic': self.current_weights.pragmatic_weight
            },
            'current_balance': self.current_weights.get_balance_score()
        }


def create_three_dimensional_balancer(
    impact_tracker=None,
    roi_optimizer=None
) -> ThreeDimensionalBalancer:
    """
    Factory function для создания Three-Dimensional Balancer

    Args:
        impact_tracker: ImpactEvidenceTracker instance
        roi_optimizer: PredictiveROIOptimizer instance

    Returns:
        ThreeDimensionalBalancer instance
    """
    return ThreeDimensionalBalancer(
        impact_tracker=impact_tracker,
        roi_optimizer=roi_optimizer
    )
