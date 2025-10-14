#!/usr/bin/env python3
"""
AI Documentation Generator - Интеллектуальная генерация документации

Комбинирует:
- module_scanner.py отчёты (структура, метрики)
- AI-генерация описаний (из living-docs)
- Классификация и извлечение концепций (из document_processor)

Результат: Качественная документация с AI-сгенерированными описаниями и примерами

Использование:
    # С AI-генерацией (требует Anthropic API key)
    export ANTHROPIC_API_KEY="your-key"
    python3 tools/generators/ai_documentation_generator.py --module ai-foundation --ai

    # Без AI (использует шаблоны)
    python3 tools/generators/ai_documentation_generator.py --module ai-foundation

    # Полная генерация для всех модулей с AI
    python3 tools/generators/ai_documentation_generator.py --full --ai
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict


class AIDocumentationGenerator:
    """
    Интеллектуальный генератор документации

    Использует AI для создания качественных описаний, примеров и объяснений
    """

    # Ключевые слова для классификации (из document_processor)
    MODULE_CLASSIFICATION_KEYWORDS = {
        'ai_module': [
            'intelligence', 'ai', 'ml', 'predictive', 'learning',
            'anthropic', 'claude', 'llm', 'embedding', 'rag'
        ],
        'orchestration': [
            'orchestrat', 'workflow', 'temporal', 'coordination',
            'delegation', 'routing', 'decision'
        ],
        'api_service': [
            'fastapi', 'router', 'endpoint', 'api', 'routes',
            'middleware', 'rest', 'http'
        ],
        'data_service': [
            'database', 'postgresql', 'supabase', 'sqlalchemy',
            'repository', 'model', 'schema'
        ],
        'integration': [
            'integration', 'adapter', 'client', 'connector',
            'bridge', 'external'
        ],
        'foundation': [
            'foundation', 'core', 'base', 'shared', 'common',
            'utils', 'helpers'
        ]
    }

    def __init__(self, use_ai: bool = False):
        self.project_root = Path(__file__).parent.parent.parent
        self.reports_dir = self.project_root / "tools" / "reports" / "modules"
        self.use_ai = use_ai

        if not self.reports_dir.exists():
            print(f"❌ Директория с отчётами не найдена: {self.reports_dir}")
            print("💡 Запустите: python3 tools/analyzers/module_scanner.py --section intelligent-core")
            sys.exit(1)

        # Инициализация AI (если включено)
        if self.use_ai:
            self._init_ai_client()

    def _init_ai_client(self):
        """Инициализация Anthropic AI клиента"""
        try:
            import anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')

            if not api_key:
                print("⚠️  ANTHROPIC_API_KEY не найден. AI-генерация отключена.")
                print("💡 Установите: export ANTHROPIC_API_KEY='your-key'")
                self.use_ai = False
                return

            self.ai_client = anthropic.Anthropic(api_key=api_key)
            print("✅ AI клиент инициализирован (Claude)")

        except ImportError:
            print("⚠️  anthropic не установлен. Установите: pip install anthropic")
            self.use_ai = False

    def classify_module(self, scan_data: Dict) -> Dict[str, any]:
        """
        Классифицировать модуль по ключевым словам

        Returns:
            {
                'primary_type': str,
                'secondary_types': List[str],
                'key_concepts': List[str],
                'confidence': float
            }
        """

        name = scan_data['module_name'].lower()
        dependencies = ' '.join(scan_data.get('dependencies', [])).lower()

        # Собрать весь текст для анализа
        classes = ' '.join([c['name'] for c in scan_data.get('classes', [])]).lower()
        text_to_analyze = f"{name} {dependencies} {classes}"

        # Подсчитать совпадения
        scores = {}
        for module_type, keywords in self.MODULE_CLASSIFICATION_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_to_analyze)
            if score > 0:
                scores[module_type] = score

        # Определить основной и второстепенные типы
        if not scores:
            return {
                'primary_type': 'utility',
                'secondary_types': [],
                'key_concepts': [],
                'confidence': 0.5
            }

        sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary_type = sorted_types[0][0]
        secondary_types = [t for t, s in sorted_types[1:3]]

        # Извлечь ключевые концепции
        key_concepts = self._extract_key_concepts(scan_data)

        return {
            'primary_type': primary_type,
            'secondary_types': secondary_types,
            'key_concepts': key_concepts,
            'confidence': min(sorted_types[0][1] / 10.0, 1.0)
        }

    def _extract_key_concepts(self, scan_data: Dict) -> List[str]:
        """Извлечь ключевые концепции из модуля"""

        concepts = set()

        # Из имени модуля
        name_parts = scan_data['module_name'].replace('-', '_').split('_')
        concepts.update(p for p in name_parts if len(p) > 3)

        # Из названий классов (топ-5)
        top_classes = sorted(
            scan_data.get('classes', []),
            key=lambda x: x.get('methods', 0),
            reverse=True
        )[:5]

        for cls in top_classes:
            # CamelCase -> отдельные слова
            name = cls['name']
            # Простое разделение по заглавным буквам
            words = []
            current = ""
            for char in name:
                if char.isupper() and current:
                    words.append(current)
                    current = char
                else:
                    current += char
            if current:
                words.append(current)

            concepts.update(w.lower() for w in words if len(w) > 3)

        return sorted(list(concepts))[:10]

    async def generate_ai_description(
        self,
        module_name: str,
        classification: Dict,
        scan_data: Dict
    ) -> str:
        """Генерировать описание модуля с помощью AI"""

        if not self.use_ai:
            return self._generate_template_description(module_name, classification)

        # Подготовить контекст для AI
        context = {
            'module_name': module_name,
            'type': classification['primary_type'],
            'concepts': classification['key_concepts'],
            'metrics': scan_data.get('metrics', {}),
            'has_api': scan_data.get('metrics', {}).get('endpoints', 0) > 0,
            'top_classes': [c['name'] for c in sorted(
                scan_data.get('classes', []),
                key=lambda x: x.get('methods', 0),
                reverse=True
            )[:3]]
        }

        prompt = f"""Ты технический писатель для BCM (Business Continuity Management) платформы.

Модуль: {context['module_name']}
Тип: {context['type']}
Ключевые концепции: {', '.join(context['concepts'])}
Основные классы: {', '.join(context['top_classes']) if context['top_classes'] else 'нет'}
API endpoints: {context['metrics'].get('endpoints', 0)}

Напиши краткое (2-3 предложения) техническое описание этого модуля:
- Что он делает
- Для чего используется
- Ключевые возможности

Стиль: профессиональный, технический, конкретный.
Формат: только текст, без маркдауна."""

        try:
            response = self.ai_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text.strip()

        except Exception as e:
            print(f"⚠️  AI генерация не удалась: {e}")
            return self._generate_template_description(module_name, classification)

    def _generate_template_description(
        self,
        module_name: str,
        classification: Dict
    ) -> str:
        """Генерировать описание по шаблону (fallback без AI)"""

        templates = {
            'ai_module': f"AI-powered модуль для {module_name}. Использует машинное обучение и LLM для интеллектуальной обработки.",
            'orchestration': f"Оркестрация и координация компонентов платформы. Управляет workflow и делегированием задач.",
            'api_service': f"REST API сервис для {module_name}. Предоставляет HTTP endpoints для интеграции.",
            'data_service': f"Сервис управления данными. Работает с PostgreSQL/Supabase для хранения и извлечения информации.",
            'integration': f"Интеграционный модуль для подключения внешних систем и сервисов.",
            'foundation': f"Базовый модуль платформы. Предоставляет общую функциональность для других компонентов.",
            'utility': f"Вспомогательный модуль {module_name}."
        }

        return templates.get(
            classification['primary_type'],
            f"Модуль {module_name} платформы BCM."
        )

    async def generate_ai_usage_examples(
        self,
        module_name: str,
        classification: Dict,
        scan_data: Dict
    ) -> str:
        """Генерировать примеры использования с AI"""

        if not self.use_ai:
            return self._generate_template_examples(module_name, classification, scan_data)

        endpoints = scan_data.get('endpoints', [])
        top_classes = sorted(
            scan_data.get('classes', []),
            key=lambda x: x.get('methods', 0),
            reverse=True
        )[:2]

        context = {
            'has_api': len(endpoints) > 0,
            'sample_endpoint': endpoints[0] if endpoints else None,
            'main_classes': [c['name'] for c in top_classes]
        }

        if context['has_api']:
            prompt = f"""Создай пример кода для использования API модуля {module_name}.

Доступные endpoints: {endpoints[0]['method']} {endpoints[0]['path']}

Формат:
- Python код с использованием httpx
- Комментарии на русском
- Обработка ошибок
- 10-15 строк максимум

Только код, без дополнительного текста."""
        else:
            prompt = f"""Создай пример импорта и использования модуля {module_name}.

Основные классы: {', '.join(context['main_classes'])}

Формат:
- Python код
- Import и базовое использование
- Комментарии на русском
- 10-15 строк максимум

Только код, без дополнительного текста."""

        try:
            response = self.ai_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )

            code = response.content[0].text.strip()

            # Убрать markdown если есть
            if code.startswith('```'):
                lines = code.split('\n')
                code = '\n'.join(lines[1:-1]) if len(lines) > 2 else code

            return code

        except Exception as e:
            print(f"⚠️  AI генерация примеров не удалась: {e}")
            return self._generate_template_examples(module_name, classification, scan_data)

    def _generate_template_examples(
        self,
        module_name: str,
        classification: Dict,
        scan_data: Dict
    ) -> str:
        """Шаблонные примеры использования"""

        endpoints = scan_data.get('endpoints', [])

        if endpoints:
            ep = endpoints[0]
            return f"""import httpx

# Запрос к {module_name}
async with httpx.AsyncClient() as client:
    response = await client.{ep['method'].lower()}(
        "http://localhost:8000{ep['path']}",
        headers={{"Authorization": "Bearer <token>"}}
    )
    data = response.json()
    print(data)"""
        else:
            return f"""from {module_name.replace('-', '_')} import ...

# Использование модуля
# TODO: Добавить конкретный пример"""

    def generate_readme(
        self,
        scan_data: Dict,
        module_path: Path,
        ai_generated: Optional[Dict] = None
    ) -> str:
        """Генерировать README.md с AI-контентом"""

        name = scan_data['module_name']
        metrics = scan_data.get('metrics', {})
        classification = self.classify_module(scan_data)

        # Использовать AI-генерированный контент если есть
        description = ai_generated.get('description') if ai_generated else \
                     self._generate_template_description(name, classification)

        usage_example = ai_generated.get('usage_example') if ai_generated else \
                       self._generate_template_examples(name, classification, scan_data)

        # Иконка по типу модуля
        type_icons = {
            'ai_module': '🤖',
            'orchestration': '🎯',
            'api_service': '🌐',
            'data_service': '💾',
            'integration': '🔗',
            'foundation': '🏗️',
            'utility': '🔧'
        }

        icon = type_icons.get(classification['primary_type'], '📦')

        readme = f"""# {icon} {name}

> {description}

## 📊 Обзор

| Метрика | Значение |
|---------|----------|
| **Строк кода** | {metrics.get('loc', 0):,} |
| **Python файлов** | {metrics.get('python_files', 0)} |
| **Классов** | {metrics.get('classes', 0)} |
| **Функций** | {metrics.get('functions', 0)} |
| **API Endpoints** | {metrics.get('endpoints', 0)} |

**Тип:** {classification['primary_type'].replace('_', ' ').title()}
**Ключевые концепции:** {', '.join(classification['key_concepts'][:5])}
**Последнее обновление:** {datetime.now().strftime('%Y-%m-%d')}

---

"""

        # API секция
        endpoints = scan_data.get('endpoints', [])
        if endpoints:
            readme += "## 🌐 API\n\n"
            by_method = defaultdict(list)
            for ep in endpoints:
                by_method[ep['method']].append(ep)

            for method in ['GET', 'POST', 'PUT', 'DELETE']:
                if method in by_method:
                    eps = by_method[method]
                    readme += f"### {method} ({len(eps)})\n"
                    for ep in sorted(eps, key=lambda x: x['path'])[:5]:
                        readme += f"- `{ep['path']}`\n"
                    readme += "\n"

            readme += "[→ Полная API документация](./API.md)\n\n---\n\n"

        # Архитектура
        classes = scan_data.get('classes', [])
        if classes:
            top_classes = sorted(classes, key=lambda x: x.get('methods', 0), reverse=True)[:5]
            readme += "## 🏗️ Архитектура\n\n"
            readme += "### Ключевые компоненты\n\n"
            for cls in top_classes:
                readme += f"- **{cls['name']}** ({cls.get('methods', 0)} методов) - `{cls['file']}`\n"
            readme += "\n---\n\n"

        # Использование
        readme += "## 💻 Использование\n\n"
        readme += "```python\n"
        readme += usage_example
        readme += "\n```\n\n---\n\n"

        # Зависимости (топ-10)
        deps = scan_data.get('dependencies', [])
        if deps:
            readme += "## 🔗 Зависимости\n\n"
            internal = [d for d in deps if any(x in d for x in ['ai_foundation', 'shared'])][:10]
            if internal:
                readme += "### Внутренние\n"
                for dep in internal:
                    readme += f"- `{dep}`\n"
                readme += "\n"
            readme += "---\n\n"

        # Footer
        readme += f"""## 📚 Дополнительно

- [Архитектура платформы](../../docs/ARCHITECTURE.md)
- [API Reference](./API.md) {'✅' if endpoints else '⚠️'}
- [Тесты](./tests/) {'✅' if (module_path / 'tests').exists() else '⚠️'}

---

<sub>Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M')} | {'🤖 AI-powered' if ai_generated else '📝 Template-based'}</sub>
"""

        return readme

    async def process_module(self, module_name: str):
        """Обработать один модуль"""

        json_file = self.reports_dir / f"{module_name}_scan.json"

        if not json_file.exists():
            print(f"❌ Отчёт не найден: {module_name}")
            return

        with open(json_file) as f:
            scan_data = json.load(f)

        module_path = self.project_root / scan_data['path']

        print(f"\n{'='*60}")
        print(f"📝 {module_name}")
        print(f"{'='*60}\n")

        # Классификация
        classification = self.classify_module(scan_data)
        print(f"🏷️  Тип: {classification['primary_type']}")
        print(f"💡 Концепции: {', '.join(classification['key_concepts'][:3])}")

        # AI генерация (если включено)
        ai_content = None
        if self.use_ai:
            print(f"🤖 AI-генерация...")
            description = await self.generate_ai_description(
                module_name, classification, scan_data
            )
            usage_example = await self.generate_ai_usage_examples(
                module_name, classification, scan_data
            )
            ai_content = {
                'description': description,
                'usage_example': usage_example
            }
            print(f"✅ AI контент готов")

        # Генерация README
        readme_content = self.generate_readme(scan_data, module_path, ai_content)
        readme_path = module_path / "README.md"

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print(f"✅ README -> {readme_path.relative_to(self.project_root)}")
        print()


async def main():
    import argparse

    parser = argparse.ArgumentParser(description='AI Documentation Generator')
    parser.add_argument('--module', help='Модуль для генерации')
    parser.add_argument('--all', action='store_true', help='Все модули')
    parser.add_argument('--ai', action='store_true', help='Использовать AI')
    parser.add_argument('--full', action='store_true', help='Все модули + AI')

    args = parser.parse_args()

    use_ai = args.ai or args.full
    generator = AIDocumentationGenerator(use_ai=use_ai)

    if args.module:
        await generator.process_module(args.module)
    elif args.all or args.full:
        json_files = list(generator.reports_dir.glob("*_scan.json"))

        for json_file in sorted(json_files):
            module_name = json_file.stem.replace('_scan', '')
            if not module_name.startswith('_'):
                await generator.process_module(module_name)
    else:
        parser.print_help()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
