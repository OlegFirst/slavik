#!/usr/bin/env python3
"""
AST Analyzer - Извлечение всех функций, классов, эндпоинтов из кода
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import yaml


@dataclass
class FunctionInfo:
    name: str
    file: str
    line: int
    docstring: str
    params: List[str]
    returns: str
    decorators: List[str]
    complexity: int = 0
    is_async: bool = False


@dataclass
class ClassInfo:
    name: str
    file: str
    line: int
    docstring: str
    methods: List[str]
    bases: List[str]
    decorators: List[str]


@dataclass
class EndpointInfo:
    path: str
    method: str
    function: str
    file: str
    line: int
    params: List[str]
    response_model: str
    dependencies: List[str]


class ASTAnalyzer:
    def __init__(self, config_path: str = "tools/config/analysis_config.yaml"):
        # Try to find config file - check multiple possible locations
        from pathlib import Path
        possible_paths = [
            Path(config_path),
            Path(__file__).parent.parent / "config" / "analysis_config.yaml",
            Path(__file__).parent / "config" / "analysis_config.yaml",
        ]

        config_file = None
        for path in possible_paths:
            if path.exists():
                config_file = path
                break

        if not config_file:
            raise FileNotFoundError(f"Could not find analysis_config.yaml in any of: {possible_paths}")

        with open(config_file) as f:
            self.config = yaml.safe_load(f)

        self.functions: List[FunctionInfo] = []
        self.classes: List[ClassInfo] = []
        self.endpoints: List[EndpointInfo] = []

    def analyze_project(self) -> Dict[str, Any]:
        """Сканировать весь проект"""
        print(" Scanning project for functions, classes, endpoints...")

        # Use 'analysis_targets' or 'scan_paths' depending on config format
        scan_paths = self.config.get('scan_paths') or self.config.get('analysis_targets', [])

        for scan_path in scan_paths:
            path = Path(scan_path)
            if not path.exists():
                print(f"️  Path not found: {path}")
                continue

            print(f"\n Analyzing: {scan_path}")
            self._scan_directory(path)

        return {
            'functions': [asdict(f) for f in self.functions],
            'classes': [asdict(c) for c in self.classes],
            'endpoints': [asdict(e) for e in self.endpoints],
            'summary': {
                'total_functions': len(self.functions),
                'total_classes': len(self.classes),
                'total_endpoints': len(self.endpoints),
                'async_functions': sum(1 for f in self.functions if f.is_async),
            }
        }

    def _scan_directory(self, directory: Path):
        """Рекурсивно сканировать директорию"""
        errors = []
        for py_file in directory.rglob("*.py"):
            # Пропустить исключения
            if any(exclude in str(py_file) for exclude in self.config['exclude']):
                continue

            try:
                self._analyze_file(py_file)
            except SyntaxError as e:
                error_msg = f"️  Error analyzing {py_file}: {e.__class__.__name__}: {e}"
                print(error_msg)
                errors.append({'file': str(py_file), 'error': str(e), 'type': 'SyntaxError'})
            except UnicodeDecodeError as e:
                error_msg = f"️  Error analyzing {py_file}: {e.__class__.__name__}: {e}"
                print(error_msg)
                errors.append({'file': str(py_file), 'error': str(e), 'type': 'UnicodeDecodeError'})
            except Exception as e:
                error_msg = f"️  Error analyzing {py_file}: {e.__class__.__name__}: {e}"
                print(error_msg)
                errors.append({'file': str(py_file), 'error': str(e), 'type': type(e).__name__})

        # Store errors for later reporting
        if not hasattr(self, 'errors'):
            self.errors = []
        self.errors.extend(errors)

    def _analyze_file(self, file_path: Path):
        """Анализировать один Python файл"""
        with open(file_path) as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        # FIXED: Only process top-level nodes, not nested ones!
        # Classes will handle their own methods
        for node in tree.body:  # Changed from ast.walk to tree.body
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                self._extract_function(node, file_path)
            elif isinstance(node, ast.ClassDef):
                self._extract_class(node, file_path)

    def _extract_function(self, node: ast.FunctionDef, file_path: Path):
        """Извлечь информацию о функции"""
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]

        # Проверить, является ли это FastAPI эндпоинтом
        if any(d in ['get', 'post', 'put', 'delete', 'patch'] for d in decorators):
            self._extract_endpoint(node, file_path, decorators)

        func_info = FunctionInfo(
            name=node.name,
            file=str(file_path),
            line=node.lineno,
            docstring=ast.get_docstring(node) or "",
            params=[arg.arg for arg in node.args.args],
            returns=self._get_return_annotation(node),
            decorators=decorators,
            is_async=isinstance(node, ast.AsyncFunctionDef)
        )

        self.functions.append(func_info)

    def _extract_class(self, node: ast.ClassDef, file_path: Path):
        """Извлечь информацию о классе"""
        # FIXED: Extract methods as full FunctionInfo, not just names!
        methods = []
        method_names = []

        for n in node.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_names.append(n.name)

                # FIXED: Add class methods to self.functions too!
                decorators = [self._get_decorator_name(d) for d in n.decorator_list]

                func_info = FunctionInfo(
                    name=f"{node.name}.{n.name}",  # Include class name
                    file=str(file_path),
                    line=n.lineno,
                    docstring=ast.get_docstring(n) or "",
                    params=[arg.arg for arg in n.args.args],
                    returns=self._get_return_annotation(n),
                    decorators=decorators,
                    is_async=isinstance(n, ast.AsyncFunctionDef)
                )

                self.functions.append(func_info)  # FIXED: Add to functions list!

        bases = [self._get_name(base) for base in node.bases]
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]

        class_info = ClassInfo(
            name=node.name,
            file=str(file_path),
            line=node.lineno,
            docstring=ast.get_docstring(node) or "",
            methods=method_names,  # Still keep method names in class
            bases=bases,
            decorators=decorators
        )

        self.classes.append(class_info)

    def _extract_endpoint(self, node: ast.FunctionDef, file_path: Path, decorators: List[str]):
        """Извлечь FastAPI эндпоинт"""
        # Найти декоратор маршрута
        route_decorator = None
        for d in node.decorator_list:
            if isinstance(d, ast.Call) and hasattr(d.func, 'attr'):
                if d.func.attr in ['get', 'post', 'put', 'delete', 'patch']:
                    route_decorator = d
                    break

        if not route_decorator:
            return

        # Извлечь путь
        path = ""
        if route_decorator.args:
            if isinstance(route_decorator.args[0], ast.Constant):
                path = route_decorator.args[0].value

        # Извлечь зависимости (Depends)
        dependencies = []
        for default in node.args.defaults:
            if isinstance(default, ast.Call) and hasattr(default.func, 'id'):
                if default.func.id == 'Depends':
                    if default.args:
                        dependencies.append(self._get_name(default.args[0]))

        endpoint_info = EndpointInfo(
            path=path,
            method=route_decorator.func.attr.upper(),
            function=node.name,
            file=str(file_path),
            line=node.lineno,
            params=[arg.arg for arg in node.args.args],
            response_model=self._get_return_annotation(node),
            dependencies=dependencies
        )

        self.endpoints.append(endpoint_info)

    def _get_decorator_name(self, decorator) -> str:
        """Получить имя декоратора"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        elif isinstance(decorator, ast.Call):
            if hasattr(decorator.func, 'attr'):
                return decorator.func.attr
            elif hasattr(decorator.func, 'id'):
                return decorator.func.id
        return "unknown"

    def _get_return_annotation(self, node: ast.FunctionDef) -> str:
        """Получить тип возвращаемого значения"""
        if node.returns:
            return self._get_name(node.returns)
        return "Any"

    def _get_name(self, node) -> str:
        """Получить имя из AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._get_name(node.value)}[{self._get_name(node.slice)}]"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return "Unknown"

    def save_results(self, output_dir: str = "infrastructure/AI-office-infrastructure/devops-agent/reports-generated"):
        """Сохранить результаты анализа"""
        results = self.analyze_project()

        # Add errors to results
        if hasattr(self, 'errors') and self.errors:
            results['errors'] = self.errors
            results['summary']['total_errors'] = len(self.errors)
            results['summary']['error_types'] = {}
            for error in self.errors:
                error_type = error['type']
                results['summary']['error_types'][error_type] = results['summary']['error_types'].get(error_type, 0) + 1

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # JSON
        json_file = output_path / "ast_analysis.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n JSON report: {json_file}")

        # Errors log
        if hasattr(self, 'errors') and self.errors:
            errors_file = output_path / "ast_errors.log"
            with open(errors_file, 'w') as f:
                f.write("AST Analysis Errors\n")
                f.write("=" * 80 + "\n\n")
                for error in self.errors:
                    f.write(f"File: {error['file']}\n")
                    f.write(f"Type: {error['type']}\n")
                    f.write(f"Error: {error['error']}\n")
                    f.write("-" * 80 + "\n\n")
            print(f"️  Error log: {errors_file} ({len(self.errors)} errors)")

        # Markdown
        md_file = output_path / "ast_analysis.md"
        self._generate_markdown(results, md_file)
        print(f" Markdown report: {md_file}")

        # Summary
        print(f"\n SUMMARY:")
        print(f"   Functions: {results['summary']['total_functions']}")
        print(f"   Classes: {results['summary']['total_classes']}")
        print(f"   Endpoints: {results['summary']['total_endpoints']}")
        print(f"   Async functions: {results['summary']['async_functions']}")

        return results

    def _generate_markdown(self, results: Dict, output_file: Path):
        """Генерировать Markdown отчет"""
        with open(output_file, 'w') as f:
            f.write("# AST Analysis Report\n\n")

            # Summary
            f.write("## Summary\n\n")
            f.write(f"- **Total Functions:** {results['summary']['total_functions']}\n")
            f.write(f"- **Total Classes:** {results['summary']['total_classes']}\n")
            f.write(f"- **Total Endpoints:** {results['summary']['total_endpoints']}\n")
            f.write(f"- **Async Functions:** {results['summary']['async_functions']}\n\n")

            # Endpoints
            f.write("## API Endpoints\n\n")
            f.write("| Method | Path | Function | File |\n")
            f.write("|--------|------|----------|------|\n")
            for endpoint in results['endpoints']:
                f.write(f"| {endpoint['method']} | `{endpoint['path']}` | {endpoint['function']} | {endpoint['file']} |\n")

            # Classes
            f.write("\n## Classes\n\n")
            for cls in results['classes']:
                f.write(f"### {cls['name']}\n")
                f.write(f"- **File:** {cls['file']}:{cls['line']}\n")
                if cls['docstring']:
                    f.write(f"- **Description:** {cls['docstring'][:100]}...\n")
                f.write(f"- **Methods:** {', '.join(cls['methods'])}\n\n")


if __name__ == "__main__":
    analyzer = ASTAnalyzer()
    analyzer.save_results()
