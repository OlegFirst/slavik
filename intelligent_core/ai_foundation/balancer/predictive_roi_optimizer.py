"""
Predictive ROI Optimizer - Рационально-Интуитивно-Прагматичная система

Три измерения принятия решений:

1️⃣ РАЦИОНАЛЬНОЕ (Evidence-Based):
   - Доказательства из истории
   - Данные о влиянии
   - Confidence metrics

2️⃣ ИНТУИТИВНОЕ (Pattern-Based):
   - Распознавание паттернов
   - Предсказание будущего
   - "Чувство" системы

3️⃣ ПРАГМАТИЧНОЕ (ROI-Driven):
   - Максимизация возврата инвестиций
   - Оптимальное распределение ресурсов
   - Бизнес-метрики

Философия:
- Предсказываем дисбаланс ЗАРАНЕЕ (не реагируем, а предотвращаем)
- Оцениваем ROI ДО вмешательства (стоит ли вообще?)
- Оптимизируем не баланс, а ROI (баланс за счет минимальных ресурсов)
"""

import logging
import time
import statistics
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math

logger = logging.getLogger(__name__)


class PredictionHorizon(Enum):
    """Горизонт предсказания"""
    SHORT = "short"      # 1-5 минут
    MEDIUM = "medium"    # 5-30 минут
    LONG = "long"        # 30+ минут


@dataclass
class HealthTrend:
    """Тренд здоровья модуля"""
    module_name: str
    current_health: float
    trend_direction: float  # -1 to +1 (negative=degrading, positive=improving)
    trend_velocity: float   # Скорость изменения (health_per_minute)
    predicted_health_5min: float
    predicted_health_30min: float
    confidence: float  # 0-1


@dataclass
class PredictedImbalance:
    """Предсказанный дисбаланс"""
    module_name: str
    when_timestamp: float  # Когда случится
    minutes_ahead: float   # Через сколько минут
    predicted_health: float
    severity: float  # 0-1
    probability: float  # 0-1 (вероятность что случится)
    recommended_action: str
    estimated_cost: Dict[str, float]  # Стоимость предотвращения


@dataclass
class ROIProjection:
    """Проекция ROI для решения"""
    intervention_id: str
    module_name: str

    # Затраты (costs)
    cpu_cost: float
    memory_cost: float
    time_cost: float
    total_cost: float

    # Выгоды (benefits)
    expected_health_improvement: float
    expected_downtime_reduction: float  # minutes
    expected_error_reduction: float     # %
    total_benefit: float

    # ROI
    projected_roi: float  # benefit / cost
    breakeven_time: float  # Через сколько окупится
    risk_adjusted_roi: float  # ROI с учетом рисков

    # Прагматика
    worth_doing: bool  # Стоит ли вообще делать?
    priority_score: float  # Приоритет с учетом ROI
    reasoning: str


@dataclass
class OptimalIntervention:
    """Оптимальное вмешательство (лучший ROI)"""
    module_name: str
    intervention_type: str
    timing: str  # now/in_5min/in_30min
    allocated_resources: Dict[str, float]
    projected_roi: float
    reasoning: str


class PredictiveROIOptimizer:
    """
    Рационально-Интуитивно-Прагматичный оптимизатор

    Комбинирует:
    - Рациональность (данные из ImpactEvidenceTracker)
    - Интуицию (предсказание паттернов)
    - Прагматичность (максимизация ROI)
    """

    def __init__(
        self,
        impact_tracker=None,
        min_roi_threshold: float = 1.0,
        prediction_window_minutes: int = 30
    ):
        """
        Initialize Predictive ROI Optimizer

        Args:
            impact_tracker: ImpactEvidenceTracker для обучения
            min_roi_threshold: Минимальный ROI для действия (1.0 = break-even)
            prediction_window_minutes: Горизонт предсказания
        """
        self.impact_tracker = impact_tracker
        self.min_roi = min_roi_threshold
        self.prediction_window = prediction_window_minutes

        # История для предсказаний
        self.health_history: Dict[str, List[Tuple[float, float]]] = {}  # module -> [(timestamp, health)]

        # Выученные паттерны
        self.learned_patterns: Dict[str, Any] = {}

        # Статистика
        self.stats = {
            'predictions_made': 0,
            'predictions_accurate': 0,
            'preventive_actions': 0,
            'roi_optimizations': 0,
            'avoided_crises': 0
        }

        logger.info(f" Predictive ROI Optimizer initialized (min ROI: {min_roi_threshold})")

    def record_health_snapshot(self, module_name: str, health: float):
        """
        Записать snapshot здоровья для предсказаний

        Args:
            module_name: Имя модуля
            health: Текущее здоровье (0-100)
        """
        if module_name not in self.health_history:
            self.health_history[module_name] = []

        self.health_history[module_name].append((time.time(), health))

        # Хранить только последние 100 snapshots
        if len(self.health_history[module_name]) > 100:
            self.health_history[module_name] = self.health_history[module_name][-100:]

    def predict_health_trend(
        self,
        module_name: str,
        horizon: PredictionHorizon = PredictionHorizon.MEDIUM
    ) -> Optional[HealthTrend]:
        """
        Предсказать тренд здоровья модуля (ИНТУИЦИЯ)

        Args:
            module_name: Имя модуля
            horizon: Горизонт предсказания

        Returns:
            HealthTrend with predictions
        """
        history = self.health_history.get(module_name)
        if not history or len(history) < 5:
            return None

        # Текущее здоровье
        current_health = history[-1][1]

        # Рассчитать тренд (линейная регрессия)
        trend_direction, trend_velocity = self._calculate_trend(history)

        # Предсказать будущее здоровье
        predicted_5min = current_health + (trend_velocity * 5)
        predicted_30min = current_health + (trend_velocity * 30)

        # Ограничить в пределах [0, 100]
        predicted_5min = max(0, min(100, predicted_5min))
        predicted_30min = max(0, min(100, predicted_30min))

        # Confidence на основе стабильности тренда
        confidence = self._calculate_trend_confidence(history)

        trend = HealthTrend(
            module_name=module_name,
            current_health=current_health,
            trend_direction=trend_direction,
            trend_velocity=trend_velocity,
            predicted_health_5min=predicted_5min,
            predicted_health_30min=predicted_30min,
            confidence=confidence
        )

        logger.debug(
            f" Trend predicted for {module_name}: "
            f"velocity={trend_velocity:.2f}/min, "
            f"5min={predicted_5min:.1f}, 30min={predicted_30min:.1f}"
        )

        return trend

    def predict_future_imbalances(
        self,
        modules: List[str],
        horizon_minutes: int = 30
    ) -> List[PredictedImbalance]:
        """
        Предсказать будущие дисбалансы (ИНТУИЦИЯ)

        Args:
            modules: Список модулей для анализа
            horizon_minutes: Горизонт предсказания

        Returns:
            List of predicted imbalances
        """
        self.stats['predictions_made'] += 1

        predictions = []

        for module_name in modules:
            trend = self.predict_health_trend(module_name)
            if not trend:
                continue

            # Проверить будет ли дисбаланс
            future_health = (
                trend.predicted_health_5min if horizon_minutes <= 5
                else trend.predicted_health_30min
            )

            if future_health < 50:  # Порог дисбаланса
                # Вычислить когда именно случится
                if trend.trend_velocity < 0:
                    # Деградация
                    minutes_to_threshold = (trend.current_health - 50) / abs(trend.trend_velocity)
                    minutes_ahead = max(0, minutes_to_threshold)
                else:
                    # Улучшение (не будет дисбаланса)
                    continue

                # Severity
                severity = (50 - future_health) / 50  # 0-1

                # Probability (уверенность тренда)
                probability = trend.confidence

                # Рекомендуемое действие
                if severity > 0.7:
                    recommended_action = "emergency_stabilization"
                elif severity > 0.4:
                    recommended_action = "allocate_resources"
                else:
                    recommended_action = "monitor_closely"

                # Оценить стоимость предотвращения
                estimated_cost = self._estimate_prevention_cost(severity)

                prediction = PredictedImbalance(
                    module_name=module_name,
                    when_timestamp=time.time() + (minutes_ahead * 60),
                    minutes_ahead=minutes_ahead,
                    predicted_health=future_health,
                    severity=severity,
                    probability=probability,
                    recommended_action=recommended_action,
                    estimated_cost=estimated_cost
                )

                predictions.append(prediction)

                logger.warning(
                    f"️  PREDICTED imbalance: {module_name} in {minutes_ahead:.1f}min "
                    f"(health will drop to {future_health:.1f})"
                )

        return predictions

    def calculate_roi_projection(
        self,
        module_name: str,
        intervention_type: str,
        allocated_cpu: float,
        allocated_memory: float,
        predicted_health_improvement: float
    ) -> ROIProjection:
        """
        Рассчитать проекцию ROI для вмешательства (ПРАГМАТИКА)

        Args:
            module_name: Имя модуля
            intervention_type: Тип вмешательства
            allocated_cpu: CPU %
            allocated_memory: Memory MB
            predicted_health_improvement: Ожидаемое улучшение здоровья

        Returns:
            ROIProjection with detailed cost/benefit analysis
        """
        self.stats['roi_optimizations'] += 1

        # === ЗАТРАТЫ (COSTS) ===

        # CPU cost (нормализованная стоимость)
        cpu_cost = allocated_cpu * 0.5  # 1 CPU% = 0.5 cost units

        # Memory cost
        memory_cost = allocated_memory * 0.0001  # 1 MB = 0.0001 cost units

        # Time cost (opportunity cost)
        time_cost = 1.0  # Базовая стоимость времени

        total_cost = cpu_cost + memory_cost + time_cost

        # === ВЫГОДЫ (BENEFITS) ===

        # Health improvement benefit
        health_benefit = predicted_health_improvement * 1.0  # 1 health point = 1 benefit unit

        # Downtime reduction (если здоровье плохое → простои)
        expected_downtime_reduction = self._calculate_downtime_benefit(
            module_name,
            predicted_health_improvement
        )

        # Error reduction
        expected_error_reduction = predicted_health_improvement * 0.1  # Примерная корреляция

        total_benefit = (
            health_benefit +
            (expected_downtime_reduction * 10) +  # Простои очень дорогие!
            (expected_error_reduction * 5)
        )

        # === ROI ===

        if total_cost == 0:
            projected_roi = 0
        else:
            projected_roi = (total_benefit - total_cost) / total_cost

        # Breakeven time (через сколько окупится)
        if predicted_health_improvement > 0:
            # Примерная оценка: улучшение здоровья на 1% окупается за 1 минуту
            breakeven_time = total_cost / predicted_health_improvement
        else:
            breakeven_time = float('inf')

        # Risk-adjusted ROI (с учетом вероятности успеха)
        success_probability = self._estimate_success_probability(
            module_name,
            intervention_type
        )
        risk_adjusted_roi = projected_roi * success_probability

        # ПРАГМАТИКА: стоит ли делать?
        worth_doing = (
            risk_adjusted_roi >= self.min_roi and
            total_benefit > total_cost
        )

        # Priority score с учетом ROI
        priority_score = risk_adjusted_roi * (1 + predicted_health_improvement / 100)

        # Reasoning
        reasoning = self._generate_roi_reasoning(
            projected_roi,
            risk_adjusted_roi,
            total_cost,
            total_benefit,
            worth_doing
        )

        projection = ROIProjection(
            intervention_id=f"roi_{module_name}_{int(time.time())}",
            module_name=module_name,
            cpu_cost=cpu_cost,
            memory_cost=memory_cost,
            time_cost=time_cost,
            total_cost=total_cost,
            expected_health_improvement=predicted_health_improvement,
            expected_downtime_reduction=expected_downtime_reduction,
            expected_error_reduction=expected_error_reduction,
            total_benefit=total_benefit,
            projected_roi=projected_roi,
            breakeven_time=breakeven_time,
            risk_adjusted_roi=risk_adjusted_roi,
            worth_doing=worth_doing,
            priority_score=priority_score,
            reasoning=reasoning
        )

        logger.info(
            f" ROI projected for {module_name}: "
            f"ROI={projected_roi:.2f}, Risk-adjusted={risk_adjusted_roi:.2f}, "
            f"Worth doing: {worth_doing}"
        )

        return projection

    def optimize_interventions(
        self,
        predicted_imbalances: List[PredictedImbalance],
        available_resources: Dict[str, float]
    ) -> List[OptimalIntervention]:
        """
        Оптимизировать вмешательства для максимального ROI (ПРАГМАТИКА)

        Args:
            predicted_imbalances: Предсказанные дисбалансы
            available_resources: Доступные ресурсы

        Returns:
            List of optimal interventions sorted by ROI
        """
        interventions = []

        for imbalance in predicted_imbalances:
            # Рассчитать несколько вариантов вмешательства
            options = []

            # Option 1: Минимальные ресурсы (консервативный)
            min_cpu = 20
            min_memory = 256
            min_improvement = imbalance.severity * 30

            roi_min = self.calculate_roi_projection(
                imbalance.module_name,
                "conservative",
                min_cpu,
                min_memory,
                min_improvement
            )
            options.append(("conservative", min_cpu, min_memory, roi_min))

            # Option 2: Средние ресурсы (сбалансированный)
            med_cpu = 40
            med_memory = 512
            med_improvement = imbalance.severity * 50

            roi_med = self.calculate_roi_projection(
                imbalance.module_name,
                "balanced",
                med_cpu,
                med_memory,
                med_improvement
            )
            options.append(("balanced", med_cpu, med_memory, roi_med))

            # Option 3: Максимальные ресурсы (агрессивный)
            max_cpu = 60
            max_memory = 1024
            max_improvement = imbalance.severity * 70

            roi_max = self.calculate_roi_projection(
                imbalance.module_name,
                "aggressive",
                max_cpu,
                max_memory,
                max_improvement
            )
            options.append(("aggressive", max_cpu, max_memory, roi_max))

            # Выбрать вариант с лучшим risk-adjusted ROI
            best_option = max(options, key=lambda x: x[3].risk_adjusted_roi)
            strategy, cpu, memory, roi_proj = best_option

            # Проверить доступность ресурсов
            if (cpu <= available_resources.get('cpu_percent', 100) and
                memory <= available_resources.get('memory_mb', 2048)):

                # Определить timing
                if imbalance.minutes_ahead < 5:
                    timing = "now"
                elif imbalance.minutes_ahead < 15:
                    timing = "in_5min"
                else:
                    timing = "in_30min"

                intervention = OptimalIntervention(
                    module_name=imbalance.module_name,
                    intervention_type=strategy,
                    timing=timing,
                    allocated_resources={
                        'cpu': cpu,
                        'memory': memory
                    },
                    projected_roi=roi_proj.risk_adjusted_roi,
                    reasoning=roi_proj.reasoning
                )

                interventions.append(intervention)

        # Сортировать по ROI (лучшие первыми)
        interventions.sort(key=lambda x: x.projected_roi, reverse=True)

        logger.info(f" Optimized {len(interventions)} interventions by ROI")

        return interventions

    def _calculate_trend(
        self,
        history: List[Tuple[float, float]]
    ) -> Tuple[float, float]:
        """
        Рассчитать тренд (direction, velocity)

        Returns:
            (direction: -1 to +1, velocity: health_per_minute)
        """
        if len(history) < 2:
            return 0.0, 0.0

        # Взять последние 10 точек для тренда
        recent = history[-10:]

        times = [t for t, h in recent]
        healths = [h for t, h in recent]

        # Линейная регрессия
        n = len(recent)
        x_mean = statistics.mean(times)
        y_mean = statistics.mean(healths)

        numerator = sum((times[i] - x_mean) * (healths[i] - y_mean) for i in range(n))
        denominator = sum((times[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0, 0.0

        slope = numerator / denominator  # health per second

        # Конвертировать в health per minute
        velocity = slope * 60

        # Direction нормализованный к [-1, 1]
        direction = max(-1, min(1, velocity / 10))  # 10 health/min = полный тренд

        return direction, velocity

    def _calculate_trend_confidence(
        self,
        history: List[Tuple[float, float]]
    ) -> float:
        """
        Рассчитать уверенность в тренде (стабильность)

        Returns:
            0-1
        """
        if len(history) < 5:
            return 0.3

        healths = [h for t, h in history[-10:]]

        # Стандартное отклонение (чем меньше → стабильнее → выше confidence)
        std_dev = statistics.stdev(healths) if len(healths) > 1 else 0

        # Нормализовать: std_dev = 0 → confidence = 1.0, std_dev = 20 → confidence = 0.5
        confidence = 1.0 - min(std_dev / 40, 0.5)

        return confidence

    def _estimate_prevention_cost(self, severity: float) -> Dict[str, float]:
        """Оценить стоимость предотвращения дисбаланса"""
        base_cpu = 20 + (severity * 40)
        base_memory = 256 + (severity * 768)

        return {
            'cpu_percent': base_cpu,
            'memory_mb': base_memory,
            'time_seconds': 300
        }

    def _calculate_downtime_benefit(
        self,
        module_name: str,
        health_improvement: float
    ) -> float:
        """
        Рассчитать выгоду от сокращения простоев

        Примерная корреляция: +10 health → -1 minute downtime
        """
        downtime_reduction_minutes = health_improvement / 10
        return downtime_reduction_minutes

    def _estimate_success_probability(
        self,
        module_name: str,
        intervention_type: str
    ) -> float:
        """
        Оценить вероятность успеха на основе истории

        Использует данные из ImpactEvidenceTracker
        """
        if not self.impact_tracker:
            return 0.7  # Default

        insights = self.impact_tracker.get_learning_insights()

        if insights.get('insufficient_data'):
            return 0.7

        # Вероятность на основе success rate
        if intervention_type in ["conservative", "balanced"]:
            success_rate = insights.get('penalty_success_rate', 70)
        else:
            success_rate = insights.get('reward_success_rate', 70)

        return success_rate / 100.0

    def _generate_roi_reasoning(
        self,
        roi: float,
        risk_adjusted_roi: float,
        cost: float,
        benefit: float,
        worth_doing: bool
    ) -> str:
        """Генерировать обоснование ROI"""
        if worth_doing:
            return (
                f" HIGH ROI: Invest {cost:.1f} units → gain {benefit:.1f} units. "
                f"ROI={roi:.2f}, Risk-adjusted={risk_adjusted_roi:.2f}. RECOMMENDED."
            )
        else:
            return (
                f" LOW ROI: Invest {cost:.1f} → gain {benefit:.1f}. "
                f"ROI={roi:.2f} below threshold {self.min_roi}. NOT RECOMMENDED."
            )

    def get_stats(self) -> Dict[str, Any]:
        """Статистика оптимизатора"""
        return {
            **self.stats,
            'accuracy_rate': (
                self.stats['predictions_accurate'] / self.stats['predictions_made'] * 100
                if self.stats['predictions_made'] > 0 else 0
            )
        }


def create_predictive_roi_optimizer(
    impact_tracker=None,
    min_roi: float = 1.0
) -> PredictiveROIOptimizer:
    """
    Factory function для создания Predictive ROI Optimizer

    Args:
        impact_tracker: ImpactEvidenceTracker instance
        min_roi: Minimum ROI threshold

    Returns:
        PredictiveROIOptimizer instance
    """
    return PredictiveROIOptimizer(
        impact_tracker=impact_tracker,
        min_roi_threshold=min_roi
    )
