"""Testing Module — анализ тестового покрытия и качества тестов"""
from __future__ import annotations
import subprocess
import json
from pathlib import Path
from typing import Dict, List
from ..config import get_repo_path, get_reports_dir

def run_testing_checks(config: Dict) -> Dict[str, any]:
    """
    Анализирует тестовое покрытие проекта

    Returns:
        {
            "coverage": {...},
            "test_files": [...],
            "frameworks": [...],
            "summary": {...}
        }
    """
    testing_config = config.get("modules", {}).get("testing", {})
    threshold = testing_config.get("coverage_threshold", 70)
    frameworks = testing_config.get("frameworks", ["pytest", "jest", "go-test"])

    repo_path = get_repo_path()

    results = {
        "coverage": {},
        "test_files": [],
        "frameworks": [],
        "summary": {}
    }

    # Определяем какие фреймворки есть в проекте
    detected_frameworks = _detect_test_frameworks(repo_path)
    results["frameworks"] = detected_frameworks

    # Ищем тестовые файлы
    test_files = _find_test_files(repo_path)
    results["test_files"] = test_files

    # Запускаем тесты и собираем coverage (если возможно)
    if "pytest" in detected_frameworks:
        results["coverage"]["python"] = _run_pytest_coverage(repo_path)

    if "jest" in detected_frameworks:
        results["coverage"]["javascript"] = _run_jest_coverage(repo_path)

    if "go-test" in detected_frameworks:
        results["coverage"]["go"] = _run_go_coverage(repo_path)

    # Summary
    avg_coverage = _calculate_average_coverage(results["coverage"])
    results["summary"] = {
        "test_files_count": len(test_files),
        "frameworks_detected": detected_frameworks,
        "average_coverage": avg_coverage,
        "threshold": threshold,
        "status": "OK" if avg_coverage >= threshold else "BELOW_THRESHOLD"
    }

    # Сохраняем отчет
    _save_testing_report(results)

    return results

def _detect_test_frameworks(repo_path: Path) -> List[str]:
    """Определяет какие тестовые фреймворки используются"""
    frameworks = []

    # Python: pytest
    if (repo_path / "pytest.ini").exists() or \
       (repo_path / "setup.cfg").exists() or \
       list(repo_path.rglob("test_*.py")) or \
       list(repo_path.rglob("*_test.py")):
        frameworks.append("pytest")

    # JavaScript: jest
    package_json = repo_path / "package.json"
    if package_json.exists():
        try:
            import json
            with open(package_json, 'r', encoding='utf-8') as f:
                pkg = json.load(f)
                if "jest" in pkg.get("devDependencies", {}) or "jest" in pkg.get("dependencies", {}):
                    frameworks.append("jest")
        except Exception:
            pass

    # Go: go test
    if (repo_path / "go.mod").exists() or list(repo_path.rglob("*_test.go")):
        frameworks.append("go-test")

    return frameworks

def _find_test_files(repo_path: Path) -> List[str]:
    """Находит все тестовые файлы"""
    test_files = []
    exclude_dirs = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build'}

    # Python tests
    for pattern in ["test_*.py", "*_test.py"]:
        for file_path in repo_path.rglob(pattern):
            if not any(ex in file_path.parts for ex in exclude_dirs):
                test_files.append(str(file_path.relative_to(repo_path)))

    # JavaScript tests
    for pattern in ["*.test.js", "*.test.ts", "*.spec.js", "*.spec.ts"]:
        for file_path in repo_path.rglob(pattern):
            if not any(ex in file_path.parts for ex in exclude_dirs):
                test_files.append(str(file_path.relative_to(repo_path)))

    # Go tests
    for file_path in repo_path.rglob("*_test.go"):
        if not any(ex in file_path.parts for ex in exclude_dirs):
            test_files.append(str(file_path.relative_to(repo_path)))

    return sorted(test_files)

def _run_pytest_coverage(repo_path: Path) -> Dict:
    """Запускает pytest с coverage (если установлен)"""
    result = {"available": False, "coverage": 0, "note": ""}

    try:
        # Проверяем есть ли pytest
        subprocess.run(["pytest", "--version"], capture_output=True, check=True, timeout=5)

        # Запускаем pytest с coverage
        proc = subprocess.run(
            ["pytest", "--cov", "--cov-report=json", "--cov-report=term"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=120
        )

        # Читаем coverage.json если есть
        coverage_json = repo_path / "coverage.json"
        if coverage_json.exists():
            with open(coverage_json, 'r') as f:
                cov_data = json.load(f)
                result["coverage"] = cov_data.get("totals", {}).get("percent_covered", 0)
                result["available"] = True
        else:
            result["note"] = "pytest-cov not installed"

    except subprocess.TimeoutExpired:
        result["note"] = "Tests timeout (>120s)"
    except subprocess.CalledProcessError:
        result["note"] = "Tests failed"
    except FileNotFoundError:
        result["note"] = "pytest not found"
    except Exception as e:
        result["note"] = f"Error: {str(e)}"

    return result

def _run_jest_coverage(repo_path: Path) -> Dict:
    """Запускает jest с coverage"""
    result = {"available": False, "coverage": 0, "note": ""}

    try:
        # Запускаем jest с coverage
        proc = subprocess.run(
            ["npm", "run", "test", "--", "--coverage", "--json"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=120
        )

        # TODO: парсинг jest coverage output
        result["note"] = "Jest coverage parsing not implemented yet"

    except subprocess.TimeoutExpired:
        result["note"] = "Tests timeout (>120s)"
    except FileNotFoundError:
        result["note"] = "npm not found"
    except Exception as e:
        result["note"] = f"Error: {str(e)}"

    return result

def _run_go_coverage(repo_path: Path) -> Dict:
    """Запускает go test с coverage"""
    result = {"available": False, "coverage": 0, "note": ""}

    try:
        # Запускаем go test с coverage
        proc = subprocess.run(
            ["go", "test", "-cover", "./..."],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=120
        )

        # Парсим вывод
        if proc.returncode == 0 and "coverage:" in proc.stdout:
            import re
            match = re.search(r'coverage:\s+([\d.]+)%', proc.stdout)
            if match:
                result["coverage"] = float(match.group(1))
                result["available"] = True
        else:
            result["note"] = "Go tests failed or no coverage"

    except subprocess.TimeoutExpired:
        result["note"] = "Tests timeout (>120s)"
    except FileNotFoundError:
        result["note"] = "go not found"
    except Exception as e:
        result["note"] = f"Error: {str(e)}"

    return result

def _calculate_average_coverage(coverage_data: Dict) -> float:
    """Вычисляет среднее покрытие по всем языкам"""
    coverages = [v.get("coverage", 0) for v in coverage_data.values() if v.get("available")]

    if not coverages:
        return 0.0

    return round(sum(coverages) / len(coverages), 2)

def _save_testing_report(results: Dict) -> None:
    """Сохраняет отчет о тестировании"""
    import json
    reports_dir = get_reports_dir()

    # JSON
    json_path = reports_dir / "testing_report.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Markdown
    md_path = reports_dir / "testing_report.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# Testing Report\n\n")
        f.write(f"**Status:** {results['summary']['status']}\n\n")

        f.write("## Summary\n\n")
        f.write(f"- Test files: **{results['summary']['test_files_count']}**\n")
        f.write(f"- Frameworks: **{', '.join(results['summary']['frameworks_detected']) or 'None'}**\n")
        f.write(f"- Average coverage: **{results['summary']['average_coverage']}%**\n")
        f.write(f"- Threshold: **{results['summary']['threshold']}%**\n\n")

        if results["coverage"]:
            f.write("## Coverage by Language\n\n")
            for lang, data in results["coverage"].items():
                status = "✅" if data.get("available") else "❌"
                cov = data.get("coverage", 0)
                note = data.get("note", "")
                f.write(f"- {status} **{lang.title()}**: {cov}% {f'({note})' if note else ''}\n")
            f.write("\n")

        if results["test_files"]:
            f.write(f"## Test Files ({len(results['test_files'])})\n\n")
            for tf in results["test_files"][:20]:
                f.write(f"- `{tf}`\n")
            if len(results["test_files"]) > 20:
                f.write(f"\n... and {len(results['test_files']) - 20} more\n")
