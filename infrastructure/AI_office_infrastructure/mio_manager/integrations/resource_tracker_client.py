"""
Resource Tracker Client для MIO Manager

Интеграция Phase 2: Resource Tracker как ГЛАЗА () для мониторинга ресурсов системы.

MIO Manager = Глаза + Руки инфраструктуры
Resource Tracker = Специализированный модуль для системных ресурсов

Публикует метрики в EventBus:
- platform.resources.snapshot (каждые 60s)
- platform.resources.deficit (при дефиците)
- platform.resources.surplus (при избытке)
"""

import asyncio
import logging
import time
import psutil
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from collections import deque
import sys
from pathlib import Path

# Add coordination-center to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / 'intelligent-core'))

logger = logging.getLogger(__name__)


@dataclass
class ResourceSnapshot:
    """Снимок ресурсов"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_io_mb: float
    network_bytes: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'memory_mb': self.memory_mb,
            'disk_io_mb': self.disk_io_mb,
            'network_bytes': self.network_bytes
        }


class ResourceTrackerClient:
    """
    Resource Tracker Client для MIO Manager

    Роль:  ГЛАЗА для системных ресурсов

    Возможности:
    - Мониторинг CPU, Memory, Disk, Network
    - Расчет трендов (растет/падает/стабильно)
    - Предсказание дефицита
    - Публикация в EventBus
    """

    def __init__(
        self,
        eventbus=None,
        snapshot_interval_seconds: float = 60.0,
        history_size: int = 100
    ):
        """
        Initialize Resource Tracker Client

        Args:
            eventbus: EventBus для публикации метрик
            snapshot_interval_seconds: Интервал снимков (default: 60s)
            history_size: Размер истории (default: 100 snapshots)
        """
        self.eventbus = eventbus
        self.snapshot_interval = snapshot_interval_seconds
        self.history_size = history_size

        # История снимков
        self.history = deque(maxlen=history_size)

        # Флаги
        self.running = False
        self.monitor_task = None

        # Callbacks
        self.on_deficit_callback: Optional[Callable] = None
        self.on_surplus_callback: Optional[Callable] = None

        # Счетчики
        self.snapshots_taken = 0
        self.deficits_detected = 0
        self.surplus_detected = 0

    async def start(self):
        """Запустить мониторинг"""
        if self.running:
            logger.warning("Resource Tracker already running")
            return

        self.running = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info(f" Resource Tracker Client started (interval: {self.snapshot_interval}s)")

    async def stop(self):
        """Остановить мониторинг"""
        self.running = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logger.info(" Resource Tracker Client stopped")

    async def _monitor_loop(self):
        """Основной цикл мониторинга"""
        while self.running:
            try:
                # Снять snapshot
                snapshot = self._take_snapshot()
                self.history.append(snapshot)
                self.snapshots_taken += 1

                # Определить состояние
                state = self._detect_resource_state()

                # Публикация snapshot в EventBus
                if self.eventbus:
                    await self.eventbus.publish({
                        'type': 'platform.resources.snapshot',
                        'source': 'mio-manager.resource-tracker',
                        'data': {
                            **snapshot.to_dict(),
                            'state': state,
                            'trend': {
                                'cpu': self._calculate_trend('cpu_percent'),
                                'memory': self._calculate_trend('memory_percent')
                            }
                        }
                    })

                # Обработка дефицита/избытка
                if state == 'deficit':
                    self.deficits_detected += 1
                    await self._handle_deficit(snapshot)
                elif state == 'surplus':
                    self.surplus_detected += 1
                    await self._handle_surplus(snapshot)

                # Ждать следующий интервал
                await asyncio.sleep(self.snapshot_interval)

            except Exception as e:
                logger.error(f"Resource monitor loop error: {e}")
                await asyncio.sleep(self.snapshot_interval)

    def _take_snapshot(self) -> ResourceSnapshot:
        """Снять снимок ресурсов"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()

        # Disk IO
        try:
            disk_io = psutil.disk_io_counters()
            disk_io_mb = (disk_io.read_bytes + disk_io.write_bytes) / (1024 * 1024)
        except:
            disk_io_mb = 0.0

        # Network
        try:
            net_io = psutil.net_io_counters()
            network_bytes = net_io.bytes_sent + net_io.bytes_recv
        except:
            network_bytes = 0.0

        return ResourceSnapshot(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=mem.percent,
            memory_mb=mem.used / (1024 * 1024),
            disk_io_mb=disk_io_mb,
            network_bytes=network_bytes
        )

    def _calculate_trend(self, metric_name: str, window_size: int = 10) -> float:
        """
        Рассчитать тренд метрики

        Returns:
            -1.0 to +1.0 (negative = падает, positive = растет, 0 = стабильно)
        """
        if len(self.history) < 2:
            return 0.0

        recent = list(self.history)[-window_size:]
        if len(recent) < 2:
            return 0.0

        values = [getattr(s, metric_name) for s in recent]

        # Простая линейная регрессия
        n = len(values)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        slope = numerator / denominator

        # Нормализовать slope к [-1, 1]
        max_change = max(values) - min(values)
        if max_change == 0:
            return 0.0

        normalized_slope = slope / max_change
        return max(-1.0, min(1.0, normalized_slope))

    def _detect_resource_state(self) -> str:
        """
        Определить состояние ресурсов

        Returns:
            'deficit' | 'normal' | 'surplus'
        """
        if not self.history:
            return 'normal'

        latest = self.history[-1]

        # Дефицит: CPU > 85% ИЛИ Memory > 85%
        if latest.cpu_percent > 85.0 or latest.memory_percent > 85.0:
            return 'deficit'

        # Избыток: CPU < 20% И Memory < 30%
        if latest.cpu_percent < 20.0 and latest.memory_percent < 30.0:
            return 'surplus'

        return 'normal'

    async def _handle_deficit(self, snapshot: ResourceSnapshot):
        """Обработка дефицита ресурсов"""
        logger.warning(f"️  Resource DEFICIT detected: CPU={snapshot.cpu_percent:.1f}%, Memory={snapshot.memory_percent:.1f}%")

        # Публикация события дефицита
        if self.eventbus:
            await self.eventbus.publish({
                'type': 'platform.resources.deficit',
                'source': 'mio-manager.resource-tracker',
                'data': {
                    **snapshot.to_dict(),
                    'severity': 'high' if snapshot.cpu_percent > 95 or snapshot.memory_percent > 95 else 'medium'
                }
            })

        # Callback
        if self.on_deficit_callback:
            await self.on_deficit_callback(snapshot)

    async def _handle_surplus(self, snapshot: ResourceSnapshot):
        """Обработка избытка ресурсов"""
        logger.info(f" Resource SURPLUS: CPU={snapshot.cpu_percent:.1f}%, Memory={snapshot.memory_percent:.1f}%")

        # Публикация события избытка
        if self.eventbus:
            await self.eventbus.publish({
                'type': 'platform.resources.surplus',
                'source': 'mio-manager.resource-tracker',
                'data': snapshot.to_dict()
            })

        # Callback
        if self.on_surplus_callback:
            await self.on_surplus_callback(snapshot)

    def get_available_resources(self) -> Dict[str, float]:
        """
        Получить доступные ресурсы для Wishlist

        Returns:
            Dict с доступными процентами ресурсов
        """
        if not self.history:
            return {
                'cpu_percent': 50.0,
                'memory_mb': 1024.0,
                'time_seconds': 300.0
            }

        latest = self.history[-1]

        # Доступно = 100 - используется
        available_cpu = max(0, 100 - latest.cpu_percent)
        available_memory_mb = max(0, psutil.virtual_memory().available / (1024 * 1024))

        # Time всегда доступен (виртуальный ресурс)
        available_time = 300.0

        return {
            'cpu_percent': available_cpu,
            'memory_mb': available_memory_mb,
            'time_seconds': available_time
        }

    def get_stats(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            'snapshots_taken': self.snapshots_taken,
            'deficits_detected': self.deficits_detected,
            'surplus_detected': self.surplus_detected,
            'history_size': len(self.history),
            'current_state': self._detect_resource_state() if self.history else 'unknown',
            'latest_snapshot': self.history[-1].to_dict() if self.history else None
        }

    def on_deficit(self, callback: Callable):
        """Зарегистрировать callback для дефицита"""
        self.on_deficit_callback = callback

    def on_surplus(self, callback: Callable):
        """Зарегистрировать callback для избытка"""
        self.on_surplus_callback = callback


async def create_resource_tracker_client(eventbus=None, **kwargs) -> ResourceTrackerClient:
    """
    Factory function для создания Resource Tracker Client

    Args:
        eventbus: EventBus instance
        **kwargs: Дополнительные параметры

    Returns:
        ResourceTrackerClient instance
    """
    client = ResourceTrackerClient(eventbus=eventbus, **kwargs)
    await client.start()
    return client
