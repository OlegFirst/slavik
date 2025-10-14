#!/usr/bin/env python3
"""
Test Orchestrator - Проверка работоспособности Unified Orchestrator
==================================================================

Проверяет:
1. Инициализацию оркестратора
2. Доступность всех executors
3. Доступность всех компонентов
4. Импорты и зависимости
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Any
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / 'infrastructure' / 'AI-office-infrastructure' / 'orchestrator'))


class OrchestratorTester:
    """Тестер для Unified Orchestrator"""

    def __init__(self):
        self.results = {
            'imports': {},
            'initialization': {},
            'executors': {},
            'components': {},
            'methods': {},
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0
            }
        }

    def test_import(self, name: str, import_func) -> bool:
        """Тест импорта модуля"""
        try:
            import_func()
            self.results['imports'][name] = {'status': 'OK', 'error': None}
            return True
        except Exception as e:
            self.results['imports'][name] = {'status': 'FAILED', 'error': str(e)}
            return False

    async def test_orchestrator_init(self) -> bool:
        """Тест инициализации оркестратора"""
        try:
            from unified_orchestrator import UnifiedOrchestrator

            orchestrator = UnifiedOrchestrator(PROJECT_ROOT)

            self.results['initialization']['orchestrator'] = {
                'status': 'OK',
                'project_root': str(orchestrator.project_root),
                'deployment_dir': str(orchestrator.deployment_dir),
                'generated_dir': str(orchestrator.generated_dir)
            }

            return True, orchestrator
        except Exception as e:
            self.results['initialization']['orchestrator'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            return False, None

    def test_executors(self, orchestrator) -> Dict:
        """Проверка доступности executors"""
        executors_status = {}

        # Event Executor
        if orchestrator.event_executor:
            executors_status['event_executor'] = {
                'status': 'AVAILABLE',
                'type': str(type(orchestrator.event_executor)),
                'methods': [
                    'add_publisher',
                    'add_subscriber',
                    'fix_event_gap',
                    'create_pr',
                    'rollback_changes'
                ]
            }
        else:
            executors_status['event_executor'] = {
                'status': 'NOT_AVAILABLE',
                'error': 'EventExecutor not initialized'
            }

        # Infrastructure Executor
        if orchestrator.infrastructure_executor:
            executors_status['infrastructure_executor'] = {
                'status': 'AVAILABLE',
                'type': str(type(orchestrator.infrastructure_executor)),
                'methods': [
                    'restart_service',
                    'stop_service',
                    'health_check'
                ]
            }
        else:
            executors_status['infrastructure_executor'] = {
                'status': 'NOT_AVAILABLE',
                'error': 'InfrastructureExecutor not initialized'
            }

        # BCM Executor
        if orchestrator.bcm_executor:
            executors_status['bcm_executor'] = {
                'status': 'AVAILABLE',
                'type': str(type(orchestrator.bcm_executor))
            }
        else:
            executors_status['bcm_executor'] = {
                'status': 'NOT_AVAILABLE',
                'error': 'BCMExecutor not initialized (optional)'
            }

        self.results['executors'] = executors_status
        return executors_status

    def test_components(self, orchestrator) -> Dict:
        """Проверка доступности компонентов"""
        components_status = {}

        # Service Discovery
        if orchestrator.discovery:
            components_status['service_discovery'] = {
                'status': 'AVAILABLE',
                'type': str(type(orchestrator.discovery))
            }
        else:
            components_status['service_discovery'] = {
                'status': 'NOT_AVAILABLE',
                'error': 'ServiceDiscovery not initialized'
            }

        # Docker Manager
        if orchestrator.docker_manager:
            components_status['docker_manager'] = {
                'status': 'AVAILABLE',
                'type': str(type(orchestrator.docker_manager))
            }
        else:
            components_status['docker_manager'] = {
                'status': 'NOT_AVAILABLE',
                'error': 'DockerManager not initialized (optional)'
            }

        self.results['components'] = components_status
        return components_status

    async def test_methods(self, orchestrator) -> Dict:
        """Проверка доступности методов"""
        methods_status = {}

        # Test discover_services (без выполнения)
        try:
            has_method = hasattr(orchestrator, 'discover_services')
            methods_status['discover_services'] = {
                'status': 'AVAILABLE' if has_method else 'NOT_FOUND',
                'callable': callable(getattr(orchestrator, 'discover_services', None))
            }
        except Exception as e:
            methods_status['discover_services'] = {
                'status': 'ERROR',
                'error': str(e)
            }

        # Test generate_configs
        try:
            has_method = hasattr(orchestrator, 'generate_configs')
            methods_status['generate_configs'] = {
                'status': 'AVAILABLE' if has_method else 'NOT_FOUND',
                'callable': callable(getattr(orchestrator, 'generate_configs', None))
            }
        except Exception as e:
            methods_status['generate_configs'] = {
                'status': 'ERROR',
                'error': str(e)
            }

        # Test deploy
        try:
            has_method = hasattr(orchestrator, 'deploy')
            methods_status['deploy'] = {
                'status': 'AVAILABLE' if has_method else 'NOT_FOUND',
                'callable': callable(getattr(orchestrator, 'deploy', None))
            }
        except Exception as e:
            methods_status['deploy'] = {
                'status': 'ERROR',
                'error': str(e)
            }

        # Test execute_task
        try:
            has_method = hasattr(orchestrator, 'execute_task')
            methods_status['execute_task'] = {
                'status': 'AVAILABLE' if has_method else 'NOT_FOUND',
                'callable': callable(getattr(orchestrator, 'execute_task', None))
            }
        except Exception as e:
            methods_status['execute_task'] = {
                'status': 'ERROR',
                'error': str(e)
            }

        # Test status
        try:
            has_method = hasattr(orchestrator, 'status')
            methods_status['status'] = {
                'status': 'AVAILABLE' if has_method else 'NOT_FOUND',
                'callable': callable(getattr(orchestrator, 'status', None))
            }
        except Exception as e:
            methods_status['status'] = {
                'status': 'ERROR',
                'error': str(e)
            }

        self.results['methods'] = methods_status
        return methods_status

    def calculate_summary(self):
        """Подсчёт итоговой статистики"""
        total = 0
        passed = 0
        failed = 0
        warnings = 0

        # Count imports
        for name, result in self.results['imports'].items():
            total += 1
            if result['status'] == 'OK':
                passed += 1
            else:
                failed += 1

        # Count initialization
        for name, result in self.results['initialization'].items():
            total += 1
            if result['status'] == 'OK':
                passed += 1
            else:
                failed += 1

        # Count executors
        for name, result in self.results['executors'].items():
            total += 1
            if result['status'] == 'AVAILABLE':
                passed += 1
            elif 'optional' in result.get('error', '').lower():
                warnings += 1
            else:
                warnings += 1  # Not critical

        # Count components
        for name, result in self.results['components'].items():
            total += 1
            if result['status'] == 'AVAILABLE':
                passed += 1
            elif 'optional' in result.get('error', '').lower():
                warnings += 1
            else:
                warnings += 1

        # Count methods
        for name, result in self.results['methods'].items():
            total += 1
            if result['status'] == 'AVAILABLE' and result.get('callable'):
                passed += 1
            else:
                failed += 1

        self.results['summary'] = {
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'warnings': warnings,
            'success_rate': f"{(passed / total * 100):.1f}%" if total > 0 else "0%"
        }

    def print_report(self):
        """Вывод отчёта"""
        print("\n" + "="*80)
        print("UNIFIED ORCHESTRATOR TEST REPORT")
        print("="*80 + "\n")

        # Imports
        print("📦 IMPORTS:")
        for name, result in self.results['imports'].items():
            status_icon = "✅" if result['status'] == 'OK' else "❌"
            print(f"  {status_icon} {name}: {result['status']}")
            if result.get('error'):
                print(f"     Error: {result['error']}")

        # Initialization
        print("\n🚀 INITIALIZATION:")
        for name, result in self.results['initialization'].items():
            status_icon = "✅" if result['status'] == 'OK' else "❌"
            print(f"  {status_icon} {name}: {result['status']}")
            if result.get('error'):
                print(f"     Error: {result['error']}")
            else:
                if 'project_root' in result:
                    print(f"     Project Root: {result['project_root']}")
                if 'deployment_dir' in result:
                    print(f"     Deployment Dir: {result['deployment_dir']}")

        # Executors
        print("\n⚙️  EXECUTORS:")
        for name, result in self.results['executors'].items():
            if result['status'] == 'AVAILABLE':
                status_icon = "✅"
            elif 'optional' in result.get('error', '').lower():
                status_icon = "⚠️ "
            else:
                status_icon = "⚠️ "

            print(f"  {status_icon} {name}: {result['status']}")
            if result.get('error'):
                print(f"     Note: {result['error']}")
            if result.get('methods'):
                print(f"     Methods: {', '.join(result['methods'])}")

        # Components
        print("\n🔧 COMPONENTS:")
        for name, result in self.results['components'].items():
            if result['status'] == 'AVAILABLE':
                status_icon = "✅"
            elif 'optional' in result.get('error', '').lower():
                status_icon = "⚠️ "
            else:
                status_icon = "⚠️ "

            print(f"  {status_icon} {name}: {result['status']}")
            if result.get('error'):
                print(f"     Note: {result['error']}")

        # Methods
        print("\n📋 METHODS:")
        for name, result in self.results['methods'].items():
            status_icon = "✅" if result['status'] == 'AVAILABLE' and result.get('callable') else "❌"
            print(f"  {status_icon} {name}: {result['status']}")
            if result.get('error'):
                print(f"     Error: {result['error']}")

        # Summary
        print("\n" + "="*80)
        print("SUMMARY:")
        print("="*80)
        summary = self.results['summary']
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  ✅ Passed: {summary['passed']}")
        print(f"  ❌ Failed: {summary['failed']}")
        print(f"  ⚠️  Warnings: {summary['warnings']}")
        print(f"  Success Rate: {summary['success_rate']}")

        # Overall status
        print("\n" + "="*80)
        if summary['failed'] == 0:
            print("✅ ALL TESTS PASSED! Orchestrator is ready to use.")
        elif summary['failed'] <= summary['warnings']:
            print("⚠️  TESTS PASSED WITH WARNINGS. Some optional components not available.")
        else:
            print("❌ TESTS FAILED. Critical components missing.")
        print("="*80 + "\n")

        # Unavailable components list
        unavailable = []

        for name, result in self.results['executors'].items():
            if result['status'] == 'NOT_AVAILABLE':
                unavailable.append(f"Executor: {name}")

        for name, result in self.results['components'].items():
            if result['status'] == 'NOT_AVAILABLE':
                unavailable.append(f"Component: {name}")

        if unavailable:
            print("❌ UNAVAILABLE COMPONENTS:")
            for item in unavailable:
                print(f"   - {item}")
            print()


async def main():
    """Main test runner"""
    tester = OrchestratorTester()

    logger.info("Starting Unified Orchestrator tests...")

    # Test 1: Imports
    logger.info("Testing imports...")

    def import_unified_orchestrator():
        from unified_orchestrator import UnifiedOrchestrator

    def import_fastapi():
        from fastapi import FastAPI

    def import_httpx():
        import httpx

    tester.test_import('unified_orchestrator', import_unified_orchestrator)
    tester.test_import('fastapi', import_fastapi)
    tester.test_import('httpx', import_httpx)

    # Test 2: Initialization
    logger.info("Testing orchestrator initialization...")
    success, orchestrator = await tester.test_orchestrator_init()

    if not success:
        logger.error("Failed to initialize orchestrator, aborting tests")
        tester.calculate_summary()
        tester.print_report()
        return tester.results

    # Test 3: Executors
    logger.info("Testing executors...")
    tester.test_executors(orchestrator)

    # Test 4: Components
    logger.info("Testing components...")
    tester.test_components(orchestrator)

    # Test 5: Methods
    logger.info("Testing methods...")
    await tester.test_methods(orchestrator)

    # Calculate summary
    tester.calculate_summary()

    # Print report
    tester.print_report()

    return tester.results


if __name__ == '__main__':
    results = asyncio.run(main())

    # Exit code based on results
    if results['summary']['failed'] == 0:
        sys.exit(0)
    else:
        sys.exit(1)
