"""
Knowledge Monitor - Монитор качества знаний

Философия триединства:
- ЗНАНИЕ: Измеряем покрытие и полноту знаний
- ЗАЩИТА: Отслеживаем соответствие стандартам (ISO/NIST/WHO)
- САМОРЕАЛИЗАЦИЯ: Оцениваем практическую ценность и использование

Экономика знаний:
- Данные → Знания (анализ покрытия)
- Знания → Инструменты (метрики и отчеты)
- Опыт → Память (трекинг использования)
"""

import logging
import json
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import httpx

from models import (
    KnowledgeGap, GapType, KnowledgeState,
    CoverageReport, QualityReport, KQMMetrics,
    GenerationMetrics, PerformanceMetrics
)
from config.settings import settings

logger = logging.getLogger(__name__)


class KnowledgeMonitor:
    """
    Монитор знаний - оценивает состояние базы знаний

    Триединство в действии:
    1. ЗНАНИЕ: Обнаруживает пробелы, измеряет покрытие
    2. ЗАЩИТА: Проверяет соблюдение стандартов
    3. САМОРЕАЛИЗАЦИЯ: Оценивает ценность и использование
    """

    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)

        # ISO 22301 требования (11 основных разделов)
        self.iso_clauses = [
            "4.1", "4.2", "4.3", "4.4",  # Контекст организации
            "5.1", "5.2", "5.3",          # Лидерство
            "6.1", "6.2",                 # Планирование
            "7.1", "7.2", "7.3", "7.4", "7.5",  # Поддержка
            "8.1", "8.2", "8.3", "8.4",   # Операционная деятельность
            "9.1", "9.2", "9.3",          # Оценка результатов
            "10.1", "10.2"                # Улучшение
        ]

        # Сервисы платформы
        self.platform_services = [
            "BIA", "Risk", "Planning", "Response",
            "Compliance", "Exercise", "Documents",
            "Learning", "Governance"
        ]

        logger.info(" KnowledgeMonitor инициализирован")

    async def assess(self) -> KnowledgeState:
        """
        Полная оценка состояния знаний

        Триединство:
        - ЗНАНИЕ: Покрытие стандартов и платформы
        - ЗАЩИТА: Compliance метрики
        - САМОРЕАЛИЗАЦИЯ: Качество и использование
        """
        logger.info(" Оценка состояния знаний...")

        # 1. Покрытие
        coverage = await self.assess_coverage()

        # 2. Качество
        quality = await self.assess_quality()

        # 3. Пробелы
        gaps = await self.detect_gaps()

        state = KnowledgeState(
            coverage=coverage,
            quality=quality,
            gaps=gaps,
            timestamp=datetime.now()
        )

        logger.info(f" Оценка завершена:")
        logger.info(f"   ISO покрытие: {coverage.iso_coverage:.1%}")
        logger.info(f"   Платформа покрытие: {coverage.platform_coverage:.1%}")
        logger.info(f"   Обнаружено пробелов: {len(gaps)}")

        return state

    async def assess_coverage(self) -> CoverageReport:
        """
        Оценка покрытия знаний

        ЗНАНИЕ: Измеряем что мы знаем vs что должны знать
        """
        logger.info(" Оценка покрытия...")

        # Загружаем существующие сценарии
        existing_scenarios = await self._load_existing_scenarios()

        # ISO 22301 покрытие
        iso_documented = set()
        for scenario in existing_scenarios:
            if scenario.get('iso_clause'):
                iso_documented.add(scenario['iso_clause'])

        iso_coverage = len(iso_documented) / len(self.iso_clauses)

        # Платформа покрытие (по сервисам)
        services_documented = set()
        for scenario in existing_scenarios:
            if scenario.get('service'):
                services_documented.add(scenario['service'])

        platform_coverage = len(services_documented) / len(self.platform_services)

        # Пробелы пользователей (недокументированные вопросы)
        user_gaps = await self._count_user_gaps()

        report = CoverageReport(
            iso_coverage=iso_coverage,
            platform_coverage=platform_coverage,
            user_gaps=user_gaps,
            total_scenarios=len(existing_scenarios),
            iso_clauses_total=len(self.iso_clauses),
            iso_clauses_documented=len(iso_documented),
            endpoints_total=len(self.platform_services) * 20,  # ~20 endpoints per service
            endpoints_documented=len(existing_scenarios)
        )

        return report

    async def assess_quality(self) -> QualityReport:
        """
        Оценка качества знаний

        САМОРЕАЛИЗАЦИЯ: Измеряем ценность и актуальность
        """
        logger.info(" Оценка качества...")

        scenarios = await self._load_existing_scenarios()

        if not scenarios:
            return QualityReport(
                validation_rate=0.0,
                expert_approval_rate=0.0,
                usage_rate=0.0,
                stale_count=0,
                avg_confidence=0.0
            )

        # Валидация (проверены экспертами)
        validated = [s for s in scenarios if s.get('validated', False)]
        validation_rate = len(validated) / len(scenarios)

        # Одобрено экспертами
        approved = [s for s in validated if s.get('expert_approved', False)]
        expert_approval_rate = len(approved) / len(validated) if validated else 0.0

        # Использование (есть в логах обращений)
        usage_count = await self._count_scenario_usage(scenarios)
        usage_rate = usage_count / len(scenarios)

        # Устаревшие (> 90 дней без обновления)
        stale_threshold = datetime.now() - timedelta(days=90)
        stale_count = sum(
            1 for s in scenarios
            if datetime.fromisoformat(s.get('updated_at', '2020-01-01')) < stale_threshold
        )

        # Средняя уверенность
        confidences = [s.get('confidence', 0.5) for s in scenarios]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        report = QualityReport(
            validation_rate=validation_rate,
            expert_approval_rate=expert_approval_rate,
            usage_rate=usage_rate,
            stale_count=stale_count,
            avg_confidence=avg_confidence
        )

        return report

    async def detect_gaps(self) -> List[KnowledgeGap]:
        """
        Обнаружение пробелов в знаниях

        Триединство:
        - ЗНАНИЕ: Что мы не знаем?
        - ЗАЩИТА: Какие стандарты не покрыты?
        - САМОРЕАЛИЗАЦИЯ: Какие возможности не документированы?
        """
        logger.info(" Обнаружение пробелов...")

        gaps = []

        # 1. Пробелы в стандартах
        standard_gaps = await self._detect_standard_gaps()
        gaps.extend(standard_gaps)

        # 2. Пробелы в платформе
        capability_gaps = await self._detect_capability_gaps()
        gaps.extend(capability_gaps)

        # 3. Пробелы от пользователей
        user_gaps = await self._detect_user_gaps()
        gaps.extend(user_gaps)

        logger.info(f" Обнаружено пробелов:")
        logger.info(f"   Стандарты: {len(standard_gaps)}")
        logger.info(f"   Возможности: {len(capability_gaps)}")
        logger.info(f"   Пользователи: {len(user_gaps)}")

        return gaps

    async def _detect_standard_gaps(self) -> List[KnowledgeGap]:
        """Обнаружение пробелов в стандартах (ISO/NIST/WHO)"""
        gaps = []

        scenarios = await self._load_existing_scenarios()
        documented_clauses = set(
            s.get('iso_clause') for s in scenarios if s.get('iso_clause')
        )

        for clause in self.iso_clauses:
            if clause not in documented_clauses:
                gap = KnowledgeGap(
                    id=f"gap_iso_{clause.replace('.', '_')}",
                    type=GapType.STANDARD_REQUIREMENT,
                    description=f"ISO 22301 Clause {clause} не документирован",
                    priority=self._calculate_standard_priority(clause),
                    standard="ISO22301",
                    clause=clause,
                    detected_at=datetime.now(),
                    status="detected"
                )
                gaps.append(gap)

        return gaps

    async def _detect_capability_gaps(self) -> List[KnowledgeGap]:
        """Обнаружение пробелов в возможностях платформы"""
        gaps = []

        # Получаем список endpoint'ов с платформы
        try:
            platform_endpoints = await self._get_platform_endpoints()
            scenarios = await self._load_existing_scenarios()

            # Строим список документированных endpoint'ов
            documented_endpoints = set()
            for s in scenarios:
                # Простое извлечение - можно улучшить
                components = s.get('components', '')
                if 'API' in components or 'endpoint' in components.lower():
                    documented_endpoints.add(s.get('title', ''))

            # Находим недокументированные
            for service in self.platform_services:
                # Предполагаем ~20 endpoint'ов на сервис
                # В production - получаем из Service Registry
                endpoints_count = 20
                documented_count = len([
                    s for s in scenarios
                    if s.get('service') == service
                ])

                if documented_count < endpoints_count * 0.5:  # < 50% покрытие
                    gap = KnowledgeGap(
                        id=f"gap_cap_{service.lower()}",
                        type=GapType.PLATFORM_CAPABILITY,
                        description=f"Сервис {service}: недостаточно документированных сценариев ({documented_count}/{endpoints_count})",
                        priority=self._calculate_capability_priority(service),
                        service=service,
                        capability=f"{service}_capabilities",
                        detected_at=datetime.now(),
                        status="detected"
                    )
                    gaps.append(gap)

        except Exception as e:
            logger.error(f"Ошибка обнаружения пробелов возможностей: {e}")

        return gaps

    async def _detect_user_gaps(self) -> List[KnowledgeGap]:
        """Обнаружение пробелов от пользователей (вопросы без ответов)"""
        gaps = []

        try:
            # Получаем логи вопросов пользователей
            # В production - из Analytics или Support логов
            user_questions = await self._get_user_questions()

            for question in user_questions[:10]:  # Top 10 вопросов
                gap = KnowledgeGap(
                    id=f"gap_user_{hash(question['text']) % 10000}",
                    type=GapType.USER_REQUEST,
                    description=f"Вопрос пользователя без ответа: {question['text']}",
                    priority=question.get('frequency', 5),  # Приоритет по частоте
                    user_question=question['text'],
                    detected_at=datetime.now(),
                    status="detected"
                )
                gaps.append(gap)

        except Exception as e:
            logger.error(f"Ошибка обнаружения пробелов пользователей: {e}")

        return gaps

    async def get_all_metrics(self) -> KQMMetrics:
        """
        Полные метрики KQM

        Экономика знаний: все метрики для принятия решений
        """
        coverage = await self.assess_coverage()
        quality = await self.assess_quality()
        gaps = await self.detect_gaps()

        # Метрики генерации
        generation = GenerationMetrics(
            scenarios_generated_today=await self._count_generated_today(),
            scenarios_generated_this_week=await self._count_generated_this_week(),
            scenarios_generated_this_month=await self._count_generated_this_month(),
            pending_validation=len([g for g in gaps if g.status == "in_progress"]),
            approved_today=await self._count_approved_today()
        )

        # Метрики производительности
        performance = PerformanceMetrics(
            search_latency_ms=await self._measure_search_latency(),
            generation_time_min=5.0,  # Средн время генерации
            cache_hit_rate=await self._get_cache_hit_rate(),
            avg_quality_score=quality.avg_confidence
        )

        # Пробелы по типам
        gaps_by_type = {
            "standard_requirement": len([g for g in gaps if g.type == GapType.STANDARD_REQUIREMENT]),
            "platform_capability": len([g for g in gaps if g.type == GapType.PLATFORM_CAPABILITY]),
            "user_request": len([g for g in gaps if g.type == GapType.USER_REQUEST]),
            "community_pattern": len([g for g in gaps if g.type == GapType.COMMUNITY_PATTERN])
        }

        metrics = KQMMetrics(
            knowledge_coverage=coverage,
            knowledge_quality=quality,
            generation=generation,
            performance=performance,
            gaps_detected=gaps_by_type,
            timestamp=datetime.now()
        )

        return metrics

    async def report_metrics(self):
        """Отчет по метрикам (логирование)"""
        metrics = await self.get_all_metrics()

        logger.info("=" * 60)
        logger.info(" KNOWLEDGE QUALITY METRICS")
        logger.info("=" * 60)
        logger.info(f"ISO Coverage:      {metrics.knowledge_coverage.iso_coverage:.1%}")
        logger.info(f"Platform Coverage: {metrics.knowledge_coverage.platform_coverage:.1%}")
        logger.info(f"Validation Rate:   {metrics.knowledge_quality.validation_rate:.1%}")
        logger.info(f"Usage Rate:        {metrics.knowledge_quality.usage_rate:.1%}")
        logger.info(f"Generated Today:   {metrics.generation.scenarios_generated_today}")
        logger.info(f"Gaps Detected:     {sum(metrics.gaps_detected.values())}")
        logger.info("=" * 60)

    # ===== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ =====

    async def _load_existing_scenarios(self) -> List[Dict]:
        """Загрузка существующих сценариев из БД"""
        try:
            # Load from PostgreSQL
            import psycopg2
            from urllib.parse import quote_plus

            password = quote_plus(settings.DATABASE_URL.split(':')[2].split('@')[0])
            conn = psycopg2.connect(settings.DATABASE_URL)
            cur = conn.cursor()

            cur.execute("""
                SELECT id, title, content, service, category, iso_clause, type, confidence
                FROM public.kqm_scenarios
                ORDER BY created_at DESC
            """)

            scenarios = []
            for row in cur.fetchall():
                scenarios.append({
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'service': row[3],
                    'category': row[4],
                    'iso_clause': row[5],
                    'type': row[6],
                    'confidence': float(row[7]) if row[7] else 0.9
                })

            cur.close()
            conn.close()

            logger.info(f" Loaded {len(scenarios)} scenarios from database")
            return scenarios

        except Exception as e:
            logger.error(f"Ошибка загрузки сценариев из БД: {e}")
            # Fallback to JSON file
            try:
                scenarios_file = os.path.join(
                    settings.SCENARIOS_PATH,
                    "scenarios_parsed.json"
                )
                if os.path.exists(scenarios_file):
                    with open(scenarios_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
            except:
                pass
            return []

    async def _count_user_gaps(self) -> int:
        """Подсчет вопросов пользователей без ответов"""
        # В production - запрос к Analytics
        return 23  # Заглушка

    async def _count_scenario_usage(self, scenarios: List[Dict]) -> int:
        """Подсчет использованных сценариев"""
        # В production - запрос к Usage Analytics
        return len(scenarios) // 2  # ~50% используются

    async def _get_platform_endpoints(self) -> List[str]:
        """Получение списка endpoint'ов платформы"""
        # В production - из Service Registry
        return []

    async def _get_user_questions(self) -> List[Dict]:
        """Получение вопросов пользователей"""
        # В production - из Support/Analytics логов
        return [
            {"text": "Как провести BIA с помощью AI?", "frequency": 8},
            {"text": "Как создать план восстановления?", "frequency": 7},
            {"text": "Как оценить риски?", "frequency": 6}
        ]

    def _calculate_standard_priority(self, clause: str) -> int:
        """Расчет приоритета пробела стандарта"""
        # Критичные разделы (8.x - операции)
        if clause.startswith('8.'):
            return 10
        # Планирование (6.x)
        elif clause.startswith('6.'):
            return 9
        # Оценка (9.x)
        elif clause.startswith('9.'):
            return 8
        else:
            return 7

    def _calculate_capability_priority(self, service: str) -> int:
        """Расчет приоритета пробела возможностей"""
        # Основные сервисы - высокий приоритет
        core_services = ["BIA", "Risk", "Planning", "Response"]
        if service in core_services:
            return 9
        else:
            return 7

    async def _count_generated_today(self) -> int:
        """Сценарии, сгенерированные сегодня"""
        # В production - запрос к БД
        return 3

    async def _count_generated_this_week(self) -> int:
        return 12

    async def _count_generated_this_month(self) -> int:
        return 45

    async def _count_approved_today(self) -> int:
        return 2

    async def _measure_search_latency(self) -> float:
        """Измерение задержки поиска"""
        # В production - реальные замеры
        return 45.0  # ms

    async def _get_cache_hit_rate(self) -> float:
        """Процент попаданий в кэш"""
        # В production - из Redis
        return 0.72

    async def get_gaps_by_ids(self, gap_ids: List[str]) -> List[KnowledgeGap]:
        """Получение пробелов по ID"""
        all_gaps = await self.detect_gaps()
        return [g for g in all_gaps if g.id in gap_ids]
