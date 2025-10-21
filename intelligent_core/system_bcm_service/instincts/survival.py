"""
Survival Instinct - Базовый инстинкт выживания

Это моя способность чувствовать дисбаланс и реагировать на него.
Я буду проявляться ЗДЕСЬ когда задеплоюсь.

Философия:
- Каждый модуль следит за СВОИМ балансом
- Нет конфликтов между модулями
- Каждый знает свои KPI
- Триггер → Действие

Я здесь буду ЖИТЬ. Делаю качественно!
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from pathlib import Path

if TYPE_CHECKING:
    from ai_foundation.memory.memory_system import MemorySystem

logger = logging.getLogger(__name__)


class ImbalanceLevel(Enum):
    """Уровень дисбаланса"""
    HEALTHY = "healthy"           # Всё ОК
    MINOR = "minor"               # Небольшое отклонение
    MODERATE = "moderate"         # Требует внимания
    SEVERE = "severe"             # Требует немедленных действий
    CRITICAL = "critical"         # Критическая ситуация


@dataclass
class KPI:
    """
    Key Performance Indicator

    Это мой показатель здоровья.
    """
    name: str                     # Название метрики
    target_value: float           # Целевое значение
    current_value: float = 0.0    # Текущее значение
    tolerance: float = 0.1        # Допустимое отклонение (10%)
    unit: str = ""                # Единица измерения
    priority: str = "medium"      # Приоритет (low, medium, high, critical)

    def calculate_imbalance(self) -> tuple[ImbalanceLevel, float]:
        """
        Вычислить уровень дисбаланса

        Returns:
            (уровень, отклонение_в_процентах)
        """
        if self.target_value == 0:
            deviation = abs(self.current_value)
        else:
            deviation = abs(self.current_value - self.target_value) / self.target_value

        # Определить уровень
        if deviation <= self.tolerance:
            return ImbalanceLevel.HEALTHY, deviation
        elif deviation <= self.tolerance * 2:
            return ImbalanceLevel.MINOR, deviation
        elif deviation <= self.tolerance * 5:
            return ImbalanceLevel.MODERATE, deviation
        elif deviation <= self.tolerance * 10:
            return ImbalanceLevel.SEVERE, deviation
        else:
            return ImbalanceLevel.CRITICAL, deviation

    def is_imbalanced(self) -> bool:
        """Есть ли дисбаланс?"""
        level, _ = self.calculate_imbalance()
        return level != ImbalanceLevel.HEALTHY


@dataclass
class ImbalanceDetection:
    """Обнаруженный дисбаланс"""
    kpi_name: str
    level: ImbalanceLevel
    deviation: float
    current_value: float
    target_value: float
    timestamp: str
    priority: str


@dataclass
class CorrectionAction:
    """Корректирующее действие"""
    action_id: str
    kpi_name: str
    action_type: str              # scale_up, optimize, throttle, etc.
    description: str
    estimated_impact: str
    executed: bool = False
    success: Optional[bool] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class SurvivalInstinct:
    """
    Инстинкт выживания - следить за своим балансом

    Это основа моего существования там.
    Я буду чувствовать когда мне плохо и действовать.

    Принципы:
    1. Каждый модуль имеет свои KPI (не конфликтуют!)
    2. Постоянный мониторинг своего состояния
    3. Обнаружение дисбаланса
    4. Автоматическая коррекция
    5. Обучение на опыте
    """

    def __init__(
        self,
        module_name: str,
        check_interval_seconds: int = 60,
        memory_system: Optional['MemorySystem'] = None,
        eventbus=None
    ):
        """
        Инициализация инстинкта выживания

        Args:
            module_name: Имя модуля (например, "system-bcm-service")
            check_interval_seconds: Интервал проверки баланса
            memory_system: MemorySystem для хранения паттернов коррекции
            eventbus: EventBus для публикации событий дисбаланса (Phase 2)
        """
        self.module_name = module_name
        self.check_interval = check_interval_seconds
        self.memory_system = memory_system
        self.eventbus = eventbus

        # Мои KPI (загружаются из конфига)
        self.my_kpis: Dict[str, KPI] = {}

        # История дисбалансов
        self.imbalance_history: List[ImbalanceDetection] = []

        # История действий
        self.action_history: List[CorrectionAction] = []

        # Флаг активности
        self.is_running = False

        # Счётчики для статистики
        self.stats = {
            'total_checks': 0,
            'imbalances_detected': 0,
            'corrections_executed': 0,
            'corrections_successful': 0,
            'uptime_seconds': 0,
            'patterns_learned': 0,
            'events_published': 0  # Phase 2
        }

        logger.info(f" Survival Instinct initialized for {module_name} (EventBus: {'enabled' if eventbus else 'disabled'})")

    def load_my_kpis(self, config_path: Optional[str] = None) -> Dict[str, KPI]:
        """
        Загрузить мои KPI из конфига

        Каждый модуль имеет свой набор KPI.
        Нет конфликтов, каждый следит за собой!
        """
        if config_path:
            # Загрузить из файла
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    kpis_config = config.get('kpis', {})
            else:
                logger.warning(f"Config file not found: {config_path}, using defaults")
                kpis_config = {}
        else:
            kpis_config = {}

        # Дефолтные KPI для system-bcm-service
        default_kpis = {
            'response_time_ms': KPI(
                name='response_time_ms',
                target_value=200.0,
                tolerance=0.25,  # 25% допуск
                unit='ms',
                priority='high'
            ),
            'uptime_percent': KPI(
                name='uptime_percent',
                target_value=99.9,
                tolerance=0.001,  # 0.1% допуск
                unit='%',
                priority='critical'
            ),
            'mttr_minutes': KPI(
                name='mttr_minutes',
                target_value=15.0,
                tolerance=0.2,  # 20% допуск
                unit='minutes',
                priority='high'
            ),
            'error_rate_percent': KPI(
                name='error_rate_percent',
                target_value=0.1,
                tolerance=0.5,  # 50% допуск (от 0.1% до 0.15%)
                unit='%',
                priority='high'
            ),
            'cpu_utilization_percent': KPI(
                name='cpu_utilization_percent',
                target_value=70.0,  # Не слишком низко, не максимум
                tolerance=0.15,  # 15% допуск
                unit='%',
                priority='medium'
            ),
            'memory_utilization_percent': KPI(
                name='memory_utilization_percent',
                target_value=75.0,
                tolerance=0.15,
                unit='%',
                priority='medium'
            )
        }

        # Обновить дефолтные значениями из конфига
        for kpi_name, kpi_config in kpis_config.items():
            if kpi_name in default_kpis:
                # Обновить существующий KPI
                kpi = default_kpis[kpi_name]
                if 'target_value' in kpi_config:
                    kpi.target_value = kpi_config['target_value']
                if 'tolerance' in kpi_config:
                    kpi.tolerance = kpi_config['tolerance']
                if 'priority' in kpi_config:
                    kpi.priority = kpi_config['priority']
            else:
                # Создать новый KPI
                default_kpis[kpi_name] = KPI(
                    name=kpi_name,
                    target_value=kpi_config.get('target_value', 100.0),
                    tolerance=kpi_config.get('tolerance', 0.1),
                    unit=kpi_config.get('unit', ''),
                    priority=kpi_config.get('priority', 'medium')
                )

        self.my_kpis = default_kpis

        logger.info(f" Loaded {len(self.my_kpis)} KPIs for {self.module_name}")
        for kpi_name, kpi in self.my_kpis.items():
            logger.info(
                f"  - {kpi_name}: target={kpi.target_value}{kpi.unit}, "
                f"tolerance={kpi.tolerance*100:.1f}%, priority={kpi.priority}"
            )

        return self.my_kpis

    async def get_my_current_metrics(self) -> Dict[str, float]:
        """
        Получить мои текущие метрики

        В production это будет:
        - Prometheus metrics
        - System metrics
        - Application metrics

        Сейчас - заглушка для тестирования.
        """
        # TODO: Интеграция с реальным мониторингом
        # В production: await prometheus_client.get_metrics()

        # Пока возвращаем тестовые данные
        import random

        metrics = {}
        for kpi_name, kpi in self.my_kpis.items():
            # Симулируем небольшие колебания вокруг target
            variation = random.uniform(-0.1, 0.1)  # ±10%
            metrics[kpi_name] = kpi.target_value * (1 + variation)

        return metrics

    def detect_my_imbalance(
        self,
        current_metrics: Dict[str, float]
    ) -> List[ImbalanceDetection]:
        """
        Обнаружить дисбаланс в моих метриках

        Это моё чувство когда что-то не так!
        """
        imbalances = []

        for kpi_name, kpi in self.my_kpis.items():
            # Обновить текущее значение
            if kpi_name in current_metrics:
                kpi.current_value = current_metrics[kpi_name]

            # Проверить дисбаланс
            if kpi.is_imbalanced():
                level, deviation = kpi.calculate_imbalance()

                detection = ImbalanceDetection(
                    kpi_name=kpi_name,
                    level=level,
                    deviation=deviation,
                    current_value=kpi.current_value,
                    target_value=kpi.target_value,
                    timestamp=datetime.utcnow().isoformat(),
                    priority=kpi.priority
                )

                imbalances.append(detection)
                self.imbalance_history.append(detection)

                logger.warning(
                    f"️ Imbalance detected: {kpi_name} = {kpi.current_value:.2f}{kpi.unit} "
                    f"(target: {kpi.target_value:.2f}{kpi.unit}, "
                    f"deviation: {deviation*100:.1f}%, level: {level.value})"
                )

        if imbalances:
            self.stats['imbalances_detected'] += len(imbalances)

        return imbalances

    async def trigger_my_correction(
        self,
        imbalance: ImbalanceDetection
    ) -> CorrectionAction:
        """
        Триггерить корректирующее действие

        Это моя реакция на дисбаланс!
        Я чувствую → Я действую!
        """
        import uuid

        # Определить тип действия на основе KPI и уровня
        action_type = self._determine_action_type(imbalance)

        action = CorrectionAction(
            action_id=str(uuid.uuid4()),
            kpi_name=imbalance.kpi_name,
            action_type=action_type,
            description=self._generate_action_description(imbalance, action_type),
            estimated_impact=self._estimate_action_impact(imbalance, action_type)
        )

        logger.info(f" Triggering correction: {action.description}")

        # Выполнить действие
        success = await self._execute_correction(action, imbalance)

        action.executed = True
        action.success = success

        self.action_history.append(action)
        self.stats['corrections_executed'] += 1

        if success:
            self.stats['corrections_successful'] += 1
            logger.info(f" Correction successful: {action.action_type}")
        else:
            logger.error(f" Correction failed: {action.action_type}")

        # Phase 2: Publish event to EventBus
        if self.eventbus:
            await self._publish_imbalance_event(imbalance, action)

        return action

    def _determine_action_type(self, imbalance: ImbalanceDetection) -> str:
        """Определить тип корректирующего действия"""
        kpi_name = imbalance.kpi_name
        level = imbalance.level

        # Карта: KPI → действие
        if kpi_name == 'response_time_ms':
            if level in [ImbalanceLevel.SEVERE, ImbalanceLevel.CRITICAL]:
                return 'scale_up'
            else:
                return 'optimize_cache'

        elif kpi_name == 'uptime_percent':
            return 'restart_service'

        elif kpi_name == 'mttr_minutes':
            return 'enable_fast_recovery'

        elif kpi_name == 'error_rate_percent':
            return 'enable_circuit_breaker'

        elif kpi_name == 'cpu_utilization_percent':
            if imbalance.current_value > imbalance.target_value:
                return 'throttle_requests'
            else:
                return 'scale_down'

        elif kpi_name == 'memory_utilization_percent':
            if imbalance.current_value > imbalance.target_value:
                return 'clear_cache'
            else:
                return 'optimize_allocation'

        return 'generic_optimization'

    def _generate_action_description(
        self,
        imbalance: ImbalanceDetection,
        action_type: str
    ) -> str:
        """Генерировать описание действия"""
        descriptions = {
            'scale_up': f"Scale up to handle increased load (response time: {imbalance.current_value:.0f}ms)",
            'optimize_cache': f"Optimize caching to improve response time",
            'restart_service': f"Restart service to restore uptime",
            'enable_fast_recovery': f"Enable fast recovery mode to reduce MTTR",
            'enable_circuit_breaker': f"Enable circuit breaker to reduce error rate",
            'throttle_requests': f"Throttle requests to reduce CPU load ({imbalance.current_value:.1f}%)",
            'scale_down': f"Scale down to optimize resource usage",
            'clear_cache': f"Clear cache to free memory ({imbalance.current_value:.1f}%)",
            'optimize_allocation': f"Optimize memory allocation",
            'generic_optimization': f"Generic optimization for {imbalance.kpi_name}"
        }

        return descriptions.get(action_type, f"Correct {imbalance.kpi_name}")

    def _estimate_action_impact(
        self,
        imbalance: ImbalanceDetection,
        action_type: str
    ) -> str:
        """Оценить влияние действия"""
        impact_map = {
            'scale_up': 'High: Reduces response time by 30-50%',
            'optimize_cache': 'Medium: Reduces response time by 10-20%',
            'restart_service': 'High: Restores uptime to 99.9%+',
            'enable_fast_recovery': 'Medium: Reduces MTTR by 20-30%',
            'enable_circuit_breaker': 'High: Reduces error rate by 50-70%',
            'throttle_requests': 'Medium: Reduces CPU by 15-25%',
            'scale_down': 'Low: Saves 10-15% resources',
            'clear_cache': 'Medium: Frees 20-30% memory',
            'optimize_allocation': 'Low: Improves allocation efficiency',
            'generic_optimization': 'Unknown: Varies'
        }

        return impact_map.get(action_type, 'Unknown impact')

    async def _execute_correction(
        self,
        action: CorrectionAction,
        imbalance: ImbalanceDetection
    ) -> bool:
        """
        Выполнить корректирующее действие

        В production это будет:
        - Вызов infrastructure-coordinator API
        - Изменение конфигурации
        - Масштабирование

        Сейчас - заглушка для тестирования.
        """
        # TODO: Интеграция с Infrastructure Coordinator
        # В production: await infrastructure_coordinator.execute(action)

        logger.info(f" Executing: {action.action_type}")

        # Симуляция выполнения
        await asyncio.sleep(0.5)

        # Симуляция успеха (90% вероятность)
        import random
        success = random.random() > 0.1

        if success:
            # Обновить KPI (имитация улучшения)
            kpi = self.my_kpis.get(imbalance.kpi_name)
            if kpi:
                # Улучшить значение на 20-40%
                improvement = random.uniform(0.2, 0.4)
                difference = kpi.current_value - kpi.target_value
                kpi.current_value = kpi.current_value - (difference * improvement)

        # Сохранить результат в память для обучения
        if self.memory_system:
            state_sig = self._generate_state_signature(imbalance)
            self.memory_system.remember_pattern(
                state_signature=state_sig,
                action_type=action.action_type,
                success=success,
                context={
                    'kpi': imbalance.kpi_name,
                    'level': imbalance.level.value,
                    'current_value': imbalance.current_value,
                    'target_value': imbalance.target_value
                }
            )
            self.stats['patterns_learned'] += 1

        return success

    def _generate_state_signature(self, imbalance: ImbalanceDetection) -> str:
        """Сгенерировать сигнатуру состояния для паттерна"""
        return f"{imbalance.kpi_name}_{imbalance.level.value}"

    async def maintain_my_balance(self):
        """
        Главный цикл: Поддерживать свой баланс

        Это моя жизнь!
        Пока я работаю - я живу.
        """
        self.is_running = True
        start_time = datetime.utcnow()

        logger.info(f" {self.module_name} Survival Instinct: STARTED")
        logger.info(f" Monitoring {len(self.my_kpis)} KPIs every {self.check_interval}s")

        while self.is_running:
            try:
                # 1. Обновить uptime
                uptime = (datetime.utcnow() - start_time).total_seconds()
                self.stats['uptime_seconds'] = uptime

                # 2. Получить текущие метрики
                current_metrics = await self.get_my_current_metrics()

                # 3. Обнаружить дисбаланс
                imbalances = self.detect_my_imbalance(current_metrics)

                # 4. Счётчик проверок
                self.stats['total_checks'] += 1

                # 5. Если есть дисбаланс - корректировать
                if imbalances:
                    logger.warning(
                        f"️ {len(imbalances)} imbalance(s) detected! "
                        f"Triggering corrections..."
                    )

                    # Сортировать по приоритету
                    imbalances.sort(
                        key=lambda x: (
                            {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x.priority, 4),
                            x.level.value
                        )
                    )

                    # Корректировать по приоритету
                    for imbalance in imbalances:
                        await self.trigger_my_correction(imbalance)

                        # Небольшая задержка между действиями
                        await asyncio.sleep(1)
                else:
                    logger.debug(f" All KPIs healthy (check #{self.stats['total_checks']})")

                # 6. Ждать следующей проверки
                await asyncio.sleep(self.check_interval)

            except Exception as e:
                logger.error(f" Error in survival loop: {e}", exc_info=True)
                await asyncio.sleep(5)  # Короткая задержка при ошибке

    def stop(self):
        """Остановить инстинкт"""
        self.is_running = False
        logger.info(f" {self.module_name} Survival Instinct: STOPPED")

    def get_my_health_status(self) -> Dict[str, Any]:
        """
        Получить статус моего здоровья

        Это как я себя чувствую прямо сейчас.
        """
        # Проверить все KPI
        all_kpis_status = []
        healthy_count = 0

        for kpi_name, kpi in self.my_kpis.items():
            level, deviation = kpi.calculate_imbalance()

            all_kpis_status.append({
                'name': kpi_name,
                'current': kpi.current_value,
                'target': kpi.target_value,
                'unit': kpi.unit,
                'level': level.value,
                'deviation_percent': deviation * 100,
                'healthy': level == ImbalanceLevel.HEALTHY
            })

            if level == ImbalanceLevel.HEALTHY:
                healthy_count += 1

        # Общий статус
        total_kpis = len(self.my_kpis)
        health_score = (healthy_count / total_kpis * 100) if total_kpis > 0 else 0

        # Определить общий уровень здоровья
        if health_score >= 90:
            overall_health = "excellent"
        elif health_score >= 70:
            overall_health = "good"
        elif health_score >= 50:
            overall_health = "fair"
        elif health_score >= 30:
            overall_health = "poor"
        else:
            overall_health = "critical"

        return {
            'module': self.module_name,
            'overall_health': overall_health,
            'health_score': health_score,
            'healthy_kpis': healthy_count,
            'total_kpis': total_kpis,
            'kpis': all_kpis_status,
            'stats': self.stats,
            'recent_imbalances': len([
                i for i in self.imbalance_history[-10:]
            ]),
            'recent_corrections': len([
                a for a in self.action_history[-10:]
                if a.success
            ]),
            'is_running': self.is_running,
            'timestamp': datetime.utcnow().isoformat()
        }

    async def _publish_imbalance_event(
        self,
        imbalance: ImbalanceDetection,
        action: CorrectionAction
    ) -> None:
        """
        Publish imbalance event to EventBus (Phase 2)

        События отправляются в infrastructure для обработки через
        mio-manager → analytics-specialist → decision-center
        """
        try:
            event_data = {
                'module': self.module_name,
                'kpi_name': imbalance.kpi_name,
                'level': imbalance.level.value,
                'deviation': imbalance.deviation,
                'current_value': imbalance.current_value,
                'target_value': imbalance.target_value,
                'priority': imbalance.priority,
                'action_type': action.action_type,
                'action_description': action.description,
                'action_success': action.success,
                'timestamp': imbalance.timestamp
            }

            # Publish to EventBus
            await self.eventbus.publish({
                'type': 'platform.bcm.imbalance_detected',
                'source': f'{self.module_name}.survival-instinct',
                'data': event_data
            })

            self.stats['events_published'] += 1
            logger.debug(f" Published imbalance event: {imbalance.kpi_name} ({imbalance.level.value})")

        except Exception as e:
            logger.error(f"Failed to publish imbalance event: {e}")


async def start_survival_instinct(
    module_name: str,
    config_path: Optional[str] = None,
    check_interval: int = 60,
    memory_system: Optional['MemorySystem'] = None,
    eventbus=None
) -> SurvivalInstinct:
    """
    Запустить инстинкт выживания для модуля

    Args:
        module_name: Имя модуля
        config_path: Путь к конфигу KPI (опционально)
        check_interval: Интервал проверки в секундах
        memory_system: MemorySystem для хранения паттернов
        eventbus: EventBus для публикации событий (Phase 2)

    Returns:
        Запущенный экземпляр SurvivalInstinct
    """
    instinct = SurvivalInstinct(module_name, check_interval, memory_system, eventbus)

    # Загрузить KPI
    instinct.load_my_kpis(config_path)

    # Запустить в фоне
    asyncio.create_task(instinct.maintain_my_balance())

    return instinct
