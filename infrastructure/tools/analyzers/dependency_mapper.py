#!/usr/bin/env python3
"""
Dependency Mapper - Карта зависимостей между модулями
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
import yaml


class DependencyMapper:
    def __init__(self, config_path: str = "tools/config/analysis_config.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.imports_detail: Dict[str, List[Dict]] = defaultdict(list)

    def analyze_dependencies(self) -> Dict:
        """Анализировать зависимости между модулями"""
        print("🔗 Analyzing module dependencies...")

        for scan_path in self.config['scan_paths']:
            path = Path(scan_path)
            if not path.exists():
                continue

            print(f"📂 Scanning: {scan_path}")
            self._scan_directory(path)

        return {
            'dependencies': {k: list(v) for k, v in self.dependencies.items()},
            'imports_detail': self.imports_detail,
            'statistics': self._calculate_stats()
        }

    def _scan_directory(self, directory: Path):
        """Рекурсивно сканировать директорию"""
        for py_file in directory.rglob("*.py"):
            if any(exclude in str(py_file) for exclude in self.config['exclude']):
                continue

            try:
                self._analyze_file(py_file)
            except Exception as e:
                print(f"⚠️  Error: {py_file}: {e}")

    def _analyze_file(self, file_path: Path):
        """Анализировать импорты в файле"""
        with open(file_path) as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        module_name = self._get_module_name(file_path)

        for node in ast.walk(tree):
            # Standard static imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._add_dependency(module_name, alias.name, file_path, node.lineno)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self._add_dependency(module_name, node.module, file_path, node.lineno,
                                       names=[alias.name for alias in node.names])

            # FIXED: Dynamic imports - importlib.import_module('module_name')
            elif isinstance(node, ast.Call):
                # Case 1: importlib.import_module('module_name' or variable)
                if (hasattr(node.func, 'attr') and node.func.attr == 'import_module' and
                    hasattr(node.func.value, 'id') and node.func.value.id == 'importlib'):
                    if node.args:
                        # Extract module name from constant or variable
                        imported_module = self._extract_import_module_name(node.args[0])
                        if imported_module:
                            self._add_dependency(module_name, imported_module, file_path, node.lineno)

                # Case 2: __import__('module_name')
                elif hasattr(node.func, 'id') and node.func.id == '__import__':
                    if node.args:
                        imported_module = self._extract_import_module_name(node.args[0])
                        if imported_module:
                            self._add_dependency(module_name, imported_module, file_path, node.lineno)

    def _extract_import_module_name(self, arg_node) -> str:
        """
        Extract module name from import argument.

        Handles:
        - Constant: 'fastapi'
        - Name (variable): module_name
        - JoinedStr (f-string): f"prefix.{suffix}"
        """
        if isinstance(arg_node, ast.Constant):
            return arg_node.value
        elif isinstance(arg_node, ast.Name):
            # Variable name - mark as dynamic
            return f"<dynamic:{arg_node.id}>"
        elif isinstance(arg_node, ast.JoinedStr):
            # f-string - try to extract static parts
            parts = []
            for value in arg_node.values:
                if isinstance(value, ast.Constant):
                    parts.append(value.value)
                elif isinstance(value, ast.FormattedValue):
                    # Dynamic part - mark as variable
                    if isinstance(value.value, ast.Name):
                        parts.append(f"<{value.value.id}>")
                    else:
                        parts.append("<expr>")
            return "".join(parts) if parts else None
        return None

    def _add_dependency(self, from_module: str, to_module: str, file_path: Path,
                       line: int, names: List[str] = None):
        """Добавить зависимость"""
        # Ignore standard library
        if to_module.split('.')[0] in ['os', 'sys', 'typing', 'datetime', 'asyncio',
                                         'pathlib', 'json', 'logging', 'collections']:
            return

        # Ignore dynamic placeholders from standard imports
        if to_module.startswith('<dynamic:') or to_module.startswith('<expr>'):
            # Still log it but with special marker
            to_module = f"DYNAMIC_IMPORT"

        self.dependencies[from_module].add(to_module)
        self.imports_detail[from_module].append({
            'module': to_module,
            'file': str(file_path),
            'line': line,
            'names': names or []
        })

    def _get_module_name(self, file_path: Path) -> str:
        """Получить имя модуля из пути к файлу"""
        # Преобразовать путь в имя модуля Python
        parts = file_path.parts

        # Найти индекс platform-services или shared
        try:
            if 'platform-services' in parts:
                idx = parts.index('platform-services')
                module_parts = parts[idx+1:]
            elif 'shared' in parts:
                idx = parts.index('shared')
                module_parts = parts[idx:]
            else:
                module_parts = parts[-2:]

            # Убрать .py и __init__
            module_name = '.'.join(module_parts)
            module_name = module_name.replace('.py', '').replace('.__init__', '')
            return module_name
        except:
            return str(file_path.stem)

    def _calculate_stats(self) -> Dict:
        """Расчет статистики зависимостей"""
        total_modules = len(self.dependencies)
        total_edges = sum(len(deps) for deps in self.dependencies.values())

        # Найти самые зависимые модули
        most_dependencies = sorted(
            [(mod, len(deps)) for mod, deps in self.dependencies.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Найти модули, от которых больше всего зависят
        incoming_deps = defaultdict(int)
        for mod, deps in self.dependencies.items():
            for dep in deps:
                incoming_deps[dep] += 1

        most_depended_on = sorted(
            incoming_deps.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            'total_modules': total_modules,
            'total_dependencies': total_edges,
            'avg_dependencies': total_edges / total_modules if total_modules > 0 else 0,
            'most_dependencies': [{'module': m, 'count': c} for m, c in most_dependencies],
            'most_depended_on': [{'module': m, 'count': c} for m, c in most_depended_on]
        }

    def generate_graph(self, output_file: str = "infrastructure/AI-office-infrastructure/devops-agent/reports-generated/dependency_graph.png"):
        """Генерировать граф зависимостей"""
        print("\n📊 Generating dependency graph...")

        G = nx.DiGraph()

        # Добавить узлы и ребра
        for module, deps in self.dependencies.items():
            G.add_node(module)
            for dep in deps:
                G.add_edge(module, dep)

        # Определить размер узлов по количеству зависимостей
        node_sizes = [len(self.dependencies.get(node, [])) * 100 + 300 for node in G.nodes()]

        # Создать визуализацию
        plt.figure(figsize=(20, 20))
        pos = nx.spring_layout(G, k=2, iterations=50)

        # Нарисовать граф
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='lightblue', alpha=0.7)
        nx.draw_networkx_labels(G, pos, font_size=8)
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True,
                              arrowsize=10, alpha=0.5, width=1)

        plt.title("Module Dependency Graph", fontsize=16)
        plt.axis('off')
        plt.tight_layout()

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✅ Graph saved: {output_path}")

        # Также сохранить в формате GraphML для Gephi/Cytoscape
        graphml_file = output_path.with_suffix('.graphml')
        nx.write_graphml(G, graphml_file)
        print(f"✅ GraphML saved: {graphml_file}")

    def detect_circular_dependencies(self) -> List[List[str]]:
        """Обнаружить циклические зависимости"""
        print("\n🔄 Detecting circular dependencies...")

        G = nx.DiGraph()
        for module, deps in self.dependencies.items():
            for dep in deps:
                G.add_edge(module, dep)

        try:
            cycles = list(nx.simple_cycles(G))
            if cycles:
                print(f"⚠️  Found {len(cycles)} circular dependencies!")
                for i, cycle in enumerate(cycles[:5]):  # Show first 5
                    print(f"   {i+1}. {' → '.join(cycle + [cycle[0]])}")
            else:
                print("✅ No circular dependencies found")
            return cycles
        except:
            return []

    def save_results(self, output_dir: str = "infrastructure/AI-office-infrastructure/devops-agent/reports-generated"):
        """Сохранить результаты анализа"""
        results = self.analyze_dependencies()

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # JSON
        json_file = output_path / "dependencies.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✅ Dependencies JSON: {json_file}")

        # Markdown
        md_file = output_path / "dependencies.md"
        self._generate_markdown(results, md_file)
        print(f"✅ Dependencies Markdown: {md_file}")

        # Graph
        self.generate_graph(str(output_path / "dependency_graph.png"))

        # Circular dependencies
        cycles = self.detect_circular_dependencies()
        if cycles:
            cycles_file = output_path / "circular_dependencies.json"
            with open(cycles_file, 'w') as f:
                json.dump(cycles, f, indent=2)
            print(f"⚠️  Circular dependencies: {cycles_file}")

        # Stats
        print(f"\n📊 STATISTICS:")
        print(f"   Total modules: {results['statistics']['total_modules']}")
        print(f"   Total dependencies: {results['statistics']['total_dependencies']}")
        print(f"   Avg dependencies: {results['statistics']['avg_dependencies']:.1f}")

        return results

    def _generate_markdown(self, results: Dict, output_file: Path):
        """Генерировать Markdown отчет"""
        with open(output_file, 'w') as f:
            f.write("# Module Dependencies Report\n\n")

            # Statistics
            stats = results['statistics']
            f.write("## Statistics\n\n")
            f.write(f"- **Total Modules:** {stats['total_modules']}\n")
            f.write(f"- **Total Dependencies:** {stats['total_dependencies']}\n")
            f.write(f"- **Average Dependencies:** {stats['avg_dependencies']:.1f}\n\n")

            # Most dependencies
            f.write("## Modules with Most Dependencies\n\n")
            f.write("| Module | Dependencies Count |\n")
            f.write("|--------|-------------------|\n")
            for item in stats['most_dependencies']:
                f.write(f"| {item['module']} | {item['count']} |\n")

            # Most depended on
            f.write("\n## Most Depended On Modules\n\n")
            f.write("| Module | Dependents Count |\n")
            f.write("|--------|------------------|\n")
            for item in stats['most_depended_on']:
                f.write(f"| {item['module']} | {item['count']} |\n")

            # Dependency list
            f.write("\n## Full Dependency List\n\n")
            for module, deps in sorted(results['dependencies'].items()):
                if deps:
                    f.write(f"### {module}\n")
                    for dep in sorted(deps):
                        f.write(f"- {dep}\n")
                    f.write("\n")


if __name__ == "__main__":
    mapper = DependencyMapper()
    mapper.save_results()
