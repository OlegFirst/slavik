#!/usr/bin/env python3
"""
Automation Toolkit Manager - Запуск инструментов анализа
MIO Manager использует эти инструменты для принятия решений
"""

import sys
from pathlib import Path
import subprocess
import json
import asyncio
from typing import Dict, List, Optional
from datetime import datetime

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "tools"))

from analyzers.ast_analyzer import ASTAnalyzer
from analyzers.dependency_mapper import DependencyMapper
from generators.test_generator import TestGenerator
from prometheus_client import Gauge, Counter

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from repositories import ReportsRepository
from models.database import AnalysisType


# Prometheus metrics
service_coverage = Gauge('mio_service_coverage_percentage', 'Service monitoring coverage')
services_total = Gauge('mio_services_total', 'Total services discovered')
unmonitored_services = Gauge('mio_unmonitored_services', 'Unmonitored services count')

security_high_issues = Gauge('mio_security_high_issues', 'High severity security issues')
security_medium_issues = Gauge('mio_security_medium_issues', 'Medium severity security issues')

code_complexity_avg = Gauge('mio_code_complexity_avg', 'Average code complexity', ['service'])
code_complexity_max = Gauge('mio_code_complexity_max', 'Max code complexity', ['service'])

dependency_graph_nodes = Gauge('mio_dependency_graph_nodes', 'Dependency graph nodes')
circular_dependencies = Gauge('mio_circular_dependencies', 'Circular dependencies detected')

actions_executed = Counter('mio_actions_executed_total', 'Actions executed', ['action_type'])


class AutomationToolkitManager:
    """Управление запуском Automation Toolkit инструментов"""

    def __init__(self, response_engine=None):
        self.ast_analyzer = ASTAnalyzer()
        self.dependency_mapper = DependencyMapper()
        self.test_generator = TestGenerator()

        # Automated Response Engine (опционально)
        self.response_engine = response_engine

        self.last_discovery = None
        self.last_security_scan = None
        self.last_complexity_analysis = {}

    async def discover_services(self) -> Dict:
        """
        Auto-discovery всех сервисов
        Возвращает список сервисов и coverage
        """
        print("🔍 Running service discovery...")

        # Run AST analyzer
        results = self.ast_analyzer.analyze_project()

        # Find monitoring endpoints (/health, /metrics)
        monitoring_endpoints = [
            e for e in results['endpoints']
            if e['path'] in ['/health', '/metrics', '/ready', '/healthz']
        ]

        # Group by service
        services = {}
        for endpoint in monitoring_endpoints:
            service_name = self._extract_service_name(endpoint['file'])
            if service_name not in services:
                services[service_name] = {
                    'name': service_name,
                    'endpoints': [],
                    'has_health': False,
                    'has_metrics': False
                }

            services[service_name]['endpoints'].append(endpoint)

            if endpoint['path'] in ['/health', '/healthz']:
                services[service_name]['has_health'] = True
            if endpoint['path'] == '/metrics':
                services[service_name]['has_metrics'] = True

        # Calculate coverage
        monitored = sum(1 for s in services.values() if s['has_health'] and s['has_metrics'])
        total = len(services)
        coverage_pct = (monitored / total * 100) if total > 0 else 0

        # Update Prometheus metrics
        service_coverage.set(coverage_pct)
        services_total.set(total)
        unmonitored_services.set(total - monitored)

        result = {
            'total_services': total,
            'monitored_services': monitored,
            'services': list(services.values()),
            'coverage': {
                'percentage': coverage_pct,
                'monitored': monitored,
                'total': total
            },
            'timestamp': datetime.utcnow().isoformat()
        }

        self.last_discovery = result
        actions_executed.labels(action_type='service_discovery').inc()

        # Save to database
        try:
            ReportsRepository.save_service_discovery(
                total_services=total,
                monitored_services=monitored,
                unmonitored_services=total - monitored,
                coverage_percentage=coverage_pct,
                services_list=list(services.values())
            )
        except Exception as e:
            print(f"⚠️  Failed to save service discovery to DB: {e}")

        return result

    async def analyze_dependencies(self, service_name: Optional[str] = None) -> Dict:
        """
        Root cause analysis через dependency graph
        Если service_name указан - анализ только для него
        """
        print(f"🔗 Analyzing dependencies{f' for {service_name}' if service_name else ''}...")

        # Run dependency mapper
        results = self.dependency_mapper.analyze_dependencies()

        if service_name:
            # Specific service analysis
            deps = results['dependencies'].get(service_name, [])

            # Check health of dependencies (would call Prometheus here)
            down_deps = await self._check_dependencies_health(deps)

            return {
                'service': service_name,
                'dependencies': deps,
                'dependency_count': len(deps),
                'down_dependencies': down_deps,
                'root_cause': down_deps[0] if down_deps else None
            }
        else:
            # Full dependency analysis
            dependency_graph_nodes.set(results['statistics']['total_modules'])

            # Detect circular dependencies
            cycles = self.dependency_mapper.detect_circular_dependencies()
            circular_dependencies.set(len(cycles))

            actions_executed.labels(action_type='dependency_analysis').inc()

            result_data = {
                'statistics': results['statistics'],
                'circular_dependencies': cycles,
                'graph_nodes': results['statistics']['total_modules'],
                'graph_edges': results['statistics']['total_dependencies']
            }

            # Save to database
            try:
                ReportsRepository.save_dependency_analysis(
                    total_modules=results['statistics']['total_modules'],
                    total_dependencies=results['statistics']['total_dependencies'],
                    circular_dependencies_count=len(cycles),
                    circular_dependencies=cycles,
                    dependency_graph=results.get('graph', {})
                )
            except Exception as e:
                print(f"⚠️  Failed to save dependency analysis to DB: {e}")

            return result_data

    async def run_security_scan(self) -> Dict:
        """
        Security scan через Bandit
        Возвращает список уязвимостей
        """
        print("🔒 Running security scan...")

        result = subprocess.run(
            ['bandit', '-r', 'platform-services/', '-f', 'json', '-ll'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            issues = {'results': []}
        else:
            try:
                issues = json.loads(result.stdout)
            except:
                issues = {'results': []}

        # Categorize by severity
        high = [i for i in issues['results'] if i['issue_severity'] == 'HIGH']
        medium = [i for i in issues['results'] if i['issue_severity'] == 'MEDIUM']
        low = [i for i in issues['results'] if i['issue_severity'] == 'LOW']

        # Update Prometheus metrics
        security_high_issues.set(len(high))
        security_medium_issues.set(len(medium))

        actions_executed.labels(action_type='security_scan').inc()

        scan_result = {
            'status': 'clean' if not high else 'issues_found',
            'high_severity': len(high),
            'medium_severity': len(medium),
            'low_severity': len(low),
            'high_issues': high,
            'timestamp': datetime.utcnow().isoformat()
        }

        self.last_security_scan = scan_result

        # Save to database
        report_id = None
        try:
            report_id = ReportsRepository.save_security_scan(
                high_count=len(high),
                medium_count=len(medium),
                low_count=len(low),
                high_issues=high,
                all_issues=issues['results']
            )
        except Exception as e:
            print(f"⚠️  Failed to save security scan to DB: {e}")

        # 🚨 AUTOMATED RESPONSE: Если есть HIGH severity проблемы
        if self.response_engine and len(high) > 0:
            print(f"🤖 Triggering automated response for {len(high)} HIGH security issues...")
            try:
                response = await self.response_engine.handle_security_incident(
                    scan_result=scan_result,
                    report_id=report_id
                )
                scan_result['automated_response'] = response
                print(f"✅ Automated response: workflow_id={response.get('workflow_id')}")
            except Exception as e:
                print(f"⚠️  Automated response failed: {e}")

        return scan_result

    async def analyze_code_complexity(self, service_name: str) -> Dict:
        """
        Code complexity analysis через Radon
        """
        print(f"📊 Analyzing code complexity for {service_name}...")

        service_path = f'platform-services/{service_name}-service'

        result = subprocess.run(
            ['radon', 'cc', service_path, '-j'],
            capture_output=True,
            text=True
        )

        try:
            complexity = json.loads(result.stdout)
        except:
            complexity = {}

        # Calculate metrics
        all_complexities = []
        high_complexity_funcs = []

        for file_path, functions in complexity.items():
            for func in functions:
                all_complexities.append(func['complexity'])
                if func['complexity'] > 15:
                    high_complexity_funcs.append({
                        'name': func['name'],
                        'complexity': func['complexity'],
                        'file': file_path
                    })

        avg_complexity = sum(all_complexities) / len(all_complexities) if all_complexities else 0
        max_complexity = max(all_complexities) if all_complexities else 0

        # Update Prometheus metrics
        code_complexity_avg.labels(service=service_name).set(avg_complexity)
        code_complexity_max.labels(service=service_name).set(max_complexity)

        actions_executed.labels(action_type='complexity_analysis').inc()

        analysis_result = {
            'service': service_name,
            'avg_complexity': round(avg_complexity, 2),
            'max_complexity': max_complexity,
            'high_complexity_count': len(high_complexity_funcs),
            'high_complexity_functions': high_complexity_funcs,
            'timestamp': datetime.utcnow().isoformat()
        }

        self.last_complexity_analysis[service_name] = analysis_result

        # Save to database
        try:
            ReportsRepository.save_complexity_analysis(
                service_name=service_name,
                avg_complexity=avg_complexity,
                max_complexity=max_complexity,
                high_complexity_count=len(high_complexity_funcs),
                high_complexity_functions=high_complexity_funcs
            )
        except Exception as e:
            print(f"⚠️  Failed to save complexity analysis to DB: {e}")

        return analysis_result

    async def generate_synthetic_tests(self, service_name: Optional[str] = None) -> Dict:
        """
        Генерация Synthetic Monitoring тестов
        """
        print(f"🧪 Generating synthetic tests{f' for {service_name}' if service_name else ''}...")

        # Generate tests
        self.test_generator.generate_all_tests()
        self.test_generator.generate_unit_tests()
        self.test_generator.generate_pytest_config()

        # Find generated test files
        test_dir = Path('tests/generated')
        api_tests = list(test_dir.glob('test_*_api.py'))
        tavern_tests = list(test_dir.glob('tavern_test_*.yaml'))

        actions_executed.labels(action_type='test_generation').inc()

        return {
            'status': 'generated',
            'api_tests': [str(f) for f in api_tests],
            'tavern_tests': [str(f) for f in tavern_tests],
            'total_tests': len(api_tests) + len(tavern_tests),
            'timestamp': datetime.utcnow().isoformat()
        }

    async def create_improvement_task(self, issue_type: str, details: Dict) -> Dict:
        """
        Формирование задачи для улучшения/исправления
        Отправляется в Orchestrator
        """
        task = {
            'task_id': f"{issue_type}_{datetime.utcnow().timestamp()}",
            'type': issue_type,
            'priority': self._calculate_priority(issue_type, details),
            'details': details,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'pending'
        }

        actions_executed.labels(action_type='task_created').inc()

        return task

    def _extract_service_name(self, file_path: str) -> str:
        """Extract service name from file path"""
        parts = Path(file_path).parts
        for i, part in enumerate(parts):
            if part.endswith('-service'):
                return part.replace('-service', '')
        return 'unknown'

    async def _check_dependencies_health(self, dependencies: List[str]) -> List[str]:
        """Check health of dependencies (placeholder)"""
        # Would query Prometheus here
        # For now, return empty list
        return []

    def _calculate_priority(self, issue_type: str, details: Dict) -> str:
        """Calculate task priority"""
        if issue_type == 'security' and details.get('high_severity', 0) > 0:
            return 'critical'
        elif issue_type == 'service_down':
            return 'critical'
        elif issue_type == 'high_complexity':
            return 'medium'
        else:
            return 'low'
