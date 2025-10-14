"""
Metrics Calculator
==================

Расчет метрик эффективности и обучения из симуляций.

Адаптировано из BCM Incident module:
- _calculate_effectiveness_score
- _assess_learning_progress
- _calculate_risk_score
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class EffectivenessCalculator:
    """
    Калькулятор эффективности симуляции

    Адаптировано из bcm_incident_unified.py:1135-1160
    """

    def calculate_effectiveness(
        self,
        target_rto: Optional[float],
        actual_rto: Optional[float],
        target_rpo: Optional[float],
        actual_rpo: Optional[float],
        escalation_level: int = 0,
        ai_classification_confidence: Optional[float] = None,
        post_review_completed: bool = False,
        quality_score: float = 0.0
    ) -> float:
        """
        Рассчитать оценку эффективности (0-100)

        Args:
            target_rto: Целевое RTO (hours)
            actual_rto: Фактическое RTO (hours)
            target_rpo: Целевое RPO (hours)
            actual_rpo: Фактическое RPO (hours)
            escalation_level: Уровень эскалации (больше = хуже)
            ai_classification_confidence: AI уверенность (0-100)
            post_review_completed: Был ли пост-анализ
            quality_score: Общая оценка качества (0-10)

        Returns:
            Оценка эффективности (0-100)
        """
        score = 50.0  # Базовый балл

        # === RTO Compliance (до +30 или -20) ===
        if target_rto is not None and actual_rto is not None and target_rto > 0:
            if actual_rto <= target_rto:
                # Достигли целевого RTO
                score += 30.0
                # Бонус если сильно лучше
                if actual_rto <= target_rto * 0.8:
                    score += 5.0
            else:
                # Превысили целевое RTO - штраф
                penalty = min(20.0, (actual_rto - target_rto) / target_rto * 20.0)
                score -= penalty

        # === RPO Compliance (до +15 или -10) ===
        if target_rpo is not None and actual_rpo is not None and target_rpo > 0:
            if actual_rpo <= target_rpo:
                score += 15.0
            else:
                penalty = min(10.0, (actual_rpo - target_rpo) / target_rpo * 10.0)
                score -= penalty

        # === Escalation Penalty (-5 за каждый уровень) ===
        score -= (escalation_level * 5.0)

        # === AI Confidence Bonus (до +10) ===
        if ai_classification_confidence is not None:
            score += (ai_classification_confidence / 100.0) * 10.0

        # === Post-Review Bonus (+10) ===
        if post_review_completed:
            score += 10.0

        # === Quality Score Factor (до +10) ===
        if quality_score > 0:
            # Конвертируем 0-10 в бонус 0-10
            score += min(10.0, quality_score)

        # Нормализуем в диапазон 0-100
        final_score = max(0.0, min(100.0, score))

        logger.info(
            f"Effectiveness calculated: {final_score:.1f} "
            f"(RTO: {actual_rto}/{target_rto}, "
            f"Escalation: {escalation_level}, "
            f"Quality: {quality_score})"
        )

        return round(final_score, 1)


class LearningProgressCalculator:
    """
    Калькулятор прогресса обучения

    Адаптировано из bcm_incident_unified.py:1162-1185
    """

    def assess_learning_progress(
        self,
        similar_scenarios_count: int = 0,
        has_ai_recommendations: bool = False,
        has_lessons_learned: bool = False,
        lessons_learned_count: int = 0,
        has_preventive_measures: bool = False,
        preventive_measures_count: int = 0,
        has_root_cause_analysis: bool = False
    ) -> float:
        """
        Оценить прогресс обучения из симуляции (0-100)

        Args:
            similar_scenarios_count: Количество похожих сценариев
            has_ai_recommendations: Есть ли AI рекомендации
            has_lessons_learned: Есть ли извлеченные уроки
            lessons_learned_count: Количество уроков
            has_preventive_measures: Есть ли превентивные меры
            preventive_measures_count: Количество мер
            has_root_cause_analysis: Есть ли root cause analysis

        Returns:
            Прогресс обучения (0-100)
        """
        progress = 0.0

        # === Similar Scenarios Handling (до 40) ===
        # Чем больше похожих сценариев, тем больше опыта
        if similar_scenarios_count > 0:
            progress += min(40.0, similar_scenarios_count * 10.0)

        # === AI Recommendations Usage (20) ===
        if has_ai_recommendations:
            progress += 20.0

        # === Lessons Learned (до 25) ===
        if has_lessons_learned:
            base_lessons = 15.0
            # Бонус за количество
            bonus = min(10.0, lessons_learned_count * 2.0)
            progress += (base_lessons + bonus)

        # === Preventive Measures (до 20) ===
        if has_preventive_measures:
            base_preventive = 10.0
            # Бонус за количество
            bonus = min(10.0, preventive_measures_count * 2.0)
            progress += (base_preventive + bonus)

        # === Root Cause Analysis (15) ===
        if has_root_cause_analysis:
            progress += 15.0

        # Нормализуем в диапазон 0-100
        final_progress = min(100.0, progress)

        logger.info(
            f"Learning progress calculated: {final_progress:.1f}% "
            f"(Similar: {similar_scenarios_count}, "
            f"Lessons: {lessons_learned_count}, "
            f"Preventive: {preventive_measures_count})"
        )

        return round(final_progress, 1)


class RiskScoreCalculator:
    """
    Калькулятор оценки риска

    Адаптировано из bcm_incident_unified.py:756-780
    """

    SEVERITY_SCORES = {
        'low': 10,
        'medium': 30,
        'high': 60,
        'critical': 90
    }

    CATEGORY_MODIFIERS = {
        'cyber_security': 1.5,
        'pandemic': 1.4,
        'facility_damage': 1.3,
        'system_failure': 1.2,
        'disaster_recovery': 1.1,
        'supply_chain': 0.9,
        'communication': 0.8
    }

    def calculate_risk_score(
        self,
        severity: str,
        category: str,
        complexity_level: int = 3,
        hours_since_creation: Optional[float] = None
    ) -> float:
        """
        Рассчитать оценку риска сценария (0-100)

        Args:
            severity: Серьезность (low, medium, high, critical)
            category: Категория сценария
            complexity_level: Уровень сложности (1-5)
            hours_since_creation: Часов с создания сценария

        Returns:
            Оценка риска (0-100)
        """
        # Базовый score по серьезности
        score = self.SEVERITY_SCORES.get(severity, 30)

        # Модификатор по категории
        category_modifier = self.CATEGORY_MODIFIERS.get(category, 1.0)
        score *= category_modifier

        # Фактор сложности (больше сложность = больше риск)
        complexity_factor = 0.8 + (complexity_level * 0.1)
        score *= complexity_factor

        # Временной фактор (старые сценарии = выше риск устаревания)
        if hours_since_creation is not None and hours_since_creation > 24:
            # Каждые 24 часа +2% риска, максимум +20%
            age_factor = min(1.2, 1.0 + (hours_since_creation / 24.0) * 0.02)
            score *= age_factor

        # Нормализуем в диапазон 0-100
        final_score = min(100.0, max(0.0, score))

        logger.info(
            f"Risk score calculated: {final_score:.1f} "
            f"(Severity: {severity}, Category: {category}, "
            f"Complexity: {complexity_level})"
        )

        return round(final_score, 1)


class ComprehensiveMetricsCalculator:
    """
    Комплексный калькулятор всех метрик

    Объединяет все калькуляторы для удобства использования.
    """

    def __init__(self):
        self.effectiveness = EffectivenessCalculator()
        self.learning = LearningProgressCalculator()
        self.risk = RiskScoreCalculator()

    def calculate_all_metrics(
        self,
        scenario_data: Dict,
        results_data: Dict
    ) -> Dict[str, float]:
        """
        Рассчитать все метрики для симуляции

        Args:
            scenario_data: Данные сценария
            results_data: Данные результатов

        Returns:
            Словарь со всеми метриками
        """
        metrics = {}

        try:
            # Effectiveness
            metrics['effectiveness_score'] = self.effectiveness.calculate_effectiveness(
                target_rto=scenario_data.get('target_rto'),
                actual_rto=results_data.get('actual_rto'),
                target_rpo=scenario_data.get('target_rpo'),
                actual_rpo=results_data.get('actual_rpo'),
                escalation_level=results_data.get('escalation_level', 0),
                ai_classification_confidence=scenario_data.get('ai_classification_confidence'),
                post_review_completed=results_data.get('post_review_completed', False),
                quality_score=results_data.get('quality_score', 0.0)
            )

            # Learning Progress
            metrics['learning_progress'] = self.learning.assess_learning_progress(
                similar_scenarios_count=len(results_data.get('similar_scenarios', [])),
                has_ai_recommendations=bool(results_data.get('ai_recommendations')),
                has_lessons_learned=len(results_data.get('lessons_learned', [])) > 0,
                lessons_learned_count=len(results_data.get('lessons_learned', [])),
                has_preventive_measures=len(results_data.get('preventive_measures', [])) > 0,
                preventive_measures_count=len(results_data.get('preventive_measures', [])),
                has_root_cause_analysis=bool(results_data.get('root_cause_analysis'))
            )

            # Risk Score
            created_at = scenario_data.get('created_at')
            hours_since = None
            if created_at:
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                hours_since = (datetime.utcnow() - created_at).total_seconds() / 3600

            metrics['risk_score'] = self.risk.calculate_risk_score(
                severity=scenario_data.get('severity', 'medium'),
                category=scenario_data.get('category', 'custom'),
                complexity_level=scenario_data.get('complexity_level', 3),
                hours_since_creation=hours_since
            )

            logger.info(f"Comprehensive metrics calculated: {metrics}")

        except Exception as e:
            logger.error(f"Metrics calculation failed: {e}", exc_info=True)
            # Возвращаем безопасные дефолтные значения
            metrics = {
                'effectiveness_score': 50.0,
                'learning_progress': 0.0,
                'risk_score': 50.0
            }

        return metrics
