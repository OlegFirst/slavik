"""
Проектный Менеджер - Запуск всех проверок соответствия

Запускает проверки в правильном порядке приоритетов:
1. Конфликты портов (КРИТИЧНО - должно быть первым)
2. Интеграция с метриками (Grafana/Prometheus)
3. Подключение к базам данных
4. Регистрация KPI
5. Публикация событий в EventBus
6. Контроль оркестратором/координатором

Это инструменты для ПРОЕКТНОГО МЕНЕДЖЕРА.
Центральный мозг получает только фактическое состояние.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Добавляем пути
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


class ComplianceCheckRunner:
    """Запускает все проверки соответствия"""

    def __init__(self):
        self.results: Dict[str, Dict] = {}
        self.start_time = datetime.utcnow()

    def run_priority_1_port_conflicts(self) -> bool:
        """
        ПРИОРИТЕТ 1: Конфликты портов

        КРИТИЧНО: Должно быть проверено ПЕРВЫМ
        """
        logger.info("=" * 80)
        logger.info("ЗАПУСК: ПРИОРИТЕТ 1 - Проверка конфликтов портов")
        logger.info("=" * 80)

        try:
            from compliance_checks.priority_1_port_conflicts import check_port_conflicts

            has_conflicts, conflicts = check_port_conflicts()

            self.results['port_conflicts'] = {
                'priority': 1,
                'passed': not has_conflicts,
                'conflicts_found': len(conflicts),
                'conflicts': [
                    {
                        'port': c.port,
                        'services': c.services,
                        'severity': c.severity
                    }
                    for c in conflicts
                ]
            }

            if has_conflicts:
                logger.error(f"❌ ПРИОРИТЕТ 1 FAILED: Обнаружено {len(conflicts)} конфликтов портов")
                logger.error("⚠️  ОСТАНОВКА: Невозможно продолжить пока есть конфликты портов")
                return False
            else:
                logger.info("✅ ПРИОРИТЕТ 1 PASSED: Конфликтов портов не обнаружено")
                return True

        except Exception as e:
            logger.error(f"❌ Ошибка при проверке конфликтов портов: {e}", exc_info=True)
            return False

    def run_priority_2_metrics(self) -> bool:
        """
        ПРИОРИТЕТ 2: Интеграция с метриками
        """
        logger.info("")
        logger.info("=" * 80)
        logger.info("ЗАПУСК: ПРИОРИТЕТ 2 - Проверка интеграции с метриками")
        logger.info("=" * 80)

        try:
            from compliance_checks.priority_2_metrics_integration import check_metrics_integration

            success = check_metrics_integration()

            self.results['metrics_integration'] = {
                'priority': 2,
                'passed': success
            }

            if success:
                logger.info("✅ ПРИОРИТЕТ 2 PASSED: Интеграция с метриками в порядке")
            else:
                logger.warning("⚠️  ПРИОРИТЕТ 2 WARNING: Проблемы с интеграцией метрик")

            return success

        except Exception as e:
            logger.error(f"❌ Ошибка при проверке метрик: {e}", exc_info=True)
            return False

    def run_priority_3_database(self) -> bool:
        """
        ПРИОРИТЕТ 3: Подключение к базам данных
        """
        logger.info("")
        logger.info("=" * 80)
        logger.info("ЗАПУСК: ПРИОРИТЕТ 3 - Проверка подключений к БД")
        logger.info("=" * 80)

        try:
            from compliance_checks.priority_3_database_connections import check_database_connections

            success = check_database_connections()

            self.results['database_connections'] = {
                'priority': 3,
                'passed': success
            }

            if success:
                logger.info("✅ ПРИОРИТЕТ 3 PASSED: Подключения к БД в порядке")
            else:
                logger.warning("⚠️  ПРИОРИТЕТ 3 WARNING: Проблемы с подключениями к БД")

            return success

        except Exception as e:
            logger.error(f"❌ Ошибка при проверке БД: {e}", exc_info=True)
            return False

    def run_priority_4_kpi(self) -> bool:
        """
        ПРИОРИТЕТ 4: Регистрация KPI
        """
        logger.info("")
        logger.info("=" * 80)
        logger.info("ЗАПУСК: ПРИОРИТЕТ 4 - Проверка регистрации KPI")
        logger.info("=" * 80)

        try:
            from compliance_checks.priority_4_kpi_registration import KPIRegistrationChecker

            checker = KPIRegistrationChecker()
            results = checker.check_all_kpis()
            success = checker.print_results(results)

            self.results['kpi_registration'] = {
                'priority': 4,
                'passed': success
            }

            if success:
                logger.info("✅ ПРИОРИТЕТ 4 PASSED: Регистрация KPI в порядке")
            else:
                logger.warning("⚠️  ПРИОРИТЕТ 4 WARNING: Проблемы с регистрацией KPI")

            return success

        except Exception as e:
            logger.error(f"❌ Ошибка при проверке KPI: {e}", exc_info=True)
            return False

    def run_priority_5_eventbus(self) -> bool:
        """
        ПРИОРИТЕТ 5: Публикация событий в EventBus
        """
        logger.info("")
        logger.info("=" * 80)
        logger.info("ЗАПУСК: ПРИОРИТЕТ 5 - Проверка публикации событий в EventBus")
        logger.info("=" * 80)

        try:
            from compliance_checks.priority_5_eventbus_events import EventBusEventChecker

            checker = EventBusEventChecker()
            results = checker.check_all_services()
            success = checker.print_results(results)

            self.results['eventbus_events'] = {
                'priority': 5,
                'passed': success
            }

            if success:
                logger.info("✅ ПРИОРИТЕТ 5 PASSED: EventBus интеграция в порядке")
            else:
                logger.warning("⚠️  ПРИОРИТЕТ 5 WARNING: Проблемы с EventBus интеграцией")

            return success

        except Exception as e:
            logger.error(f"❌ Ошибка при проверке EventBus: {e}", exc_info=True)
            return False

    def run_priority_6_orchestrator(self) -> bool:
        """
        ПРИОРИТЕТ 6: Контроль оркестратором
        """
        logger.info("")
        logger.info("=" * 80)
        logger.info("ЗАПУСК: ПРИОРИТЕТ 6 - Проверка контроля оркестратором")
        logger.info("=" * 80)

        try:
            from compliance_checks.priority_6_orchestrator_control import OrchestratorControlChecker

            checker = OrchestratorControlChecker()
            results = checker.check_all_services()
            success = checker.print_results(results)

            self.results['orchestrator_control'] = {
                'priority': 6,
                'passed': success
            }

            if success:
                logger.info("✅ ПРИОРИТЕТ 6 PASSED: Контроль оркестратором в порядке")
            else:
                logger.warning("⚠️  ПРИОРИТЕТ 6 WARNING: Проблемы с контролем оркестратором")

            return success

        except Exception as e:
            logger.error(f"❌ Ошибка при проверке оркестратора: {e}", exc_info=True)
            return False

    def run_all_checks(self) -> bool:
        """
        Запустить все проверки в правильном порядке

        Returns:
            True если все критичные проверки прошли
        """
        logger.info("╔" + "=" * 78 + "╗")
        logger.info("║" + " " * 15 + "ПРОЕКТНЫЙ МЕНЕДЖЕР - ПРОВЕРКИ СООТВЕТСТВИЯ" + " " * 21 + "║")
        logger.info("╚" + "=" * 78 + "╝")
        logger.info("")
        logger.info(f"Дата запуска: {self.start_time.isoformat()}")
        logger.info("")

        # ПРИОРИТЕТ 1: Конфликты портов (КРИТИЧНО - блокирующая проверка)
        priority_1_passed = self.run_priority_1_port_conflicts()

        if not priority_1_passed:
            logger.error("")
            logger.error("=" * 80)
            logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА: Обнаружены конфликты портов")
            logger.error("=" * 80)
            logger.error("Невозможно продолжить проверки пока не будут устранены конфликты портов.")
            logger.error("Пожалуйста, проверьте конфигурацию и перезапустите проверку.")
            self._print_final_summary()
            return False

        # ПРИОРИТЕТ 2: Метрики (некритично, но важно)
        priority_2_passed = self.run_priority_2_metrics()

        # ПРИОРИТЕТ 3: БД (некритично, но важно)
        priority_3_passed = self.run_priority_3_database()

        # ПРИОРИТЕТ 4: KPI регистрация
        priority_4_passed = self.run_priority_4_kpi()

        # ПРИОРИТЕТ 5: EventBus события
        priority_5_passed = self.run_priority_5_eventbus()

        # ПРИОРИТЕТ 6: Контроль оркестратором
        priority_6_passed = self.run_priority_6_orchestrator()

        # Итоговый отчет
        self._print_final_summary()

        # Проверка прошла если критичные проверки OK
        return priority_1_passed

    def _print_final_summary(self):
        """Вывести итоговую сводку"""
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()

        logger.info("")
        logger.info("╔" + "=" * 78 + "╗")
        logger.info("║" + " " * 28 + "ИТОГОВАЯ СВОДКА" + " " * 35 + "║")
        logger.info("╚" + "=" * 78 + "╝")
        logger.info("")

        logger.info(f"Время выполнения: {duration:.2f}с")
        logger.info("")

        # Результаты по приоритетам
        logger.info("Результаты проверок:")

        for check_name, result in self.results.items():
            priority = result.get('priority', '?')
            passed = result.get('passed', False)
            icon = "✅" if passed else "❌"

            logger.info(f"  {icon} Приоритет {priority}: {check_name.replace('_', ' ').title()}")

        logger.info("")

        # Общий статус
        all_passed = all(r.get('passed', False) for r in self.results.values())
        critical_passed = self.results.get('port_conflicts', {}).get('passed', False)

        if all_passed:
            logger.info("╔" + "=" * 78 + "╗")
            logger.info("║" + " " * 20 + "✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО ✅" + " " * 24 + "║")
            logger.info("╚" + "=" * 78 + "╝")
        elif critical_passed:
            logger.info("╔" + "=" * 78 + "╗")
            logger.info("║" + " " * 15 + "⚠️  КРИТИЧНЫЕ ПРОВЕРКИ ПРОЙДЕНЫ, ЕСТЬ ПРЕДУПРЕЖДЕНИЯ" + " " * 13 + "║")
            logger.info("╚" + "=" * 78 + "╝")
        else:
            logger.info("╔" + "=" * 78 + "╗")
            logger.info("║" + " " * 22 + "❌ КРИТИЧНЫЕ ПРОВЕРКИ ПРОВАЛЕНЫ ❌" + " " * 22 + "║")
            logger.info("╚" + "=" * 78 + "╝")

    def export_state_for_central_brain(self) -> Dict:
        """
        Экспортировать фактическое состояние для Центрального Мозга

        Центральный мозг получает ТОЛЬКО фактическое состояние,
        без информации о том, как "должно быть".

        Returns:
            Фактическое состояние системы
        """
        # Импортируем проверки
        try:
            from compliance_checks.priority_1_port_conflicts import PortConflictDetector
            from compliance_checks.priority_2_metrics_integration import MetricsIntegrationChecker
            from compliance_checks.priority_3_database_connections import DatabaseConnectionChecker

            # Собираем фактическое состояние
            port_detector = PortConflictDetector()
            metrics_checker = MetricsIntegrationChecker()
            db_checker = DatabaseConnectionChecker()

            # Получаем состояния
            port_state = port_detector.get_port_map_for_central_brain()
            metrics_state = metrics_checker.get_metrics_state_for_central_brain()
            db_state = db_checker.get_database_state_for_central_brain()

            return {
                'timestamp': datetime.utcnow().isoformat(),
                'ports': port_state,
                'metrics': metrics_state,
                'databases': db_state,
                'source': 'project_manager_compliance_checks'
            }

        except Exception as e:
            logger.error(f"Ошибка при экспорте состояния: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }


def main():
    """Основная функция"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )

    runner = ComplianceCheckRunner()
    success = runner.run_all_checks()

    # Опционально: экспортируем состояние для Центрального Мозга
    if '--export-state' in sys.argv:
        import json

        state = runner.export_state_for_central_brain()
        print("\n\n" + "=" * 80)
        print("ФАКТИЧЕСКОЕ СОСТОЯНИЕ ДЛЯ ЦЕНТРАЛЬНОГО МОЗГА:")
        print("=" * 80)
        print(json.dumps(state, indent=2, ensure_ascii=False))

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
