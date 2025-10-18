"""
Scenario Classification Engine
==============================

Автоматическая классификация симуляционных сценариев на основе:
- Анализа ключевых слов
- Оценки сложности
- Расчета риска

Адаптировано из BCM Incident module AI classification system.
"""

import logging
import re
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ScenarioClassification:
    """Результат классификации сценария"""
    category: str
    complexity: int  # 1-5
    confidence: float  # 0.0-1.0
    risk_score: float  # 0-100
    matched_keywords: List[str]
    suggested_engine: str


class ScenarioClassifier:
    """
    Классификатор сценариев симуляций

    Автоматически определяет:
    - Категорию сценария (cyber, operational, natural, etc.)
    - Уровень сложности (1-5)
    - Рекомендованный движок симуляции
    - Оценку риска
    """

    # Категории сценариев с ключевыми словами
    CATEGORY_KEYWORDS = {
        'cyber': [
            'hack', 'breach', 'malware', 'ransomware', 'phishing',
            'ddos', 'cyber', 'attack', 'security', 'data breach',
            'unauthorized access', 'exploit', 'vulnerability'
        ],
        'operational': [
            'outage', 'failure', 'down', 'unavailable', 'performance',
            'disruption', 'service', 'system', 'downtime', 'technical',
            'infrastructure', 'degradation'
        ],
        'natural': [
            'earthquake', 'flood', 'fire', 'storm', 'hurricane',
            'tornado', 'tsunami', 'disaster', 'weather', 'lightning',
            'landslide', 'avalanche', 'volcanic'
        ],
        'supply_chain': [
            'supplier', 'delivery', 'logistics', 'procurement',
            'vendor', 'shipment', 'inventory', 'manufacturing',
            'distribution', 'transportation', 'warehouse'
        ],
        'health_safety': [
            'injury', 'accident', 'safety', 'emergency', 'medical',
            'evacuation', 'hazmat', 'contamination', 'exposure',
            'health', 'casualty', 'rescue'
        ],
        'pandemic': [
            'epidemic', 'pandemic', 'outbreak', 'virus', 'disease',
            'infection', 'contagious', 'quarantine', 'lockdown',
            'vaccination', 'health crisis', 'covid'
        ],
        'infrastructure': [
            'power', 'water', 'utilities', 'facilities', 'building',
            'hvac', 'electrical', 'plumbing', 'structure',
            'telecommunications', 'network', 'datacenter'
        ],
        'financial': [
            'fraud', 'financial', 'payment', 'banking', 'transaction',
            'money', 'currency', 'economic', 'market', 'trading',
            'investment', 'credit'
        ],
        'reputational': [
            'reputation', 'media', 'public', 'brand', 'social media',
            'pr crisis', 'scandal', 'negative', 'backlash',
            'protest', 'boycott'
        ]
    }

    # Индикаторы сложности
    COMPLEXITY_INDICATORS = {
        'high': [
            'multiple', 'widespread', 'critical', 'cascade', 'complex',
            'simultaneous', 'cross-border', 'global', 'severe',
            'catastrophic', 'enterprise-wide', 'multi-site'
        ],
        'medium': [
            'moderate', 'limited', 'contained', 'local', 'regional',
            'significant', 'substantial', 'major', 'departmental'
        ],
        'low': [
            'minor', 'simple', 'single', 'isolated', 'small',
            'trivial', 'localized', 'minimal', 'brief'
        ]
    }

    # Модификаторы риска по категориям
    CATEGORY_RISK_MODIFIERS = {
        'cyber': 1.5,
        'health_safety': 1.4,
        'natural': 1.3,
        'pandemic': 1.4,
        'infrastructure': 1.2,
        'operational': 1.0,
        'supply_chain': 0.9,
        'financial': 1.1,
        'reputational': 0.8
    }

    # Рекомендации по движку симуляции
    ENGINE_RECOMMENDATIONS = {
        1: 'simple',      # Простые сценарии - простой движок
        2: 'simple',
        3: 'advanced',    # Средние сценарии - продвинутый движок
        4: 'jaamsim',     # Сложные сценарии - JaamSim
        5: 'jaamsim'      # Очень сложные - JaamSim с AI
    }

    def __init__(self):
        """Инициализация классификатора"""
        self.logger = logger

    def classify_scenario(
        self,
        title: str,
        description: str,
        severity: Optional[str] = None,
        additional_context: Optional[Dict] = None
    ) -> ScenarioClassification:
        """
        Классифицировать сценарий симуляции

        Args:
            title: Название сценария
            description: Описание сценария
            severity: Опциональная предустановленная серьезность
            additional_context: Дополнительный контекст

        Returns:
            ScenarioClassification с результатами классификации
        """
        try:
            # Объединяем текст для анализа
            text = f"{title} {description}".lower()

            # Классификация категории
            category, matched_keywords, confidence = self._classify_category(text)

            # Оценка сложности
            complexity = self._assess_complexity(text, additional_context)

            # Расчет риска
            risk_score = self._calculate_risk_score(
                category=category,
                complexity=complexity,
                severity=severity,
                text=text
            )

            # Рекомендация движка
            suggested_engine = self._recommend_engine(complexity, category)

            result = ScenarioClassification(
                category=category,
                complexity=complexity,
                confidence=confidence,
                risk_score=risk_score,
                matched_keywords=matched_keywords,
                suggested_engine=suggested_engine
            )

            self.logger.info(
                f"Classified scenario: category={category}, "
                f"complexity={complexity}, confidence={confidence:.2f}, "
                f"risk={risk_score:.1f}, engine={suggested_engine}"
            )

            return result

        except Exception as e:
            self.logger.error(f"Classification failed: {e}", exc_info=True)
            # Возвращаем безопасный дефолт
            return ScenarioClassification(
                category='general',
                complexity=3,
                confidence=0.5,
                risk_score=50.0,
                matched_keywords=[],
                suggested_engine='simple'
            )

    def _classify_category(self, text: str) -> Tuple[str, List[str], float]:
        """
        Классифицировать категорию по ключевым словам

        Returns:
            (category, matched_keywords, confidence)
        """
        category_scores = {}
        category_matches = {}

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            matches = []
            for keyword in keywords:
                # Используем границы слов для точного поиска
                pattern = rf'\b{re.escape(keyword)}\b'
                if re.search(pattern, text):
                    matches.append(keyword)

            if matches:
                category_scores[category] = len(matches)
                category_matches[category] = matches

        if not category_scores:
            return ('general', [], 0.5)

        # Находим категорию с максимальным числом совпадений
        best_category = max(category_scores, key=category_scores.get)
        max_matches = category_scores[best_category]
        matched_keywords = category_matches[best_category]

        # Рассчитываем уверенность (0.5 - 0.95)
        confidence = min(0.95, 0.5 + (max_matches * 0.15))

        # Если есть вторая близкая категория, снижаем уверенность
        sorted_scores = sorted(category_scores.values(), reverse=True)
        if len(sorted_scores) > 1 and sorted_scores[1] >= sorted_scores[0] * 0.7:
            confidence *= 0.85

        return (best_category, matched_keywords, confidence)

    def _assess_complexity(
        self,
        text: str,
        additional_context: Optional[Dict]
    ) -> int:
        """
        Оценить сложность сценария (1-5)

        Факторы:
        - Индикаторы сложности в тексте
        - Количество затронутых систем
        - Число участников
        - Продолжительность
        """
        complexity_score = 3  # Default: средняя сложность

        # Анализ текстовых индикаторов
        for level, indicators in self.COMPLEXITY_INDICATORS.items():
            matches = sum(1 for ind in indicators if ind in text)

            if level == 'high' and matches > 0:
                complexity_score = min(5, complexity_score + matches)
            elif level == 'low' and matches > 0:
                complexity_score = max(1, complexity_score - matches)

        # Учитываем дополнительный контекст
        if additional_context:
            # Много затронутых систем = выше сложность
            affected_systems = additional_context.get('affected_systems', [])
            if isinstance(affected_systems, list) and len(affected_systems) > 5:
                complexity_score = min(5, complexity_score + 1)

            # Много участников = выше сложность
            participants = additional_context.get('participants', 0)
            if participants > 50:
                complexity_score = min(5, complexity_score + 1)
            elif participants > 20:
                complexity_score = min(5, complexity_score + 0.5)

            # Длительная симуляция = выше сложность
            duration_hours = additional_context.get('duration_hours', 0)
            if duration_hours > 8:
                complexity_score = min(5, complexity_score + 1)

        return max(1, min(5, int(round(complexity_score))))

    def _calculate_risk_score(
        self,
        category: str,
        complexity: int,
        severity: Optional[str],
        text: str
    ) -> float:
        """
        Рассчитать оценку риска (0-100)

        Факторы:
        - Серьезность (severity)
        - Категория (модификатор)
        - Сложность
        - Временные факторы
        """
        # Базовая оценка по серьезности
        severity_scores = {
            'low': 10,
            'medium': 30,
            'high': 60,
            'critical': 90
        }

        # Если серьезность не указана, оцениваем по тексту
        if not severity:
            if any(word in text for word in ['critical', 'severe', 'catastrophic', 'major']):
                severity = 'critical'
            elif any(word in text for word in ['high', 'significant', 'serious']):
                severity = 'high'
            elif any(word in text for word in ['moderate', 'medium', 'noticeable']):
                severity = 'medium'
            else:
                severity = 'low'

        score = severity_scores.get(severity, 30)

        # Применяем модификатор категории
        category_modifier = self.CATEGORY_RISK_MODIFIERS.get(category, 1.0)
        score *= category_modifier

        # Применяем фактор сложности
        complexity_factor = 0.8 + (complexity * 0.1)
        score *= complexity_factor

        # Дополнительные факторы риска из текста
        high_risk_terms = [
            'data loss', 'life-threatening', 'irreversible', 'permanent',
            'widespread', 'cascading', 'systemic', 'compliance violation'
        ]

        risk_term_matches = sum(1 for term in high_risk_terms if term in text)
        if risk_term_matches > 0:
            score *= (1.0 + risk_term_matches * 0.1)

        return min(100.0, max(0.0, score))

    def _recommend_engine(self, complexity: int, category: str) -> str:
        """
        Рекомендовать движок симуляции

        Логика:
        - Сложность 1-2: простой движок
        - Сложность 3: продвинутый движок
        - Сложность 4-5: JaamSim (дискретное моделирование)
        - Некоторые категории всегда требуют JaamSim
        """
        # Некоторые категории автоматически требуют сложных движков
        complex_categories = ['cyber', 'pandemic', 'infrastructure']
        if category in complex_categories and complexity >= 3:
            return 'jaamsim'

        return self.ENGINE_RECOMMENDATIONS.get(complexity, 'simple')

    def get_category_description(self, category: str) -> str:
        """Получить описание категории"""
        descriptions = {
            'cyber': 'Кибербезопасность и информационная безопасность',
            'operational': 'Операционные нарушения и отказы систем',
            'natural': 'Природные катастрофы и стихийные бедствия',
            'supply_chain': 'Нарушения цепочки поставок',
            'health_safety': 'Здоровье, безопасность и чрезвычайные ситуации',
            'pandemic': 'Пандемии и эпидемиологические кризисы',
            'infrastructure': 'Инфраструктурные сбои и отказы',
            'financial': 'Финансовые риски и мошенничество',
            'reputational': 'Репутационные риски и PR-кризисы',
            'general': 'Общие бизнес-процессы и сценарии'
        }
        return descriptions.get(category, 'Неопределенная категория')

    def get_complexity_description(self, complexity: int) -> str:
        """Получить описание уровня сложности"""
        descriptions = {
            1: 'Очень простой сценарий с минимальными зависимостями',
            2: 'Простой сценарий с ограниченными факторами',
            3: 'Средний сценарий с умеренной сложностью',
            4: 'Сложный сценарий с множественными факторами',
            5: 'Очень сложный сценарий требующий детального моделирования'
        }
        return descriptions.get(complexity, 'Неопределенная сложность')

    def batch_classify(
        self,
        scenarios: List[Dict[str, str]]
    ) -> List[ScenarioClassification]:
        """
        Пакетная классификация нескольких сценариев

        Args:
            scenarios: Список словарей с ключами 'title' и 'description'

        Returns:
            Список ScenarioClassification
        """
        results = []
        for scenario in scenarios:
            result = self.classify_scenario(
                title=scenario.get('title', ''),
                description=scenario.get('description', ''),
                severity=scenario.get('severity'),
                additional_context=scenario.get('context')
            )
            results.append(result)

        self.logger.info(f"Batch classified {len(scenarios)} scenarios")
        return results
