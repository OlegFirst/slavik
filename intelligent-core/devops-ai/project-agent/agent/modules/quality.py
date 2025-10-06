"""Quality Module — анализ качества кода"""
from __future__ import annotations
import re
import ast
from pathlib import Path
from typing import Dict, List
from collections import Counter
from ..config import get_repo_path, get_reports_dir

def run_quality_checks(config: Dict) -> Dict[str, any]:
    """
    Анализирует качество кода

    Returns:
        {
            "complexity": {...},
            "duplication": {...},
            "tech_debt": {...},
            "summary": {...}
        }
    """
    checks = config.get("modules", {}).get("quality", {}).get("checks", [])
    repo_path = get_repo_path()

    results = {
        "complexity": {},
        "duplication": {},
        "tech_debt": {},
        "summary": {}
    }

    # 1. Cyclomatic complexity
    if "complexity" in checks:
        results["complexity"] = _check_complexity(repo_path)

    # 2. Code duplication
    if "duplication" in checks:
        results["duplication"] = _check_duplication(repo_path)

    # 3. Technical debt indicators
    if "tech-debt" in checks:
        results["tech_debt"] = _check_tech_debt(repo_path)

    # Summary
    results["summary"] = {
        "high_complexity_functions": len([f for f in results["complexity"].get("functions", []) if f["complexity"] > 10]),
        "duplicate_blocks": results["duplication"].get("duplicate_blocks", 0),
        "tech_debt_items": len(results["tech_debt"].get("items", [])),
        "status": "OK"  # TODO: определять статус по порогам
    }

    # Сохраняем отчет
    _save_quality_report(results)

    return results

def _check_complexity(repo_path: Path) -> Dict:
    """Проверяет cyclomatic complexity функций (Python only пока)"""
    functions = []
    exclude_dirs = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build'}

    for py_file in repo_path.rglob("*.py"):
        if any(ex in py_file.parts for ex in exclude_dirs):
            continue

        if py_file.stat().st_size > 1_000_000:
            continue

        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(content, filename=str(py_file))

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    complexity = _calculate_complexity(node)
                    if complexity > 5:  # Only report functions with complexity > 5
                        functions.append({
                            "file": str(py_file.relative_to(repo_path)),
                            "function": node.name,
                            "line": node.lineno,
                            "complexity": complexity
                        })
        except Exception:
            continue

    # Сортируем по complexity
    functions.sort(key=lambda x: x["complexity"], reverse=True)

    return {
        "functions": functions[:50],  # Top 50
        "note": "Currently only Python is analyzed for complexity"
    }

def _calculate_complexity(node: ast.FunctionDef) -> int:
    """Вычисляет cyclomatic complexity функции"""
    complexity = 1  # Base complexity

    for child in ast.walk(node):
        # +1 за каждую decision point
        if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
            complexity += 1
        elif isinstance(child, ast.ExceptHandler):
            complexity += 1
        elif isinstance(child, (ast.And, ast.Or)):
            complexity += 1
        elif isinstance(child, ast.comprehension):
            complexity += 1

    return complexity

def _check_duplication(repo_path: Path) -> Dict:
    """Ищет дублирование кода (простая эвристика)"""
    # Простая эвристика: ищем идентичные блоки кода (>5 строк)
    code_blocks = Counter()
    exclude_dirs = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build'}

    for code_file in repo_path.rglob("*"):
        if code_file.is_dir() or any(ex in code_file.parts for ex in exclude_dirs):
            continue

        if code_file.suffix not in {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go'}:
            continue

        if code_file.stat().st_size > 1_000_000:
            continue

        try:
            lines = code_file.read_text(encoding='utf-8', errors='ignore').splitlines()

            # Берем блоки по 5 строк
            for i in range(len(lines) - 4):
                block = '\n'.join(lines[i:i+5]).strip()
                # Игнорируем пустые и комментарии
                if block and not block.startswith('#') and not block.startswith('//'):
                    code_blocks[block] += 1
        except Exception:
            continue

    # Находим дубликаты (встречаются >1 раза)
    duplicates = [(block[:80], count) for block, count in code_blocks.items() if count > 1]

    return {
        "duplicate_blocks": len(duplicates),
        "top_duplicates": sorted(duplicates, key=lambda x: x[1], reverse=True)[:10],
        "note": "Simple heuristic: 5-line blocks"
    }

def _check_tech_debt(repo_path: Path) -> Dict:
    """Ищет индикаторы технического долга (TODO, FIXME, HACK, etc.)"""
    debt_patterns = [
        (r'#\s*TODO', 'TODO'),
        (r'#\s*FIXME', 'FIXME'),
        (r'#\s*HACK', 'HACK'),
        (r'#\s*XXX', 'XXX'),
        (r'//\s*TODO', 'TODO'),
        (r'//\s*FIXME', 'FIXME'),
        (r'//\s*HACK', 'HACK'),
    ]

    items = []
    exclude_dirs = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build'}

    for code_file in repo_path.rglob("*"):
        if code_file.is_dir() or any(ex in code_file.parts for ex in exclude_dirs):
            continue

        if code_file.suffix not in {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.c', '.cpp', '.h'}:
            continue

        if code_file.stat().st_size > 1_000_000:
            continue

        try:
            content = code_file.read_text(encoding='utf-8', errors='ignore')

            for pattern, debt_type in debt_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = content.split('\n')[line_num - 1].strip()
                    items.append({
                        "file": str(code_file.relative_to(repo_path)),
                        "line": line_num,
                        "type": debt_type,
                        "content": line_content[:100]
                    })
        except Exception:
            continue

    # Группируем по типу
    by_type = {}
    for item in items:
        debt_type = item["type"]
        by_type[debt_type] = by_type.get(debt_type, 0) + 1

    return {
        "items": items,
        "by_type": by_type,
        "total": len(items)
    }

def _save_quality_report(results: Dict) -> None:
    """Сохраняет отчет о качестве кода"""
    import json
    reports_dir = get_reports_dir()

    # JSON
    json_path = reports_dir / "quality_report.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Markdown
    md_path = reports_dir / "quality_report.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# Code Quality Report\n\n")
        f.write(f"**Status:** {results['summary']['status']}\n\n")

        f.write("## Summary\n\n")
        f.write(f"- High complexity functions: **{results['summary']['high_complexity_functions']}**\n")
        f.write(f"- Duplicate blocks: **{results['summary']['duplicate_blocks']}**\n")
        f.write(f"- Tech debt items: **{results['summary']['tech_debt_items']}**\n\n")

        # Complexity
        if results["complexity"].get("functions"):
            f.write("## High Complexity Functions (Top 10)\n\n")
            for func in results["complexity"]["functions"][:10]:
                f.write(f"- `{func['file']}:{func['line']}` — **{func['function']}()** (complexity: {func['complexity']})\n")
            f.write("\n")

        # Duplication
        if results["duplication"].get("top_duplicates"):
            f.write("## Top Duplicate Code Blocks\n\n")
            for block, count in results["duplication"]["top_duplicates"][:5]:
                f.write(f"- Found **{count}** times: `{block}...`\n")
            f.write("\n")

        # Tech Debt
        if results["tech_debt"].get("items"):
            f.write(f"## Technical Debt ({results['tech_debt']['total']} items)\n\n")
            by_type = results["tech_debt"].get("by_type", {})
            for debt_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{debt_type}**: {count} items\n")
            f.write("\n")

            f.write("### Recent Items (10)\n\n")
            for item in results["tech_debt"]["items"][:10]:
                f.write(f"- `{item['file']}:{item['line']}` — {item['type']}: {item['content']}\n")
