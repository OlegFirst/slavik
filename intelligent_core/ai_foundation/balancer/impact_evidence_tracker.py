"""
Evidence-Based Impact Tracker для рационализации решений

Философия:
- Каждое решение балансировщика → измеряем РЕАЛЬНОЕ влияние
- Доказательство работает ли наше вмешательство
- Рационализация: данные > интуиция
- Обучение на результатах

Что отслеживаем:
1. ДО вмешательства (baseline)
2. Решение балансировщика (intervention)
3. ПОСЛЕ вмешательства (outcome)
4. Причинно-следственная связь (causality)

Используется для:
- Доказательства эффективности балансировки
- Обучения коэффициентов (0.7, 1.5 → оптимальные значения)
- Рационализации бюджета ресурсов
- Отчетности для stakeholders
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics

logger = logging.getLogger(__name__)


class InterventionType(Enum):
    """Тип вмешательства балансировщика"""
    REWARD = "reward"              # Снижение ресурсов (поощрение)
    PENALTY = "penalty"            # Увеличение ресурсов (помощь)
    STABILIZATION = "stabilization"  # Emergency стабилизация
    REALLOCATION = "reallocation"    # Перераспределение


class ImpactLevel(Enum):
    """Уровень влияния"""
    POSITIVE = "positive"      # Улучшение
    NEUTRAL = "neutral"        # Без изменений
    NEGATIVE = "negative"      # Ухудшение
    UNKNOWN = "unknown"        # Еще рано оценивать


@dataclass
class BaselineMetrics:
    """Метрики ДО вмешательства"""
    module_name: str
    health_score: float
    cpu_usage: float
    memory_usage: float
    response_time: float
    error_rate: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class InterventionRecord:
    """Запись о вмешательстве"""
    intervention_id: str
    module_name: str
    intervention_type: InterventionType
    baseline: BaselineMetrics
    allocated_cpu: float
    allocated_memory: float
    reasoning: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class OutcomeMetrics:
    """Метрики ПОСЛЕ вмешательства"""
    intervention_id: str
    module_name: str
    health_score: float
    cpu_usage: float
    memory_usage: float
    response_time: float
    error_rate: float
    time_elapsed: float  # Сколько прошло времени после вмешательства
    timestamp: float = field(default_factory=time.time)


@dataclass
class ImpactEvidence:
    """
    Доказательство влияния

    Сравнение ДО и ПОСЛЕ с причинно-следственной связью
    """
    intervention_id: str
    module_name: str
    intervention_type: InterventionType

    # ДО
    baseline_health: float
    baseline_cpu: float
    baseline_memory: float

    # ПОСЛЕ
    outcome_health: float
    outcome_cpu: float
    outcome_memory: float

    # ИЗМЕНЕНИЯ (delta)
    health_delta: float
    cpu_delta: float
    memory_delta: float

    # ОЦЕНКА
    impact_level: ImpactLevel
    confidence: float  # 0-1 (уверенность в причинной связи)
    roi: float  # Return on Investment (improvement / resources_spent)

    reasoning: str
    timestamp: float = field(default_factory=time.time)


class ImpactEvidenceTracker:
    """
    Трекер доказательств влияния

    Измеряет и доказывает эффективность каждого решения балансировщика

    Workflow:
    1. record_baseline() - фиксируем ДО
    2. record_intervention() - фиксируем решение
    3. record_outcome() - фиксируем ПОСЛЕ (через N секунд)
    4. calculate_impact() - вычисляем влияние
    5. rationalize_decision() - рационализируем (стоило ли?)
    """

    def __init__(
        self,
        evaluation_delay_seconds: int = 60,
        min_confidence_threshold: float = 0.6
    ):
        """
        Initialize Impact Evidence Tracker

        Args:
            evaluation_delay_seconds: Через сколько оценивать результат
            min_confidence_threshold: Минимальная уверенность для доказательства
        """
        self.evaluation_delay = evaluation_delay_seconds
        self.min_confidence = min_confidence_threshold

        # Хранилища
        self.baselines: Dict[str, BaselineMetrics] = {}
        self.interventions: Dict[str, InterventionRecord] = {}
        self.outcomes: Dict[str, OutcomeMetrics] = {}
        self.evidences: List[ImpactEvidence] = []

        # Статистика
        self.stats = {
            'total_interventions': 0,
            'positive_impacts': 0,
            'neutral_impacts': 0,
            'negative_impacts': 0,
            'avg_health_improvement': 0.0,
            'avg_roi': 0.0,
            'successful_rewards': 0,
            'successful_penalties': 0,
            'failed_interventions': 0
        }

        logger.info(f" Impact Evidence Tracker initialized (eval delay: {evaluation_delay_seconds}s)")

    def record_baseline(
        self,
        module_name: str,
        health_score: float,
        cpu_usage: float,
        memory_usage: float,
        response_time: float = 0.0,
        error_rate: float = 0.0
    ) -> BaselineMetrics:
        """
        Зафиксировать baseline (ДО вмешательства)

        Args:
            module_name: Имя модуля
            health_score: Текущее здоровье (0-100)
            cpu_usage: CPU usage %
            memory_usage: Memory usage %
            response_time: Response time ms
            error_rate: Error rate %

        Returns:
            BaselineMetrics
        """
        baseline = BaselineMetrics(
            module_name=module_name,
            health_score=health_score,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            response_time=response_time,
            error_rate=error_rate
        )

        self.baselines[module_name] = baseline

        logger.debug(f" Baseline recorded for {module_name}: health={health_score:.1f}")

        return baseline

    def record_intervention(
        self,
        intervention_id: str,
        module_name: str,
        intervention_type: InterventionType,
        allocated_cpu: float,
        allocated_memory: float,
        reasoning: str
    ) -> InterventionRecord:
        """
        Зафиксировать вмешательство балансировщика

        Args:
            intervention_id: Уникальный ID вмешательства
            module_name: Имя модуля
            intervention_type: Тип вмешательства
            allocated_cpu: Выделенные CPU %
            allocated_memory: Выделенная память MB
            reasoning: Обоснование решения

        Returns:
            InterventionRecord
        """
        self.stats['total_interventions'] += 1

        # Получить baseline
        baseline = self.baselines.get(module_name)
        if not baseline:
            # Создать пустой baseline если не было
            baseline = BaselineMetrics(
                module_name=module_name,
                health_score=50.0,  # Unknown
                cpu_usage=0.0,
                memory_usage=0.0,
                response_time=0.0,
                error_rate=0.0
            )

        intervention = InterventionRecord(
            intervention_id=intervention_id,
            module_name=module_name,
            intervention_type=intervention_type,
            baseline=baseline,
            allocated_cpu=allocated_cpu,
            allocated_memory=allocated_memory,
            reasoning=reasoning
        )

        self.interventions[intervention_id] = intervention

        logger.info(
            f" Intervention recorded: {intervention_id} ({intervention_type.value}) "
            f"for {module_name}"
        )

        return intervention

    def record_outcome(
        self,
        intervention_id: str,
        health_score: float,
        cpu_usage: float,
        memory_usage: float,
        response_time: float = 0.0,
        error_rate: float = 0.0
    ) -> Optional[OutcomeMetrics]:
        """
        Зафиксировать outcome (ПОСЛЕ вмешательства)

        Args:
            intervention_id: ID вмешательства
            health_score: Здоровье после
            cpu_usage: CPU usage %
            memory_usage: Memory usage %
            response_time: Response time ms
            error_rate: Error rate %

        Returns:
            OutcomeMetrics or None if intervention not found
        """
        intervention = self.interventions.get(intervention_id)
        if not intervention:
            logger.warning(f"Intervention {intervention_id} not found")
            return None

        time_elapsed = time.time() - intervention.timestamp

        outcome = OutcomeMetrics(
            intervention_id=intervention_id,
            module_name=intervention.module_name,
            health_score=health_score,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            response_time=response_time,
            error_rate=error_rate,
            time_elapsed=time_elapsed
        )

        self.outcomes[intervention_id] = outcome

        # Автоматически вычислить impact
        impact = self.calculate_impact(intervention_id)

        logger.info(
            f" Outcome recorded for {intervention_id}: "
            f"health={health_score:.1f} (Δ{impact.health_delta:+.1f})"
        )

        return outcome

    def calculate_impact(self, intervention_id: str) -> Optional[ImpactEvidence]:
        """
        Вычислить влияние (compare baseline vs outcome)

        Args:
            intervention_id: ID вмешательства

        Returns:
            ImpactEvidence with proof of causality
        """
        intervention = self.interventions.get(intervention_id)
        outcome = self.outcomes.get(intervention_id)

        if not intervention or not outcome:
            logger.warning(f"Cannot calculate impact for {intervention_id}: missing data")
            return None

        baseline = intervention.baseline

        # Вычислить deltas
        health_delta = outcome.health_score - baseline.health_score
        cpu_delta = outcome.cpu_usage - baseline.cpu_usage
        memory_delta = outcome.memory_usage - baseline.memory_usage

        # Определить impact level
        if health_delta > 10.0:
            impact_level = ImpactLevel.POSITIVE
            self.stats['positive_impacts'] += 1
        elif health_delta < -10.0:
            impact_level = ImpactLevel.NEGATIVE
            self.stats['negative_impacts'] += 1
        else:
            impact_level = ImpactLevel.NEUTRAL
            self.stats['neutral_impacts'] += 1

        # Рассчитать confidence (уверенность в причинной связи)
        confidence = self._calculate_confidence(
            intervention,
            outcome,
            health_delta,
            cpu_delta,
            memory_delta
        )

        # Рассчитать ROI
        roi = self._calculate_roi(
            health_delta,
            intervention.allocated_cpu,
            intervention.allocated_memory
        )

        # Обновить статистику
        if impact_level == ImpactLevel.POSITIVE:
            if intervention.intervention_type == InterventionType.REWARD:
                self.stats['successful_rewards'] += 1
            elif intervention.intervention_type == InterventionType.PENALTY:
                self.stats['successful_penalties'] += 1
        elif impact_level == ImpactLevel.NEGATIVE:
            self.stats['failed_interventions'] += 1

        # Reasoning
        reasoning = self._generate_impact_reasoning(
            intervention.intervention_type,
            health_delta,
            cpu_delta,
            memory_delta,
            confidence,
            roi
        )

        evidence = ImpactEvidence(
            intervention_id=intervention_id,
            module_name=intervention.module_name,
            intervention_type=intervention.intervention_type,
            baseline_health=baseline.health_score,
            baseline_cpu=baseline.cpu_usage,
            baseline_memory=baseline.memory_usage,
            outcome_health=outcome.health_score,
            outcome_cpu=outcome.cpu_usage,
            outcome_memory=outcome.memory_usage,
            health_delta=health_delta,
            cpu_delta=cpu_delta,
            memory_delta=memory_delta,
            impact_level=impact_level,
            confidence=confidence,
            roi=roi,
            reasoning=reasoning
        )

        self.evidences.append(evidence)

        # Обновить avg статистику
        self._update_avg_stats()

        logger.info(
            f" Impact calculated: {intervention_id} → {impact_level.value} "
            f"(confidence: {confidence:.2f}, ROI: {roi:.2f})"
        )

        return evidence

    def _calculate_confidence(
        self,
        intervention: InterventionRecord,
        outcome: OutcomeMetrics,
        health_delta: float,
        cpu_delta: float,
        memory_delta: float
    ) -> float:
        """
        Рассчитать уверенность в причинной связи

        Факторы:
        - Время между intervention и outcome (чем меньше → выше confidence)
        - Величина изменения (чем больше → выше confidence)
        - Согласованность с ожидаемым направлением

        Returns:
            0-1
        """
        confidence = 0.5  # baseline

        # Фактор времени (если быстро → более уверены)
        if outcome.time_elapsed < 60:  # < 1 min
            confidence += 0.2
        elif outcome.time_elapsed < 300:  # < 5 min
            confidence += 0.1

        # Фактор величины изменения
        if abs(health_delta) > 20:
            confidence += 0.2
        elif abs(health_delta) > 10:
            confidence += 0.1

        # Фактор согласованности с ожиданием
        if intervention.intervention_type == InterventionType.REWARD:
            # Ожидаем: health улучшится или останется
            if health_delta >= 0:
                confidence += 0.2
        elif intervention.intervention_type == InterventionType.PENALTY:
            # Ожидаем: health улучшится (дали больше ресурсов)
            if health_delta > 0:
                confidence += 0.2

        return min(confidence, 1.0)

    def _calculate_roi(
        self,
        health_improvement: float,
        cpu_spent: float,
        memory_spent: float
    ) -> float:
        """
        Рассчитать ROI (Return on Investment)

        ROI = (Improvement / Resources Spent)

        Positive ROI = хорошее вложение
        Negative ROI = потрачены ресурсы впустую
        """
        # Нормализовать resources spent к единой метрике
        resources_spent = (cpu_spent * 0.5 + memory_spent * 0.0001)

        if resources_spent == 0:
            return 0.0

        roi = health_improvement / resources_spent

        return roi

    def _generate_impact_reasoning(
        self,
        intervention_type: InterventionType,
        health_delta: float,
        cpu_delta: float,
        memory_delta: float,
        confidence: float,
        roi: float
    ) -> str:
        """Генерировать человекочитаемое обоснование влияния"""

        impact_desc = "improved" if health_delta > 0 else "degraded" if health_delta < 0 else "unchanged"

        reasoning = (
            f"{intervention_type.value.upper()}: Health {impact_desc} by {health_delta:+.1f}. "
            f"CPU Δ{cpu_delta:+.1f}%, Memory Δ{memory_delta:+.1f}%. "
            f"Confidence: {confidence:.0%}, ROI: {roi:.2f}."
        )

        if confidence < self.min_confidence:
            reasoning += " ️  Low confidence - may not be causal."

        if roi < 0:
            reasoning += "  Negative ROI - inefficient use of resources."
        elif roi > 1.0:
            reasoning += "  Positive ROI - good investment."

        return reasoning

    def _update_avg_stats(self):
        """Обновить средние статистики"""
        if not self.evidences:
            return

        health_improvements = [e.health_delta for e in self.evidences]
        rois = [e.roi for e in self.evidences]

        self.stats['avg_health_improvement'] = statistics.mean(health_improvements)
        self.stats['avg_roi'] = statistics.mean(rois)

    def rationalize_decision(
        self,
        intervention_id: str
    ) -> Dict[str, Any]:
        """
        Рационализация решения: стоило ли?

        Возвращает:
        - Было ли решение правильным?
        - Доказательства (evidence)
        - Рекомендации на будущее
        """
        evidence = None
        for e in self.evidences:
            if e.intervention_id == intervention_id:
                evidence = e
                break

        if not evidence:
            return {
                'justified': False,
                'reason': 'No evidence available',
                'recommendations': ['Wait for outcome data']
            }

        # Критерии рационализации
        justified = (
            evidence.confidence >= self.min_confidence and
            evidence.impact_level == ImpactLevel.POSITIVE and
            evidence.roi > 0
        )

        recommendations = []

        if evidence.confidence < self.min_confidence:
            recommendations.append("Low confidence - need more data or longer evaluation period")

        if evidence.roi < 0:
            recommendations.append("Negative ROI - consider different intervention strategy")

        if evidence.impact_level == ImpactLevel.NEGATIVE:
            recommendations.append("Intervention worsened situation - rollback or adjust approach")

        if not recommendations:
            recommendations.append("Intervention successful - continue similar strategy")

        return {
            'justified': justified,
            'confidence': evidence.confidence,
            'roi': evidence.roi,
            'impact_level': evidence.impact_level.value,
            'reasoning': evidence.reasoning,
            'recommendations': recommendations
        }

    def get_learning_insights(self) -> Dict[str, Any]:
        """
        Получить инсайты для обучения

        Что работает? Что не работает?
        Какие коэффициенты оптимальны?
        """
        if len(self.evidences) < 10:
            return {
                'insufficient_data': True,
                'message': 'Need at least 10 interventions for insights'
            }

        # Разделить по типам вмешательства
        rewards = [e for e in self.evidences if e.intervention_type == InterventionType.REWARD]
        penalties = [e for e in self.evidences if e.intervention_type == InterventionType.PENALTY]

        # Эффективность REWARDS
        reward_success_rate = (
            len([r for r in rewards if r.impact_level == ImpactLevel.POSITIVE]) / len(rewards) * 100
            if rewards else 0
        )

        # Эффективность PENALTIES
        penalty_success_rate = (
            len([p for p in penalties if p.impact_level == ImpactLevel.POSITIVE]) / len(penalties) * 100
            if penalties else 0
        )

        # Средний ROI по типам
        reward_avg_roi = statistics.mean([r.roi for r in rewards]) if rewards else 0
        penalty_avg_roi = statistics.mean([p.roi for p in penalties]) if penalties else 0

        return {
            'total_interventions': len(self.evidences),
            'reward_interventions': len(rewards),
            'penalty_interventions': len(penalties),
            'reward_success_rate': reward_success_rate,
            'penalty_success_rate': penalty_success_rate,
            'reward_avg_roi': reward_avg_roi,
            'penalty_avg_roi': penalty_avg_roi,
            'recommendations': self._generate_learning_recommendations(
                reward_success_rate,
                penalty_success_rate,
                reward_avg_roi,
                penalty_avg_roi
            )
        }

    def _generate_learning_recommendations(
        self,
        reward_success: float,
        penalty_success: float,
        reward_roi: float,
        penalty_roi: float
    ) -> List[str]:
        """Генерировать рекомендации на основе обучения"""
        recommendations = []

        if reward_success < 50:
            recommendations.append(
                f"️  REWARDS только {reward_success:.0f}% успешны - "
                "возможно коэффициент 0.7 слишком агрессивный, попробовать 0.8"
            )

        if penalty_success < 50:
            recommendations.append(
                f"️  PENALTIES только {penalty_success:.0f}% успешны - "
                "возможно коэффициент 1.5 недостаточен, попробовать 1.7"
            )

        if reward_roi < 0:
            recommendations.append(
                " REWARDS имеют негативный ROI - пересмотреть стратегию поощрения"
            )

        if penalty_roi > 2.0:
            recommendations.append(
                " PENALTIES очень эффективны (ROI > 2) - увеличить использование"
            )

        if not recommendations:
            recommendations.append(
                " Текущая стратегия работает хорошо - продолжать"
            )

        return recommendations

    def get_stats(self) -> Dict[str, Any]:
        """Статистика трекера"""
        return {
            **self.stats,
            'total_evidences': len(self.evidences),
            'success_rate': (
                self.stats['positive_impacts'] / self.stats['total_interventions'] * 100
                if self.stats['total_interventions'] > 0 else 0
            )
        }


def create_impact_tracker(
    evaluation_delay: int = 60,
    min_confidence: float = 0.6
) -> ImpactEvidenceTracker:
    """
    Factory function для создания Impact Evidence Tracker

    Args:
        evaluation_delay: Delay in seconds before evaluating outcome
        min_confidence: Minimum confidence threshold

    Returns:
        ImpactEvidenceTracker instance
    """
    return ImpactEvidenceTracker(
        evaluation_delay_seconds=evaluation_delay,
        min_confidence_threshold=min_confidence
    )
