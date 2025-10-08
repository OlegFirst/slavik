"""
Reaction Rules Engine - Decision Logic for Automated Responses

Классифицирует события и определяет уровень реагирования:
- L1 (Instant): Известные проблемы, низкий risk, автоматическое решение
- L2 (Quick): Есть правило, medium risk, быстрое действие
- L3 (Escalate): Сложные проблемы, нужен мозг
"""

import logging
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ReactionLevel(str, Enum):
    """Уровни реагирования"""
    L1_INSTANT = "L1_instant"      # <10s - автоматический рефлекс
    L2_QUICK = "L2_quick"          # <1min - быстрое действие по правилу
    L3_ESCALATE = "L3_escalate"    # Нужен мозг


class ProblemSeverity(str, Enum):
    """Серьёзность проблемы"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class RiskLevel(str, Enum):
    """Уровень риска действия"""
    LOW = "low"        # Безопасно, обратимо
    MEDIUM = "medium"  # Требует осторожности
    HIGH = "high"      # Может навредить
    CRITICAL = "critical"  # Очень опасно


@dataclass
class ProblemClassification:
    """Классификация проблемы"""
    problem_type: str
    severity: ProblemSeverity
    is_known: bool
    has_auto_solution: bool
    solution_risk: Optional[RiskLevel]
    reaction_level: ReactionLevel
    recommended_action: Optional[str]
    reasoning: str


class ReactionRulesEngine:
    """
    Движок правил реагирования

    Определяет КАК реагировать на каждую проблему на основе:
    - Типа проблемы
    - Серьёзности
    - Известности (видели раньше?)
    - Наличия решения
    - Риска действия
    """

    def __init__(self):
        """Инициализация"""
        self.known_problems = self._init_known_problems()
        self.auto_solutions = self._init_auto_solutions()
        self.rules = self._init_rules()

    def _init_known_problems(self) -> Dict[str, Dict]:
        """
        Инициализация базы известных проблем

        Каждая проблема описывает:
        - pattern: Как распознать
        - severity: Насколько серьёзно
        - frequency: Как часто встречается
        - impact: Какой impact
        """
        return {
            "service_down": {
                "pattern": {
                    "type": "service_health",
                    "status": "down"
                },
                "severity": ProblemSeverity.HIGH,
                "frequency": "common",
                "impact": "service_unavailable"
            },

            "disk_full": {
                "pattern": {
                    "type": "resource",
                    "resource": "disk",
                    "threshold_exceeded": True
                },
                "severity": ProblemSeverity.HIGH,
                "frequency": "common",
                "impact": "service_degradation"
            },

            "high_memory": {
                "pattern": {
                    "type": "resource",
                    "resource": "memory",
                    "usage": ">90%"
                },
                "severity": ProblemSeverity.MEDIUM,
                "frequency": "common",
                "impact": "performance_degradation"
            },

            "high_cpu": {
                "pattern": {
                    "type": "resource",
                    "resource": "cpu",
                    "usage": ">80%"
                },
                "severity": ProblemSeverity.MEDIUM,
                "frequency": "common",
                "impact": "performance_degradation"
            },

            "predicted_load_spike": {
                "pattern": {
                    "type": "prediction",
                    "event": "load_spike"
                },
                "severity": ProblemSeverity.MEDIUM,
                "frequency": "occasional",
                "impact": "potential_overload"
            }
        }

    def _init_auto_solutions(self) -> Dict[str, Dict]:
        """
        Инициализация автоматических решений

        Каждое решение описывает:
        - action: Что делать
        - risk: Уровень риска
        - max_attempts: Макс попыток
        - success_rate: Историческая успешность
        """
        return {
            "service_down": {
                "action": "restart_service",
                "risk": RiskLevel.LOW,
                "max_attempts": 3,
                "success_rate": 0.95,
                "level": ReactionLevel.L1_INSTANT
            },

            "disk_full": {
                "action": "cleanup_old_files",
                "risk": RiskLevel.LOW,
                "targets": ["logs", "temp", "cache"],
                "success_rate": 0.90,
                "level": ReactionLevel.L1_INSTANT
            },

            "high_memory": {
                "action": "trigger_garbage_collection",
                "risk": RiskLevel.LOW,
                "success_rate": 0.85,
                "level": ReactionLevel.L1_INSTANT
            },

            "high_cpu": {
                "action": "investigate_processes",
                "risk": RiskLevel.LOW,
                "level": ReactionLevel.L2_QUICK
            },

            "predicted_load_spike": {
                "action": "scale_up_preventively",
                "risk": RiskLevel.MEDIUM,
                "success_rate": 0.80,
                "level": ReactionLevel.L2_QUICK
            }
        }

    def _init_rules(self) -> List[Dict]:
        """
        Инициализация правил классификации

        Правила применяются в порядке priority (выше = раньше)
        """
        return [
            {
                "name": "critical_always_escalate",
                "priority": 100,
                "condition": lambda p: p.get("severity") == ProblemSeverity.CRITICAL,
                "action": ReactionLevel.L3_ESCALATE,
                "reasoning": "Critical severity - always escalate to Brain"
            },

            {
                "name": "unknown_pattern_escalate",
                "priority": 90,
                "condition": lambda p: not self.is_known_problem(p),
                "action": ReactionLevel.L3_ESCALATE,
                "reasoning": "Unknown problem pattern - need Brain analysis"
            },

            {
                "name": "high_risk_escalate",
                "priority": 80,
                "condition": lambda p: self.get_solution_risk(p) in [RiskLevel.HIGH, RiskLevel.CRITICAL],
                "action": ReactionLevel.L3_ESCALATE,
                "reasoning": "High risk action - need Brain approval"
            },

            {
                "name": "known_low_risk_instant",
                "priority": 70,
                "condition": lambda p: (
                    self.is_known_problem(p) and
                    self.has_auto_solution(p) and
                    self.get_solution_risk(p) == RiskLevel.LOW
                ),
                "action": ReactionLevel.L1_INSTANT,
                "reasoning": "Known problem with safe auto-solution"
            },

            {
                "name": "known_medium_risk_quick",
                "priority": 60,
                "condition": lambda p: (
                    self.is_known_problem(p) and
                    self.has_auto_solution(p) and
                    self.get_solution_risk(p) == RiskLevel.MEDIUM
                ),
                "action": ReactionLevel.L2_QUICK,
                "reasoning": "Known problem with medium-risk solution"
            },

            {
                "name": "default_escalate",
                "priority": 0,
                "condition": lambda p: True,
                "action": ReactionLevel.L3_ESCALATE,
                "reasoning": "No matching rule - escalate by default"
            }
        ]

    def classify_problem(self, problem: Dict[str, Any]) -> ProblemClassification:
        """
        Классифицирует проблему и определяет уровень реагирования

        Args:
            problem: Описание проблемы

        Returns:
            ProblemClassification с решением
        """
        try:
            # Определяем тип и severity
            problem_type = problem.get("type", "unknown")
            severity = self._determine_severity(problem)

            # Проверяем известность
            is_known = self.is_known_problem(problem)

            # Проверяем наличие автоматического решения
            has_solution = self.has_auto_solution(problem)
            solution_risk = self.get_solution_risk(problem) if has_solution else None

            # Применяем правила
            reaction_level, reasoning = self._apply_rules(problem)

            # Рекомендуемое действие
            recommended_action = None
            if reaction_level in [ReactionLevel.L1_INSTANT, ReactionLevel.L2_QUICK]:
                recommended_action = self.auto_solutions.get(problem_type, {}).get("action")

            classification = ProblemClassification(
                problem_type=problem_type,
                severity=severity,
                is_known=is_known,
                has_auto_solution=has_solution,
                solution_risk=solution_risk,
                reaction_level=reaction_level,
                recommended_action=recommended_action,
                reasoning=reasoning
            )

            logger.info(f"Problem classified: {problem_type} -> {reaction_level.value} ({reasoning})")

            return classification

        except Exception as e:
            logger.error(f"Error classifying problem: {e}")
            # Safe fallback - escalate неизвестное
            return ProblemClassification(
                problem_type="unknown",
                severity=ProblemSeverity.HIGH,
                is_known=False,
                has_auto_solution=False,
                solution_risk=None,
                reaction_level=ReactionLevel.L3_ESCALATE,
                recommended_action=None,
                reasoning=f"Classification error: {e}"
            )

    def _determine_severity(self, problem: Dict[str, Any]) -> ProblemSeverity:
        """Определяет серьёзность проблемы"""
        # Явно указана
        if "severity" in problem:
            return ProblemSeverity(problem["severity"])

        # По типу проблемы
        problem_type = problem.get("type")
        if problem_type in self.known_problems:
            return self.known_problems[problem_type]["severity"]

        # По умолчанию - medium
        return ProblemSeverity.MEDIUM

    def is_known_problem(self, problem: Dict[str, Any]) -> bool:
        """Проверяет известна ли проблема"""
        problem_type = problem.get("type")
        return problem_type in self.known_problems

    def has_auto_solution(self, problem: Dict[str, Any]) -> bool:
        """Проверяет есть ли автоматическое решение"""
        problem_type = problem.get("type")
        return problem_type in self.auto_solutions

    def get_solution_risk(self, problem: Dict[str, Any]) -> Optional[RiskLevel]:
        """Возвращает уровень риска решения"""
        problem_type = problem.get("type")
        if problem_type in self.auto_solutions:
            return self.auto_solutions[problem_type].get("risk")
        return None

    def _apply_rules(self, problem: Dict[str, Any]) -> tuple[ReactionLevel, str]:
        """
        Применяет правила классификации

        Returns:
            (reaction_level, reasoning)
        """
        # Сортируем по priority
        sorted_rules = sorted(self.rules, key=lambda r: r["priority"], reverse=True)

        # Применяем первое подходящее
        for rule in sorted_rules:
            if rule["condition"](problem):
                return rule["action"], rule["reasoning"]

        # Не должны сюда попасть (есть default rule)
        return ReactionLevel.L3_ESCALATE, "No matching rule (fallback)"

    def get_action_for_problem(self, problem_type: str) -> Optional[str]:
        """Возвращает рекомендуемое действие для типа проблемы"""
        if problem_type in self.auto_solutions:
            return self.auto_solutions[problem_type]["action"]
        return None

    def get_max_attempts(self, problem_type: str) -> int:
        """Возвращает макс попыток для действия"""
        if problem_type in self.auto_solutions:
            return self.auto_solutions[problem_type].get("max_attempts", 1)
        return 1

    def update_rule(self, problem_type: str, updates: Dict[str, Any]):
        """
        Обновляет правило (для learning)

        Args:
            problem_type: Тип проблемы
            updates: Что обновить (success_rate, risk, etc.)
        """
        if problem_type in self.auto_solutions:
            self.auto_solutions[problem_type].update(updates)
            logger.info(f"Updated rule for {problem_type}: {updates}")

    def add_new_problem(self, problem_type: str, definition: Dict[str, Any]):
        """
        Добавляет новый тип проблемы (learning)

        Args:
            problem_type: Название типа
            definition: Определение проблемы
        """
        self.known_problems[problem_type] = definition
        logger.info(f"Added new problem type: {problem_type}")

    def add_new_solution(self, problem_type: str, solution: Dict[str, Any]):
        """
        Добавляет новое автоматическое решение (learning)

        Args:
            problem_type: Для какой проблемы
            solution: Описание решения
        """
        self.auto_solutions[problem_type] = solution
        logger.info(f"Added new solution for {problem_type}: {solution['action']}")
