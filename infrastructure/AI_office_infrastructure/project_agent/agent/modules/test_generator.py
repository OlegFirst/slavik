"""Test Generator Module — автоматическая генерация тестов"""
from __future__ import annotations
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass


@dataclass
class FunctionInfo:
    """Information about a function to test"""
    name: str
    file_path: str
    line_number: int
    is_async: bool
    parameters: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    decorators: List[str]
    class_name: Optional[str]


@dataclass
class ClassInfo:
    """Information about a class to test"""
    name: str
    file_path: str
    line_number: int
    methods: List[FunctionInfo]
    base_classes: List[str]
    docstring: Optional[str]


class CodeAnalyzer(ast.NodeVisitor):
    """Analyzes Python AST to extract testable components"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.functions: List[FunctionInfo] = []
        self.classes: List[ClassInfo] = []
        self.current_class: Optional[str] = None
        self.imports: List[str] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        module = node.module or ""
        for alias in node.names:
            self.imports.append(f"{module}.{alias.name}")
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                method_info = self._extract_function_info(item, class_name=node.name)
                methods.append(method_info)

        class_info = ClassInfo(
            name=node.name,
            file_path=self.file_path,
            line_number=node.lineno,
            methods=methods,
            base_classes=[base.id if isinstance(base, ast.Name) else str(base) for base in node.bases],
            docstring=ast.get_docstring(node)
        )
        self.classes.append(class_info)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if not self.current_class:
            func_info = self._extract_function_info(node)
            self.functions.append(func_info)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        if not self.current_class:
            func_info = self._extract_function_info(node, is_async=True)
            self.functions.append(func_info)
        self.generic_visit(node)

    def _extract_function_info(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        class_name: Optional[str] = None,
        is_async: bool = None
    ) -> FunctionInfo:
        """Extract function information from AST node"""
        parameters = []
        for arg in node.args.args:
            if arg.arg != 'self' and arg.arg != 'cls':
                parameters.append(arg.arg)

        return_type = None
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return_type = node.returns.id
            else:
                return_type = ast.unparse(node.returns)

        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            else:
                decorators.append(ast.unparse(dec))

        return FunctionInfo(
            name=node.name,
            file_path=self.file_path,
            line_number=node.lineno,
            is_async=is_async if is_async is not None else isinstance(node, ast.AsyncFunctionDef),
            parameters=parameters,
            return_type=return_type,
            docstring=ast.get_docstring(node),
            decorators=decorators,
            class_name=class_name
        )


class TemplateTestGenerator:
    """Generates pytest tests using templates"""

    def generate_function_tests(self, func: FunctionInfo, module_name: str) -> str:
        """Generate tests for a function using templates"""
        tests = []

        # Happy path test
        if func.is_async:
            tests.append(self._async_happy_path_template(func, module_name))
        else:
            tests.append(self._sync_happy_path_template(func, module_name))

        # Error handling test
        if func.parameters:
            tests.append(self._error_handling_template(func, module_name))

        # Edge case test
        tests.append(self._edge_case_template(func, module_name))

        return "\n\n".join(tests)

    def _async_happy_path_template(self, func: FunctionInfo, module_name: str) -> str:
        params = ", ".join([f"{p}=None" for p in func.parameters[:3]])
        return f'''@pytest.mark.asyncio
async def test_{func.name}_successful_execution():
    """Test {func.name} executes successfully with valid inputs"""
    # ARRANGE
    {self._generate_arrange_section(func)}

    # ACT
    result = await {func.name}({params})

    # ASSERT
    assert result is not None
    # TODO: Add specific assertions based on expected behavior'''

    def _sync_happy_path_template(self, func: FunctionInfo, module_name: str) -> str:
        params = ", ".join([f"{p}=None" for p in func.parameters[:3]])
        return f'''def test_{func.name}_successful_execution():
    """Test {func.name} executes successfully with valid inputs"""
    # ARRANGE
    {self._generate_arrange_section(func)}

    # ACT
    result = {func.name}({params})

    # ASSERT
    assert result is not None
    # TODO: Add specific assertions based on expected behavior'''

    def _error_handling_template(self, func: FunctionInfo, module_name: str) -> str:
        first_param = func.parameters[0] if func.parameters else "invalid_input"
        if func.is_async:
            return f'''@pytest.mark.asyncio
async def test_{func.name}_handles_invalid_input():
    """Test {func.name} raises appropriate error for invalid input"""
    # ARRANGE
    {first_param} = None  # Invalid value

    # ACT & ASSERT
    with pytest.raises(Exception):  # TODO: Specify exact exception type
        await {func.name}({first_param}=None)'''
        else:
            return f'''def test_{func.name}_handles_invalid_input():
    """Test {func.name} raises appropriate error for invalid input"""
    # ARRANGE
    {first_param} = None  # Invalid value

    # ACT & ASSERT
    with pytest.raises(Exception):  # TODO: Specify exact exception type
        {func.name}({first_param}=None)'''

    def _edge_case_template(self, func: FunctionInfo, module_name: str) -> str:
        if func.is_async:
            return f'''@pytest.mark.asyncio
async def test_{func.name}_handles_edge_cases():
    """Test {func.name} handles edge cases correctly"""
    # TODO: Implement edge case scenarios
    pass'''
        else:
            return f'''def test_{func.name}_handles_edge_cases():
    """Test {func.name} handles edge cases correctly"""
    # TODO: Implement edge case scenarios
    pass'''

    def _generate_arrange_section(self, func: FunctionInfo) -> str:
        arranges = []
        for param in func.parameters[:3]:
            if 'context' in param.lower():
                arranges.append(f"    {param} = {{'workflow_id': 'test-001', 'module': 'test'}}")
            elif 'id' in param.lower():
                arranges.append(f"    {param} = 'test-id-123'")
            elif 'data' in param.lower():
                arranges.append(f"    {param} = {{'key': 'value'}}")
            else:
                arranges.append(f"    {param} = None  # TODO: Provide valid test data")
        return "\n    ".join(arranges) if arranges else "    # No parameters to arrange"

    def generate_class_tests(self, cls: ClassInfo, module_name: str) -> str:
        """Generate tests for a class"""
        tests = []
        tests.append(f'''class Test{cls.name}:
    """Test suite for {cls.name}"""

    def test_{cls.name.lower()}_initialization(self):
        """Test {cls.name} can be instantiated"""
        # ARRANGE
        # TODO: Prepare initialization parameters

        # ACT
        instance = {cls.name}()

        # ASSERT
        assert instance is not None
        assert isinstance(instance, {cls.name})
''')

        for method in cls.methods:
            if method.name.startswith('_') and method.name != '__init__':
                continue
            method_tests = self._generate_method_test(cls, method)
            tests.append(f"    {method_tests}")

        return "\n\n".join(tests)

    def _generate_method_test(self, cls: ClassInfo, method: FunctionInfo) -> str:
        params = ", ".join([f"{p}=None" for p in method.parameters[:2]])
        if method.is_async:
            return f'''@pytest.mark.asyncio
    async def test_{cls.name.lower()}_{method.name}_works(self):
        """Test {cls.name}.{method.name}() executes successfully"""
        # ARRANGE
        instance = {cls.name}()

        # ACT
        result = await instance.{method.name}({params})

        # ASSERT
        # TODO: Add assertions
        pass'''
        else:
            return f'''def test_{cls.name.lower()}_{method.name}_works(self):
        """Test {cls.name}.{method.name}() executes successfully"""
        # ARRANGE
        instance = {cls.name}()

        # ACT
        result = instance.{method.name}({params})

        # ASSERT
        # TODO: Add assertions
        pass'''


def generate_tests_for_module(
    module_path: Path,
    output_dir: Path,
    max_files: int = 10,
    verbose: bool = False
) -> Dict[str, Any]:
    """Generate tests for all files in a module"""

    output_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "files_processed": 0,
        "tests_generated": 0,
        "errors": []
    }

    template_generator = TemplateTestGenerator()

    # Find all Python files
    python_files = list(module_path.rglob("*.py"))
    python_files = [
        f for f in python_files
        if f.name != "__init__.py" and not f.name.startswith("test_")
    ][:max_files]

    for file_path in python_files:
        if verbose:
            print(f"📝 Analyzing: {file_path.relative_to(module_path.parent)}")

        functions, classes = analyze_file(str(file_path))

        if not functions and not classes:
            if verbose:
                print("  ⏭️  No testable components found")
            continue

        results["files_processed"] += 1

        # Generate test file
        relative_path = file_path.relative_to(module_path)
        test_file_name = f"test_{relative_path.stem}.py"
        test_file_path = output_dir / test_file_name

        # Generate test code
        test_code_parts = [
            f'"""Auto-generated tests for {file_path.relative_to(module_path.parent)}"""',
            "",
            "import pytest",
            "from unittest.mock import Mock, AsyncMock, patch, MagicMock",
            "",
            f"# from {module_path.name}.{relative_path.stem} import *",
            "",
            ""
        ]

        # Tests for functions
        for func in functions:
            if func.name.startswith("_"):
                continue
            if verbose:
                print(f"  🧪 {func.name}")
            test_code = template_generator.generate_function_tests(func, module_path.name)
            test_code_parts.append(test_code)
            test_code_parts.append("\n")
            results["tests_generated"] += 1

        # Tests for classes
        for cls in classes:
            if cls.name.startswith("_"):
                continue
            if verbose:
                print(f"  🧪 {cls.name}")
            test_code = template_generator.generate_class_tests(cls, module_path.name)
            test_code_parts.append(test_code)
            test_code_parts.append("\n")
            results["tests_generated"] += 1

        # Write test file
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(test_code_parts))

        if verbose:
            print(f"  ✅ Generated: {test_file_path.relative_to(module_path.parent.parent)}")

    return results


def analyze_file(file_path: str) -> tuple:
    """Analyze Python file and extract testable components"""
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()

    try:
        tree = ast.parse(source)
        analyzer = CodeAnalyzer(file_path)
        analyzer.visit(tree)
        return analyzer.functions, analyzer.classes
    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}")
        return [], []


def run_test_generation(config: Dict, target_module: str = None, max_files: int = 10) -> Dict[str, Any]:
    """
    Main entry point for test generation from project_agent

    Args:
        config: Project agent configuration
        target_module: Specific module to generate tests for (or None for all)
        max_files: Maximum files to process per module

    Returns:
        {
            "modules": {...},
            "summary": {...}
        }
    """
    from ..config import get_repo_path

    repo_path = get_repo_path()
    test_gen_config = config.get("modules", {}).get("test_generation", {})
    enabled = test_gen_config.get("enabled", True)

    if not enabled:
        return {"error": "Test generation module is disabled"}

    results = {
        "modules": {},
        "summary": {
            "total_files": 0,
            "total_tests": 0,
            "modules_processed": 0
        }
    }

    # Find intelligent-core modules
    intelligent_core = repo_path / "intelligent-core"
    if not intelligent_core.exists():
        return {"error": "intelligent-core directory not found"}

    # Get modules to process
    if target_module:
        modules_to_process = [target_module]
    else:
        modules_to_process = [
            "workflow_intelligence", "ai-foundation", "orchestration",
            "expertise-center", "collective", "community_intelligence",
            "predictive", "workflow-engine", "ai_workflow_optimizer"
        ]

    # Generate tests for each module
    for module_name in modules_to_process:
        module_path = intelligent_core / module_name
        if not module_path.exists():
            continue

        output_dir = repo_path / "tests" / "generated" / module_name

        module_results = generate_tests_for_module(
            module_path,
            output_dir,
            max_files=max_files,
            verbose=True
        )

        results["modules"][module_name] = module_results
        results["summary"]["total_files"] += module_results["files_processed"]
        results["summary"]["total_tests"] += module_results["tests_generated"]
        results["summary"]["modules_processed"] += 1

    return results
