"""
Event Intelligence - AI Layer for Event Analysis and Learning

🧠 ИНТЕЛЛЕКТУАЛЬНЫЙ СЛОЙ для событийной архитектуры:
- Анализ событий и паттернов
- Обучение на исторических данных
- Предсказание будущих gaps
- Накопление знаний

Использует:
- tools/event_intelligence (для сканирования)
- ai-foundation (для ML моделей)
- Интеграция с другими AI сервисами
"""

from .analyzer import EventAnalyzer
from .learner import EventLearner
from .predictor import EventPredictor
from .knowledge_base import EventKnowledgeBase

__all__ = [
    'EventAnalyzer',
    'EventLearner',
    'EventPredictor',
    'EventKnowledgeBase'
]
