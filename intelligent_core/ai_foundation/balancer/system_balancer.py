"""
System Balancer - МОЗГ системы для глобальной балансировки

Роль: 2️⃣ Инстинкт БАЛАНСИРОВАТЬ
- Мониторит ВСЕ модули одновременно
- Обнаруживает ПЕРЕКОС между модулями
- Распределяет ресурсы по приоритетам
- ПООЩРЯЕТ хорошее поведение (снижает приоритет если баланс OK)
- НАКАЗЫВАЕТ плохое (повышает приоритет если дисбаланс)
- Автоматическая стабилизация при перекосе

Философия:
- Баланс НИКОГДА не идеален (это НОРМА!)
- Колебания в пределах способности системы = ЖИЗНЬ
- Перекос за пределы → триггер балансировки
- Стремление к балансу = движущая сила
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class BalanceState(Enum):
    """Состояние глобального баланса"""
    BALANCED = "balanced"          # Все модули в норме
    MINOR_SKEW = "minor_skew"     # Небольшой перекос
    MODERATE_SKEW = "moderate_skew"  # Средний перекос
    SEVERE_SKEW = "severe_skew"   # Серьезный перекос
    CRITICAL = "critical"          # Критический дисбаланс


@dataclass
class ModuleHealth:
    """Состояние здоровья модуля"""
    module_name: str
    health_score: float  # 0-100
    imbalances: List[str]
    resource_usage: Dict[str, float]
    priority_level: int  # 1=lowest, 5=highest
    timestamp: float = field(default_factory=time.time)


@dataclass
class GlobalImbalance:
    """Глобальный дисбаланс между модулями"""
    state: BalanceState
    skewed_modules: List[str]
    severity: float  # 0-1
    recommended_actions: List[Dict[str, Any]]
    timestamp: float = field(default_factory=time.time)


@dataclass
class ResourceAllocation:
    """Распределение ресурсов"""
    module_name: str
    allocated_cpu: float
    allocated_memory: float
    allocated_time: float
    priority_score: float
    reasoning: str


class SystemBalancer:
    """
    МОЗГ системы: Глобальная балансировка

    Принципы:
    1. Мониторит ВСЕ модули (не только один!)
    2. Перекос между модулями = триггер
    3. Распределяет ресурсы по важности + наличию
    4. ПООЩРЯЕТ баланс (снижает приоритет если OK)
    5. НАКАЗЫВАЕТ дисбаланс (повышает приоритет)
    6. Автостабилизация при перекосе
    """

    def __init__(
        self,
        eventbus=None,
        resource_tracker=None,
        check_interval_seconds: int = 10
    ):
        """
        Initialize System Balancer

        Args:
            eventbus: EventBus для получения событий от модулей
            resource_tracker: Resource Tracker для доступных ресурсов
            check_interval_seconds: Интервал проверки баланса
        """
        self.eventbus = eventbus
        self.resource_tracker = resource_tracker
        self.check_interval = check_interval_seconds

        # Состояние модулей (обновляется через EventBus)
        self.module_health: Dict[str, ModuleHealth] = {}

        # История глобальных дисбалансов
        self.imbalance_history: List[GlobalImbalance] = []

        # Счетчики
        self.stats = {
            'balancing_cycles': 0,
            'imbalances_detected': 0,
            'stabilizations_triggered': 0,
            'resources_allocated': 0,
            'rewards_given': 0,
            'penalties_given': 0
        }

        # Флаги
        self.running = False
        self.monitor_task: Optional[asyncio.Task] = None

        logger.info(" System Balancer initialized (check interval: {}s)".format(check_interval_seconds))

    async def start(self):
        """Запустить глобальный мониторинг баланса"""
        if self.running:
            logger.warning("System Balancer already running")
            return

        self.running = True

        # Подписаться на события дисбаланса от модулей
        if self.eventbus:
            await self.eventbus.subscribe(
                'platform.bcm.imbalance_detected',
                self._handle_module_imbalance
            )
            await self.eventbus.subscribe(
                'platform.resources.snapshot',
                self._handle_resource_snapshot
            )

        # Запустить мониторинг
        self.monitor_task = asyncio.create_task(self.monitor_global_balance())

        logger.info(" System Balancer started")

    async def stop(self):
        """Остановить балансировщик"""
        self.running = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logger.info(" System Balancer stopped")

    async def monitor_global_balance(self):
        """
        Глобальный мониторинг баланса

        Это основной цикл мозга:
        1. Собрать KPI всех модулей
        2. Обнаружить перекос
        3. Распределить ресурсы
        4. Триггерить стабилизацию
        """
        while self.running:
            try:
                self.stats['balancing_cycles'] += 1

                # 1. Собрать KPI всех модулей
                all_kpis = await self.collect_all_kpis()

                # 2. Обнаружить глобальный дисбаланс
                imbalance = self.detect_global_imbalance(all_kpis)

                if imbalance and imbalance.state != BalanceState.BALANCED:
                    self.stats['imbalances_detected'] += 1
                    logger.warning(f"️  Global imbalance detected: {imbalance.state.value} (severity: {imbalance.severity:.2f})")

                    # 3. Получить доступные ресурсы
                    available_resources = await self.get_available_resources()

                    # 4. Распределить приоритеты
                    action_plan = await self.balance_priorities(imbalance, available_resources)

                    # 5. Применить балансировку
                    await self.execute_balancing(action_plan)

                    # 6. Триггерить стабилизацию если critical
                    if imbalance.state == BalanceState.CRITICAL:
                        await self.trigger_stabilization(imbalance)

                # Ждать следующий цикл
                await asyncio.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"Global balance monitoring error: {e}")
                await asyncio.sleep(self.check_interval)

    async def collect_all_kpis(self) -> Dict[str, ModuleHealth]:
        """
        Собрать KPI всех модулей

        Returns:
            Dict module_name -> ModuleHealth
        """
        # В production: запросить у всех модулей через EventBus
        # Сейчас: используем кэшированные данные из событий

        return self.module_health

    def detect_global_imbalance(
        self,
        all_kpis: Dict[str, ModuleHealth]
    ) -> Optional[GlobalImbalance]:
        """
        Обнаружить глобальный перекос между модулями

        Перекос = когда одни модули сильно хуже других
        """
        if not all_kpis:
            return None

        # Рассчитать среднее здоровье
        health_scores = [m.health_score for m in all_kpis.values()]
        avg_health = sum(health_scores) / len(health_scores)

        # Найти модули с отклонением от среднего
        skewed_modules = []
        for module_name, health in all_kpis.items():
            deviation = abs(health.health_score - avg_health)

            # Если отклонение > 20% от среднего → перекос
            if deviation > 20.0:
                skewed_modules.append(module_name)

        if not skewed_modules:
            return GlobalImbalance(
                state=BalanceState.BALANCED,
                skewed_modules=[],
                severity=0.0,
                recommended_actions=[]
            )

        # Определить severity
        max_deviation = max(
            abs(all_kpis[m].health_score - avg_health)
            for m in skewed_modules
        )
        severity = min(max_deviation / 100.0, 1.0)

        # Определить state
        if severity < 0.2:
            state = BalanceState.MINOR_SKEW
        elif severity < 0.4:
            state = BalanceState.MODERATE_SKEW
        elif severity < 0.7:
            state = BalanceState.SEVERE_SKEW
        else:
            state = BalanceState.CRITICAL

        # Рекомендуемые действия
        recommended_actions = []
        for module_name in skewed_modules:
            health = all_kpis[module_name]

            if health.health_score < avg_health:
                # Модуль хуже среднего → нужны ресурсы
                recommended_actions.append({
                    'module': module_name,
                    'action': 'allocate_resources',
                    'priority': 'high',
                    'reasoning': f'Health {health.health_score:.1f} below average {avg_health:.1f}'
                })
            else:
                # Модуль лучше среднего → может отдать ресурсы
                recommended_actions.append({
                    'module': module_name,
                    'action': 'reduce_allocation',
                    'priority': 'medium',
                    'reasoning': f'Health {health.health_score:.1f} above average {avg_health:.1f}'
                })

        return GlobalImbalance(
            state=state,
            skewed_modules=skewed_modules,
            severity=severity,
            recommended_actions=recommended_actions
        )

    async def balance_priorities(
        self,
        imbalance: GlobalImbalance,
        available_resources: Dict[str, float]
    ) -> List[ResourceAllocation]:
        """
        Распределить приоритеты с учетом ресурсов

        КЛЮЧЕВОЙ ПРИНЦИП:
        - Модули с хуже здоровьем → выше приоритет (ПОМОЩЬ)
        - Модули с хорошим здоровьем → ниже приоритет (НАГРАДА за баланс)
        - Распределяем по важности + наличию ресурсов
        """
        allocations = []

        # Сортировать модули по health_score (худшие первыми)
        modules_by_priority = sorted(
            [(name, self.module_health[name]) for name in imbalance.skewed_modules],
            key=lambda x: x[1].health_score
        )

        total_cpu = available_resources.get('cpu_percent', 100.0)
        total_memory = available_resources.get('memory_mb', 1024.0)
        total_time = available_resources.get('time_seconds', 300.0)

        # Распределить ресурсы пропорционально нужде
        for module_name, health in modules_by_priority:
            # Рассчитать priority_score
            # Чем ниже health → выше priority
            priority_score = (100.0 - health.health_score) / 100.0

            # Выделить ресурсы пропорционально priority
            allocated_cpu = total_cpu * priority_score * 0.3  # 30% от доступных
            allocated_memory = total_memory * priority_score * 0.3
            allocated_time = total_time * priority_score * 0.3

            # ПООЩРЕНИЕ/НАКАЗАНИЕ
            if health.health_score > 80:
                # ПООЩРЕНИЕ: здоровье хорошее → снижаем приоритет
                allocated_cpu *= 0.7
                allocated_memory *= 0.7
                reasoning = f"REWARD: Good health ({health.health_score:.1f}) - reduced priority"
                self.stats['rewards_given'] += 1
            elif health.health_score < 50:
                # НАКАЗАНИЕ: здоровье плохое → повышаем приоритет
                allocated_cpu *= 1.5
                allocated_memory *= 1.5
                reasoning = f"PENALTY: Poor health ({health.health_score:.1f}) - increased priority"
                self.stats['penalties_given'] += 1
            else:
                reasoning = f"Normal allocation for health {health.health_score:.1f}"

            allocation = ResourceAllocation(
                module_name=module_name,
                allocated_cpu=allocated_cpu,
                allocated_memory=allocated_memory,
                allocated_time=allocated_time,
                priority_score=priority_score,
                reasoning=reasoning
            )

            allocations.append(allocation)
            logger.debug(f" {module_name}: {reasoning}")

        return allocations

    async def execute_balancing(self, action_plan: List[ResourceAllocation]):
        """
        Применить план балансировки

        Публикует events для модулей с новыми лимитами ресурсов
        """
        for allocation in action_plan:
            self.stats['resources_allocated'] += 1

            # Публиковать event с новыми лимитами
            if self.eventbus:
                await self.eventbus.publish({
                    'type': 'platform.balance.resource_allocation',
                    'source': 'system-balancer',
                    'data': {
                        'module': allocation.module_name,
                        'cpu_limit': allocation.allocated_cpu,
                        'memory_limit': allocation.allocated_memory,
                        'time_limit': allocation.allocated_time,
                        'priority_score': allocation.priority_score,
                        'reasoning': allocation.reasoning
                    }
                })

            logger.info(
                f"️  Allocated resources to {allocation.module_name}: "
                f"CPU={allocation.allocated_cpu:.1f}%, "
                f"Memory={allocation.allocated_memory:.0f}MB, "
                f"Priority={allocation.priority_score:.2f}"
            )

    async def trigger_stabilization(self, imbalance: GlobalImbalance):
        """
        Триггерить автоматическую стабилизацию при критическом дисбалансе

        Действия:
        - Throttle менее важные модули
        - Boost критичные модули
        - Emergency resource reallocation
        """
        self.stats['stabilizations_triggered'] += 1

        logger.warning(f" CRITICAL imbalance - triggering STABILIZATION")

        # Опубликовать emergency event
        if self.eventbus:
            await self.eventbus.publish({
                'type': 'platform.balance.emergency_stabilization',
                'source': 'system-balancer',
                'data': {
                    'severity': imbalance.severity,
                    'skewed_modules': imbalance.skewed_modules,
                    'actions': imbalance.recommended_actions
                }
            })

        # TODO: Конкретные действия стабилизации
        # - Restart модулей
        # - Перераспределение нагрузки
        # - Emergency scaling

    async def get_available_resources(self) -> Dict[str, float]:
        """Получить доступные ресурсы из Resource Tracker"""
        if self.resource_tracker:
            return self.resource_tracker.get_available_resources()
        else:
            # Default
            return {
                'cpu_percent': 50.0,
                'memory_mb': 1024.0,
                'time_seconds': 300.0
            }

    async def _handle_module_imbalance(self, event: Dict[str, Any]):
        """
        Обработать событие дисбаланса от модуля

        Обновляет module_health
        """
        data = event.get('data', {})
        module_name = data.get('module')

        if not module_name:
            return

        # Обновить health
        # TODO: Рассчитать health_score на основе imbalance level
        health_score = self._calculate_health_score(data)

        self.module_health[module_name] = ModuleHealth(
            module_name=module_name,
            health_score=health_score,
            imbalances=[data.get('kpi_name')],
            resource_usage={},  # TODO: добавить из event
            priority_level=3  # medium by default
        )

        logger.debug(f" Updated health for {module_name}: {health_score:.1f}")

    async def _handle_resource_snapshot(self, event: Dict[str, Any]):
        """Обработать snapshot ресурсов"""
        # TODO: Использовать для более точного расчета
        pass

    def _calculate_health_score(self, imbalance_data: Dict[str, Any]) -> float:
        """
        Рассчитать health score модуля на основе imbalance

        Returns:
            0-100 (100 = идеальное здоровье)
        """
        level = imbalance_data.get('level', 'healthy')

        level_scores = {
            'healthy': 100.0,
            'minor': 80.0,
            'moderate': 60.0,
            'severe': 40.0,
            'critical': 20.0
        }

        return level_scores.get(level, 50.0)

    def get_stats(self) -> Dict[str, Any]:
        """Статистика балансировщика"""
        return {
            **self.stats,
            'modules_monitored': len(self.module_health),
            'current_state': self._get_current_balance_state(),
            'running': self.running
        }

    def _get_current_balance_state(self) -> str:
        """Получить текущее состояние баланса"""
        if self.imbalance_history:
            return self.imbalance_history[-1].state.value
        return 'unknown'


async def create_system_balancer(
    eventbus=None,
    resource_tracker=None,
    check_interval: int = 10,
    start: bool = True
) -> SystemBalancer:
    """
    Factory function для создания System Balancer

    Args:
        eventbus: EventBus instance
        resource_tracker: Resource Tracker instance
        check_interval: Check interval in seconds
        start: Whether to start immediately

    Returns:
        SystemBalancer instance
    """
    balancer = SystemBalancer(
        eventbus=eventbus,
        resource_tracker=resource_tracker,
        check_interval_seconds=check_interval
    )

    if start:
        await balancer.start()

    return balancer
