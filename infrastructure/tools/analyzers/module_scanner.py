#!/usr/bin/env python3
"""
Module Scanner - Прицельное сканирование модулей для документирования

Сканирует каждый модуль отдельно и генерирует детальное описание:
- Структура файлов
- Найденные зависимости
- API endpoints (если есть)
- Классы и функции
- Конфигурация
- README анализ

Использование:
    # Сканировать один модуль
    python3 tools/analyzers/module_scanner.py intelligent-core/workflow_intelligence

    # Сканировать весь раздел
    python3 tools/analyzers/module_scanner.py --section intelligent-core

    # Интерактивный режим
    python3 tools/analyzers/module_scanner.py --interactive
"""

import ast
import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


class ModuleScanner:
    def __init__(self, module_path: str):
        self.module_path = Path(module_path)
        self.module_name = self.module_path.name

        if not self.module_path.exists():
            raise FileNotFoundError(f"Module not found: {module_path}")

        self.result = {
            'module_name': self.module_name,
            'path': str(self.module_path),
            'structure': {},
            'dependencies': set(),
            'endpoints': [],
            'classes': [],
            'functions': [],
            'config': {},
            'metrics': {},
            'readme': None
        }

    def scan(self) -> Dict:
        """Полное сканирование модуля"""

        print(f"\n{'='*60}")
        print(f"📦 СКАНИРОВАНИЕ: {self.module_name}")
        print(f"📁 Путь: {self.module_path}")
        print(f"{'='*60}\n")

        # 1. Структура файлов
        self._scan_structure()

        # 2. README анализ
        self._scan_readme()

        # 3. Зависимости
        self._scan_dependencies()

        # 4. API endpoints
        self._scan_endpoints()

        # 5. Классы и функции
        self._scan_code()

        # 6. Конфигурация
        self._scan_config()

        # 7. Метрики
        self._calculate_metrics()

        return self.result

    def _scan_structure(self):
        """Сканировать структуру файлов"""
        print("📂 Сканирование структуры...")

        structure = defaultdict(list)

        for root, dirs, files in os.walk(self.module_path):
            # Пропустить venv, __pycache__, node_modules
            dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', 'node_modules', '.git']]

            rel_root = Path(root).relative_to(self.module_path)

            for file in files:
                ext = Path(file).suffix
                structure[str(rel_root)].append(file)

        self.result['structure'] = dict(structure)

        # Вывод краткой структуры
        total_files = sum(len(files) for files in structure.values())
        print(f"  ✓ Найдено файлов: {total_files}")
        print(f"  ✓ Директорий: {len(structure)}")

    def _scan_readme(self):
        """Анализ README файла"""
        print("📄 Поиск README...")

        readme_variants = ['README.md', 'readme.md', 'README.txt', 'README']

        for variant in readme_variants:
            readme_path = self.module_path / variant
            if readme_path.exists():
                with open(readme_path) as f:
                    content = f.read()
                    self.result['readme'] = {
                        'file': variant,
                        'size': len(content),
                        'lines': len(content.split('\n')),
                        'content': content[:1000]  # Первые 1000 символов
                    }
                print(f"  ✓ Найден: {variant} ({len(content)} символов)")
                return

        print("  ⚠ README не найден")

    def _scan_dependencies(self):
        """Сканировать зависимости"""
        print("🔗 Анализ зависимостей...")

        dependencies = set()

        # Поиск Python файлов
        for py_file in self.module_path.rglob('*.py'):
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue

            try:
                with open(py_file) as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            dependencies.add(self._classify_import(alias.name))

                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            dependencies.add(self._classify_import(node.module))

            except:
                continue

        self.result['dependencies'] = sorted(dependencies)
        print(f"  ✓ Найдено зависимостей: {len(dependencies)}")

        # Топ-5 зависимостей
        if dependencies:
            print("  📌 Топ зависимости:")
            for dep in sorted(dependencies)[:5]:
                print(f"     • {dep}")

    def _classify_import(self, import_name: str) -> str:
        """Классифицировать import"""

        # Infrastructure
        if any(x in import_name for x in ['psycopg', 'sqlalchemy', 'supabase']):
            return 'database/postgresql'
        if 'qdrant' in import_name:
            return 'database/vector-db'
        if 'eventbus' in import_name or 'redis' in import_name.lower():
            return 'runtime/eventbus'

        # External
        if 'temporal' in import_name:
            return 'external/temporal-cloud'
        if 'anthropic' in import_name or 'claude' in import_name.lower():
            return 'external/anthropic'

        # Shared
        if import_name.startswith('shared.'):
            return f"shared/{import_name.split('.')[1]}"

        # AI Foundation
        if any(x in import_name for x in ['workflow_intelligence', 'workflow_engine', 'expertise_center']):
            return f"ai_foundation/{import_name.split('.')[0]}"

        # AI Services
        if any(x in import_name for x in ['community_intelligence', 'collective', 'predictive', 'living_docs']):
            return f"ai_services/{import_name.split('.')[0]}"

        return import_name

    def _scan_endpoints(self):
        """Поиск API endpoints"""
        print("🌐 Поиск API endpoints...")

        endpoints = []

        # Поиск FastAPI endpoints
        for py_file in self.module_path.rglob('*.py'):
            if 'venv' in str(py_file):
                continue

            try:
                with open(py_file) as f:
                    content = f.read()

                # ULTRA-FIXED: Match ALL FastAPI decorator patterns
                import re

                pattern = re.compile(
                    r'@(?:app|router)\.(get|post|put|delete|patch)\s*\('  # @router.post(
                    r'[^)]*?'  # Any params before path (non-greedy)
                    r'["\']([^"\']+)["\']',  # "/path"
                    re.MULTILINE | re.DOTALL
                )

                for match in pattern.finditer(content):
                    method = match.group(1).upper()
                    path = match.group(2)

                    # Deduplicate
                    if not any(ep['method'] == method and ep['path'] == path for ep in endpoints):
                        endpoints.append({
                            'method': method,
                            'path': path,
                            'file': py_file.name
                        })

            except:
                continue

        self.result['endpoints'] = endpoints
        print(f"  ✓ Найдено endpoints: {len(endpoints)}")

        if endpoints:
            print("  📌 Примеры:")
            for ep in endpoints[:3]:
                print(f"     • {ep['method']} {ep['path']}")

    def _scan_code(self):
        """Анализ классов и функций"""
        print("💻 Анализ кода...")

        classes = []
        functions = []

        for py_file in self.module_path.rglob('*.py'):
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue

            try:
                with open(py_file) as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        classes.append({
                            'name': node.name,
                            'file': py_file.name,
                            'methods': len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                        })

                    elif isinstance(node, ast.FunctionDef):
                        # Только top-level функции
                        if node.col_offset == 0:
                            functions.append({
                                'name': node.name,
                                'file': py_file.name,
                                'params': len(node.args.args)
                            })

            except:
                continue

        self.result['classes'] = classes
        self.result['functions'] = functions

        print(f"  ✓ Классов: {len(classes)}")
        print(f"  ✓ Функций: {len(functions)}")

        # Топ классы
        if classes:
            top_classes = sorted(classes, key=lambda x: x['methods'], reverse=True)[:3]
            print("  📌 Топ классы:")
            for cls in top_classes:
                print(f"     • {cls['name']} ({cls['methods']} методов)")

    def _scan_config(self):
        """Поиск конфигурации"""
        print("⚙️  Поиск конфигурации...")

        config_files = [
            'config.yaml', 'config.yml',
            'settings.yaml', 'settings.yml',
            '.env', '.env.example',
            'pyproject.toml', 'requirements.txt'
        ]

        found_configs = {}

        for config_file in config_files:
            config_path = self.module_path / config_file
            if config_path.exists():
                found_configs[config_file] = str(config_path)
                print(f"  ✓ Найден: {config_file}")

        self.result['config'] = found_configs

        if not found_configs:
            print("  ⚠ Конфигурационные файлы не найдены")

    def _calculate_metrics(self):
        """Рассчитать метрики"""
        print("📊 Расчет метрик...")

        # LOC (Lines of Code)
        total_loc = 0
        py_files = 0

        for py_file in self.module_path.rglob('*.py'):
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue

            try:
                with open(py_file) as f:
                    lines = len(f.readlines())
                    total_loc += lines
                    py_files += 1
            except:
                continue

        self.result['metrics'] = {
            'loc': total_loc,
            'python_files': py_files,
            'classes': len(self.result['classes']),
            'functions': len(self.result['functions']),
            'endpoints': len(self.result['endpoints']),
            'dependencies': len(self.result['dependencies'])
        }

        print(f"  ✓ LOC: {total_loc}")
        print(f"  ✓ Python файлов: {py_files}")

    def generate_yaml_entry(self) -> str:
        """Сгенерировать YAML запись для SERVICE_CATALOG.yaml"""

        result = self.result
        module_name = self.module_name.replace('-', '_')

        # Определить тип
        if 'service' in self.module_name.lower():
            module_type = 'business-service'
        elif 'intelligence' in self.module_name.lower() or 'workflow' in self.module_name.lower():
            module_type = 'ai-service'
        elif 'gateway' in self.module_name.lower():
            module_type = 'gateway'
        else:
            module_type = 'service'

        # Порт (из endpoints)
        port = None
        for py_file in self.module_path.rglob('main.py'):
            try:
                with open(py_file) as f:
                    content = f.read()
                    import re
                    port_match = re.search(r'port[=\s]*(\d+)', content)
                    if port_match:
                        port = int(port_match.group(1))
                        break
            except:
                continue

        yaml_entry = f"""
  {module_name}:
    type: {module_type}
    location: {self.module_path}
    port: {port if port else 'null'}
    technology:
      - Python 3.11
      - FastAPI
    dependencies:
      infrastructure:
{chr(10).join(f"        - {dep}" for dep in result['dependencies'] if dep.startswith('database/') or dep.startswith('runtime/'))}
      external:
{chr(10).join(f"        - {dep}" for dep in result['dependencies'] if dep.startswith('external/'))}
      internal:
{chr(10).join(f"        - {dep}" for dep in result['dependencies'] if dep.startswith('shared/') or dep.startswith('ai_'))}
    endpoints:
{chr(10).join(f"      - {ep['method']} {ep['path']}" for ep in result['endpoints'][:5])}
    metrics:
      loc: {result['metrics']['loc']}
      files: {result['metrics']['python_files']}
      classes: {result['metrics']['classes']}
      functions: {result['metrics']['functions']}
    status: discovered
"""

        return yaml_entry

    def save_report(self, output_dir: str = "infrastructure/AI-office-infrastructure/devops-agent/reports-generated/modules"):
        """Сохранить отчет"""

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # JSON отчет
        json_file = output_path / f"{self.module_name}_scan.json"

        # Конвертировать sets в lists для JSON
        result_copy = self.result.copy()
        result_copy['dependencies'] = list(result_copy['dependencies'])

        with open(json_file, 'w') as f:
            json.dump(result_copy, f, indent=2)

        # Markdown отчет
        md_file = output_path / f"{self.module_name}_scan.md"
        with open(md_file, 'w') as f:
            f.write(self._generate_markdown_report())

        # YAML entry
        yaml_file = output_path / f"{self.module_name}_catalog_entry.yaml"
        with open(yaml_file, 'w') as f:
            f.write(self.generate_yaml_entry())

        print(f"\n💾 Отчеты сохранены:")
        print(f"   • {json_file}")
        print(f"   • {md_file}")
        print(f"   • {yaml_file}")

        return {
            'json': str(json_file),
            'markdown': str(md_file),
            'yaml': str(yaml_file)
        }

    def _generate_markdown_report(self) -> str:
        """Генерация Markdown отчета"""

        result = self.result

        report = f"""# Module Scan Report: {self.module_name}

**Дата сканирования:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}
**Путь:** `{self.module_path}`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | {result['metrics']['loc']} |
| **Python файлов** | {result['metrics']['python_files']} |
| **Классов** | {result['metrics']['classes']} |
| **Функций** | {result['metrics']['functions']} |
| **API Endpoints** | {result['metrics']['endpoints']} |
| **Зависимостей** | {result['metrics']['dependencies']} |

---

## 🔗 Зависимости ({len(result['dependencies'])})

"""

        # Группировка зависимостей
        deps_by_type = defaultdict(list)
        for dep in sorted(result['dependencies']):
            dep_type = dep.split('/')[0]
            deps_by_type[dep_type].append(dep)

        for dep_type, deps in sorted(deps_by_type.items()):
            report += f"\n### {dep_type}\n"
            for dep in deps:
                report += f"- `{dep}`\n"

        # API Endpoints
        if result['endpoints']:
            report += f"\n---\n\n## 🌐 API Endpoints ({len(result['endpoints'])})\n\n"
            for ep in result['endpoints'][:10]:
                report += f"- **{ep['method']}** `{ep['path']}` (файл: `{ep['file']}`)\n"

        # Классы
        if result['classes']:
            report += f"\n---\n\n## 💻 Классы ({len(result['classes'])})\n\n"
            top_classes = sorted(result['classes'], key=lambda x: x['methods'], reverse=True)[:10]
            for cls in top_classes:
                report += f"- **{cls['name']}** ({cls['methods']} методов) - `{cls['file']}`\n"

        # README
        if result['readme']:
            report += f"\n---\n\n## 📄 README\n\n"
            report += f"**Файл:** `{result['readme']['file']}`\n"
            report += f"**Размер:** {result['readme']['size']} символов ({result['readme']['lines']} строк)\n\n"
            report += "**Превью:**\n```\n"
            report += result['readme']['content']
            report += "\n```\n"

        # Конфигурация
        if result['config']:
            report += f"\n---\n\n## ⚙️ Конфигурация\n\n"
            for config_file, path in result['config'].items():
                report += f"- `{config_file}` → `{path}`\n"

        # Структура (кратко)
        report += f"\n---\n\n## 📂 Структура\n\n"
        total_files = sum(len(files) for files in result['structure'].values())
        report += f"**Всего файлов:** {total_files}\n"
        report += f"**Директорий:** {len(result['structure'])}\n"

        return report


def scan_section(section_path: str):
    """Сканировать целый раздел (все модули)"""

    section = Path(section_path)
    if not section.exists():
        print(f"❌ Раздел не найден: {section_path}")
        return

    # Найти все подпапки (модули)
    modules = [d for d in section.iterdir() if d.is_dir() and not d.name.startswith('.') and d.name not in ['venv', '__pycache__']]

    print(f"\n{'='*60}")
    print(f"🔍 СКАНИРОВАНИЕ РАЗДЕЛА: {section.name}")
    print(f"{'='*60}")
    print(f"\nНайдено модулей: {len(modules)}\n")

    results = []

    for i, module_path in enumerate(modules, 1):
        print(f"\n[{i}/{len(modules)}] {module_path.name}")
        print("-" * 60)

        try:
            scanner = ModuleScanner(str(module_path))
            result = scanner.scan()
            files = scanner.save_report()
            results.append({
                'module': module_path.name,
                'result': result,
                'files': files
            })
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            continue

    # Сводный отчет
    print(f"\n\n{'='*60}")
    print(f"✅ СКАНИРОВАНИЕ ЗАВЕРШЕНО")
    print(f"{'='*60}\n")
    print(f"Всего модулей: {len(modules)}")
    print(f"Успешно: {len(results)}")
    print(f"\nОтчеты сохранены в: infrastructure/AI-office-infrastructure/devops-agent/reports-generated/modules/")


if __name__ == "__main__":
    import sys

    if '--interactive' in sys.argv or '-i' in sys.argv:
        print("🎯 Интерактивный режим сканирования\n")
        print("Выберите раздел:")
        print("1. intelligent-core (AI сервисы)")
        print("2. platform-services (бизнес-логика)")
        print("3. infrastructure (инфраструктура)")
        print("4. Указать путь вручную")

        choice = input("\nВыбор (1-4): ").strip()

        section_map = {
            '1': 'intelligent-core',
            '2': 'platform-services',
            '3': 'infrastructure'
        }

        if choice in section_map:
            scan_section(section_map[choice])
        elif choice == '4':
            path = input("Введите путь: ").strip()
            if Path(path).is_dir():
                scanner = ModuleScanner(path)
                scanner.scan()
                scanner.save_report()
            else:
                scan_section(path)

    elif '--section' in sys.argv:
        idx = sys.argv.index('--section')
        section_path = sys.argv[idx + 1]
        scan_section(section_path)

    elif len(sys.argv) > 1:
        # Прямое указание модуля
        module_path = sys.argv[1]
        scanner = ModuleScanner(module_path)
        scanner.scan()
        scanner.save_report()

    else:
        print(__doc__)
