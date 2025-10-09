"""
Resource Tracker - Отслеживание ресурсов и трендов

Философия:
- Ресурсы = жизненная энергия системы
- Тренды ресурсов предсказывают будущее
- Дефицит ресурсов → триггер самореализации
- Избыток ресурсов → возможность для роста

Интеграция:
- Wishlist System использует для приоритизации
- Survival Instinct мониторит критические пороги
- Self-Actualization триггерится при дефиците
"""

import asyncio
import logging
import time
import psutil
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import deque
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class ResourceSnapshot:
    """Снимок ресурсов в момент времени"""
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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResourceSnapshot':
        return cls(**data)


class ResourceTracker:
    """
    Отслеживание ресурсов системы

    Функции:
    1. Снимки ресурсов каждые N секунд
    2. Расчет трендов (растут/падают/стабильно)
    3. Предсказание дефицита
    4. Доступные ресурсы для Wishlist
    """

    def __init__(
        self,
        snapshot_interval_seconds: float = 60.0,
        history_size: int = 100,
        storage_path: str = "/tmp/resource_history.json"
    ):
        self.snapshot_interval = snapshot_interval_seconds
        self.history_size = history_size
        self.storage_path = storage_path

        # История снимков (last N snapshots)
        self.history: deque = deque(maxlen=history_size)

        # Базовые измерения для дельта
        self.baseline_disk_io: Optional[float] = None
        self.baseline_network: Optional[float] = None

        self.is_running = False

        self.stats = {
            'total_snapshots': 0,
            'deficit_events': 0,
            'surplus_events': 0
        }

        self._load_history()

        logger.info(f"ResourceTracker initialized (interval: {snapshot_interval_seconds}s)")

    def take_snapshot(self) -> ResourceSnapshot:
        """Сделать снимок текущих ресурсов"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)

        # Memory
        mem = psutil.virtual_memory()
        memory_percent = mem.percent
        memory_mb = mem.used / (1024 * 1024)

        # Disk IO (delta since last snapshot)
        disk = psutil.disk_io_counters()
        if self.baseline_disk_io is None:
            self.baseline_disk_io = disk.read_bytes + disk.write_bytes
            disk_io_mb = 0.0
        else:
            current_total = disk.read_bytes + disk.write_bytes
            delta_bytes = current_total - self.baseline_disk_io
            disk_io_mb = delta_bytes / (1024 * 1024)
            self.baseline_disk_io = current_total

        # Network (delta since last snapshot)
        net = psutil.net_io_counters()
        if self.baseline_network is None:
            self.baseline_network = net.bytes_sent + net.bytes_recv
            network_bytes = 0.0
        else:
            current_total = net.bytes_sent + net.bytes_recv
            network_bytes = current_total - self.baseline_network
            self.baseline_network = current_total

        snapshot = ResourceSnapshot(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_mb=memory_mb,
            disk_io_mb=disk_io_mb,
            network_bytes=network_bytes
        )

        self.history.append(snapshot)
        self.stats['total_snapshots'] += 1

        return snapshot

    def calculate_trend(self, metric_name: str, window_size: int = 10) -> float:
        """
        Рассчитать тренд для метрики

        Args:
            metric_name: cpu_percent, memory_percent, etc.
            window_size: Количество последних снимков для анализа

        Returns:
            -1.0 to +1.0:
                +1.0 = быстрый рост
                0.0 = стабильно
                -1.0 = быстрое падение
        """
        if len(self.history) < 2:
            return 0.0

        # Получить последние N снимков
        recent = list(self.history)[-window_size:]

        if len(recent) < 2:
            return 0.0

        # Извлечь значения метрики
        values = [getattr(snap, metric_name) for snap in recent]

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

        # Нормализовать slope в диапазон -1 to +1
        # Для CPU/Memory: slope в процентах per snapshot
        # Считаем что 10% change per snapshot = максимум
        normalized = slope / 10.0
        return max(min(normalized, 1.0), -1.0)

    def predict_deficit(
        self,
        metric_name: str,
        threshold_percent: float = 90.0,
        lookahead_snapshots: int = 5
    ) -> Optional[float]:
        """
        Предсказать когда метрика достигнет порога

        Args:
            metric_name: Метрика для анализа
            threshold_percent: Порог (%)
            lookahead_snapshots: На сколько снимков вперед смотреть

        Returns:
            Секунды до достижения порога (или None если не достигнет)
        """
        if len(self.history) < 2:
            return None

        # Тренд
        trend = self.calculate_trend(metric_name)

        if trend <= 0:
            # Не растет - дефицита не будет
            return None

        # Текущее значение
        current = getattr(self.history[-1], metric_name)

        if current >= threshold_percent:
            # Уже за порогом
            return 0.0

        # Рассчитать скорость роста (percent per second)
        growth_rate = trend * 10.0 / self.snapshot_interval  # percent per second

        if growth_rate == 0:
            return None

        # Сколько секунд до порога
        percent_to_threshold = threshold_percent - current
        seconds_to_threshold = percent_to_threshold / growth_rate

        # Проверить в пределах lookahead
        max_lookahead_seconds = lookahead_snapshots * self.snapshot_interval

        if seconds_to_threshold <= max_lookahead_seconds:
            return seconds_to_threshold

        return None

    def get_available_resources(self) -> Dict[str, float]:
        """
        Получить доступные ресурсы

        Returns:
            Словарь с доступными ресурсами для Wishlist
        """
        if not self.history:
            # Нет данных - вернуть дефолты
            return {
                'cpu_percent': 50.0,
                'memory_mb': 1000.0,
                'time_seconds': 60.0,
                'disk_io_mb': 100.0
            }

        latest = self.history[-1]

        # Доступно = 100% - используется
        available_cpu = 100.0 - latest.cpu_percent
        available_memory_percent = 100.0 - latest.memory_percent

        # Память в MB (считаем доступно 20% от total)
        mem_total = psutil.virtual_memory().total / (1024 * 1024)
        available_memory_mb = mem_total * (available_memory_percent / 100.0) * 0.2

        return {
            'cpu_percent': max(available_cpu, 0.0),
            'memory_mb': max(available_memory_mb, 0.0),
            'time_seconds': 60.0,  # Фиксированное время на задачу
            'disk_io_mb': 100.0    # Фиксированный лимит IO
        }

    def detect_resource_state(self) -> str:
        """
        Определить текущее состояние ресурсов

        Returns:
            "deficit", "normal", "surplus"
        """
        if not self.history:
            return "normal"

        latest = self.history[-1]

        # Дефицит если CPU или Memory высокие
        if latest.cpu_percent > 80 or latest.memory_percent > 80:
            self.stats['deficit_events'] += 1
            return "deficit"

        # Избыток если оба низкие
        if latest.cpu_percent < 30 and latest.memory_percent < 50:
            self.stats['surplus_events'] += 1
            return "surplus"

        return "normal"

    async def run_monitoring_loop(self):
        """Основной цикл мониторинга"""
        self.is_running = True
        logger.info("ResourceTracker monitoring started")

        while self.is_running:
            try:
                # Сделать снимок
                snapshot = self.take_snapshot()

                # Проверить дефицит CPU
                cpu_deficit = self.predict_deficit('cpu_percent', threshold_percent=90.0)
                if cpu_deficit and cpu_deficit < 300:  # Меньше 5 минут
                    logger.warning(f"CPU deficit predicted in {cpu_deficit:.0f}s")

                # Проверить дефицит памяти
                mem_deficit = self.predict_deficit('memory_percent', threshold_percent=90.0)
                if mem_deficit and mem_deficit < 300:
                    logger.warning(f"Memory deficit predicted in {mem_deficit:.0f}s")

                # Состояние ресурсов
                state = self.detect_resource_state()
                if state == "deficit":
                    logger.warning("Resource deficit detected")
                elif state == "surplus":
                    logger.info("Resource surplus detected")

                # Сохранить историю
                self._save_history()

                await asyncio.sleep(self.snapshot_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(self.snapshot_interval)

        logger.info("ResourceTracker monitoring stopped")

    def stop(self):
        """Остановить мониторинг"""
        self.is_running = False

    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику"""
        trends = {}
        if len(self.history) >= 2:
            trends = {
                'cpu_trend': self.calculate_trend('cpu_percent'),
                'memory_trend': self.calculate_trend('memory_percent')
            }

        resource_state = self.detect_resource_state()

        return {
            **self.stats,
            'history_size': len(self.history),
            'resource_state': resource_state,
            **trends
        }

    def _save_history(self):
        """Сохранить историю в файл"""
        try:
            # Сохранять только последние 50 для экономии места
            recent_history = list(self.history)[-50:]

            data = {
                'snapshots': [snap.to_dict() for snap in recent_history],
                'stats': self.stats,
                'saved_at': time.time()
            }

            Path(self.storage_path).parent.mkdir(parents=True, exist_ok=True)

            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save resource history: {e}")

    def _load_history(self):
        """Загрузить историю из файла"""
        try:
            if not Path(self.storage_path).exists():
                return

            with open(self.storage_path, 'r') as f:
                data = json.load(f)

            # Восстановить snapshots
            for snap_data in data.get('snapshots', []):
                snapshot = ResourceSnapshot.from_dict(snap_data)
                self.history.append(snapshot)

            self.stats = data.get('stats', self.stats)

            logger.info(f"Loaded {len(self.history)} snapshots from disk")

        except Exception as e:
            logger.error(f"Failed to load resource history: {e}")


async def create_resource_tracker(
    snapshot_interval_seconds: float = 60.0,
    history_size: int = 100,
    storage_path: str = "/tmp/resource_history.json"
) -> ResourceTracker:
    """
    Создать и запустить Resource Tracker

    Args:
        snapshot_interval_seconds: Интервал снимков
        history_size: Размер истории
        storage_path: Путь к файлу хранения

    Returns:
        Started ResourceTracker instance
    """
    tracker = ResourceTracker(snapshot_interval_seconds, history_size, storage_path)

    # Сделать первый снимок сразу
    tracker.take_snapshot()

    # Запустить мониторинг
    asyncio.create_task(tracker.run_monitoring_loop())

    return tracker
