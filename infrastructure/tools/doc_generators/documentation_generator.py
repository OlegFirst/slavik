#!/usr/bin/env python3
"""
Documentation Generator - Автоматическая генерация документации из сканов модулей

Читает результаты module_scanner.py и генерирует:
- README.md для каждого модуля
- API.md (если есть endpoints)
- ARCHITECTURE.md на уровне слоёв (intelligent-core, platform-services)

Использование:
    # Генерировать документацию для одного модуля
    python3 tools/generators/documentation_generator.py --module intelligent-core/ai-foundation

    # Генерировать для всех модулей
    python3 tools/generators/documentation_generator.py --all

    # Генерировать архитектурные документы по слоям
    python3 tools/generators/documentation_generator.py --architecture

    # Полная генерация (модули + архитектура)
    python3 tools/generators/documentation_generator.py --full
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from collections import defaultdict


class DocumentationGenerator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.reports_dir = self.project_root / "tools" / "reports" / "modules"

        # Проверка существования отчётов
        if not self.reports_dir.exists():
            print(f" Директория с отчётами не найдена: {self.reports_dir}")
            print(" Запустите сначала: python3 tools/analyzers/module_scanner.py --section intelligent-core")
            sys.exit(1)

    def generate_module_readme(self, scan_data: Dict, module_path: Path) -> str:
        """Генерировать README.md для модуля"""

        name = scan_data['module_name']
        metrics = scan_data.get('metrics', {})
        deps = scan_data.get('dependencies', [])
        endpoints = scan_data.get('endpoints', [])
        classes = scan_data.get('classes', [])
        functions = scan_data.get('functions', [])

        # Определить тип модуля
        module_type = self._detect_module_type(scan_data)

        readme = f"""# {name}

> {self._generate_module_description(name, module_type)}

##  Обзор

| Метрика | Значение |
|---------|----------|
| **Строк кода** | {metrics.get('loc', 0):,} |
| **Python файлов** | {metrics.get('python_files', 0)} |
| **Классов** | {metrics.get('classes', 0)} |
| **Функций** | {metrics.get('functions', 0)} |
| **API Endpoints** | {metrics.get('endpoints', 0)} |
| **Зависимостей** | {metrics.get('dependencies', 0)} |

**Тип модуля:** {module_type}
**Последнее обновление:** {datetime.now().strftime('%Y-%m-%d')}

---

"""

        # Секция API (если есть endpoints)
        if endpoints:
            readme += self._generate_api_section(endpoints)

        # Секция Architecture (основные компоненты)
        if classes or functions:
            readme += self._generate_architecture_section(classes, functions)

        # Секция Dependencies
        if deps:
            readme += self._generate_dependencies_section(deps)

        # Секция Usage (примеры использования)
        readme += self._generate_usage_section(name, module_type, endpoints)

        # Секция Configuration
        config_files = scan_data.get('config', {})
        if config_files:
            readme += self._generate_config_section(config_files)

        # Footer
        readme += f"""
---

##  Дополнительные материалы

- [Архитектура платформы](../../doc-project/FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md)
- [API Reference](./API.md) {'' if endpoints else '️ Нет API'}
- [Тесты](./tests/) {'' if (module_path / 'tests').exists() else '️ Тесты отсутствуют'}

**Сгенерировано автоматически:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Инструмент:** `tools/generators/documentation_generator.py`
"""

        return readme

    def generate_module_api_doc(self, scan_data: Dict) -> str:
        """Генерировать API.md для модуля с endpoints"""

        name = scan_data['module_name']
        endpoints = scan_data.get('endpoints', [])

        if not endpoints:
            return None

        # Группировать endpoints по ресурсам
        grouped = defaultdict(list)
        for ep in endpoints:
            resource = self._extract_resource(ep['path'])
            grouped[resource].append(ep)

        api_doc = f"""# {name} - API Documentation

> Автоматически сгенерированная документация API endpoints

**Всего endpoints:** {len(endpoints)}
**Ресурсов:** {len(grouped)}
**Последнее обновление:** {datetime.now().strftime('%Y-%m-%d')}

---

##  Содержание

"""
        # Оглавление
        for resource in sorted(grouped.keys()):
            api_doc += f"- [{resource}](#{resource.lower().replace('/', '-')})\n"

        api_doc += "\n---\n\n"

        # Детальное описание каждого ресурса
        for resource in sorted(grouped.keys()):
            eps = grouped[resource]
            api_doc += f"## {resource}\n\n"

            for ep in sorted(eps, key=lambda x: (x['path'], x['method'])):
                api_doc += f"### `{ep['method']}` {ep['path']}\n\n"
                api_doc += f"**Файл:** `{ep['file']}`\n\n"

                # Placeholder для описания
                api_doc += "**Описание:**  \n"
                api_doc += self._generate_endpoint_description(ep)
                api_doc += "\n\n"

                # Примеры запросов
                api_doc += "**Пример запроса:**\n\n"
                api_doc += self._generate_request_example(ep)
                api_doc += "\n\n"

                api_doc += "---\n\n"

        # Footer
        api_doc += f"""
##  Интеграция

### Authentication
```python
headers = {{
    "Authorization": "Bearer <token>",
    "Content-Type": "application/json"
}}
```

### Base URL
```
http://localhost:8000  # Development
https://api.example.com  # Production
```

---

**Сгенерировано:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Инструмент:** `tools/generators/documentation_generator.py`
"""

        return api_doc

    def generate_layer_architecture(self, layer_name: str, modules_data: List[Dict]) -> str:
        """Генерировать ARCHITECTURE.md для слоя (intelligent-core, platform-services)"""

        total_modules = len(modules_data)
        total_endpoints = sum(m.get('metrics', {}).get('endpoints', 0) for m in modules_data)
        total_classes = sum(m.get('metrics', {}).get('classes', 0) for m in modules_data)
        total_loc = sum(m.get('metrics', {}).get('loc', 0) for m in modules_data)

        arch_doc = f"""# {layer_name} - Architecture Overview

> Архитектура и структура слоя {layer_name}

##  Статистика слоя

| Метрика | Значение |
|---------|----------|
| **Модулей** | {total_modules} |
| **Всего endpoints** | {total_endpoints} |
| **Всего классов** | {total_classes} |
| **Всего LOC** | {total_loc:,} |

**Последнее обновление:** {datetime.now().strftime('%Y-%m-%d')}

---

## ️ Модули

"""

        # Таблица модулей
        arch_doc += "| Модуль | Тип | LOC | Endpoints | Классов |\n"
        arch_doc += "|--------|-----|-----|-----------|--------|\n"

        for module in sorted(modules_data, key=lambda x: x['module_name']):
            name = module['module_name']
            metrics = module.get('metrics', {})
            module_type = self._detect_module_type(module)

            arch_doc += f"| [{name}](./{name}/README.md) | {module_type} | "
            arch_doc += f"{metrics.get('loc', 0):,} | "
            arch_doc += f"{metrics.get('endpoints', 0)} | "
            arch_doc += f"{metrics.get('classes', 0)} |\n"

        arch_doc += "\n---\n\n"

        # Граф зависимостей между модулями
        arch_doc += "##  Граф зависимостей\n\n"
        arch_doc += "```mermaid\ngraph TD\n"

        for module in modules_data:
            name = module['module_name']
            deps = module.get('dependencies', [])

            # Только внутренние зависимости
            internal_deps = [d for d in deps if any(m['module_name'] in d for m in modules_data)]

            for dep in internal_deps[:5]:  # Топ-5
                dep_name = dep.split('/')[-1]
                arch_doc += f"    {name} --> {dep_name}\n"

        arch_doc += "```\n\n---\n\n"

        # Детальное описание каждого модуля
        arch_doc += "##  Детальное описание модулей\n\n"

        for module in sorted(modules_data, key=lambda x: x['module_name']):
            name = module['module_name']
            metrics = module.get('metrics', {})

            arch_doc += f"### {name}\n\n"
            arch_doc += self._generate_module_description(name, self._detect_module_type(module))
            arch_doc += "\n\n"

            # Ключевые компоненты
            classes = module.get('classes', [])
            if classes:
                top_classes = sorted(classes, key=lambda x: x.get('methods', 0), reverse=True)[:3]
                arch_doc += "**Ключевые классы:**\n"
                for cls in top_classes:
                    arch_doc += f"- `{cls['name']}` ({cls.get('methods', 0)} методов)\n"
                arch_doc += "\n"

            arch_doc += f"[→ Полная документация](./{name}/README.md)\n\n"
            arch_doc += "---\n\n"

        # Footer
        arch_doc += f"""
##  Roadmap

- [ ] Полное покрытие тестами (>80%)
- [ ] API документация (OpenAPI/Swagger)
- [ ] Performance мониторинг
- [ ] CI/CD интеграция

---

**Сгенерировано:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Инструмент:** `tools/generators/documentation_generator.py`
"""

        return arch_doc

    # === Helper Methods ===

    def _detect_module_type(self, scan_data: Dict) -> str:
        """Определить тип модуля"""
        endpoints = scan_data.get('endpoints', [])
        classes = scan_data.get('classes', [])
        name = scan_data['module_name'].lower()

        if endpoints:
            return " API Service"
        elif 'orchestrat' in name:
            return " Orchestrator"
        elif any(x in name for x in ['ai', 'intelligence', 'collective', 'predictive']):
            return " AI Module"
        elif 'foundation' in name:
            return "️ Foundation Layer"
        elif classes and len(classes) > 10:
            return " Library"
        else:
            return " Utility Module"

    def _generate_module_description(self, name: str, module_type: str) -> str:
        """Генерировать описание модуля"""

        descriptions = {
            'ai-foundation': 'Базовый слой AI платформы: LLM роутинг, RAG pipeline, эмбеддинги',
            'workflow_intelligence': 'Интеллектуальное управление workflow и бизнес-процессами',
            'orchestration': 'Оркестрация AI агентов и микросервисов',
            'expertise-center': 'Доменные эксперты и тактические ассистенты',
            'collective': 'Коллективный интеллект и агенты',
            'community_intelligence': 'Сообщество и обмен знаниями',
            'predictive': 'Предиктивная аналитика и ML модели',
            'workflow-engine': 'BPMN workflow engine на базе Temporal',
        }

        return descriptions.get(name, f'{module_type} модуль платформы')

    def _generate_api_section(self, endpoints: List[Dict]) -> str:
        """Секция API endpoints"""

        section = "##  API Endpoints\n\n"

        # Группировать по методам
        by_method = defaultdict(list)
        for ep in endpoints:
            by_method[ep['method']].append(ep)

        for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
            if method in by_method:
                eps = by_method[method]
                section += f"### {method} ({len(eps)})\n\n"
                for ep in sorted(eps, key=lambda x: x['path'])[:5]:  # Топ-5
                    section += f"- `{ep['path']}`\n"
                section += "\n"

        section += f"[→ Полная документация API](./API.md)\n\n---\n\n"

        return section

    def _generate_architecture_section(self, classes: List[Dict], functions: List[Dict]) -> str:
        """Секция Architecture"""

        section = "## ️ Архитектура\n\n"

        if classes:
            top_classes = sorted(classes, key=lambda x: x.get('methods', 0), reverse=True)[:5]
            section += "### Ключевые классы\n\n"
            for cls in top_classes:
                section += f"- **{cls['name']}** ({cls.get('methods', 0)} методов) - `{cls['file']}`\n"
            section += "\n"

        if functions:
            section += f"### Функции\n\nВсего публичных функций: {len(functions)}\n\n"

        section += "---\n\n"

        return section

    def _generate_dependencies_section(self, deps: List[str]) -> str:
        """Секция Dependencies"""

        section = "##  Зависимости\n\n"

        # Группировать по типу
        internal = [d for d in deps if any(x in d for x in ['ai_foundation', 'ai_services', 'shared'])]
        external = [d for d in deps if 'external/' in d]
        infrastructure = [d for d in deps if any(x in d for x in ['database', 'runtime', 'eventbus'])]

        if internal:
            section += "### Внутренние\n"
            for dep in sorted(internal)[:10]:
                section += f"- `{dep}`\n"
            section += "\n"

        if infrastructure:
            section += "### Инфраструктура\n"
            for dep in sorted(infrastructure):
                section += f"- `{dep}`\n"
            section += "\n"

        if external:
            section += "### Внешние сервисы\n"
            for dep in sorted(external):
                section += f"- `{dep}`\n"
            section += "\n"

        section += "---\n\n"

        return section

    def _generate_usage_section(self, name: str, module_type: str, endpoints: List) -> str:
        """Секция Usage"""

        section = "##  Использование\n\n"

        if endpoints:
            # API Service
            section += "### Запуск сервиса\n\n"
            section += "```bash\n"
            section += f"cd {name}\n"
            section += "python3 main.py\n"
            section += "```\n\n"

            section += "### Пример запроса\n\n"
            section += "```python\n"
            section += "import httpx\n\n"
            section += 'response = httpx.get("http://localhost:8000' + endpoints[0]['path'] + '")\n'
            section += "print(response.json())\n"
            section += "```\n\n"
        else:
            # Library/Module
            section += "### Импорт\n\n"
            section += "```python\n"
            section += f"from {name.replace('-', '_')} import ...\n"
            section += "```\n\n"

        section += "---\n\n"

        return section

    def _generate_config_section(self, config_files: Dict) -> str:
        """Секция Configuration"""

        section = "## ️ Конфигурация\n\n"

        section += "**Конфигурационные файлы:**\n\n"
        for file_name in config_files.keys():
            section += f"- `{file_name}`\n"

        section += "\n---\n\n"

        return section

    def _extract_resource(self, path: str) -> str:
        """Извлечь ресурс из пути"""
        parts = path.strip('/').split('/')
        return parts[0] if parts else 'root'

    def _generate_endpoint_description(self, endpoint: Dict) -> str:
        """Генерировать описание endpoint"""

        method = endpoint['method']
        path = endpoint['path']

        # Простая эвристика
        if method == 'GET' and '{' in path:
            return f"Получить детали по ID"
        elif method == 'GET':
            return f"Получить список"
        elif method == 'POST':
            return f"Создать новый ресурс"
        elif method == 'PUT':
            return f"Обновить ресурс"
        elif method == 'DELETE':
            return f"Удалить ресурс"
        else:
            return f"Операция {method}"

    def _generate_request_example(self, endpoint: Dict) -> str:
        """Генерировать пример запроса"""

        method = endpoint['method']
        path = endpoint['path']

        example = "```bash\n"
        example += f"curl -X {method} \\\n"
        example += f'  "http://localhost:8000{path}" \\\n'
        example += f'  -H "Authorization: Bearer <token>"\n'

        if method in ['POST', 'PUT', 'PATCH']:
            example += '  -H "Content-Type: application/json" \\\n'
            example += '  -d \'{"key": "value"}\'\n'

        example += "```"

        return example

    # === Main Execution Methods ===

    def generate_for_module(self, module_name: str):
        """Генерировать документацию для одного модуля"""

        # Найти JSON отчёт
        json_file = self.reports_dir / f"{module_name}_scan.json"

        if not json_file.exists():
            print(f" Отчёт не найден: {json_file}")
            print(f" Запустите: python3 tools/analyzers/module_scanner.py {module_name}")
            return

        # Загрузить данные
        with open(json_file) as f:
            scan_data = json.load(f)

        # Путь к модулю
        module_path = self.project_root / scan_data['path']

        print(f"\n{'='*60}")
        print(f" Генерация документации: {module_name}")
        print(f"{'='*60}\n")

        # Генерировать README.md
        readme_content = self.generate_module_readme(scan_data, module_path)
        readme_path = module_path / "README.md"

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print(f" README.md -> {readme_path}")

        # Генерировать API.md (если есть endpoints)
        api_content = self.generate_module_api_doc(scan_data)
        if api_content:
            api_path = module_path / "API.md"
            with open(api_path, 'w', encoding='utf-8') as f:
                f.write(api_content)
            print(f" API.md    -> {api_path}")

        print(f"\n Документация для '{module_name}' сгенерирована!\n")

    def generate_for_all_modules(self):
        """Генерировать документацию для всех отсканированных модулей"""

        # Найти все JSON отчёты
        json_files = list(self.reports_dir.glob("*_scan.json"))

        if not json_files:
            print(" Не найдено отчётов сканирования")
            print(" Запустите: python3 tools/analyzers/module_scanner.py --section intelligent-core")
            return

        print(f"\n Найдено модулей для документирования: {len(json_files)}\n")

        for json_file in sorted(json_files):
            module_name = json_file.stem.replace('_scan', '')

            # Пропустить _archive
            if module_name.startswith('_'):
                continue

            self.generate_for_module(module_name)

        print(f"\n Документация для {len(json_files)} модулей сгенерирована!\n")

    def generate_architecture_docs(self):
        """Генерировать архитектурные документы по слоям"""

        print(f"\n{'='*60}")
        print(f"️  Генерация архитектурной документации")
        print(f"{'='*60}\n")

        # Загрузить все отчёты
        json_files = list(self.reports_dir.glob("*_scan.json"))

        # Группировать по слоям
        layers = defaultdict(list)

        for json_file in json_files:
            module_name = json_file.stem.replace('_scan', '')

            if module_name.startswith('_'):
                continue

            with open(json_file) as f:
                scan_data = json.load(f)

            # Определить слой по пути
            path = scan_data.get('path', '')
            if 'intelligent-core' in path:
                layers['intelligent-core'].append(scan_data)
            elif 'platform-services' in path:
                layers['platform-services'].append(scan_data)

        # Генерировать документ для каждого слоя
        for layer_name, modules_data in layers.items():
            if not modules_data:
                continue

            arch_content = self.generate_layer_architecture(layer_name, modules_data)
            arch_path = self.project_root / layer_name / "ARCHITECTURE.md"

            with open(arch_path, 'w', encoding='utf-8') as f:
                f.write(arch_content)

            print(f" {layer_name}/ARCHITECTURE.md ({len(modules_data)} модулей)")

        print(f"\n Архитектурная документация сгенерирована!\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Documentation Generator')
    parser.add_argument('--module', help='Генерировать для одного модуля')
    parser.add_argument('--all', action='store_true', help='Генерировать для всех модулей')
    parser.add_argument('--architecture', action='store_true', help='Генерировать архитектурные документы')
    parser.add_argument('--full', action='store_true', help='Полная генерация (модули + архитектура)')

    args = parser.parse_args()

    generator = DocumentationGenerator()

    if args.module:
        generator.generate_for_module(args.module)
    elif args.all:
        generator.generate_for_all_modules()
    elif args.architecture:
        generator.generate_architecture_docs()
    elif args.full:
        generator.generate_for_all_modules()
        generator.generate_architecture_docs()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
