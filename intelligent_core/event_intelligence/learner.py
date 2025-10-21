"""
Event Learner - Обучение на паттернах событий (with ACE learning!)

Функции:
- Обучение на исторических решениях
- Выявление успешных паттернов
- Запоминание антипаттернов
- Улучшение рекомендаций со временем
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict
import sys

# Add platform root for ACE integration
sys.path.insert(0, '/Users/MD/AI-Platform-ISO')
from shared.ace_integration import ACEIntegration

logger = logging.getLogger(__name__)


@dataclass
class LearningExample:
    """Пример для обучения"""
    event_name: str
    suggested_action: str  # 'implement', 'postpone', 'reject'
    confidence: float
    developer_decision: Optional[str] = None  # Feedback
    outcome: Optional[str] = None  # 'success', 'failure', 'neutral'
    timestamp: str = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class Pattern:
    """Обнаруженный паттерн"""
    pattern_type: str  # 'success', 'failure'
    description: str
    confidence: float
    examples: List[str]
    learned_at: str


class EventLearner:
    """
    Система обучения на событиях

    Возможности:
    - Собирает feedback от разработчиков
    - Обучается на успешных/неудачных решениях
    - Выявляет паттерны
    - Улучшает точность рекомендаций
    """

    def __init__(self, storage_path: str = None):
        # ACE Integration for continuous learning
        self.ace = ACEIntegration(module_name="event_intelligence")

        self.storage_path = Path(storage_path or '/Users/MD/AI-Platform-ISO/intelligent-core/event_intelligence/data')
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.learning_db_path = self.storage_path / 'learning_database.json'
        self.patterns_path = self.storage_path / 'patterns.json'

        # Загружаем существующие данные
        self.learning_database = self._load_learning_database()
        self.patterns = self._load_patterns()

    def _load_learning_database(self) -> List[LearningExample]:
        """Загружает базу обучения"""
        if self.learning_db_path.exists():
            with open(self.learning_db_path, 'r') as f:
                data = json.load(f)
                return [LearningExample(**item) for item in data]
        return []

    def _save_learning_database(self):
        """Сохраняет базу обучения"""
        with open(self.learning_db_path, 'w') as f:
            json.dump([asdict(ex) for ex in self.learning_database], f, indent=2)

    def _load_patterns(self) -> List[Pattern]:
        """Загружает обнаруженные паттерны"""
        if self.patterns_path.exists():
            with open(self.patterns_path, 'r') as f:
                data = json.load(f)
                return [Pattern(**item) for item in data]
        return []

    def _save_patterns(self):
        """Сохраняет паттерны"""
        with open(self.patterns_path, 'w') as f:
            json.dump([asdict(p) for p in self.patterns], f, indent=2)

    async def record_suggestion(
        self,
        event_name: str,
        suggested_action: str,
        confidence: float
    ) -> str:
        """
        Записывает предложение для последующего feedback

        Returns:
            suggestion_id для отслеживания
        """
        example = LearningExample(
            event_name=event_name,
            suggested_action=suggested_action,
            confidence=confidence
        )

        self.learning_database.append(example)
        self._save_learning_database()

        logger.info(f" Recorded suggestion for '{event_name}': {suggested_action}")

        return example.timestamp  # Используем timestamp как ID

    async def record_feedback(
        self,
        suggestion_id: str,
        developer_decision: str,
        outcome: Optional[str] = None
    ):
        """
        Записывает feedback от разработчика

        Args:
            suggestion_id: ID предложения (timestamp)
            developer_decision: 'approved', 'rejected', 'postponed'
            outcome: 'success', 'failure', 'neutral' (после внедрения)
        """
        # Находим example
        for example in self.learning_database:
            if example.timestamp == suggestion_id:
                example.developer_decision = developer_decision
                if outcome:
                    example.outcome = outcome

                self._save_learning_database()
                logger.info(f" Feedback recorded for '{example.event_name}'")

                # Запускаем обучение
                await self._learn_from_feedback(example)
                break

    async def _learn_from_feedback(self, example: LearningExample):
        """Обучается на основе feedback"""

        # Проверяем, была ли рекомендация правильной
        if example.developer_decision == 'approved' and example.suggested_action == 'implement':
            logger.info(f" Correct prediction for '{example.event_name}'")
            # TODO: Увеличить confidence для похожих событий

        elif example.developer_decision == 'rejected' and example.suggested_action == 'implement':
            logger.warning(f" Incorrect prediction for '{example.event_name}'")
            # TODO: Анализ, почему ошиблись

        # Обновляем паттерны
        await self._update_patterns()

    async def _update_patterns(self):
        """Обновляет обнаруженные паттерны"""

        # Анализируем последние N примеров
        recent_examples = self.learning_database[-100:]  # Последние 100

        # Группируем по типам событий
        event_types = defaultdict(list)
        for ex in recent_examples:
            if ex.developer_decision:
                # Извлекаем тип события (например, *.completed)
                parts = ex.event_name.split('.')
                if len(parts) > 1:
                    event_type = f"*.{parts[-1]}"
                    event_types[event_type].append(ex)

        # Ищем паттерны
        new_patterns = []

        for event_type, examples in event_types.items():
            if len(examples) < 5:
                continue  # Недостаточно данных

            # Процент одобрений
            approved = sum(1 for ex in examples if ex.developer_decision == 'approved')
            approval_rate = approved / len(examples)

            if approval_rate > 0.8:
                # Успешный паттерн
                pattern = Pattern(
                    pattern_type='success',
                    description=f"Events of type '{event_type}' are usually approved ({approval_rate:.0%})",
                    confidence=approval_rate,
                    examples=[ex.event_name for ex in examples[:3]],
                    learned_at=datetime.utcnow().isoformat()
                )
                new_patterns.append(pattern)

            elif approval_rate < 0.2:
                # Антипаттерн
                pattern = Pattern(
                    pattern_type='failure',
                    description=f"Events of type '{event_type}' are usually rejected ({1-approval_rate:.0%})",
                    confidence=1 - approval_rate,
                    examples=[ex.event_name for ex in examples[:3]],
                    learned_at=datetime.utcnow().isoformat()
                )
                new_patterns.append(pattern)

        # Сохраняем новые паттерны
        self.patterns.extend(new_patterns)
        self._save_patterns()

        logger.info(f" Learned {len(new_patterns)} new patterns")

    async def get_learned_confidence(self, event_name: str, suggested_action: str) -> float:
        """
        Возвращает confidence на основе обучения (with ACE learning!)

        Returns:
            float: Adjusted confidence (0-1)
        """

        # Use ACE for continuous learning of confidence patterns!
        result = await self.ace.execute_with_learning(
            task_type=f"event_confidence_{suggested_action}",
            base_context={
                "event_name": event_name,
                "suggested_action": suggested_action
            },
            execute_fn=self._get_learned_confidence_impl,
            event_name=event_name,
            suggested_action=suggested_action
        )

        return result.get('learned_confidence', 0.5)

    async def _get_learned_confidence_impl(
        self,
        context: Dict,
        event_name: str,
        suggested_action: str
    ) -> Dict:
        """Internal confidence learning implementation (called by ACE)"""

        # ACE provides enhanced context!
        strategies = context.get('playbook_strategies', [])
        if strategies:
            logger.info(f" ACE enhanced confidence with {len(strategies)} strategies")

        base_confidence = 0.5

        # Проверяем, есть ли похожие примеры
        similar_examples = [
            ex for ex in self.learning_database
            if self._is_similar(ex.event_name, event_name)
            and ex.suggested_action == suggested_action
            and ex.developer_decision is not None
        ]

        if not similar_examples:
            return {
                'learned_confidence': base_confidence,
                'effectiveness': 0.5
            }

        # Вычисляем успешность на похожих примерах
        approved = sum(1 for ex in similar_examples if ex.developer_decision == 'approved')
        learned_confidence = approved / len(similar_examples)

        logger.info(f" Learned confidence for '{event_name}': {learned_confidence:.2f} (based on {len(similar_examples)} examples)")

        # Effectiveness = learned_confidence (ACE will learn to improve!)
        return {
            'learned_confidence': learned_confidence,
            'effectiveness': learned_confidence
        }

    def _is_similar(self, event1: str, event2: str) -> bool:
        """Проверяет похожесть событий"""

        # Простая эвристика: совпадает последняя часть
        parts1 = event1.split('.')
        parts2 = event2.split('.')

        if len(parts1) > 0 and len(parts2) > 0:
            return parts1[-1] == parts2[-1]

        return False

    async def get_learning_stats(self) -> Dict:
        """Возвращает статистику обучения"""

        total_examples = len(self.learning_database)
        with_feedback = sum(1 for ex in self.learning_database if ex.developer_decision)
        with_outcome = sum(1 for ex in self.learning_database if ex.outcome)

        # Accuracy
        correct_predictions = sum(
            1 for ex in self.learning_database
            if ex.developer_decision == 'approved' and ex.suggested_action == 'implement'
            or ex.developer_decision == 'rejected' and ex.suggested_action != 'implement'
        )
        accuracy = correct_predictions / with_feedback if with_feedback > 0 else 0

        return {
            'total_examples': total_examples,
            'with_feedback': with_feedback,
            'with_outcome': with_outcome,
            'accuracy': accuracy,
            'patterns_learned': len(self.patterns),
            'success_patterns': len([p for p in self.patterns if p.pattern_type == 'success']),
            'failure_patterns': len([p for p in self.patterns if p.pattern_type == 'failure'])
        }

    async def export_learning_report(self) -> Dict:
        """Экспортирует отчёт об обучении"""

        stats = await self.get_learning_stats()

        # Топ успешных паттернов
        success_patterns = [p for p in self.patterns if p.pattern_type == 'success']
        success_patterns.sort(key=lambda x: x.confidence, reverse=True)

        # Топ антипаттернов
        failure_patterns = [p for p in self.patterns if p.pattern_type == 'failure']
        failure_patterns.sort(key=lambda x: x.confidence, reverse=True)

        return {
            'stats': stats,
            'top_success_patterns': [asdict(p) for p in success_patterns[:5]],
            'top_failure_patterns': [asdict(p) for p in failure_patterns[:5]],
            'recent_learnings': [
                asdict(ex) for ex in self.learning_database[-10:]
                if ex.developer_decision
            ]
        }
