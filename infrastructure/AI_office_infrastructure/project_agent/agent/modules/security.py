"""Security Module — проверки безопасности проекта"""
from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, List
from ..config import get_repo_path, get_reports_dir

# Паттерны для поиска секретов
SECRET_PATTERNS = [
    (r'(?i)api[_\s]?key\s*=\s*["\']([^"\']+)["\']', "API Key"),
    (r'(?i)secret[_\s]?(?:key|token)\s*=\s*["\']([^"\']+)["\']', "Secret Key/Token"),
    (r'(?i)password\s*=\s*["\']([^"\']+)["\']', "Password"),
    (r'(?i)aws[_\s]?access[_\s]?key[_\s]?id\s*=\s*["\']([^"\']+)["\']', "AWS Access Key"),
    (r'(?i)aws[_\s]?secret[_\s]?access[_\s]?key\s*=\s*["\']([^"\']+)["\']', "AWS Secret Key"),
    (r'(?i)private[_\s]?key\s*=\s*["\']([^"\']+)["\']', "Private Key"),
    (r'-----BEGIN (?:RSA )?PRIVATE KEY-----', "Private Key Block"),
]

# Небезопасные паттерны в коде
VULNERABILITY_PATTERNS = [
    (r'eval\s*\(', "eval() usage (code injection risk)"),
    (r'exec\s*\(', "exec() usage (code injection risk)"),
    (r'os\.system\s*\(', "os.system() usage (command injection risk)"),
    (r'subprocess\.call\(.+shell\s*=\s*True', "subprocess with shell=True (command injection risk)"),
    (r'pickle\.loads?\s*\(', "pickle usage (deserialization risk)"),
    (r'(?i)SELECT\s+.+FROM\s+.+WHERE\s+.+\+', "Potential SQL injection (string concatenation)"),
]

def run_security_checks(config: Dict) -> Dict[str, any]:
    """
    Запускает проверки безопасности

    Returns:
        {
            "secrets": [...],
            "vulnerabilities": [...],
            "dependencies": {...},
            "summary": {...}
        }
    """
    checks = config.get("modules", {}).get("security", {}).get("checks", [])

    results = {
        "secrets": [],
        "vulnerabilities": [],
        "dependencies": {},
        "summary": {}
    }

    repo_path = get_repo_path()

    # 1. Проверка на секреты
    if "secrets" in checks:
        results["secrets"] = _scan_secrets(repo_path)

    # 2. Проверка на уязвимости в коде
    if "vulnerabilities" in checks:
        results["vulnerabilities"] = _scan_vulnerabilities(repo_path)

    # 3. Проверка зависимостей (TODO: интеграция с Safety, npm audit)
    if "dependencies" in checks:
        results["dependencies"] = _check_dependencies(repo_path)

    # Summary
    results["summary"] = {
        "secrets_found": len(results["secrets"]),
        "vulnerabilities_found": len(results["vulnerabilities"]),
        "high_risk": len([v for v in results["vulnerabilities"] if "injection" in v.get("type", "").lower()]),
        "status": "FAIL" if (results["secrets"] or results["vulnerabilities"]) else "OK"
    }

    # Сохраняем отчет
    _save_security_report(results)

    return results

def _scan_secrets(repo_path: Path) -> List[Dict]:
    """Сканирует файлы на наличие секретов"""
    secrets = []
    exclude_dirs = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build'}

    # Файлы для сканирования
    extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.env', '.yml', '.yaml', '.json', '.sh', '.conf'}

    for file_path in repo_path.rglob('*'):
        # Skip directories and excluded
        if file_path.is_dir() or any(ex in file_path.parts for ex in exclude_dirs):
            continue

        if file_path.suffix not in extensions:
            continue

        # Skip large files
        if file_path.stat().st_size > 1_000_000:
            continue

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            for pattern, secret_type in SECRET_PATTERNS:
                for match in re.finditer(pattern, content):
                    line_num = content[:match.start()].count('\n') + 1
                    secrets.append({
                        "file": str(file_path.relative_to(repo_path)),
                        "line": line_num,
                        "type": secret_type,
                        "snippet": content[max(0, match.start()-20):match.end()+20].replace('\n', ' ')[:80]
                    })
        except Exception:
            continue

    return secrets

def _scan_vulnerabilities(repo_path: Path) -> List[Dict]:
    """Сканирует код на распространенные уязвимости"""
    vulns = []
    exclude_dirs = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build'}
    code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go'}

    for file_path in repo_path.rglob('*'):
        if file_path.is_dir() or any(ex in file_path.parts for ex in exclude_dirs):
            continue

        if file_path.suffix not in code_extensions:
            continue

        if file_path.stat().st_size > 1_000_000:
            continue

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            for pattern, vuln_type in VULNERABILITY_PATTERNS:
                for match in re.finditer(pattern, content):
                    line_num = content[:match.start()].count('\n') + 1
                    vulns.append({
                        "file": str(file_path.relative_to(repo_path)),
                        "line": line_num,
                        "type": vuln_type,
                        "snippet": content[max(0, match.start()-20):match.end()+20].replace('\n', ' ')[:80]
                    })
        except Exception:
            continue

    return vulns

def _check_dependencies(repo_path: Path) -> Dict:
    """Проверяет зависимости проекта (заглушка для интеграции с Safety/npm audit)"""
    result = {
        "python": {"checked": False, "vulnerabilities": []},
        "nodejs": {"checked": False, "vulnerabilities": []},
        "note": "Dependency scanning requires Safety (Python) or npm audit (Node.js)"
    }

    # TODO: Интеграция с safety check (Python)
    # TODO: Интеграция с npm audit (Node.js)

    return result

def _save_security_report(results: Dict) -> None:
    """Сохраняет отчет о безопасности"""
    import json
    reports_dir = get_reports_dir()

    # JSON отчет
    json_path = reports_dir / "security_report.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Markdown отчет
    md_path = reports_dir / "security_report.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# Security Report\n\n")
        f.write(f"**Status:** {results['summary']['status']}\n\n")

        f.write("## Summary\n\n")
        f.write(f"- Secrets found: **{results['summary']['secrets_found']}**\n")
        f.write(f"- Vulnerabilities found: **{results['summary']['vulnerabilities_found']}**\n")
        f.write(f"- High risk issues: **{results['summary']['high_risk']}**\n\n")

        if results["secrets"]:
            f.write("## Secrets Found\n\n")
            for secret in results["secrets"]:
                f.write(f"- `{secret['file']}:{secret['line']}` — {secret['type']}\n")
            f.write("\n")

        if results["vulnerabilities"]:
            f.write("## Vulnerabilities\n\n")
            for vuln in results["vulnerabilities"]:
                f.write(f"- `{vuln['file']}:{vuln['line']}` — {vuln['type']}\n")
            f.write("\n")
