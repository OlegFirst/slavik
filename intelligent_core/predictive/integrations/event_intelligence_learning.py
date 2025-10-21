"""
Event Intelligence Learning для Predictive Service

Использует данные Event Intelligence для:
- Предсказания будущих событий
- Обучения на паттернах event flow
- Аномалий в событийной архитектуре
- Рекомендаций по улучшению
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

# Добавляем tools в путь
sys.path.append(str(Path(__file__).parents[3] / 'tools'))

from event_intelligence.event_intelligence_system import EventIntelligenceSystem
from event_intelligence.continuous_monitor import EventIntelligenceMonitor

logger = logging.getLogger(__name__)


class EventIntelligenceLearning:
    """
    Обучение Predictive Service на основе Event Intelligence

    Возможности:
    - Анализ паттернов событий
    - Предсказание будущих event gaps
    - Обнаружение аномалий в event flow
    - ML-based event recommendations
    """

    def __init__(self, project_root: str = "/Users/MD/AI-Platform-ISO"):
        self.project_root = Path(project_root)
        self.eis = EventIntelligenceSystem(str(project_root))
        self.monitor = EventIntelligenceMonitor(str(project_root))

        # Загружаем исторические данные
        self.history = self.monitor.history

    async def predict_future_gaps(self, days_ahead: int = 7) -> List[Dict]:
        """
        Предсказывает будущие пробелы в событиях

        На основе:
        - Исторических трендов
        - Текущей скорости разработки
        - Паттернов добавления новых сервисов

        Args:
            days_ahead: Горизонт предсказания в днях

        Returns:
            List предсказанных gaps с вероятностью
        """
        logger.info(f" Predicting event gaps for next {days_ahead} days...")

        if len(self.history) < 7:
            logger.warning("Not enough historical data for prediction")
            return []

        # Анализируем тренды
        recent = self.history[-7:]  # Последняя неделя

        # Вычисляем скорость появления новых событий
        event_counts = [h['summary']['code_events'] for h in recent]
        avg_growth_rate = (event_counts[-1] - event_counts[0]) / len(recent)

        # Прогноз количества событий
        current_events = event_counts[-1]
        predicted_events = int(current_events + (avg_growth_rate * days_ahead))

        # Прогноз gaps на основе текущего соотношения
        current_gaps = recent[-1]['summary']['gaps_found']
        current_ratio = current_gaps / current_events if current_events > 0 else 0

        predicted_gaps = int(predicted_events * current_ratio)

        # Определяем, какие типы gaps вероятнее всего появятся
        gap_types = defaultdict(int)
        for hist in recent:
            for gap in hist['gaps']:
                gap_types[gap['gap_type']] += 1

        # Сортируем по частоте
        likely_gap_types = sorted(
            gap_types.items(),
            key=lambda x: x[1],
            reverse=True
        )

        predictions = []

        for gap_type, count in likely_gap_types[:3]:
            probability = count / sum(gap_types.values())

            predictions.append({
                'gap_type': gap_type,
                'probability': probability,
                'estimated_count': int(predicted_gaps * probability),
                'recommended_action': self._get_recommended_action(gap_type),
                'predicted_date': (
                    datetime.utcnow() + timedelta(days=days_ahead)
                ).isoformat()
            })

        return predictions

    def _get_recommended_action(self, gap_type: str) -> str:
        """Рекомендация для типа gap"""
        actions = {
            'missing_publisher': 'Проактивно добавить publish() в новые методы изменения состояния',
            'missing_subscriber': 'Планировать reactive handlers для новых событий',
            'orphaned': 'Регулярно синхронизировать AsyncAPI схему с кодом'
        }
        return actions.get(gap_type, 'Мониторить и реагировать по необходимости')

    async def detect_event_anomalies(self) -> List[Dict]:
        """
        Обнаруживает аномалии в событийной архитектуре

        Аномалии:
        - Внезапный рост critical gaps
        - Резкое падение coverage
        - Несбалансированные publisher/subscriber ratios
        - Orphaned events без активности
        """
        logger.info(" Detecting event anomalies...")

        if len(self.history) < 14:
            return []

        anomalies = []
        recent = self.history[-14:]  # Последние 2 недели

        # 1. Проверка на спайки critical gaps
        critical_counts = [
            len([g for g in h['gaps'] if g['severity'] == 'critical'])
            for h in recent
        ]

        avg_critical = sum(critical_counts) / len(critical_counts)
        std_critical = (
            sum((x - avg_critical) ** 2 for x in critical_counts) / len(critical_counts)
        ) ** 0.5

        if critical_counts[-1] > avg_critical + (2 * std_critical):
            anomalies.append({
                'type': 'critical_spike',
                'severity': 'high',
                'description': f'Внезапный рост critical gaps: {critical_counts[-1]} (обычно {avg_critical:.1f})',
                'recommendation': 'Срочно проверить последние изменения кода'
            })

        # 2. Проверка coverage падения
        coverages = [
            (h['summary']['code_events'] / h['summary']['schema_events'] * 100)
            if h['summary']['schema_events'] > 0 else 100
            for h in recent
        ]

        if len(coverages) > 1 and coverages[-1] < coverages[-2] - 10:
            anomalies.append({
                'type': 'coverage_drop',
                'severity': 'medium',
                'description': f'Падение coverage: {coverages[-1]:.1f}% (было {coverages[-2]:.1f}%)',
                'recommendation': 'Проверить новые события в AsyncAPI схеме'
            })

        # 3. Несбалансированные ratios
        latest = recent[-1]
        total_publishers = latest['summary'].get('total_publishers', 0)
        total_subscribers = latest['summary'].get('total_subscribers', 0)

        if total_publishers > 0:
            ratio = total_subscribers / total_publishers

            if ratio < 0.2:  # Очень мало subscribers
                anomalies.append({
                    'type': 'low_subscribers',
                    'severity': 'medium',
                    'description': f'Мало subscribers: {total_subscribers} на {total_publishers} publishers (ratio: {ratio:.2f})',
                    'recommendation': 'Рассмотреть reactive processing для большего числа событий'
                })

        return anomalies

    async def generate_ml_recommendations(self) -> List[Dict]:
        """
        Генерирует ML-based рекомендации по событиям

        Использует:
        - Исторические паттерны
        - Корреляции между событиями
        - Best practices из успешных сервисов
        """
        logger.info(" Generating ML-based event recommendations...")

        # Загружаем текущее состояние
        self.eis.load_catalog()
        catalog = self.eis.catalog_data

        recommendations = []

        # 1. Анализ популярных событий
        events = catalog.get('events', {})

        # События с множественными publishers но без subscribers
        for event_name, event_data in events.items():
            pub_count = event_data.get('publisher_count', 0)
            sub_count = event_data.get('subscriber_count', 0)

            if pub_count >= 2 and sub_count == 0:
                recommendations.append({
                    'priority': 'high',
                    'event': event_name,
                    'reason': f'Event published by {pub_count} services but no subscribers',
                    'recommendation': 'Создать centralized handler для этого важного события',
                    'ml_confidence': 0.85,
                    'suggested_subscribers': self._suggest_subscribers(event_name)
                })

        # 2. Domain-specific рекомендации
        domain_events = defaultdict(list)
        for event_name in events.keys():
            domain = event_name.split('.')[0]
            domain_events[domain].append(event_name)

        for domain, domain_event_list in domain_events.items():
            # Если в домене мало событий, но много кода
            if len(domain_event_list) < 3:
                recommendations.append({
                    'priority': 'medium',
                    'domain': domain,
                    'reason': f'Domain {domain} has only {len(domain_event_list)} events',
                    'recommendation': f'Рассмотреть добавление core events для {domain} domain',
                    'ml_confidence': 0.70,
                    'suggested_events': self._suggest_domain_events(domain)
                })

        return recommendations

    def _suggest_subscribers(self, event_name: str) -> List[str]:
        """Предлагает потенциальных subscribers для события"""

        # Базовая эвристика на основе event name
        suggestions = []

        # Analytics service подписывается на большинство событий
        suggestions.append('analytics_service')

        # Audit logger на критичные события
        if any(kw in event_name for kw in ['complete', 'approve', 'delete']):
            suggestions.append('audit_logger')

        # Notification service на user-facing события
        if any(kw in event_name for kw in ['approve', 'reject', 'escalate']):
            suggestions.append('notification_service')

        # Predictive service на бизнес-события
        if any(kw in event_name for kw in ['bia', 'risk', 'incident']):
            suggestions.append('predictive_service')

        return suggestions

    def _suggest_domain_events(self, domain: str) -> List[str]:
        """Предлагает базовые события для домена"""

        base_events = [
            f'{domain}.created',
            f'{domain}.updated',
            f'{domain}.deleted',
            f'{domain}.completed',
        ]

        return base_events

    async def get_learning_insights(self) -> Dict:
        """
        Основная функция: возвращает все insights для Predictive Service

        Returns:
            Dict с предсказаниями, аномалиями и рекомендациями
        """
        predictions = await self.predict_future_gaps(days_ahead=7)
        anomalies = await self.detect_event_anomalies()
        ml_recommendations = await self.generate_ml_recommendations()

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'predictions': {
                'total': len(predictions),
                'items': predictions
            },
            'anomalies': {
                'total': len(anomalies),
                'high_severity': len([a for a in anomalies if a['severity'] == 'high']),
                'items': anomalies
            },
            'ml_recommendations': {
                'total': len(ml_recommendations),
                'high_priority': len([r for r in ml_recommendations if r['priority'] == 'high']),
                'items': ml_recommendations[:5]  # Top 5
            },
            'summary': {
                'status': self._calculate_overall_status(predictions, anomalies),
                'action_required': len([a for a in anomalies if a['severity'] == 'high']) > 0
            }
        }

    def _calculate_overall_status(self, predictions: List, anomalies: List) -> str:
        """Вычисляет общий статус событийной архитектуры"""

        high_severity_anomalies = len([a for a in anomalies if a['severity'] == 'high'])
        high_risk_predictions = len([p for p in predictions if p['probability'] > 0.7])

        if high_severity_anomalies > 0:
            return 'critical'
        elif high_risk_predictions > 2:
            return 'warning'
        else:
            return 'healthy'


# ============================================================================
# API для Predictive Service
# ============================================================================

async def get_event_intelligence_predictions() -> Dict:
    """
    Основная функция для получения predictions от Event Intelligence

    Используется Predictive Service для ML models
    """
    learning = EventIntelligenceLearning()
    return await learning.get_learning_insights()
