#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock System CLI
===============

Командная строка для управления системой моков с детекцией циклов.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

from mock_system import (
    ControllableMockSystem, MockTarget, MockType,
    get_mock_system
)

class MockCLI:
    """CLI для системы моков"""

    def __init__(self):
        self.mock_system = get_mock_system()

    def load_config(self, config_file: str) -> bool:
        """Загрузить конфигурацию из файла"""
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                print(f"Error: Configuration file not found: {config_file}")
                return False

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Загрузка целей моков
            for target_data in config.get("mock_targets", {}).values():
                target = MockTarget(
                    id=target_data["id"],
                    type=MockType(target_data["type"]),
                    endpoint=target_data["endpoint"],
                    response_data=target_data["response_data"],
                    delay_ms=target_data.get("delay_ms", 0),
                    failure_rate=target_data.get("failure_rate", 0.0),
                    tags=target_data.get("tags", [])
                )
                self.mock_system.register_target(target)

            # Загрузка правил маршрутизации
            for pattern, targets in config.get("routing_rules", {}).items():
                self.mock_system.set_routing_rule(pattern, targets)

            # Активация моков по умолчанию
            for target_id in config.get("default_active_mocks", []):
                self.mock_system.activate_mock(target_id)

            print(f"Configuration loaded from {config_file}")
            print(f"Loaded {len(config.get('mock_targets', {}))} targets")
            print(f"Activated {len(config.get('default_active_mocks', []))} mocks")
            return True

        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False

    def run_scenario(self, config_file: str, scenario_name: str) -> bool:
        """Запустить тестовый сценарий"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            scenarios = config.get("test_scenarios", {})
            if scenario_name not in scenarios:
                print(f"Error: Scenario '{scenario_name}' not found")
                print(f"Available scenarios: {list(scenarios.keys())}")
                return False

            scenario = scenarios[scenario_name]
            print(f"Running scenario: {scenario['description']}")

            # Деактивировать все моки
            for target_id in list(self.mock_system.active_mocks):
                self.mock_system.deactivate_mock(target_id)

            # Активировать моки для сценария
            for target_id in scenario.get("active_mocks", []):
                if not self.mock_system.activate_mock(target_id):
                    print(f"Warning: Could not activate mock {target_id}")

            # Применить переопределения моков
            mock_overrides = scenario.get("mock_overrides", {})
            for target_id, overrides in mock_overrides.items():
                if target_id in self.mock_system.targets:
                    target = self.mock_system.targets[target_id]
                    for key, value in overrides.items():
                        setattr(target, key, value)
                    print(f"Applied overrides to {target_id}: {overrides}")

            # Выполнить тестовые вызовы
            test_calls = scenario.get("test_calls", [])
            for i, call_config in enumerate(test_calls):
                caller = call_config["caller"]
                endpoint = call_config["endpoint"]
                params = call_config.get("parameters", {})

                print(f"\nTest call {i+1}: {caller} -> {endpoint}")
                response = self.mock_system.route_call(caller, endpoint, params)

                if response is None:
                    print("  Result: No mock response (using real service)")
                else:
                    print(f"  Result: {json.dumps(response, indent=2)[:200]}...")

                # Проверка ожидаемых ключей
                expected_keys = call_config.get("expected_response_keys", [])
                if expected_keys and response:
                    missing_keys = [key for key in expected_keys if key not in str(response)]
                    if missing_keys:
                        print(f"  Warning: Missing expected keys: {missing_keys}")
                    else:
                        print(f"  Success: All expected keys found")

            # Создание искусственных циклов для тестирования
            artificial_cycles = scenario.get("artificial_cycles", [])
            for cycle in artificial_cycles:
                for i in range(len(cycle)):
                    caller = cycle[i]
                    target = cycle[(i + 1) % len(cycle)]
                    self.mock_system.cycle_detector.add_call(caller, target)
                print(f"Created artificial cycle: {' -> '.join(cycle)}")

            return True

        except Exception as e:
            print(f"Error running scenario: {e}")
            return False

    def show_status(self):
        """Показать статус системы моков"""
        status = self.mock_system.get_status()
        print("\n=== Mock System Status ===")
        print(f"State: {status['state']}")
        print(f"Total targets: {status['total_targets']}")
        print(f"Active mocks: {status['active_mocks']}")
        print(f"Total calls: {status['total_calls']}")
        print(f"Routing rules: {status['routing_rules']}")

        print("\n=== Targets ===")
        for target_id, target_info in status['targets'].items():
            active_status = "ACTIVE" if target_info['active'] else "inactive"
            print(f"  {target_id}: {target_info['type']} | {target_info['endpoint']} | {active_status}")

    def show_stats(self):
        """Показать статистику вызовов"""
        stats = self.mock_system.get_call_stats()
        print("\n=== Call Statistics ===")
        if stats['total_calls'] == 0:
            print("No calls made yet")
            return

        print(f"Total calls: {stats['total_calls']}")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        print(f"Average duration: {stats['avg_duration_ms']:.1f}ms")

        print("\n=== Target Usage ===")
        for target_id, count in stats['target_usage'].items():
            print(f"  {target_id}: {count} calls")

        print("\n=== Recent Calls ===")
        for call in stats['recent_calls']:
            status = "SUCCESS" if call['success'] else "FAILED"
            print(f"  {call['caller']} -> {call['target']}: {status} ({call['duration_ms']:.1f}ms)")

    def detect_cycles(self):
        """Обнаружить и показать циклы"""
        cycle_report = self.mock_system.detect_cycles()
        print("\n=== Cycle Detection Report ===")
        print(f"Total cycles detected: {cycle_report['total_cycles']}")

        if cycle_report['total_cycles'] == 0:
            print("No cycles detected")
        else:
            for i, cycle in enumerate(cycle_report['cycles']):
                print(f"\nCycle {i+1}:")
                print(f"  Path: {' -> '.join(cycle['nodes'])}")
                print(f"  Length: {cycle['cycle_length']}")
                print(f"  Call count: {cycle['call_count']}")

        graph_stats = cycle_report['graph_stats']
        print(f"\nGraph statistics:")
        print(f"  Nodes: {graph_stats['nodes']}")
        print(f"  Edges: {graph_stats['edges']}")
        print(f"  Recent calls: {graph_stats['recent_calls']}")

    def activate_mock(self, target_id: str):
        """Активировать мок"""
        if self.mock_system.activate_mock(target_id):
            print(f"Activated mock: {target_id}")
        else:
            print(f"Error: Could not activate mock: {target_id}")

    def deactivate_mock(self, target_id: str):
        """Деактивировать мок"""
        if self.mock_system.deactivate_mock(target_id):
            print(f"Deactivated mock: {target_id}")
        else:
            print(f"Mock was not active: {target_id}")

    def clear_history(self):
        """Очистить историю вызовов"""
        self.mock_system.clear_history()
        print("Call history cleared")

    def test_call(self, caller: str, endpoint: str, parameters: str = "{}"):
        """Выполнить тестовый вызов"""
        try:
            params = json.loads(parameters)
            response = self.mock_system.route_call(caller, endpoint, params)

            print(f"\nTest call: {caller} -> {endpoint}")
            print(f"Parameters: {json.dumps(params, indent=2)}")

            if response is None:
                print("Result: No mock response (would use real service)")
            else:
                print(f"Result: {json.dumps(response, indent=2)}")

        except json.JSONDecodeError:
            print(f"Error: Invalid JSON parameters: {parameters}")
        except Exception as e:
            print(f"Error executing test call: {e}")

def main():
    """Главная функция CLI"""
    parser = argparse.ArgumentParser(description="Mock System CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Команда load
    load_parser = subparsers.add_parser('load', help='Load configuration from file')
    load_parser.add_argument('config_file', help='Path to configuration file')

    # Команда scenario
    scenario_parser = subparsers.add_parser('scenario', help='Run test scenario')
    scenario_parser.add_argument('config_file', help='Path to configuration file')
    scenario_parser.add_argument('scenario_name', help='Name of scenario to run')

    # Команда status
    subparsers.add_parser('status', help='Show system status')

    # Команда stats
    subparsers.add_parser('stats', help='Show call statistics')

    # Команда cycles
    subparsers.add_parser('cycles', help='Detect and show cycles')

    # Команда activate
    activate_parser = subparsers.add_parser('activate', help='Activate mock')
    activate_parser.add_argument('target_id', help='Target ID to activate')

    # Команда deactivate
    deactivate_parser = subparsers.add_parser('deactivate', help='Deactivate mock')
    deactivate_parser.add_argument('target_id', help='Target ID to deactivate')

    # Команда clear
    subparsers.add_parser('clear', help='Clear call history')

    # Команда test
    test_parser = subparsers.add_parser('test', help='Execute test call')
    test_parser.add_argument('caller', help='Caller ID')
    test_parser.add_argument('endpoint', help='Endpoint to call')
    test_parser.add_argument('--params', default='{}', help='JSON parameters')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = MockCLI()

    if args.command == 'load':
        success = cli.load_config(args.config_file)
        sys.exit(0 if success else 1)

    elif args.command == 'scenario':
        # Сначала загрузить конфигурацию
        if cli.load_config(args.config_file):
            success = cli.run_scenario(args.config_file, args.scenario_name)
            sys.exit(0 if success else 1)
        else:
            sys.exit(1)

    elif args.command == 'status':
        cli.show_status()

    elif args.command == 'stats':
        cli.show_stats()

    elif args.command == 'cycles':
        cli.detect_cycles()

    elif args.command == 'activate':
        cli.activate_mock(args.target_id)

    elif args.command == 'deactivate':
        cli.deactivate_mock(args.target_id)

    elif args.command == 'clear':
        cli.clear_history()

    elif args.command == 'test':
        cli.test_call(args.caller, args.endpoint, args.params)

if __name__ == "__main__":
    main()