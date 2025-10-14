"""
Adaptive Metrics & Priority Framework for AI Office Orchestrator
==================================================================

Адаптивная система метрик и приоритетов, которая:
1. Отслеживает производительность оркестратора в реальном времени
2. Динамически адаптирует приоритеты задач на основе метрик
3. Интегрируется с существующей системой мониторинга
4. Предоставляет рекомендации по оптимизации

Архитектура:
    AdaptiveMetricsCollector - Сбор метрик из разных источников
        ↓
    PriorityEngine - Расчет приоритетов на основе метрик
        ↓
    AdaptiveOrchestrator - Оркестрация с учетом приоритетов
"""

import time
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import deque, defaultdict
import logging
import httpx

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA MODELS
# ============================================================================

class TaskPriority(Enum):
    """Уровни приоритета задач"""
    CRITICAL = 5    # Критические задачи (сбои инфраструктуры, безопасность)
    HIGH = 4        # Высокий приоритет (деплой, масштабирование)
    NORMAL = 3      # Обычный приоритет (обновления, оптимизации)
    LOW = 2         # Низкий приоритет (фоновые задачи, аналитика)
    IDLE = 1        # Задачи для простоя (очистка, архивирование)


class MetricThreshold(Enum):
    """Пороговые значения для метрик"""
    CPU_CRITICAL = 90       # CPU > 90% - критично
    CPU_WARNING = 70        # CPU > 70% - предупреждение
    MEMORY_CRITICAL = 85    # Memory > 85% - критично
    MEMORY_WARNING = 70     # Memory > 70% - предупреждение
    LATENCY_CRITICAL = 5.0  # Latency > 5s - критично
    LATENCY_WARNING = 2.0   # Latency > 2s - предупреждение
    ERROR_RATE_CRITICAL = 5 # Error rate > 5% - критично
    ERROR_RATE_WARNING = 2  # Error rate > 2% - предупреждение


@dataclass
class OrchestratorMetrics:
    """Текущие метрики оркестратора"""
    # Performance
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    active_tasks: int = 0
    queue_length: int = 0

    # Quality
    success_rate: float = 100.0
    error_rate: float = 0.0
    avg_latency: float = 0.0
    p95_latency: float = 0.0

    # Throughput
    tasks_per_minute: float = 0.0
    requests_per_second: float = 0.0

    # Cost
    cost_per_hour: float = 0.0
    total_cost: float = 0.0

    # Timestamp
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def is_healthy(self) -> bool:
        """Проверка здоровья системы"""
        return (
            self.cpu_percent < MetricThreshold.CPU_CRITICAL.value and
            self.memory_percent < MetricThreshold.MEMORY_CRITICAL.value and
            self.p95_latency < MetricThreshold.LATENCY_CRITICAL.value and
            self.error_rate < MetricThreshold.ERROR_RATE_CRITICAL.value
        )

    def get_health_status(self) -> str:
        """Получить статус здоровья"""
        if self.is_healthy():
            if (self.cpu_percent > MetricThreshold.CPU_WARNING.value or
                self.memory_percent > MetricThreshold.MEMORY_WARNING.value or
                self.p95_latency > MetricThreshold.LATENCY_WARNING.value):
                return "warning"
            return "healthy"
        return "critical"


@dataclass
class TaskContext:
    """Контекст задачи для расчета приоритета"""
    task_id: str
    task_type: str
    base_priority: TaskPriority
    submitted_at: datetime
    deadline: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 0
    estimated_duration: float = 60.0  # seconds
    estimated_cost: float = 0.0
    user_id: Optional[str] = None

    # Calculated fields
    actual_priority: float = 0.0
    priority_factors: Dict[str, float] = field(default_factory=dict)


# ============================================================================
# ADAPTIVE METRICS COLLECTOR
# ============================================================================

class AdaptiveMetricsCollector:
    """
    Сборщик адаптивных метрик

    Собирает данные из:
    1. AI Orchestrator monitoring endpoints
    2. Infrastructure metrics (Docker, system resources)
    3. Task execution history
    """

    def __init__(self, orchestrator_url: str = "http://localhost:8030"):
        self.orchestrator_url = orchestrator_url
        self.metrics_history = deque(maxlen=1000)
        self.task_history = deque(maxlen=5000)

        # Moving averages
        self.avg_latency_5min = 0.0
        self.avg_cpu_5min = 0.0
        self.avg_memory_5min = 0.0

    async def collect_orchestrator_metrics(self) -> OrchestratorMetrics:
        """Собрать метрики из AI Orchestrator"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Получить dashboard data (оптимизированный endpoint)
                response = await client.get(
                    f"{self.orchestrator_url}/api/v1/monitoring/dashboard",
                    params={"window_minutes": 5}
                )

                if response.status_code != 200:
                    logger.warning(f"Failed to fetch orchestrator metrics: {response.status_code}")
                    return OrchestratorMetrics()

                data = response.json()

                # Парсим метрики
                golden = data.get('golden_metrics', {})
                performance = data.get('performance', {})
                tasks = data.get('tasks', {})
                resources = data.get('resources', {})

                metrics = OrchestratorMetrics(
                    cpu_percent=resources.get('cpu_percent', 0.0),
                    memory_percent=resources.get('memory_percent', 0.0),
                    active_tasks=golden.get('active_tasks', 0),
                    queue_length=0,  # TODO: add to monitoring

                    success_rate=golden.get('success_rate_percent', 100.0),
                    error_rate=100.0 - golden.get('success_rate_percent', 100.0),
                    avg_latency=performance.get('avg_latency', 0.0),
                    p95_latency=golden.get('p95_latency_seconds', 0.0),

                    tasks_per_minute=golden.get('throughput_tpm', 0.0),
                    requests_per_second=golden.get('throughput_tpm', 0.0) / 60.0,

                    cost_per_hour=tasks.get('total_cost', 0.0),
                    total_cost=tasks.get('total_cost', 0.0),
                )

                # Добавить в историю
                self.metrics_history.append(metrics)

                # Обновить moving averages
                self._update_moving_averages()

                return metrics

        except Exception as e:
            logger.error(f"Error collecting orchestrator metrics: {e}")
            return OrchestratorMetrics()

    def _update_moving_averages(self):
        """Обновить скользящие средние"""
        if not self.metrics_history:
            return

        # Last 5 minutes (assuming 10s refresh interval)
        recent = list(self.metrics_history)[-30:]

        self.avg_latency_5min = sum(m.avg_latency for m in recent) / len(recent)
        self.avg_cpu_5min = sum(m.cpu_percent for m in recent) / len(recent)
        self.avg_memory_5min = sum(m.memory_percent for m in recent) / len(recent)

    async def collect_infrastructure_metrics(self) -> Dict[str, Any]:
        """Собрать метрики инфраструктуры (Docker, сервисы)"""
        # TODO: Implement Docker metrics collection
        return {
            "containers_running": 0,
            "containers_total": 0,
            "networks": 0,
            "volumes": 0
        }

    def record_task_execution(
        self,
        task_id: str,
        task_type: str,
        duration: float,
        success: bool,
        cost: float = 0.0
    ):
        """Записать выполнение задачи"""
        self.task_history.append({
            "task_id": task_id,
            "task_type": task_type,
            "duration": duration,
            "success": success,
            "cost": cost,
            "timestamp": datetime.utcnow()
        })

    def get_task_statistics(self, task_type: Optional[str] = None) -> Dict[str, Any]:
        """Получить статистику по задачам"""
        if task_type:
            tasks = [t for t in self.task_history if t['task_type'] == task_type]
        else:
            tasks = list(self.task_history)

        if not tasks:
            return {"count": 0}

        successes = sum(1 for t in tasks if t['success'])
        total = len(tasks)

        return {
            "count": total,
            "success_rate": successes / total * 100,
            "avg_duration": sum(t['duration'] for t in tasks) / total,
            "total_cost": sum(t['cost'] for t in tasks)
        }


# ============================================================================
# PRIORITY ENGINE
# ============================================================================

class PriorityEngine:
    """
    Движок расчета приоритетов

    Использует адаптивные факторы:
    1. Текущую нагрузку системы
    2. Дедлайны задач
    3. Историю выполнения
    4. Зависимости между задачами
    5. Стоимость задач
    """

    def __init__(self, metrics_collector: AdaptiveMetricsCollector):
        self.metrics_collector = metrics_collector

        # Веса факторов (настраиваются динамически)
        self.weights = {
            "base_priority": 1.0,       # Базовый приоритет
            "system_load": 0.5,         # Нагрузка системы
            "deadline_urgency": 0.8,    # Срочность по дедлайну
            "retry_penalty": 0.3,       # Штраф за повторы
            "cost_efficiency": 0.2,     # Эффективность по стоимости
            "dependency_bonus": 0.4,    # Бонус для задач с зависимостями
        }

    async def calculate_priority(
        self,
        task: TaskContext,
        current_metrics: OrchestratorMetrics
    ) -> float:
        """
        Рассчитать адаптивный приоритет задачи

        Returns:
            Приоритет от 0.0 до 10.0 (выше = важнее)
        """
        factors = {}

        # 1. Базовый приоритет
        factors['base_priority'] = task.base_priority.value

        # 2. Фактор нагрузки системы
        factors['system_load'] = self._calculate_system_load_factor(current_metrics, task)

        # 3. Срочность по дедлайну
        factors['deadline_urgency'] = self._calculate_deadline_factor(task)

        # 4. Штраф за повторы
        factors['retry_penalty'] = self._calculate_retry_penalty(task)

        # 5. Эффективность по стоимости
        factors['cost_efficiency'] = self._calculate_cost_factor(task)

        # 6. Бонус за зависимости
        factors['dependency_bonus'] = self._calculate_dependency_factor(task)

        # Взвешенная сумма
        total_priority = sum(
            factors[key] * self.weights[key]
            for key in factors
        )

        # Нормализация 0-10
        normalized = max(0.0, min(10.0, total_priority))

        # Сохранить факторы для анализа
        task.actual_priority = normalized
        task.priority_factors = factors

        return normalized

    def _calculate_system_load_factor(
        self,
        metrics: OrchestratorMetrics,
        task: TaskContext
    ) -> float:
        """
        Фактор нагрузки системы

        Логика:
        - Если система перегружена, снижаем приоритет тяжелых задач
        - Если система простаивает, повышаем приоритет отложенных задач
        """
        # Оценка загрузки системы (0-100)
        load_score = (
            metrics.cpu_percent * 0.4 +
            metrics.memory_percent * 0.3 +
            (metrics.active_tasks / max(metrics.active_tasks, 10)) * 100 * 0.3
        )

        # Если система перегружена (>80%)
        if load_score > 80:
            # Снижаем приоритет для тяжелых задач
            if task.estimated_duration > 300:  # >5 min
                return -1.0
            elif task.estimated_duration > 60:  # >1 min
                return -0.5
            else:
                return 0.0

        # Если система простаивает (<30%)
        elif load_score < 30:
            # Повышаем приоритет для отложенных задач
            if task.base_priority == TaskPriority.LOW or task.base_priority == TaskPriority.IDLE:
                return +1.0
            return +0.5

        # Нормальная нагрузка
        return 0.0

    def _calculate_deadline_factor(self, task: TaskContext) -> float:
        """
        Фактор срочности по дедлайну

        Логика:
        - Чем ближе дедлайн, тем выше приоритет
        - Просроченные задачи получают максимальный бонус
        """
        if not task.deadline:
            return 0.0

        now = datetime.utcnow()
        time_until_deadline = (task.deadline - now).total_seconds()

        # Просрочено
        if time_until_deadline < 0:
            return +3.0

        # Осталось менее 5 минут
        elif time_until_deadline < 300:
            return +2.0

        # Осталось менее 30 минут
        elif time_until_deadline < 1800:
            return +1.0

        # Осталось менее 2 часов
        elif time_until_deadline < 7200:
            return +0.5

        return 0.0

    def _calculate_retry_penalty(self, task: TaskContext) -> float:
        """
        Штраф за повторы

        Логика:
        - Первые 1-2 попытки - нормально
        - 3+ попытки - снижаем приоритет (возможно системная проблема)
        """
        if task.retry_count == 0:
            return 0.0
        elif task.retry_count <= 2:
            return +0.2  # Небольшой бонус (повторная попытка важна)
        else:
            return -0.5 * (task.retry_count - 2)  # Штраф растет

    def _calculate_cost_factor(self, task: TaskContext) -> float:
        """
        Фактор эффективности по стоимости

        Логика:
        - Дорогие задачи откладываем на период низкой нагрузки
        - Дешевые задачи можем выполнять всегда
        """
        # Получить среднюю стоимость задач этого типа
        stats = self.metrics_collector.get_task_statistics(task.task_type)
        avg_cost = stats.get('total_cost', 0) / max(stats.get('count', 1), 1)

        if avg_cost == 0:
            return 0.0

        # Если задача значительно дороже средней
        if task.estimated_cost > avg_cost * 2:
            return -0.5

        # Если задача дешевле средней
        elif task.estimated_cost < avg_cost * 0.5:
            return +0.3

        return 0.0

    def _calculate_dependency_factor(self, task: TaskContext) -> float:
        """
        Бонус за зависимости

        Логика:
        - Задачи, от которых зависят другие, получают бонус
        - Количество зависимых задач увеличивает приоритет
        """
        if not task.dependencies:
            return 0.0

        # Бонус зависит от количества зависимых задач
        dependency_count = len(task.dependencies)

        if dependency_count >= 5:
            return +1.5
        elif dependency_count >= 3:
            return +1.0
        elif dependency_count >= 1:
            return +0.5

        return 0.0

    def adapt_weights(self, metrics: OrchestratorMetrics):
        """
        Адаптировать веса факторов на основе текущих метрик

        Динамическая оптимизация:
        - При высокой нагрузке увеличиваем вес system_load
        - При большом количестве просрочек увеличиваем вес deadline_urgency
        - При высокой стоимости увеличиваем вес cost_efficiency
        """
        # Высокая нагрузка - фокус на управлении ресурсами
        if metrics.cpu_percent > 70 or metrics.memory_percent > 70:
            self.weights['system_load'] = 1.0
            self.weights['cost_efficiency'] = 0.5
        else:
            self.weights['system_load'] = 0.5
            self.weights['cost_efficiency'] = 0.2

        # Высокий error rate - фокус на стабильности
        if metrics.error_rate > 5:
            self.weights['retry_penalty'] = 0.8
            self.weights['base_priority'] = 1.5
        else:
            self.weights['retry_penalty'] = 0.3
            self.weights['base_priority'] = 1.0

        logger.debug(f"Adapted weights: {self.weights}")


# ============================================================================
# ADAPTIVE ORCHESTRATOR INTEGRATION
# ============================================================================

class AdaptiveOrchestratorMixin:
    """
    Миксин для интеграции адаптивных метрик в UnifiedOrchestrator

    Добавляет методы:
    - prioritize_task() - расчет приоритета задачи
    - get_next_task() - выбор следующей задачи с учетом приоритета
    - monitor_and_adapt() - фоновый мониторинг и адаптация
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Инициализация адаптивных компонентов
        self.metrics_collector = AdaptiveMetricsCollector()
        self.priority_engine = PriorityEngine(self.metrics_collector)

        # Очередь задач с приоритетами
        self.task_queue: List[TaskContext] = []

        # Фоновая задача мониторинга
        self._monitoring_task: Optional[asyncio.Task] = None
        self._running = False

    async def start_adaptive_monitoring(self):
        """Запустить фоновый мониторинг и адаптацию"""
        if self._running:
            logger.warning("Adaptive monitoring already running")
            return

        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitor_loop())
        logger.info("✅ Adaptive monitoring started")

    async def stop_adaptive_monitoring(self):
        """Остановить фоновый мониторинг"""
        self._running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Adaptive monitoring stopped")

    async def _monitor_loop(self):
        """Цикл мониторинга (каждые 10 секунд)"""
        while self._running:
            try:
                # Собрать метрики
                metrics = await self.metrics_collector.collect_orchestrator_metrics()

                # Адаптировать веса приоритетов
                self.priority_engine.adapt_weights(metrics)

                # Пересчитать приоритеты задач в очереди
                await self._recalculate_queue_priorities(metrics)

                # Логировать состояние
                status = metrics.get_health_status()
                logger.debug(
                    f"Adaptive monitoring: status={status}, "
                    f"cpu={metrics.cpu_percent:.1f}%, "
                    f"mem={metrics.memory_percent:.1f}%, "
                    f"latency_p95={metrics.p95_latency:.2f}s, "
                    f"queue_size={len(self.task_queue)}"
                )

                await asyncio.sleep(10)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)

    async def _recalculate_queue_priorities(self, metrics: OrchestratorMetrics):
        """Пересчитать приоритеты всех задач в очереди"""
        for task in self.task_queue:
            await self.priority_engine.calculate_priority(task, metrics)

        # Отсортировать очередь по приоритету (убывание)
        self.task_queue.sort(key=lambda t: t.actual_priority, reverse=True)

    async def add_task_to_queue(
        self,
        task_id: str,
        task_type: str,
        base_priority: TaskPriority = TaskPriority.NORMAL,
        **kwargs
    ) -> TaskContext:
        """
        Добавить задачу в очередь с расчетом приоритета

        Args:
            task_id: Уникальный ID задачи
            task_type: Тип задачи (deploy, scale, update, etc.)
            base_priority: Базовый приоритет
            **kwargs: Дополнительные параметры (deadline, dependencies, etc.)
        """
        # Создать контекст задачи
        task = TaskContext(
            task_id=task_id,
            task_type=task_type,
            base_priority=base_priority,
            submitted_at=datetime.utcnow(),
            **kwargs
        )

        # Получить текущие метрики
        metrics = await self.metrics_collector.collect_orchestrator_metrics()

        # Рассчитать приоритет
        await self.priority_engine.calculate_priority(task, metrics)

        # Добавить в очередь
        self.task_queue.append(task)

        # Отсортировать
        self.task_queue.sort(key=lambda t: t.actual_priority, reverse=True)

        logger.info(
            f"Task added to queue: {task_id} "
            f"(type={task_type}, priority={task.actual_priority:.2f}, "
            f"position={self.task_queue.index(task) + 1}/{len(self.task_queue)})"
        )

        return task

    async def get_next_task(self) -> Optional[TaskContext]:
        """
        Получить следующую задачу для выполнения

        Учитывает:
        - Приоритет
        - Текущую нагрузку системы
        - Зависимости между задачами
        """
        if not self.task_queue:
            return None

        # Получить метрики
        metrics = await self.metrics_collector.collect_orchestrator_metrics()

        # Если система перегружена, брать только критичные задачи
        if metrics.get_health_status() == "critical":
            for task in self.task_queue:
                if task.base_priority == TaskPriority.CRITICAL:
                    self.task_queue.remove(task)
                    return task
            # Если нет критичных, не брать ничего
            logger.warning("System critical - skipping non-critical tasks")
            return None

        # Обычный режим - взять задачу с наивысшим приоритетом
        task = self.task_queue.pop(0)

        logger.info(
            f"Next task selected: {task.task_id} "
            f"(priority={task.actual_priority:.2f}, factors={task.priority_factors})"
        )

        return task

    async def get_queue_stats(self) -> Dict[str, Any]:
        """Получить статистику очереди задач"""
        if not self.task_queue:
            return {
                "total": 0,
                "by_priority": {},
                "avg_priority": 0.0,
                "oldest_task_age_seconds": 0
            }

        by_priority = defaultdict(int)
        for task in self.task_queue:
            by_priority[task.base_priority.name] += 1

        oldest = min(self.task_queue, key=lambda t: t.submitted_at)
        oldest_age = (datetime.utcnow() - oldest.submitted_at).total_seconds()

        return {
            "total": len(self.task_queue),
            "by_priority": dict(by_priority),
            "avg_priority": sum(t.actual_priority for t in self.task_queue) / len(self.task_queue),
            "oldest_task_age_seconds": oldest_age,
            "top_5_tasks": [
                {
                    "task_id": t.task_id,
                    "type": t.task_type,
                    "priority": t.actual_priority,
                    "age_seconds": (datetime.utcnow() - t.submitted_at).total_seconds()
                }
                for t in self.task_queue[:5]
            ]
        }


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    'TaskPriority',
    'MetricThreshold',
    'OrchestratorMetrics',
    'TaskContext',
    'AdaptiveMetricsCollector',
    'PriorityEngine',
    'AdaptiveOrchestratorMixin',
]
