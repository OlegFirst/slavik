#!/usr/bin/env python3
"""
Dependency Validator - Validates SERVICE_CATALOG.yaml against real code
Автоматически находит несоответствия между документацией и реальными зависимостями
"""

import ast
import yaml
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import re

class DependencyValidator:
    def __init__(self, catalog_path: str = "docs/architecture/SERVICE_CATALOG.yaml"):
        with open(catalog_path) as f:
            self.catalog = yaml.safe_load(f)

        self.real_dependencies = defaultdict(set)
        self.documented_dependencies = {}
        self.errors = []
        self.warnings = []

    def validate(self) -> Dict:
        """Полная валидация: реальные зависимости vs документированные"""
        print("🔍 Validating dependencies...")

        # 1. Извлечь реальные зависимости из кода
        self._scan_real_dependencies()

        # 2. Извлечь документированные зависимости из catalog
        self._extract_documented_dependencies()

        # 3. Сравнить и найти несоответствия
        self._compare_dependencies()

        # 4. Найти порты в коде
        self._validate_ports()

        # 5. Проверить существование сервисов
        self._validate_service_existence()

        return {
            'real_dependencies': {k: list(v) for k, v in self.real_dependencies.items()},
            'documented_dependencies': {k: list(v) if isinstance(v, set) else v for k, v in self.documented_dependencies.items()},
            'errors': self.errors,
            'warnings': self.warnings,
            'stats': self._calculate_stats()
        }

    def _scan_real_dependencies(self):
        """Сканировать реальный код и найти зависимости"""
        print("📂 Scanning real code dependencies...")

        # Сканировать intelligent-core
        self._scan_directory(Path("intelligent-core"), "ai_foundation")

        # Сканировать platform-services
        self._scan_directory(Path("platform-services"), "platform_services")

        # Сканировать infrastructure
        self._scan_directory(Path("infrastructure"), "infrastructure")

    def _scan_directory(self, directory: Path, service_type: str):
        """Рекурсивно сканировать директорию"""
        if not directory.exists():
            return

        for py_file in directory.rglob("*.py"):
            # Пропустить venv, __pycache__, tests
            if any(x in str(py_file) for x in ['venv', '__pycache__', 'test_', '.pytest']):
                continue

            try:
                self._analyze_file_dependencies(py_file, service_type)
            except Exception as e:
                pass  # Игнорировать ошибки парсинга

    def _analyze_file_dependencies(self, file_path: Path, service_type: str):
        """Анализировать зависимости в файле"""
        with open(file_path) as f:
            content = f.read()
            tree = ast.parse(content, filename=str(file_path))

        service_name = self._get_service_name(file_path)

        # 1. Найти импорты
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dep = self._classify_dependency(alias.name)
                    if dep:
                        self.real_dependencies[service_name].add(dep)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dep = self._classify_dependency(node.module)
                    if dep:
                        self.real_dependencies[service_name].add(dep)

        # 2. Найти упоминания других сервисов в строках
        # Паттерны: URLs, connection strings, service names
        patterns = [
            r'http://([a-z_-]+):(\d+)',  # HTTP URLs
            r'redis://([^:]+):',          # Redis connections
            r'postgresql://([^:]+):',     # PostgreSQL connections
            r'temporal\.io',              # Temporal
            r'supabase\.co',              # Supabase
            r'qdrant\.io',                # Qdrant
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    dep = self._classify_string_dependency(match[0])
                else:
                    dep = self._classify_string_dependency(match)
                if dep:
                    self.real_dependencies[service_name].add(dep)

    def _get_service_name(self, file_path: Path) -> str:
        """Получить имя сервиса из пути к файлу"""
        parts = file_path.parts

        # intelligent-core/workflow_intelligence → workflow_intelligence
        if 'intelligent-core' in parts:
            idx = parts.index('intelligent-core')
            if idx + 1 < len(parts):
                return parts[idx + 1]

        # platform-services/bia-service → bia_service
        if 'platform-services' in parts:
            idx = parts.index('platform-services')
            if idx + 1 < len(parts):
                return parts[idx + 1].replace('-', '_')

        # infrastructure/database/postgresql → database_postgresql
        if 'infrastructure' in parts:
            idx = parts.index('infrastructure')
            if idx + 2 < len(parts):
                return f"{parts[idx + 1]}_{parts[idx + 2]}"
            elif idx + 1 < len(parts):
                return parts[idx + 1]

        return "unknown"

    def _classify_dependency(self, import_name: str) -> str:
        """Классифицировать импорт в категорию зависимости"""
        # database/postgresql
        if any(x in import_name for x in ['psycopg', 'sqlalchemy', 'supabase']):
            return 'database/postgresql'

        # database/vector-db
        if 'qdrant' in import_name:
            return 'database/vector-db'

        # runtime/eventbus
        if 'eventbus' in import_name or 'redis' in import_name.lower():
            return 'runtime/eventbus'

        # temporal
        if 'temporal' in import_name:
            return 'external/temporal-cloud'

        # shared libraries
        if import_name.startswith('shared.'):
            return f'shared/{import_name.split(".")[1]}'

        # AI services
        if 'community_intelligence' in import_name:
            return 'ai_services/community_intelligence'
        if 'collective' in import_name:
            return 'ai_services/collective'
        if 'predictive' in import_name:
            return 'ai_services/predictive'
        if 'learning_system' in import_name or 'learning-system' in import_name:
            return 'ai_services/learning_system'
        if 'living_docs' in import_name or 'living-docs' in import_name:
            return 'ai_services/living_docs'

        # AI foundation
        if 'workflow_intelligence' in import_name:
            return 'ai_foundation/workflow_intelligence'
        if 'workflow_engine' in import_name or 'workflow-engine' in import_name:
            return 'ai_foundation/workflow_engine'
        if 'expertise_center' in import_name or 'expertise-center' in import_name:
            return 'ai_foundation/expertise_center'

        return None

    def _classify_string_dependency(self, string: str) -> str:
        """Классифицировать зависимость из строки (URL, connection string)"""
        # Порты и сервисы
        service_ports = {
            '8001': 'ai_foundation/workflow_intelligence',
            '8006': 'ai_foundation/ai_workflow_optimizer',
            '8002': 'ai_foundation/workflow_engine',
            '8030': 'ai_services/community_intelligence',
            '8031': 'ai_services/predictive',
            '8032': 'ai_services/collective',
            '8033': 'ai_services/learning_system',
            '8034': 'ai_services/living_docs',
            '5432': 'database/postgresql',
            '6379': 'runtime/eventbus',
        }

        if string in service_ports:
            return service_ports[string]

        # External services
        if 'temporal' in string:
            return 'external/temporal-cloud'
        if 'supabase' in string:
            return 'database/postgresql'
        if 'qdrant' in string:
            return 'database/vector-db'
        if 'redis' in string:
            return 'runtime/eventbus'

        return None

    def _extract_documented_dependencies(self):
        """Извлечь зависимости из SERVICE_CATALOG.yaml"""
        print("📖 Extracting documented dependencies...")

        # AI Foundation
        if 'ai_foundation' in self.catalog:
            for service_name, service_info in self.catalog['ai_foundation'].items():
                if 'dependencies' in service_info:
                    deps = set()
                    if 'infrastructure' in service_info['dependencies']:
                        for dep in service_info['dependencies']['infrastructure']:
                            deps.add(dep)
                    if 'external' in service_info['dependencies']:
                        for dep in service_info['dependencies']['external']:
                            deps.add(f'external/{dep}')
                    if 'ai_services' in service_info['dependencies']:
                        for dep in service_info['dependencies']['ai_services']:
                            deps.add(f'ai_services/{dep}')
                    self.documented_dependencies[service_name] = deps

        # AI Services
        if 'ai_services' in self.catalog:
            for service_name, service_info in self.catalog['ai_services'].items():
                if 'dependencies' in service_info:
                    deps = set()
                    if 'infrastructure' in service_info['dependencies']:
                        for dep in service_info['dependencies']['infrastructure']:
                            deps.add(dep)
                    self.documented_dependencies[service_name] = deps

        # Platform Services
        if 'platform_services' in self.catalog:
            for service_name, service_info in self.catalog['platform_services'].items():
                if 'dependencies' in service_info:
                    deps = set()
                    if 'ai_foundation' in service_info['dependencies']:
                        for dep in service_info['dependencies']['ai_foundation']:
                            deps.add(f'ai_foundation/{dep}')
                    if 'ai_services' in service_info['dependencies']:
                        for dep in service_info['dependencies']['ai_services']:
                            deps.add(f'ai_services/{dep}')
                    if 'infrastructure' in service_info['dependencies']:
                        for dep in service_info['dependencies']['infrastructure']:
                            deps.add(dep)
                    self.documented_dependencies[service_name] = deps

    def _compare_dependencies(self):
        """Сравнить реальные и документированные зависимости"""
        print("⚖️  Comparing dependencies...")

        all_services = set(self.real_dependencies.keys()) | set(self.documented_dependencies.keys())

        for service in all_services:
            real = self.real_dependencies.get(service, set())
            documented = self.documented_dependencies.get(service, set())

            # Недокументированные зависимости (есть в коде, но не в catalog)
            missing_in_docs = real - documented
            if missing_in_docs:
                self.errors.append({
                    'type': 'undocumented_dependency',
                    'service': service,
                    'missing_dependencies': list(missing_in_docs),
                    'severity': 'HIGH',
                    'message': f'{service} has undocumented dependencies: {", ".join(missing_in_docs)}'
                })

            # Лишние зависимости (есть в catalog, но не в коде)
            missing_in_code = documented - real
            if missing_in_code:
                self.warnings.append({
                    'type': 'unused_dependency',
                    'service': service,
                    'unused_dependencies': list(missing_in_code),
                    'severity': 'MEDIUM',
                    'message': f'{service} has documented but unused dependencies: {", ".join(missing_in_code)}'
                })

    def _validate_ports(self):
        """Проверить что порты в коде соответствуют catalog"""
        print("🔌 Validating ports...")

        # Извлечь порты из catalog
        documented_ports = {}
        for layer in ['ai_foundation', 'ai_services', 'platform_services', 'infrastructure']:
            if layer not in self.catalog:
                continue
            for service_name, service_info in self.catalog[layer].items():
                if isinstance(service_info, dict) and 'port' in service_info and service_info['port']:
                    documented_ports[service_name] = service_info['port']

        # Найти порты в коде
        real_ports = {}
        for root_dir in ['intelligent-core', 'platform-services', 'infrastructure']:
            root = Path(root_dir)
            if not root.exists():
                continue

            for py_file in root.rglob("main.py"):
                if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                    continue

                try:
                    with open(py_file) as f:
                        content = f.read()
                        # Найти uvicorn.run(..., port=XXXX)
                        port_match = re.search(r'port\s*=\s*(\d+)', content)
                        if port_match:
                            service_name = self._get_service_name(py_file)
                            real_ports[service_name] = int(port_match.group(1))
                except:
                    pass

        # Сравнить
        for service_name in set(documented_ports.keys()) | set(real_ports.keys()):
            doc_port = documented_ports.get(service_name)
            real_port = real_ports.get(service_name)

            if doc_port and real_port and doc_port != real_port:
                self.errors.append({
                    'type': 'port_mismatch',
                    'service': service_name,
                    'documented_port': doc_port,
                    'real_port': real_port,
                    'severity': 'CRITICAL',
                    'message': f'{service_name} port mismatch: documented={doc_port}, real={real_port}'
                })
            elif doc_port and not real_port:
                self.warnings.append({
                    'type': 'port_not_found_in_code',
                    'service': service_name,
                    'documented_port': doc_port,
                    'severity': 'LOW',
                    'message': f'{service_name} has documented port {doc_port} but not found in code'
                })

    def _validate_service_existence(self):
        """Проверить что все сервисы из catalog реально существуют"""
        print("📁 Validating service existence...")

        for layer in ['ai_foundation', 'ai_services', 'platform_services']:
            if layer not in self.catalog:
                continue

            for service_name, service_info in self.catalog[layer].items():
                if isinstance(service_info, dict) and 'location' in service_info:
                    location = Path(service_info['location'])
                    if not location.exists():
                        self.errors.append({
                            'type': 'service_not_found',
                            'service': service_name,
                            'location': str(location),
                            'severity': 'CRITICAL',
                            'message': f'{service_name} location does not exist: {location}'
                        })

    def _calculate_stats(self) -> Dict:
        """Статистика валидации"""
        return {
            'total_services_documented': len(self.documented_dependencies),
            'total_services_in_code': len(self.real_dependencies),
            'total_errors': len(self.errors),
            'total_warnings': len(self.warnings),
            'critical_errors': len([e for e in self.errors if e.get('severity') == 'CRITICAL']),
            'high_errors': len([e for e in self.errors if e.get('severity') == 'HIGH']),
            'accuracy': self._calculate_accuracy()
        }

    def _calculate_accuracy(self) -> float:
        """Рассчитать точность документации (0-100%)"""
        if not self.documented_dependencies:
            return 0.0

        total_documented = sum(len(deps) for deps in self.documented_dependencies.values())
        total_errors = len([e for e in self.errors if e['type'] == 'undocumented_dependency'])

        if total_documented == 0:
            return 0.0

        accuracy = ((total_documented - total_errors) / total_documented) * 100
        return max(0.0, min(100.0, accuracy))

    def generate_report(self, output_file: str = "infrastructure/AI-office-infrastructure/devops-agent/reports-generated/dependency_validation.json"):
        """Сгенерировать отчет"""
        result = self.validate()

        # Сохранить JSON
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)

        # Вывести в консоль
        print("\n" + "="*60)
        print("📊 DEPENDENCY VALIDATION REPORT")
        print("="*60)

        stats = result['stats']
        print(f"\n✅ Services documented: {stats['total_services_documented']}")
        print(f"✅ Services in code: {stats['total_services_in_code']}")
        print(f"📊 Documentation accuracy: {stats['accuracy']:.1f}%")
        print(f"\n❌ Critical errors: {stats['critical_errors']}")
        print(f"❌ High errors: {stats['high_errors']}")
        print(f"⚠️  Total warnings: {stats['total_warnings']}")

        if result['errors']:
            print(f"\n🔴 ERRORS ({len(result['errors'])}):")
            for error in result['errors'][:10]:  # Показать первые 10
                print(f"  • [{error['severity']}] {error['message']}")
            if len(result['errors']) > 10:
                print(f"  ... and {len(result['errors']) - 10} more")

        if result['warnings']:
            print(f"\n⚠️  WARNINGS ({len(result['warnings'])}):")
            for warning in result['warnings'][:5]:  # Показать первые 5
                print(f"  • [{warning['severity']}] {warning['message']}")
            if len(result['warnings']) > 5:
                print(f"  ... and {len(result['warnings']) - 5} more")

        print(f"\n💾 Full report saved to: {output_file}")
        print("="*60 + "\n")

        return result


if __name__ == "__main__":
    validator = DependencyValidator()
    result = validator.generate_report()

    # Exit code
    import sys
    if result['stats']['critical_errors'] > 0:
        sys.exit(1)  # Fail on critical errors
    elif result['stats']['high_errors'] > 5:
        sys.exit(1)  # Fail on too many high errors
    else:
        sys.exit(0)  # Success
