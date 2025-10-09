"""
ПРИОРИТЕТ 1: Обнаружение конфликтов портов

Первая и самая критичная проверка - конфликты портов должны быть обнаружены
ДО запуска любых других проверок.

Это инструмент для проектного менеджера, НЕ для центрального мозга.
Центральный мозг получает только фактическое состояние.
"""

import socket
import subprocess
import logging
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PortConflict:
    """Конфликт порта"""
    port: int
    services: List[str]
    severity: str  # 'critical', 'warning'
    actual_process: Optional[str] = None  # Что реально занимает порт


@dataclass
class PortAssignment:
    """Назначение порта"""
    port: int
    service_name: str
    is_critical: bool
    is_listening: bool
    actual_process: Optional[str] = None


# ИСТОЧНИК ПРАВДЫ: Ожидаемые назначения портов
EXPECTED_PORT_ASSIGNMENTS = {
    # Infrastructure Services (6000-6999)
    5432: {'service': 'postgres', 'critical': True},
    6379: {'service': 'redis', 'critical': True},
    8001: {'service': 'eventbus', 'critical': True},

    # Platform Services (8000-8099)
    8011: {'service': 'planning-service', 'critical': True},
    8023: {'service': 'plans-service', 'critical': True},
    8030: {'service': 'governance-service', 'critical': True},
    8040: {'service': 'risk-service', 'critical': True},
    8050: {'service': 'response-service', 'critical': True},
    8060: {'service': 'learning-service', 'critical': True},
    8070: {'service': 'validation-service', 'critical': False},
    8080: {'service': 'documents-service', 'critical': False},
    8090: {'service': 'bia-service', 'critical': False},

    # Intelligent Core Services (9000-9099)
    9001: {'service': 'workflow-intelligence', 'critical': True},
    9002: {'service': 'ai-workflow-optimizer', 'critical': True},
    9003: {'service': 'expertise-center', 'critical': False},
    9004: {'service': 'orchestration', 'critical': False},
    9005: {'service': 'event-intelligence', 'critical': False},
    9006: {'service': 'predictive', 'critical': False},
    9007: {'service': 'community-intelligence', 'critical': False},

    # Phase 2 Services
    9091: {'service': 'balancer-service', 'critical': True},
    9092: {'service': 'resource-tracker', 'critical': False},

    # AI Office Infrastructure (7000-7999)
    7001: {'service': 'mio-manager', 'critical': False},
    7002: {'service': 'monitoring-service', 'critical': False},
    7003: {'service': 'notification-service', 'critical': False},
    7004: {'service': 'deployment-service', 'critical': False},
    7005: {'service': 'github-integration', 'critical': False},

    # Monitoring & Observability (3000-3999)
    3000: {'service': 'grafana', 'critical': False},
    9090: {'service': 'prometheus', 'critical': False},

    # Simulation & Digital Twin (10000-10099)
    10001: {'service': 'digital-twin', 'critical': False},
    10002: {'service': 'scenario-orchestrator', 'critical': False},
}


class PortConflictDetector:
    """
    Детектор конфликтов портов

    ПРИОРИТЕТ 1: Должен запускаться ПЕРВЫМ перед всеми другими проверками
    """

    def __init__(self):
        self.conflicts: List[PortConflict] = []
        self.assignments: Dict[int, PortAssignment] = {}

    def get_listening_ports_detailed(self) -> Dict[int, str]:
        """
        Получить детальную информацию о занятых портах

        Returns:
            Dict[port -> process_name]
        """
        ports_info = {}

        try:
            # Используем lsof для получения детальной информации
            result = subprocess.run(
                ['lsof', '-iTCP', '-sTCP:LISTEN', '-n', '-P'],
                capture_output=True,
                text=True,
                timeout=10
            )

            for line in result.stdout.split('\n')[1:]:  # Пропускаем заголовок
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 9:
                        process_name = parts[0]
                        addr = parts[8]

                        if ':' in addr:
                            port_str = addr.split(':')[-1]
                            if port_str.isdigit():
                                port = int(port_str)

                                # Сохраняем первый процесс для порта
                                if port not in ports_info:
                                    ports_info[port] = process_name

        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.error(f"Не удалось получить информацию о портах через lsof: {e}")

            # Fallback: простая проверка портов
            for port in EXPECTED_PORT_ASSIGNMENTS.keys():
                if self._is_port_listening(port):
                    ports_info[port] = "unknown"

        return ports_info

    def _is_port_listening(self, port: int) -> bool:
        """Проверить, слушает ли порт"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        try:
            result = sock.connect_ex(('localhost', port))
            return result == 0
        except socket.error:
            return False
        finally:
            sock.close()

    def detect_conflicts(self) -> List[PortConflict]:
        """
        Обнаружить конфликты портов

        Returns:
            Список конфликтов
        """
        logger.info("=" * 80)
        logger.info("ПРИОРИТЕТ 1: Проверка конфликтов портов")
        logger.info("=" * 80)

        # Получаем фактическое состояние портов
        actual_ports = self.get_listening_ports_detailed()

        # Группируем ожидаемые назначения по портам
        port_to_services: Dict[int, List[str]] = {}

        for port, config in EXPECTED_PORT_ASSIGNMENTS.items():
            service_name = config['service']

            if port not in port_to_services:
                port_to_services[port] = []

            port_to_services[port].append(service_name)

            # Создаем запись о назначении
            self.assignments[port] = PortAssignment(
                port=port,
                service_name=service_name,
                is_critical=config['critical'],
                is_listening=(port in actual_ports),
                actual_process=actual_ports.get(port)
            )

        # Проверяем конфликты (несколько сервисов на одном порту)
        conflicts = []

        for port, services in port_to_services.items():
            if len(services) > 1:
                # КОНФЛИКТ: Несколько сервисов хотят один порт
                is_critical = any(
                    EXPECTED_PORT_ASSIGNMENTS[port]['critical']
                    for svc in services
                )

                conflict = PortConflict(
                    port=port,
                    services=services,
                    severity='critical' if is_critical else 'warning',
                    actual_process=actual_ports.get(port)
                )

                conflicts.append(conflict)
                logger.error(
                    f"❌ КОНФЛИКТ ПОРТА {port}: "
                    f"{', '.join(services)} "
                    f"(фактически занят: {actual_ports.get(port, 'не занят')})"
                )

        # Проверяем порты, занятые неизвестными процессами
        reserved_ports = set(EXPECTED_PORT_ASSIGNMENTS.keys())

        for port, process in actual_ports.items():
            if port not in reserved_ports:
                # Порт занят, но не зарезервирован ни одним сервисом
                logger.warning(
                    f"⚠️  Порт {port} занят процессом '{process}', "
                    f"но не зарезервирован ни одним сервисом"
                )

        self.conflicts = conflicts

        # Итоговый отчет
        if conflicts:
            logger.error(f"❌ Обнаружено {len(conflicts)} конфликтов портов")
        else:
            logger.info("✅ Конфликтов портов не обнаружено")

        return conflicts

    def get_port_map_for_central_brain(self) -> Dict[str, any]:
        """
        Получить карту портов для Центрального Мозга

        Центральный мозг получает только ФАКТИЧЕСКОЕ состояние,
        без деталей о том, как оно должно быть.

        Returns:
            Фактическое состояние портов
        """
        actual_ports = self.get_listening_ports_detailed()

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'total_ports_listening': len(actual_ports),
            'ports': [
                {
                    'port': port,
                    'process': process,
                    'is_expected': port in EXPECTED_PORT_ASSIGNMENTS
                }
                for port, process in actual_ports.items()
            ]
        }

    def generate_report(self) -> str:
        """
        Сгенерировать отчет о конфликтах портов

        Returns:
            Текстовый отчет
        """
        report = []
        report.append("=" * 80)
        report.append("ПРИОРИТЕТ 1: Отчет о конфликтах портов")
        report.append("=" * 80)
        report.append(f"Дата проверки: {datetime.utcnow().isoformat()}")
        report.append("")

        if self.conflicts:
            report.append(f"❌ ОБНАРУЖЕНО КОНФЛИКТОВ: {len(self.conflicts)}")
            report.append("")

            for conflict in self.conflicts:
                report.append(f"Порт {conflict.port}:")
                report.append(f"  Сервисы: {', '.join(conflict.services)}")
                report.append(f"  Критичность: {conflict.severity}")

                if conflict.actual_process:
                    report.append(f"  Фактически занят: {conflict.actual_process}")
                else:
                    report.append(f"  Фактически: не занят")

                report.append("")
        else:
            report.append("✅ Конфликтов не обнаружено")
            report.append("")

        # Статистика по назначениям
        report.append("Статистика по портам:")
        report.append(f"  Ожидаемых назначений: {len(EXPECTED_PORT_ASSIGNMENTS)}")

        listening_count = sum(
            1 for assignment in self.assignments.values()
            if assignment.is_listening
        )
        report.append(f"  Портов слушает: {listening_count}")

        critical_count = sum(
            1 for port, config in EXPECTED_PORT_ASSIGNMENTS.items()
            if config['critical']
        )
        report.append(f"  Критических сервисов: {critical_count}")

        critical_listening = sum(
            1 for assignment in self.assignments.values()
            if assignment.is_critical and assignment.is_listening
        )
        report.append(f"  Критических портов слушает: {critical_listening}/{critical_count}")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)


def check_port_conflicts() -> Tuple[bool, List[PortConflict]]:
    """
    Проверить конфликты портов (основная функция)

    Returns:
        (has_conflicts, conflicts)
    """
    detector = PortConflictDetector()
    conflicts = detector.detect_conflicts()

    print(detector.generate_report())

    return len(conflicts) > 0, conflicts


if __name__ == '__main__':
    """Запуск проверки"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )

    has_conflicts, conflicts = check_port_conflicts()

    if has_conflicts:
        exit(1)  # Ошибка - есть конфликты
    else:
        exit(0)  # OK
