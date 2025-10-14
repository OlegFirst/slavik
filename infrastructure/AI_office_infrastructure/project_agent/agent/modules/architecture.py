"""Architecture Analysis Module — анализ архитектуры проекта"""
from __future__ import annotations
import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from ..config import get_repo_path, get_reports_dir


def run_architecture_analysis(config: Dict, target_module: Optional[str] = None) -> Dict:
    """
    Полный архитектурный анализ проекта

    Returns:
        {
            "modules": {...},
            "dependencies": {...},
            "api_map": {...},
            "business_logic": {...},
            "issues": [...],
            "summary": {...}
        }
    """
    repo_path = get_repo_path()
    arch_config = config.get("modules", {}).get("architecture", {})
    enabled = arch_config.get("enabled", True)

    if not enabled:
        return {"error": "Architecture module is disabled"}

    results = {
        "modules": {},
        "dependencies": {},
        "api_map": {},
        "business_logic": {},
        "issues": [],
        "summary": {}
    }

    # 1. Module scanning
    print("📦 Scanning modules...")
    results["modules"] = _scan_modules(repo_path, target_module)

    # 2. Dependency analysis
    print("🔗 Analyzing dependencies...")
    results["dependencies"] = _analyze_dependencies(repo_path, target_module)

    # 3. API mapping
    print("🌐 Mapping API endpoints...")
    results["api_map"] = _map_api_endpoints(repo_path, target_module)

    # 4. Business logic extraction
    print("💼 Extracting business logic...")
    results["business_logic"] = _extract_business_logic(repo_path, target_module)

    # 5. Detect issues
    results["issues"] = _detect_architecture_issues(results)

    # 6. Summary
    results["summary"] = _generate_architecture_summary(results)

    # Save report
    _save_architecture_report(results)

    return results


def _scan_modules(repo_path: Path, target_module: Optional[str] = None) -> Dict:
    """Сканирование модулей через module_scanner.py"""
    scanner_path = repo_path / "tools" / "analyzers" / "module_scanner.py"

    if not scanner_path.exists():
        return {"error": "module_scanner.py not found"}

    try:
        result = subprocess.run(
            [sys.executable, str(scanner_path)],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0 and result.stdout:
            # Parse output
            modules = {}
            for line in result.stdout.strip().split('\n'):
                if 'Module:' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        module_name = parts[1].strip()
                        modules[module_name] = {"scanned": True}

            return modules
        else:
            return {"error": result.stderr or "Module scanner failed"}

    except subprocess.TimeoutExpired:
        return {"error": "Module scanner timeout"}
    except Exception as e:
        return {"error": str(e)}


def _analyze_dependencies(repo_path: Path, target_module: Optional[str] = None) -> Dict:
    """Анализ зависимостей через dependency_validator.py"""
    validator_path = repo_path / "tools" / "analyzers" / "dependency_validator.py"
    mapper_path = repo_path / "tools" / "analyzers" / "dependency_mapper.py"

    deps_result = {
        "validation": {},
        "mapping": {},
        "conflicts": [],
        "circular": []
    }

    # 1. Validation
    if validator_path.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(validator_path)],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                deps_result["validation"] = {"status": "OK", "output": result.stdout[:500]}
            else:
                deps_result["validation"] = {"status": "FAILED", "errors": result.stderr[:500]}

        except subprocess.TimeoutExpired:
            deps_result["validation"] = {"status": "TIMEOUT"}
        except Exception as e:
            deps_result["validation"] = {"error": str(e)}

    # 2. Mapping
    if mapper_path.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(mapper_path)],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0 and result.stdout:
                # Try to parse JSON output
                try:
                    deps_result["mapping"] = json.loads(result.stdout)
                except json.JSONDecodeError:
                    deps_result["mapping"] = {"raw_output": result.stdout[:500]}
            else:
                deps_result["mapping"] = {"error": result.stderr[:500]}

        except subprocess.TimeoutExpired:
            deps_result["mapping"] = {"error": "Timeout"}
        except Exception as e:
            deps_result["mapping"] = {"error": str(e)}

    return deps_result


def _map_api_endpoints(repo_path: Path, target_module: Optional[str] = None) -> Dict:
    """Карта API endpoints через api_mapper.py"""
    mapper_path = repo_path / "tools" / "analyzers" / "api_mapper.py"

    if not mapper_path.exists():
        return {"error": "api_mapper.py not found"}

    try:
        result = subprocess.run(
            [sys.executable, str(mapper_path)],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0 and result.stdout:
            # Try to parse JSON
            try:
                api_map = json.loads(result.stdout)
                return api_map
            except json.JSONDecodeError:
                # Parse text output
                endpoints = []
                for line in result.stdout.strip().split('\n'):
                    if 'GET' in line or 'POST' in line or 'PUT' in line or 'DELETE' in line:
                        endpoints.append(line.strip())
                return {"endpoints": endpoints, "count": len(endpoints)}
        else:
            return {"error": result.stderr or "API mapper failed"}

    except subprocess.TimeoutExpired:
        return {"error": "API mapper timeout"}
    except Exception as e:
        return {"error": str(e)}


def _extract_business_logic(repo_path: Path, target_module: Optional[str] = None) -> Dict:
    """Извлечение бизнес-логики через business_logic_mapper.py"""
    mapper_path = repo_path / "tools" / "analyzers" / "business_logic_mapper.py"

    if not mapper_path.exists():
        return {"error": "business_logic_mapper.py not found"}

    try:
        result = subprocess.run(
            [sys.executable, str(mapper_path)],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=90
        )

        if result.returncode == 0 and result.stdout:
            # Try to parse JSON
            try:
                logic_map = json.loads(result.stdout)
                return logic_map
            except json.JSONDecodeError:
                return {"raw_output": result.stdout[:1000]}
        else:
            return {"error": result.stderr or "Business logic mapper failed"}

    except subprocess.TimeoutExpired:
        return {"error": "Business logic mapper timeout"}
    except Exception as e:
        return {"error": str(e)}


def _detect_architecture_issues(results: Dict) -> List[Dict]:
    """Обнаружение архитектурных проблем"""
    issues = []

    # Check for circular dependencies
    if results["dependencies"].get("circular"):
        issues.append({
            "type": "circular_dependency",
            "severity": "high",
            "count": len(results["dependencies"]["circular"]),
            "message": "Circular dependencies detected"
        })

    # Check for conflicts
    if results["dependencies"].get("conflicts"):
        issues.append({
            "type": "dependency_conflict",
            "severity": "medium",
            "count": len(results["dependencies"]["conflicts"]),
            "message": "Dependency conflicts detected"
        })

    # Check API coverage
    api_count = results["api_map"].get("count", 0)
    if api_count == 0:
        issues.append({
            "type": "no_api_endpoints",
            "severity": "low",
            "message": "No API endpoints found or mapped"
        })

    # Check module count
    module_count = len(results["modules"])
    if module_count == 0:
        issues.append({
            "type": "no_modules",
            "severity": "high",
            "message": "No modules detected"
        })

    return issues


def _generate_architecture_summary(results: Dict) -> Dict:
    """Генерация сводки по архитектуре"""
    summary = {
        "modules_count": len(results["modules"]),
        "api_endpoints_count": results["api_map"].get("count", 0),
        "dependency_status": results["dependencies"].get("validation", {}).get("status", "UNKNOWN"),
        "issues_count": len(results["issues"]),
        "issues_high": len([i for i in results["issues"] if i.get("severity") == "high"]),
        "issues_medium": len([i for i in results["issues"] if i.get("severity") == "medium"]),
        "issues_low": len([i for i in results["issues"] if i.get("severity") == "low"]),
        "health": "GOOD" if len(results["issues"]) == 0 else "NEEDS_ATTENTION"
    }

    return summary


def _save_architecture_report(results: Dict) -> None:
    """Сохранение отчета по архитектуре"""
    reports_dir = get_reports_dir()

    # JSON
    json_path = reports_dir / "architecture_report.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Markdown
    md_path = reports_dir / "architecture_report.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# Architecture Analysis Report\n\n")

        # Summary
        summary = results["summary"]
        f.write("## Summary\n\n")
        f.write(f"- **Health:** {summary['health']}\n")
        f.write(f"- **Modules:** {summary['modules_count']}\n")
        f.write(f"- **API Endpoints:** {summary['api_endpoints_count']}\n")
        f.write(f"- **Dependency Status:** {summary['dependency_status']}\n")
        f.write(f"- **Issues:** {summary['issues_count']} total ")
        f.write(f"({summary['issues_high']} high, {summary['issues_medium']} medium, {summary['issues_low']} low)\n\n")

        # Issues
        if results["issues"]:
            f.write("## Issues\n\n")
            for issue in results["issues"]:
                severity = issue.get("severity", "unknown").upper()
                f.write(f"- **[{severity}]** {issue.get('message', 'No message')}\n")
            f.write("\n")

        # Modules
        if results["modules"]:
            f.write(f"## Modules ({len(results['modules'])})\n\n")
            for module_name in sorted(results["modules"].keys()):
                f.write(f"- {module_name}\n")
            f.write("\n")

        # API Endpoints
        if results["api_map"].get("endpoints"):
            f.write(f"## API Endpoints ({len(results['api_map']['endpoints'])})\n\n")
            for endpoint in results["api_map"]["endpoints"][:20]:
                f.write(f"- `{endpoint}`\n")
            if len(results["api_map"]["endpoints"]) > 20:
                f.write(f"\n... and {len(results['api_map']['endpoints']) - 20} more\n")
            f.write("\n")

        # Dependencies
        if results["dependencies"]:
            f.write("## Dependencies\n\n")
            f.write(f"- Validation: **{results['dependencies'].get('validation', {}).get('status', 'N/A')}**\n")
            if results["dependencies"].get("conflicts"):
                f.write(f"- Conflicts: **{len(results['dependencies']['conflicts'])}**\n")
            if results["dependencies"].get("circular"):
                f.write(f"- Circular: **{len(results['dependencies']['circular'])}**\n")
            f.write("\n")

        # Business Logic
        if results["business_logic"] and not results["business_logic"].get("error"):
            f.write("## Business Logic\n\n")
            f.write(f"- Extracted: ✅\n")
            if isinstance(results["business_logic"], dict):
                logic_count = len(results["business_logic"])
                f.write(f"- Components: {logic_count}\n")
            f.write("\n")

    print(f"\n📊 Architecture report saved to {md_path}")
