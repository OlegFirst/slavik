"""
🔄 PDCA Rules Engine для Workflow Intelligence Core

Это НЕ отдельный модуль - это ПРАВИЛА как Workflow Engine должен работать.
Каждый workflow автоматически проходит через PDCA цикл.

Usage:
    from workflow_intelligence.core import workflow_engine, pdca_rules

    # Автоматически применяет PDCA правила ко всем workflows
    pdca_rules.enable(workflow_engine)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# PDCA CYCLE DATA STRUCTURES
# ============================================================================

@dataclass
class PDCACycleData:
    """Данные одного PDCA цикла workflow"""

    workflow_id: str
    module: str
    cycle_started_at: datetime

    # PLAN phase
    plan_data: Dict[str, Any]  # Что планировали (expected outcomes)
    plan_recommendations: List[str]  # AI рекомендации из прошлых кейсов

    # DO phase
    do_data: Dict[str, Any]  # Что сделали (execution data)
    do_duration: Optional[float] = None  # Сколько времени заняло

    # CHECK phase
    check_data: Dict[str, Any] = None  # Что проверили
    deviations: List[str] = None  # Где отклонились от плана
    benchmarks: Dict[str, float] = None  # Сравнение с другими

    # ACT phase
    lessons_learned: List[str] = None  # Какие уроки извлекли
    patterns_detected: List[str] = None  # Какие паттерны нашли
    improvements: List[str] = None  # Что улучшить

    cycle_completed_at: Optional[datetime] = None


# ============================================================================
# PDCA RULES ENGINE
# ============================================================================

class PDCARulesEngine:
    """
    Правила PDCA для Workflow Intelligence Core

    НЕ делает workflow logic - только добавляет PDCA слой поверх!
    """

    def __init__(self):
        self.active_cycles: Dict[str, PDCACycleData] = {}
        self.completed_cycles: List[PDCACycleData] = []

        # Интеграции (опционально)
        self.case_library = None
        self.knowledge_base = None
        self.pattern_detector = None

    # ========================================================================
    # PLAN PHASE
    # ========================================================================

    async def plan_workflow(
        self,
        workflow_id: str,
        module: str,
        workflow_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        PLAN phase: Подготовить workflow на основе прошлых кейсов

        Returns:
            plan_data с рекомендациями AI
        """
        logger.info(f"[PDCA PLAN] workflow_id={workflow_id}, module={module}")

        # Найти похожие прошлые workflows
        similar_cases = await self._find_similar_cases(module, workflow_data)

        # Извлечь best practices
        recommendations = await self._extract_recommendations(similar_cases)

        # Создать PDCA cycle
        cycle = PDCACycleData(
            workflow_id=workflow_id,
            module=module,
            cycle_started_at=datetime.utcnow(),
            plan_data={
                "workflow_data": workflow_data,
                "expected_outcomes": self._predict_outcomes(similar_cases),
                "estimated_duration": self._estimate_duration(similar_cases)
            },
            plan_recommendations=recommendations
        )

        self.active_cycles[workflow_id] = cycle

        return {
            "recommendations": recommendations,
            "expected_outcomes": cycle.plan_data["expected_outcomes"],
            "estimated_duration": cycle.plan_data["estimated_duration"]
        }

    # ========================================================================
    # DO PHASE
    # ========================================================================

    async def track_execution(
        self,
        workflow_id: str,
        execution_data: Dict[str, Any]
    ):
        """
        DO phase: Отслеживать выполнение workflow

        Вызывается когда workflow прогрессирует
        """
        logger.info(f"[PDCA DO] workflow_id={workflow_id}")

        cycle = self.active_cycles.get(workflow_id)
        if not cycle:
            logger.warning(f"No active cycle for workflow {workflow_id}")
            return

        # Обновить DO data
        cycle.do_data = execution_data
        cycle.do_duration = (
            datetime.utcnow() - cycle.cycle_started_at
        ).total_seconds()

    # ========================================================================
    # CHECK PHASE
    # ========================================================================

    async def check_workflow(
        self,
        workflow_id: str,
        final_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        CHECK phase: Валидировать результат vs план

        Returns:
            validation_report с deviations и benchmarks
        """
        logger.info(f"[PDCA CHECK] workflow_id={workflow_id}")

        cycle = self.active_cycles.get(workflow_id)
        if not cycle:
            logger.warning(f"No active cycle for workflow {workflow_id}")
            return {}

        # Сравнить план vs факт
        deviations = self._find_deviations(
            planned=cycle.plan_data,
            actual=final_data
        )

        # Сравнить с benchmarks
        benchmarks = await self._get_benchmarks(cycle.module, final_data)

        # Сохранить CHECK data
        cycle.check_data = final_data
        cycle.deviations = deviations
        cycle.benchmarks = benchmarks

        return {
            "deviations": deviations,
            "benchmarks": benchmarks,
            "overall_score": self._calculate_score(deviations, benchmarks)
        }

    # ========================================================================
    # ACT PHASE
    # ========================================================================

    async def complete_cycle(
        self,
        workflow_id: str
    ) -> Dict[str, Any]:
        """
        ACT phase: Завершить цикл и извлечь уроки

        Returns:
            lessons_learned и improvements
        """
        logger.info(f"[PDCA ACT] workflow_id={workflow_id}")

        cycle = self.active_cycles.pop(workflow_id, None)
        if not cycle:
            logger.warning(f"No active cycle for workflow {workflow_id}")
            return {}

        # Извлечь уроки
        lessons = await self._extract_lessons(cycle)

        # Детектировать паттерны
        patterns = await self._detect_patterns(cycle)

        # Предложить улучшения
        improvements = await self._suggest_improvements(cycle)

        # Сохранить в cycle
        cycle.lessons_learned = lessons
        cycle.patterns_detected = patterns
        cycle.improvements = improvements
        cycle.cycle_completed_at = datetime.utcnow()

        # Архивировать
        self.completed_cycles.append(cycle)

        # Сохранить в knowledge base (если интеграция есть)
        await self._save_to_knowledge_base(cycle)

        return {
            "lessons": lessons,
            "patterns": patterns,
            "improvements": improvements,
            "cycle_duration": cycle.do_duration
        }

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    async def _find_similar_cases(
        self,
        module: str,
        workflow_data: Dict[str, Any]
    ) -> List[Dict]:
        """Найти похожие прошлые workflows"""

        # Если Case Library интегрирован
        if self.case_library:
            try:
                cases = await self.case_library.find_cases(
                    problem_type=module,
                    min_success_rate=0.8,
                    limit=10
                )
                return cases
            except Exception as e:
                logger.error(f"Case library error: {e}")

        # Fallback: Ищем в completed cycles
        similar = [
            {
                "plan_data": c.plan_data,
                "do_data": c.do_data,
                "lessons": c.lessons_learned,
                "success": len(c.deviations or []) < 3  # < 3 deviations = success
            }
            for c in self.completed_cycles[-50:]  # Last 50 cycles
            if c.module == module
        ]

        return similar

    async def _extract_recommendations(
        self,
        similar_cases: List[Dict]
    ) -> List[str]:
        """Извлечь рекомендации из похожих кейсов"""

        recommendations = []

        # Собрать lessons из успешных кейсов
        for case in similar_cases:
            if case.get("success"):
                recommendations.extend(case.get("lessons", []))

        # Убрать дубликаты
        return list(set(recommendations))[:5]  # Top 5

    def _predict_outcomes(
        self,
        similar_cases: List[Dict]
    ) -> Dict[str, Any]:
        """Предсказать результаты на основе похожих"""

        if not similar_cases:
            return {}

        # Простое усреднение (можно улучшить ML моделью)
        outcomes = {}

        # Пример: Average completion time
        durations = [c.get("do_duration") for c in similar_cases if c.get("do_duration")]
        if durations:
            outcomes["expected_duration_seconds"] = sum(durations) / len(durations)

        return outcomes

    def _estimate_duration(
        self,
        similar_cases: List[Dict]
    ) -> Optional[float]:
        """Оценить продолжительность"""

        durations = [c.get("do_duration") for c in similar_cases if c.get("do_duration")]

        if durations:
            return sum(durations) / len(durations)  # Average

        return None

    def _find_deviations(
        self,
        planned: Dict[str, Any],
        actual: Dict[str, Any]
    ) -> List[str]:
        """Найти отклонения от плана"""

        deviations = []

        # Duration deviation
        expected_duration = planned.get("estimated_duration")
        actual_duration = actual.get("duration")

        if expected_duration and actual_duration:
            if actual_duration > expected_duration * 1.2:  # 20% slower
                deviations.append(
                    f"Duration exceeded: {actual_duration}s vs {expected_duration}s expected"
                )

        # Можно добавить другие метрики...

        return deviations

    async def _get_benchmarks(
        self,
        module: str,
        final_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Получить benchmarks для сравнения"""

        # Простой расчет из completed cycles
        module_cycles = [c for c in self.completed_cycles if c.module == module]

        if not module_cycles:
            return {}

        durations = [c.do_duration for c in module_cycles if c.do_duration]

        return {
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0
        }

    def _calculate_score(
        self,
        deviations: List[str],
        benchmarks: Dict[str, float]
    ) -> float:
        """Рассчитать общий score (0-100)"""

        # Простой scoring: меньше deviations = выше score
        base_score = 100
        penalty_per_deviation = 10

        score = max(0, base_score - len(deviations) * penalty_per_deviation)

        return score

    async def _extract_lessons(
        self,
        cycle: PDCACycleData
    ) -> List[str]:
        """Извлечь уроки из цикла"""

        lessons = []

        # Если Pattern Detector интегрирован
        if self.pattern_detector:
            try:
                detected = await self.pattern_detector.detect_patterns({
                    "plan": cycle.plan_data,
                    "do": cycle.do_data,
                    "check": cycle.check_data
                })
                lessons.extend([p.get("description") for p in detected])
            except Exception as e:
                logger.error(f"Pattern detector error: {e}")

        # Простые эвристики
        if cycle.deviations:
            for deviation in cycle.deviations:
                lessons.append(f"Issue found: {deviation}")

        if not cycle.deviations:
            lessons.append("Workflow completed successfully with no deviations")

        return lessons

    async def _detect_patterns(
        self,
        cycle: PDCACycleData
    ) -> List[str]:
        """Детектировать паттерны"""

        patterns = []

        # Проверить на успешные паттерны
        if len(cycle.deviations or []) == 0:
            patterns.append(f"{cycle.module}_success_pattern")

        # Проверить на повторяющиеся проблемы
        recent_cycles = [
            c for c in self.completed_cycles[-10:]
            if c.module == cycle.module
        ]

        common_deviations = set()
        for c in recent_cycles:
            for dev in (c.deviations or []):
                if dev in (cycle.deviations or []):
                    common_deviations.add(dev)

        if common_deviations:
            patterns.append(f"Recurring issue detected: {list(common_deviations)[0]}")

        return patterns

    async def _suggest_improvements(
        self,
        cycle: PDCACycleData
    ) -> List[str]:
        """Предложить улучшения"""

        improvements = []

        # На основе deviations
        if cycle.deviations:
            improvements.append("Review and update estimated timelines")

        # На основе benchmarks
        if cycle.benchmarks:
            avg_duration = cycle.benchmarks.get("avg_duration", 0)
            if cycle.do_duration and cycle.do_duration > avg_duration * 1.5:
                improvements.append("Optimize workflow execution time")

        return improvements

    async def _save_to_knowledge_base(
        self,
        cycle: PDCACycleData
    ):
        """Сохранить цикл в knowledge base"""

        if not self.knowledge_base:
            return

        try:
            await self.knowledge_base.save_lesson({
                "source": "workflow_pdca",
                "module": cycle.module,
                "lessons": cycle.lessons_learned,
                "patterns": cycle.patterns_detected,
                "improvements": cycle.improvements,
                "metadata": {
                    "workflow_id": cycle.workflow_id,
                    "duration": cycle.do_duration,
                    "deviations_count": len(cycle.deviations or [])
                }
            })
        except Exception as e:
            logger.error(f"Knowledge base save error: {e}")

    # ========================================================================
    # INTEGRATION SETUP
    # ========================================================================

    def integrate_case_library(self, case_library):
        """Интегрировать Case Library"""
        self.case_library = case_library
        logger.info("Case Library integrated")

    def integrate_knowledge_base(self, knowledge_base):
        """Интегрировать Knowledge Base"""
        self.knowledge_base = knowledge_base
        logger.info("Knowledge Base integrated")

    def integrate_pattern_detector(self, pattern_detector):
        """Интегрировать Pattern Detector"""
        self.pattern_detector = pattern_detector
        logger.info("Pattern Detector integrated")


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

# Singleton instance
pdca_rules = PDCARulesEngine()


# ============================================================================
# INTEGRATION HELPER
# ============================================================================

def enable_pdca_for_workflow_engine(workflow_engine):
    """
    Enable PDCA rules для Workflow Engine

    Usage:
        from workflow_intelligence.core import workflow_engine
        from workflow_intelligence.core.pdca_rules import enable_pdca_for_workflow_engine

        enable_pdca_for_workflow_engine(workflow_engine)

        # Теперь все workflows автоматически проходят через PDCA!
    """

    # Subscribe to workflow events
    from .workflow_engine import event_bus

    @event_bus.subscribe("workflow.started")
    async def on_workflow_started(event):
        await pdca_rules.plan_workflow(
            workflow_id=event.workflow_id,
            module=event.module,
            workflow_data=event.data
        )

    @event_bus.subscribe("workflow.stage.changed")
    async def on_stage_changed(event):
        await pdca_rules.track_execution(
            workflow_id=event.workflow_id,
            execution_data=event.data
        )

    @event_bus.subscribe("workflow.completed")
    async def on_workflow_completed(event):
        # CHECK phase
        check_result = await pdca_rules.check_workflow(
            workflow_id=event.workflow_id,
            final_data=event.data
        )

        # ACT phase
        lessons = await pdca_rules.complete_cycle(
            workflow_id=event.workflow_id
        )

        logger.info(
            f"PDCA cycle completed for workflow {event.workflow_id}",
            extra={"lessons": lessons, "check_result": check_result}
        )

    logger.info("PDCA rules enabled for Workflow Engine")
