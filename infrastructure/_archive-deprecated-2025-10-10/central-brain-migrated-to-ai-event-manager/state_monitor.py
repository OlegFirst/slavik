"""
Центральный Мозг - Монитор Состояния

Получает ТОЛЬКО фактическое состояние системы.
НЕ проводит проверки соответствия - это задача Проектного Менеджера.

Использует фактическое состояние для:
1. Определения доступных ресурсов
2. Принятия стратегических решений
3. Планирования масштабирования
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SystemState:
    """Фактическое состояние системы"""
    timestamp: datetime

    # Ресурсы
    ports_available: int
    ports_used: int

    # Мониторинг
    prometheus_available: bool
    grafana_available: bool
    services_with_metrics: int

    # База данных
    postgres_available: bool
    redis_available: bool
    services_with_db: int

    # Всего сервисов
    total_services: int

    # Дополнительно
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None


class CentralBrainStateMonitor:
    """
    Монитор состояния для Центрального Мозга

    Получает ТОЛЬКО фактическое состояние, БЕЗ проверок соответствия.
    """

    def __init__(self):
        self.current_state: Optional[SystemState] = None
        self.state_history: List[SystemState] = []
        self.max_history = 100  # Хранить последние 100 состояний

    async def collect_state_from_project_manager(self) -> SystemState:
        """
        Получить фактическое состояние от Проектного Менеджера

        Returns:
            Текущее фактическое состояние
        """
        try:
            # Импортируем Проектного Менеджера
            import sys
            from pathlib import Path

            project_root = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(project_root / 'infrastructure' / 'tools' / 'project-manager'))

            from run_compliance_checks import ComplianceCheckRunner

            # Запускаем сбор состояния (БЕЗ проверок соответствия)
            runner = ComplianceCheckRunner()

            # Получаем ТОЛЬКО фактическое состояние
            state_data = runner.export_state_for_central_brain()

            # Преобразуем в SystemState
            ports_data = state_data.get('ports', {})
            metrics_data = state_data.get('metrics', {})
            db_data = state_data.get('databases', {})

            state = SystemState(
                timestamp=datetime.fromisoformat(state_data['timestamp']),
                ports_available=0,  # TODO: вычислить из ports_data
                ports_used=ports_data.get('total_ports_listening', 0),
                prometheus_available=metrics_data.get('prometheus_available', False),
                grafana_available=metrics_data.get('grafana_available', False),
                services_with_metrics=metrics_data.get('services_with_metrics', 0),
                postgres_available=db_data.get('postgres_available', False),
                redis_available=db_data.get('redis_available', False),
                services_with_db=db_data.get('services_connected', 0),
                total_services=max(
                    metrics_data.get('total_services', 0),
                    db_data.get('total_services', 0)
                )
            )

            return state

        except Exception as e:
            logger.error(f"Ошибка при сборе состояния: {e}", exc_info=True)

            # Возвращаем состояние с ошибкой
            return SystemState(
                timestamp=datetime.utcnow(),
                ports_available=0,
                ports_used=0,
                prometheus_available=False,
                grafana_available=False,
                services_with_metrics=0,
                postgres_available=False,
                redis_available=False,
                services_with_db=0,
                total_services=0
            )

    async def update_state(self):
        """Обновить текущее состояние"""
        logger.info("Центральный Мозг: Сбор фактического состояния системы...")

        state = await self.collect_state_from_project_manager()

        self.current_state = state
        self.state_history.append(state)

        # Ограничиваем историю
        if len(self.state_history) > self.max_history:
            self.state_history = self.state_history[-self.max_history:]

        logger.info(f"Состояние обновлено: {state.total_services} сервисов")

    def get_available_resources(self) -> Dict[str, any]:
        """
        Получить доступные ресурсы для принятия решений

        Returns:
            Информация о доступных ресурсах
        """
        if not self.current_state:
            return {
                'available': False,
                'reason': 'Состояние не собрано'
            }

        state = self.current_state

        return {
            'available': True,
            'timestamp': state.timestamp.isoformat(),

            # Порты
            'can_allocate_port': state.ports_used < 100,  # Упрощение

            # Мониторинг
            'monitoring_available': state.prometheus_available and state.grafana_available,
            'monitoring_coverage': (
                state.services_with_metrics / state.total_services
                if state.total_services > 0 else 0
            ),

            # База данных
            'databases_available': state.postgres_available and state.redis_available,
            'database_coverage': (
                state.services_with_db / state.total_services
                if state.total_services > 0 else 0
            ),

            # Общее
            'total_services': state.total_services,
            'system_healthy': (
                state.postgres_available and
                state.redis_available and
                state.prometheus_available
            )
        }

    def can_deploy_new_service(self, service_name: str,
                               requires_db: bool = True,
                               requires_metrics: bool = True) -> tuple[bool, str]:
        """
        Проверить, можно ли развернуть новый сервис

        Центральный Мозг принимает СТРАТЕГИЧЕСКОЕ решение на основе
        фактического состояния.

        Args:
            service_name: Имя сервиса
            requires_db: Требуется ли БД
            requires_metrics: Требуются ли метрики

        Returns:
            (can_deploy, reason)
        """
        if not self.current_state:
            return False, "Состояние системы неизвестно"

        state = self.current_state

        # Проверяем критичные ресурсы
        if requires_db and not state.postgres_available:
            return False, "PostgreSQL недоступен"

        if requires_db and not state.redis_available:
            return False, "Redis недоступен"

        if requires_metrics and not state.prometheus_available:
            return False, "Prometheus недоступен (мониторинг невозможен)"

        # Проверяем доступность портов
        if state.ports_used >= 100:  # Упрощение
            return False, "Недостаточно свободных портов"

        # Все ресурсы доступны
        return True, "Все необходимые ресурсы доступны"

    def suggest_scaling_strategy(self) -> Dict[str, any]:
        """
        Предложить стратегию масштабирования

        Центральный Мозг анализирует фактическое состояние и
        предлагает стратегию.

        Returns:
            Рекомендации по масштабированию
        """
        if not self.current_state:
            return {
                'strategy': 'unknown',
                'reason': 'Состояние не собрано'
            }

        state = self.current_state

        # Анализируем покрытие
        monitoring_coverage = (
            state.services_with_metrics / state.total_services
            if state.total_services > 0 else 0
        )

        db_coverage = (
            state.services_with_db / state.total_services
            if state.total_services > 0 else 0
        )

        # Определяем стратегию
        if not state.postgres_available or not state.redis_available:
            return {
                'strategy': 'emergency',
                'priority': 'critical',
                'action': 'Восстановить критичные БД немедленно',
                'reason': 'Критичные базы данных недоступны'
            }

        if not state.prometheus_available:
            return {
                'strategy': 'monitoring_recovery',
                'priority': 'high',
                'action': 'Восстановить Prometheus для мониторинга',
                'reason': 'Мониторинг недоступен - система работает вслепую'
            }

        if monitoring_coverage < 0.5:
            return {
                'strategy': 'improve_monitoring',
                'priority': 'medium',
                'action': 'Подключить больше сервисов к Prometheus',
                'reason': f'Только {monitoring_coverage * 100:.0f}% сервисов мониторятся'
            }

        if db_coverage < 0.7:
            return {
                'strategy': 'improve_database_connectivity',
                'priority': 'medium',
                'action': 'Подключить больше сервисов к БД',
                'reason': f'Только {db_coverage * 100:.0f}% сервисов подключены к БД'
            }

        # Все хорошо
        return {
            'strategy': 'maintain',
            'priority': 'low',
            'action': 'Поддерживать текущее состояние',
            'reason': 'Система работает в штатном режиме'
        }

    async def continuous_monitoring(self, interval_seconds: int = 60):
        """
        Непрерывный мониторинг состояния

        Args:
            interval_seconds: Интервал обновления (секунды)
        """
        logger.info(f"Центральный Мозг: Запуск непрерывного мониторинга (интервал: {interval_seconds}с)")

        while True:
            try:
                await self.update_state()

                # Получаем ресурсы
                resources = self.get_available_resources()

                if resources['available']:
                    logger.info(
                        f"Ресурсы доступны: "
                        f"Мониторинг: {resources['monitoring_coverage'] * 100:.0f}%, "
                        f"БД: {resources['database_coverage'] * 100:.0f}%"
                    )
                else:
                    logger.warning(f"Ресурсы недоступны: {resources['reason']}")

                # Получаем стратегию
                strategy = self.suggest_scaling_strategy()
                logger.info(
                    f"Стратегия: {strategy['strategy']} "
                    f"(приоритет: {strategy['priority']}) - {strategy['action']}"
                )

                await asyncio.sleep(interval_seconds)

            except asyncio.CancelledError:
                logger.info("Мониторинг остановлен")
                break

            except Exception as e:
                logger.error(f"Ошибка в мониторинге: {e}", exc_info=True)
                await asyncio.sleep(5)  # Короткая пауза при ошибке


async def main():
    """Основная функция для запуска мониторинга"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    monitor = CentralBrainStateMonitor()

    # Однократный сбор состояния
    await monitor.update_state()

    # Показываем ресурсы
    resources = monitor.get_available_resources()
    print("\n" + "=" * 80)
    print("ФАКТИЧЕСКОЕ СОСТОЯНИЕ СИСТЕМЫ (для Центрального Мозга)")
    print("=" * 80)

    if resources['available']:
        print(f"✅ Система работает")
        print(f"   Сервисов: {resources['total_services']}")
        print(f"   Мониторинг: {resources['monitoring_coverage'] * 100:.0f}% покрытие")
        print(f"   БД: {resources['database_coverage'] * 100:.0f}% подключено")
        print(f"   Здоровье: {'✅ Здорова' if resources['system_healthy'] else '⚠️ Проблемы'}")
    else:
        print(f"❌ Проблемы: {resources['reason']}")

    print("")

    # Показываем стратегию
    strategy = monitor.suggest_scaling_strategy()
    print("СТРАТЕГИЯ:")
    print(f"  {strategy['strategy'].upper()} (приоритет: {strategy['priority']})")
    print(f"  Действие: {strategy['action']}")
    print(f"  Причина: {strategy['reason']}")

    print("=" * 80)

    # Опционально: непрерывный мониторинг
    # await monitor.continuous_monitoring(interval_seconds=60)


if __name__ == '__main__':
    asyncio.run(main())
