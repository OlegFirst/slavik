"""
Circuit Breaker Pattern для AI Agent Router

Защищает от cascade failures и автоматически восстанавливает соединение.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Callable, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Состояния Circuit Breaker"""
    CLOSED = 0      # Нормальная работа
    OPEN = 1        # Circuit открыт, запросы блокируются
    HALF_OPEN = 2   # Пробный режим восстановления


@dataclass
class CircuitBreakerConfig:
    """Конфигурация Circuit Breaker"""
    failure_threshold: int = 5              # Порог неудачных попыток
    success_threshold: int = 2              # Порог успешных попыток для закрытия
    timeout: float = 60.0                   # Timeout открытого состояния (секунды)
    half_open_max_requests: int = 3         # Макс запросов в half-open состоянии

    # Exponential backoff
    initial_backoff: float = 1.0            # Начальная задержка
    max_backoff: float = 300.0              # Максимальная задержка
    backoff_multiplier: float = 2.0         # Множитель задержки


@dataclass
class CircuitBreakerStats:
    """Статистика Circuit Breaker"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rejected_requests: int = 0
    state_changes: Dict[str, int] = field(default_factory=lambda: {
        "CLOSED->OPEN": 0,
        "OPEN->HALF_OPEN": 0,
        "HALF_OPEN->CLOSED": 0,
        "HALF_OPEN->OPEN": 0
    })
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None


class CircuitBreaker:
    """
    Circuit Breaker для защиты от cascade failures.

    Работает в трех состояниях:
    1. CLOSED - нормальная работа, все запросы проходят
    2. OPEN - circuit открыт, запросы блокируются
    3. HALF_OPEN - пробный режим, разрешено ограниченное количество запросов
    """

    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.stats = CircuitBreakerStats()

        # Счетчики для управления состоянием
        self.failure_count = 0
        self.success_count = 0
        self.half_open_requests = 0

        # Временные метки
        self.opened_at: Optional[datetime] = None
        self.current_backoff = self.config.initial_backoff

        # Lock для thread-safety
        self._lock = asyncio.Lock()

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Выполнить функцию через Circuit Breaker.

        Args:
            func: Async функция для выполнения
            *args, **kwargs: Аргументы функции

        Returns:
            Результат выполнения функции

        Raises:
            CircuitBreakerOpenError: Если circuit открыт
            Exception: Ошибка выполнения функции
        """
        async with self._lock:
            self.stats.total_requests += 1

            # Проверяем состояние circuit breaker
            await self._check_state_transition()

            if self.state == CircuitState.OPEN:
                self.stats.rejected_requests += 1
                raise CircuitBreakerOpenError(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Opened at: {self.opened_at}, "
                    f"Timeout: {self.config.timeout}s"
                )

            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_requests >= self.config.half_open_max_requests:
                    self.stats.rejected_requests += 1
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker '{self.name}' is HALF_OPEN with max requests reached"
                    )
                self.half_open_requests += 1

        # Выполняем функцию (вне lock чтобы не блокировать другие запросы)
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result

        except Exception as e:
            await self._on_failure(e)
            raise

    async def _check_state_transition(self):
        """Проверить и выполнить переход состояния если нужно"""
        if self.state == CircuitState.OPEN:
            # Проверяем, прошел ли timeout
            if self.opened_at:
                elapsed = (datetime.now() - self.opened_at).total_seconds()
                if elapsed >= self.current_backoff:
                    await self._transition_to_half_open()

    async def _on_success(self):
        """Обработать успешное выполнение"""
        async with self._lock:
            self.stats.successful_requests += 1
            self.stats.last_success_time = datetime.now()
            self.failure_count = 0  # Сбрасываем счетчик неудач

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1

                # Если достигли порога успешных запросов, закрываем circuit
                if self.success_count >= self.config.success_threshold:
                    await self._transition_to_closed()

    async def _on_failure(self, exception: Exception):
        """Обработать неудачное выполнение"""
        async with self._lock:
            self.stats.failed_requests += 1
            self.stats.last_failure_time = datetime.now()
            self.failure_count += 1

            logger.warning(
                f"Circuit breaker '{self.name}' failure #{self.failure_count}: {exception}"
            )

            if self.state == CircuitState.HALF_OPEN:
                # В half-open режиме любая ошибка открывает circuit снова
                await self._transition_to_open()

            elif self.state == CircuitState.CLOSED:
                # Проверяем порог неудач
                if self.failure_count >= self.config.failure_threshold:
                    await self._transition_to_open()

    async def _transition_to_open(self):
        """Перейти в OPEN состояние"""
        old_state = self.state.name
        self.state = CircuitState.OPEN
        self.opened_at = datetime.now()
        self.success_count = 0
        self.half_open_requests = 0

        # Exponential backoff
        self.current_backoff = min(
            self.current_backoff * self.config.backoff_multiplier,
            self.config.max_backoff
        )

        transition = f"{old_state}->OPEN"
        self.stats.state_changes[transition] = self.stats.state_changes.get(transition, 0) + 1

        logger.warning(
            f"Circuit breaker '{self.name}' opened. "
            f"Failures: {self.failure_count}, Backoff: {self.current_backoff}s"
        )

    async def _transition_to_half_open(self):
        """Перейти в HALF_OPEN состояние"""
        old_state = self.state.name
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
        self.failure_count = 0
        self.half_open_requests = 0

        transition = f"{old_state}->HALF_OPEN"
        self.stats.state_changes[transition] = self.stats.state_changes.get(transition, 0) + 1

        logger.info(
            f"Circuit breaker '{self.name}' half-opened. "
            f"Allowing {self.config.half_open_max_requests} test requests"
        )

    async def _transition_to_closed(self):
        """Перейти в CLOSED состояние"""
        old_state = self.state.name
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.opened_at = None
        self.current_backoff = self.config.initial_backoff  # Сброс backoff

        transition = f"{old_state}->CLOSED"
        self.stats.state_changes[transition] = self.stats.state_changes.get(transition, 0) + 1

        logger.info(
            f"Circuit breaker '{self.name}' closed. "
            f"Successful recoveries: {self.stats.state_changes.get('HALF_OPEN->CLOSED', 0)}"
        )

    async def reset(self):
        """Принудительно сбросить circuit breaker в CLOSED состояние"""
        async with self._lock:
            logger.info(f"Manually resetting circuit breaker '{self.name}'")
            await self._transition_to_closed()

    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику circuit breaker"""
        return {
            "name": self.name,
            "state": self.state.name,
            "stats": {
                "total_requests": self.stats.total_requests,
                "successful_requests": self.stats.successful_requests,
                "failed_requests": self.stats.failed_requests,
                "rejected_requests": self.stats.rejected_requests,
                "state_changes": self.stats.state_changes,
                "last_failure": self.stats.last_failure_time.isoformat() if self.stats.last_failure_time else None,
                "last_success": self.stats.last_success_time.isoformat() if self.stats.last_success_time else None
            },
            "current_state": {
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "current_backoff": self.current_backoff,
                "opened_at": self.opened_at.isoformat() if self.opened_at else None
            },
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "timeout": self.config.timeout,
                "max_backoff": self.config.max_backoff
            }
        }


class CircuitBreakerOpenError(Exception):
    """Исключение когда circuit breaker открыт"""
    pass


class CircuitBreakerManager:
    """
    Менеджер для управления несколькими Circuit Breakers.

    Использование:
        manager = CircuitBreakerManager()
        breaker = manager.get_breaker("agent_name")
        result = await breaker.call(async_func, arg1, arg2)
    """

    def __init__(self, default_config: Optional[CircuitBreakerConfig] = None):
        self.default_config = default_config or CircuitBreakerConfig()
        self.breakers: Dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()

    async def get_breaker(self, name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """Получить или создать circuit breaker"""
        async with self._lock:
            if name not in self.breakers:
                breaker_config = config or self.default_config
                self.breakers[name] = CircuitBreaker(name, breaker_config)
            return self.breakers[name]

    def get_all_stats(self) -> Dict[str, Dict]:
        """Получить статистику всех circuit breakers"""
        return {
            name: breaker.get_stats()
            for name, breaker in self.breakers.items()
        }

    async def reset_all(self):
        """Сбросить все circuit breakers"""
        async with self._lock:
            for breaker in self.breakers.values():
                await breaker.reset()

    async def reset_breaker(self, name: str):
        """Сбросить конкретный circuit breaker"""
        async with self._lock:
            if name in self.breakers:
                await self.breakers[name].reset()
